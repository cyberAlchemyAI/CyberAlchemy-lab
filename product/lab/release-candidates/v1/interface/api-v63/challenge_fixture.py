"""Actual signed-source challenger; fresh explicitly owned candidate workspace."""
import copy
from contextlib import contextmanager
from datetime import timedelta
import json
from pathlib import Path
import tempfile
import uuid
from . import protocol as P,artifact_model as M,workspace as W,auth as A,fixtures as F,handlers as H
from .service import Service
from .challenge_submission import eligibility_bytes
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def pick(view,kind,identity=None):
    rows=[s for s in view.subjects.values() if s['kind']==kind and s['effective_state'] in ('admitted-current','local-admitted-current')
        and (identity is None or s['identity']==identity)]
    P.source.require(rows,'actual current challenge fixture source missing: '+kind+':'+str(identity))
    return sorted(rows,key=lambda s:s['version_ref'])[0]
def current_body(view,subject):return M.record_bytes(view,subject)[0]
@contextmanager
def example(view,schemas,*,grant_challenge=True):
    contract=pick(view,'challenge-contract','challenge-contract:cyberalchemy-lab-operational-foundation')
    challenger=pick(view,'principal','principal:repository-owner');subject=pick(view,'work');project=pick(view,'project')
    project_header=M.artifact_ref(view,project)
    contract_header=M.artifact_ref(view,contract);challenger_header=M.artifact_ref(view,challenger);subject_header=M.artifact_ref(view,subject)
    contract_body=P.frame_parse(current_body(view,contract));payload=contract_body['payload']
    receipt_path=HERE.parent/'checkpoint-owner-verification-v3/receipts/checks-0001.json'
    receipt_raw=receipt_path.read_bytes();receipt_binding=P.binding(str(receipt_path.relative_to(ROOT)),receipt_raw)
    accepted=[];materials={}
    header=subject_header;raw=current_body(view,subject);binding=P.binding(header['version_ref'],raw)
    accepted.append({'kind':'source','binding':binding,'artifact':header,'receipt_binding':None,'original_binding':None,'source_posture':'signed-source'});materials[binding['ref']]=raw
    evidence=P.frame_parse((ROOT/'authority/artifact-types/evidence-set/v1/fixtures/valid/record.json').read_bytes())
    evidence.update(node_id='evidence-set:R03-new-challenge:'+uuid.uuid4().hex,scope_ref=view.data['config']['scope_ref'],
        owner_ref=challenger['identity'],evidence_refs=[binding['ref'],receipt_binding['ref']],
        relation_refs=[{'relation_kind_ref':'relation.member-of','counterpart_kind':'project',
            'counterpart_ref':project_header['version_ref'],'direction':'source'}],successor_refs=[],
        claim_ceiling='New unadmitted Evidence Set collects exact inputs. No ground adjudication, source admission or actual owner outcome.')
    evidence['payload'].update(item_refs=[binding['ref'],receipt_binding['ref']],source_refs=[binding['ref']],
        coverage_statement='Exact challenged original and independently executed rule receipt; no finding of factual ground validity.',
        limitations=['Candidate unadmitted collection','Receipt proves its own rule scope only','Owner adjudication remains pending'])
    raw=(json.dumps(evidence,indent=3)+'\n').encode();version=evidence['node_id']+'@evidence.candidate.1'
    header={'scope_ref':view.data['config']['scope_ref'],'identity_ref':evidence['node_id'],'version_ref':version,
        'carrier_ref':'cal.artifact-type.evidence-set/v1','byte_sha256':P.source.sha(raw)};binding=P.binding(version,raw)
    accepted.append({'kind':'evidence-set','binding':binding,'artifact':header,'receipt_binding':None,'original_binding':None,'source_posture':'candidate-original'});materials[binding['ref']]=raw
    decision_path=ROOT/'authority/admissions/governance-transaction-surface/v1/instances/governance/decisions/decision-0074a.json'
    raw=decision_path.read_bytes();binding=P.binding(str(decision_path.relative_to(ROOT)),raw)
    accepted.append({'kind':'decision','binding':binding,'artifact':None,'receipt_binding':None,
        'original_binding':{'path':str(decision_path.relative_to(ROOT)),'sha256':P.source.sha(raw)},'source_posture':'bound-original'});materials[binding['ref']]=raw
    accepted.append({'kind':'validation-receipt','binding':receipt_binding,'artifact':None,
        'receipt_binding':{'path':str(receipt_path.relative_to(ROOT)),'sha256':P.source.sha(receipt_raw)},'original_binding':None,'source_posture':'completed-validation'})
    materials[receipt_binding['ref']]=receipt_raw
    now=A.now();expires=now+timedelta(hours=2);ground='scope-error';cut=H.cut(view)
    routing={'schema_version':'lab-independent-challenge-submit-routing/v1-candidate',
        'principal_ref':challenger['identity'],'storage_scope_ref':view.data['config']['scope_ref'],
        'candidate_scope_ref':view.data['config']['scope_ref'],'challenge_contract':contract_header,'challenger':challenger_header,
        'evidence_project':project_header,
        'source_cut':cut,'subjects':[subject_header],'grounds':[ground],'accepted_evidence':accepted,
        'policy_ref':payload['policy_ref'],'owner_route':payload['owner_route'],'resolution_gate_ref':payload['resolution_gate_ref'],
        'residue_route_ref':payload['unresolved_residue_route'],'response_mode':'evidence',
        'not_before':(now-timedelta(seconds=60)).isoformat(),'expires_at':expires.isoformat(),'revoked':False,
        'development_authorization_binding':P.binding('docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json',
            (ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json').read_bytes()),
        'actual_owner_outcome':None,'authority_effect':'none'}
    event=copy.deepcopy(P.frame_parse((ROOT/'authority/artifact-types/challenge-event/v1/fixtures/valid/record.json').read_bytes()))
    event.update(node_id='challenge-event:R03-actual-source:'+uuid.uuid4().hex,name='Exact original revision challenge candidate',
        owner_ref=contract_body['owner_ref'],scope_ref=routing['candidate_scope_ref'],lifecycle_state='candidate',
        evidence_refs=[r['binding']['ref'] for r in accepted],
        relation_refs=[{'relation_kind_ref':'relation.challenges','counterpart_kind':view.handle.operations.endpoint_kind(subject,view.data['projection']),
            'counterpart_ref':subject_header['version_ref'],'direction':'source'}],successor_refs=[],
        challenge_route=payload['owner_route'],claim_ceiling='Owned candidate fixture only; no real owner resolution, admission or changed subject history.')
    event['payload'].update(challenge_contract_ref=contract_header['version_ref'],subject_ref=subject_header['identity_ref'],
        subject_version_ref=subject_header['version_ref'],challenger_ref=challenger['identity'],ground=ground,
        evidence_refs=event['evidence_refs'],response_state='open',resolution_decision_ref='none',residue_refs=[],submitted_at=now.isoformat())
    raw=(json.dumps(event,indent=3,ensure_ascii=False)+'\n').encode();candidate_binding=P.binding('candidate:challenge-event',raw);materials[candidate_binding['ref']]=raw
    # An actual authenticated operator context has these exact Actor fields.
    # This deterministic fixture calculation supplies no eligibility authority.
    actor={'principal_ref':challenger['identity'],'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
    routes={k:routing[k] for k in ('policy_ref','owner_route','resolution_gate_ref','residue_route_ref','response_mode')}
    routes['response_period']=payload['response_period']
    validator=P.binding(str((HERE/'challenge_submission.py').relative_to(ROOT)),(HERE/'challenge_submission.py').read_bytes())
    eligible=eligibility_bytes(actor=actor,subject=subject_header,contract=contract_header,challenger=challenger_header,
        ground=ground,evidence=[{'kind':r['kind'],'binding':r['binding'],'source_posture':r['source_posture']} for r in accepted],source_cut=cut,routes=routes,validator_binding=validator)
    eligible_binding=P.binding('candidate:challenge-eligibility',eligible);materials[eligible_binding['ref']]=eligible
    with tempfile.TemporaryDirectory(prefix='cal-R03-current-challenge-') as temporary:
        root=Path(temporary);root.chmod(0o700)
        key,path,pin=F.provision(root,'reference-corrected',materials,{},principal=challenger['identity'])
        policy=P.frame_parse(path.read_bytes())
        route_raw=P.compact(routing);route_sha=P.source.sha(route_raw)
        W.atomic(Path(policy['workspace']['root'])/'objects'/(route_sha+'.json'),route_raw)
        workspace=P.frame_parse((Path(policy['workspace']['root'])/'workspace.json').read_bytes())
        control={'routing_binding':{'ref':'workspace-object:'+workspace['workspace_ref']+':'+route_sha,'sha256':route_sha}}
        policy.update(schema_version='lab-local-challenge-candidate-policy/v1-candidate' if grant_challenge else 'lab-local-metadata-candidate-policy/v1-candidate',
            source_name='custody-participation',allowed_operations=list(P.CHALLENGE_SUPPORTED if grant_challenge else P.METADATA_SUPPORTED),
            purpose='durable-metadata-and-exact-challenge-preparation' if grant_challenge else 'durable-metadata-and-exact-candidate-preparation',
            development_authorization_binding=routing['development_authorization_binding'],scope_control=None,expires_at=expires.isoformat(),max_request_bytes=1048576)
        if grant_challenge:policy['challenge_control']=control
        policy_raw=P.compact(policy);path.write_bytes(policy_raw);pin=P.source.sha(policy_raw)
        channel=A.ReaderChannel(path,pin,schemas);proof=F.proof(key,channel.challenge);authenticated=channel.authenticate(proof)
        service=Service(view,channel,schemas)
        try:
            def request():
                value=F.call(channel.context,'lab.status',cut)
                value.update(operation='challenge.submit',idempotency_key='fixture:challenge-submit',deadline=expires.isoformat(),
                    message={'schema_version':'lab-challenge-request/v1-candidate','request_ref':'request:R03-exact-challenge:'+uuid.uuid4().hex,
                        'actor':copy.deepcopy(actor),'subject':copy.deepcopy(subject_header),'challenge_contract':copy.deepcopy(contract_header),
                        'ground':ground,'evidence_bindings':[copy.deepcopy(r['binding']) for r in accepted],
                        'eligibility_evaluation_binding':copy.deepcopy(eligible_binding),'challenge_candidate_binding':copy.deepcopy(candidate_binding),
                        'source_cut':copy.deepcopy(cut),'authority_effect':'none'})
                return value
            yield service,request,{'root':root,'routing':routing,'candidate_original':raw,'authentication_reply':authenticated,
                'subject_original':current_body(view,subject),'subject':subject_header}
        finally:service.close();key=None
    P.source.require(not root.exists(),'owned challenge workspace/signer remained after cleanup')
