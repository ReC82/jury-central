"""Cours PR07 « Systèmes d'exploitation, GUI/CLI et prérequis d'installation » — parcours AMPCR
pratique écrite (ticket #207).

Matière : intégralement celle du ticket #207 (rôle d'un système d'exploitation et fonctions
noyau/pilotes/système de fichiers/comptes/services/interface, Windows et Linux courants sans
figer de version, prérequis matériel/firmware/UEFI/démarrage sécurisé/TPM selon l'édition,
sauvegarde, licences, installation propre ou mise à niveau, média d'installation, ordre de
démarrage, GPT/ESP, partitionnement et pilotes, comptes et sécurité initiale, outils GUI/CLI,
notions de virtualisation), découpée en blocs titrés (le titre pilote le type de carte,
`app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention » ni « mémo » —
donc pas « mémoire »).
Données et schémas : `app.v1.ampcr_pratique_pr07_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr07_bank`. Mise en forme partagée avec les autres cours pratiques.
L'installation détaillée de Windows et de Linux relève de PR08 et PR09 (non publiés à la
rédaction : renvoi en texte seulement).
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr07_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr07_figures import (
    BOOT_LEGACY_ENTRY,
    BOOT_MENU_FIGURE,
    BOOT_UEFI_ENTRY,
    CASE2_SETTINGS,
    CASE2_VERDICT,
    CHECK_FIGURE,
    EDITION_FEATURES,
    EDITION_HOME,
    EDITION_PRO,
    HOST_RESERVE_GIB,
    INSTALL_PLAN_FIGURE,
    INSTALL_TREE_FIGURE,
    LAYERS_FIGURE,
    LICENCE_ROWS,
    MEDIA_FIGURE,
    MSINFO_FIGURE,
    OS_FAMILIES,
    OS_FUNCTIONS,
    PROCEDURES,
    TOOLS,
    UBUNTU_DESKTOP_RECOMMENDED,
    VM_FIGURE,
    WIN11_REQUIREMENTS,
    WRITTEN_AT,
    install_type,
    usable_ram_gib,
    vm_plan,
)

PR07_TITLE = "Systèmes d'exploitation, GUI/CLI et prérequis d'installation"
PR07_SLUG = "ampcr-pratique-pr07"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr07") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _functions_table() -> str:
    rows = "\n".join(f"| **{f.name}** | {f.role} | {f.windows} | {f.linux} |" for f in OS_FUNCTIONS)
    return "| Fonction | Rôle | Sous Windows | Sous Linux |\n|---|---|---|---|\n" + rows


def _families_table() -> str:
    rows = "\n".join(
        f"| **{f.name}** | {f.publisher_licence} | {f.hardware} | {f.typical_use} | {f.lifecycle} |"
        for f in OS_FAMILIES
    )
    return ("| Système | Licence | Matériel | Usages typiques | Cycle de vie |\n|---|---|---|---|---|\n" + rows)


def _editions_table() -> str:
    rows = "\n".join(
        f"| {need} | {'oui' if home else 'non'} | oui |" for need, home in EDITION_FEATURES
    )
    return f"| Besoin | {EDITION_HOME} | {EDITION_PRO} |\n|---|---|---|\n" + rows


def _tools_table() -> str:
    rows = "\n".join(
        f"| **{t.task}** | {t.windows_gui} | `{t.windows_cli}` | {t.linux_gui} | `{t.linux_cli}` |" for t in TOOLS
    )
    return ("| Information | Windows — graphique | Windows — commande | Linux — graphique | Linux — commande |\n"
            "|---|---|---|---|---|\n" + rows)


def _win11_table() -> str:
    rows = "\n".join(f"| **{r.item}** | {r.minimum} | {r.how_to_check} |" for r in WIN11_REQUIREMENTS)
    return "| Élément | Minimum publié | Où le vérifier |\n|---|---|---|\n" + rows


def _licences_table() -> str:
    rows = "\n".join(f"| **{kind}** | {transfer} | {reinstall} |" for kind, transfer, reinstall in LICENCE_ROWS)
    return "| Licence | Transfert | Réinstallation et activation |\n|---|---|---|\n" + rows


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
p. 3). On ne te demande pas d'installer un système devant le jury, mais de **choisir** un
système et son édition, de **vérifier** les prérequis d'un PC, de **lire** une capture
(Informations système, menu de démarrage, terminal) et de **rédiger** un plan d'installation
sûr. Tu dois savoir :

1. **expliquer** le rôle d'un système d'exploitation : noyau, pilotes, système de fichiers,
   comptes, services, interface ;
2. **comparer** les systèmes du marché (Windows, distributions Linux, macOS, ChromeOS) et les
   **éditions** de Windows ;
3. **utiliser** l'interface graphique (GUI) **et** la ligne de commande (CLI) pour relever un
   PC, et dire quand préférer l'une ou l'autre ;
4. **vérifier** les prérequis : processeur 64 bits, mémoire, stockage, **UEFI**, **démarrage
   sécurisé**, **TPM 2.0** ;
5. **préparer** l'intervention : **sauvegarde**, **licences**, **installation propre ou mise à
   niveau** ;
6. **préparer** le média d'installation et **démarrer** dessus dans le bon mode ;
7. **prévoir** les partitions (GPT, ESP) et les **pilotes** ;
8. **sécuriser** le système dès l'installation (comptes, mises à jour, protection) ;
9. **expliquer** la virtualisation et vérifier ses prérequis.

Ce cours contient **3 procédures illustrées** :

{_procedures_list()}

## Exigences officielles travaillées dans ce cours

{_req("AP-08")}
{_req("AP-12")}

Le cours prépare aussi l'installation complète des systèmes, traitée en détail ensuite :

{_req("AP-10")}

et s'appuie sur la protection des données du client vue en
[PR04](/uaa/ampcr-pratique-pr04) :

{_req("AP-C03")}

Les partitions, MBR/GPT et la partition EFI sont expliqués en
[PR05](/uaa/ampcr-pratique-pr05), les messages de démarrage en
[PR11](/uaa/ampcr-pratique-pr11) et l'identification des composants en
[PR01](/uaa/ampcr-pratique-pr01). L'installation complète de Windows (PR08), celle de Linux
(PR09) et les comptes, pilotes et commandes (PR10) font l'objet des cours suivants du parcours.

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC07 BIOS, UEFI, POST et démarrage](/uaa/ampcr-mc07),
[MC08 Partitionnement, GPT/MBR et formatage](/uaa/ampcr-mc08),
[MC09 Installer Windows proprement](/uaa/ampcr-mc09),
[MC10 Windows : administration et commandes essentielles](/uaa/ampcr-mc10),
[MC11 Linux : bases utiles au technicien PC-réseaux](/uaa/ampcr-mc11) et
[MC12 Pilotes, périphériques et logiciels](/uaa/ampcr-mc12). Ce cours-ci est **pratique** :
choix justifiés, prérequis vérifiés, captures à lire et plans d'intervention rédigés, comme dans
un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **quatre
scénarios corrigés**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans
« S'entraîner », correction après envoi), puis passe le **mini-examen noté sur
{EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les captures, relevés et situations de ce cours sont des **supports fictifs**
> construits pour s'entraîner. Les prérequis cités sont ceux **publiés par les éditeurs en
> {WRITTEN_AT}** : ils changent avec les versions, et la **page officielle de l'éditeur fait
> foi** le jour de l'intervention. Aucun exercice n'est une question officielle ni une question
> déjà posée par le Jury. **Installer un système efface la partition visée : jamais sans
> sauvegarde vérifiée et accord écrit du propriétaire.**
"""


