import dataclasses
import types
import typing
from typing import TYPE_CHECKING, Annotated, Any, Generic, TypeAlias, TypeVar, Union, get_args, get_origin

_GenericAlias: TypeAlias = typing._GenericAlias  # type: ignore

if TYPE_CHECKING:
    from _typeshed import DataclassInstance
else:
    DataclassInstance: TypeAlias = type

TypeLike: TypeAlias = type | TypeVar | types.UnionType | types.GenericAlias | _GenericAlias
FieldsTypeMap: TypeAlias = dict[str, TypeLike]
TypeVarMap: TypeAlias = dict[TypeVar, TypeLike]
FieldsClassMap: TypeAlias = dict[str, TypeLike]
ClassTypeVarMap: TypeAlias = dict[TypeLike, TypeVarMap]
FieldsTypeVarMap: TypeAlias = dict[str, TypeVarMap]


def extract_type(data: Any, cls: type | None) -> type:
    data_type = _get_orig_class(data) or type(data)

    if not _is_unsubscripted_type(data_type):
        if cls and data_type != cls:
            raise ValueError(f"{cls=} is invalid but can be removed, actual type is {data_type}")
        return data_type

    if not cls:
        raise ValueError(f"Explicit cls required for unsubscripted type {data_type}")

    if _is_unsubscripted_type(cls) or get_origin(cls) != data_type:
        raise ValueError(f"{cls=} is not subscripted version of {data_type}")

    return cls


def get_fields_type_map(cls: type) -> FieldsTypeMap:
    origin: type = get_origin(cls) or cls
    if not dataclasses.is_dataclass(origin):
        raise ValueError(f"{origin} is not a dataclass")

    class_type_var_map = get_class_type_var_map(cls)
    fields_class_map = get_fields_class_map(origin)
    return {
        f.name: build_subscripted_type(f.type, class_type_var_map.get(fields_class_map[f.name], {}))
        for f in dataclasses.fields(origin)
    }


def get_fields_class_map(cls: type[DataclassInstance]) -> FieldsClassMap:
    names: dict[str, dataclasses.Field] = {}
    result: FieldsClassMap = {}

    mro = cls.__mro__
    for cls in (*mro[-1:0:-1], cls):
        if not dataclasses.is_dataclass(cls):
            continue
        for field in dataclasses.fields(cls):
            if names.get(field.name) != field:
                names[field.name] = field
                result[field.name] = cls

    return result


def build_subscripted_type(t: TypeLike, type_var_map: TypeVarMap) -> TypeLike:
    if isinstance(t, TypeVar):
        return build_subscripted_type(type_var_map[t], type_var_map)

    origin = get_origin(t)
    if origin is Union or origin is types.UnionType:
        return Union[*(build_subscripted_type(x, type_var_map) for x in get_args(t))]

    if origin is Annotated:
        t, *annotations = get_args(t)
        return Annotated[build_subscripted_type(t, type_var_map), *annotations]

    if origin and isinstance(t, types.GenericAlias):
        return types.GenericAlias(origin, tuple(build_subscripted_type(x, type_var_map) for x in get_args(t)))

    if origin and isinstance(t, _GenericAlias):
        return _GenericAlias(origin, tuple(build_subscripted_type(x, type_var_map) for x in get_args(t)))

    return _subscript_with_any(t)


def get_class_type_var_map(t: TypeLike) -> ClassTypeVarMap:
    class_type_var_map: ClassTypeVarMap = {}
    _build_class_type_var_map(t, class_type_var_map)
    return class_type_var_map


def _build_class_type_var_map(t: TypeLike, class_type_var_map: ClassTypeVarMap) -> None:
    if _get_params(t):
        raise ValueError(f"Expected subscripted generic, but got unsubscripted {t}")

    type_var_map: TypeVarMap = {}
    origin = get_origin(t) or t
    params = _get_params(origin)
    args = get_args(t)
    if params or args:
        if not params or not args or len(params) != len(args):
            raise ValueError(f"Unexpected generic {t}")
        for i, parameter in enumerate(params):
            assert isinstance(parameter, TypeVar)
            type_var_map[parameter] = args[i]
        if origin not in class_type_var_map:
            class_type_var_map[origin] = type_var_map
        elif class_type_var_map[origin] != type_var_map:
            raise ValueError(
                f"Incompatible Base class {origin} with generic args {class_type_var_map[origin]} and {type_var_map}"
            )

    if orig_bases := _get_orig_bases(origin):
        for orig_base in orig_bases:
            if get_origin(orig_base) is Generic:
                continue
            subscripted_base = build_subscripted_type(orig_base, type_var_map)
            _build_class_type_var_map(subscripted_base, class_type_var_map)


def _is_unsubscripted_type(t: TypeLike) -> bool:
    return bool(_get_params(t)) or any(_is_unsubscripted_type(arg) for arg in get_args(t) or [])


def _get_orig_class(t: Any) -> type | None:
    return getattr(t, "__orig_class__", None)


def _get_params(t: Any) -> tuple[TypeLike, ...] | None:
    return getattr(t, "__parameters__", None)


def _get_orig_bases(t: Any) -> tuple[TypeLike, ...] | None:
    return getattr(t, "__orig_bases__", None)


def _subscript_with_any(t: TypeLike) -> TypeLike:
    if t is list:
        return list[Any]
    if t is set:
        return set[Any]
    if t is frozenset:
        return frozenset[Any]
    if t is dict:
        return dict[Any, Any]
    if t is tuple:
        return tuple[Any, ...]
    return t
