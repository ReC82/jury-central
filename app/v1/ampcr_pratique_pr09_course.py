"""Cours PR09 « Installation complète de Linux — préparation et dépannage » — parcours AMPCR
pratique écrite (ticket #209).

Matière : intégralement celle du ticket #209 (choix de la distribution selon l'usage, image ISO
et contrôle d'intégrité, clé bootable, UEFI/GPT/ESP, session live, sauvegarde, racine /, /home
facultatif, swap selon le besoin, ext4, chargeur GRUB ou systemd-boot selon la distribution,
comptes et sudo, réseau, mises à jour apt/dnf, pilotes, services, tests, double démarrage avec
prudence ; diagnostic d'un disque non vu, du chargeur, de fstab/UUID, d'un réseau absent, des
permissions et de l'espace disque ; cinq cas résolus), découpée en blocs titrés (le titre pilote
le type de carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen »,
« source », « ressource », « exemple », « exercice », « méthode », « piège », « attention »,
« transfert » ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr09_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr09_bank`. Mise en forme partagée avec les autres cours pratiques.
Le choix du système et les prérequis relèvent de PR07, l'installation de Windows de PR08, les
messages d'erreur de PR11 (publiés, liens) ; les comptes et commandes (PR10) et la restauration
du système (PR12) ne sont pas publiés à la rédaction : renvoi en texte seulement.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr09_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr09_figures import (
    BOOT_TREE_FIGURE,
    CHECKLIST,
    DB_CREATE,
    DB_KEEP,
    DB_REUSE,
    DB_STOP,
    DF_FULL_FIGURE,
    DISTRIBUTIONS,
    DUAL_BOOT_FIGURE,
    EFIBOOT_FIGURE,
    FINAL_FIGURE,
    INVENTORY_FIELDS,
    ISO_BAD,
    ISO_CHECK_FIGURE,
    ISO_NAME,
    ISO_OK,
    LAYOUT_FIGURE,
    LINUX_ONLY_LAYOUT,
    PACKAGE_COMMANDS,
    PREP_FIGURE,
    PROCEDURES,
    REPORT_SECTIONS,
    SETUP_FIGURE,
    TR_CATEGORIES,
    TROUBLES_BY_CATEGORY,
    USAGE_CHOICES,
    WRITTEN_AT,
    swap_advice,
)

PR09_TITLE = "Installation complète de Linux — préparation et dépannage"
PR09_SLUG = "ampcr-pratique-pr09"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr09") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _inventory_table() -> str:
    rows = "\n".join(f"| **{field}** | {what} | {why} |" for field, what, why in INVENTORY_FIELDS)
    return "| Rubrique | Ce que l'on relève | Pourquoi |\n|---|---|---|\n" + rows


def _distributions_table() -> str:
    rows = "\n".join(
        f"| **{d.name}** | {d.family} | `{d.package_manager}` | {d.bootloader} | {d.default_fs} | {d.support} |"
        for d in DISTRIBUTIONS
    )
    return (
        "| Distribution | Famille | Paquets | Chargeur | Système de fichiers proposé | Support |\n"
        "|---|---|---|---|---|---|\n" + rows
    )


def _usage_table() -> str:
    rows = "\n".join(f"| {usage} | **{choice}** | {why} |" for usage, choice, why in USAGE_CHOICES)
    return "| Usage du client | Choix conseillé | Raison |\n|---|---|---|\n" + rows


def _packages_table() -> str:
    rows = "\n".join(f"| {action} | `{apt}` | `{dnf}` |" for action, apt, dnf in PACKAGE_COMMANDS)
    return "| Action | Debian, Ubuntu, Mint (apt) | Fedora (dnf) |\n|---|---|---|\n" + rows


def _layout_table() -> str:
    rows = "\n".join(
        f"| **{p.name}** | {p.filesystem} | `{p.mount_point}` | {p.size_label} | {p.role} |" for p in LINUX_ONLY_LAYOUT
    )
    return "| Partition | Système de fichiers | Point de montage | Taille indicative | Rôle |\n|---|---|---|---|---|\n" + rows


def _fmt_swap(value: float | None) -> str:
    return "déconseillée" if value is None else f"{value:g} Go"


def _swap_table() -> str:
    rows = "\n".join(
        f"| {ram} Go | {_fmt_swap(swap_advice(ram, hibernation=False))} | {_fmt_swap(swap_advice(ram, hibernation=True))} |"
        for ram in (2, 4, 8, 16, 32)
    )
    return "| Mémoire vive | Swap sans hibernation | Swap avec hibernation |\n|---|---|---|\n" + rows


def _troubles_tables() -> str:
    parts = []
    for number, category in enumerate(TR_CATEGORIES, start=1):
        rows = "\n".join(
            f"| {t.symptom} | {t.check} | {t.action} | {t.never} |" for t in TROUBLES_BY_CATEGORY[category]
        )
        parts.append(
            f"### 11.{number + 1} {category}\n\n"
            "| Symptôme | Vérifier | Agir | Ne jamais |\n|---|---|---|---|\n" + rows
        )
    return "\n\n".join(parts)


def _checklist_table() -> str:
    rows = "\n".join(f"| **{point}** | `{where}` | {expected} | ☐ |" for point, where, expected in CHECKLIST)
    return "| Point | Commande / outil | Résultat attendu | Fait |\n|---|---|---|---|\n" + rows


def _report_list() -> str:
    return "\n".join(f"{i}. **{title}** : {content}" for i, (title, content) in enumerate(REPORT_SECTIONS, start=1))


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
p. 3). On ne te demande pas d'installer Linux devant le jury, mais de **rédiger** une
installation complète et sûre, de **lire** des sorties de terminal et de **dépanner** par écrit
une installation qui échoue. Tu dois savoir :

1. **préparer** l'intervention : demande, **accord écrit**, **inventaire** du poste ;
2. **choisir** une distribution selon l'**usage** et le matériel ;
3. **télécharger** l'image ISO officielle, **contrôler son intégrité** et créer la **clé de
   démarrage** sans effacer le mauvais disque ;
4. **régler** le firmware **UEFI**, garder le **démarrage sécurisé** et **tester** le matériel en
   **session live** ;
5. **sauvegarder** et préparer un **double démarrage** avec prudence ;
6. **partitionner** en **GPT** : **ESP**, racine **/** en **ext4**, **/home** facultative,
   **swap** selon le besoin ;
7. **comprendre** le chargeur (**GRUB** ou **systemd-boot**) ;
8. **créer** les **comptes** et réserver **sudo** à l'administrateur ;
9. **finaliser** : réseau, **mises à jour** `apt`/`dnf`, **pilotes**, **services** ;
10. **dépanner** : disque non vu, chargeur, **fstab/UUID**, réseau absent, **permissions**,
    **espace disque** ;
11. **contrôler** avec une **liste de contrôle** et **rédiger le rapport d'intervention**.

Ce cours contient **3 procédures illustrées** :

{_procedures_list()}

## Exigence officielle travaillée dans ce cours

{_req("AP-10")}

Le cours s'appuie aussi sur la protection des données du client vue en
[PR04](/uaa/ampcr-pratique-pr04) :

{_req("AP-C03")}

Les systèmes du marché, le choix d'un système et les prérequis (UEFI, démarrage sécurisé) sont
expliqués en [PR07](/uaa/ampcr-pratique-pr07) ; l'installation de Windows, ses partitions et
son activation en [PR08](/uaa/ampcr-pratique-pr08) ; les partitions et systèmes de fichiers en
[PR05](/uaa/ampcr-pratique-pr05) ; le diagnostic d'un disque en [PR06](/uaa/ampcr-pratique-pr06) ;
les messages de démarrage de Linux (`grub rescue>`, mode d'urgence) en
[PR11](/uaa/ampcr-pratique-pr11). Les comptes, pilotes et commandes (PR10) et la restauration du
système (PR12) font l'objet des cours suivants du parcours.

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC07 BIOS, UEFI, POST et démarrage](/uaa/ampcr-mc07),
[MC08 Partitionnement, GPT/MBR et formatage](/uaa/ampcr-mc08),
[MC11 Linux : bases utiles au technicien PC-réseaux](/uaa/ampcr-mc11) et
[MC30 Dépannage Windows et Linux](/uaa/ampcr-mc30). Ce cours-ci est **pratique** : procédures
rédigées, terminaux à lire, pannes à résoudre et rapports, comme dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner »,
correction après envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet
« Examen blanc ».

> **Important —** les terminaux, relevés et situations de ce cours sont des **supports fictifs**
> construits pour s'entraîner. Les **sorties de commandes sont montrées en anglais** (système
> réglé en anglais, ou commande précédée de `LANG=C`) : sur un système en français, une partie
> des messages est traduite. Les libellés des installateurs changent selon la distribution et la
> version (rédaction : {WRITTEN_AT}) : la **documentation de la distribution fait foi**. Aucun
> exercice n'est une question officielle ni une question déjà posée par le Jury. **Installer un
> système efface les partitions choisies : jamais sans sauvegarde vérifiée et accord écrit du
> propriétaire.**
"""


