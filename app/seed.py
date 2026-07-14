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
        "question": "Le tableau x : -1, 0, 1 → f(x) : 4, 4, 4 correspond à quelle fonction ?",
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
        uaa = next((u for u in mb32.uaas if u.code == UAA1_CODE), None)
        if uaa is None:
            uaa = UAA(
                code=UAA1_CODE,
                title=UAA1_TITLE,
                slug=slugify(f"{mb32.code}-{UAA1_CODE}"),
                position=1,
                is_published=True,
                module=mb32,
            )
            db.add(uaa)
            db.flush()
            created["uaas"] += 1
        else:
            kept["uaas"] += 1

        for block in list(uaa.lesson_blocks):
            if block.title in OBSOLETE_DEMO_BLOCK_TITLES:
                db.delete(block)
                removed_obsolete += 1
        db.flush()

        existing_titles = {block.title for block in uaa.lesson_blocks}
        for block_data in UAA1_BLOCKS:
            if block_data["title"] not in existing_titles:
                db.add(LessonBlock(uaa=uaa, **block_data))
                created["blocks"] += 1
            else:
                kept["blocks"] += 1

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
