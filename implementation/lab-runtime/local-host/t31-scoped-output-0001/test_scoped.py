"""Synthetic component proofs; no native producer execution is inferred."""
import ast
import copy
import dataclasses
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scoped_store import S, ROOT, ScopeSelection, ScopedOutputJournal, sha
from scoped_currentness import Selection, OwnedCurrentness

FIXTURE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/current-api30-output-fixture-20261023/test_output_journal.py'
if sha(FIXTURE.read_bytes())!='ca61ee8b23e1d9c14331d520bdb90bed7c948c42a5fc62770f44bbf48407b880':
    raise ValueError('selected fixture changed')
spec=importlib.util.spec_from_file_location('_t31_scoped_synthetic_fixture',FIXTURE)
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)


class ScopedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='cal-T31-scoped-test-')
        self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name)
        self.plan,before,old_header=F.candidate_plan()
        run=self.plan['next_run'];self.authority_scope=old_header['scope_ref']
        body=json.loads((ROOT/'authority/artifact-types/ontology-node/v2/fixtures/valid/record.json').read_bytes())
        self.raw=S.J.K.encoded(body)
        self.header={'scope_ref':body['scope_ref'],'identity_ref':body['node_id'],
            'version_ref':body['node_id']+'@synthetic.scoped.1','carrier_ref':'cal.artifact-type.ontology-node/v2',
            'byte_sha256':sha(self.raw)}
        self.plan['allowed_output_carriers']=[self.header['carrier_ref']]
        self.plan=S.O.attach_outputs(S.J.K,self.plan,outputs=[self.header],
            raw_by_ref={self.header['version_ref']:self.raw},carriers=S.original_carriers(),
            scope_ref=self.header['scope_ref'],work_ref=run['work']['version_ref'],
            transition_ref=self.plan['event']['transition_ref'])
        self.journal=S.J.Journal.initialize(self.folder/'journal',before,self.authority_scope,run['actor']['principal_ref'])
        (self.journal.root/'outputs').mkdir(mode=0o700)
        producer=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001/workflow_ontology_outputs.py'
        self.contract={'schema_version':'lab-private-owned-native-workflow-scope/v1-candidate',
            'producer_binding':{'path':str(producer),'sha256':sha(producer.read_bytes())},
            'producer_entrypoint':'OntologyTypedCapture.produce','review_sha256':'a'*64,
            'source_binding':{'ref':'fixture:source','sha256':'b'*64},'source_cut':run['source_cut'],
            'principal_ref':run['actor']['principal_ref'],'work_ref':run['work']['version_ref'],
            'container_scope_ref':self.header['scope_ref'],'authority_scope_ref':self.authority_scope,
            'permitted_body_scope_refs':[body['scope_ref']],'authority_effect':'none'}
        self.proof={k:v for k,v in self.contract.items() if k not in ('schema_version','permitted_body_scope_refs')}
        self.proof.update(schema_version='lab-original-native-record-scope/v1-candidate',
            artifact=self.header,body_scope_ref=body['scope_ref'])
        self.lineage={'run_binding':self.plan['event']['before_run_binding'],'work_ref':run['work']['version_ref'],
            'source_cut':run['source_cut'],'principal_ref':run['actor']['principal_ref']}
        self.receipt={'schema_version':'SYNTHETIC-SCOPE-TEST-ONLY','artifact':self.header,
            'proof':self.proof,'lineage':self.lineage,'native_producer_executed':False}
        self.members=[]
        for name,value in [('contract',self.contract),('proof',self.proof),('lineage',self.lineage),('receipt',self.receipt)]:
            path=self.folder/(name+'.json');raw=S.J.K.encoded(value);path.write_bytes(raw);path.chmod(0o600)
            self.members.append({'ref':'fixture:'+name,'path':path.name,'sha256':sha(raw)})
        def binding(name):
            row=next(r for r in self.members if r['ref']=='fixture:'+name)
            return {'ref':row['ref'],'sha256':row['sha256']}
        self.index={'schema_version':'lab-owned-native-scope-index/v1','journal_config_sha256':self.journal.config_sha256,
            'scope_ref':self.authority_scope,'run_ref':run['run_ref'],'actor':run['actor'],'work':run['work'],
            'source_cut':run['source_cut'],'members':self.members,
            'entries':[{'transition_ref':self.plan['event']['transition_ref'],'artifact':self.header,
                'contract_binding':binding('contract'),'proof_binding':binding('proof'),
                'lineage_binding':binding('lineage'),'producer_receipt_binding':binding('receipt'),
                'artifact_selector':'/artifact','proof_selector':'/proof','lineage_selector':'/lineage'}],
            'authority_effect':'none'}
        self.index_path=self.folder/'scope-index.json';self.index_path.write_bytes(S.J.K.encoded(self.index));self.index_path.chmod(0o600)
        self.scope=ScopeSelection.from_host(self.index_path,sha(self.index_path.read_bytes()))
        self.store=ScopedOutputJournal(self.journal.root,self.journal.config_sha256,scope_selection=self.scope)
        self.plan['producer_receipt_bindings']=[binding('receipt')]
        self.request=F.binding('fixture:scoped-request',S.J.K.encoded({'route':self.plan['event']['transition_ref']}))
        self.selection=Selection.from_host(self.store,source_cut=run['source_cut'],actor=run['actor'],
            work=run['work'],run_ref=run['run_ref'],scope_ref=self.authority_scope,
            producer_receipts=self.plan['producer_receipt_bindings'],
            producer_paths={'fixture:receipt':self.folder/'receipt.json'},scope_selection=self.scope)

    def apply(self,**kwargs):
        return self.store.apply(self.plan,originals={self.header['version_ref']:self.raw},
            request_binding=self.request,host_guard=lambda:None,**kwargs)

    def current(self):
        raw=S.read_owned(self.store.root/'transactions/00000001.json')
        return OwnedCurrentness(self.selection,host_guard=lambda:None).resolve(
            self.header,sequence=1,transaction_sha256=sha(raw))

    def test_native_header_and_body_scope_preserved_with_Project_authority(self):
        self.assertNotEqual(self.header['scope_ref'],self.authority_scope)
        tx=self.apply();self.assertEqual(self.apply(),tx)
        self.assertEqual(self.store.consume(1),[(self.header,self.raw)])
        self.assertEqual(self.current()['posture'],'owned-produced-current')
        self.assertEqual(self.current()['artifact']['scope_ref'],self.header['scope_ref'])
        self.assertEqual(json.loads(self.raw)['scope_ref'],self.header['scope_ref'])
        self.assertEqual(tx['canonical_admissions'],0)

    def test_original_unscoped_profile_refuses_committed_native_container(self):
        self.apply()
        with self.assertRaises(ValueError):S.OutputJournal(self.store.root,self.journal.config_sha256)

    def test_separate_process_reopens_scope_evidence_and_original_bytes(self):
        self.apply()
        script="import sys;sys.path.insert(0,sys.argv[1]);from scoped_store import *;s=ScopedOutputJournal(Path(sys.argv[2]),sys.argv[3],scope_selection=ScopeSelection.from_host(sys.argv[4],sys.argv[5]));h,b=s.consume(1)[0];print(h['scope_ref'],sha(b))"
        p=subprocess.run([sys.executable,'-I','-B','-c',script,str(Path(__file__).parent),str(self.store.root),
            self.journal.config_sha256,str(self.index_path),self.scope.index_sha256],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(p.stdout.strip(),self.header['scope_ref']+' '+sha(self.raw))

    def test_changed_proof_or_receipt_refuses_before_claim(self):
        for name in ('proof','receipt','contract','lineage'):
            p=self.folder/(name+'.json');saved=p.read_bytes();p.write_bytes(saved+b' ')
            try:
                with self.assertRaises(ValueError):self.apply()
                self.assertEqual(list((self.store.root/'claims').iterdir()),[])
            finally:p.write_bytes(saved)

    def test_changed_scope_index_refuses_cold_open(self):
        self.apply();self.index_path.write_bytes(self.index_path.read_bytes()+b' ')
        with self.assertRaises(ValueError):ScopedOutputJournal(self.store.root,self.journal.config_sha256,scope_selection=self.scope)

    def test_output_changed_after_commit_refuses_currentness(self):
        self.apply();p=self.store.root/'outputs'/sha(self.raw);p.write_bytes(self.raw+b' ')
        with self.assertRaises(ValueError):self.current()

    def test_exact_producing_Run_preimage_required_before_claim(self):
        self.plan['event']['before_run_binding']={'ref':'fixture:another-run','sha256':'9'*64}
        with self.assertRaisesRegex(ValueError,'preimage'):self.apply()
        self.assertEqual(list((self.store.root/'claims').iterdir()),[])

    def test_wrong_producing_Work_refuses_before_claim(self):
        self.plan['next_run']['work']['version_ref']='work:foreign@1'
        with self.assertRaisesRegex(ValueError,'Work'):self.apply()
        self.assertEqual(list((self.store.root/'claims').iterdir()),[])

    def test_scoped_orphan_does_not_become_current(self):
        self.store._stage(self.plan,{self.header['version_ref']:self.raw})
        with self.assertRaisesRegex(ValueError,'unheaded'):
            OwnedCurrentness(self.selection,host_guard=lambda:None).resolve(
                self.header,sequence=1,transaction_sha256='0'*64)

    def test_metadata_mutation_between_stage_and_claim_refuses(self):
        calls=0
        def guard():
            nonlocal calls
            calls+=1
            if calls==2:
                p=self.folder/'proof.json';p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaises(ValueError):
            self.store.apply(self.plan,originals={self.header['version_ref']:self.raw},request_binding=self.request,host_guard=guard)
        self.assertEqual(list((self.store.root/'claims').iterdir()),[])

    def test_coordinated_Work_and_plan_digest_mutation_before_claim_refuses(self):
        calls=0
        def guard():
            nonlocal calls
            calls+=1
            if calls==2:
                self.plan['next_run']['work']['version_ref']='work:changed-after-stage@1'
                self.plan['next_run_structural_sha256']=S.J.K.digest(self.plan['next_run'])
        with self.assertRaisesRegex(ValueError,'Work'):
            self.store.apply(self.plan,originals={self.header['version_ref']:self.raw},
                request_binding=self.request,host_guard=guard)
        self.assertEqual(list((self.store.root/'claims').iterdir()),[])

    def test_scoped_recovery_rechecks_private_evidence_before_HEAD(self):
        with self.assertRaises(S.J.Indeterminate):self.apply(crash_at='after-transaction')
        fingerprint=S.J.digest({'request_binding':self.request,'plan':self.plan})
        p=self.folder/'proof.json';saved=p.read_bytes();p.write_bytes(saved+b' ')
        with self.assertRaises(ValueError):self.store.recover(self.plan['event']['idempotency_key'],fingerprint,host_guard=lambda:None)
        self.assertEqual(self.journal.replay()[0]['sequence'],0)
        p.write_bytes(saved);self.store.recover(self.plan['event']['idempotency_key'],fingerprint,host_guard=lambda:None)
        self.assertEqual(self.current()['posture'],'owned-produced-current')

    def test_retaging_header_cannot_borrow_Project_scope(self):
        self.apply();changed=copy.deepcopy(self.header);changed['scope_ref']=self.authority_scope
        resolver=OwnedCurrentness(self.selection,host_guard=lambda:None)
        with self.assertRaises(ValueError):resolver.resolve(changed,sequence=1,transaction_sha256=sha(S.read_owned(self.store.root/'transactions/00000001.json')))

    def later_output(self,container):
        self.apply()
        before=S.J.K.encoded(self.plan['next_run'])
        body=json.loads(self.raw);body['scope_ref']=container;body['name']+=' successor'
        raw=S.J.K.encoded(body);header={**self.header,'scope_ref':container,
            'version_ref':self.header['identity_ref']+'@synthetic.scoped.2','byte_sha256':sha(raw)}
        plan=copy.deepcopy(self.plan);event=plan['event'];run=plan['next_run']
        event.update(idempotency_key=event['idempotency_key']+':second',request_ref=event['request_ref']+':second',
            from_state=run['state'],to_state='responded',before_run_binding=F.binding('fixture:second-before',before))
        run['state']='responded';run['event_bindings'].append({'ref':'fixture:pending','sha256':'0'*64})
        plan['expected_before_sha256']=sha(before)
        plan=S.O.attach_outputs(S.J.K,plan,outputs=[header],raw_by_ref={header['version_ref']:raw},
            carriers=S.original_carriers(),scope_ref=container,work_ref=run['work']['version_ref'],
            transition_ref=event['transition_ref'])
        contract=copy.deepcopy(self.contract);contract.update(container_scope_ref=container,permitted_body_scope_refs=[container])
        proof=copy.deepcopy(self.proof);proof.update(artifact=header,container_scope_ref=container,body_scope_ref=container)
        lineage={**self.lineage,'run_binding':event['before_run_binding']}
        receipt={'schema_version':'SYNTHETIC-SCOPE-TEST-ONLY','artifact':header,'proof':proof,
            'lineage':lineage,'native_producer_executed':False}
        bindings={}
        for name,value in [('contract',contract),('proof',proof),('lineage',lineage),('receipt',receipt)]:
            p=self.folder/('second-'+name+'.json');b=S.J.K.encoded(value);p.write_bytes(b);p.chmod(0o600)
            row={'ref':'fixture:second-'+name,'path':p.name,'sha256':sha(b)}
            self.index['members'].append(row);bindings[name]={'ref':row['ref'],'sha256':row['sha256']}
        self.index['entries'].append({'transition_ref':event['transition_ref'],'artifact':header,
            **{key+'_binding':bindings[key] for key in ('contract','proof','lineage')},
            'producer_receipt_binding':bindings['receipt'],'artifact_selector':'/artifact',
            'proof_selector':'/proof','lineage_selector':'/lineage'})
        self.index_path.write_bytes(S.J.K.encoded(self.index))
        self.scope=ScopeSelection.from_host(self.index_path,sha(self.index_path.read_bytes()))
        self.store=ScopedOutputJournal(self.journal.root,self.journal.config_sha256,scope_selection=self.scope)
        self.selection=dataclasses.replace(self.selection,scope_selection=self.scope)
        plan['producer_receipt_bindings']=[bindings['receipt']]
        self.store.apply(plan,originals={header['version_ref']:raw},
            request_binding=F.binding('fixture:second-request',before),host_guard=lambda:None)
        self.assertEqual(self.store.replay()[0]['sequence'],2)

    def test_same_local_identity_in_another_native_container_does_not_retire(self):
        self.later_output('scope:independent-second-ontology')
        self.assertEqual(self.current()['artifact'],self.header)

    def test_later_revision_in_same_native_container_retires(self):
        self.later_output(self.header['scope_ref'])
        with self.assertRaisesRegex(ValueError,'later committed revision'):self.current()

    def test_new_kernel_changes_only_one_explicit_scope_predicate(self):
        old=ast.parse((ROOT/'implementation/lab-runtime/local-host/t31-owned-produced-0001/owned_kernel.py').read_text())
        new=ast.parse(Path(__file__).with_name('scoped_kernel.py').read_text())
        old_plan=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='plan')
        new_plan=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='plan')
        source=Path(__file__).with_name('scoped_kernel.py').read_text()
        restored=source.replace("selected_headers.scope_permitted(header,host_grant['scope_ref'])","header['scope_ref']==host_grant['scope_ref']")
        restored_plan=next(n for n in ast.parse(restored).body if isinstance(n,ast.FunctionDef) and n.name=='plan')
        self.assertNotEqual(ast.dump(old_plan,include_attributes=False),ast.dump(new_plan,include_attributes=False))
        self.assertEqual(ast.dump(old_plan,include_attributes=False),ast.dump(restored_plan,include_attributes=False))


if __name__=='__main__':unittest.main()
