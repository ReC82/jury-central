"""EX05 « Examen blanc global standard — épreuve pratique écrite » — les questions notées /100
(ticket #201).

Examen blanc **global** (tout le parcours PR01 → PR30) : un **dossier professionnel cohérent**
par variante — une petite entreprise de 6 postes avec fiche du client, schéma du réseau local,
inventaire du matériel, journal des pannes, relevés et mesures — et **10 situations de 10
points**, à réponse libre, dans la réserve `exam` uniquement (`ampcr-pratique-ex05:exam`) :

| Situation | Domaine | Points |
|---|---|---|
| 1. Poste lent : composants et évolution | Matériel | 10 |
| 2. Disque défaillant : SMART et données | Matériel | 10 |
| 3. Installation de Windows 11 | Systèmes | 10 |
| 4. Installation de Linux | Systèmes | 10 |
| 5. Cordon RJ45 et liaison cuivre | Câblage | 10 |
| 6. Segment coaxial et câble BNC | Câblage | 10 |
| 7. Plan d'adressage IPv4, MAC et IP | Réseau | 10 |
| 8. Partages, droits et imprimante | Réseau | 10 |
| 9. Portable sans Internet | Réseau | 10 |
| 10. Rapport d'intervention | Méthode | 10 |

**Deux variantes de données** (`VARIANTS` : même structure, même barème, entreprise, adresses,
pannes et mesures différentes), toutes deux calculées et vérifiées par les règles des cours
(`app.v1.ampcr_pratique_ex05_figures`). Une session d'examen blanc sert **une variante entière**,
dans l'ordre des situations (`app.v1.ampcr_pratique_bank.select_exam_variant`) : la moins faite
par le candidat, la variante 1 d'abord. Chaque question reprend les documents dont elle a
besoin : elle se résout seule. Situations fictives ; aucune question n'est présentée comme
officielle ou déjà posée par le Jury.
"""

from app.v1.ampcr_pratique_ex05_figures import (
    FIRMWARE_REQUIRED,
    SMART_REPLACE,
    SMART_RULE,
    SMART_WATCH,
    VARIANTS,
    WEB_IP,
    WEB_NAME,
    Variant,
    arp_lines,
    duration_text,
    fr,
    lan_figure,
    lan_figure_file,
    tester_lines,
)
from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _table
from app.v1.ampcr_pratique_pr06_bank import USAGE_EXAM, PR06Item
from app.v1.ampcr_pratique_pr08_figures import ACTIVATES
from app.v1.ampcr_pratique_visuals import T568B

EX05_CODE = "EX05"
EXAM_TOTAL_POINTS = 100
POINTS_PER_QUESTION = 10
SITUATIONS = 10
KIND_DOC = "analyse de document"

# Domaine de chaque situation (répartition annoncée des points) et cours à revoir.
DOMAINS: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("Matériel", (1, 2)),
    ("Systèmes d'exploitation", (3, 4)),
    ("Câblage", (5, 6)),
    ("Réseau", (7, 8, 9)),
    ("Méthode et rapport", (10,)),
)
SITUATION_COURSES: dict[int, tuple[str, ...]] = {
    1: ("PR01", "PR02", "PR05"),
    2: ("PR06", "PR04", "PR28"),
    3: ("PR08", "PR07", "PR03"),
    4: ("PR09", "PR10"),
    5: ("PR15", "PR14", "PR18"),
    6: ("PR16", "PR13"),
    7: ("PR20", "PR19"),
    8: ("PR23", "PR22"),
    9: ("PR24", "PR20"),
    10: ("PR29", "PR26", "PR27"),
}


def item_key(v: Variant, situation: int) -> str:
    return f"V{v.number}Q{situation:02d}"


def _schema(title: str, text: str, image: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="schéma", content_text=text, image=image)


def _levels(matrix: dict[str, dict[str, str]]) -> str:
    return " ; ".join(f"{p} : " + ", ".join(f"{f} {lvl.lower()}" for f, lvl in row.items()) for p, row in matrix.items())


# =============================================================================================
# Documents d'une variante
# =============================================================================================


