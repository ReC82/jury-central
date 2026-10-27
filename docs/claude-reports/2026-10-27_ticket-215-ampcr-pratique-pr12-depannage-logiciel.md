# Ticket #215 — [AMPCR pratique PR12] Dépannage logiciel et restauration du système

- Ticket : https://github.com/ReC82/jury-central/issues/215
- **État réel : Installé — à tester**
- SHA installé : `de924d0209e988148afa9a685167dec55c48a758` (fusion de la PR #273 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR12 « Dépannage logiciel et restauration du système »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`). Il est séparé de la
théorie MC : cours, banque, examen et progression distincts. Seuls des liens croisés renvoient
vers MC30 et MC32. C'est le douzième cours de l'ordre pédagogique (position 12, après PR11).
Il suit donc l'ordre demandé : EX02 (#231) peut venir ensuite.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation définitive de
#236), l'emplacement PR12 porte bien le sujet du ticket : « PR12, ticket 215, Dépannage
logiciel et restauration du système », exigences AP-15 et AP-C03. Aucun écart. Aucun autre
cours n'a été touché ni renuméroté.

Contenu (20 blocs) :

- **13 chapitres de théorie**. Chacun contient les objectifs, la théorie, la **procédure
  professionnelle à rédiger**, l'**erreur fréquente**, ce qu'on attend « à l'écrit », un repère
  rapide et le renvoi vers les exercices liés.
  1. **Situer la cause** : système, application, pilote, compte, service, logiciel malveillant ou
     stockage. Tableau des signes et des tests ; arbre d'isolement (stockage d'abord, autre
     programme, compte de test, mode sans échec, analyse hors ligne).
  2. **Recueillir les faits** : symptôme exact, depuis quand, reproductibilité, portée,
     changements récents, données. Journaux Windows et Linux ; démarche en 6 étapes.
  3. **Protéger les données** : sauvegarde préalable (copier sans déplacer), **vérification
     d'intégrité par empreinte SHA-256** (`Get-FileHash`, `certutil`, `sha256sum`),
     **accord écrit** avant réinstallation, confidentialité.
  4. **WinRE et démarrage avancé** : accès, outils, mode sans échec, lettres de lecteur dans
     WinRE.
  5. **Points de restauration** : activation, création, `rstrui`, « programmes concernés ».
     Un point de restauration ne sauvegarde pas les documents.
  6. **SFC/DISM** (y compris SFC hors ligne), **pilotes**, **mises à jour** : historique,
     désinstaller, revenir en arrière, suspendre puis reprendre, réinstallation via Windows
     Update.
  7. **Profil corrompu** (profil temporaire, événement 1511).
  8. **Logiciels malveillants** (publicitaires, rançongiciel) : isoler, ne pas payer, analyse
     hors ligne, sauvegarde saine.
  9. **Linux** : systemd, `journalctl`, test de configuration, GRUB et noyau précédent.
  10. **Linux** : permissions, paquets (`dpkg --configure -a`, `apt --fix-broken install`),
      `fsck` uniquement sur une partition démontée, espace disque (`df`, `du`,
      `journalctl --vacuum-size`, `apt clean`).
  11. **Échelle des interventions** : du geste le moins invasif à la réinstallation complète,
      avec l'effet sur les fichiers et les programmes, et la précaution exigée.
  12. **Panne réseau logicielle ou physique**.
  13. **Contrôles finaux et rapport**.
- **5 procédures illustrées** : démarche de dépannage ; sauvegarde et vérification ;
  restauration du système ; Windows qui ne démarre plus ; service Linux en échec.
- **5 cas résolus**, ceux qu'exige le ticket :
  1. **démarrage** (écran noir après un pilote graphique) ;
  2. **service** (nginx en échec, `nginx -t`) ;
  3. **profil** (profil temporaire après une coupure) ;
  4. **mise à jour** (logiciel incompatible, mise à jour désinstallée puis suspendue) ;
  5. **espace disque** (racine Ubuntu pleine à cause des journaux).
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **17 exercices corrigés** (le ticket en demande au moins 16), dont **10 avec documents**
  (consoles ou tableaux) :
  - **3 remises en ordre** : démarche, restauration, sauvegarde ;
  - **5 classements** auto-corrigés : famille de cause, effet d'un geste sur les données,
    précaution exigée, commande Linux, panne réseau logicielle ou physique ;
  - **documents à lire** : Moniteur de fiabilité, profil temporaire, volumes vus dans WinRE (SFC
    hors ligne), `dpkg` interrompu, GRUB et noyau, Stockage Windows plein, empreintes SHA-256
    (une copie abîmée), fichiers restaurés appartenant à root ;
  - **procédure d'un collègue à corriger**.

  Chaque exercice a un contexte complet, des consignes, un barème analytique et un corrigé.
