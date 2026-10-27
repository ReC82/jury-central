"""EX06 « Examen blanc global avancé — dossiers complexes » — page du sujet, version candidat
(ticket #234).

Même modèle que EX05 : la page « Sujet » de l'UAA EX06 présente l'épreuve (consignes,
répartition des points par dossier, barème global, comparaison de couverture avec EX05,
exigences évaluées et non évaluées) puis le **sujet complet sans corrigé** de chacune des
**deux variantes** : documents communs (fiche du client, schéma du réseau, inventaire), puis les
quatre dossiers A à D avec leurs documents et leurs questions numérotées. À l'impression (A4),
chaque question reçoit des lignes de réponse et chaque variante commence sur une nouvelle page.
Barèmes détaillés et corrigés n'apparaissent qu'après la remise de la session « Examen blanc »,
qui sert une variante entière (`app.v1.ampcr_pratique_bank.select_exam_variant`).

Les titres de blocs évitent les mots qui changent le type de carte (`app.card_kind`) sauf
« Méthode » et « Sources », voulus. Questions et documents : `app.v1.ampcr_pratique_ex06_bank` ;
schémas : `app.v1.ampcr_pratique_ex06_figures`.
"""

from html import escape

from app.v1.ampcr_pratique_ex05_course import evaluated_requirements as ex05_requirements
from app.v1.ampcr_pratique_ex06_bank import (
    DOSSIERS,
    EX05_COMPARISON,
    EXAM_TOTAL_POINTS,
    SITUATION_COURSES,
    SITUATION_POINTS,
    VARIANT_DOCS,
    VARIANT_ITEMS,
    dossier_of,
    situation_of,
)
from app.v1.ampcr_pratique_ex06_figures import STATIC_FIGURES, VARIANTS, Variant
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import EXERCISE_SLOTS_BY_CODE, OFFICIAL_REQUIREMENTS
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr06_course import _document_html, _fig, _req

EX06_TITLE = "Examen blanc global avancé — dossiers complexes"
EX06_SLUG = "ampcr-pratique-ex06"
EXAM_URL = f"/uaa/{EX06_SLUG}/exam"
ANSWER_LINES = 12  # lignes de réponse par question dans la version imprimée
SUGGESTED_DURATION = "4 heures"

_FIGURES_BY_FILE = {path: figure for figure, path in STATIC_FIGURES}


def evaluated_requirements() -> tuple[str, ...]:
    """Exigences réellement évaluées par les questions (identiques dans les deux variantes)."""
    ids: list[str] = []
    for item in VARIANT_ITEMS[1]:
        ids += [r for r in item.requirement_ids if r not in ids]
    return tuple(ids)


def missing_official_requirements() -> tuple[str, ...]:
    """Exigences officielles AP-01 → AP-38 que cet examen blanc n'évalue pas (manques
    explicités, traités par EX01 → EX05 et les cours)."""
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
        f'<div class="jc-ex-question" id="ex06-v{v.number}-q{number}">'
        f'<p class="jc-ex-question-head"><span>Question {number} — {escape(item.title)}</span>'
        f"<span>{item.total_points:g} points</span></p>"
        f"<p>{escape(item.context)}</p><ol>{instructions}</ol>"
        f'<div class="jc-ex-answer" aria-hidden="true"><p class="small mb-1">Ta réponse :</p>{lines}</div>'
        "</div>"
    )


def _common_documents(v: Variant) -> tuple[ExerciseDocument, ...]:
    d = VARIANT_DOCS[v.number]
    return (d.client, d.schema, d.inventory)


def _common(v: Variant) -> str:
    docs = "\n\n".join(_doc_html(doc) for doc in _common_documents(v))
    return (
        '<div class="jc-ex-dossier"></div>\n\n'
        f"{v.company}, {v.activity} à {v.city} ({v.staff} personnes), confie à ton entreprise une journée de "
        f"maintenance le {v.date}. Quatre dossiers sont ouverts (A à D). Les trois documents ci-dessous servent à "
        "plusieurs questions ; chaque dossier donne ensuite ses documents propres.\n\n"
        f"{docs}\n"
    )


