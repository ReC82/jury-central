# Ticket #64 — Qualité examen AMPCR : anti-répétition, variantes, scénarios, réponses sémantiques

**Date** : 2026-09-18
**Branche** : `feature/64-ampcr-question-quality`

---

## 1. Contexte

Validation staging réelle du ticket #62 (session MC17 complète, corrigée par un vrai
fournisseur OpenAI) : le moteur de correction hybride fonctionne, mais l'expérience
d'examen elle-même montre des défauts de qualité pédagogique constatés en usage réel :
questions identiques déjà vues en entraînement resservies en examen, classifications
triviales à 1-parmi-2 répétitives, diagnostics trop vagues, ordering parfois ambigu,
réponses courtes sémantiquement correctes notées fausses par une comparaison textuelle
stricte, et trop de répétition sur les mêmes micro-notions.

Ce ticket ne touche pas au moteur de session lui-même (#55/#57/#58/#62, inchangé dans son
architecture) ni au Français (`feature/47-francais-v1`, non rebasé — construit depuis
`develop` seul, comme pour #62).

---

## 2. Priorité 1 — Anti-répétition

`app.v1.bank.select_bank_questions`/`select_transversal_bank_questions` acceptent un
nouveau paramètre `only_unseen: bool = False` :

- `only_unseen=True` : ne renvoie QUE des questions jamais vues par l'utilisateur (ni par
  identité exacte, ni par quasi-doublon — voir § 2 ci-dessous), quitte à retourner moins
  que `limit`.
- `only_unseen=False` (défaut, comportement historique inchangé) : repli intégré sur les
  questions déjà vues si le nombre de jamais-vues est insuffisant.

