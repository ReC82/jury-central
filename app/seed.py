from app.database import Base, SessionLocal, engine
from app.exercise_blocks import ExerciseBlockConfig
from app.models import UAA, BlockType, LessonBlock, Module, Subject
from app.quiz import QuizConfig
from app.slugify import slugify

SUBJECT_NAME = "Mathématiques"
MODULE_CODES = ["MB32", "MQ32", "MQ34"]

SAMPLE_UAA_CODE = "UAA1"
SAMPLE_UAA_TITLE = "Fonctions du premier degré"
SAMPLE_BLOCKS = [
    {
        "title": "Introduction",
        "type": BlockType.MARKDOWN,
        "content": (
            "# Fonctions du premier degré\n\n"
            "Une fonction du premier degré s'écrit sous la forme "
            "$f(x) = ax + b$.\n\n"
            "- $a$ est le **coefficient angulaire**\n"
            "- $b$ est l'**ordonnée à l'origine**\n"
        ),
        "position": 1,
        "is_published": True,
    },
    {
        "title": "Vidéo d'introduction",
        "type": BlockType.YOUTUBE,
        "content": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "position": 2,
        "is_published": True,
    },
    {
        "title": "Brouillon",
        "type": BlockType.MARKDOWN,
        "content": "Contenu en cours de rédaction, non publié.",
        "position": 3,
        "is_published": False,
    },
    {
        "title": "Entraîne-toi",
        "type": BlockType.GENERATED_EXERCISE,
        "content": ExerciseBlockConfig(
            generator="maths.equations.linear_equation",
            difficulty=1,
            count=2,
            tags=["algèbre", "premier degré"],
        ).to_json(),
        "position": 4,
        "is_published": True,
    },
    {
        "title": "Quiz de compréhension",
        "type": BlockType.QUIZ,
        "content": QuizConfig(
            question="Dans f(x) = ax + b, comment appelle-t-on b ?",
            choices=[
                "Le coefficient angulaire",
                "L'ordonnée à l'origine",
                "La pente",
                "La variable",
            ],
            correct_index=1,
            explanation="b est la valeur de f(x) quand x = 0, on l'appelle l'ordonnée à l'origine.",
        ).to_json(),
        "position": 5,
        "is_published": True,
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
        uaa = next((u for u in mb32.uaas if u.code == SAMPLE_UAA_CODE), None)
        if uaa is None:
            uaa = UAA(
                code=SAMPLE_UAA_CODE,
                title=SAMPLE_UAA_TITLE,
                slug=slugify(f"{mb32.code}-{SAMPLE_UAA_CODE}"),
                module=mb32,
            )
            db.add(uaa)
            db.flush()

        existing_titles = {block.title for block in uaa.lesson_blocks}
        for block_data in SAMPLE_BLOCKS:
            if block_data["title"] not in existing_titles:
                db.add(LessonBlock(uaa=uaa, **block_data))

        db.commit()
        print(f"Seed terminé : {SUBJECT_NAME} ({', '.join(MODULE_CODES)})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
