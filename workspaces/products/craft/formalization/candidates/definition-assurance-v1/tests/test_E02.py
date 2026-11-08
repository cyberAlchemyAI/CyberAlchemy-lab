"""Real no-replace publication, collision races and interrupted preservation."""
import copy
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[3]
UNIT=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/E01'
sys.path[:0]=[str(UNIT),str(HERE),str(HERE/'tests')]
import bundles as b
import test_E01 as fixture


def advance_version(control):
    """Add a genuine next-version byte fixture, retaining prior source versions."""
    prior=next(row for row in control.fixture.entries if row['definition_id']=='DEF-A' and row['version']=='2.0.0');entry=copy.deepcopy(prior);entry.update(version='3.0.0',path='authority/definitions/DEF-A-3.0.0.json')
    raw=json.dumps({'definition_id':'DEF-A','version':'3.0.0','term':'Alpha','body':'A revised synthetic source clause.'}).encode();control.fixture.write(entry['path'],raw);entry['sha256']=b.r.digest(raw);control.fixture.entries.append(entry);control.fixture.registry['current_lookup']['DEF-A']='DEF-A@3.0.0';control.fixture.save_registry();snapshot=b.r.capture(control.root)
    sources={row['definition_id']:{key:row[key] for key in ['definition_id','version_ref','path','sha256']} for row in snapshot['current_entries']}
    rel,bindings,populations=fixture.relation.setup_relation(control.root)
    for side,key in [('left','DEF-A'),('right','DEF-B')]:rel[side+'_definition'].clear();rel[side+'_definition'].update(sources[key])
    alignment=json.loads((control.root/'alignment.json').read_text());alignment.update(left_source=rel['left_definition'],right_source=rel['right_definition']);raw=json.dumps(alignment).encode();(control.root/'alignment.json').write_bytes(raw);rel['alignment']['map_ref']['sha256']=b.r.digest(raw)
    theory=json.loads((control.root/control.bundle['theory_ref']['path']).read_text());theory['sources']=[rel['left_definition'],rel['right_definition']]
    requests=[{'relation':rel,'bindings':bindings,'proper':False,'distinction':'permitted','forbidden':[]}];required=fixture.e.o.generate(theory,requests,populations,bindings,control.root)
    bundle=copy.deepcopy(control.bundle);bundle.update(sources=copy.deepcopy(theory['sources']),snapshot_ref=control.put('candidate/snapshot.json',snapshot),theory_ref=control.put('candidate/theory.json',theory),required_set_ref=control.put('candidate/required.json',required),required_set=required,coupling_refs=[rel['alignment']['map_ref']])
    bundle['interpretations']=[{'source':copy.deepcopy(source),'scope':theory['scope'],'status':'missing','correspondence_ref':None,'typed_ir_ref':None} for source in theory['sources']]
    bundle['logical_results']=[]
    for obligation in required['logical_manifest']['obligations']:
        result=fixture.basic.payloads()['result'];result.update(obligation_id=obligation['obligation_id'],statement_sha256=fixture.e.digest(obligation['statement']),theory_sha256=required['logical_manifest']['theory_sha256'],verdict='missing')
        bundle['logical_results'].append({'obligation':copy.deepcopy(obligation),'result':result,'provider_kind':'unresolved','native_input_ref':None,'native_result':None,'profile_ref':None,'toolchain_ref':None})
    bundle['gate_results']=[{'gate':copy.deepcopy(gate),'execution':'not-run','currentness':'unknown','reported_status':'pending','evidence_refs':[],'native_result':None,'readiness':'not-assessed'} for gate in required['administrative_and_semantic_gates']]
    control.bundle=bundle;control.required=required


