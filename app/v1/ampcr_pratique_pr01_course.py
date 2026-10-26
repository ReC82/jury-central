"""Cours PR01 « Structure d'un PC et identification des composants » — parcours AMPCR pratique
écrite (ticket #202).

Matière : intégralement celle du ticket #202 (boîtier et formats ATX/microATX/Mini-ITX, carte
mère, socket, chipset, VRM, processeur et refroidissement, RAM DIMM/SO-DIMM et ROM,
BIOS/UEFI/POST, stockage HDD/SSD SATA/NVMe, bloc d'alimentation et connecteurs ATX/EPS/PCIe,
carte graphique, ports internes et externes, périphériques d'entrée/sortie et pilotes,
compatibilités ; démarche écrite d'identification, d'inventaire, de choix compatible et de
précautions ESD), découpée en blocs titrés (le titre pilote le type de carte, `app.card_kind` :
aucun titre de bloc théorique ne contient « examen », « source », « exemple », « exercice »,
« méthode », « piège », « attention » ni « mémo »). Données et schémas :
`app.v1.ampcr_pratique_pr01_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr01_bank`. Mise en forme partagée avec les autres cours pratiques.
"""

from html import escape

from app.v1.ampcr_pratique_pr01_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr01_figures import (
    AUDIO_JACKS,
    BOARD_FIGURE,
    BOARD_PARTS,
    CASE2_INSTALLED_GIB,
    CASE2_SLOTS,
    CASE_FIGURE,
    CASE_PARTS,
    COMPATIBILITY_FIGURE,
    DATA_PATH_FIGURE,
    DIMM_LENGTH_MM,
    FORM_FACTOR_FIGURE,
    FORM_FACTORS,
    IDENTIFY_FIGURE,
    INVENTORY_DISKS,
    MEMORY_FIGURE,
    MEMORY_MODULES,
    PCIE_GENERATIONS,
    POWER_CONNECTORS,
    REAR_PANEL_FIGURE,
    REAR_PORTS,
    SATA3_GBITS,
    SATA3_USEFUL_MBYTES,
    SODIMM_LENGTH_MM,
    USB_SPEEDS,
    board_fits_case,
    fr_number,
    lsblk_lines,
    memory_cim_lines,
    pcie_lane_gbytes,
    pcie_link_gbytes,
)
from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req

PR01_TITLE = "Structure d'un PC et identification des composants"
PR01_SLUG = "ampcr-pratique-pr01"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr01") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _usb(gbits: float) -> str:
    return f"{int(gbits * 1000)} Mbit/s" if gbits < 1 else f"{gbits:g} Gbit/s"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _form_table() -> str:
    rows = "\n".join(
        f"| {f.name} | {f.width_mm} × {f.depth_mm} mm | {f.max_slots} | {f.note} |" for f in FORM_FACTORS
    )
    return (
        "| Format | Dimensions maximales | Emplacements d'extension (au plus) | Usage courant |\n"
        "|---|---|---|---|\n" + rows
    )


def _fit_table() -> str:
    names = [f.name for f in FORM_FACTORS]
    header = "| Carte ↓ / boîtier → | " + " | ".join(names) + " |\n|---|" + "---|" * len(names)
    rows = "\n".join(
        f"| {board} | " + " | ".join("oui" if board_fits_case(board, case) else "non" for case in names) + " |"
        for board in names
    )
    return header + "\n" + rows


def _board_legend() -> str:
    rows = "\n".join(f"| {n} | {p.label} | {p.detail} |" for p, n in BOARD_PARTS)
    return "| Repère | Élément | Comment le reconnaître |\n|---|---|---|\n" + rows


def _case_legend() -> str:
    rows = "\n".join(f"| {n} | {p.label} |" for p, n in CASE_PARTS)
    return "| Repère | Élément |\n|---|---|\n" + rows


def _memory_table() -> str:
    rows = "\n".join(f"| {m.generation} | {m.form} | {m.contacts} | {m.voltage} |" for m in MEMORY_MODULES)
    return "| Génération | Format | Contacts | Tension nominale |\n|---|---|---|---|\n" + rows


def _pcie_table() -> str:
    rows = "\n".join(
        f"| PCIe {version} | {gt} GT/s | ≈ {fr_number(pcie_lane_gbytes(gt), 2)} Go/s | "
        f"≈ {fr_number(pcie_link_gbytes(gt, 4))} Go/s | ≈ {fr_number(pcie_link_gbytes(gt, 16))} Go/s |"
        for version, gt in PCIE_GENERATIONS
    )
    return (
        "| Génération | Transfert par ligne | Débit utile par ligne (un sens) | x4 | x16 |\n"
        "|---|---|---|---|---|\n" + rows
    )


def _usb_table() -> str:
    rows = "\n".join(f"| {name} | {old} | {_usb(speed)} | {conn} |" for name, old, speed, conn in USB_SPEEDS)
    return "| Nom actuel | Ancien nom courant | Débit maximal | Connecteurs |\n|---|---|---|---|\n" + rows


def _rear_table() -> str:
    rows = "\n".join(f"| {n} | {port} | {use} | {look} |" for n, port, use, look in REAR_PORTS)
    return "| Repère | Port | Ce qu'on y branche | Comment le reconnaître |\n|---|---|---|---|\n" + rows


def _power_table() -> str:
    rows = "\n".join(f"| {name} | {where} | {use} |" for name, where, use in POWER_CONNECTORS)
    return "| Connecteur | Côté | Rôle |\n|---|---|---|\n" + rows


def _fits_text(board: str) -> str:
    return "y entre" if board_fits_case(board, "microATX") else "n'y entre pas"


def _audio_list() -> str:
    return " ; ".join(f"**{color}** : {use}" for color, use in AUDIO_JACKS)


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Pour la partie matériel, on te remet un schéma, une photo, une fiche technique, un
inventaire ou la description d'un PC, et tu dois, sur papier :

1. **identifier** les composants et les connecteurs (sur un schéma, une photo ou une
   description) et les **nommer exactement** ;
2. **expliquer leur rôle** et **comment ils sont reliés** (cheminement des données) ;
3. **interpréter un inventaire** (fiche, relevé de commande, écran du firmware) et un
   **symptôme** simple ;
4. **sélectionner une pièce compatible** et justifier chaque critère ;
5. **justifier le montage** et les **précautions** (électricité statique, coupure secteur).

## Exigences officielles travaillées dans ce cours

{_req("AP-01")}
{_req("AP-02")}
{_req("AP-05")}
{_req("AP-07")}
{_req("AP-17")}

