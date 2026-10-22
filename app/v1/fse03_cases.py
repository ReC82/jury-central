"""FSE03 « Identités, traces numériques et appartenance » — cas nouveaux (ticket #129).

Le cours et sa banque historique analysent la présence en ligne de Sophie Lambert (forum de
jeux, photo d'anniversaire, note du recruteur). Les cas ci-dessous gardent les mêmes
notions (identité personnelle/collective, identité numérique, traces volontaires et
involontaires — publiées par autrui ou déduites —, réputation, identité réelle et image
donnée à voir) sur une autre personne, d'autres traces et d'autres questions :

1. les cinq résultats qu'un patron trouve en cherchant le nom d'un candidat apprenti
   électricien (profil professionnel, vidéo publiée par son club, palmarès scolaire, avis
   laissé sur un restaurant, information déduite par un réseau social) ;
2. deux mini-situations à choix multiple (vidéo de mariage publiée par un invité, profil
   qui ne montre que des voyages).

Personnes, club, école et entreprise fictifs."""

from app.v1.fse03_content import FSE03_HR_NOTE_TITLE, FSE03_PROFILE_TITLE, FSE03_RECENT_POST_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE03_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE03_PROFILE_TITLE, FSE03_HR_NOTE_TITLE, FSE03_RECENT_POST_TITLE}),
    markers=("Sophie Lambert", "Sophie"),
)

SEARCH_TITLE = "Recherche en ligne sur « Jonas Delcourt » avant un entretien"
_SEARCH_CONTEXT = (
    "Avant d'inviter Jonas Delcourt, 19 ans, à un entretien pour un poste d'apprenti "
    "électricien, le patron d'une petite entreprise tape son nom dans un moteur de recherche."
)
_SEARCH_HEADING = "Les cinq premiers résultats trouvés"
_SEARCH_ITEMS = (
    ("bi-person-badge",
     ("Profil sur un réseau professionnel, rempli par Jonas lui-même : « Apprenti électricien "
     "en formation en alternance. Passionné de domotique. »")),
    ("bi-camera-video",
     ("Vidéo publiée par le club de futsal de Ciney sur sa page : on y voit Jonas, capitaine "
     "de l'équipe, crier contre l'arbitre et jeter son brassard au sol après un match. "
     "Légende du club : « Match tendu hier soir… On se reprend samedi ! »")),
    ("bi-trophy",
     ("Palmarès d'un concours de robotique publié sur le site de son ancienne école : "
     "« 2e prix : Jonas Delcourt et Inès Marchal ». ")),
    ("bi-star-half",
     ("Avis écrit par Jonas il y a trois ans, sous son nom, sur la page d'une pizzeria : "
     "« Livreur en retard, pizza froide, plus jamais ! » (1 étoile sur 5).")),
    ("bi-geo-alt",
     ("Encadré « Vous connaissez peut-être… » d'un réseau social : « Jonas Delcourt — habite "
     "probablement à Ciney ». Le réseau a déduit cette information des contacts de Jonas ; "
     "Jonas ne l'a jamais publiée.")),
)

SEARCH_TEXT = f"[{_SEARCH_CONTEXT}]\n\n{_SEARCH_HEADING} :\n" + "\n".join(
    f"{index}. {text.strip()}" for index, (_icon, text) in enumerate(_SEARCH_ITEMS, start=1)
)

SEARCH_LAYOUT = {
    "kind": "findings",
    "notice": "Personne et résultats fictifs — exercice pédagogique",
    "context": _SEARCH_CONTEXT,
    "heading": _SEARCH_HEADING,
    "items": [{"icon": icon, "text": text.strip()} for icon, text in _SEARCH_ITEMS],
}

