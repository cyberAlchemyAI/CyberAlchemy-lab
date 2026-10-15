"""Compile the fixed complete schema closure; reject unsupported assertions."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
PRIOR = HERE.parent / 'K02-complete-payload-provider'


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def word(value):
    return json.dumps(value, ensure_ascii=False)


def words(values):
    return '[' + ','.join(map(word, values)) + ']'


def compile_profiles():
    manifest = json.loads((PRIOR / 'profile-manifest.json').read_text())
    emitted, roots, trace = [], [], []
    for row in manifest['profiles']:
        schema_path = ROOT / row['schema']['path']
        assert binding(schema_path) == row['schema']
        schema = json.loads(schema_path.read_text())
        prefix = 'T' + ''.join(piece.title() for piece in row['kind'].split('-'))
        defined = set()

        def compile_rule(rule, path):
            allowed = {'$schema','$id','title','description','$defs','$ref','type','const','enum',
                       'minLength','pattern','items','minItems','maxItems','uniqueItems',
                       'properties','required','additionalProperties','allOf','anyOf'}
            assert not set(rule) - allowed, (row['kind'], path, set(rule) - allowed)
            trace.append({'kind':row['kind'], 'schema_path':path, 'keywords':sorted(rule)})
            if '$ref' in rule:
                assert set(rule) == {'$ref'} and rule['$ref'].startswith('#/$defs/')
                target = schema
                for part in rule['$ref'][2:].split('/'):
                    target = target[part.replace('~1','/').replace('~0','~')]
                return compile_rule(target, path + ['resolved-local',rule['$ref']])
            if 'anyOf' in rule:
                assert set(rule) == {'anyOf'} and len(rule['anyOf']) == 2
                nulls = [item for item in rule['anyOf'] if item == {'type':'null'}]
                nonnull = [item for item in rule['anyOf'] if item != {'type':'null'}]
                assert len(nulls) == len(nonnull) == 1
                typ, decoder, encoder = compile_rule(nonnull[0],path+['anyOf-string'])
                assert typ == 'String'
                trace.append({'kind':row['kind'],'schema_path':path+['anyOf-null'],'keywords':['type']})
                return 'Option String', '(nullable ' + decoder + ')', '(fun value => match value with | none => CandidateJsonSource.Value.null | some text => '+encoder+' text)'
            typ = rule.get('type')
            if typ is None:
                if isinstance(rule.get('const'),str) or 'enum' in rule:
                    typ = 'string'
                elif isinstance(rule.get('const'),list):
                    typ = 'array'
            if typ == 'string':
                assert set(rule) <= {'type','const','enum','minLength','pattern','description'}
                constant = 'none' if 'const' not in rule else '(some '+word(rule['const'])+')'
                choices = 'none' if 'enum' not in rule else '(some '+words(rule['enum'])+')'
                if 'enum' in rule:
                    assert all(isinstance(value,str) for value in rule['enum'])
                pattern = {'\\S':'(some .nonWhitespace)',
                           '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$':'(some .timestamp)'}
                assert 'pattern' not in rule or rule['pattern'] in pattern
                return 'String', '(stringProfile '+str(rule.get('minLength',0))+' '+constant+' '+choices+' '+pattern.get(rule.get('pattern'),'none')+')', 'CandidateJsonSource.Value.string'
            if typ == 'array':
                assert set(rule) <= {'type','const','items','minItems','maxItems','uniqueItems','description'}
                item = rule.get('items',{'type':'string'})
                child_type, child_decoder, child_encoder = compile_rule(item,path+['items'])
                maximum = 'none' if 'maxItems' not in rule else '(some '+str(rule['maxItems'])+')'
                expression = '(boundedArray '+child_decoder+' '+str(rule.get('minItems',0))+' '+maximum+' '+str(rule.get('uniqueItems',False)).lower()+')'
                if 'const' in rule:
                    assert child_type == 'String' and all(isinstance(value,str) for value in rule['const'])
                    expression = '(constrained '+expression+' (fun values => values = '+words(rule['const'])+'))'
                return 'List ('+child_type+')', expression, '(fun values => CandidateJsonSource.Value.array (values.map '+child_encoder+'))'
            assert typ == 'object', (row['kind'],path,rule)
            assert rule['additionalProperties'] is False
            properties = rule['properties']
            assert len(rule['required']) == len(set(rule['required']))
            assert set(properties) == set(rule['required'])
            assert set(rule) <= {'$schema','$id','title','description','$defs','type',
                                 'properties','required','additionalProperties','allOf'}
            name = prefix + ''.join('_'+re.sub('[^a-zA-Z0-9_]','_',str(part)) for part in path)
            fields = [(key,*compile_rule(subrule,path+[key])) for key,subrule in properties.items()]
            assert name not in defined
            defined.add(name)
            lines = ['structure '+name+' where']
            lines += ['  '+key+' : '+child_type for key,child_type,_,_ in fields]
            lines += ['  deriving DecidableEq, Repr','']
            chain = 'CandidateBindingAst.empty'
            for _,_,decoder,_ in reversed(fields):
                chain = '(CandidateBindingAst.cons '+decoder+' '+chain+')'
            projections = ['p.'+'.'.join(['2']*index+['1']) for index in range(len(fields))]
            lines += ['def '+name+'.fields : CandidateBindingAst.Fields '+name+' :=',
                      '  CandidateBindingAst.mapFields '+chain,
                      '    (fun p => '+name+'.mk '+' '.join(projections)+')',
                      'def '+name+'.rawDecoder : CandidateBindingAst.Decoder '+name+' :=',
                      '  CandidateBindingAst.object '+words(list(properties))+' '+name+'.fields']
            conditions = []
            for index, clause in enumerate(rule.get('allOf',[])):
                assert set(clause) == {'if','then'}
                test, conclusion = clause['if'], clause['then']
                assert set(test) == {'properties','required'} and len(test['properties']) == 1
                field, predicate = next(iter(test['properties'].items()))
                assert test['required'] == [field] and field in properties and set(predicate) == {'const'}
                assert set(conclusion) == {'properties'} and len(conclusion['properties']) == 1
                affected, bound = next(iter(conclusion['properties'].items()))
                assert affected in properties and set(bound) == {'minItems'}
                conditions.append('(value.'+field+' = '+word(predicate['const'])+' → '+str(bound['minItems'])+' ≤ value.'+affected+'.length)')
                trace.append({'kind':row['kind'],'schema_path':path+['allOf',index],
                              'keywords':['if','then','properties','required','const','minItems'],
                              'condition_field':field,'constrained_array':affected})
            condition = ' ∧ '.join(conditions) if conditions else 'True'
            lines += ['def '+name+'.Conditions ('+('value' if conditions else '_value')+' : '+name+') : Prop := '+condition,
                      'instance : DecidablePred '+name+'.Conditions := fun value => by',
                      '  unfold '+name+'.Conditions','  infer_instance',
                      'def '+name+'.decoder : CandidateBindingAst.Decoder '+name+' :=',
                      '  constrained '+name+'.rawDecoder '+name+'.Conditions',
                      'def '+name+'.Meaning (value : CandidateBindingAst.J) (output : '+name+') : Prop :=',
                      '  CandidateBindingAst.ObjectMeaning '+words(list(properties))+' '+name+'.fields value output ∧ '+name+'.Conditions output',
                      'def '+name+'.toAst (value : '+name+') : CandidateBindingAst.J :=',
                      '  .object ['+','.join('('+word(key)+','+encoder+' value.'+key+')' for key,_,_,encoder in fields)+']','']
            emitted.extend(lines)
            return name, name+'.decoder', name+'.toAst'

        root_type, decoder, _encoder = compile_rule(schema,[])
        roots.append((row,root_type,decoder))
    text = 'import BodyStringProfiles\nset_option autoImplicit false\nset_option maxRecDepth 65536\nset_option maxHeartbeats 10000000\nnamespace RelationalSuccessor.CandidateTypedBodies\n\n'
    text += '\n'.join(emitted)
    text += '\ninductive Kind where\n' + ''.join('  | '+row['kind'].replace('-','_')+'\n' for row,_,_ in roots) + '  deriving DecidableEq, Repr\n'
    text += '\ninductive Body where\n' + ''.join('  | '+row['kind'].replace('-','_')+' (value : '+typ+')\n' for row,typ,_ in roots) + '  deriving DecidableEq, Repr\n'
    text += '\ndef decoderForKind : Kind → CandidateBindingAst.Decoder Body\n'
    text += ''.join('  | .'+row['kind'].replace('-','_')+' => mapped '+decoder+' Body.'+row['kind'].replace('-','_')+'\n' for row,_,decoder in roots)
    text += '\ndef Body.toAst : Body → CandidateBindingAst.J\n'
    text += ''.join('  | .'+row['kind'].replace('-','_')+' value => '+typ+'.toAst value\n' for row,typ,_ in roots)
    text += '\ndef Body.identity : Body → String\n'
    text += ''.join('  | .'+row['kind'].replace('-','_')+' value => value.'+row['identity_field']+'\n' for row,_,_ in roots)
    for row,typ,decoder in roots:
        short = row['kind'].replace('-','_')+'_complete_record_exact'
        text += '\ntheorem '+short+' (value : CandidateBindingAst.J) (output : '+typ+') :\n'
        text += '    '+decoder+'.decode value = some output ↔ '+typ+'.Meaning value output :=\n'
        text += '  '+decoder+'.exact value output\n'
    text += '\n'+''.join('#print axioms '+row['kind'].replace('-','_')+'_complete_record_exact\n' for row,_,_ in roots)
    text += 'end RelationalSuccessor.CandidateTypedBodies\n'
    return text,trace,roots


def run():
    text,trace,roots = compile_profiles()
    (HERE/'CompleteBodyProfiles.lean').write_text(text)
    report = {'task':'N01','unit':HERE.name,'result':'complete-pinned-schema-generation-pass',
              'generator':binding(Path(__file__)), 'manifest':binding(PRIOR/'profile-manifest.json'),
              'formalization':binding(HERE/'FORMALIZATION.md'),
              'generated_source':binding(HERE/'CompleteBodyProfiles.lean'),
              'profile_count':len(roots), 'root_record_types':[typ for _,typ,_ in roots],
              'complete_record_field_count':len(re.findall(r'^  \w+ : ',text,re.M)),
              'record_type_count':len(re.findall(r'^structure ',text,re.M)),
              'assertion_trace':trace,'active_assertion_nodes':len(trace),
              'unsupported_assertions_ignored':False,'all_declared_properties_required_verified':True,
              'general_schema_compiler_correspondence_proved':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'generation-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['result','profile_count','complete_record_field_count','record_type_count','active_assertion_nodes']},indent=2))


if __name__ == '__main__':
    run()
