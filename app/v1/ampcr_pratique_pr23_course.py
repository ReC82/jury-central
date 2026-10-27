"""Cours PR23 « Partage de dossiers, imprimantes et permissions » — parcours AMPCR pratique écrite
(ticket #223).

Matière : intégralement celle du ticket #223 (partages Windows SMB, chemins UNC, découverte du
réseau, authentification ; permissions de partage et NTFS, combinaison effective, Lecture /
Modification / Contrôle total, héritage et groupes ; Linux Samba en complément, droits Unix rwx
et ACL ; partage d'imprimante et file d'attente, accès local ou distant, pilotes, pare-feu,
disponibilité de l'hôte ; diagnostics « ping OK mais accès refusé », « nom du serveur
introuvable », « droits insuffisants », « imprimante hors connexion » ; protection des données
et moindre privilège ; cinq cas résolus), découpée en blocs titrés (le titre pilote le type de
carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen », « source »,
« ressource », « exemple », « exercice », « méthode », « piège », « attention », « transfert » ni
« mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr23_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr23_bank`. Le partage entre deux PC vient de PR21, les comptes et
groupes de PR22, le dépannage réseau de PR24, Linux de PR09 (publiés, liens).
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr22_figures import USERS_DOMAIN
from app.v1.ampcr_pratique_pr23_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr23_figures import (
    ACCESS_MATRIX,
    AUTH_USERS,
    COMPARISON,
    DRIVE_LETTER,
    EVERYONE,
    ICACLS_FIGURE,
    IPP_PORT,
    JULIE,
    LAYERS_FIGURE,
    LAYERS_PATH,
    LEVEL_ABILITIES,
    LEVELS,
    LOCAL_ADMINS,
    LX_DIR,
    LX_SHARE,
    LX_USERS,
    MATRIX_FIGURE,
    MATRIX_PATHS,
    NET_PRINTER,
    NET_PRINTER_IP,
    NTFS_TREE,
    PRINT_CHECKS,
    PRINT_HOST,
    PRINT_MODES,
    PRINT_TREE_FIGURE,
    PRINTER_FIGURE,
    PRINTER_PROC_FIGURE,
    PROCEDURES,
    RAW_PORT,
    SAM,
    SERVER_IP,
    SERVER_NAME,
    SHARE_CHECKS,
    SHARE_MESSAGES,
    SHARE_PROC_FIGURE,
    SHARE_ROOT,
    SHARE_TREE_FIGURE,
    SHARES,
    SMB_CONF_LINES,
    SMB_PORT,
    SPOOLER_LINES,
    STATIC_FIGURES,
    TREE_FIGURE,
    TROUBLE_PROC_FIGURE,
    UNC_EXAMPLE,
    UNC_EXAMPLE_IP,
    UNC_FIGURE,
    UNIX_FIGURE,
    USB_PRINTER,
    WRITTEN_AT,
    AccessState,
    Account,
    Ace,
    Folder,
    LinuxUser,
    PrintState,
    SambaShare,
    Share,
    effective_access,
    getfacl_lines,
    limiting_layer,
    linux_effective,
    ls_lines,
    mode_string,
    net_view_lines,
    ntfs_level,
    port_test_lines,
    print_checks,
    print_diagnosis,
    share_checks,
    share_diagnosis,
    share_level,
    short_path,
    unc,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR23_TITLE = "Partage de dossiers, imprimantes et permissions"
PR23_SLUG = "ampcr-pratique-pr23"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr23")
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


def _console(lines: tuple[str, ...]) -> str:
    return f'<pre class="jc-pr-console" tabindex="0">{escape(chr(10).join(lines))}</pre>'


def _md(text: str) -> str:
    """Markdown mange une barre oblique inverse sur deux hors du code : on double celles des
    chemins UNC (\\\\serveur) en dehors des passages entre accents graves."""
    pieces = text.split("`")
    return "`".join(p.replace("\\\\", "\\\\\\\\") if i % 2 == 0 else p for i, p in enumerate(pieces))


def _rule(entries: tuple[Ace, ...]) -> str:
    return "; ".join(f"{e.principal} : {'Refuser ' if e.deny else ''}{e.right}" for e in entries) or "—"


# --- Tableaux (générés depuis les données vérifiées) -----------------------------------------


def _comparison_table() -> str:
    rows = "\n".join(f"| **{what}** | {share} | {ntfs} |" for what, share, ntfs in COMPARISON)
    return "| | Autorisations du partage | Autorisations NTFS |\n|---|---|---|\n" + rows


def _levels_table() -> str:
    rows = "\n".join(f"| **{level}** | {what} |" for level, what in LEVEL_ABILITIES)
    return "| Niveau | Ce qu'il permet |\n|---|---|\n" + rows


def _shares_table() -> str:
    rows = "\n".join(f"| {s.name} | `{unc(SERVER_NAME, s.name)}` | {short_path(s.path)} | {_rule(s.entries)} |"
                     for s in SHARES.values())
    return "| Partage | Chemin UNC | Dossier | Autorisations du partage |\n|---|---|---|---|\n" + rows


def _ntfs_table() -> str:
    def own(path: str) -> str:
        entries = tuple(e for e in NTFS_TREE[path].entries if e.principal != LOCAL_ADMINS)
        return _rule(entries) if NTFS_TREE[path].entries else "aucune (tout est hérité)"

    rows = "\n".join(f"| {short_path(p)} | {'oui' if NTFS_TREE[p].inherit else '**désactivé**'} | {own(p)} |"
                     for p in MATRIX_PATHS)
    return ("| Dossier | Héritage du parent | Entrées posées sur le dossier |\n|---|---|---|\n" + rows)


def _matrix_table(matrix: dict[str, dict[str, str]]) -> str:
    folders = list(next(iter(matrix.values())))
    head = "| Compte | " + " | ".join(folders) + " |\n|---|" + "---|" * len(folders) + "\n"
    return head + "\n".join(f"| {login} | " + " | ".join(row[f] for f in folders) + " |" for login, row in matrix.items())


def _checks_table(checks: tuple[tuple[str, str, str], ...]) -> str:
    rows = "\n".join(f"| {i} | {_md(what)} | {diag} |" for i, (_k, what, diag) in enumerate(checks, start=1))
    return "| N° | Contrôle | Piste si c'est le premier échec |\n|---|---|---|\n" + rows


def _messages_table() -> str:
    rows = "\n".join(f"| {message} | {diag} |" for message, diag in SHARE_MESSAGES)
    return "| Message (Windows, en français) | Piste |\n|---|---|\n" + rows


def _print_modes_table() -> str:
    rows = "\n".join(f"| **{mode}** | `{path}` | {note} | {when} |" for mode, path, note, when in PRINT_MODES)
    return "| Mode | Les postes s'y connectent par | À savoir | Adapté à |\n|---|---|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1))


# --- Cinq cas résolus (valeurs calculées) -----------------------------------------------------

# Cas 1 : groupe de travail, PC-1 partage Plans
C1_TREE = {
    "C:\\Partages": Folder("C:\\Partages", (Ace(LOCAL_ADMINS, "Contrôle total"),), inherit=False),
    "C:\\Partages\\Plans": Folder("C:\\Partages\\Plans", (Ace("Geometres", "Modification"),)),
}
C1_SHARES = {"Plans": Share("Plans", "C:\\Partages\\Plans", (Ace(AUTH_USERS, "Modifier"),))}
C1_GEOMETRE = Account("rita", "Rita (géomètre)", ("Geometres",))
C1_STAGIAIRE = Account("stagiaire", "Stagiaire", ())
C1_RITA = effective_access(C1_GEOMETRE, "C:\\Partages\\Plans", tree=C1_TREE, shares=C1_SHARES)
C1_OTHER = effective_access(C1_STAGIAIRE, "C:\\Partages\\Plans", tree=C1_TREE, shares=C1_SHARES)

# Cas 2 : le secrétariat ajouté dans NTFS, mais pas dans le partage Direction
DIRECTION = f"{SHARE_ROOT}\\Direction"
C2_TREE = {**NTFS_TREE, DIRECTION: Folder(DIRECTION, (*NTFS_TREE[DIRECTION].entries, Ace("G_Secretariat", "Lecture et exécution")))}
C2_BEFORE = effective_access(SAM, DIRECTION, tree=C2_TREE)
C2_LIMIT = limiting_layer(SAM, DIRECTION, tree=C2_TREE)
C2_NTFS = ntfs_level(SAM, DIRECTION, C2_TREE)
C2_SHARES_FIXED = {**SHARES, "Direction": Share("Direction", DIRECTION, (Ace(AUTH_USERS, "Modifier"),))}
C2_AFTER = effective_access(SAM, DIRECTION, tree=C2_TREE, shares=C2_SHARES_FIXED)
C2_DIAG = share_diagnosis(share_checks(AccessState(effective=C2_BEFORE, needed="Lecture")))

# Cas 4 : pilote d'imprimante refusé
C4_DIAG = print_diagnosis(print_checks(PrintState(driver_ok=False)))

# Cas 5 : partage Samba d'un atelier
C5_SHARE = SambaShare("atelier", "/srv/partages/atelier", ("atelier", "bureau"), read_only=True, write_list=("atelier",))
C5_USERS = (LinuxUser("hugo", ("atelier",)), LinuxUser("emma", ("bureau",)), LinuxUser("noe", ("livraison",)))
C5_RESULTS = {
    u.login: linux_effective(u, mode=0o2770, owner="root", group="atelier", acl={"bureau": "r-x"}, share=C5_SHARE)
    for u in C5_USERS
}

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Partager le dossier Plans d'un bureau de géomètres",
        (
            "Un bureau de cinq géomètres, sans serveur, travaille en groupe de travail. PC-1 doit partager le "
            "dossier C:\\Partages\\Plans : les géomètres modifient, le stagiaire de passage ne doit rien voir."
        ),
        (
            (
                "**Comptes** : sur PC-1, un compte local avec mot de passe par géomètre, réunis dans un groupe local "
                "Geometres (en groupe de travail, l'accès au partage se fait avec un compte de PC-1, voir "
                "[PR22](/uaa/ampcr-pratique-pr22))."
            ),
            (
                f"**Autorisations** : NTFS Geometres Modification, Administrateurs Contrôle total, Tout le monde retiré ; "
                f"partage « Plans » : {AUTH_USERS} Modifier. Résultat : géomètre → {C1_RITA.lower()}, compte hors du groupe → "
                f"{C1_OTHER.lower()}."
            ),
            (
                "**Réseau** : profil Privé, règle « Partage de fichiers et d'imprimantes » active ; test de "
                "`\\\\PC-1\\Plans` depuis PC-2 avec le compte de Rita (création, modification, suppression d'un fichier)."
            ),
        ),
        f"Partage \\\\PC-1\\Plans en service, accès par le groupe local Geometres ({C1_RITA.lower()}), aucun accès pour les autres comptes ; sauvegarde de PC-1 à prévoir.",
    ),
    (
        "Cas 2 — Ajouté dans l'onglet Sécurité, toujours refusé",
        (
            f"La secrétaire Sam doit lire le dossier Direction. Un collègue a ajouté G_Secretariat en Lecture et "
            f"exécution dans l'onglet Sécurité. Sam reçoit toujours « Accès refusé » sur \\\\{SERVER_NAME}\\Direction ; "
            "le ping et les autres partages fonctionnent."
        ),
        (
            (
                f"**Calcul** : NTFS → {C2_NTFS.lower()} ; partage Direction → seulement G_Direction : "
                f"{share_level(SAM, DIRECTION).lower()} pour Sam. Par le réseau, le plus restrictif : {C2_BEFORE.lower()} "
                f"({C2_LIMIT} limite)."
            ),
            f"**Piste** : {C2_DIAG.split(' :')[0].lower()} — le serveur répond et le compte est accepté (le ping et les autres partages fonctionnent).",
            (
                f"**Correction** : partage Direction → {AUTH_USERS} en Modifier, le détail restant dans NTFS ; "
                f"Sam obtient {C2_AFTER.lower()}, les autres comptes restent sans accès (aucune entrée NTFS)."
            ),
        ),
        f"Autorisation du partage Direction élargie aux utilisateurs authentifiés ; Sam en {C2_AFTER.lower()}, NTFS inchangé ; accès testé avec Sam et refusé à un compte du secrétariat non concerné.",
    ),
    (
        "Cas 3 — Le vieux NAS refuse les postes Windows 11",
        (
            "Un garage stocke ses factures sur un NAS de 2012. Depuis le remplacement des PC par des Windows 11, "
            "\\\\NAS\\factures ne s'ouvre plus ; le ping répond. Un message indique que le partage exige le protocole "
            "SMB1, obsolète et non sécurisé."
        ),
        (
            (
                "**Relevé** : le NAS ne parle que SMB version 1 ; Windows 11 n'installe plus SMB1 (désactivé depuis Windows 10 "
                "1709) et ses versions récentes refusent aussi par défaut l'accès « invité » sans compte."
            ),
            (
                "**Choix** : ne pas réactiver SMB1 (protocole vulnérable, utilisé par des rançongiciels) ; mettre à jour le "
                "micrologiciel du NAS pour activer SMB2/SMB3, sinon le remplacer."
            ),
            (
                "**Mise en service** : compte avec mot de passe sur le NAS pour chaque utilisateur (plus d'accès invité), "
                "partage testé depuis deux postes, copie des factures sauvegardée."
            ),
        ),
        "NAS mis à jour en SMB3 avec comptes nominatifs ; aucun poste n'a été affaibli (SMB1 et accès invité restent désactivés).",
    ),
    (
        "Cas 4 — Le nouveau poste ne peut pas installer l'imprimante",
        (
            f"Sur un poste neuf, une employée ajoute \\\\{SERVER_NAME}\\{NET_PRINTER}. Windows demande un compte "
            "administrateur pour installer le pilote. Les autres postes impriment ; l'imprimante est prête."
        ),
        (
            (
                f"**Piste** : {C4_DIAG.split(' :')[0].lower()} — depuis la mise à jour de sécurité d'août 2021, l'installation "
                "d'un pilote depuis un serveur d'impression est réservée par défaut aux administrateurs."
            ),
            (
                "**Correction** : le technicien installe la connexion avec son compte d'administration (ou la déploie par "
                "stratégie de groupe) ; l'employée reste utilisateur standard."
            ),
            "**À ne pas faire** : désactiver la protection ou donner les droits d'administration à l'employée.",
        ),
        f"Imprimante \\\\{SERVER_NAME}\\{NET_PRINTER} installée par le technicien, page de test imprimée par l'employée, protection des pilotes conservée.",
    ),
    (
        "Cas 5 — Un partage Samba pour l'atelier",
        (
            "Une menuiserie installe un serveur Linux. Le dossier /srv/partages/atelier doit être modifié par l'atelier "
            "(groupe atelier), lu par le bureau (groupe bureau), et fermé aux livreurs."
        ),
        (
            (
                "**Droits Unix** : `chown root:atelier atelier` ; `chmod 2770 atelier` → "
                f"`{mode_string(0o2770)}` (s : les fichiers créés gardent le groupe atelier) ; "
                "`setfacl -m g:bureau:r-x atelier` et `setfacl -d -m g:bureau:r-x atelier`."
            ),
            (
                "**Samba** : `[atelier]`, `path = /srv/partages/atelier`, `valid users = @atelier @bureau`, `read only = yes`, "
                "`write list = @atelier` ; `testparm` ; `sudo smbpasswd -a hugo` (mot de passe Samba de chaque utilisateur) ; "
                "`sudo systemctl reload smbd`."
            ),
            "**Résultat calculé** : " + ", ".join(f"{login} → {level.lower()}" for login, level in C5_RESULTS.items()) + ".",
        ),
        "Partage \\\\SRV-ATELIER\\atelier en service ; atelier en modification, bureau en lecture, livreurs refusés ; test avec un compte de chaque groupe.",
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant une demande de partage, une matrice de droits ou un relevé d'erreur, on attend de
toi une **configuration justifiée** et un **diagnostic prouvé**, pas une liste de sigles. Tu dois
savoir :

1. **partager un dossier** sous Windows (SMB) et écrire un **chemin UNC** `\\\\serveur\\partage` ;
2. régler la **découverte du réseau**, le **profil réseau**, le **pare-feu** et
   l'**authentification** ;
3. distinguer **permissions de partage** et **permissions NTFS** et calculer la **combinaison
   effective** ;
4. choisir entre **Lecture**, **Modification** et **Contrôle total**, et maîtriser
   l'**héritage** et les **groupes** ;
5. partager sous **Linux avec Samba**, lire les **droits rwx** et les **ACL** ;
6. **partager une imprimante** : file d'attente, accès local ou distant, pilotes, pare-feu,
   disponibilité de l'hôte ;
7. **diagnostiquer** : ping OK mais accès refusé, nom du serveur introuvable, droits
   insuffisants, imprimante hors connexion ;
8. **protéger les données** avec le **principe du moindre privilège**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigences travaillées dans ce cours

{_req("AP-25")}
{_req("AP-26")}
{_req("AP-27")}

Ce sont des exigences **officielles** (consignes, p. 6). Le partage entre deux PC a été vu en
[PR21](/uaa/ampcr-pratique-pr21), les comptes et les groupes en [PR22](/uaa/ampcr-pratique-pr22),
le dépannage réseau en [PR24](/uaa/ampcr-pratique-pr24), les commandes Linux en
[PR09](/uaa/ampcr-pratique-pr09) et l'UAC en [PR10](/uaa/ampcr-pratique-pr10).

## Lien avec la théorie

La théorie AMPCR présente les partages et les droits :
[MC33 Partage de ressources, comptes, droits et permissions](/uaa/ampcr-mc33) et
[MC10 Windows : administration et commandes essentielles](/uaa/ampcr-mc10).
Ce cours-ci est **pratique** : schémas, matrices de droits et relevés à analyser et à rédiger,
comme dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont quatre **schémas à
compléter**, des **matrices de droits** et des **relevés de commandes**), puis passe le
**mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les personnes, serveurs, dossiers et relevés de ce cours sont des **supports
> fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}) ; on reprend le domaine
> fictif de PR22. Les messages reprennent le format réel de Windows (en français), en version
> simplifiée. Les menus changent d'une version à l'autre : **la documentation de l'éditeur fait
> foi**. Aucun exercice n'est une question officielle ni une question déjà posée par le Jury.
"""