def _prepare() -> str:
    return f"""**Objectifs** : recueillir la demande, obtenir l'autorisation et relever tout ce qui
décidera de l'installation, avant de toucher au poste.

## 1.1 La demande et l'accord écrit

- On note **l'usage** (bureautique, Internet, serveur de fichiers, développement), **ce qu'il
  faut garder** (données, comptes) et si **Windows doit rester** (double démarrage).
- Toute installation **modifie ou efface** des partitions : il faut l'**accord écrit** du
  propriétaire (bon d'intervention signé), qui précise ce qui peut être effacé. Un accord oral
  ne suffit pas.
- Les données du client sont **confidentielles** : on les copie, on ne les consulte pas.

## 1.2 La fiche d'inventaire

{_inventory_table()}

{_fig(PREP_FIGURE)}

Outils : sous Windows, `msinfo32` (mode du BIOS, démarrage sécurisé), Gestion des disques et
Gestionnaire de périphériques ([PR07](/uaa/ampcr-pratique-pr07)) ; depuis une session live,
`lsblk`, `lspci -nn` (identifiants des puces), `free -h` (mémoire).

**Procédure professionnelle (à rédiger)** : demande → accord écrit → fiche d'inventaire →
liste de ce qu'il faut sauvegarder et préparer (câble réseau, pilote non libre, clé BitLocker).

**Erreur fréquente** : démarrer sur la clé sans savoir si Windows doit rester, si le disque est
chiffré par BitLocker ou si la carte Wi-Fi demande un pilote non libre.

**À l'écrit** : la **fiche** (rubrique — relevé) puis, pour chaque relevé important, **ce qu'il
change** à la préparation.

**Repère rapide** : **demande → accord écrit → inventaire**. Exercices liés : {_ex("E01", "E07")}.
"""


def _distribution() -> str:
    return f"""**Objectifs** : choisir une distribution adaptée à l'usage et au matériel, et connaître
ses outils (paquets, chargeur, système de fichiers).

## 2.1 Distribution, famille et support

- **Linux** est un **noyau** ; une **distribution** l'assemble avec des programmes, un
  installateur, un **gestionnaire de paquets** et un **bureau** (GNOME, KDE Plasma, Cinnamon,
  Xfce). Les systèmes du marché sont comparés en [PR07](/uaa/ampcr-pratique-pr07).
- Pour un client, on choisit une version **à support long** (LTS) : elle reçoit des mises à jour
  de sécurité pendant plusieurs années.

{_distributions_table()}

*Valeurs par défaut des installateurs graphiques en {WRITTEN_AT} ; la documentation de chaque
distribution fait foi. Dans ce cours, les partitions de Linux sont en **ext4** ; Fedora propose
Btrfs par défaut, ext4 reste possible en partitionnement manuel.*

## 2.2 Choisir selon l'usage

{_usage_table()}

*Ce tableau est une **convention du cours**, pas une norme : on justifie toujours son choix par
l'usage, le matériel (mémoire, processeur 64 bits) et la durée de support.*

**Procédure professionnelle (à rédiger)** : usage et matériel relevés → distribution et version
à support long → justification (simplicité, durée de support, besoin de logiciels récents) →
configuration recommandée comparée à l'inventaire.

**Erreur fréquente** : choisir « la distribution du moment » sans regarder la durée de support ;
un bureau lourd sur un PC de 4 Go de mémoire.

**À l'écrit** : **usage → choix → deux raisons**.

**Repère rapide** : **usage + matériel + support long**. Exercices liés : {_ex("E01")}.
"""


