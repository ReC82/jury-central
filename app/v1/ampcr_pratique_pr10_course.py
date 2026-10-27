"""Cours PR10 « Comptes, pilotes, paramètres et commandes » — parcours AMPCR pratique écrite
(ticket #214).

Matière : intégralement celle du ticket #214 (comptes locaux et de domaine, utilisateur et
administrateur, groupes, UAC et sudo, moindre privilège ; installation, mise à jour et
restauration de pilotes, périphérique inconnu, compatibilité ; paramètres du système, gestion des
périphériques, services et démarrage ; commandes Windows ipconfig, ping, tracert, nslookup, sfc,
DISM, tasklist, net user et Linux ip, systemctl, journalctl, lsblk, df, chmod, chown, apt/dnf,
avec syntaxe, rôle, sortie attendue, droits nécessaires et risques ; cinq cas résolus : pilote
absent, droits insuffisants, service arrêté, périphérique USB, configuration réseau), découpée
en blocs titrés (le titre pilote le type de carte, `app.card_kind` : aucun titre de bloc
théorique ne contient « examen », « source », « ressource », « exemple », « exercice »,
« méthode », « piège », « attention », « transfert » ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr10_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr10_bank`. Mise en forme partagée avec les autres cours pratiques.
L'installation des systèmes relève de PR08 et PR09, les messages d'erreur de PR11, le dépannage
réseau de PR24 (publiés, liens) ; les domaines et groupes en réseau (PR22) et la restauration du
système (PR12) ne sont pas publiés à la rédaction : renvoi en texte seulement.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr08_figures import VENDOR_IDS
from app.v1.ampcr_pratique_pr10_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr10_figures import (
    ACCOUNT_FIGURE,
    ACCOUNT_TYPES,
    CASE5_GATEWAY_OK,
    CASE5_NSLOOKUP_OK,
    CASE5_PING_NET,
    CASE5_PING_PRINTER,
    CHECKLIST,
    COMMANDS,
    CUPS_FIGURE,
    DEVICE_ID_FIGURE,
    DEVICE_STATES,
    DEVICE_TREE_FIGURE,
    DRIVER_FIGURE,
    DRIVER_SOURCES,
    IPCONFIG_FIGURE,
    LINUX,
    LINUX_GROUPS,
    NET_USER_FIGURE,
    NETWORK_FIGURE,
    PERM_FIGURE,
    PROCEDURES,
    RIGHTS_MEANING,
    SERVICE_FIGURE,
    SETTINGS_TOOLS,
    USB_VENDOR_IDS,
    WIN_START_TYPES,
    WINDOWS,
    WINDOWS_GROUPS,
    WRITTEN_AT,
    can_access,
    elevation,
    mode_octal,
    mode_string,
    service_fix,
)

PR10_TITLE = "Comptes, pilotes, paramètres et commandes"
PR10_SLUG = "ampcr-pratique-pr10"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr10") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _accounts_table() -> str:
    rows = "\n".join(f"| **{a.name}** | {a.windows} | {a.linux} | {a.rights} | {a.usage} |" for a in ACCOUNT_TYPES)
    return "| Compte | Windows | Linux | Droits | Pour qui, pour quoi |\n|---|---|---|---|---|\n" + rows


def _groups_tables() -> str:
    win = "\n".join(f"| **{g}** | {role} |" for g, role in WINDOWS_GROUPS)
    lin = "\n".join(f"| **{g}** | {role} |" for g, role in LINUX_GROUPS)
    return (
        "| Groupe local Windows | Rôle |\n|---|---|\n" + win
        + "\n\n| Groupe Linux | Rôle |\n|---|---|\n" + lin
    )


def _elevation_table() -> str:
    rows = []
    for label, os_name, is_admin in (
        ("Compte standard", WINDOWS, False), ("Compte administrateur", WINDOWS, True),
        ("Compte standard", LINUX, False), ("Compte administrateur (groupe sudo)", LINUX, True),
    ):
        rows.append(
            f"| {os_name} | {label} | {elevation(os_name, is_admin=is_admin, needs_admin=False)} | "
            f"{elevation(os_name, is_admin=is_admin, needs_admin=True)} |"
        )
    return (
        "| Système | Compte | Action ordinaire | Action d'administration |\n|---|---|---|---|\n"
        + "\n".join(rows)
    )


def _rights_table() -> str:
    rows = "\n".join(f"| **{r}** | {f} | {d} |" for r, f, d in RIGHTS_MEANING)
    return "| Droit | Sur un fichier | Sur un dossier |\n|---|---|---|\n" + rows


def _modes_table() -> str:
    rows = "\n".join(f"| `{octal}` | `{mode_string(octal)}` | {use} |" for octal, use in (
        ("644", "Document : le propriétaire modifie, les autres lisent."),
        ("640", "Document d'un groupe : le groupe lit, les autres rien."),
        ("600", "Fichier privé (clé, mot de passe d'un service)."),
        ("755", "Script ou dossier lisible par tous, modifiable par le propriétaire."),
        ("750", "Dossier d'un groupe : le groupe entre et lit."),
        ("770", "Dossier partagé d'un groupe : le groupe lit et écrit, les autres rien."),
    ))
    return "| chmod | Droits | Usage courant |\n|---|---|---|\n" + rows


def _access_examples() -> str:
    cases = (
        ("anne (propriétaire)", "anne", ("anne",)),
        ("julie (membre de compta)", "julie", ("julie", "compta")),
        ("paul (ni l'un ni l'autre)", "paul", ("paul",)),
    )
    mode = "-rw-r-----"

    def yn(value: bool) -> str:
        return "oui" if value else "non"

    rows = "\n".join(
        f"| {label} | {yn(can_access(user, groups, 'anne', 'compta', mode, 'r'))} | "
        f"{yn(can_access(user, groups, 'anne', 'compta', mode, 'w'))} |"
        for label, user, groups in cases
    )
    return f"| `{mode} anne compta budget.ods` | Lire | Modifier |\n|---|---|---|\n" + rows


def _sources_table() -> str:
    rows = "\n".join(f"| {i} | {src} | {why} |" for i, (src, why) in enumerate(DRIVER_SOURCES, start=1))
    return "| Ordre | Source du pilote | Pourquoi |\n|---|---|---|\n" + rows


def _states_table() -> str:
    rows = "\n".join(f"| {s.shown} | « {s.message} » | {s.meaning} | **{s.action}** |" for s in DEVICE_STATES)
    return (
        "| Ce que l'on voit | État du périphérique | Signification | Première action |\n|---|---|---|---|\n" + rows
    )


def _vendors_table() -> str:
    pci = ", ".join(f"`{code}` {name}" for code, name in VENDOR_IDS.items())
    usb = ", ".join(f"`{code}` {name}" for code, name in USB_VENDOR_IDS.items())
    return f"- **PCI (VEN_)** : {pci}.\n- **USB (VID_)** : {usb}."


def _settings_table() -> str:
    rows = "\n".join(f"| {task} | {win} | {lin} |" for task, win, lin in SETTINGS_TOOLS)
    return "| Tâche | Windows 11 | Linux |\n|---|---|---|\n" + rows


def _start_types_table() -> str:
    rows = "\n".join(f"| **{t}** | {meaning} |" for t, meaning in WIN_START_TYPES)
    return "| Type de démarrage (Windows) | Effet |\n|---|---|\n" + rows


def _service_table() -> str:
    cases = (
        ("enabled, active (running)", "Automatique, En cours d'exécution", True, True, False),
        ("disabled, inactive (dead)", "Désactivé, Arrêté", False, False, False),
        ("disabled, active (running)", "Manuel, démarré à la main", False, True, False),
        ("enabled, inactive (dead)", "Automatique, Arrêté", True, False, False),
        ("failed", "Arrêté avec une erreur (Observateur d'événements)", True, False, True),
    )
    rows = "\n".join(
        f"| `{linux}` | {win} | {service_fix(enabled=e, running=r, failed=f)} |" for linux, win, e, r, f in cases
    )
    return "| systemd | Windows (équivalent) | Action pour un service nécessaire |\n|---|---|---|\n" + rows


def _command_cards(os_name: str, names: tuple[str, ...]) -> str:
    parts = []
    for command in COMMANDS:
        if command.os_name != os_name or command.name not in names:
            continue
        parts.append(
            f"### {command.name}\n\n"
            f"- **Syntaxe** : `{command.syntax}`\n"
            f"- **Rôle** : {command.role}\n"
            f"- **Sortie attendue** : {command.output}\n"
            f"- **Droits nécessaires** : {command.rights}\n"
            f"- **Risques** : {command.risk}"
        )
    return "\n\n".join(parts)


def _checklist_table() -> str:
    rows = "\n".join(f"| **{point}** | `{where}` | {expected} | ☐ |" for point, where, expected in CHECKLIST)
    return "| Point | Commande / outil | Résultat attendu | Fait |\n|---|---|---|---|\n" + rows


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
p. 3). On ne te demande pas de taper des commandes devant le jury, mais de **choisir** la bonne
commande ou le bon outil, d'**expliquer** ce qu'il fait, de **lire** sa sortie, de dire **quels
droits** il demande et **quels risques** il présente, et de **rédiger** l'intervention. Tu dois
savoir :

1. **choisir** le bon **compte** : local ou de **domaine**, **standard** ou **administrateur**,
   avec les bons **groupes**, selon le **moindre privilège** ;
2. **expliquer** l'**UAC** de Windows et **sudo** sous Linux ;
3. **lire** et **corriger** des **permissions** Linux (`chmod`, `chown`) ;
4. **installer**, **mettre à jour** et **restaurer** un **pilote**, identifier un
   **périphérique inconnu** et contrôler la **compatibilité** ;
5. **régler** le système : **paramètres**, **Gestionnaire de périphériques**, **services** et
   **démarrage** ;
6. **utiliser** les commandes Windows `ipconfig`, `ping`, `tracert`, `nslookup`, `sfc`, `DISM`,
   `tasklist`, `net user` et Linux `ip`, `systemctl`, `journalctl`, `lsblk`, `df`, `chmod`,
   `chown`, `apt`/`dnf` : **syntaxe**, **rôle**, **sortie attendue**, **droits**, **risques** ;
7. **contrôler** et **rédiger** le rapport d'intervention.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences officielles travaillées dans ce cours

{_req("AP-05")}
{_req("AP-11")}
{_req("AP-12")}

L'installation des systèmes est vue en [PR08](/uaa/ampcr-pratique-pr08) (Windows) et
[PR09](/uaa/ampcr-pratique-pr09) (Linux) ; l'interface graphique et la ligne de commande sont
présentées en [PR07](/uaa/ampcr-pratique-pr07) ; les messages d'erreur en
[PR11](/uaa/ampcr-pratique-pr11) ; l'adressage IP en [PR20](/uaa/ampcr-pratique-pr20) et le
dépannage réseau complet en [PR24](/uaa/ampcr-pratique-pr24). Les domaines, groupes et comptes
en réseau (PR22) et la restauration du système (PR12) font l'objet de cours suivants du
parcours.

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC10 Windows : administration et commandes essentielles](/uaa/ampcr-mc10),
[MC11 Linux : bases utiles au technicien PC-réseaux](/uaa/ampcr-mc11) et
[MC12 Pilotes, périphériques et logiciels](/uaa/ampcr-mc12). Ce cours-ci est **pratique** :
procédures rédigées, consoles à lire, pannes à résoudre et rapports, comme dans un dossier
d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (ici ou dans « S'entraîner »,
correction après envoi), puis passe le **mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet
« Examen blanc ».

> **Important —** les consoles, fenêtres et situations de ce cours sont des **supports fictifs**
> construits pour s'entraîner, souvent abrégés. Les sorties de **Windows** sont montrées
> **en français**, celles de **Linux en anglais** (système réglé en anglais, ou commande précédée
> de `LANG=C`). Les libellés de Windows 11 et des distributions changent selon les versions
> (rédaction : {WRITTEN_AT}) : la **documentation de l'éditeur fait foi**. Aucun exercice n'est
> une question officielle ni une question déjà posée par le Jury. **Une commande
> d'administration modifie le système : on sait ce qu'elle fait avant de l'exécuter.**
"""