def _sharing() -> str:
    return f"""**Objectifs** : partager un dossier sous Windows et écrire le chemin réseau qui y mène.

## 1.1 SMB, le protocole des partages Windows

Un **partage** rend un dossier d'un ordinateur (le **serveur**) accessible aux autres par le
réseau. Windows utilise le protocole **SMB** (Server Message Block), sur le port **TCP
{SMB_PORT}**. Les versions actuelles sont SMB2 et SMB3 (chiffrement possible) ; **SMB1** est
obsolète, désactivé sur les Windows récents, et ne doit pas être réactivé.

Sur le serveur : clic droit sur le dossier → Propriétés → onglet **Partage** → **Partage
avancé** → « Partager ce dossier », **nom du partage** → **Autorisations**. En commande
(administrateur) : `net share Compta=D:\\Partages\\Compta /GRANT:"Utilisateurs authentifiés",CHANGE`
ou `New-SmbShare -Name Compta -Path D:\\Partages\\Compta -ChangeAccess "Utilisateurs authentifiés"`.
`net share` sans argument liste les partages du poste ; les partages se terminant par `$`
(`C$`, `ADMIN$`) sont des **partages administratifs** cachés, réservés aux administrateurs.

## 1.2 Le chemin UNC

{_fig(UNC_FIGURE)}

Un chemin **UNC** (Universal Naming Convention) s'écrit `\\\\serveur\\partage\\chemin`, par
exemple `{UNC_EXAMPLE}` ; le serveur peut être désigné par son **nom** ou par son **adresse IP**
(`{UNC_EXAMPLE_IP}`). Pour un usage quotidien, on associe une **lettre de lecteur** :
`net use {DRIVE_LETTER} \\\\{SERVER_NAME}\\Compta /persistent:yes`, ou « Connecter un lecteur
réseau » dans l'Explorateur. Le serveur de référence de ce cours ({SERVER_NAME}, {SERVER_IP})
partage quatre dossiers :

{_shares_table()}

{_fig(SHARE_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : dossier sur un volume NTFS → groupes → NTFS →
partage (nom court, autorisations) → pare-feu et profil → test par le chemin UNC → fiche.

**Erreur fréquente** : partager le disque C: entier ; un nom de partage avec espaces et accents
qu'on recopie mal ; confondre le nom du partage et le nom du dossier.

**À l'écrit** : « partage Compta de {SERVER_NAME} = D:\\Partages\\Compta ; accès
`\\\\{SERVER_NAME}\\Compta`, lecteur Z: ».

**Repère rapide** : **`\\\\serveur\\partage\\chemin` · SMB = TCP {SMB_PORT} · jamais SMB1 · jamais
C: entier**. Exercices liés : {_ex("E01", "E08")}.
"""


