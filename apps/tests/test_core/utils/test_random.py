from core.utils import generate_random_sequence


def test_generate_random_sequence():
    actual = generate_random_sequence("test", "A")
    assert len(actual) == 20

    actual = generate_random_sequence("test", "A", 18)
    assert len(actual) == 32
