"""Closed read scopes from pinned replay; public queries never supply projections."""
from contextlib import contextmanager
import tempfile
from common import *
COUPLING=ROOT/'product/lab/release-candidates/v1/interface/coupling'
sys.path.insert(0,str(COUPLING))
loader=module('_O03_exact_engine_loader',COUPLING/'loader.py')
PINS=loader.EnginePins('53e2f74c53f123b42d60d3cc3b4c66e75f3fa0c4c9a3142bf3f11e7500bd9677','lab-operator-signed-coupling/v1-candidate',
    '4594cab2172646b1c2157e0a4be37f560088c580de875fd7d269925993fe1f0b','cbfe3d7c5f92d0bc547b836a9d84616b9be26cb399a587aab8800f93fd96ed58')
R0=ROOT/'docs/plans/0007-governance-architecture-ontology/r0-source-manifest.json'
_FACTORY=object()
def verified_call(fn,fault):
    def call(*args,**kwargs):
        try:return fn(*args,**kwargs)
        except fault as error:raise QueryFault(str(error)) from error
    return call

class VerifiedScope:
    def __init__(self,data,scope_ref,source_guard,validator,factory,*,native=None,reconciliation=None,schema_validator=None):
        require(factory is _FACTORY,'scope requires independently verified original replay')
        self.data=copy.deepcopy(data);self.original_digest=digest(self.data);self.scope_ref=scope_ref
        self.source_guard=source_guard;self.validate_relation=validator;self.validate_schema=schema_validator;self.closed=False;self.expires=time.monotonic()+900
        self.native=copy.deepcopy(native);self.reconciliation=copy.deepcopy(reconciliation or [])
        self.control_bindings=[bind(p) for p in sorted(HERE.glob('*.py'))]+[bind(p) for p in sorted((HERE/'contracts').glob('*.json'))]+[bind(PROFILE)]
        self.control_paths={b['path'] for b in self.control_bindings}
    def guard(self):
        require(not self.closed and time.monotonic()<self.expires,'query scope closed or expired')
        require(digest(self.data)==self.original_digest,'verified projection was altered')
        controls=source_status(self.control_bindings);actual={p.relative_to(ROOT).as_posix() for p in HERE.glob('*.py')}|{p.relative_to(ROOT).as_posix() for p in (HERE/'contracts').glob('*.json')}|{PROFILE.relative_to(ROOT).as_posix()}
        if actual!=self.control_paths:controls['changed'].append('query-control-file-closure');controls['state']='stale'
        try:status=self.source_guard()
        except (ValueError,OSError) as error:status={'state':'unknown','changed':[],'missing':[],'unsafe':[],'unchecked':['actual-source-replay:'+str(error)],'checked_count':0}
        for k in ['changed','missing','unsafe','unchecked']:status[k]=sorted(set(status.get(k,[])+controls[k]))
        status['checked_count']=status.get('checked_count',0)+controls['checked_count']
        status['state']='stale' if any(status[k] for k in ['changed','missing','unsafe']) else 'unknown' if status['unchecked'] else 'current'
        return status
    def close(self):self.closed=True


