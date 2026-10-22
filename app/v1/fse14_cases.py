"""FSE14 « La sécurité sociale : organismes et enjeux » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur le tableau organisme / rôle et sur un
document daté présentant deux pressions sur le financement (vieillissement, dépenses de
santé). Les cas ci-dessous gardent les mêmes notions (ONSS, INAMI, ONEM, SFP, FEDRIS, ONVA,
INASTI, mutualité, FAMIWAL, FAMIRIS ; collecteur, gestionnaire, intermédiaire payeur ;
régionalisation des allocations familiales ; enjeux de vieillissement, d'emploi et de
dépenses de santé) mais sur d'autres supports : les courriers reçus par une famille
namuroise en un trimestre et trois interventions lors d'un débat, dont une sur l'emploi,
enjeu cité par le programme et absent du document du cours.

Chaque rôle attribué à un organisme est celui du tableau vérifié du cours ; aucun montant,
âge ou projection chiffrée."""

from app.v1.fse14_content import FSE14_ISSUES_TITLE, FSE14_ORGANISMS_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE14_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE14_ORGANISMS_TITLE, FSE14_ISSUES_TITLE}),
    markers=("tableau des organismes", "document daté"),
)

# =============================================================================================
# Cas 1 — Les courriers d'une famille en un trimestre
# =============================================================================================

MAIL_TITLE = "Famille Moreau, à Namur — sept courriers reçus en un trimestre"
_MAIL_CONTEXT = (
    "Courriers reçus par une famille domiciliée à Namur (Wallonie) : un père ouvrier, une mère "
    "employée et deux enfants. Résumés pour l'exercice ; famille fictive."
)
_MAIL = (
    ("bi-briefcase", "De l'employeur de Madame Moreau",
     ("Les cotisations sociales retenues sur votre salaire et nos cotisations patronales sont "
      "versées chaque trimestre à l'ONSS.")),
    ("bi-heart-pulse", "De la mutualité",
     ("Nous vous avons remboursé une partie de votre consultation chez le médecin, pour le "
      "compte de l'INAMI.")),
    ("bi-people", "De FAMIWAL",
     "Voici le montant des allocations familiales de ce mois pour vos deux enfants."),
    ("bi-sun", "De l'ONVA",
     "Monsieur Moreau, ouvrier, votre pécule de vacances sera versé sur votre compte en mai."),
    ("bi-hourglass-split", "Du SFP",
     "Voici une estimation de votre future pension, établie à partir de votre carrière actuelle."),
    ("bi-lungs", "De FEDRIS",
     ("Votre maladie professionnelle, liée aux poussières respirées sur le chantier, est "
      "reconnue ; une indemnisation vous sera versée.")),
    ("bi-clock-history", "De l'ONEM",
     "Votre demande de crédit-temps pour réduire votre temps de travail est acceptée."),
)

MAIL_TEXT = f"[{_MAIL_CONTEXT}]\n\n" + "\n\n".join(
    f"Courrier {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_MAIL, start=1)
)

