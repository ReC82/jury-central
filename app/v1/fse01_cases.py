"""FSE01 « Communiquer : le schéma de communication » — cas nouveaux (ticket #129).

Le cours analyse un mail de candidature coupé, une affiche de sécurité routière et une
offre d'emploi sur un réseau social ; la banque historique (`import_fse01_to_bank`)
réinterroge ces trois exemples. Les cas ci-dessous gardent les mêmes notions (émetteur,
récepteur, message, code, canal, contexte, obstacle, rétroaction selon le canal) sur
d'autres situations, d'autres supports et d'autres questions :

1. une affiche événementielle d'une maison de quartier (vraie affiche composée :
   illustration dessinée + texte HTML exact), où la rétroaction passe par un AUTRE canal ;
2. une conversation de groupe d'une équipe de futsal : obstacle d'information (consigne
   ambiguë), rétroaction rapide par le même canal, correction pas encore lue par tous ;
3. une note de service affichée dans un supermarché : obstacle de code (jargon et
   abréviations que les nouveaux jobistes ne connaissent pas) ;
4. des mini-situations décrites dans l'énoncé (SMS « ne pas répondre », appel vidéo figé,
   panneau lumineux) pour les questions à choix multiple, qui n'ont pas de document.

Tous les noms, organismes et adresses sont fictifs. Aucun renvoi au cours dans les
documents ; aucune annotation qui donnerait la réponse."""

from app.v1.assets import AssetSpec, VisualType
from app.v1.fse01_content import FSE01_AFFICHE_TITLE, FSE01_MAIL_TITLE, FSE01_SOCIAL_TITLE
from app.v1.fse_cases import DOC, CourseExamples, FseCase
from app.v1.models import AssetKind, AssetSourceType, QuestionDifficulty

E, M, H = QuestionDifficulty.EASY, QuestionDifficulty.MEDIUM, QuestionDifficulty.HARD

FSE01_EXAMPLES = CourseExamples(
    document_titles=frozenset({FSE01_MAIL_TITLE, FSE01_AFFICHE_TITLE, FSE01_SOCIAL_TITLE}),
    markers=("Karim Haddad", "Techno Services", "affiche de sécurité routière"),
)

# =============================================================================================
# Cas 1 — Affiche : atelier de réparation de la Maison de quartier des Tilleuls
# =============================================================================================

_POSTER_CONTEXT = (
    "Affiche au format A3, collée début juin sur la porte vitrée de la boulangerie de la "
    "place des Tilleuls, à Jambes. Les clients la voient en entrant et en sortant du magasin."
)
_POSTER_ISSUER = "Maison de quartier des Tilleuls — asbl"
_POSTER_KICKER = "Atelier de réparation gratuit"
_POSTER_HEADLINE = "TON VÉLO GRINCE ? ON LE RÉPARE ENSEMBLE !"
_POSTER_IMAGE = (
    "deux bénévoles réparent un vélo installé sur un pied d'atelier ; des outils sont "
    "accrochés au mur derrière eux."
)
_POSTER_DATE = "Samedi 14 juin, de 10 h à 16 h"
_POSTER_PLACE = "Cour de l'école communale des Tilleuls, rue des Glycines 12, Jambes"
_POSTER_OBJECTS = "Vélos, trottinettes, petits appareils électriques"
_POSTER_TAGLINE = "Apporte ton objet : les bénévoles t'aident à le réparer toi-même."
_POSTER_FOOTER = (
    "Inscription conseillée par mail : atelier@maisondestilleuls.be — ou sur place, le "
    "jour même."
)

POSTER_TITLE = "Affiche — atelier de réparation de la Maison de quartier des Tilleuls"
POSTER_TEXT = f"""[{_POSTER_CONTEXT}]

En haut de l'affiche : « {_POSTER_ISSUER} »
Bandeau : « {_POSTER_KICKER} »
Titre, en grandes lettres : « {_POSTER_HEADLINE} »
Illustration (dessin) : {_POSTER_IMAGE}
Date : « {_POSTER_DATE} »
Lieu : « {_POSTER_PLACE} »
Objets acceptés : « {_POSTER_OBJECTS} »
Sous l'illustration : « {_POSTER_TAGLINE} »
En bas de l'affiche : « {_POSTER_FOOTER} »"""

