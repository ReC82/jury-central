# DefinitionCard

Variante de [TheoryCard](TheoryCard.md), pour le cas d'usage « définition » explicitement
cité dans `docs/UI_GUIDELINES.md` (« Les cartes » : « théorie ; exemple ; exercice ; quiz ;
fiche mémo ; définition ; attention ; méthode » — et section « Information » : « Utilisée
pour : définition ; rappel ; vocabulaire »).

---

# Objectif

Isoler visuellement une définition unique, pour la distinguer du reste du cours quand elle
mérite d'être repérée d'un coup d'œil.

---

# Quand l'utiliser

- Pour une définition centrale de la leçon, que l'étudiant doit pouvoir retrouver
  rapidement en relisant la page.
- Dans une future UAA dont le contenu isolerait explicitement ses définitions plutôt que de
  les intégrer au fil du texte de cours.

---

# Quand ne pas l'utiliser

- Pour l'ensemble du cours (vocabulaire, tableaux, formules) → [TheoryCard](TheoryCard.md).
- Pour une définition secondaire mentionnée en passant dans un paragraphe de cours : mieux
  vaut la laisser dans le texte (une DefinitionCard par phrase surchargerait la page,
  contraire au principe « éviter les murs de texte » mais aussi à « respiration visuelle »
  de `UI_GUIDELINES.md`).

---

# Structure

Identique à [TheoryCard](TheoryCard.md) (même macro générique `card()`), avec un libellé
différent :

```
.jc-card.jc-card--theory
├── .jc-card-header
│   ├── .jc-card-icon        (📘)
│   └── .jc-card-label       (« Définition »)
├── .jc-card-title (h5)      (optionnel)
└── .jc-card-body
```

---

# Comportement

- Même couleur que TheoryCard (bleu), même comportement CSS/JS (tableaux, citations).
- **Non déclenchée automatiquement** par `app/card_kind.py` : le contenu actuel de MB32
  UAA1/UAA2 regroupe les définitions dans les blocs « Cours » plutôt que dans des blocs
  dédiés. La macro `DefinitionCard()` existe dans `app/templates/_cards.html` et est prête à
  l'emploi, mais aucun bloc de leçon n'y est actuellement associé.

---

# Composants liés

- [TheoryCard](TheoryCard.md) — composant générique dont DefinitionCard est un alias.
- [MethodCard](MethodCard.md) — autre variante de carte de cours, pour une procédure plutôt
  qu'une définition.

---

# Exemple d'utilisation

```jinja
{% call cards.DefinitionCard() %}
    <p><strong>Solide :</strong> objet en trois dimensions (longueur, largeur/profondeur,
    hauteur).</p>
{% endcall %}
```
