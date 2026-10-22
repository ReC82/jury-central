"""FSE08 « La Belgique : État et niveaux de pouvoir » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur le tableau des niveaux de pouvoir et ses
cinq affirmations à vérifier (A à E). Le cas ci-dessous garde les mêmes notions (niveaux
fédéral, régional, communautaire et communal ; logique territoriale des Régions et logique
des personnes et de la langue des Communautés ; loi, décret, ordonnance ; séparation des
pouvoirs ; monarchie constitutionnelle) mais demande de les reconnaître dans des brèves
d'actualité, sans tableau à recopier.

Les compétences citées restent celles du cours (défense : fédéral ; logement et
environnement : Régions ; enseignement : Communautés ; aménagements de proximité :
commune). Brèves fictives, aucun texte réellement voté n'est décrit."""

from app.v1.fse08_content import FSE08_MAP_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE08_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE08_MAP_TITLE}),
    markers=("du tableau", "D'après le tableau"),
)

# =============================================================================================
# Cas 1 — Huit brèves d'actualité
# =============================================================================================

NEWS_TITLE = "Huit brèves d'actualité de la semaine — qui a décidé ?"
_NEWS_CONTEXT = (
    "Brèves rédigées pour l'exercice, à la manière d'une page « En bref » d'un journal belge. "
    "Elles décrivent des décisions fictives."
)
_NEWS = (
    ("bi-house", "Primes au logement",
     ("Le Parlement wallon a adopté un texte qui modifie les primes accordées pour rénover les "
     "logements situés en Wallonie.")),
    ("bi-tree", "Qualité de l'air",
     ("Le Parlement de la Région de Bruxelles-Capitale a adopté un texte sur l'environnement et "
     "la qualité de l'air à Bruxelles.")),
    ("bi-mortarboard", "Écoles francophones",
     ("Le Parlement de la Communauté française a adopté un texte qui modifie l'organisation "
     "des écoles francophones.")),
    ("bi-shield", "Armée",
     "La Chambre des représentants a adopté un texte sur l'organisation de l'armée belge."),
    ("bi-signpost", "Place du marché",
     ("Le conseil communal d'une petite commune a décidé d'installer de nouveaux bancs et un "
     "éclairage sur la place du marché.")),
    ("bi-bank", "Litige de location",
     ("Un tribunal a tranché un litige entre un locataire et son propriétaire au sujet d'une "
     "caution non rendue.")),
    ("bi-briefcase", "Mise en œuvre",
     ("Le gouvernement wallon a fixé la date à partir de laquelle les nouvelles primes de la "
     "brève 1 pourront être demandées.")),
    ("bi-pen", "Signature",
     ("Après le vote de la brève 4, le Roi a signé le texte, comme le prévoit la Constitution. "
     "Il ne pouvait pas en modifier le contenu.")),
)

NEWS_TEXT = f"[{_NEWS_CONTEXT}]\n\n" + "\n\n".join(
    f"Brève {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_NEWS, start=1)
)

