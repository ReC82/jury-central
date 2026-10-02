# DecryptTitle

Introduit lors des retouches visuelles de FSE01 (ticket #112). Composant réutilisable, mais
appliqué à FSE01 uniquement pour cette étape — l'extension à d'autres cours attend une
confirmation explicite de l'utilisateur.

---

# Objectif

Annoncer clairement, par un titre dédié, que ce qui suit est l'**analyse** du document
qu'on vient de lire — pas une suite du document lui-même. Sépare visuellement le document
de son explication, avec un espacement cohérent, sans dupliquer le composant
[DocCard](DocCard.md) (qui reste réservé au document).

---

# Quand l'utiliser

- Juste avant un tableau ou une liste d'analyse qui suit un document (mail, affiche,
  publication...), pour marquer explicitement la transition document → analyse.

---

# Quand ne pas l'utiliser

- Comme titre d'un document lui-même (→ l'en-tête `.jc-doc-header` du document suffit).
- Pour une analyse qui ne suit pas directement un document concret.

---

# Structure

```html
<h4 class="jc-decrypt-title"><span aria-hidden="true">🔍</span> Décryptons ce document</h4>
```

Suivi directement du tableau ou de la liste d'analyse (voir
`app/v1/fse01_course.py::_section_examples()`, `_analysis_table()`).

---

# Comportement

- `margin: 1.5rem 0 0.75rem` : espace net après le document qui précède, espace plus court
  avant l'analyse qui suit immédiatement.
- Couleur `--jc-blue` (information), cohérente avec le code couleur du Design System.
- `break-after: avoid` à l'impression.

---

# Composants liés

- [ExampleTitle](ExampleTitle.md) — titre du document lui-même, avant ce titre d'analyse.
- [DocCard](DocCard.md) — le document analysé.

---

# Exemple d'utilisation

Voir `app/v1/fse01_course.py::_section_examples()`.
