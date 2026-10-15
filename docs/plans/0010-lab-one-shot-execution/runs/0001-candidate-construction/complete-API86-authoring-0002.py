"""Preserve the first final-audit error and finish the unfrozen candidate."""
import ast
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD,API=BASE/'api-v85',BASE/'api-v86'


def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')


def main():
    assert API.exists() and not (API/'source-manifest.json').exists(),'only unfrozen authoring is repaired'
    changed=[]
    for path in API.rglob('*.py'):
        ast.parse(path.read_text());old=OLD/path.relative_to(API)
        if old.exists() and 'self.assertEqual(len(SUPPORTED),23)' in old.read_text():
            assert path.read_text()==old.read_text().replace('self.assertEqual(len(SUPPORTED),23)','self.assertEqual(len(SUPPORTED),24)')
            changed.append(path.relative_to(API).as_posix())
    assert set(changed)=={'run_session_checks.py','test_current_controls.py','test_custody_sessions.py'}
    emit(RUN/'API86-authoring-attempt-0001.json',{
        'schema_version':'lab-preserved-authoring-attempt/v1-candidate','result':'FAIL',
        'reason':'Final authoring audit expected two count revisions; there are three including the original run_session_checks.py test driver.',
        'producer_binding':binding(RUN/'author-API86-challenge-resolution-0001.py'),
        'candidate_files_at_failure':[binding(path) for path in sorted(API.rglob('*')) if path.is_file()],
        'runtime_qualified':False,'authority_effect':'none'})
    path=API/'service.py';text=path.read_text()
    old="'handler_binding':binding(str((HERE/'challenge_submission.py').relative_to(ROOT))"
    new="'handler_binding':binding(str((HERE.parent/'challenge-resolution-v1/preparation.py').relative_to(ROOT)),(HERE.parent/'challenge-resolution-v1/preparation.py').read_bytes()) if call['operation']=='challenge.resolve' else binding(str((HERE/'challenge_submission.py').relative_to(ROOT))"
    assert text.count(old)==1;path.write_text(text.replace(old,new,1));ast.parse(path.read_text())
    emit(RUN/'API86-authoring-completion-0002.json',{
        'schema_version':'lab-preserved-authoring-completion/v1-candidate','result':'AUTHORED',
        'preserved_attempt_binding':binding(RUN/'API86-authoring-attempt-0001.json'),
        'producer_binding':binding(Path(__file__).resolve()),'authored_handlers':24,'remaining_handlers':10,
        'explicit_registry_count_revisions':sorted(changed),'exact_resolution_method_reply_binding':True,
        'runtime_qualified':False,'task_complete':False,'authority_effect':'none'})
    print(json.dumps({'result':'AUTHORED','authored_handlers':24,'remaining_handlers':10,
                      'explicit_registry_count_revisions':sorted(changed),'runtime_qualified':False}),flush=True)


if __name__=='__main__':main()
