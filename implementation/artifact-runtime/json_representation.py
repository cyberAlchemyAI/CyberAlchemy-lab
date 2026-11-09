"""Schema-selected JSON data codecs. All representation rules are explicit input.

No domain field names, enum cases, defaults, decisions, expression evaluation,
external schema resolution, callbacks or filesystem behavior live in this module.
"""
from copy import deepcopy
from exact_io import decode, encode, pointer, require, Refusal
from json_construction import construct, uint, variant

def closed_schema(value):
    """Check schema nodes; instance literals and property names are ordinary data."""
    if not isinstance(value,dict):return
    for keyword in ('$ref','$dynamicRef','$recursiveRef'):
        if keyword in value:
            reference=value[keyword]
            require(isinstance(reference,str) and reference.startswith('#'),'external-schema-resolution-disabled')
    for keyword in ('$defs','definitions','properties','patternProperties','dependentSchemas','dependencies'):
        children=value.get(keyword)
        if isinstance(children,dict):
            for child in children.values():closed_schema(child)
    for keyword in ('additionalProperties','unevaluatedProperties','propertyNames','items','additionalItems','contains','unevaluatedItems','not','if','then','else','contentSchema'):
        child=value.get(keyword)
        if isinstance(child,list):
            for item in child:closed_schema(item)
        else:closed_schema(child)
    for keyword in ('allOf','anyOf','oneOf','prefixItems'):
        children=value.get(keyword)
        if isinstance(children,list):
            for child in children:closed_schema(child)


def remove(value, selector):
    require(isinstance(selector, str) and selector.startswith('/'), 'invalid-codec-removal')
    prefix, _, name=selector.rpartition('/')
    parent=pointer(value, prefix)
    name=name.replace('~1','/').replace('~0','~')
    require(isinstance(parent, dict) and name in parent, 'codec-removal-missing')
    del parent[name]

def represent(value, plan):
    from jsonschema import Draft202012Validator
    require(isinstance(plan,dict) and set(plan)=={'rules','opaque_fields'},'invalid-representation-plan')
    require(isinstance(plan['rules'],list) and len(plan['rules'])<=100,'representation-rule-bound')
    require(isinstance(plan['opaque_fields'],list) and len(plan['opaque_fields'])<=100 and all(isinstance(x,str) for x in plan['opaque_fields']),'invalid-opaque-fields')
    compiled=[]
    for rule in plan['rules']:
        require(isinstance(rule,dict) and set(rule)=={'schema','actions'} and isinstance(rule['schema'],str),'invalid-representation-rule')
        schema=decode(rule['schema'].encode());closed_schema(schema);Draft202012Validator.check_schema(schema)
        require(isinstance(rule['actions'],list) and len(rule['actions'])<=100,'representation-action-bound')
        compiled.append((Draft202012Validator(schema),rule['actions']))
    count=0
    def walk(node,depth=0):
        nonlocal count
        count+=1
        require(depth<=64 and count<=262144,'representation-tree-bound')
        if isinstance(node,dict):
            node={key:deepcopy(child) if key in plan['opaque_fields'] else walk(child,depth+1) for key,child in node.items()}
        elif isinstance(node,list):node=[walk(child,depth+1) for child in node]
        for validator,actions in compiled:
            if not validator.is_valid(node):continue
            for action in actions:
                tag,fields=variant(action)
                if tag=='Project':
                    require(set(fields)=={'steps'},'invalid-codec-project')
                    node,_=construct([fields['steps']],{'input':node})
                    continue
                if tag=='Unwrap':
                    require(set(fields)=={'selector'},'invalid-codec-unwrap')
                    node=deepcopy(pointer(node,fields['selector']))
                    continue
                if tag=='Remove':
                    require(set(fields)=={'selector'},'invalid-codec-remove');remove(node,fields['selector']);continue
                require(isinstance(node,dict),'codec-record-required')
                if tag=='FieldUnwrap':
                    require(set(fields)=={'field','selector'} and fields['field'] in node,'invalid-codec-field-unwrap')
                    node[fields['field']]=deepcopy(pointer(node[fields['field']],fields['selector']));continue
                if tag=='Rename':
                    require(set(fields)=={'source','target'} and fields['source'] in node and fields['target'] not in node,'codec-rename-collision')
                    node[fields['target']]=node.pop(fields['source']);continue
                require(set(fields)=={'field'} and isinstance(fields['field'],str),'invalid-codec-field')
                field=fields['field']
                if tag=='DefaultNull':
                    if field not in node:node[field]=None
                    continue
                require(field in node,'codec-field-missing')
                if tag=='Integer':node[field]=uint(node[field])
                elif tag=='IntegerText':
                    require(type(node[field]) is int,'codec-integer-required');node[field]=str(uint(node[field]))
                elif tag=='Decode':
                    require(isinstance(node[field],str),'codec-json-text-required');node[field]=decode(node[field].encode())
                elif tag=='Encode':node[field]=encode(node[field]).decode()[:-1]
                elif tag=='OmitNull':
                    if node[field] is None:del node[field]
                else:raise Refusal('unsupported-representation-action','Unknown data codec action')
        return node
    result=walk(value)
    encode(result)
    return result