Ce cours mobilise aussi, au niveau de l'identification : les branchements (AP-06) et
l'alimentation (AP-04), détaillés en **PR02** ; le stockage (AP-03), détaillé en **PR05** ; le
montage (AP-14), détaillé en **PR03**. Le diagnostic des pannes est traité en
[PR06](/uaa/ampcr-pratique-pr06).

Complément pédagogique (hors liste officielle des pp. 5-6, signalé comme tel) :

{_req("AP-C02")}

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC01 Architecture générale d'un PC](/uaa/ampcr-mc01),
[MC02 Carte mère, formats et connectiques](/uaa/ampcr-mc02),
[MC03 CPU et mémoire RAM](/uaa/ampcr-mc03), [MC04 Stockage](/uaa/ampcr-mc04),
[MC07 BIOS, UEFI, POST et démarrage](/uaa/ampcr-mc07) et
[MC12 Pilotes, périphériques et logiciels](/uaa/ampcr-mc12). Ce cours-ci est **pratique** :
schémas à repères, fiches, inventaires, choix de pièces et réponses rédigées, comme dans un
dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, ce qu'on
attend **à l'écrit** et un **repère rapide**. Étudie ensuite les **quatre cas résolus**, fais
les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner », correction après
envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** le plan de carte mère, le boîtier, le panneau arrière, les fiches produits et
> les relevés de ce cours sont des **supports fictifs** construits pour s'entraîner : ils ne
> décrivent aucun produit réel, et seule la fiche du fabricant fait foi pour un vrai matériel.
> Les valeurs normalisées (dimensions des formats, contacts des barrettes, débits PCIe, USB et
> SATA) viennent des spécifications citées en fin de cours. Aucun exercice n'est une question
> officielle ni une question déjà posée par le Jury.
"""


def _structure() -> str:
    return f"""**Objectifs** : distinguer unité centrale et périphériques ; situer chaque composant
interne ; décrire le trajet des données.

## 1.1 Unité centrale, composants internes, périphériques

- L'**unité centrale** est le boîtier et ce qu'il contient : carte mère, processeur, mémoire
  vive, stockage, carte graphique éventuelle, bloc d'alimentation, refroidissement.
- Les **périphériques** sont reliés à l'unité centrale par un port : clavier, souris, écran,
  imprimante, scanner, disque externe, casque… (chapitre 11).
- La **carte mère** relie tout : c'est sur elle que se branchent le processeur, la mémoire, les
  cartes d'extension, les unités de stockage et les câbles de façade.

{_fig(IDENTIFY_FIGURE)}

## 1.2 Le cheminement des données

{_fig(DATA_PATH_FIGURE, wide=True)}

Le **processeur** exécute les programmes ; il travaille sur des données placées en **mémoire
vive**. Les données viennent du **stockage** (SSD, disque dur), d'un **périphérique** ou du
**réseau**, et les résultats repartent vers l'**écran** (par la carte graphique ou la partie
graphique du processeur), le stockage ou un périphérique.

- **Liaisons directes au processeur** (les plus rapides) : la mémoire vive (canaux DDR), le
  slot PCIe x16 principal (carte graphique) et, souvent, le premier emplacement M.2.
- **Liaisons par le chipset** : en général les ports SATA, une partie des ports USB, le réseau,
  l'audio, des emplacements PCIe et M.2 supplémentaires. Le chipset est relié au processeur par
  une seule liaison, **partagée** par tous ces périphériques.
- **Le bloc d'alimentation** alimente tout mais ne transporte aucune donnée.

**À l'écrit**, un trajet se décrit composant par composant, avec la liaison utilisée : « le
fichier est lu sur le SSD NVMe, passe par la liaison PCIe jusqu'au processeur, est copié en
mémoire vive… ». Le manuel de la carte (schéma-bloc, tableau des ports) dit quels ports
dépendent du processeur ou du chipset.

**Repère rapide** : processeur = calcul ; RAM = travail en cours (volatile) ; stockage =
conservation ; carte mère = liaisons ; chipset = entrées-sorties secondaires ; bloc =
énergie.
"""


def _case_and_forms() -> str:
    return f"""**Objectifs** : reconnaître les formats de carte mère et de boîtier, vérifier qu'une carte
entre dans un boîtier, nommer les éléments d'une tour.

## 2.1 Les formats de carte mère

{_fig(FORM_FACTOR_FIGURE, wide=True)}

{_form_table()}

Les trois formats partagent la position de la **plaque d'E/S arrière** et des fixations de
référence : une carte **plus petite** entre dans un boîtier prévu pour un format **plus grand**,
jamais l'inverse.

{_fit_table()}

- Le **nombre d'emplacements d'extension** suit le format : une carte Mini-ITX n'en a qu'un ;
  une carte graphique épaisse peut masquer l'emplacement voisin.
