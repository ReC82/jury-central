# Ticket #197 — [P0][AMPCR pratique PR15] Câblage RJ45 T568A/B — fabrication, schémas et tests

Ticket : [#197](https://github.com/ReC82/jury-central/issues/197) · branche `feature/197-pr15-rj45` · PR [#244](https://github.com/ReC82/jury-central/pull/244)

**État réel : Installé — à tester.**

**SHA installé : `df3888f`** (merge de la PR #244 sur `develop`, 26/10/2026).

## Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr15
- S'entraîner (16 exercices, 10 tirés par session, correction après envoi) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr15/practice
- Examen blanc (mini-examen 10 questions, note /20) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr15/exam
- Accueil du parcours (« 3 cours publiés sur 30 prévus ») : https://jury-central.lodylands.com/ampcr-pratique
- Matrice (AP-18, AP-20, AP-34 passent « partiel ») : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : se connecter ; ouvrir le cours sur téléphone puis sur PC (séquences ou
« Afficher tout le cours sur une page ») ; vérifier les deux brochages (T568B puis T568A, broche
1 à gauche, liste texte sous chaque fiche), la comparaison A/B, l'ordre faux, les câbles droit et
croisé, les 4 affichages de testeur ; ouvrir quelques corrigés (repliés) ; lancer « S'entraîner »
(placements de fils, classements et une remise en ordre corrigés automatiquement), puis
« Examen blanc » (10 questions jamais vues dans le cours, aucune correction pendant la
passation) ; envoyer et lire « x / 20 », le corrigé et le barème. Vérifier que PR06, PR11 et la
théorie `/modules/ampcr` sont inchangés.

## 1. Réconciliation

- Aucune branche, PR, rapport ni contenu PR15 avant cette session (worktree créé depuis
  `origin/develop` = `4b3469d`).
- Dépendances livrées et installées : #192 (socle, matrice, `T568A`/`T568B` déjà testés,
  helpers SVG) et #236 (numérotation) : `_COURSE_ROWS` place bien PR15 = « Câblage RJ45 T568A/B —
  fabrication, schémas et tests » (ticket 197, module P3, AP-18, AP-20, AP-34). Modèle
  d'intégration repris de PR06/PR11.

## 2. Ce qui a été livré

### Cours (`/uaa/ampcr-pratique-pr15`, 13 blocs, toute la matière 1 → 6 du ticket)

| Bloc | Contenu |
|---|---|
| Objectifs et place dans l'épreuve | 6 objectifs observables ; AP-34, AP-18, AP-20 (texte exact, page) ; AP-C01 signalé complément ; renvois AP-28 / AP-36 (PR21, PR18) ; lien théorie MC15 ; supports fictifs |
| 1. Supports et connecteurs | 4 paires / 8 conducteurs, rôle de la torsade, détorsadage (≈ 13 mm au plus) ; U/UTP, F/UTP, U/FTP, S/FTP et UTP/FTP/STP historiques ; blindage continu et mise à la terre ; Cat5e/Cat6/Cat6A (fréquence ≠ débit, longueurs, compatibilité) ; 8P8C dit RJ45, fiche, prise, keystone, panneau, cordon, monobrin/multibrin et fiches adaptées ; précautions (courbure, écrasement, traction, humidité, EMI/secteur, cheminement) |
| 2. Brochage T568A/T568B | orientation de lecture explicite ; tableau broche par broche ; schémas B et A ; comparaison (A/B échangent orange et vert, bleu et marron identiques) ; positions 1-2, 3-6, 4-5, 7-8 et numérotation TIA des paires ; paire séparée (split pair) avec schéma de l'ordre faux |
| 3. Droit, croisé, Auto MDI-X | droit A-A/B-B, croisé A-B (1→3, 2→6, 3→1, 6→2) avec schémas ; usage des broches 10/100BASE-TX (2 paires) vs 1000BASE-T (4 paires bidirectionnelles) ; cas historiques PC↔switch, switch↔switch, PC↔PC, PC↔routeur ; Auto MDI-X et ses limites ; physique / négociation / IP |
| 4. Fabrication | matériel, outils (pince, dénudeur, coupe-câble, poinçonnage, testeurs continuité / qualification / certification) ; procédure en 8 étapes (schéma) et points de détail ; anatomie de fiche sertie ; sertir une fiche vs raccorder un keystone vs terminer un câble permanent |
| 5. Tests et dépannage | wiremap : conforme, ouvert, court-circuit, paire inversée, paires croisées, paire séparée, intermittent/mauvais contact ; 4 affichages de testeur ; limites du testeur de continuité ; atténuation, NEXT, blindage, signal/bruit ; 100 m / 90 m ; Cat5e 1 Gb/s, Cat6A 10 Gb/s sur 100 m, Cat6 10 Gb/s sur longueur réduite (nuancé) ; diagnostic par symptôme (lien absent, 100 Mb/s, instabilité, erreur de brochage) |
| 6. Contexte professionnel | chaîne baie → panneau → câble permanent → prise → cordon → PC (schéma, lien permanent / canal) ; cordon préfabriqué vs fabriqué ; sécurité ; rapport d'intervention (besoin, norme, schéma, outils, tests avant/après, résultats, défauts corrigés, validation) |
| Exemples (4) | 1 droit B-B ; 2 croisé A-B ; 3 erreur broches 3/6 (relevé 4↔6) ; 4 lien limité à 100 Mb/s |
| Pièges | 12 encadrés |
| Exercices corrigés (16) | cartes : contexte, documents, consignes, corrigé étape par étape + barème (replié) |
| Mini-examen /20 : mode d'emploi | 10 thèmes et points, déroulement, barème, nature de la correction |
| Fiche mémo, Sources et compléments | normes citées, compléments signalés, supports fictifs |

### Visuels (14 figures SVG, aucune image générée)

Construits **depuis les tuples `T568A`/`T568B`** du socle (TIA/EIA-568) : 1-2 brochages T568B et
T568A orientés (fiche vue côté contacts, languette dessous, câble vers le bas, broche 1 à gauche ;
fils blancs rayés ; liste texte broche · couleur · paire · position sous chaque fiche, lisible en
noir et blanc) ; 3 comparaison A/B (= / ≠) ; 4 ordre FAUX (paires séparées, marqué « ne pas
reproduire ») ; 5-6 câble droit B-B et croisé A-B (liaisons calculées) ; 7 anatomie de fiche
sertie ; 8 les 8 étapes de sertissage ; 9-12 affichages de testeur fictifs (conforme, circuit
ouvert broche 7, paire 1-2 inversée, paires séparées 3-6/4-5) ; 13 relevé de l'exemple 3 ;
14 chaîne baie → PC avec lien permanent ≤ 90 m et canal ≤ 100 m. Texte alternatif complet,
légende, « schéma non officiel », information jamais portée par la seule couleur.

### Exercices et mini-examen

- 16 exercices (ticket : ≥ 15) : **6 brochage/schéma** (≥ 5 : placer les 8 fils T568B, autre bout
  d'un croisé, ordre faux, A/B/les deux, liaisons d'un câble B-A, fiche tenue à l'envers),
  **4 analyses de testeur** (≥ 4 : circuit ouvert broche 2, paire 3-6 inversée, six relevés à
  classer, rapport de qualification 128 m), **3 choix** (≥ 3 : trois liaisons d'une imprimerie,
  monobrin/multibrin, connexion directe de deux PC), **3 procédures** (≥ 3 : remise en ordre du
  sertissage, pose d'un keystone et test du lien permanent, compte rendu). 3 classements et
  1 remise en ordre sont corrigés localement (tout ou rien par élément).
- Mini-examen : 10 questions à réponse libre (2 pts chacune, /20) avec barème détaillé ; jamais
  affichées dans le cours ; aucune question de développé d'acronyme.

### Intégration (moteur existant, aucune table, aucune migration)

- `app/v1/ampcr_pratique_pr15_{figures,bank,course}.py` ; PR15 ajouté à `PRACTICAL_COURSES`
  avec son contexte de correction (brochages exacts, refus de « Cat6 = 10 Gb/s sur 100 m »)
  dans `app/v1/ampcr_pratique_bank.py` ; seed idempotent `_seed_uaa(…, "PR15", …)`.
- Docs : `current_state.md`, `ampcr_pratique_v1.md`, `changelog.md`.

## 3. Vérifications

- `tests/test_ticket197_ampcr_pratique_pr15.py` : 30 tests — brochages comparés à la liste du
  ticket recopiée indépendamment ; seules les broches 1, 2, 3, 6 diffèrent ; paires par position ;
  paires séparées détectées sur l'ordre faux ; liaisons droit/croisé/exemple 3 ; chaque figure
  dessinée depuis les données dans l'ordre de lecture, avec le texte de chaque broche ; 4 sorties
  de testeur ; chaîne ; figures valides/accessibles ; nombres d'exercices par type ;
  **réponses auto-corrigées techniquement justes** ; **tout ordre « 1 … 8 » cité dans le cours,
  un corrigé ou un barème est T568A, T568B ou l'ordre faux/inversé voulu** ; aucune affirmation
  « Cat6 10 Gb/s sur 100 m » non nuancée ; 4 exemples ; examen absent du cours ; notions 1-6 ;
  types de cartes ; seed idempotent ; import et réserves ; contexte de correction ; page ;
  accueil « 3 cours publiés » ; sessions practice/exam tirées de leur seule réserve sans
  génération ; note /20 ; deux sessions d'entraînement soumises.
- Tests adaptés : PR11 (« cours publiés » sans nombre figé) et comptage du seed (+1 UAA, +13 blocs).
- **Suite complète : 2317 réussis, 0 échec** (17 min 35). `ruff check` propre sur les fichiers touchés.
- Installation (sous verrou) : sauvegarde `jury_central-pre-ticket197-20261026-192454.db` ;
  fast-forward `4b3469d` → `df3888f` ; `pyproject.toml` inchangé ; seed (1 UAA + 13 blocs ; les
  52 blocs FSE sont recréés à l'identique, comportement existant) ; services actifs ; `/health`
  OK local et public ; PR15, PR11, PR06, `/ampcr-pratique`, matrice, `/modules/ampcr`, MC15, `/`
  en 200 (practice/exam : 303 vers la connexion, attendu) ; 14 figures servies ; compteurs
  18 comptes / 80 sessions / 637 réponses (inchangés).
- **Rendu réel** (Chromium sur le site installé, « tout le cours sur une page ») : 390 px et
  1280 px sans débordement horizontal ; 14 figures capturées et relues. Un contrôle préalable
  avait révélé 3 tableaux trop larges à 390 px et des libellés qui se chevauchaient (chaîne,
  paires séparées) → corrigés avant fusion (listes, tableaux d'exercice verticaux).
- **Non vérifié** : qualité réelle de la correction IA (tests avec `FakeAIProvider`) ; vrai
  téléphone ; impression A4 non générée pour ce cours (mêmes styles d'impression que PR06/PR11).

## 4. Choix techniques faits seul

1. **Orientation unique** de tous les schémas : fiche vue côté contacts, languette dessous, câble
   vers le bas → broche 1 à gauche (énoncée dans le cours, l'alt et la légende). Les prises
   femelles ne sont pas dessinées : le cours renvoie au repère A/B imprimé sur le keystone, pour
   éviter toute ambiguïté de vue miroir.
2. **Pas d'image générée par API** (coût : 0) : les gestes et outils sont mieux servis par un
   schéma annoté exact ; le ticket interdit l'image pour couleurs et broches, et l'enjeu (examen
   le 28/10) privilégie l'exactitude. Aucune nouvelle bibliothèque.
3. Faits retenus (TIA-568, ISO/IEC 11801, IEEE 802.3, EN 50174-2) : détorsadage ≈ 13 mm max,
   courbure 4× (U/UTP) / 8× (blindé), traction ≈ 110 N ; Cat5e 100 MHz, Cat6 250 MHz (10 Gb/s
   ≈ 37-55 m), Cat6A 500 MHz ; canal 100 m = 90 m + cordons ; PC↔routeur historiquement croisé ;
   Auto MDI-X : un seul côté suffit, peut être désactivé si vitesse/duplex forcés.
4. « T568B le plus fréquent sur les cordons du commerce », mais **l'installation existante
   décide** (exercice X01 en T568A).
5. Classements et remise en ordre corrigés localement pour l'entraînement ; mini-examen
   uniquement en réponses libres.
6. Matrice : AP-18, AP-20, AP-34 passent « partiel » ; `VALIDATED_REQUIREMENT_IDS` reste vide
   (validation par le propriétaire).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Reste à réaliser / suites proposées

- Validation pédagogique et visuelle par le propriétaire.
- Petit détail de libellé : la légende du schéma T568B dit « Même orientation que T568A » alors
  que T568B est affiché en premier (sans effet technique) ; à reprendre au prochain passage sur
  PR15 si souhaité.
- EX03 (#232) peut réutiliser `wiremap_svg` et les données PR15 ; PR13/PR14 (#216, #217)
  approfondissent les câbles et les débits sans dupliquer la section 1.
