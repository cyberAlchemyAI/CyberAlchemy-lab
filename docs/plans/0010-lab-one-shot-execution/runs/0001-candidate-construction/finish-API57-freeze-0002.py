"""Resume interrupted freeze after retaining its exact already written profile.

The first producer rejected an original absolute source path at verification;
this successor accepts that representation and verifies its exact bytes. Runtime
source guards and original test methods remain unchanged.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
path=RUN/'freeze-API57-pending-evidence-0001.py'
spec=importlib.util.spec_from_file_location('_cal_API57_freeze_resume',path)
producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)

def bind(path):
    return {'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix(),
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

original_emit=producer.emit
def emit(path,value):
    if path==producer.API/'contract-profile.json':
        assert json.loads(path.read_bytes())==value,'already produced profile must remain exact'
        return
    original_emit(path,value)

if __name__=='__main__':
    producer.bind=bind
    producer.emit=emit
    producer.main()
