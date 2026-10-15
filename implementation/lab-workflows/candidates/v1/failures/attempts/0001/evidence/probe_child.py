#!/usr/bin/env python3
"""Fresh controlled source replay; catches preparation outcome, not interpretation."""
import importlib.util
from pathlib import Path
import sys
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'workflows'))
import research

if __name__ == '__main__':
    source, output, pin = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    research.require(research.byte_sha(source.read_bytes()) == pin, 'independent source pin differs')
    spec = importlib.util.spec_from_file_location('W05_selected_builder', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {'controlled': True, 'source_sha256': pin, 'preparation_posture': 'unknown',
        'validated_records': 0, 'exception_type': None, 'exception_message': None, 'traceback': None}
    try:
        module.prepare(output)
        selection, records, procedure = research.resolve(output, research.byte_sha((output/'selection.json').read_bytes()))
        result.update(preparation_posture='completed', validated_records=len(records), selection_sha256=research.byte_sha((output/'selection.json').read_bytes()))
    except Exception as exc:
        result.update(preparation_posture='rejected', exception_type=type(exc).__name__,
            exception_message=str(exc), traceback=traceback.format_exc())
    research.require(research.byte_sha(source.read_bytes()) == pin, 'source changed during preparation')
    sys.stdout.buffer.write(research.encoded(result))
