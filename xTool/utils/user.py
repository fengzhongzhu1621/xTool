from typing import List


def parse_user_to_list(value: str | List[str], sep=",") -> List:
    if not value:
        return []
    if isinstance(value, List):
        usernames = [username.strip().split("(")[0] for username in value if username and username.strip()]
    else:
        usernames = [
            username.strip().split("(")[0]
            for username in value.strip().strip(sep).split(sep)
            if username and username.strip()
        ]

    return usernames


def sort_username_list(usernames: List, sep=",") -> List:
    result = sorted({username.strip().strip(sep) for username in usernames if username and username.strip().strip(sep)})

    return result