def _network() -> str:
    lines_ok = port_test_lines(SERVER_NAME, SERVER_IP, open_=True)
    return f"""**Objectifs** : régler le réseau pour que le partage soit trouvé et que l'utilisateur soit
reconnu.

## 2.1 Profil réseau, découverte et pare-feu

- **Profil réseau** : **Privé** (réseau de confiance) ou **Domaine** (poste membre d'un domaine
  qui voit son contrôleur) ; **Public** pour un réseau inconnu (café, gare). Sur le profil
  Public, le pare-feu bloque le partage de fichiers.
- **Découverte du réseau** : affiche les ordinateurs dans « Réseau » de l'Explorateur. Elle est
  **pratique, pas indispensable** : un chemin UNC tapé directement fonctionne sans elle.
- **Partage de fichiers et d'imprimantes** : règles du pare-feu Windows qui ouvrent le port
  TCP {SMB_PORT} sur le serveur (activées avec le partage, sur le profil Privé ou Domaine).
- Un **ping refusé** ne prouve pas que le serveur est éteint : le pare-feu peut bloquer l'écho
  ICMP. La preuve décisive pour un partage est le test du **port {SMB_PORT}** :

{_console(lines_ok)}

## 2.2 Authentification

Ouvrir un partage, c'est **s'identifier auprès du serveur** :

- en **domaine** ([PR22](/uaa/ampcr-pratique-pr22)), le compte du domaine de la session est
  présenté automatiquement : rien à taper ;
- en **groupe de travail**, il faut un **compte du serveur** (`SERVEUR\\nom`) **avec mot de
  passe** : Windows refuse par défaut à travers le réseau un compte sans mot de passe, et les
  versions récentes bloquent l'accès **invité** (sans compte) ;
- Windows n'utilise **qu'un compte par serveur** dans une même session (erreur 1219 sinon) ;
  `net use` liste les connexions, `cmdkey /list` les identifiants mémorisés.

**Procédure professionnelle (à rédiger)** : profil Privé ou Domaine → règle « Partage de
fichiers et d'imprimantes » → compte avec mot de passe (ou compte du domaine) → test du port
{SMB_PORT} → ouverture du partage.

**Erreur fréquente** : désactiver le pare-feu « pour que ça marche » ; laisser le serveur en
profil Public ; activer l'accès invité ou un compte sans mot de passe.

**À l'écrit** : « Test-NetConnection {SERVER_NAME} -Port {SMB_PORT} : True ; profil Domaine ;
accès avec DUPONT\\jmartin ».

**Repère rapide** : **profil Privé/Domaine · port {SMB_PORT} · un compte avec mot de passe ·
un compte par serveur**. Exercices liés : {_ex("E05", "E17")}.
"""


