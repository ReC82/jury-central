"""EX02 « Examen blanc écrit — installation et dépannage des systèmes » — page du sujet,
version candidat (ticket #231).

Même modèle que EX01 (#230) : la page « Sujet » de l'UAA EX02 présente l'épreuve (consignes,
barème global, exigences évaluées) et le **sujet complet sans corrigé** : partie 1, dossiers A,
B et C avec leurs documents, captures et schémas, puis les dix questions numérotées. À
l'impression (A4), chaque question reçoit des lignes de réponse et chaque dossier commence sur
une nouvelle page. Barèmes détaillés et corrigés n'apparaissent qu'après la remise de la session
« Examen blanc ».

Les titres de blocs évitent les mots qui changent le type de carte (`app.card_kind`) sauf
« Méthode » et « Sources », voulus. Questions et documents : `app.v1.ampcr_pratique_ex02_bank`
(même source que la banque des sessions) ; schémas : `app.v1.ampcr_pratique_ex02_figures`.
"""

from html import escape

from app.v1.ampcr_pratique_ex02_bank import (
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
from app.v1.ampcr_pratique_ex02_figures import STATIC_FIGURES
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import EXERCISE_SLOTS_BY_CODE
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr06_course import _document_html, _fig, _req
from app.v1.ampcr_pratique_pr12_figures import LADDER, ladder_svg
from app.v1.ampcr_pratique_visuals import Figure

EX02_TITLE = "Examen blanc écrit — installation et dépannage des systèmes"
EX02_SLUG = "ampcr-pratique-ex02"
EXAM_URL = f"/uaa/{EX02_SLUG}/exam"
ANSWER_LINES = 12  # lignes de réponse par question dans la version imprimée

_FIGURES_BY_FILE = {path: figure for figure, path in STATIC_FIGURES}

# Rappel de méthode (pas un document de question) : l'échelle des interventions de PR12.
METHOD_LADDER_FIGURE = Figure(
    key="ex02-echelle-interventions",
    title="Rappel de méthode — du geste le moins invasif au plus invasif (PR12)",
    alt=(
        "Échelle des interventions logicielles, du moins invasif au plus invasif : "
        + " ; ".join(f"{i}. {step.name}" for i, step in enumerate(LADDER, start=1))
        + ". Plus on descend, plus on perd de programmes ou de fichiers : précaution plus forte."
    ),
    caption=(
        "Même échelle que le cours PR12 : on commence toujours par annuler le dernier changement ; "
        "on ne descend d'une marche qu'après échec de la précédente, avec la précaution indiquée."
    ),
    svg=ladder_svg(LADDER),
)


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
        f'<div class="jc-ex-question" id="ex02-q{_number(item)}">'
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
    slot = EXERCISE_SLOTS_BY_CODE["EX02"]
    reqs = "\n".join(_req(r) for r in slot.requirement_ids)
    return f"""## Ce que cet examen blanc évalue

Le deuxième examen blanc du parcours **Pratique écrite** porte sur tout le **module 2 —
systèmes d'exploitation** : choix du système et prérequis (PR07), installation de Windows
(PR08) et de Linux (PR09), comptes, pilotes, paramètres et commandes (PR10), messages d'erreur
(PR11), dépannage logiciel et restauration (PR12). Il reproduit une **logique d'intervention
écrite** : un relevé de postes et une capture de terminal, puis **trois dossiers** de clients
avec fiches, écrans d'installation, captures de WinRE et du terminal Linux, plans de partitions
et journaux, sur lesquels tu rédiges choix, procédure ordonnée, justification et vérification.

C'est un **entraînement Jury Central**, pas un sujet officiel ni une question déjà posée par le
Jury : les entreprises, les références et les relevés sont **fictifs**.

## Organisation et notation

- **10 questions à réponse rédigée**, **10 points chacune** : note sur **{EXAM_TOTAL_POINTS}**
  (ramenée aussi sur 20 sur la page de résultat, à titre de repère).
- Chaque question donne **toutes les informations nécessaires** ; elle reprend dans la session
  les documents de son dossier, dans l'ordre où le moteur te la présente.
- **Barème analytique** : chaque question est notée sur des critères explicites (lecture des
  documents, procédure dans l'ordre, justification, vérification). Toute formulation et toute
  commande techniquement justes sont acceptées, aucun mot-clé n'est exigé ; une action
  destructive pour les données (formater, supprimer une partition, réinitialiser sans
  sauvegarde vérifiée ni accord) fait perdre des points.
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
    return _part(
        PART_1,
        "Deux questions sans dossier : choisir un système et une édition à partir d'un relevé de postes, "
        "puis utiliser les outils graphiques et la ligne de commande pour relancer un service.",
        dossier=False,
    )


def _dossier_a() -> str:
    return _part(
        DOSSIER_A,
        "Le bureau d'architectes Verhaegen (cinq personnes) fait installer Windows 11 sur un SSD neuf dans "
        "son poste de dessin, puis veut des pilotes à jour et des comptes en ordre.",
        dossier=True,
    )


def _dossier_b() -> str:
    return _part(
        DOSSIER_B,
        "Le Repair Café « La Clé » est une asbl de bénévoles. Il te confie trois demandes : un double "
        "démarrage Windows-Ubuntu, son serveur de fichiers Debian qui ne démarre plus, et un problème de "
        "droits sur un dossier partagé.",
        dossier=True,
    )


def _dossier_c() -> str:
    return _part(
        DOSSIER_C,
        "À l'agence immobilière Delvaux, un poste ne démarre plus depuis une mise à jour de pilote, et un "
        "second poste a un Windows endommagé que le gérant veut faire « remettre à neuf ».",
        dossier=True,
    )


def _method() -> str:
    return f"""## Répondre à un dossier d'installation ou de dépannage écrit

{_fig(METHOD_LADDER_FIGURE)}

1. **Lis toute la question, puis les documents** : relève le message exact, le code d'erreur,
   la commande et sa sortie, ce qui a changé récemment et les contraintes (données, licence,
   accord du client).
2. **Situe l'étape** : firmware, chargeur de démarrage, noyau et pilotes, services, session de
   l'utilisateur ; c'est elle qui oriente l'outil (WinRE, mode de maintenance, journal).
3. **Cite tes preuves** : « fstab désigne /dev/sdb1, qui n'existe plus (document B4) » vaut mieux
   que « problème de disque ».
4. **Protège les données d'abord** : sauvegarde vérifiée et accord écrit avant toute opération
   qui supprime, formate ou réinitialise ; ne touche jamais un disque ou une partition qui n'est
   pas la cible.
5. **Ordonne ta procédure** : du geste le moins invasif au plus invasif ; écris les commandes
   exactes et dis qui les lance (compte standard, administrateur, root).
6. **Termine par la vérification** : comment tu prouves que c'est réglé, y compris après un
   redémarrage.

**Pièges qui coûtent des points** : réinstaller « pour voir », supprimer ou formater sans
sauvegarde, désactiver le démarrage sécurisé pour contourner un problème, donner des droits
d'administrateur ou `chmod 777` à tout le monde, oublier la vérification.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, liste des
  compétences du laboratoire. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Matière** : cours PR07 à PR12 du parcours (mêmes règles : prérequis de Windows 11,
  éditions, partitions d'une installation UEFI/GPT, double démarrage, comptes et moindre
  privilège, permissions Linux, services, échelle des interventions, empreintes SHA-256).
- **Documentation des éditeurs** : prérequis et outils de Windows 11 (Microsoft), documentation
  d'Ubuntu et de Debian (installation, systemd, fstab), identifiants de fabricants PCI et USB
  (listes publiques PCI-SIG et USB-IF).

## Supports fictifs

L'écran de l'installateur, le plan de partitions, l'écran d'arrêt, les captures de WinRE et du
terminal Linux et les journaux sont **produits par programme** depuis des données vérifiées par
des tests automatiques ; aucun n'est tiré d'une image générée ni d'une copie d'écran réelle. Les
libellés de Windows et de Linux sont ceux de la rédaction (octobre 2026) et changent selon les
versions. Les clients, noms de pilotes, UUID, empreintes et valeurs sont **fictifs** et
reconstitués pour l'entraînement. Aucune question n'est un sujet officiel ou une question déjà
posée par le Jury.
"""


def ex02_course_sections() -> list[tuple[str, str]]:
    """Blocs de la page du sujet (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("EX02 — Présentation, consignes et barème", _presentation()),
        ("EX02 — Partie 1 : choix du système et outils (questions 1 et 2)", _part1()),
        ("EX02 — Dossier A : bureau d'architectes Verhaegen (questions 3 à 5)", _dossier_a()),
        ("EX02 — Dossier B : Repair Café « La Clé » (questions 6 à 8)", _dossier_b()),
        ("EX02 — Dossier C : agence immobilière Delvaux (questions 9 et 10)", _dossier_c()),
        ("EX02 — Méthode : répondre à un dossier d'installation ou de dépannage", _method()),
        ("EX02 — Sources et supports fictifs", _sources()),
    ]
