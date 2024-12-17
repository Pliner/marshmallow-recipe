import dataclasses
import datetime
import decimal
import enum
import uuid
from contextlib import nullcontext as does_not_raise
from typing import (
    Annotated,
    Any,
    Callable,
    ContextManager,
    Dict,
    FrozenSet,
    Generic,
    Iterable,
    List,
    Set,
    Tuple,
    TypeVar,
    get_origin,
)

import pytest

import marshmallow_recipe as mr


class Parity(str, enum.Enum):
    ODD = "odd"
    EVEN = "even"


class Bit(int, enum.Enum):
    Zero = 0
    One = 1


def test_simple_types() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class SimpleTypesContainers:
        any_field: Any
        annotated_any_field: Annotated[Any, 0]
        str_field: str
        optional_str_field: str | None
        bool_field: bool
        optional_bool_field: bool | None
        decimal_field: decimal.Decimal
        optional_decimal_field: decimal.Decimal | None
        int_field: int
        optional_int_field: int | None
        float_field: float
        optional_float_field: float | None
        uuid_field: uuid.UUID
        optional_uuid_field: uuid.UUID | None
        datetime_field: datetime.datetime
        optional_datetime_field: datetime.datetime | None
        time_field: datetime.time
        optional_time_field: datetime.time | None
        date_field: datetime.date
        optional_date_field: datetime.date | None
        dict_field: dict[str, Any]
        optional_dict_field: dict[str, Any] | None
        custom_dict_field: dict[datetime.date, int]
        optional_custom_dict_field: dict[datetime.date, int] | None
        list_field: list[str]
        optional_list_field: list[str] | None
        set_field: set[str]
        optional_set_field: set[str] | None
        frozenset_field: frozenset[str]
        optional_frozenset_field: frozenset[str] | None
        tuple_field: tuple[str, ...]
        optional_tuple_field: tuple[str, ...] | None
        enum_str_field: Parity
        optional_enum_str_field: Parity | None
        enum_int_field: Bit
        optional_enum_int_field: Bit | None
        # with default
        str_field_with_default: str = "42"
        bool_field_with_default: bool = True
        decimal_field_with_default: decimal.Decimal = decimal.Decimal("42")
        int_field_with_default: int = 42
        float_field_with_default: float = 42.0
        uuid_field_with_default: uuid.UUID = uuid.UUID("15f75b02-1c34-46a2-92a5-18363aadea05")
        datetime_field_with_default: datetime.datetime = datetime.datetime(
            2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc
        )
        time_field_with_default: datetime.time = datetime.time(11, 33, 48)
        date_field_with_default: datetime.date = datetime.date(2022, 2, 20)
        enum_str_field_with_default: Parity = Parity.ODD
        enum_int_field_with_default: Bit = Bit.Zero
        # with default factory
        str_field_with_default_factory: str = dataclasses.field(default_factory=lambda: "42")
        bool_field_with_default_factory: bool = dataclasses.field(default_factory=lambda: True)
        decimal_field_with_default_factory: decimal.Decimal = dataclasses.field(
            default_factory=lambda: decimal.Decimal("42")
        )
        int_field_with_default_factory: float = dataclasses.field(default_factory=lambda: 42)
        float_field_with_default_factory: float = dataclasses.field(default_factory=lambda: 42.0)
        uuid_field_with_default_factory: uuid.UUID = dataclasses.field(
            default_factory=lambda: uuid.UUID("15f75b02-1c34-46a2-92a5-18363aadea05")
        )
        datetime_field_with_default_factory: datetime.datetime = dataclasses.field(
            default_factory=lambda: datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc)
        )
        time_field_with_default_factory: datetime.time = dataclasses.field(
            default_factory=lambda: datetime.time(11, 33, 48)
        )
        date_field_with_default_factory: datetime.date = dataclasses.field(
            default_factory=lambda: datetime.date(2022, 2, 20)
        )
        dict_field_with_default_factory: dict[str, Any] = dataclasses.field(default_factory=lambda: {})
        custom_dict_field_with_default_factory: dict[datetime.date, int] = dataclasses.field(default_factory=lambda: {})
        list_field_with_default_factory: list[str] = dataclasses.field(default_factory=lambda: [])
        set_field_with_default_factory: set[str] = dataclasses.field(default_factory=lambda: set())
        frozenset_field_with_default_factory: frozenset[str] = dataclasses.field(default_factory=lambda: frozenset())
        tuple_field_with_default_factory: tuple[str, ...] = dataclasses.field(default_factory=lambda: tuple())
        enum_str_field_with_default_factory: Parity = dataclasses.field(default_factory=lambda: Parity.ODD)
        enum_int_field_with_default_factory: Bit = dataclasses.field(default_factory=lambda: Bit.Zero)

    raw = dict(
        any_field={},
        annotated_any_field={},
        str_field="42",
        str_field_with_default="42",
        str_field_with_default_factory="42",
        optional_str_field="42",
        bool_field=True,
        bool_field_with_default=True,
        bool_field_with_default_factory=True,
        optional_bool_field=True,
        decimal_field="42.00",
        decimal_field_with_default="42.00",
        decimal_field_with_default_factory="42.00",
        optional_decimal_field="42.00",
        int_field=42,
        int_field_with_default=42,
        int_field_with_default_factory=42,
        optional_int_field=42,
        float_field=42.0,
        float_field_with_default=42.0,
        float_field_with_default_factory=42.0,
        optional_float_field=42.0,
        uuid_field="15f75b02-1c34-46a2-92a5-18363aadea05",
        uuid_field_with_default="15f75b02-1c34-46a2-92a5-18363aadea05",
        uuid_field_with_default_factory="15f75b02-1c34-46a2-92a5-18363aadea05",
        optional_uuid_field="15f75b02-1c34-46a2-92a5-18363aadea05",
        datetime_field="2022-02-20T11:33:48+00:00",
        datetime_field_with_default="2022-02-20T11:33:48.607289+00:00",
        datetime_field_with_default_factory="2022-02-20T11:33:48.607289+00:00",
        optional_datetime_field="2022-02-20T11:33:48.607289+00:00",
        time_field="11:33:48.607289",
        time_field_with_default="11:33:48",
        time_field_with_default_factory="11:33:48",
        optional_time_field="11:33:48",
        date_field="2022-02-20",
        date_field_with_default="2022-02-20",
        date_field_with_default_factory="2022-02-20",
        optional_date_field="2022-02-20",
        dict_field=dict(key="value"),
        dict_field_with_default_factory={},
        optional_dict_field=dict(key="value"),
        custom_dict_field={"2020-01-01": 42},
        custom_dict_field_with_default_factory={},
        optional_custom_dict_field={"2020-01-01": 42},
        list_field=["value"],
        list_field_with_default_factory=[],
        optional_list_field=["value"],
        set_field=["value"],
        set_field_with_default_factory=[],
        optional_set_field=["value"],
        tuple_field=["value"],
        tuple_field_with_default_factory=[],
        optional_tuple_field=["value"],
        frozenset_field=["value"],
        frozenset_field_with_default_factory=[],
        optional_frozenset_field=["value"],
        enum_str_field="odd",
        enum_str_field_with_default="odd",
        enum_str_field_with_default_factory="odd",
        optional_enum_str_field="even",
        enum_int_field=0,
        enum_int_field_with_default=0,
        enum_int_field_with_default_factory=0,
        optional_enum_int_field=1,
    )

    raw_no_defaults = {k: v for k, v in raw.items() if not k.endswith("default") and not k.endswith("default_factory")}

    loaded = mr.load(SimpleTypesContainers, raw)
    loaded_no_defaults = mr.load(SimpleTypesContainers, raw_no_defaults)
    dumped = mr.dump(loaded)

    assert (
        loaded_no_defaults
        == loaded
        == SimpleTypesContainers(
            any_field={},
            annotated_any_field={},
            str_field="42",
            optional_str_field="42",
            bool_field=True,
            optional_bool_field=True,
            decimal_field=decimal.Decimal("42.00"),
            optional_decimal_field=decimal.Decimal("42.00"),
            int_field=42,
            optional_int_field=42,
            float_field=42.0,
            optional_float_field=42.0,
            uuid_field=uuid.UUID("15f75b02-1c34-46a2-92a5-18363aadea05"),
            optional_uuid_field=uuid.UUID("15f75b02-1c34-46a2-92a5-18363aadea05"),
            datetime_field=datetime.datetime(2022, 2, 20, 11, 33, 48, 0, datetime.timezone.utc),
            optional_datetime_field=datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc),
            time_field=datetime.time(11, 33, 48, 607289),
            optional_time_field=datetime.time(11, 33, 48),
            date_field=datetime.date(2022, 2, 20),
            optional_date_field=datetime.date(2022, 2, 20),
            dict_field=dict(key="value"),
            optional_dict_field=dict(key="value"),
            custom_dict_field={datetime.date(2020, 1, 1): 42},
            optional_custom_dict_field={datetime.date(2020, 1, 1): 42},
            list_field=["value"],
            optional_list_field=["value"],
            set_field={"value"},
            optional_set_field={"value"},
            frozenset_field=frozenset({"value"}),
            optional_frozenset_field=frozenset({"value"}),
            tuple_field=("value",),
            optional_tuple_field=("value",),
            enum_str_field=Parity.ODD,
            optional_enum_str_field=Parity.EVEN,
            enum_int_field=Bit.Zero,
            optional_enum_int_field=Bit.One,
        )
    )

    assert dumped == raw
    assert mr.schema(SimpleTypesContainers) is mr.schema(SimpleTypesContainers)


