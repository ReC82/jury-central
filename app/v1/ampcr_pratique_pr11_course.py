"""Cours PR11 « Messages d'erreur Windows/Linux — diagnostic et interventions écrites » —
parcours AMPCR pratique écrite (ticket #194).

Matière : intégralement celle du ticket #194 (1. méthode universelle, 2. démarrage et
partitions, 3. Windows, 4. Linux, 5. réseau, périphériques et corrélation, 6. compte rendu),
découpée en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de
bloc théorique ne contient « examen », « source », « exemple » ni « exercice »). Schémas et
captures fictives : `app.v1.ampcr_pratique_pr11_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr11_bank` (même source que la banque des sessions). Mise en forme
partagée avec PR06 (`app.v1.ampcr_pratique_pr06_course`).
"""

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr11_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr11_figures import (
    BCD_SCREEN_FIGURE,
    BSOD_SCREEN_FIGURE,
    DEVICE_SCREEN_FIGURE,
    DISK_FULL_SCREEN_FIGURE,
    ERROR_FLOW_FIGURE,
    EVENT_SCREEN_FIGURE,
    LSBLK_SCREEN_FIGURE,
    PARTITION_FIGURE,
    STAGE_TREE_FIGURE,
    SYSTEMCTL_SCREEN_FIGURE,
    WINRE_SCREEN_FIGURE,
)

PR11_TITLE = "Messages d'erreur Windows/Linux — diagnostic et interventions écrites"
PR11_SLUG = "ampcr-pratique-pr11"
# Anciens titres de blocs déjà seedés (contenu remplacé : le bloc est recréé sous son nouveau
# titre au prochain seed, voir `app.seed._seed_uaa`).
PR11_OBSOLETE_TITLES = frozenset({"PR11 — 1. Méthode universelle face à un message d'erreur"})


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr11") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Face à une capture d'écran, un extrait de journal ou un tableau d'observations, tu dois
**rédiger** ce que tu fais. À la fin de ce cours, tu sais :

1. **lire** un message d'erreur ou un journal et en relever les éléments utiles (texte exact,
   code, source, heure, contexte) ;
2. **situer le stade** où l'erreur survient (firmware, chargeur, système, session, service,
   application, pilote, périphérique, stockage, réseau) ;
3. **distinguer** le symptôme, la cause probable, l'hypothèse et le test qui la confirme ;
4. **choisir des vérifications non destructives** sous Windows et sous Linux, et dire ce
   qu'elles prouvent ;
5. **décrire une réparation adaptée**, réversible d'abord, avec sauvegarde et autorisation
   avant toute action risquée ;
6. **confirmer le résultat** et **rédiger un compte rendu** professionnel.

## Exigences officielles travaillées dans ce cours

{_req("AP-09")}
{_req("AP-13")}
{_req("AP-15")}

Les deux premières puces sont proches mais figurent toutes les deux au PDF : ce cours traite
les **principaux messages**, leur **interprétation** et la **démarche d'intervention**
(sections 1 à 6). AP-15 est travaillée pour sa partie logicielle (le matériel est en PR06).

Compléments pédagogiques (hors liste officielle des pp. 5-6, signalés comme tels) :

{_req("AP-C01")}
{_req("AP-C03")}

## Prérequis : la théorie déjà publiée

Relis au besoin les mini-cours du parcours « Théorie » (séparé de ce parcours) :
[MC07 BIOS, UEFI, POST et démarrage](/uaa/ampcr-mc07),
[MC08 Partitionnement, GPT/MBR et formatage](/uaa/ampcr-mc08),
[MC10 Windows : administration et commandes](/uaa/ampcr-mc10),
[MC11 Linux : bases utiles](/uaa/ampcr-mc11),
[MC12 Pilotes et périphériques](/uaa/ampcr-mc12),
[MC29 Dépannage matériel](/uaa/ampcr-mc29), [MC30 Dépannage Windows et Linux](/uaa/ampcr-mc30),
[MC31 Dépannage réseau](/uaa/ampcr-mc31), [MC36 Rapport technique](/uaa/ampcr-mc36).
Le diagnostic du **matériel** (PC inerte, POST, bips) est traité dans
[PR06](/uaa/ampcr-pratique-pr06).

## Comment travailler ce cours

Lis la méthode (1), puis les erreurs de démarrage (2), Windows (3), Linux (4) et les cas
croisés (5) ; termine par le compte rendu (6). Étudie les **cinq cas résolus**, fais les
**{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner », correction après
envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les situations, captures, journaux et noms de ce cours sont des **supports
> fictifs** construits pour s'entraîner. Les messages et codes reproduits sont ceux des
> systèmes réels, mais aucun de ces exercices n'est une question officielle ni une question
> déjà posée par le Jury.
"""


def _method() -> str:
    return f"""## 1.1 Recueillir avant d'interpréter

Un message d'erreur ne s'interprète **jamais seul**. Avant de chercher une cause, note :

| À recueillir | Pourquoi |
|---|---|
| **Texte exact** du message (recopié ou photographié, pas résumé) | Un mot change tout : « not found » n'est pas « access denied ». |
| **Code** (STOP code, code d'erreur, code du Gestionnaire de périphériques, ID d'événement, code de sortie) | Il permet une recherche fiable dans la documentation. |
| **Contexte** : ce que faisait l'utilisateur, à quel moment (démarrage, ouverture de session, lancement d'une application) | Situe le stade de l'erreur. |
| **Date et heure** | Permet de retrouver l'événement dans les journaux. |
| **Événement déclencheur** et **modifications récentes** (mise à jour, pilote, matériel, réglage du firmware, mot de passe, nettoyage de partitions) | La cause est souvent là, mais une coïncidence n'est pas une preuve. |
| **Périmètre** : un poste, un utilisateur, plusieurs postes, tout le monde | Un problème commun à tous les postes pointe vers ce qu'ils partagent (réseau, serveur, mise à jour). |
| **Criticité** : poste bloqué, dégradé, gênant | Fixe la priorité. |
| **Données à préserver** : où sont-elles, sont-elles sauvegardées ? | Conditionne tout ce qui suit. |

## 1.2 À quel stade l'erreur survient-elle ?

Classer le stade réduit énormément les causes possibles. Dans l'ordre du démarrage puis de
l'utilisation : **firmware / POST**, **chargeur d'amorçage** (bootloader), **noyau / système**,
**ouverture de session**, **service**, **application**, **pilote**, **périphérique**,
**stockage**, **réseau**.

{_fig(STAGE_TREE_FIGURE, wide=True)}

## 1.3 Code, cause, hypothèse, test, résultat, action

| Notion | Exemple |
|---|---|
| **Code d'erreur** (ce que le système affiche) | `0x80070070` dans Windows Update |
| **Cause probable** (ce que dit la documentation) | Espace disque insuffisant |
| **Hypothèse** (cause possible dans ce cas précis) | « Le disque C: de ce PC est plein. » |
| **Test de confirmation** | Paramètres > Système > Stockage : espace libre de C: |
| **Résultat attendu** | Espace libre presque nul → hypothèse confirmée |
| **Action corrective** | Libérer de l'espace (fichiers temporaires, données déplacées avec accord), relancer la mise à jour |

**Chercher dans une documentation fiable.** La signification d'un code se vérifie dans la
documentation de l'éditeur (Microsoft Learn, manuel de la distribution, `man`, site du
fabricant), pas sur un forum isolé. Beaucoup de codes sont **ambigus** : un même STOP code
peut venir d'un pilote, de la mémoire ou du disque. **Ne jamais inventer une cause unique à
partir d'un code** : on en déduit des hypothèses, que l'on teste.

