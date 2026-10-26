"""PR04 « Reconditionnement, entretien et contrôles après intervention » — données de
référence, règles de décision et schémas SVG (ticket #205).

Tout est construit **depuis des données** de ce module (tuples), contrôlées par
`tests/test_ticket205_ampcr_pratique_pr04.py` :

- cinq procédures illustrées (`RECON_STEPS`, `CLEAN_STEPS`, `FIRMWARE_STEPS`, `ERASE_STEPS`,
  `AFTER_TESTS_STEPS`) : les mêmes tuples dessinent les schémas et alimentent les remises en
  ordre des exercices ;
- les quatre opérations à ne pas confondre (`OPERATIONS`) : réparation, reconditionnement,
  remise à zéro, effacement sécurisé ;
- la décision de protection des données (`data_decision`) : jamais d'effacement sans accord
  écrit du propriétaire, jamais sans sauvegarde vérifiée quand le client garde ses données ;
- l'effacement adapté au support (`ERASE_METHODS`, `erase_method_ok`) : principes de la
  publication NIST SP 800-88 (effacer / purger / détruire) ; un formatage rapide n'efface pas,
  des passes d'écrasement ne garantissent rien sur un SSD ;
- la lecture d'un relevé SMART (`smart_verdict`), l'usure d'une batterie de portable
  (`battery_wear_percent`, `battery_verdict`) et le gain de température après nettoyage
  (seuil de PR03, `temperature_verdict`) appliqués aux relevés **fictifs** des cas ;
- les points de nettoyage d'une tour (`CLEANING_POINTS`, vue annotée), les check-lists de
  réception et de remise, la filière des déchets (`WASTE_STREAMS`, `waste_stream`).

Aucun schéma ne vient d'une image générée ni d'une photographie : la « vue annotée » est un
schéma numéroté, dont chaque repère correspond à une ligne de données vérifiée.
"""

from dataclasses import dataclass
from html import escape

from app.v1.ampcr_pratique_pr03_figures import (  # noqa: F401 — seuil de PR03 réutilisé
    TEMP_ALERT_MARGIN,
    temperature_verdict,
)
from app.v1.ampcr_pratique_visuals import (
    Figure,
    _svg,
    _text_lines,
    _wrap,
    decision_tree_svg,
    line_chart_svg,
    screen_svg,
    step_flow_svg,
)

_STROKE = "#33415c"
SCREEN_WIDTH = 56  # caractères au plus par ligne de capture (lisible sur mobile, comme PR01-PR03)



# =============================================================================================
# 1. Les cinq procédures illustrées
# =============================================================================================

# Procédure 1 — reconditionner un PC (vue d'ensemble, de la réception à la remise).
RECON_STEPS: tuple[tuple[str, str], ...] = (
    ("Réceptionner", "Fiche de réception : propriétaire, numéro de série, état, accessoires, photos."),
    ("Autoriser", "Accord écrit du propriétaire sur le travail et sur le sort des données."),
    ("Diagnostiquer", "Avant toute intervention : démarrage, SMART, mémoire, batterie, ports, défauts."),
    ("Protéger les données", "Sauvegarde vérifiée ou effacement adapté, selon l'accord écrit."),
    ("Nettoyer", "Nettoyage non destructif, PC débranché : poussière, filtres, ventilateurs, pâte."),
    ("Remplacer", "Pièces usées ou défectueuses, compatibilité vérifiée ; numéros de série notés."),
    ("Mettre à jour", "Firmware si utile, système et pilotes, avec les précautions."),
    ("Tester", "Mémoire, SMART, températures, ports, stabilité : valeurs notées."),
    ("Remettre", "Check-list de remise, étiquette, rapport et traçabilité ; déchets triés."),
)

