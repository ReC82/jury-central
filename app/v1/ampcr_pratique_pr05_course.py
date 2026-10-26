"""Cours PR05 « Stockage, partitions, formatage et défragmentation » — parcours AMPCR pratique
écrite (ticket #206).

Matière : intégralement celle du ticket #206 (disque dur et SSD SATA/NVMe, interfaces,
secteurs/blocs et usure, unités Go/Gio, partitions MBR/GPT, EFI/ESP, démarrage, volume,
formatage logique, NTFS/FAT32/exFAT/ext4 et choix selon l'usage, création et gestion des
partitions sous Windows et Linux, sauvegarde préalable, SMART interprété prudemment,
TRIM/répartition de l'usure, défragmentation HDD contre SSD, symptômes disque absent / non
initialisé / espace plein / démarrage impossible, procédures écrites non destructives),
découpée en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de
bloc théorique ne contient « examen », « source », « ressource », « exemple », « exercice »,
« méthode », « piège », « attention » ni « mémo » — donc pas « mémoire »).
Données et schémas : `app.v1.ampcr_pratique_pr05_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr05_bank`. Mise en forme partagée avec les autres cours pratiques.
"""

from html import escape

from app.v1.ampcr_pratique_pr05_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr05_figures import (
    CASE1_GIB,
    CASE4_C_GIB,
    CASE4_D_GIB,
    CASE4_FIGURE,
    CASE4_HDD_TB,
    CASE4_SSD_GB,
    DISKMGMT_FIGURE,
    FAT32_MAX_FILE,
    FILESYSTEMS,
    FRAGMENTATION_ALERT,
    FSTAB_LINE,
    GIB,
    LINUX_NEW_DISK_FIGURE,
    LSBLK_FIGURE,
    MBR_GPT_ROWS,
    MBR_LIMIT_BYTES,
    MEDIA_HDD,
    MEDIA_ROWS,
    MISSING_TREE_FIGURE,
    NOT_DETECTED_FIGURE,
    NTFS_DEFAULT_CLUSTER,
    OPTIMISE_FIGURE,
    OPTIMISE_ROWS,
    OPTIMISE_SCREEN_FIGURE,
    PLANS,
    PLANS_FIGURE,
    PROCEDURES,
    SAFE_FIGURE,
    SYMPTOMS,
    UNIT_ROWS,
    WIN_NEW_DISK_FIGURE,
    clusters_used,
    fits_on_fat32,
    fr_number,
    gb_to_gib,
    needs_defrag,
    optimisation_for,
)
from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req

PR05_TITLE = "Stockage, partitions, formatage et défragmentation"
PR05_SLUG = "ampcr-pratique-pr05"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr05") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _media_table() -> str:
    rows = "\n".join(
        f"| **{m.name}** | {m.principle} | {m.interface} | {m.order_of_speed} | {m.strengths} | {m.limits} |"
        for m in MEDIA_ROWS
    )
    return ("| Support | Principe | Interface et format | Ordre de grandeur | Points forts | Limites |\n"
            "|---|---|---|---|---|---|\n" + rows)


def _units_table() -> str:
    rows = "\n".join(
        f"| {label} | {octets // 10**9} × 10^9 octets | **{fr_number(octets / GIB)}** |" for label, octets in UNIT_ROWS
    )
    return "| Vendu (fabricant, décimal) | Octets | Affiché par Windows (Gio, écrit « Go ») |\n|---|---|---|\n" + rows


def _mbr_gpt_table() -> str:
    rows = "\n".join(f"| {what} | {mbr} | {gpt} |" for what, mbr, gpt in MBR_GPT_ROWS)
    return "| Critère | MBR | GPT |\n|---|---|---|\n" + rows


def _plans_tables() -> str:
    blocks = []
    for title, table, firmware, plan in PLANS:
        rows = "\n".join(
            f"| {i} | **{p.name}** | {p.filesystem} | {p.size_label} | {p.role} |" for i, p in enumerate(plan, start=1)
        )
        blocks.append(
            f"**{title}** — table {table}, démarrage {firmware}\n\n"
            "| N° | Partition | Système de fichiers | Taille | Rôle |\n|---|---|---|---|---|\n" + rows
        )
    return "\n\n".join(blocks)


def _fs_table() -> str:
    rows = "\n".join(
        f"| **{fs.name}** | {fs.max_file} | {fs.windows} | {fs.macos} | {fs.linux} | "
        f"{'oui' if fs.journal else 'non'} | {'oui' if fs.permissions else 'non'} | {fs.typical_use} |"
        for fs in FILESYSTEMS
    )
    return ("| Système | Fichier max. | Windows | macOS | Linux | Journal | Droits | Usage typique |\n"
            "|---|---|---|---|---|---|---|---|\n" + rows)


def _symptoms_table() -> str:
    rows = "\n".join(
        f"| **{s.seen}** | {s.likely} | {s.first_action} | {s.never} |" for s in SYMPTOMS
    )
    return "| Ce qu'on voit | Causes probables | Première action | À ne jamais faire |\n|---|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). On ne te demande pas de partitionner un disque devant le jury, mais de **choisir** le bon
support, la bonne table de partitions et le bon système de fichiers, de **rédiger** une
procédure sans risque pour les données et d'**interpréter** une capture (Gestion des disques,
lsblk, « Optimiser les lecteurs ») ou un relevé SMART. Tu dois savoir :

1. **comparer** disque dur, SSD SATA et SSD NVMe, et vérifier la **compatibilité** (SATA, M.2) ;
2. **expliquer** secteurs, clusters, pages, usure, et **convertir** Go et Gio ;
3. **choisir** entre **MBR** et **GPT**, situer la **partition EFI (ESP)** et le démarrage ;
4. **choisir** un système de fichiers (**NTFS, FAT32, exFAT, ext4**) selon l'usage ;
5. **dessiner et chiffrer** un plan de partitions ;
6. **créer et gérer** des partitions sous **Windows** et sous **Linux** ;
7. **sauvegarder avant** toute opération et travailler de façon **non destructive** ;
8. **lire un relevé SMART** avec prudence, **entretenir** le support (défragmentation ou TRIM) ;
9. **diagnostiquer** un disque absent, non initialisé, RAW, plein ou un démarrage impossible.

Ce cours contient **5 procédures illustrées** :

{_procedures_list()}

## Exigence officielle travaillée dans ce cours

{_req("AP-03")}

Les opérations sur les données du client s'appuient sur le complément pédagogique déjà vu en
[PR04](/uaa/ampcr-pratique-pr04) (accord écrit, sauvegarde vérifiée, effacement sécurisé) :

{_req("AP-C03")}

