#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json
ROOT=Path(__file__).resolve().parent
SHARED=ROOT.parents[3]/'tooling/generators/endpoint_carrier.py'
spec=importlib.util.spec_from_file_location('endpoint_carrier_generator',SHARED); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
if __name__=='__main__':
 a=json.loads((ROOT/'artifact.json').read_text()); w=ROOT/a['validation_contract']['positive_witness']; d=json.loads(w.read_text()); (ROOT/'ARTIFACT.md').write_text(mod.render_artifact(a)); (ROOT/a['validation_contract']['positive_projection']).write_text(mod.render_instance(a,d))
