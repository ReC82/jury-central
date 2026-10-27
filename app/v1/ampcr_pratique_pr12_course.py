"""Cours PR12 « Dépannage logiciel et restauration du système » — parcours AMPCR pratique écrite
(ticket #215).

Matière : intégralement celle du ticket #215 (distinguer système, application, pilote, compte,
service, logiciel malveillant et stockage ; recueillir symptômes, journaux, reproductibilité et
changements ; Windows : démarrage avancé et WinRE, point de restauration, SFC et DISM, pilotes,
mises à jour, profil corrompu ; Linux : systemd, journalctl, GRUB, permissions, paquets,
système de fichiers et espace disque ; sauvegarde préalable, restauration et vérification
d'intégrité ; précautions contre la perte de données et autorisation avant réinstallation ;
diagnostic réseau logiciel ou physique ; cinq cas résolus : démarrage, service, profil, mise à
jour, espace disque), découpée en blocs titrés (le titre pilote le type de carte,
`app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention », « transfert »
ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr12_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr12_bank`. Mise en forme partagée avec les autres cours pratiques.
Les messages d'erreur (écrans bleus, BCD, GRUB rescue, fstab) relèvent de PR11, les commandes
de base de PR10, le stockage de PR05, le dépannage réseau complet de PR24 (publiés, liens) ;
l'outillage et la protection des données (PR28) ne sont pas publiés à la rédaction : renvoi en
texte seulement.
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr12_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr12_figures import (
    BACKUP_FIGURE,
    BOOT_FIGURE,
    CASE5_DF_AFTER,
    CASE5_FREED,
    CASE5_USED_AFTER,
    CASE5_USED_BEFORE,
    CAUSES,
    CHECKLIST,
    DISK_FIGURE,
    FACTS,
    HASH_COMMANDS,
    ISOLATION_FIGURE,
    LADDER,
    LADDER_FIGURE,
    LINUX_FIXES,
    LINUX_SERVICE_FIGURE,
    LOGS,
    METHOD_FIGURE,
    NETWORK_FIGURE,
    NGINX_FIGURE,
    PROCEDURES,
    PROFILE_FIGURE,
    PROFILE_STEPS,
    RESTORE_FIGURE,
    UPDATE_CASE_KB,
    UPDATE_CASE_ROWS,
    WINRE_TOOLS,
    WRITTEN_AT,
    effect_of,
    precaution_for,
    sha256_hex,
)

PR12_TITLE = "Dépannage logiciel et restauration du système"
PR12_SLUG = "ampcr-pratique-pr12"


def _exercises_html() -> str:
    return "\n\n".join(
        _exercise_card(i, item, anchor_prefix="pr12") for i, item in enumerate(PRACTICE_ITEMS, start=1)
    )


def _console(*lines: str) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _ex(*keys: str) -> str:
    """Renvoi texte vers les exercices corrigés liés à un chapitre (séquence « Exercices
    corrigés ») : pas de lien d'ancre, la page n'affiche qu'une séquence à la fois."""
    return ", ".join(f"**{key}**" for key in keys) + " (séquence « Exercices corrigés »)"


# --- Tableaux de données (générés depuis les données vérifiées) ------------------------------


def _causes_table() -> str:
    rows = "\n".join(f"| **{c.name}** | {c.signs} | {c.test} | {c.first_action} |" for c in CAUSES)
    return "| Famille | Signes typiques | Ce qui la confirme | Première piste |\n|---|---|---|---|\n" + rows


def _facts_table() -> str:
    rows = "\n".join(f"| **{fact}** | {question} |" for fact, question in FACTS)
    return "| Fait à recueillir | Question ou geste |\n|---|---|\n" + rows


def _logs_table() -> str:
    rows = "\n".join(f"| {system} | {tool} | {what} |" for system, tool, what in LOGS)
    return "| Système | Outil ou commande | Ce qu'on y lit |\n|---|---|---|\n" + rows


def _ladder_table() -> str:
    def yn(value: bool) -> str:
        return "conservés" if value else "**retirés**"

    rows = "\n".join(
        f"| {i} | **{s.name}** | {s.detail} | {'conservés' if s.keeps_files else '**effacés**'} | "
        f"{yn(s.keeps_programs)} | {precaution_for(s)} |"
        for i, s in enumerate(LADDER, start=1)
    )
    return (
        "| Marche | Intervention | Comment | Fichiers | Programmes | Précaution minimale |\n"
        "|---|---|---|---|---|---|\n" + rows
    )


def _winre_table() -> str:
    rows = "\n".join(f"| **{tool}** | {role} | {effect} |" for tool, role, effect in WINRE_TOOLS)
    return "| Outil du démarrage avancé | Rôle | Effet sur les données |\n|---|---|---|\n" + rows


def _hash_table() -> str:
    rows = "\n".join(f"| {system} | `{command}` |" for system, command in HASH_COMMANDS)
    return "| Système | Calculer une empreinte SHA-256 |\n|---|---|\n" + rows


def _linux_fixes_table() -> str:
    rows = "\n".join(f"| {need} | `{command}` |" for need, command in LINUX_FIXES)
    return "| Besoin | Commande |\n|---|---|\n" + rows


def _profile_steps() -> str:
    return "\n".join(f"{i}. **{label}** : {detail}" for i, (label, detail) in enumerate(PROFILE_STEPS, start=1))


def _checklist_table() -> str:
    rows = "\n".join(f"| **{point}** | `{where}` | {expected} | ☐ |" for point, where, expected in CHECKLIST)
    return "| Point | Commande / outil | Résultat attendu | Fait |\n|---|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(
        f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1)
    )


_HASH_DEMO_A = b"Bonjour"
_HASH_DEMO_B = b"bonjour"

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant une panne logicielle décrite dans un dossier, on attend de toi un **diagnostic
justifié** et une **intervention rédigée** qui ne fait **rien perdre** au client. Tu dois
savoir :

1. **situer** la cause : système, application, pilote, compte, service, logiciel malveillant ou
   stockage ;
2. **recueillir** les faits : symptômes, journaux, reproductibilité, changements récents ;
3. **réparer Windows** : démarrage avancé et WinRE, mode sans échec, point de restauration,
   SFC et DISM, pilotes, mises à jour, profil corrompu ;
4. **réparer Linux** : systemd et `journalctl`, GRUB, permissions, paquets, système de fichiers
   et espace disque ;
5. **protéger les données** : sauvegarde préalable, restauration, **vérification d'intégrité**,
   **autorisation** avant toute réinstallation ;
