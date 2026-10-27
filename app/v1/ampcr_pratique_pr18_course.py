"""Cours PR18 « Installation physique d'un mini-réseau » — parcours AMPCR pratique écrite
(ticket #219).

Matière : intégralement celle du ticket #219 (analyse du besoin et du plan des locaux ;
topologie en étoile ; implantation du switch, du point d'accès, du routeur, des prises et de la
baie ; choix cuivre / fibre / coaxial selon l'usage ; longueur, cheminement et repérage ;
sécurité et séparation du courant fort ; plan de câblage et nomenclature ; panneau de brassage
et keystones ; tests de continuité et certification ; alimentation PoE ; configuration de base
et validation PC-PC, Internet et partage ; documentation et recette ; cinq cas corrigés de plans
de salles et de choix du matériel), découpée en blocs titrés (le titre pilote le type de carte,
`app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention », « transfert »
ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr18_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr18_bank`. Les règles de choix et de pose du câble viennent de PR13,
les longueurs de PR15 (publiés, liens).
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr13_figures import EMI_MEDIUM, Need, choose
from app.v1.ampcr_pratique_pr18_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr18_figures import (
    BOX_M,
    CHANNEL_MAX_M,
    CHECK_FIGURE,
    CORDS_MAX_M,
    INSTALL_FIGURE,
    PANEL_PORTS,
    PATCH_FIGURE,
    PATCH_ROWS,
    PERMANENT_LINK_MAX_M,
    PLACEMENT,
    PLAN,
    PLAN_BOXES,
    PLAN_FIGURE,
    PLAN_LINKS,
    PLAN_QUOTE,
    PLAN_QUOTE_TOTALS,
    PLAN_RACK_U,
    PLAN_RUNS,
    PLAN_SWITCH,
    PLAN_TOTAL_M,
    POE_CLASS_W,
    POE_EXAMPLE,
    POE_EXAMPLE_SWITCHES,
    POE_EXAMPLE_TOTAL,
    POE_FIGURE,
    POE_STANDARDS,
    PORT_RESERVE,
    PROCEDURES,
    RACK_FIGURE,
    RACK_RESERVE,
    RACK_SIZES_U,
    RACK_USED_U,
    SEPARATION_MM,
    SLACK_M,
    STAR_FIGURE,
    STATIC_FIGURES,
    SWITCH_SIZES,
    TEST_FIGURE,
    VALIDATION_CHECKS,
    VAT_RATE,
    VERTICAL_M,
    WRITTEN_AT,
    LinkTest,
    boxes_needed,
    choose_switch,
    euro,
    fr,
    link_verdict,
    min_separation_mm,
    panels_needed,
    poe_verdict,
    run_length_m,
    switch_ports_needed,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR18_TITLE = "Installation physique d'un mini-réseau"
PR18_SLUG = "ampcr-pratique-pr18"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr18")
    for document in item.documents:
        if document.image:
            text = f'<p class="jc-pr-doc-text">{escape(document.content_text)}</p>'
            figure = str(render_figure(_SCHEMAS_BY_PATH[document.image]))
            html = html.replace(text, figure + text, 1)
    return html


def _exercises_html() -> str:
    return "\n\n".join(_card(i, item) for i, item in enumerate(PRACTICE_ITEMS, start=1))


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _placement_table() -> str:
    rows = "\n".join(f"| **{name}** | {where} | {why} |" for name, where, why in PLACEMENT)
    return "| Élément | Où l'installer | Pourquoi / à vérifier |\n|---|---|---|\n" + rows


def _runs_table() -> str:
    by_key = {o.key: o for o in PLAN.outlets}
    rows = "\n".join(
        f"| {key} | {by_key[key].label} | {fr(h)} m | {fr(h)} + {VERTICAL_M} + {SLACK_M} → **{length} m** |"
        for key, h, length in PLAN_RUNS
    )
    return "| Prise | Emplacement | Parcours horizontal | Longueur à prévoir |\n|---|---|---|---|\n" + rows


def _separation_table() -> str:
    rows = "\n".join(f"| {cls} | {mm} mm |" for cls, mm in SEPARATION_MM.items())
    return "| Classe de séparation du câble | Distance minimale sans cloison |\n|---|---|\n" + rows


def _poe_table() -> str:
    rows = "\n".join(f"| {std} | {cls} | {power} |" for std, cls, power in POE_STANDARDS)
    return "| Norme | Classes | Puissance au port du switch |\n|---|---|---|\n" + rows


def _quote_table() -> str:
    ht, vat, ttc = PLAN_QUOTE_TOTALS
    rows = "\n".join(
        f"| {line.ref} | {line.label} | {line.quantity} | {euro(line.unit_price)} | {euro(line.total)} |" for line in PLAN_QUOTE
    )
    return (
        "| Réf. | Désignation | Qté | PU HT | Total HT |\n|---|---|---|---|---|\n" + rows
        + f"\n| | **Total HT** | | | **{euro(ht)}** |\n| | TVA {fr(VAT_RATE * 100, 0)} % | | | {euro(vat)} |"
        + f"\n| | **Total TTC** | | | **{euro(ttc)}** |"
    )


def _patch_table() -> str:
    rows = "\n".join(f"| {label} | {dest} | {int(label.rsplit('-', 1)[1]):02d} | {port} |" for label, dest, port, _k in PATCH_ROWS)
    return "| Repère (prise = panneau) | Destination | Port du panneau | Port du switch |\n|---|---|---|---|\n" + rows


def _checks_table() -> str:
    rows = "\n".join(f"| {i} | **{key}** | {what} | {diag} |" for i, (key, what, diag) in enumerate(VALIDATION_CHECKS, start=1))
    return "| N° | Contrôle | Ce qu'on regarde | Piste si c'est le premier échec |\n|---|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


# --- Cinq cas résolus (valeurs calculées) -----------------------------------------------------

C1_MAX = max(length for _k, _h, length in PLAN_RUNS)
C1_HT, C1_VAT, C1_TTC = PLAN_QUOTE_TOTALS

C2_HORIZONTAL = (4.0, 5.5, 7.0, 8.5, 10.0, 11.5, 13.0, 14.5, 6.0, 7.5, 9.0, 10.5, 15.5, 16.0, 3.0, 12.0)
C2_LENGTHS = tuple(run_length_m(h) for h in C2_HORIZONTAL)
C2_LINKS = len(C2_HORIZONTAL)
C2_TOTAL = sum(C2_LENGTHS)
C2_BOXES = boxes_needed(C2_LENGTHS)
C2_PORTS = switch_ports_needed(C2_LINKS)
C2_SWITCH = choose_switch(C2_LINKS)

C3_CHOICE = choose(Need(rate_gbps=1, length_m=45, emi=EMI_MEDIUM, grounded=True))
C3_UNKNOWN = min_separation_mm(None)

C4_TOTAL = POE_EXAMPLE_TOTAL
C4_CLASSES = tuple(c for _n, c, q in POE_EXAMPLE for _ in range(q))

C5_TEST = LinkTest("B2-P1-03", False, 36, "FAIL")
C5_VERDICT = link_verdict(C5_TEST)

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Cabinet comptable : plan, baie et devis",
        (
            f"Le cabinet du plan ci-dessus ({fr(PLAN.width_m, 0)} m × {fr(PLAN.depth_m, 0)} m) veut cinq postes à deux "
            "prises, une imprimante, un écran de réunion et un point d'accès Wi-Fi. La ligne de l'opérateur "
            "arrive dans le petit local technique, au centre."
        ),
        (
            f"**Implantation** : baie et box dans le local technique, au centre de l'étoile ; {PLAN_LINKS} prises ; point d'accès au plafond du plateau, en PoE.",
            f"**Longueurs** : parcours + {VERTICAL_M} m + {SLACK_M} m ; la plus longue fait {C1_MAX} m ≤ {PERMANENT_LINK_MAX_M} m ; total {PLAN_TOTAL_M} m → {PLAN_BOXES} boîte de {BOX_M} m.",
            f"**Matériel** : {PLAN_LINKS} liens → {PLAN_LINKS} × 1,2 → {switch_ports_needed(PLAN_LINKS) - 1} + 1 = {switch_ports_needed(PLAN_LINKS)} ports → switch {PLAN_SWITCH} ports ; 1 panneau {PANEL_PORTS} ports ; baie {PLAN_RACK_U} U ({RACK_USED_U} U occupées).",
        ),
        f"Baie au centre, liens de {C1_MAX} m au plus, switch {PLAN_SWITCH} ports PoE, baie {PLAN_RACK_U} U ; devis {euro(C1_HT)} HT, {euro(C1_TTC)} TTC.",
    ),
    (
        "Cas 2 — Salle de classe de 12 PC",
        (
            "Une salle de 9 m × 7 m reçoit 12 PC élèves, le poste du professeur (deux prises), une imprimante "
            f"et un vidéoprojecteur réseau : {C2_LINKS} prises. La baie murale se place dans l'angle près de la "
            "porte ; les parcours horizontaux vont de 3 à 16 m, par goulotte le long des murs."
        ),
        (
            f"**Topologie** : étoile, une prise par PC le long des murs (pas de câble au sol), {C2_LINKS} liens jusqu'à la baie.",
            f"**Longueurs** : de {min(C2_LENGTHS)} à {max(C2_LENGTHS)} m ; total {C2_TOTAL} m → {C2_BOXES} boîte(s) de {BOX_M} m (aucun lien raccordé).",
            f"**Matériel** : {C2_LINKS} × 1,2 → {C2_PORTS - 1} + 1 = {C2_PORTS} ports → switch {C2_SWITCH} ports ; panneau {PANEL_PORTS} ports ; Cat6 U/UTP suffit (salle calme, 1 Gb/s).",
        ),
        f"Baie dans l'angle (liens ≤ {max(C2_LENGTHS)} m), {C2_LINKS} prises en goulotte, switch {C2_SWITCH} ports, {C2_BOXES} boîte(s) de câble.",
    ),
    (
        "Cas 3 — Bureaux et atelier : perturbations et courant fort",
        (
            "Une menuiserie relie son atelier (scies, aspiration, variateurs) à la baie des bureaux, à 45 m. "
            "La baie et les prises de l'atelier peuvent être reliées à la terre. Le seul passage est un "
            "chemin de câbles qui porte déjà trois circuits électriques ; la classe de séparation du câble "
            "n'est pas connue."
        ),
        (
            f"**Support** : perturbations moyennes, terre assurée → {C3_CHOICE.cable} ({C3_CHOICE.reason.lower()})",
            f"**Séparation** : classe inconnue → {C3_UNKNOWN} mm sans cloison (EN 50174-2) ; sinon compartiment à cloison métallique ; croisements à angle droit.",
            "**Contrôle** : écran continu de bout en bout (keystones et panneau blindés, baie à la terre), certification de chaque lien.",
        ),
        f"{C3_CHOICE.cable} dans un compartiment séparé ({C3_UNKNOWN} mm ou cloison métallique), système blindé relié à la terre, liens certifiés.",
    ),
    (
        "Cas 4 — Agence : Wi-Fi, caméras et téléphones en PoE",
        (
            "Une agence immobilière ajoute "
            + ", ".join(f"{q} × {n.lower()} (classe {c})" for n, c, q in POE_EXAMPLE)
            + ", tous alimentés par le câble. Trois switchs sont proposés : "
            + ", ".join(f"{s} ({fr(b, 0)} W de budget PoE)" for s, b in POE_EXAMPLE_SWITCHES) + "."
        ),
        (
            "**Puissance réservée** : " + " + ".join(f"{q} × {fr(POE_CLASS_W[c])} W" for _n, c, q in POE_EXAMPLE) + f" = {fr(C4_TOTAL)} W.",
            "**Comparaison** : " + " ; ".join(f"{s} {fr(b, 0)} W → {poe_verdict(C4_CLASSES, b).lower()}" for s, b in POE_EXAMPLE_SWITCHES) + ".",
            f"**Longueur** : le PoE passe par le même câble, {CHANNEL_MAX_M} m de canal au plus ; aucune prise électrique à prévoir près des appareils.",
        ),
        f"Switch C ({fr(POE_EXAMPLE_SWITCHES[2][1], 0)} W) : il couvre les {fr(C4_TOTAL)} W réservés avec de la marge ; A et B seraient dépassés.",
    ),
    (
        "Cas 5 — Deux bâtiments : liaison, recette et validation",
        (
            "Une école relie le pavillon des maternelles (8 prises) au bâtiment principal, à 160 m par une "
            "gaine enterrée. Au test, la prise B2-P1-03 du pavillon montre un fil coupé. Après réparation, "
            "un poste du pavillon obtient une adresse mais n'ouvre pas le dossier partagé de la direction."
        ),
        (
            "**Liaison** : 160 m entre deux bâtiments → fibre (câble d'extérieur) entre les deux switchs ; étoile cuivre dans chaque bâtiment.",
            f"**Recette** : B2-P1-03 → {C5_VERDICT.lower()} ; keystone refait, lien retesté (PASS), rapport archivé.",
            "**Validation** : lien, adresse, passerelle, autre poste, Internet réussis ; le partage échoue seul → piste « partage » (chemin, droits, compte), pas le câblage.",
        ),
        "Fibre entre les bâtiments, lien B2-P1-03 refait et certifié, réseau validé ; droits du partage corrigés et consignés au procès-verbal.",
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant le plan d'un local et une demande de client, on attend de toi une **installation
réfléchie** : où placer la baie et les prises, quel câble, quelle longueur, quel matériel, quel
prix, comment tester et comment prouver que le réseau fonctionne. Tu dois savoir :

1. **analyser le besoin** et lire un **plan de locaux** ;
2. **organiser** le réseau en **étoile** et **implanter** baie, switch, box ou routeur, point
   d'accès Wi-Fi et prises ;
3. **choisir le support** (cuivre, fibre, coaxial) selon l'usage ;
4. **estimer les longueurs**, choisir le **cheminement** et **repérer** chaque lien ;
5. **respecter la sécurité** et la **séparation du courant fort** ;
6. **équiper la baie** : **panneau de brassage**, **keystones**, cordons ;
7. **prévoir l'alimentation PoE** quand elle est utile ;
8. établir le **plan de câblage**, la **nomenclature** et le **devis** ;
9. **tester** (continuité) et **certifier** le câblage ;
10. **configurer** le minimum et **valider** : poste à poste, Internet, partage ;
11. **documenter** et faire **réceptionner** l'installation.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-36")}
{_req("AP-38")}

Ce sont deux exigences **officielles** (consignes, p. 6). Le choix et la pose des câbles sont
détaillés en [PR13](/uaa/ampcr-pratique-pr13), les distances en [PR14](/uaa/ampcr-pratique-pr14),
le brochage RJ45 et le testeur en [PR15](/uaa/ampcr-pratique-pr15), le coaxial en
[PR16](/uaa/ampcr-pratique-pr16), la fibre en [PR17](/uaa/ampcr-pratique-pr17), l'adressage IP
en [PR20](/uaa/ampcr-pratique-pr20) et le dépannage en [PR24](/uaa/ampcr-pratique-pr24). Les
topologies (PR19), la connexion de deux PC (PR21) et les partages (PR23) seront approfondis dans
leurs cours, publiés ensuite dans l'ordre du parcours.

## Lien avec la théorie

Les équipements et le câblage sont présentés dans la théorie AMPCR :
[MC14 Équipements réseau](/uaa/ampcr-mc14) et [MC15 Câblage Ethernet et RJ45](/uaa/ampcr-mc15).
Ce cours-ci est **pratique** : plans, nomenclatures, devis, rapports de test et relevés à
analyser, comme dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont cinq **schémas à
compléter** et quatre **devis ou nomenclatures**), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les plans, devis, prix, appareils, rapports de test et relevés de ce cours
> sont des **supports fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}). Les
> longueurs, puissances PoE et distances de séparation viennent des normes nommées dans les
> sources ; **la fiche du fabricant et les normes en vigueur font foi**. Aucun exercice n'est
> une question officielle ni une question déjà posée par le Jury.
"""


