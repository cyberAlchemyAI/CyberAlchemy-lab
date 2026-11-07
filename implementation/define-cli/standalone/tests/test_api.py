import base64
import copy
import json
from jsonschema import Draft202012Validator
from define_core import call
from define_core.contracts import SCHEMAS
from define_core.exact import binding, decode, encode, sha
from define_core.prepare import local_ref
from support import Case, add_source, b64, base, external_application, materialization, no_sources, raw_members, refresh


class Workflow(Case):
    def test_capabilities_have_no_lab_or_caller_paths(self):
        d = self.ok(self.invoke('capabilities'))
        self.assertFalse(d['lab_required']);self.assertFalse(d['caller_filesystem_access']);self.assertFalse(d['network_access'])
        self.assertEqual(len(d['operations']), 8)

    def test_every_advertised_schema_is_valid(self):
        for name in self.ok(self.invoke('capabilities'))['schemas']:
            with self.subTest(name=name):Draft202012Validator.check_schema(self.ok(self.invoke('schema', {'kind': name}))['schema'])

    def test_closed_pack_binds_account_filters_and_expected_rows(self):
        d = self.package();p = d['pack'];check = p['applications'][0]
        self.assertEqual(set(check['bindings']), {'S', 'A', 'F', 'E'})
        self.assertEqual(check['bindings']['A'], 'acme');self.assertEqual(check['bindings']['F']['region'], 'BR')
        self.assertEqual(p['status'], 'candidate');self.assertEqual(len(p['working_meanings']), 1)
        self.assertEqual(d['report']['assessment_execution_count'], 0)

    def test_exact_inspection_and_reconstruction(self):
        d = self.package();m = d['package_members']
        self.assertEqual(self.ok(self.invoke('inspect', {'package_members': m}))['pack_sha256'], d['pack_sha256'])
        self.assertEqual(self.ok(self.invoke('reconstruct', {'package_members': m}))['package_members'], m)

    def test_preparation_is_deterministic_for_exact_inputs(self):
        r, i = base();c = self.captured(r, i)
        self.assertEqual(self.ok(self.prepared(r, i, c)), self.ok(self.prepared(r, i, c)))

    def test_original_request_whitespace_is_preserved(self):
        r, i = base();text = json.dumps(r, indent=3)+'\n\n'
        c = self.ok(self.invoke('capture', {'request_utf8': text, 'inputs': b64(i)}))
        d = self.ok(self.invoke('prepare', {'request_utf8': text, 'capture_utf8': c['capture_utf8'], 'inputs': c['inputs']}))
        self.assertEqual(raw_members(d['package_members'])['request.json'], text.encode())

    def test_empty_source_proposal_needs_no_registry(self):
        r, i = no_sources();d = self.package(r, i)
        self.assertEqual(len(d['pack']['working_meanings']), 1)
        self.assertFalse(d['pack']['source_bindings'])

    def test_open_question_only(self):
        r, i = no_sources();r['handling'][0] = {'concept_id': r['required_concepts'][0]['concept_id'], 'disposition': 'open',
             'payload': {'question': 'What is complete?', 'reason': 'Unknown boundary', 'affected_use': 'apply-parameters', 'owner_route': None, 'continuation': 'Ask the meaning owner.'}}
        d = self.package(r, i);self.assertFalse(d['pack']['working_meanings'])
        self.assertTrue(any(g['reason'] == 'Unknown boundary' for g in d['pack']['gaps']))

    def test_local_reuse_remains_unverified(self):
        d = self.package()
        self.assertTrue(any(g['gap_id'].startswith('source-standing:') for g in d['pack']['gaps']))
        self.assertEqual(d['pack']['readiness']['governing-application']['outcome'], 'blocked')

    def test_external_explicit_parameters_are_supported(self):
        r, i = external_application();d = self.package(r, i)
        self.assertEqual(d['report']['application_checks'][0]['meaning_standing'], 'local-reference')
        self.assertEqual(d['pack']['parameter_contracts'][0]['contract_id'], 'parameters:example:export-complete@1')

    def test_values_do_not_create_shared_definitions(self):
        d = self.package()
        self.assertEqual(len(d['pack']['working_meanings']), 1);self.assertEqual(len(d['pack']['applications']), 1)
        self.assertFalse(d['pack']['materialization_selection'])

    def test_reported_fail_is_preserved_not_executed(self):
        d = self.package();self.assertEqual(d['pack']['assessments'][0]['reported_result'], 'FAIL')
        self.assertEqual(d['pack']['assessments'][0]['producer']['execution_posture'], 'synthetic')
        self.assertEqual(d['pack']['readiness']['consume-assessment']['outcome'], 'blocked')

    def test_missing_parameter_is_an_explicit_gap(self):
        r, i = base();a = r['applications'][0];a['bindings'].pop('A');a['value_provenance'] = [v for v in a['value_provenance'] if v['parameter'] != 'A']
        a['binding_gaps'] = [{'gap_id': 'parameter:A', 'reason': 'Unknown account', 'affected_use': 'apply-parameters', 'continuation': 'Select account'}]
        d = self.package(refresh(r), i);self.assertFalse(d['report']['application_checks'][0]['fully_bound'])
        self.assertEqual(d['pack']['readiness']['apply-parameters']['outcome'], 'blocked')

    def test_explicit_catalog_alias_and_reported_standing(self):
        r, i = base();r['handling'][0]['payload']['meaning_ref']['input_id'] = 'policy-alias'
        catalog = {'schema_version': 'define.source-catalog/v1', 'entries': [
            {'input_id': 'policy-alias' if path.startswith('investigation') else path, 'binding': binding(raw, path), 'reported_standing': 'Source claims approved'}
            for path, raw in i.items()], 'authority_effect': 'none'}
        c = self.captured(r, i, catalog_utf8=encode(catalog).decode());d = self.ok(self.prepared(r, i, c))
        self.assertEqual(d['pack']['status'], 'candidate')
        self.assertTrue(all(row['standing_observation']['status'] == 'local-reference' for row in c['capture']['input_rows']))

    def test_revision_lineage(self):
        r, i = base();old = self.package(r, i)
        old_raw = raw_members(old['package_members'])['pack.json'];add_source(r, i, 'predecessor.json', old_raw)
        r['predecessor_package_binding'] = binding(old_raw, 'predecessor.json');r['request_revision'] = 2;refresh(r)
        d = self.package(r, i);self.assertEqual(d['pack']['revision'], 2)
        self.assertEqual(d['pack']['lineage']['predecessor_package_binding']['sha256'], sha(old_raw))

    def test_unresolved_retention_is_reported(self):
        r, i = base();c = self.captured(r, i, permit_retention=False)
        d = self.ok(self.prepared(r, i, c));self.assertTrue(any(g['gap_id'].startswith('retention:') for g in d['pack']['gaps']))

    def test_materialization_is_explicit_and_candidate_only(self):
        r, i = materialization();d = self.package(r, i)
        m = self.ok(self.invoke('materialize', {'package_members': d['package_members']}))
        self.assertEqual(len(m['report']['definitions']), 1);self.assertIsNone(m['report']['actual_owner_outcome'])
        self.assertIn('definitions/000/DEFINITION.md', m['members'])
        self.assertEqual(m['report']['definitions'][0]['posture'], 'candidate-only')

    def test_materialization_is_deterministic(self):
        r, i = materialization();d = self.package(r, i)
        params = {'package_members': d['package_members']}
        self.assertEqual(self.ok(self.invoke('materialize', params)), self.ok(self.invoke('materialize', params)))

    def test_observation_missing_matching_drift_and_changed_use(self):
        d = self.package();members = raw_members(d['package_members']);capture = decode(members['capture.json'])
        current = members['inputs/'+capture['source_profile_binding']['path']]
        params = {'package_members': d['package_members'], 'consumer': 'reader', 'requested_use': 'inspect-preparation'}
        self.assertEqual(self.invoke('observe-use', params)['outcome'], 'not-evaluable')
        self.assertEqual(self.invoke('observe-use', {**params, 'current_source_base64': b64({'x': current})['x']})['outcome'], 'ready')
        self.assertEqual(self.invoke('observe-use', {**params, 'current_source_base64': b64({'x': b'{}'})['x']})['outcome'], 'blocked')
        self.assertEqual(self.invoke('observe-use', {**params, 'requested_use': 'governing-application'})['outcome'], 'blocked')
        self.assertEqual(self.ok(self.invoke('reconstruct', {'package_members': d['package_members']}))['package_members'], d['package_members'])


