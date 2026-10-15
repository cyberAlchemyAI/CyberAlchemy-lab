"""Independent task-local/source and stable installation entry/exit verification."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import provisioning as P
import checks

HERE=Path(__file__).resolve().parent
DEPENDENCIES=P.ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'
SELECTION=P.ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
SELECTION_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'

def main(manifest_sha,report_name,manifest_name='source-manifest.json',qualification_name='qualification-0001.json'):
    P.require(Path(manifest_name).name==manifest_name,'flat manifest selector required')
    manifest_path=HERE/manifest_name;raw=manifest_path.read_bytes();P.require(P.sha(raw)==manifest_sha,'independent task-local manifest differs')
    manifest=P.parse(raw)
    def source_guard():
        P.require(manifest_path.read_bytes()==raw,'task-local manifest changed')
        for row in manifest['files']:
            path=P.ROOT/row['path'];P.require(path.is_file() and not any(p.is_symlink() for p in [path,*path.parents]) and P.sha(path.read_bytes())==row['sha256'],'task-local exact source changed')
    source_guard();sys.path.insert(0,str(DEPENDENCIES));import closure_hardened_0003 as dependencies
    selected,_=dependencies.load_selection(SELECTION,SELECTION_SHA)
    before=dependencies.verify_installed(checks.INSTALL,selected)
    checks.checks(report_name)
    after=dependencies.verify_installed(checks.INSTALL,selected);source_guard()
    result={'schema_version':'lab-T34-qualified-focused-run/v1-candidate','result':'PASS','source_manifest_sha256':manifest_sha,'source_files':len(manifest['files']),'T07_selection_sha256':SELECTION_SHA,'installation_entry':before,'installation_exit':after,'report_sha256':P.sha((checks.RUN/report_name).read_bytes()),'authority_effect':'none','task_complete':False,'full_API17_source_guard_claimed':False,'full_shared_runtime_startup_claimed':False}
    output=checks.RUN/qualification_name;checks.write(output,json.dumps(result,sort_keys=True,indent=2).encode()+b'\n');print(json.dumps({'qualification':str(output),'result':'PASS'}))

if __name__=='__main__':main(*sys.argv[1:])
