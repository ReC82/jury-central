"""FSE06 « Droits et comportements illicites en ligne » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur dix scénarios courts (Sarah harcelée dans
son groupe de classe, commerçant accusé, critique d'un restaurant…). Les cas ci-dessous
gardent les mêmes notions (liberté d'expression et ses limites, injure, accusation non
étayée, menace, discrimination, usurpation d'identité, intrusion informatique, diffusion
malveillante, cyberharcèlement, traitement de données sans base valable) dans d'autres
supports, où il faut repérer soi-même les indices :

1. la publication d'une maison de quartier qui change ses horaires, et les commentaires
   qu'elle reçoit (critique légitime, injure, accusation, menace, discrimination, faux
   compte) ;
2. la fiche de signalement d'une stagiaire (compte piraté, photos privées publiées pour
   humilier, messages moqueurs répétés) ;
3. deux mini-situations à choix multiple (application qui copie les contacts, critique
   d'une vidéo).

Comme le cours : aucun article de loi ni aucune peine. Personnes et organismes fictifs."""

from app.v1.fse06_content import FSE06_SCENARIOS_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE06_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE06_SCENARIOS_TITLE}),
    markers=("Sarah", "scénario ", "commerçant", "restaurant"),
)

# =============================================================================================
# Cas 1 — Les commentaires sous la publication d'une maison de quartier
# =============================================================================================

POST_TITLE = "Publication de la maison de quartier « Le Préau » et commentaires reçus"
_POST_AUTHOR = "Maison de quartier Le Préau"
_POST_TEXT = (
    "« À partir du 1er avril, l'espace jeux sera ouvert du lundi au vendredi de 14 h à 20 h, "
    "et fermé le samedi, faute d'animateurs disponibles. Merci de votre compréhension ! »"
)
_POST_STATS = ("👍 64 réactions", "💬 7 commentaires")
_POST_COMMENTS = (
    ("Inès Moreau", "IM", "p1", None, False,
     ("« Fermer le samedi, c'est une mauvaise idée : ceux qui ont cours en semaine ne pourront "
     "plus venir. Pourquoi ne pas fermer le lundi à la place ? »")),
    ("Dylan_88", "D8", "p2", None, False,
     "« Bande d'incapables, vous êtes des nuls. »"),
    ("Kev Lmb", "KL", "p3", None, False,
     ("« De toute façon, l'animateur Julien revend en cachette les consoles données par les "
     "habitants. »")),
    ("ombre_du_parc", "OP", "p4", None, False,
     "« Si vous fermez le samedi, je viendrai casser vos vitres un soir. »"),
    ("Marc D.", "MD", "p5", None, False,
     "« Cet espace devrait être interdit aux jeunes d'origine étrangère, ce serait plus calme. »"),
    ("Julien Animateur — Le Préau (officiel)", "JA", "p6", None, False,
     "« Info : à partir de lundi, l'entrée coûtera 20 € par jour. »"),
    ("Julien Maes", "JM", "company", "animateur du Préau, en réponse au commentaire précédent", True,
     ("« Attention : ce compte n'est pas le mien. Quelqu'un utilise mon nom et ma photo. Je "
     "n'ai jamais écrit ce message, l'entrée reste gratuite. »")),
)
_POST_CONTEXT = (
    "Publication de la page de la maison de quartier « Le Préau » sur un réseau social. Les "
    "commentaires sont affichés dans l'ordre où ils ont été écrits."
)

POST_TEXT = (
    f"[{_POST_CONTEXT}]\n\n{_POST_AUTHOR} :\n{_POST_TEXT}\n\n" + " — ".join(_POST_STATS)
    + "\n\nCommentaires :\n"
    + "\n".join(
        f"- {author}{f' ({badge})' if badge else ''} : {text}"
        for author, _initials, _tone, badge, _reply, text in _POST_COMMENTS
    )
)

POST_LAYOUT = {
    "kind": "social_post",
    "notice": "Publication et commentaires fictifs — exercice pédagogique",
    "context": _POST_CONTEXT,
    "network": "Réseau social",
    "author": _POST_AUTHOR,
    "initials": "LP",
    "tone": "company",
    "text": _POST_TEXT,
    "stats": list(_POST_STATS),
    "comments_title": "Commentaires",
    "comments": [
        {
            "author": author, "initials": initials, "tone": tone, "text": text,
            **({"badge": badge} if badge else {}), **({"reply": True} if reply else {}),
        }
        for author, initials, tone, badge, reply, text in _POST_COMMENTS
    ],
}