L'identification des composants est traitée en [PR01](/uaa/ampcr-pratique-pr01), les connecteurs
SATA et M.2 en [PR02](/uaa/ampcr-pratique-pr02), le montage d'un disque en
[PR03](/uaa/ampcr-pratique-pr03), l'effacement sécurisé en [PR04](/uaa/ampcr-pratique-pr04), le
diagnostic des pannes en [PR06](/uaa/ampcr-pratique-pr06) et les messages de démarrage en
[PR11](/uaa/ampcr-pratique-pr11).

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC04 Stockage : HDD, SSD SATA et NVMe](/uaa/ampcr-mc04),
[MC08 Partitionnement, GPT/MBR et formatage](/uaa/ampcr-mc08) et
[MC07 BIOS, UEFI, POST et démarrage](/uaa/ampcr-mc07). Ce cours-ci est **pratique** : choix
justifiés, plans chiffrés, procédures rédigées et captures à interpréter, comme dans un dossier
d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **quatre
cas résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans
« S'entraîner », correction après envoi), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les captures, relevés et situations de ce cours sont des **supports fictifs**
> construits pour s'entraîner ; seuls la notice et l'outil du fabricant font foi pour un vrai
> matériel. Aucun exercice n'est une question officielle ni une question déjà posée par le Jury.
> **Partitionner ou formater rend les données inaccessibles : jamais sans sauvegarde vérifiée
> et accord écrit du propriétaire.**
"""


def _media() -> str:
    return f"""**Objectifs** : choisir le support adapté à l'usage et justifier ce choix par son principe
de fonctionnement.

## 1.1 Trois supports

{_media_table()}

## 1.2 Ce qui change pour le technicien

- Le **disque dur** a des pièces mobiles : têtes au-dessus de plateaux en rotation. Il craint
  les **chocs en fonctionnement**, il est lent pour démarrer un système, mais reste le moins
  cher par To : on l'utilise pour les **données volumineuses** et les **sauvegardes**.
- Le **SSD** n'a aucune pièce mobile : accès quasi immédiat, silence, résistance aux chocs.
  C'est le support **du système et des programmes**.
- Le **SSD NVMe** dialogue en PCI Express : plusieurs fois plus rapide qu'un SSD SATA, limité
  par l'interface SATA 6 Gbit/s.
- Dans un même PC, on combine souvent **SSD pour le système** et **disque dur pour les
  données** (cas 4).

**Procédure professionnelle (à rédiger)** : relever l'usage (système, données, mobilité,
budget) → relever ce que le PC accepte (baies, ports SATA, emplacements M.2 de la notice) →
choisir le support → justifier par son principe.

**Erreur fréquente** : conseiller un disque dur pour un portable qui voyage, ou « parce que
c'est plus grand », sans parler de la vitesse et des chocs.

**À l'écrit** : le choix + **deux** justifications liées à l'usage (vitesse, chocs, prix par To,
capacité).

**Repère rapide** : **système → SSD (NVMe si possible) · gros volumes et sauvegardes → disque
dur**. Exercices liés : {_ex("E05")}.
"""


def _interfaces() -> str:
    return f"""**Objectifs** : vérifier qu'un support est compatible avec le PC **avant** de l'acheter
ou de l'installer.

## 2.1 SATA

- Un disque dur ou un SSD 2,5 pouces SATA se branche par **deux câbles** : **données SATA**
  (7 broches, vers la carte mère) et **alimentation SATA** (15 broches, vers le bloc).
- SATA III : **6 Gbit/s**, soit environ **600 Mo/s** utiles au maximum ; un SSD SATA atteint
  environ 550 Mo/s, un disque dur reste bien en dessous.

## 2.2 M.2 : un format, deux langages

- **M.2** est un **format** de carte (largeur 22 mm, longueur 30 à 110 mm : « 2280 » = 22 × 80 mm).
- Une carte M.2 parle **SATA** ou **NVMe** (PCI Express). Un emplacement M.2 peut accepter
  SATA seulement, NVMe seulement, ou les deux : **la notice de la carte mère fait foi**.
- Sur certaines cartes, occuper un emplacement M.2 **désactive** un ou deux ports SATA
  (lignes partagées) : la notice le précise.
- Un SSD NVMe se fixe par **une vis** (ou un clip) ; il peut recevoir un **dissipateur**.

| Je veux installer… | Je vérifie dans la notice |
|---|---|
| un disque 3,5 ou 2,5 pouces SATA | une baie libre, un port SATA libre, un câble d'alimentation SATA |
| un SSD M.2 SATA | un emplacement M.2 qui accepte **SATA**, la longueur (2280…) |
| un SSD M.2 NVMe | un emplacement M.2 qui accepte **NVMe / PCIe**, la longueur, les ports SATA désactivés |

**Procédure professionnelle (à rédiger)** : identifier le support (SATA ou NVMe, format) →
lire la notice (emplacement, interface acceptée, longueur, partage de lignes) → conclure
« compatible » ou proposer un autre modèle.

**Erreur fréquente** : acheter un SSD NVMe pour un emplacement M.2 « SATA uniquement » : il ne
sera pas détecté.

**À l'écrit** : citer **l'interface** (SATA / NVMe) **et** le **format** (2,5 pouces, M.2 2280).

**Repère rapide** : **M.2 = forme · SATA ou NVMe = langage · la notice décide**.
Exercices liés : {_ex("E02")}.
"""


def _sectors() -> str:
    one_byte = clusters_used(1)
    ten_k = clusters_used(10_000)
    return f"""**Objectifs** : comprendre comment un support range les données, pourquoi un SSD s'use et
pourquoi un fichier occupe parfois plus de place que sa taille.

## 3.1 Secteurs et clusters

- Le **secteur** est la plus petite zone qu'un disque lit ou écrit : historiquement
  **512 octets**, **4 096 octets** sur les disques récents (« Advanced Format », souvent
  présentés en 512 octets pour la compatibilité).
