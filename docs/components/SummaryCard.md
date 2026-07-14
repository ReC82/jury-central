# SummaryCard

Carte "Fiche mémo" (voir `docs/UI_GUIDELINES.md`).

---

# Rôle

Résume uniquement les éléments essentiels. Toujours très compacte.

---

# Apparence

- Icône : 📌
- Couleur : or/jaune, distincte des cinq couleurs de base pour bien la démarquer des cartes
  de contenu
- Padding réduit et taille de police légèrement plus petite que les autres cartes

---

# Classification automatique

`app/card_kind.py`, `classify_block_title()` : un bloc dont le titre contient « fiche mémo »
ou « mémo » (ex. « Fiche mémo — Géométrie »).

---

# Impression

Le bouton « Imprimer cette fiche » (`window.print()`), déjà présent dans le contenu Markdown
des fiches mémo, continue de fonctionner à l'identique. `design-system.css` ajoute une règle
`@media print` qui aplatit les cartes (bordures fines, pas d'ombre) pour une impression
propre.

---

# Utilisation

```jinja
{% call cards.SummaryCard("Fiche mémo — Géométrie") %}
    <div class="content-markdown">{{ html | safe }}</div>
{% endcall %}
```
