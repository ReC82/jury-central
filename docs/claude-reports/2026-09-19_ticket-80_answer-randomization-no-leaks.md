# Ticket #80 — Position des bonnes réponses / fuite de réponse

**Branche** : `feature/80-answer-randomization-no-leaks`, base `develop` (486f35c, PR #81
mergée). Aucun merge, aucun déploiement effectué.

---

# Problème 1 — la bonne réponse apparaissait trop souvent en première position

## Cause racine

`MultipleChoiceContent.shuffle: bool = True` (`app/v1/question_types.py`) existe depuis
le ticket #40, exposé au client via `_mc_public`/`public_payload` (`"shuffle":
content.shuffle`) — mais **rien, nulle part dans le code, n'appliquait réellement ce
mélange**. Recherche exhaustive : aucune occurrence de shuffle des options en JS
(`app/static/js/*.js`), en template (`v1_session_question.html`), ni côté serveur. Les
`options` étaient persistées dans `content_json` exactement dans l'ordre fourni par le
générateur IA ou l'auteur éditorial — un générateur (ou un·e auteur·ice) qui place, par
habitude, la bonne réponse en premier produit alors une bonne réponse en position 0 de
façon systématique.

`correct_option_ids` référence déjà `option_id` (jamais une position) — la « vérité »
n'était donc jamais le problème, uniquement l'ABSENCE de mélange réel de l'affichage.

## Fix

Nouvelle fonction `shuffle_multiple_choice_options` (`app/v1/ai_bridge.py`), même
principe que `shuffle_ordering_items` (#69) : mélange physique de la liste `options`,
`option_id` toujours attaché à son `label`. Appliquée aux **deux** points où
`options`/`content_json` sont construits avant persistance (mêmes deux points d'entrée
que `shuffle_ordering_items`, pour ne rien manquer) :

- `questionnaire_question_to_content` (`app/v1/ai_bridge.py`) — conversion du contenu
  généré par IA.
- `_editorial_item_to_v1_content` (`app/v1/bank.py`) — import du contenu éditorial legacy
  (MC01).

Contrairement à `shuffle_ordering_items`, aucune garantie « jamais dans l'ordre
d'origine » n'est nécessaire : un QCM dont le tirage laisse par hasard la bonne réponse en
position 0 n'est pas un problème en soi (contrairement à un `ordering` déjà trié, qui
rend l'exercice trivial) — seule la répétition SYSTÉMATIQUE est le bug. Un simple
`random.shuffle` suffit, vérifié statistiquement (~25 % par position sur 400 tirages,
seed fixée).

---

# Problème 2 — une classification donnait la réponse dans l'énoncé

## Cause

Aucun contrôle n'existait pour détecter qu'un élément à classer contient littéralement le
terme qui identifie sa propre catégorie. Exemple exact du ticket : catégories « HDD
mécanique »/« SSD SATA »/« SSD NVMe », élément « Le support flash est identifié comme
NVMe sur un emplacement M.2 compatible » — le mot « NVMe » suffit à lui seul à répondre,
aucun raisonnement requis.

## Fix

Nouveau contrôle `_check_classification_reveals_answer_label`
(`app/v1/quality_validation.py`, même registre que les contrôles qualité #69) :

1. `_distinguishing_words_by_category` calcule, pour chaque catégorie, les mots
   significatifs qui n'apparaissent dans **aucune autre** catégorie de la liste — jamais
   un mot générique partagé (ex. « SSD », présent dans 2 des 3 catégories de l'exemple,
   ne compte jamais seul).
2. Pour chaque élément, si TOUS les mots distinctifs de sa catégorie correcte apparaissent
   tels quels dans son texte, la question est rejetée.

Vérifié sur l'exemple exact du ticket (rejeté) et sur les 3 reformulations suggérées
(acceptées, aucun mot distinctif littéral). Testé explicitement contre les faux positifs :
un mot partagé entre catégories (« SSD ») n'importe jamais qu'il soit présent dans
l'élément.

Portée : uniquement `classification` (comme demandé) — ne touche pas
`_check_weak_classification_phrasing` (#69, formulation molle) ni les autres contrôles
existants.

---

# Tests

Nouveau fichier `tests/test_ticket80_answer_randomization_no_leaks.py` (12 tests, seeds
déterministes, aucun appel OpenAI réel) :

1. `shuffle_multiple_choice_options` : préserve l'association option_id↔label ; change
   réellement l'ordre (seed fixée) ; no-op sous 2 options ; distribution statistique de la
   position de la bonne réponse (400 tirages, jamais 100 % en position 0, chaque position
   ≥ 10 %).
2. Vérité liée à `option_id` : `correct_option_ids` jamais exposé publiquement, reste
   cohérent après mélange ; conversion IA (`questionnaire_question_to_content`) et import
   éditorial (`_editorial_item_to_v1_content`, exercé directement — MC01 lui-même ne
   contient actuellement aucun exercice `single_choice`) mélangent bien leurs options.
3. Fuite de réponse : cas exact du ticket rejeté ; 3 reformulations acceptées ; mot
   partagé entre catégories ne déclenche jamais de faux positif ; contrôle ignoré pour
   les autres types ; `persist_generated_questions` rejette bien une classification qui
   fuite de bout en bout (jamais persistée).

Suite complète du dépôt : **1106 passed**. Ruff : **0 nouvelle erreur** (36
pré-existantes, hors fichiers touchés, confirmé par comparaison directe avec `develop`).

---

# Fichiers modifiés

- `app/v1/ai_bridge.py` — `shuffle_multiple_choice_options`, appliquée dans
  `questionnaire_question_to_content`.
- `app/v1/bank.py` — même mélange appliqué dans `_editorial_item_to_v1_content`.
- `app/v1/quality_validation.py` — `_distinguishing_words_by_category`,
  `_check_classification_reveals_answer_label`, câblée dans
  `validate_question_quality_rules`.
- `tests/test_ticket80_answer_randomization_no_leaks.py` — nouveau, 12 tests.
