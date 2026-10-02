# ExerciseStepCard

Introduit lors des retouches visuelles de FSE01 (ticket #112), remplace le rendu en bloc de
texte brut des exercices guidés (un `<details>` unique empilant consigne et corrigé imbriqué).
Étendu à FSE02-FSE16 (ticket #115) via la transformation générique
`app.v1.fse_course_sections.exercises_to_cards()` — y compris la conversion réelle en
HTML des listes jusque-là fondues en texte littéral à l'intérieur de certains corrigés
(ex. FSE03, liste numérotée), diagnostiquée en écrivant cette extension.

---

# Objectif

Présenter chaque exercice guidé comme sa propre carte, avec un numéro et un titre
clairement visibles, une consigne directement lisible (jamais masquée), un lien de retour
vers le document concerné, et un accordéon « Voir le corrigé » bien visible — jamais un
bloc de texte continu où consigne et corrigé se confondent.

**Ceci reste un exercice guidé du cours** (auto-évaluation, corrigé pédagogique) : aucun
moteur de correction, de notation ni d'appel IA n'est impliqué — à la différence des
exercices du parcours « S'entraîner »/« S'évaluer », qui restent gérés par
`app.v1.session_service` et ne changent pas.

---

# Quand l'utiliser

- Pour un exercice guidé (auto-corrigé par la lecture, pas par un moteur) à l'intérieur
  d'une `ExerciseCard`, quand la consigne et son corrigé méritent d'être visuellement
  distincts et que plusieurs exercices se suivent.

---

# Quand ne pas l'utiliser

- Pour un exercice noté/généré par le moteur V1 (QCM, question à trous, etc.) → ce n'est
  pas ce mécanisme, voir `app/v1/session_service.py`.
- Pour un exercice isolé, sans autre exercice à la suite, où une simple consigne +
  `<details>` suffirait déjà.

---

# Structure

```html
<div class="jc-exercise-card">
  <div class="jc-exercise-card-header">
    <span class="jc-exercise-number" aria-hidden="true">1</span>
    <h4 class="jc-exercise-title">Titre de l'exercice</h4>
  </div>
  <div class="jc-exercise-instructions">
    <p>Consigne courte...</p>
    <ol><li>Étape 1...</li><li>Étape 2...</li></ol>
    <p class="jc-exercise-doclink"><a href="#document-xxx">↑ Revoir le document</a></p>
  </div>
  <details class="jc-exercise-correction">
    <summary>Voir le corrigé</summary>
    <div class="jc-exercise-correction-body">
      <!-- structure du corrigé selon l'exercice : tableau, sections, comparaison... -->
      <div class="jc-why-correct">
        <span class="jc-why-correct-label">Pourquoi cette réponse est correcte</span>
        <p>...</p>
      </div>
    </div>
  </details>
</div>
```

## Variantes de corrigé observées (toutes du HTML réel, jamais du Markdown à l'intérieur d'un bloc HTML brut)

- **Tableau** (« Élément / Réponse / Justification ») : pour un exercice qui demande
  d'identifier plusieurs éléments du schéma dans un document — réutilise le style déjà
  existant `.content-markdown table`.
- **Sections labellisées** (`.jc-exercise-section`/`.jc-exercise-section-label`) : pour un
  corrigé qui distingue plusieurs notions successives (ex. Obstacle / Conséquence /
  Rétroaction).
- **Comparaison** (réutilise [CompareGrid](CompareGrid.md), `.jc-compare`) : pour une
  question qui identifie deux notions à la fois, présentées côte à côte.
- **Encadré final** `.jc-why-correct` : systématique, clôt chaque corrigé en expliquant en
  une phrase pourquoi cette réponse est correcte (pas une reformulation du corrigé, sa
  justification).

---

# Choix technique : écrire le corrigé en HTML réel, jamais en Markdown imbriqué

**Piège identifié et corrigé par ce composant** : `app.content.render_markdown` ne
retraite jamais le Markdown situé à l'intérieur d'un bloc HTML brut (`<details>`, `<div>`,
...) — une liste à tirets `- ...` placée à l'intérieur d'un `<details>` n'est donc **jamais**
convertie en `<ul><li>`, quelle que soit la présence d'une ligne vide autour (vérifié par
test direct : `render_markdown('<details>\n\n- a\n- b\n\n</details>')` renvoie les tirets
tels quels). C'est la cause exacte du rendu « encore un bloc de texte brut » signalé au
ticket #112 pour les anciens corrigés. La correction : écrire le corrigé entièrement en
HTML réel (`<p>`, `<ul>/<li>`, `<table>`...), jamais en syntaxe Markdown à l'intérieur d'un
bloc déjà en HTML brut.

---

# Comportement

- La consigne (`.jc-exercise-instructions`) est **toujours visible**, jamais masquée —
  seul le corrigé est replié par défaut.
- `<details>`/`<summary>` natifs : ouverture/fermeture au clic ET au clavier (Entrée ou
  Espace sur le `<summary>` focalisé, comportement natif du navigateur, sans JavaScript
  supplémentaire) — fermé par défaut (jamais l'attribut `open`).
- `.jc-exercise-correction summary` est stylé comme un bouton bien visible (fond teinté,
  bordure, pilule arrondie), avec un chevron qui s'inverse à l'ouverture
  (`[open] summary::after`) et un état focus visible (`:focus-visible`).
- Le lien de retour au document (`.jc-exercise-doclink`) est une simple ancre `#id` vers le
  document correspondant dans la section Exemples commentés de la même page (tous les blocs
  d'une UAA sont rendus sur une seule page — voir `app/main.py::uaa_detail`).
- `break-inside: avoid` à l'impression ; le bouton de corrigé s'affiche en style sobre
  (bordure noire) plutôt qu'en couleur, pour rester lisible en noir et blanc.

---

# Composants liés

- [CompareGrid](CompareGrid.md) — réutilisé tel quel pour les corrigés de type comparaison.
- [ExampleTitle](ExampleTitle.md)/[DecryptTitle](DecryptTitle.md) — composants voisins
  introduits par le même ticket, pour la section Exemples commentés.
- [ExerciseCard](ExerciseCard.md) — la carte globale (une par bloc de leçon) à l'intérieur
  de laquelle plusieurs `ExerciseStepCard` peuvent apparaître.

---

# Exemple d'utilisation

Voir `app/v1/fse01_course.py::_section_exercises()`.
