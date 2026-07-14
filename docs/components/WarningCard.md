# WarningCard

Carte "Attention" (voir `docs/UI_GUIDELINES.md`).

---

# Rôle

Signale un piège, une erreur fréquente ou un point important.

---

# Apparence

- Icône : ⚠️
- Couleur : rouge (attention/erreur)
- Version compacte (`jc-card--inline`) quand générée automatiquement à l'intérieur d'un
  autre bloc.

---

# Génération automatique (sans toucher au contenu)

`app/static/js/design_system.js` transforme automatiquement toute citation Markdown
(`> ...`) présente dans un bloc en WarningCard, au chargement de la page. C'est ainsi que
tous les « pièges fréquents » de MB32 UAA1/UAA2 (rédigés en Markdown avec `> **Piège
fréquent :** ...`) apparaissent comme des WarningCard, sans qu'aucun bloc de leçon dédié
n'ait été créé ni qu'aucun texte n'ait été modifié.

Une règle CSS de secours (`.content-markdown blockquote`) reproduit la même apparence si le
JavaScript est désactivé.

---

# Classification automatique de bloc

`app/card_kind.py`, `classify_block_title()` : un bloc dont le titre contient « attention »
ou « piège » serait classé `"warning"` — non utilisé actuellement (aucun bloc de leçon n'a un
tel titre ; les pièges sont toujours des citations à l'intérieur d'un autre bloc, gérées par
le mécanisme ci-dessus).

---

# Utilisation directe

```jinja
{% call cards.WarningCard() %}
    <p>Ne mélange jamais cm et m dans une même formule.</p>
{% endcall %}
```
