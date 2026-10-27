"""EX03 « Examen blanc écrit — câblage RJ45, BNC et fibre » — page du sujet, version candidat
(ticket #232).

Même modèle que EX01 (#230) et EX02 (#231) : la page « Sujet » de l'UAA EX03 présente
l'épreuve (consignes, barème global, exigences évaluées) et le **sujet complet sans corrigé** :
partie 1, dossiers A, B et C avec leurs documents et schémas, puis les dix questions numérotées.
À l'impression (A4), chaque question reçoit des lignes de réponse et chaque dossier commence sur
une nouvelle page. Barèmes détaillés et corrigés n'apparaissent qu'après la remise de la session
« Examen blanc ».

Les titres de blocs évitent les mots qui changent le type de carte (`app.card_kind`) sauf
« Méthode » et « Sources », voulus. Questions et documents : `app.v1.ampcr_pratique_ex03_bank`
(même source que la banque des sessions) ; schémas : `app.v1.ampcr_pratique_ex03_figures`.
Aucun schéma de rappel sur cette page : les brochages, règles de pose et tableaux des cours
donneraient les réponses ; on les revoit dans PR13 → PR17 (liens « À revoir » du barème).
"""

from html import escape

from app.v1.ampcr_pratique_ex03_bank import (
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
from app.v1.ampcr_pratique_ex03_figures import STATIC_FIGURES
from app.v1.ampcr_pratique_format import ExerciseDocument
from app.v1.ampcr_pratique_plan import EXERCISE_SLOTS_BY_CODE
from app.v1.ampcr_pratique_pr06_bank import PR06Item
from app.v1.ampcr_pratique_pr06_course import _document_html, _fig, _req

EX03_TITLE = "Examen blanc écrit — câblage RJ45, BNC et fibre"
EX03_SLUG = "ampcr-pratique-ex03"
EXAM_URL = f"/uaa/{EX03_SLUG}/exam"
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
        f'<div class="jc-ex-question" id="ex03-q{_number(item)}">'
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
    slot = EXERCISE_SLOTS_BY_CODE["EX03"]
    reqs = "\n".join(_req(r) for r in slot.requirement_ids)
    return f"""## Ce que cet examen blanc évalue

Le troisième examen blanc du parcours **Pratique écrite** porte sur tout le **module 3 —
câblage** : choix et pose des câbles UTP, FTP, STP et coaxiaux (PR13), débits, distances,
atténuation et impédance (PR14), câblage RJ45 T568A/B (PR15), câble coaxial et BNC (PR16), fibre
optique (PR17). Il reproduit une **logique d'intervention écrite** : une fiche RJ45 et un tableau
de liaisons, puis **trois dossiers** de clients avec fiches de chantier, rapports de test,
relevés de pose, schéma d'un bus coaxial, mesures, catalogue et trace de réflectomètre, sur
lesquels tu rédiges choix, procédure de réalisation, diagnostic, justification et vérification.

C'est un **entraînement Jury Central**, pas un sujet officiel ni une question déjà posée par le
Jury : les entreprises, les repères et les mesures sont **fictifs**.

## Organisation et notation

- **10 questions à réponse rédigée**, **10 points chacune** : note sur **{EXAM_TOTAL_POINTS}**
  (ramenée aussi sur 20 sur la page de résultat, à titre de repère).
- Chaque question donne **toutes les informations nécessaires** ; elle reprend dans la session
  les documents de son dossier, dans l'ordre où le moteur te la présente.
- **Barème analytique** : chaque question est notée sur des critères explicites (lecture des
  documents, valeurs exactes, procédure dans l'ordre, justification, vérification). Toute
  formulation juste est acceptée, aucun mot-clé n'est exigé ; un brochage faux, une valeur
  d'impédance fausse ou un geste dangereux (regarder une fibre, livrer un câble qui échoue au
  test) fait perdre des points.
- Le **barème détaillé et le corrigé** de chaque question ne sont visibles **qu'après la remise**
  de ta copie.
- **Calculatrice** utile pour les questions 9 et 10 (bilan optique, distances).
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
        "Deux questions sans dossier : contrôler une fiche RJ45 sertie par un stagiaire, puis choisir le cordon "
        "(droit ou croisé) de quatre liaisons.",
        dossier=False,
    )


def _dossier_a() -> str:
    return _part(
        DOSSIER_A,
        "L'imprimerie Lambert (18 personnes) fait recâbler ses locaux rénovés : bureaux, local technique, atelier "
        "des presses, quai de chargement et magasin de papier. Tu choisis les câbles, tu analyses le rapport de "
        "test et tu contrôles la pose.",
        dossier=True,
    )


def _dossier_b() -> str:
    return _part(
        DOSSIER_B,
        "Le musée de l'informatique « Octet » est une asbl qui fait fonctionner des machines d'époque en réseau "
        "Ethernet sur câble coaxial. Un segment ne fonctionne pas, un autre tombe en panne pendant la semaine, et "
        "le musée prépare une vitrine sur l'Ethernet épais.",
        dossier=True,
    )


def _dossier_c() -> str:
    return _part(
        DOSSIER_C,
        "La brasserie Van Daele relie ses bureaux, son entrepôt et son hall de production. Tu choisis les "
        "liaisons, tu réceptionnes la fibre posée entre deux bâtiments, puis tu la dépannes six mois plus tard.",
        dossier=True,
    )


def _method() -> str:
    return """## Répondre à un dossier de câblage écrit

1. **Lis toute la question, puis les documents** : relève les longueurs, catégories, marquages,
   valeurs gravées, lectures d'appareil et contraintes du client (norme du site, débit, budget).
2. **Écris les valeurs exactes** : ordre des fils broche par broche, impédance en ohms, longueur
   maximale, dB/km ; un schéma ou un brochage approximatif ne rapporte pas de points.
3. **Calcule en montrant le détail** : chaque terme d'un bilan, chaque soustraction de
   distance, avec l'unité ; puis compare à la limite et conclus.
4. **Cite tes preuves** : « 1→3, 2→6, 3→1, 6→2 sur le testeur (document A4) » vaut mieux que
   « câble mal fait ».
5. **Ordonne ta procédure de réalisation** : matériel adapté, préparation, montage, contrôle
   visuel, test, étiquetage ; pour un dépannage, du plus simple au plus lourd.
6. **Termine par la vérification et la sécurité** : test ou mesure qui prouve que c'est réglé,
   rapport remis au client ; jamais d'œil face à une fibre, réseau arrêté pour mesurer un bus.

**Pièges qui coûtent des points** : confondre T568A et T568B, oublier l'orientation de la fiche,
mélanger 50 Ω et 75 Ω, confondre multimode et monomode ou UPC et APC, raccourcir un cordon
pour « rattraper » un lien permanent trop long, livrer un câble qui échoue au test.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3, 5 et 6 : épreuve uniquement écrite, types de câbles,
  débits, caractéristiques, fibre optique, réalisation de câbles RJ45 et BNC. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Matière** : cours PR13 à PR17 du parcours (mêmes règles : choix du câble et du blindage,
  rayons de courbure, traction et séparation, longueurs des liens, brochages T568A/B, droit et
  croisé, bus 10BASE2 et 10BASE5, ohmmètre, portées et bilan optique, réflectométrie).
- **Normes publiques** citées par les cours : TIA/EIA-568 (brochages, longueurs, pose),
  ISO/IEC 11801 (désignations X/YTP), EN 50174-2 (séparation), IEEE 802.3 (Ethernet cuivre,
  coaxial et optique). La fiche du fabricant fait foi.

## Supports fictifs

La fiche RJ45, l'affichage du testeur, le bus coaxial et la trace du réflectomètre sont
**produits par programme** depuis des données vérifiées par des tests automatiques ; aucun n'est
tiré d'une image générée ni d'une copie d'écran réelle, et aucun ne donne de verdict. Les
entreprises, repères, fiches de modules, mesures et valeurs sont **fictifs** et reconstitués pour
l'entraînement. Aucune question n'est un sujet officiel ou une question déjà posée par le Jury.
"""


def ex03_course_sections() -> list[tuple[str, str]]:
    """Blocs de la page du sujet (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("EX03 — Présentation, consignes et barème", _presentation()),
        ("EX03 — Partie 1 : fiches et cordons RJ45 (questions 1 et 2)", _part1()),
        ("EX03 — Dossier A : imprimerie Lambert (questions 3 à 5)", _dossier_a()),
        ("EX03 — Dossier B : musée de l'informatique « Octet » (questions 6 et 7)", _dossier_b()),
        ("EX03 — Dossier C : brasserie Van Daele (questions 8 à 10)", _dossier_c()),
        ("EX03 — Méthode : répondre à un dossier de câblage écrit", _method()),
        ("EX03 — Sources et supports fictifs", _sources()),
    ]
