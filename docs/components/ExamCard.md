# ExamCard

Variante de [ExerciseCard](ExerciseCard.md) pour un mini-test type examen.

---

# Rôle

Présente un mini-test complet (plusieurs questions, consigne de justification). Comme pour
ExerciseCard, la correction n'est jamais affichée immédiatement.

---

# Apparence

- Icône : 🎓
- Couleur : orange, fond légèrement teinté (distinct d'ExerciseCard pour se démarquer d'un
  simple exercice)

---

# Classification automatique

`app/card_kind.py`, `classify_block_title()` : un bloc dont le titre contient « mini-test »
(ex. « Mini-test final — Géométrie »).

---

# Comportement interactif

Même mécanisme de masquage que [ExerciseCard](ExerciseCard.md)
(`app/static/js/design_system.js`), avec une règle supplémentaire : si un titre `## Correction
du mini-test` (ou toute section commençant par un titre contenant « correction ») démarre un
segment, **tout le segment est masqué**, y compris son titre — un seul bouton « Afficher la
correction » révèle l'ensemble.

---

# Limite connue

Le mini-test reste un seul bloc à correction masquée, pas un parcours paginé question par
question (Précédent/Suivant/Terminer) comme le suggère `docs/UI_GUIDELINES.md` — voir
`docs/current_state.md`, Points ouverts.