def test_nested_dataclass() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class BoolContainer:
        bool_field: bool

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Container:
        bool_container_field: BoolContainer
        bool_container_field_with_default: BoolContainer = BoolContainer(bool_field=True)
        bool_container_field_with_default_factory: BoolContainer = dataclasses.field(
            default_factory=lambda: BoolContainer(bool_field=True)
        )

    raw = dict(
        bool_container_field=dict(bool_field=True),
        bool_container_field_with_default=dict(bool_field=True),
        bool_container_field_with_default_factory=dict(bool_field=True),
    )
    raw_no_defaults = {k: v for k, v in raw.items() if not k.endswith("default") or not k.endswith("default_factory")}

    loaded = mr.load(Container, raw)
    loaded_no_defaults = mr.load(Container, raw_no_defaults)
    dumped = mr.dump(loaded)

    assert loaded_no_defaults == loaded == Container(bool_container_field=BoolContainer(bool_field=True))
    assert dumped == raw

    assert mr.schema(Container) is mr.schema(Container)


def test_custom_name_bool() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class BoolContainer:
        bool_field: bool = dataclasses.field(metadata=mr.meta(name="BoolField"))

    raw = dict(BoolField=False)

    loaded = mr.load(BoolContainer, raw)
    dumped = mr.dump(loaded)

    assert loaded == BoolContainer(bool_field=False)
    assert dumped == raw

    assert mr.schema(BoolContainer) is mr.schema(BoolContainer)


