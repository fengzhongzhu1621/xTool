import pytest

from xTool.collections.object import DictObject, ObjectSet


def test_dict_object_with_dict():
    data = {"id": "hello"}

    do = DictObject(data)

    assert do.is_dict

    assert do.id == "hello"
    assert do.notexists is None

    with pytest.raises(AttributeError):
        do.id = 123

    with pytest.raises(AttributeError):
        del do.id


def test_dict_object_with_class():
    class A(object):
        pass

    a = A()
    a.id = "hello"

    do = DictObject(a)

    assert not do.is_dict

    assert do.id == "hello"
    assert do.notexists is None

    with pytest.raises(AttributeError):
        do.id = 123

    with pytest.raises(AttributeError):
        del do.id


def test_object_set():
    host = DictObject(obj={"id": "192.168.1.1"})
    module = DictObject(obj={"id": "iam"})

    os = ObjectSet()
    os.add_object("host", host)
    os.add_object("module", module)

    assert os.has_object("host")
    assert os.has_object("module")
    assert not os.has_object("cluster")

    assert os.get("host.id") == "192.168.1.1"
    assert os.get("module.id") == "iam"

    assert os.get("invalidkey") is None

    assert os.get("cluster.id") is None
    assert os.get("host.path") is None

    # get/del
    obj = os.get_object("host")
    assert obj
    assert obj.id == "192.168.1.1"

    os.del_object("host")
    assert not os.has_object("host")
