"""Cours PR22 « Domaine, groupe de travail, comptes et groupes » — parcours AMPCR pratique écrite
(ticket #222).

Matière : intégralement celle du ticket #222 (groupe de travail et comptes locaux décentralisés ;
domaine Windows / Active Directory comme gestion centralisée : contrôleur de domaine, DNS,
authentification, identités utilisateurs et ordinateurs, jonction d'un poste, groupes et
stratégies ; domaine DNS et domaine d'administration ; comptes locaux et de domaine,
administrateur et utilisateur ; mots de passe, moindre privilège et désactivation d'un compte ;
dépannage de l'accès et de la connexion avec vérification réseau, heure, DNS et droits ;
organisations de 3 à 20 postes ; cinq cas résolus), découpée en blocs titrés (le titre pilote le
type de carte, `app.card_kind` : aucun titre de bloc théorique ne contient « examen »,
« source », « ressource », « exemple », « exercice », « méthode », « piège », « attention »,
« transfert » ni « mémo »).
Données et schémas : `app.v1.ampcr_pratique_pr22_figures` ; exercices et mini-examen :
`app.v1.ampcr_pratique_pr22_bank`. Les comptes locaux, l'UAC et `net user` viennent de PR10,
le réseau de PR20 et PR21, le dépannage réseau de PR24 (publiés, liens) ; les permissions de
partage détaillées sont l'objet de PR23 (cité sans lien tant qu'il n'est pas publié).
"""

from html import escape

from app.v1.ampcr_pratique_pr06_course import _exercise_card, _fig, _req
from app.v1.ampcr_pratique_pr22_bank import EXAM_ITEMS, EXAM_TOTAL_POINTS, PRACTICE_ITEMS
from app.v1.ampcr_pratique_pr22_figures import (
    ACCOUNT_COUNTS,
    ADMINS_DOMAIN,
    BARS_FIGURE,
    BOX_IP,
    COMPARISON,
    DC_FQDN,
    DC_IP,
    DC_NAME,
    DNS_DOMAIN,
    DOMAIN_FIGURE,
    GROUP_SHEET,
    GROUPS_FIGURE,
    JOIN_CONSOLE_FIGURE,
    JOIN_DIALOG_FIGURE,
    JOIN_PREREQUISITES,
    JOIN_PROC_FIGURE,
    LIFECYCLE_PROC_FIGURE,
    LOCAL_ADMINS,
    LOCAL_NESTING,
    LOCAL_USERS,
    LOGON_CHECKS,
    LOGON_MESSAGES,
    LOGON_TREE_FIGURE,
    MAX_CLOCK_SKEW_MIN,
    MAX_COMPUTER_NAME,
    MODEL_DOMAIN,
    MODEL_WG,
    NAMES_FIGURE,
    NETBIOS_DOMAIN,
    PROCEDURES,
    STATIC_FIGURES,
    TROUBLE_PROC_FIGURE,
    USERS_DOMAIN,
    WG_ACCOUNTS,
    WG_MAX_POSTES,
    WG_USERS,
    WORKGROUP_DEFAULT,
    WORKGROUP_FIGURE,
    WRITTEN_AT,
    Account,
    Organisation,
    Workstation,
    access_of,
    count_accounts,
    join_blockers,
    logon_checks,
    logon_diagnosis,
    logon_forms,
    nslookup_lines,
    recommend_model,
    secure_channel_lines,
    time_lines,
    workgroup_accounts,
)
from app.v1.ampcr_pratique_visuals import render_figure

PR22_TITLE = "Domaine, groupe de travail, comptes et groupes"
PR22_SLUG = "ampcr-pratique-pr22"

_SCHEMAS_BY_PATH = {path: figure for figure, path in STATIC_FIGURES}


def _card(number: int, item) -> str:
    """Carte d'exercice de PR06 ; un schéma à compléter est affiché (SVG) avant sa
    description textuelle."""
    html = _exercise_card(number, item, anchor_prefix="pr22")
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


# --- Tableaux (générés depuis les données vérifiées) -----------------------------------------


def _comparison_table() -> str:
    rows = "\n".join(f"| **{what}** | {wg} | {dom} |" for what, wg, dom in COMPARISON)
    return f"| | {MODEL_WG} | {MODEL_DOMAIN} |\n|---|---|---|\n" + rows


def _wg_table() -> str:
    rows = "\n".join(f"| {pc} | {', '.join(names)} | {len(names)} |" for pc, names in WG_ACCOUNTS.items())
    return "| Poste | Comptes locaux à créer | Nombre |\n|---|---|---|\n" + rows


def _counts_table() -> str:
    rows = "\n".join(f"| {n} | {wg} | {dom} |" for n, wg, dom in ACCOUNT_COUNTS)
    return "| Personnes | Comptes locaux (groupe de travail) | Comptes (domaine) |\n|---|---|---|\n" + rows


def _forms_table() -> str:
    forms = logon_forms("jmartin", computer="PC-03")
    who = {
        "local (ce poste)": "le poste lui-même",
        "local (poste nommé)": "le poste PC-03",
        "domaine (NetBIOS)": "le contrôleur de domaine",
        "domaine (UPN)": "le contrôleur de domaine",
    }
    rows = "\n".join(f"| {kind} | `{value}` | {who[kind]} |" for kind, value in forms.items())
    return "| Compte | On tape | Qui vérifie le mot de passe |\n|---|---|---|\n" + rows


def _prereq_table() -> str:
    rows = "\n".join(f"| **{what}** | {detail} |" for what, detail in JOIN_PREREQUISITES)
    return "| Prérequis | À vérifier |\n|---|---|\n" + rows


def _nesting_table() -> str:
    rows = "\n".join(f"| {NETBIOS_DOMAIN}\\{dom} | {local} | " + (
        "administre le poste" if local == LOCAL_ADMINS else "utilise le poste sans l'administrer") + " |"
        for dom, local in LOCAL_NESTING)
    return "| Groupe du domaine | Devient membre du groupe local | Effet sur chaque poste |\n|---|---|---|\n" + rows


