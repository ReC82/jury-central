"""FSE13 « La sécurité sociale : rôle et financement » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur six situations (Yasmine opérée, Marc
licencié, une famille avec deux enfants, Fatima qui part à la retraite, Thomas blessé par
une machine, un indépendant). Les cas ci-dessous gardent les mêmes notions (solidarité,
mutualisation des risques, assurance sociale, redistribution ; cotisations des travailleurs
et des employeurs ; financement, gestion et versement ; risques couverts ; repère
salarié/indépendant) mais sur d'autres supports : la fiche de paie simplifiée d'une
salariée et les demandes reçues par le service du personnel d'une entreprise, avec un
piège de transfert (un accident de ski en vacances n'est pas un accident du travail).

Aucun calcul de droits ; montants de la fiche de paie fictifs et cohérents (brut - retenues
= net)."""

from app.v1.fse13_content import FSE13_SITUATIONS_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE13_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE13_SITUATIONS_TITLE}),
    markers=("Yasmine",),
)

# =============================================================================================
# Cas 1 — Fiche de paie simplifiée
# =============================================================================================

PAYSLIP_TITLE = "Fiche de paie simplifiée de Léa, vendeuse — mois de mars"
_PAYSLIP_CONTEXT = (
    "Fiche de paie d'une salariée à temps plein dans un magasin de chaussures, simplifiée pour "
    "l'exercice. Personne, employeur et montants fictifs."
)
_UNIT = "en euros"
_PAYSLIP_SECTIONS = (
    ("SALAIRE", (("L1", "Salaire brut du mois", "2 400,00"),)),
    ("RETENUES SUR LE SALAIRE", (
        ("L2", "Cotisations sociales personnelles (sécurité sociale)", "313,68"),
        ("L3", "Précompte professionnel (avance sur l'impôt)", "380,00"),
    )),
    ("VERSÉ À LÉA", (("L4", "Salaire net versé sur son compte", "1 706,32"),)),
    ("PAYÉ EN PLUS PAR L'EMPLOYEUR", (("L5", "Cotisations sociales patronales", "600,00"),)),
)

PAYSLIP_TEXT = f"[{_PAYSLIP_CONTEXT}]\n\n" + "\n\n".join(
    f"{title} ({_UNIT})\n" + "\n".join(f"{label} — {text} : {amount}" for label, text, amount in rows)
    for title, rows in _PAYSLIP_SECTIONS
)

PAYSLIP_LAYOUT = {
    "kind": "budget",
    "notice": "Fiche de paie fictive — exercice pédagogique",
    "context": _PAYSLIP_CONTEXT,
    "sections": [
        {"title": title, "unit": _UNIT,
         "rows": [{"label": label, "text": text, "amount": amount} for label, text, amount in rows]}
        for title, rows in _PAYSLIP_SECTIONS
    ],
}

