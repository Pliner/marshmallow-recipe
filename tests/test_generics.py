import dataclasses
import types
from contextlib import nullcontext as does_not_raise
from typing import Annotated, Any, ContextManager, Generic, Iterable, List, TypeVar, Union
from unittest.mock import ANY

import pytest

from marshmallow_recipe.generics import (
    build_subscripted_type,
    extract_type,
    get_class_type_var_map,
    get_fields_class_map,
    get_fields_type_map,
)

T = TypeVar("T")


@dataclasses.dataclass()
class OtherType:
    pass


@dataclasses.dataclass()
class NonGeneric:
    pass


@dataclasses.dataclass()
class RegularGeneric(Generic[T]):
    pass


@dataclasses.dataclass(frozen=True)
class FrozenGeneric(Generic[T]):
    pass


def e(match: str) -> ContextManager:
    return pytest.raises(ValueError, match=match)


@pytest.mark.parametrize(
    "data, cls, expected, context",
    [
        (1, None, int, does_not_raise()),
        (1, int, int, does_not_raise()),
        (1, OtherType, ANY, e("OtherType'> is invalid but can be removed, actual type is <class 'int'>")),
        (NonGeneric(), None, NonGeneric, does_not_raise()),
        (NonGeneric(), NonGeneric, NonGeneric, does_not_raise()),
        (NonGeneric(), OtherType, ANY, e("OtherType'> is invalid but can be removed, actual type is <class 'tests")),
        (RegularGeneric(), None, ANY, e("Explicit cls required for unsubscripted type <class 'tests")),
        (RegularGeneric(), RegularGeneric, ANY, e("RegularGeneric'> is not subscripted version of <class 'tests")),
        (RegularGeneric(), RegularGeneric[int], RegularGeneric[int], does_not_raise()),
        (RegularGeneric[int](), None, RegularGeneric[int], does_not_raise()),
        (RegularGeneric[int](), RegularGeneric[int], RegularGeneric[int], does_not_raise()),
        (RegularGeneric[int](), RegularGeneric[str], ANY, e("str] is invalid but can be removed, actual type is")),
        (RegularGeneric[int](), RegularGeneric, ANY, e("RegularGeneric'> is invalid but can be removed, actual type")),
        (RegularGeneric[RegularGeneric[int]](), RegularGeneric[RegularGeneric[str]], ANY, e("str]] is invalid but")),
        (RegularGeneric[int](), OtherType, ANY, e("OtherType'> is invalid but can be removed, actual type is tests")),
        (FrozenGeneric[int](), None, ANY, e("Explicit cls required for unsubscripted type <class")),
        (FrozenGeneric[int](), FrozenGeneric[str], FrozenGeneric[str], does_not_raise()),
        (FrozenGeneric(), FrozenGeneric[int], FrozenGeneric[int], does_not_raise()),
        (FrozenGeneric(), FrozenGeneric[list], FrozenGeneric[list], does_not_raise()),
        (FrozenGeneric(), FrozenGeneric[dict], FrozenGeneric[dict], does_not_raise()),
        (FrozenGeneric(), FrozenGeneric[FrozenGeneric[str]], FrozenGeneric[FrozenGeneric[str]], does_not_raise()),
        (FrozenGeneric(), FrozenGeneric, ANY, e("FrozenGeneric'> is not subscripted version of <class 'tests")),
        (FrozenGeneric(), FrozenGeneric[FrozenGeneric], ANY, e("FrozenGeneric] is not subscripted version of")),
        (FrozenGeneric(), OtherType, ANY, e("OtherType'> is not subscripted version of <class 'tests")),
    ],
)
def test_extract_type(data: Any, cls: type, expected: type, context: ContextManager) -> None:
    with context:
        actual = extract_type(data, cls)
        assert actual == expected


def test_get_fields_type_map_with_field_override() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Value1:
        v1: str

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Value2(Value1):
        v2: str

    _TValue = TypeVar("_TValue", bound=Value1)
    _TItem = TypeVar("_TItem")

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class T1(Generic[_TItem]):
        value: Value1
        iterable: Iterable[_TItem]

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class T2(Generic[_TValue, _TItem], T1[_TItem]):
        value: _TValue
        iterable: set[_TItem]

    actual = get_fields_type_map(T2[Value2, int])
    assert actual == {
        "value": Value2,
        "iterable": set[int],
    }


