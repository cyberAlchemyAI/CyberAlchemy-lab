"""Source capture controls use isolated fixtures; no canonical inputs are changed."""
import base64
import copy
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(MODULE_ROOT))
import resolver as r


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.entries=[]
        for identity,version,term in [('DEF-A','1.0.0','Alpha'),('DEF-A','2.0.0','Alpha'),('DEF-B','1.0.0','Beta')]:
            path=f'authority/definitions/{identity}-{version}.json'
            raw=('  '+json.dumps({'definition_id':identity,'version':version,'term':term,'body':'A source clause.'})+'\n').encode()
            self.write(path,raw)
            self.entries.append({'definition_id':identity,'version':version,'term':term,'path':path,'sha256':r.digest(raw),
                                 'lifecycle_state':'admitted','admission_decision_ref':'DEC-A' if identity=='DEF-A' else 'DEC-B'})
        self.registry={'status':'owner-admitted','entries':self.entries,'current_lookup':{'DEF-A':'DEF-A@2.0.0','DEF-B':'DEF-B@1.0.0'},'admission_decision_ref':'DEC-B'}
        self.save_registry()
        self.write('docs/decisions/a/decision.json',json.dumps({'decision_id':'DEC-A','status':'owner-admitted'}).encode())
        self.write('docs/decisions/b/decision.json',json.dumps({'decision_refs':['OTHER','DEC-B'],'status':'owner-admitted'}).encode())

    def write(self,path,raw):
        file=self.root/path;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(raw)

    def save_registry(self):self.write(r.REGISTRY,json.dumps(self.registry).encode())

    def fault(self,code,callback):
        with self.assertRaises(r.CaptureFault) as caught:callback()
        self.assertEqual(code,caught.exception.code)

    def test_exact_current_historical_and_byte_roundtrip(self):
        snapshot=r.capture(self.root)
        self.assertEqual({'current_identities':2,'admitted_versions':3,'historical_versions':1,'decision_refs':2},snapshot['counts'])
        self.assertEqual('DEF-A@1.0.0',snapshot['historical_entries'][0]['version_ref'])
        self.assertEqual('/decision_refs/1',snapshot['admission_decision_bindings'][1]['selector'])
        for row in snapshot['captured_files']:self.assertEqual((self.root/row['path']).read_bytes(),base64.b64decode(row['content_base64']))
        self.assertEqual('PASS',r.verify(snapshot,self.root)['result'])
        self.assertEqual('none',snapshot['authority_effect'])

    def test_stale_hash_current_and_historical(self):
        for index in [0,1]:
            with self.subTest(index=index):
                file=self.root/self.entries[index]['path'];original=file.read_bytes();file.write_bytes(original+b' ')
                self.fault('stale-source-hash',lambda:r.capture(self.root));file.write_bytes(original)

    def test_missing_source(self):
        (self.root/self.entries[2]['path']).unlink()
        self.fault('missing-source',lambda:r.capture(self.root))

    def test_duplicate_version(self):
        self.registry['entries'].append(copy.deepcopy(self.entries[0]));self.save_registry()
        self.fault('duplicate-version',lambda:r.capture(self.root))

    def test_current_lookup_replaced_unbound_wrong_identity_and_nonstring(self):
        for ref in ['DEF-A@9.0.0','DEF-B@1.0.0',{'ref':'DEF-A@2.0.0'}]:
            with self.subTest(ref=ref):
                self.registry['current_lookup']['DEF-A']=ref;self.save_registry()
                self.fault('unbound-current-selection',lambda:r.capture(self.root))

    def test_incomplete_lookup_and_historical_selected(self):
        self.registry['current_lookup'].pop('DEF-B');self.save_registry()
        self.fault('incomplete-current-lookup',lambda:r.capture(self.root))
        self.registry['current_lookup']['DEF-B']='DEF-B@1.0.0';self.entries[1]['lifecycle_state']='admitted-historical';self.save_registry()
        self.fault('historical-current-selection',lambda:r.capture(self.root))

    def test_wrong_source_identity_version_term(self):
        for key,value,code in [('definition_id','DEF-C','source-identity-version-mismatch'),('version','9.0.0','source-identity-version-mismatch'),('term','Other','source-term-mismatch')]:
            with self.subTest(key=key):
                file=self.root/self.entries[1]['path'];original=file.read_bytes();doc=json.loads(original);doc[key]=value
                raw=json.dumps(doc).encode();file.write_bytes(raw);self.entries[1]['sha256']=r.digest(raw);self.save_registry()
                self.fault(code,lambda:r.capture(self.root));file.write_bytes(original);self.entries[1]['sha256']=r.digest(original);self.save_registry()

    def test_non_admitted_registry_entry_decision(self):
        self.registry['status']='candidate';self.save_registry();self.fault('non-admitted-registry',lambda:r.capture(self.root))
        self.registry['status']='owner-admitted';self.entries[0]['lifecycle_state']='candidate';self.save_registry()
        self.fault('non-admitted-entry',lambda:r.capture(self.root))
        self.entries[0]['lifecycle_state']='admitted';self.save_registry()
        self.write('docs/decisions/a/decision.json',b'{"decision_id":"DEC-A","status":"candidate"}')
        self.fault('non-admitted-decision-record',lambda:r.capture(self.root))

    def test_missing_ambiguous_admission_record(self):
        path=self.root/'docs/decisions/a/decision.json';raw=path.read_bytes();path.unlink()
        self.fault('missing-or-ambiguous-admission-record',lambda:r.capture(self.root));path.write_bytes(raw)
        self.write('docs/decisions/conflicting/decision.json',raw)
        self.fault('missing-or-ambiguous-admission-record',lambda:r.capture(self.root))

    def test_duplicate_json_not_silently_parsed(self):
        self.write(r.REGISTRY,b'{"status":"owner-admitted","status":"candidate"}')
        self.fault('malformed-source-json',lambda:r.capture(self.root))

    def test_capture_race_source_registry_and_decision(self):
        for path in [self.entries[1]['path'],r.REGISTRY,'docs/decisions/a/decision.json']:
            with self.subTest(path=path):
                file=self.root/path;raw=file.read_bytes()
                self.fault('capture-race',lambda:r.capture(self.root,after_capture=lambda:file.write_bytes(raw+b' ')));file.write_bytes(raw)

    def test_capture_race_new_conflicting_decision(self):
        raw=(self.root/'docs/decisions/a/decision.json').read_bytes()
        self.fault('missing-or-ambiguous-admission-record',lambda:r.capture(self.root,after_capture=lambda:self.write('docs/decisions/new/decision.json',raw)))

    def test_source_and_parent_symlinks_rejected(self):
        file=self.root/self.entries[1]['path'];raw=file.read_bytes();external=self.root/'external.json';external.write_bytes(raw);file.unlink();file.symlink_to(external)
        self.fault('unsafe-path',lambda:r.capture(self.root));file.unlink();file.write_bytes(raw)
        parent=self.root/'authority/definitions';parent.rename(self.root/'moved');parent.symlink_to(self.root/'moved',target_is_directory=True)
        self.fault('unsafe-path',lambda:r.capture(self.root))

    def test_nonregular_source_rejected_without_blocking(self):
        file=self.root/self.entries[1]['path'];file.unlink();os.mkfifo(file)
        self.fault('unsafe-source-kind',lambda:r.capture(self.root))

    def test_traversal_paths_and_invalid_root(self):
        for path in ['../outside','/tmp/out','a//b','a/./b','a\\b','a:b']:
            with self.subTest(path=path):self.fault('unsafe-path',lambda:r.read_bytes(self.root,path))
        self.fault('invalid-root',lambda:r.capture(self.root/'missing'))
        link=self.root/'alias';link.symlink_to(self.root,target_is_directory=True)
        self.fault('invalid-root',lambda:r.capture(link))

    def test_snapshot_tampering_bytes_duplicate_missing_metadata_and_extra(self):
        snapshot=r.capture(self.root)
        mutations=[
            ('corrupt-captured-bytes',lambda s:s['captured_files'][0].update(content_base64=base64.b64encode(b'other').decode())),
            ('malformed-captured-bytes',lambda s:s['captured_files'][0].update(content_base64='!')),
            ('duplicate-captured-path',lambda s:s['captured_files'].append(copy.deepcopy(s['captured_files'][0]))),
            ('missing-captured-source',lambda s:s['captured_files'].__setitem__(slice(None),[x for x in s['captured_files'] if x['path']!=r.REGISTRY])),
            ('inconsistent-snapshot-bindings',lambda s:s['current_entries'][0].update(term='Forged')),
            ('inconsistent-snapshot-bindings',lambda s:s['counts'].update(current_identities=183)),
            ('inconsistent-snapshot-bindings',lambda s:s.update(authority_effect='admitted')),
            ('inconsistent-snapshot-bindings',lambda s:s['source_envelope']['payload'].update(current_lookup_sha256='0'*64)),
            ('inconsistent-snapshot-bindings',lambda s:s['admission_decision_bindings'][0].update(selector='/fake')),
            ('inconsistent-snapshot-bindings',lambda s:s.update(unexpected=True)),
            ('malformed-snapshot',lambda s:s.pop('source_envelope')),
        ]
        for code,mutate in mutations:
            with self.subTest(code=code,mutation=mutate):
                changed=copy.deepcopy(snapshot);mutate(changed);self.fault(code,lambda:r.verify(changed))

    def test_boolean_and_float_metadata_cannot_impersonate_integer_counts(self):
        snapshot=r.capture(self.root)
        for key,value in [('historical_versions',True),('admitted_versions',3.0)]:
            changed=copy.deepcopy(snapshot);changed['counts'][key]=value
            self.fault('inconsistent-snapshot-bindings',lambda:r.verify(changed))


    def test_offline_snapshot_valid_even_after_live_drift_currentness_separate(self):
        snapshot=r.capture(self.root);file=self.root/self.entries[1]['path'];file.write_bytes(file.read_bytes()+b' ')
        self.assertEqual('PASS',r.verify(snapshot)['result'])
        self.fault('stale-captured-source',lambda:r.verify(snapshot,self.root))

    def test_create_only_publication_preserves_previous(self):
        snapshot=r.capture(self.root);output=r.OUTPUT_PREFIX+'fixture.json'
        r.publish(snapshot,self.root,output);file=self.root/output;raw=file.read_bytes()
        self.assertEqual(snapshot,json.loads(raw));self.fault('output-already-exists',lambda:r.publish(snapshot,self.root,output))
        self.assertEqual(raw,file.read_bytes());self.assertEqual([],list(file.parent.glob('.capture-*.tmp')))

    def test_drift_before_publication_leaves_no_output_or_temp(self):
        snapshot=r.capture(self.root);file=self.root/self.entries[1]['path'];file.write_bytes(file.read_bytes()+b' ')
        output=r.OUTPUT_PREFIX+'fixture.json';self.fault('stale-captured-source',lambda:r.publish(snapshot,self.root,output))
        self.assertFalse((self.root/output).exists());self.assertEqual([],list((self.root/output).parent.glob('.capture-*.tmp')))

    def test_protected_output_traversal_and_output_parent_symlink(self):
        snapshot=r.capture(self.root)
        self.fault('protected-output',lambda:r.publish(snapshot,self.root,'authority/fake.json'))
        self.fault('unsafe-path',lambda:r.publish(snapshot,self.root,r.OUTPUT_PREFIX+'../fake.json'))
        parent=self.root/r.OUTPUT_PREFIX;parent.parent.mkdir(parents=True,exist_ok=True);outside=self.root/'external';outside.mkdir();parent.symlink_to(outside,target_is_directory=True)
        self.fault('unsafe-path',lambda:r.publish(snapshot,self.root,r.OUTPUT_PREFIX+'fake.json'))
        self.assertEqual([],list(outside.iterdir()))


if __name__=='__main__':unittest.main()
