"""Cours PR17 « Fibre optique — choix, raccordement et diagnostic » — parcours AMPCR pratique
écrite (ticket #218).

Matière : intégralement celle du ticket #218 (principe de la lumière guidée dans le cœur et la
gaine ; monomode et multimode, portées conditionnées par la norme et le module ; types OM/OS ;
connecteurs LC/SC ; modules SFP/SFP+ ; émission/réception TX/RX et duplex ; longueur d'onde ;
pertes et atténuation ; connecteurs propres ; épissure et pigtail ; brassage et rayons de
courbure ; comparaison avec le cuivre et le coaxial : parasites, distance, coût ; procédure de
pose et de contrôle ; mesure de puissance, photométrie et réflectométrie OTDR au niveau
technicien ; sécurité laser et éclats de fibre ; cinq cas résolus : lien inversé, connecteur
sale, mauvais module, distance, casse), découpée en blocs titrés (le titre pilote le type de
carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention », « transfert »
ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr17_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr17_bank`. Les valeurs d'affaiblissement et les portées des modules
viennent de PR14 (publié, lien) ; le choix des câbles cuivre de PR13 ; le coaxial de PR16.
"""

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr14_figures import (
    CONNECTOR_PAIR_DB,
    FIBRE_REACH,
    SPLICE_DB,
    attenuation_for,
)
from app.v1.ampcr_pratique_pr17_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr17_figures import (
    BEND_FACTOR_PULL,
    BEND_FACTOR_REST,
    BUFFER_UM,
    CHAIN_FIGURE,
    CHAIN_TOTAL_DB,
    CLADDING_UM,
    CLEAN_FIGURE,
    COATING_UM,
    COMPARISON,
    CONNECTORS,
    CONNECTORS_FIGURE,
    DIAG_FIGURE,
    DUPLEX_FIGURE,
    FIBRE_KINDS,
    GROUP_INDEX,
    INSTALL_FIGURE,
    LR_SPEC,
    MODULES,
    NO_LIGHT_DBM,
    OTDR_EXAMPLE,
    OTDR_FIGURE,
    POLISHES,
    PROCEDURES,
    RX_FIGURE,
    SECTION_FIGURE,
    WRITTEN_AT,
    break_position_m,
    dbm_fr,
    fr,
    max_link_loss_db,
    measured_loss_db,
    min_bend_radius_mm,
    module_errors,
    otdr_distance_m,
    rx_power_dbm,
)

PR17_TITLE = "Fibre optique — choix, raccordement et diagnostic"
PR17_SLUG = "ampcr-pratique-pr17"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr17") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _kinds_table() -> str:
    rows = "\n".join(
        f"| **{k.code}** | {k.mode} | {fr(k.core_um)}/{CLADDING_UM} µm | "
        f"{' et '.join(f'{w} nm' for w in k.wavelengths)} | {k.jacket} | {k.connector} | {k.note} |"
        for k in FIBRE_KINDS
    )
    return ("| Fibre | Type | Cœur/gaine | Longueurs d'onde | Gaine (habituelle) | Connecteur (habituel) | Remarque |\n"
            "|---|---|---|---|---|---|---|\n" + rows)


def _reach_table() -> str:
    rows = "\n".join(
        f"| **{module}** | {fibre} | {wl} nm | {m if m < 1000 else fr(m / 1000)} {'m' if m < 1000 else 'km'} |"
        for module, fibre, wl, m in FIBRE_REACH
    )
    return "| Module | Fibre | Longueur d'onde | Portée maximale |\n|---|---|---|---|\n" + rows


def _connectors_table() -> str:
    rows = "\n".join(f"| **{name}** | {fr(ferrule, 2)} mm | {lock} | {use} |" for name, ferrule, lock, use in CONNECTORS)
    return "| Connecteur | Férule | Verrouillage | Usage courant |\n|---|---|---|---|\n" + rows


def _polish_table() -> str:
    rows = "\n".join(f"| **{name}** | {angle}° | {colour} | {note} |" for name, angle, colour, note in POLISHES)
    return "| Polissage | Angle de la face | Couleur en monomode | Remarque |\n|---|---|---|---|\n" + rows


def _modules_table() -> str:
    rows = "\n".join(f"| **{m.name}** | {m.form} | {m.rate} | {m.wavelength_nm} nm | {m.mode} |" for m in MODULES)
    return "| Module | Format | Débit | Longueur d'onde | Fibre |\n|---|---|---|---|---|\n" + rows


def _comparison_table() -> str:
    rows = "\n".join(f"| **{c}** | {cu} | {coax} | {fo} |" for c, cu, coax, fo in COMPARISON)
    return "| Critère | Cuivre (paire torsadée) | Coaxial | Fibre optique |\n|---|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


# --- Cinq cas résolus (valeurs calculées) -----------------------------------------------------

