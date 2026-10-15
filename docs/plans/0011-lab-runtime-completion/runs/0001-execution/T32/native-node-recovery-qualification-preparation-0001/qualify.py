"""Root-only bounded real-translator/native node recovery qualification.

No work runs at import. No installation, source admission or shared publication.
Requires an already provisioned, independently pinned ontology executor.
"""
import argparse, copy, datetime, hashlib, importlib, importlib.abc, importlib.util, json, os
from pathlib import Path
import stat, sys, traceback, types, uuid

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T32/native-lifecycle-recovery-adoption-0003'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
DEP=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'
LIFECYCLE=ROOT/'implementation/lab-ontology/candidates/v1/adapters/lifecycle'
MODES={'schema_version','authority_effect','mode','owned_code_bindings','active_code_bindings',
    'api_source_binding','api_profile_binding','root_dispatch_binding','technical_deadline_utc',
    'store_parent','output_root','reference_bindings','module_bindings','ontology_execution_selection_binding'}
SOURCE='ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'
PROFILE='9c8c3018226abb9077c6a99ee3cbc9dd0174c148b332b9488fd4a3a9cd30418b'

def need(v,why):
    if not v:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def pairs(items):
        out={}
        for k,v in items:need(k not in out,'duplicate qualification key');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite qualification value'))
def relative(row):
    need(type(row)is dict and set(row)=={'path','sha256'},'closed independently selected binding required')
    p=Path(row['path'])
    need(not p.is_absolute()and '..'not in p.parts and p.as_posix()==row['path']and row['path']!='.','canonical repository origin required')
    need(type(row['sha256'])is str and len(row['sha256'])==64 and all(c in '0123456789abcdef'for c in row['sha256']),'exact independent SHA required')
    return ROOT/p
def bootstrap_capture():
    # Root supplies exact runner/capture bytes before dispatch. The subsequent
    # external packet pin independently seals all three actual owned origins.
    path=HERE/'capture.py'
    raw=path.read_bytes()
    need(sha(raw)=='b41f1914e0d6a9be125e228525ca92d1b28d853be79c118adffc040bcf01f0fa','reviewed bounded capture differs')
    m=types.ModuleType('_T32_qualification_capture');m.__file__=str(path)
    exec(compile(raw,str(path),'exec'),m.__dict__)
    need(m.capture_path(path,sha(raw))==raw,'capture origin changed')
    return m.capture_path
def module(name,path,raw=None,package=False):
    need(name not in sys.modules,'fresh true-origin module namespace required')
    spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)]if package else None)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value
    exec(compile(path.read_bytes()if raw is None else raw,str(path),'exec'),value.__dict__)
    return value
