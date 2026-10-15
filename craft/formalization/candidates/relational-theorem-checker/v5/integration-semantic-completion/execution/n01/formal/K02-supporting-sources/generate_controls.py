"""Exercise complete Decision schema, exact prior endpoint cases and source alignment."""
from pathlib import Path
from copy import deepcopy
import hashlib, json
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
def binding(path): return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def literal(text): return json.dumps(text,ensure_ascii=False)
def save(name,value): (HERE/name).write_text(json.dumps(value,indent=2)+'\n')

def run():
    manifest=json.loads((HERE/'profile-manifest.json').read_text());profile=manifest['profiles'][0]
    schema_path=ROOT/profile['schema']['path'];schema=json.loads(schema_path.read_text())
    validator=Draft202012Validator(schema)
    positive_path=ROOT/profile['positive_fixture']['path'];positive=json.loads(positive_path.read_text())
    cases=[];decision_cases=[]
    def add(identifier,expression,expected): cases.append({'id':identifier,'expression':expression,'expected':expected})
    def body(identifier,value,expected):
        observed=validator.is_valid(value);assert observed==expected,identifier
        raw=json.dumps(value,ensure_ascii=False,separators=(',',':'))
        decision_cases.append({'id':identifier,'raw':raw,'expected':expected})
        add('decision:'+identifier,f'(checkedForSourceKind "decision" {literal(raw)}).isSome',str(expected).lower())
    header='''import SupportingPayloadIntegration
import DispatchControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateSupportingSources.RuntimeControls
open CandidateCatalogSnapshots.RuntimeEncoding (encodeRef encodeBytes)
def checked (text : String) :=
  (CandidateScalarConversion.parseScalarDocumentBytes text.toUTF8.toList).bind decodeFamily
def checkedForSourceKind (sourceKind text : String) :=
  (checked text).bind fun output =>
    if FamilyBody.sourceKind output = sourceKind then some output else none
def checkedArtifact (text sourceKind identity : String) :=
  (CandidateBodyDispatch.RuntimeControls.artifactAst text sourceKind identity).bind alignedArtifact.decode
'''
    prior_path=HERE.parent/'K02-typed-payload-bodies/fixture-validation.json'
    prior=json.loads(prior_path.read_text())
    for row in prior['input_cases']:
        add('endpoint:'+row['id'],f'(checkedForSourceKind {literal(row["kind"])} {literal(row["raw"])}).isSome',str(row['expected']).lower())
    body('original-positive',positive,True)
    for ref in profile['negative_fixtures']:
        path=ROOT/ref['path'];assert binding(path)==ref
        body('original-negative:'+path.name,json.loads(path.read_text()),False)
    for key in schema['required']:
        changed=deepcopy(positive);del changed[key];body('required:'+key,changed,False)
    for container,example in [('payload',positive['payload']),('relation_refs',positive['relation_refs'][0])]:
        for key in example:
            changed=deepcopy(positive)
            del (changed[container] if container=='payload' else changed[container][0])[key]
            body('nested-required:'+container+':'+key,changed,False)
    arrays=[(('evidence_refs',),schema['properties']['evidence_refs']),
            (('successor_refs',),schema['properties']['successor_refs']),
            (('relation_refs',),schema['properties']['relation_refs'])]
    arrays += [(('payload',k),r) for k,r in schema['properties']['payload']['properties'].items() if r.get('type')=='array']
    for path,rule in arrays:
        for posture in ['empty','duplicate','wrong-item']:
            changed=deepcopy(positive);target=changed
            for key in path[:-1]:target=target[key]
            key=path[-1];original=target[key]
            if posture=='empty':target[key]=[]
            elif posture=='duplicate':target[key]=[deepcopy(original[0] if original else 'example')]*2
            else:target[key]=[42]
            body('array:'+'.'.join(path)+':'+posture,changed,validator.is_valid(changed))
    for key,rule in schema['properties'].items():
        if isinstance(positive[key],str):
            changed=deepcopy(positive);changed[key]='';body('empty-string:'+key,changed,False)
        if 'const' in rule or 'enum' in rule:
            changed=deepcopy(positive);changed[key]='wrong-value';body('constant-or-enum:'+key,changed,False)
    for container,example in [('payload',positive['payload']),('relation_refs',positive['relation_refs'][0])]:
        for key,value in example.items():
            if isinstance(value,str):
                changed=deepcopy(positive);target=changed[container] if container=='payload' else changed[container][0]
                target[key]='';body('empty-nested-string:'+container+':'+key,changed,False)
    changed=deepcopy(positive);changed['payload']['selected_outcome']=' ';body('whitespace-permitted-by-minLength',changed,True)
    changed=deepcopy(positive);changed['relation_refs']=[deepcopy(positive['relation_refs'][0])]*2;body('repeated-relation-occurrences-permitted',changed,True)
    raw=json.dumps(positive,separators=(',',':'))
    header+='\ndef decisionText : String := '+literal(raw)+'\n'
    all_profiles=json.loads((HERE.parent/'K02-complete-payload-provider/profile-manifest.json').read_text())['profiles']+[profile]
    for row in all_profiles:
        name=row['kind'].replace('-','_');text='decisionText' if row['kind']=='decision' else 'CandidateBodyDispatch.RuntimeControls.text_'+name
        original=json.loads((ROOT/row['positive_fixture']['path']).read_text());identity=original[row['identity_field']]
        add(row['kind']+':family-kind',f'(checked {text}).map FamilyBody.sourceKind','some '+literal(row['kind']))
        add(row['kind']+':family-identity',f'(checked {text}).map FamilyBody.identity','some '+literal(identity))
        for other in all_profiles:
            add(row['kind']+':wrapper-kind:'+other['kind'],f'(checkedArtifact {text} {literal(other["kind"])} {literal(identity)}).isSome',str(other['kind']==row['kind']).lower())
        add(row['kind']+':wrong-identity',f'(checkedArtifact {text} {literal(row["kind"])} "wrong-identity").isSome','false')
    duplicate='{'+literal('kind')+':'+literal('decision')+','+raw[1:]
    add('decision:raw-duplicate-kind',f'(checked {literal(duplicate)}).isSome','false')
    add('decision:tag-alone-insufficient','(checked "{\\"kind\\":\\"decision\\"}").isSome','false')
    add('unknown-support-kind','(checked "{\\"kind\\":\\"satisfaction-test\\"}").isSome','false')
    add('old-synthetic-full-entry-success','(CandidateNestedProvenance.RuntimeControls.result).toOption.isSome','true')
    add('extended-full-refuses-opaque-synthetic-payloads',
        '(runSupportingFull CandidateProfileEvidence.Controls.bootstrap CandidateNestedProvenance.RuntimeControls.limits CandidateEvidenceResources.Controls.numbers CandidateProfileEvidence.Controls.root CandidateNestedProvenance.GeneratedFixture.authorityRef CandidateNestedProvenance.RuntimeControls.inputs CandidateNestedProvenance.RuntimeControls.world CandidateNestedProvenance.RuntimeControls.claim).toOption.isSome','false')
    assert len(cases)==len({c['id'] for c in cases})
    (HERE/'SupportingControls.lean').write_text(header+'\n'+'\n'.join('#eval '+c['expression'] for c in cases)+'\nend RelationalSuccessor.CandidateSupportingSources.RuntimeControls\n')
    save('control-index.json',{'task':'N01','unit':HERE.name,'runtime_cases':cases,
         'runtime_case_count':len(cases),'prior_endpoint_schema_cases':296,'decision_schema_cases':len(decision_cases),
         'family_kind_identity_cases':16,'wrapper_kind_cases':64,'wrong_identity_cases':8,'boundary_cases':5,
         'generator':binding(Path(__file__)),'prior_fixture_validation':binding(prior_path),
         'decision_profile_manifest':binding(HERE/'profile-manifest.json'),'source_fixtures':[r['positive_fixture'] for r in all_profiles],
         'decision_inputs':decision_cases,'schema_reference_method':'Exact local Draft202012Validator; fixture agreement is not a general source-schema correspondence proof.',
         'captured_context_is_synthetic':True,'independent_checker_run':False,'all_original_payload_roles_supported':False,
         'inherited_discharges':0,'authority_effect':'none'})
    print('Generated',len(cases),'observations;',len(decision_cases),'complete Decision schema controls.')
if __name__=='__main__':run()
