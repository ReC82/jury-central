"""FSE07 « Analyser un dossier médiatique » — cas nouveaux (ticket #129).

Le cours et sa banque historique analysent le dossier de l'« Athénée du Parc » (note de la
direction, messages du groupe de la classe de 5e B, publication anonyme d'un forum). Le cas
ci-dessous applique la même méthode (fait, interprétation et opinion ; fiabilité : auteur,
date, contexte, preuves ; enjeux juridique et sociologique ; conclusion argumentée) à un
autre dossier complet, sur un autre sujet : la vidéo d'un chauffeur de bus filmé pendant
une dispute avec un passager.

Les trois documents du dossier sont réunis dans UN seul document (trois fiches numérotées)
pour que chaque question qui les compare s'appuie sur exactement le même support que la
correction (voir #151 : aucune référence à un « document 3 » introuvable). Personnes,
société de transport et commune fictives."""

from app.v1.fse07_content import FSE07_CHAT_TITLE, FSE07_FORUM_TITLE, FSE07_SCHOOL_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE07_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE07_SCHOOL_TITLE, FSE07_CHAT_TITLE, FSE07_FORUM_TITLE}),
    markers=("Athénée du Parc", "5e B", "parent_inquiet93", "Yasmine", "Thibault", "groupe-classe"),
)

# =============================================================================================
# Cas 1 — Dossier : la vidéo du chauffeur de la ligne 12
# =============================================================================================

BUS_TITLE = "Dossier en trois documents — la vidéo du chauffeur de la ligne 12"
_BUS_CONTEXT = (
    "Dossier réuni pour l'exercice : trois documents sur une même vidéo, qui a circulé dans la "
    "commune de Villers-la-Source en mai 2026."
)
_BUS_DOCUMENTS = (
    ("bi-building",
     "Communiqué de TransVal, société de bus de Villers-la-Source — signé par Nathalie Petit, porte-parole — 9 mai 2026",
     ("Le 7 mai 2026 vers 17 h 30, un chauffeur de la ligne 12 a refusé l'entrée à un passager "
     "qui ne présentait pas de titre de transport. Une vidéo de la discussion, filmée par un "
     "autre passager, a été publiée le soir même sur un réseau social ; le visage du chauffeur "
     "y est reconnaissable. Les images de la caméra du bus ont été remises à la direction. Le "
     "chauffeur a été entendu le 8 mai. Il reste en service.")),
    ("bi-phone",
     "Publication de « Gaëtan R. » sur un réseau social — 7 mai 2026, 21 h 10 — vidéo de 42 secondes, 18 000 vues, 2 300 partages",
     ("« Regardez comment ce chauffeur traite les jeunes ! Il a laissé un ado sur le trottoir, "
     "sous la pluie. S'il l'a refusé, c'est sûrement parce qu'il n'aime pas les jeunes. Ces "
     "chauffeurs se croient tout permis. Partagez un max pour qu'il soit viré ! »")),
    ("bi-forward",
     "Message transféré dans un groupe de messagerie — auteur inconnu, non daté",
     ("« Info d'un cousin qui bosse chez TransVal : le chauffeur a déjà été averti dix fois et "
     "il sera licencié lundi. Faites tourner. »")),
)

BUS_TEXT = f"[{_BUS_CONTEXT}]\n\n" + "\n\n".join(
    f"Document {index} — {title}\n{text}" for index, (_icon, title, text) in enumerate(_BUS_DOCUMENTS, start=1)
)

BUS_LAYOUT = {
    "kind": "cards",
    "notice": "Dossier fictif — exercice pédagogique",
    "context": _BUS_CONTEXT,
    "item_label": "Document",
    "items": [
        {"number": index, "label": f"Document {index}", "icon": icon, "title": title, "text": text}
        for index, (icon, title, text) in enumerate(_BUS_DOCUMENTS, start=1)
    ],
}

