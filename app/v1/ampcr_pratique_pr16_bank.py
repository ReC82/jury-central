"""PR16 « Câble coaxial et BNC — impédance, fabrication et diagnostic écrit » — exercices corrigés
et mini-examen (ticket #198).

Même organisation que PR06, PR11 et PR15 (`app.v1.ampcr_pratique_pr06_bank`, dont ce module
réutilise le type d'item et la règle d'acceptation) :
- `PRACTICE_ITEMS` : 16 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — au moins 5 interprétations ou corrections de schémas, 4 choix
  d'impédance et de connecteurs, 3 procédures de fabrication écrites et 3 diagnostics
  d'installation ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Non-conformités de bus, lectures d'ohmmètre et distances de réflectomètre : **calculées** depuis
le modèle de `app.v1.ampcr_pratique_pr16_figures` (testé) ; situations et relevés : fictifs.
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, ScoringCriterion, validate_exercise
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    Ordering,
    PR06Item,
)
from app.v1.ampcr_pratique_pr16_figures import (
    ATTACH_STUB,
    ATTACH_T,
    BUS_CUT,
    BUS_MISSING_TERMINATOR,
    BUS_OK,
    BUS_SHORT,
    CRIMP_STEPS,
    GOOD_TERMINATOR,
    GROUNDED_TERMINATOR,
    Bus,
    BusEnd,
    Station,
    _stations_bus,
    bus_errors,
    fr,
    ohmmeter_reading,
    tdr_distance_m,
)

PR16_CODE = "PR16"

KIND_SCHEMA = "interprétation et correction de schéma"
KIND_CHOICE = "choix d'impédance et de connecteurs"
KIND_PROCEDURE = "procédure de fabrication écrite"
KIND_DIAGNOSIS = "diagnostic d'installation"
KIND_SCENARIO = "scénario"


def _c(label: str, points: float, expected: str) -> ScoringCriterion:
    return ScoringCriterion(label=label, points=points, expected=expected)


def _table(title: str, header: tuple[str, ...], *rows: tuple[str, ...]) -> ExerciseDocument:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return ExerciseDocument(title=title, kind="tableau", content_text="\n".join(lines))


def _end_text(end: BusEnd) -> str:
    if end.terminator_ohm is None:
        text = "rien (sortie du T libre)"
    else:
        text = f"terminateur {end.terminator_ohm} Ω"
    return text + (", relié à la terre" if end.grounded else "")


def bus_table(title: str, bus: Bus) -> ExerciseDocument:
    """Relevé d'un segment, de l'extrémité 1 à l'extrémité 2, une ligne par élément."""
    rows: list[tuple[str, str, str]] = [("Extrémité 1", "Sur le T du premier poste", _end_text(bus.first))]
    for item in bus.items:
        if isinstance(item, Station):
            rows.append(("Poste", item.name, "T BNC branché directement sur la carte" if item.attachment == ATTACH_T
                         else "T relié à la carte par un câble coaxial de 2 m"))
        else:
            detail = f"{item.cable}, {fr(item.length_m)} m"
            rows.append(("Câble", detail, item.fault or "—"))
    rows.append(("Extrémité 2", "Sur le T du dernier poste", _end_text(bus.last)))
    return _table(title, ("Élément", "Repère", "Relevé"), *rows)


# --- Données calculées des exercices --------------------------------------------------------

E01_BUS = _stations_bus(
    ("Accueil", "Compta", "Direction", "Serveur"), (9, 14, 6),
    first=GROUNDED_TERMINATOR, last=BusEnd(None), attachments={"Direction": ATTACH_STUB},
)
E01_ERRORS = bus_errors(E01_BUS)

# E02 : segments décrits en une ligne → conforme / non conforme (calculé par `bus_errors`).
E02_CASES: tuple[tuple[str, Bus], ...] = (
    ("5 postes, 60 m de RG-58, T sur chaque carte, terminateur 50 Ω à chaque bout, une terre", _stations_bus(
        ("P1", "P2", "P3", "P4", "P5"), (15, 15, 15, 15), first=GROUNDED_TERMINATOR, last=GOOD_TERMINATOR)),
    ("4 postes, 40 m de RG-58, terminateur 50 Ω à un seul bout", _stations_bus(
        ("P1", "P2", "P3", "P4"), (10, 15, 15), first=GOOD_TERMINATOR, last=BusEnd(None))),
    ("3 postes, 30 m dont 10 m de RG-59, terminateurs 50 Ω", _stations_bus(
        ("P1", "P2", "P3"), (20, 10), first=GOOD_TERMINATOR, last=GOOD_TERMINATOR, cables={1: "RG-59"})),
    ("6 postes, 190 m de RG-58 au total, terminateurs 50 Ω", _stations_bus(
        ("P1", "P2", "P3", "P4", "P5", "P6"), (40, 40, 40, 40, 30), first=GOOD_TERMINATOR, last=GOOD_TERMINATOR)),
    ("4 postes, 45 m de RG-58, terminateurs 50 Ω, un poste relié à son T par 3 m de câble", _stations_bus(
        ("P1", "P2", "P3", "P4"), (15, 15, 15), first=GOOD_TERMINATOR, last=GOOD_TERMINATOR, attachments={"P3": ATTACH_STUB})),
    ("2 postes, 0,3 m de RG-58 entre les deux T, terminateurs 50 Ω", _stations_bus(
        ("P1", "P2"), (0.3,), first=GOOD_TERMINATOR, last=GOOD_TERMINATOR)),
    ("3 postes, 180 m de RG-58, terminateurs 50 Ω, une terre", _stations_bus(
        ("P1", "P2", "P3"), (90, 90), first=GROUNDED_TERMINATOR, last=GOOD_TERMINATOR)),
    ("4 postes, 50 m de RG-58, terminateurs 50 Ω reliés tous deux à la terre", _stations_bus(
        ("P1", "P2", "P3", "P4"), (20, 15, 15), first=GROUNDED_TERMINATOR, last=BusEnd(50, grounded=True))),
)
E02_CATEGORIES = ("Conforme 10BASE2", "Non conforme")
E02_CORRECT: tuple[int, ...] = tuple(0 if not bus_errors(bus) else 1 for _label, bus in E02_CASES)

E04_BUS = _stations_bus(
    ("Labo-1", "Labo-2", "Labo-3"), (10, 6),
    first=BusEnd(75, grounded=True), last=GOOD_TERMINATOR, cables={0: "RG-59"},
)
E04_ERRORS = bus_errors(E04_BUS)

# E05 : 32 postes, 31 tronçons de 6,5 m → 201,5 m.
E05_NAMES = tuple(f"Poste {i:02d}" for i in range(1, 33))
E05_BUS = _stations_bus(E05_NAMES, (6.5,) * 31, first=GROUNDED_TERMINATOR, last=GOOD_TERMINATOR)
E05_ERRORS = bus_errors(E05_BUS)

# E06 : usage → impédance attendue (50 Ω ou 75 Ω).
E06_CASES: tuple[tuple[str, int], ...] = (
    ("Réseau Ethernet fin 10BASE2 d'un ancien atelier", 50),
    ("Caméra de vidéosurveillance analogique vers l'enregistreur", 75),
    ("Caméra de plateau en SDI vers une régie vidéo", 75),
    ("Prise d'antenne de télévision du salon", 75),
    ("Antenne d'un émetteur-récepteur radio de club", 50),
    ("Segment Ethernet épais 10BASE5 conservé dans un musée", 50),
    ("Descente d'une parabole satellite vers le décodeur", 75),
)
E06_CATEGORIES = ("50 Ω", "75 Ω")
E06_CORRECT: tuple[int, ...] = tuple(E06_CATEGORIES.index(f"{ohm} Ω") for _label, ohm in E06_CASES)