def test_custom_name_uuid() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class UuidContainer:
        uuid_field: uuid.UUID = dataclasses.field(metadata=mr.meta(name="UuidField"))

    raw = {"UuidField": "15f75b02-1c34-46a2-92a5-18363aadea05"}

    loaded = mr.load(UuidContainer, raw)
    dumped = mr.dump(loaded)

    assert loaded == UuidContainer(uuid_field=uuid.UUID("15f75b02-1c34-46a2-92a5-18363aadea05"))
    assert dumped == raw

    assert mr.schema(UuidContainer) is mr.schema(UuidContainer)


def test_none() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class BoolContainer:
        bool_field: bool | None = None

    raw: dict[str, Any] = dict()

    loaded = mr.load(BoolContainer, raw)
    dumped = mr.dump(loaded)

    assert loaded == BoolContainer(bool_field=None)
    assert dumped == raw

    assert mr.schema(BoolContainer) is mr.schema(BoolContainer)


def test_unknown_field() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class BoolContainer:
        bool_field: bool

    loaded = mr.load(BoolContainer, dict(bool_field=True, int_field=42))
    dumped = mr.dump(loaded)

    assert loaded == BoolContainer(bool_field=True)
    assert dumped == dict(bool_field=True)

    assert mr.schema(BoolContainer) is mr.schema(BoolContainer)


