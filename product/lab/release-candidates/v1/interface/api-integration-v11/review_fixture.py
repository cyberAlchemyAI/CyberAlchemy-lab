"""Real current source, independent host-selected routing and signed reader proof."""
import copy,json,os,tempfile,uuid
from contextlib import contextmanager
from datetime import timedelta
from . import protocol as P, artifact_model as M, workspace as W, auth as A
from . import fixtures as F, example_fixture as EF, handlers as H
from .review_preparation import header
from .service import Service
from .guard import verify
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
sha=P.source.sha;encoded=P.source.encoded;require=P.source.require
def selected(view,identity):
    rows=[s for s in view.subjects.values() if s['identity']==identity and s['effective_state'] in ('admitted-current','local-admitted-current')]
    require(len(rows)==1,'fixture exact current identity is missing or ambiguous: '+identity)
    return rows[0]

def preference_target(view,materials,metadata):
    original=selected(view,'user-decision-preference:lab-owner-final-review')
    body=copy.deepcopy(original['record']);identity='user-decision-preference:R03-one-final-checkpoint'
    body.update(node_id=identity,name='One exact final owner checkpoint for this proposed change',scope_ref=view.data['config']['scope_ref'],
        owner_ref='principal:repository-owner',lifecycle_state='candidate',evidence_refs=[],successor_refs=[],authority_effect='none')
    body['payload'].update(user_ref='principal:repository-owner',profile_ref='workflow-decision-profile:lab-governance-single-checkpoint',status='active')
    raw=(json.dumps(body,indent=3,ensure_ascii=False)+'\n').encode();version=identity+'@review.candidate.1';carrier='cal.artifact-type.user-decision-preference/v1'
    decision='decision:R03-proposed-one-checkpoint-preference'
    rt={'category':'artifact-instance','operation':'admit','version_ref':version,'carrier_ref':carrier,'record':body,'predecessor_ref':None,'decision_ref':decision,'contract':None}
    if view.selected['name']=='custody-participation':rt['content']=view.handle.custody.content_entry(raw)
    core={'decision_ref':decision,'category':'artifact-instance','operation':'admit','version_ref':version,'target_digest':view.handle.common.digest(rt)}
    meta={'schema_version':'lab-candidate-target-metadata/v1-candidate','category':'artifact-instance','decision_ref':decision,'contract':None}
    materials.update({'candidate:review-preference-content':raw,'candidate:review-preference-core':view.handle.common.encoded(core),'candidate:review-preference-metadata':encoded(meta)})
    mb=P.binding('candidate:review-preference-metadata',materials['candidate:review-preference-metadata']);metadata[version]=mb
    contract=view.data['projection']['contracts'][carrier]
    ref={'scope_ref':view.data['config']['scope_ref'],'identity_ref':identity,'version_ref':version,'carrier_ref':carrier,'byte_sha256':sha(raw),
        'candidate_contract_binding':{'ref':contract['schema_path'],'sha256':contract['schema_sha256']}}
    return {'operation':'admit','artifact':ref,'predecessor':None,'content':{'content_ref':'candidate:review-preference-content','byte_sha256':sha(raw),'size_bytes':len(raw),'media_type':'application/json'},
        'candidate_binding':mb,'requested_effect':'Admit only this exact preference for the recognized owner under the current single checkpoint profile after final owner authorization',
        'decision_core_binding':P.binding('candidate:review-preference-core',materials['candidate:review-preference-core'])}


@contextmanager
def example(view,schemas,*,multiple_voices=False,grant_review=True):
    materials,metadata,target=EF.materials_for(view)
    targets=[target,preference_target(view,materials,metadata)]
    with tempfile.TemporaryDirectory(prefix='cal-R03-current-review-') as temporary:
        root=Path(temporary);root.chmod(0o700)
        principal='principal:R03-review-proposer:'+uuid.uuid4().hex
        profile=M.artifact_ref(view,selected(view,'workflow-decision-profile:lab-governance-single-checkpoint'))
        owner=M.artifact_ref(view,selected(view,'principal:repository-owner'))
        routes=[]
        for t in targets:
            core=P.frame_parse(materials[t['decision_core_binding']['ref']])
            voices=[{'role_ref':'role:repository-owner','principal':copy.deepcopy(owner),'role_declaration':copy.deepcopy(profile)}]
            if multiple_voices:
                voices.append({'role_ref':'role:definition-owner','principal':copy.deepcopy(owner),
                    'role_declaration':M.artifact_ref(view,selected(view,'decision-bundle:governance-transaction-surface-0074'))})
            routes.append({'decision_ref':core['decision_ref'],'core_binding':copy.deepcopy(t['decision_core_binding']),'required_owner_voices':voices})
        authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        current=A.now()
        routing={'schema_version':'lab-independent-candidate-review-routing/v1-candidate','principal_ref':principal,
            'scope_ref':view.data['config']['scope_ref'],'not_before':(current-timedelta(seconds=1)).isoformat(),
            'expires_at':(current+timedelta(minutes=20)).isoformat(),
            'authorization_basis_binding':P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),
            'base_cut_binding':P.binding('selected-review-source-cut',P.compact(H.cut(view))),
            'workflow_decision_profile':profile,'user_decision_preference':header(targets[-1]['artifact']),
            'preference_basis':'proposed-target','accountable_owner':owner,
            'workflow_protocol':{'reference':'protocol:R03-review-workflow:'+uuid.uuid4().hex,
                'reference_class':'protocol-review-workflow','authority_effect':'none'},
            'members':routes,'allowed_operation':'proposal.review','scope_posture':'isolated-candidate-review-preparation',
            'current_owner_authority_verified':False,'actual_owner_outcome':None,'authority_effect':'none'}
        materials['candidate:review-routing']=P.compact(routing)
        key,path,pin=F.provision(root,'reference-corrected',materials,metadata,principal=principal)
        policy=P.frame_parse(path.read_bytes())
        policy.update(schema_version='lab-local-review-candidate-policy/v1-candidate' if grant_review else 'lab-local-metadata-candidate-policy/v1-candidate',
            source_name='custody-participation',allowed_operations=list(P.REVIEW_SUPPORTED if grant_review else P.METADATA_SUPPORTED),
            purpose='durable-metadata-and-exact-review-preparation' if grant_review else 'durable-metadata-and-exact-candidate-preparation',
            development_authorization_binding=P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),scope_control=None,max_request_bytes=1048576)
        policy_raw=P.compact(policy);path.write_bytes(policy_raw);pin=sha(policy_raw)
        channel=A.ReaderChannel(path,pin,schemas);proof=F.proof(key,channel.challenge);authenticated=channel.authenticate(proof)
        service=Service(view,channel,schemas)
        try:
            prepare=EF.candidate_call(service,target);prepare['message']['targets']=copy.deepcopy(targets)
            reply=service.call(P.compact(prepare))
            require(reply.get('kind')=='result','actual predecessor preparation failed')
            review=reply['message']
            def request():
                value=F.call(channel.context,'lab.status',H.cut(view))
                value.update(operation='proposal.review',idempotency_key='fixture:review',message=copy.deepcopy(review))
                return value
            yield service,request,{'public_policy':policy,'signed_nonce_proof':P.frame_parse(proof),
                'authentication_reply':authenticated,'routing':routing,'root':root,'prepare_reply':reply}
        finally:
            service.close();key=None
    require(not root.exists(),'owned current review host/key/workspace remained')
