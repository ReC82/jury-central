# Ticket #94 — Français : parcours des 20 mini-cours (PHASE A : FR01→FR05)

**Branche :** `feature/94-french-20-course-path`
**Base :** `develop` @ `5ed5f6d95962e7daaf08f71b27e011665f62bba7` (merge PR #93, ticket #92)
**NE MERGE RIEN. AUCUN DÉPLOIEMENT.**

## Contexte et cadrage

Le fichier de référence `parcours_20_mini_cours_francais_CESS_P_prompts_V2_qualite(1).html`
n'était accessible nulle part dans cette session (recherche exhaustive du système de
fichiers, y compris `~/.claude/downloads`) — jamais réellement joint à la conversation.
Sur confirmation explicite de l'utilisateur (« ChatGPT a vérifié son contenu... NE BLOQUE
PAS pour cela »), PHASE A a été implémentée directement à partir des objectifs détaillés
fournis dans le ticket lui-même (titres, objectifs pédagogiques, exigences de supports,
règles de qualité communes FR01→FR05) — non réinventés.

Seule PHASE A (FR01→FR05) est livrée dans ce ticket, conformément à l'instruction finale
de l'utilisateur (« Implémente uniquement PHASE A [...] Puis arrête-toi pour review
ChatGPT avant FR06 »).

## Architecture (générique, réutilise #47/#77/#79/#88/#90/#92 — aucune nouvelle brique)

- `app/v1/francais_plan.py` : `FRANCAIS_PLAN` étendu avec 5 nouvelles entrées
  (FR01→FR05), chacune avec ses propres `allowed_notions`/`competencies` (transmis au
  correcteur IA). **C01 (ticket #47) reste strictement inchangée** — jamais renommée,
  fusionnée ni supprimée, pour ne casser aucun test/usage existant.
- `app/v1/francais_fr01_05_content.py` (nouveau) : textes originaux support (learning
  texts, dossiers de mini-test, textes imparfaits...), jamais un contenu protégé par le
  droit d'auteur.
- `app/v1/francais_fr01_05_bank.py` (nouveau) : 5 fonctions `import_francais_frXX_to_bank`
  (même pattern idempotent que `import_francais_c01_to_bank`/`import_mc01_legacy_to_bank`),
  créant systématiquement un `SourceDocument` réel pour toute question qui en dépend.
- `app/v1/francais_fr01_05_courses.py` (nouveau) : contenu des 5 cours, structure en 10
  points imposée par le ticket, corrigés d'exercices guidés en `<details>` (masqués par
  défaut — `app.content.render_markdown` laisse déjà passer le HTML brut, aucune nouvelle
  architecture).
- `app/seed.py` : 5 nouveaux blocs `BlockSpace.COURSE` + 5 `_seed_uaa(...)`, purement
  additifs, après C01.
- `app/v1/routes_sessions.py` :
  - `_ensure_bank_seeded` généralisé via `_FRANCAIS_BANK_IMPORTERS` (dict slug→importeur)
    plutôt que d'empiler un `elif` par cours au fil des phases B/C/D.
  - **Correctif nécessaire** : la logique d'examen (`_enqueue_build_for_uaa`) donnait
    auparavant 20 questions à TOUT examen Français (`francais_plan is not None`), correct
    tant que seule C01 existait comme UAA pilote unique. Avec FR01→FR05 comme mini-cours
    PAR COURS (comme MC01→MC37, jamais comme MC38), cette règle est restreinte à
    `uaa_code in ("MC38", "C01")` — FR01→FR05 gardent le volume standard, y compris à
    l'examen. **FR20 (§ 12 du ticket, phase D) devra recevoir sa propre fonction de
    composition transversale dédiée (miroir de `_start_mc38_transversal_session`), jamais
    un simple ajustement de `question_count`.**

## Contenu par cours (structure en 10 points, aucun stub)

Chaque page `/uaa/francais-frXX` contient réellement : 1. Ce que tu dois savoir faire à
l'examen — 2. Théorie progressive — 3. Définitions importantes — 4. Méthode étape par
étape — 5. Exemples commentés (avec les textes réels intégrés) — 6. Mauvaises réponses
comparées aux bonnes — 7. Pièges et erreurs fréquentes — 8. Exercices guidés (`<details>`,
corrigé masqué par défaut) — 9. Corrigés très expliqués — 10. Fiche mémo. Les liens
S'entraîner/S'évaluer sont déjà fournis génériquement par `_uaa_space_nav.html` (ticket
#22) pour toute UAA — jamais dupliqués dans le contenu.

Supports produits (respectant les exigences exactes du ticket) :
- **FR01** : 2 textes d'apprentissage (~250 mots), une paire D1/D2 complète, dossier de
  mini-test de 2 documents NOUVEAUX.
- **FR02** : 3 documents d'apprentissage de genres différents (article, texte informatif,
  lettre professionnelle) + 1 NOUVEAU texte de mini-test (~450 mots, dans la fourchette
  350–550).
- **FR03** : 2 textes substantiels à indices réels + 1 NOUVEAU texte de mini-test
  contenant tous les indices nécessaires.