class InvalidInputs(Case):
    def test_unknown_api_and_operation(self):
        for doc in [ {'api_version':'unknown','id':'t','operation':'capabilities','params':{}},
                     {'api_version':'define.api/v1','id':'t','operation':'run-shell','params':{}} ]:
            with self.subTest(doc=doc):self.assertEqual(self.refused(call(doc))['outcome'], 'unsupported')

    def test_closed_envelope_and_params(self):
        self.refused(call({'api_version':'define.api/v1','id':'t','operation':'capabilities','params':{},'extra':True}))
        self.refused(self.invoke('capabilities', {'source_root':'/etc'}))

    def test_scalar_request_and_unsupported_request_version(self):
        for text in ('[]','null','"x"','{"schema_version":"cal.define.prepare-request/v2"}'):
            with self.subTest(text=text):self.refused(self.invoke('capture', {'request_utf8':text,'inputs':{}}))

    def test_unsafe_numbers_and_unicode(self):
        for value in (1.1, float('inf'), 2**60, '\ud800', '\x00'):
            with self.subTest(value=repr(value)):
                self.refused(call({'api_version':'define.api/v1','id':'t','operation':'capabilities','params':{'x':value}}))

    def test_bad_base64_and_paths(self):
        r,_ = no_sources()
        for inputs in ({'a':'a==='},{'a':'YQ'},{'a':'YR=='},{'../x':'eA=='},{'/x':'eA=='},{'a':'eA==','a/b':'eA=='},{'CON':'eA=='},{'a\\b':'eA=='}):
            with self.subTest(inputs=inputs):self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':inputs}))

    def test_extra_and_missing_input(self):
        r, i = base();extra = {**i,'unselected.json':b'{}'}
        self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':b64(extra)}),'unselected-input-member')
        i.pop(next(iter(i)));self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':b64(i)}),'source-unavailable')

    def test_changed_source_refuses_before_preparation(self):
        r,i = base();i[next(iter(i))] = b'{}'
        self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':b64(i)}),'binding-mismatch')

    def test_duplicate_and_incomplete_handling(self):
        for mutation in ('duplicate','missing'):
            r,i = base()
            if mutation=='duplicate':r['handling'].append(copy.deepcopy(r['handling'][0]))
            else:r['handling'].pop()
            self.refused(self.prepared(r,i))

    def test_admitted_and_live_capture_claims_refuse(self):
        r,i = base();c = self.captured(r,i)
        for mutation in ('standing','population','live','permission'):
            changed=copy.deepcopy(c);record=changed['capture']
            if mutation=='standing':record['input_rows'][0]['standing_observation']['status']='admitted-current'
            if mutation=='population':record['input_rows'][0]['population']='host-member'
            if mutation=='live':record['mode']='live-host'
            if mutation=='permission':record['permission_observation_binding']=record['source_profile_binding']
            changed['capture_utf8']=encode(record).decode()
            with self.subTest(mutation=mutation):self.refused(self.prepared(r,i,changed))

    def test_forbidden_retention_refuses(self):
        r,i=base();c=self.captured(r,i);c['capture']['input_rows'][0]['retention_posture']='forbidden';c['capture_utf8']=encode(c['capture']).decode()
        self.refused(self.prepared(r,i,c),'retention-forbidden')

    def test_value_provenance_is_not_just_a_value(self):
        r,i=base();r['applications'][0]['bindings']['A']='another-account';refresh(r)
        self.refused(self.prepared(r,i),'value-provenance-mismatch')

    def test_application_cannot_change_consumer_or_use(self):
        for key in ('consumer','intended_use'):
            r,i=base();r['applications'][0][key]='other';refresh(r)
            with self.subTest(key=key):self.refused(self.prepared(r,i),'application-use-mismatch')

    def test_parameter_schema_failures_are_structured(self):
        for schema in ({'type':'string','minLength':'bad'},{'type':'string','pattern':'(a+)+$'},{'type':'object'}, {'type':'array','items':{'type':'string'}}):
            r,i=base();r['handling'][1]['payload']['working_meaning']['parameters'][0]['value_schema']=schema;refresh(r)
            with self.subTest(schema=schema):self.refused(self.prepared(r,i))

    def test_external_target_must_be_an_object(self):
        r,i=base();r['handling'][0]['payload']['meaning_ref']['selector']='/statement'
        self.refused(self.prepared(r,i),'invalid-meaning-carrier')

    def test_embedded_reference_must_target_actual_entry(self):
        r,i=base();a=r['applications'][0];a['meaning_ref']['selector']='/working_meanings/0/parameters'
        r['handling'][2]['payload']['parent_ref']=copy.deepcopy(a['meaning_ref'])
        self.refused(self.prepared(r,i),'invalid-embedded-entry')

    def test_external_meaning_has_no_inferred_parameters(self):
        r,i=external_application();source=decode(i['complete.json']);source.pop('parameters');i['complete.json']=encode(source)
        r['source_bindings'][-1]=binding(i['complete.json'],'complete.json')
        ref=r['applications'][0]['meaning_ref'];ref['sha256']=sha(encode(source));r['handling'][1]['payload']['meaning_ref']=copy.deepcopy(ref);refresh(r)
        self.refused(self.prepared(r,i),'missing-parameter-declarations')

    def test_unverified_assessment_cannot_claim_execution(self):
        for where in ('producer','validation'):
            r,i=base()
            if where=='producer':r['assessments'][0]['producer']['execution_posture']='verified-external'
            else:r['assessments'][0]['validation_posture']='binding-verified-within-scope'
            self.refused(self.prepared(r,i))

    def test_successor_requires_predecessor(self):
        r,i=base();r['request_revision']=2;refresh(r)
        self.refused(self.prepared(r,i),'missing-predecessor')

    def test_package_missing_corrupt_extra_and_traversal(self):
        d=self.package();raw=raw_members(d['package_members'])
        variants=[]
        missing=dict(raw);missing.pop('pack.json');variants.append(missing)
        corrupt=dict(raw);corrupt['pack.json']=b'{}';variants.append(corrupt)
        extra=dict(raw);extra['extra.json']=b'{}';variants.append(extra)
        traversal=dict(raw);manifest=decode(raw['manifest.json']);next(iter(manifest['members'].values()))['path']='../outside';traversal['manifest.json']=encode(manifest);variants.append(traversal)
        for members in variants:
            with self.subTest(keys=list(members)):self.refused(self.invoke('inspect',{'package_members':b64(members)}))

    def test_no_implicit_materialization(self):
        d=self.package();self.refused(self.invoke('materialize',{'package_members':d['package_members']}),'nothing-selected')

    def test_materialization_requires_owner_route(self):
        r,i=materialization();r['materialization_selection'][0]['owner_route']=None
        d=self.package(r,i);self.refused(self.invoke('materialize',{'package_members':d['package_members']}),'materialization-owner-gap')

    def test_private_material_is_not_exported(self):
        for raw in (b'-----BEGIN PRIVATE KEY-----',b'{"access_token":"public-test-marker"}'):
            r,i=base();add_source(r,i,'excluded.txt',raw)
            self.refused(self.prepared(r,i),'private-material')

    def test_catalog_aliases_cannot_duplicate_or_drop_sources(self):
        r,i=base();rows=[{'input_id':path,'binding':binding(raw,path),'reported_standing':None} for path,raw in i.items()]
        for selected in (rows[:1], [rows[0],rows[0]], [{**row,'input_id':'same'} for row in rows]):
            c={'schema_version':'define.source-catalog/v1','entries':selected,'authority_effect':'none'}
            self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':b64(i),'catalog_utf8':encode(c).decode()}))

    def test_member_and_frame_limits_are_enforced(self):
        r,i=no_sources()
        self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':{f'f{x}':'eA==' for x in range(257)}}))
        self.refused(self.invoke('capture',{'request_utf8':'x'*(1048576+1),'inputs':{}}))


