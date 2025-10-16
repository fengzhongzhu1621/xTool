from apps.global_conf.resources import GenerateQueryTokenResource, GetQueryDataResource


def test_query_token():
    query_data = {"a": 1, "b": 2}
    query_token = "3b2284a1db2ed76b2ae15889b0be2a1f"
    params = {
        "key": "key_1",
        "query_data": query_data,
    }
    actual = GenerateQueryTokenResource()(params)
    expect = {"query_token": query_token}
    assert actual == expect

    actual = GetQueryDataResource()({"query_token": query_token})
    expect = {"query_data": query_data}
    assert actual == expect
