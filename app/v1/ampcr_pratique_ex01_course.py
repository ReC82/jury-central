"""EX01 « Examen blanc écrit — maintenance et dépannage matériel » — page du sujet, version
candidat (ticket #230).

La page « Sujet » de l'UAA EX01 présente l'épreuve (consignes, barème global, exigences
évaluées) et le **sujet complet sans corrigé** : partie 1, dossiers A, B et C avec leurs
documents et schémas, puis les dix questions numérotées. À l'impression (A4), chaque question
reçoit des lignes de réponse et chaque dossier commence sur une nouvelle page. Les barèmes
détaillés et les corrigés ne sont jamais affichés ici : ils n'apparaissent qu'après la remise
de la session « Examen blanc » (moteur existant, correction après soumission).

Les titres de blocs évitent les mots qui changent le type de carte (`app.card_kind`) sauf
« Méthode » et « Sources », voulus. Questions et documents : `app.v1.ampcr_pratique_ex01_bank`
(même source que la banque des sessions) ; schémas : `app.v1.ampcr_pratique_ex01_figures`.
"""

from html import escape

from app.v1.ampcr_pratique_ex01_bank import (
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
from app.v1.ampcr_pratique_ex01_figures import (
    BOARD_FIGURE,
    STATIC_FIGURES,
    TEMPERATURE_FIGURE,
)
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import EXERCISE_SLOTS_BY_CODE
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr06_course import _document_html, _fig, _req
from app.v1.ampcr_pratique_visuals import DIAGNOSTIC_METHOD_FIGURE

EX01_TITLE = "Examen blanc écrit — maintenance et dépannage matériel"
EX01_SLUG = "ampcr-pratique-ex01"
EXAM_URL = f"/uaa/{EX01_SLUG}/exam"
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
        f'<div class="jc-ex-question" id="ex01-q{_number(item)}">'
        f'<p class="jc-ex-question-head"><span>Question {_number(item)} — {escape(item.title)}</span>'
        f"<span>{item.total_points:g} points</span></p>"
        f"<p>{escape(item.context)}</p><ol>{instructions}</ol>"
        f'<div class="jc-ex-answer" aria-hidden="true"><p class="small mb-1">Ta réponse :</p>{lines}</div>'
        "</div>"
    )


def _dossier(part: str, intro: str, extra_figure: str = "") -> str:
    """Documents puis questions d'un dossier. Un document n'apparaît que juste avant la
    première question qui l'utilise : le journal de fin d'intervention (A5), qui donne la
    solution de la question 4, n'est donc affiché qu'avant la question 5."""
    shown: set[str] = set()
    parts = ['<div class="jc-ex-dossier"></div>', intro]
    for item in (i for i in EXAM_ITEMS if ITEM_PARTS[i.key] == part):
        new_docs = [d for d in item.documents if d.title not in shown]
        if new_docs:
            parts.append(f"## Documents pour la question {_number(item)}")
            parts += [_doc_html(d) for d in new_docs]
            shown.update(d.title for d in new_docs)
            if extra_figure and any(d.title.startswith("Dossier B, document B4") for d in new_docs):
                parts.append(extra_figure)
        parts.append(_question_html(item))
    assert shown == {d.title for d in DOSSIER_DOCUMENTS[part]}
    return "\n\n".join(parts) + "\n"


def _questions(part: str) -> str:
    return "\n\n".join(_question_html(item) for item in EXAM_ITEMS if ITEM_PARTS[item.key] == part)


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
    slot = EXERCISE_SLOTS_BY_CODE["EX01"]
    reqs = "\n".join(_req(r) for r in slot.requirement_ids)
    return f"""## Ce que cet examen blanc évalue

Le premier examen blanc du parcours **Pratique écrite** porte sur tout le **module 1 —
matériel du PC** : structure et composants (PR01), alimentation, connectique et sécurité
(PR02), montage et démontage (PR03), reconditionnement et contrôles (PR04), stockage (PR05) et
diagnostic des pannes matérielles (PR06). Il reproduit une **logique d'intervention écrite** :
un plan à lire, des consignes de sécurité, puis **trois dossiers** de clients avec fiches,
manuels, relevés et captures, sur lesquels tu rédiges diagnostic, procédure, justification,
vérification et compte rendu.

C'est un **entraînement Jury Central**, pas un sujet officiel ni une question déjà posée par le
Jury : les entreprises, les références et les relevés sont **fictifs**.

## Organisation et notation

- **10 questions à réponse rédigée**, **10 points chacune** : note sur **{EXAM_TOTAL_POINTS}**
  (ramenée aussi sur 20 sur la page de résultat, à titre de repère).
- Chaque question donne **toutes les informations nécessaires** ; elle reprend dans la session
  les documents de son dossier, dans l'ordre où le moteur te la présente.
- **Barème analytique** : chaque question est notée sur des critères explicites (lecture des
  documents, procédure, justification, vérification). Toute formulation techniquement juste est
  acceptée, aucun mot-clé n'est exigé ; une action dangereuse ou destructive pour les données
  fait perdre des points.
- Le **barème détaillé et le corrigé** de chaque question ne sont visibles **qu'après la remise**
  de ta copie.
- **Durée conseillée pour t'entraîner** : environ 2 heures. C'est un repère personnel, **pas la
  durée officielle** de l'épreuve (voir les consignes officielles).

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
    return f"""Trois questions sans dossier : lire un plan de carte mère, corriger une intervention
