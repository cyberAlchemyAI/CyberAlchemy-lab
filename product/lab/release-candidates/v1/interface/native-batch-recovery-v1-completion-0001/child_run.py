"""Exact owned child for process interruption conformance; no live dispatch."""
from dataclasses import asdict
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from recoverable_store import GenerationStore,PendingPins,write

value=json.loads(Path(sys.argv[1]).read_bytes())
store=GenerationStore(value['root'],value['identity'],value['executable'],value['executable_sha256'])
observer=None;checkpoint=None
if value['kind']=='native':
    observer={'CAL_T32_STOP_STAGE':value['stage'],'CAL_T32_STOP_FAMILY':value['family'],'CAL_T32_MARKER':value['marker']}
else:
    def checkpoint(stage):
        if stage!=value['stage']:return
        write(Path(value['marker']),stage.encode())
        while True:time.sleep(1)
store.run(value['pending'],PendingPins(**value['pins']),native_observer_env=observer,checkpoint=checkpoint)
