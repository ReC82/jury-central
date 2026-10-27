"""PR27 « Construire et justifier une procédure de diagnostic » — règles du cours, six dossiers
résolus et schémas (ticket #226).

Ce cours est un cours de **méthode de dépannage** (exigence officielle AP-15 « dépannage sur les
dysfonctionnements courants » et complément AP-C01 « rédiger une réponse écrite de
technicien »). Les règles qu'un dossier d'examen applique et qu'un correcteur vérifie sont
écrites ici une seule fois, sous forme de données et de fonctions testées, et réutilisées par
le cours, les exercices, le mini-examen et les schémas :

- `METHOD_STEPS` : hypothèse → test discriminant → résultat attendu → interprétation → action
  → validation ;
- `LEVELS` / `precautions` / `order_probes` : échelle d'invasivité 0 à 5 (convention du cours)
  et précautions exigées à chaque niveau ; tri du moins au plus invasif ;
- `NET_LAYERS` / `PC_LAYERS` : approche par couches ;
- `cross_test` : conclusion d'un test croisé (élément suspect sur un poste sain, élément sain
  sur le poste suspect) ;
- `FALSE_RESULTS` : faux positifs et faux négatifs ;
- `config_diff` : contrôle de configuration (écarts avec la référence) ;
- `common_factors` : conditions de reproduction d'une panne intermittente (facteur présent à
  chaque panne, absent sinon) ;
- `remaining` / `is_discriminant` : hypothèses encore possibles après un test, test qui
  départage ;
- `TREES` / `walk` : quatre arbres de décision (matériel, démarrage, système, réseau) ;
- `CASES` : les six dossiers entièrement résolus (démarrage, périphérique, DHCP, DNS, partage,
  panne intermittente), dont l'ordre des tests, les hypothèses écartées, la cause retenue et le
  chemin dans l'arbre sont **calculés et contrôlés**.

Les schémas sont construits en SVG depuis ces données (aucune image générée), comme PR18 à
PR26. Les personnes, entreprises, adresses et numéros sont fictifs.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    step_flow_svg,
)

WRITTEN_AT = "octobre 2026"
STATIC_DIR_REF = "img/ampcr-pratique"
_STROKE = "#33415c"
_SOFT = "#f4f6fb"

# =============================================================================================
# 1. Le cycle de diagnostic
# =============================================================================================

METHOD_STEPS: tuple[tuple[str, str], ...] = (
    ("Hypothèse", "Formuler une cause possible qui explique tous les symptômes observés."),
    ("Test discriminant", "Choisir le test dont le résultat diffère selon les hypothèses encore possibles."),
    ("Résultat attendu", "Écrire AVANT le test ce qu'il montrera si l'hypothèse est vraie, et si elle est fausse."),
    ("Interprétation", "Comparer le résultat obtenu aux résultats attendus : garder ou écarter chaque hypothèse."),
    ("Action", "Corriger la cause confirmée, avec sauvegarde, accord et plan de retour arrière si besoin."),
    ("Validation", "Refaire le test du symptôme de départ et contrôler qu'aucune autre fonction n'est touchée."),
)

# =============================================================================================
# 2. Invasivité, précautions, mesure d'impact (convention du cours)
# =============================================================================================

P_INFORM = "prévenir l'utilisateur et lui faire enregistrer son travail"
P_IMPACT = "mesurer l'impact : qui est coupé, combien de temps, à quel moment"
P_STATE = "noter ou exporter l'état initial (configuration, photo du câblage) : plan de retour arrière"
P_POWER = "hors tension, câble secteur débranché, bracelet antistatique (ESD)"
P_WARRANTY = "garantie vérifiée : on n'ouvre pas un appareil sous garantie"
P_AGREE = "accord du client ou du responsable"
P_BACKUP = "sauvegarde des données vérifiée (copie relue) et accord écrit"


@dataclass(frozen=True)
class Level:
    number: int
    name: str
    examples: str
    precautions: tuple[str, ...]


LEVELS: tuple[Level, ...] = (
    Level(0, "Observer et questionner",
          "écouter l'utilisateur, regarder le poste, les câbles, les voyants allumés ou éteints", ()),
    Level(1, "Lire sans modifier",
          "messages affichés, journaux, gestionnaire de périphériques, ipconfig /all, réglages du firmware consultés", ()),
    Level(2, "Manipulation réversible",
          "rebrancher, changer de câble ou de port, redémarrer, test croisé, menu de démarrage ponctuel",
          (P_INFORM, P_IMPACT)),
    Level(3, "Modifier la configuration",
          "changer un paramètre, démarrage minimal, mode sans échec, restaurer un pilote",
          (P_INFORM, P_IMPACT, P_STATE)),
    Level(4, "Intervenir dans le matériel",
          "ouvrir le boîtier, remettre en place ou échanger une pièce",
          (P_INFORM, P_IMPACT, P_STATE, P_POWER, P_WARRANTY, P_AGREE)),
    Level(5, "Opération destructive ou irréversible",
          "formatage, réinstallation, réinitialisation d'usine, mise à jour du firmware",
          (P_INFORM, P_IMPACT, P_STATE, P_BACKUP)),
)
LEVEL_NAMES = tuple(level.name for level in LEVELS)


def precautions(level: int) -> tuple[str, ...]:
    """Précautions exigées avant un test ou une action de ce niveau (0 à 5)."""
    if level not in range(len(LEVELS)):
        raise ValueError("Le niveau d'invasivité va de 0 à 5.")
    return LEVELS[level].precautions


def level_label(level: int) -> str:
    return f"niveau {level} — {LEVELS[level].name.lower()}"


@dataclass(frozen=True)
class Probe:
    """Un test candidat : libellé, niveau d'invasivité, durée estimée (minutes)."""

    label: str
    level: int
    minutes: int


def order_probes(probes: tuple[Probe, ...]) -> tuple[Probe, ...]:
    """Convention du cours : du moins invasif au plus invasif ; à niveau égal, le plus rapide
    d'abord."""
    return tuple(sorted(probes, key=lambda p: (p.level, p.minutes)))


# =============================================================================================
# 3. Approche par couches et isolation de variables
# =============================================================================================

