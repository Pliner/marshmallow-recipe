import dataclasses
from types import UnionType
from typing import Annotated, Any, Generic, Iterable, List, TypeVar, Union

import pytest

from marshmallow_recipe.generics import (
    build_subscripted_type,
    get_class_type_var_map,
    get_fields_class_map,
    get_fields_type_map,
)


def test_get_fields_type_map_overrides() -> None:
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


def test_get_fields_type_map_non_data_class() -> None:
    actual = get_fields_type_map(int | None)
    assert actual == {}


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


def test_get_class_type_var_map_inheritance() -> None:
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


def test_get_class_type_var_map_nesting() -> None:
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
    class Ccc(Generic[_T1, _T2, _T3], Aaa[Bbb[list[Annotated[_T2, "xxx"]]], _T1 | None]):
        pass

    actual = get_class_type_var_map(Ccc[bool, str, float])
    assert actual == {
        Aaa: {
            _T1: Bbb[list[Annotated[str, "xxx"]]],
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

GENERIC_MAP: dict[TypeVar, type[Any] | UnionType] = {
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