def _group_sheet_table() -> str:
    rows = "\n".join(f"| **{group}** | {members} | {rights} |" for group, members, rights in GROUP_SHEET)
    return "| Groupe | Membres | Droits |\n|---|---|---|\n" + rows


def _checks_table() -> str:
    rows = "\n".join(f"| {i} | {what} | {diag} |" for i, (_k, what, diag) in enumerate(LOGON_CHECKS, start=1))
    return "| N° | Contrôle | Piste si c'est le premier échec |\n|---|---|---|\n" + rows


def _messages_table() -> str:
    rows = "\n".join(f"| {message} | {diag} |" for message, diag in LOGON_MESSAGES)
    return "| Message (Windows, en français) | Piste |\n|---|---|\n" + rows


def _procedures_list() -> str:
    return "\n".join(f"{i}. **{title}** ({len(steps)} étapes)" for i, (title, steps) in enumerate(PROCEDURES, start=1))


ORG_EXAMPLES: tuple[Organisation, ...] = (
    Organisation("Indépendant, 3 postes (bureau, portable, secrétaire)", 3),
    Organisation("Association, 6 postes, bénévoles fixes", 6),
    Organisation("Agence d'intérim, 8 postes, personnel qui tourne", 8, rotation=True),
    Organisation("Bureau d'études, 9 postes, règles de sécurité imposées", 9, policies=True),
    Organisation("Cabinet, 12 postes, chacun sur son poste", 12),
    Organisation("École, 20 postes, élèves différents à chaque cours", 20, rotation=True),
)


def _org_table() -> str:
    def why(o: Organisation) -> str:
        reasons = []
        if o.postes > WG_MAX_POSTES:
            reasons.append(f"plus de {WG_MAX_POSTES} postes")
        if o.rotation:
            reasons.append("arrivées et départs fréquents")
        if o.policies:
            reasons.append("règles à imposer à tous")
        if o.roaming:
            reasons.append("personnes qui changent de poste")
        return ", ".join(reasons) or "peu de postes, personnel stable, pas de règle commune"

    rows = "\n".join(f"| {o.label} | {recommend_model(o)} | {why(o)} |" for o in ORG_EXAMPLES)
    return "| Organisation | Conseil | Raison |\n|---|---|---|\n" + rows


# --- Cinq cas résolus (valeurs calculées) -----------------------------------------------------

C1_USERS = {"eva": ("PC-1",), "lucas": ("PC-2",), "nora": ("PC-3",), "yann": ("PC-4",), "rita": ("PC-5", "PC-1")}
C1_ACCOUNTS = workgroup_accounts(C1_USERS, "PC-1", tuple(C1_USERS))
C2_WS = Workstation("PC-14", "192.168.20.24", (DC_IP, BOX_IP))
C2_DIAG = logon_diagnosis(logon_checks(C2_WS, Account("emoreau", "Emma Moreau")))
C2_BLOCKERS = join_blockers(C2_WS)
C3_WS = Workstation("PC-06", "192.168.20.16", (DC_IP,), clock_offset_min=-7)
C3_DIAG = logon_diagnosis(logon_checks(C3_WS, Account("hpetit", "Hugo Petit")))
C4_ACCOUNT = Account("lbernard", "Luc Bernard", (USERS_DOMAIN, "G_Compta"), token_groups=(USERS_DOMAIN,))
C4_BEFORE = access_of(C4_ACCOUNT, "Compta")
C4_AFTER = access_of(Account("lbernard", "Luc Bernard", (USERS_DOMAIN, "G_Compta")), "Compta")
C5_ORG = Organisation("Fiduciaire de 11 postes, deux stagiaires par an", 11, rotation=True)

CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "Cas 1 — Un bureau de cinq personnes en groupe de travail",
        (
            "Un bureau de géomètres a cinq postes et aucun serveur. Chacun a son poste ; Rita travaille aussi "
            "sur PC-1, qui partage le dossier « Plans » ouvert par tout le monde. Le gérant veut savoir combien "
            "de comptes créer et si un serveur est utile."
        ),
        (
            f"**Modèle** : 5 postes, personnel stable, pas de règle commune → {recommend_model(Organisation('géomètres', 5))}.",
            "**Comptes** : " + " ; ".join(f"{pc} : {', '.join(n)}" for pc, n in C1_ACCOUNTS.items())
            + f" → {count_accounts(C1_ACCOUNTS)} comptes locaux, tous standard avec mot de passe.",
            "**Administration** : un compte d'administration distinct sur chaque poste, Invité désactivé ; fiche des comptes remise au gérant.",
        ),
        f"Groupe de travail conservé, {count_accounts(C1_ACCOUNTS)} comptes locaux nominatifs (dont {len(C1_ACCOUNTS['PC-1'])} sur PC-1, qui partage Plans), administration par un compte distinct ; domaine à revoir au-delà d'une dizaine de postes.",
    ),
    (
        "Cas 2 — La jonction réussit un jour sur deux",
        (
            "Dans une PME en domaine, PC-14 refuse parfois les connexions (« aucun serveur d'ouverture de "
            "session disponible ») ou n'applique plus les stratégies, puis tout revient. Le DHCP de la box donne "
            f"deux DNS : le contrôleur ({DC_IP}) puis, « en secours », la box ({BOX_IP})."
        ),
        (
            f"**Relevé** : ipconfig /all → DNS {', '.join(C2_WS.dns)} ; quand le contrôleur tarde à répondre, Windows passe au DNS suivant et garde la box un moment ; elle répond « Non-existent domain » pour {DNS_DOMAIN}.",
            f"**Cause** : piste {C2_DIAG.split(' :')[0]} ; un DNS qui ne connaît pas le domaine ne doit jamais figurer dans la liste d'un poste du domaine, même en second (prérequis manquant : {', '.join(C2_BLOCKERS)}).",
            f"**Correction** : DHCP réglé pour donner {DC_IP} seul ; le contrôleur relaie Internet ; ipconfig /renew, nslookup {DNS_DOMAIN} → {DC_IP}, jonction.",
        ),
        f"DNS des postes ramené au seul contrôleur {DC_IP} par le DHCP ; jonction et connexions stables, testées sur deux postes.",
    ),
    (
        "Cas 3 — Le lundi matin, un poste refuse tout le monde",
        (
            "Après un week-end de coupure de courant, PC-06 refuse les sessions du domaine (différence d'heure "
            "avec le serveur). Les mêmes comptes fonctionnent sur les autres postes ; le ping et le DNS sont bons."
        ),
        (
            "**Relevé** : net time affiche 09:12 sur le contrôleur, time /t 09:05 sur le poste : 7 minutes de retard.",
            f"**Cause** : écart supérieur à {MAX_CLOCK_SKEW_MIN} minutes → piste {C3_DIAG.split(' :')[0].lower()} ; pile de la carte mère faible.",
            "**Correction** : session locale, heure corrigée, w32tm /resync ; pile remplacée au prochain passage ; connexion du domaine réussie.",
        ),
        "Heure de PC-06 resynchronisée sur le domaine (7 minutes de retard), pile CR2032 à remplacer, connexion validée.",
    ),
    (
        "Cas 4 — Nouveau dans la comptabilité, toujours refusé",
        (
            "Luc rejoint la comptabilité. Le technicien l'ajoute à G_Compta. Une heure plus tard, Luc reçoit "
            "toujours « Accès refusé » sur le dossier Compta. Il n'a pas fermé sa session depuis le matin."
        ),
        (
            "**Relevé** : whoami /groups ne montre pas G_Compta.",
            f"**Cause** : les groupes sont lus à l'ouverture de session ; accès actuel : {C4_BEFORE.lower()}.",
            f"**Correction** : fermer et rouvrir la session ; whoami /groups montre G_Compta ; accès : {C4_AFTER.lower()}.",
        ),
        f"Session rouverte, G_Compta présent dans whoami /groups, dossier Compta en {C4_AFTER.lower()} ; aucun droit individuel ajouté.",
    ),
    (
        "Cas 5 — Passer une fiduciaire de 11 postes en domaine",
        (
            "Une fiduciaire de 11 postes en groupe de travail accueille deux stagiaires par an ; chaque arrivée "
            "demande de créer des comptes sur plusieurs postes et les départs sont oubliés. Elle achète un serveur."
        ),
        (
            f"**Modèle** : 11 postes et rotation → {recommend_model(C5_ORG)} ; serveur {DC_NAME} contrôleur + DNS, adresse fixe {DC_IP}, domaine {DNS_DOMAIN} ({NETBIOS_DOMAIN}).",
            "**Comptes et groupes** : un compte du domaine par personne, groupes métier G_…, compte adm- séparé pour le technicien ; Invité désactivé.",
            f"**Postes** : DNS = {DC_IP}, jonction poste par poste, session du domaine testée ; profils et fichiers des anciens comptes locaux recopiés.",
        ),
        f"Domaine {DNS_DOMAIN} en service, 11 postes joints et testés, fiche comptes et groupes remise ; stagiaires désormais créés et désactivés en un seul endroit.",
    ),
)

# =============================================================================================
# Sections du cours (titre du bloc, Markdown / HTML)
# =============================================================================================


def _objectives() -> str:
    return f"""## Ce que tu sauras faire, par écrit

L'épreuve pratique AMPCR se passe **uniquement par écrit** (consignes officielles 2026-2027/1,
p. 3). Devant la demande d'un client, une fiche de comptes ou un relevé de connexion, on attend
de toi un **choix justifié** et un **diagnostic prouvé**, pas une liste de sigles. Tu dois savoir :

1. expliquer le **groupe de travail** : comptes **locaux**, gestion **décentralisée** ;
2. expliquer le **domaine Windows / Active Directory** : gestion **centralisée**, **contrôleur
   de domaine**, **DNS**, **authentification**, identités des **utilisateurs** et des
   **ordinateurs** ;
3. distinguer **domaine DNS** et **domaine d'administration**, et écrire les **noms de
   connexion** ;
4. **joindre un poste** au domaine et vérifier le résultat ;
5. distinguer **compte local** et **compte du domaine**, **administrateur** et **utilisateur** ;
6. organiser les **groupes** et connaître les **stratégies de groupe** ;
7. gérer les **mots de passe**, appliquer le **moindre privilège**, **désactiver** un compte ;
8. **dépanner** une connexion ou un accès refusé : **réseau**, **DNS**, **heure**, **compte**,
   **droits** ;
9. **conseiller** une organisation de **3 à 20 postes**.

Ce cours contient **{len(PROCEDURES)} procédures illustrées** :

{_procedures_list()}

## Exigence travaillée dans ce cours

{_req("AP-24")}

C'est une exigence **officielle** (consignes, p. 6). Les comptes locaux, l'UAC et `net user` ont
été vus en [PR10](/uaa/ampcr-pratique-pr10) ; l'adressage et le DNS en
[PR20](/uaa/ampcr-pratique-pr20), le mini-réseau en [PR21](/uaa/ampcr-pratique-pr21), le
dépannage réseau en [PR24](/uaa/ampcr-pratique-pr24). Les partages et permissions détaillés
(PR23) seront approfondis dans leur cours, publié ensuite dans l'ordre du parcours.

## Lien avec la théorie

La théorie AMPCR présente les comptes et les droits :
[MC33 Partage de ressources, comptes, droits et permissions](/uaa/ampcr-mc33) et
[MC10 Windows : administration et commandes essentielles](/uaa/ampcr-mc10).
Ce cours-ci est **pratique** : schémas, fiches de comptes et relevés à analyser et à rédiger,
comme dans un dossier d'examen.

## Comment travailler ce cours

Lis les chapitres dans l'ordre : chacun donne ses **objectifs**, la **théorie**, la
**procédure professionnelle** à rédiger, l'**erreur fréquente**, ce qu'on attend **à l'écrit**
et un **repère rapide**, avec un renvoi vers les exercices liés. Étudie ensuite les **cinq cas
résolus**, fais les **{len(PRACTICE_ITEMS)} exercices corrigés** (dont quatre **schémas à
compléter**, des **fiches comptes et groupes** et des **relevés de commandes**), puis passe le
**mini-examen noté sur {EXAM_TOTAL_POINTS}** dans l'onglet « Examen blanc ».

> **Important —** les personnes, postes, domaines et relevés de ce cours sont des **supports
> fictifs** construits pour s'entraîner (rédaction : {WRITTEN_AT}) ; le domaine
> `{DNS_DOMAIN}` utilise l'extension `.example`, réservée aux exemples. Les messages reprennent
> le format réel de Windows (en français), en version simplifiée. Les menus changent d'une
> version à l'autre : **la documentation de l'éditeur fait foi**. Aucun exercice n'est une
> question officielle ni une question déjà posée par le Jury.
"""


