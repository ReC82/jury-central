# MethodCard

Correspond au type de carte **Méthode** décrit dans `docs/UI_GUIDELINES.md` (section
« Types de cartes » : « Explique une procédure étape par étape »).

---

# Objectif

Détacher une procédure générale (une suite d'étapes réutilisable) du reste du cours, pour
que l'étudiant puisse la repérer et s'y référer facilement, indépendamment d'un exemple
chiffré particulier.

---

# Quand l'utiliser

- Pour une liste d'étapes numérotées décrivant *comment faire* (ex. « dessiner un
  parallélépipède en perspective cavalière », « associer un solide à ses vues », « choisir
  la bonne méthode » pour un problème de transfert).
- Quand la procédure est réutilisable pour plusieurs exercices, pas seulement pour l'exemple
  qui la suit immédiatement.

---

# Quand ne pas l'utiliser

- Pour un exemple résolu appliquant la méthode à un cas chiffré →
  [ExampleCard](ExampleCard.md).
- Pour la théorie générale (définitions, formules) qui précède la méthode →
  [TheoryCard](TheoryCard.md).

---

# Structure

```
.jc-card.jc-card--method
├── .jc-card-header
│   ├── .jc-card-icon        (🧭)
│   └── .jc-card-label       (« Méthode »)
├── .jc-card-title (h5)      (optionnel)
└── .jc-card-body
    └── liste d'étapes (<ol>, généralement)
```

---

# Comportement

- Couleur : orange (`--jc-orange`), fond légèrement teinté — conforme au code couleur
  « orange → méthode » de `UI_GUIDELINES.md`.
- Icône 🧭 : `UI_GUIDELINES.md` ne définit pas d'icône pour « Méthode ». La boussole a été
  choisie pour évoquer une procédure/un cheminement, sans entrer en conflit avec une icône
  déjà attribuée à une autre carte.
- **Non déclenchée automatiquement** par `app/card_kind.py` : dans le contenu actuel de MB32
  UAA1/UAA2, les sections « ## Méthode : ... » restent à l'intérieur des blocs
  [TheoryCard](TheoryCard.md) (ex. « Perspective cavalière — Cours », qui contient une
  section « Méthode : dessiner un parallélépipède... »), pour ne pas fragmenter en blocs
  supplémentaires un contenu déjà importé (voir `docs/IMPORT_WORKFLOW.md`, règle : l'import
  ne doit pas modifier l'architecture au-delà du strict nécessaire). La macro `MethodCard()`
  existe dans `app/templates/_cards.html` et est prête à l'emploi pour une future UAA qui
  isolerait ses méthodes en blocs dédiés.

---

# Composants liés

- [TheoryCard](TheoryCard.md) — contient actuellement les sections de méthode (voir
  Comportement).
- [ExampleCard](ExampleCard.md) — applique la méthode à un cas concret.
- [ExerciseCard](ExerciseCard.md) — demande à l'étudiant d'appliquer lui-même la méthode.

---

# Exemple d'utilisation

```jinja
{% call cards.MethodCard("Dessiner un parallélépipède rectangle en perspective cavalière") %}
    <ol>
        <li>Dessiner la face avant en vraie grandeur.</li>
        <li>Depuis trois sommets visibles, tracer des fuyantes parallèles.</li>
        <li>Réduire la profondeur si demandé.</li>
    </ol>
{% endcall %}
```
