"""Original-compatible role composition; inert controlled original constructors."""
import argparse,json,sys,unittest
from pathlib import Path
from test_support import P,B,Fixture
class CompositionTests(unittest.TestCase):
    def roles(self,operation='installation.execute',metadata_config=None):
        a=Fixture(TEMP,family='legacy-source8-20261018-b',config={'principal':'fixture-participation'})
        b=Fixture(TEMP,family='legacy-source8-20261018-b',role='installation-metadata',config={'principal':'fixture-metadata',**(metadata_config or{})})
        self.addCleanup(a.close);self.addCleanup(b.close)
        for f in (a,b):
            f.selection['operation']=operation
            private=P.parse((f.root/'private.json').read_bytes());private['anchor']['operation']=operation
            f.put('private','private.json',P.canonical(private),'protected-input');f.reseal()
        return a,b
    def composition(self,a,b):
        selected={k:a.selection[k]for k in ('family','operation','profile_sha256','source_cut')}
        selected.update(schema_version='lab-startup-composition-selection/v1',participation_sha256=a.sha,metadata_sha256=b.sha)
        raw=P.canonical(selected)
        return B.Composition(a.startup(),b.startup(),raw,P.digest(raw))
    def test_both_original_roles_sequential_and_counted(self):
        for operation in ('installation.execute','release.prepare'):
            with self.subTest(operation=operation):
                a,b=self.roles(operation);result=self.composition(a,b).run()
                self.assertIsNone(result['primary_code'],result);self.assertTrue(result['sequential_constructor_coverage'])
                self.assertFalse(result['simultaneously_live_contexts']);self.assertFalse(result['composite_readiness'])
                self.assertIn('context-generate',a.event_list());self.assertNotIn('release',a.event_list())
                self.assertIn('release',b.event_list());self.assertNotIn('context-generate',b.event_list());self.assertNotIn('sessions-close',b.event_list())
                for f,observed in zip((a,b),result['roles']):
                    budget=P.startup_query_budget(f.selection)
                    self.assertLessEqual(f.custody._checks+1,budget['total']);self.assertGreater(observed['elapsed_monotonic_ns'],0)
                    print(json.dumps({'role':f.role,'operation':operation,'observed_queries':f.custody._checks,'budget':budget}),file=sys.stderr,flush=True)
    def test_second_closure_corrupt_refuses_before_first_import(self):
        a,b=self.roles();composition=self.composition(a,b)
        (b.root/'code/common.py').write_bytes(b'raise RuntimeError("PRIVATE")')
        r=composition.run();self.assertIsNotNone(r['primary_code']);self.assertEqual(a.event_list(),[]);self.assertEqual(b.event_list(),[])
    def test_same_principal_cannot_compose(self):
        a,b=self.roles(metadata_config={'principal':'fixture-participation'})
        with self.assertRaises(P.Refusal):self.composition(a,b)
    def test_same_reader_key_refuses_before_import(self):
        a,b=self.roles(metadata_config={'reader_public_key':'fixture-key-participation'})
        r=self.composition(a,b).run();self.assertIsNotNone(r['primary_code']);self.assertEqual(a.event_list()+b.event_list(),[])
    def test_first_cleanup_failure_prevents_second_role(self):
        a,b=self.roles();first=a.startup();second=b.startup();check=a.custody.check
        def boundary(stage):
            if stage=='cleanup':raise P.Refusal('DENIED')
            return check(stage)
        a.custody.check=boundary
        selection={k:a.selection[k]for k in ('family','operation','profile_sha256','source_cut')}
        selection.update(schema_version='lab-startup-composition-selection/v1',participation_sha256=a.sha,metadata_sha256=b.sha)
        raw=P.canonical(selection);r=B.Composition(first,second,raw,P.digest(raw)).run()
        self.assertIsNotNone(r['primary_code']);self.assertEqual(b.event_list(),[]);self.assertTrue(r['roles'][0]['outcome']['cleanup_codes'])
    def test_other_authority_rechecked_before_second_role(self):
        a,b=self.roles();composition=self.composition(a,b);check=b.custody.check
        def boundary(stage):
            if 'source-exit' in a.event_list():raise P.Refusal('REVOKED')
            return check(stage)
        b.custody.check=boundary;r=composition.run()
        self.assertIsNotNone(r['primary_code']);self.assertEqual(len(r['roles']),1);self.assertEqual(b.event_list(),[])
    def test_authorities_rechecked_after_second_cleanup(self):
        a,b=self.roles();composition=self.composition(a,b);check=a.custody.check
        def boundary(stage):
            if 'source-exit' in b.event_list():raise P.Refusal('REVOKED')
            return check(stage)
        a.custody.check=boundary;r=composition.run()
        self.assertIsNotNone(r['primary_code']);self.assertEqual(len(r['roles']),2);self.assertFalse(r['sequential_constructor_coverage'])
    def test_optimized_metadata_never_imports(self):
        f=Fixture(TEMP,role='installation-metadata');self.addCleanup(f.close)
        with self.assertRaises(P.Refusal):f.startup()
        self.assertEqual(f.event_list(),[])
    def test_metadata_anchor_cannot_reuse_participation_principal(self):
        a,b=self.roles();private=P.parse((b.root/'private.json').read_bytes());private['anchor']['principal_ref']=a.selection['principal_ref']
        b.put('private','private.json',P.canonical(private),'protected-input');b.reseal()
        r=self.composition(a,b).run();self.assertIsNotNone(r['primary_code']);self.assertEqual(a.event_list()+b.event_list(),[])
    def test_external_composition_anchor_and_single_use(self):
        a,b=self.roles();r=self.composition(a,b);r.value['operation']='release.prepare'
        self.assertIsNotNone(r.run()['primary_code']);self.assertEqual(a.event_list()+b.event_list(),[])
        with self.assertRaises(P.Refusal):r.run()
def main():
    global TEMP
    p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);TEMP=p.parse_args().temp_root
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompositionTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if r.wasSuccessful()else'FAIL','checks':r.testsRun,'effect_state':'owned-inert','cleanup':'clean'}));raise SystemExit(0 if r.wasSuccessful()else 1)
if __name__=='__main__':main()