def _needs() -> str:
    return f"""**Objectifs** : recueillir le besoin du client et lire un plan de locaux avant de dessiner
quoi que ce soit.

## 1.1 Les questions à poser

- **Qui et quoi** : combien de postes, d'imprimantes, de téléphones IP, de caméras, d'écrans ;
  où travaille chacun ; qui a besoin du Wi-Fi (personnel, visiteurs à séparer) ;
- **usages** : Internet, partage de fichiers, imprimante commune, logiciel métier, débit ;
- **évolution** : embauches, nouvelles pièces : on prévoit **deux prises par poste** et des
  ports en réserve (**convention du cours**) ;
- **contraintes** : budget, délais, horaires des travaux, accord du propriétaire pour percer.

## 1.2 Lire le plan des locaux

On relève sur le plan : les **dimensions** (cotes, échelle), l'**arrivée de la ligne de
l'opérateur**, un **local** possible pour la baie (fermé, ventilé, prise électrique), les
**chemins** possibles (faux plafond, goulottes, gaines), les **câbles électriques** et les
sources de **perturbations** (moteurs, néons, machines), les **murs à traverser**.

{_fig(PLAN_FIGURE)}

**Procédure professionnelle (à rédiger)** : interroger le client → visiter et relever le plan →
compter les prises pièce par pièce → noter contraintes et perturbations → faire valider la liste
avant de concevoir.

**Erreur fréquente** : chiffrer le matériel au téléphone sans visite ; oublier l'imprimante, le
point d'accès ou la caméra, qui ont aussi besoin d'une prise.

**À l'écrit** : « 6 postes × 2 prises + imprimante + écran + point d'accès = 15 prises ».

**Repère rapide** : **besoin → plan → liste des prises validée par le client**. Exercices liés :
{_ex("E19", "E13")}.
"""