def _iso_media() -> str:
    return f"""**Objectifs** : obtenir une image fiable, contrôler son intégrité et écrire la clé de
démarrage sans effacer un autre disque.

## 3.1 Télécharger et contrôler l'image ISO

- Source : **site officiel** de la distribution (ou un miroir qu'il liste), jamais un site de
  partage.
- Le site publie un fichier de **sommes de contrôle** (`SHA256SUMS` pour Ubuntu et Debian, fichier
  `CHECKSUM` pour Fedora) ; on calcule la somme **SHA-256** de l'image et on compare :
  `sha256sum -c SHA256SUMS --ignore-missing` (Linux) ; `Get-FileHash fichier.iso -Algorithm
  SHA256` sous Windows ([PR07](/uaa/ampcr-pratique-pr07)).
- Résultat « `: OK` » → **{ISO_OK}**. Résultat « `: FAILED` » → **{ISO_BAD}**. La **taille** du
  fichier ne prouve rien.
- Pour aller plus loin, la distribution signe ce fichier (signature GPG) : on peut vérifier qu'il
  vient bien d'elle.

## 3.2 Créer la clé USB de démarrage

- Clé de **8 Go au moins** (l'image d'Ubuntu Desktop dépasse 5 Go), **entièrement effacée** par
  l'opération.
- Outils : **balenaEtcher** (ne propose que les supports amovibles), **Rufus** sous Windows
  (schéma **GPT**, cible **UEFI**), ou **`dd`** sous Linux.
- Avec `dd`, la cible est le **disque entier** de la clé, identifié par sa **taille** et son
  **transport** (`usb`) :

{_fig(ISO_CHECK_FIGURE)}

{_console(f"$ sudo dd if={ISO_NAME} of=/dev/sdb bs=4M status=progress oflag=sync")}

`dd` **n'avertit pas** : une erreur de cible (`of=/dev/sda`) efface ce disque. On écrit sur
`/dev/sdb` (le disque), **pas** sur `/dev/sdb1` (une partition).

**Procédure professionnelle (à rédiger)** : image du site officiel → somme contrôlée (« OK ») →
cible identifiée (`lsblk -d`, taille, `usb`) → écriture → test de démarrage.

**Erreur fréquente** : écrire une image non contrôlée ; viser `/dev/sda` « parce que c'est
toujours la clé ».

**À l'écrit** : **source → contrôle → résultat → outil et cible**.

**Repère rapide** : **site officiel · sha256sum -c = OK · cible vérifiée**. Exercices liés :
{_ex("E08", "E09")}.
"""


def _firmware_live() -> str:
    return f"""**Objectifs** : démarrer la clé dans le bon mode, garder le démarrage sécurisé et tester le
matériel avant de modifier le disque.

## 4.1 Firmware UEFI et démarrage sécurisé

- **Mode UEFI** (CSM désactivé) : Linux s'installe alors sur un disque **GPT** avec une
  **partition système EFI** ; en double démarrage, **les deux systèmes doivent démarrer dans le
  même mode** que Windows (UEFI).
- **Démarrage sécurisé** : Ubuntu, Linux Mint, Debian et Fedora démarrent avec lui grâce au
  petit chargeur **shim**, signé ; on le **laisse actif** (`mokutil --sb-state` →
  `SecureBoot enabled`). Un pilote compilé sur le PC (par exemple NVIDIA) est signé par une **clé
  locale (MOK)** à **enrôler** au redémarrage : écran « Perform MOK management » → **« Enroll
  MOK »** → mot de passe choisi pendant l'installation.
- **Mode du contrôleur de stockage** (AHCI, RAID / Intel RST, VMD) : à **noter**. Certains
  installateurs ne voient pas un disque derrière Intel RST (voir le chapitre 11).

## 4.2 Démarrer sur la clé

- **Menu de démarrage** (selon le fabricant : F12, F11, F8, Échap) : entrée **« UEFI: »** de la
  clé. Le menu de la clé (GRUB) propose d'**essayer** ou d'**installer**.

## 4.3 La session live : tester avant d'installer

La **session live** fait tourner le système **depuis la clé, sans rien écrire sur le disque**.
On y teste : **Wi-Fi** et Ethernet, **écran** (résolution), **son**, pavé tactile, webcam, et
on vérifie les disques vus (`lsblk`). Un matériel qui ne fonctionne pas en live demandera un
**pilote** après l'installation (souvent non libre : case « logiciels tiers »).

**Procédure professionnelle (à rédiger)** : firmware en UEFI, démarrage sécurisé actif, mode du
stockage noté → entrée « UEFI: » → session live → liste des tests et résultats.

**Erreur fréquente** : désactiver le démarrage sécurisé « parce que Linux ne le supporte pas » ;
installer directement sans tester le Wi-Fi.

**À l'écrit** : **réglages du firmware → mode de démarrage → tests en live et résultats**.

**Repère rapide** : **UEFI · Secure Boot actif (shim) · tester en live d'abord**. Exercices
liés : {_ex("E02", "E07")}.
"""


def _backup_dual_boot() -> str:
    return f"""**Objectifs** : protéger les données et préparer un double démarrage Windows + Linux sans
rien perdre.

## 5.1 Sauvegarde vérifiée

- On copie **sur un autre support** les données de **tous les comptes** (et, en double démarrage,
  celles de Windows) ; on **vérifie** la copie (nombre et taille des fichiers, ouverture de
  quelques fichiers). Même si « on ne touche pas à Windows », un redimensionnement peut échouer.

## 5.2 Double démarrage : préparer Windows d'abord

1. **Clé de récupération BitLocker** relevée et conservée hors du PC (un changement du démarrage
   peut la faire demander).
2. **Démarrage rapide** de Windows **désactivé** (Options d'alimentation) : sinon la partition
   Windows reste dans un état d'hibernation, risqué à modifier.
3. **Réduire C:** **depuis Windows** (Gestion des disques → « Réduire le volume ») pour libérer
   de l'**espace non alloué** (par exemple 100 Go).
4. Démarrer la clé **en UEFI**, comme Windows.

## 5.3 Dans le partitionnement manuel

{_fig(DUAL_BOOT_FIGURE)}

| Zone du disque | Action |
|---|---|
| Partition système EFI de Windows (≈ 100 Mo, vfat) | **{DB_REUSE}** |
| Partition réservée Microsoft, Windows, récupération, disques de données | **{DB_KEEP}** |
| Espace libre préparé depuis Windows | **{DB_CREATE}** (/ en ext4, swap) |
| Pas de sauvegarde vérifiée ou pas d'accord écrit | **{DB_STOP}** |

L'installateur d'Ubuntu propose aussi « Installer à côté de Windows » : utile, mais on vérifie
**l'écran récapitulatif** avant de valider. **« Effacer le disque » supprime Windows** et ses
données : jamais dans un double démarrage. Si l'option « à côté » n'apparaît pas : pas d'espace
libre, démarrage rapide ou chiffrement, ou clé démarrée dans un autre mode que Windows.

**Procédure professionnelle (à rédiger)** : sauvegarde vérifiée → clé BitLocker → démarrage
rapide désactivé → C: réduite depuis Windows → clé en UEFI → ESP réutilisée sans formatage →
Linux dans l'espace libre → les deux systèmes testés.

**Erreur fréquente** : **formater l'ESP** de Windows (son chargeur disparaît) ; réduire Windows
depuis l'installateur sans sauvegarde ; choisir « Effacer le disque ».

**À l'écrit** : la **préparation dans l'ordre** et, pour chaque partition, **l'action**.

**Repère rapide** : **sauvegarde · BitLocker · démarrage rapide off · réduire depuis Windows ·
ESP non formatée**. Exercices liés : {_ex("E06", "E07", "E10")}.
"""


