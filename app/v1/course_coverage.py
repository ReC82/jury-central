"""Garde d'alignement cours ↔ questions (ticket #83) : une question ne peut interroger
sur la signification d'un acronyme/abréviation que si ce dernier est réellement expliqué
dans le cours du mini-cours (MC) concerné — ou dans le lexique AMPCR transverse (ticket
#84, voir `app.v1.lexicon`, branché en § F ci-dessous).

Cas réel ayant motivé ce ticket : la question « Que signifie l'acronyme SMART ? » a été
posée alors que MC04 utilisait SMART comme indicateur de santé du disque sans jamais
donner son développé (« Self-Monitoring, Analysis and Reporting Technology ») — corrigé
dans le contenu (voir MC04, § 83.C), mais rien n'empêchait techniquement qu'un cas
similaire se reproduise sur un autre acronyme/MC. Cette garde ferme le risque
structurellement, sans dépendre d'un futur audit manuel à chaque nouveau contenu.

Portée volontairement bornée (§ 83.B du ticket, pas de NLP complexe) : cette garde ne
juge PAS la difficulté générale d'une question, seulement le cas concret et détectable
sans ambiguïté « la question demande le développé d'un acronyme » — repérée par un motif
de formulation typique (« que signifie X », « que veut dire X », « que représente
l'acronyme X »...), jamais une compréhension sémantique complète de l'énoncé.
"""

import re
from typing import Any

from app.v1.ampcr_courses import AMPCR_COURSE_MARKDOWN

# --- Extraction des notions réellement expliquées dans un cours -----------------------------
#
# Convention d'écriture observée dans TOUT app/v1/ampcr_courses.py (audit § 83.A) : un
# acronyme expliqué apparaît soit en gras suivi d'une parenthèse de développé
# (« **SMART** (*Self-Monitoring...*) », « **BIOS** (Basic Input/Output System) »), soit en
# gras suivi d'un deux-points de définition (« **Modèle OSI** : 7 couches... »). Les deux
# formes comptent comme « expliqué dans le cours ».

_BOLD_TERM_RE = re.compile(r"\*\*([^*\n]{1,40})\*\*")
_PAREN_ACRONYM_RE = re.compile(r"\b([A-Z]{2,8})\s*\(")


def _extract_defined_notions(course_markdown: str) -> frozenset[str]:
    """Notions (acronymes/termes) considérés comme réellement expliqués dans un texte de
    cours — détection structurelle (regex), jamais un jugement sémantique."""
    notions: set[str] = set()
    for match in _BOLD_TERM_RE.findall(course_markdown):
        # Un terme en gras peut contenir plusieurs mots (« Modèle OSI », « Partition EFI ») —
        # chaque mot tout-en-majuscules qui le compose est une notion couverte à part
        # entière, pour que « OSI » ressorte de « **Modèle OSI** » sans exiger que le gras
        # soit réduit au seul acronyme.
        for word in match.split():
            cleaned = word.strip(".,;:()/")
            if len(cleaned) >= 2 and cleaned.upper() == cleaned:
                notions.add(cleaned)
        cleaned_full = match.strip()
        if cleaned_full:
            notions.add(cleaned_full)
    notions.update(_PAREN_ACRONYM_RE.findall(course_markdown))
    return frozenset(notions)


_DEFINED_NOTIONS_BY_CODE: dict[str, frozenset[str]] = {
    code: _extract_defined_notions(markdown) for code, markdown in AMPCR_COURSE_MARKDOWN.items()
}


def _lexicon_defined_notions() -> frozenset[str]:
    """Notions couvertes par le lexique AMPCR transverse (ticket #84 § F) : une ressource
    pédagogique autorisée au même titre qu'un cours de MC — importé ici en différé (pas au
    niveau module) pour ne jamais dépendre de l'ordre de chargement entre `course_coverage`
    et `lexicon`."""
    try:
        from app.v1.lexicon import lexicon_defined_notions
    except ImportError:
        return frozenset()
    return lexicon_defined_notions()


def defined_notions_for_code(code: str | None) -> frozenset[str]:
    """Notions autorisées pour un MC donné : celles de son propre cours + celles du
    lexique transverse (#84 § F). `code=None` (question hors MC, ex. transversale sans
    UAA) : seul le lexique s'applique."""
    course_notions = _DEFINED_NOTIONS_BY_CODE.get(code, frozenset()) if code else frozenset()
    return course_notions | _lexicon_defined_notions()


# --- Détection des questions qui demandent le développé d'un acronyme -----------------------

_ACRONYM_QUESTION_RE = re.compile(
    r"(?:que\s+(?:signifie|veut\s+dire|repr[ée]sente)|signification\s+de|d[ée]veloppe(?:r)?\s+l['’]acronyme)"
    r"\s+(?:l['’]acronyme\s+|l['’]abr[ée]viation\s+)?[«\"']?([A-Z][A-Z0-9./]{1,8})\b",
    re.IGNORECASE,
)

# Notions dont la signification est un savoir de base (pas une notion « enseignée » par un
# MC spécifique) — jamais bloquées par cette garde, quel que soit le cours. Volontairement
# minimal (§ 83.B : pas de liste blanche extensive qui viderait la garde de son sens).
_ALWAYS_ALLOWED = frozenset({"PC"})


def _prompt_of(content: dict[str, Any]) -> str:
    return str(content.get("prompt", "")) if isinstance(content, dict) else ""


def check_course_coverage_gap(
    module: Any, uaa: Any, question_type: str, content_json: dict[str, Any]
) -> list[str]:
    """Point d'entrée (§ 83.B), même registre que `app.v1.quality_validation` et
    `app.v1.domain_validation`. Rejette toute question qui demande le développé d'un
    acronyme non expliqué dans le cours du MC concerné ni dans le lexique AMPCR — la
    question n'est alors ni persistée ni utilisée (COURSE_COVERAGE_GAP)."""
    if not isinstance(content_json, dict):
        return []
    prompt = _prompt_of(content_json)
    if not prompt:
        return []

    uaa_code = getattr(uaa, "code", None)
    allowed = defined_notions_for_code(uaa_code) | _ALWAYS_ALLOWED

    errors: list[str] = []
    for acronym in _ACRONYM_QUESTION_RE.findall(prompt):
        acronym_upper = acronym.upper()
        if acronym_upper in allowed:
            continue
        errors.append(
            f"COURSE_COVERAGE_GAP: la question interroge sur la signification de "
            f"« {acronym} », jamais expliquée dans le cours {uaa_code or '(sans MC)'} ni "
            "dans le lexique AMPCR — une question ne peut porter que sur une notion "
            "réellement enseignée."
        )
    return errors