MAIL_LAYOUT = {
    "kind": "cards",
    "notice": "Courriers fictifs — exercice pédagogique",
    "context": _MAIL_CONTEXT,
    "item_label": "Courrier",
    "items": [
        {"number": index, "label": f"Courrier {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_MAIL, start=1)
    ],
}

_MAIL_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "À quelle branche de la sécurité sociale se rapporte chacun de ces courriers ?",
            "source_document_version_id": DOC,
            "categories": [
                "Soins de santé", "Allocations familiales", "Vacances annuelles", "Pensions",
                "Risques professionnels",
            ],
            "elements": [
                "Courrier 2 — la mutualité",
                "Courrier 3 — FAMIWAL",
                "Courrier 4 — l'ONVA",
                "Courrier 5 — le SFP",
                "Courrier 6 — FEDRIS",
            ],
            "correct_categories": [0, 1, 2, 3, 4],
            "explanation": (
                "La mutualité rembourse des soins de santé ; FAMIWAL verse les allocations "
                "familiales en Wallonie ; l'ONVA gère le pécule de vacances des ouvriers ; le SFP "
                "s'occupe des pensions ; FEDRIS, des accidents du travail et des maladies "
                "professionnelles."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "D'après les courriers de la famille Moreau, quel rôle joue chacun de ces "
                "organismes ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Collecteur", "Gestionnaire", "Intermédiaire payeur"],
            "elements": [
                "L'ONSS (courrier 1)",
                "L'ONEM (courrier 7)",
                "La mutualité (courrier 2)",
                "FAMIWAL (courrier 3)",
            ],
            "correct_categories": [0, 1, 2, 2],
            "explanation": (
                "L'ONSS perçoit les cotisations (collecteur) ; l'ONEM met en œuvre le crédit-temps "
                "(gestionnaire) ; la mutualité et FAMIWAL versent concrètement des prestations "
                "aux familles (intermédiaires payeurs)."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Courrier 2 : la mutualité rembourse « pour le compte de l'INAMI ». Quel rôle "
                "joue chacun de ces deux organismes ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle indique que l'INAMI est le gestionnaire de l'assurance "
                "maladie-invalidité et que la mutualité est l'intermédiaire payeur : c'est elle "
                "qui verse concrètement le remboursement à la personne affiliée, pour le compte "
                "de l'INAMI."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "La famille Moreau déménage de Namur à Bruxelles. Qui lui versera désormais ses "
                "allocations familiales, et pourquoi le courrier 3 ne viendra-t-il plus de "
                "FAMIWAL ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite FAMIRIS (service d'Iriscare) comme caisse publique "
                "bruxelloise et explique la régionalisation : les allocations familiales sont "
                "organisées par chaque Région/Communauté selon le lieu de domicile de la "
                "famille ; FAMIWAL ne verse qu'aux familles domiciliées en Wallonie."
            ),
            "max_length": 400,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Trois interventions lors d'un débat
# =============================================================================================

DEBATE_TITLE = "Débat « Quel avenir pour notre sécurité sociale ? » — trois interventions"
_DEBATE_CONTEXT = (
    "Débat organisé dans une école pour adultes ; interventions résumées pour l'exercice. "
    "Intervenants fictifs ; aucun chiffre n'est cité."
)
_DEBATE = (
    ("Inès, économiste invitée", "I", "p1",
     ("Quand davantage de personnes ont un emploi, davantage de cotisations entrent dans la "
      "sécurité sociale, et moins d'allocations de chômage doivent être versées.")),
    ("Paul, retraité", "P", "p2",
     ("Nous vivons plus longtemps : je toucherai sans doute ma pension plus longtemps que mes "
      "parents n'ont touché la leur. Et nous sommes de plus en plus nombreux à la retraite.")),
    ("Docteure Leclercq, médecin généraliste", "L", "p3",
     ("Les nouveaux traitements soignent mieux, mais coûtent souvent plus cher. Et une "
      "population plus âgée a besoin de davantage de soins.")),
)

DEBATE_TEXT = f"[{_DEBATE_CONTEXT}]\n\n" + "\n\n".join(
    f"{actor} : « {text} »" for actor, _initials, _tone, text in _DEBATE
)

DEBATE_LAYOUT = {
    "kind": "quotes",
    "notice": "Débat fictif — exercice pédagogique",
    "context": _DEBATE_CONTEXT,
    "items": [
        {"actor": actor, "initials": initials, "tone": tone, "text": text}
        for actor, initials, tone, text in _DEBATE
    ],
}

_DEBATE_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Quel enjeu du financement de la sécurité sociale chaque intervenant évoque-t-il ?",
            "source_document_version_id": DOC,
            "categories": ["Emploi", "Vieillissement (pensions)", "Dépenses de santé"],
            "elements": ["Inès, économiste", "Paul, retraité", "Docteure Leclercq"],
            "correct_categories": [0, 1, 2],
            "explanation": (
                "Inès parle du nombre de personnes au travail ; Paul, de la durée et du nombre "
                "des pensions ; la docteure Leclercq, du coût des soins."
            ),
        },
        E,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Compare l'intervention d'Inès et celle de Paul : explique comment chacune agit "
                "sur l'équilibre entre les recettes et les dépenses de la sécurité sociale."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : Inès — plus d'emploi augmente les recettes (davantage de cotisations) "
                "(1 point) et diminue des dépenses (moins d'allocations de chômage) : elle agit "
                "des deux côtés à la fois (1 point) ; Paul — le vieillissement augmente les "
                "dépenses de pension (pensions plus longues, retraités plus nombreux) (1 point) "
                "alors que le nombre de cotisants actifs ne suit pas : c'est une pression sur le "
                "financement, sans chiffre à inventer (1 point)."
            ),
            "expected_points": [
                "Emploi : plus de cotisations (recettes)",
                "Emploi : moins d'allocations de chômage (dépenses)",
                "Vieillissement : plus de dépenses de pension",
                "Moins de cotisants par retraité : pression sur le financement",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 — Mini-situation à choix multiple
# =============================================================================================

_SELF_EMPLOYED = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Clara ouvre son propre salon de coiffure comme indépendante. Quel organisme "
                "national gère la sécurité sociale des travailleurs indépendants, de la création "
                "de leur activité jusqu'à leur retraite ?"
            ),
            "options": [
                {"option_id": "a", "label": "L'INASTI"},
                {"option_id": "b", "label": "L'ONVA"},
                {"option_id": "c", "label": "FAMIWAL"},
                {"option_id": "d", "label": "L'ONEM"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "L'INASTI gère la sécurité sociale des indépendants ; l'ONVA, le pécule de "
                "vacances des ouvriers ; FAMIWAL verse les allocations familiales en Wallonie ; "
                "l'ONEM gère le chômage et le crédit-temps."
            ),
        },
        E,
    ),
)

FSE14_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE14", key="fse14-courriers-famille-moreau", title=MAIL_TITLE,
        content_text=MAIL_TEXT, layout=MAIL_LAYOUT, questions=_MAIL_QUESTIONS,
    ),
    FseCase(
        course_code="FSE14", key="fse14-debat-avenir-securite-sociale", title=DEBATE_TITLE,
        content_text=DEBATE_TEXT, layout=DEBATE_LAYOUT, questions=_DEBATE_QUESTIONS,
    ),
    FseCase(course_code="FSE14", key="fse14-salon-coiffure-independante", questions=_SELF_EMPLOYED),
)
