import ast
import json
from pathlib import Path
import types
import unittest
from unittest.mock import patch

P=Path(__file__).with_name('adapter.py');a=types.ModuleType('adapter');a.__file__=str(P)
exec(compile(P.read_bytes(),str(P),'exec'),a.__dict__)

class AtOpen(Exception):pass
class Tests(unittest.TestCase):
    def guard(self,view):
        module=types.ModuleType('projected_guard')
        raw=a.project_policy_guard(view)
        exec(compile(raw,'selected-guard','exec'),module.__dict__)
        return module
    def check_path(self,view,root,source,expect_open):
        g=self.guard(view)
        with patch.object(g._policy_os,'open',side_effect=AtOpen),patch.object(g._policy_os,'getuid',return_value=1000),patch.object(g._policy_os,'geteuid',return_value=1000),patch.object(g._policy_os,'getgid',return_value=1000),patch.object(g._policy_os,'getegid',return_value=1000):
            with self.assertRaises(AtOpen if expect_open else g.PolicyRefused):
                g._policy_open_selected(root+'/permission.json',root,source,(),1000,1000)
    def test_exact_host_and_child_preopen_admission(self):
        self.check_path('host',a.HOST_ROOT,a.HOST_SOURCE,True)
        self.check_path('child',a.CHILD_ROOT,a.CHILD_SOURCE,True)
    def test_wrong_views_stale_tmp_and_alias_refuse_before_open(self):
        for view,root,source in [('host','/tmp/old',a.HOST_SOURCE),('child',a.HOST_ROOT,a.HOST_SOURCE),('host',a.CHILD_ROOT,a.CHILD_SOURCE),('child',a.CHILD_ROOT,'/workspace/other'),('child','/context-policy/../other',a.CHILD_SOURCE)]:
            self.check_path(view,root,source,False)
    def test_projection_inverse_and_other_guard_functions_unchanged(self):
        original=ast.parse(a.original('context-policy-0002/held_policy.py'))
        for view in ('host','child'):
            projected=ast.parse(a.project_policy_guard(view))
            old={n.name:ast.dump(n) for n in original.body if isinstance(n,ast.FunctionDef)}
            new={n.name:ast.dump(n) for n in projected.body if isinstance(n,ast.FunctionDef)}
            self.assertEqual(set(old),set(new))
            self.assertEqual([k for k in old if old[k]!=new[k]],['_policy_open_selected'])
            for code in ('st_nlink','0o700','0o600','O_NOFOLLOW','_policy_close'):
                self.assertIn(code,a.project_policy_guard(view).decode())
        control=a.project_control();ast.parse(control)
        self.assertNotIn(b"_PolicyPurePath('/tmp') in base.parents",control)
    def test_build_retains_guard_and_no_child_provision_call(self):
        raw=a.project_build();tree=ast.parse(raw)
        build=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build')
        calls=[n.func.id for n in ast.walk(build) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
        self.assertNotIn('provision',calls);self.assertIn('_ctx_parent_proof',calls)
        self.assertIn('_ctx_policy_retained',calls);self.assertIn('_ctx_release_transport_scratch',calls)
        self.assertIn('_t35_effect_refused',calls)
        self.assertNotIn(b"require(not root.exists()",raw)
        self.assertIn(b"'owned_host_policy_and_transport_key_removed': False",raw)
        self.assertIn(b"'private_policy_retained_pending_external_verification': True",raw)
        ast.parse(a.project_release_hook())
    def test_preimage_drift_refuses(self):
        with patch.object(a.Path,'read_bytes',return_value=b'changed'):
            for fn in (a.project_build,a.project_control,a.project_release_hook):
                with self.assertRaisesRegex(a.Refused,'ORIGINAL_DRIFT'):fn()
    def rows(self):
        targets=['/workspace','/control','/runner','/cache-disabled','/attempt/input/lab-context-native-reader',a.CHILD_ROOT]
        return [{'source':a.HOST_ROOT if t==a.CHILD_ROOT else '/fixture'+t,'target':t,'read_only':True} for t in targets]
    def test_sixth_bind_required_and_ro(self):
        rows=self.rows();self.assertEqual(a.validate_mount_observation(a.compact(rows)),'SYNTHETIC_TOPOLOGY_ONLY')
        for mutation in ('five','rw','key','nested','alias'):
            rows=self.rows()
            if mutation=='five':rows.pop()
            elif mutation=='rw':rows[-1]['read_only']=False
            elif mutation=='key':rows[-1]['target']='/signing-key'
            elif mutation=='nested':rows[-1]['target']='/workspace/private'
            else:rows[-1]['source']='/foreign/private'
            with self.assertRaises(a.Refused):a.validate_mount_observation(a.compact(rows))
    def retained(self):
        model=a.RetentionModel();model.closed_channel(channel_closed=True,local_proof_handle_dropped=True,policy_attached=True)
        return model
    def test_release38_result39_does_not_remove_policy(self):
        m=self.retained()
        with self.assertRaises(a.Refused):m.result()
        m.release_transport_scratch(38,scratch_empty=True,policy_attached=True)
        self.assertFalse(m.result()['owned_host_policy_and_transport_key_removed'])
        self.assertTrue(m.result()['private_policy_retained_pending_external_verification'])
        with self.assertRaises(a.Refused):m.cleanup_effect()
    def test_external_gate_and_cleanup_uncertainty(self):
        for k,bad in [('os_exit',False),('os_exit',0.0),('container_absent',False),('final_closed',False),('output_verified',False),('independent_review',False),('parent_key_dropped',False)]:
            m=self.retained();m.release_transport_scratch(38,scratch_empty=True,policy_attached=True)
            args=dict(os_exit=0,container_absent=True,final_closed=True,output_verified=True,independent_review=True,parent_key_dropped=True);args[k]=bad
            with self.assertRaises(a.Refused):m.external_gate(**args)
            self.assertTrue(m.unknown);self.assertEqual(m.state,'UNKNOWN')
            with self.assertRaises(a.Refused):m.result()
        m=self.retained();m.release_transport_scratch(38,scratch_empty=True,policy_attached=True)
        m.external_gate(os_exit=0,container_absent=True,final_closed=True,output_verified=True,independent_review=True,parent_key_dropped=True)
        self.assertEqual(m.state,'CLEANUP_ELIGIBLE_MODEL_ONLY')
        with self.assertRaises(a.Refused):m.cleanup_effect()
    def test_failed_channel_close_cannot_reach_result(self):
        m=a.RetentionModel()
        with self.assertRaises(a.Refused):m.closed_channel(channel_closed=False,local_proof_handle_dropped=True,policy_attached=True)
        with self.assertRaises(a.Refused):m.release_transport_scratch(38,scratch_empty=True,policy_attached=True)
    def test_first_failed_release_poisoned_no_retry(self):
        for ordinal,empty,attached in ((37,True,True),(38,False,True),(38,True,False),
                                        (False,True,True)):
            with self.subTest(ordinal=ordinal,empty=empty,attached=attached):
                m=self.retained()
                with self.assertRaises(a.Refused):
                    m.release_transport_scratch(ordinal,scratch_empty=empty,
                                                policy_attached=attached)
                self.assertEqual(m.state,'UNKNOWN');self.assertTrue(m.unknown)
                with self.assertRaises(a.Refused):
                    m.release_transport_scratch(38,scratch_empty=True,
                                                policy_attached=True)
                with self.assertRaises(a.Refused):m.result()
                with self.assertRaises(a.Refused):m.cleanup_effect()
    def proof(self):
        m=a.ProofModel(policy_sha='a'*64,expires_at='2026-10-20T18:20:00Z',attempt='fixture-attempt',peer=(42,1000,1000))
        c={'schema_version':'lab-context-host-challenge/v1-candidate','host_instance_ref':'host:R03-context:á',
            'connection_ref':'connection:R03-context:test','nonce':'b'*64,'policy_sha256':'a'*64,
            'expires_at':m.expiry,'authority_effect':'none'}
        return m,{'schema':'context-parent-proof-request/v1','attempt':'fixture-attempt','challenge':c}
    def test_original_challenge_bytes_and_once_consumption(self):
        m,r=self.proof();result=m.consume(a.compact(r),peer=(42,1000,1000),current=True)
        self.assertEqual(result['bytes_to_sign'],json.dumps(r['challenge'],sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
        self.assertIn('á'.encode(),result['bytes_to_sign'])
        with self.assertRaises(a.Refused):m.consume(a.compact(r),peer=(42,1000,1000),current=True)
        m.durable(retained_request_sha=result['request_sha256'],fsync_observed=True,current=True)
        with self.assertRaises(a.Refused):m.sign()
        with self.assertRaises(a.Refused):m.restart()
    def test_wrong_policy_scope_expiry_peer_and_arbitrary_payload(self):
        for field,value in [('policy_sha256','c'*64),('authority_effect','write'),('expires_at','2026-10-21T19:00:00Z'),('schema_version','arbitrary')]:
            m,r=self.proof();r['challenge'][field]=value
            with self.assertRaises(a.Refused):m.consume(a.compact(r),peer=(42,1000,1000),current=True)
        m,r=self.proof()
        with self.assertRaises(a.Refused):m.consume(a.compact(r),peer=(43,1000,1000),current=True)
        with self.assertRaises(a.Refused):m.consume(b'{}',peer=(42,1000,1000),current=True)
        with self.assertRaises(a.Refused):m.consume(b'x'*8193,peer=(42,1000,1000),current=True)
    def test_lost_durability_stays_consumed(self):
        m,r=self.proof();result=m.consume(a.compact(r),peer=(42,1000,1000),current=True)
        with self.assertRaises(a.Refused):m.durable(retained_request_sha=result['request_sha256'],fsync_observed=False,current=True)
        self.assertEqual(m.state,'UNKNOWN_CONSUMED')
        with self.assertRaises(a.Refused):m.consume(a.compact(r),peer=(42,1000,1000),current=True)
    def test_first_invalid_proof_attempt_consumed_no_retry(self):
        for mutation in ('malformed','wrong_peer','stale','oversize','wrong_policy'):
            with self.subTest(mutation=mutation):
                m,r=self.proof();raw=a.compact(r);peer=(42,1000,1000);current=True
                if mutation=='malformed':raw=b'{}'
                elif mutation=='wrong_peer':peer=(43,1000,1000)
                elif mutation=='stale':current=False
                elif mutation=='oversize':raw=b'x'*8193
                else:
                    r['challenge']['policy_sha256']='c'*64;raw=a.compact(r)
                with self.assertRaises(a.Refused):m.consume(raw,peer=peer,current=current)
                self.assertEqual(m.state,'UNKNOWN_CONSUMED')
                _,valid=self.proof()
                with self.assertRaisesRegex(a.Refused,'PROOF_ALREADY_CONSUMED'):
                    m.consume(a.compact(valid),peer=(42,1000,1000),current=True)
                with self.assertRaises(a.Refused):m.sign()
    def test_no_effect_entrypoint(self):
        self.assertFalse(a.EFFECT_ENABLED)
        with self.assertRaises(a.Refused):a.provision_or_launch()

if __name__=='__main__':unittest.main()
