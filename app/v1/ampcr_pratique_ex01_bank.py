"""EX01 « Examen blanc écrit — maintenance et dépannage matériel » — les 10 questions notées
/100 (ticket #230).

Épreuve autonome du module 1 (PR01 → PR06) : 10 questions de 10 points, **réponses libres**,
dans la réserve `exam` uniquement (`ampcr-pratique-ex01:exam`) — il n'y a pas d'exercices
d'entraînement propres à EX01 : on s'entraîne dans les cours PR01 → PR06. Organisation :

- partie 1 (sans dossier) : identification sur un plan lettré (X01), sécurité et ESD (X02),
  choix des outils (X03) ;
- **dossier A** (fiduciaire Mertens) : absence de POST après un ajout de mémoire (X04),
  vérification et compte rendu (X05) ;
- **dossier B** (studio Lumen) : compatibilité processeur/mémoire/bloc et calcul de
  puissance (X06), procédure de démontage-remontage (X07), refroidissement (X08) ;
- **dossier C** (clinique Les Saules) : SSD ajouté non détecté (X09), relevé SMART et
  protection des données (X10).

Chaque question reprend les documents du dossier dont elle a besoin : elle se résout seule,
dans n'importe quel ordre (le moteur de sessions peut mélanger les questions). Valeurs,
calculs et verdicts viennent de `app.v1.ampcr_pratique_ex01_figures` (mêmes règles que les
cours). Situations, références et relevés **fictifs** ; aucune question n'est présentée comme
officielle ou déjà posée par le Jury.
"""

from app.v1.ampcr_pratique_ex01_figures import (
    BOARD_ANSWERS,
    BOARD_CONNECTIONS,
    BOARD_CPU_LINKED,
    BOARD_FIGURE_FILE,
    BOARD_LETTERS,
    CASE_MAX_GPU_LENGTH_MM,
    DOSSIER_A_SLOTS,
    DOSSIER_A_WAIT_SECONDS,
    DOSSIER_B_LOADS,
    DOSSIER_B_PSU_W,
    DOSSIER_B_RAM_INSTALLED,
    DOSSIER_B_RAM_MAX_GB,
    DOSSIER_B_RAM_SLOTS,
    DOSSIER_B_RAM_TOTAL_AFTER_GB,
    DOSSIER_B_TOTAL_W,
    DOSSIER_C_SMART_VERDICT,
    FREE_SATA_PORTS,
    GPU_NEW_LENGTH_MM,
    GPU_NEW_PCIE_8PIN,
    GPU_NEW_PSU_RECOMMENDATION,
    GPU_NEW_W,
    LEDS_FIGURE_FILE,
    MANUAL_SHARING_RULE,
    NEW_SSD_PORT,
    PSU_CURRENT_PCIE_8PIN,
    PSU_CURRENT_W,
    TEMP_LIMIT_C,
    TEMPERATURE_LOG,
    UEFI_STORAGE_SCREEN,
    board_document_text,
    leds_document_text,
    smart_document_lines,
)
from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr02_figures import DEFAULT_MARGIN, PSU_RANGE_STEP
from app.v1.ampcr_pratique_pr03_figures import TEMP_ALERT_MARGIN
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _table
from app.v1.ampcr_pratique_pr06_bank import USAGE_EXAM, PR06Item

EX01_CODE = "EX01"
EXAM_TOTAL_POINTS = 100
POINTS_PER_QUESTION = 10
KIND_DOC = "analyse de document"
KIND_CASE = "scénario"

# Partie ou dossier de chaque question (sujet imprimable, barème global).
PART_1 = "Partie 1 — Identification et préparation"
DOSSIER_A = "Dossier A — Fiduciaire Mertens"
DOSSIER_B = "Dossier B — Studio Lumen"
DOSSIER_C = "Dossier C — Clinique vétérinaire Les Saules"


def _schema(title: str, text: str, image: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="schéma", content_text=text, image=image)


def _fr(value: float) -> str:
    return f"{value:g}".replace(".", ",")


# --- Documents partagés des dossiers ----------------------------------------------------------

_BOARD_DOC = _schema("Document 1 — Plan lettré de la carte mère (schéma fictif)", board_document_text(), BOARD_FIGURE_FILE)

_A_REQUEST = _table(
    "Dossier A, document A1 — Fiche d'intervention",
    ("Rubrique", "Contenu"),
    ("Client", "Fiduciaire Mertens (4 postes), gérante : Mme Mertens"),
    ("Poste", "PC-COMPTA-03, tour ATX, carte mère à 4 emplacements DDR5 (A1, A2, B1, B2), Windows 11"),
    ("Demande", (f"« Samedi, mon neveu a ajouté deux barrettes pour accélérer le PC. Depuis, il ne démarre plus : "
                 f"les ventilateurs tournent mais l'écran reste noir. Il a attendu une trentaine de secondes "
                 f"({DOSSIER_A_WAIT_SECONDS} s) puis a coupé, plusieurs fois. »")),
    ("Données", "Dossiers comptables sur le NAS du cabinet ; copie de vendredi soir vérifiée par le prestataire"),
    ("Autorisation", "Diagnostic et remise en état jusqu'à 100 € sans autre accord ; au-delà, devis"),
)
_A_LEDS = _schema("Dossier A, document A2 — LED de diagnostic relevées (schéma fictif)", leds_document_text(), LEDS_FIGURE_FILE)
_A_MANUAL = _table(
    "Dossier A, document A3 — Extrait du manuel de la carte mère (fictif)",
    ("Sujet", "Indication du fabricant"),
    ("LED CPU", "Processeur non détecté ou défaillant"),
    ("LED DRAM", "Mémoire non détectée ou défaillante"),
    ("LED VGA", "Aucune carte graphique ni sortie vidéo détectée"),
    ("LED BOOT", "Aucun périphérique de démarrage"),
    ("Deux barrettes", "Installer en A2 et B2"),
    ("Quatre barrettes", "La fréquence peut être abaissée automatiquement"),
    ("Mélange de barrettes", "La mémoire fonctionne à la vitesse de la plus lente ; préférer un kit identique de la liste de compatibilité"),
    ("Après une modification de la mémoire", "Le premier démarrage peut durer plusieurs minutes (entraînement de la mémoire) : ne pas couper"),
)
_A_SLOTS = _table(
    "Dossier A, document A4 — Mémoire relevée à l'ouverture (PC débranché)",
    ("Emplacement", "Barrette relevée"),
    *DOSSIER_A_SLOTS,
)
_A_LOG = _table(
    "Dossier A, document A5 — Journal de l'intervention",
    ("Heure", "Action", "Résultat"),
    ("09:10", "Réception, fiche signée, copie de vendredi vérifiée sur le NAS", "Accord écrit, données à l'abri"),
    ("09:20", "PC débranché, bouton appuyé, bracelet relié au châssis ; barrette A1 retirée puis réinsérée", "Deux clips fermés, barrette droite"),
    ("09:30", "Mise sous tension, attente sans couper", "Image après 2 min 40 s ; l'UEFI affiche 48 Go en DDR5-4800"),
    ("09:40", "Test mémoire complet (4 passages)", "11:50 — aucune erreur"),
    ("12:00", "Trois démarrages à froid, Windows, logiciel comptable ouvert par la gérante", "Démarrage normal, 48 Go reconnus, logiciel et NAS accessibles"),
)