def _role() -> str:
    return f"""**Objectifs** : expliquer à quoi sert un système d'exploitation et situer ses parties,
pour comprendre ce que l'on installe, configure ou dépanne.

## 1.1 À quoi sert un système d'exploitation

Le **système d'exploitation** (OS, *operating system*) est le logiciel qui démarre après le
firmware et qui **gère le matériel pour les programmes** : sans lui, chaque application devrait
savoir piloter elle-même chaque disque, chaque carte réseau, chaque écran. Il **partage** les
ressources du PC entre les programmes et entre les utilisateurs, et il **protège** chacun des
autres.

{_functions_table()}

## 1.2 Les couches

{_fig(LAYERS_FIGURE)}

- Une **application** ne parle jamais directement au matériel : elle demande au **noyau**, qui
  passe par le **pilote** du périphérique.
- Un **pilote** manquant ou inadapté = un matériel qui ne fonctionne pas (ou mal), même s'il est
  en parfait état : c'est pourquoi on **prépare les pilotes** avant d'installer.
- Les **services** travaillent sans fenêtre : un service arrêté (impression, mises à jour) peut
  expliquer une panne sans aucun message à l'écran.
- L'**interface** n'est que la partie visible : la même configuration peut se lire en
  **graphique (GUI)** ou en **ligne de commande (CLI)** — chapitre 4.

**Procédure professionnelle (à rédiger)** : décrire la panne ou le besoin → dire quelle partie
du système est concernée (pilote, service, compte…) → citer l'outil qui permet de le vérifier.

**Erreur fréquente** : confondre le système d'exploitation et l'interface (« Linux, c'est un
écran noir ») ou le système et le firmware (« le BIOS de Windows »).

**À l'écrit** : la **fonction** + un **exemple concret** sur le PC du cas (« le pilote de la
carte Wi-Fi traduit… »), pas une définition récitée.

**Repère rapide** : **application → noyau → pilote → matériel** ; services en arrière-plan ;
interface GUI ou CLI. Exercices liés : {_ex("E04")}.
"""


def _market() -> str:
    return f"""**Objectifs** : présenter les systèmes actuellement sur le marché et choisir en fonction
du besoin, du matériel et du support dans le temps.

## 2.1 Les grandes familles

{_families_table()}

## 2.2 Distribution Linux, version à support long, environnement de bureau

- **Linux** est un **noyau** ; une **distribution** (Ubuntu, Debian, Linux Mint, Fedora…)
  l'assemble avec des programmes, un installateur et un **gestionnaire de paquets** (`apt` pour
  Debian, Ubuntu et Mint, `dnf` pour Fedora) qui installe et met à jour les logiciels depuis des
  dépôts officiels.
- Une version **LTS** (*Long Term Support*, support long) reçoit des mises à jour de sécurité
  pendant plusieurs années : c'est le choix normal pour un poste de travail ou un serveur.
- L'**environnement de bureau** est l'interface graphique : **GNOME** ou **KDE Plasma**
  (complets), **Xfce** ou **LXQt** (légers, adaptés à un PC ancien). Un **serveur** s'installe
  souvent **sans** interface graphique et s'administre en ligne de commande.

## 2.3 Choisir un système : les quatre questions

1. **Quels logiciels sont indispensables ?** Un logiciel métier « Windows uniquement » impose
   Windows ; un usage web et bureautique laisse le choix.
2. **Dans quel environnement ?** Un réseau d'entreprise avec domaine Active Directory impose une
   édition de Windows qui sait le rejoindre (chapitre 3).
3. **Quel matériel ?** Un PC qui ne respecte pas les prérequis de Windows 11 peut recevoir une
   distribution Linux légère ; un Mac reçoit macOS.
4. **Pour combien de temps ?** Un système qui ne reçoit plus de mises à jour de sécurité ne
   doit plus servir en ligne : on vérifie la **date de fin de support** de la version.

**Procédure professionnelle (à rédiger)** : relever les logiciels et contraintes → relever le
matériel → comparer aux prérequis et au cycle de vie → proposer **un** système (et son édition)
avec **deux** justifications, et une alternative si le premier choix est impossible.

**Erreur fréquente** : proposer « le système que je préfère » sans regarder les logiciels du
client, ou laisser en service un système sans mises à jour de sécurité.

**À l'écrit** : système + édition ou distribution + justification par le **besoin** et le
**matériel**.

**Repère rapide** : **logiciels → environnement → matériel → durée de support**. Exercices
liés : {_ex("E09", "E10")}.
"""


def _editions() -> str:
    return f"""**Objectifs** : choisir l'édition de Windows adaptée au besoin et tenir compte du cycle
de vie des versions.

## 3.1 Famille ou Professionnel

{_editions_table()}

Il existe aussi des éditions **Entreprise** et **Éducation**, distribuées par contrat aux
organisations. Pour un particulier ou une petite entreprise, le choix se fait entre **Famille**
et **Professionnel**.

## 3.2 Versions, mises à jour et fin de support

- Microsoft publie des **mises à jour** chaque mois et une **mise à jour de fonctionnalités**
  environ chaque année ; chaque version a une **date de fin de support** publiée.
- **Windows 10** n'est plus pris en charge depuis le **14 octobre 2025** (sauf programme payant
  de mises à jour de sécurité étendues) : un PC qui reste sous Windows 10 ne reçoit plus de
  correctifs de sécurité.
- On ne retient pas une liste de versions par cœur : on **vérifie la page de cycle de vie** de
  l'éditeur le jour de l'intervention.

**Procédure professionnelle (à rédiger)** : lister les besoins → cocher ceux que l'édition
Famille ne couvre pas → si un seul manque, édition Professionnel → vérifier que la **licence**
correspond à l'édition installée (chapitre 8).

**Erreur fréquente** : installer l'édition Famille dans une entreprise à domaine, ou
l'édition Professionnel sur un PC dont la licence est Famille (Windows ne s'active pas).

**À l'écrit** : l'édition + le **besoin** qui l'impose (domaine, BitLocker, hôte Bureau à
distance, Hyper-V).

**Repère rapide** : **domaine, BitLocker, hôte Bureau à distance, Hyper-V, gpedit → Pro**.
Exercices liés : {_ex("E05", "E16")}.
"""