# (couche, ce qu'elle contient, test typique) — de bas en haut.
NET_LAYERS: tuple[tuple[str, str, str], ...] = (
    ("Physique", "câble, prise, voyant de lien, radio Wi-Fi", "voyant allumé ? « Média déconnecté » ?"),
    ("Liaison", "carte réseau, port du switch, VLAN, association Wi-Fi", "carte activée ? port actif ? SSID associé ?"),
    ("Réseau (IP)", "adresse, masque, passerelle", "adresse valide (pas 169.254) ? ping de la passerelle ?"),
    ("Transport", "ports des services (TCP 445 partage, 443 web)", "le port du service répond-il ? pare-feu ?"),
    ("Application", "noms (DNS), comptes, droits, logiciel", "nslookup ? « Accès refusé » ? message du logiciel ?"),
)
PC_LAYERS: tuple[tuple[str, str, str], ...] = (
    ("Alimentation", "secteur, bloc, bouton", "voyant, ventilateur au démarrage"),
    ("Matériel", "carte mère, processeur, mémoire, carte graphique", "image du firmware, bips, codes POST"),
    ("Firmware et démarrage", "UEFI, disques détectés, ordre de démarrage", "disque vu ? chargeur trouvé ?"),
    ("Système", "noyau, services, fichiers système", "journaux, sfc /scannow, mode sans échec"),
    ("Pilotes", "pilotes des périphériques", "gestionnaire de périphériques, version du pilote"),
    ("Application et compte", "logiciel, profil, droits", "autre compte, autre logiciel, message exact"),
)
STRATEGIES: tuple[tuple[str, str], ...] = (
    ("Ascendante", "de la couche physique vers l'application : quand le symptôme est total (plus rien ne passe)."),
    ("Descendante", "de l'application vers le physique : quand un seul service échoue et que le reste marche."),
    ("Par division", "un test au milieu (ping de la passerelle) coupe le problème en deux moitiés à la fois."),
)

# =============================================================================================
# 4. Test croisé, test négatif, faux positifs et faux négatifs
# =============================================================================================

CROSS_PART = "L'élément suspect est en cause"
CROSS_HOST = "Le poste d'origine est en cause, pas l'élément"
CROSS_BOTH = "Les deux échouent : plusieurs causes, ou élément « sain » à revérifier"
CROSS_NONE = "Panne non reproduite : mauvais contact ou panne intermittente"
CROSS_KINDS = (CROSS_PART, CROSS_HOST, CROSS_BOTH, CROSS_NONE)


def cross_test(suspect_on_good_ok: bool, good_on_suspect_ok: bool) -> str:
    """Test croisé : A = élément suspect monté sur un poste sain ; B = élément sain (connu bon)
    monté sur le poste suspect. Chaque argument vaut True si le montage fonctionne."""
    if not suspect_on_good_ok and good_on_suspect_ok:
        return CROSS_PART
    if suspect_on_good_ok and not good_on_suspect_ok:
        return CROSS_HOST
    if not suspect_on_good_ok and not good_on_suspect_ok:
        return CROSS_BOTH
    return CROSS_NONE


FALSE_POSITIVE = "Faux positif (le test signale une panne qui n'existe pas)"
FALSE_NEGATIVE = "Faux négatif (le test ne voit pas une panne qui existe)"
FALSE_KINDS = (FALSE_POSITIVE, FALSE_NEGATIVE)
FALSE_RESULTS: tuple[tuple[str, str, str], ...] = (
    ("Le ping du serveur échoue alors que le partage s'ouvre : le pare-feu du serveur bloque le ping.",
     FALSE_POSITIVE, "un test qui échoue pour une autre raison que la panne cherchée"),
    ("Le testeur de câble indique une coupure ; avec des piles neuves, le même câble est correct.",
     FALSE_POSITIVE, "outil de mesure défaillant : contrôler l'outil sur un élément connu bon"),
    ("« Aucun signal » sur l'écran : l'entrée HDMI 2 était sélectionnée, le câble est sur HDMI 1.",
     FALSE_POSITIVE, "mauvais réglage pendant le test"),
    ("La carte réseau semble morte : le cordon utilisé pour la tester était lui-même coupé.",
     FALSE_POSITIVE, "élément de test non vérifié"),
    ("Le testeur de continuité valide un câble dont deux paires sont mélangées ; le lien reste instable.",
     FALSE_NEGATIVE, "le test ne mesure pas ce qui est en panne (paires, diaphonie)"),
    ("Un test mémoire d'un seul passage ne trouve rien ; la barrette provoque pourtant des écrans bleus.",
     FALSE_NEGATIVE, "test trop court pour une panne intermittente"),
    ("Pendant les 10 minutes de l'intervention, le Wi-Fi ne coupe pas ; la panne revient le lendemain midi.",
     FALSE_NEGATIVE, "conditions de reproduction absentes pendant le test"),
    ("L'antivirus ne détecte rien sur un poste dont les fichiers sont renommés en « .locked ».",
     FALSE_NEGATIVE, "un outil de détection ne voit pas tout"),
)

# =============================================================================================
# 5. Contrôle de configuration, conditions de reproduction, tests discriminants
# =============================================================================================


def config_diff(reference: dict[str, str], observed: dict[str, str]) -> tuple[str, ...]:
    """Paramètres de la référence dont la valeur relevée diffère (ordre de la référence)."""
    return tuple(k for k, v in reference.items() if observed.get(k, "").strip() != v.strip())


def common_factors(header: tuple[str, ...], rows: tuple[tuple[str, ...], ...], *,
                   outcome: str, failure: str) -> tuple[tuple[str, str], ...]:
    """Conditions de reproduction : (colonne, valeur) identique à CHAQUE panne et jamais vue
    quand la panne ne se produit pas. `outcome` = colonne du résultat, `failure` = sa valeur
    en cas de panne."""
    o = header.index(outcome)
    failures = [r for r in rows if r[o] == failure]
    others = [r for r in rows if r[o] != failure]
    found = []
    for i, name in enumerate(header):
        if i == o or not failures:
            continue
        values = {r[i] for r in failures}
        if len(values) == 1 and not any(r[i] in values for r in others):
            found.append((name, values.pop()))
    return tuple(found)


def remaining(expected: tuple[str, ...], observed: str, alive: tuple[int, ...]) -> tuple[int, ...]:
    """Hypothèses (indices) encore possibles : celles dont le résultat attendu est le résultat
    obtenu."""
    return tuple(i for i in alive if expected[i] == observed)


def is_discriminant(expected: tuple[str, ...], alive: tuple[int, ...]) -> bool:
    """Un test départage s'il prévoit au moins deux résultats différents parmi les hypothèses
    encore possibles."""
    return len({expected[i] for i in alive}) > 1


# =============================================================================================
# 6. Quatre arbres de décision (question fermée, piste si « non »)
# =============================================================================================


