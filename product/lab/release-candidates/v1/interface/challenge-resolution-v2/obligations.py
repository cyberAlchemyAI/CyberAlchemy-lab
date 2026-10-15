"""Check exact response obligations; documents do not grant authority."""
from .gate import require, instant

CONTROL_FIELDS=frozenset({'policy_ref','owner_route','resolution_gate_ref',
    'unresolved_residue_route','response_period','response_seconds','response_mode',
    'response_binding','challenger','accepted_evidence'})
RESPONSE_FIELDS=frozenset({'schema_version','challenge','challenge_contract','subject',
    'owner_principal','response_mode','responded_at','evidence_bindings','authority_effect'})


def verify(control,*,rules,challenge,challenge_header,contract_header,subject_header,
           owner_header,challenger,response,evidence_bindings,now):
    """Inputs are exact originals selected and verified by the host adapter.

    response_seconds is an independently selected interpretation of the exact
    response_period reference. It does not change the source Contract.
    """
    require(type(control) is dict and set(control)==CONTROL_FIELDS,'closed response obligation control required')
    for field in ('policy_ref','owner_route','resolution_gate_ref','unresolved_residue_route','response_period'):
        require(control[field]==rules[field],'response Contract route differs: '+field)
    require(type(control['response_seconds']) is int and 0<control['response_seconds']<=86400,
            'bounded explicit response-period interpretation required')
    require(control['response_mode'] in rules['response_modes'],'response mode undeclared')
    require(challenger['kind'] in rules['eligible_challenger_kinds']
            and challenger['payload']['status']=='active'
            and challenge['challenger_ref'] in (challenger['node_id'],control['challenger']['version_ref']),
            'actual challenger not recognized by exact Contract')
    require(type(response) is dict and set(response)==RESPONSE_FIELDS,'closed exact response original required')
    expected={'schema_version':'lab-exact-challenge-response/v1-candidate',
              'challenge':challenge_header,'challenge_contract':contract_header,'subject':subject_header,
              'owner_principal':owner_header,'response_mode':control['response_mode'],
              'responded_at':response['responded_at'],'evidence_bindings':evidence_bindings,'authority_effect':'none'}
    require(response==expected,'response original does not bind this exact contest and owner')
    submitted=instant(challenge['submitted_at']);responded=instant(response['responded_at'])
    require(submitted<=responded<=now and (responded-submitted).total_seconds()<control['response_seconds'],
            'response absent from original response window or clock moved backward')
    accepted=control['accepted_evidence']
    require(type(accepted) is list and accepted,'independently selected evidence descriptors required')
    require(all(type(row) is dict and set(row)=={'binding','artifact','kind'} for row in accepted),
            'closed original source evidence descriptors required')
    bindings=[row['binding'] for row in accepted]
    require(len({(item['ref'],item['sha256']) for item in bindings})==len(bindings),
            'duplicate independently selected evidence')
    require(bindings==evidence_bindings,'response evidence differs from independent exact selection')
    require(set(rules['required_evidence_kinds'])<=set(row['kind'] for row in accepted),
            'required response evidence kinds missing')
    require(set(challenge['evidence_refs'])<=set(item['ref'] for item in bindings),
            'original Challenge evidence not preserved in response')


def composition(result,branches,*,subject_header):
    """Retain ordered axes, exact common bindings and original proposal fields."""
    require(branches,'one exact semantic or governance consequence proposal required')
    common=('actor','scope_ref','base_cut','source_profile_binding','workspace_binding',
            'idempotency_key','challenge_route','authority_effect')
    for field in common:
        require(all(body[field]==result[field] for body in branches.values()),'consequence composition differs: '+field)
    for field in ('targets','connection_proposals','evidence_bindings','schema_bindings'):
        values=[item for body in branches.values() for item in body[field]]
        if field!='targets':
            unique=[]
            for item in values:
                if item not in unique:unique.append(item)
            values=unique
        require(result[field]==values,'result is not exact ordered consequence composition: '+field)
    targets=result['targets']
    require(len({target['artifact']['version_ref'] for target in targets})==len(targets),
            'duplicate consequence target versions')
    for target in targets:
        require(target['artifact']['version_ref']!=subject_header['version_ref'],
                'existing challenged version cannot be a prospective postimage')
        if target['artifact']['identity_ref']==subject_header['identity_ref']:
            require(target['operation']=='revise' and target['predecessor']==subject_header,
                    'semantic revision must preserve the exact challenged predecessor')