- Le système de fichiers regroupe les secteurs en **clusters** (unités d'allocation), par
  défaut **{NTFS_DEFAULT_CLUSTER // 1024} Kio** en NTFS et en ext4. Un fichier occupe toujours
  des clusters entiers : un fichier de 1 octet occupe {one_byte} cluster ({NTFS_DEFAULT_CLUSTER}
  octets), un fichier de 10 000 octets en occupe {ten_k}.

## 3.2 Pages, blocs et usure d'un SSD

- La mémoire flash s'**écrit par pages** (quelques Kio) mais ne s'**efface que par blocs**
  entiers (des centaines de pages). Pour réécrire une page, le contrôleur écrit ailleurs et
  efface plus tard (« ramasse-miettes »).
- Chaque cellule supporte un **nombre limité de cycles d'écriture et d'effacement**. Le
  fabricant indique l'**endurance** en **téraoctets écrits (TBW)**.
- Le contrôleur **répartit l'usure** (wear leveling) : il déplace les écritures pour que toutes
  les cellules s'usent au même rythme, et garde des **cellules de réserve**.
- **TRIM** : le système signale au SSD les blocs qui ne contiennent plus de fichiers ; le
  contrôleur peut les effacer à l'avance, ce qui garde des écritures rapides et limite l'usure
  (chapitre 13).

## 3.3 Et le disque dur ?

- Les secteurs sont sur des **pistes** de plateaux ; lire des secteurs **éloignés** oblige la
  tête à se déplacer : c'est la **fragmentation** qui ralentit un disque dur.
- Un secteur illisible est remplacé par un secteur de réserve : il apparaît dans le compteur
  SMART des **secteurs réalloués** (chapitre 12).

**Procédure professionnelle (à rédiger)** : pour expliquer une lenteur ou une usure, nommer le
mécanisme (déplacement des têtes, usure des cellules) avant de proposer l'entretien adapté.

**Erreur fréquente** : penser qu'un SSD « s'use à la lecture » ou qu'il faut le défragmenter
pour le ménager : c'est l'**écriture** qui use, et la défragmentation écrit beaucoup.

**À l'écrit** : employer le bon terme (secteur, cluster, page, bloc, endurance) dans une
phrase qui explique le phénomène.

**Repère rapide** : **disque dur : secteurs + têtes → fragmentation · SSD : pages + blocs →
usure, TRIM**. Exercices liés : {_ex("E05")}.
"""


def _units() -> str:
    one_tb = gb_to_gib(1000)
    return f"""**Objectifs** : expliquer à un client pourquoi la capacité affichée est « plus petite »
que la capacité achetée, avec le calcul.

## 4.1 Deux familles d'unités

- **Décimales** (fabricants, Système international) : 1 Go = **10^9** = 1 000 000 000 octets ;
  1 To = **10^12** octets.
- **Binaires** (CEI) : 1 Gio = **2^30** = 1 073 741 824 octets ; 1 Tio = 2^40 octets.
- **Windows** calcule en Gio **mais écrit « Go »** ; Linux (`lsblk`, `df -h`) écrit « G » ou
  « T » pour des Gio et des Tio.

## 4.2 Le calcul

Capacité affichée = octets ÷ 1 073 741 824. Pour un disque de 1 To :
10^12 ÷ 2^30 ≈ **{fr_number(one_tb)}**. Il ne « manque » rien : c'est le même nombre d'octets.

{_units_table()}

## 4.3 Dans Gestion des disques

La taille d'un nouveau volume se saisit en « Mo », qui sont en réalité des **Mio**
(1 Gio = 1 024 Mio) : pour 300 Gio, on saisit **300 × 1 024 = 307 200**.

**Procédure professionnelle (à rédiger)** : rappeler les deux unités → poser la division →
conclure « même capacité, deux unités ».

**Erreur fréquente** : attribuer l'écart à « la place prise par Windows » ou à un disque
défectueux.

**À l'écrit** : le calcul posé, avec les puissances (10^9, 2^30) et l'arrondi.

**Repère rapide** : **Go affiché par Windows ≈ Go vendus × 0,93**. Exercices liés :
{_ex("E07", "E08", "E09")}.
"""


def _tables() -> str:
    limit_gib = MBR_LIMIT_BYTES // GIB
    return f"""**Objectifs** : choisir la table de partitions d'un disque et expliquer ses limites.

## 5.1 Partition, table, volume

- Une **partition** est une zone continue du disque. La **table de partitions**, au début du
  disque, décrit où commence et où finit chaque partition.
- Un **volume** est une partition (ou un ensemble) **formatée** dans un système de fichiers et
  rendue accessible : une **lettre** sous Windows (C:, D:), un **point de montage** sous Linux
  (/, /home, /srv/donnees).
- **Initialiser** un disque (Windows) = y écrire une table de partitions vide (MBR ou GPT).

## 5.2 MBR ou GPT

{_mbr_gpt_table()}

La limite du MBR vient du calcul : les adresses de secteurs tiennent sur 32 bits, soit
2^32 × 512 octets = **{limit_gib} Gio (2 Tio)**. Sur un disque de 3 To en MBR, environ 746 Gio
restent inutilisables.

## 5.3 Règle de choix (disque vide, données sauvegardées)

- **GPT** : PC qui démarre en **UEFI** (obligatoire pour Windows 11), disque de **plus de
  2 Tio**, besoin de **plus de 4 partitions**, et en général tout disque de données récent
  (Windows lit un disque de données GPT même sur un ancien PC).
- **MBR** : seulement le **disque de démarrage** d'un PC **sans UEFI** (BIOS uniquement).
- **Convertir** MBR ↔ GPT avec Gestion des disques ou diskpart exige un disque **vide** :
  sauvegarde vérifiée d'abord (l'outil `mbr2gpt` de Windows convertit un disque système sans
  perte, mais on sauvegarde quand même).

**Procédure professionnelle (à rédiger)** : PC UEFI ou BIOS ? → disque de démarrage ou de
données ? → taille ? → nombre de partitions ? → table choisie et justifiée.

**Erreur fréquente** : initialiser en MBR un disque de 3 ou 4 To, ou « convertir » un disque
qui contient des données sans sauvegarde.

**À l'écrit** : la table **et** la raison (mode de démarrage, taille, nombre de partitions).

**Repère rapide** : **UEFI ou > 2 Tio → GPT · vieux PC BIOS, disque système → MBR**.
Exercices liés : {_ex("E06")}.
"""


def _boot() -> str:
    return f"""**Objectifs** : savoir de quelles partitions un système a besoin pour démarrer, et
reconnaître un plan de partitions correct.

## 6.1 Comment le PC trouve le système

- **UEFI + GPT** : le firmware lit la **partition EFI** (**ESP**, *EFI System Partition*,
  **FAT32**) et lance un **fichier chargeur** qui s'y trouve (`Windows Boot Manager`, `GRUB`).
  L'**ordre de démarrage** de l'UEFI désigne ce chargeur.
- **BIOS hérité + MBR** : le BIOS lit le premier secteur du disque, qui lance la **partition
  active** (« Réservé au système » sous Windows).
- Le mode de démarrage doit **correspondre** à la table : **GPT ↔ UEFI**, **MBR ↔ BIOS
  hérité (CSM)**. Passer le firmware en mode hérité sur un PC installé en UEFI donne « No
  bootable device » (exercice E15).

## 6.2 Trois plans de partitions à connaître

{_fig(PLANS_FIGURE)}

{_plans_tables()}

- La **MSR** (Microsoft Reserved, 16 Mo) n'a ni lettre ni système de fichiers : elle est
  normale sur un disque GPT Windows.
- La **partition de récupération** contient l'environnement de récupération (WinRE) : on ne la
  supprime pas pour « gagner » 750 Mo.
- Sous Linux, l'espace d'échange peut être une partition **swap** ou un **fichier**
  d'échange ; ESP et racine restent indispensables.

**Procédure professionnelle (à rédiger)** : mode de démarrage → table → partitions dans
l'ordre avec système de fichiers, taille et rôle → schéma.

**Erreur fréquente** : supprimer ou formater la partition EFI « parce qu'elle n'a pas de
lettre » : le PC ne démarre plus, même si C: est intact.

**À l'écrit** : un plan **complet et ordonné** : nom, système de fichiers, taille, rôle.

**Repère rapide** : **UEFI : ESP (FAT32) + système · BIOS : partition active + système**.
Exercices liés : {_ex("E08", "E09", "E15")}.
"""


def _formatting() -> str:
    return f"""**Objectifs** : distinguer partitionner, formater et effacer, et connaître les quatre
systèmes de fichiers du programme.

## 7.1 Formater, c'est quoi ?

- **Formatage logique** : écrire dans une partition un **système de fichiers vide** (tables,
  répertoire racine). C'est ce que font Windows (Formater, `format`) et Linux (`mkfs`).
- **Formatage rapide** : seulement ces structures. **Formatage complet** (Windows) : en plus,
  il parcourt tout le volume, écrit des zéros (Windows récents) et repère les secteurs
  défectueux — beaucoup plus long.
- Le « formatage **de bas niveau** » (pistes et secteurs) est fait **en usine** ; un technicien
  ne le refait pas.
- **Formater n'efface pas** de façon sûre : les anciens fichiers restent souvent
  récupérables. Pour rendre des données illisibles : effacement sécurisé adapté au support
  ([PR04](/uaa/ampcr-pratique-pr04)).

## 7.2 Quatre systèmes de fichiers

{_fs_table()}

- **Journal** : le système note ses opérations avant de les faire ; après une coupure, il
  se remet en état cohérent sans long contrôle (NTFS, ext4).
- **Droits** : propriétaire et permissions sur chaque fichier et dossier (NTFS, ext4) ;
  FAT32 et exFAT n'en ont pas.
- **FAT32** refuse tout fichier de plus de **{f"{FAT32_MAX_FILE:,}".replace(",", " ")} octets** (4 Gio moins 1) :
  une vidéo de 6 Go ne passe pas. L'outil de
  formatage de Windows ne propose d'ailleurs FAT32 que pour des volumes de 32 Go au plus.

**Procédure professionnelle (à rédiger)** : nommer l'opération (partitionner / formater /
effacer) → choisir le système de fichiers → rapide ou complet selon l'état du disque.

