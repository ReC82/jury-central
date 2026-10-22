# Ticket #83 — Alignement pédagogique : ne pas interroger sur une notion absente du cours

- Ticket : #83 — https://github.com/ReC82/jury-central/issues/83
- **État réel : Installé — à tester**
- SHA installé : `d9d146eca1f896b398ac65c7e2565bad17ac7c5d` (PR #174)

## Synthèse

Le ticket avait déjà été traité le 2026-09-19 (PR #87, rapport
`docs/claude-reports/2026-09-19_ticket-83_course-question-alignment.md`) :

- **A — SMART** : cours MC04 enrichi dans le code (développé *Self-Monitoring, Analysis
  and Reporting Technology*, rôle de surveillance, « ne prédit pas toutes les pannes »,
  ne remplace pas une sauvegarde ; repris dans le vocabulaire FR/EN et le résumé).
- **B/D — audit** MC01→MC38 des acronymes (tableau question → notion → MC → couverture
  cours/lexique → gap) dans ce rapport du 2026-09-19.
- **C — garde de génération** : `app/v1/course_coverage.py` (`COURSE_COVERAGE_GAP`)
  branchée dans `QUALITY_VALIDATORS` (rejet avant persistance) + prompt de génération
  enrichi (`vocabulary` = notions réellement expliquées par le cours, consigne « ne
  demande jamais le développé d'un acronyme absent »).
- **E — tests** : `tests/test_ticket83_course_question_alignment.py` (16 tests).

**Ce qui manquait (constaté le 2026-10-22, lecture seule)** : la base servie par le site
contenait toujours l'**ancien** cours MC04 (SMART sans développé). `seed()` ne modifie
jamais un bloc déjà présent, donc l'enrichissement n'atteignait pas le site. C'est
exactement la situation du ticket signalé : l'élève voyait une question sur le développé
de SMART sans l'avoir dans le cours.

## Changement de cette session (2026-10-22)

- `app/seed.py` : `repair_mc04_smart_expansion` (appelée depuis `seed()`, même modèle que
  la réparation MC08 du ticket #65) remplace uniquement 3 fragments **exacts** d'avant
  correctif du bloc MC04 : définition SMART, ligne « Surveillance de l'état du disque »
  du tableau FR/EN, ligne SMART du résumé d'examen. Un fragment modifié depuis l'admin
  n'est jamais touché ; le reste du bloc est conservé ; idempotent.
- `tests/test_ticket83_mc04_smart_seed_refresh.py` (4 tests) : fragments corrigés = cours
  actuel, ancien cours sans développé, réparation → cours actuel exact + idempotence,
  texte admin modifié et autres UAA intacts.
- Visible : la page MC04 affiche « SMART (Self-Monitoring, Analysis and Reporting
  Technology) » dans les définitions, le vocabulaire FR/EN et « À retenir pour l'examen ».

## Tester

- Cours MC04 : https://jury-central.lodylands.com/uaa/ampcr-mc04 — section 2 «
  Définitions essentielles », section 7 (tableau FR/EN), section 8.
- Entraînement / examen MC04 depuis cette page : une question « Que signifie SMART ? »
  est désormais couverte par le cours.

## Vérifications effectuées

- Lecture seule avant correctif : le bloc MC04 servi ne contenait pas le développé ; les
  3 anciens fragments y étaient présents à l'identique ; appliquer la réparation à ce
  texte donne exactement le cours actuel du code.
- Tests : nouveaux + #83 + #65 → 30 passed ; tests lançant `seed()` (MC01, hiérarchie
  admin, #151) → 37 passed. `ruff check` fichiers touchés : OK. Suite complète non lancée
  (changement borné au seed MC04).
- Installation : sauvegarde de la base, ff-only, seed (« Corrigé (développé SMART ajouté
  au MC04) : 1 bloc(s) »), redémarrage des deux services (active), `/health` local et
  public OK, page MC04 HTTP 200 avec 4 occurrences du développé, page MC08 HTTP 200,
  compteurs utilisateurs/sessions/réponses inchangés (18/71/584).
- Non vérifié : génération réelle d'une session par l'IA (le comportement de la garde est
  couvert par les tests du 2026-09-19).

## Choix techniques faits seul

- Réparation par fragments exacts plutôt que réécriture du bloc entier (PR #89, ouverte,
  qui remplaçait tout le bloc) : protège d'éventuelles éditions admin, cohérent avec
  #169 pour MC08. La PR #89 est donc **remplacée** (MC08 par #169, MC04 par #174) ; elle
  n'a pas été fusionnée et peut être fermée par le propriétaire.
- Pas de nouvel audit : celui du 2026-09-19 reste valable (aucun cours AMPCR modifié
  depuis sur ce point).

## Décisions demandées au propriétaire

Aucune décision utilisateur nécessaire.

## Éléments restant à réaliser

- Gaps résiduels documentés en 2026-09 (DDR3/MC03, ITX/MC02, RFC1918/MC16, RJ45/MC37) :
  non enseignés en toutes lettres, mais neutralisés par la garde (une question demandant
  leur développé est rejetée). Enrichir ces cours serait un ticket de contenu séparé.
- Fermer la PR #89 (remplacée).