## 1.4 L'ordre des actions

1. **Sauvegarde et protection des données** (copie, image, au minimum vérifier qu'une
   sauvegarde existe).
2. **Collecte des preuves** : captures, journaux, codes, **avant** qu'un redémarrage ou une
   réparation ne les efface.
3. **Tests simples** et non destructifs (lecture d'état, commandes de diagnostic).
4. **Réparation réversible** : restaurer un pilote, un réglage, un point de restauration,
   désinstaller une mise à jour.
5. **Opérations invasives** (réparation du système de fichiers, réécriture du démarrage,
   réinstallation) **seulement avec autorisation** et données à l'abri.
6. **Validation** : reproduire le scénario, vérifier que l'erreur a disparu, noter.

{_fig(ERROR_FLOW_FIGURE)}

> **Erreur fréquente —** proposer « réinstaller Windows » ou « formater » comme première
> action. C'est l'action la plus lourde, elle détruit les preuves et parfois les données, et
> elle ne dit rien de la cause.
"""


def _boot_windows() -> str:
    return rf"""## 2.1 « Aucun périphérique de démarrage » : quatre messages, une même question

| Message (selon le fabricant du firmware) | Ce qu'il dit |
|---|---|
| « No bootable device » | Le firmware n'a trouvé aucun support de démarrage utilisable. |
| « Operating system not found » | Idem : aucun système démarrable sur les supports essayés. |
| « Boot device not found » | Idem, formulation de certains portables. |
| « Reboot and Select proper Boot device or Insert Boot Media in selected Boot device » | Idem, formulation fréquente des firmwares de PC de bureau. |

Ces messages viennent du **firmware**, avant tout chargeur. Ils ne disent **pas** si la cause
est matérielle ou de configuration. Vérifications, dans l'ordre :

1. **Le disque est-il détecté par le firmware ?** S'il n'apparaît pas : piste **matérielle**
   (câble, alimentation, emplacement M.2, disque en panne ; voir [PR06](/uaa/ampcr-pratique-pr06)).
2. **Mode de démarrage** : **UEFI** (disque **GPT** avec une partition EFI) ou **hérité**
   (Legacy/CSM, disque **MBR**). Un disque MBR ne démarre pas en UEFI seul, et inversement.
   Une mise à jour ou une remise à zéro du firmware change souvent ce réglage.
3. **Ordre de démarrage** : la bonne entrée (« Windows Boot Manager », « ubuntu ») est-elle en
   tête ? Une clé USB ou un nouveau disque est-il passé devant ?
4. **Câblage** et ports (après un nettoyage, un ajout de disque).
5. **Partitions** : la partition EFI (ESP) existe-t-elle ? A-t-elle été supprimée ?
6. **Chargeur** (Windows Boot Manager, BCD, GRUB) : seulement si tout ce qui précède est bon.

Les étapes 1 à 4 sont des **réglages et contrôles réversibles** ; les étapes 5-6 touchent au
disque : sauvegarde et prudence.

## 2.2 Windows Boot Manager, BCD et WinRE

- **Windows Boot Manager** est le chargeur de Windows. En UEFI, c'est un fichier de la
  partition EFI (`\EFI\Microsoft\Boot\bootmgfw.efi`). Il lit le **BCD** (*Boot Configuration
  Data*, magasin de configuration du démarrage) pour savoir quel Windows lancer.
- Si le BCD est absent ou abîmé, Windows Boot Manager affiche un écran de **récupération**
  avec un code, par exemple `0xc000000f` (cas 1 ci-dessous).

{_fig(BCD_SCREEN_FIGURE)}

- **WinRE** (environnement de récupération Windows) s'ouvre après plusieurs échecs de
  démarrage, depuis une clé d'installation (« Réparer l'ordinateur ») ou par Maj + Redémarrer.

{_fig(WINRE_SCREEN_FIGURE)}

| Outil de WinRE | Rôle | Limite |
|---|---|---|
| **Réparation du démarrage** (« Outil de redémarrage système ») | Diagnostique et répare automatiquement les fichiers de démarrage | Ne répare pas un disque défaillant ni un fichier personnel |
| **Restauration du système** | Revient à un point de restauration (pilotes, registre, programmes) | Ne touche pas aux documents ; inutile s'il n'existe aucun point |
| **Désinstaller des mises à jour** | Retire la dernière mise à jour de qualité ou de fonctionnalité | Seulement si l'erreur suit une mise à jour |
| **Paramètres** (de démarrage) | Mode sans échec, désactiver le redémarrage automatique après échec | Diagnostic, pas une réparation |
| **Invite de commandes** | Lecture (`bcdedit /enum`, `dir`) et réparations manuelles | Les commandes de réparation **modifient** le démarrage |

**Prudence avant toute commande qui modifie le démarrage** (`bootrec /rebuildbcd`,
`bcdboot C:\Windows`, `diskpart`) : identifier d'abord les volumes (lettres différentes dans
WinRE), sauvegarder les données si possible, essayer la réparation automatique avant. Dans
`diskpart`, une commande comme `clean` **efface la table de partitions** du disque sélectionné :
ne jamais l'utiliser pour « réparer » un démarrage.
"""


def _boot_linux() -> str:
    return f"""## 2.3 Linux : GRUB, initramfs, racine et /etc/fstab

| Message | Stade | Ce qu'il indique | Vérifications prudentes |
|---|---|---|---|
| `error: no such partition.` puis `grub rescue>` | Chargeur (GRUB) | GRUB démarre mais ne trouve plus la partition de ses fichiers | Partition supprimée ou déplacée ? Démarrer sur une clé live, `lsblk` en lecture seule, sauvegarde ; réinstaller GRUB seulement ensuite |
| `error: unknown filesystem.` | Chargeur | GRUB ne reconnaît pas le système de fichiers attendu (partition écrasée, reformatée) | Idem, pas de formatage |
| `Gave up waiting for root file system device` … `ALERT! UUID=… does not exist. Dropping to a shell!` puis `(initramfs)` | Noyau / démarrage précoce | Le noyau ne trouve pas la partition racine indiquée (UUID modifié, disque absent, pilote de stockage manquant) | `blkid` ou `lsblk -f` dans le shell pour comparer les UUID ; mode du contrôleur dans le firmware ; dernier noyau installé |
| `[DEPEND] Dependency failed for Local File Systems.` puis `You are in emergency mode.` | Système (systemd) | Un montage de `/etc/fstab` a échoué (disque absent, UUID faux, option erronée) | `journalctl -xb`, comparer `/etc/fstab` à `lsblk -f`, tester par `mount -a` |
| `No space left on device` au démarrage d'un service, connexion graphique qui échoue | Système / stockage | Partition pleine (ou plus d'inodes) | `df -h`, `df -i` |

- **/etc/fstab** liste les systèmes de fichiers à monter au démarrage. Chaque ligne désigne
  le volume (de préférence par son **UUID**, identifiant unique du système de fichiers, que
  donnent `blkid` ou `lsblk -f`), le point de montage, le type, les options.
- Un UUID **change** quand on reformate ou remplace un disque, même si l'on recopie les
  fichiers : la ligne fstab doit être mise à jour.
- L'option `nofail` évite le mode d'urgence pour un disque **non indispensable** au démarrage.
- Avant de modifier fstab : **copie de sauvegarde** du fichier, puis test par `mount -a` (ou
  `findmnt --verify`) **avant** de redémarrer.

{_fig(LSBLK_SCREEN_FIGURE)}

## 2.4 MBR, GPT et partition EFI

