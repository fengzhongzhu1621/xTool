from xTool.time_utils.convert import infer_time_unit, scale_time_units


def test_infer_time_unit():
    actual = infer_time_unit([])
    expected = "hours"
    assert expected == actual

    actual = infer_time_unit([120])
    expected = "seconds"
    assert expected == actual

    actual = infer_time_unit([60 * 60 * 2])
    expected = "minutes"
    assert expected == actual

    actual = infer_time_unit([24 * 60 * 60 * 2])
    expected = "hours"
    assert expected == actual

    actual = infer_time_unit([24 * 60 * 60 * 365])
    expected = "days"
    assert expected == actual


def test_scale_time_units():
    unit = "minutes"
    actual = scale_time_units([120, 123, 60 * 60 * 2], unit)
    expected = [2.0, 2.05, 120.0]
    assert expected == actual

    unit = "hours"
    actual = scale_time_units([360, 60 * 60, 60 * 60 * 2], unit)
    expected = [0.1, 1.0, 2.0]
    assert expected == actual

    unit = "days"
    actual = scale_time_units([60 * 60 * 24, 60 * 60 * 24 * 365], unit)
    expected = [1.0, 365.0]
    assert expected == actual