class Docs:
    """Documents numérotés d'une variante (titres « Variante n, document k — … »)."""

    def __init__(self, v: Variant) -> None:
        self.v = v
        n = v.label
        srv, nas = v.host("SRV-01"), v.host("NAS-01")
        coax = ", ".join(s.name for s in v.coax_bus.stations)
        self.client = _table(
            f"{n}, document 1 — Fiche du client",
            ("Rubrique", "Contenu"),
            ("Client", f"{v.company}, {v.activity} à {v.city} ; 6 personnes, 6 postes ; responsable : {v.manager}"),
            ("Réseau", (f"{v.network} ; box du fournisseur en {v.box_ip} (passerelle, NAT, pare-feu, DNS, DHCP "
                       f"de {v.pool[0]} à {v.pool[1]})")),
            ("Serveur SRV-01", (f"{srv.ip}, Windows Server 2022, serveur de fichiers ; groupe de travail, comptes et "
                               "groupes locaux du serveur")),
            ("NAS-01", f"{nas.ip}, sauvegardes des postes et du serveur"),
            ("Conventions d'adressage", f"{v.printer_ip_rule} ; postes en DHCP sauf exception"),
            ("Ancien matériel", (f"{v.coax_room.capitalize()} : {coax}, reliés par un segment coaxial 10BASE2, "
                                "hors du switch (remplacement prévu l'an prochain)")),
            ("Intervention", f"Contrat de maintenance ; passage du technicien le {v.date}"),
        )
        self.schema = _schema(lan_figure(v).title, lan_figure(v).alt, lan_figure_file(v))
        self.inventory = _table(
            f"{n}, document 3 — Inventaire du matériel",
            ("Poste", "Utilisateur", "Système", "Processeur", "Mémoire", "Stockage", "Année"),
            *((r.name, r.user, r.os, r.cpu, r.ram, r.storage, str(r.year)) for r in v.inventory),
        )
        lap = v.laptop
        self.journal = _table(
            f"{n}, document 4 — Journal des pannes et demandes",
            ("Poste ou zone", "Signalement"),
            (v.slow_post, "Très lent dès que plusieurs logiciels et onglets sont ouverts ; le pointeur se fige"),
            (v.failing.post, ("Gels de plusieurs secondes, fichiers longs à ouvrir, message « Windows a détecté un "
                             "problème de disque dur »")),
            (v.linux_post, "Poste à réinstaller sous Ubuntu 24.04 LTS (logiciel métier disponible sous Linux)"),
            (v.run_post, "Nouvelle prise murale ; le cordon fabriqué par le stagiaire ne donne pas de lien fiable"),
            (v.coax_room.capitalize(), f"{coax} : réseau coupé depuis une manipulation dans le local"),
            (lap.name, "Revenu de chez un autre réparateur : plus d'Internet au bureau, le reste du réseau répond"),
        )
        slow = next(r for r in v.inventory if r.name == v.slow_post)
        self.task_manager = _table(
            f"{n}, document 5 — Gestionnaire des tâches de {v.slow_post}, logiciels habituels ouverts",
            ("Ressource", "Valeur relevée"),
            ("Processeur", f"{slow.cpu} : 38 % d'utilisation"),
            ("Mémoire", (f"{fr(v.ram_used[0])} Go utilisés sur {fr(v.ram_used[1])} Go utilisables "
                        f"({v.ram_used_pct} %) ; emplacements utilisés : {len(v.ram_modules)} sur {v.ram_slots}")),
            ("Disque 0", f"{v.disk_label} : temps d'activité {v.disk_busy_pct} %"),
        )
        m2 = ("1 emplacement M.2 NVMe libre (PCIe 3.0 x4) ; 4 ports SATA" if v.number == 1
              else "1 emplacement M.2 NVMe, occupé par le SSD")
        self.board = _table(
            f"{n}, document 6 — Fiche technique du fabricant de {v.slow_post} (extrait)",
            ("Élément", "Caractéristique"),
            ("Mémoire", (f"{v.ram_slots} emplacements {v.ram_type} ; {v.ram_max_gb} Go au maximum ; double canal "
                        "avec deux barrettes identiques")),
            ("Barrette installée", f"{len(v.ram_modules)} × {v.ram_modules[0]} Go {v.ram_type.split(' (')[0]}"),
            ("Stockage", m2),
        )
        self.smart = _table(
            f"{n}, document 7 — Relevés SMART des disques suspects (CrystalDiskInfo, fictifs)",
            ("Appareil", "Disque", "Heures de fonctionnement", "Secteurs réalloués", "Secteurs en attente",
             "Secteurs illisibles (hors ligne)"),
            *((r.post, r.disk, f"{r.hours:,}".replace(",", " "), str(r.reallocated), str(r.pending),
               str(r.uncorrectable)) for r in v.smart),
            ("Règle", SMART_RULE, "", "", "", ""),
        )
        lic = ("Licence OEM Windows 11 Pro (clé inscrite dans le micrologiciel du PC)" if v.number == 1
               else "Licence numérique Windows 11 Pro liée à ce PC")
        self.firmware = _table(
            f"{n}, document 8 — Réglages du micrologiciel de {v.failing.post} après le remplacement du disque",
            ("Réglage", "Valeur relevée"),
            *((name, v.firmware[name]) for name in FIRMWARE_REQUIRED),
            ("Remarque", ("Le micrologiciel a été remis aux réglages d'usine lors du changement de la pile le mois "
                         "dernier")),
            ("Licence", lic),
        )
        self.iso = _console(
            f"{n}, document 9 — Vérification de l'image téléchargée pour {v.linux_post} (relevé fictif)",
            "$ sha256sum -c SHA256SUMS 2>/dev/null \\", f"    | grep {v.iso_check_line.split(':')[0]}",
            v.iso_check_line,
        )
        self.tester = _console(
            f"{n}, document 10 — Test du cordon fabriqué pour {v.run_post} (testeur fictif)",
            *tester_lines(v.tester_links),
        )
        self.run = _table(
            f"{n}, document 11 — Liaison de la nouvelle prise de {v.run_post}",
            ("Élément", "Valeur"),
            ("Câble installé", "Cat6 U/UTP, du panneau de brassage à la prise murale"),
            ("Lien permanent (panneau → prise)", f"{v.run_permanent_m} m (mesuré au testeur)"),
            ("Cordons", f"{v.run_cords_m[0]} m au panneau, {v.run_cords_m[1]} m au poste"),
            ("Débit visé", "1 Gb/s (1000BASE-T) entre le switch et le poste"),
        )
        bus = v.coax_bus
        rows = []
        for item in bus.items:
            if hasattr(item, "length_m"):
                rows.append(("Tronçon", f"{fr(item.length_m)} m de câble marqué {item.cable}"))
            else:
                rows.append(("Station", f"{item.name} : T BNC fixé directement sur la carte réseau"))
        first, last = bus.stations[0].name, bus.stations[-1].name
        ends = []
        for side, end in ((first, bus.first), (last, bus.last)):
            if end.terminator_ohm is None:
                ends.append((f"Extrémité {side}", "rien n'est vissé sur la sortie libre du T"))
            else:
                ground = ", avec chaînette de mise à la terre" if end.grounded else ""
                ends.append((f"Extrémité {side}", f"terminateur marqué {end.terminator_ohm} Ω{ground}"))
        reading = v.coax_reading
        replace_len = next(s.length_m for s in bus.spans if s.cable != "RG-58") if v.number == 2 else bus.spans[-1].length_m
        self.coax = _table(
            f"{n}, document 12 — Constats sur le segment coaxial du {v.coax_room}",
            ("Élément", "Constat"),
            *rows,
            *ends,
            ("Mesure", (f"Ohmmètre entre l'âme et le blindage, au T de {first}, machines arrêtées : "
                       f"{'infini' if reading is None else fr(reading) + ' Ω'}")),
            ("Demande", (f"Préparer un câble coaxial de {fr(replace_len)} m muni de connecteurs BNC mâles à sertir "
                        f"(longueur du tronçon {bus.stations[-2].name} — {last})")),
        )
        self.arp = _console(f"{n}, document 13 — Table ARP relevée sur SRV-01 (relevé fictif)", *arp_lines(v))
        users = _table(
            f"{n}, document 14 — Comptes et groupes locaux de SRV-01",
            ("Personne", "Fonction", "Groupes"),
            *((p, f, ", ".join(g)) for p, f, g in v.accounts),
        )
        self.accounts = users
        person, folder, _wanted = v.need
        share_rows = []
        for name in v.shares:
            ntfs = ", ".join(f"{g} : {lvl}" for g, lvl in v.ntfs[name].items())
            share_rows.append((name, f"Tout le monde : {'Lecture' if v.shares[name] == 'Lecture' else 'Modifier'}",
                               f"Administrateurs : Contrôle total, {ntfs}"))
        self.shares = _table(
            f"{n}, document 15 — Partages de SRV-01 et autorisations NTFS",
            ("Dossier partagé", "Autorisations du partage", "Autorisations NTFS"),
            *share_rows,
            ("Besoin exprimé", f"{person} doit pouvoir modifier les fichiers de {folder}", "—"),
        )
        screens = v.laptop_screens
        lines: list[str] = []
        for index, screen in enumerate(screens, start=1):
            lines += [f"Relevé {index} :", *screen, ""]
        self.laptop = _console(
            f"{n}, document 16 — Relevés sur {lap.name} au bureau (fictifs)", *lines[:-1],
        )
        self.intervention = _table(
            f"{n}, document 17 — Journal de l'intervention sur {v.failing.post} du {v.date}",
            ("Début", "Fin", "Action"),
            *v.journal,
        )


# =============================================================================================
# Les 10 situations
# =============================================================================================


