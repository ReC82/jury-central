"""EX03 « Examen blanc écrit — câblage RJ45, BNC et fibre » — les 10 questions notées /100
(ticket #232).

Épreuve autonome du module 3 (PR13 → PR17) : 10 questions de 10 points, **réponses libres**,
dans la réserve `exam` uniquement (`ampcr-pratique-ex03:exam`) — pas d'exercices
d'entraînement propres à EX03 : on s'entraîne dans les cours PR13 → PR17. Organisation :

- partie 1 (sans dossier) : fiche RJ45 à contrôler et brochages T568A/T568B (X01), cordon droit,
  croisé et Auto MDI-X (X02) ;
- **dossier A** (Imprimerie Lambert, câblage cuivre neuf) : choix des câbles (X03),
  certification des liens (X04), relevé de pose et réalisation d'un cordon (X05) ;
- **dossier B** (musée de l'informatique « Octet », coaxial) : bus 10BASE2 non conforme (X06),
  mesures à l'ohmmètre, réalisation d'un câble BNC et 10BASE5 (X07) ;
- **dossier C** (Brasserie Van Daele, fibre) : choix des liaisons et des modules (X08), bilan
  et réception au photomètre (X09), panne après des travaux et réflectomètre (X10).

Chaque question reprend les documents du dossier dont elle a besoin : elle se résout seule,
dans n'importe quel ordre. Valeurs et verdicts viennent de `app.v1.ampcr_pratique_ex03_figures`
(mêmes règles que les cours). Situations, références et mesures **fictives** ; aucune question
n'est présentée comme officielle ou déjà posée par le Jury.
"""

from app.v1.ampcr_pratique_ex03_figures import (
    BUS_FIGURE,
    BUS_FIGURE_FILE,
    CABLE_CHOICES,
    CABLE_NEEDS,
    CERT_FIGURE,
    CERT_FIGURE_FILE,
    CERT_FIGURE_LINKS,
    CERT_PORT_FIGURE,
    CERT_ROWS,
    FIBRE_L1_M,
    HALL_1G_VERDICT,
    HALL_10G_VERDICT,
    HALL_M,
    L1_CHOICE,
    L1_CONNECTORS,
    L1_DB_PER_KM,
    L1_MAX_LOSS,
    L1_OM4_VERDICT,
    L1_RX_EXPECTED,
    L1_RX_MARGIN,
    L1_RX_STATUS,
    L1_SPLICES,
    L1_TX_DBM,
    L1_WAVELENGTH,
    L2_CHOICE,
    LINKS,
    LONG_CORDS_M,
    LONG_PERMANENT_M,
    LONG_PORT,
    MADE_PLUG_LINKS,
    MUSEUM_ERRORS,
    OHM_READINGS,
    OPEN_PORT,
    OTDR_FIGURE,
    OTDR_FIGURE_FILE,
    OUTAGE_BEND_M,
    OUTAGE_BREAK_M,
    OUTAGE_SCREEN,
    OUTAGE_TRACE,
    PHOTO_LOSSES,
    PHOTO_READINGS,
    PHOTO_REFERENCE_DBM,
    PHOTO_VERDICTS,
    PLUG_FIGURE,
    PLUG_FIGURE_FILE,
    REPAIR_BEND_PULL_MM,
    REPAIR_BEND_REST_MM,
    REPAIR_CABLE_DIAMETER_MM,
    REPAIRED_MAX_LOSS,
    RUN_ERRORS,
    RUN_MIN_RADIUS,
    RUNS,
    SPLIT_PORT,
    TEN_G_LENGTH_M,
    TEN_G_PORT,
    TEN_G_VERDICT,
    WRONG_PINS,
    WRONG_TERMINATOR_GAMMA,
    run_rows,
)
from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _table
from app.v1.ampcr_pratique_pr06_bank import USAGE_EXAM, PR06Item
from app.v1.ampcr_pratique_pr13_figures import RUN_OK
from app.v1.ampcr_pratique_pr16_figures import reading_text
from app.v1.ampcr_pratique_pr17_figures import LR_SPEC, dbm_fr, fr

EX03_CODE = "EX03"
EXAM_TOTAL_POINTS = 100
POINTS_PER_QUESTION = 10
KIND_DOC = "analyse de document"
KIND_CASE = "scénario"

# Partie ou dossier de chaque question (sujet imprimable, barème global).
PART_1 = "Partie 1 — Fiches et cordons RJ45"
DOSSIER_A = "Dossier A — Imprimerie Lambert"
DOSSIER_B = "Dossier B — Musée de l'informatique « Octet »"
DOSSIER_C = "Dossier C — Brasserie Van Daele"

T568A_TEXT = ("1 blanc/vert, 2 vert, 3 blanc/orange, 4 bleu, 5 blanc/bleu, 6 orange, 7 blanc/marron, "
              "8 marron")
T568B_TEXT = ("1 blanc/orange, 2 orange, 3 blanc/vert, 4 bleu, 5 blanc/bleu, 6 vert, 7 blanc/marron, "
              "8 marron")
ORIENTATION_TEXT = "fiche vue côté contacts, languette dessous, extrémité vers le haut : broche 1 à gauche"


def _schema(title: str, text: str, image: str) -> ExerciseDocument:
    return ExerciseDocument(title=title, kind="schéma", content_text=text, image=image)


def _links(links: tuple[tuple[int, int], ...]) -> str:
    return ", ".join(f"{a}→{b}" for a, b in links if a != b)


_RUN_BY_KEY = {run.name.split(" — ")[0]: run for run in RUNS}


def _run_verdict(key: str) -> str:
    run = _RUN_BY_KEY[key]
    errors = RUN_ERRORS[run.name]
    return " et ".join(errors).lower() if errors else RUN_OK.lower()


def _min_radius(key: str) -> str:
    return f"{fr(RUN_MIN_RADIUS[_RUN_BY_KEY[key].name])} mm"


_CHOICE = {ref: choice.cable for ref, choice in CABLE_CHOICES.items()}
_OHM = {day: reading_text(value) for day, _ctx, value in OHM_READINGS}
_F1, _F2 = (name for name, _r in PHOTO_READINGS)
_LAUNCH = OUTAGE_TRACE.launch_m
_BEND_AT = OUTAGE_TRACE.events[1].position_m
_END_AT = OUTAGE_TRACE.end_m

# --- Documents ---------------------------------------------------------------------------------

_P1_PLUG = _schema("Document 1 — Fiche RJ45 sertie par le stagiaire (schéma fictif)", PLUG_FIGURE.alt, PLUG_FIGURE_FILE)
_P1_LINKS = _table(
    "Document 2 — Liaisons à réaliser dans l'atelier de formation",
    ("Liaison", "Auto MDI-X (fiches techniques)"),
    *((name, "oui, sur les deux équipements" if auto else "non, sur aucun des deux") for name, _a, _b, auto in LINKS),
)

_A_REQUEST = _table(
    "Dossier A, document A1 — Fiche du chantier",
    ("Rubrique", "Contenu"),
    ("Client", "Imprimerie Lambert (18 personnes) ; responsable : M. Lambert"),
    ("Travaux", ("Recâblage complet après rénovation : bureaux à l'étage, local technique (baie B1), atelier des "
                 "presses au rez-de-chaussée, quai de chargement, magasin de papier au fond du site")),
    ("Norme du chantier", "Toutes les prises et tous les panneaux en T568B ; repère identique aux deux bouts (B1-P1-xx)"),
    ("Exigences", "1 Gb/s partout ; 10 Gb/s entre le serveur et le switch cœur et vers le poste de PAO ; caméra analogique conservée"),
    ("Réception", "Chaque lien est testé et le rapport de test est remis au client avant paiement"),
)
_A_NEEDS = _table(
    "Dossier A, document A2 — Liaisons à câbler",
    ("Repère", "Trajet", "Besoin et environnement"),
    *((ref, path, env) for ref, path, _need, env in CABLE_NEEDS),
)
_A_CERT = _table(
    "Dossier A, document A3 — Extrait du rapport de test des liens",
    ("Lien", "Résultat du testeur", "Remarque"),
    *CERT_ROWS,
)
_A_TESTER = _schema(
    f"Dossier A, document A4 — Testeur sur le lien {CERT_PORT_FIGURE} (affichage fictif)",
    CERT_FIGURE.alt,
    CERT_FIGURE_FILE,
)
_A_RUNS = _table(
    "Dossier A, document A5 — Relevé de pose fait par le chef d'équipe",
    ("Tronçon", "Rayon de courbure le plus serré", "Traction mesurée au tirage", "Câbles électriques en parallèle"),
    *run_rows(),
)

