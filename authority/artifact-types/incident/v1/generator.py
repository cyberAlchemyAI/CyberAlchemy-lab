#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json
R=Path(__file__).resolve().parent;S=R.parents[3]/'tooling/generators/endpoint_carrier.py'
s=importlib.util.spec_from_file_location('g',S);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=json.loads((R/'artifact.json').read_text());w=json.loads((R/a['validation_contract']['positive_witness']).read_text());(R/'ARTIFACT.md').write_text(m.render_artifact(a));(R/a['validation_contract']['positive_projection']).write_text(m.render_instance(a,w))
