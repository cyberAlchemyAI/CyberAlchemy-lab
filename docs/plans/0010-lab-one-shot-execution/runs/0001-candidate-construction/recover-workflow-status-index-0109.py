"""Complete the index step; preserve the predecessor and already written outputs."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v74'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    predecessor=RUN/'R03-CURRENT-PROGRESS-0108.json'
    assert bind(predecessor)['sha256']=='b9f29ce65e5e38467b8bc0ae057ac88804ea1f3b36ce29c7179034e8a19c4938'
    progress=API/'receipts/R03-0109.json';value=json.loads(progress.read_bytes())
    handoff=RUN/'custody-integration-handoff-0094.json';h=json.loads(handoff.read_bytes())
    current=ROOT/h['currentness_binding']['path'];c=json.loads(current.read_bytes())
    status=RUN/'OPERATIONAL-FOUNDATION-STATUS-0109.md'
    assert h['current_progress_binding']==bind(progress) and h['current_status_binding']==bind(status)
    assert h['currentness_binding']==bind(current) and c['result']=='PASS' and c['completed_tasks']==36
    assert value['API74_focused_workflow_qualified']
    index={'schema_version':'lab-current-progress-index/v1-candidate',
        'publisher_binding':bind(RUN/'publish-workflow-status-0109.py'),
        'publisher_recovery_binding':bind(Path(__file__).resolve()),
        'carrier_resolver_design_successor_binding':bind(RUN/'GENERATED-CARRIER-RESOLVER-DESIGN-0002.md'),
        'progress_binding':bind(progress),'currentness_binding':bind(current),
        'status_binding':bind(status),'handoff_binding':bind(handoff),
        'closed_tasks':36,'total_tasks':46,'authored_handlers':21,'unimplemented_operations':13,
        'API71_preparation_selected_qualified':True,'API74_focused_workflow_qualified':True,
        'Machine_read_diagnostic_result':value['Machine_read_diagnostic_result'],
        'whole_API_qualified':False,'authority_effect':'none','task_complete':False,'goal_complete':False}
    path=RUN/'R03-CURRENT-PROGRESS-0109.json'
    with path.open('x') as stream:json.dump(index,stream,indent=2,sort_keys=True);stream.write('\n')
    assert bind(predecessor)['sha256']=='b9f29ce65e5e38467b8bc0ae057ac88804ea1f3b36ce29c7179034e8a19c4938'
    print(json.dumps({'result':'PUBLISHED-SCOPED-PROGRESS','index':bind(path),'status':bind(status)}),flush=True)
if __name__=='__main__':main()
