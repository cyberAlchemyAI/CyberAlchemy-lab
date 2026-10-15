"""Owned authenticated preparation examples; proposed preference is an exact target."""
import copy,json,os,tempfile,uuid
from contextlib import contextmanager,ExitStack
from datetime import timedelta
from .base import *
from .review import ReviewPreparation,header
F=imported('example_fixture')

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
def example(source_pin,source_name='reference-corrected',*,proposed_preference=True,multiple_voices=False):
    guard(source_pin)
    with ExitStack() as stack:
        view=stack.enter_context(P.source.replay_source(source_name));schemas=P.Schemas(API_PROFILE)
        materials,metadata,target=F.materials_for(view);targets=[target]
        if proposed_preference:targets.append(preference_target(view,materials,metadata))
        root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-exact-review-example-')));root.chmod(0o700)
        principal=P.source.custody_delivery().records.PRINCIPAL if source_name=='custody-participation' else 'principal:R03-exact-review-proposer'
        key,policy,pin=F.provision(root,source_name,materials,metadata,principal=principal)
        channel=F.ReaderChannel(policy,pin,schemas);proof=F.proof(key,channel.challenge);auth=channel.authenticate(proof)
        service=S.Service(view,channel,schemas);stack.callback(service.close)
        call=F.candidate_call(service,target,'change.prepare','fixture:prepare');call['message']['targets']=targets
        reply=service.call(P.compact(call));require(reply.get('kind')=='result','actual precursor API preparation failed: '+str(reply))
        review=reply['message'];profile=M.artifact_ref(view,selected(view,'workflow-decision-profile:lab-governance-single-checkpoint'))
        owner=M.artifact_ref(view,selected(view,'principal:repository-owner'))
        preference=header(targets[-1]['artifact']) if proposed_preference else M.artifact_ref(view,selected(view,'user-decision-preference:lab-owner-final-review'))
        routes=[]
        for t in targets:
            core=P.frame_parse(materials[t['decision_core_binding']['ref']]);voices=[{'role_ref':'role:repository-owner','principal':copy.deepcopy(owner),'role_declaration':copy.deepcopy(profile)}]
            if multiple_voices:voices.append({'role_ref':'role:definition-owner','principal':copy.deepcopy(owner),'role_declaration':M.artifact_ref(view,selected(view,'decision-bundle:governance-transaction-surface-0074'))})
            routes.append({'decision_ref':core['decision_ref'],'core_binding':copy.deepcopy(t['decision_core_binding']),'required_owner_voices':voices})
        now=imported('auth').now();routing={'schema_version':'lab-independent-candidate-review-routing/v1-candidate','principal_ref':principal,'scope_ref':view.data['config']['scope_ref'],
            'not_before':(now-timedelta(seconds=1)).isoformat(),'expires_at':min(now+timedelta(minutes=10),imported('auth').instant(channel.context['expires_at'])).isoformat(),
            'authorization_basis_binding':P.binding(str((ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json').relative_to(ROOT)),(ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json').read_bytes()),
            'base_cut_binding':P.binding('selected-review-source-cut',P.compact(imported('handlers').cut(view))),'workflow_decision_profile':profile,'user_decision_preference':preference,
            'preference_basis':'proposed-target' if proposed_preference else 'current-source','accountable_owner':owner,'workflow_protocol':{'reference':'protocol:R03-review-workflow:'+uuid.uuid4().hex,'reference_class':'protocol-review-workflow','authority_effect':'none'},
            'members':routes,'allowed_operation':'proposal.review','scope_posture':'isolated-candidate-review-preparation','current_owner_authority_verified':False,'actual_owner_outcome':None,'authority_effect':'none'}
        raw=P.compact(routing);path=root/'review-routing.json';fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(raw)
        builder=ReviewPreparation(service,path,sha(raw),source_pin)
        yield builder,review,{'root':str(root),'public_policy':json.loads(policy.read_bytes()),'nonce_challenge':channel.challenge,'signed_nonce_proof':json.loads(proof),'authentication_reply':auth,'routing':copy.deepcopy(routing),'actual_preparation_reply':reply}
        guard(source_pin)
    require(not root.exists(),'owned review host/key/workspace remains')