def _gui_cli() -> str:
    return f"""**Objectifs** : relever les informations d'un PC en interface graphique et en ligne de
commande, et choisir l'outil adapté à la situation.

## 4.1 Deux façons de dialoguer avec le système

- **Interface graphique (GUI)** : fenêtres, menus, souris. Facile à découvrir, guide
  l'utilisateur ; mais chaque écran change d'une version à l'autre et se décrit mal par écrit.
- **Interface en ligne de commande (CLI)** : on tape une commande, le système répond en texte.
  Sous Windows : **Invite de commandes** (`cmd`) et **PowerShell**, regroupés dans le **Terminal
  Windows** ; sous Linux : un **terminal** avec le shell **bash**. Une commande est **exacte**,
  **reproductible**, se **copie** dans un rapport, s'**automatise** (script) et fonctionne **à
  distance** (SSH) sur un serveur sans écran.

## 4.2 Les outils du technicien

{_tools_table()}

{_console(
    "PS C:\\> systeminfo | findstr /B /C:\"Nom du système\" /C:\"Mémoire physique totale\"",
    "Nom du système d'exploitation:    Microsoft Windows 11 Professionnel",
    "Mémoire physique totale:          16 263 Mo",
    "",
    "$ cat /etc/os-release | grep PRETTY_NAME ; free -h | grep Mem",
    'PRETTY_NAME="Ubuntu 24.04.1 LTS"',
    "Mem:    15Gi   3,1Gi   9,2Gi",
)}

*Relevés fictifs, à titre d'illustration : le texte exact varie selon la langue et la version.*

## 4.3 Droits d'administration

Beaucoup de commandes de configuration exigent des **droits d'administration** : sous Windows,
« Exécuter en tant qu'administrateur » (le Contrôle de compte d'utilisateur demande
confirmation) ; sous Linux, la commande est précédée de **`sudo`** et demande le mot de passe de
l'utilisateur autorisé. On ne travaille pas en permanence avec ces droits (chapitre 13).

**Procédure professionnelle (à rédiger)** : pour chaque information demandée, citer **un chemin
graphique et une commande**, préciser s'il faut des droits d'administration, et noter le
résultat exact dans le rapport.

**Erreur fréquente** : décrire un chemin de menus approximatif quand une commande donne la
réponse exacte, ou lancer une commande d'administration sans comprendre ce qu'elle modifie.

**À l'écrit** : la **commande exacte** (orthographe, options) et ce qu'elle **affiche** ou
**change**.

**Repère rapide** : **GUI pour découvrir et montrer au client · CLI pour mesurer, documenter,
répéter et intervenir à distance**. Exercices liés : {_ex("E04", "E09")}.
"""


def _architecture() -> str:
    usable = usable_ram_gib(8, 32)
    return f"""**Objectifs** : vérifier que le système choisi correspond au processeur et à la quantité
de mémoire du PC.

## 5.1 32 bits ou 64 bits

- Un processeur **64 bits** (architecture **x64**, aussi notée x86-64 ou AMD64) exécute un
  système 64 bits **ou** 32 bits ; un processeur **32 bits** n'exécute qu'un système 32 bits.
- Un système **32 bits** ne peut adresser que **2^32 octets = {usable:g} Gio** : avec 8 Go
  installés, il n'en utilise qu'**environ 3,2 à 3,5 Gio**, le reste de l'espace d'adresses étant
  réservé aux périphériques.
- **Windows 11 n'existe qu'en 64 bits** et la plupart des distributions Linux actuelles ne
  publient plus d'image 32 bits pour PC.
- On **ne passe pas** d'un système 32 bits à un système 64 bits par une mise à niveau : il faut
  une **installation propre** (chapitre 9).

## 5.2 x64 ou ARM

Certains portables récents ont un processeur **ARM64** (par exemple Snapdragon) : ils reçoivent
la version ARM de Windows ou de Linux, pas la version x64. Avant de télécharger une image, on
vérifie **l'architecture** : `msinfo32` (« Type du système ») ou `uname -m` (`x86_64` ou
`aarch64`).

## 5.3 Mémoire et stockage

Chaque système publie un **minimum** (le système démarre) et souvent une configuration
**recommandée** (le système est confortable). Pour un poste de travail, on vise au-dessus du
minimum : par exemple **8 Go** pour Windows 11 en bureautique, et un **SSD** pour le système.

**Procédure professionnelle (à rédiger)** : relever « Type du système » ou `uname -m`, la
mémoire installée et utilisable, le stockage → choisir l'image de la bonne architecture.

**Erreur fréquente** : croire qu'une barrette est défectueuse parce qu'un système 32 bits
n'affiche que 3,2 Go utilisables, ou télécharger une image x64 pour un portable ARM.

**À l'écrit** : l'architecture du processeur **et** celle du système, avec le calcul de la
limite 32 bits si elle explique le symptôme.

**Repère rapide** : **32 bits = 4 Gio au plus · Windows 11 = 64 bits · 32 → 64 bits =
installation propre**. Exercices liés : {_ex("E09", "E11")}.
"""


def _firmware() -> str:
    return f"""**Objectifs** : relever et régler le firmware avant une installation : mode de démarrage,
démarrage sécurisé, TPM.

## 6.1 UEFI ou mode hérité

- Le **firmware** démarre le PC avant le système. Les PC récents ont un firmware **UEFI** ;
  beaucoup peuvent aussi imiter l'ancien BIOS grâce au **mode de compatibilité (CSM, mode
  hérité, « Legacy »)**.
- En **UEFI**, le système démarre depuis un disque **GPT** grâce à la **partition EFI (ESP)** ;
  en **mode hérité**, depuis un disque **MBR** (détails en [PR05](/uaa/ampcr-pratique-pr05)).
- Windows 11 exige l'UEFI : un PC réglé en mode hérité doit être **converti** (disque MBR → GPT
  avec `mbr2gpt`, après sauvegarde) **puis** basculé en UEFI. Dans l'ordre inverse, Windows ne
  démarre plus.

## 6.2 Démarrage sécurisé (Secure Boot)

- Le **démarrage sécurisé** est une fonction de l'UEFI : le firmware ne lance que des
  chargeurs **signés** par une clé reconnue. Il bloque les programmes malveillants qui
  s'installent avant le système.
- Il **n'existe pas en mode hérité** : msinfo32 affiche alors « Non pris en charge ».
- Windows 11 exige un firmware **compatible** démarrage sécurisé ; l'**activer** est recommandé.
- Les grandes distributions Linux (Ubuntu, Debian, Fedora, Linux Mint) démarrent **avec** le
  démarrage sécurisé grâce à un petit chargeur signé (**shim**) : inutile de le désactiver. Un
  pilote tiers **compilé sur le PC** (par exemple un pilote NVIDIA installé par DKMS) n'est pas
  signé par la distribution : on enregistre alors une clé locale (**MOK**) au redémarrage.

## 6.3 TPM 2.0

- Le **TPM** (*Trusted Platform Module*) est un composant de sécurité qui conserve des clés de
  chiffrement (BitLocker, connexion Windows Hello). Il peut être une puce ou être **intégré au
  processeur** : **Intel PTT** ou **AMD fTPM**, parfois **désactivé** par défaut dans le
  firmware.
- Windows 11 exige la **version 2.0** : `tpm.msc` affiche « Version de la spécification ».
- Avant de toucher au firmware d'un PC chiffré par **BitLocker**, on sauvegarde la **clé de
  récupération** : un changement de réglage peut la faire demander au démarrage.

{_console(
    "PS C:\\> Confirm-SecureBootUEFI        (PowerShell administrateur)",
    "True",
    "PS C:\\> Get-Tpm | Select-Object TpmPresent, TpmReady",
    "TpmPresent TpmReady",
    "---------- --------",
    "      True     True",
    "",
    "$ mokutil --sb-state                   (Linux)",
    "SecureBoot enabled",
)}

*Relevés fictifs. Sur un PC en mode hérité, `Confirm-SecureBootUEFI` répond que la commande
n'est pas prise en charge sur cette plateforme, et le dossier `/sys/firmware/efi` n'existe pas
sous Linux.*

**Procédure professionnelle (à rédiger)** : relever Mode BIOS, État du démarrage sécurisé et
version du TPM → sauvegarder (et la clé BitLocker) → régler un point à la fois (conversion GPT
avant bascule UEFI) → contrôler à nouveau.

**Erreur fréquente** : basculer en UEFI un PC qui démarre en MBR, désactiver le démarrage
sécurisé « par habitude » pour installer Linux, ou désactiver le TPM d'un PC chiffré.

**À l'écrit** : la **lecture** du relevé (« Mode BIOS : Hérité → … ») puis le **réglage** et
son **ordre**.

**Repère rapide** : **UEFI + GPT + ESP · démarrage sécurisé = UEFI seulement · TPM 2.0 =
tpm.msc · mbr2gpt avant la bascule**. Exercices liés : {_ex("E06", "E08", "E13")}.
"""