- **Mini-examen de 10 questions /20** (2 points chacune, réponses libres), dans l'onglet
  « Examen blanc ». Il n'est jamais affiché dans le cours. Thèmes :
  - premier appel ;
  - Word qui plante dans un seul profil ;
  - scanner en panne après une mise à jour ;
  - boucle de réparation automatique ;
  - choix d'un point de restauration ;
  - base MariaDB arrêtée par un disque plein ;
  - rançongiciel ;
  - `fsck` sur une partition montée ;
  - « réinstallez tout » et accord écrit ;
  - « Média déconnecté » ou adresse 169.254.
- **11 schémas SVG** produits depuis des données testées :
  - 5 procédures ;
  - arbre d'isolement ;
  - échelle des interventions (✓/✗, indépendante de la couleur) ;
  - arbre réseau ;
  - 3 captures **clairement fictives** : profil temporaire, nginx, `df`/`du`.

  Chaque schéma a un texte alternatif complet, une légende et la mention « schéma non
  officiel ». **Aucune image générée, aucune photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr12_figures.py` — règles et données :
  - `CAUSES`, `ISOLATION_TREE`/`isolate`, `FACTS`, `LOGS` ;
  - `LADDER`, `precaution_for`, `effect_of`, `ladder_svg`, `WINRE_TOOLS` ;
  - `sha256_hex`, `BACKUP_FILES`, `copy_check` ;
  - `df_use_percent` (arrondi au-dessus comme GNU df), `LINUX_FIXES` ;
  - `network_layer`, `NETWORK_TREE` ;
  - procédures, relevés fictifs, figures, liste de contrôle.
- `app/v1/ampcr_pratique_pr12_bank.py` — 17 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr12_course.py` — les 20 blocs du cours.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR12 et contexte de correction IA propre au
  cours.
- `app/seed.py` — `_seed_uaa(…, "PR12", …, position 12)` (ajout seul).
- `tests/test_ticket215_ampcr_pratique_pr12.py` (28 tests). Comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket214_ampcr_pratique_pr10.py`
  (nombre de cours publiés).
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr12
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr12/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr12/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :

1. Ouvrir le cours et parcourir les séquences : chapitres 1 à 13, cas résolus, exercices.
2. Lancer une session « S'entraîner » : 10 exercices tirés des 17, dont des remises en ordre et
   des classements auto-corrigés.
3. Lancer un « Examen blanc » : 10 questions, note sur 20.
4. Après l'envoi, vérifier la correction et le barème.

Dans l'accueil du parcours, PR12 apparaît après PR11 (« 16 cours publiés sur 30 prévus »).

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket215_ampcr_pratique_pr12.py` : **28 passed**. Ils couvrent :
  - **règles** : les 7 familles et l'arbre d'isolement (chaque branche) ; l'échelle des
    interventions (effets d'après Microsoft, précautions jamais décroissantes, accord écrit
    pour toute réinitialisation) ; les outils de WinRE ;
  - **empreintes** : SHA-256 recalculées avec `hashlib`, copie abîmée détectée ;
  - **espace disque** : arrondi et `Use%` de `df`, tailles cohérentes avant et après ;
  - **réseau** : panne logicielle ou physique ;
  - **procédures** : ordre des étapes ;
  - **captures** : ≤ 56 caractères par ligne et cohérentes ;
  - **schémas** : validité, accessibilité, données ;
  - **exercices** : remises en ordre et classements auto-corrigés, aucun classement trivial,
    aucune question d'acronyme, aucune affirmation fausse ;
  - **cours** : matière du ticket, 5 cas résolus, 5 procédures, examen absent du cours, liens
    (MC30, MC32, PR05, PR06, PR08-PR11, PR20, PR24 ; aucun lien vers PR28, non publié) ;
  - **intégration** : seed idempotent et position après PR11, réserves séparées, contexte de
    correction, pages, sessions d'entraînement et d'examen, note /20, aucune génération IA.
