import copy
import json
import os
import shutil
import subprocess
import sys
import unittest
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE))
from bootstrap import *
from build_package import seed_materials,write_package


class BootstrapTests(unittest.TestCase):
    observed=None

    @classmethod
    def setUpClass(cls):
        row=next(r for r in load(RUNTIME/'profiles/selections.json')['selections'] if r['name']=='d75')
        selection=select(ROOT,**{k:v for k,v in row.items() if k not in ['name','source_materials','source_bytes']})
        cls.baseline=capture(selection);cls.materials=seed_materials(cls.baseline)
        cls.catalog=compose(cls.materials)
        cls.original_source={p:byte_digest(file_bytes(ROOT/p)) for p in cls.baseline['materials']}

    @classmethod
    def tearDownClass(cls):
        assert cls.original_source=={p:byte_digest(file_bytes(ROOT/p)) for p in cls.baseline['materials']}

    def setUp(self):
        self.tmp=TemporaryDirectory(prefix='lab-bootstrap-rehearsal-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.repo=self.root/'repository';self.repo.mkdir()
        for r in executable_manifest()['files']:
            p=under(self.repo,r['path']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(file_bytes(ROOT/r['path']))
        compatibility='docs/proposals/0007-lab-integrated-schema-package/schema-dependencies.json'
        p=under(self.repo,compatibility);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(file_bytes(ROOT/compatibility))
        self.packages=self.repo/'implementation/lab-bootstrap/candidates/v1/packages'
        self.sel,self.cat=write_package(self.repo,self.packages/'0001',self.materials)
        self.policy,self.key=self.policy_for('old')

    def policy_for(self,name):
        private=Ed25519PrivateKey.generate();key=self.root/(name+'.pem')
        key.write_bytes(private.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));key.chmod(0o600)
        policy=RehearsalPolicy('fixture:catalog-owner:'+name,private.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex(),
            'fixture-catalog-'+name,str(self.root/('store-'+name)),'scope:S01:isolated-fixture',(datetime.now(timezone.utc)+timedelta(minutes=20)).isoformat())
        return policy,key

    def initialized(self):
        proposal=prepare(self.sel,self.policy);response=sign(proposal,self.policy,self.key)
        result=apply(self.sel,proposal,response,self.policy);pins=CatalogPins(**result['pins'])
        return proposal,response,result,pins

    def change_target(self,materials,index,fn):
        inp=loads(materials['input.json']);target=inp['targets'][index];record=loads(materials[target['path']]);fn(record)
        materials[target['path']]=encoded(record);target['sha256']=byte_digest(materials[target['path']])
        if target['carrier_ref']==METHOD_TYPE and 'residue_rule' in record:materials[target['path'].removesuffix('.json')+'.md']=method_markdown(record)
        materials['input.json']=encoded(inp)

    def successor(self):
        materials=copy.deepcopy(self.materials);inp=loads(materials['input.json'])
        excluded=next(t for t in inp['targets'] if t['path']=='relations/product-uses-method.json')
        inp['targets'].remove(excluded);materials.pop(excluded['path'])
        method=loads(materials['method/example.json']);method.update(method_id='method:lab-second-inspection',name='Second bounded inspection')
        materials['method/second.json']=encoded(method);materials['method/second.md']=method_markdown(method)
        inp['targets'].append({'version_ref':method['method_id']+'@'+method['version'],'identity_ref':method['method_id'],'identity_selector':'/method_id',
            'category':'artifact-instance','carrier_ref':METHOD_TYPE,'semantic_kind':'method','path':'method/second.json','sha256':byte_digest(materials['method/second.json']),'predecessor_ref':None})
        materials['input.json']=encoded(inp)
        selected,catalog=write_package(self.repo,self.packages/'0002',materials,parent_selection=self.sel)
        choices=[{'version_ref':t['version_ref'],'disposition':'exclude' if t['version_ref']==excluded['version_ref'] else 'carry',
                  'reason':'explicit selected candidate scope'} for t in self.cat['candidate_subjects'].values()]
        return selected,catalog,choices,excluded['version_ref']

    def test_01_complete_method_and_inherited_catalog(self):
        self.assertEqual(len(self.cat['contracts']),144);self.assertEqual(len(self.cat['source_subjects']),485)
        self.assertEqual(len(self.cat['relation_contracts']),41);self.assertEqual(len(self.cat['candidate_subjects']),6)
        self.assertIsNone(self.cat['contracts'][METHOD_TYPE]['admission_decision_ref'])
        self.assertEqual(self.cat['contracts'][METHOD_TYPE]['lifecycle_state'],'candidate-unadmitted')
        self.assertEqual(self.cat['contracts'][METHOD_TYPE]['semantic_definition_refs'],[METHOD_DEFINITION])
        self.assertEqual(self.materials['method/example.md'],method_markdown(loads(self.materials['method/example.json'])))
        body=self.materials['method/example.md'].decode().split('```json\n',1)[1].split('\n```',1)[0]
        self.assertEqual(loads(body),loads(self.materials['method/example.json']))

    def test_02_bootstrap_and_fresh_process(self):
        proposal,response,result,pins=self.initialized()
        verified=replay(self.policy.destination,pins,self.policy)
        control=self.root/'cold-controls.json';control.write_bytes(encoded({'pins':asdict(pins),'policy':self.policy.core()}))
        code="import sys;sys.path.insert(0,sys.argv[1]);from bootstrap import *;c=load(sys.argv[2]);r=replay(c['policy']['destination'],CatalogPins(**c['pins']),RehearsalPolicy(**c['policy']));print(digest(r['records']))"
        process=subprocess.run([sys.executable,'-c',code,str(PACKAGE),str(control)],capture_output=True,text=True,timeout=60)
        self.assertEqual(process.returncode,0,process.stderr);self.assertEqual(process.stdout.strip(),digest(verified['records']))
        self.assertTrue(apply(self.sel,proposal,response,self.policy)['idempotent'])
        BootstrapTests.observed={'fixture_only':True,'catalog_contract_versions':144,'inherited_source_subjects':485,
            'candidate_subjects':6,'relation_kinds':41,'new_relation_kinds':0,'cold_fresh_process_verified':True,
            'generator_implementation_ref':self.cat['generator']['implementation_ref'],'canonical_registry_mutations':0,
            'canonical_project_state_mutations':0,'actual_owner_outcome':None}

    def test_03_same_executable_new_profile_transition(self):
        _,_,_,oldpins=self.initialized();oldfiles={p.relative_to(Path(self.policy.destination)).as_posix():byte_digest(file_bytes(p)) for p in Path(self.policy.destination).rglob('*') if p.is_file()}
        selected,catalog,choices,excluded=self.successor();newpolicy,key=self.policy_for('new')
        proposed=prepare(selected,newpolicy,parent_path=self.policy.destination,parent_pins=oldpins,parent_policy=self.policy,selections=choices)
        response=sign(proposed,newpolicy,key)
        result=apply(selected,proposed,response,newpolicy,parent_path=self.policy.destination,parent_pins=oldpins,parent_policy=self.policy)
        verified=replay(newpolicy.destination,CatalogPins(**result['pins']),newpolicy)
        self.assertNotIn(excluded,verified['records']);self.assertEqual(len(verified['records']),6)
        self.assertFalse(verified['plan']['parent']['signatures_copied'])
        self.assertEqual(oldfiles,{p.relative_to(Path(self.policy.destination)).as_posix():byte_digest(file_bytes(p)) for p in Path(self.policy.destination).rglob('*') if p.is_file()})
        self.assertEqual(self.sel.executable_manifest,selected.executable_manifest)
        self.assertNotEqual(self.sel.profile_sha256,selected.profile_sha256)
        BootstrapTests.observed['profile_transition']={'observed':True,'carried':5,'excluded':1,'new_candidates':1,'same_exact_executable':True,'parent_bytes_preserved':True,'signatures_copied':False,'fresh_fixture_key':True}

    def test_04_missing_method_definition_rejected(self):
        materials=copy.deepcopy(self.materials);baseline=loads(materials['baseline.json'])
        baseline['subjects'].pop(METHOD_DEFINITION);baseline['snapshot_digest']=digest({k:v for k,v in baseline.items() if k!='snapshot_digest'})
        materials['baseline.json']=encoded(baseline);inp=loads(materials['input.json']);inp['baseline_snapshot_digest']=baseline['snapshot_digest'];materials['input.json']=encoded(inp)
        with self.assertRaises(RuntimeFault):compose(materials)

    def test_05_wrapper_identity_and_mapping_noncollapse(self):
        materials=copy.deepcopy(self.materials);inp=loads(materials['input.json']);inp['endpoint_mappings'][0]['identity_selector']='/node_id';materials['input.json']=encoded(inp)
        with self.assertRaises(RuntimeFault):compose(materials)
        inp=loads(self.materials['input.json']);inp['endpoint_mappings'][1]['endpoint_kind']='project';materials['input.json']=encoded(inp)
        with self.assertRaises(RuntimeFault):compose(materials)

    def test_06_method_binding_cannot_substitute_method(self):
        materials=copy.deepcopy(self.materials);inp=loads(materials['input.json']);inp['targets'][1]['carrier_ref']='cal.artifact-type.method-binding/v1';materials['input.json']=encoded(inp)
        with self.assertRaises(RuntimeFault):compose(materials)

    def test_07_unknown_and_private_material_rejected(self):
        materials=copy.deepcopy(self.materials);materials['secret.json']=encoded({'short_memory':'keep me'})
        with self.assertRaises(RuntimeFault):compose(materials)
        materials=copy.deepcopy(self.materials);self.change_target(materials,1,lambda r:r.update(scope='PRIVATE KEY fixture'))
        with self.assertRaises(RuntimeFault):compose(materials)

    def test_08_missing_method_fields_and_projection_drift(self):
        materials=copy.deepcopy(self.materials);self.change_target(materials,1,lambda r:r.pop('residue_rule'))
        with self.assertRaises((RuntimeFault,KeyError)):compose(materials)
        materials=copy.deepcopy(self.materials);materials['method/example.md']+=b'edited projection\n'
        with self.assertRaises(RuntimeFault):compose(materials)

    def test_09_typed_axis_and_endpoint_closure(self):
        for change in [lambda r:r['payload']['source'].update(kind='method'),lambda r:r['payload']['target'].update(version_ref='missing@v1'),lambda r:r['payload'].update(qualifiers={'purpose':'wrong-axis'})]:
            materials=copy.deepcopy(self.materials);self.change_target(materials,3,change)
            with self.assertRaises(RuntimeFault):compose(materials)

    def test_10_contract_and_generator_pins(self):
        materials=copy.deepcopy(self.materials);materials['method/schema.json']+=b' '
        with self.assertRaises(RuntimeFault):compose(materials)
        materials=copy.deepcopy(self.materials);self.change_target(materials,2,lambda r:r['payload'].update(execution_entrypoint_ref='implementation/lab-runtime/v1/lab.py'))
        with self.assertRaises(RuntimeFault):compose(materials)

    def test_11_effect_and_identity_collision_rejected(self):
        materials=copy.deepcopy(self.materials);self.change_target(materials,1,lambda r:r.update(authority_effect='admit'))
        with self.assertRaises(RuntimeFault):compose(materials)
        materials=copy.deepcopy(self.materials);self.change_target(materials,2,lambda r:r.update(node_id='implementation:cyberalchemy-lab:operational-runtime:v1'))
        inp=loads(materials['input.json']);t=inp['targets'][2];t['identity_ref']='implementation:cyberalchemy-lab:operational-runtime:v1';t['version_ref']=t['identity_ref']+'@candidate.2';materials['input.json']=encoded(inp)
        with self.assertRaises(RuntimeFault):compose(materials)

    def test_12_live_repository_or_nonfixture_policy_rejected(self):
        with self.assertRaises(RuntimeFault):replace(self.policy,destination=str(ROOT/'.local'/'candidate-illegal')).core()
        with self.assertRaises(RuntimeFault):replace(self.policy,fixture_only=False).core()
        with self.assertRaises(RuntimeFault):replace(self.policy,effect='admit-repository').core()

    def test_13_wrong_key_and_fabricated_human_outcome_rejected(self):
        proposed=prepare(self.sel,self.policy);other,key=self.policy_for('other')
        with self.assertRaises(RuntimeFault):sign(proposed,self.policy,key)
        response=sign(proposed,self.policy,self.key);response['human_outcome']='Admit'
        with self.assertRaises(RuntimeFault):apply(self.sel,proposed,response,self.policy)
        self.assertFalse(Path(self.policy.destination).exists())

    def test_14_tamper_extra_file_and_symlink_rejected(self):
        _,_,_,pins=self.initialized();root=Path(self.policy.destination)
        original=file_bytes(root/'records.json');(root/'records.json').write_bytes(original+b' ')
        with self.assertRaises(RuntimeFault):replay(root,pins,self.policy)
        (root/'records.json').write_bytes(original);(root/'extra.json').write_bytes(b'{}')
        with self.assertRaises(RuntimeFault):replay(root,pins,self.policy)
        (root/'extra.json').unlink();(root/'linked').symlink_to(root/'records.json')
        with self.assertRaises(RuntimeFault):replay(root,pins,self.policy)

    def test_15_wrong_external_pins_and_expired_policy(self):
        _,_,_,pins=self.initialized()
        with self.assertRaises(RuntimeFault):replay(self.policy.destination,replace(pins,head_sha256='0'*64),self.policy)
        expired=replace(self.policy,expires_at=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat());proposal=prepare(self.sel,expired)
        with self.assertRaises(RuntimeFault):sign(proposal,expired,self.key)

    def test_16_unknown_destination_and_writer_lock(self):
        proposed=prepare(self.sel,self.policy);response=sign(proposed,self.policy,self.key)
        dest=Path(self.policy.destination);dest.mkdir();(dest/'unknown').write_bytes(b'preserve')
        with self.assertRaises(RuntimeFault):apply(self.sel,proposed,response,self.policy)
        self.assertEqual((dest/'unknown').read_bytes(),b'preserve')
        shutil.rmtree(dest)
        fd=os.open(dest.parent/('.'+dest.name+'.bootstrap.lock'),os.O_CREAT|os.O_RDWR,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaises(RuntimeFault):apply(self.sel,proposed,response,self.policy)
        finally:os.close(fd)

    def test_17_transition_needs_fresh_key_and_explicit_exclusion(self):
        _,_,_,pins=self.initialized();selected,catalog,choices,excluded=self.successor();policy,key=self.policy_for('new')
        with self.assertRaises(RuntimeFault):prepare(selected,replace(policy,public_key=self.policy.public_key),parent_path=self.policy.destination,parent_pins=pins,parent_policy=self.policy,selections=choices)
        with self.assertRaises(RuntimeFault):prepare(selected,policy,parent_path=self.policy.destination,parent_pins=pins,parent_policy=self.policy,selections=choices[:-1])
        bad=copy.deepcopy(choices);next(r for r in bad if r['version_ref']==excluded)['disposition']='carry'
        with self.assertRaises(RuntimeFault):prepare(selected,policy,parent_path=self.policy.destination,parent_pins=pins,parent_policy=self.policy,selections=bad)

    def test_18_capture_source_drift_rejected(self):
        proposed=prepare(self.sel,self.policy);response=sign(proposed,self.policy,self.key)
        (self.packages/'0001/method/example.json').write_bytes(file_bytes(self.packages/'0001/method/example.json')+b' ')
        with self.assertRaises(RuntimeFault):apply(self.sel,proposed,response,self.policy)

    def test_19_crash_stage_and_after_commit_recover(self):
        for hook in ['after-stage','after-publish']:
            policy,key=self.policy_for(hook);proposal=prepare(self.sel,policy);response=sign(proposal,policy,key)
            controls=self.root/(hook+'.json');controls.write_bytes(encoded({'selection':load(self.packages/'0001/selection.json'),'policy':policy.core(),'response':response}))
            code="import sys;sys.path.insert(0,sys.argv[1]);from bootstrap import *;c=load(sys.argv[2]);s=select(Path(sys.argv[3]),**c['selection']);p=RehearsalPolicy(**c['policy']);v=prepare(s,p);apply(s,v,c['response'],p,crash_at=sys.argv[4])"
            p=subprocess.run([sys.executable,'-c',code,str(PACKAGE),str(controls),str(self.repo),hook],capture_output=True,text=True,timeout=60)
            self.assertEqual(p.returncode,75 if hook=='after-stage' else 76,p.stderr)
            result=apply(self.sel,proposal,response,policy);self.assertTrue(replay(policy.destination,CatalogPins(**result['pins']),policy)['cold_replay'])

    def test_20_historical_carrier_and_mechanics_drift_rejected(self):
        materials=copy.deepcopy(self.materials);inp=loads(materials['input.json']);inp['targets'][3]['carrier_ref']='cal.artifact-type.typed-relation/v2';materials['input.json']=encoded(inp)
        with self.assertRaises(RuntimeFault):compose(materials)
        materials=copy.deepcopy(self.materials);mech=loads(materials['method/mechanics.json']);mech['lifecycle']['admission']='automatic';materials['method/mechanics.json']=encoded(mech)
        with self.assertRaises(RuntimeFault):compose(materials)


if __name__=='__main__':unittest.main()
