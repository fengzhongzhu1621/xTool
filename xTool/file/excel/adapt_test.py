from xTool.file.excel import from_dict, to_list, to_matrix

data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

headers = [{"id": "id", "name": "ID"}, {"id": "name", "name": "Name"}]

header_style = {"id": "FFFF00", "name": "00FF00"}  # 黄色  # 绿色


def test_from_dict():
    wb = from_dict(data, headers=headers, header_style=header_style, match_header=True)
    wb.save("output.xlsx")

    with open("output.xlsx", "rb") as fb:
        actual = to_list(fb)
        expect = [
            {'ID': '1', 'Name': 'Alice'},
            {'ID': '2', 'Name': 'Bob'},
        ]
        assert actual == expect

    with open("output.xlsx", "rb") as fb:
        actual = to_matrix(fb)
        expect = {
            0: {
                'Name': {
                    '1': 'Alice',
                    '2': 'Bob',
                }
            },
        }
        assert actual == expect