# Procédure 2 — nettoyage non destructif d'une tour.
CLEAN_STEPS: tuple[tuple[str, str], ...] = (
    ("Couper", "Arrêt, interrupteur du bloc sur 0, câble secteur débranché, bouton appuyé."),
    ("Sortir le PC", "Dans un local aéré ou dehors, pas sur le poste de montage ; bracelet relié."),
    ("Filtres", "Retirer et rincer ou brosser les filtres ; les laisser sécher complètement."),
    ("Bloquer les ventilateurs", "Tenir les pales avant de souffler : un ventilateur lancé peut s'abîmer."),
    ("Dépoussiérer", "Air sec par courtes impulsions, bombe tenue droite ; pinceau antistatique."),
    ("Contacts et pâte", "Alcool isopropylique et chiffon non pelucheux ; pâte neuve si ventirad retiré."),
    ("Contrôler", "Rien d'oublié dans le boîtier, filtres remis, puis tests et températures."),
)

# Procédure 3 — mise à jour du firmware (UEFI/BIOS) avec précautions.
FIRMWARE_STEPS: tuple[tuple[str, str], ...] = (
    ("Justifier", "Correctif, sécurité ou compatibilité utile : on ne met pas à jour « pour rien »."),
    ("Identifier", "Modèle et révision exacts de la carte (ou du portable), version installée."),
    ("Télécharger", "Fichier du site du fabricant pour ce modèle ; lire les notes de version."),
    ("Préparer", "Sauvegarde, réglages UEFI notés, BitLocker suspendu, secteur stable."),
    ("Flasher", "Outil prévu par le fabricant ; ne jamais couper ni redémarrer pendant l'écriture."),
    ("Vérifier", "Nouvelle version affichée, réglages remis (mode SATA, démarrage), BitLocker repris."),
)

# Procédure 4 — effacement sécurisé avant revente, don ou recyclage.
ERASE_STEPS: tuple[tuple[str, str], ...] = (
    ("Accord écrit", "Le propriétaire autorise l'effacement, par écrit, pour ce support précis."),
    ("Sauvegarde", "Données à garder copiées et relues, ou renonciation écrite du propriétaire."),
    ("Identifier", "Type de support (HDD, SSD SATA, SSD NVMe), numéro de série, chiffrement."),
    ("Effacer", "Technique adaptée au support (tableau) ; un formatage rapide n'efface rien."),
    ("Vérifier", "Contrôle du résultat : outil de vérification, aucune donnée lisible."),
    ("Tracer", "Certificat ou rapport : support, numéro de série, technique, date, technicien."),
)

# Procédure 5 — contrôles après intervention (avant la remise).
AFTER_TESTS_STEPS: tuple[tuple[str, str], ...] = (
    ("Contrôle visuel", "PC débranché : fixations, câbles, ventilateurs libres, aucune vis libre."),
    ("Démarrage", "POST sans erreur ; UEFI : matériel détecté, date et heure, températures."),
    ("Mémoire", "Test de la mémoire, plusieurs passes sans erreur."),
    ("Stockage", "État SMART lu et interprété ; espace libre suffisant."),
    ("Températures", "Au repos et en charge, comparées à la limite de la fiche."),
    ("Ports", "Chaque port USB, sorties vidéo, audio, réseau, Wi-Fi, clavier et pavé tactile."),
    ("Stabilité", "Au moins 30 minutes de charge sans arrêt ni erreur ; batterie si portable."),
)

PROCEDURES: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Reconditionner un PC, de la réception à la remise", RECON_STEPS),
    ("Nettoyer une tour sans rien abîmer", CLEAN_STEPS),
    ("Mettre à jour le firmware avec précaution", FIRMWARE_STEPS),
    ("Effacer un support de manière sécurisée", ERASE_STEPS),
    ("Contrôler après l'intervention", AFTER_TESTS_STEPS),
)


def _procedure_alt(intro: str, steps: tuple[tuple[str, str], ...]) -> str:
    return (
        f"{intro} {len(steps)} étapes reliées par des flèches : "
        + " ; ".join(f"{i} {label} : {detail}" for i, (label, detail) in enumerate(steps, start=1))
        + "."
    )


RECON_FIGURE = Figure(
    key="pr04-reconditionner",
    title="Procédure 1 — Reconditionner un PC, de la réception à la remise",
    alt=_procedure_alt("Procédure complète de reconditionnement d'un PC.", RECON_STEPS),
    caption=(
        "Le diagnostic précède toute intervention, la décision sur les données précède le "
        "nettoyage et les remplacements, et rien n'est remis sans tests ni rapport."
    ),
    svg=step_flow_svg(RECON_STEPS),
)

