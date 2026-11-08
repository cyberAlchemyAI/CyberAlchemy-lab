"""Pure provider/AST tests. Generated source is parsed/compiled, never executed."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0,str(ROOT/'implementation/lab-runtime/candidates/runtime-completion-0001'))
from t35_external_v1.phase_scoped_v2 import context_fixture_provider_0001 as provider
from t35_external_v1.phase_scoped_v2 import context_fixture_adapter_0001 as adapter

E = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-05'
PREIMAGE = (E/'context-orchestration-pure-preimage-0001.py').read_bytes()
PREIMAGE_SHA = '7c202a0613e651b693f2abc8fdb059048b2e6711f84dd0dbf33752c77151d082'
if hashlib.sha256(PREIMAGE).hexdigest()!=PREIMAGE_SHA:
    raise RuntimeError('TEST_PREIMAGE_DRIFT')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def rows(raws):
    return [{'fixture_id':f'fixture:context:{i:02d}','sha256':sha(raw),'size_bytes':len(raw)}
            for i,raw in enumerate(raws)]


class Bodies(unittest.TestCase):
    def setUp(self):
        self.kw={'mapper_manifest_sha256':'1'*64,'mapping_sha256':'2'*64}
        self.raw=provider.make_bodies(**self.kw)
        self.selected=rows(self.raw)

    def select(self,raw=None,selected=None):
        return provider.select_bodies(self.raw if raw is None else raw,
                                      expected_rows=self.selected if selected is None else selected,**self.kw)

    def test_exact_30_deterministic_labeled_bodies(self):
        self.assertEqual(self.raw,provider.make_bodies(**self.kw))
        self.assertEqual(len(self.raw),30)
        bodies,_=self.select().values()
        self.assertEqual(list(bodies),[f'fixture:context:{i:02d}' for i in range(30)])
        self.assertEqual([x['fixture_kind'] for x in bodies.values()],list(provider.KINDS))
        self.assertTrue(all(x['authority_effect']=='none' and x['actual_owner_outcome'] is None for x in bodies.values()))

    def test_reference_hashes_and_nonsemantic_carrier(self):
        bodies,refs=self.select().values()
        for identity,body in bodies.items():
            self.assertEqual(refs[identity],{'identity_ref':identity,'version_ref':identity+'@1',
                'carrier_ref':'fixture:context-orchestration-body/v1','byte_sha256':sha(provider.encoded(body))})

    def test_original_selection_mismatch(self):
        for field,value in [('sha256','3'*64),('size_bytes',1),('fixture_id','other')]:
            selected=copy.deepcopy(self.selected);selected[0][field]=value
            with self.subTest(field=field),self.assertRaises(provider.Refusal):self.select(selected=selected)

    def test_wrong_predecessor_refuses(self):
        with self.assertRaises(provider.Refusal):
            provider.select_bodies(self.raw,expected_rows=self.selected,mapper_manifest_sha256='3'*64,mapping_sha256='2'*64)

    def test_count_order_and_duplicate(self):
        for raw in [self.raw[:-1],self.raw+(self.raw[0],),tuple(reversed(self.raw)),(self.raw[0],)*30]:
            with self.subTest(count=len(raw)),self.assertRaises(provider.Refusal):self.select(raw=raw,selected=rows(raw))

    def test_extra_field_refuses_even_coherently_repinned(self):
        body=json.loads(self.raw[0]);body['scope_ref']='invented'
        raw=(provider.encoded(body),)+self.raw[1:]
        with self.assertRaisesRegex(provider.Refusal,'FIELDS'):self.select(raw=raw,selected=rows(raw))

    def test_bool_ordinal_refuses(self):
        body=json.loads(self.raw[0]);body['ordinal']=False
        raw=(provider.encoded(body),)+self.raw[1:]
        with self.assertRaisesRegex(provider.Refusal,'ORDINAL'):self.select(raw=raw,selected=rows(raw))

    def test_schema_claim_and_label_substitutions(self):
        for field,value in [('schema_version','actual'),('authority_effect','grant'),('actual_owner_outcome','approve'),('fixture_kind','ontology-node'),('fixture_id','real:node')]:
            body=json.loads(self.raw[0]);body[field]=value;raw=(provider.encoded(body),)+self.raw[1:]
            with self.subTest(field=field),self.assertRaises(provider.Refusal):self.select(raw=raw,selected=rows(raw))

    def test_noncanonical_duplicate_and_malformed_json(self):
        for first in [self.raw[0]+b' ',b'{"ordinal":0,"ordinal":0}',b'\xff',b'null']:
            raw=(first,)+self.raw[1:]
            with self.subTest(raw=first[:10]),self.assertRaises(provider.Refusal):self.select(raw=raw,selected=rows(raw))

    def test_selection_types_and_bound(self):
        for selected in [tuple(self.selected),self.selected[:-1],self.selected+[self.selected[0]]]:
            with self.assertRaises(provider.Refusal):self.select(selected=selected)
        s=copy.deepcopy(self.selected);s[0]['size_bytes']=True
        with self.assertRaises(provider.Refusal):self.select(selected=s)
        with self.assertRaises(provider.Refusal):self.select(raw=(b' '*4097,)+self.raw[1:])

    def test_returned_mutation_is_not_retained(self):
        value=self.select();bodies,refs=value.values();bodies['fixture:context:00']['ordinal']=99;refs.clear()
        b2,r2=value.values();self.assertEqual(b2['fixture:context:00']['ordinal'],0);self.assertEqual(len(r2),30)

    def test_direct_forged_value_revalidates(self):
        forged=provider.FixtureBodies((b'{}',)*30,'1'*64,'2'*64)
        with self.assertRaises(provider.Refusal):forged.values()

    def test_hash_types_refuse(self):
        for value in [None,1,'A'*64,'0'*63,'0'*65]:
            with self.assertRaises(provider.Refusal):provider.make_bodies(mapper_manifest_sha256=value,mapping_sha256='2'*64)

    def test_runtime_entrypoints_remain_unavailable(self):
        for function in [provider.generate,provider.fixture_query]:
            with self.assertRaisesRegex(provider.Refusal,'NOT_IMPLEMENTED'):function()


class Projection(unittest.TestCase):
    def project(self,raw=PREIMAGE,**overrides):
        kw={'expected_preimage_sha256':sha(raw),'expected_completion_sha256':adapter.completion_digest()};kw.update(overrides)
        return adapter.adapt(raw,**kw)

    def test_seven_groups_inverse_and_two_compilations(self):
        output,record=self.project()
        self.assertEqual(len(record['groups']),7)
        self.assertEqual(sum(len(g['sites']) for g in record['groups']),8)
        self.assertTrue(record['inverse_ast_equal'])
        self.assertFalse(record['effect_ready'])
        self.assertEqual(adapter.verify_postimage(PREIMAGE,output,expected_preimage_sha256=PREIMAGE_SHA,expected_completion_sha256=adapter.completion_digest()),record)
        for optimization in (0,2):compile(output,'<not-executed>','exec',optimize=optimization)

    def test_original_finally_policy_and_emit_preserved(self):
        output,_=self.project();before=ast.parse(PREIMAGE);after=ast.parse(output)
        get=lambda t,name:next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name==name)
        for name in ['emit','_t35_binding_path','_t35_effect_refused']:
            self.assertEqual(ast.dump(get(before,name)),ast.dump(get(after,name)))
        p1,p2=get(before,'provision'),get(after,'provision')
        self.assertEqual(ast.dump(ast.Module(body=p1.body[1:],type_ignores=[])),ast.dump(ast.Module(body=p2.body[1:],type_ignores=[])))
        for tree in [before,after]:
            node=next(n for n in ast.walk(get(tree,'build')) if isinstance(n,ast.Try))
            self.assertEqual([ast.unparse(n) for n in node.finalbody],['channel.close()','key = None'])

    def test_manifest_only_two_values_change(self):
        output,_=self.project()
        def fields(raw):
            n=next(n for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='manifest' for t in n.targets))
            return {k.value:ast.dump(v) for k,v in zip(n.value.keys,n.value.values)}
        a,b=fields(PREIMAGE),fields(output)
        self.assertEqual(set(a),set(b));self.assertEqual({k for k in a if a[k]!=b[k]},{'schema_version','claim_ceiling'})

    def test_result_claims_are_fixture_only(self):
        output,_=self.project();tree=ast.parse(output)
        n=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='result' for t in n.targets))
        d={k.value:v.value for k,v in zip(n.value.keys,n.value.values) if isinstance(v,ast.Constant)}
        for k in ['original_generation_executed','actual_carrier_validation','authentic_permission','task_complete']:self.assertIs(d[k],False)
        self.assertIs(d['fixture_only'],True);self.assertEqual(d['native_processes'],0)

    def test_completion_contract_and_final_call_route(self):
        output,record=self.project();c=adapter.completion_contract()
        self.assertEqual(c['sequence'][-5:],['FINISH_SENT_ONCE','FINISH_ACK','CHECKED_CLIENT_CLOSE','EMIT_RETURN','SUMMARY'])
        self.assertEqual(c['missing_manifest_ack_finish_count'],0)
        self.assertFalse(c['retry']);self.assertFalse(record['bridge_implemented'])
        build=next(n for n in ast.parse(output).body if isinstance(n,ast.FunctionDef) and n.name=='build')
        self.assertEqual(ast.unparse(build.body[-2]),"emit(out / 'manifest.json', manifest)")
        self.assertIsInstance(build.body[-1].value.func,ast.Name);self.assertEqual(build.body[-1].value.func.id,'print')

    def test_wrong_preimage_and_completion_pins(self):
        for kw in [{'expected_preimage_sha256':'0'*64},{'expected_completion_sha256':'0'*64}]:
            with self.assertRaises(adapter.Refusal):self.project(**kw)

    def test_reselected_lifecycle_mutations_refuse(self):
        for old,new in [(b'channel.close()',b'channel = None'),(b'key = None',b'key = key'),(b'_ctx_private_root_absent(root)',b'pass'),(b'root = Path(tmp)',b"root = Path('/tmp/other')"),(b'Ed25519PrivateKey.generate()',b'None'),(b"emit(out / 'manifest.json', manifest)",b"emit(out / 'other.json', manifest)")]:
            self.assertIn(old,PREIMAGE)
            with self.subTest(old=old),self.assertRaisesRegex(adapter.Refusal,'SKELETON'):self.project(PREIMAGE.replace(old,new,1))

    def test_extra_finish_or_unknown_source_edit_refuses(self):
        for raw in [PREIMAGE+b'\nextra = True\n',PREIMAGE.replace(b"emit(out / 'manifest.json', manifest)",b"emit(out / 'manifest.json', manifest)\n    finish()")]:
            with self.assertRaisesRegex(adapter.Refusal,'SKELETON'):self.project(raw)

    def test_new_fixture_pin_and_layout_remain_explicit(self):
        raw=PREIMAGE.replace(b'/tmp/legacy-context-pure-0001',b'/tmp/legacy-context-pure-0002').replace(b'2dc815a9cf7b6bf38c7bc32d97feec1ebfbba6745fba363ff4058e4db6c5a22b',b'3'*64)
        output,record=self.project(raw);self.assertIn(b'/tmp/legacy-context-pure-0002',output);self.assertEqual(record['preimage_sha256'],sha(raw))

    def test_nonfixture_or_aliased_layout_refuses(self):
        for new in [b'/etc/output',b'/tmp/../output',b'/tmp/context-pure-snapshot-0001']:
            with self.assertRaises(adapter.Refusal):self.project(PREIMAGE.replace(b'/tmp/legacy-context-pure-0001',new))

    def test_changed_postimage_refuses(self):
        output,_=self.project()
        with self.assertRaisesRegex(adapter.Refusal,'POSTIMAGE_DRIFT'):
            adapter.verify_postimage(PREIMAGE,output+b'\n',expected_preimage_sha256=PREIMAGE_SHA,expected_completion_sha256=adapter.completion_digest())


if __name__=='__main__':unittest.main(verbosity=2)
