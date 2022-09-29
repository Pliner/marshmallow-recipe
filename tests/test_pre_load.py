import dataclasses
from typing import Any
from unittest.mock import ANY

import marshmallow_recipe as mr
from marshmallow_recipe.hooks import add_pre_load, get_pre_loads


def test_get_pre_loads() -> None:
    @dataclasses.dataclass
    class MyClass:
        x: int

        @staticmethod
        @mr.pre_load
        def pre_load(data: dict[str, Any]) -> dict[str, Any]:
            data["test"] = "value"
            return data

        @classmethod
        @mr.pre_load
        def pre_load2(cls, data: dict[str, Any]) -> dict[str, Any]:
            assert cls is MyClass
            data["test"] = "value"
            return data

    add_pre_load(MyClass, lambda data: {**data, "test": "value"})

    a = get_pre_loads(MyClass)
    assert a == [MyClass.pre_load, MyClass.pre_load2, ANY]
    assert a[0]({}) == {"test": "value"}
    assert a[1]({}) == {"test": "value"}
    assert a[2]({}) == {"test": "value"}


def test_deserialize_with_pre_load() -> None:
    @dataclasses.dataclass
    class MyClass:
        x: str

        @staticmethod
        @mr.pre_load
        def pre_load1(data: dict[str, Any]) -> dict[str, Any]:
            data["x"] = data["x"] + "_pre_loaded1"
            return data

        @staticmethod
        @mr.pre_load
        def pre_load2(data: dict[str, Any]) -> dict[str, Any]:
            data["x"] = data["x"] + "_pre_loaded2"
            return data

    add_pre_load(MyClass, lambda data: {**data, "x": data["x"] + "_pre_loaded3"})

    assert mr.load(MyClass, {"x": "value"}) == MyClass(x="value_pre_loaded1_pre_loaded2_pre_loaded3")


def test_deserialize_with_pre_load_decorator() -> None:
    def strip_strings(cls: Any) -> Any:
        def pre_load(data: dict[str, Any]) -> dict[str, Any]:
            return {k: pre_load_value(v) for k, v in data.items()}

        def pre_load_value(value: Any) -> Any:
            if not isinstance(value, str):
                return value
            return value.strip()

        add_pre_load(cls, pre_load)
        return cls

    @dataclasses.dataclass
    @strip_strings
    class MyClass:
        x: str | None

    assert mr.load(MyClass, {"x": "  abc  "}) == MyClass(x="abc")
