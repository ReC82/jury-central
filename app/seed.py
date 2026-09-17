from pathlib import Path

from app.ai_exercise_blocks import AIExerciseBlockConfig
from app.database import DATABASE_URL, Base, SessionLocal, engine, ensure_schema_migrations
from app.editorial_exercise import EditorialExerciseBlockConfig, EditorialExerciseItem
from app.exercise_blocks import ExerciseBlockConfig
from app.models import UAA, BlockSpace, BlockType, LessonBlock, Module, Subject
from app.quiz import QuizConfig
from app.slugify import slugify

SUBJECT_NAME = "Mathématiques"
MODULE_CODES = ["MB32", "MQ32", "MQ34"]

UAA1_CODE = "UAA1"
UAA1_TITLE = "Tableaux, graphiques, formules"

UAA2_CODE = "UAA2"
UAA2_TITLE = "Géométrie"

# Anciens blocs de démonstration/placeholder, remplacés par du vrai contenu au fil des
# tranches verticales. Supprimés par leur titre lors du seed pour ne pas laisser de
# contenu obsolète mélangé au nouveau.
OBSOLETE_DEMO_BLOCK_TITLES = {
    "Introduction",
    "Vidéo d'introduction",
    "Brouillon",
    "Entraîne-toi",
    "Quiz de compréhension",
    "2. Fonction constante et fonction du premier degré",
    "Exemple d'exercice généré — Fonction du premier degré",
    "Exemple de quiz — Lecture de graphique",
    "Fiche mémo — Tableaux, graphiques, formules",
}

# Ticket #21 : les exercices 1, 2, 9 et 11 du mini-cours 01 AMPCR migrent de blocs
# Markdown statiques vers des blocs `editorial_exercise` structurés (classification,
# ordering). Les deux blocs Markdown qui les contenaient sont retirés PAR TITRE lors du
# seed (même mécanisme que `OBSOLETE_DEMO_BLOCK_TITLES` ci-dessus) et remplacés par des
# blocs de titres différents (voir `MC01_BLOCKS`) : ce mécanisme est indispensable sur un
# staging déjà seedé, où `_seed_uaa` ne modifie jamais le contenu d'un bloc existant dont
# le titre correspond déjà — sans ce retrait explicite, l'ancien texte des exercices 1/2/9/11
# resterait affiché en doublon à côté des nouveaux blocs structurés. Voir
# `docs/claude-reports/2026-09-16_ticket-21_classification-ordering.md`, section
# « Migration du contenu déjà seedé (staging) », pour le détail de la procédure de
# déploiement (seed-db, sans reset-db).
#
# Ticket #29 : même mécanisme pour les 3 derniers blocs Markdown restants de MC01
# (exercices 3/4, 5/6/7/8, 10/12), migrés en blocs `editorial_exercise`
# (long_answer/diagnostic/vocabulary). Après ce ticket, MC01 ne contient plus AUCUN bloc
# Markdown d'exercice — les 12 exercices sont tous des blocs `editorial_exercise`.
MC01_OBSOLETE_TITLES = {
    "Architecture d'un PC — Exercices (1/3 : composants et rôles)",
    "Architecture d'un PC — Exercices (3/3 : scénario, diagnostic, vocabulaire)",
    "Architecture d'un PC — Exercices (composants et rôles : suite)",
    "Architecture d'un PC — Exercices (2/3 : RAM, stockage, GPU, PSU)",
    "Architecture d'un PC — Exercices (diagnostic et vocabulaire : suite)",
}

# Ticket #37 : `_seed_uaa` ne met jamais à jour `position` pour un bloc déjà existant
# (voir sa docstring — au même titre que `content`/`title`/`is_published`, `position` est
# modifiable depuis l'admin et ne doit donc jamais être écrasé en silence pour un bloc
# quelconque). Or les 6 blocs ci-dessous existaient déjà AVANT le ticket #29 (créés au
# #21, ou avant) : ils ont gardé la valeur de `position` de l'époque, alors que les 8
# nouveaux blocs d'exercices insérés par #29 ont reçu la position actuellement déclarée
# dans `MC01_BLOCKS` — d'où des positions dupliquées (ex. 16, 17, 18) et un ordre
# d'affichage incorrect (Exercice 9 et Exercice 11 intercalés), documenté dans le rapport
# de validation staging du ticket #29. Liste explicite et bornée à MC01 (jamais un
# mécanisme générique appliqué à tous les blocs, voir `_seed_uaa(reposition_titles=...)`)
# : seuls ces 6 titres verront leur `position` resynchronisée sur la valeur de
# `MC01_BLOCKS` si elle diverge, garantissant que les 12 exercices s'affichent dans
# l'ordre pédagogique strict 1→12 même sur un staging déjà seedé avant ce ticket, sans
# reset-db. Voir `docs/claude-reports/2026-09-17_ticket-37_mc01-practice-order.md`.
MC01_PRACTICE_REPOSITION_TITLES = frozenset(
    {
        "Exercice 9 — Lancement d'un programme (ordering)",
        "Exercice 11 — Entrée, sortie ou mixte (classification)",
        "Architecture d'un PC — Génère ton propre exercice (IA)",
        "Fiche mémo — Architecture générale d'un PC",
        "Examen final — Architecture générale d'un PC (10 questions, 20 points)",
        "Examen final — Corrigé (réservé formateur, non publié)",
    }
)

_CONSTANT_FUNCTION_PRESENTATION = r"""# Fonction constante

## Présentation

Une **fonction constante** est la fonction la plus simple qui existe : elle donne toujours
le même résultat, peu importe la valeur que tu lui donnes en entrée.

On la note :

$$f(x) = p$$

où $p$ (une lettre qui se lit "pé") est un nombre fixe, choisi une fois pour toutes.

## Objectifs

À la fin de ce chapitre, tu sauras :

- reconnaître une fonction constante à partir de sa formule, d'un tableau de valeurs ou
  d'un graphique ;
- calculer l'image $f(x)$ d'un nombre $x$ quelconque ;
- construire le tableau de valeurs et le graphique d'une fonction constante ;
- retrouver la valeur de $p$ à partir d'un graphique ou d'un tableau.

## Prérequis

- Savoir lire un tableau de nombres et un graphique.
- Savoir ce qu'est une fonction : une "machine" qui associe à chaque nombre $x$ un seul
  résultat $f(x)$.
"""

_CONSTANT_FUNCTION_COURSE = r"""## Définition

$$f(x) = p \quad \text{où } p \text{ est un nombre réel fixe}$$

Quelle que soit la valeur de $x$ que tu choisis, le résultat $f(x)$ est **toujours** $p$.
$x$ n'intervient jamais dans le calcul : c'est ce qui rend cette fonction "constante".

## Exemple d'introduction

Imagine un abonnement à une salle de sport qui coûte 30 € par mois, **quel que soit** le
nombre de fois où tu t'y rends. Si $x$ représente le nombre de visites et $f(x)$ le prix à
payer :

$$f(x) = 30$$

Que tu y ailles 0 fois ou 20 fois dans le mois, tu payes toujours 30 €.

## Tableau de valeurs

Pour $f(x) = 5$ :

| $x$ | -2 | -1 | 0 | 1 | 2 | 10 |
|---|---|---|---|---|---|---|
| $f(x)$ | 5 | 5 | 5 | 5 | 5 | 5 |

La ligne du bas ne change jamais : c'est la signature d'une fonction constante.

## Graphique

Le graphique d'une fonction constante $f(x) = p$ est **toujours une droite horizontale**,
qui coupe l'axe des $y$ à la hauteur $p$. Regarde le graphique interactif ci-dessous pour
t'en convaincre.

## À retenir

- $f(x) = p$ : le résultat ne dépend jamais de $x$.
- Le graphique est une droite **horizontale**.
- La droite coupe l'axe des $y$ (l'axe vertical) exactement en $p$.
- $p$ peut être positif, négatif, ou nul.

## Erreurs fréquentes

- Confondre $f(x) = p$ avec $f(x) = x$ (la fonction identité, qui elle dépend de $x$).
- Penser que le graphique est une droite verticale (une droite verticale n'est même pas le
  graphique d'une fonction).
- Oublier que $p$ peut être négatif : $f(x) = -3$ est aussi une fonction constante.
"""

_CONSTANT_FUNCTION_GRAPH = r"""Utilise le curseur pour changer la valeur de $p$ et observe comment la droite se déplace
immédiatement, tout en restant horizontale.

<div class="jc-graph-constant" data-p="3" data-min="-10" data-max="10"></div>
"""

_CONSTANT_FUNCTION_EXAMPLES = r"""## Exemple 1

Soit $f(x) = 7$. Calcule $f(4)$.

**Solution :** $f(x) = 7$ pour tout $x$, donc $f(4) = 7$.

## Exemple 2

Soit $f(x) = -2$. Calcule $f(0)$ et $f(100)$.

**Solution :** La fonction est constante, donc $f(0) = -2$ et $f(100) = -2$ : le résultat ne
change jamais.

## Exemple 3

Le graphique d'une fonction constante passe par le point $(5, 8)$. Quelle est la valeur de
$p$ ?

**Solution :** Pour une fonction constante, $f(x) = p$ pour tout $x$. Le point $(5, 8)$
donne directement $p = 8$, donc $f(x) = 8$.

## Exemple 4

Complète le tableau de valeurs de $f(x) = -1$ pour $x \in \{-3, 0, 4\}$.

**Solution :**

| $x$ | -3 | 0 | 4 |
|---|---|---|---|
| $f(x)$ | -1 | -1 | -1 |

## Exemple 5

Un parking facture un forfait unique de 12 € par jour, quel que soit le nombre d'heures de
stationnement. Écris la fonction $f(x)$ qui donne le prix payé en fonction du nombre
d'heures $x$, puis calcule $f(3)$.

**Solution :** $f(x) = 12$ (le prix ne dépend pas du nombre d'heures). Donc $f(3) = 12$ €.
"""

_CONSTANT_FUNCTION_GUIDED_EXERCISE = r"""## Énoncé

Une bibliothèque facture un abonnement annuel de 15 €, qui donne un accès illimité aux
livres pendant un an, peu importe le nombre de livres empruntés.

1. Écris la fonction $f(x)$ qui donne le prix payé en fonction du nombre de livres
   empruntés $x$.
2. Calcule $f(0)$, $f(5)$ et $f(50)$.
3. Représente cette fonction dans un tableau de valeurs pour $x = 0, 5, 10, 50$.
4. Décris à quoi ressemble le graphique de cette fonction.

## Correction détaillée

**1.** Le prix ne dépend jamais du nombre de livres empruntés : $f(x) = 15$.

**2.** Comme la fonction est constante : $f(0) = 15$, $f(5) = 15$, $f(50) = 15$. Le résultat
est toujours 15, quel que soit $x$.

**3.**

| $x$ (livres) | 0 | 5 | 10 | 50 |
|---|---|---|---|---|
| $f(x)$ (€) | 15 | 15 | 15 | 15 |

**4.** Le graphique est une droite horizontale qui coupe l'axe vertical à la hauteur 15.
"""

_CONSTANT_FUNCTION_MEMO = r"""# Fiche mémo — Fonction constante

**Définition**

$$f(x) = p$$

où $p$ est un nombre réel fixe. Le résultat ne dépend jamais de $x$.

**Graphique**

Toujours une droite **horizontale**, qui coupe l'axe des $y$ en $p$.

**Méthodes**

- Calculer une image : $f(x) = p$, peu importe $x$.
- Retrouver $p$ à partir d'un point du graphique : $p$ est la coordonnée verticale du point.
- Compléter un tableau de valeurs : toutes les valeurs de $f(x)$ sont égales à $p$.

**Erreurs fréquentes**

- Confondre avec $f(x) = x$ (la fonction identité).
- Oublier que $p$ peut être négatif ou nul.

<div class="d-print-none mt-3">
    <button type="button" class="btn btn-outline-dark btn-sm" onclick="window.print()">
        Imprimer cette fiche
    </button>
</div>
"""

_CONSTANT_FUNCTION_QUIZ_GROUP = "fonction-constante"

_CONSTANT_FUNCTION_QUIZ_QUESTIONS = [
    {
        "question": "Quelle est la forme générale d'une fonction constante ?",
        "choices": ["f(x) = x", "f(x) = p", "f(x) = mx + p", "f(x) = 2x"],
        "correct_index": 1,
        "explanation": "Une fonction constante s'écrit f(x) = p, où p est un nombre fixe.",
    },
    {
        "question": "Soit f(x) = 9. Calcule f(20).",
        "answer_type": "numeric",
        "correct_value": "9",
        "explanation": "f(x) = 9 pour tout x, donc f(20) = 9.",
    },
    {
        "question": "Le graphique d'une fonction constante est toujours une droite horizontale.",
        "choices": ["Vrai", "Faux"],
        "correct_index": 0,
        "explanation": (
            "f(x) ne change jamais, donc y = p pour tout x : c'est une droite horizontale."
        ),
    },
    {
        "question": (
            "Le graphique d'une fonction constante passe par le point (3, -6). "
            "Quelle est la valeur de p ?"
        ),
        "answer_type": "numeric",
        "correct_value": "-6",
        "explanation": "Pour une fonction constante, le point donne directement p = -6.",
    },
    {
        "question": "Laquelle de ces fonctions n'est PAS une fonction constante ?",
        "choices": ["f(x) = 4", "f(x) = -1", "f(x) = 2x", "f(x) = 0"],
        "correct_index": 2,
        "explanation": "f(x) = 2x dépend de x, ce n'est pas une fonction constante.",
    },
    {
        "question": "p peut être un nombre négatif dans f(x) = p.",
        "choices": ["Vrai", "Faux"],
        "correct_index": 0,
        "explanation": "p peut être n'importe quel nombre réel, y compris négatif ou nul.",
    },
    {
        "question": (
            "Un trajet en bus coûte toujours 2 € quel que soit le nombre d'arrêts. "
            "Si f(x) est le prix en fonction du nombre d'arrêts x, que vaut f(7) ?"
        ),
        "answer_type": "numeric",
        "correct_value": "2",
        "explanation": "Le prix ne dépend pas du nombre d'arrêts : f(x) = 2, donc f(7) = 2.",
    },
    {
        "question": (
            "Le tableau suivant correspond à quelle fonction ?\n\n"
            "| $x$ | -1 | 0 | 1 |\n"
            "|---|---|---|---|\n"
            "| $f(x)$ | 4 | 4 | 4 |"
        ),
        "choices": ["f(x) = x + 4", "f(x) = 4", "f(x) = 4x", "f(x) = -4"],
        "correct_index": 1,
        "explanation": "f(x) reste égal à 4 quel que soit x : c'est f(x) = 4.",
    },
    {
        "question": "La fonction f(x) = 0 n'est pas une fonction constante car elle vaut zéro.",
        "choices": ["Vrai", "Faux"],
        "correct_index": 1,
        "explanation": "f(x) = 0 EST bien une fonction constante (avec p = 0) : cas valide.",
    },
    {
        "question": "Soit f(x) = -3,5. Calcule f(0) + f(1).",
        "answer_type": "numeric",
        "correct_value": "-7",
        "explanation": "f(0) = -3,5 et f(1) = -3,5, donc f(0) + f(1) = -7.",
    },
]

UAA1_BLOCKS = [
    {
        "title": "Plan de l'UAA",
        "type": BlockType.MARKDOWN,
        "content": (
            "# Tableaux, graphiques, formules\n\n"
            "Dans cette UAA, tu vas apprendre à traiter un problème en choisissant l'outil "
            "le plus adapté : un tableau de nombres, un graphique, ou une formule.\n\n"
            "## Sommaire\n\n"
            "1. Lire un tableau, un graphique, une formule\n"
            "2. Fonction constante\n"
            "3. Construire un tableau et un graphique\n"
            "4. Intersection de deux fonctions\n"
            "5. Puissances et notation scientifique\n"
            "6. Proportionnalité inverse et croissance exponentielle\n"
            "7. Intérêts simples et composés\n"
            "8. Choisir le bon outil\n\n"
            "*Cette page est en cours de construction : les sections seront complétées "
            "progressivement. La section 2 (Fonction constante) est terminée.*\n"
        ),
        "position": 1,
        "is_published": True,
    },
    {
        "title": "1. Lire un tableau, un graphique, une formule",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Lire un tableau de nombres\n"
            "- Lire un graphique\n"
            "- Comprendre une formule\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 2,
        "is_published": False,
    },
    {
        "title": "Fonction constante — Présentation et objectifs",
        "type": BlockType.MARKDOWN,
        "content": _CONSTANT_FUNCTION_PRESENTATION,
        "position": 3,
        "is_published": True,
    },
    {
        "title": "Fonction constante — Cours",
        "type": BlockType.MARKDOWN,
        "content": _CONSTANT_FUNCTION_COURSE,
        "position": 4,
        "is_published": True,
    },
    {
        "title": "Fonction constante — Graphique interactif",
        "type": BlockType.MARKDOWN,
        "content": _CONSTANT_FUNCTION_GRAPH,
        "position": 5,
        "is_published": True,
    },
    {
        "title": "Fonction constante — Exemples résolus",
        "type": BlockType.MARKDOWN,
        "content": _CONSTANT_FUNCTION_EXAMPLES,
        "position": 6,
        "is_published": True,
    },
    {
        "title": "Fonction constante — Exercice guidé",
        "type": BlockType.MARKDOWN,
        "content": _CONSTANT_FUNCTION_GUIDED_EXERCISE,
        "position": 7,
        "is_published": True,
    },
    {
        "title": "Fonction constante — Exercices automatiques",
        "type": BlockType.GENERATED_EXERCISE,
        "content": ExerciseBlockConfig(
            generator="maths.functions.constant_function",
            difficulty=1,
            count=3,
            tags=["fonctions", "fonction constante"],
        ).to_json(),
        "position": 8,
        "is_published": True,
    },
    *[
        {
            "title": f"Fonction constante — Quiz {index + 1}/10",
            "type": BlockType.QUIZ,
            "content": QuizConfig(
                question=q["question"],
                choices=q.get("choices", []),
                correct_index=q.get("correct_index", 0),
                explanation=q["explanation"],
                answer_type=q.get("answer_type", "choice"),
                correct_value=q.get("correct_value", ""),
                group=_CONSTANT_FUNCTION_QUIZ_GROUP,
                order_in_group=index + 1,
            ).to_json(),
            "position": 9 + index,
            "is_published": True,
        }
        for index, q in enumerate(_CONSTANT_FUNCTION_QUIZ_QUESTIONS)
    ],
    {
        "title": "Fonction constante — Fiche mémo",
        "type": BlockType.MARKDOWN,
        "content": _CONSTANT_FUNCTION_MEMO,
        "position": 19,
        "is_published": True,
    },
    {
        "title": "3. Construire un tableau et un graphique",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Construire un tableau de valeurs\n"
            "- Construire un graphique à partir d'un tableau ou d'une formule\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 20,
        "is_published": False,
    },
    {
        "title": "4. Intersection de deux fonctions",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Intersection de deux fonctions constantes ou du premier degré\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 21,
        "is_published": False,
    },
    {
        "title": "5. Puissances et notation scientifique",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Puissances à exposant entier\n"
            "- Notation scientifique\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 22,
        "is_published": False,
    },
    {
        "title": "6. Proportionnalité inverse et croissance exponentielle",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Proportionnalité inverse\n"
            "- Croissance exponentielle\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 23,
        "is_published": False,
    },
    {
        "title": "7. Intérêts simples et composés",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Intérêt simple\n"
            "- Intérêt composé\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 24,
        "is_published": False,
    },
    {
        "title": "8. Choisir le bon outil",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Choix de l'outil pertinent : tableau, graphique ou formule\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 25,
        "is_published": False,
    },
]

# Contenu réel de MB32 UAA2 (Géométrie), importé depuis
# docs/sources_cours/CESS/P/Mathématiques/MB32/UAA2/cours.html (source officielle, non
# modifiée). Découpage en 6 leçons, conforme à docs/content_workflow.md et
# docs/REFERENCE_UAA.md : Solides, Perspective cavalière, Patrons, Vues coordonnées, Aires,
# Volumes. Tout le contenu du cours est repris (théorie, exemples, exercices, corrections,
# mini-test, fiche mémo, ressources), sans résumé ni reformulation.

_UAA2_PLAN = r"""# Géométrie

Objectif de l'UAA : apprendre à représenter dans le plan des objets de l'espace, associer un
solide à ses représentations planes, utiliser les patrons, les vues coordonnées, la
perspective cavalière, et calculer des longueurs, des aires et des volumes.

Contenu couvert : solides usuels, perspective cavalière, développements/patrons, vues
coordonnées, aires et volumes. Pas de statistique, pas de fonctions, pas de probabilités.

## Sommaire

1. Solides
2. Perspective cavalière
3. Patrons
4. Vues coordonnées
5. Aires
6. Volumes

À la fin de l'UAA : un mini-test final type examen, une fiche mémo récapitulative et des
ressources pour réviser.
"""

_SOLIDES_PRESENTATION = r"""# Solides

## Ce qu'il faut savoir faire à l'examen

| Processus | Ce qu'on attend de toi | Exemples de tâches |
|---|---|---|
| **Connaître** | Reconnaître, nommer, décrire. | Identifier un cylindre, une pyramide, une sphère ; donner faces, arêtes, sommets ; choisir l'unité correcte. |
| **Appliquer** | Utiliser une méthode entraînée. | Calculer le volume d'une cuve cylindrique ; dessiner un patron ; faire une perspective cavalière. |
| **Transférer** | Choisir soi-même la méthode dans une situation réelle. | Calculer le prix de remplissage d'une cuve, associer vue de face/vue de dessus/patron, vérifier si un résultat est plausible. |
"""

_SOLIDES_COURSE = r"""## Vocabulaire de base

Un **solide** est un objet en trois dimensions : longueur, largeur/profondeur, hauteur.

Une **face** est une surface plane ou courbe qui limite le solide.

Une **arête** est un segment où deux faces se rencontrent.

Un **sommet** est un point où plusieurs arêtes se rencontrent.

## Les solides à connaître

| Solide | Type | Faces / surface | À retenir |
|---|---|---|---|
| Cube | Polyèdre | 6 faces carrées | Toutes les arêtes ont la même longueur. |
| Parallélépipède rectangle | Polyèdre | 6 faces rectangulaires | Boîte, brique, carton. |
| Prisme | Polyèdre | 2 bases identiques + faces latérales | Les bases sont parallèles. |
| Pyramide | Polyèdre | 1 base + faces triangulaires | Les faces latérales se rejoignent en un sommet. |
| Cylindre | Non-polyèdre | 2 disques + surface latérale courbe | Boîte de conserve, cuve. |
| Cône | Non-polyèdre | 1 disque + surface latérale courbe | Base circulaire et sommet. |
| Sphère | Non-polyèdre | Surface courbe uniquement | Balle, globe. |

> **Piège fréquent :** un cylindre, un cône et une sphère ne sont pas des polyèdres, car ils
> possèdent des surfaces courbes.

## Les unités : longueurs, aires, volumes

| Grandeur | Unité | Exemples | Conversion importante |
|---|---|---|---|
| Longueur | m, cm, mm | rayon, diamètre, hauteur | 1 m = 100 cm |
| Aire | m², cm² | surface à peindre, surface d'un patron | 1 m² = 10 000 cm² |
| Volume | m³, cm³, L | contenance d'une cuve | 1 m³ = 1000 L ; 1 L = 1 dm³ |

> **Piège majeur :** ne mélange jamais cm et m dans une même formule. Convertis tout dans la
> même unité avant de calculer.
"""