def test_get_fields_type_map_non_generic() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Value1:
        v1: int

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Value2(Value1):
        v2: bool

    actual = get_fields_type_map(Value2)
    assert actual == {
        "v1": int,
        "v2": bool,
    }


def test_get_fields_type_map_generic_inheritance() -> None:
    _T = TypeVar("_T")

    @dataclasses.dataclass()
    class NonGeneric:
        v: bool

    @dataclasses.dataclass()
    class Value1(Generic[_T]):
        v1: _T

    @dataclasses.dataclass()
    class Value2(Value1[int], NonGeneric):
        v2: float

    actual = get_fields_type_map(Value2)
    assert actual == {
        "v": bool,
        "v1": int,
        "v2": float,
    }


def test_get_fields_type_map_non_dataclass() -> None:
    with pytest.raises(ValueError) as e:
        get_fields_type_map(list[int])
    assert e.value.args[0] == "<class 'list'> is not a dataclass"


def test_get_fields_type_map_not_subscripted() -> None:
    _T = TypeVar("_T")

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Xxx(Generic[_T]):
        xxx: _T

    with pytest.raises(Exception) as e:
        get_fields_type_map(Xxx)

    assert e.value.args[0] == (
        "Expected subscripted generic, but got unsubscripted "
        "<class 'tests.test_generics.test_get_fields_type_map_not_subscripted.<locals>.Xxx'>"
    )


def test_get_fields_type_map_for_subscripted() -> None:
    _T = TypeVar("_T")

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Xxx(Generic[_T]):
        xxx: _T

    actual = get_fields_type_map(Xxx[str])
    assert actual == {"xxx": str}


def test_get_fields_class_map() -> None:
    _T = TypeVar("_T")

    @dataclasses.dataclass()
    class Base1(Generic[_T]):
        a: str
        b: str
        c: str

    @dataclasses.dataclass()
    class Base2(Base1[int]):
        a: str
        b: str
        d: str
        e: str

    @dataclasses.dataclass()
    class BaseG:
        f: str
        g: str

    @dataclasses.dataclass()
    class Base3(Base2, BaseG):
        a: str
        d: str
        f: str
        h: str

    actual = get_fields_class_map(Base3)
    assert actual == {
        "a": Base3,
        "b": Base2,
        "c": Base1,
        "d": Base3,
        "e": Base2,
        "f": Base3,
        "g": BaseG,
        "h": Base3,
    }


def test_get_class_type_var_map_with_inheritance() -> None:
    _T1 = TypeVar("_T1")
    _T2 = TypeVar("_T2")
    _T3 = TypeVar("_T3")

    @dataclasses.dataclass()
    class NonGeneric:
        pass

    @dataclasses.dataclass()
    class Aaa(Generic[_T1, _T2]):
        pass

    @dataclasses.dataclass()
    class Bbb(Generic[_T1], Aaa[int, _T1]):
        pass

    @dataclasses.dataclass()
    class Ccc(Generic[_T3]):
        pass

    @dataclasses.dataclass()
    class Ddd(Generic[_T1, _T2, _T3], Bbb[_T2], Ccc[_T1], NonGeneric):
        pass

    actual = get_class_type_var_map(Ddd[bool, str, float])
    assert actual == {
        Aaa: {
            _T1: int,
            _T2: str,
        },
        Bbb: {
            _T1: str,
        },
        Ccc: {
            _T3: bool,
        },
        Ddd: {
            _T1: bool,
            _T2: str,
            _T3: float,
        },
    }


