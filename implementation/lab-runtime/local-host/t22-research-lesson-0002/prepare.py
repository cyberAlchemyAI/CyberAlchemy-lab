"""Derive a new candidate from the retained actual W04 timeout; no admission."""
from datetime import datetime,timedelta,timezone
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import consumer as C
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
INPUT=ROOT/'implementation/lab-runtime/local-host/t31-workflow-stream-0002/run-0001/research'
COUNTER=ROOT/'implementation/lab-runtime/local-host/t31-workflow-stream-0001/run-0001/research'
def write(path,value):
    raw=C.encoded(value);descriptor=__import__('os').open(path,__import__('os').O_WRONLY|__import__('os').O_CREAT|__import__('os').O_EXCL,0o600)
    with __import__('os').fdopen(descriptor,'wb') as stream:stream.write(raw);stream.flush();__import__('os').fsync(stream.fileno())
def main():
    observed=json.loads((INPUT/'observed.json').read_bytes());assessment=json.loads((INPUT/'assessment.json').read_bytes())
    labels=[C.label(t) for t in observed['trials']]
    C.require(labels==assessment['labels']==['parity','parity','timeout'],'retained actual research failure differs')
    bindings=[{'path':str((INPUT/name).relative_to(ROOT)),'sha256':C.sha((INPUT/name).read_bytes())} for name in ('observed.json','assessment.json','research-run.json','measurement-result.json','experiment-run.json','observation.json')]
    bindings.extend({'path':str((COUNTER/name).relative_to(ROOT)),'sha256':C.sha((COUNTER/name).read_bytes())} for name in ('observed.json','assessment.json','research-run.json','measurement-result.json','experiment-run.json','observation.json'))
    body=json.loads((ROOT/'authority/artifact-types/operational-lesson/v1/fixtures/valid/record.json').read_bytes())
    body.update(node_id='operational-lesson:T22-preserve-inconclusive-W04',name='Include the observed timeout in the finite W04 research population',owner_ref='principal:repository-owner@candidate.1',scope_ref=C.PROJECT,relation_refs=[{'relation_kind_ref':'relation.derives-from','direction':'source','counterpart_kind':'observation','counterpart_ref':json.loads((INPUT/'observation.json').read_bytes())['node_id']}],evidence_refs=['evidence:T22-observed-W04-timeout'],claim_ceiling='Reviewed private candidate procedure for exact recorded W04 sample reanalysis only; no Source currentness, admission or causal performance improvement.')
    body['payload'].update(lesson_statement=C.RULE,applicability='Only the two exact independently pinned historical W04 cohorts, each with three replay pairs in this Project; analyze each separately without pooling.',exclusions=['other studies or cohorts','pooling the two historical cohorts','timing entropy','Source-current Lesson selection','protected source authority','causal performance or population inference'],predicted_benefit='Keep all three declared samples and the observed timeout visible in the analysis instead of dropping the incomplete pair.',falsifier='The later procedure omits the timeout, analyzes fewer than three declared pairs, or fails to reproduce the independently recomputed finite label entropy.',expires_at=(datetime.now(timezone.utc)+timedelta(hours=6)).isoformat(),retention_policy_ref='protocol:T22-local-candidate-input-retention',scope_refs=[C.PROJECT],status='candidate',classification_assignment_refs=[],evidence_refs=['evidence:T22-observed-W04-timeout'],counterevidence_refs=['counterevidence:W04-small-confounded-historical-sample'])
    provenance={'schema_version':'lab-T22-genuine-research-Lesson-provenance/v1-candidate','source_inputs':bindings,'actual_failure':{'sample':3,'direct_posture':'timeout','direct_seconds':observed['trials'][2]['observations']['direct']['seconds'],'direct_limit_seconds':45,'facade_seconds':observed['trials'][2]['observations']['facade']['seconds']},'generator_binding':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':C.sha(Path(__file__).read_bytes())},'consumer_binding':{'path':str((HERE/'consumer.py').relative_to(ROOT)),'sha256':C.sha((HERE/'consumer.py').read_bytes())},'candidate_lesson_sha256':C.sha(C.encoded(body)),'created_at':datetime.now(timezone.utc).isoformat(),'counterevidence':['The separate all-parity cohort has zero label entropy but a negative timing result; entropy cannot establish performance improvement.','Three historical pairs only, with one timeout; no current performance or population estimate.','Completed pair timings and order are confounded; a finite label entropy is not timing entropy.','The ablation shows information inclusion changes, not broad or causal Lesson effectiveness.'],'authority_effect':'none'}
    sys.path.insert(0,'/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001/deps')
    from jsonschema import Draft202012Validator
    Draft202012Validator(json.loads((ROOT/'authority/artifact-types/operational-lesson/v1/schema.json').read_bytes())).validate(body)
    write(HERE/'candidate-lesson.json',body);write(HERE/'provenance.json',provenance)
    print(json.dumps({'result':'PREPARED-real-failure-derived-candidate','lesson_sha256':C.sha(C.encoded(body)),'failure_sample':3,'not_yet_reviewed_or_applied':True}))
if __name__=='__main__':main()
