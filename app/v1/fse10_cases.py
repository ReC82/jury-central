"""FSE10 « Élections et participation citoyenne » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur le tableau daté des scrutins belges et sur
les quatre bulletins fictifs A à D. Les cas ci-dessous gardent les mêmes notions (scrutin
proportionnel et coalition, vote valable/blanc/nul, abstention, procuration, témoin du
dépouillement, pétition, consultation populaire, règle électorale propre à un scrutin et à
une région) mais les appliquent à d'autres supports : la feuille de résultats d'une commune
fictive et la conversation de jeunes électeurs la veille d'un scrutin communal.

Aucune règle n'est inventée ni généralisée : la seule règle régionale citée (vote communal
plus obligatoire en Région flamande depuis le scrutin du 13 octobre 2024, toujours
obligatoire en Wallonie) est celle du tableau daté du cours ; aucune condition d'âge n'est
mobilisée. Les sièges de la feuille de résultats suivent une répartition proportionnelle
(vérifiée avec la méthode D'Hondt), sans que la méthode soit enseignée ni demandée."""

from app.v1.fse10_content import FSE10_BALLOTS_TITLE, FSE10_TABLE_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE10_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE10_TABLE_TITLE, FSE10_BALLOTS_TITLE}),
    markers=("Bulletin A", "bulletin D", "D'après le tableau", "tableau daté"),
)

# =============================================================================================
# Cas 1 — Feuille de résultats d'un scrutin communal
# =============================================================================================

RESULTS_TITLE = "Résultats du scrutin communal de Valbrise — feuille affichée le soir du vote"
_RESULTS_CONTEXT = (
    "Feuille de résultats affichée à l'administration communale le soir du scrutin, dans une "
    "commune fictive de Wallonie. Listes et chiffres fictifs."
)
_RESULTS_HEADING = "Conseil communal de Valbrise : 27 sièges à pourvoir"
_RESULTS_ROWS = (
    ("Liste Horizon", "4 860 voix", "11 sièges"),
    ("Liste Avenir", "3 520 voix", "8 sièges"),
    ("Liste Valbrise Verte", "2 210 voix", "5 sièges"),
    ("Liste Ensemble", "1 310 voix", "3 sièges"),
    ("Bulletins blancs et nuls", "410 bulletins", "—"),
)
_RESULTS_NOTE = "Pour former une majorité au conseil communal, il faut au moins 14 sièges sur 27."

RESULTS_TEXT = (
    f"[{_RESULTS_CONTEXT}]\n\n{_RESULTS_HEADING}\n"
    + "\n".join(" — ".join(row) for row in _RESULTS_ROWS)
    + f"\n\n{_RESULTS_NOTE}"
)

RESULTS_LAYOUT = {
    "kind": "table",
    "notice": "Résultats fictifs — exercice pédagogique",
    "context": _RESULTS_CONTEXT,
    "heading": _RESULTS_HEADING,
    "columns": ["Liste", "Voix obtenues", "Sièges obtenus"],
    "rows": [list(row) for row in _RESULTS_ROWS],
    "note": _RESULTS_NOTE,
}