def _s1(v: Variant, d: Docs) -> PR06Item:
    slow = next(r for r in v.inventory if r.name == v.slow_post)
    user = slow.user.split(" (")[0]
    hdd = "HDD" in v.disk_label
    storage_expected = (
        f"Oui : le disque mécanique ({v.disk_label}) est occupé à {v.disk_busy_pct} % ; la mémoire saturée l'oblige "
        "en plus à écrire le fichier d'échange. Remplacer le HDD par un SSD (NVMe dans l'emplacement M.2 libre, ou "
        "SATA 2,5 pouces), capacité au moins égale aux données, après sauvegarde, par clonage ou réinstallation."
        if hdd else
        f"Non : le {v.disk_label} n'est occupé qu'à {v.disk_busy_pct} %, il n'est pas le goulet ; changer le disque "
        "coûterait sans gain. Seule la mémoire est saturée."
    )
    storage_corr = (
        f"Le stockage freine aussi : le disque mécanique est occupé à {v.disk_busy_pct} %, et comme la mémoire est "
        "pleine, Windows y écrit en plus son fichier d'échange. Je recommande un SSD (NVMe dans l'emplacement M.2 "
        "libre de la fiche, ou SATA 2,5 pouces), d'une capacité au moins égale aux données, installé par clonage ou "
        "par réinstallation après une sauvegarde."
        if hdd else
        f"Le stockage n'est pas en cause : le SSD n'est occupé qu'à {v.disk_busy_pct} %. Le changer coûterait sans "
        "rien améliorer ; seule la mémoire est saturée."
    )
    module = f"1 barrette de {v.ram_added_gb} Go {v.ram_type}"
    return PR06Item(
        key=item_key(v, 1),
        usage=USAGE_EXAM,
        title="Poste lent : lire l'inventaire et proposer une évolution matérielle",
        question_type="document_analysis",
        requirement_ids=("AP-01", "AP-16"),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : {v.slow_post} (poste : {user}) est très lent (document 4). L'inventaire "
            f"est au document 3, le relevé du Gestionnaire des tâches au document 5 et la fiche du fabricant au "
            "document 6. Le budget permet une seule pièce par composant."
        ),
        documents=(d.inventory, d.journal, d.task_manager, d.board),
        instructions=(
            ("À partir des documents 3 et 5, explique le rôle de la mémoire vive et du stockage de ce poste, et ce que "
            "montrent les relevés."),
            ("Propose l'ajout de mémoire le plus utile : pièce exacte (type, format, capacité), emplacement, capacité "
            "totale obtenue et raisons de la compatibilité."),
            "Dis si le stockage doit aussi être changé, en le justifiant par les relevés.",
            "Donne les précautions pendant l'intervention et les contrôles après.",
        ),
        criteria=(
            _c("Lecture des relevés", 3, f"Mémoire vive = espace de travail des programmes ouverts, vidé à l'arrêt ; "
               f"stockage = programmes et fichiers conservés. Relevé : {fr(v.ram_used[0])} Go sur {fr(v.ram_used[1])} "
               f"({v.ram_used_pct} %) → mémoire saturée, Windows déplace des données vers le fichier d'échange sur le "
               f"disque (lenteurs, pointeur figé) ; disque à {v.disk_busy_pct} % ; processeur à 38 % : pas en cause."),
            _c("Mémoire choisie", 3, f"{module} (même type et même format que la barrette en place), dans "
               f"l'emplacement libre ({len(v.ram_modules)} sur {v.ram_slots} utilisés) → {v.ram_after_gb} Go en double "
               f"canal ; ≤ {v.ram_max_gb} Go admis par la fiche ; un autre type (DDR4/DDR5) ou format (DIMM/SO-DIMM) "
               "n'entre pas (détrompeur)."),
            _c("Stockage", 2, storage_expected),
            _c("Précautions et contrôles", 2, "Sauvegarde si le disque est touché ; arrêt complet, débranché"
               + (", batterie déconnectée selon la notice du fabricant" if "portable" in slow.user else "")
               + " ; bracelet antistatique relié à la masse ; barrette tenue par les bords, encoche alignée, clips "
               f"enclenchés. Après : le micrologiciel et le Gestionnaire des tâches affichent {v.ram_after_gb} Go et "
               f"{len(v.ram_modules) + 1} emplacements utilisés, test mémoire (Diagnostic de mémoire Windows), "
               "nouveau relevé avec les logiciels habituels, avis de l'utilisateur."),
        ),
        correction=(
            ("La mémoire vive (RAM) est l'espace de travail du processeur : les programmes ouverts et leurs données y "
            "sont chargés, et elle se vide à l'arrêt. Le stockage conserve le système, les programmes et les fichiers."),
            (f"Le relevé montre {fr(v.ram_used[0])} Go utilisés sur {fr(v.ram_used[1])} Go, soit {v.ram_used_pct} % : la "
            "mémoire est saturée, Windows déplace des pages vers le fichier d'échange sur le disque, d'où les "
            f"lenteurs et le pointeur figé. Le disque est occupé à {v.disk_busy_pct} %, le processeur à 38 % "
            "seulement : il n'est pas en cause."),
            (f"J'ajoute {module}, identique à celle en place, dans l'emplacement libre : le poste passe à "
            f"{v.ram_after_gb} Go et fonctionne en double canal. La fiche admet {v.ram_max_gb} Go ; une barrette d'un "
            "autre type ou d'un autre format n'entrerait pas (encoche) et ne fonctionnerait pas."),
            storage_corr,
            ("Pendant : PC arrêté et débranché (batterie déconnectée sur un portable si la notice le prévoit), bracelet "
            "antistatique relié à la masse, barrette tenue par les bords, encoche alignée, clips enclenchés. Après : "
            f"vérifier {v.ram_after_gb} Go dans le micrologiciel et le Gestionnaire des tâches, lancer le Diagnostic "
            "de mémoire Windows, refaire le relevé avec les logiciels habituels et demander l'avis de l'utilisateur."),
        ),
    )


def _s2(v: Variant, d: Docs) -> PR06Item:
    bad = v.failing
    other = next(r for r in v.smart if r is not bad)
    other_text = ("sain : aucun secteur réalloué, en attente ni illisible" if other.verdict not in (SMART_REPLACE, SMART_WATCH)
                  else f"à surveiller : {other.reallocated} secteurs réalloués, mais aucun en attente ni illisible")
    other_action = ("rien à faire pour ce disque ; la lenteur de ce poste a une autre cause"
                    if other.verdict not in (SMART_REPLACE, SMART_WATCH)
                    else "nouveau relevé dans un mois, vérifier que les sauvegardes sont complètes et prévoir son "
                         "remplacement si le compteur augmente")
    replacement = "SSD SATA 2,5 pouces de 1 To" if "1 To" in bad.disk else "SSD SATA 2,5 pouces de 2 To"
    user = next(r.user for r in v.inventory if r.name == bad.post)
    return PR06Item(
        key=item_key(v, 2),
        usage=USAGE_EXAM,
        title="Disque défaillant : interpréter les relevés SMART et protéger les données",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-01"),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : {bad.post} se fige et affiche un avertissement de disque (document 4). Tu as "
            "relevé l'état SMART des disques suspects (document 7, avec la règle de l'atelier) ; l'inventaire est au "
            f"document 3. Le poste contient les dossiers de travail du {user}, qui ne sont pas tous sur le serveur."
        ),
        documents=(d.inventory, d.journal, d.smart),
        instructions=(
            "Interprète chaque ligne du document 7 avec la règle de l'atelier et donne ta conclusion pour chaque disque.",
            "Indique ce que tu fais en premier pour les données de l'utilisateur, et pourquoi.",
            "Rédige la procédure de remplacement du disque, de la mise hors tension au contrôle dans le micrologiciel.",
            "Choisis le disque de remplacement et justifie ton choix.",
        ),
        criteria=(
            _c("Interprétation", 3, f"{bad.post} ({bad.disk}) : {bad.pending} secteurs en attente et "
               f"{bad.uncorrectable} illisibles > 0 → à remplacer d'urgence"
               + (f" (les {bad.reallocated} réalloués confirment l'usure)" if bad.reallocated else
                  " même sans secteur réalloué : la règle porte sur les secteurs en attente ou illisibles")
               + f" ; {other.post} ({other.disk}) : {other_text}. Conclusion par disque, avec la valeur qui la fonde."),
            _c("Données d'abord", 3, "Sauvegarde immédiate des données utilisateur (dossiers personnels, bureau, "
               f"courriel) vers NAS-01 ou un disque externe, avec l'accord du {user}, en commençant par les plus "
               "importantes ; contrôle de la copie (ouvrir des fichiers) ; éviter tout ce qui sollicite le disque "
               "(défragmentation, chkdsk /r, nombreux redémarrages) ; clonage possible si le disque le permet. "
               "Le disque peut lâcher à tout moment : les données sont irremplaçables, le disque non."),
            _c("Procédure", 2, "Arrêt, débranchement, appui sur le bouton pour décharger ; bracelet antistatique ; "
               "ouvrir, débrancher câbles SATA données et alimentation, déposer le disque ; poser le nouveau "
               "(adaptateur 3,5 pouces si besoin), rebrancher ; refermer ; au démarrage, le micrologiciel détecte le "
               "nouveau disque (modèle, capacité) ; ancien disque conservé ou effacé de façon sûre avec l'accord du "
               "client."),
            _c("Choix", 2, f"{replacement} : même interface SATA, capacité au moins égale, bien plus rapide et sans "
               "pièce mobile (un NVMe n'est possible que si la carte mère a un emplacement M.2)."),
        ),
        correction=(
            f"{bad.post} : {bad.pending} secteurs en attente et {bad.uncorrectable} secteurs illisibles. La règle de "
            "l'atelier dit qu'au-delà de 0 le disque est à remplacer"
            + (f" ; les {bad.reallocated} secteurs déjà réalloués confirment l'usure." if bad.reallocated else
               ", même si aucun secteur n'a encore été réalloué.")
            + f" {other.post} : {other_text} ; {other_action}.",
            (f"Avant toute réparation, je sauvegarde les données du {user} vers NAS-01 (ou un disque externe), avec son "
            "accord, les plus importantes d'abord, et je vérifie la copie en ouvrant des fichiers. Je n'exécute rien "
            "qui sollicite le disque (défragmentation, chkdsk /r) : il peut lâcher à tout moment. Si le disque le "
            "permet, un clonage vers le nouveau disque est possible."),
            ("Remplacement : arrêt complet, câble secteur débranché, appui sur le bouton de démarrage pour décharger ; "
            "bracelet antistatique relié à la masse ; débrancher les câbles SATA (données) et d'alimentation, déposer "
            "l'ancien disque, fixer le nouveau (adaptateur 3,5 pouces si besoin), rebrancher, refermer. Au démarrage, "
            "le micrologiciel doit afficher le nouveau disque avec son modèle et sa capacité."),
            (f"Je choisis un {replacement} : même interface que l'ancien, capacité au moins égale, beaucoup plus rapide "
            "et sans pièce mobile. L'ancien disque est rendu au client ou effacé de façon sûre avec son accord."),
        ),
    )


