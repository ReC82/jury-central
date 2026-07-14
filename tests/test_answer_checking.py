from fractions import Fraction

from app.answer_checking import answers_match, parse_answer


def test_parse_integer():
    assert parse_answer("5") == Fraction(5)


def test_parse_negative_integer():
    assert parse_answer("-3") == Fraction(-3)


def test_parse_decimal_with_dot():
    assert parse_answer("1.75") == Fraction(7, 4)


def test_parse_decimal_with_comma():
    assert parse_answer("1,75") == Fraction(7, 4)


def test_parse_fraction_format():
    assert parse_answer("3/4") == Fraction(3, 4)


def test_parse_fraction_with_spaces():
    assert parse_answer(" 3 / 4 ") == Fraction(3, 4)


def test_parse_empty_returns_none():
    assert parse_answer("") is None
    assert parse_answer("   ") is None
    assert parse_answer(None) is None


def test_parse_invalid_returns_none():
    assert parse_answer("abc") is None
    assert parse_answer("3/0") is None
    assert parse_answer("1/2/3") is None


def test_answers_match_exact():
    assert answers_match(Fraction(5), "5") is True
    assert answers_match(Fraction(7, 4), "1,75") is True
    assert answers_match(Fraction(-21, 4), "-21/4") is True


def test_answers_match_incorrect():
    assert answers_match(Fraction(5), "6") is False


def test_answers_match_invalid_input():
    assert answers_match(Fraction(5), "abc") is False
