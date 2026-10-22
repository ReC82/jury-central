"""FSE09 « Qui décide de quoi ? » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur les dix situations du cours (procédure
pénale, aides aux entreprises, programmes de cours, bancs publics, mission internationale…).
Les cas ci-dessous gardent les mêmes notions (compétences du fédéral, des Régions, des
Communautés, des communes et rôle d'appui des provinces ; matière partagée entre plusieurs
niveaux, sans réponse unique trompeuse) mais les appliquent à d'autres situations : les
demandes reçues par une permanence d'information citoyenne et une conversation de voisins
qui se trompent d'interlocuteur.

Les compétences citées restent celles du cours : justice, sécurité sociale (chômage,
assurance maladie) et défense au fédéral ; logement, emploi, environnement et économie aux
Régions ; enseignement, culture et jeunesse aux Communautés ; voirie de proximité à la
commune ; appui technique aux communes pour la province. Personnes et demandes fictives."""

from app.v1.fse09_content import FSE09_SITUATIONS_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE09_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE09_SITUATIONS_TITLE}),
    markers=("situation 4", "situation 5", "situation 8", "situation 9", "situation 10", "Situation 6"),
)

# =============================================================================================
# Cas 1 — Les demandes d'une permanence « Qui contacter ? »
# =============================================================================================