| | MBR (ancien) | GPT (actuel) |
|---|---|---|
| Démarrage associé | Hérité (BIOS, CSM) | UEFI |
| Partitions | 4 principales (ou 3 + une étendue) | 128 par défaut sous Windows |
| Taille maximale du disque | 2 Tio (secteurs de 512 octets) | Bien au-delà |
| Où est le chargeur | Code d'amorçage du MBR + partition active | Fichier `.efi` dans la **partition EFI (ESP)**, en FAT32 |

{_fig(PARTITION_FIGURE, wide=True)}

**Règles à écrire dans une réponse d'examen :**

- Windows démarre en **UEFI sur un disque GPT** ou en **mode hérité sur un disque MBR** ;
  Windows 11 exige l'UEFI.
- La **partition EFI** contient les chargeurs de tous les systèmes du disque : la supprimer ou
  la formater empêche tout démarrage, même si C: ou / sont intacts.
- Une partition « sans lettre » dans la Gestion des disques n'est pas inutile : ce peut être
  l'ESP, la partition de récupération ou une partition Linux.
- La conversion MBR → GPT (outil `mbr2gpt` de Windows, après `mbr2gpt /validate`) modifie la
  table de partitions : sauvegarde préalable.
- **Jamais de formatage ni de réinstallation comme premier réflexe** : on vérifie d'abord la
  détection, le mode, l'ordre, les partitions.
"""


def _windows_symptoms() -> str:
    return r"""## 3.1 Écran bleu (BSOD) et STOP code

Un **écran bleu** (*Blue Screen of Death*) signale un arrêt du noyau Windows : il redémarre pour
protéger le système. À relever :

- le **code d'arrêt** (*STOP code*), en texte (`DRIVER_IRQL_NOT_LESS_OR_EQUAL`) et parfois en
  hexadécimal (`0x000000D1`) ;
- la ligne **« Ce qui a échoué »** quand elle est présente (un fichier `.sys`, c'est-à-dire un
  pilote) ;
- le **contexte** : au démarrage, en jeu, à la mise en veille, après un ajout de matériel ou
  une mise à jour.

{BSOD}

**Redémarrage automatique.** Par défaut, Windows redémarre aussitôt : l'écran disparaît avant
d'être lu. On peut désactiver « Redémarrer automatiquement » (Paramètres système avancés >
Démarrage et récupération, ou WinRE > Paramètres). Après coup, le code se retrouve dans le
journal **Système**, événement **BugCheck, ID 1001**, et un fichier de vidage est écrit (par
exemple dans `C:\Windows\Minidump`), lisible avec l'outil WinDbg de Microsoft.

| Code d'arrêt (exemples) | Pistes à **tester** (jamais une conclusion) |
|---|---|
| `DRIVER_IRQL_NOT_LESS_OR_EQUAL` (0xD1), `IRQL_NOT_LESS_OR_EQUAL` (0xA) | Pilote récent ou défectueux (fichier cité), mémoire |
| `MEMORY_MANAGEMENT` (0x1A), `PAGE_FAULT_IN_NONPAGED_AREA` (0x50) | Mémoire (test, une barrette à la fois), pilote, disque |
| `INACCESSIBLE_BOOT_DEVICE` (0x7B) | Le noyau ne lit plus le disque système : mode du contrôleur changé (AHCI/RAID), pilote de stockage, disque |
| `VIDEO_TDR_FAILURE` (0x116) | Pilote graphique, température ou stabilité de la carte graphique |
| `CRITICAL_PROCESS_DIED` (0xEF) | Processus système arrêté : fichiers système, disque, mise à jour |
| `WHEA_UNCORRECTABLE_ERROR` (0x124) | Erreur matérielle signalée par le processeur : température, alimentation, surcadençage |

Les hypothèses classiques — **pilote, RAM, disque, mise à jour, température** — se testent :
mode sans échec (le problème disparaît-il sans les pilotes tiers ?), restaurer le pilote
récent, test mémoire, état du disque, relevé de températures, désinstaller la mise à jour.

## 3.2 Gestionnaire de périphériques (`devmgmt.msc`)

| Ce que l'on voit | Signification | Première action |
|---|---|---|
| **Périphérique inconnu**, rubrique « Autres périphériques » | Aucun pilote ne correspond | Pilote du fabricant (identifiant matériel dans Propriétés > Détails) |
| **Triangle jaune avec point d'exclamation** | Le périphérique a un problème ; le code est dans Propriétés > Général > État | Lire le code |
| **Flèche vers le bas** | Périphérique désactivé | Le réactiver s'il n'a pas été désactivé volontairement |
| **Code 28** — « Les pilotes de ce périphérique ne sont pas installés. » | Pilote absent | Installer le pilote |
| **Code 22** — « Ce périphérique est désactivé. » | Désactivé | Activer |
| **Code 10** — « Ce périphérique ne peut pas démarrer. » | Le pilote n'arrive pas à démarrer le périphérique (pilote inadapté, incompatible) | Restaurer ou mettre à jour le pilote (fabricant) |
| **Code 43** — « Windows a arrêté ce périphérique car il a signalé des problèmes. » | Le périphérique ou son pilote a signalé une défaillance | Autre port, autre câble, autre PC, pilote : matériel **ou** logiciel |

Le **numéro du code** est l'élément fiable ; le texte varie un peu selon la version de Windows.
L'onglet **Pilote** permet de **mettre à jour**, **restaurer le pilote** précédent (réversible),
**désactiver** ou **désinstaller** le périphérique.

{DEVICES}

## 3.3 Observateur d'événements (`eventvwr.msc`)

Journaux à connaître : **Journaux Windows > Système** (noyau, pilotes, services, disques) et
**Application** (programmes), plus **Sécurité** (ouvertures de session) et **Installation**.
Chaque événement porte un **niveau** (Critique, Erreur, Avertissement, Information), une
**date et heure**, une **source** et un **ID**.

| Source et ID (exemples réels) | Ce qu'il dit |
|---|---|
| Kernel-Power **41** | Le système a redémarré **sans arrêt correct** : conséquence (coupure, plantage), pas cause |
| EventLog **6008** | L'arrêt précédent était inattendu |
| BugCheck **1001** | Un écran bleu a eu lieu, avec son code d'arrêt et le fichier de vidage |
| disk **7** | Un disque signale un **bloc défectueux** |
| disk **153** | Une opération de lecture/écriture a dû être **réessayée** |
| Service Control Manager **7000**, **7009**, **7031**, **7038** | Service qui n'a pas démarré, délai dépassé, arrêt inattendu, échec d'ouverture de session du compte du service |
| WindowsUpdateClient **20** | Échec d'installation d'une mise à jour, avec son code |
| User Profile Service **1511** | Profil local introuvable : connexion avec un **profil temporaire** |

{EVENTS}

**Un événement corrélé n'est pas une preuve de causalité.** Deux événements proches dans le
temps peuvent être sans lien ; on cherche ce qui **se répète** à chaque panne, puis on le
**teste** (cas 2, exercice E15).
""".replace("{BSOD}", _fig(BSOD_SCREEN_FIGURE)).replace(
        "{DEVICES}", _fig(DEVICE_SCREEN_FIGURE)
    ).replace("{EVENTS}", _fig(EVENT_SCREEN_FIGURE))


def _windows_tools() -> str:
    return r"""## 3.4 Gestion des disques (`diskmgmt.msc`)

