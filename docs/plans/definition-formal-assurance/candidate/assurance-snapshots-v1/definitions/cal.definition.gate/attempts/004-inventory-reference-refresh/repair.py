from pathlib import Path
import shutil,json,hashlib
u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.gate');a=u/'attempts/004-inventory-reference-refresh';a.mkdir()
names=['current-inventory.json','current-dependency-selection.json','current-dependency-graph.json','inventory-stdout.txt','inventory-stderr.txt','fresh-command-results.json']+[f'fresh-{s}-{k}.txt' for s in ['contract','model','source','profile','dependency','inventory'] for k in ['stdout','stderr']]
rows=[]
for n in names:
 shutil.copyfile(u/n,a/n);rows.append({'path':n,'sha256':hashlib.sha256((a/n).read_bytes()).hexdigest()})
(a/'initial-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
(a/'NOTE.md').write_text('The first six-check replay exited1: contract/model/source/profile/dependency exited0 and inventory exited1 on final fresh JSON comparison. Inventory still referenced the pre-metadata-correction model report. Actual authored models and query results are identical under attempt003. This refresh changes exactly one input_refs digest in current-inventory.json to bind the corrected Gate model-controls report. It changes no source,row,witness,count,graph or checker. Producer stdout remains the actual unchanged bounded-count result. All first replay captures are retained; a new six-check replay will independently test the refreshed report.\n')
old=json.loads((u/'current-inventory.json').read_bytes());new=json.loads(json.dumps(old));relative=str(u/'model-controls.json');rows=[x for x in new['input_refs'] if x['path']==relative];assert len(rows)==1
oldhash=rows[0]['sha256'];newhash=hashlib.sha256((u/'model-controls.json').read_bytes()).hexdigest();assert oldhash!=newhash
assert oldhash==hashlib.sha256((u/'attempts/003-report-metadata-correction/model-controls.json').read_bytes()).hexdigest();rows[0]['sha256']=newhash
oldmodel=json.loads((u/'attempts/003-report-metadata-correction/model-controls.json').read_bytes());current=json.loads((u/'model-controls.json').read_bytes());assert oldmodel['results']==current['results'] and oldmodel['nonentailment_countermodels']==current['nonentailment_countermodels']
assert {k:v for k,v in old.items() if k!='input_refs'}=={k:v for k,v in new.items() if k!='input_refs'}
(u/'current-inventory.json').write_text(json.dumps(new,indent=2,sort_keys=True)+'\n')
for n in names:
 if n.startswith('fresh-'):(u/n).unlink()
shutil.copyfile('/tmp/repair_gate_inventory_binding.py',a/'repair.py')
print('One inventory model-report reference refreshed; failed replay preserved')