def _workgroup() -> str:
    return f"""**Objectifs** : expliquer le fonctionnement d'un groupe de travail et compter les comptes
qu'il demande.

## 1.1 Chaque poste gère ses comptes

Dans un **groupe de travail** (par défaut `{WORKGROUP_DEFAULT}`), il n'y a **aucun serveur
d'identités** : chaque poste a sa **propre base de comptes locaux** et vérifie lui-même les
mots de passe. C'est une gestion **décentralisée**. Le nom du groupe de travail sert surtout à
**ranger** les postes dans l'affichage « Réseau » ; il ne donne **aucun droit**.

## 1.2 Conséquence : un compte sur chaque poste utilisé

Pour **ouvrir une session** sur un poste, ou **ouvrir le partage** d'un poste par le réseau, il
faut un **compte avec mot de passe sur CE poste** (un compte sans mot de passe est refusé par le
réseau). Exemple de référence : {len(WG_USERS)} personnes, Marc utilise PC-4 et PC-2, tout le
monde ouvre le dossier partagé par PC-1 :

{_fig(WORKGROUP_FIGURE)}

{_wg_table()}

Total : **{count_accounts(WG_ACCOUNTS)} comptes locaux pour {len(WG_USERS)} personnes**. Quand
une personne change son mot de passe, il faut le changer **sur chaque poste** où elle a un compte.

## 1.3 Le nombre de comptes grandit vite

{_fig(BARS_FIGURE)}

{_counts_table()}

**Procédure professionnelle (à rédiger)** : lister les personnes et les postes qu'elles
utilisent → lister les partages et qui les ouvre → créer sur chaque poste un compte local
standard avec mot de passe → un compte d'administration distinct → noter la fiche des comptes.

**Erreur fréquente** : croire qu'un même nom de groupe de travail suffit pour accéder aux
partages ; un seul compte « bureau » sans mot de passe pour tout le monde.

**À l'écrit** : « groupe de travail : comptes locaux de PC-1 = anne, paul, sara, marc (accès au
partage) ; 8 comptes au total ».

**Repère rapide** : **pas de serveur · chaque poste ses comptes · un compte sur chaque poste
utilisé**. Exercices liés : {_ex("E10", "E18")}.
"""


def _domain() -> str:
    return f"""**Objectifs** : expliquer ce que centralise un domaine Active Directory et le rôle de
chaque élément.

## 2.1 Gestion centralisée

Un **domaine Windows** repose sur **Active Directory** (AD DS) : un **annuaire** qui contient
les **comptes d'utilisateurs**, les **groupes**, les **comptes d'ordinateurs** et les **règles**
(stratégies). Il est tenu par un ou plusieurs **contrôleurs de domaine** (serveurs Windows
Server ; **deux** sont conseillés pour ne pas tout perdre si l'un tombe). Une seule base, valable
sur **tous les postes membres** : c'est une gestion **centralisée**.

{_comparison_table()}

## 2.2 Le contrôleur, le DNS et l'authentification

- Le **contrôleur** {DC_NAME} a une **adresse fixe** ({DC_IP}) : tout le monde doit le retrouver.
- Il est aussi **serveur DNS** du domaine : les postes trouvent le contrôleur **par le DNS**.
  Leur DNS doit donc être **le contrôleur** (pas la box) ; il relaie les noms d'Internet.
- L'**authentification** : à l'ouverture de session, le poste fait vérifier le nom et le mot de
  passe par le contrôleur (protocole **Kerberos**, qui exige des horloges à **{MAX_CLOCK_SKEW_MIN}
  minutes** près).
- **Identités** : chaque **personne** a un compte d'utilisateur ; chaque **poste** membre a,
  lui aussi, un **compte d'ordinateur** dans l'annuaire, avec un mot de passe qu'il change seul.
- La **box** reste la **passerelle** vers Internet.

{_fig(DOMAIN_FIGURE)}

**Procédure professionnelle (à rédiger)** : serveur à adresse fixe → rôle contrôleur de domaine
et DNS → nom du domaine → postes avec le contrôleur comme DNS → jonction → comptes et groupes.

**Erreur fréquente** : laisser la box comme DNS des postes ; un contrôleur en DHCP ; un seul
contrôleur sans sauvegarde.

**À l'écrit** : « DC01, contrôleur et DNS, {DC_IP} fixe ; postes : DNS {DC_IP}, passerelle
{BOX_IP} ».

**Repère rapide** : **un annuaire · un contrôleur à adresse fixe · DNS des postes = contrôleur ·
box = passerelle**. Exercices liés : {_ex("E08", "E04")}.
"""