| État affiché | Signification | À faire — à ne pas faire |
|---|---|---|
| Disque **hors ligne** (*Offline*) | Windows n'utilise pas ce disque (politique, conflit de signature) | Le mettre **en ligne** (clic droit) ; ne rien initialiser |
| Disque **non initialisé** (« Inconnu ») | Windows ne lit aucune table de partitions | **Ne pas initialiser** un disque qui contenait des données : l'initialisation écrit une nouvelle table. Vérifier câble, autre PC, outil de récupération |
| Volume **sans lettre** | Le volume existe mais n'est pas accessible dans l'Explorateur | Attribuer une lettre (Modifier la lettre de lecteur) **si** c'est un volume de données ; ne pas toucher à l'ESP ni à la récupération |
| Volume **RAW**, message « Vous devez formater le disque… » | Système de fichiers illisible | **Refuser le formatage** ; données d'abord (récupération), puis réparation |
| Espace **non alloué** | Aucune partition | Ne créer une partition qu'après avoir vérifié qu'aucune donnée n'y était |
| Volume **plein** | Plus d'espace | Libérer (fichiers temporaires, déplacement de données avec accord) |

## 3.5 Services (`services.msc`)

Chaque service a un **statut** (En cours d'exécution, Arrêté), un **type de démarrage**
(Automatique, Automatique — début différé, Manuel, Désactivé), un **compte d'ouverture de
session** (onglet Connexion) et des **dépendances** (onglet Dépendances : un service ne démarre
pas si celui dont il dépend est arrêté). Un service qui ne démarre pas se diagnostique avec son
**message**, ses **dépendances** et le journal **Système** (Service Control Manager).
Exemple : le service **Spouleur d'impression** arrêté → aucune impression possible.

## 3.6 Commandes : diagnostic ou modification ?

| Commande | Rôle | Diagnostic / modification |
|---|---|---|
| `ipconfig /all` | Adresse IP, masque, passerelle, DNS, DHCP, adresse MAC de chaque carte | Diagnostic |
| `ipconfig /release`, `/renew`, `/flushdns` | Libérer / redemander une adresse DHCP ; vider le cache DNS | Modification (sans risque pour les données) |
| `ping <adresse ou nom>` | Joignabilité d'une machine | Diagnostic |
| `nslookup <nom>` | Résolution d'un nom par le serveur DNS | Diagnostic |
| `tracert <nom>` | Chemin des routeurs jusqu'à la destination | Diagnostic |
| `sfc /scannow` (administrateur) | Vérifie les fichiers système protégés et **remplace** ceux qui sont endommagés | Modification (fichiers système) |
| `DISM /Online /Cleanup-Image /RestoreHealth` (administrateur) | Répare le magasin de composants de Windows (référence utilisée par SFC), à lancer **avant** SFC si SFC échoue ; `/CheckHealth` et `/ScanHealth` ne font que vérifier | Modification (`/RestoreHealth`) |
| `chkdsk C:` | Vérifie le système de fichiers **en lecture seule** et fait un rapport | Diagnostic |
| `chkdsk C: /f` | **Corrige** les erreurs du système de fichiers ; le volume doit être verrouillé (proposé au prochain redémarrage pour C:) | Modification |
| `chkdsk C: /r` | Comme /f, **plus** recherche des secteurs défectueux et récupération des données lisibles ; très long, sollicite fortement le disque | Modification |
| Gestionnaire des tâches (Ctrl + Maj + Échap) | Processus, charge du processeur, de la mémoire, du disque ; programmes au démarrage | Diagnostic (fin de tâche = modification) |
| `msconfig` | Démarrage sélectif, mode sans échec au prochain démarrage | Modification (à annuler ensuite) |

> **Précaution chkdsk —** sur un disque qui fait du bruit ou signale des blocs défectueux,
> **sauvegarder d'abord** : `/f` et surtout `/r` sollicitent le disque et modifient le système
> de fichiers. Un disque mécaniquement défaillant passe par la récupération de données, pas par
> chkdsk.

## 3.7 Mises à jour, profils, droits, applications : pas de solution magique

- **Échec de Windows Update** : relever le code (Paramètres > Windows Update > Historique,
  journal WindowsUpdateClient), vérifier l'**espace disque** (`0x80070070` = espace
  insuffisant), la **connexion**, l'heure du PC ; utiliser l'utilitaire de résolution des
  problèmes ; ne pas désactiver les mises à jour « pour régler le problème ».
- **Profil utilisateur** : « Vous êtes connecté avec un profil temporaire » (User Profile
  Service 1511) — ne rien enregistrer dans cette session, vérifier le dossier
  `C:\Users\<nom>`, l'espace et l'état du disque ; sauvegarder avant toute réparation du
  profil.
- **Droits et permissions** : « Accès refusé » — l'utilisateur a-t-il les droits sur ce
  fichier ou ce dossier (onglet Sécurité) ? Un compte standard ne peut pas installer de
  programme pour tous : on demande l'élévation, on ne rend pas l'utilisateur administrateur.
- **Application** : message exact, journal **Application** (Application Error, ID 1000 :
  programme et module en cause), version, mise à jour récente, droits, espace ; un seul
  utilisateur ou tous ?

Toujours : **périmètre** (qui, quoi, depuis quand), **journaux**, **stockage**, **connexion**,
**permissions**. « Nettoyer le registre », « optimiseur miracle » ou « réinstaller par
précaution » ne sont pas des diagnostics.
"""


def _linux_systemd() -> str:
    return f"""## 4.1 Messages Linux fréquents

| Message | Stade | Lecture |
|---|---|---|
| `grub rescue>`, `error: no such partition.` | Chargeur | Voir 2.3 |
| `You are in emergency mode.` | Système | Un élément indispensable au démarrage a échoué (souvent un montage de fstab) : `journalctl -xb` |
| `[FAILED] Failed to start ….service` | Service | Le service n'a pas démarré : `systemctl status`, `journalctl -u` |
| `[DEPEND] Dependency failed for …` | Service / montage | Une unité n'a pas démarré **parce qu'une autre** a échoué : chercher la première erreur |
| `Active: inactive (dead)` | Service | Service arrêté (pas forcément en erreur) ; `enabled`/`disabled` dit s'il démarre au boot |
| `Permission denied` | Droits | Voir 4.4 |
| `Read-only file system` | Stockage | Le système de fichiers est monté en lecture seule, souvent **remonté** ainsi par le noyau après une erreur (dmesg) |
| `No space left on device` | Stockage | Plus d'espace **ou** plus d'inodes : `df -h` **et** `df -i` |
| `bash: ifconfig: command not found` | Commande | Commande non installée (paquet absent), faute de frappe, ou dossier absent du `PATH` |
| `mount: … wrong fs type, bad option, bad superblock` | Montage | Type ou option erronés, ou système de fichiers abîmé : ne pas formater |
| `Network is unreachable`, `Temporary failure in name resolution` | Réseau | Pas de route (passerelle) ; DNS qui ne répond pas |

## 4.2 systemd et journald : lire avant d'agir

