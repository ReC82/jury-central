# Ticket #214 — [AMPCR pratique PR10] Comptes, pilotes, paramètres et commandes

- Ticket : https://github.com/ReC82/jury-central/issues/214
- **État réel : Installé — à tester**
- SHA installé : `5f15369598026c5366d4ff3dcb237b9390fae8f1` (fusion de la PR #271 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR10 « Comptes, pilotes, paramètres et commandes »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`). Il est séparé de la
théorie MC : cours, banque, examen et progression distincts. Seuls des liens croisés renvoient
vers MC10, MC11 et MC12. C'est le dixième cours de l'ordre pédagogique, placé juste après PR09
(position 10).

**Numérotation vérifiée** : l'emplacement PR10 du plan installé (`_COURSE_ROWS`, numérotation
définitive de #236) porte bien le sujet du ticket (« PR10, ticket 214, Comptes, pilotes,
paramètres et commandes », exigences AP-05, AP-11, AP-12). Aucun écart, aucun autre cours touché
ni renuméroté.

Contenu (19 blocs) :

- **12 chapitres de théorie**. Chacun comprend les objectifs, la théorie, la **procédure
  professionnelle à rédiger**, l'**erreur fréquente**, ce qu'on attend « à l'écrit », un repère
  rapide et le renvoi aux exercices liés :
  1. **comptes locaux et de domaine**, standard / administrateur / intégré, compte Microsoft,
     **groupes** Windows et Linux, création et contrôle (`net user nom * /add`, `adduser`,
     `usermod -aG`) ;
  2. **UAC, sudo et moindre privilège** (tableau calculé : invite d'identifiants ou de
     consentement, sudo accepté ou refusé) ;
  3. **permissions Linux** : lecture de `ls -l`, schéma des triplets, `chmod` (chiffres et
     lettres), `chown`, tableau des modes courants, jamais 777 ;
  4. **pilotes** : rôle, sources fiables dans l'ordre, compatibilité (version, x64/ARM64,
     modèle, signature) ;
  5. **Gestionnaire de périphériques** : codes 28, 22, 10, 43 et **périphérique inconnu**
     (ID du matériel `PCI\VEN_&DEV_`, `USB\VID_&PID_`, fabricants), arbre de décision ;
  6. **installer, mettre à jour, restaurer** un pilote (point de restauration, « Restaurer le
     pilote », équivalent Linux) ;
  7. **paramètres du système** (outil Windows / Linux pour chaque tâche) et programmes au
     **démarrage** ;
  8. **services** Windows (état, types de démarrage) et systemd (`enabled`, `active`, `failed`,
     `enable --now`, `journalctl -u`) ;
  9. à 11. **fiches des 16 commandes du ticket**, une par commande, avec **syntaxe, rôle, sortie
     attendue, droits nécessaires, risques** : `ipconfig`, `ping`, `tracert`, `nslookup`, `ip` ;
     `sfc`, `DISM` (ordre DISM puis SFC, invite administrateur), `tasklist`, `net user` ;
     `systemctl`, `journalctl`, `lsblk`, `df`, `chmod`, `chown`, `apt`/`dnf` ;
  12. **liste de contrôle** et **rapport d'intervention** (jamais de mot de passe).
- **4 procédures illustrées** : créer un compte selon le moindre privilège ; intervenir sur un
  pilote ; remettre en route un service ; contrôler et corriger la configuration réseau.