def _accounts() -> str:
    return f"""**Objectifs** : distinguer les types de comptes et les groupes, et créer le compte qui
convient à chaque personne.

## 1.1 Comptes locaux et comptes de domaine

- Un **compte local** n'existe que sur **un** poste : il est créé et vérifié par ce poste
  (ex. `.\\julie` ou `PC-ACCUEIL\\julie`).
- Un **compte de domaine** est créé sur le **contrôleur de domaine** (Active Directory) de
  l'entreprise : le même compte (`ENTREPRISE\\julie`) ouvre tous les postes du domaine, et les
  droits sur les partages et imprimantes sont donnés à ses **groupes**. Les domaines sont
  détaillés dans le cours PR22.
- Sous Windows 11, un **compte Microsoft** (adresse électronique) est un compte local lié à un
  compte en ligne ; il reste standard ou administrateur comme un autre.

{_accounts_table()}

## 1.2 Groupes

Les droits se donnent **à des groupes**, puis on place les comptes dans les groupes.

{_groups_tables()}

{_fig(ACCOUNT_FIGURE)}

## 1.3 Créer et contrôler un compte

- **Windows** : Paramètres → Comptes → Autres utilisateurs ; en ligne de commande (invite
  administrateur) : `net user julie * /add` (le `*` fait **demander** le mot de passe sans
  l'afficher), `net localgroup Administrateurs julie /add` seulement pour un administrateur ;
  contrôle : `net user julie`.
- **Linux** : `sudo adduser julie` (Debian, Ubuntu) ; `sudo usermod -aG sudo julie` seulement
  pour un administrateur (`-a` : **ajouter** sans retirer les autres groupes) ; contrôle :
  `groups julie`, après reconnexion.

{_fig(NET_USER_FIGURE)}

**Procédure professionnelle (à rédiger)** : besoin → type de compte → création → mot de passe
personnel → groupes → contrôle et connexion d'essai.

**Erreur fréquente** : un compte commun pour plusieurs personnes ; un compte administrateur pour
le travail quotidien ; un mot de passe tapé en clair dans `net user nom motdepasse /add`.

**À l'écrit** : la **liste des comptes** (nom, local ou domaine, type, groupes) et la **raison**
de chaque choix.

**Repère rapide** : **un compte par personne · standard par défaut · droits par les groupes**.
Exercices liés : {_ex("E01", "E07", "E09")}.
"""