def _permissions() -> str:
    return f"""**Objectifs** : distinguer les deux ensembles d'autorisations et choisir le bon niveau.

## 3.1 Deux ensembles d'autorisations

Un dossier partagé est protégé par **deux barrières** indépendantes :

{_comparison_table()}

## 3.2 Lecture, Modification, Contrôle total

{_levels_table()}

Côté partage, les niveaux s'appellent **Lecture**, **Modifier** et **Contrôle total** ; côté
NTFS, on utilise surtout **Lecture et exécution** (Lecture), **Modification** et **Contrôle
total**. **Écriture** seule (créer sans pouvoir supprimer ni lire) est rare. Chaque case peut être
**Autoriser** ou **Refuser**.

Les autorisations NTFS du serveur de référence (Administrateurs : Contrôle total sur
`{SHARE_ROOT}`, hérité partout sauf là où l'héritage est désactivé) :

{_ntfs_table()}

Pour lire ou modifier en commande : `icacls D:\\Partages\\Compta` ;
`icacls D:\\Partages\\Compta /grant "DUPONT\\G_Compta:(OI)(CI)M"`.

{_fig(ICACLS_FIGURE)}

**Procédure professionnelle (à rédiger)** : lister qui doit lire, qui doit modifier → un groupe
par besoin → NTFS aux groupes (Modification ou Lecture et exécution) → Contrôle total aux seuls
administrateurs → retirer Tout le monde.

**Erreur fréquente** : donner Contrôle total à une équipe (elle peut changer les droits) ;
régler l'onglet Partage et oublier l'onglet Sécurité, ou l'inverse.

**À l'écrit** : « Compta : G_Compta Modification, G_Direction Lecture et exécution,
Administrateurs Contrôle total ».

**Repère rapide** : **deux barrières · Lecture < Modification < Contrôle total · Contrôle total =
administrateurs**. Exercices liés : {_ex("E04", "E12")}.
"""