_SEARCH_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "Classe chacun des cinq résultats trouvés sur Jonas Delcourt : trace "
                "volontaire (publiée par Jonas lui-même) ou trace involontaire (publiée par "
                "quelqu'un d'autre, ou déduite) ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Trace volontaire", "Trace involontaire"],
            "elements": [
                "Résultat 1 — le profil professionnel",
                "Résultat 2 — la vidéo du club de futsal",
                "Résultat 3 — le palmarès du concours de robotique",
                "Résultat 4 — l'avis sur la pizzeria",
                "Résultat 5 — « habite probablement à Ciney »",
            ],
            "correct_categories": [0, 1, 1, 0, 1],
            "explanation": (
                "Jonas a lui-même rempli son profil et écrit l'avis (traces volontaires, même "
                "ancienne pour l'avis). La vidéo et le palmarès ont été publiés par le club et "
                "par l'école ; l'adresse probable a été déduite par le réseau social : ce sont "
                "des traces involontaires."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "D'après le résultat 2, Jonas est capitaine d'une équipe de futsal. Cette "
                "information relève-t-elle de son identité personnelle ou de son identité "
                "collective ? Explique."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle parle d'identité collective : appartenir à un club, à "
                "une équipe, c'est faire partie d'un groupe (groupe d'appartenance), au-delà "
                "de ce que Jonas est seul."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Le résultat 5 n'a jamais été publié par Jonas. Pourquoi est-ce quand même une "
                "trace numérique le concernant, et de quel type ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que l'information concerne Jonas et reste "
                "visible en ligne, et qu'il s'agit d'une trace involontaire, déduite par le "
                "réseau social à partir de ses contacts, que Jonas ne maîtrise pas."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quel résultat risque le plus de nuire à la réputation de Jonas auprès du "
                "patron, et quelle conséquence concrète cela peut-il avoir sur sa "
                "candidature ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle désigne la vidéo du club (résultat 2) — Jonas y paraît "
                "colérique — et explique une conséquence concrète : le patron peut douter de "
                "son calme ou de son comportement avec les clients, hésiter à l'inviter, ou "
                "lui poser la question en entretien. L'avis sur la pizzeria peut être cité en "
                "complément, pas à la place."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "La vidéo du club (résultat 2) montre-t-elle qui est vraiment Jonas ? Réponds "
                "en utilisant la distinction entre identité réelle et image donnée à voir, et "
                "appuie-toi sur un autre résultat."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que la vidéo ne montre qu'un moment, publié "
                "par d'autres : c'est une image donnée à voir, qui ne résume pas l'identité "
                "réelle de Jonas ; d'autres traces (profil d'apprenti passionné, 2e prix du "
                "concours de robotique) montrent d'autres aspects de lui."
            ),
            "max_length": 500,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Analyse l'identité numérique de Jonas Delcourt : distingue ses traces "
                "volontaires et involontaires, explique quelle réputation l'ensemble de ces "
                "traces peut lui construire auprès du patron, puis explique pourquoi le "
                "patron devrait nuancer cette impression."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : traces volontaires (profil, avis) et involontaires (vidéo du club, "
                "palmarès, adresse déduite) correctement distinguées (1 point) ; réputation "
                "mêlant éléments positifs (formation, passion, concours) et négatifs (colère "
                "filmée, avis agressif) (1 point) ; conséquence possible sur la candidature "
                "(1 point) ; nuance : image partielle, publiée par d'autres ou ancienne, "
                "différente de l'identité réelle (1 point)."
            ),
            "expected_points": [
                "Distingue les traces volontaires et involontaires",
                "Décrit une réputation mêlant éléments positifs et négatifs",
                "Explique une conséquence concrète possible sur la candidature",
                "Nuance : image partielle, différente de l'identité réelle",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

_WEDDING = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Lors d'un mariage, un invité publie une vidéo où l'on voit Yanis danser. "
                "Yanis n'a rien publié lui-même. Pour Yanis, cette vidéo est une trace "
                "numérique…"
            ),
            "options": [
                {"option_id": "a", "label": "volontaire"},
                {"option_id": "b", "label": "involontaire"},
                {"option_id": "c", "label": "sans importance, car elle n'a pas été publiée par lui"},
                {"option_id": "d", "label": "qui fait partie de son identité réelle uniquement"},
            ],
            "correct_option_ids": ["b"],
            "explanation": (
                "Une trace publiée par quelqu'un d'autre au sujet d'une personne est une trace "
                "involontaire pour elle : elle la concerne et peut contribuer à sa réputation, "
                "même si elle ne l'a pas publiée."
            ),
        },
        E,
    ),
)

_TRAVEL_PROFILE = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Sur son profil, Clara ne publie que des photos de voyages et de restaurants "
                "chics, alors qu'elle passe la plupart de ses soirées à étudier. Que montre "
                "cet exemple ?"
            ),
            "options": [
                {"option_id": "a", "label": "Une trace numérique involontaire"},
                {"option_id": "b", "label": "Une identité collective"},
                {"option_id": "c", "label": "La différence entre l'identité réelle et l'image donnée à voir"},
                {"option_id": "d", "label": "Une réputation construite uniquement par les autres"},
            ],
            "correct_option_ids": ["c"],
            "explanation": (
                "Clara choisit ce qu'elle montre : ses publications (volontaires) construisent "
                "une image qui ne correspond qu'à une petite partie de sa vie réelle."
            ),
        },
        M,
    ),
)

FSE03_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE03", key="fse03-recherche-candidat-apprenti", title=SEARCH_TITLE,
        content_text=SEARCH_TEXT, layout=SEARCH_LAYOUT, questions=_SEARCH_QUESTIONS,
    ),
    FseCase(course_code="FSE03", key="fse03-video-mariage", questions=_WEDDING),
    FseCase(course_code="FSE03", key="fse03-profil-voyages", questions=_TRAVEL_PROFILE),
)
