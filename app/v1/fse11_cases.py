"""FSE11 « Partis politiques et choix argumenté » — cas nouveaux (ticket #129).

Le cours et sa banque historique s'appuient sur six extraits sourcés décrivant six partis
belges réels et sur deux propositions fictives (partis imaginaires « Alpha » et « Beta »).
Les cas ci-dessous gardent les mêmes notions (familles socialiste, libérale, écologiste,
centriste/humaniste ; axe gauche-centre-droite comme repère simplifié ; comparaison neutre
par valeurs, priorités et effets attendus) mais sur d'autres supports : quatre tracts de
listes imaginaires et trois réponses d'élèves à une consigne de comparaison.

Neutralité : aucune liste réelle n'est décrite ni évaluée ; les tracts sont rédigés pour
l'exercice, chacun avec ses propres arguments, et aucune question ne demande d'opinion."""

from app.v1.fse11_content import FSE11_PARTIES_TITLE, FSE11_PROPOSALS_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE11_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE11_PARTIES_TITLE, FSE11_PROPOSALS_TITLE}),
    markers=("Alpha", "Beta", "Extrait 1", "extrait 3", "extrait 4", "extrait 6", "proposition fictive A"),
)

# =============================================================================================
# Cas 1 — Quatre tracts de listes imaginaires
# =============================================================================================

TRACTS_TITLE = "Quatre tracts distribués avant une élection dans un pays imaginaire"
_TRACTS_CONTEXT = (
    "Tracts rédigés pour l'exercice. Les listes portent des noms d'arbres et n'existent pas ; "
    "chaque tract résume les idées mises en avant par sa liste."
)
_TRACTS = (
    ("bi-hospital", "Liste Saule",
     ("Des services publics forts pour tous : des soins de santé accessibles, une école "
      "publique gratuite et une sécurité sociale solidaire, financées par une contribution plus "
      "grande des revenus les plus élevés.")),
    ("bi-shop", "Liste Chêne",
     ("Moins de charges et de formalités pour celles et ceux qui entreprennent : c'est "
      "l'initiative de chacun qui crée l'emploi. L'État doit se limiter à l'essentiel.")),
    ("bi-tree", "Liste Érable",
     ("Isoler les logements, développer les transports en commun, protéger la biodiversité : "
      "préparons une société durable pour les générations futures.")),
    ("bi-people", "Liste Bouleau",
     ("Ni tout à l'État, ni tout au marché : le dialogue entre tous, l'attention portée à "
      "chaque personne et aux familles, pour une politique du juste milieu.")),
)

TRACTS_TEXT = f"[{_TRACTS_CONTEXT}]\n\n" + "\n\n".join(
    f"Tract {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_TRACTS, start=1)
)

