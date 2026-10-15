"""Assemble actual separately guarded operator branches into one candidate."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-installation-release-v3';NEW=BASE/'api-integration-v10'
PARENT_PIN='8e1570873803fe7603f5a997c7b7fac956485bc73fd0220dc51df8febfd3c876'
MEMBERS={
 'actions':{'directory':'api-action-integration-v2','source_sha256':'d92fee4f26271ee3ffe588ba5d78962ffa02e2c27ff7cd848ef54239aee3753d','profile_sha256':'b3767b2b1ececc73ce24ea7d55924956feab8a5f3b563c3359391122a95b3576','operations':['action.evaluate','action.dispatch','action.reconcile']},
 'governance':{'directory':'api-governance-integration-v4','source_sha256':'ff7c71a891276dbdbf81f3997e79bf3b486611fb13f1cff374e5986e9ce3b415','profile_sha256':'7798fda1f9e7e4038425bc8aa6f227f2e22612affa4acb2c28c9a12d31531af3','operations':['checkpoint.resolve','admission.apply','capability.adoption.prepare']}}
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    assert not NEW.exists()
    spec=importlib.util.spec_from_file_location('_cal_common_parent_guard_0159',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);parent=guard.verify(PARENT_PIN)
    for member in MEMBERS.values():
        folder=BASE/member['directory']
        assert bind(folder/'source-manifest.json')['sha256']==member['source_sha256']
        assert bind(folder/'contract-profile.json')['sha256']==member['profile_sha256']
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','__pycache__'))
    for name in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json'):(NEW/name).unlink()
    p=NEW/'protocol.py';text=p.read_text();tree=ast.parse(text)
    node=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPPORTED' for t in n.targets)][-1]
    lines=text.splitlines(keepends=True);section=''.join(lines[node.lineno-1:node.end_lineno])
    lines[node.lineno-1:node.end_lineno]=[section.rstrip()+"+('action.evaluate','action.dispatch','action.reconcile','checkpoint.resolve','admission.apply','capability.adoption.prepare')\n"]
    p.write_text(''.join(lines))
    # The supported count is a current selector witness. Other inherited test
    # assertions retain their meanings; the documented classification fixture
    # correction already qualified in the parent schema candidate is retained.
    p=NEW/'run_session_checks.py';text=p.read_text()
    old='self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(SUPPORTED),26)'
    assert text.count(old)==1;p.write_text(text.replace(old,'self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(SUPPORTED),34)'))
    shutil.copyfile(BASE/'api-integration-v7/test_classification_api.py',NEW/'test_classification_api.py')
    shutil.copyfile(RUN/'common-dispatch-staging-0159/integration_dispatch.py',NEW/'integration_dispatch.py')
    # Members are host selections. Callers cannot choose implementation paths,
    # source pins, private root identity, nonce scope or governing authority.
    emit(NEW/'integration-members.json',{'schema_version':'lab-common-operator-members/v1-candidate','members':MEMBERS,'authority_effect':'none','actual_owner_outcome':None,'whole_API_qualified':False})
    p=NEW/'jcs.py';text=p.read_text();assert text.count("WHEEL=HERE/'dependencies/rfc8785-0.1.4-py3-none-any.whl'")==1;p.write_text(text.replace("WHEEL=HERE/'dependencies/rfc8785-0.1.4-py3-none-any.whl'","WHEEL=HERE.parent/'api-integration-v6/dependencies/rfc8785-0.1.4-py3-none-any.whl'"))
    for p in NEW.glob('*.py'):ast.parse(p.read_text())
    selection=load(OLD/'SCHEMA-EXECUTION-DEPENDENCIES.json')
    oldprefix=OLD.relative_to(ROOT).as_posix()+'/';newprefix=NEW.relative_to(ROOT).as_posix()+'/'
    rows={};reasons={}
    for row in selection['files']:
        key=newprefix+row['path'][len(oldprefix):] if row['path'].startswith(oldprefix) else row['path']
        rows[key]=bind(ROOT/key);reasons[key]=selection['selection_reasons'][row['path']]
    for p in (NEW/'integration_dispatch.py',NEW/'integration-members.json'):
        row=bind(p);rows[row['path']]=row;reasons[row['path']]=['Actual common unchanged-envelope dispatcher and independent member selections.']
    selection.update(files=[rows[k] for k in sorted(rows)],selection_reasons=reasons,parent_source_binding=bind(OLD/'source-manifest.json'),parent_profile_binding=bind(OLD/'contract-profile.json'))
    emit(NEW/'SCHEMA-EXECUTION-DEPENDENCIES.json',selection)
    profile=load(OLD/'contract-profile.json');fullrows={r['path']:r for r in profile['files']}
    for row in [*rows.values(),bind(NEW/'SCHEMA-EXECUTION-DEPENDENCIES.json')]:fullrows[row['path']]=row
    for member in MEMBERS.values():
        folder=BASE/member['directory']
        for p in sorted(folder.rglob('*')):
            if p.is_file() and not {'receipts','history','__pycache__'}&set(p.relative_to(folder).parts):fullrows[bind(p)['path']]=bind(p)
    operations=profile['implemented_operations']+[op for m in MEMBERS.values() for op in m['operations']]
    assert len(operations)==len(set(operations))==34
    original=[r['operation'] for r in load(ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json')['operations']]
    assert set(operations)==set(original)
    profile.update(implemented_operations=operations,files=[fullrows[k] for k in sorted(fullrows)],schema_execution_dependency_binding=bind(NEW/'SCHEMA-EXECUTION-DEPENDENCIES.json'),integration_members_binding=bind(NEW/'integration-members.json'),
        claim_ceiling='34authored candidate operations composed from independently scoped authenticated branches. Sharedprofile/conformance, original323 regression, realpilot/privacy/acceptance/finalowner remain unqualified.')
    emit(NEW/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for row in fullrows.values():full[row['path']]=row
    for p in sorted(NEW.rglob('*')):
        if p.is_file():full[bind(p)['path']]=bind(p)
    for member in MEMBERS.values():
        for row in load(BASE/member['directory']/'source-manifest.json')['files']:full[row['path']]=row
    for p in [Path(__file__).resolve(),RUN/'ARE-common-integration-boundary-0155.json',RUN/'ARE-transport-evidence-boundary-0158.json',RUN/'ARE-governance-parser-boundary-0160.json',RUN/'ARE-common-codec-boundary-0164.json']:full[bind(p)['path']]=bind(p)
    emit(NEW/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'authored_handler_count':34,'integration_members_binding':bind(NEW/'integration-members.json'),
        'whole_API_qualified':False,'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(NEW/'source-manifest.json'),'profile_binding':bind(NEW/'contract-profile.json'),'authored_handlers':34}),flush=True)
if __name__=='__main__':main()