def _elevation() -> str:
    return f"""**Objectifs** : expliquer comment Windows et Linux protègent les actions
d'administration, et appliquer le moindre privilège.

## 2.1 Le moindre privilège

On donne à chaque compte **les seuls droits nécessaires** à son travail, et **seulement le
temps nécessaire**. Un logiciel malveillant ouvert dans une session standard ne peut pas
modifier le système ; dans une session administrateur, il le peut.

## 2.2 L'UAC (Windows) et sudo (Linux)

- **UAC** (Contrôle de compte d'utilisateur) : même un administrateur travaille avec des droits
  standard ; une action d'administration ouvre une **invite**. Avec un compte **standard**,
  l'invite demande le **nom et le mot de passe d'un administrateur** ; avec un compte
  **administrateur**, un simple **Oui / Non**. On **ne désactive pas** l'UAC.
- **sudo** : exécute **une** commande avec les droits de root, après le mot de passe **de
  l'utilisateur** lui-même, s'il est membre du groupe `sudo` (`wheel` sous Fedora). Sinon :
  « *nom* is not in the sudoers file ». Chaque usage est journalisé à son nom.
- Le compte **Administrateur** intégré de Windows est désactivé par défaut ; **root** est
  verrouillé sous Ubuntu. On ne travaille **jamais** dans ces comptes.

{_elevation_table()}

*Réglages par défaut de l'UAC ; sous Linux, l'administrateur est membre du groupe sudo.*

**Procédure professionnelle (à rédiger)** : identifier si l'action modifie le système → la
faire depuis un compte administrateur nominatif (invite « en tant qu'administrateur » ou
`sudo`) → revenir au compte standard.

**Erreur fréquente** : rendre un employé administrateur « pour éviter les appels » ; désactiver
l'UAC ; partager le mot de passe de l'administrateur ; ouvrir une session root.

**À l'écrit** : **qui** fait l'action, **avec quel compte**, **quelle invite** apparaît, et
**pourquoi** on ne donne pas plus de droits.

**Repère rapide** : **standard → identifiants admin · admin → Oui/Non · sudo → son propre mot
de passe**. Exercices liés : {_ex("E06", "E10", "E17")}.
"""