_SOLIDES_EXAMPLES = r"""## Exemple corrigé 1 — identifier un solide

**Énoncé :** Un objet possède deux bases circulaires identiques et parallèles, reliées par
une surface courbe. Quel est ce solide ?

**Correction :**

1. Bases circulaires : ce n'est pas un prisme à base polygonale.
2. Deux bases parallèles : ce n'est pas un cône, qui n'a qu'une base.
3. Surface latérale courbe : ce n'est pas un polyèdre.

**Réponse :** c'est un cylindre.
"""

_SOLIDES_EXERCISES = r"""## Exercice — connaître

Pour chaque description, indique le solide :

<ol class="jc-list-alpha">
<li>Une seule base circulaire et un sommet.</li>
<li>Une seule surface courbe, aucun sommet, aucune arête.</li>
<li>Deux bases triangulaires parallèles et trois faces rectangulaires.</li>
<li>Une base carrée et quatre faces triangulaires.</li>
</ol>

## Exercice 1 — connaître

Donne le nom du solide :

<ol class="jc-list-alpha">
<li>deux bases circulaires parallèles ;</li>
<li>une base circulaire et un sommet ;</li>
<li>six faces rectangulaires ;</li>
<li>une surface courbe unique.</li>
</ol>

**Correction :** a) cylindre ; b) cône ; c) parallélépipède rectangle ; d) sphère.

## Exercice 2 — connaître

Explique la différence entre un polyèdre et un non-polyèdre.

**Correction :** Un polyèdre est limité uniquement par des faces planes. Un non-polyèdre
possède au moins une surface courbe. Exemple : cube = polyèdre ; cylindre = non-polyèdre.

## Exercice 3 — connaître

Dans quelle unité exprime-t-on une aire ? un volume ? une longueur ?

**Correction :** Longueur : m, cm, mm. Aire : m², cm². Volume : m³, cm³, L.
"""

_SOLIDES_QUIZ_GROUP = "geometrie-solides"
_SOLIDES_QUIZ_QUESTIONS = [
    {
        "question": (
            "Un objet a deux bases circulaires parallèles reliées par une surface courbe. "
            "Quel est ce solide ?"
        ),
        "choices": ["Cône", "Cylindre", "Sphère", "Prisme"],
        "correct_index": 1,
        "explanation": (
            "Deux bases parallèles écarte le cône, la surface latérale courbe écarte les "
            "polyèdres : c'est un cylindre."
        ),
    },
    {
        "question": "Un cylindre, un cône et une sphère sont des polyèdres.",
        "choices": ["Vrai", "Faux"],
        "correct_index": 1,
        "explanation": "Ils possèdent des surfaces courbes, ils ne sont donc pas des polyèdres.",
    },
    {
        "question": "Dans quelle unité exprime-t-on un volume ?",
        "choices": ["m", "m²", "m³", "kg"],
        "correct_index": 2,
        "explanation": "Le volume s'exprime en m³, cm³ ou en litres.",
    },
]

_PERSPECTIVE_PRESENTATION = r"""# Perspective cavalière

La **perspective cavalière** est une façon de représenter un solide 3D sur une feuille 2D.
Elle garde la face avant en vraie grandeur. Les arêtes qui partent vers la profondeur sont
tracées inclinées, souvent à 45°, et parfois réduites.
"""

_PERSPECTIVE_COURSE = r"""## Vocabulaire

- **Plan frontal :** face dessinée de face, en vraie grandeur.
- **Fuyantes :** arêtes qui partent vers l'arrière.
- **Coefficient de réduction :** nombre qui réduit la longueur des fuyantes, souvent 1/2.
- **Arêtes cachées :** arêtes non visibles, dessinées en pointillés.

<svg width="650" height="330" viewBox="0 0 650 330" role="img" aria-label="Parallélépipède en perspective cavalière">
<rect x="110" y="110" width="230" height="130" fill="none" stroke="#222" stroke-width="3"/>
<line x1="110" y1="110" x2="200" y2="60" stroke="#222" stroke-width="3"/>
<line x1="340" y1="110" x2="430" y2="60" stroke="#222" stroke-width="3"/>
<line x1="340" y1="240" x2="430" y2="190" stroke="#222" stroke-width="3"/>
<line x1="200" y1="60" x2="430" y2="60" stroke="#222" stroke-width="3"/>
<line x1="430" y1="60" x2="430" y2="190" stroke="#222" stroke-width="3"/>
<line x1="200" y1="60" x2="200" y2="190" stroke="#999" stroke-width="2" stroke-dasharray="6 6"/>
<line x1="200" y1="190" x2="430" y2="190" stroke="#999" stroke-width="2" stroke-dasharray="6 6"/>
<line x1="110" y1="240" x2="200" y2="190" stroke="#999" stroke-width="2" stroke-dasharray="6 6"/>
<text x="140" y="270" font-size="16">face frontale en vraie grandeur</text>
<text x="445" y="120" font-size="16">fuyantes</text>
<text x="205" y="205" font-size="16" fill="#777">arêtes cachées</text>
</svg>

## Méthode : dessiner un parallélépipède rectangle en perspective cavalière

1. Dessiner la face avant en vraie grandeur.
2. Depuis trois sommets visibles, tracer des fuyantes parallèles, souvent à 45°.
3. Réduire la profondeur si demandé, par exemple profondeur × 1/2.
4. Relier les extrémités des fuyantes.
5. Mettre les arêtes cachées en pointillés.

> **Pièges fréquents :** les angles ne sont pas toujours conservés ; seules les longueurs
> dans le plan frontal sont en vraie grandeur. Les arêtes parallèles dans le solide restent
> parallèles sur le dessin.
"""

_PERSPECTIVE_QUIZ_GROUP = "geometrie-perspective-cavaliere"
_PERSPECTIVE_QUIZ_QUESTIONS = [
    {
        "question": (
            "Dans la perspective cavalière, quelle partie du solide est représentée en "
            "vraie grandeur ?"
        ),
        "choices": ["La face arrière", "La face frontale", "Les fuyantes", "Aucune"],
        "correct_index": 1,
        "explanation": "La face frontale est dessinée de face, en vraie grandeur.",
    },
    {
        "question": "Les arêtes cachées sont dessinées en pointillés.",
        "choices": ["Vrai", "Faux"],
        "correct_index": 0,
        "explanation": "Les arêtes non visibles se dessinent en pointillés.",
    },
]

_PATRONS_PRESENTATION = r"""# Patrons

Un **patron** ou **développement** est une figure plane que l'on peut découper et plier pour
reconstituer un solide.
"""

_PATRONS_COURSE = r"""## Patrons à connaître

| Solide | Patron |
|---|---|
| Cube | 6 carrés identiques. |
| Parallélépipède rectangle | 6 rectangles, opposés deux à deux identiques. |
| Prisme droit | 2 bases identiques + rectangles latéraux. |
| Pyramide | 1 base + triangles autour de la base. |
| Cylindre | 2 disques + 1 rectangle dont une dimension est le périmètre du disque. |
| Cône | 1 disque + 1 secteur circulaire. |
"""

_PATRONS_EXAMPLES = r"""## Exemple corrigé 2 — patron d'un cylindre

**Énoncé :** Un cylindre a un rayon de 4 cm et une hauteur de 10 cm. Quelles sont les
dimensions du rectangle dans son patron ?

**Correction :**

Le patron d'un cylindre contient deux disques et un rectangle.

La hauteur du rectangle est la hauteur du cylindre : $10$ cm.

La longueur du rectangle est le périmètre du disque : $2\pi r = 2 \times \pi \times 4 = 8\pi
\approx 25{,}1$ cm.

**Réponse :** rectangle de 10 cm sur environ 25,1 cm.
"""

_PATRONS_EXERCISES = r"""## Exercice 7 — appliquer

Un cylindre a un rayon de 3 cm et une hauteur de 8 cm. Donne les dimensions du rectangle de
son patron.

**Correction :** Rectangle du patron : hauteur = 8 cm ; longueur = périmètre du disque =
$2\pi r = 2\pi \times 3 = 6\pi \approx 18{,}8$ cm.
"""

_PATRONS_QUIZ_GROUP = "geometrie-patrons"
_PATRONS_QUIZ_QUESTIONS = [
    {
        "question": (
            "Un cylindre a un rayon de 3 cm et une hauteur de 8 cm. Quelle est, parmi ces "
            "valeurs, la longueur du rectangle de son patron ?"
        ),
        "choices": ["8 cm", "18,8 cm", "25,1 cm", "6 cm"],
        "correct_index": 1,
        "explanation": "Longueur = 2πr = 2π × 3 ≈ 18,8 cm.",
    },
    {
        "question": "Le patron d'un cône est composé de...",
        "choices": [
            "2 disques et 1 rectangle",
            "1 disque et 1 secteur circulaire",
            "6 carrés",
            "1 base et des triangles",
        ],
        "correct_index": 1,
        "explanation": "Un cône se développe en un disque (la base) et un secteur circulaire.",
    },
]

_VUES_PRESENTATION = r"""# Vues coordonnées

Les **vues coordonnées** sont les projections orthogonales d'un objet : vue de face, vue de
dessus, vue de côté/profil. Dans ces vues, les dimensions sont représentées en vraie grandeur
sur le plan choisi.
"""

_VUES_COURSE = r"""## Les trois vues

| Vue | Ce qu'on voit | Exemple pour un cylindre horizontal |
|---|---|---|
| Vue de face | largeur × hauteur | un cercle ou un rectangle selon l'orientation |
| Vue de dessus | longueur × profondeur | souvent un rectangle |
| Vue de profil | profondeur × hauteur | un cercle si on regarde la base |

## Méthode pour associer un solide à ses vues

1. Repérer la forme générale : boîte, cylindre, pyramide, cône...
2. Chercher les faces visibles dans chaque direction.
3. Comparer les dimensions : hauteur, largeur, profondeur.
4. Vérifier si la vue contient des cercles, rectangles, triangles.
5. Écarter les vues impossibles.
"""

_AIRES_PRESENTATION = r"""# Aires

Cette leçon rassemble les formules d'aires planes et d'aires totales de solides, ainsi que
des exemples et exercices d'application.
"""

_AIRES_COURSE = r"""## Aires planes utiles

| Figure | Formule | Signification |
|---|---|---|
| Rectangle | $A = L \times l$ | longueur × largeur |
| Carré | $A = c^2$ | côté × côté |
| Triangle | $A = \dfrac{\text{base} \times \text{hauteur}}{2}$ | moitié du rectangle correspondant |
| Disque | $A = \pi r^2$ | r = rayon |
| Cercle : périmètre | $P = 2\pi r = \pi D$ | D = diamètre |

## Aires totales courantes

| Solide | Aire totale | À comprendre |
|---|---|---|
| Cube | $A = 6c^2$ | 6 faces carrées |
| Parallélépipède rectangle | $A = 2(Ll + Lh + lh)$ | faces opposées identiques |
| Cylindre | $A = 2\pi r^2 + 2\pi rh$ | 2 disques + rectangle enroulé |
| Sphère | $A = 4\pi r^2$ | surface courbe complète |
"""

_AIRES_EXAMPLES = r"""## Exemple corrigé 6 — surface d'un cylindre fermé

**Énoncé :** Une boîte cylindrique fermée a un rayon de 6 cm et une hauteur de 15 cm.
Calcule l'aire totale.

**Correction :**

Aire totale d'un cylindre fermé : $A = 2\pi r^2 + 2\pi rh$

Aire des deux bases : $2\pi \times 6^2 = 72\pi$

Aire latérale : $2\pi \times 6 \times 15 = 180\pi$

Total : $252\pi \approx 791{,}7$ cm²

**Réponse :** environ 791,7 cm².
"""

_AIRES_EXERCISES = r"""## Exercice 6 — appliquer

Calcule l'aire totale d'un cube de côté 4 cm.

**Correction :** Cube : 6 faces carrées. $A = 6c^2 = 6 \times 4^2 = 6 \times 16 = 96$ cm².

## Exercice 8 — transférer

Une entreprise veut peindre une cuve cylindrique fermée de rayon 0,5 m et de longueur 3 m.
Un pot de peinture couvre 4 m². Combien de pots faut-il acheter ?

**Correction :**

Cuve fermée = cylindre fermé. $A = 2\pi r^2 + 2\pi rh$

$A = 2\pi \times 0{,}5^2 + 2\pi \times 0{,}5 \times 3 = 0{,}5\pi + 3\pi = 3{,}5\pi \approx
11{,}0$ m².

Un pot couvre 4 m² : $11{,}0 / 4 = 2{,}75$. Il faut acheter 3 pots, car on ne peut pas
acheter 2,75 pots.
"""

_AIRES_QUIZ_GROUP = "geometrie-aires"
_AIRES_QUIZ_QUESTIONS = [
    {
        "question": "Calcule l'aire totale d'un cube de côté 4 cm (en cm²).",
        "answer_type": "numeric",
        "correct_value": "96",
        "explanation": "A = 6c² = 6 × 4² = 96 cm².",
    },
    {
        "question": (
            "Une boîte cylindrique fermée a un rayon de 6 cm et une hauteur de 15 cm. "
            "Quelle est son aire totale approximative ?"
        ),
        "choices": ["252 cm²", "471,2 cm²", "791,7 cm²", "1130,4 cm²"],
        "correct_index": 2,
        "explanation": "A = 2πr² + 2πrh = 72π + 180π = 252π ≈ 791,7 cm².",
    },
    {
        "question": "L'aire totale d'une sphère de rayon r est donnée par...",
        "choices": ["4πr²", "πr²", "2πr²", "4/3 πr³"],
        "correct_index": 0,
        "explanation": "L'aire d'une sphère est A = 4πr² (le dernier choix est son volume).",
    },
]

_VOLUMES_PRESENTATION = r"""# Volumes

Cette leçon rassemble les formules de volumes des solides usuels, des exemples résolus, des
exercices d'application et un problème de transfert (facture de mazout).
"""

_VOLUMES_COURSE = r"""## Volumes

| Solide | Volume | Remarque |
|---|---|---|
| Cube | $V = c^3$ | c = côté |
| Parallélépipède rectangle | $V = L \times l \times h$ | longueur × largeur × hauteur |
| Prisme | $V = \text{aire de la base} \times \text{hauteur}$ | fonctionne pour tout prisme droit |
| Cylindre | $V = \pi r^2 h$ | h = longueur/hauteur du cylindre |
| Pyramide | $V = \dfrac{\text{aire de la base} \times \text{hauteur}}{3}$ | hauteur perpendiculaire à la base |
| Cône | $V = \dfrac{\pi r^2 h}{3}$ | un tiers du cylindre correspondant |
| Sphère | $V = \dfrac{4}{3}\pi r^3$ | r = rayon |
"""

_VOLUMES_EXAMPLES = r"""## Exemple corrigé 3 — volume d'une cuve cylindrique

**Énoncé :** Une cuve cylindrique horizontale mesure 2 m de long. Son diamètre est 1,2 m.
On la remplit à 95 %. Combien de litres contient-elle ?

**Correction :**

1. Identifier le solide : cylindre.
2. Formule : $V = \pi r^2 h$
3. Rayon : diamètre / 2 = 1,2 / 2 = 0,6 m.
4. Volume total : $V = \pi \times 0{,}6^2 \times 2 = \pi \times 0{,}36 \times 2 = 0{,}72\pi
   \approx 2{,}262$ m³.
5. Remplissage à 95 % : $2{,}262 \times 0{,}95 \approx 2{,}149$ m³.
6. Conversion en litres : $2{,}149 \text{ m}^3 \times 1000 \approx 2149$ L.

**Réponse :** environ 2149 litres.

## Exemple corrigé 4 — volume d'un cône

**Énoncé :** Un cône a un rayon de 3 cm et une hauteur de 12 cm. Calcule son volume.

**Correction :**

Formule : $V = \dfrac{\pi r^2 h}{3}$

Calcul : $V = \dfrac{\pi \times 3^2 \times 12}{3} = \dfrac{\pi \times 9 \times 12}{3} = 36\pi
\approx 113{,}1$ cm³.

**Réponse :** environ 113,1 cm³.

## Exemple corrigé 5 — volume d'une sphère

**Énoncé :** Une boule a un rayon de 5 cm. Calcule son volume.

**Correction :**

Formule : $V = \dfrac{4}{3}\pi r^3$

Calcul : $V = \dfrac{4}{3} \times \pi \times 5^3 = \dfrac{4}{3} \times \pi \times 125 \approx
523{,}6$ cm³.

**Réponse :** environ 523,6 cm³.
"""

_VOLUMES_TRANSFER = r"""## Choisir la bonne méthode (problèmes de transfert)

Pour résoudre un problème contextualisé :

1. Lire la question finale : que demande-t-on ? longueur, aire, volume, prix ?
2. Identifier le solide ou l'assemblage de solides.
3. Relever les données utiles et convertir les unités.
4. Choisir la formule.
5. Calculer étape par étape.
6. Donner une phrase-réponse avec l'unité.
7. Vérifier si le résultat est plausible.

## Exemple corrigé 7 — facture de mazout

**Énoncé :** Une cuve cylindrique de longueur 2 m et de diamètre 1,2 m est remplie à 95 %.
Le prix est de 0,7133 €/L si la commande est inférieure à 2000 L et de 0,6848 €/L si elle
dépasse 2000 L. Quel est le prix approximatif ?

**Correction :**

On reprend le volume trouvé plus haut : environ 2149 L.

Comme 2149 L > 2000 L, on utilise le prix de 0,6848 €/L.

Prix : $2149 \times 0{,}6848 \approx 1471{,}6$ €.

**Réponse :** la facture sera d'environ 1471,6 €.
"""

_VOLUMES_EXERCISES = r"""## Exercice 4 — appliquer

Calcule le volume d'un parallélépipède rectangle de dimensions 8 cm, 5 cm et 3 cm.

**Correction :** $V = L \times l \times h = 8 \times 5 \times 3 = 120$ cm³.

## Exercice 5 — appliquer

Calcule le volume d'un cylindre de rayon 2 m et de hauteur 7 m.

**Correction :** $V = \pi r^2 h = \pi \times 2^2 \times 7 = 28\pi \approx 88{,}0$ m³.

## Exercice 9 — transférer

Une pyramide à base carrée a une base de côté 6 cm et une hauteur de 10 cm. Calcule son
volume et explique pourquoi on divise par 3.

**Correction :**

Aire de la base : $6 \times 6 = 36$ cm².

Volume : $V = \dfrac{A_{base} \times h}{3} = \dfrac{36 \times 10}{3} = 120$ cm³.

On divise par 3 car une pyramide occupe un tiers du volume du prisme de même base et même
hauteur.

## Exercice 10 — transférer

Un objet est composé d'un cylindre de rayon 4 cm et de hauteur 10 cm surmonté d'un cône de
même rayon et de hauteur 6 cm. Calcule le volume total.

**Correction :**

Cylindre : $V = \pi \times 4^2 \times 10 = 160\pi$.

Cône : $V = \dfrac{\pi \times 4^2 \times 6}{3} = 32\pi$.

Total : $192\pi \approx 603{,}2$ cm³.
"""

_VOLUMES_QUIZ_GROUP = "geometrie-volumes"
_VOLUMES_QUIZ_QUESTIONS = [
    {
        "question": (
            "Calcule le volume (en cm³) d'un parallélépipède rectangle de dimensions "
            "8 cm, 5 cm et 3 cm."
        ),
        "answer_type": "numeric",
        "correct_value": "120",
        "explanation": "V = L × l × h = 8 × 5 × 3 = 120 cm³.",
    },
    {
        "question": (
            "Un cône a un rayon de 3 cm et une hauteur de 12 cm. Quel est son volume "
            "approximatif ?"
        ),
        "choices": ["36 cm³", "113,1 cm³", "339,3 cm³", "452,4 cm³"],
        "correct_index": 1,
        "explanation": "V = (πr²h)/3 = (π × 9 × 12)/3 = 36π ≈ 113,1 cm³.",
    },
    {
        "question": "Le volume d'une sphère de rayon r est donné par...",
        "choices": ["4/3 πr³", "πr²h", "4πr²", "πr²h/3"],
        "correct_index": 0,
        "explanation": "Le volume d'une sphère est V = (4/3)πr³.",
    },
]

_UAA2_MINI_TEST = r"""# Mini-test final type examen

**Consigne :** toutes les réponses doivent être justifiées. Une réponse numérique sans
méthode peut être refusée.

## Question 1 — Connaître

Complète le tableau.

| Solide | Polyèdre ou non-polyèdre ? | Une caractéristique |
|---|---|---|
| Cylindre | | |
| Pyramide | | |
| Sphère | | |
| Prisme | | |

## Question 2 — Appliquer

Une cuve cylindrique a une longueur de 1,8 m et un diamètre de 1 m.

<ol class="jc-list-alpha">
<li>Calcule son volume en m³.</li>
<li>Convertis ce volume en litres.</li>
<li>Si elle est remplie à 90 %, combien de litres contient-elle ?</li>
</ol>

## Question 3 — Appliquer

Un cube a une arête de 7 cm. Calcule son volume et son aire totale.

## Question 4 — Transférer

Une citerne est composée d'un cylindre de rayon 0,8 m et de longueur 2,5 m. Elle doit être
peinte entièrement. Un pot couvre 5 m² et coûte 28 €. Calcule le coût minimum de peinture à
prévoir.

## Question 5 — Représentation

Explique comment construire la perspective cavalière d'un parallélépipède rectangle. Ta
réponse doit mentionner la face frontale, les fuyantes, le coefficient de réduction et les
arêtes cachées.

---

## Correction du mini-test

**Question 1**

Cylindre : non-polyèdre, deux bases circulaires et surface courbe.

Pyramide : polyèdre, une base et des faces triangulaires.

Sphère : non-polyèdre, surface courbe unique.

Prisme : polyèdre, deux bases identiques et parallèles.

**Question 2**

Rayon : 1 / 2 = 0,5 m.

Volume : $V = \pi r^2 h = \pi \times 0{,}5^2 \times 1{,}8 = 0{,}45\pi \approx 1{,}4$ m³.

En litres : $1{,}4 \times 1000 \approx 1413{,}7$ L.

À 90 % : $1413{,}7 \times 0{,}9 \approx 1272{,}3$ L.

**Question 3**

Volume : $V = 7^3 = 343$ cm³.

Aire totale : $A = 6 \times 7^2 = 6 \times 49 = 294$ cm².

**Question 4**

Aire cylindre fermé : $A = 2\pi r^2 + 2\pi rh$.

$A = 2\pi \times 0{,}8^2 + 2\pi \times 0{,}8 \times 2{,}5 = 1{,}28\pi + 4\pi = 5{,}28\pi
\approx 16{,}6$ m².

Nombre de pots : $16{,}6 / 5 = 3{,}32$, donc 4 pots.

Coût : $4 \times 28 = 112$ €.

**Question 5**

On dessine d'abord la face frontale en vraie grandeur. Depuis les sommets, on trace des
fuyantes parallèles, souvent inclinées à 45°. Si un coefficient de réduction est donné, on
réduit la longueur des fuyantes. On relie les extrémités pour former la face arrière. Les
arêtes cachées sont tracées en pointillés.
"""

