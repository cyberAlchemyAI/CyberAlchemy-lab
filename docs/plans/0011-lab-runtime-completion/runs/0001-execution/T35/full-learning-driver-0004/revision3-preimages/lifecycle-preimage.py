def source8_lifecycle(stack,H,M,D,selected,parent,selection,events,roots):
 P=M['protocol'];A=M['auth'];view=selected.view;sid=selection['session_ref'];resource=parent.sessions.live[sid]
 item=next(item for item in selection['items'] if item['posture']=='selected');lesson=item['lesson']
 selection_binding=parent.vault.object(P.compact(selection));instruction=selection['instruction_precedence_binding'];applicability=item['applicability_check_binding']
 root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-Source8-application-action-0148-')));root.chmod(0o700);roots.append(str(root))
 body=P.source.parse((P.ROOT/'authority/artifact-types/lesson-application/v1/fixtures/valid/record.json').read_bytes())
 body.update(node_id='lesson-application:Source8-'+__import__('uuid').uuid4().hex,owner_ref=D.records.PRINCIPAL,scope_ref=selected.sources.scope_ref,
             evidence_refs=[lesson['version_ref']],claim_ceiling='Controlled unadmitted application candidate; no Tool dispatch or effectiveness claim.')
 body['payload'].update(lesson_revision_ref=lesson['version_ref'],session_ref=sid,applicability_assessment_ref=applicability['ref'],
                        intended_influence='Record the exact reviewed fixture Lesson in this actual Session candidate.',conflict_refs=[],override_refs=[],application_posture='candidate-attributed-no-tool-dispatch')
 body['relation_refs']=[{'relation_kind_ref':'relation.applies-lesson','direction':'source','counterpart_kind':'operational-lesson','counterpart_ref':lesson['version_ref']}]
 materials,metadata,target=H.candidate_materials(M,view,body,'fixture:application')
 key,path,_=H.provision(M,root,D,selected,'source8-lesson-fixture-participation',materials,kind='lab-local-lesson-application-policy/v2-candidate',metadata=metadata)
 policy=P.frame_parse(path.read_bytes());operation_key='Source8:actual-application';proposal=H.proposal_before_auth(M,view,policy,target,operation_key)
 proposal_binding=H.object_before_auth(M,root,policy,P.compact(proposal));method=P.ROOT/'product/lab/release-candidates/v1/interface/lesson-application-v3-action-0148/preparation.py';method_binding=P.binding(str(method.relative_to(P.ROOT)),method.read_bytes())
 routing={'schema_version':'lab-lesson-application-routing/v1-candidate','source_cut':selected.source_cut,'scope_ref':selected.sources.scope_ref,
          'proposal_binding':proposal_binding,'method_binding':method_binding,'selection_binding':selection_binding,'applicability_binding':applicability,
          'instruction_precedence_binding':instruction,'intended_influence':body['payload']['intended_influence'],'action_bound_refs':[],
          'override_bindings':[],'authorization_basis_binding':policy['development_authorization_binding'],'authority_effect':'none','actual_owner_outcome':None}
 routing_binding=H.object_before_auth(M,root,policy,P.compact(routing))
 policy['application_control']={'routing_binding':routing_binding,'method_binding':method_binding,
                               'runtime_identities':{'session_ref':sid,'agent_instance_ref':resource.agent['node_id']}}
 path.write_bytes(P.compact(policy));pin=P.source.sha(path.read_bytes());channel=A.ReaderChannel(path,pin,parent.schemas);channel.authenticate(M['fixtures'].proof(key,channel.challenge))
 manifest=P.source.parse((root/'workspace/workspace.json').read_bytes());row=parent.sessions.selected(sid)
 attachment={'schema_version':'lab-private-Source8-Session-attachment/v1-candidate','parent_source_binding':bind(API/'source-manifest.json'),
   'session_ref':sid,'agent_instance_ref':resource.agent['node_id'],'assignment':row['assignment'],'session_state_binding':row['session_state_binding'],
   'source_cut':selected.source_cut,'principal_ref':D.records.PRINCIPAL,'parent_policy_sha256':parent.channel.expected_sha,'operator_policy_sha256':pin,
   'parent_workspace_binding':parent.vault.control_binding,'operator_workspace_binding':{'ref':'workspace:'+manifest['workspace_ref'],'sha256':policy['workspace']['manifest_sha256']},
   'selection_binding':selection_binding,'applicability_binding':applicability,'instruction_precedence_binding':instruction,'authority_effect':'none'}
 bad=copy.deepcopy(attachment);bad['session_ref']='agent-session:R03-live:'+'f'*32
 before=len(list((root/'workspace/journal').glob('*.claim.json')))
 try:M['service'].Service(view,channel,parent.schemas,parent_host=parent,session_attachment_binding=bad)
 except (ValueError,KeyError):pass
 else:raise AssertionError('foreign private resource attachment unexpectedly accepted')
 assert before==len(list((root/'workspace/journal').glob('*.claim.json')))
 events.append({'case':'foreign-Session-attachment','result':'actual-refusal'})
 application=M['service'].Service(view,channel,parent.schemas,parent_host=parent,session_attachment_binding=attachment);stack.callback(application.close)
 app_api=importlib.import_module(M['service'].__package__+'.integration_dispatch').IntegrationService(application)
 actor={k:channel.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')};actor['role_assignment_refs']=[]
 message={'schema_version':'lab-lesson-application-request/v1-candidate','request_ref':'request:Source8-application','actor':actor,
   'source_cut':selected.source_cut,'lesson':lesson,'session_ref':sid,'selection_binding':selection_binding,'applicability_binding':applicability,
   'conflict_refs':[],'override_basis':[],'application_candidate_binding':P.binding('fixture:application:body',materials['fixture:application:body']),
   'authority_effect':'none'}
 call=H.call(M,application,'lesson.apply',message,key=operation_key);raw=P.compact(call);reply=pair(application,call,application.vault.root,app_api)
 events.append({'operation':'lesson.apply','raw_sha256':P.source.sha(raw),'reply':reply});assert reply.get('kind')=='result',reply
 claims=len(list((application.vault.root/'journal').glob('*.claim.json')));retry_call=copy.deepcopy(call);retry_call['call_id']+='-retry';require(retry_call['message']==call['message'] and retry_call['idempotency_key']==call['idempotency_key'],'exact operation retry must retain original message and key');retry=invoke(app_api,retry_call,'actual-completed-application-exact-retry','result',root=application.vault.root)
 assert retry.get('kind')=='result' and retry['message']==reply['message'];assert claims==len(list((application.vault.root/'journal').glob('*.claim.json')))
 events.append({'operation':'lesson.apply','case':'exact-retry','reply':retry})
 lookup=M['fixtures'].call(channel.context,'operation.inspect',None,lookup={'operation':'lesson.apply','idempotency_key':operation_key})
 inspected=invoke(app_api,lookup,'actual-completed-application-inspection','result',root=application.vault.root);events.append({'operation':'operation.inspect','reply':inspected});assert inspected.get('kind')=='result',inspected
 # Current independent observer records what these actual calls returned.
 evidence={'schema_version':'lab-controlled-application-observation/v1-candidate','source_cut':selected.source_cut,
           'application_result_sha256':P.source.sha(P.compact(reply['message'])),'inspection_result_sha256':P.source.sha(P.compact(inspected['message'])),
           'completed_claim_count':claims,'Tool_dispatches':0,'canonical_admission':False,'authority_effect':'none','actual_owner_outcome':None}
 app_header={k:target['artifact'][k] for k in ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256')}
 assess_root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-Source8-assessment-action-0148-')));assess_root.chmod(0o700);roots.append(str(assess_root))
 ceiling='Exact recorded application outcome only; no general or causal effectiveness inferred.'
 eb=P.binding('fixture:observed-application',P.compact(evidence));predicted='Prepare one exact unadmitted application candidate.';observed='Actual authenticated application result and separate scoped inspection were returned; no admission or Tool effect.'
 assessment=P.source.parse((P.ROOT/'authority/artifact-types/lesson-outcome-assessment/v1/fixtures/valid/record.json').read_bytes())
 assessment.update(node_id='lesson-outcome-assessment:Source8-'+__import__('uuid').uuid4().hex,owner_ref=D.records.PRINCIPAL,scope_ref=selected.sources.scope_ref,evidence_refs=[eb['ref']],claim_ceiling=ceiling)
 assessment['payload'].update(lesson_application_ref=app_header['version_ref'],predicted_outcome=predicted,observed_outcome=observed,
    disposition='recorded-outcome-only',evidence_refs=[eb['ref']],counterevidence_refs=[],causal_claim_ceiling=ceiling)
 assessment['relation_refs']=[{'relation_kind_ref':'relation.derives-from','direction':'source','counterpart_kind':'lesson-application','counterpart_ref':app_header['version_ref']}]
 mats,meta,ass_target=H.candidate_materials(M,view,assessment,'fixture:assessment');mats[eb['ref']]=P.compact(evidence)
 observation={'schema_version':'lab-recorded-application-outcome/v1-candidate','method_ref':'recorded-application-outcome/v1-candidate',
   'scope_ref':selected.sources.scope_ref,'source_cut':selected.source_cut,'application':app_header,'predicted_outcome':predicted,
   'observed_outcome':observed,'evidence_bindings':[eb],'counterevidence_bindings':[],'causal_claim_ceiling':ceiling,'authority_effect':'none'}
 mats['fixture:outcome-observation']=P.compact(observation)
 ak,ap,_=H.provision(M,assess_root,D,selected,'source8-lesson-fixture-participation',mats,kind='lab-local-lesson-assessment-policy/v1-candidate',metadata=meta)
 pol=P.frame_parse(ap.read_bytes());ass_key='Source8:actual-assessment';prop=H.proposal_before_auth(M,view,pol,ass_target,ass_key)
 pb=H.object_before_auth(M,assess_root,pol,P.compact(prop));method=method.parent.parent/'lesson-assessment-v2-action-0148/preparation.py';mb=P.binding(str(method.relative_to(P.ROOT)),method.read_bytes())
 route={'schema_version':'lab-lesson-assessment-routing/v1-candidate','scope_ref':selected.sources.scope_ref,'source_cut':selected.source_cut,
    'proposal_binding':pb,'method_binding':mb,'observation_binding':P.binding('fixture:outcome-observation',mats['fixture:outcome-observation']),
    'authorization_basis_binding':pol['development_authorization_binding'],'authority_effect':'none','actual_owner_outcome':None}
 rb=H.object_before_auth(M,assess_root,pol,P.compact(route));pol['assessment_control']={'routing_binding':rb,'method_binding':mb}
 pol['source8_control']['application_journal_scope']={'root':str(application.vault.root),'workspace_binding':application.vault.control_binding,'manifest_sha256':policy['workspace']['manifest_sha256']}
 ap.write_bytes(P.compact(pol));ac=A.ReaderChannel(ap,P.source.sha(ap.read_bytes()),parent.schemas);ac.authenticate(M['fixtures'].proof(ak,ac.challenge))
 assessor=M['service'].Service(view,ac,parent.schemas);stack.callback(assessor.close)
 actor={k:ac.context[k] for k in ('principal_ref','agent_instance_ref','session_ref','assignment_ref')};actor['role_assignment_refs']=[]
 msg={'schema_version':'lab-lesson-assessment-request/v1-candidate','request_ref':'request:Source8-assessment','actor':actor,'source_cut':selected.source_cut,
   'application':app_header,'assessment_candidate_binding':P.binding('fixture:assessment:body',mats['fixture:assessment:body']),
   'evidence_bindings':[eb],'counterevidence_bindings':[],'causal_claim_ceiling':ceiling,'authority_effect':'none'}
 assess_api=importlib.import_module(M['service'].__package__+'.integration_dispatch').IntegrationService(assessor)
 reply=pair(assessor,H.call(M,assessor,'lesson.assess',msg,key=ass_key),assessor.vault.root,assess_api)
 events.append({'operation':'lesson.assess','reply':reply});assert reply.get('kind')=='result',reply
 application.close();assert resource.closed is False and parent.sessions.live.get(sid) is resource
 return ['foreign-Session-attachment','actual-late-application-attachment','completed-application-exact-retry','completed-application-inspection','actual-journal-candidate-assessment','attached-close-preserves-parent']