`app.v1.session_service.start_session`/`_start_mc38_transversal_session` appellent
désormais la sélection banque INITIALE avec `only_unseen=True`, puis, seulement si le
compte est encore insuffisant, tentent une génération IA ciblée, et seulement en tout
dernier recours retombent sur `only_unseen=False` (repli explicite déjà existant, ticket
#55). La séquence « générer avant de recycler » est donc désormais une vraie séquence
observable (testée via `fake.questionnaire_calls`), pas un mélange aléatoire comme avant
(où la sélection initiale mélangeait déjà vues/jamais vues dans le pool oversample dès que
le nombre de jamais-vues était inférieur à `limit = count * 3`, même quand il restait
largement suffisant pour couvrir `count`).

`UserQuestionHistory` alimente déjà l'exclusion pour **practice ET exam** (aucune
distinction de mode dans son schéma, ticket #38 § J) — non-régression confirmée.

---

## 3. Priorité 2 — Déduplication (`app.v1.dedup`, nouveau module)

Signature structurelle locale, sans appel IA :

- `question_signature(question_type, content_json)` : type + libellés
  structurels **triés** (options/éléments/catégories/items — un réordonnancement seul ne
  change jamais la signature) + ensemble de mots significatifs normalisés de l'énoncé.
- `is_near_duplicate(a, b)` : même type, ET (recouvrement lexical de l'énoncé ≥ 72 %, OU
  structure triée strictement identique avec au moins un peu de vocabulaire commun — ce
  second garde-fou évite qu'une collision fortuite d'options génériques entre deux
  questions sans rapport soit prise pour un doublon).

Utilisé à deux niveaux :

1. **À la sélection** (`select_bank_questions`/`select_transversal_bank_questions`) : une
   question jamais vue PAR SON PROPRE ID mais quasi-identique à une question déjà vue
   (options réordonnées, reformulation superficielle par une génération IA ultérieure)
   tombe désormais côté « déjà vue », pas « nouvelle ».
2. **À la persistance** (`persist_generated_questions`) : une question générée qui serait
   un quasi-doublon d'une question ACTIVE déjà en banque (même module/mini-cours) — ou
   d'une autre question DU MÊME LOT généré en un seul appel — n'est jamais persistée.

---

## 4. Priorité 3 — Variantes réelles

`QuestionnaireRequest` (contrat #23) gagne un champ optionnel `avoid_prompts: tuple[str,
...] = ()` (vide par défaut, n'affecte aucun appelant existant). `app.v1.bank.
recent_seen_prompts()` (nouveau) récupère les énoncés les plus récemment vus par
l'utilisateur (practice ET exam), scopés module/mini-cours. `start_session`/
`_start_mc38_transversal_session` le transmettent à chaque génération de complément.
`app.ai.prompts.build_generate_questionnaire_messages` inclut ces énoncés dans le prompt
avec une consigne explicite de ne jamais les reproduire à l'identique ni sous une forme à
peine reformulée/réordonnée.

Garde mécanique complémentaire (puisque la créativité de l'IA n'est pas testable en
pytest) : la déduplication à la persistance (§ 2) rejette toute « fausse variante »
produite malgré la consigne — un test dédié vérifie qu'une variante réellement différente
(autre notion) est acceptée alors qu'un quasi-clone est rejeté.

---

## 5. Priorité 4 — Questions contextualisées

`GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT` (`app.ai.prompts`) porte désormais une section
« QUALITÉ » explicite, avec l'exemple exact du ticket (mauvaise formulation vague vs. mise
en situation concrète avec poste/symptôme/valeur mesurée — 8.8.8.8/intranet.local).
Prompt-engineering uniquement (non mécaniquement vérifiable côté serveur pour du contenu
généré par un vrai fournisseur) — testé par assertion de présence dans le prompt système,
même style que les instructions de sévérité du ticket #62.

---

## 6. Priorité 5 — Ordering

Même section QUALITÉ : consigne explicite d'indiquer TOUJOURS, dans l'énoncé lui-même, le
point de départ, le point d'arrivée et le sens du classement demandé — jamais une double
consigne ambiguë.

---

## 7. Priorité 6 — QCM / Classification

Même section QUALITÉ : consigne d'éviter les classifications triviales à 1-parmi-2 quand
une question plus riche est possible, de préférer 3 à 6 propositions plausibles avec des
distracteurs crédibles et un contexte concret — un choix à 2 options reste autorisé s'il
est réellement justifié (ex. vrai/faux binaire par nature).

---

## 8. Priorité 7 — Short answer sémantique (`app.v1.hybrid_correction`)

Exception délibérée et ciblée à `short_answer`/`vocabulary` (`CONDITIONALLY_LOCAL_QUESTION_
TYPES`, contrat #23, inchangé) : une réponse jugée INCORRECTE par la comparaison textuelle
locale (`text_answer_matches`) n'est plus verrouillée comme les autres types déterministes.
Elle est envoyée dans le MÊME lot IA batch avec une grille de ré-évaluation sémantique
explicite (« cette comparaison stricte a pu produire un faux négatif — évalue le sens
réel ») et son score, cette fois, est validé/borné comme une question sémantique ordinaire
(`validate_semantic_correction`, [0, points_max]) — potentiellement révisé à la hausse.

**Ordering/classification/QCM/numeric/fill_blank restent strictement inchangés** : score
toujours verrouillé localement, l'IA ne peut fournir qu'une explication textuelle (voir
tests ticket #62, tous encore verts). Une réponse locale déjà CORRECTE en short_answer/
vocabulary n'est, comme avant, jamais envoyée à l'IA (aucun coût inutile). La sévérité 1-5
(#62) s'applique normalement à cette ré-évaluation, comme à toute question sémantique.

Testé avec l'exemple exact du ticket (« l'écart entre deux débuts de sous-réseaux » vs.
« le nombre entre le début d'un sous-réseau et le début du suivant ») et un test combiné
vérifiant que, dans le MÊME appel batch, `ordering` reste verrouillé pendant que
`short_answer` est réévalué.

---

## 9. Priorité 8 — Examen blanc 20Q

- **Diversité mini-cours** : `_category_balanced_oversample` (MC38, #58) généralisée en
  `_diversity_capped_oversample(pool, target_count, key_fn)` — même logique, clé
  paramétrable. Nouvelle fonction `_uaa_balanced_oversample`, appliquée à l'examen blanc
  global AMPCR (`uaa_id=None`) : plafonne la représentation d'un seul mini-cours dans le
  pool transmis à `compose_selection`, best-effort (repli documenté si la banque est trop
  pauvre pour l'atteindre sans redescendre en dessous de `target_count`, comme pour MC38).
- **Micro-notions répétées** : nouvelle `_limit_near_duplicate_clusters(pool, max_per_
  cluster=2)`, réutilise `app.v1.dedup` — plafonne à 2 le nombre de questions quasi-
  identiques dans un même pool de composition.
- **Diversité de types** : déjà assurée par `compose_selection` (round-robin par type,
  inchangé).
- **Limite assumée** : « limiter les définitions pures / assurer diagnostics-procédures-
  calculs-commandes-matériel-système-réseau-sécurité » reste une consigne de
  prompt-engineering (section QUALITÉ, § 5 ci-dessus) — aucune taxonomie thématique
  n'existe dans le schéma actuel (`question_type` est générique : QCM/ordering/etc., pas
  « commande »/« matériel »/« sécurité ») ; créer une telle taxonomie est hors périmètre
  de ce ticket (changement de schéma non demandé), documenté ici plutôt que bricolé.

---

## 10. Fichiers modifiés/créés

- **`app/v1/dedup.py`** (nouveau) : signature structurelle, `is_near_duplicate`,
  `find_near_duplicate`.
- **`app/v1/bank.py`** : `only_unseen` sur les deux fonctions de sélection,
  `_seen_signatures`/`_split_unseen_and_seen` (exclusion par quasi-doublon d'une vue),
  `recent_seen_prompts` (nouveau), dédup à la persistance dans
  `persist_generated_questions`.
- **`app/v1/session_service.py`** : `only_unseen=True` sur la sélection initiale
  (`start_session`/`_start_mc38_transversal_session`), `avoid_prompts` transmis à la
  génération, `_diversity_capped_oversample` (généralisation), `_uaa_balanced_oversample`
  (nouveau), `_limit_near_duplicate_clusters` (nouveau).
- **`app/v1/hybrid_correction.py`** : `RESCORABLE_LOCAL_TYPES`, `_semantic_rescoring_
  rubric`, groupe `rescorable_questions` dans `correct_session_hybrid` (§ 8 ci-dessus).
- **`app/ai/schemas.py`** : `QuestionnaireRequest.avoid_prompts` (optionnel, défaut vide).
- **`app/ai/prompts.py`** : section QUALITÉ dans `GENERATE_QUESTIONNAIRE_SYSTEM_PROMPT`,
  `_avoid_prompts_block` + intégration dans `build_generate_questionnaire_messages`.
- **`tests/test_ticket64_ampcr_question_quality.py`** (nouveau, 32 tests) : dedup unitaire,
  sélection banque (`only_unseen`, quasi-doublon d'une vue), persistance dédupliquée,
  `recent_seen_prompts`, ré-évaluation sémantique short_answer/vocabulary (verrou ordering
  contrasté), diversité UAA/quasi-doublons de composition, HTTP bout en bout (examen
  global multi-MC, séquence génération-avant-repli, non-régression MC01/MC17).

---

## 11. Tests

`pytest -q` (suite complète) : **953 passed** (921 baseline ticket #62 + 32 nouveaux),
`0 failed`. Aucun appel OpenAI réel (`FakeAIProvider` partout, `OPENAI_API_KEY=""` forcé
par `tests/conftest.py`, inchangé). Ruff : **36 erreurs, 0 nouvelle** (baseline identique
à celle documentée au ticket #62). `git diff --check` : propre.

Non-régression explicite : toute la suite ticket #62 (hybrid correction, sévérité 1-5,
historique, impression, export) repasse sans modification, y compris avec le nouveau
groupe `rescorable_questions` ajouté au même appel batch.

---

## 12. Limites assumées

- **Qualité pédagogique réelle des variantes/mises en situation générées** non vérifiable
  en pytest (`FakeAIProvider` déterministe) — seule la PLOMBERIE (avoid_prompts transmis,
  dédup mécanique au rejet des quasi-clones, contenu du prompt système) est testée
  automatiquement ; la qualité réelle nécessite une validation manuelle sur staging avec
  un vrai fournisseur, comme pour le reste du moteur IA (déjà noté au ticket #62).
- **Taxonomie thématique absente** (§ 9) : la diversité « diagnostics/procédures/calculs/
  commandes/matériel/système/réseau/sécurité » reste une consigne IA, non mécaniquement
  vérifiable côté serveur sans changement de schéma — hors périmètre.
- **Quasi-doublons pré-existants dans la banque déjà seedée avant ce ticket** : la
  déduplication à la persistance protège les FUTURES générations ; elle ne réécrit ni ne
  purge rétroactivement des questions déjà en banque (aucune opération destructive sur la
  banque existante, conformément à la consigne de ne jamais toucher aux données déjà
  produites sans instruction explicite). L'exclusion par quasi-doublon d'une question déjà
  vue (§ 2), elle, s'applique immédiatement à toute sélection future, y compris sur la
  banque existante.
- **Seuils de similarité (Jaccard 72 %, recouvrement structurel minimal 15 %)** calibrés
  empiriquement sur les exemples du ticket et des cas adverses ajoutés en test — un
  réglage fin en usage réel (faux positifs/négatifs observés sur staging) resterait à
  ajuster si nécessaire, pas figé dans le contrat public.

---

## Statut

Implémentation, tests et documentation terminés. `pytest -q` (suite complète) : 953
passed. Ruff : 36 erreurs, 0 nouvelle. `git diff --check` : propre. Aucun appel OpenAI
réel. Aucune modification de `jury_central.db`. Prêt pour commit/push. **Aucun merge,
aucun déploiement.** Le Français (`feature/47-francais-v1`) et #45/#46/#48 n'ont pas été
touchés.
