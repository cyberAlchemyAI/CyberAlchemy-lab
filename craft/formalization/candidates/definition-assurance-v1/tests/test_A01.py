import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('assurance_contracts',ROOT/'contracts.py')
C=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(C)
ZERO='0'*64


def source(identity='cal.definition.example',version='1.0.0'):
    return {'definition_id':identity,'version_ref':identity+'@'+version,'path':'candidate/example/definition.json','sha256':ZERO}


def formula():
    return {'op':'forall','var':'x','sort':'Object','body':{'op':'pred','name':'P','args':[{'op':'var','name':'x'}]}}


def payloads():
    return {
      'source':{'snapshot_id':'S1','registry_path':'authority/definitions/registry.json','registry_sha256':ZERO,'sources':[source()],'historical_sources':[], 'capture_status':'incomplete','current_lookup_sha256':ZERO},
      'interpretation':{'interpretation_id':'I1','source':source(),'scope':'candidate-scope','declarations':[
        {'kind':'sort','symbol_id':'Object','scope':'candidate-scope','domain_policy':'nonempty'},
        {'kind':'predicate','symbol_id':'P','scope':'candidate-scope','argument_sorts':['Object']}],
        'clauses':[{'clause_id':'C1','source_selector':'/voices/scientific_formal/normative_statement','excerpt_sha256':ZERO,'disposition':'encoded','forms':['genus-differentia'],'roles':['definition'],'formal_statement':formula(),'rationale':'Synthetic structural fixture; no source correspondence claim.','start_character':0}],
        'depends_on':[],'relations':[],'assumptions':[],'populations':[],'logic_features':['first-order'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':None},
      'relation':{'relation_id':'R1','left_definition':source('cal.definition.left'),'right_definition':source('cal.definition.right'),'relation_class':'unresolved','direction':'unresolved','scope':'candidate-scope','alignment':{'status':'unresolved','map_ref':None},'required_statements':[],'minimum_strength':'unresolved'},
      'assumption':{'assumption_id':'A1','statement':formula(),'source_refs':[],'scope':'candidate-scope','role':'selected-premise','selected':False,'context_id':'CTX1','selection_basis':'Candidate conditional context','commitment':'defeasible','dependency_refs':[],'evidence_posture':'unreviewed','revision_route':'candidate review'},
      'population':{'population_id':'POP1','carrier':'Object','predicate_ref':'P','requirement':'unresolved','statement':None,'scope':'candidate-scope','rationale':'Required policy not selected.','review_ref':None},
      'result':{'obligation_id':'O1','statement_sha256':ZERO,'theory_sha256':ZERO,'execution':'not-run','verdict':'unknown','strength':'none','currentness':'unknown','source_fidelity':{'status':'pending','review_ref':None},'profile_ref':None,'evidence_refs':[],'readiness':'not-assessed'},
      'obligation-manifest':{'manifest_id':'OM1','theory_sha256':ZERO,'policy_sha256':ZERO,'obligations':[{'obligation_id':'O1','statement':formula(),'assumption_set_ref':'CTX1','source_refs':[],'dependency_refs':[],'population_refs':[],'direction':'none','minimum_strength':'model-witness','status':'required'}],'population_refs':[]}}


def envelope(kind):
    return {'schema_version':'definition-assurance-input/v1-candidate','kind':kind,'authority_effect':'none','payload':payloads()[kind]}


def decode(data,kind=None):return C.decode(json.dumps(data).encode(),kind)


class InputControls(unittest.TestCase):
    def assertMalformed(self,data):
        result=decode(data)
        self.assertEqual(result['status'],'malformed')
        self.assertEqual(result['semantic_assurance'],'not-assessed')
        self.assertTrue(result['diagnostics'])

    def test_all_seven_kinds_are_structural_only(self):
        for kind in payloads():
            with self.subTest(kind=kind):
                result=decode(envelope(kind),kind)
                self.assertEqual(result['status'],'structurally-valid')
                self.assertEqual(result['authority_effect'],'none')
                self.assertEqual(result['semantic_assurance'],'not-assessed')

    def test_delete_every_root_and_payload_required_key(self):
        for kind in payloads():
            original=envelope(kind)
            for key in original:
                with self.subTest(kind=kind,root_key=key):
                    candidate=copy.deepcopy(original);del candidate[key];self.assertMalformed(candidate)
            for key in original['payload']:
                with self.subTest(kind=kind,payload_key=key):
                    candidate=copy.deepcopy(original);del candidate['payload'][key];self.assertMalformed(candidate)

    def test_delete_every_nested_fixture_required_key(self):
        def paths(value,path=()):
            if isinstance(value,dict):
                for key,item in value.items():
                    yield (*path,key)
                    yield from paths(item,(*path,key))
            elif isinstance(value,list):
                for index,item in enumerate(value):yield from paths(item,(*path,index))
        for kind in payloads():
            original=envelope(kind)
            for path in paths(original['payload'],('payload',)):
                if len(path)<3:continue
                with self.subTest(kind=kind,path=path):
                    candidate=copy.deepcopy(original);parent=candidate
                    for key in path[:-1]:parent=parent[key]
                    del parent[path[-1]]
                    self.assertMalformed(candidate)

    def test_unknown_fields_at_root_payload_and_clause_are_rejected(self):
        for kind in payloads():
            for container in ['root','payload']:
                candidate=envelope(kind)
                (candidate if container=='root' else candidate['payload'])['ignored_marker']=True
                self.assertMalformed(candidate)
        candidate=envelope('interpretation');candidate['payload']['clauses'][0]['ignored_marker']=True;self.assertMalformed(candidate)

    def test_duplicate_json_keys_nested_and_unicode_escaped(self):
        for raw in [b'{"kind":"source","kind":"result"}',b'{"payload":{"x":1,"x":2}}',b'{"op":1,"o\\u0070":2}']:
            result=C.decode(raw)
            self.assertEqual(result['status'],'malformed')
            self.assertEqual(result['diagnostics'][0]['code'],'duplicate-json-key')

    def test_duplicate_source_identity_with_changed_fields(self):
        candidate=envelope('source');candidate['payload']['sources'].append(source(version='2.0.0'))
        result=decode(candidate)
        self.assertEqual(result['diagnostics'][0]['code'],'duplicate-identity')

    def test_historical_versions_remain_distinct_exact_identities(self):
        candidate=envelope('source');candidate['payload']['historical_sources']=[source(version='0.1.0'),source(version='0.2.0')]
        self.assertEqual(decode(candidate)['status'],'structurally-valid')

    def test_duplicate_clauses_and_symbols_with_different_metadata(self):
        for collection,key in [('clauses','rationale'),('declarations','domain_policy')]:
            candidate=envelope('interpretation');row=copy.deepcopy(candidate['payload'][collection][0])
            row[key]='changed' if collection=='clauses' else 'extension-required'
            candidate['payload'][collection].append(row)
            self.assertMalformed(candidate)

    def test_wrong_types_boolean_is_not_integer_and_no_defaults(self):
        candidate=envelope('interpretation');candidate['payload']['clauses'][0]['start_character']=True;self.assertMalformed(candidate)
        candidate=envelope('assumption');candidate['payload']['selected']='false';self.assertMalformed(candidate)
        for kind in payloads():
            candidate=envelope(kind);candidate['payload']=[];self.assertMalformed(candidate)

    def test_nonfinite_and_overflow_numbers_are_typed_malformed(self):
        for token in ['NaN','Infinity','-Infinity','1e400']:
            result=C.decode(('{"value":'+token+'}').encode())
            self.assertEqual(result['status'],'malformed')
            self.assertEqual(result['diagnostics'][0]['code'],'nonfinite-number')

    def test_utf8_surrogates_wrong_transport_and_invalid_json(self):
        for raw in [b'\xff',b'{"value":"\\ud800"}',b'{broken',b'{} trailing']:
            self.assertEqual(C.decode(raw)['status'],'malformed')
        self.assertEqual(C.decode('{}')['diagnostics'][0]['code'],'utf8-bytes-required')

    def test_explicit_resource_limits_precede_schema_validation(self):
        self.assertEqual(C.decode(b' '*(C.MAX_BYTES+1))['diagnostics'][0]['code'],'byte-limit')
        nested='['*70+'0'+']'*70
        self.assertEqual(C.decode(nested.encode())['diagnostics'][0]['code'],'depth-limit')
        with patch.object(C,'MAX_NODES',2):
            self.assertEqual(decode(envelope('source'))['diagnostics'][0]['code'],'node-limit')

    def test_valid_nested_quantifiers_do_not_validate_unrelated_recursive_branches(self):
        candidate=envelope('interpretation');body=formula()
        for n in range(12):body={'op':'forall','var':'x'+str(n),'sort':'Object','body':body}
        candidate['payload']['clauses'][0]['formal_statement']=body
        self.assertEqual(decode(candidate)['status'],'structurally-valid')

    def test_unknown_operator_and_extra_ast_field_are_rejected(self):
        for body in [{'op':'eventually','body':formula()},{**formula(),'ignored':True}]:
            candidate=envelope('interpretation');candidate['payload']['clauses'][0]['formal_statement']=body;self.assertMalformed(candidate)

    def test_unresolved_clause_preserves_missing_statement_without_semantic_pass(self):
        candidate=envelope('interpretation');clause=candidate['payload']['clauses'][0]
        clause['disposition']='unresolved';clause['formal_statement']=None;clause['forms']=['unresolved'];clause['roles']=['unresolved']
        candidate['payload']['semantic_status']='unresolved'
        result=decode(candidate)
        self.assertEqual(result['status'],'structurally-valid')
        self.assertEqual(result['semantic_assurance'],'not-assessed')
        clause['disposition']='encoded';self.assertMalformed(candidate)

    def test_required_population_and_review_claim_need_their_declared_bindings(self):
        candidate=envelope('population');candidate['payload']['requirement']='required';self.assertMalformed(candidate)
        candidate=envelope('result');candidate['payload']['source_fidelity']['status']='reviewed';self.assertMalformed(candidate)
        candidate=envelope('relation');candidate['payload']['alignment']['status']='reviewed';self.assertMalformed(candidate)

    def test_submitter_cannot_declare_derived_readiness_or_authority_effect(self):
        candidate=envelope('result');candidate['payload']['readiness']='ready';self.assertMalformed(candidate)
        candidate=envelope('interpretation');candidate['authority_effect']='admit';self.assertMalformed(candidate)

    def test_scope_paths_and_version_identity_are_checked_without_source_io(self):
        for badpath in ['../private.json','/etc/passwd','candidate/../private.json','C:\\private.json']:
            candidate=envelope('source');candidate['payload']['sources'][0]['path']=badpath;self.assertMalformed(candidate)
        candidate=envelope('source');candidate['payload']['sources'][0]['version_ref']='other.identity@1.0.0';self.assertMalformed(candidate)
        candidate=envelope('source');candidate['payload']['sources'][0]['version_ref']='cal.definition.example@';self.assertMalformed(candidate)

    def test_input_cannot_select_remote_schema_or_fetch_refs(self):
        candidate=envelope('source');candidate['$ref']='https://example.invalid/schema';self.assertMalformed(candidate)
        candidate=envelope('source');candidate['payload']['schema_url']='https://example.invalid/schema';self.assertMalformed(candidate)

    def test_repeated_mathematical_argument_is_permitted(self):
        candidate=envelope('interpretation')
        candidate['payload']['clauses'][0]['formal_statement']={'op':'eq','left':{'op':'fn','name':'pair','args':[{'op':'const','name':'a'},{'op':'const','name':'a'}]},'right':{'op':'const','name':'a'}}
        self.assertEqual(decode(candidate)['status'],'structurally-valid')

    def test_digest_identity_and_path_cannot_hide_trailing_whitespace(self):
        for key in ['sha256','version_ref','path','definition_id']:
            candidate=envelope('source');candidate['payload']['sources'][0][key]+='\n';self.assertMalformed(candidate)
        candidate=envelope('interpretation');candidate['payload']['declarations'][0]['symbol_id']+='\n';self.assertMalformed(candidate)

    def test_partial_function_requires_explicit_definedness_policy(self):
        candidate=envelope('interpretation');row={'kind':'partial-function','symbol_id':'lookup','scope':'candidate-scope','argument_sorts':['Object'],'result_sort':'Object','definedness_policy':None}
        candidate['payload']['declarations'].append(row);self.assertMalformed(candidate)
        row['definedness_policy']='Explicit Defined(x) plus result graph'
        self.assertEqual(decode(candidate)['status'],'structurally-valid')
        row['kind']='total-function';self.assertMalformed(candidate)
        row['definedness_policy']=None
        self.assertEqual(decode(candidate)['status'],'structurally-valid')

    def test_incompatible_or_external_local_schema_is_typed_unavailable(self):
        original=json.loads(C.SCHEMA_PATH.read_text())
        with tempfile.TemporaryDirectory(prefix='assurance_A01_schema_') as tmp:
            path=Path(tmp)/'schema.json'
            for key in ['$ref','$dynamicRef','$recursiveRef']:
                altered=copy.deepcopy(original);altered[key]='https://example.invalid/schema';path.write_text(json.dumps(altered))
                with patch.object(C,'SCHEMA_PATH',path):
                    self.assertEqual(decode(envelope('source'))['diagnostics'][0]['code'],'external-schema-reference-prohibited')
            altered=copy.deepcopy(original);altered['$ref']='#/$defs/missing';path.write_text(json.dumps(altered))
            with patch.object(C,'SCHEMA_PATH',path):
                self.assertEqual(decode(envelope('source'))['diagnostics'][0]['code'],'unbound-local-schema-reference')
            altered=copy.deepcopy(original);altered['type']='not-a-type';path.write_text(json.dumps(altered))
            with patch.object(C,'SCHEMA_PATH',path):
                self.assertEqual(decode(envelope('source'))['diagnostics'][0]['code'],'invalid-local-schema')

    def test_expected_kind_and_missing_runtime_return_typed_results(self):
        self.assertEqual(decode(envelope('source'),'result')['diagnostics'][0]['code'],'unexpected-input-kind')
        with patch.object(C,'Draft202012Validator',None):
            self.assertEqual(decode(envelope('source'))['status'],'unsupported-runtime')

    def test_cli_valid_invalid_and_missing_file_exit_codes(self):
        with tempfile.TemporaryDirectory(prefix='assurance_A01_') as tmp:
            path=Path(tmp)/'input.json';path.write_text(json.dumps(envelope('source')))
            run=subprocess.run([sys.executable,str(ROOT/'contracts.py'),'validate','--kind','source','--input',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0);self.assertEqual(json.loads(run.stdout)['semantic_assurance'],'not-assessed')
            path.write_text('{broken')
            run=subprocess.run([sys.executable,str(ROOT/'contracts.py'),'validate','--input',str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,2);self.assertEqual(json.loads(run.stdout)['status'],'malformed')
            run=subprocess.run([sys.executable,str(ROOT/'contracts.py'),'validate','--input',str(Path(tmp)/'missing.json')],capture_output=True,text=True)
            self.assertEqual(run.returncode,2);self.assertEqual(json.loads(run.stdout)['diagnostics'][0]['code'],'unreadable-input')


if __name__=='__main__':unittest.main()