def _s3(v: Variant, d: Docs) -> PR06Item:
    bad = v.failing
    changes = v.firmware_changes
    keep = [name for name in FIRMWARE_REQUIRED if name not in {c[0] for c in changes}]
    change_text = " ; ".join(f"{name} : {now} → {wanted}" for name, now, wanted in changes)
    keep_text = ", ".join(keep)
    why = {
        "Mode de démarrage": "Windows 11 démarre en UEFI ; le nouveau disque sera en GPT",
        "Démarrage sécurisé (Secure Boot)": "prérequis de Windows 11, protège la chaîne de démarrage",
        "TPM 2.0 (Intel PTT / AMD fTPM)": "prérequis de Windows 11 (clés de chiffrement, BitLocker)",
        "Mode du contrôleur SATA": "en mode RST/RAID, l'installateur ne voit pas le disque sans pilote ; le disque "
                                   "est neuf, passer en AHCI est sans risque (ou charger le pilote RST/VMD)",
    }
    why_text = " ; ".join(f"{name} : {why[name]}" for name, _n, _w in changes)
    result, reason = v.activation
    activates = "Oui, Windows s'activera" if result == ACTIVATES else "Non, Windows ne s'activera pas"
    lic_kind = "OEM" if v.number == 1 else "numérique"
    user = next(r.user for r in v.inventory if r.name == bad.post)
    share = next(iter(v.shares))
    return PR06Item(
        key=item_key(v, 3),
        usage=USAGE_EXAM,
        title="Installer Windows 11 sur le poste réparé",
        question_type="document_analysis",
        requirement_ids=("AP-10", "AP-15"),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : le disque de {bad.post} vient d'être remplacé par un disque neuf et vide ; les "
            "données sont sauvegardées sur NAS-01. Tu installes Windows 11 Pro. Le poste figure au document 3, les "
            "réglages relevés dans le micrologiciel et la licence au document 8."
        ),
        documents=(d.inventory, d.firmware),
        instructions=(
            ("Compare les réglages du document 8 aux prérequis de Windows 11 : indique chaque réglage à modifier et "
            "ceux à garder, avec la raison."),
            ("Rédige la procédure d'installation, de la préparation du support au premier démarrage, partitionnement "
            "du disque compris."),
            (f"Dis si Windows s'activera et ce qu'il reste à faire pour que le {user} retrouve un poste prêt à "
            "travailler."),
            "Donne les vérifications finales.",
        ),
        criteria=(
            _c("Micrologiciel", 3, f"À modifier : {change_text}. Raisons : {why_text}. À garder : {keep_text}. "
               "Une réponse qui désactive une sécurité ou garde le mode Legacy perd ces points."),
            _c("Installation", 3, "Clé USB de 8 Go au moins créée avec l'outil de création de support de Microsoft "
               "(sur un autre PC) ; démarrage sur l'entrée UEFI de la clé (menu de démarrage) ; langue et clavier "
               "belges ; édition Windows 11 Pro (celle de la licence) ; installation personnalisée sur le disque neuf "
               "(espace non alloué) : l'installateur crée en GPT la partition système EFI, la MSR, C: et la partition "
               "de récupération ; premier démarrage : compte, nom du poste, confidentialité."),
            _c("Activation et finitions", 2, f"{activates} : licence {lic_kind} Pro du même PC et même édition "
               f"({reason}), activation automatique une fois connecté à Internet. Puis : pilotes (Windows Update, "
               f"site du fabricant), mises à jour, antivirus, logiciels métier, restauration des données depuis "
               f"NAS-01, lecteur réseau \\\\SRV-01\\{share}, imprimante IMP-01, réglages de sauvegarde."),
            _c("Vérifications", 2, "Gestionnaire de périphériques sans pilote manquant ; Paramètres → Activation : "
               "« Windows est activé » ; msinfo32 : mode BIOS UEFI, démarrage sécurisé activé ; tpm.msc : TPM 2.0 "
               "prêt ; fichiers restaurés ouverts, lecteur réseau et impression testés, avec l'utilisateur."),
        ),
        correction=(
            (f"Réglages à modifier : {change_text}. Raisons : {why_text}. Réglages déjà conformes, à garder : "
            f"{keep_text}."),
            ("Je prépare une clé USB d'au moins 8 Go avec l'outil de création de support de Microsoft, sur un autre "
            "PC. Je démarre le poste sur l'entrée UEFI de la clé (menu de démarrage), je choisis la langue et le "
            "clavier belges, l'édition Windows 11 Pro, puis l'installation personnalisée sur le disque neuf (espace "
            "non alloué) : l'installateur crée lui-même, en GPT, la partition système EFI, la MSR, la partition C: et "
            "la partition de récupération. Au premier démarrage : compte, nom du poste, options de confidentialité."),
            f"Activation : {activates.lower()}, car c'est le même PC et la même édition que la licence {lic_kind} Pro "
            "(" + reason + ") ; elle se fait automatiquement une fois le poste connecté à Internet. Ensuite : "
            "pilotes (Windows Update, puis site du fabricant), mises à jour, antivirus, logiciels métier, "
            f"restauration des données depuis NAS-01, lecteur réseau \\\\SRV-01\\{share}, imprimante IMP-01 et "
            "sauvegarde automatique.",
            ("Vérifications : aucun pilote manquant dans le Gestionnaire de périphériques ; « Windows est activé » ; "
            "msinfo32 indique le mode BIOS UEFI et le démarrage sécurisé activé ; tpm.msc montre un TPM 2.0 prêt ; "
            "l'utilisateur ouvre ses fichiers, accède au lecteur réseau et imprime une page de test."),
        ),
    )