def test_schema_with_default_case() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class DataClass:
        str_field: str

    origin = dict(str_field="foobar")
    loaded = mr.load(DataClass, origin)
    dumped = mr.dump(loaded)

    assert loaded == DataClass(str_field="foobar")
    assert dumped == origin


def test_schema_with_capital_camel_case() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class DataClass:
        str_field: str

    origin = dict(StrField="foobar")
    loaded = mr.load(DataClass, origin, naming_case=mr.CAPITAL_CAMEL_CASE)
    dumped = mr.dump(loaded, naming_case=mr.CAPITAL_CAMEL_CASE)

    assert loaded == DataClass(str_field="foobar")
    assert dumped == origin


def test_schema_with_camel_case() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class DataClass:
        str_field: str

    origin = dict(strField="foobar")
    loaded = mr.load(DataClass, origin, naming_case=mr.CAMEL_CASE)
    dumped = mr.dump(loaded, naming_case=mr.CAMEL_CASE)

    assert loaded == DataClass(str_field="foobar")
    assert dumped == origin


def test_many() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class BoolContainer:
        bool_field: bool

    loaded = mr.load_many(BoolContainer, [dict(bool_field=True), dict(bool_field=False)])
    dumped = mr.dump_many(loaded)

    assert loaded == [BoolContainer(bool_field=True), BoolContainer(bool_field=False)]
    assert dumped == [dict(bool_field=True), dict(bool_field=False)]

    assert mr.schema(BoolContainer) is mr.schema(BoolContainer)


def test_many_empty() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class BoolContainer:
        bool_field: bool

    loaded = mr.load_many(BoolContainer, [])
    dumped = mr.dump_many(loaded)

    assert loaded == []
    assert dumped == []

    assert mr.schema(BoolContainer) is mr.schema(BoolContainer)


@pytest.mark.parametrize(
    "raw, dt",
    [
        ("2022-02-20T11:33:48.607289+00:00", datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc)),
        ("2022-02-20T11:33:48.607289", datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc)),
        ("2022-02-20T11:33:48", datetime.datetime(2022, 2, 20, 11, 33, 48, 0, datetime.timezone.utc)),
        ("2022-02-20T11:33:48.607289Z", datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc)),
        ("2022-02-20T11:33:48Z", datetime.datetime(2022, 2, 20, 11, 33, 48, 0, datetime.timezone.utc)),
        ("2022-02-20", datetime.datetime(2022, 2, 20, 0, 0, 0, 0, datetime.timezone.utc)),
    ],
)
def test_datetime_field_load(raw: str, dt: datetime.datetime) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class DateTimeContainer:
        datetime_field: datetime.datetime

    loaded = mr.load(DateTimeContainer, dict(datetime_field=raw))
    assert loaded == DateTimeContainer(datetime_field=dt)