def _effective() -> str:
    julie_remote = effective_access(JULIE, LAYERS_PATH)
    julie_local = effective_access(JULIE, LAYERS_PATH, remote=False)
    return f"""**Objectifs** : calculer l'accès réel d'un compte et organiser les droits par groupes et par
héritage.

## 4.1 La règle de combinaison

1. **Dans chaque barrière**, les autorisations des **groupes** du compte **se cumulent** : le
   droit le plus fort compte. Un **refus explicite** (posé sur le dossier) l'emporte sur toutes
   les autorisations ; une autorisation explicite l'emporte sur un refus **hérité**.
2. **Entre les deux barrières**, par le réseau, c'est **la plus restrictive** qui s'applique.
3. En **session ouverte sur le serveur** (localement ou par bureau à distance), le partage
   n'intervient pas : **NTFS seul**.

{_fig(LAYERS_FIGURE)}

Julie, sur Archives : partage Lecture, NTFS Modification → **{julie_remote}** par le réseau,
**{julie_local}** sur le serveur. Pratique courante (Microsoft) : autorisation de partage large
pour les utilisateurs authentifiés (Modifier ou Contrôle total) et **détail dans NTFS** ; régler
les deux de façon identique est aussi juste. Ce qui compte : savoir **laquelle limite**.

## 4.2 La matrice des droits

On résume tout dans une **matrice** comptes × dossiers, que l'on remet au client. Celle du
serveur de référence (calculée depuis les tableaux du chapitre 3) :

{_fig(MATRIX_FIGURE)}

{_matrix_table(ACCESS_MATRIX)}

## 4.3 Héritage et groupes

Un sous-dossier **hérite** des autorisations de son parent (marque **(I)** dans icacls). Pour un
dossier confidentiel (Paie), on **désactive l'héritage** (Sécurité → Avancé → Désactiver
l'héritage → convertir en autorisations explicites ; ou `icacls … /inheritance:d`), puis on
retire les groupes non autorisés.

{_fig(TREE_FIGURE)}

Comme en [PR22](/uaa/ampcr-pratique-pr22) : les droits vont aux **groupes**, les comptes dans les
groupes ; un ajout à un groupe compte à la **prochaine ouverture de session**.

**Procédure professionnelle (à rédiger)** : pour chaque compte et chaque dossier, droit du
partage → droit NTFS (posé + hérité) → le plus faible → matrice → test avec un compte de
chaque groupe.

**Erreur fréquente** : oublier que le sous-dossier hérite ; ajouter un refus au lieu de ne pas
accorder ; calculer en local un accès qui se fait par le réseau.

**À l'écrit** : « Claire sur Compta : partage Modification, NTFS Lecture → Lecture ; c'est NTFS
qui limite ».

**Repère rapide** : **cumul dans une barrière · refus explicite gagne · par le réseau la plus
restrictive · en local NTFS seul**. Exercices liés : {_ex("E09", "E12", "E13", "E14", "E15")}.
"""


def _linux() -> str:
    return f"""**Objectifs** : lire les droits Unix d'un dossier partagé par Samba et les ajuster.
(Complément du programme : Linux est cité comme alternative ; voir aussi
[PR09](/uaa/ampcr-pratique-pr09).)

## 5.1 Les droits rwx

`ls -ld` affiche le **type**, puis trois triplets **rwx** : **propriétaire**, **groupe**,
**autres**. Pour un dossier : **r** = lister, **w** = créer et supprimer, **x** = entrer
(indispensable pour r et w). Les classes **ne se cumulent pas** : la première qui correspond
(propriétaire, puis groupe, puis autres) s'applique. En octal : r = 4, w = 2, x = 1 ;
`chmod 2770` = setgid + rwx propriétaire + rwx groupe + rien pour les autres
(`{mode_string(0o2770)}`) ; `chmod 750` = `{mode_string(0o750)}`.

{_console(ls_lines())}

## 5.2 Les ACL

Une **ACL** (liste de contrôle d'accès) ajoute des entrées pour d'autres groupes ou
utilisateurs, signalées par un **+** après les droits : `setfacl -m g:direction:r-x compta`
(et `setfacl -d -m …` pour les fichiers créés ensuite), lecture avec `getfacl`.

{_console(getfacl_lines())}

## 5.3 Samba

**Samba** fait parler SMB à un serveur Linux : les postes Windows y accèdent par
`\\\\NAS-LIN\\{LX_SHARE.name}`. Partage dans `/etc/samba/smb.conf`, vérification par `testparm`,
rechargement par `sudo systemctl reload smbd` ; chaque utilisateur reçoit un mot de passe Samba
(`sudo smbpasswd -a marie`).

{_console(SMB_CONF_LINES)}

Comme sous Windows, **deux barrières** : la règle Samba (`valid users`, `read only`, `write
list`) et les droits Unix ; l'accès réel est le **plus restrictif** des deux.

{_fig(UNIX_FIGURE)}

**Procédure professionnelle (à rédiger)** : groupe Unix → dossier `chown root:groupe`,
`chmod 2770` → ACL pour les lecteurs → section smb.conf → `testparm` → `smbpasswd -a` →
rechargement → test depuis un poste Windows.

**Erreur fréquente** : `chmod 777` « pour que ça marche » ; modifier smb.conf sans les droits
Unix (ou l'inverse) ; oublier `smbpasswd -a`.

**À l'écrit** : « {LX_DIR} : {mode_string(0o2770, acl=True)} root compta + ACL direction r-x ;
Samba write list = @compta → {', '.join(f'{u.login} {linux_effective(u).lower()}' for u in LX_USERS)} ».

**Repère rapide** : **propriétaire / groupe / autres · r=4 w=2 x=1 · + = ACL · Samba ET Unix**.
Exercices liés : {_ex("E07", "E11", "E19")}.
"""


