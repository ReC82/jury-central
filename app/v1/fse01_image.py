"""Génération et conservation durable de l'illustration de l'affiche de sécurité routière
(FSE01, ticket #108 § 4).

Principes stricts imposés par le ticket :
- **Aucun appel API à l'ouverture du cours** : l'image est un fichier statique
  (`app/static/img/fse01_affiche_securite_routiere.png`), servi tel quel comme n'importe
  quel autre asset — jamais générée à la demande dans une route.
- **Aucune régénération automatique au seed ou au déploiement** : `generate_and_save_poster_image()`
  n'est appelée par aucun code de démarrage, de seed ou de déploiement. C'est une action
  déclenchée à la main, via la commande `generate-fse01-poster-image` (voir
  `pyproject.toml`, `[project.scripts]`) — `--force` pour un remplacement volontaire.
- **Au maximum une seconde tentative** : une erreur technique (réseau, timeout, modération,
  format de réponse) déclenche une nouvelle tentative, jamais plus. Il n'existe aucun moyen
  automatique de juger qu'une image générée avec succès serait « inutilisable » sur le plan
  esthétique — un tel jugement reste humain, via `--force` après inspection manuelle.
- **Prompt et modèle conservés durablement**, pas seulement dans ce fichier : un fichier de
  métadonnées sidecar (`fse01_affiche_securite_routiere.json`) accompagne l'image, avec le
  prompt exact, le modèle et l'horodatage de génération — pour audit et reproductibilité.
- **Échec sans casser le cours** : si la génération échoue (clé absente, erreur API, 2
  tentatives épuisées), cette fonction retourne `None` sans lever et sans écrire de fichier
  partiel — `app/v1/fse01_content.py` affiche alors un rendu de secours en CSS pur (voir
  `FSE01_AFFICHE_CARD_HTML`), jamais une image cassée ni un faux succès."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.ai.factory import get_image_provider
from app.ai.provider import AIProviderError
from app.config import settings

IMG_DIR = Path(__file__).resolve().parent.parent / "static" / "img"
IMAGE_PATH = IMG_DIR / "fse01_affiche_securite_routiere.png"
METADATA_PATH = IMG_DIR / "fse01_affiche_securite_routiere.json"

# Conservé ici ET dans le fichier sidecar généré à côté de l'image (voir docstring) : un
# futur remplacement manuel doit pouvoir repartir de ce prompt sans deviner son contenu.
FSE01_POSTER_PROMPT = (
    "Flat, clean pedagogical illustration for a Belgian road-safety awareness poster. "
    "Scene: a simplified street crosswalk, a stylized child silhouette crossing, a car "
    "silhouette slowing down in the background. Dominant colors: red and white, with "
    "muted neutral tones, minimal flat vector illustration style, clearly schematic and "
    "non-photorealistic silhouettes (no realistic faces). No text, no lettering, no "
    "logos, no brand marks anywhere in the image — all text and logos are added "
    "separately as HTML overlay. Wide poster composition, portrait orientation, plenty "
    "of empty space at the top and bottom for text to be overlaid later."
)
FSE01_POSTER_SIZE = "1024x1536"
FSE01_POSTER_QUALITY = "high"


def generate_and_save_poster_image(force: bool = False) -> Path | None:
    """Voir docstring du module. Ne lève jamais : retourne le chemin existant (sans appel
    API) si l'image est déjà présente et `force` est faux, le chemin nouvellement écrit en
    cas de succès, ou `None` si la génération a échoué après au maximum 2 tentatives."""
    if IMAGE_PATH.exists() and not force:
        return IMAGE_PATH

    provider = get_image_provider()
    image_bytes: bytes | None = None
    last_error: Exception | None = None
    for _attempt in range(2):
        try:
            image_bytes = provider.generate_image(
                prompt=FSE01_POSTER_PROMPT,
                size=FSE01_POSTER_SIZE,
                quality=FSE01_POSTER_QUALITY,
            )
            break
        except AIProviderError as exc:
            last_error = exc
            image_bytes = None

    if image_bytes is None:
        print(
            f"Échec de la génération de l'illustration après 2 tentative(s) : {last_error}",
            file=sys.stderr,
        )
        return None

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_PATH.write_bytes(image_bytes)
    METADATA_PATH.write_text(
        json.dumps(
            {
                "prompt": FSE01_POSTER_PROMPT,
                "model": settings.openai_image_model,
                "size": FSE01_POSTER_SIZE,
                "quality": FSE01_POSTER_QUALITY,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return IMAGE_PATH


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Génère (ou régénère avec --force) l'illustration de l'affiche FSE01. "
            "Ne fait rien si l'image existe déjà et que --force n'est pas passé."
        )
    )
    parser.add_argument(
        "--force", action="store_true", help="Régénère même si l'image existe déjà."
    )
    args = parser.parse_args()
    result = generate_and_save_poster_image(force=args.force)
    if result is None:
        print("Aucune image générée — le cours utilisera le rendu de secours (CSS).")
        raise SystemExit(1)
    print(f"Image enregistrée : {result}")
    print(f"Métadonnées : {METADATA_PATH}")


if __name__ == "__main__":
    main()