def _dossier(v: Variant, letter: str) -> str:
    shown = {d.title for d in _common_documents(v)}
    for item in VARIANT_ITEMS[v.number]:
        if dossier_of(situation_of(item)) < letter:
            shown.update(d.title for d in item.documents)
    _l, title, numbers = next(row for row in DOSSIERS if row[0] == letter)
    points = sum(SITUATION_POINTS[n] for n in numbers)
    parts = [f"**Dossier {letter} — {title}** : questions {numbers[0]} à {numbers[-1]}, {points} points."]
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
        rows.append(f"| {number} | {dossier_of(number)} | {item.title} | {item.total_points:g} | "
                    f"{', '.join(item.requirement_ids)} | {_course_links(SITUATION_COURSES[number])} |")
    return (
        "| N° | Dossier | Situation | Points | Exigences | À revoir |\n|---|---|---|---|---|---|\n"
        + "\n".join(rows)
        + f"\n| — | — | **Total** | **{EXAM_TOTAL_POINTS}** | — | — |"
    )


def _dossiers() -> str:
    return "\n".join(
        f"- **Dossier {letter} — {title}** : questions {', '.join(str(n) for n in nums)} — "
        f"**{sum(SITUATION_POINTS[n] for n in nums)} points**"
        for letter, title, nums in DOSSIERS
    )


def _comparison() -> str:
    rows = "\n".join(f"| {number} | {EX05_COMPARISON[number]} |" for number in sorted(EX05_COMPARISON))
    ex05, ex06 = set(ex05_requirements()), set(evaluated_requirements())
    both = ", ".join(sorted(ex05 & ex06))
    only6 = ", ".join(sorted(ex06 - ex05))
    only5 = ", ".join(sorted(ex05 - ex06))
    return (
        "| N° | Par rapport à EX05 |\n|---|---|\n" + rows
        + f"\n\nExigences évaluées par les deux examens blancs globaux : {both}. **En plus dans EX06** : {only6}. "
        f"Évaluées par EX05 seulement : {only5}. Aucune question d'EX05 n'est reprise."
    )


def _presentation() -> str:
    slot = EXERCISE_SLOTS_BY_CODE["EX06"]
    evaluated = evaluated_requirements()
    reqs = "\n".join(_req(r) for r in evaluated)
    missing = ", ".join(missing_official_requirements())
    extra = [r for r in evaluated if r not in slot.requirement_ids]
    extra_text = f" ; en plus : {', '.join(extra)}" if extra else ""
    companies = " et ".join(f"**{v.label}** : {v.company} ({v.city})" for v in VARIANTS)
    return f"""## Ce que cet examen blanc évalue

Cet examen blanc **global avancé** porte sur **tout le parcours Pratique écrite** (cours PR01 à
PR30) et se passe **après l'examen blanc global standard
[EX05](/uaa/ampcr-pratique-ex05)**. Il reproduit une **journée d'intervention** chez un client,
avec **quatre dossiers complexes** : un poste qui ne démarre plus (stockage et données), l'évolution
du parc (devis, Windows, Linux), le câblage (RJ45 et coaxial BNC) et le réseau (adressage, Wi-Fi,
partages, rapport).

Chaque dossier contient **plusieurs causes possibles** et des **indices plausibles qui ne sont pas
décisifs** : il faut les départager par des **tests discriminants**, calculer (puissance, unités,
masques, signal Wi-Fi, résistances, durées), rédiger des procédures et protéger les données. Tous
les documents nécessaires sont fournis ; aucun indice n'est piégé : chacun s'explique par les
documents.

C'est un **entraînement Jury Central**, pas un sujet officiel ni une question déjà posée par le
Jury : entreprises, personnes, adresses et mesures sont **fictives**.

## Deux variantes du même examen

L'examen existe en **deux variantes** : {companies}. Même structure, mêmes situations et
même barème, mais **données, pannes et réponses différentes**. Chaque valeur a été recalculée par
programme avec les règles des cours. La session « Examen blanc » te donne **une variante
entière** : la variante 1 la première fois, puis la variante 2, puis celle que tu as le moins
faite. Les deux sujets sont imprimables ci-dessous.

## Organisation et notation

- **12 situations à réponse rédigée**, de **8 ou 9 points** : note sur **{EXAM_TOTAL_POINTS}**
  (ramenée aussi sur 20 sur la page de résultat, à titre de repère). Répartition par dossier :

{_dossiers()}

- Chaque question donne **le contexte, les documents, des consignes numérotées et ses points** ;
  elle se résout seule, dans n'importe quel ordre.
- **Barème analytique** : chaque question est notée sur 4 critères explicites (hypothèses, tests
  discriminants, calcul, procédure, vérification, justification). Toute formulation et toute
  méthode justes sont acceptées, aucun mot-clé n'est exigé ; une action dangereuse ou destructive
  sans sauvegarde ni accord fait perdre des points.
- Le **barème détaillé et le corrigé** de chaque question ne sont visibles **qu'après la remise**
  de ta copie.
- **Calculatrice** utile (questions 2, 4, 8, 9, 10 et 12).
- **Durée conseillée pour t'entraîner** : environ {SUGGESTED_DURATION}. C'est un repère
  personnel, **pas la durée officielle** de l'épreuve (voir les consignes officielles).

## Comment passer l'examen

1. Lis le sujet de ta variante sur cette page (ou imprime-le) : documents communs, puis dossiers
   A à D.
2. Ouvre l'onglet **[Examen blanc]({EXAM_URL})** (connexion nécessaire) et démarre la session :
   les 12 questions s'affichent une à une, dans l'ordre du sujet, avec leurs documents.
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

## Couverture comparée avec EX05

{_comparison()}

## Exigences des consignes officielles évaluées

{reqs}

Exigences prévues pour EX06 dans le plan : {', '.join(slot.requirement_ids)}{extra_text}.

**Non évaluées dans cet examen blanc** (manques explicités) : {missing}. Elles sont évaluées dans
les examens blancs EX01 → EX05 et dans les cours. Une exigence n'est jamais déclarée « validée »
par cet examen seul : voir la [matrice de couverture](/ampcr-pratique/matrice).
"""


