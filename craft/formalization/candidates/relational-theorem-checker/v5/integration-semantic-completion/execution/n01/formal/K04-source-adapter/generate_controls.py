"""Targeted complete-schema controls and explicitly synthetic semantic joins."""
from pathlib import Path
import copy, hashlib, json
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'authority/artifact-types').is_dir())
def binding(path):
    return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def ast(value):
    if value is None:return '.null'
    if isinstance(value,bool):return '(.boolean '+str(value).lower()+')'
    if isinstance(value,str):return '(.string '+json.dumps(value,ensure_ascii=False)+')'
    if isinstance(value,(int,float)):return '(.number '+json.dumps(str(value))+')'
    if isinstance(value,list):return '(.array ['+','.join(ast(v) for v in value)+'])'
    return '(.object ['+','.join('('+json.dumps(k)+','+ast(v)+')' for k,v in value.items())+'])'
def at(value,path):
    for key in path:value=value[key]
    return value
def replace(value,path,replacement):
    result=copy.deepcopy(value)
    if not path:return replacement
    at(result,path[:-1])[path[-1]]=replacement
    return result
def walk(rule,value,path=()):
    yield rule,value,path
    if rule.get('type')=='object':
        for key,subrule in rule['properties'].items():yield from walk(subrule,value[key],path+(key,))
    elif rule.get('type')=='array' and value:
        yield from walk(rule['items'],value[0],path+(0,))

