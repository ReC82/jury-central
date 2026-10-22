"""FSE02 « Les médias et leurs financements » — cas nouveaux (ticket #129).

Le cours et sa banque historique analysent L'Hebdo du Littoral (abonnement/vente), Le Flash
Infos (publicité) et la radio publique RCW (fonds publics). Les cas ci-dessous gardent les
mêmes notions (quatre modes de financement, audience, interactivité, comportements des
publics) sur d'autres médias et d'autres questions :

1. la page « Qui finance votre radio ? » d'une radio locale à financement MIXTE (publicité
   et subvention), avec un prix de spot qui dépend de l'audience et une émission où les
   auditeurs appellent le studio ;
2. la couverture d'un magazine mensuel sans publicité, vendu au numéro et par abonnement ;
3. la publication d'un site d'information gratuit qui devient payant, et les réactions de
   ses lecteurs ;
4. deux mini-situations à choix multiple (publicité avant une vidéo en ligne, programmes
   pour enfants sans publicité d'une télévision publique).

Médias, personnes et chiffres fictifs."""

from app.v1.fse02_content import FSE02_FREE_AD_TITLE, FSE02_PAID_TITLE, FSE02_PUBLIC_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE02_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE02_PAID_TITLE, FSE02_FREE_AD_TITLE, FSE02_PUBLIC_TITLE}),
    markers=("Hebdo du Littoral", "Flash Infos", "RCW"),
)

# =============================================================================================
# Cas 1 — Radio locale à financement mixte
# =============================================================================================

RADIO_TITLE = "Vallée FM — page « Qui finance votre radio ? »"
_RADIO_SITE = "VALLÉE FM"
_RADIO_TAGLINE = "La radio locale de la vallée de l'Ourthe"
_RADIO_LEAD = (
    "Vallée FM s'écoute gratuitement, en FM et sur internet. Voici d'où viennent nos recettes."
)
_RADIO_OFFERS_TITLE = "Nos recettes de l'année :"
_RADIO_OFFERS = (
    ("Spots publicitaires de commerces et d'entreprises de la région", "65 %"),
    ("Subvention de la Fédération Wallonie-Bruxelles", "35 %"),
)
_RADIO_PRICE = (
    "Le prix d'un spot publicitaire dépend du nombre d'auditeurs à l'heure de diffusion : un "
    "spot coûte trois fois plus cher à 7 h 30 qu'à 22 h."
)
_RADIO_SHOW = (
    "Chaque matin, « Le Direct des auditeurs » : appelez le studio pour réagir en direct à "
    "l'actualité de la vallée."
)

RADIO_TEXT = (
    f"[Page « Qui finance votre radio ? » du site de {_RADIO_SITE} — radio locale fictive]\n\n"
    f"{_RADIO_SITE} — {_RADIO_TAGLINE}\n\n{_RADIO_LEAD}\n\n{_RADIO_OFFERS_TITLE}\n"
    + "\n".join(f"- {label} : {value}" for label, value in _RADIO_OFFERS)
    + f"\n\n{_RADIO_PRICE}\n\n{_RADIO_SHOW}"
)

RADIO_LAYOUT = {
    "kind": "webpage",
    "variant": "public",
    "notice": "Radio fictive — exercice pédagogique",
    "url": "Qui finance votre radio ?",
    "site": _RADIO_SITE,
    "tagline": _RADIO_TAGLINE,
    "blocks": [
        {"type": "lead", "text": _RADIO_LEAD},
        {
            "type": "offers",
            "title": _RADIO_OFFERS_TITLE,
            "items": [{"label": label, "value": value} for label, value in _RADIO_OFFERS],
        },
        {"type": "text", "text": _RADIO_PRICE},
        {"type": "feature", "icon": "bi-telephone", "text": _RADIO_SHOW},
    ],
}