def _star() -> str:
    return f"""**Objectifs** : organiser le réseau en étoile et placer chaque équipement au bon endroit.

## 2.1 La topologie en étoile

Dans un réseau local actuel, chaque prise est reliée **par son propre câble** au **switch**,
centre de l'**étoile**. La **box** (ou le routeur) de l'opérateur est reliée au switch : c'est la
**passerelle** vers Internet. Un câble coupé n'arrête **qu'un poste** ; on ajoute un poste en
brassant un port de plus. Avec plusieurs switchs reliés entre eux (deux étages, deux bâtiments),
on parle d'**étoile étendue** (ou d'arbre). Le détail des topologies est l'objet de PR19.

{_fig(STAR_FIGURE)}

## 2.2 Implanter les équipements

{_placement_table()}

Le **switch** et le **panneau de brassage** sont dans la **baie** ; la **box** y est souvent
posée sur une étagère. Le **point d'accès Wi-Fi** se place là où sont les utilisateurs, pas dans
la baie fermée (le métal arrête les ondes).

**Procédure professionnelle (à rédiger)** : placer la baie au centre (longueurs) dans un local
adapté → la box à l'arrivée de l'opérateur → les prises près des postes → le point d'accès au
centre de la zone à couvrir → tracer les chemins.

**Erreur fréquente** : baie dans un coin du bâtiment (liens trop longs), dans un local humide ou
ouvert à tous ; point d'accès posé dans la baie métallique.

**À l'écrit** : « baie au centre : lien le plus long 23 m ≤ 90 m ; local fermé et ventilé ».

**Repère rapide** : **un câble par prise · switch au centre · box à l'arrivée · Wi-Fi en hauteur
au milieu**. Exercices liés : {_ex("E04", "E08", "E11")}.
"""