def _requirements() -> str:
    ubuntu = " ; ".join(UBUNTU_DESKTOP_RECOMMENDED)
    return f"""**Objectifs** : comparer un PC aux prérequis publiés et conclure clairement :
compatible, compatible après réglages, ou non compatible.

## 7.1 Windows 11 (prérequis publiés par Microsoft, relevés en {WRITTEN_AT})

{_win11_table()}

L'application **Contrôle d'intégrité du PC** de Microsoft fait la comparaison
automatiquement ; le technicien sait **lire** et **expliquer** son résultat. Un processeur
absent de la liste ou un TPM 1.2 sont des **blocages matériels** : aucun réglage ne les corrige,
et l'on ne propose pas d'installation non prise en charge.

## 7.2 Une distribution Linux

Exemple : pour sa version Desktop, Ubuntu recommande **{ubuntu}**. Une distribution avec un
bureau léger (Xfce, LXQt) demande moins ; une version serveur sans interface graphique encore
moins. Le **démarrage sécurisé** et le **TPM** ne sont pas exigés.

## 7.3 Trois verdicts

- **Compatible tel quel** : on peut installer ou mettre à niveau.
- **Compatible après réglages du firmware** : mode UEFI (après conversion GPT), TPM intégré à
  activer.
- **Non compatible** : processeur, mémoire, stockage ou TPM insuffisants → autre système, autre
  version prise en charge, ou remplacement du matériel.

{_fig(CHECK_FIGURE)}

**Procédure professionnelle (à rédiger)** : procédure 1 ci-dessus, en citant pour chaque
critère la **valeur relevée** et le **minimum**.

**Erreur fréquente** : conclure « non compatible » pour un PC simplement réglé en mode hérité
ou dont le TPM intégré est désactivé ; à l'inverse, proposer de contourner un blocage matériel.

**À l'écrit** : un tableau ou une liste « critère — relevé — minimum — conforme ? », puis le
**verdict** et la **solution**.

**Repère rapide** : **relevé → minimum → verdict → solution**. Exercices liés :
{_ex("E03", "E06", "E08")}.
"""


def _backup_licences() -> str:
    return f"""**Objectifs** : protéger les données et les droits d'utilisation du client avant toute
installation.

## 8.1 Sauvegarde

Une installation **efface la partition du système** ; même une mise à niveau peut échouer. Avant
d'intervenir (règle AP-C03, vue en [PR04](/uaa/ampcr-pratique-pr04)) :

- **accord écrit** du client sur ce qui sera effacé ;
- sauvegarde des **données** (documents, photos, bureau, téléchargements), des **favoris** et
  du **courrier**, des **mots de passe** enregistrés si le client le souhaite, sur un **autre
  support** ;
- **copie vérifiée** (fichiers ouverts au hasard, tailles comparées) ;
- **clé de récupération BitLocker** si le disque est chiffré.

## 8.2 Licences et activation

{_licences_table()}

- La **licence** est le droit d'utiliser le logiciel ; l'**activation** vérifie ce droit.
  Réinstaller la **même édition** sur le **même PC** s'active normalement tout seul.
- On relève aussi les **licences des logiciels** du client (suite bureautique, logiciels
  métiers) et leurs installateurs : ils seront à réinstaller après une installation propre.
- On n'utilise jamais une clé « trouvée sur Internet » ni un outil d'activation pirate.

**Procédure professionnelle (à rédiger)** : accord écrit → sauvegarde vérifiée → relevé de
l'édition, de la licence et des logiciels à réinstaller → clé BitLocker → seulement alors,
l'installation.

**Erreur fréquente** : « on garde D:, pas besoin de sauvegarde », ou installer une autre édition
que celle de la licence.

**À l'écrit** : ce que l'on sauvegarde, **où**, comment on **vérifie**, et la situation de la
**licence**.

**Repère rapide** : **accord → sauvegarde vérifiée → licences → clé BitLocker**. Exercices liés :
{_ex("E01", "E12", "E16")}.
"""


def _clean_or_upgrade() -> str:
    return f"""**Objectifs** : choisir entre une installation propre et une mise à niveau sur place, et
le justifier.

## 9.1 Deux démarches

- **Mise à niveau sur place** : lancée **depuis le système en marche** ; elle remplace le
  système mais **conserve** fichiers, programmes et réglages. Elle suppose un système **sain**,
  de la **même famille** et de la **même architecture**, et une édition compatible (Famille →
  Famille, Professionnel → Professionnel).
- **Installation propre** : démarrage sur le média, partition du système **effacée**, système
  neuf ; programmes réinstallés et données restaurées. Plus longue, mais elle **repart de
  zéro**.

## 9.2 L'arbre de décision du cours

{_fig(INSTALL_TREE_FIGURE)}

Par exemple, un PC sous Windows 10 **32 bits** que l'on veut passer à Windows 11 (64 bits
uniquement) donne : « {install_type(backup_ok=True, requirements_ok=True, same_family_and_arch=False,
system_healthy=True, keep_programs=True)} ».

**Procédure professionnelle (à rédiger)** : parcourir l'arbre dans l'ordre et noter la réponse
à chaque question ; annoncer au client ce qui sera **conservé** et ce qui sera **à
réinstaller**.

**Erreur fréquente** : proposer une mise à niveau pour « réparer » un système infecté ou
instable, ou pour passer de 32 à 64 bits.

**À l'écrit** : la démarche + la **raison décisive** (architecture, état du système, souhait du
client) + la sauvegarde préalable.

**Repère rapide** : **sauvegarde → prérequis → même famille et architecture → système sain →
garder les programmes ?** Exercices liés : {_ex("E07", "E11")}.
"""


