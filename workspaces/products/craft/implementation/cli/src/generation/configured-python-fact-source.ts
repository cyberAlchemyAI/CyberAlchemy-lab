/** Immutable data facts for Rule evaluation, never validated domain snapshots.
 * Static protocol combinators only; no runtime graph/type/expression interpreter. */
export function renderPythonFactSupport(): string {
  return String.raw`from __future__ import annotations
from dataclasses import dataclass
from .values import ValueProtocol, part, optional_value, sequence_value


@dataclass(frozen=True, slots=True)
class _Fact:
    entries: tuple[tuple[str, object], ...]

    def __getitem__(self, name: str):
        for key, value in self.entries:
            if key == name:
                return value
        raise KeyError(name)


def _data(value: object) -> dict[str, object]:
    # Facts may flow into a referenced Rule, but confer no provider ownership.
    if type(value) is _Fact:
        entries = value.entries
        if type(entries) is not tuple or any(type(row) is not tuple or len(row) != 2 or type(row[0]) is not str for row in entries):
            raise TypeError("RULE_INPUT")
        if len({row[0] for row in entries}) != len(entries):
            raise TypeError("RULE_INPUT")
        return dict(entries)
    if type(value) is not dict or any(type(key) is not str for key in value):
        raise TypeError("RULE_INPUT")
    return value


def record_fact(kind: str, selector: str, fields: tuple, key_fields: tuple[str, ...]):
    allowed = frozenset(name for name, _, _ in fields)
    protocols = {name: protocol for name, protocol, _ in fields}
    def normalize(value):
        data = _data(value)
        if not set(data).issubset(allowed):
            raise TypeError("RULE_INPUT")
        entries = []
        for name, protocol, optional in fields:
            if name not in data and not optional:
                raise TypeError("RULE_INPUT")
            entries.append((name, protocol.normalize(data.get(name))))
        return _Fact(tuple(entries))
    def key(value):
        return part(kind) + part(selector) + "".join(part(name) + part(protocols[name].key(value[name])) for name in key_fields)
    return ValueProtocol(normalize, key, lambda value: False)


def sum_fact(cases: dict):
    variants = dict(cases)
    def normalize(value):
        data = _data(value)
        variant = data.get("variant")
        if type(variant) is not str or variant not in variants:
            raise TypeError("RULE_INPUT")
        protocol = variants[variant]
        if set(data) != ({"variant"} if protocol is None else {"variant", "payload"}):
            raise TypeError("RULE_INPUT")
        entries = (("variant", variant),) if protocol is None else (("variant", variant), ("payload", protocol.normalize(data["payload"])))
        return _Fact(entries)
    def key(value):
        variant = value["variant"]
        protocol = variants[variant]
        return part("sum") + part(variant) + (part("no-payload") if protocol is None else part(protocol.key(value["payload"])))
    return ValueProtocol(normalize, key, lambda value: False)


def named_sum_fact(selector: str, payload):
    return ValueProtocol(payload.normalize, lambda value: part(selector) + part(payload.key(value)), lambda value: False)


def optional_fact(element):
    def key(value):
        return part("absent") if value is None else part("present") + part(element.key(value))
    return ValueProtocol(optional_value(element).normalize, key, lambda value: False)


def sequence_fact(element, unique: bool):
    def key(values):
        return part("set" if unique else "list") + part(str(len(values))) + "".join(part(element.key(value)) for value in values)
    return ValueProtocol(sequence_value(element, unique).normalize, key, lambda value: False)
`;
}
