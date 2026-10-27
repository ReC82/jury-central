"""PR22 « Domaine, groupe de travail, comptes et groupes » — exercices corrigés et mini-examen
(ticket #222).

Même organisation que PR21 (`app.v1.ampcr_pratique_pr21_bank`) : type d'item de PR06, petits
constructeurs de PR04.
- `PRACTICE_ITEMS` : 20 exercices corrigés affichés dans le cours (corrigé replié) et proposés
  dans « S'entraîner » — remises en ordre (jonction, cycle de vie d'un compte, dépannage),
  classements (groupe de travail ou domaine, compte local ou de domaine, piste d'une ouverture
  de session, action sur un compte), **quatre schémas à compléter** (domaine, noms, groupe de
  travail, groupes, servis en SVG), **relevés de commandes** à analyser (ipconfig, nslookup,
  net time, nltest, net user, whoami), **fiches comptes et groupes** à rédiger ou auditer ;
- `EXAM_ITEMS` : les 10 questions du mini-examen noté /20 (2 points chacune), réponses libres,
  uniquement dans « Examen blanc », jamais affichées dans le cours.

Les situations, personnes, postes et domaines sont **fictifs** ; les comptes à créer, les
recommandations, les erreurs de fiches et les pistes de diagnostic des énoncés et des corrigés
viennent des fonctions de `app.v1.ampcr_pratique_pr22_figures` (mêmes données que les schémas).
"""

from app.v1.ampcr_pratique_format import ExerciseDocument, validate_exercise
from app.v1.ampcr_pratique_pr04_bank import _c, _console, _labels, _shuffled_ordering, _table
from app.v1.ampcr_pratique_pr06_bank import (
    USAGE_EXAM,
    USAGE_PRACTICE,
    Classification,
    PR06Item,
)
from app.v1.ampcr_pratique_pr22_figures import (
    ACCOUNT_ACTION_DISABLE,
    ACCOUNT_ACTION_GROUP,
    ACCOUNT_ACTION_RESET,
    ACCOUNT_ACTION_UNLOCK,
    ACCOUNT_ACTIONS,
    ADMINS_DOMAIN,
    BOX_IP,
    D_ACCOUNT,
    D_DNS,
    D_NET,
    D_RIGHTS,
    D_TIME,
    D_TRUST,
    DC_IP,
    DIAGNOSES,
    DNS_DOMAIN,
    DOMAIN_BLANK_ANSWERS,
    ERR_ADMIN,
    ERR_GUEST,
    ERR_LEFT,
    ERR_SHARED,
    GROUPS_BLANK_ANSWERS,
    JOIN_STEPS,
    LIFECYCLE_STEPS,
    MAX_CLOCK_SKEW_MIN,
    MODEL_DOMAIN,
    MODEL_WG,
    MODELS,
    NAMES_BLANK_ANSWERS,
    NETBIOS_DOMAIN,
    SCOPE_DOMAIN,
    SCOPE_LOCAL,
    SCOPES,
    STATIC_BY_KEY,
    TROUBLE_STEPS,
    USERS_DOMAIN,
    WG_ACCOUNTS,
    WG_BLANK_ANSWERS,
    Account,
    AccountRow,
    Organisation,
    Workstation,
    access_of,
    account_errors,
    account_scope,
    count_accounts,
    first_failure,
    ipconfig_dns_lines,
    join_blockers,
    logon_checks,
    logon_diagnosis,
    net_user_lines,
    nslookup_lines,
    recommend_model,
    secure_channel_lines,
    time_lines,
    whoami_groups_lines,
    workgroup_accounts,
)

PR22_CODE = "PR22"

KIND_ORDER = "ordonnancement"
KIND_MODEL = "groupe de travail ou domaine"
KIND_ACCOUNT = "comptes et groupes"
KIND_SCHEMA = "schéma à compléter"
KIND_DIAG = "diagnostic sur relevés de commandes"
KIND_SHEET = "fiche comptes et groupes"

# Exigence du cours (matrice #192, audit #236) : chaque item la cite.
REQ = frozenset({"AP-24"})


def _schema(key: str, title: str) -> ExerciseDocument:
    """Schéma à compléter : fichier SVG statique + description textuelle complète."""
    figure, path = STATIC_BY_KEY[key]
    return ExerciseDocument(title=title, kind="schéma", content_text=figure.alt, image=path)


# --- Données calculées réutilisées dans les énoncés et les corrigés --------------------------

E01_STEPS = _labels(JOIN_STEPS)
E02_STEPS = _labels(LIFECYCLE_STEPS)
E03_STEPS = _labels(TROUBLE_STEPS)

E04_CASES: tuple[Organisation, ...] = (
    Organisation("Cabinet de 14 postes, une secrétaire volante qui change de bureau chaque jour", 14, roaming=True),
    Organisation("Indépendante avec 3 PC (bureau, portable, PC de la secrétaire), personne ne change", 3),
    Organisation("Association de 5 postes, bénévoles fixes, aucune règle imposée", 5),
    Organisation("Agence d'intérim de 8 postes, intérimaires qui arrivent et partent chaque semaine", 8, rotation=True),
    Organisation("École de 20 postes en salle informatique, élèves différents à chaque cours", 20, rotation=True),
    Organisation("Garage de 4 postes, mêmes mécaniciens depuis des années", 4),
    Organisation("Bureau d'études de 9 postes devant imposer le verrouillage des sessions et des mots de passe longs", 9, policies=True),
)
E04_ANSWERS = tuple(recommend_model(o) for o in E04_CASES)
E04_CORRECT = tuple(MODELS.index(a) for a in E04_ANSWERS)

E05_NAMES: tuple[str, ...] = (
    f"{NETBIOS_DOMAIN}\\jmartin",
    ".\\support",
    f"jmartin@{DNS_DOMAIN}",
    "PC-03\\support",
    f"{NETBIOS_DOMAIN}\\adm-tleroy",
    "PC-ACCUEIL\\accueil",
    f"adm-tleroy@{DNS_DOMAIN}",
)
E05_ANSWERS = tuple(account_scope(n) for n in E05_NAMES)
E05_CORRECT = tuple(SCOPES.index(a) for a in E05_ANSWERS)

E06_CATEGORIES = DIAGNOSES
E06_CASES: tuple[tuple[str, str], ...] = (
    ("« Votre compte a été désactivé. Contactez votre administrateur système. »", "compte"),
    ("« Il n'existe actuellement aucun serveur d'ouverture de session disponible » ; câble du poste débranché", "reseau"),
    (f"Jonction refusée : le contrôleur de {DNS_DOMAIN} n'a pas pu être contacté ; DNS du poste = box", "dns"),
    ("Le poste avance de 9 minutes sur le contrôleur ; erreur Kerberos à l'ouverture de session", "heure"),
    ("« La relation d'approbation entre cette station de travail et le domaine principal a échoué »", "approbation"),
    ("Session ouverte ; ajoutée ce matin à G_Compta, Julie reçoit « Accès refusé » sans s'être reconnectée", "droits"),
    ("« Le compte référencé est actuellement verrouillé » après cinq mots de passe faux", "compte"),
    ("nslookup du domaine répond « Non-existent domain » : le poste interroge un DNS public", "dns"),
)
E06_CORRECT = tuple(E06_CATEGORIES.index(logon_diagnosis(first_failure(k))) for _t, k in E06_CASES)

E07_CASES: tuple[tuple[str, str], ...] = (
    ("Paul a oublié son mot de passe au retour de congé", ACCOUNT_ACTION_RESET),
    ("Une employée quitte l'entreprise vendredi soir", ACCOUNT_ACTION_DISABLE),
    ("Après cinq essais faux, le compte de Sara refuse toute connexion", ACCOUNT_ACTION_UNLOCK),
    ("Julie reprend aussi la comptabilité et doit ouvrir le dossier Compta", ACCOUNT_ACTION_GROUP),
    ("Fin de stage : le stagiaire ne revient plus", ACCOUNT_ACTION_DISABLE),
    ("Un mot de passe a été noté sur un papier collé à l'écran", ACCOUNT_ACTION_RESET),
    ("Le nouveau directeur doit lire les dossiers de la direction", ACCOUNT_ACTION_GROUP),
    ("Le compte de Marc est bloqué depuis qu'il a tapé son ancien mot de passe sur son téléphone", ACCOUNT_ACTION_UNLOCK),
)
E07_CORRECT = tuple(ACCOUNT_ACTIONS.index(a) for _t, a in E07_CASES)

