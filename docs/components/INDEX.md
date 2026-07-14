# Composants du Design System

Implémentation : `app/templates/_cards.html` (macros Jinja), `app/static/css/design-system.css`,
`app/static/js/design_system.js`, `app/card_kind.py`.

Toutes les cartes partagent le même rendu (icône, libellé, couleur, titre optionnel) via la
macro générique `card(meta, title)`. Les composants ci-dessous en sont des alias nommés, sauf
mention contraire. Conformité stricte à `docs/UI_GUIDELINES.md` : voir chaque fiche pour le
détail des choix de couleur/icône et leurs justifications quand `UI_GUIDELINES.md` ne les
précise pas explicitement.

---

# Cartes de contenu (théorie et illustration)

- [TheoryCard](TheoryCard.md) — théorie, présentation, vocabulaire. Type par défaut.
- [DefinitionCard](DefinitionCard.md) — une définition isolée (variante de TheoryCard).
- [MethodCard](MethodCard.md) — procédure étape par étape.
- [ExampleCard](ExampleCard.md) — exemple entièrement résolu.
- [WarningCard](WarningCard.md) — piège, erreur fréquente ; généré automatiquement à partir
  des citations Markdown (`> ...`), sans appel manuel dans le cas courant.

# Cartes d'évaluation (interactives)

- [ExerciseCard](ExerciseCard.md) — exercice rédigé ou généré, correction masquée jusqu'à
  demande explicite.
- [ExamCard](ExamCard.md) — mini-test type examen (variante d'ExerciseCard).
- [QuizCard](QuizCard.md) — parcours de quiz auto-corrigé, avec explication systématique.

# Cartes de synthèse et navigation

- [SummaryCard](SummaryCard.md) — fiche mémo, compacte et imprimable.
- [ProgressCard](ProgressCard.md) — progression de lecture / de l'UAA / du quiz (barre et
  badges, pas une carte encadrée — voir la fiche pour le détail).
- [CourseCard](CourseCard.md) — carte de navigation vers une UAA, **non implémentée**.

---

# État d'implémentation

| Composant | Macro dans `_cards.html` | Déclenchée automatiquement |
|---|---|---|
| TheoryCard | ✅ | ✅ (type par défaut) |
| DefinitionCard | ✅ | ❌ (contenu actuel regroupé dans TheoryCard) |
| MethodCard | ✅ | ❌ (contenu actuel regroupé dans TheoryCard) |
| ExampleCard | ✅ | ✅ |
| WarningCard | ✅ | ✅ (via les citations Markdown, pas le titre du bloc) |
| ExerciseCard | ✅ | ✅ |
| ExamCard | ✅ | ✅ |
| QuizCard | — (contenu piloté par `QuizConfig`, pas de `{% call %}` direct) | ✅ |
| SummaryCard | ✅ | ✅ |
| ProgressCard | — (barre + badges, pas une macro de carte) | ✅ |
| CourseCard | ❌ | — |

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

---

# Règle de création de nouveaux composants

Ne créer un nouveau composant que si aucun des composants existants ne convient, et
uniquement après l'avoir justifié (voir `docs/PROJECT_RULES.md`, règle 2 : « Tu ne crées
jamais une nouvelle façon de faire si une solution existe déjà dans le projet »). Documenter
toute création dans ce dossier en suivant la structure utilisée par les fiches existantes :
Objectif, Quand l'utiliser, Quand ne pas l'utiliser, Structure, Comportement, Composants
liés, Exemple d'utilisation.
