"""Actual prospective target validation; no publisher, signature or owner outcome."""
import copy
from .handlers import ApplicationError,cut,gap
from .protocol import *
from .workspace import privacy
from . import artifact_model as model
CLAIM='Exact prospective construction checks only. No owner approval, Work satisfaction, committed Project State, activation or operational acceptance.'

class CandidateHandlers:
    def __init__(self,readers,vault,schemas):self.readers=readers;self.vault=vault;self.schemas=schemas
    def preflight(self,message,outer):
        observed=self.readers.selected_cut({'source_cut':message['base_cut']},outer)
        if observed!=cut(self.readers.view):raise ApplicationError('stale-cut','Candidate effects require the current selected head, not a historical prefix.')
        view=self.readers.selected_view;config=view.data['config']
        if message['scope_ref']!=config['scope_ref']:raise ApplicationError('unauthorized','Candidate target scope differs from independently provisioned workspace.')
        expected={'ref':view.handle.manifest['profile_binding']['path'],'sha256':view.handle.manifest['profile_binding']['sha256']}
        if message['source_profile_binding']!=expected:raise ApplicationError('invalid-contract','Candidate source profile differs from the selected executable profile.')
        if message['workspace_binding']!=self.vault.control_binding:raise ApplicationError('invalid-contract','Candidate does not select this exact independently provisioned material vault.')
        if message['challenge_route']!=config['challenge_route']:raise ApplicationError('invalid-contract','Candidate challenge route differs from provisioned scope.')
        if len(message['targets'])>64:raise ApplicationError('budget-exceeded','Candidate target bound exceeded.')
        self.vault.guard();return observed
    def validate(self,message,request,outer,inner):
        observed=self.preflight(message,outer);view=self.readers.selected_view;config=view.data['config'];vault=self.vault
        proposal_binding=vault.object(inner);evidence=[];checks=[];refs=[];gaps=[];runtime_targets=[];cores=[];diffs=[]
        def check(name,result,details,bindings):
            b=vault.object(source.encoded({'check':name,'result':result,'details':details,'inputs':bindings,'authority_effect':'none'}));evidence.append(b)
            checks.append({'check_ref':'check:'+name,'obligation_ref':'candidate:'+name,'result':result,'evidence_bindings':[b],'claim_ceiling':CLAIM})
        try:
            schemas={};schema_bytes={}
            for b in message['schema_bindings']:
                raw=vault.material(b);doc=source.parse(raw)
                selected=vault.inputs[b['ref']]['path'];path='runtime/schemas/'+Path(selected).name
                source.require(path not in schemas,'duplicate schema destination');schemas[path]=doc;schema_bytes[path]=raw
            for b in message['evidence_bindings']:vault.material(b)
            for index,target in enumerate(message['targets']):
                h=target['artifact'];version=h['version_ref'];source.require(h['scope_ref']==config['scope_ref'],'candidate header scope differs')
                selected=vault.manifest['target_metadata'].get(version);source.require(selected is not None,'target metadata is not independently selected')
                meta=source.parse(vault.material(selected))
                source.require(set(meta)=={'schema_version','category','decision_ref','contract'} and meta['schema_version']=='lab-candidate-target-metadata/v1-candidate','closed target metadata required')
                source.require(meta['category'] in view.handle.operations.CATEGORIES and isinstance(meta['decision_ref'],str) and meta['decision_ref'],'target category/Decision identity invalid')
                record=None;raw=None;content=target['content'];prior=None
                if target['operation']!='admit':
                    prior=self.readers.resolve_exact(target['predecessor'])
                    source.require(prior['effective_state'] in ('admitted-current','local-admitted-current'),'exact current predecessor required')
                    refs.append({'source_version_ref':version,'selector':'/predecessor','requested_ref':prior['version_ref'],
                        'resolved_ref':model.artifact_ref(view,prior),'posture':'resolved'})
                if target['operation']=='withdraw':
                    source.require({k:h[k] for k in ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')}==target['predecessor'],'withdraw target must bind exact current predecessor')
                else:
                    source.require(target['candidate_binding']==selected,'target metadata binding differs from independently selected version')
                    raw=vault.material({'ref':content['content_ref'],'sha256':content['byte_sha256']})
                    source.require(len(raw)==content['size_bytes'] and content['media_type']=='application/json' and source.sha(raw)==h['byte_sha256'],'original candidate content/header differs')
                    record=source.parse(raw);privacy(record)
                    contract=view.data['projection']['contracts'].get(h['carrier_ref'])
                    source.require(contract is not None,'carrier not in selected catalog')
                    if 'candidate_contract_binding' in h:
                        source.require(h['candidate_contract_binding']=={'ref':contract['schema_path'],'sha256':contract['schema_sha256']},'candidate contract binding differs')
                    identity=view.handle.common.identity(record,contract['artifact'].get('instance_contract',{}).get('identity_field')) if meta['category']!='artifact-type' else record['artifact_type_ref'].rsplit('/',1)[0]
                    source.require(identity==h['identity_ref'],'candidate body/header identity differs')
                runtime_target={'category':meta['category'],'operation':target['operation'],'version_ref':version,
                    'carrier_ref':h['carrier_ref'],'record':record,'predecessor_ref':target['predecessor']['version_ref'] if target['predecessor'] else None,
                    'decision_ref':meta['decision_ref'],'contract':meta['contract']}
                if view.selected['name']=='custody-participation':
                    runtime_target['content']=None if target['operation']=='withdraw' else view.handle.custody.content_entry(raw)
                core={'decision_ref':meta['decision_ref'],'category':meta['category'],'operation':target['operation'],'version_ref':version,'target_digest':view.handle.common.digest(runtime_target)}
                coreraw=vault.material(target['decision_core_binding'])
                source.require(coreraw==view.handle.common.encoded(core),'independent stable Decision core does not match exact selected target')
                cores.append(target['decision_core_binding']);runtime_targets.append(runtime_target)
                diffs.append({'artifact':h,'operation':target['operation'],'predecessor':target['predecessor'],
                    'before':copy.deepcopy(prior['record']) if prior else None,'after':record,'requested_effect':target['requested_effect'],
                    'stable_core_binding':target['decision_core_binding'],'effective_admission':'unadmitted-candidate','authority_effect':'none'})
            runtime_proposal={'schema_version':'lab-runtime-proposal/v1','proposal_id':message['proposal_ref'],
                'expected_head':view.data['head']['transaction_digest'],'source_snapshot_digest':config['source_snapshot_digest'],
                'scope_ref':config['scope_ref'],'policy_ref':config['policy_ref'],'challenge_route':config['challenge_route'],
                'schemas':schemas,'targets':runtime_targets}
            if view.selected['name']=='custody-participation':
                originals={t['version_ref']:view.handle.custody.decode_content(t['content']) for t in runtime_targets if t['operation']!='withdraw'}
                runtime_proposal=view.handle.custody.with_originals(runtime_proposal,originals,schema_bytes,exact_schema_bytes=True)
                source.require(runtime_proposal['targets']==runtime_targets,'raw custody changed a previously compared target core')
            before=view.handle.common.digest(view.data['projection'])
            post,actual_cores=view.handle.operations.prepare(view.data['projection'],runtime_proposal,view.data['head']['transaction_digest'],config)
            source.require(before==view.handle.common.digest(view.data['projection']),'pure prepare changed selected source projection')
            source.require(actual_cores==[source.parse(vault.material(b)) for b in cores],'backend computed cores differ')
            check('exact-source-target-schema-core', 'pass',{'target_count':len(runtime_targets),'backend_projection_simulated_only':True,
                'runtime_proposal_sha256':view.handle.common.digest(runtime_proposal),'source_projection_unchanged':True},[proposal_binding,*cores])
            # Every declared connection must be an explicit proposed relation target.
            # Endpoint headers retain original candidate bytes and exact source revisions.
            headers={t['artifact']['version_ref']:{k:t['artifact'][k] for k in ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')} for t in message['targets'] if t['operation']!='withdraw'}
            for c in message['connection_proposals']:
                matches=[t for t in runtime_targets if t['category']=='typed-relation' and t['operation']!='withdraw'
                    and t['record']['payload']['relation_kind_ref']==c['relation_kind_ref']
                    and t['record']['payload']['source']['version_ref']==c['source']['artifact']['version_ref']
                    and t['record']['payload']['target']['version_ref']==c['target']['artifact']['version_ref']
                    and t['record']['payload']['qualifiers']==c['qualifiers']]
                source.require(len(matches)==1,'connection lacks one explicit exact proposed relation target')
                record,b=model.signature(view,c['relation_kind_ref'])
                source.require(c['signature_sha256']==b['sha256'] and c['axis_ref']==record['payload']['axis_id'],'connection signature/axis differs')
                for key in ('source','target'):
                    header=c[key]['artifact'];subject=post['subjects'][header['version_ref']]
                    expected=headers.get(header['version_ref']) or model.artifact_ref(view,view.subjects[header['version_ref']])
                    source.require(header==expected and view.handle.operations.endpoint_kind(subject,post)==c[key]['semantic_kind'],'connection exact endpoint differs')
            check('declared-typed-connection-closure','pass',{'explicit_connections':len(message['connection_proposals'])},[proposal_binding])
            # Do not invent a generic resolver for unspecified domain reference semantics.
            # Such obligations remain not-evaluable until a carrier-specific resolver exists.
            for t in runtime_targets:
                if t['operation']=='withdraw':continue
                record=t['record'];unresolved=[]
                for relation in record.get('relation_refs',[]):
                    ref=relation.get('counterpart_ref')
                    if not ref:continue
                    matches=[s for s in post['subjects'].values() if (s['version_ref']==ref or s['identity']==ref) and s['effective_state'] in ('admitted-current','local-admitted-current')]
                    resolved=None
                    if len(matches)==1:
                        s=matches[0];resolved=headers.get(s['version_ref']) or model.artifact_ref(view,view.subjects[s['version_ref']])
                    posture='resolved' if resolved else 'ambiguous' if len(matches)>1 else 'unresolved'
                    refs.append({'source_version_ref':t['version_ref'],'selector':'/relation_refs/counterpart_ref','requested_ref':ref,'resolved_ref':resolved,'posture':posture})
                    if resolved is None:unresolved.append(ref)
                if unresolved:
                    check('domain-reference-'+source.sha(t['version_ref'].encode())[:12],'not-evaluable',{'unresolved_refs':unresolved},[proposal_binding])
                    gaps.append(gap(t['version_ref'],'Declared domain counterpart references remain unresolved; structural validation cannot substitute for semantic closure.','candidate-semantic-use'))
                if t['carrier_ref']=='cal.artifact-type.work/v1':
                    payload=record['payload'];missing=[]
                    selectors=[('/payload/project_ref',payload['project_ref'],'project')]
                    selectors += [('/payload/'+key+'/'+str(i),ref,'goal' if key=='goal_refs' else None)
                        for key in ('goal_refs','input_refs','output_refs') for i,ref in enumerate(payload[key])]
                    for selector,ref,kind in selectors:
                        matches=[s for s in post['subjects'].values() if (s['version_ref']==ref or s['identity']==ref)
                            and s['effective_state'] in ('admitted-current','local-admitted-current')]
                        resolved=None
                        if len(matches)==1:
                            s=matches[0]
                            semantic=view.handle.operations.endpoint_kind(s,post)
                            if kind is None or semantic==kind:resolved=headers.get(s['version_ref']) or model.artifact_ref(view,view.subjects[s['version_ref']])
                        refs.append({'source_version_ref':t['version_ref'],'selector':selector,'requested_ref':ref,
                            'resolved_ref':resolved,'posture':'resolved' if resolved else 'ambiguous' if len(matches)>1 else 'unresolved'})
                        if resolved is None:missing.append({'selector':selector,'requested_ref':ref})
                    check('work-domain-reference-'+source.sha(t['version_ref'].encode())[:12], 'not-evaluable' if missing else 'pass',
                        {'unresolved_refs':missing,'resolver':'exact current Work project/Goal/input/output references'},[proposal_binding])
                    if missing:gaps.append(gap(t['version_ref'],'Work Goal/input/output closure is incomplete in this exact selected cut. The missing references require selected material or a declared resolver before semantic use.','candidate-semantic-use'))
                elif t['category'] not in ('typed-relation','artifact-type','relation-kind'):
                    check('remaining-domain-reference-'+source.sha(t['version_ref'].encode())[:12],'not-evaluable',
                        {'carrier_ref':t['carrier_ref'],'reason':'Carrier-specific full domain reference resolver is not yet implemented in this package.'},[proposal_binding])
                    gaps.append(gap(t['version_ref'],'Exact schema/core checks do not close every carrier-specific domain reference obligation; semantic use remains blocked.','candidate-semantic-use'))
            check('private-boundary','pass',{'all_selected_materials_scanned':True,'session_memory_exported':False,'private_credentials_exported':False},[vault.control_binding])
        except Exception as error:
            # Refusals are observable construction evidence, never successful admission.
            check('candidate-construction-refusal','fail',{'reason':str(error)[:1000]},[proposal_binding])
            gaps.append(gap(message['proposal_ref'],'Candidate closure failed; inspect the exact bound validation check evidence.','candidate-use'))
        vault.guard();source.require(self.readers.current(),'original source changed while validating')
        report={'schema_version':'lab-validation-report/v1-candidate','report_ref':'validation:'+source.sha(inner),
            'subject_binding':proposal_binding,'source_cut':observed,'validator_binding':binding(str((HERE/'candidate.py').relative_to(ROOT)),(HERE/'candidate.py').read_bytes()),
            'checks':checks,'reference_checks':refs,'gaps':gaps,'result':'fail' if any(c['result']=='fail' for c in checks) else 'not-evaluable' if gaps else 'pass',
            'claim_ceiling':CLAIM,'authority_effect':'none'}
        source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:validation-report:v1-candidate',report),'constructed validation report shape differs')
        report_binding=vault.object(source.encoded(report));evidence.append(report_binding)
        return report,{'proposal_binding':proposal_binding,'report_binding':report_binding,'cores':cores,'diffs':diffs,'evidence':evidence}
    def prepare(self,message,request,outer,inner):
        report,details=self.validate(message,request,outer,inner);vault=self.vault
        if not details['cores']:raise ApplicationError('invalid-contract','No exact stable core was validated; inspect the recorded construction refusal before new preparation.')
        examples=vault.object(source.encoded({'schema_version':'lab-candidate-target-diff/v1-candidate','targets':details['diffs'],'authority_effect':'none'}))
        effects=vault.object(source.encoded({'schema_version':'lab-candidate-effects/v1-candidate','targets':[{'version_ref':t['artifact']['version_ref'],'requested_effect':t['requested_effect']} for t in message['targets']],
            'current_effect':'candidate evidence staging only','canonical_admissions':0,'signed_transactions':0,'owner_outcome':None,'authority_effect':'none'}))
        privacy_binding=vault.object(source.encoded({'schema_version':'lab-candidate-private-public-review/v1-candidate','selected_inputs_checked':True,
            'session_memory_exported':False,'private_keys_exported':False,'public_export_permitted':False,'claim_ceiling':'Private scoped candidate custody only; publication requires its own selected review.','authority_effect':'none'}))
        # Full owner/operational obligations are explicit; construction pass is separate.
        review={'schema_version':'lab-proposal-review/v1-candidate','proposal_binding':details['proposal_binding'],'source_cut':report['source_cut'],
            'validation_report_binding':details['report_binding'],'stable_core_bindings':details['cores'],'example_bindings':[examples],
            'declared_consequence_bindings':[effects],'private_public_review_binding':privacy_binding,
            'gaps':[*report['gaps'],gap(message['proposal_ref'],'Construction evidence is staged. Final owner/operational review closure belongs to S02/R08; proposal.review is not implemented here.','admission')],
            'posture':'blocked','authority_effect':'none'}
        source.require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:proposal-review:v1-candidate',review),'constructed proposal review shape differs')
        return review,[*details['evidence'],examples,effects,privacy_binding]
    def inspect(self,message,request,outer):
        if outer is not None and outer!=cut(self.readers.view):raise ApplicationError('invalid-contract','Operation inspection does not select a different artifact cut.')
        claim,result=self.vault.lookup(message['lookup'],self.vault.channel.context)
        if claim is None:raise ApplicationError('not-found','No operation record exists in this independently selected principal namespace. Absence does not authorize a prior effect replay.')
        return {'schema_version':'lab-operation-inspect-result/v1-candidate','request_binding':request,'original_call_binding':claim['original_call_binding'],
            'operation':claim['operation'],'posture':result['posture'] if result else 'indeterminate',
            'result_binding':result['domain_binding'] if result else None,'effect_evidence_bindings':result['evidence_bindings'] if result else [claim['original_call_binding']],
            'reconciliation_required':result is None,'retry_allowed':False,
            'gaps':[] if result else [gap(claim['namespace'],'A durable claim exists without a complete verified result. Inspect/reconcile; never redispatch.','retry')],
            'claim_ceiling':'Private principal-scoped candidate invocation metadata only; inspection never redispatches effects or restores Agent memory.','authority_effect':'none'}
