"""FSE16 « Analyser une décision publique » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur un dossier en trois documents : une carte de
transport collectif subventionnée par une Région, sa note budgétaire et trois réactions. Le
cas ci-dessous garde la même méthode (décision, niveau compétent, objectifs, agents, effets
attendus, limites, conséquences indirectes, court terme / long terme ; budget et circuit
économique comme outils) mais sur une autre décision, prise par un autre niveau de
pouvoir : la création d'une zone piétonne par une commune.

Les trois pièces du dossier sont réunies dans un seul support à trois fiches numérotées,
pour que l'élève et la correction disposent exactement du même document (cf. #151).
Commune, montants et personnes fictifs ; le subside régional est explicitement présenté
comme une hypothèse en attente de confirmation."""

from app.v1.fse16_content import (
    FSE16_BUDGET_NOTE_TITLE,
    FSE16_PROPOSAL_TITLE,
    FSE16_REACTIONS_TITLE,
)
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE16_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE16_PROPOSAL_TITLE, FSE16_BUDGET_NOTE_TITLE, FSE16_REACTIONS_TITLE}),
    markers=("carte de transport", "aide aux transports"),
)

# =============================================================================================
# Cas 1 — Dossier : la zone piétonne de Rochebelle
# =============================================================================================

DOSSIER_TITLE = "Dossier en trois pièces — la zone piétonne du centre de Rochebelle"
_DOSSIER_CONTEXT = (
    "Dossier réuni pour l'exercice sur une décision d'une commune fictive de Wallonie. "
    "Montants et personnes fictifs."
)
_PIECES = (
    ("bi-bank2", "Décision du conseil communal de Rochebelle",
     ("À partir du 1er septembre, la rue du Marché et la place de l'Église deviennent "
      "piétonnes. Objectifs : rendre le centre plus agréable et plus sûr, réduire le bruit et "
      "la pollution, et attirer davantage de promeneurs vers les commerces. Des travaux "
      "d'aménagement (revêtement, bancs, arbres) dureront six mois.")),
    ("bi-calculator", "Extrait de la note budgétaire de la commune",
     ("Les travaux d'aménagement coûtent 1\u00a0200\u00a0000\u00a0euros, inscrits au budget "
      "communal. Le stationnement payant de la place rapportait 80\u00a0000\u00a0euros par an à "
      "la commune : cette recette disparaît. Un subside de la Région couvrant 50\u00a0% des "
      "travaux a été demandé ; "
      "il n'est pas encore confirmé.")),
    ("bi-chat-quote", "Trois réactions recueillies par le journal local",
     ("Une commerçante de la rue du Marché : « Pendant six mois de travaux, mes clients vont "
      "fuir. Ensuite, peut-être que les promeneurs viendront plus nombreux. » Un habitant âgé : "
      "« Je ne pourrai plus me garer devant la pharmacie ; comment vais-je porter mes courses ? » "
      "Une association de cyclistes : « Enfin un centre où l'on circule à vélo en sécurité. »")),
)

DOSSIER_TEXT = f"[{_DOSSIER_CONTEXT}]\n\n" + "\n\n".join(
    f"Pièce {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_PIECES, start=1)
)

