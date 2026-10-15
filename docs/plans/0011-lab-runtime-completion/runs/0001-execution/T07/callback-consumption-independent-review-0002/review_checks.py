"""Passive independent review: metadata and AST only, no runtime imports."""
from pathlib import Path
import ast, hashlib, json, os, runpy, shutil

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
C=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/callback-consumption-closure-0002'
checks=[]
def need(ok,label):
    if not ok: raise AssertionError(label)
    checks.append(label)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(name):return (ROOT/name).read_bytes()
def load(name):return json.loads(read(name))
def pin(row):
    raw=read(row['path']);need(sha(raw)==row['sha256'],'pin '+row['path'])
    if 'size_bytes'in row:need(len(raw)==row['size_bytes'],'size '+row['path'])
    return raw
def fdmap():
    out={}
    for name in os.listdir('/proc/self/fd'):
        try:out[name]=os.readlink('/proc/self/fd/'+name)
        except FileNotFoundError:pass
    return out

before=fdmap()
need(sha((C/'HANDOFF.json').read_bytes())=='71cd1fabc52c1e0e3438d6e8c3a09422c722ab9d077b0f992e7c4522f17dc485','frozen HH')
need(sha((C/'source-manifest.json').read_bytes())=='19b3b763ac061d1ee65233a10e9a96e90fa79fe641b0ce0e83cb91bcff3303cb','frozen MF')
manifest=json.loads((C/'source-manifest.json').read_bytes())
for row in manifest['files']:pin(row)
external=json.loads((C/'external-inputs.json').read_bytes())
for row in external['bindings']:pin(row)
report=json.loads((C/'report.json').read_bytes());audit=json.loads((C/'table-audit.json').read_bytes())
union=json.loads(pin(report['union_binding']));targets=union['rows']
need(isinstance(targets,list),'union targets list')
target_names={r['target'] for r in targets}
need(len(target_names)==38,'38 unique targets')
generated={str(Path('product/lab/release-candidates/v1/interface/api-integration-v17')/n) for n in ('source-manifest.json','contract-profile.json','SCHEMA-EXECUTION-DEPENDENCIES.json','INPUT-ACCOUNTING.json')}
ten_total=0
for row in audit['primary_ten_tables']:
    doc=json.loads(pin(row['binding']));rows=doc['files'];ten_total+=len(rows)
    need(len(rows)==row['row_count'],'row count '+row['binding']['path'])
    need(not ({r['path'] for r in rows}&(target_names|generated)),'ten-table target exclusion '+row['binding']['path'])
need(ten_total==59255,'59255 ten flat rows')
for row in audit['additional_explicit_integrated_workflow_tables']:
    doc=json.loads(pin(row['binding']));need(len(doc['files'])==row['row_count'],'extra count '+row['binding']['path'])
    need(not ({r['path'] for r in doc['files']}&(target_names|generated)),'extra target exclusion '+row['binding']['path'])
api12=json.loads(pin(audit['api12_profile']['binding']))
need(len(api12['files'])==22976,'API12 rows22976')
need(not({r['path'] for r in api12['files']}&(target_names|generated)),'API12 target exclusion')
for key in ('engine','explicit_parent'):
    doc=json.loads(pin(audit['engine_flat_tables'][key]))
    need(not({r['path'] for r in doc['files']}&(target_names|generated)),'engine target exclusion '+key)
anchors=json.loads((C/'source-anchors.json').read_bytes())['anchors']
need(len(anchors)==22,'22 anchors')
for row in anchors:
    raw=pin(row['binding']);tree=ast.parse(raw)
    
    if row['symbol']=='MAPPING_PATH/MAPPING_SHA/PROPOSAL_PATH/PROPOSAL_SHA':
        need(all(any(isinstance(n,ast.Assign) and n.lineno>=12 and n.end_lineno<=15 and any(isinstance(t,ast.Name) and t.id==name for t in n.targets) for n in tree.body) for name in row['symbol'].split('/')),'mapping literal AST anchors corrected12-15');continue
    name=row['symbol'].split(' (')[0].split('.')[-1]
    matches=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name and n.lineno==row['line'] and n.end_lineno==row['end_line']]
    need(len(matches)==1,'AST anchor '+row['symbol'])
profile=json.loads(pin(report['profile_binding']));schema=json.loads(pin(report['schema_execution_binding']))
old={r['target']:r for r in targets if r['preimage_binding'] is not None}
need(len(old)==6,'six replace-existing targets')
for doc,kind in ((profile,'profile'),(schema,'schema')):
    rows={r['path']:r for r in doc['files']}
    for name,row in old.items():
        pre=row['preimage_binding']
        need(pre is not None and rows[name]['sha256']==pre['sha256'],'real affected '+kind+' '+name)
original=json.loads((C/'baseline-selector-paths.json').read_bytes())
need(len(original['names'])==788 and len(original['metadata_documents'])==725,'successor recorded788/725')
for name,expected in original['metadata_documents'].items():
    need(not name.endswith('.snapshot'),'public metadata only')
    need(sha(read(name))==expected,'public selector pin '+name)
copy=HERE/'public_selector_paths.py';copy.write_bytes((C/'public_selector_paths.py').read_bytes())
runpy.run_path(str(copy),run_name='__main__')
reproduced=json.loads((HERE/'baseline-selector-paths.json').read_bytes())
need(reproduced==original,'original enumerator reproduced exactly')
source='product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/lab_runtime/endpoint_mapping.py'
vals={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(read(source)).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('MAPPING_PATH','MAPPING_SHA','PROPOSAL_PATH','PROPOSAL_SHA')}
mapping=json.loads(pin({'path':vals['MAPPING_PATH'],'sha256':vals['MAPPING_SHA']}));pin({'path':vals['PROPOSAL_PATH'],'sha256':vals['PROPOSAL_SHA']})
extension={vals['MAPPING_PATH'],vals['PROPOSAL_PATH']}
for row in mapping['mappings']:
    for key in ('schema_binding','descriptor_binding'):
        pin(row[key]);extension.add(row[key]['path'])
missing=sorted(extension-set(original['names']))
need(missing==[],'complete capture extension selected')
old_names=set(json.loads((C.parent/'callback-consumption-closure-0001/baseline-selector-paths.json').read_bytes())['names'])
need(sorted(set(original['names'])-old_names)==['implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json','product/lab/release-candidates/v1/interface/coupling/engine/endpoint-mapping.json'],'exact two additions')
need(old_names<=set(original['names']),'old selectors all conserved')
need(not (extension&(target_names|generated)),'omitted extension does not touch exact union')
for row in manifest['files']:pin(row)
need(before==fdmap(),'exact FD map unchanged')
result={'result':'PASS-scoped-inactive-original-union38-only','checks_passed':len(checks),'checks':checks,'FD_delta':0,'original_enumerator_reproduced':True,'missing_actual_capture_extension':missing,'complete_public_selector_counts':{'logical_paths':788,'public_metadata_documents':725},'actual_runtime_guards_Source_callbacks_archives_leases_invoked':False,'authority_effect':'none'}
(HERE/'checks-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},sort_keys=True))
