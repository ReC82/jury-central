"""FSE12 « Le budget de l'État » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur un seul tableau fictif (TVA, accises, IPP,
cotisations, patrimoine ; solde de -100, déficit). Les cas ci-dessous gardent les mêmes
notions (recettes fiscales, parafiscales et non fiscales ; dépenses de fonctionnement,
d'investissement et de transfert ; solde, déficit, excédent et dette comme vocabulaire ;
calculs simples) mais avec d'autres données et un autre résultat : le budget d'un État
imaginaire en excédent, puis quatre mesures annoncées qui font basculer un autre budget en
déficit.

Aucun calcul d'impôt personnel (IPP exclue, comme dans le cours) ; chiffres entièrement
fictifs, totaux à calculer volontairement absents des documents."""

from app.v1.fse12_content import FSE12_BUDGET_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE12_EXAMPLES = CourseExamples(
    # Toutes les questions historiques sur le tableau du cours y sont rattachées : aucun
    # marqueur (« du tableau » attraperait aussi des questions générales sans document).
    document_titles=frozenset({FSE12_BUDGET_TITLE}),
)

# =============================================================================================
# Cas 1 — Budget d'un État imaginaire en excédent
# =============================================================================================

BUDGET_TITLE = "Budget prévu de la République de Valmerie — année fictive"
_BUDGET_CONTEXT = (
    "Extrait du budget présenté au parlement d'un État imaginaire. Données entièrement fictives."
)
_UNIT = "en millions d'unités fictives"
_INCOME = (
    ("R1", "Impôt des sociétés payé par les entreprises", "240"),
    ("R2", "Taxe sur les billets d'avion", "30"),
    ("R3", "Cotisations sociales des travailleurs et des employeurs", "310"),
    ("R4", "Vente d'un bâtiment public inutilisé", "25"),
    ("R5", "Loyers perçus pour des terrains appartenant à l'État", "15"),
)
_SPENDING = (
    ("D1", "Salaires des agents des administrations", "180"),
    ("D2", "Construction d'une nouvelle ligne de tram", "90"),
    ("D3", "Pensions versées aux retraités", "250"),
    ("D4", "Bourses d'études versées aux étudiants", "40"),
    ("D5", "Chauffage et entretien des bâtiments publics", "30"),
)

BUDGET_TEXT = (
    f"[{_BUDGET_CONTEXT}]\n\nRECETTES ({_UNIT})\n"
    + "\n".join(f"{label} — {text} : {amount}" for label, text, amount in _INCOME)
    + f"\n\nDÉPENSES ({_UNIT})\n"
    + "\n".join(f"{label} — {text} : {amount}" for label, text, amount in _SPENDING)
)

BUDGET_LAYOUT = {
    "kind": "budget",
    "notice": "Budget fictif — exercice pédagogique",
    "context": _BUDGET_CONTEXT,
    "sections": [
        {"title": title, "unit": _UNIT,
         "rows": [{"label": label, "text": text, "amount": amount} for label, text, amount in rows]}
        for title, rows in (("RECETTES", _INCOME), ("DÉPENSES", _SPENDING))
    ],
}

