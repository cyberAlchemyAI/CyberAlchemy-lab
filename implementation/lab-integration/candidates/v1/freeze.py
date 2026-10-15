#!/usr/bin/env python3
"""Freeze source bytes and inventory before regression; existing packages are immutable."""
import argparse,json,os,subprocess,sys
from pathlib import Path
from inventory_manifest import *

parser=argparse.ArgumentParser();parser.add_argument('native_executable');args=parser.parse_args()
directory=PACKAGE/'packages';directory.mkdir(exist_ok=True);index=1
while (directory/f'{index:04d}').exists():index+=1
stage=directory/f'{index:04d}';stage.mkdir()
manifest={'schema_version':'lab-successor-integration-manifest/v1-candidate','authority_effect':'none','files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(read(p))} for p in selected_files()], 'groups':groups(),'native_executable_sha256':sha(read(args.native_executable)),'candidate_scope':'Complete declared C09 successor regression and joined isolated inspection; no generic API, ontology domain adapter, real Work satisfaction or owner admission.','actual_owner_outcome':None,'frozen_source_policy':'Original v1/v2, all current component source/profile bytes and numbered staged inputs remain unchanged.'}
path=stage/'manifest.json';path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');pin=sha(read(path))
inventory=[]
env={**os.environ,'LAB_C08_NATIVE_EXECUTABLE':str(Path(args.native_executable).resolve()),'LAB_C08_GENERATOR_MANIFEST':'implementation/lab-context/candidates/v1/packages/0004/generator-manifest.json','C09_MANIFEST_PATH':str(path),'C09_MANIFEST_SHA256':pin}
for group in groups():
    output=stage/(group['id']+'.inventory.json')
    result=subprocess.run([sys.executable,str(PACKAGE/'worker.py'),group['id'],str(output),'--inventory'],capture_output=True,text=True,env=env,timeout=30)
    if result.returncode:raise RuntimeError(result.stderr)
    data=load(output);inventory.append({'group':group['id'],'path':output.relative_to(ROOT).as_posix(),'sha256':sha(read(output)),'test_ids':data['test_ids'],'count':data['count']})
selection={'schema_version':'lab-C09-selection/v1-candidate','authority_effect':'none','manifest_path':path.relative_to(ROOT).as_posix(),'manifest_sha256':pin,'regression_inventory':inventory,'total_cases':sum(r['count'] for r in inventory),'actual_owner_outcome':None}
sp=stage/'selection.json';sp.write_text(json.dumps(selection,indent=2,sort_keys=True)+'\n')
validate_manifest(path,pin)
print(json.dumps({'package':stage.relative_to(ROOT).as_posix(),'selection_sha256':sha(read(sp)),'source_files':len(manifest['files']),'cases':selection['total_cases']}))