POSTER_ILLUSTRATION = AssetSpec(
    key="fse01_atelier_reparation",
    storage_ref="img/fse/cases/fse01_atelier_reparation.svg",
    kind=AssetKind.SVG,
    mime_type="image/svg+xml",
    source_type=AssetSourceType.MANUAL,
    visual_type=VisualType.ILLUSTRATION,
    alt_text="Dessin : " + _POSTER_IMAGE,
    license="Création originale Jury Central",
    provenance="Dessin vectoriel original (SVG) écrit pour le ticket #129",
    caption="Illustration de l'affiche de l'atelier de réparation",
    extra={
        "production": "svg_hand_authored",
        "prompt": "Dessin plat, sans texte ni visage détaillé : " + _POSTER_IMAGE,
        "model": None,
        "ticket": 129,
    },
)

POSTER_LAYOUT = {
    "kind": "poster_sheet",
    "palette": "green",
    "notice": "Affiche fictive — exercice pédagogique",
    "context": _POSTER_CONTEXT,
    "issuer": _POSTER_ISSUER,
    "kicker": _POSTER_KICKER,
    "headline": _POSTER_HEADLINE,
    "image_alt": _POSTER_IMAGE,
    "details": [
        {"icon": "calendar-event", "text": _POSTER_DATE},
        {"icon": "geo-alt", "text": _POSTER_PLACE},
        {"icon": "tools", "text": _POSTER_OBJECTS},
    ],
    "tagline": _POSTER_TAGLINE,
    "footer": _POSTER_FOOTER,
}

