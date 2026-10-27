"""Présentation structurée des consignes d'examen AMPCR pratique (ticket #299).

Une question du parcours pratique est enregistrée avec une consigne d'une seule tenue
(`PR06Item.prompt` : « contexte À faire : 1) … 2) … »), transmise telle quelle à la
correction. Ce module décrit seulement comment la MONTRER : contexte, documents à consulter,
données et règles, questions numérotées, sous-questions.

Règles (même principe que `app.v1.document_layouts`, ticket #149) :
- **Structure explicite, jamais devinée.** Le découpage vient de la rédaction elle-même :
  `context` et `instructions` de l'exercice (`PR06Item`), retrouvé par le texte EXACT de la
  consigne enregistrée. Une consigne qui ne correspond à aucun exercice (autre matière,
  ancienne version) garde l'affichage d'origine. Aucune donnée en base n'est modifiée : une
  session en cours ou une copie rendue garde sa version de question, simplement mieux
  présentée.
- **Texte mot pour mot.** Les annotations (`ANNOTATIONS`) ne font que déplacer des extraits
  exacts : une phrase du contexte dans l'encadré « Données et règles », une consigne en
  phrase d'introduction + sous-questions. `validate_annotations` vérifie que chaque extrait
  existe et qu'une consigne découpée ne perd que des séparateurs (virgule, point-virgule,
  « et ») ; aucune information, contrainte, question ou indice n'est ajouté ni retiré.
- **Barème et correction inchangés** : la consigne enregistrée, le barème et le contenu
  envoyé au correcteur ne passent jamais par ce module.

Rendu : `app/templates/_prompt_layout.html`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(frozen=True)
class SubItems:
    """Une consigne présentée en phrase d'introduction + sous-questions (extraits exacts)."""

    lead: str
    items: tuple[str, ...]


@dataclass(frozen=True)
class Annotation:
    # Phrases exactes du contexte montrées dans l'encadré « Données et règles ».
    data_rules: tuple[str, ...] = ()
    # Numéro de consigne (1, 2…) → découpage en sous-questions.
    sub_items: dict[int, SubItems] = field(default_factory=dict)


@dataclass(frozen=True)
class Step:
    text: str
    lead: str = ""
    items: tuple[str, ...] = ()


@dataclass(frozen=True)
class PromptLayout:
    label: str  # « Partie 1 », « Dossier A »… ou ""
    context: str
    data_rules: tuple[str, ...]
    steps: tuple[Step, ...]


# Repère de partie en tête du contexte des examens blancs (« Partie 1. », « Dossier B. »).
_PART_RE = re.compile(r"^(Partie \d+|Dossier [A-Z])\.\s+")

# Ce qu'une consigne découpée peut perdre : séparateurs entre ses extraits.
_SEPARATORS_RE = re.compile(r"^(?:[\s,;:.]|\bet\b)*$")


ANNOTATIONS: dict[tuple[str, str], Annotation] = {
    ("EX01", "X01"): Annotation(
        sub_items={
            2: SubItems(
                lead="Indique sur quel repère tu branches ou installes :",
                items=(
                    "1) le câble 8 broches marqué « CPU » du bloc d'alimentation",
                    "2) le câble du ventilateur du ventirad",
                    "3) les fils du bouton marche de la façade",
                    "4) un SSD NVMe au format M.2 2280.",
                ),
            ),
        },
    ),
    ("EX01", "X06"): Annotation(
        data_rules=(
            "Le document B3 donne les puissances maximales des fiches, nouvelle carte graphique comprise.",
            ("Règle de l'atelier : bloc = total des fiches + 30 % de marge, arrondi au palier de 50 W supérieur, "
            "jamais sous la recommandation du fabricant de la carte graphique."),
        ),
    ),
    ("EX01", "X08"): Annotation(
        data_rules=(
            ("La fiche du processeur indique 100 °C au maximum ; convention de l'atelier : « à surveiller » à "
            "moins de 10 °C de ce maximum."),
        ),
    ),
    ("EX01", "X10"): Annotation(
        data_rules=(
            "La dernière sauvegarde date de trois semaines.",
            ("Règle de l'atelier : secteurs en attente ou illisibles supérieurs à 0 → disque à remplacer ; "
            "secteurs réalloués seuls → à surveiller."),
        ),
    ),
    ("EX02", "X01"): Annotation(
        data_rules=(
            ("Elle préfère Windows 11 quand c'est possible et utile, et accepte un autre système si un poste ne "
            "le permet pas."),
            ("Le relevé a été fait avec Informations système (msinfo32), la console TPM (tpm.msc) et Gestion des "
            "disques ; la liste de compatibilité citée est celle des processeurs publiée par Microsoft."),
        ),
    ),
    ("EX02", "X06"): Annotation(
        data_rules=("Tu utilises l'installation manuelle des partitions.",),
    ),
    ("EX03", "X01"): Annotation(
        data_rules=("La norme du client est T568B ; l'autre bout du cordon est correct.",),
    ),
    ("EX03", "X02"): Annotation(
        data_rules=(
            "Le stock contient des fiches RJ45, du câble Cat5e U/UTP multibrin et une pince à sertir.",
        ),
    ),
    ("EX04", "X02"): Annotation(
        data_rules=("La calculatrice est autorisée ; toute méthode juste est acceptée (binaire, taille de bloc…).",),
        sub_items={
            1: SubItems(
                lead="Pour chaque ligne a à d du document 3, donne",
                items=(
                    "le préfixe et le masque",
                    "l'adresse du réseau",
                    "l'adresse de diffusion",
                    "la plage des adresses d'hôtes",
                    "le nombre d'hôtes ;",
                    "détaille la méthode pour au moins une ligne.",
                ),
            ),
            4: SubItems(
                lead="Pour chaque valeur du document 4, dis si c'est une adresse MAC ou une adresse IPv4 et comment "
                "tu le reconnais ;",
                items=(
                    "pour une MAC, unicast ou groupe, fabricant ou administrée localement (bit utilisé) ;",
                    "pour une IPv4, son type.",
                ),
            ),
        },
    ),
}