def _support() -> str:
    c_office = choose(Need(rate_gbps=1, length_m=35))
    return f"""**Objectifs** : choisir le support de chaque liaison selon l'usage, la distance et
l'environnement.

## 3.1 Règle de choix (PR13)

- **Ethernet dans un bâtiment**, jusqu'à {CHANNEL_MAX_M} m de canal : **paire torsadée cuivre**
  ({c_office.cable} pour un poste à 1 Gb/s dans des bureaux calmes ; Cat6A pour 10 Gb/s) ; blindage
  F/UTP ou S/FTP seulement si les perturbations l'exigent **et** si la terre est assurée de bout
  en bout ;
- **plus de {CHANNEL_MAX_M} m**, **entre deux bâtiments**, **perturbations fortes** sans terre
  possible : **fibre optique** (PR17) ;
- **vidéo analogique** (caméra, enregistreur) et **télévision** : **coaxial 75 Ω** existant
  (PR16) ; le coaxial ne sert plus au réseau informatique.

## 3.2 Toute la chaîne de la même catégorie

Câble, keystones, panneau et cordons sont de la **même catégorie** (Cat6A avec Cat6A) : le lien
vaut son maillon le plus faible. Dans le lien permanent : câble **monobrin** poinçonné ; cordons :
**multibrin**.

**Procédure professionnelle (à rédiger)** : pour chaque liaison, noter l'usage, la longueur,
l'environnement → appliquer la règle → écrire la référence complète (catégorie, blindage).

**Erreur fréquente** : câble cuivre entre deux bâtiments ; câble blindé posé avec des keystones
non blindés (écran interrompu, inutile) ; mélanger Cat5e et Cat6A.

**À l'écrit** : « 140 m vers le bâtiment B → fibre ; postes à 35 m → Cat6 U/UTP ».

**Repère rapide** : **≤ 100 m dans le bâtiment : cuivre · au-delà ou entre bâtiments : fibre ·
vidéo, TV : coaxial 75 Ω**. Exercices liés : {_ex("E05", "E11")}.
"""


def _lengths() -> str:
    return f"""**Objectifs** : estimer la longueur de chaque lien, choisir le cheminement et repérer.

## 4.1 Estimer une longueur

Un câble ne traverse pas les pièces en diagonale : il suit les **murs**, le **faux plafond**,
les **goulottes**. **Convention du cours** : longueur = parcours horizontal (écart en x + écart
en y) + **{VERTICAL_M} m** de montée et de descente + **{SLACK_M} m** de réserve, arrondie au mètre
supérieur. Chaque lien permanent doit rester **≤ {PERMANENT_LINK_MAX_M} m**, cordons compris le canal
**≤ {CHANNEL_MAX_M} m** (cordons ≤ {CORDS_MAX_M} m) — données de [PR15](/uaa/ampcr-pratique-pr15).

Pour le cabinet du plan (baie en B) :

{_runs_table()}

Total : **{PLAN_TOTAL_M} m**. Le câble se vend en **boîtes de {BOX_M} m** ; un lien ne se raboute
jamais : on vérifie que chaque longueur tient dans le reste d'une boîte (ici {PLAN_BOXES} boîte).

## 4.2 Cheminement

- par le **faux plafond** (chemin de câbles), puis **descente** en goulotte jusqu'à la prise ;
- jamais au sol dans un passage, jamais fixé sur les câbles électriques ;
- rayons de courbure, traction et colliers non serrés : règles de [PR13](/uaa/ampcr-pratique-pr13).

## 4.3 Repérage

Chaque lien porte le **même repère aux deux extrémités** : à la prise et au port du panneau.
**Convention du cours** : « B1-P1-07 » = baie 1, panneau 1, port 07. On étiquette le câble
**avant** de le tirer, puis la prise et le panneau.

**Procédure professionnelle (à rédiger)** : mesurer le parcours sur le plan → calculer chaque
longueur → vérifier ≤ {PERMANENT_LINK_MAX_M} m → total et boîtes → attribuer les repères.

**Erreur fréquente** : mesurer à vol d'oiseau ; oublier montée, descente et réserve ; commander
« total ÷ 305 » sans vérifier que chaque lien tient dans une boîte.

**À l'écrit** : « 87,5 + 5 = 92,5 → 93 m > 90 m → non conforme ».

**Repère rapide** : **parcours + {VERTICAL_M + SLACK_M} m · ≤ {PERMANENT_LINK_MAX_M} m · boîtes de {BOX_M} m · même
repère aux deux bouts**. Exercices liés : {_ex("E13", "E17", "E10")}.
"""


