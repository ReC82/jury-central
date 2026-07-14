# CourseCard

Carte de navigation vers une UAA, utilisée sur les pages de listing (matière, module).

---

# État actuel

**Non implémentée.** Cette tranche (Design System) portait sur le rendu du contenu d'une
UAA (`/uaa/{slug}`), pas sur les pages de listing (`/subjects`, `/subjects/{slug}`,
`/modules/{slug}`), qui affichent toujours de simples liens Bootstrap.

---

# Prochaine étape suggérée

Appliquer le même principe que les autres cartes (`app/templates/_cards.html`) à
`module_detail.html` et `subject_detail.html` : une UAA ou un module listé deviendrait une
CourseCard (titre, statut de progression via `data-uaa-slug-badge`, éventuellement un résumé
du plan de l'UAA). Non prioritaire — voir `docs/current_state.md`, Points ouverts.