_UAA2_MEMO = r"""# Fiche mémo — Géométrie

## Définitions

- **Solide :** objet en 3 dimensions.
- **Polyèdre :** solide limité uniquement par des faces planes.
- **Patron :** développement à plat d'un solide.
- **Perspective cavalière :** représentation plane d'un solide avec face frontale en vraie
  grandeur et fuyantes parallèles.
- **Vues coordonnées :** vues de face, de dessus et de profil.

## Formules essentielles

| Objet | Formule |
|---|---|
| Disque | $A = \pi r^2$ |
| Cercle | $P = 2\pi r = \pi D$ |
| Parallélépipède rectangle | $V = L \times l \times h$ |
| Prisme | $V = \text{aire de base} \times \text{hauteur}$ |
| Cylindre | $V = \pi r^2 h$ |
| Pyramide | $V = \text{aire de base} \times \text{hauteur} / 3$ |
| Cône | $V = \pi r^2 h / 3$ |
| Sphère | $V = 4\pi r^3 / 3$ ; $A = 4\pi r^2$ |

## Procédure examen

1. Identifier le solide.
2. Repérer les données utiles.
3. Convertir les unités.
4. Choisir la formule.
5. Calculer proprement.
6. Arrondir si nécessaire.
7. Écrire une phrase-réponse avec unité.
8. Vérifier la plausibilité du résultat.

<div class="d-print-none mt-3">
    <button type="button" class="btn btn-outline-dark btn-sm" onclick="window.print()">
        Imprimer cette fiche
    </button>
</div>
"""

_UAA2_RESOURCES = r"""# Ressources pour réviser

- [YouTube – volumes cylindre, cône, sphère exercices](https://www.youtube.com/results?search_query=volume+cylindre+c%C3%B4ne+sph%C3%A8re+exercices)
- [YouTube – perspective cavalière en mathématiques](https://www.youtube.com/results?search_query=perspective+cavali%C3%A8re+maths)
- [YouTube – patrons de solides](https://www.youtube.com/results?search_query=patron+d%27un+solide+maths)
- [Khan Academy – solides, volumes et aires](https://fr.khanacademy.org/math/geometry/hs-geo-solids)
- [Alloprof – les solides](https://www.alloprof.qc.ca/fr/eleves/bv/mathematiques/les-solides-m1251)
"""


def _quiz_blocks(
    questions: list[dict], group: str, title_prefix: str, start_position: int
) -> list[dict]:
    """Construit une série de LessonBlock de type quiz à partir de questions brutes."""
    return [
        {
            "title": f"{title_prefix} — Quiz {index + 1}/{len(questions)}",
            "type": BlockType.QUIZ,
            "content": QuizConfig(
                question=q["question"],
                choices=q.get("choices", []),
                correct_index=q.get("correct_index", 0),
                explanation=q["explanation"],
                answer_type=q.get("answer_type", "choice"),
                correct_value=q.get("correct_value", ""),
                group=group,
                order_in_group=index + 1,
            ).to_json(),
            "position": start_position + index,
            "is_published": True,
        }
        for index, q in enumerate(questions)
    ]


UAA2_BLOCKS = [
    {
        "title": "Plan de l'UAA",
        "type": BlockType.MARKDOWN,
        "content": _UAA2_PLAN,
        "position": 1,
        "is_published": True,
    },
    {
        "title": "Solides — Présentation",
        "type": BlockType.MARKDOWN,
        "content": _SOLIDES_PRESENTATION,
        "position": 2,
        "is_published": True,
    },
    {
        "title": "Solides — Cours",
        "type": BlockType.MARKDOWN,
        "content": _SOLIDES_COURSE,
        "position": 3,
        "is_published": True,
    },
    {
        "title": "Solides — Exemples résolus",
        "type": BlockType.MARKDOWN,
        "content": _SOLIDES_EXAMPLES,
        "position": 4,
        "is_published": True,
    },
    {
        "title": "Solides — Exercices",
        "type": BlockType.MARKDOWN,
        "content": _SOLIDES_EXERCISES,
        "position": 5,
        "is_published": True,
    },
    *_quiz_blocks(_SOLIDES_QUIZ_QUESTIONS, _SOLIDES_QUIZ_GROUP, "Solides", 6),
    {
        "title": "Perspective cavalière — Présentation",
        "type": BlockType.MARKDOWN,
        "content": _PERSPECTIVE_PRESENTATION,
        "position": 9,
        "is_published": True,
    },
    {
        "title": "Perspective cavalière — Cours",
        "type": BlockType.MARKDOWN,
        "content": _PERSPECTIVE_COURSE,
        "position": 10,
        "is_published": True,
    },
    *_quiz_blocks(
        _PERSPECTIVE_QUIZ_QUESTIONS, _PERSPECTIVE_QUIZ_GROUP, "Perspective cavalière", 11
    ),
    {
        "title": "Patrons — Présentation",
        "type": BlockType.MARKDOWN,
        "content": _PATRONS_PRESENTATION,
        "position": 13,
        "is_published": True,
    },
    {
        "title": "Patrons — Cours",
        "type": BlockType.MARKDOWN,
        "content": _PATRONS_COURSE,
        "position": 14,
        "is_published": True,
    },
    {
        "title": "Patrons — Exemples résolus",
        "type": BlockType.MARKDOWN,
        "content": _PATRONS_EXAMPLES,
        "position": 15,
        "is_published": True,
    },
    {
        "title": "Patrons — Exercices",
        "type": BlockType.MARKDOWN,
        "content": _PATRONS_EXERCISES,
        "position": 16,
        "is_published": True,
    },
    *_quiz_blocks(_PATRONS_QUIZ_QUESTIONS, _PATRONS_QUIZ_GROUP, "Patrons", 17),
    {
        "title": "Vues coordonnées — Présentation",
        "type": BlockType.MARKDOWN,
        "content": _VUES_PRESENTATION,
        "position": 19,
        "is_published": True,
    },
    {
        "title": "Vues coordonnées — Cours",
        "type": BlockType.MARKDOWN,
        "content": _VUES_COURSE,
        "position": 20,
        "is_published": True,
    },
    {
        "title": "Aires — Présentation",
        "type": BlockType.MARKDOWN,
        "content": _AIRES_PRESENTATION,
        "position": 21,
        "is_published": True,
    },
    {
        "title": "Aires — Cours",
        "type": BlockType.MARKDOWN,
        "content": _AIRES_COURSE,
        "position": 22,
        "is_published": True,
    },
    {
        "title": "Aires — Exemples résolus",
        "type": BlockType.MARKDOWN,
        "content": _AIRES_EXAMPLES,
        "position": 23,
        "is_published": True,
    },
    {
        "title": "Aires — Exercices",
        "type": BlockType.MARKDOWN,
        "content": _AIRES_EXERCISES,
        "position": 24,
        "is_published": True,
    },
    *_quiz_blocks(_AIRES_QUIZ_QUESTIONS, _AIRES_QUIZ_GROUP, "Aires", 25),
    {
        "title": "Volumes — Présentation",
        "type": BlockType.MARKDOWN,
        "content": _VOLUMES_PRESENTATION,
        "position": 28,
        "is_published": True,
    },
    {
        "title": "Volumes — Cours",
        "type": BlockType.MARKDOWN,
        "content": _VOLUMES_COURSE,
        "position": 29,
        "is_published": True,
    },
    {
        "title": "Volumes — Exemples résolus",
        "type": BlockType.MARKDOWN,
        "content": _VOLUMES_EXAMPLES,
        "position": 30,
        "is_published": True,
    },
    {
        "title": "Volumes — Problème de transfert",
        "type": BlockType.MARKDOWN,
        "content": _VOLUMES_TRANSFER,
        "position": 31,
        "is_published": True,
    },
    {
        "title": "Volumes — Exercices",
        "type": BlockType.MARKDOWN,
        "content": _VOLUMES_EXERCISES,
        "position": 32,
        "is_published": True,
    },
    *_quiz_blocks(_VOLUMES_QUIZ_QUESTIONS, _VOLUMES_QUIZ_GROUP, "Volumes", 33),
    {
        "title": "Mini-test final — Géométrie",
        "type": BlockType.MARKDOWN,
        "content": _UAA2_MINI_TEST,
        "position": 36,
        "is_published": True,
    },
    {
        "title": "Fiche mémo — Géométrie",
        "type": BlockType.MARKDOWN,
        "content": _UAA2_MEMO,
        "position": 37,
        "is_published": True,
    },
    {
        "title": "Ressources — Géométrie",
        "type": BlockType.MARKDOWN,
        "content": _UAA2_RESOURCES,
        "position": 38,
        "is_published": True,
    },
]

# Contenu réel du mini-cours 01 Informatique AMPCR (« Architecture générale d'un PC »),
# ticket #10 : cours pilote de la série des 38 mini-cours Informatique. Contenu et
# périmètre pédagogique fournis par ChatGPT (chef de projet), rédigés ici sans en changer
# la portée. Réutilise exactement les mêmes mécanismes que MB32 (blocs markdown, cartes
# classées par titre via app/card_kind.py, correction masquée générique via
# app/static/js/design_system.js::splitExerciseCorrections) — aucune architecture
# spécifique à ce cours.

INFORMATIQUE_SUBJECT_NAME = "Informatique"
INFORMATIQUE_MODULE_CODES = ["AMPCR"]

MC01_CODE = "MC01"
MC01_TITLE = "Architecture générale d'un PC"

_MC01_PLAN = r"""# Architecture générale d'un PC

Ce mini-cours est le premier d'une série consacrée à la formation Assistant/Assistante de
maintenance PC-réseaux (AMPCR). Il pose les bases : de quoi un ordinateur est-il fait, à
quoi sert chaque composant, et comment ces composants collaborent lorsque tu utilises ton
PC.

## Objectifs

À la fin de ce mini-cours, tu sauras :

- distinguer le matériel (hardware) du logiciel (software) ;
- nommer les composants principaux d'un PC et expliquer le rôle de chacun ;
- expliquer la différence entre la RAM et le stockage (HDD/SSD) ;
- décrire ce qui se passe, composant par composant, quand tu lances un programme ;
- utiliser le vocabulaire informatique correct, en français et en anglais.

## Sommaire

1. Vue globale d'un ordinateur
2. Carte mère
3. Processeur (CPU)
4. Mémoire vive (RAM)
5. Stockage
6. Carte graphique (GPU)
7. Alimentation (PSU)
8. Périphériques et entrées/sorties
9. Interaction des composants : que se passe-t-il quand tu lances un programme ?
10. Vocabulaire FR/EN
11. Vocabulaire ancien du référentiel

*Les détails approfondis du CPU et de la RAM sont traités dans le mini-cours 03, ceux du
stockage dans le mini-cours 04, et ceux de l'alimentation/refroidissement/sécurité dans le
mini-cours 05. Ce mini-cours donne les bases nécessaires pour comprendre la suite.*
"""

_MC01_VUE_GLOBALE = r"""## Matériel (hardware) et logiciel (software)

Un ordinateur combine deux univers très différents :

| | Matériel — Hardware | Logiciel — Software |
|---|---|---|
| Définition | Tout ce qui est physique, que tu peux toucher | Les programmes et données qui font fonctionner le matériel |
| Exemples | carte mère, CPU, RAM, disque dur, écran, souris | Windows, un traitement de texte, un jeu vidéo |
| Sans l'autre ? | Sans logiciel, le matériel ne sait rien faire | Sans matériel, le logiciel n'a rien pour s'exécuter |

Le matériel est la partie que tu peux réparer ou remplacer physiquement ; le logiciel
s'installe, se met à jour et se réinstalle sans changer un seul composant.

## Unité centrale et périphériques

- L'**unité centrale** (le boîtier / tour) regroupe les composants qui traitent
  l'information : carte mère, CPU, RAM, stockage, alimentation, carte graphique.
- Les **périphériques** sont les éléments qui communiquent avec l'unité centrale sans en
  faire partie : écran, clavier, souris, imprimante, disque externe...

## Le chemin général de l'information

Un ordinateur, quel qu'il soit, traite toujours l'information selon le même principe :

<div class="jc-flow">
    <div class="jc-flow-step">Entrée<br><small>clavier, souris, micro…</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">Traitement<br><small>CPU</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">Mémoire / stockage<br><small>RAM, SSD, HDD</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">Sortie<br><small>écran, imprimante, haut-parleurs…</small></div>
</div>

Ce schéma revient dans toute la suite du mini-cours : chaque composant que tu vas
découvrir occupe une place précise dans ce chemin.

## RAM et stockage : ne pas confondre

C'est l'une des confusions les plus fréquentes chez un débutant :

| | RAM (mémoire vive) | Stockage (HDD/SSD) |
|---|---|---|
| Rôle | Mémoire de travail *temporaire* | Conservation *durable* des données |
| À l'extinction du PC ? | Contenu **perdu** (volatile) | Contenu **conservé** (persistant) |
| Unité de mesure typique | quelques Go (8, 16, 32 Go...) | souvent bien plus (250 Go à plusieurs To) |
| Rapidité | très rapide | plus lente (HDD) à rapide (SSD) |

> **Piège fréquent :** dire « j'ai 32 Go dans mon PC » ne veut rien dire tout seul — 32 Go
> de RAM et 32 Go de stockage n'ont pas du tout le même usage. Il faut toujours préciser
> RAM ou stockage.
"""

_MC01_CARTE_MERE = r"""## Rôle de la carte mère

La carte mère (*motherboard*) est le support physique qui **interconnecte tous les
composants** de l'unité centrale. Elle ne calcule rien elle-même : son rôle est de
permettre à chaque composant de communiquer avec les autres.

## Ce qu'on trouve sur une carte mère

| Élément | Rôle |
|---|---|
| Socket CPU | Emplacement où se fixe le processeur |
| Emplacements RAM (slots) | Reçoivent les barrettes de mémoire vive |
| Emplacements PCIe | Reçoivent la carte graphique et d'autres cartes d'extension |
| Connecteurs de stockage | Relient les disques (HDD/SSD) à la carte mère |
| Connecteurs E/S | Ports à l'arrière/l'avant du boîtier : USB, réseau, audio... |
| Chipset | Petit circuit qui gère la circulation des données entre les composants |

## Le chipset, en une phrase

Le **chipset** est un circuit intégré à la carte mère qui joue le rôle de chef
d'orchestre : il gère quels composants peuvent communiquer entre eux, à quelle vitesse, et
combien de ports/emplacements sont réellement utilisables. Le détail de son fonctionnement
interne n'est pas nécessaire à ce stade.

## Compatibilité : le point le plus important à retenir

Tous les composants ne s'installent pas sur n'importe quelle carte mère : le socket doit
correspondre au CPU, le type de RAM doit être supporté, l'alimentation doit fournir les
connecteurs nécessaires. **Choisir des composants, c'est toujours vérifier qu'ils sont
compatibles entre eux — la carte mère est au centre de cette compatibilité.**

> **Piège fréquent :** un processeur récent ne rentre pas physiquement dans un socket plus
> ancien, même s'il est « plus performant ». Compatibilité physique et performance sont deux
> questions différentes.
"""

_MC01_CPU = r"""## Rôle du processeur

Le **processeur** (CPU, *Central Processing Unit*) exécute les instructions des programmes
et effectue les calculs. C'est le composant qui « pense » à la place de la machine : chaque
action d'un logiciel finit par se traduire en instructions traitées par le CPU.

## Cœurs, threads et fréquence

| Terme | Signification simple |
|---|---|
| Cœur (*core*) | Une unité de calcul indépendante. Plusieurs cœurs = plusieurs tâches traitées en parallèle. |
| Thread | Un fil d'exécution ; certains CPU traitent plusieurs threads par cœur. |
| Fréquence (GHz) | Le nombre de cycles d'horloge par seconde — une mesure de la « vitesse » d'un cœur. |

## Le cache : une mémoire très rapide et très proche

Le CPU dispose de petites mémoires internes appelées **cache**, beaucoup plus rapides que
la RAM mais beaucoup plus petites, qui stockent temporairement les données que le
processeur va réutiliser tout de suite. Le cache réduit les temps d'attente du CPU.

## La fréquence seule ne suffit pas à comparer deux CPU

> **Piège fréquent :** un CPU à 4,0 GHz n'est pas automatiquement plus rapide qu'un CPU à
> 3,2 GHz. Le nombre de cœurs, l'architecture interne, la quantité de cache et la génération
> du processeur influencent tout autant les performances réelles. Comparer deux CPU sur la
> seule fréquence est une erreur classique à éviter.

*Le détail des architectures, de l'hyperthreading et des générations de processeurs est
traité dans le mini-cours 03 — ici, il suffit de comprendre le rôle du CPU et pourquoi une
seule caractéristique ne suffit jamais à le juger.*
"""

_MC01_RAM = r"""## Rôle de la RAM

La **mémoire vive** (RAM, *Random Access Memory*) est la mémoire de travail temporaire de
l'ordinateur. Quand tu ouvres un programme, ses instructions et les données dont il a
besoin *tout de suite* sont chargées en RAM, où le CPU peut les lire et les écrire très
rapidement.

## Volatile : le mot-clé à retenir

La RAM est **volatile** : dès que le PC s'éteint (ou redémarre), tout son contenu est
effacé. C'est pour cela qu'un document non enregistré est perdu si le PC s'éteint
brutalement — il n'existait qu'en RAM, jamais encore écrit sur le stockage.

## Capacité

La capacité de la RAM se mesure en **gigaoctets (Go)** — typiquement 8, 16 ou 32 Go sur un
PC actuel. Plus il y a de RAM disponible, plus l'ordinateur peut garder de programmes
ouverts en même temps sans ralentir.

## RAM et stockage : la différence fondamentale (rappel)

| | RAM | SSD / HDD (stockage) |
|---|---|---|
| Rôle | Mémoire de travail, à court terme | Conservation des données, à long terme |
| À l'extinction | Contenu perdu (volatile) | Contenu conservé (persistant) |

*Les détails techniques — types de RAM (DDR4, DDR5), fonctionnement en dual-channel,
fréquence de la mémoire — sont traités dans le mini-cours 03.*
"""

_MC01_STOCKAGE = r"""## Rôle du stockage

Le **stockage** conserve les données de façon **durable**, même lorsque l'ordinateur est
éteint : système d'exploitation, programmes installés, documents, photos... C'est la
mémoire à long terme du PC, à l'opposé de la RAM.

## Deux grandes familles

| | HDD (disque dur) | SSD (disque à mémoire flash) |
|---|---|---|
| Fonctionnement | Plateaux magnétiques en rotation, tête de lecture mécanique | Mémoire flash électronique, aucune pièce mécanique |
| Vitesse | Plus lent | Plus rapide, souvent beaucoup plus rapide |
| Robustesse aux chocs | Plus sensible (pièces mobiles) | Plus résistant |
| Prix au Go | Généralement moins cher | Généralement plus cher |

## SSD SATA et SSD NVMe : juste une introduction

Il existe deux grandes façons de connecter un SSD à la carte mère : **SATA** (même type de
connecteur qu'un HDD, plus lent) et **NVMe** (connecté directement en PCIe, beaucoup plus
rapide). Retiens simplement qu'un SSD n'est pas toujours branché de la même façon, et que
cela influence sa vitesse — le détail complet (interfaces, performances réelles, fiabilité,
sauvegarde) est traité dans le mini-cours 04.

## Capacité et performance sont deux choses différentes

Un disque de grande capacité (beaucoup de Go/To) n'est pas nécessairement rapide : la
capacité mesure *combien* de données tiennent sur le disque, la performance mesure *à
quelle vitesse* on peut les lire ou les écrire. Un HDD de 4 To reste plus lent qu'un petit
SSD de 250 Go.

## Persistance hors tension

Contrairement à la RAM, un stockage (HDD ou SSD) **conserve** ses données même sans
alimentation électrique. C'est pour cela qu'un fichier enregistré reste disponible après
avoir éteint puis rallumé le PC.
"""

_MC01_GPU = r"""## Rôle du GPU

Le **GPU** (*Graphics Processing Unit*, processeur graphique) calcule et produit l'image
affichée à l'écran. Il est spécialisé dans un type de calcul particulier — le traitement
d'images et de graphismes — qu'il effectue beaucoup plus efficacement qu'un CPU classique
pour ce genre de tâche.

## GPU intégré ou carte graphique dédiée

| | GPU intégré | Carte graphique dédiée |
|---|---|---|
| Où se trouve-t-il ? | Intégré au CPU ou à la carte mère | Carte séparée, branchée en PCIe |
| Mémoire utilisée | Partage la RAM du système | Possède sa propre mémoire (VRAM) |
| Usage typique | Bureautique, vidéo, usage courant | Jeu vidéo, montage vidéo, calcul intensif |
| Coût | Inclus, pas de surcoût | Composant supplémentaire, souvent coûteux |

## La VRAM

La **VRAM** (*Video RAM*) est la mémoire propre à une carte graphique dédiée, réservée aux
données graphiques (textures, images en cours de calcul). Comme la RAM du système, elle est
volatile, mais elle est physiquement séparée et réservée au GPU.

## Exemples d'usage

- Bureautique, navigation, vidéos : un GPU intégré suffit largement.
- Jeu vidéo récent, montage vidéo, modélisation 3D : une carte graphique dédiée devient
  nécessaire ou très recommandée.

*Ce mini-cours ne va pas plus loin dans l'architecture d'un GPU (unités de calcul,
pipelines graphiques...) : l'objectif ici est de savoir reconnaître son rôle et la
différence entre intégré et dédié.*
"""

