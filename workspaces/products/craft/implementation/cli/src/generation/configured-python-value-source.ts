/** Private statically composed Python value protocols; no runtime schema
 * interpreter. R10 scope and remaining factory work: R10-PYTHON.md. */
export function renderPythonValueSupport(): string {
  return String.raw`from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable, Generic, TypeVar
from weakref import ref

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ValueProtocol(Generic[T]):
    normalize: Callable[[object], T]
    key: Callable[[T], str]
    is_owned: Callable[[object], bool]


def part(value: str) -> str:
    return str(len(value.encode("utf-16-le", "surrogatepass")) // 2) + ":" + value


def _string(value: object) -> str:
    if type(value) is not str:
        raise TypeError("INVALID_STRING")
    # Python permits both an astral code point and explicit surrogate pairs;
    # they represent the same JavaScript UTF-16 string, without NFC folding.
    return value.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "surrogatepass")


def _bool(value: object) -> bool:
    if type(value) is not bool:
        raise TypeError("INVALID_BOOL")
    return value


def _uint64(value: object) -> int:
    if type(value) is int:
        result = value
    elif type(value) is str and 1 <= len(value) <= 20 and value.isascii() and value.isdecimal() and (value == "0" or value[0] != "0"):
        result = int(value)
    else:
        raise TypeError("INVALID_UINT64")
    if result < 0 or result > 18446744073709551615:
        raise TypeError("INVALID_UINT64")
    return result


STRING = ValueProtocol(_string, lambda x: part("String") + part(_string(x)), lambda x: type(x) is str)
BOOL = ValueProtocol(_bool, lambda x: part("Bool") + part("1" if _bool(x) else "0"), lambda x: type(x) is bool)
UINT64 = ValueProtocol(_uint64, lambda x: part("UInt64") + part(str(_uint64(x))), lambda x: type(x) is int and 0 <= x <= 18446744073709551615)


def optional_value(element: ValueProtocol[T]) -> ValueProtocol[T | None]:
    return ValueProtocol(
        lambda x: None if x is None else element.normalize(x),
        lambda x: part("Optional") + (part("absent") if x is None else part("present") + part(element.key(x))),
        lambda x: x is None or element.is_owned(x),
    )


def sequence_value(element: ValueProtocol[T], unique: bool) -> ValueProtocol[tuple[T, ...]]:
    def normalize(value: object) -> tuple[T, ...]:
        if type(value) is not list and type(value) is not tuple:
            raise TypeError("INVALID_COLLECTION")
        entries = [(element.normalize(item)) for item in value]
        keyed = [(element.key(item), item) for item in entries]
        if unique:
            keys = [key for key, _ in keyed]
            if len(set(keys)) != len(keys):
                raise TypeError("DUPLICATE_SET_VALUE")
            keyed.sort(key=lambda pair: pair[0].encode("utf-16-be", "surrogatepass"))
        return tuple(item for _, item in keyed)

    def key(value: tuple[T, ...]) -> str:
        if type(value) is not tuple:
            raise TypeError("UNOWNED_COLLECTION")
        keys = [element.key(item) for item in value]
        if unique:
            if len(set(keys)) != len(keys):
                raise TypeError("DUPLICATE_SET_VALUE")
            keys.sort(key=lambda item: item.encode("utf-16-be", "surrogatepass"))
        return part("Set" if unique else "List") + part(str(len(keys))) + "".join(part(item) for item in keys)

    def is_owned(value: object) -> bool:
        if type(value) is not tuple or not all(element.is_owned(item) for item in value):
            return False
        try:
            key(value)
            return True
        except TypeError:
            return False

    return ValueProtocol(normalize, key, is_owned)


def list_value(element: ValueProtocol[T]) -> ValueProtocol[tuple[T, ...]]:
    return sequence_value(element, False)


def set_value(element: ValueProtocol[T]) -> ValueProtocol[tuple[T, ...]]:
    return sequence_value(element, True)


_owned: dict[int, tuple[ref, object, str]] = {}


def _registration(value: object):
    entry = _owned.get(id(value))
    return entry if entry is not None and entry[0]() is value else None


class OwnedCase:
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        left, right = _registration(self), _registration(other)
        return left is not None and right is not None and left[1] is right[1] and left[2] == right[2]

    def __hash__(self) -> int:
        entry = _registration(self)
        if entry is None:
            raise TypeError("UNOWNED_SUM_CASE")
        # Process-independent hash; equality is nominal owner + complete key.
        value = int.from_bytes(sha256(entry[2].encode("utf-16-le", "surrogatepass")).digest()[:8], "big", signed=True)
        return -2 if value == -1 else value


def owned_value(component: ValueProtocol[T]) -> ValueProtocol[T]:
    def normalize(value: object) -> T:
        if not component.is_owned(value):
            raise TypeError("UNOWNED_COMPONENT")
        return value
    return ValueProtocol(normalize, component.key, component.is_owned)


def enum_value(kind, emit, concept: str, contract: str) -> ValueProtocol:
    def normalize(value):
        if type(value) is not kind:
            raise TypeError("UNOWNED_ENUM_CASE")
        emit(value)
        return value
    return ValueProtocol(normalize, lambda value: part("Enum") + part(concept) + part(contract) + part(emit(normalize(value))), lambda value: type(value) is kind and any(value is member for member in kind))


def sum_value(cases: dict[str, tuple[type[OwnedCase], ValueProtocol | None]], concept: str, contract: str) -> ValueProtocol:
    # Copy the static assembly so later mutation of the caller's dictionary
    # cannot change the component's closed alternatives.
    alternatives = dict(cases)
    owner = object()

    def is_owned(value: object) -> bool:
        entry = _registration(value)
        return entry is not None and entry[1] is owner

    def key(value: object) -> str:
        entry = _registration(value)
        if entry is None or entry[1] is not owner:
            raise TypeError("UNOWNED_SUM_CASE")
        return entry[2]

    def normalize(value: object):
        if type(value) is not dict or any(type(k) is not str for k in value):
            raise TypeError("INVALID_SUM")
        variant = value.get("variant")
        if type(variant) is not str or variant not in alternatives:
            raise TypeError("INVALID_SUM_VARIANT")
        kind, payload = alternatives[variant]
        if set(value) != ({"variant"} if payload is None else {"variant", "payload"}):
            raise TypeError("INVALID_SUM_PAYLOAD")
        normalized = None if payload is None else payload.normalize(value["payload"])
        signature = part(concept) + part(contract) + part("Sum") + part(variant) + (part("no-payload") if payload is None else part("payload") + part(payload.key(normalized)))
        result = object.__new__(kind)
        object.__setattr__(result, "variant", variant)
        if payload is not None:
            object.__setattr__(result, "payload", normalized)
        identifier = id(result)
        def release(reference):
            current = _owned.get(identifier)
            if current is not None and current[0] is reference:
                del _owned[identifier]
        _owned[identifier] = (ref(result, release), owner, signature)
        return result

    return ValueProtocol(normalize, key, is_owned)
`;
}