def _printers() -> str:
    return f"""**Objectifs** : partager une imprimante, choisir où se trouve la file d'attente et
connecter les postes.

## 6.1 Trois façons de rendre une imprimante disponible

{_print_modes_table()}

{_fig(PRINTER_FIGURE)}

## 6.2 File d'attente, accès local ou distant

- La **file d'attente** (service **Spouleur d'impression**) se trouve sur l'**hôte** qui partage :
  c'est lui qui reçoit les documents et les envoie à l'imprimante. Accès **local** : l'imprimante
  est branchée ou installée sur le poste lui-même ; accès **distant** : le poste envoie à la file
  d'un autre ordinateur (`\\\\{PRINT_HOST}\\{USB_PRINTER}`).
- Une imprimante **USB partagée** n'imprime que si son **poste hôte est allumé**.
- Une imprimante **réseau** garde une **adresse fixe** (ou une **réservation DHCP**) : le port
  d'impression (`IP_{NET_PRINTER_IP}`, port {RAW_PORT} ou IPP {IPP_PORT}) pointe vers elle.

## 6.3 Partager, pilotes, droits et pare-feu

- **Partager** : Paramètres → Bluetooth et appareils → Imprimantes et scanners → l'imprimante →
  **Propriétés de l'imprimante** → onglet **Partage** → « Partager cette imprimante », nom court.
- **Pilotes** : le poste client reçoit le pilote de l'hôte ; depuis la mise à jour de sécurité
  d'**août 2021**, cette installation demande **par défaut un administrateur**. On installe les
  pilotes **64 bits** du bon modèle.
- **Droits** (onglet Sécurité de l'imprimante) : **Imprimer**, **Gérer les documents**, **Gérer
  cette imprimante** ; par défaut, Tout le monde peut imprimer.
- **Pare-feu** : règle « Partage de fichiers et d'imprimantes » sur le profil Privé ou Domaine.

{_fig(PRINTER_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : installer sur l'hôte → adresse fixe → partager →
droits → pare-feu → connecter les postes → page de test.

**Erreur fréquente** : partager l'imprimante d'un poste qu'on éteint le soir ; laisser
l'imprimante réseau en DHCP sans réservation ; donner les droits d'administration à un
utilisateur pour installer un pilote.

**À l'écrit** : « {NET_PRINTER} : {NET_PRINTER_IP} réservée, partagée par {SERVER_NAME}
(`\\\\{SERVER_NAME}\\{NET_PRINTER}`), Imprimer pour G_Compta ».

**Repère rapide** : **hôte allumé · adresse fixe · pilote par un administrateur · Imprimer par
groupe**. Exercices liés : {_ex("E02", "E06", "E10")}.
"""


def _diagnosis() -> str:
    return f"""**Objectifs** : trouver pourquoi un partage ne s'ouvre pas, dans l'ordre, preuves à l'appui.

## 7.1 L'ordre des contrôles

Du plus général (le serveur répond-il ?) au plus particulier (les permissions) :

{_checks_table(SHARE_CHECKS)}

{_fig(SHARE_TREE_FIGURE)}

## 7.2 Les quatre situations du programme

- **Ping OK mais accès refusé** : le réseau et le serveur vont bien. « Accès refusé » prouve que
  le serveur a répondu et refusé : « Erreur système 5 » dès `net use` si c'est le **partage** qui
  refuse, refus à l'**ouverture** du dossier si c'est **NTFS** (la connexion au partage ne
  vérifie que ses propres autorisations). On calcule l'**accès effectif** (partage + NTFS) ; si le port {SMB_PORT} ne répond pas, c'est le **pare-feu** ou le **profil réseau**.
- **Nom du serveur introuvable** : on essaie **par l'adresse IP** (`\\\\{SERVER_IP}\\Compta`). Si
  ça marche, la panne est la **résolution du nom** (DNS du poste, [PR24](/uaa/ampcr-pratique-pr24)).
- **Droits insuffisants** : le partage s'ouvre mais l'enregistrement est refusé : quelle
  barrière limite ? groupe présent dans la session (`whoami /groups`) ?
- **Imprimante hors connexion** : voir le chapitre 8.

## 7.3 Lire les messages

{_messages_table()}

`net view \\\\{SERVER_NAME}` liste les partages réellement disponibles :

{_console(net_view_lines(SERVER_NAME, tuple(SHARES)))}

{_fig(TROUBLE_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : message exact → par l'adresse IP → par le nom →
port {SMB_PORT} → net view → compte → accès effectif → corriger → tester lecture et écriture →
consigner.

**Erreur fréquente** : donner Contrôle total à tout le monde alors que le nom n'est pas résolu ;
remplacer définitivement le nom par l'adresse IP (la panne DNS reste) ; désactiver le pare-feu.

**À l'écrit** : « `\\\\{SERVER_IP}\\Commun` OK, `\\\\{SERVER_NAME}\\Commun` KO → DNS du poste = box ;
DNS corrigé, nslookup {SERVER_NAME} = {SERVER_IP} ».

**Repère rapide** : **IP → nom → port {SMB_PORT} → partage → compte → droits**. Exercices liés :
{_ex("E03", "E05", "E15", "E16", "E17")}.
"""


