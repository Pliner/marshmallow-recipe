import abc
import dataclasses
import datetime
import decimal
import functools
import types
import uuid
from typing import Any, TypeVar, Union, get_args, get_origin

import marshmallow as m

from .hooks import get_pre_loads
from .naming_case import NamingCase

NO_FIELD_NAME = "_schema"


def dump_slim(data: Any, *, naming_case: NamingCase | None = None) -> dict[str, Any]:
    cls = type(data)
    if not dataclasses.is_dataclass(cls):
        raise ValueError(f"{cls} is not a dataclass")
    if naming_case is not None:
        raise ValueError("naming_case is not supported")

    container = __get_field_for_dataclass(cls, naming_case=naming_case)
    return container.dump(data)


def dump_slim_many(data: list[Any], *, naming_case: NamingCase | None = None) -> list[dict[str, Any]]:
    if naming_case is not None:
        raise ValueError("naming_case is not supported")

    if not data:
        return []

    cls = type(data[0])
    container = __get_field_for_dataclass(cls, naming_case=naming_case)
    list_container = ListContainer(required=True, item_container=container)
    return list_container.dump(data)


_T = TypeVar("_T")


def load_slim(cls: type[_T], data: dict[str, Any], *, naming_case: NamingCase | None = None) -> dict[str, Any]:
    if not dataclasses.is_dataclass(cls):
        raise ValueError(f"{cls} is not a dataclass")
    if naming_case is not None:
        raise ValueError("naming_case is not supported")
    container = __get_field_for_dataclass(cls, naming_case=naming_case)
    return container.load(data)


def load_slim_many(
    cls: type[_T], data: list[dict[str, Any]], *, naming_case: NamingCase | None = None
) -> list[dict[str, Any]]:
    if naming_case is not None:
        raise ValueError("naming_case is not supported")

    if not data:
        return []

    container = __get_field_for_dataclass(cls, naming_case=naming_case)
    list_container = ListContainer(required=True, item_container=container)
    return list_container.load(data)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Container(abc.ABC):
    required: bool

    @abc.abstractmethod
    def dump(self, value: Any) -> Any:
        ...

    @abc.abstractmethod
    def load(self, value: Any) -> Any:
        ...


