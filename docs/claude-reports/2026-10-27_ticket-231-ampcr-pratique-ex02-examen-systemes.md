# Ticket #231 — [AMPCR pratique EX02] Examen blanc écrit — installation et dépannage des systèmes

- Ticket : https://github.com/ReC82/jury-central/issues/231
- **État réel : Installé — à tester**
- SHA installé : `8a77caab3d68ff878069558dbec35b95eda6473c` (fusion de la PR #275 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le **deuxième examen blanc** du parcours **Informatique AMPCR → Pratique écrite** est publié :
**EX02 « Examen blanc écrit — installation et dépannage des systèmes »**, épreuve autonome
**/100** du module 2 (cours PR07 → PR12, tous publiés avant cette session). Il est placé juste
après PR12 dans la navigation. L'emplacement EX02 du plan installé (`_EXERCISE_ROWS`,
numérotation définitive de #236 : « EX02, ticket 231 ») porte bien le sujet du ticket : aucun
écart, aucun autre cours ni examen touché. Module `AMPCR-PRATIQUE` uniquement : Théorie (MC) et
Pratique restent séparées (banques, sessions, progression). Même modèle d'intégration que EX01
(#230), sans nouveau mécanisme.

### Ce que voit le candidat

- **Page « Sujet »** (`/uaa/ampcr-pratique-ex02`, onglets « Sujet » et « Examen blanc ») —
  version candidat **sans aucun corrigé**, 7 séquences :
  1. présentation, organisation et notation (10 questions × 10 points, réponses rédigées,
     barème analytique, corrigé après remise, durée conseillée de 2 h donnée comme repère
     personnel **et non comme durée officielle**), mode d'emploi, impression A4 ; **barème
     global** (question, partie, points, exigences AP, cours à revoir) ; les 12 exigences
     officielles évaluées ;
  2. **Partie 1** — relevé de trois postes, relevés à faire et capture `systemctl status cups`,
     questions 1 et 2 ;
  3. **Dossier A — bureau d'architectes Verhaegen** (Windows) : fiche d'intervention, inventaire,
     **écran de l'installateur** (schéma), Gestionnaire de périphériques, personnes et comptes ;
  4. **Dossier B — Repair Café « La Clé »** (Linux) : demandes, **plan de partitions** du double
     démarrage (schéma), écran du **mode d'urgence**, `lsblk`/`blkid`/fstab, sessions `ls -l`/`id`/sudo ;
  5. **Dossier C — agence immobilière Delvaux** (Windows) : fiche, **écran d'arrêt** (schéma),
     écran de **réparation automatique et options de WinRE**, points de restauration, constats
     d'un second poste, **empreintes SHA-256** d'une sauvegarde ;
  6. méthode (avec l'échelle des interventions de PR12 en rappel) ; 7. sources et supports fictifs.
  À l'impression : 12 lignes de réponse sous chaque question, chaque dossier sur une nouvelle page.
- **Examen blanc** (`/uaa/ampcr-pratique-ex02/exam`) : session de 10 questions, une par écran,
  chacune avec les documents de son dossier (les trois schémas s'affichent dans leur question,
  avec leur description écrite complète) ; **sauvegarde automatique et reprise** (moteur
  existant) ; barème et corrigé invisibles avant la remise ; résultats avec la **note /100**
  (et le repère /20), puis corrigé détaillé par question.
- « S'entraîner » n'existe pas pour un examen blanc : `/practice` redirige vers l'examen (on
  s'entraîne dans PR07 → PR12).

### Les 10 questions (10 points chacune, barème en 3 ou 4 critères, corrigé détaillé)

| N° | Partie | Question | Exigences |
|---|---|---|---|
| 1 | Partie 1 | Trois postes : compatible Windows 11 tel quel / après réglages / non compatible ; système et édition (Famille, Professionnel pour BitLocker + hôte Bureau à distance, Linux LTS ou ChromeOS Flex pour le poste non compatible) ; réglages ordonnés (mbr2gpt **avant** le passage en UEFI, TPM, démarrage sécurisé) et vérification GUI/CLI | AP-08, AP-10, AP-12 |
| 2 | Partie 1 | Outil graphique et commande, Windows et Ubuntu, pour disques, pilotes, réseau, service ; `cups` arrêté et désactivé → `sudo systemctl enable --now cups`, droits, vérifications après redémarrage ; équivalent Spouleur | AP-11, AP-12, AP-15 |
| 3 | Dossier A | Installation propre de Windows 11 Pro sur SSD neuf : préparation (profil sauvegardé, licence numérique, pilotes, autres disques débranchés), choix sur l'écran de l'installateur (disque 2 non alloué, 931,5 Go ; disques 0 et 1 intouchés), partitions créées (ESP FAT32, MSR, C: NTFS, récupération), lien UEFI/GPT/ESP, vérifications | AP-10, AP-03, AP-C03 |
| 4 | Dossier A | Pilotes manquants : VEN_10EC Realtek, VID_04F9 Brother, VEN_10DE NVIDIA ; Code 28, carte graphique de base ; réseau d'abord via un autre PC, sources fiables, point de restauration, vérifications | AP-05, AP-11, AP-15 |
| 5 | Dossier A | Groupe de travail ou domaine ; un compte standard par personne, administrateur nominatif, compte partagé refusé ; `net user … * /add`, `net localgroup Administrateurs`, fin de stage | AP-24, AP-11, AP-27 |
| 6 | Dossier B | Double démarrage Ubuntu : clé BitLocker, démarrage rapide, image contrôlée ; ESP réutilisée sans formatage, partitions Windows intouchées, `/`, swap 8 Go (16 Go avec hibernation), `/home` ; arrêt sans copie vérifiée ; vérifications | AP-10, AP-03, AP-C03 |
| 7 | Dossier B | Mode d'urgence : fstab désigne `/dev/sdb1`, devenu `sdc1` après l'ajout d'un disque vide ; ligne par UUID + `nofail`, `findmnt --verify`, `daemon-reload`, `mount -a`, vérifications ; interdits | AP-09, AP-13, AP-15 |
| 8 | Dossier B | Permissions : dossier 770, Lucie hors du groupe (« autres » ---) ; fichier 640, Marc lit sans écrire ; refus de sudo normal ; `sudo usermod -aG`, `chmod g+w` (660) par l'administrateur ; jamais 777 | AP-27, AP-11, AP-12 |
| 9 | Dossier C | Écran d'arrêt `SYSTEM_THREAD_EXCEPTION_NOT_HANDLED` (pilote graphique installé la veille), réparation automatique en échec ; mode sans échec → restaurer le pilote, sinon point de restauration ; pas de réinitialisation ; vérification et prévention | AP-09, AP-13, AP-15 |
| 10 | Dossier C | Empreintes SHA-256 : une copie différente à refaire ; sfc/DISM échoués, aucun point → réinstaller via Windows Update, sinon « Réinitialiser en conservant mes fichiers » (programmes retirés, sauvegarde vérifiée et accord écrit) ; plan, message au gérant | AP-C03, AP-15, AP-03 |

Les 12 exigences de l'emplacement EX02 (AP-03, 05, 08, 09, 10, 11, 12, 13, 15, 24, 27, C03) sont
toutes évaluées ; aucune n'est déclarée « validée » (matrice inchangée).

### Fichiers

- `app/v1/ampcr_pratique_ex02_figures.py` — données des dossiers et schémas ; chaque verdict
  vient de la règle **du cours** : `win11_check`/`edition_needed` (PR07), `service_fix`,
  `account_for`, `vendor_name`, `device_action`, `can_access`, `mode_octal` (PR10),
  `activation_result`, `partition_action`, `STANDARD_LAYOUT` (PR08), `dual_boot_action`,
  `swap_advice` (PR09), `WINRE_OPTIONS` (PR11), `LADDER`, `precaution_for`, `effect_of`,
  `sha256_hex`, `copy_check` (PR12) ; 3 figures SVG.
- `app/v1/ampcr_pratique_ex02_bank.py` — 10 questions, documents des dossiers, validation.
- `app/v1/ampcr_pratique_ex02_course.py` — 7 blocs de la page du sujet.
- `app/static/img/ampcr-pratique/ex02-installateur-disques.svg`,
  `ex02-partitions-double-demarrage.svg`, `ex02-ecran-arret.svg` — schémas affichés dans les
  questions (identiques au SVG du code, vérifié par test).
- `app/v1/ampcr_pratique_bank.py` — EX02 déclaré, contexte de correction spécifique (notions,
  pénalités : formatage de l'ESP, partition supprimée sans accord, `chmod 777`, fstab par
  `/dev/sdX`, réinitialisation prématurée…).
- `app/seed.py` — `_seed_uaa(…, "EX02", …, position 12)` (additif).
- `tests/test_ticket231_ampcr_pratique_ex02.py` (29 tests) ; comptage adapté dans
  `tests/test_admin_content_hierarchy.py` ; motif « 1 examens blancs » assoupli dans
  `tests/test_ticket230_ampcr_pratique_ex01.py` (il y en a maintenant 2).
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

Aucun gabarit, aucune route, aucun CSS modifié : tout le reste (onglets « Sujet / Examen blanc »,
redirection, note /100, mise en page `figure`) vient du modèle posé par EX01.

## 2. Liens pour tester

- Sujet (public) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex02
- Examen blanc (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex02/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : ouvrir le sujet, parcourir les 7 séquences (ou « Afficher tout le cours sur
une page ») ; essayer l'aperçu avant impression (Ctrl + P : sujet complet, lignes de réponse,
aucun corrigé) ; lancer l'examen blanc, répondre à quelques questions, quitter et reprendre
(sauvegarde), remettre, puis vérifier la note /100, le barème et le corrigé de chaque question.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket231_ampcr_pratique_ex02.py` : **29 passed** — verdicts
  Windows 11 et éditions recalculés (poste 1 « après réglages » avec mbr2gpt en premier, poste 2
  non compatible : processeur hors liste et TPM 1.2, poste 3 tel quel ; Professionnel pour
  BitLocker + hôte Bureau à distance) ; service `cups` « disabled / inactive » → activer et
  démarrer ; écran de l'installateur (seul le disque 2 non alloué est sélectionné, 931,5 et
  1863,0 Go recalculés en Gio) ; fabricants Realtek / Brother / NVIDIA ; comptes (4 standard,
  1 administrateur nominatif) ; double démarrage (ESP réutilisée sans formatage, swap 8/16 Go,
  arrêt sans copie vérifiée) ; fstab : pas de `sdb1` dans `lsblk`, données sur `sdc1`, UUID au
  bon format ; permissions 770/640 et accès recalculés ; empreintes SHA-256 recalculées avec
  `hashlib` (une seule copie différente) ; captures ≤ 56 caractères ; 4 figures valides et
  accessibles, 3 fichiers statiques identiques au SVG du code ; 10 questions × 10 = 100, réponses
  libres, 3 dossiers dont chaque document sert, matière du ticket présente, 12 exigences de
  l'emplacement couvertes, pas de question d'acronyme ; sujet sans corrigé ni barème détaillé,
  10 zones de réponse ; seed idempotent, EX02 juste après PR12 (EX01 toujours après PR06) ;
  réserve `exam` seule ; contexte de correction propre à EX02 ; navigation (pas de « S'entraîner »,
  redirection), accueil « 2 examens blancs sur 6 » ; session d'examen : 10 questions, aucune
  génération IA, corrigé masqué avant remise, les 3 schémas affichés dans leurs questions, note /100.
- Tests EX01 (#230), numérotation (#236) et hiérarchie seedée : verts (114 passed avec #231).
- **Suite complète : 2742 passed** (une exécution, le seed et la banque partagée étant touchés).
- `ruff check` : fichiers créés sans erreur ; `ampcr_pratique_bank.py` et `seed.py` sans erreur.
- Contrôle visuel (navigateur sans interface) : les 3 schémas (capture de l'installateur
  corrigée : la colonne des noms touchait celle des tailles) ; page du sujet rendue par l'app à
  1 280 px et à 400 px (séquences, barème global, tableaux, captures, échelle de méthode).
  Relecture technique : heures ajoutées aux lignes `ls -l`, option `/allowFullOS` de mbr2gpt,
  suppression d'un indice qui donnait la réponse de la question 5.
- Installation : arbre propre sur `develop`, sauvegarde
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket231-20261027-060652.db`),
  fast-forward `f276f5e → 8a77caa`, seed idempotent (1 UAA créée ; 59 blocs « créés » = 7 blocs
  EX02 + le remplacement habituel des 52 blocs FSE pilotés par le code), redémarrage des deux
  services (actifs), `/health` local et public OK ; sujet, accueil, matrice, PR12, EX01 et les 3
  SVG en HTTP 200 (examen : 303 vers la connexion sans session, normal) ; sujet servi avec 10
  questions et aucun « Corrigé de référence » ; accueil « 2 examens blancs sur 6 ». Compteurs
  utilisateurs/sessions/réponses inchangés (18 / 81 / 638).

Non effectué : validation pédagogique humaine (au propriétaire) ; correction réelle par l'IA
(les tests utilisent `FakeAIProvider`) ; contrôle de l'impression PDF page par page ; session
d'examen parcourue en vrai sur le site (seulement dans les tests).

## 4. Choix techniques faits seul

- **10 questions de 10 points** (le ticket demande 10 à 14) : même choix que EX01 — longueur de
  session standard du moteur, toutes les questions tirées, total exactement 100.
- **Pas d'onglet « S'entraîner »**, sujet = page de l'UAA, corrigés jamais sur le sujet : modèle
  EX01 réutilisé tel quel.
- **Questions autonomes** (le moteur mélange l'ordre) : chaque question reprend les documents de
  son dossier ; sur la page du sujet, un document n'apparaît qu'avant la première question qui
  l'utilise. Les situations ont été choisies pour qu'aucune question n'en corrige une autre
  (le second poste du dossier C est un autre PC que celui de la question 9).
- **Cas nouveaux, règles des cours** : les situations ne recopient pas les cas des cours (PR11 a
  déjà un fstab avec un UUID périmé et un écran BCD 0xc000000f) ; EX02 utilise un fstab par
  `/dev/sdb1` cassé par l'ajout d'un disque, et un écran d'arrêt après une mise à jour de pilote.
- **Schémas dans les questions** : capture de l'installateur, plan de partitions et écran
  d'arrêt en SVG produits par programme (documents `figure` avec description textuelle complète) ;
  les terminaux, le Gestionnaire de périphériques et WinRE en documents « console » (texte à
  chasse fixe, ≤ 56 caractères par ligne). Pas d'image générée : des écrans et valeurs exacts
  sont mieux servis par un dessin construit sur des données testées.
- **Libellés** : Windows en français (poste belge), Linux en anglais (comme les cours) ; libellés
  datés d'octobre 2026 et signalés comme approximatifs ; identifiants PCI/USB de fabricants réels
  (Realtek, Brother, NVIDIA), modèles, noms de pilotes, UUID et empreintes fictifs (empreintes
  calculées par `hashlib` sur des contenus fictifs, donc exactes).
- **Domaine / groupe de travail (AP-24)** : traité au niveau des cours publiés (PR10 et PR24) —
  le cours PR22 (#222) n'est pas encore publié ; aucun lien vers lui.
- **Renvois « À revoir »** : PR07 → PR12, plus PR05 (partitions et formatage) pour les
  questions 3 et 6.
- **Position 12** (même position que PR12, créé après lui) : EX02 suit PR12 et précède PR13
  quand il sera publié.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (sujet, impression, correction réelle
  par l'IA).
- Suite de l'ordre pédagogique : PR13 (#216) → … → PR18, puis EX03 (#232).
- Suggestion (hors périmètre, non implémentée, déjà notée pour EX01) : permettre de fixer l'ordre
  des questions d'un examen blanc dans le moteur de sessions, pour suivre exactement le sujet.
- Remarque (hors périmètre) : le bouton de fin de séquence du sujet s'intitule « Passer à
  l'entraînement » (script commun des cours) alors qu'il mène à l'examen blanc pour un EX ; même
  comportement que EX01.

## Notification

L'email de livraison est envoyé par le superviseur jcorch à la fin de la session, avec ce rapport
en pièce jointe (copie dans `~/.local/state/jury-central-orch/reports/`).
