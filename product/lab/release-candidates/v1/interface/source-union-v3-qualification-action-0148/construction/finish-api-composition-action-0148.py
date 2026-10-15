exec(open('/tmp/cal-session-diagnostic-action-0148/construct-source-composition-action-0148.py').read().split('M.mkdir(mode=0o700)')[0].split('# Additional rows')[0])
API=I/'api-session-source-action-0148';M=I/'current-mapped-context-action-0148';C=I/'current-context-delivery-action-0148'
shutil.copytree(I/'api-integration-v7/dependencies',API/'dependencies')
e=load(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');prefix=str((I/'api-integration-v7').relative_to(ROOT))+'/'
e['files']=[bind(API/row['path'][len(prefix):]) if row['path'].startswith(prefix) else row for row in e['files']]
e['files']=files_union(e['files'],[bind(API/'custody_context_sessions.py')]);e['selection_reasons']={r['path']:['Exact real schema/runtime input selected for new source family.'] for r in e['files']};put(API/'SCHEMA-EXECUTION-DEPENDENCIES.json',e)
p=load(API/'contract-profile.json');p['files']=files_union(p['files'],ownfiles(API),[bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json')]);p['schema_execution_dependency_binding']=bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json');put(API/'contract-profile.json',p)
owned=ownfiles(C)+ownfiles(M)+ownfiles(A)+[bind(A/'source-manifest.json'),bind(M/'source-manifest.json')]
m=load(API/'source-manifest.json');m['files']=files_union(m['files'],ownfiles(API),[bind(API/'contract-profile.json'),bind(API/'SCHEMA-EXECUTION-DEPENDENCIES.json'),bind(C/'source-manifest.json'),bind(C/'EXECUTION-DEPENDENCIES.json'),bind(M/'source-manifest.json'),bind(A/'source-manifest.json')],owned);put(API/'source-manifest.json',m)
print(json.dumps({'adapter':bind(A/'source-manifest.json'),'mapper':bind(M/'source-manifest.json'),'context':bind(C/'source-manifest.json'),'api':bind(API/'source-manifest.json'),'profile':bind(API/'contract-profile.json')}))