# E12 : jonction impossible, DNS de la box
E12_WS = Workstation("PC-07", "192.168.20.17", (BOX_IP,))
E12_BLOCKERS = join_blockers(E12_WS)
E12_DIAG = logon_diagnosis(logon_checks(E12_WS, Account("jmartin", "Julie Martin")))

# E13 : heure
E13_WS = Workstation("PC-05", "192.168.20.15", (DC_IP,), clock_offset_min=9)
E13_DIAG = logon_diagnosis(logon_checks(E13_WS, Account("lbernard", "Luc Bernard")))

# E14 : relation d'approbation rompue après restauration d'une image
E14_WS = Workstation("PC-09", "192.168.20.19", (DC_IP,), secure_channel=False)
E14_DIAG = logon_diagnosis(logon_checks(E14_WS, Account("sdubois", "Sara Dubois")))

# E15 : compte verrouillé
E15_ACCOUNT = Account("pnoel", "Paul Noël", (USERS_DOMAIN, "G_Atelier"), locked=True)
E15_DIAG = logon_diagnosis(logon_checks(Workstation("PC-04", "192.168.20.14", (DC_IP,)), E15_ACCOUNT))

# E16 : groupe ajouté, session pas rouverte
E16_ACCOUNT = Account("jmartin", "Julie Martin", (USERS_DOMAIN, "G_Compta"), token_groups=(USERS_DOMAIN,))
E16_BEFORE = access_of(E16_ACCOUNT, "Compta")
E16_AFTER = access_of(Account("jmartin", "Julie Martin", (USERS_DOMAIN, "G_Compta")), "Compta")
E16_DIAG = logon_diagnosis(logon_checks(Workstation("PC-03", "192.168.20.13", (DC_IP,)), E16_ACCOUNT,
                                        needed_group="G_Compta"))

# E18 : groupe de travail de 3 postes, comptes à créer
E18_USERS = {"lea": ("PC-A",), "noah": ("PC-B",), "ines": ("PC-C", "PC-B")}
E18_ACCOUNTS = workgroup_accounts(E18_USERS, "PC-A", ("lea", "noah", "ines"))
E18_TOTAL = count_accounts(E18_ACCOUNTS)

# E20 : fiche de comptes à auditer
E20_ROWS: tuple[AccountRow, ...] = (
    AccountRow("cdupont", "Claire Dupont (directrice)", (USERS_DOMAIN, "G_Direction")),
    AccountRow("accueil", "Les trois personnes de l'accueil", (USERS_DOMAIN,), shared=True),
    AccountRow("tleroy", "Tom Leroy (technicien)", (USERS_DOMAIN, ADMINS_DOMAIN)),
    AccountRow("adm-tleroy", "Tom Leroy (administration)", (USERS_DOMAIN, ADMINS_DOMAIN)),
    AccountRow("mvincent", "Marc Vincent (parti en août)", (USERS_DOMAIN, "G_Compta"), left=True),
    AccountRow("jmartin", "Julie Martin (comptable)", (USERS_DOMAIN, "G_Compta")),
    AccountRow("Invité", "Compte intégré", (), enabled=True),
)
E20_ERRORS = account_errors(E20_ROWS)

# --- Mini-examen -------------------------------------------------------------------------------

X01_ORG = Organisation("Cabinet médical de 14 postes, remplaçants fréquents", 14, rotation=True)
X01_MODEL = recommend_model(X01_ORG)
X02_USERS = {"emma": ("PC-1", "PC-2"), "hugo": ("PC-2",), "zoe": ("PC-3",)}
X02_ACCOUNTS = workgroup_accounts(X02_USERS, "PC-1", ("emma", "hugo", "zoe"))
X03_WS = Workstation("PC-11", "192.168.20.21", (BOX_IP,))
X03_DIAG = logon_diagnosis(logon_checks(X03_WS, Account("emoreau", "Emma Moreau")))
X04_WS = Workstation("PC-12", "192.168.20.22", (DC_IP,), clock_offset_min=-12)
X04_DIAG = logon_diagnosis(logon_checks(X04_WS, Account("hpetit", "Hugo Petit")))
X08_ACCOUNT = Account("lbernard", "Luc Bernard", (USERS_DOMAIN, "G_Direction"), token_groups=(USERS_DOMAIN,))

# =============================================================================================
# 20 exercices corrigés (cours + « S'entraîner »)
# =============================================================================================

