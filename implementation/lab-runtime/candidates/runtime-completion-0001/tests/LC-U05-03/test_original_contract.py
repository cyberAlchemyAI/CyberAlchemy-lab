"""Static exact-original compatibility; never import an original module/body."""
import argparse,ast,hashlib,json,unittest
from pathlib import Path
from test_support import R,B,P
T07='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
POLICY=R/'implementation/lab-runtime/candidates/runtime-completion-0001/selectors/public-source-role-policy.json'
API=R/B.API
def tree(path):return ast.parse(path.read_bytes(),filename=str(path))
def method(path,cls,name):
    nodes=tree(path).body
    if cls:nodes=next(n for n in nodes if isinstance(n,ast.ClassDef)and n.name==cls).body
    return next(n for n in nodes if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name==name)
def args(node):return [a.arg for a in node.args.args]

class OriginalTests(unittest.TestCase):
    def test_anchor_exact_original_fields(self):
        t=tree(R/B.ORIGINAL_ROLES['protected_inputs'])
        cls=next(n for n in t.body if isinstance(n,ast.ClassDef)and n.name=='CustodyAnchor')
        self.assertEqual([n.target.id for n in cls.body if isinstance(n,ast.AnnAssign)],
            ['principal_ref','public_key_b64','source_binding','profile_binding','source_cut','operation','selector_binding','grant_binding','selector_locator','grant_locator'])
    def test_protected_reader_signature(self):
        self.assertEqual(args(method(R/B.ORIGINAL_ROLES['protected_inputs'],'ProtectedReader','__init__')),
                         ['self','selector_raw','grant_raw','anchor'])
    def test_schemas_independent_expected_profile_argument(self):
        self.assertEqual(args(method(API/'protocol.py','Schemas','__init__')),['self','expected_profile_sha256'])
    def test_reader_channel_original_signature_and_authentication(self):
        self.assertEqual(args(method(API/'auth.py','ReaderChannel','__init__')),['self','path','expected_sha','schemas'])
        self.assertEqual(args(method(API/'auth.py','ReaderChannel','authenticate')),['self','raw'])
    def test_service_session_constructor_signature(self):
        selected=method(API/'service.py','Service','__init__')
        self.assertEqual(args(selected),['self','view','channel','schemas'])
        self.assertEqual([a.arg for a in selected.args.kwonlyargs],['parent_host','session_attachment_binding'])
        for name in ('current_context_sessions.py','current_legacy_context_sessions.py'):
            self.assertEqual(args(method(API/name,'ContextSessions','__init__')),['self','view','channel','schemas','vault'])
            self.assertEqual(args(method(API/name,'PermissionBridge','__init__')),['self','selected','channel','schemas'])
            call=next(n for n in ast.walk(method(API/name,'ContextSessions','view_get')) if isinstance(n,ast.Call)
                      and isinstance(n.func,ast.Attribute)and n.func.attr=='generate')
            self.assertEqual(ast.unparse(call.args[0]),'self.source')
            self.assertEqual(ast.unparse(call.args[1]),'self.bridge')
    def test_original_composite_constructor_signature(self):
        self.assertEqual(args(method(R/B.ORIGINAL_ROLES['environment'],'CompositeEnvironment','__init__')),
                         ['self','descriptor','pin','repository','r02','dependencies','original_guard'])
    def test_completion_bridge_and_release_signatures(self):
        self.assertEqual(args(method(API/'completion_bridges.py','CompletionBridge','__init__')),
                         ['self','raw','independent_binding','repository','modules','environment'])
        self.assertEqual(args(method(API/'installation_release.py','InstallationRelease','__init__')),['self','host','operation','deadline'])
    def test_native_and_context_calls_both_families(self):
        base=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02'
        for family in ('optimized-family-preparation-0005/instances/optimized-0005',
                       'fresh-legacy-current-runtime-preparation-0009/instances/legacy-source8-20261018-b'):
            path=base/family/'context/generation.py'
            self.assertEqual(args(method(path,None,'generate')),['source','channel','message','request_raw','mapped_pin','schemas'])
            self.assertEqual(args(method(path,None,'selected_mapping')),['package_pin'])
    def test_original_full_22_table_occurrences_metadata_only(self):
        raw=POLICY.read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),B.PUBLIC_POLICY_SHA)
        policy=json.loads(raw);docs={}
        for row in policy['documents']:
            b=row['binding'];self.assertEqual(b['root_id'],'repository')
            data=(R/b['relative_path']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(),b['sha256']);self.assertEqual(len(data),b['size_bytes'])
            docs[row['id']]=json.loads(data)
        counts=[]
        for row in policy['tables']:
            values=docs[row['document_id']][row['selector'][1:]]
            if isinstance(values,dict):values=[values]
            self.assertEqual(len(values),row['row_count']);counts.append(len(values))
        self.assertEqual(len(counts),22);self.assertEqual(sum(counts),241598)
        self.assertEqual(len(docs['current-source']['files']),32011)
        # No path in any metadata row is opened by this test.
    def test_complete_720_original_dependency_rows(self):
        raw=(R/T07).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),B.DEPENDENCY_SHA)
        value=json.loads(raw);counts={}
        for row in value['inputs']:counts[row['kind']]=counts.get(row['kind'],0)+1
        self.assertEqual(counts,{'wheel':8,'interpreter':1,'native-executable':1,'stdlib':687,'host-abi':23})
        self.assertEqual(value['execution_configuration']['python_flags'],['-I','-X','utf8','-B','-S'])
    def test_actual_scope_requires_installed_flags_not_env_assumption(self):
        class InertActualPosture:
            posture='actual'
        with self.assertRaises(P.Refusal):B.installed_runtime(InertActualPosture(),
            {'executable_file_id':'x','bytecode_prefix_file_id':'y','preloaded_modules':{},'mapped_file_ids':[]},[])
    def test_actual_cold_cannot_coherently_repin_original(self):
        class InertActualPosture:
            posture='actual'
        selected={'policy_file_id':'p','policy_sha256':'0'*64,'documents':{},'origins':[],
                  'dependencies_file_id':'d','dependencies_sha256':'0'*64,'runtime_origins':[]}
        with self.assertRaises(P.Refusal):B.cold_closure(InertActualPosture(),selected,[])

def main():
    p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);p.parse_args()
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OriginalTests))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if r.wasSuccessful()else'FAIL','checks':r.testsRun,'effect_state':'owned-inert','cleanup':'clean'}));raise SystemExit(0 if r.wasSuccessful()else 1)
if __name__=='__main__':main()
