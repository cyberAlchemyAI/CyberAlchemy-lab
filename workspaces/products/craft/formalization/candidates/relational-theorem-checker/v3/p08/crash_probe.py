"""Actual owned metadata-process crash; no theorem qualification is claimed."""
from pathlib import Path
import os
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import BASE,C
from v3.p08.metadata import Store
store=Store(Path(sys.argv[1]));stage=sys.argv[2]
request=C.decode((BASE/'p01/request-fixture.json').read_bytes())
def fault(at):
    if at==stage:os._exit(91)
store.probe(request['proposal']['after'],fault=fault)
raise SystemExit('requested crash phase was never reached')