**Erreur fréquente** : croire qu'un formatage rapide « efface tout » avant de donner un disque.

**À l'écrit** : ne jamais employer « formater » pour « effacer de façon sûre ».

**Repère rapide** : **partitionner = découper · formater = organiser · effacer = rendre
illisible**. Exercices liés : {_ex("E16")}.
"""


def _choose_fs() -> str:
    return f"""**Objectifs** : choisir le système de fichiers d'après l'usage réel du support.

## 8.1 La règle du cours

| Usage | Système de fichiers | Pourquoi |
|---|---|---|
| Partition système Windows, disque de données sous Windows | **NTFS** | journal, droits d'accès, grands fichiers |
| Partition système ou de données Linux | **ext4** | journal, droits, système natif de Linux |
| Partition EFI (ESP) | **FAT32** | exigé par le firmware UEFI |
| Clé, carte, disque externe échangé entre Windows, macOS et Linux | **exFAT** | lu et écrit partout, fichiers de plus de 4 Gio |
| Petite clé pour un appareil ancien (autoradio, TV, mise à jour du firmware) | **FAT32** | seul système lu par l'appareil ; fichiers de moins de 4 Gio |

## 8.2 Les trois questions à se poser

1. **Qui doit lire et écrire** ce support (Windows seul, Linux seul, plusieurs systèmes, un
   appareil) ?
2. **Quelle taille** pour le plus gros fichier (plus de 4 Gio → pas FAT32) ?
3. A-t-on besoin de **droits d'accès** et d'un **journal** (disque interne, sauvegardes) ?

**Procédure professionnelle (à rédiger)** : usage → lecteurs → taille du plus gros fichier →
droits → système choisi et justifié ; **sauvegarde avant reformatage** d'un support qui
contient déjà des fichiers.

**Erreur fréquente** : FAT32 « parce que ça marche partout » pour des vidéos de plusieurs Go,
ou NTFS sur une clé qu'un Mac doit modifier (macOS lit le NTFS mais ne l'écrit pas sans outil).

**À l'écrit** : le système **et** deux justifications (compatibilité, taille de fichier,
droits).

**Repère rapide** : **Windows → NTFS · Linux → ext4 · ESP → FAT32 · échange → exFAT**.
Exercices liés : {_ex("E04", "E16")}.
"""


def _windows() -> str:
    return f"""**Objectifs** : créer, modifier et contrôler des partitions sous Windows, avec
l'interface graphique et en ligne de commande.

## 9.1 Gestion des disques (diskmgmt.msc)

| Besoin | Action dans Gestion des disques | Attention |
|---|---|---|
| Disque neuf | Initialiser (GPT) → Nouveau volume simple → taille, lettre, NTFS | disque **neuf** seulement |
| Agrandir C: | Étendre le volume | l'espace **non alloué** doit suivre **immédiatement** C: |
| Faire de la place | Réduire le volume | limité par les fichiers non déplaçables |
| Lecteur invisible | Modifier la lettre de lecteur et les chemins d'accès | aucune donnée touchée |
| Effacer une partition | Supprimer le volume | **détruit l'accès aux données** : sauvegarde vérifiée |

Sur un disque Windows récent, la partition de **récupération** est souvent placée juste après
C: : elle empêche « Étendre » d'utiliser l'espace libre situé plus loin. On ne la supprime pas
à la légère ; on documente et on demande conseil.

{_fig(WIN_NEW_DISK_FIGURE)}

## 9.2 diskpart (ligne de commande)

{_console("diskpart", "list disk", "select disk 1", "detail disk", "convert gpt", "create partition primary", 'format fs=ntfs quick label="Donnees"', "assign letter=D", "list volume")}

- **`list disk` puis `detail disk`** : on vérifie le **numéro**, la **taille** et le contenu du
  disque **avant** toute commande qui écrit.
- `convert gpt` ne fonctionne que sur un disque **vide**.
- **`clean`** efface la table de partitions de **tout** le disque sélectionné : réservé à un
  disque qu'on veut volontairement vider, après sauvegarde vérifiée et accord écrit.

**Procédure professionnelle (à rédiger)** : identifier le disque (numéro, taille, contenu) →
sauvegarde si données → action dans Gestion des disques ou diskpart → contrôle (lettre,
taille, fichier test).

**Erreur fréquente** : `select disk 1` sans `list disk` : le numéro des disques change selon
les branchements, et l'on vide le mauvais disque.

**À l'écrit** : les actions dans l'ordre, chacune avec ce qu'on **vérifie**.

**Repère rapide** : **identifier → sauvegarder → agir → contrôler**. Exercices liés :
{_ex("E01", "E02", "E14")}.
"""


def _linux() -> str:
    return f"""**Objectifs** : préparer un disque sous Linux et le monter de façon permanente.

