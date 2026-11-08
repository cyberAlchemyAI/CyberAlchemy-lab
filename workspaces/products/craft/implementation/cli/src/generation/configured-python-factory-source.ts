/** Native immutable validated-factory pipeline. No ambient predicate injection,
 * persistence, reference resolution, reflection sandbox or runtime graph. */
export function renderPythonFactorySupport(): string {
  return String.raw`from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Callable
from weakref import ref
from .values import ValueProtocol, part

_snapshots = {}
_factories = {}


def _lookup(registry, value):
    entry = registry.get(id(value))
    return entry[1:] if entry is not None and entry[0]() is value else None


def _register(registry, value, *data):
    identity = id(value)
    def cleanup(reference):
        entry = registry.get(identity)
        if entry is not None and entry[0] is reference:
            del registry[identity]
    registry[identity] = (ref(value, cleanup), *data)


class OwnedSnapshot:
    __slots__ = ()
    def __eq__(self, other):
        left, right = _lookup(_snapshots, self), _lookup(_snapshots, other)
        return left is not None and right is not None and left[0] is right[0] and left[1] == right[1]
    def __hash__(self):
        entry = _lookup(_snapshots, self)
        if entry is None:
            raise TypeError("UNOWNED_SNAPSHOT")
        value = int.from_bytes(sha256(entry[1].encode("utf-16-le", "surrogatepass")).digest()[:8], "big", signed=True)
        return -2 if value == -1 else value


@dataclass(frozen=True, slots=True)
class Validator:
    rule: str
    closure_sha256: str
    artifact_sha256: str
    validate: Callable


@dataclass(frozen=True, slots=True)
class ValidatorTrace:
    rule: str
    closure_sha256: str
    artifact_sha256: str
    outcome: str


@dataclass(frozen=True, slots=True)
class Trace:
    route: str
    phases: tuple[str, ...]
    validators: tuple[ValidatorTrace, ...]


@dataclass(frozen=True, slots=True)
class Result:
    ok: bool
    value: object | None
    failure_codes: tuple[str, ...]
    trace: Trace


def invalid_fact():
    raise TypeError("INVALID_RULE_FACT")


def factory_provider(snapshot_type, fields_type, field_specs: tuple, key_fields: tuple[str, ...], concept: str, contract: str, base: tuple[Validator, ...], extensions: dict[str, tuple[Validator, ...]], entity: bool):
    owner = object()
    extension_table = dict(extensions)
    field_table = {name: (native, protocol) for name, native, protocol, _ in field_specs}
    allowed = frozenset(field_table)
    def owned(value):
        entry = _lookup(_snapshots, value)
        return entry is not None and entry[0] is owner
    def key(value):
        if not owned(value):
            raise TypeError("UNOWNED_SNAPSHOT")
        return _lookup(_snapshots, value)[1]
    def require_owned(value):
        key(value)
        return value
    component = ValueProtocol(require_owned, key, owned)
    def state(factory):
        entry = _lookup(_factories, factory)
        if entry is None or entry[0] is not owner:
            raise TypeError("UNOWNED_FACTORY")
        return entry[1:]
    def construct(factory, route, input, previous=None):
        _, validators = state(factory)
        phases, traces = ["normalize"], []
        def failure(code):
            return Result(False, None, (code,), Trace(route, tuple(phases), tuple(traces)))
        try:
            if type(input) is not dict or any(type(name) is not str for name in input) or not set(input).issubset(allowed):
                return failure("INVALID_FIELDS")
            normalized = {}
            for name, native, protocol, optional in field_specs:
                if name not in input and not optional:
                    return failure("INVALID_FIELDS")
                normalized[native] = protocol.normalize(input.get(name))
            fields = fields_type(**normalized)
        except Exception:
            return failure("INVALID_FIELDS")
        for validator in validators:
            try:
                outcome = "pass" if validator.validate(fields) is True else "fail"
            except Exception:
                outcome = "exception"
            traces.append(ValidatorTrace(validator.rule, validator.closure_sha256, validator.artifact_sha256, outcome))
            if outcome != "pass":
                return failure("RULE_" + outcome.upper() + ":" + validator.rule)
        if entity:
            phases.append("resolve-identity")
        identity = part(concept) + part(contract) + "".join(part(name) + part(field_table[name][1].key(getattr(fields, field_table[name][0]))) for name in key_fields)
        if entity and previous is not None and (not owned(previous) or key(previous) != identity):
            return failure("IDENTITY_CHANGED")
        phases.append("form")
        snapshot = object.__new__(snapshot_type)
        object.__setattr__(snapshot, "fields", fields)
        _register(_snapshots, snapshot, owner, identity)
        phases.append("freeze")
        return Result(True, snapshot, (), Trace(route, tuple(phases), tuple(traces)))

    @_dataclass_factory()
    class Factory:
        def __init__(self, *args, **kwargs):
            raise TypeError("FACTORY_CONSTRUCTION_REQUIRES_PROVIDER")
        @property
        def extensions(self):
            return state(self)[0]
        def create(self, input):
            return construct(self, "create", input)
        def reconstruct(self, input):
            return construct(self, "reconstruct", input)
        if entity:
            def transition(self, previous, input):
                state(self)
                if not owned(previous):
                    return Result(False, None, ("INVALID_PREVIOUS",), Trace("transition", (), ()))
                return construct(self, "transition", input, previous)
        def extend(self, id):
            ids, validators = state(self)
            if type(id) is not str or id not in extension_table or id in ids:
                raise TypeError("INVALID_EXTENSION")
            return make(ids + (id,), validators + extension_table[id])
    def make(ids=(), validators=base):
        factory = object.__new__(Factory)
        _register(_factories, factory, owner, ids, validators)
        return factory
    def create_factory():
        return make()
    return create_factory, component


def _dataclass_factory():
    return dataclass(frozen=True, slots=True, eq=False, init=False, weakref_slot=True)
`;
}