def _s4(v: Variant, d: Docs) -> PR06Item:
    ok = v.iso_check_line.endswith(": OK")
    layout = "; ".join(f"{part} : {fs}, {mount}, {size}" for part, fs, mount, size in v.linux_layout)
    rule = (f"{v.linux_ram_gb} Go de mémoire, sans hibernation → swap égal à la mémoire ({fr(v.swap_gb)} Go)"
            if v.linux_ram_gb <= 8 else
            f"{v.linux_ram_gb} Go de mémoire, sans hibernation → 4 Go de swap suffisent")
    share = list(v.shares)[-1]
    iso_expected = (
        "« OK » : la somme SHA-256 de l'image correspond à celle publiée ; l'image est intègre, on peut écrire la clé "
        "(Startup Disk Creator, balenaEtcher, Rufus en mode image DD)."
        if ok else
        "« FAILED » : la somme ne correspond pas ; image corrompue ou modifiée → la supprimer, la retélécharger "
        "depuis le site officiel d'Ubuntu, refaire sha256sum -c jusqu'à « OK », seulement ensuite écrire la clé."
    )
    return PR06Item(
        key=item_key(v, 4),
        usage=USAGE_EXAM,
        title="Installer Linux sur un poste de travail",
        question_type="document_analysis",
        requirement_ids=("AP-10",),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : {v.linux_post} (document 3) doit être installé sous Ubuntu 24.04 LTS, seul "
            "système du disque, en mode UEFI, sans hibernation (document 4). Tu as téléchargé l'image et son fichier "
            f"SHA256SUMS ; le relevé de la vérification est au document 9. {v.linux_post} a {v.linux_ram_gb} Go de "
            f"mémoire et un disque de {v.linux_disk_gb} Go."
        ),
        documents=(d.inventory, d.journal, d.iso),
        instructions=(
            "Interprète le document 9 et dis ce que tu fais avant de créer la clé d'installation.",
            ("Propose le partitionnement du disque : partitions, systèmes de fichiers, points de montage et tailles, "
            "avec la règle utilisée pour le swap."),
            "Rédige les étapes de l'installation, du démarrage sur la clé au premier redémarrage.",
            (f"Indique les commandes et contrôles après l'installation : mises à jour, réseau, accès au partage "
            f"\\\\SRV-01\\{share}."),
        ),
        criteria=(
            _c("Image", 2, iso_expected),
            _c("Partitionnement", 3, f"Table GPT (UEFI). {layout}. Règle du swap : {rule} (un fichier d'échange "
               "au lieu d'une partition est accepté)."),
            _c("Étapes", 3, "Démarrer sur l'entrée UEFI de la clé ; « Installer Ubuntu » ; langue et clavier belges ; "
               "réseau ; installation normale ; partitionnement manuel (« Installation manuelle ») selon le plan, "
               "chargeur de démarrage sur le disque ; fuseau Europe/Brussels ; compte utilisateur avec mot de passe "
               "(administration par sudo) et nom du poste ; installation, retrait de la clé, redémarrage."),
            _c("Après installation", 2, "sudo apt update puis sudo apt upgrade (ou full-upgrade) ; ip addr et "
               f"ip route (adresse dans {v.network}, route par défaut via {v.box_ip}) ; ping -c 4 {v.srv_ip} ; "
               f"partage : Fichiers → Autres emplacements → smb://{v.srv_ip}/{share} (ou paquet cifs-utils et "
               "mount -t cifs) avec un compte du serveur ; ouverture d'un fichier."),
        ),
        correction=(
            ("La ligne se termine par « OK » : la somme SHA-256 calculée correspond à celle publiée, l'image est "
             "intègre. Je peux écrire la clé (Startup Disk Creator, balenaEtcher ou Rufus en mode image DD)."
             if ok else
             "La ligne se termine par « FAILED » : la somme calculée ne correspond pas à celle publiée. L'image est "
             "corrompue ou modifiée : je la supprime, je la retélécharge depuis le site officiel d'Ubuntu et je "
             "relance sha256sum -c ; je n'écris la clé qu'après un « OK »."),
            (f"Partitionnement en GPT : {layout}. Swap : {rule}. Un fichier d'échange à la place de la partition "
            "convient aussi."),
            ("Je démarre sur l'entrée UEFI de la clé, je choisis « Installer Ubuntu », la langue et le clavier belges, "
            "le réseau, puis l'installation manuelle des partitions selon le plan, avec le chargeur de démarrage sur "
            "le disque. Je règle le fuseau Europe/Brussels, je crée le compte utilisateur (administration par sudo) "
            "et le nom du poste, je lance l'installation, puis je retire la clé et je redémarre."),
            ("Après : sudo apt update puis sudo apt upgrade ; ip addr et ip route pour contrôler l'adresse reçue dans "
            f"{v.network} et la route par défaut via {v.box_ip} ; ping -c 4 {v.srv_ip} ; accès au partage par "
            f"Fichiers → Autres emplacements → smb://{v.srv_ip}/{share} (ou cifs-utils et mount -t cifs) avec un "
            "compte du serveur, puis ouverture d'un fichier."),
        ),
    )


def _s5(v: Variant, d: Docs) -> PR06Item:
    order = ", ".join(f"{i} {w}" for i, w in enumerate(T568B, start=1))
    faults = " et ".join(v.tester_faults)
    if v.number == 1:
        fault = (f"{faults} : les deux fils de la paire 1-2 (blanc-orange et orange) sont permutés à une extrémité "
                 "(paire inversée) ; le cordon n'est pas conforme et doit être refait, même si certaines cartes "
                 "tolèrent l'inversion.")
    else:
        fault = (f"{faults} : circuit ouvert, le fil n'arrive pas (pas en butée dans la fiche, coupé ou mal serti) ; "
                 "en 1 Gb/s, il faut les 4 paires : lien absent ou replié à 100 Mb/s.")
    total = v.run_total_m
    verdict = v.run_verdict
    if verdict == "Conforme":
        run = (f"Lien permanent {v.run_permanent_m} m ≤ 90 m ; canal {v.run_permanent_m} + {v.run_cords_m[0]} + "
               f"{v.run_cords_m[1]} = {total} m ≤ 100 m ; Cat6 ≥ Cat5e exigée pour 1000BASE-T → liaison conforme, "
               "à certifier au testeur.")
    else:
        run = (f"Lien permanent {v.run_permanent_m} m > 90 m ; canal {v.run_permanent_m} + {v.run_cords_m[0]} + "
               f"{v.run_cords_m[1]} = {total} m > 100 m : trop long pour la paire torsadée, même en Cat6 ; "
               "raccourcir les cordons ne suffit pas. Solution : un petit switch plus près du poste (relié au "
               "premier), ou une autre arrivée plus courte (autre baie) ; 1 Gb/s non garanti en l'état.")
    return PR06Item(
        key=item_key(v, 5),
        usage=USAGE_EXAM,
        title="Cordon RJ45 et liaison cuivre d'un nouveau poste",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-36"),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : une nouvelle prise murale dessert {v.run_post}. Le stagiaire a fabriqué le "
            "cordon du poste en T568B aux deux bouts ; le relevé du testeur est au document 10. Les longueurs de la "
            "liaison sont au document 11."
        ),
        documents=(d.journal, d.tester, d.run),
        instructions=(
            ("Donne l'ordre des 8 fils d'une fiche RJ45 en T568B, de la broche 1 à 8, et dis quelles paires servent "
            "en 1 Gb/s."),
            "Interprète le relevé du testeur : défaut, cause probable et conséquence.",
            "Rédige la procédure pour refaire et contrôler le cordon.",
            ("Vérifie la liaison du document 11 pour un débit de 1 Gb/s et conclus, avec une solution si elle ne "
            "convient pas."),
        ),
        criteria=(
            _c("Brochage", 2, f"T568B : {order}. En 1000BASE-T, les 4 paires transmettent dans les deux sens."),
            _c("Testeur", 3, fault),
            _c("Procédure", 2, "Couper la fiche fautive, dénuder la gaine sur 2 à 3 cm sans entailler les fils, "
               "détorsader au minimum, ranger les fils dans l'ordre T568B, couper droit à environ 12 mm, enfoncer "
               "jusqu'en butée (fils visibles au bout de la fiche, gaine sous le serre-câble), sertir ; tester : "
               "1→1 à 8→8, aucun ouvert, court-circuit ni inversion ; essai du lien sur le poste."),
            _c("Liaison", 3, run),
        ),
        correction=(
            (f"T568B, broche 1 à 8 : {order}. En 1000BASE-T (1 Gb/s), les quatre paires transmettent, dans les deux "
            "sens à la fois."),
            fault[0].upper() + fault[1:],
            ("Je coupe la fiche fautive, je dénude la gaine sur 2 à 3 cm sans entailler les fils, je détorsade le "
            "moins possible, je range les fils dans l'ordre T568B, je les coupe droit à environ 12 mm et je les "
            "enfonce jusqu'en butée, gaine sous le serre-câble, puis je sertis. Je teste : 1→1 à 8→8, sans ouvert, "
            "court-circuit ni inversion, puis j'essaie le lien sur le poste."),
            run,
        ),
    )


