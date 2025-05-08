from xTool.utils import parse_user_to_list


def test_parse_user_to_list():
    actual = parse_user_to_list(" username1, username2(中文名) ")
    expect = ['username1', 'username2']
    assert actual == expect
