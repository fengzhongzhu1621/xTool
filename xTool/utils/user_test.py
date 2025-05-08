from xTool.utils import parse_user_to_list, sort_username_list


def test_parse_user_to_list():
    actual = parse_user_to_list(" username1, username2(中文名) ")
    expect = ['username1', 'username2']
    assert actual == expect


def test_sort_username_list():
    actual = sort_username_list([" username1 ", "username2,"])
    expect = ['username1', 'username2']
    assert actual == expect