def test_get_class_type_var_map_with_incompatible_inheritance() -> None:
    _T = TypeVar("_T")

    @dataclasses.dataclass()
    class Aaa(Generic[_T]):
        pass

    @dataclasses.dataclass()
    class Bbb(Aaa[int]):
        pass

    @dataclasses.dataclass()
    class Ccc(Bbb, Aaa[str]):  # type: ignore
        pass

    with pytest.raises(ValueError, match="Incompatible Base class") as e:
        get_class_type_var_map(Ccc)
    assert "<locals>.Aaa'> with generic args {~_T: <class 'int'>} and {~_T: <class 'str'>}" in e.value.args[0]


def test_get_class_type_var_map_with_duplicated_generic_inheritance() -> None:
    _T = TypeVar("_T")

    @dataclasses.dataclass()
    class NonGeneric:
        pass

    @dataclasses.dataclass()
    class Aaa(Generic[_T]):
        pass

    @dataclasses.dataclass()
    class Bbb(Aaa[int], NonGeneric):
        pass

    @dataclasses.dataclass()
    class Ccc(Bbb, Aaa[int], NonGeneric):
        pass

    actual = get_class_type_var_map(Ccc)
    assert actual == {
        Aaa: {
            _T: int,
        },
    }


def test_get_class_type_var_map_with_nesting() -> None:
    _T1 = TypeVar("_T1")
    _T2 = TypeVar("_T2")
    _T3 = TypeVar("_T3")

    @dataclasses.dataclass()
    class Aaa(Generic[_T1, _T2]):
        pass

    @dataclasses.dataclass()
    class Bbb(Generic[_T1]):
        pass

    @dataclasses.dataclass()
    class Ccc(Generic[_T1, _T2, _T3], Aaa[Bbb[list[Annotated[Bbb[_T2], "xxx"]]], _T1 | None]):
        pass

    actual = get_class_type_var_map(Ccc[bool, str, float])
    assert actual == {
        Aaa: {
            _T1: Bbb[list[Annotated[Bbb[str], "xxx"]]],
            _T2: bool | None,
        },
        Ccc: {
            _T1: bool,
            _T2: str,
            _T3: float,
        },
    }


_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


class Xxx(Generic[_T1, _T2]):
    pass


class Zzz(Generic[_T1]):
    pass


_TInt = TypeVar("_TInt")
_TIntNone = TypeVar("_TIntNone")
_TStr = TypeVar("_TStr")
_TList = TypeVar("_TList")
_TDictIntTStr = TypeVar("_TDictIntTStr")

GENERIC_MAP: dict[TypeVar, type[Any] | types.UnionType] = {
    _TInt: int,
    _TIntNone: int | None,
    _TStr: str,
    _TList: list,
    _TDictIntTStr: dict[int, _TStr],  # type: ignore
}


@pytest.mark.parametrize(
    "t, expected",
    [
        (_TIntNone, int | None),
        (list[_TInt], list[int]),  # type: ignore
        (list[_TIntNone], list[int | None]),  # type: ignore
        (List[_TStr], List[str]),  # type: ignore
        (dict[_TStr, _TInt], dict[str, int]),  # type: ignore
        (dict[_TStr, list[_TInt]], dict[str, list[int]]),  # type: ignore
        (_TInt | None, int | None),
        (bool | None, bool | None),
        (Union[_TInt, float, bool, _TStr], int | float | bool | str),  # type: ignore
        (_TInt | float | bool | _TStr, int | float | bool | str),
        (list[_TInt | None], list[int | None]),  # type: ignore
        (list[_TList], list[list[Any]]),  # type: ignore
        (dict[_TInt, _TDictIntTStr], dict[int, dict[int, str]]),  # type: ignore
        (Annotated[_TStr, "qwe", 123, None], Annotated[str, "qwe", 123, None]),  # type: ignore
        (Annotated[list[_TStr], "qwe", 123, None], Annotated[list[str], "qwe", 123, None]),  # type: ignore
        (list[Annotated[list[_TInt], "asd", "zxc"]], list[Annotated[list[int], "asd", "zxc"]]),  # type: ignore
        (Xxx[list[_TInt], Zzz[_TStr]], Xxx[list[int], Zzz[str]]),  # type: ignore
    ],
)
def test_build_subscripted_type(t: type, expected: type) -> None:
    actual = build_subscripted_type(t, GENERIC_MAP)
    assert actual == expected
