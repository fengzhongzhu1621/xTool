# pythran export dprod(int list, int list)
def dprod(l0, l1):
    """计算点积 ."""
    return sum(x * y for x, y in zip(l0, l1))