class RawContainer(Container):
    def dump(self, value: Any) -> Any:
        return value

    def load(self, value: Any) -> Any:
        return value


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ListContainer(Container):
    item_container: Container

    def dump(self, value: Any) -> Any:
        if not isinstance(value, list):
            raise m.ValidationError("Not a valid list.")

        container = []
        error_messages: dict[str, Any] | None = None

        for i in range(len(value)):
            try:
                container.append(self.item_container.dump(value[i]))
            except m.ValidationError as item_validation_error:
                error_messages = error_messages or {}
                error_messages[str(i)] = item_validation_error.messages

        if error_messages is not None:
            raise m.ValidationError(error_messages, NO_FIELD_NAME)

        return container

    def load(self, value: Any) -> Any:
        if not isinstance(value, list):
            raise m.ValidationError("Not a valid list.")

        container = []
        error_messages: dict[str, Any] | None = None

        for i in range(len(value)):
            try:
                container.append(self.item_container.load(value[i]))
            except m.ValidationError as item_validation_error:
                error_messages = error_messages or {}
                error_messages[str(i)] = item_validation_error.messages

        if error_messages is not None:
            raise m.ValidationError(error_messages, NO_FIELD_NAME)

        return container


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DictContainer(Container):
    key_container: Container
    value_container: Container

    def dump(self, value: Any) -> Any:
        if not isinstance(value, dict):
            raise m.ValidationError("Not a valid dict.")

        return {self.key_container.dump(key): self.value_container.dump(value) for key, value in value.items()}

    def load(self, value: Any) -> Any:
        if not isinstance(value, dict):
            raise m.ValidationError("Not a valid dict.")

        return {self.key_container.load(key): self.value_container.load(value) for key, value in value.items()}


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class UuidContainer(Container):
    def dump(self, value: Any) -> Any:
        if not isinstance(value, uuid.UUID):
            raise m.ValidationError("Not a valid uuid.")
        return str(value)

    def load(self, value: Any) -> Any:
        if not isinstance(value, str):
            raise m.ValidationError("Not a valid string.")
        try:
            return uuid.UUID(value)
        except ValueError:
            raise m.ValidationError("Not a valid uuid.")


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class IntContainer(Container):
    def dump(self, value: Any) -> Any:
        if not isinstance(value, int):
            raise m.ValidationError("Not a valid integer.")
        return value

    def load(self, value: Any) -> Any:
        if not isinstance(value, int):
            raise m.ValidationError("Not a valid integer.")
        return value


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class StrContainer(Container):
    def dump(self, value: Any) -> Any:
        if not isinstance(value, str):
            raise m.ValidationError("Not a valid string.")
        return value

    def load(self, value: Any) -> Any:
        if not isinstance(value, str):
            raise m.ValidationError("Not a valid string.")
        return value


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class BoolContainer(Container):
    def dump(self, value: Any) -> Any:
        if value is True:
            return True
        if value is False:
            return False
        raise m.ValidationError("Not a valid boolean.")

    def load(self, value: Any) -> Any:
        if value is True:
            return True
        if value is False:
            return False
        raise m.ValidationError("Not a valid boolean.")


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DatetimeContainer(Container):
    def dump(self, value: Any) -> Any:
        if not isinstance(value, datetime.datetime):
            raise m.ValidationError("Not a valid datetime.")
        return value.isoformat()

    def load(self, value: Any) -> Any:
        if not isinstance(value, str):
            raise m.ValidationError("Not a valid string.")
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            raise m.ValidationError("Not a valid datetime.")


@functools.cache
def _exponent_for(places: int) -> decimal.Decimal:
    if places < 0:
        raise ValueError(f"{places=} must be >= 0")
    return decimal.Decimal(10) ** -places


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DecimalContainer(Container):
    places: int = 2

    def dump(self, value: Any) -> Any:
        if not isinstance(value, decimal.Decimal):
            raise m.ValidationError("Not a valid number.")
        if value.is_nan() or value.is_infinite():
            raise m.ValidationError("Special numeric values (nan or infinity) are not permitted.")
        value = value.quantize(_exponent_for(self.places))
        return str(value)

    def load(self, value: Any) -> Any:
        if not isinstance(value, str):
            raise m.ValidationError("Not a valid string.")
        try:
            result = decimal.Decimal(value)
        except ValueError:
            raise m.ValidationError("Not a valid number.")
        if result.is_nan() or result.is_infinite():
            raise m.ValidationError("Special numeric values (nan or infinity) are not permitted.")
        result = result.quantize(_exponent_for(self.places))
        return result


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DataclassContainerField:
    name: str
    data_name: str
    container: Container


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DataclassContainer(Container):
    dataclass_type: type
    dataclass_fields: tuple[DataclassContainerField, ...]

    def dump(self, value: Any) -> Any:
        if not isinstance(value, self.dataclass_type):
            raise m.ValidationError(f"Not a valid {self.dataclass_type}.")

        container = {}
        error_messages: dict[str, Any] | None = None

        for dataclass_field in self.dataclass_fields:
            field_value = getattr(value, dataclass_field.name)
            if field_value is None and not dataclass_field.container.required:
                continue
            try:
                container[dataclass_field.data_name] = dataclass_field.container.dump(field_value)
            except m.ValidationError as field_validation_error:
                error_messages = error_messages or {}
                error_messages[dataclass_field.name] = field_validation_error.messages

        if error_messages is not None:
            raise m.ValidationError(error_messages, NO_FIELD_NAME)

        return container

    def load(self, value: Any) -> Any:
        if not isinstance(value, dict):
            raise m.ValidationError("Not a valid dict.")

        for pre_load in get_pre_loads(self.dataclass_type):
            value = pre_load(value)

        fields = {}
        error_messages: dict[str, Any] | None = None

        for dataclass_field in self.dataclass_fields:
            field_value = value.get(dataclass_field.data_name)
            if field_value is None and not dataclass_field.container.required:
                fields[dataclass_field.name] = None
                continue

            try:
                fields[dataclass_field.name] = dataclass_field.container.load(field_value)
            except m.ValidationError as field_validation_error:
                error_messages = error_messages or {}
                error_messages[dataclass_field.name] = field_validation_error.messages

        if error_messages is not None:
            raise m.ValidationError(error_messages, NO_FIELD_NAME)

        return self.dataclass_type(**fields)


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class DataclassFieldCacheKey:
    type: type
    naming_case: NamingCase | None