@dataclass(frozen=True)
class Tree:
    key: str
    title: str
    start: str  # symptôme de départ
    questions: tuple[tuple[str, str], ...]
    final: str


TREE_HARDWARE = Tree(
    key="materiel",
    title="Matériel — un périphérique USB ne fonctionne pas",
    start="Imprimante, scanner, webcam… branché en USB, sans effet.",
    questions=(
        ("L'appareil est-il alimenté (voyant allumé, interrupteur sur marche) ?",
         "Alimentation : prise, bloc secteur, interrupteur ; tester la prise avec un autre appareil."),
        ("Son autotest réussit-il (page de test interne, écran « Prête ») ?",
         "Panne de l'appareil : code d'erreur dans le manuel ; garantie ou réparation (escalade)."),
        ("Le système le détecte-t-il (gestionnaire de périphériques) ?",
         "Liaison : autre port USB avec le même câble, puis autre câble connu bon, une variable à la fois."),
        ("Le pilote est-il installé sans erreur (pas de point d'exclamation) ?",
         "Pilote : installer celui du fabricant, après avoir noté la version en place."),
        ("Fonctionne-t-il depuis l'outil de test du système (page de test Windows) ?",
         "Configuration : file d'attente bloquée, périphérique par défaut, réglages de l'appareil."),
    ),
    final="L'appareil fonctionne depuis le système : chercher dans le logiciel ou le document de l'utilisateur.",
)
TREE_BOOT = Tree(
    key="demarrage",
    title="Démarrage — le PC ne démarre pas jusqu'au système",
    start="Écran noir, message du firmware ou redémarrage en boucle.",
    questions=(
        ("Un signe de vie à l'appui sur le bouton (voyant, ventilateur) ?",
         "Alimentation : prise et câble, interrupteur du bloc, bouton de façade, test du bloc (PR06)."),
        ("Une image s'affiche-t-elle (logo ou écran du firmware) ?",
         "Écran, câble et entrée, puis bips ou codes POST du manuel ; configuration minimale (PR06)."),
        ("Le firmware détecte-t-il le disque système ?",
         "Disque : câble SATA ou logement M.2 ; disque défaillant : protéger les données d'abord."),
        ("Le disque système est-il le premier dans l'ordre de démarrage ?",
         "Ordre de démarrage : photographier l'ordre initial, essayer le menu de démarrage ponctuel, corriger."),
        ("Le chargeur lance-t-il le système sans erreur ?",
         "Chargeur ou système : réparation du démarrage (environnement de récupération), après sauvegarde."),
    ),
    final="Le système démarre : poursuivre avec l'arbre « système » ou le symptôme de départ.",
)
TREE_OS = Tree(
    key="systeme",
    title="Système — Windows démarre, mais un dysfonctionnement persiste",
    start="Lenteur, plantages, messages d'erreur après l'ouverture de session.",
    questions=(
        ("Les journaux sont-ils sans erreur de disque ou de mémoire ?",
         "Matériel probable : sauvegarder d'abord, puis contrôler disque (SMART) et mémoire (PR06)."),
        ("Le problème se produit-il aussi avec un autre compte ?",
         "Profil de l'utilisateur : tester un nouveau profil, y copier ses données ; ne rien supprimer."),
        ("Se produit-il aussi en démarrage minimal (programmes tiers désactivés) ?",
         "Logiciel ou service tiers : les réactiver par moitiés jusqu'à trouver le coupable."),
        ("Se produit-il aussi en mode sans échec ?",
         "Pilote chargé en mode normal : restaurer le pilote récemment modifié."),
        ("Les fichiers système sont-ils intègres (sfc /scannow sans violation) ?",
         "Fichiers système : DISM /Online /Cleanup-Image /RestoreHealth, puis sfc /scannow."),
    ),
    final="Système intègre, problème présent : point de restauration, puis réinstallation en dernier recours (sauvegarde, accord écrit).",
)
TREE_NETWORK = Tree(
    key="reseau",
    title="Réseau — un poste n'accède pas au réseau ou à Internet",
    start="Pas d'Internet, pas de partage, « Aucun accès réseau ».",
    questions=(
        ("Le lien est-il présent (voyant, pas « Média déconnecté ») ?",
         "Physique : câble, prise murale, port du switch ; test croisé avec un câble connu bon."),
        ("L'adresse IP est-elle valide (pas 169.254.x.x) ?",
         "DHCP : ipconfig /renew ; autre poste sur la même prise ; port et VLAN du switch ; serveur DHCP."),
        ("La passerelle répond-elle (ping de son adresse) ?",
         "Configuration IP : masque, passerelle, conflit d'adresse ; comparer au plan d'adressage."),
        ("Une adresse IP publique répond-elle (ping 8.8.8.8) ?",
         "Au-delà de la passerelle : box, liaison du fournisseur, pare-feu ; tracert situe l'arrêt."),
        ("Les noms sont-ils résolus (nslookup) ?",
         "DNS : serveurs de ipconfig /all comparés au plan ; nslookup avec un autre serveur ; ipconfig /flushdns."),
    ),
    final="Le réseau fonctionne : chercher au niveau du service (navigateur, proxy, partage, compte, droits).",
)
TREES: tuple[Tree, ...] = (TREE_HARDWARE, TREE_BOOT, TREE_OS, TREE_NETWORK)
TREES_BY_KEY = {t.key: t for t in TREES}


def walk(tree: Tree, answers: tuple[bool, ...]) -> tuple[int | None, str]:
    """Parcourt l'arbre avec les réponses données (True = « oui »). Renvoie (numéro de la
    question du premier « non », piste) ou (None, conclusion finale) si tout est « oui »."""
    if len(answers) > len(tree.questions) or (False in answers and answers.index(False) != len(answers) - 1):
        raise ValueError("Les réponses s'arrêtent au premier « non ».")
    for number, (answer, (_q, if_no)) in enumerate(zip(answers, tree.questions, strict=False), start=1):
        if not answer:
            return number, if_no
    if len(answers) < len(tree.questions):
        raise ValueError("Réponses incomplètes : il faut aller jusqu'au premier « non » ou au bout.")
    return None, tree.final


# =============================================================================================
# 7. Procédures : conservation de preuves, retour arrière, DHCP
# =============================================================================================