def _safety() -> str:
    return f"""**Objectifs** : poser le câblage sans danger et loin des perturbations électriques.

## 5.1 Séparation du courant fort

Les câbles d'énergie induisent des **parasites** dans les câbles de données. La norme
**EN 50174-2** fixe une **distance minimale** selon la **classe de séparation** du câble de
données (donnée par le fabricant), sans cloison et jusqu'à trois circuits d'énergie :

{_separation_table()}

Classe inconnue : on applique **{min_separation_mm(None)} mm**. Une **cloison métallique** reliée à
la terre permet de réduire la distance ; on **croise** un câble électrique **à angle droit**.
Détails en [PR13](/uaa/ampcr-pratique-pr13).

## 5.2 Sécurité du chantier

- avant de percer : **plans** et **détecteur** de câbles et de canalisations ;
- travail près d'un circuit : le faire **couper** ; on ne touche jamais un conducteur nu ;
- **escabeau** stable, **lunettes** pour percer, poussière aspirée ;
- **traversées coupe-feu** refermées après passage ;
- baie : **prise électrique dédiée**, pas de multiprise en cascade.

**Procédure professionnelle (à rédiger)** : repérer les câbles d'énergie sur le plan → fixer
les distances → choisir chemin séparé ou cloison → sécuriser le chantier → refermer et nettoyer.

**Erreur fréquente** : coucher le câble réseau sur les câbles électriques « parce qu'il y a de la
place » ; percer sans détecteur.

**À l'écrit** : « classe b, sans cloison : 100 mm ; 50 mm → non conforme → chemin séparé ».

**Repère rapide** : **a 300 · b 100 · c 50 · d 10 mm · inconnue 300 mm · croiser à angle
droit · détecteur avant de percer**. Exercices liés : {_ex("E18")}.
"""


def _rack() -> str:
    used = RACK_USED_U
    return f"""**Objectifs** : équiper la baie et raccorder les câbles au panneau et aux prises.

## 6.1 Panneau de brassage et keystones

Chaque câble du lien permanent est **poinçonné** à ses deux extrémités : sur un **keystone**
(connecteur RJ45 femelle à contacts autodénudants) clipsé dans la **prise murale**, et sur le
**panneau de brassage** (ports déjà équipés, ou panneau vide qu'on équipe de keystones). On suit
**une seule norme** (T568A ou T568B) partout, et on détorsade au plus 13 mm (PR13, PR15). Un lien
avec panneau vide compte donc **deux keystones**.

Devant le panneau, des **cordons de brassage** courts relient chaque port du panneau à un port
du switch : on peut changer un poste de port sans toucher au câblage fixe.

## 6.2 Organiser la baie

{_fig(RACK_FIGURE)}

Ordre courant (**convention de l'atelier**) : panneau, **passe-câbles**, switch (cordons courts
et rangés), étagère de la box, **bandeau électrique** en bas. Hauteur en **unités** (1 U =
44,45 mm) : ici {used} U occupées ; avec **{int(RACK_RESERVE * 100)} % de réserve** (convention du cours),
{used} × {fr(1 + RACK_RESERVE, 2)} = {fr(used * (1 + RACK_RESERVE), 2)} → baie de **{PLAN_RACK_U} U** (tailles courantes :
{", ".join(str(u) for u in RACK_SIZES_U)} U). Un panneau de {PANEL_PORTS} ports dessert {PANEL_PORTS} liens.

**Procédure professionnelle (à rédiger)** : fixer la baie → monter panneau, passe-câbles,
switch, étagère, bandeau → poinçonner chaque câble au repère prévu → brasser → étiqueter.

**Erreur fréquente** : panneau en bas et switch en haut (cordons d'un mètre qui pendent) ;
mélanger T568A et T568B ; baie pleine sans réserve.

**À l'écrit** : « 10 U × 1,25 = 12,5 → baie 15 U ; 40 prises → 2 panneaux 24 ports ».

**Repère rapide** : **keystone à la prise et au panneau · une seule norme · panneau / passe-câbles
/ switch · réserve 25 %**. Exercices liés : {_ex("E09", "E16")}.
"""


