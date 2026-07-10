from app.database import Base, SessionLocal, engine
from app.exercise_blocks import ExerciseBlockConfig
from app.models import UAA, BlockType, LessonBlock, Module, Subject
from app.quiz import QuizConfig
from app.slugify import slugify

SUBJECT_NAME = "Mathématiques"
MODULE_CODES = ["MB32", "MQ32", "MQ34"]

UAA1_CODE = "UAA1"
UAA1_TITLE = "Tableaux, graphiques, formules"

# Anciens blocs de démonstration (utilisés pour tester markdown/youtube/quiz/exercices
# générés lors des premières étapes du projet) : remplacés par la vraie structure de
# contenu de l'UAA1 ci-dessous. Supprimés par leur titre lors du seed pour ne pas laisser
# de contenu obsolète mélangé aux nouvelles sections.
OBSOLETE_DEMO_BLOCK_TITLES = {
    "Introduction",
    "Vidéo d'introduction",
    "Brouillon",
    "Entraîne-toi",
    "Quiz de compréhension",
}

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
            "2. Fonction constante et fonction du premier degré\n"
            "3. Construire un tableau et un graphique\n"
            "4. Intersection de deux fonctions\n"
            "5. Puissances et notation scientifique\n"
            "6. Proportionnalité inverse et croissance exponentielle\n"
            "7. Intérêts simples et composés\n"
            "8. Choisir le bon outil\n\n"
            "*Cette page est en cours de construction : les sections ci-dessous seront "
            "complétées progressivement (théorie, exemples, exercices, quiz, fiche mémo).*\n"
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
        "title": "2. Fonction constante et fonction du premier degré",
        "type": BlockType.MARKDOWN,
        "content": (
            "## Notions couvertes\n\n"
            "- Fonction constante f(x) = p\n"
            "- Fonction du premier degré f(x) = mx + p, avec m différent de 0\n"
            "- Pente et ordonnée à l'origine\n\n"
            "## À compléter\n\n"
            "- [ ] Théorie\n"
            "- [ ] Exemples\n"
            "- [ ] Exercices\n"
            "- [ ] Quiz\n"
        ),
        "position": 3,
        "is_published": False,
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
        "position": 4,
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
        "position": 5,
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
        "position": 6,
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
        "position": 7,
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
        "position": 8,
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
        "position": 9,
        "is_published": False,
    },
    {
        "title": "Exemple d'exercice généré — Fonction du premier degré",
        "type": BlockType.GENERATED_EXERCISE,
        "content": ExerciseBlockConfig(
            generator="maths.equations.linear_equation",
            difficulty=1,
            count=1,
            tags=["fonctions", "premier degré"],
        ).to_json(),
        "position": 10,
        "is_published": False,
    },
    {
        "title": "Exemple de quiz — Lecture de graphique",
        "type": BlockType.QUIZ,
        "content": QuizConfig(
            question=(
                "Un graphique passe par les points (0, 3) et (2, 7). "
                "Quelle est la pente de la droite ?"
            ),
            choices=["1", "2", "3", "4"],
            correct_index=1,
            explanation=(
                "La pente se calcule par (y2 - y1) / (x2 - x1) = (7 - 3) / (2 - 0) = 2."
            ),
        ).to_json(),
        "position": 11,
        "is_published": False,
    },
    {
        "title": "Fiche mémo — Tableaux, graphiques, formules",
        "type": BlockType.MARKDOWN,
        "content": (
            "*Fiche de synthèse à rédiger une fois les sections ci-dessus complétées : "
            "formules clés (pente, ordonnée à l'origine, intérêt simple/composé, notation "
            "scientifique), méthode de choix de l'outil (tableau / graphique / formule).*\n"
        ),
        "position": 12,
        "is_published": False,
    },
]


def seed() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        subject = db.query(Subject).filter_by(name=SUBJECT_NAME).first()
        if subject is None:
            subject = Subject(name=SUBJECT_NAME, slug=slugify(SUBJECT_NAME))
            db.add(subject)
            db.flush()

        existing_codes = {module.code for module in subject.modules}
        for code in MODULE_CODES:
            if code not in existing_codes:
                db.add(Module(code=code, slug=slugify(code), subject=subject))
        db.flush()

        mb32 = next(module for module in subject.modules if module.code == "MB32")
        uaa = next((u for u in mb32.uaas if u.code == UAA1_CODE), None)
        if uaa is None:
            uaa = UAA(
                code=UAA1_CODE,
                title=UAA1_TITLE,
                slug=slugify(f"{mb32.code}-{UAA1_CODE}"),
                module=mb32,
            )
            db.add(uaa)
            db.flush()
        elif uaa.title != UAA1_TITLE:
            uaa.title = UAA1_TITLE

        for block in list(uaa.lesson_blocks):
            if block.title in OBSOLETE_DEMO_BLOCK_TITLES:
                db.delete(block)
        db.flush()

        existing_titles = {block.title for block in uaa.lesson_blocks}
        for block_data in UAA1_BLOCKS:
            if block_data["title"] not in existing_titles:
                db.add(LessonBlock(uaa=uaa, **block_data))

        db.commit()
        print(f"Seed terminé : {SUBJECT_NAME} ({', '.join(MODULE_CODES)})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
