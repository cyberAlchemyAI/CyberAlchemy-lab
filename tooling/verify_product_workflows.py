#!/usr/bin/env python3
"""Portable source verification using the selected shared environment."""
import argparse,importlib.util,json,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def define_api():
 source=ROOT/"workspaces/products/define/implementation/cli/standalone"
 sys.path[:0]=[str(source),str(source/"tests")]
 suite=unittest.TestSuite([unittest.defaultTestLoader.discover(str(source/"tests"),pattern=p) for p in ["test_api.py","test_adapter_and_bounds.py"]])
 return not unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful()
def website():
 site=ROOT/"workspaces/products/lab-website/implementation/site"
 with tempfile.TemporaryDirectory(prefix="lab-site-render-") as temporary:
  out=Path(temporary);stage=out/"source";logs=out/"logs";logs.mkdir()
  shutil.copytree(site/"source",stage,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
  shutil.copy2(site/"hackathon.json",stage/"governance-lab-series/hackathon.json")
  spec=importlib.util.spec_from_file_location("selected_site_build",site/"build.py")
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  module.render(stage,logs);files=module.select_files(stage)
  print(json.dumps({"rendered_resource_files":len(files),"deployment":False,"runtime_installations_created":0}))
 return 0
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("workflow",choices=["define-api","website-render"]);args=p.parse_args()
 raise SystemExit(define_api() if args.workflow=="define-api" else website())