def _permissions() -> str:
    return f"""**Objectifs** : lire les permissions affichées par `ls -l` et les corriger sans ouvrir
l'accès à tous.

## 3.1 Propriétaire, groupe, autres

Chaque fichier a un **propriétaire**, un **groupe** et trois triplets de droits : propriétaire,
groupe, autres. Linux applique la **première** classe qui correspond à l'utilisateur ; root
passe outre.

{_fig(PERM_FIGURE)}

{_rights_table()}

{_access_examples()}

## 3.2 chmod et chown

- `chmod` change les droits, en chiffres (`chmod 640 budget.ods`) ou en lettres
  (`chmod u+x script.sh`, `chmod g+w dossier`). Le **propriétaire** peut le faire sur ses
  fichiers ; sinon `sudo`.
- `chown` change le propriétaire et le groupe : `sudo chown anne:compta budget.ods` ; `-R`
  agit sur tout un dossier (à manier avec prudence).

{_modes_table()}

`{mode_octal("-rwxr-x---")}` = `rwxr-x---` : on additionne r = 4, w = 2, x = 1 pour chaque
triplet.

**Procédure professionnelle (à rédiger)** : `ls -l` (ou `ls -ld` pour un dossier) et `id
utilisateur` → classe qui s'applique → droit manquant → **le seul** droit manquant donné à la
bonne classe → contrôle par l'utilisateur.

**Erreur fréquente** : `chmod -R 777` (tout le monde lit, modifie et supprime) ; `chown -R` sur
`/etc` ou `/home` ; oublier le `x` d'un dossier.

**À l'écrit** : **lecture** des droits (classe, triplet) → **commande exacte** → **contrôle**.

**Repère rapide** : **r 4 · w 2 · x 1 · propriétaire / groupe / autres · jamais 777**.
Exercices liés : {_ex("E05", "E12", "E17")}.
"""


def _drivers() -> str:
    return f"""**Objectifs** : expliquer le rôle d'un pilote, choisir une source sûre et vérifier la
compatibilité.

## 4.1 Le rôle d'un pilote

Un **pilote** est le logiciel qui permet au système de dialoguer avec un périphérique (carte
réseau, carte graphique, imprimante, scanner). Sans pilote adapté, le périphérique est
**inconnu** ou fonctionne mal. Sous Linux, la plupart des pilotes sont des **modules du noyau**
fournis avec la distribution (`lspci -k` : « Kernel driver in use ») ; quelques-uns sont non
libres (Wi-Fi Broadcom, NVIDIA, voir [PR09](/uaa/ampcr-pratique-pr09)).

## 4.2 Où trouver un pilote fiable

{_sources_table()}

## 4.3 Compatibilité

- **Version du système** : un pilote prévu pour Windows 11 (ou 10) ; Windows 7 ne convient pas.
- **Architecture** : 64 bits (x64) ou ARM64 ; un pilote 32 bits ne s'installe pas sur un
  Windows 64 bits.
- **Modèle exact** : celui de l'étiquette ou de l'**ID du matériel**, pas « à peu près ».
- **Signature** : Windows 64 bits refuse un pilote non signé ; on ne désactive pas ce contrôle.

**Procédure professionnelle (à rédiger)** : modèle exact → système et architecture → source
dans l'ordre du tableau → version notée.

**Erreur fréquente** : un « pack de pilotes » d'un site inconnu ; un pilote 32 bits ou prévu
pour un autre Windows ; désactiver la signature des pilotes.

**À l'écrit** : **périphérique identifié → source choisie → compatibilité vérifiée**.

**Repère rapide** : **Windows Update · fabricant du PC · fabricant du composant · jamais un site
inconnu**. Exercices liés : {_ex("E02", "E11")}.
"""


def _device_manager() -> str:
    return f"""**Objectifs** : lire le Gestionnaire de périphériques, identifier un périphérique
inconnu et choisir la première action.

## 5.1 États et codes d'erreur

Le **Gestionnaire de périphériques** (clic droit sur Démarrer, ou `devmgmt.msc`) liste le
matériel par catégorie. Propriétés → Général → **État du périphérique** donne un message et un
**code**.

{_states_table()}

## 5.2 Identifier un périphérique inconnu

Propriétés → **Détails** → **ID du matériel** : `PCI\\VEN_xxxx&DEV_yyyy` (carte interne) ou
`USB\\VID_xxxx&PID_yyyy` (périphérique USB). **VEN / VID** = fabricant, **DEV / PID** = modèle.
Sous Linux, `lspci -nn` et `lsusb` affichent les mêmes identifiants (`14e4:43a0`).

{_vendors_table()}

*Identifiants publiés par le PCI-SIG et l'USB-IF ; liste réduite aux fabricants du cours.*

{_fig(DEVICE_TREE_FIGURE)}

**Procédure professionnelle (à rédiger)** : catégorie et icône → état et code → ID du matériel
→ fabricant et modèle → première action.

**Erreur fréquente** : installer « un pilote qui ressemble » sans lire l'ID du matériel ;
conclure à une panne pour un périphérique simplement désactivé.

**À l'écrit** : **ce que l'on voit → code → signification → action**.

**Repère rapide** : **Code 28 pilote · 22 désactivé · 10 ne démarre pas · 43 matériel**.
Exercices liés : {_ex("E08", "E11")}.
"""


def _driver_operations() -> str:
    return f"""**Objectifs** : installer, mettre à jour et restaurer un pilote en gardant un retour
arrière.

## 6.1 Les quatre gestes du Gestionnaire de périphériques

- **Mettre à jour le pilote** : recherche automatique, ou pilote téléchargé (« Parcourir mon
  ordinateur »).
- **Restaurer le pilote** (Propriétés → Pilote) : revient à la version précédente, si Windows
  l'a conservée ; sinon le bouton est grisé.
- **Désactiver** / **Activer le périphérique**.
- **Désinstaller l'appareil** (option « Tenter de supprimer le pilote de ce périphérique »),
  puis « Rechercher les modifications sur le matériel ».

{_fig(DRIVER_FIGURE)}

## 6.2 Sous Linux

Les pilotes viennent avec le noyau et les mises à jour (`sudo apt upgrade`) ; « Pilotes
additionnels » (Ubuntu) propose les pilotes non libres ; contrôle : `lspci -k`, `lsusb`.
Après une mise à jour du noyau qui pose problème, on démarre l'ancien noyau depuis le menu GRUB
(« Options avancées »).

**Procédure professionnelle (à rédiger)** : point de restauration → installer / mettre à jour /
restaurer → redémarrer si demandé → état « Ce périphérique fonctionne correctement » → essai
réel → version notée.

**Erreur fréquente** : mettre à jour tous les pilotes « par principe » sur un poste qui
fonctionne ; aucun point de restauration ; réinstaller Windows pour un pilote.

**À l'écrit** : **geste choisi → raison → contrôle**.

**Repère rapide** : **point de restauration · restaurer après une mauvaise mise à jour ·
contrôler**. Exercices liés : {_ex("E02", "E08")}.
"""