_B_REQUEST = _table(
    "Dossier B, document B1 — Demande du musée de l'informatique « Octet » (asbl)",
    ("Rubrique", "Contenu"),
    ("Salle rétro", ("Cinq machines d'époque en réseau Ethernet 10BASE2 pour les démonstrations. Un bénévole a "
                     "remonté le segment avec le matériel trouvé dans les réserves, dont un kit de vidéosurveillance. "
                     "Le réseau ne fonctionne pas.")),
    ("Salle 2", "Second segment 10BASE2 (4 postes), fonctionnel en temps normal ; relevés de la semaine en B3"),
    ("Projet", "Exposer aussi un segment d'Ethernet épais 10BASE5 récupéré dans une université"),
    ("Matériel disponible", "RG-58 C/U, BNC à sertir pour RG-58, T BNC, terminateurs 50 Ω, pince et matrices, dénudeur coaxial, multimètre"),
)
_B_BUS = _schema(
    "Dossier B, document B2 — Bus 10BASE2 de la salle rétro, relevé avant intervention (schéma fictif)",
    BUS_FIGURE.alt,
    BUS_FIGURE_FILE,
)
_B_OHM = _table(
    "Dossier B, document B3 — Salle 2 : mesures à l'ohmmètre entre âme et blindage au T du Poste A, réseau arrêté",
    ("Jour", "Contexte", "Lecture"),
    *((day, ctx, _OHM[day]) for day, ctx, _v in OHM_READINGS),
)

_C_REQUEST = _table(
    "Dossier C, document C1 — Fiche du projet",
    ("Rubrique", "Contenu"),
    ("Client", "Brasserie Van Daele ; gérante : Mme Van Daele"),
    ("L1", f"Bureaux → entrepôt (autre bâtiment), {FIBRE_L1_M} m de fourreau enterré mesuré ; 10 Gb/s souhaité"),
    ("L2", "Salle serveur → plateau du 1er étage, même bâtiment, 70 m de parcours ; 10 Gb/s souhaité"),
    ("L3 existante", (f"Bureaux → hall de production : fibre multimode OM2 de {HALL_M} m posée en 2009, "
                      "modules 1000BASE-SX ; la gérante voudrait passer à 10 Gb/s sans travaux")),
    ("Switchs", "Ports SFP+ (10 Gb/s) et SFP (1 Gb/s) disponibles aux deux bouts"),
)
_C_CATALOGUE = _table(
    "Dossier C, document C2 — Catalogue du fournisseur (extrait)",
    ("Article", "Description"),
    ("Module SFP+ 10GBASE-SR", "850 nm, multimode, connecteur LC duplex"),
    ("Module SFP+ 10GBASE-LR", "1 310 nm, monomode, connecteur LC duplex"),
    ("Module SFP 1000BASE-SX", "850 nm, multimode, connecteur LC duplex"),
    ("Câble OM4 8 fibres", "Multimode 50 µm, gaine aqua, extérieur, armé"),
    ("Câble OS2 8 fibres", "Monomode 9 µm, gaine jaune, extérieur, armé"),
    ("Jarretière OS2 LC/UPC – LC/UPC duplex", "Connecteurs bleus"),
    ("Jarretière OS2 SC/APC – LC/UPC duplex", "Un connecteur vert, un bleu"),
    ("Jarretière OM4 LC – LC duplex", "Connecteurs aqua"),
)
_C_RECEPTION = _table(
    f"Dossier C, document C3 — Réception de L1 (OS2, {FIBRE_L1_M} m) : relevés de l'installateur",
    ("Élément", "Relevé"),
    ("Composition", f"{L1_CONNECTORS} paires de connecteurs (une par tiroir optique) et {L1_SPLICES} épissures par fusion (pigtails)"),
    ("Valeurs du cours", f"OS2 à {L1_WAVELENGTH} nm : {fr(L1_DB_PER_KM, 1)} dB/km ; 0,75 dB par paire de connecteurs ; 0,3 dB par épissure"),
    ("Photomètre", f"Source à {L1_WAVELENGTH} nm ; référence prise avec le cordon de référence : {dbm_fr(PHOTO_REFERENCE_DBM)} dBm"),
    *((name, f"Lecture au bout de la liaison : {dbm_fr(reading)} dBm") for name, reading in PHOTO_READINGS),
    ("Module 10GBASE-LR (fiche fictive)", (f"Puissance émise mesurée {dbm_fr(L1_TX_DBM)} dBm ; réception de "
                                           f"{dbm_fr(LR_SPEC.sensitivity_dbm)} à {dbm_fr(LR_SPEC.overload_dbm)} dBm")),
)
_C_OUTAGE = _console("Dossier C, document C4 — État des ports de L1 le jour de la panne (capture fictive)", *OUTAGE_SCREEN)
_C_OTDR = _schema(
    "Dossier C, document C5 — Réflectomètre sur la fibre 2, depuis le tiroir BUREAUX (trace fictive)",
    OTDR_FIGURE.alt,
    OTDR_FIGURE_FILE,
)

# =============================================================================================
# Les 10 questions (10 points chacune)
# =============================================================================================

_WRONG = ", ".join(str(p) for p in WRONG_PINS)

