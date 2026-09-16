# Ticket #17 — Interactivité : socle générique des exercices éditoriaux

**Date** : 2026-09-16
**Branche** : `feature/17-editorial-exercise-socle`
**Ticket GitHub** : #17 « Interactivité — socle générique des exercices éditoriaux »
**Fait suite à** : `docs/claude-reports/2026-09-16_audit_interactivite.md` (sections C, D, E)

---

## 1. Résumé

Le ticket construit le **socle** générique des exercices éditoriaux interactifs
(`editorial_exercise`), réutilisable dans toutes les matières, sur le patron déjà en place
pour `value_table`/`quiz`/`ai_exercise` : bloc → configuration JSON → route de
vérification serveur → widget AJAX sans rechargement. Première tranche de types :
`single_choice`, `true_false`, `short_answer`, à correction locale déterministe
uniquement.

**MC01 n'a reçu aucune migration réelle** dans ce ticket : les 12 exercices existants ont
été passés en revue un par un (§ 8) et aucun ne peut être honnêtement exprimé avec cette
première tranche de types sans en dénaturer le contenu pédagogique. Conformément à la
consigne explicite du ticket (« ne force pas artificiellement »), ils restent intacts. La
validation visuelle de l'architecture se fait via une route de démonstration admin
(`/admin/editorial-exercise-demo`), sur le même principe que `/admin/value-table-demo`
déjà existant dans le projet — pas via du contenu MC01 réinventé.

Aucun changement de règle pédagogique, aucun nouvel appel IA, aucune régression sur
MC01/MC02/MC03/Mathématiques.

---

## 2. Architecture

```
LessonBlock (type = editorial_exercise)
    content (JSON) : EditorialExerciseBlockConfig
        mode: "practice" | "exam"
        items: [ EditorialExerciseItem ]
                exercise_id, type, prompt, points
                + données privées de correction selon le type
        ↓
    to_public_dict() — jamais la solution
        ↓
    app/main.py::uaa_detail → item["editorial_exercise"] = {verify_url, items_json}
        ↓
    app/templates/uaa_detail.html → <div class="editorial-exercise-block" data-verify-url data-items>
        ↓
    app/static/js/editorial_exercise.js — un composant par type, AJAX
        ↓
    POST /practice/api/editorial/{block_id}/verify {exercise_id, answer}
        ↓
    app/practice.py recharge EditorialExerciseBlockConfig depuis la base (jamais confiée au client)
        ↓
    app/editorial_exercise.py::check_editorial_answer(...)
        ↓
    { exercise_id, correct, correct_answer(_html), explanation(_html) }
```

Même principe de sécurité que les mécanismes existants : le serveur ne fait jamais
confiance au client pour la solution, aucune donnée de correction n'est jamais présente
dans le DOM avant l'appel de vérification.

---

## 3. Fichiers créés/modifiés

Créés :
- `app/editorial_exercise.py` — modèle, validation, sérialisation, correction.
- `app/static/js/editorial_exercise.js` — widget générique (single_choice, true_false, short_answer).
- `app/templates/admin_editorial_exercise_demo.html` — page de démonstration admin.
- `docs/editorial_exercise_engine.md` — documentation technique dédiée.
- `docs/claude-reports/2026-09-16_ticket-17_editorial-exercises.md` — ce rapport.
- `tests/test_editorial_exercise.py`, `tests/test_practice_editorial_routes.py`,
  `tests/test_ticket17_no_regression.py`.

Modifiés :
- `app/models.py` — ajout `BlockType.EDITORIAL_EXERCISE`.
- `app/answer_checking.py` — ajout `normalize_text`/`text_answer_matches`.
- `app/practice.py` — route `POST /api/editorial/{block_id}/verify`.
- `app/main.py` — rendu du nouveau type de bloc dans `uaa_detail`.
- `app/templates/uaa_detail.html` — branche de template correspondante.
- `app/templates/base.html` — inclusion de `editorial_exercise.js`.
- `app/admin.py` — route et config de démonstration
  `/admin/editorial-exercise-demo`(`/verify`).
- `docs/EXERCISE_TYPES.md`, `docs/admin.md`, `docs/current_state.md`, `docs/INDEX.md`,
  `docs/README.md`, `docs/changelog.md`.

**Non modifié** : `app/seed.py` (aucun exercice MC01 migré, voir § 8).

---

## 4. Modèle JSON

```json
{
  "mode": "practice",
  "items": [
    {
      "exercise_id": "demo-single-choice",
      "type": "single_choice",
      "prompt": "Lequel de ces composants est une mémoire volatile ?",
      "points": 1.0,
      "choices": ["Le disque dur (HDD)", "La mémoire vive (RAM)", "Le SSD"],
      "correct_index": 1,
      "explanation": "La RAM perd son contenu à l'extinction du PC ; le HDD et le SSD conservent leurs données hors tension."
    },
    {
      "exercise_id": "demo-short-answer",
      "type": "short_answer",
      "prompt": "Quel sigle anglais désigne la mémoire vive ?",
      "points": 1.0,
      "accepted_answers": ["RAM", "Random Access Memory"],
      "explanation": "RAM = Random Access Memory, la mémoire de travail temporaire et volatile."
    }
  ]
}
```

