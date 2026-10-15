#!/usr/bin/env python3
"""Prepare one independently pinned repaired source; no research comparisons or authority effects."""
import importlib.util
from pathlib import Path
import sys
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'workflows'))
import research

if __name__ == '__main__':
    p, destination, pin = Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
    research.require(p.is_file() and not p.is_symlink() and research.byte_sha(p.read_bytes()) == pin, 'independent repaired source pin differs')
    spec = importlib.util.spec_from_file_location('W06_later_preparation',p)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result = {'controlled':True,'source_sha256':pin,'preparation_posture':'unknown','validated_records':0,'error':None}
    try:
        module.prepare(destination)
        _, records, _ = research.resolve(destination,research.byte_sha((destination/'selection.json').read_bytes()))
        result.update(preparation_posture='completed',validated_records=len(records),selection_sha256=research.byte_sha((destination/'selection.json').read_bytes()))
    except Exception:
        result.update(preparation_posture='rejected',error=traceback.format_exc())
    research.require(research.byte_sha(p.read_bytes()) == pin,'repaired source changed during probe')
    sys.stdout.buffer.write(research.encoded(result))
