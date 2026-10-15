"""Freeze exact adapter inputs without mutating any selected predecessor."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    source=HERE.parent/'current-participation-v2'
    proof=RUN/'current-participation-audit-proof-0001.json'
    rows={r['path']:r for r in json.loads(proof.read_bytes())['files']}
    for row in rows.values():
        if bind(ROOT/row['path'])!=row:raise ValueError('selected predecessor changed '+row['path'])
    selected=[proof,source/'source-manifest.json',source/'packages/0001/manifest.json',RUN/'authorization.json',RUN/'ONE-APPROVAL-BOUNDARIES.md',*(HERE.glob('*.py'))]
    context={'schema_version':'lab-task-context/v1-candidate','task_ref':'R03/new-current-source-adapter','strict_coverage':'PASS','source_bindings':[bind(p) for p in selected],
        'obligations':[{'id':item,'status':'covered'} for item in ['exact-independent-source-package-adapter-pins','all23-original-bodies','same-cut-current-participation','schema-and-source-mutation-refusals','no-private-memory','closed-reader-denial','original-episode-preserved','no-authority-or-Agent-inference']],
        'constraints':['Candidate implementation and owned read-only cold fixtures only.','No actual owner response, host permission, live Agent, Session memory restoration or admission.','Freeze all source before owned replay and retain all outcomes.'],
        'write_scope':[HERE.relative_to(ROOT).as_posix(),RUN.relative_to(ROOT).as_posix(),'new owned temporary cold fixtures'],
        'validation':'Full15 adapter checks, followed by independent original-body/same-cut audit before downstream mapping.',
        'blockers':[],'authority_effect':'none','actual_owner_outcome':None,'goal_complete':False}
    context_path=RUN/'context-R03-current-source-adapter-0001.json';emit(context_path,context)
    for path in [*selected,context_path]:rows[bind(path)['path']]=bind(path)
    manifest={'schema_version':'lab-current-source-adapter-source/v1-candidate','context_binding':bind(context_path),'producer_source_binding':bind(source/'source-manifest.json'),'producer_package_binding':bind(source/'packages/0001/manifest.json'),
        'files':[rows[k] for k in sorted(rows)],'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},
        'expected_tests':15,'authority_effect':'none','actual_owner_outcome':None,'current_Agent_qualified':False}
    path=HERE/'source-manifest.json';emit(path,manifest)
    print(json.dumps({'source_binding':bind(path),'files':len(rows),'expected_tests':15}),flush=True)
if __name__=='__main__':main()
