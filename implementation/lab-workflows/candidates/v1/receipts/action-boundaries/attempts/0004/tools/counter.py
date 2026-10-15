"""Closed owned local Tool; no arbitrary paths, commands, network or admission."""
from pathlib import Path
import os
import sys

AUTHORITY = Path(__file__).resolve().parents[1] / 'authority'
if str(AUTHORITY) not in sys.path:
    sys.path.insert(0, str(AUTHORITY))
from evaluator import BoundaryFault, byte_sha, encoded, parse, require

INPUT_CONTRACT = {'type': 'object', 'additionalProperties': False,
                  'properties': {'increment': {'type': 'integer', 'minimum': 1, 'maximum': 10}},
                  'required': ['increment']}
OUTPUT_CONTRACT = {'type': 'object', 'additionalProperties': False,
                   'properties': {'value': {'type': 'integer', 'minimum': 0},
                                  'action_id': {'type': 'string', 'minLength': 1},
                                  'input_sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}},
                   'required': ['value', 'action_id', 'input_sha256']}


def fsync_directory(root):
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic(path, value):
    temporary = path.with_name(path.name + '.staging')
    require(not temporary.exists() and not temporary.is_symlink(), 'recovery required for staging residue')
    with temporary.open('xb') as stream:
        stream.write(encoded(value)); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)
    fsync_directory(path.parent)


def regular_json(path):
    require(path.is_file() and not path.is_symlink(), 'required operational metadata absent or unsafe')
    return parse(path.read_bytes())


class CounterTool:
    def __init__(self, root):
        self.root = Path(root)
        self.path = self.root / 'counter.json'

    def state(self):
        value = regular_json(self.path)
        require(set(value) == {'value', 'action_id', 'input_sha256'}, 'counter state contract invalid')
        require(type(value['value']) is int and value['value'] >= 0, 'counter value invalid')
        return value

    def execute(self, original, action_id):
        from jsonschema import Draft202012Validator
        payload = parse(original)
        require(Draft202012Validator(INPUT_CONTRACT).is_valid(payload), 'Tool input contract rejected')
        old = self.state()
        new = {'value': old['value'] + payload['increment'], 'action_id': action_id,
               'input_sha256': byte_sha(original)}
        require(Draft202012Validator(OUTPUT_CONTRACT).is_valid(new), 'Tool output contract rejected')
        atomic(self.path, new)
        return new
