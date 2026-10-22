"""Assets visuels réutilisables de la banque V1 (ticket #48).

Le modèle `Asset`/`QuestionAsset` existe depuis le ticket #38 (§ F) ; ce module en fait
une chaîne utilisable, sans nouvelle table :

- **Trois natures visuelles distinguées** (`VisualType`) : photo réelle, illustration
  générée, schéma technique. Stockée dans `Asset.metadata_json["visual_type"]` (aucune
  migration de schéma), en plus de `kind` (format : image raster, SVG…) et `source_type`
  (manuel, IA, externe…), qui restent les colonnes existantes.
- **Source, licence, provenance** : colonnes existantes `source_url`, `license`,
  `provenance` ; auteur, légende et texte alternatif dans `metadata_json`.
- **Aucun doublon inutile** : `get_or_create_asset` réutilise tout asset déjà connu pour le
  même fichier (empreinte SHA-256 du contenu, pas seulement le chemin) — une même image
  sert à plusieurs `QuestionVersion` via `QuestionAsset`, jamais copiée.
- **Référence par ID** : une `QuestionVersion` pointe vers ses assets via `QuestionAsset`
  (`asset_id`), jamais via un chemin recopié dans `content_json`.
- **Signalement admin** : `mark_asset_incorrect` passe l'asset `INVALID` et peut
  enregistrer une demande de régénération. Une question dont la version courante utilise
  un asset non `ACTIVE` n'est plus servie (`unusable_asset_question_ids`), jusqu'au
  remplacement ou à la réactivation. Aucune validation manuelle n'est requise avant la
  première utilisation (un asset est `ACTIVE` dès sa création).
- **Régénération** (`regenerate_asset`) : uniquement pour un asset généré par IA dont le
  prompt est conservé. Jamais automatique : action manuelle
  (`python -m app.v1.assets regenerate`), comme `app.v1.fse01_image`. Le remplacement crée
  un NOUVEL asset et une nouvelle `QuestionVersion` par question concernée — l'ancien
  asset et les anciennes versions restent intacts pour la relecture des sessions passées.
"""