_RADIO_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": "Par quels modes de financement Vallée FM se finance-t-elle ? Cite-les tous.",
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite les DEUX modes : la publicité (spots de commerces "
                "et d'entreprises de la région) et les fonds publics (subvention de la "
                "Fédération Wallonie-Bruxelles). Une réponse qui n'en cite qu'un, ou qui "
                "ajoute l'abonnement ou la vente (l'écoute est gratuite), est incomplète."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "D'après la page de Vallée FM, indique pour chaque mode de financement s'il "
                "est utilisé par cette radio ou non."
            ),
            "source_document_version_id": DOC,
            "categories": ["Utilisé par Vallée FM", "Non utilisé par Vallée FM"],
            "elements": [
                "La publicité",
                "La vente à l'unité",
                "L'abonnement",
                "Les fonds publics",
            ],
            "correct_categories": [0, 1, 1, 0],
            "explanation": (
                "Les recettes viennent des spots publicitaires (65 %) et d'une subvention de "
                "la Fédération Wallonie-Bruxelles (35 %). L'écoute est gratuite : ni vente à "
                "l'unité ni abonnement."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Pourquoi un spot publicitaire coûte-t-il trois fois plus cher à 7 h 30 qu'à "
                "22 h sur Vallée FM ? Utilise la notion d'audience."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique qu'à 7 h 30 l'audience (le nombre "
                "d'auditeurs) est plus grande qu'à 22 h : l'annonceur touche plus de "
                "personnes, donc la radio peut vendre le spot plus cher."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quel élément de la page montre que Vallée FM est un média interactif ? "
                "Explique ce que cela permet aux auditeurs."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite « Le Direct des auditeurs » (appeler le studio) et "
                "explique que les auditeurs peuvent réagir ou participer à l'émission, en "
                "direct — ils ne font pas que recevoir l'information."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Analyse le financement de Vallée FM : identifie ses deux sources de "
                "recettes, explique le lien entre la publicité et la recherche d'audience, "
                "puis explique en quoi la subvention peut rendre la radio un peu moins "
                "dépendante de son audience."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "3 points : publicité (65 %) et fonds publics (35 %) identifiés (1 point) ; "
                "lien publicité-audience expliqué avec un indice du document (prix du spot "
                "selon le nombre d'auditeurs) (1 point) ; la subvention ne dépend pas du "
                "nombre d'auditeurs, elle assure une partie des recettes même pour des "
                "émissions moins écoutées (1 point)."
            ),
            "expected_points": [
                "Identifie la publicité et la subvention publique",
                "Explique que les recettes publicitaires dépendent de l'audience (prix du spot)",
                "Explique que la subvention garantit une partie des recettes indépendamment de l'audience",
            ],
            "max_score": 3.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Couverture d'un magazine sans publicité
# =============================================================================================

MAGAZINE_TITLE = "Couverture du magazine « Jardins & Potagers »"
_MAG_ISSUER = "Mensuel — n° 87 — avril"
_MAG_KICKER = "Jardins & Potagers"
_MAG_HEADLINE = "SEMER SES TOMATES SANS SERRE"
_MAG_TAGLINE = "Le magazine des jardiniers amateurs"
_MAG_DETAILS = (
    ("cash-coin", "4,90 € — en vente chez votre libraire chaque mois"),
    ("envelope-paper", "Abonnement : 12 numéros pour 45 €, livrés chez vous"),
)
_MAG_FOOTER = "Ce magazine ne contient aucune publicité : il est financé uniquement par ses lecteurs."

MAGAZINE_TEXT = (
    "[Couverture d'un magazine mensuel vendu en librairie — magazine fictif]\n\n"
    f"En haut : « {_MAG_ISSUER} »\nNom du magazine : « {_MAG_KICKER} »\n"
    f"Titre principal : « {_MAG_HEADLINE} »\nSous le titre : « {_MAG_TAGLINE} »\n"
    + "\n".join(f"Encadré : « {text} »" for _icon, text in _MAG_DETAILS)
    + f"\nEn bas de la couverture : « {_MAG_FOOTER} »"
)

MAGAZINE_LAYOUT = {
    "kind": "poster_sheet",
    "palette": "orange",
    "sheet_label": "Couverture de magazine",
    "notice": "Magazine fictif — exercice pédagogique",
    "issuer": _MAG_ISSUER,
    "kicker": _MAG_KICKER,
    "headline": _MAG_HEADLINE,
    "tagline": _MAG_TAGLINE,
    "details": [{"icon": icon, "text": text} for icon, text in _MAG_DETAILS],
    "footer": _MAG_FOOTER,
}

_MAGAZINE_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": (
                "Quels sont les deux modes de financement du magazine « Jardins & "
                "Potagers » ? Appuie chaque réponse sur un élément de la couverture."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite la vente à l'unité (4,90 € chez le libraire) et "
                "l'abonnement (12 numéros pour 45 €), chacun relié à l'élément de la "
                "couverture correspondant."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "« Jardins & Potagers » annonce ne contenir aucune publicité. Quel avantage "
                "cela peut-il présenter pour son contenu, et quelle contrainte cela crée-t-il "
                "pour le magazine ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite un avantage (le contenu est choisi pour les "
                "lecteurs, sans devoir plaire à des annonceurs ni rechercher la plus grande "
                "audience possible) ET une contrainte (le magazine dépend entièrement de ses "
                "lecteurs payants : il doit les convaincre d'acheter ou de s'abonner, sinon "
                "ses recettes baissent)."
            ),
            "max_length": 500,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 — Un site gratuit devient payant
