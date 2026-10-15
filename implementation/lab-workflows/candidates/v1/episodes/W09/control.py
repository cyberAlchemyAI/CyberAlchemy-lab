"""Exact W09 selections and bounded host/Agent context integration."""
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime,timezone
import copy
import importlib.util
from pathlib import Path
import sys
import time

from build import HERE,PACKAGE,ROOT,RUN,require,sha,bind,load,encoded,mapped,emit
SELECTION_PATH=HERE/'packages/bc3c50170a404b4ba8d8/selection.json'
SELECTION_SHA='182062167f8620c5f2c679a0bacd3bf9ab8a645569ffffb11225b6642faff8d6'


def original(b):
    require(set(b)=={'path','sha256'},'closed original binding required')
    p=ROOT/b['path'];require(not Path(b['path']).is_absolute() and '..' not in Path(b['path']).parts
        and p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(ROOT) and not any(x.is_symlink() for x in p.parents),'unsafe source')
    raw=p.read_bytes();require(sha(raw)==b['sha256'],'selected source differs: '+b['path']);return raw


def selection():
    require(sha(SELECTION_PATH.read_bytes())==SELECTION_SHA,'independent W09 selection differs');v=load(SELECTION_PATH)
    require(v['authority_effect']=='none' and v['actual_owner_outcome'] is None and v['canonical_effects_applied']==0
        and v['runtime_activation'] is False and set(v['inputs'])=={'engineering','research'},'selection scope/authority differs')
    for b in v['source_files']:original(b)
    for row in v['constructor_recipes']:
        text=original(row['original_binding']).decode()
        for edit in row['ordered_edits']:
            require(text.count(edit['before'])==edit['occurrences'],'exact source recipe no longer applies');text=text.replace(edit['before'],edit['after'])
        require(text.encode()==original(row['generated_binding']),'prospective constructor differs from exact recipe')
    for row in v['inputs'].values():
        actual=load(ROOT/row['selection_binding']['path']);original(row['selection_binding'])
        for r in actual['records']:original({'path':str((ROOT/row['selection_binding']['path']).parent.joinpath(r['path']).relative_to(ROOT)),'sha256':r['sha256']})
    native=Path(v['native_executable_binding']['path']);require(native.is_file() and not native.is_symlink()
        and sha(native.read_bytes())==v['native_executable_binding']['sha256'],'selected native executable differs')
    return v


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(spec);sys.modules[name]=v;spec.loader.exec_module(v);return v


def select_sources(selected,domain):
    directory=SELECTION_PATH.parent/'sources';sys.path.insert(0,str(directory))
    sys.path.insert(0,str(PACKAGE/'authority'));sys.path.insert(0,str(PACKAGE/'tools'))
    engine=module('engineering',directory/'engineering.py');research=module('research',directory/'research.py')
    if domain=='learning':
        adapter=module('adapter',directory/'adapter.py')
        sys.path.insert(0,str(PACKAGE/'learning'))
        import lessons
        application=module('application',directory/'application.py')
        runtime=module('_W09_learning_episode',directory/'run_learning.py')
        return runtime,engine,research
    path=PACKAGE/'examples'/domain/'run_episode.py';sys.path.insert(0,str(path.parent))
    return module('_W09_'+domain+'_episode',path),engine,research


def token_map(value,changes):
    if isinstance(value,str):return changes.get(value,value)
    if isinstance(value,list):return [token_map(v,changes) for v in value]
    if isinstance(value,dict):return {token_map(k,changes):token_map(v,changes) for k,v in value.items()}
    return value


