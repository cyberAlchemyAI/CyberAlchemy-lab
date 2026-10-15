"""Read-only plan/source consistency checks; imports no Lab implementation."""
from pathlib import Path
import ast
import collections
import hashlib
import json
import re
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check():
    dag=json.loads((HERE/'dag.json').read_text())
    units=json.loads((HERE/'swu-manifest.json').read_text())['units']
    base=json.loads((HERE/'SOURCE-BASELINE.json').read_text())
    coverage=json.loads((HERE/'coverage.json').read_text())
    cross=json.loads((HERE/'obligation-crosswalk.json').read_text())
    findings=json.loads((HERE/'finding-crosswalk.json').read_text())['findings']
    problems=[]
    def require(ok, message):
        if not ok:problems.append(message)
    nodes={t['id']:t for t in dag['nodes']}
    require(len(nodes)==len(dag['nodes'])==dag['node_count'],'unique node accounting')
    declared={(e['from'],e['to']) for e in dag['edges']}
    expected={(d,t['id']) for t in dag['nodes'] for d in t['depends_on']}
    require(declared==expected and len(declared)==len(dag['edges'])==dag['edge_count'],'unique exact dependency edges')
    require(all(a in nodes and b in nodes for a,b in declared),'known edge endpoints')
    todo=set(nodes);order=[]
    while todo:
        ready=sorted(t for t in todo if set(nodes[t]['depends_on'])<=set(order))
        if not ready:problems.append('cycle in DAG');break
        order+=ready;todo-=set(ready)
    require(set(nodes['T15']['depends_on']).isdisjoint({'T10','T11','T12','T13'}),'technical freeze directly overblocked by target semantics')
    ancestors=set();todo=list(nodes['T15']['depends_on'])
    while todo:
        ident=todo.pop()
        if ident in ancestors:continue
        ancestors.add(ident);todo+=nodes[ident]['depends_on']
    require(not ancestors.intersection({'T10','T11','T12','T13'}),'technical freeze indirectly overblocked by target semantics')
    require(nodes['T01']['depends_on']==['T00'],'Machine diagnostic independent of Source8 construction')
    require('T02' in nodes['T35']['depends_on'],'current Source8 construction precedes Source8 diagnostics')
    unitmap={u['id']:u for u in units}
    require(len(unitmap)==len(units),'unique SWUs')
    for t in nodes.values():
        require((HERE/t['contract_path']).is_file(),'missing task contract '+t['id'])
        require(t['status']=='not-started' and t['authority_effect']=='none','false execution status '+t['id'])
        require(all(t.get(k) for k in ['source_anchors','prospective_modules','inputs','ordered_rules','acceptance_evidence','failure_modes','reviewable_check','original_tasks','acceptance_conditions','swu_ids']),'incomplete task detail '+t['id'])
        for p in t['source_anchors']:require((ROOT/p).is_file(),'missing source '+p)
        for ident in t['swu_ids']:
            require(ident in unitmap,'missing SWU '+ident)
            if ident in unitmap:
                u=unitmap[ident]
                require(u['parent_task']==t['id'],'SWU parent '+ident)
                require(u['depends_on']==[f'SWU-{d}-01' for d in t['depends_on']],'SWU dependency mismatch '+ident)
                require(all(u.get(k) for k in ['source_anchors','related_context','write_scope','inputs','ordered_rules','done_criteria','failure_modes','validation_surface','execution_owner','handoff_status']),'incomplete SWU '+ident)
    require({u['parent_task'] for u in units}==set(nodes),'orphan/missing SWU parents')
    original=json.loads((ROOT/'docs/plans/0010-lab-one-shot-execution/dag.json').read_text())
    original_units=json.loads((ROOT/'docs/plans/0010-lab-one-shot-execution/swu-manifest.json').read_text())['units']
    require([x['full_original_node'] for x in cross['tasks']]==original['nodes'],'original task bodies not exactly preserved')
    require(cross['original_units']==original_units,'original SWU bodies not exactly preserved')
    require(cross['original_task_count']==len(original['nodes'])==46,'original46 tasks')
    require(cross['original_swu_count']==len(original_units)==63,'original63 SWUs')
    for row in cross['tasks']:
        require(bool(row['completion_tasks']) and set(row['completion_tasks'])<=set(nodes),'unmapped original obligation '+row['original_id'])
    require({c for t in nodes.values() for c in t['acceptance_conditions']}=={f'AC{i:02d}' for i in range(1,14)},'all13 acceptance conditions')
    require({r['operation'] for r in coverage['operations']}==set(base['operations']) and len(coverage['operations'])==34,'all34 operation coverage')
    require(len(coverage['areas'])==10 and len({x['area'] for x in coverage['areas']})==10,'all ten implementation areas')
    for op in coverage['operations']:
        require((ROOT/op['implementation_anchor']).is_file(),'operation source '+op['operation'])
        require(set(op['completion_tasks'])<=set(nodes),'operation task map '+op['operation'])
    require(len({f['id'] for f in findings})==len(findings)==33,'all33 audit findings')
    for f in findings:require(bool(f['completion_tasks']) and set(f['completion_tasks'])<=set(nodes),'finding mapped '+f['id'])
    checked_sources=0
    for row in base['api_python_files']+base['existing_tracked_dirty_files']:
        require((ROOT/row['path']).is_file() and digest(ROOT/row['path'])==row['sha256'],'changed selected/preserved bytes '+row['path']);checked_sources+=1
    for area in json.loads((HERE/'analysis/source-inventory.json').read_text())['areas']:
        require(area['source_file_count']==len(area['files']),'area source accounting '+area['area'])
        for row in area['files']:
            require((ROOT/row['path']).is_file() and digest(ROOT/row['path'])==row['sha256'],'changed implementation source '+row['path']);checked_sources+=1
    for row in json.loads((HERE/'sources.json').read_text())['files']:
        require((ROOT/row['path']).is_file() and digest(ROOT/row['path'])==row['sha256'],'changed audit source/evidence '+row['path']);checked_sources+=1
    require(digest(ROOT/base['api_directory']/'source-manifest.json')==base['source_sha256'],'API16 source manifest changed')
    require(digest(ROOT/base['api_directory']/'contract-profile.json')==base['profile_sha256'],'API16 contract profile changed')
    links=0
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            target=target.strip('<>').split('#',1)[0]
            if not target or re.match(r'^[a-z]+://',target):continue
            target=re.sub(r':\d+(?:[-–]\d+)?$','',unquote(target))
            resolved=Path(target) if target.startswith('/') else p.parent/target
            require(resolved.exists(),'broken link '+str(p.relative_to(HERE))+' -> '+target);links+=1
    for p in HERE.rglob('*.json'):
        try:json.loads(p.read_text())
        except Exception:problems.append('invalid JSON '+str(p.relative_to(HERE)))
    for p in HERE.glob('*.py'):ast.parse(p.read_text())
    secret_markers=['-----BEGIN PRIVATE KEY-----','-----BEGIN RSA PRIVATE KEY-----','-----BEGIN OPENSSH PRIVATE KEY-----','-----BEGIN EC PRIVATE KEY-----']
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in {'.json','.md'}:
            require(not any(s in p.read_text() for s in secret_markers),'private key marker '+str(p.relative_to(HERE)))
    return {'schema_version':'lab-runtime-plan-validation/v1-candidate','result':'PASS' if not problems else 'FAIL','problems':problems,'nodes':len(nodes),'edges':len(declared),'swus':len(units),'topological_order':order,'original_tasks_preserved':46,'original_swus_preserved':63,'acceptance_conditions':13,'operations':34,'implementation_areas':10,'audit_findings_mapped':len(findings),'existing_sources_hash_checked':checked_sources+2,'local_links_checked':links,'no_new_runtime_tests':True,'runtime_qualified_by_this_check':False,'authority_effect':'none'}

if __name__=='__main__':
    report=check()
    (HERE/'validation.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))
    raise SystemExit(0 if report['result']=='PASS' else 1)
