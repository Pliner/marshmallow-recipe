import dataclasses
import datetime
import decimal
import enum
import uuid
from typing import Any

import pytest

import marshmallow_recipe as mr


class Parity(str, enum.Enum):
    ODD = "odd"
    EVEN = "even"


def test_simple_types() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class SimpleTypesContainers:
        any_field: Any
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
        date_field: datetime.date
        optional_date_field: datetime.date | None
        dict_field: dict[str, Any]
        optional_dict_field: dict[str, Any] | None
        custom_dict_field: dict[datetime.date, int]
        optional_custom_dict_field: dict[datetime.date, int] | None
        list_field: list[str]
        optional_list_field: list[str] | None
        enum_field: Parity
        optional_enum_field: Parity | None
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
        date_field_with_default: datetime.date = datetime.date(2022, 2, 20)
        enum_field_with_default: Parity = Parity.ODD
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
        date_field_with_default_factory: datetime.date = dataclasses.field(
            default_factory=lambda: datetime.date(2022, 2, 20)
        )
        dict_field_with_default_factory: dict[str, Any] = dataclasses.field(default_factory=lambda: {})
        custom_dict_field_with_default_factory: dict[datetime.date, int] = dataclasses.field(default_factory=lambda: {})
        list_field_with_default_factory: list[str] = dataclasses.field(default_factory=lambda: [])
        enum_field_with_default_factory: Parity = dataclasses.field(default_factory=lambda: Parity.ODD)

    raw = dict(
        any_field={},
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
        datetime_field="2022-02-20T11:33:48.607289+00:00",
        datetime_field_with_default="2022-02-20T11:33:48.607289+00:00",
        datetime_field_with_default_factory="2022-02-20T11:33:48.607289+00:00",
        optional_datetime_field="2022-02-20T11:33:48.607289+00:00",
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
        enum_field="odd",
        enum_field_with_default="odd",
        enum_field_with_default_factory="odd",
        optional_enum_field="even",
    )

    raw_no_defaults = {k: v for k, v in raw.items() if not k.endswith("default") or not k.endswith("default_factory")}

    loaded = mr.load(SimpleTypesContainers, raw)
    loaded_no_defaults = mr.load(SimpleTypesContainers, raw_no_defaults)
    dumped = mr.dump(loaded)

    assert (
        loaded_no_defaults
        == loaded
        == SimpleTypesContainers(
            any_field={},
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
            datetime_field=datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc),
            optional_datetime_field=datetime.datetime(2022, 2, 20, 11, 33, 48, 607289, datetime.timezone.utc),
            date_field=datetime.date(2022, 2, 20),
            optional_date_field=datetime.date(2022, 2, 20),
            dict_field=dict(key="value"),
            optional_dict_field=dict(key="value"),
            custom_dict_field={datetime.date(2020, 1, 1): 42},
            optional_custom_dict_field={datetime.date(2020, 1, 1): 42},
            list_field=["value"],
            optional_list_field=["value"],
            enum_field=Parity.ODD,
            optional_enum_field=Parity.EVEN,
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


def test_custom_name() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class BoolContainer:
        bool_field: bool = dataclasses.field(metadata=mr.metadata(name="BoolField"))

    raw = dict(BoolField=False)

    loaded = mr.load(BoolContainer, raw)
    dumped = mr.dump(loaded)

    assert loaded == BoolContainer(bool_field=False)
    assert dumped == raw

    assert mr.schema(BoolContainer) is mr.schema(BoolContainer)


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
    loaded = mr.load(DataClass, origin, naming_case=mr.DEFAULT_CASE)
    dumped = mr.dump(loaded, naming_case=mr.DEFAULT_CASE)

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
def test_enum_field_dump(value: Parity, raw: str) -> None:
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
def test_enum_field_load(value: Parity, raw: str) -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    class EnumContainer:
        enum_field: Parity

    dumped = mr.load(EnumContainer, dict(enum_field=raw))
    assert dumped == EnumContainer(enum_field=value)


def test_naming_case_in_options() -> None:
    @dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
    @mr.options(naming_case=mr.CAMEL_CASE)
    class TestFieldContainer:
        test_field: str

    dumped = mr.dump(TestFieldContainer(test_field="some_value"))
    assert dumped == {"testField": "some_value"}


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
