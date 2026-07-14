# ExerciseCard

Correspond aux sections **Exercices** et **Exercices à compléter** de
`docs/UI_GUIDELINES.md`.

---

# Objectif

Faire travailler l'étudiant activement : présenter un exercice sans révéler la correction,
proposer un champ de réponse, et n'afficher la correction que sur demande explicite.

---

# Quand l'utiliser

- Pour tout exercice rédigé demandant à l'étudiant de produire une réponse (calcul,
  explication, complétion de tableau).
- Pour un exercice généré automatiquement par un générateur Python
  (`app/exercise_blocks.py`, `generators/`).

---

# Quand ne pas l'utiliser

- Pour un exemple déjà résolu, où la correction doit être visible immédiatement →
  [ExampleCard](ExampleCard.md).
- Pour un mini-test complet type examen (plusieurs questions, consigne de justification) →
  [ExamCard](ExamCard.md), qui masque tout un ensemble de questions plutôt qu'un exercice
  isolé.
- Pour un quiz à choix multiples ou à réponse courte, avec explication et score →
  [QuizCard](QuizCard.md) (mécanisme différent : vérification serveur immédiate, pas de
  masquage de texte).

---

# Structure

Deux formes coexistent selon le type de bloc de leçon (`app/models.py`, `BlockType`) :

**Exercice généré (`generated_exercise`)** — structure fixe, générée par
`app/templates/uaa_detail.html` :

```
.jc-card.jc-card--exercise
└── .jc-card-body
    └── .exercise-widget (un par exercice généré)
        ├── .exercise-statement
        ├── champ de réponse + bouton Vérifier
        ├── .exercise-feedback
        ├── bouton Indice (optionnel) + bouton Afficher la correction
        ├── .exercise-hint (masqué initialement)
        ├── .exercise-steps (masqué initialement)
        └── bouton Nouvel exercice
```

**Exercice rédigé (bloc `markdown`)** — structure Markdown normale, retraitée par le
Design System (voir Comportement) :

```
.jc-card.jc-card--exercise
└── .jc-card-body
    └── .content-markdown
        ├── énoncé (visible)
        ├── .jc-exercise-controls        (inséré par JS : champ réponse libre + bouton)
        └── .jc-exercise-correction.d-none   (correction déplacée ici par JS, masquée)
```

---

# Comportement

- Couleur : orange (`--jc-orange`), conforme au code couleur « orange → méthode/exercice »
  de `UI_GUIDELINES.md` (orange y est associé à « méthode » ; réutilisé ici car un exercice
  demande d'appliquer une méthode).
- Classification automatique (`app/card_kind.py`) : tout bloc dont le titre contient
  « exercice » ; tout bloc de type `generated_exercise`, quel que soit son titre.
- **Exercice généré** : interactif dès le rendu serveur (`app/static/js/exercise.js`) —
  champ de réponse + bouton Vérifier (`/practice/api/verify`), indice, correction affichée
  uniquement sur demande (`/practice/api/reveal`), jamais de réponse envoyée au navigateur
  avant validation (voir `app/answer_checking.py`).
- **Exercice rédigé** : rendu interactif côté client, sans aucune modification du texte
  pédagogique (`app/static/js/design_system.js`, fonction `splitExerciseCorrections()`) : la
  correction — repérée par un paragraphe commençant par `**Correction :**` ou un titre
  `## Correction...` — est déplacée dans un conteneur masqué (`d-none`) ; un champ de
  réponse libre et un bouton « Afficher la correction » sont insérés à sa place. Aucune
  vérification automatique n'est effectuée pour ce cas : la plupart des exercices rédigés
  n'ont pas de réponse unique vérifiable (voir Limite connue).

---

# Limite connue

Pour les exercices rédigés, il n'y a pas de vérification serveur (pas de ✅/❌) : le champ de
réponse sert uniquement à encourager l'étudiant à répondre avant de comparer avec la
correction. Une vérification automatique nécessiterait une réponse structurée par exercice,
ce qui impliquerait de modifier le contenu pédagogique — explicitement hors périmètre de
cette tranche (voir `docs/current_state.md`, Points ouverts).

---

# Composants liés

- [ExampleCard](ExampleCard.md) — même position dans une leçon, comportement opposé.
- [ExamCard](ExamCard.md) — variante pour un mini-test complet.
- [MethodCard](MethodCard.md) — la méthode qu'un exercice met en pratique.
- [QuizCard](QuizCard.md) — autre forme d'exercice interactif, avec vérification serveur.

---

# Exemple d'utilisation

Rendu automatique pour tout bloc classé `"exercise"`. Pour un usage direct :

```jinja
{% call cards.ExerciseCard("Exercice 4 — appliquer") %}
    <div class="content-markdown">{{ html | safe }}</div>
{% endcall %}
```
