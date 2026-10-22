"""Banque visuelle MC01 « Architecture générale d'un PC » (ticket #48) : premières
questions d'identification de composants à partir d'images réelles.

Notions strictement limitées à celles de MC01 (ticket #83) : RAM, CPU, alimentation (PSU),
HDD, SSD, carte mère, carte graphique (GPU), et les six éléments du tableau « Ce qu'on
trouve sur une carte mère » (socket CPU, emplacements RAM, emplacements PCIe, connecteurs
de stockage, connecteurs E/S, chipset).

Trois natures de visuels (`app.v1.assets.VisualType`) :
- **photos réelles** : Wikimedia Commons, licences libres (auteur, licence et lien
  conservés et affichés) ; miniatures 800 px ré-encodées, métadonnées EXIF retirées ; sur
  la photo du SSD, la mention imprimée du type de composant est floutée (elle donnait la
  réponse) — modification signalée dans la provenance, licence d'origine conservée ;
- **illustration générée** : carte graphique en SVG, générée par IA (Claude Code) pour
  ce ticket ; la consigne de génération est conservée dans les métadonnées de l'asset ;
- **schéma technique** : carte mère simplifiée en SVG avec repères A à F, réutilisé par
  deux questions (diagram_labeling et image_identification) — preuve qu'un même asset
  sert plusieurs `QuestionVersion` sans être dupliqué.

Import idempotent, sur le même principe que `app.v1.bank.import_mc01_legacy_to_bank` :
appelé au premier accès practice/exam de MC01 (`app.v1.routes_sessions.
_ensure_bank_seeded`). Marqueur d'idempotence : `QuestionVersion.prompt_version ==
VISUAL_BANK_VERSION` (jamais `generation_source=IMPORTED`, déjà utilisé comme marqueur par
l'import legacy MC01). Difficulté déclarée volontairement absente : comme le reste
d'AMPCR, pour ne pas changer la composition des sessions (voir `compose_selection`).
"""

from typing import Any

from sqlalchemy.orm import Session

from app.models import UAA, Module
from app.v1.assets import AssetSpec, VisualType, get_or_create_asset, link_asset
from app.v1.models import (
    AssetKind,
    AssetSourceType,
    GenerationSource,
    Question,
    QuestionVersion,
    create_question,
)
from app.v1.question_engine import validate_content

VISUAL_BANK_VERSION = "ticket48-mc01-visual-v1"

_COMMONS = "Wikimedia Commons"


def _photo(key: str, *, alt: str, author: str, license: str, source_url: str, note: str = "") -> AssetSpec:
    provenance = f"Photo {_COMMONS}, miniature 800 px ré-encodée (EXIF retiré)"
    if note:
        provenance = f"{provenance} ; {note}"
    return AssetSpec(
        key=f"mc01-photo-{key}",
        storage_ref=f"img/ampcr/mc01_photo_{key}.jpg",
        kind=AssetKind.IMAGE,
        mime_type="image/jpeg",
        source_type=AssetSourceType.EXTERNAL,
        visual_type=VisualType.PHOTO,
        alt_text=alt,
        license=license,
        provenance=provenance,
        source_url=source_url,
        author=author,
    )


