# ExamCard

Correspond à la section **Mini-tests** de `docs/UI_GUIDELINES.md` (« Les mini-tests doivent
ressembler à un examen »).

---

# Objectif

Présenter un mini-test complet type examen (plusieurs questions, consigne de justification),
en le distinguant visuellement d'un simple exercice.

---

# Quand l'utiliser

- Pour un mini-test final regroupant plusieurs questions couvrant toute une UAA (ex.
  « Mini-test final — Géométrie »).
- Pour toute évaluation présentée comme un examen blanc, avec consigne de justification des
  réponses.

---

# Quand ne pas l'utiliser

- Pour un exercice isolé au sein d'une leçon → [ExerciseCard](ExerciseCard.md).
- Pour un quiz auto-corrigé question par question avec score →
  [QuizCard](QuizCard.md).

---

# Structure

Identique à la forme « exercice rédigé » d'[ExerciseCard](ExerciseCard.md) : un bloc
Markdown normal, retraité par le Design System.

```
.jc-card.jc-card--exam
└── .jc-card-body
    └── .content-markdown
        ├── consigne + questions (visibles)
        ├── .jc-exercise-controls          (bouton « Afficher la correction », sans champ de
        │                                    réponse — voir Comportement)
        └── .jc-exercise-correction.d-none  (toute la section de correction, y compris son
                                              titre, masquée)
```

---

# Comportement

- Couleur : orange (`--jc-orange`), fond légèrement teinté (`--jc-orange-bg`) — même famille
  que [ExerciseCard](ExerciseCard.md), mais fond distinct pour se démarquer visuellement
  d'un simple exercice.
- Icône 🎓 : `UI_GUIDELINES.md` ne définit pas d'icône pour les mini-tests. Choisie pour
  évoquer un examen, sans conflit avec une icône déjà attribuée ailleurs.
- Classification automatique (`app/card_kind.py`) : tout bloc dont le titre contient
  « mini-test ».
- Même mécanisme de masquage que [ExerciseCard](ExerciseCard.md)
  (`app/static/js/design_system.js`, `splitExerciseCorrections()`), avec une règle
  supplémentaire : si un segment commence par un titre contenant « correction » (ex.
  « ## Correction du mini-test »), **tout le segment est masqué, y compris son titre** — un
  seul bouton « Afficher la correction » révèle l'ensemble des réponses. Contrairement à
  ExerciseCard, aucun champ de réponse libre n'est inséré (une réponse par question aurait
  demandé de fragmenter le mini-test question par question, hors périmètre actuel — voir
  Limite connue).

---

# Limite connue

Le mini-test reste un seul bloc à correction masquée globalement, pas un parcours paginé
question par question (Précédent/Suivant/Terminer) comme le décrit `UI_GUIDELINES.md`. Cela
demanderait de restructurer le contenu en plusieurs blocs (un par question), une évolution
volontairement reportée pour ne pas modifier le contenu pédagogique dans cette tranche — voir
`docs/current_state.md`, Points ouverts.

---

# Composants liés

- [ExerciseCard](ExerciseCard.md) — même mécanisme de masquage, sans champ de réponse.
- [QuizCard](QuizCard.md) — alternative auto-corrigée question par question, déjà paginée.

---

# Exemple d'utilisation

Rendu automatique pour tout bloc classé `"exam"`. Pour un usage direct :

```jinja
{% call cards.ExamCard("Mini-test final — Géométrie") %}
    <div class="content-markdown">{{ html | safe }}</div>
{% endcall %}
```
