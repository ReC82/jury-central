"""EX04 « Examen blanc écrit — réseau, configuration et dépannage » — page du sujet, version
candidat (ticket #233).

Même modèle que EX01 (#230), EX02 (#231) et EX03 (#232) : la page « Sujet » de l'UAA EX04 présente
l'épreuve (consignes, barème global, exigences évaluées) et le **sujet complet sans corrigé** :
partie 1, dossiers A, B et C avec leurs documents et schémas, puis les dix questions numérotées.
À l'impression (A4), chaque question reçoit des lignes de réponse et chaque dossier commence sur
une nouvelle page. Barèmes détaillés et corrigés n'apparaissent qu'après la remise de la session
« Examen blanc ».

Les titres de blocs évitent les mots qui changent le type de carte (`app.card_kind`) sauf
« Méthode » et « Sources », voulus. Questions et documents : `app.v1.ampcr_pratique_ex04_bank`
(même source que la banque des sessions) ; schémas : `app.v1.ampcr_pratique_ex04_figures`.
Aucun schéma de rappel sur cette page : tableaux de couches, d'adresses ou de diagnostic des
cours donneraient les réponses ; on les revoit dans PR18 → PR25 (liens « À revoir » du barème).
"""

from html import escape

from app.v1.ampcr_pratique_ex04_bank import (
    DOSSIER_A,
    DOSSIER_B,
    DOSSIER_C,
    DOSSIER_DOCUMENTS,
    EXAM_ITEMS,
    EXAM_TOTAL_POINTS,
    ITEM_COURSES,
    ITEM_PARTS,
    PART_1,
)
from app.v1.ampcr_pratique_ex04_figures import STATIC_FIGURES
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import EXERCISE_SLOTS_BY_CODE
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr06_course import _document_html, _fig, _req

EX04_TITLE = "Examen blanc écrit — réseau, configuration et dépannage"
EX04_SLUG = "ampcr-pratique-ex04"
EXAM_URL = f"/uaa/{EX04_SLUG}/exam"
ANSWER_LINES = 12  # lignes de réponse par question dans la version imprimée

_FIGURES_BY_FILE = {path: figure for figure, path in STATIC_FIGURES}


def _number(item: PR06Item) -> int:
    return EXAM_ITEMS.index(item) + 1


def _course_links(codes: tuple[str, ...]) -> str:
    return ", ".join(f"[{code}](/uaa/ampcr-pratique-{code.lower()})" for code in codes)


def _doc_html(document: ExerciseDocument) -> str:
    """Document d'un dossier : un schéma est dessiné en SVG (même dessin que le fichier
    affiché dans la question) ; les autres réutilisent la mise en forme des cours."""
    if document.image:
        figure = _FIGURES_BY_FILE[document.image]
        return f'<div class="jc-pr-doc"><p class="jc-pr-doc-title">{escape(document.title)}</p>{_fig(figure).strip()}</div>'
    return _document_html(document)


def _question_html(item: PR06Item) -> str:
    instructions = "".join(f"<li>{escape(text)}</li>" for text in item.instructions)
    lines = "".join('<div class="jc-ex-answer-line"></div>' for _ in range(ANSWER_LINES))
    return (
        f'<div class="jc-ex-question" id="ex04-q{_number(item)}">'
        f'<p class="jc-ex-question-head"><span>Question {_number(item)} — {escape(item.title)}</span>'
        f"<span>{item.total_points:g} points</span></p>"
        f"<p>{escape(item.context)}</p><ol>{instructions}</ol>"
        f'<div class="jc-ex-answer" aria-hidden="true"><p class="small mb-1">Ta réponse :</p>{lines}</div>'
        "</div>"
    )


def _part(part: str, intro: str, *, dossier: bool) -> str:
    """Documents puis questions d'une partie. Un document n'apparaît que juste avant la
    première question qui l'utilise (il n'est pas répété ensuite)."""
    shown: set[str] = set()
    parts = (['<div class="jc-ex-dossier"></div>'] if dossier else []) + [intro]
    for item in (i for i in EXAM_ITEMS if ITEM_PARTS[i.key] == part):
        new_docs = [d for d in item.documents if d.title not in shown]
        if new_docs:
            parts.append(f"## Documents pour la question {_number(item)}")
            parts += [_doc_html(d) for d in new_docs]
            shown.update(d.title for d in new_docs)
        parts.append(_question_html(item))
    if dossier:
        assert shown == {d.title for d in DOSSIER_DOCUMENTS[part]}
    return "\n\n".join(parts) + "\n"


