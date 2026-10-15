"""Prepare byte-bound postimages only; never write the shared API or frozen packages."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
I=ROOT/'product/lab/release-candidates/v1/interface';API=I/'api-integration-v17'
F=I/'current-session-fixtures-v1-completion-0001';LEG=F/'instances/legacy-diagnostic-0001';CUR=F/'instances/diagnostic-0004'
L='completion-legacy:legacy-diagnostic-0001';S='completion-current-participation:diagnostic-0004'
rows=[];originals={};texts={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(p):return json.loads(p.read_bytes())
def rel(p):return p.relative_to(ROOT).as_posix()
def read(name):
 p=API/name;raw=p.read_bytes();originals[name]=raw;texts[name]=raw.decode();return texts[name]
def replace(name,old,new,count=None):
 n=texts[name].count(old)
 assert n and (count is None or n==count),(name,old,n,count)
 texts[name]=texts[name].replace(old,new)
def output(target,raw,prior=None,category='selector-binding'):
 p=HERE/'postimages'/target.relative_to(ROOT);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(raw)
 if target.suffix=='.py':ast.parse(raw)
 if target.suffix=='.json':json.loads(raw)
 rows.append({'target':rel(target),'preimage_sha256':sha(prior) if prior is not None else None,'postimage':rel(p),'postimage_sha256':sha(raw),'category':category})
def jsonbytes(v):return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
for name in ['source_bridge.py','auth.py','service.py','guarded_candidate.py','machine_auth_scope.py','machine_transport.py','session_attachment.py','source8_catalog.py','fixtures.py','authentication.schema.json','legacy_fixture_selection.py','test_custody_sessions.py','run_session_checks.py','test_termination_boundaries.py','test_current_controls.py','test_custody_api.py','test_machine_transport.py','lesson_selection.py','lesson_application.py'] :read(name)
# New producers are closed exact selections, original producers remain available.
bridge=texts['source_bridge.py']
bridge=bridge.replace("def source_selection(name):\n", "def source_selection(name):\n    if name in (CURRENT_LEGACY_NAME,CURRENT_SOURCE8_NAME):\n        d=current_legacy_delivery() if name==CURRENT_LEGACY_NAME else current_session_fixture_delivery()\n        return d.reader.selection(d.SOURCE_PIN,d.SOURCE_PACKAGE,'custody-participation')\n",1)
start="    row=source_selection(name)\n"
block="""    if name in (CURRENT_LEGACY_NAME,CURRENT_SOURCE8_NAME):
        require(source_repo==ROOT,'current fixture requires exact original repository')
        d=current_legacy_delivery() if name==CURRENT_LEGACY_NAME else current_session_fixture_delivery()
        expected=CURRENT_LEGACY_STORE if name==CURRENT_LEGACY_NAME else CURRENT_SOURCE8_STORE
        with d.reader.open_signed(d.SOURCE_PIN,d.SOURCE_PACKAGE) as selected:
            require(type(selected) is d.reader.adapter.SignedSources and type(selected.view) is d.reader.Inspection
                and selected.source_cut['store_ref']==expected and selected.source_cut['branch_ref']=='branch:'+expected
                and selected.selected['name']=='custody-participation','actual current source class/cut/ABI differs')
            if name==CURRENT_LEGACY_NAME:
                selected.view.legacy_signed_sources=selected;selected.view.legacy_context_producer=d
            else:selected.view.source8_context_producer=d
            selected.view.integrated_reader=d.reader
            yield selected.view
            selected.guard();d.reader.guard()
        return