_RESULTS_QUESTIONS = (
    (
        "multiple_choice",
        {
            "prompt": (
                "D'après la feuille de résultats de Valbrise, la Liste Horizon, arrivée en "
                "tête, peut-elle diriger seule la commune ?"
            ),
            "source_document_version_id": DOC,
            "options": [
                {"option_id": "a", "label": "Non : avec 11 sièges sur 27, elle doit former une coalition pour atteindre 14 sièges"},
                {"option_id": "b", "label": "Oui : la liste arrivée en tête obtient automatiquement la majorité"},
                {"option_id": "c", "label": "Oui : elle a obtenu plus de voix que chacune des autres listes"},
                {"option_id": "d", "label": "Non : il faut organiser un nouveau scrutin"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Avec le scrutin proportionnel, les sièges sont répartis entre toutes les "
                "listes. 11 sièges ne suffisent pas pour la majorité (14) : il faut un accord "
                "avec une ou plusieurs autres listes, une coalition."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "La Liste Ensemble a obtenu beaucoup moins de voix que les autres. Pourquoi "
                "obtient-elle quand même 3 sièges au conseil communal ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique le scrutin proportionnel : les sièges sont "
                "répartis entre les listes selon leur nombre de voix, pas seulement attribués à "
                "la liste arrivée en tête ; avec 1 310 voix, la Liste Ensemble reçoit une part "
                "des sièges proportionnée à son score."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "classification",
        {
            "prompt": (
                "Après le scrutin, plusieurs coalitions sont envisagées à Valbrise. Lesquelles "
                "réunissent une majorité au conseil communal ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Majorité (14 sièges ou plus)", "Pas de majorité"],
            "elements": [
                "Liste Horizon + Liste Valbrise Verte",
                "Liste Avenir + Liste Valbrise Verte",
                "Liste Horizon + Liste Ensemble",
                "Liste Avenir + Liste Valbrise Verte + Liste Ensemble",
                "Liste Valbrise Verte + Liste Ensemble",
            ],
            "correct_categories": [0, 1, 0, 0, 1],
            "explanation": (
                "On additionne les sièges : 11 + 5 = 16 (majorité) ; 8 + 5 = 13 (non) ; "
                "11 + 3 = 14 (majorité, de justesse) ; 8 + 5 + 3 = 16 (majorité, sans la liste "
                "arrivée en tête) ; 5 + 3 = 8 (non)."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "La feuille de résultats mentionne 410 bulletins blancs et nuls. Ces bulletins "
                "comptent-ils dans la répartition des 27 sièges ? Profitent-ils à une liste ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle indique que les bulletins blancs et nuls ne comptent pas "
                "dans la répartition des sièges et ne profitent à aucune liste ; seuls les votes "
                "valables (un choix clair pour une seule liste) sont pris en compte. Les "
                "électeurs concernés se sont pourtant bien présentés pour voter."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Le lendemain, un journal local titre : « La Liste Horizon a gagné, elle "
                "dirigera seule la commune. » À l'aide de la feuille de résultats, explique "
                "pourquoi ce titre est trompeur et ce qui doit se passer pour qu'une majorité "
                "dirige Valbrise."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : la Liste Horizon arrive bien en tête (le plus de voix et de "
                "sièges) (1 point) ; mais 11 sièges sur 27 ne font pas une majorité, il en faut "
                "14 (1 point) ; le scrutin proportionnel a réparti les sièges entre les quatre "
                "listes, d'où la nécessité d'une coalition (1 point) ; au moins une coalition "
                "majoritaire possible chiffrée, par exemple Horizon + Valbrise Verte (16) ou "
                "Avenir + Valbrise Verte + Ensemble (16), ce qui montre que la liste arrivée en "
                "tête pourrait même ne pas gouverner (1 point)."
            ),
            "expected_points": [
                "Reconnaît que la Liste Horizon arrive en tête",
                "11 sièges sur 27 : pas de majorité (14 nécessaires)",
                "Relie scrutin proportionnel et coalition",
                "Propose une coalition majoritaire chiffrée",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Conversation de jeunes électeurs la veille du scrutin
# =============================================================================================

CHAT_TITLE = "Conversation du groupe « Premiers votes — Liège »"
_CHAT_CONTEXT = (
    "Groupe d'une application de messagerie réunissant des amis de 18 à 20 ans qui habitent "
    "Liège (Région wallonne), la veille d'un scrutin communal. Échange fictif."
)
_CHAT_DAY = "Samedi 10 octobre"
_CHAT_MESSAGES = (
    ("Thomas", "p1", "17 h 30",
     ("Demain je suis en stage à l'étranger pour mes études. Je ne pourrai pas voter, tant "
      "pis : je ne fais rien.")),
    ("Léa", "p2", "17 h 34", "Moi je n'irai pas au bureau de vote : comme ça, c'est un vote blanc."),
    ("Jonas", "p3", "17 h 36",
     ("Mon cousin habite Gand : il m'a dit que pour les communales, il n'est plus obligé "
      "d'aller voter. Donc c'est pareil pour nous à Liège.")),
    ("Amira", "p4", "17 h 41",
     ("Ma mère a été désignée par une liste pour assister au comptage des voix demain soir, "
      "dans un bureau de dépouillement.")),
    ("Thomas", "p1", "17 h 45",
     ("Au fait, la pétition pour le skatepark qu'on a signée à 600 : la commune est obligée de "
      "le construire maintenant !")),
    ("Léa", "p2", "17 h 52",
     ("Le bourgmestre veut organiser une consultation populaire sur le nouveau plan de "
      "circulation. Si le oui gagne, la commune devra obligatoirement l'appliquer ?")),
)

CHAT_TEXT = f"[{_CHAT_CONTEXT}]\n\n{_CHAT_DAY}\n" + "\n".join(
    f"{time} — {author} : « {text} »" for author, _tone, time, text in _CHAT_MESSAGES
)

CHAT_LAYOUT = {
    "kind": "chat",
    "notice": "Échange fictif — exercice pédagogique",
    "context": _CHAT_CONTEXT,
    "group": "Premiers votes — Liège",
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
                "Quel mécanisme de participation correspond à chacun de ces éléments de la "
                "conversation ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Procuration", "Témoin du dépouillement", "Pétition", "Consultation populaire"],
            "elements": [
                "Mandater un ami pour voter à la place de Thomas pendant son stage",
                "Le rôle de la mère d'Amira demain soir",
                "Les 600 signatures pour le skatepark",
                "L'avis demandé aux habitants sur le plan de circulation",
            ],
            "correct_categories": [0, 1, 2, 3],
            "explanation": (
                "La procuration permet à un électeur absent de mandater quelqu'un ; le témoin, "
                "désigné par une liste, assiste au comptage ; la pétition est une demande "
                "collective ; la consultation populaire recueille l'avis des habitants sur une "
                "question précise."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Léa écrit à 17 h 34 que ne pas aller au bureau de vote revient à voter blanc. "
                "Explique son erreur."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle distingue abstention et vote blanc : ne pas se présenter "
                "est une abstention (aucun acte de vote, sanctionnable là où le vote est "
                "obligatoire, comme pour les communales en Wallonie) ; voter blanc suppose de se "
                "présenter et de déposer un bulletin sans aucune marque."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Jonas conclut (17 h 36) que, comme son cousin de Gand, il n'est plus obligé de "
                "voter aux communales à Liège. Pourquoi son raisonnement est-il faux ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique qu'une règle électorale dépend du scrutin et de "
                "la région : depuis le scrutin communal du 13 octobre 2024, le vote n'est plus "
                "obligatoire en Région flamande (Gand) pour les communales, mais il reste "
                "obligatoire en Région wallonne (Liège). On ne généralise pas la règle d'une "
                "région à une autre."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "multiple_choice",
        {
            "prompt": (
                "Thomas affirme à 17 h 45 que la commune est obligée de construire le "
                "skatepark grâce aux 600 signatures. Que faut-il lui répondre ?"
            ),
            "source_document_version_id": DOC,
            "options": [
                {"option_id": "a", "label": "Non : une pétition est une demande collective, sans effet contraignant automatique"},
                {"option_id": "b", "label": "Oui : une pétition oblige l'autorité à agir dès 500 signatures"},
                {"option_id": "c", "label": "Oui : une pétition a la même valeur qu'un vote au conseil communal"},
                {"option_id": "d", "label": "Non : une pétition n'est possible qu'au niveau fédéral"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "La pétition permet de faire connaître une demande à une autorité, qui n'est pas "
                "automatiquement tenue d'y donner suite."
            ),
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Rédige la réponse que tu enverrais dans le groupe à Thomas (17 h 30) et à Léa "
                "(17 h 52) : explique à chacun ce qu'il peut faire ou ce qu'il faut savoir, en "
                "utilisant le vocabulaire du cours."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : Thomas peut donner une procuration, c'est-à-dire mandater une autre "
                "personne pour voter à sa place (1 point) ; ne rien faire serait une abstention, "
                "alors que le vote communal est obligatoire en Wallonie (1 point) ; pour Léa, la "
                "consultation populaire recueille l'avis des habitants sur une question précise "
                "(1 point) ; son résultat ne lie pas obligatoirement la commune : ce n'est pas un "
                "référendum contraignant (1 point)."
            ),
            "expected_points": [
                "Thomas : procuration (mandater quelqu'un)",
                "Ne rien faire = abstention, alors que le vote est obligatoire à Liège",
                "Léa : la consultation recueille un avis",
                "Le résultat de la consultation ne s'impose pas automatiquement",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 — Mini-situation à choix multiple
# =============================================================================================

_SLOGAN_BALLOT = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Au bureau de vote, Malik dépose dans l'urne un bulletin sur lequel il n'a "
                "coché aucune case, mais où il a écrit « Tous pareils ! » en travers de la page. "
                "Comment ce vote est-il compté ?"
            ),
            "options": [
                {"option_id": "a", "label": "Vote nul : l'inscription personnelle invalide le bulletin"},
                {"option_id": "b", "label": "Vote blanc : aucune case n'est cochée"},
                {"option_id": "c", "label": "Vote valable, réparti entre toutes les listes"},
                {"option_id": "d", "label": "Abstention : Malik n'a choisi personne"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Un vote blanc ne comporte aucune marque ; une inscription personnelle rend le "
                "bulletin nul. Malik s'est présenté et a voté : ce n'est pas une abstention."
            ),
        },
        E,
    ),
)

FSE10_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE10", key="fse10-resultats-valbrise", title=RESULTS_TITLE,
        content_text=RESULTS_TEXT, layout=RESULTS_LAYOUT, questions=_RESULTS_QUESTIONS,
    ),
    FseCase(
        course_code="FSE10", key="fse10-premiers-votes-liege", title=CHAT_TITLE,
        content_text=CHAT_TEXT, layout=CHAT_LAYOUT, questions=_CHAT_QUESTIONS,
    ),
    FseCase(course_code="FSE10", key="fse10-bulletin-tous-pareils", questions=_SLOGAN_BALLOT),
)
