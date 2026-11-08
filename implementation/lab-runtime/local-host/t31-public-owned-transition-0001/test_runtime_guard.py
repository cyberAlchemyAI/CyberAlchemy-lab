"""Causal component tests of the actual selection guard predicates.

The adapter's AST-defined guard functions run unchanged over synthetic host
objects. This avoids asserting API authentication from a component harness.
"""
import ast
import hashlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def sha(raw):return hashlib.sha256(raw).hexdigest()

tree=ast.parse((HERE/'owned_workflow_transition.py').read_bytes())
names={'need','method_identity','same_method'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Selection')
methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in ('_runtime_guard','guard')]
nodes.append(ast.ClassDef(name='ActualGuard',bases=[],keywords=[],body=methods,decorator_list=[]))
ns={'inspect':inspect,'Path':Path,'ROOT':ROOT,'source':SimpleNamespace(sha=sha,parse=json.loads),
    'read_private':lambda p:p.read_bytes(),'material':lambda policy,b:policy['scope_bytes']}
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(HERE/'owned_workflow_transition.py'),'exec'),ns)
ActualGuard=ns['ActualGuard'];identity=ns['method_identity']

class Kernel:
    def plan(self):return 'plan'
class Journal:
    def apply(self):return 'apply'
    def replay(self):return 'replay'
    def recover(self):return 'recover'
class Carriers:
    def output(self):return 'validated'
class Store(Journal):
    def consume(self):return 'consume'
class Scope:
    def guard(self):
        if sha(Path(self.selection.index_path).read_bytes())!=self.selection.index_sha256:
            raise ValueError('scope bytes changed')

class RuntimeGuard(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        folder=self.root/'workflows'/'selected';folder.mkdir(parents=True)
        self.config={'principal_ref':'principal:fixture','scope_ref':'project:fixture','run_ref':'workflow-run:fixture'}
        raw=json.dumps(self.config).encode();(folder/'config.json').write_bytes(raw)
        self.route={'journal_root':'workflows/selected','journal_config_sha256':sha(raw)}
        self.policy={'principal_ref':'principal:fixture'};self.profile={'scope_ref':'project:fixture'}
        j=Journal();j.root=folder;j.config=dict(self.config);j.config_sha256=sha(raw)
        s=Store();s.root=folder;s.journal=j;s.carriers=Carriers()
        g=ActualGuard();g.kernel=Kernel();g.store=s;g.bound_kernel=g.kernel;g.bound_store=s;g.bound_journal=j
        g.bound_carriers=s.carriers;g.bound_scope=None;g.scope_selection=None;g.scope_index_path=None;g.journal_config_raw=raw
        g.kernel_plan=identity(g.kernel.plan)
        g.store_methods={n:identity(getattr(s,n)) for n in ('apply','replay','consume','recover')}
        g.journal_methods={n:identity(getattr(j,n)) for n in ('apply','replay','recover')}
        g.carriers_output=identity(s.carriers.output)
        g.journal_origin=(str(Path(__file__).resolve()),sha(Path(__file__).read_bytes()))
        self.g=g;self.check()
    def tearDown(self):self.temp.cleanup()
    def check(self):self.g._runtime_guard(self.root,self.route,self.policy,self.profile)
    def test_exact_actual_objects_and_config_pass(self):self.check()
    def test_store_redirect_after_selection_refused(self):
        self.g.store=Store()
        with self.assertRaisesRegex(ValueError,'routing changed'):self.check()
    def test_journal_redirect_after_selection_refused(self):
        self.g.store.journal=Journal()
        with self.assertRaisesRegex(ValueError,'routing changed'):self.check()
    def test_kernel_replacement_or_plan_monkeypatch_refused(self):
        self.g.kernel=Kernel()
        with self.assertRaisesRegex(ValueError,'routing changed'):self.check()
        self.g.kernel=self.g.bound_kernel;self.g.kernel.plan=Kernel().plan
        with self.assertRaisesRegex(ValueError,'method changed'):self.check()
    def test_store_apply_redirect_after_preflight_refused(self):
        self.g.store.apply=Store().apply
        with self.assertRaisesRegex(ValueError,'method changed'):self.check()
    def test_delegated_journal_method_redirect_refused(self):
        self.g.store.journal.recover=Journal().recover
        with self.assertRaisesRegex(ValueError,'method changed'):self.check()
    def test_carrier_validator_replacement_refused(self):
        self.g.store.carriers.output=Carriers().output
        with self.assertRaisesRegex(ValueError,'method changed'):self.check()
    def test_root_change_and_same_object_config_changes_refused(self):
        self.g.store.root=self.root/'other'
        with self.assertRaisesRegex(ValueError,'routing changed'):self.check()
        self.g.store.root=self.g.bound_journal.root
        self.g.store.journal.config['run_ref']='workflow-run:foreign'
        with self.assertRaisesRegex(ValueError,'config changed'):self.check()
    def test_physical_config_change_refused(self):
        (self.g.store.root/'config.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'config changed'):self.check()
    def test_external_guard_mutation_refused_before_effect(self):
        self.g._bindings_guard=lambda deadline:self.check()
        self.g.callbacks={'guard':lambda:setattr(self.g.store,'apply',Store().apply)}
        with self.assertRaisesRegex(ValueError,'method changed'):self.g.guard()
    def test_scoped_profile_selection_cannot_be_rebound(self):
        p=self.root/'scope.json';p.write_bytes(b'{}')
        scope=Scope();scope.selection=SimpleNamespace(index_path=str(p),index_sha256=sha(b'{}'));scope.journal=self.g.bound_journal
        self.g.store.scope=scope;self.g.bound_scope=scope;self.g.scope_selection=scope.selection;self.g.scope_index_path=str(p)
        self.g.store.carriers.scope=scope;self.profile['scope_selection_binding']={'sha256':sha(b'{}')};self.policy['scope_bytes']=b'{}'
        self.check();scope.selection=SimpleNamespace(index_path=str(p),index_sha256=sha(b'{}'))
        with self.assertRaisesRegex(ValueError,'scope selection changed'):self.check()
    def test_scope_original_path_cannot_be_substituted_with_equal_bytes(self):
        self.test_scoped_profile_selection_cannot_be_rebound()
        self.g.bound_scope.selection=self.g.scope_selection
        other=self.root/'other-scope.json';other.write_bytes(b'{}');self.g.scope_selection.index_path=str(other)
        with self.assertRaisesRegex(ValueError,'scope selection changed'):self.check()

if __name__=='__main__':unittest.main()
