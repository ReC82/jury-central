"""Ordre d'affichage des réponses propre à chaque question servie (ticket #150).

Bug constaté : dans le quiz (et de la même façon en entraînement/examen), choisir
systématiquement la première réponse suffisait à réussir. Cause : beaucoup de QCM des
banques actives (FSE, AMPCR rédigés à la main) stockent la bonne réponse en première
position et l'écran affichait les options dans l'ordre de la banque. Le mélange de #80
(`app.v1.ai_bridge.shuffle_multiple_choice_options`) n'est appliqué qu'aux contenus
importés ou générés, pas aux banques créées directement par `create_question`.

Correctif : à la création de la session, chaque `SessionQuestion` reçoit sa propre
permutation, persistée dans `content_snapshot_json["display_order"]` (identifiants
seulement, jamais la solution). Elle est réappliquée à chaque affichage : stable après
navigation, rafraîchissement et reprise. La banque et ses versions ne sont jamais
modifiées, et la correction reste faite par identifiant d'option/d'élément sur le contenu
privé (`content_json`) — l'ordre affiché n'intervient jamais dans le calcul du score.

Les sessions créées avant ce correctif n'ont pas de permutation : leur ordre (celui de la
banque) reste inchangé, pour que l'élève revoie exactement ce qu'il a vu."""

import random
import re
from typing import Any

SNAPSHOT_KEY = "display_order"

# Options dont le sens dépend de leur place (« toutes les réponses ci-dessus »…) : elles
# gardent leur position d'origine, seules les autres sont mélangées autour d'elles.
_POSITION_DEPENDENT = re.compile(
    r"\b(toutes|aucune|tous|aucun)\s+(les|des|de\s+ces)\s+(réponses|propositions|choix|options)\s*"
    r"(ci-dessus|précédentes|précédents|ci-dessous|suivantes|suivants)?\b"
    r"|^\s*(les\s+réponses\s+)?[A-H]\s*(,\s*[A-H]\s*)*(et|ou)\s+[A-H]\s*\.?\s*$",
    re.IGNORECASE,
)


def is_position_dependent(label: str) -> bool:
    return bool(_POSITION_DEPENDENT.search(label or ""))


def _shuffle_options(options: list[dict[str, Any]], rng: random.Random) -> list[str]:
    ids = [o["option_id"] for o in options]
    pinned = {i for i, o in enumerate(options) if is_position_dependent(o.get("label", ""))}
    movable = [ids[i] for i in range(len(ids)) if i not in pinned]
    rng.shuffle(movable)
    shuffled = iter(movable)
    return [ids[i] if i in pinned else next(shuffled) for i in range(len(ids))]


def build_display_order(
    question_type: str, content: dict[str, Any], rng: random.Random | None = None
) -> dict[str, list[str]] | None:
    """Tire la permutation d'affichage d'une question servie (`None` si rien à mélanger).

    QCM : tirage uniforme — la bonne réponse peut tomber en première position par hasard
    (1 chance sur n), ce n'est plus un indice systématique ; on n'impose pas « jamais en
    premier », qui deviendrait lui-même un indice. Un QCM marqué `shuffle: false` par son
    auteur garde son ordre. Remise en ordre : jamais affichée déjà dans le bon ordre."""
    rng = rng or random.SystemRandom()
    if question_type == "multiple_choice":
        options = content.get("options") or []
        if len(options) < 2 or content.get("shuffle") is False:
            return None
        return {"options": _shuffle_options(options, rng)}
    if question_type == "ordering":
        items = content.get("items") or []
        if len(items) < 2:
            return None
        # Même règle que `app.v1.ai_bridge.shuffle_ordering_items` (#80), avec le tirage de
        # la session : retirer si le mélange retombe sur l'ordre attendu.
        correct_order = list(content.get("correct_order") or [])
        ids = [item["id"] for item in items]
        for _ in range(20):
            rng.shuffle(ids)
            if ids != correct_order:
                break
        if ids == correct_order:
            ids = ids[1:] + ids[:1]
        return {"items": ids}
    return None


def _reorder(entries: list[dict[str, Any]], key: str, order: list[str] | None) -> list[dict[str, Any]]:
    if not order:
        return entries
    rank = {entry_id: index for index, entry_id in enumerate(order)}
    # Élément inconnu de la permutation (ne devrait pas arriver : la version servie est
    # immuable) : gardé, placé après les autres, jamais perdu.
    return sorted(entries, key=lambda entry: rank.get(entry.get(key), len(rank)))


def apply_display_order(question_type: str, payload: dict[str, Any], snapshot: Any) -> dict[str, Any]:
    """Réordonne une copie du payload public (ou du contenu, pour la relecture après
    validation) selon la permutation persistée de la question servie."""
    order = (snapshot or {}).get(SNAPSHOT_KEY) if isinstance(snapshot, dict) else None
    if not order:
        return payload
    payload = dict(payload)
    if question_type == "multiple_choice" and isinstance(payload.get("options"), list):
        payload["options"] = _reorder(payload["options"], "option_id", order.get("options"))
    elif question_type == "ordering" and isinstance(payload.get("items"), list):
        payload["items"] = _reorder(payload["items"], "id", order.get("items"))
    return payload