"""
assert bridge.count(start)>=1;pos=bridge.index(start,bridge.index('def replay_source('));bridge=bridge[:pos+len(start)]+block+bridge[pos+len(start):]
old="require(module is not None and Path(module.__file__).resolve()==HERE.parent/'legacy-session-fixture-reader-v1-action-0148/reader.py'"
new="reader_path=ROOT/CURRENT_LEGACY_READER/'reader.py' if d.HERE==ROOT/CURRENT_LEGACY_CONTEXT else HERE.parent/'legacy-session-fixture-reader-v1-action-0148/reader.py'\n        require(module is not None and Path(module.__file__).resolve()==reader_path"
assert old in bridge;bridge=bridge.replace(old,new,1)
old="folder='source8-lesson-fixture-reader-v4-action-0148' if reader.HERE.name=='source8-lesson-fixture-source-v4-action-0148' else 'current-source-adapter-v7'\n        class_name='FixtureReader' if folder.startswith('source8-lesson-fixture') else 'SelectedReader'\n        require(reader_module is not None and Path(reader_module.__file__).resolve()==HERE.parent/folder/'reader.py'"
new="""if producer.HERE==ROOT/CURRENT_SOURCE8_CONTEXT:
            reader_path=ROOT/CURRENT_SOURCE8_READER/'reader.py';class_name='CurrentFixtureReader'
        else:
            folder='source8-lesson-fixture-reader-v4-action-0148' if reader.HERE.name=='source8-lesson-fixture-source-v4-action-0148' else 'current-source-adapter-v7'
            reader_path=HERE.parent/folder/'reader.py';class_name='FixtureReader' if folder.startswith('source8-lesson-fixture') else 'SelectedReader'
        require(reader_module is not None and Path(reader_module.__file__).resolve()==reader_path"""
assert old in bridge;bridge=bridge.replace(old,new,1)
bridge=bridge.replace("require(name in ('source8-session-participation','source8-lesson-fixture-participation'),", "require(name in ('source8-session-participation','source8-lesson-fixture-participation',CURRENT_SOURCE8_NAME),")
bridge=bridge.replace("def source8_delivery_for(name):\n", "def source8_delivery_for(name):\n    if name==CURRENT_SOURCE8_NAME:return current_session_fixture_delivery()\n",1)
bridge=bridge.replace("def source8_period_path(name):\n", "def source8_period_path(name):\n    if name==CURRENT_SOURCE8_NAME:return ROOT/CURRENT_SOURCE8_SOURCE/'packages/0001/period.json'\n",1)
bridge=bridge.replace("d=legacy_delivery();selected=view.legacy_signed_sources;origin=", "producer=view.legacy_context_producer\n    current=producer.HERE==ROOT/CURRENT_LEGACY_CONTEXT\n    d=current_legacy_delivery() if current else legacy_delivery();selected=view.legacy_signed_sources;origin=",1)
bridge=bridge.replace("selected.source_cut['store_ref']=='R03-legacy-session-fixture-0257'\n        and selected.selected", "selected.source_cut['store_ref']==(CURRENT_LEGACY_STORE if current else 'R03-legacy-session-fixture-0257')\n        and selected.selected",1)
bridge=bridge.replace("def legacy_profile_binding():\n    d=legacy_delivery();", "def legacy_profile_binding(name='legacy-session-fixture'):\n    d=legacy_delivery_for(name);",1)
ld=load(LEG/'runtime/runtime-selection.json');cd=load(CUR/'runtime/runtime-selection.json')
constants={'CURRENT_LEGACY_NAME':L,'CURRENT_SOURCE8_NAME':S,'CURRENT_LEGACY_STORE':load(LEG/'construction-selection.json')['prefix'],'CURRENT_SOURCE8_STORE':load(CUR/'construction-selection.json')['prefix'],'CURRENT_LEGACY_CONTEXT':rel(LEG/'context'),'CURRENT_SOURCE8_CONTEXT':rel(CUR/'context'),'CURRENT_LEGACY_READER':rel(LEG/'reader'),'CURRENT_SOURCE8_READER':rel(CUR/'reader'),'CURRENT_LEGACY_SOURCE':rel(LEG/'source'),'CURRENT_SOURCE8_SOURCE':rel(CUR/'source'),'CURRENT_LEGACY_DELIVERY_PIN':ld['bindings']['context']['sha256'],'CURRENT_SOURCE8_DELIVERY_PIN':cd['context_source_binding']['sha256']}
bridge+='\n\n# Independently captured current technical fixture selections; no old renewal.\n'+''.join(k+'='+repr(v)+'\n' for k,v in constants.items())
bridge+='''
def _current_delivery(name,path,pin):
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
        package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    module=__import__(name+'.build',fromlist=['preflight'])
    require(Path(module.__file__).resolve()==path/'build.py' and module.HERE==path,'current Context producer origin differs')
    scope=module.FACT_SCOPE.active_scope()
    if scope is None:module.preflight(pin)
    else:
        require(scope.producer is module,'foreign current borrowed producer')
        checker=module.preflight if any(check is module.preflight and selected==pin for check,selected in scope.package_checks) else module.verify_source
        module.FACT_SCOPE.package_guard(scope.parent,checker,pin)
    return module
def current_legacy_delivery():return _current_delivery('_cal_api17_current_legacy_diagnostic0001',ROOT/CURRENT_LEGACY_CONTEXT,CURRENT_LEGACY_DELIVERY_PIN)
def current_session_fixture_delivery():return _current_delivery('_cal_api17_current_source8_diagnostic0004',ROOT/CURRENT_SOURCE8_CONTEXT,CURRENT_SOURCE8_DELIVERY_PIN)
def legacy_delivery_for(name):
    require(name in ('legacy-session-fixture',CURRENT_LEGACY_NAME),'unselected legacy family')
    return current_legacy_delivery() if name==CURRENT_LEGACY_NAME else legacy_delivery()
def legacy_period_path(name):
    require(name in ('legacy-session-fixture',CURRENT_LEGACY_NAME),'unselected legacy period family')
    return ROOT/CURRENT_LEGACY_SOURCE/'packages/0001/period.json' if name==CURRENT_LEGACY_NAME else HERE.parent/'legacy-session-fixture-source-v1-action-0148/packages/0001/period.json'
def current_legacy_view(view):
    if not hasattr(view,'legacy_signed_sources'):return False
    if view.legacy_context_producer.HERE!=ROOT/CURRENT_LEGACY_CONTEXT:return False
    return legacy_session_view(view)
def current_source8_view(view):
    if getattr(view,'source8_context_producer',None) is None:return False
    if view.source8_context_producer.HERE!=ROOT/CURRENT_SOURCE8_CONTEXT:return False
    reader_for_view(view);return source8_session_view(view)
'''
texts['source_bridge.py']=bridge
# Fresh legacy has a distinct production module. Original runtime stays intact.
legacy_raw=(API/'legacy_context_sessions.py').read_bytes();legacy=legacy_raw.decode()
legacy=legacy.replace('D=source.legacy_delivery()','D=source.current_legacy_delivery()',1).replace("DELIVERY_PIN='8501857f8219e0f797c323813a2857aa3e78a4b14297b44ebe7b98361102b496'",'DELIVERY_PIN='+repr(constants['CURRENT_LEGACY_DELIVERY_PIN']),1).replace("MAPPING_PIN='ba99b0023708613af17196ff4d5ed3ef9f2e9ddb68de06ab14d374182f5a5b94'",'MAPPING_PIN='+repr(ld['bindings']['mapper_package']['sha256']),1)
legacy=legacy.replace("channel.policy['source_name']=='legacy-session-fixture'", "channel.policy['source_name']==source.CURRENT_LEGACY_NAME").replace("reader_root=HERE.parent/'legacy-session-fixture-reader-v1-action-0148'", "reader_root=ROOT/source.CURRENT_LEGACY_READER").replace('R03-legacy-session-fixture-0257',constants['CURRENT_LEGACY_STORE'])
output(API/'current_legacy_context_sessions.py',legacy.encode(),category='new-exact-legacy-runtime')
for name in ['current_context_sessions.py','current_machine_context_scope.py']:
 output(API/name,(CUR/'runtime/postimages'/name).read_bytes(),category='new-exact-Source8-runtime')
# Closed native Source8 and legacy route selections, retaining all old cases.
for name in ['auth.py','fixtures.py','guarded_candidate.py']:
 replace(name,"('source8-session-participation','source8-lesson-fixture-participation')", "('source8-session-participation','source8-lesson-fixture-participation',source.CURRENT_SOURCE8_NAME)") if "('source8-session-participation','source8-lesson-fixture-participation')" in texts[name] else None
for name in ['auth.py','fixtures.py']:
 replace(name,"('custody-participation','legacy-session-fixture')", "('custody-participation','legacy-session-fixture',source.CURRENT_LEGACY_NAME)")
 replace(name,"source.legacy_delivery() if value['source_name']=='legacy-session-fixture' else source.custody_delivery()" if name=='auth.py' else "source.legacy_delivery() if source_name=='legacy-session-fixture' else source.custody_delivery()", "source.legacy_delivery_for(value['source_name']) if value['source_name'] in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME) else source.custody_delivery()" if name=='auth.py' else "source.legacy_delivery_for(source_name) if source_name in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME) else source.custody_delivery()")
replace('auth.py',"('custody-participation','legacy-session-fixture','source8-session-participation','source8-lesson-fixture-participation')", "('custody-participation','legacy-session-fixture','source8-session-participation','source8-lesson-fixture-participation',source.CURRENT_LEGACY_NAME,source.CURRENT_SOURCE8_NAME)")
replace('auth.py',"period==ROOT/('product/lab/release-candidates/v1/interface/legacy-session-fixture-source-v1-action-0148/packages/0001/period.json' if value['source_name']=='legacy-session-fixture' else 'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json')", "period==(source.legacy_period_path(value['source_name']) if value['source_name'] in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME) else ROOT/'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json')",1)
replace('auth.py',"if self.policy['source_name']=='legacy-session-fixture':", "if self.policy['source_name'] in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME):",1)
replace('auth.py','selected=source.legacy_profile_binding();','selected=source.legacy_profile_binding(self.policy[\'source_name\']);',1)
# Two pure calculation entrypoints select exact new modules with same boundaries.
for name in ['guarded_candidate.py']:
 replace(name,"if name=='legacy-session-fixture':\n        delivery=source.legacy_delivery();runtime=importlib.import_module(__package__+'.legacy_context_sessions')\n        source.require(Path(runtime.__file__).resolve()==HERE/'legacy_context_sessions.py'", "if name in ('legacy-session-fixture',source.CURRENT_LEGACY_NAME):\n        delivery=source.legacy_delivery_for(name);leaf='current_legacy_context_sessions' if name==source.CURRENT_LEGACY_NAME else 'legacy_context_sessions'\n        runtime=importlib.import_module(__package__+'.'+leaf)\n        source.require(Path(runtime.__file__).resolve()==HERE/(leaf+'.py')",2)
 replace(name,"leaf='source8_context_sessions' if name=='source8-session-participation' else 'fixture_context_sessions'", "leaf='current_context_sessions' if name==source.CURRENT_SOURCE8_NAME else 'source8_context_sessions' if name=='source8-session-participation' else 'fixture_context_sessions'",2)
for name in ['service.py','machine_transport.py']:
 replace(name,"'fixture_context_sessions.py','legacy_context_sessions.py'", "'fixture_context_sessions.py','legacy_context_sessions.py','current_context_sessions.py','current_legacy_context_sessions.py'")
replace('service.py',"if source.legacy_session_view(view) and channel.policy['session_control'] is not None:", "if source.current_legacy_view(view) and channel.policy['session_control'] is not None:\n                from .current_legacy_context_sessions import ContextSessions as CurrentLegacyContextSessions\n                self.sessions=CurrentLegacyContextSessions(view,channel,schemas,self.vault)\n            elif source.current_source8_view(view) and channel.policy['session_control'] is not None:\n                from .current_context_sessions import ContextSessions as CurrentContextSessions\n                self.sessions=CurrentContextSessions(view,channel,schemas,self.vault)\n            elif source.legacy_session_view(view) and channel.policy['session_control'] is not None:",1)
replace('service.py',"'legacy_fixture_selection.py','guarded_candidate.py')", "'legacy_fixture_selection.py','guarded_candidate.py','current_context_sessions.py','current_machine_context_scope.py','current_legacy_context_sessions.py')",1)
replace('machine_auth_scope.py',"('custody_context_sessions.py','legacy_context_sessions.py')", "('custody_context_sessions.py','legacy_context_sessions.py','current_legacy_context_sessions.py')",1)
replace('machine_auth_scope.py',"RUNTIMES={\n", "RUNTIMES={\n    'current_context_sessions.py':("+repr(str(CUR.relative_to(I)/'context'))+','+repr(constants['CURRENT_SOURCE8_DELIVERY_PIN'])+'),\n',1)
replace('session_attachment.py',"('source8_context_sessions.py','fixture_context_sessions.py')", "('source8_context_sessions.py','fixture_context_sessions.py','current_context_sessions.py')",1)
replace('source8_catalog.py',"view.source8_context_producer.reader.HERE.name=='source8-lesson-fixture-source-v4-action-0148'", "(view.source8_context_producer.reader.HERE.name=='source8-lesson-fixture-source-v4-action-0148' or source.current_source8_view(view))",1)
# Fresh fixtures use new literals/imports; retained old5 chain function is unchanged.
expect=dict(ld['independently_declared_fixture_expectations']);expect['EXPECTED_READER_ROOT']=(LEG/'reader').relative_to(I).as_posix()
tree=ast.parse(texts['legacy_fixture_selection.py'])
for node in reversed(tree.body):
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in expect:
  key=node.targets[0].id;value=expect[key];line=key+'='+('frozenset('+repr(value)+')' if key=='EXPECTED_RELATION_VERSIONS' else repr(value))
  lines=texts['legacy_fixture_selection.py'].splitlines(keepends=True);lines[node.lineno-1:node.end_lineno]=[line+'\n'];texts['legacy_fixture_selection.py']=''.join(lines)
for name in ['test_custody_sessions.py','run_session_checks.py','test_termination_boundaries.py','test_current_controls.py','test_custody_api.py','test_machine_transport.py']:
 replace(name,'from .legacy_context_sessions import','from .current_legacy_context_sessions import')
# Enums extend only exact admitted technical selectors in the matching policy branch.
schema=load(API/'authentication.schema.json');enum_changes=[]
def walk(v,path=()):
 if isinstance(v,dict):
  if 'source_name' in v.get('properties',{}):
   prop=v['properties']['source_name'];values=prop.get('enum')
   if values is not None:
    before=list(values)
    if 'legacy-session-fixture' in values:values.append(L)
    if 'source8-session-participation' in values:values.append(S)
    if before!=values:enum_changes.append({'pointer':'/'+('/'.join(path+('properties','source_name','enum'))),'before':before,'after':values})
  for k,x in v.items():walk(x,path+(k,))
 elif isinstance(v,list):
  for i,x in enumerate(v):walk(x,path+(str(i),))
walk(schema);texts['authentication.schema.json']=jsonbytes(schema).decode()
# Changed frozen external components become separately named new packages.
for old,new,filename in [('lesson-host-composition-v45-action-0148','lesson-host-composition-v46-completion-0001','host.py'),('lesson-application-v3-action-0148','lesson-application-v4-completion-0001','preparation.py')]:
 for p in sorted((I/old).iterdir()):
  if not p.is_file() or p.name=='source-manifest.json':continue
  raw=p.read_bytes()
  if p.name==filename:
   txt=raw.decode().replace("'source8_context_sessions.py','fixture_context_sessions.py'", "'source8_context_sessions.py','fixture_context_sessions.py','current_context_sessions.py'")
   txt=txt.replace("Path(self.C.__file__).name=='fixture_context_sessions.py'", "Path(self.C.__file__).name in ('fixture_context_sessions.py','current_context_sessions.py')")
   raw=txt.encode()
  output(I/new/p.name,raw,category='new-external-exact-current-runtime-composition')
current_lesson=texts['lesson_selection.py'].replace('lesson-host-composition-v45-action-0148','lesson-host-composition-v46-completion-0001').replace('_lesson_host_v3','_current_lesson_host_v1')
output(API/'current_lesson_selection.py',current_lesson.encode(),category='new-current-only-LessonHost-selector')
current_application=texts['lesson_application.py'].replace('lesson-application-v3-action-0148','lesson-application-v4-completion-0001').replace('_lesson_application_v1','_current_lesson_application_v1')
output(API/'current_lesson_application.py',current_application.encode(),category='new-current-only-application-selector')
replace('service.py','from .lesson_application import LessonApplication', "from .current_lesson_application import LessonApplication if_placeholder",1)
# Select imports inside the existing method; no wrapper or class guard changes.
replace('service.py','        from .current_lesson_application import LessonApplication if_placeholder', "        if self.channel.policy['source_name']==source.CURRENT_SOURCE8_NAME:\n            from .current_lesson_application import LessonApplication\n        else:from .lesson_application import LessonApplication",1)
replace('service.py','                    from .lesson_application import LessonApplicationFailure', "                    if self.channel.policy['source_name']==source.CURRENT_SOURCE8_NAME:\n                        from .current_lesson_application import LessonApplicationFailure\n                    else:from .lesson_application import LessonApplicationFailure",1)
replace('service.py',"                builder=LessonHost(self,{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})", "                if source.current_source8_view(self.handlers.view):\n                    from .current_lesson_selection import LessonHost as CurrentLessonHost\n                    lesson_host_class=CurrentLessonHost\n                else:lesson_host_class=LessonHost\n                builder=lesson_host_class(self,{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})",1)
replace('service.py',"'current_legacy_context_sessions.py')","'current_legacy_context_sessions.py','current_lesson_selection.py','current_lesson_application.py')",1)

# The policy method binding must point to the exact current application helper.
replace('auth.py',"method=HERE.parent/('lesson-application-v3-action-0148' if source8", "method=HERE.parent/('lesson-application-v4-completion-0001' if value['source_name']==source.CURRENT_SOURCE8_NAME else 'lesson-application-v3-action-0148' if source8",1)
for name,txt in texts.items():
 if txt.encode()!=originals[name]:output(API/name,txt.encode(),originals[name])
# Changes to test bodies are bounded: only the two origin constructor methods.
def methods(raw):
 return {c.name+'.'+n.name:ast.dump(n,include_attributes=False) for c in ast.parse(raw).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')}
for name in ['test_custody_sessions.py','run_session_checks.py','test_termination_boundaries.py']:
 old=methods(originals[name]);new=methods(texts[name]);assert set(old)==set(new)
 changed=[k for k in old if old[k]!=new[k]]
 assert changed==(['Sessions.test_23_metadata_does_not_recreate_live_resource'] if name!='test_termination_boundaries.py' else []),(name,changed)
ledger={'schema_version':'lab-T02-closed-integration-patch/v1-candidate','status':'PREPARED-UNAPPLIED-UNQUALIFIED','rows':rows,'schema_enum_changes':enum_changes,'original_source_v16_or_frozen_packages_mutated':False,'original_legacy_runtime_and_period_preserved':True,'sharedAPI17_written':False,'T05_required_coordinator_change':"machine-context-scope-v2-completion-0001 selected() must accept only exact current_legacy_context_sessions.py with its actual class and matchingAPI17module origin, retaining all original owner/peer/resource/permission/source/policy guards.",'runtime_guard_PASS_claimed':False,'qualification_blocker':'25 original global proof paths missing, including5 unrecoveredbyte inputs; coordinator must resolve full source/active closure without dropping original proof rows. This patch does not alter source/profile manifests or claim source guard PASS.','whole_Session_classes_executed':False,'task_complete':False,'authority_effect':'none','actual_owner_outcome':None}
with (HERE/'patch-ledger.json').open('x') as f:json.dump(ledger,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({'result':'PREPARED-UNAPPLIED-UNQUALIFIED','targets':len(rows),'enum_changes':len(enum_changes)}))
