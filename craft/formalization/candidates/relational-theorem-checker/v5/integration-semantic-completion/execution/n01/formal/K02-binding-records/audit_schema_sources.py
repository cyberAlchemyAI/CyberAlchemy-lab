"""Compare full draft syntax and compiled spellings; no Schema interpreter proof."""
from pathlib import Path
import copy,hashlib,json,re
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
SCHEMAS=HERE.parent/'K02-pipeline/schemas'
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def closed(props):return {'type':'object','additionalProperties':False,'required':list(props),'properties':props}
def run():
    text=(HERE/'BindingRecord.lean').read_text();ft=(HERE/'BindingFrame.lean').read_text()
    bt=(HERE.parent/'K02-binding-ast/BindingTargets.lean').read_text();rt=(HERE.parent/'K02-binding-ast/BindingReferences.lean').read_text()
    nonempty={'type':'string','minLength':1};ref={'$ref':'#/$defs/revisionRef'}
    key=closed({x:nonempty for x in ['owner','artifact','revision']})
    reference=closed({'key':{'$ref':'#/$defs/revisionKey'},'digest':nonempty})
    frame=closed({**{x:ref for x in ['profile','subject','target','context','scope','snapshot']},'epoch':{'type':'integer','minimum':0},'timeDomain':nonempty})
    role=closed({'ref':ref,'code':nonempty,'subjectKind':{'enum':['agent-assignment','goal','product','product-capability','project','research-inquiry','other']}})
    resolution=closed({**{x:ref for x in ['ref','scope','intent','ownerDecision']},**{x:{'type':'array','items':ref} for x in ['selectedSubjects','excludedSubjects','satisfactionTests']}})
    body=closed({'token':nonempty,'target':{'$ref':'#/$defs/target'},'frame':{'$ref':'#/$defs/frame'}})
    comparisons=[];cases=[];sources=[];fixtures=[]
    for kind,target in [('resolution',resolution),('role',role)]:
        p=SCHEMAS/f'{kind}-binding.schema.json';schema=json.loads(p.read_text());Draft202012Validator.check_schema(schema);sources.append(binding(p))
        assert set(schema)=={'$schema','$id','description','$defs','type','additionalProperties','required','properties'},kind
        assert set(schema['$defs'])=={'revisionKey','revisionRef','frame','target'},kind
        version=re.search(r'def '+kind+r'Version : String := "([^"]+)"',text).group(1)
        kind_const=re.search(r'def '+kind+r'Kind : String := "([^"]+)"',text).group(1)
        root=closed({'schema_version':{'const':version},'binding_revision_key':{'$ref':'#/$defs/revisionKey'},'kind':{'const':kind_const},'body':body,'owner_review_ref':ref})
        for name,actual,expected in [('revisionKey',schema['$defs']['revisionKey'],key),('revisionRef',schema['$defs']['revisionRef'],reference),('frame',schema['$defs']['frame'],frame),('target',schema['$defs']['target'],target),('body',schema['properties']['body'],body),('root',{k:schema[k] for k in root},root)]:
            assert actual==expected,(kind,name)
            comparisons.append({'schema':kind,'subschema':name,'exact_expected_shape':True})
        fixture=SCHEMAS/f'{kind}-binding.fixture.json';fixtures.append(binding(fixture));original=json.loads(fixture.read_text());validator=Draft202012Validator(schema)
        samples=[('original',original,True)]
        for path in [[],['body'],['body','frame'],['body','target']]:
            obj=original
            for x in path:obj=obj[x]
            for field in obj:
                val=copy.deepcopy(original);obj2=val
                for x in path:obj2=obj2[x]
                del obj2[field];samples.append(('missing_'+'_'.join(path+[field]),val,False))
            val=copy.deepcopy(original);obj2=val
            for x in path:obj2=obj2[x]
            obj2['approval']=True;samples.append(('extra_'+'_'.join(path or ['record']),val,False))
        for field in ['schema_version','kind']:
            val=copy.deepcopy(original);val[field]='unapproved-alias';samples.append(('wrong_'+field,val,False))
        for name,epoch,expected in [('negative_epoch',-1,False),('fractional_epoch',0.5,False),('string_epoch','42',False),('integer_decimal_epoch',42.0,True),('integer_exponent_epoch',4.2e1,True)]:
            val=copy.deepcopy(original);val['body']['frame']['epoch']=epoch;samples.append((name,val,expected))
        val=copy.deepcopy(original)
        if kind=='role':val['body']['target']['subjectKind']='other'
        else:val['body']['target']['selectedSubjects']=[]
        samples.append(('syntax_valid_without_relation_qualification',val,True))
        for name,val,expected in samples:
            actual=validator.is_valid(val);assert actual==expected,(kind,name)
            cases.append({'schema':kind,'case':name,'expected':expected,'actual':actual,'value_sha256':hashlib.sha256(json.dumps(val,sort_keys=True).encode()).hexdigest()})
    for source,definition,keys in [(rt,'keyKeys',list(key['properties'])),(rt,'refKeys',list(reference['properties'])),(bt,'roleKeys',list(role['properties'])),(bt,'resolutionKeys',list(resolution['properties'])),(ft,'frameKeys',list(frame['properties'])),(text,'bodyKeys',list(body['properties'])),(text,'recordKeys',list(root['properties']))]:
        m=re.search(r'def '+definition+r' : List String :=\s*\[([^]]*)\]',source);assert m and re.findall(r'"([^"]+)"',m.group(1))==keys,definition
    assert re.findall(r'\| \.\w+ => "([^"]+)"',bt)==role['properties']['subjectKind']['enum']
    v=json.loads((HERE/'verification.json').read_text());assert v['complete_binding_record_AST_proved'] and v['complete_frame_AST_proved']
    report={'task':'N01','unit':'K02-binding-records','result':'candidate-full-binding-schema-source-shape-audit-pass','driver':binding(Path(__file__)),'verification':binding(HERE/'verification.json'),'schemas':sources,'fixtures':fixtures,'candidate_sources':[binding(HERE/'BindingRecord.lean'),binding(HERE/'BindingFrame.lean'),binding(HERE.parent/'K02-binding-ast/BindingReferences.lean'),binding(HERE.parent/'K02-binding-ast/BindingTargets.lean')],'exact_shape_assertions':comparisons,'case_count':len(cases),'cases':cases,'worked_proof_controls':84,'claim_scope':'Complete source-shape comparison and ordinary syntax corpus only. Independent AST denotation proofs are kernel checked separately. Numeric Python cases are illustrative; exact retained-lexeme proofs avoid Python float normalization. Duplicate keys require retained AST controls and are not assessed by dictionary-based Schema validation.','binding_schema_AST_correspondence_proved':False,'JSON_schema_semantics_interpreter_proved':False,'byte_parser_proved':False,'authenticated_capture_proved':False,'N03_schema_freeze':False,'inherited_discharges':0}
    (HERE/'full-schema-source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'result':report['result'],'shape_comparisons':len(comparisons),'cases':len(cases)}))
if __name__=='__main__':run()