6. **distinguer** une panne réseau **logicielle** d'une panne **physique** ;
7. **contrôler** et **rédiger** le rapport d'intervention.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-15")}
{_req("AP-C03")}

AP-15 est une exigence officielle (consignes, p. 5) ; ce cours en traite la partie
**logicielle**, la partie matérielle étant vue en [PR06](/uaa/ampcr-pratique-pr06). AP-C03 est
un **complément pédagogique** de la matrice du parcours, signalé comme tel.

Les **messages d'erreur** (écrans bleus, code `0xc000000f`, `grub rescue>`, mode d'urgence)
sont étudiés en [PR11](/uaa/ampcr-pratique-pr11) ; les **commandes de base** (`sfc`, `DISM`,
`systemctl`, `journalctl`, `chmod`, `chown`) en [PR10](/uaa/ampcr-pratique-pr10) ; le
**stockage** et les partitions en [PR05](/uaa/ampcr-pratique-pr05) ; l'**installation** en
[PR08](/uaa/ampcr-pratique-pr08) et [PR09](/uaa/ampcr-pratique-pr09) ; le **dépannage réseau**
complet en [PR24](/uaa/ampcr-pratique-pr24). L'outillage et la protection des données font
l'objet d'un cours suivant du parcours (PR28).

## Lien avec la théorie

Les notions de base sont présentées dans la théorie AMPCR :
[MC30 Dépannage Windows et Linux](/uaa/ampcr-mc30) et
[MC32 Maintenance préventive et entretien](/uaa/ampcr-mc32). Ce cours-ci est **pratique** :
démarches rédigées, relevés à lire, pannes à résoudre et rapports, comme dans un dossier
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
> une question officielle ni une question déjà posée par le Jury. **Avant toute réparation qui
> retire quelque chose : sauvegarde et accord du client.**
"""


def _locate() -> str:
    return f"""**Objectifs** : nommer la famille de cause d'une panne logicielle à partir des
observations, et la confirmer par un test.

## 1.1 Sept familles de causes

Une panne « logicielle » n'est pas un diagnostic : il faut dire **où** elle se situe. Chaque
famille a ses signes et un **test** qui la confirme ou l'écarte.

{_causes_table()}

## 1.2 Isoler par élimination

On change **une seule condition** à la fois et l'on observe :

