# ExampleCard

Correspond au type de carte **Exemple** décrit dans `docs/UI_GUIDELINES.md` (section
« Types de cartes »).

---

# Objectif

Présenter un exemple entièrement résolu, pour montrer comment appliquer la théorie qui
précède avant de laisser l'étudiant s'exercer seul.

---

# Quand l'utiliser

- Pour un exemple corrigé où l'énoncé, la résolution et la réponse finale doivent être
  visibles immédiatement — conforme à `UI_GUIDELINES.md` : « Toujours afficher : l'énoncé ;
  la résolution ; la réponse finale. »
- Pour un problème de transfert entièrement résolu (l'énoncé et sa méthode générale font
  aussi partie de ce cas, voir Classification automatique ci-dessous).

---

# Quand ne pas l'utiliser

- Pour un exercice que l'étudiant doit résoudre lui-même, avec une correction qui ne doit
  pas apparaître immédiatement → [ExerciseCard](ExerciseCard.md). C'est la distinction
  centrale entre les deux cartes : ExampleCard montre, ExerciseCard fait travailler.
- Pour une procédure générale indépendante d'un énoncé chiffré → [MethodCard](MethodCard.md).

---

# Structure

```
.jc-card.jc-card--example
├── .jc-card-header
│   ├── .jc-card-icon        (💡)
│   └── .jc-card-label       (« Exemple »)
├── .jc-card-title (h5)      (optionnel)
└── .jc-card-body
    ├── énoncé
    ├── résolution détaillée
    └── réponse finale
```

Aucune partie n'est masquée : à la différence d'ExerciseCard, `content-markdown` n'est pas
retraité par le mécanisme de correction masquée (voir Comportement).

---

# Comportement

- Couleur : vert (`--jc-green`), conforme au code couleur « vert → réussite » de
  `UI_GUIDELINES.md` — un exemple résolu illustre une réussite, pas une information neutre.
- Classification automatique (`app/card_kind.py`, `classify_block_title()`) : tout bloc dont
  le titre contient « exemple » ou « transfert » (ex. « Solides — Exemples résolus »,
  « Volumes — Problème de transfert »).
- Icône 💡 : `UI_GUIDELINES.md` associe cette icône à « Astuce » et ne définit pas d'icône
  propre au type « Exemple ». Elle est réutilisée ici car un exemple résolu joue un rôle
  proche d'une astuce (il révèle une façon de procéder) ; aucune autre carte ne revendique
  cette icône.
- Le contenu Markdown bénéficie des mêmes traitements génériques que
  [TheoryCard](TheoryCard.md) (tableaux responsives, citations → WarningCard).

---

# Composants liés

- [TheoryCard](TheoryCard.md) — précède généralement une ExampleCard dans une leçon.
- [ExerciseCard](ExerciseCard.md) — suit généralement une ExampleCard ; comportement
  opposé (correction toujours visible vs. toujours masquée).
- [MethodCard](MethodCard.md) — une ExampleCard illustre souvent une MethodCard.

---

# Exemple d'utilisation

```jinja
{% call cards.ExampleCard("Exemple corrigé 1 — identifier un solide") %}
    <p><strong>Énoncé :</strong> ...</p>
    <p><strong>Correction :</strong> ...</p>
    <p><strong>Réponse :</strong> ...</p>
{% endcall %}
```
