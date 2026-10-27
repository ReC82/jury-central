"""EX05 « Examen blanc global standard — épreuve pratique écrite » — page du sujet, version
candidat (ticket #201).

Même modèle que EX01 → EX04 : la page « Sujet » de l'UAA EX05 présente l'épreuve (consignes,
répartition des points, barème global, exigences évaluées et non évaluées) puis le **sujet
complet sans corrigé**, pour chacune des **deux variantes** du dossier : documents communs
(fiche du client, schéma du réseau, inventaire, journal des pannes), puis les dix situations
numérotées avec leurs documents propres. À l'impression (A4), chaque question reçoit des lignes
de réponse et chaque variante commence sur une nouvelle page. Barèmes détaillés et corrigés
n'apparaissent qu'après la remise de la session « Examen blanc », qui sert une variante entière
(`app.v1.ampcr_pratique_bank.select_exam_variant`).

Les titres de blocs évitent les mots qui changent le type de carte (`app.card_kind`) sauf
« Méthode » et « Sources », voulus. Questions et documents : `app.v1.ampcr_pratique_ex05_bank`
(même source que la banque des sessions) ; schémas : `app.v1.ampcr_pratique_ex05_figures`.
"""

from html import escape

from app.v1.ampcr_pratique_ex05_bank import (
    DOMAINS,
    EXAM_TOTAL_POINTS,
    SITUATION_COURSES,
    VARIANT_DOCS,
    VARIANT_ITEMS,
    situation_of,
)
from app.v1.ampcr_pratique_ex05_figures import STATIC_FIGURES, VARIANTS, Variant
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import EXERCISE_SLOTS_BY_CODE, OFFICIAL_REQUIREMENTS
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr06_course import _document_html, _fig, _req

EX05_TITLE = "Examen blanc global standard — épreuve pratique écrite"
EX05_SLUG = "ampcr-pratique-ex05"
EXAM_URL = f"/uaa/{EX05_SLUG}/exam"
ANSWER_LINES = 12  # lignes de réponse par question dans la version imprimée
SUGGESTED_DURATION = "3 heures"

_FIGURES_BY_FILE = {path: figure for figure, path in STATIC_FIGURES}


def evaluated_requirements() -> tuple[str, ...]:
    """Exigences réellement évaluées par les questions (identiques dans les deux variantes)."""
    ids: list[str] = []
    for item in VARIANT_ITEMS[1]:
        ids += [r for r in item.requirement_ids if r not in ids]
    return tuple(ids)


def missing_official_requirements() -> tuple[str, ...]:
    """Exigences officielles AP-01 → AP-38 que cet examen blanc n'évalue pas (manques
    explicités, traités par EX01 → EX04 et les cours)."""
    evaluated = set(evaluated_requirements())
    return tuple(r.id for r in OFFICIAL_REQUIREMENTS if r.id not in evaluated)


def _course_links(codes: tuple[str, ...]) -> str:
    return ", ".join(f"[{code}](/uaa/ampcr-pratique-{code.lower()})" for code in codes)


def _doc_html(document: ExerciseDocument) -> str:
    if document.image:
        figure = _FIGURES_BY_FILE[document.image]
        return (f'<div class="jc-pr-doc"><p class="jc-pr-doc-title">{escape(document.title)}</p>'
                f"{_fig(figure).strip()}</div>")
    return _document_html(document)


def _question_html(v: Variant, item: PR06Item) -> str:
    number = situation_of(item)
    instructions = "".join(f"<li>{escape(text)}</li>" for text in item.instructions)
    lines = "".join('<div class="jc-ex-answer-line"></div>' for _ in range(ANSWER_LINES))
    return (
        f'<div class="jc-ex-question" id="ex05-v{v.number}-q{number}">'
        f'<p class="jc-ex-question-head"><span>Question {number} — {escape(item.title)}</span>'
        f"<span>{item.total_points:g} points</span></p>"
        f"<p>{escape(item.context)}</p><ol>{instructions}</ol>"
        f'<div class="jc-ex-answer" aria-hidden="true"><p class="small mb-1">Ta réponse :</p>{lines}</div>'
        "</div>"
    )


def _common_documents(v: Variant) -> tuple[ExerciseDocument, ...]:
    d = VARIANT_DOCS[v.number]
    return (d.client, d.schema, d.inventory, d.journal)


def _dossier(v: Variant) -> str:
    docs = "\n\n".join(_doc_html(doc) for doc in _common_documents(v))
    return (
        '<div class="jc-ex-dossier"></div>\n\n'
        f"{v.company}, {v.activity} à {v.city}, confie la maintenance de ses 6 postes à ton entreprise. "
        f"Tu interviens le {v.date}. Les quatre documents ci-dessous servent à plusieurs questions ; "
        "chaque question donne ensuite ses documents propres.\n\n"
        f"{docs}\n"
    )