class PublicationControls(unittest.TestCase):
    def setUp(self):
        self.fixture,self.bundle,self.required,self.put=fixture.create_fixture();self.addCleanup(self.fixture.doCleanups);self.root=self.fixture.root;self.parent=b.BASE+'/units/E02/test-published'
    def publish(self,**options):return b.publish(self.root,self.bundle,self.required,self.parent,**options)
    def inspect(self,report,live=True):return b.inspect(self.root,report['bundle_ref'],self.required,self.root if live else None)
    def bytes_under(self,path):return {str(file.relative_to(path)):file.read_bytes() for file in path.rglob('*') if file.is_file()}

    def test_actual_publish_and_closed_capture_inspection(self):
        out=self.publish();self.assertEqual('published-candidate',out['status']);self.assertEqual(8,out['artifact_files']);self.assertFalse(out['semantic_ready']);report=self.inspect(out);self.assertEqual('PASS',report['result']);self.assertEqual('verified-live',report['source_currentness'])

    def test_repeated_identity_collides_and_preserves_original_and_attempt(self):
        first=self.publish();path=self.root/first['bundle_ref'];before=self.bytes_under(path);second=self.publish();self.assertEqual('publication-collision',second['status']);self.assertEqual(before,self.bytes_under(path));attempt=self.root/second['preserved_attempt_ref'];self.assertTrue((attempt/'manifest.json').is_file());self.assertTrue((attempt/'envelope.json').is_file())

    def test_empty_directory_created_at_final_race_is_not_overwritten(self):
        inode=[]
        def compete(info):
            path=self.root/info['output_parent']/info['target'];path.mkdir();inode.append(path.stat().st_ino)
        out=self.publish(before_publish=compete);self.assertEqual('publication-collision',out['status']);attempt=self.root/out['preserved_attempt_ref'];manifest=json.loads((attempt/'manifest.json').read_text());target=self.root/self.parent/('bundle-'+manifest['bundle_id'].split(':',1)[1]);self.assertEqual(inode[0],target.stat().st_ino);self.assertEqual([],list(target.iterdir()))

    def test_file_created_at_final_race_is_not_overwritten(self):
        targets=[]
        def compete(info):
            path=self.root/info['output_parent']/info['target'];path.write_bytes(b'competing publication');targets.append(path)
        out=self.publish(before_publish=compete);self.assertEqual('publication-collision',out['status']);self.assertEqual(b'competing publication',targets[0].read_bytes())

    def test_target_symlink_does_not_replace_or_modify_its_referent(self):
        referent=self.root/'other';referent.mkdir();marker=referent/'marker';marker.write_bytes(b'preserve')
        def compete(info):(self.root/info['output_parent']/info['target']).symlink_to(referent,target_is_directory=True)
        out=self.publish(before_publish=compete);self.assertEqual('publication-collision',out['status']);self.assertEqual(b'preserve',marker.read_bytes())

    def test_interruption_keeps_private_attempt_and_previous_success(self):
        first=self.publish();before=self.bytes_under(self.root/first['bundle_ref'])
        def interrupt(info):raise InterruptedError('synthetic interruption')
        out=self.publish(before_publish=interrupt);self.assertEqual('publication-unresolved',out['status']);self.assertTrue((self.root/out['preserved_attempt_ref']).is_dir());self.assertEqual(before,self.bytes_under(self.root/first['bundle_ref']))

    def test_partial_write_failure_preserves_inputs_and_attempt(self):
        original=b.write_file;calls=[0];source=self.root/self.bundle['sources'][0]['path'];raw=source.read_bytes()
        def fail(directory,name,data):
            calls[0]+=1
            if calls[0]==2:raise InterruptedError('synthetic interrupted write')
            return original(directory,name,data)
        with patch.object(b,'write_file',side_effect=fail):out=self.publish()
        self.assertEqual('publication-unresolved',out['status']);self.assertEqual(raw,source.read_bytes());attempt=self.root/out['preserved_attempt_ref'];self.assertTrue(attempt.is_dir());self.assertEqual(1,len(list((attempt/'objects').iterdir())))

    def test_source_change_before_installation_keeps_attempt_without_publication(self):
        source=self.root/self.bundle['sources'][0]['path'];changed=source.read_bytes()+b' '
        out=self.publish(before_publish=lambda info:source.write_bytes(changed));self.assertEqual('publication-unresolved',out['status']);self.assertEqual('artifact-changed-before-publication',out['diagnostics'][0]['code']);self.assertEqual(changed,source.read_bytes());self.assertTrue((self.root/out['preserved_attempt_ref']).is_dir())

    def test_registry_change_is_detected_by_final_full_snapshot_check(self):
        registry=self.root/b.r.REGISTRY;out=self.publish(before_publish=lambda info:registry.write_bytes(registry.read_bytes()+b' '));self.assertEqual('publication-unresolved',out['status']);self.assertEqual('stale-captured-source',out['diagnostics'][0]['code'])

    def test_alignment_or_non_source_artifact_change_blocks_installation(self):
        file=self.root/self.bundle['coupling_refs'][0]['path'];out=self.publish(before_publish=lambda info:file.write_bytes(file.read_bytes()+b' '));self.assertEqual('publication-unresolved',out['status']);self.assertEqual('artifact-changed-before-publication',out['diagnostics'][0]['code'])

    def test_changed_evidence_creates_new_identity_without_mutating_prior(self):
        first=self.publish();before=self.bytes_under(self.root/first['bundle_ref']);self.bundle['logical_results'][0]['result']['verdict']='unknown';second=self.publish();self.assertEqual('published-candidate',second['status']);self.assertNotEqual(first['bundle_id'],second['bundle_id']);self.assertEqual(before,self.bytes_under(self.root/first['bundle_ref']))

    def test_stale_source_version_cannot_reuse_a_current_bundle(self):
        self.bundle['sources'][0]['version_ref']='DEF-A@9.0.0';out=self.publish();self.assertEqual('publication-unresolved',out['status']);self.assertIsNone(out['preserved_attempt_ref'])

    def test_private_staging_and_files_have_restrictive_modes(self):
        out=self.publish();directory=self.root/out['bundle_ref'];self.assertEqual(0o700,directory.stat().st_mode&0o777)
        for file in directory.rglob('*'):
            self.assertEqual(0o700 if file.is_dir() else 0o600,file.stat().st_mode&0o777)

    def test_output_cannot_escape_candidate_area_or_follow_symlink_parent(self):
        out=b.publish(self.root,self.bundle,self.required,'authority/definitions/publication');self.assertEqual('publication-unresolved',out['status']);self.assertEqual('output-outside-candidate-evidence-area',out['diagnostics'][0]['code'])
        directory=self.root/b.BASE/'units/E02';directory.mkdir(parents=True);(directory/'test-published').symlink_to(self.root,target_is_directory=True);out=self.publish();self.assertEqual('publication-unresolved',out['status']);self.assertIsNone(out['preserved_attempt_ref'])

    def test_unsupported_atomic_operation_has_no_unsafe_rename_fallback(self):
        with patch.object(b,'install_no_replace',side_effect=b.BundleFault('atomic-no-replace-unavailable')):out=self.publish()
        self.assertEqual('publication-unresolved',out['status']);self.assertEqual('atomic-no-replace-unavailable',out['diagnostics'][0]['code']);self.assertTrue((self.root/out['preserved_attempt_ref']).is_dir())

    def test_corrupted_or_extra_published_objects_rejected(self):
        out=self.publish();directory=self.root/out['bundle_ref'];file=next((directory/'objects').iterdir());raw=file.read_bytes();file.write_bytes(raw+b' ')
        with self.assertRaises(b.BundleFault) as caught:self.inspect(out)
        self.assertEqual('corrupt-published-object',caught.exception.code);file.write_bytes(raw);(directory/'extra').write_bytes(b'unselected')
        with self.assertRaises(b.BundleFault) as caught:self.inspect(out)
        self.assertEqual('unexpected-published-file',caught.exception.code)

    def test_historical_capture_survives_later_live_source_change(self):
        out=self.publish();source=self.root/self.bundle['sources'][0]['path'];source.write_bytes(source.read_bytes()+b' ');historical=self.inspect(out,live=False);self.assertEqual('PASS',historical['result']);self.assertEqual('historical-capture-only',historical['source_currentness'])
        with self.assertRaises(b.r.CaptureFault):self.inspect(out,live=True)

    def test_post_installation_source_race_is_retained_but_not_reported_current(self):
        original=b.install_no_replace;source=self.root/self.bundle['sources'][0]['path']
        def change(parent,attempt,target):
            original(parent,attempt,target);source.write_bytes(source.read_bytes()+b' ')
        with patch.object(b,'install_no_replace',side_effect=change):out=self.publish()
        self.assertEqual('published-currentness-unconfirmed',out['status']);self.assertTrue((self.root/out['published_ref']).is_dir());self.assertFalse(out['semantic_ready'])

    def test_post_installation_fsync_failure_keeps_output_and_reports_uncertainty(self):
        original_install=b.install_no_replace;original_sync=os.fsync;installed=[False]
        def install(parent,attempt,target):original_install(parent,attempt,target);installed[0]=True
        def sync(fd):
            if installed[0]:raise OSError('synthetic post-install fsync failure')
            return original_sync(fd)
        with patch.object(b,'install_no_replace',side_effect=install),patch.object(b.os,'fsync',side_effect=sync):out=self.publish()
        self.assertEqual('published-durability-unconfirmed',out['status']);self.assertTrue((self.root/out['published_ref']).is_dir())

    def test_admitted_next_version_changes_identity_and_preserves_historical_bundle(self):
        first=self.publish();before=self.bytes_under(self.root/first['bundle_ref']);old_required=copy.deepcopy(self.required);advance_version(self);second=self.publish();self.assertEqual('published-candidate',second['status']);self.assertNotEqual(first['bundle_id'],second['bundle_id']);self.assertEqual(before,self.bytes_under(self.root/first['bundle_ref']))
        historical=b.inspect(self.root,first['bundle_ref'],old_required);self.assertEqual('historical-capture-only',historical['source_currentness']);self.assertEqual('PASS',historical['result'])
        with self.assertRaises(b.r.CaptureFault):b.inspect(self.root,first['bundle_ref'],old_required,self.root)

    def test_independently_selected_producer_build_rejects_substitution(self):
        out=self.publish();expected=b.checked_contract();report=b.inspect(self.root,out['bundle_ref'],self.required,self.root,expected);self.assertEqual('compared-with-independently-selected-build',report['producer_build']);expected['publisher_sha256']='0'*64
        with self.assertRaises(b.BundleFault) as caught:b.inspect(self.root,out['bundle_ref'],self.required,self.root,expected)
        self.assertEqual('published-contract-build-substitution',caught.exception.code)

    def test_total_capture_limit_preserves_inputs_without_partial_publication(self):
        source=self.root/self.bundle['sources'][0]['path'];before=source.read_bytes()
        with patch.object(b,'MAX_TOTAL_BYTES',16):out=self.publish()
        self.assertEqual('publication-unresolved',out['status']);self.assertEqual('bundle-total-byte-limit',out['diagnostics'][0]['code']);self.assertIsNone(out['preserved_attempt_ref']);self.assertEqual(before,source.read_bytes())


if __name__=='__main__':unittest.main()
