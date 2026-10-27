# Ticket #225 — [AMPCR pratique PR26] Analyser une demande d'intervention technique

- Ticket : https://github.com/ReC82/jury-central/issues/225
- **État réel : Installé — à tester**
- SHA installé : `b01778b936c91acd7c695a82e30c4bdfcd85b3fa` (fusion de la PR #300 dans `develop`)
- Date : 2026-10-27 (session jcorch autonome)

## 1. Résultat

Le cours **PR26 « Analyser une demande d'intervention technique »** est publié dans le parcours
**Informatique AMPCR → Pratique écrite** (module `AMPCR-PRATIQUE`), séparé de la théorie MC
(cours, banque, examen et progression distincts ; lien seulement vers MC36). Il occupe la
position 26, juste après l'examen blanc EX04.

**Numérotation vérifiée** : dans le plan installé (`_COURSE_ROWS`, numérotation de #236),
l'emplacement PR26 porte bien le sujet du ticket (« PR26, ticket 225, Analyser une demande
d'intervention technique », exigences **AP-16** « Vocabulaire technique » (officielle, p. 5) et
**AP-C01** (complément : rédiger une réponse écrite de technicien)). Aucun autre cours n'a été
touché ni renuméroté.

### Contenu (16 blocs)

**9 chapitres**, chacun avec objectifs, théorie, procédure professionnelle, erreur fréquente,
attendu « à l'écrit », repère rapide et renvoi aux exercices liés :

1. **Recueillir la demande** : démarche complète, demandeur, date, symptômes, interprétation,
   attente et échéance.
2. **Contexte** matériel / logiciel / réseau ; **inventaire et références** (n° d'inventaire,
   n° de série, garantie) ; date d'apparition ; **changements récents** ; **utilisateurs touchés**.
3. **Qualifier** : observation ou hypothèse ; panne reproductible ou intermittente (journal,
   critère sur une durée).
4. **Impact, urgence et priorisation** : règles, matrice P1–P4, délais de prise en charge.
5. **Sauvegarde, consentement, confidentialité, risques et autorisation** ; modèle de **bon
   d'accord** avant une opération risquée.
6. **Questions utiles** (ouvertes puis fermées, sans jargon ni accusation) et **reformulation**.
7. **Fiche d'incident** (formulaire en 6 sections), **vocabulaire technique**, **grille
   d'évaluation** sur 20.
8. **Critères de réussite**, **plan d'action**, **estimation**.
9. **Escalade** : arbre des 5 contrôles (sécurité, droits, données, compétence, budget) et fiche
   d'escalade.

**5 dossiers entièrement corrigés** (ticket : PC inerte, impression, lenteur, accès partagé,
Wi-Fi) : demande reçue, questions et réponses, qualification, priorité, critères de réussite,
plan et estimation, décision d'escalade, **fiche d'incident complétée** et conclusion rédigée.

**20 exercices corrigés** (ticket : ≥ 18) : 1 remise en ordre de la démarche ;
7 qualifications (observation/hypothèse, reproductible/intermittente, priorités, questions,
escalade, ticket du centre de services, journal d'une panne intermittente) ; **2 schémas à
compléter** (matrice de priorité, arbre d'escalade) ; **5 analyses de tickets** (fiche
incomplète, courriel client, journal de tickets à regrouper, inventaire et garantie, évaluation
d'une fiche avec la grille) ; **5 rédactions** (reformulation, critères de réussite, plan et
estimation, accord du client, fiche d'escalade).

**Mini-examen de 10 questions /20** (2 points chacune, réponses libres, onglet « Examen blanc »,
jamais affiché dans le cours).

**Visuels** : 3 procédures, matrice de priorité, schéma observation/hypothèse, arbre d'escalade,
fiche d'incident vierge (7 figures SVG) + 2 schémas à compléter servis en fichiers statiques ;
formulaires et grille en tableaux HTML imprimables. **Aucune image générée** (rien d'utile ici :
toutes les informations sont du texte et des règles exactes).

### Fichiers

- `app/v1/ampcr_pratique_pr26_figures.py` — règles et données (`priority`, `escalation`,
  `INCIDENT_FIELDS`/`missing_fields`, `estimate`, `EVAL_GRID`/`grid_score`, `STATEMENTS`,
  `OCCURRENCES`, `QUESTIONS`, `DOSSIERS`) et schémas.
- `app/v1/ampcr_pratique_pr26_bank.py` — 20 exercices et 10 questions d'examen.
- `app/v1/ampcr_pratique_pr26_course.py` — les 16 blocs.
- `app/v1/ampcr_pratique_bank.py` — déclaration de PR26 et contexte de correction IA propre.
- `app/seed.py` — `_seed_uaa(…, "PR26", …, position 26)`, ajout seul.
- `app/static/img/ampcr-pratique/pr26-*.svg` (2 fichiers).
- `tests/test_ticket225_ampcr_pratique_pr26.py` (31 tests) ; comptages adaptés dans
  `tests/test_admin_content_hierarchy.py` et `tests/test_ticket224_ampcr_pratique_pr25.py`.
- `docs/current_state.md`, `docs/ampcr_pratique_v1.md`, `docs/changelog.md`.

## 2. Liens pour tester

- Cours : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr26
- S'entraîner (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr26/practice
- Examen blanc /20 (connexion requise) : https://jury-central.lodylands.com/uaa/ampcr-pratique-pr26/exam
- Accueil du parcours : https://jury-central.lodylands.com/ampcr-pratique
- Matrice : https://jury-central.lodylands.com/ampcr-pratique/matrice

Procédure courte :
1. Ouvrir le cours, parcourir les 16 séquences (chapitres, matrice, fiche d'incident, bon
   d'accord, grille, cinq dossiers corrigés avec leurs fiches, exercices).
2. « S'entraîner » : 10 exercices tirés des 20 (schémas et documents affichés dans la question).
3. « Examen blanc » : 10 questions, note sur 20 ; après l'envoi, vérifier corrigé et barème.

## 3. Vérifications effectuées

- **Tests ciblés** `tests/test_ticket225_ampcr_pratique_pr26.py` : **31 passed** — matrice
  recalculée case par case, ordre et premier échec des contrôles d'escalade, rubriques
  obligatoires et fiche incomplète, estimation (+ 25 %, quart d'heure supérieur) et grille
  recalculées à la main, absence d'ambiguïté des phrases à classer, cohérence des 5 dossiers
  (priorité affichée = priorité calculée, fiche complète, escalade), figures (validité,
  accessibilité, données dessinées), schémas à compléter sans leurs réponses, fichiers statiques
  identiques au SVG généré, exercices (format du socle, auto-correction, valeurs des corrigés),
  matière du ticket, liens, types de cartes, seed idempotent et position, réserves séparées,
  contexte de correction, pages, sessions d'entraînement et d'examen /20 sans génération IA.
- **Suite complète** (une exécution, `seed.py` partagé) : **3 111 passed**, aucun échec (26 min).
- **`ruff check`** sur les fichiers créés et modifiés : All checks passed.
- **Contrôle visuel** (Chromium sans interface) des schémas et des dossiers rendus ; corrigés
  pendant la session : titres de colonnes du schéma observation/hypothèse qui débordaient,
  décimales affichées avec un point (« 56.25 » → « 56,25 »).
- **Installation** : arbre propre sur `develop` ; sauvegarde
  `~/.local/state/jury-central-orch/backups/jury_central-pre-ticket225-20261027-171149.db` ;
  avance rapide `976afdc → b01778b` ; seed : 1 UAA et 68 blocs créés (16 de PR26 + remplacement
  habituel des 52 blocs FSE) ; deux services actifs ; `/health` local et public OK ; PR26, PR25,
  EX04, accueil, matrice et les 2 schémas statiques en HTTP 200 ; entraînement en 303 vers la
  connexion (normal sans session) ; 20 cartes d'exercice servies ; « 26 cours publiés sur 30 » ;
  compteurs utilisateurs / sessions / réponses inchangés (18 / 84 / 661).

**Non effectué** : validation pédagogique humaine ; session réelle avec la vraie correction IA.

## 4. Choix techniques faits seul

- **Matrice de priorité** : 3 niveaux d'impact × 3 niveaux d'urgence → P1 à P4 (1+1 → P1,
  1+2 → P2, 1+3 ou 2+2 → P3, au-delà → P4), délais 30 min / 2 h / journée / 5 jours ouvrables.
  Version simplifiée des pratiques de centre de services (ITIL), présentée partout comme
  **convention du cours** (« la procédure de l'entreprise fait foi »).
- **Estimation** : somme des tâches + 25 %, arrondie au quart d'heure supérieur (convention).
- **Grille d'évaluation sur 20** en 9 critères (acquis / partiel = moitié / absent).
- **Ordre d'escalade** : sécurité → autorisation → données → compétence → budget (le plus grave
  d'abord ; une intrusion continue d'agir).
- **Exigences citées** : AP-16 (officielle) et AP-C01 (complément) selon la matrice ; AP-C03
  (protection des données) et AP-15 (dépannage) ajoutées sur les items concernés.
- **Fichiers** : même découpage que PR25 (figures / bank / course) ; schémas à compléter en
  fichiers statiques comme PR18 à PR25.
- **Pas de lien** vers un lexique AMPCR (non publié, #84) ni vers PR27–PR29 (non publiés).

## 5. Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## 6. Éléments restant à réaliser

- Validation visuelle et pédagogique par le propriétaire.
- Suggestions (hors périmètre, non faites) : PR27 (#226) et PR29 (#228) pourront renvoyer à la
  fiche d'incident et à la grille de PR26 ; MC36 (théorie) pourrait renvoyer vers PR26.
