"""Candidate complete body decoding; does not establish ownership or admission."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator, ValidationError, validators

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
TIMESTAMP_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
ECMA_WHITESPACE = frozenset([9, 10, 11, 12, 13, 32, 160, 5760,
                           *range(8192, 8203), 8232, 8233, 8239, 8287, 12288, 65279])


class Refused(ValueError):
    def __init__(self, code: str, detail: Any = None):
        self.code, self.detail = code, detail
        super().__init__(code)


@dataclass(frozen=True)
class LocalLimits:
    max_bytes: int = 200000
    max_depth: int = 64
    max_numeric_characters: int = 128
    max_mantissa_digits: int = 96
    max_exponent_digits: int = 6
    max_exponent_magnitude: int = 256


def check_limits(limits: LocalLimits):
    if any(type(value) is not int or value < 0 for value in vars(limits).values()):
        raise Refused('invalid-limits')


def parse_body(raw: bytes, limits: LocalLimits) -> dict[str, Any]:
    check_limits(limits)
    if len(raw) > limits.max_bytes:
        raise Refused('byte-budget', {'actual': len(raw), 'maximum': limits.max_bytes})
    try:
        text = raw.decode('utf-8', errors='strict')
    except UnicodeDecodeError as error:
        raise Refused('utf8', {'byte_offset': error.start}) from error
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '{[':
            depth += 1
            if depth > limits.max_depth:
                raise Refused('depth-budget', {'maximum': limits.max_depth})
        elif char in '}]':
            depth -= 1

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Refused('duplicate-member', {'member': key})
            result[key] = value
        return result

    def numeric(token):
        mantissa, _, exponent = token.lower().partition('e')
        digits = exponent.lstrip('+-')
        if (len(token) > limits.max_numeric_characters or
                sum(char.isdigit() for char in mantissa) > limits.max_mantissa_digits or
                len(digits) > limits.max_exponent_digits):
            raise Refused('numeric-budget')
        if digits and int(digits) > limits.max_exponent_magnitude:
            raise Refused('numeric-budget')
        return Decimal(token)

    def constant(token):
        raise Refused('non-json-constant', {'token': token})

    try:
        body = json.loads(text, object_pairs_hook=pairs, parse_int=numeric,
                          parse_float=numeric, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise Refused('json', {'character_offset': error.pos,
                               'line': error.lineno, 'column': error.colno}) from error
    except RecursionError as error:
        raise Refused('parser-resource') from error

    def check_scalars(value):
        if isinstance(value, str):
            if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
                raise Refused('unsupported-surrogate')
        elif isinstance(value, dict):
            for key, child in value.items():
                check_scalars(key)
                check_scalars(child)
        elif isinstance(value, list):
            for child in value:
                check_scalars(child)

    check_scalars(body)
    if not isinstance(body, dict):
        raise Refused('object-required')
    return body


def read_bound(binding):
    path = ROOT / binding['path']
    try:
        raw = path.read_bytes()
    except FileNotFoundError as error:
        raise Refused('missing-profile-source', {'path': binding['path']}) from error
    if hashlib.sha256(raw).hexdigest() != binding['sha256']:
        raise Refused('changed-profile-source', {'path': binding['path']})
    return json.loads(raw)


def schema_refs(schema):
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == '$ref':
                yield value
            else:
                yield from schema_refs(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from schema_refs(value)


def schema_patterns(schema):
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == 'pattern':
                yield value
            else:
                yield from schema_patterns(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from schema_patterns(value)


def pattern_matches(pattern: str, value: str) -> bool:
    if pattern == r'\S':
        return any(ord(char) not in ECMA_WHITESPACE for char in value)
    if pattern == TIMESTAMP_PATTERN:
        if len(value) != 20:
            return False
        separators = {4: '-', 7: '-', 10: 'T', 13: ':', 16: ':', 19: 'Z'}
        return all(char == separators[index] if index in separators else '0' <= char <= '9'
                   for index, char in enumerate(value))
    raise Refused('unsupported-pattern', {'pattern': pattern})


def exact_pattern(validator, pattern, instance, schema):
    if validator.is_type(instance, 'string') and not pattern_matches(pattern, instance):
        yield ValidationError('String does not match the pinned ECMAScript pattern.')


CompleteSchemaValidator = validators.extend(Draft202012Validator, {'pattern': exact_pattern})


@dataclass(frozen=True)
class DecodedBody:
    kind: str
    schema_ref: str
    schema_digest: str
    body_digest: str
    identity_token: str
    original_bytes: bytes
    limits: LocalLimits

    @property
    def body(self):
        # A fresh full value prevents callers mutating a previously returned body.
        return parse_body(self.original_bytes, self.limits)


class CandidateBodyProvider:
    def __init__(self):
        self._manifest_bytes = (HERE / 'profile-manifest.json').read_bytes()

    @property
    def profiles(self):
        return {row['kind']: row for row in json.loads(self._manifest_bytes)['profiles']}

    def decode(self, kind: str, raw: bytes, expected_digest: str,
               limits: LocalLimits = LocalLimits()) -> DecodedBody:
        check_limits(limits)
        if not isinstance(raw, bytes):
            raise Refused('invalid-byte-input')
        if not isinstance(kind, str) or kind not in self.profiles:
            raise Refused('unsupported-kind', {'kind': kind})
        if len(raw) > limits.max_bytes:
            raise Refused('byte-budget', {'actual': len(raw), 'maximum': limits.max_bytes})
        if not isinstance(expected_digest, str) or not re.fullmatch('[0-9a-f]{64}', expected_digest):
            raise Refused('digest-format')
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected_digest:
            raise Refused('digest-mismatch')
        row = self.profiles[kind]
        artifact, schema = read_bound(row['artifact']), read_bound(row['schema'])
        if (artifact['schema_digest'] != row['schema']['sha256'] or
                artifact['schema_ref'] != row['schema_ref'] or
                artifact['artifact_type_ref'] != row['artifact_type_ref'] or
                artifact['instance_contract']['identity_field'] != row['identity_field'] or
                artifact['status'] != row['source_status']):
            raise Refused('profile-contract-mismatch')
        if any(not ref.startswith('#/') for ref in schema_refs(schema)):
            raise Refused('external-schema-reference')
        if set(schema_patterns(schema)) - {r'\S', TIMESTAMP_PATTERN}:
            raise Refused('unsupported-pattern')
        Draft202012Validator.check_schema(schema)
        body = parse_body(raw, limits)
        errors = sorted(CompleteSchemaValidator(schema).iter_errors(body),
                        key=lambda error: (tuple(map(str, error.absolute_path)), error.message))
        if errors:
            raise Refused('schema', [{'instance_path': list(error.absolute_path),
                                     'schema_path': list(error.absolute_schema_path),
                                     'keyword': error.validator, 'cause': error.message}
                                    for error in errors])
        return DecodedBody(kind, row['schema_ref'], row['schema']['sha256'], digest,
                           body[row['identity_field']], raw, limits)
