"""Clause-accounting and explicit-role controls are independent of proof."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_A02 as fixtures
ROOT=Path(__file__).resolve().parents[5]
UNIT=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/A04'
sys.path.insert(0,str(UNIT))
import correspondence as c
import build_review_packet as b


class CorrespondenceTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.CaptureTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.root=self.fixture.root
        for entry in self.fixture.entries:
            path=self.root/entry['path'];doc=json.loads(path.read_text());doc.update(voices={'scientific_formal':{'normative_statement':'A record is relevant iff it has property P.','formal_expression':'R(x) iff P(x)'},'plain_language':{'explanation':'A relevant record has the selected property.'}},boundaries={'exclusions':['An arbitrary label is not conformance.']},scope={'applicability':'A selected local record universe.'},claim_ceiling='Source fixture only; no authority or truth claim.')
            raw=json.dumps(doc).encode();path.write_bytes(raw);entry['sha256']=c.r.digest(raw)
        self.fixture.save_registry();self.snapshot=c.r.capture(self.root);row=self.snapshot['current_entries'][0];source={k:row[k] for k in ['definition_id','version_ref','path','sha256']};self.document=c.source_document(self.snapshot,source);self.packet=b.draft(source,self.document)

    def check(self,**kwargs):return c.check(self.packet,self.snapshot,**kwargs)

    def invalid(self,code):
        result=self.check();self.assertFalse(result['semantic_ready']);self.assertEqual(code,result['diagnostics'][0]['code'])

    def formula(self):return {'op':'forall','var':'x','sort':'Record','body':{'op':'pred','name':'P','args':[{'op':'var','name':'x'}]}}

    def encode(self,index=0,role='definition'):
        clause=self.packet['interpretation']['clauses'][index];clause.update(disposition='encoded',forms=['genus-differentia'],roles=[role],formal_statement=self.formula());return clause

    def select_assumption(self,index=0,role='selected-premise'):
        clause=self.encode(index,role);clause['disposition']='externally-assumed'
        assumption={'assumption_id':'A1','statement':copy.deepcopy(clause['formal_statement']),'source_refs':[copy.deepcopy(self.packet['interpretation']['source'])],'scope':self.packet['interpretation']['scope'],'role':role,'selected':True,'context_id':'CTX1','selection_basis':'Explicit conditional reasoning context selected for this synthetic control.','commitment':'defeasible','dependency_refs':[],'evidence_posture':'unproved','revision_route':'Reconsider before the next decision.'}
        self.packet['interpretation']['assumptions']=[assumption];self.packet['assumption_links']=[{'clause_id':clause['clause_id'],'assumption_id':'A1'}];return assumption

    def test_every_source_leaf_retained_without_default_axioms(self):
        result=self.check();self.assertEqual('correspondence-pending',result['status']);self.assertTrue(result['character_accounting_complete'])
        self.assertEqual(len(c.inventory(self.document)),result['source_units']);self.assertTrue(result['unresolved_clauses'])
        self.assertEqual([],self.packet['interpretation']['assumptions']);self.assertTrue(all(x['formal_statement'] is None for x in self.packet['interpretation']['clauses']))

    def test_complete_text_and_candidate_formulas_do_not_supply_semantic_readiness(self):
        for index in range(len(self.packet['interpretation']['clauses'])):self.encode(index)
        result=self.check();self.assertEqual('candidate-accounted',result['status']);self.assertFalse(result['semantic_ready'])
        self.assertEqual('not-assessed',result['logical_typing']);self.assertEqual('pending',result['source_fidelity']);self.assertEqual('not-assessed',result['proof'])

    def test_inventory_cannot_omit_boundary_example_or_normative_unit(self):
        for selector in ['/boundaries/exclusions/0','/voices/plain_language/explanation','/voices/scientific_formal/normative_statement']:
            with self.subTest(selector=selector):
                original=copy.deepcopy(self.packet);self.packet['source_units']=[x for x in self.packet['source_units'] if x['selector']!=selector];self.invalid('source-unit-denominator-mismatch');self.packet=original

    def test_duplicate_unit_and_forged_source_digest_rejected(self):
        original=copy.deepcopy(self.packet);self.packet['source_units'].append(copy.deepcopy(self.packet['source_units'][0]));self.assertEqual('malformed',self.check()['status'])
        self.packet=original;self.packet['interpretation']['source']['sha256']='0'*64;self.invalid('unbound-current-interpretation-source')

    def test_missing_entire_clause_leaves_partial_character_accounting(self):
        self.packet['interpretation']['clauses'].pop();self.packet['correspondence'].pop()
        result=self.check();self.assertFalse(result['character_accounting_complete']);self.assertEqual('correspondence-pending',result['status']);self.assertFalse(result['semantic_ready'])

    def test_forged_excerpt_hash_start_or_end_rejected(self):
        original=copy.deepcopy(self.packet)
        for mutate in [lambda:self.packet['correspondence'][0].update(excerpt='Invented'),lambda:self.packet['interpretation']['clauses'][0].update(excerpt_sha256='0'*64),lambda:self.packet['interpretation']['clauses'][0].update(start_character=1),lambda:self.packet['correspondence'][0].update(end_character=999)]:
            self.packet=copy.deepcopy(original);mutate();self.invalid('clause-excerpt-binding-mismatch')

    def test_partial_ranges_are_visible_and_overlap_is_rejected(self):
        clause=self.packet['interpretation']['clauses'][0];link=self.packet['correspondence'][0];text=link['excerpt'];split=len(text)//2
        clause['excerpt_sha256']=c.r.digest(text[:split].encode());link.update(excerpt=text[:split],end_character=split)
        self.assertFalse(self.check()['character_accounting_complete'])
        second=copy.deepcopy(clause);second.update(clause_id='split-clause',start_character=split,excerpt_sha256=c.r.digest(text[split:].encode()))
        self.packet['interpretation']['clauses'].append(second);self.packet['correspondence'].append({'unit_id':link['unit_id'],'clause_id':'split-clause','end_character':len(text),'excerpt':text[split:]})
        self.assertTrue(self.check()['character_accounting_complete'])
        second.update(start_character=split-1,excerpt_sha256=c.r.digest(text[split-1:].encode()));self.packet['correspondence'][-1]['excerpt']=text[split-1:]
        self.invalid('overlapping-source-clause-ranges')

    def test_unmapped_formal_clause_and_duplicate_mapping_rejected(self):
        clause=copy.deepcopy(self.packet['interpretation']['clauses'][0]);clause['clause_id']='UNMAPPED';self.packet['interpretation']['clauses'].append(clause);self.invalid('unmapped-formal-clause')
        self.packet['interpretation']['clauses'].pop();link=copy.deepcopy(self.packet['correspondence'][0]);link['end_character']+=1;self.packet['correspondence'].append(link);self.invalid('duplicate-clause-correspondence')

    def test_explicit_premise_binding_required_and_statement_not_substitutable(self):
        assumption=self.select_assumption();self.assertEqual('correspondence-pending',self.check()['status'])
        assumption['selected']=False;self.invalid('unselected-or-substituted-assumption');assumption['selected']=True
        assumption['statement']={'op':'not','arg':self.formula()};self.invalid('unselected-or-substituted-assumption')

    def test_hypothesis_proof_target_and_explanation_never_silent_assumptions(self):
        for role in ['hypothesis','proof-obligation','explanation-example']:
            with self.subTest(role=role):
                original=copy.deepcopy(self.packet);clause=self.encode(0,role);clause['disposition']='externally-assumed';self.invalid('unselected-or-substituted-assumption');self.packet=original

    def test_unlinked_selected_assumption_and_encoded_premise_rejected(self):
        self.select_assumption();self.packet['assumption_links']=[];self.invalid('unselected-or-substituted-assumption')
        self.packet['assumption_links']=[{'clause_id':self.packet['interpretation']['clauses'][0]['clause_id'],'assumption_id':'A1'}];self.packet['interpretation']['clauses'][0]['disposition']='encoded';self.invalid('assumption-disposition-mismatch')

    def test_explanation_and_unresolved_cannot_hide_formula(self):
        self.packet['interpretation']['clauses'][0]['formal_statement']=self.formula();self.invalid('nonencoded-clause-has-formula')
        self.packet['interpretation']['clauses'][0].update(formal_statement=None,disposition='explanatory',roles=['definition']);self.invalid('explanation-role-mismatch')

    def test_required_dependency_cannot_be_omitted_substituted_or_unused(self):
        ref={k:self.snapshot['current_entries'][1][k] for k in ['definition_id','version_ref','path','sha256']}
        result=self.check(required_dependencies=[ref['version_ref']]);self.assertEqual('required-dependency-denominator-mismatch',result['diagnostics'][0]['code'])
        self.packet['interpretation']['depends_on']=[ref];self.invalid('unused-declared-dependency')
        self.packet['dependency_links']=[{'clause_id':self.packet['interpretation']['clauses'][0]['clause_id'],'dependency_ref':copy.deepcopy(ref),'kind':'semantic-use','rationale':'Explicit dependency for synthetic control.'}]
        self.assertEqual('correspondence-pending',self.check(required_dependencies=[ref['version_ref']])['status'])
        self.packet['dependency_links'][0]['dependency_ref']['sha256']='0'*64;self.invalid('undeclared-semantic-dependency')

    def test_source_conflict_must_be_present_and_point_to_actual_source(self):
        result=self.check(required_conflicts=['FID-HYP-001']);self.assertEqual('required-source-conflict-omitted',result['diagnostics'][0]['code'])
        self.packet['source_precedence']['conflicts']=[{'finding_id':'FID-HYP-001','selectors':['/missing'],'description':'Source conflict','status':'unresolved','owner_route':'role:definition-owner'}];self.invalid('unbound-conflict-selector')

    def test_realistic_instance_and_counterexample_required(self):
        for key in ['instances','counterexamples']:
            original=copy.deepcopy(self.packet);self.packet['review_packet'][key]=[];self.assertEqual('malformed',self.check()['status']);self.packet=original
        self.packet['review_packet']['instances'][0]['related_clause_ids']=['missing'];self.invalid('unbound-review-case-clause')

    def test_no_input_declared_owner_acceptance_readiness_or_extra_keys(self):
        for mutate in [lambda:self.packet.update(semantic_ready=True),lambda:self.packet['interpretation'].update(source_fidelity='accepted'),lambda:self.packet['review_packet'].update(review_status='owner-accepted'),lambda:self.packet.update(authority_effect='admitted')]:
            original=copy.deepcopy(self.packet);mutate();self.assertEqual('malformed',self.check()['status']);self.packet=original

    def test_logical_sort_errors_are_not_hidden_as_verified_types(self):
        self.encode();self.packet['interpretation']['clauses'][0]['formal_statement']['sort']='Undeclared'
        result=self.check();self.assertEqual('not-assessed',result['logical_typing']);self.assertFalse(result['semantic_ready'])

    def test_case_identity_and_conflict_identity_not_overloaded(self):
        self.packet['review_packet']['counterexamples'][0]['case_id']='instance-1';self.invalid('duplicate-review-case-id')
        self.packet['review_packet']['counterexamples'][0]['case_id']='counterexample-1'
        conflict={'finding_id':'FID-1','selectors':['/voices/scientific_formal/normative_statement'],'description':'Review tension','status':'unresolved','owner_route':'role:definition-owner'}
        self.packet['source_precedence']['conflicts']=[conflict,{**conflict,'description':'Another description'}];self.invalid('duplicate-source-conflict-id')


    def test_nominal_historical_source_not_current_translation(self):
        row=self.snapshot['historical_entries'][0];self.packet['interpretation']['source']={k:row[k] for k in ['definition_id','version_ref','path','sha256']};self.invalid('unbound-current-interpretation-source')


if __name__=='__main__':unittest.main()
