from app.card_kind import classify_block_title


def test_classify_exam_by_mini_test_keyword():
    assert classify_block_title("Mini-test final — Géométrie") == "exam"


def test_classify_exam_by_examen_keyword():
    assert (
        classify_block_title("Examen final — Architecture générale d'un PC (10 questions, 20 points)")
        == "exam"
    )


def test_classify_exercise_keyword():
    assert classify_block_title("Architecture d'un PC — Exercices (1/3)") == "exercise"


def test_classify_example_keyword():
    assert classify_block_title("9. Interaction des composants — Exemple") == "example"


def test_classify_default_theory():
    assert classify_block_title("1. Vue globale d'un ordinateur — Cours") == "theory"


def test_classify_memo_keyword():
    assert classify_block_title("Fiche mémo — Architecture générale d'un PC") == "summary"