dataclass_container_cache: dict[DataclassFieldCacheKey, DataclassContainer] = {}


def __get_field_for_dataclass(dataclass_type: type, *, naming_case: NamingCase | None = None) -> DataclassContainer:
    if not dataclasses.is_dataclass(dataclass_type):
        raise ValueError(f"{dataclass_type} is not a dataclass")

    cache_key = DataclassFieldCacheKey(type=dataclass_type, naming_case=naming_case)
    if cached_container := dataclass_container_cache.get(cache_key):
        return cached_container

    container_field = DataclassContainer(
        required=True,
        dataclass_type=dataclass_type,
        dataclass_fields=tuple(
            DataclassContainerField(
                name=field.name,
                data_name=field.name if naming_case is None else naming_case(field.name),
                container=__get_field_for(field.type, naming_case=naming_case),
            )
            for field in dataclasses.fields(dataclass_type)
            if field.init
        ),
    )
    dataclass_container_cache[cache_key] = container_field
    return container_field


def __get_field_for(field_type: type, *, naming_case: NamingCase | None = None) -> Container:
    if field_type is Any:
        return RawContainer(required=False)

    field_type = __substitute_any_to_open_generic(field_type)

    if underlying_field_type := __try_get_underlying_type_from_optional(field_type):
        required = False
        field_type = underlying_field_type
    else:
        required = True

    if dataclasses.is_dataclass(field_type):
        dataclass_field = __get_field_for_dataclass(field_type, naming_case=naming_case)
        return dataclasses.replace(dataclass_field, required=required)

    if (origin := get_origin(field_type)) is not None:
        arguments = get_args(field_type)
        if origin is list:
            element_container = __get_field_for(arguments[0], naming_case=naming_case)
            return ListContainer(required=required, item_container=element_container)
        if origin is dict:
            key_container = __get_field_for(arguments[0], naming_case=naming_case)
            value_container = __get_field_for(arguments[1], naming_case=naming_case)
            return DictContainer(required=required, key_container=key_container, value_container=value_container)
    if field_type is int:
        return IntContainer(required=required)
    if field_type is bool:
        return BoolContainer(required=required)
    if field_type is str:
        return StrContainer(required=required)
    if field_type is uuid.UUID:
        return UuidContainer(required=required)
    if field_type is datetime.datetime:
        return DatetimeContainer(required=required)
    if field_type is decimal.Decimal:
        return DecimalContainer(required=required)
    raise ValueError(f"Unsupported {field_type=}")


def __try_get_underlying_type_from_optional(type: type) -> type | None:
    # to support Union[int, None] and int | None
    if get_origin(type) is Union or isinstance(type, types.UnionType):
        type_args = get_args(type)
        if types.NoneType not in type_args or len(type_args) != 2:
            raise ValueError(f"Unsupported {type=}")
        return next(type_arg for type_arg in type_args if type_arg is not types.NoneType)  # noqa

    return None


def __substitute_any_to_open_generic(type: type) -> type:
    if type is list:
        return list[Any]
    if type is set:
        return set[Any]
    if type is frozenset:
        return frozenset[Any]
    if type is dict:
        return dict[Any, Any]
    if type is tuple:
        return tuple[Any, ...]
    return type
