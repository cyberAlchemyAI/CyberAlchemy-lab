"""Container-side exact-byte one-shot release of the reviewed Reader tool."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

TOOL = Path(__file__).resolve().parent
READER_ONCE_SHA = '307bbf71e131bf6df91a328d3e6f4855defda7fb8a8633882af39549ce24ec53'
SELECTION_SHA = 'a5fea0a94c27900c4975d11924c7ba0abcb7e118d8795c721e5a6c9cefc4cab7'
STAGE_PLAN_SHA = 'a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b'


class Refused(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def basis():
    for name, digest in (('reader_once.py', READER_ONCE_SHA),
                         ('selection.json', SELECTION_SHA),
                         ('stage-plan.json', STAGE_PLAN_SHA)):
        path = TOOL / name
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes()) != digest:
            raise Refused('READER_TOOL_PIN_DRIFT')
    spec = importlib.util.spec_from_file_location('cal_reviewed_reader_once',
                                                   TOOL / 'reader_once.py')
    if spec is None or spec.loader is None:
        raise Refused('READER_TOOL_IMPORT')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.EFFECT_ENABLED is not False:
        raise Refused('READER_TOOL_EFFECT_DRIFT')
    return module


def execute():
    module = basis()
    module.EFFECT_ENABLED = True
    try:
        return module.run()
    finally:
        module.EFFECT_ENABLED = False


if __name__ == '__main__':
    if sys.argv[1:] != ['--execute-reviewed-one-shot']:
        raise SystemExit('reviewed one-shot flag required')
    print(json.dumps(execute(), sort_keys=True))