- **Tests liés** (PR09, PR10, numérotation #236, socle #192, hiérarchie admin) : **139 passed**.
- **Suite complète** (une exécution, car `seed.py` est partagé) : **2 713 passed** en 22 min,
  aucun échec.
- **`ruff check`** sur les fichiers créés et modifiés : **All checks passed**.
- **Contrôle visuel** des 11 schémas (navigateur sans interface, 440 px de large) : rendu
  correct.
- **Installation** :
  - arbre propre sur `develop` ;
  - sauvegarde de la base
    (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket215-20261027-051525.db`) ;
  - avance rapide (fast-forward) `1ecaa87 → de924d0` ;
  - seed idempotent : 1 UAA créée et 72 blocs « créés ». Ce sont les 20 blocs de PR12 et le
    remplacement habituel des 52 blocs FSE pilotés par le code, sans doublon ;
  - redémarrage des deux services (actifs), `/health` local et public OK ;
  - pages du cours, de l'accueil, de la matrice, de PR10 et de PR11 en HTTP 200 ;
    entraînement et examen répondent 303 vers la connexion, ce qui est normal sans session ;
  - 17 cartes d'exercice servies ; l'accueil affiche « 16 cours publiés sur 30 prévus » ;
  - compteurs utilisateurs / sessions / réponses inchangés (18 / 81 / 638).

Non effectué :

- validation pédagogique humaine (au propriétaire) ;
- session réelle avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ;
- exécution réelle sur Windows 11 ou Linux. Les sorties sont des reconstitutions fictives et
  abrégées, vérifiées par relecture. À confirmer sur un poste réel :
  - les libellés français de Windows (notification de profil temporaire, « Résoudre les
    problèmes à l'aide de Windows Update ») ;
  - le texte exact du message de MariaDB.

## 4. Choix techniques faits seul

- **Périmètre réparti avec les cours voisins** :
  - messages d'erreur (BCD, `grub rescue`, fstab, écrans bleus) → **PR11** ;
  - commandes de base → **PR10** ;
  - stockage → **PR05** ;
  - dépannage réseau complet → **PR24**.

  Des liens y renvoient. PR12 traite la **réparation et la restauration**, ainsi que la
  **protection des données**. **PR28** (non publié) n'est cité qu'en texte.
- **Arbre d'isolement, échelle des interventions, trois niveaux de précaution, seuil de 15 %
  d'espace libre** : ce sont des **conventions du cours**, signalées comme telles. Les effets de
  chaque outil suivent la documentation Microsoft.
- **Empreintes SHA-256 calculées** par `hashlib` sur des contenus fictifs : elles sont exactes.
  Les tests les recalculent.
- **Tailles `df`/`du` arrondies au-dessus**, comme GNU coreutils. `Use%` est calculé et
  contrôlé.
- **Numéro de mise à jour fictif** (`KB5099999`), signalé : il ne désigne aucune mise à jour
  réelle.
- **Exigences** : AP-15 (officielle, partie logicielle ; partie matérielle en PR06) et AP-C03
  (complément de la matrice). Statut « partiel » dans la matrice, jamais « validé ».
- **Pas de nouvelle dépendance** : un seul nouveau type de schéma local (`ladder_svg`). Les
  autres réutilisent `step_flow_svg`, `decision_tree_svg` et `screen_svg`.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : EX02 « Examen blanc écrit — installation et dépannage des
  systèmes » (#231), puis PR13 (#216).
- Améliorations repérées, non réalisées (hors périmètre) :
  1. Dans l'arbre de décision partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la
     flèche sur mobile, et un texte long de la colonne de droite peut toucher le bord du cadre
     (visible sur l'arbre d'isolement de PR12). Défaut déjà signalé pour PR02 à PR10.
  2. PR10 et PR11 citent la restauration (PR12) en texte seulement. Un lien vers
     `/uaa/ampcr-pratique-pr12` pourrait y être ajouté ; le test de PR10 vérifie aujourd'hui
     l'absence de ce lien et serait à adapter.