def _names() -> str:
    return f"""**Objectifs** : distinguer domaine DNS et domaine d'administration et écrire correctement
un nom de connexion.

## 3.1 Deux sens du mot « domaine »

- Un **domaine DNS** est un **nom** dans le système de noms (ex. `dupont.example` pour un site
  web) : il sert à **trouver des machines**.
- Un **domaine Active Directory** est un **domaine d'administration** : un ensemble de comptes,
  de groupes, d'ordinateurs et de règles gérés par les contrôleurs. Il **s'appuie** sur le DNS et
  porte donc un **nom DNS** (`{DNS_DOMAIN}`), plus un **nom NetBIOS** court
  (`{NETBIOS_DOMAIN}`, {MAX_COMPUTER_NAME} caractères au plus).

Bon choix de nom : un **sous-domaine d'un nom public que l'entreprise possède**
(`{DNS_DOMAIN}` pour `dupont.example`) ; à éviter : `.local` (utilisé par la découverte
automatique des appareils) et exactement le nom du site public.

{_fig(NAMES_FIGURE)}

## 3.2 Les noms de connexion

Le **préfixe** dit **qui vérifie** le mot de passe :

{_forms_table()}

Le nom complet du contrôleur est `{DC_FQDN}`, celui d'un poste `pc-03.{DNS_DOMAIN}`.

**Procédure professionnelle (à rédiger)** : choisir le nom DNS (sous-domaine possédé) → nom
NetBIOS court → règle de nommage des comptes et des postes → fiche remise aux utilisateurs.

**Erreur fréquente** : taper `.\\jmartin` et s'étonner de ne pas retrouver ses fichiers du
domaine ; nommer le domaine comme le site web public.

**À l'écrit** : « compte du domaine : {NETBIOS_DOMAIN}\\jmartin ou jmartin@{DNS_DOMAIN} ; compte
local : .\\support ».

**Repère rapide** : **DOMAINE\\nom ou nom@domaine = domaine · .\\nom ou POSTE\\nom = local**.
Exercices liés : {_ex("E05", "E09", "E19")}.
"""


def _join() -> str:
    return f"""**Objectifs** : joindre un poste au domaine sans échec et prouver le résultat.

## 4.1 Prérequis

{_prereq_table()}

## 4.2 Joindre

Paramètres → Système → Informations système → **Domaine ou groupe de travail** (ou
`sysdm.cpl`) → Modifier → **Domaine** : `{DNS_DOMAIN}` → compte autorisé → « Bienvenue dans le
domaine » → **redémarrage**. En PowerShell administrateur :
`Add-Computer -DomainName {DNS_DOMAIN} -Credential {NETBIOS_DOMAIN}\\adm-tleroy -Restart`.
Le poste reçoit alors un **compte d'ordinateur** dans l'annuaire. (Un poste Linux peut aussi
rejoindre un domaine Active Directory, par exemple avec `realm join` : hors programme de ce cours.)

{_fig(JOIN_DIALOG_FIGURE)}

## 4.3 Vérifier

Après redémarrage, on ouvre une **session du domaine** et on contrôle : `whoami`,
`whoami /groups`, `gpresult /r` (stratégies appliquées), `nltest /sc_query:{DNS_DOMAIN}`
(relation avec le domaine).

{_fig(JOIN_CONSOLE_FIGURE)}

{_fig(JOIN_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : prérequis → DNS = contrôleur → ping et nslookup →
jonction → redémarrage → session du domaine et contrôles → fiche.

**Erreur fréquente** : tenter la jonction avec un poste Windows **Famille** ; DNS de la box ;
oublier le redémarrage ; joindre avec le compte quotidien.

**À l'écrit** : « PC-03 joint à {DNS_DOMAIN} par adm-tleroy ; whoami = dupont\\jmartin ;
gpresult /r : stratégies du domaine appliquées ».

**Repère rapide** : **Pro · nom unique · DNS = contrôleur · heure · compte autorisé ·
redémarrer · tester**. Exercices liés : {_ex("E01", "E12")}.
"""


def _accounts() -> str:
    return f"""**Objectifs** : choisir le bon type de compte pour chaque personne et chaque usage.

## 5.1 Local ou domaine

- **Compte local** : n'existe que sur **un poste** ; utile pour un groupe de travail et comme
  **compte de secours** d'un poste du domaine (il fonctionne sans contrôleur).
- **Compte du domaine** : dans l'annuaire ; **ouvre tous les postes** du domaine ; ses droits
  passent par ses **groupes**. Sur un portable, Windows garde en mémoire la dernière connexion
  réussie : on peut ouvrir sa session hors du réseau de l'entreprise.

## 5.2 Administrateur ou utilisateur

- **Utilisateur standard** : travaille, ne modifie pas le système (invite UAC, voir
  [PR10](/uaa/ampcr-pratique-pr10)).
- **Administrateur** : installe, configure, crée des comptes. Sur un poste du domaine, les
  **{ADMINS_DOMAIN}** sont automatiquement administrateurs (voir chapitre 6).
- **Comptes intégrés** : `Administrateur` (désactivé par défaut sur les postes Windows récents)
  et `Invité` (à laisser **désactivé**).

**Moindre privilège** : le technicien a **deux comptes** : `tleroy` (standard, pour le courriel
et le web) et `adm-tleroy` (administration seulement). Un compte **par personne** : jamais de
compte commun « accueil ».

**Procédure professionnelle (à rédiger)** : identifier la personne et son besoin → type
(domaine ou local) → standard par défaut → groupes → mot de passe initial → test.

**Erreur fréquente** : mettre tout le monde administrateur « pour éviter les appels » ; un
compte partagé par trois personnes (impossible de savoir qui a fait quoi).

**À l'écrit** : « Julie : compte du domaine jmartin, standard, groupe G_Compta ; Tom : tleroy
standard + adm-tleroy dans {ADMINS_DOMAIN} ».

**Repère rapide** : **un compte par personne · standard par défaut · admin séparé · Invité
désactivé**. Exercices liés : {_ex("E05", "E17", "E20")}.
"""