@pytest.mark.parametrize(
    "dt, raw",
    [
        (datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc), "2022-02-20T11:33:48.607289+00:00"),
        (datetime.datetime(2022, 2, 20, 11, 33, 48, 0, datetime.timezone.utc), "2022-02-20T11:33:48+00:00"),
        (datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, None), "2022-02-20T11:33:48.607289+00:00"),
        (datetime.datetime(2022, 2, 20, 11, 33, 48, 0, None), "2022-02-20T11:33:48+00:00"),
        (datetime.datetime(2022, 2, 20, 0, 0, 0, 0, None), "2022-02-20T00:00:00+00:00"),
    ],
)
def test_datetime_field_dump(dt: datetime.datetime, raw: str) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class DateTimeContainer:
        datetime_field: datetime.datetime

    dumped = mr.dump(DateTimeContainer(datetime_field=dt))
    assert dumped == dict(datetime_field=raw)


@pytest.mark.parametrize(
    "value, raw",
    [
        (Parity.ODD, "odd"),
        (Parity.EVEN, "even"),
    ],
)
def test_enum_str_field_dump(value: Parity, raw: str) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class EnumContainer:
        enum_field: Parity

    dumped = mr.dump(EnumContainer(enum_field=value))
    assert dumped == dict(enum_field=raw)


@pytest.mark.parametrize(
    "raw, value",
    [
        ("odd", Parity.ODD),
        ("even", Parity.EVEN),
    ],
)
def test_enum_str_field_load(value: Parity, raw: str) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class EnumContainer:
        enum_field: Parity

    dumped = mr.load(EnumContainer, dict(enum_field=raw))
    assert dumped == EnumContainer(enum_field=value)


@pytest.mark.parametrize(
    "value, raw",
    [
        (Bit.Zero, 0),
        (Bit.One, 1),
    ],
)
def test_enum_int_field_dump(value: Bit, raw: str) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class EnumContainer:
        enum_field: Bit

    dumped = mr.dump(EnumContainer(enum_field=value))
    assert dumped == dict(enum_field=raw)


@pytest.mark.parametrize(
    "raw, value",
    [
        (0, Bit.Zero),
        (1, Bit.One),
    ],
)
def test_enum_int_field_load(value: Bit, raw: str) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class EnumContainer:
        enum_field: Bit

    dumped = mr.load(EnumContainer, dict(enum_field=raw))
    assert dumped == EnumContainer(enum_field=value)


def test_naming_case_in_options() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    @mr.options(naming_case=mr.CAMEL_CASE)
    class TestFieldContainer:
        test_field: str

    dumped = mr.dump(TestFieldContainer(test_field="some_value"))
    assert dumped == {"testField": "some_value"}


def test_naming_case_in_options_should_not_affect_field_schemas() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Container:
        value: str

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    @mr.options(naming_case=mr.CAPITAL_CAMEL_CASE)
    class ContainerContainer:
        value: Container

    dumped = mr.dump(ContainerContainer(value=Container(value="some_value")))
    assert dumped == {"Value": {"value": "some_value"}}


def test_dict_with_complex_value() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class IdContainer:
        id: uuid.UUID

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Container:
        values: dict[str, IdContainer]

    id = uuid.uuid4()

    container = Container(values={"key": IdContainer(id=id)})

    dumped = mr.dump(container)
    assert dumped == {"values": {"key": {"id": str(id)}}}

    assert container == mr.load(Container, dumped)


def test_bake_schema_should_reuse_already_generated_schemas() -> None:
    schema_cache = getattr(getattr(mr, "bake"), "_schema_types")

    schema_cache.clear()

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Holder:
        value: int

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class HolderHolder:
        holder: Holder

    mr.bake_schema(HolderHolder)
    mr.bake_schema(Holder)

    assert len(schema_cache) == 2


