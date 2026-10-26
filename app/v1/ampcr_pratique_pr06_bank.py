"""PR06 « Diagnostic des pannes matérielles » — exercices corrigés et mini-examen (ticket #193).

Une seule source pour le cours ET la banque :
- `PRACTICE_ITEMS` : les 12 exercices corrigés du cours (≥ 8 scénarios professionnels,
  ≥ 3 analyses de documents), affichés dans le cours avec leur corrigé replié, et proposés
  dans « S'entraîner » (correction après soumission, moteur existant) ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points par question),
  uniquement dans l'onglet « Examen blanc », jamais affichées dans le cours.

Les deux réserves sont séparées par `QuestionVersion.prompt_version`
(`ampcr-pratique-pr06:practice` / `…:exam`, voir `app.v1.ampcr_pratique_bank`). Chaque
question donne toutes les informations nécessaires ; les documents sont des supports
fictifs, identifiés comme tels. Le barème est transmis au correcteur en proportion des
points de la question : une réponse juste formulée autrement est acceptée (aucun mot-clé
exigé).
"""

from dataclasses import dataclass

from app.v1.ampcr_pratique_format import (
    ExerciseDocument,
    PracticalExercise,
    ScoringCriterion,
    validate_exercise,
)

USAGE_PRACTICE = "practice"
USAGE_EXAM = "exam"
PR06_CODE = "PR06"

# Consigne commune ajoutée à chaque barème transmis au correcteur.
ACCEPTANCE_RULE = (
    "Accepter toute formulation techniquement équivalente : aucun mot-clé n'est exigé tel quel. "
    "Retirer des points pour une action dangereuse (manipulation sous tension, ouverture d'un "
    "bloc d'alimentation ou d'une batterie) ou destructive pour les données (formatage, "
    "réinstallation, réparation de disque) proposée sans sauvegarde ni accord, et pour une "
    "conclusion catégorique non justifiée par un test."
)


@dataclass(frozen=True)
class Classification:
    categories: tuple[str, ...]
    elements: tuple[str, ...]
    correct: tuple[int, ...]


@dataclass(frozen=True)
class Ordering:
    """Remise en ordre d'une procédure (ticket #194, PR11) : `steps` dans l'ordre affiché
    (jamais l'ordre attendu), `correct` = indices de `steps` dans l'ordre attendu."""

    steps: tuple[str, ...]
    correct: tuple[int, ...]


@dataclass(frozen=True)
class PR06Item:
    key: str  # E01..E12 (exercices) / X01..X10 (mini-examen)
    usage: str
    title: str
    question_type: str  # short_answer | long_answer | document_analysis | classification | ordering
    requirement_ids: tuple[str, ...]
    kind: str  # « scénario » | « analyse de document »
    context: str
    instructions: tuple[str, ...]
    criteria: tuple[ScoringCriterion, ...]
    correction: tuple[str, ...]  # corrigé étape par étape
    documents: tuple[ExerciseDocument, ...] = ()
    classification: Classification | None = None
    ordering: Ordering | None = None

    @property
    def total_points(self) -> float:
        return sum(c.points for c in self.criteria)

    @property
    def prompt(self) -> str:
        """Énoncé autonome d'une seule tenue (affiché tel quel dans les sessions)."""
        steps = " ".join(f"{i}) {text}" for i, text in enumerate(self.instructions, start=1))
        return f"{self.context} À faire : {steps}"

    def as_exercise(self) -> PracticalExercise:
        return PracticalExercise(
            code=self.key,
            title=self.title,
            requirement_ids=self.requirement_ids,
            context=self.context,
            documents=self.documents,
            instructions=self.instructions,
            criteria=self.criteria,
            justified_correction=" ".join(self.correction),
        )

    def rubric(self) -> str:
        total = self.total_points
        lines = [f"Barème (question notée sur {total:g} points ; noter en proportion) :"]
        for c in self.criteria:
            share = round(100 * c.points / total)
            lines.append(f"- {c.label} ({c.points:g} pt, soit {share} % de la question) : {c.expected}")
        lines.append("Corrigé de référence : " + " ".join(self.correction))
        lines.append(ACCEPTANCE_RULE)
        return "\n".join(lines)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