PRACTICE_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="E01",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la jonction d'un poste au domaine",
        question_type="ordering",
        requirement_ids=("AP-24",),
        kind=KIND_ORDER,
        context=(
            f"Un cabinet comptable vient d'installer son contrôleur de domaine {DNS_DOMAIN}. Tu dois "
            "joindre un nouveau poste Windows 11 Professionnel au domaine. La fiche de l'atelier compte "
            "sept étapes, recopiées dans le désordre par un stagiaire."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3.5, "Prérequis → DNS → tester le contrôleur → joindre → redémarrer → session du domaine → consigner (0,5 pt par étape)."),
        ),
        correction=(
            f"1. On vérifie les prérequis (édition Professionnel, nom unique, réseau, heure). 2. On règle le DNS du poste sur le contrôleur ({DC_IP}). 3. On teste : ping du contrôleur, nslookup {DNS_DOMAIN}. 4. On joint le domaine avec un compte autorisé.",
            f"5. On redémarre (obligatoire). 6. On ouvre une session du domaine ({NETBIOS_DOMAIN}\\jmartin) et on contrôle whoami et gpresult /r. 7. On consigne. Le DNS se règle avant la jonction : c'est lui qui permet de trouver le contrôleur.",
        ),
        ordering=_shuffled_ordering(E01_STEPS, (3, 6, 0, 5, 1, 4, 2)),
    ),
    PR06Item(
        key="E02",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre la vie d'un compte, de l'arrivée au départ",
        question_type="ordering",
        requirement_ids=("AP-24",),
        kind=KIND_ORDER,
        context=(
            "Dans une PME de douze postes en domaine, tu rédiges la procédure de gestion des comptes "
            "pour l'équipe informatique : de la demande d'arrivée d'une personne jusqu'à la suppression "
            "de son compte après son départ. Les sept étapes ont été mélangées."
        ),
        instructions=("Remets les sept étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 3.5, "Demande → créer → mot de passe initial → groupes → tester → départ : désactiver → supprimer plus tard (0,5 pt par étape)."),
        ),
        correction=(
            "1. On part d'une demande écrite et validée. 2. On crée un compte nominatif. 3. Mot de passe initial temporaire, remis à part, à changer à la première ouverture de session. 4. On ajoute le compte aux seuls groupes métier nécessaires. 5. On teste la connexion et les accès.",
            "6. Le jour du départ, on désactive le compte (et on le retire des groupes) : plus personne ne peut s'en servir, mais ses fichiers et son historique restent. 7. On le supprime plus tard, après sauvegarde des données et le délai prévu.",
        ),
        ordering=_shuffled_ordering(E02_STEPS, (4, 1, 6, 0, 5, 3, 2)),
    ),
    PR06Item(
        key="E03",
        usage=USAGE_PRACTICE,
        title="Remettre dans l'ordre le dépannage d'une ouverture de session",
        question_type="ordering",
        requirement_ids=("AP-24",),
        kind=KIND_ORDER,
        context=(
            "Le service d'assistance d'une école reçoit chaque semaine des appels « je ne peux pas me "
            "connecter » ou « accès refusé ». Tu rédiges la fiche de dépannage en huit étapes, du plus "
            "général au plus particulier ; le brouillon est dans le désordre."
        ),
        instructions=("Remets les huit étapes dans l'ordre.",),
        criteria=(
            _c("Ordre", 4, "Message → réseau → DNS → heure → poste (relation d'approbation) → compte → droits → consigner (0,5 pt par étape)."),
        ),
        correction=(
            "1. On note le message exact et on regarde si un seul poste ou un seul compte est touché. 2. Réseau : le poste joint-il le contrôleur ? 3. DNS : le poste interroge-t-il le contrôleur ? 4. Heure : écart de 5 minutes au plus (Kerberos).",
            "5. Poste : relation d'approbation valide. 6. Compte : actif, non verrouillé, mot de passe valide. 7. Droits : groupe présent dans la session (whoami /groups), sinon fermer et rouvrir la session. 8. On consigne. Le premier contrôle en échec désigne la piste.",
        ),
        ordering=_shuffled_ordering(E03_STEPS, (5, 2, 7, 0, 6, 3, 1, 4)),
    ),
    PR06Item(
        key="E04",
        usage=USAGE_PRACTICE,
        title="Groupe de travail ou domaine pour chaque organisation ?",
        question_type="classification",
        requirement_ids=("AP-24",),
        kind=KIND_MODEL,
        context=(
            "Ton entreprise de maintenance conseille sept clients de 3 à 20 postes. Repère de l'atelier : "
            "un groupe de travail suffit jusqu'à une dizaine de postes (10 au plus) si personne ne change "
            "de poste, si le personnel est stable et s'il n'y a pas de règles à imposer à tous ; sinon, un domaine."
        ),
        instructions=("Range chaque organisation selon le modèle à conseiller.",),
        criteria=(
            _c("Classement", 3.5, "3, 5 et 4 postes stables → groupe de travail ; 14 postes, intérimaires, école, règles imposées → domaine (0,5 pt par élément)."),
        ),
        correction=(
            "Dans un groupe de travail, chaque poste a ses propres comptes : c'est simple et sans serveur tant que les postes sont peu nombreux et que chacun reste sur le sien (indépendante, association, garage).",
            "Dès qu'on dépasse une dizaine de postes, que des personnes changent de poste (secrétaire volante), arrivent et partent souvent (intérim, élèves) ou qu'il faut imposer des règles à tous (verrouillage, mots de passe), il faut gérer les comptes et les règles depuis un point central : un domaine Active Directory, avec un serveur contrôleur.",
        ),
        classification=Classification(categories=MODELS, elements=tuple(o.label for o in E04_CASES), correct=E04_CORRECT),
    ),
    PR06Item(
        key="E05",
        usage=USAGE_PRACTICE,
        title="Compte local ou compte du domaine ?",
        question_type="classification",
        requirement_ids=("AP-24",),
        kind=KIND_ACCOUNT,
        context=(
            f"Sur l'écran de connexion des postes du domaine {DNS_DOMAIN} (nom court {NETBIOS_DOMAIN}), les "
            "utilisateurs tapent leur nom de différentes façons. Pour la fiche d'aide, tu dois dire pour "
            "chacune quel compte est utilisé : celui du poste ou celui du domaine."
        ),
        instructions=("Range chaque nom de connexion selon le compte utilisé.",),
        criteria=(
            _c("Classement", 3.5, f"{NETBIOS_DOMAIN}\\… et …@{DNS_DOMAIN} → domaine ; .\\… et NOMDUPOSTE\\… → local (0,5 pt par élément)."),
        ),
        correction=(
            f"Le préfixe dit qui vérifie le mot de passe. « {NETBIOS_DOMAIN}\\nom » (nom NetBIOS du domaine) et « nom@{DNS_DOMAIN} » (UPN, nom DNS du domaine) désignent un compte du domaine, vérifié par le contrôleur.",
            "« .\\nom » (le point = ce poste) et « PC-03\\nom » (nom du poste) désignent un compte local, vérifié par le poste lui-même : il n'existe que sur ce poste et ne donne aucun accès au domaine.",
        ),
        classification=Classification(categories=SCOPES, elements=E05_NAMES, correct=E05_CORRECT),
    ),
    PR06Item(
        key="E06",
        usage=USAGE_PRACTICE,
        title="Quelle piste pour chaque échec de connexion ?",
        question_type="classification",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            f"Le domaine {DNS_DOMAIN} a un contrôleur en {DC_IP}. En une semaine, l'assistance a reçu huit "
            "signalements. Ordre des contrôles : réseau, DNS, heure, relation d'approbation du poste, compte, "
            "droits ; le premier en échec désigne la piste."
        ),
        instructions=("Range chaque signalement selon la piste à suivre.",),
        criteria=(
            _c("Classement", 4, "Câble → réseau ; DNS de la box, DNS public → DNS ; 9 minutes → heure ; relation d'approbation → poste ; désactivé, verrouillé → compte ; groupe sans reconnexion → droits (0,5 pt par élément)."),
        ),
        correction=(
            "« Aucun serveur d'ouverture de session » avec le câble débranché : le poste ne joint pas le contrôleur (réseau). Le contrôleur introuvable ou « Non-existent domain » : le poste interroge un DNS qui ne connaît pas le domaine (box, DNS public) ; son DNS doit être le contrôleur. Un écart de 9 minutes dépasse la tolérance Kerberos de 5 minutes.",
            "« La relation d'approbation… a échoué » : le compte d'ordinateur du poste ne correspond plus au domaine. « Désactivé » ou « verrouillé » : état du compte. Ajoutée à un groupe sans rouvrir sa session, Julie garde les anciens groupes de sa session : droits.",
        ),
        classification=Classification(categories=E06_CATEGORIES, elements=tuple(t for t, _k in E06_CASES), correct=E06_CORRECT),
    ),
    PR06Item(
        key="E07",
        usage=USAGE_PRACTICE,
        title="Quelle action sur le compte ?",
        question_type="classification",
        requirement_ids=("AP-24",),
        kind=KIND_ACCOUNT,
        context=(
            "Tu es le technicien d'une PME de 15 postes en domaine. Tu tiens la console « Utilisateurs et "
            "ordinateurs Active Directory » et reçois huit demandes du jour. Pour chacune, choisis l'action "
            "minimale et sûre à faire sur le compte."
        ),
        instructions=("Range chaque demande selon l'action à faire.",),
        criteria=(
            _c("Classement", 4, "Départ, fin de stage → désactiver ; oubli, mot de passe affiché → réinitialiser ; essais faux, ancien mot de passe sur le téléphone → déverrouiller ; nouvelle mission, nouveau directeur → groupe métier (0,5 pt par élément)."),
        ),
        correction=(
            "Une personne qui part : on désactive le compte le jour même (on ne le supprime pas tout de suite : fichiers, historique, boîte aux lettres). Un mot de passe oublié ou connu d'autres personnes : réinitialisation avec « changer à la prochaine ouverture de session ».",
            "Un compte verrouillé après des essais faux : on le déverrouille (et pour Marc, on met à jour le mot de passe enregistré dans son téléphone, sinon il se reverrouille). Un nouvel accès : on ajoute le compte au groupe métier qui a le droit, jamais un droit à la personne.",
        ),
        classification=Classification(categories=ACCOUNT_ACTIONS, elements=tuple(t for t, _a in E07_CASES), correct=E07_CORRECT),
    ),
    PR06Item(
        key="E08",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : le domaine et son DNS",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_SCHEMA,
        context=(
            f"Un bureau d'architectes de dix postes passe en domaine {DNS_DOMAIN}. Le document 1 est le schéma "
            "du réseau remis au client : il manque le rôle et l'adresse du serveur, et le DNS et la passerelle "
            f"du poste PC-03. La box ({BOX_IP}) donne l'accès à Internet."
        ),
        documents=(_schema("pr22-domaine-a-completer", "Document 1 — Domaine à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Explique pourquoi le DNS des postes n'est pas la box.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in DOMAIN_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Justification", 1, "Les postes trouvent le contrôleur (et s'authentifient) grâce aux enregistrements DNS du domaine, que seul le DNS du contrôleur connaît ; il relaie lui-même les autres noms vers Internet."),
        ),
        correction=(
            f"① Le serveur DC01 est le contrôleur de domaine (Active Directory : comptes, groupes, stratégies) et le serveur DNS du domaine. ② Il a une adresse fixe, ici {DC_IP}/24 : tous les postes doivent le retrouver. ③ Le DNS de PC-03 est {DC_IP}. ④ La passerelle reste la box, {BOX_IP}.",
            f"Pour ouvrir une session, le poste cherche dans le DNS où se trouve le contrôleur du domaine {DNS_DOMAIN}. La box ne connaît pas ce domaine : avec elle en DNS, la jonction et les connexions échouent. Le contrôleur, lui, répond pour le domaine et transmet les autres noms (sites Internet) vers la box ou l'opérateur.",
        ),
    ),
    PR06Item(
        key="E09",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : les noms du domaine",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_SCHEMA,
        context=(
            "Tu prépares la fiche remise aux nouveaux employés d'un cabinet en domaine. Elle doit expliquer "
            "les différents noms du domaine et la façon de se connecter. Le document 1 est la fiche à terminer ; "
            "le poste de l'exemple s'appelle PC-03 et l'employée Julie Martin a pour identifiant jmartin."
        ),
        documents=(_schema("pr22-noms-a-completer", "Document 1 — Noms du domaine à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ②, ③ et ④.",
            "Explique la différence entre le domaine DNS et le domaine d'administration (Active Directory).",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in NAMES_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Distinction", 1.5, "Domaine DNS = nom dans le système de noms (adresse des machines) ; domaine Active Directory = ensemble administré (comptes, groupes, stratégies) ; il porte un nom DNS et un nom NetBIOS court."),
        ),
        correction=(
            f"① {NETBIOS_DOMAIN} : nom NetBIOS, court (15 caractères au plus). ② pc-03.{DNS_DOMAIN} : nom DNS complet du poste. ③ {NETBIOS_DOMAIN}\\jmartin et ④ jmartin@{DNS_DOMAIN} : les deux écritures du même compte du domaine.",
            f"Un domaine DNS n'est qu'un nom dans l'annuaire des noms (il sert à trouver des machines, comme un site web). Le domaine Active Directory est un domaine d'administration : un ensemble de comptes, de groupes, d'ordinateurs et de règles gérés par les contrôleurs. Il s'appuie sur le DNS et porte donc un nom DNS ({DNS_DOMAIN}), plus un nom court ({NETBIOS_DOMAIN}).",
        ),
    ),
    PR06Item(
        key="E10",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : comptes d'un groupe de travail",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_SCHEMA,
        context=(
            "Un petit cabinet de quatre personnes travaille en groupe de travail, sans serveur. Anne, Paul et "
            "Sara ont chacun leur poste ; Marc travaille sur PC-4 et parfois sur PC-2. Tout le monde ouvre le "
            "dossier « Commun » partagé par PC-1. Le document 1 montre les comptes locaux, dont deux listes manquent."
        ),
        documents=(_schema("pr22-groupe-de-travail-a-completer", "Document 1 — Groupe de travail à compléter (schéma fictif)"),),
        instructions=(
            "Complète les listes ① (PC-1) et ② (PC-2).",
            "Calcule le nombre total de comptes locaux et compare avec un domaine.",
        ),
        criteria=(
            _c("Listes", 2, f"① {WG_BLANK_ANSWERS['①']} ; ② {WG_BLANK_ANSWERS['②']} (1 pt chacune)."),
            _c("Calcul et comparaison", 1, f"{count_accounts(WG_ACCOUNTS)} comptes locaux, à tenir à jour poste par poste (mots de passe identiques) ; en domaine, 4 comptes."),
        ),
        correction=(
            "① PC-1 : anne (son poste) et paul, sara, marc, qui ouvrent le partage « Commun » par le réseau : chaque accès à un partage d'un groupe de travail se fait avec un compte de PC-1. ② PC-2 : paul (son poste) et marc, qui y travaille parfois.",
            f"Total : {count_accounts(WG_ACCOUNTS)} comptes locaux (4 + 2 + 1 + 1) pour 4 personnes, et un changement de mot de passe à refaire sur chaque poste concerné. En domaine, 4 comptes suffisent, vérifiés par le contrôleur sur tous les postes.",
        ),
    ),
    PR06Item(
        key="E11",
        usage=USAGE_PRACTICE,
        title="Schéma à compléter : la fiche des groupes",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_SCHEMA,
        context=(
            "Dans une fiduciaire en domaine, les droits sur les dossiers du serveur sont donnés aux groupes. "
            "La comptabilité (jmartin, lbernard) modifie le dossier Compta ; la directrice modifie le dossier "
            "Direction et lit Compta ; tout le monde modifie Commun. Le document 1 est la fiche à terminer."
        ),
        documents=(_schema("pr22-groupes-a-completer", "Document 1 — Fiche des groupes à compléter (schéma fictif)"),),
        instructions=(
            "Complète ①, ② ; puis ③ et ④ (groupes locaux de chaque poste après la jonction).",
            "Explique pourquoi on donne les droits aux groupes plutôt qu'aux personnes.",
        ),
        criteria=(
            _c("Valeurs", 2, " ; ".join(f"{k} {v}" for k, v in GROUPS_BLANK_ANSWERS.items()) + " (0,5 pt chacune)."),
            _c("Justification", 1, "Arrivée, départ ou changement de poste : on modifie l'appartenance aux groupes, pas les droits des dossiers ; fiche lisible, moins d'erreurs."),
        ),
        correction=(
            f"① G_Compta, le groupe métier de la comptabilité, qui a Modification sur Compta. ② Direction : Modification ; Compta : Lecture. ③ À la jonction, {NETBIOS_DOMAIN}\\{ADMINS_DOMAIN} devient membre du groupe local Administrateurs de chaque poste. ④ {NETBIOS_DOMAIN}\\{USERS_DOMAIN} devient membre du groupe local Utilisateurs.",
            "Si les droits sont donnés aux groupes, une nouvelle comptable reçoit tous ses accès en une seule action (ajout à G_Compta) et les perd en une action à son départ. Des droits donnés personne par personne finissent oubliés sur des dossiers.",
        ),
    ),
    PR06Item(
        key="E12",
        usage=USAGE_PRACTICE,
        title="La jonction au domaine échoue",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            f"Tu joins PC-07 au domaine {DNS_DOMAIN}. Windows répond qu'un contrôleur de domaine pour ce "
            f"domaine n'a pas pu être contacté. Le ping de {DC_IP} (le contrôleur) réussit. Le poste a été "
            "configuré à la main par un collègue. Les documents 1 et 2 sont tes relevés."
        ),
        documents=(
            _console("Document 1 — ipconfig /all sur PC-07 (capture fictive)", *ipconfig_dns_lines(E12_WS)),
            _console("Document 2 — nslookup sur PC-07 (capture fictive)", *nslookup_lines(BOX_IP, knows_domain=False)),
        ),
        instructions=(
            "Indique la cause en t'appuyant sur les deux relevés.",
            "Donne la correction et les tests avant de relancer la jonction.",
        ),
        criteria=(
            _c("Cause", 1.5, f"DNS du poste = box {BOX_IP} ; elle ne connaît pas {DNS_DOMAIN} (Non-existent domain) : le poste ne trouve pas le contrôleur ; le réseau, lui, fonctionne (ping)."),
            _c("Correction et tests", 1.5, f"DNS = {DC_IP} seul ; ipconfig /all ; nslookup {DNS_DOMAIN} renvoie {DC_IP} ; puis jonction."),
        ),
        correction=(
            f"Le ping du contrôleur réussit : le réseau est bon. Mais le seul serveur DNS du poste est la box ({BOX_IP}), qui répond « Non-existent domain » pour {DNS_DOMAIN} : le poste ne peut pas trouver le contrôleur du domaine par le DNS, d'où l'échec. Piste : {E12_DIAG.split(' :')[0]}.",
            f"On met {DC_IP} comme seul serveur DNS (le contrôleur relaie les noms d'Internet), on vérifie avec ipconfig /all, puis nslookup {DNS_DOMAIN} doit renvoyer {DC_IP}. Ensuite seulement, on relance la jonction. Si le réseau utilise le DHCP de la box, on y règle l'option DNS (ou on confie le DHCP au serveur).",
        ),
    ),
    PR06Item(
        key="E13",
        usage=USAGE_PRACTICE,
        title="Connexion refusée sur un seul poste",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            "Depuis le remplacement de la pile de sa carte mère, PC-05 refuse toutes les ouvertures de session "
            "du domaine (message signalant une différence d'heure avec le serveur), alors que les mêmes comptes "
            "fonctionnent sur les autres postes. Réseau et DNS sont corrects. Le document 1 est ton relevé."
        ),
        documents=(_console("Document 1 — heure du contrôleur et du poste (capture fictive)", *time_lines(E13_WS)),),
        instructions=(
            "Calcule l'écart et conclus.",
            "Donne la correction durable et le test.",
        ),
        criteria=(
            _c("Écart", 1, f"09:21 − 09:12 = 9 minutes, plus que la tolérance de {MAX_CLOCK_SKEW_MIN} minutes : Kerberos refuse l'authentification."),
            _c("Correction", 1.5, "Remettre le poste à l'heure du domaine (w32tm /resync, ou date/heure puis resynchronisation) ; vérifier fuseau horaire et BIOS ; laisser la synchronisation automatique ; nouvelle connexion réussie."),
        ),
        correction=(
            f"Le contrôleur indique 09:12, le poste 09:21 : 9 minutes d'écart. L'authentification du domaine (Kerberos) refuse un écart de plus de {MAX_CLOCK_SKEW_MIN} minutes par défaut ; la pile changée a remis l'horloge à une mauvaise valeur. Piste : {E13_DIAG.split(' :')[0]}.",
            "On corrige l'heure (BIOS si besoin, fuseau horaire), puis on force la synchronisation sur le domaine : w32tm /resync (invite administrateur, compte local si aucune session du domaine ne s'ouvre). On vérifie l'heure, puis on ouvre une session du domaine.",
        ),
    ),
    PR06Item(
        key="E14",
        usage=USAGE_PRACTICE,
        title="Plus aucune connexion après la restauration d'une image",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            "Le disque de PC-09 a été restauré à partir d'une image de trois mois. Depuis, toute ouverture de "
            "session du domaine affiche « La relation d'approbation entre cette station de travail et le domaine "
            "principal a échoué ». Réseau, DNS et heure sont corrects. Le document 1 est ton relevé."
        ),
        documents=(_console("Document 1 — nltest sur PC-09, session locale (capture fictive)", *secure_channel_lines(False)),),
        instructions=(
            "Explique la cause.",
            "Propose deux corrections possibles et le test.",
        ),
        criteria=(
            _c("Cause", 1, "Le poste a un compte d'ordinateur dans le domaine dont le mot de passe change automatiquement ; l'image contient un ancien mot de passe : le domaine ne reconnaît plus le poste."),
            _c("Corrections et test", 1.5, f"Session locale administrateur : Test-ComputerSecureChannel -Repair avec un compte autorisé du domaine ; ou sortir du domaine puis le rejoindre ; puis nltest /sc_query:{DNS_DOMAIN} = succès et connexion du domaine."),
        ),
        correction=(
            f"Un poste du domaine a, lui aussi, un compte (compte d'ordinateur) avec un mot de passe qu'il change seul régulièrement. L'image de trois mois a remis un ancien mot de passe : le contrôleur refuse le poste (canal sécurisé rompu). Piste : {E14_DIAG.split(' :')[0]}.",
            f"On ouvre une session locale (.\\support) et, en PowerShell administrateur : Test-ComputerSecureChannel -Repair -Credential {NETBIOS_DOMAIN}\\adm-tleroy. Autre solution : passer le poste en groupe de travail puis le rejoindre au domaine (deux redémarrages). Test : nltest /sc_query:{DNS_DOMAIN} doit afficher un succès, puis une session du domaine s'ouvre.",
        ),
    ),
    PR06Item(
        key="E15",
        usage=USAGE_PRACTICE,
        title="Un employé ne peut plus se connecter",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            "Paul Noël, de l'atelier, appelle : il ne peut plus ouvrir de session, ni sur son poste ni sur celui "
            "de son collègue. Il dit avoir changé son mot de passe hier et l'avoir peut-être mal tapé plusieurs "
            "fois ce matin. Les autres employés se connectent normalement. Le document 1 est ton relevé."
        ),
        documents=(_console("Document 1 — net user pnoel /domain (capture fictive)", *net_user_lines(E15_ACCOUNT)),),
        instructions=(
            "Indique la cause en t'appuyant sur le relevé et les symptômes.",
            "Donne l'action à faire, ce qu'il ne faut pas faire, et le test.",
        ),
        criteria=(
            _c("Cause", 1, "« Compte : actif  Verrouillé » : trop d'essais faux ; un seul compte touché, sur tous les postes : le compte, pas le poste ni le réseau."),
            _c("Action", 1.5, "Vérifier l'identité de Paul, déverrouiller le compte (Utilisateurs et ordinateurs Active Directory, ou Unlock-ADAccount) ; pas de réinitialisation nécessaire s'il connaît son mot de passe ; mettre à jour les appareils qui gardent l'ancien ; connexion d'essai."),
        ),
        correction=(
            f"Le relevé indique « Compte : actif  Verrouillé ». Un seul compte est touché, sur plusieurs postes, et les autres se connectent : le problème vient du compte (piste : {E15_DIAG.split(' :')[0].lower()}), verrouillé après trop d'essais faux.",
            "Après avoir vérifié qu'on parle bien à Paul, on déverrouille le compte dans « Utilisateurs et ordinateurs Active Directory » (ou Unlock-ADAccount pnoel). S'il connaît son nouveau mot de passe, inutile de le réinitialiser ; on vérifie qu'aucun appareil (téléphone, lecteur réseau mémorisé) n'essaie encore l'ancien. On ne désactive pas la stratégie de verrouillage. Test : connexion réussie.",
        ),
    ),
    PR06Item(
        key="E16",
        usage=USAGE_PRACTICE,
        title="Ajoutée au groupe, mais toujours « Accès refusé »",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            "Ce matin à 9 h, le technicien a ajouté Julie Martin au groupe G_Compta pour qu'elle modifie le dossier "
            "Compta du serveur. À 10 h, sans avoir fermé sa session ouverte à 8 h, Julie reçoit toujours « Accès "
            "refusé ». La fiche des groupes donne G_Compta : Modification sur Compta. Le document 1 est ton relevé."
        ),
        documents=(_console("Document 1 — whoami sur le poste de Julie (capture fictive)", *whoami_groups_lines(E16_ACCOUNT)),),
        instructions=(
            "Explique pourquoi l'accès est refusé alors que le groupe est correct.",
            "Donne la solution et le test.",
        ),
        criteria=(
            _c("Cause", 1, "La session ouverte à 8 h a gardé les groupes de 8 h : G_Compta n'apparaît pas dans whoami /groups ; l'ajout ne compte qu'à la prochaine ouverture de session."),
            _c("Solution et test", 1, f"Fermer la session et la rouvrir (ou redémarrer) ; whoami /groups montre G_Compta ; accès en {E16_AFTER.lower()} au dossier Compta."),
        ),
        correction=(
            f"Les groupes d'un compte sont lus à l'ouverture de session et gardés pendant toute la session. Julie a ouvert sa session à 8 h, avant l'ajout : whoami /groups ne montre pas G_Compta, son accès à Compta est donc « {E16_BEFORE} ». Piste : {E16_DIAG.split(' :')[0].lower()}.",
            f"Julie ferme sa session et la rouvre (ou redémarre). whoami /groups doit afficher {NETBIOS_DOMAIN}\\G_Compta ; le dossier Compta s'ouvre en {E16_AFTER.lower()}. On ne donne pas un droit à Julie directement sur le dossier pour « aller plus vite ».",
        ),
    ),
    PR06Item(
        key="E17",
        usage=USAGE_PRACTICE,
        title="Rédiger la fiche comptes et groupes d'un cabinet de 12 postes",
        question_type="long_answer",
        requirement_ids=("AP-24",),
        kind=KIND_SHEET,
        context=(
            f"Un cabinet d'avocats passe en domaine {DNS_DOMAIN} : 2 associés, 6 avocats, 3 secrétaires et un "
            "technicien à temps partiel, 12 postes. Dossiers du serveur : Clients (avocats et associés modifient, "
            "secrétaires lisent), Associés (associés seulement), Commun (tout le monde)."
        ),
        documents=(_table("Document 1 — Demande du client", ("Dossier", "Qui modifie", "Qui lit"),
                          ("Clients", "associés, avocats", "secrétaires"),
                          ("Associés", "associés", "—"),
                          ("Commun", "tout le monde", "—")),),
        instructions=(
            "Propose les comptes (types et règles de nommage) et les groupes, puis les droits de chaque groupe.",
            "Justifie le traitement du compte du technicien.",
        ),
        criteria=(
            _c("Comptes", 1, "Un compte du domaine nominatif par personne (12) ; aucun compte commun ; technicien : un compte quotidien standard + un compte adm- séparé."),
            _c("Groupes et droits", 2, f"G_Associes, G_Avocats, G_Secretariat ; Clients : G_Associes et G_Avocats Modification, G_Secretariat Lecture ; Associés : G_Associes Modification ; Commun : {USERS_DOMAIN} Modification."),
            _c("Justification", 1, "Moindre privilège : le compte d'administration ne sert qu'à administrer ; s'il est volé ou si un logiciel malveillant s'ouvre dans la session de tous les jours, il n'a pas les droits d'administration."),
        ),
        correction=(
            f"Comptes : un compte du domaine par personne, nommé de la même façon (ex. initiale + nom), mot de passe personnel. Groupes métier : G_Associes (2), G_Avocats (6), G_Secretariat (3). Droits : Clients → G_Associes et G_Avocats en Modification, G_Secretariat en Lecture ; Associés → G_Associes en Modification ; Commun → {USERS_DOMAIN} en Modification.",
            f"Le technicien a deux comptes : son compte de tous les jours (standard, groupes métier éventuels) et un compte « adm-… » membre de {ADMINS_DOMAIN}, utilisé uniquement pour administrer. C'est le moindre privilège : la messagerie et le web ne tournent jamais avec des droits d'administration.",
        ),
    ),
    PR06Item(
        key="E18",
        usage=USAGE_PRACTICE,
        title="Comptes locaux à créer dans un groupe de travail",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_SHEET,
        context=(
            "Une petite librairie installe trois postes en groupe de travail, sans serveur. Léa travaille sur "
            "PC-A, Noah sur PC-B, Inès sur PC-C et parfois sur PC-B. Le dossier « Stock » est partagé par PC-A "
            "et tout le monde doit l'ouvrir par le réseau. Le document 1 est la demande du gérant."
        ),
        documents=(_table("Document 1 — Postes et besoins", ("Personne", "Postes utilisés", "Ouvre Stock (PC-A)"),
                          ("Léa", "PC-A", "oui"), ("Noah", "PC-B", "oui"), ("Inès", "PC-C, PC-B", "oui")),),
        instructions=(
            "Dresse la fiche des comptes locaux de chaque poste et le total.",
            "Explique la règle et la contrainte sur les mots de passe.",
        ),
        criteria=(
            _c("Fiche", 2, " ; ".join(f"{pc} : {', '.join(names)}" for pc, names in E18_ACCOUNTS.items()) + f" ; total {E18_TOTAL}."),
            _c("Règle", 1, "En groupe de travail, chaque poste vérifie ses propres comptes : un compte local avec mot de passe sur chaque poste où l'on ouvre une session et sur le poste qui partage ; mots de passe à tenir identiques à la main."),
        ),
        correction=(
            ("PC-A : lea (son poste) + noah et ines, qui ouvrent le partage Stock (l'accès réseau se fait avec un compte de PC-A). PC-B : noah + ines, qui y travaille parfois. PC-C : ines. "
             f"Total : {E18_TOTAL} comptes locaux pour 3 personnes."),
            "Chaque poste ne connaît que ses propres comptes. Un compte sans mot de passe est refusé par le réseau : chacun a un mot de passe. Quand Inès change le sien, il faut le changer sur PC-A, PC-B et PC-C (sinon l'accès au partage redemande un mot de passe) : c'est la limite du groupe de travail.",
        ),
    ),
    PR06Item(
        key="E19",
        usage=USAGE_PRACTICE,
        title="Choisir le nom du domaine",
        question_type="short_answer",
        requirement_ids=("AP-24",),
        kind=KIND_MODEL,
        context=(
            "La société Dupont, qui possède le nom de site public dupont.example, crée son domaine Active Directory. "
            "Le stagiaire propose « dupont.local », un collègue « dupont.example » (le nom du site), ton responsable "
            "« ad.dupont.example » avec le nom court DUPONT. Tu dois trancher par écrit."
        ),
        instructions=("Choisis le nom et justifie, en distinguant nom DNS et nom NetBIOS.",),
        criteria=(
            _c("Choix", 1, f"{DNS_DOMAIN} (sous-domaine du nom public possédé par l'entreprise), nom NetBIOS {NETBIOS_DOMAIN}."),
            _c("Justification", 1.5, "Pas .local (réservé à d'autres usages sur les réseaux locaux, conflits) ; pas le même nom que le site public (le DNS interne masquerait le site) ; sous-domaine possédé = unique et sans conflit ; NetBIOS = nom court pour DUPONT\\nom."),
        ),
        correction=(
            f"On choisit {DNS_DOMAIN} : un sous-domaine du nom public que l'entreprise possède. Il est unique et ne risque pas d'entrer en conflit. Le nom NetBIOS (court, 15 caractères au plus) sera {NETBIOS_DOMAIN}, utilisé dans {NETBIOS_DOMAIN}\\jmartin.",
            "« dupont.local » est déconseillé : .local est utilisé par la découverte automatique des appareils (imprimantes, Mac, Linux) et provoque des conflits. Reprendre exactement le nom du site public obligerait le DNS interne à répondre aussi pour le site web et la messagerie.",
        ),
    ),
    PR06Item(
        key="E20",
        usage=USAGE_PRACTICE,
        title="Auditer la fiche des comptes d'une PME",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_SHEET,
        context=(
            f"À ton arrivée dans une PME en domaine {DNS_DOMAIN}, ton responsable te remet l'export des comptes "
            "(document 1) et te demande les corrections à faire avant l'audit de sécurité du mois prochain. Marc "
            "Vincent a quitté l'entreprise en août."
        ),
        documents=(_table("Document 1 — Export des comptes (extrait fictif)", ("Compte", "Personne", "Groupes", "Actif"),
                          *((r.login, r.person, ", ".join(r.groups) or "—", "oui" if r.enabled else "non") for r in E20_ROWS)),),
        instructions=(
            "Relève chaque erreur et la correction.",
            "Indique les comptes qui sont corrects.",
        ),
        criteria=(
            _c("Erreurs", 2.5, f"{len(E20_ERRORS)} erreurs : accueil commun ; tleroy dans {ADMINS_DOMAIN} ; mvincent parti mais actif ; Invité activé (0,5 pt chacune) + corrections (0,5 pt)."),
            _c("Comptes corrects", 1, "cdupont, adm-tleroy (compte d'administration séparé) et jmartin."),
        ),
        correction=(
            f"accueil : {ERR_SHARED} (créer trois comptes, puis désactiver accueil). tleroy : {ERR_ADMIN} → le retirer de {ADMINS_DOMAIN}, adm-tleroy suffit. mvincent : {ERR_LEFT} (sauvegarder ses données puis supprimer après le délai). Invité : {ERR_GUEST}.",
            f"Restent corrects : cdupont et jmartin (groupes métier seulement) et adm-tleroy, compte nominatif réservé à l'administration. Total : {len(E20_ERRORS)} erreurs.",
        ),
    ),
)