_PAYSLIP_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Sur la fiche de paie de Léa, que représente chacune de ces lignes ?",
            "source_document_version_id": DOC,
            "categories": ["Cotisation sociale", "Impôt", "Salaire"],
            "elements": [
                "L2 — cotisations sociales personnelles",
                "L3 — précompte professionnel",
                "L4 — salaire net versé",
                "L5 — cotisations sociales patronales",
            ],
            "correct_categories": [0, 1, 2, 0],
            "explanation": (
                "Les cotisations (personnelles ou patronales) financent la sécurité sociale ; le "
                "précompte professionnel est une avance sur l'impôt ; le net est le salaire que "
                "Léa reçoit réellement."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "D'après la fiche de paie, qui finance la sécurité sociale à partir du travail de "
                "Léa ? Cite les deux lignes concernées."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle nomme les deux sources de cotisations : Léa elle-même "
                "(L2, cotisations personnelles retenues sur son salaire brut) et son employeur "
                "(L5, cotisations patronales payées en plus du salaire)."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "classification",
        {
            "prompt": (
                "Ces étapes concernent la sécurité sociale de Léa. Lesquelles relèvent du "
                "financement, de la gestion ou du versement ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Financement", "Gestion", "Versement"],
            "elements": [
                "313,68 € sont retenus sur le salaire brut de Léa",
                "Son employeur paie 600 € de cotisations patronales",
                "Un organisme public organise la branche maladie-invalidité",
                "Sa mutualité lui rembourse une consultation chez le médecin",
            ],
            "correct_categories": [0, 0, 1, 2],
            "explanation": (
                "Les cotisations financent le système ; un organisme public gère une branche ; "
                "la mutualité verse concrètement la prestation à la personne."
            ),
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Un collègue de Léa regarde la ligne L2 et dit : « Je ne suis jamais malade, ces "
                "313,68 € sont de l'argent perdu. » Réponds-lui en utilisant les notions de "
                "mutualisation des risques, d'assurance sociale, de solidarité et de "
                "redistribution."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : mutualisation — tous les travailleurs cotisent ensemble pour couvrir "
                "des risques qui ne touchent que certains d'entre eux à un moment donné (1 point) ; "
                "assurance sociale — les cotisations ouvrent une protection si le risque survient "
                "un jour (maladie, chômage, accident, vieillesse…), même s'il ne s'est pas encore "
                "produit (1 point) ; solidarité — les bien portants financent les soins des "
                "malades, les actifs les pensions (1 point) ; redistribution — l'argent collecté "
                "est reversé à ceux qui en ont besoin ; ce n'est pas une épargne personnelle, "
                "donc pas de l'argent perdu (1 point)."
            ),
            "expected_points": [
                "Mutualisation des risques",
                "Assurance sociale : protection si le risque survient",
                "Solidarité entre bien portants et malades, actifs et retraités",
                "Redistribution, pas une épargne personnelle",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Demandes reçues par le service du personnel
# =============================================================================================

DESK_TITLE = "Service du personnel d'une entreprise de livraison — six demandes de la semaine"
_DESK_CONTEXT = (
    "Demandes notées par la responsable du personnel d'une entreprise de livraison qui emploie "
    "des salariés et travaille avec un indépendant. Personnes fictives."
)
_DESK = (
    ("bi-bandaid", "Kevin, livreur",
     "Kevin est tombé d'un escalier pendant une livraison chez un client et s'est cassé le poignet."),
    ("bi-snow", "Amélie, employée",
     ("Amélie s'est blessée au genou en skiant pendant ses vacances. Elle ne peut pas "
      "travailler pendant deux mois.")),
    ("bi-door-open", "Romain, magasinier",
     "Le contrat à durée déterminée de Romain n'est pas renouvelé : il se retrouve sans emploi."),
    ("bi-balloon-heart", "Nadia, comptable",
     "Nadia et son compagnon viennent d'adopter un enfant de trois ans."),
    ("bi-calendar-check", "Jean, chauffeur",
     "Jean arrête de travailler à la fin du mois, après une carrière complète."),
    ("bi-person-badge", "Sofiane, graphiste",
     ("Sofiane, graphiste indépendant, crée les affiches de l'entreprise. Il n'est pas salarié "
      "et demande qui paie ses cotisations sociales.")),
)

DESK_TEXT = f"[{_DESK_CONTEXT}]\n\n" + "\n\n".join(
    f"Demande {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_DESK, start=1)
)

DESK_LAYOUT = {
    "kind": "cards",
    "notice": "Demandes fictives — exercice pédagogique",
    "context": _DESK_CONTEXT,
    "item_label": "Demande",
    "items": [
        {"number": index, "label": f"Demande {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_DESK, start=1)
    ],
}

_DESK_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Quel risque de la sécurité sociale est concerné par chacune de ces demandes ?",
            "source_document_version_id": DOC,
            "categories": [
                "Accident du travail", "Maladie-invalidité", "Chômage", "Charges familiales",
                "Vieillesse (pension)",
            ],
            "elements": [
                "Demande 1 — Kevin",
                "Demande 2 — Amélie",
                "Demande 3 — Romain",
                "Demande 4 — Nadia",
                "Demande 5 — Jean",
            ],
            "correct_categories": [0, 1, 2, 3, 4],
            "explanation": (
                "Kevin se blesse pendant son travail (accident du travail) ; Amélie, en "
                "vacances (incapacité couverte par l'assurance maladie-invalidité) ; Romain perd "
                "son emploi (chômage) ; Nadia accueille un enfant (charges familiales) ; Jean "
                "part à la retraite (vieillesse)."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Kevin (demande 1) et Amélie (demande 2) sont tous les deux blessés et ne peuvent "
                "pas travailler. Pourquoi leur situation ne relève-t-elle pas du même risque ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que c'est l'origine de la blessure qui compte : "
                "Kevin s'est blessé pendant son travail (livraison chez un client) — accident du "
                "travail ; Amélie s'est blessée pendant ses vacances, en dehors du travail — "
                "son incapacité relève de l'assurance maladie-invalidité."
            ),
            "max_length": 400,
        },
        H,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Demande 6 : que faut-il répondre à Sofiane, graphiste indépendant, qui demande "
                "qui paie ses cotisations sociales ? Compare avec un salarié de l'entreprise."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle indique qu'un indépendant paie lui-même ses cotisations "
                "sociales (il n'a pas d'employeur), alors que pour un salarié, des cotisations "
                "sont retenues sur son salaire et l'employeur paie en plus des cotisations "
                "patronales."
            ),
            "max_length": 400,
        },
        M,
    ),
)

# =============================================================================================
# Cas 3 — Mini-situation à choix multiple
# =============================================================================================

_POOL = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Dans une entreprise de 50 personnes, toutes cotisent chaque mois. Cette année, "
                "seules trois d'entre elles ont été longtemps malades et ont reçu des indemnités. "
                "Quel principe de la sécurité sociale cette situation illustre-t-elle ?"
            ),
            "options": [
                {"option_id": "a", "label": "La mutualisation des risques"},
                {"option_id": "b", "label": "L'épargne personnelle de chaque travailleur"},
                {"option_id": "c", "label": "Le remboursement des cotisations aux personnes jamais malades"},
                {"option_id": "d", "label": "La vente d'un service par une entreprise privée"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Tout le monde cotise pour couvrir un risque qui ne touche que certains : le "
                "risque est partagé (mutualisé) entre tous."
            ),
        },
        E,
    ),
)

FSE13_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE13", key="fse13-fiche-de-paie-lea", title=PAYSLIP_TITLE,
        content_text=PAYSLIP_TEXT, layout=PAYSLIP_LAYOUT, questions=_PAYSLIP_QUESTIONS,
    ),
    FseCase(
        course_code="FSE13", key="fse13-service-du-personnel", title=DESK_TITLE,
        content_text=DESK_TEXT, layout=DESK_LAYOUT, questions=_DESK_QUESTIONS,
    ),
    FseCase(course_code="FSE13", key="fse13-entreprise-cinquante-cotisants", questions=_POOL),
)