def _partitions() -> str:
    return f"""**Objectifs** : établir et justifier un plan de partitions : ESP, racine, /home, swap,
système de fichiers ext4.

## 6.1 Les partitions d'une installation de Linux (GPT, UEFI)

{_layout_table()}

{_fig(LAYOUT_FIGURE)}

- Sous Linux, on ne parle pas de lettres (C:, D:) mais de **points de montage** : chaque
  partition est « accrochée » à un dossier de l'arborescence unique qui part de **/**.
- **ext4** est le système de fichiers proposé par Ubuntu, Debian et Linux Mint : journalisé,
  fiable et compatible avec tous les outils de dépannage.
- **/home séparée (facultative)** : on peut réinstaller le système en reformatant **/** seulement
  et en remontant **/home sans la formater** (après sauvegarde quand même).
- **Une seule ESP** par disque suffit ; en double démarrage, Linux **réutilise** celle de Windows.

## 6.2 Le swap selon le besoin

Le **swap** prend le relais quand la mémoire vive est pleine et reçoit l'image de la mémoire
pour l'**hibernation**. Ubuntu crée par défaut un **fichier d'échange** (`/swap.img`) ; une
**partition swap** reste possible. Repère indicatif (tableau de recommandations de la
documentation Red Hat) :

{_swap_table()}

*Repère du cours, pas une norme ; avec beaucoup de mémoire et sans hibernation, un petit swap
suffit.*

## 6.3 Comment les partitions sont montées : /etc/fstab et UUID

Le fichier **`/etc/fstab`** liste ce qui est monté au démarrage. Chaque partition y est désignée
par son **UUID** (identifiant unique créé au **formatage**), plus fiable qu'un nom comme
`/dev/sdb1`, qui dépend de l'ordre de détection des disques :

{_console(
    "# <file system>                           <mount point> <type> <options>         <dump> <pass>",
    "UUID=8e2f41c0-6d3a-4b9e-91f7-0c5a2d7e3b64 /             ext4   errors=remount-ro 0      1",
    "UUID=4A1C-9F2E                            /boot/efi     vfat   umask=0077        0      1",
    "/swap.img                                 none          swap   sw                0      0",
)}

*Extrait fictif, dans le format de Debian et d'Ubuntu.* `lsblk -f` ou `blkid` affichent les UUID
réels ; reformater une partition **change son UUID**.

**Procédure professionnelle (à rédiger)** : GPT → ESP (FAT32, /boot/efi) → / en ext4 (au moins
25 Go) → /home si l'on veut séparer les données → swap selon mémoire et hibernation →
justification de chaque choix.

**Erreur fréquente** : racine trop petite (10-20 Go) qui se remplit en un an ; formater une /home
existante lors d'une réinstallation ; désigner un disque par `/dev/sdb1` dans fstab.

**À l'écrit** : un **tableau** partition — système de fichiers — point de montage — taille —
raison.

**Repère rapide** : **ESP /boot/efi · / ext4 ≥ 25 Go · /home facultative · swap selon besoin ·
UUID dans fstab**. Exercices liés : {_ex("E05", "E06")}.
"""


def _installer_bootloader() -> str:
    return f"""**Objectifs** : conduire l'installateur et comprendre ce que fait le chargeur de
démarrage.

## 7.1 L'installateur pas à pas

{_fig(SETUP_FIGURE)}

- **Type d'installation** (libellés d'Ubuntu, approximatifs) : **effacer le disque** (disque
  entièrement dédié à Linux, après accord), **à côté de Windows** (double démarrage), ou
  **partitionnement manuel** (on choisit chaque partition et son point de montage).
- **Logiciels tiers** : case qui installe des pilotes **non libres** (Wi-Fi Broadcom, NVIDIA) et
  des formats multimédias ; utile si un matériel ne fonctionnait pas en live.
- **Écran récapitulatif** : on relit les partitions qui seront **formatées** avant de valider.

## 7.2 Le chargeur : GRUB ou systemd-boot

- Le firmware UEFI lance un fichier `.efi` de l'**ESP** ; c'est le **chargeur**, qui charge le
  noyau Linux. Le firmware garde une **liste d'entrées** et un **ordre** (`efibootmgr`).
- **GRUB** : chargeur d'Ubuntu, Debian, Linux Mint et Fedora (dans l'ESP :
  `EFI/ubuntu/shimx64.efi` puis `grubx64.efi`). Il affiche un **menu** qui peut proposer
  Windows en double démarrage.
- **systemd-boot** : chargeur plus simple, uniquement UEFI, utilisé par exemple par Pop!_OS.
- Après une modification de sa configuration (`/etc/default/grub`), GRUB se régénère par
  `sudo update-grub` sous Debian et Ubuntu (commande différente sous Fedora).

{_fig(EFIBOOT_FIGURE)}

**Procédure professionnelle (à rédiger)** : type d'installation justifié → partitions vérifiées
sur l'écran récapitulatif → copie → clé retirée → menu du chargeur contrôlé (chaque système
démarre).

**Erreur fréquente** : valider sans relire quelles partitions seront formatées ; croire Linux
« disparu » alors que l'entrée de Windows est simplement en tête de l'ordre de démarrage.

**À l'écrit** : **type d'installation et raison → partitions → chargeur et ordre de démarrage**.

**Repère rapide** : **effacer / à côté / manuel · relire le récapitulatif · GRUB dans l'ESP ·
efibootmgr pour l'ordre**. Exercices liés : {_ex("E02", "E11")}.
"""


