# TheoryCard

Carte "Information" (voir `docs/UI_GUIDELINES.md`).

---

# Rôle

Présente une notion de cours : présentation, vocabulaire, tableaux, formules.

C'est le type de carte par défaut (`app/card_kind.py`, `classify_block_title()` retombe sur
`"theory"` si aucun autre type ne correspond au titre du bloc).

---

# Apparence

- Icône : 📘
- Couleur : bleu (information)
- Bordure gauche colorée, fond blanc

---

# Comportement

Aucune interaction propre. Le contenu Markdown à l'intérieur peut néanmoins déclencher
d'autres comportements du Design System :

- une citation (`> ...`) est transformée automatiquement en [WarningCard](WarningCard.md) ;
- les tableaux deviennent responsives, et leurs cellules vides deviennent éditables (tableaux
  à compléter).

---

# Utilisation

```jinja
{% call cards.TheoryCard("Solides — Cours") %}
    <div class="content-markdown">{{ html | safe }}</div>
{% endcall %}
```
