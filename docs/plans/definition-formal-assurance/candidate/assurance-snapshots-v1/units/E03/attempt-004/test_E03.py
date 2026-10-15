"""Independent byte selection, denial controls and denotation checks."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];sys.path[:0]=[str(HERE),str(HERE/'tests')]
import verifier as v
import test_E01 as evidence
import test_A01 as fixtures
import test_P02 as finite_fixtures


def setup_selection():
    fixture,bundle,required,put=evidence.create_fixture();root=fixture.root
    theory=json.loads((root/bundle['theory_ref']['path']).read_text())
    rel=fixtures.payloads()['relation'];rel.update(relation_class='alias',direction='both',minimum_strength='mechanized-theorem',left_definition=theory['sources'][0],right_definition=theory['sources'][1],scope=theory['scope'],alignment={'status':'reviewed','map_ref':bundle['coupling_refs'][0]})
    endpoints={side:{'source':rel[side+'_definition'],'scope':rel['scope'],'predicate':name,'carrier':'Object'} for side,name in [('left','P'),('right','Q')]}
    populations=[{'population_id':'POP-'+name,'carrier':'Object','predicate_ref':name,'requirement':'required','statement':v.o.p.quant('exists','Object',v.o.p.pred(name)),'scope':rel['scope'],'rationale':'Required hypothetical inhabitant for this synthetic relation.','review_ref':None} for name in ['P','Q']]
    selection={'schema_version':'definition-assurance-verification-selection/v1-candidate','authority_effect':'none',**{key:bundle[key] for key in ['theory_ref','snapshot_ref','assumption_set_ref','dependency_graph_ref','coupling_refs']},'relation_requests_ref':put('selected/relations.json',[{'relation':rel,'bindings':endpoints,'proper':False,'distinction':'permitted','forbidden':[]}]),'populations_ref':put('selected/populations.json',populations),'endpoint_bindings_ref':put('selected/endpoints.json',endpoints),'finite_requests_ref':put('selected/finite.json',{}),'expected_contract':v.b.checked_contract(),'expected_provider_bindings_ref':put('selected/provider.json',{'bindings':v.f.current_bindings()})}
    assert v.r.same_json(required,v.o.generate(theory,json.loads((root/selection['relation_requests_ref']['path']).read_text()),populations,endpoints,root))
    return fixture,bundle,required,put,selection


def add_witness(bundle,put,selection,root,identity='query:consistency',mode='witness'):
    theory=json.loads((root/bundle['theory_ref']['path']).read_text());originals=[]
    for source,name in zip(theory['sources'],['P','Q']):
        core=fixtures.payloads()['interpretation'];core['source']=source;core['declarations'][1]['symbol_id']=name;core['clauses'][0]['formal_statement']['body']['name']=name
        originals.append(v.ir.compile_interpretation(core))
    subject=v.ir.compose(originals,bundle['coupling_refs'],root)
    names={name:v.ir.qualified(source,theory['scope'],name) for source,name in zip(theory['sources'],['P','Q'])}
    names['Object']=subject['sort_alignment'][v.ir.qualified(theory['sources'][0],theory['scope'],'Object')]
    renaming=[{'local_symbol_id':name,'canonical_id':names[name],'source':theory['sources'][0] if name in {'P','Object'} else theory['sources'][1]} for name in ['Object','P','Q']]
    obligations={row['obligation_id']:row for row in bundle['required_set']['logical_manifest']['obligations']}
    I=[] if identity=='query:consistency' else v.renamed([row['statement'] for key,row in obligations.items() if key.startswith('population:')],names)
    Q=v.renamed(obligations[identity]['statement'],names);cards={names['Object']:2}
    native=v.f.search(subject,[],I,Q,cards,mode=mode,selected_inputs=originals,selected_alignments=bundle['coupling_refs'],alignment_root=root)
    assert native['status'] in {'witness-found','countermodel-found'},native['status']
    request={'schema_version':'definition-assurance-verifier-finite-input/v1-candidate','subject_ref':put('selected/subject.json',subject),'selected_input_refs':[put('selected/input-'+str(i)+'.json',item) for i,item in enumerate(originals)],'alignment_refs':bundle['coupling_refs'],'renaming':renaming,'cardinalities':cards,'mode':mode}
    request_ref=put('selected/request.json',request);selection['finite_requests_ref']=put('selected/finite.json',{identity:request_ref})
    native_ref=put('candidate/native.json',native);row=next(row for row in bundle['logical_results'] if row['obligation']['obligation_id']==identity)
    row.update(provider_kind='finite-static',native_input_ref=request_ref,native_result={'binding':native_ref,'data':native},profile_ref=put('candidate/profile.json',json.loads(v.f.POLICY_PATH.read_text())),toolchain_ref=selection['expected_provider_bindings_ref'])
    execution,verdict,strength=v.b.e.finite_dimensions(native);row['result'].update(execution=execution,verdict=verdict,strength=strength,evidence_refs=[native_ref],profile_ref='profile:finite-static')
    return row,request,native,names


class DenotationControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject,cls.names=finite_fixtures.subject();cls.cards={cls.names['Object']:2};cls.bindings=v.f.current_bindings()
        cls.query={'op':'exists','sort':cls.names['Object'],'var':'x','body':{'op':'pred','name':cls.names['P'],'args':[{'op':'var','name':'x'}]}}
        cls.native=v.f.search(cls.subject,[],[],cls.query,cls.cards)
    def check(self,native=None,**options):return v.witness(self.subject,self.native if native is None else native,[],[],self.query,self.cards,'witness',self.bindings,**options)
    def fault(self,code,fn):
        with self.assertRaises(v.VerificationFault) as caught:fn()
        self.assertEqual(code,caught.exception.code)
    def test_actual_provider_witness_checked_by_separate_evaluator(self):
        with patch.object(v.f.s.Evaluator,'holds',side_effect=AssertionError('provider evaluator must not run')):
            out=self.check();self.assertEqual('checked-model-witness',out['status']);self.assertFalse(out['mechanized_proof']);self.assertFalse(out['semantic_ready'])
    def test_rehashed_false_witness_rejected(self):
        bad=copy.deepcopy(self.native);bad['witness']['model']['predicates'][self.names['P']]=[];bad['witness']['model_sha256']=v.ir.digest(bad['witness']['model']);self.fault('witness-fails-query',lambda:self.check(bad))
    def test_substituted_query_and_provider_rejected(self):
        bad=copy.deepcopy(self.native);bad['input_bindings']['query_sha256']='0'*64;self.fault('witness-input-substitution',lambda:self.check(bad))
        bad=copy.deepcopy(self.native);bad['implementation_bindings'][0]['sha256']='0'*64;self.fault('provider-build-substitution',lambda:self.check(bad))
    def test_boolean_cardinality_and_claim_promotion_rejected(self):
        cards={self.names['Object']:True};self.fault('invalid-witness-cardinalities',lambda:v.witness(self.subject,self.native,[],[],self.query,cards,'witness',self.bindings))
        bad=copy.deepcopy(self.native);bad['unbounded_conclusion']='proved';self.fault('invalid-witness-claim-boundary',lambda:self.check(bad))
    def test_native_policy_and_missing_null_context_binding_rejected(self):
        bad=copy.deepcopy(self.native);bad['policy_sha256']='0'*64;self.fault('native-policy-substitution',lambda:self.check(bad))
        bad=copy.deepcopy(self.native);bad['input_bindings'].pop('composition_input_ir_sha256');self.fault('witness-input-substitution',lambda:self.check(bad))
    def test_duplicate_or_ill_sorted_extension_has_no_truth(self):
        bad=copy.deepcopy(self.native);rows=bad['witness']['model']['predicates'][self.names['P']];rows.append(rows[0]);self.fault('duplicate-predicate-tuple',lambda:self.check(bad))
        bad=copy.deepcopy(self.native);bad['witness']['model']['predicates'][self.names['P']]=[['outside']];self.fault('ill-sorted-model-tuple',lambda:self.check(bad))
    def test_model_incomplete_empty_domain_or_extra_predicate_rejected(self):
        for mutation,code in [(lambda model:model['predicates'].clear(),'model-signature-denominator-mismatch'),(lambda model:model['domains'].update({self.names['Object']:[]}),'empty-or-malformed-domain'),(lambda model:model['predicates'].update({'extra':[]}),'model-signature-denominator-mismatch')]:
            bad=copy.deepcopy(self.native);mutation(bad['witness']['model']);self.fault(code,lambda:self.check(bad))
    def test_population_and_theory_failure_are_distinct(self):
        neg={'op':'not','arg':self.query}
        for T,I,code in [([neg],[],'witness-fails-theory'),([],[neg],'witness-fails-population')]:
            bad=copy.deepcopy(self.native);bad['input_bindings'].update(theory_sha256=v.ir.digest(T),populations_sha256=v.ir.digest(I));self.fault(code,lambda:v.witness(self.subject,bad,T,I,self.query,self.cards,'witness',self.bindings))
    def test_cancellation_and_step_limit_no_truth(self):
        self.fault('cancelled',lambda:self.check(cancelled=lambda:True));self.fault('verifier-step-limit',lambda:self.check(max_steps=1))
    def test_bounded_exhaustion_is_not_accepted_as_model_or_theorem(self):
        bad=copy.deepcopy(self.native);bad['status']='bounded-supported';self.fault('no-checkable-model-witness',lambda:self.check(bad))
    def test_boolean_truth_rank_and_mode_substitution_rejected(self):
        bad=copy.deepcopy(self.native);bad['witness']['query_truth']=1;self.fault('witness-fails-query',lambda:self.check(bad))
        bad=copy.deepcopy(self.native);bad['witness']['interpretation_rank_zero_based']=True;self.fault('invalid-witness-rank',lambda:self.check(bad))
        bad=copy.deepcopy(self.native);bad['mode']='countermodel';self.fault('witness-mode-substitution',lambda:self.check(bad))
    def test_connective_truth_table_and_empty_identities(self):
        model=self.native['witness']['model'];e=v.Denotation(self.subject['declarations'],model);t={'op':'and','args':[]};f={'op':'or','args':[]}
        self.assertTrue(e.truth(t));self.assertFalse(e.truth(f))
        for left in [t,f]:
            for right in [t,f]:
                a=left==t;bb=right==t
                self.assertEqual((not a) or bb,e.truth({'op':'implies','left':left,'right':right}));self.assertEqual(a==bb,e.truth({'op':'iff','left':left,'right':right}))
    def test_total_function_product_and_nullary_extensions(self):
        decl=[{'kind':'sort','symbol_id':'S'},{'kind':'constant','symbol_id':'c','result_sort':'S'},{'kind':'total-function','symbol_id':'f','argument_sorts':['S'],'result_sort':'S'},{'kind':'predicate','symbol_id':'flag','argument_sorts':[]}]
        model={'domains':{'S':['a','b']},'constants':{'c':'a'},'functions':{'f':[{'args':['a'],'value':'b'},{'args':['b'],'value':'a'}]},'predicates':{'flag':[[]]}}
        e=v.Denotation(decl,model);self.assertTrue(e.truth({'op':'pred','name':'flag','args':[]}));self.assertTrue(e.truth({'op':'eq','left':{'op':'fn','name':'f','args':[{'op':'const','name':'c'}]},'right':{'op':'const','name':'c'}}) is False)
        model['functions']['f'].pop();self.fault('nontotal-function',lambda:v.Denotation(decl,model))
    def test_shadowing_is_local_and_separate_sorts_not_unified(self):
        decl=[{'kind':'sort','symbol_id':'S'},{'kind':'sort','symbol_id':'U'},{'kind':'predicate','symbol_id':'P','argument_sorts':['S']}];model={'domains':{'S':['a','b'],'U':['a']},'constants':{},'functions':{},'predicates':{'P':[['a']]}}
        e=v.Denotation(decl,model);p={'op':'pred','name':'P','args':[{'op':'var','name':'x'}]};inner={'op':'exists','var':'x','sort':'S','body':p};formula={'op':'forall','var':'x','sort':'S','body':{'op':'and','args':[inner,{'op':'eq','left':{'op':'var','name':'x'},'right':{'op':'var','name':'x'}}]}}
        self.assertTrue(e.truth(formula));self.assertEqual(['a'],model['domains']['U'])


class SelectionControls(unittest.TestCase):
    def setUp(self):
        self.fixture,self.bundle,self.required,self.put,self.selection=setup_selection();self.addCleanup(self.fixture.doCleanups);self.root=self.fixture.root
    def publish(self):
        out=v.b.publish(self.root,self.bundle,self.required,v.b.BASE+'/units/E03/controlled');self.assertEqual('published-candidate',out['status']);return out['bundle_ref']
    def verify(self,published=None):return v.verify(self.root,self.publish() if published is None else published,self.put('selected/selection.json',self.selection))
    def test_complete_missing_package_regenerated_independently_stays_pending(self):
        out=self.verify();self.assertEqual('verified-candidate-accounting',out['status']);self.assertEqual(5,len(out['pending_logical']));self.assertEqual(6,len(out['pending_gates']));self.assertFalse(out['semantic_ready']);self.assertEqual('historical-capture-only',out['source_currentness'])
    def test_actual_consistency_witness_integrates_explicit_nominal_mapping(self):
        add_witness(self.bundle,self.put,self.selection,self.root);out=self.verify();self.assertEqual('verified-candidate-accounting',out['status']);self.assertEqual(1,len(out['checked_logical']));self.assertTrue(out['checked_logical'][0]['minimum_strength_met']);self.assertEqual(4,len(out['pending_logical']))
    def test_removed_required_statement_rejected_not_inferred_from_result_list(self):
        self.bundle['logical_results'].pop();out=self.verify_failure_publish();self.assertEqual('publication-unresolved',out['status'])
    def verify_failure_publish(self):return v.b.publish(self.root,self.bundle,self.required,v.b.BASE+'/units/E03/controlled')
    def test_independently_selected_relation_changes_denominator(self):
        published=self.publish();requests=json.loads((self.root/self.selection['relation_requests_ref']['path']).read_text());requests[0]['relation'].update(relation_class='disjoint');self.selection['relation_requests_ref']=self.put('selected/relations.json',requests)
        out=self.verify(published);self.assertEqual('verification-rejected',out['status']);self.assertEqual('published-contract-accounting-invalid',out['diagnostics'][0]['code'])
    def test_dependency_or_assumption_artifact_substitution_rejected(self):
        published=self.publish()
        for key in ['dependency_graph_ref','assumption_set_ref']:
            old=self.selection[key];self.selection[key]=self.put('selected/'+key+'.json',{'status':'substitution'});out=self.verify(published);self.assertEqual('independent-artifact-substitution',out['diagnostics'][0]['code']);self.selection[key]=old
    def test_stale_independent_input_and_contract_build_rejected(self):
        published=self.publish();file=self.root/self.selection['populations_ref']['path'];raw=file.read_bytes();file.write_bytes(raw+b' ');out=self.verify(published);self.assertEqual('stale-independent-input',out['diagnostics'][0]['code']);file.write_bytes(raw)
        self.selection['expected_contract']['publisher_sha256']='0'*64;out=self.verify(published);self.assertEqual('unavailable-selected-contract-build',out['diagnostics'][0]['code'])
    def test_native_query_substitution_and_nominal_source_substitution(self):
        row,request,native,names=add_witness(self.bundle,self.put,self.selection,self.root);published=self.publish();request['renaming'][1]['source']=self.bundle['sources'][1]
        # Keep independently selected original ref: rehashed request substitution cannot hide behind provider success.
        self.put('selected/request.json',request);out=self.verify(published);self.assertEqual('stale-independent-input',out['diagnostics'][0]['code'])
    def test_rehashed_bad_model_rejected_even_in_validly_published_package(self):
        row,request,native,names=add_witness(self.bundle,self.put,self.selection,self.root,identity='query:joint-population');native['witness']['model']['predicates'][names['P']]=[];native['witness']['model_sha256']=v.ir.digest(native['witness']['model']);ref=self.put('candidate/native.json',native);row['native_result']['binding']=ref;row['result']['evidence_refs']=[ref]
        out=self.verify();self.assertEqual('witness-fails-population',out['diagnostics'][0]['code'])
    def forge(self):
        captured={ref['path']:v.r.read_bytes(self.root,ref['path']) for ref in v.b.e.artifact_refs(self.bundle)}
        manifest,name,envelope=v.b.manifest_for(self.bundle,captured,v.b.checked_contract());ref=v.b.BASE+'/units/E03/forged/'+name;target=self.root/ref;(target/'objects').mkdir(parents=True)
        (target/'envelope.json').write_bytes(envelope);(target/'manifest.json').write_bytes(v.b.canonical(manifest))
        for raw in captured.values():(target/'objects'/(v.r.digest(raw)+'.bin')).write_bytes(raw)
        return ref
    def test_forged_closed_package_omits_each_required_logical_or_gate_row(self):
        original=copy.deepcopy(self.bundle)
        for key in ['logical_results','gate_results']:
            self.bundle=copy.deepcopy(original);self.bundle[key].pop();out=self.verify(self.forge());self.assertEqual('published-contract-accounting-invalid',out['diagnostics'][0]['code'])
    def test_same_byte_bound_nominal_mapping_cannot_attribute_Q_to_source_A(self):
        row,request,native,names=add_witness(self.bundle,self.put,self.selection,self.root);request['renaming'][2]['source']=self.bundle['sources'][0]
        ref=self.put('selected/request.json',request);row['native_input_ref']=ref;self.selection['finite_requests_ref']=self.put('selected/finite.json',{'query:consistency':ref})
        out=self.verify();self.assertEqual('nominal-source-or-identity-substitution',out['diagnostics'][0]['code'])
    def test_countermodel_of_required_universal_is_checked_without_support(self):
        identity=next(row['obligation']['obligation_id'] for row in self.bundle['logical_results'] if row['obligation']['obligation_id'].startswith('relation:'))
        add_witness(self.bundle,self.put,self.selection,self.root,identity=identity,mode='countermodel');out=self.verify();self.assertEqual('verified-candidate-accounting',out['status']);self.assertFalse(out['checked_logical'][0]['query_truth']);self.assertFalse(out['checked_logical'][0]['minimum_strength_met'])
    def test_selected_input_mutation_during_check_is_rejected(self):
        row,request,native,names=add_witness(self.bundle,self.put,self.selection,self.root);published=self.publish();original=v.witness
        def change(*args,**kwargs):
            out=original(*args,**kwargs);file=self.root/self.selection['dependency_graph_ref']['path'];file.write_bytes(file.read_bytes()+b' ');return out
        with patch.object(v,'witness',side_effect=change):out=self.verify(published)
        self.assertEqual('independent-input-changed-during-verification',out['diagnostics'][0]['code'])
    def test_bounded_result_stays_explicitly_unverified(self):
        control=evidence.EvidenceControls();control.fixture=self.fixture;control.bundle=self.bundle;control.required=self.required;control.put=self.put;control.root=self.root
        control.finite('bounded-supported');out=self.verify();self.assertEqual('verified-candidate-accounting',out['status']);self.assertEqual(0,len(out['checked_logical']));self.assertEqual(5,len(out['pending_logical']));self.assertFalse(out['semantic_ready'])
    def test_selected_provider_drift_does_not_accept_historical_build_as_current(self):
        published=self.publish();record=json.loads((self.root/self.selection['expected_provider_bindings_ref']['path']).read_text());record['bindings'][0]['sha256']='0'*64;self.selection['expected_provider_bindings_ref']=self.put('selected/provider.json',record)
        out=self.verify(published);self.assertEqual('stale-selected-provider-build',out['diagnostics'][0]['code'])
    def test_live_source_changed_old_historical_capture_remains(self):
        published=self.publish();source=self.root/self.bundle['sources'][0]['path'];source.write_bytes(source.read_bytes()+b' ')
        self.assertEqual('verified-candidate-accounting',self.verify(published)['status']);out=v.verify(self.root,published,self.put('selected/selection.json',self.selection),live_source_root=self.root);self.assertEqual('verification-rejected',out['status']);self.assertTrue((self.root/published).is_dir())
    def test_pending_native_evidence_does_not_skip_nested_selected_input_bytes(self):
        row,request,native,names=add_witness(self.bundle,self.put,self.selection,self.root);row['native_result']=None;row['provider_kind']='unresolved';row['native_input_ref']=None;row['profile_ref']=None;row['toolchain_ref']=None;row['result'].update(execution='not-run',verdict='missing',strength='none',evidence_refs=[])
        published=self.publish();file=self.root/request['subject_ref']['path'];file.write_bytes(file.read_bytes()+b' ');out=self.verify(published);self.assertEqual('stale-independent-input',out['diagnostics'][0]['code'])
    def test_pending_gate_support_is_not_independently_verified(self):
        gate=self.bundle['gate_results'][0];data={'status':'supported','authority_effect':'none'};ref=self.put('candidate/gate.json',data);gate.update(execution='completed',currentness='current',reported_status='reported-supported',native_result={'binding':ref,'data':data},evidence_refs=[ref])
        out=self.verify();self.assertEqual('verified-candidate-accounting',out['status']);self.assertEqual(6,len(out['pending_gates']));self.assertFalse(out['semantic_ready'])
    def test_unknown_selection_fields_and_non_json_inputs_have_no_escape(self):
        published=self.publish();self.selection['extra']=True;out=self.verify(published);self.assertEqual('malformed-independent-selection',out['diagnostics'][0]['code'])
        file=self.root/'selected/malformed.json';file.write_text('{broken');out=v.verify(self.root,published,{'path':'selected/malformed.json','sha256':v.r.digest(file.read_bytes())});self.assertEqual('verification-rejected',out['status'])


if __name__=='__main__':unittest.main()