- **un autre programme** fait-il la même chose ? (sinon : l'application) ;
- **un compte de test** a-t-il le problème ? (sinon : le compte ou le profil) ;
- **le mode sans échec** le fait-il disparaître ? (oui : pilote, service ou programme au
  démarrage ; sous Windows, `msconfig` → **démarrage minimal** permet ensuite de réactiver les
  services un par un) ;
- **une analyse antivirus hors ligne** trouve-t-elle quelque chose ?

{_fig(ISOLATION_FIGURE)}

Un **service** en panne se repère directement par son état (`services.msc`, `systemctl
status`) ; un **disque défaillant** passe avant tout le reste, parce qu'il impose de sauvegarder
tout de suite. Les pannes **matérielles** (RAM, alimentation, surchauffe) sont traitées en
[PR06](/uaa/ampcr-pratique-pr06).

**Procédure professionnelle (à rédiger)** : observations → hypothèse (famille) → test qui la
confirme → conclusion justifiée.

**Erreur fréquente** : conclure « c'est Windows » sans avoir essayé un compte de test ni le
mode sans échec ; réinstaller pour une seule application qui plante.

**À l'écrit** : « **Observation** → donc **famille** → **test** de confirmation ».

**Repère rapide** : **stockage d'abord · un programme ? · un compte ? · mode sans échec ? ·
antivirus ? · sinon le système**. Exercices liés : {_ex("E04", "E09")}.
"""


def _collect() -> str:
    return f"""**Objectifs** : recueillir les faits utiles et lire les journaux qui datent et nomment
l'erreur.

## 2.1 Les six faits à recueillir

{_facts_table()}

Le **changement récent** est la piste la plus fréquente : mise à jour, pilote, logiciel,
matériel, coupure de courant. Le client dit souvent « on n'a rien changé » : les journaux
disent ce qui a été installé et quand.

## 2.2 Reproductibilité

- **Permanente** (à chaque démarrage, à chaque ouverture) : on peut tester chaque correction
  tout de suite.
- **Intermittente** : on note les conditions (heure, programme, charge, température) ; on
  compare avec les journaux ; une correction n'est validée qu'après une **durée d'observation**
  (une journée de travail, par exemple).

## 2.3 Les journaux

{_logs_table()}

## 2.4 La démarche complète

Le recueil des faits ouvre une démarche en six étapes, la même pour toutes les pannes
logicielles de ce cours.

{_fig(METHOD_FIGURE)}

**Procédure professionnelle (à rédiger)** : questions au client → reproduction de la panne →
lecture des journaux à la date de la première apparition → rapprochement avec un changement.

**Erreur fréquente** : se fier à « on n'a rien changé » ; corriger avant d'avoir lu le message
exact ; oublier que `journalctl -b -1` ne montre le démarrage précédent que si le journal est
conservé sur disque.

**À l'écrit** : les **questions** posées, le **message exact**, la **date**, le **changement**
rapproché.

**Repère rapide** : **quoi · depuis quand · reproductible · qui · quoi de neuf · quelles
données**. Exercices liés : {_ex("E01", "E09")}.
"""


def _protect() -> str:
    demo_a = sha256_hex(_HASH_DEMO_A)
    demo_b = sha256_hex(_HASH_DEMO_B)
    return f"""**Objectifs** : ne jamais faire perdre de données au client : sauvegarder, vérifier la
copie, demander l'accord avant d'effacer ou de réinstaller.

## 3.1 Sauvegarder avant de modifier

Toute réparation peut mal tourner. Avant la **première modification**, on vérifie qu'une
sauvegarde **récente** existe, ou on la fait. Si le disque montre des signes de faiblesse
(erreurs de lecture, SMART mauvais, bruits), la sauvegarde passe **avant tout le reste**, même
avant le diagnostic.

- On **copie**, on ne **déplace** pas : l'original reste en place tant que la copie n'est pas
  vérifiée.
- Outils : Explorateur ou **Historique des fichiers** sous Windows ; `robocopy` (copie
  journalisée, reprise après erreur) ; `rsync -a` ou `cp -a` sous Linux (`-a` **conserve
  propriétaires et droits**, voir l'exercice E16).
- Ce qu'on oublie souvent : messagerie locale, favoris du navigateur, données d'un logiciel
  métier, fichiers sur le Bureau, licences et codes d'activation.

{_fig(BACKUP_FIGURE)}

## 3.2 Vérifier l'intégrité : l'empreinte SHA-256

Une **empreinte** (*hash*) SHA-256 est une suite de 64 caractères calculée à partir du contenu
d'un fichier. Si **un seul octet** change, l'empreinte change complètement. Deux fichiers qui
ont la même empreinte sont identiques. Exemple calculé : « Bonjour » donne
`{demo_a[:16]}…`, « bonjour » donne `{demo_b[:16]}…`.

{_hash_table()}

On compare l'empreinte de l'original et celle de la copie ; on ouvre aussi quelques fichiers
pour essai. Une copie « terminée sans erreur » n'est pas forcément complète (câble qui a bougé,
disque plein).

## 3.3 Autorisation avant réinstallation

- On **informe** le client de ce qu'il peut perdre, dans des mots simples.
- Avant une **réinitialisation** ou une **réinstallation**, on obtient son **accord écrit** :
  ce qui sera effacé, ce qui est sauvegardé (où, vérifié), ce qu'il faudra réinstaller
  (licences, comptes), la date, la signature.
- On ne consulte pas ses données au-delà de ce qu'exige l'intervention (confidentialité) ; le
  support de sauvegarde est étiqueté et rendu ou effacé selon l'accord. Ces règles sont
  reprises en PR28.

**Procédure professionnelle (à rédiger)** : inventorier → copier → vérifier (empreintes,
ouverture) → consigner → accord écrit → seulement alors intervenir.

**Erreur fréquente** : « les documents restent, pas besoin de sauvegarde » ; déplacer au lieu
de copier ; ne pas vérifier la copie ; réinstaller sur simple accord oral.

**À l'écrit** : **ce qui est sauvegardé**, **comment c'est vérifié**, **l'accord** obtenu.

**Repère rapide** : **copier · vérifier · consigner · accord écrit**. Exercices liés :
{_ex("E03", "E06", "E15")}.
"""


def _winre() -> str:
    return f"""**Objectifs** : accéder au démarrage avancé de Windows et choisir l'outil adapté, du moins
au plus invasif.

## 4.1 Accéder au démarrage avancé (WinRE)

- Depuis Windows : **Maj + Redémarrer**, ou Paramètres → Système → Récupération → **Démarrage
  avancé** → Redémarrer maintenant ; en ligne de commande : `shutdown /r /o`.
- Automatiquement : après **deux échecs** de démarrage consécutifs, Windows ouvre l'écran de
  **réparation automatique** puis WinRE.
- Depuis une **clé d'installation** de Windows : Suivant → **Réparer l'ordinateur**.

Puis **Dépannage → Options avancées**.

{_winre_table()}

## 4.2 Le mode sans échec

Le **mode sans échec** démarre Windows avec les **pilotes et services de base** seulement :
Options avancées → **Paramètres** → Redémarrer → touche **4** (ou **5** avec le réseau). Si la
panne disparaît, la cause est un **pilote**, un **service** ou un **programme lancé au
démarrage** ; on peut alors restaurer ou désinstaller le dernier pilote ou logiciel, faire une
sauvegarde, ou lancer la restauration du système.

{_fig(BOOT_FIGURE)}

## 4.3 Prudence dans l'invite de commandes de WinRE

Dans WinRE, les **lettres de lecteur changent** : `X:` est WinRE lui-même, et le Windows du
disque peut être sur `D:`. On identifie le volume avec `dir D:\\` avant toute commande. Les
commandes qui modifient le démarrage (`bootrec`, `bcdboot`, `diskpart`) sont vues en
[PR11](/uaa/ampcr-pratique-pr11) ; on n'utilise **jamais** `diskpart clean` pour « réparer ».

**Procédure professionnelle (à rédiger)** : noter l'écran → WinRE → réparation du démarrage →
mode sans échec et retour arrière du dernier changement → désinstaller la mise à jour →
restauration du système → (réinitialisation : sauvegarde et accord écrit).

**Erreur fréquente** : choisir « Réinitialiser ce PC » en premier ; lancer une commande de
réparation sans avoir identifié les lecteurs.

**À l'écrit** : **l'outil** choisi, **pourquoi** lui, **ce qu'il touche** et le **contrôle**.

**Repère rapide** : **Maj + Redémarrer · 2 échecs → WinRE · F4 mode sans échec · X: = WinRE**.
Exercices liés : {_ex("E11")}.
"""


def _restore_points() -> str:
    return f"""**Objectifs** : créer un point de restauration et revenir à un état antérieur en sachant
ce qui sera retiré.

## 5.1 Le point de restauration

Un **point de restauration** enregistre l'état des **fichiers système**, du **registre**, des
**pilotes** et des **programmes installés**. Il ne contient **pas** les documents de
l'utilisateur : ce n'est **pas une sauvegarde**.

- **Activer la protection** : rechercher « Créer un point de restauration » (Propriétés
  système → Protection du système) → disque C: → **Configurer** → Activer la protection,
  espace réservé. La protection n'est pas toujours active par défaut : on la contrôle.
- **Créer un point** à la main avant une intervention : même fenêtre → **Créer**, avec une
  description claire (« Avant pilote imprimante, 21/10 »).
- Windows crée aussi des points **automatiquement** avant l'installation de certains
  programmes, pilotes et mises à jour, si la protection est active.

## 5.2 Restaurer

- Depuis Windows : `rstrui.exe` (ou bouton **Restauration du système**) ; si Windows ne démarre
  pas : WinRE → Options avancées → Restauration du système.
- On choisit le **dernier point antérieur à la panne** ; le bouton **Rechercher les programmes
  concernés** liste ce qui sera **retiré** (programmes, pilotes et mises à jour installés après
  le point) et ce qui pourrait être restauré.
- Les **documents** ne sont pas touchés ; une restauration lancée depuis Windows peut être
  **annulée** ensuite (un point est créé avant elle).

{_fig(RESTORE_FIGURE)}

**Procédure professionnelle (à rédiger)** : sauvegarde et accord → choisir le point (date,
description) → programmes concernés notés → restaurer sans éteindre → contrôler et réinstaller
ce qui manque.

**Erreur fréquente** : croire qu'un point de restauration sauvegarde les documents ; choisir le
point le plus ancien « pour être sûr » ; oublier de réinstaller les programmes retirés.

**À l'écrit** : **quel point** et **pourquoi**, **ce qui sera retiré**, **ce qui reste**.

**Repère rapide** : **point = système, pas les documents · rstrui · programmes concernés**.
Exercices liés : {_ex("E02", "E05")}.
"""


def _system_files() -> str:
    rows = "\n".join(f"| {date} | {name} |" for date, name in UPDATE_CASE_ROWS)
    return f"""**Objectifs** : réparer les fichiers système, revenir sur un pilote ou une mise à jour, sans
aller plus loin que nécessaire.

## 6.1 SFC et DISM

- `sfc /scannow` vérifie les fichiers système protégés et remplace ceux qui sont endommagés à
  partir du **magasin de composants**.
- `DISM /Online /Cleanup-Image /RestoreHealth` répare ce **magasin de composants** (avec Windows
  Update : le PC doit être en ligne).
- **Ordre** : `DISM` **puis** `sfc /scannow`, dans une **invite de commandes en
  administrateur** ; on redémarre et l'on relance `sfc` si besoin. Détails dans
  [PR10](/uaa/ampcr-pratique-pr10).
- **Hors ligne**, depuis WinRE : `sfc /scannow /offbootdir=D:\\ /offwindir=D:\\Windows`, avec la
  lettre **vérifiée** du volume Windows (exercice E11).

## 6.2 Pilotes

Si la panne suit une **mise à jour de pilote** : Gestionnaire de périphériques → Propriétés →
Pilote → **Restaurer le pilote** (version précédente) ; sinon désinstaller l'appareil et
installer la version qui fonctionnait, depuis le site du fabricant. En mode sans échec si
Windows ne démarre plus. Détails des codes d'erreur en [PR10](/uaa/ampcr-pratique-pr10).

## 6.3 Mises à jour

- **Historique** : Paramètres → Windows Update → Historique des mises à jour (date, numéro KB).
- **Désinstaller** une mise à jour qualité : Historique → **Désinstaller des mises à jour** ;
  depuis WinRE : **Désinstaller des mises à jour** → dernière mise à jour qualité ou de
  fonctionnalité.
- **Revenir à la version précédente** après une mise à jour de fonctionnalité : Paramètres →
  Système → Récupération → **Revenir en arrière**, possible pendant une durée limitée (dix
  jours par défaut).
- **Suspendre** les mises à jour quelques semaines, le temps qu'un correctif sorte : Windows
  Update → Suspendre. On **reprend** ensuite : un poste sans mises à jour de sécurité est
  exposé.
- **Réinstaller la version actuelle** en gardant fichiers, applications et réglages : Paramètres
  → Système → Récupération → « **Résoudre les problèmes à l'aide de Windows Update** » (selon
  la version de Windows 11).