# =============================================================================================
# Mini-examen /20 (10 questions × 2 points, réponses libres, « Examen blanc » uniquement)
# =============================================================================================

EXAM_ITEMS: tuple[PR06Item, ...] = (
    PR06Item(
        key="X01",
        usage=USAGE_EXAM,
        title="Conseiller un cabinet médical",
        question_type="long_answer",
        requirement_ids=("AP-24",),
        kind=KIND_MODEL,
        context=(
            "Un cabinet médical de 14 postes travaille aujourd'hui en groupe de travail. Des médecins remplaçants "
            "arrivent et partent chaque mois et utilisent n'importe quel poste libre ; la secrétaire passe ses "
            "journées à créer des comptes. Le gérant hésite à acheter un serveur."
        ),
        instructions=("Conseille groupe de travail ou domaine et justifie par trois arguments liés à la situation.",),
        criteria=(
            _c("Choix", 0.5, f"{X01_MODEL}."),
            _c("Arguments", 1.5, "Plus d'une dizaine de postes ; un compte par personne valable sur tous les postes (remplaçants qui changent de poste) ; création et désactivation en un seul endroit ; règles communes (stratégies) ; coût : un serveur contrôleur (0,5 pt par argument, 3 attendus)."),
        ),
        correction=(
            "Un domaine Active Directory. Avec 14 postes, un remplaçant qui change de poste devrait avoir un compte local sur chacun : des dizaines de comptes à créer, puis à supprimer à son départ.",
            "En domaine, un seul compte par personne ouvre tous les postes ; on le crée à l'arrivée et on le désactive au départ, en un seul endroit ; les règles (verrouillage, mots de passe) s'appliquent à tous par les stratégies de groupe. Il faut un serveur contrôleur de domaine (idéalement deux) : c'est l'investissement à prévoir.",
        ),
    ),
    PR06Item(
        key="X02",
        usage=USAGE_EXAM,
        title="Emma ne peut pas ouvrir de session sur PC-3",
        question_type="short_answer",
        requirement_ids=("AP-24",),
        kind=KIND_ACCOUNT,
        context=(
            "Dans une agence en groupe de travail, Emma ouvre une session sur PC-1 et sur PC-2 sans problème. "
            "Aujourd'hui, PC-1 est en panne ; elle s'assied devant PC-3 et tape le même nom et le même mot de "
            "passe : « Nom d'utilisateur ou mot de passe incorrect ». Comptes de PC-3 : zoe."
        ),
        instructions=("Explique la cause et la solution, puis la limite du groupe de travail que cela montre.",),
        criteria=(
            _c("Cause et solution", 1.5, "En groupe de travail, chaque poste vérifie ses propres comptes : PC-3 n'a pas de compte emma ; créer un compte local emma avec mot de passe sur PC-3 (ou utiliser un poste où elle a un compte)."),
            _c("Limite", 0.5, "Comptes à créer et mots de passe à tenir à jour poste par poste."),
        ),
        correction=(
            "Le compte emma n'existe que sur PC-1 et PC-2 : en groupe de travail, il n'y a pas de base de comptes commune, chaque poste vérifie lui-même le nom et le mot de passe. PC-3 ne connaît que zoe. On crée un compte local emma (standard, avec mot de passe) sur PC-3.",
            "Cela montre la limite du groupe de travail : chaque compte est à créer et à maintenir sur chaque poste utilisé, ce qui devient ingérable quand les postes ou les personnes sont nombreux.",
        ),
    ),
    PR06Item(
        key="X03",
        usage=USAGE_EXAM,
        title="Domaine introuvable au moment de la jonction",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            f"Tu joins PC-11 au domaine {DNS_DOMAIN}. Windows indique que le contrôleur de domaine n'a pas pu "
            f"être contacté. Le contrôleur DC01 est en {DC_IP} et répond au ping depuis PC-11. Le document 1 est "
            "le relevé du poste, configuré par la box en DHCP."
        ),
        documents=(_console("Document 1 — ipconfig /all sur PC-11 (capture fictive)", *ipconfig_dns_lines(X03_WS)),),
        instructions=("Donne la cause et la correction durable pour tous les postes, puis le test.",),
        criteria=(
            _c("Cause", 1, f"DNS du poste = box {BOX_IP}, qui ne connaît pas {DNS_DOMAIN} : le poste ne trouve pas le contrôleur ; le réseau fonctionne (ping)."),
            _c("Correction et test", 1, f"DNS = {DC_IP} distribué par le DHCP (option DNS de la box ou DHCP sur le serveur) ; ipconfig /renew ; nslookup {DNS_DOMAIN} renvoie {DC_IP} ; jonction."),
        ),
        correction=(
            f"Le réseau est bon (ping), mais le poste interroge la box ({BOX_IP}) comme DNS. La box ne connaît pas le domaine {DNS_DOMAIN} : le poste ne peut pas localiser le contrôleur. Piste : {X03_DIAG.split(' :')[0]}.",
            f"Pour que tous les postes soient corrects, le DHCP doit distribuer {DC_IP} comme DNS (option DNS de la box, ou rôle DHCP confié au serveur). Sur PC-11 : ipconfig /renew, ipconfig /all montre {DC_IP}, nslookup {DNS_DOMAIN} répond {DC_IP} ; puis jonction.",
        ),
    ),
    PR06Item(
        key="X04",
        usage=USAGE_EXAM,
        title="L'horloge d'un portable",
        question_type="short_answer",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            "Un commercial revient d'un salon à l'étranger. Sur le réseau de l'entreprise, son portable du domaine "
            "refuse la connexion avec un message signalant une différence d'heure. Le contrôleur affiche 14:30, "
            "le portable 14:18. Les autres postes fonctionnent ; réseau et DNS du portable sont corrects."
        ),
        instructions=("Explique la cause, la correction et une vérification à faire pour éviter que cela revienne.",),
        criteria=(
            _c("Cause", 1, f"12 minutes d'écart, plus que la tolérance Kerberos de {MAX_CLOCK_SKEW_MIN} minutes : authentification refusée."),
            _c("Correction", 1, "Corriger heure et fuseau horaire (réglé à la main à l'étranger ?), w32tm /resync, réglage automatique de l'heure activé ; nouvelle connexion."),
        ),
        correction=(
            f"L'écart est de 12 minutes. L'authentification du domaine (Kerberos) refuse un écart supérieur à {MAX_CLOCK_SKEW_MIN} minutes. Piste : {X04_DIAG.split(' :')[0]}.",
            "On corrige l'heure et le fuseau horaire (probablement modifiés à la main pendant le voyage), puis w32tm /resync et on vérifie que le réglage automatique de l'heure est actif : en domaine, le poste se synchronise sur le contrôleur. Connexion d'essai.",
        ),
    ),
    PR06Item(
        key="X05",
        usage=USAGE_EXAM,
        title="Un poste rejeté par le domaine",
        question_type="short_answer",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            "Un poste éteint et rangé pendant un an est remis en service. Toutes les ouvertures de session du "
            "domaine affichent : « La relation d'approbation entre cette station de travail et le domaine principal "
            "a échoué ». Les autres postes fonctionnent ; réseau, DNS et heure sont corrects."
        ),
        instructions=("Explique la cause et la correction, avec le test.",),
        criteria=(
            _c("Cause", 1, "Le compte d'ordinateur du poste ne correspond plus au domaine (mot de passe du compte d'ordinateur, compte supprimé ou désactivé pendant l'année)."),
            _c("Correction et test", 1, "Session locale administrateur ; Test-ComputerSecureChannel -Repair (compte autorisé) ou sortir du domaine et le rejoindre ; nltest /sc_query réussi ; session du domaine."),
        ),
        correction=(
            "Un poste du domaine possède un compte d'ordinateur. Après un an, ce compte a pu être supprimé ou désactivé par un nettoyage, ou son mot de passe ne correspond plus : le domaine ne fait plus confiance au poste (relation d'approbation rompue).",
            "On ouvre une session locale d'administration, puis on répare le canal sécurisé (Test-ComputerSecureChannel -Repair avec un compte autorisé du domaine) ou, si le compte d'ordinateur a été supprimé, on sort le poste du domaine et on le rejoint. Test : nltest /sc_query réussi, puis session du domaine.",
        ),
    ),
    PR06Item(
        key="X06",
        usage=USAGE_EXAM,
        title="Départ d'une employée",
        question_type="long_answer",
        requirement_ids=("AP-24",),
        kind=KIND_ACCOUNT,
        context=(
            "Une comptable quitte une PME en domaine ce vendredi à 17 h. Elle était dans G_Compta et accédait à "
            "la messagerie et au dossier Compta. Le gérant demande « supprime son compte tout de suite » ; ses "
            "dossiers personnels contiennent encore des fichiers de clients."
        ),
        instructions=("Décris ce que tu fais vendredi et plus tard, et justifie pourquoi tu ne supprimes pas immédiatement.",),
        criteria=(
            _c("Vendredi", 1, "Désactiver le compte à l'heure du départ ; le retirer des groupes ; mot de passe changé si besoin ; noter la date."),
            _c("Plus tard et justification", 1, "Sauvegarder et confier ses fichiers ; supprimer après le délai prévu ; la suppression est définitive (identité, fichiers, historique perdus) alors que la désactivation bloque l'accès tout de suite et reste réversible."),
        ),
        correction=(
            "Vendredi à 17 h : on désactive le compte (plus aucune connexion possible), on le retire de G_Compta et des autres groupes et on note l'opération. Ses accès sont coupés immédiatement.",
            "Ensuite : on sauvegarde ses fichiers et on les confie à son successeur, puis on supprime le compte après le délai prévu par l'entreprise. Supprimer tout de suite effacerait une identité qu'on ne peut pas recréer à l'identique (droits, historique) et ferait perdre l'accès aux fichiers ; désactiver protège autant, et reste réversible.",
        ),
    ),
    PR06Item(
        key="X07",
        usage=USAGE_EXAM,
        title="Le comptable veut être administrateur",
        question_type="short_answer",
        requirement_ids=("AP-24",),
        kind=KIND_ACCOUNT,
        context=(
            "Dans une PME en domaine, le comptable doit installer deux fois par an la mise à jour de son logiciel "
            "de comptabilité. Il demande que son compte jmartin soit ajouté au groupe « Admins du domaine » « pour "
            "ne plus déranger personne ». Tu dois lui répondre par écrit."
        ),
        instructions=("Refuse ou accepte en justifiant, et propose une solution respectant le moindre privilège.",),
        criteria=(
            _c("Refus justifié", 1, "Admins du domaine = droits d'administration sur tous les postes et le domaine ; un compte de tous les jours ne doit pas les avoir (logiciel malveillant, erreur)."),
            _c("Solution", 1, "Installation faite par le technicien avec son compte adm- (ou déploiement) ; à défaut, droit limité à son seul poste et au temps nécessaire ; jamais Admins du domaine."),
        ),
        correction=(
            f"Refus : « {ADMINS_DOMAIN} » donne les droits d'administration sur tous les postes et sur le domaine. Un compte qui lit les courriels et navigue sur le web ne doit pas les avoir : un logiciel malveillant ou une erreur aurait les mêmes droits. C'est le principe du moindre privilège.",
            "Solution : le technicien installe la mise à jour avec son compte d'administration séparé (adm-…), ou la déploie à distance ; si l'entreprise veut l'autonomie du comptable, on lui donne un droit limité à son seul poste et seulement le temps de l'installation.",
        ),
    ),
    PR06Item(
        key="X08",
        usage=USAGE_EXAM,
        title="Accès refusé malgré le bon groupe",
        question_type="document_analysis",
        requirement_ids=("AP-24",),
        kind=KIND_DIAG,
        context=(
            "Luc Bernard est nommé directeur adjoint. À 11 h, le technicien l'ajoute au groupe G_Direction, qui a "
            "Modification sur le dossier Direction. À 11 h 30, Luc, dont la session est ouverte depuis le matin, "
            "reçoit « Accès refusé » sur ce dossier. Le document 1 est relevé sur son poste."
        ),
        documents=(_console("Document 1 — whoami sur le poste de Luc (capture fictive)", *whoami_groups_lines(X08_ACCOUNT)),),
        instructions=("Explique le relevé, la solution et le test.",),
        criteria=(
            _c("Explication", 1, "G_Direction absent de whoami /groups : la session ouverte le matin garde les groupes lus à l'ouverture."),
            _c("Solution et test", 1, "Fermer et rouvrir la session ; whoami /groups montre G_Direction ; le dossier Direction s'ouvre en Modification."),
        ),
        correction=(
            "whoami /groups montre les groupes de la session : G_Direction n'y figure pas. Les groupes sont lus à l'ouverture de session ; l'ajout de 11 h n'est pas encore pris en compte dans la session ouverte le matin.",
            "Luc ferme sa session et la rouvre (ou redémarre) ; whoami /groups affiche alors DUPONT\\G_Direction, et le dossier Direction s'ouvre en Modification. Inutile de modifier les droits du dossier.",
        ),
    ),
    PR06Item(
        key="X09",
        usage=USAGE_EXAM,
        title="Quel nom taper à la connexion ?",
        question_type="short_answer",
        requirement_ids=("AP-24",),
        kind=KIND_ACCOUNT,
        context=(
            f"Un poste PC-08 est membre du domaine {DNS_DOMAIN} (nom court {NETBIOS_DOMAIN}). Il a aussi un compte "
            "local de secours « support ». L'employée Inès Robert a pour identifiant irobert. Le technicien doit "
            "écrire, sur la fiche d'intervention, comment se connecter avec chacun des deux comptes."
        ),
        instructions=("Écris deux formes pour le compte d'Inès et deux formes pour le compte local, et dis qui vérifie chaque mot de passe.",),
        criteria=(
            _c("Formes", 1, f"{NETBIOS_DOMAIN}\\irobert et irobert@{DNS_DOMAIN} ; .\\support et PC-08\\support."),
            _c("Qui vérifie", 1, "Compte du domaine : le contrôleur de domaine ; compte local : le poste PC-08 lui-même."),
        ),
        correction=(
            f"Compte du domaine d'Inès : {NETBIOS_DOMAIN}\\irobert (nom NetBIOS du domaine) ou irobert@{DNS_DOMAIN} (UPN, nom DNS du domaine) ; le mot de passe est vérifié par le contrôleur de domaine.",
            "Compte local : .\\support (le point désigne ce poste) ou PC-08\\support ; le mot de passe est vérifié par PC-08 lui-même, ce compte n'existe que sur ce poste et fonctionne même sans contrôleur.",
        ),
    ),
    PR06Item(
        key="X10",
        usage=USAGE_EXAM,
        title="Fiche comptes et groupes d'une association de 6 postes",
        question_type="long_answer",
        requirement_ids=("AP-24",),
        kind=KIND_SHEET,
        context=(
            "Une association de 6 postes, sans serveur, garde ses bénévoles depuis des années. Chaque bénévole "
            "a son poste ; la trésorière doit seule modifier le dossier « Trésorerie » partagé par son poste, que "
            "le président lit. Un technicien bénévole administre les postes."
        ),
        instructions=("Propose le modèle, les comptes et les groupes ou droits, en appliquant le moindre privilège.",),
        criteria=(
            _c("Modèle et comptes", 1, "Groupe de travail (6 postes stables, sans serveur) ; un compte local standard nominatif avec mot de passe par personne sur son poste ; sur le poste de la trésorière, aussi un compte pour le président ; administrateur séparé (compte d'administration distinct) ; Invité désactivé."),
            _c("Droits", 1, "Trésorerie : trésorière Modification, président Lecture, personne d'autre ; comptes du quotidien hors du groupe Administrateurs."),
        ),
        correction=(
            "Six postes stables sans serveur : un groupe de travail suffit. Chaque bénévole a un compte local standard, nominatif, avec mot de passe, sur son poste. Sur le poste de la trésorière, on crée aussi un compte pour le président, qui ouvre le partage Trésorerie par le réseau.",
            "Droits : Trésorerie → trésorière en Modification, président en Lecture (partage et dossier), retirer Tout le monde. Le technicien utilise un compte d'administration distinct sur chaque poste ; les comptes du quotidien ne sont pas dans le groupe Administrateurs ; le compte Invité reste désactivé.",
        ),
    ),
)