C1_MAX = max_link_loss_db(800, "OS2", 1310, 2, 2)
C1_RX = rx_power_dbm(-2.1, 1.9)
C2_MAX = max_link_loss_db(60, "OM4", 850, 2, 0)
C2_EXPECTED = rx_power_dbm(-2.4, C2_MAX)
C2_EXTRA = round(C2_EXPECTED - (-11.8), 2)
C3_ERRORS = module_errors("10GBASE-SR", "10GBASE-LR", "OS2", 2000)
C4_LOSS = max_link_loss_db(420, "OM1", 850, 2, 0)
C5_BREAK = break_position_m(562, 150)
C5_AFTER = max_link_loss_db(640, "OS2", 1310, 2, 4)

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Lien inversé",
        (
            "Une fibre OS2 de 800 m (2 connecteurs, 2 épissures) relie deux bâtiments d'une école. Modules "
            "10GBASE-LR posés, aucun lien. Les deux modules émettent −2,1 dBm et reçoivent −40 dBm (LOS). Au "
            "photomètre, les fibres perdent 1,9 et 2,0 dB."
        ),
        (
            f"**Fibres** : perte admissible 0,8 × 0,4 + 2 × {fr(CONNECTOR_PAIR_DB, 2)} + 2 × {fr(SPLICE_DB)} = {fr(C1_MAX, 2)} dB ; 1,9 et 2,0 dB : les fibres sont bonnes.",
            "**Modules** : ils émettent ; aucun ne reçoit. La lumière de chaque TX arrive donc sur le TX d'en face : polarité inversée.",
            "**Correction** : croiser les deux fibres à une seule extrémité (clip duplex de la jarretière).",
        ),
        (
            f"Polarité inversée. Après croisement à une extrémité, le lien monte ; chaque côté reçoit environ "
            f"{dbm_fr(C1_RX)} dBm (−2,1 − 1,9). Polarité notée dans le plan de brassage."
        ),
    ),
    (
        "Cas 2 — Connecteur sale",
        (
            "Liaison 10GBASE-SR en OM4 de 60 m entre deux baies (2 connecteurs). Depuis un rebrassage, le "
            "switch A compte des erreurs CRC. B émet −2,4 dBm ; A reçoit −11,8 dBm ; la fiche (fictive) "
            "demande au moins −9,9 dBm."
        ),
        (
            f"**Attendu** : perte ≤ 0,06 × 3,5 + 1,5 = {fr(C2_MAX, 2)} dB, donc réception vers {dbm_fr(C2_EXPECTED)} dBm.",
            f"**Constat** : −11,8 dBm, soit {fr(C2_EXTRA, 1)} dB de trop, et sous la sensibilité : d'où les erreurs.",
            "**Inspection** : la sonde montre une tache grasse sur la jarretière côté A. Nettoyage à sec, réinspection propre, rebranchement.",
        ),
        "Connecteur sale côté A. Après nettoyage, A reçoit −3,0 dBm et les erreurs ne progressent plus ; intervention consignée.",
    ),
    (
        "Cas 3 — Mauvais module",
        (
            "Après le remplacement du switch d'un siège, le lien vers le dépôt (2 km de fibre jaune OS2) ne "
            "monte plus. Le technicien a mis un module 10GBASE-SR du stock ; le dépôt a un 10GBASE-LR."
        ),
        (
            "**Modules** : SR à 850 nm d'un côté, LR à 1 310 nm de l'autre : ils ne sont pas de la même norme.",
            "**Fibre** : le SR est un module multimode ; la fibre jaune OS2 est monomode.",
            "**Correction** : un 10GBASE-LR, reconnu par le nouveau switch, aux deux extrémités.",
        ),
        f"Deux erreurs : {C3_ERRORS[0].lower()} et {C3_ERRORS[1].lower()}. Avec un LR de chaque côté, le lien monte ; puissance reçue contrôlée.",
    ),
    (
        "Cas 4 — Distance trop grande pour le module",
        (
            "Une liaison 1000BASE-SX relie un atelier aux bureaux par 420 m de fibre OM1 (2 connecteurs). Le "
            "lien tombe et compte des erreurs. Le collègue a calculé une perte faible."
        ),
        (
            f"**Bilan** : 0,42 × 3,5 + 1,5 = {fr(C4_LOSS, 2)} dB : les pertes ne sont pas en cause.",
            "**Portée** : 1000BASE-SX ne tient que 275 m sur OM1 (dispersion modale) ; 420 m la dépassent.",
            "**Solution** : tirer une fibre monomode OS2 et passer en 1000BASE-LX (5 km), ou une OM2 et plus (550 m en 1000BASE-SX).",
        ),
        "Portée dépassée : on vérifie toujours la portée du module sur la fibre posée, pas seulement le bilan des pertes.",
    ),
    (
        "Cas 5 — Fibre cassée",
        (
            "Après le terrassement d'un parking, la liaison OS2 de 640 m entre une mairie et le hall des sports "
            "est coupée. Aucune lumière au photomètre. Trace OTDR depuis la mairie, bobine amorce de 150 m : "
            "pic à 150 m, puis grand pic à 562 m et plus que du bruit."
        ),
        (
            "**Lecture** : 150 m = connecteur du tiroir (début de la liaison) ; la trace finit à 562 m au lieu de 790 m.",
            f"**Position** : 562 − 150 = {C5_BREAK:g} m de fibre depuis le tiroir de la mairie, dans la zone des travaux.",
            f"**Réparation** : deux épissures par fusion en boîtier étanche ; perte admissible portée à {fr(C5_AFTER, 2)} dB.",
        ),
        f"Cassure à {C5_BREAK:g} m. Après réparation, mesure au photomètre et à l'OTDR conforme ; dossier mis à jour.",
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant un dossier sur une liaison optique, on attend de toi un **choix justifié**, une
**procédure** de raccordement et de contrôle, et un **diagnostic** appuyé sur des mesures. Tu dois
savoir :

1. **expliquer** comment la lumière est guidée dans le **cœur** et la **gaine** ;
2. **choisir** entre **monomode** et **multimode** (types **OM** et **OS**) et le **module
   optique** (SFP, SFP+) qui tient la distance ;
3. **reconnaître** les connecteurs **LC** et **SC**, le polissage **UPC/APC**, et relier
   correctement **émission (TX)** et **réception (RX)** d'une liaison **duplex** ;
4. **décrire** le raccordement : **épissure**, **pigtail**, tiroir optique, **brassage**, **rayon
   de courbure** ;
5. **comparer** la fibre au **cuivre** et au **coaxial** (parasites, distance, coût) ;
6. **contrôler** une liaison : **connecteurs propres**, **mesure de puissance**, **photométrie**,
   **réflectométrie (OTDR)** ;
7. **travailler en sécurité** : lumière **laser** invisible, **éclats de fibre** ;
8. **diagnostiquer** un lien inversé, un connecteur sale, un mauvais module, une distance trop
   grande ou une casse.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-21")}
{_req("AP-22")}

Ce sont deux exigences **officielles** (consignes, p. 6). Les valeurs d'affaiblissement et les
portées des modules sont celles de [PR14](/uaa/ampcr-pratique-pr14) (le bilan y est détaillé) ;
le choix et la pose des câbles cuivre sont étudiés en [PR13](/uaa/ampcr-pratique-pr13), le
brochage RJ45 en [PR15](/uaa/ampcr-pratique-pr15), le coaxial en
[PR16](/uaa/ampcr-pratique-pr16).

## Lien avec la théorie

Les notions de base sur les câbles réseau sont présentées dans la théorie AMPCR :
[MC15 Câblage Ethernet et RJ45](/uaa/ampcr-mc15). Ce cours-ci est **pratique** : relevés de
modules, rapports de mesure, traces de réflectomètre et chantiers à analyser, comme dans un
dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner »,
correction après envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet
« Examen blanc ».

> **Important —** les relevés, fiches de modules, rapports de mesure, traces et chantiers de ce
> cours sont des **supports fictifs** construits pour s'entraîner. Les valeurs citées viennent
> des normes nommées dans les sources (rédaction : {WRITTEN_AT}) ; **la fiche technique du
> fabricant et les normes en vigueur font foi**. Aucun exercice n'est une question officielle
> ni une question déjà posée par le Jury.
"""


def _principle() -> str:
    return f"""**Objectifs** : expliquer pourquoi la lumière reste dans la fibre et ce que la fibre
transporte.

## 1.1 Cœur, gaine, revêtement

Une fibre optique est un fil de **verre** très pur. Au centre, le **cœur** transporte la lumière ;
autour, la **gaine optique** ({CLADDING_UM} µm de diamètre, en verre aussi) a un **indice de
réfraction un peu plus faible**. La lumière qui touche la limite cœur-gaine sous un angle rasant
est **entièrement renvoyée** vers le cœur : c'est la **réflexion totale**. Un **revêtement**
plastique ({COATING_UM} µm), souvent une protection serrée ({BUFFER_UM} µm), puis le câble
(éléments de traction en **aramide**, gaine extérieure) protègent ce verre fragile.

{_fig(SECTION_FIGURE)}

## 1.2 Ce que transporte la fibre

La fibre transporte des **impulsions de lumière** : un **émetteur** (laser ou diode) dans le
module convertit le signal électrique, un **récepteur** (photodiode) le reconvertit au bout.
Aucun courant électrique ne circule : la fibre est **insensible aux parasites
électromagnétiques** et **isole électriquement** les deux extrémités. Les longueurs d'onde
utilisées (**850, 1 300, 1 310, 1 550 nm**) sont dans l'**infrarouge** : **invisibles**.

**Procédure professionnelle (à rédiger)** : nommer le support (verre), le principe (réflexion
totale dans le cœur), puis la conséquence utile pour le dossier (parasites, isolation, distance).

**Erreur fréquente** : écrire que la fibre « conduit le courant » ou qu'on « voit la lumière » au
bout d'une fibre en service.

**À l'écrit** : « la lumière reste dans le cœur par réflexion totale sur la gaine, d'indice plus
faible ».

**Repère rapide** : **cœur + gaine 125 µm · réflexion totale · lumière infrarouge invisible ·
aucun courant**. Exercices liés : {_ex("E15", "E17")}.
"""


def _types() -> str:
    return f"""**Objectifs** : distinguer monomode et multimode, identifier une fibre et choisir le
module qui tient la distance.

## 2.1 Multimode et monomode

- **Multimode** : cœur large (**50 ou 62,5 µm**), la lumière suit **plusieurs trajets** (modes)
  de longueurs différentes. Les impulsions s'étalent : c'est la **dispersion modale**, qui limite
  la **portée** à quelques centaines de mètres. Émetteurs bon marché à **850 nm**.
- **Monomode** : cœur fin (**environ 9 µm**), **un seul trajet** : pas de dispersion modale,
  portée de plusieurs **kilomètres**. Lasers à **1 310 ou 1 550 nm**, modules plus chers.

## 2.2 Types OM et OS : les reconnaître

{_kinds_table()}

Les couleurs sont un **usage courant** (TIA-598) : le **marquage imprimé** sur la gaine
(« 50/125 OM3 », « 9/125 OS2 ») fait foi ; un câble d'extérieur est souvent noir. L'OM5
(gaine vert anis) est un complément. Une liaison utilise **un seul type de fibre** de bout en
bout, jarretières comprises.

## 2.3 La portée dépend du module et de la fibre

La portée n'est **pas** une propriété de la fibre seule : elle est fixée par la **norme du
module** (IEEE 802.3) **sur ce type de fibre**. Valeurs de [PR14](/uaa/ampcr-pratique-pr14) :

{_reach_table()}

Un bilan de pertes favorable ne suffit pas : en multimode, au-delà de la portée, la dispersion
rend le lien instable même si la lumière arrive.

**Procédure professionnelle (à rédiger)** : relever le marquage → famille de fibre → débit voulu
→ module de la bonne famille → portée sur cette fibre ≥ longueur → bilan des pertes.

**Erreur fréquente** : choisir un module 850 nm pour une fibre jaune monomode ; se fier à la
seule couleur ; oublier la portée.

**À l'écrit** : « 10GBASE-SR sur OM3 : 300 m ≥ 180 m → portée respectée ; perte à calculer ».

**Repère rapide** : **multimode 850 nm, centaines de m · monomode 1 310/1 550 nm, km · le
marquage fait foi · portée ET budget**. Exercices liés : {_ex("E06", "E07", "E12")}.
"""


def _connectors() -> str:
    return f"""**Objectifs** : reconnaître les connecteurs et choisir des jarretières compatibles.

## 3.1 LC, SC (et ST)

{_connectors_table()}

{_fig(CONNECTORS_FIGURE)}

## 3.2 Polissage UPC ou APC

{_polish_table()}

La face d'un connecteur **APC** est inclinée : elle renvoie très peu de lumière vers l'émetteur.
On ne raccorde **jamais** un APC sur un UPC : il resterait un vide en biais, d'où une forte perte
et des faces abîmées. Une traversée (adaptateur) relie deux connecteurs **du même type**.

## 3.3 Jarretières

Une **jarretière** (cordon de brassage) relie un module à un tiroir, ou deux tiroirs. On la
choisit selon : les **connecteurs** des deux bouts (LC-LC, SC-LC…), le **polissage**, le **type
de fibre** (OM4 avec OM4, OS2 avec OS2), le **duplex** (deux fibres) ou le simplex, la longueur.

**Procédure professionnelle (à rédiger)** : relever les deux extrémités (connecteur, polissage,
fibre) → choisir la jarretière qui correspond → la nettoyer et l'inspecter avant de la brancher.

**Erreur fréquente** : jarretière OM1 orange sur un tiroir OM4 ; SC/UPC face à un SC/APC vert.

**À l'écrit** : « SC/APC côté opérateur, LC/UPC côté tiroir, OS2 : jarretière SC/APC – LC/UPC ».

**Repère rapide** : **LC = petit, SFP · SC = carré · APC vert ≠ UPC bleu · même fibre de bout en
bout**. Exercices liés : {_ex("E13", "E18")}.
"""


def _modules() -> str:
    return f"""**Objectifs** : choisir un module SFP ou SFP+ et relier correctement émission et
réception.

## 4.1 Modules SFP et SFP+

Un **module optique** (émetteur-récepteur) s'enfiche dans un port du switch. Le **SFP** travaille
à **1 Gb/s**, le **SFP+** à **10 Gb/s** ; leur face avant porte en général un **LC duplex**. Le
module fixe la **norme**, la **longueur d'onde**, le **type de fibre** et la **portée**.

{_modules_table()}

Règles : **le même type de module aux deux extrémités** ; un module de la **famille de la fibre**
(SR/SX multimode, LR/LX monomode) ; un module **reconnu par le switch** (certains refusent les
modules non référencés). Beaucoup de ports SFP+ acceptent aussi un SFP à 1 Gb/s ; un port SFP
n'accepte pas le 10 Gb/s : on vérifie la fiche du switch.

## 4.2 TX, RX et liaison duplex

Chaque module a une **émission (TX)** et une **réception (RX)** : une liaison utilise **deux
fibres**. La fibre partie du **TX de A** doit arriver sur le **RX de B**, et inversement : on dit
que la liaison est **croisée** (polarité A-B). Si le TX arrive sur le TX, **aucun récepteur ne
reçoit de lumière** : pas de lien, alors que les fibres sont bonnes.

{_fig(DUPLEX_FIGURE)}

**Correction d'une inversion** : croiser les deux fibres **à une seule extrémité** (le clip
duplex d'une jarretière LC s'ouvre pour inverser les deux fiches). Les croiser aux deux bouts
ramène le défaut.