def _score_table() -> str:
    rows = "\n".join(
        f"| {_number(item)} | {item.title} | {ITEM_PARTS[item.key].split(' — ')[0]} | "
        f"{item.total_points:g} | {', '.join(item.requirement_ids)} | {_course_links(ITEM_COURSES[item.key])} |"
        for item in EXAM_ITEMS
    )
    return (
        "| N° | Question | Partie | Points | Exigences | À revoir |\n|---|---|---|---|---|---|\n"
        + rows
        + f"\n| — | **Total** | — | **{EXAM_TOTAL_POINTS}** | — | — |"
    )


def _presentation() -> str:
    slot = EXERCISE_SLOTS_BY_CODE["EX04"]
    reqs = "\n".join(_req(r) for r in slot.requirement_ids)
    return f"""## Ce que cet examen blanc évalue

Le quatrième examen blanc du parcours **Pratique écrite** porte sur tout le **module 4 —
réseau** : installation physique d'un mini-réseau (PR18), topologies, modèles OSI et TCP/IP,
NetBEUI et équipements (PR19), adressage IPv4, masques, MAC et passerelles (PR20), connexion
directe de deux PC et mini-réseau (PR21), domaine, groupe de travail et comptes (PR22), partage de
dossiers, d'imprimantes et permissions (PR23), dépannage réseau et Internet (PR24) et Wi-Fi
(PR25). Il reproduit une **logique d'intervention écrite** : un plan de réseau et des calculs
d'adresses, puis **trois dossiers** de clients avec fiches, relevés `ipconfig`, `ip addr`,
`ip route`, `ping`, `tracert`, `nslookup`, journal DHCP, fiche d'un point d'accès, mesures
Wi-Fi et autorisations, sur lesquels tu rédiges diagnostic, configuration, procédure,
vérification et rapport.

C'est un **entraînement Jury Central**, pas un sujet officiel ni une question déjà posée par le
Jury : les entreprises, les personnes, les adresses et les mesures sont **fictives** (adresses
publiques des plages de documentation).

## Organisation et notation

- **10 questions à réponse rédigée**, **10 points chacune** : note sur **{EXAM_TOTAL_POINTS}**
  (ramenée aussi sur 20 sur la page de résultat, à titre de repère).
- Chaque question donne **toutes les informations nécessaires** ; elle reprend dans la session
  les documents de son dossier, dans l'ordre où le moteur te la présente.
- **Barème analytique** : chaque question est notée sur des critères explicites (lecture des
  relevés, calculs exacts, configuration complète, procédure dans l'ordre, justification,
  vérification). Toute formulation et toute méthode justes sont acceptées (calcul binaire ou par
  taille de bloc, écran ou ligne de commande), aucun mot-clé n'est exigé ; confondre une panne de
  connectivité IP et une panne DNS, ou proposer une correction qui casse autre chose, fait perdre
  des points.
- Le **barème détaillé et le corrigé** de chaque question ne sont visibles **qu'après la remise**
  de ta copie.
- **Calculatrice** utile pour les questions 2 et 8 (adresses, signal et débit).
- **Durée conseillée pour t'entraîner** : environ 2 heures 30. C'est un repère personnel, **pas
  la durée officielle** de l'épreuve (voir les consignes officielles).

## Comment passer l'examen

1. Lis le sujet sur cette page (ou imprime-le) : partie 1, puis dossiers A, B et C.
2. Ouvre l'onglet **[Examen blanc]({EXAM_URL})** (connexion nécessaire) et démarre la session :
   les 10 questions s'affichent une à une, avec leurs documents.
3. Rédige tes réponses : elles sont **enregistrées automatiquement** et tu peux reprendre plus
   tard là où tu t'es arrêté.
4. Remets ta copie : la correction suit le barème de chaque question, puis tu vois ta note, le
   corrigé et les points à revoir.

**Version papier** : imprime cette page (Ctrl + P, format A4). Le sujet s'imprime complet, sans
corrigé, avec des lignes de réponse sous chaque question et chaque dossier sur une nouvelle page.

## Barème global

{_score_table()}

## Exigences des consignes officielles évaluées

{reqs}

Une exigence n'est jamais déclarée « validée » par cet examen seul : voir la
[matrice de couverture](/ampcr-pratique/matrice).
"""


def _part1() -> str:
    return _part(
        PART_1,
        "Deux questions sans dossier : lire le plan d'un réseau (topologie, équipements, domaines, trames), puis "
        "calculer des réseaux IPv4 et identifier des adresses MAC et IP.",
        dossier=False,
    )


