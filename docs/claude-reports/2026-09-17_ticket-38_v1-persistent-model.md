# Ticket #38 — Architecture V1 : modèle persistant comptes, banque, sessions, historique

**Date** : 2026-09-17
**Branche** : `feature/38-v1-persistent-model`

---

## 1. Audit initial

Avant toute écriture de code, audit du socle existant (voir aussi
`docs/architecture_v1_data_model.md`, § 4, 9, 13, pour les décisions qui en découlent) :

- **`app/models.py`** : hiérarchie `Subject → Module → UAA → LessonBlock`, quatre tables.
  `BlockType`/`BlockSpace` sont des enums Python (`str, enum.Enum`) mappés via
  `Enum(...)` SQLAlchemy — convention à réutiliser pour tous les nouveaux enums V1
  plutôt que d'introduire un mécanisme différent (ex. tables de lookup pour
  `Role`/`Plan`).
- **`app/database.py`** : pas d'Alembic. `Base.metadata.create_all()` crée les tables
  manquantes (idempotent, `checkfirst=True` par défaut) ; `ensure_schema_migrations()`
  gère uniquement l'ajout de **colonnes** sur des tables déjà existantes (`ALTER TABLE`,
  cas du ticket #22). Comme ce ticket n'ajoute que des tables entièrement nouvelles
  (aucune colonne sur `subjects`/`modules`/`uaas`/`lesson_blocks`), `create_all()` seul
  suffit — aucune fonction de migration par `ALTER TABLE` n'était nécessaire ici.
- **`app/seed.py`** : mécanisme additif déjà établi (`_seed_uaa`, retrait par titre pour
  le contenu obsolète, `reclassified`/`repositioned` pour les migrations de métadonnées
  sur des lignes déjà existantes) — non réutilisé directement (aucune donnée V1 n'est
  seedée par ce ticket), mais le principe « jamais de suppression, jamais d'écrasement
  d'un contenu édité » a directement inspiré les règles d'immutabilité du nouveau modèle.