- **FR04** : idées en vrac, paragraphes désorganisés (4 paragraphes mélangés), situation
  de communication complète (courriel de réclamation) en mini-test.
- **FR05** : 2 textes imparfaits avec versions corrigées (visibles uniquement en exercice
  guidé, masquées par défaut) + 1 NOUVEAU texte imparfait en mini-test.

## Banque — 40 questions, 0 orphelin

8 (FR01) + 9 (FR02) + 8 (FR03) + 7 (FR04) + 8 (FR05) = 40 questions, réparties sur
`short_answer`/`long_answer`/`document_analysis`/`source_comparison`/`vocabulary`/
`classification` — **aucun QCM artificiel** (vérifié :
`test_fr01_05_bank_uses_only_relevant_question_types`). Audit exhaustif (§ 6/§ 8 du
ticket) : toute question dont l'énoncé suppose un texte lisible (« d'après le texte »,
« compare »...) référence un `source_document_version_id`/`_ids` réel —
`test_no_orphan_document_dependent_questions_in_fr01_05` confirme **0 orphelin**.

## Documents — parité IA/élève (#77/#79 réutilisés tels quels)

`build_question_display`/`_document_contexts_for` (inchangés depuis #77) garantissent
structurellement qu'un document non déclaré dans le modèle Pydantic d'un type de question
ne peut jamais atteindre l'IA sans être aussi montré à l'élève. Vérifié explicitement sur
FR03 (exam complet, comparaison `student_doc_ids == ai_doc_ids`) : **AI_STUDENT_SOURCE_PARITY
confirmée**, y compris après résolution complète de la correction (le lien « Voir le
texte » reste présent sur la page de résultats).

## Async build (#92) / async correction (#88/#90) — aucune régression, aucun 504

`_enqueue_build_for_uaa`/`run_session_build_job` (inchangés) traitent FR01→FR05 comme tout
autre UAA générique — vérifié : POST `/start` redirige toujours immédiatement vers
`/session-build-jobs/{id}` (jamais de génération dans le cycle HTTP), et POST `/submit`
retourne toujours 303 immédiatement, la correction réelle s'exécutant via le job
(`test_fr01_exam_session_is_nonblocking_and_scoped`,
`test_fr04_full_practice_flow_async_correction_no_false_zero`). Aucun faux 0 : chaque
réponse corrigée a un `correction_status == "corrected"` et un `points_awarded` non
`None`.

## Tests (`tests/test_ticket94_french_20_courses.py`, 16 tests)

Plan/registre (FR01→FR05 présents, C01 intacte, titres lisibles sans « UAA ») ; seed
(5 UAA publiées) ; pages non-stub (10 sections présentes sur les 5 cours) ; corrigés
masqués par défaut (`<details>`) ; audit anti-orphelin (0 détecté) ; idempotence de
l'import ; types de questions pertinents uniquement ; practice ciblé par cours (jamais de
question d'un autre FRxx) ; exam non bloquant et volume standard (pas 20) ; document
visible pendant la question (FR02) ; parité IA/élève pendant la correction (FR03) ; flux
practice complet async sans faux 0 (FR04) ; export + historique mentionnant le cours
(FR05) ; réponse longue 13 000+ caractères sans troncature ; non-régression C01. Un test
pré-existant (`tests/test_admin_content_hierarchy.py::test_seed_is_idempotent`) attendait
un nombre fixe d'UAA/blocs — mis à jour pour inclure les 5 nouvelles UAA (+5 UAA, +5
blocs), seule modification hors périmètre strict de #94.

Validation : `pytest -q` (suite complète) → **1306 passed, 0 failed**. `ruff check .` →
36 erreurs, baseline `develop` inchangée, **0 nouvelle dette**. `git diff --check` propre.
Aucun appel OpenAI réel (`FakeAIProvider` partout).

## Statut final — PHASE A uniquement (B/C/D non commencées, par instruction explicite)

FR01, FR02, FR03, FR04, FR05 : **READY**. FR06→FR20 : non implémentées (phases B/C/D,
prochains tickets après review ChatGPT).

## Fichiers

- `app/v1/francais_plan.py` (FR01→FR05 ajoutées, `FrancaisUAAPlan.allowed_notions`/
  `competencies` par cours)
- `app/v1/francais_fr01_05_content.py` (nouveau — textes originaux)
- `app/v1/francais_fr01_05_bank.py` (nouveau — 40 questions, 17 `SourceDocument`)
- `app/v1/francais_fr01_05_courses.py` (nouveau — 5 cours complets, structure 10 points)
- `app/seed.py` (5 blocs + 5 `_seed_uaa`, purement additif)
- `app/v1/routes_sessions.py` (`_FRANCAIS_BANK_IMPORTERS`, correctif volume d'examen
  Français par cours vs global)
- `tests/test_ticket94_french_20_courses.py` (nouveau, 16 tests)
- `tests/test_admin_content_hierarchy.py` (compteurs UAA/blocs mis à jour)
- `docs/claude-reports/2026-09-20_ticket-94_french-20-course-path.md` (ce rapport)
