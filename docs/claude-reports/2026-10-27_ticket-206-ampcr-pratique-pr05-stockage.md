# Ticket #206 — [AMPCR pratique PR05] Stockage, partitions, formatage et défragmentation

- Ticket : https://github.com/ReC82/jury-central/issues/206
- **État réel : Installé — à tester**
- SHA installé : `3cae295e2a35aff7fd3f6831f05cf360a6a63941` (fusion de la PR #261 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR05 « Stockage, partitions, formatage et défragmentation »** est publié dans le
parcours **Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`, distinct de la
théorie MC : cours, banque, examen et progression séparés ; liens croisés vers MC04, MC07 et
MC08 seulement). C'est le cinquième cours de l'ordre pédagogique PR01 → PR30. L'emplacement PR05
du plan installé (`_COURSE_ROWS`, numérotation définitive de #236) porte bien le sujet du ticket
(« PR05, ticket 206, Stockage, partitions, formatage et défragmentation », exigence AP-03) :
aucun écart de numérotation, aucun autre cours touché ni renuméroté.

Contenu (21 blocs) :

- **14 chapitres de théorie**, chacun avec objectifs, théorie, **procédure professionnelle à
  rédiger**, **erreur fréquente**, « à l'écrit », repère rapide et renvoi aux exercices liés :
  1. **disque dur, SSD SATA, SSD NVMe** (tableau : principe, interface, ordre de grandeur des
     débits, points forts, limites, entretien) ;
  2. **interfaces et formats** : SATA (7 + 15 broches, 6 Gbit/s), **M.2 = format, SATA ou
     NVMe = interface**, emplacements « SATA uniquement », ports partagés, compatibilité ;
  3. **secteurs (512 / 4 096 o), clusters, pages et blocs, endurance (TBW), répartition de
     l'usure, cellules de réserve** ;
  4. **Go et Gio** : 10^9 contre 2^30, tableau 256 Go → 4 To, saisie en Mio dans Gestion des
     disques ;
  5. **partitions, volumes, initialisation ; MBR ou GPT** (tableau comparatif, limite 2 Tio
     calculée, règle de choix, conversion) ;
  6. **démarrage UEFI/ESP et BIOS/partition active** ; **trois plans de partitions exacts**
     (Windows UEFI/GPT, Windows BIOS/MBR, Linux UEFI/GPT) ;
  7. **formatage logique** (rapide, complet, bas niveau) et **NTFS / FAT32 / exFAT / ext4**
     (tableau : taille de fichier, Windows/macOS/Linux, journal, droits, usage) ;
  8. **choisir le système de fichiers selon l'usage** ;
  9. **Windows** : Gestion des disques (initialiser, nouveau volume, étendre, réduire, lettre)
     et **diskpart** (`list disk` d'abord, `clean` = tout le disque) ;
  10. **Linux** : `lsblk -f`, `parted`, `mkfs.ext4`, `mount`, `blkid`, `/etc/fstab` par UUID,
      `mount -a`, `df -h` ;
  11. **sauvegarde préalable et opérations non destructives** (accord écrit, autre support,
      copie vérifiée, image d'un disque qui faiblit, 3-2-1) ;
  12. **SMART interprété avec prudence** (attributs, « PASSED » insuffisant, évolution,
      erreurs CRC = câble, un bon relevé ne garantit rien) ;
  13. **défragmentation (disque dur) contre TRIM (SSD)**, « Optimiser les lecteurs »,
      `fstrim.timer` ;
  14. **symptômes** : disque absent de l'UEFI, non initialisé, sans lettre, RAW, C: plein,
      démarrage impossible (« No bootable device », mode UEFI/hérité, mode SATA).
- **5 procédures illustrées** : avant toute opération sur un disque ; ajouter un disque sous
  Windows ; partitionner, formater et monter sous Linux ; optimiser un lecteur selon son type ;
  retrouver un disque non détecté.
- **4 cas intégralement résolus** : disque dur neuf de 2 To « Non initialisé » ; clé USB FAT32
  qui refuse une vidéo de 6 Go ; PC lent (SSD non défragmenté, disque dur à 27 %) ; plan de
  partitions chiffré d'un poste UEFI (SSD NVMe 500 Go + disque dur 2 To).
- **Pièges fréquents**, **fiche mémo + glossaire**, **sources et compléments**.
- **16 exercices corrigés** (cours + « S'entraîner ») : **3 remises en ordre** (précautions,
  disque sous Windows, disque sous Linux), **3 classements** auto-corrigés (**choix du système
  de fichiers** pour 8 supports, disque dur / SSD / les deux, **GPT ou MBR** pour 6 disques),
  **2 plans de partitions chiffrés** (Windows + D: 300 Gio sur SSD 1 To ; Ubuntu avec /home
  sur SSD 256 Go), calcul Go/Gio, captures et relevés (disque de photos non initialisé, disque
  RAW, « Optimiser les lecteurs », SMART avant redimensionnement), C: plein, « No bootable
  device » après passage en mode hérité, procédure d'un collègue à corriger. Chacun : contexte
  complet, documents, consignes, barème analytique, corrigé.
- **Mini-examen 10 questions /20** (2 pts chacune, réponses libres) dans « Examen blanc », jamais
  affiché dans le cours (support d'un portable de chantier et compatibilité M.2, 2 To affiché
  1862 Go, clé FAT32 et fichier de 8 Go, disque de 3 To en MBR, plan d'un PC BIOS, erreurs CRC,
  formatage rapide/complet, SSD et défragmentation, SMART « à surveiller », montage Linux).
- **11 schémas SVG** produits depuis des données testées : 5 procédures, **plans de partitions**
  (3 dispositions + cas 4), arbre de décision « disque invisible », captures fictives (Gestion
  des disques, lsblk/parted, Optimiser les lecteurs). Alt complet, légende, mention « schéma non
  officiel », responsive. **Aucune image générée ni photographie.**

### Fichiers

- `app/v1/ampcr_pratique_pr05_figures.py` — supports, conversions Go/Gio, limite MBR et
  `partition_table_choice`, systèmes de fichiers et `filesystem_for`, plans de partitions,
  entretien (`optimisation_for`, `needs_defrag`), lecture SMART + câble (`smart_reading`),
  symptômes, cohérence mode/table, procédures, SVG
- `app/v1/ampcr_pratique_pr05_bank.py` — 16 exercices + 10 questions d'examen
- `app/v1/ampcr_pratique_pr05_course.py` — 21 blocs du cours
- `app/v1/ampcr_pratique_bank.py` — déclaration PR05 + contexte de correction IA spécifique
- `app/seed.py` — `_seed_uaa(…, "PR05", …, position 5)` dans le module pratique (additif)
- `tests/test_ticket206_ampcr_pratique_pr05.py` (27 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket205_ampcr_pratique_pr04.py`
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr05
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr05/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr05/exam
- Accueil du parcours pratique : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le cours, parcourir les séquences (chapitres 1 → 14, cas, exercices) ;
lancer une session « S'entraîner » (10 exercices tirés des 16, dont des remises en ordre et des
classements auto-corrigés) puis un « Examen blanc » (10 questions, note sur 20) ; vérifier la
correction et le barème après envoi.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket206_ampcr_pratique_pr05.py` : **27 passed** — calculs Go/Gio et
  plans chiffrés recalculés indépendamment, limite MBR (2^41 octets) et choix MBR/GPT, limite
  FAT32 (4 Gio − 1) et choix du système de fichiers, plans exacts (ESP FAT32 en UEFI, partition
  active en BIOS), entretien HDD/SSD, SMART (remplacer / surveiller / câble CRC), cohérence mode
  de démarrage-table, ordre des procédures, schémas (validité, accessibilité, étapes et
  partitions = données), remises en ordre et classements auto-corrigés, absence de question
  d'acronyme et d'affirmation fausse, matière du ticket présente, 5 procédures et 4 cas, examen
  absent du cours, seed idempotent, réserves séparées, contexte de correction, pages, sessions
  entraînement/examen, note /20, aucune génération IA.
- Tests liés (socle #192, numérotation #236, hiérarchie admin, PR03, PR04) : 131 passed.
- **Suite complète : 2552 passed** (une seule exécution, `seed.py` étant partagé).
- `ruff check` sur les fichiers modifiés : aucune erreur.
- Contrôle visuel (navigateur sans interface, 420 px de large) des 11 schémas ; corrigé après ce
  contrôle : libellé « Récupération » qui débordait de sa case (→ « Récup. »).
- Installation : arbre propre sur `develop`, sauvegarde de la base
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket206-20261027-005635.db`),
  fast-forward `3bbc987 → 3cae295`, seed idempotent (1 UAA créée ; les 73 blocs « créés » =
  21 blocs PR05 + le remplacement habituel des 52 blocs FSE pilotés par le code, sans doublon),
  redémarrage des deux services (actifs), `/health` local et public OK, pages du cours, de
  l'accueil, de la matrice, de PR04 et PR06 en HTTP 200 (entraînement/examen : 303 vers la
  connexion, normal sans session), « 11 cours publiés » sur l'accueil, 16 cartes d'exercice et
  11 figures servies. Compteurs utilisateurs/sessions/réponses inchangés (18 / 81 / 638).