TRACTS_LAYOUT = {
    "kind": "cards",
    "notice": "Listes imaginaires — exercice pédagogique",
    "context": _TRACTS_CONTEXT,
    "item_label": "Tract",
    "items": [
        {"number": index, "label": f"Tract {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_TRACTS, start=1)
    ],
}

_TRACTS_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "À quelle famille politique se rattache le plus probablement chacun des quatre tracts ?",
            "source_document_version_id": DOC,
            "categories": ["Socialiste", "Libérale", "Écologiste", "Centriste/humaniste"],
            "elements": ["Tract 1 — Liste Saule", "Tract 2 — Liste Chêne", "Tract 3 — Liste Érable", "Tract 4 — Liste Bouleau"],
            "correct_categories": [0, 1, 2, 3],
            "explanation": (
                "Saule met en avant la solidarité et les services publics (socialiste) ; Chêne, "
                "l'initiative individuelle et un État limité (libérale) ; Érable, la société "
                "durable et l'environnement (écologiste) ; Bouleau, le juste milieu, le dialogue "
                "et l'attention à la personne (centriste/humaniste)."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quels mots du tract 4 (Liste Bouleau) permettent de le rattacher à la famille "
                "centriste/humaniste ? Explique."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite au moins deux indices du tract (« ni tout à l'État, "
                "ni tout au marché », « juste milieu », « dialogue entre tous », « attention "
                "portée à chaque personne et aux familles ») et explique que la famille "
                "centriste/humaniste se situe entre les tendances qui privilégient l'État et "
                "celles qui privilégient l'initiative privée, avec une attention à la personne."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "multiple_choice",
        {
            "prompt": (
                "Un commentateur place la Liste Saule « à gauche » et la Liste Chêne « à "
                "droite ». Comment faut-il considérer ce classement ?"
            ),
            "source_document_version_id": DOC,
            "options": [
                {"option_id": "a", "label": "Comme un repère simplifié, utile mais qui ne décrit pas tout"},
                {"option_id": "b", "label": "Comme une classification officielle et définitive"},
                {"option_id": "c", "label": "Comme un classement de la meilleure à la moins bonne liste"},
                {"option_id": "d", "label": "Comme une preuve que les deux listes ne peuvent jamais s'accorder"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "L'axe gauche-centre-droite aide à situer des idées (plus ou moins "
                "d'intervention publique), mais c'est un repère simplifié, jamais une vérité "
                "absolue ni un jugement de valeur."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Pourquoi est-il difficile de situer la Liste Érable (tract 3) sur le seul axe "
                "gauche-centre-droite ? Utilise ce que dit son tract."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que l'axe gauche-droite porte surtout sur le "
                "rôle de l'État et du marché, alors que le tract de la Liste Érable met en avant "
                "une autre priorité, l'environnement et la société durable (isolation, "
                "transports en commun, biodiversité) : l'axe seul ne suffit pas à le décrire, "
                "c'est un repère simplifié."
            ),
            "max_length": 400,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Compare les tracts de la Liste Saule (tract 1) et de la Liste Chêne (tract 2) : "
                "pour chacun, la valeur mise en avant, la priorité affichée et l'effet attendu, "
                "sans dire lequel te semble préférable."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : Saule — valeur de solidarité, priorité aux services publics "
                "accessibles financés par les plus hauts revenus (1 point) ; effet attendu : un "
                "accès aux soins et à l'école pour tous (1 point) ; Chêne — valeur d'initiative "
                "individuelle, priorité à l'allègement des charges et formalités, État limité "
                "(1 point) ; effet attendu : la création d'emplois ; comparaison neutre, sans "
                "aucune préférence exprimée (1 point)."
            ),
            "expected_points": [
                "Saule : solidarité, services publics",
                "Saule : effet attendu (accès pour tous)",
                "Chêne : initiative individuelle, moins de charges",
                "Chêne : effet attendu (emploi) ; comparaison neutre",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Trois réponses d'élèves à une consigne de comparaison
# =============================================================================================

ANSWERS_TITLE = "Trois réponses d'élèves à la consigne « Compare les tracts des listes Saule et Chêne »"
_ANSWERS_CONTEXT = (
    "Réponses écrites rendues lors d'un entraînement en classe, recopiées telles quelles. "
    "Élèves fictifs."
)
_ANSWERS = (
    ("Réponse d'Élise", "É", "p1",
     ("La Liste Saule veut renforcer les services publics grâce à une contribution plus forte "
      "des hauts revenus ; la Liste Chêne veut alléger les charges des entreprises. Franchement, "
      "la Liste Chêne a raison : trop d'impôts tue l'emploi.")),
    ("Réponse de Hamza", "H", "p2",
     ("La Liste Saule met en avant la solidarité ; sa priorité, ce sont des services publics "
      "accessibles, avec comme effet attendu l'accès de tous aux soins et à l'école. La Liste "
      "Chêne met en avant l'initiative individuelle ; sa priorité est d'alléger les charges et "
      "les formalités, avec comme effet attendu la création d'emplois.")),
    ("Réponse de Lina", "L", "p3", "Il y a la Liste Saule et la Liste Chêne. Ce sont deux listes différentes."),
)

ANSWERS_TEXT = f"[{_ANSWERS_CONTEXT}]\n\n" + "\n\n".join(
    f"{actor} : « {text} »" for actor, _initials, _tone, text in _ANSWERS
)

ANSWERS_LAYOUT = {
    "kind": "quotes",
    "notice": "Réponses fictives — exercice pédagogique",
    "context": _ANSWERS_CONTEXT,
    "items": [
        {"actor": actor, "initials": initials, "tone": tone, "text": text}
        for actor, initials, tone, text in _ANSWERS
    ],
}

_ANSWERS_QUESTIONS = (
    (
        "classification",
        {
            "prompt": "Comment qualifier chacune des trois réponses d'élèves ?",
            "source_document_version_id": DOC,
            "categories": ["Comparaison neutre et complète", "Opinion personnelle", "Comparaison incomplète"],
            "elements": ["Réponse d'Élise", "Réponse de Hamza", "Réponse de Lina"],
            "correct_categories": [1, 0, 2],
            "explanation": (
                "Élise termine par une prise de position (« la Liste Chêne a raison ») ; Hamza "
                "compare valeur, priorité et effet attendu sans juger ; Lina ne fait que nommer "
                "les deux listes."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "La réponse d'Élise commence bien. Quelle phrase faut-il retirer pour qu'elle "
                "respecte la consigne, et pourquoi ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle désigne la dernière phrase (« Franchement, la Liste Chêne "
                "a raison : trop d'impôts tue l'emploi ») et explique que comparer, dans ce "
                "cours, signifie décrire valeurs, priorités et effets attendus sans exprimer "
                "d'opinion personnelle."
            ),
            "max_length": 300,
        },
        M,
    ),
)

FSE11_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE11", key="fse11-tracts-listes-imaginaires", title=TRACTS_TITLE,
        content_text=TRACTS_TEXT, layout=TRACTS_LAYOUT, questions=_TRACTS_QUESTIONS,
    ),
    FseCase(
        course_code="FSE11", key="fse11-reponses-eleves-comparaison", title=ANSWERS_TITLE,
        content_text=ANSWERS_TEXT, layout=ANSWERS_LAYOUT, questions=_ANSWERS_QUESTIONS,
    ),
)