def _media() -> str:
    return f"""**Objectifs** : préparer un média d'installation fiable.

## 10.1 L'image officielle

- On télécharge l'**image** (fichier **ISO**) ou l'**outil de création** **sur le site officiel**
  de l'éditeur, pour la **version**, l'**édition** et l'**architecture** voulues.
- On contrôle l'image avec sa **somme de contrôle SHA-256** publiée par l'éditeur :
  `Get-FileHash fichier.iso -Algorithm SHA256` (PowerShell) ou `sha256sum fichier.iso` (Linux).
  Une somme différente = fichier **corrompu ou modifié** : on ne l'utilise pas.

## 10.2 La clé USB

- Clé de **8 Go** au moins ; son contenu sera **effacé** (sauvegarde si besoin).
- Outils : **outil de création** de l'éditeur (Windows), **Rufus** (schéma de partition **GPT**
  pour un PC UEFI), **balenaEtcher**, ou **`dd`** sous Linux (en vérifiant le nom du
  périphérique avec `lsblk`).
- Une clé démarrable en UEFI est en général en **FAT32** : copier à la main une image Windows
  dont un fichier dépasse **4 Gio** échoue (limite de FAT32 vue en PR05) ; les outils ci-dessus
  gèrent ce cas.

{_fig(MEDIA_FIGURE)}

**Procédure professionnelle (à rédiger)** : procédure 2 ci-dessus.

**Erreur fréquente** : utiliser une image d'un site de partage, sauter le contrôle de la somme,
ou écrire l'image avec `dd` sur le mauvais disque.

**À l'écrit** : la **source** de l'image, le **contrôle** et l'**outil**.

**Repère rapide** : **site officiel → SHA-256 identique → clé effacée → test de démarrage**.
Exercices liés : {_ex("E02")}.
"""


def _boot() -> str:
    return f"""**Objectifs** : démarrer sur le média dans le **bon mode** et comprendre la disposition
des partitions créée par l'installateur.

## 11.1 Ordre de démarrage et menu de démarrage

- L'**ordre de démarrage** (*boot order*), réglé dans le firmware, dit quel support essayer en
  premier.
- Le **menu de démarrage** ponctuel (touche indiquée par le fabricant : souvent **F12, F11, F8
  ou Échap**) permet de démarrer **une fois** sur la clé sans changer l'ordre : c'est la
  méthode la plus sûre.
- La même clé peut apparaître **deux fois** : une entrée **« UEFI: »** (démarrage UEFI) et une
  entrée sans préfixe (mode hérité). Pour une installation en **GPT**, on choisit l'entrée
  **« UEFI: »**.

{_fig(BOOT_MENU_FIGURE)}

Ici, on choisit **« {BOOT_UEFI_ENTRY} »** ; « {BOOT_LEGACY_ENTRY} » démarrerait l'installateur en
mode hérité, et l'installateur de Windows refuserait alors un disque GPT.

## 11.2 GPT et partition EFI

En UEFI, l'installateur crée lui-même, sur un disque **GPT**, la **partition EFI (ESP, FAT32)**
qui contient le chargeur de démarrage, puis les partitions du système (plans exacts en
[PR05](/uaa/ampcr-pratique-pr05)). Le technicien **identifie le disque cible** (taille, modèle)
et ne supprime jamais de partition sur un autre disque.

**Procédure professionnelle (à rédiger)** : brancher la clé → menu de démarrage → entrée
« UEFI: » → dans l'installateur, identifier le disque cible → laisser l'installateur créer la
disposition standard.

**Erreur fréquente** : choisir l'entrée sans « UEFI: », puis convertir le disque en MBR pour
« contourner » le refus.

**À l'écrit** : l'**entrée** choisie, le **mode** obtenu et la **table** de partitions qui en
découle.

**Repère rapide** : **menu de démarrage → « UEFI: » → GPT + ESP**. Exercices liés :
{_ex("E13")}.
"""


def _partitions_drivers() -> str:
    return f"""**Objectifs** : prévoir avant l'installation les partitions et les pilotes, pour ne pas
être bloqué au milieu.

## 12.1 Partitions à prévoir

- **Disque entier pour le système** : l'installateur crée la disposition standard (ESP, MSR et
  récupération sous Windows ; ESP, racine et éventuellement swap sous Linux).
- **Partition de données séparée** (D: sous Windows, `/home` sous Linux) : elle permet de
  réinstaller le système **sans toucher** aux données — ce qui ne remplace pas la sauvegarde.
- **Deux systèmes sur un PC (double démarrage)** : on installe d'abord Windows puis Linux, on
  réserve de l'espace non alloué, on sauvegarde la clé BitLocker ; le chargeur de Linux propose
  ensuite le choix au démarrage.

## 12.2 Pilotes à préparer

- **Stockage** : sur certains PC Intel, le SSD est géré par le contrôleur **Intel VMD / Rapid
  Storage Technology** ; l'installateur de Windows n'en a pas le pilote et affiche « Nous n'avons
  trouvé aucun lecteur ». On prépare le pilote « F6 » du fabricant sur une clé et on utilise
  **« Charger un pilote »**.
- **Réseau** : sans pilote Wi-Fi ou Ethernet, pas d'Internet pour les mises à jour et
  l'activation (et, pour l'édition Famille, pour la mise en route) : on garde le pilote sur clé.
- **Chipset et carte graphique** : installés juste après le système, depuis Windows Update ou
  le site du fabricant du PC.
- **Linux** : la plupart des pilotes sont **dans le noyau** ; certains matériels demandent un
  paquet de **firmware** ou un pilote **propriétaire** (cartes NVIDIA), proposé par l'outil
  « Pilotes additionnels » d'Ubuntu.

**Procédure professionnelle (à rédiger)** : relever le modèle exact du PC → télécharger chez le
fabricant les pilotes stockage, réseau, chipset et graphique pour le système visé → les copier
sur une clé → après l'installation, vérifier qu'aucun périphérique n'est inconnu.

**Erreur fréquente** : conclure « disque en panne » quand l'installateur ne voit pas le SSD,
alors que le firmware le voit (pilote de stockage manquant).

**À l'écrit** : **quel pilote**, **où** on l'obtient, **quand** on l'installe.

**Repère rapide** : **stockage et réseau sur clé avant · chipset et graphique juste après ·
Gestionnaire de périphériques sans point d'exclamation**. Exercices liés : {_ex("E01", "E14")}.
"""