Représentation **publique** (`to_public_dict()`, réellement envoyée au navigateur avant
correction) pour le premier item ci-dessus :

```json
{
  "exercise_id": "demo-single-choice",
  "type": "single_choice",
  "prompt": "Lequel de ces composants est une mémoire volatile ?",
  "prompt_html": "<p>Lequel de ces composants est une mémoire volatile ?</p>",
  "points": 1.0,
  "choices": ["Le disque dur (HDD)", "La mémoire vive (RAM)", "Le SSD"]
}
```

`correct_index`, `accepted_answers` et `explanation` sont structurellement absents —
vérifié par test unitaire (`tests/test_editorial_exercise.py`) et par test HTTP sur le
HTML réel de `/uaa/{slug}` (`tests/test_practice_editorial_routes.py`).

---

## 5. Endpoints

| Route | Méthode | Payload | Réponse |
|---|---|---|---|
| `/practice/api/editorial/{block_id}/verify` | POST | `{exercise_id, answer}` | `{exercise_id, correct, correct_answer, correct_answer_html, explanation, explanation_html}` |
| `/admin/editorial-exercise-demo` | GET (admin) | — | Page de démonstration (3 exercices fixes) |
| `/admin/editorial-exercise-demo/verify` | POST (admin) | `{exercise_id, answer}` | Même forme que ci-dessus |

Codes d'erreur : `404` si `block_id` introuvable, type de bloc incorrect, bloc non
publié, ou `exercise_id` introuvable dans la configuration — jamais de fuite
d'information sur la raison précise au-delà de « introuvable ».

---

## 6. Sécurité

- Le serveur recharge systématiquement `EditorialExerciseBlockConfig` depuis
  `LessonBlock.content` (jamais depuis une valeur confiée par le client) avant de
  corriger.
- Aucune réponse correcte, liste de réponses acceptées ou explication n'est jamais
  présente dans le HTML/JSON public avant l'appel de vérification — testé explicitement
  au niveau unitaire et au niveau HTTP réel (`/uaa/{slug}` et la page de démo admin).
- Comparaison textuelle sans `eval()` (`app/answer_checking.py::text_answer_matches`,
  extension de la même logique déjà en place pour les réponses numériques).
- Aucun appel réseau, aucun appel IA : correction 100 % locale et déterministe pour cette
  tranche de types.
- `from_json()` tolère un contenu admin mal formé (item invalide silencieusement ignoré)
  sans jamais faire échouer le rendu de la page publique ; la validation stricte a lieu à
  la construction directe (`app/seed.py`, tests), pour détecter les erreurs d'auteur tôt.

---

## 7. Exercices MC01 migrés

**Aucun.** Voir § 8 pour le détail exercice par exercice.

---

## 8. Exercices MC01 non migrés — raison précise

Les 12 exercices existants de MC01 (`app/seed.py::_MC01_EXERCICES_1/2/3`) ont été relus un
par un :

| Exercice | Intitulé | Type requis | Pourquoi pas cette tranche |
|---|---|---|---|
| 1 | Classer matériel/logiciel (5 éléments) | `classification` | Classement multi-éléments dans 2 catégories — pas un choix unique |
| 2 | Classer unité centrale/périphériques (6 éléments) | `classification` | Idem |
| 3 | Expliquer compatibilité CPU/carte mère | `long_answer` | Réponse rédigée ouverte, pas de réponse courte unique |
| 4 | Diagnostiquer absence d'affichage | `long_answer` | Justification écrite multi-parties centrale à l'exercice |
| 5 | Expliquer RAM vs stockage (2 points) | `long_answer` | Réponse rédigée structurée |
| 6 | Expliquer l'ambiguïté « 32 Go » | `long_answer` | Explication argumentée |
| 7 | Expliquer GPU intégré/dédié + VRAM + exemple | `long_answer` | Réponse rédigée composite |
| 8 | Expliquer 750 W + règle de sécurité | `long_answer` | Réponse rédigée composite |
| 9 | Reconstruire l'ordre d'exécution (4 étapes) | `ordering` | Remise en ordre, pas un choix unique |
| 10 | Diagnostiquer un ralentissement (RAM vs disque) | `long_answer` | Diagnostic justifié, pas une réponse courte fermée |
| 11 | Classer périphériques entrée/sortie/mixte (5 éléments) | `classification` | Classement multi-éléments |
| 12 | Vocabulaire FR/EN (4 termes + explication) | `long_answer` | Réponse composite (traduction + explication), pas une réponse courte unique |