DOSSIER_LAYOUT = {
    "kind": "cards",
    "notice": "Dossier fictif — exercice pédagogique",
    "context": _DOSSIER_CONTEXT,
    "item_label": "Pièce",
    "items": [
        {"number": index, "label": f"Pièce {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_PIECES, start=1)
    ],
}

_DOSSIER_QUESTIONS = (
    (
        "multiple_choice",
        {
            "prompt": (
                "D'après la pièce 1 du dossier de Rochebelle, quel niveau de pouvoir a pris la "
                "décision de créer la zone piétonne ?"
            ),
            "source_document_version_id": DOC,
            "options": [
                {"option_id": "a", "label": "La commune, par son conseil communal"},
                {"option_id": "b", "label": "La Région wallonne, qui accorde un subside"},
                {"option_id": "c", "label": "Le gouvernement fédéral"},
                {"option_id": "d", "label": "L'association de cyclistes"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "La décision émane du conseil communal (pièce 1) : l'aménagement des rues d'un "
                "centre relève de la proximité. La Région n'intervient que par un subside "
                "demandé, et l'association ne fait que réagir."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": "Dans le dossier de Rochebelle, quel agent économique est touché par chacun de ces effets ?",
            "source_document_version_id": DOC,
            "categories": ["Ménages", "Entreprises", "État (la commune)"],
            "elements": [
                "Les clients qui fuient pendant les travaux (commerçante)",
                "Ne plus pouvoir se garer devant la pharmacie (habitant âgé)",
                "La disparition des 80 000 euros de stationnement payant",
                "Le coût des travaux d'aménagement",
            ],
            "correct_categories": [1, 0, 2, 2],
            "explanation": (
                "La commerçante est une entreprise ; l'habitant, un ménage ; la recette de "
                "stationnement perdue et le coût des travaux pèsent sur le budget de la commune."
            ),
        },
        M,
    ),
    (
        "classification",
        {
            "prompt": "Ces effets de la décision se produisent-ils plutôt à court terme ou à long terme ?",
            "source_document_version_id": DOC,
            "categories": ["Court terme", "Long terme (incertain)"],
            "elements": [
                "Les clients qui fuient pendant les six mois de travaux",
                "Davantage de promeneurs vers les commerces",
                "La dépense de 1 200 000 euros pour les travaux",
                "Moins de bruit et de pollution dans le centre",
            ],
            "correct_categories": [0, 1, 0, 1],
            "explanation": (
                "Les travaux, leur coût et leurs nuisances sont immédiats ; l'attrait du centre "
                "et la baisse du bruit et de la pollution sont des effets attendus plus tard, "
                "sans garantie."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "D'après la pièce 2, combien la zone piétonne coûtera-t-elle à la commune la "
                "première année si le subside régional de 50 % est confirmé ? Compte aussi la "
                "recette perdue et détaille le calcul."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle calcule : part communale des travaux = 1 200 000 × 50 % = "
                "600 000 euros ; recette de stationnement perdue = 80 000 euros ; total = "
                "680 000 euros. Une réponse qui rappelle que, sans subside, la part des travaux "
                "serait de 1 200 000 euros est un plus."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quelle limite ou conséquence indirecte de la décision la réaction de l'habitant "
                "âgé (pièce 3) met-elle en évidence ? Pourquoi les objectifs de la pièce 1 n'en "
                "parlent-ils pas ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle identifie une conséquence indirecte non voulue : l'accès "
                "en voiture aux commerces et services (la pharmacie) devient plus difficile pour "
                "les personnes âgées ou à mobilité réduite ; les objectifs affichés présentent "
                "les effets recherchés (centre agréable, sûr, moins pollué, plus de promeneurs), "
                "pas les inconvénients, qu'il faut chercher dans les autres pièces."
            ),
            "max_length": 400,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Rédige une conclusion argumentée sur la zone piétonne de Rochebelle, fondée sur "
                "les trois pièces du dossier : décision et niveau compétent, objectifs, effets "
                "attendus à court et à long terme, limites."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : décision et niveau — la commune (conseil communal) rend deux rues "
                "piétonnes (pièce 1) (1 point) ; objectifs et effets attendus à long terme — "
                "centre plus agréable et plus sûr, moins de bruit et de pollution, plus de "
                "promeneurs pour les commerces, effets incertains (1 point) ; effets à court "
                "terme et coût — six mois de travaux qui font fuir des clients, dépense de "
                "1 200 000 euros et perte de 80 000 euros par an, subside régional non confirmé "
                "(pièces 2 et 3) (1 point) ; limites et conclusion nuancée fondée sur les pièces, "
                "sans opinion gratuite (accès difficile pour l'habitant âgé, bénéfice pour les "
                "cyclistes) (1 point)."
            ),
            "expected_points": [
                "Décision prise par la commune (conseil communal)",
                "Objectifs et effets attendus à long terme, incertains",
                "Effets à court terme : travaux, coût, recette perdue, subside incertain",
                "Limites et conclusion nuancée fondée sur les pièces",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

FSE16_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE16", key="fse16-zone-pietonne-rochebelle", title=DOSSIER_TITLE,
        content_text=DOSSIER_TEXT, layout=DOSSIER_LAYOUT, questions=_DOSSIER_QUESTIONS,
    ),
)