# E10 : étapes de montage d'un BNC, affichées dans le désordre.
E10_SHOWN: tuple[int, ...] = (3, 0, 5, 2, 6, 1, 4)

# E13 : lectures d'ohmmètre au T du premier poste, calculées sur des bus décrits.
READING_CATEGORIES = (
    "Normal : deux terminateurs 50 Ω vus",
    "Un seul terminateur vu : terminateur absent ou câble coupé",
    "Court-circuit âme/blindage",
    "Aucun terminateur vu : bus ouvert",
    "Terminateur de mauvaise valeur",
)


def classify_reading(value: float | None) -> int:
    if value is None:
        return 3
    if value == 0:
        return 2
    if value == 25:
        return 0
    if value == 50:
        return 1
    return 4


E13_CASES: tuple[tuple[str, Bus], ...] = (
    ("Salle A", BUS_OK),
    ("Salle B", BUS_MISSING_TERMINATOR),
    ("Salle C", BUS_SHORT),
    ("Salle D", _stations_bus(("P1", "P2", "P3"), (10, 10), first=BusEnd(None), last=BusEnd(None))),
    ("Salle E", _stations_bus(("P1", "P2", "P3"), (10, 10), first=BusEnd(75), last=BusEnd(75))),
    ("Salle F", BUS_CUT),
    ("Salle G", _stations_bus(("P1", "P2", "P3"), (10, 10), first=GOOD_TERMINATOR, last=BusEnd(75))),
)
E13_READINGS: tuple[float | None, ...] = tuple(ohmmeter_reading(bus, 0) for _name, bus in E13_CASES)
E13_CORRECT: tuple[int, ...] = tuple(classify_reading(v) for v in E13_READINGS)


def _reading_label(value: float | None) -> str:
    return "OL (infini)" if value is None else f"{fr(value)} Ω"


# E14 / X05 : réflectomètre.
E14_NS, E14_VF = 520, 0.66
E14_DISTANCE = tdr_distance_m(E14_NS, E14_VF)
X05_NS, X05_VF = 180, 0.66
X05_DISTANCE = tdr_distance_m(X05_NS, X05_VF)

X03_BUS = _stations_bus(
    ("Poste 1", "Poste 2", "Poste 3", "Poste 4"), (11, 9, 13),
    first=GROUNDED_TERMINATOR, last=BusEnd(50, grounded=True), attachments={"Poste 3": ATTACH_STUB},
)
X03_ERRORS = bus_errors(X03_BUS)


