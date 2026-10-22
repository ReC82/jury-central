"""Génération et conservation durable des deux illustrations de Sophie Lambert (FSE03,
ticket #118) : un portrait professionnel et une scène d'anniversaire — même personnage,
même apparence dans les deux images.

Mêmes principes stricts que `app.v1.fse01_image` (ticket #108 § 4), avec une étape
supplémentaire pour la cohérence du personnage :

- **Aucun appel API à l'ouverture du cours ni au seed/déploiement** : les images sont des
  fichiers statiques (`app/static/img/fse03_sophie_portrait.png`,
  `fse03_sophie_birthday.png`), générées une seule fois via la commande dédiée
  `generate-fse03-sophie-images` (voir `pyproject.toml`), jamais à la demande.
- **Cohérence du personnage entre les deux images** : le portrait est généré une première
  fois (`POST /v1/images/generations`), puis réutilisé comme IMAGE DE RÉFÉRENCE pour
  générer la scène d'anniversaire via `POST /v1/images/edits` (`ImageProvider.edit_image`,
  `input_fidelity="high"`) — le modèle reçoit réellement le portrait en entrée et doit
  reproduire la même personne dans une nouvelle scène, plutôt que deux générations
  indépendantes à partir du seul texte (qui produiraient presque certainement deux
  apparences différentes). Voir docs/components/DialogueComponents.md pour la discussion
  de cette technique.
- **Au maximum une seconde tentative, par image** : une erreur technique déclenche une
  nouvelle tentative, jamais plus, pour le portrait comme pour la scène d'anniversaire.
- **Prompt et modèle conservés durablement** dans un fichier de métadonnées sidecar par
  image.
- **Échec sans casser le cours** : si le portrait échoue, la scène d'anniversaire n'est
  même pas tentée (elle en dépend) ; dans les deux cas, `app/v1/fse03_content.py` bascule
  sur un rendu de secours en CSS/SVG pur si le fichier correspondant est absent."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.ai.factory import get_image_provider
from app.ai.provider import AIProviderError
from app.config import settings

IMG_DIR = Path(__file__).resolve().parent.parent / "static" / "img"
PORTRAIT_IMAGE_PATH = IMG_DIR / "fse03_sophie_portrait.png"
PORTRAIT_METADATA_PATH = IMG_DIR / "fse03_sophie_portrait.json"
BIRTHDAY_IMAGE_PATH = IMG_DIR / "fse03_sophie_birthday.png"
BIRTHDAY_METADATA_PATH = IMG_DIR / "fse03_sophie_birthday.json"

# Description de personnage détaillée et réutilisée mot pour mot dans le prompt de la
# scène d'anniversaire (en plus de l'image de référence elle-même) : une double garantie
# de cohérence (conditionnement par l'image ET par le texte).
_SOPHIE_DESCRIPTION = (
    "a woman in her early thirties with shoulder-length straight dark brown hair, "
    "warm medium skin tone, a friendly confident expression"
)

FSE03_PORTRAIT_PROMPT = (
    f"Flat vector illustration, professional profile picture style, of {_SOPHIE_DESCRIPTION}, "
    "wearing a teal blazer over a plain white top, looking directly at the viewer with a "
    "warm smile. Head-and-shoulders composition, centered, plain soft blue-grey background, "
    "clean minimal flat design, soft rounded shapes, even lighting. No text, no logos, no "
    "watermarks. Clearly an illustrated character, not photorealistic, no realistic skin "
    "texture or photographic detail."
)
FSE03_PORTRAIT_SIZE = "1024x1024"
FSE03_PORTRAIT_QUALITY = "high"

FSE03_BIRTHDAY_PROMPT = (
    f"Using the exact same woman shown in the reference image ({_SOPHIE_DESCRIPTION}, same "
    "hair, same face, same skin tone — keep her appearance identical to the reference), "
    "create a new flat vector illustration scene: she is laughing at an outdoor birthday "
    "celebration with two friends standing beside her, string lights and a small birthday "
    "cake with candles visible in the background, warm pastel color palette, early evening "
    "setting. Same clean flat minimal illustration style as the reference image, soft "
    "rounded shapes, no text, no logos, no watermarks, not photorealistic."
)
FSE03_BIRTHDAY_SIZE = "1024x1024"
FSE03_BIRTHDAY_QUALITY = "high"

# `input_fidelity` vérifié empiriquement (ticket #118) : ni "gpt-image-2.5-flare" ni
# "gpt-image-2.5-sunburst" ne l'acceptent sur ce compte à cette date (erreur
# `invalid_input_fidelity_model` dans les deux cas, malgré la documentation officielle
# mentionnant ce paramètre) — omis (`None`). La cohérence du personnage repose donc
# uniquement sur l'image de référence transmise à `/v1/images/edits` (vérifiée
# suffisante par un test empirique préalable : une forme de référence est correctement
# conservée et complétée) et sur la description textuelle répétée dans le prompt.
FSE03_BIRTHDAY_INPUT_FIDELITY = None


def _write_metadata(path: Path, prompt: str, size: str, quality: str, extra: dict | None = None) -> None:
    payload = {
        "prompt": prompt,
        "model": settings.openai_image_model,
        "size": size,
        "quality": quality,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        payload.update(extra)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _generate_with_retry(call, *, label: str) -> bytes | None:
    """Au maximum 2 tentatives (ticket #108/#118) ; retourne None sans lever en cas
    d'échec total, pour laisser l'appelant décider du repli."""
    last_error: Exception | None = None
    for _attempt in range(2):
        try:
            return call()
        except AIProviderError as exc:
            last_error = exc
    print(f"Échec de la génération ({label}) après 2 tentative(s) : {last_error}", file=sys.stderr)
    return None


def generate_and_save_sophie_images(force: bool = False) -> tuple[Path | None, Path | None]:
    """Voir docstring du module. Ne lève jamais. Retourne (chemin_portrait, chemin_anniversaire),
    chacun `None` si la génération correspondante a échoué (ou n'a pas pu être tentée, pour
    l'anniversaire si le portrait manque)."""
    portrait_exists = PORTRAIT_IMAGE_PATH.exists() and not force
    birthday_exists = BIRTHDAY_IMAGE_PATH.exists() and not force

    if portrait_exists and birthday_exists:
        return PORTRAIT_IMAGE_PATH, BIRTHDAY_IMAGE_PATH

    provider = get_image_provider()
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    portrait_path: Path | None = PORTRAIT_IMAGE_PATH if portrait_exists else None
    portrait_bytes: bytes | None = None

    if not portrait_exists:
        portrait_bytes = _generate_with_retry(
            lambda: provider.generate_image(
                prompt=FSE03_PORTRAIT_PROMPT,
                size=FSE03_PORTRAIT_SIZE,
                quality=FSE03_PORTRAIT_QUALITY,
            ),
            label="portrait de Sophie",
        )
        if portrait_bytes is not None:
            PORTRAIT_IMAGE_PATH.write_bytes(portrait_bytes)
            _write_metadata(
                PORTRAIT_METADATA_PATH, FSE03_PORTRAIT_PROMPT, FSE03_PORTRAIT_SIZE, FSE03_PORTRAIT_QUALITY
            )
            portrait_path = PORTRAIT_IMAGE_PATH
    elif not birthday_exists:
        # Le portrait existe déjà mais pas la scène d'anniversaire (ex. --force partiel
        # ou échec précédent) : on le relit du disque pour servir de référence.
        portrait_bytes = PORTRAIT_IMAGE_PATH.read_bytes()

    birthday_path: Path | None = BIRTHDAY_IMAGE_PATH if birthday_exists else None
    if not birthday_exists and portrait_bytes is not None:
        birthday_bytes = _generate_with_retry(
            lambda: provider.edit_image(
                prompt=FSE03_BIRTHDAY_PROMPT,
                reference_images=[portrait_bytes],
                size=FSE03_BIRTHDAY_SIZE,
                quality=FSE03_BIRTHDAY_QUALITY,
                input_fidelity=FSE03_BIRTHDAY_INPUT_FIDELITY,
            ),
            label="scène d'anniversaire de Sophie",
        )
        if birthday_bytes is not None:
            BIRTHDAY_IMAGE_PATH.write_bytes(birthday_bytes)
            _write_metadata(
                BIRTHDAY_METADATA_PATH,
                FSE03_BIRTHDAY_PROMPT,
                FSE03_BIRTHDAY_SIZE,
                FSE03_BIRTHDAY_QUALITY,
                extra={
                    "reference_image": str(PORTRAIT_IMAGE_PATH.name),
                    "input_fidelity": FSE03_BIRTHDAY_INPUT_FIDELITY,
                },
            )
            birthday_path = BIRTHDAY_IMAGE_PATH
    elif not birthday_exists:
        print(
            "Scène d'anniversaire non générée : le portrait de référence est manquant.",
            file=sys.stderr,
        )

    return portrait_path, birthday_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Génère (ou régénère avec --force) le portrait et la scène d'anniversaire de "
            "Sophie Lambert (FSE03). Ne fait rien pour une image déjà existante si "
            "--force n'est pas passé."
        )
    )
    parser.add_argument(
        "--force", action="store_true", help="Régénère même si les images existent déjà."
    )
    args = parser.parse_args()
    portrait_path, birthday_path = generate_and_save_sophie_images(force=args.force)

    if portrait_path is None:
        print("Échec : aucun portrait généré — la scène d'anniversaire n'a pas pu être tentée.")
        raise SystemExit(1)
    print(f"Portrait enregistré : {portrait_path}")

    if birthday_path is None:
        print("Échec : scène d'anniversaire non générée (voir message d'erreur ci-dessus).")
        raise SystemExit(1)
    print(f"Scène d'anniversaire enregistrée : {birthday_path}")


if __name__ == "__main__":
    main()