def _poe() -> str:
    return f"""**Objectifs** : décider si le PoE est utile et vérifier le budget du switch.

## 7.1 Le principe

Le **PoE** (alimentation par le câble Ethernet) permet au **switch** d'alimenter un appareil par
son câble réseau : **point d'accès Wi-Fi**, **caméra IP**, **téléphone IP**. Plus besoin d'une
prise électrique au plafond ; le câble reste limité à {CHANNEL_MAX_M} m. Chaque appareil annonce une
**classe** ; le switch **réserve** une puissance par port :

{_poe_table()}

Puissance réservée par classe : classe 1 {fr(POE_CLASS_W[1])} W, classe 2 {fr(POE_CLASS_W[2])} W, classe 3
{fr(POE_CLASS_W[3])} W, classe 4 {fr(POE_CLASS_W[4])} W.

## 7.2 Le budget PoE

Un switch PoE a un **budget total** (par exemple 65, 130 ou 370 W) : la somme des puissances
réservées ne doit pas le dépasser, sinon un appareil ne démarre pas ou s'éteint.

{_fig(POE_FIGURE)}

**Procédure professionnelle (à rédiger)** : lister les appareils PoE et leur classe → additionner
les puissances réservées → comparer au budget total du switch → choisir (ou injecteur PoE).

**Erreur fréquente** : compter les ports PoE et oublier le budget total ; brancher un appareil
non PoE en pensant l'alimenter.

**À l'écrit** : « 30 + 4 × 15,4 + 6 × 7 = {fr(POE_EXAMPLE_TOTAL)} W > 130 W → switch de 370 W ».

**Repère rapide** : **af 15,4 W · at 30 W · bt 60-90 W · somme ≤ budget total**. Exercices
liés : {_ex("E15")}.
"""


def _documents() -> str:
    ht, vat, ttc = PLAN_QUOTE_TOTALS
    return f"""**Objectifs** : produire le plan de câblage, la nomenclature et le devis.

## 8.1 Plan de câblage et plan de brassage

Le **plan de câblage** est le plan des locaux avec les prises numérotées, la baie, les chemins.
Le **plan de brassage** dit, pour chaque repère, la destination, le port du panneau et le port
du switch :

{_fig(PATCH_FIGURE)}

{_patch_table()}

## 8.2 Nomenclature

La **nomenclature** (liste du matériel) se déduit du plan : pour **{PLAN_LINKS} liens** :
{PLAN_BOXES} boîte de câble, **{2 * PLAN_LINKS} keystones** (prise + panneau vide),
{panels_needed(PLAN_LINKS)} panneau de {PANEL_PORTS} ports, {PLAN_LINKS} boîtiers muraux, {PLAN_LINKS} cordons de brassage,
{PLAN_LINKS} cordons de poste, un switch, la baie et ses accessoires. Le switch : liens + {int(PORT_RESERVE * 100)} % de
réserve + 1 port pour la box ({PLAN_LINKS} × 1,2 → {switch_ports_needed(PLAN_LINKS) - 1} + 1 = {switch_ports_needed(PLAN_LINKS)} → **{PLAN_SWITCH} ports** ;
tailles courantes {", ".join(str(s) for s in SWITCH_SIZES)}).

## 8.3 Devis

Chaque ligne : **quantité × prix unitaire HT** ; puis **total HT**, **TVA** (taux normal belge
**{fr(VAT_RATE * 100, 0)} %**) et **total TTC** (prix fictifs) :

{_quote_table()}

**Procédure professionnelle (à rédiger)** : compter sur le plan → nomenclature → prix unitaires
→ totaux de ligne → HT, TVA, TTC → relire et faire signer avant de commander.

**Erreur fréquente** : un seul keystone par lien ; TVA au mauvais taux ; total de ligne mal
calculé ; oublier cordons et passe-câbles.

**À l'écrit** : « total HT {euro(ht)} + TVA {euro(vat)} = {euro(ttc)} TTC ».

**Repère rapide** : **plan → nomenclature → devis HT + 21 % = TTC**. Exercices liés :
{_ex("E12", "E13", "E14", "E15", "E16")}.
"""


def _tests() -> str:
    return f"""**Objectifs** : tester chaque lien et savoir lire un rapport de certification.

## 9.1 Trois niveaux d'appareils

- **testeur de continuité** (vérificateur) : contrôle les **8 fils** et les paires (coupure,
  court-circuit, inversion, paires séparées selon le modèle) et souvent la **longueur** ;
- **qualificateur** : dit si le lien supporte un débit (100 Mb/s, 1 Gb/s) — complément ;
- **certificateur** : mesure tous les paramètres de la **catégorie visée** (perte d'insertion,
  paradiaphonie…) et rend **PASS** ou **FAIL**, avec un **rapport** par lien : c'est ce qu'on
  remet au client d'une installation neuve.

## 9.2 Lire un rapport, dans l'ordre

1. **Câblage** (wiremap) : un fil coupé ou une paire inversée → refaire le raccordement ;
2. **Longueur** : au-delà de {PERMANENT_LINK_MAX_M} m → le lien est trop long ;
3. **Performances** : câblage et longueur corrects mais **FAIL** → raccordement trop détorsadé,
   câble écrasé ou plié, composant d'une catégorie inférieure.

{_fig(TEST_FIGURE)}

**Procédure professionnelle (à rédiger)** : les six étapes ci-dessus, lien par lien, avec le
repère et le résultat.

**Erreur fréquente** : « le PC a du réseau, donc le câble est bon » (un lien peut monter à
100 Mb/s avec une paire coupée) ; retester sans avoir corrigé.

**À l'écrit** : « B1-P1-11 : câblage correct, 94 m → trop long ; B1-P1-15 : FAIL paradiaphonie →
poinçonnage refait ».

**Repère rapide** : **câblage → longueur → performances · PASS archivé par lien**. Exercices
liés : {_ex("E03", "E06")}.
"""


