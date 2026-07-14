# MethodCard

Carte "Méthode" (voir `docs/UI_GUIDELINES.md`).

---

# Rôle

Explique une procédure étape par étape (ex. « dessiner un parallélépipède en perspective
cavalière », « choisir la bonne méthode » pour un problème de transfert).

---

# Apparence

- Icône : 🧭
- Couleur : orange (méthode)

---

# État actuel

Macro disponible (`app/templates/_cards.html`, kind `"method"`, styles dans
`design-system.css`), mais non déclenchée automatiquement par `app/card_kind.py` : dans le
contenu actuel, les sections « ## Méthode : ... » restent à l'intérieur des blocs
[TheoryCard](TheoryCard.md) (ex. « Perspective cavalière — Cours »), pour éviter de
fragmenter le contenu pédagogique existant en blocs supplémentaires. Utilisable directement
dans un template pour une future UAA qui isolerait ses méthodes.

---

# Utilisation

```jinja
{% call cards.MethodCard("Dessiner un parallélépipède en perspective cavalière") %}
    <ol><li>...</li></ol>
{% endcall %}
```