**Procédure professionnelle (à rédiger)** : relever modules et ports → vérifier la paire de
modules, la famille de fibre et la portée → vérifier la polarité (TX → RX) → noter la polarité
dans le plan de brassage.

**Erreur fréquente** : remplacer un module neuf parce que le lien ne monte pas, alors que la
polarité est inversée.

**À l'écrit** : « LOS des deux côtés, fibres bonnes au photomètre → TX sur TX → croiser à une
extrémité ».

**Repère rapide** : **SFP 1 Gb/s · SFP+ 10 Gb/s · mêmes modules aux deux bouts · TX → RX**.
Exercices liés : {_ex("E06", "E08", "E12")}.
"""


def _losses() -> str:
    lr = rx_power_dbm(-2.1, 1.9)
    return f"""**Objectifs** : calculer la perte d'une liaison et vérifier la puissance reçue par un
module.

## 5.1 Pertes et atténuation

Le calcul est celui de [PR14](/uaa/ampcr-pratique-pr14) : **perte = longueur (km) × dB/km +
connecteurs + épissures**, avec au plus **{fr(attenuation_for("OM3", 850))} dB/km** en multimode
à 850 nm, **{fr(attenuation_for("OS2", 1310))} dB/km** en monomode OS2, **{fr(CONNECTOR_PAIR_DB, 2)} dB**
par paire de connecteurs, **{fr(SPLICE_DB)} dB** par épissure. Un connecteur **sale** ou abîmé,
une **courbure** trop serrée ou une épissure ratée ajoutent des pertes.

