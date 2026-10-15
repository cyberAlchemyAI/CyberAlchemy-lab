"""Exact multi-member review; all outcomes and authority verification stay pending."""
import copy,json
from pathlib import Path
from importlib import import_module
from . import protocol as P, artifact_model as M, workspace as W, guard as G
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];API=HERE
sha=P.source.sha;encoded=P.source.encoded;require=P.source.require
def imported(name):return import_module(__package__+'.'+name)

CLAIM='Candidate review bytes only. Every target, gap and required owner voice is retained; no owner authorization, admission, WorkflowRun, activation or broader Product/API completion.'
CORE_FIELDS={'decision_ref','category','operation','version_ref','target_digest'}
HEADER_FIELDS=('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')

def header(value):return {k:value[k] for k in HEADER_FIELDS}

class ReviewPreparation:
    def __init__(self,service,routing_path,routing_sha256,source_sha256):
        from .service import Service
        require(type(service) is Service,'actual selected frozen Service required')
        self.service=service;self.view=service.handlers.view;self.schemas=service.schemas;self.vault=service.vault
        self.path=Path(routing_path);self.routing_pin=routing_sha256;self.source_pin=source_sha256
        self.routing=self.routing_guard();self.guard()
    def routing_guard(self):
        require(self.path.is_absolute() and self.path.is_relative_to(Path('/tmp')) and not self.path.is_relative_to(ROOT),'independently selected owned routing file required')
        raw=W.read_private(self.path);require(sha(raw)==self.routing_pin,'selected review routing changed')
        value=P.frame_parse(raw);W.privacy(value)
        schema=json.loads((HERE/'review-routing.schema.json').read_bytes())
        P.Draft202012Validator(schema,registry=self.schemas.registry,format_checker=self.schemas.checker).validate(value)
        require(value['principal_ref']==self.service.channel.guard()['principal_ref'],'review routing proposer is not current authenticated principal')
        require(value['scope_ref']==self.view.data['config']['scope_ref'],'review routing scope differs')
        authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        require(value['authorization_basis_binding']==P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),'candidate review authorization basis differs')
        now=imported('auth').now();instant=imported('auth').instant
        require(instant(value['not_before'])<=now<instant(value['expires_at'])<=instant(self.service.channel.context['expires_at']),'routing permission is outside current bounded host interval')
        return value
    def guard(self):
        G.verify(self.source_pin);self.schemas.guard();self.vault.guard()
        require(all(sha((HERE/name).read_bytes())==digest for name,digest in self.service.code_files.items()),'selected current API code changed')
        require(self.routing_guard()==self.routing,'review routing selection changed')
        require(self.service.handlers.current(),'selected source is not current')
        require(self.routing['base_cut_binding']==P.binding('selected-review-source-cut',P.compact(imported('handlers').cut(self.view))),'independent routing selects another source cut')
    def preflight(self,message,outer):
        self.guard()
        observed=self.service.handlers.selected_cut({'source_cut':message['source_cut']},outer)
        require(observed==imported('handlers').cut(self.view),'candidate review requires exact current head')
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:proposal-review:v1-candidate',message),'exact original proposal-review schema required')
        proposal=P.frame_parse(self.vault.object_read(message['proposal_binding']))
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate',proposal),'selected original proposal schema differs')
        require(proposal['base_cut']==observed and proposal['scope_ref']==self.routing['scope_ref'],'review original proposal cut or scope differs')
        require([m['core_binding'] for m in self.routing['members']]==message['stable_core_bindings'],'independent routing core order differs')
        return observed
    def current_record(self,ref,kind):
        subject=self.service.handlers.resolve_exact(ref)
        require(subject['effective_state'] in ('admitted-current','local-admitted-current'),'review routing source is not current')
        contract=self.view.data['projection']['contracts'][M.carrier(self.view,subject)]
        require(contract['semantic_kind']==kind,'review routing source kind differs')
        raw=M.record_bytes(self.view,subject)[0];require(sha(raw)==ref['byte_sha256'],'routing original body bytes differ')
        body=P.frame_parse(raw);self.view.handle.operations.validate_record(body,ref['carrier_ref'],self.view.data['projection']);W.privacy(body)
        return body,raw
    def role_declared(self,ref,role):
        subject=self.service.handlers.resolve_exact(ref)
        require(subject['effective_state'] in ('admitted-current','local-admitted-current'),'owner role declaration not current')
        raw=M.record_bytes(self.view,subject)[0];require(sha(raw)==ref['byte_sha256'],'owner role declaration original differs')
        body=P.frame_parse(raw);W.privacy(body)
        declared={body.get('owner_ref')}
        if body.get('kind')=='decision-bundle':
            declared.update(row['owner_ref'] for row in body['payload']['ordered_decisions'])
        require(role.startswith('role:') and role in declared,'required owner role is not explicitly declared by selected source')
        return P.binding(ref['version_ref'],raw)
    def resolve_routing(self,proposal):
        r=self.routing;profile,_=self.current_record(r['workflow_decision_profile'],'workflow-decision-profile');p=profile['payload']
        require(p['decision_mode']=='single' and p['exact_target_required'] is True and p['default_checkpoint_kind']=='final-review' and 'final-review' in p['allowed_checkpoint_kinds'],'selected workflow profile does not permit one exact final checkpoint')
        principal,_=self.current_record(r['accountable_owner'],'principal')
        require(principal['payload']['status']=='active','accountable owner Principal not active')
        preference_ref=r['user_decision_preference']
        if r['preference_basis']=='current-source':
            preference,_=self.current_record(preference_ref,'user-decision-preference')
        else:
            matches=[t for t in proposal['targets'] if header(t['artifact'])==preference_ref and t['operation']!='withdraw']
            require(len(matches)==1,'proposed preference must be one exact materialized target in this proposal')
            target=matches[0];require(preference_ref['carrier_ref']=='cal.artifact-type.user-decision-preference/v1','proposed preference carrier differs')
            raw=self.vault.material({'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']});preference=P.frame_parse(raw)
            require(preference['node_id']==preference_ref['identity_ref'] and sha(raw)==preference_ref['byte_sha256'],'proposed preference original body/header differs')
            self.view.handle.operations.validate_record(preference,preference_ref['carrier_ref'],self.view.data['projection'])
        q=preference['payload']
        require(q['user_ref']==r['accountable_owner']['identity_ref'],'preference owner is unresolved; no Principal alias inferred')
        require(q['profile_ref'] in (profile['node_id'],r['workflow_decision_profile']['version_ref']) and q['status']=='active' and q['preferred_checkpoint_kind']=='final-review','preference does not select this current profile/final checkpoint')
        require(q['scope_kind']=='workflow-type' and q['scope_ref']==p['workflow_type_ref'],'preference workflow type scope differs')
        return profile,preference
    def record(self,kind,identity,payload,evidence,owner,profile):
        carrier='cal.artifact-type.'+kind+'/v1';contract=self.view.data['projection']['contracts'][carrier]
        schema=P.source.parse(P.source.original({'path':contract['schema_path'],'sha256':contract['schema_sha256']}))
        body={'schema_version':'cyberalchemy-lab-'+kind+'/v1','node_id':identity,'kind':kind,'name':'Exact pending '+kind,
            'lifecycle_state':'candidate','owner_ref':owner,'scope_ref':self.routing['scope_ref'],'payload':payload,
            'relation_refs':copy.deepcopy(profile['relation_refs']),'evidence_refs':list(dict.fromkeys(b['ref'] for b in evidence)),
            'successor_refs':[],'claim_ceiling':CLAIM,'challenge_route':self.view.data['config']['challenge_route'],'authority_effect':'none'}
        P.Draft202012Validator(schema,format_checker=self.schemas.checker).validate(body)
        self.view.handle.operations.validate_record(body,carrier,self.view.data['projection']);W.privacy(body)
        raw=encoded(body);ref={'scope_ref':self.routing['scope_ref'],'identity_ref':identity,'version_ref':identity+'@review.candidate.1','carrier_ref':carrier,'byte_sha256':sha(raw)}
        return body,ref,self.vault.object(raw)
    def build(self,message,original_message):
        self.guard();require(len(original_message)<=self.service.channel.context['limits']['max_request_bytes'],'review input exceeds current host limit')
        require(P.frame_parse(original_message)==message and self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:proposal-review:v1-candidate',message),'original review bytes or schema differ')
        require(message['source_cut']==imported('handlers').cut(self.view),'review cut is stale or different')
        # Re-execute the exact existing preparation kernel. A hash of a caller-
        # supplied report never establishes that its validator actually ran.
        proposal_raw=self.vault.object_read(message['proposal_binding']);proposal=P.frame_parse(proposal_raw)
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate',proposal),'original selected proposal schema differs')
        actual,evidence=self.service.candidates.prepare(proposal,P.binding('review-revalidation',proposal_raw),message['source_cut'],proposal_raw)
        require(actual==message,'review targets/cores/validation/examples/effects/privacy/gaps do not match independent revalidation')
        report=P.frame_parse(self.vault.object_read(message['validation_report_binding']))
        require(report['result']!='fail' and any(c['check_ref']=='check:exact-source-target-schema-core' and c['result']=='pass' for c in report['checks']),'exact construction/core validation did not pass')
        for binding in message['example_bindings']+message['declared_consequence_bindings']+[message['private_public_review_binding']]:
            W.privacy(P.frame_parse(self.vault.object_read(binding)))
        privacy=P.frame_parse(self.vault.object_read(message['private_public_review_binding']))
        require(privacy['selected_inputs_checked'] is True and privacy['session_memory_exported'] is False and privacy['private_keys_exported'] is False and privacy['public_export_permitted'] is False,'private/public review basis differs')
        profile,preference=self.resolve_routing(proposal)
        routes=self.routing['members'];require(len(routes)==len(proposal['targets'])==len(message['stable_core_bindings']),'owner routes do not cover every independent target/core')
        ordered=[];required=[];target_materials=[];decisions=set();versions=set()
        for index,(target,core_binding,route) in enumerate(zip(proposal['targets'],message['stable_core_bindings'],routes)):
            core_raw=self.vault.material(core_binding);core=P.frame_parse(core_raw)
            require(set(core)==CORE_FIELDS and route['core_binding']==core_binding and route['decision_ref']==core['decision_ref'],'owner route/core order or complete core differs')
            require(core['decision_ref'] not in decisions and core['version_ref'] not in versions,'duplicate independent Decision or target')
            decisions.add(core['decision_ref']);versions.add(core['version_ref'])
            require(core['version_ref']==target['artifact']['version_ref'] and core['operation']==target['operation'],'core target/operation differs')
            voices=[]
            for voice_index,voice in enumerate(route['required_owner_voices']):
                owner,_=self.current_record(voice['principal'],'principal');declaration=self.role_declared(voice['role_declaration'],voice['role_ref'])
                require(owner['payload']['status']=='active','required owner Principal not active')
                require((voice['role_ref'],voice['principal']['version_ref']) not in voices,'duplicate required owner voice')
                voices.append((voice['role_ref'],voice['principal']['version_ref']))
                required.append({'core_index':index,'voice_index':voice_index,'core_binding':copy.deepcopy(core_binding),'owner_role_ref':voice['role_ref'],
                    'owner_principal':copy.deepcopy(voice['principal']),'role_declaration_binding':declaration,'selected_outcome':None,'current_owner_authority_verified':False})
            selected=target['artifact'];raw=None if target['operation']=='withdraw' else self.vault.material({'ref':target['content']['content_ref'],'sha256':target['content']['byte_sha256']})
            if raw is not None:require(sha(raw)==selected['byte_sha256'] and len(raw)==target['content']['size_bytes'],'target bytes changed')
            else:require(M.artifact_ref(self.view,self.view.subjects[selected['version_ref']])==header(selected),'withdraw preimage differs')
            target_materials.append({'target':copy.deepcopy(target),'original_content_binding':None if raw is None else {'ref':target['content']['content_ref'],'sha256':sha(raw)},'core_binding':copy.deepcopy(core_binding),
                'requested_effect':target['requested_effect'],'admission_posture':'unadmitted-proposed-effect'})
            ordered.append({'decision_ref':core['decision_ref'],'decision_core_sha256':core_binding['sha256'],'scope_ref':proposal['scope_ref'],
                'owner_ref':route['required_owner_voices'][0]['principal']['identity_ref'],'effect_kind':core['category']+':'+core['operation'],
                'target_refs':[selected['version_ref']],'target_digests':[{'target_ref':selected['version_ref'],'sha256':selected['byte_sha256']}],'selected_outcome':None})
        identity=sha(P.compact({'original_review_sha256':sha(original_message),'routing_sha256':self.routing_pin}))
        bundle_id='decision-bundle:R03-exact-review:'+identity;checkpoint_id='decision-checkpoint:R03-exact-review:'+identity
        invalidation=list(dict.fromkeys(profile['payload']['invalidation_conditions']+preference['payload']['invalidation_conditions']+
            ['any-target-original-byte-change','source-cut-or-profile-change','owner-routing-or-current-authority-change','validation-or-example-change','new-runtime-or-external-effect']))
        common_evidence=[message['proposal_binding'],message['validation_report_binding'],*message['stable_core_bindings']]
        bundle,bundle_ref,bundle_object=self.record('decision-bundle',bundle_id,{'ordered_decisions':ordered,'bundle_digest':sha(P.compact(ordered)),
            'all_targets_materialized':True,'atomicity_requirement':'all-or-nothing','checkpoint_ref':checkpoint_id,'invalidation_conditions':invalidation},common_evidence,self.routing['accountable_owner']['identity_ref'],profile)
        checkpoint,checkpoint_ref,checkpoint_object=self.record('decision-checkpoint',checkpoint_id,{'workflow_instance_ref':self.routing['workflow_protocol']['reference'],
            'workflow_profile_ref':self.routing['workflow_decision_profile']['version_ref'],'resolved_preference_ref':self.routing['user_decision_preference']['version_ref'],
            'decision_bundle_ref':bundle_id,'checkpoint_kind':'final-review','presentation_state':'pending','opened_at':self.routing['not_before'],'closed_at':None},common_evidence,self.routing['accountable_owner']['identity_ref'],profile)
        manifest={'schema_version':'lab-exact-review-materialization/v1-candidate','package_ref':'review-package:R03:'+identity,'base_cut':message['source_cut'],
            'source_API_binding':{'ref':str((API/'source-manifest.json').relative_to(ROOT)),'sha256':self.source_pin},
            'original_review_binding':self.vault.object(original_message),'proposal_binding':message['proposal_binding'],'validation_report_binding':message['validation_report_binding'],
            'original_semantic_and_operational_gaps':copy.deepcopy(message['gaps']),'input_posture':message['posture'],'targets':target_materials,
            'ordered_core_bindings':copy.deepcopy(message['stable_core_bindings']),'ordered_required_owner_responses':required,
            'workflow_decision_profile':copy.deepcopy(self.routing['workflow_decision_profile']),'preference':copy.deepcopy(self.routing['user_decision_preference']),
            'preference_basis':self.routing['preference_basis'],'preference_current_admission_claimed':self.routing['preference_basis']=='current-source',
            'workflow_protocol':copy.deepcopy(self.routing['workflow_protocol']),'workflow_protocol_is_WorkflowRun_artifact':False,
            'routing_original_binding':P.binding('owned-review-routing:'+self.routing_pin,W.read_private(self.path)),
            'generated_carriers':[{'artifact':bundle_ref,'object_binding':bundle_object},{'artifact':checkpoint_ref,'object_binding':checkpoint_object}],
            'example_bindings':copy.deepcopy(message['example_bindings']),'declared_consequence_bindings':copy.deepcopy(message['declared_consequence_bindings']),
            'private_public_review_binding':copy.deepcopy(message['private_public_review_binding']),'human_checkpoint_count':1,'all_targets_materialized':True,
            'atomicity_requirement':'all-or-nothing','actual_owner_outcome':None,'current_owner_authority_verified':False,'repository_admissions_applied':0,
            'runtime_activations':0,'external_effect_refs':[],'invalidation_conditions':invalidation,'claim_ceiling':CLAIM,'authority_effect':'none'}
        manifest_binding=self.vault.object(encoded(manifest))
        result={'schema_version':'lab-review-package/v1-candidate','package_ref':manifest['package_ref'],'base_cut':message['source_cut'],'manifest_binding':manifest_binding,
            'decision_bundle':bundle_ref,'checkpoint':checkpoint_ref,'workflow_decision_profile':copy.deepcopy(self.routing['workflow_decision_profile']),
            'ordered_core_bindings':copy.deepcopy(message['stable_core_bindings']),'validation_bindings':[message['validation_report_binding']],
            'example_bindings':copy.deepcopy(message['example_bindings']),'operational_instruction_bindings':[],'all_targets_materialized':True,
            'human_checkpoint_count':1,'atomicity_requirement':'all-or-nothing','invalidation_conditions':invalidation,'authority_effect':'none'}
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:review-package:v1-candidate',result),'actual review package violates original API result schema')
        self.guard();return copy.deepcopy(result),[manifest_binding,bundle_object,checkpoint_object,*evidence]