CLEAN_FIGURE = Figure(
    key="pr04-nettoyer",
    title="Procédure 2 — Nettoyer une tour sans rien abîmer",
    alt=_procedure_alt("Nettoyage non destructif de l'intérieur d'une tour.", CLEAN_STEPS),
    caption=(
        "Nettoyage non destructif : PC débranché, air sec par impulsions, ventilateurs bloqués, "
        "aucun liquide sur les circuits sauf l'alcool isopropylique sur les contacts et le "
        "processeur. Pas d'aspirateur ménager ni de compresseur d'atelier non filtré."
    ),
    svg=step_flow_svg(CLEAN_STEPS),
)

FIRMWARE_FIGURE = Figure(
    key="pr04-firmware",
    title="Procédure 3 — Mettre à jour le firmware avec précaution",
    alt=_procedure_alt("Mise à jour du firmware UEFI d'une carte mère ou d'un portable.", FIRMWARE_STEPS),
    caption=(
        "Une coupure pendant l'écriture du firmware peut rendre la carte inutilisable : "
        "secteur stable, portable sur son chargeur, aucune interruption. La notice du "
        "fabricant fait foi."
    ),
    svg=step_flow_svg(FIRMWARE_STEPS),
)

ERASE_FIGURE = Figure(
    key="pr04-effacement",
    title="Procédure 4 — Effacer un support de manière sécurisée",
    alt=_procedure_alt("Effacement sécurisé d'un disque avant revente, don ou recyclage.", ERASE_STEPS),
    caption=(
        "Pas d'accord écrit, pas d'effacement. La technique dépend du support : on ne traite "
        "pas un SSD comme un disque dur. Le certificat prouve ce qui a été fait."
    ),
    svg=step_flow_svg(ERASE_STEPS),
)

AFTER_TESTS_FIGURE = Figure(
    key="pr04-controles",
    title="Procédure 5 — Contrôler après l'intervention",
    alt=_procedure_alt("Contrôles effectués après une intervention, avant la remise.", AFTER_TESTS_STEPS),
    caption=(
        "Chaque contrôle donne une valeur notée dans le rapport (mémoire, état SMART, "
        "températures, ports) : « tout fonctionne » n'est pas un résultat de test."
    ),
    svg=step_flow_svg(AFTER_TESTS_STEPS),
)

# =============================================================================================
# 2. Quatre opérations à ne pas confondre
# =============================================================================================


@dataclass(frozen=True)
class Operation:
    name: str
    goal: str
    data: str  # sort des données du client
    owner: str  # pour qui
    proof: str  # trace attendue


OP_REPAIR = "Réparation"
OP_RECON = "Reconditionnement"
OP_RESET = "Remise à zéro"
OP_ERASE = "Effacement sécurisé"

OPERATIONS: tuple[Operation, ...] = (
    Operation(OP_REPAIR, "Corriger une panne précise.", "Conservées (sauvegarde avant intervention).",
              "Le même client.", "Fiche d'intervention : panne, pièce, tests."),
    Operation(OP_RECON, "Remettre un PC complet en état de servir à nouveau : diagnostic, nettoyage, "
              "pièces, mises à jour, tests.", "Effacées de façon sécurisée si le PC change de main.",
              "Un nouvel utilisateur (revente, don, réaffectation).", "Rapport de reconditionnement et étiquette."),
    Operation(OP_RESET, "Réinstaller ou réinitialiser le système (« Réinitialiser ce PC », retour "
              "usine).", "Supprimées du système, mais pas forcément illisibles sur le disque.",
              "Le même client ou un proche, quand le support ne quitte pas sa sphère.", "Fiche d'intervention."),
    Operation(OP_ERASE, "Rendre les données d'un support illisibles, avec une technique adaptée et "
              "vérifiée.", "Détruites définitivement, après accord écrit.",
              "Avant revente, don, retour de location ou recyclage.", "Certificat d'effacement par support."),
)
OPERATIONS_BY_NAME = {op.name: op for op in OPERATIONS}

