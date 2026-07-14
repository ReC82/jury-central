# ProgressCard

Progression — voir `docs/UI_GUIDELINES.md` (« L'étudiant doit toujours savoir où il en
est »).

---

# État actuel

N'est pas une carte au sens de `.jc-card` : les indicateurs de progression existants sont
volontairement légers (barre fine, badge), pas des blocs encadrés, pour ne pas alourdir la
page.

Trois niveaux, déjà distincts avant le Design System et complétés par lui :

- **Progression de la leçon** *(nouveau)* : barre fine collante en haut du contenu
  (`.jc-lesson-progress`), qui suit le défilement de la page —
  `app/static/js/design_system.js`, fonction `initLessonProgress()`.
- **Progression de l'UAA** : bouton « Marquer comme terminé » + badges (À faire / En cours /
  Terminé), déjà existant — `app/static/js/progress.js`, stockage `localStorage` (pas de
  compte utilisateur).
- **Progression du quiz** : « Question N / M » + score final, déjà existant —
  `app/static/js/quiz.js`.

---

# Limite connue

Pas de vue d'ensemble consolidée (ex. « 3 leçons sur 6 terminées » pour une UAA) : le badge
de progression est binaire par UAA (todo/in_progress/done), pas proportionnel au nombre de
blocs lus. Amélioration possible mais non prioritaire (voir `docs/current_state.md`, Points
ouverts).