def _accounts_security() -> str:
    return f"""**Objectifs** : livrer un système sûr dès sa première utilisation.

## 13.1 Comptes

- **Un compte par personne** : chacun ses fichiers et ses réglages.
- **Compte administrateur** réservé à l'administration (installer, configurer), protégé par un
  mot de passe solide ; **compte standard** pour le travail quotidien. Sous Windows, le
  **Contrôle de compte d'utilisateur (UAC)** demande alors le mot de passe administrateur avant
  une modification du système.
- Sous **Windows 11 Famille**, la mise en route demande une **connexion Internet** et un
  **compte Microsoft** ; dans une entreprise, le poste utilise des **comptes du domaine**.
- Sous **Linux**, l'utilisateur créé pendant l'installation peut administrer avec **`sudo`** ;
  sur Ubuntu, le compte `root` n'a pas de mot de passe utilisable. On crée des comptes standard
  pour les autres utilisateurs.

## 13.2 Protection initiale

- **Mises à jour** installées jusqu'au bout (Windows Update ; `sudo apt update` puis
  `sudo apt upgrade`).
- **Antivirus** actif (Microsoft Defender sous Windows) et **pare-feu** actif (pare-feu Windows ;
  `ufw` sous Ubuntu, à activer).
- **Chiffrement** du disque si le PC sort de l'entreprise ou de la maison (BitLocker ou
  chiffrement de l'appareil, chiffrement proposé par l'installateur de Linux), avec la **clé de
  récupération sauvegardée hors du PC**.
- **Démarrage sécurisé** et **TPM** laissés actifs.

**Procédure professionnelle (à rédiger)** : comptes (administrateur protégé, standard au
quotidien) → mises à jour → antivirus et pare-feu → chiffrement et clé de récupération →
contrôle et rapport.

**Erreur fréquente** : un seul compte administrateur partagé, sans mot de passe « pour aller
plus vite ».

**À l'écrit** : chaque réglage **et** le risque qu'il évite.

**Repère rapide** : **un compte par personne · admin protégé · standard au quotidien · à jour ·
antivirus · pare-feu · chiffrement**. Exercices liés : {_ex("E16")}.
"""


def _virtualisation() -> str:
    left, ok = vm_plan(16, (4, 2))
    return f"""**Objectifs** : expliquer la virtualisation et vérifier qu'un PC peut faire tourner une
machine virtuelle.

## 14.1 Principe

Une **machine virtuelle** (VM) est un PC simulé par un logiciel, l'**hyperviseur** : elle a son
processeur virtuel, sa mémoire, son disque virtuel (un fichier) et son propre système, dit
**invité**. Le système qui fait tourner l'hyperviseur est l'**hôte**. Usages : **tester** un
système ou une installation sans toucher au PC, garder un vieux logiciel, s'entraîner,
regrouper des serveurs.

{_fig(VM_FIGURE)}

## 14.2 Prérequis et réglages

- Extensions de virtualisation du processeur **Intel VT-x** ou **AMD-V** (SVM), **activées
  dans le firmware**.
- **Mémoire** : celle des VM en marche s'ajoute à celle de l'hôte. Règle du cours : laisser au
  moins **{HOST_RESERVE_GIB} Go** à l'hôte. Exemple : PC de 16 Go, VM de 4 Go et de 2 Go →
  {left:g} Go restent à l'hôte ({'acceptable' if ok else 'insuffisant'}).
- **Disque** : place pour le disque virtuel (au moins le stockage minimum du système invité).
- Une VM **Windows 11** doit respecter ses prérequis : firmware **EFI**, **démarrage
  sécurisé**, **TPM virtuel 2.0**.
- Un **instantané** (*snapshot*) fige l'état de la VM pour revenir en arrière après un essai ;
  ce **n'est pas une sauvegarde** des données.

**Procédure professionnelle (à rédiger)** : vérifier VT-x/AMD-V → calculer la mémoire → prévoir
le disque → créer la VM avec l'image officielle → instantané avant les essais.

**Erreur fréquente** : donner à la VM presque toute la mémoire du PC, ou considérer un
instantané comme une sauvegarde.

**À l'écrit** : type d'hyperviseur, **calcul de mémoire** posé, réglage du firmware.

**Repère rapide** : **VT-x/AMD-V activé · mémoire hôte + invités · instantané ≠ sauvegarde**.
Exercices liés : {_ex("E15")}.
"""