def generate():
    manifest=json.loads((HERE/'profile-manifest.json').read_text())
    cases=[]
    def case(name,expression,expected,category):
        cases.append({'name':name,'expression':expression,'expected':expected,'category':category})
    for profile in manifest['profiles']:
        kind=profile['kind']
        schema=json.loads((ROOT/profile['schema']['path']).read_text())
        validator=Draft202012Validator(schema)
        baseline=json.loads((ROOT/profile['positive_fixture']['path']).read_text())
        def shape(name,value):
            expression='(decoderForKind .'+kind.replace('-','_')+').decode '+ast(value)
            case(kind+'/'+name,'('+expression+').isSome',validator.is_valid(value),'complete-schema')
        shape('original-positive',baseline)
        for negative in profile['negative_fixtures']:
            shape('original-'+Path(negative['path']).stem,json.loads((ROOT/negative['path']).read_text()))
        for rule,value,path in walk(schema,baseline):
            label='/'.join(map(str,path)) or 'root'
            if rule.get('type')=='object':
                for key in rule['required']:
                    modified=copy.deepcopy(baseline)
                    del at(modified,path)[key]
                    shape(label+'/missing-'+key,modified)
                extended={**value,'undeclared-extra':'value'}
                shape(label+'/extra',replace(baseline,path,extended))
            if rule.get('type')=='array':
                shape(label+'/empty',replace(baseline,path,[]))
                element=value[0] if value else 'synthetic-item'
                shape(label+'/duplicate',replace(baseline,path,[element,element]))
                shape(label+'/wrong-item',replace(baseline,path,[7]))
            if rule.get('type')=='string' or 'const' in rule or 'enum' in rule:
                shape(label+'/empty-string',replace(baseline,path,''))
                shape(label+'/whitespace-string',replace(baseline,path,' '))
                shape(label+'/wrong-type',replace(baseline,path,7))
    app=json.loads((ROOT/manifest['profiles'][0]['positive_fixture']['path']).read_text())
    lesson=json.loads((ROOT/manifest['profiles'][1]['positive_fixture']['path']).read_text())
    app.update(node_id='application',owner_ref='owner',scope_ref='scope')
    app['payload'].update(lesson_revision_ref='lesson',session_ref='session',
        application_posture='used',applicability_assessment_ref='assessment',
        conflict_refs=['conflict'],override_refs=['override'])
    app['relation_refs']=[{'relation_kind_ref':'relation.applies-lesson','direction':'source',
        'counterpart_kind':'operational-lesson','counterpart_ref':'lesson'}]
    lesson.update(node_id='lesson')
    q={'lesson_revision_ref':'lesson','application_posture':'used',
        'applicability_assessment_ref':'assessment','instruction_precedence':'policy'}
    bundle={'application':app,'lesson':lesson,'qualifiers':q}
    def semantic(name,value,expected=True,resolution='resolution',claim='C.used',world=None):
        world=world or '(C.world '+claim+')'
        case(name,'sourceCheck '+resolution+' '+world+' '+claim+' '+ast(value),expected,'source-join')
    semantic('synthetic-qualified-use',bundle)
    nonuse=copy.deepcopy(bundle)
    nonuse['application']['payload']['application_posture']='declined'
    nonuse['qualifiers']['application_posture']='declined'
    semantic('synthetic-qualified-non-use',nonuse,claim='C.declined')
    for name,path,value in [
        ('lesson-mismatch',('application','payload','lesson_revision_ref'),'other'),
        ('session-mismatch',('application','payload','session_ref'),'other'),
        ('target-mismatch',('lesson','node_id'),'other'),
        ('owner-mismatch',('application','owner_ref'),'other'),
        ('scope-mismatch',('application','scope_ref'),'other'),
        ('posture-mismatch',('application','payload','application_posture'),'declined'),
        ('assessment-mismatch',('application','payload','applicability_assessment_ref'),'other'),
        ('conflicts-mismatch',('application','payload','conflict_refs'),[]),
        ('overrides-mismatch',('application','payload','override_refs'),[]),
        ('qualifier-lesson-mismatch',('qualifiers','lesson_revision_ref'),'other'),
        ('qualifier-posture-mismatch',('qualifiers','application_posture'),'declined'),
        ('qualifier-assessment-mismatch',('qualifiers','applicability_assessment_ref'),'other'),
        ('qualifier-policy-mismatch',('qualifiers','instruction_precedence'),'other'),
        ('counterpart-mismatch',('application','relation_refs',0,'counterpart_ref'),'other'),
        ('counterpart-direction-mismatch',('application','relation_refs',0,'direction'),'target'),
        ('unknown-policy-token',('qualifiers','instruction_precedence'),'unmapped-policy')]:
        semantic(name,replace(bundle,path,value),False)
    semantic('absent-token-provider',bundle,False,resolution='emptyResolution')
    semantic('ambiguous-token-provider',bundle,False,resolution='ambiguousResolution')
    semantic('label-alone',bundle,False,world='{ C.world C.used with evidence := [] }')
    semantic('missing-assessment-record',bundle,False,world='{ C.world C.used with assessments := [] }')
    for posture in ['selected','presented']:
        value=copy.deepcopy(bundle)
        value['application']['payload']['application_posture']=posture
        value['qualifiers']['application_posture']=posture
        semantic(posture+'-insufficient',value,False,claim='(C.claim .'+posture+')')
    for key in q:
        value=copy.deepcopy(bundle);del value['qualifiers'][key]
        semantic('missing-qualifier-'+key,value,False)
    value=copy.deepcopy(bundle);value['qualifiers']['extra']='value'
    semantic('extra-qualifier',value,False)
    (HERE/'synthetic-source-models.json').write_text(json.dumps({'synthetic':True,'use':bundle,'non_use':nonuse,'owned_mapping_is_real':False},indent=2)+'\n')
    prelude='''import LessonSourceAdapter
import LessonUseControls
set_option autoImplicit false
set_option maxRecDepth 65536
set_option maxHeartbeats 10000000
namespace RelationalSuccessor.CandidateLessonSource
def resolution : Resolution :=
  ⟨[('''+','.join('('+json.dumps(name)+', C.ref '+json.dumps(name)+')' for name in ['application','lesson','session','owner','scope','assessment','policy','conflict','override','other'])+''')],
    [("used", .used), ("declined", .declined), ("selected", .selected), ("presented", .presented)]⟩
def emptyResolution : Resolution := ⟨[], []⟩
def ambiguousResolution : Resolution :=
  { resolution with references := resolution.references ++ [("lesson", C.ref "other")] }
'''
    # The initial list opener is already in the prelude; remove its extra tuple parens.
    prelude=prelude.replace('⟨[(', '⟨[').replace(')],\n    [("used"', '],\n    [("used"')
    prelude=prelude.replace('C.', 'CandidateLessonUse.Controls.')
    for row in cases:
        row['expression']=row['expression'].replace('C.', 'CandidateLessonUse.Controls.')
    text=prelude+'\n'+'\n'.join('#eval '+row['expression'] for row in cases)+'\nend RelationalSuccessor.CandidateLessonSource\n'
    return text,cases
if __name__=='__main__':
    text,cases=generate()
    (HERE/'LessonSourceControls.lean').write_text(text)
    report={'result':'generated-targeted-k04-controls','generator':binding(Path(__file__)),
        'source':binding(HERE/'LessonSourceControls.lean'),'runtime_cases':cases,
        'independent_expectation':'Draft202012Validator for complete shape; declared targeted synthetic join cases for semantics',
        'runtime_control_is_theorem':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'control-index.json').write_text(json.dumps(report,indent=2)+'\n')
    print({'runtime_controls':len(cases),'complete_shape':sum(c['category']=='complete-schema' for c in cases),'source_join':sum(c['category']=='source-join' for c in cases)})
