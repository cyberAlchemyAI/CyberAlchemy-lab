"""Generate explicit synthetic full-record AST controls; translation is not proved."""
from pathlib import Path
import hashlib,json,copy
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
SCHEMAS=HERE.parent/'K02-pipeline/schemas'
class Lexeme:
    def __init__(self,token):self.token=token

def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def string(s):return json.dumps(s,ensure_ascii=False)
def ast(x):
    if isinstance(x,Lexeme):return f'(.number {string(x.token)})'
    if x is None:return '.null'
    if isinstance(x,bool):return '.boolean '+('true' if x else 'false')
    if isinstance(x,str):return f'(.string {string(x)})'
    if isinstance(x,int):return f'(.number {string(str(x))})'
    if isinstance(x,list):return '(.array ['+', '.join(ast(v) for v in x)+'])'
    if isinstance(x,dict):return object_ast(list(x.items()))
    raise ValueError(x)
def object_ast(items):return '(.object ['+', '.join('('+string(k)+', '+ast(v)+')' for k,v in items)+'])'
def key(x):return '⟨'+','.join(string(x[k]) for k in ['owner','artifact','revision'])+'⟩'
def ref(x):return '⟨'+key(x['key'])+','+string(x['digest'])+'⟩'
def refs(xs):return '['+','.join(ref(x) for x in xs)+']'
def frame(x):return '⟨'+','.join([ref(x[k]) for k in ['profile','subject','target','context','scope','snapshot']]+[str(x['epoch']),string(x['timeDomain'])])+'⟩'
def target(kind,x):
    if kind=='resolution':return '⟨'+','.join([ref(x[k]) for k in ['ref','scope','intent','ownerDecision']]+[refs(x[k]) for k in ['selectedSubjects','excludedSubjects','satisfactionTests']])+'⟩'
    name={'agent-assignment':'agentAssignment','goal':'goal','product':'product','product-capability':'productCapability','project':'project','research-inquiry':'researchInquiry','other':'other'}[x['subjectKind']]
    return '⟨'+ref(x['ref'])+','+string(x['code'])+',.'+name+'⟩'
def record(kind,x):return '⟨'+','.join([string(x['schema_version']),key(x['binding_revision_key']),string(x['kind']),'⟨'+','.join([string(x['body']['token']),target(kind,x['body']['target']),frame(x['body']['frame'])])+'⟩',ref(x['owner_review_ref'])])+'⟩'
def path_get(x,path):
    for p in path:x=x[p]
    return x

