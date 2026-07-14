from pathlib import Path

from app.database import DATABASE_URL, Base, SessionLocal, engine
from app.exercise_blocks import ExerciseBlockConfig
from app.models import UAA, BlockType, LessonBlock, Module, Subject
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
) -> int:
    """Crée (ou complète) une UAA et ses blocs, sans jamais écraser l'existant.

    Retourne le nombre de blocs obsolètes retirés (voir `OBSOLETE_DEMO_BLOCK_TITLES`).
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

    existing_titles = {block.title for block in uaa.lesson_blocks}
    for block_data in blocks:
        if block_data["title"] not in existing_titles:
            db.add(LessonBlock(uaa=uaa, **block_data))
            created["blocks"] += 1
        else:
            kept["blocks"] += 1

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
    removed_obsolete = 0

    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        subject = db.query(Subject).filter_by(name=SUBJECT_NAME).first()
        if subject is None:
            subject = Subject(name=SUBJECT_NAME, slug=slugify(SUBJECT_NAME))
            db.add(subject)
            db.flush()
            created["subjects"] += 1
        else:
            kept["subjects"] += 1

        existing_codes = {module.code for module in subject.modules}
        for code in MODULE_CODES:
            if code not in existing_codes:
                db.add(Module(code=code, slug=slugify(code), subject=subject))
                created["modules"] += 1
            else:
                kept["modules"] += 1
        db.flush()

        mb32 = next(module for module in subject.modules if module.code == "MB32")
        removed_obsolete += _seed_uaa(
            db, mb32, UAA1_CODE, UAA1_TITLE, 1, UAA1_BLOCKS, created, kept,
            obsolete_titles=OBSOLETE_DEMO_BLOCK_TITLES,
        )
        _seed_uaa(db, mb32, UAA2_CODE, UAA2_TITLE, 2, UAA2_BLOCKS, created, kept)

        db.commit()

        print(f"Seed terminé : {SUBJECT_NAME} ({', '.join(MODULE_CODES)})")
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
