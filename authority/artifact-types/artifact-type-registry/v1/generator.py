#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parents[3]/"tooling/generators/artifact_surface.py"
spec=importlib.util.spec_from_file_location("g",SHARED); g=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(g)
if __name__=="__main__":
 a=json.loads((ROOT/"artifact.json").read_text()); (ROOT/"ARTIFACT.md").write_text(g.render_artifact(a)); d=json.loads((ROOT/a["validation_contract"]["positive_witness"]).read_text()); (ROOT/a["validation_contract"]["positive_projection"]).write_text(g.render_instance(a,d))