def _s6(v: Variant, d: Docs) -> PR06Item:
    bus = v.coax_bus
    reading = v.coax_reading
    errors = " ; ".join(v.coax_errors)
    first = bus.stations[0].name
    if v.number == 1:
        diag = (f"Mesure {fr(reading)} Ω au lieu de 25 Ω : un seul terminateur est vu. Constat : {errors} Le "
                "signal se réfléchit sur l'extrémité ouverte : collisions et erreurs, tout le segment est coupé. "
                f"Correction : visser un terminateur 50 Ω sur la sortie libre du T de {bus.stations[-1].name}, sans "
                "seconde mise à la terre (une seule, déjà côté " + first + ").")
    else:
        diag = (f"Mesure {fr(reading)} Ω = 50 Ω en parallèle avec 75 Ω (50 × 75 / 125), au lieu de 25 Ω. Constats : "
                f"{errors} Rupture d'impédance : réflexions, erreurs, segment inutilisable. Correction : terminateur "
                "50 Ω et tronçon refait en RG-58 50 Ω ; le RG-59 (75 Ω, vidéo, antenne) ne convient pas.")
    replace_len = next(s.length_m for s in bus.spans if s.cable != "RG-58") if v.number == 2 else bus.spans[-1].length_m
    return PR06Item(
        key=item_key(v, 6),
        usage=USAGE_EXAM,
        title="Segment coaxial : diagnostic et fabrication d'un câble BNC",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-36"),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : dans le {v.coax_room}, les machines anciennes reliées en 10BASE2 ne "
            "communiquent plus (document 4). Tes constats et ta mesure sont au document 12, avec la demande du "
            "client."
        ),
        documents=(d.client, d.journal, d.coax),
        instructions=(
            "Indique la valeur que l'ohmmètre doit afficher sur un segment conforme, et pourquoi.",
            "Interprète la mesure et les constats du document 12 : chaque non-conformité, son effet et sa correction.",
            f"Décris la fabrication du câble de {fr(replace_len)} m demandé : matériel, étapes et contrôles.",
            "Donne les vérifications finales du segment.",
        ),
        criteria=(
            _c("Valeur attendue", 2, "25 Ω : deux terminateurs 50 Ω, un à chaque extrémité du bus, vus en "
               "parallèle (50 × 50 / 100) ; câble et cartes n'interviennent pas en continu."),
            _c("Diagnostic", 3, diag),
            _c("Fabrication", 3, "Câble RG-58 (50 Ω), deux connecteurs BNC mâles à sertir prévus pour le RG-58, "
               "dénudeuse coaxiale, pince à sertir à la bonne matrice. Couper net ; enfiler manchon et bague à "
               "sertir ; dénuder aux cotes de la notice (gaine, tresse, diélectrique) sans couper la tresse ni "
               "entailler l'âme ; sertir (ou souder) la broche centrale sur l'âme ; enfoncer le corps sous la tresse, "
               "broche en butée ; ramener la bague sur la tresse et sertir ; manchon. Contrôles : âme-blindage = "
               "infini (pas de court-circuit), continuité de l'âme et du blindage d'un bout à l'autre, traction."),
            _c("Vérifications", 2, f"T directement sur chaque carte ; 0,5 m au moins entre deux T ; segment ≤ 185 m "
               f"(ici {fr(bus.length_m)} m) ; une seule mise à la terre ; ohmmètre au T de {first} : 25 Ω ; puis "
               "échange réel entre les machines (ping, accès aux fichiers)."),
        ),
        correction=(
            ("Sur un segment conforme, l'ohmmètre placé entre l'âme et le blindage voit les deux terminateurs de 50 Ω "
            "en parallèle : 50 × 50 / (50 + 50) = 25 Ω. Les cartes et le câble n'interviennent pas en continu."),
            diag,
            ("Fabrication : câble RG-58 (50 Ω), deux connecteurs BNC mâles à sertir pour RG-58, dénudeuse coaxiale, "
            "pince à sertir avec la bonne matrice. Je coupe net, j'enfile le manchon et la bague, je dénude aux cotes "
            "de la notice sans couper la tresse ni entailler l'âme, je sertis la broche centrale sur l'âme, j'enfonce "
            "le corps sous la tresse jusqu'à ce que la broche soit en butée, je ramène la bague sur la tresse et je "
            "la sertis, puis je pose le manchon. Contrôles : aucun contact entre âme et blindage, continuité de l'âme "
            "et du blindage d'un bout à l'autre, essai de traction."),
            (f"Vérifications : T directement sur chaque carte, 0,5 m au moins entre deux T, segment de "
            f"{fr(bus.length_m)} m (185 m au plus), une seule mise à la terre, 25 Ω mesurés au T de {first}, puis "
            "échange réel entre les machines."),
        ),
    )


def _s7(v: Variant, d: Docs) -> PR06Item:
    f = v.facts
    usable = f"{f.usable:,}".replace(",", " ")
    errors = " ".join(v.plan_errors)
    if v.number == 1:
        consequences = ("IMP-01 en adresse fixe dans l'étendue DHCP : la box peut attribuer la même adresse à un "
                        "poste → conflit, impression ou poste coupés. PC-06 en /16 : il croit local tout "
                        "192.168.x.x et utilise la diffusion 192.168.255.255 ; il fonctionne ici par hasard mais "
                        "rate les diffusions du réseau et ne joindrait pas un autre réseau 192.168.")
        fixes = ("IMP-01 : 192.168.1.20/24 (plage des imprimantes, hors étendue), passerelle et DNS 192.168.1.1, "
                 "ports d'impression des postes mis à jour (ou réservation DHCP) ; PC-06 : masque 255.255.255.0 "
                 "(/24), le reste inchangé (ou DHCP).")
        mac_case = ("Toutes les lignes correspondent aux MAC du schéma (ex. 192.168.1.120 → 00-80-77-31-01-20 = "
                    "IMP-01).")
    else:
        consequences = ("PC-04 en /24 : son réseau devient 172.16.41.0/24 ; la passerelle 172.16.40.1 est hors de "
                        "ce réseau → pas d'Internet et pas d'accès à SRV-01, NAS-01, IMP-01 (172.16.40.x). PC-06 "
                        "a l'adresse de NAS-01 (172.16.40.10) : conflit d'adresse, sauvegardes et accès au NAS "
                        "aléatoires.")
        fixes = ("PC-04 : masque 255.255.254.0 (/23), adresse 172.16.41.30 et passerelle 172.16.40.1 inchangées ; "
                 "PC-06 : une adresse libre de la plage des postes fixes, ex. 172.16.41.11/23 (ou DHCP), passerelle "
                 "et DNS 172.16.40.1 ; NAS-01 garde 172.16.40.10.")
        mac_case = ("La ligne 172.16.40.10 porte 3c-52-82-22-01-06, la MAC de PC-06 et non celle de NAS-01 "
                    "(00-11-32-CD-00-10) : preuve du conflit d'adresse.")
    return PR06Item(
        key=item_key(v, 7),
        usage=USAGE_EXAM,
        title="Plan d'adressage IPv4 : calculer, corriger, identifier MAC et IP",
        question_type="document_analysis",
        requirement_ids=("AP-30",),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : avant toute intervention, tu contrôles le plan d'adressage. Le réseau et les "
            "conventions sont au document 1, les configurations relevées au document 2 (schéma), la table ARP de "
            "SRV-01 au document 13."
        ),
        documents=(d.client, d.schema, d.arp),
        instructions=(
            ("Pour le réseau du document 1, calcule le masque, l'adresse du réseau, l'adresse de diffusion, la plage "
            "des adresses d'hôtes et le nombre d'hôtes ; montre la méthode."),
            "Relève dans le document 2 chaque configuration erronée et explique sa conséquence.",
            "Donne la configuration corrigée de chaque appareil concerné, selon les conventions du document 1.",
            ("À partir du document 13, distingue une adresse IPv4 d'une adresse MAC, dis à quoi sert chacune et ce "
            "que tu remarques en comparant au document 2."),
        ),
        criteria=(
            _c("Calculs", 3, f"/{f.prefix} = masque {f.mask} ; réseau {f.network} ; diffusion {f.broadcast} ; "
               f"hôtes {f.first_host} à {f.last_host} ; 2^{32 - f.prefix} − 2 = {usable} hôtes ; méthode binaire ou "
               "taille de bloc acceptée."),
            _c("Erreurs", 3, f"{errors} Conséquences : {consequences}"),
            _c("Corrections", 2, fixes),
            _c("MAC et IP", 2, "IPv4 : 32 bits, 4 nombres décimaux de 0 à 255, logique, attribuée par configuration "
               "ou DHCP, sert à joindre un appareil d'un réseau à l'autre (routage). MAC : 48 bits, 6 octets "
               "hexadécimaux, gravée dans la carte (fabricant), sert à livrer la trame sur le réseau local ; ARP "
               f"fait la correspondance IP → MAC. {mac_case}"),
        ),
        correction=(
            (f"Réseau {v.network} : préfixe /{f.prefix}, masque {f.mask}. Adresse du réseau {f.network} (tous les bits "
            f"d'hôte à 0), diffusion {f.broadcast} (tous à 1), hôtes de {f.first_host} à {f.last_host}, soit "
            f"2^{32 - f.prefix} − 2 = {usable} hôtes."),
            f"Erreurs relevées : {errors} Conséquences : {consequences}",
            f"Corrections : {fixes}",
            ("Une adresse IPv4 (32 bits, quatre nombres de 0 à 255) est logique : elle est configurée ou donnée par "
            "DHCP et permet d'atteindre un appareil, même à travers un routeur. Une adresse MAC (48 bits, six octets "
            "hexadécimaux) identifie la carte réseau et sert à livrer la trame sur le réseau local ; ARP fait la "
            f"correspondance entre les deux. {mac_case}"),
        ),
    )