## 10.1 Noms des disques

- Disques SATA et USB : **`/dev/sda`**, `/dev/sdb`… ; partitions : `/dev/sdb1`, `/dev/sdb2`.
- SSD NVMe : **`/dev/nvme0n1`** ; partitions : `/dev/nvme0n1p1`, `/dev/nvme0n1p2`.
- Ces noms **peuvent changer** d'un démarrage à l'autre (ordre de détection) : dans
  `/etc/fstab`, on désigne la partition par son **UUID** (identifiant unique du système de
  fichiers, lu avec `blkid`).

## 10.2 Les commandes

| Commande | Rôle |
|---|---|
| `lsblk -f` | disques, partitions, systèmes de fichiers, points de montage |
| `sudo parted /dev/sdb mklabel gpt` | créer une table GPT (efface la table existante) |
| `sudo parted -a optimal /dev/sdb mkpart donnees ext4 0% 100%` | créer une partition sur tout le disque |
| `sudo mkfs.ext4 -L donnees /dev/sdb1` | formater en ext4 avec un nom |
| `sudo mount /dev/sdb1 /srv/donnees` | monter (le dossier doit exister) |
| `sudo blkid /dev/sdb1` | lire l'UUID |
| `sudo mount -a` | tester `/etc/fstab` sans redémarrer |
| `df -h` | espace utilisé et libre de chaque volume |

D'autres outils font le même travail (`fdisk`, `gdisk`, l'outil graphique GParted) ; la
démarche reste la même.

{_fig(LINUX_NEW_DISK_FIGURE)}

{_fig(LSBLK_FIGURE)}

Ligne ajoutée dans `/etc/fstab` (UUID fictif) :

{_console(FSTAB_LINE)}

**Procédure professionnelle (à rédiger)** : `lsblk` (bon disque, vide) → table → partition →
`mkfs` → dossier et `mount` → UUID et `fstab` → `mount -a` → `df -h`.

**Erreur fréquente** : écrire `/dev/sdb1` dans `fstab` (le nom peut changer) ou ne pas tester
avec `mount -a` : une faute de frappe peut bloquer le démarrage.

**À l'écrit** : les commandes complètes, dans l'ordre, avec le **disque vérifié** d'abord.

**Repère rapide** : **lsblk → parted → mkfs → mount → blkid → fstab → mount -a**.
Exercices liés : {_ex("E03", "E09")}.
"""


def _backup() -> str:
    return f"""**Objectifs** : ne jamais perdre de données pendant une opération de stockage.

## 11.1 Pourquoi sauvegarder avant

Créer, supprimer, réduire, étendre, convertir une partition, formater, initialiser : chacune
de ces opérations peut **rendre les données inaccessibles** — par erreur de sélection, par
coupure de courant ou parce que le disque faiblit. La sauvegarde **précède** toujours
l'opération.

## 11.2 Une sauvegarde qui compte

- **Accord écrit** du propriétaire sur l'opération et sur le sort des données
  ([PR04](/uaa/ampcr-pratique-pr04)).
- Copie sur **un autre support** (disque externe, partage réseau) — jamais sur une autre
  partition **du même disque**.
- Copie **vérifiée** : on ouvre quelques fichiers sur la copie, on compare tailles et nombres.
- Bonne pratique pour le client : la règle **3-2-1** (trois copies, deux supports différents,
  une copie hors du lieu).

## 11.3 Travailler de façon non destructive

{_fig(SAFE_FIGURE)}

- Disque **qui contenait des données** et qui apparaît **non initialisé** ou **RAW** : on
  n'initialise pas, on ne formate pas ; on lit l'état SMART et on **récupère d'abord**.
- Disque qui **faiblit** : on en fait une **image** (copie secteur par secteur) avant toute
  tentative de réparation.
- Une opération à la fois, relue avant validation ; le résultat est contrôlé et noté.

**Procédure professionnelle (à rédiger)** : identifier → SMART → sauvegarder → vérifier la copie
→ relever l'état → agir → contrôler.

**Erreur fréquente** : « sauvegarder » les données de D: sur C: avant de repartitionner le
**même** disque.

**À l'écrit** : la sauvegarde nommée **avant** l'opération, avec le support et la
vérification.

**Repère rapide** : **pas de copie vérifiée sur un autre support, pas d'opération**.
Exercices liés : {_ex("E01", "E10", "E11", "E13")}.
"""


def _smart() -> str:
    return f"""**Objectifs** : lire l'état SMART d'un disque et en tirer une décision prudente.

## 12.1 Ce qu'est SMART

L'autosurveillance des disques (SMART) enregistre des **compteurs** : heures de
fonctionnement, secteurs réalloués, secteurs en attente, erreurs, température, usure d'un SSD.
On les lit avec un utilitaire (CrystalDiskInfo sous Windows, `smartctl -a` de smartmontools
sous Linux) ou avec l'outil du fabricant.

## 12.2 Les attributs à lire

| Attribut | Ce qu'il dit | Règle du cours |
|---|---|---|
| Secteurs réalloués (`Reallocated_Sector_Ct`) | zones défectueuses déjà remplacées | > 0 seul → **à surveiller** |
| Secteurs en attente (`Current_Pending_Sector`) | zones que le disque n'arrive plus à lire | > 0 → **à remplacer** |
| Secteurs illisibles (`Offline_Uncorrectable`) | erreurs non corrigées | > 0 → **à remplacer** |
| Erreurs CRC (`UDMA_CRC_Error_Count`) | données abîmées **pendant le transfert** | > 0 → **câble ou connecteur** à contrôler |
| Usure d'un SSD NVMe (`Percentage_Used`) | part de l'endurance consommée | ≥ 80 % surveiller, ≥ 100 % remplacer |

Ces seuils sont des **conventions du cours** (reprises de PR04), pas des normes : la fiche
du fabricant fait foi.

## 12.3 Interpréter avec prudence

- Le résumé **« PASSED / OK » ne suffit jamais** : on lit les attributs (cas 2 de PR04).
- Un relevé **bon** ne garantit pas l'avenir : un disque peut tomber en panne **sans alerte
  préalable**. SMART ne remplace pas une sauvegarde.
- Un compteur se suit dans le temps : un nombre de secteurs réalloués **qui augmente** est plus
  inquiétant qu'un petit nombre stable.
- Des erreurs **CRC** désignent d'abord la **liaison** : on change le câble SATA avant de
  condamner le disque ; le compteur ne redescend jamais, on vérifie qu'il **n'augmente plus**.
- Disque **à remplacer** : sauvegarde immédiate, **aucune** défragmentation, aucun
  redimensionnement, remplacement.

**Procédure professionnelle (à rédiger)** : relever les attributs → appliquer la règle → décider
(bon / à surveiller / à remplacer / câble) → conseiller (sauvegarde, nouveau relevé) → noter les
valeurs.

