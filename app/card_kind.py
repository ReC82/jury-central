"""Classification purement présentationnelle des blocs de leçon en "cartes" du Design
System (voir docs/UI_GUIDELINES.md). Ne lit ni ne modifie jamais le contenu pédagogique :
seul le titre du bloc (déjà rédigé selon une convention "Leçon — Rôle") est utilisé pour
choisir l'habillage visuel (icône, couleur, libellé).
"""

CARD_META = {
    "theory": {"icon": "📘", "label": "Théorie"},
    "example": {"icon": "💡", "label": "Exemple"},
    "exercise": {"icon": "📝", "label": "Exercice"},
    "exam": {"icon": "🎓", "label": "Mini-test"},
    "quiz": {"icon": "🎯", "label": "Quiz"},
    "summary": {"icon": "📌", "label": "À retenir"},
    "info": {"icon": "ℹ️", "label": "Ressources"},
    "warning": {"icon": "⚠️", "label": "Attention"},
    "method": {"icon": "🧭", "label": "Méthode"},
}


def classify_block_title(title: str) -> str:
    """Choisit un type de carte à partir du titre d'un bloc.

    Convention déjà utilisée par tout le contenu importé (ex. « Solides — Cours »,
    « Solides — Exercices »). Retombe sur "theory" par défaut (présentation, cours, plan de
    l'UAA, méthode).
    """
    lowered = title.lower()
    if "mini-test" in lowered:
        return "exam"
    if "fiche mémo" in lowered or "mémo" in lowered:
        return "summary"
    if "ressource" in lowered:
        return "info"
    if "attention" in lowered or "piège" in lowered:
        return "warning"
    if "exercice" in lowered:
        return "exercise"
    if "exemple" in lowered or "transfert" in lowered:
        return "example"
    return "theory"


def card_meta(kind: str) -> dict:
    meta = CARD_META.get(kind, CARD_META["theory"])
    return {"kind": kind, "icon": meta["icon"], "label": meta["label"]}
