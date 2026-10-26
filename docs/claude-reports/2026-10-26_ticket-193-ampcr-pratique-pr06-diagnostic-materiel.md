# Ticket #193 — [P0][AMPCR pratique PR06] Diagnostic des pannes matérielles — cours, cas et examen écrit

Ticket : [#193](https://github.com/ReC82/jury-central/issues/193) · branche `feature/193-pr06-diagnostic-materiel` · PR [#237](https://github.com/ReC82/jury-central/pull/237)

**État réel : Installé — à tester.**

**SHA installé : `3bf01fe`** (merge de la PR [#237](https://github.com/ReC82/jury-central/pull/237) sur `develop`, 26/10/2026).

## Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr06
- S'entraîner (12 exercices, correction après envoi) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr06/practice
- Examen blanc (mini-examen 10 questions, note /20) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr06/exam
- Accueil du parcours (PR06 publié, les autres « à venir ») : https://jury-central.lodylands.com/ampcr-pratique
- Matrice (AP-15, AP-17, AP-C02 passent « partiel ») : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : se connecter, ouvrir le cours (sur téléphone et sur PC), parcourir les
séquences ou « Afficher tout le cours sur une page » ; vérifier les 8 schémas (lisibles à
360 px, légendes, mention « schéma non officiel ») ; ouvrir quelques corrigés d'exercices
(repliés par défaut) ; lancer « S'entraîner » (10 des 12 exercices), puis « Examen blanc »
(10 questions jamais vues dans le cours, aucune correction pendant la passation) ; envoyer et
lire la note « Soit x / 20 », le corrigé et le barème. Imprimer le cours (A4) si souhaité.
Vérifier que `/modules/ampcr` (théorie MC01–MC38) est inchangé.

## 1. Réconciliation

- #192 (socle, matrice, modèles, PDF officiel) fusionné et installé (`f61242c`) avant cette
  session ; aucune branche, PR ni rapport #193 existant ; aucun cours pratique en base.
- Numérotation vérifiée sur `origin/develop` : `_COURSE_ROWS` place bien PR06 = « Diagnostic
  des pannes matérielles » (module P2), exigences AP-15, AP-17, AP-C02.

## 2. Ce qui a été livré

### Cours (`/uaa/ampcr-pratique-pr06`, 15 blocs)

Toute la matière obligatoire du ticket, dans l'ordre A → D :

| Bloc | Contenu (points du ticket) |
|---|---|
| Objectifs et place dans l'épreuve | objectifs observables ; AP-15, AP-17 (texte exact, page) ; AP-C02 signalé complément ; liens vers la théorie MC02/03/04/05/07/12/29/36 ; mention « supports fictifs » |
| A. Méthode de diagnostic | 1 recueil (tableau) ; 2 observation/hypothèse/test/résultat/conclusion, échelle du plus simple au plus invasif ; 3 reproduire sans aggraver, un changement à la fois, configuration minimale (schéma), test croisé, test négatif ; 5 traçabilité ; démarche (schéma #192) |
| A. Sécurité | 4 coupure secteur et +5 VSB, décharge résiduelle prudente, ESD, jamais ouvrir un bloc, rien sous tension (mesures seulement habilité/outillé), batterie gonflée, matériel endommagé/liquide, données et accord |
| B. Chaîne de démarrage | 6 chaîne secteur → système (schéma), tableau des 6 situations (absence de courant, alimentation partielle, absence de POST, absence d'image, échec de boot, plantage OS), arbre « PC ne démarre pas » (schéma) |
| B. Pannes de démarrage | 7 PC inerte ; 8 ventilateurs/écran noir (iGPU, suffixe F, entraînement mémoire DDR5) ; 9 bips/LED/codes = fabricant, aucune correspondance universelle ; 10 No boot device / OS not found (SATA, M.2 SATA vs NVMe, ports partagés, GPT/ESP vs MBR/CSM, pas de formatage réflexe) ; 11 redémarrages/BSOD/extinction sous charge, indices vs preuves (Kernel-Power 41) |
| Connecteurs | ATX 24 et EPS 8 (schémas), tableau PCIe 6/8, SATA 15/7, Molex ; 20+4, 4+4, EPS ≠ PCIe 8, 12VHPWR, testeur |
| C. Sous-systèmes (1) | 12 RAM (barrette/slot, compatibilité, ECC, test) ; 13 CPU/refroidissement (throttling, arrêt de protection, pâte, firmware) ; 14 PSU ; 15 carte mère (condensateurs, VRM, liquide, codes) + plan de carte (schéma) |
| C. Sous-systèmes (2) | 16 affichage ; 17 stockage (SMART indice, bruit, détection, données d'abord) ; 18 périphériques (panne/connexion/logiciel) ; 19 compatibilité (tableau) |
| D. Documents et décisions | 20 lire capture firmware, photo, voyants, messages, journaux, inventaire, températures, câblage, devis ; 21 constat → cause → test → action → test final → prévention ; 22 escalade, données, remplacer vs réparer ; « Méthode examen » et modèle de compte rendu |
| Exemples : 4 cas résolus | PC inerte ; ventilateurs sans affichage ; stockage non détecté (écran firmware fictif) ; extinction après 10 min de charge (tableau + courbe) |
| Pièges et erreurs fréquentes | 10 encadrés |
| Exercices corrigés (12) | cartes : contexte, documents, consignes, corrigé étape par étape + barème (replié) |
| Mini-examen /20 : mode d'emploi | 10 thèmes et points, déroulement, nature de la correction |
| Fiche mémo, Sources et compléments | sources des valeurs ; compléments non imposés par le PDF listés ; supports fictifs |

### Schémas (8, SVG construits sur données testées)

Chaîne de démarrage (8 étapes) ; arbre décisionnel (6 questions) ; ATX 24 broches (brochage
et couleurs ATX12V) ; EPS 8 broches ; plan schématique de carte mère (fictif) ; écran firmware
(capture fictive) ; courbe de température (mêmes valeurs que le tableau) ; configuration
minimale (garder/retirer, symboles ✓/✗, pas seulement la couleur). Texte alternatif complet,
légende, « schéma non officiel », mise à l'échelle mobile. Aucune image générée (pas
nécessaire ; aucun coût API).

### Exercices et mini-examen

- 12 exercices : 8 scénarios professionnels (comptoir, classement observation/hypothèse,
  PC inerte après orage, « Aucun signal » avec processeur sans iGPU, No boot device MBR/UEFI,
  DDR5 dans un slot DDR4, batterie gonflée, imprimante USB) et 4 analyses de documents (LED
  DRAM + relevé, manuel M.2 + étiquette, journal + températures + test mémoire, rapport SMART).
- Mini-examen : 10 questions à réponse libre (7 courtes, 3 rédigées avec ou sans document),
  2 points chacune, critères explicites ; jamais affichées dans le cours.

### Intégration au moteur existant (aucun nouveau système, aucune table)

- `app/v1/ampcr_pratique_bank.py` : registre `PRACTICAL_COURSES` (cours rédigés + contexte de
  correction), import idempotent avec documents en tableau, réserves séparées par
  `QuestionVersion.prompt_version` (`ampcr-pratique-pr06:practice|exam`, robuste aux nouvelles
  versions).
- `select_bank_questions(mode=…)`, `available_session_lengths(mode=…)` : filtre de réserve,
  sans effet sur les autres matières (testé) ; `start_session` : aucune génération IA pour les
  cours pratiques ; `_pedagogical_context_for` : contexte PR06.
- Routes `/uaa/…/practice|exam` (`app/main.py`), `_ensure_bank_seeded`, `_uaa_code_for`,
  `has_v1_sessions` : ajout du cours pratique.
- Seed : module `AMPCR-PRATIQUE` + UAA PR06 (idempotent, additif).
- Résultats : « Soit x / 20 » pour les sessions du parcours pratique ; cours : fil d'Ariane et
  « Tous les cours » vers `/ampcr-pratique`. CSS des figures et documents dans `jc-theme.css`.
- Docs : `current_state.md`, `ampcr_pratique_v1.md` (procédure d'intégration d'un cours PR
  pour les tickets suivants), `changelog.md`.

## 3. Vérifications

- `tests/test_ticket193_ampcr_pratique_pr06.py` : 26 tests (brochage ATX/EPS exact et dessiné
  dans l'ordre, valeurs PCIe/SATA, ordre de la chaîne et de l'arbre, courbe = tableau, plan sans
  chevauchement, figures valides et accessibles, nombres d'exercices/scénarios/documents, 10
  questions = 20 points, examen absent du cours, matière A-D présente (≈ 60 notions), 4 cas,
  seed idempotent et module séparé, import 12 + 10, réserves, contexte de correction, MC01 non
  filtré, page cours (9 figures, 12 cartes, corrigés repliés), accueil et matrice, théorie
  inchangée, sessions practice/exam tirées de leur seule réserve sans génération (y compris une
  2ᵉ session), longueur d'examen limitée à 10, note /20 affichée).
- Tests #192 (45) verts ; test de comptage du seed mis à jour (+1 module, +1 UAA, +15 blocs).
- Suite complète : 2217 réussis, 1 échec `tests/test_ticket55_urgent_ampcr_full.py::test_json_autosave_api_never_reveals_correctness` (422) — non reproductible : vert 3 fois en isolé et avec son fichier complet (30/30) ; le test envoie une réponse texte à la première question MC01 tirée au hasard (test aléatoire préexistant, sans lien avec PR06, dont la sélection MC01 n'est pas affectée — testé).
- `ruff check` sans erreur sur tous les fichiers touchés (4 B008 préexistants de `app/main.py`
  inchangés).
- Rendu réel (Chromium/Playwright, 390 px) : aucun débordement horizontal de page ; schémas,
  tableaux défilants, cartes d'exercice et encadrés lisibles ; impression A4 générée
  (PDF non inspecté page par page).
- Après installation : base sauvegardée (`jury_central-pre-ticket193-20261026-175102.db`), fast-forward `f61242c` → `3bf01fe`, pas de changement de `pyproject.toml`, seed idempotent (1 module, 1 UAA, +15 blocs nets ; les 52 blocs FSE sont supprimés/recréés à l'identique par le rafraîchissement FSE existant à chaque seed), services `jury-central` et `jury-central-correction-worker` actifs, `/health` OK local et public, `/uaa/ampcr-pratique-pr06`, `/ampcr-pratique`, `/ampcr-pratique/matrice`, `/modules/ampcr`, `/uaa/ampcr-mc01`, `/uaa/fse-fse01`, `/` en 200 (practice/exam : 303 vers la connexion, attendu), 9 figures et 12 cartes servies, « 1 cours publiés » sur l'accueil, compteurs inchangés 18 comptes / 79 sessions / 636 réponses.
- **Non vérifié** : qualité réelle de la correction IA sur ces barèmes (tests avec
  `FakeAIProvider` uniquement) ; rendu sur un vrai téléphone.

## 4. Checklist de validation éditoriale et visuelle (#192 § 3)

- [x] Toute la matière obligatoire enseignée, dans l'ordre A → D (test des notions).
- [x] Sections rattachées à AP-15/AP-17 ; AP-C02 et autres compléments signalés.
- [x] Valeurs vérifiées et sources citées (bloc « Sources » : ATX12V/EPS12V, PCI-SIG CEM, Serial ATA, Microsoft, Intel).
- [x] Aucune modalité, durée, question « officielle » inventée ; supports marqués fictifs.
- [x] Sécurité rappelée avant les manipulations ; aucune action destructive en premier réflexe.
- [x] Renvois vers la théorie MC au lieu de la dupliquer.
- [x] Chaque question : contexte, données, tâche, barème, corrigé ; pas de récitation d'acronyme.
- [x] Correction invisible avant envoi ; formulation libre acceptée (consigne du barème).
- [x] 4 cas, 12 exercices (8 scénarios, 4 documents), mini-examen 10 questions /20.
- [x] Schémas SVG depuis des données testées ; orientation indiquée (numérotation, lecture).
- [x] Légende, texte alternatif, « non officiel » ; information non portée par la seule couleur.
- [x] Lisible à 360-390 px ; A4 généré (non inspecté page par page).
- [x] Aucune image générée.
- [x] UAA du module `AMPCR-PRATIQUE`, seed idempotent ; matrice à jour ; MC01–MC38 inchangés.
- [x] Tests ciblés verts, ruff sans nouvelle erreur ; rapport, commentaire ; email par l'orchestrateur.

## 5. Choix techniques faits seul

1. **Réserves séparées** entraînement/examen via `prompt_version` (champ existant) : le moteur
   partage d'habitude une seule réserve, mais le ticket veut 12 exercices corrigés visibles dans
   le cours ET un mini-examen sans correction visible ; mélanger les deux aurait exposé les
   corrigés. Aucune migration.
2. **Pas de génération IA** pour PR06 : le ticket exige des questions contextualisées,
   techniquement exactes et barémées ; une réserve épuisée réutilise des questions déjà vues
   (repli existant) plutôt que d'en générer.
3. **Note /20** = score / nombre de questions × 20 (chaque question vaut 1 point dans le moteur,
   2 points sur 20 dans le barème) ; le barème transmis au correcteur est en proportion des
   points de la question.
4. **Types existants** : `short_answer` (avec barème → correction IA), `long_answer`,
   `document_analysis`, une `classification` (correction locale) dans les exercices.
5. **Matrice** : PR06 laisse AP-15, AP-17, AP-C02 en « partiel » (EX02 et autres cours liés pas
   encore publiés) ; `VALIDATED_REQUIREMENT_IDS` reste vide (validation par le propriétaire).
6. **Module** `AMPCR-PRATIQUE` dans la matière Informatique (constante prévue par #192) ; il
   apparaît aussi sur `/subjects/informatique`, à côté de la théorie, sans mélange.
7. Pas d'image générée par API : tous les supports nécessaires sont des schémas à données.

## 6. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire. Remarque (hors périmètre, non modifiée) : le
mini-cours théorique MC29 indique « bips répétés → cause très probable RAM » ; PR06 enseigne
que les codes sonores dépendent du fabricant. Un ajustement de MC29 pourrait faire l'objet d'un
ticket.

## 7. Reste à réaliser / suites proposées

- Validation pédagogique et visuelle par le propriétaire (puis ajout éventuel de AP-15/AP-17 à
  `VALIDATED_REQUIREMENT_IDS` quand cours et EX liés seront relus).
- EX02 (examen du module P2) et les autres cours : réutiliser le modèle PR06 décrit dans
  `docs/ampcr_pratique_v1.md` § 2 (PR11 #194, PR15 #197… sont déjà ouverts).
