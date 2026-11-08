"""Separate expression witness and source-bound norm activation adapter."""
from pathlib import Path
import json
import sys
from ..p03.context import BASE,C,check,binding,require,UnsupportedProfile,ResourceExhausted
from ..execution.extension_runtime import lean_string,lean_ref
from .evaluator import prepare,evaluate
HERE=Path(__file__).resolve().parent
SCHEMA=HERE/'expression.schema.json'
SCOPE='Full bounded expression under exact supplied leaf assumptions; origin-bearing activation of an independently inspected selected mapped query; no core application authorization.'

def prevalidate(request):
    nodes=0
    def walk(e,depth):
        nonlocal nodes
        nodes+=1
        if nodes>128 or depth>16:raise ResourceExhausted('expression work/depth ceiling')
        if not isinstance(e,dict):return
        op=e.get('op')
        if isinstance(op,str) and op not in ['atom','and','or','not']:raise UnsupportedProfile('unsupported expression operator '+op)
        if op in ['and','or']:walk(e.get('left'),depth+1);walk(e.get('right'),depth+1)
        elif op=='not':walk(e.get('operand'),depth+1)
    if isinstance(request,dict) and 'expression' in request:walk(request['expression'],1)

def normalize(request,ctx):
    keys,values,supports=prepare(request['expression'],request['frame'],request['evaluations'])
    verdict=evaluate(request['expression'],request['frame'],values)
    origins=[];sources=[];mode='none';source_key=None
    if request['mapped'] is not None:
        mapped=request['mapped'];paths=[]
        for field in ['request','result']:
            p=check(mapped[field]);require(p.is_relative_to(BASE) and p.stat().st_size<=ctx.resource_policy['work_limits']['input_bytes'],'mapped source input envelope');paths.append(p);sources.append(mapped[field])
        source_request=C.decode(paths[0].read_bytes());source_result=C.decode(paths[1].read_bytes())
        p=ctx.run_tool([sys.executable,str(BASE/'p04/mapping_worker.py')],input=json.dumps({'request':source_request,'result':source_result}),timeout=ctx.resource_policy['stage_seconds'])
        answer=C.decode(p.stdout.encode());require(p.returncode==0 and answer['ok'],answer.get('error','mapped inspection failed'))
        inspected=answer['value'];require(inspected['variant']=='inheritance' and inspected['verdict']=='yes','only complete yes inheritance potentials may activate')
        source_key=inspected['condition_key']
        frame={k:v for k,v in inspected['condition_key'].items() if k!='condition'}
        require(frame==request['frame'],'expression context/subject/target/scope/epoch differs from mapped source')
        require(inspected['condition_key']['condition']==request['condition'],'expression root condition revision differs from selected mapped condition')
        potentials=inspected['potential_norms'];require(len(potentials)<=256,'potential norm ceiling')
        origins=[json.dumps(n,sort_keys=True,separators=(',',':'),ensure_ascii=False) for n in potentials]
        mode='recorded-current-source-witness'
        sources.append(source_result['dependencies'])
        for m in source_result['kernel_evidence']:sources.extend([m['source'],m['olean']])
        for m in C.decode(check(source_result['dependencies']).read_bytes())['modules']:sources.extend([m['source'],m['olean']])
        for ref in sources:check(ref)
    return {'request':request,'keys':keys,'supports':supports,'verdict':verdict,'origins':origins,
        'active':origins if verdict=='yes' else [],'mapped_mode':mode,'source_bindings':sources,'source_key':source_key}

def modules():return [('ExpressionSemantics',HERE/'ExpressionSemantics.lean')]
def frame_lean(frame):return '⟨'+', '.join([lean_string(frame['profile']),lean_ref(frame['context']),lean_ref(frame['subject']),lean_ref(frame['target']),lean_string(frame['scope']),str(frame['epoch'])])+'⟩'
def expr_lean(e):
    if e['op']=='atom':return '(Expr.atom '+lean_ref(e['condition'])+')'
    if e['op']=='not':return '(Expr.neg '+expr_lean(e['operand'])+')'
    return '(Expr.'+{'and':'conj','or':'disj'}[e['op']]+' '+expr_lean(e['left'])+' '+expr_lean(e['right'])+')'
def render(p):
    r=p['request'];frame=frame_lean(r['frame']);entries=[]
    for support in p['supports']:
        entries.append('(⟨frame, '+lean_ref(support['key']['condition'])+'⟩, Truth.'+support['value']+')')
    origins='['+', '.join(map(lean_string,p['origins']))+']';active='['+', '.join(map(lean_string,p['active']))+']'
    mapped=[]
    if p['source_key'] is not None:
        f={k:v for k,v in p['source_key'].items() if k!='condition'}
        mapped=['def source_frame : Frame := '+frame_lean(f),'def source_condition : Ref := '+lean_ref(p['source_key']['condition']),
            'theorem mapped_frame_exact : frame = source_frame := by decide',
            'theorem mapped_condition_exact : root_condition = source_condition := by decide',
            '#print axioms mapped_frame_exact','#print axioms mapped_condition_exact']
    return '\n'.join(['import ExpressionSemantics','set_option maxRecDepth 2048','open RelationalExtensions.Expression','namespace ExpressionInstance',
        'def frame : Frame := '+frame,'def expression : Expr := '+expr_lean(r['expression']),
        'def root_condition : Ref := '+lean_ref(r['condition']),
        'def entries : List (Key × Truth) := ['+', '.join(entries)+']',
        'def env : Key → Truth := lookup entries','def potentials : List String := '+origins,
        'theorem evaluated : evaluate frame env expression = Truth.'+p['verdict']+' := by decide',
        'theorem activated : active frame env expression potentials = '+active+' := by decide',
        'theorem independent_activation (origin : String) : origin ∈ active frame env expression potentials ↔ origin ∈ potentials ∧ (meaning frame env expression).1 = true := activation_exact frame env expression potentials origin',
        '#print axioms evaluated','#print axioms activated','#print axioms independent_activation',*mapped,'end ExpressionInstance',''])

def result(p):return {'schema':'relational.condition-expression-result/v1','profile':'condition-expression-v1','frame':p['request']['frame'],'condition':p['request']['condition'],
    'definition_identity':C.identity({'condition':p['request']['condition'],'expression':p['request']['expression'],'profile':p['request']['profile']}),
    'expression_identity':C.identity(p['request']['expression']),'verdict':p['verdict'],'leaf_keys':p['keys'],'supports':p['supports'],
    'potential_origins':p['origins'],'active_origins':p['active'],'mapped_proof_mode':p['mapped_mode'],
    'fulfilled':'not-established','admission':'not-derived','truth_boundary':'Supplied exact leaf assessment truth; tested JSON/source bridge; pinned same Lean kernel and host/hash assumptions.',
    'authority_effect':'none','application_authorized':False}