- **`app/ai/schemas.py`** (ticket #23) : `QUESTION_TYPES` (13 types), la dataclass
  `QuestionnaireQuestion` (forme générique d'une question, tous types), et la
  distinction `DETERMINISTIC_QUESTION_TYPES` / `CONDITIONALLY_LOCAL_QUESTION_TYPES` /
  `ALWAYS_SEMANTIC_QUESTION_TYPES` — vocabulaire et forme conceptuelle réutilisés tels
  quels pour `QuestionVersion.content_json`/`question_type`, sans dupliquer un second
  système de types de questions.
- **`app/editorial_exercise.py`** : moteur persisté existant pour les exercices
  éditorialisés (MC01/MC02/MC03) — architecture différente (contenu figé en base par
  bloc, pas de banque réutilisable ni de versionnement), volontairement non touché ni
  fusionné : le ticket demande un socle générique séparé, pas une refonte de l'existant.
- **`app/auth.py`/`app/admin.py`** : aucun modèle `User` en base — l'admin actuel est un
  unique compte HTTP Basic codé en configuration (`settings.admin_username`). Confirme
  qu'`User`/`Role`/`Plan` sont un ajout net, sans concept dupliqué.
- **`app/quiz.py`/`app/quiz_import.py`** : mécanisme CSV pour les quiz existants, sans
  rapport avec la banque V1 — non réutilisé, non modifié.

Conclusion de l'audit : aucun concept à dupliquer, le seul point de couplage nécessaire
est `Module` (`app.models.Module`), réutilisé tel quel comme portée pédagogique des
nouvelles entités (voir § 2 pour la discussion du choix Module vs UAA).

---

## 2. Décisions de conception

Détaillées et justifiées dans `docs/architecture_v1_data_model.md`, § 9 (« Points
ambigus »). Résumé :

1. `UserRole`/`UserPlan` : enums Python, pas des tables séparées (cohérence avec
   `BlockType`/`BlockSpace`).
2. `Question.module_id`/`SourceDocument.module_id`/... : portée `Module`, pas `UAA` (le
   ticket demande explicitement un rating « par module », et la priorité produit est
   énoncée au niveau matière/module).
3. `QuestionAsset` scopé à `QuestionVersion` (pas `Question`) : un asset peut changer
   d'une version à l'autre sans affecter rétroactivement une ancienne session.
4. Rating empirique de question : champs directs sur `Question`
   (`difficulty_rating`/`rating_sample_size`), pas une table `QuestionRating` séparée —
   le ticket autorise explicitement cette alternative.
5. `SessionAnswer` : une ligne par `SessionQuestion`, mise à jour en place (autosave =
   upsert), pas un journal de tentatives multiples.
6. `AIUsage.period_key` : granularité mensuelle simple (`"AAAA-MM"`), pas de plage de
   dates configurable.

---

## 3. Tables ajoutées

17 nouvelles tables, toutes préfixées `v1_` (aucune collision possible avec le socle
existant), créées dans `app/v1/models.py` :

`v1_users`, `v1_questions`, `v1_question_versions`, `v1_concepts`,
`v1_question_concepts`, `v1_source_documents`, `v1_source_document_versions`,
`v1_assets`, `v1_question_assets`, `v1_questionnaire_sessions`, `v1_session_questions`,
`v1_session_answers`, `v1_user_question_history`, `v1_user_module_ratings`,
`v1_question_feedback`, `v1_ai_usage`, `v1_module_generation_configs`.

Détail du rôle de chacune : voir `docs/architecture_v1_data_model.md`, § 3.

13 enums Python (`UserRole`, `UserPlan`, `ContentStatus`, `GenerationSource`,
`QuestionDifficulty`, `AssetKind`, `AssetSourceType`, `SessionMode`, `SessionStatus`,
`SessionDifficultyRequest`, `AnswerCorrectionStatus`, `FeedbackType`,
`ModuleGenerationStatus`).

6 fonctions utilitaires de création (`create_question`, `add_question_version`,
`create_source_document`, `add_source_document_version`, `record_question_seen`) —
strictement nécessaires pour respecter l'invariant « pas de `current_version_id`
orphelin en dehors de l'instant de création » (référence circulaire Question ↔
QuestionVersion, SourceDocument ↔ SourceDocumentVersion), pas une couche de service.

---

## 4. Index / contraintes

| Table | Contrainte/index | Objectif |
|---|---|---|
| `v1_questions` | `Index(module_id, status)` | « questions par module/status » |
| `v1_question_versions` | `UniqueConstraint(question_id, version)`, `index(question_type)` | version unique par question ; « questions par type » |
| `v1_question_concepts` | `UniqueConstraint(question_id, concept_id)` | pas de tag dupliqué |
| `v1_source_document_versions` | `UniqueConstraint(source_document_id, version)` | version unique par document |
| `v1_question_assets` | `UniqueConstraint(question_version_id, asset_id, role)` | pas de lien dupliqué |
| `v1_questionnaire_sessions` | `Index(user_id, status)` | « sessions user/status » |
| `v1_session_questions` | `UniqueConstraint(session_id, position)` | position unique dans une session |
| `v1_session_answers` | `unique=True` sur `session_question_id` | une réponse par question de session |
| `v1_user_question_history` | `UniqueConstraint(user_id, question_version_id)`, `Index(user_id, question_id)` | historique exact par version + exclusion par question |
| `v1_user_module_ratings` | `UniqueConstraint(user_id, module_id)` | un seul rating par (user, module) |
| `v1_question_feedback` | `Index(question_id, feedback_type)` | requêtes de modération |
| `v1_ai_usage` | `UniqueConstraint(user_id, period_key, provider, model)`, `Index(user_id, period_key)` | usage par période |
| `v1_module_generation_configs` | `unique=True` sur `module_id` | une config par module |

`@validates` (SQLAlchemy) pour quelques invariants simples à valider dès l'affectation
Python, sans attendre un flush : `QuestionVersion.version >= 1`,
`SourceDocumentVersion.version >= 1`, `SessionQuestion.points_max > 0`.

`ForeignKey(..., use_alter=True, name=...)` sur les deux références circulaires
(`Question.current_version_id`, `SourceDocument.current_version_id`) — résout un
avertissement SQLAlchemy sur `drop_all()` (cycle de dépendances FK non ordonnable) et
reste portable vers PostgreSQL (voir § 5 pour la genèse de ce correctif).

Cascades : `QuestionnaireSession → SessionQuestion → SessionAnswer` en
`cascade="all, delete-orphan"` (lignes sans sens hors de leur session, même principe que
`UAA → LessonBlock`) ; **aucune** cascade delete sur `Question`, `QuestionVersion`,
`Asset`, `SourceDocument`, `SourceDocumentVersion`, `User` — vérifié explicitement par
`test_deleting_session_cascades_to_its_own_questions_but_not_to_question_version`.

---

## 5. Migrations

Aucune fonction de migration par `ALTER TABLE` n'a été nécessaire (voir § 1 : aucune
colonne ajoutée à une table existante). La seule action requise est
`Base.metadata.create_all(bind=engine)`, déjà appelée dans `app/main.py` et
`app/seed.py` — il suffisait d'y importer `app.v1.models` pour que ses classes
s'enregistrent auprès de `Base.metadata` avant l'appel :

