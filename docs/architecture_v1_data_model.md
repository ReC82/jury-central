# Jury Central — Architecture V1 : modèle de données persistant

Ce document décrit le socle de données introduit par le ticket #38 : comptes
utilisateurs, banque de questions versionnée, sessions de questionnaire persistantes et
reprenables, historique, ratings, feedback et suivi d'usage IA — pour toutes les
matières, en commençant par Informatique AMPCR et Français CESS Professionnel.

Il complète `docs/ARCHITECTURE.md` (organisation générale du projet) sans le remplacer :
le socle éditorial existant (`Subject`/`Module`/`UAA`/`LessonBlock`, `app/models.py`) et
les moteurs d'exercices déjà déployés (`app/editorial_exercise.py`, `app/quiz.py`,
`app/ai/`) restent inchangés et continuent de servir MC01/MC02/MC03 tels quels — voir §
« Ce qui n'est pas touché » plus bas.

Le code vit dans `app/v1/models.py` (nouveau package, séparé de `app/models.py`) — voir
§ « Pourquoi un module séparé ».

---

# 1. Objectifs

Décisions produit qui contraignent directement ce modèle (voir le ticket #38) :

- les cours restent consultables sans compte ; entraînement et examen nécessitent un
  compte ;
- toute question générée est conservée — aucune suppression physique dans les workflows
  métier futurs ;
- modifier le contenu d'une question crée toujours une nouvelle version, jamais une
  modification rétroactive d'une version déjà servie ;
- une session est persistante, reprenable exactement après fermeture du navigateur, et
  immuable une fois terminée ;
- plusieurs sessions simultanées par utilisateur ;
- une banque locale de questions réutilisables réduit le besoin d'appeler l'IA à chaque
  questionnaire (génération IA en batch uniquement si la banque est insuffisante) ;
- rating utilisateur **par module** (jamais un rating global) et rating empirique par
  question, distinct de la difficulté déclarée ;
- SQL pour les relations métier, JSON versionné pour le contenu spécifique à un type de
  question ;
- SQLite aujourd'hui, migration PostgreSQL envisageable plus tard sans réécriture.

---

# 2. Diagramme des entités

```
                    ┌───────────┐        ┌──────────┐
                    │  Subject  │──1:N──▶│  Module  │◀────────────────────────┐
                    └───────────┘        └────┬─────┘                        │
                                               │ (existant, réutilisé)        │
                    ┌──────────────────────────┼──────────────────────────┐  │
                    │                          │                          │  │
                    ▼                          ▼                          │  │
            ┌───────────────┐         ┌─────────────────┐                 │  │
            │    Question   │         │  SourceDocument  │                 │  │
            │ (identité)    │         │   (identité)     │                 │  │
            └───┬───────┬───┘         └────────┬─────────┘                 │  │
                │        │ current_version_id            │ current_version_id │  │
                │1:N      └──────────────┐                └──────────┐        │  │
                ▼                        ▼                           ▼        │  │
      ┌──────────────────┐   (pointeur, pas de   ┌──────────────────────────┐ │  │
      │  QuestionVersion  │◀── FK circulaire ──   │  SourceDocumentVersion   │ │  │
      │   (immuable)      │    résolue via        │       (immuable)         │ │  │
      └───┬──────┬────────┘    use_alter=True)    └──────────────────────────┘ │  │
          │      │ source_document_version_id ───────────────┘                 │  │
          │      │                                                             │  │
          │      │ M:N (question_version_id, asset_id, role)                   │  │
          │      ▼                                                             │  │
          │  ┌───────────────┐        ┌───────┐                                │  │
          │  │ QuestionAsset │───────▶│ Asset │                                │  │
          │  └───────────────┘        └───────┘                                │  │
          │                                                                    │  │
          │ M:N (question_id, concept_id)                                      │  │
          ▼                                                                    │  │
      ┌─────────┐     ┌─────────┐                                              │  │
      │ Concept │◀────│Question │ (déjà représenté ci-dessus)                  │  │
      └─────────┘     │ Concept │                                              │  │
                       └─────────┘                                             │  │
                                                                                │  │
┌──────┐   1:N   ┌──────────────────────┐  1:N  ┌────────────────┐  1:1  ┌─────────────┐
│ User │────────▶│ QuestionnaireSession │──────▶│ SessionQuestion│──────▶│SessionAnswer│
└──┬───┘         │ (mode, module, statut)│      │ (position,     │       │(answer_json,│
   │             └──────────┬───────────┘      │  question_     │       │ correction) │
   │                        │ module_id ────────┤  version_id,   │       └─────────────┘
   │                        └───────────────────▶  points_max)   │
   │                                             └────────────────┘
   │
   ├──1:N──▶ UserQuestionHistory (user_id, question_id, question_version_id, session_id)
   ├──1:N──▶ UserModuleRating (user_id, module_id, rating)
   ├──1:N──▶ QuestionFeedback (user_id, question_id, feedback_type)
   └──1:N──▶ AIUsage (user_id, period_key, provider, model)

Module ──1:1──▶ ModuleGenerationConfig (generation_status)
```

---

# 3. Responsabilité de chaque table

| Table | Rôle |
|---|---|
| `v1_users` | Un compte = un utilisateur V1. Rôle (student/teacher/admin/author) et plan (free/premium/internal). Pas d'authentification (mot de passe, session de connexion) — ticket #39. |
| `v1_questions` | Identité permanente d'une question : jamais de contenu directement, uniquement métadonnées (module, statut, difficulté déclarée/empirique, source, pointeur vers la version courante). |
| `v1_question_versions` | Contenu concret et **immuable** d'une question à un instant donné. Une édition = une nouvelle ligne, jamais une modification en place. |
| `v1_concepts` | Notion/compétence transversale, non spécialisée par matière (« RAM », « argumentation »…). |
| `v1_question_concepts` | Association M:N Question ↔ Concept. |
| `v1_source_documents` | Identité permanente d'un document source partagé (compréhension à la lecture, Français). |
| `v1_source_document_versions` | Contenu immuable d'un document source à un instant donné ; plusieurs `QuestionVersion` peuvent pointer vers la même ligne. |
| `v1_assets` | Ressource réutilisable (image, SVG, graphique, formule, document, futur audio/vidéo), jamais supprimée ni modifiée en place. |
| `v1_question_assets` | Association Asset ↔ **QuestionVersion** (voir § 9, choix documenté). |
| `v1_questionnaire_sessions` | Session de questionnaire persistante et reprenable ; mode, module, difficulté demandée, statut, score. |
| `v1_session_questions` | Snapshot exact de ce qui a été servi à une position donnée d'une session — référence une `QuestionVersion` précise, jamais juste une `Question`. |
| `v1_session_answers` | Réponse autosauvegardée (une par `SessionQuestion`), JSON générique et versionné, statut/résultat de correction. |
| `v1_user_question_history` | Index dédié « cet utilisateur a-t-il déjà vu cette question/version ? », mis à jour en place plutôt que recalculé par scan. |
| `v1_user_module_ratings` | Rating utilisateur **par module** (jamais global). |
| `v1_question_feedback` | Signalement utilisateur sur une question (trop facile/dure, ambiguë, incorrecte…). |
| `v1_ai_usage` | Compteurs d'usage IA par utilisateur et par période (mensuelle) — pas de paiement réel. |
| `v1_module_generation_configs` | Interrupteur ACTIVE/PAUSED de génération IA par module (#43/#46). |

---

# 4. Relations avec le socle existant

`Question.module_id`, `SourceDocument.module_id`, `QuestionnaireSession.module_id`,
`UserModuleRating.module_id` et `ModuleGenerationConfig.module_id` référencent tous
directement `app.models.Module` (table `modules`, déjà existante). Aucune hiérarchie
matière/module n'est dupliquée — voir § 9 pour la discussion du choix de granularité
(Module plutôt que UAA).

Aucune table V1 ne référence `LessonBlock` : le contenu éditorial (cours, exercices
`editorial_exercise` déjà publiés) et la banque de questions V1 sont deux systèmes
distincts qui coexistent, exactement comme le contrat questionnaire du ticket #23
coexiste avec le contrat à exercice unique du ticket #10 (voir
`docs/ai_exercise_engine.md`).

---

# 5. Règles d'immutabilité / versionnement

Principe transversal : **aucune ligne de `Question`, `QuestionVersion`,
`SourceDocument`, `SourceDocumentVersion`, `Asset`, `User` ou
`QuestionnaireSession` n'est jamais supprimée** une fois créée. Un contenu devenu
invalide change de `status` (`ARCHIVED`/`OBSOLETE`/`INVALID`/`FLAGGED`/
`REVIEW_NEEDED`), il n'est jamais retiré de la base.

- **`QuestionVersion`** : écrite une fois, jamais modifiée après création. Toute édition
  passe par `add_question_version()` (`app/v1/models.py`), qui insère une nouvelle ligne
  et déplace `Question.current_version_id` — jamais un `UPDATE` sur une ligne existante.
- **`SourceDocumentVersion`** : même principe, via `add_source_document_version()`.
- **`SessionQuestion.question_version_id`** référence toujours une `QuestionVersion`
  précise (jamais la Question elle-même) : une session reste donc exacte pour toujours,
  même si la question a depuis une version plus récente (voir test
  `test_old_session_stays_linked_to_old_version_after_new_version_created`).
- **`QuestionnaireSession.is_locked()`** : une session `COMPLETED` ou `ABANDONED` est
  considérée immuable — l'application effective (refuser une écriture) revient au
  service d'autosave du ticket #42 ; ce ticket expose seulement la condition.
- **Cascades** : jamais de suppression en cascade sur `Question`/`QuestionVersion`/
  `Asset`/`SourceDocument`/`SourceDocumentVersion`/`User` (aucune route ne les supprime
  d'ailleurs). `QuestionnaireSession → SessionQuestion → SessionAnswer` utilise
  `cascade="all, delete-orphan"` côté ORM (ces lignes n'ont pas de sens hors de leur
  session, même principe que `UAA → LessonBlock` déjà établi dans `app/models.py|) —
  mais aucune route de suppression de session n'est construite par ce ticket : cette
  cascade reste une plomberie défensive, jamais exercée en pratique pour l'instant.

---

# 6. JSON vs SQL

- **SQL** (colonnes typées, FK, contraintes) pour tout ce qui est **relation métier** ou
  **interrogeable en base** : qui a répondu à quoi, quand, avec quel score, quel
  statut, quel module, quelle position dans une session.
- **JSON** (colonne `JSON`, portable SQLite → PostgreSQL `JSON`/`JSONB`) pour tout ce qui
  est **spécifique au type de question** et non uniformément interrogeable :
  `QuestionVersion.content_json` (prompt, options, réponse(s) correcte(s)...),
  `SessionAnswer.answer_json` (texte, nombre, indices de choix, permutation, appariement,
  futures réponses visuelles), `SessionAnswer.feedback_json`, `Asset.metadata_json`,
  `QuestionnaireSession.parameters_json`.

Chaque champ JSON versionné porte son propre `schema_version` (`QuestionVersion.
schema_version`, `SessionAnswer.answer_schema_version`) : le schéma exact par type de
question est délibérément **repoussé au ticket #40** — `content_json` n'est pas contraint
par un schéma JSON strict au niveau base, seulement documenté comme suivant, pour
`schema_version=1`, la forme déjà établie par `app.ai.schemas.QuestionnaireQuestion`
(ticket #23) : `question_type` reste un texte libre indexé, référençant le même
vocabulaire (`app.ai.schemas.QUESTION_TYPES`) plutôt qu'un second vocabulaire.

---

# 7. Stratégie assets

Un `Asset` est une ressource indépendante (image, SVG, graphique, formule, document,
futur audio/vidéo), avec sa provenance (`source_type` : manual/ai_generated/official/
external), sa licence et ses métadonnées (`metadata_json`). Il n'est jamais dupliqué ni
recréé pour chaque question qui l'utilise : `QuestionAsset` est une table d'association
pure (voir § 9 pour le choix de la scoper à `QuestionVersion`). Un asset n'est jamais
supprimé en cascade quand une question qui le référence est archivée — le cycle de vie
d'un `Asset` est géré par son propre `status`, indépendamment des questions qui l'ont
utilisé un jour.

---

# 8. Stratégie SourceDocument (Français)

Un texte source (article, extrait littéraire...) est modélisé en identité +
version, exactement comme une `Question` : `SourceDocument` (permanent) et
`SourceDocumentVersion` (immuable, une ligne par révision). Plusieurs `QuestionVersion`,
y compris de `Question` différentes, peuvent référencer la même
`SourceDocumentVersion` (`QuestionVersion.source_document_version_id`, nullable — vide
pour toute question qui n'a pas de support documentaire, la majorité en Informatique).

`SourceDocumentVersion.content_text` porte le texte long aujourd'hui ; `asset_id`
(nullable) permet, sans nouvelle table, qu'une version future d'un document soit un
fichier (PDF, scan) plutôt qu'un texte brut — anticipé, non construit ici.

Une session (`SessionQuestion.source_document_version_id`, nullable) peut capturer quelle
version du document a été montrée à l'utilisateur, garantissant qu'une relecture
ultérieure affiche exactement le même texte même si le document a depuis une nouvelle
révision. L'UX Français elle-même (affichage, découpage en questions liées à un même
texte) est repoussée au ticket #47.

---

# 9. Points ambigus du ticket — choix effectués et justification

Le ticket #38 laisse volontairement plusieurs choix à l'appréciation de l'implémentation
(« si un point important est ambigu, privilégie le modèle le plus générique et documente
le choix ») :

1. **`Role`/`Plan` : enum Python, pas des tables séparées.** Le ticket cite ces deux noms
   comme des « modèles », ce qui pourrait suggérer des tables de référence. Choisi malgré
   tout comme enum (`UserRole`, `UserPlan`, colonnes `Enum(...)`) pour rester cohérent
   avec la convention déjà établie par ce projet (`BlockType`, `BlockSpace` dans
   `app/models.py`) plutôt que d'introduire un mécanisme de lookup-table inédit pour un
   ensemble de valeurs fixé par le code applicatif (les futurs contrôles d'autorisation
   #39 testeront `user.role == UserRole.TEACHER`, pas une jointure). Migration triviale
   vers une table dédiée le jour où un besoin réel de rôles/plans dynamiques (définis par
   un enseignant, par exemple) apparaît.

2. **Granularité de `Question.module_id` : `Module`, pas `UAA`.** Le registre pédagogique
   IA existant (`app.ai.context.PEDAGOGICAL_CONTEXTS`) est borné au niveau UAA (ex.
   `"ampcr-mc01"`), ce qui aurait pu suggérer la même granularité pour la banque V1.
   Choisi au niveau `Module` car (a) le ticket #38 lui-même écrit explicitement « rating
   utilisateur **par module** », jamais par UAA ; (b) une banque de questions générées en
   volume est conceptuellement plus proche d'un « module » entier (ex. AMPCR) que d'un
   mini-cours isolé, cohérent avec la priorité produit « 1. Informatique AMPCR ; 2.
   Français CESS Professionnel » énoncée au niveau matière/module, pas UAA par UAA.

3. **`QuestionAsset` scopé à `QuestionVersion`, pas à `Question`.** Le ticket nomme
   littéralement la table `QuestionAsset`. Implémenté avec une colonne
   `question_version_id` (pas `question_id`) : un asset utilisé par une question peut
   changer d'une version à l'autre (schéma remplacé lors d'une correction éditoriale) — le
   lier à la `Question` (identité) changerait silencieusement ce qu'une ancienne session
   affiche en relecture, ce que le ticket interdit explicitement pour le contenu
   (« aucune modification rétroactive des sessions historiques »), et qui doit s'appliquer
   de la même façon aux illustrations d'une question qu'à son texte.

4. **`QuestionRating` : champs sur `Question`, pas une table séparée.** Le ticket propose
   explicitement l'alternative (« `QuestionRating` ou champs appropriés »). Implémenté
   comme `Question.difficulty_rating` + `Question.rating_sample_size`, suffisant pour «
   modèle + contraintes + valeurs par défaut seulement » sans table dédiée à ce stade —
   une table séparée n'apporterait de valeur que si un historique de rating dans le temps
   devenait nécessaire, ce que le ticket ne demande pas.

5. **`SessionAnswer` : une ligne par `SessionQuestion` (mise à jour en place), pas un
   journal de tentatives.** « Autosave à chaque réponse » est interprété comme un
   upsert continu plutôt qu'un historique de tentatives multiples — le ticket ne demande
   nulle part de conserver plusieurs tentatives par question dans une même session.

6. **`AIUsage.period_key` : chaîne `"AAAA-MM"` (mensuel), pas une plage de dates.**
   Choix le plus simple satisfaisant « usage par période » sans construire une notion de
   période configurable non demandée par le ticket.

---

# 10. Compatibilité future PostgreSQL

Choix de types faits explicitement en vue d'une migration future (SQLite aujourd'hui,
PostgreSQL possible plus tard) :

- `JSON` (type SQLAlchemy générique) plutôt qu'un `Text` sérialisé à la main : mappé
  nativement vers `JSON`/`JSONB` côté PostgreSQL, vers `TEXT` (sérialisé/désérialisé par
  SQLAlchemy) côté SQLite — aucun changement de code applicatif requis au moment de la
  migration.
- `DateTime(timezone=True)` avec des valeurs Python `datetime.now(UTC)` (jamais de
  fonction SQL type `CURRENT_TIMESTAMP` propre à un moteur) : portable tel quel.
- Contraintes (`UniqueConstraint`, `ForeignKey`, index) exprimées au niveau SQLAlchemy,
  jamais en SQL brut spécifique à SQLite.
- `ForeignKey(..., use_alter=True, name=...)` sur les deux références circulaires
  (`Question.current_version_id`, `SourceDocument.current_version_id`) : SQLite n'a pas
  besoin d'un ALTER réel (pas d'ordonnancement de création strict, `checkfirst` suffit),
  mais PostgreSQL en aurait besoin pour créer les tables dans un ordre valide — la
  contrainte est déjà nommée et prête pour cette bascule.
- Aucun SQL spécifique à SQLite (`PRAGMA`, fonctions `sqlite_*`) dans `app/v1/models.py`.

Non traité par ce ticket (au moment de la bascule effective, pas avant) : script de
migration de données SQLite → PostgreSQL, choix d'un outil de migration de schéma
(Alembic ou équivalent — le projet n'en utilise aucun aujourd'hui, voir
`app/database.py::ensure_schema_migrations`).

---

# 11. Ce qui n'est pas touché

- `app/models.py` (Subject/Module/UAA/LessonBlock/BlockType/BlockSpace) : aucune
  modification.
- Les routes publiques existantes (`app/main.py`, `app/practice.py`) : aucune nouvelle
  route ajoutée par ce ticket, seul l'enregistrement des tables (`from app.v1 import
  models`) a été ajouté à `app/main.py`/`app/seed.py` pour que `Base.metadata.
  create_all()` les crée.
- MC01/MC02/MC03, `app.editorial_exercise`, `app.quiz`, `app.ai/*` : inchangés,
  continuent de fonctionner exactement comme avant.
- Aucune donnée existante de `jury_central.db` n'est lue, modifiée ou migrée par ce
  ticket (voir le rapport de ticket, § Migrations, pour la preuve que la création des
  17 nouvelles tables est purement additive sur une base synthétique reproduisant un
  état pré-#38).

---

# 12. Ce qui est volontairement repoussé aux tickets suivants

- Authentification complète (mot de passe, connexion, inscription) : #39.
- Schémas stricts par type de question (`content_json` détaillé par type) : #40.
- Sélection/algorithme de banque (exclusion des questions déjà vues, complétion par
  génération IA) : #41.
- API d'autosave (écriture de `SessionAnswer`, verrouillage effectif d'une session
  `COMPLETED`) : #42.
- Génération IA en batch : #43.
- Correction (locale + un seul appel IA batch pour les réponses sémantiques) : #44.
- Algorithme de rating (mise à jour de `UserModuleRating.rating`/
  `Question.difficulty_rating`) : #45.
- Interface d'administration V1 : #46.
- UX Français (découpage d'un texte en questions liées) : #47.
- Reconnaissance d'image : #48.

---

# 13. Pourquoi un module séparé (`app/v1/models.py`)

Toutes les classes V1 utilisent le même `Base` (`app.database.Base`) que le socle
éditorial existant — une seule base de métadonnées, un seul fichier SQLite, une seule
transaction possible entre les deux mondes si nécessaire plus tard (ex. lier une future
`Question` V1 à un `LessonBlock` existant). Le code est cependant séparé dans
`app/v1/models.py` (nouveau package `app/v1/`) plutôt qu'ajouté à `app/models.py` :

- réduit le risque de toucher accidentellement au socle éditorial existant pendant un
  ticket déjà volumineux (« ne pas casser MC01/MC02/MC03 ») ;
- suit la même logique de package déjà appliquée à `app/ai/` (sous-système cohérent,
  regroupé) plutôt que de faire grossir un seul fichier plat de ~20 classes
  supplémentaires ;
- laisse `app/models.py` entièrement stable, ce qui simplifie la revue du diff de ce
  ticket.

`app/v1/models.py` est importé (pour son seul effet d'enregistrement des tables auprès de
`Base.metadata`) par `app/main.py` et `app/seed.py`, aux côtés de `from app import
models`.
