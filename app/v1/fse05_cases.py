"""FSE05 « Image, vie privée et données personnelles » — cas nouveaux (ticket #129).

Le cours et sa banque historique analysent six situations (monument touristique,
anniversaire de Nabil, manifestation, photo de soirée publiée par Chloé, enfant en vacances,
formulaire de concours). Les cas ci-dessous gardent les mêmes notions (prise de vue et
diffusion, sujet principal et personne accessoire, pas de règle absolue « lieu public »,
exception personnelle ou domestique, consentement lié à une finalité, données personnelles,
protection des mineurs) dans d'autres situations et d'autres supports :

1. la conversation du groupe des parents d'une équipe de football de jeunes après un
   tournoi (photos et vidéo à publier, autorisation signée pour un autre usage, enfant qui
   refuse) ;
2. la fiche d'inscription en ligne d'une salle d'escalade (données demandées, but annoncé,
   case pré-cochée pour des partenaires) ;
3. deux mini-situations à choix multiple (vidéo de vacances envoyée aux grands-parents,
   photo d'une passante pour une publicité).

Personnes, club et entreprise fictifs."""

from app.v1.fse05_content import FSE05_SITUATIONS_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE05_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE05_SITUATIONS_TITLE}),
    markers=("Nabil", "Chloé", "monument", "concours"),
)

# =============================================================================================
# Cas 1 — Les photos du tournoi de football
# =============================================================================================

TOURNAMENT_TITLE = "Groupe des parents des Aiglons U11 — les photos du tournoi"
_TOURNAMENT_CONTEXT = (
    "Groupe de messagerie des parents des joueurs de l'équipe U11 (enfants de 9 et 10 ans) du "
    "club de football fictif « Les Aiglons ». Vanessa est l'entraîneuse de l'équipe."
)
_TOURNAMENT_GROUP = "Parents — Aiglons U11"
_TOURNAMENT_DAY = "Samedi 8 mars"
_TOURNAMENT_MESSAGES = (
    ("Vanessa, entraîneuse", "p1", "18 h 05",
     ("Super tournoi aujourd'hui ! J'ai pris une cinquantaine de photos des enfants pendant "
     "les matchs. Je mets les meilleures demain sur la page publique du club, comme "
     "d'habitude.")),
    ("Olivier, papa de Noé", "p2", "18 h 12",
     ("Pour Noé, je préfère que ses photos ne soient pas publiées. Tu peux les garder pour "
     "toi, pas de souci.")),
    ("Vanessa, entraîneuse", "p1", "18 h 15",
     ("Pourtant, à l'inscription, vous avez tous signé l'autorisation de photos pour le "
     "trombinoscope affiché dans le vestiaire.")),
    ("Myriam, maman d'Elsa", "p3", "18 h 20",
     ("Sur la photo du but, on voit Elsa en gros plan. Elle m'a dit qu'elle ne veut pas qu'on "
     "la voie en ligne : elle n'aime pas sa grimace.")),
    ("Patrick, papa de Tom", "p4", "18 h 31",
     ("Moi, j'ai filmé la tribune pendant la finale : on voit des dizaines de supporters, de "
     "loin. Je l'envoie au journal du quartier ?")),
    ("Vanessa, entraîneuse", "p1", "18 h 40",
     ("Le terrain est public, donc tout le monde accepte d'être photographié et publié, "
     "non ?")),
)

TOURNAMENT_TEXT = (
    f"[{_TOURNAMENT_CONTEXT}]\n\nGroupe : « {_TOURNAMENT_GROUP} »\n{_TOURNAMENT_DAY}\n"
    + "\n".join(f"{time} — {author} : « {text} »" for author, _tone, time, text in _TOURNAMENT_MESSAGES)
)

TOURNAMENT_LAYOUT = {
    "kind": "chat",
    "notice": "Échange fictif — exercice pédagogique",
    "context": _TOURNAMENT_CONTEXT,
    "group": _TOURNAMENT_GROUP,
    "messages": [
        {"author": author, "tone": tone, "day": _TOURNAMENT_DAY, "time": time, "text": text}
        for author, tone, time, text in _TOURNAMENT_MESSAGES
    ],
}