def _printer_trouble() -> str:
    return f"""**Objectifs** : dépanner une imprimante partagée « hors connexion » ou qui n'imprime pas.

## 8.1 L'ordre des contrôles

{_checks_table(PRINT_CHECKS)}

{_fig(PRINT_TREE_FIGURE)}

## 8.2 Imprimante hors connexion

Causes les plus fréquentes : **poste hôte éteint** (imprimante USB partagée) ; imprimante
**éteinte ou en erreur** (papier, bourrage) ; imprimante réseau **qui a changé d'adresse** (DHCP
sans réservation) : le port pointe vers l'ancienne adresse. On compare l'adresse du port
(`Get-Printer`, propriétés → Ports) à celle de la **page de configuration** imprimée par
l'imprimante, puis on fixe l'adresse.

## 8.3 File d'attente bloquée

Un document en erreur bloque toute la file. On **arrête le spouleur**, on vide le dossier des
travaux en attente, on le **redémarre** (en invite administrateur) ; les documents en attente sont
perdus : on prévient les utilisateurs.

{_console(SPOOLER_LINES)}

**Procédure professionnelle (à rédiger)** : hôte allumé ? → imprimante prête, bonne adresse ? →
file et spouleur → pilote → droit Imprimer → page de test → consigner.

**Erreur fréquente** : réinstaller le pilote alors que l'adresse a changé ; supprimer et recréer
l'imprimante sur chaque poste au lieu de corriger le port une fois sur le serveur d'impression.

**À l'écrit** : « {NET_PRINTER} hors connexion : port {NET_PRINTER_IP}, imprimante en
192.168.20.117 (DHCP) ; réservation créée, page de test OK ».

**Repère rapide** : **hôte · imprimante et adresse · file · pilote · droit**. Exercices liés :
{_ex("E06", "E18")}.
"""


def _protection() -> str:
    return f"""**Objectifs** : protéger les données partagées et appliquer le moindre privilège.

## 9.1 Moindre privilège

Chaque compte reçoit **les seuls droits nécessaires**, **le temps nécessaire** : Lecture plutôt
que Modification si on ne fait que consulter, Contrôle total réservé aux administrateurs,
droits aux **groupes** revus aux arrivées et aux départs. On **n'accorde pas** plutôt que de
**refuser** : les refus se propagent par l'héritage et bloquent des personnes par erreur.

## 9.2 Protéger les données

- Retirer **{EVERYONE}** des dossiers sensibles ; jamais « {EVERYONE} : Contrôle total » à la fois
  sur le partage et dans NTFS.
- Ne pas partager un **disque entier** (C:) ; partager un **dossier dédié**.
- Données personnelles (clients, salaires) : dossier à accès limité, héritage désactivé si
  besoin.
- **Sauvegarde** régulière et **testée** du serveur (un rançongiciel chiffre tout ce que le
  compte infecté peut modifier : moins de droits = moins de dégâts).
- Pas de SMB1, pas d'accès invité, comptes nominatifs avec mot de passe.
- **Matrice des droits** écrite, remise au client, revue régulièrement.

**Procédure professionnelle (à rédiger)** : inventaire des dossiers sensibles → qui doit y
accéder et comment → groupes → autorisations minimales → sauvegarde → matrice écrite → revue.

**Erreur fréquente** : « tout le monde administrateur » ou « {EVERYONE} : Contrôle total » pour
éviter les appels ; partage du disque C: « pour dépanner » ; aucune sauvegarde.

**À l'écrit** : « Clients : G_Agents Modification, Administrateurs Contrôle total, {EVERYONE}
retiré ; sauvegarde quotidienne testée ; partage de C: supprimé ».

**Repère rapide** : **le minimum nécessaire · groupes · pas de {EVERYONE} · pas de disque
entier · sauvegarde testée**. Exercices liés : {_ex("E14", "E20")}.
"""


