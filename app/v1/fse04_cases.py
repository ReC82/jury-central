"""FSE04 « Normes, valeurs et influence sociale » — cas nouveaux (ticket #129).

Le cours et sa banque historique analysent le groupe en ligne « Fous rires du quotidien »
(vidéo humiliante partagée), le témoignage de Karim et un message privé. Les cas
ci-dessous gardent les mêmes notions (norme, valeur, besoin, comportement, frustration,
groupe d'appartenance, influence sociale, socialisation, limites de l'influence) dans
d'autres groupes et d'autres situations :

1. la conversation de l'équipe d'un garage le jour où un nouvel apprenti part sans avoir
   rangé son poste (norme implicite, pression du groupe, besoin, frustration,
   apprentissage des règles du groupe) ;
2. l'affiche du règlement d'une maison de jeunes (normes écrites et valeur affichée) ;
3. deux mini-situations à choix multiple (socialisation familiale, refus de suivre le
   groupe).

Personnes et lieux fictifs."""

from app.v1.fse04_content import FSE04_FRUSTRATION_TITLE, FSE04_GROUP_TITLE, FSE04_TESTIMONY_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE04_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE04_GROUP_TITLE, FSE04_TESTIMONY_TITLE, FSE04_FRUSTRATION_TITLE}),
    markers=("Fous rires", "Karim"),
)

# =============================================================================================
# Cas 1 — L'équipe d'un garage et le nouvel apprenti
# =============================================================================================

GARAGE_TITLE = "Conversation de l'équipe du garage Meurice — le poste de Lucas"
_GARAGE_CONTEXT = (
    "Groupe de messagerie des six mécaniciens du garage Meurice. Lucas, 17 ans, y fait son "
    "apprentissage depuis une semaine."
)
_GARAGE_GROUP = "Équipe atelier — garage Meurice"
_GARAGE_DAY = "Jeudi 16 janvier"
_GARAGE_MESSAGES = (
    ("Serge, chef d'atelier", "p1", "17 h 40",
     ("Qui a laissé le pont n° 2 avec les outils par terre ? Ici, personne ne part avant "
     "d'avoir rangé son poste.")),
    ("Anaïs", "p2", "17 h 42",
     ("C'est Lucas, il est parti à 17 h pile. On ne laisse jamais le boulot aux collègues du "
     "matin.")),
    ("Mehdi", "p3", "17 h 45",
     "La première semaine, j'ai fait pareil. Personne ne me l'avait dit."),
    ("Lucas", "p4", "18 h 10",
     ("Désolé, je devais aller chercher ma petite sœur à l'école à 17 h 15. Je ne savais "
     "pas qu'il fallait tout ranger. Ça m'énerve de passer pour quelqu'un qui s'en fiche.")),
    ("Serge, chef d'atelier", "p1", "18 h 25",
     ("Merci de l'avoir dit. Demain je te montre comment on range, et tu commenceras ton "
     "rangement à 16 h 45. Chez nous, on s'entraide, mais on ne laisse rien traîner : un "
     "outil par terre, c'est un accident.")),
)

GARAGE_TEXT = f"[{_GARAGE_CONTEXT}]\n\nGroupe : « {_GARAGE_GROUP} »\n{_GARAGE_DAY}\n" + "\n".join(
    f"{time} — {author} : « {text} »" for author, _tone, time, text in _GARAGE_MESSAGES
)

GARAGE_LAYOUT = {
    "kind": "chat",
    "notice": "Échange fictif — exercice pédagogique",
    "context": _GARAGE_CONTEXT,
    "group": _GARAGE_GROUP,
    "messages": [
        {"author": author, "tone": tone, "day": _GARAGE_DAY, "time": time, "text": text}
        for author, tone, time, text in _GARAGE_MESSAGES
    ],
}