DESK_TITLE = "Permanence « Qui contacter ? » — neuf demandes notées un mercredi"
_DESK_CONTEXT = (
    "Fiches remplies par une bénévole lors de la permanence d'information d'une maison "
    "citoyenne, dans une commune de Wallonie. Personnes et demandes fictives."
)
_DESK = (
    ("bi-house", "Toit à isoler",
     ("Madame Lemaire veut isoler le toit de la maison qu'elle habite en Wallonie. Elle demande "
      "quelle aide existe pour rénover son logement.")),
    ("bi-mortarboard", "Changer d'école",
     ("Yanis, 13 ans, veut changer d'école secondaire francophone en cours d'année. Sa mère "
      "demande qui fixe les règles d'inscription dans ces écoles.")),
    ("bi-cone-striped", "Trottoir abîmé",
     ("Monsieur Ferreira signale un trou profond dans le trottoir d'une petite rue du centre "
      "du village, juste devant l'arrêt de bus.")),
    ("bi-cash-coin", "Allocations de chômage",
     ("Sofia vient de perdre son emploi. Elle demande quelles règles fixent le droit aux "
      "allocations de chômage et leur montant, les mêmes partout en Belgique.")),
    ("bi-briefcase", "Trouver du travail",
     ("Kevin, demandeur d'emploi en Wallonie, cherche un service public qui l'aide à trouver "
      "des offres d'emploi et à préparer ses entretiens d'embauche.")),
    ("bi-music-note-beamed", "Atelier de musique",
     ("Un groupe de jeunes veut créer un atelier de musique et demande s'il existe un subside "
      "pour les maisons de jeunes francophones.")),
    ("bi-bank", "Mur mitoyen",
     ("Monsieur et Madame Diallo veulent porter devant un tribunal leur conflit avec un voisin "
      "au sujet d'un mur mitoyen.")),
    ("bi-heart-pulse", "Diabète",
     ("Marc, diabétique, demande qui rembourse ses consultations chez le médecin (sa "
      "mutualité, dans le cadre de l'assurance maladie-invalidité) et qui organise les "
      "campagnes de prévention du diabète dans les écoles francophones.")),
    ("bi-tools", "Projet de la commune voisine",
     ("Une échevine d'une petite commune voisine cherche un appui technique pour préparer un "
      "projet local que les services de sa commune ne peuvent pas étudier seuls.")),
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
            "prompt": (
                "Pour chacune de ces demandes de la permanence, quel niveau de pouvoir est "
                "compétent ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Fédéral", "Région", "Communauté", "Commune"],
            "elements": [
                "Demande 2 — changer d'école secondaire francophone",
                "Demande 3 — trou dans le trottoir d'une rue du village",
                "Demande 4 — règles des allocations de chômage",
                "Demande 5 — aide pour trouver des offres d'emploi",
            ],
            "correct_categories": [2, 3, 0, 1],
            "explanation": (
                "L'enseignement relève des Communautés ; la voirie de proximité, de la commune ; "
                "le chômage fait partie de la sécurité sociale, fédérale ; l'emploi (aide à la "
                "recherche d'emploi) relève des Régions."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": "Et pour ces trois autres demandes, quel niveau de pouvoir est compétent ?",
            "source_document_version_id": DOC,
            "categories": ["Fédéral", "Région", "Communauté", "Commune"],
            "elements": [
                "Demande 1 — aide pour rénover son logement",
                "Demande 6 — subside pour une maison de jeunes francophone",
                "Demande 7 — conflit porté devant un tribunal",
            ],
            "correct_categories": [1, 2, 0],
            "explanation": (
                "Le logement est une compétence régionale ; la jeunesse et la culture relèvent "
                "des Communautés ; la justice est une compétence fédérale."
            ),
        },
        M,
    ),
    (
        "classification",
        {
            "prompt": "Quelle matière est concernée par chacune de ces demandes ?",
            "source_document_version_id": DOC,
            "categories": ["Logement", "Enseignement", "Emploi", "Justice", "Sécurité sociale"],
            "elements": [
                "Demande 1 — Madame Lemaire",
                "Demande 2 — Yanis",
                "Demande 4 — Sofia",
                "Demande 5 — Kevin",
                "Demande 7 — Monsieur et Madame Diallo",
            ],
            "correct_categories": [0, 1, 4, 2, 3],
            "explanation": (
                "On identifie d'abord la matière : rénover son logement (logement), changer "
                "d'école (enseignement), allocations de chômage (sécurité sociale), trouver du "
                "travail (emploi), conflit devant un tribunal (justice)."
            ),
        },
        M,
    ),
    (
        "multiple_choice",
        {
            "prompt": (
                "Demande 9 : vers quel niveau de pouvoir la bénévole doit-elle orienter "
                "l'échevine qui cherche un appui technique pour un projet de sa commune ?"
            ),
            "source_document_version_id": DOC,
            "options": [
                {"option_id": "a", "label": "La province"},
                {"option_id": "b", "label": "La Communauté française"},
                {"option_id": "c", "label": "Le niveau fédéral"},
                {"option_id": "d", "label": "Aucun : une commune doit toujours se débrouiller seule"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Les provinces jouent un rôle d'appui technique aux communes de leur territoire "
                "pour des projets d'intérêt local."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Les demandes 4 et 5 concernent toutes les deux une personne sans emploi. "
                "Pourquoi ne relèvent-elles pas du même niveau de pouvoir ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle distingue les deux matières : les allocations de chômage "
                "(demande 4) font partie de la sécurité sociale, compétence fédérale, avec des "
                "règles identiques dans tout le pays ; l'aide à la recherche d'emploi (demande "
                "5) relève de l'emploi, compétence des Régions. C'est la matière, pas la "
                "personne, qui détermine le niveau compétent."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "La bénévole hésite pour la demande 8 (Marc, diabétique). Peut-elle lui "
                "indiquer un seul niveau de pouvoir ? Justifie à partir de la demande."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que non : la santé est une matière partagée. Le "
                "remboursement des consultations par la mutualité relève de l'assurance "
                "maladie-invalidité (sécurité sociale, fédéral) ; la prévention (campagnes dans "
                "les écoles francophones) relève des matières personnalisables, gérées par les "
                "Communautés. Une réponse donnant un seul niveau est incorrecte."
            ),
            "max_length": 400,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Rédige la réponse d'orientation de la bénévole pour les demandes 1, 2 et 7 : "
                "pour chacune, le niveau de pouvoir à contacter, la matière concernée et une "
                "justification."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : demande 1 — Région, logement, matière liée au territoire (1 point) ; "
                "demande 2 — Communauté (française), enseignement, matière liée aux personnes et "
                "à la langue (1 point) ; demande 7 — fédéral, justice, compétence exercée pour "
                "tout le pays (1 point) ; justifications fondées sur la matière plutôt que sur le "
                "lieu où habite la personne ou sur l'administration la plus proche (1 point)."
            ),
            "expected_points": [
                "Demande 1 : Région, logement",
                "Demande 2 : Communauté, enseignement",
                "Demande 7 : fédéral, justice",
                "Justifie chaque fois par la matière concernée",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Conversation de voisins : à qui s'adresser ?
# =============================================================================================

CHAT_TITLE = "Conversation du groupe « Voisins de la rue des Glycines »"
_CHAT_CONTEXT = (
    "Groupe d'une application de messagerie réunissant des habitants d'une même rue, dans une "
    "commune de Wallonie. Échange fictif."
)
_CHAT_DAY = "Jeudi 12 mars"
_CHAT_MESSAGES = (
    ("Luc", "p1", "19 h 02",
     ("Le trottoir devant l'école est dangereux depuis des mois. J'ai écrit au Premier "
      "ministre : c'est à lui de le faire réparer !")),
    ("Fatima", "p2", "19 h 05",
     ("Ma fille entre en secondaire. Je vais demander au bourgmestre de changer le programme "
      "de maths des écoles francophones, c'est la commune qui décide des cours.")),
    ("Bernard", "p3", "19 h 11",
     ("Pour l'usine de recyclage qui veut s'installer près du village, c'est la Région qui "
      "accorde le permis : l'environnement est une compétence régionale.")),
    ("Luc", "p1", "19 h 13", "De toute façon, en Belgique, c'est le fédéral qui décide de tout."),
    ("Nadia", "p4", "19 h 20",
     ("Pas de tout ! Mais la défense et la justice, oui : ce sont des compétences fédérales, "
      "pour tout le pays.")),
)

CHAT_TEXT = f"[{_CHAT_CONTEXT}]\n\n{_CHAT_DAY}\n" + "\n".join(
    f"{time} — {author} : « {text} »" for author, _tone, time, text in _CHAT_MESSAGES
)

CHAT_LAYOUT = {
    "kind": "chat",
    "notice": "Échange fictif — exercice pédagogique",
    "context": _CHAT_CONTEXT,
    "group": "Voisins de la rue des Glycines",
    "messages": [
        {"author": author, "tone": tone, "day": _CHAT_DAY, "time": time, "text": text}
        for author, tone, time, text in _CHAT_MESSAGES
    ],
}

_CHAT_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "Dans la conversation des voisins, chaque message attribue une décision à un "
                "niveau de pouvoir. L'attribution est-elle correcte ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Attribution correcte", "Attribution erronée"],
            "elements": [
                "Luc, 19 h 02 — le trottoir devant l'école",
                "Fatima, 19 h 05 — le programme de maths",
                "Bernard, 19 h 11 — le permis de l'usine de recyclage",
                "Nadia, 19 h 20 — la défense et la justice",
            ],
            "correct_categories": [1, 1, 0, 0],
            "explanation": (
                "Le trottoir relève de la commune (proximité), pas du Premier ministre ; les "
                "programmes des écoles francophones relèvent de la Communauté française, pas de "
                "la commune. L'environnement est bien régional ; la défense et la justice sont "
                "bien fédérales."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Luc a écrit au Premier ministre pour le trottoir devant l'école (19 h 02). À "
                "quel niveau de pouvoir aurait-il dû s'adresser, et pourquoi ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle indique la commune et justifie par la proximité : "
                "l'entretien des trottoirs et de la voirie locale est une compétence communale ; "
                "le Premier ministre dirige le gouvernement fédéral, qui n'en est pas chargé."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Rédige un message court et respectueux pour le groupe des voisins : corrige les "
                "deux attributions erronées de la conversation et réponds à l'affirmation de "
                "Luc à 19 h 13, en nommant chaque fois le niveau de pouvoir et la matière."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : trottoir — commune, voirie de proximité (1 point) ; programme de "
                "maths — Communauté française, enseignement (1 point) ; réponse à « le fédéral "
                "décide de tout » : les compétences sont réparties entre plusieurs niveaux, le "
                "fédéral n'a que les siennes (défense, justice…), exemple tiré du groupe comme "
                "l'environnement régional (1 point) ; ton respectueux et explication par la "
                "matière, sans moquerie (1 point)."
            ),
            "expected_points": [
                "Trottoir : commune (proximité)",
                "Programme scolaire : Communauté française (enseignement)",
                "Réfute « le fédéral décide de tout » avec un exemple",
                "Message respectueux qui justifie par la matière",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 — Mini-situation à choix multiple
# =============================================================================================

_BAKERY = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Samir ouvre une boulangerie en Wallonie et demande une aide publique à "
                "l'installation pour sa nouvelle entreprise. Quel niveau de pouvoir est "
                "compétent pour cette aide ?"
            ),
            "options": [
                {"option_id": "a", "label": "La Région wallonne, compétente pour l'économie"},
                {"option_id": "b", "label": "La Communauté française, compétente pour la culture"},
                {"option_id": "c", "label": "Le niveau fédéral, compétent pour la défense"},
                {"option_id": "d", "label": "La commune, compétente pour l'état civil"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Les aides aux entreprises relèvent de l'économie, une compétence des Régions : "
                "l'entreprise est installée sur le territoire wallon."
            ),
        },
        E,
    ),
)

FSE09_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE09", key="fse09-permanence-qui-contacter", title=DESK_TITLE,
        content_text=DESK_TEXT, layout=DESK_LAYOUT, questions=_DESK_QUESTIONS,
    ),
    FseCase(
        course_code="FSE09", key="fse09-voisins-rue-des-glycines", title=CHAT_TITLE,
        content_text=CHAT_TEXT, layout=CHAT_LAYOUT, questions=_CHAT_QUESTIONS,
    ),
    FseCase(course_code="FSE09", key="fse09-boulangerie-aide-installation", questions=_BAKERY),
)