NEWS_LAYOUT = {
    "kind": "cards",
    "notice": "Brèves fictives — exercice pédagogique",
    "context": _NEWS_CONTEXT,
    "item_label": "Brève",
    "items": [
        {"number": index, "label": f"Brève {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_NEWS, start=1)
    ],
}

_NEWS_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "D'après les brèves de la semaine, à quel niveau de pouvoir appartient "
                "l'institution qui a pris chaque décision ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Fédéral", "Région", "Communauté", "Commune"],
            "elements": [
                "Brève 1 — primes au logement",
                "Brève 3 — écoles francophones",
                "Brève 4 — armée",
                "Brève 5 — place du marché",
            ],
            "correct_categories": [1, 2, 0, 3],
            "explanation": (
                "Le Parlement wallon est l'assemblée d'une Région (logement) ; le Parlement de "
                "la Communauté française, celle d'une Communauté (enseignement) ; la Chambre "
                "des représentants, une assemblée fédérale (défense) ; le conseil communal, la "
                "commune (proximité)."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "Quel nom porte la norme adoptée dans chacune de ces brèves : loi, décret ou "
                "ordonnance ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Loi", "Décret", "Ordonnance"],
            "elements": [
                "Brève 1 — Parlement wallon",
                "Brève 2 — Parlement de la Région de Bruxelles-Capitale",
                "Brève 3 — Parlement de la Communauté française",
                "Brève 4 — Chambre des représentants",
            ],
            "correct_categories": [1, 2, 1, 0],
            "explanation": (
                "Le niveau fédéral adopte des lois ; la Région wallonne et la Communauté "
                "française adoptent des décrets ; la Région de Bruxelles-Capitale adopte des "
                "ordonnances."
            ),
        },
        M,
    ),
    (
        "classification",
        {
            "prompt": (
                "La séparation des pouvoirs distingue trois pouvoirs. Lequel s'exerce dans "
                "chacune de ces brèves ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Pouvoir législatif", "Pouvoir exécutif", "Pouvoir judiciaire"],
            "elements": [
                "Brève 1 — le Parlement wallon adopte un texte",
                "Brève 6 — un tribunal tranche un litige",
                "Brève 7 — le gouvernement wallon fixe la date d'application des primes",
            ],
            "correct_categories": [0, 2, 1],
            "explanation": (
                "Un parlement fait les règles (législatif), un gouvernement les applique "
                "(exécutif), un tribunal tranche les litiges (judiciaire)."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Les brèves 1 et 3 concernent toutes les deux des habitants francophones de "
                "Wallonie. Pourquoi l'une relève-t-elle d'une Région et l'autre d'une "
                "Communauté ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique la différence de logique : les Régions sont "
                "compétentes pour des matières liées au territoire (le logement situé en "
                "Wallonie, brève 1) ; les Communautés pour des matières liées aux personnes, à "
                "la langue et à la culture (l'enseignement dans les écoles francophones, "
                "brève 3)."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Que montre la brève 8 sur le régime politique de la Belgique ? Utilise la "
                "notion de monarchie constitutionnelle."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que la Belgique est une monarchie "
                "constitutionnelle : le Roi n'exerce que les pouvoirs que lui donne la "
                "Constitution ; il signe un texte voté par les élus (la Chambre, brève 4) sans "
                "pouvoir en modifier le contenu. Le texte vient des représentants élus "
                "(démocratie parlementaire) en complément apprécié."
            ),
            "max_length": 400,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Un ami affirme : « En Belgique, c'est le gouvernement fédéral qui décide de "
                "tout. » Réfute cette affirmation à l'aide d'au moins trois brèves, en "
                "nommant chaque fois le niveau de pouvoir et le type de norme ou de pouvoir "
                "en jeu."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : au moins une décision régionale avec sa norme (brève 1 : décret "
                "wallon ; ou brève 2 : ordonnance bruxelloise) (1 point) ; une décision "
                "communautaire (brève 3 : décret de la Communauté française) (1 point) ; une "
                "décision communale ou le rôle d'un autre pouvoir (tribunal, brève 6 ; "
                "gouvernement wallon, brève 7) (1 point) ; conclusion : le pouvoir est réparti "
                "entre plusieurs niveaux et séparé entre législatif, exécutif et judiciaire ; "
                "le fédéral n'a que ses propres compétences, comme la défense (brève 4) "
                "(1 point)."
            ),
            "expected_points": [
                "Cite une décision régionale et sa norme (décret ou ordonnance)",
                "Cite une décision communautaire et sa norme (décret)",
                "Cite une décision communale ou le rôle d'un autre pouvoir",
                "Conclut sur la répartition et la séparation des pouvoirs",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Mini-situation à choix multiple
# =============================================================================================

_ID_CARD = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Zoé doit renouveler sa carte d'identité. Elle se rend au service population "
                "de l'administration la plus proche de chez elle. De quel niveau de pouvoir "
                "s'agit-il ?"
            ),
            "options": [
                {"option_id": "a", "label": "La commune"},
                {"option_id": "b", "label": "La province"},
                {"option_id": "c", "label": "La Communauté française"},
                {"option_id": "d", "label": "La Région wallonne"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "La commune est le niveau de pouvoir le plus proche du citoyen : elle s'occupe "
                "notamment de l'état civil et de la population (cartes d'identité)."
            ),
        },
        E,
    ),
)

FSE08_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE08", key="fse08-breves-qui-a-decide", title=NEWS_TITLE,
        content_text=NEWS_TEXT, layout=NEWS_LAYOUT, questions=_NEWS_QUESTIONS,
    ),
    FseCase(course_code="FSE08", key="fse08-carte-identite-commune", questions=_ID_CARD),
)