def _groups() -> str:
    return f"""**Objectifs** : organiser les droits par groupes et expliquer le rôle des stratégies de
groupe.

## 6.1 Les droits passent par les groupes

On donne les **droits aux groupes**, puis on place les **comptes dans les groupes** : une arrivée
ou un départ ne change que l'appartenance aux groupes. Groupes **métier** (convention du cours :
préfixe `G_`) et groupes **par défaut** du domaine ({USERS_DOMAIN}, {ADMINS_DOMAIN}, Ordinateurs
du domaine).

{_group_sheet_table()}

À la **jonction**, Windows ajoute deux groupes du domaine dans les groupes locaux du poste :

{_nesting_table()}

{_fig(GROUPS_FIGURE)}

Un ajout à un groupe ne compte qu'à la **prochaine ouverture de session** : les groupes sont lus
à la connexion (`whoami /groups` montre ceux de la session en cours).

## 6.2 Les stratégies de groupe (GPO)

Une **stratégie de groupe** est un ensemble de réglages appliqué **automatiquement** aux
utilisateurs ou aux ordinateurs d'une **unité d'organisation** (dossier de l'annuaire, par
exemple « Postes-Compta ») : règles de mot de passe et de verrouillage, écran de veille avec mot
de passe, lecteur réseau, interdiction des clés USB… On les gère dans la console « Gestion des
stratégies de groupe » ; sur le poste, `gpupdate /force` les recharge et `gpresult /r` montre
celles qui s'appliquent.

**Procédure professionnelle (à rédiger)** : lister les métiers → un groupe par métier → droits
des dossiers aux groupes → comptes dans les groupes → stratégies par unité d'organisation →
tester avec un compte de chaque groupe.

**Erreur fréquente** : donner un droit à une personne directement « pour aller vite » ; oublier
de rouvrir la session après un ajout ; modifier la stratégie par défaut du domaine au lieu d'en
créer une.

**À l'écrit** : « G_Compta : Modification sur Compta ; jmartin ajoutée à G_Compta ; session
rouverte, accès vérifié ».

**Repère rapide** : **droits → groupes → comptes · reconnexion après ajout · GPO par unité
d'organisation**. Exercices liés : {_ex("E11", "E16", "E17")}.
"""


def _security() -> str:
    return f"""**Objectifs** : gérer les mots de passe, appliquer le moindre privilège et traiter le départ
d'une personne.

## 7.1 Mots de passe

- **Personnel** et **jamais communiqué** ; le technicien ne le connaît pas.
- Mot de passe **initial temporaire**, remis à part, avec l'option **« L'utilisateur doit
  changer le mot de passe à la prochaine ouverture de session »**.
- **Long** plutôt que compliqué (une phrase de passe), **unique** ; la longueur minimale et le
  **verrouillage** après plusieurs essais faux se règlent par **stratégie**.
- Oubli → **réinitialisation** (après vérification de l'identité) ; essais faux → compte
  **verrouillé** → **déverrouillage** (sans changer le mot de passe si la personne le connaît).

## 7.2 Moindre privilège

Chaque compte a **les seuls droits nécessaires**, **le temps nécessaire** : utilisateurs
standard, administration avec un compte séparé, droits limités au dossier ou au poste concerné.

## 7.3 Départ : désactiver d'abord

Le jour du départ, on **désactive** le compte (et on le retire des groupes) : l'accès est coupé,
mais ses fichiers, son historique et ses droits restent récupérables. On **supprime plus tard**,
après sauvegarde des données et le délai prévu. Commandes : `net user nom /active:no` (compte
local), `Disable-ADAccount nom` (domaine) ; console « Utilisateurs et ordinateurs Active
Directory » : Désactiver le compte, Réinitialiser le mot de passe, Déverrouiller.

{_fig(LIFECYCLE_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : demande écrite → vérification d'identité → action
minimale (déverrouiller, réinitialiser, désactiver, groupe) → test → trace écrite.

**Erreur fréquente** : supprimer le compte le jour du départ (fichiers perdus) ; oublier les
départs (anciens comptes actifs) ; désactiver le verrouillage pour « éviter les appels ».

**À l'écrit** : « mvincent parti le 31/08 : compte désactivé, retiré de G_Compta ; données
sauvegardées ; suppression prévue après le délai ».

**Repère rapide** : **personnel · temporaire à l'arrivée · déverrouiller ≠ réinitialiser ·
désactiver puis supprimer**. Exercices liés : {_ex("E02", "E07", "E15", "E20")}.
"""


def _troubleshooting() -> str:
    ok_dns = nslookup_lines(DC_IP, knows_domain=True)
    return f"""**Objectifs** : dépanner une ouverture de session ou un accès refusé dans l'ordre, preuves
à l'appui.

## 8.1 L'ordre des contrôles

On commence par le **plus général** (le poste joint-il le contrôleur ?) et on finit par le plus
particulier (les droits du compte) :

{_checks_table()}

{_fig(LOGON_TREE_FIGURE)}

## 8.2 Lire les messages

{_messages_table()}

Un **seul compte** touché sur tous les postes → le **compte** ; **un seul poste** touché pour
tous les comptes → le **poste** (réseau, DNS, heure, relation d'approbation).

## 8.3 Les relevés utiles

DNS correct : le contrôleur répond pour le domaine.

{_console(ok_dns)}

Heure : comparer avec le contrôleur (écart de {MAX_CLOCK_SKEW_MIN} minutes au plus), puis
`w32tm /resync`.

{_console(time_lines(Workstation("PC-05", "192.168.20.15", (DC_IP,), clock_offset_min=9)))}

Relation d'approbation rompue (poste restauré depuis une ancienne image, compte d'ordinateur
supprimé) : réparer avec `Test-ComputerSecureChannel -Repair` depuis une session locale
d'administration, ou sortir du domaine puis le rejoindre.

{_console(secure_channel_lines(False))}

{_fig(TROUBLE_PROC_FIGURE)}

**Procédure professionnelle (à rédiger)** : message exact → un poste ou un compte ? → contrôles
dans l'ordre → s'arrêter au premier échec → corriger → tester une connexion → consigner.

**Erreur fréquente** : réinitialiser le mot de passe alors que le DNS est faux ; sortir le poste
du domaine sans compte local de secours connu ; ajouter un droit individuel au lieu de rouvrir
la session.

**À l'écrit** : « PC-05 : 9 minutes d'écart avec DC01 → Kerberos refuse ; w32tm /resync,
connexion du domaine réussie ».

**Repère rapide** : **réseau → DNS → heure → poste → compte → droits**. Exercices liés :
{_ex("E03", "E06", "E12", "E13", "E14", "E15", "E16")}.
"""


