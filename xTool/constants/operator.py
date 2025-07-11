from enum import Enum


class OP(Enum):
    """
    NOTE: don't want to use Enum
    """

    AND = "AND"
    OR = "OR"

    EQ = "eq"
    NOT_EQ = "not_eq"

    IN = "in"
    NOT_IN = "not_in"

    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"

    STARTS_WITH = "starts_with"
    NOT_STARTS_WITH = "not_starts_with"

    ENDS_WITH = "ends_with"
    NOT_ENDS_WITH = "not_ends_with"

    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"

    ANY = "any"

    ALLOWED_OPERATORS = {
        "string": [
            EQ,
            NOT_EQ,
            IN,
            NOT_IN,
            CONTAINS,
            NOT_CONTAINS,
            STARTS_WITH,
            NOT_STARTS_WITH,
            ENDS_WITH,
            NOT_ENDS_WITH,
            ANY,
        ],
        "numberic": [EQ, NOT_EQ, IN, NOT_IN, LT, LTE, GT, GTE],
        "boolean": [EQ, NOT_EQ, IN, NOT_IN],
    }