_POSTER_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": (
                "Sur l'affiche de l'atelier de réparation, qui est l'émetteur du message, et "
                "à qui ce message s'adresse-t-il (récepteur) ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle identifie la Maison de quartier des Tilleuls (asbl) "
                "comme émetteur et, comme récepteurs, les habitants ou passants du quartier "
                "qui voient l'affiche (clients de la boulangerie), en particulier ceux qui "
                "ont un vélo, une trottinette ou un petit appareil à réparer."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "classification",
        {
            "prompt": (
                "Classe chaque élément de l'affiche de l'atelier de réparation : fait-il "
                "partie du code, du canal ou du message ?"
            ),
            "source_document_version_id": DOC,
            "categories": ["Code", "Canal", "Message"],
            "elements": [
                "Le dessin de deux bénévoles qui réparent un vélo",
                "La question tutoyée en grandes lettres « Ton vélo grince ? »",
                "La feuille A3 collée sur la porte vitrée de la boulangerie",
                "Venir faire réparer gratuitement son objet le 14 juin, avec l'aide de bénévoles",
            ],
            "correct_categories": [0, 0, 1, 2],
            "explanation": (
                "Le dessin et la question tutoyée sont des signes utilisés pour construire le "
                "message (code) ; la feuille collée sur la porte est le support par lequel il "
                "circule (canal) ; l'invitation à venir réparer son objet le 14 juin est ce "
                "qui est transmis (message)."
            ),
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Une cliente de la boulangerie voudrait savoir si elle peut apporter son "
                "grille-pain. Peut-elle poser sa question à l'émetteur par l'affiche "
                "elle-même ? Explique, puis indique ce que l'affiche lui offre pour joindre "
                "l'organisateur."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que l'affiche ne permet pas de rétroaction "
                "directe (on ne peut pas répondre à l'émetteur par la feuille collée sur la "
                "porte), puis indique que l'adresse mail de l'atelier (ou la possibilité de "
                "venir sur place le jour même) permet de joindre l'organisateur par un AUTRE "
                "canal. Une réponse qui affirme que l'affiche permet de répondre "
                "directement est fausse."
            ),
            "max_length": 400,
        },
        H,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Imagine que la boulangerie ferme pour congé du 1er au 15 juin, volet baissé "
                "devant la porte vitrée. Quel élément du schéma de communication est "
                "touché, et quelle conséquence cela a-t-il pour le message de l'affiche ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle identifie le canal (l'affiche sur la porte vitrée "
                "n'est plus visible) comme élément touché — un obstacle — et explique que le "
                "message n'atteint plus les récepteurs avant l'atelier du 14 juin."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Analyse complète de l'affiche de l'atelier de réparation : identifie "
                "l'émetteur, le récepteur, le message, le code, le canal et le contexte, "
                "puis explique ce que l'affiche prévoit pour compenser l'absence de "
                "rétroaction directe."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : émetteur (Maison de quartier des Tilleuls) et récepteurs "
                "(habitants, clients de la boulangerie) correctement identifiés (1 point) ; "
                "message (inviter à venir réparer gratuitement son objet le 14 juin) et "
                "contexte (atelier de quartier, lieu et date) (1 point) ; code (titre "
                "tutoyé, dessin, informations pratiques) distingué du canal (affiche A3 sur "
                "la porte vitrée) (1 point) ; absence de rétroaction directe par l'affiche "
                "et adresse mail ou présence sur place comme autre canal pour joindre "
                "l'organisateur (1 point)."
            ),
            "expected_points": [
                "Identifie l'émetteur (Maison de quartier des Tilleuls) et les récepteurs (habitants, clients)",
                "Résume le message et le situe dans son contexte (atelier gratuit du 14 juin)",
                "Distingue le code (titre, dessin, informations) du canal (affiche sur la porte)",
                "Explique qu'aucune rétroaction directe n'est possible par l'affiche",
                "Indique le mail ou la venue sur place comme autre canal pour joindre l'organisateur",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 2 — Conversation de groupe : changement de salle d'entraînement
# =============================================================================================

CHAT_TITLE = "Conversation du groupe « Futsal Saint-Servais — équipe B »"
_CHAT_CONTEXT = (
    "Groupe d'une application de messagerie, sur smartphone : 12 membres, l'entraîneuse et "
    "les joueurs de l'équipe."
)
_CHAT_MESSAGES = (
    ("Nadia, entraîneuse", "p1", "18 h 02",
     "Changement pour demain : entraînement à 19 h en salle B. Pensez aux chasubles !"),
    ("Bruno", "p2", "18 h 05",
     "Salle B du hall omnisports ou salle B de l'école ? On a les deux 😅"),
    ("Samir", "p3", "18 h 07", "Moi j'avais compris l'école, comme la semaine passée."),
    ("Nadia, entraîneuse", "p1", "18 h 20",
     "Désolée ! Salle B du HALL OMNISPORTS, rue du Stade. Pas l'école."),
    ("Kevin", "p4", "21 h 46",
     "Je découvre seulement les messages, j'étais au travail sans réseau. Ok pour demain."),
)
_CHAT_READ = "Lu par 8 des 12 membres du groupe"
_CHAT_DAY = "Mardi 7 octobre"

CHAT_TEXT = f"""[{_CHAT_CONTEXT}]

{_CHAT_DAY}
""" + "\n".join(f"{time} — {author} : « {text} »" for author, _tone, time, text in _CHAT_MESSAGES[:4]) + f"""
(Sous ce dernier message de Nadia, l'application indique : « {_CHAT_READ} ».)
""" + "\n".join(f"{time} — {author} : « {text} »" for author, _tone, time, text in _CHAT_MESSAGES[4:])

CHAT_LAYOUT = {
    "kind": "chat",
    "notice": "Échange fictif — exercice pédagogique",
    "context": _CHAT_CONTEXT,
    "group": "Futsal Saint-Servais — équipe B",
    "messages": [
        {"author": author, "tone": tone, "day": _CHAT_DAY, "time": time, "text": text,
         **({"status": _CHAT_READ} if index == 3 else {})}
        for index, (author, tone, time, text) in enumerate(_CHAT_MESSAGES)
    ],
}

_CHAT_QUESTIONS = (
    (
        "classification",
        {
            "prompt": (
                "Dans la conversation du groupe de futsal, classe chaque élément dans la "
                "bonne catégorie du schéma de communication (pour le premier message de "
                "Nadia)."
            ),
            "source_document_version_id": DOC,
            "categories": ["Émetteur", "Récepteur", "Canal", "Code"],
            "elements": [
                "Nadia, l'entraîneuse",
                "Les membres du groupe de l'équipe B",
                "L'application de messagerie sur smartphone",
                "Des messages écrits courts, au ton familier",
            ],
            "correct_categories": [0, 1, 2, 3],
            "explanation": (
                "Nadia est à l'origine du message (émetteur) ; les membres du groupe le "
                "reçoivent (récepteurs) ; l'application de messagerie est le support par "
                "lequel il circule (canal) ; les phrases écrites courtes et familières sont "
                "les signes utilisés pour le construire (code)."
            ),
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Quel obstacle contient le premier message de Nadia, et quel message du "
                "groupe montre que cet obstacle a été remarqué ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle identifie une information imprécise ou ambiguë (« salle "
                "B » sans préciser le bâtiment, alors qu'il existe deux salles B) comme "
                "obstacle, et cite la question de Bruno (18 h 05) — ou la réponse de Samir, "
                "qui a compris l'école — comme signe que l'obstacle a été remarqué."
            ),
            "max_length": 400,
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Le message de Bruno à 18 h 05 est-il une rétroaction ? Justifie en "
                "t'appuyant sur le canal utilisé."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle répond oui : Bruno répond à l'émetteur (Nadia) par le "
                "même canal (le groupe de messagerie), ce qui est une rétroaction directe ; "
                "elle permet à Nadia de préciser le lieu. Bonus de justification si elle "
                "note que ce canal permet de répondre facilement et rapidement."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Sous la précision de Nadia (18 h 20), l'application indique « Lu par 8 des "
                "12 membres du groupe ». Pourquoi le message n'est-il peut-être pas encore "
                "arrivé à tous les récepteurs, et quel risque cela crée-t-il pour "
                "l'entraînement du lendemain ?"
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle explique que quatre membres n'ont pas encore lu la "
                "précision (ils n'ont pas consulté le groupe, ou n'avaient pas de réseau, "
                "comme Kevin jusqu'à 21 h 46) : le message n'a donc pas encore atteint tous "
                "les récepteurs ; risque : certains joueurs iront à la mauvaise salle B (à "
                "l'école), comme Samir l'avait compris."
            ),
            "max_length": 400,
        },
        H,
    ),
    (
        "long_answer",
        {
            "prompt": (
                "Rédige une réponse complète : explique comment le premier message de Nadia "
                "a créé un malentendu, comment la rétroaction des joueurs a permis de le "
                "corriger, et pourquoi la même consigne écrite sur une affiche au vestiaire "
                "n'aurait pas permis cette correction."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "3 points : obstacle identifié (« salle B » imprécis, deux salles possibles, "
                "Samir comprend l'école) (1 point) ; rôle de la rétroaction (question de "
                "Bruno, réponse de Samir, précision de Nadia à 18 h 20 par le même canal) "
                "(1 point) ; comparaison des canaux : la messagerie permet de répondre "
                "directement à l'émetteur, une affiche ne le permet pas, donc le "
                "malentendu n'aurait pas été signalé ni corrigé (1 point)."
            ),
            "expected_points": [
                "Identifie l'information imprécise (« salle B ») comme obstacle",
                "Explique comment la question de Bruno et la réponse de Nadia corrigent le malentendu",
                "Explique que la messagerie permet une rétroaction directe, contrairement à une affiche",
            ],
            "max_score": 3.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 3 — Note de service affichée en salle de pause (jargon)
# =============================================================================================

MEMO_TITLE = "Note de service — magasin Gamma Frais de Herstal"
_MEMO_CONTEXT = (
    "Note imprimée et punaisée au panneau d'affichage de la salle de pause. Trois étudiants "
    "jobistes commencent ce samedi : c'est leur premier emploi en magasin."
)
_MEMO_ORG = "Gamma Frais — magasin de Herstal"
_MEMO_TYPE = "Note de service"
_MEMO_META = (
    ("À", "Tout le personnel, y compris les étudiants jobistes du week-end"),
    ("De", "Marc Lenoir, gérant"),
    ("Date", "Vendredi 3 octobre"),
)
_MEMO_PARAGRAPHS = (
    (
        "À partir de ce samedi, réassort du rayon frais avant 8 h via le PDA. Scannez en "
        "priorité les DLC courtes et passez-les en démarque 30 %."
    ),
    "Tout écart de stock est à signaler au N+1 avant la clôture.",
)
_MEMO_CLOSING = "Merci à tous. Questions : Julie Mertens, cheffe du rayon frais, poste téléphonique 214."

MEMO_TEXT = f"""[{_MEMO_CONTEXT}]

{_MEMO_ORG} — {_MEMO_TYPE}
""" + "\n".join(f"{field} : {value}" for field, value in _MEMO_META) + "\n\n" + "\n\n".join(
    _MEMO_PARAGRAPHS
) + f"\n\n{_MEMO_CLOSING}"

MEMO_LAYOUT = {
    "kind": "memo",
    "notice": "Document fictif — exercice pédagogique",
    "context": _MEMO_CONTEXT,
    "org": _MEMO_ORG,
    "doc_type": _MEMO_TYPE,
    "meta": [{"field": field, "value": value} for field, value in _MEMO_META],
    "paragraphs": list(_MEMO_PARAGRAPHS),
    "closing": _MEMO_CLOSING,
}

_MEMO_QUESTIONS = (
    (
        "short_answer",
        {
            "prompt": (
                "Dans la note de service du magasin Gamma Frais, identifie l'émetteur, les "
                "récepteurs et le canal utilisé."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle identifie Marc Lenoir, le gérant (ou la direction du "
                "magasin), comme émetteur ; tout le personnel, y compris les étudiants "
                "jobistes, comme récepteurs ; la feuille imprimée punaisée au panneau "
                "d'affichage de la salle de pause comme canal."
            ),
            "max_length": 300,
        },
        E,
    ),
    (
        "short_answer",
        {
            "prompt": (
                "Pour les trois étudiants jobistes, quel obstacle risque d'empêcher la "
                "bonne compréhension de cette note ? Cite deux mots ou abréviations précis "
                "du document."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "Bonne réponse si elle identifie un obstacle lié au code : un vocabulaire "
                "professionnel et des abréviations que ces nouveaux récepteurs ne "
                "connaissent pas, et cite deux exemples exacts parmi « réassort », « PDA », "
                "« DLC », « démarque », « N+1 », « clôture »."
            ),
            "max_length": 400,
        },
        M,
    ),
    (
        "classification",
        {
            "prompt": (
                "Pour chaque difficulté rencontrée avec la note de service, indique si "
                "l'obstacle touche surtout le code ou surtout le canal."
            ),
            "source_document_version_id": DOC,
            "categories": ["Obstacle lié au code", "Obstacle lié au canal"],
            "elements": [
                "Les jobistes ne savent pas ce que signifie « DLC »",
                "Les jobistes ne passent pas par la salle de pause avant leur premier service",
                "L'abréviation « N+1 » n'est expliquée nulle part",
                "La note est cachée derrière un calendrier sur le panneau d'affichage",
            ],
            "correct_categories": [0, 1, 0, 1],
            "explanation": (
                "Ne pas comprendre une abréviation, c'est ne pas partager le code (les signes "
                "utilisés) ; ne pas voir la feuille, parce qu'on ne passe pas devant le "
                "panneau ou qu'elle est cachée, c'est un problème de support : le canal "
                "n'atteint pas le récepteur."
            ),
        },
        M,
    ),
    (
        "document_analysis",
        {
            "prompt": (
                "Analyse la note de service : identifie l'émetteur, le récepteur, le "
                "message, le code, le canal et le contexte, puis explique l'obstacle qui "
                "touche les jobistes et le moyen que la note leur donne pour obtenir une "
                "réponse à leurs questions."
            ),
            "source_document_version_id": DOC,
            "rubric": (
                "4 points : émetteur (Marc Lenoir, gérant) et récepteurs (tout le personnel, "
                "dont les jobistes) (1 point) ; message (nouvelle organisation du réassort "
                "et des produits à date courte, signaler les écarts) et contexte (magasin, "
                "arrivée de jobistes sans expérience) (1 point) ; code (texte écrit, "
                "vocabulaire professionnel et abréviations) distingué du canal (feuille "
                "punaisée en salle de pause), avec l'obstacle de code pour les jobistes "
                "(1 point) ; la note ne permet pas de répondre directement, mais elle "
                "indique une personne et un poste téléphonique (Julie Mertens, poste 214) "
                "pour poser des questions par un autre canal (1 point)."
            ),
            "expected_points": [
                "Identifie l'émetteur (gérant) et les récepteurs (personnel, jobistes)",
                "Résume le message et précise le contexte (nouveaux jobistes sans expérience)",
                "Distingue le code (vocabulaire, abréviations) du canal (note affichée)",
                "Explique l'obstacle de code pour les jobistes",
                "Indique Julie Mertens (poste 214) comme moyen d'obtenir une réponse par un autre canal",
            ],
            "max_score": 4.0,
        },
        H,
    ),
)

# =============================================================================================
# Cas 4 — Mini-situations décrites dans l'énoncé (questions à choix multiple)
# =============================================================================================

_SITUATION_QUESTIONS_SMS = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Une pharmacie envoie un SMS automatique : « Votre commande est prête. Ne "
                "pas répondre à ce message. » Quel élément du schéma de communication la "
                "mention « Ne pas répondre » limite-t-elle ?"
            ),
            "options": [
                {"option_id": "a", "label": "Le code"},
                {"option_id": "b", "label": "Le contexte"},
                {"option_id": "c", "label": "La rétroaction"},
                {"option_id": "d", "label": "L'émetteur"},
            ],
            "correct_option_ids": ["c"],
            "explanation": (
                "Le client ne peut pas répondre à la pharmacie par ce SMS : la possibilité "
                "de rétroaction par ce canal est volontairement fermée. Le code (texte "
                "écrit), le contexte (commande prête) et l'émetteur (la pharmacie) ne "
                "changent pas."
            ),
        },
        E,
    ),
)

