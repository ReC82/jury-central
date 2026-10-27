# Ticket #223 — [AMPCR pratique PR23] Partage de dossiers, imprimantes et permissions

- Ticket : https://github.com/ReC82/jury-central/issues/223
- **État réel : Installé — à tester**
- SHA installé : `dbaec62c23aad6ee873a96bcb2bae52c53087807` (fusion de la PR #293 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR23 « Partage de dossiers, imprimantes et permissions »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie MC
(cours, banque, examen et progression distincts ; liens seulement vers MC33 et MC10). Il occupe
la position 23 de l'ordre pédagogique : après PR22, avant PR24.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation de #236),
l'emplacement PR23 porte bien le sujet du ticket (« PR23, ticket 223, Partage de dossiers,
imprimantes et permissions », exigences officielles p. 6 : AP-25 « Partage de ressources
(imprimantes, disques, répertoires…) », AP-26 « Mise en partage sur un réseau informatique de
documents et applications », AP-27 « Les notions de droit et de permission »). Aucun autre cours
n'a été touché ni renuméroté.

### Contenu (16 blocs)

**9 chapitres**, chacun avec objectifs, théorie, procédure professionnelle à rédiger, erreur
fréquente, attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Partage Windows SMB et chemins UNC** : SMB sur TCP 445, SMB1 obsolète, Partage avancé,
   `net share` / `New-SmbShare`, partages administratifs, `\\serveur\partage\chemin` par nom ou
   adresse IP, lecteur réseau `net use`.
2. **Profil réseau, découverte, pare-feu, authentification** : Privé / Domaine / Public, règle
   « Partage de fichiers et d'imprimantes », découverte = affichage seulement, test du port 445
   (`Test-NetConnection`), compte avec mot de passe, accès invité bloqué, un compte par serveur
   (erreur 1219).
3. **Permissions de partage et NTFS** : tableau comparatif, Lecture / Modification / Contrôle
   total, autorisations du serveur de référence, `icacls`.
4. **Combinaison effective, héritage, groupes** : cumul des groupes, refus explicite, refus
   hérité, par le réseau la plus restrictive, en local NTFS seul ; **matrice des droits** calculée
   (3 comptes × 6 dossiers) ; héritage et désactivation (dossier Paie).
5. **Linux (complément)** : rwx, octal, setgid, ACL (`setfacl`/`getfacl`), Samba (`smb.conf`
   `valid users`, `read only`, `write list`, `testparm`, `smbpasswd -a`), double barrière.
6. **Imprimantes partagées** : USB sur un poste hôte, imprimante réseau via serveur
   d'impression, impression directe par IP ; file d'attente (spouleur), accès local ou distant,
   pilotes (installation réservée aux administrateurs depuis août 2021), droits, pare-feu.
7. **Diagnostiquer un accès** : ordre IP → nom → port 445 → nom du partage → compte →
   permissions ; « ping OK mais accès refusé », « nom du serveur introuvable », « droits
   insuffisants » ; messages 5, 53, 67, 86, 1219 ; `net view`.
8. **Imprimante hors connexion et file bloquée** : ordre hôte → imprimante et adresse → file →
   pilote → droit ; adresse DHCP changée ; arrêt / vidage / redémarrage du spouleur.
9. **Protection des données et moindre privilège**.

**3 procédures illustrées** : partager un dossier (7 étapes), partager une imprimante (7),
dépanner un accès (8).

**5 cas résolus** : partage en groupe de travail (bureau de géomètres) ; secrétariat ajouté dans
NTFS mais pas dans le partage ; vieux NAS en SMB1 ; pilote d'imprimante refusé ; partage Samba
d'un atelier.

**20 exercices corrigés** (le ticket en demande au moins 18 « de matrices de droits et
diagnostics »), avec contexte, consignes, barème et corrigé : 3 remises en ordre ; 4 classements
auto-corrigés (droit minimal, piste d'un échec d'accès, piste d'une panne d'impression, accès
Samba) ; **4 schémas à compléter** (chemin UNC, deux barrières, imprimantes, droits Unix),
affichés en SVG ; **matrices de droits** (matrice complète d'un serveur, refus explicite,
local / réseau, plan de partage d'un cabinet) ; **relevés de commandes** (ping, net use, dir,
net share, icacls, Get-Printer, ls, getfacl, smb.conf) : héritage non voulu, ping OK mais accès
refusé, nom introuvable, imprimante hors connexion, Samba en lecture seule.

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours).

**12 figures SVG + 4 schémas à compléter**, produits depuis des données testées ; texte
alternatif, légende, mention « schéma non officiel ». **Aucune image générée.**

### Fichiers