| Commande | Rôle | Lecture / action |
|---|---|---|
| `systemctl status <service>` | État, activation au démarrage, dernières lignes du journal | Lecture |
| `systemctl --failed` | Liste des unités en échec | Lecture |
| `journalctl -b` | Journal du démarrage en cours (`-b -1` : précédent, si le journal est conservé sur disque) | Lecture |
| `journalctl -u <service>` | Journal d'un seul service | Lecture |
| `journalctl -p err` | Messages de priorité « err » et plus graves (`-p 3`) | Lecture |
| `journalctl -xb` | Démarrage en cours, avec explications | Lecture |
| `dmesg` (souvent avec `sudo`, `-T` pour l'heure lisible) | Messages du noyau : disques, USB, pilotes, erreurs d'E/S | Lecture |
| `/var/log/syslog` (Debian/Ubuntu), `/var/log/messages` (Red Hat, Fedora) | Journaux texte classiques, selon la distribution | Lecture |
| `systemctl start` / `stop` / `restart <service>` | Démarrer, arrêter, redémarrer **maintenant** | Action |
| `systemctl enable` / `disable <service>` | Activer / désactiver **au démarrage** (ne démarre pas tout de suite, sauf `--now`) | Action |

Méthode : `systemctl status` dit **que** le service a échoué ; le **journal du service** dit
**pourquoi**. On corrige la cause (configuration, droits, espace, dépendance), on **teste la
configuration** quand l'outil le permet (`sshd -t`, `nginx -t`, `apachectl configtest`), puis on
redémarre le service et on vérifie de nouveau.

{_fig(SYSTEMCTL_SCREEN_FIGURE)}

## 4.3 Espace disque, montages, réseau : les commandes de lecture

| Commande | Ce qu'elle montre |
|---|---|
| `df -h` | Espace utilisé et disponible de chaque système de fichiers monté |
| `df -i` | **Inodes** utilisés et libres : un système de fichiers peut être « plein » de petits fichiers alors qu'il reste de la place |
| `du -xh -d1 <dossier>` | Taille des sous-dossiers (pour trouver ce qui grossit) |
| `lsblk` (`-f` : systèmes de fichiers et UUID) | Disques, partitions, points de montage |
| `mount`, `findmnt` | Systèmes de fichiers montés et leurs options (`ro` = lecture seule) |
| `ip addr` | Adresses IP et état des cartes réseau |
| `ip route` | Routes, dont la **passerelle par défaut** (`default via …`) |
| `ping <adresse>` | Joignabilité |
| `ss -tulpn` | Ports en écoute et programmes associés |
| `resolvectl status` (systemd-resolved) ou `cat /etc/resolv.conf` ; `dig <nom>` (paquet dnsutils/bind-utils) | Serveurs DNS utilisés ; résolution d'un nom — selon la distribution |

{_fig(DISK_FULL_SCREEN_FIGURE)}

**Un fichier supprimé mais encore ouvert** par un programme continue d'occuper le disque
jusqu'à sa fermeture (`lsof +L1` le montre « (deleted) »). On ne supprime pas au hasard dans
`/var` : on identifie ce qui grossit, on décide avec le responsable, on corrige la cause
(rotation des journaux par `logrotate`, purge d'un cache, `journalctl --vacuum-size=…` pour le
journal systemd).
"""


def _linux_rights() -> str:
    return """## 4.4 Droits Unix : lire `ls -l` avant de toucher

```text
-rw-r----- 1 marc compta 4096 mars 10 08:30 bilan.ods
│└┬┘└┬┘└┬┘   │    │
│ │  │  │    │    └ groupe propriétaire
│ │  │  │    └ utilisateur propriétaire
│ │  │  └ droits des autres : aucun
│ │  └ droits du groupe : lecture
│ └ droits du propriétaire : lecture, écriture
└ type : - fichier, d dossier, l lien
```

- **r** lecture, **w** écriture, **x** exécution (pour un dossier : droit d'y entrer). En
  chiffres : r = 4, w = 2, x = 1 (ex. `640` = rw-r-----).
- `chmod` change les droits (`chmod u+x script.sh`, `chmod 640 bilan.ods`) ; `chown` change le
  propriétaire et le groupe (`chown marc:compta bilan.ods`, en administrateur).
- « Permission denied » : vérifier **qui** est l'utilisateur (`id`), **à qui** appartient le
  fichier et **quels droits** s'appliquent (propriétaire, groupe ou autres), puis corriger le
  **minimum** : ajouter l'utilisateur au bon groupe, donner un droit précis.
- **Ne jamais recommander `chmod 777`** comme dépannage : tout le monde pourrait lire, modifier
  ou supprimer le fichier, et un script modifiable par tous devient une faille.

## 4.5 Paquets : apt, dnf et leurs messages

Un **gestionnaire de paquets** installe les logiciels **et leurs dépendances** depuis les
dépôts de la distribution. Les commandes **ne sont pas les mêmes partout** :

| Famille | Outil | Exemples de messages |
|---|---|---|
| Debian, Ubuntu | `apt` (`sudo apt update`, `sudo apt install <paquet>`) | `E: Unable to locate package …` (nom faux ou liste non mise à jour : `apt update`) ; `E: Could not get lock /var/lib/dpkg/lock-frontend` (une autre installation est en cours : attendre, ne pas supprimer le verrou) ; `dpkg was interrupted, you must manually run 'sudo dpkg --configure -a'` ; `The following packages have unmet dependencies` |
| Fedora, Red Hat | `dnf` (`sudo dnf install <paquet>`) | `Error: Unable to find a match: …` ; `Problem: … requires …, but none of the providers can be installed` |

Sur Ubuntu, une commande absente affiche souvent le paquet à installer : `Command 'ifconfig'
not found, but can be installed with: sudo apt install net-tools` — et l'on peut aussi utiliser
la commande actuelle équivalente (`ip addr`). Ne jamais forcer une installation en cassant les
dépendances : lire le message, mettre à jour la liste des paquets, vérifier la version de la
distribution.
"""


def _network_correlation() -> str:
    return """## 5.1 Réseau : tests gradués

| Message ou constat | Où chercher |
|---|---|
| « Connectivité limitée » (anciens Windows), « Aucun accès à Internet » | Adresse obtenue ? Passerelle ? DNS ? |
| Adresse **169.254.x.x** (masque 255.255.0.0) | **APIPA** : Windows s'est attribué cette adresse faute de réponse d'un serveur DHCP |
| « Média déconnecté » dans `ipconfig` | Couche physique : câble, prise, port, carte désactivée, Wi-Fi coupé |
| `ping` de la passerelle échoue | Réseau local : câble, Wi-Fi, switch, adresse ou masque faux |
| `ping 8.8.8.8` répond mais pas un nom (« La requête Ping n'a pas pu trouver l'hôte… ») | **DNS** |
| « Windows a détecté un conflit d'adresse IP » | Deux appareils ont la même adresse (adresse fixe dans la plage DHCP) |
| Imprimante « Hors ligne » | Imprimante allumée et en réseau ? Adresse changée ? Service Spouleur d'impression ? |

Ordre des tests : **physique** (voyants, câble, Wi-Fi) → **configuration du poste**
(`ipconfig /all`, `ip addr`) → **passerelle** (ping) → **Internet par adresse IP** (ping d'une
adresse publique) → **noms** (`nslookup`, `dig`). Le **périmètre** sépare les causes : un seul
poste touché → le poste ou son câble ; tous les postes → DHCP, DNS, routeur, fournisseur
d'accès. On distingue ainsi panne de l'OS, du DHCP, du DNS, de la couche physique et du routeur.

## 5.2 Messages du firmware et du POST

Les **bips**, LED et codes POST, ainsi que les messages du firmware, **dépendent du
constructeur** de la carte mère ou du PC : on lit le **manuel** du modèle, on ne se fie pas à
une table « universelle » trouvée en ligne. Méthode complète : [PR06](/uaa/ampcr-pratique-pr06).

## 5.3 Pannes intermittentes : chronologie et preuves

Une erreur qui apparaît « de temps en temps » ne se règle pas sur une intuition :

1. **Chronologie** : date et heure de chaque occurrence, ce que faisait l'utilisateur.
2. **Conditions** : température, charge (jeu, export, copie), branchement d'un périphérique,
   moment de la journée.
3. **Changements** : mises à jour, pilotes, matériel, réglages, déplacements du PC.
4. **Preuves** : événements du journal à chaque occurrence, relevés, captures.
5. Chercher ce qui **se répète à chaque panne** ; ce qui n'arrive qu'une fois est une
   **coïncidence** jusqu'à preuve du contraire.
6. **Reproduire** dans les mêmes conditions, puis tester **un changement à la fois**.

> **Erreur fréquente —** « Ça plante depuis l'orage, c'est l'orage. » Une coïncidence dans
> le temps n'est pas une preuve : il faut un test.
"""


def _report() -> str:
    return """## 6.1 Le modèle de compte rendu

| Rubrique | Contenu |
|---|---|
| **Demande** | Qui, quand, ce qui est demandé |
| **Environnement** | Poste, système, réseau, données concernées, sauvegarde existante |
| **Symptômes** | Ce que l'on observe, avec le **message exact** |
| **Preuves** | Captures, codes, événements, relevés de commandes |
| **Hypothèses** | Causes possibles, classées |
| **Tests** | Ce qui a été vérifié, dans l'ordre |
| **Résultats** | Ce que chaque test a donné |
| **Cause retenue** | Celle que les tests prouvent — ou « **cause non déterminée** », dit honnêtement |
| **Action** | Ce qui a été fait, **avec quelle autorisation** |
| **Validation** | Comment on a vérifié que le problème a disparu |
| **Risques résiduels** | Ce qui peut encore arriver (disque fatigué, réglage fragile) |
| **Recommandation** | Ce que le client devrait faire (sauvegarde, remplacement, formation) |
| **Clôture** | Date, accord du client |

## 6.2 Ce que l'on attend d'une réponse écrite

Une bonne réponse d'épreuve écrite contient :

1. des **étapes ordonnées** et numérotées, du plus simple au plus invasif ;
2. les **outils choisis**, nommés précisément (journal, console, commande et option) ;
3. pour chaque test, le **résultat attendu** et ce qu'il prouve ;
4. une **justification** de chaque choix (« parce que… ») ;
5. la **sécurité des données** : sauvegarde et accord avant toute action risquée ;
6. la **validation** finale.

**Exemple de réponse courte et complète.** Situation : « Le service d'impression d'un serveur
Linux ne démarre plus. » — « 1) Je lis l'état avec `systemctl status cups` pour savoir s'il est
en échec et depuis quand. 2) Je lis son journal avec `journalctl -u cups -b` pour trouver la
cause exacte. 3) Selon le message, je corrige la cause (configuration, droits, espace disque)
après avoir copié le fichier modifié. 4) Je redémarre le service (`systemctl restart cups`) et
je vérifie qu'il est `active (running)`. 5) J'imprime une page de test depuis un poste client.
6) Je note la cause et l'action dans le compte rendu. »
"""


def _cases() -> str:
    return r"""Chaque cas suit la même démarche : situation, message et preuves, stade, hypothèses
