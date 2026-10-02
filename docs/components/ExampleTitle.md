# ExampleTitle

Introduit lors des retouches visuelles de FSE01 (ticket #112), étendu à FSE02-FSE16
(ticket #115) via la transformation générique `app.v1.fse_course_sections.exemple_headers_to_titles`.

---

# Objectif

Espacer correctement le titre de chaque exemple commenté par rapport au tableau d'analyse
de l'exemple précédent (32px avant le titre) et par rapport au document qui le suit (16px),
sans dépendre d'une règle générique `h3` qui changerait le rendu d'autres cours avant
qu'elle n'y soit appliquée volontairement.

---

# Quand l'utiliser

- Pour le titre d'un exemple commenté, dans une carte `ExampleCard`, quand plusieurs
  exemples se suivent dans le même bloc et doivent rester visuellement distincts.

---

# Quand ne pas l'utiliser

- Pour un titre de section générique (`##`/`###` Markdown normal) ailleurs dans un cours :
  cette classe n'est volontairement pas la règle par défaut de `.content-markdown h3`.

---

# Structure

```html
<h3 class="jc-example-title">Exemple 1 — Titre du document</h3>
```

Écrit en HTML brut (pas en syntaxe Markdown `###`) pour pouvoir porter la classe — voir
`app/v1/fse01_course.py::_section_examples()`.

---

# Comportement

- `margin: 2rem 0 1rem` (32px avant, 16px après) ; `margin-top: 0` sur le premier titre de
  la carte (`:first-child`), pour ne jamais créer un espace inutile en haut du bloc.
- `break-after: avoid` à l'impression : jamais de titre isolé en bas de page, séparé de son
  document.
- Les 32px/16px restent cohérents à toutes les largeurs (aucune règle responsive
  spécifique n'était nécessaire : un espacement vertical fixe reste approprié du téléphone
  à l'impression).

---

# Composants liés

- [DecryptTitle](DecryptTitle.md) — même logique de titre dédié, pour l'analyse plutôt que
  pour le document lui-même.

---

# Exemple d'utilisation

Voir `app/v1/fse01_course.py::_section_examples()`.
