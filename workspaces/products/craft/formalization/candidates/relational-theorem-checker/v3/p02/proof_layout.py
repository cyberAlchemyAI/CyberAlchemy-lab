"""Structured concrete witness generation; no source-marker splitting."""
from dataclasses import dataclass
import json
import re


def literal(value):
    if not isinstance(value,str): raise ValueError('Lean text must be a string')
    if any(0xD800 <= ord(c) <= 0xDFFF for c in value): raise ValueError('invalid Unicode scalar')
    return '(String.ofList ['+', '.join('(Char.ofNat '+str(ord(c))+')' for c in value)+'])'


def rows(values,fn): return '['+', '.join(fn(v) for v in values)+']'
def key(k): return '{ id := '+literal(k['id'])+', version := '+literal(k['version'])+', hash := '+literal(k['hash'])+' }'
def value(v):
    if v['kind']=='reference': return '(.reference '+literal(v['id'])+' '+literal(v['version'])+')'
    if v['kind']=='epoch':
        if type(v['value'])!=int or v['value']<0: raise ValueError('invalid natural epoch')
        return '(.epoch '+str(v['value'])+')'
    if v['kind'] not in ['effect','scope','text']: raise ValueError('unknown value sort')
    return '(.'+v['kind']+' '+literal(v['value'])+')'
def atom(a): return '{ predicate := '+key(a['predicate'])+', values := '+rows(a['values'],value)+' }'
def pattern(p):
    def term(t): return '(.slot '+str(t['slot'])+')' if 'slot' in t else '(.constant '+value(t['constant'])+')'
    return '{ predicate := '+key(p['predicate'])+', terms := '+rows(p['terms'],term)+' }'
def rule(r): return '{ key := '+key(r)+', variables := '+rows(r['variables'],lambda v:'.'+v['sort'])+', head := '+pattern(r['head'])+', body := '+rows(r['body'],pattern)+' }'
def theory(n):
    roles={'ordinary':'ordinary','protected':'protectedConclusion','checked-root':'checkedRoot','root-carrier':'rootCarrier'}
    def pred(p): return '{ key := '+key(p)+', sorts := '+rows(p['sorts'],lambda x:'.'+x)+', role := .'+roles[p['role']]+' }'
    return '{ domain := '+rows(n['domain'],value)+', predicates := '+rows(n['predicates'],pred)+', rules := '+rows(n['rules'],rule)+', roots := '+rows(n['roots'],lambda r:rows(r['values'],value))+', epoch := '+str(n['snapshot_epoch'])+' }'
def instance(i): return '{ rule := '+key(i['rule'])+', substitution := '+rows(i['substitution'],value)+', head := '+atom(i['head'])+', body := '+rows(i['body'],atom)+' }'
def step(s):
    if s['kind']=='base': return '(.base '+atom(s['conclusion'])+')'
    if s['kind']!='apply': raise ValueError('unknown certificate step')
    return '(.apply '+instance(s['instance'])+' '+rows(s['indices'],str)+')'


@dataclass(frozen=True)
class Section:
    role: str
    text: str


NAMESPACE='Successor.Runtime.Actual'
PREFIX='set_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace '+NAMESPACE+'\nopen Inference Inference.Extension\n'
END='end '+NAMESPACE+'\n'


def sections(old,new,evaluation):
    sealed=[{k:next(p for p in new['predicates'] if p['id']==id)[k] for k in ['id','version','hash']} for id in ['ConformsTo','TargetKind','Conforms']]
    data='def before : Theory := '+theory(old)+'\ndef after : Theory := '+theory(new)+'\ndef facts : List Atom := '+rows(new['facts'],atom)+'\ndef C : List Atom := '+rows(evaluation['closure'],atom)+'\ndef steps : List Step := '+rows(evaluation['steps'],step)+'\ndef sealed : List Key := '+rows(sealed,key)+'\n'
    typed='theorem before_valid : TheoryValid before := by decide\ntheorem after_valid : TheoryValid after := by decide\ntheorem initial_valid : InitialValid after facts := by decide\ntheorem lineage_valid : checkLineage after facts = true := by decide\ntheorem sealed_heads : Producer.checkHeads after sealed = true := by decide\n'
    closure='theorem complete_closure : checkClosure after facts C [steps] = true := by decide\n'
    expansion='def added := (groundInstances after).filter fun i => decide (¬ Old before i.head)\ndef extension : Recursive.CheckedExtension before after := {\n'
    expansion+='fresh := after.predicates.drop '+str(len(old['predicates']))+', addedRules := after.rules.drop '+str(len(old['rules']))+', added := added,domain_same := by decide,predicates_append := by decide,rules_append := by decide,roots_same := by decide,epoch_same := by decide,fresh_keys := by decide,fresh_ordinary := by decide,cover := by decide,old_bodies := by decide,fresh_heads := by decide,head_typed := by decide,head_roots := by decide,added_valid := by decide,producer_safe := by decide }\n'
    expansion+='theorem actual_expansion : ∀ F M, SemanticModel before F M → ∃ N, SemanticModel after F N ∧ ∀ a, Old before a → (N a ↔ M a) := Recursive.every_old_model_expands before after extension\n'
    expansion+='theorem closure_exact : ∀ a, a ∈ C ↔ Derivable after facts a := checked_closure_exact complete_closure\n'
    for t in ['before_valid','after_valid','initial_valid','lineage_valid','sealed_heads','complete_closure','actual_expansion','closure_exact']:
        expansion+='#print axioms '+t+'\n'
    return (Section('data',data),Section('typed',typed),Section('closure',closure),Section('expansion',expansion))


def render(old,new,evaluation,layout,stem):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',stem): raise ValueError('invalid module stem')
    parts=sections(old,new,evaluation)
    if layout=='combined':
        return [('combined',stem,'import RuntimeProofs\n'+PREFIX+''.join(p.text for p in parts)+END)]
    if layout!='staged': raise ValueError('unknown proof layout')
    result=[]
    suffix={'data':'Data','typed':'Typed','closure':'Closure','expansion':'Expansion'}
    predecessor='RuntimeProofs'
    for p in parts:
        name=stem+'_'+suffix[p.role]
        result.append((p.role,name,'import '+predecessor+'\n'+PREFIX+p.text+END))
        predecessor=name
    return result