def _accounts() -> str:
    return f"""**Objectifs** : créer des comptes adaptés et réserver l'administration à ceux qui en ont
besoin.

## 8.1 Compte créé à l'installation et sudo

- L'installateur crée un **utilisateur** (nom, mot de passe), le **nom de la machine** et le
  **fuseau horaire** (Europe/Brussels).
- Sous Ubuntu et Linux Mint, ce premier compte est **administrateur** : membre du groupe
  **`sudo`** ; le compte **root** n'a pas de mot de passe utilisable. Sous Debian, si l'on donne un
  mot de passe à root pendant l'installation, l'utilisateur **n'est pas** dans `sudo`. Sous
  Fedora, l'administrateur est membre du groupe **`wheel`**.
- `sudo commande` exécute **une** commande avec les droits d'administration, après le mot de
  passe de l'utilisateur ; l'action reste tracée à son nom.

## 8.2 Comptes des utilisateurs

- **Un compte par personne** ; un **compte standard** pour l'usage quotidien ; `sudo` seulement
  pour la personne qui administre.
- Ajouter un administrateur : `sudo usermod -aG sudo marie` (ou Paramètres → Utilisateurs), puis
  reconnexion ; contrôle : `groups marie`. Les autres commandes de comptes sont vues en PR10.

{_console(
    "$ groups",
    "paul adm cdrom sudo dip plugdev lpadmin",
    "$ sudo -l",
    "User paul may run the following commands on atelier-pc:",
    "    (ALL : ALL) ALL",
)}

*Relevé fictif : `paul` est membre de `sudo` et peut administrer.*

**Procédure professionnelle (à rédiger)** : nom de la machine → compte administrateur (mot de
passe solide, remis au client) → comptes standard des utilisateurs → contrôle `groups`.

**Erreur fréquente** : travailler dans une **session root** ; donner `sudo` à tous les comptes ;
partager un mot de passe.

**À l'écrit** : la **liste des comptes** (nom, type, groupes) et la **raison**.

**Repère rapide** : **un compte par personne · sudo pour l'administrateur · pas de session
root**. Exercices liés : {_ex("E03", "E14")}.
"""


def _network_updates_drivers() -> str:
    return f"""**Objectifs** : obtenir le réseau, mettre le système à jour et installer les pilotes
manquants.

## 9.1 Réseau

- Le réseau est géré par **NetworkManager** (icône du bureau). Contrôles :
  `ip a` (interfaces et adresses ; `NO-CARRIER` = pas de lien sur le câble), `ip route` (route
  par défaut, passerelle), `ping -c 3` vers la passerelle puis vers un **nom** (DNS). Le
  dépannage réseau complet est vu en [PR24](/uaa/ampcr-pratique-pr24).

## 9.2 Mises à jour et logiciels : apt et dnf

{_packages_table()}

- Sous Debian et Ubuntu, `apt update` **rafraîchit la liste** des paquets disponibles et
  `apt upgrade` **installe** les mises à jour : les deux, dans cet ordre. On **redémarre** après
  une mise à jour du noyau.
- On installe les logiciels **depuis les dépôts** de la distribution (ou sa logithèque), jamais un
  paquet `.deb` ou `.rpm` d'un site inconnu.

## 9.3 Pilotes

- La plupart des pilotes sont **dans le noyau Linux** : rien à installer. `lspci -k` affiche,
  sous chaque matériel, la ligne **`Kernel driver in use:`** quand un pilote est chargé.
- Certains matériels demandent un **pilote non libre** : Wi-Fi **Broadcom** (pilote STA, paquet
  `bcmwl-kernel-source` sous Ubuntu), cartes **NVIDIA** (pilote propriétaire). Sous Ubuntu et
  Mint : outil **« Pilotes additionnels »** (ou `ubuntu-drivers devices`) ; avec le démarrage
  sécurisé, enrôlement de la **clé MOK** au redémarrage.
- Sans Wi-Fi, on utilise d'abord un **câble Ethernet** (ou le partage de connexion d'un
  smartphone par USB) pour télécharger le pilote.

{_console(
    "$ lspci -nnk | grep -A2 -i ethernet",
    "02:00.0 Ethernet controller [0200]: Realtek Semiconductor Co., Ltd. RTL8111/8168/8211/8411 PCI Express Gigabit Ethernet Controller [10ec:8168] (rev 15)",
    "\tKernel driver in use: r8169",
    "\tKernel modules: r8169",
)}

*Relevé fictif : `[10ec:8168]` = fabricant Realtek (10ec), modèle 8168 ; pilote `r8169` chargé.*

**Procédure professionnelle (à rédiger)** : réseau (`ip a`, `ping`) → `sudo apt update` puis
`sudo apt upgrade` → pilotes manquants (`lspci -k`, Pilotes additionnels, MOK) → redémarrage et
contrôle.

**Erreur fréquente** : `apt upgrade` sans `apt update` ; pilote téléchargé sur un forum ;
désactiver le démarrage sécurisé au lieu d'enrôler la clé MOK.

**À l'écrit** : **commande exacte → résultat attendu**, dans l'ordre.

**Repère rapide** : **ip a · apt update puis upgrade · Kernel driver in use · Pilotes
additionnels + MOK**. Exercices liés : {_ex("E03", "E13")}.
"""


def _services_tests() -> str:
    return f"""**Objectifs** : vérifier les services et tester le poste avant de le rendre.

## 10.1 Les services

- Un **service** est un programme lancé en arrière-plan (impression **CUPS**, accès à distance
  **SSH**, NetworkManager), géré par **systemd** :
  `systemctl status cups` (état), `sudo systemctl enable --now ssh` (activer au démarrage et
  lancer), `systemctl --failed` (services en échec). L'interprétation des messages est vue en
  [PR11](/uaa/ampcr-pratique-pr11).
- On n'active que les services **demandés** (par exemple SSH seulement si un accès à distance est
  prévu).

{_console(
    "$ systemctl --failed",
    "  UNIT LOAD ACTIVE SUB DESCRIPTION",
    "0 loaded units listed.",
)}

## 10.2 Les tests du poste

Avant de rendre le PC : **plusieurs redémarrages** (et choix de chaque système en double
démarrage), réseau, son, impression d'une page de test, ouverture des documents du client,
espace libre (`df -h`) ; tout est reporté dans la liste de contrôle (chapitre 12).

**Procédure professionnelle (à rédiger)** : `systemctl --failed` → services demandés activés et
contrôlés → tests d'usage avec le client.

**Erreur fréquente** : activer SSH « au cas où » ; rendre le PC sans l'avoir redémarré.

**À l'écrit** : **service → commande → état attendu**.

**Repère rapide** : **systemctl status · enable --now · --failed = 0**. Exercices liés :
{_ex("E03")}.
"""


