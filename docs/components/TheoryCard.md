# TheoryCard

Correspond au type de carte **Information** décrit dans `docs/UI_GUIDELINES.md` (section
« Types de cartes »).

---

# Objectif

Présenter une notion de cours : présentation, vocabulaire, définitions, tableaux de
référence, formules. C'est la carte de base sur laquelle repose la théorie d'une leçon.

---

# Quand l'utiliser

- Pour la présentation d'une leçon (objectifs, prérequis).
- Pour le corps du cours (vocabulaire, tableaux de référence, formules).
- Pour un rappel ou une notion transversale qui ne constitue ni un exemple résolu, ni un
  exercice, ni un piège.
- Par défaut : `app/card_kind.py` classe tout bloc de leçon dans `"theory"` si son titre ne
  correspond à aucun autre type (voir Comportement).

---

# Quand ne pas l'utiliser

- Pour un exemple entièrement résolu → [ExampleCard](ExampleCard.md).
- Pour un exercice à réponse masquée → [ExerciseCard](ExerciseCard.md).
- Pour un piège ou une erreur fréquente → [WarningCard](WarningCard.md) (généré
  automatiquement, voir plus bas — ne jamais l'appeler manuellement pour ce cas).
- Pour un résumé très compact en fin de leçon → [SummaryCard](SummaryCard.md).
- Pour une définition que l'on souhaite isoler visuellement du reste du cours →
  [DefinitionCard](DefinitionCard.md) (variante dédiée, même rendu).

---

# Structure

Rendu par la macro générique `card()` (`app/templates/_cards.html`) via l'alias
`TheoryCard(title=None)` :

```
.jc-card.jc-card--theory
├── .jc-card-header
│   ├── .jc-card-icon        (📘)
│   └── .jc-card-label       (« Théorie »)
├── .jc-card-title (h5)      (optionnel, titre du bloc)
└── .jc-card-body            (contenu, transmis via {% call %})
```

Aucune structure interne imposée dans `.jc-card-body` : le contenu Markdown rendu
(`.content-markdown`) y est inséré tel quel.

---

# Comportement

- Couleur : bleu (`--jc-blue`), conforme au code couleur « bleu → information » de
  `UI_GUIDELINES.md`.
- Classification automatique (`app/card_kind.py`, `classify_block_title()`) : type par
  défaut, utilisé pour tout titre contenant « présentation », « cours », « plan de l'UAA »,
  ou ne correspondant à aucun mot-clé plus spécifique.
- Le contenu Markdown à l'intérieur d'une TheoryCard peut déclencher d'autres comportements
  du Design System, gérés par `app/static/js/design_system.js` :
  - une citation (`> ...`) est transformée automatiquement en [WarningCard](WarningCard.md) ;
  - les tableaux deviennent responsives (`table-responsive`) ;
  - les cellules de tableau vides deviennent éditables (`.jc-fill-input`).
- Aucune correction n'est masquée dans une TheoryCard : contrairement à
  [ExerciseCard](ExerciseCard.md), tout le contenu reste visible immédiatement.

---

# Composants liés

- [DefinitionCard](DefinitionCard.md) — variante pour une définition isolée.
- [MethodCard](MethodCard.md) — variante pour une procédure étape par étape.
- [WarningCard](WarningCard.md) — généré automatiquement à partir des citations du contenu.
- [ExampleCard](ExampleCard.md) — étape suivante d'une leçon (théorie puis exemples).
- [SummaryCard](SummaryCard.md) — condense la théorie en fin de leçon.

---

# Exemple d'utilisation

```jinja
{% import "_cards.html" as cards %}

{% call cards.TheoryCard("Solides — Cours") %}
    <div class="content-markdown">{{ html | safe }}</div>
{% endcall %}
```

Rendu automatique (sans appel manuel) pour tout bloc de leçon classé `"theory"` par
`app/main.py` (route `uaa_detail`) via `app/card_kind.py`.
