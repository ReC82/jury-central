# Ticket #198 — [P0][AMPCR pratique PR16] Câble coaxial et BNC — impédance, fabrication et diagnostic écrit

Ticket : [#198](https://github.com/ReC82/jury-central/issues/198) · branche `feature/198-pr16-coax-bnc` · PR [#246](https://github.com/ReC82/jury-central/pull/246) (cours) et [#247](https://github.com/ReC82/jury-central/pull/247) (lisibilité à 390 px)

**État réel : Installé — à tester.**

**SHA installé : `47a2967`** (merge de la PR #247 sur `develop`, 26/10/2026).

## Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr16
- S'entraîner (16 exercices, 10 tirés par session, correction après envoi) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr16/practice
- Examen blanc (mini-examen 10 questions, note /20) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr16/exam
- Accueil du parcours (« 4 cours publiés ») : https://jury-central.lodylands.com/ampcr-pratique
- Matrice (AP-35 passe « partiel ») : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte : se connecter ; ouvrir le cours sur téléphone puis sur PC (séquences ou
« Afficher tout le cours sur une page ») ; vérifier la coupe du coax, le schéma du bus 10BASE2
conforme (T sur chaque carte, **deux** terminateurs 50 Ω, une seule terre), les **4 schémas
fautifs** et leurs corrections, la comparaison 10BASE2 / 10BASE5 / vidéo 75 Ω, le BNC éclaté et
la procédure de montage, les lectures d'ohmmètre et les deux traces de réflectomètre ; ouvrir
quelques corrigés ; lancer « S'entraîner » (3 classements et une remise en ordre corrigés
automatiquement), puis « Examen blanc » (10 questions absentes du cours, aucune correction
pendant la passation), envoyer et lire « x / 20 ». Vérifier que PR06, PR11, PR15 et la théorie
`/modules/ampcr` sont inchangés.

## 1. Réconciliation et prérequis

- Aucune branche, PR, rapport ni contenu PR16 avant cette session (worktree créé depuis
  `origin/develop` = `030795b`).
- **PDF officiel** : présent et versionné par #192,
  `docs/references-officielles/ampcr/2026-2027-1/26-27-1-CESSP-Consignes-Assistant_Maintenance_PCreseaux-Pratique.pdf`
  (avec README de provenance et transcription page par page). Exigences utilisées, texte exact
  p. 5-6 : **AP-35** « Description de la réalisation d'un câble avec connecteurs BNC. » (p. 6),
  **AP-18** « Les différents types de câbles : UTP, FTP, STP, Coax. » (p. 5), **AP-20**
  caractéristiques des câbles dont la « notion d'impédance » (p. 6).
- Numérotation #236 installée : `_COURSE_ROWS` place bien **PR16 = « Câble coaxial et BNC —
  impédance, fabrication et diagnostic écrit »** (ticket 198, module P3, AP-18, AP-20, AP-35).
  Aucune autre unité touchée. Modèle d'intégration repris de PR06/PR11/PR15.

## 2. Ce qui a été livré

### Cours (`/uaa/ampcr-pratique-pr16`, 15 blocs, toute la matière 1 → 12 du ticket)

| Bloc | Contenu |
|---|---|
| Objectifs et place dans l'épreuve | 6 objectifs ; AP-35, AP-18, AP-20 (texte exact, page) ; AP-C01 complément ; caractère historique de l'Ethernet coaxial (retiré d'IEEE 802.3 en 2011) ; aucune théorie MC sur le coaxial |
| 1. Structure | âme, diélectrique, blindage feuille/tresse, gaine (figure) ; EMI, atténuation, bande passante, souplesse, contraintes de pose ; familles RG-58/épais/RG-59/RG-6/RG-62 et marquage |
| 2-3. Impédance et réflexions | définition intuitive, indépendante de la longueur, non mesurable à l'ohmmètre ; 50 Ω vs 75 Ω ; câble = connecteur = terminaison = équipement ; **BNC en 50 Ω et 75 Ω** ; Γ = (Zc−Z0)/(Zc+Z0) calculé (0 ; +0,2 ; +1 ; −1) ; effet selon la fréquence |
| 4. BNC | baïonnette quart de tour, mâle/femelle, T, terminateur, raccord ; compatibilité 50/75 Ω ; à sertir / à compression / à souder / à visser ; outils (figure éclatée) |
| 5-7. 10BASE2, 10BASE5, vidéo | tableau 10BASE2 (10 Mb/s, bus, RG-58 50 Ω, 185 m, 30 postes, 0,5 m, T sur la carte, deux terminateurs 50 Ω, une terre, 5-4-3) avec schéma ; 10BASE5 (≈ 10 mm, 500 m, prise vampire, transceiver, AUI ≤ 50 m, 100 transceivers, 2,5 m, N) **distinct** ; vidéo/TV/RF 75 Ω ; « la forme ne fait pas le protocole » |
| 8-9. Fabrication et outils | choix du matériel, sécurité, cotes **de la notice** (figure A/B/C sans valeur), 7 étapes de montage, contrôles (visuel, traction, continuité, court-circuit, adaptation, ≈ 25 Ω), tableau d'outils |
| 10. Schémas | grille de relecture en 7 points ; 4 schémas fautifs (terminateur absent ; dérivation + deux terres ; tronçon et terminateur 75 Ω ; câble coupé) et corrections |
| 11. Diagnostic | symptômes → causes ; démarche en 5 étapes ; lectures d'ohmmètre (figure + tableau) ; dichotomie ; réflectomètre (sens de la réflexion, d = VF × c × t ÷ 2, 2 traces) |
| 12. Sécurité et rapport | hors tension / réseau arrêté, prévenir avant d'ouvrir un bus, une seule terre, migration conseillée ; grille du rapport |
| Exemples (4) | 1 réaliser une liaison 10BASE2 ; 2 terminateur absent ; 3 mauvaise impédance ; 4 connecteur mal serti |
| Pièges (12), Exercices (16), Mini-examen /20, Fiche mémo, Sources et compléments | |

### Visuels (14 figures SVG, aucune image générée)

Coupe annotée du coax ; BNC à sertir éclaté ; **bus 10BASE2 conforme** ; **4 bus fautifs** ;
comparaison 10BASE2 / 10BASE5 / vidéo 75 Ω ; cotes de dénudage « de la notice » ; 7 étapes de
montage ; contrôle d'un BNC serti (✓/✗) ; lectures d'ohmmètre ; traces de réflectomètre
(ouvert, court-circuit). Les bus sont **dessinés depuis un modèle de données** (`Bus`,
`Station`, `Span`) : la liste des non-conformités sous chaque schéma, les lectures d'ohmmètre et
les distances sont **calculées** par les mêmes fonctions que les corrigés. Texte alternatif
complet, légende, « schéma non officiel », information jamais portée par la seule couleur,
largeur 380 px (mobile), protégées des coupures de page (A4).

### Exercices et mini-examen

- 16 exercices (ticket : ≥ 15) : **5 schémas** (≥ 5 : relevé à corriger, 8 segments conforme/non
  conforme, « étoile » coaxiale, impédances fausses, limites 185 m / 30 postes), **4 choix**
  (≥ 4 : 50 ou 75 Ω selon 7 usages, câble vidéo pour rallonger le bus, liste de matériel,
  catalogue), **3 procédures** (≥ 3 : remise en ordre du montage, cordon BNC/BNC, remplacement
  d'un BNC sur bus en service), **4 diagnostics** (≥ 3 : 7 lectures d'ohmmètre, réflectomètre,
  poste déplacé, connecteur intermittent). 3 classements et 1 remise en ordre corrigés localement.
- Mini-examen : 10 questions à réponse libre (2 pts, /20), barème détaillé, absentes du cours,
  aucune question de développé de sigle.

### Intégration (moteur existant, aucune table, aucune migration)

`app/v1/ampcr_pratique_pr16_{figures,bank,course}.py` ; PR16 ajouté à `PRACTICAL_COURSES` avec
son contexte de correction (refus de « tous les BNC sont à 50 Ω », des cotes universelles, de la
confusion 10BASE5/10BASE2…) ; seed idempotent `_seed_uaa(…, "PR16", …)` avec titres obsolètes
(PR #247). Docs : `current_state.md`, `ampcr_pratique_v1.md`, `changelog.md`.

## 3. Vérifications

- `tests/test_ticket198_ampcr_pratique_pr16.py` : 31 tests — impédances et limites recopiées du
  ticket indépendamment du code ; Γ et distances TDR ; bus conforme à deux terminateurs 50 Ω et
  une terre ; chaque règle détectée (terminateur, terre, dérivation, RG-59, 185 m, 30 postes,
  0,5 m, limite exacte acceptée) ; lectures 25/50/0/∞ ; figures dessinées depuis leur bus ;
  10BASE5 sans BNC ni T ; aucune cote chiffrée ; figures valides et accessibles ; nombres
  d'exercices par type ; **réponses auto-corrigées justes** ; 4 exemples ; examen absent du
  cours ; matière 1-12 ; types de cartes ; seed idempotent ; import et réserves ; contexte de
  correction ; page ; accueil « 4 cours publiés » ; sessions practice/exam sans génération ;
  note /20 ; deux sessions d'entraînement soumises.
- Tests adaptés : PR15 (« cours publiés » sans nombre figé), comptage du seed (+1 UAA, +15 blocs).
- **Suite complète : 2348 réussis, 0 échec** (18 min 09). `ruff check` propre sur les fichiers
  touchés. Après le correctif #247 : tests PR16/PR15/PR11/hiérarchie, 104 réussis.
- Installation (sous verrou, deux fois) : sauvegardes `jury_central-pre-ticket198-20261026-200617.db`
  et `jury_central-pre-ticket198-fix-20261026-200944.db` ; `030795b` → `635c97c` → `47a2967` ;
  `pyproject.toml` inchangé ; seed (1 UAA + 15 blocs, puis 4 blocs remplacés ; les 52 blocs FSE
  sont recréés à l'identique, comportement existant) ; services actifs ; `/health` OK local et
  public ; PR16, PR15, PR11, PR06, `/ampcr-pratique`, matrice, `/modules/ampcr`, `/` en 200
  (practice/exam : 303 vers la connexion, attendu) ; 14 figures servies ; compteurs
  18 comptes / 80 sessions / 637 réponses inchangés.
- **Rendu réel** (Chromium sur le site, « tout le cours sur une page ») : 390 px et 1280 px sans
  débordement de la page ; figures relues en capture. Le premier contrôle a révélé 4 tableaux
  défilant horizontalement à 390 px → convertis en listes (PR #247).
- **Valeurs vérifiées** : IEEE 802.3 cl. 8/10 et IEC 61169-8 via la documentation publiée
  (articles Wikipédia 10BASE2, 10BASE5, BNC connector, qui citent ces clauses) ; non retenues
  faute de confirmation : tolérance des terminateurs, résistance linéique, facteur de vélocité
  normatif (le facteur de vélocité est donné comme donnée d'exercice).
- **Non vérifié** : qualité réelle de la correction IA (tests avec `FakeAIProvider`) ; vrai
  téléphone ; impression A4 non générée (mêmes styles que PR06/PR11/PR15).
- **Limite connue** : le tableau du catalogue (exercice E09) défile encore dans son cadre à
  390 px, comme les tableaux de documents d'exercice de PR15 (style partagé des documents
  d'exercice) ; la page elle-même ne déborde pas.

## 4. Choix techniques faits seul

1. **Modèle de bus** plutôt que des SVG dessinés à la main : un seul objet produit le schéma,
   ses non-conformités, la lecture d'ohmmètre et le corrigé ; impossible de les contredire.
2. **Bus vertical** (stations à droite) : lisible sur téléphone sans réduire le texte.
3. **Pas de cotes de dénudage** : figure A/B/C « voir la notice », conformément au ticket.
4. **Ohmmètre** : réseau arrêté, résistance du câble négligée (mentionné partout) ; 25 Ω normal.
5. **Aucune image générée par API** (coût 0) : les schémas exacts suffisent ; aucune nouvelle
   bibliothèque.
6. 10BASE2 « 30 postes / 0,5 m » repris tels que cités par la documentation (IEEE 802.3 cl. 10) ;
   règle 5-4-3 et réflectomètre présentés comme **compléments**.
7. Matrice : AP-35 (ainsi que AP-18, AP-20) passent « partiel » ; `VALIDATED_REQUIREMENT_IDS`
   reste vide (validation par le propriétaire).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Reste à réaliser / suites proposées

- Validation pédagogique et visuelle par le propriétaire.
- EX03 (#232, câblage RJ45/BNC/fibre) peut réutiliser `Bus`, `bus_svg`, `bus_errors` et les
  lectures d'ohmmètre ; PR13/PR14 (#216, #217) approfondissent les supports et l'atténuation sans
  dupliquer les sections 1-3.
- Amélioration repérée, hors périmètre : les tableaux de documents d'exercice ne se replient pas
  à 390 px (défilement dans le cadre) sur PR15 et PR16 ; une mise en page empilée de
  `_table_html` profiterait à tous les cours pratiques.