_MC01_PSU = r"""## Rôle de l'alimentation

L'**alimentation** (PSU, *Power Supply Unit*) transforme le courant électrique du secteur
en plusieurs tensions utilisables par les composants du PC, et les distribue à chacun
d'eux : carte mère, CPU, stockage, carte graphique...

## La puissance, en watts

La puissance d'une alimentation s'exprime en **watts (W)** — par exemple 550 W ou 750 W.
Ce chiffre indique la puissance **maximale** que l'alimentation peut fournir, pas ce
qu'elle fournit à chaque instant.

> **Piège fréquent :** une alimentation 750 W ne consomme pas 750 W en permanence. La
> consommation réelle varie selon ce que fait le PC à cet instant précis (au repos, en
> pleine charge...) ; 750 W est une limite maximale, pas une consommation constante.

## Sécurité : ne jamais ouvrir une alimentation

Une alimentation conserve une charge électrique dangereuse **même débranchée**, à cause de
ses condensateurs internes. Règle de sécurité à retenir dès maintenant : **on ne démonte
jamais une alimentation**, même hors tension, sauf formation spécifique et matériel adapté.

*Les aspects électriques détaillés (connecteurs, certifications d'efficacité, redondance) et
le refroidissement sont traités dans le mini-cours 05, avec les autres consignes de
sécurité matérielle.*
"""

_MC01_PERIPHERIQUES = r"""## Qu'est-ce qu'un périphérique ?

Un **périphérique** (*peripheral / device*) est un élément externe à l'unité centrale, qui
communique avec elle via un **connecteur d'entrée/sortie** (E/S — *I/O*, port USB, HDMI,
réseau...).

## Entrée, sortie ou mixte ?

| Type | Rôle | Exemples |
|---|---|---|
| Entrée (*input*) | Envoie de l'information *vers* le PC | clavier, souris, micro, scanner |
| Sortie (*output*) | Reçoit de l'information *depuis* le PC | écran, imprimante, haut-parleurs |
| Mixte | Envoie **et** reçoit de l'information | écran tactile, disque externe, casque avec micro, imprimante multifonction |

Le réseau (carte réseau, câble ou Wi-Fi) est également une entrée/sortie : le PC y envoie
et y reçoit des données en permanence.

## Les connecteurs E/S : l'interface entre PC et périphériques

Un connecteur E/S est le point de contact physique (ou sans fil) entre l'unité centrale et
un périphérique : port USB, prise réseau, prise audio, HDMI... Sans connecteur compatible,
un périphérique ne peut tout simplement pas être relié au PC.
"""

_MC01_INTERACTION = r"""## Scénario : tu lances un programme installé sur un SSD

Voici, étape par étape, ce qu'il se passe entre le moment où tu double-cliques sur une
icône et le moment où le programme s'affiche à l'écran :

<div class="jc-flow">
    <div class="jc-flow-step">1. Stockage<br><small>lecture sur le SSD</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">2. RAM<br><small>chargement en mémoire vive</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">3. CPU<br><small>traitement des instructions</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">4. GPU<br><small>calcul de l'image (si nécessaire)</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">5. Écran<br><small>affichage du résultat</small></div>
</div>

1. **Stockage.** Le programme est enregistré sur le SSD. Double-cliquer sur son icône
   demande au système de le lire depuis le SSD.
2. **RAM.** Le contenu nécessaire (code du programme, données de démarrage) est copié du
   SSD vers la RAM : c'est là que le CPU va pouvoir le lire rapidement.
3. **CPU.** Le processeur exécute les instructions du programme chargées en RAM : calculs,
   logique, gestion des actions de l'utilisateur.
4. **GPU.** Si le programme doit afficher quelque chose (une fenêtre, une image, une
   vidéo), le calcul de cette image passe par le GPU (intégré ou dédié).
5. **Écran.** Le résultat calculé est envoyé à l'écran, qui l'affiche.

Deux composants ne sont pas dans ce chemin mais le rendent possible partout :

- la **carte mère** assure toutes les connexions entre stockage, RAM, CPU, GPU et écran ;
- l'**alimentation (PSU)** fournit l'énergie nécessaire à chacun de ces composants, du
  premier au dernier.

Ce scénario est la synthèse de tout ce mini-cours : chaque composant vu séparément dans
les sections précédentes joue ici un rôle précis dans une même chaîne.
"""

_MC01_VOCAB_FR_EN = r"""## Vocabulaire à connaître (français / anglais)

Le vocabulaire technique s'utilise aussi bien en français qu'en anglais dans le métier :
apprends les deux formes pour chaque terme.

| Français | Anglais |
|---|---|
| Matériel | Hardware |
| Logiciel | Software |
| Carte mère | Motherboard |
| Processeur | CPU (*Central Processing Unit*) |
| Mémoire vive | RAM (*Random Access Memory*) |
| Stockage | Storage |
| Disque dur | HDD (*Hard Disk Drive*) |
| Disque SSD | SSD (*Solid State Drive*) |
| Carte graphique | Graphics card |
| Processeur graphique | GPU (*Graphics Processing Unit*) |
| Alimentation | Power supply / PSU (*Power Supply Unit*) |
| Périphérique | Device / peripheral |
| Entrée | Input |
| Sortie | Output |

## Méthode examen

Face à un sigle anglais (CPU, RAM, SSD, GPU, PSU...), commence toujours par retrouver le
terme complet en anglais, puis traduis-le en français — cela évite de confondre des sigles
qui se ressemblent.
"""

_MC01_VOCAB_ANCIEN = r"""## Du vocabulaire à connaître... sans l'enseigner comme technologie actuelle

Le référentiel officiel de la formation AMPCR (programme 345/2007/249) date de 2007. Il
cite encore du matériel aujourd'hui obsolète. Tu dois connaître ces termes pour comprendre
un document ancien ou une question qui les mentionne, **sans qu'ils fassent partie du
matériel que tu utiliseras en pratique aujourd'hui**.

| Terme | Ce que c'était |
|---|---|
| Lecteur de disquettes | Lecteur pour disquette magnétique (quelques centaines de Ko à 1,44 Mo), remplacé depuis longtemps par la clé USB et le stockage en ligne. |
| Graveur optique | Lecteur/graveur de CD ou DVD, aujourd'hui largement remplacé par les téléchargements et le stockage USB/SSD. |

La formation doit suivre la réalité technologique actuelle : ces éléments sont mentionnés
comme repères historiques et vocabulaire de référentiel, pas comme du matériel à
recommander ou à installer aujourd'hui.
"""

# Ticket #29 : exercices 3, 4, 5, 6, 7, 8, 10, 12 migrés en blocs `editorial_exercise`
# structurés (long_answer/diagnostic/vocabulary, corrigés par le fournisseur IA existant
# — voir app/editorial_ai_correction.py). Contenu pédagogique IDENTIQUE à la version
# Markdown d'origine (question et grille de correction reprises mot pour mot, voir
# l'historique git de cette section) — seule la structure technique change (zone de
# réponse + bouton « Corriger » au lieu d'un texte de correction visible sans action).
# context_key requis : ce sont les premiers items MC01 dont la correction passe par l'IA.

_MC01_EXERCICE_3_LONG_ANSWER = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex3",
            type="long_answer",
            prompt=(
                "Explique en une ou deux phrases pourquoi on ne peut pas installer "
                "n'importe quel processeur sur n'importe quelle carte mère."
            ),
            explanation=(
                "Le processeur doit être compatible avec le socket de la carte mère (sa "
                "forme physique de connexion) et avec le chipset qui gère la "
                "communication entre les composants. Sans cette compatibilité, le CPU ne "
                "rentre pas physiquement ou ne fonctionne pas."
            ),
        )
    ],
)

_MC01_EXERCICE_4_DIAGNOSTIC = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex4",
            type="diagnostic",
            prompt=(
                "Un PC s'allume (les ventilateurs tournent, les voyants s'éclairent) mais "
                "rien ne s'affiche à l'écran. En te basant sur le rôle de chaque "
                "composant, cite deux composants ou connexions à vérifier en priorité, et "
                "explique pourquoi."
            ),
            explanation=(
                "À vérifier en priorité : la carte graphique (ou la connexion GPU/écran) "
                "et le câble/connecteur reliant le PC à l'écran, car ce sont eux qui "
                "produisent et transmettent l'image. Le fait que le PC démarre "
                "(ventilateurs, voyants) montre que l'alimentation et une partie au moins "
                "de la carte mère fonctionnent ; le problème est donc probablement "
                "localisé du côté de l'affichage plutôt que de l'alimentation générale."
            ),
        )
    ],
)

_MC01_EXERCICE_5_LONG_ANSWER = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex5",
            type="long_answer",
            prompt=(
                "Explique la différence entre la RAM et le stockage (HDD/SSD) en deux "
                "points précis."
            ),
            explanation=(
                "1) La RAM est une mémoire de travail temporaire et volatile (son contenu "
                "est perdu à l'extinction du PC), alors que le stockage conserve les "
                "données de façon durable, même hors tension. 2) La RAM sert à ce que le "
                "CPU utilise *pendant* l'exécution d'un programme, alors que le stockage "
                "conserve les fichiers et programmes *entre* deux utilisations."
            ),
        )
    ],
)

_MC01_EXERCICE_6_LONG_ANSWER = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex6",
            type="long_answer",
            prompt=(
                "Un ami te dit : « J'ai 32 Go dans mon PC, donc je peux stocker "
                "énormément de vidéos ! » Explique pourquoi cette phrase est ambiguë, et "
                "ce qu'il faudrait lui demander pour vérifier si son raisonnement est "
                "correct."
            ),
            explanation=(
                "La phrase est ambiguë car « 32 Go » peut désigner la RAM ou le stockage, "
                "qui n'ont rien à voir. 32 Go de RAM ne permet pas de stocker des vidéos "
                "de façon durable (la RAM est temporaire et bien plus chère au Go) ; il "
                "faudrait lui demander s'il parle de la RAM ou de la capacité de son "
                "disque dur/SSD pour savoir combien d'espace de stockage il possède "
                "réellement."
            ),
        )
    ],
)

_MC01_EXERCICE_7_LONG_ANSWER = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex7",
            type="long_answer",
            prompt=(
                "Explique la différence entre un GPU intégré et une carte graphique "
                "dédiée, en précisant ce qu'est la VRAM. Donne un exemple de situation où "
                "chacun est suffisant/nécessaire."
            ),
            explanation=(
                "Un GPU intégré est directement intégré au CPU ou à la carte mère et "
                "partage la RAM du système ; une carte graphique dédiée est un composant "
                "séparé, avec sa propre mémoire appelée VRAM, réservée aux calculs "
                "graphiques. Un GPU intégré suffit pour de la bureautique ou de la vidéo "
                "classique ; une carte dédiée devient nécessaire pour un jeu vidéo récent "
                "ou du montage vidéo, qui demandent beaucoup de calcul graphique."
            ),
        )
    ],
)

_MC01_EXERCICE_8_LONG_ANSWER = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex8",
            type="long_answer",
            prompt=(
                "Une alimentation est annoncée « 750 W ». Explique ce que signifie "
                "réellement ce chiffre, et cite une règle de sécurité essentielle à "
                "propos de ce composant."
            ),
            explanation=(
                "750 W est la puissance **maximale** que l'alimentation peut fournir, pas "
                "ce qu'elle consomme en permanence : la consommation réelle varie selon "
                "l'activité du PC à chaque instant. Règle de sécurité : on ne démonte "
                "jamais une alimentation, même débranchée, car elle peut conserver une "
                "charge électrique dangereuse dans ses condensateurs."
            ),
        )
    ],
)

_MC01_EXERCICE_10_DIAGNOSTIC = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex10",
            type="diagnostic",
            prompt=(
                "Un utilisateur se plaint : dès qu'il ouvre plusieurs programmes en même "
                "temps, son PC ralentit fortement. Son disque dispose pourtant de "
                "beaucoup d'espace libre. Quel composant est le plus probablement en "
                "cause, et pourquoi ?"
            ),
            explanation=(
                "La RAM est la piste la plus probable : ouvrir plusieurs programmes en "
                "même temps demande de plus en plus de mémoire de travail, et si la RAM "
                "disponible est insuffisante, le système ralentit fortement. Le fait que "
                "l'espace disque libre soit important écarte un problème de stockage "
                "plein — le symptôme correspond typiquement à un manque de RAM."
            ),
        )
    ],
)

_MC01_EXERCICE_12_VOCABULARY = EditorialExerciseBlockConfig(
    mode="practice",
    context_key="ampcr-mc01",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex12",
            type="vocabulary",
            prompt=(
                "Donne l'équivalent anglais des quatre termes français suivants, et "
                "explique brièvement ce que désigne chacun : mémoire vive, disque dur, "
                "carte mère, alimentation."
            ),
            explanation=(
                "Mémoire vive → RAM (*Random Access Memory*), mémoire de travail "
                "temporaire et volatile. Disque dur → HDD (*Hard Disk Drive*), stockage "
                "magnétique durable. Carte mère → Motherboard, support qui interconnecte "
                "tous les composants. Alimentation → Power supply / PSU (*Power Supply "
                "Unit*), transforme et distribue l'énergie électrique aux composants."
            ),
        )
    ],
)

# Ticket #21 : exercices 1, 2, 9, 11 migrés en blocs `editorial_exercise` structurés
# (classification/ordering). Contenu pédagogique identique à la version Markdown d'origine
# (voir historique git) — seule la structure technique change (boutons de catégorie /
# boutons monter-descendre au lieu d'un texte de correction statique).

_MC01_EXERCICE_1_CLASSIFICATION = EditorialExerciseBlockConfig(
    mode="practice",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex1",
            type="classification",
            prompt=(
                "Classe chacun des éléments suivants dans la bonne catégorie : "
                "**matériel** ou **logiciel**."
            ),
            categories=["Matériel", "Logiciel"],
            elements=[
                "Une carte graphique",
                "Un navigateur internet",
                "Une barrette de RAM",
                "Un antivirus",
                "Un disque SSD",
            ],
            correct_categories=[0, 1, 0, 1, 0],
            explanation=(
                "Le matériel est physique (tu peux le toucher), le logiciel est un "
                "programme installé sur ce matériel."
            ),
        )
    ],
)

_MC01_EXERCICE_2_CLASSIFICATION = EditorialExerciseBlockConfig(
    mode="practice",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex2",
            type="classification",
            prompt=(
                "Parmi les éléments suivants, indique lesquels font partie de "
                "l'**unité centrale** et lesquels sont des **périphériques**."
            ),
            categories=["Unité centrale", "Périphérique"],
            elements=["Écran", "Carte mère", "Clavier", "Alimentation", "Imprimante", "CPU"],
            correct_categories=[1, 0, 1, 0, 1, 0],
            explanation=(
                "L'unité centrale regroupe les composants qui traitent l'information à "
                "l'intérieur du boîtier ; les périphériques communiquent avec elle de "
                "l'extérieur."
            ),
        )
    ],
)

_MC01_EXERCICE_9_ORDERING = EditorialExerciseBlockConfig(
    mode="practice",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex9",
            type="ordering",
            prompt=(
                "Remets dans le bon ordre les étapes suivantes, qui décrivent le lancement "
                "d'un programme installé sur un SSD."
            ),
            order_items=[
                "Le résultat s'affiche à l'écran",
                "Le programme est lu sur le SSD",
                "Le CPU exécute les instructions",
                "Le contenu est chargé en RAM",
            ],
            # Ordre correct (index dans order_items ci-dessus) : lecture SSD → chargement
            # RAM → exécution CPU → affichage écran.
            correct_order=[1, 3, 2, 0],
            explanation=(
                "Le programme est d'abord lu sur le SSD, puis chargé en RAM, puis ses "
                "instructions sont exécutées par le CPU, et le résultat est finalement "
                "affiché à l'écran — éventuellement après un calcul du GPU si une image "
                "doit être produite."
            ),
        )
    ],
)

_MC01_EXERCICE_11_CLASSIFICATION = EditorialExerciseBlockConfig(
    mode="practice",
    items=[
        EditorialExerciseItem(
            exercise_id="mc01-ex11",
            type="classification",
            prompt=(
                "Classe les périphériques suivants en **entrée**, **sortie**, ou **mixte**."
            ),
            categories=["Entrée", "Sortie", "Mixte"],
            elements=[
                "Microphone",
                "Imprimante multifonction (scan + impression)",
                "Enceintes",
                "Écran tactile",
                "Souris",
            ],
            correct_categories=[0, 2, 1, 2, 0],
            explanation=(
                "Entrée : microphone, souris. Sortie : enceintes. Mixtes : imprimante "
                "multifonction (elle imprime — sortie — et scanne — entrée), écran tactile "
                "(il affiche — sortie — et reçoit le toucher — entrée)."
            ),
        )
    ],
)

_MC01_MEMO = r"""# Fiche mémo — Architecture générale d'un PC

## Les composants et leur rôle

| Composant | Rôle en une phrase |
|---|---|
| Carte mère | Interconnecte tous les composants |
| CPU | Exécute les instructions et fait les calculs |
| RAM | Mémoire de travail temporaire, volatile |
| Stockage (HDD/SSD) | Conserve les données durablement, même hors tension |
| GPU | Calcule et produit l'image affichée |
| Alimentation (PSU) | Transforme et distribue l'énergie électrique |
| Périphériques | Communiquent avec l'unité centrale via des connecteurs E/S |

## Le chemin de l'exécution d'un programme

Stockage → RAM → CPU → (GPU) → Écran, la carte mère reliant tout et le PSU alimentant
chaque étape.

## Pièges à ne jamais oublier

- RAM ≠ stockage : l'un est temporaire (volatile), l'autre est durable (persistant).
- Une fréquence CPU seule ne permet pas de comparer deux processeurs.
- Les watts d'une alimentation sont une puissance **maximale**, pas une consommation
  constante.
- Ne jamais ouvrir une alimentation, même débranchée.

## Vocabulaire FR/EN essentiel

| Français | Anglais |
|---|---|
| Matériel | Hardware |
| Logiciel | Software |
| Carte mère | Motherboard |
| Processeur | CPU |
| Mémoire vive | RAM |
| Stockage | Storage |
| Disque dur | HDD |
| Carte graphique | Graphics card / GPU |
| Alimentation | Power supply / PSU |
| Périphérique | Device / peripheral |

<div class="d-print-none mt-3">
    <button type="button" class="btn btn-outline-dark btn-sm" onclick="window.print()">
        Imprimer cette fiche
    </button>
</div>
"""

_MC01_EXAMEN = r"""# Examen final — Architecture générale d'un PC

**Consigne :** réponds à chaque question de façon complète et justifiée. Chaque question
vaut 2 points, pour un total de 20 points.

## Question 1 (2 pts)

Explique en une phrase le rôle du CPU, de la RAM, du stockage et de la carte mère.

## Question 2 (2 pts)

Décris, étape par étape, ce qui se passe entre le moment où tu lances un programme
installé sur un SSD et le moment où le résultat s'affiche à l'écran.

## Question 3 (2 pts)

Un camarade affirme : « J'ai 32 Go dans mon PC, donc je peux stocker beaucoup de vidéos. »
Explique pourquoi ce raisonnement peut être une erreur.

## Question 4 (2 pts)

Explique la différence entre un GPU intégré et une carte graphique dédiée, et précise ce
qu'est la VRAM.

## Question 5 (2 pts)

Explique le rôle de l'alimentation (PSU) et ce que signifie réellement une puissance
annoncée de 750 W.

## Question 6 (2 pts)

Classe les périphériques suivants en entrée, sortie ou mixte : clavier, écran, casque avec
micro, imprimante.

## Question 7 (2 pts)

Explique la différence entre la volatilité de la RAM et la persistance du stockage.

## Question 8 (2 pts)

Un PC ralentit fortement dès que plusieurs programmes sont ouverts, mais son disque dur est
presque vide. Le problème vient-il plutôt d'un manque de RAM ou d'un manque d'espace
disque ? Justifie ta réponse.

## Question 9 (2 pts)

Donne quatre termes informatiques vus dans ce mini-cours, avec leur équivalent en anglais,
et explique brièvement chacun.

## Question 10 (2 pts)

En synthèse, décris les interactions principales entre les composants d'un PC en état de
fonctionnement (tu peux t'appuyer sur un schéma ou un exemple concret).
"""

# Corrigé/barème réservé au formateur — bloc volontairement non publié (is_published=False)
# pour qu'il ne soit jamais servi sur la route publique /uaa/{slug} (voir app/main.py,
# uaa_detail : `if not block.is_published: continue`). Consultable/éditable depuis l'admin.
_MC01_EXAMEN_CORRIGE = r"""# Corrigé — Examen final « Architecture générale d'un PC »

**Ce bloc n'est jamais publié côté candidat** (non publié) — réservé à la
correction/notation par le formateur depuis l'administration. Barème : 2 points par
question, 20 points au total.

## Question 1 (2 pts)

CPU : exécute les instructions et effectue les calculs. RAM : mémoire de travail temporaire
et volatile. Stockage : conserve les données durablement. Carte mère : interconnecte tous
les composants. *(0,5 pt par rôle correct)*

## Question 2 (2 pts)

Stockage (lecture du programme) → RAM (chargement) → CPU (exécution des instructions) →
GPU si nécessaire (calcul de l'image) → écran (affichage). *(0,4 pt par étape correcte dans
le bon ordre)*

## Question 3 (2 pts)

« 32 Go » est ambigu car il peut désigner la RAM (mémoire de travail, non adaptée au
stockage durable de fichiers) ou le stockage (capacité réelle de conservation). *(1 pt
identification de l'ambiguïté, 1 pt explication correcte)*

## Question 4 (2 pts)

GPU intégré : partagé avec le CPU/la RAM système. Carte dédiée : composant séparé, VRAM
propre. VRAM : mémoire réservée aux calculs graphiques de la carte dédiée. *(1 pt
différence intégré/dédié, 1 pt définition VRAM)*

## Question 5 (2 pts)

PSU : transforme et distribue l'énergie électrique aux composants. 750 W = puissance
maximale disponible, pas une consommation constante. *(1 pt rôle, 1 pt puissance max ≠
consommation réelle)*

## Question 6 (2 pts)

Entrée : clavier. Sortie : écran. Mixtes : casque avec micro, imprimante (si multifonction ;
imprimante simple = sortie seule, accepter les deux réponses si justifiées). *(0,5 pt par
classification correcte)*

## Question 7 (2 pts)

RAM volatile : contenu perdu à l'extinction. Stockage persistant : contenu conservé hors
tension. *(1 pt par notion correctement expliquée)*

## Question 8 (2 pts)

Manque de RAM le plus probable : le ralentissement apparaît avec l'ouverture de plusieurs
programmes (consommation de mémoire de travail), et l'espace disque n'est pas en cause
puisqu'il reste disponible. *(1 pt bon diagnostic, 1 pt justification correcte)*

## Question 9 (2 pts)

Tout regroupement de 4 termes du cours avec équivalent anglais correct et explication
correcte est acceptable (ex. RAM, HDD, CPU, motherboard...). *(0,5 pt par terme correct)*

## Question 10 (2 pts)

Réponse ouverte : évaluer la cohérence globale de la synthèse (carte mère = interconnexion,
PSU = énergie, chemin stockage → RAM → CPU → (GPU) → écran). *(notation qualitative sur 2
points, à l'appréciation du correcteur)*
"""

