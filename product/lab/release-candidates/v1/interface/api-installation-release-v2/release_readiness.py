"""Fresh exact readiness closure; signed observations are required, never synthesized."""
import base64
from datetime import timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from .protocol import source, compact, ROOT, HERE
from jsonschema import Draft202012Validator
from .auth import now, instant
from .handlers import gap, ApplicationError, cut

KINDS={'api-qualification','human-pilot','acceptance','privacy','installation','review-closure'}

class ReleaseReadiness:
    def __init__(self, builder, selected_binding):
        self.builder=builder;self.host=builder.host;self.read=builder.read;self.binding=selected_binding
        self.contract=source.parse(self.read(selected_binding))
        schema=source.parse((HERE/'release-readiness-contract.schema.json').read_bytes());source.require(Draft202012Validator(schema,registry=self.host.schemas.registry,format_checker=self.host.schemas.checker).is_valid(self.contract),'readiness contract violates exact selected schema')
        source.require(set(self.contract)=={'schema_version','manifest_binding','source_cut','acceptance_scope_binding','evidence_requirements','signers','owner_prerequisites','authority_effect','actual_owner_outcome'},'closed release readiness contract required')
        source.require(self.contract['schema_version']=='lab-release-readiness-contract/v1-candidate' and self.contract['authority_effect']=='none' and self.contract['actual_owner_outcome'] is None,'readiness contract cannot convey owner approval')
        source.require(isinstance(self.contract['evidence_requirements'],list) and isinstance(self.contract['signers'],list) and isinstance(self.contract['owner_prerequisites'],list),'closed readiness arrays required')
        source.require(len({s['signer_ref'] for s in self.contract['signers']})==len(self.contract['signers']),'duplicate reviewer signer selection')

    @staticmethod
    def verify_signature(public_b64, payload, signature_b64):
        Ed25519PublicKey.from_public_bytes(base64.b64decode(public_b64,validate=True)).verify(base64.b64decode(signature_b64,validate=True),compact(payload))

    def attested(self, row, manifest_binding, outer):
        source.require(set(row)=={'obligation_refs','kind','evidence_binding','attestation_binding','signer_ref'},'closed selected evidence requirement')
        source.require(row['kind'] in KINDS and row['obligation_refs'],'unsupported or unscoped readiness evidence')
        raw=self.read(row['evidence_binding']);document=source.parse(raw)
        selected=next((s for s in self.contract['signers'] if s['signer_ref']==row['signer_ref']),None)
        source.require(selected is not None and set(selected)=={'signer_ref','principal_ref','public_key_binding','role_assignment','allowed_kinds'},'independent reviewer signer selection missing')
        source.require(row['kind'] in selected['allowed_kinds'],'reviewer lacks exact evidence responsibility')
        assignment=self.host.handlers.resolve_exact(selected['role_assignment'])
        source.require(assignment['effective_state'] in ('admitted-current','local-admitted-current'),'reviewer assignment is not current')
        role=assignment['record'];source.require(role['kind']=='role-assignment' and role['assignment_state']=='active' and role['assignee_ref']==selected['principal_ref'] and role['assignee_kind']=='person-reference','reviewer assignment is inactive or names another person')
        source.require(role['scope_ref'] in self.host.channel.context['scope_refs'],'reviewer assignment does not cover this actual selected scope')
        source.require(instant(role['period']['start'])<=now() and (role['period']['end'] is None or now()<instant(role['period']['end'])),'reviewer assignment period is not current')
        public=source.parse(self.read(selected['public_key_binding']))
        source.require(set(public)=={'schema_version','principal_ref','public_key_b64','authority_effect'} and public['schema_version']=='lab-release-reviewer-public-key/v1-candidate' and public['principal_ref']==selected['principal_ref'] and public['authority_effect']=='none','independent reviewer public key differs')
        attestation=source.parse(self.read(row['attestation_binding']))
        source.require(set(attestation)=={'schema_version','payload','signature_b64','authority_effect'},'closed evidence attestation required')
        payload=attestation['payload']
        source.require(payload=={'evidence_binding':row['evidence_binding'],'manifest_binding':manifest_binding,'source_cut':outer,'obligation_refs':row['obligation_refs'],'kind':row['kind'],'principal_ref':selected['principal_ref'],'role_assignment':selected['role_assignment'],'authority_effect':'none'},'signed reviewer scope differs from exact independent closure')
        source.require(attestation['schema_version']=='lab-release-evidence-attestation/v1-candidate' and attestation['authority_effect']=='none','evidence signature grants no release authority')
        self.verify_signature(public['public_key_b64'],payload,attestation['signature_b64'])
        source.require(isinstance(document,dict) and document.get('authority_effect')=='none','evidence must preserve candidate authority ceiling')
        return document

    def validate(self, manifest, manifest_binding, outer):
        contract=self.contract;gaps=[];verified=[]
        source.require(contract['manifest_binding']==manifest_binding and contract['source_cut']==outer==cut(self.host.handlers.view),'readiness contract selects different exact candidate/cut')
        scope=source.parse(self.read(contract['acceptance_scope_binding']))
        source.require(scope['schema_version']=='lab-product-release-scope/v1-candidate' and scope['authority_effect']=='none','actual predeclared Product acceptance scope required')
        operations=set(scope['operations']);source.require(len(operations)==34 and operations==set(self.host.schemas.operations),'complete original34operation scope required')
        expected={row['id'] for row in scope['candidate_acceptance']};source.require(expected=={'AC'+str(i).zfill(2) for i in range(1,14)},'complete13predeclared Product conditions required')
        coverage={};kinds=set()
        for requirement in contract['evidence_requirements']:
            subjects=requirement['obligation_refs'];source.require(set(subjects)<=expected,'undeclared readiness obligation')
            kinds.add(requirement['kind'])
            for ref in subjects:coverage.setdefault(ref,[]).append(requirement)
            try:
                document=self.attested(requirement,manifest_binding,outer)
                kind=requirement['kind']
                source.require(document.get('schema_version')=='lab-release-readiness-evidence/v1-candidate' and set(document)=={'schema_version','kind','manifest_binding','source_cut','obligation_refs','result','source_bindings','observations','claim_ceiling','authority_effect'},'exact readiness evidence envelope required')
                source.require(document['kind']==kind and document['manifest_binding']==manifest_binding and document['source_cut']==outer and document['obligation_refs']==subjects and document['result']=='pass','selected actual readiness observation is absent, failed or scope differs')
                source.require(document['source_bindings'] and document['claim_ceiling'],'actual bound source evidence and claim ceiling required')
                originals=[self.read(b) for b in document['source_bindings']]
                observations=document['observations']
                if kind=='api-qualification':self.api(observations,originals,operations)
                elif kind=='human-pilot':self.pilot(observations,originals,manifest)
                elif kind=='acceptance':
                    source.require(set(observations)=={'condition_results','measurement_bindings','candidate_operation_only'} and observations['candidate_operation_only'] is True,'exact measured candidate acceptance observation required')
                    source.require(set(observations['condition_results'])==set(subjects) and all(v=='pass' for v in observations['condition_results'].values()) and observations['measurement_bindings'],'all named conditions must be actually evaluated')
                    for b in observations['measurement_bindings']:self.read(b)
                elif kind=='privacy':
                    source.require(set(observations)=={'privacy_review_binding','checked_material_bindings','private_credentials_present','session_memory_present','publication_allowed'} and observations['privacy_review_binding']==manifest['privacy_review_binding'] and observations['private_credentials_present'] is False and observations['session_memory_present'] is False and observations['publication_allowed'] is False,'exact privacy review or excluded material differs')
                    for b in observations['checked_material_bindings']:self.read(b)
                    source.require(set((b['ref'],b['sha256']) for b in manifest['implementation_bindings']+manifest['package_bindings'])<=set((b['ref'],b['sha256']) for b in observations['checked_material_bindings']),'privacy review omits release materials')
                elif kind=='installation':
                    source.require(set(observations)=={'receipt_bindings','environment_bindings','service_activation_count'} and observations['service_activation_count']==0 and observations['environment_bindings']==manifest['supported_environment_bindings'],'installation environment/effect scope differs')
                    receipts=[source.parse(self.read(b)) for b in observations['receipt_bindings']]
                    source.require(receipts and all(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:installation-receipt:v1-candidate',v) and v['posture'] in ('installed','rolled-back') and v['recovery_required'] is False for v in receipts),'actual complete verified installation receipts required')
                    for receipt in receipts:
                        source.require(receipt['release_manifest_binding']==manifest_binding,'installation receipt selects different candidate');self.read(receipt['postimage_binding'])
                        for b in receipt['verification_bindings']:self.read(b)
                elif kind=='review-closure':
                    source.require(set(observations)=={'member_bindings','closure_bindings','digest_edges','open_gaps','acyclic_digest_graph','owner_review_preconditions_resolved','final_release_decision_required'} and observations['open_gaps']==[] and observations['acyclic_digest_graph'] is True and observations['owner_review_preconditions_resolved'] is True and observations['final_release_decision_required'] is True,'actual exact final member closure or review precondition missing')
                    expected_members=manifest['implementation_bindings']+manifest['package_bindings']+manifest['acceptance_contract_bindings']+manifest['pilot_evidence_bindings']+[manifest['privacy_review_binding']]+manifest['validation_bindings']+[manifest['install_contract_binding']]+manifest['supported_environment_bindings']
                    source.require(set((b['ref'],b['sha256']) for b in observations['member_bindings'])==set((b['ref'],b['sha256']) for b in expected_members),'review closure omits or adds candidate members')
                    self.graph(observations,expected_members+[manifest_binding])
                verified.extend([requirement['evidence_binding'],requirement['attestation_binding']])
            except Exception:
                for ref in subjects:gaps.append(gap(ref,'Actual independently signed '+requirement['kind']+' evidence is absent, invalid, incomplete or does not match this exact release.','release-review-readiness'))
        for ref in sorted(expected-set(coverage)):gaps.append(gap(ref,'Predeclared Product acceptance condition has no independently selected actual evidence.','release-review-readiness'))
        for kind in sorted(KINDS-kinds):gaps.append(gap(kind,'Required actual readiness evidence class has not been independently selected.','release-review-readiness'))
        for header in contract['owner_prerequisites']:
            try:
                subject=self.host.handlers.resolve_exact(header)
                source.require(subject['effective_state'] in ('admitted-current','local-admitted-current'),'owner prerequisite is not current')
                record=subject['record'];source.require(record['kind']=='decision' and record.get('payload',record).get('outcome') in ('approved','approve-exact-scope'),'owner prerequisite lacks actual positive Decision')
            except Exception:gaps.append(gap(header['version_ref'],'An independently selected prior owner prerequisite is unresolved; no owner outcome is inferred.','release-review-readiness'))
        self.builder.guard()
        return {'result':'blocked' if gaps else 'ready-for-final-review','gaps':gaps,'verified_bindings':verified,'contract_binding':self.binding,'release_decision_created':False,'whole_lab_release_approved':False,'authority_effect':'none'}

    def graph(self, observed, roots):
        bindings=observed['closure_bindings'];keys=[(b['ref'],b['sha256']) for b in bindings]
        source.require(len(keys)==len(set(keys)) and set((b['ref'],b['sha256']) for b in roots)<=set(keys),'unique complete digest closure required')
        nodes=set(keys);actual=set()
        def walk(value):
            if isinstance(value,dict):
                if set(value)=={'ref','sha256'}:yield (value['ref'],value['sha256'])
                elif set(value)=={'path','sha256'}:yield (value['path'],value['sha256'])
                else:
                    for child in value.values():yield from walk(child)
            elif isinstance(value,list):
                for child in value:yield from walk(child)
        for b in bindings:
            raw=self.read(b)
            if raw.lstrip().startswith((b'{',b'[')):
                for dependency in walk(source.parse(raw)):
                    source.require(dependency in nodes,'bound original digest dependency omitted from closure')
                    actual.add(((b['ref'],b['sha256']),dependency))
        declared=set()
        for edge in observed['digest_edges']:
            source.require(set(edge)=={'source','dependency'},'closed digest edge required')
            pair=((edge['source']['ref'],edge['source']['sha256']),(edge['dependency']['ref'],edge['dependency']['sha256']))
            source.require(pair[0] in nodes and pair[1] in nodes,'digest edge outside exact closure');declared.add(pair)
        source.require(actual==declared,'declared digest graph differs from actual original bindings')
        active=set();done=set();adj={key:[] for key in nodes}
        for origin,target in actual:adj[origin].append(target)
        def visit(key):
            source.require(key not in active,'cyclic release digest graph')
            if key in done:return
            active.add(key)
            for target in adj[key]:visit(target)
            active.remove(key);done.add(key)
        for key in nodes:visit(key)

    def api(self, observed, originals, operations):
        source.require(set(observed)=={'source_binding','profile_binding','aggregate_receipt_binding','terminal_bindings','wire_bindings','operations','inherited_case_count','complete_case_count'},'closed full API qualification observations')
        source.require(set(observed['operations'])==operations==set(self.host.schemas.profile['implemented_operations']),'actual API does not implement all34operations')
        source.require(observed['profile_binding']==self.host.schemas.profile_binding and observed['inherited_case_count']>=323 and observed['complete_case_count']>=observed['inherited_case_count'],'actual exact API profile/inherited qualification differs')
        source.require(observed['source_binding']['ref'].endswith('/source-manifest.json'),'actual API source manifest binding required');self.read(observed['source_binding'])
        expected_source=self.host.schemas.profile_path.parent/'source-manifest.json';source.require(observed['source_binding']['ref']==str(expected_source.relative_to(ROOT)),'qualified source belongs to another API')
        from .guard import verify
        verify(observed['source_binding']['sha256'])
        report=source.parse(self.read(observed['aggregate_receipt_binding']));source.require(report['result']=='PASS' and report['tests_run']==report['expected_tests'] and report['tests_run']==observed['complete_case_count'] and report['whole_API_qualified'] is True,'complete actual aggregate API qualification absent')
        source.require(len(report['cases'])==report['tests_run'] and all(c['result']=='PASS' for c in report['cases']),'aggregate API cases are absent or not all passing')
        source.require(observed['terminal_bindings'] and observed['wire_bindings'],'actual terminal and wire evidence required')
        for b in observed['terminal_bindings']:
            terminal=source.parse(self.read(b));source.require(terminal['exit_code']==0,'qualified process did not exit successfully')
        covered=set()
        for b in observed['wire_bindings']:
            rows=source.parse(self.read(b));source.require(isinstance(rows,list) and rows,'actual public call observations required')
            for row in rows:
                request=row['request'];reply=row['reply'];source.require(self.host.schemas.valid('api-call',request),'recorded API request violates actual schema')
                source.require(self.host.schemas.valid('api-reply',reply),'recorded API reply violates actual schema')
                source.require(reply['operation']==request['operation'] and reply['call_id']==request['call_id'] and request['expected_contract_profile_binding']==observed['profile_binding'] and reply['contract_profile_binding']==observed['profile_binding'],'exact actual public API binding mismatch')
                covered.add(request['operation'])
        source.require(covered==operations,'recorded actual public conformance omits an operation')

    def pilot(self, observed, originals, manifest):
        source.require(set(observed)=={'protocol_binding','episode_binding','participant_ref','actual_human_responses_binding','attempts_binding','qualified_api_profile_binding','journeys','baseline_recorded','improvement_claim','permission_binding','fixture_evidence'},'closed genuine human pilot observations required')
        source.require(observed['fixture_evidence'] is False and observed['participant_ref'] and observed['qualified_api_profile_binding']==self.host.schemas.profile_binding and set(observed['journeys'])=={'engineering','research','fresh-session'},'genuine actual participant and all three journeys required')
        if not observed['baseline_recorded']:source.require(observed['improvement_claim'] is False,'missing baseline cannot establish improvement')
        self.read(observed['protocol_binding']);self.read(observed['episode_binding']);self.read(observed['permission_binding'])
        responses=source.parse(self.read(observed['actual_human_responses_binding']));attempts=source.parse(self.read(observed['attempts_binding']))
        source.require(responses['participant_ref']==observed['participant_ref'] and responses['enrollment_response'] and responses['usefulness_response'] and responses['source_conversation'],'actual human enrollment/usefulness response and custody source required')
        source.require(isinstance(attempts,list) and attempts,'actual pilot attempts are absent')
        coverage=set()
        for attempt in attempts:
            source.require(set(attempt)=={'journey','question','criterion','actual_answer','started_at','finished_at','elapsed_seconds','result','request_reply_bindings','participant_response_binding','negative_findings','claim_ceiling'},'closed actual pilot attempt required')
            source.require(attempt['journey'] in observed['journeys'] and attempt['question'] and attempt['criterion'] and attempt['actual_answer'] and attempt['claim_ceiling'],'actual task or answer missing')
            elapsed=(instant(attempt['finished_at'])-instant(attempt['started_at'])).total_seconds();source.require(elapsed>=0 and abs(elapsed-attempt['elapsed_seconds'])<0.001 and instant(attempt['finished_at'])<=now(),'actual pilot clock observations differ')
            source.require(attempt['result'] in ('success','failure','unavailable','unresolved') and attempt['request_reply_bindings'],'preserve actual pilot outcomes, negatives and operation evidence')
            for b in [*attempt['request_reply_bindings'],attempt['participant_response_binding']]:self.read(b)
            coverage.add(attempt['journey'])
        source.require(coverage==set(observed['journeys']),'actual pilot observations omit a required journey')
