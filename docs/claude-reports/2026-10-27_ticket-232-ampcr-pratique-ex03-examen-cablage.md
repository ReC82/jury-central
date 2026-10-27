# Ticket #232 — [AMPCR pratique EX03] Examen blanc écrit — câblage RJ45, BNC et fibre

- Ticket : https://github.com/ReC82/jury-central/issues/232
- **État réel : Installé — à tester**
- SHA installé : `4a7e78a7845bb348eb11db16aaa4547d77008de5` (fusion de la PR #283 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le **troisième examen blanc** du parcours **Informatique AMPCR → Pratique écrite** est publié :
**EX03 « Examen blanc écrit — câblage RJ45, BNC et fibre »**, épreuve autonome **/100** du
module 3 du plan (cours PR13 → PR17, tous publiés avant cette session). Il est placé juste
après PR17 dans la navigation. L'emplacement EX03 du plan installé (`_EXERCISE_ROWS`,
numérotation définitive de #236 : « EX03, ticket 232 ») porte bien le sujet du ticket : aucun
écart, aucun autre cours ni examen touché. Module `AMPCR-PRATIQUE` uniquement : Théorie (MC) et
Pratique restent séparées (banques, sessions, progression). Même modèle d'intégration que EX01
(#230) et EX02 (#231), sans nouveau mécanisme.

### Ce que voit le candidat

- **Page « Sujet »** (`/uaa/ampcr-pratique-ex03`, onglets « Sujet » et « Examen blanc ») —
  version candidat **sans aucun corrigé**, 7 séquences : présentation, organisation et notation
  (10 × 10 points, barème analytique, corrigé après remise, durée conseillée de 2 h donnée comme
  repère personnel **et non comme durée officielle**, calculatrice utile), barème global,
  7 exigences officielles évaluées ; partie 1 ; dossiers A, B, C ; méthode ; sources et supports
  fictifs. À l'impression : 12 lignes de réponse par question, chaque dossier sur une nouvelle page.
- **Examen blanc** (`/uaa/ampcr-pratique-ex03/exam`) : 10 questions, une par écran, avec les
  documents de leur dossier (les 4 schémas s'affichent dans leur question, avec leur description
  écrite complète) ; sauvegarde automatique et reprise ; barème et corrigé invisibles avant la
  remise ; note /100 (et repère /20) puis corrigé détaillé. `/practice` redirige vers l'examen.

### Les 10 questions (10 points chacune, barème en 3 ou 4 critères, corrigé détaillé)

| N° | Partie | Question | Exigences |
|---|---|---|---|
| 1 | Partie 1 | Fiche RJ45 d'un stagiaire (schéma) contre T568B : broches 4-5 et 7-8 inversées ; ordres complets T568A et T568B avec l'orientation de lecture ; affichage du testeur (4→5, 5→4, 7→8, 8→7), on ne livre pas, procédure de reprise | AP-34, AP-18, AP-20 |
| 2 | Partie 1 | Quatre liaisons : droit ou croisé (MDI/MDI-X, Auto MDI-X), broches 1-2 / 3-6, croisé 1→3, 2→6, 3→1, 6→2, 4 paires à 1 Gb/s | AP-18, AP-20, AP-34 |
| 3 | Dossier A | Choix des câbles de 5 liaisons : Cat5e U/UTP, Cat6A F/UTP, Cat5e S/FTP, coaxial 75 Ω RG-59 + BNC 75 Ω, fibre (140 m) ; désignations X/YTP et limites du blindage ; 90/100 m, Cat5e/Cat6/Cat6A | AP-18, AP-19, AP-20 |
| 4 | Dossier A | Rapport de test : lien croisé par mélange A/B prise/panneau (schéma de testeur), lien permanent 96 m (canal 101 m), circuit ouvert broche 7, paires séparées 3-6/4-5, 10 Gb/s sur Cat6 à 70 m | AP-34, AP-19, AP-20 |
| 5 | Dossier A | Relevé de pose de 5 tronçons (rayon 4/8/10 × Ø, 110 N, séparation EN 50174-2, cloison) et procédure de fabrication d'un cordon droit T568B | AP-18, AP-20, AP-34 |
| 6 | Dossier B | Bus 10BASE2 (schéma) : terminateur 75 Ω, tronçon RG-59, T relié par un cordon, tronçon de 0,3 m ; rôle des terminateurs, Γ = 0,2 ; remise en conformité et contrôle 25 Ω | AP-35, AP-18, AP-20 |
| 7 | Dossier B | Ohmmètre 25 / 50 / 0 Ω ; procédure de réalisation d'un câble RG-58 à BNC sertis ; comparaison 10BASE2 / 10BASE5 | AP-35, AP-19, AP-20 |
| 8 | Dossier C | 420 m entre bâtiments → 10GBASE-LR sur OS2, jarretières LC/UPC (pas d'OM4 : 400 m ; pas de SC/APC) ; 70 m → 10GBASE-T Cat6A ; OM2 180 m : 1 Gb/s oui, 10 Gb/s non (82 m) ; comparaison fibre/cuivre | AP-21, AP-22, AP-19 |
| 9 | Dossier C | Bilan à 1 310 nm (0,168 + 1,5 + 0,6 = 2,27 dB), photométrie (2,10 dB conforme, 4,62 dB non conforme → inspecter, nettoyer, remesurer, réflectomètre), puissance reçue −4,37 dBm, marge, sécurité laser | AP-21, AP-19, AP-22 |
| 10 | Dossier C | Panne après travaux : LOS d'un seul côté (pas la polarité), trace de réflectomètre (connecteur, courbure, cassure à 175 m du tiroir), réparation (épissures, rayons 60/120 mm), seuil 2,87 dB | AP-21, AP-22, AP-20 |

Les 7 exigences de l'emplacement EX03 (AP-18, 19, 20, 21, 22, 34, 35) sont toutes évaluées ;
aucune n'est déclarée « validée » (matrice inchangée).

### Fichiers

- `app/v1/ampcr_pratique_ex03_figures.py` — données des dossiers et 4 schémas ; chaque verdict
  vient de la règle **du cours** : `T568A/T568B`, `links_between`, `split_pairs`, `pinout_svg`,
  `wiremap_svg` (PR15), `choose`, `run_errors`, `channel_errors`, `label_for` (PR13),
  `copper_verdict`, `choose_10g` (PR14), `bus_errors`, `ohmmeter_reading`,
  `reflection_coefficient` (PR16), `module_verdict`, `max_link_loss_db`, `measured_loss_db`,
  `photometry_verdict`, `rx_status`, `otdr_event_kind`, `break_position_m` (PR17). Bus et trace
  redessinés **sans verdict** (les dessins des cours écrivent leurs conclusions).
- `app/v1/ampcr_pratique_ex03_bank.py` — 10 questions, documents des dossiers, validation.
- `app/v1/ampcr_pratique_ex03_course.py` — 7 blocs de la page du sujet.
- `app/static/img/ampcr-pratique/ex03-fiche-stagiaire.svg`, `ex03-testeur-b1-p1-09.svg`,
  `ex03-bus-salle-retro.svg`, `ex03-otdr-fibre-2.svg` (identiques au SVG du code, vérifié par test).
- `app/v1/ampcr_pratique_bank.py` — EX03 déclaré, contexte de correction propre (notions,
  pénalités : brochage faux, A/B ou 50/75 Ω confondus, câble livré malgré un test en échec,
  cordons raccourcis pour un lien permanent trop long, cuivre entre bâtiments, UPC/APC ou
  multimode/monomode mélangés, regarder une fibre).
- `app/seed.py` — `_seed_uaa(…, "EX03", …, position 17)` (additif).
- `tests/test_ticket232_ampcr_pratique_ex03.py` (29 tests) ; comptage adapté dans
  `tests/test_admin_content_hierarchy.py` ; motif « 2 examens blancs » assoupli dans
  `tests/test_ticket231_ampcr_pratique_ex02.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Sujet (public) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex03
- Examen blanc (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-ex03/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Schémas : https://jury-central.lodylands.com/static/img/ampcr-pratique/ex03-fiche-stagiaire.svg,
  …/ex03-testeur-b1-p1-09.svg, …/ex03-bus-salle-retro.svg, …/ex03-otdr-fibre-2.svg

Procédure courte : ouvrir le sujet, parcourir les 7 séquences (ou « Afficher tout le cours sur
une page ») ; aperçu avant impression (Ctrl + P) ; lancer l'examen blanc, répondre à quelques
questions, quitter et reprendre, remettre, vérifier la note /100, le barème et le corrigé.

## 3. Vérifications effectuées

- Tests ciblés `tests/test_ticket232_ampcr_pratique_ex03.py` : **29 passed** — brochages T568A/B
  écrits en dur dans le test et comparés à la fiche du stagiaire (broches 4, 5, 7, 8 ; aucune paire
  séparée ; liaisons du testeur recalculées) ; droit/croisé des 4 liaisons ; choix des 5 câbles ;
  96 m / 101 m et 10 Gb/s en Cat6 à 70 m ; rayons 4/8/10 × Ø, 110 N, 100 mm ; 4 non-conformités du
  bus, Γ = 0,2 ; lectures 25 / 50 / 0 Ω ; portées 400 / 82 / 550 m ; bilan 2,27 dB recalculé,
  pertes 2,10 / 4,62 dB, réception −4,37 dBm dans la plage ; trace : connecteur, courbure (130 m),
  cassure à 175 m ; 4 figures valides, accessibles, **sans ✓/✗ ni conclusion**, fichiers
  statiques identiques ; 10 × 10 = 100, matière du ticket, 7 exigences couvertes, aucun brochage
  donné dans les énoncés ; sujet sans corrigé ; seed idempotent, EX03 juste après PR17 (EX01, EX02
  inchangés) ; réserve `exam` seule ; contexte de correction propre ; navigation, accueil « 3
  examens blancs sur 6 » ; session d'examen : corrigé masqué avant remise, 4 schémas dans leurs
  questions, note /100.
- Tests EX01, EX02, numérotation #236 et hiérarchie seedée : 143 passed (avec EX03).
- **Suite complète : 2853 passed** (une exécution ; seed et banque partagée touchés).
- `ruff check` : fichiers créés et modifiés sans erreur.
- Contrôle visuel (navigateur sans interface, 400 px) des 4 schémas — corrigé pendant la
  session : numéros d'événements de la trace qui se chevauchaient (courbure déplacée à 280 m),
  libellé du cordon du Poste 3 coupé ; page du sujet rendue par l'app à 1 280 px et 400 px.
- Installation : arbre propre sur `develop`, sauvegarde
  (`~/.local/state/jury-central-orch/backups/jury_central-pre-ticket232-20261027-095113.db`),
  fast-forward `4d6cdb3 → 4a7e78a`, seed idempotent (1 UAA créée ; 59 blocs « créés » = 7 blocs
  EX03 + le remplacement habituel des 52 blocs FSE pilotés par le code), redémarrage des deux
  services (actifs), `/health` local et public OK ; sujet, accueil, matrice, PR17, EX02 et les 4
  SVG en HTTP 200 (examen : 303 vers la connexion sans session, normal) ; sujet servi avec 10
  questions et aucun « Corrigé de référence » ; accueil « 3 examens blancs sur 6 ». Compteurs
  utilisateurs/sessions/réponses inchangés (18 / 83 / 658).

Non effectué : validation pédagogique humaine (au propriétaire) ; correction réelle par l'IA
(tests avec `FakeAIProvider`) ; contrôle de l'impression PDF page par page ; session d'examen
parcourue en vrai sur le site.

## 4. Choix techniques faits seul

- **Périmètre du module** : le plan installé rattache PR13 → PR17 au module 3 et PR18 (#219,
  pas encore publié) au module 4 ; la liste des matières du ticket ne cite pas l'installation d'un
  mini-réseau. EX03 couvre donc PR13 → PR17, sans attendre PR18 (la file du superviseur fait
  d'ailleurs dépendre #219 de #232). Position 17 : EX03 suit PR17 et PR18 viendra après lui.
- **10 questions de 10 points** (le ticket demande 10 à 14) : même choix que EX01/EX02.
- **Schémas sans verdict** : la fiche, le testeur, le bus et la trace ne disent pas ce qui est
  faux (les dessins des cours PR16/PR17 affichent leurs conclusions : bus et trace redessinés
  dans le module EX03 avec les mêmes données). Le testeur affiche seulement « ÉCHEC — câblage »,
  comme un appareil réel.
- **Aucun schéma de rappel sur la page du sujet** (EX02 en avait un) : brochages, arbre de choix
  ou tableau de pose donneraient les réponses ; les liens « À revoir » renvoient aux cours.
- **Cas nouveaux, règles des cours** : situations différentes des exemples des cours (fiche
  avec deux paires inversées, mélange A/B prise/panneau, bus avec cordon de vidéosurveillance,
  liaison de 420 m juste au-delà de la portée OM4, cassure après des travaux).
- **Pas d'image générée** : brochages, valeurs et traces exacts sont mieux servis par un dessin
  construit sur des données testées.
- **Valeurs** : celles des cours (normes TIA-568, ISO/IEC 11801, EN 50174-2, IEEE 802.3) ; fiche
  du module 10GBASE-LR fictive (celle de PR17) ; entreprises, repères, mesures fictifs.

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation pédagogique et visuelle par le propriétaire (sujet, impression, correction réelle).
- Suite de l'ordre pédagogique : PR18 (#219) → … → EX04 (#233).
- Suggestion déjà notée (hors périmètre) : fixer l'ordre des questions d'un examen blanc dans le
  moteur de sessions ; bouton de fin de séquence « Passer à l'entraînement » sur la page d'un EX.

## Notification

L'email de livraison est envoyé par le superviseur jcorch à la fin de la session, avec ce rapport
en pièce jointe (copie dans `~/.local/state/jury-central-orch/reports/`).