MC01_BLOCKS = [
    {
        "title": "Plan du mini-cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_PLAN,
        "position": 1,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "1. Vue globale d'un ordinateur — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_VUE_GLOBALE,
        "position": 2,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "2. Carte mère — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_CARTE_MERE,
        "position": 3,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "3. Processeur (CPU) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_CPU,
        "position": 4,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "4. Mémoire vive (RAM) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_RAM,
        "position": 5,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "5. Stockage — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_STOCKAGE,
        "position": 6,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "6. Carte graphique (GPU) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_GPU,
        "position": 7,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "7. Alimentation (PSU) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_PSU,
        "position": 8,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "8. Périphériques et entrées/sorties — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_PERIPHERIQUES,
        "position": 9,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "9. Interaction des composants — Exemple",
        "type": BlockType.MARKDOWN,
        "content": _MC01_INTERACTION,
        "position": 10,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "10. Vocabulaire FR/EN — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_VOCAB_FR_EN,
        "position": 11,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "11. Vocabulaire ancien du référentiel — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC01_VOCAB_ANCIEN,
        "position": 12,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        # Ticket #21 : ex-Exercice 1, migré de Markdown vers `editorial_exercise`
        # (classification). Titre distinct des blocs Markdown ci-dessous : ne fait pas
        # partie de MC01_OBSOLETE_TITLES.
        "title": "Exercice 1 — Matériel ou logiciel (classification)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_1_CLASSIFICATION.to_json(),
        "position": 13,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 2 — Unité centrale ou périphérique (classification)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_2_CLASSIFICATION.to_json(),
        "position": 14,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        # Ticket #29 : titre nouveau (n'était pas un bloc structuré avant), donc aucun
        # besoin de figurer dans MC01_OBSOLETE_TITLES pour celui-ci.
        "title": "Exercice 3 — Compatibilité CPU/carte mère (réponse rédigée)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_3_LONG_ANSWER.to_json(),
        "position": 15,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 4 — Diagnostic : rien ne s'affiche (diagnostic)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_4_DIAGNOSTIC.to_json(),
        "position": 16,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 5 — RAM et stockage (réponse rédigée)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_5_LONG_ANSWER.to_json(),
        "position": 17,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 6 — Ambiguïté des Go (réponse rédigée)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_6_LONG_ANSWER.to_json(),
        "position": 18,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 7 — GPU intégré ou dédié (réponse rédigée)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_7_LONG_ANSWER.to_json(),
        "position": 19,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 8 — Puissance de l'alimentation (réponse rédigée)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_8_LONG_ANSWER.to_json(),
        "position": 20,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 9 — Lancement d'un programme (ordering)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_9_ORDERING.to_json(),
        "position": 21,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 10 — Diagnostic : le PC ralentit (diagnostic)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_10_DIAGNOSTIC.to_json(),
        "position": 22,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 11 — Entrée, sortie ou mixte (classification)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_11_CLASSIFICATION.to_json(),
        "position": 23,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Exercice 12 — Vocabulaire FR/EN (vocabulaire)",
        "type": BlockType.EDITORIAL_EXERCISE,
        "content": _MC01_EXERCICE_12_VOCABULARY.to_json(),
        "position": 24,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Architecture d'un PC — Génère ton propre exercice (IA)",
        "type": BlockType.AI_EXERCISE,
        "content": AIExerciseBlockConfig(
            context_key="ampcr-mc01",
            intro=(
                "En complément des exercices ci-dessus : choisis une difficulté, génère un "
                "nouvel exercice, réponds, puis demande une correction personnalisée. "
                "L'exercice reste strictement dans la matière de ce mini-cours."
            ),
        ).to_json(),
        "position": 25,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Fiche mémo — Architecture générale d'un PC",
        "type": BlockType.MARKDOWN,
        "content": _MC01_MEMO,
        "position": 26,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "Examen final — Architecture générale d'un PC (10 questions, 20 points)",
        "type": BlockType.MARKDOWN,
        "content": _MC01_EXAMEN,
        "position": 27,
        "is_published": True,
        "space": BlockSpace.EXAM,
    },
    {
        "title": "Examen final — Corrigé (réservé formateur, non publié)",
        "type": BlockType.MARKDOWN,
        "content": _MC01_EXAMEN_CORRIGE,
        "position": 28,
        "is_published": False,
        "space": BlockSpace.EXAM,
    },
]

# Contenu réel du mini-cours 02 Informatique AMPCR (« Carte mère, formats et
# connectiques »), ticket #12 : contenu et périmètre pédagogique fournis par ChatGPT (chef
# de projet), rédigés ici sans en changer la portée. Réutilise exactement l'architecture du
# ticket #10 (blocs markdown, classification par titre, correction masquée générique,
# bloc ai_exercise + contexte pédagogique borné) — aucune nouvelle architecture.

MC02_CODE = "MC02"
MC02_TITLE = "Carte mère, formats et connectiques"

_MC02_PLAN = r"""# Carte mère, formats et connectiques

Ce mini-cours prolonge le mini-cours 01 : après la vue d'ensemble d'un PC, on entre dans le
détail de la carte mère elle-même — son rôle exact, ses formats, ses connecteurs, et la
méthode professionnelle pour vérifier la compatibilité des composants et diagnostiquer une
panne de démarrage.

## Objectifs

À la fin de ce mini-cours, tu sauras :

- expliquer le rôle détaillé de la carte mère (interconnexion, alimentation distribuée,
  firmware, contrôleurs) ;
- reconnaître les formats ATX, micro-ATX, Mini-ITX et leurs conséquences pratiques ;
- vérifier la compatibilité socket/chipset/RAM/PCIe/alimentation d'une configuration ;
- identifier les connecteurs internes et la connectique arrière ;
- appliquer une procédure structurée de diagnostic en cas d'absence de POST ;
- respecter les règles de sécurité (hors tension, ESD) avant toute manipulation.

## Sommaire

1. Rôle détaillé de la carte mère
2. Formats : ATX, micro-ATX, Mini-ITX
3. Socket CPU et compatibilité
4. Chipset
5. Slots RAM (DIMM)
6. PCI Express (PCIe)
7. Stockage sur la carte mère (SATA, M.2)
8. Alimentation interne (ATX 24 broches, EPS)
9. Connecteurs internes
10. Connectique arrière (E/S)
11. F_PANEL
12. BIOS/UEFI et POST
13. Méthode de compatibilité
14. Diagnostic professionnel : pas de POST/affichage
15. Sécurité et décharge électrostatique (ESD)
16. Vocabulaire FR/EN

*Les détails DDR/dual-channel de la RAM restent traités au mini-cours 03, les détails
SATA/NVMe du stockage au mini-cours 04, et l'alimentation/le refroidissement complets au
mini-cours 05.*
"""

_MC02_ROLE = r"""## Interconnexion

Comme vu au mini-cours 01, la carte mère relie physiquement et électriquement tous les
composants : CPU, RAM, stockage, carte graphique, alimentation, périphériques. Ici, on va
plus loin : ce rôle se décompose en plusieurs fonctions précises.

## Alimentation distribuée

La carte mère ne produit aucune énergie : elle reçoit le courant de l'alimentation (PSU) et
le **distribue** aux composants qu'elle héberge (CPU, RAM, cartes d'extension) via des
circuits de régulation dédiés (VRM — *Voltage Regulator Module* — pour le CPU notamment).

## Firmware

La carte mère embarque un petit programme stocké sur une puce dédiée, le **firmware**
(BIOS/UEFI, voir section 12), qui s'exécute avant le système d'exploitation pour
initialiser le matériel.

## Contrôleurs

La carte mère intègre plusieurs **contrôleurs** : puces spécialisées qui gèrent un type de
périphérique particulier (réseau, audio, USB, stockage). Un contrôleur défaillant peut
rendre indisponible une fonction précise (ex. plus de son) sans affecter le reste du PC.

## À retenir

La carte mère n'est pas un simple support passif : elle interconnecte, distribue l'énergie,
exécute un firmware, et intègre des contrôleurs actifs.
"""

_MC02_FORMATS = r"""## Trois formats courants

| Format | Dimensions typiques | Emplacements d'extension | Usage typique |
|---|---|---|---|
| ATX | 305 × 244 mm | Nombreux (jusqu'à 7 PCIe, plusieurs DIMM) | PC de bureau standard, extensible |
| micro-ATX (mATX) | 244 × 244 mm | Réduits (souvent 2 à 4 PCIe) | Compromis taille/extensibilité |
| Mini-ITX | 170 × 170 mm | Très réduits (1 seul PCIe en général) | PC compact, silencieux, peu extensible |

## Conséquences pratiques

- Le **boîtier** doit être compatible avec le format de la carte mère (un boîtier ATX
  accepte en général aussi micro-ATX et Mini-ITX, l'inverse n'est pas vrai).
- Une carte plus petite offre **moins d'emplacements** (RAM, PCIe, connecteurs de
  stockage) : elle limite les possibilités d'évolution future.
- Le format influence l'espace disponible pour le refroidissement et le câblage, pas
  seulement la taille du boîtier.

## Ce que le format ne détermine PAS

> **Piège fréquent :** le format d'une carte mère (ATX/micro-ATX/Mini-ITX) ne détermine
> pas à lui seul les performances du PC. Une carte Mini-ITX peut héberger un CPU et une
> carte graphique haut de gamme ; elle offre seulement moins d'emplacements et de marge
> d'extension future.
"""

_MC02_SOCKET = r"""## Rôle du socket

Le **socket** est l'emplacement physique où se fixe le processeur sur la carte mère. Il
détermine si un CPU peut être **physiquement** installé.

## Compatibilité mécanique ≠ compatibilité complète

> **Piège fréquent :** un CPU qui rentre physiquement dans un socket n'est pas forcément
> pleinement compatible. Il faut aussi vérifier la **génération** du CPU supportée par la
> carte mère, la compatibilité avec le **chipset**, et si nécessaire une **mise à jour du
> BIOS/UEFI** (support constructeur) avant que le CPU ne soit reconnu.

## Méthode rapide de vérification

1. Identifier le socket du CPU (ex. LGA1700, AM5...).
2. Vérifier que la carte mère annonce ce même socket.
3. Vérifier, sur le site du fabricant de la carte mère, la liste de compatibilité CPU (CPU
   support list) et la version de BIOS minimale requise pour ce CPU.
4. Mettre à jour le BIOS si nécessaire, **avant** d'installer un CPU très récent sur une
   carte plus ancienne.

## À retenir

Socket correspondant = condition nécessaire, pas suffisante. Toujours croiser socket,
génération CPU, chipset et version BIOS.
"""

_MC02_CHIPSET = r"""## Rôle moderne du chipset

Le chipset est aujourd'hui un circuit unique intégré à la carte mère, qui gère la
communication entre le CPU et les composants qui ne sont pas directement reliés à lui :
ports USB supplémentaires, connexions SATA, lanes PCIe additionnelles, certains
contrôleurs réseau/audio.

Il détermine notamment :

- le nombre de ports USB, SATA et lanes PCIe réellement disponibles ;
- certaines fonctionnalités avancées (overclocking, RAID, etc., selon la gamme de
  chipset).

## Éviter une description historique dépassée

> **Piège fréquent :** les anciennes architectures « north bridge / south bridge » (deux
> puces séparées) ne décrivent plus les plateformes modernes, où la plupart des fonctions
> du north bridge ont été intégrées directement au CPU. Ne pas présenter cette architecture
> à deux puces comme la réalité actuelle.
"""

_MC02_RAM_SLOTS = r"""## Slots DIMM

Les barrettes de RAM s'installent dans des **slots DIMM** (*Dual In-line Memory Module*)
sur la carte mère. Un **détrompeur** (encoche asymétrique) empêche d'insérer une barrette
dans le mauvais sens ou un type de RAM incompatible avec la carte.

## Canaux et emplacements recommandés

Les cartes mères modernes fonctionnent en **plusieurs canaux mémoire** (dual-channel le
plus souvent) : pour en bénéficier, les barrettes doivent être installées dans des slots
précis, indiqués par le **manuel de la carte mère** (souvent des couleurs de slots
alternées). Installer les barrettes au hasard peut désactiver ce mode multi-canal sans
provoquer d'erreur visible.

> **Piège fréquent :** deux barrettes installées côte à côte dans les mauvais slots
> fonctionnent souvent quand même, mais sans le gain de performance du mode dual-channel —
> toujours consulter le manuel pour l'emplacement recommandé.

*Le fonctionnement détaillé du dual-channel et les générations DDR sont traités au
mini-cours 03 — ici, il suffit de savoir que l'emplacement des barrettes compte.*
"""

_MC02_PCIE = r"""## Lanes et formats x1/x4/x8/x16

Le PCI Express (PCIe) relie des cartes d'extension (carte graphique, carte réseau, carte de
capture, contrôleurs additionnels...) à la carte mère via des **lanes** (voies de
communication). Un emplacement PCIe existe en plusieurs tailles : x1, x4, x8, x16 — le
chiffre indique le nombre de lanes disponibles.

## Taille physique ≠ liaison électrique

> **Piège fréquent :** un emplacement de taille physique x16 n'est pas toujours câblé avec
> 16 lanes électriques réelles (parfois seulement x4 ou x8 électriquement, selon la carte
> mère). La taille du connecteur et le nombre de lanes réellement actives sont deux choses
> différentes à vérifier dans la documentation.

## Générations PCIe

Chaque génération (PCIe 3.0, 4.0, 5.0...) double environ le débit par lane par rapport à la
précédente. Les générations sont **rétrocompatibles** : une carte PCIe 4.0 fonctionne dans
un emplacement PCIe 3.0 (à la vitesse la plus basse des deux), et inversement une carte
PCIe 3.0 fonctionne dans un emplacement PCIe 5.0.

## Exemples d'usage

Carte graphique (généralement x16), carte réseau ou de capture (souvent x1 ou x4),
contrôleurs additionnels (USB, SATA supplémentaires).
"""

_MC02_STOCKAGE_CM = r"""## SATA : le connecteur de données

Le connecteur **SATA** (data) relie un disque (HDD ou SSD SATA) à la carte mère pour le
transfert de données. Il est distinct du câble d'alimentation SATA, qui vient du PSU (voir
section 8).

## M.2 : un format de connecteur, pas une technologie

> **Piège fréquent :** « M.2 » désigne la **forme physique** du connecteur et du
> composant, pas une technologie de vitesse. Un emplacement M.2 peut accueillir un SSD
> SATA ou un SSD NVMe (bien plus rapide, connecté en PCIe) — la carte mère précise dans sa
> documentation quel(s) mode(s) chaque emplacement M.2 supporte. M.2 n'est donc **jamais
> synonyme de NVMe**.

*Le détail des performances et de la fiabilité SATA/NVMe est traité au mini-cours 04 — ici,
il suffit de distinguer le connecteur SATA data, le format M.2, et de savoir qu'ils ne se
recouvrent pas exactement.*
"""

_MC02_ALIM_INTERNE = r"""## ATX 24 broches et EPS

La carte mère reçoit l'énergie du PSU via deux connecteurs principaux :

| Connecteur | Alimente | Broches typiques |
|---|---|---|
| ATX principal | La carte mère elle-même | 24 broches |
| EPS (CPU) | Le processeur, via les VRM | 4 ou 8 broches (parfois 4+4) |

## À ne pas confondre avec le connecteur GPU

> **Piège fréquent :** le connecteur EPS (CPU, 4/8 broches) ressemble à certains
> connecteurs d'alimentation de cartes graphiques (PCIe 6/8 broches, ou le récent
> 12V-2x6/12VHPWR) mais ce ne sont **pas les mêmes connecteurs** et ils ne sont pas
> interchangeables. Toujours vérifier l'étiquette du câble et le connecteur correspondant.

## Le SATA Power vient du PSU, pas de la carte mère

Le câble d'alimentation SATA (différent du câble de données SATA, voir section 7) part
directement de l'alimentation (PSU) vers le disque — il ne transite pas par la carte mère.

*Le détail complet de l'alimentation (watts, certifications, câblage) est traité au
mini-cours 05.*
"""

_MC02_CONNECTEURS_INTERNES = r"""## Ventilateurs

| Connecteur | Rôle |
|---|---|
| CPU_FAN | Ventilateur du processeur — surveillé par la carte mère (vitesse, arrêt détecté) |
| SYS_FAN / CHA_FAN | Ventilateurs du boîtier (*system/chassis fan*) |

## F_PANEL (façade avant)

Regroupe les connexions du bouton d'allumage, du bouton reset, et des voyants — détaillé en
section 11.

## USB internes et audio façade

- En-têtes **USB internes** : alimentent les ports USB en façade du boîtier.
- En-tête **audio façade** (souvent « AAFP » ou « HD Audio ») : relie la prise casque/micro
  en façade du boîtier à la carte mère.

## RGB/ARGB (extension moderne)

Certaines cartes mères récentes ajoutent des en-têtes RGB ou ARGB pour piloter un éclairage
décoratif. Il s'agit d'une extension purement esthétique, clairement séparée des
connecteurs fonctionnels ci-dessus.

> **Piège fréquent :** un connecteur RGB/ARGB standard 3 broches (5 V) branché par erreur
> sur un connecteur RGB 4 broches (12 V), ou inversement, peut endommager les composants —
> toujours vérifier le voltage et le nombre de broches avant de brancher.
"""

_MC02_IO_ARRIERE = r"""## Panneau E/S arrière

| Connecteur | Rôle | Remarque |
|---|---|---|
| USB-A | Périphériques USB classiques | Plusieurs versions (débit variable) |
| USB-C | Périphériques USB récents, réversible | De plus en plus courant |
| Audio (jack) | Casque, micro, haut-parleurs | Souvent plusieurs prises couleur |
| Ethernet (RJ45) | Connexion réseau filaire | Débit selon le contrôleur réseau |
| Vidéo (HDMI/DisplayPort) | Sortie image | Présent seulement si GPU intégré utilisé |
| PS/2 | Clavier/souris très anciens | Ancien, de moins en moins présent |

## Connecteur physique ≠ protocole

> **Piège fréquent :** un même connecteur physique (ex. USB-C) peut supporter des
> protocoles différents selon la carte mère (USB simple, Thunderbolt, DisplayPort via
> USB-C...). Le connecteur physique ne suffit pas à connaître les capacités réelles — il
> faut vérifier la documentation.
"""

_MC02_F_PANEL = r"""## Les 4 connexions principales

| Connecteur | Rôle | Type |
|---|---|---|
| Power SW | Bouton d'allumage | Interrupteur (pas de polarité) |
| Reset SW | Bouton de redémarrage matériel | Interrupteur (pas de polarité) |
| Power LED | Voyant d'alimentation allumée | LED (polarité à respecter) |
| HDD LED | Voyant d'activité disque | LED (polarité à respecter) |

## Polarité : interrupteurs vs LED

Les **interrupteurs** (Power SW, Reset SW) n'ont pas de polarité : ils fonctionnent dans
les deux sens de branchement, car ils ferment simplement un circuit. Les **LED** (Power
LED, HDD LED) ont une polarité (+ / −) : branchées à l'envers, elles ne s'allument
simplement pas, en général sans risque d'endommager le matériel.

> **Piège fréquent :** brancher les connecteurs F_PANEL au hasard « pour voir » fonctionne
> souvent pour l'allumage (interrupteurs) mais peut laisser les voyants éteints (LED à
> l'envers). Toujours consulter le manuel de la carte mère : le brochage F_PANEL n'est pas
> standardisé entre fabricants.
"""

_MC02_BIOS_UEFI = r"""## Rôle du firmware

Le **BIOS** (*Basic Input/Output System*, terme historique toujours utilisé) ou son
successeur, l'**UEFI** (*Unified Extensible Firmware Interface*, la norme actuelle), est le
firmware qui s'exécute au démarrage, avant tout système d'exploitation. Il initialise le
matériel (CPU, RAM, contrôleurs) et transfère ensuite le contrôle au système d'exploitation.

## Le POST

Le **POST** (*Power-On Self-Test*) est la séquence de vérifications matérielles effectuée
par le firmware juste après la mise sous tension, avant l'affichage du système
d'exploitation. Un POST réussi précède toujours un démarrage normal ; un POST qui échoue
bloque le démarrage (voir section 14, diagnostic).

## À retenir

BIOS = terme historique encore utilisé couramment ; UEFI = norme actuelle, plus complète
(interface graphique, disques de grande capacité, sécurité au démarrage).
L'approfondissement de l'UEFI (menus, options avancées) sera vu plus tard.
"""

_MC02_METHODE_COMPATIBILITE = r"""## Méthode examen : vérifier la compatibilité d'une configuration

Face à une configuration à valider (montage, mise à niveau, dépannage), suis toujours cet
ordre :

1. **Besoin** — que doit faire ce PC (bureautique, jeu, serveur...) ?
2. **Format** — quel format de carte mère et de boîtier convient à ce besoin ?
3. **Socket / support CPU** — le CPU choisi est-il supporté par la carte mère (socket,
   génération, version BIOS) ?
4. **RAM** — le type de RAM (voir mini-cours 03), la capacité et le nombre de slots
   conviennent-ils ?
5. **Stockage** — les connecteurs disponibles (SATA, M.2) correspondent-ils aux disques
   prévus ?
6. **PCIe** — les emplacements disponibles conviennent-ils à la carte graphique et aux
   éventuelles cartes d'extension ?
7. **Alimentation et connecteurs** — le PSU fournit-il les connecteurs nécessaires (ATX 24
   broches, EPS, PCIe GPU) avec une puissance suffisante ?
8. **Boîtier** — le boîtier accepte-t-il le format de carte mère et la taille des autres
   composants (GPU, ventirad) ?
9. **Manuel / QVL / support constructeur** — vérifier la documentation officielle et la
   liste de compatibilité (*Qualified Vendor List*) avant de finaliser le choix.

Cet ordre n'est pas arbitraire : chaque étape dépend en partie de la précédente (le format
conditionne les emplacements disponibles, qui conditionnent les choix de RAM/stockage/PCIe).
"""