# =============================================================================================
# 12 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Recueillir les informations au comptoir",
        question_type="long_answer",
        requirement_ids=("AP-15", "AP-C01"),
        kind="scénario",
        context=(
            "Mme Lambert, gérante d'un petit cabinet comptable, dépose son PC de bureau à "
            "l'atelier et dit seulement : « Il ne marche plus, il me le faut pour demain. » Tu "
            "n'as pas encore allumé ni ouvert l'ordinateur."
        ),
        instructions=(
            ("Rédige au moins six questions à poser à la cliente avant toute intervention, en "
             "indiquant pour chacune ce qu'elle t'apprend."),
            "Indique ce que tu notes ou fais valider par écrit avant d'ouvrir la machine.",
        ),
        criteria=(
            _c("Symptôme exact", 1, "Ce qui se passe à l'allumage (rien, voyant, ventilateurs, bips, image, message) et le texte exact d'un éventuel message."),
            _c("Chronologie et changements", 1, "Depuis quand, en permanence ou par intermittence, et ce qui a changé juste avant (orage, déménagement, chute, liquide, ajout de matériel, mise à jour)."),
            _c("Données", 1, "Présence de données importantes, existence et date d'une sauvegarde, comptes ou mots de passe nécessaires aux tests."),
            _c("Autorisations et traçabilité", 1, "Fiche d'entrée : état initial, numéro de série, accessoires, coordonnées ; accord écrit avant toute action coûteuse ou risquée pour les données."),
        ),
        correction=(
            "1. « Que se passe-t-il exactement quand vous appuyez sur le bouton ? » : situe la panne sur la chaîne de démarrage (rien du tout, ventilateurs sans image, message).",
            "2. « Un message ou des bips ? Pouvez-vous me le lire ou le photographier ? » : un message exact vaut mieux qu'un souvenir approximatif.",
            "3. « Depuis quand ? Toujours ou de temps en temps ? » : une panne intermittente se teste autrement (reproduction, journaux).",
            "4. « Qu'est-ce qui a changé juste avant ? » (orage, déménagement, chute, liquide, nouveau matériel, mise à jour) : la cause est souvent là.",
            "5. « Y a-t-il des données importantes, et une sauvegarde récente ? » : fixe la priorité et interdit toute action risquée sans accord.",
            "6. « Le PC sert-il dans un environnement particulier ? » (poussière, chaleur, multiprise surchargée) : oriente vers surchauffe ou alimentation.",
            "Avant d'ouvrir : remplir la fiche d'entrée (état extérieur, numéro de série, accessoires laissés, coordonnées, symptôme décrit par la cliente) et faire signer l'accord pour le diagnostic, en précisant qu'aucune action touchant aux données ou entraînant un coût ne sera faite sans nouvel accord.",
        ),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Séparer observation, hypothèse, test, résultat et conclusion",
        question_type="classification",
        requirement_ids=("AP-15", "AP-C01"),
        kind="scénario",
        context=(
            "Un collègue a noté son intervention sur un PC qui ne s'allume plus, mais ses notes "
            "mélangent tout. Pour un compte rendu clair, chaque phrase doit être rangée dans la "
            "bonne catégorie de la démarche de diagnostic."
        ),
        instructions=(
            ("Classe chacune des cinq phrases du collègue dans la catégorie qui lui correspond : "
             "observation, hypothèse, test, résultat ou conclusion."),
        ),
        criteria=(
            _c("Classement", 5, "Bloc d'atelier = test ; bloc d'origine défectueux = conclusion ; voyant éteint = observation ; logo affiché = résultat ; bloc peut-être hors service = hypothèse (1 point par phrase)."),
        ),
        correction=(
            "« Le voyant vert de la carte mère est éteint, prise branchée » est une observation : un fait constaté, sans interprétation.",
            "« Le bloc d'alimentation est peut-être hors service » est une hypothèse : une cause possible, encore à vérifier.",
            "« Je branche un bloc de l'atelier connu fonctionnel » est un test : une action qui permet de vérifier l'hypothèse.",
            "« Avec ce bloc, le logo du firmware s'affiche » est le résultat du test.",
            "« Le bloc d'origine est défectueux » est la conclusion : elle n'est permise qu'après le test et son résultat.",
        ),
        classification=Classification(
            categories=("Observation", "Hypothèse", "Test", "Résultat", "Conclusion"),
            elements=(
                "Je branche le PC sur un bloc d'alimentation de l'atelier connu fonctionnel.",
                "Le bloc d'alimentation d'origine est défectueux.",
                "Le voyant vert de la carte mère est éteint, prise branchée.",
                "Avec le bloc de l'atelier, les ventilateurs tournent et le logo du firmware s'affiche.",
                "Le bloc d'alimentation est peut-être hors service.",
            ),
            correct=(2, 4, 0, 3, 1),
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="PC totalement inerte après un orage",
        question_type="long_answer",
        requirement_ids=("AP-15", "AP-C02"),
        kind="scénario",
        context=(
            "Dans une petite école, le PC de la salle des professeurs ne réagit plus depuis "
            "l'orage de la nuit : aucun voyant, aucun ventilateur quand on appuie sur le bouton. "
            "Il est branché sur une multiprise avec l'écran et une imprimante, qui s'allument "
            "normalement. Tu disposes d'un testeur d'alimentation ATX, d'un bloc d'alimentation "
            "de test connu fonctionnel et d'un bracelet antistatique."
        ),
        instructions=(
            "Classe tes tests du plus simple et moins risqué au plus invasif, en justifiant l'ordre.",
            "Pour chaque test, indique comment tu interprètes un résultat positif et un résultat négatif.",
            "Indique ce que tu t'interdis de faire, et pourquoi.",
        ),
        criteria=(
            _c("Ordre des tests", 2, "Câble secteur échangé et interrupteur du bloc sur I ; voyant de veille de la carte ; bouton de façade et son raccordement ; connecteurs ATX 24 et EPS ; testeur d'alimentation ou bloc connu bon ; configuration minimale pour chercher un court-circuit ; carte mère en dernier."),
            _c("Interprétation des résultats", 2, "Écran et imprimante sur la même multiprise : le secteur arrive, mais câble et bloc du PC restent à tester ; testeur sans tension ou PC qui démarre avec le bloc de test : bloc d'origine en cause (surtension probable) ; aucun changement avec le bloc de test : bouton, carte mère ou court-circuit."),
            _c("Sécurité", 1, "Prise retirée avant d'ouvrir, bracelet ESD relié, ne jamais ouvrir le bloc d'alimentation (condensateurs chargés), aucune manipulation sous tension."),
            _c("Prudence de la conclusion", 1, "Un seul changement à la fois, chaque test noté, pas de conclusion sans test ; conseiller une protection contre les surtensions."),
        ),
        correction=(
            "1. Échanger le câble secteur et vérifier l'interrupteur du bloc (sur I) : rien à démonter. Si le PC démarre, le câble était en cause ; sinon on continue.",
            "2. PC débranché puis rebranché, capot ouvert sans toucher aux composants : le voyant de veille de la carte mère (s'il existe) indique si le +5 VSB arrive. Éteint : le bloc ou sa liaison sont suspects ; allumé : le bloc fournit au moins la veille, on regarde le bouton.",
            "3. Prise retirée et bracelet ESD relié : contrôler le câble du bouton sur le connecteur de façade (manuel de la carte) et l'enfichage des connecteurs ATX 24 et EPS.",
            "4. Testeur d'alimentation sur le bloc d'origine : aucune tension ou PWR_OK absent oriente vers le bloc. Contre-test : brancher le bloc de test connu fonctionnel. Si le PC démarre, le bloc d'origine est défectueux (surtension de l'orage probable).",
            "5. Si rien ne change avec le bloc de test : configuration minimale (retirer cartes, disques, périphériques) pour chercher un court-circuit, puis bouton, puis carte mère.",
            "Interdits : ouvrir le bloc d'alimentation (ses condensateurs peuvent rester chargés à une tension dangereuse), manipuler sous tension, remplacer plusieurs pièces d'un coup (on ne saurait plus laquelle était en panne). Conseil final : multiprise avec parafoudre ou onduleur.",
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="LED DRAM allumée après un ajout de mémoire",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-17"),
        kind="analyse de document",
        context=(
            "Un client a ajouté deux barrettes de 8 Go à son PC, qui en avait déjà deux. Depuis, "
            "les ventilateurs tournent, l'écran reste noir et la LED DRAM de la carte mère reste "
            "allumée. Le document 1 est un extrait (fictif) du manuel de la carte ; le document 2 "
            "est ton relevé d'intervention."
        ),
        instructions=(
            "Interprète la LED DRAM à l'aide du document 1.",
            "Explique ce que prouvent les tests 1 et 2 du document 2.",
            "Donne la cause la plus probable, deux solutions et le test final.",
            "Rédige le compte rendu en quatre lignes : constat, cause, action, résultat.",
        ),
        documents=(
            _table(
                "Document 1 — Manuel de la carte mère (extrait fictif) : LED de diagnostic",
                ("LED restée allumée", "Signification donnée par le manuel"),
                ("CPU", "Processeur non détecté ou défaillant"),
                ("DRAM", "Mémoire non détectée ou défaillante"),
                ("VGA", "Carte graphique non détectée ou défaillante"),
                ("BOOT", "Aucun périphérique de démarrage trouvé"),
            ),
            _table(
                "Document 2 — Relevé de l'intervention",
                ("Configuration", "Barrettes installées", "Résultat"),
                ("Avant l'ajout", "2 × 8 Go DDR4-3200 marque A (slots A2, B2)", "Démarrage normal"),
                ("Après l'ajout", "2 × 8 Go marque A + 2 × 8 Go DDR4-2666 marque B (4 slots)", "LED DRAM allumée, pas d'image, même après 5 minutes d'attente"),
                ("Test 1", "2 barrettes marque A seules (A2, B2)", "Démarrage normal, 16 Go"),
                ("Test 2", "2 barrettes marque B seules (A2, B2)", "Démarrage normal, 16 Go"),
            ),
        ),
        criteria=(
            _c("Lecture de la LED", 1, "Selon le manuel, la LED DRAM restée allumée signifie que le POST s'arrête à l'étape mémoire : la mémoire n'est pas initialisée."),
            _c("Apport des tests 1 et 2", 1.5, "Chaque paire fonctionne seule dans les mêmes slots : aucune barrette n'est défectueuse et les slots A2/B2 fonctionnent."),
            _c("Cause et solutions", 1.5, "Incompatibilité du mélange de 4 barrettes différentes (marques, fréquences) ; solutions : firmware à jour et compatibilité vérifiée dans la liste du fabricant, réglage mémoire prudent, ou kit identique (par ex. 2 × 16 Go)."),
            _c("Test final", 1, "Démarrage, 32 Go reconnus (ou la capacité prévue), test mémoire complet sans erreur."),
            _c("Compte rendu", 1, "Constat, cause, action et résultat clairement séparés, sans jargon inutile."),
        ),
        correction=(
            "1. D'après le document 1, la LED DRAM qui reste allumée indique que le POST bloque à l'initialisation de la mémoire. L'attente de 5 minutes exclut un simple entraînement mémoire prolongé.",
            "2. Tests 1 et 2 : chaque paire démarre seule dans A2/B2. Aucune barrette n'est défectueuse et ces slots fonctionnent : remplacer une barrette « au hasard » serait une erreur.",
            "3. Cause la plus probable : le mélange de quatre barrettes de marques et de fréquences différentes n'est pas accepté par la carte (compatibilité). Solutions : mettre le firmware à jour et vérifier la liste de compatibilité du fabricant pour 4 barrettes, régler la mémoire de façon prudente ; ou remplacer par un kit identique (par exemple 2 × 16 Go). Test final : démarrage, capacité totale reconnue, test mémoire complet sans erreur.",
            "4. Compte rendu : Constat : écran noir et LED DRAM après ajout de 2 barrettes. Cause : barrettes non compatibles entre elles en 4 slots (chaque paire fonctionne seule). Action : remplacement par un kit 2 × 16 Go compatible. Résultat : démarrage normal, 32 Go reconnus, test mémoire sans erreur.",
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Ventilateurs en marche, « Aucun signal » à l'écran",
        question_type="short_answer",
        requirement_ids=("AP-15", "AP-17"),
        kind="scénario",
        context=(
            "Un client a assemblé lui-même son PC. Les ventilateurs tournent, la carte graphique "
            "s'éclaire, mais l'écran affiche « Aucun signal ». Le document 1 donne l'inventaire et "
            "les branchements que tu as relevés."
        ),
        instructions=(
            "Donne la cause la plus probable en t'appuyant sur le document.",
            "Indique la correction et la façon de vérifier le résultat.",
        ),
        documents=(
            _table(
                "Document 1 — Inventaire et branchements relevés",
                ("Élément", "Relevé"),
                ("Processeur", "Intel Core i5-12400F (sans circuit graphique intégré, suffixe F)"),
                ("Carte graphique", "Dédiée, emplacement PCIe x16, câble PCIe 8 broches branché"),
                ("Câble de l'écran", "HDMI, branché sur la sortie HDMI du panneau arrière de la carte mère"),
                ("Écran", "Entrée HDMI 1 sélectionnée, écran testé avec un autre PC : fonctionne"),
                ("LED de diagnostic", "Toutes éteintes après 30 secondes (selon le manuel : POST terminé)"),
            ),
        ),
        criteria=(
            _c("Cause", 1.5, "Le câble est sur la sortie vidéo de la carte mère, alors que le processeur n'a pas de circuit graphique intégré : cette sortie ne peut rien afficher."),
            _c("Indice des LED", 0.5, "LED éteintes = POST terminé selon le manuel : ce n'est pas une absence de POST mais un problème de sortie vidéo."),
            _c("Correction", 1, "Brancher l'écran sur une sortie de la carte graphique dédiée."),
            _c("Vérification", 1, "Le logo ou l'écran du firmware apparaît, puis le système démarre."),
        ),
        correction=(
            "Le document dit que le processeur (suffixe F) n'a pas de circuit graphique intégré : la sortie HDMI de la carte mère ne reçoit donc aucune image. Les LED éteintes (POST terminé selon le manuel) et l'écran testé ailleurs confirment qu'il ne s'agit ni d'un arrêt au POST ni de l'écran.",
            "Correction : débrancher le câble de la carte mère et le brancher sur une sortie de la carte graphique dédiée. Vérification : le logo du firmware s'affiche, puis le système démarre.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="SSD M.2 neuf non détecté",
        question_type="short_answer",
        requirement_ids=("AP-15", "AP-17"),
        kind="analyse de document",
        context=(
            "Pour accélérer le PC d'un client, tu installes un SSD M.2 neuf dans l'emplacement "
            "M2_1. Le firmware ne le détecte pas. Le document 1 est un extrait (fictif) du manuel "
            "de la carte mère, le document 2 l'étiquette du SSD."
        ),
        instructions=(
            "Explique pourquoi le SSD n'est pas détecté.",
            "Indique où l'installer et la conséquence à signaler au client.",
            "Explique pourquoi formater ou renvoyer le SSD n'est pas la bonne première réponse.",
        ),
        documents=(
            _table(
                "Document 1 — Manuel de la carte mère (extrait fictif) : emplacements M.2",
                ("Emplacement", "Interfaces acceptées", "Remarque"),
                ("M2_1", "PCIe 4.0 x4 (NVMe) uniquement", "Relié au processeur"),
                ("M2_2", "PCIe 3.0 x4 (NVMe) et SATA", "En mode SATA, le port SATA3_2 est désactivé"),
            ),
            ExerciseDocument(
                title="Document 2 — Étiquette du SSD",
                kind="texte",
                content_text="SSD M.2 2280 — Interface SATA III 6 Gb/s — 1 To",
            ),
        ),
        criteria=(
            _c("Cause", 1.5, "Le SSD est un M.2 SATA ; l'emplacement M2_1 n'accepte que le PCIe (NVMe) : même format physique, interface différente."),
            _c("Bon emplacement", 1, "Installer le SSD dans M2_2, qui accepte le SATA."),
            _c("Conséquence", 1, "Le port SATA3_2 est alors désactivé : déplacer un éventuel disque branché sur ce port."),
            _c("Justification", 0.5, "Le SSD n'est pas forcément défectueux : un disque non détecté ne se formate pas, et la compatibilité se vérifie d'abord."),
        ),
        correction=(
            "L'étiquette indique un SSD M.2 à interface SATA ; le manuel indique que M2_1 n'accepte que le PCIe (NVMe). Le format 2280 est le même, mais l'interface ne l'est pas : le SSD ne peut pas être détecté dans ce slot.",
            "Solution : l'installer dans M2_2, qui accepte le SATA, puis vérifier sa détection dans le firmware. Conséquence à signaler : le port SATA3_2 est alors désactivé ; un disque branché sur ce port doit passer sur un autre port.",
            "Formater est impossible (le disque n'est pas vu) et inutile ; renvoyer le SSD serait une erreur : il n'est pas en panne, c'est une question de compatibilité.",
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="« No boot device found » après un changement de PC",
        question_type="short_answer",
        requirement_ids=("AP-15", "AP-17"),
        kind="scénario",
        context=(
            "Un client récupère le disque dur de son ancien PC (Windows installé en mode BIOS "
            "hérité, disque partitionné en MBR) et le branche comme seul disque dans un PC récent "
            "réglé en démarrage UEFI, CSM désactivé. Au démarrage s'affiche « No boot device "
            "found », alors que le disque apparaît dans la liste des périphériques SATA du "
            "firmware."
        ),
        instructions=(
            "Explique la cause probable.",
            "Propose une solution sans perte de données et indique ce qu'il ne faut pas faire.",
        ),
        criteria=(
            _c("Cause", 1.5, "Le disque est détecté (câblage correct) ; c'est le mode de démarrage qui ne correspond pas : une installation MBR en mode hérité ne démarre pas en UEFI pur, CSM désactivé."),
            _c("Solution", 1.5, "Activer le CSM (mode hérité) si le firmware le propose et choisir l'entrée de démarrage du disque ; ou, après sauvegarde, convertir le disque en GPT avec l'outil prévu (par exemple MBR2GPT de Microsoft)."),
            _c("À ne pas faire", 1, "Ni formatage ni réinstallation réflexe : les données du client sont sur ce disque ; sauvegarder d'abord."),
        ),
        correction=(
            "Le disque apparaît dans le firmware : câbles et disque fonctionnent. Le problème est le mode de démarrage : Windows installé en mode BIOS hérité sur un disque MBR n'a pas de partition système EFI ; un firmware en UEFI pur (CSM désactivé) ne trouve donc aucun chargeur à lancer.",
            "Solution sans perte : activer le CSM ou le démarrage hérité si le firmware le propose, puis choisir le disque dans l'ordre de démarrage. Solution durable, après sauvegarde : convertir le disque en GPT avec l'outil prévu (MBR2GPT sous Windows) puis repasser en UEFI.",
            "À ne pas faire : formater ou réinstaller « pour voir ». On sauvegarde toujours avant une opération sur les partitions.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Redémarrages aléatoires : indices et preuves",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind="analyse de document",
        context=(
            "Le PC d'une graphiste redémarre seul plusieurs fois par semaine, à des moments sans "
            "rapport avec la charge de travail. Tu as relevé le journal système Windows "
            "(document 1), les températures (document 2) et le résultat d'un logiciel de test "
            "mémoire lancé au démarrage (document 3)."
        ),
        instructions=(
            "Classe les éléments des documents en indices et en preuves, en justifiant.",
            "Conclus et décris l'intervention.",
            "Indique le test final.",
        ),
        documents=(
            _table(
                "Document 1 — Journal système Windows (extrait reconstitué)",
                ("Date et heure", "Source", "ID", "Message"),
                ("03/10 10:12", "Kernel-Power", "41", "Le système a redémarré sans s'arrêter correctement au préalable."),
                ("03/10 10:12", "BugCheck", "1001", "Redémarrage après une erreur grave : 0x0000001a (MEMORY_MANAGEMENT)."),
                ("06/10 15:47", "Kernel-Power", "41", "Le système a redémarré sans s'arrêter correctement au préalable."),
                ("06/10 15:47", "BugCheck", "1001", "Redémarrage après une erreur grave : 0x0000000a (IRQL_NOT_LESS_OR_EQUAL)."),
            ),
            _table(
                "Document 2 — Températures relevées",
                ("Composant", "Au repos", "En charge", "Maximum du fabricant"),
                ("Processeur", "38 °C", "71 °C", "100 °C"),
                ("Carte graphique", "45 °C", "68 °C", "90 °C"),
            ),
            _table(
                "Document 3 — Test mémoire (une barrette à la fois)",
                ("Configuration testée", "Passes", "Erreurs"),
                ("Barrettes 1 et 2 (slots A2 et B2)", "2", "14"),
                ("Barrette 1 seule, slot A2", "4", "0"),
                ("Barrette 2 seule, slot A2", "2", "12"),
                ("Barrette 1 seule, slot B2", "4", "0"),
            ),
        ),
        criteria=(
            _c("Indices et preuves", 2, "Kernel-Power 41 : simple constat d'arrêt non propre (indice, pas une cause) ; codes d'arrêt liés à la mémoire : indices orientant vers la RAM (un pilote peut aussi les provoquer) ; températures normales : surchauffe écartée ; erreurs reproductibles de la barrette 2 dans un slot où la barrette 1 n'en fait aucune : preuve."),
            _c("Conclusion", 1.5, "Barrette 2 défectueuse ; slots A2 et B2 fonctionnels (la barrette 1 y passe sans erreur)."),
            _c("Intervention", 1.5, "PC débranché, protection ESD, remplacement de la barrette 2 par une barrette compatible (idéalement identique à la barrette 1)."),
            _c("Test final", 1, "Test mémoire de plusieurs passes sur la configuration complète, puis utilisation suivie et journal sans nouvel arrêt imprévu."),
        ),
        correction=(
            "Indices : l'événement 41 dit seulement que le PC ne s'est pas arrêté proprement ; les codes MEMORY_MANAGEMENT et IRQL_NOT_LESS_OR_EQUAL orientent vers la mémoire, mais un pilote peut aussi les produire. Les températures normales écartent la surchauffe.",
            "Preuve : le test mémoire est reproductible. La barrette 2 fait des erreurs dans le slot A2, où la barrette 1 n'en fait aucune ; la barrette 1 passe aussi sans erreur en B2. C'est donc la barrette 2, pas le slot.",
            "Intervention : PC débranché, bracelet ESD, remplacement de la barrette 2 par une barrette compatible (même génération, même capacité, idéalement identique à la barrette 1).",
            "Test final : plusieurs passes de test mémoire avec les deux barrettes, puis quelques jours d'utilisation sans nouvel événement 41 dans le journal.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Une barrette qui ne rentre pas",
        question_type="short_answer",
        requirement_ids=("AP-17",),
        kind="scénario",
        context=(
            "Un client a commandé en ligne une barrette DDR5 de 16 Go pour son PC de bureau, dont "
            "la carte mère accepte de la DDR4 au format DIMM. Il te l'apporte : la barrette ne "
            "rentre pas dans le slot et il propose d'appuyer plus fort."
        ),
        instructions=(
            "Explique pourquoi la barrette ne rentre pas et pourquoi forcer est exclu.",
            "Indique au moins trois critères pour choisir la bonne barrette et où les vérifier.",
        ),
        criteria=(
            _c("Détrompeur et génération", 1.5, "Chaque génération de DDR a son encoche (détrompeur) à une position différente : la DDR5 n'est ni physiquement ni électriquement compatible avec un slot DDR4."),
            _c("Forcer", 0.5, "Forcer abîme le slot, la barrette, voire la carte mère."),
            _c("Critères de choix", 2, "Génération (DDR4), format (DIMM pour un PC de bureau, SO-DIMM pour un portable), capacité maximale par slot et totale, fréquences acceptées, ECC ou non (la plupart des PC grand public n'acceptent que du non-ECC) ; vérifiés dans le manuel ou la liste de compatibilité du fabricant."),
        ),
        correction=(
            "L'encoche de la barrette (détrompeur) n'est pas au même endroit selon la génération : une DDR5 ne peut pas entrer dans un slot DDR4, et ne fonctionnerait pas de toute façon (tensions et signaux différents). Forcer casserait le slot ou la barrette.",
            "Pour choisir : génération DDR4, format DIMM, capacité acceptée par slot et au total, fréquence supportée, mémoire non-ECC (sauf si la carte et le processeur acceptent l'ECC). On vérifie dans le manuel de la carte mère ou sa liste de compatibilité (QVL), puis on conseille au client de retourner la DDR5.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Batterie de portable gonflée",
        question_type="short_answer",
        requirement_ids=("AP-15", "AP-C02"),
        kind="scénario",
        context=(
            "Une cliente apporte son ordinateur portable : le pavé tactile est soulevé et le "
            "boîtier ne ferme plus bien. En retournant l'appareil, tu vois la coque inférieure "
            "bombée au niveau de la batterie."
        ),
        instructions=(
            "Donne la cause probable et explique le danger.",
            "Décris la conduite à tenir, étape par étape.",
            "Indique ce que tu expliques à la cliente.",
        ),
        criteria=(
            _c("Cause et danger", 1.5, "Batterie lithium-ion gonflée (gaz interne) : risque d'échauffement, de feu ou d'explosion si elle est percée, pliée, chauffée ou chargée."),
            _c("Conduite à tenir", 2, "Débrancher le chargeur, éteindre, ne plus utiliser ni recharger ; aucune pression, ne pas percer ni chauffer ; retrait seulement si la procédure du fabricant le permet sans forcer, sinon service qualifié ; batterie isolée dans un contenant non inflammable, loin de toute matière combustible ; dépôt dans une filière de collecte des piles et batteries."),
            _c("Information de la cliente", 0.5, "Expliquer le danger, ne plus utiliser l'appareil, sauvegarder les données dès que c'est possible sans risque, batterie de remplacement compatible."),
        ),
        correction=(
            "La batterie lithium-ion a gonflé (formation de gaz) : percée, pliée, chauffée ou rechargée, elle peut s'enflammer.",
            "Conduite : débrancher le chargeur, éteindre, ne plus recharger ; ne jamais appuyer sur la coque, percer ou chauffer ; ne retirer la batterie que si la procédure du fabricant le permet sans forcer, sinon confier l'appareil à un service qualifié ; placer la batterie retirée dans un contenant non inflammable, loin des matières combustibles ; la déposer dans une filière de collecte des batteries.",
            "À la cliente : expliquer le risque, déconseiller toute utilisation, proposer de récupérer les données si c'est possible sans danger, puis une batterie de remplacement compatible.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Disque dur qui « clique » et données non sauvegardées",
        question_type="document_analysis",
        requirement_ids=("AP-15",),
        kind="analyse de document",
        context=(
            "Le PC d'un cabinet d'architecte devient très lent et son disque dur (HDD de 2 To) "
            "émet des « clics » réguliers. Les plans des clients des trois derniers mois ne sont "
            "sauvegardés nulle part. Le document 1 reprend le rapport SMART du disque relevé avec "
            "un logiciel de diagnostic."
        ),
        instructions=(
            "Interprète le rapport SMART et le bruit.",
            "Classe tes priorités et décris l'intervention, en justifiant ce que tu ne fais pas.",
            "Indique quand il faut faire appel à un service de récupération de données.",
        ),
        documents=(
            _table(
                "Document 1 — Rapport SMART du disque (extrait)",
                ("Attribut", "Valeur brute", "État affiché"),
                ("Secteurs réalloués (05)", "1 240", "Attention"),
                ("Secteurs en attente de réallocation (C5)", "87", "Attention"),
                ("Secteurs non corrigibles (C6)", "41", "Attention"),
                ("Température", "39 °C", "Bon"),
                ("Heures de fonctionnement", "31 450", "—"),
                ("État global", "Prudence", "—"),
            ),
        ),
        criteria=(
            _c("Interprétation", 1.5, "Nombreux secteurs réalloués, en attente et non corrigibles + clics mécaniques : disque en dégradation. SMART est un indice, pas une garantie, mais ici tout concorde."),
            _c("Priorité aux données", 1.5, "Arrêter d'utiliser le disque ; copier d'abord les données critiques ou cloner le disque avec un outil qui gère les erreurs de lecture, vers un support sain."),
            _c("Actions refusées", 1, "Pas de vérification ou réparation du disque (chkdsk), pas de défragmentation, pas de formatage ni de réinstallation : ces opérations sollicitent un disque mourant."),
            _c("Escalade", 1, "Disque non détecté, clics qui s'aggravent ou copie qui échoue : laboratoire de récupération ; ne jamais ouvrir un disque dur hors salle blanche."),
            _c("Après", 1, "Remplacement du disque, restauration, mise en place d'une sauvegarde régulière vérifiée."),
        ),
        correction=(
            "Le rapport montre des centaines de secteurs réalloués, des secteurs en attente et des secteurs illisibles : la surface se dégrade. Les clics signalent un problème mécanique. SMART n'est qu'un indicateur, mais tout concorde : le disque peut lâcher à tout moment.",
            "Priorité : les données. On arrête d'utiliser le disque, puis on copie d'abord les plans récents, ou on clone le disque avec un outil qui gère les erreurs de lecture vers un disque sain.",
            "Refusés : réparation de disque (chkdsk), défragmentation, formatage, réinstallation. Ces opérations lisent et écrivent beaucoup et peuvent achever le disque.",
            "Si le disque n'est plus détecté, si les clics s'aggravent ou si la copie échoue : on s'arrête et on propose un laboratoire de récupération ; on n'ouvre jamais un disque dur soi-même. Ensuite : nouveau disque, restauration, sauvegarde automatique vérifiée.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Imprimante USB : périphérique, connexion ou logiciel ?",
        question_type="short_answer",
        requirement_ids=("AP-15", "AP-17"),
        kind="scénario",
        context=(
            "À l'accueil d'une agence, l'imprimante USB ne fonctionne plus sur le PC A. Constats : "
            "branchée avec son câble sur le PC B, elle imprime normalement ; sur le PC A, quel que "
            "soit le port USB, le Gestionnaire de périphériques affiche « Périphérique inconnu » "
            "avec un triangle jaune ; une clé USB fonctionne sur ces mêmes ports."
        ),
        instructions=(
            "Dis si la panne vient de l'imprimante, de la connexion ou du logiciel, en justifiant avec chaque constat.",
            "Décris la suite de l'intervention et la vérification.",
        ),
        criteria=(
            _c("Raisonnement par élimination", 2, "Imprimante et câble fonctionnent sur le PC B ; les ports du PC A fonctionnent (clé USB) ; le périphérique est vu mais inconnu : la panne est logicielle, côté pilote du PC A."),
            _c("Intervention", 1.5, "Désinstaller le périphérique inconnu et l'ancien pilote, installer le pilote du fabricant correspondant au modèle et au système, redémarrer si demandé."),
            _c("Vérification", 0.5, "Périphérique reconnu sans triangle, page de test imprimée depuis le PC A."),
        ),
        correction=(
            "L'imprimante et son câble fonctionnent sur le PC B : ce n'est pas le périphérique. Une clé USB fonctionne sur les ports du PC A : ce n'est pas la connexion. Le PC A détecte quelque chose mais ne sait pas quoi : c'est un problème de pilote sur le PC A.",
            "Suite : supprimer le périphérique inconnu et l'ancien pilote, installer le pilote du fabricant adapté au modèle et au système, puis vérifier dans le Gestionnaire de périphériques et imprimer une page de test.",
        ),
    ),
)


# =============================================================================================
# Mini-examen : 10 questions notées sur 2 points (total /20), seulement dans l'onglet « Examen blanc »
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Avant de toucher un composant",
        question_type="short_answer",
        requirement_ids=("AP-C02", "AP-15"),
        kind="scénario",
        context=(
            "Un client te confie sa tour pour remplacer une barrette de mémoire. Quand tu la "
            "reçois, le PC est encore allumé et branché sur le secteur. Ses données sont "
            "importantes pour son travail."
        ),
        instructions=(
            ("Décris, dans l'ordre, ce que tu fais avant de toucher un composant à l'intérieur, "
             "en justifiant chaque mesure."),
        ),
        criteria=(
            _c("Coupure et décharge", 0.8, "Arrêt propre du système, interrupteur du bloc sur 0, câble secteur retiré, appui de quelques secondes sur le bouton pour vider la charge résiduelle."),
            _c("Protection ESD", 0.8, "Bracelet antistatique relié à la masse (ou tapis), composants tenus par les bords, barrettes posées sur ou dans un sachet antistatique."),
            _c("Données et accord", 0.4, "Sauvegarde ou accord du client, état initial noté avant l'ouverture."),
        ),
        correction=(
            "Arrêter proprement le système, couper l'interrupteur du bloc, retirer le câble secteur (le +5 VSB reste présent tant que le PC est branché), appuyer quelques secondes sur le bouton pour vider la charge résiduelle.",
            "Mettre un bracelet antistatique relié à la masse, tenir les barrettes par les bords, les poser sur un sachet antistatique. Avant d'ouvrir : noter l'état initial et vérifier la sauvegarde ou l'accord du client.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Absence d'image ou absence de POST ?",
        question_type="short_answer",
        requirement_ids=("AP-15",),
        kind="scénario",
        context=(
            "Sur un PC de bureau, les ventilateurs tournent mais l'écran affiche « Aucun signal ». "
            "Ton collègue conclut aussitôt : « La carte mère est morte. »"
        ),
        instructions=(
            ("Explique pourquoi cette conclusion est prématurée et donne, dans l'ordre, trois "
             "vérifications simples qui distinguent un problème d'affichage d'une absence de POST."),
        ),
        criteria=(
            _c("Conclusion prématurée", 0.6, "Des ventilateurs qui tournent ne prouvent pas le POST, et « Aucun signal » dit seulement que l'écran ne reçoit rien, pas pourquoi ; aucune pièce n'a été testée."),
            _c("Vérifications ordonnées", 1.4, "Écran, entrée et câble testés (autre source ou autre câble) ; sortie vidéo correcte (carte graphique dédiée ou carte mère) ; indicateurs du POST (LED, bips, code) lus dans le manuel, ou signes que le système démarre (activité disque, son)."),
        ),
        correction=(
            "Les ventilateurs tournent dès que le bloc est allumé, même si le POST échoue ; « Aucun signal » indique seulement que l'écran ne reçoit pas d'image. Rien ne prouve encore que la carte mère est en cause.",
            "Vérifications : 1) l'écran, son entrée et son câble avec une autre source ; 2) le câble branché sur la bonne sortie (carte graphique dédiée si elle existe) ; 3) les LED, bips ou codes POST interprétés avec le manuel de la carte. Si le système démarre sans image (activité disque, son), c'est l'affichage ; si le POST s'arrête, on passe à la configuration minimale.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Conclure un diagnostic de PC inerte",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-C01"),
        kind="analyse de document",
        context=(
            "Dans un bureau, un PC ne présente aucun signe de vie quand on appuie sur le bouton. "
            "Tu as réalisé les tests du document 1, dans cet ordre."
        ),
        instructions=(
            "Conclus en distinguant le constat, la cause et le test qui la confirme.",
            "Décris l'intervention et le test final.",
            "Rédige le compte rendu destiné au client en cinq lignes au maximum.",
        ),
        documents=(
            _table(
                "Document 1 — Relevé de diagnostic",
                ("Test", "Résultat"),
                ("1. Lampe branchée sur la même prise", "La lampe s'allume"),
                ("2. Câble secteur remplacé par un câble de l'atelier", "Aucun changement"),
                ("3. Interrupteur du bloc d'alimentation", "Sur I"),
                ("4. Voyant de veille de la carte mère", "Éteint"),
                ("5. Testeur d'alimentation ATX sur le bloc d'origine", "Aucune tension affichée"),
                ("6. Bloc de l'atelier connu fonctionnel, branché temporairement", "Le PC démarre, logo du firmware affiché"),
            ),
        ),
        criteria=(
            _c("Conclusion justifiée", 0.8, "Constat : PC inerte, secteur et câble mis hors de cause (tests 1-2) ; cause : bloc d'alimentation d'origine défectueux ; confirmation : testeur sans tension et démarrage avec le bloc connu fonctionnel (tests 5-6)."),
            _c("Intervention", 0.6, "Remplacer le bloc par un modèle de puissance et de connecteurs adaptés, PC débranché, protection ESD ; ne jamais ouvrir ni réparer le bloc."),
            _c("Test final", 0.3, "Démarrage, fonctionnement stable en charge, tensions vérifiées dans le firmware ou par un outil."),
            _c("Compte rendu", 0.3, "Court et compréhensible : panne constatée, cause, action, résultat, conseil."),
        ),
        correction=(
            "Constat : aucun signe de vie. Les tests 1 et 2 mettent hors de cause la prise et le câble ; le voyant de veille éteint oriente vers le bloc. Cause : bloc d'alimentation défectueux, confirmée par le test 5 (aucune tension) et le test 6 (démarrage avec un bloc connu fonctionnel).",
            "Intervention : PC débranché, bracelet ESD, remplacement par un bloc de puissance suffisante et aux connecteurs adaptés ; l'ancien bloc n'est jamais ouvert. Test final : démarrage, stabilité sous charge, tensions contrôlées.",
            "Compte rendu : « Votre PC ne s'allumait plus. La prise et le câble fonctionnaient ; le bloc d'alimentation ne délivrait plus aucune tension. Nous l'avons remplacé par un bloc adapté. Le PC démarre et fonctionne normalement. Conseil : brancher le PC sur une multiprise avec parafoudre. »",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Disque disparu après un nettoyage",
        question_type="short_answer",
        requirement_ids=("AP-15",),
        kind="scénario",
        context=(
            "Après avoir dépoussiéré l'intérieur de son PC, un client obtient au démarrage le "
            "message « Reboot and Select proper Boot device ». Le firmware ne liste plus son "
            "disque SATA, qui contient toutes ses photos."
        ),
        instructions=(
            ("Donne la cause la plus probable, ce que tu vérifies en premier et l'action à ne "
             "surtout pas faire."),
        ),
        criteria=(
            _c("Cause probable", 0.8, "Câble SATA de données ou d'alimentation débranché ou mal enfiché pendant le nettoyage (lien direct avec l'intervention récente)."),
            _c("Vérifications", 0.8, "PC débranché : câbles des deux côtés (disque et carte), autre câble ou autre port, puis détection du disque et ordre de démarrage dans le firmware."),
            _c("À ne pas faire", 0.4, "Ni formatage ni réinstallation : les photos sont sur le disque."),
        ),
        correction=(
            "Le disque a disparu juste après un nettoyage : un câble SATA (données ou alimentation) a très probablement été déplacé.",
            "PC débranché, on contrôle les deux extrémités de chaque câble, on essaie un autre câble ou un autre port, puis on vérifie que le firmware voit le disque et qu'il est premier dans l'ordre de démarrage. Surtout pas de formatage ni de réinstallation : les données du client seraient en danger.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="« Trois bips, c'est la carte graphique »",
        question_type="short_answer",
        requirement_ids=("AP-15",),
        kind="scénario",
        context=(
            "Au téléphone, un client explique que son PC émet trois bips au démarrage et "
            "n'affiche rien. Il a lu sur un forum que « trois bips = carte graphique morte » et "
            "veut en commander une nouvelle."
        ),
        instructions=(
            ("Rédige ta réponse au client et explique la démarche pour interpréter correctement "
             "ces bips."),
        ),
        criteria=(
            _c("Pas de table universelle", 0.8, "La signification des bips dépend du fabricant de la carte ou du firmware : le message du forum peut concerner un tout autre modèle."),
            _c("Démarche", 1.2, "Identifier le modèle de carte mère ; noter le motif exact (bips longs, courts, répétés) ; le chercher dans le manuel ou sur le site du fabricant ; recouper par des tests simples (réinsertion de la RAM, sortie vidéo) avant tout achat."),
        ),
        correction=(
            "Ne commandez rien pour l'instant : les bips n'ont pas la même signification d'une carte mère à l'autre ; le code lu sur un forum peut concerner un autre fabricant.",
            "Démarche : relever le modèle de la carte mère, noter précisément les bips (longs, courts, répétés), chercher ce motif dans le manuel ou sur le site du fabricant, puis confirmer par des tests simples (réinsérer la mémoire, vérifier la sortie vidéo) avant de remplacer une pièce.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Extinctions en jeu",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-17"),
        kind="analyse de document",
        context=(
            "Un PC de jeu s'éteint brutalement après quelques minutes de jeu, jamais en "
            "bureautique. Le document 1 rassemble ton relevé."
        ),
        instructions=(
            "Formule et classe tes hypothèses à partir du document.",
            "Propose le test qui confirme l'hypothèse principale sans ouvrir le bloc d'alimentation.",
            "Indique l'action corrective et la vérification finale.",
        ),
        documents=(
            _table(
                "Document 1 — Relevé de l'intervention",
                ("Élément", "Relevé"),
                ("Bloc d'alimentation", "Étiquette : 450 W"),
                ("Carte graphique", "Fabricant : alimentation recommandée 650 W ; 2 connecteurs PCIe 8 broches, dont un alimenté par un adaptateur Molex"),
                ("Températures en jeu, juste avant l'arrêt", "Processeur 74 °C (maximum fabricant 100 °C) ; carte graphique 71 °C (maximum fabricant 90 °C)"),
                ("Journal Windows", "Kernel-Power 41 à chaque arrêt ; aucun écran bleu"),
            ),
        ),
        criteria=(
            _c("Hypothèses classées", 0.8, "Principale : alimentation insuffisante ou inadaptée sous forte charge (450 W pour 650 W recommandés, adaptateur Molex) ; surchauffe écartée par les températures ; Kernel-Power 41 = arrêt non propre, indice et non cause."),
            _c("Test de confirmation", 0.5, "Même scénario de jeu avec un bloc de puissance adaptée et connu fonctionnel, branché temporairement."),
            _c("Action corrective", 0.4, "Bloc d'au moins la puissance recommandée, avec connecteurs PCIe natifs, sans adaptateur ; ancien bloc jamais ouvert."),
            _c("Vérification", 0.3, "Session de jeu prolongée sans arrêt et journal sans nouvel événement 41."),
        ),
        correction=(
            "Hypothèse principale : le bloc de 450 W est sous-dimensionné pour une carte graphique dont le fabricant recommande 650 W, et un connecteur PCIe passe par un adaptateur Molex : sous forte charge, le bloc se met en protection. La surchauffe est écartée (températures sous les maxima). L'événement 41 confirme seulement un arrêt brutal.",
            "Test : brancher temporairement un bloc de puissance suffisante, connu fonctionnel, et rejouer le même scénario. Action : installer un bloc adapté avec des connecteurs PCIe natifs, sans adaptateur. Vérification : longue session de jeu sans arrêt, journal sans nouvel événement 41.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Nouveau processeur, même socket, plus d'image",
        question_type="short_answer",
        requirement_ids=("AP-17", "AP-15"),
        kind="scénario",
        context=(
            "Un client remplace son processeur par un modèle plus récent, de même socket (AM4), "
            "sans autre changement. Depuis, les ventilateurs tournent mais rien ne s'affiche, et "
            "la LED CPU de la carte reste allumée. Remonté, l'ancien processeur fonctionne "
            "toujours."
        ),
        instructions=(
            "Donne la cause probable, puis explique comment la vérifier et la corriger proprement.",
        ),
        criteria=(
            _c("Cause", 0.8, "Le firmware de la carte est trop ancien pour reconnaître ce processeur : même socket ne veut pas dire compatibilité garantie."),
            _c("Vérification", 0.6, "Liste des processeurs pris en charge par la carte (site du fabricant) et version minimale du firmware, comparée à la version installée."),
            _c("Correction", 0.6, "Mettre le firmware à jour avec l'ancien processeur (ou avec la fonction de mise à jour sans processeur si la carte en dispose), puis remonter le nouveau, avec protection ESD et pâte thermique neuve ; contrôler aussi les broches du processeur."),
        ),
        correction=(
            "L'ancien processeur fonctionne et la LED CPU reste allumée avec le nouveau : la carte ne le reconnaît pas. Cause la plus probable : un firmware trop ancien. Même socket ne garantit pas la compatibilité.",
            "Vérifier dans la liste de compatibilité du fabricant la version de firmware nécessaire et la comparer à la version installée. Corriger : remonter l'ancien processeur, mettre le firmware à jour (ou utiliser la mise à jour sans processeur si la carte la propose), puis installer le nouveau processeur avec de la pâte thermique neuve, en contrôlant ses broches.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Écran bleu MEMORY_MANAGEMENT",
        question_type="short_answer",
        requirement_ids=("AP-15",),
        kind="scénario",
        context=(
            "Un PC équipé de deux barrettes de 8 Go (slots A2 et B2) affiche régulièrement un "
            "écran bleu MEMORY_MANAGEMENT. Tu disposes d'un logiciel de test mémoire démarrant "
            "depuis une clé USB."
        ),
        instructions=(
            ("Décris une procédure qui permet d'établir avec certitude si une barrette (et "
             "laquelle) ou un slot est en cause."),
        ),
        criteria=(
            _c("Outil", 0.5, "Test mémoire hors système (outil sur clé, ou Diagnostic de mémoire Windows), plusieurs passes complètes."),
            _c("Une barrette à la fois", 0.6, "Tester chaque barrette seule, dans le même slot, et noter le résultat."),
            _c("Séparer barrette et slot", 0.6, "Placer une barrette saine dans le slot suspect (et inversement) : si l'erreur suit la barrette, c'est la barrette ; si elle reste sur le slot, c'est le slot."),
            _c("Précautions", 0.3, "Hors tension et protection ESD à chaque échange ; réglages mémoire par défaut (pas de surcadençage) pendant le test."),
        ),
        correction=(
            "Remettre les réglages mémoire par défaut, puis lancer plusieurs passes de test mémoire avec les deux barrettes. Ensuite, PC débranché et protection ESD : tester la barrette 1 seule en A2, puis la barrette 2 seule en A2.",
            "Pour séparer barrette et slot : mettre la barrette sans erreur dans l'autre slot. Si l'erreur suit une barrette, elle est défectueuse ; si elle reste liée à un slot, c'est le slot ou la carte. On note chaque résultat.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="« Lancez une réparation du disque »",
        question_type="long_answer",
        requirement_ids=("AP-15", "AP-C01"),
        kind="scénario",
        context=(
            "La comptable d'une PME t'appelle : son PC est très lent et le disque dur fait des "
            "« clacs » répétés. Les comptes de l'année ne sont sauvegardés nulle part. Elle te "
            "demande de « lancer une réparation du disque » pour gagner du temps."
        ),
        instructions=(
            ("Rédige ta réponse à la cliente et ton plan d'intervention : priorités, actions, "
             "actions refusées avec leur raison, et moment où tu fais appel à un spécialiste."),
        ),
        criteria=(
            _c("Priorité aux données", 0.5, "Arrêter d'utiliser le PC ; les données passent avant la réparation."),
            _c("Refus justifié", 0.5, "Pas de réparation de disque, de défragmentation ni de formatage : ces opérations sollicitent un disque mécaniquement défaillant et peuvent détruire les données."),
            _c("Sauvetage", 0.5, "Copier d'abord les fichiers critiques, ou cloner avec un outil qui gère les erreurs de lecture, vers un support sain."),
            _c("Escalade", 0.3, "Disque non détecté, bruit qui s'aggrave ou copie impossible : laboratoire de récupération ; ne jamais ouvrir le disque."),
            _c("Suite", 0.2, "Remplacement du disque, restauration, sauvegarde régulière."),
        ),
        correction=(
            "« Je vous déconseille la réparation : votre disque montre des signes de panne mécanique, et une réparation le ferait beaucoup travailler. Votre comptabilité passe d'abord. N'utilisez plus le PC d'ici mon passage. »",
            "Plan : copier en premier les comptes de l'année vers un support sain, ou cloner le disque avec un outil qui gère les erreurs de lecture. Refusés : réparation du disque, défragmentation, formatage. Si le disque n'est plus détecté, si les bruits s'aggravent ou si la copie échoue : arrêt et laboratoire de récupération, sans jamais ouvrir le disque. Ensuite : disque neuf, restauration, sauvegarde automatique vérifiée.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Clavier USB : deux situations",
        question_type="short_answer",
        requirement_ids=("AP-15",),
        kind="scénario",
        context=(
            "Le clavier USB d'un poste de travail ne fonctionne plus. Situation A : le clavier "
            "fonctionne sur les autres ports USB du même PC, mais pas sur le port avant gauche. "
            "Situation B : le clavier ne fonctionne sur aucun port de ce PC, mais fonctionne sur un "
            "autre PC ; une souris USB fonctionne sur ce PC."
        ),
        instructions=(
            ("Pour chaque situation, indique si la panne vient du périphérique, de la connexion ou "
             "du logiciel, et l'action suivante."),
        ),
        criteria=(
            _c("Situation A", 1, "Le clavier est bon ; panne de connexion : port avant ou son câble de façade ; inspecter le port et son raccordement à la carte, utiliser un autre port en attendant."),
            _c("Situation B", 1, "Clavier et ports sont bons ; panne logicielle sur ce PC : pilote ou périphérique désactivé ; Gestionnaire de périphériques, réinstallation du pilote."),
        ),
        correction=(
            "Situation A : le clavier marche sur les autres ports, donc il n'est pas en cause ; le défaut est la connexion du port avant gauche (port abîmé ou câble de façade mal raccordé). Action : PC débranché, inspecter le port et son raccordement à la carte ; en attendant, un autre port.",
            "Situation B : le clavier marche ailleurs et les ports de ce PC fonctionnent (souris) : la panne est logicielle sur ce PC. Action : Gestionnaire de périphériques, supprimer et réinstaller le pilote, vérifier que le périphérique n'est pas désactivé.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), barème d'examen de 2 points
    par question, classification cohérente."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and item.classification is None:
            errors.append(f"{item.key} : classification sans données.")
        if item.question_type == "ordering" and (
            item.ordering is None
            or sorted(item.ordering.correct) != list(range(len(item.ordering.steps)))
            or list(item.ordering.correct) == list(range(len(item.ordering.steps)))
        ):
            errors.append(f"{item.key} : remise en ordre invalide ou déjà dans l'ordre attendu.")
        if item.question_type == "document_analysis" and not item.documents:
            errors.append(f"{item.key} : analyse de document sans document.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
    return errors