def _remove(text: str, fragments: tuple[str, ...]) -> str:
    for fragment in fragments:
        text = text.replace(fragment, " ")
    return re.sub(r"\s+", " ", text).strip()


def _residual(text: str, parts: tuple[str, ...]) -> str | None:
    """Ce qui reste de `text` une fois ses extraits retirés dans l'ordre (None : extrait
    absent ou hors ordre)."""
    rest, position = [], 0
    for part in parts:
        index = text.find(part, position)
        if index < 0:
            return None
        rest.append(text[position:index])
        position = index + len(part)
    rest.append(text[position:])
    return " ".join(rest)


def _items_by_prompt() -> dict[str, tuple[str, object]]:
    from app.v1.ampcr_pratique_bank import PRACTICAL_COURSES

    return {item.prompt: (course.code, item) for course in PRACTICAL_COURSES for item in course.items}


@lru_cache(maxsize=1)
def _index() -> dict[str, tuple[str, object]]:
    return _items_by_prompt()


def layout_for_item(code: str, item) -> PromptLayout:
    annotation = ANNOTATIONS.get((code, item.key), Annotation())
    context = item.context
    label = ""
    match = _PART_RE.match(context) if code.startswith("EX") else None
    if match:
        label, context = match.group(1), context[match.end():]
    steps = []
    for number, text in enumerate(item.instructions, start=1):
        split = annotation.sub_items.get(number)
        steps.append(Step(text=text, lead=split.lead, items=split.items) if split else Step(text=text))
    return PromptLayout(
        label=label,
        context=_remove(context, annotation.data_rules),
        data_rules=annotation.data_rules,
        steps=tuple(steps),
    )


def prompt_layout(prompt: str | None) -> PromptLayout | None:
    """Présentation structurée d'une consigne enregistrée, ou None (affichage d'origine)."""
    found = _index().get(prompt or "")
    return layout_for_item(*found) if found else None


def validate_annotations() -> list[str]:
    from app.v1.ampcr_pratique_bank import PRACTICAL_COURSES_BY_CODE

    errors = []
    for (code, key), annotation in ANNOTATIONS.items():
        course = PRACTICAL_COURSES_BY_CODE.get(code)
        item = next((i for i in course.items if i.key == key), None) if course else None
        if item is None:
            errors.append(f"{code} {key} : exercice inconnu.")
            continue
        for rule in annotation.data_rules:
            if rule not in item.context:
                errors.append(f"{code} {key} : donnée absente du contexte : {rule!r}.")
        for number, split in annotation.sub_items.items():
            if not 1 <= number <= len(item.instructions):
                errors.append(f"{code} {key} : consigne {number} inexistante.")
                continue
            rest = _residual(item.instructions[number - 1], (split.lead, *split.items))
            if rest is None or not _SEPARATORS_RE.match(rest):
                errors.append(f"{code} {key} : consigne {number} mal découpée (reste : {rest!r}).")
    return errors