Non effectué : validation pédagogique humaine (au propriétaire) ; passage d'une session réelle
avec la vraie correction IA (les tests utilisent `FakeAIProvider`) ; capture pleine page mobile
du cours installé (même composant de page que les cours déjà publiés).

## 4. Choix techniques faits seul

- **Pas de photographie ni d'image générée** : les schémas techniques (plans de partitions,
  procédures, arbre) sont produits en SVG depuis des données vérifiées, comme le ticket l'exige ;
  une image générée n'apportait rien de fiable pour ce sujet.
- **Plans de partitions** : dispositions créées par les installateurs (documentation
  Microsoft UEFI/GPT : EFI 100 Mo, MSR 16 Mo, C:, récupération ; BIOS/MBR : « Réservé au
  système » ≈ 500 Mo ; Linux : ESP 512 Mo, /, swap). Les tailles de récupération et de l'ESP
  Linux varient selon les versions : présentées comme « tailles d'exemple ».
- **Débits** donnés en **ordres de grandeur** (HDD 100-250 Mo/s, SATA ≈ 550 Mo/s, NVMe
  ≈ 3 500 / 7 000 Mo/s en PCIe 3.0 / 4.0 x4), jamais comme valeurs garanties.
- **Seuils signalés comme conventions du cours** : défragmentation manuelle au-delà de 10 %
  fragmenté ; lecture SMART reprise de PR04 (en attente ou illisibles > 0 → remplacer,
  réalloués seuls → surveiller) ; ajout ici : erreurs CRC > 0 → câble à contrôler d'abord.
