# ProgressCard

Correspond à la section **Progression** de `docs/UI_GUIDELINES.md` (« L'étudiant doit
toujours savoir où il en est »).

---

# Objectif

Donner à l'étudiant une indication constante de sa progression, à trois niveaux : la leçon
en cours, l'UAA, et le quiz en cours.

---

# Quand l'utiliser

- Sur toute page de contenu d'UAA, pour la progression de lecture (barre en haut de page).
- Sur toute page listant des UAA ou modules, pour le badge de statut (À faire / En cours /
  Terminé).
- Dans tout quiz ou parcours de quiz, pour le numéro de question et le score.

---

# Quand ne pas l'utiliser

- Ne pas transformer la progression en carte encadrée (`.jc-card`) : `UI_GUIDELINES.md`
  demande une interface « aérée », et un indicateur de progression consulté en permanence
  doit rester discret (barre fine, badge), pas un bloc de contenu supplémentaire à chaque
  leçon.

---

# Structure

**Progression de la leçon** *(ajoutée par le Design System)* :

```
.jc-lesson-progress                  (barre fine, collante en haut du contenu)
└── .jc-lesson-progress-bar          (largeur = % de défilement de la page)
```

**Progression de l'UAA** *(existante avant le Design System, inchangée)* :

```
button.mark-complete-btn[data-uaa-slug]     (bouton « Marquer comme terminé »)
span[data-uaa-slug-badge] / [data-uaa-slugs]  (badges À faire / En cours / Terminé)
```

**Progression du quiz** *(existante avant le Design System, inchangée)* — voir
[QuizCard](QuizCard.md) : `.quiz-run-progress` (« Question N / M ») et le score affiché en
fin de parcours.

---

# Comportement

- **Progression de la leçon** *(nouveau)* : barre sticky en haut du contenu
  (`position: sticky; top: 0`), dont la largeur suit le défilement de la page —
  `app/static/js/design_system.js`, fonction `initLessonProgress()`. Couleur bleue
  (`--jc-blue`), cohérente avec [TheoryCard](TheoryCard.md).
- **Progression de l'UAA** : stockage dans `localStorage` (pas de compte utilisateur),
  `app/static/js/progress.js` — inchangé par cette tranche.
- **Progression du quiz** : calculée côté client à partir des réponses envoyées au serveur,
  `app/static/js/quiz.js` — inchangé par cette tranche, sauf l'ajout de l'explication
  systématique (voir [QuizCard](QuizCard.md)).

---

# Limite connue

Pas de vue d'ensemble consolidée (ex. « 3 leçons sur 6 terminées » pour une UAA) : le badge
de progression est binaire par UAA (todo/in_progress/done), pas proportionnel au nombre de
blocs lus. Amélioration possible mais non prioritaire — voir `docs/current_state.md`, Points
ouverts.

---

# Composants liés

- [QuizCard](QuizCard.md) — porte sa propre progression (question N/M, score).
- [CourseCard](CourseCard.md) — afficherait le badge de progression sur les pages de listing
  (non implémentée).

---

# Exemple d'utilisation

La barre de progression de la leçon est ajoutée automatiquement en haut de toute page
`uaa_detail.html`, sans configuration :

```html
<div class="jc-lesson-progress d-print-none mb-4" aria-hidden="true">
    <div class="jc-lesson-progress-bar"></div>
</div>
```
