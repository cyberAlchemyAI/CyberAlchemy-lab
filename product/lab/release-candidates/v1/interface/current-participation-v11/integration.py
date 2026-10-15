"""Declared development contest records and explicit current connection tuples."""
import copy
from .base import ROOT,load,require,sha
from . import records as R

OWNER='principal:'+R.PREFIX+':resolution-owner'
OWNER_REFERENCE='principal-reference:'+R.PREFIX+':resolution-owner'
POLICY='policy:'+R.PREFIX+':contest'
CONTRACT='challenge-contract:'+R.PREFIX+':contest'
EVIDENCE='evidence-set:'+R.PREFIX+':contest'
CHALLENGE='challenge-event:'+R.PREFIX+':contest'
DECISION='decision:'+R.PREFIX+':contest'
RESPONSE='response:'+R.PREFIX+':contest'
EFFECTS={axis:'effect:'+R.PREFIX+':'+axis for axis in ('semantic','governance')}
SCOPES={axis:'decision-scope:'+R.PREFIX+':'+axis for axis in EFFECTS}
BOUNDARIES={axis:'authority-boundary:'+R.PREFIX+':'+axis for axis in EFFECTS}
EFFECT_KINDS={axis:'prepare-exact-'+axis+'-consequence' for axis in EFFECTS}
NEXT={axis:identity+'@1.0.0-candidate.2' for axis,identity in [('semantic',R.WORK),('governance',CHALLENGE)]}
OUTCOME='prepare-controlled-development-contest-consequences'
ROUTES={'policy_ref':POLICY+'@'+R.VERSION,'owner_route':'protocol:'+R.PREFIX+':controlled-contest-owner',
        'resolution_gate_ref':'protocol:'+R.PREFIX+':independent-signed-contest-gate',
        'unresolved_residue_route':'protocol:'+R.PREFIX+':unresolved-contest-residue',
        'response_period':'protocol:'+R.PREFIX+':300-second-response'}
DIAG='docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/API83-original-Machine-generation-diagnosis-0001.json'
CLAIM='Controlled development source declarations and candidate consequences only; no actual human owner outcome, canonical admission, authority inferred from records or restored Agent memory.'


def fixture(kind):
    version='v2' if kind in ('policy','decision','decision-scope') else 'v1'
    folder=ROOT/'authority/artifact-types'
    if version=='v2':folder=folder/'candidates/0013-governance-transaction-surface/impacted-carrier-successors'
    return load(folder/kind/version/'fixtures/valid/record.json')


def common(kind,identity,scope):
    body=fixture(kind)
    body.update(node_id=identity,owner_ref=OWNER,scope_ref=scope,name='Controlled '+kind,
        lifecycle_state='candidate',authority_effect='none',evidence_refs=[DIAG],
        challenge_route=ROUTES['owner_route'],successor_refs=[],relation_refs=[],claim_ceiling=CLAIM)
    return body


def role(kind,other_kind,other,direction='source'):
    return {'relation_kind_ref':kind,'direction':direction,'counterpart_kind':other_kind,'counterpart_ref':other}


