"""Author an immutable API successor; retain every predecessor test assertion."""
import ast, hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parent
PARENT = ROOT / 'product/lab/release-candidates/v1/interface/api-v17'
OUT = PARENT.parent / 'api-v18'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def bind(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}
def encoded(value): return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
def methods(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

def main():
    assert not OUT.exists(), 'successor already exists'
    context = json.loads((RUN / 'context-R03-custody-api-0002.json').read_bytes())
    assert context['strict_coverage'] == 'PASS'
    assert sha((PARENT / 'source-manifest.json').read_bytes()) == '99f1d11bbb28f86cd2a745caed8849a6a14fc9753566b36fc11241e65c6d7740'
    manifest = json.loads((PARENT / 'source-manifest.json').read_bytes())
    for row in manifest['files']:
        assert sha((ROOT / row['path']).read_bytes()) == row['sha256'], row['path']
    shutil.copytree(PARENT, OUT, ignore=shutil.ignore_patterns('__pycache__', 'receipts', 'observations',
        'source-manifest.json', 'contract-profile.json', '*.log', 'derivation.json'))
    changes = {}
    for name in ['run_session_checks.py', 'test_custody_sessions.py']:
        path = OUT / name
        text = path.read_text()
        old = "ref=lambda i:selected.sources.resolve(i+'@'+R.VERSION)[0].artifact"
        assert text.count(old) == 1
        text = text.replace(old, "ref=lambda i:copy.deepcopy(selected.sources.resolve(i+'@'+R.VERSION)[0].artifact)")
        begin = text.index('    @classmethod\n    def setUpClass(cls):')
        end = text.index('    def invoke(self,c,*,raw=None):', begin)
        selected = 'custody-participation' if name == 'test_custody_sessions.py' else 'fresh-participation'
        setup = f'''    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.addClassCleanup(cls.stack.close)
        cls.view=cls.stack.enter_context(source.replay_source('{selected}'));cls.schemas=Schemas(PROFILE)
        cls.materials,cls.metadata,cls.target=materials_for(cls.view)
        cls.events=[]
    def setUp(self):
        # Every method receives a fresh host/key/nonce and the same bounded grant.
        # A slow full suite must not inherit another method's expired permission.
        self.fixture_stack=ExitStack();self.addCleanup(self.fixture_stack.close)
        self.root=Path(self.fixture_stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-isolated-Session-method-')));self.root.chmod(0o700)
        self.key,self.policy,self.policy_pin=provision(self.root,'{selected}',self.materials,self.metadata,principal=R.PRINCIPAL,projection_control=projection_control(self.view))
        self.channel=ReaderChannel(self.policy,self.policy_pin,self.schemas);self.authenticated=self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas);self.fixture_stack.callback(self.service.close)
        self.delivery_result=None;self.opened=[]
'''
        text = text[:begin] + setup + text[end:]
        assert text.count('self.__class__.delivery_result=self.success(c)') == 1
        text = text.replace('self.__class__.delivery_result=self.success(c)', 'self.delivery_result=self.success(c)')
        path.write_text(text)
        assert methods(path) == methods(PARENT / name), name
        changes[name] = {'methods': len(methods(path)), 'changed_test_method_ASTs': [],
                        'helper_changes': ['copy exact source headers before request mutation',
                                           'new independently bounded host/key/nonce for each method',
                                           'method-local delivery and Session resource cleanup'],
                        'production_permission_limits_changed': False}
    for name in ['checks.py', 'source_bridge.py']:
        path=OUT/name;path.write_text(path.read_text().replace('_cal_api_v17', '_cal_api_v18'))
    path=OUT/'schemas/catalog-envelope.schema.json';value=json.loads(path.read_bytes())
    for branch in value['oneOf']:
        branch['properties']['representation_profile_binding']['const']['ref']=str((OUT/'catalog-representations.json').relative_to(ROOT))
    path.write_bytes(encoded(value))
    # Final freeze also requires the actual predecessor terminal and full failed report.
    path=OUT/'freeze.py';text=path.read_text().replace("parent=HERE.parent/'api-v16'", "parent=HERE.parent/'api-v17'")
    text=text.replace("for p in [HERE/'custody_context_sessions.py',HERE/'guard.py']:profile['files'].append(bind(p))", "assert len({r['path'] for r in profile['files']})==len(profile['files'])")
    text=text.replace("RUN/'context-R03-custody-api-0001.json',RUN/'CONTEXT-R03-custody-api-0001.md',RUN/'derive-R03-custody-api-0001.py'", "RUN/'context-R03-custody-api-0002.json',RUN/'CONTEXT-R03-custody-api-0002.md',RUN/'derive-R03-custody-api-0002.py',RUN/'custody-api-terminal-0001.json',RUN/'custody-api-failure-analysis-0001.json',parent/'checks-0001.log',parent/'receipts/checks.json',parent/'receipts/wire-observations.json'")
    text=text.replace("assert changed==(['test_30_current_handler_profile_retains_all_original_contracts'] if name=='run_session_checks.py' else []),(name,changed)", "assert changed==[],(name,changed)")
    text=text.replace("for name in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py']:", "for name in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py','test_custody_sessions.py','test_custody_api.py']:")
    text=text.replace("    original_profile=json.loads", "    terminal=json.loads((RUN/'custody-api-terminal-0001.json').read_bytes());failed=json.loads((parent/'receipts/checks.json').read_bytes())\n    assert terminal['exit_code']==1 and failed['result']=='FAIL' and failed['tests_run']==failed['expected_tests']==129\n    assert terminal['source_binding']==bind(parent/'source-manifest.json') and terminal['checks_binding']==bind(parent/'receipts/checks.json') and terminal['log_binding']==bind(parent/'checks-0001.log')\n    original_profile=json.loads")
    path.write_text(text)
    derivation = {'schema_version':'lab-original-source-api-correction/v1-candidate',
        'parent_source_binding':bind(PARENT/'source-manifest.json'),
        'context_binding':bind(RUN/'context-R03-custody-api-0002.json'),
        'helper_corrections':changes,'original_tests_retained':129,
        'actual_predecessor_terminal_pending':True,'freeze_requires_actual_full_predecessor_result':True,
        'public_operations_added':0,'implemented_operations':12,'original_operations':34,
        'remaining_operations':22,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    (OUT/'derivation.json').write_bytes(encoded(derivation))
    for path in OUT.rglob('*.py'): ast.parse(path.read_bytes())
    print(json.dumps({'result':'AUTHORED-UNFROZEN','root':str(OUT),'unchanged_test_methods':sum(len(methods(OUT/n)) for n in ['run_session_checks.py','test_custody_sessions.py']), 'freeze_blocked_on_actual_predecessor_terminal':True}))

if __name__ == '__main__': main()
