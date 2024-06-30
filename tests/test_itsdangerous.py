from itsdangerous import (
    Signer,
    TimedSerializer,
    TimestampSigner,
    URLSafeSerializer,
    URLSafeTimedSerializer,
)


def test_signer():
    signer = Signer("key")

    data = "hello world"
    actual = signed_data = signer.sign(data)
    expect = b"hello world.6n2uw0Rxbhjllkt0oDp5mAuIfAM"
    assert actual == expect

    actual = signer.unsign(signed_data)
    expect = b"hello world"
    assert actual == expect


def test_timestamp_signer():
    timestamp_signer = TimestampSigner("key")

    data = "hello world"
    signed_data = timestamp_signer.sign(data)

    actual = timestamp_signer.unsign(signed_data)
    expect = b"hello world"
    assert actual == expect


def test_safe_url():
    serializer = URLSafeSerializer("key")
    actual = serialized_data = serializer.dumps({"a": 1, "b": 2})
    expect = "eyJhIjoxLCJiIjoyfQ.v9LuilO5VVufIHEun74y4552vfE"
    assert actual == expect

    actual = serializer.loads(serialized_data)
    expect = {"a": 1, "b": 2}
    assert actual == expect


def test_timestamp_safe_url():
    serializer = URLSafeTimedSerializer("key")
    serialized_data = serializer.dumps({"a": 1, "b": 2})

    actual = serializer.loads(serialized_data)
    expect = {"a": 1, "b": 2}
    assert actual == expect


def test_timestamp_serializer():
    serializer = TimedSerializer("key")
    serialized_data = serializer.dumps({"a": 1, "b": 2})

    actual = serializer.loads(serialized_data)
    expect = {"a": 1, "b": 2}
    assert actual == expect