## 5.2 Puissance émise, puissance reçue

Le module affiche (fonction de surveillance des modules) sa **puissance émise** et sa
**puissance reçue**, en **dBm** (0 dBm = 1 mW). **Puissance reçue = puissance émise − perte** :
un module qui émet −2,1 dBm à travers 1,9 dB de pertes reçoit à l'autre bout {dbm_fr(lr)} dBm. La
perte d'**un sens** se lit donc : **émise d'un côté − reçue de l'autre**.

La fiche du module donne une **plage de réception** : au-dessus de la **sensibilité** et en
dessous du **maximum**. Trop faible, le récepteur commet des erreurs ou perd le lien ; trop fort
(module longue portée sur une liaison très courte), il **sature** : on ajoute l'atténuateur
prévu par la fiche ou on choisit un module adapté. Vers {dbm_fr(NO_LIGHT_DBM)} dBm et en dessous, il
ne voit **aucune lumière** (alarme **LOS**, souvent affichée −40 dBm).

{_fig(RX_FIGURE)}

**Procédure professionnelle (à rédiger)** : calculer la perte admissible → relever émise et
reçue des deux côtés → perte de chaque sens → comparer à la plage de la fiche → conclure.

**Erreur fréquente** : comparer une puissance en dBm à une perte en dB sans la soustraction ;
oublier que chaque sens a sa propre fibre.

