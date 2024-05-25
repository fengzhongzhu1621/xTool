from config import celery_app as app


@app.task
def add(x, y, c=3):
    return x + y + c


def test_add():
    assert add(1, 2) == 6
    result = add.apply_async((1, 2))
    assert result.get() == 6

    result = add.apply_async(args=(1, 2), kwargs={"c": 4})
    assert result.get() == 7

    route_params = {"queue": "er_execute", "priority": 100, "routing_key": "er_execute"}
    result = add.apply_async(args=(1, 2), kwargs={"c": 4}, **route_params)
    assert result.get() == 7