```python
from app.v1 import models as v1_models  # noqa: F401 — enregistre les tables V1 (#38)
```

`create_all()` est idempotent par nature (`checkfirst=True` par défaut) : sur une base
existante possédant déjà les 4 tables historiques, il crée uniquement les 17 tables
manquantes, sans toucher ni aux tables ni aux lignes déjà présentes. Prouvé par
`test_additive_migration_on_pre_existing_synthetic_database`, qui reconstruit un état
« pré-#38 » synthétique (les 4 tables historiques seules, avec une ligne de donnée), y
applique la création complète du schéma, puis un second passage — voir § 8.

Un bug de conception a été détecté et corrigé pendant le développement : le cycle de
dépendances FK entre `Question`/`QuestionVersion` (et `SourceDocument`/
`SourceDocumentVersion`) déclenchait un `SAWarning` de SQLAlchemy sur `drop_all()`
(« unresolvable foreign key dependency »), utilisé par `tests/conftest.py` avant chaque
test. Corrigé en ajoutant `use_alter=True` + un nom explicite sur les deux FK
`current_version_id` concernées — confirmé disparu après correction (voir § 7).

---

## 6. Tests

`tests/test_ticket38_v1_persistent_model.py` (24 tests), couvrant les 16 scénarios
minimaux demandés plus des invariants d'intégrité supplémentaires :