def _questions(v: Variant, numbers: range) -> str:
    common = {d.title for d in _common_documents(v)}
    shown: set[str] = set(common)
    parts = []
    for item in VARIANT_ITEMS[v.number]:
        number = situation_of(item)
        if number not in numbers:
            continue
        new_docs = [d for d in item.documents if d.title not in shown]
        if new_docs:
            parts.append(f"## Documents pour la question {number}")
            parts += [_doc_html(d) for d in new_docs]
            shown.update(d.title for d in new_docs)
        parts.append(_question_html(v, item))
    return "\n\n".join(parts) + "\n"


def _score_table() -> str:
    rows = []
    for item in VARIANT_ITEMS[1]:
        number = situation_of(item)
        domain = next(name for name, nums in DOMAINS if number in nums)
        rows.append(f"| {number} | {item.title} | {domain} | {item.total_points:g} | "
                    f"{', '.join(item.requirement_ids)} | {_course_links(SITUATION_COURSES[number])} |")
    return (
        "| N° | Situation | Domaine | Points | Exigences | À revoir |\n|---|---|---|---|---|---|\n"
        + "\n".join(rows)
        + f"\n| — | **Total** | — | **{EXAM_TOTAL_POINTS}** | — | — |"
    )


def _domains() -> str:
    return "\n".join(
        f"- **{name}** : questions {', '.join(str(n) for n in nums)} — **{10 * len(nums)} points**"
        for name, nums in DOMAINS
    )


def _presentation() -> str:
    slot = EXERCISE_SLOTS_BY_CODE["EX05"]
    evaluated = evaluated_requirements()
    reqs = "\n".join(_req(r) for r in evaluated)
    missing = ", ".join(missing_official_requirements())
    extra = [r for r in evaluated if r not in slot.requirement_ids]
    extra_text = f" ; en plus : {', '.join(extra)}" if extra else ""
    companies = " et ".join(f"**{v.label}** : {v.company} ({v.city})" for v in VARIANTS)
    return f"""## Ce que cet examen blanc évalue

Cet examen blanc **global** porte sur **tout le parcours Pratique écrite** (cours PR01 à PR30).
Il reproduit une **intervention écrite complète** chez un client : une petite entreprise de
**6 postes** dont tu reçois le dossier — fiche du client, **schéma du réseau local**,
**inventaire du matériel**, **journal des pannes** — puis des relevés et des mesures (Gestionnaire
des tâches, SMART, micrologiciel, vérification d'une image Linux, testeur de câble, segment
coaxial, table ARP, partages et NTFS, `ipconfig`, `ping`, `nslookup`, journal d'intervention).
Tu y rédiges diagnostics, procédures, configurations, vérifications et un rapport.

C'est un **entraînement Jury Central**, pas un sujet officiel ni une question déjà posée par le
Jury : entreprises, personnes, adresses et mesures sont **fictives** (adresses publiques des plages
de documentation).

## Deux variantes du même dossier

Le dossier existe en **deux variantes** : {companies}. Même structure, mêmes
situations et même barème, mais **données différentes** (adresses, pannes, mesures, réglages) :
la réponse juste n'est pas la même. Chaque valeur a été recalculée par programme avec les règles
des cours. La session « Examen blanc » te donne **une variante entière** : la variante 1 la
première fois, puis la variante 2, puis celle que tu as le moins faite. Les deux sujets sont
imprimables ci-dessous.

## Organisation et notation

- **10 situations à réponse rédigée**, **10 points chacune** : note sur **{EXAM_TOTAL_POINTS}**
  (ramenée aussi sur 20 sur la page de résultat, à titre de repère). Répartition :

{_domains()}

- Chaque question donne **le contexte, les documents, les données, des consignes numérotées et
  ses points** ; elle se résout seule, dans n'importe quel ordre.
- **Barème analytique** : chaque question est notée sur 4 critères explicites (lecture des
  relevés, diagnostic, procédure, vérification, justification). Toute formulation et toute méthode
  justes sont acceptées, aucun mot-clé n'est exigé ; une action dangereuse ou destructive sans
  sauvegarde ni accord fait perdre des points.
- Le **barème détaillé et le corrigé** de chaque question ne sont visibles **qu'après la remise**
  de ta copie.
- **Calculatrice** utile pour les questions 7 (adressage) et 6 (résistances).
- **Durée conseillée pour t'entraîner** : environ {SUGGESTED_DURATION}. C'est un repère
  personnel, **pas la durée officielle** de l'épreuve (voir les consignes officielles).

## Comment passer l'examen

1. Lis le sujet de ta variante sur cette page (ou imprime-le) : dossier, puis questions 1 à 10.
2. Ouvre l'onglet **[Examen blanc]({EXAM_URL})** (connexion nécessaire) et démarre la session :
   les 10 questions s'affichent une à une, dans l'ordre du sujet, avec leurs documents.
3. Rédige tes réponses : elles sont **enregistrées automatiquement** et tu peux reprendre plus
   tard là où tu t'es arrêté.
4. Remets ta copie : la correction suit le barème de chaque question, puis tu vois ta note, le
   corrigé et les cours à revoir. Le bouton « Imprimer / PDF » de la page de résultat enregistre
   ta copie corrigée en PDF.

**Version papier** : imprime cette page (Ctrl + P, format A4). Les deux sujets s'impriment
complets, sans corrigé, avec des lignes de réponse sous chaque question et chaque variante sur
une nouvelle page.

## Barème global (identique pour les deux variantes)

{_score_table()}

## Exigences des consignes officielles évaluées

{reqs}

Exigences prévues pour EX05 dans le plan : {', '.join(slot.requirement_ids)}{extra_text}.

**Non évaluées dans cet examen blanc** (manques explicités) : {missing}. Elles sont évaluées dans
les examens blancs de module EX01 → EX04 et dans les cours. Une exigence n'est jamais déclarée
« validée » par cet examen seul : voir la [matrice de couverture](/ampcr-pratique/matrice).
"""


