"""Parcours « AMPCR — Pratique écrite » (cycle 2026-2027/1) : socle et matrice de couverture
officielle (ticket #192).

**Source faisant foi** : consignes officielles du Jury de la FWB
« 26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf » (6 pages, voir
`OFFICIAL_SOURCE`). Les textes des exigences (`OFFICIAL_REQUIREMENTS`) et des consignes du
jour (`DAY_INSTRUCTIONS`) sont recopiés depuis ce PDF (extraction texte, espaces multiples
réduits à un seul) — jamais reformulés. Le programme 345/2007/249 (`PROGRAMME_SOURCE`) est
un complément : les consignes ne le remplacent pas, mais il n'est pas transcrit ici.

Ce module ne crée **aucun contenu** en base. Les emplacements PR01–PR30 (cours) et
EX01–EX06 (exercices pratiques écrits) sont un plan : un emplacement n'est « publié » que
si une UAA de même code existe en base et est publiée (`published_codes`). Les 6 modules,
les titres des emplacements et leur rattachement aux exigences sont une proposition de
découpage (ticket #192), à confirmer ou ajuster par les tickets de cours.

Statut d'une exigence (`requirement_status`) :
- « non traité » : aucun cours ni exercice lié publié ;
- « partiel » : au moins un élément publié, mais pas tous, ou pas encore validé ;
- « validé » : TOUS les cours ET l'exercice liés sont publiés ET l'exigence figure dans
  `VALIDATED_REQUIREMENT_IDS` (validation explicite d'un ticket de cours). La couverture
  n'est jamais déclarée complète autrement.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session as DBSession

from app import models

PRACTICAL_PATH_URL = "/ampcr-pratique"
# Module en base qui accueillera les UAA PR01-PR30 / EX01-EX06 (créé par le premier ticket de
# cours, pas ici). Slug d'UAA attendu : `ampcr-pratique-pr01` (convention `slugify(module-uaa)`).
PRACTICAL_MODULE_CODE = "AMPCR-PRATIQUE"
CYCLE_LABEL = "2026-2027/1"


@dataclass(frozen=True)
class SourceDocumentRef:
    title: str
    url: str
    version: str
    date: str
    pages: int
    sha256: str
    retrieved_on: str


OFFICIAL_SOURCE = SourceDocumentRef(
    title=(
        "Consignes d'examen — Cycle 2026-2027/1 — CESS P — Option assistant·e de maintenance "
        "PC-réseaux — Examen pratique (Laboratoire, T.P. méthodes)"
    ),
    url=(
        "https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/"
        "Consignes_specifiques/CESS/CESS_P/OBG/AMPCR/"
        "26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf"
    ),
    version="Cycle 2026-2027/1 (août 2026 à janvier 2027)",
    date="2026-07-13 (date de création du PDF)",
    pages=6,
    sha256="7a93c3858ffd67b42620bc5364aa9b8e964a379bdf255bbcd126b50c4df095e1",
    retrieved_on="2026-10-26",
)

PROGRAMME_SOURCE = SourceDocumentRef(
    title=(
        "Programme d'études de l'option de base groupée Assistant / Assistante de maintenance "
        "PC-réseaux — 345/2007/249"
    ),
    url=(
        "https://jurys.cfwb.be/fileadmin/sites/jurys/secondaire/uploads/BDD_document/"
        "Programmes/CESS/CESS_P/OBG/AMPCR/AMPCR.pdf"
    ),
    version="345/2007/249 (d'application depuis 2008-2009)",
    date="2015-10-29 (dernière modification du PDF)",
    pages=46,
    sha256="95e45949fc3c36d6e8ea82e7643791d323b7f1a668da54113c373f41a69bf14b",
    retrieved_on="2026-10-26",
)

# Lien cité p. 2 du PDF des consignes (tel quel).
PROGRAMME_LINK_IN_CONSIGNES = "http://www.wallonie-bruxelles-enseignement.be/progr/345-2007-249%20.pdf"


# --- Consignes du jour (pp. 2-4, texte officiel) ---------------------------------------------


@dataclass(frozen=True)
class InstructionSection:
    title: str
    page: int
    paragraphs: tuple[str, ...]
    emphasis: tuple[str, ...] = ()  # paragraphes mis en avant (majuscules / « !! » du PDF)


DAY_INSTRUCTIONS: tuple[InstructionSection, ...] = (
    InstructionSection(
        title="Modalités de passation",
        page=3,
        paragraphs=(
            "L’EXAMEN SE FERA UNIQUEMENT PAR ÉCRIT.",
            ("À partir du cycle 2022-2023/1, les deux matières pratiques de l’OBG AMPCR, à "
            "savoir : « laboratoire » et « T.P. et méthodes », ont fait l’objet d’une "
            "évaluation commune."),
            "Les deux matières sont évaluées dans un seul et même examen.",
            ("Une dispense sera attribuée au candidat ayant obtenu une moyenne générale d’au "
            "moins 50% (10/20) à l’ensemble de l’épreuve pratique. Aucune dispense partielle "
            "ne sera accordée."),
            "La moyenne globale sera donc calculée pour ces deux matières.",
            ("Il ne sera, dès lors, plus possible d’être dispensé de l’une des deux matières à "
            "partir du cycle 2022-2023/1."),
            ("!! Cette mesure ne s’applique qu’aux candidats qui doivent présenter ces deux "
            "matières."),
            ("Le candidat ayant obtenu une dispense à l’une des deux matières pratiques lors des "
            "cycles précédents ne devra présenter que la matière pour laquelle il a été ajourné."),
            ("L’examen pratique sera basé sur les matières suivantes : T.P. ET MÉTHODES — "
            "LABORATOIRE"),
            ("La date et le lieu de l’épreuve sont repris dans l'horaire de votre titre publié "
            "sur le site Internet des jurys."),
            ("Pour rappel : d’un cycle à l’autre le mode d’évaluation et la conception des "
            "examens peuvent changer."),
        ),
        emphasis=(
            "L’EXAMEN SE FERA UNIQUEMENT PAR ÉCRIT.",
            ("!! Cette mesure ne s’applique qu’aux candidats qui doivent présenter ces deux "
            "matières."),
        ),
    ),
    InstructionSection(
        title="Organisation de l’examen",
        page=3,
        paragraphs=(
            ("A l’exception des candidats dispensés des 2 matières théoriques, seuls les "
            "candidats présents à l’épreuve théorique (structure des ordinateurs et systèmes "
            "d’exploitation et Télécommunication et réseaux) seront autorisés à présenter "
            "l’épreuve pratique (Laboratoire et T.P. et Méthodes)."),
        ),
    ),
    InstructionSection(
        title="Matériel",
        page=4,
        paragraphs=(
            ("Matériel autorisé : matériel de base d’écriture, crayons de couleur, latte, crayon "
            "gris, gomme et le matériel scolaire de base, pochette ou trousse plastique "
            "transparente."),
            ("En début d’examen, on vous préviendra si l’utilisation d’une calculatrice (non "
            "programmable) est nécessaire ou non."),
            ("Matériel refusé : dictionnaire des noms communs/propres, les correcteurs "
            "orthographiques, Tipp-Ex (ou autres correcteurs similaires), feuilles de "
            "brouillon, calculatrice programmable, pochette ou trousse non transparente."),
            ("Les candidats veilleront à posséder le matériel requis lors de l’épreuve car aucun "
            "prêt de matériel ne sera accordé. L’échange de matériel durant l’épreuve, étant "
            "considéré comme une interaction avec autrui, sera sanctionné. De même, en cas "
            "d’oubli, aucun matériel ne pourra être apporté en cours d’épreuve aux candidats "
            "par une tierce personne."),
            ("Les GSM, montres connectables ou tout autre objet connectable sont éteints et "
            "laissés dans votre sac. Ils ne peuvent ni être visibles ni être portés sur vous "
            "pendant l’examen."),
        ),
    ),
    InstructionSection(
        title="Programme",
        page=2,
        paragraphs=(
            "Le numéro du programme : 345/2007/249",
            ("Rappel : ces consignes ne se substituent pas au programme de la Fédération "
            "Wallonie-Bruxelles."),
        ),
    ),
)


# --- Exigences (pp. 5-6, liste exhaustive) ---------------------------------------------------

KIND_OFFICIAL = "officiel"
KIND_COMPLEMENT = "complément pédagogique"


@dataclass(frozen=True)
class Requirement:
    id: str  # identifiant stable : AP-01..AP-38 (officiel), AP-C01.. (complément)
    text: str
    page: int | None  # page du PDF des consignes ; None pour un complément
    kind: str
    theory_codes: tuple[str, ...] = ()  # mini-cours théoriques MC existants qui abordent la notion
    note: str = ""


# Texte exact des puces des pp. 5-6, dans l'ordre du PDF. theory_codes : uniquement des MC
# dont le cours publié mentionne réellement la notion (contrôle textuel au ticket #192) —
# un lien de lecture, jamais une preuve de couverture de l'épreuve pratique.
_OFFICIAL_ROWS: tuple[tuple[str, int, tuple[str, ...], str], ...] = (
    ("La structure d’un ordinateur, ses composants et ses périphériques.", 5, ("MC01",), ""),
    (
        ("Les différents éléments qui peuvent constituer un ordinateur (Processeur, mémoire "
        "RAM-ROM, carte mère, BIOS, UEFI, etc.)."),
        5, ("MC01", "MC02", "MC03", "MC07"), "",
    ),
    (
        ("Les différents types de disque dur et unités de stockage, le formatage, la "
        "défragmentation."),
        5, ("MC04", "MC08"), "",
    ),
    ("Les caractéristiques d’une alimentation PC.", 5, ("MC05",), ""),
    ("Les périphériques d’entrée et de sortie et le rôle d'un pilote.", 5, ("MC12",), ""),
    ("Branchements, interfaces et connexions.", 5, ("MC02",), ""),
    ("La carte mère et ses éléments constitutifs.", 5, ("MC02",), ""),
    ("Les différents systèmes d’exploitation actuellement sur le marché.", 5, ("MC09", "MC11"), ""),
    (
        ("Les principaux messages d’erreurs, l’interprétation et les démarches d’intervention y "
        "afférant."),
        5, ("MC07", "MC29", "MC30"), "Proche de AP-13 (les deux puces figurent au PDF).",
    ),
    ("Installation complète des différents systèmes d’exploitation courants.", 5, ("MC08", "MC09"), ""),
    ("Paramètres et commandes de base des systèmes d'exploitation courants.", 5, ("MC10", "MC11"), ""),
    ("Interface graphique et interface de ligne de commande.", 5, ("MC10", "MC11"), ""),
    (
        ("Connaître les principaux messages d’erreurs, comment interpréter ceux-ci et comment "
        "intervenir si possible."),
        5, ("MC29", "MC30"), "Proche de AP-09 (les deux puces figurent au PDF).",
    ),
    ("Montage, démontage et reconditionnement d’un PC.", 5, ("MC06",), ""),
    ("Dépannage sur les dysfonctionnements courants (hardware ou software).", 5, ("MC29", "MC30"), ""),
    ("Vocabulaire technique.", 5, (), "Transversal : lexique AMPCR existant."),
    ("Notion de compatibilité.", 5, ("MC04", "MC12"), ""),
    ("Les différents types de câbles : UTP, FTP, STP, Coax.", 5, ("MC15",), "FTP et coaxial absents de la théorie actuelle."),
    ("Les débits binaires des câbles.", 6, ("MC15",), ""),
    (
        ("Les caractéristiques des câbles : atténuation, notion d’impédance, sensibilité aux "
        "parasites, blindage, précautions d’utilisation, les avantages, les inconvénients des "
        "uns par rapport aux autres, la longueur maximale d’un tronçon suivant le débit, les "
        "connecteurs, etc."),
        6, ("MC15",), "Atténuation et impédance absentes de la théorie actuelle.",
    ),
    (
        ("La fibre optique et ses caractéristiques : support d’information, débit binaire, "
        "longueur d’un tronçon, notion d’atténuation, connexion, avantages et inconvénients, "
        "etc."),
        6, ("MC14",), "La théorie actuelle ne fait que citer la fibre.",
    ),
    ("Comparaison entre la fibre optique et les autres types de câbles.", 6, (), "Aucune théorie existante."),
    ("Topologies de réseaux.", 6, ("MC23",), ""),
    (
        "Notions de domaine, groupe de travail, comptes utilisateurs et groupes d’utilisateurs.",
        6, ("MC33",), "Domaine / groupe de travail absents de la théorie actuelle.",
    ),
    ("Partage de ressources (imprimantes, disques, répertoires…).", 6, ("MC33",), ""),
    ("Mise en partage sur un réseau informatique de documents et applications.", 6, ("MC33",), ""),
    ("Les notions de droit et de permission.", 6, ("MC33", "MC10"), ""),
    ("Connexion de deux machines en direct.", 6, ("MC15",), ""),
    ("Notions de base sur les protocoles (TCP/IP, OSI, NETBEUI…).", 6, ("MC13", "MC21"), "NetBEUI absent de la théorie actuelle."),
    (
        ("L’adressage IP, les adresses MAC, l’identification d’une adresse MAC et d’une adresse "
        "IP."),
        6, ("MC16", "MC20"), "",
    ),
    ("Hub, switch, passerelle, routeur, modem.", 6, ("MC14",), "Hub absent de la théorie actuelle."),
    ("Connexions et interventions en cas de panne internet.", 6, ("MC22", "MC31"), ""),
    ("WIFI : principe, sécurisation, cryptage, répéteur.", 6, ("MC25", "MC26"), "Répéteur absent de la théorie actuelle."),
    ("Description de la réalisation d’un câble avec connecteurs RJ45 (code des couleurs).", 6, ("MC15",), ""),
    ("Description de la réalisation d’un câble avec connecteurs BNC.", 6, (), "Aucune théorie existante."),
    ("Câblage et installation physique d’un réseau informatique.", 6, ("MC15", "MC23"), ""),
    ("Dépannage de problèmes simples d’accès au réseau.", 6, ("MC31",), ""),
    ("Création d’un mini réseau entre plusieurs machines.", 6, ("MC16", "MC37"), ""),
)

OFFICIAL_REQUIREMENTS: tuple[Requirement, ...] = tuple(
    Requirement(id=f"AP-{index:02d}", text=text, page=page, kind=KIND_OFFICIAL, theory_codes=theory, note=note)
    for index, (text, page, theory, note) in enumerate(_OFFICIAL_ROWS, start=1)
)

# Compléments pédagogiques : utiles pour réussir l'épreuve écrite, mais absents de la liste
# des pp. 5-6 — toujours affichés comme tels, jamais comme exigence officielle.
COMPLEMENT_REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement(
        id="AP-C01",
        text=(
            "Rédiger une réponse écrite de technicien : décrire une intervention étape par "
            "étape et justifier chaque choix."
        ),
        page=None,
        kind=KIND_COMPLEMENT,
        theory_codes=("MC36",),
        note="Méthode : l'épreuve pratique se fait uniquement par écrit (p. 3).",
    ),
    Requirement(
        id="AP-C02",
        text="Sécurité électrique et protection ESD lors d'une intervention sur un PC.",
        page=None,
        kind=KIND_COMPLEMENT,
        theory_codes=("MC05",),
        note="Prérequis des interventions de montage/démontage (AP-14).",
    ),
)

ALL_REQUIREMENTS: tuple[Requirement, ...] = OFFICIAL_REQUIREMENTS + COMPLEMENT_REQUIREMENTS
REQUIREMENTS_BY_ID: dict[str, Requirement] = {r.id: r for r in ALL_REQUIREMENTS}


# --- Modules, cours PR01-PR30 et exercices EX01-EX06 ---------------------------------------


@dataclass(frozen=True)
class CourseSlot:
    code: str  # PR01..PR30
    title: str
    module_key: str
    requirement_ids: tuple[str, ...]


@dataclass(frozen=True)
class ExerciseSlot:
    code: str  # EX01..EX06
    title: str
    module_key: str


@dataclass(frozen=True)
class PracticalModule:
    key: str  # P1..P6
    title: str
    summary: str
    icon: str  # Bootstrap Icons
    course_codes: tuple[str, ...]
    exercise_code: str


_COURSE_ROWS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("PR01", "Structure d'un ordinateur, composants et périphériques", "P1", ("AP-01", "AP-02")),
    ("PR02", "Carte mère, processeur, mémoire RAM-ROM, BIOS et UEFI", "P1", ("AP-02", "AP-07")),
    ("PR03", "Disques, unités de stockage, formatage et défragmentation", "P1", ("AP-03",)),
    ("PR04", "Caractéristiques d'une alimentation PC", "P1", ("AP-04",)),
    ("PR05", "Branchements, interfaces, connexions et compatibilité", "P1", ("AP-06", "AP-17")),
    ("PR06", "Systèmes d'exploitation actuellement sur le marché", "P2", ("AP-08",)),
    ("PR07", "Installation complète d'un système d'exploitation courant", "P2", ("AP-10",)),
    ("PR08", "Paramètres et commandes de base", "P2", ("AP-11",)),
    ("PR09", "Interface graphique et interface de ligne de commande", "P2", ("AP-12",)),
    ("PR10", "Périphériques d'entrée et de sortie, rôle d'un pilote", "P2", ("AP-05", "AP-17")),
    ("PR11", "Messages d'erreur : interpréter et intervenir", "P3", ("AP-09", "AP-13")),
    ("PR12", "Montage et démontage d'un PC en sécurité", "P3", ("AP-14", "AP-C02")),
    ("PR13", "Reconditionnement d'un PC", "P3", ("AP-14", "AP-17")),
    ("PR14", "Dépannage des dysfonctionnements matériels courants", "P3", ("AP-15",)),
    ("PR15", "Dépannage des dysfonctionnements logiciels courants", "P3", ("AP-15", "AP-09")),
    ("PR16", "Types de câbles : UTP, FTP, STP, coaxial", "P4", ("AP-18",)),
    ("PR17", "Caractéristiques et débits des câbles", "P4", ("AP-19", "AP-20")),
    ("PR18", "La fibre optique et sa comparaison avec les câbles", "P4", ("AP-21", "AP-22")),
    ("PR19", "Réaliser un câble RJ45 : le code des couleurs", "P4", ("AP-34",)),
    ("PR20", "Réaliser un câble à connecteurs BNC", "P4", ("AP-35",)),
    ("PR21", "Topologies, câblage et installation physique d'un réseau", "P5", ("AP-23", "AP-36")),
    ("PR22", "Notions de base sur les protocoles", "P5", ("AP-29",)),
    ("PR23", "Adressage IP et adresses MAC", "P5", ("AP-30",)),
    ("PR24", "Hub, switch, passerelle, routeur, modem", "P5", ("AP-31",)),
    ("PR25", "Wi-Fi : principe, sécurisation, cryptage, répéteur", "P5", ("AP-33",)),
    ("PR26", "Domaine, groupe de travail, comptes et groupes", "P6", ("AP-24",)),
    ("PR27", "Partages, droits et permissions", "P6", ("AP-25", "AP-26", "AP-27")),
    ("PR28", "Connexion directe et mini réseau entre plusieurs machines", "P6", ("AP-28", "AP-38")),
    ("PR29", "Panne internet et problèmes simples d'accès au réseau", "P6", ("AP-32", "AP-37")),
    ("PR30", "Vocabulaire technique et rédaction d'une intervention", "P6", ("AP-16", "AP-C01")),
)

COURSE_SLOTS: tuple[CourseSlot, ...] = tuple(
    CourseSlot(code=code, title=title, module_key=module_key, requirement_ids=reqs)
    for code, title, module_key, reqs in _COURSE_ROWS
)
COURSE_SLOTS_BY_CODE: dict[str, CourseSlot] = {c.code: c for c in COURSE_SLOTS}

_MODULE_ROWS: tuple[tuple[str, str, str, str], ...] = (
    ("P1", "Matériel du PC", "Composants, carte mère, stockage, alimentation et connexions.", "cpu"),
    ("P2", "Systèmes d'exploitation", "Systèmes du marché, installation, paramètres, interfaces et pilotes.", "windows"),
    ("P3", "Intervention et dépannage du PC", "Messages d'erreur, montage, reconditionnement et dépannage.", "tools"),
    ("P4", "Câbles et supports de transmission", "Cuivre, fibre optique, caractéristiques et réalisation de câbles.", "plug"),
    ("P5", "Réseau : architecture et adressage", "Topologies, protocoles, adressage, équipements et Wi-Fi.", "diagram-3"),
    ("P6", "Partages, comptes et dépannage réseau", "Comptes, partages, droits, mini réseau et pannes d'accès.", "share"),
)

EXERCISE_SLOTS: tuple[ExerciseSlot, ...] = tuple(
    ExerciseSlot(code=f"EX0{index}", title=f"Exercices pratiques écrits — {title}", module_key=key)
    for index, (key, title, _summary, _icon) in enumerate(_MODULE_ROWS, start=1)
)
EXERCISE_SLOTS_BY_CODE: dict[str, ExerciseSlot] = {e.code: e for e in EXERCISE_SLOTS}

MODULES: tuple[PracticalModule, ...] = tuple(
    PracticalModule(
        key=key,
        title=title,
        summary=summary,
        icon=icon,
        course_codes=tuple(c.code for c in COURSE_SLOTS if c.module_key == key),
        exercise_code=next(e.code for e in EXERCISE_SLOTS if e.module_key == key),
    )
    for key, title, summary, icon in _MODULE_ROWS
)
MODULES_BY_KEY: dict[str, PracticalModule] = {m.key: m for m in MODULES}

# Exigences explicitement validées (cours ET exercice relus) par un ticket de cours.
# Vide au ticket #192 : aucun cours pratique n'existe encore.
VALIDATED_REQUIREMENT_IDS: frozenset[str] = frozenset()

STATUS_TODO = "non traité"
STATUS_PARTIAL = "partiel"
STATUS_VALIDATED = "validé"


def courses_for_requirement(requirement_id: str) -> tuple[CourseSlot, ...]:
    return tuple(c for c in COURSE_SLOTS if requirement_id in c.requirement_ids)


def exercises_for_requirement(requirement_id: str) -> tuple[ExerciseSlot, ...]:
    module_keys = {c.module_key for c in courses_for_requirement(requirement_id)}
    return tuple(e for e in EXERCISE_SLOTS if e.module_key in module_keys)


def requirement_status(requirement_id: str, published: frozenset[str] | set[str]) -> str:
    codes = [c.code for c in courses_for_requirement(requirement_id)]
    codes += [e.code for e in exercises_for_requirement(requirement_id)]
    done = [code for code in codes if code in published]
    if codes and len(done) == len(codes) and requirement_id in VALIDATED_REQUIREMENT_IDS:
        return STATUS_VALIDATED
    return STATUS_PARTIAL if done else STATUS_TODO


# --- Lien avec la base (aucune écriture) ---------------------------------------------------

PLANNED_CODES: frozenset[str] = frozenset(
    [c.code for c in COURSE_SLOTS] + [e.code for e in EXERCISE_SLOTS]
)


def published_uaas(db: DBSession) -> dict[str, models.UAA]:
    """UAA publiées du module pratique portant un code PRxx/EXxx du plan. Aucune au ticket
    #192 : les cours et exercices pratiques seront créés par leurs propres tickets."""
    rows = (
        db.query(models.UAA)
        .join(models.Module, models.Module.id == models.UAA.module_id)
        .filter(
            models.Module.code == PRACTICAL_MODULE_CODE,
            models.UAA.code.in_(PLANNED_CODES),
            models.UAA.is_published.is_(True),
        )
        .all()
    )
    return {u.code: u for u in rows}


def theory_uaas(db: DBSession) -> dict[str, models.UAA]:
    """Mini-cours théoriques MC publiés du module AMPCR, par code (liens « théorie »)."""
    module = db.query(models.Module).filter_by(code="AMPCR").first()
    if module is None:
        return {}
    return {u.code: u for u in module.uaas if u.is_published}


def coverage_rows(published: frozenset[str] | set[str]) -> list[dict]:
    return [
        {
            "requirement": req,
            "courses": courses_for_requirement(req.id),
            "exercises": exercises_for_requirement(req.id),
            "status": requirement_status(req.id, published),
        }
        for req in ALL_REQUIREMENTS
    ]


def coverage_summary(rows: list[dict]) -> dict:
    official = [r for r in rows if r["requirement"].kind == KIND_OFFICIAL]
    counts = {s: sum(1 for r in official if r["status"] == s) for s in (STATUS_TODO, STATUS_PARTIAL, STATUS_VALIDATED)}
    return {
        "official_total": len(official),
        "complement_total": len(rows) - len(official),
        "counts": counts,
        "complete": bool(official) and counts[STATUS_VALIDATED] == len(official),
    }
