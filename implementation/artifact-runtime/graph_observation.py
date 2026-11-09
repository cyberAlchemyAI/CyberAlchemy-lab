"""Single-node/edge observations over explicit JSON adjacency data.

Field names and query choices are supplied by the compiled caller. This module
performs no traversal, root selection, visited-state update or acceptance policy.
"""
from exact_io import require
from json_construction import uint

def observe(document,layout,query):
    require(isinstance(document,dict) and isinstance(layout,dict) and isinstance(query,dict),'invalid-graph-observation')
    nodes=document[layout['nodes_field']]
    roots=document[layout['roots_field']]
    require(isinstance(nodes,dict) and isinstance(roots,list),'invalid-graph-containers')
    identifiers=sorted(nodes)
    mode=query['mode']
    if mode=='counts':return {'nodes':str(len(identifiers)),'roots':str(len(roots))}
    index=uint(query['index']);parent=query.get('parent');identity=None
    if mode=='identity':identity=query['id']
    elif mode=='node':
        if index<len(identifiers):identity=identifiers[index]
    elif mode=='root':
        if index<len(roots):identity=roots[index]
    elif mode=='child':
        if parent in nodes:
            edges=nodes[parent][layout['edges_field']]
            require(isinstance(edges,list),'invalid-graph-edges')
            if index<len(edges):identity=edges[index]
    else:raise ValueError('unsupported-graph-observation-mode')
    found=isinstance(identity,str) and identity in nodes
    row=nodes[identity] if found else None
    if found:
        require(isinstance(row,dict),'invalid-graph-node')
        edges=row[layout['edges_field']]
        marked=row[layout['marked_field']]
        require(isinstance(edges,list) and type(marked) is bool,'invalid-graph-node-fields')
        missing=sum(1 for edge in edges if not isinstance(edge,str) or edge not in nodes)
        slot=identifiers.index(identity)
    else:edges=[];marked=False;missing=0;slot=0
    return {'observation':{'found':found,'id':identity if found else None,'slot':str(slot),'required':marked,'dependencies':str(len(edges)),'unknown':str(missing),'parent':parent,'edge_index':str(index)},'record':row}