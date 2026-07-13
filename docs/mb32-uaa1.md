# MB32 UAA1 — Tableaux, graphiques, formules

État détaillé de cette UAA. Développée en tranches verticales (une leçon complète à la fois,
pas toute l'UAA d'un coup) — voir `docs/content_workflow.md` pour la méthode.

## Objectifs de l'UAA

Compétence générale : **traiter un problème en utilisant un tableau de nombres, un
graphique ou une formule.**

8 sections prévues (voir le bloc "Plan de l'UAA", toujours publié en tête de l'UAA) :

1. Lire un tableau, un graphique, une formule
2. **Fonction constante** ✅ terminée
3. Construire un tableau et un graphique
4. Intersection de deux fonctions
5. Puissances et notation scientifique
6. Proportionnalité inverse et croissance exponentielle
7. Intérêts simples et composés
8. Choisir le bon outil

## Section 2 — Fonction constante (terminée)

Accès : http://127.0.0.1:8000/uaa/mb32-uaa1 (section publiée en 2ᵉ position, après le plan).

### Contenu

| Bloc | Type | Rôle |
|---|---|---|
| Fonction constante — Présentation et objectifs | `markdown` | Définition, objectifs, prérequis |
| Fonction constante — Cours | `markdown` | Théorie complète (MathJax), exemple d'intro, tableau de valeurs, "À retenir", "Erreurs fréquentes" |
| Fonction constante — Graphique interactif | `markdown` | Graphique Plotly, curseur pour faire varier $p$ en temps réel |
| Fonction constante — Exemples résolus | `markdown` | 5 exemples résolus |
| Fonction constante — Exercice guidé | `markdown` | Énoncé + correction détaillée pas à pas |
| Fonction constante — Exercices automatiques | `generated_exercise` | Générateur `maths.functions.constant_function`, difficulté 1, 3 exercices affichés (régénérables à l'infini) |
| Fonction constante — Quiz 1/10 … 10/10 | `quiz` × 10 | Regroupées (`group="fonction-constante"`) en un seul parcours avec score |
| Fonction constante — Fiche mémo | `markdown` | Synthèse imprimable |

### Générateur : `maths.functions.constant_function`

Génère $f(x) = p$ sous 4 formulations tirées aléatoirement (calculer une image, compléter un
tableau, retrouver $p$ à partir d'un point, associer graphique et formule), sur 3 niveaux de
difficulté (entiers positifs simples → entiers relatifs → fractions/décimaux simples).
Aucun cas ambigu à gérer : contrairement à une équation, une fonction constante est toujours
bien définie quel que soit $p$. Déterministe par seed, réponse toujours calculée (jamais
écrite en dur) — voir `generators/maths/constant_function.py` et
`docs/exercise_generators.md`.

### Quiz : 10 questions, mélange de types

- 4 QCM classiques
- 3 vrai/faux
- 3 réponses numériques (`answer_type="numeric"`, validées comme les exercices générés :
  virgule ou point, comparaison exacte)

Rendu comme un seul parcours interactif (une question à la fois, score final, bouton
"Recommencer") grâce au regroupement par `group`/`order_in_group` — voir
`docs/content_workflow.md`.

### Validation des réponses

100 % côté serveur. Aucune réponse correcte n'est présente dans le HTML envoyé au
navigateur avant que l'étudiant ait répondu — voir `docs/exercise_generators.md`, section
"Validation des réponses : jamais côté client".

### Données initiales

```bash
seed-db          # idempotent : relancer ne duplique rien
# ou : python -m app.seed
```

`app/seed.py` supprime automatiquement les anciens blocs de démonstration devenus obsolètes
(`OBSOLETE_DEMO_BLOCK_TITLES`) avant d'insérer le contenu réel de cette section.

### Limites restantes (assumées pour cette tranche)

- Pas de modèle `Chapter` : une "leçon" reste une séquence de `LessonBlock` groupés par
  titre/position, pas une entité de base de données dédiée. Suffisant pour une leçon ; à
  reconsidérer si la navigation "chapitre précédent/suivant" devient nécessaire pour
  plusieurs leçons à la fois.
- Progression suivie au niveau de **l'UAA entière** (bouton "Marquer comme terminé"
  existant), pas encore par section individuelle — cohérent avec l'absence de modèle
  `Chapter`.
- Sections 1 et 3 à 8 : toujours au stade "placeholder" (checklist, non publiées).
- Pas d'évaluation finale de l'UAA à ce stade (prévue plus tard, une fois plusieurs sections
  terminées).
- Le graphique interactif ne couvre que la fonction constante ; le même widget
  (`interactive_graph.js`) sera étendu pour la fonction du premier degré et les
  intersections dans une prochaine tranche.