def historical_d73(data):
    """Replay only original D71-D73 admission overlays; later postures cannot leak."""
    result=copy.deepcopy(data);source=data['projection'];p=result['projection'];subjects={};docs=p['documents']
    chosen=[]
    for family in ['cyberalchemy-lab-operational-foundation','project-state-bootstrap','first-governed-agent-work-episode']:
        base='authority/admissions/'+family+'/v1/'
        for name,category in [('artifact-instance-admission.json','artifact-instance'),('typed-relation-admission.json','typed-relation')]:
            overlay_path=base+name;overlay=docs[overlay_path]
            for row in overlay['entries']:
                path=row['admitted_instance_path'];record=docs[path];b={'path':path,'sha256':data['baseline']['materials'][path]}
                ref=row['version_ref'] if 'version_ref' in row else record['node_id']+'@sha256.'+b['sha256']
                matches=[v for v in source['subjects'].values() if v['source']['path']==path and v['version_ref']==ref]
                require(len(matches)==1,'historical admitted exact revision unresolved')
                entry=copy.deepcopy(matches[0]);entry['effective_state']=row['lifecycle_state'];entry['admission_overlay_binding']={'path':overlay_path,'sha256':data['baseline']['materials'][overlay_path]}
                entry['decision_ref']=overlay['decision_id'];subjects[ref]=entry;chosen.append(b)
                for facet in ['agent_instance','agent_session','work','assignment']:
                    closure=overlay.get('operational_closure',{})
                    if closure.get(facet+'_ref')==entry['identity']:entry['operational_disposition']=closure.get(facet+'_disposition','unknown')
            for transition in overlay.get('predecessor_transitions',[])+([overlay['predecessor_transition']] if 'predecessor_transition' in overlay else []):
                for v in subjects.values():
                    if v['identity']==transition['identity_ref'] and (not transition.get('version_ref') or v['version_ref']==transition['version_ref']):v['effective_state']=transition['to']
    # Selected old type descriptors/Definitions explain source contracts, with their own recorded epochs.
    carrier_refs={v['carrier_ref'] for v in subjects.values() if v.get('carrier_ref')};definitions=set()
    for ref in sorted(carrier_refs):
        if ref in source['subjects']:
            subjects[ref]=copy.deepcopy(source['subjects'][ref]);subjects[ref]['historical_contract_posture']='Descriptor inspected at its own D75 source epoch; D73 type posture is not inferred.'
            definitions.update(subjects[ref]['record'].get('semantic_definition_refs',[]))
    for ref in sorted(definitions):
        if ref in source['subjects']:subjects[ref]=copy.deepcopy(source['subjects'][ref])
    p['subjects']=subjects;p['state']=next(v['record'] for v in subjects.values() if v['kind']=='project-state' and v['effective_state']=='admitted-current')
    p['histories']={kind:next(v['record'] for v in subjects.values() if v['kind']==kind and v['effective_state']=='admitted-current') for kind in ['project-semantic-event-history','project-governance-event-history']}
    result['selected_admission_epoch']='decision:0073';result['historical_scope']=True
    return result


@contextmanager
def governed_scope(scope_ref):
    require(scope_ref in ['d75-selected-source','historical-d73-slice'],'closed governed query scope')
    loader.verify_engine(PINS)
    with tempfile.TemporaryDirectory(prefix='cal-O03-query-') as temp,loader.engine(PINS) as handle:
        owned=Path(temp);store,key=handle.create_owned(owned,'O03-query-'+scope_ref,selected_project_scope=True)
        data=store.replay(require_current=True);head=data['head']['transaction_digest']
        r0=load(R0);require(r0['source_count']==len(r0['sources'])==50,'original query source inventory differs')
        relocations=[];extra=[]
        for row in r0['sources']:
            b={k:row[k] for k in ['path','sha256']}
            if b['path']=='authority/definitions/registry.json':
                archived={'path':'authority/admissions/project-state-bootstrap/v1/registries/definition-registry.json','sha256':b['sha256']}
                original(archived);relocations.append({'historical_binding':b,'original_byte_archive_binding':archived,'rule':'Same original bytes at explicitly named immutable archive; current mutable lookup remains a different D75 source.'});extra.append(archived)
            else:extra.append(b)
        extra.append(bind(R0))
        require(source_status(extra)['state']=='current','R0 original source material changed')
        if scope_ref=='historical-d73-slice':data=historical_d73(data)
        else:data['selected_admission_epoch']='decision:0075';data['historical_scope']=False
        def guard():
            handle.guard();replay=store.replay(require_current=False);f=replay['freshness'];status=source_status(extra)
            status['changed']+=f.get('changed',[])
            if replay['head']['transaction_digest']!=head:status['changed'].append('actual-selected-query-store-HEAD')
            return status
        data['historical_source_relocations']=relocations
        query_scope=VerifiedScope(data,scope_ref,verified_call(guard,handle.common.RuntimeFault),verified_call(lambda r,p:handle.operations.validate_relation(r,p,allow_historical=True),handle.common.RuntimeFault),_FACTORY,schema_validator=verified_call(lambda r,b,p:handle.sources.validate_schema(r,b['path'],None,p['documents']),handle.common.RuntimeFault))
        try:yield query_scope
        finally:query_scope.close()
    require(not owned.exists(),'owned query store/key remains')


