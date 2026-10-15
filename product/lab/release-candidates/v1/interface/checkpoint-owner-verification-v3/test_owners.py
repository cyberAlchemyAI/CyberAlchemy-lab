"""Synthetic original-schema joins and actual private-file custody checks."""
import base64
import copy
from datetime import datetime,timedelta,timezone
import os
from pathlib import Path
import tempfile
import unittest
from . import owners as O

class OwnerChecks(unittest.TestCase):
    def setUp(self):
        self.scope='scope:fixture:checkpoint-owner';self.principal='principal:fixture:checkpoint-owner'
        self.role='role:fixture:owner';self.at='2026-10-11T15:00:00Z';self.permission='admit-exact-reviewed-work'
        self.rows={k:O.parse((O.ROOT/f'authority/artifact-types/{k}/v1/fixtures/valid/record.json').read_bytes()) for k in O.KINDS}
        for kind,body in self.rows.items():body.update(node_id=kind+':fixture:checkpoint-owner',scope_ref=self.scope)
        p,a,c,b,s=(self.rows[k] for k in O.KINDS)
        p['node_id']=self.principal;p['payload'].update(stable_subject_ref='person-reference:fixture:owner',status='active',principal_kind='human',recognition_boundary_refs=[b['node_id']])
        a.update(assignee_kind='person-reference',assignee_ref='person-reference:fixture:owner',role_ref=self.role,
            authority_claim_refs=[c['node_id']],assignment_state='active',period={'start':'2026-10-10T00:00:00Z','end':None})
        c['payload'].update(claimant_ref=self.role,decision_scope_ref=s['node_id'],claimed_permissions=[self.permission],limitations=['no consumer activation'])
        b['payload'].update(owner_role_ref=self.role,accountable_principal_ref=self.principal,authority_scope_ref=s['node_id'],
            allowed_effect_kinds=[self.permission],excluded_effect_kinds=[],revocation_state='not-revoked',effective_period='until-revoked-or-superseded')
        s['payload'].update(subject_kind_refs=['work'],subject_refs=['work:fixture:one@1'],permitted_effects=['admit'],excluded_effects=['activate-consumer'])
        self.targets=({'identity_ref':'work:fixture:one','version_ref':'work:fixture:one@1','kind':'work','operation':'admit','scope_ref':self.scope},)
    def records(self):
        result={}
        for kind,body in self.rows.items():
            raw=(__import__('json').dumps(body,indent=3)+'\n').encode()
            h={'scope_ref':self.scope,'identity_ref':body['node_id'],'version_ref':body['node_id']+'@1',
                'carrier_ref':'cal.artifact-type.'+kind+'/v1','byte_sha256':O.sha(raw)}
            result[kind]=O.Record(h,raw,'local-admitted-current')
        return result
    def join(self,records=None):
        return O.verify_join(records or self.records(),principal_ref=self.principal,role_ref=self.role,storage_scope_ref=self.scope,assignment_scope_ref=self.scope,
            evaluated_at=self.at,permission=self.permission,targets=self.targets)
    def rejected(self):
        with self.assertRaises(O.OwnerFault) as caught: self.join()
        if self._testMethodName not in ('test11_claim_missing_basis','test23_schema_unknown_field'):
            self.assertNotIn('invalid original',str(caught.exception),'negative case stopped at an unintended schema error')
    def policy(self):
        now=datetime.now(timezone.utc)
        return {'schema_version':'lab-independent-checkpoint-owner-selection/v1-candidate',
            'source_cut':{'store_ref':'store:fixture','branch_ref':'branch:fixture','commit_sequence':1,
                'commit_sha256':'a'*64,'source_profile_sha256':'b'*64,'streams':[]},
            'accountable_principal_ref':self.principal,'storage_scope_ref':self.scope,'not_before':(now-timedelta(seconds=5)).isoformat(),
            'expires_at':(now+timedelta(minutes=2)).isoformat(),'revoked':False,'fixture_only':True,'authority_effect':'none',
            'owners':[{'principal_ref':self.principal,'role_ref':self.role,'assignment_scope_ref':self.scope,'public_key':base64.b64encode(b'k'*32).decode(),
                'records':{k:r.header for k,r in self.records().items()},'permission':self.permission,
                'targets':list(self.targets),'core_bindings':[{'ref':'core:fixture:one','sha256':'c'*64}]}]}
    def selection_check(self,change=None):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            root=Path(temporary);root.chmod(0o700);path=root/'selection.json';value=self.policy()
            if change: change(value)
            raw=O.encoded(value);path.write_bytes(raw);path.chmod(0o600)
            return O.Selection(path,O.sha(raw)).guard()
    def selection_rejected(self,change):
        with self.assertRaises(O.OwnerFault): self.selection_check(change)
    def test01_exact_join_retains_unverified_basis(self):
        result=self.join();self.assertTrue(result['join_consistent'])
        for key in ('authority_basis_verified','live_authority_verified','canonical_admission_granted'):self.assertFalse(result[key])
        self.assertEqual(len(result['source_bindings']),5);self.assertEqual(result['authority_effect'],'none')
    def test02_suspended_principal(self): self.rows['principal']['payload']['status']='suspended';self.rejected()
    def test03_wrong_assignee(self): self.rows['role-assignment']['assignee_ref']='person-reference:other';self.rejected()
    def test04_wrong_role(self): self.rows['role-assignment']['role_ref']='role:other';self.rejected()
    def test05_suspended_assignment(self): self.rows['role-assignment']['assignment_state']='suspended';self.rejected()
    def test06_future_assignment(self): self.rows['role-assignment']['period']['start']='2026-10-12T00:00:00Z';self.rejected()
    def test07_claim_not_selected_by_assignment(self): self.rows['role-assignment']['authority_claim_refs']=[];self.rejected()
    def test08_claim_role_substitution(self): self.rows['authority-claim']['payload']['claimant_ref']='role:other';self.rejected()
    def test09_claim_scope_substitution(self): self.rows['authority-claim']['payload']['decision_scope_ref']='scope:other';self.rejected()
    def test10_claim_limitations_need_semantic_adapter(self):
        self.rows['authority-claim']['payload']['limitations']=['Only after owner approval']
        result=self.join();self.assertEqual(result['unresolved_semantic_limitations'],['Only after owner approval'])
        self.assertFalse(result['live_authority_verified']);self.assertFalse(result['authority_basis_verified'])
    def test11_claim_missing_basis(self): self.rows['authority-claim']['payload']['authority_basis_refs']=[];self.rejected()
    def test12_boundary_principal_substitution(self): self.rows['authority-boundary']['payload']['accountable_principal_ref']='principal:other';self.rejected()
    def test13_boundary_revoked(self): self.rows['authority-boundary']['payload']['revocation_state']='revoked';self.rejected()
    def test14_unsupported_boundary_period(self): self.rows['authority-boundary']['payload']['effective_period']='until-the-next-meeting';self.rejected()
    def test15_boundary_not_recognized_by_principal(self): self.rows['principal']['payload']['recognition_boundary_refs']=[];self.rejected()
    def test16_permission_excluded(self): self.rows['authority-boundary']['payload']['excluded_effect_kinds']=[self.permission];self.rejected()
    def test17_permission_not_in_claim(self): self.rows['authority-claim']['payload']['claimed_permissions']=['other-effect'];self.rejected()
    def test18_scope_operation_excluded(self): self.rows['decision-scope']['payload']['excluded_effects']=['admit'];self.rejected()
    def test19_scope_target_substitution(self): self.rows['decision-scope']['payload']['subject_refs']=['work:other'];self.rejected()
    def test20_scope_kind_substitution(self): self.rows['decision-scope']['payload']['subject_kind_refs']=['product'];self.rejected()
    def test21_historical_source_refused(self):
        records=self.records();r=records['principal'];records['principal']=O.Record(r.header,r.original,'local-admitted-historical')
        with self.assertRaises(O.OwnerFault):self.join(records)
    def test22_raw_bytes_changed(self):
        records=self.records();r=records['principal'];records['principal']=O.Record(r.header,r.original+b'\n',r.source_state)
        with self.assertRaises(O.OwnerFault):self.join(records)
    def test23_schema_unknown_field(self): self.rows['authority-claim']['caller_grants_authority']=True;self.rejected()
    def test24_duplicate_target_grant(self): self.targets=self.targets*2;self.rejected()
    def test25_exact_identity_scope_is_explicit(self):
        self.rows['decision-scope']['payload']['subject_refs']=['work:fixture:one'];self.assertTrue(self.join()['join_consistent'])
    def test26_private_selected_key_and_complete_sources(self): self.assertTrue(self.selection_check()['fixture_only'])
    def test27_duplicate_owner_selection(self): self.selection_rejected(lambda p:p['owners'].append(copy.deepcopy(p['owners'][0])))
    def test28_revoked_selection(self): self.selection_rejected(lambda p:p.update(revoked=True))
    def test29_expired_selection(self): self.selection_rejected(lambda p:p.update(expires_at='2020-01-01T00:00:00Z'))
    def test30_caller_key_field_refused(self): self.selection_rejected(lambda p:p.update(caller_public_key='bad'))
    def test31_selected_key_width_refused(self): self.selection_rejected(lambda p:p['owners'][0].update(public_key=base64.b64encode(b'k'*31).decode()))
    def test32_core_grants_cannot_repeat(self): self.selection_rejected(lambda p:p['owners'][0]['core_bindings'].append(copy.deepcopy(p['owners'][0]['core_bindings'][0])))
    def test33_changed_private_original_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            path=Path(temporary)/'selection.json';raw=O.encoded(self.policy());path.write_bytes(raw);path.chmod(0o600)
            selection=O.Selection(path,O.sha(raw));path.write_bytes(raw+b'\n')
            with self.assertRaises(O.OwnerFault): selection.guard()
    def test34_readable_private_policy_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            path=Path(temporary)/'selection.json';raw=O.encoded(self.policy());path.write_bytes(raw);path.chmod(0o644)
            with self.assertRaises(O.OwnerFault): O.Selection(path,O.sha(raw))
    def test35_symlink_policy_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            target=Path(temporary)/'original.json';raw=O.encoded(self.policy());target.write_bytes(raw);target.chmod(0o600)
            path=Path(temporary)/'selection.json';path.symlink_to(target)
            with self.assertRaises(O.OwnerFault): O.Selection(path,O.sha(raw))
    def test36_nonfinite_json_refused(self):
        with self.assertRaises(O.OwnerFault): O.parse(b'{"clock":NaN}')
    def test37_no_fake_service_authority(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            path=Path(temporary)/'selection.json';raw=O.encoded(self.policy());path.write_bytes(raw);path.chmod(0o600)
            with self.assertRaises(O.OwnerFault): O.API59Sources(object(),O.Selection(path,O.sha(raw)))
    def test38_join_reads_without_changing_inputs(self):
        records=self.records();before=copy.deepcopy(records);self.join(records);self.assertEqual(records,before)

    def test39_valid_original_schema_fixture_before_mutation(self):
        for kind,record in self.records().items(): O.checked_record(record,kind,self.scope)
    def test40_original_source_cut_hash_shape_enforced(self):
        self.selection_rejected(lambda p:p['source_cut'].update(commit_sha256='caller-text'))
    def test41_hardlinked_policy_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            path=Path(temporary)/'selection.json';raw=O.encoded(self.policy());path.write_bytes(raw);path.chmod(0o600)
            os.link(path,Path(temporary)/'other.json')
            with self.assertRaises(O.OwnerFault): O.Selection(path,O.sha(raw))
    def test42_readable_policy_directory_refused(self):
        with tempfile.TemporaryDirectory(prefix='cal-checkpoint-owner-selection-') as temporary:
            root=Path(temporary);path=root/'selection.json';raw=O.encoded(self.policy());path.write_bytes(raw);path.chmod(0o600);root.chmod(0o755)
            with self.assertRaises(O.OwnerFault): O.Selection(path,O.sha(raw))
    def test43_duplicate_json_key_refused(self):
        with self.assertRaises(O.OwnerFault): O.parse(b'{"revoked":false,"revoked":true}')

    def test44_principal_body_scope_is_separate_from_storage(self):
        self.rows['principal']['scope_ref']='scope:principal-registry'
        self.assertTrue(self.join()['join_consistent'])
    def test45_assignment_domain_is_independently_checked(self):
        self.rows['role-assignment']['scope_ref']='scope:other-authority-domain';self.rejected()
    def test46_target_domain_is_not_storage_scope(self):
        self.targets=({**self.targets[0],'scope_ref':'scope:other-target-domain'},);self.rejected()
    def test47_original_header_storage_scope_is_checked(self):
        records=self.records();r=records['principal'];h={**r.header,'scope_ref':'store-scope:other'}
        records['principal']=O.Record(h,r.original,r.source_state)
        with self.assertRaises(O.OwnerFault): self.join(records)
    def test48_one_assignment_does_not_cover_another_domain(self):
        self.targets=(*self.targets,{**self.targets[0],'version_ref':'work:fixture:two@1','scope_ref':'scope:other-domain'})
        self.rejected()
    def test49_distinct_authority_record_body_domains_are_retained(self):
        for kind in ('principal','authority-claim','authority-boundary','decision-scope'):
            self.rows[kind]['scope_ref']='scope:record-domain:'+kind
        result=self.join();self.assertTrue(result['join_consistent'])
        self.assertEqual(result['assignment_scope_ref'],self.scope);self.assertEqual(result['storage_scope_ref'],self.scope)