_POST_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "Sous la publication du Préau, quels commentaires restent dans le cadre de la "
                "liberté d'expression, et lesquels en dépassent les limites ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Couvert par la liberté d'expression", "Dépasse les limites"],
            "elements": [
                "Le commentaire d'Inès Moreau",
                "Le commentaire de Dylan_88",
                "Le commentaire d'ombre_du_parc",
                "Le commentaire de Marc D.",
            ],
            "correct_categories": [0, 1, 1, 1],
            "explanation": (
                "Inès critique une décision et propose une autre solution, sans insulte ni "
                "accusation : c'est une opinion. Dylan_88 insulte, ombre_du_parc menace et "
                "Marc D. veut exclure des jeunes en raison de leur origine."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "Associe chacun de ces commentaires au comportement en ligne qu'il illustre."
            ),
            "source_document_version_id": DOC,
            "categories": ["Injure", "Accusation non étayée", "Menace", "Discrimination"],
            "elements": [
                "« Bande d'incapables, vous êtes des nuls. »",
                "« L'animateur Julien revend en cachette les consoles données par les habitants. »",
                "« Je viendrai casser vos vitres un soir. »",
                "« Cet espace devrait être interdit aux jeunes d'origine étrangère. »",
            ],
            "correct_categories": [0, 1, 2, 3],
            "explanation": (
                "Insulte sans fait précis : injure. Fait précis et négatif affirmé sans preuve : "
                "accusation non étayée. Annonce d'un mal futur pour faire pression : menace. "
                "Exclusion fondée sur l'origine : discrimination."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quel comportement la réponse de Julien Maes révèle-t-elle ? Cite deux indices "
                "de la publication qui le montrent."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle nomme l'usurpation d'identité et cite deux indices : un "
                "compte « officiel » au nom de Julien qu'il dit ne pas être le sien ; son nom "
                "et sa photo utilisés sans accord ; un message qu'il n'a jamais écrit (entrée "
                "à 20 €), contredit par Julien."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Inès Moreau et Kev Lmb critiquent tous les deux le Préau. Pourquoi le "
                "commentaire de Kev Lmb dépasse-t-il les limites de la liberté d'expression, "
                "alors que celui d'Inès Moreau ne les dépasse pas ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique qu'Inès donne une opinion argumentée sur une "
                "décision (horaires), sans attaquer personne ; Kev Lmb affirme un fait précis et "
                "négatif (Julien revendrait les consoles) sans aucune preuve, ce qui nuit à la "
                "réputation d'une personne identifiable : accusation non étayée."
            ),
            "max_length": 500,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "La maison de quartier veut faire le tri dans les commentaires. Analyse-les : "
                "pour chaque commentaire problématique, nomme le comportement et l'indice qui "
                "le montre, puis explique pourquoi il ne faut pas supprimer celui d'Inès "
                "Moreau. Ne cite ni peine ni article de loi."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : injure (Dylan_88) et menace (ombre_du_parc) avec leurs indices "
                "(1 point) ; accusation non étayée (Kev Lmb) et discrimination (Marc D.) avec "
                "leurs indices (1 point) ; usurpation d'identité (faux compte de Julien, "
                "démenti par Julien Maes) (1 point) ; le commentaire d'Inès est une critique "
                "argumentée, protégée par la liberté d'expression (1 point)."
            ),
            "expected_points": [
                "Injure et menace reconnues, avec leurs indices",
                "Accusation non étayée et discrimination reconnues, avec leurs indices",
                "Usurpation d'identité reconnue (faux compte démenti)",
                "Critique d'Inès : opinion couverte par la liberté d'expression",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — La fiche de signalement d'Amina
# =============================================================================================

REPORT_TITLE = "Fiche de signalement remise à l'éducatrice du centre de formation Horizon"
_REPORT_CONTEXT = (
    "Amina, 18 ans, suit une formation en boulangerie au centre de formation Horizon. Elle "
    "remet cette fiche à son éducatrice."
)
_REPORT_ORG = "Centre de formation Horizon"
_REPORT_TYPE = "Fiche de signalement"
_REPORT_META = (
    ("Rédigée par", "Amina, stagiaire en boulangerie"),
    ("Remise à", "Mme Laurent, éducatrice"),
    ("Date", "4 février"),
)
_REPORT_PARAGRAPHS = (
    ("Le 6 janvier, Bastien a regardé par-dessus mon épaule quand je tapais le mot de passe de "
     "ma messagerie. Le soir même, quelqu'un s'est connecté à mon compte depuis un autre "
     "téléphone : j'ai reçu une alerte de connexion."),
    ("Le 8 janvier, des photos de moi en pyjama, que je n'avais envoyées qu'à ma sœur, ont été "
     "publiées dans le groupe « Promo boulangerie » (30 membres) avec le message « Regardez la "
     "future star, mdr ». Bastien a écrit ensuite dans le groupe : « C'était pour qu'elle ait "
     "honte. »"),
    ("Depuis, je reçois presque chaque jour, de plusieurs comptes de la promo, des messages "
     "moqueurs sur mon physique. J'ai demandé trois fois d'arrêter. Cela dure depuis quatre "
     "semaines."),
)
_REPORT_CLOSING = "Je n'ose plus venir aux cours pratiques."

REPORT_TEXT = (
    f"[{_REPORT_CONTEXT}]\n\n{_REPORT_ORG}\n{_REPORT_TYPE}\n"
    + "\n".join(f"{field} : {value}" for field, value in _REPORT_META)
    + "\n\n" + "\n\n".join(_REPORT_PARAGRAPHS) + f"\n\n{_REPORT_CLOSING}"
)

REPORT_LAYOUT = {
    "kind": "memo",
    "notice": "Document fictif — exercice pédagogique",
    "context": _REPORT_CONTEXT,
    "org": _REPORT_ORG,
    "doc_type": _REPORT_TYPE,
    "meta": [{"field": field, "value": value} for field, value in _REPORT_META],
    "paragraphs": list(_REPORT_PARAGRAPHS),
    "closing": _REPORT_CLOSING,
}

_REPORT_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": (
                "Quel comportement en ligne le premier paragraphe de la fiche d'Amina "
                "(6 janvier) décrit-il ? Justifie."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle nomme l'intrusion informatique : quelqu'un s'est "
                "connecté au compte de messagerie d'Amina sans son autorisation, avec un mot de "
                "passe vu par-dessus son épaule (alerte de connexion depuis un autre téléphone)."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "Associe chaque fait rapporté par Amina au comportement en ligne qu'il "
                "illustre."
            ),
            "source_document_version_id": DOC,
            "categories": [
                "Intrusion informatique", "Diffusion malveillante", "Cyberharcèlement",
                "Usurpation d'identité",
            ],
            "elements": [
                "Connexion à la messagerie d'Amina depuis un autre téléphone",
                "Publication des photos en pyjama « pour qu'elle ait honte »",
                "Messages moqueurs presque chaque jour depuis quatre semaines",
            ],
            "correct_categories": [0, 1, 2],
            "explanation": (
                "Accéder au compte d'autrui sans autorisation : intrusion. Publier des photos "
                "privées dans le but de nuire : diffusion malveillante. Messages hostiles "
                "répétés visant la même personne : cyberharcèlement. Personne ne se fait passer "
                "pour Amina : pas d'usurpation d'identité."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quels indices du troisième paragraphe montrent qu'il s'agit de "
                "cyberharcèlement, et pas d'une simple dispute ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite au moins deux indices : répétition (presque chaque "
                "jour), durée (quatre semaines), une même personne visée (Amina), plusieurs "
                "comptes, Amina a demandé trois fois d'arrêter ; conséquence : elle n'ose plus "
                "venir aux cours."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Pourquoi la publication du 8 janvier est-elle une diffusion malveillante, et "
                "pas un simple partage de photos ? Appuie-toi sur deux indices de la fiche."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite deux indices : les photos étaient privées (envoyées "
                "seulement à sa sœur) et ont été publiées sans son accord devant 30 personnes ; "
                "le but de nuire est explicite (« C'était pour qu'elle ait honte », message "
                "moqueur « Regardez la future star, mdr »)."
            ),
            "max_length": 500,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 et 4 — Mini-situations à choix multiple
# =============================================================================================

_QUIZ_APP = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Une application de quiz gratuite copie toute la liste de contacts du "
                "téléphone de ses utilisateurs, sans les en informer ni expliquer à quoi "
                "cette liste servira. De quel comportement s'agit-il ?"
            ),
            "options": [
                {"option_id": "a", "label": "Un cyberharcèlement"},
                {"option_id": "b", "label": "Une usurpation d'identité"},
                {"option_id": "c", "label": "Un traitement de données sans base valable"},
                {"option_id": "d", "label": "Une injure"},
            ],
            "correct_option_ids": ["c"],
            "explanation": (
                "Collecter des données personnelles (les contacts) sans justification ni "
                "information des personnes concernées, c'est un traitement de données sans "
                "base valable."
            ),
        },
        E,
    ),
)