- Le **bloc d'alimentation** a aussi un format : **ATX** dans la plupart des tours, **SFX** dans
  certains petits boîtiers (la fiche du boîtier l'indique).

## 2.2 L'intérieur d'une tour

{_fig(CASE_FIGURE, wide=True)}

{_case_legend()}

- **Flux d'air** : l'air frais entre par la façade (ventilateurs d'entrée) et sort à l'arrière
  ou par le haut (extraction) ; un flux inversé ou obstrué fait chauffer les composants.
- **Limites du boîtier** à relever sur sa fiche : formats de carte mère acceptés, **longueur
  maximale de la carte graphique**, **hauteur maximale du ventirad**, format du bloc, nombre de
  baies 3,5" et 2,5", ports de façade.

**À l'écrit** : « la carte ATX (305 × 244 mm) ne peut pas être montée dans ce boîtier, qui
n'accepte que le microATX (244 × 244 mm au plus) » — une réponse chiffrée et justifiée.
"""


def _motherboard() -> str:
    return f"""**Objectifs** : identifier les éléments d'une carte mère sur un plan ou une description ;
expliquer le rôle du socket, du chipset et du VRM.

## 3.1 Plan d'une carte mère ATX

{_fig(BOARD_FIGURE, wide=True)}

{_board_legend()}

## 3.2 Socket, chipset et VRM

- **Socket** : le support du processeur. Il fixe la **plateforme** : un processeur ne s'installe
  que dans le socket prévu pour lui. Deux familles : **LGA** (les broches sont sur la carte mère,
  le processeur a des pastilles) et **PGA** (les broches sont sous le processeur). Exemples
  courants : AMD **AM4** (PGA, mémoire DDR4), AMD **AM5** (LGA, DDR5 uniquement), Intel
  **LGA1700** (DDR4 ou DDR5 selon la carte mère), Intel **LGA1851** (DDR5).
- **Même socket ne veut pas dire compatibilité garantie** : la **liste des processeurs pris en
  charge** du fabricant de la carte indique les modèles acceptés et la **version de firmware**
  minimale.
- **Chipset** : la puce (sous un radiateur plat) qui gère une partie des entrées-sorties
  (SATA, USB, réseau, audio, PCIe et M.2 supplémentaires). Sa **gamme** fixe le nombre de ports et
  certaines fonctions ; il est relié au processeur par une liaison dédiée.
- **VRM** (étage d'alimentation du processeur) : selfs, transistors et condensateurs autour du
  socket, souvent sous radiateur. Il transforme le **+12 V** du connecteur **EPS** en tension
  basse (de l'ordre de 1 V) adaptée au processeur. Un VRM mal refroidi limite les performances.

## 3.3 Emplacements et connecteurs de la carte

- **Emplacements mémoire DIMM** (chapitre 5), **socket** et **EPS** autour du processeur.
- **PCIe** : un emplacement se décrit par sa **taille mécanique** (x1, x4, x16) et par ses
  **lignes câblées** (« x16 mécanique, x4 électrique ») ; une carte x1 fonctionne dans un slot
  plus long ; le PCIe est **rétrocompatible** entre générations, au débit de la plus ancienne.

{_pcie_table()}

- **M.2** : emplacement plat pour SSD (ou carte Wi-Fi). Il se décrit par sa **clé** (M pour les
  SSD, E pour le Wi-Fi), son **interface** (NVMe sur PCIe, SATA, ou les deux) et les
  **longueurs** acceptées : **2280** = 22 mm de large, 80 mm de long (aussi 2242, 2260, 22110).
- **SATA** : connecteurs de données à 7 contacts, en forme de L, sur le bord de la carte.
- **Connecteurs internes** : **USB 2.0** (9 broches) et **USB 3.x** (19 broches) pour les ports
  de façade, **USB-C de façade** sur les cartes récentes, **HD_AUDIO** (prises audio de façade),
  ventilateurs (**CPU_FAN**, 4 broches : la quatrième règle la vitesse), **connecteur de
  façade** (bouton, reset, voyants : brochage dans le manuel), **pile CMOS**, **puce du
  firmware**.

**À l'écrit** : nomme le connecteur exactement (« connecteur interne USB 3.x 19 broches ») et
dis à quoi il est relié (« au câble des ports USB de la façade »).
"""


def _cpu() -> str:
    return """**Objectifs** : décrire le rôle du processeur et de son refroidissement ; vérifier un
ventirad et un processeur compatibles.

## 4.1 Le processeur

- Il **exécute les instructions** des programmes. Ses caractéristiques utiles à l'écrit :
  **socket**, nombre de **cœurs**, **fréquence**, **puissance thermique** indiquée par le
  fabricant (en watts), **mémoire prise en charge** (DDR4, DDR5), présence d'une **partie
  graphique intégrée**.
- Il contient le **contrôleur mémoire** (relié directement aux barrettes) et les **lignes PCIe**
  principales, ainsi qu'une petite mémoire très rapide, le **cache** (volatile).
- **Partie graphique intégrée** : elle permet d'utiliser les sorties vidéo de la carte mère sans
  carte graphique. **Certains processeurs n'en ont pas** (par exemple les modèles Intel à
  suffixe F) : sans carte graphique, un tel PC n'affiche rien. La fiche du fabricant fait foi.

## 4.2 Le refroidissement

- **Ventirad** : radiateur + ventilateur, fixé sur le processeur ; ou **watercooling** tout-en-un
  (pompe, radiateur, ventilateurs).
- **Pâte thermique** : couche fine entre le processeur et le radiateur, qui comble les
  micro-vides ; on la **renouvelle** à chaque démontage du ventirad.
- **Compatibilité d'un ventirad** : **socket** pris en charge (kit de fixation), **puissance
  dissipée** au moins égale à la puissance thermique du processeur, **hauteur** inférieure à la
  hauteur maximale du boîtier, dégagement autour des barrettes de RAM.
- Le ventilateur se branche sur **CPU_FAN** : sans lui, de nombreuses cartes signalent une
  erreur au démarrage.
- Sans refroidissement suffisant, le processeur **baisse sa fréquence** pour se protéger, puis
  provoque un **arrêt de protection** (diagnostic : cours PR06).

**À l'écrit** : « V1 convient : socket AM5 pris en charge, 150 W dissipés pour 105 W, 158 mm
pour 160 mm au plus » — chaque critère avec sa valeur.
"""


def _memory() -> str:
    return f"""**Objectifs** : distinguer RAM, ROM et stockage ; reconnaître DIMM et SO-DIMM ; choisir une
barrette compatible.

## 5.1 Volatile ou non : trois familles à ne pas confondre

| Mémoire | Volatile ? | Contenu | Exemples |
|---|---|---|---|
| **Mémoire vive (RAM)** | oui : vidée à l'extinction | programmes et données en cours d'utilisation | barrettes DDR4/DDR5, cache du processeur, mémoire GDDR de la carte graphique |
| **Mémoire du firmware (ROM)** | non | le firmware UEFI/BIOS de la carte mère | puce flash de la carte mère |
| **Stockage de masse** | non | système d'exploitation, programmes, fichiers | SSD, disque dur, clé USB |

- **ROM** (mémoire morte) désigne historiquement une mémoire **en lecture seule**. Le firmware de
  la carte mère est aujourd'hui dans une **mémoire flash réinscriptible** (on peut le mettre à
  jour), qu'on appelle encore souvent « ROM » : elle n'est pas modifiée en usage normal.
- **La ROM n'est pas du stockage** : elle ne contient ni le système ni les fichiers. Un SSD
  utilise aussi de la mémoire flash, mais c'est une **unité de stockage**.
- **Plus de RAM** permet de garder plus de programmes ouverts sans ralentissement ; elle ne
  remplace pas le stockage.

## 5.2 Barrettes DIMM et SO-DIMM

{_fig(MEMORY_FIGURE, wide=True)}

{_memory_table()}

- **DIMM** ({fr_number(DIMM_LENGTH_MM, 2)} mm) pour les PC de bureau ; **SO-DIMM** (environ
  {fr_number(SODIMM_LENGTH_MM)} mm) pour les portables et mini-PC ; certaines machines ont la mémoire
  **soudée** (non extensible).
- **Génération** : DDR3, DDR4 et DDR5 ont une **encoche-détrompeur** à des endroits différents et
  des tensions différentes : **non interchangeables**. Même nombre de contacts (DDR4 et DDR5
  DIMM : 288) ne veut pas dire compatible.
- **Fréquence** (ex. DDR5-4800, DDR5-5600) : une barrette plus rapide fonctionne en général à la
  vitesse la plus basse commune ; mélanger des barrettes différentes peut poser problème : la
  **liste de compatibilité** de la carte fait foi.
- **Capacité maximale** : par emplacement et au total (fiche de la carte ou du portable).
- **Double canal** : avec deux barrettes, le manuel indique les emplacements à utiliser
  (souvent A2 et B2) pour qu'elles travaillent en parallèle.
- **ECC** : mémoire qui corrige certaines erreurs, pour serveurs et stations de travail ; il faut
  un processeur **et** une carte qui la prennent en charge.

**À l'écrit** : « la barrette C convient : SO-DIMM, DDR4, 8 Go, sous la capacité maximale par
emplacement » — format, génération, capacité, puis précautions.
"""


def _firmware() -> str:
    return """**Objectifs** : expliquer le rôle du firmware, du POST et de la pile CMOS ; répondre aux
questions courantes d'un client.

## 6.1 BIOS et UEFI

- Le **firmware** est le programme de la carte mère qui s'exécute **avant** le système
  d'exploitation : il teste le matériel, permet les réglages et lance le démarrage. Il est
  enregistré dans la **puce flash** de la carte (la « ROM »).
- **BIOS** est l'ancien firmware des PC ; **UEFI** est son successeur : interface graphique,
  démarrage sur disques **GPT** (au-delà de 2 To), **démarrage sécurisé** (Secure Boot). Beaucoup
  de techniciens disent encore « le BIOS » pour l'écran de configuration UEFI. Le mode **CSM**
  émule l'ancien démarrage.
- **Mise à jour du firmware** : elle ajoute la prise en charge de nouveaux processeurs ou
  corrige des défauts ; elle **ne touche pas au disque** mais une **coupure pendant la mise à
  jour** peut rendre la carte inutilisable ; les réglages reviennent souvent aux valeurs par
  défaut.

## 6.2 Le POST

Le **POST** (autotest à la mise sous tension) vérifie le processeur, la mémoire et l'affichage
avant de lire les réglages et de chercher une unité de démarrage. Une erreur au POST se signale
par des **bips**, des **LED** ou un **code** dont la signification dépend du fabricant : le
**manuel** fait foi (diagnostic détaillé : [PR06](/uaa/ampcr-pratique-pr06)).

## 6.3 La pile CMOS

- **Pile bouton** (3 V) de la carte : elle alimente l'**horloge** quand le PC est débranché et,
  sur certaines cartes, la mémoire des **réglages**.
- **Pile usée** : la date et l'heure se réinitialisent à chaque démarrage ; on la remplace par le
  même modèle, PC débranché, puis on règle date et heure.
- **Effacer le CMOS** (cavalier ou bouton CLR_CMOS, selon le manuel) remet les **réglages** du
  firmware par défaut ; cela n'efface **aucune donnée** du disque.

**À l'écrit** : distingue toujours « réglages du firmware » (carte mère) et « données »
(disque).
"""


def _storage() -> str:
    return f"""**Objectifs** : reconnaître les unités de stockage et leurs interfaces ; choisir un SSD
compatible (le partitionnement et le formatage sont traités en PR05).

## 7.1 Les unités et leurs interfaces

| Unité | Format | Interface | À retenir |
|---|---|---|---|
| Disque dur (HDD) | 3,5" (bureau), 2,5" (portable) | SATA | plateaux en rotation (5 400 ou 7 200 tr/min) : grande capacité, lent, sensible aux chocs |
| SSD SATA | 2,5" | SATA | sans pièce mobile ; limité par la liaison SATA |
| SSD M.2 SATA | module M.2 (souvent clé B+M) | SATA | même débit qu'un SSD SATA 2,5" |
| SSD M.2 NVMe | module M.2 (clé M) | PCIe (protocole NVMe) | le plus rapide ; exige un emplacement M.2 qui accepte le NVMe |

- **SATA** {SATA3_GBITS} Gbit/s : environ **{SATA3_USEFUL_MBYTES} Mo/s utiles** au plus. Un SSD ou un
  disque SATA a **deux câbles** : données (7 contacts, vers la carte mère) et alimentation
  (15 contacts, vers le bloc).
- **NVMe** : le SSD est relié en **PCIe** (souvent x4) : PCIe 3.0 x4 ≈ {fr_number(pcie_link_gbytes(8, 4))} Go/s,
  PCIe 4.0 x4 ≈ {fr_number(pcie_link_gbytes(16, 4))} Go/s (débits théoriques de l'interface ; la fiche du
  SSD donne son débit réel).
- **Piège de compatibilité** : un SSD M.2 **SATA** s'enfiche souvent dans un emplacement M.2
  **NVMe seul**, mais n'y est **pas détecté**. Sur certaines cartes, utiliser un M.2 en mode SATA
  **désactive un port SATA** : le manuel le précise.

## 7.2 Lire un inventaire de disques

{_console(*lsblk_lines((INVENTORY_DISKS[0], INVENTORY_DISKS[2])))}

- **TRAN** : interface (sata, nvme, usb) ; **ROTA** : 1 = disque à plateaux, 0 = sans pièce
  mobile.
- **Go ou Gio ?** Le fabricant compte en unités **décimales** (1 To = 10¹² octets) ; les outils
  système comptent souvent en unités **binaires** (1T = 1024⁴ octets) : un disque de 2 To
  s'affiche « 1.8T », un SSD de 1 To « 931.3G ». **Ce n'est pas une panne.**
- Sous Windows : **Gestion des disques**, Gestionnaire de périphériques, ou PowerShell
  `Get-PhysicalDisk` (type de média et type de bus).

**À l'écrit** : « nvme0n1 est un SSD NVMe sur M.2 (PCIe) : c'est l'unité la plus rapide, on y
installe le système ».
"""


def _power_gpu() -> str:
    return f"""**Objectifs** : reconnaître les connecteurs du bloc d'alimentation (le dimensionnement et
la sécurité de l'alimentation sont traités en PR02) ; vérifier qu'une carte graphique peut être
installée.

## 8.1 Les connecteurs du bloc d'alimentation

{_power_table()}

- Connecteurs **sécables** : ATX **20+4**, EPS **4+4**, PCIe **6+2** ; une carte qui prévoit
  24 ou 8 broches doit recevoir toutes ses broches.
- **EPS 8 broches et PCIe 8 broches se ressemblent** mais **ne sont pas interchangeables**
  (détrompage différent) : ne jamais forcer.
- Certaines cartes graphiques récentes utilisent un connecteur **16 broches (12VHPWR /
  12V-2x6)**, à enfoncer complètement.
- **Bloc modulaire** : les câbles se branchent sur le bloc ; on n'utilise **que les câbles
  d'origine du bloc** (le brochage côté bloc n'est pas normalisé).

## 9.1 La carte graphique

- Elle calcule l'affichage et pilote l'écran ; elle a sa **propre mémoire** (GDDR, volatile).
- Elle se monte dans le slot **PCIe x16** relié au processeur ; l'emplacement fournit au plus
  **75 W**, au-delà elle reçoit des connecteurs **PCIe 6 ou 8 broches** (ou 16 broches) du bloc.
- **À vérifier avant achat** : slot PCIe x16 libre (la génération importe peu, rétrocompatible) ;
  **longueur** et **épaisseur** (2 à 3 emplacements) face au boîtier ; **alimentation
  recommandée** par le fabricant et **connecteurs** disponibles sur le bloc ; **sorties** (HDMI,
  DisplayPort) adaptées à l'écran.
- **Sorties vidéo de la carte mère** : elles ne fonctionnent qu'avec un processeur à partie
  graphique intégrée, et elles sont souvent désactivées quand une carte graphique est installée :
  **l'écran se branche sur la carte graphique**.

**À l'écrit** : une ligne par critère, avec la valeur relevée et la conclusion (« longueur :
320 mm pour 300 mm au plus, incompatible »).
"""


def _ports() -> str:
    return f"""**Objectifs** : identifier les ports externes et internes, choisir le bon port pour un
