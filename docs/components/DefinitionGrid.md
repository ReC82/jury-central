# DefinitionGrid

Composant interne à une carte (pas une carte à part entière, pas un alias de
`DefinitionCard`), introduit lors de la refonte pédagogique et visuelle des cours FSE
(ticket #103).

---

# Objectif

Présenter plusieurs définitions courtes côte à côte, à l'intérieur d'une carte de théorie,
sans empiler des `DefinitionCard` (qui imbriqueraient une `.jc-card` dans une autre
`.jc-card`, jamais fait ailleurs dans le projet) ni noyer les définitions dans un paragraphe
continu.

---

# Quand l'utiliser

- Pour le vocabulaire central d'une leçon (3 à 8 termes), quand chaque terme mérite d'être
  repéré d'un coup d'œil (terme, explication courte, exemple concret optionnel).

---

# Quand ne pas l'utiliser

- Pour une seule définition isolée dans tout le cours → la laisser dans le texte ou utiliser
  `DefinitionCard` (`_cards.html`) si elle doit vraiment former sa propre carte de bloc.
- Pour plus de 8-10 termes : préférer un tableau (`content-markdown table`), plus compact.

---

# Structure

```html
<div class="jc-definitions">
  <div class="jc-definition">
    <span class="jc-definition-term">Terme</span>
    <p class="jc-definition-body">Explication simple, en une ou deux phrases.</p>
    <p class="jc-definition-example"><strong>Exemple :</strong> cas concret.</p>
  </div>
  ...
</div>
```

`.jc-definition-example` est optionnel (omis si le terme n'a pas besoin d'exemple séparé).

---

# Comportement

- Grille responsive (`repeat(auto-fit, minmax(230px, 1fr))`) : passe automatiquement à une
  colonne sur mobile, sans media query dédiée.
- Couleur bleue (`--jc-blue`/`--jc-blue-bg`), cohérente avec `TheoryCard`/`DefinitionCard`
  (même famille de notions : théorie/vocabulaire).
- `break-inside: avoid` à l'impression (la grille entière reste sur une page si possible).
- Toujours placé À L'INTÉRIEUR d'une carte existante (théorie), jamais à la racine du
  contenu Markdown d'un bloc.

---

# Composants liés

- [TheoryCard](TheoryCard.md) / [DefinitionCard](DefinitionCard.md) — la grille vit à
  l'intérieur d'une carte de ce type.

---

# Exemple d'utilisation

Directement dans le Markdown d'un bloc de leçon (le Markdown passe le HTML brut sans le
modifier, voir `app/content.py`) :

```markdown
<div class="jc-definitions">
<div class="jc-definition">
<span class="jc-definition-term">Canal</span>
<p class="jc-definition-body">Support matériel de transmission du message.</p>
<p class="jc-definition-example"><strong>Exemple :</strong> un mail, une affiche.</p>
</div>
</div>
```