# =============================================================================================

PAYWALL_TITLE = "Publication d'Infos Pays Vert — « Notre site devient payant »"
_PAYWALL_TEXT = (
    "« À partir du 1er mars, Infos Pays Vert devient payant : 3 articles gratuits par mois, "
    "puis un abonnement à 5,99 € par mois. Nos recettes publicitaires ont baissé de moitié en "
    "deux ans ; nous voulons continuer à payer nos quatre journalistes sans multiplier les "
    "publicités. »"
)
_PAYWALL_STATS = ("👍 112 réactions", "💬 46 commentaires", "🔁 9 partages")
_PAYWALL_COMMENTS = (
    ("Sandrine V.", "SV", "p1", None, False,
     "« Dommage, je lisais tout gratuitement… Je vais chercher mes infos ailleurs. »"),
    ("Infos Pays Vert", "IP", "company", "en réponse au commentaire de Sandrine V.", True,
     "« Les 3 premiers articles du mois restent gratuits, et l'abonnement est sans engagement. »"),
    ("Théo M.", "TM", "p2", None, False,
     "« Enfin moins de publicités qui clignotent partout ! Je m'abonne. »"),
    ("Ahmed K.", "AK", "p4", None, False,
     "« 5,99 € par mois, c'est le prix d'un hebdo papier. Je vais réfléchir. »"),
)

PAYWALL_TEXT = (
    "[Publication de la page « Infos Pays Vert », site d'information régional fictif, sur un "
    "réseau social]\n\nInfos Pays Vert :\n" + _PAYWALL_TEXT + "\n\n" + " — ".join(_PAYWALL_STATS)
    + "\n\nCommentaires affichés sous la publication :\n"
    + "\n".join(
        f"- {author}{f' ({badge})' if badge else ''} : {text}"
        for author, _initials, _tone, badge, _reply, text in _PAYWALL_COMMENTS
    )
)

PAYWALL_LAYOUT = {
    "kind": "social_post",
    "notice": "Média et lecteurs fictifs — exercice pédagogique",
    "network": "Réseau social",
    "author": "Infos Pays Vert",
    "initials": "IP",
    "tone": "company",
    "text": _PAYWALL_TEXT,
    "stats": list(_PAYWALL_STATS),
    "comments_title": "Commentaires affichés sous la publication",
    "comments": [
        {
            "author": author, "initials": initials, "tone": tone, "text": text,
            **({"badge": badge} if badge else {}), **({"reply": True} if reply else {}),
        }
        for author, initials, tone, badge, reply, text in _PAYWALL_COMMENTS
    ],
}

