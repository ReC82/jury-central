# ExerciseCard

Carte "Exercice" (voir `docs/UI_GUIDELINES.md`).

---

# Rôle

Présente un exercice rédigé. La correction n'est **jamais** affichée immédiatement.

---

# Apparence

- Icône : 📝
- Couleur : orange (méthode/exercice)

---

# Classification automatique

`app/card_kind.py`, `classify_block_title()` : un bloc dont le titre contient « exercice »
(ex. « Solides — Exercices »). Les blocs de type `generated_exercise` (exercices générés
automatiquement, voir `app/exercise_blocks.py`) sont toujours classés `"exercise"`, quel que
soit leur titre.

---

# Comportement interactif

Deux mécanismes coexistent, selon le type de bloc :

**Exercice généré (`generated_exercise`)** — déjà interactif avant le Design System :
champ de réponse + bouton Vérifier (`app/static/js/exercise.js`, `/practice/api/verify`),
indice, correction affichée uniquement sur demande (`/practice/api/reveal`).

**Exercice rédigé (bloc Markdown)** — rendu interactif par
`app/static/js/design_system.js` sans aucune modification du texte pédagogique : la
correction (repérée par un paragraphe `**Correction :**` ou un titre `## Correction...`) est
déplacée dans un conteneur masqué. Un champ de réponse libre et un bouton « Afficher la
correction » sont insérés à sa place. Aucune vérification automatique n'est effectuée : la
plupart des exercices rédigés n'ont pas de réponse unique vérifiable (voir
`docs/current_state.md`, Points ouverts).

---

# Utilisation

Automatique pour tout bloc classé `"exercise"`. Pour un usage direct :

```jinja
{% call cards.ExerciseCard("Exercice 4 — appliquer") %}
    <div class="content-markdown">{{ html | safe }}</div>
{% endcall %}
```
