# ExampleCard

Carte "Exemple" (voir `docs/UI_GUIDELINES.md`).

---

# Rôle

Présente un exemple entièrement résolu : énoncé, résolution, réponse finale — toujours
affichés immédiatement (à la différence d'[ExerciseCard](ExerciseCard.md), la correction
n'est jamais masquée).

---

# Apparence

- Icône : 💡
- Couleur : vert (réussite)

---

# Classification automatique

`app/card_kind.py`, `classify_block_title()` : un bloc dont le titre contient « exemple » ou
« transfert » (ex. « Solides — Exemples résolus », « Volumes — Problème de transfert »).

---

# Utilisation

```jinja
{% call cards.ExampleCard("Exemple corrigé 1 — identifier un solide") %}
    <p>...énoncé, résolution, réponse...</p>
{% endcall %}
```
