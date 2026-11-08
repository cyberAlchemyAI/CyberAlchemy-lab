"""Selected historical bytes and synthetic mutations; no native/role execution."""
import copy
import hashlib
import json
from pathlib import Path
import re
import traceback
import unittest

from t35_external_v1.phase_scoped_v2 import mapper_package_validators_0004 as v

ROOT=Path(__file__).resolve().parents[6]
PACKAGE=ROOT/'product/lab/release-candidates/v1/interface/legacy-session-fixture-mapped-v2-action-0148/packages/0001'
INSTALL=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files={name:(PACKAGE/name).read_bytes() for name in sorted(v.package_names())}
        inventory=[[name,len(raw),v.sha(raw)] for name,raw in sorted(cls.files.items())]
        raw=(json.dumps(inventory,separators=(',',':'),ensure_ascii=True)+'\n').encode()
        if v.sha(raw)!='e38101f67689dc56ba23815a6d6017125bbb391e64757dff643c52876095b4d6':
            raise RuntimeError('HISTORICAL_INVENTORY_DRIFT')
        cls.sem=[cls.files[f'semantic/{i:08d}.json'] for i in range(1,26)]
        cls.gov=[cls.files[f'governance/{i:08d}.json'] for i in range(1,26)]
        cls.mapping=json.loads(cls.files['mapping.json'])
        cls.basis=v.encoded({k:cls.mapping[k] for k in v.MAPPING_BASIS_FIELDS})
        cls.originals={'native':(INSTALL/'bin/lab-context-native-reader').read_bytes(),
                       'loader':(INSTALL/'lib/abi/ld-linux-x86-64.so.2').read_bytes(),
                       'libgcc':(INSTALL/'lib/abi/libgcc_s.so.1').read_bytes(),
                       'libc':(INSTALL/'lib/abi/libc.so.6').read_bytes(),
                       'bwrap':Path('/usr/bin/bwrap').read_bytes()}
        cls.launch_basis={'schema_version':'lab-mapper-native-launch-basis/v1','files':{}}
        cls.observed={}
        for index,role in enumerate(v.NATIVE_ROLES,1):
            source='native' if role=='snapshot' else role;data=cls.originals[source]
            identity={'device':1,'inode':index,'mount_id':2,'uid':1000,'gid':1000,
                      'mode':0o400 if role=='snapshot' else 0o644 if role in ('libgcc','libc') else 0o755,
                      'nlink':1,'size_bytes':len(data),'kind':'regular','locator':'/owned/'+role}
            cls.launch_basis['files'][role]={'sha256':v.sha(data),'size_bytes':len(data),
                                           'origin':{'path':'selected/'+source,'sha256':v.sha(data)},'identity':identity}
            cls.observed[role]={'identity':copy.deepcopy(identity),'bytes':data}
        cls.launch_raw=v.encoded(cls.launch_basis)

    def cold(self, first=None, second=None, sem=None, gov=None, request=None):
        raw=self.files['native-output.json'] if first is None else first
        return v.validate_cold(raw,raw if second is None else second,semantic_raw=self.sem if sem is None else sem,
                               governance_raw=self.gov if gov is None else gov,
                               request_raw=self.files['request.json'] if request is None else request)

    def mapping_check(self, raw=None, basis=None, pin=None):
        basis=self.basis if basis is None else basis
        return v.validate_mapping(self.files['mapping.json'] if raw is None else raw,basis_raw=basis,
                                   expected_basis_sha256=v.sha(basis) if pin is None else pin,
                                   semantic_raw=self.sem,governance_raw=self.gov)

    def native_check(self, observed=None, raw=None, pin=None, index=0, phase='before'):
        raw=self.launch_raw if raw is None else raw
        return v.validate_native_basis(raw,expected_basis_sha256=v.sha(raw) if pin is None else pin,
                                       originals=self.originals,observed=self.observed if observed is None else observed,
                                       launch_index=index,phase=phase)

    def test_all50_actual_standalone_events_and_entire_actual_cold_output(self):
        sem,gov=v.validate_events(self.sem,self.gov)
        self.assertEqual(len(sem),25);self.assertEqual(len(gov),25)
        result=self.cold();self.assertFalse(result['fresh_runtime_qualified'])
        self.assertEqual(result['stdout_sha256'],'669b5eced4988dbe4fdf562ab82ad605ce671cd37490ec75251e94f06c680177')
        self.assertEqual(len(self.files['native-output.json']),221942)

    def test_closed_native_struct_field_order_matches_pinned_rust_source(self):
        raw=(ROOT/'ontology-lifecycle/runtime/src/lib.rs').read_bytes()
        self.assertEqual(v.sha(raw),'f1b3f7cf463ebcc6e7b887b374d75adeac29ba38acfec3bafacfe4d3159f3a7b')
        schemas={'OntologySubjectIdentity':v.IDENTITY,'DefinitionReference':v.DEFINITION,'SemanticComponent':v.COMPONENT,
                 'TypedPropertySet':v.PROPERTY,'UseObligation':v.OBLIGATION,'ForbiddenCollapse':v.COLLAPSE,
                 'OntologyNodeSemanticState':v.NODE,'OntologyRelationSemanticState':v.RELATION,'SemanticEvent':v.SEMANTIC,
                 'ExactSemanticEventReference':v.SEMREF,'ProvenanceEntry':v.PROVENANCE,'AuthorityKindAndPosture':v.AUTHORITY,
                 'ConfidenceReference':v.CONFIDENCE,'EdgeReference':v.EDGE,'ChallengeContract':v.CHALLENGE,'TypedResidue':v.RESIDUE,
                 'TypedConflict':v.CONFLICT,'OntologyGovernanceState':v.GOVSTATE,'GovernanceEvent':v.GOVERNANCE,
                 'ProjectionSubjectReference':v.REFERENCE,'ProjectedSubject':v.PROJECTED,'ConsistentOntologyCut':v.CUT,
                 'ContextSelector':v.SELECTOR,'ContextProjection':v.CONTEXT,'GovernedOntologyNodeView':v.VIEW}
        for name,schema in schemas.items():
            body=re.search(r'pub struct '+name+r' \{(.*?)\n\}',raw.decode(),re.S).group(1)
            keys=re.findall(r'^\s*pub (?:r#)?([a-z_][a-z0-9_]*):',body,re.M)
            self.assertEqual([key for key,_ in schema],keys,name)

    def test_seal_real_event_bytes_only_digest_change_and_governance_join(self):
        for family,events,schema in [('semantic',self.sem,v.SEMANTIC),('governance',self.gov,v.GOVERNANCE)]:
            sealed=[json.loads(raw) for raw in events];inputs=copy.deepcopy(sealed)
            for x in inputs:x['event_digest']=v.ZERO
            body={'semantic':inputs if family=='semantic' else [],'governance':inputs if family=='governance' else []}
            original=v.encoded(body)
            # Reconstruct wrapper only; every selected actual standalone event span is retained.
            output=(b'{"semantic":['+(b','.join(x.rstrip(b'\n') for x in events) if family=='semantic' else b'')+
                    b'],"governance":['+(b','.join(x.rstrip(b'\n') for x in events) if family=='governance' else b'')+b']}\n')
            self.assertEqual(len(v.validate_seal(original,output,expected_input_sha256=v.sha(original),family=family,semantic_raw=self.sem)),25)
            changed=json.loads(output);changed[family][0]['event_id']='different'
            with self.assertRaises(v.Refusal):
                v.validate_seal(original,v.native_bytes(changed,v.FIXTURE),expected_input_sha256=v.sha(original),family=family,semantic_raw=self.sem)
            with self.assertRaises(v.Refusal):
                v.validate_seal(original+b' ',output,expected_input_sha256=v.sha(original),family=family,semantic_raw=self.sem)

    def test_event_unknown_fields_digest_cursor_identity_and_float_refuse(self):
        for change in ('unknown','digest','cursor','identity','float','map'):
            event=json.loads(self.sem[0])
            if change=='unknown':event['unknown']='PRIVATE_MARKER'
            elif change=='digest':event['event_digest']='1'*64
            elif change=='cursor':event['semantic_cursor']=True
            elif change=='identity':event['subject_identity']['subject_kind']='other'
            elif change=='float':event['complete_resulting_semantic_state']['typed_properties']['values']['number']=1.25
            else:event['complete_resulting_semantic_state']['typed_properties']['values']=[]
            raw=(json.dumps(event,ensure_ascii=False,separators=(',',':'))+'\n').encode()
            with self.subTest(change=change),self.assertRaises(v.Refusal):v.exact_event(raw,'semantic')

    def test_reordered_resealed_governance_and_relation_endpoint_refuse(self):
        with self.assertRaises(v.Refusal):v.validate_events(self.sem[::-1],self.gov)
        g=json.loads(self.gov[0]);g['semantic_ref']['semantic_cursor']=2;g['event_digest']=v.ZERO
        g['event_digest']=v.sha(v.native_bytes(g,v.GOVERNANCE));gov=[v.native_bytes(g,v.GOVERNANCE),*self.gov[1:]]
        with self.assertRaisesRegex(v.Refusal,'GOVERNANCE_JOIN'):v.validate_events(self.sem,gov)
        s=json.loads(self.sem[15]);s['complete_resulting_semantic_state']['source_node_id']='absent';s['event_digest']=v.ZERO
        s['event_digest']=v.sha(v.native_bytes(s,v.SEMANTIC));sem=[*self.sem[:15],v.native_bytes(s,v.SEMANTIC),*self.sem[16:]]
        with self.assertRaises(v.Refusal):v.validate_events(sem,self.gov)

    def test_every_cold_component_and_parity_is_checked(self):
        for component in ('cut','context','governance_event_refs','governed_nodes','authority_effect','unknown'):
            value=json.loads(self.files['native-output.json'])
            if component=='cut':value['cut']['subjects'].reverse()
            elif component=='context':value['context']['projection_body']['subjects'][0]['source_event_digest']='0'*64
            elif component=='governance_event_refs':value[component][0]='other'
            elif component=='governed_nodes':value[component][0]['calculated_view_digest']='0'*64
            elif component=='authority_effect':value[component]='publish'
            else:value['unknown']=1
            raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
            with self.subTest(component=component),self.assertRaises(v.Refusal):self.cold(raw)
        with self.assertRaisesRegex(v.Refusal,'COLD_PARITY'):self.cold(second=b'wrong')
        req=json.loads(self.files['request.json']);req['selector']['required_subject_set'].reverse()
        with self.assertRaises(v.Refusal):self.cold(request=v.encoded(req))

    def test_exact_mapping25rows582dispositions_and_external_basis(self):
        result=self.mapping_check();self.assertEqual((result['rows'],result['dispositions']),(25,582))
        self.assertFalse(result['source_custody_verified'])
        for field in ('rows','projection_dispositions'):
            changed=copy.deepcopy(self.mapping);changed[field].reverse()
            with self.assertRaises(v.Refusal):self.mapping_check(v.encoded(changed))
        basis=json.loads(self.basis);basis['source_name']='different'
        with self.assertRaisesRegex(v.Refusal,'SELECTION_DRIFT'):
            self.mapping_check(basis=v.encoded(basis),pin=v.sha(self.basis))

    def test_coherently_changed_mapping_basis_still_must_join_native_events(self):
        for change in ('record','endpoint','definition','qualifier','scopeflag'):
            value=copy.deepcopy(self.mapping)
            if change=='record':value['rows'][0]['artifact']['byte_sha256']='0'*64
            elif change=='endpoint':value['rows'][15]['source']['ref']='wrong'
            elif change=='definition':value['rows'][0]['definition_witnesses'][0]['selected_original_sha256']='0'*64
            elif change=='qualifier':value['rows'][15]['qualifiers']['extra']='no'
            else:value['projection_is_host_permission']=True
            basis=v.encoded({k:value[k] for k in v.MAPPING_BASIS_FIELDS})
            with self.subTest(change=change),self.assertRaises(v.Refusal):self.mapping_check(v.encoded(value),basis=basis)

    def test_actual_result_and_selected_duration_source_bounds(self):
        result=json.loads(self.files['build-result.json']);duration=result['duration_seconds']
        self.assertLess(duration,180)
        def check(raw):return v.validate_result(raw,source_sha256=result['source_sha256'],observed_duration_seconds=duration,maximum_duration_seconds=180)
        self.assertFalse(check(self.files['build-result.json'])['timing_independently_measured'])
        for key,new in [('node_count',14),('task_complete',True),('source_sha256','0'*64),('duration_seconds',duration+1)]:
            changed=dict(result);changed[key]=new
            with self.assertRaises(v.Refusal):check(v.encoded(changed))
        with self.assertRaises(v.Refusal):
            v.validate_result(self.files['build-result.json'],source_sha256=result['source_sha256'],observed_duration_seconds=float('inf'),maximum_duration_seconds=180)

    def test_actual_manifest_full54rows_and55files_no_selfcycle(self):
        manifest=json.loads(self.files['manifest.json']);prefix=manifest['files'][0]['path'].rsplit('/',1)[0]
        self.assertTrue(prefix.endswith('/packages/0001'))
        def check(files,raw=None):return v.validate_manifest(files['manifest.json'] if raw is None else raw,
            package_files=files,package_path=prefix,source_manifest_binding=manifest['source_manifest_binding'])
        self.assertEqual(check(self.files)['manifest_rows'],54)
        for mutation in ('omit','extra','bytes','order','self'):
            files=dict(self.files);changed=copy.deepcopy(manifest)
            if mutation=='omit':del files['request.json']
            elif mutation=='extra':files['../foreign']=b'x'
            elif mutation=='bytes':files['request.json']+=b' '
            elif mutation=='order':changed['files'].reverse();files['manifest.json']=v.encoded(changed)
            else:changed['files'].append({'path':prefix+'/manifest.json','sha256':v.sha(files['manifest.json'])});files['manifest.json']=v.encoded(changed)
            with self.subTest(mutation=mutation),self.assertRaises(v.Refusal):check(files)

    def test_native_selected_bytes_all_four_prepost_observations_are_inert(self):
        for index in range(4):
            for phase in ('before','after'):
                result=self.native_check(index=index,phase=phase)
                self.assertTrue(result['observed_bytes_equal'])
                self.assertFalse(result['kernel_identity_verified']);self.assertFalse(result['executed_image_verified'])

    def test_each_native_abi_snapshot_drift_and_identity_substitution_refuse(self):
        for role in v.NATIVE_ROLES:
            for kind in ('bytes','inode','mount','symlink'):
                observations=copy.deepcopy(self.observed)
                if kind=='bytes':
                    raw=observations[role]['bytes'];observations[role]['bytes']=bytes([raw[0]^1])+raw[1:]
                elif kind=='inode':observations[role]['identity']['inode']+=1
                elif kind=='mount':observations[role]['identity']['mount_id']+=1
                else:observations[role]['identity']['kind']='symlink'
                with self.subTest(role=role,kind=kind),self.assertRaises(v.Refusal):self.native_check(observations)
        changed=copy.deepcopy(self.launch_basis);changed['files']['native']['sha256']='0'*64
        with self.assertRaisesRegex(v.Refusal,'SELECTION_DRIFT'):self.native_check(raw=v.encoded(changed),pin=v.sha(self.launch_raw))
        for index in (True,-1,4):
            with self.assertRaises(v.Refusal):self.native_check(index=index)

    def test_unicode_escape_and_integer_codec_without_sorted_struct_rewriting(self):
        event=json.loads(self.sem[0]);event['event_id']='semantic:combining-e\u0301-\U0001f30d-"-\\-\n'
        event['semantic_cursor']=2**64-1;event['event_digest']=v.ZERO
        raw=v.native_bytes(event,v.SEMANTIC);self.assertIn('e\u0301-\U0001f30d'.encode(),raw)
        event['event_digest']=v.sha(raw);sealed=v.native_bytes(event,v.SEMANTIC)
        self.assertEqual(v.exact_event(sealed,'semantic'),event)
        self.assertEqual(v.zero_root_digest(sealed,'event_digest'),raw)
        sorted_raw=(json.dumps(event,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n').encode()
        with self.assertRaisesRegex(v.Refusal,'EVENT_NONCANONICAL'):v.exact_event(sorted_raw,'semantic')

    def test_malformed_private_errors_are_bounded_and_no_effect_api(self):
        for raw in (b'{"PRIVATE_MARKER":NaN}',b'{"a":1,"a":2}',b'['*65+b'0'+b']'*65,b'{"x":1e309}',b'\xff'):
            try:v.validate_cold(raw,raw,semantic_raw=self.sem,governance_raw=self.gov,request_raw=self.files['request.json'])
            except v.Refusal:
                self.assertNotIn('PRIVATE_MARKER',traceback.format_exc().split('Refusal:')[-1])
            else:self.fail('invalid JSON accepted')
        for name in ('os','subprocess','socket','open','run_native_checked','serve','publish'):
            self.assertFalse(hasattr(v,name))


if __name__=='__main__':unittest.main()
