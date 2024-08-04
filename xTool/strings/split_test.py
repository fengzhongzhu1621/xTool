import pytest

from xTool.strings.split import split_member_list


@pytest.mark.parametrize(
    "member_str,members",
    [
        [None, []],
        ["", []],
        ["     ", []],
        ["a", ["a"]],
        [" , a , b , ", ["a", "b"]],
    ],
)
def test_split_member_list(member_str, members):
    assert split_member_list(member_str) == members
