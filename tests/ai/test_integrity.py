from app.ai.integrity import sign_exercise, verify_exercise_signature


def test_sign_and_verify_roundtrip():
    signature = sign_exercise(1, "facile", "calcul", "Combien font 2 + 2 ?")
    assert verify_exercise_signature(1, "facile", "calcul", "Combien font 2 + 2 ?", signature)


def test_verify_rejects_tampered_statement():
    signature = sign_exercise(1, "facile", "calcul", "Combien font 2 + 2 ?")
    assert not verify_exercise_signature(
        1, "facile", "calcul", "Combien font 2 + 2000 ?", signature
    )


def test_verify_rejects_tampered_block_id():
    signature = sign_exercise(1, "facile", "calcul", "Combien font 2 + 2 ?")
    assert not verify_exercise_signature(2, "facile", "calcul", "Combien font 2 + 2 ?", signature)


def test_verify_rejects_wrong_signature():
    assert not verify_exercise_signature(1, "facile", "calcul", "Combien font 2 + 2 ?", "0" * 64)
