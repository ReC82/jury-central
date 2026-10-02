# CompareGrid

Composant interne à une carte, introduit lors de la refonte pédagogique et visuelle des
cours FSE (ticket #103).

---

# Objectif

Opposer visuellement deux notions souvent confondues, ou une mauvaise réponse à la bonne
réponse correspondante, côte à côte plutôt qu'en texte continu.

---

# Quand l'utiliser

- Pour une paire « mauvaise réponse / bonne réponse » (variantes `--bad`/`--good`).
- Pour deux notions proches que les étudiants confondent souvent (variantes `--a`/`--b`,
  neutres, sans jugement de valeur entre les deux).

---

# Quand ne pas l'utiliser

- Pour plus de deux éléments à comparer → préférer un tableau.
- Pour un piège ponctuel sans comparaison explicite → `WarningCard` (citation Markdown
  `>`), pas ce composant.

---

# Structure

```html
<div class="jc-compare">
  <div class="jc-compare-item jc-compare-item--bad">
    <span class="jc-compare-label">❌ Mauvaise réponse</span>
    <p>...</p>
  </div>
  <div class="jc-compare-item jc-compare-item--good">
    <span class="jc-compare-label">✅ Bonne réponse</span>
    <p>...</p>
  </div>
</div>
```

Variantes neutres : `--a` (bleu) / `--b` (orange), mêmes classes de structure.

---

# Comportement

- Deux colonnes égales (`grid-template-columns: 1fr 1fr`), une seule colonne sous 576px.
- Couleur rouge/vert pour mauvaise/bonne réponse (code couleur `UI_GUIDELINES.md`) ; bleu/
  orange pour une comparaison neutre entre deux notions.
- `break-inside: avoid` à l'impression.

---

# Composants liés

- [WarningCard](WarningCard.md) — pour un piège isolé, sans comparaison à deux éléments.
- [ExampleCard](ExampleCard.md)/[TheoryCard](TheoryCard.md) — carte dans laquelle ce
  composant est généralement utilisé.

---

# Exemple d'utilisation

```markdown
<div class="jc-compare">
<div class="jc-compare-item jc-compare-item--a">
<span class="jc-compare-label">Code</span>
<p>Système de signes utilisé (langue, symboles).</p>
</div>
<div class="jc-compare-item jc-compare-item--b">
<span class="jc-compare-label">Canal</span>
<p>Support matériel de transmission (mail, affiche...).</p>
</div>
</div>
```