_B_CONFIG = _table(
    "Dossier B, document B1 — Configuration actuelle de la station de montage (fiches fictives)",
    ("Élément", "Caractéristiques"),
    ("Carte mère", f"ATX, socket LGA1700, {DOSSIER_B_RAM_SLOTS} emplacements DDR5 (A1, A2, B1, B2), {DOSSIER_B_RAM_MAX_GB} Go au maximum"),
    ("Processeur", f"Socket LGA1700, puissance maximale 180 W, température maximale {TEMP_LIMIT_C} °C (fiche)"),
    ("Mémoire", DOSSIER_B_RAM_INSTALLED),
    ("Carte graphique actuelle", "160 W, un connecteur PCIe 8 broches"),
    ("Bloc d'alimentation", f"{PSU_CURRENT_W} W, 80 PLUS Bronze, non modulaire, {PSU_CURRENT_PCIE_8PIN} câble PCIe 8 broches (6+2)"),
    ("Boîtier", f"Tour ATX, bloc en bas avec filtre, carte graphique de {CASE_MAX_GPU_LENGTH_MM} mm de long au maximum"),
    ("Stockage et ventilation", "SSD NVMe, disque dur 3,5 pouces, 4 ventilateurs de boîtier"),
)
_B_REQUEST = _table(
    "Dossier B, document B2 — Demande du studio et offres reçues",
    ("Objet", "Détail"),
    ("Demande", "Remplacer la carte graphique pour accélérer les rendus et passer à 64 Go de mémoire"),
    ("Carte graphique proposée", (f"{GPU_NEW_W} W, bloc conseillé par le fabricant : {GPU_NEW_PSU_RECOMMENDATION} W, "
                                  f"{GPU_NEW_PCIE_8PIN} connecteurs PCIe 8 broches, longueur {GPU_NEW_LENGTH_MM} mm, "
                                  "2,5 emplacements, PCIe 4.0 x16")),
    ("Mémoire, kit 1", "2 × 16 Go DDR5-5600, même référence que les barrettes installées"),
    ("Mémoire, kit 2", "2 × 32 Go DDR4-3200 de récupération, offert par un ami"),
)
_B_LOADS = _table(
    "Dossier B, document B3 — Puissances maximales après la modification (fiches fictives)",
    ("Élément", "Puissance (W)"),
    *((load.name, str(load.watts)) for load in DOSSIER_B_LOADS),
)
_B_TEMPS = _table(
    "Dossier B, document B4 — Relevé pendant un rendu vidéo (logiciel de surveillance, fictif)",
    ("Minute", "Température CPU (°C)", "Fréquence CPU (GHz)", "Ventilateur CPU (tr/min)"),
    *((str(m), str(t), f, str(v)) for m, t, f, v in TEMPERATURE_LOG),
)
_B_OBS = _table(
    "Dossier B, document B5 — Observations du technicien",
    ("Point observé", "Constat"),
    ("Symptôme", "Depuis environ un mois, rendus longs très ralentis ; deux extinctions brutales en plein rendu"),
    ("Historique", "Il y a un mois, le client a remplacé lui-même le ventilateur du ventirad, bruyant"),
    ("UEFI", "Ventilateur du ventirad détecté sur SYS_FAN2, réglé à vitesse fixe ; CPU_FAN : aucun ventilateur"),
    ("Intérieur", "Filtre de façade couvert de poussière ; ailettes du ventirad grisâtres ; PC jamais nettoyé en 4 ans"),
    ("Pâte thermique", "D'origine (4 ans)"),
)

_C_REQUEST = _table(
    "Dossier C, document C1 — Demande de la clinique",
    ("Rubrique", "Contenu"),
    ("Client", "Clinique vétérinaire Les Saules, PC de l'accueil (dossiers des animaux et radiographies)"),
    ("Demande 1", (f"Un collègue a ajouté hier un SSD SATA 2,5 pouces de 1 To, neuf et vide, branché sur {NEW_SSD_PORT} "
                   "avec un câble de données neuf et une alimentation SATA du bloc. Il n'apparaît pas dans Windows.")),
    ("Demande 2", "Depuis quelques jours, certains dossiers du disque de données D: s'ouvrent très lentement, parfois avec une « erreur de lecture »"),
    ("Données", "Dossiers confidentiels ; dernière sauvegarde du disque D: sur un disque externe il y a trois semaines"),
)
_C_UEFI = _console("Dossier C, document C2 — Écran Stockage du firmware UEFI (capture fictive)", *UEFI_STORAGE_SCREEN)
_C_MANUAL = _table(
    "Dossier C, document C3 — Extrait du manuel de la carte mère (fictif)",
    ("Sujet", "Indication du fabricant"),
    ("Ports partagés", MANUAL_SHARING_RULE),
    ("Ports SATA", "SATA_1 à SATA_6, reliés au chipset, mode AHCI par défaut"),
)
_C_SMART = _console("Dossier C, document C4 — Relevé SMART du disque D: (fictif)", *smart_document_lines())

_LETTERS = ", ".join(letter for letter, _key in BOARD_LETTERS)
_PSU_WITH_MARGIN = DOSSIER_B_TOTAL_W * (1 + DEFAULT_MARGIN)
_TEMP_WATCH = TEMP_LIMIT_C - TEMP_ALERT_MARGIN

