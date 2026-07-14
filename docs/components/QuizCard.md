# QuizCard

Correspond au type de carte **Quiz** et à la section **Quiz** de `docs/UI_GUIDELINES.md`.

---

# Objectif

Faire passer un quiz auto-corrigé (question isolée ou parcours de plusieurs questions), avec
une explication systématique après chaque réponse — jamais une simple mention
Correct/Incorrect.

---

# Quand l'utiliser

- Pour toute question à choix multiples, vrai/faux, ou à réponse numérique, dont la
  correction est vérifiable automatiquement côté serveur.
- Pour un ensemble de questions formant un parcours noté (score final).

---

# Quand ne pas l'utiliser

- Pour un exercice à réponse libre non vérifiable automatiquement →
  [ExerciseCard](ExerciseCard.md).
- Pour un mini-test avec consigne de justification écrite → [ExamCard](ExamCard.md).

---

# Structure

**Quiz isolé** (bloc `quiz` sans `QuizConfig.group`) :

```
.jc-card.jc-card--quiz
└── .jc-card-body
    └── .quiz-widget[data-block-id][data-answer-type]
        ├── question
        ├── choix (boutons) ou champ numérique + bouton Vérifier
        ├── .quiz-feedback
        └── .quiz-explanation (masqué initialement)
```

**Parcours de quiz groupé** (plusieurs blocs `quiz` partageant `QuizConfig.group`, fusionnés
par `app/main.py` en un seul item `quiz_run`) :

```
.jc-card.jc-card--quiz
└── .jc-card-body
    └── .quiz-run[data-questions]
        ├── .quiz-run-progress    (« Question N / M »)
        ├── .quiz-run-question    (rendu dynamiquement par JS)
        └── .quiz-run-result      (score + bouton Recommencer, masqué jusqu'à la fin)
```

---

# Comportement

- Couleur : violet (`--jc-purple`) — couleur dédiée au quiz, en plus des cinq couleurs de
  base de `docs/UI_GUIDELINES.md`, pour le distinguer visuellement des exercices rédigés.
- Icône 🎯, conforme à `UI_GUIDELINES.md`.
- Classification automatique (`app/card_kind.py`) : tout bloc de type `quiz`, qu'il soit
  isolé ou fusionné en parcours, est toujours classé `"quiz"`, indépendamment de son titre.
- Vérification serveur (`app/quiz.py`, `QuizConfig.check()` + `POST
  /practice/api/quiz/{block_id}/verify`) : la réponse correcte n'est jamais envoyée au
  navigateur avant validation.
- Après chaque réponse (`app/static/js/quiz.js`) :
  - ✅ Correct / ❌ Incorrect (texte explicite, jamais un simple mot) ;
  - l'explication renvoyée par le serveur est **toujours affichée**, y compris dans le
    parcours groupé (`quiz-run`) — corrigé dans cette tranche : ce parcours n'affichait
    auparavant que « Correct. »/« Incorrect. » sans explication, ce qui ne respectait pas
    `UI_GUIDELINES.md` (« Ne jamais se limiter à Correct ou Incorrect »).
- Toujours affichés dans un parcours groupé : numéro de la question, progression, score
  final, bouton Recommencer — conforme à `UI_GUIDELINES.md`.
- La question et l'explication sont rendues via le renderer de contenu riche unique
  (`app/content.py::render_markdown` côté serveur, `renderRichContent()` côté client —
  voir `app/static/js/rich_content.js`) plutôt qu'affichées comme texte brut : un tableau
  Markdown dans une question de quiz s'affiche comme un vrai tableau, pas comme une phrase
  (VS003.1).

---

# Composants liés

- [ExerciseCard](ExerciseCard.md) — autre forme d'interactivité, sans vérification serveur
  pour les exercices rédigés.
- [ExamCard](ExamCard.md) — alternative non auto-corrigée pour un mini-test.

---

# Exemple d'utilisation

Le contenu d'une QuizCard n'est jamais rédigé directement dans un template : il provient de
`QuizConfig` (`app/quiz.py`) et est assemblé par la route `uaa_detail` (`app/main.py`), qui
choisit automatiquement `cards.card(item.card, title=...)` avec `item.card.kind == "quiz"`.

```jinja
{% call cards.card(item.card, title="Quiz — " ~ item.quiz_run.count ~ " questions") %}
    <div class="quiz-run" data-questions="{{ item.quiz_run.questions_json }}">
        <div class="quiz-run-progress small text-muted mb-2"></div>
        <div class="quiz-run-question"></div>
        <div class="quiz-run-result d-none"></div>
    </div>
{% endcall %}
```