Exemple d'historique (cas 4) :

| Date | Mise à jour |
|---|---|
{rows}

*{UPDATE_CASE_KB} est un numéro fictif, pour l'exercice.*

**Procédure professionnelle (à rédiger)** : dater la panne → rapprocher d'un pilote ou d'une
mise à jour → retour arrière **ciblé** → contrôle → suspendre et noter la date de reprise.

**Erreur fréquente** : `sfc` dans une invite standard ; `sfc` avant `DISM` quand SFC ne répare
pas ; désactiver Windows Update définitivement.

**À l'écrit** : la **commande exacte** ou le **chemin dans les Paramètres**, et le **contrôle**.

**Repère rapide** : **DISM puis SFC · Restaurer le pilote · Désinstaller des mises à jour ·
Suspendre puis reprendre**. Exercices liés : {_ex("E05", "E11")}.
"""


def _profile() -> str:
    return f"""**Objectifs** : reconnaître un profil utilisateur corrompu, protéger ses données et le
recréer.

## 7.1 Reconnaître le problème

Le **profil** d'un utilisateur est son dossier `C:\\Users\\nom` et ses réglages (fichier
`NTUSER.DAT`, dossier `AppData`). S'il ne se charge pas (coupure de courant, erreur disque),
Windows ouvre une session avec un **profil temporaire** : bureau vide, réglages par défaut. Les
fichiers ne sont **pas perdus** : ils restent dans l'ancien dossier. Mais tout ce qui est créé
dans le profil temporaire est **supprimé à la déconnexion**.

{_fig(PROFILE_FIGURE)}

## 7.2 Réparer

{_profile_steps()}

- Un **compte de test** qui fonctionne confirme que le problème vient du profil, pas de
  Windows.
- La réparation par le registre (clé `ProfileList` de `HKLM\\SOFTWARE\\Microsoft\\Windows
  NT\\CurrentVersion`, entrée en `.bak`) est réservée à un technicien confirmé, **après
  sauvegarde** ; la recréation du profil est la voie sûre.
- On ne recopie pas tout `AppData` : il peut contenir la corruption ; on reconfigure la
  messagerie et les logiciels.

**Procédure professionnelle (à rédiger)** : ne rien enregistrer → sauvegarde de l'ancien profil
depuis un compte administrateur → disque et fichiers système vérifiés → nouveau profil →
données recopiées → contrôle avec l'utilisateur.

**Erreur fréquente** : laisser l'utilisateur travailler dans le profil temporaire ; supprimer
l'ancien dossier `C:\\Users\\nom` avant d'avoir copié ses fichiers.

**À l'écrit** : **ce que dit le message**, **où sont les fichiers**, **ordre des gestes**.

**Repère rapide** : **profil temporaire = rien n'est perdu, mais rien n'est gardé**. Exercices
liés : {_ex("E10")}.
"""


def _malware() -> str:
    return f"""**Objectifs** : reconnaître un logiciel malveillant et réagir sans aggraver la situation.

## 8.1 Signes

- **Publicitaires** : fenêtres, page d'accueil ou moteur de recherche changés, extension
  inconnue dans le navigateur, souvent après un « logiciel gratuit ».
- **Rançongiciel** : fichiers renommés (`.locked`…), illisibles, note de rançon ; il peut
  chiffrer les **dossiers partagés** et les **disques branchés**.
- **Général** : processus inconnu qui occupe le processeur, antivirus désactivé, comptes
  modifiés.

## 8.2 Réagir

1. **Isoler** : débrancher le câble réseau, couper le Wi-Fi ; **ne pas brancher** de disque de
   sauvegarde ; de préférence ne pas éteindre (le responsable décide).
2. **Prévenir** le responsable ; ne **jamais payer** une rançon ; noter l'heure et le message.
3. **Analyser** : Sécurité Windows → Protection contre les virus et menaces → Options d'analyse
   → **analyse hors ligne de Microsoft Defender** (redémarre et analyse avant Windows).
4. **Nettoyer** : désinstaller le programme et l'extension en cause ; restauration du système
   au point d'avant l'installation.
5. **Restaurer** les fichiers chiffrés depuis une **sauvegarde saine antérieure** ; si le poste
   est compromis, **réinstallation** avec accord écrit.
6. **Changer les mots de passe** depuis un **appareil sain**.

