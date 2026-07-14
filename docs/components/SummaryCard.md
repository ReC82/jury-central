# SummaryCard

Correspond au type de carte **Fiche mémo** décrit dans `docs/UI_GUIDELINES.md` (« Toujours
très compacte. Uniquement les éléments essentiels. »).

---

# Objectif

Résumer, en fin de leçon ou d'UAA, uniquement les éléments essentiels (définitions clés,
formules, procédure d'examen), dans un format compact et imprimable.

---

# Quand l'utiliser

- Pour la fiche mémo de fin de leçon ou de fin d'UAA.
- Pour tout contenu explicitement présenté comme un pense-bête (« à retenir »).

---

# Quand ne pas l'utiliser

- Pour le cours complet, même synthétique → [TheoryCard](TheoryCard.md). Une SummaryCard ne
  doit contenir que l'essentiel, jamais une reformulation complète du cours.
- Pour un exemple ou un exercice, même bref → [ExampleCard](ExampleCard.md) /
  [ExerciseCard](ExerciseCard.md).

---

# Structure

```
.jc-card.jc-card--summary
├── .jc-card-header
│   ├── .jc-card-icon        (📌)
│   └── .jc-card-label       (« À retenir »)
├── .jc-card-title (h5)      (optionnel)
└── .jc-card-body            (padding réduit, texte légèrement plus petit — voir Comportement)
    ├── définitions clés
    ├── tableau de formules
    ├── procédure résumée
    └── bouton « Imprimer cette fiche » (`window.print()`, déjà présent dans le contenu
        Markdown existant, inchangé)
```

---

# Comportement

- Couleur : or/jaune (`--jc-gold`), volontairement distincte des cinq couleurs de base de
  `docs/UI_GUIDELINES.md`, pour bien démarquer la fiche mémo des cartes de contenu courant.
- Icône 📌, conforme à `UI_GUIDELINES.md` (« À retenir »).
- Classification automatique (`app/card_kind.py`) : tout bloc dont le titre contient
  « fiche mémo » ou « mémo » (ex. « Fiche mémo — Géométrie »).
- Compacité : `padding` réduit (`1rem 1.25rem` contre `1.25rem 1.5rem` pour les autres
  cartes) et taille de police légèrement réduite (`0.95rem`) dans `design-system.css`.
- Impression : le bouton « Imprimer cette fiche », déjà présent dans le contenu Markdown des
  fiches mémo, continue de fonctionner à l'identique. `design-system.css` ajoute une règle
  `@media print` qui aplatit toutes les cartes (bordure fine, sans ombre) pour une impression
  propre.

---

# Composants liés

- [TheoryCard](TheoryCard.md) — la fiche mémo condense le contenu qui y est développé.
- [ExamCard](ExamCard.md) — souvent placée juste avant la fiche mémo dans l'ordre d'une UAA.

---

# Exemple d'utilisation

```jinja
{% call cards.SummaryCard("Fiche mémo — Géométrie") %}
    <div class="content-markdown">{{ html | safe }}</div>
{% endcall %}
```