**À l'écrit** : « A → B : −2,5 − (−10,8) = 8,3 dB > 1,85 dB admissibles → fibre A → B en
cause ».

**Repère rapide** : **reçue = émise − perte · plage de la fiche ({dbm_fr(LR_SPEC.sensitivity_dbm)} à
{dbm_fr(LR_SPEC.overload_dbm)} dBm dans l'exemple) · LOS = aucune lumière**. Exercices liés :
{_ex("E04", "E11")}.
"""


def _splicing() -> str:
    return f"""**Objectifs** : décrire le raccordement d'un câble optique et le brassage.

## 6.1 Épissure et pigtail

- **Épissure par fusion** : on dénude, on **clive** (coupe nette à 90°) les deux fibres, puis la
  **soudeuse** les aligne et les fond par un arc électrique. Perte très faible (**{fr(SPLICE_DB)} dB au
  plus**, souvent bien moins), sans réflexion. Un **manchon de protection** recouvre la soudure.
- **Épissure mécanique** : les fibres sont maintenues bout à bout dans un petit boîtier à gel ;
  dépannage ou petits volumes, perte plus élevée (complément).
- **Pigtail** : courte fibre munie d'un **connecteur posé et poli en usine**. On épisse chaque
  fibre du câble à un pigtail : le connecteur a la qualité de l'usine.

## 6.2 Tiroir optique et brassage

Le câble arrive dans un **tiroir optique** (panneau) : les épissures sont rangées dans des
**cassettes**, les pigtails sont branchés à l'arrière des **traversées**. Devant, on **brasse**
avec des **jarretières** vers les modules des switchs. Chaque élément compte dans le bilan :

{_fig(CHAIN_FIGURE)}

Pose de connecteurs « sur site » (à coller ou pré-polis) : possible, mais plus délicate ; le
pigtail épissé reste la solution courante en tiroir (complément).

**Procédure professionnelle (à rédiger)** : préparer le câble dans le tiroir → cliver → épisser
chaque fibre à un pigtail → protéger et ranger en cassette → étiqueter → nettoyer, inspecter,
mesurer.

**Erreur fréquente** : compter seulement la longueur de fibre dans le bilan, sans les connecteurs
et les épissures.

**À l'écrit** : « 2 traversées × {fr(CONNECTOR_PAIR_DB, 2)} + 2 épissures × {fr(SPLICE_DB)} + 0,8 km × 0,4 =
{fr(CHAIN_TOTAL_DB, 2)} dB ».

**Repère rapide** : **pigtail = connecteur d'usine · épissure par fusion ≤ {fr(SPLICE_DB)} dB · cassette
· jarretière**. Exercices liés : {_ex("E02", "E18")}.
"""


def _laying() -> str:
    rest, pull = min_bend_radius_mm(6, pulling=False), min_bend_radius_mm(6, pulling=True)
    return f"""**Objectifs** : poser un câble optique sans l'abîmer et préparer son contrôle.

## 7.1 Rayon de courbure et traction

Une fibre courbée trop serré **laisse fuir la lumière** (perte, surtout à 1 550 nm) et peut se
**fissurer** avec le temps. Repère d'installation courant (**convention du cours**, la fiche du
câble fait foi) : rayon de courbure au moins **{BEND_FACTOR_REST} × le diamètre du câble au repos** et
**{BEND_FACTOR_PULL} ×** pendant le **tirage**. Pour un câble de 6 mm : {rest:g} mm au repos, {pull:g} mm au
tirage. On tire par l'**élément de traction** (aramide), jamais par les fibres ni par la seule
gaine, sans dépasser la **tension** de la fiche.

## 7.2 Rangement et repérage

- **love de réserve** en grandes boucles, aux deux extrémités ;
- attaches **souples et non serrées** : un collier serré **écrase** le câble ;
- chemins séparés des câbles d'énergie pour la protection mécanique ;
- **étiquettes** aux deux bouts, plan de brassage et **polarité** notés.

## 7.3 Procédure de pose et de contrôle

{_fig(INSTALL_FIGURE)}

**Procédure professionnelle (à rédiger)** : les six étapes ci-dessus, avec les valeurs du
chantier (longueur, rayons, nombre de connecteurs et d'épissures, budget).

**Erreur fréquente** : boucles serrées dans le local technique ; câble tiré par la gaine ;
mesure oubliée « parce que le lien monte ».

**À l'écrit** : « câble de 8 mm : {min_bend_radius_mm(8, pulling=False):g} mm au repos, {min_bend_radius_mm(8, pulling=True):g} mm au tirage ;
love à 60 mm → non conforme ».

**Repère rapide** : **{BEND_FACTOR_REST} × Ø au repos · {BEND_FACTOR_PULL} × Ø au tirage · tirer par l'aramide ·
attaches non serrées**. Exercices liés : {_ex("E02", "E14")}.
"""


def _comparison() -> str:
    return f"""**Objectifs** : comparer la fibre au cuivre et au coaxial, et justifier un choix.

## 8.1 Tableau comparatif

{_comparison_table()}

## 8.2 Quand choisir la fibre

- **distance** : au-delà des **100 m** d'un canal cuivre ;
- **entre deux bâtiments** : la fibre n'établit **aucune liaison électrique** (terres
  différentes, foudre) ;
