#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[5]; P=LAB/"tooling/generators/artifact_surface.py"
spec=importlib.util.spec_from_file_location("generator",P); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
load=lambda p: json.loads(p.read_text())
if __name__=="__main__":
 (ROOT/"ARTIFACT.md").write_text(module.render_artifact(load(ROOT/"artifact.json")))
 (ROOT/"fixtures/valid/MIGRATION.md").write_text(module.render_instance(load(ROOT/"artifact.json"),load(ROOT/"fixtures/valid/migration.json")))
