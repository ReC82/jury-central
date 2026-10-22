"""FSE15 « Le circuit économique et les interventions de l'État » — cas nouveaux
(ticket #129).

Le cours et sa banque historique s'appuient sur le schéma à compléter du circuit à quatre
agents et sur l'exemple d'une aide publique à un média local. Les cas ci-dessous gardent
les mêmes notions (ménages, entreprises, État, reste du monde ; flux réels et flux
monétaires ; redistribution, régulation et production de services collectifs) mais les
font repérer dans la vie quotidienne d'une infirmière et de sa famille, puis dans les
effets d'une prime à l'isolation des logements (avec une « fuite » vers le reste du monde).

Notions d'économie générale ; montants absents ou fictifs."""

from app.v1.fse15_content import FSE15_AID_TITLE, FSE15_CIRCUIT_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE15_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE15_CIRCUIT_TITLE, FSE15_AID_TITLE}),
    markers=("D'après le schéma", "média local"),
)

# =============================================================================================
# Cas 1 — Une semaine de Sara, infirmière
# =============================================================================================

WEEK_TITLE = "Une semaine dans la vie de Sara, infirmière — sept moments"
_WEEK_CONTEXT = (
    "Récit rédigé pour l'exercice : Sara, infirmière salariée d'une clinique privée, vit avec "
    "sa fille de dix ans ; son père est retraité. Personnes et entreprises fictives."
)
_WEEK = (
    ("bi-hospital", "Lundi",
     "Sara assure ses gardes à la clinique. À la fin du mois, la clinique lui verse son salaire."),
    ("bi-bicycle", "Mardi",
     ("Sara achète un vélo électrique chez le marchand de cycles de son quartier. Ce vélo a été "
      "fabriqué en Allemagne et importé par le magasin.")),
    ("bi-receipt", "Mercredi",
     "Sur sa fiche de paie, Sara voit les impôts et les cotisations sociales retenus sur son salaire."),
    ("bi-backpack", "Jeudi",
     "La fille de Sara suit ses cours dans une école publique gratuite, financée par l'État."),
    ("bi-piggy-bank", "Vendredi",
     "Le père de Sara reçoit sa pension de retraite sur son compte."),
    ("bi-cup-straw", "Samedi",
     ("Sara visite une brasserie de sa région qui vend une grande partie de sa bière en France. "
      "Les acheteurs français paient la brasserie.")),
    ("bi-clipboard-check", "Dimanche",
     ("Le brasseur explique que des inspecteurs de l'État contrôlent régulièrement que sa "
      "brasserie respecte les normes d'hygiène.")),
)

WEEK_TEXT = f"[{_WEEK_CONTEXT}]\n\n" + "\n\n".join(
    f"Moment {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_WEEK, start=1)
)