périphérique.

## 10.1 Le panneau arrière

{_fig(REAR_PANEL_FIGURE, wide=True)}

{_rear_table()}

## 10.2 L'USB : la forme n'est pas le débit

{_usb_table()}

- **USB-C** est une **forme de connecteur** (réversible), pas une vitesse : une prise USB-C peut
  être en USB 2.0, en 5, 10, 20 ou 40 Gbit/s. Le **marquage**, le **manuel** et le **câble**
  déterminent le débit réel.
- La couleur bleue d'une languette USB-A signale **souvent** l'USB 3.x : c'est une habitude, pas
  une garantie.

## 10.3 Les autres ports

- **Vidéo** : **HDMI** (image et son, téléviseurs et écrans), **DisplayPort** (écrans
  informatiques, image et son), **DVI** (ancien, numérique), **VGA** (ancien, analogique, prise
  bleue à 15 broches).
- **Réseau** : **RJ45** (Ethernet, voyants de liaison et d'activité) ; **antennes Wi-Fi** si la
  carte a un module sans fil.
- **Audio** (code couleur des PC de bureau) : {_audio_list()}.
- **PS/2** : ancien port rond (violet = clavier, vert = souris).
- **Ports internes** : voir le chapitre 3.3 (USB de façade, HD_AUDIO, ventilateurs,
  connecteur de façade).

**À l'écrit** : « le SSD externe 10 Gbit/s se branche sur la prise USB-C arrière marquée
10 Gbit/s : la prise USB-C de façade n'est qu'en 5 Gbit/s ».
"""


def _peripherals() -> str:
    return """**Objectifs** : classer les périphériques ; expliquer le rôle d'un pilote et l'installer
proprement.

## 11.1 Entrée, sortie, entrée-sortie

| Catégorie | Le périphérique… | Exemples |
|---|---|---|
| **Entrée** | envoie des informations au PC | clavier, souris, scanner, micro, webcam, lecteur de codes-barres |
| **Sortie** | reçoit des informations du PC | écran, imprimante, haut-parleurs, vidéoprojecteur |
| **Entrée et sortie** | fait les deux | écran tactile, imprimante multifonction, casque-micro, disque externe |

## 11.2 Le rôle d'un pilote

- Le **pilote** (driver) est le logiciel qui permet au **système d'exploitation** de dialoguer
  avec un **matériel précis** : il traduit les demandes du système en commandes du
  périphérique. Sans lui, le matériel est vu mais **inutilisable** (« Périphérique inconnu »,
  triangle jaune dans le Gestionnaire de périphériques).
- **Pilote générique** : fourni par le système pour les classes courantes (clavier, souris, clé
  USB) ; **pilote du fabricant** : nécessaire pour les fonctions complètes (imprimante, carte
  graphique, webcam particulière).
- Un pilote est propre au **système** et à son **architecture** (32 ou 64 bits) ; on le prend
  sur le **site du fabricant** ou par **Windows Update**, jamais sur un site de téléchargement
  tiers (logiciel modifié ou malveillant).
- **Identifier le matériel** : Gestionnaire de périphériques (Windows), `lspci`, `lsusb` (Linux).

## 11.3 Procédure écrite d'installation d'un périphérique

1. Relever le **modèle exact** et la **connexion** (USB, réseau, Bluetooth).
2. Vérifier la **compatibilité** avec le système (version, architecture).
3. Récupérer le **pilote du fabricant** (ou Windows Update) ; l'installer avec un compte
   administrateur.
4. Brancher, laisser la détection se faire, contrôler le **Gestionnaire de périphériques**.
5. **Tester** la fonction (page de test, image de la webcam, son) et noter l'intervention.
"""


def _compatibility() -> str:
    return f"""**Objectifs** : appliquer une grille de compatibilité complète avant un achat ou un montage
et la rédiger.

{_fig(COMPATIBILITY_FIGURE, wide=True)}

| Pièce | Critères à vérifier (fiche ou manuel) |
|---|---|
| Processeur | socket ; liste des processeurs pris en charge par la carte et version du firmware ; mémoire acceptée ; partie graphique si pas de carte graphique ; refroidissement |
| Mémoire | DIMM ou SO-DIMM ; génération DDR ; capacité par emplacement et totale ; fréquence ; emplacements à utiliser ; ECC ou non |
| Carte mère | format face au boîtier ; socket ; chipset ; emplacements M.2, PCIe, SATA ; connecteurs du bloc |
| Stockage | format (3,5", 2,5", M.2 2280…) ; interface (SATA ou NVMe) acceptée par l'emplacement ; port SATA désactivé par un M.2 ; câbles |
| Carte graphique | slot PCIe x16 ; longueur et épaisseur ; puissance recommandée et connecteurs PCIe ; sorties face à l'écran |
| Ventirad | socket ; puissance dissipée ; hauteur maximale du boîtier |
| Boîtier | formats de carte mère et de bloc ; longueur de carte graphique ; hauteur de ventirad ; baies |
| Périphérique | port et débit ; pilote pour le système et l'architecture |

- **« Ça rentre » ne veut pas dire « c'est compatible »** : un M.2 SATA s'enfiche dans un M.2
  NVMe seul sans fonctionner ; un processeur de même socket peut exiger une mise à jour du
  firmware.
- **Ne jamais inventer une caractéristique** : si la fiche ne la donne pas, on l'écrit (« à
  vérifier sur la liste de compatibilité du fabricant »).