# =============================================================================================
# Les 10 questions (10 points chacune)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    # ------------------------------------------------------------------ Partie 1
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Identifier les éléments d'une carte mère sur un plan",
        question_type="document_analysis",
        requirement_ids=("AP-01", "AP-02", "AP-07", "AP-06"),
        kind=KIND_DOC,
        context=(
            "Partie 1. À l'atelier, tu prépares la fiche d'un PC de bureau à monter pour un client. "
            "Le document 1 est le plan simplifié de sa carte mère ATX, vue de dessus, plaque "
            f"d'entrées-sorties à gauche, avec douze repères lettrés ({_LETTERS}) ; chaque repère est "
            "aussi décrit par écrit. Les cadres gris sans lettre ne sont pas à identifier."
        ),
        documents=(_BOARD_DOC,),
        instructions=(
            "Nomme chacun des douze éléments repérés de A à L (une ligne par repère).",
            ("Indique sur quel repère tu branches ou installes : "
             + " ; ".join(f"{i}) {what}" for i, (what, _letter) in enumerate(BOARD_CONNECTIONS, start=1)) + "."),
            ("Cite deux repères en général reliés directement au processeur sur une plateforme récente, "
             "et dis où tu vérifies cette information pour une carte précise."),
        ),
        criteria=(
            _c("Identification des douze repères", 6, "; ".join(f"{letter} {BOARD_ANSWERS[letter]}" for letter, _key in BOARD_LETTERS) + " (0,5 pt par repère)."),
            _c("Branchements", 2, "; ".join(f"{what} → {letter}" for what, letter in BOARD_CONNECTIONS) + " (0,5 pt chacun)."),
            _c("Liaison au processeur", 2, f"{' et '.join(BOARD_CPU_LINKED)} (mémoire et PCIe x16 principal) ; H accepté si la réponse précise que le premier M.2 est souvent relié au processeur ; vérification dans le manuel (schéma-bloc ou tableau des emplacements)."),
        ),
        correction=(
            "Identification : " + " ; ".join(f"{letter} = {BOARD_ANSWERS[letter]}" for letter, _key in BOARD_LETTERS) + ".",
            ("Branchements : le câble EPS 8 broches marqué CPU va sur B (jamais un câble PCIe 8 broches, aux détrompeurs différents) ; "
             "le ventilateur du ventirad sur I (CPU_FAN, que le firmware surveille) ; les fils du bouton marche sur J, selon le brochage du manuel ; "
             "le SSD NVMe M.2 2280 dans H, fixé par sa vis."),
            ("Sur une plateforme récente, la mémoire (A) et le premier PCIe x16 (C) sont reliés au processeur, comme souvent le premier M.2 ; "
             "les ports SATA (F) passent par le chipset (K). Pour une carte précise, on le vérifie dans son manuel (schéma-bloc ou tableau des emplacements), jamais au jugé."),
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Corriger une intervention dangereuse pour le PC et pour le technicien",
        question_type="long_answer",
        requirement_ids=("AP-C02", "AP-14"),
        kind=KIND_CASE,
        context=(
            "Partie 1. Thomas, stagiaire, doit remplacer une barrette de mémoire dans un PC de bureau. "
            "Tu le trouves dans le bureau du client : il a arrêté Windows par le menu Démarrer, mais le "
            "câble secteur est toujours branché et une LED reste allumée sur la carte mère. Il est assis "
            "sur la moquette, en pull en laine, avec une montre à bracelet métallique. La barrette neuve, "
            "sortie de son sachet, est posée sur le dessus du boîtier, et il la tient par ses contacts "
            "dorés. Il porte un bracelet antistatique dont la pince est accrochée à sa ceinture."
        ),
        instructions=(
            "Relève chacune des erreurs de Thomas et explique le risque qu'elle fait courir (au PC ou à lui-même).",
            "Rédige la procédure correcte, dans l'ordre, de la mise hors tension jusqu'à l'insertion de la barrette.",
            ("Explique à Thomas, en deux ou trois phrases, pourquoi « le PC est éteint » ne suffit pas, et "
             "pourquoi une barrette peut être abîmée sans aucune trace visible."),
        ),
        criteria=(
            _c("Erreurs et risques", 4, "Câble secteur branché (le +5 VSB reste présent : court-circuit, composant abîmé) ; moquette et pull en laine (charges électrostatiques) ; bracelet relié à sa ceinture au lieu du châssis ou du tapis (aucune protection) ; barrette hors de son sachet sur le boîtier ; contacts dorés touchés (décharge, traces) ; montre métallique (contact avec la carte)."),
            _c("Procédure ordonnée", 4, "Arrêt du système ; interrupteur du bloc sur 0 ; câble secteur débranché ; appui sur le bouton marche pour décharger ; poste dégagé, table et tapis antistatique ; bijoux retirés ; bracelet relié au châssis métallique ; photo avant de toucher ; ouvrir les clips, insérer la barrette tenue par les bords, encoche alignée, jusqu'au double clic ; autre barrette dans son sachet."),
            _c("Explications", 2, "Éteint n'est pas hors tension : tant que le câble est branché, le bloc fournit le +5 VSB à la carte (LED allumée). Une décharge de quelques centaines de volts, imperceptible pour nous, peut endommager une puce sans trace visible : panne immédiate ou aléatoire plus tard."),
        ),
        correction=(
            "Erreurs : le câble secteur branché (la LED prouve que le +5 VSB est présent : un faux contact peut abîmer la carte) ; la moquette et le pull en laine, qui chargent le corps ; le bracelet accroché à la ceinture, qui ne relie Thomas à rien ; la barrette posée hors de son sachet ; les contacts dorés touchés ; la montre métallique, qui peut toucher un composant.",
            "Procédure : arrêter le système, mettre l'interrupteur du bloc sur 0, débrancher le câble secteur, appuyer quelques secondes sur le bouton marche ; installer le PC sur une table dégagée avec un tapis antistatique ; retirer bijoux et montre ; relier la pince du bracelet au châssis métallique ; photographier l'intérieur ; ouvrir les clips, sortir l'ancienne barrette, prendre la neuve par les bords, aligner l'encoche, enfoncer jusqu'à la fermeture des deux clips ; ranger l'ancienne dans le sachet.",
            "Explication : un PC éteint mais branché reçoit encore le +5 VSB (veille) ; il n'est hors tension qu'une fois débranché. Une décharge électrostatique que l'on ne sent pas suffit à détériorer une puce sans trace visible ; la panne peut n'apparaître que plus tard, de façon aléatoire.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Choisir l'outillage d'un nettoyage et d'un changement de bloc",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-C02"),
        kind=KIND_DOC,
        context=(
            "Partie 1. Tu prépares ta caisse pour une intervention sur place : dépoussiérer une tour de "
            "bureau, renouveler la pâte thermique du processeur et remplacer le bloc d'alimentation par un "
            "modèle neuf. Le document 1 liste ce qui est disponible à l'atelier."
        ),
        documents=(
            _table(
                "Document 1 — Outils et produits disponibles à l'atelier",
                ("N°", "Outil ou produit"),
                ("1", "Tournevis cruciformes PH1 et PH2"),
                ("2", "Visseuse électrique sans fil"),
                ("3", "Bracelet et tapis antistatiques"),
                ("4", "Bombe d'air sec"),
                ("5", "Aspirateur ménager avec embout fin"),
                ("6", "Pinceau souple antistatique"),
                ("7", "Alcool isopropylique et chiffon non pelucheux"),
                ("8", "Eau savonneuse et éponge"),
                ("9", "Pâte thermique neuve"),
                ("10", "Cutter"),
                ("11", "Bac à vis à cases, étiquettes et colliers de câblage"),
                ("12", "Lampe et pince à bec fin"),
            ),
        ),
        instructions=(
            "Choisis les outils et produits que tu emportes et justifie, pour chacun, l'étape où il sert.",
            "Indique au moins trois éléments du document 1 que tu écartes et pourquoi.",
            "Donne les précautions d'emploi de la bombe d'air et du dépoussiérage des ventilateurs.",
        ),
        criteria=(
            _c("Outils retenus et justifiés", 4, "PH1/PH2 (vis du boîtier, du bloc, du ventirad) ; bracelet et tapis (ESD) ; bombe d'air sec et pinceau (poussière) ; alcool isopropylique et chiffon (ancienne pâte, contacts) ; pâte neuve ; bac à vis et étiquettes (repérage des câbles du bloc), colliers ; lampe et pince (vis tombée, câbles)."),
            _c("Éléments écartés", 3, "Visseuse (arrache les filetages, glisse) ; aspirateur ménager (électricité statique, aspire des pièces) ; eau savonneuse (liquide sur l'électronique) ; cutter (raye la carte, court-circuit) — au moins trois, avec la raison."),
            _c("Précautions", 3, "PC débranché ; bombe tenue droite, courtes impulsions (sinon gaz liquide très froid) ; ventilateurs bloqués pendant le soufflage (sinon ils tournent en générateur) ; souffler de l'intérieur vers l'extérieur, filtres nettoyés à part ; ne jamais ouvrir le bloc."),
        ),
        correction=(
            "J'emporte : les tournevis PH1 et PH2 pour le boîtier, le bloc et le ventirad ; le bracelet et le tapis antistatiques pour toute manipulation ; la bombe d'air sec et le pinceau pour la poussière ; l'alcool isopropylique et le chiffon pour retirer l'ancienne pâte ; la pâte neuve ; le bac à vis, les étiquettes (repérer chaque câble du bloc avant de le débrancher) et les colliers ; la lampe et la pince à bec fin.",
            "J'écarte : la visseuse électrique, qui arrache les filetages et peut glisser sur la carte ; l'aspirateur ménager, qui crée de l'électricité statique et peut aspirer une petite pièce ; l'eau savonneuse, car aucun liquide aqueux ne doit toucher l'électronique ; le cutter, qui raye les pistes et peut provoquer un court-circuit.",
            "Précautions : PC débranché ; bombe tenue droite, par courtes impulsions (inclinée, elle projette du gaz liquide très froid) ; ventilateurs bloqués du doigt ou d'un pinceau pendant qu'on souffle ; filtres nettoyés à part ; le bloc d'alimentation n'est jamais ouvert.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier A
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Diagnostiquer un PC qui ne démarre plus après un ajout de mémoire",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-02", "AP-17"),
        kind=KIND_DOC,
        context=(
            "Dossier A. Tu interviens pour la fiduciaire Mertens sur le poste PC-COMPTA-03 qui ne démarre "
            "plus depuis l'ajout de deux barrettes de mémoire (document A1). Sous tension, les ventilateurs "
            "tournent mais rien ne s'affiche ; tu as relevé les LED de diagnostic (document A2), consulté le "
            "manuel (document A3) puis, PC débranché, noté la mémoire installée (document A4)."
        ),
        documents=(_A_REQUEST, _A_LEDS, _A_MANUAL, _A_SLOTS),
        instructions=(
            "Interprète les documents : à quelle étape le démarrage s'arrête-t-il, et quels indices (au moins trois) l'expliquent ?",
            ("Rédige ta procédure de diagnostic, dans l'ordre, de la plus simple à la plus invasive, en indiquant "
             "pour chaque test le résultat qui confirme ou écarte ton hypothèse."),
            "Indique deux actions que tu ne fais pas à ce stade, et pourquoi.",
        ),
        criteria=(
            _c("Lecture des documents", 2, "Arrêt pendant le POST, à l'étape mémoire : LED DRAM allumée fixe, CPU éteinte (processeur passé), aucune image ; des ventilateurs qui tournent ne prouvent pas un démarrage."),
            _c("Indices", 2, f"Panne apparue juste après l'ajout ; barrette A1 mal enclenchée (clip ouvert, inclinée) ; attente de {DOSSIER_A_WAIT_SECONDS} s alors que le premier démarrage après modification peut durer plusieurs minutes ; mélange de barrettes de capacités et de vitesses différentes (hors kit)."),
            _c("Procédure ordonnée et tests", 4, "PC débranché, ESD ; réinsérer A1 (deux clips) puis démarrer en attendant plusieurs minutes sans couper → image = cause trouvée ; sinon configuration d'origine seule (2 × 8 Go en A2/B2) → si elle démarre, la mémoire ajoutée est en cause ; puis les deux nouvelles seules en A2/B2, une à la fois si besoin (test croisé) ; un seul changement à la fois ; test mémoire complet une fois l'image obtenue ; liste de compatibilité du fabricant."),
            _c("Ce qu'on ne fait pas", 2, "Pas de mise à jour du firmware à l'aveugle ni de réinstallation de Windows (les données et le système ne sont pas en cause, le PC n'atteint pas le système) ; ne pas forcer une barrette ni manipuler sous tension ; ne pas déclarer une barrette défectueuse sans test croisé ; pas de remplacement de la carte mère."),
        ),
        correction=(
            f"Lecture : la LED DRAM reste allumée et la LED CPU est éteinte : le processeur a passé son contrôle, le démarrage s'arrête au POST, à l'étape mémoire (document A3). Les ventilateurs tournent simplement parce que le bloc alimente la carte. Indices : la panne date de l'ajout ; la barrette A1 est mal enclenchée (clip ouvert, inclinée) ; le neveu a coupé après {DOSSIER_A_WAIT_SECONDS} s alors que le manuel annonce un premier démarrage de plusieurs minutes après une modification de la mémoire ; les barrettes ajoutées ne forment pas un kit avec celles d'origine (16 Go DDR5-6000 et 8 Go DDR5-4800).",
            "Procédure : PC débranché, bouton appuyé, bracelet relié au châssis ; réinsérer la barrette A1 jusqu'à la fermeture des deux clips ; rebrancher et attendre plusieurs minutes sans couper. Image → cause trouvée (barrette mal insérée et entraînement de la mémoire interrompu). Toujours rien → remettre la configuration d'origine seule (8 Go en A2 et B2) : si le PC démarre, la mémoire ajoutée est en cause ; tester alors les deux barrettes neuves seules en A2/B2, puis une à la fois, pour isoler une barrette défectueuse ; un seul changement à chaque essai. Une fois l'image obtenue : test mémoire complet et vérification de la référence dans la liste de compatibilité.",
            "Je ne mets pas à jour le firmware à l'aveugle et je ne réinstalle pas Windows : le PC n'atteint même pas le système, les données ne sont pas en cause. Je ne force jamais une barrette et je ne manipule rien sous tension ; je ne conclus pas qu'une barrette est défectueuse sans l'avoir testée seule.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Vérifier la réparation et rédiger le compte rendu d'intervention",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-C01"),
        kind=KIND_DOC,
        context=(
            "Dossier A. Le poste PC-COMPTA-03 de la fiduciaire Mertens (document A1) redémarre. Ton journal "
            "d'intervention (document A5) indique ce que tu as fait et constaté. La gérante s'étonne que "
            "l'UEFI affiche de la DDR5-4800 alors que son neveu a acheté des barrettes « 6000 », et elle "
            "attend un compte rendu écrit avant de reprendre le poste."
        ),
        documents=(_A_REQUEST, _A_LOG),
        instructions=(
            "Liste au moins cinq contrôles qui permettent de déclarer l'intervention terminée, en précisant ceux déjà prouvés par le document A5.",
            ("Rédige le compte rendu d'intervention destiné à la gérante : demande, constat, cause, actions, "
             "vérifications, résultat et recommandations."),
            "Explique en termes simples pourquoi la mémoire fonctionne en DDR5-4800 et ce qu'il faudrait faire pour profiter de 6000.",
        ),
        criteria=(
            _c("Contrôles de fin d'intervention", 3, "Mémoire totale reconnue (48 Go) dans l'UEFI et Windows ; test mémoire complet sans erreur ; plusieurs démarrages à froid ; applications métier et NAS accessibles, validés par la gérante ; températures et ventilateurs normaux ; boîtier refermé, câbles rangés, date et heure correctes."),
            _c("Structure du compte rendu", 3, "Demande, constat (LED DRAM, pas d'image), cause, actions dans l'ordre, vérifications avec résultats, état final et accord de la cliente ; style professionnel, daté, compréhensible."),
            _c("Cause et explication de la vitesse", 2, "Barrette A1 mal enclenchée et premiers démarrages coupés trop tôt (entraînement de la mémoire interrompu) ; des barrettes mélangées fonctionnent toutes à la vitesse de la plus lente (4800) : ce n'est pas une panne."),
            _c("Recommandations", 2, "Pour profiter de 6000 : remplacer toutes les barrettes par un kit identique de la liste de compatibilité (4 barrettes peuvent encore abaisser la fréquence) ; après toute modification de mémoire, laisser le premier démarrage aller à son terme ; confier les ajouts de matériel à un technicien ; garder la sauvegarde sur le NAS."),
        ),
        correction=(
            "Contrôles : 48 Go reconnus dans l'UEFI et dans Windows (prouvé à 09:30 et 12:00) ; test mémoire de 4 passages sans erreur (prouvé à 11:50) ; trois démarrages à froid normaux (prouvé) ; logiciel comptable et NAS ouverts par la gérante (prouvé) ; à ajouter : températures et ventilateurs normaux, boîtier refermé, câbles en place, date et heure correctes.",
            "Compte rendu (exemple) : « Demande : le PC-COMPTA-03 ne démarrait plus depuis l'ajout de deux barrettes. Constat : ventilateurs en marche, pas d'image, LED de diagnostic DRAM allumée ; barrette A1 mal enclenchée. Cause : barrette mal insérée et premiers démarrages interrompus après 30 s, alors que la carte a besoin de plusieurs minutes pour s'adapter à une nouvelle mémoire. Actions : copie du NAS vérifiée, PC débranché, barrette réinsérée, premier démarrage mené à terme (2 min 40 s). Vérifications : 48 Go reconnus, test mémoire sans erreur, trois démarrages normaux, logiciel et NAS validés par vous. Résultat : poste opérationnel. Recommandations : voir ci-dessous. »",
            "Explication : des barrettes différentes fonctionnent toutes à la vitesse de la plus lente ; avec des 4800 d'origine, l'ensemble tourne en 4800 : c'est normal, pas une panne. Pour profiter de 6000, il faut un kit identique de la liste de compatibilité de la carte (même avec 4 barrettes identiques, la fréquence peut être abaissée). Après une modification de la mémoire, ne jamais couper le premier démarrage ; confier les ajouts à un technicien.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier B
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Vérifier la compatibilité d'une évolution et calculer le bloc d'alimentation",
        question_type="document_analysis",
        requirement_ids=("AP-17", "AP-04", "AP-06"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Le studio Lumen veut faire évoluer sa station de montage vidéo (documents B1 et B2). "
            "Avant de passer commande, tu dois vérifier chaque élément et proposer une solution complète. "
            "Le document B3 donne les puissances maximales des fiches, nouvelle carte graphique comprise. "
            f"Règle de l'atelier : bloc = total des fiches + {round(DEFAULT_MARGIN * 100)} % de marge, arrondi au "
            f"palier de {PSU_RANGE_STEP} W supérieur, jamais sous la recommandation du fabricant de la carte graphique."
        ),
        documents=(_B_CONFIG, _B_REQUEST, _B_LOADS),
        instructions=(
            ("Pour la carte graphique proposée, vérifie la puissance du bloc, les connecteurs et l'encombrement ; "
             "pour chaque kit de mémoire, dis s'il est compatible. Justifie chaque verdict."),
            "Calcule, en détaillant, la puissance du bloc nécessaire avec la règle de l'atelier.",
            "Rédige la solution complète que tu proposes au studio.",
        ),
        criteria=(
            _c("Calcul du bloc", 3, f"Total {DOSSIER_B_TOTAL_W} W ; avec la marge {_fr(round(_PSU_WITH_MARGIN, 1))} W ; palier supérieur {DOSSIER_B_PSU_W} W, au-dessus des {GPU_NEW_PSU_RECOMMENDATION} W conseillés → bloc de {DOSSIER_B_PSU_W} W."),
            _c("Bloc et connecteurs", 2, f"Bloc actuel de {PSU_CURRENT_W} W insuffisant ; un seul câble PCIe 8 broches alors que la carte en demande {GPU_NEW_PCIE_8PIN} ; pas d'adaptateur Molex ou SATA vers PCIe → nouveau bloc avec {GPU_NEW_PCIE_8PIN} connecteurs PCIe 8 broches."),
            _c("Encombrement", 2, f"Carte de {GPU_NEW_LENGTH_MM} mm pour {CASE_MAX_GPU_LENGTH_MM} mm au maximum : elle n'entre pas → choisir un modèle de {CASE_MAX_GPU_LENGTH_MM} mm au plus (vérifier aussi les 2,5 emplacements) ou changer de boîtier ; emplacement PCIe x16 compatible."),
            _c("Mémoire", 2, f"Kit 2 incompatible : DDR4 sur une carte DDR5 (encoche à une autre position, insertion impossible) ; kit 1 compatible : DDR5, même référence, {DOSSIER_B_RAM_TOTAL_AFTER_GB} Go ≤ {DOSSIER_B_RAM_MAX_GB} Go ; avec 4 barrettes, fréquence éventuellement abaissée ; liste de compatibilité."),
            _c("Solution proposée", 1, f"Kit 1 ; bloc de {DOSSIER_B_PSU_W} W avec {GPU_NEW_PCIE_8PIN} PCIe 8 broches ; carte graphique équivalente de {CASE_MAX_GPU_LENGTH_MM} mm au plus (ou nouveau boîtier) ; devis et accord du client avant commande."),
        ),
        correction=(
            f"Calcul : {' + '.join(str(load.watts) for load in DOSSIER_B_LOADS)} = {DOSSIER_B_TOTAL_W} W ; {DOSSIER_B_TOTAL_W} × {_fr(1 + DEFAULT_MARGIN)} = {_fr(round(_PSU_WITH_MARGIN, 1))} W ; palier de {PSU_RANGE_STEP} W supérieur : {DOSSIER_B_PSU_W} W, ce qui dépasse les {GPU_NEW_PSU_RECOMMENDATION} W conseillés par le fabricant. Il faut donc un bloc de {DOSSIER_B_PSU_W} W.",
            f"Bloc : celui de {PSU_CURRENT_W} W est trop faible et n'a qu'un câble PCIe 8 broches, alors que la carte en demande {GPU_NEW_PCIE_8PIN} ; un adaptateur Molex ou SATA vers PCIe est exclu (échauffement). Encombrement : {GPU_NEW_LENGTH_MM} mm pour {CASE_MAX_GPU_LENGTH_MM} mm disponibles, la carte n'entre pas : modèle de {CASE_MAX_GPU_LENGTH_MM} mm au plus, ou autre boîtier ; l'emplacement PCIe x16 convient.",
            f"Mémoire : le kit 2 est de la DDR4, incompatible avec cette carte DDR5 (l'encoche n'est pas au même endroit, la barrette n'entre pas). Le kit 1 (DDR5-5600, même référence) est compatible : {DOSSIER_B_RAM_TOTAL_AFTER_GB} Go pour {DOSSIER_B_RAM_MAX_GB} Go au maximum ; avec quatre barrettes, la carte peut abaisser la fréquence. Solution : kit 1, bloc de {DOSSIER_B_PSU_W} W avec {GPU_NEW_PCIE_8PIN} PCIe 8 broches, carte graphique de {CASE_MAX_GPU_LENGTH_MM} mm au plus ; devis soumis au studio avant toute commande.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Rédiger la procédure de démontage et de remontage de l'évolution",
        question_type="document_analysis",
        requirement_ids=("AP-14", "AP-06", "AP-C02"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Le studio Lumen a accepté le devis établi après la vérification de compatibilité : "
            "un bloc d'alimentation neuf, non modulaire, assez puissant et doté des connecteurs PCIe nécessaires ; "
            f"une carte graphique ({GPU_NEW_W} W, {GPU_NEW_PCIE_8PIN} connecteurs PCIe 8 broches) qui entre dans le boîtier ; "
            "deux barrettes DDR5 identiques à celles en place. La configuration actuelle est décrite dans le "
            "document B1. Un collègue reprendra ton travail : ta procédure doit lui permettre de tout faire sans toi."
        ),
        documents=(_B_CONFIG,),
        instructions=(
            "Rédige, dans l'ordre, la préparation et la mise en sécurité.",
            "Rédige le démontage de l'ancienne carte graphique et de l'ancien bloc.",
            "Rédige le remontage du bloc, de la carte graphique et de la mémoire, avec les points de contrôle de chaque étape.",
            "Termine par les contrôles avant fermeture et le premier démarrage.",
        ),
        criteria=(
            _c("Préparation et sécurité", 2, "Accord écrit et sauvegarde ; arrêt, interrupteur sur 0, câble débranché, bouton appuyé ; tapis et bracelet relié au châssis ; photos et étiquettes de chaque câble avant de débrancher."),
            _c("Démontage", 2, "Câbles PCIe débranchés (loquets) ; équerre dévissée ; clip du PCIe x16 ouvert ; carte sortie à la verticale ; tous les câbles du bloc débranchés (ATX 24, EPS, SATA…), vis du bloc, bloc retiré ; vis triées."),
            _c("Remontage", 4, "Bloc vissé, ventilateur vers le filtre ; ATX 24 et EPS (pas un PCIe sur l'EPS), SATA ; carte graphique dans le premier PCIe x16, clip enclenché, équerre vissée, deux câbles PCIe 8 broches enfoncés à fond, sans adaptateur ; barrettes en A1 et B1 en plus de A2/B2, encoche alignée, deux clips fermés ; câbles rangés loin des ventilateurs."),
            _c("Contrôles et premier démarrage", 2, "Contrôle visuel (aucune vis libre, câbles à fond) ; premier démarrage parfois long (entraînement de la mémoire) sans couper ; l'UEFI affiche 64 Go et la carte graphique ; pilote graphique ; test en charge avec températures ; compte rendu."),
        ),
        correction=(
            "Préparation : vérifier l'accord écrit et la sauvegarde ; arrêter le système, interrupteur du bloc sur 0, câble secteur débranché, bouton marche appuyé ; poser la tour sur une table dégagée, tapis antistatique, bracelet relié au châssis ; photographier l'intérieur et étiqueter chaque câble avant d'en débrancher un.",
            "Démontage : débrancher les câbles PCIe de la carte graphique en pressant les loquets ; dévisser son équerre ; ouvrir le clip de l'emplacement PCIe x16 ; sortir la carte à la verticale, la ranger dans un sachet antistatique. Débrancher tous les câbles du bloc (ATX 24, EPS, SATA, éventuellement Molex), dévisser ses quatre vis à l'arrière, sortir le bloc ; vis dans le bac.",
            "Remontage : visser le nouveau bloc, ventilateur vers le filtre du fond ; brancher l'ATX 24, l'EPS 8 broches marqué CPU (jamais un PCIe), les alimentations SATA. Insérer la carte graphique dans le premier emplacement PCIe x16 jusqu'au clic du clip, visser l'équerre, brancher les deux câbles PCIe 8 broches à fond, sans adaptateur. Installer les deux nouvelles barrettes en A1 et B1, encoche alignée, jusqu'à la fermeture des deux clips. Ranger les câbles avec des colliers, loin des ventilateurs.",
            "Contrôles : aucune vis libre, tous les connecteurs enfoncés ; brancher, démarrer et attendre sans couper (entraînement de la mémoire) ; vérifier dans l'UEFI 64 Go de mémoire et la carte graphique ; installer le pilote graphique ; test en charge en surveillant les températures ; fermer le boîtier et rédiger le compte rendu.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Diagnostiquer et corriger une surchauffe du processeur",
        question_type="document_analysis",
        requirement_ids=("AP-15", "AP-14", "AP-06"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Avant l'évolution, le studio Lumen signale que la station de montage ralentit fortement "
            "pendant les rendus longs et s'est éteinte deux fois. Tu as relevé les températures pendant un rendu "
            f"(document B4) et noté tes observations (document B5). La fiche du processeur indique {TEMP_LIMIT_C} °C au "
            f"maximum ; convention de l'atelier : « à surveiller » à moins de {TEMP_ALERT_MARGIN} °C de ce maximum."
        ),
        documents=(_B_TEMPS, _B_OBS),
        instructions=(
            "Interprète le relevé : verdict de la température au fil du rendu, lien avec la fréquence, le ventilateur, les ralentissements et les extinctions.",
            "Classe tes hypothèses de la plus probable à la moins probable, chacune avec l'indice qui la soutient.",
            "Rédige ton intervention dans l'ordre, avec les précautions.",
            "Indique comment tu prouves que la panne est corrigée (test, durée, valeurs attendues).",
        ),
        criteria=(
            _c("Interprétation", 3, f"Normal au repos ; à surveiller dès {_TEMP_WATCH} °C (minute 4, 98 °C) ; maximum atteint ({TEMP_LIMIT_C} °C) dès la minute 6 : anormal ; fréquence qui baisse (throttling) = ralentissements ; extinctions = arrêt de protection ; ventilateur à vitesse constante malgré la charge."),
            _c("Hypothèses classées", 3, "1) ventilateur branché sur SYS_FAN2 à vitesse fixe au lieu de CPU_FAN depuis son remplacement (chronologie d'un mois, vitesse constante) ; 2) poussière dans le filtre et le ventirad ; 3) pâte thermique de 4 ans ; écarter une cause unique non testée."),
            _c("Intervention ordonnée", 2, "Accord, PC débranché, ESD ; ventilateur rebranché sur CPU_FAN, profil automatique dans l'UEFI ; dépoussiérage (filtres, ventirad, ventilateurs bloqués, bombe droite) ; ancienne pâte retirée à l'alcool, pâte neuve, ventirad serré en croix ; un changement à la fois si on veut isoler la cause."),
            _c("Preuve de la correction", 2, f"Même rendu ou test de charge d'au moins 30 minutes ; température maximale sous {_TEMP_WATCH} °C, fréquence stable, ventilateur qui accélère avec la charge, plus d'extinction ; valeurs avant/après dans le compte rendu."),
        ),
        correction=(
            f"Le relevé est normal au repos (45 °C), « à surveiller » à la minute 4 (98 °C, à moins de {TEMP_ALERT_MARGIN} °C du maximum), puis anormal : {TEMP_LIMIT_C} °C dès la minute 6. Le processeur se protège en baissant sa fréquence (de {TEMPERATURE_LOG[0][2]} à {TEMPERATURE_LOG[-1][2]} GHz) : ce sont les ralentissements ; les extinctions sont des arrêts de protection. Le ventilateur reste vers 600 tr/min alors que la charge augmente.",
            "Hypothèses : 1) le ventilateur remplacé il y a un mois est branché sur SYS_FAN2 à vitesse fixe : il n'accélère pas (vitesse constante, panne apparue depuis ce remplacement) ; 2) la poussière (filtre de façade couvert, ailettes grisâtres) gêne l'évacuation de la chaleur ; 3) la pâte thermique d'origine, vieille de quatre ans, peut être sèche. Aucune n'est affirmée sans test.",
            "Intervention : accord du client ; PC débranché, bracelet ; rebrancher le ventilateur sur CPU_FAN et remettre son profil automatique dans l'UEFI ; dépoussiérer le filtre, le ventirad et les ventilateurs (pales bloquées, bombe tenue droite, par impulsions) ; retirer l'ancienne pâte à l'alcool isopropylique, appliquer une pâte neuve et resserrer le ventirad en croix.",
            f"Preuve : relancer le même rendu (ou un test de charge) au moins 30 minutes : la température doit rester sous {_TEMP_WATCH} °C, la fréquence stable, le ventilateur doit accélérer avec la charge, sans extinction. Les relevés avant et après sont notés dans le compte rendu.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier C
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Retrouver un SSD ajouté qui n'est pas détecté",
        question_type="document_analysis",
        requirement_ids=("AP-03", "AP-06", "AP-15"),
        kind=KIND_DOC,
        context=(
            "Dossier C. À la clinique vétérinaire Les Saules, un collègue a ajouté un SSD SATA neuf et vide qui "
            "n'apparaît pas dans Windows (document C1, demande 1). Tu as photographié l'écran Stockage du "
            "firmware UEFI (document C2) et l'extrait du manuel de la carte mère (document C3)."
        ),
        documents=(_C_REQUEST, _C_UEFI, _C_MANUAL),
        instructions=(
            "Explique pourquoi le SSD n'apparaît pas : cause la plus probable et preuve tirée des documents.",
            "Rédige la correction, puis les vérifications à faire si le SSD reste absent du firmware.",
            ("Une fois le SSD visible dans le firmware, décris ce que Windows affichera et les étapes pour le rendre "
             "utilisable ; explique pourquoi cette opération est sans risque ici et ce qui changerait pour un disque contenant des données."),
        ),
        criteria=(
            _c("Cause et preuve", 3, f"Le SSD est branché sur {NEW_SSD_PORT}, désactivé parce que M.2_2 contient un SSD M.2 SATA (documents C2 et C3) : le firmware ne le voit pas, Windows non plus ; ce n'est pas une panne du SSD."),
            _c("Correction et vérifications", 3, f"PC débranché, ESD ; déplacer le câble de données sur un port libre ({', '.join(FREE_SATA_PORTS)}) ; vérifier dans l'UEFI. Toujours absent : câble de données et alimentation SATA enfoncés, autre câble, autre port, SSD testé sur un autre PC ou un adaptateur USB."),
            _c("Rendre le SSD utilisable", 3, "Gestion des disques : disque « Non initialisé » ; initialiser en GPT ; nouveau volume simple, NTFS, lettre et nom ; vérifier dans l'Explorateur."),
            _c("Sécurité des données", 1, "Initialiser est sans risque ici car le SSD est neuf et vide ; sur un disque qui contient des données, ne jamais initialiser ni formater : identifier, sauvegarder ou récupérer d'abord."),
        ),
        correction=(
            f"Le firmware n'affiche rien sur {NEW_SSD_PORT} : ce port est désactivé, car M.2_2 contient un SSD M.2 SATA et le manuel indique que SATA_5 et SATA_6 sont alors coupés. Un disque invisible dans le firmware ne peut pas apparaître dans Windows ; le SSD n'est pas forcément en panne.",
            f"Correction : PC débranché, bracelet ; brancher le câble de données du SSD sur un port libre ({', '.join(FREE_SATA_PORTS)}) ; démarrer et vérifier l'écran Stockage. S'il reste absent : vérifier que le câble de données et l'alimentation SATA sont enfoncés des deux côtés, essayer un autre câble et un autre port, puis tester le SSD sur un autre PC ou avec un adaptateur USB.",
            "Dans Windows, Gestion des disques affichera le SSD comme « Non initialisé » : l'initialiser en GPT, créer un nouveau volume simple en NTFS, lui donner une lettre et un nom, puis vérifier qu'il apparaît dans l'Explorateur. C'est sans risque parce que le SSD est neuf et vide ; un disque qui contient des données ne s'initialise ni ne se formate jamais : on identifie le disque et on récupère ou sauvegarde d'abord.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Interpréter un relevé SMART et protéger les données du client",
        question_type="document_analysis",
        requirement_ids=("AP-03", "AP-15", "AP-C03"),
        kind=KIND_DOC,
        context=(
            "Dossier C. À la clinique vétérinaire Les Saules, certains dossiers du disque de données D: s'ouvrent "
            "très lentement, parfois avec une « erreur de lecture » (document C1, demande 2). La dernière sauvegarde "
            "date de trois semaines. Tu as relevé l'état SMART du disque (document C4). Règle de l'atelier : secteurs "
            "en attente ou illisibles supérieurs à 0 → disque à remplacer ; secteurs réalloués seuls → à surveiller."
        ),
        documents=(_C_REQUEST, _C_SMART),
        instructions=(
            "Interprète le relevé SMART avec la règle de l'atelier, relie-le aux symptômes et explique pourquoi « PASSED » ne suffit pas.",
            "Rédige ton plan d'action dans l'ordre, en protégeant les données et leur confidentialité.",
            "Cite deux actions à ne pas faire sur ce disque avant d'avoir copié les données, et pourquoi.",
            "Rédige le court message (quatre ou cinq lignes) qui explique la situation au vétérinaire et lui demande son accord.",
        ),
        criteria=(
            _c("Interprétation", 3, f"24 secteurs en attente et 24 illisibles : disque {DOSSIER_C_SMART_VERDICT} selon la règle, même si le résumé affiche PASSED (seuils du fabricant pas encore atteints) ; cohérent avec les lenteurs et les erreurs de lecture ; câble hors de cause (CRC à 0)."),
            _c("Plan d'action ordonné", 4, "Accord écrit ; limiter l'utilisation du disque ; copier d'abord les données (ou une image avec un outil qui tolère les erreurs) vers un autre support de capacité suffisante, jamais vers le même disque ; vérifier la copie ; remplacer le disque ; restaurer et contrôler ; remettre en place une sauvegarde régulière (3-2-1) ; confidentialité : on ne consulte pas les dossiers."),
            _c("Actions interdites", 1, "Pas de chkdsk /r, de défragmentation, de formatage ni de réparation avant la copie : ces opérations sollicitent un disque qui faiblit et peuvent détruire les données encore lisibles."),
            _c("Message au client", 2, "Clair et sans jargon : le disque des dossiers montre des signes d'usure qui mènent à la perte de données ; risque pour les données créées depuis la dernière sauvegarde ; proposition (copie immédiate, remplacement, coût) ; demande d'accord écrit."),
        ),
        correction=(
            f"Le relevé montre 24 secteurs en attente et 24 secteurs illisibles : selon la règle de l'atelier, le disque est {DOSSIER_C_SMART_VERDICT}. Le résumé « PASSED » signifie seulement qu'aucun seuil du fabricant n'est encore franchi : il ne garantit rien. Ces secteurs illisibles expliquent les lenteurs (le disque réessaie) et les erreurs de lecture ; avec 0 erreur CRC, le câble n'est pas en cause.",
            "Plan : obtenir l'accord écrit ; demander de limiter l'usage du disque D: ; copier d'abord les dossiers, ou faire une image avec un outil qui tolère les erreurs, vers un autre support de capacité suffisante (jamais vers le même disque) ; vérifier que la copie se relit ; remplacer le disque ; restaurer les données et faire contrôler l'accès par la clinique ; mettre en place une sauvegarde régulière (règle 3-2-1). Les dossiers des animaux ne sont pas consultés pendant l'opération.",
            "Avant la copie, ni chkdsk /r, ni défragmentation, ni formatage ou réparation : ces opérations lisent ou réécrivent tout le disque et peuvent faire perdre les données encore lisibles.",
            "Message : « Le disque qui contient vos dossiers présente des secteurs illisibles : c'est un signe d'usure qui mène à la perte de données. Votre dernière sauvegarde date de trois semaines. Je vous propose de copier immédiatement vos données sur un autre support, puis de remplacer ce disque (devis joint). Pouvez-vous me donner votre accord écrit ? »",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = EXAM_ITEMS
PRACTICE_ITEMS: tuple[PR06Item, ...] = ()

# Partie ou dossier de chaque question, dans l'ordre du sujet.
ITEM_PARTS: dict[str, str] = {
    "X01": PART_1, "X02": PART_1, "X03": PART_1,
    "X04": DOSSIER_A, "X05": DOSSIER_A,
    "X06": DOSSIER_B, "X07": DOSSIER_B, "X08": DOSSIER_B,
    "X09": DOSSIER_C, "X10": DOSSIER_C,
}
# Cours où revoir la matière de chaque question.
ITEM_COURSES: dict[str, tuple[str, ...]] = {
    "X01": ("PR01",),
    "X02": ("PR02", "PR03"),
    "X03": ("PR03", "PR04"),
    "X04": ("PR06", "PR01"),
    "X05": ("PR04", "PR06"),
    "X06": ("PR01", "PR02"),
    "X07": ("PR03", "PR02"),
    "X08": ("PR04", "PR06"),
    "X09": ("PR05", "PR01"),
    "X10": ("PR04", "PR05"),
}
DOSSIER_DOCUMENTS: dict[str, tuple[ExerciseDocument, ...]] = {
    DOSSIER_A: (_A_REQUEST, _A_LEDS, _A_MANUAL, _A_SLOTS, _A_LOG),
    DOSSIER_B: (_B_CONFIG, _B_REQUEST, _B_LOADS, _B_TEMPS, _B_OBS),
    DOSSIER_C: (_C_REQUEST, _C_UEFI, _C_MANUAL, _C_SMART),
}


def validate_items() -> list[str]:
    errors = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.total_points != POINTS_PER_QUESTION:
            errors.append(f"{item.key} : {item.total_points:g} points au lieu de {POINTS_PER_QUESTION}.")
        if item.question_type not in ("long_answer", "document_analysis"):
            errors.append(f"{item.key} : réponse libre attendue.")
        if (item.question_type == "document_analysis") != bool(item.documents):
            errors.append(f"{item.key} : type et documents incohérents.")
    if sum(i.total_points for i in ALL_ITEMS) != EXAM_TOTAL_POINTS:
        errors.append("Total différent de 100 points.")
    return errors
