# QuizCard

Carte "Quiz" (voir `docs/UI_GUIDELINES.md`).

---

# Rôle

Enveloppe un quiz (question isolée ou parcours de plusieurs questions groupées).

---

# Apparence

- Icône : 🎯
- Couleur : violet (dédiée au quiz, en plus des cinq couleurs de
  `docs/UI_GUIDELINES.md`)

---

# Classification automatique

`app/card_kind.py` : tout bloc de type `quiz`, qu'il soit isolé ou fusionné en parcours
(`QuizConfig.group`), est toujours classé `"quiz"` — indépendamment de son titre.

---

# Comportement interactif

Logique inchangée par le Design System (`app/static/js/quiz.js`), à une correction près :
le parcours de quiz groupé (`quiz-run`, une question à la fois) n'affichait que
« Correct. »/« Incorrect. » ; il affiche désormais systématiquement l'explication retournée
par le serveur après chaque réponse, comme le fait déjà le widget de quiz isolé — conforme à
`docs/UI_GUIDELINES.md` (« Ne jamais se limiter à Correct ou Incorrect »).

Toujours affichés : numéro de la question, progression (« Question N / M »), score final,
bouton Recommencer.

---

# Utilisation

Automatique pour tout bloc de type `quiz`. Le contenu (question, choix, réponse) n'est
jamais géré via un `{% call %}` direct : il provient de `QuizConfig`
(`app/quiz.py`) et est rendu par `uaa_detail.html`.
