from app.database import Base, SessionLocal, engine
from app.models import Module, Subject

SUBJECT_NAME = "Mathématiques"
MODULE_CODES = ["MB32", "MQ32", "MQ34"]


def seed() -> None:
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        subject = db.query(Subject).filter_by(name=SUBJECT_NAME).first()
        if subject is None:
            subject = Subject(name=SUBJECT_NAME)
            db.add(subject)
            db.flush()

        existing_codes = {module.code for module in subject.modules}
        for code in MODULE_CODES:
            if code not in existing_codes:
                db.add(Module(code=code, subject=subject))

        db.commit()
        print(f"Seed terminé : {SUBJECT_NAME} ({', '.join(MODULE_CODES)})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