- **Choix MBR/GPT codé** (`partition_table_choice`) et utilisé pour calculer les réponses du
  classement E06 ; de même pour le système de fichiers (E04) : énoncé, cours et corrigé ne
  peuvent pas diverger.
- **Recouvrement limité** : effacement sécurisé renvoyé à PR04, connecteurs à PR02, montage
  physique à PR03, réparation du démarrage à PR11, installation de Windows/Linux à PR08/PR09
  (renvoi en texte, ces cours n'étant pas encore publiés). Exigence : AP-03 (plan installé),
  statut « partiel » dans la matrice, jamais « validé ».
- Mêmes moteur, réserves `practice`/`exam`, format d'exercice et mise en forme que les cours
  pratiques déjà publiés ; pas de nouvelle dépendance ; petits constructeurs d'items réutilisés
  depuis la banque PR04.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire.
- Suite de l'ordre pédagogique : PR06 est déjà publié ; prochain élément : EX01 (#230).
- Améliorations repérées, non implémentées (hors périmètre) : (1) les cours PR01 et PR04 citent
  PR05 en texte ; un lien vers `/uaa/ampcr-pratique-pr05` pourrait maintenant être ajouté (le
  test de PR04 vérifie aujourd'hui l'absence de ce lien et serait à adapter) ; (2) dans l'arbre
  de décision partagé (`decision_tree_svg`), l'étiquette « NON » chevauche la flèche sur mobile
  (déjà signalé pour PR02/PR03/PR04/PR06).