@pytest.mark.parametrize("naming_case", [mr.CAMEL_CASE, None])
@pytest.mark.parametrize("none_value_handling", [mr.NoneValueHandling.INCLUDE, None])
def test_bake_schema_should_generate_schemas_per_parameters(
    naming_case: mr.NamingCase | None, none_value_handling: mr.NoneValueHandling | None
) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Holder:
        value: int

    default_schema = mr.bake_schema(Holder)
    parametrised_schema = mr.bake_schema(Holder, naming_case=naming_case, none_value_handling=none_value_handling)

    if naming_case is None and none_value_handling is None:
        assert default_schema is parametrised_schema
    else:
        assert default_schema is not parametrised_schema


def test_legacy_collection_typings() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Container:
        list_field: List[int]
        dict_field: Dict[str, Any]
        set_field: Set[str]
        frozenset_field: FrozenSet[str]
        tuple_field: Tuple[str, ...]

    assert mr.schema(Container)


def test_str_strip_whitespaces() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class StrContainer:
        value: Annotated[str, mr.str_meta(strip_whitespaces=True)]

    assert StrContainer(value="some_value") == mr.load(StrContainer, {"value": " some_value "})
    assert mr.dump(StrContainer(value=" some_value ")) == {"value": "some_value"}

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class OptionalStrContainer:
        value1: Annotated[str | None, mr.str_meta(strip_whitespaces=True)]
        value2: Annotated[str | None, mr.str_meta(strip_whitespaces=False)]

    assert OptionalStrContainer(value1=None, value2="") == mr.load(OptionalStrContainer, {"value1": "", "value2": ""})
    assert OptionalStrContainer(value1=None, value2=None) == mr.load(
        OptionalStrContainer, {"value1": None, "value2": None}
    )
    assert mr.dump(OptionalStrContainer(value1="", value2="")) == {"value2": ""}
    assert mr.dump(OptionalStrContainer(value1=None, value2=None)) == {}


def test_list_str_strip_whitespaces() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class StrContainer:
        value1: list[Annotated[str, mr.str_meta(strip_whitespaces=True)]]
        value2: list[Annotated[str, mr.str_meta(strip_whitespaces=True)]] | None

    assert StrContainer(value1=["some_value"], value2=None) == mr.load(StrContainer, {"value1": [" some_value "]})
    assert mr.dump(StrContainer(value1=[" some_value "], value2=None)) == {"value1": ["some_value"]}


def test_str_post_load() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class StrContainer:
        value1: Annotated[str, mr.str_meta(post_load=lambda x: x.replace("-", ""))]
        value2: Annotated[str | None, mr.str_meta(post_load=lambda x: x.replace("-", ""))]

    assert StrContainer(value1="111111", value2=None) == mr.load(StrContainer, {"value1": "11-11-11"})
    assert mr.dump(StrContainer(value1="11-11-11", value2=None)) == {"value1": "11-11-11"}


def test_nested_default() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class IntContainer:
        value: int = 42

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class RootContainer:
        int_container: IntContainer = dataclasses.field(default_factory=IntContainer)

    assert mr.load(RootContainer, {}) == RootContainer()


@pytest.mark.parametrize(
    "frozen, slots, get_type, context",
    [
        (False, False, lambda x: None, does_not_raise()),
        (False, False, lambda x: int, pytest.raises(ValueError, match="<class 'int'> is invalid but can be removed")),
        (True, False, lambda x: None, pytest.raises(ValueError, match="Explicit cls required for unsubscripted type")),
        (False, True, lambda x: None, pytest.raises(ValueError, match="Explicit cls required for unsubscripted type")),
        (True, True, lambda x: None, pytest.raises(ValueError, match="Explicit cls required for unsubscripted type")),
        (True, True, lambda x: get_origin(x), pytest.raises(ValueError, match=".Data'> is not subscripted version of")),
        (True, True, lambda x: list[int], pytest.raises(ValueError, match="int] is not subscripted version of")),
        (True, True, lambda x: int, pytest.raises(ValueError, match="<class 'int'> is not subscripted version of")),
        (True, True, lambda x: x, does_not_raise()),
    ],
)
def test_generic_extract_type_on_dump(
    frozen: bool, slots: bool, get_type: Callable[[type], type | None], context: ContextManager
) -> None:
    _TValue = TypeVar("_TValue")

    @dataclasses.dataclass(frozen=frozen, slots=slots)
    class Data(Generic[_TValue]):
        value: _TValue

    instance = Data[int](value=123)
    with context:
        dumped = mr.dump(instance, cls=get_type(Data[int]))
        assert dumped == {"value": 123}

    instance_many = [Data[int](value=123), Data[int](value=456)]
    with context:
        dumped = mr.dump_many(instance_many, cls=get_type(Data[int]))
        assert dumped == [{"value": 123}, {"value": 456}]