def _config() -> str:
    return f"""**Objectifs** : faire la configuration de base et prouver que le réseau fonctionne.

## 10.1 Configuration de base

- **box** : réseau local (par exemple 192.168.1.0/24), **serveur DHCP** actif, mot de passe
  d'administration changé, Wi-Fi chiffré (WPA2/WPA3) et réseau invité pour les visiteurs ;
- **switch** : non administrable, il fonctionne branché ; administrable : adresse fixe dans le
  réseau, mot de passe changé, ports PoE vérifiés ;
- **postes** : adresse automatique (DHCP), nom unique, même groupe de travail ou domaine ;
  le partage de dossiers et d'imprimantes est détaillé en PR23, l'adressage en
  [PR20](/uaa/ampcr-pratique-pr20).

## 10.2 Valider dans l'ordre

{_checks_table()}

{_fig(CHECK_FIGURE)}

Chaque contrôle suppose que les précédents réussissent : **le premier qui échoue désigne la
piste** ; inutile de chercher le partage tant que le poste a une adresse 169.254.x.x. Le
dépannage détaillé est l'objet de [PR24](/uaa/ampcr-pratique-pr24).

**Procédure professionnelle (à rédiger)** : configurer box, switch et postes → valider depuis
chaque poste dans l'ordre → corriger la première piste en échec → consigner.

**Erreur fréquente** : tester Internet d'abord ; conclure « le câble est mauvais » alors que le
voyant est allumé et que l'adresse est en 169.254.

**À l'écrit** : « voyant allumé, adresse 169.254.88.14 → pas de DHCP → vérifier brassage et box ».

**Repère rapide** : **lien → adresse → passerelle → autre poste → Internet → partage**.
Exercices liés : {_ex("E02", "E07")}.
"""


def _handover() -> str:
    return f"""**Objectifs** : documenter l'installation et la faire réceptionner par le client.

## 11.1 Le dossier de recette

- **plan de câblage** (locaux, prises, baie, chemins) ;
- **plan de brassage** (repère, destination, port du panneau, port du switch) ;
- **rapport de test** de chaque lien (PASS) ;
- **configuration** de base (adresses de la box et du switch) — mots de passe remis à part ;
- **résultats de la validation** (lien, adresse, passerelle, autre poste, Internet, partage) ;
- **procès-verbal de réception** daté et signé, avec les **réserves** éventuelles.

## 11.2 La réception

On fait la **visite** avec le client, on montre la validation sur un poste, on remet le dossier.
Une réserve (prise non accessible, lien à reprendre) est notée et levée ensuite. Le dossier est
**mis à jour** à chaque modification : c'est la base de tout dépannage.

{_fig(INSTALL_FIGURE)}

**Procédure professionnelle (à rédiger)** : rassembler plans, rapports, configuration et
validation → visite avec le client → PV signé → archivage et copie au client.

**Erreur fréquente** : livrer sans plan de brassage ni rapports ; mots de passe écrits dans le
dossier remis à tous.

**À l'écrit** : « dossier remis : plans, 13 rapports PASS, validation, PV signé sans réserve ».

**Repère rapide** : **plans + rapports + validation + PV signé**. Exercices liés :
{_ex("E01", "E20")}.
"""


