/** Event carriers have their own checked contract, distinct from Rule UInt64. */
export function renderPythonEventValues(): string {
  return `from math import isfinite as _isfinite
from re import compile as _compile

_INTEGER = _compile(r"(?:0|-?[1-9][0-9]*)\\Z")

def fail():
    raise TypeError("EVENT_INPUT")

def data(value, allowed, required):
    if type(value) is not dict or any(type(key) is not str for key in value):
        return fail()
    if any(key not in allowed for key in value) or any(key not in value for key in required):
        return fail()
    return value

def string(value):
    if type(value) is not str:
        return fail()
    return value

def text(value):
    if type(value) is not str or not value:
        return fail()
    return value

def boolean(value):
    if type(value) is not bool:
        return fail()
    return value

def integer(value):
    if type(value) is int:
        number = value
    elif type(value) is str and len(value) <= 20 and _INTEGER.fullmatch(value):
        number = int(value)
    else:
        return fail()
    if number < -9223372036854775808 or number > 9223372036854775807:
        return fail()
    return number

def decimal(value):
    if type(value) is not int and type(value) is not float:
        return fail()
    try:
        number = float(value)
    except OverflowError:
        return fail()
    if not _isfinite(number):
        return fail()
    return 0.0 if number == 0 else number
`;
}