ordonnées, tests et résultats, cause retenue, action, validation et compte rendu. Supports
fictifs, messages au format réel.

<h3 class="jc-example-title">Cas 1 — Absence de démarrage : « Votre PC/appareil doit être réparé » (0xc000000f)</h3>

**Situation.** Le PC Windows 10 (UEFI, disque GPT) d'une fleuriste affiche l'écran de
récupération reproduit en section 2.2, depuis une coupure de courant pendant une mise à
jour. Ses factures sont sur le disque ; la dernière sauvegarde a un mois.

**Message et preuves.** « Les données de configuration de démarrage de votre PC sont manquantes
ou contiennent des erreurs. Fichier : `\EFI\Microsoft\Boot\BCD`. Code d'erreur : `0xc000000f`. »
Photo de l'écran prise.

**Stade.** Chargeur : le firmware a trouvé le disque et lancé Windows Boot Manager, qui ne lit
pas son BCD.

**Hypothèses ordonnées.** 1) magasin BCD abîmé par la coupure ; 2) partition EFI abîmée ;
3) disque défaillant.

**Tests et résultats.**

1. Firmware : le disque est détecté, mode UEFI, « Windows Boot Manager » en tête. → Pas de
   problème de détection ni de réglage.
2. Démarrage sur une clé d'installation de Windows > Réparer l'ordinateur > Invite de commandes :
   `dir D:\Users` montre les dossiers des utilisateurs (lecture seule). → Le volume Windows est
   lisible.
3. Sauvegarde des factures sur un disque externe (copie depuis l'invite de commandes) avec
   l'accord de la fleuriste.
4. **Réparation du démarrage** (réparation automatique, réversible dans son principe) : elle
   reconstruit les fichiers de démarrage. Redémarrage : Windows démarre.

**Cause retenue.** Configuration de démarrage (BCD) endommagée par la coupure pendant la mise à
jour ; le disque et les données sont intacts.

**Action.** Réparation automatique du démarrage. Les commandes manuelles (`bootrec`,
`bcdboot`) n'ont pas été nécessaires ; elles auraient été utilisées seulement après la
sauvegarde, volumes identifiés.

**Validation.** Trois redémarrages normaux, mise à jour réinstallée avec succès, factures
accessibles. Vérification de l'état du disque (aucune erreur).

**Compte rendu.** « PC bloqué au démarrage (code 0xc000000f, configuration de démarrage
endommagée après une coupure pendant une mise à jour). Disque détecté et lisible ; factures
sauvegardées avant intervention. Réparation automatique du démarrage : PC fonctionnel, mise à
jour installée. Recommandation : sauvegarde automatique et onduleur. »

<h3 class="jc-example-title">Cas 2 — Écran bleu après l'installation d'un pilote</h3>

**Situation.** Un consultant a installé lundi un pilote Wi-Fi « plus récent » téléchargé sur
un site de pilotes. Depuis, son portable affiche un écran bleu une ou deux fois par jour, et
redémarre seul.

**Message et preuves.** Écran bleu photographié par le consultant (capture fictive de la
section 3.1) et journal Système (capture fictive de la section 3.3).

Code d'arrêt `DRIVER_IRQL_NOT_LESS_OR_EQUAL` (0xD1) ; « Ce qui a échoué : wlanxv64.sys » (nom
inventé pour l'exercice). L'événement UserPnp de lundi montre l'ajout de ce pilote.

**Stade.** Noyau / pilote.

**Hypothèses ordonnées.** 1) le nouveau pilote Wi-Fi (cité par l'écran bleu, installé juste
avant les pannes) ; 2) mémoire ; 3) autre pilote.

**Tests et résultats.**

1. Le fichier cité correspond au pilote de la carte Wi-Fi (Gestionnaire de périphériques >
   carte Wi-Fi > Pilote > Détails du pilote). → Lien direct entre le code et le changement.
2. Gestionnaire de périphériques > carte Wi-Fi > **Restaurer le pilote** (réversible). Puis,
   par précaution, installation du pilote proposé par le **fabricant du portable**.