WEEK_LAYOUT = {
    "kind": "cards",
    "notice": "Récit fictif — exercice pédagogique",
    "context": _WEEK_CONTEXT,
    "item_label": "Moment",
    "items": [
        {"number": index, "label": f"Moment {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_WEEK, start=1)
    ],
}

_WEEK_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Dans la semaine de Sara, s'agit-il d'un flux réel ou d'un flux monétaire ?",
            "source_document_version_id": DOC,
            "categories": ["Flux réel", "Flux monétaire"],
            "elements": [
                "Le travail de Sara à la clinique (moment 1)",
                "Le salaire versé à Sara (moment 1)",
                "Le vélo arrivé d'Allemagne au magasin (moment 2)",
                "La pension versée au père de Sara (moment 5)",
                "Les cours donnés à la fille de Sara (moment 4)",
            ],
            "correct_categories": [0, 1, 0, 1, 0],
            "explanation": (
                "Un flux réel est un bien, un service ou du travail (travail, vélo, cours) ; un "
                "flux monétaire est un paiement en argent (salaire, pension)."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": "Entre quels agents du circuit économique circule chacun de ces flux ?",
            "source_document_version_id": DOC,
            "categories": ["Ménages et entreprises", "Ménages et État", "Entreprises et reste du monde"],
            "elements": [
                "Le salaire de Sara (moment 1)",
                "L'achat du vélo par Sara (moment 2)",
                "Les impôts et cotisations de Sara (moment 3)",
                "La pension du père de Sara (moment 5)",
                "Le paiement de la bière par les acheteurs français (moment 6)",
            ],
            "correct_categories": [0, 0, 1, 1, 2],
            "explanation": (
                "Salaire et achats relient les ménages aux entreprises ; impôts, cotisations et "
                "pension relient les ménages à l'État ; les exportations relient une entreprise "
                "au reste du monde."
            ),
        },
        M,
    ),
    (
        "classification",
        {
            "prompt": "Quel type d'intervention de l'État reconnais-tu dans chacun de ces moments ?",
            "source_document_version_id": DOC,
            "categories": ["Redistribution", "Régulation", "Production de services collectifs"],
            "elements": [
                "La pension du père de Sara (moment 5)",
                "Les inspections d'hygiène à la brasserie (moment 7)",
                "L'école publique gratuite (moment 4)",
            ],
            "correct_categories": [0, 1, 2],
            "explanation": (
                "Verser une pension financée par les cotisations, c'est redistribuer ; imposer et "
                "contrôler des normes, c'est réguler ; organiser l'enseignement public, c'est "
                "produire un service collectif."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Moment 2 : le vélo de Sara a été fabriqué en Allemagne. Quels deux flux relient "
                "le magasin au reste du monde ? Précise leur sens et leur nature."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle décrit l'importation : un flux réel du reste du monde "
                "vers l'entreprise (le vélo livré au magasin) et, en sens inverse, un flux "
                "monétaire de l'entreprise vers le reste du monde (le paiement du vélo au "
                "fabricant allemand)."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Suis l'argent du salaire de Sara dans le circuit économique, à l'aide des "
                "moments 1, 2, 3 et 5 : d'où vient-il et vers quels agents repart-il ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : le salaire est un flux monétaire d'une entreprise (la clinique) vers "
                "un ménage (Sara) (1 point) ; une partie repart vers l'État sous forme d'impôts "
                "et de cotisations (1 point), que l'État reverse notamment en prestations "
                "sociales comme la pension du père (1 point) ; une autre partie repart vers une "
                "entreprise (achat du vélo), puis en partie vers le reste du monde, puisque le "
                "vélo est importé (1 point)."
            ),
            "expected_points": [
                "Salaire : entreprise vers ménage",
                "Impôts et cotisations : ménage vers État",
                "Prestations sociales : État vers ménages (pension)",
                "Achat du vélo : vers une entreprise puis le reste du monde",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Une prime à l'isolation des logements
# =============================================================================================

GRANT_TITLE = "Exemple fictif — une prime à l'isolation des toitures, étape par étape"
_GRANT_CONTEXT = (
    "Exemple rédigé pour l'exercice : un pouvoir public accorde une prime aux ménages qui "
    "isolent la toiture de leur logement. Aucun montant ni organisme réel."
)
_GRANT = (
    ("bi-bank", "La prime",
     "L'État verse une prime à la famille Diallo, qui fait isoler la toiture de sa maison."),
    ("bi-house-gear", "Les travaux",
     "La famille Diallo paie une petite entreprise de toiture de sa commune pour réaliser les travaux."),
    ("bi-box-seam", "Les matériaux",
     "L'entreprise achète les panneaux isolants à un fabricant situé aux Pays-Bas."),
    ("bi-people", "Les salaires",
     "L'entreprise verse les salaires des deux ouvriers qui ont posé l'isolation."),
    ("bi-arrow-repeat", "Le retour",
     "Les ouvriers et l'entreprise paient des impôts et des cotisations à l'État."),
)

GRANT_TEXT = f"[{_GRANT_CONTEXT}]\n\n" + "\n\n".join(
    f"Étape {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_GRANT, start=1)
)

GRANT_LAYOUT = {
    "kind": "cards",
    "notice": "Exemple fictif — exercice pédagogique",
    "context": _GRANT_CONTEXT,
    "item_label": "Étape",
    "items": [
        {"number": index, "label": f"Étape {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_GRANT, start=1)
    ],
}

_GRANT_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Pour chaque étape de la prime à l'isolation, quel agent paie et quel agent reçoit l'argent ?",
            "source_document_version_id": DOC,
            "categories": [
                "État → ménages", "Ménages → entreprises", "Entreprises → reste du monde",
                "Entreprises → ménages",
            ],
            "elements": [
                "Étape 1 — la prime",
                "Étape 2 — le paiement des travaux",
                "Étape 3 — l'achat des panneaux isolants",
                "Étape 4 — les salaires des ouvriers",
            ],
            "correct_categories": [0, 1, 2, 3],
            "explanation": (
                "La prime va de l'État à un ménage ; le ménage paie une entreprise ; "
                "l'entreprise paie un fabricant étranger (importation) et verse des salaires à "
                "des ménages."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Une partie de l'argent de la prime ne reste pas dans l'économie du pays. À quelle "
                "étape, et pourquoi faut-il en tenir compte pour analyser les effets de la prime ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle désigne l'étape 3 : l'entreprise paie des panneaux "
                "importés des Pays-Bas, un flux monétaire vers le reste du monde ; cette partie "
                "de la dépense ne fait pas travailler d'entreprises ni de ménages du pays et ne "
                "revient pas à l'État en impôts et cotisations : l'effet de la prime sur "
                "l'économie du pays est donc plus faible que son montant."
            ),
            "max_length": 400,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 — Mini-situation à choix multiple
# =============================================================================================

_STREETLIGHTS = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Une commune fait installer un nouvel éclairage public dans toutes ses rues, "
                "utilisé gratuitement par tous les habitants et les entreprises. De quel type "
                "d'intervention publique s'agit-il ?"
            ),
            "options": [
                {"option_id": "a", "label": "La production d'un bien ou service collectif"},
                {"option_id": "b", "label": "Une redistribution de revenus entre ménages"},
                {"option_id": "c", "label": "Une régulation par des normes imposées aux entreprises"},
                {"option_id": "d", "label": "Une exportation vers le reste du monde"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "L'éclairage public profite à tous sans être vendu à chacun : c'est un bien "
                "ou service collectif produit (ou financé) par les pouvoirs publics."
            ),
        },
        E,
    ),
)

FSE15_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE15", key="fse15-semaine-de-sara", title=WEEK_TITLE,
        content_text=WEEK_TEXT, layout=WEEK_LAYOUT, questions=_WEEK_QUESTIONS,
    ),
    FseCase(
        course_code="FSE15", key="fse15-prime-isolation-toitures", title=GRANT_TITLE,
        content_text=GRANT_TEXT, layout=GRANT_LAYOUT, questions=_GRANT_QUESTIONS,
    ),
    FseCase(course_code="FSE15", key="fse15-eclairage-public", questions=_STREETLIGHTS),
)