def diagnostic(error):
    kind,_,tb=error;frames=[]
    while tb:
        p=Path(tb.tb_frame.f_code.co_filename)
        if p.is_relative_to(ROOT):frames.append({'path':str(p.relative_to(ROOT)),'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
        tb=tb.tb_next
    return {'exception_class':kind.__name__,'frames':frames}

def run(packet,packet_binding,capture):
    need(type(packet)is dict and set(packet)==MODES and packet['schema_version']=='lab-T32-owned-node-recovery-qualification/v1-candidate'
        and packet['mode']=='bounded-original-node-recovery-and-immutable-cold'and packet['authority_effect']=='none','closed bounded technical selection required')
    need(Path(sys.executable)==INSTALL/'bin/python'and sys.dont_write_bytecode,'selected0004 Python with -B required')
    need(packet['api_source_binding']=={'path':str((API/'source-manifest.json').relative_to(ROOT)),'sha256':SOURCE}
        and packet['api_profile_binding']=={'path':str((API/'contract-profile.json').relative_to(ROOT)),'sha256':PROFILE},'current exact API5 Source/profile selection required')
    exact=lambda row:capture(relative(row),row['sha256'])
    own=packet['owned_code_bindings']
    need(type(own)is dict and set(own)=={'runner','capture','boundary'},'all owned code required')
    for role,leaf in [('runner','qualify.py'),('capture','capture.py'),('boundary','boundary.py')]:
        need(relative(own[role])==HERE/leaf,'actual owned code origin differs');exact(own[role])
    refs=packet['reference_bindings']
    need(type(refs)is dict and set(refs)=={'adoption_handoff','adoption_manifest','adoption_peer','migration_scope'},'closed actual accepted reference set required')
    expected={'adoption_handoff':(P/'HANDOFF.json','697e4380d32d778606e7bd849850e5e907c8909869fc61de07dc472bfa3ef873'),
        'adoption_manifest':(P/'source-manifest.json','803b642a55a97b9a83721e1585ff686e666713904634de34cf4b7141541b7534'),
        'adoption_peer':(RUN/'T32/native-lifecycle-recovery-independent-review-0003/independent-review-0001.json','ad05e2ad6519e43702054ccb63231fd73de41792b385434d9fcf97a0c8c0d732'),
        'migration_scope':(ROOT/'implementation/lab-ontology/candidates/v1/migration/adapters/build-scope.json','9f42e28db872ad237c0859d99614758e13c9016168c3c93704bb83fd3573b3ad')}
    for key,(path,pin)in expected.items():need(refs[key]=={'path':str(path.relative_to(ROOT)),'sha256':pin},'exact accepted reference differs');exact(refs[key])
    selected=parse(exact(refs['adoption_manifest']))['files']
    selected_cache={}
    def all_selected():
        for row in selected:
            p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
            raw=capture(p,row['sha256']);need(len(raw)==row['size_bytes'],'full130 selected bytes differ')
            if str(p)not in selected_cache:selected_cache[str(p)]=raw
        for row in own.values():exact(row)
        exact(packet_binding)
    all_selected()
    # Selection is not an effect grant: this receipt records only Root's
    # exclusive scheduling of fixed owned technical cases.
    dispatch=parse(exact(packet['root_dispatch_binding']))
    need(type(dispatch)is dict and set(dispatch)=={'schema_version','authority_effect','mode','api_source_binding','api_profile_binding','store_parent','output_root','technical_deadline_utc','native_cases','migration_status'}
        and dispatch['schema_version']=='lab-T32-Root-owned-technical-dispatch/v1-candidate'and dispatch['authority_effect']=='none'
        and dispatch['mode']==packet['mode']and dispatch['native_cases']==['original-node-postcommit-refusal','explicit-live-reconciliation','recovered-node-relation-challenge','immutable-generation-A-after-B']
        and dispatch['migration_status']=='REFUSED-original480-versus-selected57416','Root fixed technical dispatch required')
    for key in ('api_source_binding','api_profile_binding','store_parent','output_root','technical_deadline_utc'):
        need(dispatch[key]==packet[key],'Root technical custody/clock correspondence differs')
    deadline=datetime.datetime.fromisoformat(packet['technical_deadline_utc'])
    remaining=(deadline-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
    need(deadline.utcoffset()==datetime.timedelta(0)and 0<remaining<=900,'fresh independently selected technical deadline within original900 seconds required')
    mods=packet['module_bindings']
    origins={'checked_io':DEP/'checked_io.py','stage_io':DEP/'stage_io.py','closure':DEP/'closure.py','dependencies':DEP/'closure_hardened_0003.py',
        'control':ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/control.py',
        'executor':RUN/'T07/ontology-native-execution-preparation-0001/native_executor.py','api_guard':API/'guard.py',
        'native_store':LIFECYCLE/'native_store.py','translation':LIFECYCLE/'translation.py','represented_subjects':LIFECYCLE.parent/'represented_subjects.py'}
    need(type(mods)is dict and set(mods)==set(origins),'complete true bootstrap module origins required')
    for key,path in origins.items():need(relative(mods[key])==path,'bootstrap origin differs');exact(mods[key])
    required_active={tuple(sorted(v.items()))for v in [*own.values(),*mods.values()]}
    for leaf in ('capture.py','private_io.py','generation_store.py','selected_store.py'):
        row=next(v for v in selected if ROOT/v['path']==P/leaf)
        required_active.add(tuple(sorted({'path':row['path'],'sha256':row['sha256']}.items())))
    need(type(packet['active_code_bindings'])is list and {tuple(sorted(v.items()))for v in packet['active_code_bindings']}==required_active
        and len(packet['active_code_bindings'])==len(required_active),'exact full active code set required')
    # Early selected custody, before full guard/import/native effects.
    pkgname='_T32_selected_native_'+uuid.uuid4().hex
    class CapturedLoader(importlib.abc.Loader):
        def __init__(self,path):self.path=path
        def create_module(self,spec):return None
        def exec_module(self,value):
            value.__file__=str(self.path)
            exec(compile(selected_cache[str(self.path)],str(self.path),'exec'),value.__dict__)
    class CapturedFinder(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname.startswith(pkgname+'.'):
                leaf=fullname[len(pkgname)+1:]
                need(leaf in {'capture','private_io','generation_store','selected_store'},'unselected native package module')
                p=P/(leaf+'.py')
                return importlib.util.spec_from_loader(fullname,CapturedLoader(p),origin=str(p))
            return None
    finder=CapturedFinder();sys.meta_path.insert(0,finder)
    module(pkgname,P/'__init__.py',selected_cache[str(P/'__init__.py')],package=True)
    io=importlib.import_module(pkgname+'.private_io')
    for key in ('store_parent','output_root'):
        custody=packet[key];need(type(custody)is dict and set(custody)=={'path','identity'},'closed independent owned root required')
        path=Path(custody['path']);need(path.is_absolute()and '..'not in path.parts and not path.is_relative_to(ROOT),'owned root outside repository required')
        with io.directory(path)as fd:
            s=os.fstat(fd);need([s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==custody['identity']and s.st_uid==os.getuid()and stat.S_IMODE(s.st_mode)==0o700,'owned root identity differs')
            need(os.listdir(fd)==[],'both roots must be freshly empty')
    out=Path(packet['output_root']['path'])
    need(out!=Path(packet['store_parent']['path'])and not out.is_relative_to(packet['store_parent']['path'])and not Path(packet['store_parent']['path']).is_relative_to(out),'separate technical output/store custody required')
    emit=lambda name,value:io.write(out/name,io.canonical(value))
    emit('started.json',{'authority_effect':'none','actual_native_started':False,'packet_binding':packet_binding})
    guard=None;entered=False;store=None;boundary=None;events=[];failure=None;exit_errors=[];fd0=len(os.listdir('/proc/self/fd'))
    try:
        guard=module('_T32_current_guard_'+uuid.uuid4().hex,origins['api_guard'],exact(mods['api_guard']))
        guard.verify(SOURCE);exact(packet['api_profile_binding']);entered=True
        sys.path.insert(0,str(INSTALL/'deps'))
        for name in ('checked_io','stage_io','closure'):
            module(name,origins[name],exact(mods[name]))
        deps=module('_T32_dependencies_'+uuid.uuid4().hex,origins['dependencies'],exact(mods['dependencies']))
        control=module('_T32_control_'+uuid.uuid4().hex,origins['control'],exact(mods['control']))
        executor_module=module('_T32_ontology_executor_'+uuid.uuid4().hex,origins['executor'],exact(mods['executor']))
        raw=exact(packet['ontology_execution_selection_binding'])
        executor=executor_module.SelectedOntologyExecutor(raw,packet['ontology_execution_selection_binding']['sha256'],deps,control)
        executor.guard() # existing complete installation only; no provision call
        sys.path.insert(0,str(LIFECYCLE.parent));sys.path.insert(0,str(LIFECYCLE))
        sys.path.insert(0,str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation'))
        for name in ('represented_subjects','translation','native_store'):
            module(name,origins[name],exact(mods[name]))
        original=sys.modules['native_store']
        generation=importlib.import_module(pkgname+'.generation_store')
        selected_store=importlib.import_module(pkgname+'.selected_store')
        bmod=module('_T32_technical_boundary_'+uuid.uuid4().hex,HERE/'boundary.py',exact(own['boundary']))
        boundary=bmod.OwnedTechnicalBoundary(packet,packet_binding,capture,io)
        selection={'schema_version':selected_store.VERSION,'authority_effect':'none','original_store_binding':mods['native_store'],
            'generation_module_binding':{'path':str((P/'generation_store.py').relative_to(ROOT)),'sha256':sha(selected_cache[str(P/'generation_store.py')])},
            'executor_class_binding':{'code_binding':mods['executor'],'class_name':'SelectedOntologyExecutor'},
            'boundary_class_binding':{'code_binding':own['boundary'],'class_name':'OwnedTechnicalBoundary'},
            'owned_parent':packet['store_parent']['path'],'owned_parent_identity':packet['store_parent']['identity'],
            'retention_policy':'preserve-all-until-explicit-disposition'}
        factory=selected_store.StoreFactory(original,generation,executor,boundary,selection)
        def record(label,value):
            events.append({'case':label,**value});emit('case-%02d.json'%len(events),events[-1])
        with original.signed_catalog()as(catalog,operations):
            adapter=original.CandidateRepresentationAdapter(catalog,operations)
            translator=original.RichTranslation(adapter,original.bind(original.PROFILE))
            casepath=ROOT/'implementation/lab-workflows/candidates/v1/receipts/integration/W07/0001/scenarios/failure/case.json'
            case=original.parse(casepath.read_bytes())
            cut={'cut_id':case['case_id'],'authority_effect':'none','actual_owner_outcome':None,'records':[{k:r[k]for k in ['path','sha256','kind','version_ref']}for r in case['records']]}
            view=adapter.candidate_cut(cut);adapter.validate_candidate_relations(view)
            old=next(v for v in view['views'].values()if v['represented_subject']['identity']=='implementation:lab-W05:historical-builder')
            cap=next(v for v in view['views'].values()if v['carrier']['kind']=='product-capability')
            edge=next(v for v in view['views'].values()if v['carrier']['kind']=='typed-relation'and v['record']['payload']['source']['version_ref']==old['represented_subject']['version_ref']and v['record']['payload']['target']['version_ref']==cap['represented_subject']['version_ref'])
            store=factory.create(translator,executor.executable_path,executor.executable_sha256)
            boundary.arm_after_head_transition(store.store_root)
            try:store.map_node(old)
            except bmod.TechnicalBoundaryRefusal:pass
            else:raise ValueError('declared real postcommit fault was not observed')
            need(store.pending_operation is not None and store.specs=={}and store.semantic_events==[], 'refused commit adopted unaccepted RAM metadata')
            pending=store.pending_operation
            control_binding={'path':pending['control_path'],'sha256':pending['control_sha256']}
            committed=store.committed.head()
            need(committed[0]['request_sha256']==pending['pins'].request_sha256 and committed[0]['files'],'native HEAD did not actually commit before fault')
            record('actual-postcommit-refusal',{'result':'PASS','pending_control_binding':control_binding,'head_sha256':sha(committed[1]),'rich_metadata_adopted':False})
            boundary.acknowledge_retained_commit(control_binding)
            recovered=store.reconcile_pending(control_binding)
            node=translator.node_spec(old)['node_id']
            need(store.pending_operation is None and store.specs[node]==translator.node_spec(old)and len(store.semantic_events)==1,'exact live node metadata reconciliation failed')
            try:store.map_node(old)
            except original.RepresentationFault:pass
            else:raise ValueError('duplicate recovered node was accepted')
            record('explicit-live-reconciliation',{'result':'PASS','node_id':node,'semantic_cursor':len(store.semantic_events),'governance_cursor':len(store.governance_events),'duplicate_refused':True})
            snapshot=store.snapshot_original_outcome()
            io.write(out/'retained-generation-A-head.json',snapshot['head_raw'])
            headA={'path':str(out/'retained-generation-A-head.json'),'sha256':sha(snapshot['head_raw'])}
            cap_node,_=store.map_node(cap)
            relation,_=store.map_relation(edge,view,{old['represented_subject']['version_ref']:node,cap['represented_subject']['version_ref']:cap_node})
            contract=next(r for r in case['records']if r['kind']=='challenge-contract')
            decisions=next(r for r in case['records']if r['kind']=='decision')
            challenges=sorted([r for r in case['records']if r['kind']=='challenge-event'],key=lambda r:r['version_ref'])
            before_sem={k:v for k,v in store.files().items()if k.startswith('semantic/')}
            for row in challenges:store.map_challenge(node,row,contract,decisions)
            need(before_sem=={k:v for k,v in store.files().items()if k.startswith('semantic/')},'recovered-node challenge changed semantic original bytes')
            later=store.snapshot_original_outcome()
            record('recovered-node-relation-challenge',{'result':'PASS','relation_id':relation,'challenge_revisions':len(challenges),'semantic_original_bytes_unchanged':True,'semantic_cursor':len(store.semantic_events),'governance_cursor':len(store.governance_events)})
            cold=factory.cold_snapshot_original_outcome(store_root=store.store_root,store_identity=store.committed.identity,
                expected_head_binding=headA,expected_generation=snapshot['generation'],expected_event_files={k:v['sha256']for k,v in snapshot['event_files'].items()},expected_projection_sha256=snapshot['projection_sha256'])
            need(cold['projection_raw']==snapshot['projection_raw']and cold['semantic_events']==snapshot['semantic_events']and cold['governance_events']==snapshot['governance_events'],'actual old immutable generation replay differs')
            need(store.snapshot_original_outcome()['head_raw']==later['head_raw'],'old generation replay changed current HEAD')
            record('immutable-generation-A-after-B',{'result':'PASS','generation_A':snapshot['generation'],'generation_B':later['generation'],'projection_A_sha256':cold['projection_sha256'],'mutable_HEAD_followed':cold['mutable_inner_HEAD_followed'],'write_or_retry_performed':cold['write_or_retry_performed']})
    except BaseException:failure=diagnostic(sys.exc_info())
    finally:
        if finder in sys.meta_path:sys.meta_path.remove(finder)
        if store is not None:
            store.close()
            if not(store.closed and store.root.is_dir()):exit_errors.append({'exception_class':'RetainedStorePostconditionFailure'})
        if entered:
            for fn in (lambda:guard.verify(SOURCE),all_selected,lambda:exact(packet['api_profile_binding'])):
                try:fn()
                except BaseException:exit_errors.append(diagnostic(sys.exc_info()))
        if boundary is not None:
            try:boundary.check_base()
            except BaseException:exit_errors.append(diagnostic(sys.exc_info()))
        fd_delta=len(os.listdir('/proc/self/fd'))-fd0
        passed=failure is None and not exit_errors and len(events)==4 and fd_delta==0
        emit('result.json',{'schema_version':'lab-T32-bounded-real-node-recovery-result/v1-candidate','authority_effect':'none',
            'result':'PASS-bounded-actual-node-recovery'if passed else 'FAIL-preserved-owned-attempt','cases':events,'failure':failure,'exit_errors':exit_errors,
            'FD_delta':fd_delta,'native_root_retained':None if store is None else str(store.root),'source_sha256':SOURCE,'profile_sha256':PROFILE,
            'migration_status':'REFUSED-original480-versus-selected57416','N01_full_lifecycle_route_completed':False,'N02_withdrawal_completed':False,'N03_migration_completed':False,
            'original27_interruption_23_regression_cohort_rerun':False,'T14_mixed_publisher_qualified':False,'genuine_owner_authority':False,'full_runtime_or_task_complete':False})
    return 0 if passed else 1

def main():
    a=argparse.ArgumentParser();a.add_argument('--selection',required=True);a.add_argument('--selection-sha256',required=True);args=a.parse_args()
    capture=bootstrap_capture();binding={'path':args.selection,'sha256':args.selection_sha256}
    raw=capture(relative(binding),binding['sha256'])
    return run(parse(raw),binding,capture)
if __name__=='__main__':raise SystemExit(main())
