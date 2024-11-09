import marshmallow_recipe as mr
import dataclasses


def test_order():
    @dataclasses.dataclass
    class A:
        a: int
        b: int

    assert [name for name in mr.dump(A(a=1, b=2))] == ["a", "b"]
