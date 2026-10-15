"""Author an unfrozen API successor; original producer sources remain immutable."""
import ast,hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
PARENT=ROOT/'product/lab/release-candidates/v1/interface/api-v16';OUT=PARENT.parent/'api-v17'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()
def change(name,old,new):
    p=OUT/name;text=p.read_text();assert old in text,(name,old);p.write_text(text.replace(old,new))
def main():
    assert not OUT.exists();ctx=json.loads((HERE/'context-R03-custody-api-0001.json').read_bytes());assert ctx['strict_coverage']=='PASS'
    for r in ctx['source_bindings']:
        b=r['binding'];assert sha((ROOT/b['path']).read_bytes())==b['sha256'],b['path']
    OUT.mkdir()
    for p in PARENT.rglob('*'):
        rel=p.relative_to(PARENT)
        if any(x in {'__pycache__','observations','receipts'} for x in rel.parts):continue
        if rel.as_posix() in {'source-manifest.json','contract-profile.json','derived-manifest.json'}:continue
        if p.is_file():q=OUT/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    # One lazy package owns all new-source reader, mapper and eligibility objects.
    change('source_bridge.py',"def source_selection(name):\n", "def source_selection(name):\n    if name=='custody-participation':\n        d=custody_delivery();return d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,name)\n")
    change('source_bridge.py',"    row=source_selection(name)\n", "    row=source_selection(name)\n    if name=='custody-participation':\n        d=custody_delivery()\n        with d.reader.open_signed(d.SOURCE_PIN,d.SOURCE_PACKAGE) as selected:\n            selected.view.custody_signed_sources=selected\n            yield selected.view\n            selected.guard()\n        return\n")
    with (OUT/'source_bridge.py').open('a') as f:f.write('''

def custody_delivery():
    """Explicit same-package new-source selection; no bare global reader import."""
    name='_cal_api_v17_custody_context';path=HERE.parent/'custody-context-delivery-v1'
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py','unselected original Context producer')
    module.preflight('0b83d4fc1de04bb34519c9be28167e2b8bc6a2bfa8d0ce15c2b156512c21277c')
    return module

def inspection(data,selected,originals,handle):
    cls=custody_delivery().reader.Inspection if selected['name']=='custody-participation' else Inspection
    return cls(data,selected,originals,handle)

def selected_profile_sha(view):
    return view.handle.manifest['profile_binding']['sha256'] if view.selected['name']=='custody-participation' else PINS.profile_sha256
''')
    # Domain originals are distinct from the catalog declaration representation.
    change('artifact_model.py',"    binding=subject['source']\n", "    if view.selected['name']=='custody-participation':\n        return source.custody_delivery().reader.adapter.model.artifact_ref(view,subject)\n    binding=subject['source']\n")
    change('artifact_model.py',"    report=view.source_record(subject);b=subject['source']\n", "    if view.selected['name']=='custody-participation':\n        return source.custody_delivery().reader.adapter.model.record_bytes(view,subject)\n    report=view.source_record(subject);b=subject['source']\n")
    change('handlers.py',"'source_profile_sha256':source.PINS.profile_sha256", "'source_profile_sha256':source.selected_profile_sha(view)")
    change('handlers.py','source.Inspection(data,view.selected,view.originals,view.handle)','source.inspection(data,view.selected,view.originals,view.handle)')
    change('handlers.py',"        if hasattr(self.view,'fresh_signed_sources'):self.view.fresh_signed_sources.guard()", "        if hasattr(self.view,'custody_signed_sources'):self.view.custody_signed_sources.guard()\n        if hasattr(self.view,'fresh_signed_sources'):self.view.fresh_signed_sources.guard()")
    change('projection.py',"(self.ref,source.sha(compact(cut)),source.PINS.profile_sha256,self.projector_sha", "(self.ref,source.sha(compact(cut)),source.selected_profile_sha(view),self.projector_sha")
    change('projection_refresh.py',"'source_profile_sha256': source.PINS.profile_sha256", "'source_profile_sha256': source.selected_profile_sha(view)")
    # A distinct Session module keeps every former branch's D/EL/R globals intact.
    custody=(OUT/'context_sessions.py').read_text()
    start=custody.index("DELIVERY=HERE.parent/");end=custody.index("CLAIM=",start)
    custody=custody[:start]+'''D=source.custody_delivery()
DELIVERY=D.HERE
DELIVERY_PIN='0b83d4fc1de04bb34519c9be28167e2b8bc6a2bfa8d0ce15c2b156512c21277c'
MAPPING_PIN='fe205340b240838aad5dd3d4cd1a03115b1b9dc4b939358334a0ca4dbd7e6c34'
EL=D.EL;R=D.records
'''+custody[end:]
    custody=custody.replace("hasattr(view,'fresh_signed_sources')","hasattr(view,'custody_signed_sources')").replace('self.source=view.fresh_signed_sources','self.source=view.custody_signed_sources')
    custody=custody.replace("source.require(Path(D.reader.adapter.source.__file__).resolve()==HERE.parent/'api-v12/source_bridge.py' and Path(D.reader.adapter.model.__file__).resolve()==HERE.parent/'api-v12/artifact_model.py','frozen source reader dependency origins differ')", "source.require(D.reader is D.MAPPED.reader and EL is D.reader.adapter.eligibility and Path(D.reader.adapter.source.__file__).resolve()==D.reader.HERE/'base.py' and Path(D.reader.adapter.model.__file__).resolve()==D.reader.HERE/'model.py','explicit original source reader and eligibility selection differs')")
    custody=custody.replace("period['not_before'],v['expires_at']", "period['not_before'],min(v['expires_at'],period['expires_at'],key=instant)")
    (OUT/'custody_context_sessions.py').write_text(custody)
    change('service.py',"from .context_sessions import ContextSessions", "from .context_sessions import ContextSessions\nfrom .custody_context_sessions import ContextSessions as CustodyContextSessions")
    change('service.py',"self.sessions=ContextSessions(view,channel,schemas,self.vault) if hasattr(view,'fresh_signed_sources') else None", "self.sessions=CustodyContextSessions(view,channel,schemas,self.vault) if hasattr(view,'custody_signed_sources') else ContextSessions(view,channel,schemas,self.vault) if hasattr(view,'fresh_signed_sources') else None")
    change('service.py',"'context_sessions.py','source_bridge.py')", "'context_sessions.py','custody_context_sessions.py','source_bridge.py','guard.py')")
    change('service.py',"(HERE/'context_sessions.py').relative_to(ROOT)),(HERE/'context_sessions.py').read_bytes()", "(HERE/('custody_context_sessions.py' if isinstance(self.sessions,CustodyContextSessions) else 'context_sessions.py')).relative_to(ROOT)),(HERE/('custody_context_sessions.py' if isinstance(self.sessions,CustodyContextSessions) else 'context_sessions.py')).read_bytes()")
    # Closed independently provided new-source policy; original scopes preserved.
    schema=json.loads((OUT/'authentication.schema.json').read_bytes())
    def enums(v):
        if isinstance(v,dict):
            if v.get('enum')==['engineering','research','product','reference-corrected','fresh-participation']:v['enum'].append('custody-participation')
            for x in v.values():enums(x)
        elif isinstance(v,list):
            for x in v:enums(x)
    enums(schema);(OUT/'authentication.schema.json').write_bytes(encoded(schema))
    change('auth.py',"        if value['source_name']=='fresh-participation':", "        if value['source_name']=='custody-participation':\n            d=source.custody_delivery();period=d.reader.HERE/'packages/0001/period.json';p=d.load(period)\n            source.require(value['principal_ref']==d.records.PRINCIPAL and control is not None and control['period_binding']==binding(str(period.relative_to(ROOT)),period.read_bytes()),'original participation permission or exact period differs')\n            source.require(instant(p['not_before'])<=now()<instant(value['expires_at'])<=instant(p['expires_at']),'original source host window exceeds retained absolute Assignment interval')\n        elif value['source_name']=='fresh-participation':")
    change('auth.py',"'source_profile_binding':{'ref':'implementation/lab-runtime/v2/profile.json','sha256':profile}", "'source_profile_binding':{'ref':str(source.custody_delivery().reader.HERE.parent.joinpath('custody-correction-v4/runtime/profile.json').relative_to(ROOT)) if self.policy['source_name']=='custody-participation' else 'implementation/lab-runtime/v2/profile.json','sha256':profile}")
    change('fixtures.py',"    if source_name=='fresh-participation':", "    if source_name=='custody-participation':\n        d=source.custody_delivery();period=d.reader.HERE/'packages/0001/period.json';p=d.load(period)\n        source.require(instant(p['not_before'])<=now()<instant(p['expires_at']),'original Assignment period not current')\n        policy['expires_at']=min(now()+timedelta(minutes=30),instant(p['expires_at'])).isoformat()\n        policy['session_control']={'period_binding':binding(str(period.relative_to(ROOT)),period.read_bytes()),'max_session_seconds':900}\n    elif source_name=='fresh-participation':")
    # Original target/schema bytes enter the shape before independent core checks.
    change('candidate.py',"            schemas={}\n", "            schemas={};schema_bytes={}\n")
    change('candidate.py',"                source.require(path not in schemas,'duplicate schema destination');schemas[path]=doc", "                source.require(path not in schemas,'duplicate schema destination');schemas[path]=doc;schema_bytes[path]=raw")
    change('candidate.py',"                record=None;content=target['content'];prior=None", "                record=None;raw=None;content=target['content'];prior=None")
    change('candidate.py',"                core={'decision_ref':meta['decision_ref']", "                if view.selected['name']=='custody-participation':\n                    runtime_target['content']=None if target['operation']=='withdraw' else view.handle.custody.content_entry(raw)\n                core={'decision_ref':meta['decision_ref']")
    change('candidate.py',"            before=view.handle.common.digest(view.data['projection'])", "            if view.selected['name']=='custody-participation':\n                originals={t['version_ref']:view.handle.custody.decode_content(t['content']) for t in runtime_targets if t['operation']!='withdraw'}\n                runtime_proposal=view.handle.custody.with_originals(runtime_proposal,originals,schema_bytes,exact_schema_bytes=True)\n                source.require(runtime_proposal['targets']==runtime_targets,'raw custody changed a previously compared target core')\n            before=view.handle.common.digest(view.data['projection'])")
    # Fixture cores independently cover the same full raw target shape.
    change('example_fixture.py',"    raw=(json.dumps(record,indent=3,ensure_ascii=False)+'\\n').encode();metaraw=source.encoded(metadata);coreraw=view.handle.common.encoded(core)", "    raw=(json.dumps(record,indent=3,ensure_ascii=False)+'\\n').encode();metaraw=source.encoded(metadata)\n    if view.selected['name']=='custody-participation':\n        target['content']=None if operation=='withdraw' else view.handle.custody.content_entry(raw)\n        core['target_digest']=view.handle.common.digest(target)\n    coreraw=view.handle.common.encoded(core)")
    # Schema-profile catalog envelope constants must select this exact map path.
    p=OUT/'schemas/catalog-envelope.schema.json';v=json.loads(p.read_bytes())
    for branch in v['oneOf']:branch['properties']['representation_profile_binding']['const']['ref']=str((OUT/'catalog-representations.json').relative_to(ROOT))
    p.write_bytes(encoded(v))
    derivation={'schema_version':'lab-original-source-api-derivation/v1-candidate','parent_source_binding':{'path':str((PARENT/'source-manifest.json').relative_to(ROOT)),'sha256':sha((PARENT/'source-manifest.json').read_bytes())},'context_binding':{'path':str((HERE/'context-R03-custody-api-0001.json').relative_to(ROOT)),'sha256':sha((HERE/'context-R03-custody-api-0001.json').read_bytes())},'original_operations':34,'implemented_operations':12,'public_operations_added':0,'former_branches_preserved':True,'new_source_name':'custody-participation','authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    (OUT/'derivation.json').write_bytes(encoded(derivation))
    for p in OUT.rglob('*.py'):ast.parse(p.read_bytes())
    print(json.dumps({'result':'AUTHORED-UNFROZEN','root':str(OUT),'source_name':'custody-participation','implemented_operations':12,'original_operations':34}))
if __name__=='__main__':main()