- `app/v1/ampcr_pratique_pr23_figures.py` — données et calculs (`layer_level`, `ntfs_acl`,
  `effective_access`, `limiting_layer`, `access_matrix`, `mode_string`, `unix_access`,
  `samba_level`, `linux_effective`, `share_checks`/`share_diagnosis`,
  `print_checks`/`print_diagnosis`), relevés fictifs, figures.
- `app/v1/ampcr_pratique_pr23_bank.py` — 20 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr23_course.py` — les 16 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR23 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR23", …, position 23)`, ajout seul.
- `app/static/img/ampcr-pratique/pr23-*.svg` (4 fichiers).
- `tests/test_ticket223_ampcr_pratique_pr23.py` (33 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket222_ampcr_pratique_pr22.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr23
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr23/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr23/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 16 séquences (chapitres, cas résolus, exercices avec les 4 schémas à compléter).
2. « S'entraîner » : 10 exercices tirés des 20 (schémas et relevés affichés dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket223_ampcr_pratique_pr23.py` : **33 passed** — règles de
  droits recalculées indépendamment (cumul, refus explicite, refus hérité contre autorisation
  explicite, héritage, désactivation) ; matrice des droits attendue écrite à la main ; local ≥
  réseau ; rwx, setgid, ACL, Samba ; ordre des diagnostics d'accès et d'impression ; largeur
  (≤ 56 caractères) de toutes les captures ; figures (validité, accessibilité, données
  dessinées) ; schémas à compléter sans leurs réponses ; fichiers statiques identiques au SVG
  généré ; exercices (format du socle, auto-correction, valeurs des corrigés) ; cours (matière du
  ticket, 5 cas, 3 procédures, examen absent, liens, pas de lien vers PR25 non publié) ; **rendu
  Markdown des chemins UNC** (aucun `\\serveur` réduit à une seule barre) ; types de cartes ;
  seed idempotent et position ; réserves séparées ; contexte de correction ; pages ; sessions
  d'entraînement et d'examen /20 sans génération IA.
- **Suite complète** (une exécution, `seed.py` partagé) : **3 015 passed**, aucun échec (30 min).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (Chromium sans interface) des 16 schémas ; corrigés pendant la session :
  colonne des dossiers de la matrice trop étroite, titre « Accès par Samba » qui débordait,
  liaison imprimante réseau / switch.
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket223-20261027-144229.db` ;
  avance rapide `b3f7848 → dbaec62` ; seed : 1 UAA et 68 blocs créés (16 de PR23 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR23, PR22,
  accueil, matrice et schéma statique en HTTP 200 ; entraînement en 303 vers la connexion
  (normal sans session) ; 20 cartes d'exercice servies ; « 24 cours publiés sur 30 » ; compteurs
  utilisateurs / sessions / réponses inchangés (18 / 84 / 658).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Périmètre** : le partage entre deux PC (PR21), les comptes et groupes (PR22), le dépannage
  réseau (PR24) et Linux (PR09) sont liés, pas répétés.
- **Réseau et domaine de PR22 réutilisés** (`ad.dupont.example`, `DUPONT`, 192.168.20.0/24) ;
  serveur de fichiers `SRV-FICH` en .20, serveur Linux en .40, imprimante réseau en .50.
- **Échelle simplifiée** Aucun accès < Lecture < Modification < Contrôle total, signalée comme
  convention ; « Écriture » seule et les autorisations spéciales sont citées, pas calculées.
- **Refus** modélisé comme « Refuser : Contrôle total » ; règle exacte : refus explicite gagne,
  autorisation explicite bat un refus hérité. Les refus sont montrés en tableau de l'onglet
  Sécurité, pas en sortie `icacls` (format non reproduit pour éviter une capture inexacte).
- **Bonne pratique de partage** : présentée comme « partage large pour les utilisateurs
  authentifiés et détail dans NTFS » (pratique Microsoft) **ou** les deux réglés pareil ;
  l'essentiel évalué est de savoir quelle barrière limite.
- **Diagnostic « accès refusé »** : `net use` échoue (erreur 5) quand le partage refuse ; quand
  seul NTFS refuse, la connexion réussit et l'ouverture du dossier est refusée (relevé `dir`).
- **Linux** traité en complément (signalé), avec ACL au masque `rwx`.
- Schémas à compléter servis en fichiers statiques, comme PR18 à PR22.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestion (hors périmètre, non faite) : PR18, PR19, PR21 et PR22 citent « PR23 » sans lien
  (il n'était pas publié) ; un lien vers `/uaa/ampcr-pratique-pr23` pourrait y être ajouté lors
  d'une prochaine retouche.