@contextmanager
def native_source_scope():
    """Validate exact O05 carrier/original-event closure and native replay; no import effect."""
    migration=PACKAGE/'migration/adapters';sys.path.insert(0,str(migration));build=module('build',migration/'build.py');check=module('_O03_O05_check',migration/'check.py')
    root=PACKAGE/'migration/candidate/0001';receipt_path=PACKAGE/'receipts/O05/0001.json';require(sha(receipt_path.read_bytes())=='4375c986a84e1be17416517f0a55120895011728877ddee168cb1e7ded7ac562','independent O05 receipt differs');receipt=load(receipt_path);pin=receipt['manifest_binding']
    require(bind(root/'manifest.json')==pin,'independent O05 manifest differs');files=check.load_package(root)
    with build.signed_catalog() as (catalog,operations):
        translator=build.SourceTranslation(catalog,operations);checked=check.validate_payload(files,translator,pin['sha256'],native=False)
        rebuild=load(PACKAGE/'queries/attempts/0001/native-build.json');exe=rebuild['executable_binding'];require(rebuild['status']=='PASS' and sha(Path(exe['path']).read_bytes())==exe['sha256'],'native rebuild differs')
        archive=parse(files['native.snapshot']);require(exe['sha256']==archive['native_executable_sha256'],'native executable semantics not independently pinned')
        native=check.read_native(archive,exe);core=parse(files['core.json']);manifest=parse(files['manifest.json']);index=parse(files['record-index.json'])
        subjects={}
        for row in index:
            v=parse(files[row['path']]);b=bind(root/row['path']);subjects[row['version_ref']]={'identity':row['node_id'],'version_ref':row['version_ref'],'category':'artifact-instance','kind':row['kind'],
                'carrier_ref':row['carrier_ref'],'effective_state':'candidate-unadmitted','source':b,'decision_ref':None,'record':v}
        data={'projection':{'subjects':subjects,'contracts':catalog.projection['contracts'],'relation_contracts':{},'documents':{},'state':None,'histories':{}},
            'baseline':{'materials':{b['path']:b['sha256'] for b in [bind(root/r['path']) for r in manifest['files']]+[pin]},'profile':{'implementation_bindings':[]},'snapshot_digest':digest(core)},
            'head':None,'selected_admission_epoch':'candidate:O05','historical_scope':False,'native_checked':checked,
            'source_translation_profile':translator.profile,'source_profile_binding':core['profile_binding']}
        def guard():
            status=source_status([pin]+[{'path':(root/r['path']).relative_to(ROOT).as_posix(),'sha256':r['sha256']} for r in manifest['files']])
            try:translator.guard()
            except ValueError as error:status['changed'].append('O05-original-source-observation:'+str(error))
            if not Path(exe['path']).is_file() or sha(Path(exe['path']).read_bytes())!=exe['sha256']:status['changed'].append('exact-native-executable')
            return status
        scope=VerifiedScope(data,'O05-source-interpretation',guard,None,_FACTORY,native=native,reconciliation=core['dispositions'],schema_validator=verified_call(lambda r,b,p:operations.validate_schema(r,b['path'],None,catalog.projection['documents']),operations.RuntimeFault))
        try:yield scope
        finally:scope.close()
