import copy
from dataclasses import replace
from datetime import timedelta
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from fixtures import Fixture,KINDS,ROOT
from eligibility import *


class EligibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(prefix='cal-R03-session-preflight-');self.addCleanup(self.tmp.cleanup)
        self.f=Fixture(Path(self.tmp.name))

    def rebuild(self,mutate=None,**options):
        tmp=TemporaryDirectory(prefix='cal-R03-session-preflight-case-');self.addCleanup(tmp.cleanup)
        self.f=Fixture(Path(tmp.name),mutate,**options)

    def denied_context(self,reason):
        with self.assertRaisesRegex(EligibilityFault,reason):self.f.context_plan()

    def denied_open(self,reason,**changes):
        with self.assertRaisesRegex(EligibilityFault,reason):self.f.open_plan(**changes)

    def test_actual_original_carrier_schemas_validate_all_selected_source_bytes(self):
        for row in self.f.records:self.f.sources.get(row.artifact)
        self.assertTrue(all(row.original.startswith(b'{\n   ') for row in self.f.records))

    def test_profile_eligible_context_plan_creates_no_Agent_or_permission_token(self):
        p=self.f.context_plan()
        self.assertEqual(p['goal'].artifact,self.f.refs['goal']);self.assertEqual(p['work'].artifact,self.f.refs['work'])
        self.assertFalse(p['Agent_created']);self.assertFalse(p['Session_created']);self.assertFalse(p['permission_result_is_dispatch_token'])

    def test_profile_eligible_open_plan_creates_no_Agent_or_persistent_memory(self):
        p=self.f.open_plan()
        self.assertEqual(p['agent_capability_refs'],[self.f.refs['agent-capability']['version_ref']])
        self.assertFalse(p['memory_persistence_allowed']);self.assertEqual(p['durable_continuity_source'],'project-state-via-context-and-ontology-views')

    def test_exact_reserved_fresh_instance_eligibility_is_explicit(self):
        fresh='agent-instance:R03-reserved-new-instance'
        self.rebuild(lambda b:b['agent-assignment']['payload'].update(eligible_agent_ref=fresh))
        with self.assertRaisesRegex(EligibilityFault,'another Profile'):self.f.open_plan()
        p=self.f.authority.open_plan(self.f.open(),self.f.actor,lambda _:self.f.delivery,fresh_instance_ref=fresh)
        self.assertFalse(p['Agent_created'])

    def test_old_fixed_instance_never_matches_new_instance_or_profile(self):
        self.rebuild(lambda b:b['agent-assignment']['payload'].update(eligible_agent_ref='agent-instance:old-expired'))
        self.denied_context('another Profile');self.denied_open('another Profile')

    def test_assignment_is_not_host_permission(self):
        self.f.authority.permission_reader=lambda:None
        self.denied_open('host Session permission absent')

    def test_public_actor_cannot_replace_authenticated_principal(self):
        m=self.f.open();m['actor']['principal_ref']='principal:attacker';self.denied_open('authenticated transport',**m)

    def test_wrong_host_principal(self):
        self.f.permission=replace(self.f.permission,principal_ref='principal:other');self.denied_context('principal or scope')

    def test_wrong_host_scope(self):
        self.f.permission=replace(self.f.permission,scope_ref='project:other');self.denied_open('principal or scope')

    def test_operation_not_permitted_by_host(self):
        self.f.permission=replace(self.f.permission,operations=frozenset(['context.get']));self.denied_open('does not permit')

    def test_unverifiable_host_permission(self):
        self.f.authority.permission_guard=lambda _:False;self.denied_open('evidence cannot be verified')

    def test_empty_host_permission_evidence(self):
        self.f.permission=replace(self.f.permission,evidence_bindings=());self.denied_open('evidence cannot be verified')

    def test_expired_host_permission(self):
        self.f.permission=replace(self.f.permission,expires_at=(self.f.now-timedelta(seconds=1)).isoformat());self.denied_open('permission expired')

    def test_future_host_permission(self):
        self.f.permission=replace(self.f.permission,not_before=(self.f.now+timedelta(seconds=1)).isoformat());self.denied_open('not yet effective')

    def test_unknown_assignment_period(self):
        self.f.permission=replace(self.f.permission,periods={});self.denied_open('explicit host resolution')

    def test_expired_assignment_period(self):
        periods=copy.deepcopy(self.f.permission.periods);periods['protocol:R03-assignment-period'][1]=(self.f.now-timedelta(seconds=1)).isoformat()
        self.f.permission=replace(self.f.permission,periods=periods);self.denied_context('Assignment period expired')

    def test_future_assignment_period(self):
        periods=copy.deepcopy(self.f.permission.periods);periods['protocol:R03-assignment-period'][0]=(self.f.now+timedelta(seconds=1)).isoformat()
        self.f.permission=replace(self.f.permission,periods=periods);self.denied_open('not yet effective')

    def test_naive_period_timestamp(self):
        periods=copy.deepcopy(self.f.permission.periods);periods['protocol:R03-assignment-period'][0]=self.f.now.replace(tzinfo=None).isoformat()
        self.f.permission=replace(self.f.permission,periods=periods);self.denied_open('timezone')

    def test_current_source_cut_must_match(self):
        cut=copy.deepcopy(self.f.cut);cut['commit_sha256']='3'*64;self.denied_open('cut differs',source_cut=cut)

    def test_foreign_artifact_scope(self):
        ref={**self.f.refs['agent-assignment'],'scope_ref':'project:other'};self.denied_open('source scope differs',assignment=ref)

    def test_original_bytes_are_not_semantic_or_normalized_hashes(self):
        row=self.f.records[0];parsed=parse(row.original);normalized=(json.dumps(parsed,sort_keys=True,indent=2)+'\n').encode()
        self.assertNotEqual(digest(row.original),digest(normalized))
        ref={**row.artifact,'byte_sha256':digest(normalized)}
        with self.assertRaisesRegex(EligibilityFault,'source reference unresolved'):self.f.sources.get(ref)

    def test_body_identity_cannot_be_relabelled_by_header(self):
        row=self.f.records[0];ref={**row.artifact,'identity_ref':'principal:relabeled','version_ref':'principal:relabeled@fixture.1'}
        source=ExactSources(self.f.sources.scope_ref,self.f.cut,[SourceRecord(ref,row.original,row.posture,row.source_ref)],self.f.schemas,self.f.guard)
        with self.assertRaisesRegex(EligibilityFault,'body identity'):source.get(ref)

    def test_historical_source_posture_denied(self):
        self.rebuild(postures={'agent-assignment':'admitted-historical'});self.denied_open('not current')

    def test_source_file_drift(self):
        file=Path(self.tmp.name)/'agent-assignment.json';file.write_bytes(file.read_bytes()+b'\n');self.denied_open('no longer current')

    def test_missing_goal_reference(self):
        self.rebuild(omit=['goal']);self.denied_context('missing or ambiguous')

    def test_ambiguous_current_identity(self):
        self.rebuild(duplicate_identity=True);self.denied_context('missing or ambiguous')

    def test_assignment_owner_binding(self):
        self.rebuild(lambda b:b['agent-assignment']['payload'].update(owner_ref='principal:other'));self.denied_open('Assignment owner')

    def test_assignment_work_binding(self):
        self.rebuild(lambda b:b['agent-assignment']['payload'].update(work_ref='work:other'));self.denied_open('Assignment Work')

    def test_assignment_project_binding(self):
        self.rebuild(lambda b:b['agent-assignment']['payload'].update(project_ref='project:other'));self.denied_context('Project differ')

    def test_one_goal_coordination_binding(self):
        self.rebuild(lambda b:b['coordination-context'].update(goal_ref=None));self.denied_open('one explicit Work Goal')

    def test_wrong_coordination_goal(self):
        self.rebuild(lambda b:b['coordination-context'].update(goal_ref='goal:other'));self.denied_context('one explicit Work Goal')

    def test_coordination_consumer_binding(self):
        self.rebuild(lambda b:b['coordination-context'].update(consumer_refs=['principal:other']));self.denied_open('does not select this consumer')

    def test_inactive_coordination_context(self):
        self.rebuild(lambda b:b['coordination-context'].update(lifecycle_state='retired'));self.denied_context('inactive')

    def test_assignment_expected_outputs_match_declared_work(self):
        self.rebuild(lambda b:b['agent-assignment']['payload'].update(expected_output_refs=['protocol:other-output']));self.denied_open('expected outputs differ')

    def test_membership_declaration_cannot_disagree_with_project_field(self):
        self.rebuild(lambda b:b['work']['relation_refs'][0].update(counterpart_ref='project:other'));self.denied_open('membership declaration')

    def test_assignment_relation_cannot_disagree_with_intent_binding(self):
        self.rebuild(lambda b:b['agent-assignment']['relation_refs'][1].update(counterpart_ref='intent:other'));self.denied_context('declared relationship')

    def test_required_work_input_closure(self):
        self.rebuild(lambda b:b['work']['payload'].update(input_refs=['intent:unknown']));self.denied_context('missing or ambiguous')

    def test_profile_input_kinds(self):
        self.rebuild(lambda b:b['agent-profile']['payload'].update(allowed_input_kinds=['context-view']));self.denied_open('does not accept')

    def test_unknown_profile_policy(self):
        self.rebuild(lambda b:b['agent-profile']['payload'].update(policy_refs=['policy:unknown']));self.denied_open('Policy unresolved')

    def test_assignment_stop_condition(self):
        self.f.permission=replace(self.f.permission,reached_stop_conditions=frozenset(['candidate-validation-pass']));self.denied_context('stop condition')

    def test_revoked_assignment(self):
        self.f.permission=replace(self.f.permission,revoked_refs=frozenset([self.f.refs['agent-assignment']['version_ref']]));self.denied_open('revoked')

    def test_revoked_goal_in_closure(self):
        self.f.permission=replace(self.f.permission,revoked_refs=frozenset([self.f.refs['goal']['identity_ref']]));self.denied_open('revoked')

    def test_request_budget_cannot_expand_host_budget(self):
        budget=self.f.budget(1);budget['max_actions']=65;self.denied_open('exceeds current host',budget=budget)

    def test_bool_is_not_integer_action_budget(self):
        budget=self.f.budget(1);budget['max_actions']=True;self.denied_open('nonnegative integers',budget=budget)

    def test_context_read_action_budget_zero(self):
        m=self.f.context();m['budget']['max_actions']=1
        with self.assertRaisesRegex(EligibilityFault,'must be zero'):self.f.authority.context_plan(m,self.f.actor,self.f.refs['agent-profile'])

    def test_creation_action_budget_positive(self):
        self.denied_open('positive independently',budget=self.f.budget(0))

    def test_expired_request_deadline(self):
        budget=self.f.budget(1);budget['deadline']=(self.f.now-timedelta(seconds=1)).isoformat();self.denied_open('request deadline expired',budget=budget)

    def test_strictest_lifetime_includes_host_session_cap(self):
        self.f.permission=replace(self.f.permission,max_session_seconds=30)
        self.assertEqual(instant(self.f.open_plan()['expires_at']),self.f.now+timedelta(seconds=30))

    def test_strictest_lifetime_includes_assignment_and_context(self):
        periods=copy.deepcopy(self.f.permission.periods);periods['protocol:R03-assignment-period'][1]=(self.f.now+timedelta(seconds=20)).isoformat()
        self.f.permission=replace(self.f.permission,periods=periods)
        self.assertEqual(instant(self.f.open_plan()['expires_at']),self.f.now+timedelta(seconds=20))

    def test_context_expired(self):
        self.f.delivery['expires_at']=(self.f.now-timedelta(seconds=1)).isoformat();self.denied_open('context expired')

    def test_context_principal_binding(self):
        self.f.delivery['authenticated_principal_ref']='principal:other';self.denied_open('another principal')

    def test_context_source_cut_binding(self):
        self.f.delivery['source_cut']['commit_sha256']='4'*64;self.denied_open('not current')

    def test_context_scope_enforcement_required(self):
        self.f.delivery['scope_enforced']=False;self.denied_open('scope enforced')

    def test_context_delivery_original_binding(self):
        self.denied_open('context binding unresolved',context_delivery_binding={'ref':self.f.delivery_binding['ref'],'sha256':'5'*64})

    def test_exact_authority_envelope_binding(self):
        self.denied_open('authority envelope differs',authority_envelope_binding={'ref':self.f.envelope_binding['ref'],'sha256':'6'*64})

    def test_implementation_source_environment_selection_required(self):
        self.f.permission=replace(self.f.permission,implementation_bindings={});self.denied_open('independent code/environment')

    def test_implementation_declared_entrypoint_not_permission(self):
        self.rebuild(lambda b:b['implementation']['payload'].update(execution_entrypoint_ref='protocol:unselected-entrypoint'));self.denied_open('source or environment differs')

    def test_agent_capability_exact_implementation_binding(self):
        self.rebuild(lambda b:b['agent-capability']['payload'].update(implementation_refs=['implementation:other@fixture.1']));self.denied_open('exact selected Implementation')

    def test_undeclared_agent_capability_denied(self):
        self.rebuild(lambda b:b['agent-profile']['relation_refs'][0].update(counterpart_ref='agent-capability:unknown'));self.denied_open('missing or ambiguous')

    def test_duplicate_agent_capability_denied(self):
        self.denied_open('duplicate Agent Capability',capabilities=[self.f.refs['agent-capability'],self.f.refs['agent-capability']])

    def test_product_or_other_carrier_cannot_replace_agent_capability(self):
        self.denied_open('source carrier differs',capabilities=[self.f.refs['product']])

    def test_unknown_capability_contract_reference(self):
        self.rebuild(lambda b:b['agent-capability']['payload'].update(input_contract_refs=['protocol:unknown-input']));self.denied_open('declared kind/byte')

    def test_protocol_contract_kind_not_collapsed(self):
        protocols=copy.deepcopy(self.f.permission.protocol_bindings);protocols['protocol:R03-input-contract']['kind']='output-contract'
        self.f.permission=replace(self.f.permission,protocol_bindings=protocols);self.denied_open('evidence cannot be verified')

    def test_memory_policy_is_exact_booleans(self):
        for p in [{'persistence_allowed':True,'expires_with_session':True},{'persistence_allowed':False,'expires_with_session':False},{'persistence_allowed':0,'expires_with_session':1}]:
            self.denied_open('memory must expire',memory_policy=p)

    def test_blank_Session_metadata_policy_is_not_memory_content(self):
        body={'payload':{'session_memory':{'selected_input_refs':[],'working_record_refs':[],'unresolved_questions':[],'expires_with_session':True}}}
        no_private_memory(body,blank_session_policy=True)
        for field in ['selected_input_refs','working_record_refs','unresolved_questions']:
            value=copy.deepcopy(body);value['payload']['session_memory'][field]=['private']
            with self.assertRaisesRegex(EligibilityFault,'private to its live Session'):no_private_memory(value,blank_session_policy=True)

    def test_arbitrary_nested_or_schema_memory_no_exemption(self):
        for body in [{'nested':{'session_memory':{}}},{'properties':{'session_memory':{'type':'object'}}}]:
            with self.assertRaisesRegex(EligibilityFault,'private to its live Session'):no_private_memory(body,blank_session_policy=True)

    def test_private_credentials_excluded(self):
        for body in [{'password':'secret-text'},{'private_key':'-----BEGIN PRIVATE KEY-----'},{'x':'-----BEGIN RSA PRIVATE KEY-----'}]:
            with self.assertRaises(EligibilityFault):no_private_memory(body)

    def test_permission_mutation_during_checks_cannot_bypass_freshness(self):
        calls=[0];original=self.f.sources.current_guard
        def change():
            calls[0]+=1
            if calls[0]==3:self.f.permission.periods['protocol:R03-assignment-period'][1]=(self.f.now+timedelta(seconds=1)).isoformat()
            return original()
        self.f.sources.current_guard=change;self.denied_open('permission changed during preflight')

    def test_stale_source_during_checks_fails_before_any_creation(self):
        calls=[0]
        def change():calls[0]+=1;return calls[0]<4
        self.f.sources.current_guard=change;self.denied_open('no longer current')

    def test_intended_use_enforced(self):
        m=self.f.context();m['intended_use']='run-arbitrary-command'
        with self.assertRaisesRegex(EligibilityFault,'outside Coordination Context'):self.f.authority.context_plan(m,self.f.actor,self.f.refs['agent-profile'])

    def test_required_closure_cannot_be_excluded(self):
        m=self.f.context();m['exclusions']=[self.f.refs['goal']['version_ref']]
        with self.assertRaisesRegex(EligibilityFault,'excludes required'):self.f.authority.context_plan(m,self.f.actor,self.f.refs['agent-profile'])

    def test_historical_context_is_not_fresh_operational_permission(self):
        m=self.f.context();m['freshness_requirement']='exact-historical'
        with self.assertRaisesRegex(EligibilityFault,'historical context'):self.f.authority.context_plan(m,self.f.actor,self.f.refs['agent-profile'])

    def test_external_schema_refs_not_implicitly_fetched(self):
        raw=b'{"$schema":"https://json-schema.org/draft/2020-12/schema","$ref":"https://example.invalid/schema"}'
        with self.assertRaisesRegex(EligibilityFault,'external schema'):SchemaSpec('carrier','kind','node_id',raw,digest(raw)).validator()

    def test_duplicate_original_JSON_rejected(self):
        with self.assertRaisesRegex(EligibilityFault,'source JSON'):parse(b'{"a":1,"a":2}')


if __name__=='__main__':unittest.main(verbosity=2)