def run():
    rows=['import BindingRecord','set_option autoImplicit false','namespace RelationalSuccessor.CandidateBindingRecords.Controls','open RelationalSuccessor','open RelationalSuccessor.CandidateBindingAst','open RelationalSuccessor.CandidateBindingRecords','open RelationalSuccessor.CandidateIntentAddressing (Resolution Role)','']
    names=[];cases=[];sources=[]
    def theorem(name,expr,proof='by decide'):
        rows.extend([f'theorem {name} : {expr} := {proof}','']);names.append(name)
    for kind,typ in [('resolution','Resolution'),('role','Role')]:
        fixture=SCHEMAS/f'{kind}-binding.fixture.json';schema=SCHEMAS/f'{kind}-binding.schema.json'
        original=json.loads(fixture.read_text());sources.extend([binding(fixture),binding(schema)])
        rows.extend([f'def {kind}Ast : J := {ast(original)}',f'def {kind}Expected : Record {typ} := {record(kind,original)}',''])
        theorem(kind+'_original_accepts',f'{kind}Record.decode {kind}Ast = some {kind}Expected')
        def check(name,x,expected='none'):
            theorem(kind+'_'+name,f'{kind}Record.decode {ast(x)} = {expected}')
            cases.append({'name':kind+'_'+name,'expected_acceptance':expected!='none','method':'Explicit mutated AST proof control'})
        # Every required field at the enclosing record, body, frame and typed target.
        for path in [[],['body'],['body','frame'],['body','target']]:
            for field in path_get(original,path):
                x=copy.deepcopy(original);del path_get(x,path)[field]
                check('missing_'+'_'.join(path+[field]),x)
        for path in [[],['body'],['body','frame'],['body','target']]:
            x=copy.deepcopy(original);path_get(x,path)['approval']=True
            check('extra_'+'_'.join(path or ['record']),x)
        for field in ['schema_version','kind']:
            x=copy.deepcopy(original);x[field]='unapproved-alias';check('wrong_'+field,x)
        for field in ['token']:
            x=copy.deepcopy(original);x['body'][field]='';check('empty_'+field,x)
        x=copy.deepcopy(original);x['body']['frame']['timeDomain']='';check('empty_time_domain',x)
        x=copy.deepcopy(original);x['binding_revision_key']['owner']='';check('empty_binding_owner',x)
        x=copy.deepcopy(original);x['owner_review_ref']['digest']='';check('empty_review_digest',x)
        for name,epoch in [('negative_epoch',Lexeme('-1')),('fractional_epoch',Lexeme('42.0000000000000001')),('string_epoch','42'),('malformed_epoch',Lexeme('42e+'))]:
            x=copy.deepcopy(original);x['body']['frame']['epoch']=epoch;check(name,x)
        x=copy.deepcopy(original);x['body']['frame']['epoch']=Lexeme('4.2e1');check('exponent_epoch_accepts',x,f'some {kind}Expected')
        x=copy.deepcopy(original);x['body']['frame']['epoch']=Lexeme('42.0');check('decimal_epoch_accepts',x,f'some {kind}Expected')
        # Retained entry lists can carry duplicates; dictionary fixtures cannot.
        entries=list(original.items())+[('kind',original['kind'])]
        theorem(kind+'_identical_duplicate_kind_refuses',f'{kind}Record.decode {object_ast(entries)} = none')
        entries=list(original['body']['frame'].items())+[('epoch',42)]
        # Replace the nested frame AST directly while retaining the enclosing fields.
        body_ast=object_ast([(k,v) for k,v in original['body'].items() if k!='frame'])
        frame_ast=object_ast(entries)
        body_ast=body_ast[:-2]+', ("frame", '+frame_ast+')])'
        record_ast='(.object ['+', '.join('('+string(k)+', '+(body_ast if k=='body' else ast(v))+')' for k,v in original.items())+'])'
        theorem(kind+'_identical_duplicate_epoch_refuses',f'{kind}Record.decode {record_ast} = none')
        entries=list(reversed(list(original.items())))
        theorem(kind+'_record_key_order_accepts',f'{kind}Record.decode {object_ast(entries)} = some {kind}Expected')
        theorem(kind+'_independent_record_meaning',f'RecordMeaning {kind}Version {kind}Kind {kind} {kind}Ast {kind}Expected',f'({kind}_record_exact {kind}Ast {kind}Expected).mp {kind}_original_accepts')
    rows.extend(f'#print axioms {name}' for name in names)
    rows.extend(['end RelationalSuccessor.CandidateBindingRecords.Controls',''])
    (HERE/'BindingRecordControls.lean').write_text('\n'.join(rows))
    capture={'task':'N01','unit':'K02-binding-records','method':'Python to explicit retained AST and typed fixture literals; this translation is not proved.','generator':binding(Path(__file__)),'model_generator':binding(HERE/'create_model.py'),'sources':sources,'controls':binding(HERE/'BindingRecordControls.lean'),'worked_control_declarations':len(names),'mutation_cases':cases,'captured_context_is_synthetic':True,'binding_record_bytes_are_synthetic':True,'byte_parser_proved':False,'schema_AST_correspondence_proved':False,'authenticated_capture_proved':False,'inherited_discharges':0}
    (HERE/'source-capture.json').write_text(json.dumps(capture,indent=2)+'\n')
    print('worked record controls',len(names))
if __name__=='__main__':run()
