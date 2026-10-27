# Ticket #222 — [AMPCR pratique PR22] Domaine, groupe de travail, comptes et groupes

- Ticket : https://github.com/ReC82/jury-central/issues/222
- **État réel : Installé — à tester**
- SHA installé : `67b654ef5fa8664583a7cceebe6a61881777fbed` (fusion de la PR #291 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR22 « Domaine, groupe de travail, comptes et groupes »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie MC
(cours, banque, examen et progression distincts ; liens seulement vers MC33 et MC10). Il occupe
la position 22 de l'ordre pédagogique : après PR21, avant PR24.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive de
#236), l'emplacement PR22 porte bien le sujet du ticket (« PR22, ticket 222, Domaine, groupe de
travail, comptes et groupes », exigence officielle AP-24 « Notions de domaine, groupe de travail,
comptes utilisateurs et groupes d'utilisateurs », p. 6). Aucun autre cours n'a été touché ni
renuméroté.

### Contenu (16 blocs)

**9 chapitres**, chacun avec objectifs, théorie, procédure professionnelle à rédiger, erreur
fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Groupe de travail** : comptes locaux, gestion décentralisée, un compte sur chaque poste
   utilisé et sur le poste qui partage ; nombre de comptes calculé (8 comptes pour 4 personnes
   dans l'exemple ; 5/10/21/44 comptes contre 3/5/10/20 en domaine).
2. **Domaine Active Directory** : annuaire, contrôleur(s) à adresse fixe, DNS du domaine (DNS des
   postes = contrôleur, box = passerelle), authentification Kerberos (5 minutes d'écart au plus),
   comptes d'utilisateurs et **comptes d'ordinateurs** ; tableau comparatif.
3. **Domaine DNS et domaine d'administration**, nom NetBIOS, choix du nom (sous-domaine possédé,
   pas `.local`), formes de connexion `DUPONT\nom`, `nom@ad.dupont.example`, `.\nom`, `POSTE\nom`.
4. **Jonction d'un poste** : prérequis (édition Pro, nom ≤ 15 caractères et unique, réseau, DNS,
   heure, compte autorisé), interface et `Add-Computer`, redémarrage, contrôles (`whoami`,
   `gpresult /r`, `nltest /sc_query`).
5. **Comptes** local / domaine, administrateur / standard, comptes intégrés, compte
   d'administration séparé (`adm-…`), un compte par personne.
6. **Groupes et stratégies** : droits aux groupes, groupes métier, « Admins du domaine » →
   Administrateurs locaux et « Utilisateurs du domaine » → Utilisateurs locaux à la jonction,
   reconnexion après ajout, GPO par unité d'organisation.
7. **Mots de passe, moindre privilège, désactivation** (déverrouiller ≠ réinitialiser ;
   désactiver le jour du départ, supprimer plus tard).
8. **Dépannage** de l'ouverture de session / accès refusé : réseau → DNS → heure → relation
   d'approbation → compte → droits ; messages Windows ; relevés nslookup, net time, nltest.
9. **Organisations de 3 à 20 postes** : repère et tableau de six organisations.

**3 procédures illustrées** : jonction (7 étapes), vie d'un compte (7), dépannage (8).

**5 cas résolus** : bureau de 5 personnes en groupe de travail ; DNS de secours sur la box ;
horloge décalée ; groupe ajouté sans reconnexion ; passage d'une fiduciaire de 11 postes en domaine.

**20 exercices corrigés** (le ticket en demande au moins 16), avec contexte, consignes, barème et
corrigé : 3 remises en ordre ; 4 classements auto-corrigés (modèle, compte local ou du domaine,
piste d'un échec de connexion, action sur un compte) ; **4 schémas à compléter** (domaine, noms,
groupe de travail, fiche des groupes), affichés en SVG dans le cours et dans les sessions ;
**5 relevés de commandes** (ipconfig + nslookup, net time, nltest, net user, whoami) ;
**fiches comptes et groupes** (rédiger celle d'un cabinet de 12 postes, comptes d'un groupe de
travail, audit d'une fiche) ; choix du nom de domaine.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours).

**11 figures SVG + 4 schémas à compléter**, produits depuis des données testées ; texte
alternatif, légende, mention « schéma non officiel ». **Aucune image générée.**

### Fichiers

- `app/v1/ampcr_pratique_pr22_figures.py` — données et calculs (`workgroup_accounts`,
  `office_accounts`, `logon_forms`, `account_scope`, `join_blockers`, `access_of`,
  `account_errors`, `recommend_model`, `LOGON_CHECKS`/`logon_checks`/`logon_diagnosis`), relevés
  fictifs, figures.
- `app/v1/ampcr_pratique_pr22_bank.py` — 20 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr22_course.py` — les 16 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR22 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR22", …, position 22)`, ajout seul.
- `app/static/img/ampcr-pratique/pr22-*.svg` (4 fichiers).
- `tests/test_ticket222_ampcr_pratique_pr22.py` (34 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket221_ampcr_pratique_pr21.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr22
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr22/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr22/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 16 séquences (chapitres, cas résolus, exercices avec les 4 schémas à compléter).
2. « S'entraîner » : 10 exercices tirés des 20 (schémas et relevés affichés dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket222_ampcr_pratique_pr22.py` : **34 passed** — comptes locaux
  d'un groupe de travail recomptés indépendamment (exemple, organisations de 3 à 20 personnes) ;
  formes de connexion et portée (local / domaine) ; prérequis de jonction (édition Famille, nom
  > 15 caractères ou en double, réseau, DNS de la box même en second, heure ±5 min) ;
  imbrication des groupes et droits avant / après reconnexion ; audit d'une fiche de comptes ;
  choix du modèle ; ordre du diagnostic et cumul de pannes ; largeur (≤ 56 caractères) de toutes
  les captures ; figures (validité, accessibilité, données dessinées) ; schémas à compléter sans
  leurs réponses et fichiers statiques identiques au SVG généré ; exercices (format du socle,
  auto-correction, nombres des corrigés) ; cours (matière du ticket, 5 cas, 3 procédures, examen
  absent, liens, pas de lien vers PR23/PR25 non publiés, types de cartes) ; seed idempotent et
  position ; réserves séparées ; contexte de correction ; pages ; sessions d'entraînement et
  d'examen /20 sans génération IA.
- **Suite complète** (une exécution, `seed.py` partagé) : **2 982 passed**, aucun échec.
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (navigateur sans interface) des 15 schémas ; corrigés pendant la session :
  titre de PC-1 et libellés des barres qui débordaient, lignes des postes du domaine tronquées
  (passerelle), cases de groupes trop étroites, imbrication des groupes illisible, espace vide
  sous le schéma du groupe de travail.
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket222-20261027-131353.db` ;
  avance rapide `e70299b → 67b654e` ; seed : 1 UAA et 68 blocs créés (16 de PR22 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR22, PR21,
  accueil, matrice et schéma statique en HTTP 200 ; entraînement en 303 vers la connexion
  (normal sans session) ; 20 cartes d'exercice servies ; « 23 cours publiés sur 30 » ; compteurs
  utilisateurs / sessions / réponses inchangés (18 / 84 / 658).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Périmètre** : comptes locaux, UAC et `net user` déjà vus en PR10 (lien) ; permissions de
  partage et NTFS détaillées laissées à PR23 (cité sans lien, non publié) ; réseau de PR20/PR21,
  dépannage réseau de PR24 (liens).
- **Domaine fictif `ad.dupont.example`** (TLD réservé RFC 2606/6761), NetBIOS `DUPONT`, réseau
  192.168.20.0/24 (contrôleur .10, box .254) pour ne pas réutiliser le réseau de PR21.
- **Repère « groupe de travail jusqu'à une dizaine de postes stables »** présenté comme
  convention du cours, pas comme limite technique ; domaine dès qu'il y a rotation du personnel,
  itinérance ou règles communes.
- **DNS** : un DNS qui ne connaît pas le domaine (box, DNS public) est une erreur même en
  second serveur ; le contrôleur relaie Internet.
- **Mots de passe** : pas d'affirmation sur des valeurs par défaut de stratégie hormis la
  tolérance Kerberos de 5 minutes ; recommandation « longue et unique » plutôt que changement
  périodique.
- **Relevés** (`net user`, `whoami /groups`, `nltest`, `nslookup`, `net time`) simplifiés au
  format réel, 56 caractères par ligne ; « Compte : actif » vaut Oui / Non / Verrouillé comme
  sous Windows.
- Linux et Microsoft Entra ID non traités (hors matière du ticket ; `realm join` seulement cité).
- Schémas à compléter servis en fichiers statiques, comme PR18/PR19/PR21.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestion (hors périmètre, non faite) : PR10 mentionne « détails PR22 » sans lien ; un lien
  vers `/uaa/ampcr-pratique-pr22` pourrait y être ajouté lors d'une prochaine retouche.
