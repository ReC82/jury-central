# Examen blanc CESS Français — mode Examen blanc (chantier prioritaire)

**Branche :** `feature/french-cess-mock-exam`
**Base :** `develop` @ `3f8b172962825af664ea8f887d46a52285c5c430` (merge PR #95, ticket #94 PHASE A)
**NE MERGE RIEN. AUCUN DÉPLOIEMENT.**

## Contexte officiel

L'épreuve écrite du CESS Français (filière TQ/P) dure 3h et compte pour 50% de la note
globale. Elle demande **une seule tâche parmi deux familles**, choisie le jour de
l'examen sans que le candidat ne le sache à l'avance : synthèse de documents (informer un
lecteur qui n'a pas lu les documents) OU argumentation (convaincre, en réaction à une
opinion ou dans une réclamation/demande). Ce chantier construit un moteur capable de
générer des examens blancs réellement différents à chaque fois, dans les deux familles,
avec correction adaptée.

## ARCHITECTURE

Modèle dédié `FrenchMockExam` (`app/v1/models.py`) plutôt que de forcer ce contrat dans
le registre `Question`/`QuestionVersion` (#40) : un examen blanc est **une production
longue holistique notée /100**, jamais un ensemble de questions indépendantes notées 0-1
comme le reste du moteur V1 — § 46 du chantier, « créer uniquement le nécessaire ».

Point d'architecture notable : **`FrenchMockExam.status` EST son propre job**, pas une
table `CorrectionJob`/`SessionBuildJob` séparée. Ces deux tables existantes (#88/#92) sont
taillées pour `QuestionnaireSession` (session_id unique, uaa_id/question_count...) — un
schéma sans rapport avec un examen blanc. Le worker réclame atomiquement les lignes
`PENDING` (build) et `SUBMITTED` (correction) directement sur `FrenchMockExam`, avec la
MÊME primitive `UPDATE ... WHERE status = X` (jamais deux appels IA concurrents pour la
même ligne) que `claim_next_pending_correction_job`/`claim_next_pending_build_job`.

Exactement 3 documents par examen, référencés par 3 colonnes FK (`document_1_id`/`_2_id`/
`_3_id`) plutôt qu'une table d'association — le nombre est fixe par construction (jamais
un 4e document possible, ce qui EST la règle métier § 28).

## OFFICIAL_FORMAT_MAPPING

- `exam_type=SYNTHESIS` → synthèse de documents (grille A. Pertinence / B. Reformulation
  / C. Intelligibilité / D. Recevabilité, § 17).
- `exam_type=ARGUMENTATION_OPINION` → réaction à une opinion (grille A. Pertinence /
  B. Intelligibilité / C. Recevabilité, § 25).
- `exam_type=ARGUMENTATION_REQUEST` → réclamation/demande (même grille que ci-dessus).

## SYNTHESIS

Génération IA (`app.ai.french_mock_exam_prompts.build_generate_mock_exam_messages`)
suit l'ORDRE STRICT imposé (§ 9) : thème/type déjà choisis côté serveur → 3 documents
originaux → analyse → tâche créée APRÈS. La tâche doit exploiter au moins 2 documents
(instruction explicite au modèle). Grille /100 en 4 catégories, corrigé privé
(`expected_information_json`) avec idées essentielles + document(s) source + axe,
contradictions, compléments — jamais exposé avant correction (vérifié :
`test_expected_information_never_exposed_before_correction`).

## ARGUMENTATION_OPINION / ARGUMENTATION_REQUEST

Même portefeuille de 3 documents. OPINION : le prompt exige qu'un document contienne une
opinion claire attribuable à un énonciateur du document (jamais une personne réelle),
`target_opinion`/`required_genre` stockés. REQUEST : relation asymétrique explicite
(élève→direction, employé→employeur...), `required_genre`/`recipient` stockés. Le
correcteur IA reçoit l'instruction explicite de **ne jamais juger l'opinion/la thèse
choisie elle-même** (§ 26), uniquement la qualité du raisonnement — testé via
`test_ai_correction_failure_never_produces_a_zero` et la lecture du prompt système
(`CORRECT_MOCK_EXAM_SYSTEM_PROMPT`).

## SURPRISE_MODE

`choose_exam_type` (`app.v1.french_mock_exam_service`) : type choisi CÔTÉ SERVEUR (jamais
laissé à l'IA — fiabilité de l'anti-répétition), fenêtre glissante des 3 dernières
sessions. Si les 2 dernières sont de la même famille, force l'autre famille ; sinon
alterne SYNTHESIS/ARGUMENTATION selon la parité du nombre de sessions déjà créées
(déterministe, testable, « pas besoin d'algorithme complexe », § 27). Au sein
d'ARGUMENTATION, alterne OPINION/REQUEST. Le type devient immuable dès la création de la
ligne (`FrenchMockExam.exam_type`, jamais modifié après) — la tâche générée ensuite
utilise TOUJOURS la grille correspondante.

## DOCUMENT_GENERATION

Documents 500-900 mots ciblés dans le prompt (§ 8) ; validation serveur tolérante sur la
longueur exacte mais stricte sur les invariants structurels (`_validate_generation`,
`app.v1.french_mock_exam_service`) : exactement 3 documents, angles distincts
(`doc_kind` ∈ {faits_donnees, expert_analyse, temoignage_chronique}, ≥2 valeurs
différentes exigées), tâche non vide, grille sommant à 100 (±5). Un dossier qui échoue
cette validation est traité comme un échec de génération (`BUILD_FAILED`), jamais
silencieusement accepté — § 28/§ 29.

## SOURCE_TRANSPARENCY

Interdiction explicite dans le prompt système de toute source réelle inventée (Le Soir,
RTBF, Le Monde, CNRS...) ou de journaliste réel — chaque document présenté comme support
d'entraînement original Jury Central. Vérifié : `test_no_fake_real_source_in_generated_documents`.
Documents visibles pendant la question ET la correction via le système SourceDocument
existant (#77/#79, réutilisé strictement — `create_source_document`, route
`/documents/{version_id}` déjà en place, inchangée) : « Lire » + « Ouvrir dans un nouvel
onglet » sur chaque document, dans le portefeuille de rédaction ET la page de résultats.

## MULTI_EXAM_VARIATION / RECENT_THEME_AVOIDANCE

Catalogue de 20 thèmes (`app.v1.french_mock_exam_themes.MOCK_EXAM_THEMES`, liste du § 4
du chantier, non limitative — le prompt autorise explicitement l'IA à proposer un autre
thème si accessible/non spécialisé/riche/compatible, mais la sélection SERVEUR reste bornée
au catalogue pour une anti-répétition fiable et testable). `choose_theme` évite les
`theme_key` des 5 dernières sessions de l'utilisateur. `compute_signature` (theme_key +
exam_type + empreinte de la tâche générée) stockée par examen, jamais deux signatures
identiques sur 10 générations consécutives (`test_multi_generation_produces_varied_themes_and_types`,
`test_compute_signature_deterministic_and_distinct`).

## RUBRICS / EXPECTED_INFORMATION

Grilles structurées en catégories `{name, max_points, criteria}`, sommant à 100,
générées PAR l'IA (jamais codées en dur — seul le NOMBRE de catégories differe par type,
4 pour synthèse/3 pour argumentation, vérifié par le prompt système). `expected_information_json`
(corrigé privé) : idées essentielles avec documents sources, contradictions, compléments,
opinion cible — utilisé uniquement comme contexte du prompt de correction, jamais exposé
côté navigateur avant `COMPLETED`.

## ANTI_COPY

Heuristique LÉGÈRE (`_similarity_ratio`, `app.v1.french_mock_exam_service`) : ratio de
mots significatifs (4+ lettres) de la réponse également présents dans les documents
source — jamais une détection NLP lourde, jamais un rejet automatique. Transmis à l'IA
correctrice comme simple INDICATION dans le prompt (« taux de similarité textuelle :
X%, interprète avec discernement — citations légitimes/termes techniques/noms propres
acceptables, copier-coller excessif non reformulé à sanctionner dans la catégorie
reformulation/recevabilité »).

## ASYNC_BUILD / ASYNC_CORRECTION / NO_504

`POST /francais/examen-blanc/start` ne fait JAMAIS d'appel IA — crée la ligne `PENDING`
et redirige immédiatement (confirmé avec un `FakeAIProvider` délibérément ralenti,
`test_build_with_deliberately_slow_provider_does_not_block_start` : réponse < 0.5s malgré
un délai de 1s côté fournisseur, 0 appel IA constaté pendant le POST). Même garantie pour
`POST .../submit`. Le worker existant (`app.v1.correction_worker`, déjà étendu par #92)
traite maintenant QUATRE files dans la même boucle : `CorrectionJob`, `SessionBuildJob`,
et les deux nouvelles (`FrenchMockExam` PENDING/SUBMITTED) — toujours un seul processus,
**aucun changement systemd nécessaire**, l'unité déjà déployée couvre le nouveau
traitement dès que ce code est redéployé.

## AI_FAILURE_FALSE_ZERO

**0** — si la correction IA échoue, `status=CORRECTION_INCOMPLETE`, `score` reste `None`
(jamais 0 fabriqué), bouton « Reprendre la correction » ciblé sur la MÊME ligne (jamais un
second examen créé). Vérifié bout en bout :
`test_ai_correction_failure_never_produces_a_zero` (échec puis retry réussi, une seule
ligne `FrenchMockExam` pour l'utilisateur au final).

## HISTORY / EXPORT_PRINT

`/mes-sessions` affiche désormais une troisième catégorie de lignes, distincte des
sessions V1 génériques et des préparations en attente : `Examen blanc CESS — <type> —
<thème>`, avec date/statut/score. Export Markdown (portefeuille, consigne, production,
grille détaillée, feedback) et impression (bannière imprimable pour l'état
CORRECTION_INCOMPLÈTE, boutons interactifs masqués en `@media print`).

## Tests (`tests/test_french_mock_exam.py`, 27 tests)

Landing (3 modes) ; lien depuis la page module Français ; démarrage non bloquant pour les
3 modes ; provider délibérément ralenti prouvant l'absence d'appel IA dans le POST ;
exactement 3 documents distincts ; aucune source réelle inventée ; documents visibles
avec liens Lire/nouvel onglet ; tâche créée après les documents + corrigé privé jamais
exposé ; grilles synthèse et argumentation sommant à 100 ; autosave + compteur de mots ;
réponse longue (20 000+ caractères) sans troncature ; reprise après logout/login ;
soumission non bloquante ; flux complet avec score ; échec IA sans faux 0 + retry ciblé ;
échec de génération sans examen fantôme + retry ; parité documents élève/IA ; anti-
répétition thème (fonction unitaire) ; anti-répétition type sans série de 5 identiques ;
génération multiple (10 examens) avec thèmes/types variés et signatures distinctes ;
signature déterministe ; historique avec type/thème ; export + print après correction ;
isolation entre utilisateurs (404 si non-propriétaire).

Validation : `pytest -q` (suite complète) → **1338 passed, 0 failed**. `ruff check .` →
36 erreurs, baseline `develop` inchangée, **0 nouvelle dette**. `git diff --check` propre.
Aucun appel OpenAI réel (`FakeAIProvider` partout, y compris pour simuler un échec IA).

## Simplifications assumées (transparence)

- **Tableau préparatoire** (§ 15) : implémenté comme un champ de texte libre autosauvegardé
  (`preparation_table_json.notes`), non comme une grille HTML dynamique à colonnes
  Document/Axe éditables — objectif identique (brouillon facultatif, jamais noté,
  persistant), complexité d'implémentation très inférieure. Documenté ici pour arbitrage
  ChatGPT si une vraie grille éditable est requise dans une itération suivante.
- **Anti-copier-coller** (§ 42) : heuristique de recouvrement lexical simple transmise
  comme indication au correcteur IA (voir ANTI_COPY ci-dessus), pas une détection NLP de
  paraphrase — cohérent avec l'esprit du chantier (« ne pas sanctionner termes
  techniques/titres/noms propres »/laisser l'IA distinguer citation légitime et copie).
- **Mise en réseau vs succession de résumés** (§ 41) : évaluée QUALITATIVEMENT par l'IA
  correctrice via la grille et le prompt système (instruction explicite de sanctionner
  une succession « Document 1 dit... Document 2 dit... »), jamais une blacklist de mots —
  exactement ce que demandait le chantier (« Ne pas utiliser une blacklist naïve »).
- **Cours à relire** (§ 43) : mapping préparé pour FR08/FR09/FR10/FR11-14, mais seuls
  FR08/FR09/FR10 (livrés, ticket #94 PHASE B) sont effectivement liés — FR11-14 (non
  livrés) ne produisent jamais de lien mort.

## Fichiers

- `app/v1/models.py` (`FrenchMockExam`, `FrenchMockExamType`, `FrenchMockExamStatus`)
- `app/ai/french_mock_exam_schemas.py` (nouveau — dataclasses génération/correction)
- `app/ai/french_mock_exam_prompts.py` (nouveau — prompts + schémas JSON stricts OpenAI)
- `app/ai/provider.py` (Protocol étendu : `generate_french_mock_exam`/`correct_french_mock_exam`)
- `app/ai/openai_provider.py` (implémentation réelle des 2 méthodes)
- `app/ai/fake_provider.py` (implémentation factice déterministe, tracée)
- `app/v1/french_mock_exam_themes.py` (nouveau — catalogue de 20 thèmes)
- `app/v1/french_mock_exam_service.py` (nouveau — sélection thème/type, build/correction
  async, validation, anti-répétition, similarité anti-copie)
- `app/v1/correction_worker.py` (étendu : traite désormais 4 files dans la même boucle)
- `app/v1/routes_french_mock_exam.py` (nouveau — toutes les routes du chantier)
- `app/main.py` (routeur enregistré)
- `app/v1/routes_sessions.py` (`my_sessions` inclut les examens blancs)
- `app/templates/v1_mock_exam_landing.html`, `v1_mock_exam_build_waiting.html`,
  `v1_mock_exam_write.html`, `v1_mock_exam_correcting.html`, `v1_mock_exam_results.html`
  (nouveaux)
- `app/templates/module_detail.html` (entrée « Examen blanc CESS » sur la page Français)
- `app/templates/v1_history.html` (lignes examen blanc)
- `tests/test_french_mock_exam.py` (nouveau, 27 tests)
- `docs/claude-reports/2026-09-20_french-cess-mock-exam.md` (ce rapport)
