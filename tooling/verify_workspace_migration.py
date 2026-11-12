#!/usr/bin/env python3
"""Verify canonical ownership and selected runtime contracts without repository aliases."""
import hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AREAS={"product","project","work","authority","ontology","architecture","implementation","docs"}
def need(ok,message):
 if not ok:raise ValueError(message)
def check(root=ROOT):
 # Historical move journals include deliberately retired imports and Python adapters.
 # Verify the selected current ownership model rather than demanding their resurrection.
 if (root/".git").exists():
  tracked=subprocess.check_output(["git","-C",str(root),"ls-files","-s","-z"])
  need(not any(entry.startswith(b"120000 ") for entry in tracked.split(b"\0") if entry),"tracked repository symlink")
 current_selection=root/"implementation/lab-workspaces/CURRENT.json"
 need(current_selection.is_file(),"workspace-selection-missing")
 for alias in ("craft","define","website","ontology-lifecycle"):
  need(not (root/alias).exists() and not (root/alias).is_symlink(),"retired root alias: "+alias)
 products=list((root/"workspaces/products").iterdir())
 for home in products:
  if not home.is_dir():continue
  physical={p.name for p in home.iterdir() if p.is_dir() and not p.is_symlink()}
  need(physical==AREAS,"nonstandard physical areas: "+str(home)+": "+str(physical^AREAS))
 need(not (root/"implementation/define-cli").exists() and not (root/"implementation/define-cli").is_symlink(),"Define source left in shared implementation")
 need(not (root/"implementation/bindings").exists() and not (root/"implementation/bindings").is_symlink(),"Ontology bindings left in shared implementation")
 for p in (root/"implementation").iterdir():
  if p.is_dir() and not p.is_symlink():
   need(p.name.startswith("lab-") or p.name in {"bindings","artifact-runtime"},"non-shared Lab implementation: "+p.name)
 need(not (root/"workspaces/products/lab-website/implementation/site/.venv").exists() and not (root/"workspaces/products/lab-website/implementation/site/.venv").is_symlink(),"website environment copied")
 craft=root/"workspaces/products/craft/implementation"
 for rel in ["node_modules","cli/node_modules","alchlang/node_modules","profiles/ai/node_modules","test-derivation-engine/node_modules"]:
  modules=craft/rel
  if not modules.exists():continue
  for base,dirs,files in os.walk(modules,followlinks=False):
   dirs[:]=[d for d in dirs if d not in {".vite",".cache"}]  # Generated test metadata is not an installed dependency copy.
   for name in files:need((Path(base)/name).is_symlink(),"copied dependency file: "+str(Path(base)/name))
 spec=importlib.util.spec_from_file_location("current_workspaces",root/"implementation/lab-workspaces/v2/workspaces.py")
 w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
 model=w.verify_layout(root)
 current=json.loads((root/"implementation/lab-workspaces/CURRENT.json").read_text())
 body=root/"ontology/lab-workspace/v2/definition.json"
 need(hashlib.sha256(body.read_bytes()).hexdigest()==current["definition_sha256"],"definition selection drift")
 selected=json.loads(body.read_text());prepared=root/"docs/migration-plans/0009-complete-workspace-migration-20261108/define/materialized/definitions/000/definition.json"
 need(prepared.read_bytes()==body.read_bytes(),"Define materialization differs from current meaning")
 result={"status":"pass","ownership_basis":"selected-current-workspaces-and-admitted-registry","product_homes":len(products),"uniform_areas":sorted(AREAS),
         "shared_runtime_targets":model["shared_runtime_targets"],"runtime_copies":0,"runtime_model":model["model_version"],"authority_effect":"none"}
 return result
if __name__=="__main__":print(json.dumps(check(),indent=2))