def targets(projection,scope,config,gate_public_key,submitted_at):
    bodies={}
    principal=common('principal',OWNER,scope)
    principal['payload'].update(principal_kind='isolated-development-resolution-owner',status='active',
        stable_subject_ref='ed25519-public-key-sha256:'+sha(bytes.fromhex(gate_public_key)),
        registry_ref='protocol:'+R.PREFIX+':independent-contest-key-registry',
        recognition_boundary_refs=[ROUTES['resolution_gate_ref']])
    principal['relation_refs']=[role('relation.asserts-identity-of','principal-reference',OWNER_REFERENCE+'@'+R.VERSION,'target')]
    bodies[OWNER]=principal
    reference=common('principal-reference',OWNER_REFERENCE,scope)
    reference['payload'].update(principal_ref=OWNER,principal_kind='isolated-development-resolution-owner',
        issuer_ref=config['owner_ref'],resolution_route=ROUTES['owner_route'],
        integrity_digest=principal['payload']['stable_subject_ref'],privacy_posture='Public digest only; independent ephemeral development key is not exported.')
    reference['relation_refs']=[role('relation.asserts-identity-of','principal',OWNER+'@'+R.VERSION)]
    bodies[OWNER_REFERENCE]=reference
    policy=common('policy',POLICY,scope)
    policy['payload'].update(issuer_ref=OWNER,governed_scope_ref=scope,rule_refs=[ROUTES['resolution_gate_ref']],
        effective_period='Exact independently fixed Source6 episode period',exception_route=ROUTES['unresolved_residue_route'])
    policy['relation_refs']=[role('relation.governed-by','context',R.CONTEXT+'@'+R.VERSION,'target')]
    bodies[POLICY]=policy
    contract=common('challenge-contract',CONTRACT,scope)
    contract['payload'].update(**ROUTES,challengeable_subject_kinds=['work'],eligible_challenger_kinds=['principal'],
        grounds=['scope-error'],required_evidence_kinds=['evidence-set'],response_modes=['evidence-and-revision'])
    contract['relation_refs']=[role('relation.governed-by','policy',POLICY+'@'+R.VERSION)]
    bodies[CONTRACT]=contract
    evidence=common('evidence-set',EVIDENCE,scope)
    evidence['payload'].update(item_refs=[DIAG],source_refs=[DIAG],
        coverage_statement='Exact retained Machine refusal evidence for the controlled response; no whole Lab acceptance.',
        limitations=['No actual owner admission outcome','Original repair predates later application; no causal benefit is inferred.'])
    evidence['relation_refs']=[role('relation.member-of','project',scope)]
    bodies[EVIDENCE]=evidence
    challenge=common('challenge-event',CHALLENGE,scope)
    challenge['payload'].update(challenge_contract_ref=CONTRACT+'@'+R.VERSION,challenger_ref=OWNER,
        subject_ref=R.WORK,subject_version_ref=R.WORK+'@'+R.VERSION,ground='scope-error',
        evidence_refs=[EVIDENCE+'@'+R.VERSION],submitted_at=submitted_at,response_state='responded',
        resolution_decision_ref='none',residue_refs=[])
    challenge['relation_refs']=[role('relation.challenges','work',R.WORK+'@'+R.VERSION)]
    bodies[CHALLENGE]=challenge
    decision=common('decision',DECISION,scope)
    decision['payload'].update(decision_maker_ref=OWNER,subject_refs=[CHALLENGE+'@'+R.VERSION],selected_outcome=OUTCOME,
        evidence_basis_refs=[RESPONSE,EVIDENCE+'@'+R.VERSION],declared_effect_refs=[EFFECTS[axis]+'@'+R.VERSION for axis in EFFECTS])
    decision['relation_refs']=[role('relation.declares-effect-on','effect',EFFECTS[axis]+'@'+R.VERSION) for axis in EFFECTS]
    bodies[DECISION]=decision
    for axis in EFFECTS:
        subject=R.WORK if axis=='semantic' else CHALLENGE
        kind='work' if axis=='semantic' else 'challenge-event'
        effect=common('effect',EFFECTS[axis],scope)
        effect['payload'].update(effect_kind=EFFECT_KINDS[axis],subject_ref=subject,
            intended_state='candidate-revised' if axis=='semantic' else 'resolved-for-revision',
            effective_when='Independent exact development gate and prospective native validation pass; no canonical effect.',
            verification_refs=[RESPONSE,EVIDENCE+'@'+R.VERSION])
        effect['relation_refs']=[role('relation.declares-effect-on','decision',DECISION+'@'+R.VERSION,'target')]
        bodies[EFFECTS[axis]]=effect
        selected=common('decision-scope',SCOPES[axis],scope)
        selected['payload'].update(subject_kind_refs=[kind],subject_refs=[subject],
            permitted_effects=[EFFECT_KINDS[axis]],excluded_effects=['canonical-admission','live-activation','tool-dispatch','challenged-subject-overwrite'])
        selected['relation_refs']=[role('relation.scopes-authority-over','authority-boundary',BOUNDARIES[axis]+'@'+R.VERSION,'target')]
        bodies[SCOPES[axis]]=selected
        boundary=common('authority-boundary',BOUNDARIES[axis],scope)
        boundary['payload'].update(owner_role_ref='role:'+R.PREFIX+':controlled-candidate-consequence-owner',
            accountable_principal_ref=OWNER,authority_scope_ref=SCOPES[axis]+'@'+R.VERSION,
            allowed_effect_kinds=[EFFECT_KINDS[axis]],excluded_effect_kinds=selected['payload']['excluded_effects'],
            challenge_route_ref=ROUTES['owner_route'],effective_period='Exact independent development gate interval',revocation_state='not-revoked')
        boundary['relation_refs']=[role('relation.scopes-authority-over','decision-scope',SCOPES[axis]+'@'+R.VERSION)]
        bodies[BOUNDARIES[axis]]=boundary
    result=[]
    for identity,body in bodies.items():
        kind=body['kind'];carrier='cal.artifact-type.'+kind+('/v2' if kind in ('policy','decision','decision-scope') else '/v1')
        result.append({'category':'artifact-instance','operation':'admit','version_ref':identity+'@'+R.VERSION,
            'carrier_ref':carrier,'record':body,'predecessor_ref':None,'decision_ref':'decision:'+R.PREFIX+':source-record:'+identity,'contract':None})
    selected={target['record']['node_id']:target for target in result}
    def endpoint(identity):
        if identity in selected:
            target=selected[identity]
            return {'kind':target['record']['kind'],'ref':identity,'version_ref':target['version_ref']}
        if identity==R.WORK:return {'kind':'work','ref':identity,'version_ref':identity+'@'+R.VERSION}
        if identity==R.CONTEXT:return {'kind':'context','ref':identity,'version_ref':identity+'@'+R.VERSION}
        rows=[row for row in projection['subjects'].values() if row['identity']==identity and row['effective_state'] in ('admitted-current','local-admitted-current')]
        require(len(rows)==1,'integration original endpoint unresolved: '+identity)
        row=rows[0]
        return {'kind':'project' if identity==scope else row['kind'],'ref':identity,'version_ref':row['version_ref']}
    specs=[('owner-reference','relation.asserts-identity-of',OWNER_REFERENCE,OWNER,{'assertion_kind':'Exact independent development gate key digest','claim_scope':scope}),
        ('contract-policy','relation.governed-by',CONTRACT,POLICY,{'governance_role':'Declared controlled contest response obligations'}),
        ('context-policy','relation.governed-by',R.CONTEXT,POLICY,{'governance_role':'Declared candidate contest policy; no caller permission inference'}),
        ('challenge-work','relation.challenges',CHALLENGE,R.WORK,{'challenge_contract_ref':CONTRACT+'@'+R.VERSION,
            'challenge_mode':'evidence-and-revision','challenged_version_ref':R.WORK+'@'+R.VERSION}),
        ('evidence-project','relation.member-of',EVIDENCE,scope,{'membership_role':'Controlled contest evidence'})]
    for axis in EFFECTS:
        specs.extend([('decision-effect-'+axis,'relation.declares-effect-on',DECISION,EFFECTS[axis],
                       {'effect_kind':EFFECT_KINDS[axis],'exact_target_version_ref':EFFECTS[axis]+'@'+R.VERSION}),
                      ('boundary-scope-'+axis,'relation.scopes-authority-over',BOUNDARIES[axis],SCOPES[axis],
                       {'authority_role':'Explicit controlled candidate consequence declaration','scope_ref':scope})])
    template=load(ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json')
    for name,kind,left,right,qualifiers in specs:
        body=copy.deepcopy(template);identity='typed-relation:'+R.PREFIX+':contest:'+name
        body.update(node_id=identity,owner_ref=OWNER,scope_ref=scope,name=name,evidence_refs=[DIAG],
            challenge_route=ROUTES['owner_route'],successor_refs=[],relation_refs=[],claim_ceiling=CLAIM)
        body['payload'].update(relation_kind_ref=kind,source=endpoint(left),target=endpoint(right),
            qualifiers=qualifiers,relation_evidence_refs=[DIAG])
        result.append({'category':'typed-relation','operation':'admit','version_ref':identity+'@'+R.VERSION,
            'carrier_ref':'cal.artifact-type.typed-relation/v3','record':body,'predecessor_ref':None,
            'decision_ref':'decision:'+R.PREFIX+':contest-relation:'+name,'contract':None})
    require(len(bodies)==13 and len(specs)==9,'complete declared contest closure required')
    return result