def rebind(f,namespace,phase,*,guard=None,handles=None,clock=None,owned_store_scope=None,source_bindings=(),adapter_binding=None):
    from evaluator import SessionLease
    clock=clock or [time.time()];clock[0]=time.time();old_handles=(f.session.instance_ref,f.session.session_ref)
    old_ids={k:v['node_id'] for k,v in f.by_kind.items()};old_refs={k:f.ref(k) for k in f.by_kind}
    old_tool_class=f.status['tool_classes'][old_refs['tool']]
    previous=f.session;previous.close()
    def current():
        clock[0]=time.time()
        try:
            result=guard() if guard else None
            for b in source_bindings:original(b)
            return result
        except BaseException:
            if guard and hasattr(guard,'agent'):guard.agent.close()
            raise
    f.session=SessionLease(clock=lambda:clock[0],context_reader=current);f.now=clock
    if handles:f.session.instance_ref,f.session.session_ref=handles
    nonce=f.session.instance_ref.split(':')[-1]
    for k in f.by_kind:f.by_kind[k]['node_id']=k+':lab-W09:'+namespace+':'+phase+':'+nonce
    changes={old_ids[k]:f.by_kind[k]['node_id'] for k in f.by_kind}
    changes.update({old_refs[k]:f.ref(k) for k in f.by_kind});changes.update(zip(old_handles,(f.session.instance_ref,f.session.session_ref)))
    f.by_kind=token_map(f.by_kind,changes);f.status=token_map(f.status,changes);f.request=token_map(f.request,changes)
    f.records={}
    for k in f.by_kind:f.reselect(k)
    head=guard.head if guard else f.status['head'];f.status['head']=head
    f.status['periods']={ref:[clock[0]-60,clock[0]+900] for ref in f.status['periods']}
    f.status['runtime_handle_bindings']={f.ref('agent-instance'):f.session.instance_ref,f.ref('agent-session'):f.session.session_ref}
    f.status['tool_classes']={f.ref('tool'):old_tool_class};f.status['role_versions']={f.by_kind['role']['node_id']:f.ref('role')}
    f.request.update(principal_ref=f.ref('principal'),instance_ref=f.session.instance_ref,session_ref=f.session.session_ref,
        assignment_ref=f.ref('agent-assignment'),delegation_ref=f.ref('delegation'),role_assignment_ref=f.ref('role-assignment'),
        tool_ref=f.ref('tool'),instance_record_ref=f.ref('agent-instance'),session_record_ref=f.ref('agent-session'),profile_ref=f.ref('agent-profile'),
        expected_head=head,idempotency_key='W09:'+namespace+':'+phase,deadline=datetime.fromtimestamp(clock[0]+800,timezone.utc).isoformat())
    adapter_sha=f.authority.adapter_sha256
    if adapter_binding:
        original(adapter_binding);adapter_sha=adapter_binding['sha256'];f.adapter_sha256=adapter_sha
    evidence=encoded({'schema_version':'lab-W09-controlled-host-permission/v1-candidate','fixture_only':True,'actual_owner_outcome':None,'authority_effect':'none',
        'authorization_binding':bind(RUN/'authorization.json'),'selection_binding':bind(SELECTION_PATH),'integration_adapter_binding':bind(Path(__file__)),
        'business_Project_scope':f.scope,'owned_store_scope':owned_store_scope,'run_namespace':namespace,'phase':phase,
        'source_bindings':list(source_bindings),'selected_adapter_binding':adapter_binding,'allowed_action_kinds':sorted(f.grant.action_kinds),'actual_current_head':head,
        'actual_runtime_handles':{'instance_ref':f.session.instance_ref,'session_ref':f.session.session_ref},
        'excluded_effects':['canonical admission','live or existing stores','service activation','external effects','private Session memory export','human pilot inference']})
    f.grant=replace(f.grant,principal_ref=f.ref('principal'),tool_ref=f.ref('tool'),role_assignment_ref=f.ref('role-assignment'),
        not_before=clock[0]-60,expires_at=clock[0]+900,evidence_original=evidence,evidence_sha256=sha(evidence),
        evidence_ref='protocol:W09:owned-host-permission:'+namespace+':'+phase,adapter_sha256=adapter_sha)
    old=f.authority;kwargs={'adapter_sha256':adapter_sha,'environment_sha256':old.environment_sha256}
    if hasattr(old,'registered_interfaces'):kwargs['registered_interfaces']=old.registered_interfaces
    f.authority=type(old)(f.session,lambda ref:f.records.get(ref),lambda:copy.deepcopy(f.status),lambda:f.grant,**kwargs)
    require(previous.closed and not previous._memory,'old prototype lease memory remains')
    return f