def _settings() -> str:
    return f"""**Objectifs** : retrouver l'outil adapté à chaque réglage du système, sous Windows et
sous Linux.

## 7.1 Où régler quoi

{_settings_table()}

*Libellés de Windows 11 en {WRITTEN_AT} ; lusrmgr.msc n'existe pas dans l'édition Famille.*

## 7.2 Programmes lancés au démarrage

- **Windows** : Paramètres → Applications → Démarrage, ou Gestionnaire des tâches →
  Applications de démarrage : on **désactive** une application inutile (le programme reste
  installé). msconfig sert au dépannage (démarrage sélectif).
- **Linux** : applications au démarrage du bureau ; services : `systemctl list-unit-files
  --state=enabled`.

**Procédure professionnelle (à rédiger)** : réglage demandé → outil → valeur avant → valeur
après → contrôle → noté dans le rapport.

**Erreur fréquente** : modifier un réglage sans noter la valeur d'origine ; un logiciel
d'« optimisation » qui change tout d'un coup.

**À l'écrit** : **réglage → outil → chemin → contrôle**.

**Repère rapide** : **Paramètres · Gestionnaire de périphériques · Services · Observateur
d'événements**. Exercices liés : {_ex("E03", "E13")}.
"""


def _services() -> str:
    return f"""**Objectifs** : lire l'état d'un service, comprendre son type de démarrage et le
remettre en route.

## 8.1 Services sous Windows

Un **service** est un programme qui tourne en arrière-plan (Spouleur d'impression, Windows
Update, Client DHCP). Console **Services** (`services.msc`) : **État** (En cours d'exécution,
Arrêté) et **Type de démarrage** :

{_start_types_table()}

## 8.2 Services sous Linux (systemd)

- `systemctl status cups` : **enabled / disabled** (lancé au démarrage ou non) et **active
  (running) / inactive (dead) / failed**.
- `sudo systemctl start | stop | restart cups` ; `sudo systemctl enable --now cups` (activer
  au démarrage **et** démarrer) ; `systemctl --failed` : services en échec.
- `journalctl -u cups -b` : messages du service depuis le démarrage.

{_service_table()}

{_fig(SERVICE_FIGURE)}

{_fig(CUPS_FIGURE)}

**Procédure professionnelle (à rédiger)** : service concerné → état et type de démarrage →
**cause** (journal) → correction → démarrage → contrôle, y compris après un redémarrage.

**Erreur fréquente** : redémarrer le service sans lire le journal ; désactiver des services
« inconnus » ; arrêter `ssh` ou le réseau d'une machine à distance.

**À l'écrit** : **état relevé → interprétation → commande → contrôle**.

**Repère rapide** : **activé ≠ démarré · lire le journal · enable --now**. Exercices liés :
{_ex("E03", "E13")}.
"""


def _windows_network_commands() -> str:
    return f"""**Objectifs** : utiliser les commandes réseau de Windows et de Linux, lire leur sortie
et connaître leurs droits et risques.

## 9.1 Commandes réseau de Windows

{_command_cards(WINDOWS, ("ipconfig", "ping", "tracert", "nslookup"))}

## 9.2 La commande ip sous Linux

{_command_cards(LINUX, ("ip",))}

{_fig(NETWORK_FIGURE)}

*L'adressage (masque, passerelle, DHCP) est détaillé en [PR20](/uaa/ampcr-pratique-pr20), le
dépannage réseau complet en [PR24](/uaa/ampcr-pratique-pr24).*

**Procédure professionnelle (à rédiger)** : configuration → passerelle → adresse Internet →
nom → correction → contrôle.

**Erreur fréquente** : `ipconfig /release` lancé à distance ; conclure « Internet en panne »
sans tester la passerelle puis un nom.

**À l'écrit** : **commande → ce qu'elle a montré → conclusion → étape suivante**.

**Repère rapide** : **ipconfig · ping passerelle · ping Internet · nslookup · tracert**.
Exercices liés : {_ex("E04", "E15")}.
"""


def _windows_system_commands() -> str:
    return f"""**Objectifs** : utiliser les commandes système de Windows en connaissant les droits
qu'elles demandent.

## 10.1 Commandes système de Windows

Pour **ouvrir une invite en administrateur** : Démarrer → taper « cmd » ou « Terminal » →
« Exécuter en tant qu'administrateur » ; l'UAC s'affiche. Le titre de la fenêtre commence alors
par « Administrateur : ».

{_command_cards(WINDOWS, ("sfc", "DISM", "tasklist", "net user"))}

## 10.2 L'ordre DISM puis SFC

SFC remplace les fichiers abîmés par ceux du **magasin de composants**. Si SFC « n'a pas pu tous
les réparer », le magasin est lui-même abîmé : on lance `DISM /Online /Cleanup-Image
/RestoreHealth` (connexion Internet), on redémarre, puis on relance `sfc /scannow`. Les messages
de Windows sont analysés en [PR11](/uaa/ampcr-pratique-pr11).

**Procédure professionnelle (à rédiger)** : sauvegarde vérifiée → invite en administrateur →
commande → lecture du résultat → étape suivante → contrôle du symptôme.

**Erreur fréquente** : lancer `sfc` dans une invite standard et conclure « rien trouvé » ;
interrompre DISM ; arrêter un processus inconnu avec taskkill.

**À l'écrit** : **commande exacte + droits + résultat attendu**.

**Repère rapide** : **invite admin · DISM puis SFC · tasklist pour voir · net user pour
contrôler**. Exercices liés : {_ex("E04", "E09", "E16")}.
"""