def _method() -> str:
    return """## Répondre à un dossier d'intervention global

1. **Lis la question, puis les documents qu'elle cite** : relève les valeurs exactes (compteurs,
   adresses, longueurs, mesures, messages) et ce que demande le client.
2. **Compare à la règle et calcule** : seuils SMART, prérequis de Windows 11, swap, longueurs de
   câble, résistance d'un segment coaxial, réseau et diffusion, accès effectif.
3. **Conclus en citant la valeur qui fonde ta conclusion** : « 24 secteurs en attente > 0, donc… ».
4. **Protège avant d'agir** : données sauvegardées et accord du client, poste hors tension,
   bracelet antistatique.
5. **Décris l'intervention dans l'ordre**, au bon endroit, sans casser autre chose.
6. **Termine par la vérification et la trace** : test qui prouve le résultat, rapport, client
   informé.

**Pièges qui coûtent des points** : réparer avant de sauvegarder, changer une pièce qui n'est pas
en cause, désactiver une sécurité pour « faire passer » une installation, accuser le DNS quand une
adresse IP ne répond pas (ou l'inverse), corriger les droits d'une personne au lieu de son groupe,
oublier la mesure de contrôle finale.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, Laboratoire et T.P. et
  méthodes évalués ensemble. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Matière** : cours PR01 à PR30 du parcours (mêmes règles : composants et mémoire, SMART,
  prérequis de Windows 11 et activation, sha256sum et swap, T568B et testeur, longueurs de canal,
  10BASE2 et BNC, calculs IPv4 et ARP, partage + NTFS, dépannage réseau, rapport d'intervention).
- **Documents publics** cités par les cours : configuration requise de Windows 11 (Microsoft),
  documentation d'installation d'Ubuntu, ANSI/TIA-568 (brochage et longueurs), IEEE 802.3
  (Ethernet, 10BASE2, 1000BASE-T), RFC 1918 et RFC 5737 (adresses).

## Supports fictifs

Les schémas des réseaux sont **produits par programme** depuis des données vérifiées par des tests
automatiques ; les relevés et captures sont **fictifs et simplifiés**, au format réel. Aucun n'est
tiré d'une image générée ni d'une copie d'écran réelle, et aucun schéma ne donne de verdict.
Entreprises, personnes, adresses et mesures sont **fictives**. Aucune question n'est un sujet
officiel ou une question déjà posée par le Jury.
"""


def ex05_course_sections() -> list[tuple[str, str]]:
    """Blocs de la page du sujet (titre, contenu), dans l'ordre d'affichage."""
    sections = [("EX05 — Présentation, consignes et barème", _presentation())]
    for v in VARIANTS:
        sections += [
            (f"EX05 — {v.label} : dossier {v.company}", _dossier(v)),
            (f"EX05 — {v.label} : questions 1 à 5", _questions(v, range(1, 6))),
            (f"EX05 — {v.label} : questions 6 à 10", _questions(v, range(6, 11))),
        ]
    sections += [
        ("EX05 — Méthode : répondre à un dossier d'intervention global", _method()),
        ("EX05 — Sources et supports fictifs", _sources()),
    ]
    return sections
