"""Compare the exact draft subschema syntax to the candidate's stated profile.
This is a source-shape audit, not a formal JSON Schema semantics interpreter.
"""
from pathlib import Path
import hashlib,json,re
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
SCHEMAS=HERE.parent/'K02-pipeline/schemas'

def binding(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def closed(properties):
    return {'type':'object','additionalProperties':False,'required':list(properties),'properties':properties}

def run():
    nonempty={'type':'string','minLength':1}
    revision_key=closed({x:nonempty for x in ['owner','artifact','revision']})
    revision_ref=closed({'key':{'$ref':'#/$defs/revisionKey'},'digest':nonempty})
    ref={'$ref':'#/$defs/revisionRef'}
    ref_array={'type':'array','items':ref}
    role=closed({'ref':ref,'code':nonempty,'subjectKind':{'enum':['agent-assignment','goal','product','product-capability','project','research-inquiry','other']}})
    resolution=closed({**{x:ref for x in ['ref','scope','intent','ownerDecision']},**{x:ref_array for x in ['selectedSubjects','excludedSubjects','satisfactionTests']}})
    assertions=[]
    sources=[]
    for kind,target in [('resolution',resolution),('role',role)]:
        source=SCHEMAS/f'{kind}-binding.schema.json'
        schema=json.loads(source.read_text());Draft202012Validator.check_schema(schema)
        sources.append(binding(source))
        for name,expected in [('revisionKey',revision_key),('revisionRef',revision_ref),('target',target)]:
            assert schema['$defs'][name]==expected,(kind,name)
            assertions.append({'schema':kind,'subschema':name,'exact_expected_shape':True})
    # Verify the key/enum spellings in the actual compiled candidate sources.
    references=(HERE/'BindingReferences.lean').read_text()
    targets=(HERE/'BindingTargets.lean').read_text()
    for text,definition,keys in [(references,'keyKeys',list(revision_key['properties'])),(references,'refKeys',list(revision_ref['properties'])),(targets,'roleKeys',list(role['properties'])),(targets,'resolutionKeys',list(resolution['properties']))]:
        found=re.search(r'def '+definition+r' : List String :=\s*\[([^]]*)\]',text)
        assert found and re.findall(r'"([^"]+)"',found.group(1))==keys,definition
    enum=re.findall(r'\| \.\w+ => "([^"]+)"',targets)
    assert enum==role['properties']['subjectKind']['enum']
    # The epoch component is deliberately not included in the completed AST work.
    # Confirm why a canonical decimal-digit subset would fail whole-schema coverage.
    source=SCHEMAS/'resolution-binding.schema.json'
    schema=json.loads(source.read_text())
    epoch_validator=Draft202012Validator(schema['$defs']['frame']['properties']['epoch'])
    numeric_cases=[]
    for value,expected in [(42,True),(42.0,True),(4.2e1,True),(-0.0,True),(-1,False),(0.5,False),('42',False)]:
        actual=epoch_validator.is_valid(value); assert actual==expected
        numeric_cases.append({'python_value':value,'expected':expected,'actual':actual})
    report={'task':'N01','unit':'K02-binding-ast','result':'candidate-subschemas-source-shape-audit-pass','driver':binding(Path(__file__)),'schemas':sources,'candidate_sources':[binding(HERE/x) for x in ['BindingAstCombinators.lean','BindingReferences.lean','BindingTargets.lean','BindingAstControls.lean']],'exact_shape_assertions':assertions,'numeric_boundary_cases':numeric_cases,'claim_scope':'Exact source-shape agreement for revisionKey, revisionRef, role target and resolution target only. Formal decoders match independently defined local AST meanings. This script does not prove a JSON Schema interpreter or byte-parser translation.','complete_frame_AST_proved':False,'complete_binding_record_AST_proved':False,'schema_AST_correspondence_proved':False,'JSON_schema_semantics_interpreter_proved':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'N03_schema_freeze':False,'inherited_discharges':0}
    (HERE/'subschema-source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'result':report['result'],'shape_assertions':len(assertions),'numeric_boundary_cases':len(numeric_cases)}))

if __name__=='__main__':run()