def _dossier_a() -> str:
    return _part(
        DOSSIER_A,
        "Le cabinet de kinésithérapie Kiné Sambre relie d'abord deux postes par un seul câble, puis installe un "
        "mini-réseau de cinq postes et une imprimante derrière une box. Tu dépannes la connexion directe et tu "
        "corriges le plan d'adressage.",
        dossier=True,
    )


def _dossier_b() -> str:
    return _part(
        DOSSIER_B,
        "L'agence immobilière Immo Meuse a un serveur Linux qui distribue les adresses et résout les noms. Dans la "
        "même semaine : un poste sans noms, un poste sans route, un portable sans adresse, puis une panne Internet "
        "de toute l'agence, avec un rapport pour le gérant.",
        dossier=True,
    )


def _dossier_c() -> str:
    return _part(
        DOSSIER_C,
        "Le bureau d'architectes Atelier Linéa veut un Wi-Fi sûr et rapide jusque dans la salle de dessin, des "
        "droits justes sur son serveur de fichiers, et retrouver son traceur et ses lecteurs réseau après le "
        "remplacement de la box.",
        dossier=True,
    )


def _method() -> str:
    return """## Répondre à un dossier réseau écrit

1. **Lis toute la question, puis les documents** : relève adresses, masques, passerelles, DNS,
   messages exacts des commandes, étendue DHCP, conventions du client.
2. **Calcule et montre le calcul** : réseau, diffusion, plage et nombre d'hôtes ; signal et débit ;
   compare à la règle et conclus.
3. **Diagnostique de bas en haut** : lien, adresse, passerelle, Internet par adresse IP, puis
   noms (DNS), puis service ou droits ; chaque relevé prouve ou exclut quelque chose : dis-le.
4. **Lis le message exact** : une demande sans réponse, une adresse où personne ne répond, une
   absence de route et un nom introuvable ne mènent pas à la même panne.
5. **Corrige le minimum, durablement** : la valeur fautive, au bon endroit (poste, box, serveur),
   sans casser le reste ; donne la configuration complète.
6. **Termine par la vérification et la trace** : test qui prouve que c'est réglé, plan
   d'adressage ou rapport mis à jour, utilisateur informé.

**Pièges qui coûtent des points** : accuser le DNS alors qu'une adresse IP ne répond pas (ou
l'inverse), oublier la passerelle, fixer une adresse dans l'étendue DHCP, confondre partage et
NTFS, croire qu'un SSID masqué protège, placer un répéteur là où il reçoit mal.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, topologies,
  protocoles, adressage IP et MAC, équipements, connexion directe, mini-réseau, partages et
  droits, pannes Internet, Wi-Fi. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Matière** : cours PR18 à PR25 du parcours (mêmes règles : domaines de collision et de
  diffusion, calculs IPv4, bits I/G et U/L, Auto MDI-X, plan d'adressage, lecture des relevés,
  étendue DHCP, accès effectif partage + NTFS, sécurité Wi-Fi, canaux, répéteur).
- **Normes et documents publics** cités par les cours : ISO/IEC 7498-1 (OSI), RFC 1122 (TCP/IP),
  RFC 1918 (adresses privées), RFC 3927 (APIPA), RFC 5737 (adresses de documentation),
  IEEE 802.3 (Ethernet) et IEEE 802.11 (Wi-Fi).

## Supports fictifs

Le plan du réseau, le mini-réseau du cabinet et le plan Wi-Fi sont **produits par programme**
depuis des données vérifiées par des tests automatiques ; les relevés de commandes sont des
**captures fictives simplifiées** au format réel. Aucun n'est tiré d'une image générée ni d'une
copie d'écran réelle, et aucun schéma ne donne de verdict. Entreprises, personnes, adresses et
mesures sont **fictives**. Aucune question n'est un sujet officiel ou une question déjà posée
par le Jury.
"""


def ex04_course_sections() -> list[tuple[str, str]]:
    """Blocs de la page du sujet (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("EX04 — Présentation, consignes et barème", _presentation()),
        ("EX04 — Partie 1 : plan de réseau et adressage (questions 1 et 2)", _part1()),
        ("EX04 — Dossier A : cabinet Kiné Sambre (questions 3 et 4)", _dossier_a()),
        ("EX04 — Dossier B : agence Immo Meuse (questions 5 à 7)", _dossier_b()),
        ("EX04 — Dossier C : bureau d'architectes Atelier Linéa (questions 8 à 10)", _dossier_c()),
        ("EX04 — Méthode : répondre à un dossier réseau écrit", _method()),
        ("EX04 — Sources et supports fictifs", _sources()),
    ]