ASSET_SPECS: dict[str, AssetSpec] = {
    "ram": _photo(
        "ram",
        alt="Photo d'un composant électronique rouge, long et fin, posé à plat",
        author="ElooKoN",
        license="CC BY-SA 4.0",
        source_url="https://commons.wikimedia.org/wiki/File:RAM_Module_(SDRAM-DDR4).jpg",
    ),
    "cpu": _photo(
        "cpu",
        alt="Photo de la face inférieure d'un petit composant carré couvert de contacts dorés",
        author="45746845685468q",
        license="CC0",
        source_url=(
            "https://commons.wikimedia.org/wiki/"
            "File:Processor_INTEL_CORE_2_DUO_(%D0%B2%D0%B8%D0%B4_%D1%81%D0%B7%D0%B0%D0%B4%D0%B8).jpg"
        ),
    ),
    "psu": _photo(
        "psu",
        alt="Photo d'un boîtier métallique ajouré d'où sort un faisceau de câbles colorés terminés par des connecteurs",
        author="Dmitry Makeev",
        license="CC BY-SA 4.0",
        source_url="https://commons.wikimedia.org/wiki/File:ATX_Computer_power_supply_unit.jpg",
    ),
    "hdd": _photo(
        "hdd",
        alt="Photo d'un composant ouvert montrant un disque métallique brillant et un bras de lecture",
        author="Evan-Amos",
        license="CC BY-SA 3.0",
        source_url="https://commons.wikimedia.org/wiki/File:Laptop-hard-drive-exposed.jpg",
    ),
    "ssd": _photo(
        "ssd",
        alt="Photo d'un boîtier rectangulaire plat et fermé, gris clair, avec une étiquette",
        author="Raimond Spekking",
        license="CC BY-SA 4.0",
        source_url="https://commons.wikimedia.org/wiki/File:Crucial_SSD_MX300_525GB-8478.jpg",
        note="mention du type de composant floutée sur l'étiquette",
    ),
    "motherboard": _photo(
        "motherboard",
        alt="Photo vue de dessus d'un grand circuit imprimé noir portant de nombreux connecteurs et emplacements",
        author="Jacek Halicki",
        license="CC BY-SA 4.0",
        source_url=(
            "https://commons.wikimedia.org/wiki/"
            "File:2023_P%C5%82yta_g%C5%82%C3%B3wna_ASRock_A320M-DVS.jpg"
        ),
    ),
    "gpu": _photo(
        "gpu",
        alt="Photo d'une carte électronique bleue munie d'un ventilateur et d'une équerre métallique avec des prises",
        author="Evan-Amos",
        license="Domaine public",
        source_url="https://commons.wikimedia.org/wiki/File:Sapphire-Radeon-HD-5570-Video-Card.jpg",
    ),
    "gpu_illustration": AssetSpec(
        key="mc01-illustration-carte-graphique",
        storage_ref="img/ampcr/mc01_illustration_carte_graphique.svg",
        kind=AssetKind.SVG,
        mime_type="image/svg+xml",
        source_type=AssetSourceType.AI_GENERATED,
        visual_type=VisualType.ILLUSTRATION,
        alt_text="Illustration d'une carte électronique avec deux ventilateurs, une équerre à prises et une rangée de contacts dorés",
        license="Créé pour Jury Central",
        provenance="Illustration vectorielle générée par IA (Claude Code) pour le ticket #48",
        extra={
            "generation_prompt": (
                "Flat, clean pedagogical vector illustration of a desktop PC graphics card seen "
                "from the front: blue printed circuit board, dark shroud with two round fans, "
                "metal bracket with display outputs on the left, gold PCIe edge connector at "
                "the bottom, small power connector on top. No text, no logos, no brand marks, "
                "light grey background."
            ),
            "generation_model": "claude (SVG rédigé)",
        },
    ),
    "motherboard_diagram": AssetSpec(
        key="mc01-schema-carte-mere",
        storage_ref="img/ampcr/mc01_schema_carte_mere.svg",
        kind=AssetKind.SVG,
        mime_type="image/svg+xml",
        source_type=AssetSourceType.MANUAL,
        visual_type=VisualType.DIAGRAM,
        alt_text="Schéma simplifié d'une carte mère vue de dessus, avec six repères lettrés de A à F",
        license="Créé pour Jury Central",
        provenance="Schéma technique simplifié réalisé pour le ticket #48 (éléments du tableau MC01 « Ce qu'on trouve sur une carte mère »)",
    ),
}

# Libellés communs des composants (options des questions d'identification).
_RAM = "Barrette de mémoire vive (RAM)"
_CPU = "Processeur (CPU)"
_PSU = "Bloc d'alimentation (PSU)"
_HDD = "Disque dur (HDD)"
_SSD = "SSD"
_MB = "Carte mère"
_GPU = "Carte graphique (GPU)"


def _choice(prompt: str, labels: list[str], correct: str) -> dict[str, Any]:
    options = [{"option_id": str(index), "label": label} for index, label in enumerate(labels, start=1)]
    correct_ids = [option["option_id"] for option in options if option["label"] == correct]
    return {
        "prompt": prompt,
        "response_mode": "choice",
        "options": options,
        "correct_option_ids": correct_ids,
    }


# Repères du schéma de carte mère (voir le SVG) — ordre des étiquettes volontairement
# différent de l'ordre des repères.
_DIAGRAM_LABELS = [
    {"id": "socket", "label": "Socket CPU"},
    {"id": "ram_slots", "label": "Emplacements RAM"},
    {"id": "pcie", "label": "Emplacements PCIe"},
    {"id": "storage", "label": "Connecteurs de stockage"},
    {"id": "io", "label": "Connecteurs E/S (panneau arrière)"},
    {"id": "chipset", "label": "Chipset"},
]
_DIAGRAM_MAPPING = {
    "A": "pcie",
    "B": "ram_slots",
    "C": "socket",
    "D": "chipset",
    "E": "io",
    "F": "storage",
}

