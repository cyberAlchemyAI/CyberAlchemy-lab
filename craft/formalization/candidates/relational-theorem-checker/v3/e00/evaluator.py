"""Bounded Strong Kleene expression evaluation after complete key validation."""
import copy
from ..p03.context import C,require,ResourceExhausted

def leaf_keys(expression,frame):
    keys=[];nodes=0
    def walk(e,depth):
        nonlocal nodes
        nodes+=1
        if nodes>128 or depth>16:raise ResourceExhausted('expression work/depth ceiling')
        if e['op']=='atom':
            key={**copy.deepcopy(frame),'condition':copy.deepcopy(e['condition'])}
            if key not in keys:keys.append(key)
            if len(keys)>64:raise ResourceExhausted('expression leaf ceiling')
        elif e['op'] in ['and','or']:walk(e['left'],depth+1);walk(e['right'],depth+1)
        elif e['op']=='not':walk(e['operand'],depth+1)
        else:raise ValueError('unsupported expression operator')
    walk(expression,1);return keys

def prepare(expression,frame,evaluations):
    require(type(frame['epoch']) is int,'Boolean/noncanonical epoch is not natural')
    keys=leaf_keys(expression,frame);values={};supports=[]
    for entry in evaluations:
        require(type(entry['key']['epoch']) is int,'Boolean/noncanonical leaf epoch')
        require(entry['key'] in keys,'supplied leaf has wrong revision/frame or is outside expression')
        identity=C.identity(entry['key'])
        require(identity not in values,'duplicate or contradictory leaf evidence')
        values[identity]=entry['value'];supports.append(copy.deepcopy(entry))
    return keys,values,supports

def evaluate(expression,frame,values):
    op=expression['op']
    if op=='atom':return values.get(C.identity({**frame,'condition':expression['condition']}),'unknown')
    if op=='not':return {'yes':'no','no':'yes','unknown':'unknown'}[evaluate(expression['operand'],frame,values)]
    left=evaluate(expression['left'],frame,values);right=evaluate(expression['right'],frame,values)
    if op=='and':return 'no' if 'no' in (left,right) else 'yes' if left==right=='yes' else 'unknown'
    if op=='or':return 'yes' if 'yes' in (left,right) else 'no' if left==right=='no' else 'unknown'
    raise ValueError('unsupported expression operator')
