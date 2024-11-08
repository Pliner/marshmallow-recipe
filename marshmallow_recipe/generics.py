import dataclasses
import typing
from dataclasses import Field
from types import GenericAlias, UnionType
from typing import Annotated, Any, Generic, TypeAlias, TypeVar, Union, get_args, get_origin

_GenericAlias: TypeAlias = typing._GenericAlias  # type: ignore

TypeLike: TypeAlias = type | TypeVar | UnionType | GenericAlias | _GenericAlias
TypeVarMap: TypeAlias = dict[TypeVar, TypeLike]
ClassTypeVarMap: TypeAlias = dict[TypeLike, TypeVarMap]
FieldsTypeVarMap: TypeAlias = dict[str, TypeVarMap]
FieldsClassMap: TypeAlias = dict[str, TypeLike]
FieldsTypeMap: TypeAlias = dict[str, TypeLike]


def get_fields_type_map(t: TypeLike) -> FieldsTypeMap:
    origin = get_origin(t) or t
    if not dataclasses.is_dataclass(origin):
        return {}

    class_type_var_map = get_class_type_var_map(t)
    fields_type_map = get_fields_class_map(t)
    return {
        f.name: build_subscripted_type(f.type, class_type_var_map.get(fields_type_map[f.name], {}))
        for f in dataclasses.fields(origin)
    }


def get_fields_class_map(t: TypeLike) -> FieldsClassMap:
    origin = get_origin(t) or t
    if not dataclasses.is_dataclass(origin):
        return {}

    names: dict[str, Field] = {}
    result: FieldsClassMap = {}

    mro = origin.__mro__  # type: ignore
    for base in (*mro[-1:0:-1], origin):
        if not dataclasses.is_dataclass(base):
            continue
        for field in dataclasses.fields(base):
            if names.get(field.name) != field:
                names[field.name] = field
                result[field.name] = base
    return result


def build_subscripted_type(t: TypeLike, type_var_map: TypeVarMap) -> TypeLike:
    if isinstance(t, TypeVar):
        return build_subscripted_type(type_var_map[t], type_var_map)

    origin = get_origin(t)
    if origin is Union or isinstance(t, UnionType):
        return Union[*(build_subscripted_type(x, type_var_map) for x in get_args(t))]  # type: ignore

    if origin is Annotated:
        t, *annotations = get_args(t)
        return Annotated[build_subscripted_type(t, type_var_map), *annotations]  # type: ignore

    if origin and isinstance(t, GenericAlias):
        return GenericAlias(origin, tuple(build_subscripted_type(x, type_var_map) for x in get_args(t)))

    if origin and isinstance(t, _GenericAlias):
        return _GenericAlias(origin, tuple(build_subscripted_type(x, type_var_map) for x in get_args(t)))

    return _subscript_with_any(t)


def get_class_type_var_map(t: TypeLike) -> ClassTypeVarMap:
    class_type_var_map: ClassTypeVarMap = {}
    _get_class_type_var_map(t, class_type_var_map)
    return class_type_var_map


def _get_class_type_var_map(t: TypeLike, class_type_var_map: ClassTypeVarMap) -> None:
    if _get_parameters(t):
        raise Exception(f"Expected subscripted generic, but got unsubscripted {t}")

    type_var_map: TypeVarMap = {}
    origin = get_origin(t) or t
    parameters = _get_parameters(origin)
    args = get_args(t)
    if parameters or args:
        if not parameters or not args or len(parameters) != len(args):
            raise Exception(f"Unexpected generic {t}")
        class_type_var_map[origin] = type_var_map
        for i, parameter in enumerate(parameters):
            assert isinstance(parameter, TypeVar)
            type_var_map[parameter] = args[i]

    if orig_bases := _get_orig_bases(origin):
        for orig_base in orig_bases:
            if get_origin(orig_base) is not Generic:
                _get_class_type_var_map(build_subscripted_type(orig_base, type_var_map), class_type_var_map)


def _get_parameters(t: Any) -> tuple[TypeLike, ...] | None:
    return hasattr(t, "__parameters__") and getattr(t, "__parameters__") or None


def _get_orig_bases(t: Any) -> tuple[TypeLike, ...] | None:
    return hasattr(t, "__orig_bases__") and getattr(t, "__orig_bases__") or None


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