EVIDENCE_STEPS: tuple[tuple[str, str], ...] = (
    ("Horodater", "Noter la date, l'heure et ce que l'utilisateur a vu ou fait au moment du problème."),
    ("Capturer", "Photographier ou copier le message exact, l'écran, les voyants."),
    ("Exporter", "Enregistrer les journaux et la configuration (ipconfig /all > fichier) avant tout changement."),
    ("Photographier", "Le câblage et les réglages avant de débrancher ou de modifier : c'est l'état initial."),
    ("Ne rien effacer", "En cas d'incident de sécurité : isoler du réseau, ne pas « nettoyer » soi-même."),
    ("Joindre", "Attacher les preuves à la fiche d'incident ; elles servent au rapport et à l'escalade."),
)
ROLLBACK_STEPS: tuple[tuple[str, str], ...] = (
    ("État initial", "Noter ou exporter la configuration, la version du pilote, photographier le câblage."),
    ("Sauvegarde", "Point de restauration, copie de la configuration ou de l'ancien pilote."),
    ("Critère d'échec", "Écrire à l'avance ce qui déclenchera le retour arrière, et le délai maximum."),
    ("Modifier", "Appliquer une seule modification à la fois, la noter sur la fiche."),
    ("Tester", "Refaire le test du symptôme de départ et le test des fonctions voisines."),
    ("Revenir ou valider", "Si le critère d'échec est atteint : restaurer l'état initial et le vérifier."),
)
DHCP_STEPS: tuple[tuple[str, str], ...] = (
    ("Lire", "ipconfig /all et voyant : lien présent ? adresse en 169.254.x.x ?"),
    ("Renouveler", "ipconfig /release puis ipconfig /renew : le poste obtient-il un bail ?"),
    ("Test croisé", "Un portable connu bon, en DHCP, sur la même prise : prise ou poste en cause ?"),
    ("Autre prise", "Le poste sur une prise du bon VLAN d'après le plan de brassage."),
    ("Escalader", "Port, VLAN ou serveur DHCP hors de mes droits : fiche avec les résultats des tests."),
)
PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Le cycle de diagnostic", METHOD_STEPS),
    ("Conserver les preuves", EVIDENCE_STEPS),
    ("Préparer un retour arrière", ROLLBACK_STEPS),
    ("Diagnostiquer une adresse 169.254.x.x", DHCP_STEPS),
)

# =============================================================================================
# 8. Les six dossiers entièrement résolus
# =============================================================================================


@dataclass(frozen=True)
class DTest:
    label: str
    level: int
    minutes: int
    expected: tuple[str, ...]  # résultat attendu pour chaque hypothèse du dossier
    observed: str


@dataclass(frozen=True)
class Case:
    key: str
    theme: str
    title: str
    context: str
    symptoms: tuple[str, ...]
    hypotheses: tuple[str, ...]
    tests: tuple[DTest, ...]
    tree: Tree
    tree_answers: tuple[bool, ...]
    action: str
    action_level: int
    rollback: str
    impact: str
    evidence: str
    validation: tuple[str, ...]
    escalation: str
    conclusion: str

    def alive_before(self, index: int) -> tuple[int, ...]:
        alive = tuple(range(len(self.hypotheses)))
        for test in self.tests[:index]:
            alive = remaining(test.expected, test.observed, alive)
        return alive

    @property
    def cause(self) -> int | None:
        alive = self.alive_before(len(self.tests))
        return alive[0] if len(alive) == 1 else None

    @property
    def tree_result(self) -> tuple[int | None, str]:
        return walk(self.tree, self.tree_answers)