**Procédure professionnelle (à rédiger)** : isoler → prévenir → analyser → nettoyer ou
réinstaller → restaurer depuis une sauvegarde saine → mots de passe → contrôle.

**Erreur fréquente** : brancher le disque de sauvegarde pour « récupérer » les fichiers ;
laisser le poste sur le réseau ; désactiver l'antivirus « parce qu'il ralentit ».

**À l'écrit** : **ordre** des gestes immédiats et **justification** de chacun.

**Repère rapide** : **isoler · prévenir · ne pas payer · sauvegarde saine**. Exercices liés :
{_ex("E04")}.
"""


def _linux_systemd() -> str:
    return f"""**Objectifs** : dépanner un service systemd et un démarrage Linux à partir du journal et de
GRUB.

## 9.1 Services et journal

- `systemctl --failed` liste les services en échec ; `systemctl status nom` donne l'état
  (`active (running)`, `inactive (dead)`, `failed`) et les dernières lignes du journal.
- `journalctl -u nom -b` : messages du service depuis le démarrage ; `journalctl -b -p err` :
  erreurs du démarrage ; `journalctl -b -1` : démarrage **précédent** (journal conservé sur
  disque).
- **Tester la configuration** avant de redémarrer : `sudo nginx -t`, `sudo sshd -t`,
  `sudo apache2ctl configtest`. Un redémarrage sur une configuration fausse échoue de nouveau.
- Avant de modifier un fichier de configuration : **copie** (`sudo cp fichier fichier.bak`).

{_fig(LINUX_SERVICE_FIGURE)}

## 9.2 GRUB et noyaux

- Afficher le menu : maintenir **Maj** (démarrage BIOS) ou appuyer sur **Échap** (UEFI) au
  démarrage.
- **Advanced options for Ubuntu** liste les noyaux installés : si la panne suit une mise à jour
  du noyau, on démarre sur le **précédent** pour confirmer, puis on cherche le correctif. On ne
  supprime pas le noyau qui fonctionne.
- **Recovery mode** : menu de réparation (dont `fsck`, `dpkg`, shell root) ; `sudo update-grub`
  régénère le menu. Les messages `grub rescue>` et le mode d'urgence sont vus en
  [PR11](/uaa/ampcr-pratique-pr11).

**Procédure professionnelle (à rédiger)** : `systemctl --failed` → journal du service → test de
la configuration → correction prudente (copie) → redémarrage du service → contrôle.

**Erreur fréquente** : redémarrer le service en boucle sans lire le journal ; modifier la
configuration sans copie ; supprimer l'ancien noyau.

**À l'écrit** : la **ligne du journal** qui donne la cause, la **commande** de correction, le
**contrôle**.

**Repère rapide** : **--failed · status · journalctl -u · -t avant restart · ancien noyau dans
GRUB**. Exercices liés : {_ex("E07", "E13")}.
"""


def _linux_storage() -> str:
    return f"""**Objectifs** : corriger des permissions, réparer des paquets, vérifier un système de
fichiers et libérer de l'espace sous Linux, sans rien perdre.

## 10.1 Permissions

Un fichier qui appartient à **root** dans le dossier d'un utilisateur (copié avec `sudo`)
devient non modifiable pour lui. On le lui rend sur **ce seul dossier** :
`sudo chown -R anne:anne /home/anne/Documents`. Jamais `chmod 777`, jamais `chown -R` sur `/`,
`/etc` ou tout `/home`. Lecture des droits : [PR10](/uaa/ampcr-pratique-pr10).

## 10.2 Paquets

- **Installation interrompue** (coupure pendant une mise à jour) : `sudo dpkg --configure -a`.
- **Dépendances cassées** : `sudo apt --fix-broken install`.
- **Historique** : `/var/log/apt/history.log` (Debian, Ubuntu) ou `dnf history` (Fedora) dit
  ce qui a changé et quand.

## 10.3 Système de fichiers

- `fsck` vérifie et répare un système de fichiers **démonté** : depuis une **clé live** ou le
  **mode de récupération**. **Jamais** sur une partition montée en écriture.
- Erreurs répétées : on **sauvegarde d'abord**, on lit l'état SMART (outil Disques, `smartctl`),
  on remplace le disque s'il faiblit ([PR05](/uaa/ampcr-pratique-pr05),
  [PR06](/uaa/ampcr-pratique-pr06)).

## 10.4 Espace disque

- `df -h` : espace de chaque partition (`Use%`) ; `df -i` : inodes. `100%` ou « No space left
  on device » : services qui échouent, session qui ne s'ouvre plus.
- `sudo du -xh -d1 /var | sort -h` : quels dossiers occupent la place (sans changer de
  partition).
