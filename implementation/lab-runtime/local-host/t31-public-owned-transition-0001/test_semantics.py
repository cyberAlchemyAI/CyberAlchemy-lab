"""Independent predicates over real original Work records; no API auth claim."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001/deps'),str(HERE),str(HERE.parent/'t31-retained-work-0001')]
import profiles as P
import coordination as C
import owned_workflow_semantics as S

class Semantics(unittest.TestCase):
    def setUp(self):
        self.p=P.load('engineering');m=self.p['manifest'];scope=self.p['scope_ref']
        project={'scope_ref':scope,'identity_ref':scope,'version_ref':scope+'@fixture.1','carrier_ref':'cal.artifact-type.project-identity/v1','byte_sha256':'1'*64}
        cap,raws=C.construct(self.p,run_ref='workflow-run:unit',principal='principal:fixture-metadata',source_cut=self.p['original_producer_source_cut'],project=project)
        def old(key):
            ref=m[key];return {'artifact':self.p['headers'][ref],'original':self.p['raws'][ref]}
        def new(key):
            h=cap['artifacts'][key];return {'artifact':h,'original':raws[h['version_ref']]}
        self.facts={'intent':old('intent_ref'),'resolution':new('intent-resolution'),'work':old('work_ref'),'coordination':old('coordination_ref'),
          'goal':old('goal_ref'),'decision':new('decision'),'effects':[new('effect')],'decision_edges':[new('declared-effect')],'goal_edges':[new('goal-project')]}
        self.run={role:self.facts[key]['artifact'] for key,role in [('intent','intent'),('resolution','intent_resolution'),('work','work'),('coordination','coordination_context')]}
        self.grant={'scope_ref':scope};self.definition={'single_goal_coordination':True}
    def validate(self):
        return S.validate(self.run,self.definition,self.grant,self.facts,lambda row:json.loads(row['original']))
    def mutate(self,key,edit,index=None):
        row=self.facts[key] if index is None else self.facts[key][index]
        body=json.loads(row['original']);edit(body);row['original']=P.enc(body)
    def test_actual_original_Work_meaning_and_private_IR_declaration_closes(self):self.assertTrue(self.validate())
    def test_matching_header_success_cannot_replace_wrong_Work_or_Goal_meaning(self):
        self.mutate('coordination',lambda b:b.update(project_ref='project:foreign'))
        with self.assertRaisesRegex(ValueError,'scope does not close'):self.validate()
    def test_selected_and_excluded_Work_contradiction_refused(self):
        self.mutate('resolution',lambda b:b['payload'].update(excluded_subject_refs=[self.run['work']['version_ref']]))
        with self.assertRaisesRegex(ValueError,'does not select'):self.validate()
    def test_an_unrelated_Decision_cannot_satisfy_owner_evidence(self):
        self.mutate('decision',lambda b:b['payload'].update(subject_refs=['intent-resolution:another@1']))
        with self.assertRaisesRegex(ValueError,'Decision/Resolution'):self.validate()
    def test_missing_or_foreign_Effect_refused(self):
        self.mutate('effects',lambda b:b['payload'].update(subject_ref='intent-resolution:another@1'),0)
        with self.assertRaisesRegex(ValueError,'Effect names another'):self.validate()
    def test_exact_typed_connections_required(self):
        self.mutate('decision_edges',lambda b:b['payload']['qualifiers'].update(exact_target_version_ref='intent-resolution:another@1'),0)
        with self.assertRaisesRegex(ValueError,'relation differs'):self.validate()
        self.setUp();self.mutate('goal_edges',lambda b:b['payload']['target'].update(ref='project:foreign'),0)
        with self.assertRaisesRegex(ValueError,'membership differs'):self.validate()
    def test_carrier_role_substitution_refused(self):
        self.facts['goal']['artifact']['carrier_ref']='cal.artifact-type.work/v1'
        with self.assertRaisesRegex(ValueError,'carrier role differs'):self.validate()
    def test_extra_self_declared_success_flag_refused(self):
        self.facts['permission_passed']=True
        with self.assertRaisesRegex(ValueError,'closed actual'):self.validate()

if __name__=='__main__':unittest.main()