_VIDEO_REVIEW = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Sous la vidéo d'un créateur de contenu, Léon écrit : « Ta dernière vidéo est "
                "longue et ennuyeuse, j'ai décroché au bout de cinq minutes. » Comment "
                "qualifier ce commentaire ?"
            ),
            "options": [
                {"option_id": "a", "label": "Une critique couverte par la liberté d'expression"},
                {"option_id": "b", "label": "Une injure, parce qu'il est négatif"},
                {"option_id": "c", "label": "Une accusation non étayée"},
                {"option_id": "d", "label": "Une menace"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Léon donne son avis sur une vidéo, sans insulte, sans affirmer de fait "
                "précis contre la personne et sans menace : une critique, même sévère, reste "
                "dans le cadre de la liberté d'expression."
            ),
        },
        M,
    ),
)

FSE06_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE06", key="fse06-commentaires-maison-quartier", title=POST_TITLE,
        content_text=POST_TEXT, layout=POST_LAYOUT, questions=_POST_QUESTIONS,
    ),
    FseCase(
        course_code="FSE06", key="fse06-signalement-stagiaire", title=REPORT_TITLE,
        content_text=REPORT_TEXT, layout=REPORT_LAYOUT, questions=_REPORT_QUESTIONS,
    ),
    FseCase(course_code="FSE06", key="fse06-application-contacts", questions=_QUIZ_APP),
    FseCase(course_code="FSE06", key="fse06-critique-video", questions=_VIDEO_REVIEW),
)