_MC02_DIAGNOSTIC = r"""## Scénario : les ventilateurs tournent, mais aucun affichage

Un client apporte un PC qui s'allume (ventilateurs, voyants) mais qui n'affiche jamais rien
à l'écran — aucun POST. Voici la procédure professionnelle structurée, étape par étape :

<div class="jc-flow">
    <div class="jc-flow-step">1. Couper<br><small>l'alimentation</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">2. Contrôle visuel<br><small>connecteurs, dégâts</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">3. ATX/EPS<br><small>bien enfoncés</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">4. RAM<br><small>réinsérer/tester une barrette</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">5. GPU/écran<br><small>connexion, sortie vidéo</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">6. Codes LED/beep<br><small>si disponibles</small></div>
</div>

1. **Couper l'alimentation** avant toute manipulation (voir section 15, sécurité).
2. **Contrôle visuel** : connecteurs bien enfoncés, absence de dégâts visibles (composants
   gonflés, traces de brûlure, corps étranger).
3. **Vérifier ATX 24 broches et EPS** : bien enfoncés jusqu'au clic.
4. **RAM** : réinsérer les barrettes, tester avec une seule barrette dans le slot
   recommandé par le manuel, tester chaque barrette séparément si plusieurs sont
   disponibles.
5. **GPU et écran** : vérifier que le câble vidéo est branché sur la bonne sortie (carte
   dédiée vs GPU intégré), tester un autre câble/écran si possible.
6. **Codes LED ou signaux sonores (beep codes)** : de nombreuses cartes mères affichent un
   code d'erreur (LED dédiées ou séquence de bips) qui identifie le composant en cause —
   consulter le manuel pour l'interpréter.
7. **Configuration minimale** : si le problème persiste, démonter tout ce qui n'est pas
   indispensable (une seule barrette de RAM, pas de carte d'extension autre que le GPU si
   nécessaire) pour isoler la panne.
8. **Clear CMOS** : réinitialiser les paramètres du BIOS/UEFI selon la procédure du
   fabricant (cavalier dédié ou bouton) si un mauvais réglage est suspecté.
9. **Documenter** chaque étape testée et son résultat, pour ne pas répéter un test déjà
   fait et pour transmettre l'information si le problème est escaladé.

> **Piège fréquent :** ne jamais retirer, insérer ou tester un composant alors que le PC
> est sous tension, même « juste pour voir » — toujours couper l'alimentation d'abord (voir
> section 15).
"""

_MC02_SECURITE_ESD = r"""## Toujours hors tension

Avant toute intervention à l'intérieur du boîtier : éteindre le PC, débrancher le câble
d'alimentation secteur (pas seulement éteindre l'interrupteur du PSU).

## Décharge électrostatique (ESD)

L'électricité statique accumulée par le corps humain peut détruire silencieusement un
composant électronique (RAM, CPU, carte mère) au contact, sans dégât visible immédiat.

- Se décharger avant de toucher un composant (toucher une partie métallique non peinte du
  boîtier, ou utiliser un bracelet antistatique relié à la masse).
- Manipuler les composants **par les bords**, jamais par les broches, les connecteurs ou
  les puces.
- Éviter de travailler sur une surface générant de l'électricité statique (tapis
  synthétique, par exemple), et éviter les vêtements très isolants dans un environnement
  sec.

## Connecteurs : ne jamais forcer

> **Piège fréquent :** un connecteur qui ne s'insère pas facilement est presque toujours
> mal orienté ou mal aligné — ne jamais forcer. Vérifier le détrompeur (RAM, câbles SATA,
> connecteurs alimentation) avant d'insister.
"""

_MC02_VOCAB_FR_EN = r"""## Vocabulaire à connaître (français / anglais)

| Français | Anglais |
|---|---|
| Carte mère | Motherboard |
| Socket (même terme) | Socket |
| Jeu de composants | Chipset |
| Emplacement (RAM, PCIe) | Slot |
| Connecteur interne (façade, ventilateur...) | Header |
| Panneau avant | Front panel |
| Emplacement d'extension | Expansion slot |
| Entrée/sortie | I/O |
| Voie de communication (PCIe) | Lane |
| Micrologiciel | Firmware |
| Auto-test de démarrage | POST (Power-On Self-Test) |

## Méthode examen

Comme au mini-cours 01 : pour un sigle anglais (POST, I/O, EPS...), retrouve d'abord le
terme complet en anglais, puis traduis-le en français.
"""

_MC02_EXERCICES_1 = r"""## Exercice 1 — choisir

Un client veut un PC très compact pour du bureautique simple, sans intention d'ajouter des
cartes d'extension plus tard. Quel format de carte mère lui recommandes-tu, et pourquoi
n'est-ce pas nécessairement un problème pour ses performances ?

**Correction :** Mini-ITX est adapté : format le plus compact, un seul emplacement PCIe
suffit pour un usage bureautique sans extension prévue. Le format ne détermine pas les
performances : une Mini-ITX peut recevoir un CPU performant, elle offre seulement moins
d'emplacements pour évoluer plus tard.

## Exercice 2 — vérifier une compatibilité

Un technicien veut installer un CPU récent (socket LGA1700, dernière génération) sur une
carte mère qui annonce elle aussi le socket LGA1700, mais plus ancienne. Le socket
correspond : peut-il en conclure que la compatibilité est garantie ? Justifie.

**Correction :** Non. Le socket correspondant est nécessaire mais pas suffisant : il faut
aussi vérifier que la carte mère supporte cette génération précise de CPU (liste de
compatibilité du fabricant) et que le BIOS est à une version suffisante — une mise à jour
du BIOS est parfois nécessaire avant que le CPU récent soit reconnu.

## Exercice 3 — expliquer

Explique pourquoi il est incorrect aujourd'hui de décrire le chipset comme « deux puces
séparées, north bridge et south bridge ».

**Correction :** Cette description correspond à d'anciennes architectures. Sur les
plateformes modernes, la plupart des fonctions autrefois assurées par le north bridge sont
intégrées directement au CPU ; le chipset est aujourd'hui un circuit unique qui gère les
connexions restantes (USB, SATA, PCIe additionnels...).

## Exercice 4 — expliquer

Deux barrettes de RAM identiques sont installées, mais pas dans les slots recommandés par
le manuel de la carte mère. Le PC démarre normalement. Le technicien en conclut qu'il n'y a
aucun problème. A-t-il raison ?

**Correction :** Pas nécessairement. Le PC peut démarrer normalement même sans le mode
dual-channel : dans ce cas, les barrettes fonctionnent, mais sans le gain de performance
associé à ce mode. Il faut consulter le manuel pour installer les barrettes dans les slots
recommandés.
"""

_MC02_EXERCICES_2 = r"""## Exercice 5 — expliquer

Un emplacement PCIe est annoncé « x16 » sur la carte mère, mais la documentation précise
qu'il n'est câblé électriquement qu'en x4 lorsqu'un second emplacement est utilisé en même
temps. Explique ce que cela signifie concrètement pour l'utilisateur.

**Correction :** La taille physique du connecteur (x16) n'indique pas toujours le nombre
réel de lanes électriques actives. Dans ce cas, une carte installée dans cet emplacement
peut ne recevoir que la bande passante d'un x4 si un second emplacement est occupé en même
temps — ce qui peut réduire les performances d'une carte graphique exigeante, par exemple.

## Exercice 6 — vrai ou faux, justifié

« Un SSD M.2 est toujours un SSD NVMe. » Vrai ou faux ? Justifie ta réponse.

**Correction :** Faux. M.2 est un format de connecteur/composant, pas une technologie de
vitesse. Un emplacement M.2 peut accueillir un SSD SATA ou un SSD NVMe (connecté en PCIe,
plus rapide) — il faut vérifier la documentation de la carte mère pour savoir quel(s)
mode(s) un emplacement M.2 donné supporte.

## Exercice 7 — classer

Classe les éléments suivants selon leur origine et leur rôle : câble ATX 24 broches, câble
EPS, câble SATA Power, câble SATA data.

**Correction :** ATX 24 broches (du PSU vers la carte mère, alimente la carte mère) ; EPS
(du PSU vers la carte mère, alimente le CPU via les VRM) ; SATA Power (du PSU directement
vers le disque, ne passe pas par la carte mère) ; SATA data (de la carte mère vers le
disque, transfert de données uniquement, aucune alimentation).

## Exercice 8 — associer

Associe chaque connecteur F_PANEL à son rôle et précise s'il faut respecter une polarité :
Power SW, Reset SW, Power LED, HDD LED.

**Correction :** Power SW : bouton d'allumage, interrupteur, pas de polarité. Reset SW :
bouton de redémarrage matériel, interrupteur, pas de polarité. Power LED : voyant
d'alimentation, LED, polarité à respecter. HDD LED : voyant d'activité disque, LED,
polarité à respecter.
"""

_MC02_EXERCICES_3 = r"""## Exercice 9 — reconnaître

Pour chacun de ces connecteurs du panneau arrière, indique à quoi il sert : USB-C, RJ45,
jack audio, HDMI.

**Correction :** USB-C : périphériques USB récents (réversible). RJ45 : connexion réseau
filaire (Ethernet). Jack audio : casque/micro/haut-parleurs. HDMI : sortie vidéo (présente
seulement si le GPU intégré est utilisé, ou absente sur une carte mère sans sortie vidéo
intégrée).

## Exercice 10 — expliquer

Explique ce qu'est le POST, et pourquoi son échec empêche tout affichage à l'écran, même si
les ventilateurs tournent.

**Correction :** Le POST (Power-On Self-Test) est la séquence de vérifications matérielles
effectuée par le firmware (BIOS/UEFI) juste après la mise sous tension, avant tout
affichage. Les ventilateurs qui tournent montrent seulement que l'alimentation électrique
de base fonctionne ; si le POST échoue (RAM, GPU ou autre composant essentiel non détecté
correctement), le firmware ne transmet jamais le contrôle à l'affichage.

## Exercice 11 — ordonner

Un PC s'allume mais n'affiche rien à l'écran. Remets dans l'ordre professionnel ces
étapes de diagnostic : (A) réinsérer/tester la RAM ; (B) couper l'alimentation ; (C)
vérifier le câble vidéo et l'écran ; (D) contrôle visuel des connecteurs.

**Correction :** Ordre correct : B → D → A → C (couper l'alimentation, contrôle visuel,
RAM, puis GPU/écran) — on ne manipule jamais un composant sous tension, et on procède du
plus simple/rapide à vérifier vers le plus spécifique.

## Exercice 12 — interpréter un mini-schéma

Un technicien te donne cette description : « CPU socket AM5, carte mère annoncée socket
AM4 ». Que peux-tu en conclure immédiatement, sans autre information ?

**Correction :** Incompatibilité physique certaine : les sockets AM5 et AM4 ne sont pas le
même connecteur, le CPU ne peut pas être installé sur cette carte mère, quelle que soit la
version du BIOS. Il faut soit un CPU socket AM4, soit une carte mère socket AM5.
"""

_MC02_MEMO = r"""# Fiche mémo — Carte mère, formats et connectiques

## Formats

| Format | Taille | Extensibilité |
|---|---|---|
| ATX | Grande | Élevée |
| micro-ATX | Moyenne | Moyenne |
| Mini-ITX | Petite | Faible |

## Compatibilité — ordre de vérification

Besoin → format → socket/CPU/BIOS → RAM → stockage → PCIe → alimentation/connecteurs →
boîtier → manuel/QVL.

## Alimentation de la carte mère

- ATX 24 broches : alimente la carte mère.
- EPS 4/8 broches : alimente le CPU (≠ connecteur GPU).
- SATA Power : vient du PSU directement, pas de la carte mère.

## Pièges à ne jamais oublier

- Format ≠ performances.
- Socket compatible ≠ compatibilité complète (génération, chipset, BIOS).
- x16 physique ≠ toujours x16 électrique.
- M.2 ≠ synonyme de NVMe (SATA possible aussi).
- F_PANEL : interrupteurs sans polarité, LED avec polarité.
- Ne jamais manipuler un composant sous tension ; toujours se protéger de l'ESD.

## Diagnostic no-POST (ordre)

Couper l'alimentation → contrôle visuel → ATX/EPS → RAM → GPU/écran → codes LED/beep →
configuration minimale → clear CMOS → documenter.

<div class="d-print-none mt-3">
    <button type="button" class="btn btn-outline-dark btn-sm" onclick="window.print()">
        Imprimer cette fiche
    </button>
</div>
"""

_MC02_EXAMEN = r"""# Examen final — Carte mère, formats et connectiques

**Consigne :** réponds à chaque question de façon complète et justifiée. Chaque question
vaut 2 points, pour un total de 20 points.

## Question 1 (2 pts)

Explique les différences principales entre les formats ATX, micro-ATX et Mini-ITX.

## Question 2 (2 pts)

Un CPU rentre physiquement dans le socket d'une carte mère. Cela suffit-il à garantir la
compatibilité ? Justifie.

## Question 3 (2 pts)

Explique la différence entre la taille physique d'un emplacement PCIe (ex. x16) et le
nombre réel de lanes électriques actives.

## Question 4 (2 pts)

Décris le rôle des connecteurs ATX 24 broches et EPS, et explique en quoi ils diffèrent
d'un connecteur d'alimentation de carte graphique.

## Question 5 (2 pts)

Cite et explique le rôle de trois connecteurs internes (hors F_PANEL) : par exemple
CPU_FAN, USB interne, audio façade.

## Question 6 (2 pts)

Explique pourquoi « M.2 » n'est pas synonyme de « NVMe ».

## Question 7 (2 pts)

Explique la différence de polarité entre les interrupteurs et les LED du F_PANEL, et ses
conséquences en cas d'inversion.

## Question 8 (2 pts)

Explique le rôle du BIOS/UEFI et du POST dans le démarrage d'un PC.

## Question 9 (2 pts)

Cite trois règles de sécurité à respecter avant d'intervenir à l'intérieur d'un boîtier.

## Question 10 (2 pts)

Un PC s'allume (ventilateurs, voyants) mais n'affiche rien à l'écran. Décris une procédure
structurée de diagnostic, dans l'ordre.
"""

_MC02_EXAMEN_CORRIGE = r"""# Corrigé — Examen final « Carte mère, formats et connectiques »

**Ce bloc n'est jamais publié côté candidat** (non publié) — réservé à la
correction/notation par le formateur depuis l'administration. Barème : 2 points par
question, 20 points au total.

## Question 1 (2 pts)

ATX : grand format, nombreux emplacements. micro-ATX : format intermédiaire, emplacements
réduits. Mini-ITX : très compact, un seul PCIe en général. *(différences de taille et
d'extensibilité, pas de performance intrinsèque)*

## Question 2 (2 pts)

Non. Le socket correspondant est nécessaire mais pas suffisant : il faut aussi vérifier la
génération CPU supportée, le chipset, et la version BIOS. *(1 pt « non » justifié, 1 pt
éléments supplémentaires cités)*

## Question 3 (2 pts)

La taille physique (x16) indique le connecteur ; le nombre de lanes électriques actives
peut être inférieur (x4, x8) selon la carte mère — à vérifier dans la documentation. *(1 pt
distinction, 1 pt conséquence pratique)*

## Question 4 (2 pts)

ATX 24 broches alimente la carte mère, EPS (4/8 broches) alimente le CPU. Différents des
connecteurs d'alimentation GPU (PCIe 6/8 broches, 12V-2x6), non interchangeables. *(1 pt
rôles, 1 pt distinction GPU)*

## Question 5 (2 pts)

Ex. CPU_FAN (ventilateur CPU, surveillé), USB interne (ports USB façade), audio façade
(prise casque/micro façade). *(0,67 pt par connecteur correctement décrit)*

## Question 6 (2 pts)

M.2 est un format de connecteur physique ; un emplacement M.2 peut recevoir un SSD SATA ou
NVMe selon ce que supporte la carte mère. *(1 pt distinction format/technologie, 1 pt
exemple SATA/NVMe)*

## Question 7 (2 pts)

Interrupteurs (Power SW, Reset SW) : pas de polarité, fonctionnent dans les deux sens. LED
(Power LED, HDD LED) : polarité à respecter, ne s'allument pas si inversées. *(1 pt par
catégorie correctement expliquée)*

## Question 8 (2 pts)

BIOS/UEFI : firmware qui initialise le matériel avant l'OS. POST : séquence de
vérifications matérielles juste après la mise sous tension, doit réussir avant tout
affichage. *(1 pt par notion)*

## Question 9 (2 pts)

Ex. couper l'alimentation/débrancher le secteur, se décharger de l'électricité statique
(ESD)/bracelet antistatique, manipuler les composants par les bords, ne jamais forcer un
connecteur. *(2/3 règles pertinentes acceptées, 0,67 pt chacune)*

## Question 10 (2 pts)

Couper l'alimentation → contrôle visuel → vérifier ATX/EPS → RAM → GPU/écran → codes
LED/beep → configuration minimale → clear CMOS → documenter. *(notation qualitative sur 2
points selon la structure et l'ordre logique de la réponse)*
"""

MC02_BLOCKS = [
    {
        "title": "Plan du mini-cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_PLAN,
        "position": 1,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "1. Rôle détaillé de la carte mère — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_ROLE,
        "position": 2,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "2. Formats ATX, micro-ATX, Mini-ITX — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_FORMATS,
        "position": 3,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "3. Socket CPU et compatibilité — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_SOCKET,
        "position": 4,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "4. Chipset — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_CHIPSET,
        "position": 5,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "5. Slots RAM (DIMM) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_RAM_SLOTS,
        "position": 6,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "6. PCI Express (PCIe) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_PCIE,
        "position": 7,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "7. Stockage sur la carte mère (SATA, M.2) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_STOCKAGE_CM,
        "position": 8,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "8. Alimentation interne (ATX 24 broches, EPS) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_ALIM_INTERNE,
        "position": 9,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "9. Connecteurs internes — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_CONNECTEURS_INTERNES,
        "position": 10,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "10. Connectique arrière (E/S) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_IO_ARRIERE,
        "position": 11,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "11. F_PANEL — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_F_PANEL,
        "position": 12,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "12. BIOS/UEFI et POST — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_BIOS_UEFI,
        "position": 13,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "13. Méthode de compatibilité — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_METHODE_COMPATIBILITE,
        "position": 14,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "14. Diagnostic professionnel : pas de POST — Exemple",
        "type": BlockType.MARKDOWN,
        "content": _MC02_DIAGNOSTIC,
        "position": 15,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "15. Sécurité et décharge électrostatique (ESD) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_SECURITE_ESD,
        "position": 16,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "16. Vocabulaire FR/EN — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC02_VOCAB_FR_EN,
        "position": 17,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "Carte mère — Exercices (1/3 : formats, socket, chipset, RAM)",
        "type": BlockType.MARKDOWN,
        "content": _MC02_EXERCICES_1,
        "position": 18,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Carte mère — Exercices (2/3 : PCIe, stockage, alimentation, F_PANEL)",
        "type": BlockType.MARKDOWN,
        "content": _MC02_EXERCICES_2,
        "position": 19,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Carte mère — Exercices (3/3 : E/S, POST, diagnostic)",
        "type": BlockType.MARKDOWN,
        "content": _MC02_EXERCICES_3,
        "position": 20,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Carte mère — Génère ton propre exercice (IA)",
        "type": BlockType.AI_EXERCISE,
        "content": AIExerciseBlockConfig(
            context_key="ampcr-mc02",
            intro=(
                "En complément des exercices ci-dessus : choisis une difficulté, génère un "
                "nouvel exercice sur la carte mère, réponds, puis demande une correction "
                "personnalisée. L'exercice reste strictement dans la matière de ce "
                "mini-cours."
            ),
        ).to_json(),
        "position": 21,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Fiche mémo — Carte mère, formats et connectiques",
        "type": BlockType.MARKDOWN,
        "content": _MC02_MEMO,
        "position": 22,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "Examen final — Carte mère, formats et connectiques (10 questions, 20 points)",
        "type": BlockType.MARKDOWN,
        "content": _MC02_EXAMEN,
        "position": 23,
        "is_published": True,
        "space": BlockSpace.EXAM,
    },
    {
        "title": "Examen final — Corrigé (réservé formateur, non publié)",
        "type": BlockType.MARKDOWN,
        "content": _MC02_EXAMEN_CORRIGE,
        "position": 24,
        "is_published": False,
        "space": BlockSpace.EXAM,
    },
]

# Contenu réel du mini-cours 03 Informatique AMPCR (« CPU et mémoire RAM »), ticket #14 :
# contenu et périmètre pédagogique fournis par ChatGPT (chef de projet), rédigés ici sans
# en changer la portée. Réutilise exactement l'architecture des tickets #10/#12 (blocs
# markdown, classification par titre, correction masquée générique, bloc ai_exercise +
# contexte pédagogique borné) — aucune nouvelle architecture.

MC03_CODE = "MC03"
MC03_TITLE = "CPU et mémoire RAM"

_MC03_PLAN = r"""# CPU et mémoire RAM

Ce mini-cours prolonge les mini-cours 01 et 02 : après la vue d'ensemble d'un PC et le
détail de la carte mère, on approfondit les deux composants les plus souvent mis en avant
commercialement — le CPU et la RAM — et on apprend à ne pas se laisser piéger par des
chiffres mal interprétés (GHz, TDP, Go, bits).

## Objectifs

À la fin de ce mini-cours, tu sauras :

- expliquer le rôle du CPU et les facteurs qui influencent réellement ses performances ;
- comparer deux CPU sans te fier à un seul chiffre ;
- expliquer les générations de RAM, les canaux mémoire et leurs conditions d'installation ;
- distinguer RAM, VRAM et stockage sans confusion ;
- appliquer une procédure de diagnostic structurée en cas de panne RAM ou thermique ;
- éviter les pièges d'unités et d'interprétation les plus fréquents à l'examen.

## Sommaire

1. Rôle du CPU et cycle d'exécution
2. Cœurs, threads et fréquence
3. IPC et hiérarchie de cache (L1/L2/L3)
4. Architecture 32/64 bits
5. Socket, génération et compatibilité
6. TDP, refroidissement et throttling
7. CPU avec ou sans graphique intégré
8. Rôle et capacité de la RAM
9. DDR3, DDR4, DDR5
10. DIMM, SO-DIMM et canaux mémoire
11. Capacité maximale et compatibilité
12. XMP/EXPO et ECC
13. RAM, VRAM et stockage
14. Goulot d'étranglement et symptômes
15. Diagnostic RAM et CPU/thermique
16. Unités et pièges d'examen
17. Vocabulaire FR/EN

*Ce mini-cours s'appuie sur le mini-cours 02 (carte mère, socket, connecteurs) : la
compatibilité CPU/RAM/carte mère y a déjà été introduite, elle est ici approfondie côté
CPU et RAM.*
"""