1–16 (numérotation du ticket) : création Question+QuestionVersion ; plusieurs versions
d'une même question ; ancienne session liée à l'ancienne version après une nouvelle
édition ; archivage sans destruction ; SourceDocumentVersion partagée par plusieurs
questions ; Asset réutilisé par plusieurs questions ; session avec 10 SessionQuestion
ordonnées ; contrainte de position unique (violée intentionnellement, `IntegrityError`
attendue) ; réponse JSON de forme non textuelle (liste d'indices) sauvegardable ;
plusieurs sessions simultanées pour un utilisateur ; historique user/question
consultable et upserté (pas de doublon à la deuxième exposition) ; rating utilisateur
par module (deux modules, deux ratings distincts) + contrainte d'unicité ; feedback
utilisateur ; usage IA/quota (accumulation + contrainte d'unicité par période) ;
migration additive sur DB synthétique pré-#38 ; idempotence du second passage.

Tests d'intégrité supplémentaires : version dupliquée pour une même question
(`IntegrityError`) ; `version`/`points_max` invalides rejetés à la construction
(`ValueError`, via `@validates`) ; `QuestionnaireSession.is_locked()` correct pour
IN_PROGRESS/COMPLETED/ABANDONED ; cascade de suppression d'une session limitée à ses
propres `SessionQuestion`/`SessionAnswer`, jamais à la `QuestionVersion` partagée ;
`ModuleGenerationConfig` par défaut `ACTIVE` ; `Concept` attaché à plusieurs questions
(M:N).

Aucun test n'utilise de fournisseur IA réel ni ne fait d'appel réseau (ce ticket ne
construit ni génération ni correction).

---

## 7. Résultat pytest

```
479 passed, 2 warnings in 88.39s
```

(455 avant ce ticket + 24 nouveaux). Les 2 warnings sont préexistants
(dépréciations `httpx`/`anyio`), sans lien avec ce ticket. Le `SAWarning` initialement
observé sur `Base.metadata.drop_all()` (cycle FK non ordonnable, voir § 5) a été
corrigé et confirmé disparu : absent du résumé de warnings ci-dessus.

---

## 8. Résultat Ruff

```
Found 36 errors.
```

Identique, fichier par fichier et règle par règle, à la base `develop` (comparé via un
worktree isolé). **0 nouvelle erreur.** Un ajustement mineur a été nécessaire pendant le
développement : `UP017` (utiliser l'alias `datetime.UTC` plutôt que
`datetime.timezone.utc`) sur `app/v1/models.py`, corrigé avant validation finale.

---

## 9. git diff --check

```
$ git diff --check --cached
(aucune sortie, exit code 0)
```

Aucune erreur d'espace/fin de ligne détectée sur l'ensemble des fichiers modifiés/créés
par ce ticket.

---

## 10. Limites

- **Aucune route HTTP, aucun template, aucune page** n'est construite par ce ticket
  (conforme à « ne pas construire toute l'UX ») — le modèle est vérifié uniquement au
  niveau base de données via les tests, jamais via une requête HTTP de bout en bout.
- **Pas de schéma strict pour `content_json`** par type de question : validé
  uniquement en JSON générique, la validation stricte par type est explicitement le
  ticket #40.
- **Pas de génération/correction réelle** : `SessionAnswer.correction_status` existe
  mais rien ne le fait transitionner de `PENDING` à `CORRECTED`/`FAILED` — tickets
  #43/#44.
- **`Question.difficulty_rating`/`UserModuleRating.rating`** : valeurs et contraintes
  seulement, aucun algorithme de mise à jour (#45).
- **Pas de test contre une vraie base PostgreSQL** : la portabilité (§ 10 du document
  d'architecture) est un choix de types fait par construction (JSON, DateTime portable,
  FK nommées), pas vérifiée empiriquement contre un second moteur — hors périmètre
  raisonnable de ce ticket.
- **`jury_central.db` réel non touché** : toutes les vérifications se sont faites via
  `pytest` (base SQLite temporaire isolée) ou un fichier SQLite synthétique dans
  `tmp_path` — aucun `seed-db`/`reset-db` exécuté sur la vraie base pendant ce ticket.

---

## 11. Prochaines dépendances

- **#39 (authentification)** : ajoutera les champs manquants sur `User` (mot de passe,
  jetons/session de connexion) — `User` existe déjà, prêt à être complété sans migration
  de table.
- **#40 (schémas par type)** : définira la forme stricte de `content_json` pour chaque
  valeur de `question_type` déjà indexée sur `QuestionVersion`.
- **#41 (sélection banque)** : s'appuiera sur `v1_user_question_history` (exclusion des
  questions déjà vues) et `Question.status`/`module_id` pour la sélection, complètera
  par génération IA si la banque est insuffisante.
- **#42 (autosave)** : construira l'API qui écrit réellement dans `SessionAnswer` et
  fera respecter `QuestionnaireSession.is_locked()`.
- **#43/#44/#45/#46/#47/#48** : consommateurs directs des tables déjà posées
  (génération, correction, rating, admin V1, UX Français, reconnaissance d'image).

---

## Statut

Implémentation, tests, documentation terminés. `pytest -q` : 479 passed. Ruff : 36
erreurs, 0 nouvelle. `git diff --check` : propre. `jury_central.db` réel non modifié.
Prêt pour commit/push. **Aucun merge, aucun déploiement, aucun seed-db sur staging.**