dangereuse et préparer son outillage.

{_fig(BOARD_FIGURE, wide=True)}

Le plan ci-dessus est le **document 1** de la question 1 ; dans la session, il est affiché avec
la description écrite de chaque repère.

## Questions

{_questions(PART_1)}
"""


def _dossier_a() -> str:
    return _dossier(
        DOSSIER_A,
        "La fiduciaire Mertens (quatre postes) t'appelle : le PC de comptabilité ne démarre plus "
        "depuis qu'un proche de la gérante y a ajouté de la mémoire. Tu interviens sur place, puis tu "
        "rends compte de ton intervention.",
    )


def _dossier_b() -> str:
    return _dossier(
        DOSSIER_B,
        "Le studio Lumen fait du montage vidéo. Sa station de travail, vieille de quatre ans, ralentit "
        "pendant les rendus et doit recevoir une nouvelle carte graphique et plus de mémoire.",
        extra_figure=(
            "Le relevé du document B4, en courbe :\n\n" + _fig(TEMPERATURE_FIGURE).strip()
        ),
    )


def _dossier_c() -> str:
    return _dossier(
        DOSSIER_C,
        "À la clinique vétérinaire Les Saules, le PC de l'accueil conserve les dossiers des animaux et "
        "leurs radiographies. Deux problèmes : un SSD ajouté reste invisible, et le disque de données "
        "donne des signes de faiblesse.",
    )


def _method() -> str:
    return f"""## Répondre à un dossier d'intervention écrit

{_fig(DIAGNOSTIC_METHOD_FIGURE)}

1. **Lis toute la question, puis les documents** : souligne les valeurs, les messages exacts,
   ce qui a changé récemment et les contraintes (données, accord, budget).
2. **Cite tes preuves** : « la LED DRAM reste allumée (document A2) » vaut mieux que « c'est la
   RAM ».
3. **Ordonne ta procédure** : sécurité d'abord (débrancher, ESD, sauvegarde), puis du test le
   plus simple au plus invasif, un changement à la fois ; pour chaque test, le résultat attendu.
4. **Montre tes calculs** : formule, valeurs, résultat et unité, puis la conclusion.
5. **Termine par la vérification** : comment tu prouves que c'est réparé (test, durée, valeur).
6. **Rédige pour le client** quand on te le demande : phrases courtes, sans jargon, risques et
   accord demandé.

**Pièges qui coûtent des points** : manipuler sous tension, conclure sans test, réinstaller ou
formater « pour voir », oublier les données du client, donner un résultat sans calcul.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, liste des
  compétences du laboratoire. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Matière** : cours PR01 à PR06 du parcours (mêmes règles : budget d'alimentation avec 30 % de
  marge, température « à surveiller » à moins de 10 °C du maximum de la fiche, lecture SMART,
  ordre de montage, sécurité et ESD).
- **Documentation des fabricants** : manuels de cartes mères (LED de diagnostic, ports SATA
  partagés avec un emplacement M.2, installation de la mémoire), fiches de processeurs et de
  cartes graphiques.

## Supports fictifs

Le plan, les LED, la courbe et les captures sont **produits par programme** depuis des données
vérifiées par des tests automatiques ; aucun n'est tiré d'une image générée ni d'une
photographie. Les clients, les références et les valeurs sont **fictifs** et reconstitués pour
l'entraînement. Le plan de carte mère n'est pas à l'échelle : sur une vraie carte, le manuel fait
foi. Aucune question n'est un sujet officiel ou une question déjà posée par le Jury.
"""


def ex01_course_sections() -> list[tuple[str, str]]:
    """Blocs de la page du sujet (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("EX01 — Présentation, consignes et barème", _presentation()),
        ("EX01 — Partie 1 : identification et préparation (questions 1 à 3)", _part1()),
        ("EX01 — Dossier A : fiduciaire Mertens (questions 4 et 5)", _dossier_a()),
        ("EX01 — Dossier B : studio Lumen (questions 6 à 8)", _dossier_b()),
        ("EX01 — Dossier C : clinique vétérinaire Les Saules (questions 9 et 10)", _dossier_c()),
        ("EX01 — Méthode : répondre à un dossier d'intervention écrit", _method()),
        ("EX01 — Sources et supports fictifs", _sources()),
    ]