**Synthèse** : 8 exercices nécessitent `long_answer` (correction IA, ticket séparé), 3
nécessitent `classification`, 1 nécessite `ordering` — 0 sur 12 ne correspond
honnêtement à `single_choice`, `true_false` ou `short_answer` sans en changer la nature
pédagogique (ex. transformer un exercice de classement en 5 questions vrai/faux
séparées aurait changé le grain de l'activité, pas seulement sa forme technique).

Une démonstration technique du socle (3 exercices fixes, un par type disponible) a été
ajoutée sous `/admin/editorial-exercise-demo` — même principe que le composant
`value_table` avant d'avoir un générateur réel — afin de permettre une validation visuelle
de l'architecture sans attendre les tickets `classification`/`ordering`/`long_answer`.

---

## 9. Tests

| Fichier | Couverture |
|---|---|
| `tests/test_editorial_exercise.py` | Validation de configuration (10 cas d'erreur), sérialisation/désérialisation, tolérance de `from_json` aux items invalides et au mode invalide, absence de fuite dans `to_public_dict()`, correction correcte/incorrecte/id inconnu pour les 3 types, normalisation `short_answer` |
| `tests/test_practice_editorial_routes.py` | Route HTTP bout en bout : réponse correcte/incorrecte, `short_answer` normalisé, `block_id`/`exercise_id` invalides (404), bloc non publié (404), mauvais type de bloc (404), absence de fuite dans le HTML public de `/uaa/{slug}`, page + vérification de démo admin, authentification requise sur la démo |
| `tests/test_ticket17_no_regression.py` | `app/seed.py` non modifié : MC01 (12 exercices intacts, 0 bloc `editorial_exercise`), MC02, MC03, Mathématiques tous strictement inchangés |

**Résultat** : `pytest -q` → **236 passed** (198 avant ce ticket + 38 nouveaux), 2
warnings préexistants. Aucun appel réseau/IA réel.

**Ruff** : `ruff check .` → **36 erreurs**, strictement identiques (mêmes fichiers, mêmes
règles) à celles de `develop` — comparé via un worktree isolé sur `develop`. **0 nouvelle
erreur.**

**Vérifié manuellement** sur une base SQLite temporaire isolée (jamais `jury_central.db`,
intégrité re-vérifiée par MD5 avant/après) :
- `/uaa/ampcr-mc01`, `/uaa/ampcr-mc02`, `/uaa/ampcr-mc03`, `/uaa/mb32-uaa1` → 200,
  contenu inchangé ;
- connexion admin puis `/admin/editorial-exercise-demo` → 200, aucune fuite de solution
  dans le HTML brut ;
- `demo-true-false` réponse correcte (`1`) → `correct: true` ;
- `demo-single-choice` réponse incorrecte (`0`) → `correct: false`, réponse attendue
  révélée ;
- `demo-short-answer` réponse `"ram"` (minuscules) → `correct: true` (normalisation
  vérifiée en conditions réelles, pas seulement en test unitaire).

---

## 10. Limites connues

- Seulement 3 types sur les 7 identifiés par l'audit (`single_choice`, `true_false`,
  `short_answer`) — `long_answer`, `classification`, `ordering`, `matching` restent à
  construire.
- `mode: "exam"` existe dans le modèle mais n'est pas encore exploité (aucune UI, aucune
  route de soumission groupée) — réservé au ticket examen interactif.
- Aucun formulaire admin dédié pour créer/éditer un bloc `editorial_exercise` (comme pour
  `ai_exercise` avant lui) : édition uniquement via `app/seed.py` ou JSON brut dans le
  formulaire générique.
- Aucune intégration avec `progress.js` dans ce ticket (progression fine) — prévue par un
  ticket séparé selon l'audit.
- `short_answer` reste volontairement limité à une comparaison exacte après
  normalisation : aucune tolérance de faute de frappe au-delà des accents/casse/espaces
  (pas de distance de Levenshtein ni de correction approximative) — choix délibéré pour
  rester strictement déterministe et prévisible.

---

## 11. Prochaines dépendances

Ordre recommandé (reprend le découpage de l'audit, § J) :
1. Types `classification`/`ordering` (couvrent 4 des 12 exercices MC01 restants).
2. Correction IA pour `long_answer` (extension `rubric` du provider existant, couvre les
   8 exercices MC01 restants) — permettrait, combiné à l'étape 1, une migration complète
   des 12 exercices MC01 vers le socle interactif.
3. Examen interactif (`mode: "exam"`, soumission groupée, correction différée).
4. Progression enrichie (`progress.js`).
5. Formulaire admin dédié.

---

## Statut

Ticket terminé jusqu'au commit + push. Aucun merge, aucun déploiement. En attente de
validation ChatGPT, notamment sur : l'acceptation du taux de migration MC01 (0/12, avec
justification détaillée ci-dessus) et l'ordre de priorité des tickets suivants (§ 11).
