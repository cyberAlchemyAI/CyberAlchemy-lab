"""Versioned signing bytes shared with the independent Rust vectors.

Legacy metadata is hashed as original bytes; it must never pass through this
codec to manufacture a replacement identity. Integers use the signed i64 range.
"""
import hashlib
import json

MIN_INTEGER = -(2 ** 63)
MAX_INTEGER = 2 ** 63 - 1
MAX_FRAME = 65536


class Refusal(ValueError):
    """Only a bounded public diagnostic code; never include input values."""


def need(condition, code):
    if not condition:
        raise Refusal(code)


def closed(value, fields):
    need(type(value) is dict and set(value) == set(fields), 'CLOSED_FIELDS')


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def _bad_number(_):
    raise Refusal('NON_INTEGER_NUMBER')


def _integer(token):
    need(token != '-0', 'NEGATIVE_ZERO')
    return int(token)


def _check(value, depth=0):
    need(depth <= 64, 'JSON_DEPTH')
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        need(MIN_INTEGER <= value <= MAX_INTEGER, 'INTEGER_RANGE')
        return
    if type(value) is str:
        need(not any(0xD800 <= ord(c) <= 0xDFFF for c in value), 'UNICODE_SCALAR')
        return
    if type(value) is list:
        for child in value:
            _check(child, depth + 1)
        return
    need(type(value) is dict, 'JSON_TYPE')
    for key, child in value.items():
        need(type(key) is str, 'OBJECT_KEY')
        _check(key, depth + 1)
        _check(child, depth + 1)


def parse(raw, max_bytes=MAX_FRAME):
    need(type(max_bytes) is int and 0 < max_bytes <= 64 * 1024 * 1024, 'PARSE_LIMIT')
    need(type(raw) is bytes and len(raw) <= max_bytes, 'JSON_BYTES_LIMIT')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                           parse_int=_integer, parse_float=_bad_number, parse_constant=_bad_number)
        _check(value)
        return value
    except Refusal:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise Refusal('INVALID_JSON') from None


def canonical(value):
    _check(value)
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def signing_bytes(value):
    need(type(value) is dict and type(value.get('schema_version')) is str
         and bool(value['schema_version']), 'SIGNING_DOMAIN')
    return canonical(value)


def sha(raw):
    need(type(raw) is bytes, 'HASH_BYTES')
    return hashlib.sha256(raw).hexdigest()