def _troubleshooting() -> str:
    return f"""**Objectifs** : diagnostiquer une installation qui échoue ou un système qui se comporte
mal, par familles de pannes, sans jamais effacer de données.

## 11.1 Linux ne démarre pas après l'installation

{_fig(BOOT_TREE_FIGURE)}

{_troubles_tables()}

## 11.8 Trois relevés à savoir lire

{_console(
    "$ ls -l ~/Documents/devis.odt",
    "-rw-r--r-- 1 root root 48213 Oct 14 09:12 /home/anne/Documents/devis.odt",
    "         (propriétaire root : anne peut lire, pas modifier)",
    "$ sudo chown anne:anne ~/Documents/devis.odt",
)}

{_fig(DF_FULL_FIGURE)}

{_console(
    "$ sudo apt clean",
    "$ sudo journalctl --vacuum-size=200M",
    "$ sudo apt autoremove",
    "$ df -h /",
)}

*Relevés fictifs. Les permissions (propriétaire, droits `rwx`) sont approfondies en PR10.*

**Procédure professionnelle (à rédiger)** : relever le **message exact** → famille de panne →
**vérification** (commande en lecture seule) → **action** (copie de sauvegarde avant de modifier un
fichier de configuration) → contrôle.

**Erreur fréquente** : réinstaller pour un ordre de démarrage ; supprimer une ligne de fstab sans
comprendre ; `chmod -R 777` ; supprimer des fichiers de `/usr` pour faire de la place ;
désactiver le démarrage sécurisé « pour voir ».

**À l'écrit** : **symptôme → cause → vérification → action → ce qu'on ne fait pas**.

**Repère rapide** : **disque · chargeur · fstab/UUID · réseau · permissions · espace**.
Exercices liés : {_ex("E04", "E11", "E12", "E13", "E14", "E15")}.
"""


def _checklist_report() -> str:
    return f"""**Objectifs** : valider l'installation devant le client et laisser une trace écrite
complète.

## 12.1 Liste de contrôle finale

{_fig(FINAL_FIGURE)}

{_checklist_table()}

## 12.2 Rapport d'intervention

{_report_list()}

Le rapport ne contient **que ce qui a été fait et vérifié** ; on n'y écrit jamais de mot de
passe. Il est signé par le technicien et par le client.

**Procédure professionnelle (à rédiger)** : passer la liste de contrôle **avec le client** →
reporter chaque résultat → rédiger le rapport par rubriques → recommandations.

**Erreur fréquente** : rendre le PC sans vérifier que Windows démarre encore ; rapport réduit à
« Linux installé ».

**À l'écrit** : la **liste** (point — commande — résultat) et le **rapport en rubriques**.

**Repère rapide** : **contrôler devant le client · rubriques · recommandations · signatures**.
Exercices liés : {_ex("E03", "E16")}.
"""


def _examples() -> str:
    return f"""## Cas 1 — Installation complète de Linux seul sur un PC donné

**Situation.** Une association reçoit un PC de 2016 (64 bits, 8 Go de mémoire, SSD de 480 Go,
UEFI) pour son secrétariat (bureautique, courriel). Windows n'y est plus maintenu ; le donateur a
signé l'effacement et récupéré ses données.

**Résolution.**

1. **Demande et accord** : Linux seul, effacement autorisé par écrit ; inventaire (8 Go,
   Ethernet Realtek, Wi-Fi Intel, firmware UEFI, démarrage sécurisé).
2. **Choix** : **Linux Mint** (base Ubuntu LTS, bureau simple, support long).
3. **Image** : ISO du site officiel, `sha256sum -c` → « OK » ; clé de 16 Go écrite avec Etcher.
4. **Démarrage** : entrée « UEFI: », démarrage sécurisé laissé actif ; **session live** : Wi-Fi,
   son et écran fonctionnent, SSD vu par `lsblk`.
5. **Partitions** (manuel, GPT) : ESP 1 Go FAT32 sur `/boot/efi`, `/` ext4 60 Go, `/home` ext4
   le reste ; swap en fichier ({swap_advice(8, hibernation=False):g} Go, sans hibernation).
6. **Compte** : nom de la machine `secretariat-01`, compte administrateur du responsable,
   compte standard de la secrétaire ; fuseau Europe/Brussels.
7. **Finalisation** : `sudo apt update` puis `sudo apt upgrade`, redémarrage ; `lspci -k` :
   pilotes chargés ; imprimante ajoutée et page de test ; `systemctl --failed` : 0.

**Conclusion rédigée.** « Linux Mint installé seul (accord du 12/10), image contrôlée, ESP,
racine et /home en ext4 ; système à jour, pilotes et imprimante fonctionnels, aucun service en
échec ; comptes administrateur et standard créés. »

## Cas 2 — Double démarrage Windows 11 + Ubuntu, avec prudence

**Situation.** Un étudiant garde Windows 11 (BitLocker actif, SSD de 512 Go) et veut Ubuntu pour
ses cours de programmation. Accord écrit signé.

**Résolution.**

1. **Sauvegarde** de ses documents sur disque externe, copie vérifiée ; **clé de récupération
   BitLocker** notée hors du PC.
2. **Sous Windows** : démarrage rapide **désactivé** ; Gestion des disques → **« Réduire le
   volume »** de C: : 100 Go d'espace non alloué.
3. **Clé Ubuntu contrôlée**, démarrée en « UEFI: » (comme Windows) ; session live : `lsblk`
   montre l'ESP de 100 Mo, la MSR, Windows et WinRE.
4. **Partitionnement manuel** : ESP de Windows → `/boot/efi` **sans formatage** ; dans l'espace
   libre, `/` en ext4 ; écran récapitulatif relu (seule la nouvelle partition est formatée).
5. **Contrôle** : menu GRUB proposant Ubuntu et Windows ; **les deux démarrent** ; Windows ne
   demande pas la clé BitLocker (sinon, la saisir).

**Conclusion rédigée.** « Ubuntu ajouté dans 100 Go libérés depuis Windows ; ESP de Windows
réutilisée sans formatage ; Windows et Ubuntu démarrent depuis GRUB ; données sauvegardées et clé
BitLocker conservées par le client. »

## Cas 3 — Après l'installation, le PC démarre toujours sous Windows

**Situation.** Le lendemain d'un double démarrage, le client dit qu'Ubuntu « a disparu » : le PC
démarre directement sous Windows.

{_fig(EFIBOOT_FIGURE)}

**Résolution.**

1. **Lecture** : l'entrée `ubuntu` (0001) existe : l'installation a réussi ; `BootOrder` commence
   par `Windows Boot Manager` (0000).
2. **Correction** : `sudo efibootmgr -o 0001,0000,0002` (ou ordre de démarrage du firmware).
3. **Contrôle** : redémarrage, menu GRUB, Ubuntu puis Windows démarrent.
4. **Ce qu'on ne fait pas** : réinstaller Ubuntu, toucher aux partitions ou à l'ESP.

**Conclusion rédigée.** « Ordre de démarrage UEFI corrigé (entrée ubuntu en premier) ; menu GRUB
rétabli ; les deux systèmes démarrent ; rien n'a été réinstallé. »

## Cas 4 — Mode d'urgence : fstab et UUID après un remplacement de disque

**Situation.** Sur un PC Ubuntu, le disque de données (monté sur `/mnt/donnees`) a été remplacé
et formaté en ext4 ; au démarrage : « You are in emergency mode », puis « Cannot open access to
console, the root account is locked » (Ubuntu : root verrouillé).

{_console(
    "[DEPEND] Dependency failed for /mnt/donnees.",
    "[DEPEND] Dependency failed for Local File Systems.",
    "You are in emergency mode. After logging in, type \"journalctl -xb\" to view system logs, ...",
)}

**Résolution.**

1. **Session live** (root verrouillé) ; racine montée : `sudo mount /dev/nvme0n1p2 /mnt`.
2. **Comparaison** : `lsblk -f` donne le **nouvel UUID** du disque ; `/mnt/etc/fstab` contient
   l'**ancien**.
3. **Copie** de sécurité : `sudo cp /mnt/etc/fstab /mnt/etc/fstab.bak` ; ligne corrigée avec le
   nouvel UUID et l'option **`nofail`** (disque de données non indispensable au démarrage).
4. **Redémarrage** sur le disque ; contrôle : `findmnt --verify` sans erreur, `/mnt/donnees`
   monté, fichiers présents.

**Conclusion rédigée.** « Mode d'urgence causé par l'UUID de l'ancien disque dans /etc/fstab ;
ligne corrigée (nouvel UUID, nofail) après copie du fichier ; démarrage normal, données
accessibles. »

## Cas 5 — Réseau absent : Wi-Fi sans pilote

**Situation.** Après l'installation d'Ubuntu sur un portable, sans réseau et sans les logiciels
tiers, aucun réseau Wi-Fi n'apparaît.

{_console(
    "$ lspci -nnk | grep -A2 -i network",
    "03:00.0 Network controller [0280]: Broadcom Inc. and subsidiaries BCM4360 802.11ac Wireless Network Adapter [14e4:43a0] (rev 03)",
)}

**Résolution.**

1. **Lecture** : carte Broadcom BCM4360 (`14e4:43a0`) ; **aucune** ligne `Kernel driver in use` :
   pas de pilote chargé.
2. **Réseau provisoire** : câble Ethernet (adaptateur USB) ; `ip a` : adresse obtenue.
3. **Pilote** : « Pilotes additionnels » → pilote Broadcom STA (`bcmwl-kernel-source`) ;
   démarrage sécurisé actif : clé MOK enrôlée au redémarrage.
4. **Contrôle** : `lspci -nnk` affiche `Kernel driver in use: wl` ; réseaux visibles ; connexion et
   `ping` réussis.

**Conclusion rédigée.** « Carte Wi-Fi Broadcom sans pilote ; pilote STA des dépôts installé par
câble, clé MOK enrôlée ; Wi-Fi fonctionnel. »
"""