_BUS_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "Classe chacune de ces phrases du dossier sur le chauffeur de la ligne 12 : "
                "fait, interprétation ou opinion ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Fait", "Interprétation", "Opinion"],
            "elements": [
                "« Le chauffeur a été entendu le 8 mai. » (document 1)",
                "« S'il l'a refusé, c'est sûrement parce qu'il n'aime pas les jeunes. » (document 2)",
                "« Ces chauffeurs se croient tout permis. » (document 2)",
                "« Un chauffeur de la ligne 12 a refusé l'entrée à un passager qui ne présentait pas de titre de transport. » (document 1)",
            ],
            "correct_categories": [0, 1, 2, 0],
            "explanation": (
                "Un fait est vérifiable (l'audition du 8 mai, le refus d'entrée). « Sûrement "
                "parce qu'il n'aime pas les jeunes » propose une explication discutable du "
                "refus : interprétation. « Se croient tout permis » est un jugement personnel : "
                "opinion."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Dans le dossier sur la ligne 12, qui est l'auteur du document 1, et à quelle "
                "date a-t-il été publié ? Pourquoi ces deux informations comptent-elles ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite Nathalie Petit, porte-parole de TransVal (ou la "
                "société TransVal), et le 9 mai 2026, et explique qu'un auteur identifié et une "
                "date permettent de vérifier d'où vient l'information et de la situer, ce qui "
                "rend le document plus fiable."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Le document 3 annonce que le chauffeur « sera licencié lundi ». Peut-on "
                "utiliser cette information dans une analyse ? Cite deux indices de fiabilité "
                "qui manquent ou qui posent problème."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle répond non (ou seulement avec prudence) et cite deux "
                "indices : auteur inconnu ; message non daté ; information de seconde main "
                "(« un cousin ») ; aucune preuve ; le document 1, signé et daté, dit au "
                "contraire que le chauffeur reste en service."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quel enjeu juridique la publication du document 2 soulève-t-elle pour le "
                "chauffeur ? Appuie-toi sur des éléments précis du dossier."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle relève le droit à l'image : le chauffeur est filmé et "
                "reconnaissable (document 1), il est le sujet principal de la vidéo, diffusée "
                "à des milliers de personnes (18 000 vues, 2 300 partages) sans son accord ; "
                "l'appel « Partagez un max pour qu'il soit viré » montre en plus une volonté de "
                "nuire (diffusion malveillante)."
            ),
            "max_length": 500,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quel enjeu sociologique ce dossier soulève-t-il ? Utilise au moins une notion "
                "vue en FSE04 (norme, valeur, influence sociale…)."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle relève par exemple : la norme de présenter un titre de "
                "transport (appliquée par le chauffeur) ; l'influence sociale ou la pression du "
                "groupe en ligne, qui pousse à partager et à condamner sans vérifier (« Partagez "
                "un max », 2 300 partages, « Faites tourner ») ; des valeurs en tension "
                "(solidarité avec le jeune contre respect de la règle). Au moins une notion "
                "correctement reliée au dossier."
            ),
            "max_length": 500,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Rédige une conclusion argumentée sur ce dossier : que peut-on affirmer avec "
                "certitude, quelles affirmations faut-il écarter ou nuancer, et quels enjeux "
                "juridique et sociologique ressortent ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : faits établis par le document 1 (refus d'entrée sans titre, vidéo "
                "publiée, chauffeur reconnaissable, entendu, toujours en service) (1 point) ; "
                "le document 2 mêle faits, interprétation et opinion, et le document 3 n'est pas "
                "fiable (anonyme, non daté, sans preuve, contredit) (1 point) ; enjeu juridique "
                "(droit à l'image, diffusion pour nuire) et enjeu sociologique (norme, pression "
                "du groupe) (1 point) ; conclusion nuancée, appuyée explicitement sur ces faits "
                "et enjeux (1 point)."
            ),
            "expected_points": [
                "S'appuie sur les faits établis par le document 1",
                "Distingue faits, interprétations et opinions et écarte le document 3",
                "Identifie un enjeu juridique et un enjeu sociologique",
                "Conclusion nuancée, appuyée sur les faits et les enjeux",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 et 3 — Mini-situations à choix multiple
# =============================================================================================

_SCREENSHOT = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Une capture d'écran d'un prétendu message de la commune circule : aucun nom, "
                "aucune date, et le logo semble découpé. Avant de l'utiliser dans un dossier, "
                "que faut-il faire d'abord ?"
            ),
            "options": [
                {"option_id": "a", "label": "La partager pour demander l'avis de ses contacts"},
                {"option_id": "b", "label": "Vérifier l'auteur, la date, le contexte et les preuves, par exemple sur le site de la commune"},
                {"option_id": "c", "label": "La considérer comme fiable parce qu'elle a été beaucoup partagée"},
                {"option_id": "d", "label": "En tirer directement une conclusion"},
            ],
            "correct_option_ids": ["b"],
            "explanation": (
                "Un document sans auteur ni date ne peut pas être utilisé tel quel : il faut le "
                "vérifier (auteur, date, contexte, preuves), par exemple en cherchant la "
                "source d'origine. Le nombre de partages ne prouve rien."
            ),
        },
        E,
    ),
)

_LIBRARY = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Dans un article : « La bibliothèque de quartier ferme à 17 h depuis janvier ; "
                "la commune veut sans doute la fermer définitivement. » La seconde partie de "
                "la phrase est…"
            ),
            "options": [
                {"option_id": "a", "label": "un fait, car elle parle de la commune"},
                {"option_id": "b", "label": "une opinion, car elle juge la bibliothèque"},
                {"option_id": "c", "label": "une preuve, car elle suit un fait vérifiable"},
                {"option_id": "d", "label": "une interprétation, car elle propose une explication discutable d'un fait"},
            ],
            "correct_option_ids": ["d"],
            "explanation": (
                "L'horaire est un fait vérifiable. « Veut sans doute la fermer » explique ce fait "
                "par une intention supposée, sans preuve : c'est une interprétation, pas un "
                "jugement de valeur."
            ),
        },
        M,
    ),
)

FSE07_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE07", key="fse07-dossier-chauffeur-ligne-12", title=BUS_TITLE,
        content_text=BUS_TEXT, layout=BUS_LAYOUT, questions=_BUS_QUESTIONS,
    ),
    FseCase(course_code="FSE07", key="fse07-capture-sans-source", questions=_SCREENSHOT),
    FseCase(course_code="FSE07", key="fse07-bibliotheque-interpretation", questions=_LIBRARY),
)