def _linux_commands() -> str:
    return f"""**Objectifs** : utiliser les commandes de base de Linux, lire leur sortie et
connaître leurs droits et risques.

## 11.1 Commandes de base de Linux

{_command_cards(LINUX, ("systemctl", "journalctl", "lsblk", "df", "chmod", "chown", "apt / dnf"))}

## 11.2 Lire avant d'agir

Les commandes de **lecture** (`systemctl status`, `journalctl`, `lsblk`, `df`, `ip a`,
`ls -l`) s'utilisent sans risque et souvent sans sudo. Les commandes qui **modifient** (start,
stop, enable, chmod, chown, apt install) demandent sudo ou la propriété du fichier : on les
écrit dans le rapport avec leur raison.

**Procédure professionnelle (à rédiger)** : lecture (état, journal, disque) → cause → commande
de correction exacte → contrôle.

**Erreur fréquente** : `sudo` devant toutes les commandes « au cas où » ; `apt upgrade` sans
`apt update` ; supprimer des fichiers pour faire de la place sans `df` ni `du`.

**À l'écrit** : **commande → sortie relevée → interprétation → correction**.

**Repère rapide** : **status · journalctl -u · lsblk -f · df -h · chmod/chown · apt update puis
upgrade**. Exercices liés : {_ex("E05", "E13", "E14")}.
"""


def _checklist_report() -> str:
    return f"""**Objectifs** : valider l'intervention et laisser une trace écrite complète.

## 12.1 Liste de contrôle

{_checklist_table()}

## 12.2 Rapport d'intervention

1. **Demande** : client, date, besoin, accord.
2. **Constat** : symptôme, message exact, commandes de lecture et leur sortie.
3. **Actions** : comptes créés ou modifiés, pilote (version, source), service, réglage, commande
   exacte.
4. **Contrôles** : liste ci-dessus et résultats.
5. **Recommandations** : comptes standard, mises à jour, sauvegarde ; signatures.

Le rapport ne contient **jamais de mot de passe**.

**Procédure professionnelle (à rédiger)** : passer la liste avec le client → reporter chaque
résultat → rapport en rubriques.

**Erreur fréquente** : rapport réduit à « pilote installé » ; mot de passe écrit dans le
rapport.

**À l'écrit** : la **liste** (point — commande — résultat) et le **rapport en rubriques**.

**Repère rapide** : **constat · actions · contrôles · recommandations · pas de mot de passe**.
Exercices liés : {_ex("E17")}.
"""