def _pitfalls() -> str:
    return """> **Installer sans accord écrit** ni sauvegarde vérifiée, « parce qu'on ne touche pas à
> Windows ».

> **Écrire une image non contrôlée** ou téléchargée sur un site de partage.

> **Viser le mauvais disque avec `dd`** (`of=/dev/sda`) ou écrire sur une partition (`/dev/sdb1`).

> **Désactiver le démarrage sécurisé** « parce que Linux ne le supporte pas » : les grandes
> distributions le supportent (shim) ; un pilote compilé demande l'enrôlement de la clé MOK.

> **Formater l'ESP de Windows** en double démarrage : Windows ne démarre plus.

> **Choisir « Effacer le disque »** quand le client veut garder Windows.

> **Changer le mode du contrôleur (RAID/Intel RST ↔ AHCI)** sous un Windows à garder, sans le
> préparer.

> **Racine trop petite** (10-20 Go) ; formater /home lors d'une réinstallation.

> **Désigner un disque par `/dev/sdb1`** dans `/etc/fstab`, ou modifier fstab sans copie.

> **Réinstaller** parce que le PC démarre sous Windows : c'est l'ordre des entrées UEFI.

> **`apt upgrade` sans `apt update`** ; pilote ou paquet d'un site inconnu.

> **Travailler en root, `chmod -R 777`**, donner `sudo` à tous les comptes.

> **Supprimer au hasard** des fichiers de `/usr`, `/var/lib` ou `/boot` pour faire de la place.

> **Rendre le PC sans liste de contrôle** ni vérifier que chaque système démarre.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (préparation, installation,
finalisation), classements (symptôme → famille de pannes, points de montage, double démarrage,
avant / pendant / après), terminaux à lire (somme de contrôle, clé USB, partitions, efibootmgr,
fstab, lspci, permissions, espace disque), rapport et procédure à corriger. Rédige ta réponse
sur papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée.
Ces mêmes exercices sont proposés dans [S'entraîner](/uaa/{PR09_SLUG}/practice), avec
correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR09_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (terminaux fictifs, extraits de fichiers).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** La **lecture correcte** des relevés, la **cause** identifiée, la
**commande exacte**, l'**ordre** des opérations et les **précautions** (accord écrit, sauvegarde
vérifiée, ESP non formatée, copie avant de modifier un fichier) — pas la récitation de sigles.
Une autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Avant tout** : demande, **accord écrit**, **inventaire** (mémoire, disques, firmware, mode du
  stockage, puces Wi-Fi et graphique, Windows à garder, BitLocker).
- **Distribution** : selon l'usage et le matériel, version **à support long** ; `apt` (Debian,
  Ubuntu, Mint) ou `dnf` (Fedora).
- **Image** : site officiel ; `sha256sum -c SHA256SUMS --ignore-missing` → **OK** ; FAILED →
  retélécharger.
- **Clé** : ≥ 8 Go ; Etcher, Rufus (GPT/UEFI) ou `dd of=/dev/sdX` sur le **disque entier**,
  cible vérifiée par `lsblk -d` (taille, `usb`).
- **Firmware** : UEFI ; **démarrage sécurisé actif** (shim) ; mode du stockage noté ; entrée
  **« UEFI: »**.
- **Session live** : tester Wi-Fi, écran, son, disques **avant** d'installer.
- **Double démarrage** : sauvegarde, clé BitLocker, démarrage rapide off, **C: réduite depuis
  Windows**, **ESP réutilisée sans formatage**, jamais « Effacer le disque ».
- **Partitions** (GPT) : **ESP** FAT32 `/boot/efi` · **/** ext4 ≥ 25 Go · **/home**
  facultative · **swap** selon mémoire et hibernation.
- **fstab** : partitions désignées par **UUID** ; reformater change l'UUID ; copie avant
  modification ; `findmnt --verify`, `mount -a` ; `nofail` pour un disque de données.
- **Chargeur** : GRUB (Ubuntu, Debian, Mint, Fedora) ou systemd-boot (Pop!_OS) dans l'ESP ;
  ordre des entrées : `efibootmgr`, `efibootmgr -o`.
- **Comptes** : premier compte dans **sudo** (wheel sous Fedora) ; compte standard au quotidien ;
  `usermod -aG sudo` seulement pour un administrateur.
- **Après** : `sudo apt update` puis `sudo apt upgrade` ; `lspci -k` (Kernel driver in use) ;
  Pilotes additionnels + MOK ; `ip a`, `ping` ; `systemctl --failed`.
- **Pannes** : disque non vu (RST/AHCI) · chargeur (ordre, grub rescue) · fstab/UUID (mode
  d'urgence) · réseau (pilote, NO-CARRIER) · permissions (`chown`, jamais 777) · espace
  (`df -h`, `apt clean`, `journalctl --vacuum-size`).
- **Contrôle** : liste de contrôle avec le client ; **rapport** en rubriques, signé.

## Glossaire des termes employés

- **Distribution** : système Linux complet (noyau, programmes, installateur, paquets, bureau).
- **ESP (partition système EFI)** : partition FAT32 où le firmware UEFI lit le chargeur.
- **ext4** : système de fichiers journalisé proposé par Debian, Ubuntu et Mint.
- **fstab** : fichier `/etc/fstab`, liste des systèmes de fichiers montés au démarrage.
- **GRUB / systemd-boot** : chargeurs de démarrage qui lancent le noyau Linux.
- **LTS** : version à support long, maintenue plusieurs années.
- **MOK** : clé locale enrôlée dans le firmware pour autoriser un pilote compilé sur le PC avec
  le démarrage sécurisé.
- **Point de montage** : dossier de l'arborescence où une partition est accessible (/, /home).
- **Session live** : système lancé depuis la clé, sans rien écrire sur le disque.
- **shim** : petit chargeur signé qui permet de démarrer Linux avec le démarrage sécurisé.
- **Somme de contrôle (SHA-256)** : empreinte d'un fichier ; identique à celle publiée → fichier
  intact.
- **sudo** : exécution d'une commande avec les droits d'administration, au nom de l'utilisateur.
- **Swap** : espace d'échange sur disque (partition ou fichier), utilisé aussi pour l'hibernation.
- **UUID** : identifiant unique d'un système de fichiers, créé au formatage.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigence AP-10
  « Installation complète des différents systèmes d'exploitation courants ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Distributions** : documentation d'Ubuntu (installation de la version Desktop, configuration
  recommandée, vérification de l'image ISO, Secure Boot et MOK, `ubuntu-drivers`), de Debian
  (manuel d'installation, `apt`), de Fedora (guide d'installation, `dnf`), de Linux Mint (guide
  d'installation) et de Pop!_OS (systemd-boot).
- **Outils** : pages de manuel de `sha256sum`, `lsblk`, `blkid`, `dd`, `efibootmgr`, `mokutil`,
  `fstab(5)`, `findmnt`, `mount`, `ip`, `lspci`, `systemctl`, `journalctl`, `usermod`, `chown`,
  `df`, `du` ; documentation de balenaEtcher et de Rufus.
- **Swap** : tableau de recommandations de taille de la documentation Red Hat Enterprise Linux,
  repris comme repère indicatif.
- **Windows (double démarrage)** : documentation Microsoft (réduire un volume, démarrage rapide,
  clé de récupération BitLocker).

Les installateurs cités sont ceux d'Ubuntu, de Linux Mint, de Debian et de Fedora en
{WRITTEN_AT} ; leurs libellés changent avec les versions : la documentation de la distribution
fait foi le jour de l'intervention. Les procédures, plans de partitions, repères de swap, règles
du double démarrage, le tableau de dépannage, l'arbre de décision et la liste de contrôle du
cours sont **produits par programme** depuis des données **vérifiées par des tests
automatiques** ; aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 cite l'installation complète des systèmes courants (AP-10). Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- la protection des données et l'accord écrit (AP-C03, complément du parcours, repris de PR04) ;
- le double démarrage avec Windows ;
- le dépannage de l'installation par familles de pannes ;
- le tableau « usage → distribution », le repère de taille du swap, la liste de contrôle et le
  plan du rapport d'intervention : ce sont des **conventions du cours**, pas une norme.

## Supports fictifs

Les terminaux, relevés et situations de ce cours sont **fictifs** et reconstitués pour
l'entraînement, parfois abrégés ; ils ne décrivent aucun client réel. Aucun n'est une question
officielle ou déjà posée par le Jury.
"""


