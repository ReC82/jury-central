"""Mise en page structurée des documents sources (ticket #149).

Un `SourceDocumentVersion` reste la seule source de vérité (texte exact, immuable, utilisé
par la correction). Ce module décrit seulement comment le MONTRER selon sa vraie nature :
mail, affiche, publication de réseau social, page de média, forum, conversation, note sur
papier à en-tête, fiches numérotées, tableau, schéma de circuit…

Règles :
- **Liée au texte exact.** Une mise en page n'est appliquée que si l'empreinte du texte de la
  version affichée (`text_fingerprint`) correspond à celle pour laquelle elle a été écrite.
  Une nouvelle version du document (texte modifié) retombe sur le rendu générique tant que
  sa mise en page n'est pas revue — jamais une présentation périmée. Un ancien questionnaire
  garde exactement son document (même version, même rendu).
- **Texte mot pour mot.** Chaque texte affiché (hors habillage : en-têtes de colonnes,
  libellés d'interface, mention discrète « fictif ») est un extrait exact du document ;
  `tests/test_ticket149_document_layouts.py` le vérifie, ainsi que la couverture du contenu.
- **Aucune annotation-réponse.** Les commentaires éditoriaux entre crochets deviennent une
  mention discrète hors du document (`notice`) ; les renvois de cours (« voir FSE02 ») et
  les annotations d'analyse qui donneraient la réponse sont listés dans `omitted` — absents
  de l'écran élève, toujours présents dans le texte transmis à la correction.
- **Nouveaux documents** : un document créé avec `content_json={"layout": {...}}` est rendu
  directement par les mêmes composants (`resolve_layout`), sans passer par ce registre.

Rendu : `app/templates/_document_layouts.html` (un composant par `kind`).
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

LAYOUT_SCHEMA_VERSION = 1

# Clés d'habillage : jamais vérifiées comme extraits du texte (libellés d'interface,
# icônes, couleurs, numérotation, mention discrète, colonnes d'un tableau…).
PRESENTATION_KEYS = frozenset(
    {
        "kind",
        "tone",
        "icon",
        "initials",
        "notice",
        "number",
        "display_title",
        "columns",
        "html_ref",
        "image",
        "image_alt",
        "chrome",
        "variant",
        "item_label",
        "marks",
        "type",
        "omitted",
        "header",
        "focusable",
        "branches_from",
        "url",
        "network",
        "forum",
        "field",
        "id",
    }
)

_FOCUS_WORDS = {
    "situation": "situations?",
    "scénario": "scénarios?",
    "extrait": "extraits?",
    "bulletin": "bulletins?",
    "affirmation": "affirmations?",
}


def normalize_text(text: str) -> str:
    """Espaces normalisés ; « assurance- chômage » (coupure de ligne du texte source)
    comparé comme « assurance-chômage »."""
    text = re.sub(r"\s+", " ", text or "").strip()
    return re.sub(r"(\w)- (\w)", r"\1-\2", text)


def text_fingerprint(text: str | None) -> str:
    return hashlib.sha256(normalize_text(text or "").encode("utf-8")).hexdigest()[:16]


def iter_content_strings(node: Any, key: str | None = None):
    """Toutes les chaînes de CONTENU d'une mise en page (hors clés d'habillage)."""
    if key in PRESENTATION_KEYS:
        return
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for child_key, child in node.items():
            yield from iter_content_strings(child, child_key)
    elif isinstance(node, list | tuple):
        for child in node:
            yield from iter_content_strings(child, key)


def comparable(text: str) -> str:
    """Forme de comparaison (tests de fidélité) : espaces et casse neutralisés."""
    text = normalize_text(text)
    return re.sub(r"\s+([.,;:)])", r"\1", text).casefold()


def verification_corpus(title: str | None, content_text: str | None, layout: dict[str, Any]) -> str:
    """Titre + texte exact de la version, privés des fragments volontairement retirés de
    l'écran (`omitted`) : tout texte de contenu d'une mise en page doit en être un extrait."""
    corpus = normalize_text(f"{title or ''} {content_text or ''}")
    for fragment in layout.get("omitted", []):
        corpus = corpus.replace(normalize_text(fragment), " ")
    return comparable(corpus)


# =========================================================================================
# Registre — une entrée par document installé (titre exact + empreinte du texte exact).
# =========================================================================================

_FICTIVE = "Document fictif — exercice pédagogique"

_REGISTRY: dict[tuple[str, str], dict[str, Any]] = {}


def _register(title: str, fingerprint: str, layout: dict[str, Any]) -> None:
    _REGISTRY[(title, fingerprint)] = layout


# --- FSE01 -------------------------------------------------------------------------------

_register(
    "Candidature par mail — coupure de connexion",
    "4f3a13974433231a",
    {
        "kind": "email_thread",
        "notice": "Échange fictif — exercice pédagogique",
        "messages": [
            {
                "initials": "KH",
                "tone": "p1",
                "from_name": "Karim Haddad, candidat",
                "from_addr": "karim.haddad82@maileo.be",
                "to": "recrutement@entrepots-dufresne.be",
                "date": "12 mars à 9h04",
                "subject": "Candidature — poste de manutentionnaire",
                "paragraphs": [
                    "Madame, Monsieur,",
                    ("Je me permets de vous contacter suite à votre annonce parue sur le site "
                    "du Forem pour le poste de manutentionnaire au sein de vos entrepôts de "
                    "Wavre. Je dispose d'une expérience de trois ans dans la préparation de "
                    "commandes et je suis titulaire du permis cariste catégorie 3."),
                    "Vous trouverez en pièce jointe mon",
                ],
                "interrupted": "Le message s'arrête ici, en pleine phrase, sans pièce jointe. "
                "La connexion internet de Karim a été coupée à ce moment précis ; son "
                "logiciel de messagerie a automatiquement envoyé le message resté inactif "
                "quelques minutes plus tard, tel quel, sans que Karim ne s'en rende compte "
                "avant le lendemain.",
            },
            {
                "initials": "ED",
                "tone": "p3",
                "from_name": "Le service recrutement — Entrepôts Dufresne",
                "from_addr": "recrutement@entrepots-dufresne.be",
                "to": "karim.haddad82@maileo.be",
                "date": "13 mars à 14h20",
                "subject": "RE: Candidature — poste de manutentionnaire",
                "paragraphs": [
                    "Bonjour,",
                    ("Nous avons bien reçu votre message, mais celui-ci s'arrête au milieu "
                    "d'une phrase et ne comporte aucune pièce jointe. Pourriez-vous nous "
                    "renvoyer votre candidature complète, accompagnée de votre CV ?"),
                    "Cordialement,",
                ],
                "signature": "Le service recrutement — Entrepôts Dufresne",
            },
        ],
    },
)

_register(
    "Affiche de sécurité routière — bord d'autoroute",
    "9fa16f4fb40135a8",
    {
        "kind": "poster",
        "html_ref": "FSE01_AFFICHE_CARD_HTML",
        "legend_title": "Affiche grand format installée en bordure d'autoroute, visible depuis "
        "les véhicules en circulation",
        "legend": [
            {
                "label": "Texte principal",
                "text": "en grandes lettres blanches sur fond rouge : « 90, C'EST DÉJÀ TROP "
                "VITE QUAND UN ENFANT TRAVERSE »",
            },
            {
                "label": "Sous-titre",
                "text": "en lettres plus petites, sous le texte principal : « Ralentir, c'est "
                "voir à temps. »",
            },
            {
                "label": "Image",
                "text": "silhouette noire et stylisée d'un enfant en train de traverser, à côté "
                "d'un passage piéton dessiné de façon simplifiée.",
            },
            {
                "label": "Logo institutionnel",
                "text": "en bas à droite de l'affiche : logo du Service public de Wallonie "
                "(SPW), accompagné de la mention « Sécurité routière Wallonie ».",
            },
            {
                "label": "QR code",
                "text": "Un petit QR code est imprimé dans le coin inférieur gauche de "
                "l'affiche ; il renvoie, une fois scanné, vers une page d'information sur "
                "les limitations de vitesse en zone habitée.",
            },
        ],
    },
)

_register(
    "Publication sur un réseau social — offre d'emploi",
    "bccc9e8f2e95dd33",
    {
        "kind": "social_post",
        "network": "Réseau social professionnel",
        "author": "Techno Services Wallonie",
        "initials": "TS",
        "tone": "company",
        "time": "publiée il y a 3 heures",
        "text": "« Nous recrutons ! Techno Services cherche un·e technicien·ne de maintenance "
        "industrielle pour notre site de Charleroi. Contrat à durée indéterminée, expérience "
        "en électromécanique appréciée. Postulez via le lien en commentaire ! #emploi "
        "#Charleroi #technicien »",
        "stats": ["👍 24 réactions", "💬 7 commentaires", "🔁 5 partages"],
        "comments_title": "Commentaires affichés sous la publication",
        "comments": [
            {
                "author": "Fatima B.",
                "initials": "FB",
                "tone": "p1",
                "text": "« Le poste est-il ouvert aux débutant·e·s avec un certificat obtenu "
                "via le Forem ? »",
            },
            {
                "author": "Techno Services Wallonie",
                "initials": "TS",
                "tone": "company",
                "reply": True,
                "badge": "en réponse au commentaire de Fatima B.",
                "text": "« Oui, une formation complémentaire est prévue à l'embauche. "
                "N'hésitez pas à postuler ! »",
            },
            {
                "author": "Mourad T.",
                "initials": "MT",
                "tone": "p2",
                "badge": "a partagé la publication",
                "text": "« Je connais quelqu'un que ça peut intéresser, je transmets ! »",
            },
            {
                "author": "Julien P.",
                "initials": "JP",
                "tone": "p4",
                "text": "« Encore une offre qui ne précise pas le salaire... »",
            },
        ],
    },
)

# --- FSE02 -------------------------------------------------------------------------------

_register(
    "L'Hebdo du Littoral — page d'abonnement",
    "ddccae089e1537f6",
    {
        "kind": "webpage",
        "variant": "paid",
        "notice": "Média fictif créé pour cet exercice — journal hebdomadaire papier et "
        "numérique",
        "url": "Page d'abonnement",
        "site": "L'HEBDO DU LITTORAL",
        "tagline": "Abonnez-vous",
        "blocks": [
            {"type": "lead", "text": "Accédez à l'intégralité de nos articles, dossiers et enquêtes locales."},
            {
                "type": "offers",
                "title": "Nos formules :",
                "items": [
                    {"label": "Édition papier + numérique", "value": "14 € par mois"},
                    {"label": "Édition numérique seule", "value": "9 € par mois"},
                    {"label": "Numéro à l'unité, en kiosque", "value": "2,50 €"},
                ],
            },
            {
                "type": "quote",
                "text": "« Sans publicité intrusive, sans contenu sponsorisé : notre seule source "
                "de revenus est constituée par nos lecteurs et lectrices. »",
            },
            {
                "type": "text",
                "text": "Aucun article complet n'est consultable sans abonnement ou achat du "
                "numéro. Un encadré « Vos lettres » publie chaque semaine une sélection de "
                "courriers de lecteurs en réaction aux articles parus.",
            },
        ],
    },
)

_register(
    "Le Flash Infos — page d'accueil",
    "9c0d21631df1708f",
    {
        "kind": "webpage",
        "variant": "free",
        "notice": "Capture d'une page d'accueil — média fictif créé pour cet exercice",
        "url": "Page d'accueil",
        "site": "LE FLASH INFOS",
        "tagline": "Toute l'actu, 100 % gratuite",
        "blocks": [
            {"type": "ad", "text": "« Soldes chez MégaStore, -40 % cette semaine »"},
            {
                "type": "headline",
                "kicker": "À LA UNE",
                "text": "Travaux sur le pont de la gare, circulation perturbée dès lundi",
            },
            {"type": "ad", "text": "« Assurance auto moins chère avec AutoPlus »"},
            {
                "type": "text",
                "text": "Tous nos articles sont accessibles gratuitement, sans inscription. Le "
                "Flash Infos vit exclusivement des revenus publicitaires générés par les "
                "annonceurs visibles sur le site : plus un article est consulté, plus il "
                "génère de revenus publicitaires pour le site. Chaque article affiche un "
                "compteur de vues et un bouton « Partager », et permet de laisser un "
                "commentaire visible publiquement sous le texte.",
            },
        ],
    },
)

_register(
    "Radio Communauté Wallonie (RCW) — page « Qui sommes-nous »",
    "34192ad6c15592e2",
    {
        "kind": "webpage",
        "variant": "public",
        "notice": "Extrait d'une page web — média de service public fictif, créé pour cet "
        "exercice",
        "url": "Qui sommes-nous",
        "site": "Radio Communauté Wallonie (RCW)",
        "tagline": "Qui sommes-nous",
        "blocks": [
            {
                "type": "text",
                "text": "Radio Communauté Wallonie (RCW) est un média de service public. Son "
                "fonctionnement est financé par une dotation publique, votée chaque année, et "
                "non par la vente de ses programmes ni par la publicité commerciale.",
            },
            {
                "type": "feature",
                "icon": "bi-bullseye",
                "text": "Notre mission : informer l'ensemble de la population, y compris sur des "
                "sujets qui intéressent peu les annonceurs publicitaires (santé publique, "
                "éducation, actualité institutionnelle locale).",
            },
            {
                "type": "feature",
                "icon": "bi-broadcast",
                "text": "RCW ne diffuse aucune publicité commerciale entre ses programmes. Chaque "
                "matin, une émission en direct permet aux auditeurs d'appeler l'antenne pour "
                "réagir à l'actualité du jour.",
            },
        ],
    },
)

# --- FSE03 -------------------------------------------------------------------------------

_register(
    "Présence en ligne de Sophie Lambert — éléments retrouvés par une recherche",
    "33ea1c5ff256b728",
    {
        "kind": "findings",
        "notice": "Candidate fictive à un poste de gestionnaire de stock — éléments créés pour "
        "cet exercice",
        "heading": "Éléments retrouvés en ligne au sujet de Sophie Lambert",
        "items": [
            {
                "icon": "bi-person-badge",
                "image": "img/fse03_sophie_portrait.png",
                "image_alt": "Illustration : photo de profil professionnelle",
                "text": "Une photo de profil professionnelle, publiée par Sophie elle-même sur "
                "un réseau professionnel, accompagnée d'un résumé de son parcours.",
            },
            {
                "icon": "bi-camera",
                "image": "img/fse03_sophie_birthday.png",
                "image_alt": "Illustration : photo prise lors d'un anniversaire",
                "text": "Une photo prise lors d'un anniversaire il y a deux ans, sur laquelle "
                "Sophie apparaît : la photo a été publiée par une amie, qui y a identifié "
                "Sophie par son nom. Sophie n'a jamais publié cette photo elle-même et n'a pas "
                "demandé son retrait.",
            },
            {
                "icon": "bi-controller",
                "text": "Un commentaire écrit par Sophie il y a cinq ans, sous son vrai nom, sur "
                "un forum de jeux vidéo : le ton y est très familier et comporte des insultes "
                "adressées à d'autres joueurs dans le feu d'une partie en ligne.",
            },
            {
                "icon": "bi-chat-square-quote",
                "text": "Une recommandation professionnelle écrite par un ancien collègue de "
                "Sophie sur le même réseau professionnel, décrivant Sophie comme « rigoureuse "
                "et fiable dans la gestion des commandes ».",
            },
            {
                "icon": "bi-people",
                "text": "Sophie est membre visible de deux groupes en ligne : un groupe de "
                "randonneurs amateurs de sa région, et un groupe professionnel rassemblant des "
                "gestionnaires de stock du secteur de la logistique.",
            },
        ],
    },
)

_register(
    "Note interne du service recrutement — avant l'entretien de Sophie Lambert",
    "e0a81733917ad7ee",
    {
        "kind": "memo",
        "notice": "Note rédigée dans une entreprise fictive, créée pour cet exercice",
        "org": "Service recrutement",
        "doc_type": "Note interne",
        "meta": [{"field": "Objet", "value": "avant un entretien d'embauche"}],
        "paragraphs": [
            ("Avant l'entretien de demain avec Sophie Lambert, j'ai consulté sa présence en "
            "ligne."),
            ("Première impression plutôt bonne : la recommandation d'un ancien collègue, qui la "
            "décrit comme rigoureuse et fiable, correspond bien au profil recherché pour ce "
            "poste. Son appartenance au groupe professionnel de gestionnaires de stock "
            "confirme aussi son implication dans le secteur."),
            ("Un point m'a cependant interpellé : un ancien commentaire, publié il y a cinq "
            "ans sur un forum de jeux vidéo, où elle s'exprime de façon très familière et "
            "insultante envers d'autres joueurs. Ce commentaire date d'avant le début de sa "
            "carrière professionnelle et concerne un contexte de loisir sans aucun rapport "
            "avec le poste, mais il reste visible publiquement sous son vrai nom et pourrait "
            "donner une impression négative à qui tombe dessus sans contexte."),
            ("Je vais quand même mener l'entretien normalement, en me concentrant sur son "
            "parcours et ses compétences réelles — mais ce point me rappelle qu'une "
            "publication ancienne, même sans lien avec la vie professionnelle, peut rester "
            "visible des années plus tard et influencer la première impression que l'on se "
            "fait de quelqu'un."),
        ],
    },
)

# --- FSE04 -------------------------------------------------------------------------------

_register(
    "Publication dans un groupe en ligne « Fous rires du quotidien »",
    "cbbfbe56db74045c",
    {
        "kind": "social_post",
        "notice": "Groupe et commentaires fictifs, créés pour cet exercice — le contenu de la "
        "vidéo elle-même n'est pas décrit",
        "network": "Groupe en ligne",
        "group": "Fous rires du quotidien",
        "visibility": "Groupe public",
        "members": "2 400 membres",
        "author": "Publication d'un membre",
        "initials": "?",
        "tone": "p5",
        "text": "« Regardez ce qui est arrivé à ce pauvre gars dans la rue aujourd'hui, "
        "j'étais mort de rire ! »",
        "attachment": {
            "type": "video",
            "label": "vidéo jointe, non reproduite ici",
            "text": "une personne trébuche dans un lieu public et est filmée à son insu par "
            "un passant, visiblement désorientée et gênée après sa chute",
        },
        "stats": ["En quelques heures, la vidéo est partagée 340 fois dans le groupe."],
        "comments_title": "Commentaires affichés sous la publication",
        "comments": [
            {"author": "Membre A", "initials": "A", "tone": "p1", "text": "« Hahaha, il a trop la honte ! »"},
            {
                "author": "Membre B",
                "initials": "B",
                "tone": "p2",
                "text": "« Quelqu'un sait qui c'est ? Faut vraiment pas avoir de chance »",
            },
            {"author": "Membre C", "initials": "C", "tone": "p3", "text": "« Je l'ai aussi envoyée à mes potes, trop drôle »"},
            {
                "author": "Membre D",
                "initials": "D",
                "tone": "p4",
                "text": "« Franchement, c'est méchant de se moquer comme ça, elle n'a rien "
                "demandé »",
            },
            {
                "author": "Membre E",
                "initials": "E",
                "tone": "p6",
                "text": "« Allez, c'est juste pour rire, personne n'est blessé »",
            },
        ],
    },
)

_register(
    "Témoignage de Karim, membre du groupe, qui n'a pas partagé la vidéo",
    "0c2ed457040968aa",
    {
        "kind": "quotes",
        "notice": "Témoignage fictif — exercice pédagogique",
        "items": [
            {
                "actor": "Karim, membre du groupe, qui n'a pas partagé la vidéo",
                "initials": "K",
                "tone": "p2",
                "text": "« J'ai vu la vidéo passer dans le groupe, comme beaucoup d'autres "
                "membres. Honnêtement, la première réaction, c'est presque un réflexe de "
                "sourire parce que tout le monde autour de moi trouvait ça drôle, et le groupe "
                "entier semblait d'accord. Mais je me suis dit que cette personne n'avait rien "
                "demandé, et que ça pourrait être n'importe qui, moi y compris. Je n'ai ni "
                "partagé la vidéo, ni laissé de commentaire moqueur. Je sais que d'autres "
                "membres du groupe n'ont pas non plus participé, même s'ils ne l'ont pas dit "
                "publiquement. Ce n'est pas parce qu'un groupe entier semble pousser dans une "
                "direction que chaque personne qui en fait partie agit forcément de la même "
                "façon. »",
            }
        ],
    },
)

# --- FSE05 / FSE06 (fiches numérotées) ----------------------------------------------------


def _numbered(label: str, texts: list[str], icons: list[str] | None = None) -> list[dict]:
    items = []
    for index, text in enumerate(texts, start=1):
        item = {"number": index, "label": f"{label} {index}", "text": text}
        if icons:
            item["icon"] = icons[index - 1]
        items.append(item)
    return items


_register(
    "Six situations — photographier et diffuser une image ou une donnée",
    "8fe757516308dadd",
    {
        "kind": "cards",
        "notice": "Six situations fictives, rédigées pour cet exercice — aucune personne, aucun "
        "lieu réel",
        "item_label": "Situation",
        "items": _numbered(
            "Situation",
            [
                ("Léa photographie la façade d'un monument touristique très fréquenté. "
                "Plusieurs passants anonymes se trouvent par hasard en arrière-plan, parmi la "
                "foule ; aucun n'est mis en évidence ni facilement identifiable sur la photo."),
                ("Lors d'un anniversaire chez des amis, Thomas prend une photo nette de son ami "
                "Nabil en train de souffler ses bougies, bien reconnaissable au premier plan. "
                "Il publie ensuite cette photo sur son compte public (1 200 abonnés), sans en "
                "parler à Nabil au préalable."),
                ("Pendant une manifestation dans une rue commerçante, un reporter filme "
                "l'ensemble du cortège pour un reportage : la caméra montre la foule des "
                "participants, sans isoler ni mettre en avant un visage en particulier."),
                ("Chloé reçoit par message privé, de la part d'une amie, une photo prise « entre "
                "nous » lors d'une soirée réunissant un petit groupe de proches. Elle décide "
                "ensuite de publier cette photo dans un groupe public de 500 membres, sans "
                "demander l'accord des personnes qui y figurent."),
                ("Un parent publie, sur un compte visible par ses 800 contacts, une photo de son "
                "enfant de 9 ans en vacances, parfaitement identifiable, sans avoir posé la "
                "question à l'enfant au préalable."),
                ("Un site internet propose à ses visiteurs de remplir un formulaire (nom, numéro "
                "de téléphone, établissement scolaire) pour « participer à un concours », sans "
                "préciser à quoi ces informations serviront ensuite ni qui pourra les "
                "consulter."),
            ],
        ),
    },
)

_register(
    "Dix scénarios — comportements en ligne à reconnaître",
    "0435cfd0bab2e1d1",
    {
        "kind": "cards",
        "notice": "Dix scénarios fictifs, rédigés pour cet exercice — aucune personne, aucun "
        "organisme réel",
        "item_label": "Scénario",
        "items": _numbered(
            "Scénario",
            [
                ("Depuis plusieurs semaines, un petit groupe d'élèves envoie chaque jour des "
                "messages moqueurs à Sarah dans un groupe de classe, même après qu'elle leur a "
                "demandé d'arrêter à plusieurs reprises."),
                ("Dans les commentaires sous une vidéo, un internaute écrit à l'auteur : « Tu es "
                "vraiment un idiot fini, tu ne sers à rien »."),
                ("Un internaute affirme publiquement, sans fournir aucune preuve, qu'un "
                "commerçant du quartier « vole systématiquement ses clients sur la monnaie "
                "rendue »."),
                ("Dans un message privé envoyé à une ancienne collègue, une personne écrit : « Si "
                "tu continues à parler de moi comme ça, tu vas le regretter »."),
                ("Sous une offre d'emploi publiée en ligne, un commentaire affirme que les "
                "candidats d'une origine précise « ne devraient pas être engagés dans cette "
                "entreprise »."),
                ("Une personne crée un faux profil au nom d'un camarade de classe, utilise sa "
                "photo, et publie des messages en se faisant passer pour lui auprès d'autres "
                "élèves."),
                ("Un adolescent devine le mot de passe du compte d'un ami et consulte ses "
                "messages privés, sans le lui avoir demandé ni le lui dire ensuite."),
                ("Une personne reçoit en privé une photo intime, puis la partage dans plusieurs "
                "groupes en ligne dans le but explicite d'humilier la personne concernée."),
                ("Une association collecte les adresses e-mail des participants à un événement, "
                "puis les transmet à une entreprise de publicité, sans en avoir informé les "
                "participants au préalable."),
                ("Un internaute publie un commentaire qui critique sévèrement, mais sans insulte "
                "ni accusation non prouvée, la qualité du service d'un restaurant où il a "
                "mangé."),
            ],
        ),
    },
)

# --- FSE07 (dossier : note, conversation, forum) --------------------------------------------

_register(
    "Note de la direction — école fictive « Athénée du Parc »",
    "a3198d31e33fbd80",
    {
        "kind": "memo",
        "notice": _FICTIVE,
        "org": "Athénée du Parc",
        "doc_type": "Note interne",
        "meta": [
            {"field": "Signée par", "value": "M. Devos, directeur adjoint"},
            {"field": "Date", "value": "14 mars 2026"},
        ],
        "paragraphs": [
            ("Le 12 mars 2026, durant la récréation de midi, un élève a filmé un camarade qui "
            "trébuchait dans la cour, sans le consentement de la personne filmée. La vidéo a "
            "été partagée le jour même dans le groupe de discussion de la classe de 5e B, "
            "comptant 24 élèves. La direction a été informée le 13 mars par un enseignant. "
            "L'élève ayant filmé et partagé la vidéo a été reçu avec ses parents le 14 mars. "
            "La vidéo a été supprimée du groupe à la demande de la direction. Aucune autre "
            "mesure n'est communiquée dans cette note.")
        ],
    },
)

_register(
    "Messages échangés dans le groupe de la classe de 5e B",
    "61190deddb600265",
    {
        "kind": "chat",
        "notice": "Échange fictif, rédigé pour cet exercice — prénoms fictifs",
        "group": "Classe de 5e B",
        "messages": [
            {"author": "Yasmine", "tone": "p1", "day": "12 mars", "time": "12h41",
             "text": "« Vous avez vu la vidéo de Lucas qui tombe dans la cour ? Trop drôle »"},
            {"author": "Karim", "tone": "p2", "day": "12 mars", "time": "12h43",
             "text": "« Pas cool de filmer ça sans lui demander, non ? »"},
            {"author": "Yasmine", "tone": "p1", "day": "12 mars", "time": "12h45",
             "text": "« Oh ça va, c'est juste une vidéo, il va pas en mourir »"},
            {"author": "Elena", "tone": "p3", "day": "12 mars", "time": "12h50",
             "text": "« Moi je trouve que ça craint, il a eu l'air vraiment gêné après »"},
            {"author": "Thibault", "tone": "p4", "day": "12 mars", "time": "13h02",
             "text": "« De toute façon tout le monde filme tout le temps, c'est normal maintenant »"},
            {"author": "Karim", "tone": "p2", "day": "12 mars", "time": "13h10",
             "text": "« Justement, je pense que c'est là le problème »"},
            {"author": "Elena", "tone": "p3", "day": "13 mars", "time": "08h15",
             "text": "« La direction est au courant, Lucas a dû être super mal à l'aise pendant deux jours »"},
        ],
    },
)

_register(
    "Publication anonyme sur un forum local (non datée, auteur non identifié)",
    "6873c0086db2c7da",
    {
        "kind": "forum_post",
        "notice": _FICTIVE,
        "display_title": "Publication sur un forum local",
        "forum": "Forum local",
        "topic": "« Encore une école qui ne fait rien contre le harcèlement »",
        "pseudo": "parent_inquiet93",
        "status": "Utilisateur anonyme",
        "body": "« On m'a raconté qu'un élève de l'Athénée du Parc a été filmé et humilié "
        "devant toute l'école, et que la direction n'a strictement rien fait. C'est à chaque "
        "fois pareil dans ces écoles, elles préfèrent cacher les problèmes plutôt que de "
        "sanctionner vraiment les responsables. Il paraît même que ce genre de vidéo circule "
        "encore ailleurs. Il serait temps que les autorités s'occupent sérieusement de ce "
        "problème qui ne fait qu'empirer d'année en année. »",
    },
)

# --- FSE08 / FSE09 ------------------------------------------------------------------------

_register(
    "Tableau des niveaux de pouvoir en Belgique (à compléter) et affirmations à vérifier",
    "a5bb5cb319adf548",
    {
        "kind": "table",
        "notice": "Document rédigé pour cet exercice à partir de sources belges officielles "
        "vérifiées — références dans le cours",
        "heading": "TABLEAU DES NIVEAUX DE POUVOIR",
        "columns": ["Niveau de pouvoir", "Compétences", "Norme adoptée"],
        "rows": [
            ["Niveau fédéral",
             ("compétences qui concernent l'ensemble du pays : justice, affaires étrangères, "
             "défense, police fédérale, sécurité sociale."),
             "la loi."],
            ["Régions (Région flamande, Région wallonne, Région de Bruxelles-Capitale)",
             ("compétences liées au territoire : économie, emploi, environnement, logement, "
             "travaux publics."),
             ("Norme adoptée par la Région flamande ou la Région wallonne : le décret. Norme "
             "adoptée par la Région de Bruxelles-Capitale : l'ordonnance.")],
            ["Communautés (Communauté française, Communauté flamande, Communauté germanophone)",
             ("compétences liées aux personnes, à la langue et à la culture : enseignement, "
             "culture, aide à la jeunesse, matières personnalisables."),
             ("Norme adoptée par une Communauté : le décret (sauf la Communauté germanophone "
             "pour certaines matières, où des règles particulières existent).")],
            ["Provinces", "niveau intermédiaire, compétences d'intérêt provincial.", "—"],
            ["Communes",
             ("niveau de pouvoir le plus proche du citoyen, compétences de proximité (état "
             "civil, urbanisme local, propreté publique)."),
             "—"],
        ],
        "after": {
            "heading": "AFFIRMATIONS À VÉRIFIER",
            "intro": "certaines sont vraies, d'autres fausses — les exceptions sont précisées "
            "ci-dessus",
            "item_label": "Affirmation",
            "items": [
                {"number": "A", "label": "Affirmation A",
                 "text": "« Le niveau fédéral s'occupe de la justice et de la défense nationale. »"},
                {"number": "B", "label": "Affirmation B",
                 "text": "« La Région de Bruxelles-Capitale adopte des décrets, exactement comme "
                 "la Wallonie et la Flandre. »"},
                {"number": "C", "label": "Affirmation C",
                 "text": "« Il existe trois Communautés et trois Régions en Belgique, qui se "
                 "superposent exactement sur le même territoire. »"},
                {"number": "D", "label": "Affirmation D",
                 "text": "« Les communes sont le niveau de pouvoir le plus proche du citoyen. »"},
                {"number": "E", "label": "Affirmation E",
                 "text": "« La Belgique est une monarchie constitutionnelle où le roi dispose de "
                 "tous les pouvoirs qu'il souhaite exercer. »"},
            ],
        },
        "omitted": ["Norme adoptée à ce niveau :"],
    },
)

_register(
    "Dix situations — qui décide de quoi ?",
    "4c9fa08a390e7772",
    {
        "kind": "cards",
        "notice": "Dix situations fictives, rédigées pour cet exercice — aucun organisme réel",
        "item_label": "Situation",
        "items": _numbered(
            "Situation",
            [
                ("Une nouvelle loi fixe les règles de la procédure pénale applicables dans tout "
                "le pays."),
                ("Une région modifie les aides financières destinées aux entreprises qui "
                "s'installent sur son territoire."),
                ("Une communauté adapte les programmes de cours applicables dans les écoles qui "
                "relèvent d'elle."),
                ("Une commune décide d'installer de nouveaux bancs publics et d'entretenir ses "
                "trottoirs."),
                ("L'État décide d'envoyer des troupes dans le cadre d'une mission "
                "internationale."),
                ("Une région adopte de nouvelles normes environnementales pour les entreprises "
                "situées sur son territoire."),
                ("Une communauté organise une campagne culturelle dans les bibliothèques "
                "publiques qu'elle subventionne."),
                ("Une personne malade est soignée à l'hôpital et une partie des soins est "
                "remboursée par une mutualité : plusieurs niveaux de pouvoir interviennent "
                "dans ce remboursement (fédéral pour l'assurance maladie-invalidité, mais aussi "
                "des matières personnalisables gérées par les Communautés pour d'autres "
                "aspects de la santé)"),
                ("Une province organise une aide technique aux communes de son territoire pour "
                "un projet d'intérêt local."),
                ("Un gouvernement fédéral et un gouvernement régional doivent chacun donner leur "
                "accord pour une politique qui touche à la fois une compétence fédérale (ex. "
                "fiscalité générale) et une compétence régionale (ex. logement)"),
            ],
        ),
        "omitted": [
            "— exemple volontairement présenté comme partagé, sans réponse unique trompeuse.",
            (": exemple volontairement présenté comme nécessitant une coordination entre "
            "niveaux, sans réponse unique trompeuse."),
            "sauf mention explicite du niveau de pouvoir lui-même",
        ],
    },
)

# Ticket #152 : version d'examen (le niveau qui décide n'est plus nommé dans la situation).
_register(
    "Dix situations — qui décide de quoi ?",
    "288cacd0111fb3e4",
    {
        "kind": "cards",
        "notice": "Dix situations fictives, rédigées pour cet exercice — aucun organisme réel. "
        "Le niveau de pouvoir qui décide n'est volontairement pas nommé : c'est à toi de le "
        "déterminer.",
        "item_label": "Situation",
        "items": _numbered(
            "Situation",
            [
                ("De nouvelles règles de procédure pénale s'appliqueront de la même façon dans "
                "tout le pays."),
                ("Les aides financières destinées aux entreprises qui s'installent en Wallonie "
                "sont modifiées."),
                "Les programmes de cours des écoles francophones sont adaptés.",
                ("De nouveaux bancs publics sont installés dans un quartier et les trottoirs de "
                "la localité sont entretenus."),
                ("Des militaires belges sont envoyés à l'étranger dans le cadre d'une mission "
                "internationale."),
                ("De nouvelles normes environnementales sont adoptées pour les entreprises "
                "situées en Wallonie."),
                ("Une campagne culturelle est organisée dans des bibliothèques publiques "
                "francophones subventionnées."),
                ("Une personne malade est soignée à l'hôpital. Une partie des soins est "
                "remboursée par sa mutualité, dans le cadre de l'assurance maladie-invalidité ; "
                "d'autres aspects de sa prise en charge, comme la prévention, relèvent des "
                "matières personnalisables."),
                ("Les communes d'un même territoire reçoivent une aide technique pour un projet "
                "d'intérêt local, organisée par le niveau de pouvoir situé entre la commune et "
                "la Région."),
                ("Une même politique combine une réforme de la fiscalité générale et de "
                "nouvelles règles sur le logement : elle ne peut être mise en œuvre qu'avec "
                "l'accord de deux gouvernements différents."),
            ],
        ),
    },
)

# --- FSE10 / FSE11 ------------------------------------------------------------------------

_register(
    "Tableau daté des scrutins belges (vérifié le 2026-10-01)",
    "d70aa5142c16745e",
    {
        "kind": "table",
        "notice": "Tableau rédigé pour ce cours à partir de sources belges officielles/publiques "
        "vérifiées le 2026-10-01 — références dans le cours",
        "columns": ["Scrutin", "Ce qu'il élit et ses règles"],
        "rows": [
            ["SCRUTIN FÉDÉRAL",
             ("élit la Chambre des représentants. Vote obligatoire sur tout le territoire belge. "
             "Scrutin proportionnel (les sièges sont répartis entre les listes selon leur "
             "nombre de voix, pas seulement à la liste arrivée en tête).")],
            ["SCRUTIN RÉGIONAL",
             ("élit les parlements de Région/Communauté. Vote obligatoire sur tout le territoire "
             "belge. Scrutin proportionnel, comme le scrutin fédéral.")],
            ["SCRUTIN EUROPÉEN",
             ("élit les député·e·s belges au Parlement européen. Vote obligatoire pour les "
             "personnes de 18 ans et plus. Depuis une loi du 25 décembre 2023, confirmée par un "
             "arrêt de la Cour constitutionnelle du 21 mars 2024, les jeunes de 16 et 17 ans "
             "peuvent voter à ce scrutin et y sont également soumis à l'obligation de vote.")],
            ["SCRUTIN COMMUNAL ET PROVINCIAL",
             ("élit les conseils communaux et provinciaux. Depuis le scrutin du 13 octobre 2024, "
             "le vote n'est plus obligatoire en Région flamande pour ces deux scrutins. Il "
             "reste obligatoire en Région wallonne et en Région de Bruxelles-Capitale pour ces "
             "mêmes scrutins.")],
        ],
        "note": "NOTE IMPORTANTE : ce tableau reflète la situation vérifiée à la date indiquée "
        "ci-dessus. Les règles électorales peuvent évoluer : avant toute affirmation sur un "
        "scrutin réel, vérifie la date, le scrutin précis et la région concernée auprès d'une "
        "source officielle.",
    },
)

_register(
    "Quatre bulletins fictifs à analyser",
    "87bbd470a73068bd",
    {
        "kind": "ballots",
        "notice": "Bulletins fictifs, rédigés pour cet exercice — aucune liste ni aucun "
        "candidat réel",
        "items": [
            {"number": "A", "label": "Bulletin A", "marks": [], "type": "",
             "text": "Le bulletin ne porte aucune marque, aucune case n'est remplie."},
            {"number": "B", "label": "Bulletin B", "marks": [1], "type": "",
             "text": "Une seule case est remplie, en face du nom d'une liste précise."},
            {"number": "C", "label": "Bulletin C", "marks": [2], "type": "margin",
             "text": "Une case est remplie en face d'une liste, mais l'électeur a aussi écrit un "
             "commentaire personnel dans la marge du bulletin."},
            {"number": "D", "label": "Bulletin D", "marks": [0, 2], "type": "",
             "text": "Deux cases sont remplies, chacune en face d'une liste différente."},
        ],
    },
)

_register(
    "Six extraits sourcés et datés — identifier la famille politique",
    "db2502668258080c",
    {
        "kind": "cards",
        "notice": "Extraits reformulés à partir d'une source de presse neutre et datée — "
        "référence complète dans le cours",
        "source": "Brussels Times, « A beginner's guide to Belgium's political parties », "
        "consulté le 2026-10-01",
        "intro": "Chaque extrait vise uniquement à identifier la FAMILLE politique du parti, "
        "jamais à résumer l'ensemble de son programme actuel.",
        "item_label": "Extrait",
        "items": [
            {"number": 1, "label": "Extrait 1", "title": "PS (Parti Socialiste)",
             "text": "parti francophone situé dans la famille socialiste, mettant en avant la "
             "justice sociale, la santé publique et l'éducation publique."},
            {"number": 2, "label": "Extrait 2", "title": "MR (Mouvement Réformateur)",
             "text": "parti francophone situé dans la famille libérale, mettant en avant "
             "l'initiative privée et une intervention publique plus limitée."},
            {"number": 3, "label": "Extrait 3", "title": "Ecolo",
             "text": "parti francophone situé dans la famille écologiste, mettant en avant la "
             "transition environnementale et une société plus durable."},
            {"number": 4, "label": "Extrait 4", "title": "Les Engagés",
             "text": "parti francophone situé dans la famille centriste/humaniste, issu à "
             "l'origine d'une tradition démocrate-chrétienne."},
            {"number": 5, "label": "Extrait 5", "title": "PTB (Parti du Travail de Belgique)",
             "text": "parti situé à l'extrême gauche de l'échiquier politique belge, se "
             "revendiquant d'une tradition marxiste."},
            {"number": 6, "label": "Extrait 6", "title": "Vlaams Belang",
             "text": "parti flamand situé à l'extrême droite de l'échiquier politique belge, "
             "défendant des positions nationalistes flamandes et une politique migratoire très "
             "restrictive."},
        ],
    },
)

_register(
    "Deux propositions fictives à comparer",
    "38a9cf2a835dfc8f",
    {
        "kind": "cards",
        "variant": "proposals",
        "notice": "Propositions entièrement fictives, rédigées pour cet exercice — aucun parti "
        "réel, aucune date, aucun chiffre réel",
        "item_label": "Proposition fictive",
        "items": [
            {"number": "A", "label": "Proposition fictive A", "title": "Parti imaginaire « Alpha »",
             "icon": "bi-flag", "tone": "p1",
             "text": "propose d'augmenter le financement public de services collectifs "
             "(transports, santé, enseignement), financé par une hausse des contributions des "
             "plus hauts revenus, en avançant comme priorité la réduction des inégalités entre "
             "citoyens."},
            {"number": "B", "label": "Proposition fictive B", "title": "Parti imaginaire « Beta »",
             "icon": "bi-flag", "tone": "p4",
             "text": "propose de réduire les contraintes administratives pesant sur les "
             "entreprises et de diminuer certaines contributions, en avançant comme priorité le "
             "développement de l'activité économique et de l'emploi privé."},
        ],
    },
)

# --- FSE12 -> FSE16 -----------------------------------------------------------------------

_register(
    "Tableau fictif — recettes et dépenses d'un État imaginaire (année fictive)",
    "8b020bd471f7a794",
    {
        "kind": "budget",
        "notice": "Données entièrement fictives, rédigées pour cet exercice — aucun chiffre "
        "réel",
        "sections": [
            {
                "title": "RECETTES",
                "unit": "en millions d'unités fictives",
                "rows": [
                    {"label": "Recette 1", "text": "TVA perçue sur les ventes", "amount": "400"},
                    {"label": "Recette 2", "text": "Accises perçues sur certains produits", "amount": "50"},
                    {"label": "Recette 3",
                     "text": "Impôt des personnes physiques (IPP, nommé ici uniquement comme "
                     "catégorie de recette, sans calcul ni déclaration)", "amount": "350"},
                    {"label": "Recette 4",
                     "text": "Cotisations sociales versées par les travailleurs et les "
                     "employeurs", "amount": "280"},
                    {"label": "Recette 5",
                     "text": "Revenus du patrimoine public (ex. participations de l'État)",
                     "amount": "20"},
                ],
            },
            {
                "title": "DÉPENSES",
                "unit": "en millions d'unités fictives",
                "rows": [
                    {"label": "Dépense 1", "text": "Fonctionnement des administrations publiques", "amount": "150"},
                    {"label": "Dépense 2",
                     "text": "Investissement dans des infrastructures publiques", "amount": "100"},
                    {"label": "Dépense 3",
                     "text": "Transferts vers la sécurité sociale (prestations sociales)",
                     "amount": "700"},
                    {"label": "Dépense 4", "text": "Intérêts sur la dette publique existante", "amount": "70"},
                    {"label": "Dépense 5",
                     "text": "Autres dépenses de transfert (hors sécurité sociale)", "amount": "180"},
                ],
            },
        ],
        "note": "ce tableau est une donnée fictive construite pour l'exercice ; il ne "
        "représente aucun budget réel ni aucune année réelle.",
        # Les totaux et le solde sont exactement ce que les questions demandent de calculer.
        "omitted": [("Total des recettes : 1 100. Total des dépenses : 1 200. Solde budgétaire : "
                    "-100 (déficit).")],
    },
)

_register(
    "Six situations — quel risque est couvert ?",
    "d4b75be0fb31695e",
    {
        "kind": "cards",
        "notice": "Six situations fictives, rédigées pour cet exercice — aucune personne réelle",
        "item_label": "Situation",
        "items": _numbered(
            "Situation",
            [
                ("Yasmine est en incapacité de travail pendant plusieurs semaines après une "
                "opération chirurgicale."),
                "Marc perd son emploi après la fermeture de l'entreprise qui l'employait.",
                ("Une famille reçoit chaque mois un soutien financier pour l'éducation de ses "
                "deux enfants."),
                ("Fatima atteint l'âge où elle cesse son activité professionnelle après une "
                "longue carrière."),
                "Thomas se blesse sur son lieu de travail en manipulant une machine.",
                ("Un indépendant, propriétaire de son petit commerce, cotise lui-même pour sa "
                "propre protection sociale future."),
            ],
        ),
    },
)

_register(
    "Tableau organisme / rôle — sécurité sociale belge (vérifié le 2026-10-01)",
    "845af8bfc1947b0a",
    {
        "kind": "table",
        "notice": "Tableau rédigé pour ce cours à partir de sources belges officielles vérifiées "
        "le 2026-10-01 — références dans le cours",
        "columns": ["Organisme", "Rôle", "Mission"],
        "rows": [
            ["ONSS (Office National de Sécurité Sociale)", "COLLECTEUR",
             ("perçoit la quasi-totalité des cotisations sociales dues par les employeurs et les "
             "travailleurs des secteurs public et privé.")],
            ["INAMI (Institut National d'Assurance Maladie-Invalidité)", "GESTIONNAIRE",
             ("gère les branches de l'assurance maladie et invalidité pour les travailleurs "
             "salariés.")],
            ["ONEM (Office National de l'Emploi)", "GESTIONNAIRE",
             ("met en œuvre les régimes d'assurance-chômage, d'interruption de carrière et de "
             "crédit-temps.")],
            ["SFP (Service Fédéral des Pensions)", "GESTIONNAIRE/INFORMATEUR",
             "informe et conseille les citoyens sur leur pension et gère son versement."],
            ["FEDRIS (Agence Fédérale des Risques Professionnels)", "GESTIONNAIRE",
             ("s'occupe des accidents du travail et des maladies professionnelles (contrôle, "
             "indemnisation, prévention).")],
            ["ONVA (Office National des Vacances Annuelles)", "GESTIONNAIRE/INTERMÉDIAIRE PAYEUR",
             "gère et verse le pécule de vacances des travailleurs manuels."],
            ["INASTI (Institut National d'Assurances Sociales pour Travailleurs Indépendants)",
             "GESTIONNAIRE",
             ("gère la sécurité sociale des travailleurs indépendants, de la création de leur "
             "activité jusqu'à leur retraite.")],
            ["MUTUALITÉ", "INTERMÉDIAIRE PAYEUR",
             ("verse concrètement certaines prestations (ex. remboursement de soins de santé) "
             "aux personnes affiliées, pour le compte de l'INAMI.")],
            ["FAMIWAL (Caisse publique wallonne d'allocations familiales)",
             "INTERMÉDIAIRE PAYEUR, RÉGION WALLONNE",
             ("verse les allocations familiales aux familles domiciliées en Wallonie, depuis le "
             "1er janvier 2019.")],
            ["FAMIRIS (Caisse d'allocations familiales, service d'Iriscare)",
             "INTERMÉDIAIRE PAYEUR, RÉGION DE BRUXELLES-CAPITALE",
             ("verse les allocations familiales aux familles domiciliées à Bruxelles, dans le "
             "cadre du système géré par Iriscare depuis le 1er janvier 2020.")],
        ],
        "note": "NOTE : les allocations familiales ont été régionalisées — chaque "
        "Région/Communauté organise désormais son propre système (FAMIWAL en Wallonie, "
        "Iriscare/FAMIRIS à Bruxelles, un système distinct en Flandre, non détaillé ici).",
    },
)

_register(
    "Document daté — deux pressions sur le financement (2026-10-01)",
    "373867f4fcabad2a",
    {
        "kind": "memo",
        "variant": "dossier",
        "notice": "Document rédigé pour ce cours à partir de constats généraux publics et "
        "datés — aucun chiffre réel",
        "doc_type": "Document daté",
        "meta": [{"field": "Date", "value": "2026-10-01"}],
        "paragraphs": [
            ("Deux évolutions générales pèsent sur le financement de la sécurité sociale, de "
            "façon documentée et régulièrement commentée par les institutions publiques "
            "belges :")
        ],
        "points": [
            {"title": "Le VIEILLISSEMENT DE LA POPULATION",
             "text": "un nombre croissant de personnes atteint l'âge de la retraite par rapport "
             "au nombre de personnes en activité qui cotisent, ce qui augmente les dépenses de "
             "pension tout en maintenant un nombre de cotisants relativement plus restreint."},
            {"title": "L'AUGMENTATION DES DÉPENSES DE SANTÉ",
             "text": "les progrès médicaux et le vieillissement de la population augmentent le "
             "coût global des soins remboursés par l'assurance maladie-invalidité, ce qui pèse "
             "sur le financement de cette branche."},
        ],
        "closing": "Ces deux évolutions sont des enjeux généraux, documentés par les "
        "institutions publiques belges, sans qu'un montant ou une projection chiffrée précise "
        "soit donné ici.",
    },
)

_register(
    "Schéma à compléter — circuit économique à quatre agents",
    "0a7e5a585824b9e3",
    {
        "kind": "circuit",
        "notice": "Schéma original, rédigé pour ce cours",
        "heading": "QUATRE AGENTS DU CIRCUIT ÉCONOMIQUE",
        "agents": [
            {"name": "MÉNAGES", "icon": "bi-house-heart", "tone": "p1",
             "text": "fournissent leur travail aux entreprises et reçoivent un salaire en "
             "échange. Utilisent leur revenu pour consommer des biens/services et payer des "
             "impôts/cotisations."},
            {"name": "ENTREPRISES", "icon": "bi-building", "tone": "p2",
             "text": "produisent des biens et services, versent des salaires aux ménages qui y "
             "travaillent, vendent leur production (consommation des ménages, investissements, "
             "exportations), et paient des impôts/cotisations."},
            {"name": "ÉTAT", "icon": "bi-bank", "tone": "p3",
             "text": "perçoit des impôts et des cotisations (ménages et entreprises), et "
             "effectue des dépenses : services publics (utilisés par les ménages et les "
             "entreprises) et prestations sociales (versées aux ménages, ex. allocations, "
             "pensions)."},
            {"name": "RESTE DU MONDE", "icon": "bi-globe2", "tone": "p4",
             "text": "achète des biens/services produits par les entreprises du pays "
             "(exportations) et vend des biens/services aux agents du pays (importations)."},
        ],
        "flows_title": "FLUX À COMPLÉTER DANS UN EXERCICE",
        "flows_intro": "exemples de flux réels et monétaires entre agents",
        "flows": [
            ("Ménages → Entreprises : travail (flux réel) / Entreprises → Ménages : salaires (flux "
            "monétaire)."),
            ("Ménages → Entreprises : achats de biens/services, consommation (flux monétaire et "
            "réel combinés)."),
            "Ménages/Entreprises → État : impôts et cotisations (flux monétaire).",
            ("État → Ménages : prestations sociales (flux monétaire) ; État → Ménages/Entreprises : "
            "services publics (flux réel)."),
            ("Entreprises → Reste du monde : exportations (flux réel) / Reste du monde → "
            "Entreprises : paiement des exportations (flux monétaire)."),
            ("Reste du monde → Ménages/Entreprises : importations (flux réel) / "
            "Ménages/Entreprises → Reste du monde : paiement des importations (flux monétaire)."),
        ],
    },
)

_register(
    "Exemple fictif — effet d'une aide publique sur le circuit",
    "8ebab55b3be96663",
    {
        "kind": "flow_chain",
        "notice": "Exemple fictif, rédigé pour cet exercice — aucun montant ni organisme réel",
        "case": "L'État verse une aide publique à un média local pour soutenir son "
        "fonctionnement. Le média utilise cette aide, en partie, pour verser des salaires à ses "
        "employés, qui utilisent ensuite ce revenu pour consommer et payer des "
        "impôts/cotisations.",
        "chain": [
            {"type": "node", "name": "L'État", "icon": "bi-bank", "tone": "p3"},
            {"type": "arrow", "text": "verse une aide publique"},
            {"type": "node", "name": "un média local", "icon": "bi-newspaper", "tone": "p2"},
            {"type": "arrow", "text": "verser des salaires", "detail": "en partie"},
            {"type": "node", "name": "ses employés", "icon": "bi-people", "tone": "p1"},
        ],
        "branches_from": "ses employés",
        "branches": [
            {"text": "consommer", "icon": "bi-cart"},
            {"text": "payer des impôts/cotisations", "to": "L'État", "icon": "bi-arrow-return-left"},
        ],
        # Annotations d'analyse (réponses attendues) et renvoi de cours retirés de l'écran.
        "omitted": [
            "(voir FSE02, financement des médias)",
            "Cette aide est un flux monétaire allant de l'État vers une entreprise (le média).",
            "(flux monétaire vers les ménages)",
            "(flux monétaire vers d'autres entreprises)",
            "(flux monétaire retournant vers l'État)",
        ],
    },
)

_register(
    "Proposition fictive — carte de transport collectif subventionnée",
    "9bd2887d08c965ba",
    {
        "kind": "memo",
        "variant": "proposal",
        "number": 1,
        "display_title": "Proposition — carte de transport collectif subventionnée",
        "notice": "Proposition entièrement fictive, rédigée pour cet exercice — aucun montant, "
        "aucun organisme réel",
        "org": "Gouvernement régional",
        "doc_type": "Proposition",
        "paragraphs": [
            ("Un gouvernement régional fictif propose de subventionner une partie du prix des "
            "abonnements de transport collectif (bus, train régional) pour les travailleurs à "
            "revenus modestes, financée par le budget régional. L'objectif affiché est de "
            "faciliter l'accès à l'emploi et de réduire l'usage de la voiture individuelle "
            "pour les trajets domicile-travail.")
        ],
    },
)

_register(
    "Note budgétaire fictive accompagnant la proposition",
    "9a76d9817f854274",
    {
        "kind": "memo",
        "variant": "budget-note",
        "number": 2,
        "display_title": "Note budgétaire accompagnant la proposition",
        "notice": "Document fictif, rédigé pour cet exercice — aucun montant réel",
        "doc_type": "Note budgétaire",
        "paragraphs": [
            ("La subvention serait financée par une partie du budget régional existant. À "
            "court terme, la dépense régionale augmente. À moyen terme, la note budgétaire "
            "évoque un effet indirect possible : si davantage de travailleurs à revenus "
            "modestes accèdent plus facilement à un emploi grâce au transport subventionné, "
            "les recettes fiscales et parafiscales de cet emploi pourraient partiellement "
            "compenser la dépense initiale — un effet incertain, présenté comme une "
            "hypothèse, pas un résultat garanti."),
        ],
        "omitted": ["(compétence territoriale, voir FSE09)", "(vues en FSE12-13)"],
    },
)

_register(
    "Réactions fictives de trois groupes concernés",
    "597a07ff14489b15",
    {
        "kind": "quotes",
        "number": 3,
        "display_title": "Réactions des groupes concernés",
        "notice": "Témoignages fictifs — exercice pédagogique",
        "items": [
            {"actor": "Un ménage concerné", "icon": "bi-house-heart", "tone": "p1",
             "text": "« Cette aide me permettrait d'accepter un emploi plus loin de chez moi, que "
             "je refusais jusqu'ici à cause du coût du transport. »"},
            {"actor": "Une entreprise de transport collectif", "icon": "bi-bus-front", "tone": "p2",
             "text": "« Nous nous attendons à une hausse de la fréquentation, mais aussi à des "
             "coûts supplémentaires pour augmenter la capacité de nos lignes les plus "
             "demandées. »"},
            {"actor": "Une association de défense de l'environnement", "icon": "bi-tree", "tone": "p3",
             "text": "« Nous saluons l'effet attendu de réduction de l'usage de la voiture "
             "individuelle, mais rappelons que cet effet dépendra de la capacité réelle du "
             "réseau à absorber la demande supplémentaire — un effet incertain à court terme, "
             "qui pourrait ne se concrétiser qu'à plus long terme si le réseau est renforcé en "
             "conséquence. »"},
        ],
    },
)


# =========================================================================================
# Résolution
# =========================================================================================


def registered_layouts() -> dict[tuple[str, str], dict[str, Any]]:
    return dict(_REGISTRY)


def resolve_layout(document: Any) -> dict[str, Any] | None:
    """Mise en page d'une `SourceDocumentVersion` (ou de tout objet ayant `title`,
    `content_text`, `content_json`), ou `None` → rendu générique.

    1. `content_json["layout"]` : document créé directement sous forme structurée ;
    2. registre : titre exact ET empreinte du texte exact de CETTE version."""
    content_json = getattr(document, "content_json", None)
    if isinstance(content_json, dict) and isinstance(content_json.get("layout"), dict):
        return content_json["layout"]
    title = getattr(document, "title", None) or ""
    return _REGISTRY.get((title, text_fingerprint(getattr(document, "content_text", None))))


_LEADING_NOTE = re.compile(r"^\s*\[([^\[\]]{3,600})\]\s*\n", re.DOTALL)
_TRAILING_NUMBER = re.compile(r"^Document\s+(\d+|[A-Z])\s+—\s+(.+)$")


def generic_parts(text: str | None) -> dict[str, Any]:
    """Rendu générique (aucune mise en page dédiée) : paragraphes lisibles, mention
    éditoriale initiale entre crochets sortie du corps comme note discrète. Les autres
    crochets (citation, notation) sont conservés tels quels — jamais supprimés à l'aveugle."""
    text = text or ""
    notice = None
    match = _LEADING_NOTE.match(text)
    if match:
        notice = match.group(1).strip()
        text = text[match.end():]
    paragraphs = [re.sub(r"[ \t]*\n[ \t]*", "\n", block).strip() for block in re.split(r"\n\s*\n", text)]
    # `text` : texte exact (hors mention initiale), affiché en `pre-line` — paragraphes et
    # retours à la ligne respectés, rien de reformulé.
    return {"notice": notice, "text": text.lstrip("\n") if notice else text, "paragraphs": [p for p in paragraphs if p]}