def _method() -> str:
    return """## Répondre à un dossier complexe

1. **Liste les hypothèses** que suggèrent la demande et l'historique, sans en retenir une trop vite.
2. **Cherche le test qui départage** : celui qui élimine le plus d'hypothèses sans rien abîmer
   (le micrologiciel voit-il le disque ? la mesure vaut-elle 25 ou 50 Ω ? le ping par adresse
   IP répond-il ?).
3. **Calcule avec la règle du cours** et cite la valeur qui fonde ta conclusion : « 165 mm pour
   160 mm au plus, donc… ».
4. **Écarte explicitement les faux indices** : dis pourquoi ils ne sont pas la cause.
5. **Protège avant d'agir** : sauvegarde vérifiée, accord écrit, poste hors tension, bracelet
   antistatique ; annule d'abord le dernier changement connu.
6. **Décris l'intervention dans l'ordre**, puis la **vérification** qui prouve le résultat et la
   **trace** laissée au client.

**Pièges qui coûtent des points** : réinstaller un système qui ne demandait qu'un réglage,
désactiver une sécurité pour faire passer une installation, partitionner sans accord écrit,
écrire une image non vérifiée, oublier qu'un testeur de continuité ne voit pas des paires
séparées, corriger les droits d'une personne au lieu de son groupe, compter la pause dans les
heures facturées.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, Laboratoire et T.P. et
  méthodes évalués ensemble. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Matière** : cours PR01 à PR30 du parcours (mêmes règles : chaîne de démarrage et messages
  d'erreur, pile CR2032, MBR/GPT et unités, systèmes de fichiers, règle 3-2-1 et empreintes,
  compatibilité et budget de puissance, pilote VMD, mbr2gpt et activation, double démarrage,
  sha256sum et efibootmgr, T568B et paires séparées, 10BASE2 et BNC, calculs IPv4, signal Wi-Fi,
  canaux et sécurité, partage + NTFS, rapport d'intervention).
- **Documents publics** cités par les cours : configuration requise de Windows 11 et
  documentation de mbr2gpt (Microsoft), documentation d'installation d'Ubuntu, ANSI/TIA-568,
  IEEE 802.3 (10BASE2, 100BASE-TX, 1000BASE-T), IEEE 802.11, RFC 1918, RFC 3927 (APIPA) et
  RFC 5737.

## Supports fictifs

Les schémas des réseaux et du Wi-Fi sont **produits par programme** depuis des données vérifiées
par des tests automatiques ; les relevés et captures sont **fictifs et simplifiés**, au format
réel. Aucun n'est tiré d'une image générée ni d'une copie d'écran réelle, et aucun schéma ne
donne de verdict. Entreprises, personnes, adresses et mesures sont **fictives**. Aucune question
n'est un sujet officiel ou une question déjà posée par le Jury.
"""


def ex06_course_sections() -> list[tuple[str, str]]:
    """Blocs de la page du sujet (titre, contenu), dans l'ordre d'affichage."""
    sections = [("EX06 — Présentation, consignes et barème", _presentation())]
    for v in VARIANTS:
        sections.append((f"EX06 — {v.label} : documents communs, {v.company}", _common(v)))
        for letter, title, _nums in DOSSIERS:
            sections.append((f"EX06 — {v.label}, dossier {letter} — {title}", _dossier(v, letter)))
    sections += [
        ("EX06 — Méthode : répondre à un dossier complexe", _method()),
        ("EX06 — Sources et supports fictifs", _sources()),
    ]
    return sections