class AdditionalBoundaries(Case):
    def test_binding_shaped_task_value_is_not_an_input_reference(self):
        r,i=base();meaning=r['handling'][1]['payload']['working_meaning']
        schema={'type':'object','additionalProperties':False,'required':['path','sha256','bytes','digest_kind'],
                'properties':{'path':{'type':'string'},'sha256':{'type':'string'},'bytes':{'type':'integer'},'digest_kind':{'type':'string'}}}
        next(p for p in meaning['parameters'] if p['name']=='F')['value_schema']=schema
        values=decode(i['incident-values.json']);values['filters']=binding(b'unselected-file','not-a-source.json');i['incident-values.json']=encode(values)
        old=r['source_bindings'][1];new=binding(i['incident-values.json'],'incident-values.json')
        r['source_bindings'][1]=new;meaning['lineage']=[new]
        a=r['applications'][0];a['lineage']=[new];a['bindings']['F']=values['filters']
        next(v for v in a['value_provenance'] if v['parameter']=='F')['sha256']=sha(encode(values['filters']))
        assessment=r['assessments'][0];assessment['input_bindings']=[new];assessment['lineage']=[new]
        d=self.package(refresh(r),i)
        self.assertEqual(d['pack']['applications'][0]['bindings']['F'],values['filters'])

    def test_capture_cannot_generate_reserved_control_prefix_collision(self):
        r,i=no_sources();add_source(r,i,'define-source-catalog.json/child.json',b'{}')
        self.refused(self.invoke('capture',{'request_utf8':encode(r).decode(),'inputs':b64(i)}))

    def test_preparation_cannot_silently_drop_extra_supplied_bytes(self):
        r,i=base();c=self.captured(r,i);c['inputs']['ignored.json']=b64({'x':b'{}'})['x']
        self.refused(self.prepared(r,i,c))

    def test_every_bound_input_row_refers_to_whole_captured_file(self):
        r,i=base();c=self.captured(r,i);c['capture']['input_rows'][0]['selector']='/nonexistent'
        c['capture_utf8']=encode(c['capture']).decode();self.refused(self.prepared(r,i,c))

    def test_invalid_assessment_reason_does_not_accompany_pass(self):
        r,i=base();r['assessments'][0]['reported_result']='PASS';r['assessments'][0]['unevaluable_reason']='Could not evaluate'
        self.refused(self.prepared(r,i))

    def test_materialization_references_are_checked_before_prepare_succeeds(self):
        r,i=materialization();r['materialization_selection'][0]['meaning_ref']['sha256']='f'*64
        self.refused(self.prepared(r,i))

    def test_method_gap_prevents_claimed_evaluable_assessment(self):
        r,i=base();r['assessments'][0]['reported_result']='NOT_EVALUABLE';r['assessments'][0]['unevaluable_reason']='Missing qualified method'
        d=self.package(r,i);self.assertEqual(d['pack']['assessments'][0]['reported_result'],'NOT_EVALUABLE')

    def test_specialize_meaning_change_does_not_overwrite_parent(self):
        r,i=base();parent=copy.deepcopy(r['handling'][0]['payload']['meaning_ref']);meaning=copy.deepcopy(r['handling'][1]['payload']['working_meaning'])
        r['handling'][1]={'concept_id':'complete-export','disposition':'specialize','payload':{'mode':'meaning-change','parent_ref':parent,
             'working_meaning':meaning,'delta':'Add completeness criterion for this bounded proposal','identity_intention':'new-identity','applicability':'One candidate examination'}}
        d=self.package(refresh(r),i);self.assertEqual(len(d['pack']['working_meanings']),1)
        self.assertEqual(d['pack']['working_meanings'][0]['status'],'local-proposed')

    def test_claimed_not_evaluable_needs_reason(self):
        r,i=base();r['assessments'][0]['reported_result']='NOT_EVALUABLE';r['assessments'][0]['unevaluable_reason']=None
        self.refused(self.prepared(r,i),'missing-unevaluable-reason')

    def test_reported_four_five_and_six_rows_are_preserved_without_execution(self):
        for count,result in ((4,'FAIL'),(5,'PASS'),(6,'FAIL')):
            r,i=base();values=decode(i['incident-values.json']);values['observed_ids']=[f'row-{x}' for x in range(1,count+1)]
            raw=encode(values);old=r['source_bindings'][1];new=binding(raw,'incident-values.json');i['incident-values.json']=raw
            r['source_bindings'][1]=new;r['handling'][1]['payload']['working_meaning']['lineage']=[new]
            r['applications'][0]['lineage']=[new];r['assessments'][0]['lineage']=[new];r['assessments'][0]['input_bindings']=[new]
            r['assessments'][0]['reported_result']=result
            r['assessments'][0]['applicability_limits']=[f'Authored report for {count} observed against 5 expected; no execution by Define.']
            with self.subTest(observed=count):
                d=self.package(refresh(r),i);self.assertEqual(d['pack']['assessments'][0]['reported_result'],result)
                self.assertEqual(d['report']['assessment_execution_count'],0)


class PredecessorCompatibility(Case):
    def test_rc1_empty_capture_encoding_record_is_preserved(self):
        from define_core.capture import ENCODING, ENCODING_PATH
        r,i=no_sources();c=self.captured(r,i);c['inputs'][ENCODING_PATH]=b64({'x':ENCODING})['x']
        d=self.ok(self.prepared(r,i,c))
        self.assertEqual(raw_members(d['package_members'])['inputs/'+ENCODING_PATH],ENCODING)