def display_heading(document: Any, layout: dict[str, Any] | None, fallback_label: str) -> dict[str, str]:
    """Libellé + titre affichés. Réutilise un numéro réel (« Document 3 ») quand le
    document en porte un — dans son titre ou dans sa mise en page (consignes « d'après le
    document 3 ») — jamais une numérotation inventée."""
    title = getattr(document, "title", None) or "Document source"
    if layout and layout.get("display_title"):
        title = layout["display_title"]
    number = layout.get("number") if layout else None
    match = _TRAILING_NUMBER.match(title)
    if match and number is None:
        return {"label": f"Document {match.group(1)}", "title": match.group(2)}
    if number is not None:
        return {"label": f"Document {number}", "title": title}
    return {"label": fallback_label, "title": title}


def focus_numbers(layout: dict[str, Any] | None, question_text: str | None) -> list:
    """Numéros des fiches explicitement visées par la question (« situation 5 », « extrait
    3 », « Situation 6 (…) » dans les éléments à classer). Vide si la question porte sur
    tout le dossier ou si la mise en page n'a pas de fiches numérotées."""
    if not layout or layout.get("kind") != "cards" or not question_text:
        return []
    label = (layout.get("item_label") or "").split(" ")[0].lower()
    pattern = _FOCUS_WORDS.get(label)
    if not pattern:
        return []
    found: list = []
    for match in re.finditer(rf"\b{pattern}\s+(\d+)\b", question_text, re.IGNORECASE):
        value = int(match.group(1))
        if value not in found:
            found.append(value)
    numbers = [item.get("number") for item in layout.get("items", [])]
    found = [value for value in found if value in numbers]
    if not found or len(found) >= len(numbers):
        return []
    return found


def course_card_html(ref: str) -> str:
    """Composition déjà validée dans le cours, réutilisée telle quelle (même affiche en
    Cours et en session). Liste blanche : jamais un nom arbitraire venu des données."""
    if ref == "FSE01_AFFICHE_CARD_HTML":
        from app.v1.fse01_content import FSE01_AFFICHE_CARD_HTML

        return FSE01_AFFICHE_CARD_HTML
    return ""