_GARAGE_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": (
                "Dans la conversation de l'équipe du garage Meurice, quelle norme Lucas "
                "n'a-t-il pas respectée ? Cite le message qui l'exprime."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle formule la norme « ne pas partir avant d'avoir rangé "
                "son poste » (ne pas laisser le travail aux collègues) et cite le message de "
                "Serge (17 h 40) ou d'Anaïs (17 h 42)."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "Classe chaque élément de la conversation du garage : s'agit-il d'une norme, "
                "d'une valeur ou d'un besoin ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Norme", "Valeur", "Besoin"],
            "elements": [
                "Ranger son poste avant de partir",
                "L'entraide entre collègues",
                "Aller chercher sa petite sœur à l'école à 17 h 15",
                "Commencer le rangement à 16 h 45",
            ],
            "correct_categories": [0, 1, 2, 0],
            "explanation": (
                "Ranger son poste et commencer le rangement à 16 h 45 sont des règles de "
                "comportement attendues (normes) ; l'entraide est ce que l'équipe juge "
                "important (valeur) ; aller chercher sa sœur répond à un besoin de Lucas et "
                "de sa famille."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Le message de Lucas à 18 h 10 exprime-t-il une frustration ? Explique d'où "
                "elle vient."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle répond oui (« Ça m'énerve de passer pour quelqu'un qui "
                "s'en fiche ») et explique qu'elle vient du décalage entre son besoin (partir "
                "à l'heure pour sa sœur) ou son ignorance de la règle, et le reproche du "
                "groupe."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Le message de Mehdi (17 h 45) et la réponse de Serge (18 h 25) montrent "
                "comment un nouveau membre apprend les règles d'un groupe. Comment "
                "s'appelle ce processus, et comment se déroule-t-il ici ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle nomme la socialisation et explique qu'elle passe ici par "
                "l'expérience (Mehdi a appris en faisant l'erreur), puis par l'explication et "
                "la démonstration (Serge va montrer à Lucas comment ranger) : Lucas intègre "
                "les normes et valeurs de l'équipe."
            ),
            "max_length": 500,
        },
        H,
    ),
    (
        "long_answer",
        {
            "prompt": (
                "Rédige une réponse complète : explique comment l'équipe exerce une pression "
                "sur Lucas pour qu'il respecte la norme du groupe, puis explique pourquoi on "
                "ne peut pas réduire son comportement à un manque de respect envers ses "
                "collègues."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "3 points : pression du groupe identifiée (reproches publics de Serge et "
                "d'Anaïs devant toute l'équipe, rappel de la norme) (1 point) ; la norme est "
                "liée aux valeurs de l'équipe (entraide, sécurité : « un outil par terre, "
                "c'est un accident ») (1 point) ; nuance : Lucas avait un besoin (sa sœur) et "
                "ignorait une règle jamais expliquée, comme Mehdi avant lui ; son "
                "comportement ne s'explique pas seulement par le groupe ni par un manque de "
                "respect (1 point)."
            ),
            "expected_points": [
                "Identifie la pression du groupe (reproches devant l'équipe)",
                "Relie la norme aux valeurs de l'équipe (entraide, sécurité)",
                "Nuance avec le besoin de Lucas et la règle qu'il ignorait",
            ],
            "max_score": 3.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — L'affiche du règlement d'une maison de jeunes
# =============================================================================================

RULES_TITLE = "Affiche du règlement de la maison de jeunes « Le Tremplin »"
_RULES_ISSUER = "Maison de jeunes Le Tremplin — Jemeppe"
_RULES_KICKER = "Notre règlement"
_RULES_HEADLINE = "ICI, ON PREND LE TEMPS D'ÊTRE ENSEMBLE"
_RULES_DETAILS = (
    ("1-circle", "Pendant les activités, les téléphones restent dans les casiers."),
    ("2-circle", "On dit bonjour en arrivant et au revoir en partant."),
    ("3-circle", "Chacun aide à ranger la salle à la fin de la soirée."),
)
_RULES_FOOTER = (
    "Un jeune qui ne respecte pas le règlement en parle avec un animateur avant de revenir à "
    "l'activité."
)
_RULES_CONTEXT = "Affiche collée à l'entrée de la salle principale de la maison de jeunes."

RULES_TEXT = (
    f"[{_RULES_CONTEXT}]\n\nEn haut : « {_RULES_ISSUER} »\nBandeau : « {_RULES_KICKER} »\n"
    f"Titre : « {_RULES_HEADLINE} »\n"
    + "\n".join(f"Règle {index} : « {text} »" for index, (_icon, text) in enumerate(_RULES_DETAILS, start=1))
    + f"\nEn bas : « {_RULES_FOOTER} »"
)

RULES_LAYOUT = {
    "kind": "poster_sheet",
    "palette": "blue",
    "notice": "Affiche fictive — exercice pédagogique",
    "context": _RULES_CONTEXT,
    "issuer": _RULES_ISSUER,
    "kicker": _RULES_KICKER,
    "headline": _RULES_HEADLINE,
    "details": [{"icon": icon, "text": text} for icon, text in _RULES_DETAILS],
    "footer": _RULES_FOOTER,
}

_RULES_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": (
                "Sur l'affiche de la maison de jeunes « Le Tremplin », quelle phrase exprime "
                "une valeur plutôt qu'une norme ? Explique la différence."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite le titre « Ici, on prend le temps d'être "
                "ensemble » comme valeur (ce que le groupe juge important) et explique que les "
                "trois règles numérotées sont des normes (comportements concrets attendus)."
            ),
            "max_length": 400,
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Explique le lien entre la règle 1 de l'affiche (téléphones dans les casiers) "
                "et la valeur affichée par la maison de jeunes."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que la norme (laisser son téléphone au casier) "
                "met en pratique la valeur « prendre le temps d'être ensemble » : sans "
                "téléphone, les jeunes se parlent et participent à l'activité commune."
            ),
            "max_length": 400,
        },
        M,
    ),
)

