# Composants du Design System

Implémentation : `app/templates/_cards.html` (macros Jinja), `app/static/css/design-system.css`,
`app/static/js/design_system.js`, `app/card_kind.py`.

Toutes les cartes partagent le même rendu (icône, libellé, couleur, titre optionnel) via la
macro générique `card(meta, title)`. Les macros ci-dessous en sont des alias nommés.

---

# Cartes disponibles

- [TheoryCard](TheoryCard.md) — théorie, présentation, vocabulaire.
- [DefinitionCard](DefinitionCard.md) — une définition isolée (variante de TheoryCard).
- [ExampleCard](ExampleCard.md) — exemple entièrement résolu.
- [MethodCard](MethodCard.md) — procédure étape par étape.
- [ExerciseCard](ExerciseCard.md) — exercice rédigé, interactif.
- [ExamCard](ExamCard.md) — mini-test type examen.
- [QuizCard](QuizCard.md) — parcours de quiz.
- [WarningCard](WarningCard.md) — piège, erreur fréquente, point d'attention.
- [SummaryCard](SummaryCard.md) — fiche mémo, compacte.
- [ProgressCard](ProgressCard.md) — progression de lecture / de l'UAA.
- [CourseCard](CourseCard.md) — carte de navigation vers une UAA (non encore implémentée).

---

# Utilisation dans un template

```jinja
{% import "_cards.html" as cards %}

{% call cards.TheoryCard("Fonction constante — Cours") %}
    <p>...</p>
{% endcall %}
```

Pour le rendu automatique d'une UAA (`uaa_detail.html`), le type de carte de chaque bloc de
leçon est déduit de son titre par `app/card_kind.py` — voir `classify_block_title()`. Aucune
lecture ni modification du contenu pédagogique.