- **Rétrocompatibilités utiles** : PCIe entre générations, USB entre versions (au débit le plus
  bas), carte plus petite dans un boîtier plus grand.
"""


def _procedure_esd() -> str:
    return """**Objectifs** : rédiger une démarche d'identification, d'inventaire ou de montage ;
justifier les précautions électriques et antistatiques.

## 13.1 Identifier et inventorier par écrit

1. **Observer** : forme, taille, nombre de broches, détrompeur, position, inscriptions.
2. **Nommer** exactement le composant.
3. Donner son **rôle** en une phrase.
4. **Relier** : à quoi il est connecté et par quelle liaison.
5. **Vérifier** : inscription, manuel, fiche du fabricant, outil d'inventaire (firmware,
   Gestionnaire de périphériques, `lsblk`, `lscpu`, `free -h`).
6. **Noter** dans une fiche d'inventaire : composant, modèle, caractéristique utile, état.

## 13.2 Interpréter un inventaire et un symptôme

- **Comparer** ce qui est installé et ce qui est détecté (capacité mémoire, disques, cartes).
- Une différence est un **indice** : barrette mal insérée, emplacement à utiliser selon le
  manuel, pièce incompatible, pilote absent, unités décimales ou binaires.
- On **confirme** par un test simple (réinsertion, échange d'emplacement, fiche du fabricant)
  avant de conclure ; le diagnostic complet des pannes est l'objet de PR06.

## 13.3 Précautions électriques et antistatiques

| Précaution | Pourquoi |
|---|---|
| Arrêter le système, **débrancher le secteur**, appuyer sur le bouton de démarrage | le bloc garde une tension de veille tant qu'il est branché ; on vide la charge résiduelle |
| **Bracelet antistatique** relié au châssis ou au tapis antistatique | une décharge électrostatique, même imperceptible, peut abîmer des puces sans trace visible |
| Composants dans leur **sachet antistatique** jusqu'au montage, tenus **par les bords** | on évite de toucher contacts, broches et puces |
| Éviter moquette, laine, air très sec ; travailler sur un plan dégagé | ces conditions favorisent les charges statiques |
| **Ne jamais forcer** : détrompeur aligné, clips ouverts, vis adaptées | un connecteur forcé ou une broche tordue détruit la pièce |
| Ne jamais ouvrir un **bloc d'alimentation** | ses condensateurs gardent une tension dangereuse |

**À l'écrit**, chaque précaution est **justifiée** : « je débranche le secteur, car le bloc reste
sous tension de veille ».
"""


def _examples() -> str:
    case2_lines = memory_cim_lines(CASE2_SLOTS)
    detected = sum(s.capacity_gib for s in CASE2_SLOTS)
    return f"""## Cas 1 — Identifier les éléments d'une unité centrale pour l'inventaire

**Situation.** Une école te confie l'inventaire d'un PC de bureau ouvert. Le relevé du stagiaire
dit : « (a) gros connecteur à 24 broches sur le bord droit de la carte ; (b) deux barrettes
longues dans des emplacements à clips ; (c) carte d'extension dans le long slot le plus proche du
processeur, avec deux connecteurs 8 broches branchés et des sorties DisplayPort ; (d) boîtier
métallique en bas à l'arrière, avec un ventilateur et un interrupteur ; (e) disque 3,5" relié par
deux câbles, l'un fin à 7 contacts, l'autre plat à 15 contacts ; (f) pile ronde sur la carte. »

**Résolution, étape par étape (démarche du chapitre 13).**

| Repère | Nom exact | Rôle | Relié à / par |
|---|---|---|---|
| a | connecteur d'alimentation ATX 24 broches | alimentation principale de la carte mère | bloc d'alimentation |
| b | barrettes DIMM de mémoire vive | mémoire de travail, volatile | contrôleur mémoire du processeur (canaux DDR) |
| c | carte graphique PCIe x16 | calcule et envoie l'affichage | processeur par PCIe x16 ; bloc par 2 × PCIe 8 broches ; écran par DisplayPort |
| d | bloc d'alimentation (format ATX) | convertit le secteur en tensions continues | tous les composants (aucune donnée) |
| e | disque dur 3,5" SATA | stockage de masse non volatile | carte mère par le câble de données SATA (7 contacts) ; bloc par l'alimentation SATA (15 contacts) |
| f | pile CMOS | maintient l'horloge (et parfois les réglages) | carte mère |

**Conclusion rédigée.** Pour la fiche d'inventaire, on complète chaque ligne par le **modèle**
lu sur l'étiquette ou dans l'outil d'inventaire (capacité des barrettes, modèle de la carte
graphique, puissance du bloc, capacité du disque) ; on n'invente aucune valeur absente.