def _examples() -> str:
    return f"""## Cas 1 — Pilote absent : pas de Wi-Fi après la réinstallation

**Situation.** Après la réinstallation de Windows 11 sur un ancien portable, aucun réseau Wi-Fi
n'est proposé. Le câble réseau fonctionne.

{_fig(DEVICE_ID_FIGURE)}

**Résolution.**

1. **Lecture** : « Contrôleur de réseau » sous Autres périphériques, **Code 28** : aucun pilote.
2. **Identification** : `PCI\\VEN_14E4&DEV_43A0` → fabricant **Broadcom**, puce BCM4360.
3. **Source** : par le câble, Windows Update → Mises à jour facultatives → pilotes ; à défaut,
   site du fabricant du portable, modèle exact, Windows 11 64 bits.
4. **Point de restauration**, installation, redémarrage.
5. **Contrôle** : « Ce périphérique fonctionne correctement », réseaux visibles, connexion.

**Conclusion rédigée.** « Wi-Fi absent : carte Broadcom sans pilote (Code 28) ; pilote installé
par Windows Update après point de restauration ; Wi-Fi fonctionnel. »

## Cas 2 — Droits insuffisants : ajouter une imprimante sous Ubuntu

**Situation.** Nadia, comptable avec un compte standard sur Ubuntu, doit pouvoir ajouter et
régler les imprimantes du bureau. Paramètres → Imprimantes (ou l'interface web de CUPS,
`http://localhost:631`) lui demande un mot de passe d'administrateur qu'elle n'a pas.

{_console(
    "$ groups nadia",
    "nadia : nadia",
    "$ sudo usermod -aG lpadmin nadia",
    "$ groups nadia",
    "nadia : nadia lpadmin",
)}

**Résolution.**

1. **Besoin précis** : gérer les imprimantes, **pas** administrer tout le poste.
2. **Moindre privilège** : groupe **`lpadmin`** (gestion des imprimantes), **pas** `sudo`.
3. **Commande** (compte administrateur) : `sudo usermod -aG lpadmin nadia` ; reconnexion de
   Nadia.
4. **Contrôle** : `groups nadia` affiche `lpadmin` ; Nadia ajoute l'imprimante et imprime une
   page de test.

**Conclusion rédigée.** « Nadia ajoutée au groupe lpadmin (gestion des imprimantes) ; elle gère
les imprimantes sans être administratrice du poste. »

## Cas 3 — Service arrêté : le spouleur d'impression s'arrête tout seul

**Situation.** Sur un PC Windows 11, l'impression échoue ; dans `services.msc`, le **Spouleur
d'impression** est **Arrêté** alors que son type est **Automatique**. Démarré à la main, il
s'arrête dès qu'on imprime.

**Résolution.**

1. **Cause** : Observateur d'événements → Journaux Windows → Système : le service s'est arrêté
   de façon inattendue ; un document bloqué dans la file est en cause.
2. **Correction** (invite en administrateur) : `net stop spooler` ; supprimer le contenu de
   `C:\\Windows\\System32\\spool\\PRINTERS` (les travaux en attente, pas le dossier) ;
   `net start spooler`.
3. **Contrôle** : service **En cours d'exécution**, `tasklist /fi "imagename eq spoolsv.exe"`
   trouve le processus, page de test imprimée, toujours actif après un redémarrage.

**Conclusion rédigée.** « Spouleur arrêté par un travail bloqué ; file vidée, service
redémarré ; impression rétablie et contrôlée après redémarrage. »

## Cas 4 — Périphérique USB : un disque externe invisible sous Linux

**Situation.** Le disque externe USB d'un client n'apparaît pas sur son PC Ubuntu, branché sur
le hub USB non alimenté de l'écran.

{_console(
    "$ lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS",
    "NAME          SIZE FSTYPE MOUNTPOINTS",
    "nvme0n1     476.9G",
    "├─nvme0n1p1     1G vfat   /boot/efi",
    "└─nvme0n1p2 475.9G ext4   /",
    "$ # disque rebranché directement sur un port du PC",
    "$ lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS /dev/sda",
    "NAME   SIZE FSTYPE MOUNTPOINTS",
    "sda    1.8T",
    "└─sda1 1.8T exfat  /media/luc/Sauvegarde",
)}

**Résolution.**

1. **Lecture** : premier `lsblk`, aucun disque `sd…` : le système ne voit pas le disque. Ce
   n'est pas un problème de pilote ni de système de fichiers.
2. **Matériel d'abord** : le disque 2,5 pouces tire son courant du port USB ; un hub non
   alimenté ne suffit pas. Branchement **direct** sur un port du PC (autre câble si besoin).
3. **Contrôle** : `lsblk` montre `sda` et `sda1` (exFAT) monté sur `/media/luc/Sauvegarde` ;
   `df -h` affiche son espace ; les fichiers s'ouvrent.

**Conclusion rédigée.** « Disque externe non détecté via un hub non alimenté ; branché
directement, il est reconnu et monté ; aucune donnée touchée. »

## Cas 5 — Configuration réseau : une passerelle mal saisie

**Situation.** Le poste de l'accueil, configuré à la main, imprime sur l'imprimante réseau
(192.168.1.40) mais n'ouvre aucun site. La box du client est {CASE5_GATEWAY_OK}.

{_fig(IPCONFIG_FIGURE)}

**Résolution.**

1. **Lecture** : adresse fixe (DHCP : Non), adresse et masque cohérents ; passerelle
   **192.168.1.254**, qui ne répond pas ; l'imprimante répond (le réseau local fonctionne) :

{_console(*CASE5_PING_PRINTER)}

2. **Cause** : passerelle mal saisie : le poste n'atteint rien hors du réseau local.
3. **Correction** : Paramètres → Réseau et Internet → Ethernet → Attribution IP → passerelle
   **{CASE5_GATEWAY_OK}** (ou retour en DHCP).
4. **Contrôle** :

{_console(*CASE5_PING_NET, "", *CASE5_NSLOOKUP_OK)}

**Conclusion rédigée.** « Passerelle mal saisie (192.168.1.254 au lieu de {CASE5_GATEWAY_OK}) ;
corrigée ; Internet joignable, nom résolu, site ouvert. »
"""


