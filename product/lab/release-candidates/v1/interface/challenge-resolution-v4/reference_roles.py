"""Scoped reference meanings for an independently verified resolution episode.

Expected output declarations are contracts, not artifact revisions. A retained
challenged revision is evidence history, not current participation or authority.
Only the already signed semantic/governance proposals enter this resolver.
"""
import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
CURRENT=('admitted-current','local-admitted-current')
KIND='lab-local-integrated-challenge-resolution-policy/v3-candidate'
CARRIERS=('cal.artifact-type.work/v1','cal.artifact-type.challenge-event/v1')

def require(value,reason):
    if not value:raise ValueError(reason)

def selected(path):
    require(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'unsafe reference contract file')
    raw=path.read_bytes()
    return {'ref':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()},raw

def validate_control(policy):
    require(policy['schema_version']==KIND,'independent exact reference policy required')
    control=policy['resolution_reference_control']
    require(set(control)=={'resolver_binding','contract_binding'},'closed reference control required')
    expected,raw=selected(HERE/'reference-role-contract.json')
    resolver,_=selected(Path(__file__).resolve())
    require(control=={'resolver_binding':resolver,'contract_binding':expected},'independently selected reference resolver/contract differs')
    contract=json.loads(raw);_,schema=selected(HERE/'reference-role-contract.schema.json')
    Draft202012Validator(json.loads(schema)).validate(contract)
    require(contract['routing_binding']==policy['resolution_control']['routing_binding']
            and policy['scope_refs']==[contract['scope_ref']],'reference routing or exact scope differs')
    for item in (contract['definition_binding'],contract['expected_output']['contract_binding']):
        actual,_=selected(ROOT/item['ref']);require(actual==item,'reference meaning source changed')
    return copy.deepcopy(control),contract