# =============================================================================================
# Cas 3 — Mini-situations (choix multiple)
# =============================================================================================

_SORTING = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Depuis qu'il est petit, Malik voit ses parents trier les déchets. "
                "Aujourd'hui, dans son propre appartement, il trie sans même y penser. Quelle "
                "notion cette situation illustre-t-elle ?"
            ),
            "options": [
                {"option_id": "a", "label": "La frustration"},
                {"option_id": "b", "label": "La socialisation"},
                {"option_id": "c", "label": "Le besoin"},
                {"option_id": "d", "label": "La pression d'un groupe d'amis"},
            ],
            "correct_option_ids": ["b"],
            "explanation": (
                "Malik a intégré, dans sa famille, une norme et la valeur qui l'accompagne : "
                "c'est la socialisation. Elle peut se faire sans pression ni conflit."
            ),
        },
        E,
    ),
)

_REFUSAL = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Toute la bande d'amis d'Emma sèche le cours de sport du vendredi. Emma, "
                "elle, continue d'y aller, même si on se moque d'elle. Que montre cette "
                "situation ?"
            ),
            "options": [
                {"option_id": "a", "label": "Que l'influence d'un groupe est une tendance, pas une obligation absolue"},
                {"option_id": "b", "label": "Qu'Emma ne fait pas partie de ce groupe d'amis"},
                {"option_id": "c", "label": "Que le groupe n'exerce aucune pression"},
                {"option_id": "d", "label": "Que sécher le cours est une valeur du groupe"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Le groupe exerce bien une pression (moqueries), mais Emma garde sa "
                "responsabilité individuelle : l'influence sociale n'explique pas tous les "
                "comportements."
            ),
        },
        M,
    ),
)

FSE04_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE04", key="fse04-garage-apprenti", title=GARAGE_TITLE,
        content_text=GARAGE_TEXT, layout=GARAGE_LAYOUT, questions=_GARAGE_QUESTIONS,
    ),
    FseCase(
        course_code="FSE04", key="fse04-reglement-maison-de-jeunes", title=RULES_TITLE,
        content_text=RULES_TEXT, layout=RULES_LAYOUT, questions=_RULES_QUESTIONS,
    ),
    FseCase(course_code="FSE04", key="fse04-tri-des-dechets", questions=_SORTING),
    FseCase(course_code="FSE04", key="fse04-refus-du-groupe", questions=_REFUSAL),
)