def _examples() -> str:
    blocks: list[str] = []
    for title, situation, steps, conclusion in CASES:
        lines = "\n".join(f"{i}. {line}" for i, line in enumerate(steps, start=1))
        blocks.append(
            f"""## {title}

**Situation.** {situation}

**Résolution.**

{lines}

**Conclusion rédigée.** « {conclusion} »
"""
        )
    return (
        "Cinq plans de salles résolus pas à pas avec les règles du cours : implantation, longueurs, "
        "choix du support et du matériel, PoE, recette. Chaque conclusion est justifiée par une valeur.\n\n"
        + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return f"""> **Placer la baie dans un coin** : les liens les plus éloignés dépassent {PERMANENT_LINK_MAX_M} m.

> **Mesurer à vol d'oiseau** : le câble suit les murs, monte et descend ; prévoir la réserve.

> **Un seul keystone par lien** sur un panneau vide : il en faut un à la prise et un au panneau.

> **Câble cuivre entre deux bâtiments** ou au-delà de {CHANNEL_MAX_M} m : fibre.

> **Câble réseau couché sur les câbles électriques** : distance de séparation ou cloison.

> **Compter les ports PoE sans le budget total** du switch.

> **Repère différent à la prise et au panneau**, ou pas de repère du tout.

> **Mélanger T568A et T568B**, ou Cat5e et Cat6A, dans un même lien.

> **Livrer sans tester** : « le PC a du réseau » ne prouve pas que le lien est conforme.

> **Valider dans le désordre** : chercher le partage alors que le poste n'a pas d'adresse.

> **TVA au mauvais taux** ou total de ligne faux dans le devis.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (installation, tests du câblage, validation),
classements (implantation, choix du support, rapport de recette, premier contrôle en échec),
**cinq schémas à compléter** (plan des locaux, baie, chaîne d'un lien, étoile, plan de
brassage), **quatre devis et nomenclatures** (nomenclature d'un plan, devis à vérifier, choix d'un
switch PoE, baie), longueurs et commande de câble, sécurité, analyse du besoin et dossier de
recette. Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute réponse équivalente
et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR18_SLUG}/practice), avec correction après envoi.

{_exercises_html()}
"""


_ANSWER_TYPES = {
    "short_answer": "réponse courte",
    "long_answer": "réponse développée",
    "document_analysis": "analyse de document",
}


def _mini_exam() -> str:
    rows = "\n".join(
        f"| {i} | {item.title} | {_ANSWER_TYPES[item.question_type]} | {item.total_points:g} |"
        for i, item in enumerate(EXAM_ITEMS, start=1)
    )
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR18_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (plans, devis et relevés fictifs). Une calculatrice simple
peut aider pour le devis. **Aucune correction n'est visible pendant la passation** ; tes réponses
sont enregistrées au fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le
**barème analytique** de la question (critères et points), puis tu vois ta note sur
{EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **choix justifié** (emplacement, support, matériel), le
**calcul juste** (longueurs, ports, PoE, devis), la **procédure** et la **sécurité** — pas la
récitation de sigles. Une autre solution technique juste et justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Besoin** : appareils, usages, Wi-Fi, PoE, évolution ; deux prises par poste ; plan relevé.
- **Étoile** : un câble par prise jusqu'au switch ; box à l'arrivée de l'opérateur ; point
  d'accès en hauteur au centre de la zone.
- **Baie** : local fermé, ventilé, central ; panneau / passe-câbles / switch / box / bandeau ;
  réserve {int(RACK_RESERVE * 100)} %.
- **Support** : cuivre ≤ {CHANNEL_MAX_M} m dans un bâtiment ; fibre au-delà ou entre bâtiments ; coaxial
  75 Ω pour la vidéo et la TV.
- **Longueur** : parcours + {VERTICAL_M} m + {SLACK_M} m ; lien permanent ≤ {PERMANENT_LINK_MAX_M} m, canal ≤ {CHANNEL_MAX_M} m ;
  boîtes de {BOX_M} m, sans raboutage.
- **Repère** : même repère à la prise et au panneau (B1-P1-07).
- **Courant fort** : a 300, b 100, c 50, d 10 mm ; inconnue 300 mm ; croiser à angle droit.
- **Keystones** : 2 par lien avec panneau vide ; une seule norme T568A ou B.
- **PoE** : af 15,4 W, at 30 W, bt 60-90 W ; somme ≤ budget total.
- **Devis** : quantité × PU HT ; total HT ; TVA {fr(VAT_RATE * 100, 0)} % ; TTC.
- **Tests** : câblage → longueur → performances ; PASS archivé.
- **Validation** : lien → adresse → passerelle → autre poste → Internet → partage.
- **Recette** : plans, rapports, validation, PV signé.

## Glossaire des termes employés

- **Baie** : armoire qui reçoit panneau, switch et accessoires, en unités (U).
- **Canal** : liaison complète du switch au PC, cordons compris (≤ {CHANNEL_MAX_M} m).
- **Certificateur** : testeur qui mesure les performances d'un lien selon sa catégorie (PASS/FAIL).
- **Keystone** : connecteur RJ45 femelle à poinçonner, clipsé dans une prise ou un panneau.
- **Lien permanent** : câble fixe du panneau à la prise (≤ {PERMANENT_LINK_MAX_M} m).
- **Nomenclature** : liste du matériel avec quantités.
- **Panneau de brassage** : rangée de ports dans la baie où arrivent les câbles des prises.
- **Passe-câbles** : panneau qui guide les cordons de brassage.
- **PoE** : alimentation d'un appareil par son câble Ethernet.
- **Procès-verbal (PV) de réception** : document signé par lequel le client accepte l'installation.
- **Topologie en étoile** : chaque appareil relié par son propre câble à un point central.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « Câblage et installation physique d'un réseau
  informatique » (AP-36) et « Création d'un mini réseau entre plusieurs machines » (AP-38).
  Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **TIA-568** et **ISO/IEC 11801** : câblage structuré, lien permanent ≤ 90 m, canal ≤ 100 m,
  catégories ; **ISO/IEC 14763-2** et **EN 50174-1/-2** : installation, repérage,
  documentation, séparation des câbles d'énergie.
- **IEEE 802.3af, 802.3at, 802.3bt** : alimentation par le câble (classes et puissances).
- **EIA-310** : unité de baie (1 U = 44,45 mm).
- **TVA belge** : taux normal de 21 %.

Les valeurs sont celles de {WRITTEN_AT} ; les normes évoluent et les fabricants précisent leurs
propres valeurs : **la fiche technique et les normes en vigueur font foi**. Les plans, étoiles,
baies, plans de brassage, budgets PoE, devis et procédures du cours sont **produits par
programme** depuis des données **vérifiées par des tests automatiques** ; aucun schéma n'est
tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite le câblage, l'installation physique et la création d'un mini-réseau. Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- les **conventions du cours** : longueur = parcours + {VERTICAL_M} m + {SLACK_M} m ; {int(PORT_RESERVE * 100)} % de ports
  de réserve ; {int(RACK_RESERVE * 100)} % d'unités libres ; deux prises par poste ; repère « B1-P1-07 » ;
  ordre des équipements dans la baie ;
- le budget PoE par classe, le qualificateur, le devis et la TVA ;
- la configuration de base de la box et du switch (détaillée dans d'autres cours).

## Supports fictifs

Les plans, entreprises, prix, appareils, devis, rapports de test et relevés de ce cours sont
**fictifs** et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucune
n'est une question officielle ou déjà posée par le Jury. Pour un chantier réel, on utilise les
fiches des fabricants, les normes et un appareil de mesure.
"""


def pr18_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR18 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR18 — 1. Analyser le besoin et le plan des locaux", _needs()),
        ("PR18 — 2. Topologie en étoile et implantation des équipements", _star()),
        ("PR18 — 3. Choisir le support : cuivre, fibre ou coaxial", _support()),
        ("PR18 — 4. Longueurs, cheminement et repérage", _lengths()),
        ("PR18 — 5. Sécurité et séparation du courant fort", _safety()),
        ("PR18 — 6. Baie, panneau de brassage et keystones", _rack()),
        ("PR18 — 7. Alimentation par le câble (PoE)", _poe()),
        ("PR18 — 8. Plan de câblage, nomenclature et devis", _documents()),
        ("PR18 — 9. Tests de continuité et certification", _tests()),
        ("PR18 — 10. Configuration de base et validation du réseau", _config()),
        ("PR18 — 11. Documentation et réception", _handover()),
        ("PR18 — Exemples : cinq plans de salles résolus", _examples()),
        ("PR18 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR18 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR18 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR18 — Fiche mémo et glossaire", _memo()),
        ("PR18 — Sources et compléments pédagogiques", _sources()),
    ]