CASES: tuple[Case, ...] = (
    Case(
        key="D1",
        theme="démarrage",
        title="« No bootable device » après l'ajout d'un disque",
        context=(
            "Bureau d'études Delta (fictif). Hier soir, un collègue a ajouté dans le PC tour de Julie un second SSD "
            "SATA, vide, destiné aux données. Ce matin, après le logo, l'écran affiche « No bootable device »."
        ),
        symptoms=("logo du fabricant affiché", "puis « No bootable device »", "à chaque démarrage depuis l'ajout"),
        hypotheses=(
            "le nouveau disque (vide) est devenu le premier dans l'ordre de démarrage",
            "le câble SATA du disque système a été débranché pendant l'ajout",
            "le disque système est défaillant et n'est plus détecté",
            "le chargeur de démarrage (Windows Boot Manager) est endommagé",
        ),
        tests=(
            DTest("Réglages du firmware ouverts en consultation : liste des disques détectés", 1, 5,
                  ("disque système présent", "disque système absent", "disque système absent",
                   "disque système présent"),
                  "disque système présent"),
            DTest("Menu de démarrage ponctuel (touche du fabricant) : choisir « Windows Boot Manager »", 2, 5,
                  ("Windows démarre", "Windows Boot Manager absent", "Windows Boot Manager absent",
                   "erreur du chargeur"),
                  "Windows démarre"),
        ),
        tree=TREE_BOOT,
        tree_answers=(True, True, True, False),
        action="Placer « Windows Boot Manager » en tête de l'ordre de démarrage dans le firmware.",
        action_level=3,
        rollback="Ordre initial photographié avant la modification : il suffit de le remettre.",
        impact="Un seul poste, déjà arrêté ; Julie prévenue ; aucune donnée touchée.",
        evidence="Photo du message et de l'ordre de démarrage initial, jointes à la fiche.",
        validation=(
            "Trois démarrages à froid de suite jusqu'au bureau Windows.",
            "Le nouveau SSD apparaît dans l'Explorateur ; les documents de Julie sont intacts.",
        ),
        escalation="Non : réglage du firmware dans mes compétences, accord de Julie.",
        conclusion=(
            "Le disque système est détecté et Windows démarre par le menu ponctuel : seul l'ordre de démarrage "
            "était en cause depuis l'ajout du SSD. Ordre corrigé (ancien ordre photographié), trois démarrages "
            "validés."
        ),
    ),
    Case(
        key="D2",
        theme="périphérique",
        title="Imprimante USB : « Erreur — impression », rien ne sort",
        context=(
            "Cabinet de kinésithérapie Mouvance (fictif). L'imprimante laser USB de l'accueil n'imprime plus : "
            "Windows affiche « Erreur — impression » dans la file d'attente. Le câble USB passe derrière le meuble."
        ),
        symptoms=("« Erreur — impression » dans la file d'attente", "rien ne sort", "depuis ce matin, à chaque essai"),
        hypotheses=(
            "l'imprimante elle-même est en panne",
            "le port USB du PC est défaillant",
            "le câble USB est défectueux",
            "le pilote ou la file d'attente sont bloqués",
        ),
        tests=(
            DTest("Lire l'écran de l'imprimante", 1, 1,
                  ("code d'erreur", "« Prête »", "« Prête »", "« Prête »"), "« Prête »"),
            DTest("Gestionnaire de périphériques : l'imprimante est-elle listée ?", 1, 3,
                  ("—", "absente", "absente", "présente"), "absente"),
            DTest("Même câble branché sur un autre port USB du PC (une seule variable changée)", 2, 3,
                  ("—", "détectée", "absente", "—"), "absente"),
        ),
        tree=TREE_HARDWARE,
        tree_answers=(True, True, False),
        action="Remplacer le câble USB par un câble connu bon, sur le port d'origine.",
        action_level=2,
        rollback="Sans objet : aucun réglage modifié ; l'ancien câble est étiqueté « HS » et retiré.",
        impact="Impression de l'accueil seulement ; patients prévenus d'un délai de dix minutes.",
        evidence="Contenu de la file d'attente noté ; câble défectueux étiqueté et conservé pour le rapport.",
        validation=(
            "Page de test Windows imprimée depuis le PC de l'accueil.",
            "Un document de la secrétaire imprimé en entier ; file d'attente vide.",
        ),
        escalation="Non.",
        conclusion=(
            "L'imprimante est « Prête » et n'est plus détectée sur deux ports différents avec le même câble : "
            "le câble USB est en cause. Remplacé ; page de test et document de la secrétaire imprimés."
        ),
    ),
    Case(
        key="D3",
        theme="DHCP",
        title="Poste en 169.254.x.x après un déménagement de bureau",
        context=(
            "Fiduciaire Atrium (fictive). Le poste PC-COMPTA-03 a été déplacé hier au bureau 12 et branché sur la "
            "prise murale 12-B. Ce matin : « Aucun accès Internet ». Les autres postes de l'étage fonctionnent. Plan "
            "de brassage : 12-A → port 14 (VLAN 10, comptabilité) ; 12-B → port 15 (VLAN 99, inutilisé)."
        ),
        symptoms=("« Aucun accès Internet »", "ipconfig : 169.254.37.112", "depuis le déplacement, à chaque essai"),
        hypotheses=(
            "câble ou prise murale défectueux (pas de lien)",
            "carte réseau ou client DHCP du poste en panne",
            "le port du switch de la prise 12-B est dans un mauvais VLAN",
            "le serveur DHCP n'a plus d'adresse libre (étendue pleine)",
        ),
        tests=(
            DTest("ipconfig /all et voyant de la carte", 1, 2,
                  ("Média déconnecté", "lien, 169.254.x.x", "lien, 169.254.x.x", "lien, 169.254.x.x"),
                  "lien, 169.254.x.x"),
            DTest("Test croisé : un portable connu bon, en DHCP, sur la même prise 12-B", 2, 10,
                  ("—", "adresse valide", "169.254.x.x", "169.254.x.x"), "169.254.x.x"),
            DTest("Le poste sur la prise libre 12-A (VLAN 10 d'après le plan de brassage)", 2, 15,
                  ("—", "—", "adresse valide", "169.254.x.x"), "adresse valide"),
        ),
        tree=TREE_NETWORK,
        tree_answers=(True, False),
        action="Faire affecter le port 15 au VLAN 10 par l'administrateur réseau (je n'ai pas les droits sur le switch).",
        action_level=3,
        rollback="L'administrateur exporte la configuration du switch avant la modification.",
        impact="Le test croisé et le changement de prise n'ont coupé personne : prise libre, portable de test.",
        evidence="ipconfig /all enregistré dans un fichier, résultats des deux tests croisés, extrait du plan de brassage.",
        validation=(
            "Sur la prise 12-B, le poste obtient une adresse du VLAN 10 (192.168.10.x).",
            "La passerelle répond, Internet et le logiciel de comptabilité fonctionnent.",
        ),
        escalation="Oui : administrateur réseau (configuration du switch) ; en attendant, le poste reste sur 12-A.",
        conclusion=(
            "Lien présent mais 169.254 ; un portable sain échoue sur la même prise ; le poste fonctionne sur la "
            "prise 12-A : ni le poste ni le serveur DHCP ne sont en cause, c'est le port 15 (VLAN 99). Escaladé avec "
            "les preuves ; contournement sur 12-A."
        ),
    ),
    Case(
        key="D4",
        theme="DNS",
        title="Plus aucun site ne s'ouvre sur le poste du gérant",
        context=(
            "Agence immobilière Horizon (fictive). Vendredi, l'ancien serveur 192.168.1.250 a été retiré. Lundi, sur "
            "le poste du gérant seul, aucun site ne s'ouvre et Outlook ne se connecte plus. Plan d'adressage : "
            "passerelle et DNS = box 192.168.1.1, adresses données par DHCP."
        ),
        symptoms=("aucun site ne s'ouvre", "Outlook déconnecté", "un seul poste, depuis lundi"),
        hypotheses=(
            "liaison Internet coupée (box ou fournisseur)",
            "navigateur ou proxy mal configuré",
            "serveur DNS saisi à la main sur le poste, devenu obsolète",
            "service DNS de la box en panne",
        ),
        tests=(
            DTest("ping 8.8.8.8 (adresse IP publique)", 1, 1,
                  ("aucune réponse", "réponses", "réponses", "réponses"), "réponses"),
            DTest("nslookup www.exemple.be", 1, 2,
                  ("—", "nom résolu", "délai dépassé", "délai dépassé"), "délai dépassé"),
            DTest("Contrôle de configuration : serveurs DNS de ipconfig /all comparés au plan", 1, 5,
                  ("—", "—", "différent du plan", "conforme au plan"), "différent du plan"),
        ),
        tree=TREE_NETWORK,
        tree_answers=(True, True, True, True, False),
        action="Repasser la carte réseau en « Obtenir les adresses des serveurs DNS automatiquement », puis ipconfig /flushdns.",
        action_level=3,
        rollback="Configuration initiale enregistrée (ipconfig /all > fichier) : DNS 192.168.1.250 à ressaisir si besoin.",
        impact="Poste du gérant seulement ; modification faite pendant sa pause.",
        evidence="Sortie de nslookup et de ipconfig /all enregistrées avant la modification.",
        validation=(
            "nslookup www.exemple.be répond par le serveur 192.168.1.1.",
            "Les sites et Outlook fonctionnent ; un autre poste n'a pas été modifié.",
        ),
        escalation="Non ; signaler au responsable les autres postes éventuellement configurés à la main.",
        conclusion=(
            "Internet répond par adresse IP mais pas par nom, et le DNS du poste est l'ancien serveur retiré "
            "(192.168.1.250 au lieu de 192.168.1.1) : DNS manuel obsolète. Repassé en automatique, configuration "
            "initiale conservée, résolution validée."
        ),
    ),
    Case(
        key="D5",
        theme="partage",
        title="« Accès refusé » sur le partage Projets",
        context=(
            "Bureau d'architectes Ligne (fictif). Léa a changé de service lundi : de l'accueil au service Projets. "
            "Elle ne peut pas ouvrir \\\\SRV-FICH\\Projets ; ses nouveaux collègues y travaillent normalement. Le "
            "technicien interne n'a pas les droits d'administration du domaine."
        ),
        symptoms=("message à l'ouverture de \\\\SRV-FICH\\Projets", "une seule utilisatrice", "depuis son changement de service"),
        hypotheses=(
            "serveur injoignable ou chemin erroné",
            "compte de Léa absent du groupe GG-Projets",
            "permissions du dossier modifiées pour tout le groupe",
        ),
        tests=(
            DTest("Lire le message exact", 1, 1,
                  ("« Le chemin réseau n'a pas été trouvé »", "« Accès refusé »", "« Accès refusé »"),
                  "« Accès refusé »"),
            DTest("whoami /groups dans la session de Léa", 1, 2,
                  ("—", "GG-Projets absent", "GG-Projets présent"), "GG-Projets absent"),
        ),
        tree=TREE_NETWORK,
        tree_answers=(True, True, True, True, True),
        action="Demander l'ajout de Léa au groupe GG-Projets (administrateur, accord du chef de service), puis fermer et rouvrir sa session.",
        action_level=3,
        rollback="Retrait du groupe si l'accès ouvre plus que prévu ; l'administrateur note la modification.",
        impact="Aucun : simple lecture ; la modification ne touche que le compte de Léa.",
        evidence="Capture du message « Accès refusé » et sortie de whoami /groups, jointes à la demande.",
        validation=(
            "Après fermeture et réouverture de session, Léa ouvre et enregistre un fichier dans Projets.",
            "Le chef de service décide du retrait de ses anciens droits de l'accueil.",
        ),
        escalation="Oui : administrateur du domaine (gestion des groupes), avec l'accord du chef de service.",
        conclusion=(
            "« Accès refusé » prouve que le serveur et le chemin répondent ; GG-Projets absent des groupes de Léa : "
            "le changement de service n'a pas été reporté dans l'annuaire. Ajout demandé avec preuves ; la session "
            "doit être rouverte pour recevoir le nouveau groupe."
        ),
    ),
    Case(
        key="D6",
        theme="panne intermittente",
        title="La réception perd le réseau quelques minutes, plusieurs fois par jour",
        context=(
            "Hôtel Les Tilleuls (fictif). Le PC de la réception perd le réseau quelques minutes, deux ou trois fois "
            "par jour ; les autres postes ne sont pas touchés. La réceptionniste a tenu un journal pendant trois "
            "jours (document du dossier)."
        ),
        symptoms=("coupures de quelques minutes", "deux ou trois fois par jour", "seulement à la réception"),
        hypotheses=(
            "câble réseau abîmé (écrasé par la chaise)",
            "conflit d'adresse IP avec un autre appareil",
            "port du switch défaillant",
        ),
        tests=(
            DTest("Journal Système de Windows aux heures des coupures", 1, 10,
                  ("lien réseau déconnecté", "conflit d'adresse IP détecté", "lien réseau déconnecté"),
                  "lien réseau déconnecté"),
            DTest("Reproduire les conditions : ping -t vers la passerelle en faisant rouler la chaise sur le câble", 2, 10,
                  ("pertes à chaque passage", "—", "aucun lien avec le câble"), "pertes à chaque passage"),
        ),
        tree=TREE_NETWORK,
        tree_answers=(False,),
        action="Remplacer le cordon et le faire passer dans un passe-câble, hors du passage de la chaise.",
        action_level=2,
        rollback="Sans objet : aucun réglage modifié ; ancien cordon conservé et photographié.",
        impact="Test fait entre deux arrivées de clients, réceptionniste prévenue (coupure possible).",
        evidence="Journal de la réceptionniste, extrait du journal Système, photo du câble écrasé.",
        validation=(
            "ping -t sans aucune perte pendant cinq passages de la chaise.",
            "Une semaine de journal sans coupure (panne intermittente : jamais validée sur un seul essai).",
        ),
        escalation="Non.",
        conclusion=(
            "Le journal montre une coupure à chaque fois que la chaise recule vers l'imprimante, et le journal "
            "Système un « lien déconnecté » : la panne devient reproductible en roulant sur le câble. Cordon "
            "remplacé et protégé ; validation sur une semaine."
        ),
    ),
)
CASES_BY_KEY = {c.key: c for c in CASES}