_TOURNAMENT_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "Classe chaque action citée dans le groupe des parents des Aiglons : s'agit-il "
                "d'une prise de vue ou d'une diffusion ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Prise de vue", "Diffusion"],
            "elements": [
                "Vanessa prend une cinquantaine de photos pendant les matchs",
                "Mettre les meilleures photos sur la page publique du club",
                "Patrick filme la tribune pendant la finale",
                "Envoyer la vidéo au journal du quartier",
            ],
            "correct_categories": [0, 1, 0, 1],
            "explanation": (
                "Photographier et filmer sont des prises de vue ; publier sur la page du club "
                "ou transmettre la vidéo à un journal sont des diffusions, qui demandent leur "
                "propre réflexion sur le consentement."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Dans son message de 18 h 12, Olivier refuse-t-il que Vanessa photographie "
                "Noé, ou que ses photos soient publiées ? Explique la différence."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle indique qu'Olivier accepte la prise de vue (« tu peux "
                "les garder pour toi ») mais refuse la diffusion (la publication sur la page "
                "publique du club), et que ce sont deux étapes distinctes."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "À 18 h 15, Vanessa répond que les parents ont signé une autorisation à "
                "l'inscription. Pourquoi cette autorisation ne suffit-elle pas pour publier "
                "les photos sur la page publique du club ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que le consentement est donné pour une "
                "finalité précise — le trombinoscope affiché dans le vestiaire — et qu'un "
                "accord pour cet usage n'autorise pas automatiquement un autre usage (une "
                "publication en ligne, visible par tous)."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Sur la vidéo de Patrick, les supporters sont-ils sujets principaux ou "
                "personnes accessoires ? Et Elsa sur la photo du but ? Quelle conséquence "
                "cela a-t-il sur l'accord à demander ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle classe les supporters comme personnes accessoires "
                "(filmés de loin, dans la foule, aucun n'est mis en avant) et Elsa comme sujet "
                "principal (en gros plan, reconnaissable), et en déduit que la diffusion de la "
                "photo d'Elsa demande un accord, ce qui est moins le cas pour des supporters "
                "non individualisés."
            ),
            "max_length": 500,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Le dernier message de Vanessa (18 h 40) est-il correct ? Explique en "
                "t'appuyant sur deux éléments de la conversation."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle répond non : aucune règle absolue ne dit qu'un lieu "
                "public autorise toute diffusion. Deux éléments parmi : les enfants sont "
                "photographiés comme sujets principaux (Elsa en gros plan) ; ce sont des "
                "mineurs, pour qui l'accord des parents est nécessaire (Olivier refuse) ; Elsa "
                "elle-même refuse ; l'autorisation signée visait un autre usage."
            ),
            "max_length": 500,
        },
        H,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Vanessa te demande conseil avant de publier la photo du but où l'on voit "
                "Elsa. Analyse la situation : qui doit donner son accord, pour quel usage, "
                "quelle place donner à l'avis d'Elsa, et quelle solution proposer ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : Elsa est mineure, l'accord de ses parents est nécessaire pour cette "
                "diffusion (1 point) ; l'accord doit viser cette finalité précise — la page "
                "publique —, l'autorisation du trombinoscope ne suffit pas (1 point) ; l'avis "
                "d'Elsa (10 ans) compte : elle refuse, et un enfant est associé de plus en "
                "plus à la décision avec l'âge (1 point) ; solution cohérente : ne pas publier "
                "cette photo, choisir une photo où elle n'est pas reconnaissable, ou la garder "
                "dans un cercle familial restreint (1 point)."
            ),
            "expected_points": [
                "Accord des parents nécessaire pour un enfant mineur",
                "Accord lié à une finalité précise : l'autorisation du trombinoscope ne suffit pas",
                "L'avis d'Elsa compte et elle refuse",
                "Propose une solution respectueuse (ne pas publier, photo non reconnaissable…)",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — La fiche d'inscription de la salle d'escalade
# =============================================================================================

FORM_TITLE = "Fiche d'inscription en ligne — salle d'escalade « Le Bloc »"
_FORM_CONTEXT = (
    "Yanis, 16 ans, veut s'abonner à une salle d'escalade de sa ville. Avant de payer, il doit "
    "remplir cette fiche sur le site de la salle."
)
_FORM_ORG = "Le Bloc — salle d'escalade"
_FORM_TYPE = "Fiche d'inscription"
_FORM_META = (
    ("Tarif", "35 € par mois, sans engagement"),
    ("But annoncé",
     ("« Ces informations servent uniquement à gérer ton abonnement et à te prévenir en cas de "
     "fermeture de la salle. »")),
)
_FORM_FIELDS = (
    ("Nom et prénom", "obligatoire"),
    ("Adresse e-mail", "obligatoire"),
    ("Date de naissance", "obligatoire"),
    ("Numéro de carte d'identité", "obligatoire"),
    ("Profession de tes parents", "obligatoire"),
    ("Photo de ton visage", "obligatoire, pour ta carte de membre"),
)
_FORM_CHECKBOX = (
    "☑ (case déjà cochée) J'accepte que mes coordonnées soient transmises aux partenaires de "
    "la salle (magasins de sport) pour recevoir leurs offres."
)
_FORM_CLOSING = "En cliquant sur « Valider », tu acceptes toutes ces conditions."

FORM_TEXT = (
    f"[{_FORM_CONTEXT}]\n\n{_FORM_ORG}\n{_FORM_TYPE}\n"
    + "\n".join(f"{field} : {value}" for field, value in _FORM_META)
    + "\n\nChamps à remplir :\n"
    + "\n".join(f"{index}. {field} : {value}" for index, (field, value) in enumerate(_FORM_FIELDS, start=1))
    + f"\n\n{_FORM_CHECKBOX}\n\n{_FORM_CLOSING}"
)

FORM_LAYOUT = {
    "kind": "memo",
    "notice": "Formulaire fictif — exercice pédagogique",
    "context": _FORM_CONTEXT,
    "org": _FORM_ORG,
    "doc_type": _FORM_TYPE,
    "paragraphs": [f"{field} : {value}" for field, value in _FORM_META] + ["Champs à remplir :"],
    "points": [{"title": field, "text": value} for field, value in _FORM_FIELDS],
    "closing": f"{_FORM_CHECKBOX} {_FORM_CLOSING}",
}

_FORM_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "Parmi ces éléments de la fiche d'inscription du Bloc, lesquels sont des "
                "données personnelles de Yanis ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Donnée personnelle", "Pas une donnée personnelle"],
            "elements": [
                "L'adresse e-mail",
                "La photo du visage",
                "Le tarif de 35 € par mois",
                "Le numéro de carte d'identité",
            ],
            "correct_categories": [0, 0, 1, 0],
            "explanation": (
                "Une donnée personnelle est toute information qui permet d'identifier une "
                "personne : adresse e-mail, photo du visage et numéro de carte d'identité en "
                "sont ; le tarif de la salle ne dit rien de Yanis."
            ),
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "Compare chaque donnée demandée au but annoncé par la salle. Est-elle utile à "
                "ce but, ou le dépasse-t-elle ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Utile au but annoncé", "Dépasse le but annoncé"],
            "elements": [
                "Nom et prénom",
                "Adresse e-mail",
                "Profession des parents",
                "Transmission des coordonnées aux magasins de sport",
            ],
            "correct_categories": [0, 0, 1, 1],
            "explanation": (
                "Le but annoncé est de gérer l'abonnement et de prévenir en cas de fermeture : "
                "le nom et l'adresse e-mail y servent. La profession des parents n'y sert à "
                "rien, et la transmission aux partenaires poursuit un autre but (la publicité)."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Pourquoi la case déjà cochée, en bas de la fiche, pose-t-elle problème ? "
                "Utilise la notion de finalité."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que la transmission aux partenaires sert une "
                "autre finalité que celle annoncée (recevoir des offres publicitaires, et non "
                "gérer l'abonnement) et que l'accord n'est pas réellement donné : la case est "
                "cochée d'avance, Yanis ne choisit pas. Un accord pour un usage n'autorise pas "
                "un autre usage."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Yanis te demande s'il peut envoyer la fiche telle quelle. Analyse-la : quelles "
                "données sont justifiées, lesquelles dépassent la finalité annoncée, et que "
                "devrait changer la salle pour respecter ses données ? Tiens compte de son âge."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : données justifiées par le but annoncé (nom, adresse e-mail, "
                "éventuellement date de naissance ou photo pour la carte) (1 point) ; données "
                "qui dépassent la finalité (profession des parents, numéro de carte "
                "d'identité sans raison donnée) (1 point) ; la case pré-cochée vise un autre "
                "but et doit être décochée par défaut, au choix de Yanis (1 point) ; Yanis a 16 "
                "ans : protection renforcée des mineurs, en parler à ses parents (1 point)."
            ),
            "expected_points": [
                "Identifie les données utiles au but annoncé",
                "Identifie les données qui dépassent la finalité",
                "Critique la case pré-cochée (autre finalité, pas de vrai choix)",
                "Tient compte de la protection des mineurs",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 et 4 — Mini-situations à choix multiple
# =============================================================================================

_HOLIDAY_VIDEO = (
    (
        "multiple_choice",
        {
            "prompt": (
                "En vacances, Inès filme ses deux cousins sur la plage et envoie la vidéo "
                "uniquement à ses grands-parents, par message privé. Quelle notion s'applique "
                "à cette diffusion ?"
            ),
            "options": [
                {"option_id": "a", "label": "Une diffusion publique, qui exige un accord écrit"},
                {"option_id": "b", "label": "L'activité strictement personnelle ou domestique : un cercle très restreint"},
                {"option_id": "c", "label": "La règle selon laquelle une plage, lieu public, autorise toute diffusion"},
                {"option_id": "d", "label": "Un traitement de données personnelles sans finalité"},
            ],
            "correct_option_ids": ["b"],
            "explanation": (
                "Partager une vidéo dans un cercle familial très restreint relève de l'activité "
                "personnelle ou domestique. Cette exception ne vaudrait plus si Inès publiait "
                "la vidéo sur un compte public."
            ),
        },
        E,
    ),
)

_SHOP_AD = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Un magasin de vélos photographie une passante, bien reconnaissable au centre "
                "de l'image, sur le trottoir devant sa vitrine. Il veut utiliser cette photo "
                "sur une affiche publicitaire. Que faut-il en conclure ?"
            ),
            "options": [
                {"option_id": "a", "label": "Sur la voie publique, le magasin peut utiliser la photo librement"},
                {"option_id": "b", "label": "La passante est une personne accessoire : aucun accord n'est nécessaire"},
                {"option_id": "c", "label": "Il suffit de flouter le nom du magasin sur la vitrine"},
                {"option_id": "d", "label": "Elle est le sujet principal : il faut son accord pour cet usage publicitaire"},
            ],
            "correct_option_ids": ["d"],
            "explanation": (
                "La passante est mise en avant et reconnaissable : c'est le sujet principal. "
                "Être dans un lieu public n'autorise pas toute diffusion, surtout pour une "
                "publicité : son accord, pour cet usage précis, est nécessaire."
            ),
        },
        M,
    ),
)

FSE05_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE05", key="fse05-photos-tournoi-u11", title=TOURNAMENT_TITLE,
        content_text=TOURNAMENT_TEXT, layout=TOURNAMENT_LAYOUT, questions=_TOURNAMENT_QUESTIONS,
    ),
    FseCase(
        course_code="FSE05", key="fse05-inscription-salle-escalade", title=FORM_TITLE,
        content_text=FORM_TEXT, layout=FORM_LAYOUT, questions=_FORM_QUESTIONS,
    ),
    FseCase(course_code="FSE05", key="fse05-video-vacances-famille", questions=_HOLIDAY_VIDEO),
    FseCase(course_code="FSE05", key="fse05-passante-publicite", questions=_SHOP_AD),
)
