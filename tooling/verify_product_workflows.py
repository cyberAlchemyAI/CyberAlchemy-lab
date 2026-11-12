#!/usr/bin/env python3
"""Verify current Define and website workflows without retired source paths."""
import argparse,importlib.util,json,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def define_api():
 node=ROOT.parent/"cyberAlchemy-v2/.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node"
 verifier=ROOT/"workspaces/products/define/implementation/cli/alchlang/verify-cli-workflow.mjs"
 result=subprocess.run([str(node),str(verifier)],cwd=ROOT,text=True,capture_output=True)
 if result.returncode:
  print(result.stderr or result.stdout)
  return 1
 receipt=json.loads(result.stdout)
 if receipt.get("status")!="PASS":
  print(result.stdout)
  return 1
 print(json.dumps({"define_cli":receipt["status"],"checks":receipt["check_count"],"canonical_owner_admission":False}))
 return 0
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