_PAYWALL_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": (
                "Quel changement de mode de financement Infos Pays Vert annonce-t-il, et "
                "pour quelle raison ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que le site, gratuit et financé surtout par "
                "la publicité, passe à l'abonnement (5,99 € par mois après 3 articles "
                "gratuits), parce que ses recettes publicitaires ont baissé de moitié."
            ),
            "max_length": 400,
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "Classe chaque lecteur selon le comportement que son commentaire annonce "
                "face au passage d'Infos Pays Vert à l'abonnement."
            ),
            "source_document_version_id": DOC,
            "categories": ["Accepte de payer", "Hésite encore", "Se tourne vers un média gratuit"],
            "elements": ["Théo M.", "Ahmed K.", "Sandrine V."],
            "correct_categories": [0, 1, 2],
            "explanation": (
                "Théo s'abonne (il apprécie d'avoir moins de publicités), Ahmed compare le prix "
                "et réfléchit, Sandrine annonce qu'elle cherchera ses informations ailleurs : "
                "un même changement de financement provoque des comportements différents chez "
                "les publics."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quel élément de cette publication montre qu'Infos Pays Vert est un média "
                "interactif ? Explique."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle cite les commentaires des lecteurs et surtout la "
                "réponse d'Infos Pays Vert à Sandrine V. : les lecteurs peuvent réagir et le "
                "média leur répond."
            ),
            "max_length": 300,
        },
        M,
    ),
    (
        "long_answer",
        {
            "prompt": (
                "Rédige une réponse complète : compare le financement d'Infos Pays Vert avant "
                "et après le 1er mars, explique l'effet possible sur son audience en "
                "t'appuyant sur deux commentaires, puis explique pourquoi le média garde "
                "3 articles gratuits par mois."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "3 points : avant = gratuit, financé surtout par la publicité ; après = "
                "abonnement (1 point) ; effet sur l'audience appuyé sur deux commentaires "
                "(certains lecteurs partent comme Sandrine, d'autres paient comme Théo, "
                "d'autres hésitent comme Ahmed : l'audience risque de baisser) (1 point) ; "
                "les articles gratuits servent à garder une partie de l'audience et à "
                "donner envie de s'abonner (1 point)."
            ),
            "expected_points": [
                "Compare le financement avant (publicité, gratuit) et après (abonnement)",
                "Explique l'effet possible sur l'audience à partir de deux commentaires",
                "Explique le rôle des 3 articles gratuits pour garder des lecteurs",
            ],
            "max_score": 3.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 4 — Mini-situations (choix multiple)
# =============================================================================================

_VIDEO_AD = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Une chaîne de recettes de cuisine en ligne est gratuite pour tout le monde ; "
                "avant chaque vidéo, une publicité de 15 secondes est diffusée. Quel mode de "
                "financement cette situation montre-t-elle ?"
            ),
            "options": [
                {"option_id": "a", "label": "L'abonnement"},
                {"option_id": "b", "label": "Les fonds publics"},
                {"option_id": "c", "label": "La vente à l'unité"},
                {"option_id": "d", "label": "La publicité"},
            ],
            "correct_option_ids": ["d"],
            "explanation": (
                "Le public ne paie rien : ce sont les annonceurs qui paient pour diffuser leur "
                "message avant les vidéos. Plus la chaîne a d'audience, plus elle intéresse "
                "les annonceurs."
            ),
        },
        E,
    ),
)

_PUBLIC_TV = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Une télévision publique ne diffuse aucune publicité pendant ses programmes "
                "pour enfants. Qu'est-ce qui lui permet de s'en passer ?"
            ),
            "options": [
                {"option_id": "a", "label": "Elle reçoit des fonds publics"},
                {"option_id": "b", "label": "Les enfants paient un abonnement"},
                {"option_id": "c", "label": "Ces programmes n'ont aucune audience"},
                {"option_id": "d", "label": "Elle vend chaque émission à l'unité"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Financée en partie par des fonds publics, elle ne dépend pas uniquement des "
                "annonceurs : elle peut renoncer à la publicité pour certains publics ou "
                "certains programmes."
            ),
        },
        M,
    ),
)

FSE02_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE02", key="fse02-radio-locale-mixte", title=RADIO_TITLE,
        content_text=RADIO_TEXT, layout=RADIO_LAYOUT, questions=_RADIO_QUESTIONS,
    ),
    FseCase(
        course_code="FSE02", key="fse02-magazine-sans-publicite", title=MAGAZINE_TITLE,
        content_text=MAGAZINE_TEXT, layout=MAGAZINE_LAYOUT, questions=_MAGAZINE_QUESTIONS,
    ),
    FseCase(
        course_code="FSE02", key="fse02-site-devient-payant", title=PAYWALL_TITLE,
        content_text=PAYWALL_TEXT, layout=PAYWALL_LAYOUT, questions=_PAYWALL_QUESTIONS,
    ),
    FseCase(course_code="FSE02", key="fse02-publicite-video-en-ligne", questions=_VIDEO_AD),
    FseCase(course_code="FSE02", key="fse02-television-publique-enfants", questions=_PUBLIC_TV),
)
