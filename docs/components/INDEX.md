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

# Composants internes à une carte (sous-éléments, ticket #103)

Contrairement aux cartes ci-dessus (une par bloc de leçon, via `app/card_kind.py`), ces
composants vivent À L'INTÉRIEUR d'une carte existante (généralement `TheoryCard`/
`ExampleCard`), embarqués directement en HTML brut dans le Markdown du bloc (passé tel
quel par `app/content.py`) :

- [DefinitionGrid](DefinitionGrid.md) — plusieurs définitions courtes côte à côte (terme,
  explication, exemple).
- [CompareGrid](CompareGrid.md) — deux notions souvent confondues, ou mauvaise/bonne
  réponse, côte à côte.
- [DocCard](DocCard.md) — document support (mail, affiche, publication) séparé de son
  analyse.
- [EmailCard](EmailCard.md) — variante de DocCard : mail réaliste (en-tête, fil de réponse),
  texte réel et sélectionnable (ticket #108, FSE01 uniquement pour l'instant).
- [SocialPostCard](SocialPostCard.md) — variante de DocCard : publication de réseau social
  réaliste (avatar, réactions, commentaires), texte réel (ticket #108, FSE01 uniquement).
- [PosterCard](PosterCard.md) — variante de DocCard : affiche avec illustration générée une
  fois via l'API OpenAI et conservée durablement + slogan/mentions en HTML (ticket #108,
  FSE01 uniquement).
- [Diagram](Diagram.md) — schéma SVG relationnel (remplace les schémas en caractères),
  pour les cas que `.jc-flow` (linéaire) ne couvre pas. Depuis le ticket #108, un schéma
  destiné à un usage mobile peut fournir deux rendus distincts (large/colonne) permutés par
  média-requête, plutôt qu'un simple redimensionnement qui rendrait le texte illisible.

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
