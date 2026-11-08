"""Pin inherited executed controls to accepted receipts, preserving their scope."""
from pathlib import Path
import sys
import json
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE/'execution'));import support as s
names={'P00':['controls.json'],'P01':['contract-controls.json'],'P02':['layout-equivalence-report.json'],
       'P03':['integration-controls.json'],'P04':['explanation-controls.json'],'P05':['binding-controls.json'],
       'P06':['resource-controls.json','full-bridge-controls.json','transport-controls.json'],
       'P07':['repeatability-controls.json','contract-controls.json'],
       'P08':['publication-controls.json','metadata-controls.json','mapped-controls.json']}
reports=[];receipts=[]
for task,candidates in names.items():
    receipt_path=BASE/task.lower()/'task-acceptance.json';receipt=s.read(receipt_path);s.require(receipt['result']=='accepted','unaccepted '+task)
    receipts.append(s.binding(receipt_path))
    # Every expected digest is taken from the accepted receipt. Alternate file
    # names are discovered in its artifacts, not trusted from current content.
    found=[]
    for ref in receipt['artifacts']:
        p=Path(ref['path'])
        if p.name in candidates:found.append(ref)
    if not found:
        found=[r for r in receipt['artifacts'] if Path(r['path']).parent.name==task.lower() and Path(r['path']).name.endswith('.json') and 'controls' in Path(r['path']).name]
    s.require(found,'no accepted control report '+task)
    unique={r['path']:r for r in found}
    for ref in unique.values():
        report=s.read(s.check(ref));controls=report.get('controls',[])
        if not controls:
            controls=receipt['controls'];control_origin=s.binding(receipt_path)
        else:control_origin=ref
        s.require(controls,'empty accepted controls '+task)
        reports.append({'task':task,'report':ref,'control_origin':control_origin,'controls':controls,'scope':report.get('scope',report.get('method','Exact inherited controls; not newly executed by indexing.'))})
(HERE/'inherited-controls.json').write_text(json.dumps({'result':'pass','source_receipts':receipts,'reports':reports,
    'unique_control_count':len({(r['task'],c['name']) for r in reports for c in r['controls']}),
    'actual_new_kernel_qualifications':0,'method':'Exact accepted reports are reused as executed evidence. No inherited control is reissued as a new live event.',
    'authority_effect':'none'},indent=2)+'\n')
print('Inherited reports indexed:',len(reports),'unique controls:',len({(r['task'],c['name']) for r in reports for c in r['controls']}))
