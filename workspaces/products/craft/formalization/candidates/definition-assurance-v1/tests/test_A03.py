"""Coverage-denominator, provenance and claim-ceiling controls."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_A02 as fixtures
ROOT=Path(__file__).resolve().parents[5]
HELPER=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/A03/assessment.py'
spec=importlib.util.spec_from_file_location('assurance_assessment',HELPER);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.CaptureTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.root=self.fixture.root
        for entry in self.fixture.entries:
            path=self.root/entry['path'];doc=json.loads(path.read_text())
            doc['voices']={'scientific_formal':{'normative_statement':'A thing has a property.','formal_expression':'P(x)'}}
            doc['source_refs']=[{'source_ref':'cyberalchemy-v2:CAV2-D55'}] if entry['definition_id']=='DEF-A' else []
            raw=json.dumps(doc).encode();path.write_bytes(raw);entry['sha256']=a.r.digest(raw)
        self.fixture.save_registry();self.snapshot=a.r.capture(self.root)
        self.paths=[]

    def write(self,path,doc):
        self.fixture.write(path,(json.dumps(doc) if not isinstance(doc,str) else doc).encode());self.paths.append(path)

    def report(self,**kwargs):return a.assess(self.snapshot,self.root,paths=self.paths,**kwargs)

    def row(self,report,identity='DEF-A'):return next(x for x in report['current_queue'] if x['definition_id']==identity)

    def fault(self,code,callback):self.fixture.fault(code,callback)

    def test_total_current_queue_and_historical_versions(self):
        report=self.report();self.assertEqual(2,len(report['current_queue']));self.assertEqual(1,len(report['historical_versions']))
        self.assertEqual('DEF-A@1.0.0',report['historical_versions'][0]['version_ref'])
        self.assertEqual(3,report['counts']['admitted_versions']);self.assertEqual(2,report['counts']['source_formal_expressions'])
        self.assertEqual('unassigned',self.row(report)['definition_form_status'])
        self.assertEqual('PASS',a.validate_coverage(self.snapshot,report)['result'])

    def test_plain_id_mentions_never_become_proofs(self):
        self.write('craft/formalization/fake.lean','-- DEF-A\ntheorem fake : True := by trivial')
        row=self.row(self.report());self.assertEqual(1,len(row['direct_identity_leads']))
        self.assertEqual([],row['verified_whole_definition_proofs']);self.assertEqual('not-established',row['whole_definition_assurance'])

    def test_structured_pass_profile_admission_and_digest_not_proof(self):
        e=self.snapshot['current_entries'][0]
        self.write('craft/formalization/self-assertion.json',{'definition_id':'DEF-A','version_ref':e['version_ref'],'sha256':e['sha256'],'result':'PASS','status':'owner-admitted','source_fidelity':'accepted','provider':'lean'})
        report=self.report();self.assertTrue(self.row(report)['direct_identity_leads'])
        self.assertEqual(0,report['counts']['verified_whole_definition_proofs']);self.assertEqual('owner-review-pending',self.row(report)['source_fidelity'])

    def test_indirect_origin_mapping_is_lead_not_identity_equality(self):
        self.write('craft/formalization/vocabulary.json',{'definition_id':'DSF-D01','source_definition_refs':['CAV2-D55']})
        row=self.row(self.report());self.assertEqual([],row['direct_identity_leads']);self.assertEqual(1,len(row['indirect_origin_leads']))
        self.assertEqual(['CAV2-D55'],row['origin_vocabulary_ids']);self.assertEqual([],row['candidate_bindings'])

    def test_no_fuzzy_term_or_prefix_join(self):
        self.write('craft/formalization/names.json',{'term':'Alpha','similar_id':'DEF-A-extra','similar_origin':'CAV2-D550'})
        row=self.row(self.report());self.assertEqual([],row['direct_identity_leads']);self.assertEqual([],row['indirect_origin_leads'])

    def test_source_drift_reports_unresolved_for_every_row(self):
        file=self.root/self.snapshot['current_entries'][0]['path'];file.write_bytes(file.read_bytes()+b' ')
        report=self.report();self.assertEqual('source-currentness-unresolved',report['status'])
        self.assertTrue(all(x['source_currentness']['status']=='unresolved' for x in report['current_queue']+report['historical_versions']))
        self.assertEqual(3,report['counts']['admitted_versions'])

    def test_corrupt_snapshot_fails_instead_of_fabricating_rows(self):
        self.snapshot['counts']['current_identities']=183
        self.fault('inconsistent-snapshot-bindings',self.report)

    def test_expected_denominator_required(self):
        self.fault('unexpected-source-denominator',lambda:self.report(expected_counts=(183,189)))

    def test_missing_duplicate_and_forged_source_rows_rejected(self):
        report=self.report()
        for mutate,code in [(lambda x:x['current_queue'].pop(),'coverage-denominator-mismatch'),(lambda x:x['current_queue'].__setitem__(1,copy.deepcopy(x['current_queue'][0])),'coverage-denominator-mismatch'),(lambda x:x['historical_versions'][0].update(sha256='0'*64),'coverage-source-binding-mismatch'),(lambda x:x['counts'].update(admitted_versions=189),'coverage-denominator-mismatch')]:
            with self.subTest(code=code):
                changed=copy.deepcopy(report);mutate(changed);self.fault(code,lambda:a.validate_coverage(self.snapshot,changed))

    def test_boolean_and_float_cannot_impersonate_exact_coverage_counts(self):
        report=self.report()
        for key,value in [('historical_versions',True),('admitted_versions',3.0)]:
            changed=copy.deepcopy(report);changed['counts'][key]=value
            self.fault('malformed-coverage-count',lambda:a.validate_coverage(self.snapshot,changed))


    def test_self_promoted_whole_assurance_owner_acceptance_and_authority_rejected(self):
        report=self.report()
        for mutate in [lambda x:x.update(authority_effect='admitted'),lambda x:x['counts'].update(verified_whole_definition_proofs=1),lambda x:x['current_queue'][0].update(whole_definition_assurance='PASS'),lambda x:x['current_queue'][0].update(source_fidelity='accepted'),lambda x:x['current_queue'][0].update(verified_whole_definition_proofs=['fake'])]:
            changed=copy.deepcopy(report);mutate(changed);self.fault('unjustified-coverage-claim',lambda:a.validate_coverage(self.snapshot,changed))

    def test_malformed_artifact_not_silently_omitted(self):
        path='craft/formalization/broken.json';self.fixture.write(path,b'{"result":"PASS","result":"FAIL"}');self.paths.append(path)
        report=self.report();self.assertEqual(1,len(report['inspected_artifacts']));self.assertEqual('uninspectable',report['inspected_artifacts'][0]['status'])
        self.assertEqual('malformed-source-json',report['inspected_artifacts'][0]['error'])

    def test_exact_candidate_partial_bindings_stale_versions_and_selectors(self):
        e=self.snapshot['current_entries'][0]
        dep={'source_path':e['path'],'source_sha256':e['sha256'],'version_ref':e['version_ref'],'selectors':['/voices/scientific_formal/normative_statement']}
        path=a.PILOT+'interpretation.json'
        self.fixture.write(path,json.dumps({'dependencies':{'DEF-A':dep}}).encode())
        report=self.report();binding=self.row(report)['candidate_bindings'][0];self.assertEqual('exact-source-bound',binding['status']);self.assertEqual('selected clauses only',binding['coverage'])
        self.assertEqual(1,report['counts']['source_bound_partial_pilot_translations']);self.assertEqual(0,report['counts']['verified_whole_definition_proofs'])
        historical=report['historical_versions'][0];self.assertEqual('stale-or-unbound',historical['candidate_bindings'][0]['status'])
        dep['selectors']=['/missing'];self.fixture.write(path,json.dumps({'dependencies':{'DEF-A':dep}}).encode())
        self.assertEqual('stale-or-unbound',self.row(self.report())['candidate_bindings'][0]['status'])

    def test_foundation_exact_excerpt_required_and_priority_kept(self):
        e=self.snapshot['current_entries'][0];text='A thing has a property.'
        annotation={'definition_id':'DEF-A','source_ref':e['version_ref'],'selector':'/voices/scientific_formal/normative_statement','excerpt':text,'start_character':0,'excerpt_sha256':a.r.digest(text.encode()),'definitional_forms':['genus-differentia'],'statement_roles':['definition']}
        doc={'source_bindings':[{k:e[k] for k in ['definition_id','version_ref','path','sha256']}],'source_clause_annotations':[annotation]};path=a.DATA+'foundations/definition-kinds.json'
        self.fixture.write(path,json.dumps(doc).encode());report=self.report()
        self.assertEqual('selected-clause-candidate',self.row(report)['definition_form_status']);self.assertEqual('DEF-A',report['current_queue'][0]['definition_id'])
        annotation['excerpt']='Invented';annotation['excerpt_sha256']=a.r.digest(b'Invented');self.fixture.write(path,json.dumps(doc).encode())
        report=self.report();self.assertEqual('unassigned',self.row(report)['definition_form_status']);self.assertEqual('stale-or-unbound',self.row(report)['candidate_bindings'][0]['status'])

    def test_two_origin_successors_are_retained_without_merging(self):
        entries=copy.deepcopy(self.snapshot['current_entries']);docs=a.source_documents(self.snapshot)
        docs[entries[1]['version_ref']]['source_refs']=[{'source_ref':'cyberalchemy-v2:CAV2-D55'}]
        self.write('craft/formalization/vocabulary.json',{'source_definition_refs':['CAV2-D55']})
        _,direct,indirect=a.inventory(self.root,docs,entries,self.paths)
        self.assertEqual(1,len(indirect['DEF-A']));self.assertEqual(1,len(indirect['DEF-B']));self.assertEqual([],direct['DEF-A'])

    def test_create_only_publication_is_complete_and_preserves_previous(self):
        report=self.report();path=a.DATA+'fixture-coverage.json';a.publish_report(report,self.root,path)
        raw=(self.root/path).read_bytes();self.assertEqual(report,json.loads(raw))
        self.fault('output-already-exists',lambda:a.publish_report(report,self.root,path));self.assertEqual(raw,(self.root/path).read_bytes())
        self.assertEqual([],list((self.root/path).parent.glob('.coverage-*.tmp')))


if __name__=='__main__':unittest.main()