ALL_ITEMS: tuple[PR06Item, ...] = PRACTICE_ITEMS + EXAM_ITEMS
EXAM_TOTAL_POINTS = 20


def validate_items() -> list[str]:
    """Contrôles éditoriaux : format d'exercice du socle (#192), 2 points par question du
    mini-examen, réponses libres à l'examen, données des classements et remises en ordre,
    exigence du cours citée, schémas à compléter, relevés et fiches demandés par le ticket."""
    errors: list[str] = []
    for item in ALL_ITEMS:
        errors += [f"{item.key} : {e}" for e in validate_exercise(item.as_exercise())]
        if item.question_type == "classification" and (
            item.classification is None
            or len(item.classification.correct) != len(item.classification.elements)
            or len(set(item.classification.elements)) != len(item.classification.elements)
            or max(item.classification.correct) >= len(item.classification.categories)
        ):
            errors.append(f"{item.key} : classification incohérente.")
        if item.question_type == "ordering" and (
            item.ordering is None
            or sorted(item.ordering.correct) != list(range(len(item.ordering.steps)))
            or list(item.ordering.correct) == list(range(len(item.ordering.steps)))
        ):
            errors.append(f"{item.key} : remise en ordre invalide ou déjà dans l'ordre attendu.")
        if item.question_type == "document_analysis" and not item.documents:
            errors.append(f"{item.key} : analyse de document sans document.")
        if not REQ & set(item.requirement_ids):
            errors.append(f"{item.key} : au moins une exigence du cours doit être citée.")
    for item in EXAM_ITEMS:
        if abs(item.total_points - 2) > 1e-9:
            errors.append(f"{item.key} : une question du mini-examen vaut 2 points.")
        if item.question_type not in ("short_answer", "long_answer", "document_analysis"):
            errors.append(f"{item.key} : le mini-examen n'accepte que des réponses libres.")
    if len(PRACTICE_ITEMS) < 16:
        errors.append("Ticket #222 : au moins 16 exercices.")
    schemas = [i for i in PRACTICE_ITEMS if i.kind == KIND_SCHEMA and any(d.image for d in i.documents)]
    if len(schemas) < 4:
        errors.append("Ticket #222 : au moins 4 schémas à compléter.")
    if sum(1 for i in PRACTICE_ITEMS if i.kind == KIND_SHEET) < 3:
        errors.append("Ticket #222 : au moins 3 fiches comptes et groupes.")
    if sum(1 for i in PRACTICE_ITEMS if any(d.kind == "console" for d in i.documents)) < 5:
        errors.append("Ticket #222 : au moins 5 exercices avec des relevés de commandes.")
    expected = {"E12": D_DNS, "E13": D_TIME, "E14": D_TRUST, "E15": D_ACCOUNT, "E16": D_RIGHTS,
                "X03": D_DNS, "X04": D_TIME}
    found = {"E12": E12_DIAG, "E13": E13_DIAG, "E14": E14_DIAG, "E15": E15_DIAG, "E16": E16_DIAG,
             "X03": X03_DIAG, "X04": X04_DIAG}
    if found != expected:
        errors.append("Diagnostics des relevés inattendus.")
    if E12_BLOCKERS != ["DNS"]:
        errors.append("E12 : seul le DNS doit bloquer la jonction.")
    if len(E20_ERRORS) != 4:
        errors.append("E20 : la fiche doit contenir exactement 4 erreurs.")
    if set(E04_ANSWERS) != {MODEL_WG, MODEL_DOMAIN} or set(E05_ANSWERS) != {SCOPE_LOCAL, SCOPE_DOMAIN}:
        errors.append("E04/E05 : catégories inutilisées.")
    if {logon_diagnosis(first_failure(k)) for _t, k in E06_CASES} != set(DIAGNOSES) or D_NET not in DIAGNOSES:
        errors.append("E06 : toutes les pistes doivent être utilisées.")
    if (E16_BEFORE, E16_AFTER) != ("Aucun accès", "Modification"):
        errors.append("E16 : droits avant/après reconnexion inattendus.")
    return errors