_SITUATION_QUESTIONS_VIDEO = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Pendant un entretien d'embauche en appel vidéo, l'image de la recruteuse se "
                "fige et sa voix n'arrive plus que par morceaux. De quoi s'agit-il dans le "
                "schéma de communication ?"
            ),
            "options": [
                {"option_id": "a", "label": "D'un changement de code"},
                {"option_id": "b", "label": "D'une rétroaction"},
                {"option_id": "c", "label": "D'un changement d'émetteur"},
                {"option_id": "d", "label": "D'un obstacle technique qui perturbe le canal"},
            ],
            "correct_option_ids": ["d"],
            "explanation": (
                "La connexion qui transporte l'image et le son (le canal) est perturbée : "
                "c'est un obstacle technique. La langue utilisée (le code) et la personne "
                "qui parle (l'émetteur) restent les mêmes."
            ),
        },
        M,
    ),
)

_SITUATION_QUESTIONS_SIGN = (
    (
        "multiple_choice",
        {
            "prompt": (
                "Un panneau lumineux au-dessus d'une route nationale affiche « Accident à "
                "2 km — serrez à droite ». Lequel de ces éléments est le CODE de ce message ?"
            ),
            "options": [
                {"option_id": "a", "label": "Les mots et le pictogramme affichés"},
                {"option_id": "b", "label": "Le panneau lumineux lui-même"},
                {"option_id": "c", "label": "Les conducteurs qui passent sous le panneau"},
                {"option_id": "d", "label": "L'accident signalé plus loin"},
            ],
            "correct_option_ids": ["a"],
            "explanation": (
                "Le code est le système de signes utilisé (mots, pictogramme). Le panneau "
                "est le canal, les conducteurs sont les récepteurs et l'accident fait partie "
                "du contexte."
            ),
        },
        M,
    ),
)

FSE01_CASES: tuple[FseCase, ...] = (
    FseCase(
        course_code="FSE01", key="fse01-affiche-atelier-reparation", title=POSTER_TITLE,
        content_text=POSTER_TEXT, layout=POSTER_LAYOUT, illustration=POSTER_ILLUSTRATION,
        questions=_POSTER_QUESTIONS,
    ),
    FseCase(
        course_code="FSE01", key="fse01-groupe-futsal", title=CHAT_TITLE, content_text=CHAT_TEXT,
        layout=CHAT_LAYOUT, questions=_CHAT_QUESTIONS,
    ),
    FseCase(
        course_code="FSE01", key="fse01-note-de-service-jargon", title=MEMO_TITLE,
        content_text=MEMO_TEXT, layout=MEMO_LAYOUT, questions=_MEMO_QUESTIONS,
    ),
    FseCase(course_code="FSE01", key="fse01-sms-ne-pas-repondre", questions=_SITUATION_QUESTIONS_SMS),
    FseCase(course_code="FSE01", key="fse01-appel-video-fige", questions=_SITUATION_QUESTIONS_VIDEO),
    FseCase(course_code="FSE01", key="fse01-panneau-lumineux", questions=_SITUATION_QUESTIONS_SIGN),
)
