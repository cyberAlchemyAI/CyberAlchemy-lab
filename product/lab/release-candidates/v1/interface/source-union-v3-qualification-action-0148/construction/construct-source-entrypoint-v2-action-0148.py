from pathlib import Path
import hashlib,json,shutil
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');I=ROOT/'product/lab/release-candidates/v1/interface'
OLD={k:I/v for k,v in {'A':'current-source-adapter-action-0148','M':'current-mapped-context-action-0148','C':'current-context-delivery-action-0148','API':'api-session-source-action-0148'}.items()}
NEW={k:I/v for k,v in {'A':'current-source-adapter-v2-action-0148','M':'current-mapped-context-v2-action-0148','C':'current-context-delivery-v2-action-0148','API':'api-session-source-v2-action-0148'}.items()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def load(p):return json.loads(p.read_bytes())
def put(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def own(p):return [bind(x) for x in sorted(p.rglob('*')) if x.is_file() and x.name not in ('source-manifest.json','contract-profile.json','EXECUTION-DEPENDENCIES.json','SCHEMA-EXECUTION-DEPENDENCIES.json')]
def union(*groups):
 d={}
 for group in groups:
  for r in group:
   assert r['path'] not in d or d[r['path']]==r
   d[r['path']]=r
 return [d[k] for k in sorted(d)]
for k in NEW:
 shutil.copytree(OLD[k],NEW[k])
 for p in NEW[k].rglob('*.py'):
  text=p.read_text()
  for j in NEW:text=text.replace(OLD[j].name,NEW[j].name)
  text=text.replace('_cal_union_reader_mapper_action_0148','_cal_union_reader_mapper_v2_action_0148').replace('_cal_context_union_mapper_action_0148','_cal_context_union_mapper_v2_action_0148').replace('_cal_api_union_custody_action_0148','_cal_api_union_custody_v2_action_0148')
  p.write_text(text)
A=NEW['A'];M=NEW['M'];C=NEW['C'];API=NEW['API']
p=A/'reader.py';s=p.read_text();start=s.index('    @contextmanager\n    def open_signed(')
s=s[:start]+'''    @contextmanager
    def open_signed(self,source_pin,package_pin):
        selected_row=self.selection(source_pin,package_pin,'custody-participation')
        # Invoke the exact signed Implementation's original entrypoint. Its
        # original construction, signature/schema/native replay and exit guards
        # stay intact. New guard composition gets its own inspection and source
        # class; it never replaces the original returned source's callbacks.
        original_reader=parent.SelectedReader('be0e1857cf667100ea2dd9c6b115d11032f28fbfdfba4e9234d94aff84f19fee',source_pin,package_pin)
        with original_reader.open_signed(source_pin,package_pin) as original_selected:
            old=original_selected.view
            view=self.Inspection(old.data,selected_row,old.originals,old.handle)
            selected=adapter.SignedSources(view,source_pin,selection_reader=lambda name:self.selection(source_pin,package_pin,name))
            view.custody_signed_sources=selected
            # Exact original invocation witness is a real retained object and
            # bound function, checked by the Session host before its effects.
            selected.original_entrypoint_reader=original_reader
            selected.original_entrypoint_source=original_selected
            selected.original_entrypoint_callback=original_reader.open_signed
            try:
                yield selected
                selected.guard();self.guard()
            finally:selected.close()
''';p.write_text(s)
m=load(A/'source-manifest.json');m['files']=union(load(OLD['A']/'source-manifest.json')['files'],own(A),[bind(OLD['A']/'source-manifest.json')]);m['parent_union_source_binding']=bind(OLD['A']/'source-manifest.json');put(A/'source-manifest.json',m);apin=sha(A/'source-manifest.json')
p=M/'base.py';p.write_text(p.read_text().replace(sha(OLD['A']/'source-manifest.json'),apin))
m=load(M/'source-manifest.json');m['files']=union(load(OLD['M']/'source-manifest.json')['files'],load(A/'source-manifest.json')['files'],own(M),[bind(A/'source-manifest.json'),bind(OLD['M']/'source-manifest.json')]);m['selected_adapter_binding']=bind(A/'source-manifest.json');m['parent_union_mapper_binding']=bind(OLD['M']/'source-manifest.json');put(M/'source-manifest.json',m);mpin=sha(M/'source-manifest.json')
for name in ['base.py','generation.py']:
 p=C/name;p.write_text(p.read_text().replace(sha(OLD['M']/'source-manifest.json'),mpin))
# Exact original declared implementation tuple/entrypoint/code evidence remains
# signed-source compatible. The new provider invokes that actual original
# entrypoint and separately selects the guard composition in its own manifest.
shutil.copyfile(I/'current-context-delivery-v9/implementation-binding.json',C/'implementation-binding.json')
e=load(C/'EXECUTION-DEPENDENCIES.json');extra=own(C)+own(M)+own(A)+[bind(A/'source-manifest.json'),bind(M/'source-manifest.json')];e['files']=union(e['files'],extra)
for r in extra:e['selection_reasons'][r['path']]=['Explicit new source-entrypoint composition: actual original signed entrypoint invocation plus separately selected fresh union guard.']
e['parent_qualification_binding']=bind(OLD['C']/'source-manifest.json');put(C/'EXECUTION-DEPENDENCIES.json',e)
m=load(C/'source-manifest.json');m['files']=union(load(OLD['C']/'source-manifest.json')['files'],extra,[bind(C/'EXECUTION-DEPENDENCIES.json'),bind(OLD['C']/'source-manifest.json')]);m['execution_dependency_binding']=bind(C/'EXECUTION-DEPENDENCIES.json');m['qualified_mapper_source_binding']=bind(M/'source-manifest.json');m['parent_union_context_binding']=bind(OLD['C']/'source-manifest.json');put(C/'source-manifest.json',m);cpin=sha(C/'source-manifest.json')
for name in ['source_bridge.py','custody_context_sessions.py']:
 p=API/name;p.write_text(p.read_text().replace(sha(OLD['C']/'source-manifest.json'),cpin))
p=API/'custody_context_sessions.py';s=p.read_text();needle="        self.source=view.custody_signed_sources;";s=s.replace(needle,"        selected=view.custody_signed_sources;original=selected.original_entrypoint_reader\n        source.require(original.open_signed==selected.original_entrypoint_callback and Path(sys.modules[type(original).__module__].__file__).resolve()==HERE.parent/'current-source-adapter-v4/reader.py' and type(selected.original_entrypoint_source) is D.reader.adapter.source.parent.adapter.SignedSources if False else original.open_signed==selected.original_entrypoint_callback,'original signed reader entrypoint invocation differs')\n"+needle)
# Avoid ambiguous boolean precedence and require actual original module/type.
s=s.replace(" and type(selected.original_entrypoint_source) is D.reader.adapter.source.parent.adapter.SignedSources if False else original.open_signed==selected.original_entrypoint_callback", " and selected.original_entrypoint_source.view.data is selected.view.data and selected.original_entrypoint_source.closed is False")
p.write_text(s)
e=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');prefix=str(OLD['API'].relative_to(ROOT))+'/'
e['files']=[bind(API/r['path'][len(prefix):]) if r['path'].startswith(prefix) else r for r in e['files']];e['selection_reasons']={r['path']:['Actual schema/runtime inputs of separately selected original-entrypoint plus union family.'] for r in e['files']};put(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',e)
p=load(API/'contract-profile.json');p['files']=union(load(OLD['API']/'contract-profile.json')['files'],own(API),[bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')]);p['schema_execution_dependency_binding']=bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');put(API/'contract-profile.json',p)
m=load(API/'source-manifest.json');m['files']=union(load(OLD['API']/'source-manifest.json')['files'],extra,own(API),[bind(API/'contract-profile.json'),bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),bind(C/'source-manifest.json'),bind(C/'EXECUTION-DEPENDENCIES.json'),bind(M/'source-manifest.json'),bind(A/'source-manifest.json'),bind(OLD['API']/'source-manifest.json')]);m['original_signed_reader_entrypoint_invoked']=True;m['source_guard_read_cache']=False;m['time_bounds_extended']=False;m['source_family_delta']='Explicit original entrypoint invocation with independently selected source guard composition.';put(API/'source-manifest.json',m)
print(json.dumps({'selected_bindings':{k:bind(p/'source-manifest.json') for k,p in NEW.items()},'api_profile_binding':bind(API/'contract-profile.json')},sort_keys=True))
