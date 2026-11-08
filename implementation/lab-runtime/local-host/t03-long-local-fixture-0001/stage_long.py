"""Stage an additive Lesson + API30 Agent-contest fixture, never repository authority.

The old cuts are read-only inputs. Construction must run using the selected
durable native installation's Python and dependencies.
"""
from __future__ import annotations
import ast
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import secrets
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INSTALL = Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001'
T03 = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/local-lifecycle-actual-clock-0001'
OLD = T03/'native-durable-20261024/instances/legacy-local-4051bec8ca41c6e2'
CONTEST = ROOT/'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-d3537e8c3cb77a71'
ORIGINAL = ROOT/'implementation/lab-runtime/local-host/source8-current-fixture'
PRIVATE = Path.home()/'.local/share/cyberalchemy-lab/t03-long-fixture-private-0001'

def require(ok, message):
    if not ok: raise ValueError(message)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(v): return (json.dumps(v, indent=2, sort_keys=True)+'\n').encode()
def parse(p): return json.loads(p.read_bytes())
def binding(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def write(p,raw):
    p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream: stream.write(raw);stream.flush();os.fsync(stream.fileno())
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def rebase(value,old,new):
    if isinstance(value,dict):return {k:rebase(v,old,new) for k,v in value.items()}
    if isinstance(value,list):return [rebase(v,old,new) for v in value]
    return value.replace(old,new) if isinstance(value,str) else value

def engine():
    old=ORIGINAL/'engine-v3';new=HERE/'engine-v3'
    if new.exists():
        loaded=module('_integrated_engine_reuse_preflight',new/'loader.py')
        loaded.verify_engine(loaded.EnginePins(**parse(new/'pins.json')))
        return {'parent':binding(old/'engine-manifest.json'),'selected':binding(new/'engine-manifest.json'),'profile':binding(new/'runtime/profile.json'),'added_runtime_material':binding(ROOT/'product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json')}
    shutil.copytree(old,new,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    profile=parse(new/'runtime/profile.json')
    manifest_path='product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json'
    require(manifest_path not in profile['runtime_materials'],'API30 manifest unexpectedly present')
    profile['runtime_materials'].append(manifest_path)
    (new/'runtime/profile.json').write_bytes(encoded(profile))
    oldref=old.relative_to(ROOT).as_posix();newref=new.relative_to(ROOT).as_posix()
    manifest=rebase(parse(old/'engine-manifest.json'),oldref,newref)
    for row in manifest['files']:row['sha256']=sha((ROOT/row['path']).read_bytes())
    for row in manifest['changed_files']:
        row['candidate_binding']['sha256']=sha((ROOT/row['candidate_binding']['path']).read_bytes())
    manifest['profile_binding']=binding(new/'runtime/profile.json')
    (new/'engine-manifest.json').write_bytes(encoded(manifest))
    pins=parse(old/'pins.json');pins['profile_sha256']=manifest['profile_binding']['sha256'];pins['manifest_sha256']=sha((new/'engine-manifest.json').read_bytes())
    (new/'pins.json').write_bytes(encoded(pins))
    loaded=module('_integrated_engine_preflight',new/'loader.py')
    loaded.verify_engine(loaded.EnginePins(**pins))
    return {'parent':binding(old/'engine-manifest.json'),'selected':binding(new/'engine-manifest.json'),'profile':binding(new/'runtime/profile.json'),'added_runtime_material':binding(ROOT/manifest_path)}

def stage():
    sys.path.insert(0,str(INSTALL/'deps'))
    require((platform.python_version(),importlib.metadata.version('jsonschema'),importlib.metadata.version('cryptography'))==('3.14.4','4.23.0','46.0.5'),'selected durable ABI differs')
    selected_engine=engine()
    for name in ('installed_context_role.py','private_archive_hardening.py','prepare_installed_runtime.py'):
        destination=HERE/name;raw=(T03/'native-durable-20261024'/name).read_bytes()
        if destination.exists():require(destination.read_bytes()==raw,'selected helper differs')
        else:write(destination,raw)
    PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700)
    require(PRIVATE.stat().st_uid==os.getuid() and PRIVATE.stat().st_mode&0o777==0o700,'private root owner/mode differs')
    native=module('_integrated_stage_native',ORIGINAL/'native_successor.py')
    native.HERE=HERE;native.ENGINE_PROFILE=HERE/'engine-v3/runtime/profile.json';native.CLEAN_INSTALL=INSTALL
    identity='legacy-local-'+secrets.token_hex(8);out=native.stage(identity,PRIVATE);family=Path(out['family'])
    # Every fresh identity occurs once. Retarget the actual API30 Work body rather
    # than adding a second version with the generic 4051 Work's identity.
    selected=[]
    for role in ('source','reader','mapped','context'):
        for origin in sorted((OLD/role).glob('*.py')):
            if role=='source' and origin.name=='records.py':origin=CONTEST/'source/records.py'
            text=origin.read_text().replace(OLD.name,identity).replace(CONTEST.name,identity)
            text=text.replace(OLD.name.replace('-','_'),identity.replace('-','_')).replace(CONTEST.name.replace('-','_'),identity.replace('-','_'))
            text=re.sub(r'legacy_local_[0-9a-f]{16}',identity.replace('-','_'),text)
            text=text.replace((OLD.parent.parent).relative_to(ROOT).as_posix(),HERE.relative_to(ROOT).as_posix())
            text=text.replace((CONTEST.parent.parent).relative_to(ROOT).as_posix(),HERE.relative_to(ROOT).as_posix())
            text=text.replace(str(OLD/'source'),str(family/'source'))
            text=text.replace(str(Path.home()/'.local/share/cyberalchemy-lab/t03-native-private-20261024'/identity/'branch.snapshot'),str(PRIVATE/identity/'branch.snapshot'))
            if role=='source' and origin.name=='base.py':
                text=text.replace('implementation/lab-runtime/local-host/source8-current-fixture/engine-v3', (HERE/'engine-v3').relative_to(ROOT).as_posix())
                text=text.replace(sha((OLD/'source/context-native-role.json').read_bytes()),sha((family/'source/context-native-role.json').read_bytes()))
            if role=='source' and origin.name=='build.py':
                text=text.replace('len(items)==25','len(items)==26').replace('len(cores)==25','len(cores)==26').replace('thirteen sources and twelve','fourteen sources and twelve').replace('twenty-five independent','twenty-six independent')
                for old,new in (("'authored_current_artifacts':13","'authored_current_artifacts':14"),("'independent_participation_decision_cores':25","'independent_participation_decision_cores':26"),("'actual_original_targets':27","'actual_original_targets':28"),("'records':25","'records':26")):
                    text=text.replace(old,new)
            if role=='mapped' and origin.name=='build.py':
                text=text.replace("'operational-lesson:'+records.PREFIX+'-bounded-Session-review']", "'operational-lesson:'+records.PREFIX+'-bounded-Session-review',\n            'challenge-contract:'+records.PREFIX+'-agent-contest']")
            if role in ('mapped','context'):
                text=re.sub(r'\b29\b','30',text);text=re.sub(r'\b17\b','18',text);text=re.sub(r'\b34\b','35',text)
                text=text.replace('exact seventeen','exact eighteen')
            if role in ('mapped','context'):
                # Rebind the inherited producer pins only after each new phase.
                replacements={
                    sha((OLD/'source/source-manifest.json').read_bytes()):'f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2',
                    sha((OLD/'source/packages/0001/manifest.json').read_bytes()):'8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964',
                    sha((OLD/'reader/source-manifest.json').read_bytes()):'0ad1c974a5725d7bf0c23cc08b27c9e4e6c2b4fba512ddc0009aef337e81c0a5',
                    sha((OLD/'mapped/source-manifest.json').read_bytes()):'04a22ae3cd37ee70f2e2eb4dcf9a6b2d164fd08382a90c50e2d6a26be8f3f73c',
                    sha((OLD/'mapped/packages/0001/manifest.json').read_bytes()):'ba99b0023708613af17196ff4d5ed3ef9f2e9ddb68de06ab14d374182f5a5b94'}
                for before,after in replacements.items():text=text.replace(before,after)
            ast.parse(text)
            (family/role/origin.name).write_text(text)
            selected.append({'original':binding(origin),'staged':binding(family/role/origin.name)})
    # New explicitly bounded fixture, not an extension of any previous lease.
    episode_path=family/'source/episode-contract.json';declared=parse(episode_path)
    require(declared['max_session_seconds']==900,'original stage fixture budget differs')
    declared['max_session_seconds']=3600
    declared['purpose']='New local API30 learning lifecycle fixture with an explicitly declared 3600-second Session/View cap; actual Source, Reader, Context, Session and caller minima still apply.'
    episode_path.write_bytes(encoded(declared))
    source_base=family/'source/base.py';text=source_base.read_text()
    require(text.count("value['max_session_seconds']==900")==1,'exact Source episode lifetime seam required')
    text=text.replace("value['max_session_seconds']==900","value['max_session_seconds']==3600")
    source_base.write_text(text)
    generation=family/'context/generation.py';text=generation.read_text()
    require(text.count("policy['maximum_view_lifetime_seconds']<=900")==1,'exact Context lifetime seam required')
    generation.write_text(text.replace("policy['maximum_view_lifetime_seconds']<=900","policy['maximum_view_lifetime_seconds']<=3600"))
    policy_path=family/'context/lifetime-policy.json';policy=parse(policy_path)
    require(policy['default_request_seconds']==policy['maximum_view_lifetime_seconds']==900,'original Context policy budget differs')
    policy.update(default_request_seconds=3600,maximum_view_lifetime_seconds=3600,
                  claim_ceiling='New explicit 3600-second local fixture budget. Actual expiry remains the minimum of current Source period, independently current host grant, Context, Session and caller deadline. No previous lease or original Assignment is extended.')
    policy_path.write_bytes(encoded(policy))
    budget_bindings=[binding(path)for path in (episode_path,source_base,generation,policy_path)]
    for path in family.rglob('*.py'):compile(path.read_bytes(),str(path),'exec',dont_inherit=True)
    # Constructor behavior is retained; this local entry provides ordinary phase
    # dispatch while retaining immutable O_EXCL phase receipts.
    text=(T03/'lesson_construct_legacy_v3.py').read_text()
    text=text.replace("if __name__=='__main__':raise SystemExit('Use independently selected execute_recipe.py; direct helper dispatch is inactive.')","if __name__=='__main__':main()")
    if (HERE/'construct_integrated.py').exists():require((HERE/'construct_integrated.py').read_text()==text,'constructor changed')
    else:write(HERE/'construct_integrated.py',text.encode())
    report={'schema_version':'lab-integrated-fixture-stage/v1-candidate','selection':out,'engine':selected_engine,'templates':selected,
      'retained_one_lesson':True,'current_record_count_expected':26,'original_targets_expected':28,'mapped_nodes_expected':18,'mapped_edges_expected':12,'mapped_cursor_expected':30,'Context_carriers_expected':35,
      'identity_collision_strategy':'Fresh unique family identities; replace generic Work/Intent/Goal/Context with exact API30-specific templates once; add one distinct Agent Contract. Baseline foundation principal/Contract and historical Session remain untouched.',
      'authority_effect':'none','actual_owner_outcome':None,'shared_API_qualified':False,'new_fixture_session_seconds':3600,'budget_bindings':budget_bindings,'old_900_fixtures_modified':False}
    write(HERE/('stage-'+identity+'.json'),encoded(report));print(json.dumps(report['selection'],sort_keys=True),flush=True)

if __name__=='__main__':stage()