# =============================================================================================
# 3. Protection des données : décision et technique d'effacement
# =============================================================================================

DEST_SAME_CLIENT = "rendu au même client"
DEST_NEW_USER = "revente, don ou réaffectation"
DEST_RECYCLING = "recyclage"
DESTINATIONS = (DEST_SAME_CLIENT, DEST_NEW_USER, DEST_RECYCLING)

DECISION_NO_CONSENT = "Ne rien effacer : obtenir d'abord l'accord écrit du propriétaire"
DECISION_BACKUP_FIRST = "Sauvegarder et vérifier la copie avant toute intervention sur le disque"
DECISION_KEEP = "Conserver les données (sauvegarde vérifiée), aucun effacement"
DECISION_ERASE = "Effacement sécurisé adapté au support, vérifié et certifié"
DECISION_ERASE_OR_DESTROY = "Effacement sécurisé ou destruction physique du support, avec trace"


def data_decision(*, owner_consent: bool, wants_data: bool, backup_verified: bool, destination: str) -> str:
    """Décision du technicien sur les données d'un PC confié.

    Même ordre que l'arbre `DATA_TREE` :
    - sans accord écrit du propriétaire sur le sort des données, on n'efface et on ne
      réinstalle rien (ni demande d'un tiers, ni initiative du technicien) ;
    - le propriétaire veut garder ses données mais aucune copie vérifiée n'existe : on
      sauvegarde d'abord ;
    - PC rendu au même client : on conserve ; PC qui change de main : effacement sécurisé ;
      recyclage : effacement ou destruction physique du support."""
    if destination not in DESTINATIONS:
        raise ValueError(f"Destination inconnue : {destination}")
    if not owner_consent:
        return DECISION_NO_CONSENT
    if wants_data and not backup_verified:
        return DECISION_BACKUP_FIRST
    if destination == DEST_SAME_CLIENT:
        return DECISION_KEEP
    if destination == DEST_NEW_USER:
        return DECISION_ERASE
    return DECISION_ERASE_OR_DESTROY


MEDIA_HDD = "Disque dur (HDD)"
MEDIA_SATA_SSD = "SSD SATA"
MEDIA_NVME_SSD = "SSD NVMe"
MEDIA = (MEDIA_HDD, MEDIA_SATA_SSD, MEDIA_NVME_SSD)

# (support, techniques adaptées, techniques insuffisantes, pourquoi). Principes de NIST
# SP 800-88 « Guidelines for Media Sanitization » : effacer (écraser), purger (commandes
# d'effacement du support, effacement cryptographique), détruire.
ERASE_METHODS: tuple[tuple[str, tuple[str, ...], tuple[str, ...], str], ...] = (
    (
        MEDIA_HDD,
        ("écrasement complet du disque (une passe suffit sur un disque récent)",
         "commande d'effacement sécurisé du disque (ATA Secure Erase) par un outil fiable",
         "destruction physique par une filière agréée (disque hors d'usage)"),
        ("formatage rapide", "suppression des fichiers et corbeille vidée", "suppression des partitions"),
        ("Le formatage rapide ne réécrit que la table du système de fichiers : les données restent "
         "lisibles par un logiciel de récupération."),
    ),
    (
        MEDIA_SATA_SSD,
        ("commande d'effacement sécurisé ou Sanitize du SSD (outil du fabricant ou firmware)",
         "effacement cryptographique si le SSD est chiffré (clé détruite)",
         "destruction physique par une filière agréée (SSD hors d'usage)"),
        ("formatage rapide", "passes d'écrasement multiples avec un logiciel de PC",
         "défragmentation", "suppression des fichiers et corbeille vidée"),
        ("Le contrôleur du SSD répartit l'usure et garde des cellules de réserve : un logiciel ne peut "
         "pas écrire partout, seule la commande du SSD atteint toutes les cellules."),
    ),
    (
        MEDIA_NVME_SSD,
        ("commande NVMe Format avec effacement sécurisé ou Sanitize (outil du fabricant ou firmware)",
         "effacement cryptographique si le SSD est chiffré (clé détruite)",
         "destruction physique par une filière agréée (SSD hors d'usage)"),
        ("formatage rapide", "passes d'écrasement multiples avec un logiciel de PC",
         "défragmentation", "suppression des fichiers et corbeille vidée"),
        "Même raison que pour le SSD SATA ; la commande passe par l'interface NVMe.",
    ),
)
ERASE_BY_MEDIA = {media: (ok, ko, why) for media, ok, ko, why in ERASE_METHODS}


