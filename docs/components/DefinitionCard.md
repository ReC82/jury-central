# DefinitionCard

Variante de [TheoryCard](TheoryCard.md) pour une définition isolée.

---

# Rôle

Met en avant une définition unique plutôt qu'un bloc de théorie complet.

---

# Apparence

- Icône : 📘
- Couleur : bleu (information), comme TheoryCard
- Libellé : « Définition »

---

# État actuel

Macro disponible (`app/templates/_cards.html`), mais non déclenchée automatiquement par
`app/card_kind.py` : le contenu actuel (MB32 UAA1/UAA2) regroupe les définitions dans les
blocs "Cours" plutôt que dans des blocs dédiés. Utilisable directement dans un template pour
une future UAA qui isolerait ses définitions.

---

# Utilisation

```jinja
{% call cards.DefinitionCard() %}
    <p><strong>Solide :</strong> objet en trois dimensions.</p>
{% endcall %}
```