**Erreur fréquente** : écrire « disque OK » parce que le résumé affiche PASSED, ou défragmenter
un disque qui a des secteurs en attente.

**À l'écrit** : les **valeurs** relevées, le verdict, et une décision **prudente**.

**Repère rapide** : **lire les attributs · en attente ou illisibles → remplacer · réalloués →
surveiller · CRC → câble**. Exercices liés : {_ex("E13")}.
"""


def _optimise() -> str:
    rows = "\n".join(
        f"| {drive} | {media} | {state} | {optimisation_for(media)} |" for drive, media, state, _f in OPTIMISE_ROWS
    )
    hdd_frag = next(f for _d, m, _s, f in OPTIMISE_ROWS if m == MEDIA_HDD)
    return f"""**Objectifs** : appliquer l'entretien adapté au type de support.

## 13.1 Défragmentation : pour le disque dur

- Un fichier **fragmenté** est écrit en morceaux éparpillés : la tête doit se déplacer plusieurs
  fois pour le lire, d'où la lenteur.
- La **défragmentation** regroupe les morceaux. Windows l'appelle « **optimisation** » et la
  **planifie** chaque semaine (« Optimiser les lecteurs », `dfrgui`).
- Il faut de l'**espace libre** (environ 15 % ou plus) ; l'opération peut être longue mais
  s'interrompt sans danger.
- Convention du cours : on lance une défragmentation manuelle au-delà de
  **{FRAGMENTATION_ALERT} % fragmenté**.
- On ne défragmente **pas** un disque qui a des secteurs en attente : on **sauvegarde**.
- Sous Linux, ext4 limite la fragmentation : on ne défragmente généralement pas.

## 13.2 TRIM : pour le SSD

- Un SSD lit n'importe quel bloc aussi vite : la fragmentation ne le ralentit pas.
- **La défragmentation n'apporte rien à un SSD** et consomme des écritures (endurance).
- L'entretien d'un SSD, c'est **TRIM** : Windows l'envoie depuis « Optimiser les lecteurs »
  (état « dernier découpage ») ; sous Linux, le service planifié `fstrim.timer` (ou
  `sudo fstrim -v /`).
- La **répartition de l'usure** est faite par le contrôleur lui-même : rien à lancer.

## 13.3 Lire « Optimiser les lecteurs »

{_fig(OPTIMISE_SCREEN_FIGURE)}

| Lecteur | Type | État | Entretien |
|---|---|---|---|
{rows}

Ici, seul le disque dur D: ({hdd_frag} % fragmenté) {'a besoin' if needs_defrag(MEDIA_HDD, hdd_frag) else "n'a pas besoin"}
d'une défragmentation.

{_fig(OPTIMISE_FIGURE)}

**Procédure professionnelle (à rédiger)** : type de support → état SMART → espace libre →
défragmentation (disque dur) ou TRIM (SSD) → planification → contrôle.

**Erreur fréquente** : installer un défragmenteur tiers sur un SSD, ou défragmenter un disque
qui perd des secteurs.

**À l'écrit** : pour chaque lecteur, **l'action et sa raison** (type de support, pourcentage,
état SMART).

**Repère rapide** : **disque dur → défragmenter (si > {FRAGMENTATION_ALERT} %) · SSD → TRIM,
jamais défragmenter**. Exercices liés : {_ex("E05", "E12")}.
"""


def _symptoms() -> str:
    return f"""**Objectifs** : reconnaître les pannes de stockage courantes et commencer par une action
qui ne modifie pas le disque.

## 14.1 Six symptômes

{_symptoms_table()}

## 14.2 Le disque « disparu »

{_fig(MISSING_TREE_FIGURE)}

{_fig(NOT_DETECTED_FIGURE)}

## 14.3 Espace plein

- On **mesure** d'abord (Paramètres > Système > Stockage ; `df -h` et `du` sous Linux).
- On libère par les outils prévus : corbeille, **Nettoyage de disque** (fichiers temporaires,
  anciennes mises à jour), Assistant Stockage, désinstallation propre, **déplacement** des
  données personnelles vers un disque de données.
- On ne supprime **jamais** à la main dans `C:\\Windows` ou les dossiers de programmes.

## 14.4 Démarrage impossible

« No bootable device », « Operating system not found », « BOOTMGR is missing » : on vérifie
dans l'UEFI que le disque est **détecté**, que le **gestionnaire de démarrage** est en tête de
l'ordre et que le **mode** (UEFI ou hérité) correspond à la table (GPT ou MBR). Un changement
du **mode SATA** (AHCI ↔ RAID) après l'installation peut aussi provoquer l'écran bleu
« INACCESSIBLE_BOOT_DEVICE » : on remet le réglage d'origine. La réparation du démarrage
elle-même est traitée en [PR11](/uaa/ampcr-pratique-pr11).

**Procédure professionnelle (à rédiger)** : observer (UEFI, Gestion des disques, message
exact) → hypothèse → action non destructive → contrôle → rapport.

**Erreur fréquente** : formater, initialiser ou réinstaller « pour voir » : c'est
l'intervention qui fait perdre les données, pas la panne.

**À l'écrit** : le symptôme, la cause probable, la **première action non destructive** et ce
qu'on ne fait pas.

**Repère rapide** : **absent de l'UEFI → matériel · non initialisé / RAW → récupérer d'abord ·
plein → mesurer puis nettoyer · pas de démarrage → mode et ordre**. Exercices liés :
{_ex("E10", "E11", "E14", "E15")}.
"""


def _examples() -> str:
    c_size = fr_number(CASE4_C_GIB)
    d_size = fr_number(CASE4_D_GIB)
    return f"""## Cas 1 — Un disque dur neuf invisible dans l'Explorateur

**Situation.** Tu viens d'installer un disque dur neuf vendu « 2 To » dans la tour UEFI d'un
photographe, à côté de son SSD système. Le disque apparaît dans l'UEFI, mais pas dans
l'Explorateur. Gestion des disques affiche :

{_fig(DISKMGMT_FIGURE)}

**Résolution.**

1. Le disque est vu par l'UEFI : le branchement est bon.
2. « Inconnu, Non initialisé, Non alloué » sur un disque **neuf** : il n'a encore ni table ni
   partition — c'est normal, aucune donnée n'est en jeu.
3. Initialiser en **GPT** (PC UEFI, disque de 2 To ; GPT reste le bon choix pour un disque
   récent).
4. Nouveau volume simple sur tout l'espace, lettre **D:**, **NTFS** (PC Windows), nom
   « Photos », formatage rapide (disque neuf).
5. Contrôle : D: visible, **{fr_number(CASE1_GIB)} Go** affichés — c'est bien 2 To
   (2 × 10^12 ÷ 2^30) —, fichier test écrit et relu.

**Conclusion rédigée.** « Disque dur 2 To neuf détecté dans l'UEFI, non initialisé : initialisé
en GPT, volume NTFS D: « Photos » créé ({fr_number(CASE1_GIB)} Go affichés, soit 2 To), test
d'écriture et de lecture correct. »

