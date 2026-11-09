#!/usr/bin/env python3
"""Verify canonical ownership, source-preserving links and selected runtime contracts."""
import hashlib,importlib.util,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AREAS={"product","project","work","authority","ontology","architecture","implementation","docs"}
def need(ok,message):
 if not ok:raise ValueError(message)
def check(root=ROOT):
 journal=json.loads((root/"docs/migration-plans/0009-complete-workspace-migration-20261108/JOURNAL.json").read_text())
 for row in journal["moves"]:
  old,new=root/row["source"],root/row["destination"]
  need(old.is_symlink() and old.resolve()==new.resolve(),"compatibility alias: "+row["source"])
  need(new.exists() and not new.is_symlink(),"canonical owner: "+row["destination"])
 products=list((root/"workspaces/products").iterdir())
 for home in products:
  if not home.is_dir():continue
  physical={p.name for p in home.iterdir() if p.is_dir() and not p.is_symlink()}
  need(physical==AREAS,"nonstandard physical areas: "+str(home)+": "+str(physical^AREAS))
 for name in ["define-cli"]:
  need((root/"implementation"/name).is_symlink(),"product source left in shared implementation: "+name)
 for p in (root/"implementation/bindings").iterdir():
  need(p.is_symlink() and p.resolve().is_relative_to(root/"workspaces/products/ontology"),"product binding outside owner")
 for p in (root/"implementation").iterdir():
  if p.is_dir() and not p.is_symlink():
   need(p.name.startswith("lab-") or p.name=="bindings","non-shared Lab implementation: "+p.name)
 need((root/"workspaces/products/lab-website/implementation/site/.venv").is_symlink(),"website environment copied")
 need((root/"workspaces/products/lab-website/implementation/site/.venv").resolve().is_relative_to(root/".local/shared-environments"),"website shared environment selection")
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
 result={"status":"pass","ownership_moves":len(journal["moves"]),"product_homes":len(products),"uniform_areas":sorted(AREAS),
         "shared_runtime_targets":model["shared_runtime_targets"],"runtime_copies":0,"runtime_model":model["model_version"],"authority_effect":"none"}
 return result
if __name__=="__main__":print(json.dumps(check(),indent=2))
