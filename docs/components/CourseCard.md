# CourseCard

Carte de navigation vers une UAA ou un module, pour les pages de listing.

---

# Objectif

Présenter une UAA ou un module dans une liste (page matière, page module) sous forme de
carte cohérente avec le reste du Design System, plutôt que comme un simple lien.

---

# Quand l'utiliser

*(Prévu, non implémenté — voir État actuel.)* Sur `subject_detail.html` (liste des modules
d'une matière) et `module_detail.html` (liste des UAA d'un module).

---

# Quand ne pas l'utiliser

- Pour le contenu d'une UAA elle-même (théorie, exercices, quiz) → les autres cartes du
  Design System ([TheoryCard](TheoryCard.md), [ExerciseCard](ExerciseCard.md), etc.).
- Dans le panneau d'administration : les listes admin (`/admin/subjects`, etc.) suivent les
  conventions Bootstrap existantes de `docs/admin.md`, non celles du Design System public.

---

# Structure

Non définie : aucune macro `CourseCard()` n'existe dans `app/templates/_cards.html`.

Proposition cohérente avec les autres cartes (à valider avant implémentation) :

```
.jc-card.jc-card--course
├── .jc-card-header
│   ├── .jc-card-icon
│   └── .jc-card-label            (code de l'UAA ou du module)
├── .jc-card-title (h5)           (titre de l'UAA/du module, lien)
└── .jc-card-body
    ├── résumé court (optionnel)
    └── badge de progression ([ProgressCard](ProgressCard.md))
```

---

# Comportement

*(Non implémenté.)*

---

# État actuel

**Non implémentée.** Cette tranche (Design System) a porté sur le rendu du contenu d'une UAA
(`/uaa/{slug}`, `uaa_detail.html`), pas sur les pages de listing (`/subjects`,
`/subjects/{slug}`, `/modules/{slug}`), qui affichent toujours de simples liens Bootstrap
(`subject_detail.html`, `module_detail.html`).

---

# Composants liés

- [ProgressCard](ProgressCard.md) — afficherait le badge de progression sur chaque
  CourseCard.
- [TheoryCard](TheoryCard.md) — même famille de composants (icône + libellé + titre), à
  réutiliser pour la structure de CourseCard le jour de son implémentation.

---

# Prochaine étape suggérée

Appliquer le même principe que les autres cartes à `module_detail.html` et
`subject_detail.html` : une UAA ou un module listé deviendrait une CourseCard (titre, statut
de progression via `data-uaa-slug-badge`, éventuellement un résumé du plan de l'UAA). Non
prioritaire — voir `docs/current_state.md`, Points ouverts.