- **parasites forts** : postes à souder, moteurs, variateurs, haute tension, imagerie médicale ;
- **débit élevé** et évolution future (10 Gb/s et plus sur des centaines de mètres).

Le **cuivre** reste le bon choix pour un poste, un téléphone IP, une caméra alimentée en **PoE**,
à moins de 100 m dans un bâtiment : moins cher, robuste, raccordement simple. Le **coaxial** ne
sert plus au réseau informatique (vidéo, TV ; voir [PR16](/uaa/ampcr-pratique-pr16)).

**Procédure professionnelle (à rédiger)** : relever la distance, le site (un ou deux bâtiments),
l'environnement, le débit, l'alimentation → comparer → choisir et justifier, en citant les
inconvénients du choix.

**Erreur fréquente** : proposer un câble cuivre « blindé » pour 250 m ou entre deux bâtiments ;
présenter la fibre comme sans inconvénient.

**À l'écrit** : « 180 m entre deux bâtiments près d'une IRM → fibre (distance, isolation,
parasites) ; contrepartie : modules et raccordement plus chers ».

**Repère rapide** : **> 100 m, deux bâtiments, parasites forts → fibre · PoE et poste de travail →
cuivre**. Exercices liés : {_ex("E12", "E17")}.
"""


def _testing() -> str:
    end = OTDR_EXAMPLE.events[-1].position_m
    d = otdr_distance_m(4.9e-6)
    return f"""**Objectifs** : contrôler une liaison optique au niveau technicien : propreté,
photométrie, réflectométrie.

## 9.1 Connecteurs propres : inspecter, nettoyer, inspecter

Un grain de poussière sur un cœur de 9 µm suffit à **perdre plusieurs dB**, et la saleté passe
d'un connecteur à l'autre. Règle : **on inspecte avant de brancher**, à chaque fois, la fiche
**et** la traversée.

{_fig(CLEAN_FIGURE)}

## 9.2 Photométrie : mesurer la perte