# =============================================================================================
# 16 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Relevé d'un bus 10BASE2 à corriger",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-23", "AP-36"),
        kind=KIND_SCHEMA,
        context=(
            "Dans une petite entreprise de transport, quatre postes anciens sont encore reliés en "
            "Ethernet fin 10BASE2 pour piloter une machine d'étiquetage. Depuis un déménagement de "
            "bureau, plus aucun poste ne communique. Tu relèves le câblage de bout en bout "
            "(document 1)."
        ),
        instructions=(
            "Relève toutes les non-conformités du segment et explique l'effet de chacune.",
            "Décris le segment corrigé, de l'extrémité 1 à l'extrémité 2.",
        ),
        documents=(bus_table("Document 1 — Relevé du segment (fictif)", E01_BUS),),
        criteria=(
            _c("Terminateur manquant", 0.75, "L'extrémité 2 (T du Serveur) n'a pas de terminateur : le signal s'y réfléchit entièrement, tout le segment est perturbé ; ajouter un terminateur 50 Ω."),
            _c("Câble entre T et carte", 0.75, "La Direction est reliée à son T par un câble : branche non terminée qui crée des réflexions ; le T doit être branché directement sur la carte."),
            _c("Segment corrigé", 0.5, "Terminateur 50 Ω relié à la terre, T Accueil, 9 m, T Compta, 14 m, T Direction (sur la carte), 6 m, T Serveur, terminateur 50 Ω (sans seconde terre)."),
        ),
        correction=(
            "Non-conformités calculées : " + " ".join(E01_ERRORS),
            "Sans terminateur, l'extrémité côté Serveur est un circuit ouvert : le signal s'y réfléchit en totalité et se superpose aux trames suivantes ; les cartes voient des collisions permanentes et aucun poste ne communique.",
            "Le câble entre le T et la carte de la Direction forme une dérivation non terminée : chaque signal s'y réfléchit. En 10BASE2, le T se branche directement sur la carte et le bus passe de T en T.",
            "Segment corrigé : terminateur 50 Ω (point de terre unique) sur le T de l'Accueil, 9 m de RG-58, T de la Compta, 14 m, T de la Direction branché sur sa carte, 6 m, T du Serveur avec un terminateur 50 Ω. Contrôle : environ 25 Ω entre âme et blindage à un T, réseau arrêté.",
        ),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Conforme ou non conforme ?",
        question_type="classification",
        requirement_ids=("AP-35", "AP-20"),
        kind=KIND_SCHEMA,
        context=(
            "Tu prépares l'audit de huit petits segments Ethernet fin 10BASE2 encore présents dans "
            "les ateliers d'un centre de formation. Pour chacun, le formateur a résumé le schéma "
            "en une ligne. Les règles à appliquer sont celles du cours (RG-58 50 Ω, 185 m, 30 postes, "
            "0,5 m entre deux T, T sur la carte, deux terminateurs 50 Ω, une seule terre)."
        ),
        instructions=("Classe chaque segment : conforme 10BASE2 ou non conforme.",),
        criteria=(
            _c("Classement", 8, "Conformes : 5 postes / 60 m et 3 postes / 180 m. Non conformes : un seul terminateur, tronçon RG-59, 190 m, câble entre T et carte, 0,3 m entre deux T, deux terres (1 point chacun)."),
        ),
        correction=(
            "Conformes : « 5 postes, 60 m » (tout est respecté) et « 3 postes, 180 m » (180 m reste sous la limite de 185 m).",
            "Non conformes : terminateur à un seul bout (extrémité libre) ; tronçon RG-59 (75 Ω dans un bus 50 Ω) ; 190 m (plus de 185 m) ; poste relié à son T par un câble (dérivation) ; 0,3 m entre deux T (0,5 m au moins) ; deux terres (une seule, sinon boucle de masse).",
        ),
        classification=Classification(
            categories=E02_CATEGORIES,
            elements=tuple(label for label, _bus in E02_CASES),
            correct=E02_CORRECT,
        ),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Un « réseau en étoile » en coaxial",
        question_type="short_answer",
        requirement_ids=("AP-35", "AP-23"),
        kind=KIND_SCHEMA,
        context=(
            "Un stagiaire doit relier trois PC de démonstration en 10BASE2. Il a dessiné le schéma "
            "suivant : un T BNC posé au milieu de la table, dont les trois sorties partent chacune "
            "par 5 m de RG-58 vers un PC, « comme un petit switch ». Aucun terminateur n'est prévu, "
            "puisque « chaque câble arrive sur une carte »."
        ),
        instructions=(
            "Explique pourquoi ce schéma ne peut pas fonctionner.",
            "Propose le schéma correct, élément par élément.",
        ),
        criteria=(
            _c("Pourquoi c'est faux", 1, "10BASE2 est un bus, pas une étoile : un T n'est pas un switch ; les cartes ne terminent pas le câble, les trois branches sont des extrémités libres qui réfléchissent le signal ; le T doit être sur la carte."),
            _c("Schéma correct", 1, "Bus : terminateur 50 Ω sur le T du PC 1, câble, T du PC 2, câble, T du PC 3 avec terminateur 50 Ω ; T branchés directement sur les cartes ; 0,5 m au moins entre T ; une seule terre."),
        ),
        correction=(
            "Le 10BASE2 est une topologie en bus : un seul câble passe d'un poste à l'autre. Un T BNC n'est qu'une dérivation passive, pas un switch : il relie électriquement les trois câbles. La carte réseau ne termine pas le câble (elle a une entrée à haute impédance) : chacune des trois branches est donc une extrémité libre qui réfléchit le signal. Aucun poste ne communiquerait de façon fiable.",
            "Schéma correct : T sur la carte du PC 1 avec un terminateur 50 Ω sur une sortie, câble RG-58 vers le T de la carte du PC 2, câble vers le T du PC 3 qui reçoit le second terminateur 50 Ω. Au moins 0,5 m entre deux T, une seule terre.",
        ),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Mauvaises impédances sur le schéma du laboratoire",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-20"),
        kind=KIND_SCHEMA,
        context=(
            "Dans le laboratoire d'un lycée technique, un ancien segment 10BASE2 de trois postes a "
            "été « réparé » avec du matériel trouvé dans un tiroir de l'atelier vidéo. Le réseau "
            "fonctionne mal : erreurs et collisions nombreuses. Le document 1 donne le relevé "
            "actuel ; les marquages ont été lus sur la gaine des câbles et sur les terminateurs."
        ),
        instructions=(
            "Relève les non-conformités et explique pourquoi elles perturbent le réseau.",
            "Indique le matériel à remplacer et le contrôle à faire ensuite.",
        ),
        documents=(bus_table("Document 1 — Relevé du segment du laboratoire (fictif)", E04_BUS),),
        criteria=(
            _c("Non-conformités", 0.75, "Terminateur de 75 Ω côté Labo-1 (il faut 50 Ω) ; tronçon de 10 m en RG-59 75 Ω (il faut du RG-58 50 Ω)."),
            _c("Effet", 0.75, "Chaque passage 50 Ω ↔ 75 Ω et le terminateur désadapté renvoient une partie du signal (réflexions) : erreurs, collisions."),
            _c("Remplacement et contrôle", 0.5, "Terminateur 50 Ω et tronçon RG-58 avec BNC 50 Ω ; vérifier le marquage, puis ≈ 25 Ω âme/blindage réseau arrêté et test de communication."),
        ),
        correction=(
            "Non-conformités calculées : " + " ".join(E04_ERRORS),
            "Le bus est prévu pour 50 Ω. À chaque changement d'impédance (passage du RG-59 au RG-58, terminateur de 75 Ω), une partie du signal est réfléchie : Γ = (75 − 50) / (75 + 50) = 0,2, soit 20 % de l'amplitude renvoyée. Ces échos se mélangent aux trames : erreurs et fausses collisions.",
            "Remplacer le terminateur par un 50 Ω et le tronçon de 10 m par du RG-58 50 Ω muni de BNC 50 Ω (marquage lu sur la gaine et le connecteur). Contrôle : environ 25 Ω entre âme et blindage à un T, réseau arrêté, puis échanges sans erreur entre les trois postes.",
        ),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Trop long, trop de postes : vérifier les limites",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-20", "AP-36"),
        kind=KIND_SCHEMA,
        context=(
            "Un musée de l'informatique veut faire fonctionner une salle de démonstration en "
            "10BASE2 avec 32 postes d'époque, alignés le long d'un mur, à 6,5 m l'un de l'autre. "
            "Le guide de montage (document 1) a été rédigé par un bénévole ; tu dois le vérifier "
            "avant la pose."
        ),
        instructions=(
            "Calcule la longueur du segment et compare-la, ainsi que le nombre de postes, aux limites du 10BASE2.",
            "Propose une organisation conforme.",
        ),
        documents=(
            _table(
                "Document 1 — Guide de montage (fictif)",
                ("Élément", "Valeur"),
                ("Postes", "32, chacun avec un T BNC sur la carte"),
                ("Câble entre deux postes", "RG-58, 6,5 m"),
                ("Extrémités", "terminateur 50 Ω de chaque côté, une seule terre"),
            ),
        ),
        criteria=(
            _c("Calcul", 0.75, f"31 tronçons × 6,5 m = {fr(E05_BUS.length_m)} m, plus que 185 m."),
            _c("Nombre de postes", 0.5, "32 postes : plus que 30 par segment."),
            _c("Organisation conforme", 0.75, "Deux segments (par exemple 16 + 16 postes, ≈ 97,5 m chacun), terminés chacun par deux terminateurs 50 Ω, reliés par un répéteur ; ou garder 30 postes au plus et ≤ 185 m."),
        ),
        correction=(
            f"Il y a 32 postes, donc 31 tronçons : 31 × 6,5 = {fr(E05_BUS.length_m)} m. Non-conformités calculées : " + " ".join(E05_ERRORS),
            "Solution : découper en deux segments de 16 postes (15 tronçons × 6,5 = 97,5 m chacun), chacun avec ses deux terminateurs 50 Ω et un seul point de terre, reliés par un répéteur 10BASE2 (ou un équipement d'interconnexion d'époque). Chaque segment respecte alors 185 m et 30 postes.",
        ),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="50 Ω ou 75 Ω selon l'usage",
        question_type="classification",
        requirement_ids=("AP-18", "AP-20", "AP-35"),
        kind=KIND_CHOICE,
        context=(
            "Un magasin de matériel d'occasion range ses câbles coaxiaux et ses connecteurs BNC par "
            "impédance. Le vendeur te demande, pour chaque demande de client, l'impédance du câble "
            "et des connecteurs à proposer. Les connecteurs se ressemblent : seule l'impédance "
            "marquée permet de choisir."
        ),
        instructions=("Classe chaque usage selon l'impédance à retenir.",),
        criteria=(
            _c("Classement", 7, "50 Ω : 10BASE2, radio, 10BASE5. 75 Ω : vidéosurveillance analogique, SDI, antenne TV, satellite (1 point chacun)."),
        ),
        correction=(
            "50 Ω : Ethernet coaxial historique (10BASE2 fin, 10BASE5 épais) et radiofréquence d'émission (antennes, mesure).",
            "75 Ω : vidéo (vidéosurveillance analogique, SDI), télévision et satellite. Un BNC peut être 50 Ω ou 75 Ω : la forme du connecteur ne suffit pas, on lit le marquage.",
        ),
        classification=Classification(
            categories=E06_CATEGORIES,
            elements=tuple(label for label, _ohm in E06_CASES),
            correct=E06_CORRECT,
        ),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Rallonger le bus avec du câble vidéo ?",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20", "AP-35"),
        kind=KIND_CHOICE,
        context=(
            "Pour ajouter un poste au bout d'un segment 10BASE2, un collègue propose d'utiliser une "
            "bobine de câble coaxial noir de même diamètre que le RG-58, déjà munie de BNC, restée "
            "après l'installation de caméras. Il affirme : « Un coax est un coax, et les BNC "
            "s'emboîtent, donc ça marchera »."
        ),
        instructions=(
            "Indique comment vérifier ce câble avant de l'utiliser.",
            "Explique pourquoi le raisonnement du collègue est faux et ce qu'il faut utiliser.",
        ),
        criteria=(
            _c("Vérification", 0.75, "Lire le marquage de la gaine (RG-59 = 75 Ω, RG-58 = 50 Ω) et celui des connecteurs ; un câble de caméra est très probablement du 75 Ω."),
            _c("Raisonnement faux", 0.75, "Le diamètre et l'emboîtement ne disent rien de l'impédance : les BNC 50 et 75 Ω s'accouplent mécaniquement ; un tronçon 75 Ω dans un bus 50 Ω crée des réflexions."),
            _c("Choix correct", 0.5, "RG-58 (A/U ou C/U) 50 Ω avec des BNC 50 Ω, T et terminateur 50 Ω ; respecter 185 m et 0,5 m entre T."),
        ),
        correction=(
            "On lit d'abord le marquage imprimé sur la gaine (par exemple « RG-59 … 75 Ω ») et celui des connecteurs. Un câble de vidéosurveillance est en général du RG-59 75 Ω.",
            "Le diamètre et le fait que les BNC s'emboîtent ne prouvent rien : les BNC 50 Ω et 75 Ω sont conçus pour s'accoupler mécaniquement. Le bus 10BASE2 est prévu pour 50 Ω ; un tronçon de 75 Ω crée deux changements d'impédance et donc des réflexions.",
            "Il faut du RG-58 50 Ω (A/U ou C/U) muni de BNC 50 Ω, avec le T du nouveau poste et le terminateur 50 Ω déplacé en bout de segment, en respectant 185 m au total.",
        ),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Liste de matériel pour ajouter un poste",
        question_type="short_answer",
        requirement_ids=("AP-35", "AP-36"),
        kind=KIND_CHOICE,
        context=(
            "Une imprimerie conserve un segment 10BASE2 de 140 m pour une ancienne machine. On doit "
            "ajouter un poste de contrôle au bout du segment, 20 m après le dernier poste actuel, "
            "qui porte aujourd'hui le terminateur. Tu dois rédiger la liste de matériel à commander "
            "et vérifier que l'ajout est possible."
        ),
        instructions=(
            "Vérifie que l'ajout respecte la longueur maximale.",
            "Rédige la liste de matériel avec, pour chaque élément, l'impédance ou le type attendu.",
        ),
        criteria=(
            _c("Longueur", 0.5, "140 + 20 = 160 m ≤ 185 m : possible."),
            _c("Matériel", 1, "20 m de RG-58 A/U ou C/U 50 Ω ; deux BNC mâles 50 Ω à sertir prévus pour ce câble (ou un cordon prêt à l'emploi) ; un T BNC 50 Ω pour la carte ; le terminateur 50 Ω existant déplacé (ou un neuf)."),
            _c("Outils et contrôle", 0.5, "Dénudeur coaxial et pince à sertir adaptés ; ≈ 25 Ω âme/blindage, réseau arrêté, et test de communication."),
        ),
        correction=(
            "Longueur après ajout : 140 + 20 = 160 m, sous la limite de 185 m : l'ajout est possible (le nombre de postes doit aussi rester ≤ 30).",
            "Matériel : 20 m de RG-58 A/U ou C/U (50 Ω) ; deux BNC mâles 50 Ω à sertir prévus pour ce câble, ou un cordon RG-58 de 20 m déjà équipé ; un T BNC 50 Ω à brancher directement sur la carte du nouveau poste ; le terminateur 50 Ω retiré de l'ancien dernier poste est vissé sur le T du nouveau.",
            "Outils : coupe-câble, dénudeur coaxial réglé pour le RG-58, pince à sertir avec la matrice du connecteur. Contrôle : environ 25 Ω entre âme et blindage à un T, réseau arrêté, puis communication de tous les postes.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Choisir dans un catalogue de connecteurs",
        question_type="document_analysis",
        requirement_ids=("AP-18", "AP-35"),
        kind=KIND_CHOICE,
        context=(
            "Une salle de spectacle installe une caméra de plateau en SDI reliée à la régie par "
            "45 m de câble vidéo RG-59, et doit réparer en même temps un ancien segment 10BASE2 "
            "de sa billetterie, en RG-58. Le catalogue du fournisseur (document 1) propose cinq "
            "références qui se ressemblent toutes."
        ),
        instructions=(
            "Choisis la ou les références pour chaque liaison et justifie.",
            "Indique pourquoi les autres références sont écartées.",
        ),
        documents=(
            _table(
                "Document 1 — Extrait de catalogue (fictif)",
                ("Réf.", "Désignation — impédance — câble prévu"),
                ("C1", "BNC mâle à sertir — 50 Ω — RG-58"),
                ("C2", "BNC mâle à sertir — 75 Ω — RG-59"),
                ("C3", "BNC mâle à visser (« twist-on ») — impédance non indiquée — RG-58 / RG-59"),
                ("C4", "T BNC mâle/femelle/femelle — 50 Ω"),
                ("C5", "Fiche F à compression — 75 Ω — RG-6"),
            ),
        ),
        criteria=(
            _c("Liaison SDI", 0.75, "C2 : BNC 75 Ω prévu pour le RG-59 (vidéo, SDI)."),
            _c("Segment 10BASE2", 0.75, "C1 (BNC 50 Ω pour RG-58) et C4 (T 50 Ω) si un T est à remplacer."),
            _c("Références écartées", 0.5, "C3 : impédance non indiquée et serrage à visser peu fiable ; C5 : fiche F pour RG-6 (TV/satellite), pas un BNC."),
        ),
        correction=(
            "Caméra SDI : le câble est du RG-59 75 Ω, il faut des BNC 75 Ω prévus pour ce câble : référence C2. En SDI (signal numérique très rapide), un connecteur 50 Ω provoquerait des réflexions.",
            "Billetterie 10BASE2 : bus en RG-58 50 Ω, il faut des BNC 50 Ω prévus pour le RG-58 : C1, et un T 50 Ω (C4) si un T est défectueux.",
            "Écartées : C3, dont l'impédance n'est pas indiquée et dont le montage à visser tient mal (contact du blindage peu fiable) ; C5, une fiche F 75 Ω pour câble RG-6 de télévision ou satellite, qui n'est pas un BNC.",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Remettre en ordre le montage d'un BNC à sertir",
        question_type="ordering",
        requirement_ids=("AP-35",),
        kind=KIND_PROCEDURE,
        context=(
            "Un nouveau technicien a noté sur des fiches les étapes de montage d'un connecteur BNC "
            "à sertir sur un câble RG-58, mais les fiches ont été mélangées. Le connecteur est "
            "un modèle en trois pièces (contact central, corps, bague) avec sa notice de cotes."
        ),
        instructions=("Remets les étapes dans l'ordre d'exécution.",),
        criteria=(
            _c("Ordre", 7, "Vérifier, enfiler, dénuder, contact, corps, sertir, contrôler."),
        ),
        correction=(
            "Ordre : " + " → ".join(f"{i}. {name}" for i, (name, _d) in enumerate(CRIMP_STEPS, start=1)) + ".",
            "Le manchon et la bague s'enfilent AVANT de préparer le câble (impossible ensuite) ; le contact central se fixe sur l'âme avant d'enfoncer le corps ; on sertit la bague sur la tresse en dernier ; on contrôle toujours avant de brancher.",
        ),
        ordering=Ordering(
            steps=tuple(f"{CRIMP_STEPS[i][0]} : {CRIMP_STEPS[i][1]}" for i in E10_SHOWN),
            correct=tuple(E10_SHOWN.index(i) for i in range(len(CRIMP_STEPS))),
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Procédure écrite : un cordon RG-58 BNC/BNC",
        question_type="long_answer",
        requirement_ids=("AP-35", "AP-C01"),
        kind=KIND_PROCEDURE,
        context=(
            "Le responsable d'un atelier de maintenance te demande une fiche de procédure pour "
            "fabriquer un cordon de 10 m en RG-58, équipé d'un BNC mâle 50 Ω à sertir à chaque bout, "
            "destiné à un segment 10BASE2. La fiche doit permettre à un stagiaire de travailler "
            "seul, en sécurité, et de contrôler son travail."
        ),
        instructions=(
            "Rédige la procédure complète : matériel, outils, sécurité, étapes de montage, contrôles.",
        ),
        criteria=(
            _c("Matériel et outils", 0.4, "RG-58 50 Ω, BNC mâles 50 Ω prévus pour ce câble, coupe-câble, dénudeur coaxial réglé, pince avec matrice adaptée, multimètre."),
            _c("Sécurité", 0.3, "Câble non raccordé au réseau, lames : gestes maîtrisés, chutes ramassées."),
            _c("Montage", 0.8, "Enfiler manchon et bague ; dénuder aux cotes de la notice sans entailler ; contact sur l'âme en butée et serti ; corps poussé, tresse sur le fût sans brin vers l'âme ; bague sertie ; autre bout."),
            _c("Contrôles", 0.5, "Visuel, traction, continuité âme-âme et blindage-blindage, résistance âme/blindage infinie (pas de court-circuit) ; étiquette."),
        ),
        correction=(
            "Matériel : 10 m de RG-58 A/U ou C/U 50 Ω, deux BNC mâles 50 Ω à sertir prévus pour ce câble, deux manchons. Outils : coupe-câble, dénudeur coaxial réglé pour le RG-58, pince à sertir avec la matrice du connecteur, multimètre.",
            "Sécurité : travailler sur un câble non raccordé, lames et dénudeur manipulés avec soin, chutes de tresse ramassées (un brin peut court-circuiter un connecteur).",
            "Montage de chaque bout : 1) couper franc ; 2) enfiler manchon et bague ; 3) dénuder aux cotes de la notice, sans entailler l'âme ni la tresse ; 4) âme dans le contact central jusqu'en butée, sertir le contact ; 5) pousser le corps : contact enclenché, tresse étalée sur le fût, aucun brin vers l'âme ; 6) ramener la bague sur la tresse et sertir ; 7) manchon par-dessus.",
            "Contrôles : visuel (contact à la bonne hauteur, pas de brin), traction ferme, multimètre : continuité âme-âme et blindage-blindage d'un bout à l'autre, résistance infinie entre âme et blindage. Étiqueter le cordon (RG-58, 50 Ω, 10 m).",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="Remplacer un BNC abîmé sur un bus en service",
        question_type="long_answer",
        requirement_ids=("AP-35", "AP-37", "AP-C01"),
        kind=KIND_PROCEDURE,
        context=(
            "Dans un laboratoire de contrôle qualité, le BNC d'un câble 10BASE2 a été écrasé par "
            "une chaise à roulettes, au T du poste 4 d'un segment qui en compte six. Le réseau "
            "fonctionne de façon intermittente. Tu dois remplacer le connecteur pendant la pause "
            "de midi, sans perdre de données."
        ),
        instructions=(
            "Rédige la procédure, de la préparation à la remise en service, en justifiant l'organisation.",
        ),
        criteria=(
            _c("Préparation", 0.5, "Prévenir et faire enregistrer le travail : ouvrir le bus coupe tout le segment ; matériel 50 Ω prévu pour le câble ; heure convenue."),
            _c("Remplacement", 0.75, "Couper la partie abîmée, monter un BNC 50 Ω selon la notice, contrôler visuellement et mécaniquement ; câble plus court : vérifier ≥ 0,5 m entre T."),
            _c("Tests", 0.5, "Avant reconnexion : continuité, pas de court-circuit ; segment refermé : ≈ 25 Ω âme/blindage réseau arrêté ; communication de tous les postes."),
            _c("Prévention et trace", 0.25, "Protéger le passage du câble (goulotte) ; consigner l'intervention."),
        ),
        correction=(
            "Préparation : ouvrir un bus 10BASE2 interrompt les six postes (deux demi-bus non terminés) : prévenir les utilisateurs et leur faire enregistrer leur travail, intervenir à l'heure convenue. Préparer un BNC mâle 50 Ω prévu pour le RG-58 et les outils adaptés.",
            "Remplacement : débrancher le câble du T, couper la partie écrasée, monter le nouveau BNC selon la notice (bague et manchon enfilés, dénudage aux cotes, contact serti, corps, bague sertie), contrôle visuel et traction. Vérifier que le câble raccourci laisse au moins 0,5 m entre deux T.",
            "Tests : continuité âme et blindage, pas de court-circuit âme/blindage ; segment refermé et réseau encore arrêté, environ 25 Ω entre âme et blindage à un T ; puis remise en service et vérification de la communication de chaque poste.",
            "Prévention : faire passer le câble dans une goulotte ou un passe-câble pour éviter un nouvel écrasement. Compte rendu : cause, pièce remplacée, mesures, résultat.",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Interpréter des mesures à l'ohmmètre",
        question_type="classification",
        requirement_ids=("AP-35", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Dans un centre de formation, sept salles ont chacune un petit segment 10BASE2. Un "
            "technicien a mesuré, réseau arrêté, la résistance entre l'âme et le blindage au T du "
            "premier poste de chaque salle. La résistance du câble est négligeable sur ces courtes "
            "longueurs."
        ),
        instructions=("Associe chaque mesure à son diagnostic.",),
        criteria=(
            _c("Classement", 7, "25 Ω = normal ; 50 Ω = un seul terminateur vu (absent ou coupure) ; 0 Ω = court-circuit ; OL = aucun terminateur ; 37,5 Ω ou 30 Ω = terminateur de mauvaise valeur (1 point chacun)."),
        ),
        correction=(
            "Deux terminateurs 50 Ω en parallèle donnent 50 × 50 / (50 + 50) = 25 Ω : c'est la valeur normale.",
            "50 Ω : un seul terminateur est « vu » depuis le T, soit parce que l'autre manque, soit parce qu'une coupure isole l'autre partie du bus. 0 Ω : court-circuit entre âme et blindage. OL (infini) : aucun terminateur vu.",
            "37,5 Ω (deux 75 Ω en parallèle) ou 30 Ω (50 Ω ∥ 75 Ω) : au moins un terminateur n'a pas la bonne valeur.",
        ),
        classification=Classification(
            categories=READING_CATEGORIES,
            elements=tuple(f"{name} : {_reading_label(v)}" for (name, _bus), v in zip(E13_CASES, E13_READINGS, strict=True)),
            correct=E13_CORRECT,
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Localiser une coupure au réflectomètre",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-20", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Un segment 10BASE2 de 120 m traverse un faux plafond entre deux ateliers. Les "
            "ohmmètres donnent 50 Ω au T du premier poste au lieu de 25 Ω. L'entreprise loue un "
            "réflectomètre (TDR) ; branché au premier T, il affiche le résultat du document 1."
        ),
        instructions=(
            "Interprète la trace : nature du défaut et distance depuis le point de mesure (montre le calcul).",
            "Indique comment confirmer et réparer.",
        ),
        documents=(
            _table(
                "Document 1 — Mesure au réflectomètre (fictive)",
                ("Paramètre", "Valeur"),
                ("Facteur de vélocité réglé (fiche du câble)", fr(E14_VF, 2)),
                ("Réflexion", "même sens que l'impulsion (positive), forte"),
                ("Temps aller-retour", f"{E14_NS} ns"),
            ),
        ),
        criteria=(
            _c("Nature", 0.75, "Réflexion positive forte = impédance qui monte jusqu'au circuit ouvert : coupure (ou connecteur ouvert), cohérent avec 50 Ω à l'ohmmètre."),
            _c("Distance", 0.75, f"d = 0,66 × 0,3 m/ns × {E14_NS} ns ÷ 2 ≈ {fr(E14_DISTANCE)} m (aller-retour divisé par 2)."),
            _c("Confirmation et réparation", 0.5, "Inspecter le câble vers cette distance (faux plafond, connecteurs) ; remplacer le tronçon ou monter deux BNC et un raccord ; re-mesurer : plus de réflexion, ≈ 25 Ω."),
        ),
        correction=(
            "Une réflexion de même sens que l'impulsion signifie que l'impédance augmente ; forte, elle indique un circuit ouvert : câble coupé ou connecteur ouvert. C'est cohérent avec la lecture de 50 Ω (un seul terminateur vu).",
            f"Le signal fait l'aller-retour : d = facteur de vélocité × c × t ÷ 2 = 0,66 × 0,2998 m/ns × {E14_NS} ns ÷ 2 ≈ {fr(E14_DISTANCE)} m depuis le T de mesure.",
            "On inspecte le câble autour de cette distance (passage dans le faux plafond, raccords). Réparation : remplacer le tronçon, ou couper proprement de part et d'autre du défaut, monter deux BNC 50 Ω et un raccord droit (femelle/femelle) 50 Ω. Contrôle : nouvelle mesure sans réflexion jusqu'au terminateur, 25 Ω à l'ohmmètre, communication rétablie.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Tout le réseau tombe quand un poste est déplacé",
        question_type="short_answer",
        requirement_ids=("AP-35", "AP-37", "AP-23"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Dans une agence de voyages équipée en 10BASE2, une employée a déplacé son PC sur un "
            "autre bureau. Pour libérer le poste, elle a dévissé les deux câbles de son T BNC et "
            "les a laissés pendre. Depuis, plus aucun des six postes de l'agence n'accède au "
            "serveur."
        ),
        instructions=(
            "Explique pourquoi tous les postes sont touchés et non seulement le sien.",
            "Indique la remise en service immédiate et la bonne façon de déplacer un poste sur ce réseau.",
        ),
        criteria=(
            _c("Explication", 1, "Le bus est ouvert : deux demi-bus avec chacun une extrémité libre, non terminée ; réflexions et collisions sur tout le segment."),
            _c("Remise en service et règle", 1, "Rebrancher les deux câbles sur le T (ou les relier par un raccord femelle/femelle 50 Ω) pour refermer le bus ; pour déplacer un poste, retirer le T de la carte sans jamais ouvrir le bus ; vérifier ≈ 25 Ω, réseau arrêté."),
        ),
        correction=(
            "En 10BASE2, tous les postes partagent le même câble. En dévissant les deux câbles du T, l'employée a coupé le bus en deux morceaux ; chacun a désormais une extrémité libre, sans terminateur : le signal s'y réfléchit, les cartes voient des collisions et le réseau entier s'arrête.",
            "Remise en service : revisser les deux câbles sur le T (le T peut rester sans PC) ou les relier par un raccord femelle/femelle 50 Ω. Règle : pour déplacer un poste, on débranche le T de la carte, on ne sépare jamais les câbles du T. Contrôle : environ 25 Ω entre âme et blindage, réseau arrêté, et accès au serveur rétabli.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Coupures quand on touche un connecteur",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-37"),
        kind=KIND_DIAGNOSIS,
        context=(
            "Dans un atelier d'électronique, le poste de mesure perd le réseau quand quelqu'un "
            "bouge le câble derrière son établi. Le segment 10BASE2 mesure 25 Ω à l'ohmmètre, "
            "réseau arrêté. Tu examines le connecteur BNC le plus proche et notes tes "
            "observations (document 1)."
        ),
        instructions=(
            "Interprète les observations et nomme le défaut.",
            "Explique pourquoi la mesure à 25 Ω ne l'a pas révélé et décris la réparation et le contrôle.",
        ),
        documents=(
            _table(
                "Document 1 — Observations sur le connecteur (fictives)",
                ("Contrôle", "Observation"),
                ("Bague de sertissage", "tourne autour du câble"),
                ("Traction légère", "le câble recule de 2 mm dans le connecteur"),
                ("Ohmmètre âme/blindage en tordant le câble", "passe par moments de 25 Ω à 50 Ω"),
                ("Contact central", "en retrait par rapport au corps"),
            ),
        ),
        criteria=(
            _c("Défaut", 0.75, "Connecteur mal serti : bague non serrée sur la tresse, contact central en retrait ; contact intermittent."),
            _c("Pourquoi 25 Ω au repos", 0.5, "Au repos le contact se fait ; le défaut n'apparaît qu'en bougeant (lecture qui saute à 50 Ω)."),
            _c("Réparation et contrôle", 0.75, "Couper le connecteur, en monter un neuf 50 Ω selon la notice, avec l'outil adapté ; contrôle visuel, traction, mesure stable en manipulant ; protéger le câble des efforts."),
        ),
        correction=(
            "La bague tourne et le câble recule : la bague n'est pas sertie sur la tresse. Le contact central en retrait touche mal la prise. La lecture qui passe de 25 à 50 Ω en tordant le câble prouve un contact intermittent : connecteur mal serti.",
            "Au repos, le contact se fait par chance : la mesure statique donne 25 Ω. Le défaut n'apparaît qu'en bougeant le câble, d'où les coupures quand on touche l'établi. Une mesure se fait aussi en manipulant le câble.",
            "Réparation : couper ce connecteur, en monter un neuf, 50 Ω, prévu pour le RG-58, selon la notice et avec la matrice adaptée. Contrôle : visuel, traction ferme, mesure stable à 25 Ω en manipulant le câble ; fixer le câble pour éviter les efforts sur le connecteur.",
        ),
    ),
)

# =============================================================================================
# Mini-examen /20 (« Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="50 Ω au lieu de 25 Ω",
        question_type="short_answer",
        requirement_ids=("AP-35", "AP-37"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une scierie, cinq postes reliés en 10BASE2 ne communiquent plus depuis le "
            "nettoyage de l'atelier. Réseau arrêté, tu mesures 50 Ω entre l'âme et le blindage au "
            "T du premier poste. Tous les câbles semblent branchés sur leurs T."
        ),
        instructions=(
            "Interprète la mesure et indique les deux causes possibles.",
            "Décris comment les distinguer et corriger.",
        ),
        criteria=(
            _c("Interprétation", 1, "Normal = 25 Ω (deux 50 Ω en parallèle) ; 50 Ω = un seul terminateur vu : terminateur absent (retiré, perdu) ou coupure du câble."),
            _c("Distinguer et corriger", 1, "Vérifier les deux extrémités (terminateur présent, 50 Ω) ; si présent, chercher la coupure (mesure de proche en proche ou réflectomètre) ; remettre un terminateur 50 Ω ou réparer ; re-mesurer 25 Ω."),
        ),
        correction=(
            "Avec deux terminateurs 50 Ω, on lit 25 Ω. Une lecture de 50 Ω signifie qu'un seul terminateur est vu : soit l'autre a été retiré ou perdu pendant le nettoyage, soit une coupure isole une partie du bus.",
            "On contrôle d'abord les deux extrémités : présence et valeur du terminateur (50 Ω). S'il est en place, on cherche la coupure (mesures de T en T, réflectomètre). On remet un terminateur 50 Ω ou on répare le câble, puis on re-mesure 25 Ω et on vérifie la communication.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Câbler une caméra SDI",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20"),
        kind=KIND_SCENARIO,
        context=(
            "Une église installe une caméra pour diffuser les offices ; elle sort en SDI sur une "
            "prise BNC et doit être reliée à un mélangeur vidéo par 40 m de câble. Le bénévole "
            "a récupéré un lot de RG-58 et de BNC 50 Ω issus d'un ancien réseau informatique."
        ),
        instructions=(
            "Indique le câble et les connecteurs à utiliser et justifie.",
            "Explique ce que risquerait la solution du bénévole.",
        ),
        criteria=(
            _c("Choix", 1, "Liaison vidéo SDI = 75 Ω : câble 75 Ω (RG-59 ou câble vidéo numérique adapté à la distance) et BNC 75 Ω prévus pour ce câble."),
            _c("Risque", 1, "RG-58 et BNC 50 Ω : désadaptation, réflexions importantes aux fréquences du SDI : image dégradée ou absente ; la forme du BNC ne garantit pas l'impédance."),
        ),
        correction=(
            "Le SDI est une liaison vidéo 75 Ω : on utilise un câble coaxial 75 Ω (RG-59 ou câble vidéo numérique prévu pour la distance) et des BNC 75 Ω prévus pour ce câble, aux deux bouts.",
            "Le RG-58 et les BNC 50 Ω s'emboîteraient, mais l'impédance ne correspond pas : aux fréquences très élevées du SDI, chaque désadaptation réfléchit une partie du signal ; l'image peut être dégradée, décrocher ou ne pas apparaître. La forme du connecteur ne dit rien de l'impédance.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Schéma d'atelier à corriger",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-23", "AP-36"),
        kind=KIND_SCENARIO,
        context=(
            "Un formateur prépare un schéma de câblage 10BASE2 pour une salle de quatre postes et "
            "te demande de le relire avant l'installation. Le document 1 reprend le schéma "
            "élément par élément."
        ),
        instructions=(
            "Relève les erreurs du schéma et explique le risque de chacune.",
            "Écris la version corrigée.",
        ),
        documents=(bus_table("Document 1 — Schéma prévu (fictif)", X03_BUS),),
        criteria=(
            _c("Erreurs", 1, "Poste 3 relié à son T par un câble (dérivation non terminée, réflexions) ; blindage à la terre aux deux bouts (boucle de masse, courants parasites)."),
            _c("Version corrigée", 1, "T du Poste 3 directement sur sa carte ; un seul point de terre (une extrémité) ; le reste inchangé : deux terminateurs 50 Ω, RG-58, 33 m."),
        ),
        correction=(
            "Erreurs calculées : " + " ".join(X03_ERRORS),
            "La liaison de 2 m entre le T et la carte du Poste 3 est une branche non terminée : elle réfléchit le signal. Deux mises à la terre créent une boucle de masse : des courants peuvent circuler dans le blindage et perturber le signal.",
            "Version corrigée : terminateur 50 Ω relié à la terre sur le T du Poste 1, 11 m, T du Poste 2, 9 m, T du Poste 3 branché sur sa carte, 13 m, T du Poste 4 avec terminateur 50 Ω non relié à la terre.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="Procédure écrite : monter un BNC à sertir",
        question_type="long_answer",
        requirement_ids=("AP-35",),
        kind=KIND_SCENARIO,
        context=(
            "Pour l'atelier d'une école, on te demande de rédiger la procédure de montage d'un BNC "
            "mâle à sertir 50 Ω sur un câble RG-58, à afficher près de l'établi. Les connecteurs "
            "achetés sont des modèles en trois pièces livrés avec une notice de cotes."
        ),
        instructions=(
            "Rédige la procédure, du choix du matériel au contrôle final, en citant les points de contrôle.",
        ),
        criteria=(
            _c("Matériel et outils", 0.5, "Connecteur 50 Ω prévu pour le RG-58, dénudeur coaxial réglé, pince avec matrice adaptée, multimètre ; notice."),
            _c("Étapes ordonnées", 1, "Manchon et bague enfilés ; dénudage aux cotes de la notice sans entailler ; contact sur l'âme, serti ; corps poussé, tresse sur le fût, aucun brin vers l'âme ; bague sertie."),
            _c("Contrôles", 0.5, "Visuel (hauteur du contact, brins), traction, continuité âme et blindage, pas de court-circuit âme/blindage."),
        ),
        correction=(
            "Matériel : BNC mâle 50 Ω à sertir prévu pour le RG-58 et sa notice, manchon ; outils : coupe-câble, dénudeur coaxial réglé pour le RG-58, pince à sertir avec la matrice du connecteur, multimètre.",
            "Étapes : 1) couper franc ; 2) enfiler manchon et bague ; 3) dénuder aux cotes A, B, C de la notice, sans entailler l'âme ni la tresse ; 4) âme dans le contact central jusqu'en butée, sertir le contact ; 5) pousser le corps, contact enclenché, tresse étalée sur le fût, aucun brin vers l'âme ; 6) ramener la bague, sertir ; 7) manchon.",
            "Contrôles : contact à la bonne hauteur, pas de brin libre, bague qui ne tourne pas, traction ferme ; multimètre : continuité de l'âme et du blindage, résistance infinie entre âme et blindage.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Réflexion négative au réflectomètre",
        question_type="document_analysis",
        requirement_ids=("AP-35", "AP-20", "AP-37"),
        kind=KIND_SCENARIO,
        context=(
            "Le segment 10BASE2 d'un entrepôt est en panne ; l'ohmmètre affiche 0 Ω entre âme et "
            "blindage au T du premier poste, réseau arrêté. Un réflectomètre branché à ce T donne "
            "le résultat du document 1."
        ),
        instructions=(
            "Indique la nature du défaut et calcule sa distance (montre le calcul).",
            "Cite deux causes plausibles et la réparation.",
        ),
        documents=(
            _table(
                "Document 1 — Mesure au réflectomètre (fictive)",
                ("Paramètre", "Valeur"),
                ("Facteur de vélocité réglé", fr(X05_VF, 2)),
                ("Réflexion", "sens inverse de l'impulsion (négative), forte"),
                ("Temps aller-retour", f"{X05_NS} ns"),
            ),
        ),
        criteria=(
            _c("Nature et distance", 1, f"Réflexion négative forte = court-circuit (cohérent avec 0 Ω) ; d = 0,66 × 0,3 × {X05_NS} ÷ 2 ≈ {fr(X05_DISTANCE)} m."),
            _c("Causes et réparation", 1, "Brin de tresse touchant l'âme dans un connecteur, câble écrasé ou percé (agrafe, vis) ; refaire le connecteur ou remplacer le tronçon ; re-mesurer 25 Ω."),
        ),
        correction=(
            f"Une réflexion inversée et forte indique une impédance qui chute jusqu'au court-circuit, cohérent avec 0 Ω à l'ohmmètre. Distance : 0,66 × 0,2998 m/ns × {X05_NS} ns ÷ 2 ≈ {fr(X05_DISTANCE)} m depuis le T de mesure.",
            "Causes plausibles : brin de tresse en contact avec l'âme dans un connecteur, câble écrasé ou percé par une agrafe ou une vis. Réparation : refaire le connecteur ou remplacer le tronçon ; contrôle : 25 Ω, réseau arrêté, plus de réflexion, communication rétablie.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Thick Ethernet n'est pas thin Ethernet",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-35"),
        kind=KIND_SCENARIO,
        context=(
            "Dans les archives techniques d'une usine, un plan décrit un « câble jaune épais » de "
            "400 m, avec des « prises vampires » et des boîtiers reliés aux machines par des "
            "câbles à connecteur 15 broches. Un collègue propose de remplacer un boîtier "
            "défectueux par un T BNC branché sur le câble jaune."
        ),
        instructions=(
            "Identifie la technologie décrite et ses caractéristiques principales.",
            "Explique pourquoi la proposition du collègue ne convient pas.",
        ),
        criteria=(
            _c("Identification", 1, "10BASE5 (Ethernet épais) : coax 50 Ω ≈ 10 mm, 10 Mb/s, segment ≤ 500 m, prise vampire + transceiver, câble AUI (15 broches, ≤ 50 m), terminateurs 50 Ω (N)."),
            _c("Pourquoi pas un T BNC", 1, "Le câble épais n'a pas de BNC : connecteurs N, raccordement par prise vampire et transceiver ; on ne coupe pas le câble pour un T ; le 10BASE2 (RG-58, T sur la carte) est une autre technologie ; remplacer le transceiver."),
        ),
        correction=(
            "C'est de l'Ethernet épais 10BASE5 : câble coaxial 50 Ω d'environ 10 mm (souvent jaune), 10 Mb/s, segment de 500 m au plus (ici 400 m), stations raccordées par une prise vampire et un transceiver posés sur le câble (repères tous les 2,5 m), puis un câble AUI à connecteur 15 broches de 50 m au plus ; terminateurs 50 Ω sur connecteurs N.",
            "Le câble épais ne se raccorde pas en BNC : y insérer un T imposerait de le couper et de monter des connecteurs qui n'existent pas pour ce câble, et la station n'aurait pas de transceiver. Le 10BASE2 (RG-58, T BNC sur la carte) est une autre technologie. On remplace le transceiver défectueux par un modèle équivalent.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Câble écrasé sous une porte",
        question_type="short_answer",
        requirement_ids=("AP-35", "AP-20", "AP-37"),
        kind=KIND_SCENARIO,
        context=(
            "Dans une menuiserie, un segment 10BASE2 passe sous une porte coulissante. Depuis des "
            "travaux, le réseau fait beaucoup d'erreurs sans être coupé. L'ohmmètre affiche 25 Ω, "
            "réseau arrêté, et le câble est visiblement aplati sous le rail de la porte."
        ),
        instructions=(
            "Explique pourquoi un câble écrasé perturbe le réseau alors que l'ohmmètre est normal.",
            "Décris la réparation et la prévention.",
        ),
        criteria=(
            _c("Explication", 1, "L'écrasement change la géométrie âme/blindage, donc l'impédance à cet endroit : réflexions et erreurs ; en continu, âme et blindage restent continus et isolés : 25 Ω normal."),
            _c("Réparation et prévention", 1, "Remplacer le tronçon (ou couper, deux BNC 50 Ω et un raccord) ; contrôles (25 Ω, réflectomètre si disponible, communication) ; faire passer le câble dans un passe-câble protégé, loin du rail."),
        ),
        correction=(
            "L'impédance caractéristique dépend de la géométrie (diamètres de l'âme et du blindage, diélectrique). En écrasant le câble, on modifie cette géométrie : l'impédance change localement et une partie du signal est réfléchie, d'où les erreurs. L'ohmmètre mesure en continu : âme et blindage restent continus et isolés, donc 25 Ω.",
            "Réparation : remplacer le tronçon abîmé (ou couper le passage écrasé, monter deux BNC 50 Ω et un raccord droit 50 Ω), puis vérifier 25 Ω, l'absence de réflexion au réflectomètre si disponible et la communication. Prévention : faire passer le câble par un passe-câble ou une goulotte, hors du rail de la porte.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Localiser un court-circuit sans réflectomètre",
        question_type="short_answer",
        requirement_ids=("AP-35", "AP-37"),
        kind=KIND_SCENARIO,
        context=(
            "Un segment 10BASE2 de cinq postes (PC-1 à PC-5) affiche 0 Ω entre âme et blindage à "
            "n'importe quel T, réseau arrêté. Tu n'as qu'un multimètre ; les tronçons sont "
            "accessibles et se débranchent aux T."
        ),
        instructions=(
            "Décris une méthode ordonnée pour trouver le tronçon ou le connecteur en court-circuit.",
            "Précise les précautions et le contrôle final.",
        ),
        criteria=(
            _c("Méthode", 1.25, "Réseau arrêté et utilisateurs prévenus ; ouvrir le bus au milieu (débrancher un câble d'un T), mesurer chaque moitié : le 0 Ω reste d'un seul côté ; recommencer (dichotomie) ou tester chaque tronçon débranché isolément (âme/blindage infini attendu)."),
            _c("Précautions et contrôle", 0.75, "Multimètre seulement réseau arrêté ; repérer les câbles ; réparer le connecteur ou le tronçon ; refermer le bus, ≈ 25 Ω, communication."),
        ),
        correction=(
            "Le court-circuit se voit de partout tant que le bus est fermé. Réseau arrêté et utilisateurs prévenus, on ouvre le bus vers le milieu (par exemple entre PC-2 et PC-3, en débranchant le câble du T) et on mesure chaque moitié : seule la moitié qui contient le défaut affiche encore 0 Ω. On recommence sur cette moitié (recherche par dichotomie) jusqu'à isoler un tronçon ; un tronçon débranché seul doit afficher une résistance infinie entre âme et blindage.",
            "Précautions : mesurer réseau arrêté, repérer chaque câble avant de le débrancher. On refait le connecteur ou on remplace le tronçon fautif, on referme le bus, on vérifie environ 25 Ω et la communication de tous les postes.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Compte rendu : terminateur remplacé",
        question_type="long_answer",
        requirement_ids=("AP-35", "AP-C01"),
        kind=KIND_SCENARIO,
        context=(
            "Dans un garage, le segment 10BASE2 de quatre postes était en panne. Réseau arrêté, tu "
            "as mesuré 50 Ω au T du poste atelier au lieu de 25 Ω. Le terminateur du poste "
            "réception, à l'autre bout, était fêlé et mesurait l'infini ; tu l'as remplacé par un "
            "terminateur 50 Ω neuf et tout fonctionne."
        ),
        instructions=(
            "Rédige le compte rendu : demande, constats et mesures, hypothèse, action, contrôles, résultat et recommandation.",
        ),
        criteria=(
            _c("Constats et mesures", 0.5, "Réseau en panne, 4 postes ; 50 Ω au T atelier au lieu de 25 Ω (réseau arrêté) : un seul terminateur vu."),
            _c("Cause et action", 0.5, "Terminateur du poste réception fêlé, ouvert (infini) ; remplacé par un terminateur 50 Ω neuf."),
            _c("Contrôles et résultat", 0.5, "25 Ω après remplacement ; communication des quatre postes vérifiée avec les utilisateurs."),
            _c("Recommandation", 0.5, "Protéger l'extrémité (choc), garder un terminateur 50 Ω de rechange ; envisager la migration vers un câblage à paires torsadées et un switch."),
        ),
        correction=(
            "Demande : réseau des quatre postes du garage en panne. Constat : réseau arrêté, 50 Ω entre âme et blindage au T du poste atelier au lieu de 25 Ω : un seul terminateur est vu.",
            "Hypothèse et vérification : terminateur absent ou défectueux, ou coupure ; le terminateur du poste réception, fêlé, mesure l'infini. Action : remplacement par un terminateur 50 Ω neuf.",
            "Contrôles : 25 Ω au T du poste atelier, puis communication des quatre postes vérifiée avec les utilisateurs. Résultat : réseau rétabli.",
            "Recommandation : protéger l'extrémité contre les chocs, garder un terminateur 50 Ω de rechange ; l'Ethernet coaxial étant une technologie ancienne, envisager le passage à un câblage à paires torsadées avec un switch.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="BNC 50 Ω ou 75 Ω : la fréquence compte",
        question_type="short_answer",
        requirement_ids=("AP-18", "AP-20", "AP-35"),
        kind=KIND_SCENARIO,
        context=(
            "Un technicien a relié un appareil de mesure basse fréquence avec un BNC 75 Ω sur un "
            "câble 50 Ω : tout fonctionne. Il en conclut qu'il peut mélanger BNC 50 Ω et 75 Ω "
            "partout, y compris sur les liaisons 3G-SDI d'une régie vidéo."
        ),
        instructions=(
            "Explique pourquoi le mélange a pu fonctionner dans le premier cas.",
            "Explique pourquoi sa conclusion est fausse pour la régie et ce qu'il faut faire.",
        ),
        criteria=(
            _c("Premier cas", 1, "Les BNC 50/75 Ω s'accouplent mécaniquement ; à basse fréquence (en dessous d'une dizaine de MHz) la courte désadaptation d'un connecteur a un effet négligeable."),
            _c("Régie SDI", 1, "Aux fréquences très élevées du SDI, chaque désadaptation réfléchit une partie du signal : erreurs, image instable ou absente ; utiliser partout câble, connecteurs et équipements 75 Ω."),
        ),
        correction=(
            "Les BNC 50 Ω et 75 Ω sont conçus pour s'accoupler sans dommage. À basse fréquence (en dessous d'une dizaine de MHz environ), la très courte zone désadaptée d'un connecteur n'a pratiquement pas d'effet : le mélange a pu fonctionner.",
            "En 3G-SDI, le signal monte à des fréquences très élevées : chaque désadaptation (connecteur, câble ou équipement) réfléchit une partie du signal et dégrade la liaison (erreurs, image instable ou absente). En vidéo, on utilise partout câble, connecteurs et équipements 75 Ω ; on lit le marquage plutôt que de juger à la forme.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
        ):
            errors.append(f"{item.key} : classification incohérente.")
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
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    return errors