def erase_method_ok(media: str, technique: str) -> bool:
    """True si `technique` figure parmi les techniques adaptées à `media`."""
    ok, ko, _why = ERASE_BY_MEDIA[media]
    if technique in ok:
        return True
    if technique in ko:
        return False
    raise ValueError(f"Technique non référencée pour {media} : {technique}")


DATA_TREE: tuple[tuple[str, str], ...] = (
    ("Le propriétaire a-t-il donné son accord écrit sur le sort des données ?",
     "Ne rien effacer, ne rien réinstaller : demander l'accord écrit au propriétaire (pas à un tiers)."),
    ("Les données à garder sont-elles copiées et la copie relue ?",
     "Sauvegarder et vérifier la copie, ou faire signer une renonciation écrite."),
    ("Le PC ou le disque reste-t-il chez le même client ?",
     "Il change de main : effacement sécurisé adapté au support, vérifié, certificat."),
)
DATA_TREE_FINAL = "Même client : conserver les données ; une réinstallation se fait avec restauration de la sauvegarde."

DATA_TREE_FIGURE = Figure(
    key="pr04-decision-donnees",
    title="Décider du sort des données d'un PC confié",
    alt=(
        "Arbre de décision en trois questions. "
        + " ".join(f"Question {i} : {q} Si non : {n}" for i, (q, n) in enumerate(DATA_TREE, start=1))
        + f" Si toutes les réponses sont oui : {DATA_TREE_FINAL}"
    ),
    caption=(
        "La décision vient du propriétaire, par écrit ; le technicien choisit ensuite la "
        "technique adaptée au support et en garde la trace."
    ),
    svg=decision_tree_svg(DATA_TREE, DATA_TREE_FINAL),
)

# =============================================================================================
# 4. Vue annotée : points de nettoyage d'une tour
# =============================================================================================


@dataclass(frozen=True)
class CleaningPoint:
    number: int
    zone: str
    action: str
    x: int  # position du repère sur le schéma
    y: int


CLEANING_POINTS: tuple[CleaningPoint, ...] = (
    CleaningPoint(1, "Filtre de façade", "Démonter, brosser ou rincer, sécher avant de remettre.", 34, 190),
    CleaningPoint(2, "Ventilateurs de façade", "Bloquer les pales, souffler par impulsions.", 76, 255),
    CleaningPoint(3, "Radiateur du ventirad", "Air sec entre les ailettes, pales bloquées.", 260, 105),
    CleaningPoint(4, "Carte graphique", "Souffler ailettes et ventilateurs, sans démonter le refroidissement.", 106, 203),
    CleaningPoint(5, "Grille du bloc d'alimentation", "Souffler de l'extérieur ; ne jamais ouvrir le bloc.", 155, 292),
    CleaningPoint(6, "Ventilateur arrière", "Bloquer les pales, souffler, vérifier qu'il tourne librement.", 297, 116),
    CleaningPoint(7, "Filtre inférieur", "Sous le bloc : glisser, brosser, remettre.", 235, 326),
)

_TOWER_PARTS: tuple[tuple[str, int, int, int, int], ...] = (
    ("Ventirad", 165, 70, 80, 70),
    ("Carte graphique", 120, 185, 180, 36),
    ("Bloc d'alimentation", 170, 270, 130, 44),
    ("Façade", 14, 40, 40, 280),
    ("Ventilateur arrière", 262, 46, 72, 52),
)