class ReferenceRoles:
    def __init__(self,owner,message,branches,result):
        self.owner=owner;self.P=owner.P;self.M=owner.M;self.host=owner.host
        self.control,self.contract=validate_control(self.host.channel.policy_guard())
        c=self.contract
        require(message['source_cut']==c['source_cut']==owner.routing['source_cut']
                and message['challenge']==c['challenge'] and message['resolution_decision']==c['decision']
                and owner.routing['subject']==c['work'],'reference episode differs from independently signed gate')
        self.messages=[copy.deepcopy(body) for body in branches.values()]+[copy.deepcopy(result)]

    def supports(self,target,message):
        return target['carrier_ref'] in CARRIERS and message in self.messages

    def resolve(self,target,message,post):
        require(self.supports(target,message),'undeclared reference scope or carrier')
        control,c=validate_control(self.host.channel.policy_guard())
        require(control==self.control and c==self.contract,'reference control changed')
        view=self.host.handlers.view;before=view.data['projection'];body=target['record'];payload=body['payload']
        require(message['base_cut']==c['source_cut'] and body['scope_ref']==c['scope_ref']
                and post is not before,'exact prospective scope required')
        proposed=[t for t in message['targets'] if t['artifact']['version_ref']==target['version_ref']]
        require(len(proposed)==1 and self.P.frame_parse(self.owner.vault.material(
            {'ref':proposed[0]['content']['content_ref'],'sha256':proposed[0]['content']['byte_sha256']}))==body,
            'reference target differs from independently signed original proposal')
        refs=[];roles=[];inputs=[self.control['contract_binding'],self.control['resolver_binding'],self.owner.routing_binding]
        def reference(selector,ref,kind=None,exact=None,historical=False):
            rows=[s for s in post['subjects'].values() if (s['version_ref']==ref or s['identity']==ref)
                and s['effective_state'] in CURRENT]
            posture='resolved'
            if historical:
                require(exact==c['work'] and ref==exact['version_ref'],'only exact challenged revision has historical eligibility')
                row=before['subjects'].get(ref)
                require(row is not None and row['effective_state'] in CURRENT and ref in post['subjects'],
                        'historical subject not retained from exact original cut')
                require(post['subjects'][ref]['record']==row['record'],'historical challenged original was overwritten')
                resolved=self.M.artifact_ref(view,row);require(resolved==exact,'retained challenged original header differs')
                if post['subjects'][ref]['effective_state'] not in CURRENT:posture='historical'
            else:
                require(len(rows)==1,'current reference unresolved or ambiguous: '+ref)
                row=rows[0]
                require(row['record']['scope_ref']==c['scope_ref'],'reference outside exact source scope')
                require(row['version_ref'] in before['subjects'],'reference cannot promote a prospective target to current authority')
                resolved=self.M.artifact_ref(view,before['subjects'][row['version_ref']])
                if exact is not None:require(resolved==exact,'exact reference header differs')
            semantic=view.handle.operations.endpoint_kind(row,post)
            require(kind is None or semantic==kind,'reference semantic kind differs')
            original=self.M.record_bytes(view,before['subjects'][row['version_ref']])[0]
            require(self.P.source.sha(original)==resolved['byte_sha256'],'reference original bytes differ')
            refs.append({'source_version_ref':target['version_ref'],'selector':selector,'requested_ref':ref,
                         'resolved_ref':resolved,'posture':posture})
            roles.append({'selector':selector,'requested_ref':ref,'role':'exact-challenged-version' if historical else 'current-artifact-reference',
                          'artifact':resolved,'posture':posture,'current_authority_asserted':False})
            inputs.append(self.P.binding(ref,original))
            return row['record']
        if target['carrier_ref']==CARRIERS[0]:
            require(target['version_ref']==next(r['target_version_ref'] for r in self.owner.routing['consequence_routes'] if r['axis']=='semantic'),
                    'Work target is not exact signed semantic consequence')
            reference('/payload/project_ref',payload['project_ref'],'project')
            for key,kind in [('goal_refs','goal'),('input_refs',None)]:
                for i,ref in enumerate(payload[key]):reference('/payload/'+key+'/'+str(i),ref,kind)
            expected=c['expected_output'];ref=expected['requested_ref']
            require(payload['output_refs']==[ref] and payload['completion_state']==expected['eligible_completion_state'],
                    'expected output declaration cannot certify produced output or completed Work')
            actual,raw=selected(ROOT/expected['contract_binding']['ref']);doc=json.loads(raw)
            require(actual==expected['contract_binding'] and doc['$id']==expected['contract_id'],'expected output protocol contract differs')
            inputs.extend([actual,c['definition_binding']])
            roles.append(copy.deepcopy(expected))
            # The shared report slot models artifact revisions. Exclude this
            # contract declaration from artifact resolution; its separate typed
            # check resolves the exact protocol meaning without a fabricated body.
            refs.append({'source_version_ref':target['version_ref'],'selector':expected['selector'],'requested_ref':ref,
                         'resolved_ref':None,'posture':'excluded'})
        else:
            require(target['version_ref']==next(r['target_version_ref'] for r in self.owner.routing['consequence_routes'] if r['axis']=='governance'),
                    'Challenge target is not exact signed governance consequence')
            routing=self.owner.routing;obligations=routing['response_obligations']
            contract=reference('/payload/challenge_contract_ref',payload['challenge_contract_ref'],'challenge-contract',routing['challenge_contract'])
            reference('/payload/challenger_ref',payload['challenger_ref'],'principal',obligations['challenger'])
            require(payload['subject_ref']==c['work']['identity_ref'],'challenged identity differs from retained exact revision')
            reference('/payload/subject_version_ref',payload['subject_version_ref'],'work',c['work'],True)
            roles.append({'selector':'/payload/subject_ref','requested_ref':payload['subject_ref'],'role':'challenged-identity-of-exact-version',
                          'artifact':c['work'],'current_authority_asserted':False})
            evidence=obligations['accepted_evidence'];expected=[r['artifact']['version_ref'] for r in evidence]
            require(payload['evidence_refs']==expected,'Challenge evidence inventory differs')
            for i,row in enumerate(evidence):
                reference('/payload/evidence_refs/'+str(i),payload['evidence_refs'][i],row['kind'],row['artifact'])
                require(self.owner.vault.material(row['binding'])==self.M.record_bytes(view,self.host.handlers.resolve_exact(row['artifact']))[0],
                        'Challenge evidence original differs');inputs.append(row['binding'])
            reference('/payload/resolution_decision_ref',payload['resolution_decision_ref'],'decision',c['decision'])
            require(payload['response_state']=='resolved-for-revision' and payload['residue_refs']==[]
                    and payload['ground'] in contract['payload']['grounds'],'undeclared resolution state, residue or ground')
            prior=self.owner.record(c['challenge'],'challenge-event')['payload']
            require(prior['response_state']=='responded' and prior['resolution_decision_ref']=='none'
                    and payload['submitted_at']==prior['submitted_at'],'Challenge transition lacks exact responded predecessor')
            roles.append({'selector':'/payload/residue_refs','requested_refs':[],
                          'role':'empty-residue-under-verified-response-obligations','current_authority_asserted':False})
        # Every common carrier reference and role hint is accounted for. Hints
        # never create a new Typed Relation or inherit authority from its endpoint.
        require(body['successor_refs']==[],'undeclared successor references')
        original=c['work'] if target['carrier_ref']==CARRIERS[0] else c['challenge']
        predecessor=self.owner.record(original)
        require(body['owner_ref']==predecessor['owner_ref'] and body['challenge_route']==predecessor['challenge_route']
                and body['evidence_refs']==predecessor['evidence_refs'],'common carrier reference changed outside signed consequence')
        for i,ref in enumerate(body['evidence_refs']):
            require(ref in c['original_evidence_bindings'],'common original evidence lacks independent exact binding')
            actual,_=selected(ROOT/ref);require(actual==c['original_evidence_bindings'][ref],'common original evidence changed')
            inputs.append(actual);roles.append({'selector':'/evidence_refs/'+str(i),'requested_ref':ref,
                'role':'bound-original-document','binding':actual,'current_authority_asserted':False})
        reference('/owner_ref',body['owner_ref'],'principal')
        for i,relation in enumerate(body['relation_refs']):
            historical=target['carrier_ref']==CARRIERS[1] and relation['relation_kind_ref']=='relation.challenges'
            if historical:
                require(relation['counterpart_kind']=='work' and relation['direction']=='source','undeclared historical relation role')
            reference('/relation_refs/'+str(i)+'/counterpart_ref',relation['counterpart_ref'],relation['counterpart_kind'],
                      c['work'] if historical else None,historical)
        return refs,{'schema_version':'lab-exact-resolution-reference-check/v1-candidate',
            'source_cut':c['source_cut'],'target_version_ref':target['version_ref'],'typed_references':roles,
            'input_bindings':list({(b['ref'],b['sha256']):b for b in inputs}.values()),
            'actual_output_asserted':False,'work_satisfaction_asserted':False,'current_authority_asserted':False,
            'new_typed_relation_asserted':False,'canonical_admission_granted':False,'authority_effect':'none'}