## Cas 2 — Une clé USB qui refuse une vidéo de 6 Go

**Situation.** Une monteuse vidéo veut copier un film de 6 Go sur sa clé de 64 Go pour le
travailler sur le Mac d'un studio. Windows répond « Le fichier est trop volumineux pour le
système de fichiers de destination ». La clé est en FAT32 et contient déjà des rushes.

**Résolution.**

1. **Cause** : FAT32 limite un fichier à 4 Gio moins 1 octet ; le film de 6 Go est
   {'accepté' if fits_on_fat32(6 * 10**9) else 'refusé'}, quel que soit l'espace libre.
2. **Choix** : exFAT — lu et écrit par Windows et macOS, sans limite pratique de taille de
   fichier. NTFS ne convient pas (le Mac le lit sans pouvoir y écrire).
3. **Sauvegarde** : le reformatage efface la clé → copie des rushes sur le PC, copie vérifiée.
4. Reformater la clé en **exFAT**, recopier les rushes puis le film.
5. Contrôle : le film s'ouvre sur le Mac.

**Conclusion rédigée.** « Clé en FAT32 (fichiers de 4 Gio au plus) : contenu sauvegardé et
vérifié, clé reformatée en exFAT, fichiers recopiés ; film de 6 Go copié et lu sur le Mac. »

## Cas 3 — PC lent : défragmenter… mais quoi ?

**Situation.** Un PC de bureau a un SSD NVMe (C:) et un disque dur de données (D:). Son
utilisateur demande « une défragmentation complète ». L'état SMART des deux supports est bon ;
« Optimiser les lecteurs » affiche la capture du chapitre 13 (C: OK, D: 27 % fragmenté).

**Résolution.**

1. **C:** est un SSD : pas de défragmentation (aucun gain, écritures inutiles). Le TRIM
   (« découpage ») a été fait il y a 3 jours : rien à faire.
2. **D:** est un disque dur à 27 % fragmenté, au-delà du seuil de {FRAGMENTATION_ALERT} % :
   SMART bon et espace libre suffisant → **optimiser D:**.
3. Vérifier que l'**optimisation planifiée** est active, pour que la situation ne se
   reproduise pas.
4. Contrôle : D: « OK (0 % fragmenté) » après l'opération ; si la lenteur persiste, chercher une
   autre cause (programmes au démarrage, espace, PR06).

**Conclusion rédigée.** « SSD C: non défragmenté (entretien par TRIM, à jour) ; disque dur D:
défragmenté (27 % → 0 %) ; optimisation hebdomadaire vérifiée. »

## Cas 4 — Le plan de partitions d'un poste d'atelier

**Situation.** Tu prépares un PC UEFI neuf avec un **SSD NVMe « {CASE4_SSD_GB} Go »** pour
Windows 11 et un **disque dur « {CASE4_HDD_TB} To »** pour les données. Rédige le plan de
partitions avec les tailles.

**Résolution.**

1. **Tables** : GPT pour les deux disques (PC UEFI, Windows 11).
2. **SSD** ({fr_number(gb_to_gib(CASE4_SSD_GB))} Gio) : disposition standard de Windows —
   EFI 100 Mo (FAT32), MSR 16 Mo, C: (NTFS), récupération ≈ 750 Mo (NTFS).
3. **C:** ≈ {fr_number(gb_to_gib(CASE4_SSD_GB))} − 0,10 − 0,02 − 0,73 ≈ **{c_size} Gio**.
4. **Disque dur** ({d_size} Gio) : une seule partition **D: Données**, NTFS.
5. Les dossiers Documents, Images… des utilisateurs peuvent être déplacés vers D: : une
   réinstallation de Windows ne touchera pas les données.

{_fig(CASE4_FIGURE)}

**Conclusion rédigée.** « Disque 0 (SSD NVMe {CASE4_SSD_GB} Go, GPT) : EFI 100 Mo FAT32, MSR
16 Mo, C: NTFS ≈ {c_size} Gio, récupération ≈ 750 Mo. Disque 1 (disque dur {CASE4_HDD_TB} To,
GPT) : D: NTFS {d_size} Gio. »
"""


def _pitfalls() -> str:
    return """> **Partitionner, formater ou initialiser sans sauvegarde vérifiée** sur un autre support et
> sans accord écrit du propriétaire.

> **Sélectionner le mauvais disque** (`select disk`, `/dev/sdX`) sans `list disk` ou `lsblk`.

> **Initialiser ou formater un disque qui contenait des données** parce qu'il apparaît « Non
> initialisé » ou « RAW » : on récupère d'abord.

> **Confondre Go et Gio** et croire qu'un disque de 1 To affiché à 931 Go est défectueux.

> **Initialiser en MBR un disque de plus de 2 To**, ou un disque système de PC UEFI.

> **Formater en FAT32 un support destiné à des fichiers de plus de 4 Gio.**

> **Supprimer la partition EFI ou de récupération** « pour gagner de la place ».

> **Défragmenter un SSD**, ou un disque dur qui a des secteurs en attente.

> **Croire qu'un formatage rapide efface les données** avant de donner un disque ;
> et la défragmentation n'efface rien non plus.

> **Se fier au résumé « PASSED »** sans lire les attributs SMART.

> **Supprimer à la main des fichiers de C:\\Windows** pour libérer de l'espace.