On utilise une **source** (à la longueur d'onde de la liaison) et un **photomètre**
(wattmètre optique). On prend d'abord une **référence** (source + cordon de référence), puis on
mesure au bout de la liaison : **perte = référence − lecture**, fibre par fibre. Exemple :
référence −10,00 dBm, lecture −12,30 dBm → {fr(measured_loss_db(-10.0, -12.3), 2)} dB. On compare à la
**perte admissible** calculée (PR14). La mesure de **puissance reçue** sur un lien en service
(chapitre 5) est un contrôle rapide du même ordre.

## 9.3 Réflectométrie (OTDR) : localiser

Le **réflectomètre** envoie des impulsions dans **une** extrémité et mesure la lumière renvoyée
en fonction du temps, donc de la **distance** (la lumière fait l'aller-retour à environ
c / {fr(GROUP_INDEX, 3)} dans le verre : un écho reçu après 4,9 µs vient de {fr(d, 0)} m). On branche une
**bobine amorce** pour voir le premier connecteur. Sur la trace :

- la **pente** = affaiblissement linéique (dB/km) ;
- un **pic** suivi d'une petite marche = **connecteur** ;
- une **marche sans pic**, égale à 1 310 et 1 550 nm = **épissure** ;
- une marche sans pic **bien plus forte à 1 550 nm** = **courbure** trop serrée ;
- un pic puis **plus que du bruit** = **fin de fibre** ; avant la longueur prévue = **cassure**.

{_fig(OTDR_FIGURE)}

Dans cet exemple, la fin à {end:g} m correspond au tiroir B ({break_position_m(end, OTDR_EXAMPLE.launch_m):g} m de
liaison après l'amorce) : liaison complète, mais la courbure à 980 m est à reprendre.

Un **stylo laser rouge** (localisateur visuel, 650 nm) fait briller une cassure ou une courbure
sur quelques kilomètres ; il se manipule avec les mêmes précautions (complément).

**Procédure professionnelle (à rédiger)** : inspecter et nettoyer → photomètre (référence,
lecture, perte, comparaison au budget) → OTDR pour localiser un défaut → consigner.

**Erreur fréquente** : mesurer sans référence ; nettoyer sans inspecter ; oublier la bobine
amorce et lire la distance depuis l'appareil au lieu du tiroir.

**À l'écrit** : « référence − lecture = perte ; 5,80 dB > 2,74 dB → non conforme → inspection
puis OTDR ».

**Repère rapide** : **inspecter avant de brancher · perte = référence − lecture · pic =
connecteur · marche = épissure · plus fort à 1 550 = courbure · bruit = fin**. Exercices liés :
{_ex("E01", "E04", "E05", "E09", "E10")}.
"""


def _safety() -> str:
    return f"""**Objectifs** : travailler sans danger pour les yeux ni pour la peau.

## 10.1 Lumière laser invisible

Les modules et appareils de mesure émettent de l'**infrarouge invisible**. Un faisceau laser
peut léser la rétine **sans aucune sensation**. Règles :

- **ne jamais regarder** l'extrémité d'une fibre, d'une jarretière ou d'un module, même si on la
  croit éteinte ;
- vérifier l'absence de lumière au **photomètre** (ou par la puissance affichée), jamais à l'œil ;
- **capuchon** sur tout connecteur débranché ;
- n'inspecter une face qu'avec une **sonde d'inspection**, fibre déconnectée de toute source.

## 10.2 Éclats de fibre

Une chute de fibre est un **éclat de verre** très fin, presque invisible : il pénètre la peau ou
l'œil et peut être avalé. Règles :

- travailler sur un **tapis sombre**, avec des **lunettes** ;
- déposer chaque chute aussitôt dans un **récipient fermé et étiqueté** ;
- ramasser au **ruban adhésif**, jamais à la main ni en soufflant ;
- **ni manger ni boire** au poste, se **laver les mains** ;
- l'alcool isopropylique de nettoyage est **inflammable** : petites quantités, loin des flammes.

**Procédure professionnelle (à rédiger)** : avant d'intervenir, écrire ces consignes pour
l'équipe ; après, vérifier que le poste est propre et les chutes évacuées.

**Erreur fréquente** : regarder un connecteur « pour voir s'il y a de la lumière » ; balayer les
chutes à la main.

**À l'écrit** : « infrarouge invisible → ne jamais regarder → vérifier au photomètre ».

**Repère rapide** : **jamais l'œil · photomètre · capuchons · tapis sombre · récipient fermé ·
ruban adhésif**. Exercices liés : {_ex("E15", "E16")}.
"""


def _diagnosis() -> str:
    return f"""**Objectifs** : diagnostiquer par écrit une liaison optique qui ne fonctionne pas ou
mal.

## 11.1 Cinq causes à reconnaître

| Cause | Symptômes typiques | Correction |
|---|---|---|
| **Polarité inversée** | lien neuf ou rebrassé ; LOS des deux côtés ; chaque fibre bonne au photomètre | croiser les fibres à une seule extrémité |
| **Connecteur sale** | erreurs, puissance reçue trop basse d'un côté, perte excessive d'un sens | inspecter, nettoyer, réinspecter, remesurer |
| **Mauvais module** | modules différents aux deux bouts, module de la mauvaise famille, module refusé par le switch | même module adapté aux deux bouts |
| **Distance** | perte faible mais lien instable ; longueur supérieure à la portée du module sur cette fibre | fibre de meilleure catégorie, monomode, ou débit réduit |
| **Casse** | plus aucune lumière ; trace OTDR qui s'arrête avant la longueur prévue | localiser, épisser ou remplacer, remesurer |

## 11.2 Démarche

{_fig(DIAG_FIGURE)}

**Procédure professionnelle (à rédiger)** : les six étapes ci-dessus, chaque conclusion
justifiée par une **valeur** (puissance, perte, portée, position).

**Erreur fréquente** : changer les modules au hasard ; conclure à une casse sans mesurer chaque
fibre ; oublier de remesurer après la réparation.

**À l'écrit** : « émise normale, reçue LOS des deux côtés, fibres à 1,9 et 2,0 dB → polarité ».

**Repère rapide** : **relever → modules → polarité → connecteurs → mesurer → réparer et
consigner**. Exercices liés : {_ex("E03", "E08", "E10", "E11")}.
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
        "Cinq dossiers résolus pas à pas avec les règles du cours : lien inversé, connecteur sale, "
        "mauvais module, distance, casse. Chaque conclusion est justifiée par une valeur.\n\n" + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return """> **Regarder une fibre pour voir s'il y a de la lumière** : infrarouge invisible, danger pour
> l'œil ; on vérifie au photomètre.

> **Se fier à la seule couleur** d'une gaine : le marquage imprimé fait foi.

> **Mélanger multimode et monomode**, ou deux types de modules aux deux bouts.

> **Vérifier le budget en oubliant la portée** du module sur la fibre posée.

> **Raccorder un APC sur un UPC** : forte perte, faces abîmées.

> **Brancher sans inspecter** : un connecteur sale salit aussi celui d'en face.

> **Croiser les fibres aux deux extrémités** pour corriger une polarité : le défaut revient.

> **Plier ou serrer le câble** : rayon de courbure de 10 × le diamètre au repos, 20 × au tirage.

> **Lire une distance OTDR sans retirer la bobine amorce**.

> **Balayer les chutes de fibre à la main** ou manger au poste d'épissure.

> **Proposer du cuivre au-delà de 100 m** ou entre deux bâtiments.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (nettoyage d'un connecteur, pose et
contrôle, diagnostic), classements (puissance reçue, événements OTDR, compatibilité des modules,
identification d'une fibre, cause d'une panne), documents (photométrie, trace OTDR, relevé des
modules, choix d'un module, jarretières, chantier) et rédactions (sécurité laser, éclats, fibre ou
cuivre, pigtail et épissure). Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute
réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR17_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR17_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (relevés et fiches fictifs). Une calculatrice n'est pas
nécessaire. **Aucune correction n'est visible pendant la passation** ; tes réponses sont
enregistrées au fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème
analytique** de la question (critères et points), puis tu vois ta note sur
{EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **diagnostic justifié** par les mesures, le **choix argumenté**,
la **procédure** et la **sécurité** — pas la récitation de sigles. Un résultat arrondi
raisonnablement ou une autre formulation juste est accepté.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Principe** : cœur d'indice plus élevé que la gaine (125 µm) → réflexion totale ; lumière
  infrarouge invisible ; aucun courant.
- **Multimode** : cœur 50 / 62,5 µm, 850 nm, centaines de m (dispersion modale) ; OM1/OM2
  orange, OM3/OM4 aqua (OM4 parfois violet). **Monomode** : ≈ 9 µm, 1 310 / 1 550 nm, km ; OS2
  jaune. Le marquage fait foi.
- **Portée = module + fibre** : 10GBASE-SR 300 m OM3, 400 m OM4 ; 10GBASE-LR 10 km OS2 ;
  1000BASE-SX 275 m OM1, 550 m OM2 ; 1000BASE-LX 5 km.
- **Connecteurs** : LC 1,25 mm (SFP), SC 2,5 mm ; APC vert ≠ UPC bleu.
- **Modules** : SFP 1 Gb/s, SFP+ 10 Gb/s ; mêmes modules aux deux bouts ; TX → RX.
- **Pertes** : km × dB/km + {fr(CONNECTOR_PAIR_DB, 2)} dB par connecteur + {fr(SPLICE_DB)} dB par épissure ;
  reçue = émise − perte ; plage de la fiche ; LOS ≤ {dbm_fr(NO_LIGHT_DBM)} dBm.
- **Raccordement** : pigtail épissé par fusion dans une cassette du tiroir ; jarretières.
- **Pose** : rayon ≥ {BEND_FACTOR_REST} × Ø au repos, {BEND_FACTOR_PULL} × Ø au tirage ; tirer par l'aramide ; attaches non
  serrées ; étiquettes.
- **Contrôle** : inspecter, nettoyer, inspecter ; perte = référence − lecture ; OTDR : pic =
  connecteur, marche = épissure, plus fort à 1 550 nm = courbure, bruit = fin ou cassure.
- **Sécurité** : jamais l'œil, photomètre, capuchons ; tapis sombre, récipient fermé, ruban
  adhésif, ni manger ni boire.

## Glossaire des termes employés

- **APC / UPC** : polissage de la face d'un connecteur, incliné à 8° (APC) ou droit (UPC).
- **Bobine amorce** : fibre de quelques centaines de mètres placée entre le réflectomètre et la
  liaison pour voir le premier connecteur.
- **Cœur / gaine** : partie centrale qui guide la lumière / verre d'indice plus faible autour.
- **Dispersion modale** : étalement des impulsions en multimode, qui limite la portée.
- **Épissure par fusion** : soudure de deux fibres bout à bout par arc électrique.
- **Jarretière** : cordon optique de brassage.
- **LOS** : perte de signal (aucune lumière reçue).
- **Module optique (SFP, SFP+)** : émetteur-récepteur enfichable d'un port de switch.
- **OTDR (réflectomètre)** : appareil qui localise les événements d'une fibre par la lumière
  renvoyée.
- **Photomètre** : appareil qui mesure une puissance optique (dBm) ; avec une source, il mesure
  la perte d'une liaison.
- **Pigtail** : courte fibre munie d'un connecteur posé en usine, à épisser.
- **TX / RX** : émission / réception d'un module.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « La fibre optique et ses caractéristiques : support
  d'information, débit binaire, longueur d'un tronçon, notion d'atténuation, connexion,
  avantages et inconvénients, etc. » (AP-21) et « Comparaison entre la fibre optique et les
  autres types de câbles » (AP-22). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **IEEE 802.3** : 1000BASE-SX/LX (clause 38), 10GBASE-SR/LR (clause 52) : longueurs d'onde,
  types de fibre et portées.
- **TIA-568** (fibre câblée : 3,5 et 1,5 dB/km en multimode, 0,75 dB par paire de connecteurs,
  0,3 dB par épissure) et **ISO/IEC 11801** (OM1 à OM4, OS1, OS2 ; OS2 0,4 dB/km).
- **TIA-598** : code couleur habituel des gaines et des connecteurs.
- **IEC 60825** : sécurité des appareils à laser (classes, précautions).
- **IEC 61300-3-35** : inspection des faces de connecteurs ; **IEC 61280-4** : mesure de
  l'affaiblissement des liaisons installées (photométrie).

Les valeurs sont celles de {WRITTEN_AT} ; les normes évoluent et les fabricants précisent
leurs propres valeurs : **la fiche technique et les normes en vigueur font foi**. Les tableaux,
coupes, polarités, chaînes de raccordement, traces et procédures du cours sont **produits par
programme** depuis des données **vérifiées par des tests automatiques** ; aucun schéma n'est
tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite la fibre, ses caractéristiques et sa comparaison avec les autres câbles. Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- les modules SFP/SFP+, la polarité TX/RX, la plage de réception et la saturation ;
- la photométrie, la lecture d'une trace OTDR (dont la distinction courbure / épissure par les
  deux longueurs d'onde) et le stylo laser rouge ;
- le code couleur TIA-598, l'OM5, l'épissure mécanique et les connecteurs posés sur site ;
- le rayon de courbure « 10 × / 20 × le diamètre » : **convention du cours**, la fiche du câble
  fait foi.

## Supports fictifs

Les relevés, fiches de modules, rapports de mesure, traces, chantiers et entreprises de ce cours
sont **fictifs** et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel.
Aucune n'est une question officielle ou déjà posée par le Jury. Pour un cas réel, on utilise la
fiche du fabricant et un appareil de mesure.
"""


def pr17_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR17 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR17 — 1. Principe : la lumière guidée dans le cœur et la gaine", _principle()),
        ("PR17 — 2. Monomode ou multimode : types OM et OS, portée", _types()),
        ("PR17 — 3. Connecteurs LC et SC, polissage UPC ou APC, jarretières", _connectors()),
        ("PR17 — 4. Modules SFP et SFP+, émission et réception (TX/RX), duplex", _modules()),
        ("PR17 — 5. Pertes, atténuation et puissance reçue", _losses()),
        ("PR17 — 6. Raccordement : épissure, pigtail, tiroir et brassage", _splicing()),
        ("PR17 — 7. Pose : rayon de courbure, traction et rangement", _laying()),
        ("PR17 — 8. Fibre, cuivre ou coaxial : comparer et choisir", _comparison()),
        ("PR17 — 9. Contrôle : propreté, photométrie et réflectométrie", _testing()),
        ("PR17 — 10. Sécurité : lumière laser et éclats de fibre", _safety()),
        ("PR17 — 11. Diagnostic d'une liaison optique", _diagnosis()),
        ("PR17 — Exemples : cinq cas résolus", _examples()),
        ("PR17 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR17 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR17 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR17 — Fiche mémo et glossaire", _memo()),
        ("PR17 — Sources et compléments pédagogiques", _sources()),
    ]
