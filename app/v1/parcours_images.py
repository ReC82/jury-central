"""Illustrations du parcours (ticket #136) : accueil + une par matière du parcours AMPCR.

Mêmes principes que `app.v1.fse01_image` (ticket #108) :
- **aucun appel API à la consultation** : fichiers statiques sous `app/static/img/parcours/`,
  commités et servis tels quels ; les templates retombent sur une icône si un fichier
  manque (`static_exists`) — jamais une image cassée ;
- **génération manuelle uniquement** (`generate-parcours-images`), jamais au seed ni au
  démarrage ; une image existante n'est jamais régénérée sans `--force` ;
- **au maximum 2 tentatives par image**, puis abandon propre ; un solde/quota insuffisant
  ou une clé refusée est signalé explicitement et arrête la série (pas de boucle) ;
- **prompt, modèle et date conservés** dans un fichier `.json` à côté de chaque image ;
- **poids maîtrisé** : la sortie PNG de l'API est recadrée au ratio d'affichage puis
  convertie en WebP (Pillow) à une largeur raisonnable — pas d'image géante.

Dessins plats, sans texte (le texte exact reste en HTML), sans visage réaliste."""

import argparse
import io
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.ai.factory import get_image_provider
from app.ai.provider import AIProviderError
from app.config import settings

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "static" / "img" / "parcours"

STYLE = (
    "Warm, modern flat vector illustration for an adult-friendly educational web app "
    "(learners aged 16 to 50 preparing a Belgian secondary-school diploma exam). Soft "
    "rounded shapes, gentle gradients, limited palette of indigo, violet, warm peach and "
    "off-white with one accent colour, light paper-like background, generous empty space. "
    "Friendly and calm, not childish, no cartoon mascots. Simplified stylized people "
    "without detailed faces. Absolutely no text, letters, numbers, logos or brand marks."
)


@dataclass(frozen=True)
class IllustrationSpec:
    name: str
    subject: str
    ratio: tuple[int, int]
    width: int


SPECS = (
    IllustrationSpec(
        "accueil",
        "A winding path with milestone flags climbing gently across rolling hills toward a "
        "graduation cap on the horizon; along the path, floating icons-like objects: an "
        "open book, a laptop, a speech bubble, a small trophy. Two adult learners of "
        "different ages walking the path together, seen from behind.",
        (3, 2),
        1200,
    ),
    IllustrationSpec(
        "informatique",
        "A tidy workbench with an open desktop PC tower showing motherboard, RAM sticks "
        "and fans, a network switch with a few coloured cables, a screwdriver and an "
        "anti-static wrist strap; a technician's hands assembling a component.",
        (16, 9),
        960,
    ),
    IllustrationSpec(
        "francais",
        "A calm reading and writing desk: an open book, a printed article with highlighted "
        "lines, a notebook with handwriting-like squiggles (no readable letters), a pen and "
        "a cup of tea, soft window light.",
        (16, 9),
        960,
    ),
    IllustrationSpec(
        "fse",
        "Society and media: a stylized town square with a public building with columns, a "
        "few diverse people talking, a smartphone and a newspaper, speech bubbles without "
        "text, a ballot box suggesting citizenship.",
        (16, 9),
        960,
    ),
)

API_SIZE = "1536x1024"
API_QUALITY = "medium"


def _fatal_reason(error: Exception) -> str | None:
    """Erreurs qui touchent toute la série (inutile de réessayer ni de continuer)."""
    text = str(error).lower()
    if any(k in text for k in ("insufficient_quota", "billing", "quota", "statut 402")):
        return "Solde ou quota OpenAI insuffisant"
    if "invalid_api_key" in text or "statut 401" in text:
        return "Clé API OpenAI absente ou refusée"
    return None


def _to_webp(png_bytes: bytes, ratio: tuple[int, int], width: int) -> bytes:
    from PIL import Image  # disponible dans l'environnement serveur (outil manuel)

    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    target = ratio[0] / ratio[1]
    w, h = image.size
    if w / h > target:  # trop large : recadrage horizontal centré
        new_w = int(h * target)
        image = image.crop(((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h))
    else:
        new_h = int(w / target)
        image = image.crop((0, (h - new_h) // 2, w, (h - new_h) // 2 + new_h))
    image = image.resize((width, int(width / target)), Image.LANCZOS)
    out = io.BytesIO()
    image.save(out, format="WEBP", quality=80, method=6)
    return out.getvalue()


def generate(output_dir: Path, *, force: bool = False, only: set[str] | None = None) -> int:
    """Génère les illustrations manquantes. Retourne le nombre d'échecs (0 = tout bon)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    provider = get_image_provider()
    failures = 0
    for spec in SPECS:
        if only and spec.name not in only:
            continue
        target = output_dir / f"{spec.name}.webp"
        if target.exists() and not force:
            print(f"{spec.name} : déjà présente, ignorée (--force pour remplacer)")
            continue
        prompt = f"{STYLE} Scene: {spec.subject}"
        png: bytes | None = None
        for _attempt in range(2):
            try:
                png = provider.generate_image(prompt=prompt, size=API_SIZE, quality=API_QUALITY)
                break
            except AIProviderError as exc:
                reason = _fatal_reason(exc)
                if reason:
                    print(
                        f"{reason} — génération arrêtée, aucune image partielle écrite.",
                        file=sys.stderr,
                    )
                    return failures + 1
                print(f"{spec.name} : échec ({exc})", file=sys.stderr)
        if png is None:
            failures += 1
            continue
        target.write_bytes(_to_webp(png, spec.ratio, spec.width))
        (output_dir / f"{spec.name}.json").write_text(
            json.dumps(
                {
                    "prompt": prompt,
                    "model": settings.openai_image_model,
                    "api_size": API_SIZE,
                    "quality": API_QUALITY,
                    "output": {"format": "webp", "ratio": spec.ratio, "width": spec.width},
                    "generated_at": datetime.now(UTC).isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"{spec.name} : enregistrée ({target.stat().st_size // 1024} Ko)")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Illustrations du parcours (ticket #136).")
    parser.add_argument("--force", action="store_true", help="Régénère même si présente.")
    parser.add_argument("--only", nargs="*", help="Noms à générer (accueil, informatique…).")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    failures = generate(args.output_dir, force=args.force, only=set(args.only or []) or None)
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