def _s8(v: Variant, d: Docs) -> PR06Item:
    person, folder, wanted = v.need
    layer = v.need_limiting_layer
    matrix = _levels(v.access_matrix)
    group = next(g for p, _f, g in v.accounts if p == person)[0] if layer == "NTFS" else ""
    if layer == "partage":
        fix = (f"Le partage {folder} (« Tout le monde : Lecture ») limite {person} alors que NTFS lui donne "
               f"Modification : passer le partage à « Utilisateurs authentifiés » (ou Tout le monde) : Modifier et "
               "laisser NTFS décider ; ne pas donner un droit à une personne seule ni ouvrir NTFS à tous.")
    else:
        fix = (f"Le partage donne Modifier à tous, mais NTFS ne donne que Lecture à {group} sur {folder} : passer "
               f"{group} en Modification dans l'onglet Sécurité de {folder} (le groupe, pas le compte de {person}) ; "
               "ne pas toucher aux autres groupes.")
    fixed = {p: dict(row) for p, row in v.access_matrix.items()}
    fixed[person][folder] = wanted
    return PR06Item(
        key=item_key(v, 8),
        usage=USAGE_EXAM,
        title="Partages du serveur : accès effectifs, correction, lecteur réseau et imprimante",
        question_type="document_analysis",
        requirement_ids=("AP-25",),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : les dossiers de SRV-01 sont partagés pour trois personnes. Comptes et groupes "
            "au document 14 ; partages, autorisations NTFS et besoin exprimé au document 15. Les postes ouvrent une "
            "session avec un compte du même nom et du même mot de passe que sur le serveur."
        ),
        documents=(d.accounts, d.shares),
        instructions=(
            "Calcule l'accès effectif par le réseau de chaque personne sur chaque dossier, en montrant la règle.",
            f"Le besoin de {person} n'est pas satisfait : indique la couche qui bloque et la correction minimale.",
            (f"Rédige la procédure pour connecter {folder} en lecteur réseau sur le poste de {person}, puis pour "
            "installer l'imprimante réseau IMP-01 sur un poste."),
            "Indique comment tu vérifies le résultat.",
        ),
        criteria=(
            _c("Accès effectifs", 4, "Dans chaque couche, les droits des groupes d'une personne se cumulent (le plus "
               "fort) ; par le réseau, l'accès effectif est le plus restrictif du partage et de NTFS. Résultat : "
               f"{matrix}. Environ 0,5 point par case, la règle compte pour le reste."),
            _c("Couche et correction", 3, fix),
            _c("Procédures", 2, f"Explorateur → Ce PC → Connecter un lecteur réseau : lettre, \\\\SRV-01\\{folder}, "
               "« Se reconnecter à la connexion », identifiants du compte serveur si demandés (ou net use T: "
               f"\\\\SRV-01\\{folder} /persistent:yes). Imprimante : Paramètres → Imprimantes et scanners → Ajouter "
               "→ par adresse TCP/IP → adresse fixe de IMP-01 → pilote du fabricant → page de test."),
            _c("Vérification", 1, f"Session de {person} : créer, modifier, enregistrer un fichier dans {folder} ; un "
               "compte sans droit reste refusé ; page de test imprimée."),
        ),
        correction=(
            ("Règle : dans le partage comme dans NTFS, les autorisations des groupes d'une personne se cumulent ; par "
            f"le réseau, l'accès effectif est le plus restrictif des deux couches. Résultat : {matrix}."),
            f"{fix} Après correction : {_levels(fixed)}.",
            (f"Lecteur réseau : Explorateur → Ce PC → Connecter un lecteur réseau, une lettre, le chemin "
            f"\\\\SRV-01\\{folder}, case « Se reconnecter à la connexion », identifiants du compte serveur si "
            f"demandés (ou « net use T: \\\\SRV-01\\{folder} /persistent:yes »). Imprimante : Paramètres → Imprimantes "
            "et scanners → Ajouter un périphérique → ajout manuel par adresse TCP/IP (adresse fixe de IMP-01), "
            "pilote du fabricant, page de test."),
            (f"Vérification : avec la session de {person}, créer et modifier un fichier dans {folder} ; un compte "
            "sans droit reste refusé ; la page de test sort."),
        ),
    )


def _s9(v: Variant, d: Docs) -> PR06Item:
    lap = v.laptop
    if v.laptop_fault == "dns":
        reading = (f"Relevé 1 : adresse fixe {lap.ip}/{lap.prefix}, passerelle {lap.gateway} (la box) mais DNS "
                   f"{v.old_dns}, qui n'est pas un serveur du bureau (le DNS est la box). Relevé 2 : la box répond → "
                   f"lien, adresse et réseau local OK. Relevé 3 : {WEB_IP} répond → la sortie vers Internet par la "
                   f"passerelle fonctionne. Relevé 4 : le nom {WEB_NAME} n'est pas trouvé. Relevé 5 : nslookup vers "
                   f"{v.old_dns} → délai dépassé : personne ne répond aux requêtes DNS.")
        cause = (f"Panne de résolution de noms (DNS) : le portable interroge {v.old_dns}, qui ne répond pas ; la "
                 "connectivité IP est intacte (ce n'est ni le câble, ni l'adresse, ni la passerelle).")
        fix = (f"Repasser la carte en DHCP (adresse, passerelle et DNS de la box, convient aussi à la maison), ou en "
               f"fixe : {lap.ip}/{lap.prefix}, passerelle et DNS {v.box_ip}.")
        tests = (f"ipconfig /all (DNS {v.box_ip}), ipconfig /flushdns, nslookup {WEB_NAME} répond par {v.box_ip}, "
                 f"ping {WEB_NAME} répond, navigation ; noter la correction.")
    else:
        reading = (f"Relevé 1 : adresse fixe {lap.ip}/{lap.prefix} (bon réseau), DNS {v.box_ip}, mais passerelle "
                   "par défaut vide. Relevés 2 et 3 : la box et SRV-01 répondent → lien, adresse et réseau local "
                   f"OK. Relevé 4 : « Défaillance générale » vers {WEB_IP} : la demande ne part même pas, le poste "
                   "n'a aucune route vers un autre réseau.")
        cause = ("Passerelle par défaut absente : le portable ne sait pas où envoyer ce qui sort du réseau local ; "
                 "le réseau local fonctionne, Internet est injoignable (ce n'est pas le DNS ni le câble).")
        fix = (f"Repasser la carte en DHCP, ou garder l'adresse fixe {lap.ip}/{lap.prefix} (hors étendue) avec "
               f"passerelle {v.box_ip} et DNS {v.box_ip}.")
        tests = (f"ipconfig /all (passerelle {v.box_ip}), route print (route 0.0.0.0 via {v.box_ip}), ping {WEB_IP} "
                 f"répond, ping {WEB_NAME} et navigation, tracert -d {WEB_IP} passe par la box ; noter la correction.")
    return PR06Item(
        key=item_key(v, 9),
        usage=USAGE_EXAM,
        title="Portable sans Internet : diagnostic à partir des relevés",
        question_type="document_analysis",
        requirement_ids=("AP-37", "AP-30"),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : {lap.name} revient de chez un autre réparateur qui l'a configuré à la main "
            f"(document 4). Au bureau, il n'a plus Internet. Tu fais les relevés du document 16 ; le réseau et ses "
            "conventions sont au document 1."
        ),
        documents=(d.client, d.journal, d.laptop),
        instructions=(
            "Interprète chaque relevé du document 16, dans l'ordre : ce qu'il prouve ou exclut.",
            "Donne la cause de la panne.",
            "Indique la correction durable et la configuration complète du portable dans ce réseau.",
            "Donne les tests qui prouvent que c'est réglé.",
        ),
        criteria=(
            _c("Lecture des relevés", 4, reading),
            _c("Cause", 2, cause),
            _c("Correction", 2, fix),
            _c("Tests", 2, tests),
        ),
        correction=(reading, cause, f"Correction : {fix}", f"Tests : {tests}"),
    )