def _examples() -> str:
    blocks: list[str] = []
    for title, situation, steps, conclusion in CASES:
        lines = "\n".join(f"{i}. {_md(line)}" for i, line in enumerate(steps, start=1))
        blocks.append(
            f"""## {title}

**Situation.** {_md(situation)}

**Résolution.**

{lines}

**Conclusion rédigée.** « {_md(conclusion)} »
"""
        )
    return (
        "Cinq situations résolues pas à pas avec les règles du cours : partage en groupe de travail, deux "
        "barrières, protocole obsolète, pilote d'imprimante et partage Samba. Chaque conclusion s'appuie sur "
        "une preuve.\n\n" + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return f"""> **« {EVERYONE} : Contrôle total »** sur le partage **et** dans NTFS : n'importe qui peut tout effacer et changer les droits.

> **Régler un seul onglet** (Partage ou Sécurité) : par le réseau, la plus restrictive des deux l'emporte.

> **Oublier l'héritage** : un sous-dossier confidentiel créé dans un dossier commun est ouvert à tous.

> **Ajouter un refus** au lieu de ne pas accorder : il bloque aussi les autres groupes du compte.

> **Contrôle total à une équipe** : elle peut modifier les autorisations elle-même.

> **Désactiver le pare-feu** ou réactiver **SMB1** « pour que ça marche ».

> **Remplacer le nom par l'adresse IP** définitivement : la panne de nom reste cachée.

> **Partager le disque C: entier** au lieu d'un dossier dédié.

> **Imprimante USB partagée** sur un poste éteint le soir ; imprimante réseau **sans adresse fixe**.

> **Donner les droits d'administration** à un utilisateur pour installer un pilote.

> **`chmod 777`** sur un dossier Linux partagé.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (partager un dossier, une imprimante, dépanner un
accès), classements (droit minimal, piste d'un échec d'accès, piste d'une panne d'impression,
accès Samba), **quatre schémas à compléter** (chemin UNC, deux barrières, imprimantes, droits
Unix), **matrices de droits** à remplir ou à corriger et **relevés de commandes** à analyser
(ping, net use, Test-NetConnection, icacls, net share, Get-Printer, ls, getfacl, smb.conf).
Rédige ta réponse sur papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et
justifiée est acceptée. Ces mêmes exercices sont proposés dans
[S'entraîner](/uaa/{PR23_SLUG}/practice), avec correction après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR23_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (autorisations et relevés fictifs). **Aucune correction
n'est visible pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après
l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question (critères et
points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** L'**accès effectif calculé et justifié**, le **diagnostic
prouvé** par les relevés, la **correction minimale** respectant le moindre privilège — pas la
récitation de sigles. Une autre solution technique juste et justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Partage Windows** : SMB, TCP {SMB_PORT} ; `\\\\serveur\\partage\\chemin` (nom ou adresse IP) ;
  `net use Z: \\\\{SERVER_NAME}\\Compta` ; jamais SMB1, jamais le disque C: entier.
- **Réseau** : profil Privé ou Domaine ; règle « Partage de fichiers et d'imprimantes » ;
  découverte du réseau = affichage seulement ; compte avec mot de passe ; un compte par serveur.
- **Deux barrières** : partage (réseau seulement) et NTFS (local et réseau, héritage).
- **Niveaux** : {" < ".join(LEVELS)} ; Contrôle total = administrateurs.
- **Combinaison** : cumul des groupes dans une barrière ; refus explicite gagne ; par le réseau
  la plus restrictive ; en local NTFS seul.
- **Héritage** : (I) dans icacls ; désactiver pour un dossier confidentiel.
- **Linux** : propriétaire / groupe / autres, r=4 w=2 x=1 ; `+` = ACL ; Samba ET Unix ;
  `smbpasswd -a`, `testparm`.
- **Imprimantes** : hôte allumé, adresse fixe, file = spouleur, pilote par un administrateur,
  droit Imprimer.
- **Dépannage partage** : IP → nom → port {SMB_PORT} → partage → compte → droits (5 = droits,
  53 = chemin, 67 = nom du partage, 86 = mot de passe, 1219 = deux comptes).
- **Protection** : moindre privilège, groupes, pas de {EVERYONE}, sauvegarde testée, matrice écrite.

## Glossaire des termes employés

- **ACL (liste de contrôle d'accès)** : liste des comptes et groupes autorisés ou refusés sur un objet.
- **Autorisations du partage** : droits appliqués à l'accès par le réseau à un dossier partagé.
- **Autorisations NTFS** : droits du système de fichiers, valables en local et par le réseau.
- **Chemin UNC** : adresse réseau d'un partage, `\\\\serveur\\partage\\chemin`.
- **File d'attente** : liste des documents en attente d'impression, gérée par le spouleur de l'hôte.
- **Héritage** : transmission des autorisations d'un dossier à son contenu.
- **Matrice des droits** : tableau comptes × dossiers donnant l'accès de chacun.
- **Moindre privilège** : n'accorder que les droits nécessaires, le temps nécessaire.
- **Profil réseau** : Public, Privé ou Domaine ; il détermine les règles du pare-feu.
- **Samba** : logiciel qui permet à un serveur Linux de partager en SMB.
- **SMB** : protocole de partage de fichiers et d'imprimantes de Windows.
- **Spouleur d'impression** : service Windows qui gère les files d'attente.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « Partage de ressources (imprimantes, disques,
  répertoires…) » (AP-25), « Mise en partage sur un réseau informatique de documents et
  applications » (AP-26), « Les notions de droit et de permission » (AP-27). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Documentation Microsoft** : partage de fichiers SMB (`net share`, `New-SmbShare`,
  `net use`, `net view`, codes d'erreur système 5, 53, 67, 86, 1219), autorisations de partage
  et NTFS (combinaison, refus, héritage, `icacls`), SMB1 retiré des installations récentes et
  accès invité bloqué, règles de pare-feu « Partage de fichiers et d'imprimantes », profils
  réseau, partage d'imprimante et spouleur, installation des pilotes réservée aux
  administrateurs (mise à jour d'août 2021, KB5005652), `Test-NetConnection`, `Get-Printer`.
- **Linux et Samba** : pages de manuel `chmod`, `chown`, `ls`, `setfacl`/`getfacl`,
  `smb.conf` (`valid users`, `read only`, `write list`), `smbpasswd`, `testparm`.

Les valeurs et menus sont ceux de {WRITTEN_AT} ; ils évoluent selon les versions : **la
documentation de l'éditeur fait foi**. Les schémas, matrices, relevés et procédures du cours sont
**produits par programme** depuis des données **vérifiées par des tests automatiques** (accès
effectif partage + NTFS, héritage, droits Unix et Samba, piste d'un échec d'accès ou
d'impression) ; aucun schéma n'est tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite le partage de ressources, la mise en partage et les notions de droit et de
permission. Sont des **compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- Linux, Samba, droits rwx et ACL (alternative à Windows) ;
- les **conventions du cours** : serveur {SERVER_NAME} en {SERVER_IP}, imprimante réseau en
  {NET_PRINTER_IP}, groupes `G_…`, échelle {" < ".join(LEVELS)}, {USERS_DOMAIN} et
  {AUTH_USERS} ;
- l'ordre de dépannage d'un accès et d'une impression, la matrice des droits remise au client.

## Supports fictifs

Les personnes, serveurs, dossiers, entreprises et relevés de commandes de ce cours sont
**fictifs** et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucune
n'est une question officielle ou déjà posée par le Jury.
"""


def pr23_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR23 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR23 — 1. Partager un dossier sous Windows : SMB et chemins UNC", _sharing()),
        ("PR23 — 2. Profil réseau, découverte, pare-feu et authentification", _network()),
        ("PR23 — 3. Permissions de partage et permissions NTFS", _permissions()),
        ("PR23 — 4. Combinaison effective, héritage et groupes", _effective()),
        ("PR23 — 5. Linux : Samba, droits rwx et ACL", _linux()),
        ("PR23 — 6. Partager une imprimante : file d'attente, pilotes, accès local ou distant", _printers()),
        ("PR23 — 7. Diagnostiquer un accès : ping OK mais accès refusé, nom introuvable, droits", _diagnosis()),
        ("PR23 — 8. Imprimante hors connexion et file d'attente bloquée", _printer_trouble()),
        ("PR23 — 9. Protection des données et moindre privilège", _protection()),
        ("PR23 — Exemples : cinq situations résolues", _examples()),
        ("PR23 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR23 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR23 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR23 — Fiche mémo et glossaire", _memo()),
        ("PR23 — Sources et compléments pédagogiques", _sources()),
    ]

