"""Pair a real original source proof with real uncached private policy proof."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v7';NEW=BASE/'api-policy-source-boundaries-v1'
PIN='c373b7b65c381b97f3016192d74a21b6d13463ef8f6fdbd0938c1260dd828707'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    assert not NEW.exists()
    spec=importlib.util.spec_from_file_location('_cal_paired_policy_parent_0156',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);parent=guard.verify(PIN)
    shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('receipts','__pycache__'))
    for name in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json'):(NEW/name).unlink()
    path=NEW/'custody_context_sessions.py';text=path.read_text()
    old='    def guard(self):D.FACT_SCOPE.parent_guard(self.source);return copy.deepcopy(self.channel.guard())'
    new='''    def guard(self):
        # Full original signed-source proof (or its checked synchronous sealed
        # facts) and live private permission are separate obligations. The
        # original source callback remains unchanged. Original policy_guard's
        # source-independent path rereads custody, nonce-bound policy, exact
        # retained period, revocation, principal, limits and actual UTC.
        D.FACT_SCOPE.parent_guard(self.source)
        from .auth import ReaderChannel
        if type(self.channel) is ReaderChannel:
            context=self.channel.termination_guard()
        else:
            # Machine authentication/liveness retains its actual original
            # channel proof; it cannot borrow reader termination authority.
            context=self.channel.guard()
        return copy.deepcopy(context)'''
    assert text.count(old)==1;path.write_text(text.replace(old,new))
    for p in NEW.glob('*.py'):ast.parse(p.read_text())
    before={n.name:ast.dump(n,include_attributes=False) for p in OLD.glob('*.py') for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    after={n.name:ast.dump(n,include_attributes=False) for p in NEW.glob('*.py') for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    assert before==after,'original test assertions changed'
    selection=load(OLD/'SCHEMA-EXECUTION-DEPENDENCIES.json')
    oldprefix=OLD.relative_to(ROOT).as_posix()+'/';newprefix=NEW.relative_to(ROOT).as_posix()+'/'
    rows=[];reasons={}
    for row in selection['files']:
        key=newprefix+row['path'][len(oldprefix):] if row['path'].startswith(oldprefix) else row['path']
        rows.append(bind(ROOT/key));reasons[key]=selection['selection_reasons'][row['path']]
    selection.update(files=sorted(rows,key=lambda r:r['path']),selection_reasons=reasons,parent_source_binding=bind(OLD/'source-manifest.json'),parent_profile_binding=bind(OLD/'contract-profile.json'))
    emit(NEW/'SCHEMA-EXECUTION-DEPENDENCIES.json',selection)
    profile=load(OLD/'contract-profile.json');fullrows={r['path']:r for r in profile['files']}
    for row in [*rows,bind(NEW/'SCHEMA-EXECUTION-DEPENDENCIES.json')]:fullrows[row['path']]=row
    profile.update(files=[fullrows[k] for k in sorted(fullrows)],schema_execution_dependency_binding=bind(NEW/'SCHEMA-EXECUTION-DEPENDENCIES.json'))
    emit(NEW/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for p in sorted(NEW.rglob('*')):
        if p.is_file():full[bind(p)['path']]=bind(p)
    full[bind(Path(__file__).resolve())['path']]=bind(Path(__file__).resolve())
    emit(NEW/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'paired_source_policy_boundary':'Original full signed-source guard plus original source-independent live policy guard; Machine channel guard unchanged.',
        'test_assertions_changed':False,'original_callbacks_or_clocks_replaced':False,'runtime_qualification_transferred':False,
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(NEW/'source-manifest.json'),'profile_binding':bind(NEW/'contract-profile.json')}),flush=True)
if __name__=='__main__':main()