## Cas 2 — Interpréter un inventaire : 8 Go détectés pour {CASE2_INSTALLED_GIB} Go installés

**Situation.** Un client a ajouté une barrette DDR5 de 8 Go (en B2) à la barrette de 8 Go déjà
en A2. Windows indique toujours 8 Go. Tu relèves les barrettes détectées :

{_console(*case2_lines)}

**Résolution.**

1. **Lire** : une seule ligne, DIMM_A2, capacité 8 589 934 592 octets = 8 × 1024³ octets, soit
   8 Go ; total détecté : {detected} Go pour {CASE2_INSTALLED_GIB} Go installés.
2. **Hypothèses** : barrette de B2 mal enfoncée (clips non verrouillés), barrette incompatible
   (génération, fréquence, liste de compatibilité), barrette ou emplacement défectueux.
3. **Tests, du plus simple au plus invasif**, PC débranché et protégé contre l'électricité
   statique : vérifier la **référence** de la nouvelle barrette (DDR5 DIMM comme l'ancienne ?),
   la **réinsérer** jusqu'au verrouillage des clips, puis, si besoin, l'essayer **seule** en A2.
4. **Conclusion** : si elle fonctionne seule en A2 après réinsertion, elle était mal insérée ou
   l'emplacement B2 est en cause (essayer une barrette sûre en B2) ; si elle n'est jamais
   détectée, elle est défectueuse ou incompatible.
5. **Vérification** : {CASE2_INSTALLED_GIB} Go détectés dans le firmware et dans le système, deux
   lignes dans le relevé, test mémoire si doute.

## Cas 3 — Choisir une carte mère de remplacement

**Situation.** La carte mère d'un PC de bureau est hors service. Le client garde son processeur
(socket AM4), ses 2 × 8 Go DIMM DDR4, son SSD NVMe M.2 2280, sa carte graphique (PCIe x16) et sa
carte son (PCIe x1), son boîtier (microATX) et son bloc (ATX 24 + EPS 8). Trois cartes fictives :

| Carte | Format | Socket | Mémoire | Emplacements |
|---|---|---|---|---|
| B1 | ATX | AM5 | 4 × DIMM DDR5 | 1 × M.2 NVMe, 3 × PCIe |
| B2 | microATX | AM4 | 4 × DIMM DDR4 | 1 × M.2 NVMe 2280, 1 × PCIe x16, 2 × PCIe x1 |
| B3 | Mini-ITX | AM4 | 2 × DIMM DDR4 | 1 × M.2 NVMe 2280, 1 × PCIe x16 |

**Résolution.**

1. **Format** : le boîtier est microATX ; B1 (ATX) {_fits_text('ATX')} ; B2 (microATX)
   {_fits_text('microATX')} ; B3 (Mini-ITX) {_fits_text('Mini-ITX')}.
2. **Socket et mémoire** : B1 est en AM5/DDR5 : ni le processeur ni la mémoire ne conviennent ;
   B2 et B3 sont en AM4/DDR4.
3. **Emplacements** : il faut un PCIe x16 et un PCIe x1 ; B3 n'a qu'un emplacement d'extension
   (Mini-ITX) : la carte son serait perdue. B2 a un x16 et deux x1.
4. **Stockage et alimentation** : B2 a un M.2 NVMe 2280 ; les connecteurs ATX 24 et EPS 8 du
   bloc conviennent.
5. **Dernier contrôle** : le processeur du client figure-t-il dans la **liste des processeurs
   pris en charge** de B2, avec quelle version de firmware ? À vérifier sur le site du fabricant.

**Conclusion rédigée.** B2 est retenue : bon format, même socket et même génération de mémoire,
emplacements suffisants ; prise en charge du processeur à confirmer sur la liste du fabricant.

## Cas 4 — Justifier l'installation d'une carte graphique et les précautions

**Situation.** Un client veut ajouter une carte graphique (fiche fictive : PCIe 4.0 x16, 267 mm,
2 emplacements, 1 connecteur PCIe 8 broches, bloc recommandé 550 W) à son PC : slot PCIe 3.0 x16
libre, boîtier acceptant 310 mm, bloc 650 W avec un câble PCIe 6+2, écran HDMI.

**Résolution.**

1. **Compatibilité** : slot x16 libre, PCIe rétrocompatible (débit du 3.0) ; 267 mm ≤ 310 mm ;
   deux emplacements libres ; 650 W ≥ 550 W et un câble PCIe 6+2 pour un connecteur 8 broches ;
   sortie HDMI pour l'écran : **compatible**.
2. **Préparation** : aucune donnée n'est touchée, mais on télécharge d'abord le pilote du
   fabricant ; arrêt du système, **secteur débranché**, bouton maintenu pour décharger.
3. **Précautions antistatiques** : bracelet relié au châssis, carte gardée dans son sachet,
   tenue par les bords et l'équerre.
4. **Montage** : retirer les équerres de fermeture, ouvrir le loquet du slot, enfoncer la carte
   droite jusqu'au déclic, la visser, brancher le **câble PCIe 6+2 en 8 broches** jusqu'au
   verrouillage.
5. **Mise en service** : brancher l'écran **sur la carte graphique**, démarrer, installer le
   **pilote** du fabricant, vérifier la résolution et la température en charge, noter
   l'intervention.
"""


def _pitfalls() -> str:
    return """> **Confondre ROM et stockage** : la puce du firmware ne contient ni le système ni les
> fichiers ; le disque, lui, ne contient pas le firmware.

> **Croire que « ça rentre » prouve la compatibilité** : M.2 SATA dans un M.2 NVMe seul, carte
> PCIe dans un slot x16 câblé en x4, processeur de même socket sans le bon firmware.

> **Confondre DIMM et SO-DIMM, DDR4 et DDR5** : formats et encoches différents ; jamais forcer.

> **Brancher l'écran sur la carte mère** alors qu'une carte graphique est installée.

> **Prendre USB-C pour une vitesse** : c'est une forme de connecteur ; le débit dépend du port.

> **Inventer une caractéristique** absente de la fiche (fréquence, longueur, puissance) au lieu
> d'écrire « à vérifier ».

> **Confondre EPS 8 broches et PCIe 8 broches**, ou mélanger les câbles de deux blocs
> modulaires.

> **Prendre la capacité affichée en Gio pour une panne** (500 Go affichés 465,7G).

> **Oublier les limites du boîtier** : longueur de la carte graphique, hauteur du ventirad,
> format de la carte mère.

> **Travailler sous tension ou sans protection antistatique**, toucher les contacts d'une
> barrette, poser une carte hors de son sachet sur la moquette.

> **Réciter des sigles** sans dire le rôle : à l'écrit, chaque nom de composant est suivi de ce
> qu'il fait et de ce à quoi il est relié.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : identifications sur description ou schéma, classements,
remise en ordre d'un trajet de données, analyses d'inventaire, choix de pièces compatibles,
scénarios de client et procédures écrites. Rédige ta réponse sur papier **avant** d'ouvrir le
corrigé ; toute réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont proposés
dans [S'entraîner](/uaa/{PR01_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR01_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (descriptions, fiches fictives, relevés).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** L'**identification exacte**, le **rôle** et les **liaisons**, la
**justification chiffrée** d'un choix compatible et des **précautions** justifiées — pas la
récitation de sigles. Une autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Structure** : processeur (calcul) · RAM (travail, volatile) · stockage (conservation) ·
  carte mère (liaisons) · chipset (E/S secondaires) · bloc (énergie, aucune donnée).
- **Liaisons directes au processeur** : RAM, PCIe x16 principal, souvent le premier M.2 ; le
  reste passe par le chipset.
- **Formats** : ATX 305 × 244 mm (7 emplacements), microATX 244 × 244 mm (4), Mini-ITX
  170 × 170 mm (1) ; une carte plus petite entre dans un boîtier plus grand, jamais l'inverse.
- **Socket** = plateforme ; même socket ≠ compatibilité garantie : liste des processeurs et
  version du firmware.
- **VRM** : +12 V de l'EPS → tension du processeur. **Chipset** : SATA, USB, réseau, audio.
- **Mémoires** : RAM volatile · ROM/flash = firmware · stockage = système et fichiers.
- **Barrettes** : DIMM (bureau) / SO-DIMM (portable) ; DDR3/DDR4/DDR5 non interchangeables ;
  capacité maximale ; emplacements du manuel.
- **Firmware** : UEFI (successeur du BIOS), POST, pile CMOS = horloge ; mise à jour sans coupure.
- **Stockage** : HDD (plateaux) · SSD SATA (≈ 600 Mo/s utiles) · M.2 NVMe (PCIe) ; M.2 SATA ≠
  M.2 NVMe ; Go décimaux, Gio binaires.
- **Alimentation** : ATX 24, EPS 8 (CPU), PCIe 6/8 (carte graphique), SATA 15, Molex 4.
- **Carte graphique** : slot x16, longueur, épaisseur, puissance et connecteurs, sorties ;
  écran sur la carte graphique.
- **USB-C** = forme, pas débit. Audio : vert sortie, rose micro, bleu clair entrée ligne.
- **Pilote** : fait dialoguer le système et le matériel ; système et architecture ; site du
  fabricant.
- **Sécurité** : secteur débranché, décharge, bracelet antistatique, sachet, bords, ne jamais
  forcer.

## Glossaire des termes employés

- **Chipset** : puce de la carte mère qui gère une partie des entrées-sorties.
- **DIMM / SO-DIMM** : formats de barrette mémoire pour PC de bureau / pour portable.
- **EPS** : connecteur 8 broches (4+4) d'alimentation du processeur.
- **Firmware** : programme de la carte mère exécuté avant le système (UEFI, BIOS).
- **M.2** : emplacement plat pour SSD, en SATA ou en NVMe selon la carte.
- **NVMe** : protocole des SSD reliés en PCIe.
- **PCIe** : bus d'extension par lignes (x1, x4, x16).
- **Pilote** : logiciel qui permet au système d'utiliser un matériel.
- **POST** : autotest du matériel à la mise sous tension.
- **Socket** : support du processeur sur la carte mère.
- **VRM** : étage d'alimentation du processeur sur la carte mère.
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigences AP-01, AP-02,
  AP-05, AP-07 et AP-17. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Formats de carte mère** : spécifications ATX 2.x et microATX (Intel), Mini-ITX (VIA) ;
  **alimentation** : guide de conception ATX12V / EPS12V (Intel, SSI) ; **PCI Express** :
  spécifications de base et CEM (PCI-SIG) — débits calculés depuis le débit de transfert et le
  codage 128b/130b ; **mémoire** : normes JEDEC DDR3, DDR4, DDR5 (contacts, tensions,
  dimensions des modules) ; **SATA** : spécification Serial ATA révision 3 ; **M.2** :
  spécification PCI-SIG M.2 ; **USB** : USB-IF (USB 2.0, USB 3.2, USB4) ; **NVMe** : NVM
  Express ; **UEFI** : spécification UEFI Forum ; code couleur des prises : guide PC 99.
- **Outils** : documentation Microsoft (Gestionnaire de périphériques, `Get-CimInstance`,
  `Get-PhysicalDisk`) et pages de manuel Linux (`lsblk`, `lspci`, `lsusb`, `lscpu`, `free`).

Les tableaux de valeurs du cours (formats, barrettes, PCIe, USB, SATA, connecteurs) et les
schémas sont **produits par programme** depuis ces données, **vérifiés par des tests
automatiques** ; aucun schéma n'est tiré d'une image générée.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande la structure de l'ordinateur et ses composants (AP-01, AP-02), les
périphériques et le rôle d'un pilote (AP-05), la carte mère (AP-07) et la compatibilité
(AP-17). Sont des **compléments**, signalés comme tels :

- les précautions électriques et antistatiques (AP-C02, approfondies en PR02, PR03 et PR28) ;
- les débits chiffrés PCIe, USB et SATA, les unités décimales et binaires, les commandes
  d'inventaire (`lsblk`, `Get-CimInstance`).

## Supports fictifs

Le plan de carte mère, la tour, le panneau arrière, les fiches produits, les relevés et les
situations de ce cours sont **fictifs** et reconstitués pour l'entraînement ; ils ne décrivent
aucun produit réel. Aucun n'est une question officielle ou déjà posée par le Jury.
"""


def pr01_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR01 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR01 — 1. Structure d'un PC : unité centrale, périphériques et cheminement des données", _structure()),
        ("PR01 — 2. Boîtier et formats de carte mère : ATX, microATX, Mini-ITX", _case_and_forms()),
        ("PR01 — 3. Carte mère : socket, chipset, VRM, emplacements et connecteurs internes", _motherboard()),
        ("PR01 — 4. Processeur et refroidissement", _cpu()),
        ("PR01 — 5. RAM, ROM et stockage : volatiles ou non ; barrettes DIMM et SO-DIMM", _memory()),
        ("PR01 — 6. Firmware BIOS/UEFI, POST et pile CMOS", _firmware()),
        ("PR01 — 7. Stockage : disque dur, SSD SATA, M.2 SATA et NVMe", _storage()),
        ("PR01 — 8-9. Connecteurs du bloc d'alimentation et carte graphique", _power_gpu()),
        ("PR01 — 10. Ports externes et internes : USB, vidéo, réseau, audio", _ports()),
        ("PR01 — 11. Périphériques d'entrée et de sortie, rôle d'un pilote", _peripherals()),
        ("PR01 — 12. Compatibilité : la grille de contrôle avant achat ou montage", _compatibility()),
        ("PR01 — 13. Démarche écrite : identifier, inventorier, monter sans risque (ESD)", _procedure_esd()),
        ("PR01 — Exemples : quatre cas intégralement résolus", _examples()),
        ("PR01 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR01 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR01 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR01 — Fiche mémo et glossaire", _memo()),
        ("PR01 — Sources et compléments pédagogiques", _sources()),
    ]