# Journal du dossier D6 (conditions de reproduction).
D6_HEADER = ("Jour", "Heure", "Activité de la réceptionniste", "Autres postes coupés", "Coupure")
D6_ROWS: tuple[tuple[str, ...], ...] = (
    ("Lundi", "9 h 10", "recule sa chaise vers l'imprimante", "non", "oui"),
    ("Lundi", "11 h 30", "saisie d'une réservation", "non", "non"),
    ("Lundi", "15 h 45", "recule sa chaise vers l'imprimante", "non", "oui"),
    ("Mardi", "10 h 05", "appel téléphonique", "non", "non"),
    ("Mardi", "14 h 20", "recule sa chaise vers l'imprimante", "non", "oui"),
    ("Mercredi", "8 h 50", "saisie d'une réservation", "non", "non"),
)
D6_FACTORS = common_factors(D6_HEADER, D6_ROWS, outcome="Coupure", failure="oui")

# =============================================================================================
# 9. Schémas
# =============================================================================================


def ladder_svg() -> str:
    """Échelle d'invasivité : un niveau par ligne, du plus léger (haut) au plus lourd (bas),
    avec ses exemples ; le numéro du niveau est écrit (la couleur n'est qu'un repère)."""
    width, x0, num_w = 400, 6, 40
    fills = ("#e9f5ec", "#e9f5ec", "#e8f0fb", "#fff3c4", "#fde8d4", "#fbecec")
    parts: list[str] = []
    y = 6
    for level in LEVELS:
        name_lines = _wrap(level.name, 34)
        ex_lines = _wrap(level.examples, 46)
        h = 12 + 15 * len(name_lines) + 14 * len(ex_lines)
        parts.append(
            f'<rect data-level="{level.number}" x="{x0}" y="{y}" width="{width - 2 * x0}" height="{h}" rx="6" '
            f'fill="{fills[level.number]}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + num_w // 2, y + h // 2 + 6, [str(level.number)], size=18, weight="700",
                                 anchor="middle"))
        parts.append(_text_lines(x0 + num_w + 6, y + 17, name_lines, size=12.5, weight="700", step=15))
        parts.append(_text_lines(x0 + num_w + 6, y + 17 + 15 * len(name_lines), ex_lines, size=11, step=14))
        y += h + 4
    parts.append(_text_lines(x0, y + 12, ["↓ plus invasif : plus de précautions avant le test"], size=11, weight="700"))
    return _svg(width, y + 20, parts)