def _choosing() -> str:
    return f"""**Objectifs** : conseiller une organisation de 3 à 20 postes et justifier le choix.

## 9.1 Le repère du cours

Un **groupe de travail** convient jusqu'à **une dizaine de postes** ({WG_MAX_POSTES} au plus)
quand chacun reste sur son poste, que le personnel est stable et qu'aucune règle ne doit être
imposée à tous. Au-delà, ou dès qu'il faut **gérer de façon centralisée** (arrivées et départs
fréquents, personnes qui changent de poste, règles communes), on conseille un **domaine**, avec
au moins un serveur contrôleur. Ce repère est une **convention du cours**, pas une limite
technique : on justifie toujours par la situation.

{_org_table()}

## 9.2 Ce qu'on écrit au client

Le **modèle** conseillé et ses **raisons**, le **matériel** (serveur ou non), la **fiche des
comptes et des groupes**, les **règles** (mots de passe, moindre privilège, départs) et le
**coût** (serveur, licences, temps de gestion).

**Procédure professionnelle (à rédiger)** : compter postes et personnes → repérer rotation,
itinérance et règles → choisir le modèle → fiche comptes et groupes → plan de mise en place.

**Erreur fréquente** : conseiller un domaine à trois postes stables sans budget serveur ; garder
un groupe de travail à vingt postes « parce que ça marche ».

**À l'écrit** : « 14 postes et remplaçants qui changent de poste : domaine ; un compte par
personne valable partout, désactivation en un seul endroit ».

**Repère rapide** : **≤ {WG_MAX_POSTES} postes stables → groupe de travail · plus, ou rotation,
itinérance, règles → domaine**. Exercices liés : {_ex("E04", "E17")}.
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
        "Cinq situations résolues pas à pas avec les règles du cours : groupe de travail, DNS, heure, "
        "groupes et passage en domaine. Chaque conclusion s'appuie sur une preuve.\n\n" + "\n".join(blocks)
    )


def _pitfalls() -> str:
    return f"""> **Box comme DNS des postes du domaine** : jonction et connexions impossibles ou aléatoires.

> **Croire que le nom du groupe de travail donne des droits** : il ne sert qu'à l'affichage.

> **Compte commun** pour plusieurs personnes : impossible de savoir qui a fait quoi.

> **Utilisateurs dans {ADMINS_DOMAIN}** : tout le domaine exposé à une erreur ou à un logiciel malveillant.

> **Supprimer un compte le jour du départ** : fichiers et historique perdus ; on désactive d'abord.

> **Oublier de rouvrir la session** après un ajout à un groupe.

> **Réinitialiser un mot de passe** quand le compte est seulement verrouillé, ou quand la panne est le DNS.

> **Horloge décalée de plus de {MAX_CLOCK_SKEW_MIN} minutes** : authentification refusée.

> **Joindre un poste Windows Famille** : impossible, il faut l'édition Professionnel.

> **Nommer le domaine en .local** ou exactement comme le site public.