_MC03_CPU_ROLE = r"""## Rôle du CPU (rappel et approfondissement)

Le CPU exécute les instructions des programmes. De façon simplifiée, chaque instruction
suit un cycle en trois temps :

<div class="jc-flow">
    <div class="jc-flow-step">Instruction<br><small>lue en mémoire</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">Traitement<br><small>données manipulées</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">Résultat<br><small>écrit en mémoire</small></div>
</div>

Ce cycle se répète des milliards de fois par seconde. C'est cette répétition extrêmement
rapide, pas une « intelligence » du CPU, qui donne l'impression que l'ordinateur
« réfléchit ».

## À retenir

Le CPU ne fait qu'exécuter des instructions très simples, très vite, dans un ordre précis —
toute la complexité perçue vient du nombre d'instructions exécutées, pas de leur
sophistication individuelle.
"""

_MC03_CORES_FREQ = r"""## Cœurs et threads

Un CPU moderne contient plusieurs **cœurs** (*cores*), chacun capable de traiter des
instructions de façon indépendante — plusieurs tâches peuvent donc progresser en
parallèle.

Le **SMT** (*Simultaneous Multi-Threading*, appelé Hyper-Threading chez Intel) permet à un
seul cœur physique de traiter deux **threads** (fils d'exécution) en même temps, en
exploitant les temps morts internes du cœur. Un thread SMT n'égale pas un cœur physique
complet : le gain dépend fortement du type de tâche.

## Fréquence : base, boost, et GHz

La fréquence (en GHz) indique le nombre de cycles d'horloge par seconde. Les CPU modernes
annoncent une fréquence **de base** (garantie en continu) et une fréquence **boost**
(atteinte ponctuellement, sous conditions thermiques favorables, pas en continu).

> **Piège fréquent :** un CPU à fréquence plus élevée n'est pas automatiquement plus
> rapide qu'un CPU à fréquence plus basse. Le nombre de cœurs, l'IPC (voir section
> suivante), la génération et la charge de travail réelle comptent au moins autant que le
> chiffre en GHz seul.
"""

_MC03_IPC_CACHE = r"""## IPC : l'autre moitié de l'équation

L'**IPC** (*Instructions Per Cycle*) mesure, en moyenne, combien d'instructions un CPU
traite à chaque cycle d'horloge. Deux CPU à la même fréquence peuvent avoir des
performances très différentes si leur IPC diffère : un CPU plus récent, à IPC plus élevé,
peut dépasser un CPU plus ancien pourtant cadencé plus haut.

Retiens la logique globale, sans qu'il soit nécessaire de calculer l'IPC toi-même :
performance ≈ fréquence × IPC × nombre de cœurs utiles à la tâche — jamais la fréquence
seule.

## Le cache : mémoire très rapide, très proche du CPU

Comme vu au mini-cours 01, le cache est une mémoire minuscule mais extrêmement rapide,
intégrée au CPU. Il existe en plusieurs niveaux :

| Niveau | Taille typique | Vitesse | Rôle |
|---|---|---|---|
| L1 | Quelques dizaines de Ko, par cœur | La plus rapide | Données/instructions immédiates du cœur |
| L2 | Quelques centaines de Ko à quelques Mo, par cœur | Rapide | Relais entre L1 et L3 |
| L3 | Plusieurs Mo, partagé entre les cœurs | Plus lente que L1/L2, bien plus rapide que la RAM | Réservoir commun, réduit les accès à la RAM |

Plus une donnée est trouvée dans un niveau de cache proche (L1), plus vite le CPU peut
l'utiliser ; à défaut, il doit aller la chercher plus loin (L2, L3, puis RAM), ce qui prend
plus de temps à chaque niveau.
"""

_MC03_32_64_BITS = r"""## Ce que « bits » désigne ici

L'architecture 32 ou 64 bits d'un CPU détermine notamment la taille des données qu'il
traite nativement et surtout la quantité de mémoire vive qu'il peut adresser.

| | 32 bits | 64 bits |
|---|---|---|
| RAM adressable (théorique) | Environ 4 Go maximum | Bien au-delà (largement suffisant aujourd'hui) |
| Système d'exploitation requis | Version 32 bits | Version 64 bits (aujourd'hui la norme) |
| Compatibilité logicielle | Logiciels 32 bits uniquement | Logiciels 32 bits **et** 64 bits en général |

## Piège d'examen

> **Piège fréquent :** passer de 32 à 64 bits ne rend **pas** un CPU « deux fois plus
> rapide ». Cela change la quantité de mémoire adressable et certaines capacités de
> traitement, pas un doublement direct de la vitesse d'exécution.

*Le sujet est traité ici sans digression historique sur l'évolution des architectures —
l'essentiel est de connaître le lien avec l'OS et la mémoire adressable.*
"""

_MC03_SOCKET_COMPAT = r"""## Rappel du mini-cours 02

Le socket détermine la compatibilité physique CPU/carte mère ; la génération du CPU, le
chipset et la version du firmware (BIOS/UEFI) déterminent la compatibilité **complète**
(voir mini-cours 02, section Socket CPU et compatibilité).

## Ce qu'il faut ajouter côté CPU

Un même socket peut accueillir plusieurs **générations** de CPU au fil du temps, mais pas
indéfiniment : le fabricant publie une liste de compatibilité (CPU support list) par carte
mère, qui évolue avec les mises à jour de firmware.

## Méthode examen

Avant d'installer ou de recommander un CPU : vérifier socket → génération supportée par la
carte mère → version de firmware minimale requise → mise à jour du firmware si
nécessaire.
"""

_MC03_TDP_THROTTLING = r"""## TDP : un indicateur de conception, pas une mesure de consommation exacte

Le **TDP** (*Thermal Design Power*) exprime, en watts, la quantité de chaleur que le
système de refroidissement doit être capable d'évacuer en fonctionnement soutenu typique.

> **Piège fréquent :** le TDP n'est **pas** une mesure exacte de la consommation
> électrique instantanée du CPU. La consommation réelle varie selon la charge de travail et
> peut, à certains moments (boost), dépasser temporairement le TDP annoncé. Le TDP sert
> avant tout à dimensionner le refroidissement, pas à calculer une facture électrique
> précise.

## Refroidissement et throttling thermique

Le refroidisseur (ventirad, watercooling...) évacue la chaleur produite par le CPU. Si la
température devient trop élevée, le CPU réduit automatiquement sa fréquence pour se
protéger : c'est le **throttling thermique**. Conséquence pratique : un refroidissement
insuffisant ou mal installé peut faire chuter les performances, même sans panne matérielle
au sens strict.
"""

_MC03_GPU_INTEGRE = r"""## Conséquence pratique lors d'un diagnostic

Comme vu au mini-cours 01, certains CPU intègrent un GPU, d'autres non. Cette distinction a
une conséquence pratique importante en diagnostic : un CPU **sans** graphique intégré,
installé sur une carte mère sans carte graphique dédiée fonctionnelle, ne produira **aucun
affichage**, même si tout le reste fonctionne correctement — ce n'est pas nécessairement
une panne.

> **Piège fréquent :** face à une absence d'affichage, toujours vérifier si le CPU dispose
> d'un graphique intégré avant de conclure à une panne de carte graphique ou de carte
> mère.
"""

_MC03_RAM_ROLE = r"""## Rappel et approfondissement

Comme vu au mini-cours 01, la RAM est une mémoire de travail temporaire et volatile. Trois
caractéristiques la décrivent :

| Caractéristique | Ce qu'elle mesure |
|---|---|
| Capacité (Go) | Quantité de données que la RAM peut contenir simultanément |
| Fréquence / débit | Vitesse à laquelle les données transitent |
| Latence | Délai avant qu'une donnée demandée soit disponible |

## Capacité et latence : deux choses différentes

Une RAM plus rapide (fréquence élevée) n'a pas forcément une latence plus faible : les deux
caractéristiques évoluent parfois en sens contraires selon les modules. Pour un usage
courant, la capacité suffisante compte généralement plus que quelques nanosecondes de
latence.
"""

_MC03_DDR_GENERATIONS = r"""## Générations incompatibles

| Génération | Statut | Compatibilité |
|---|---|---|
| DDR3 | Ancienne, encore présente sur du matériel plus âgé | Non compatible avec DDR4/DDR5 |
| DDR4 | Très répandue | Non compatible avec DDR3/DDR5 |
| DDR5 | Génération actuelle | Non compatible avec DDR3/DDR4 |

## Incompatibilité physique et électrique

> **Piège fréquent :** les générations DDR ne sont **pas** interchangeables : le
> détrompeur (encoche) est positionné différemment selon la génération, ce qui empêche
> physiquement d'insérer le mauvais type de barrette dans un slot — et même si cela
> semblait possible, les tensions électriques diffèrent. Une carte mère ne supporte
> qu'**une seule** génération de RAM.

## DDR5 n'est pas juste « DDR4 en plus rapide »

> **Piège fréquent :** présenter la DDR5 comme une simple version accélérée de la DDR4 est
> une erreur d'examen classique. Il s'agit d'une génération différente, avec une
> compatibilité physique/électrique différente — une carte mère DDR4 n'accepte jamais de
> DDR5, quelle que soit la vitesse annoncée.

*Le terme « DDR » reste utilisé couramment même pour désigner la génération la plus
récente : ce n'est pas un vocabulaire dépassé.*
"""

_MC03_DIMM_CHANNELS = r"""## DIMM et SO-DIMM

| Format | Taille | Usage typique |
|---|---|---|
| DIMM | Standard, plus grand | PC de bureau |
| SO-DIMM (*Small Outline DIMM*) | Compact | Ordinateurs portables, PC très compacts |

## Canaux mémoire et population des slots

Comme introduit au mini-cours 02, le mode **dual-channel** exige d'installer les
barrettes dans des slots précis (souvent indiqués par une couleur), selon le **manuel** de
la carte mère.

> **Piège fréquent :** des barrettes installées dans les mauvais slots fonctionnent
> généralement quand même (le PC démarre normalement), mais sans le gain de bande passante
> du dual-channel — aucune erreur visible n'avertit l'utilisateur.
"""

_MC03_CAPACITE_MAX = r"""## Deux limites à croiser

La capacité maximale de RAM installable dépend à la fois :

- de la **carte mère** (nombre de slots, capacité maximale supportée) ;
- du **CPU** (capacité maximale de RAM qu'il peut adresser/gérer).

La limite réelle d'une configuration est toujours la plus basse des deux. Vérifier les
deux documentations (carte mère et CPU) avant de recommander une capacité de RAM.
"""

_MC03_XMP_ECC = r"""## XMP / EXPO : des profils de paramètres mémoire

Par défaut, une carte mère fait fonctionner la RAM à une fréquence standard, prudente. Les
profils **XMP** (Intel) ou **EXPO** (AMD) permettent d'activer, en un clic dans le
BIOS/UEFI, des paramètres plus performants **déjà validés par le fabricant de la RAM**,
au-delà de la fréquence de base.

> **Piège fréquent :** XMP/EXPO reste un paramétrage au-delà des spécifications de base
> (JEDEC) : bien que validé par le fabricant de la RAM, ce n'est pas garanti par le
> fabricant de la carte mère ou du CPU dans toutes les configurations — à activer avec
> prudence et à tester après activation.

## ECC : une notion à connaître, sans approfondissement serveur

La RAM **ECC** (*Error-Correcting Code*) détecte et corrige automatiquement certaines
erreurs mineures de mémoire. Elle est surtout utilisée dans les serveurs et stations de
travail critiques, rarement sur un PC grand public standard. Il suffit ici de connaître
son existence et son usage typique, sans entrer dans le détail de son fonctionnement.
"""

_MC03_RAM_VRAM_STOCKAGE = r"""## Trois mémoires, trois rôles

| | RAM | VRAM | Stockage |
|---|---|---|---|
| Rôle | Mémoire de travail générale (système, programmes) | Mémoire dédiée aux données graphiques | Conservation durable des données |
| Volatile ? | Oui | Oui | Non |
| Où se trouve-t-elle ? | Barrettes sur la carte mère | Intégrée à la carte graphique | HDD/SSD |

## À retenir

Ne jamais confondre ces trois mémoires dans une phrase du type « mon PC a X Go » — préciser
systématiquement laquelle est concernée (voir aussi mini-cours 01, section RAM et
stockage).
"""

_MC03_GOULOT = r"""## Un PC est un système

Augmenter un seul composant (par exemple ajouter de la RAM) n'améliore pas forcément les
performances globales : si un autre composant (CPU, stockage) limite déjà le système, il
devient le **goulot d'étranglement** (*bottleneck*) — la performance globale reste limitée
par le composant le plus faible pour la tâche concernée.

> **Piège fréquent :** ajouter de la RAM sur un PC qui en a déjà suffisamment pour l'usage
> prévu n'accélère généralement rien. L'augmentation de capacité n'aide que si la RAM était
> réellement le facteur limitant.

## Symptômes typiques d'un manque de RAM

- Ralentissements progressifs quand plusieurs applications sont ouvertes.
- Recours à la **pagination/swap** (le système utilise le stockage comme RAM de secours,
  beaucoup plus lent).
- Applications qui se ferment ou affichent des erreurs de mémoire dans les cas extrêmes.

## Ne pas confondre avec un manque d'espace disque

Un disque presque plein peut aussi ralentir un PC (moins d'espace pour les fichiers
temporaires), mais les symptômes et la solution diffèrent d'un manque de RAM — voir
mini-cours 01, exercice sur ce diagnostic.
"""

_MC03_DIAGNOSTIC = r"""## Diagnostic RAM

<div class="jc-flow">
    <div class="jc-flow-step">1. Couper<br><small>l'alimentation</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">2. Inspection<br><small>visuelle des barrettes</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">3. Réinsertion<br><small>un module à la fois</small></div>
    <div class="jc-flow-arrow">→</div>
    <div class="jc-flow-step">4. Test<br><small>outil de test mémoire</small></div>
</div>

1. Couper l'alimentation avant toute manipulation (sécurité ESD, voir mini-cours 02).
2. Inspection visuelle des barrettes et des slots (poussière, dégâts, mauvaise insertion).
3. Réinsérer chaque barrette fermement, puis tester **un module à la fois** dans le slot
   recommandé par le manuel, pour isoler un module défectueux.
4. Utiliser un outil de test mémoire dédié pour une vérification plus poussée.

> **Piège fréquent :** un test mémoire qui ne détecte rien ne garantit pas l'absence totale
> de panne — certains défauts intermittents échappent à un test unique. Un résultat propre
> est un indice favorable, pas une certitude absolue.

## Diagnostic CPU / thermique

1. Vérifier les températures (logiciel de monitoring si le système démarre).
2. Vérifier que le ventilateur du CPU tourne réellement.
3. Vérifier l'installation du refroidisseur et l'état de la pâte thermique (mal appliquée
   ou desséchée = mauvais transfert de chaleur).
4. Observer si un throttling thermique est en cause (baisse de performance sous charge).
5. Vérifier la compatibilité firmware si le CPU est récent sur une carte mère plus
   ancienne (voir section 5).

## POST / no-POST : causes possibles côté CPU/RAM

RAM mal installée ou défectueuse, CPU non reconnu (firmware à mettre à jour), connecteur
EPS CPU non branché (voir mini-cours 02), absence de sortie vidéo si le CPU n'a pas de
graphique intégré et qu'aucune carte dédiée n'est installée.
"""

_MC03_UNITES_PIEGES = r"""## Bit vs octet

| Symbole | Signification | Relation |
|---|---|---|
| b (minuscule) | bit | Unité de base (0 ou 1) |
| B (majuscule) | octet (byte) | 8 bits |

Confondre **b** et **B** peut fausser une lecture de débit réseau (souvent en mégabits/s,
Mb/s) avec une capacité de stockage (toujours en Go/To, gigaoctets/téraoctets).

## Synthèse des pièges du mini-cours

- Go de RAM ≠ Go de stockage (rappel du mini-cours 01).
- GHz seul ne mesure pas la performance absolue d'un CPU (IPC, cœurs, génération comptent
  aussi).
- Plus de RAM n'accélère pas systématiquement un PC si la capacité était déjà suffisante.
- DDR5 n'est pas simplement « DDR4 en plus rapide » : la compatibilité diffère.
- 64 bits ne signifie pas « deux fois plus rapide » que 32 bits.
- Le TDP n'est pas une mesure exacte de la consommation électrique du CPU.
"""

_MC03_VOCAB_FR_EN = r"""## Vocabulaire à connaître (français / anglais)

| Français | Anglais |
|---|---|
| Processeur | CPU / Processor |
| Cœur | Core |
| Fil d'exécution | Thread |
| Fréquence / horloge | Clock / Frequency |
| Antémémoire | Cache |
| Support de processeur | Socket |
| Réduction thermique automatique | Thermal throttling |
| Mémoire vive | RAM / Memory |
| Barrette mémoire (format standard) | DIMM |
| Barrette mémoire (format compact) | SO-DIMM |
| Canal mémoire | Channel |
| Latence | Latency |
| Débit | Bandwidth |
| Correction d'erreur | ECC |
| Graphique intégré | Integrated graphics |

## Méthode examen

Comme dans les mini-cours précédents : pour un sigle anglais (IPC, TDP, ECC, DIMM...),
retrouve le terme complet en anglais avant de le traduire.
"""

_MC03_EXERCICES_1 = r"""## Exercice 1 — comparer

Deux CPU sont proposés : CPU A (3,5 GHz, 4 cœurs, génération ancienne) et CPU B (3,0 GHz,
8 cœurs, génération récente, IPC plus élevé). Pour une tâche fortement multi-threadée
(montage vidéo), lequel recommandes-tu ? Justifie sans te limiter à la fréquence.

**Correction :** CPU B est généralement préférable pour une tâche multi-threadée : plus de
cœurs à exploiter, et un IPC plus élevé compense largement la fréquence légèrement plus
basse. La fréquence seule (CPU A plus élevée) ne suffit pas à conclure — cœurs et IPC
comptent au moins autant.

## Exercice 2 — interpréter

Une fiche technique indique : « 6 cœurs / 12 threads, 3,7 GHz base / 4,6 GHz boost ».
Explique ce que signifie chacun de ces chiffres.

**Correction :** 6 cœurs physiques, chacun traitant 2 threads grâce au SMT/Hyper-Threading
(12 threads au total, pas 12 cœurs réels). 3,7 GHz est la fréquence garantie en continu ;
4,6 GHz est une fréquence boost atteinte ponctuellement, sous conditions thermiques
favorables, pas en continu.

## Exercice 3 — expliquer

Explique pourquoi une donnée présente en cache L1 est traitée plus vite qu'une donnée qui
doit être cherchée en RAM, en citant les niveaux intermédiaires.

**Correction :** Le CPU cherche d'abord en L1 (la plus rapide, la plus proche) ; si absente,
il cherche en L2, puis en L3 (partagé entre cœurs, plus lent que L1/L2 mais bien plus
rapide que la RAM), et enfin en RAM si la donnée n'est dans aucun niveau de cache — chaque
niveau supplémentaire ajoute un délai.

## Exercice 4 — expliquer un piège

Un fabricant annonce un CPU « TDP 65 W ». Un client en conclut que ce CPU consomme
exactement 65 W en permanence. Explique pourquoi ce raisonnement est incorrect.

**Correction :** Le TDP est un indicateur de conception thermique (la chaleur que le
refroidissement doit pouvoir évacuer en usage soutenu typique), pas une mesure exacte de
consommation instantanée. La consommation réelle varie selon la charge, et peut dépasser
temporairement le TDP lors d'un boost.
"""

_MC03_EXERCICES_2 = r"""## Exercice 5 — vérifier une compatibilité

Une carte mère supporte la DDR4 jusqu'à 3200 MHz. Un technicien propose d'y installer des
barrettes DDR5. Est-ce possible ? Explique.

**Correction :** Non, impossible. DDR4 et DDR5 ne sont pas compatibles physiquement
(détrompeur différent) ni électriquement (tensions différentes). Une carte mère DDR4
n'accepte jamais de barrettes DDR5, quelle que soit leur fréquence annoncée.

## Exercice 6 — choisir le bon format

Un client veut ajouter de la RAM à son ordinateur portable. Doit-il acheter des barrettes
DIMM ou SO-DIMM ? Pourquoi ?

**Correction :** SO-DIMM — format compact utilisé dans les ordinateurs portables et les PC
très compacts. Le format DIMM standard, plus grand, est réservé aux PC de bureau et ne
rentre pas physiquement dans un portable.

## Exercice 7 — expliquer le dual-channel

Une carte mère a 4 slots RAM (2 slots noirs, 2 slots gris) et le manuel recommande
d'utiliser les deux slots de même couleur pour 2 barrettes. Un technicien installe les 2
barrettes dans un slot noir et un slot gris. Le PC démarre normalement. A-t-il bien fait ?

**Correction :** Le PC fonctionne, mais le technicien n'a probablement pas respecté la
configuration recommandée pour le dual-channel : les barrettes doivent être dans des slots
de même couleur pour bénéficier du mode multi-canal. Sans erreur visible, la RAM
fonctionne alors en simple canal, avec une bande passante réduite.

## Exercice 8 — classer

Classe les éléments suivants selon qu'ils désignent de la RAM, de la VRAM ou du stockage :
barrette DIMM sur la carte mère, mémoire intégrée à une carte graphique dédiée, SSD NVMe,
barrette SO-DIMM d'un portable.

**Correction :** RAM : barrette DIMM sur la carte mère, barrette SO-DIMM d'un portable.
VRAM : mémoire intégrée à une carte graphique dédiée. Stockage : SSD NVMe.
"""