> **Réinstaller d'emblée** un PC qui ne démarre plus, au lieu de vérifier le mode de démarrage.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (précautions, disque sous
Windows, disque sous Linux), choix du système de fichiers, de la table de partitions et de
l'entretien selon le support, plans de partitions chiffrés, calcul Go/Gio, captures et relevés
à interpréter (disque non initialisé, RAW, « Optimiser les lecteurs », SMART), disque plein,
démarrage impossible et procédure à corriger. Rédige ta réponse sur papier **avant** d'ouvrir le
corrigé ; toute réponse équivalente et justifiée est acceptée. Ces mêmes exercices sont
proposés dans [S'entraîner](/uaa/{PR05_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR05_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (captures, relevés fictifs).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** Le **bon choix justifié** (support, table, système de
fichiers, entretien), les **calculs posés**, la **lecture correcte** des captures et relevés,
et les **précautions** (disque identifié, sauvegarde vérifiée) — pas la récitation de sigles.
Une autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Supports** : disque dur (plateaux, têtes, grande capacité, chocs) · SSD SATA (≈ 550 Mo/s,
  limite de l'interface) · SSD NVMe (PCIe, plusieurs Go/s) ; **M.2 = format, SATA ou NVMe =
  interface, la notice décide**.
- **Unités** : 1 Go = 10^9 octets, 1 Gio = 2^30 ; Windows affiche des Gio écrits « Go » ;
  1 To ≈ 931 Gio, 2 To ≈ 1 863 Gio.
- **Secteur** 512 ou 4 096 octets · **cluster** 4 Kio par défaut · **SSD** : pages, blocs,
  endurance (TBW), répartition de l'usure, TRIM.
- **MBR** : 2 Tio, 4 partitions principales, BIOS hérité · **GPT** : UEFI, grands disques,
  128 partitions, copie de secours.
- **Démarrage** : UEFI + GPT + ESP (FAT32) · BIOS + MBR + partition active ; mode et table
  doivent correspondre.
- **Plans** : Windows UEFI = EFI 100 Mo + MSR 16 Mo + C: + récupération · Windows BIOS =
  Réservé au système + C: · Linux UEFI = ESP + / + swap.
- **Formater** : rapide (structures) ou complet (zéros et secteurs défectueux) ; **n'efface
  pas** de façon sûre.
- **Systèmes de fichiers** : Windows → NTFS · Linux → ext4 · ESP → FAT32 · échange → exFAT ;
  FAT32 : fichiers de 4 Gio au plus.
- **Windows** : Gestion des disques, diskpart (`list disk` avant tout, `clean` = tout le disque).
- **Linux** : `lsblk -f`, `parted`, `mkfs.ext4`, `mount`, `blkid`, `/etc/fstab` par UUID,
  `mount -a`, `df -h`.
- **Avant toute opération** : identifier, SMART, sauvegarde sur un autre support, copie
  vérifiée, accord écrit.
- **SMART** : lire les attributs ; en attente ou illisibles → remplacer ; réalloués → surveiller ;
  CRC → câble ; un bon relevé ne garantit rien.
- **Entretien** : disque dur → défragmentation (au-delà de {FRAGMENTATION_ALERT} %) · SSD →
  TRIM, jamais de défragmentation.
- **Symptômes** : absent de l'UEFI → matériel · non initialisé ou RAW avec données → récupérer
  d'abord · plein → mesurer puis nettoyer · pas de démarrage → mode, ordre, détection.

## Glossaire des termes employés

- **Cluster (unité d'allocation)** : plus petite zone qu'un système de fichiers attribue à un
  fichier.
- **ESP (partition système EFI)** : partition FAT32 qui contient les chargeurs de démarrage UEFI.
- **exFAT** : système de fichiers pour supports amovibles, sans limite pratique de taille de
  fichier.
- **GPT / MBR** : deux formats de table de partitions.
- **Gio** : gibioctet, 2^30 = 1 073 741 824 octets.
- **Initialiser** : écrire une table de partitions vide sur un disque.
- **NVMe** : protocole d'accès aux SSD par le bus PCI Express.
- **RAW** : volume dont Windows ne reconnaît pas le système de fichiers.
- **Répartition de l'usure (wear leveling)** : répartition des écritures sur toutes les cellules
  d'un SSD.
- **SMART** : autosurveillance des disques (compteurs d'erreurs et d'usure).
- **TBW** : endurance d'un SSD en téraoctets écrits.
- **TRIM** : commande qui signale au SSD les blocs libérés.
- **UUID** : identifiant unique d'un système de fichiers, utilisé dans `/etc/fstab`.
- **Volume** : partition formatée et accessible (lettre ou point de montage).
"""


def _sources() -> str:
    return """## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigence AP-03
  « Les différents types de disque dur et unités de stockage, le formatage, la
  défragmentation ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Partitions et démarrage** : documentation Microsoft (partitions de disque dur UEFI/GPT et
  BIOS/MBR, Gestion des disques, diskpart, Optimiser les lecteurs) ; spécification UEFI
  (table GPT, partition système EFI).
- **Systèmes de fichiers** : documentation Microsoft (NTFS, FAT32, exFAT, formatage rapide et
  complet), documentation du noyau Linux (ext4, exFAT, ntfs3) et de Debian/Ubuntu (`parted`,
  `mkfs.ext4`, `/etc/fstab`, `fstrim.timer`).
- **Unités** : Système international (préfixes décimaux) et norme CEI 80000-13 (préfixes
  binaires Kio, Mio, Gio, Tio).
- **Interfaces** : spécifications SATA et NVMe (débits d'interface, M.2) ; notices des
  fabricants de cartes mères et de SSD.
- **SMART** : documentation de smartmontools (`smartctl`, attributs des disques durs et des SSD
  NVMe).

Les plans de partitions, les tableaux, les procédures, l'arbre de décision et les calculs de
capacité du cours sont **produits par programme** depuis des données **vérifiées par des tests
automatiques** ; aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 cite les types de disques, le formatage et la défragmentation (AP-03).
Sont des **compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- les tables de partitions MBR/GPT, la partition EFI et le démarrage (repris en PR08 et PR09
  pour l'installation des systèmes) ;
- la création des partitions sous Windows et Linux, les unités Go/Gio ;
- la lecture SMART et la protection des données (AP-C03, déjà vu en PR04) ;
- les seuils (fragmentation à 10 %, lecture SMART) : ce sont des **conventions du cours**, pas
  des normes ; la fiche du fabricant fait foi.

## Supports fictifs

Les captures, relevés et situations de ce cours sont **fictifs** et reconstitués pour
l'entraînement ; ils ne décrivent aucun produit réel. Aucun n'est une question officielle ou
déjà posée par le Jury.
"""


def pr05_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR05 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR05 — 1. Disque dur, SSD SATA et SSD NVMe : fonctionnement et choix", _media()),
        ("PR05 — 2. Interfaces et formats : SATA, M.2 et compatibilité", _interfaces()),
        ("PR05 — 3. Secteurs, clusters, pages et usure", _sectors()),
        ("PR05 — 4. Capacités : Go et Gio, To et Tio", _units()),
        ("PR05 — 5. Partitions, volumes et tables MBR ou GPT", _tables()),
        ("PR05 — 6. Démarrage : UEFI, partition EFI (ESP) et plans de partitions", _boot()),
        ("PR05 — 7. Formatage logique et systèmes de fichiers NTFS, FAT32, exFAT, ext4", _formatting()),
        ("PR05 — 8. Choisir le système de fichiers selon l'usage", _choose_fs()),
        ("PR05 — 9. Créer et gérer des partitions sous Windows", _windows()),
        ("PR05 — 10. Créer, formater et monter des partitions sous Linux", _linux()),
        ("PR05 — 11. Sauvegarde préalable et opérations non destructives", _backup()),
        ("PR05 — 12. SMART : lire l'état d'un disque avec prudence", _smart()),
        ("PR05 — 13. Défragmentation, TRIM et répartition de l'usure : disque dur contre SSD", _optimise()),
        ("PR05 — 14. Symptômes : disque absent, non initialisé, plein, démarrage impossible", _symptoms()),
        ("PR05 — Exemples : quatre cas intégralement résolus", _examples()),
        ("PR05 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR05 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR05 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR05 — Fiche mémo et glossaire", _memo()),
        ("PR05 — Sources et compléments pédagogiques", _sources()),
    ]