def _examples() -> str:
    settings = "\n".join(f"   - {s} ;" for s in CASE2_SETTINGS)
    return f"""## Scénario 1 — Choisir le système de trois postes d'un cabinet

**Situation.** Un cabinet d'expertise comptable renouvelle trois postes : (a) le poste d'une
comptable, qui utilise un logiciel fiscal disponible uniquement sous Windows et doit se
connecter au domaine Active Directory du cabinet ; (b) un PC de 2012 (processeur 64 bits
double cœur, 4 Go, disque dur, sans TPM) que le cabinet veut donner à une association pour la
navigation et la bureautique ; (c) le Mac de la graphiste qui prépare les brochures.

**Résolution.**

1. **(a)** Logiciel « Windows uniquement » → Windows ; domaine Active Directory → l'édition
   Famille ne sait pas le rejoindre → **{EDITION_PRO}**, après vérification des prérequis
   (chapitre 7).
2. **(b)** Sans TPM 2.0 et avec un processeur de 2012, Windows 11 est exclu ; Windows 10 n'a
   plus de mises à jour de sécurité. Usage web et bureautique → **distribution Linux à support
   long avec un bureau léger** (par exemple Linux Mint Xfce), gratuite ; un **SSD** à la place
   du disque dur donnera le plus grand gain.
3. **(c)** macOS ne s'installe que sur un Mac, et ses logiciels de mise en page y sont : on
   **garde macOS**, à jour tant que le modèle est pris en charge.

**Conclusion rédigée.** « Poste comptable : Windows 11 Professionnel (logiciel Windows, domaine).
PC donné : distribution Linux LTS légère + SSD (matériel hors prérequis de Windows 11). Mac :
macOS conservé. »

## Scénario 2 — Prérequis de Windows 11 sur un PC réglé en mode hérité

**Situation.** Une PME veut passer à Windows 11 un PC de bureau sous Windows 10, en gardant ses
programmes. Le contrôle de compatibilité échoue. Tu relèves :

{_fig(MSINFO_FIGURE)}

**Résolution.**

1. **Matériel** : processeur 64 bits de la liste, 8 Go, 256 Go, TPM 2.0 prêt → conformes.
2. **Firmware** : « Mode BIOS : Hérité » → le PC démarre en mode de compatibilité (CSM) sur un
   disque **MBR** ; le démarrage sécurisé n'existe pas dans ce mode.
3. **Verdict** : **{CASE2_VERDICT}**. Réglages, dans l'ordre :
{settings}
4. **Ordre impératif** : sauvegarde vérifiée → `mbr2gpt /validate /allowFullOS` →
   `mbr2gpt /convert /allowFullOS` → firmware en UEFI → démarrage sécurisé activé → contrôle
   dans msinfo32 (« UEFI », « Activé ») → mise à niveau.

**Conclusion rédigée.** « PC conforme sur le plan matériel ; démarrage hérité sur disque MBR.
Disque converti en GPT (mbr2gpt) après sauvegarde, firmware basculé en UEFI avec démarrage
sécurisé activé ; contrôle de compatibilité réussi, mise à niveau réalisée. »

## Scénario 3 — Installation propre ou mise à niveau ?

**Situation.** Un indépendant a un PC compatible Windows 11 avec 8 Go de mémoire, sous
Windows 10 **32 bits** ; il voit « 3,20 Go utilisable ». Ses données sont sur le disque C:.
Il voudrait « mettre à niveau en gardant tout ».

**Résolution.**

1. **Sauvegarde** de ses données sur un disque externe, copie vérifiée, accord écrit.
2. **Prérequis** : PC compatible.
3. **Même famille et architecture ?** Non : Windows 11 n'existe qu'en 64 bits ; il n'y a pas de
   mise à niveau de 32 à 64 bits → **{install_type(backup_ok=True, requirements_ok=True,
   same_family_and_arch=False, system_healthy=True, keep_programs=True)}**.
4. **Licences** : même édition que la licence actuelle ; logiciels et leurs clés relevés, pour
   les réinstaller en version 64 bits.
5. **Après** : les 8 Go sont utilisables (un système 64 bits n'a plus la limite de 4 Gio).

**Conclusion rédigée.** « Passage de Windows 10 32 bits à Windows 11 64 bits par installation
propre (aucune mise à niveau entre architectures) ; données sauvegardées et restaurées,
logiciels réinstallés ; 8 Go de mémoire désormais utilisables. »

## Scénario 4 — Plan d'installation d'un poste Linux pour une association

**Situation.** Une association reçoit un portable UEFI récent (SSD NVMe vide, démarrage
sécurisé activé) et veut **Ubuntu** (version à support long) pour deux bénévoles.

**Résolution.**

{_fig(INSTALL_PLAN_FIGURE)}

1. **Sauvegarder** : SSD vide, rien à sauvegarder ; on le constate par écrit.
2. **Licences et pilotes** : Ubuntu est libre, aucune clé ; carte Wi-Fi reconnue par le noyau
   (vérifié en session live).
3. **Média** : image ISO officielle, somme SHA-256 identique, clé écrite en GPT.
4. **Firmware** : démarrage sécurisé **laissé actif** (chargeur signé) ; menu de démarrage :
   entrée **« UEFI: »** de la clé (capture du chapitre 11).
5. **Installer** : disque NVMe entier, partitions GPT et ESP créées par l'installateur,
   chiffrement proposé par l'installateur activé (portable qui sort).
6. **Pilotes** : « Pilotes additionnels » vérifié, aucun matériel inconnu.
7. **Sécuriser** : un compte administrateur (sudo) pour le responsable, deux comptes standard,
   `sudo apt update` puis `sudo apt upgrade`, pare-feu `ufw` activé.
8. **Contrôler et documenter** : Wi-Fi, impression, sessions des bénévoles ; rapport.

**Conclusion rédigée.** « Ubuntu LTS installé en UEFI avec démarrage sécurisé actif, disque
chiffré, comptes séparés (un administrateur, deux standard), mises à jour et pare-feu actifs ;
tests de réseau et d'impression réussis. »
"""