> **Sortir un poste du domaine** sans connaître un compte local d'administration.
"""


def _exercises_intro() -> str:
    return f"""{len(PRACTICE_ITEMS)} exercices corrigés : remises en ordre (jonction, vie d'un compte, dépannage),
classements (groupe de travail ou domaine, compte local ou du domaine, piste d'un échec de
connexion, action sur un compte), **quatre schémas à compléter** (domaine, noms, groupe de
travail, groupes), **relevés de commandes** à analyser (ipconfig, nslookup, net time, nltest,
net user, whoami) et **fiches comptes et groupes** à rédiger ou auditer. Rédige ta réponse sur
papier **avant** d'ouvrir le corrigé ; toute réponse équivalente et justifiée est acceptée. Ces
mêmes exercices sont proposés dans [S'entraîner](/uaa/{PR22_SLUG}/practice), avec correction
après envoi.

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
    return f"""Le mini-examen se passe dans l'onglet [Examen blanc](/uaa/{PR22_SLUG}/exam) : **10 questions à réponse
libre**, chacune notée sur **2 points**, soit une note sur **{EXAM_TOTAL_POINTS}**. Les
questions ne figurent pas dans ce cours.

| N° | Thème | Type | Points |
|---|---|---|---|
{rows}

**Déroulement.** Chaque question est une situation complète : toutes les données nécessaires
sont dans l'énoncé et ses documents (configurations et relevés fictifs). **Aucune correction
n'est visible pendant la passation** ; tes réponses sont enregistrées au fur et à mesure. Après
l'envoi, chaque réponse est corrigée selon le **barème analytique** de la question (critères et
points), puis tu vois ta note sur {EXAM_TOTAL_POINTS}, le corrigé et le barème.

**Ce que valorise le barème.** Le **choix justifié** (modèle, type de compte, groupe), le
**diagnostic prouvé** par les relevés et la **procédure** — pas la récitation de sigles. Une
autre solution technique juste et justifiée est acceptée.

**Nature de la correction.** Les réponses rédigées reçoivent une **proposition de correction
automatique** (assistée par IA) appuyée sur le barème : c'est un repère d'entraînement, pas une
note officielle ; en cas de doute, compare ta réponse au corrigé.
"""


def _memo() -> str:
    return f"""## Mémo

- **Groupe de travail** : pas de serveur ; chaque poste ses comptes locaux ; un compte (avec
  mot de passe) sur chaque poste utilisé et sur le poste qui partage.
- **Domaine** : annuaire Active Directory sur un contrôleur (adresse fixe, DNS) ; un compte par
  personne pour tous les postes ; comptes d'ordinateurs ; stratégies de groupe.
- **DNS des postes** = contrôleur ({DC_IP}) ; **passerelle** = box ({BOX_IP}).
- **Noms** : {DNS_DOMAIN} (DNS) · {NETBIOS_DOMAIN} (NetBIOS) · {NETBIOS_DOMAIN}\\jmartin ou
  jmartin@{DNS_DOMAIN} (domaine) · .\\support (local).
- **Jonction** : Pro · nom unique · DNS · heure · compte autorisé · redémarrage · whoami.
- **Groupes** : droits → groupes → comptes ; {ADMINS_DOMAIN} → {LOCAL_ADMINS} ; {USERS_DOMAIN} →
  {LOCAL_USERS} ; reconnexion après un ajout.
- **Sécurité** : un compte par personne · standard par défaut · admin séparé (adm-) · Invité
  désactivé · mot de passe temporaire à changer · désactiver puis supprimer.
- **Dépannage** : réseau → DNS → heure ({MAX_CLOCK_SKEW_MIN} min) → poste (relation
  d'approbation) → compte → droits.
- **Choix** : ≤ {WG_MAX_POSTES} postes stables → groupe de travail ; sinon domaine.

## Glossaire des termes employés

- **Active Directory (AD DS)** : annuaire Microsoft des comptes, groupes, ordinateurs et règles d'un domaine.
- **Compte d'ordinateur** : identité d'un poste membre du domaine, avec son propre mot de passe.
- **Contrôleur de domaine** : serveur qui tient l'annuaire et vérifie les connexions.
- **Domaine d'administration** : ensemble de comptes et de postes gérés depuis un point central.
- **Domaine DNS** : nom dans le système de noms, utilisé pour trouver des machines.
- **Groupe de travail** : postes en réseau sans gestion centralisée des comptes.
- **Kerberos** : protocole d'authentification du domaine, sensible à l'heure.
- **Moindre privilège** : n'accorder que les droits nécessaires, le temps nécessaire.
- **NetBIOS (nom)** : nom court d'un domaine ou d'un poste (15 caractères au plus).
- **Relation d'approbation** : lien de confiance entre un poste et son domaine.
- **Stratégie de groupe (GPO)** : réglages appliqués automatiquement aux comptes ou postes d'une unité d'organisation.
- **Unité d'organisation** : dossier de l'annuaire qui range comptes et postes.
- **UPN** : nom de connexion sous la forme nom@domaine.
"""


def _sources() -> str:
    return f"""## Sources utilisées

- **Consignes officielles** de l'épreuve pratique AMPCR, cycle 2026-2027/1 (Jurys de la
  Fédération Wallonie-Bruxelles), p. 6 : « Notions de domaine, groupe de travail, comptes
  utilisateurs et groupes d'utilisateurs » (AP-24). Copie versionnée :
  [docs/references-officielles/ampcr/2026-2027-1](https://github.com/ReC82/jury-central/tree/develop/docs/references-officielles/ampcr/2026-2027-1).
  Programme officiel n° 345/2007/249 (option AMPCR).
- **Documentation Microsoft** : Active Directory Domain Services, contrôleurs de domaine et DNS,
  jonction d'un ordinateur à un domaine (`Add-Computer`, éditions éligibles), groupes par défaut
  ({ADMINS_DOMAIN}, {USERS_DOMAIN}) et leur ajout aux groupes locaux, stratégie Kerberos
  (tolérance d'horloge de {MAX_CLOCK_SKEW_MIN} minutes), stratégies de groupe (`gpupdate`,
  `gpresult`), `Test-ComputerSecureChannel`, `nltest`, `net user`, `whoami`, `w32tm`.
- **RFC 2606 / RFC 6761** : noms réservés aux exemples (`.example`), utilisés pour le domaine
  fictif du cours ; **RFC 6762** : usage de `.local` par la découverte automatique (mDNS).

Les valeurs et menus sont ceux de {WRITTEN_AT} ; ils évoluent selon les versions : **la
documentation de l'éditeur fait foi**. Les schémas, fiches, relevés et procédures du cours sont
**produits par programme** depuis des données **vérifiées par des tests automatiques** (comptes
à créer, choix du modèle, erreurs d'une fiche, piste d'un échec de connexion) ; aucun schéma n'est
tiré d'une image générée ni d'une photographie.

## Compléments pédagogiques (non imposés par la liste officielle)

La p. 6 cite les notions de domaine, groupe de travail, comptes et groupes. Sont des
**compléments**, signalés comme tels, utiles pour traiter un dossier écrit :

- les **conventions du cours** : réseau 192.168.20.0/24, contrôleur en .10, box en .254,
  groupes `G_…`, comptes d'administration `adm-…`, repère « une dizaine de postes » ;
- les stratégies de groupe, la relation d'approbation et l'ordre de dépannage d'une connexion ;
- la fiche des comptes et des groupes remise au client.

## Supports fictifs

Les personnes, postes, domaines, entreprises et relevés de commandes de ce cours sont
**fictifs** et reconstitués pour l'entraînement ; ils ne décrivent aucun client réel. Aucune
n'est une question officielle ou déjà posée par le Jury.
"""


def pr22_course_sections() -> list[tuple[str, str]]:
    """Blocs du cours (titre, contenu), dans l'ordre d'affichage."""
    return [
        ("PR22 — Objectifs et place dans l'épreuve", _objectives()),
        ("PR22 — 1. Groupe de travail : comptes locaux et gestion décentralisée", _workgroup()),
        ("PR22 — 2. Domaine Active Directory : contrôleur, DNS et authentification", _domain()),
        ("PR22 — 3. Domaine DNS, domaine d'administration et noms de connexion", _names()),
        ("PR22 — 4. Joindre un poste au domaine", _join()),
        ("PR22 — 5. Comptes locaux ou du domaine, administrateur ou utilisateur", _accounts()),
        ("PR22 — 6. Groupes et stratégies de groupe", _groups()),
        ("PR22 — 7. Mots de passe, moindre privilège et désactivation d'un compte", _security()),
        ("PR22 — 8. Dépanner l'accès : réseau, DNS, heure, compte et droits", _troubleshooting()),
        ("PR22 — 9. Groupe de travail ou domaine : organisations de 3 à 20 postes", _choosing()),
        ("PR22 — Exemples : cinq situations résolues", _examples()),
        ("PR22 — Pièges et erreurs fréquentes", _pitfalls()),
        (f"PR22 — Exercices corrigés ({len(PRACTICE_ITEMS)}) et leurs corrigés", _exercises_intro()),
        ("PR22 — Mini-examen noté sur 20 : mode d'emploi", _mini_exam()),
        ("PR22 — Fiche mémo et glossaire", _memo()),
        ("PR22 — Sources et compléments pédagogiques", _sources()),
    ]