- Libérer **sans risque** : `sudo journalctl --vacuum-size=500M` (anciens journaux),
  `sudo apt clean` (paquets téléchargés), `sudo apt autoremove` (anciens noyaux et dépendances
  inutiles, après vérification de la liste) ; puis **corriger la cause** (service qui écrit en
  boucle dans les journaux, sauvegardes qui s'accumulent).

{_linux_fixes_table()}

**Procédure professionnelle (à rédiger)** : mesurer (`df -h`) → localiser (`du`) → libérer ce
qui est sans risque → corriger la cause → contrôler.

**Erreur fréquente** : supprimer à la main dans `/var/lib` ou `/usr` ; `fsck` sur `/` monté ;
`rm` des fichiers du client sans accord.

**À l'écrit** : **mesure**, **ce qui occupe**, **ce qui est libéré et comment**, **cause**.

**Repère rapide** : **df · du · vacuum · apt clean · fsck démonté · chown sur le seul dossier**.
Exercices liés : {_ex("E07", "E12", "E16")}.
"""


def _ladder() -> str:
    return f"""**Objectifs** : choisir le geste de réparation le moins invasif qui règle la panne, et
savoir quand une réinstallation devient justifiée.

## 11.1 L'échelle des interventions

On **monte d'une marche** seulement si la précédente n'a pas suffi, et l'on contrôle après
chaque marche.

{_fig(LADDER_FIGURE)}

{_ladder_table()}

*Effets d'après la documentation de Microsoft ; ordre des marches et précautions : convention
du cours.*

## 11.2 Quand réinstaller ?

Une réinstallation (ou réinitialisation) est justifiée quand les marches précédentes ont
échoué, quand le système est **compromis** par un logiciel malveillant, ou quand la réparation
coûterait plus de temps que la remise à neuf **avec l'accord du client**. Elle se fait
toujours après une **sauvegarde vérifiée** et un **accord écrit**, puis l'on **restaure** les
données et l'on **vérifie** leur présence.

Sous Linux, l'équivalent de l'échelle : annuler le changement (ancien noyau, version
précédente d'un fichier de configuration), réparer les paquets (`dpkg`, `apt`), puis
réinstaller en **conservant la partition `/home`** si elle est séparée.

**Procédure professionnelle (à rédiger)** : marche choisie → précaution prise → résultat →
marche suivante seulement si nécessaire.

**Erreur fréquente** : sauter directement à la dernière marche ; changer plusieurs choses à la
fois.

**À l'écrit** : **la marche**, **sa précaution**, **ce qu'elle retire**.

**Repère rapide** : **{effect_of(LADDER[0]).lower()} en bas · fichiers effacés en haut ·
accord écrit avant toute réinitialisation**. Exercices liés : {_ex("E05", "E06", "E17")}.
"""


def _network() -> str:
    return f"""**Objectifs** : dire si une panne réseau est physique ou logicielle, avec le test qui le
prouve.

## 12.1 Du plus proche au plus lointain

{_fig(NETWORK_FIGURE)}

- **Physique** : « Média déconnecté » dans `ipconfig`, voyant éteint, `state DOWN` / `NO-CARRIER`
  dans `ip link` ; Wi-Fi désactivé (touche, mode avion). On vérifie câble, prise, port, carte.
- **Logiciel ou configuration** : adresse 169.254.x.x (pas de DHCP), passerelle ou DNS faux,
  pilote de la carte, pare-feu, proxy, VPN, navigateur.
- **Comparer** : un autre poste au même endroit fonctionne-t-il ? un autre navigateur ? un autre
  câble ? La comparaison isole sans rien modifier.

Les relevés (`ipconfig /all`, `ping`, `tracert`, `nslookup`) sont détaillés en
[PR20](/uaa/ampcr-pratique-pr20) et le dépannage réseau complet en
[PR24](/uaa/ampcr-pratique-pr24).

**Procédure professionnelle (à rédiger)** : lien → adresse → passerelle → adresse Internet →
nom → application ; conclure à la première étape qui échoue.

**Erreur fréquente** : réinstaller le pilote réseau alors que le câble est débranché ;
remplacer un câble alors que l'adresse est en 169.254.

**À l'écrit** : **l'observation**, **physique ou logiciel**, **le premier geste**.

**Repère rapide** : **Média déconnecté = physique · 169.254 = DHCP · IP OK nom KO = DNS**.
Exercices liés : {_ex("E08")}.
"""


def _checklist_report() -> str:
    return f"""**Objectifs** : valider l'intervention et laisser une trace écrite complète.

## 13.1 Liste de contrôle

{_checklist_table()}

## 13.2 Rapport d'intervention

1. **Demande** : client, date, symptôme décrit, accord obtenu (et sa forme).
2. **Constat** : message exact, journaux, changement rapproché, famille de cause.
3. **Sauvegarde** : ce qui a été sauvegardé, où, comment c'est vérifié.
4. **Actions** : chaque geste, dans l'ordre, avec son résultat (commande, outil, version).
5. **Contrôles** : liste ci-dessus et résultats.
6. **Recommandations** : sauvegardes régulières, mises à jour (date de reprise si suspendues),
   onduleur, comptes standard ; signatures.

Le rapport ne contient **jamais de mot de passe**.

**Procédure professionnelle (à rédiger)** : passer la liste avec le client → reporter chaque
résultat → rapport en rubriques.

**Erreur fréquente** : rapport réduit à « Windows réparé » ; oublier de dire ce qui a été
retiré (programmes, mise à jour).

**À l'écrit** : la **liste** (point — commande — résultat) et le **rapport en rubriques**.

**Repère rapide** : **constat · sauvegarde · actions · contrôles · recommandations**.
Exercices liés : {_ex("E17")}.
"""


def _examples() -> str:
    freed = " ; ".join(f"`{cmd}` (environ {size:g} Gio)" for cmd, size in CASE5_FREED)
    return f"""## Cas 1 — Démarrage : écran noir depuis le nouveau pilote graphique

**Situation.** Un photographe a installé hier un pilote graphique téléchargé sur le site du
fabricant de la carte. Depuis, Windows 11 reste sur un écran noir après le logo ; au troisième
essai, l'écran **Réparation automatique** apparaît. Ses photos sont sauvegardées chaque
semaine ; celles de la semaine ne le sont pas.

**Résolution.**

1. **Lecture** : la panne suit le pilote : piste **pilote** (famille « pilote, service ou
   programme au démarrage »). Le disque est détecté, Windows commence à charger.
2. **WinRE** : Options avancées → **Outil de redémarrage système** : échec. Puis Paramètres →
   Redémarrer → **4** : le **mode sans échec** démarre (pilote d'affichage de base) : la
   piste est confirmée.
3. **Données** : en mode sans échec, copie des photos de la semaine sur un disque externe,
   vérification de quelques fichiers.
4. **Retour arrière ciblé** : Gestionnaire de périphériques → carte graphique → Pilote →
   **Restaurer le pilote** (à défaut : restauration du système au point « Installed … »
   d'hier).
5. **Contrôle** : deux démarrages normaux, affichage correct, Moniteur de fiabilité sans nouvel
   arrêt ; mises à jour de pilote de cette carte à surveiller.

**Conclusion rédigée.** « Écran noir causé par le pilote graphique installé le 20/10 ; photos
sauvegardées ; pilote précédent restauré en mode sans échec ; démarrage normal contrôlé deux
fois. »

## Cas 2 — Service : le site de la boutique ne répond plus

**Situation.** Sur le petit serveur Debian d'une boutique en ligne, le site affiche « Impossible
de se connecter » depuis que le neveu du gérant a modifié la configuration du serveur web
nginx. Le serveur lui-même répond.

{_fig(NGINX_FIGURE)}

**Résolution.**

1. **Lecture** : `nginx.service` est **failed** ; `nginx -t` désigne la **ligne 14** du fichier
   `/etc/nginx/sites-enabled/boutique` : une accolade en trop.
2. **Correction prudente** : copie du fichier (`sudo cp … boutique.bak-2026-10-21`), puis
   correction de la ligne 14 (ou retour à la version qui fonctionnait, si elle existe).
3. **Test** : `sudo nginx -t` → « syntax is ok », « test is successful ».
4. **Redémarrage** : `sudo systemctl restart nginx` ; le service est `enabled`.
5. **Contrôle** : `systemctl status nginx` → `active (running)`, page d'accueil et commande
   d'essai, `journalctl -u nginx -b` sans nouvelle erreur.

**Conclusion rédigée.** « Service web arrêté par une erreur de syntaxe (ligne 14) ; fichier
copié puis corrigé, configuration testée, service redémarré ; site contrôlé. »

## Cas 3 — Profil : « profil temporaire » après une coupure de courant

**Situation.** Après une coupure de courant, Lucie, secrétaire d'un cabinet dentaire, ouvre sa
session Windows 11 : bureau vide, message de profil temporaire (voir la capture du chapitre 7).

**Résolution.**

1. **Lecture** : profil non chargé (événement 1511) ; les fichiers sont dans
   `C:\\Users\\lucie` ; rien ne doit être enregistré dans la session temporaire.
2. **Données** : connexion avec le compte administrateur du cabinet, copie de
   `C:\\Users\\lucie` (Documents, Bureau, Images, favoris, fichier de messagerie) sur un disque
   externe, vérification.
3. **Vérifications** : espace libre, état SMART, `DISM` puis `sfc /scannow` (coupure de
   courant).
4. **Réparation** : un redémarrage ne suffit pas ; nouveau profil créé (ancien dossier renommé
   par le technicien, nouvelle ouverture de session) ; données recopiées, messagerie
   reconfigurée.
5. **Contrôle** : session normale, fichiers présents, imprimante et messagerie opérationnelles.

**Conclusion rédigée.** « Profil local endommagé par une coupure ; données sauvegardées ;
profil recréé et données recopiées ; session contrôlée avec l'utilisatrice. »

## Cas 4 — Mise à jour : le logiciel de facturation ne démarre plus

**Situation.** Depuis le 21 octobre, le logiciel de facturation d'un plombier se ferme dès son
ouverture. Tous les autres programmes fonctionnent, dans tous les comptes. L'historique de
Windows Update montre {UPDATE_CASE_KB} installée le 21 octobre (tableau du chapitre 6) ; l'éditeur
du logiciel signale ce problème et annonce un correctif.

**Résolution.**

1. **Lecture** : une seule application touchée ; la date coïncide avec la mise à jour ;
   l'éditeur confirme.
2. **Retour arrière ciblé** : état noté ; Historique des mises à jour → **Désinstaller des mises
   à jour** → {UPDATE_CASE_KB} ; redémarrage.
3. **Éviter la réinstallation automatique** : Windows Update → **Suspendre** jusqu'à la date du
   correctif annoncé.
4. **Contrôle** : le logiciel s'ouvre, facture d'essai imprimée ; date de reprise des mises à
   jour notée dans le rapport.

**Conclusion rédigée.** « Logiciel de facturation incompatible avec {UPDATE_CASE_KB} ; mise à jour
désinstallée, mises à jour suspendues jusqu'au correctif ; reprise prévue et notée. »

## Cas 5 — Espace disque : plus rien ne s'enregistre sur un poste Ubuntu

**Situation.** Sur le PC Ubuntu d'une bibliothèque, la session graphique ne s'ouvre plus et
les applications affichent « No space left on device ». Une imprimante mal configurée a fait
tourner en boucle un message d'erreur dans les journaux pendant des semaines.

{_fig(DISK_FIGURE)}

**Résolution.**

1. **Lecture** : `/` à 100 % (environ {CASE5_USED_BEFORE:g} Gio utilisés) ; `du` montre que
   `/var/log` est le plus gros dossier, puis `/var/lib` et `/var/cache`.
2. **Libérer sans risque** (session texte, Ctrl + Alt + F3) : {freed}.
3. **Corriger la cause** : file d'impression et imprimante reconfigurées, le message d'erreur
   ne se répète plus (`journalctl -f`).
4. **Contrôle** :

{_console(*CASE5_DF_AFTER)}

   Session graphique ouverte, environ {CASE5_USED_AFTER:g} Gio utilisés ; recommandation :
   surveiller l'espace.

**Conclusion rédigée.** « Partition racine pleine à cause des journaux d'une imprimante en
erreur ; journaux réduits et cache nettoyé ; cause corrigée ; session contrôlée. »
"""


def _pitfalls() -> str:
    return """> **Réinstaller d'emblée** « parce que c'est plus rapide », sans diagnostic.

> **Intervenir sans sauvegarde** ; **déplacer** au lieu de copier ; **ne pas vérifier** la copie.

> **Réinitialiser sur simple accord oral**, sans dire au client ce qu'il perd.

> **Croire qu'un point de restauration sauvegarde les documents.**

> **Laisser travailler l'utilisateur dans un profil temporaire.**

> **Lancer `sfc` dans une invite standard** ou dans WinRE sans `/offwindir` ; oublier que les
> lettres changent dans WinRE.

> **Supprimer à la main** dans `C:\\Windows\\WinSxS`, `/var/lib` ou `/usr`.

> **`fsck` sur une partition montée** ; `fsck -y` sans lire.

> **Brancher le disque de sauvegarde** sur un poste infecté par un rançongiciel.

> **Changer plusieurs réglages à la fois** : on ne sait plus ce qui a réglé ou aggravé la
> panne.

> **Suspendre les mises à jour sans date de reprise.**

> **Remplacer un câble** quand l'adresse est en 169.254, ou **réinstaller un pilote** quand le
> câble est débranché.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (démarche, restauration du
système, sauvegarde), classements (famille de cause, effet d'un geste sur les données,
précaution, commande Linux, panne réseau logicielle ou physique), relevés à lire (Moniteur de
fiabilité, profil temporaire, volumes de WinRE, dpkg interrompu, GRUB, espace disque,
empreintes SHA-256, fichiers restaurés), procédure à corriger. Rédige ta réponse sur papier
**avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces mêmes
exercices sont proposés dans [S'entraîner](/uaa/{PR12_SLUG}/practice), avec correction après
envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR12_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les informations
nécessaires sont dans l'énoncé et ses documents (consoles et tableaux fictifs).
**Aucune correction n'est visible pendant la passation** ; tes réponses sont enregistrées au
fur et à mesure. Après l'envoi, chaque réponse est corrigée selon le **barème analytique** de la
question (critères et points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le
barème.

**Ce que valorise le barème.** Le **diagnostic justifié** (observation → cause), l'**ordre**
des gestes, du moins invasif au plus invasif, la **protection des données** et l'**accord** du
client, la **commande** ou le **chemin** exact et le **contrôle** — pas la récitation de sigles.
Une autre formulation juste est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return """## Mémo

- **Démarche** : recueillir → reproduire et délimiter → journaux → **sauvegarder** → corriger
  par étapes → contrôler et rédiger.
- **Familles** : stockage · application · compte/profil · pilote, service ou démarrage ·
  service · malveillant · système. **Tests** : autre programme, compte de test, mode sans
  échec, analyse hors ligne.
- **Faits** : symptôme exact · depuis quand · reproductible · portée · changement récent ·
  données et sauvegarde.
- **Journaux** : Observateur d'événements · Moniteur de fiabilité · Historique des mises à jour
  · `journalctl -b -p err` · `systemctl --failed` · `/var/log/apt/history.log`.
- **WinRE** : Maj + Redémarrer · 2 échecs · clé → Réparer l'ordinateur ; réparation du
  démarrage · mode sans échec (4) · désinstaller des mises à jour · restauration du système ·
  réinitialiser en dernier.
- **Windows** : `DISM /Online /Cleanup-Image /RestoreHealth` puis `sfc /scannow` (admin) ;
  hors ligne `/offbootdir` `/offwindir` ; Restaurer le pilote ; Suspendre puis reprendre les
  mises à jour ; profil temporaire : sauvegarder puis recréer.
- **Linux** : `systemctl status` · `journalctl -u … -b` · `nginx -t` avant `restart` · ancien
  noyau dans GRUB · `dpkg --configure -a` · `apt --fix-broken install` · `fsck` démonté ·
  `df -h`, `du -xh -d1`, `journalctl --vacuum-size`, `apt clean` · `chown` sur le seul dossier.
- **Données** : copier, vérifier (SHA-256 : `Get-FileHash`, `certutil -hashfile … SHA256`,
  `sha256sum`), consigner, **accord écrit** avant réinitialisation.
- **Réseau** : Média déconnecté = physique · 169.254 = DHCP · passerelle · Internet · DNS ·
  application.

## Glossaire des termes employés

- **Démarrage minimal** : démarrage de Windows sans les services et programmes tiers
  (`msconfig`), pour les réactiver un par un.
- **Empreinte (SHA-256)** : valeur calculée sur le contenu d'un fichier ; identique si et
  seulement si les contenus sont identiques (en pratique).
- **Magasin de composants** : copie de référence des fichiers de Windows, réparée par DISM et
  utilisée par SFC.
- **Mode sans échec** : démarrage de Windows avec les pilotes et services de base seulement.
- **Point de restauration** : état enregistré des fichiers système, du registre, des pilotes et
  des programmes ; ne contient pas les documents.
- **Profil temporaire** : session ouverte par Windows quand le profil de l'utilisateur ne se
  charge pas ; vidée à la déconnexion.
- **Rançongiciel** : logiciel malveillant qui chiffre les fichiers et demande une rançon.
- **Réinitialiser ce PC** : réinstallation de Windows depuis les Paramètres ou WinRE, en
  conservant ou non les fichiers personnels.
- **WinRE** : environnement de récupération de Windows (démarrage avancé).
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), pp. 3 et 5 : épreuve uniquement écrite, exigence AP-15
  « Dépannage sur les dysfonctionnements courants (hardware ou software) ». Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Windows** : documentation Microsoft (environnement de récupération Windows et options de
  démarrage avancé, mode sans échec, protection du système et restauration du système, SFC et
  DISM, désinstallation et suspension des mises à jour, options de récupération et
  réinitialisation, profils utilisateurs, Moniteur de fiabilité, analyse hors ligne de
  Microsoft Defender, `Get-FileHash`, `certutil`, `robocopy`).
- **Linux** : pages de manuel de `systemctl`, `journalctl`, `dpkg`, `apt`, `fsck`, `df`, `du`,
  `chown`, `cp`, `rsync`, `sha256sum`, `nginx` ; documentation d'Ubuntu et de Debian (GRUB,
  mode de récupération, journal de systemd).
- **SHA-256** : norme FIPS 180-4 ; les empreintes du cours et des exercices sont calculées par
  programme.

Les libellés de Windows 11 et des distributions sont ceux de {WRITTEN_AT} ; ils changent avec
les versions : la documentation de l'éditeur fait foi le jour de l'intervention. Les familles
de causes, l'arbre d'isolement, l'échelle des interventions, les précautions, les procédures,
les empreintes, les relevés d'espace disque et l'arbre réseau du cours sont **produits par
programme** depuis des données **vérifiées par des tests automatiques** ; aucun schéma n'est
tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La liste des pp. 5-6 cite le dépannage des dysfonctionnements courants (AP-15). Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- la protection des données du client, la vérification d'intégrité et l'accord écrit avant
  réinstallation (AP-C03 de la matrice du parcours) ;
- les logiciels malveillants et la distinction panne réseau logicielle / physique ;
- l'arbre d'isolement, l'échelle des interventions, les trois niveaux de précaution, le seuil
  d'espace libre et la liste de contrôle : ce sont des **conventions du cours**, pas une norme.

## Supports fictifs

Les consoles, fenêtres et situations de ce cours sont **fictives** et reconstituées pour
l'entraînement, parfois abrégées ; elles ne décrivent aucun client réel. Les numéros de mise à
jour et les noms de logiciels des exercices sont inventés. Aucune n'est une question
officielle ou déjà posée par le Jury.
"""


def pr12_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR12 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR12 — 1. Situer la cause : système, application, pilote, compte, service, malveillant, stockage", _locate()),
        ("PR12 — 2. Recueillir les faits : symptômes, reproductibilité, changements et journaux", _collect()),
        ("PR12 — 3. Protéger les données : sauvegarde, intégrité et autorisation", _protect()),
        ("PR12 — 4. Windows : démarrage avancé, WinRE et mode sans échec", _winre()),
        ("PR12 — 5. Windows : points de restauration et restauration du système", _restore_points()),
        ("PR12 — 6. Windows : SFC, DISM, pilotes et mises à jour", _system_files()),
        ("PR12 — 7. Windows : profil utilisateur corrompu", _profile()),
        ("PR12 — 8. Logiciels malveillants : reconnaître et réagir", _malware()),
        ("PR12 — 9. Linux : systemd, journalctl et GRUB", _linux_systemd()),
        ("PR12 — 10. Linux : permissions, paquets, système de fichiers et espace disque", _linux_storage()),
        ("PR12 — 11. Réparer, restaurer ou réinstaller : l'échelle des interventions", _ladder()),
        ("PR12 — 12. Panne réseau : logicielle ou physique ?", _network()),
        ("PR12 — 13. Contrôles finaux et rapport d'intervention", _checklist_report()),
        ("PR12 — Exemples : cinq cas résolus", _examples()),
        ("PR12 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR12 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR12 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR12 — Fiche mémo et glossaire", _memo()),
        ("PR12 — Sources et compléments pédagogiques", _sources()),
    ]