def _pitfalls() -> str:
    return """> **Installer ou mettre à niveau sans sauvegarde vérifiée** ni accord écrit, « parce que
> les données sont sur D: ».

> **Choisir un système sans regarder les logiciels indispensables** du client ni la date de fin
> de support de la version.

> **Installer l'édition Famille** sur un poste qui doit rejoindre un domaine ou utiliser
> BitLocker, ou une autre édition que celle de la licence.

> **Conclure « non compatible »** pour un PC seulement réglé en mode hérité ou dont le TPM
> intégré est désactivé — ou, à l'inverse, **contourner un blocage matériel**.

> **Basculer le firmware en UEFI avant de convertir le disque** MBR en GPT : Windows ne démarre
> plus.

> **Désactiver le démarrage sécurisé ou le TPM « par sécurité »** : c'est l'inverse.

> **Croire qu'une mise à niveau passe de 32 à 64 bits** ou répare un système infecté.

> **Utiliser une image d'un site de partage** ou sauter le contrôle de la somme SHA-256.

> **Démarrer la clé par l'entrée sans « UEFI: »** puis convertir le disque en MBR pour
> « contourner » le refus de l'installateur.

> **Conclure « SSD en panne »** quand l'installateur ne voit aucun disque alors que le firmware
> le voit : il manque le pilote de stockage.

> **Laisser un seul compte administrateur partagé**, sans mot de passe.

> **Donner presque toute la mémoire à une machine virtuelle**, ou prendre un instantané pour une
> sauvegarde.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (plan d'installation, clé
d'installation, vérification des prérequis), classements (parties du système, édition de
Windows, compatibilité Windows 11, installation propre ou mise à niveau), captures à lire
(Informations système, terminal Linux, menu de démarrage), choix d'un système, architecture
32/64 bits, licences, pilote de stockage, virtualisation et plan à corriger. Rédige ta réponse
sur papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée.
Ces mêmes exercices sont proposés dans [S'entraîner](/uaa/{PR07_SLUG}/practice), avec
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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR07_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (fiches, captures fictives).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** Le **bon choix justifié** (système, édition, démarche), la
**lecture correcte** des relevés, l'**ordre** des opérations et les **précautions** (sauvegarde
vérifiée, licence, clé de récupération) — pas la récitation de sigles. Une autre formulation
juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Système d'exploitation** : gère le matériel pour les programmes ; **noyau** (processeur,
  mémoire), **pilotes** (un par matériel), **système de fichiers**, **comptes et droits**,
  **services** (arrière-plan), **interface** GUI ou CLI.
- **Marché** : Windows (éditions, fin de support publiée ; Windows 10 : 14 octobre 2025) ·
  distributions Linux (libres, LTS, bureau GNOME/KDE/Xfce, `apt`) · macOS (Mac uniquement) ·
  ChromeOS / ChromeOS Flex.
- **Choisir** : logiciels indispensables → environnement (domaine) → matériel → durée de support.
- **Éditions** : Famille pour l'usage courant ; **Professionnel** pour domaine, BitLocker, hôte
  Bureau à distance, Hyper-V, gpedit.
- **GUI / CLI** : GUI pour découvrir et montrer ; CLI pour mesurer, documenter, répéter, à
  distance. `systeminfo`, `ipconfig /all`, `Get-Tpm` · `cat /etc/os-release`, `uname -m`,
  `free -h`, `lsblk -f`, `ip a`, `sudo`.
- **Architecture** : 32 bits = 4 Gio au plus ; Windows 11 = 64 bits ; x64 ou ARM64.
- **Firmware** : UEFI + GPT + ESP ; mode hérité (CSM) + MBR ; démarrage sécurisé = UEFI
  seulement ; TPM 2.0 (PTT, fTPM) ; **mbr2gpt avant la bascule en UEFI**.
- **Windows 11** : processeur 64 bits de la liste, 4 Go, 64 Go, UEFI compatible démarrage
  sécurisé, TPM 2.0 ; verdict : tel quel, après réglages, non compatible.
- **Avant d'installer** : accord écrit, sauvegarde vérifiée, licence et édition, logiciels,
  clé BitLocker.
- **Licences** : OEM liée au PC · commerciale transférable · volume par l'organisation · Linux
  libre.
- **Propre ou mise à niveau** : mise à niveau seulement si compatible, même famille et
  architecture, système sain, programmes à garder.
- **Média** : site officiel, SHA-256 identique, clé de 8 Go effacée, GPT pour l'UEFI.
- **Démarrage** : menu de démarrage (F12, F11, F8, Échap) → entrée « UEFI: ».
- **Pilotes** : stockage (Intel VMD/RST, « Charger un pilote ») et réseau sur clé avant ; chipset
  et graphique juste après.
- **Sécurité initiale** : un compte par personne, administrateur protégé, standard au
  quotidien, mises à jour, antivirus, pare-feu, chiffrement + clé hors du PC.
- **Virtualisation** : hyperviseur type 2 (VirtualBox) ou type 1 (Hyper-V, Proxmox) ; VT-x /
  AMD-V ; mémoire hôte ≥ {HOST_RESERVE_GIB} Go ; instantané ≠ sauvegarde.

## Glossaire des termes employés

- **CLI** : interface en ligne de commande (commandes tapées, réponses en texte).
- **CSM (mode hérité)** : mode de compatibilité de l'UEFI qui imite l'ancien BIOS.
- **Démarrage sécurisé (Secure Boot)** : fonction de l'UEFI qui ne lance que des chargeurs
  signés.
- **Distribution** : système Linux complet (noyau, programmes, installateur, gestionnaire de
  paquets).
- **Édition** : variante d'un même système (Windows 11 Famille, Professionnel…).
- **GUI** : interface graphique (fenêtres, menus, souris).
- **Hyperviseur** : logiciel qui fait tourner des machines virtuelles.
- **LTS** : version à support long, mise à jour pendant plusieurs années.
- **Mise à niveau sur place** : remplacement du système qui garde fichiers, programmes et
  réglages.
- **MOK** : clé locale enregistrée pour autoriser un pilote tiers avec le démarrage sécurisé.
- **Noyau** : cœur du système qui gère le processeur, la mémoire et l'accès au matériel.
- **Pilote** : programme qui permet au système de commander un matériel précis.
- **Service** : programme d'arrière-plan lancé avec le système.
- **SHA-256** : somme de contrôle qui permet de vérifier qu'un fichier n'a pas été modifié.
- **TPM** : composant de sécurité qui conserve des clés de chiffrement.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigences AP-08
  « Les différents systèmes d'exploitation actuellement sur le marché » et AP-12 « Interface
  graphique et interface de ligne de commande ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Windows** : documentation Microsoft (configuration requise de Windows 11, liste des
  processeurs compatibles, comparaison des éditions, cycle de vie de Windows 10, MBR2GPT,
  activation et licences numériques, Contrôle d'intégrité du PC, `Get-FileHash`, `Get-Tpm`,
  `Confirm-SecureBootUEFI`).
- **Linux** : documentation Ubuntu (configuration recommandée de la version Desktop,
  vérification de l'image ISO, démarrage sécurisé et MOK, pilotes additionnels, `ufw`) et
  Debian (installation, `apt`, firmware) ; pages de manuel de `uname`, `free`, `lsblk`,
  `mokutil`, `sha256sum`.
- **Firmware** : spécification UEFI (démarrage sécurisé, partition système EFI) ; Trusted
  Computing Group (TPM 2.0).
- **Virtualisation** : documentation VirtualBox (prérequis matériels, machine Windows 11 avec
  EFI, démarrage sécurisé et TPM virtuel) et Microsoft Hyper-V.

Les prérequis et dates sont ceux **publiés en {WRITTEN_AT}** ; ils évoluent avec les versions : la
page officielle de l'éditeur fait foi le jour de l'intervention. Les tableaux, verdicts de
compatibilité, choix d'édition et d'installation, procédures, arbre de décision et piles du
cours sont **produits par programme** depuis des données **vérifiées par des tests
automatiques** ; aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 cite les systèmes du marché (AP-08), l'interface graphique et la ligne de
commande (AP-12) et l'installation complète des systèmes (AP-10, traitée en PR08 et PR09). Sont
des **compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- les prérequis du firmware (UEFI, démarrage sécurisé, TPM) et la conversion `mbr2gpt` ;
- les licences et l'activation, le choix entre installation propre et mise à niveau ;
- la virtualisation ;
- la règle de mémoire laissée à l'hôte ({HOST_RESERVE_GIB} Go) : c'est une **convention du cours**,
  pas une norme.

## Supports fictifs

Les captures, relevés et situations de ce cours sont **fictifs** et reconstitués pour
l'entraînement ; ils ne décrivent aucun client réel. Aucun n'est une question officielle ou
déjà posée par le Jury.
"""


def pr07_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR07 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR07 — 1. Rôle d'un système d'exploitation : noyau, pilotes, fichiers, comptes, services", _role()),
        ("PR07 — 2. Systèmes sur le marché : Windows, distributions Linux, macOS, ChromeOS", _market()),
        ("PR07 — 3. Éditions de Windows et cycle de vie des versions", _editions()),
        ("PR07 — 4. Interface graphique et ligne de commande : les outils du technicien", _gui_cli()),
        ("PR07 — 5. Architecture 32 ou 64 bits, x64 ou ARM, capacité", _architecture()),
        ("PR07 — 6. Firmware : UEFI ou mode hérité, démarrage sécurisé, TPM 2.0", _firmware()),
        ("PR07 — 7. Prérequis selon le système et l'édition : Windows 11 et Linux", _requirements()),
        ("PR07 — 8. Sauvegarde, licences et activation", _backup_licences()),
        ("PR07 — 9. Installation propre ou mise à niveau", _clean_or_upgrade()),
        ("PR07 — 10. Média d'installation : image officielle, somme de contrôle, clé USB", _media()),
        ("PR07 — 11. Démarrer sur le média : menu, ordre de démarrage, GPT et ESP", _boot()),
        ("PR07 — 12. Partitionnement et pilotes à prévoir", _partitions_drivers()),
        ("PR07 — 13. Comptes et sécurité initiale", _accounts_security()),
        ("PR07 — 14. Notions de virtualisation", _virtualisation()),
        ("PR07 — Exemples : quatre scénarios intégralement corrigés", _examples()),
        ("PR07 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR07 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR07 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR07 — Fiche mémo et glossaire", _memo()),
        ("PR07 — Sources et compléments pédagogiques", _sources()),
    ]
