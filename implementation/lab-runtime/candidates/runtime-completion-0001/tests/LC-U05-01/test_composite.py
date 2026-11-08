"""Complete original Composite/R02 mapping and causal origin/scope refusals."""
import t08_prerequisite
from bootstrap import R,S,E,checked
import argparse,copy,json,tempfile,traceback,unittest
from pathlib import Path
from lab_contracts.codec import Refusal,sha
from environment.composite import verify_environment
from environment.origins import verify_selected_origins
from composite_fixture import CompositeFixture,PUBLIC_INPUTS
from semantic_fixture import final_original_guard

OWNED=[]
OBSERVATIONS=[]

class CompositeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='owned-composite-',dir=E)
        self.root=Path(self.temp.name);OWNED.append(self.root);self.f=CompositeFixture(self.root)
    def tearDown(self):self.temp.cleanup()
    def check(self,values=None):
        return verify_environment(*(values or self.f.selections()),repository=str(R))
    def reject(self,mutation):
        self.f.change_descriptor(mutation)
        with self.assertRaisesRegex(Refusal,'^COMPOSITE_ENVIRONMENT_REFUSED$'):self.check()
    def test_complete_original_mapping_bytes_wheels_elf_and_semantic_roles(self):
        result=self.check()
        self.assertEqual(result['source_rows'],24497);self.assertEqual(result['profile_rows'],24496)
        self.assertEqual(result['semantic_graph']['nodes'],3)
        self.assertEqual(result['execution_requirement_counts'],{'wheel':8,'interpreter':1,'native-executable':1,'stdlib':687,'host-abi':23})
        origins=result['execution_origins'];self.assertEqual(origins['elf_members'],77)
        self.assertTrue(origins['selected_content_verified']);self.assertFalse(origins['actual_modes_verified'])
        self.assertFalse(result['runtime_qualified']);self.assertFalse(result['full_original_proof_qualified'])
        self.assertFalse(result['actual_modules_imported']);self.assertFalse(result['installed_source_loading_policy_verified'])
        self.assertIn('-I',result['historical_execution_configuration']['python_flags'])
        self.assertNotIn('original_descriptor',result);self.assertNotIn('original_value',result)
        self.assertNotIn('elf_observations',origins);OBSERVATIONS.append(result)
    def test_unknown_environment_requirement_refuses(self):self.reject(lambda d:d.update(unselected_requirement=True))
    def test_wrong_versioned_r02_pointer_refuses(self):self.reject(lambda d:d['r02_selection'].update(json_pointer='/environment'))
    def test_r02_subdocument_cannot_hide_changed_runtime(self):self.reject(lambda d:d['r02_selection']['environment'].update(sqlite_version='0.0'))
    def test_r02_unknown_field_refuses(self):self.reject(lambda d:d['r02_selection']['environment'].update(extra='INERT_PRIVATE_VALUE'))
    def test_module_origin_missing_refuses(self):self.reject(lambda d:d['module_bindings'].pop())
    def test_coherently_repinned_module_origin_refuses(self):self.reject(lambda d:d['module_bindings'][0].update(sha256='0'*64))
    def coherent_closure_change(self,kind):
        value=copy.deepcopy(self.f.requirements)
        if kind=='reorder':value['inputs'].reverse()
        else:
            row=next(r for r in value['inputs'] if r['kind']==kind and
                (kind!='stdlib' or r['destination'] not in value['elf_graph']))
            value['inputs'].remove(row);value['elf_graph'].pop(row['destination'],None)
            self.f.origin_members=[r for r in self.f.origin_members if r['destination']!=row['destination']]
        raw=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
        self.f.add('candidate-execution','execution-selection',raw)
        selected_path=self.f.descriptor['execution_dependencies']['selection_binding']['path']
        for entry in self.f.legacy:
            if entry['path']==selected_path:
                entry.update(file_id='candidate-execution',binding=self.f.binding('candidate-execution'))
        def change(d):
            d['execution_dependencies']['selection_binding']['sha256']=sha(raw)
            if kind=='host-abi':
                d['host_ABI_library_bindings']=[r for r in d['host_ABI_library_bindings'] if r['path']!=row['path']]
        self.f.change_descriptor(change)
        with self.assertRaisesRegex(Refusal,'^COMPOSITE_ENVIRONMENT_REFUSED$'):self.check()
    def test_coherent_descriptor_execution_origin_unused_stdlib_omission(self):self.coherent_closure_change('stdlib')
    def test_coherent_descriptor_execution_origin_abi_omission(self):self.coherent_closure_change('host-abi')
    def test_coherent_descriptor_execution_origin_input_reorder(self):self.coherent_closure_change('reorder')
    def test_module_role_cannot_be_inferred_from_path(self):
        reader,selection,origins,graph=self.f.selections()
        row=next(r for r in selection.legacy_origins if r['role']=='host-dependency');row['role']='history-proof'
        with self.assertRaises(Refusal):self.check((reader,selection,origins,graph))
    def test_duplicate_legacy_origin_refuses(self):
        reader,selection,origins,graph=self.f.selections();selection.legacy_origins.append(copy.deepcopy(selection.legacy_origins[0]))
        with self.assertRaises(Refusal):self.check((reader,selection,origins,graph))
    def test_missing_legacy_origin_refuses(self):
        reader,selection,origins,graph=self.f.selections();selection.legacy_origins.pop()
        with self.assertRaises(Refusal):self.check((reader,selection,origins,graph))
    def test_legacy_digest_alone_cannot_replace_full_root(self):
        reader,selection,origins,graph=self.f.selections();selection.legacy_origins[0]['binding']['root_id']='other-root'
        with self.assertRaises(Refusal):self.check((reader,selection,origins,graph))
    def test_independent_cut_differs_from_reader(self):
        reader,selection,origins,graph=self.f.selections()
        from dataclasses import replace
        selection=replace(selection,source_cut={**selection.source_cut,'commit_sequence':2})
        with self.assertRaises(Refusal):self.check((reader,selection,origins,graph))
    def test_source_proof_cannot_be_replaced_by_alias_or_truncated_count(self):
        self.reject(lambda d:d['retained_full_proof'].update(source_rows=1))
    def test_historical_locator_alias_does_not_qualify_original_proof(self):
        self.reject(lambda d:d['retained_full_proof'].update(original_locator_aliases=['copy']))
    def test_native_requirement_cannot_be_dropped(self):self.reject(lambda d:d.pop('host_native_binding'))
    def test_native_mode_requirement_preserved(self):self.reject(lambda d:d['host_native_binding'].update(mode=420))
    def test_native_identity_substitution_refuses(self):self.reject(lambda d:d['host_native_binding'].update(sha256='0'*64))
    def test_abi_omission_refuses(self):self.reject(lambda d:d['host_ABI_library_bindings'].pop())
    def test_abi_order_is_original_contract_identity(self):self.reject(lambda d:d['host_ABI_library_bindings'].reverse())
    def test_historical_config_not_silently_rewritten_for_candidate(self):
        self.reject(lambda d:d['execution_dependencies']['execution_configuration'].update(python_flags=['-B','-S']))
    def test_complete_semantic_contract_is_consumed(self):
        reader,selection,origins,graph=self.f.selections();graph['declared_edges']=[{'source':'unselected','dependency':'missing'}]
        with self.assertRaises(Refusal):self.check((reader,selection,origins,graph))
    def test_private_schema_value_is_not_rendered(self):
        marker='INERT_'+'COMPOSITE_PRIVATE_MARKER';self.f.change_descriptor(lambda d:d.update(unknown=marker))
        try:self.check()
        except Refusal as e:
            self.assertEqual(str(e),'COMPOSITE_ENVIRONMENT_REFUSED');self.assertNotIn(marker,''.join(traceback.format_exception(e)))
        else:self.fail('unknown private field must refuse')
    def test_origin_member_omission_refuses_before_member_reads(self):
        reader,selection,origins,graph=self.f.selections();origins.members.pop()
        with self.assertRaisesRegex(Refusal,'^EXECUTION_ORIGIN_REFUSED$'):verify_selected_origins(reader,self.f.requirements,origins)
    def test_origin_alias_duplicate_refuses(self):
        reader,selection,origins,graph=self.f.selections();origins.members.append(copy.deepcopy(origins.members[0]))
        with self.assertRaises(Refusal):verify_selected_origins(reader,self.f.requirements,origins)
    def test_origin_binding_root_substitution_refuses(self):
        reader,selection,origins,graph=self.f.selections();origins.members[0]['binding']['root_id']='other-root'
        with self.assertRaises(Refusal):verify_selected_origins(reader,self.f.requirements,origins)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);p.add_argument('--report',type=Path);a=p.parse_args()
    if a.temp_root!=E or not E.is_dir():raise ValueError('owned root')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CompositeTests))
    final_original_guard();t08_prerequisite.guard()
    for path,b in PUBLIC_INPUTS.items():
        if len(checked(R/path,b['sha256']))!=b['size_bytes']:raise ValueError('public origin drift')
    clean=not any(p.exists() for p in OWNED)
    if a.report:
        if a.report.parent!=E or not a.report.name.startswith('composite-observation-'):raise ValueError('owned report')
        with a.report.open('x') as f:
            json.dump({'schema_version':'lab-u0501-composite-observation/v1','T08_checkpoint_sha256':t08_prerequisite.CHECKPOINT_SHA,
                'T08_independent_review_sha256':t08_prerequisite.REVIEW_SHA,'public_input_bindings':list(PUBLIC_INPUTS.values()),
                'observations':OBSERVATIONS,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
                'actual_modules_executed':0,'authority_effect':'none'},f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() and clean else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean' if clean else 'retained-owned'}))
    raise SystemExit(0 if result.wasSuccessful() and clean else 1)
