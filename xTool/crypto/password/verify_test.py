from password_validation.password import Password


def test_password():
    password = Password("hello world")

    # quick check on object
    assert password
    assert isinstance(password, Password)

    # check attrs
    assert password.lowercase == 10
    assert password.whitespace == 1
    assert password.length == 11

    assert password.uppercase == 0
    assert password.other == 0
    assert password.symbols == 0

    assert isinstance(password.entropy, (int, float))