_MC03_EXERCICES_3 = r"""## Exercice 9 — diagnostiquer

Un PC ne démarre pas (pas d'affichage), et la carte mère émet une série de bips répétés
que le manuel associe à une erreur mémoire. Décris la procédure de diagnostic à suivre.

**Correction :** Couper l'alimentation, inspecter visuellement les barrettes et les slots,
réinsérer fermement chaque barrette, puis tester une seule barrette à la fois dans le slot
recommandé par le manuel pour isoler un module défectueux ; utiliser un outil de test
mémoire si le problème persiste.

## Exercice 10 — diagnostiquer

Un PC ralentit fortement après quelques minutes d'utilisation intensive, et les
ventilateurs deviennent très bruyants. Quelle piste explorer en priorité, et comment la
vérifier ?

**Correction :** Piste prioritaire : throttling thermique. Vérifier les températures
(logiciel de monitoring), que le ventilateur du CPU tourne correctement, et l'état du
refroidisseur et de la pâte thermique — une pâte mal appliquée ou desséchée réduit le
transfert de chaleur et provoque une surchauffe sous charge.

## Exercice 11 — expliquer une unité

Une offre internet annonce « 100 Mb/s ». Un client pense qu'il pourra télécharger un fichier
de 100 Mo en une seconde. Explique son erreur.

**Correction :** Confusion entre bit (Mb, minuscule) et octet (Mo, majuscule) : 1 octet =
8 bits, donc 100 Mb/s correspond à environ 12,5 Mo/s réels, pas 100 Mo/s. Le débit annoncé
en mégabits par seconde est près de 8 fois inférieur à ce que suggère une lecture rapide en
« Mo ».

## Exercice 12 — identifier un goulot d'étranglement

Un PC dispose de 32 Go de RAM (largement suffisant pour l'usage du client) mais d'un vieux
disque dur mécanique lent. Le client envisage de doubler la RAM à 64 Go pour améliorer les
performances. Est-ce la bonne solution ? Que proposer à la place ?

**Correction :** Non : la RAM n'est pas le facteur limitant ici (32 Go suffisaient déjà).
Le goulot d'étranglement est probablement le disque dur mécanique lent. Remplacer le
disque par un SSD apporterait un gain de performance bien plus perceptible qu'ajouter de
la RAM déjà suffisante.
"""

_MC03_MEMO = r"""# Fiche mémo — CPU et mémoire RAM

## CPU

| Facteur | Ce qu'il faut retenir |
|---|---|
| Fréquence (GHz) | Ne suffit jamais seule : IPC, cœurs, génération comptent aussi |
| Cœurs / threads | Plusieurs cœurs = parallélisme ; SMT ≠ cœur physique complet |
| Cache L1/L2/L3 | Plus proche = plus rapide, plus petit |
| TDP | Indicateur thermique de conception, pas la consommation exacte |
| 32/64 bits | Change la RAM adressable, pas un doublement de vitesse |

## RAM

| Notion | À retenir |
|---|---|
| DDR3/DDR4/DDR5 | Générations incompatibles entre elles (physique et électrique) |
| DIMM / SO-DIMM | Format standard (PC bureau) / format compact (portable) |
| Dual-channel | Slots précis à respecter (manuel), sinon perte de bande passante silencieuse |
| XMP/EXPO | Profil au-delà des specs de base, validé par le fabricant RAM |
| ECC | Correction d'erreurs, surtout serveurs/stations critiques |
| RAM vs VRAM vs stockage | Trois mémoires différentes, ne jamais confondre |

## Pièges à ne jamais oublier

- GHz seul ≠ performance absolue.
- TDP ≠ consommation électrique exacte.
- 64 bits ≠ deux fois plus rapide que 32 bits.
- DDR5 ≠ « DDR4 en plus rapide » : compatibilité différente.
- Plus de RAM n'aide que si la RAM était le facteur limitant.
- bit (b) ≠ octet (B) : 1 octet = 8 bits.

## Diagnostic express

RAM : couper alimentation → inspection → réinsertion, un module à la fois → outil de test.
Thermique : températures → ventilateur → pâte thermique/refroidisseur → throttling.

<div class="d-print-none mt-3">
    <button type="button" class="btn btn-outline-dark btn-sm" onclick="window.print()">
        Imprimer cette fiche
    </button>
</div>
"""

_MC03_EXAMEN = r"""# Examen final — CPU et mémoire RAM

**Consigne :** réponds à chaque question de façon complète et justifiée. Chaque question
vaut 2 points, pour un total de 20 points.

## Question 1 (2 pts)

Explique le rôle du CPU et décris, en trois étapes, le cycle simplifié d'exécution d'une
instruction.

## Question 2 (2 pts)

Explique pourquoi la fréquence (GHz) seule ne suffit pas à comparer deux CPU.

## Question 3 (2 pts)

Décris le rôle de la hiérarchie de cache (L1, L2, L3) et pourquoi plusieurs niveaux
existent.

## Question 4 (2 pts)

Explique pourquoi un CPU compatible avec le socket d'une carte mère n'est pas
automatiquement pleinement compatible.

## Question 5 (2 pts)

Explique le rôle de la RAM et pourquoi elle est dite volatile.

## Question 6 (2 pts)

Explique pourquoi les générations DDR3, DDR4 et DDR5 ne sont pas compatibles entre elles.

## Question 7 (2 pts)

Explique le principe du dual-channel et la condition nécessaire à son bon fonctionnement.

## Question 8 (2 pts)

Explique la différence entre bit et octet, et pourquoi confondre Go de RAM et Go de
stockage est une erreur fréquente.

## Question 9 (2 pts)

Décris une procédure structurée de diagnostic en cas de panne mémoire suspectée (no-POST).

## Question 10 (2 pts)

Décris une procédure structurée de diagnostic en cas de ralentissement suspecté d'origine
thermique.
"""

_MC03_EXAMEN_CORRIGE = r"""# Corrigé — Examen final « CPU et mémoire RAM »

**Ce bloc n'est jamais publié côté candidat** (non publié) — réservé à la
correction/notation par le formateur depuis l'administration. Barème : 2 points par
question, 20 points au total.

## Question 1 (2 pts)

Le CPU exécute les instructions des programmes. Cycle simplifié : lecture de l'instruction
→ traitement des données → écriture du résultat. *(1 pt rôle, 1 pt cycle en 3 étapes)*

## Question 2 (2 pts)

L'IPC, le nombre de cœurs et la génération influencent autant la performance réelle que la
fréquence ; deux CPU à fréquences égales peuvent avoir des performances très différentes.
*(1 pt affirmation correcte, 1 pt au moins un facteur supplémentaire cité)*

## Question 3 (2 pts)

L1 : le plus rapide, le plus proche du cœur. L2 : relais intermédiaire. L3 : partagé entre
cœurs, plus lent mais plus rapide que la RAM. Plusieurs niveaux réduisent les accès coûteux
à la RAM. *(1 pt hiérarchie correcte, 1 pt rôle global)*

## Question 4 (2 pts)

Le socket assure seulement la compatibilité physique ; il faut aussi vérifier la génération
supportée, le chipset et la version du firmware/BIOS. *(1 pt socket = nécessaire pas
suffisant, 1 pt éléments additionnels cités)*

## Question 5 (2 pts)

La RAM est la mémoire de travail temporaire utilisée pendant l'exécution des programmes ;
volatile car son contenu est perdu à l'extinction du PC. *(1 pt rôle, 1 pt volatilité
expliquée)*

## Question 6 (2 pts)

Chaque génération DDR a un détrompeur différent (incompatibilité physique) et des tensions
électriques différentes (incompatibilité électrique) : aucune interchangeabilité possible.
*(1 pt par type d'incompatibilité)*

## Question 7 (2 pts)

Le dual-channel fait fonctionner deux barrettes en parallèle pour augmenter la bande
passante ; il exige d'installer les barrettes dans les slots précis indiqués par le manuel
de la carte mère. *(1 pt principe, 1 pt condition d'installation)*

## Question 8 (2 pts)

1 octet (B) = 8 bits (b) ; confondre les deux fausse la lecture d'un débit (Mb/s) avec une
capacité (Go). Go de RAM et Go de stockage désignent deux mémoires différentes malgré la
même unité. *(1 pt bit/octet, 1 pt RAM/stockage)*

## Question 9 (2 pts)

Couper l'alimentation → inspection visuelle → réinsertion des barrettes → test un module à
la fois dans le slot recommandé → outil de test mémoire si besoin. *(notation qualitative
sur l'ordre et la complétude de la procédure)*

## Question 10 (2 pts)

Vérifier les températures → vérifier le ventilateur CPU → vérifier l'installation du
refroidisseur et la pâte thermique → identifier un éventuel throttling. *(notation
qualitative sur l'ordre et la complétude de la procédure)*
"""

MC03_BLOCKS = [
    {
        "title": "Plan du mini-cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_PLAN,
        "position": 1,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "1. Rôle du CPU et cycle d'exécution — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_CPU_ROLE,
        "position": 2,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "2. Cœurs, threads et fréquence — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_CORES_FREQ,
        "position": 3,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "3. IPC et hiérarchie de cache (L1/L2/L3) — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_IPC_CACHE,
        "position": 4,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "4. Architecture 32/64 bits — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_32_64_BITS,
        "position": 5,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "5. Socket, génération et compatibilité — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_SOCKET_COMPAT,
        "position": 6,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "6. TDP, refroidissement et throttling — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_TDP_THROTTLING,
        "position": 7,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "7. CPU avec ou sans graphique intégré — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_GPU_INTEGRE,
        "position": 8,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "8. Rôle et capacité de la RAM — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_RAM_ROLE,
        "position": 9,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "9. DDR3, DDR4, DDR5 — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_DDR_GENERATIONS,
        "position": 10,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "10. DIMM, SO-DIMM et canaux mémoire — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_DIMM_CHANNELS,
        "position": 11,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "11. Capacité maximale et compatibilité — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_CAPACITE_MAX,
        "position": 12,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "12. XMP/EXPO et ECC — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_XMP_ECC,
        "position": 13,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "13. RAM, VRAM et stockage — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_RAM_VRAM_STOCKAGE,
        "position": 14,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "14. Goulot d'étranglement et symptômes — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_GOULOT,
        "position": 15,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "15. Diagnostic RAM et CPU/thermique — Exemple",
        "type": BlockType.MARKDOWN,
        "content": _MC03_DIAGNOSTIC,
        "position": 16,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "16. Unités et pièges d'examen — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_UNITES_PIEGES,
        "position": 17,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "17. Vocabulaire FR/EN — Cours",
        "type": BlockType.MARKDOWN,
        "content": _MC03_VOCAB_FR_EN,
        "position": 18,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "CPU et RAM — Exercices (1/3 : CPU, fréquence, cache, TDP)",
        "type": BlockType.MARKDOWN,
        "content": _MC03_EXERCICES_1,
        "position": 19,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "CPU et RAM — Exercices (2/3 : DDR, formats, dual-channel, VRAM)",
        "type": BlockType.MARKDOWN,
        "content": _MC03_EXERCICES_2,
        "position": 20,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "CPU et RAM — Exercices (3/3 : diagnostic, unités, goulot d'étranglement)",
        "type": BlockType.MARKDOWN,
        "content": _MC03_EXERCICES_3,
        "position": 21,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "CPU et RAM — Génère ton propre exercice (IA)",
        "type": BlockType.AI_EXERCISE,
        "content": AIExerciseBlockConfig(
            context_key="ampcr-mc03",
            intro=(
                "En complément des exercices ci-dessus : choisis une difficulté, génère un "
                "nouvel exercice sur le CPU ou la RAM, réponds, puis demande une "
                "correction personnalisée. L'exercice reste strictement dans la matière de "
                "ce mini-cours."
            ),
        ).to_json(),
        "position": 22,
        "is_published": True,
        "space": BlockSpace.PRACTICE,
    },
    {
        "title": "Fiche mémo — CPU et mémoire RAM",
        "type": BlockType.MARKDOWN,
        "content": _MC03_MEMO,
        "position": 23,
        "is_published": True,
        "space": BlockSpace.COURSE,
    },
    {
        "title": "Examen final — CPU et mémoire RAM (10 questions, 20 points)",
        "type": BlockType.MARKDOWN,
        "content": _MC03_EXAMEN,
        "position": 24,
        "is_published": True,
        "space": BlockSpace.EXAM,
    },
    {
        "title": "Examen final — Corrigé (réservé formateur, non publié)",
        "type": BlockType.MARKDOWN,
        "content": _MC03_EXAMEN_CORRIGE,
        "position": 25,
        "is_published": False,
        "space": BlockSpace.EXAM,
    },
]


def _ensure_subject(db, name: str, created: dict, kept: dict) -> Subject:
    """Crée une matière si elle n'existe pas encore, sans jamais la modifier sinon.

    Générique : réutilisé pour chaque matière (Mathématiques, Informatique, futures
    matières), pas seulement pour le contenu Mathématiques historique.
    """
    subject = db.query(Subject).filter_by(name=name).first()
    if subject is None:
        subject = Subject(name=name, slug=slugify(name))
        db.add(subject)
        db.flush()
        created["subjects"] += 1
    else:
        kept["subjects"] += 1
    return subject


def _ensure_modules(db, subject: Subject, codes: list[str], created: dict, kept: dict) -> None:
    """Crée les modules manquants d'une matière, sans jamais modifier ceux déjà présents."""
    existing_codes = {module.code for module in subject.modules}
    for code in codes:
        if code not in existing_codes:
            db.add(Module(code=code, slug=slugify(code), subject=subject))
            created["modules"] += 1
        else:
            kept["modules"] += 1
    db.flush()


def _seed_uaa(
    db,
    module: Module,
    code: str,
    title: str,
    position: int,
    blocks: list[dict],
    created: dict,
    kept: dict,
    obsolete_titles: frozenset[str] = frozenset(),
    reclassified: dict | None = None,
    reposition_titles: frozenset[str] = frozenset(),
    repositioned: dict | None = None,
) -> int:
    """Crée (ou complète) une UAA et ses blocs, sans jamais écraser l'existant.

    Retourne le nombre de blocs obsolètes retirés (voir `OBSOLETE_DEMO_BLOCK_TITLES`).

    `reclassified` (optionnel, ticket #22) : si fourni, incrémente `reclassified["blocks"]`
    et met à jour EN PLACE le champ `LessonBlock.space` de tout bloc déjà existant (matché
    par titre) dont la valeur explicite dans `blocks` (`block_data.get("space")`) diffère
    de celle actuellement en base. Seule la métadonnée `space` est touchée — jamais
    `content`, `title`, `position` ni `is_published` d'un bloc déjà existant. Nécessaire
    pour qu'un staging déjà seedé AVANT l'introduction de `LessonBlock.space` (colonne
    ajoutée avec la valeur par défaut COURSE, voir `app.database.ensure_schema_migrations`)
    reclasse correctement ses exercices/examens déjà existants vers PRACTICE/EXAM au
    prochain `seed-db`, sans `reset-db` ni duplication de contenu.

    `reposition_titles`/`repositioned` (optionnels, ticket #37) : contrairement à
    `reclassified`, ce mécanisme n'est PAS appliqué à tous les blocs — `position` est
    modifiable depuis l'admin (voir `app/admin.py`), donc l'écraser silencieusement pour
    un bloc quelconque romprait la garantie « un contenu édité depuis l'admin n'est
    jamais écrasé par un second seed ». Seuls les titres explicitement listés dans
    `reposition_titles` voient leur `position` resynchronisée sur la valeur déclarée dans
    `blocks` si elle diverge (voir `MC01_PRACTICE_REPOSITION_TITLES`) ; tout autre bloc
    garde sa position actuelle, quelle que soit sa valeur.
    """
    uaa = next((u for u in module.uaas if u.code == code), None)
    if uaa is None:
        uaa = UAA(
            code=code,
            title=title,
            slug=slugify(f"{module.code}-{code}"),
            position=position,
            is_published=True,
            module=module,
        )
        db.add(uaa)
        db.flush()
        created["uaas"] += 1
    else:
        kept["uaas"] += 1

    removed_obsolete = 0
    for block in list(uaa.lesson_blocks):
        if block.title in obsolete_titles:
            db.delete(block)
            removed_obsolete += 1
    db.flush()

    existing_by_title = {block.title: block for block in uaa.lesson_blocks}
    for block_data in blocks:
        existing_block = existing_by_title.get(block_data["title"])
        if existing_block is None:
            db.add(LessonBlock(uaa=uaa, **block_data))
            created["blocks"] += 1
            continue

        kept["blocks"] += 1
        if reclassified is not None:
            target_space = block_data.get("space", BlockSpace.COURSE)
            if existing_block.space != target_space:
                existing_block.space = target_space
                reclassified["blocks"] += 1
        if repositioned is not None and block_data["title"] in reposition_titles:
            target_position = block_data["position"]
            if existing_block.position != target_position:
                existing_block.position = target_position
                repositioned["blocks"] += 1

    return removed_obsolete


def seed() -> None:
    """Charge les données de développement/démonstration.

    Idempotent et strictement additif : une matière/module/UAA/bloc déjà présent (identifié
    par son code, ou son titre pour les blocs) n'est jamais modifié ni supprimé — en
    particulier, un contenu édité depuis l'admin après le premier seed n'est jamais écrasé
    par un second appel. Seule exception, ponctuelle et documentée : les anciens blocs de
    démonstration listés dans `OBSOLETE_DEMO_BLOCK_TITLES` sont retirés une fois pour toutes
    (migration de contenu obsolète, pas un comportement général).

    N'effectue jamais de suppression de matière/module/UAA existants. Pour repartir d'une
    base vide, utiliser `reset()` (commande `reset-db`) explicitement.
    """
    created = {"subjects": 0, "modules": 0, "uaas": 0, "blocks": 0}
    kept = {"subjects": 0, "modules": 0, "uaas": 0, "blocks": 0}
    reclassified = {"blocks": 0}
    repositioned = {"blocks": 0}
    removed_obsolete = 0

    Base.metadata.create_all(engine)
    ensure_schema_migrations()
    db = SessionLocal()
    try:
        mathematiques = _ensure_subject(db, SUBJECT_NAME, created, kept)
        _ensure_modules(db, mathematiques, MODULE_CODES, created, kept)

        mb32 = next(module for module in mathematiques.modules if module.code == "MB32")
        removed_obsolete += _seed_uaa(
            db, mb32, UAA1_CODE, UAA1_TITLE, 1, UAA1_BLOCKS, created, kept,
            obsolete_titles=OBSOLETE_DEMO_BLOCK_TITLES, reclassified=reclassified,
        )
        _seed_uaa(
            db, mb32, UAA2_CODE, UAA2_TITLE, 2, UAA2_BLOCKS, created, kept,
            reclassified=reclassified,
        )

        # Informatique AMPCR (ticket #10) : même mécanisme générique, purement additif —
        # ne touche jamais Mathématiques/MB32/MQ32/MQ34.
        informatique = _ensure_subject(db, INFORMATIQUE_SUBJECT_NAME, created, kept)
        _ensure_modules(db, informatique, INFORMATIQUE_MODULE_CODES, created, kept)

        ampcr = next(module for module in informatique.modules if module.code == "AMPCR")
        # Ticket #21 : `obsolete_titles=MC01_OBSOLETE_TITLES` retire, par leur ANCIEN titre,
        # les deux blocs Markdown qui contenaient encore le texte des exercices 1/2/9/11
        # avant leur migration vers des blocs `editorial_exercise` — indispensable pour
        # qu'un staging déjà seedé se mette réellement à jour (voir le commentaire sur
        # `MC01_OBSOLETE_TITLES` en tête de fichier). Les blocs de remplacement portent des
        # titres différents (voir MC01_BLOCKS), donc ce retrait ne s'exécute qu'une seule
        # fois : sans effet sur une base déjà migrée ou jamais seedée.
        # Ticket #22 : `reclassified=reclassified` reclasse EN PLACE (métadonnée `space`
        # uniquement) les blocs déjà existants dont l'espace pédagogique (COURSE/PRACTICE/
        # EXAM) diffère de la valeur explicite désormais définie dans MC01_BLOCKS/MC02_
        # BLOCKS/MC03_BLOCKS — indispensable pour qu'un staging déjà seedé avant ce ticket
        # (où `space` vaut COURSE partout par défaut) affiche correctement ses exercices en
        # PRACTICE et son examen en EXAM, sans reset-db. Voir le rapport de ticket, section
        # « Migration du contenu déjà seedé (staging) ».
        # Ticket #37 : `reposition_titles=MC01_PRACTICE_REPOSITION_TITLES` resynchronise en
        # place la `position` des 6 blocs MC01 créés avant #29 (jamais mise à jour par ce
        # mécanisme pour aucun autre bloc), corrigeant l'ordre d'affichage des 12 exercices
        # sur un staging déjà seedé, sans reset-db. Voir
        # `docs/claude-reports/2026-09-17_ticket-37_mc01-practice-order.md`.
        removed_obsolete += _seed_uaa(
            db, ampcr, MC01_CODE, MC01_TITLE, 1, MC01_BLOCKS, created, kept,
            obsolete_titles=MC01_OBSOLETE_TITLES, reclassified=reclassified,
            reposition_titles=MC01_PRACTICE_REPOSITION_TITLES, repositioned=repositioned,
        )
        # Mini-cours 02 (ticket #12) : même mécanisme, purement additif — ne touche jamais
        # MC01 ni Mathématiques.
        _seed_uaa(
            db, ampcr, MC02_CODE, MC02_TITLE, 2, MC02_BLOCKS, created, kept,
            reclassified=reclassified,
        )
        # Mini-cours 03 (ticket #14) : même mécanisme, purement additif — ne touche jamais
        # MC01/MC02 ni Mathématiques.
        _seed_uaa(
            db, ampcr, MC03_CODE, MC03_TITLE, 3, MC03_BLOCKS, created, kept,
            reclassified=reclassified,
        )

        db.commit()

        all_subjects = f"{SUBJECT_NAME} ({', '.join(MODULE_CODES)}), " \
            f"{INFORMATIQUE_SUBJECT_NAME} ({', '.join(INFORMATIQUE_MODULE_CODES)})"
        print(f"Seed terminé : {all_subjects}")
        print(
            f"  Créé   : {created['subjects']} matière(s), {created['modules']} module(s), "
            f"{created['uaas']} UAA, {created['blocks']} bloc(s)"
        )
        print(
            f"  Conservé (déjà présent, non modifié) : {kept['subjects']} matière(s), "
            f"{kept['modules']} module(s), {kept['uaas']} UAA, {kept['blocks']} bloc(s)"
        )
        if removed_obsolete:
            print(f"  Retiré : {removed_obsolete} bloc(s) de démonstration obsolète(s)")
        if reclassified["blocks"]:
            print(
                f"  Reclassé (espace pédagogique COURSE/PRACTICE/EXAM mis à jour, "
                f"contenu inchangé) : {reclassified['blocks']} bloc(s)"
            )
        if repositioned["blocks"]:
            print(
                f"  Repositionné (ordre d'affichage MC01 corrigé, contenu inchangé) : "
                f"{repositioned['blocks']} bloc(s)"
            )
    finally:
        db.close()


def reset() -> None:
    """Supprime la base SQLite locale puis relance `seed()`.

    Action explicite et destructive, jamais appelée automatiquement par `seed()` ni au
    démarrage de l'application. Réservée au développement local (commande `reset-db`).
    """
    db_path = Path(DATABASE_URL.removeprefix("sqlite:///"))
    if db_path.exists() and db_path != Path(":memory:"):
        db_path.unlink()
        print(f"Base supprimée : {db_path}")
    seed()


if __name__ == "__main__":
    seed()
