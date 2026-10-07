#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent; SHARED=ROOT.parents[3]/'tooling/generators/artifact_type_successor.py'
s=importlib.util.spec_from_file_location('g',SHARED);m=importlib.util.module_from_spec(s);assert s and s.loader;s.loader.exec_module(m)
if __name__=='__main__':
 a=json.loads((ROOT/'artifact.json').read_text());p=ROOT/a['validation_contract']['positive_witness'];d=json.loads(p.read_text());(ROOT/'ARTIFACT.md').write_text(m.render_artifact(a));(ROOT/a['validation_contract']['positive_projection']).write_text(m.render_instance(a,d))
