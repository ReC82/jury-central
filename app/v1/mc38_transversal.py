"""MC38 — révision finale et examen blanc transversal (ticket #58).

Correctif du bug bloquant constaté en validation : MC38 générait des questions MÉTA sur
le processus de révision lui-même (« quel est l'objectif d'une révision finale ? »,
« que faire après avoir corrigé un exercice ? »...) au lieu de vraies questions
d'informatique AMPCR, parce que la génération utilisait le propre contexte pédagogique de
MC38 (dont l'objectif du plan — « synthèse, fiches mémo, pièges, exercices transversaux et
examen type qualification » — invite justement l'IA à parler DE la révision plutôt qu'À
partir du contenu technique réel).

Ce module fournit :
- `MC38_CODE` / `mc01_to_mc37_codes()` : le périmètre réel de MC38 (MC01→MC37, jamais
  MC38 lui-même comme sujet).
- `pick_transversal_contexts()` : un échantillon de contextes pédagogiques MC01→MC37,
  diversifié par catégorie (§ 6 du ticket #58 : « plusieurs catégories obligatoires »),
  à transmettre à `generate_questionnaire` (qui accepte déjà plusieurs contextes, ticket
  #23) — jamais le contexte MC38 lui-même.
- `is_meta_revision_question()` : garde de contenu ciblant le SENS méta (réviser,
  mémoriser, fiche mémo, après correction...), pas une liste noire naïve de mots isolés
  (ne bloque jamais le mot « examen » seul, qui apparaît légitimement dans de vraies
  questions techniques)."""

import random
import re

from app.ai.schemas import PedagogicalContext
from app.v1.ampcr_plan import AMPCR_CONTEXTS, AMPCR_PLAN

MC38_CODE = "MC38"

# Marqueur stocké dans `QuestionnaireSession.parameters_json` (colonne JSON déjà présente,
# jamais utilisée avant ce ticket — aucune migration de schéma nécessaire) pour repérer
# une session MC38 sans dépendre de `SessionQuestion.uaa_id` : ses questions appartiennent
# à MC01→MC37, jamais à MC38 lui-même, donc un simple `uaa_id == mc38.id` ne matcherait
# jamais (voir `app.v1.session_service.get_in_progress_session`).
MC38_SESSION_SCOPE = "mc38"

# Nombre de contextes distincts transmis à un seul appel de génération transversale —
# borné pour garder un prompt raisonnable (voir app/ai/prompts.py::_questionnaire_context_block,
# qui numérote déjà chaque contexte fourni, aucune modification nécessaire côté #23).
DEFAULT_TRANSVERSAL_CONTEXT_COUNT = 6


def mc01_to_mc37_codes() -> list[str]:
    """Les 37 mini-cours réels qui composent le périmètre de MC38 — jamais MC38
    lui-même (qui n'est pas une matière, voir docstring du module)."""
    return [plan.code for plan in AMPCR_PLAN if plan.code != MC38_CODE]


def pick_transversal_contexts(count: int = DEFAULT_TRANSVERSAL_CONTEXT_COUNT) -> tuple[PedagogicalContext, ...]:
    """Échantillon de contextes MC01→MC37, diversifié par catégorie (round-robin, comme
    `app.v1.session_service.compose_selection`) : borne réellement l'IA au contenu
    technique existant, jamais au sujet « comment réviser » de MC38 lui-même."""
    by_category: dict[str, list[str]] = {}
    for plan in AMPCR_PLAN:
        if plan.code == MC38_CODE:
            continue
        by_category.setdefault(plan.category, []).append(plan.code)
    for codes in by_category.values():
        random.shuffle(codes)

    categories = list(by_category.keys())
    random.shuffle(categories)

    selected_codes: list[str] = []
    progressed = True
    while len(selected_codes) < count and progressed:
        progressed = False
        for category in categories:
            if len(selected_codes) >= count:
                break
            bucket = by_category[category]
            if bucket:
                selected_codes.append(bucket.pop())
                progressed = True

    course_keys = [f"ampcr-{code.lower()}" for code in selected_codes]
    return tuple(AMPCR_CONTEXTS[key] for key in course_keys if key in AMPCR_CONTEXTS)


# Motifs ciblant le SENS méta (le processus de révision/examen lui-même), jamais un mot
# isolé trop générique — voir § 8 du ticket #58 : « ne pas interdire le mot examen partout
# si une vraie question technique le contient ». Chaque motif reprend directement un des
# exemples interdits fournis par le ticket, ou son équivalent sémantique direct.
_META_REVISION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"objectif\w*.{0,40}(r[ée]vision|r[ée]viser)",
        r"(r[ée]vision|r[ée]viser).{0,40}objectif\w*",
        r"fiches?\s+m[ée]mo",
        r"m[ée]moris\w*",
        r"apr[èe]s\s+avoir\s+corrig[ée]",
        r"apr[èe]s\s+(la|ta|une)\s+correction.{0,30}(exercice|examen)",
        r"organisation\s+de\s+(la|ta|l['’])\s*(r[ée]vision|[ée]tude)",
        r"organiser\s+(ta|sa|votre)\s+(r[ée]vision|[ée]tude)",
        r"comment\s+r[ée]viser",
        r"(qu['’]est-ce\s+qu['’]|à\s+quoi\s+sert)\s+un\s+examen\s+blanc",
        r"pourquoi\s+faire\s+un\s+examen\s+blanc",
        r"fonctionnement\s+du\s+site",
    )
)


def is_meta_revision_question(text: str) -> bool:
    """True si `text` (l'énoncé d'une question) porte sur le PROCESSUS de révision/examen
    lui-même plutôt que sur du contenu technique AMPCR (voir les 3 exemples interdits du
    ticket #58 § « contexte »). Volontairement ciblé sur des expressions distinctives du
    sens méta — ne bannit jamais un mot générique isolé comme « examen » ou « piège »."""
    if not text:
        return False
    return any(pattern.search(text) for pattern in _META_REVISION_PATTERNS)