import argparse
import enum
import hashlib
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.v1.models import (
    Asset,
    AssetKind,
    AssetSourceType,
    ContentStatus,
    Question,
    QuestionAsset,
    QuestionVersion,
    add_question_version,
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
GENERATED_DIR = "img/assets/generated"


class AssetError(ValueError):
    """Asset incompatible avec le type de question, fichier absent, régénération
    impossible…"""


class VisualType(str, enum.Enum):
    PHOTO = "photo"
    ILLUSTRATION = "illustration"
    DIAGRAM = "diagram"


VISUAL_TYPE_LABELS = {
    VisualType.PHOTO: "Photo réelle",
    VisualType.ILLUSTRATION: "Illustration générée",
    VisualType.DIAGRAM: "Schéma technique",
}


@dataclass(frozen=True)
class AssetSpec:
    """Description déclarative d'un asset livré avec le code (fichier sous
    `app/static/`). `key` est un identifiant stable lisible (jamais affiché à l'élève)."""

    key: str
    storage_ref: str
    kind: AssetKind
    mime_type: str
    source_type: AssetSourceType
    visual_type: VisualType
    alt_text: str
    license: str
    provenance: str
    source_url: str | None = None
    author: str | None = None
    caption: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def static_path(storage_ref: str) -> Path:
    return STATIC_DIR / storage_ref


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def asset_metadata(asset: Asset) -> dict[str, Any]:
    return dict(asset.metadata_json or {})


def asset_visual_type(asset: Asset) -> VisualType | None:
    raw = asset_metadata(asset).get("visual_type")
    try:
        return VisualType(raw) if raw else None
    except ValueError:
        return None


def find_asset_by_sha256(db: Session, sha256: str) -> Asset | None:
    """Asset déjà connu pour ce contenu exact. Préfère un asset ACTIVE ; sinon le plus
    récent (un fichier marqué incorrect reste incorrect : jamais recréé « neuf » en
    silence). Filtre en Python sur `metadata_json` : volume V1 de quelques dizaines
    d'assets, pas d'index JSON nécessaire."""
    matches = [
        asset
        for asset in db.query(Asset).order_by(Asset.id.desc()).all()
        if asset_metadata(asset).get("sha256") == sha256
    ]
    for asset in matches:
        if asset.status == ContentStatus.ACTIVE:
            return asset
    return matches[0] if matches else None


def get_or_create_asset(db: Session, spec: AssetSpec) -> Asset:
    """Point d'entrée unique pour enregistrer un asset livré avec le code — idempotent
    et sans doublon (voir docstring du module)."""
    path = static_path(spec.storage_ref)
    if not path.is_file():
        raise AssetError(f"Fichier d'asset introuvable : {spec.storage_ref}")
    sha256 = file_sha256(path)
    existing = find_asset_by_sha256(db, sha256)
    if existing is not None:
        return existing
    metadata: dict[str, Any] = {
        "key": spec.key,
        "visual_type": spec.visual_type.value,
        "alt_text": spec.alt_text,
        "sha256": sha256,
    }
    if spec.author:
        metadata["author"] = spec.author
    if spec.caption:
        metadata["caption"] = spec.caption
    metadata.update(spec.extra)
    asset = Asset(
        kind=spec.kind,
        storage_ref=spec.storage_ref,
        mime_type=spec.mime_type,
        source_type=spec.source_type,
        source_url=spec.source_url,
        license=spec.license,
        provenance=spec.provenance,
        metadata_json=metadata,
        status=ContentStatus.ACTIVE,
    )
    db.add(asset)
    db.flush()
    return asset


def link_asset(db: Session, version: QuestionVersion, asset: Asset, *, role: str = "main") -> QuestionAsset:
    """Rattache `asset` à `version` en respectant le contrat d'assets du type de question
    (`AssetContract`, ticket #40). Idempotent."""
    from app.v1.question_engine import get_question_type

    contract = get_question_type(version.question_type).asset_contract
    if asset.kind not in contract.allowed_kinds:
        raise AssetError(
            f"Un asset {asset.kind.value} n'est pas accepté par le type {version.question_type}."
        )
    existing = (
        db.query(QuestionAsset)
        .filter_by(question_version_id=version.id, asset_id=asset.id, role=role)
        .one_or_none()
    )
    if existing is not None:
        return existing
    count = db.query(QuestionAsset).filter_by(question_version_id=version.id).count()
    if contract.max_assets and count >= contract.max_assets:
        raise AssetError(
            f"Le type {version.question_type} accepte au plus {contract.max_assets} asset(s)."
        )
    link = QuestionAsset(question_version_id=version.id, asset_id=asset.id, role=role)
    db.add(link)
    db.flush()
    return link


def assets_for_version(db: Session, version_id: int) -> list[Asset]:
    return (
        db.query(Asset)
        .join(QuestionAsset, QuestionAsset.asset_id == Asset.id)
        .filter(QuestionAsset.question_version_id == version_id)
        .order_by(QuestionAsset.id)
        .all()
    )


def assets_by_version(db: Session, version_ids: list[int]) -> dict[int, list[Asset]]:
    """Même chose que `assets_for_version` pour plusieurs versions en une requête
    (écran de résultats)."""
    if not version_ids:
        return {}
    rows = (
        db.query(QuestionAsset.question_version_id, Asset)
        .join(Asset, QuestionAsset.asset_id == Asset.id)
        .filter(QuestionAsset.question_version_id.in_(version_ids))
        .order_by(QuestionAsset.id)
        .all()
    )
    result: dict[int, list[Asset]] = {}
    for version_id, asset in rows:
        result.setdefault(version_id, []).append(asset)
    return result


def asset_url(asset: Asset) -> str | None:
    if asset.storage_ref:
        return f"/static/{asset.storage_ref}"
    return asset.source_url


def asset_display(asset: Asset) -> dict[str, Any]:
    """Données d'affichage (template) : jamais la clé interne ni l'empreinte."""
    metadata = asset_metadata(asset)
    visual_type = asset_visual_type(asset)
    return {
        "id": asset.id,
        "url": asset_url(asset),
        "alt": metadata.get("alt_text") or "Illustration de la question",
        "caption": metadata.get("caption"),
        "visual_type_label": VISUAL_TYPE_LABELS.get(visual_type, "Visuel") if visual_type else "Visuel",
        "author": metadata.get("author"),
        "license": asset.license,
        "source_url": asset.source_url,
        "provenance": asset.provenance,
        "usable": asset.status == ContentStatus.ACTIVE,
    }


def unusable_asset_question_ids(db: Session) -> set[int]:
    """Questions dont la VERSION COURANTE référence un asset non ACTIVE (marqué incorrect,
    archivé…) : à ne plus servir dans une nouvelle session. Les sessions déjà créées ne
    sont jamais modifiées."""
    rows = (
        db.query(Question.id)
        .join(QuestionAsset, QuestionAsset.question_version_id == Question.current_version_id)
        .join(Asset, Asset.id == QuestionAsset.asset_id)
        .filter(Asset.status != ContentStatus.ACTIVE)
        .distinct()
        .all()
    )
    return {row[0] for row in rows}


def questions_using_asset(db: Session, asset: Asset) -> list[Question]:
    """Questions dont la version COURANTE utilise `asset`."""
    return (
        db.query(Question)
        .join(QuestionAsset, QuestionAsset.question_version_id == Question.current_version_id)
        .filter(QuestionAsset.asset_id == asset.id)
        .order_by(Question.id)
        .all()
    )


def version_usage_count(db: Session, asset: Asset) -> int:
    """Nombre de QuestionVersion (toutes versions confondues) qui référencent `asset`."""
    return db.query(QuestionAsset).filter_by(asset_id=asset.id).count()


def can_regenerate(asset: Asset) -> bool:
    return asset.source_type == AssetSourceType.AI_GENERATED and bool(
        asset_metadata(asset).get("generation_prompt")
    )


def mark_asset_incorrect(
    db: Session, asset: Asset, *, reason: str = "", request_regeneration: bool = False
) -> None:
    metadata = asset_metadata(asset)
    metadata["flagged_at"] = datetime.now(UTC).isoformat()
    metadata["flag_reason"] = reason.strip()[:500]
    metadata["regeneration_requested"] = bool(request_regeneration)
    asset.metadata_json = metadata
    asset.status = ContentStatus.INVALID
    db.flush()


def reactivate_asset(db: Session, asset: Asset) -> None:
    metadata = asset_metadata(asset)
    metadata["regeneration_requested"] = False
    metadata["reactivated_at"] = datetime.now(UTC).isoformat()
    asset.metadata_json = metadata
    asset.status = ContentStatus.ACTIVE
    db.flush()


def pending_regeneration_assets(db: Session) -> list[Asset]:
    return [
        asset
        for asset in db.query(Asset).filter_by(status=ContentStatus.INVALID).order_by(Asset.id).all()
        if asset_metadata(asset).get("regeneration_requested")
    ]


def copy_asset_links(db: Session, source_version_id: int, target: QuestionVersion) -> None:
    """Reporte les visuels d'une version sur la nouvelle version d'une même question
    (édition admin = nouvelle version, ticket #46) : sans cela, une question visuelle
    modifiée perdrait son image."""
    links = (
        db.query(QuestionAsset)
        .filter_by(question_version_id=source_version_id)
        .order_by(QuestionAsset.id)
        .all()
    )
    for link in links:
        link_asset(db, target, db.get(Asset, link.asset_id), role=link.role)


def replace_asset(db: Session, old: Asset, new: Asset) -> list[QuestionVersion]:
    """Nouvelle `QuestionVersion` (même contenu) pour chaque question dont la version
    courante utilise `old`, rattachée à `new` à la place de `old` (les autres assets de la
    version sont conservés). Jamais de modification d'une version existante."""
    created: list[QuestionVersion] = []
    for question in questions_using_asset(db, old):
        current = question.current_version
        links = (
            db.query(QuestionAsset)
            .filter_by(question_version_id=current.id)
            .order_by(QuestionAsset.id)
            .all()
        )
        version = add_question_version(
            db,
            question,
            question_type=current.question_type,
            content_json=current.content_json,
            generator_model=current.generator_model,
            prompt_version=current.prompt_version,
            source_program_version=current.source_program_version,
            source_document_version_id=current.source_document_version_id,
        )
        for link in links:
            target = new if link.asset_id == old.id else db.get(Asset, link.asset_id)
            link_asset(db, version, target, role=link.role)
        created.append(version)
    metadata = asset_metadata(old)
    metadata["regeneration_requested"] = False
    metadata["replaced_by_asset_id"] = new.id
    old.metadata_json = metadata
    db.flush()
    return created


def regenerate_asset(db: Session, asset: Asset, image_provider, *, size: str = "1024x1024") -> Asset:
    """Régénère un asset IA à partir de son prompt conservé (au plus 2 tentatives, comme
    `app.v1.fse01_image`), enregistre le nouveau fichier et le nouvel asset, puis
    remplace l'ancien dans les questions concernées (`replace_asset`)."""
    from app.ai.provider import AIProviderError

    if not can_regenerate(asset):
        raise AssetError(
            "Régénération automatique impossible : seul un asset généré par IA avec son "
            "prompt conservé peut être régénéré (photo ou schéma : remplacement manuel)."
        )
    metadata = asset_metadata(asset)
    prompt = metadata["generation_prompt"]
    image_bytes: bytes | None = None
    last_error: Exception | None = None
    for _attempt in range(2):
        try:
            image_bytes = image_provider.generate_image(prompt=prompt, size=size, quality="high")
            break
        except AIProviderError as exc:
            last_error = exc
    if not image_bytes:
        raise AssetError(f"Échec de la génération après 2 tentatives : {last_error}")

    sha256 = hashlib.sha256(image_bytes).hexdigest()
    storage_ref = f"{GENERATED_DIR}/asset-{asset.id}-{sha256[:12]}.png"
    target = static_path(storage_ref)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(image_bytes)

    new_metadata = {
        key: metadata[key]
        for key in ("key", "visual_type", "alt_text", "caption", "generation_prompt")
        if key in metadata
    }
    new_metadata.update(
        {
            "sha256": sha256,
            "generation_model": getattr(image_provider, "_model", None),
            "generated_at": datetime.now(UTC).isoformat(),
            "replaces_asset_id": asset.id,
        }
    )
    new = Asset(
        kind=AssetKind.IMAGE,
        storage_ref=storage_ref,
        mime_type="image/png",
        source_type=AssetSourceType.AI_GENERATED,
        license=asset.license,
        provenance=f"Régénération IA de l'asset #{asset.id}",
        metadata_json=new_metadata,
        status=ContentStatus.ACTIVE,
    )
    db.add(new)
    db.flush()
    replace_asset(db, asset, new)
    return new


def main() -> None:
    parser = argparse.ArgumentParser(description="Assets visuels de la banque V1 (ticket #48).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list-pending", help="Liste les assets marqués incorrects avec régénération demandée.")
    regen = sub.add_parser("regenerate", help="Régénère les assets IA en attente (appel IA réel).")
    regen.add_argument("--asset-id", type=int, help="Limiter à un asset précis.")
    args = parser.parse_args()

    from app.database import SessionLocal

    db = SessionLocal()
    try:
        pending = pending_regeneration_assets(db)
        if args.command == "list-pending":
            for asset in pending:
                print(f"#{asset.id} {asset.storage_ref} régénérable={can_regenerate(asset)}")
            return
        from app.ai.factory import get_image_provider

        provider = get_image_provider()
        targets = [a for a in pending if args.asset_id in (None, a.id)]
        failures = 0
        for asset in targets:
            try:
                new = regenerate_asset(db, asset, provider)
                db.commit()
                print(f"Asset #{asset.id} remplacé par #{new.id} ({new.storage_ref})")
            except AssetError as exc:
                db.rollback()
                failures += 1
                print(f"Asset #{asset.id} : {exc}", file=sys.stderr)
        if failures:
            raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
