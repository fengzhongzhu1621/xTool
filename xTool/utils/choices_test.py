from xTool.utils.choices import IntegerChoices


class DemoIntegerChoices(IntegerChoices):
    a = 1, "name_a"
    b = 2, "name_b"


class TestIntegerChoices:
    def test__members__(self):
        actual = []
        for name, member in DemoIntegerChoices.__members__.items():
            actual.append([name, member.value, member.name])
        expect = [["a", 1, "a"], ["b", 2, "b"]]
        assert actual == expect

    def test_names(self):
        actual = DemoIntegerChoices.names
        expect = ["a", "b"]
        assert actual == expect

    def test_choices(self):
        actual = DemoIntegerChoices.choices
        expect = [(1, "name_a"), (2, "name_b")]
        assert actual == expect

    def test_labels(self):
        actual = DemoIntegerChoices.labels
        expect = ["name_a", "name_b"]
        assert actual == expect

    def test_values(self):
        actual = DemoIntegerChoices.values
        expect = [1, 2]
        assert actual == expect