# (clé d'asset, type, contenu)
VISUAL_QUESTIONS: list[tuple[str, str, dict[str, Any]]] = [
    (
        "ram",
        "image_identification",
        _choice(
            "Quel composant de l'ordinateur reconnais-tu sur cette photo ?",
            [_CPU, _RAM, _GPU, _PSU],
            _RAM,
        ),
    ),
    (
        "cpu",
        "image_identification",
        _choice(
            "Cette photo montre la face inférieure d'une pièce qui se fixe directement sur la "
            "carte mère. De quelle pièce s'agit-il ?",
            [_SSD, _RAM, _CPU, _HDD],
            _CPU,
        ),
    ),
    (
        "psu",
        "image_identification",
        _choice(
            "Identifie l'élément matériel photographié, avec son faisceau de câbles et ses "
            "connecteurs.",
            [_PSU, _MB, _HDD, _GPU],
            _PSU,
        ),
    ),
    (
        "hdd",
        "image_identification",
        _choice(
            "Ce composant de stockage est photographié capot retiré. Lequel est-ce ?",
            [_SSD, _RAM, _GPU, _HDD],
            _HDD,
        ),
    ),
    (
        "ssd",
        "image_identification",
        _choice(
            "Ce support de stockage fermé ne contient aucune pièce mécanique en mouvement. "
            "Quel est son nom ?",
            [_HDD, _SSD, _PSU, _CPU],
            _SSD,
        ),
    ),
    (
        "motherboard",
        "image_identification",
        _choice(
            "Sur quel composant, visible ici, viennent se brancher tous les autres éléments "
            "du PC ?",
            [_GPU, _PSU, _MB, _RAM],
            _MB,
        ),
    ),
    (
        "gpu",
        "image_identification",
        _choice(
            "Nomme la carte d'extension visible sur cette photo, sortie de l'ordinateur.",
            [_RAM, _MB, _CPU, _GPU],
            _GPU,
        ),
    ),
    (
        "gpu_illustration",
        "image_identification",
        {
            "prompt": "Écris le nom du composant représenté sur cette illustration.",
            "response_mode": "text",
            "accepted_answers": [
                "carte graphique",
                "une carte graphique",
                "la carte graphique",
                "GPU",
                "carte graphique (GPU)",
                "carte graphique GPU",
                "carte vidéo",
                "une carte vidéo",
            ],
            "rubric": (
                "Bonne réponse : la carte graphique (GPU), aussi appelée carte vidéo. Une "
                "réponse « processeur » ou « CPU » est fausse."
            ),
        },
    ),
    (
        "motherboard_diagram",
        "diagram_labeling",
        {
            "prompt": (
                "Sur ce schéma simplifié d'une carte mère, associe chaque repère (A à F) à "
                "l'élément qu'il désigne."
            ),
            "zones": [{"zone_id": marker, "marker": marker} for marker in "ABCDEF"],
            "label_options": _DIAGRAM_LABELS,
            "correct_mapping": _DIAGRAM_MAPPING,
        },
    ),
    (
        "motherboard_diagram",
        "image_identification",
        _choice(
            "Regarde le repère B du schéma : quel élément de la carte mère désigne-t-il ?",
            ["Socket CPU", "Emplacements PCIe", "Emplacements RAM", "Chipset"],
            "Emplacements RAM",
        ),
    ),
]


def visual_bank_already_imported(db: Session, uaa: UAA) -> bool:
    return (
        db.query(Question.id)
        .join(QuestionVersion, QuestionVersion.question_id == Question.id)
        .filter(Question.uaa_id == uaa.id, QuestionVersion.prompt_version == VISUAL_BANK_VERSION)
        .first()
        is not None
    )


def import_mc01_visual_questions(db: Session, module: Module, uaa: UAA) -> int:
    """Crée les assets (sans doublon) et les questions visuelles MC01. Idempotent."""
    if visual_bank_already_imported(db, uaa):
        return 0
    assets = {key: get_or_create_asset(db, spec) for key, spec in ASSET_SPECS.items()}
    created = 0
    for asset_key, question_type, content in VISUAL_QUESTIONS:
        validate_content(question_type, 1, content)
        question = create_question(
            db,
            module_id=module.id,
            uaa_id=uaa.id,
            question_type=question_type,
            content_json=content,
            generation_source=GenerationSource.MANUAL,
            prompt_version=VISUAL_BANK_VERSION,
        )
        link_asset(db, question.current_version, assets[asset_key])
        created += 1
    db.flush()
    return created
