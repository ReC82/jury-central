# WarningCard

Correspond au type de carte **Attention** décrit dans `docs/UI_GUIDELINES.md`.

---

# Objectif

Signaler un piège, une erreur fréquente ou un point important, avec une couleur qui le
distingue immédiatement du reste du cours.

---

# Quand l'utiliser

- Pour tout piège ou erreur fréquente identifié dans le cours source (ex. « ne mélange
  jamais cm et m dans une même formule »).
- Pour un point important qui mérite d'interrompre visuellement la lecture.

---

# Quand ne pas l'utiliser

- Pour une information neutre (définition, rappel) → [TheoryCard](TheoryCard.md).
- Pour signaler qu'une réponse est incorrecte dans un exercice ou un quiz : ce n'est pas le
  rôle de WarningCard, qui documente un piège pédagogique général, pas un retour sur une
  tentative de l'étudiant (voir [ExerciseCard](ExerciseCard.md), [QuizCard](QuizCard.md)).

---

# Structure

**Générée automatiquement** (cas normal, voir Comportement) :

```
.jc-card.jc-card--warning.jc-card--inline
├── .jc-card-header
│   ├── .jc-card-icon    (⚠️)
│   └── .jc-card-label   (« Attention »)
└── .jc-card-body        (contenu de la citation Markdown d'origine)
```

**Appelée directement** via la macro `WarningCard()` : structure identique, sans le
modificateur `jc-card--inline` (plus grande, comme les autres cartes de bloc).

---

# Comportement

- Couleur : rouge (`--jc-red`), fond légèrement teinté — conforme au code couleur
  « rouge → erreur » de `UI_GUIDELINES.md`.
- **Génération automatique sans modification du contenu** : `app/static/js/design_system.js`
  (fonction `wrapBlockquotesAsWarningCards()`) transforme, au chargement de la page, toute
  citation Markdown (`> ...`) présente dans un bloc en WarningCard. C'est ainsi que tous les
  « pièges fréquents » de MB32 UAA1/UAA2 (rédigés en Markdown avec `> **Piège fréquent :**
  ...`) apparaissent comme des WarningCard, sans qu'aucun bloc de leçon dédié n'ait été créé
  ni qu'aucun texte n'ait été modifié.
- Une règle CSS de secours (`.content-markdown blockquote` dans `design-system.css`)
  reproduit la même apparence si le JavaScript est désactivé (dégradation progressive).
- Classification automatique de bloc entier (`app/card_kind.py`) : un bloc dont le **titre**
  contient « attention » ou « piège » serait classé `"warning"`. Non observé actuellement :
  aucun bloc de leçon n'a un tel titre, les pièges étant toujours des citations à l'intérieur
  d'un autre bloc, gérées par le mécanisme ci-dessus.

---

# Composants liés

- [TheoryCard](TheoryCard.md) — bloc à l'intérieur duquel les citations sont détectées.
- [MethodCard](MethodCard.md) — contient parfois un piège lié à la procédure décrite.

---

# Exemple d'utilisation

Cas normal : aucun appel direct nécessaire, écrire une citation Markdown suffit.

```markdown
> **Piège fréquent :** un cylindre, un cône et une sphère ne sont pas des polyèdres.
```

Appel direct (cas où l'on écrit du HTML dans un template plutôt que du Markdown) :

```jinja
{% call cards.WarningCard() %}
    <p>Ne mélange jamais cm et m dans une même formule.</p>
{% endcall %}
```