3. Observation pendant une semaine : aucun écran bleu. Test mémoire : aucune erreur (exclut
   l'hypothèse 2).

**Cause retenue.** Pilote Wi-Fi inadapté, installé depuis une source non officielle.

**Action.** Restauration du pilote précédent, puis pilote du fabricant.

**Validation.** Une semaine sans écran bleu ni nouvel événement BugCheck 1001 ; Wi-Fi
fonctionnel.

**Compte rendu.** « Écrans bleus (0xD1) depuis l'installation d'un pilote Wi-Fi tiers ; le
fichier cité est ce pilote. Pilote restauré puis remplacé par celui du fabricant ; test mémoire
sans erreur. Une semaine sans incident. Recommandation : pilotes uniquement depuis le site du
fabricant ou Windows Update. »

<h3 class="jc-example-title">Cas 3 — Périphérique en Code 43</h3>

**Situation.** Dans une pharmacie, le lecteur de cartes USB du comptoir ne fonctionne plus.
Le Gestionnaire de périphériques affiche la capture fictive de la section 3.2 : « Périphérique
USB inconnu (échec de la demande de descripteur de périphérique) », état « Windows a arrêté ce
périphérique car il a signalé des problèmes. (Code 43) ».

**Stade.** Pilote / périphérique : le système fonctionne, ce périphérique a signalé un défaut.

**Hypothèses ordonnées.** 1) liaison : câble, port, concentrateur USB non alimenté ;
2) lecteur défectueux ; 3) pilote.

**Tests et résultats.**

1. Le lecteur est branché sur un **concentrateur USB non alimenté**, avec un câble abîmé. On le
   branche **directement** sur un port arrière du PC, avec le même câble : toujours Code 43.
2. Autre câble USB, même port arrière : le lecteur est reconnu, plus de Code 43.
3. Ancien câble sur un autre PC : même échec. Le câble est en cause.

**Cause retenue.** Câble USB défectueux (test croisé : la panne suit le câble).

**Action.** Remplacement du câble ; lecteur branché directement sur le PC.

**Validation.** Lecture d'une carte réussie, état « Ce périphérique fonctionne correctement »,
après redémarrage aussi.

**Compte rendu.** « Lecteur de cartes en Code 43. Tests : branchement direct, autre câble,
câble d'origine sur un autre PC. Cause : câble USB défectueux. Câble remplacé, lecteur
fonctionnel. » Le Code 43 ne disait pas à lui seul si la cause était matérielle ou logicielle :
ce sont les tests qui ont tranché, **sans réinstaller de pilote inutilement**.

<h3 class="jc-example-title">Cas 4 — Linux : service en échec (« failed »)</h3>

**Situation.** Sur le serveur Debian d'une école, l'accès à distance par SSH ne fonctionne plus
depuis qu'un collègue a « durci » la configuration ce matin.

**Message et preuves.** Capture fictive de la section 4.2 (`systemctl status ssh` puis
`journalctl -u ssh -b`).

**Stade.** Service.

**Lecture.** `systemctl status` : le service `ssh` est `failed` ; c'est la vérification de la
configuration (`ExecStartPre=/usr/sbin/sshd -t`) qui a échoué. Le journal du service donne la
cause exacte : ligne 14 de `/etc/ssh/sshd_config`, option inconnue `PermitRootLogn` (faute de
frappe pour `PermitRootLogin`).

**Hypothèse.** Erreur de saisie dans le fichier modifié ce matin (le message est explicite, et
la modification est récente).

**Tests et action.**