EXAM_ITEMS: tuple[PR06Item, ...] = (
    # ------------------------------------------------------------------ Partie 1
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Contrôler une fiche RJ45 et rédiger les brochages T568A et T568B",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-18", "AP-20"),
        kind=KIND_DOC,
        context=(
            "Partie 1. Un stagiaire a fabriqué un cordon droit de 2 m. La norme du client est T568B ; l'autre bout du "
            "cordon est correct. Tu relèves la fiche qu'il vient de sertir (document 1), dans l'orientation de "
            "lecture du cours."
        ),
        documents=(_P1_PLUG,),
        instructions=(
            ("Écris l'ordre complet des fils des normes T568A et T568B, de la broche 1 à la broche 8, en précisant "
             "comment la fiche est tenue pour lire la broche 1."),
            "Compare la fiche du document 1 à la norme du client : cite chaque broche fausse et le fil qui devrait s'y trouver.",
            ("Indique ce qu'affichera un testeur de câble (wiremap) sur ce cordon, puis ce que tu fais : peut-on le "
             "livrer, et comment le corriges-tu ?"),
        ),
        criteria=(
            _c("Brochages et orientation", 4, f"T568A : {T568A_TEXT}. T568B : {T568B_TEXT}. Lecture : {ORIENTATION_TEXT}. 1,5 point par norme complète et exacte, 1 point pour l'orientation."),
            _c("Erreurs repérées", 3, f"Broches {_WRONG} fausses : broche 4 blanc/bleu au lieu de bleu, broche 5 bleu au lieu de blanc/bleu (paire bleue inversée) ; broche 7 marron au lieu de blanc/marron, broche 8 blanc/marron au lieu de marron (paire marron inversée). Les paires restent sur leurs positions 4-5 et 7-8 : pas de paire séparée."),
            _c("Testeur et correction", 3, f"Wiremap en échec : {_links(MADE_PLUG_LINKS)} (paires 4-5 et 7-8 inversées), les autres broches droites. Cordon non conforme : on ne le livre pas, même si un lien s'établit (beaucoup de cartes corrigent la polarité) ; couper la fiche, redénuder, ranger en T568B, contrôler l'ordre à travers la fiche, sertir, retester jusqu'à « réussi »."),
        ),
        correction=(
            f"T568A, broches 1 à 8 : {T568A_TEXT}. T568B : {T568B_TEXT}. On lit la fiche contacts dorés vers soi, languette dessous, extrémité de la fiche vers le haut et câble vers le bas : la broche 1 est à gauche. Seules les paires orange et verte changent de place entre les deux normes.",
            f"Par rapport à T568B, les broches {_WRONG} sont fausses : en 4 il y a blanc/bleu au lieu de bleu, en 5 bleu au lieu de blanc/bleu, en 7 marron au lieu de blanc/marron, en 8 blanc/marron au lieu de marron. Les deux fils de chaque paire sont permutés, mais chaque paire reste sur sa position (4-5, 7-8) : ce n'est pas une paire séparée.",
            f"L'autre bout étant correct, le testeur affiche un échec avec {_links(MADE_PLUG_LINKS)} : paires 4-5 et 7-8 inversées. Un cordon qui échoue au test ne se livre pas, même si une carte réseau arrive parfois à établir un lien. Je coupe la fiche, je redénude 25 à 30 mm, je range les fils en T568B, je recoupe droit à 12-13 mm, je contrôle l'ordre à travers la fiche, je sertis puis je reteste jusqu'à obtenir 1→1 … 8→8.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Choisir un cordon droit ou croisé et expliquer l'Auto MDI-X",
        question_type="document_analysis",
        requirement_ids=("AP-18", "AP-20", "AP-34"),
        kind=KIND_DOC,
        context=(
            "Partie 1. Dans l'atelier de formation, tu prépares les cordons de quatre liaisons (document 2). Le stock "
            "contient des fiches RJ45, du câble Cat5e U/UTP multibrin et une pince à sertir. Un collègue affirme "
            "qu'« un câble croisé n'est plus jamais utile »."
        ),
        documents=(_P1_LINKS,),
        instructions=(
            "Pour chaque liaison, indique le cordon (droit ou croisé) et la norme de chacun des deux bouts ; justifie.",
            ("Explique à l'aide des broches pourquoi deux ports de même type sans Auto MDI-X demandent un croisé "
             "en 10/100 Mb/s : quelles broches émettent, lesquelles reçoivent, et comment le croisé les relie."),
            ("Explique ce que fait l'Auto MDI-X, puis réponds au collègue : quand un croisé reste-t-il nécessaire, "
             "et quel cordon poses-tu par défaut aujourd'hui ?"),
        ),
        criteria=(
            _c("Quatre cordons justifiés", 4, "Liaison 1 : droit (MDI ↔ MDI-X), T568B aux deux bouts (ou A/A) ; liaison 2 : croisé (deux MDI-X sans Auto MDI-X), T568A d'un côté et T568B de l'autre ; liaison 3 : droit, l'Auto MDI-X des cartes 1 Gb/s fait l'inversion (un croisé marcherait aussi) ; liaison 4 : croisé (deux MDI sans Auto MDI-X). 1 point par liaison."),
            _c("Broches et croisement", 3, "En 10BASE-T et 100BASE-TX, un port MDI (carte) émet sur 1-2 et reçoit sur 3-6 ; un port MDI-X (switch) fait l'inverse ; 4-5 et 7-8 ne servent pas. Le croisé relie 1→3, 2→6, 3→1, 6→2 (paires orange et verte échangées, 4, 5, 7, 8 droits) : l'émission de chaque côté arrive sur la réception de l'autre."),
            _c("Auto MDI-X et réponse", 3, "Le port détecte seul s'il doit inverser émission et réception : un cordon droit suffit partout. À 1 Gb/s, les 4 paires émettent et reçoivent en même temps. Le croisé reste nécessaire entre deux équipements de même type dont aucun ne fait l'Auto MDI-X (anciens switchs, anciennes cartes 10/100) ; par défaut on pose du droit, aux normes du site."),
        ),
        correction=(
            "Liaison 1 : cordons droits (T568B aux deux bouts, comme le site), car une carte réseau (MDI) se relie à un switch (MDI-X). Liaison 2 : deux switchs MDI-X sans Auto MDI-X ni port uplink → croisé, T568A à un bout et T568B à l'autre. Liaison 3 : les cartes 1 Gb/s font l'Auto MDI-X → un cordon droit suffit (un croisé fonctionnerait aussi). Liaison 4 : deux cartes 100 Mb/s (MDI) sans Auto MDI-X → croisé A/B.",
            "En 10/100 Mb/s, une carte réseau émet sur les broches 1-2 et reçoit sur 3-6 ; un switch reçoit sur 1-2 et émet sur 3-6 ; 4-5 et 7-8 sont inutilisées. Entre deux ports de même type, émission face à émission : rien ne passe. Le croisé (A d'un côté, B de l'autre) relie 1→3, 2→6, 3→1 et 6→2 : la paire orange et la paire verte changent de place, l'émission de chacun arrive sur la réception de l'autre.",
            "L'Auto MDI-X détecte automatiquement le câble et inverse lui-même émission et réception : avec lui, un cordon droit convient partout. À 1 Gb/s, les quatre paires servent dans les deux sens à la fois. Le collègue a presque raison : le croisé ne sert plus qu'entre deux équipements de même type dont aucun ne fait l'Auto MDI-X (vieux switchs, vieilles cartes 10/100). Par défaut, on pose des cordons droits, à la norme du site.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier A
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Choisir le câble de chaque liaison d'un recâblage",
        question_type="document_analysis",
        requirement_ids=("AP-18", "AP-19", "AP-20"),
        kind=KIND_DOC,
        context=(
            "Dossier A. L'imprimerie Lambert fait recâbler ses locaux rénovés (document A1). Tu dois rédiger la "
            "commande de câbles pour les cinq liaisons du document A2, en justifiant chaque choix auprès de "
            "M. Lambert, qui a entendu dire qu'« un câble blindé, c'est toujours mieux »."
        ),
        documents=(_A_REQUEST, _A_NEEDS),
        instructions=(
            ("Pour chaque liaison L1 à L5, donne le support (catégorie et blindage, ou autre famille), le connecteur "
             "et la justification : débit, longueur, perturbations, mise à la terre."),
            ("Explique ce que veulent dire les désignations U/UTP, F/UTP et S/FTP (lettres avant et après la barre), "
             "et pourquoi « blindé » n'est pas toujours mieux."),
            "Rappelle la longueur maximale d'un lien en paire torsadée et le débit atteint par Cat5e, Cat6 et Cat6A sur cette longueur.",
        ),
        criteria=(
            _c("Cinq choix justifiés", 5, f"L1 : {_CHOICE['L1']} (1 Gb/s, perturbations faibles ; Cat6 ou Cat6A accepté si on prévoit plus) ; L2 : {_CHOICE['L2']} (10 Gb/s → Cat6A, perturbations moyennes, baie à la terre) ; L3 : {_CHOICE['L3']} (perturbations fortes, terre disponible ; Cat6A accepté) ; L4 : {_CHOICE['L4']}, BNC 75 Ω (vidéo analogique, impédance de la caméra) ; L5 : fibre optique (140 m > 100 m de canal). Connecteurs blindés avec un câble blindé. 1 point par liaison."),
            _c("Désignations et blindage", 3, "Avant la barre : écran global (U aucun, F feuillard, S tresse) ; après : écran de chaque paire (U aucun, F feuillard) ; TP = paires torsadées. U/UTP sans écran ; F/UTP feuillard global ; S/FTP tresse globale et paires sous feuillard. Un écran n'est utile que relié à la terre de bout en bout avec des connecteurs blindés ; mal raccordé, il ne protège plus et peut même capter des perturbations ; câble plus cher, plus épais et rayon de courbure plus grand."),
            _c("Longueurs et débits", 2, "Canal de 100 m au plus (lien permanent ≤ 90 m + cordons ≤ 10 m). Cat5e : 1 Gb/s ; Cat6 : 1 Gb/s sur 100 m, 10 Gb/s seulement sur une longueur réduite (55 m au plus, à certifier) ; Cat6A : 10 Gb/s sur 100 m."),
        ),
        correction=(
            f"L1 (bureaux, 1 Gb/s, 45 m, perturbations faibles) : {_CHOICE['L1']}, connecteurs non blindés ; Cat6A se défend si l'on veut 10 Gb/s plus tard. L2 (serveur, 10 Gb/s, 25 m, onduleur et climatisation, baie à la terre) : {_CHOICE['L2']}, connecteurs blindés. L3 (presses et variateurs, perturbations fortes, terre disponible) : {_CHOICE['L3']}, connecteurs blindés reliés à la terre. L4 (caméra analogique) : {_CHOICE['L4']} avec BNC 75 Ω, la caméra et l'enregistreur étant en 75 Ω. L5 (140 m) : fibre optique, car la paire torsadée est limitée à 100 m de canal.",
            "La lettre avant la barre décrit l'écran global (U : aucun, F : feuillard, S : tresse), celle après la barre l'écran de chaque paire ; TP signifie paires torsadées. U/UTP n'a aucun écran, F/UTP un feuillard autour des quatre paires, S/FTP une tresse globale et un feuillard par paire. Un écran ne protège que s'il est continu et relié à la terre aux deux bouts du lien, avec des connecteurs blindés ; sinon il est inutile, voire nuisible. Il coûte plus cher, rend le câble plus épais et demande un rayon de courbure plus grand : on le réserve aux zones perturbées.",
            "Un lien en paire torsadée ne dépasse pas 100 m de canal : 90 m de lien permanent plus 10 m de cordons. Sur cette longueur, Cat5e porte 1 Gb/s, Cat6 aussi (10 Gb/s seulement sur 55 m au plus, après certification) et Cat6A 10 Gb/s.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Interpréter le rapport de test des liens et décider des reprises",
        question_type="document_analysis",
        requirement_ids=("AP-34", "AP-19", "AP-20"),
        kind=KIND_DOC,
        context=(
            "Dossier A. À la fin du chantier de l'imprimerie Lambert (document A1), tu analyses le rapport de test "
            "des liens avant de le remettre au client : un extrait (document A3) et l'affichage du testeur sur le lien "
            f"{CERT_PORT_FIGURE} (document A4). Chaque lien va du panneau de la baie B1 à une prise murale."
        ),
        documents=(_A_REQUEST, _A_CERT, _A_TESTER),
        instructions=(
            (f"Interprète l'affichage du lien {CERT_PORT_FIGURE} : quel défaut, quelle cause probable sur ce chantier, "
             "et quelle reprise ?"),
            f"Pour {LONG_PORT}, vérifie les longueurs avec les limites de la norme et propose une solution.",
            f"Pour {OPEN_PORT} et {SPLIT_PORT}, donne le défaut, sa cause probable et la reprise.",
            (f"Pour {TEN_G_PORT}, dis si le lien convient à 10 Gb/s et ce que tu proposes au client. "
             "Termine par ce que tu fais après chaque reprise."),
        ),
        criteria=(
            _c(f"Lien {CERT_PORT_FIGURE}", 3, f"{_links(CERT_FIGURE_LINKS)} : paires orange et verte croisées, 4, 5, 7, 8 droits → le lien est câblé en croisé : une extrémité en T568A, l'autre en T568B. Sur ce chantier tout doit être en T568B : la prise murale a été poinçonnée en A (code couleur A/B imprimé sur le connecteur) ; reprendre la prise en T568B, puis retester."),
            _c(f"Longueurs de {LONG_PORT}", 2, f"Lien permanent {LONG_PERMANENT_M} m > 90 m et canal {LONG_PERMANENT_M + LONG_CORDS_M} m > 100 m : non conforme ; raccourcir les cordons ne suffit pas (le lien permanent reste trop long) ; repasser le câble par un chemin plus court, déplacer la prise ou installer un switch d'étage (ou une fibre) ; retester."),
            _c("Ouvert et paires séparées", 3, f"{OPEN_PORT} : circuit ouvert sur la broche 7 (blanc/marron en T568B) : fil mal poinçonné, pas en butée ou coupé, à la prise ou au panneau → contrôler les deux bouts, repoinçonner, retester. {SPLIT_PORT} : continuité parfaite mais diaphonie en échec sur 3-6 et 4-5 : paires séparées (fils rangés dans l'ordre 1 à 8 sans respecter les paires, aux deux bouts) → reprendre les deux bouts au code couleur T568B."),
            _c(f"Lien {TEN_G_PORT} et suite", 2, f"10GBASE-T sur Cat6 à {TEN_G_LENGTH_M} m : {TEN_G_VERDICT.lower()} (Cat6 limité à 55 m à 10 Gb/s) ; le lien reste bon pour 1 Gb/s ; pour 10 Gb/s, tirer du Cat6A (ou une fibre) ; informer le client. Après chaque reprise : retester, joindre le nouveau rapport, étiquettes vérifiées."),
        ),
        correction=(
            f"Le testeur du lien {CERT_PORT_FIGURE} montre {_links(CERT_FIGURE_LINKS)}, les broches 4, 5, 7 et 8 étant droites : les paires orange et verte sont croisées. Le lien est donc câblé en croisé : T568B au panneau, T568A à la prise. Le chantier étant entièrement en T568B, la prise murale a été poinçonnée en suivant le code A imprimé sur le connecteur. Je reprends la prise en T568B et je reteste.",
            f"Pour {LONG_PORT}, le lien permanent mesure {LONG_PERMANENT_M} m, plus que les 90 m admis, et le canal avec 5 m de cordons atteint {LONG_PERMANENT_M + LONG_CORDS_M} m, plus que 100 m. Raccourcir les cordons ne suffit pas : il faut un chemin plus court, déplacer la prise, ou rapprocher l'équipement actif (switch d'étage) ou passer en fibre ; puis retester.",
            f"{OPEN_PORT} : circuit ouvert sur la broche 7, le fil blanc/marron n'arrive pas : fil mal poinçonné ou coupé à la prise ou au panneau ; je contrôle les deux bouts, je repoinçonne et je reteste. {SPLIT_PORT} : la continuité est parfaite mais la diaphonie échoue sur 3-6 et 4-5 : ce sont des paires séparées, les fils ayant été rangés dans l'ordre sans respecter les paires aux deux bouts ; je reprends les deux bouts au code T568B.",
            f"{TEN_G_PORT} : 10 Gb/s en Cat6 sur {TEN_G_LENGTH_M} m dépasse les 55 m tolérés : {TEN_G_VERDICT.lower()}. Le lien convient pour 1 Gb/s ; pour 10 Gb/s, je propose de tirer un câble Cat6A (ou une fibre). Après chaque reprise, je reteste le lien, je joins le nouveau rapport au dossier remis au client et je vérifie les étiquettes.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Contrôler un relevé de pose et rédiger la réalisation d'un cordon",
        question_type="document_analysis",
        requirement_ids=("AP-18", "AP-20", "AP-34"),
        kind=KIND_DOC,
        context=(
            "Dossier A. Pendant le chantier de l'imprimerie Lambert (document A1), le chef d'équipe te remet son "
            "relevé de pose (document A5). Ensuite, tu dois former un apprenti à la fabrication des cordons de "
            "brassage de 3 m pour la baie."
        ),
        documents=(_A_REQUEST, _A_RUNS),
        instructions=(
            ("Pour chaque tronçon T1 à T5, calcule le rayon de courbure minimal, puis conclus : conforme ou non, "
             "avec la règle utilisée (courbure, traction, séparation des câbles électriques)."),
            "Pour chaque tronçon non conforme, indique la correction.",
            ("Rédige, dans l'ordre, la procédure de fabrication d'un cordon droit T568B de 3 m pour l'apprenti : "
             "matériel, préparation du câble, rangement des fils, sertissage, contrôles et test."),
        ),
        criteria=(
            _c("Verdicts des cinq tronçons", 4, f"Rayon minimal : 4 × Ø non écranté, 8 × Ø écranté, 10 × Ø coaxial sans fiche ; traction ≤ 110 N ; séparation selon la classe (a 300, b 100, c 50, d 10 mm) sauf cloison métallique. T1 : minimum {_min_radius('T1')}, 15 mm → {_run_verdict('T1')} ; T2 : minimum {_min_radius('T2')}, 160 N → {_run_verdict('T2')} ; T3 : 40 mm < 100 mm (classe b, sans cloison) → {_run_verdict('T3')} ; T4 : minimum {_min_radius('T4')}, 40 mm → {_run_verdict('T4')} ; T5 : {_run_verdict('T5')} (cloison métallique). 0,8 point par tronçon."),
            _c("Corrections", 2, "T1 et T4 : reprendre les angles (coudes de goulotte, boucle plus large), contrôler le câble et retester (remplacer si abîmé) ; T2 : câble tiré trop fort, peut être abîmé → tester, remplacer si le test échoue, tirer à la main ou avec un tire-câble limité ; T3 : écarter à 100 mm au moins des câbles d'énergie ou poser une cloison métallique."),
            _c("Procédure du cordon", 4, "Câble multibrin (souple) Cat6A ou Cat5e selon le lien, fiches adaptées, manchons enfilés ; couper droit, retirer 25 à 30 mm de gaine sans entailler ; détorsader le minimum (≤ 13 mm), ranger en T568B (blanc/orange, orange, blanc/vert, bleu, blanc/bleu, vert, blanc/marron, marron) ; recouper droit à 12-13 mm ; insérer contacts vers soi, broche 1 à gauche, fils en butée, gaine sous la patte ; vérifier l'ordre ; sertir ; même chose à l'autre bout (T568B) ; tester au wiremap, étiqueter."),
        ),
        correction=(
            f"Règles : rayon de courbure d'au moins 4 fois le diamètre pour un câble non écranté, 8 fois s'il est écranté, 10 fois pour un coaxial sans fiche du fabricant ; traction de 110 N au plus ; distance aux câbles électriques selon la classe de séparation (b : 100 mm, c : 50 mm) sauf cloison métallique. T1 : minimum {_min_radius('T1')}, relevé 15 mm → {_run_verdict('T1')}. T2 : minimum {_min_radius('T2')}, 70 mm convient, mais 160 N → {_run_verdict('T2')}. T3 : courbure correcte (minimum {_min_radius('T3')}), mais 40 mm des câbles d'énergie en classe b → {_run_verdict('T3')}. T4 : coaxial, minimum {_min_radius('T4')}, relevé 40 mm → {_run_verdict('T4')}. T5 : 30 mm ≥ {_min_radius('T5')}, 100 N, cloison métallique → {_run_verdict('T5')}.",
            "Corrections : T1 et T4, reprendre les angles avec un rayon suffisant puis tester le câble (le remplacer s'il est abîmé) ; T2, le câble a peut-être été déformé au tirage : le tester et le remplacer en cas d'échec, puis tirer sans dépasser 110 N ; T3, l'écarter à 100 mm au moins des câbles d'énergie ou poser une cloison métallique.",
            "Cordon droit T568B de 3 m : câble multibrin souple de la catégorie du lien, fiches prévues pour du multibrin, manchons enfilés d'abord. Couper droit ; retirer 25 à 30 mm de gaine sans entailler les fils ; détorsader le moins possible et ranger en T568B (blanc/orange, orange, blanc/vert, bleu, blanc/bleu, vert, blanc/marron, marron) ; recouper droit à 12-13 mm. Insérer, contacts vers soi et broche 1 à gauche, les huit fils jusqu'en butée, la gaine sous la patte ; vérifier l'ordre à travers la fiche ; sertir à fond. Faire l'autre bout de la même façon, en T568B. Tester au wiremap (1→1 … 8→8), étiqueter.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier B
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Diagnostiquer et corriger un bus coaxial 10BASE2",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-18", "AP-20"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Au musée de l'informatique « Octet » (document B1), le segment 10BASE2 de la salle rétro "
            "ne fonctionne pas. Le bénévole a fait le relevé du document B2 avant ton arrivée."
        ),
        documents=(_B_REQUEST, _B_BUS),
        instructions=(
            "Relève toutes les non-conformités du segment (document B2) et justifie chacune par la règle du 10BASE2.",
            ("Explique le rôle des deux terminateurs et pourquoi tout doit être en 50 Ω ; calcule la part de "
             "l'amplitude renvoyée par un terminateur de 75 Ω sur ce câble."),
            "Rédige l'intervention de remise en conformité, dans l'ordre, jusqu'à la vérification.",
        ),
        criteria=(
            _c("Non-conformités", 4, "1 point chacune : " + " ".join(MUSEUM_ERRORS) + " Mise à la terre en un seul point : conforme. Longueur et nombre de stations : conformes."),
            _c("Terminateurs et impédance", 3, f"Le bus est une ligne de transmission 50 Ω (RG-58) ; à chaque bout, un terminateur 50 Ω absorbe le signal : sans lui ou avec une autre valeur, le signal se réfléchit et brouille les trames (collisions, plus aucune communication). Coefficient de réflexion Γ = (75 − 50) / (75 + 50) = {fr(WRONG_TERMINATOR_GAMMA)} : {fr(WRONG_TERMINATOR_GAMMA * 100, 0)} % de l'amplitude renvoyée. Le RG-59 (75 Ω) et son terminateur viennent du kit de vidéosurveillance."),
            _c("Intervention ordonnée", 3, "Prévenir et arrêter le réseau ; remplacer le terminateur 75 Ω par un 50 Ω ; remplacer le tronçon RG-59 par du RG-58 ; supprimer le cordon du Poste 3 (T directement sur la carte) ; allonger le tronçon de 0,3 m à 0,5 m au moins ; contrôler les BNC ; mesure à l'ohmmètre au T d'une station : environ 25 Ω ; redémarrer et tester (échange entre postes) ; consigner."),
        ),
        correction=(
            "Non-conformités : " + " ".join(MUSEUM_ERRORS) + " La terre en un seul point, la longueur totale (22,3 m) et le nombre de stations (5) sont conformes.",
            f"Le 10BASE2 est une ligne de transmission d'impédance 50 Ω : câble RG-58, T et terminateurs 50 Ω. Le terminateur de chaque extrémité absorbe le signal qui arrive au bout ; sans lui, ou s'il n'a pas la même impédance, une partie du signal repart en sens inverse et se superpose aux trames : collisions, plus aucune communication. Ici Γ = (75 − 50) / (75 + 50) = {fr(WRONG_TERMINATOR_GAMMA)} : {fr(WRONG_TERMINATOR_GAMMA * 100, 0)} % de l'amplitude est renvoyée. Le tronçon RG-59 (75 Ω) crée aussi des réflexions à chaque changement d'impédance.",
            "Intervention : prévenir le musée et arrêter le réseau ; remplacer le terminateur 75 Ω du Serveur par un 50 Ω ; remplacer le tronçon RG-59 par du RG-58 de même longueur ; visser le T directement sur la carte du Poste 3 (sans cordon) ; remplacer le tronçon de 0,3 m par un tronçon de 0,5 m au moins ; contrôler visuellement les BNC ; mesurer à l'ohmmètre entre âme et blindage au T d'une station : environ 25 Ω (deux 50 Ω en parallèle) ; remettre en route et tester les échanges entre postes ; noter l'intervention.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Interpréter l'ohmmètre, réaliser un câble BNC, distinguer 10BASE5",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-19", "AP-20"),
        kind=KIND_DOC,
        context=(
            "Dossier B. Le musée « Octet » (document B1) te transmet les mesures faites cette semaine sur le "
            "segment de la salle 2 (document B3). Il te demande aussi une fiche de fabrication des câbles BNC pour "
            "les bénévoles, et des explications sur le segment 10BASE5 qu'il veut exposer."
        ),
        documents=(_B_REQUEST, _B_OHM),
        instructions=(
            "Interprète chaque lecture du document B3 : ce qu'elle signifie et ce que tu vérifies ou répares.",
            ("Rédige pour les bénévoles la procédure de réalisation d'un câble RG-58 avec deux BNC à sertir, dans "
             "l'ordre, avec les contrôles."),
            ("Compare 10BASE2 et 10BASE5 : câble, longueur d'un segment, nombre de stations, raccordement des "
             "stations, terminaisons, débit."),
        ),
        criteria=(
            _c("Trois lectures", 3, f"Lundi {_OHM['Lundi']} : normal, deux terminateurs 50 Ω en parallèle. Mercredi {_OHM['Mercredi']} : un seul terminateur vu → terminateur manquant ou desserré (visite) ou coupure ; vérifier les deux extrémités, remettre un 50 Ω, remesurer 25 Ω. Vendredi {_OHM['Vendredi']} : court-circuit âme/blindage ; le BNC refait est suspect (brin de tresse vers l'âme) → débrancher ce câble, mesurer, refaire le BNC, remesurer."),
            _c("Procédure BNC", 4, "Vérifier câble RG-58 et BNC prévus pour lui (50 Ω), notice ; enfiler manchon puis bague ; dénuder au dénudeur coaxial aux cotes de la notice, sans entailler âme ni tresse ; âme dans le contact central, sertir ; pousser le corps, tresse sur le fût, aucun brin vers l'âme ; sertir la bague avec la bonne matrice, manchon ; contrôle visuel et traction ; continuité âme-âme et blindage-blindage, pas de court-circuit âme/blindage (infini à vide) ; puis l'autre bout."),
            _c("10BASE2 et 10BASE5", 3, "Les deux : 10 Mb/s, bus coaxial 50 Ω, half-duplex, terminateur 50 Ω à chaque bout, terre en un point. 10BASE2 : coaxial fin RG-58, 185 m, 30 stations, T BNC sur la carte, 0,5 m entre T. 10BASE5 : coaxial épais (≈ 10 mm), 500 m, 100 transceivers, prises vampires sur les repères tous les 2,5 m, transceiver relié à la carte par un câble AUI (≤ 50 m), terminateurs sur connecteurs N."),
        ),
        correction=(
            f"Lundi, {_OHM['Lundi']} : c'est normal, on voit les deux terminateurs de 50 Ω en parallèle. Mercredi, {_OHM['Mercredi']} : on ne voit plus qu'un terminateur ; après la visite, un terminateur a probablement été retiré ou desserré (sinon le câble est coupé). Je vérifie les deux extrémités, je remets un terminateur 50 Ω et je remesure 25 Ω. Vendredi, {_OHM['Vendredi']} : court-circuit entre âme et blindage ; le BNC que l'on vient de refaire est le premier suspect (brin de tresse qui touche l'âme). Je débranche ce câble, je le mesure seul, je refais le connecteur et je remesure le segment.",
            "Procédure : vérifier que le câble est du RG-58 et que les BNC, la bague et la matrice sont prévus pour lui (50 Ω), lire la notice ; enfiler le manchon puis la bague ; dénuder au dénudeur coaxial aux cotes de la notice sans entailler l'âme ni la tresse ; engager l'âme dans le contact central et le sertir ; pousser le corps : contact enclenché, tresse sur le fût, aucun brin vers l'âme ; ramener la bague sur la tresse, sertir, puis le manchon. Contrôler : aspect, traction ferme ; à l'ohmmètre, continuité de l'âme et du blindage d'un bout à l'autre et aucune liaison entre âme et blindage. Faire l'autre bout de la même façon.",
            "Les deux sont des bus coaxiaux 50 Ω à 10 Mb/s, half-duplex, avec un terminateur 50 Ω à chaque bout et une seule mise à la terre. 10BASE2 : coaxial fin RG-58, segment de 185 m, 30 stations, T BNC vissé sur la carte, 0,5 m au moins entre deux T. 10BASE5 : coaxial épais d'environ 10 mm, segment de 500 m, 100 transceivers, prises vampires posées sur les repères tous les 2,5 m, transceiver relié à la carte par un câble AUI de 50 m au plus, terminateurs sur connecteurs N.",
        ),
    ),
    # ------------------------------------------------------------------ Dossier C
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Choisir la fibre, les modules et les jarretières de trois liaisons",
        question_type="document_analysis",
        requirement_ids=("AP-21", "AP-22", "AP-19"),
        kind=KIND_DOC,
        context=(
            "Dossier C. La brasserie Van Daele modernise son réseau (document C1). Tu dois choisir le support et les "
            "articles du catalogue (document C2) pour les liaisons L1 et L2, et répondre à la question de la "
            "gérante sur la liaison existante L3."
        ),
        documents=(_C_REQUEST, _C_CATALOGUE),
        instructions=(
            ("Pour L1, choisis le type de fibre, les modules et la jarretière dans le catalogue ; explique pourquoi "
             "ni le cuivre ni la fibre OM4 ne conviennent."),
            "Pour L2, propose la solution la plus simple qui tient le débit et la distance.",
            "Pour L3, dis si 10 Gb/s est possible sur la fibre existante et ce que tu proposes à la gérante.",
            "Compare fibre et paire torsadée en quatre points pour justifier tes choix auprès de la gérante.",
        ),
        criteria=(
            _c("Liaison L1", 4, f"{L1_CHOICE} : 10GBASE-LR aux deux bouts, câble OS2 jaune, jarretières OS2 LC/UPC duplex (bleues). Cuivre exclu : {FIBRE_L1_M} m > 100 m et liaison entre deux bâtiments (terres différentes, foudre). OM4 exclue : 10GBASE-SR porte 400 m au plus sur OM4 ({L1_OM4_VERDICT.lower()}). Pas de jarretière SC/APC : un APC face à un UPC ne se raccorde pas (forte perte, faces abîmées) et les modules sont en LC."),
            _c("Liaison L2", 1, f"{L2_CHOICE} : 70 m ≤ 100 m dans le même bâtiment ; câble Cat6A, cuivre suffisant et moins cher."),
            _c("Liaison L3", 3, f"OM2 de {HALL_M} m : 1000BASE-SX porte 550 m → {HALL_1G_VERDICT.lower()} ; 10GBASE-SR ne porte que 82 m sur OM2 → {HALL_10G_VERDICT.lower()}. 10 Gb/s impossible sans travaux : garder 1 Gb/s, ou tirer une nouvelle fibre (OM3 300 m, OM4 400 m ou OS2) dans le fourreau existant."),
            _c("Comparaison", 2, "Fibre : insensible aux parasites, isolation électrique entre bâtiments, longues distances (centaines de m à km), débits élevés ; mais modules, outillage et mesure plus chers, connecteurs à nettoyer, fragile en courbure, pas de PoE. Cuivre : simple et bon marché, PoE, mais 100 m, sensible aux parasites, à éviter entre bâtiments."),
        ),
        correction=(
            f"L1 : {L1_CHOICE}. Le cuivre est exclu : {FIBRE_L1_M} m dépassent les 100 m d'un canal, et un câble en cuivre entre deux bâtiments relie des terres différentes (courants de terre, foudre). La fibre OM4 ne convient pas non plus : un module 10GBASE-SR ne porte que 400 m sur OM4 ({L1_OM4_VERDICT.lower()}). Je commande le câble OS2 8 fibres (gaine jaune), deux modules SFP+ 10GBASE-LR et des jarretières OS2 LC/UPC duplex. Pas de jarretière SC/APC : les modules sont en LC, et un connecteur APC (vert) ne se raccorde pas à un UPC (bleu).",
            f"L2 : {L2_CHOICE}. 70 m dans le même bâtiment restent sous les 100 m d'un canal : un câble Cat6A et des ports 10GBASE-T suffisent, c'est plus simple et moins cher que la fibre.",
            f"L3 : la fibre OM2 de {HALL_M} m accepte le 1000BASE-SX (550 m au plus) : {HALL_1G_VERDICT.lower()}. Mais le 10GBASE-SR ne porte que 82 m sur OM2 : {HALL_10G_VERDICT.lower()}. On ne passe donc pas à 10 Gb/s sans travaux : soit on garde 1 Gb/s, soit on tire une nouvelle fibre (OM3 jusqu'à 300 m, OM4 jusqu'à 400 m, ou OS2) dans le fourreau existant.",
            "Comparaison pour la gérante : la fibre transporte de la lumière, elle est insensible aux parasites électriques et isole électriquement les bâtiments ; elle porte des débits élevés sur des centaines de mètres (multimode) à des kilomètres (monomode). En revanche, modules, outillage et mesures coûtent plus cher, les connecteurs doivent rester propres et elle craint les courbures ; elle ne transporte pas l'alimentation PoE. Le cuivre est simple, bon marché et accepte le PoE, mais il est limité à 100 m et sensible aux parasites.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Calculer le bilan d'une liaison et réceptionner la fibre au photomètre",
        question_type="document_analysis",
        requirement_ids=("AP-21", "AP-19", "AP-22"),
        kind=KIND_DOC,
        context=(
            f"Dossier C. La liaison L1 de la brasserie Van Daele vient d'être posée en fibre OS2 sur {FIBRE_L1_M} m "
            "(document C1). Tu fais sa réception avec les relevés de l'installateur (document C3) avant de mettre "
            "les modules 10GBASE-LR en service."
        ),
        documents=(_C_REQUEST, _C_RECEPTION),
        instructions=(
            ("Calcule la perte maximale admissible de la liaison à 1 310 nm (atténuation de la fibre, connecteurs, "
             "épissures), en détaillant chaque terme."),
            "Calcule la perte mesurée de chaque fibre au photomètre et conclus pour chacune.",
            "Pour la fibre non conforme, rédige ce que tu fais, dans l'ordre, avant de conclure à un défaut du câble.",
            ("Estime la puissance que recevra le module, compare-la à sa fiche et donne la marge ; termine par la "
             "précaution de sécurité à respecter pendant ces mesures."),
        ),
        criteria=(
            _c("Perte maximale", 3, f"Atténuation de la fibre : {fr(FIBRE_L1_M / 1000, 2)} km × {fr(L1_DB_PER_KM, 1)} dB/km = {fr(FIBRE_L1_M / 1000 * L1_DB_PER_KM, 3)} dB ; connecteurs : {L1_CONNECTORS} × 0,75 = {fr(L1_CONNECTORS * 0.75, 2)} dB ; épissures : {L1_SPLICES} × 0,3 = {fr(L1_SPLICES * 0.3, 1)} dB ; total ≈ {fr(L1_MAX_LOSS, 2)} dB."),
            _c("Photométrie", 2, f"Perte = référence − lecture. {_F1} : {dbm_fr(PHOTO_REFERENCE_DBM)} − ({dbm_fr(PHOTO_READINGS[0][1])}) = {fr(PHOTO_LOSSES[_F1], 2)} dB → {PHOTO_VERDICTS[_F1].lower()} ; {_F2} : {fr(PHOTO_LOSSES[_F2], 2)} dB > {fr(L1_MAX_LOSS, 2)} dB → {PHOTO_VERDICTS[_F2].lower()}."),
            _c("Fibre 2 : démarche", 3, "Inspecter à la sonde les connecteurs des deux tiroirs et le cordon de référence, nettoyer à sec, réinspecter (alcool isopropylique si besoin, remplacer si rayé), capuchons ; vérifier la référence ; remesurer ; si la perte reste trop forte : réflectomètre pour localiser (épissure, courbure, connecteur), reprise par l'installateur, nouvelle mesure ; ne pas réceptionner avant."),
            _c("Puissance reçue et sécurité", 2, f"Reçu ≈ {dbm_fr(L1_TX_DBM)} − {fr(L1_MAX_LOSS, 2)} = {dbm_fr(L1_RX_EXPECTED)} dBm, entre {dbm_fr(LR_SPEC.sensitivity_dbm)} et {dbm_fr(LR_SPEC.overload_dbm)} dBm : {L1_RX_STATUS.lower()} ; marge ≈ {fr(L1_RX_MARGIN, 1)} dB au-dessus de la sensibilité. Lumière infrarouge invisible : ne jamais regarder un connecteur ou un module, même éteint en apparence ; source coupée avant inspection, contrôle au photomètre, capuchons."),
        ),
        correction=(
            f"Perte maximale à {L1_WAVELENGTH} nm : fibre {fr(FIBRE_L1_M / 1000, 2)} km × {fr(L1_DB_PER_KM, 1)} dB/km = {fr(FIBRE_L1_M / 1000 * L1_DB_PER_KM, 3)} dB ; {L1_CONNECTORS} paires de connecteurs × 0,75 dB = {fr(L1_CONNECTORS * 0.75, 2)} dB ; {L1_SPLICES} épissures × 0,3 dB = {fr(L1_SPLICES * 0.3, 1)} dB. Total : {fr(L1_MAX_LOSS, 2)} dB.",
            f"La perte se calcule en retranchant la lecture de la référence. {_F1} : {fr(PHOTO_LOSSES[_F1], 2)} dB, sous {fr(L1_MAX_LOSS, 2)} dB → {PHOTO_VERDICTS[_F1].lower()}. {_F2} : {fr(PHOTO_LOSSES[_F2], 2)} dB, au-dessus → {PHOTO_VERDICTS[_F2].lower()}.",
            "Pour la fibre 2 : couper la source, inspecter à la sonde les connecteurs des deux tiroirs et le cordon de référence ; nettoyer à sec, réinspecter (alcool isopropylique si la saleté résiste, remplacement si la face est rayée) ; vérifier la référence et remesurer. Si la perte reste trop élevée, faire passer le réflectomètre pour localiser le défaut (épissure ratée, courbure serrée dans un tiroir, connecteur abîmé), faire reprendre par l'installateur, remesurer ; la liaison n'est réceptionnée qu'avec deux fibres conformes.",
            f"Le module émet {dbm_fr(L1_TX_DBM)} dBm ; après {fr(L1_MAX_LOSS, 2)} dB de perte, il reçoit environ {dbm_fr(L1_RX_EXPECTED)} dBm, dans la plage de la fiche ({dbm_fr(LR_SPEC.sensitivity_dbm)} à {dbm_fr(LR_SPEC.overload_dbm)} dBm) : {L1_RX_STATUS.lower()}, avec une marge d'environ {fr(L1_RX_MARGIN, 1)} dB. Sécurité : la lumière de 1 310 nm est infrarouge, donc invisible ; on ne regarde jamais l'extrémité d'une fibre ni un module ; on coupe la source avant d'inspecter, on vérifie l'absence de lumière au photomètre et on remet les capuchons.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Diagnostiquer une liaison optique coupée et rédiger la réparation",
        question_type="document_analysis",
        requirement_ids=("AP-21", "AP-22", "AP-20"),
        kind=KIND_DOC,
        context=(
            f"Dossier C. Six mois après sa mise en service, la liaison L1 de la brasserie Van Daele (OS2, {FIBRE_L1_M} m, "
            "document C1) ne fonctionne plus, le lendemain de travaux de terrassement dans la cour. Un collègue "
            "propose d'« inverser les deux fibres à un bout ». Tu relèves l'état des ports (document C4) puis tu "
            "fais passer le réflectomètre sur la fibre 2 depuis le tiroir BUREAUX (document C5)."
        ),
        documents=(_C_REQUEST, _C_OUTAGE, _C_OTDR),
        instructions=(
            "Interprète le document C4 : quelle fibre est en cause ? Réponds au collègue sur la polarité et dis pourquoi les modules ne sont pas en cause.",
            ("Interprète chaque événement de la trace (document C5) et calcule la position du défaut dans la liaison, "
             "depuis le tiroir BUREAUX."),
            ("Rédige la réparation dans l'ordre, avec les règles de pose d'un câble optique de "
             f"{REPAIR_CABLE_DIAMETER_MM} mm de diamètre, jusqu'aux mesures de contrôle et leur seuil d'acceptation."),
        ),
        criteria=(
            _c("Lecture des ports", 3, "L'entrepôt reçoit normalement (−4,4 dBm) la lumière émise par les bureaux : fibre 1 intacte. Les bureaux ne reçoivent rien (LOS) : la fibre 2, de l'entrepôt vers les bureaux, est coupée. Pas un problème de polarité : la liaison a fonctionné six mois, et une polarité inversée donnerait LOS des deux côtés ; inverser les fibres couperait aussi la fibre 1. Modules reconnus, puissance émise normale, l'entrepôt reçoit : ils fonctionnent."),
            _c("Trace et position", 4, f"1 : {_LAUNCH:g} m, pic de réflexion → connecteur du tiroir BUREAUX (début de la liaison, après la bobine amorce). 2 : {_BEND_AT:g} m, sans pic, 0,8 dB à 1 550 nm contre 0,12 dB à 1 310 nm → courbure trop serrée, à {fr(OUTAGE_BEND_M, 0)} m du tiroir. 3 : {_END_AT:g} m, la trace retombe dans le bruit → cassure (fin de fibre) ; position dans la liaison : {_END_AT:g} − {_LAUNCH:g} = {fr(OUTAGE_BREAK_M, 0)} m depuis le tiroir BUREAUX, alors que la liaison mesure {FIBRE_L1_M} m : câble écrasé et cassé dans la zone des travaux."),
            _c("Réparation et contrôle", 3, f"Couper la lumière, ne jamais regarder une fibre ; repérer la zone sur le plan du fourreau (≈ {fr(OUTAGE_BREAK_M, 0)} m) ; ouvrir, remplacer le tronçon écrasé et le raccorder par épissures (et libérer la courbure vers {fr(OUTAGE_BEND_M, 0)} m) par fusion dans un boîtier étanche (ou tirer un câble neuf de tiroir à tiroir) ; rayon ≥ {fr(REPAIR_BEND_REST_MM, 0)} mm au repos et {fr(REPAIR_BEND_PULL_MM, 0)} mm au tirage (10 et 20 × le diamètre), tirer par l'aramide, love de réserve, grillage avertisseur, étiquettes ; nettoyer, inspecter, mesurer les deux fibres au photomètre : ≤ {fr(REPAIRED_MAX_LOSS, 2)} dB avec deux épissures de plus ; nouvelle trace, rapport et plan mis à jour."),
        ),
        correction=(
            "Document C4 : l'entrepôt reçoit −4,4 dBm, une valeur normale : la fibre qui va des bureaux vers l'entrepôt (fibre 1) est intacte. Les bureaux ne reçoivent plus rien (LOS) : la fibre qui va de l'entrepôt vers les bureaux (fibre 2) est interrompue. Ce n'est pas la polarité : la liaison a fonctionné six mois sans qu'on y touche, et une polarité inversée donnerait LOS des deux côtés ; inverser les fibres ferait perdre aussi la fibre 1. Les modules sont reconnus, émettent normalement et celui de l'entrepôt reçoit : ils ne sont pas en cause.",
            f"Trace : l'événement 1 ({_LAUNCH:g} m, pic de réflexion, 0,4 dB) est le connecteur du tiroir BUREAUX, au bout de la bobine amorce : c'est le début de la liaison. L'événement 2 ({_BEND_AT:g} m, sans pic) perd 0,8 dB à 1 550 nm mais 0,12 dB à 1 310 nm : une perte nettement plus forte à 1 550 nm signe une courbure trop serrée, à {_BEND_AT:g} − {_LAUNCH:g} = {fr(OUTAGE_BEND_M, 0)} m du tiroir. L'événement 3 ({_END_AT:g} m) est suivi de bruit : c'est la fin de la fibre, une cassure, à {_END_AT:g} − {_LAUNCH:g} = {fr(OUTAGE_BREAK_M, 0)} m du tiroir BUREAUX, bien avant les {FIBRE_L1_M} m de la liaison. Le câble a été écrasé et cassé dans la zone des travaux.",
            f"Réparation : couper la lumière et ne jamais regarder une fibre ; reporter les {fr(OUTAGE_BREAK_M, 0)} m sur le plan du fourreau pour situer la zone ; ouvrir, dégager le câble (y compris la courbure vers {fr(OUTAGE_BEND_M, 0)} m) et remplacer le tronçon écrasé, raccordé par deux épissures par fusion dans un boîtier étanche (ou tirer un câble neuf entre les deux tiroirs). Pour un câble de {REPAIR_CABLE_DIAMETER_MM} mm, rayon de courbure de {fr(REPAIR_BEND_REST_MM, 0)} mm au moins au repos et {fr(REPAIR_BEND_PULL_MM, 0)} mm pendant le tirage, traction par l'élément aramide, love de réserve, grillage avertisseur, étiquettes. Contrôle : nettoyer, inspecter, mesurer les deux fibres au photomètre, la perte ne devant pas dépasser {fr(REPAIRED_MAX_LOSS, 2)} dB (deux épissures de plus) ; nouvelle trace au réflectomètre, remise en service, rapport et plan mis à jour.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = EXAM_ITEMS
PRACTICE_ITEMS: tuple[PR06Item, ...] = ()

# Partie ou dossier de chaque question, dans l'ordre du sujet.
ITEM_PARTS: dict[str, str] = {
    "X01": PART_1, "X02": PART_1,
    "X03": DOSSIER_A, "X04": DOSSIER_A, "X05": DOSSIER_A,
    "X06": DOSSIER_B, "X07": DOSSIER_B,
    "X08": DOSSIER_C, "X09": DOSSIER_C, "X10": DOSSIER_C,
}
# Cours où revoir la matière de chaque question.
ITEM_COURSES: dict[str, tuple[str, ...]] = {
    "X01": ("PR15",),
    "X02": ("PR15", "PR14"),
    "X03": ("PR13", "PR14"),
    "X04": ("PR15", "PR13", "PR14"),
    "X05": ("PR13", "PR15"),
    "X06": ("PR16",),
    "X07": ("PR16", "PR14"),
    "X08": ("PR17", "PR14"),
    "X09": ("PR17", "PR14"),
    "X10": ("PR17",),
}
DOSSIER_DOCUMENTS: dict[str, tuple[ExerciseDocument, ...]] = {
    DOSSIER_A: (_A_REQUEST, _A_NEEDS, _A_CERT, _A_TESTER, _A_RUNS),
    DOSSIER_B: (_B_REQUEST, _B_BUS, _B_OHM),
    DOSSIER_C: (_C_REQUEST, _C_CATALOGUE, _C_RECEPTION, _C_OUTAGE, _C_OTDR),
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