def _s10(v: Variant, d: Docs) -> PR06Item:
    bad = v.failing
    total = v.journal_minutes
    first, last = v.journal[0][0], v.journal[-1][1]
    explain = {
        "SMART": "le disque surveille lui-même son état et note ses erreurs ; ces compteurs annonçaient sa panne",
        "SSD": "un disque sans pièce mobile, à mémoire électronique, bien plus rapide et plus résistant aux chocs",
        "sauvegarde": "une copie des données sur un autre support (ici le NAS), pour les récupérer si le PC tombe "
                      "en panne",
        "TPM": "une puce de sécurité du PC qui garde des clés secrètes ; Windows 11 l'exige pour protéger le "
               "démarrage et les données",
        "micrologiciel (UEFI)": "le petit programme de la carte mère qui démarre le PC avant Windows et garde ses "
                                "réglages",
    }
    terms = " ; ".join(f"{t} : {explain[t]}" for t in v.explain_terms)
    terms_list = ", ".join(v.explain_terms)
    watch = next((r for r in v.smart if r.verdict == SMART_WATCH), None)
    recos = ("mettre en place une sauvegarde automatique quotidienne des postes vers NAS-01 avec une copie hors du "
             "bureau, et tester une restauration ; ")
    recos += (f"surveiller le disque de {watch.post} ({watch.reallocated} secteurs réalloués) et prévoir son "
              "remplacement" if watch else
              f"remplacer le disque mécanique de {v.slow_post} par un SSD et ajouter la mémoire proposée")
    return PR06Item(
        key=item_key(v, 10),
        usage=USAGE_EXAM,
        title="Rapport d'intervention et explication au client",
        question_type="document_analysis",
        requirement_ids=("AP-C01", "AP-16"),
        kind=KIND_DOC,
        context=(
            f"{v.label}. {v.company} : tu as remplacé le disque de {bad.post} et réinstallé le poste. {v.manager} "
            "veut un rapport écrit compréhensible. Les relevés SMART sont au document 7 et ton journal de la journée "
            "au document 17."
        ),
        documents=(d.smart, d.intervention),
        instructions=(
            f"Rédige le rapport d'intervention destiné à {v.manager}, avec les rubriques d'un rapport professionnel.",
            "Calcule la durée totale de l'intervention à partir du document 17 et indique-la dans le rapport.",
            f"Explique en mots simples les termes {terms_list} utilisés dans ton rapport.",
            "Termine par deux recommandations justifiées.",
        ),
        criteria=(
            _c("Structure et contenu", 4, f"Client ({v.company}), date ({v.date}), technicien, poste ({bad.post}), "
               f"demande (gels, avertissement de disque) ; constats chiffrés ({bad.pending} secteurs en attente, "
               f"{bad.uncorrectable} illisibles) ; diagnostic (disque en fin de vie) ; actions dans l'ordre "
               "(sauvegarde contrôlée, remplacement, micrologiciel, installation, pilotes, activation, restauration, "
               "tests) ; pièce posée ; état final vérifié avec l'utilisateur ; ancien disque rendu ou effacé avec "
               "accord ; phrases claires, sans jargon inutile."),
            _c("Durée", 2, f"Somme des lignes du journal : de {first} à {last} sans interruption = {total} minutes, "
               f"soit {duration_text(total)}."),
            _c("Vocabulaire", 2, terms),
            _c("Recommandations", 2, recos + " ; chaque recommandation est justifiée par un constat."),
        ),
        correction=(
            (f"Rapport : client {v.company}, intervention du {v.date} sur {bad.post}. Demande : gels et avertissement "
            f"de disque. Constats : {bad.pending} secteurs en attente et {bad.uncorrectable} secteurs illisibles au "
            "relevé SMART. Diagnostic : disque en fin de vie. Actions : sauvegarde des données vers NAS-01 et "
            "contrôle de la copie, remplacement du disque, réglage du micrologiciel, installation de Windows 11 Pro, "
            "pilotes, mises à jour et activation, restauration des données, lecteurs réseau et imprimante, tests avec "
            "l'utilisateur. État final : poste fonctionnel, vérifié avec lui. L'ancien disque est rendu ou effacé avec "
            "l'accord du client."),
            (f"Durée : les lignes du journal se suivent de {first} à {last}, soit {total} minutes = "
            f"{duration_text(total)}."),
            f"En mots simples : {terms}.",
            f"Recommandations : {recos}.",
        ),
    )


_BUILDERS = (_s1, _s2, _s3, _s4, _s5, _s6, _s7, _s8, _s9, _s10)


def build_items(v: Variant) -> tuple[PR06Item, ...]:
    docs = Docs(v)
    return tuple(builder(v, docs) for builder in _BUILDERS)


VARIANT_ITEMS: dict[int, tuple[PR06Item, ...]] = {v.number: build_items(v) for v in VARIANTS}
VARIANT_DOCS: dict[int, Docs] = {v.number: Docs(v) for v in VARIANTS}
# Clés des questions de chaque variante, dans l'ordre des situations (sélection des sessions).
VARIANT_KEYS: tuple[tuple[str, ...], ...] = tuple(
    tuple(item.key for item in VARIANT_ITEMS[v.number]) for v in VARIANTS
)
EXAM_ITEMS: tuple[PR06Item, ...] = tuple(item for v in VARIANTS for item in VARIANT_ITEMS[v.number])
ALL_ITEMS: tuple[PR06Item, ...] = EXAM_ITEMS
PRACTICE_ITEMS: tuple[PR06Item, ...] = ()


def situation_of(item: PR06Item) -> int:
    return int(item.key[-2:])


def validate_items() -> list[str]:
    errors = []
    for v in VARIANTS:
        items = VARIANT_ITEMS[v.number]
        if len(items) != SITUATIONS:
            errors.append(f"{v.label} : {len(items)} situations au lieu de {SITUATIONS}.")
        if sum(i.total_points for i in items) != EXAM_TOTAL_POINTS:
            errors.append(f"{v.label} : total différent de 100 points.")
        for item in items:
            errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
            if item.total_points != POINTS_PER_QUESTION:
                errors.append(f"{item.key} : {item.total_points:g} points au lieu de {POINTS_PER_QUESTION}.")
            if item.question_type != "document_analysis" or not item.documents:
                errors.append(f"{item.key} : réponse libre sur documents attendue.")
            if not item.context.startswith(f"{v.label}. "):
                errors.append(f"{item.key} : la variante doit ouvrir le contexte.")
    return errors
