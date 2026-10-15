"""Changed leaf, SCC, deleted edge, exact-byte and real cache replay controls."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path[:0]=[str(HERE),str(HERE/'tests')]
import invalidation as i
import test_C03 as graph_fixture
import test_E03 as evidence_fixture

class InvalidationControls(unittest.TestCase):
    def setUp(self):
        self.fixture=graph_fixture.DependencyControls();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups);self.root=self.fixture.fixture.root;self.edges={('DEF-C','DEF-A'),('DEF-A','DEF-B')};self.roles={};self.last_selection=None
    def put(self,path,value,raw=None):
        raw=json.dumps(value,sort_keys=True).encode() if raw is None else raw;p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return {'path':path,'sha256':i.r.digest(raw)}
    def artifact(self,identity,role,value,format='json',raw=None):
        ref=self.put(f'candidate/{identity}-{role}.json' if format=='json' else f'candidate/{identity}-{role}.bin',value,raw);self.roles.setdefault(identity,{x:[] for x in i.ROLES})[role]=[{'ref':ref,'format':format}];return ref
    def capture(self,with_packets=True):
        snapshot=i.r.capture(self.root);refs={x['definition_id']:i.d.source_ref(x) for x in snapshot['current_entries']};packets={key:graph_fixture.draft.draft(ref,i.d.correspondence.source_document(snapshot,ref)) for key,ref in refs.items()}
        for left,right in sorted(self.edges):
            if left not in refs or right not in refs:continue
            packet=packets[left];ref=refs[right]
            if ref not in packet['interpretation']['depends_on']:packet['interpretation']['depends_on'].append(copy.deepcopy(ref))
            packet['dependency_links'].append({'kind':'semantic-use','clause_id':packet['interpretation']['clauses'][0]['clause_id'],'dependency_ref':copy.deepcopy(ref),'rationale':'Explicit synthetic I01 dependency control.'})
        packet_refs=[self.put(f'candidate/packet-{key}.json',value) for key,value in sorted(packets.items())] if with_packets else []
        selection={'snapshot_ref':self.put('candidate/snapshot.json',snapshot),'roots':[refs[key] for key in sorted(refs)],'packet_refs':packet_refs,'cycle_policies':[],'required_edges':[{'from_source':refs[a],'to_source':refs[b]} for a,b in sorted(self.edges) if a in refs and b in refs] if with_packets else [],'bindings':[{'definition_id':key,'artifacts':copy.deepcopy(self.roles.get(key,{role:[] for role in i.ROLES}))} for key in sorted(refs)]};self.last_selection=selection;return i.capture_epoch(self.root,selection)
    def source(self,identity,format_only=False):
        f=self.fixture.fixture;version=f.registry['current_lookup'][identity];entry=next(x for x in f.entries if x['definition_id']+'@'+x['version']==version);path=self.root/entry['path'];value=json.loads(path.read_bytes())
        if not format_only:value['voices']['scientific_formal']['normative_statement']+=' An additional selected condition.'
        raw=json.dumps(value,indent=4).encode();path.write_bytes(raw);entry['sha256']=i.r.digest(raw);f.save_registry()
    def fault(self,code,callback):
        with self.assertRaises(i.InvalidationFault) as caught:callback()
        self.assertEqual(code,caught.exception.code)
    def test_unchanged_epoch_has_no_invalidated_nodes_and_no_automatic_acceptance(self):
        old=self.capture();new=self.capture();plan=i.compare_epochs(old,new);self.assertEqual([],plan['invalidated_current_definitions']);self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['unaffected_cache_candidates']);self.assertFalse(plan['global_regression_required']);self.assertFalse(plan['semantic_ready']);self.assertEqual('not-established',plan['semantic_closure'])
    def test_changed_leaf_invalidates_all_transitive_consumers(self):
        old=self.capture();self.source('DEF-B');plan=i.compare_epochs(old,self.capture());self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['invalidated_current_definitions']);self.assertTrue(plan['global_regression_required'])
    def test_changed_middle_preserves_unaffected_leaf_as_candidate_only(self):
        old=self.capture();self.source('DEF-A');plan=i.compare_epochs(old,self.capture());self.assertEqual(['DEF-A','DEF-C'],plan['invalidated_current_definitions']);self.assertEqual(['DEF-B'],plan['unaffected_cache_candidates'])
    def test_mutual_component_invalidates_peers_and_consumers(self):
        self.edges.add(('DEF-B','DEF-A'));old=self.capture();self.artifact('DEF-A','assumption',{'selected':True});plan=i.compare_epochs(old,self.capture());self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['invalidated_current_definitions']);self.assertIn(['DEF-A','DEF-B'],plan['propagation_components']);self.assertEqual('unresolved-cycle-classification',old['coverage']['cycle_reviews'][0]['disposition'])
    def test_removed_edge_cannot_hide_old_affected_consumers(self):
        old=self.capture();self.edges.remove(('DEF-A','DEF-B'));self.source('DEF-B');plan=i.compare_epochs(old,self.capture());self.assertIn(['DEF-A','DEF-B'],plan['propagation_edges']);self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['invalidated_current_definitions'])
    def test_added_dependency_invalidates_authored_consumer_and_its_dependants(self):
        self.edges={('DEF-C','DEF-A')};old=self.capture();self.edges.add(('DEF-A','DEF-B'));plan=i.compare_epochs(old,self.capture());self.assertEqual(['DEF-A','DEF-C'],plan['invalidated_current_definitions']);self.assertTrue(plan['global_regression_required'])
    def test_every_semantic_role_changes_propagate(self):
        for role in i.ROLES:
            with self.subTest(role=role):
                self.roles={};self.artifact('DEF-B',role,{'condition':'first'});old=self.capture();self.artifact('DEF-B',role,{'condition':'second'});plan=i.compare_epochs(old,self.capture());self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['invalidated_current_definitions']);self.assertTrue(any(role in x['changed_content_parts'] for x in plan['direct_deltas']))
    def test_json_representation_only_delta_still_requires_rebinding(self):
        self.artifact('DEF-B','assumption',{'P':True,'Q':1});old=self.capture();ref=self.artifact('DEF-B','assumption',None,raw=b'{\n "Q": 1, "P": true\n}');plan=i.compare_epochs(old,self.capture());delta=next(x for x in plan['direct_deltas'] if x['definition_id']=='DEF-B');self.assertEqual('representation-change',delta['delta']);self.assertEqual([],delta['changed_content_parts']);self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['invalidated_current_definitions'])
    def test_source_format_changes_are_not_ignored(self):
        old=self.capture(with_packets=False);self.source('DEF-B',True);plan=i.compare_epochs(old,self.capture(with_packets=False));delta=next(x for x in plan['direct_deltas'] if x['definition_id']=='DEF-B');self.assertEqual('representation-change',delta['delta']);self.assertTrue(plan['global_regression_required'])
    def test_opaque_tool_bytes_are_never_semantically_normalized(self):
        self.artifact('DEF-B','tool',None,'opaque',b'code\n');old=self.capture();self.artifact('DEF-B','tool',None,'opaque',b'code \n');plan=i.compare_epochs(old,self.capture());self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['invalidated_current_definitions']);self.assertTrue(any('tool' in x['changed_content_parts'] for x in plan['direct_deltas']))
    def test_boolean_integer_and_float_are_distinct_structural_values(self):
        self.artifact('DEF-B','assumption',{'value':True});old=self.capture()
        for value in [1,1.0]:
            self.artifact('DEF-B','assumption',{'value':value});plan=i.compare_epochs(old,self.capture());self.assertTrue(any('assumption' in x['changed_content_parts'] for x in plan['direct_deltas']))
    def test_new_definition_changes_global_denominator_without_inventing_edges(self):
        old=self.capture();f=self.fixture.fixture;row=copy.deepcopy(f.entries[-1]);row.update(definition_id='DEF-D',term='Delta',version='1.0.0',path='authority/definitions/DEF-D-1.0.0.json');raw=json.dumps({'definition_id':'DEF-D','term':'Delta','version':'1.0.0','voices':{'scientific_formal':{'normative_statement':'A new synthetic source.'}}}).encode();f.write(row['path'],raw);row['sha256']=i.r.digest(raw);f.entries.append(row);f.registry['current_lookup']['DEF-D']='DEF-D@1.0.0';f.save_registry();plan=i.compare_epochs(old,self.capture());self.assertTrue(plan['global_denominator_changed']);self.assertEqual(['DEF-D'],plan['invalidated_current_definitions']);self.assertTrue(plan['global_regression_required'])
    def test_deleted_definition_retains_prior_affected_closure(self):
        old=self.capture();f=self.fixture.fixture;f.entries[:]=[x for x in f.entries if x['definition_id']!='DEF-B'];del f.registry['current_lookup']['DEF-B'];f.save_registry();plan=i.compare_epochs(old,self.capture());self.assertTrue(plan['global_denominator_changed']);self.assertEqual(['DEF-B'],plan['affected_prior_only_definitions']);self.assertEqual(['DEF-A','DEF-C'],plan['invalidated_current_definitions'])
    def test_source_version_change_is_not_rebound_by_label(self):
        old=self.capture();f=self.fixture.fixture;row=copy.deepcopy(next(x for x in f.entries if x['definition_id']=='DEF-B'));row.update(version='2.0.0',path='authority/definitions/DEF-B-2.0.0.json');value=json.loads((self.root/'authority/definitions/DEF-B-1.0.0.json').read_bytes());value['version']='2.0.0';raw=json.dumps(value).encode();f.write(row['path'],raw);row['sha256']=i.r.digest(raw);f.entries.append(row);f.registry['current_lookup']['DEF-B']='DEF-B@2.0.0';f.save_registry();plan=i.compare_epochs(old,self.capture());self.assertTrue(plan['global_denominator_changed']);self.assertEqual(['DEF-A','DEF-B','DEF-C'],plan['invalidated_current_definitions'])
    def test_rehashed_graph_and_node_forgery_rejected_by_regeneration(self):
        old=self.capture()
        for change in [lambda x:x['graph_projection']['edges'].clear(),lambda x:x['nodes'][0].update(content_fingerprint='0'*64),lambda x:x['coverage'].update(semantic_closure='established')]:
            bad=copy.deepcopy(old);change(bad);bad['epoch_sha256']=i.digest({k:v for k,v in bad.items() if k!='epoch_sha256'});self.fault('epoch-integrity-or-build-substitution',lambda:i.validate_epoch(bad))
    def test_missing_captured_input_or_role_node_never_silently_skipped(self):
        old=self.capture();bad=copy.deepcopy(old);bad['captured_artifacts'].pop();self.fault('captured-artifact-denominator-mismatch',lambda:i.validate_epoch(bad));selection=copy.deepcopy(self.last_selection);selection['bindings'].pop();self.fault('role-binding-node-denominator-mismatch',lambda:i.capture_epoch(self.root,selection))
    def test_stale_artifact_and_post_capture_race_have_no_epoch(self):
        ref=self.artifact('DEF-B','assumption',{'P':True});self.capture();selection=copy.deepcopy(self.last_selection);(self.root/ref['path']).write_bytes(b'{}');self.fault('captured-artifact-byte-substitution',lambda:i.capture_epoch(self.root,selection));self.artifact('DEF-B','assumption',{'P':True});self.capture();selection=copy.deepcopy(self.last_selection);self.fault('stale-live-epoch-artifact',lambda:i.capture_epoch(self.root,selection,before_final_check=lambda:(self.root/ref['path']).write_bytes(b'{}')))
    def test_source_race_after_capture_rejects_live_epoch(self):
        old=self.capture();selection=copy.deepcopy(self.last_selection)
        with self.assertRaises(i.r.CaptureFault):i.capture_epoch(self.root,selection,before_final_check=lambda:self.source('DEF-B'))
    def test_engine_drift_and_corrupt_capture_remain_rejected(self):
        old=self.capture();bad=copy.deepcopy(old);bad['engine_bindings'][0]['sha256']='0'*64;self.fault('epoch-integrity-or-build-substitution',lambda:i.validate_epoch(bad));bad=copy.deepcopy(old);bad['captured_artifacts'][0]['content_base64']='!';self.fault('malformed-captured-bytes',lambda:i.validate_epoch(bad))
    def test_ambiguous_artifact_format_and_unsafe_refs_are_rejected(self):
        self.capture();selection=copy.deepcopy(self.last_selection);selection['bindings'][0]['artifacts']['tool']=[{'ref':selection['snapshot_ref'],'format':'opaque'}];self.fault('ambiguous-artifact-binding',lambda:i.capture_epoch(self.root,selection));selection=copy.deepcopy(self.last_selection);selection['snapshot_ref']['path']='../outside.json'
        with self.assertRaises(i.r.CaptureFault):i.capture_epoch(self.root,selection)
    def test_capture_resource_limits_have_explicit_nonsemantic_failures(self):
        self.capture();selection=copy.deepcopy(self.last_selection)
        with patch.object(i,'MAX_ARTIFACTS',1):self.fault('artifact-count-limit',lambda:i.capture_epoch(self.root,selection))
        with patch.object(i,'MAX_CAPTURE_BYTES',1):self.fault('capture-total-byte-limit',lambda:i.capture_epoch(self.root,selection))
        with patch.object(i,'MAX_EPOCH_BYTES',1):self.fault('epoch-byte-limit',lambda:i.capture_epoch(self.root,selection))
    def test_selected_epoch_ref_cannot_be_rehashed_or_symlinked(self):
        value=self.capture();ref=self.put('candidate/epoch.json',value);self.assertEqual(value,i.read_epoch(self.root,ref));bad=copy.deepcopy(ref);bad['sha256']='0'*64;self.fault('stale-selected-epoch',lambda:i.read_epoch(self.root,bad));(self.root/'candidate/link.json').symlink_to(self.root/ref['path'])
        with self.assertRaises(OSError):i.read_epoch(self.root,{'path':'candidate/link.json','sha256':ref['sha256']})

class CacheControls(unittest.TestCase):
    def setUp(self):
        self.fixture,self.bundle,self.required,self.put,self.verification_selection=evidence_fixture.setup_selection();self.addCleanup(self.fixture.doCleanups);self.root=self.fixture.root
        sources=self.bundle['sources'];selection={'snapshot_ref':self.bundle['snapshot_ref'],'roots':sources,'packet_refs':[],'cycle_policies':[],'required_edges':[],'bindings':[{'definition_id':x['definition_id'],'artifacts':{role:[] for role in i.ROLES}} for x in sources]};self.epoch=i.capture_epoch(self.root,selection);self.old_ref=self.put('candidate/old-epoch.json',self.epoch);self.new_ref=self.put('candidate/current-epoch.json',self.epoch);published=evidence_fixture.v.b.publish(self.root,self.bundle,self.required,evidence_fixture.v.b.BASE+'/units/I01/controlled');self.assertEqual('published-candidate',published['status']);self.bundle_path=published['bundle_ref'];manifest_path=self.bundle_path+'/manifest.json';self.entry={'cache_id':'cache:synthetic-current','definition_ids':sorted(x['definition_id'] for x in sources),'bundle_manifest_ref':{'path':manifest_path,'sha256':i.r.digest((self.root/manifest_path).read_bytes())},'verification_selection_ref':self.put('candidate/verification-selection.json',self.verification_selection)}
    def check(self,entries=None,**kw):return i.check_cache(self.root,self.old_ref,self.new_ref,[self.entry] if entries is None else entries,**kw)
    def test_unchanged_cache_is_rehashed_replayed_and_keeps_all_pending_gates(self):
        out=self.check();self.assertEqual('cache-check-completed',out['status']);entry=out['entries'][0];self.assertEqual('freshly-checked-candidate-cache',entry['status']);self.assertFalse(out['semantic_ready']);self.assertEqual('not-accepted',out['owner_fidelity']);self.assertEqual(5,len(entry['verification']['pending_logical']));self.assertEqual(6,len(entry['verification']['pending_gates']))
    def test_altered_epoch_reference_is_unresolved_without_cache_support(self):
        self.new_ref['sha256']='0'*64;out=self.check();self.assertEqual('cache-check-unresolved',out['status']);self.assertEqual([],out['entries']);self.assertEqual('stale-selected-epoch',out['diagnostics'][0]['code'])
    def test_malformed_duplicate_and_empty_definition_cache_inputs_do_not_escape(self):
        for entries in [None,{},[self.entry,self.entry],[{**self.entry,'definition_ids':[]}],[{**self.entry,'ignored':True}]]:
            out=i.check_cache(self.root,self.old_ref,self.new_ref,entries);self.assertEqual('cache-check-unresolved',out['status']);self.assertEqual([],out['entries'])
    def test_changed_definition_never_uses_cached_verification(self):
        raw=b'{"selected":true}';path='candidate/new-assumption.json';ref=self.put(path,json.loads(raw));selection=copy.deepcopy(self.epoch['selection']);selection['bindings'][0]['artifacts']['assumption']=[{'ref':ref,'format':'json'}];new=i.capture_epoch(self.root,selection);self.new_ref=self.put('candidate/new-current-epoch.json',new)
        with patch.object(evidence_fixture.v,'verify',side_effect=AssertionError('invalidated evidence must not replay')):out=self.check()
        self.assertEqual('cache-check-completed',out['status']);self.assertEqual('invalidated-cache',out['entries'][0]['status'])
    def test_unchanged_reference_does_not_hide_corrupt_published_objects(self):
        obj=next((self.root/self.bundle_path/'objects').iterdir());obj.write_bytes(obj.read_bytes()+b' ');out=self.check();self.assertEqual('cache-check-completed',out['status']);self.assertEqual('cache-verification-failed',out['entries'][0]['status'])
    def test_incomplete_cache_source_denominator_rejected(self):
        self.entry['definition_ids']=self.entry['definition_ids'][:1];out=self.check();self.assertEqual('cache-check-unresolved',out['status']);self.assertEqual('cache-source-denominator-substitution',out['diagnostics'][0]['code'])
    def test_selected_input_race_after_verification_clears_all_support(self):
        ref=self.verification_selection['relation_requests_ref'];out=self.check(before_final_check=lambda:(self.root/ref['path']).write_bytes(b'[]'));self.assertEqual('cache-check-unresolved',out['status']);self.assertEqual([],out['entries']);self.assertEqual('cache-input-changed-during-check',out['diagnostics'][0]['code'])
    def test_published_object_race_after_verification_clears_all_support(self):
        obj=next((self.root/self.bundle_path/'objects').iterdir());out=self.check(before_final_check=lambda:obj.write_bytes(obj.read_bytes()+b' '));self.assertEqual('cache-check-unresolved',out['status']);self.assertEqual([],out['entries']);self.assertEqual('cache-input-changed-during-check',out['diagnostics'][0]['code'])
    def test_epoch_race_after_verification_clears_all_support(self):
        out=self.check(before_final_check=lambda:(self.root/self.new_ref['path']).write_bytes(b'{}'));self.assertEqual('cache-check-unresolved',out['status']);self.assertEqual([],out['entries']);self.assertEqual('epoch-changed-during-cache-check',out['diagnostics'][0]['code'])

if __name__=='__main__':unittest.main()