@pytest.mark.parametrize(
    "frozen, slots, get_type, context",
    [
        (False, False, lambda x: None, does_not_raise()),
        (False, True, lambda x: x, does_not_raise()),
        (True, False, lambda x: x, does_not_raise()),
        (True, True, lambda x: x, does_not_raise()),
        (False, False, lambda x: int, pytest.raises(ValueError, match="<class 'int'> is invalid but can be removed")),
        (True, True, lambda x: int, pytest.raises(ValueError, match="<class 'int'> is invalid but can be removed")),
    ],
)
def test_non_generic_extract_type_on_dump(
    frozen: bool, slots: bool, get_type: Callable[[type], type | None], context: ContextManager
) -> None:
    @dataclasses.dataclass(frozen=frozen, slots=slots)
    class Data:
        value: int

    instance = Data(value=123)
    with context:
        dumped = mr.dump(instance, cls=get_type(Data))
        assert dumped == {"value": 123}

    instance_many = [Data(value=123), Data(value=456)]
    with context:
        dumped = mr.dump_many(instance_many, cls=get_type(Data))
        assert dumped == [{"value": 123}, {"value": 456}]


def test_generic_in_parents() -> None:
    _TXxx = TypeVar("_TXxx")
    _TData = TypeVar("_TData")

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class Data(Generic[_TXxx]):
        xxx: _TXxx

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class ParentClass(Generic[_TData]):
        value: str
        data: _TData

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class ChildClass(ParentClass[Data[int]]):
        pass

    instance = ChildClass(value="vvv", data=Data(xxx=111))
    dumped = mr.dump(instance)

    assert dumped == {"value": "vvv", "data": {"xxx": 111}}
    assert mr.load(ChildClass, dumped) == instance


def test_generic_type_var_with_reuse() -> None:
    _T = TypeVar("_T")

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class T1(Generic[_T]):
        t1: _T

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class T2(Generic[_T], T1[int]):
        t2: _T

    instance = T2[str](t1=1, t2="2")

    dumped = mr.dump(instance, cls=T2[str])

    assert dumped == {"t1": 1, "t2": "2"}
    assert mr.load(T2[str], dumped) == instance


def test_generic_with_field_override() -> None:
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

    instance = T2[Value2, int](value=Value2(v1="aaa", v2="bbb"), iterable=set([3, 4, 5]))

    dumped = mr.dump(instance, cls=T2[Value2, int])

    assert dumped == {"value": {"v1": "aaa", "v2": "bbb"}, "iterable": [3, 4, 5]}
    assert mr.load(T2[Value2, int], dumped) == instance


def test_generic_reuse_with_different_args() -> None:
    _TItem = TypeVar("_TItem")

    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class GenericContainer(Generic[_TItem]):
        items: list[_TItem]

    container_int = GenericContainer[int](items=[1, 2, 3])
    dumped = mr.dump(container_int, cls=GenericContainer[int])

    assert dumped == {"items": [1, 2, 3]}
    assert mr.load(GenericContainer[int], dumped) == container_int

    container_str = GenericContainer[str](items=["q", "w", "e"])
    dumped = mr.dump(container_str, cls=GenericContainer[str])

    assert dumped == {"items": ["q", "w", "e"]}
    assert mr.load(GenericContainer[str], dumped) == container_str
