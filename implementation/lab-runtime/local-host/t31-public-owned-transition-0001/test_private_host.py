"""Synthetic callback mechanics; does not authenticate an API or producer."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace,ModuleType
import sys
import unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE));import private_host as H
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(body):return json.dumps(body,sort_keys=True,separators=(',',':')).encode()
def producer_guard():return None

class Vault:
    def material(self,b):
        raw=self.raws[b['ref']]
        if sha(raw)!=b['sha256']:raise ValueError('synthetic selected original changed')
        return raw
class Channel:
    policy={'scope_refs':['project:fixture']}
    def termination_guard(self):return None
class Host:pass
Host.__module__='_private_callback_component.service'

class PrivateHost(unittest.TestCase):
    def setUp(self):
        self.names=[]
        protocol=ModuleType('_private_callback_component.protocol');protocol.ROOT=ROOT;protocol.source=SimpleNamespace(sha=sha)
        protocol.frame_parse=json.loads;protocol.compact=enc
        model=ModuleType('_private_callback_component.artifact_model')
        handlers=ModuleType('_private_callback_component.handlers');handlers.cut=lambda view:view.cut
        for module in (protocol,model,handlers):sys.modules[module.__name__]=module;self.names.append(module.__name__)
        self.host=Host();self.host.channel=Channel();self.host.handlers=SimpleNamespace(view=SimpleNamespace(cut={'fixture':'cut'}));self.host.vault=Vault();self.host.vault.raws={}
        raw=enc({'kind':'work','node_id':'work:fixture'});binding={'ref':'original:work','sha256':sha(raw)}
        self.host.vault.raws[binding['ref']]=raw;self.row={'artifact':{'scope_ref':'project:fixture','identity_ref':'work:fixture','version_ref':'work:fixture@1','carrier_ref':'cal.artifact-type.work/v1','byte_sha256':sha(raw)},'original_binding':binding}
        roles={key:self.row for key in ('intent','resolution','work','coordination','goal','decision','decision_profile')}
        roles.update(effects=[self.row],decision_edges=[self.row],goal_edges=[])
        self.index={'schema_version':'lab-private-owned-workflow-host-inputs/v1','scope_ref':'project:fixture','source_cut':{'fixture':'cut'},'actor':{'fixture':'actor'},'run_ref':'workflow-run:fixture',
          'roles':roles,'inputs':{'work:fixture@1':self.row},'outputs':{'transition:fixture:done':[self.row]},'producer_receipt_bindings':[binding],'authority_effect':'none'}
        raw=enc(self.index);self.input_binding={'ref':'private:index','sha256':sha(raw)};self.host.vault.raws['private:index']=raw
        self.state=H.HostState(self.host,input_binding=self.input_binding,store=SimpleNamespace(),header_type=object,currentness_type=object,selection_type=object,producer_guard=producer_guard)
        self.run={'run_ref':'workflow-run:fixture','actor':{'fixture':'actor'}}
    def tearDown(self):
        for name in self.names:sys.modules.pop(name,None)
    def test_exact_private_body_and_producer_binding_are_read(self):
        result=self.state.outputs({'transition_ref':'transition:fixture:done'},{},self.run,{})
        self.assertEqual(result['artifacts'],[self.row['artifact']]);self.assertEqual(sha(result['originals']['work:fixture@1']),self.row['artifact']['byte_sha256'])
    def test_changed_independent_index_refused(self):
        self.host.vault.raws['private:index']+=b' '
        with self.assertRaisesRegex(ValueError,'original changed'):self.state.guard()
    def test_captured_index_mutation_refused(self):
        self.state.index['authority_effect']='admit'
        with self.assertRaisesRegex(ValueError,'inputs changed'):self.state.guard()
    def test_changed_original_output_refused(self):
        self.host.vault.raws['original:work']+=b' '
        with self.assertRaisesRegex(ValueError,'original changed'):self.state.outputs({'transition_ref':'transition:fixture:done'},{},self.run,{})
    def test_foreign_Run_Actor_and_unknown_transition_refused(self):
        with self.assertRaisesRegex(ValueError,'Run/Actor'):self.state.semantics({'run_ref':'another','actor':{}},{},{})
        with self.assertRaisesRegex(ValueError,'lacks this transition'):self.state.outputs({'transition_ref':'transition:foreign'},{},self.run,{})
    def test_current_cut_mutation_refused(self):
        self.host.handlers.view.cut={'fixture':'another'}
        with self.assertRaisesRegex(ValueError,'cut changed'):self.state.guard()

if __name__=='__main__':unittest.main()