def pr09_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR09 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR09 — 1. Préparer l'intervention : demande, accord écrit et inventaire", _prepare()),
        ("PR09 — 2. Choisir la distribution selon l'usage", _distribution()),
        ("PR09 — 3. Image ISO, contrôle d'intégrité et clé USB de démarrage", _iso_media()),
        ("PR09 — 4. Firmware UEFI, démarrage sécurisé et session live", _firmware_live()),
        ("PR09 — 5. Sauvegarde et double démarrage avec prudence", _backup_dual_boot()),
        ("PR09 — 6. Partitions : ESP, racine, /home, swap et ext4", _partitions()),
        ("PR09 — 7. L'installateur et le chargeur GRUB ou systemd-boot", _installer_bootloader()),
        ("PR09 — 8. Comptes, sudo et nom de la machine", _accounts()),
        ("PR09 — 9. Réseau, mises à jour apt/dnf et pilotes", _network_updates_drivers()),
        ("PR09 — 10. Services et tests du poste", _services_tests()),
        ("PR09 — 11. Dépannage : six familles de pannes", _troubleshooting()),
        ("PR09 — 12. Liste de contrôle finale et rapport d'intervention", _checklist_report()),
        ("PR09 — Exemples : cinq cas résolus", _examples()),
        ("PR09 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR09 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR09 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR09 — Fiche mémo et glossaire", _memo()),
        ("PR09 — Sources et compléments pédagogiques", _sources()),
    ]
