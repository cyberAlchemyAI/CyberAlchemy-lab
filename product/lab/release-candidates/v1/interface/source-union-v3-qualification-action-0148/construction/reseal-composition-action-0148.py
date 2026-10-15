exec(open('/tmp/cal-session-diagnostic-action-0148/construct-source-composition-action-0148.py').read().split('M.mkdir(mode=0o700)')[0].split('# Additional rows')[0])
API=I/'api-session-source-action-0148';M=I/'current-mapped-context-action-0148';C=I/'current-context-delivery-action-0148'
def refresh(p,files):
 d={r['path']:r for r in files}
 for r in ownfiles(p):d[r['path']]=r
 return [d[k] for k in sorted(d)]
p=A/'adapter.py';s=p.read_text();
if 'ROOT=source.ROOT' not in s:p.write_text(s.replace('source=parent.adapter.source;', 'source=parent.adapter.source;ROOT=source.ROOT;'))
oldapin=sha(A/'source-manifest.json');m=load(A/'source-manifest.json');m['files']=refresh(A,m['files']);put(A/'source-manifest.json',m);apin=sha(A/'source-manifest.json')
p=M/'base.py';p.write_text(p.read_text().replace(oldapin,apin))
oldmpin=sha(M/'source-manifest.json');m=load(M/'source-manifest.json');m['selected_adapter_binding']=bind(A/'source-manifest.json');m['files']=refresh(M,m['files']);d={r['path']:r for r in m['files']};d.update({r['path']:r for r in load(A/'source-manifest.json')['files']});d[bind(A/'source-manifest.json')['path']]=bind(A/'source-manifest.json');m['files']=[d[k] for k in sorted(d)];put(M/'source-manifest.json',m);mpin=sha(M/'source-manifest.json')
for name in ['base.py','generation.py']:
 p=C/name;p.write_text(p.read_text().replace(oldmpin,mpin))
oldcpin=sha(C/'source-manifest.json');m=load(C/'source-manifest.json');e=load(C/'EXECUTION-DEPENDENCIES.json');e['files']=refresh(C,e['files']);d={r['path']:r for r in e['files']}
for r in [*ownfiles(A),*ownfiles(M),bind(A/'source-manifest.json'),bind(M/'source-manifest.json')]:d[r['path']]=r
e['files']=[d[k] for k in sorted(d)];put(C/'EXECUTION-DEPENDENCIES.json',e)
m['files']=refresh(C,m['files']);d={r['path']:r for r in m['files']};d.update({r['path']:r for r in e['files']});d[bind(C/'EXECUTION-DEPENDENCIES.json')['path']]=bind(C/'EXECUTION-DEPENDENCIES.json');m['files']=[d[k] for k in sorted(d)];m['execution_dependency_binding']=bind(C/'EXECUTION-DEPENDENCIES.json');m['qualified_mapper_source_binding']=bind(M/'source-manifest.json');put(C/'source-manifest.json',m);cpin=sha(C/'source-manifest.json')
for name in ['source_bridge.py','custody_context_sessions.py']:
 p=API/name;p.write_text(p.read_text().replace(oldcpin,cpin))
e=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');e['files']=[bind(ROOT/r['path']) if r['path'].startswith(str(API.relative_to(ROOT))+'/') else r for r in e['files']];put(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',e)
p=load(API/'contract-profile.json');p['files']=refresh(API,p['files']);d={r['path']:r for r in p['files']};d[bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')['path']]=bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');p['files']=[d[k] for k in sorted(d)];p['schema_execution_dependency_binding']=bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');put(API/'contract-profile.json',p)
m=load(API/'source-manifest.json');d={r['path']:r for r in m['files']}
for folder in [A,M,C,API]:
 for r in ownfiles(folder)+[bind(folder/'source-manifest.json') if folder!=API else bind(API/'contract-profile.json')]:d[r['path']]=r
for p in [C/'EXECUTION-DEPENDENCIES.json',API/'SCHEMA-EXECUTION-DEPENDENCIES.json']:d[bind(p)['path']]=bind(p)
m['files']=[d[k] for k in sorted(d)];put(API/'source-manifest.json',m)
print(json.dumps({'adapter':bind(A/'source-manifest.json'),'mapper':bind(M/'source-manifest.json'),'context':bind(C/'source-manifest.json'),'api':bind(API/'source-manifest.json'),'profile':bind(API/'contract-profile.json')}))