def stack_svg(title: str, layers: tuple[tuple[str, str, str], ...]) -> str:
    """Pile de couches dessinée de bas (couche 1) en haut, avec le test typique de chacune."""
    width, x0, gap, top = 400, 6, 6, 30
    blocks = [(_wrap(content, 54), _wrap(f"Test : {test}", 54)) for _n, content, test in layers]
    heights = [22 + 13 * (len(c) + len(t)) for c, t in blocks]
    parts = [_text_lines(width // 2, 18, [title], size=13, weight="700", anchor="middle")]
    y = top
    for i in reversed(range(len(layers))):  # la couche 1 est dessinée en bas
        name = layers[i][0]
        content, test = blocks[i]
        h = heights[i]
        parts.append(
            f'<rect data-layer="{i + 1}" x="{x0 + 22}" y="{y}" width="{width - 2 * x0 - 22}" height="{h}" rx="6" '
            f'fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>'
        )
        parts.append(_text_lines(x0 + 30, y + 16, [f"{i + 1}. {name}"], size=12, weight="700"))
        parts.append(_text_lines(x0 + 30, y + 31, content + test, size=11, step=13))
        y += h + gap
    bottom = y
    parts.append(_arrow_up(x0 + 10, bottom - gap, top))
    parts.append(_text_lines(x0, bottom + 14, ["↑ on valide chaque couche avant la suivante"],
                             size=11, weight="700"))
    return _svg(width, bottom + 22, parts)


def _arrow_up(x: int, y1: int, y2: int) -> str:
    return (
        f'<path d="M{x} {y1} V{y2 + 4}" stroke="{_STROKE}" stroke-width="2"/>'
        f'<path d="M{x - 6} {y2 + 10} L{x} {y2 + 2} L{x + 6} {y2 + 10}" fill="none" stroke="{_STROKE}" stroke-width="2"/>'
    )


def cross_svg() -> str:
    """Tableau 2 × 2 du test croisé : lignes = élément suspect sur un poste sain (fonctionne ou
    non), colonnes = élément sain sur le poste suspect ; chaque case = conclusion calculée."""
    head_w, cell_w, head_h, cell_h = 128, 132, 64, 78
    x0, y0 = 6, 6
    width, height = x0 + head_w + 2 * cell_w + 6, y0 + head_h + 2 * cell_h + 8
    fills = {CROSS_PART: "#fbecec", CROSS_HOST: "#fff3c4", CROSS_BOTH: "#fde8d4", CROSS_NONE: "#e8f0fb"}
    parts = [
        f'<rect x="{x0}" y="{y0}" width="{head_w}" height="{head_h}" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>',
        _text_lines(x0 + 6, y0 + 16, ["A = suspect sur", "poste sain ↓", "B = sain sur", "poste suspect →"], size=10.5,
                    weight="700", step=13),
    ]
    for j, b_ok in enumerate((True, False)):
        x = x0 + head_w + j * cell_w
        parts.append(f'<rect x="{x}" y="{y0}" width="{cell_w}" height="{head_h}" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>')
        parts.append(_text_lines(x + cell_w // 2, y0 + 36, ["B fonctionne" if b_ok else "B échoue"], size=12,
                                 weight="700", anchor="middle"))
    for i, a_ok in enumerate((True, False)):
        y = y0 + head_h + i * cell_h
        parts.append(f'<rect x="{x0}" y="{y}" width="{head_w}" height="{cell_h}" fill="{_SOFT}" stroke="{_STROKE}" stroke-width="1.5"/>')
        parts.append(_text_lines(x0 + head_w // 2, y + cell_h // 2 + 4, ["A fonctionne" if a_ok else "A échoue"],
                                 size=12, weight="700", anchor="middle"))
        for j, b_ok in enumerate((True, False)):
            verdict = cross_test(a_ok, b_ok)
            lines = _wrap(verdict, 19)
            x = x0 + head_w + j * cell_w
            parts.append(
                f'<rect data-cross="{int(a_ok)}{int(b_ok)}" x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" '
                f'fill="{fills[verdict]}" stroke="{_STROKE}" stroke-width="1.5"/>'
            )
            parts.append(_text_lines(x + cell_w // 2, y + cell_h // 2 - (len(lines) - 1) * 7 + 4, lines, size=11,
                                     step=14, anchor="middle"))
    return _svg(width, height, parts)


def _cross_alt() -> str:
    cells = []
    for a_ok in (True, False):
        for b_ok in (True, False):
            a = "A fonctionne" if a_ok else "A échoue"
            b = "B fonctionne" if b_ok else "B échoue"
            cells.append(f"{a} et {b} : {cross_test(a_ok, b_ok)}")
    return ("Test croisé. A = élément suspect monté sur un poste sain ; B = élément sain monté sur le poste suspect. "
            + " ; ".join(cells) + ".")


def _proc_figure(key: str, number: int, title: str, steps: tuple[tuple[str, str], ...], caption: str) -> Figure:
    return Figure(
        key=key,
        title=f"Procédure {number} — {title}",
        alt=f"{len(steps)} étapes : " + " ; ".join(f"{i}. {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1)),
        caption=caption,
        svg=step_flow_svg(steps),
    )


def tree_alt(tree: Tree, questions: tuple[tuple[str, str], ...] | None = None) -> str:
    qs = questions or tree.questions
    return (f"Arbre de décision « {tree.title} ». Départ : {tree.start} "
            + " ".join(f"{i}. {q} Si non : {n}" for i, (q, n) in enumerate(qs, start=1))
            + f" Si tout est oui : {tree.final}")


def _tree_figure(tree: Tree, number: int) -> Figure:
    return Figure(
        key=f"pr27-arbre-{tree.key}",
        title=f"Arbre {number} — {tree.title}",
        alt=tree_alt(tree),
        caption="On descend tant que la réponse est « oui » ; au premier « non », on suit la piste de droite.",
        svg=decision_tree_svg(tree.questions, tree.final),
    )


METHOD_FIGURE = _proc_figure("pr27-cycle-diagnostic", 1, PROCEDURES[0][0], METHOD_STEPS,
                             "Chaque test est choisi pour départager des hypothèses ; on écrit le résultat attendu avant.")
EVIDENCE_FIGURE = _proc_figure("pr27-procedure-preuves", 2, PROCEDURES[1][0], EVIDENCE_STEPS,
                               "Avant de changer quoi que ce soit : ce qui est modifié ne peut plus être observé.")
ROLLBACK_FIGURE = _proc_figure("pr27-procedure-retour-arriere", 3, PROCEDURES[2][0], ROLLBACK_STEPS,
                               "Une modification sans retour arrière préparé est un pari sur le poste du client.")
DHCP_FIGURE = _proc_figure("pr27-procedure-dhcp", 4, PROCEDURES[3][0], DHCP_STEPS,
                           "Chaque étape change une seule variable : la prise, le poste ou le port.")
LADDER_FIGURE = Figure(
    key="pr27-echelle-invasivite",
    title="Échelle d'invasivité des tests (0 à 5)",
    alt="Six niveaux, du moins au plus invasif : "
    + " ; ".join(f"{lv.number}. {lv.name} (ex. : {lv.examples})" for lv in LEVELS) + ".",
    caption="Convention du cours : on commence en haut de l'échelle ; chaque niveau exige plus de précautions.",
    svg=ladder_svg(),
)
NET_LAYERS_FIGURE = Figure(
    key="pr27-couches-reseau",
    title="Approche par couches — réseau",
    alt="Cinq couches de bas en haut, avec un test pour chacune : "
    + " ; ".join(f"{i}. {n} ({c}) — test : {t}" for i, (n, c, t) in enumerate(NET_LAYERS, start=1)) + ".",
    caption="Une couche ne fonctionne que si toutes celles du dessous fonctionnent.",
    svg=stack_svg("Couches réseau (de bas en haut)", NET_LAYERS),
)
PC_LAYERS_FIGURE = Figure(
    key="pr27-couches-poste",
    title="Approche par couches — poste de travail",
    alt="Six couches de bas en haut, avec un test pour chacune : "
    + " ; ".join(f"{i}. {n} ({c}) — test : {t}" for i, (n, c, t) in enumerate(PC_LAYERS, start=1)) + ".",
    caption="Même logique pour un poste : de l'alimentation jusqu'à l'application et au compte.",
    svg=stack_svg("Couches du poste (de bas en haut)", PC_LAYERS),
)
CROSS_FIGURE = Figure(
    key="pr27-test-croise",
    title="Interpréter un test croisé",
    alt=_cross_alt(),
    caption="Deux montages croisés suffisent à dire si la panne suit l'élément ou reste sur le poste.",
    svg=cross_svg(),
)
TREE_FIGURES: tuple[Figure, ...] = tuple(_tree_figure(t, i) for i, t in enumerate(TREES, start=1))

PR27_FIGURES: tuple[Figure, ...] = (
    METHOD_FIGURE,
    LADDER_FIGURE,
    NET_LAYERS_FIGURE,
    PC_LAYERS_FIGURE,
    CROSS_FIGURE,
    *TREE_FIGURES,
    EVIDENCE_FIGURE,
    ROLLBACK_FIGURE,
    DHCP_FIGURE,
)

# Schémas à compléter (exercices), servis en fichiers statiques comme PR18 à PR26 ------------

MARKS = ("①", "②", "③", "④")


def _blank_tree(tree: Tree, blank_numbers: tuple[int, ...]) -> tuple[tuple[tuple[str, str], ...], dict[str, str]]:
    """Remplace la piste « si non » des questions données (numéros 1…) par ①, ②… ; renvoie
    l'arbre à afficher et les réponses attendues."""
    marks = dict(zip(blank_numbers, MARKS, strict=False))
    shown = tuple((q, marks.get(i, n)) for i, (q, n) in enumerate(tree.questions, start=1))
    answers = {marks[i]: tree.questions[i - 1][1] for i in blank_numbers}
    return shown, answers


NET_BLANK_NUMBERS = (1, 2, 3, 5)
NET_BLANK_QUESTIONS, NET_BLANK_ANSWERS = _blank_tree(TREE_NETWORK, NET_BLANK_NUMBERS)
NET_BLANK_FIGURE = Figure(
    key="pr27-arbre-reseau-a-completer",
    title="Arbre réseau à compléter",
    alt=tree_alt(TREE_NETWORK, NET_BLANK_QUESTIONS),
    caption="Schéma à compléter : piste à suivre en ①, ②, ③ et ④ quand la réponse est « non ».",
    svg=decision_tree_svg(NET_BLANK_QUESTIONS, TREE_NETWORK.final),
)
BOOT_BLANK_NUMBERS = (1, 3, 4, 5)
BOOT_BLANK_QUESTIONS, BOOT_BLANK_ANSWERS = _blank_tree(TREE_BOOT, BOOT_BLANK_NUMBERS)
BOOT_BLANK_FIGURE = Figure(
    key="pr27-arbre-demarrage-a-completer",
    title="Arbre de démarrage à compléter",
    alt=tree_alt(TREE_BOOT, BOOT_BLANK_QUESTIONS),
    caption="Schéma à compléter : piste à suivre en ①, ②, ③ et ④ quand la réponse est « non ».",
    svg=decision_tree_svg(BOOT_BLANK_QUESTIONS, TREE_BOOT.final),
)

STATIC_FIGURES: tuple[tuple[Figure, str], ...] = (
    (NET_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr27-arbre-reseau-a-completer.svg"),
    (BOOT_BLANK_FIGURE, f"{STATIC_DIR_REF}/pr27-arbre-demarrage-a-completer.svg"),
)
STATIC_BY_KEY = {figure.key: (figure, path) for figure, path in STATIC_FIGURES}


def static_svg(figure: Figure) -> str:
    """Contenu exact du fichier statique d'un schéma (même règle que PR18 à PR26)."""
    head_end = figure.svg.index(">") + 1
    return (
        figure.svg[:head_end]
        + f"<title>{escape(figure.title)}</title><desc>{escape(figure.alt)}</desc>"
        + figure.svg[head_end:]
        + "\n"
    )