1. On travaille **sur la console du serveur** (l'accès SSH ne fonctionne plus) ; copie du
   fichier : `cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak`.
2. Correction de la ligne 14 : `PermitRootLogin no` (valeur voulue par le collègue).
3. Test de la configuration **avant** de redémarrer : `sudo sshd -t` ne renvoie rien (pas
   d'erreur).
4. `sudo systemctl restart ssh`, puis `systemctl status ssh` : `active (running)`.

**Validation.** Connexion SSH réussie depuis un poste du réseau avec un compte autorisé ;
connexion directe de root refusée comme prévu ; plus d'erreur dans `journalctl -u ssh -b`.

**Compte rendu.** « Service SSH en échec après modification de sa configuration. Journal : option
mal orthographiée ligne 14. Fichier sauvegardé, ligne corrigée, configuration testée (sshd -t),
service redémarré. Accès distant rétabli. Recommandation : tester la configuration avant chaque
redémarrage du service. »

<h3 class="jc-example-title">Cas 5 — « No space left on device »</h3>

**Situation.** Le serveur Linux d'une association (partage de documents) refuse les nouveaux
fichiers depuis ce matin.

**Message et preuves.** Capture fictive de la section 4.3 : `cp` échoue avec « No space left
on device », puis `df -h` et `du`.

**Stade.** Stockage.

**Lecture.** `df -h` : la partition racine `/` est **pleine** (100 %, 0 disponible).
`du` remonte jusqu'à `/var/log/sauvegarde-agent` : 30 Go de journaux.

**Hypothèses.** 1) journaux d'un programme qui grossissent anormalement (mode « débogage »
oublié, absence de rotation) ; 2) autre consommation (vérifier aussi `df -i` : les inodes sont
à 3 %, ce n'est pas le problème ici).

**Tests et résultats.**

1. `ls -lh /var/log/sauvegarde-agent` : un fichier `agent.log` de 30 Go, qui grossit encore.
   La configuration de l'agent est en niveau de journal « debug » depuis un test du mois
   dernier.
2. `lsof +L1` : aucun fichier supprimé encore ouvert.

**Cause retenue.** Journal de l'agent de sauvegarde en mode débogage, sans rotation.

**Action (avec l'accord du responsable).** Copie des dernières lignes utiles du journal
(`tail -n 1000`), remise du niveau de journal normal dans la configuration de l'agent, puis
**vidage** du fichier par `truncate -s 0` (le programme le garde ouvert : le supprimer ne
libérerait pas la place tant qu'il tourne), redémarrage de l'agent, et ajout d'une règle
`logrotate`. **Rien d'autre n'est supprimé au hasard.**

**Validation.** `df -h` : `/` à 34 % ; dépôt d'un fichier réussi ; le lendemain, journal de
l'agent de taille normale, rotation effectuée.

**Compte rendu.** « Partition système pleine (journal de l'agent de sauvegarde en mode débogage,
30 Go). Avec l'accord du responsable : niveau de journal normal, journal vidé, rotation mise en
place. Espace libre : 66 %. Recommandation : surveiller l'espace disque (alerte à 80 %). »
"""


def _pitfalls() -> str:
    return """> **Résumer le message au lieu de le recopier.** « Une erreur de démarrage » ne permet
> aucune recherche ; le texte exact et le code, si.

> **Une cause unique déduite d'un code.** Un STOP code ou un Code 43 donne des pistes, pas
> une conclusion : il faut un test.

> **Prendre une corrélation pour une cause.** Kernel-Power 41 dit qu'un arrêt n'était pas
> propre, pas pourquoi ; une mise à jour la veille n'est pas forcément coupable.

> **Réinstaller ou formater d'abord.** Action lourde, destructrice pour les preuves et parfois
> pour les données, qui ne prouve rien.

> **Initialiser un disque « non initialisé » ou accepter « Vous devez formater le disque ».**
> Cela écrit sur le disque : les données d'abord.

> **Lancer chkdsk /r sur un disque qui fait du bruit.** Sauvegarde ou clonage d'abord.

> **Réparer un système de fichiers Linux monté** (fsck sur un volume en cours d'utilisation).
> On démonte (support externe) et on sauvegarde avant.

> **`chmod 777` « pour que ça marche ».** On corrige le droit précis ou le groupe, jamais
> tous les droits pour tout le monde.

> **Supprimer des fichiers au hasard dans /var** pour libérer de la place. On identifie ce qui
> grossit et pourquoi, avec l'accord du responsable.

> **Supposer les mêmes commandes sur toutes les distributions.** `apt` sur Debian/Ubuntu,
> `dnf` sur Fedora/Red Hat ; les journaux texte changent aussi de nom.

> **Modifier /etc/fstab ou la configuration d'un service sans copie de sauvegarde et sans
> test** (`mount -a`, `sshd -t`) avant de redémarrer.

> **Oublier la validation et le compte rendu.** Une intervention non vérifiée et non tracée
> n'est pas terminée.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : six analyses de captures ou de journaux,
six procédures ordonnées (dont deux remises en ordre) et quatre cas croisés matériel / système
/ réseau. Rédige ta réponse sur papier **avant** d'ouvrir le corrigé. Ces mêmes exercices sont
proposés dans [S'entraîner](/uaa/{PR11_SLUG}/practice), avec correction après envoi.

{_exercises_html()}
"""


def _mini_exam() -> str:
    rows = "\n".join(
        f"| {i} | {item.title} | {item.kind} | {item.total_points:g} |"
        for i, item in enumerate(EXAM_ITEMS, start=1)
    )
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR11_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Toutes les informations nécessaires sont dans chaque question et ses
documents (captures et journaux fictifs, au format réel). **Aucune correction n'est visible
pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après l'envoi,
chaque réponse est corrigée selon la **grille analytique** de la question, puis tu vois ta note
sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise la grille.** La **méthode** (stade identifié, étapes ordonnées), la
**sécurité** (données protégées, accord avant toute action risquée), les **tests** (outil
précis et résultat attendu) et la **justification** de chaque choix — pas la récitation de
mots-clés. Une réponse techniquement juste formulée autrement est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur la grille : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé. Une action destructive
proposée sans sauvegarde ni accord fait perdre des points.
"""


def _memo() -> str:
    return """- **Recueillir** : texte exact, code, contexte, date et heure, déclencheur, changements
  récents, périmètre, criticité, données à préserver.
- **Situer le stade** : firmware/POST → chargeur → noyau/système → session → service →
  application → pilote / périphérique → stockage → réseau.
- **Code ≠ cause** : code → cause probable (documentation fiable) → hypothèse → test → résultat
  → action. Jamais une cause unique tirée d'un code ambigu.
- **Ordre** : données → preuves → tests simples → réparation réversible → invasif avec accord →
  validation.
- **Pas de démarrage** : disque détecté ? mode UEFI/GPT ou hérité/MBR ? ordre ? câbles ?
  partition EFI ? puis BCD/GRUB. Pas de formatage réflexe.
- **Windows** : écran bleu → code + fichier + BugCheck 1001 ; Gestionnaire de périphériques →
  numéro de code (10, 22, 28, 43) ; Observateur → source, ID, niveau, heure ; corrélation ≠
  causalité ; DISM puis SFC ; chkdsk sans paramètre = lecture, /f et /r = modification.
- **Linux** : `systemctl status` (que) puis `journalctl -u … -b` (pourquoi) ; `-p err` ;
  `dmesg` ; `df -h` **et** `df -i` ; `lsblk -f` vs `/etc/fstab` ; copie + test (`mount -a`,
  `sshd -t`) avant redémarrage ; jamais `chmod 777` ; apt ≠ dnf.
- **Réseau** : 169.254 = pas de DHCP ; passerelle → IP publique → nom ; un poste ou tous ?
- **Intermittent** : chronologie, conditions, changements, preuves ; ce qui se répète.
- **Compte rendu** : demande, environnement, symptômes, preuves, hypothèses, tests, résultats,
  cause (ou non déterminée), action et autorisation, validation, risques, recommandation,
  clôture.
"""


def _sources() -> str:
    return """## Sources utilisées pour les messages, codes et commandes

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigences AP-09,
  AP-13 et AP-15. Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
- **Windows — démarrage et récupération** : documentation Microsoft Learn (Windows Boot
  Manager et BCD, `bcdedit`, `bcdboot`, `bootrec`, environnement de récupération WinRE,
  partitions UEFI/GPT par défaut de Windows, `mbr2gpt`).
- **Windows — codes d'arrêt** : référence Microsoft des *bug check codes* (0xA, 0xD1, 0x1A,
  0x50, 0x7B, 0xEF, 0x116, 0x124) ; événements Kernel-Power 41, EventLog 6008, BugCheck 1001.
- **Windows — Gestionnaire de périphériques** : liste Microsoft des codes d'erreur du
  Gestionnaire de périphériques (Codes 10, 22, 28, 43).
- **Windows — outils** : documentation Microsoft de `sfc`, `DISM /Cleanup-Image`, `chkdsk`
  (/f, /r, /scan), `ipconfig`, `ping`, `nslookup`, `tracert`, `msconfig` ; code
  0x80070070 (ERROR_DISK_FULL) ; événements Service Control Manager 7000/7009/7031/7038, disk
  7/153, User Profile Service 1511, WindowsUpdateClient 19/20.
- **Linux** : pages de manuel (`man`) de `systemctl`, `journalctl`, `dmesg`, `df`, `du`,
  `lsblk`, `blkid`, `mount`, `findmnt`, `fstab(5)`, `ip`, `ss`, `resolvectl`, `dig`, `chmod`,
  `chown`, `lsof`, `truncate` ; manuel de GRUB 2 (mode rescue) ; documentation Debian/Ubuntu
  (`apt`, `dpkg`, initramfs) et Fedora (`dnf`) ; `sshd(8)` (option `-t`).
- **Réseau** : adresses link-local IPv4 169.254.0.0/16 (RFC 3927, APIPA sous Windows).

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 demande les principaux messages d'erreur, leur interprétation et les
démarches d'intervention (AP-09, AP-13) et le dépannage des dysfonctionnements courants
(AP-15). Sont des **compléments**, signalés comme tels :

- la protection des données et l'autorisation avant toute action risquée (AP-C03) ;
- la rédaction de la réponse et du compte rendu (AP-C01, approfondis en PR29) ;
- les outils précis cités en exemple (WinDbg, `lsof`, `logrotate`, `resolvectl`), les inodes,
  l'option `nofail` de fstab.

## Supports fictifs

Les cas, captures, journaux, noms de machines, de personnes, de pilotes et UUID de ce cours
sont **fictifs** et reconstitués pour l'entraînement. Les messages, codes et commandes suivent
le format réel des systèmes cités, mais la présentation exacte varie selon la version et la
langue du système. Aucun n'est une question officielle ou déjà posée par le Jury.
"""


def pr11_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR11 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR11 — 1. Méthode universelle : lire un message d'erreur", _method()),
        ("PR11 — 2. Démarrage et partitions : firmware, Windows Boot Manager, WinRE", _boot_windows()),
        ("PR11 — 2. Démarrage et partitions : GRUB, initramfs, fstab, MBR/GPT", _boot_linux()),
        ("PR11 — 3. Windows : écrans bleus, périphériques, journaux", _windows_symptoms()),
        ("PR11 — 3. Windows : disques, services, commandes, mises à jour", _windows_tools()),
        ("PR11 — 4. Linux : messages, systemd, journald, espace disque", _linux_systemd()),
        ("PR11 — 4. Linux : droits Unix et gestionnaires de paquets", _linux_rights()),
        ("PR11 — 5. Réseau, périphériques et pannes intermittentes", _network_correlation()),
        ("PR11 — 6. Compte rendu professionnel et réponse écrite attendue", _report()),
        ("PR11 — Exemples : cinq cas intégralement résolus", _cases()),
        ("PR11 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR11 — Exercices corrigés ({len(PRACTICE_ITEMS)})", _exercises_intro()),
        ("PR11 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR11 — Fiche mémo", _memo()),
        ("PR11 — Sources et compléments pédagogiques", _sources()),
    ]
