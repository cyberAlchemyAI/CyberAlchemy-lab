"""Execute pinned original policy AST and complete original release v1 constructor."""
import argparse,ast,copy,json,sys,types,unittest
from pathlib import Path
from policy_compat import API,PINS,LINEAGE,checked,method,policy,require
class OriginalCompatibility(unittest.TestCase):
    def test_original_separate_shapes_and_worker_uid(self):
        for role in ('participation','installation-metadata'):
            p=policy(role,'legacy-source8-20261018-b',role,'fixture-key',uid=20001)
            checked(p,20001)
            with self.assertRaises(ValueError):checked(p,20002)
    def test_original_rejects_old_union_fields(self):
        p=policy('participation','legacy-source8-20261018-b','p','k');p['installation_release_control']={}
        with self.assertRaises(ValueError):checked(p)
    def test_original_rejects_old_union_operations(self):
        p=policy('participation','legacy-source8-20261018-b','p','k');p['allowed_operations'].append('installation.execute')
        with self.assertRaises(ValueError):checked(p)
    def test_original_source8_kind_and_session_predicates(self):
        fn=method('auth.py','ReaderChannel','policy_guard')
        messages=('unselected Source8 authority kind','Source8 source requires actual Session permission or independent assessment grant')
        nodes=[n for n in ast.walk(fn)if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant)and n.value.args[1].value in messages]
        self.assertEqual(len(nodes),2)
        for role,accept in (('participation',True),('installation-metadata',False)):
            value=policy(role,'optimized-0005',role,'k');env=checked(value);env['control']=value['session_control']
            code=compile(ast.Module(body=copy.deepcopy(nodes),type_ignores=[]),str(API/'auth.py'),'exec')
            if accept:exec(code,env)
            else:
                with self.assertRaises(ValueError):exec(code,env)
    def test_complete_original_release_constructor(self):
        fn=method('installation_release.py','InstallationRelease','__init__')
        env={'source':types.SimpleNamespace(parse=json.loads,require=require),'ApplicationError':ValueError}
        exec(compile(ast.Module(body=[copy.deepcopy(fn)],type_ignores=[]),str(API/'installation_release.py'),'exec'),env)
        plan={'schema_version':'lab-installation-release-plan/v1-candidate','principal_ref':'metadata','source_cut':{},'install':None,'release':None,'authority_effect':'none','actual_owner_outcome':None}
        cls=type('OriginalV1Constructor',(),{'__init__':env['__init__'],'read':lambda self,b:json.dumps(plan).encode()})
        for role in ('participation','installation-metadata'):
            p=policy(role,'legacy-source8-20261018-b','metadata','k')
            host=types.SimpleNamespace(vault=object(),channel=types.SimpleNamespace(policy_guard=lambda:p,context={'principal_ref':'metadata'}))
            if role=='participation':
                with self.assertRaises(ValueError):cls(host,'release.prepare',object())
            else:self.assertEqual(cls(host,'release.prepare',object()).plan,plan)
        print(json.dumps({'executed_original':{'path':str(API/'installation_release.py'),'sha256':PINS['installation_release.py'],'method':'InstallationRelease.__init__','range':[fn.lineno,fn.end_lineno]},'v2_validation':'NOT_RUN'}),file=sys.stderr)
def main():
    p=argparse.ArgumentParser();p.add_argument('--temp-root',required=True,type=Path);p.parse_args()
    print(json.dumps({'original_ast_lineage':LINEAGE,'source_pins':PINS,'actual_original_path':'NOT_RUN'}),file=sys.stderr)
    r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OriginalCompatibility))
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS'if r.wasSuccessful()else'FAIL','checks':r.testsRun,'effect_state':'owned-inert','cleanup':'clean'}));raise SystemExit(0 if r.wasSuccessful()else 1)
if __name__=='__main__':main()