_BUDGET_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Dans le budget de Valmerie, de quel type est chaque recette ?",
            "source_document_version_id": DOC,
            "categories": ["Recette fiscale", "Recette parafiscale", "Recette non fiscale"],
            "elements": [
                "R1 — impôt des sociétés",
                "R2 — taxe sur les billets d'avion",
                "R3 — cotisations sociales",
                "R4 — vente d'un bâtiment public",
                "R5 — loyers de terrains de l'État",
            ],
            "correct_categories": [0, 0, 1, 2, 2],
            "explanation": (
                "Impôts et taxes sont des recettes fiscales ; les cotisations sociales, une "
                "recette parafiscale ; la vente d'un bien public et les loyers de terrains "
                "publics ne sont ni des impôts ni des cotisations : recettes non fiscales."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": "Dans le même budget, de quel type est chaque dépense ?",
            "source_document_version_id": DOC,
            "categories": ["Fonctionnement", "Investissement", "Transfert"],
            "elements": [
                "D1 — salaires des agents",
                "D2 — nouvelle ligne de tram",
                "D3 — pensions",
                "D4 — bourses d'études",
                "D5 — chauffage et entretien des bâtiments",
            ],
            "correct_categories": [0, 1, 2, 2, 0],
            "explanation": (
                "Faire tourner les administrations (salaires, chauffage, entretien) relève du "
                "fonctionnement ; construire une infrastructure, de l'investissement ; verser de "
                "l'argent à des personnes (pensions, bourses), du transfert."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Calcule le total des recettes et le total des dépenses prévus pour Valmerie. "
                "Détaille les additions."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle donne les deux totaux avec le détail : recettes = 240 + "
                "30 + 310 + 25 + 15 = 620 ; dépenses = 180 + 90 + 250 + 40 + 30 = 590 (en "
                "millions d'unités fictives). Un seul total juste et détaillé = réponse "
                "partielle."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Calcule le solde budgétaire prévu de Valmerie et nomme-le : déficit ou "
                "excédent ? Montre ton calcul."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle calcule recettes moins dépenses : 620 - 590 = +30 "
                "(millions d'unités fictives) et nomme ce solde positif un excédent."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Un député de Valmerie affirme : « Avec ce budget, nous allons encore creuser "
                "la dette publique. » Son affirmation est-elle cohérente avec le solde prévu ? "
                "Justifie."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que non : la dette publique est formée par les "
                "déficits accumulés ; or ce budget prévoit un excédent (+30), pas un déficit. "
                "Cette année-là ne crée pas de nouveau déficit qui alourdirait la dette ; "
                "l'excédent pourrait même servir à en rembourser une partie."
            ),
            "max_length": 400,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Quatre mesures annoncées qui modifient un budget
# =============================================================================================

MEASURES_TITLE = "Royaume d'Ostrelande — quatre mesures annoncées par le gouvernement"
_MEASURES_CONTEXT = (
    "Communiqué d'un gouvernement imaginaire, résumé en quatre mesures. Montants en millions "
    "d'unités fictives."
)
_MEASURES_INTRO = "Budget prévu avant ces mesures : recettes 900, dépenses 880."
_MEASURES = (
    ("bi-person-plus", "Plus d'agents aux guichets",
     "Engager des agents supplémentaires dans les administrations : +12 de dépenses."),
    ("bi-building", "Trois nouvelles écoles", "Construire trois nouvelles écoles : +45 de dépenses."),
    ("bi-mortarboard", "Bourses d'études", "Augmenter les bourses d'études versées aux étudiants : +8 de dépenses."),
    ("bi-airplane", "Billets d'avion", "Relever la taxe sur les billets d'avion : +5 de recettes."),
)

MEASURES_TEXT = f"[{_MEASURES_CONTEXT}]\n\n{_MEASURES_INTRO}\n\n" + "\n\n".join(
    f"Mesure {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_MEASURES, start=1)
)

MEASURES_LAYOUT = {
    "kind": "cards",
    "notice": "Communiqué fictif — exercice pédagogique",
    "context": _MEASURES_CONTEXT,
    "intro": _MEASURES_INTRO,
    "item_label": "Mesure",
    "items": [
        {"number": index, "label": f"Mesure {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_MEASURES, start=1)
    ],
}

_MEASURES_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Dans le communiqué d'Ostrelande, que représente chacune des quatre mesures ?",
            "source_document_version_id": DOC,
            "categories": [
                "Dépense de fonctionnement", "Dépense d'investissement", "Dépense de transfert",
                "Recette fiscale",
            ],
            "elements": [
                "Mesure 1 — agents supplémentaires",
                "Mesure 2 — trois nouvelles écoles",
                "Mesure 3 — bourses d'études",
                "Mesure 4 — taxe sur les billets d'avion",
            ],
            "correct_categories": [0, 1, 2, 3],
            "explanation": (
                "Payer des agents fait fonctionner l'administration ; construire des écoles est "
                "un investissement ; verser des bourses est un transfert ; une taxe est une "
                "recette fiscale."
            ),
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Le ministre du budget d'Ostrelande déclare : « Ces quatre mesures ne changent "
                "rien : notre budget restera en excédent. » Vérifie son affirmation en "
                "calculant les nouvelles recettes, les nouvelles dépenses et le nouveau solde."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : solde avant les mesures : 900 - 880 = +20, un excédent (1 point) ; "
                "nouvelles recettes : 900 + 5 = 905 (1 point) ; nouvelles dépenses : 880 + 12 + "
                "45 + 8 = 945 (1 point) ; nouveau solde : 905 - 945 = -40, un déficit : "
                "l'affirmation du ministre est fausse (1 point)."
            ),
            "expected_points": [
                "Solde initial +20 (excédent)",
                "Nouvelles recettes : 905",
                "Nouvelles dépenses : 945",
                "Nouveau solde -40 : déficit, affirmation fausse",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 — Mini-situation à choix multiple
# =============================================================================================

_MUSEUM = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Un musée appartenant à l'État vend des billets d'entrée aux visiteurs. Pour "
                "l'État, l'argent de ces billets est…"
            ),
            "options": [
                {"option_id": "a", "label": "Une recette non fiscale"},
                {"option_id": "b", "label": "Une recette fiscale"},
                {"option_id": "c", "label": "Une recette parafiscale"},
                {"option_id": "d", "label": "Une dépense de transfert"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Le prix d'un billet n'est ni un impôt ni une cotisation sociale : c'est un "
                "revenu tiré d'un bien public, donc une recette non fiscale."
            ),
        },
        E,
    ),
)

FSE12_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE12", key="fse12-budget-valmerie", title=BUDGET_TITLE,
        content_text=BUDGET_TEXT, layout=BUDGET_LAYOUT, questions=_BUDGET_QUESTIONS,
    ),
    FseCase(
        course_code="FSE12", key="fse12-mesures-ostrelande", title=MEASURES_TITLE,
        content_text=MEASURES_TEXT, layout=MEASURES_LAYOUT, questions=_MEASURES_QUESTIONS,
    ),
    FseCase(course_code="FSE12", key="fse12-billets-musee", questions=_MUSEUM),
)