- **5 cas résolus**, ceux qu'exige le ticket :
  1. **pilote absent** (Wi-Fi Broadcom, Code 28, ID du matériel) ;
  2. **droits insuffisants** (gestion des imprimantes par le groupe `lpadmin` plutôt que
     `sudo`) ;
  3. **service arrêté** (spouleur d'impression bloqué, file vidée) ;
  4. **périphérique USB** (disque externe sur un hub non alimenté, `lsblk`/`df`) ;
  5. **configuration réseau** (passerelle mal saisie, `ipconfig /all`, `ping`, `nslookup`).
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **17 exercices corrigés** (ticket : ≥ 16), dont **8 avec extraits de console ou captures** :
  - **3 remises en ordre** : compte, pilote, service ;
  - **5 classements** auto-corrigés : besoin → commande Windows, besoin → commande Linux,
    commande → droits nécessaires, besoin → compte, état du périphérique → première action ;
  - **exercices sur documents** : `net user` (administratrice sans raison), invite UAC, ID du
    matériel Code 28, permissions d'un dossier partagé (`id`, `ls -ld`), `systemctl status
    cups`, `lsblk`/`df` (disque non monté), `ipconfig`/`ping`/`nslookup` (DNS faux), `sfc`
    refusé puis incomplet → DISM ;
  - **procédure d'un collègue à corriger**.

  Chaque exercice a son contexte complet, ses consignes, un barème analytique et un corrigé.
- **Mini-examen 10 questions /20** (2 points chacune, réponses libres) dans « Examen blanc »,
  jamais affiché dans le cours. Thèmes :
  - plan de comptes d'un cabinet ;
  - compte local ou compte de domaine ;
  - restauration d'un pilote ;
  - imprimante USB inconnue (VID_04F9) ;
  - spouleur désactivé (`tasklist`) ;
  - `ssh` en échec (`journalctl`) ;
  - script non exécutable (`chmod u+x`) ;
  - absence de route par défaut (`ip route`) ;
  - lecture de `ping`, `nslookup` et `tracert` ;
  - droits et risques de trois commandes.
- **10 schémas SVG** produits depuis des données testées :
  - 4 procédures ;
  - lecture des permissions `ls -l` (triplets et valeurs octales) ;
  - arbre « un périphérique ne fonctionne pas » ;
  - 4 captures **clairement identifiées comme fictives** (`net user`, ID du matériel,
    `systemctl status cups`, `ipconfig /all` + `ping`).

  Chaque schéma a un texte alternatif complet, une légende, la mention « schéma non officiel »
  et s'adapte à la largeur de l'écran. **Aucune image générée ni photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr10_figures.py` — règles et données :
  - comptes (`ACCOUNT_TYPES`, groupes, `account_for`, `elevation`) ;
  - permissions (`mode_string`, `mode_octal`, `can_access`, `permission_bits_svg`) ;
  - pilotes (`DEVICE_STATES`, `device_action`, `parse_hardware_id`, `vendor_name`,
    `DRIVER_SOURCES`) ;
  - services (`service_fix`, `WIN_START_TYPES`), `SETTINGS_TOOLS` ;
  - commandes (`COMMANDS`, `needs_admin`) ;
  - relevés fictifs, procédures, figures, liste de contrôle.
- `app/v1/ampcr_pratique_pr10_bank.py` — 17 exercices + 10 questions d'examen.
- `app/v1/ampcr_pratique_pr10_course.py` — 19 blocs du cours.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR10 + contexte de correction IA spécifique.
- `app/seed.py` — `_seed_uaa(…, "PR10", …, position 10)` (ajout seul).
- `tests/test_ticket214_ampcr_pratique_pr10.py` (28 tests). Comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket209_ampcr_pratique_pr09.py`
  (nombre de cours publiés).
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr10
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr10/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr10/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :

1. Ouvrir le cours et parcourir les séquences : chapitres 1 à 12 (fiches de commandes aux
   chapitres 9 à 11), cas résolus, exercices.
2. Lancer une session « S'entraîner » : 10 exercices tirés des 17, dont des remises en ordre et
   des classements auto-corrigés.
3. Lancer un « Examen blanc » : 10 questions, note sur 20.
4. Après envoi, vérifier la correction et le barème.

Dans l'accueil du parcours, PR10 apparaît après PR09 (« 15 cours publiés sur 30 prévus »).

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket214_ampcr_pratique_pr10.py` : **28 passed**. Ils couvrent :
  - **règles** : moindre privilège et comportements UAC/sudo ; permissions (conversions
    chiffres ↔ lettres, première classe qui s'applique, cas du dossier partagé et du script) ;
    codes du Gestionnaire de périphériques et première action ; lecture des ID PCI/USB et
    fabricants ; règle des services ;
  - **commandes** : les 16 commandes du ticket avec leurs cinq rubriques ; droits
    (lecture → compte standard, modification → élévation) ;
  - **procédures et relevés** : ordre des procédures ; captures ≤ 56 caractères par ligne ;
    statistiques de ping cohérentes ;
  - **schémas** : validité, accessibilité, étapes et triplets tirés des données ;
  - **exercices** : remises en ordre et classements auto-corrigés ; aucune question d'acronyme
    ni affirmation fausse ;
  - **cours** : matière du ticket présente, une fiche par commande, 5 cas résolus, examen absent
    du cours, liens (MC10–12, PR07–PR09, PR11, PR20, PR24 ; aucun lien vers PR12/PR22 non
    publiés) ;
  - **intégration** : seed idempotent et position après PR09, réserves séparées, contexte de
    correction, pages, sessions entraînement/examen, note /20, aucune génération IA.
- **Tests liés** (PR08, PR09, numérotation #236, socle #192, hiérarchie admin) : **138 passed**.
- **Suite complète** (une exécution, `seed.py` étant partagé) : **2 685 passed** en 21 min 42 s, aucun échec.
- **`ruff check`** sur les fichiers créés et modifiés : **All checks passed**.
- **Contrôle visuel** des 10 schémas (navigateur sans interface, 440 px de large) : rendu
  correct.
- **Installation** : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket214-20261027-043151.db`),
  avance rapide (fast-forward) `c06b875 → 5f15369`, seed idempotent. Le seed annonce 1 UAA créée
  et 71 blocs « créés » : ce sont les 19 blocs de PR10 et le remplacement habituel des 52 blocs
  FSE pilotés par le code, sans doublon. Redémarrage des deux services (actifs), `/health` local
  et public OK. Pages du cours, de l'accueil, de la matrice et de PR09 en HTTP 200 ;
  entraînement et examen répondent 303 vers la connexion, ce qui est normal sans session.
  L'accueil affiche « 15 cours publiés sur 30 prévus » ; 17 cartes d'exercice et 10 figures sont
  servies. Compteurs utilisateurs / sessions / réponses inchangés (18 / 81 / 638).

Non effectué :

- validation pédagogique humaine (au propriétaire) ;
- session réelle avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ;
- exécution réelle des commandes sur Windows 11 ou Linux : les sorties sont des reconstitutions
  fictives et abrégées, vérifiées par relecture ; les messages français de Windows (SFC,
  tasklist, net user) restent à confirmer sur un poste réel.

## 4. Choix techniques faits seul

- **Sorties Windows en français, Linux en anglais**, comme PR09 et PR24. Les relevés `ipconfig`,
  `ping`, `tracert` et `nslookup` sont produits par les générateurs existants de PR20/PR24 : même
  format dans tout le parcours, statistiques calculées.
- **Règles codées et partagées** par les tableaux, schémas, classements et corrigés :
  `account_for`, `elevation`, `can_access`, `device_action`, `service_fix`, `needs_admin`,
  `COMMANDS`. L'énoncé, le cours et le corrigé ne peuvent pas diverger.
- **Droits par défaut** : UAC au réglage par défaut. Lecture (`ipconfig /all`, `net user`,
  `systemctl status`, `df`…) possible avec un compte standard. Modifications (`/release`,
  `/renew`, `/flushdns`, `sfc`, `DISM`, `/add`, `start`/`enable`, `chown`, `apt install`) en
  administrateur ou avec sudo. `chmod` par le propriétaire.
- **Comptes de domaine** traités au niveau du poste (local ou domaine, effet sur les partages).
  Le détail (contrôleur, groupes du domaine, jonction) est laissé à **PR22**, cité en texte
  seulement (non publié), de même que **PR12** (restauration).
- **Moindre privilège appliqué partout** : le cas « droits insuffisants » utilise le groupe
  `lpadmin` plutôt que `sudo` ; aucune désactivation de l'UAC ; aucun `chmod 777`.
- **Recouvrement limité** : installation renvoyée à PR08/PR09, messages d'erreur à PR11,
  adressage et dépannage réseau à PR20/PR24 (liens). Le cas réseau reste au niveau
  « configuration du poste ».
- **Identifiants de fabricants** : table PCI de PR08 réutilisée ; table USB (Logitech, Brother,
  HP, Canon, Realtek) ajoutée d'après la liste publique de l'USB-IF.
- **Exigences** AP-05, AP-11 et AP-12 citées, statut « partiel » dans la matrice, jamais
  « validé ». Les tableaux de sources de pilotes, d'ordre des tests et la liste de contrôle sont
  signalés comme **conventions du cours**.
- **Pas de nouvelle dépendance** ni de nouvel assistant partagé : un seul schéma local
  (`permission_bits_svg`), les autres via `step_flow_svg`, `decision_tree_svg` et `screen_svg`.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR12 « Dépannage logiciel et restauration du système » (#215).
- Améliorations repérées, non réalisées (hors périmètre) :
  1. PR08 et PR09 citent PR10 en texte seulement. Un lien vers `/uaa/ampcr-pratique-pr10`
     pourrait y être ajouté ; leurs tests vérifient aujourd'hui l'absence de ce lien et
     seraient à adapter.
  2. Dans l'arbre de décision partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la
     flèche sur mobile. Le défaut est déjà signalé pour PR02 à PR09 et visible aussi sur l'arbre
     de PR10.