def _pitfalls() -> str:
    return """> **Un compte commun** pour plusieurs personnes, ou un compte administrateur sans mot de
> passe.

> **Rendre un employé administrateur** « pour éviter les appels » ; **désactiver l'UAC**.

> **Taper un mot de passe en clair** dans `net user nom motdepasse /add`.

> **`chmod -R 777`** pour « régler les droits » ; **`chown -R`** sur `/etc` ou `/home`.

> **Télécharger un pilote** sur un site inconnu ou un « pack de pilotes » ; un pilote d'une
> autre version de Windows ou d'une autre architecture.

> **Mettre à jour un pilote sans point de restauration**, ou réinstaller Windows pour un pilote.

> **Démarrer un service sans lire le journal** ; **désactiver des services inconnus**.

> **Lancer `sfc` dans une invite standard** et conclure « rien trouvé ».

> **`ipconfig /release` ou `systemctl stop ssh` à distance** : on perd la main.

> **Conclure « Internet en panne »** sans tester la passerelle, une adresse puis un nom.

> **`sudo` devant tout** « au cas où » ; **`apt upgrade` sans `apt update`**.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (compte, pilote, service),
classements (commandes Windows, commandes Linux, droits nécessaires, compte selon le besoin,
état d'un périphérique), consoles et fenêtres à lire (net user, UAC, ID du matériel,
permissions, systemctl, lsblk et df, ipconfig, ping et nslookup, sfc), procédure à corriger.
Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et
justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR10_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR10_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (consoles et fenêtres fictives).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** La **lecture correcte** des relevés, la **cause** identifiée, la
**commande exacte**, les **droits** nécessaires, les **risques** et le **contrôle** — pas la
récitation de sigles. Une autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Comptes** : un par personne ; **standard** par défaut ; **administrateur nominatif** pour
  qui administre ; **domaine** quand il y a un contrôleur ; droits par les **groupes**.
- **Créer** : `net user nom * /add` (invite admin) · `sudo adduser nom` ; **contrôler** :
  `net user nom` · `groups nom`.
- **UAC** : standard → identifiants d'un administrateur ; administrateur → Oui / Non ; ne
  jamais la désactiver. **sudo** : son propre mot de passe, groupe `sudo` (`wheel`).
- **Permissions** : propriétaire / groupe / autres ; r 4, w 2, x 1 ; `chmod 640`, `chmod u+x`,
  `sudo chown anne:compta` ; **jamais 777**.
- **Pilotes** : ID du matériel (VEN/DEV, VID/PID) → Windows Update ou fabricant → modèle,
  version de Windows, 64 bits → point de restauration → contrôle.
- **Codes** : 28 pilote absent · 22 désactivé · 10 ne démarre pas · 43 matériel ;
  **Restaurer le pilote** après une mauvaise mise à jour.
- **Services** : `services.msc` (État, Type de démarrage) · `systemctl status`, `sudo systemctl
  enable --now`, `journalctl -u … -b` ; activé ≠ démarré.
- **Réseau** : `ipconfig /all` · `ping` passerelle, adresse, nom · `tracert -d` · `nslookup` ·
  `ip a`, `ip route`.
- **Système Windows** : invite admin ; `DISM /Online /Cleanup-Image /RestoreHealth` puis
  `sfc /scannow` ; `tasklist` ; `net user`.
- **Linux** : `lsblk -f` · `df -h` · `apt update` puis `apt upgrade` · `dnf upgrade`.
- **Risques** : `/release` ou `stop ssh` à distance ; `-R` sur un dossier système ; mot de
  passe en clair.

## Glossaire des termes employés

- **Compte de domaine** : compte créé sur le contrôleur de domaine, valable sur tous les postes
  du domaine.
- **Compte local** : compte qui n'existe que sur un poste.
- **Groupe** : ensemble de comptes auxquels on donne des droits en une fois.
- **ID du matériel** : identifiant d'un périphérique (fabricant et modèle), lu dans les
  propriétés du périphérique.
- **Magasin de composants** : copie de référence des fichiers de Windows, réparée par DISM et
  utilisée par SFC.
- **Moindre privilège** : principe qui donne à chaque compte les seuls droits dont il a besoin.
- **Pilote** : logiciel qui permet au système d'utiliser un périphérique.
- **Point de restauration** : état enregistré des fichiers système et des pilotes de Windows,
  pour revenir en arrière.
- **Service** : programme qui tourne en arrière-plan, géré par le système.
- **sudo** : exécution d'une commande avec les droits d'administration, au nom de l'utilisateur.
- **UAC** : Contrôle de compte d'utilisateur, l'invite de Windows avant une action
  d'administration.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigences AP-05
  « Les périphériques d'entrée et de sortie et le rôle d'un pilote », AP-11 « Paramètres et
  commandes de base des systèmes d'exploitation courants » et AP-12 « Interface graphique et
  interface de ligne de commande ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Windows** : documentation Microsoft (comptes d'utilisateurs et Contrôle de compte
  d'utilisateur, codes d'erreur du Gestionnaire de périphériques, restauration d'un pilote,
  services, commandes `ipconfig`, `ping`, `tracert`, `nslookup`, `sfc`, `DISM`, `tasklist`,
  `net user`, `net localgroup`).
- **Linux** : pages de manuel de `ip`, `systemctl`, `journalctl`, `lsblk`, `df`, `chmod`,
  `chown`, `adduser`, `usermod`, `groups`, `sudo`, `apt`, `dnf` ; documentation d'Ubuntu et de
  Debian (groupes `sudo`, `adm`, `lpadmin`, `dialout`) et de Fedora (`wheel`).
- **Identifiants matériels** : listes publiques des Vendor ID du PCI-SIG et de l'USB-IF.

Les libellés de Windows 11 et des distributions sont ceux de {WRITTEN_AT} ; ils changent avec
les versions : la documentation de l'éditeur fait foi le jour de l'intervention. Les
procédures, tableaux de comptes et de droits, permissions, états des périphériques, actions sur
les services, fiches de commandes, l'arbre de décision et les relevés du cours sont **produits
par programme** depuis des données **vérifiées par des tests automatiques** ; aucun schéma
n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 cite les périphériques et le rôle d'un pilote (AP-05), les paramètres et
commandes de base (AP-11) et l'interface graphique et la ligne de commande (AP-12). Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- les comptes de domaine (détaillés en PR22) et le principe du moindre privilège ;
- les permissions Linux détaillées et les codes d'erreur du Gestionnaire de périphériques ;
- le tableau des sources de pilotes, l'ordre des tests réseau, les actions sur les services et
  la liste de contrôle : ce sont des **conventions du cours**, pas une norme.

## Supports fictifs

Les consoles, fenêtres et situations de ce cours sont **fictives** et reconstituées pour
l'entraînement, parfois abrégées ; elles ne décrivent aucun client réel. Les adresses publiques
viennent des plages de documentation de la RFC 5737. Aucune n'est une question officielle ou
déjà posée par le Jury.
"""


def pr10_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR10 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR10 — 1. Comptes locaux et de domaine, utilisateurs et groupes", _accounts()),
        ("PR10 — 2. UAC, sudo et moindre privilège", _elevation()),
        ("PR10 — 3. Permissions Linux : chmod et chown", _permissions()),
        ("PR10 — 4. Pilotes : rôle, provenance et compatibilité", _drivers()),
        ("PR10 — 5. Gestionnaire de périphériques et périphérique inconnu", _device_manager()),
        ("PR10 — 6. Installer, mettre à jour et restaurer un pilote", _driver_operations()),
        ("PR10 — 7. Paramètres du système et programmes au démarrage", _settings()),
        ("PR10 — 8. Services Windows et systemd", _services()),
        ("PR10 — 9. Commandes réseau : ipconfig, ping, tracert, nslookup et ip", _windows_network_commands()),
        ("PR10 — 10. Commandes Windows : sfc, DISM, tasklist et net user", _windows_system_commands()),
        ("PR10 — 11. Commandes Linux : systemctl, journalctl, lsblk, df, chmod, chown, apt", _linux_commands()),
        ("PR10 — 12. Liste de contrôle et rapport d'intervention", _checklist_report()),
        ("PR10 — Exemples : cinq cas résolus", _examples()),
        ("PR10 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR10 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR10 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR10 — Fiche mémo et glossaire", _memo()),
        ("PR10 — Sources et compléments pédagogiques", _sources()),
    ]