def cleaning_svg(points: tuple[CleaningPoint, ...]) -> str:
    """Tour vue de côté, panneau retiré (schéma, pas une photographie) : chaque repère numéroté
    renvoie à une ligne de la légende placée sous le dessin."""
    width = 380
    parts = [
        (f'<text x="{width // 2}" y="16" text-anchor="middle" font-size="13.5" font-weight="700">'
         "Tour vue de côté, panneau retiré (schéma)</text>"),
        f'<rect x="8" y="28" width="{width - 40}" height="310" rx="8" fill="#f7f7f7" stroke="{_STROKE}" stroke-width="1.8"/>',
    ]
    for label, x, y, w, h in _TOWER_PARTS:
        parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#ffffff" stroke="{_STROKE}" stroke-width="1.2"/>'
        )
        lines = _wrap(label, max(6, w // 7))
        for i, line in enumerate(lines):
            parts.append(
                f'<text x="{x + w / 2:.0f}" y="{y + 14 + 12 * i}" font-size="10" text-anchor="middle">{escape(line)}</text>'
            )
    for point in points:
        parts.append(
            f'<g data-point="{point.number}" data-zone="{escape(point.zone)}">'
            f'<circle cx="{point.x}" cy="{point.y}" r="11" fill="#fff4e5" stroke="#b35c00" stroke-width="2"/>'
            f'<text x="{point.x}" y="{point.y + 4}" font-size="12" font-weight="700" text-anchor="middle">{point.number}</text></g>'
        )
    y = 360
    for point in points:
        lines = _wrap(f"{point.number}. {point.zone} : {point.action}", 58)
        parts.append(_text_lines(10, y, lines, size=11, step=14))
        y += 14 * len(lines) + 3
    return _svg(width, y + 4, parts)


CLEANING_FIGURE = Figure(
    key="pr04-points-nettoyage",
    title="Vue annotée — où s'accumule la poussière dans une tour",
    alt=(
        "Schéma d'une tour vue de côté, panneau retiré, avec sept repères numérotés : "
        + " ; ".join(f"{p.number} {p.zone} : {p.action}" for p in CLEANING_POINTS)
        + "."
    ),
    caption=(
        "Schéma annoté (pas une photographie) : les repères suivent le trajet de l'air, de "
        "l'entrée (filtres, façade) aux sorties (arrière, bloc). Une poussière épaisse sur "
        "ces points suffit à faire monter les températures."
    ),
    svg=cleaning_svg(CLEANING_POINTS),
)

# =============================================================================================
# 5. Relevés fictifs : SMART, batterie, températures
# =============================================================================================

SMART_OK = "bon"
SMART_WATCH = "à surveiller"
SMART_REPLACE = "à remplacer"


def smart_verdict(attributes: dict[str, int]) -> str:
    """Verdict d'un relevé SMART (valeurs brutes) selon la règle du cours :

    - disque dur : secteurs en attente (`Current_Pending_Sector`) ou illisibles
      (`Offline_Uncorrectable`) > 0 → à remplacer ; secteurs réalloués > 0 → à surveiller ;
    - SSD NVMe : réserve disponible sous son seuil, `Media_Errors` > 0 ou usure
      (`Percentage_Used`) ≥ 100 % → à remplacer ; usure ≥ 80 % → à surveiller.
    Le résumé « PASSED / OK » du disque ne suffit jamais : on lit les attributs."""
    if attributes.get("Current_Pending_Sector", 0) > 0 or attributes.get("Offline_Uncorrectable", 0) > 0:
        return SMART_REPLACE
    if "Available_Spare" in attributes and attributes["Available_Spare"] < attributes.get("Available_Spare_Threshold", 10):
        return SMART_REPLACE
    if attributes.get("Media_Errors", 0) > 0 or attributes.get("Percentage_Used", 0) >= 100:
        return SMART_REPLACE
    if attributes.get("Reallocated_Sector_Ct", 0) > 0 or attributes.get("Percentage_Used", 0) >= 80:
        return SMART_WATCH
    return SMART_OK


def smart_lines(title: str, summary: str, attributes: tuple[tuple[str, int], ...]) -> tuple[str, ...]:
    lines = [title, f"Résultat global : {summary}", "Attribut                      Valeur brute"]
    lines += [f"{name:<30}{value}" for name, value in attributes]
    return tuple(lines)


# Cas 2 (PC de bureau à reconditionner) : disque dur d'origine.
CASE2_SMART: tuple[tuple[str, int], ...] = (
    ("Power_On_Hours", 38412),
    ("Reallocated_Sector_Ct", 24),
    ("Current_Pending_Sector", 8),
    ("Offline_Uncorrectable", 8),
    ("Temperature_Celsius", 39),
)
CASE2_SCREEN = smart_lines("Relevé SMART — disque dur 1 To (fictif)", "PASSED", CASE2_SMART)

SMART_FIGURE = Figure(
    key="pr04-releve-smart",
    title="Relevé SMART d'un disque dur à reconditionner (fictif)",
    alt="Écran texte d'un utilitaire SMART. " + " ; ".join(CASE2_SCREEN) + ".",
    caption=(
        "Le résumé affiche « PASSED », mais 8 secteurs sont en attente et 8 illisibles : le "
        "disque perd des données. Verdict du cours : à remplacer, même si le résumé est bon. "
        "Capture fictive."
    ),
    svg=screen_svg(CASE2_SCREEN, label="Capture fictive — pas un écran officiel"),
)

BATTERY_REPLACE_BELOW = 80  # % de la capacité d'origine : convention du cours (usage courant)


def battery_health_percent(design_mwh: int, full_charge_mwh: int) -> int:
    """Capacité restante en % de la capacité d'origine (arrondie à l'unité)."""
    if design_mwh <= 0:
        raise ValueError("Capacité d'origine invalide.")
    return round(100 * full_charge_mwh / design_mwh)


def battery_wear_percent(design_mwh: int, full_charge_mwh: int) -> int:
    return 100 - battery_health_percent(design_mwh, full_charge_mwh)


def battery_verdict(design_mwh: int, full_charge_mwh: int) -> str:
    """« bonne » ou « à remplacer » (capacité restante sous 80 % de l'origine)."""
    return "à remplacer" if battery_health_percent(design_mwh, full_charge_mwh) < BATTERY_REPLACE_BELOW else "bonne"


# Cas 3 (portable de prêt) : extrait du rapport de batterie de Windows (powercfg /batteryreport).
CASE3_DESIGN = 56000
CASE3_FULL = 38080
CASE3_CYCLES = 612
CASE3_SCREEN: tuple[str, ...] = (
    "Rapport de batterie (extrait, fictif)",
    f"DESIGN CAPACITY        {CASE3_DESIGN:,} mWh".replace(",", " "),
    f"FULL CHARGE CAPACITY   {CASE3_FULL:,} mWh".replace(",", " "),
    f"CYCLE COUNT            {CASE3_CYCLES}",
)

# Cas 4 (portable qui chauffe) : températures avant / après nettoyage (limite de la fiche).
CASE4_LIMIT = 100
CASE4_BEFORE = ((0, 62), (5, 92), (10, 99))
CASE4_AFTER = ((0, 44), (5, 71), (10, 76), (30, 78))

TEMPS_FIGURE = Figure(
    key="pr04-temperatures-nettoyage",
    title="Températures du processeur en charge, après nettoyage (fictif)",
    alt=(
        f"Courbe de la température du processeur en charge après nettoyage, limite de la fiche à "
        f"{CASE4_LIMIT} °C : "
        + " ; ".join(f"{m} min : {t} °C" for m, t in CASE4_AFTER)
        + ". Avant nettoyage, la même charge donnait "
        + " ; ".join(f"{m} min : {t} °C" for m, t in CASE4_BEFORE)
        + "."
    ),
    caption=(
        "Après nettoyage, la température se stabilise vers "
        f"{CASE4_AFTER[-1][1]} °C, loin de la limite ; avant, elle atteignait {CASE4_BEFORE[-1][1]} °C "
        "en 10 minutes. Relevés fictifs."
    ),
    svg=line_chart_svg(
        CASE4_AFTER, threshold=CASE4_LIMIT, x_label="Minutes de charge", y_label="°C",
        threshold_label=f"Limite de la fiche : {CASE4_LIMIT} °C", y_max=120,
    ),
)

# =============================================================================================
# 6. Formulaires : réception, remise ; déchets
# =============================================================================================

RECEPTION_FIELDS: tuple[tuple[str, str], ...] = (
    ("Identification", "Date, propriétaire (ou organisme), technicien, numéro de fiche."),
    ("Matériel", "Marque, modèle, numéro de série ; étiquette d'inventaire posée."),
    ("Accessoires remis", "Chargeur, câbles, sacoche, clé, disque externe…"),
    ("État initial", "Rayures, pièces manquantes, écran, charnières, photos datées."),
    ("Mots de passe", "Fournis ou non ; utilisés seulement pour tester, à changer après."),
    ("Demande", "Réparation, reconditionnement, remise à zéro, effacement ; avec les mots du client."),
    ("Données", "À conserver (sauvegarde vérifiée) ou à effacer ; accord écrit signé."),
    ("Signature", "Propriétaire et technicien ; copie remise au client."),
)

HANDOVER_CHECKS: tuple[tuple[str, str], ...] = (
    ("Tests", "Mémoire, SMART, températures, ports, stabilité : valeurs dans le rapport."),
    ("Système", "Système et pilotes à jour, activé, aucune session ni fichier du technicien."),
    ("Données", "Restaurées et vérifiées avec le client, ou effacement certifié."),
    ("Propreté", "Boîtier fermé, toutes les vis, extérieur nettoyé, clavier et écran propres."),
    ("Accessoires", "Tous les accessoires de la fiche de réception rendus."),
    ("Pièces", "Pièces remplacées listées (références, numéros de série), anciennes rendues ou recyclées."),
    ("Conseils", "Sauvegardes, mises à jour, aération ; garantie de l'intervention."),
    ("Signature", "Rapport signé par le client ; étiquette de reconditionnement datée."),
)

WASTE_DEEE = "Collecte des équipements électriques (DEEE)"
WASTE_BATTERY = "Collecte séparée des piles et batteries"
WASTE_PAPER = "Papier-carton"
WASTE_STREAMS: tuple[tuple[str, str, str], ...] = (
    (WASTE_DEEE, ("Recyclage des appareils électriques et électroniques (Recupel en Belgique) : "
                  "recyparc, point de collecte, reprise par le vendeur à l'achat d'un appareil neuf."),
     "Cartes, blocs d'alimentation, disques (après effacement ou destruction), écrans, claviers, souris."),
    (WASTE_BATTERY, ("Piles et batteries collectées à part (Bebat en Belgique) : jamais avec les autres "
                     "déchets ; batterie lithium gonflée isolée, sans la percer ni l'écraser."),
     "Pile CR2032 de la carte mère, batteries de portable, piles de souris."),
    (WASTE_PAPER, "Emballages et notices en papier ou carton propres.", "Cartons d'emballage, notices."),
)

# (élément, filière) : tri des déchets de l'atelier (exercice E09).
WASTE_ITEMS: tuple[tuple[str, str], ...] = (
    ("Carte mère hors d'usage", WASTE_DEEE),
    ("Pile bouton CR2032 remplacée", WASTE_BATTERY),
    ("Bloc d'alimentation en panne", WASTE_DEEE),
    ("Carton d'emballage du SSD neuf", WASTE_PAPER),
    ("Batterie de portable gonflée", WASTE_BATTERY),
    ("Disque dur effacé puis déclassé", WASTE_DEEE),
    ("Piles AA de la souris sans fil", WASTE_BATTERY),
    ("Écran LCD fêlé", WASTE_DEEE),
)


def waste_stream(item: str) -> str:
    return dict(WASTE_ITEMS)[item]


PR04_FIGURES: tuple[Figure, ...] = (
    RECON_FIGURE,
    CLEANING_FIGURE,
    CLEAN_FIGURE,
    TEMPS_FIGURE,
    FIRMWARE_FIGURE,
    SMART_FIGURE,
    AFTER_TESTS_FIGURE,
    DATA_TREE_FIGURE,
    ERASE_FIGURE,
)
