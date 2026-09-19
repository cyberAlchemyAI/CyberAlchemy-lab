import copy
from catalog import TYPES, RELATIONS, LIFECYCLES, EVALUATIONS, POLICIES
SUPPORT_KINDS=['definition','goal','work','method','receipt','evidence-set','implementation','policy','residue','source','evaluation','constitution','decision','effect','generated-output','schema','bounded-context','responsibility','person','authority-claim','hypothesis','gate','source-admission']
SCOPE='scope:review-fixtures'
def ident(kind): return 'example:'+kind

def graph_records():
    nodes=[]
    for kind in SUPPORT_KINDS:
        nodes.append({'node_id':ident(kind),'kind':kind,'status':'fixture-only','authority_effect':'none','scope_ref':SCOPE,'owner_ref':'role:example-owner','fixture_only':True})
    for kind,fields in TYPES.items():
        node={'node_id':ident(kind),'kind':kind,'status':'candidate-unadmitted','authority_effect':'none','scope_ref':SCOPE,'owner_ref':'role:example-owner'}
        for key,ft in fields.items():
            if ft.startswith('id:'): value=ident(ft.split(':')[1].split('|')[0])
            elif ft.startswith(('ids:','ids0:')): value=[ident(ft.split(':')[1].split('|')[0])]
            elif ft=='period': value={'start':'2026-09-01T00:00:00Z','end':'2026-09-02T00:00:00Z' if kind in ['research-run','experiment-run'] else None}
            elif ft=='time': value='2026-09-01T12:00:00Z'
            elif ft in ['number','nonnegative','nonnegative-int','positive-int']: value=1
            elif ft=='membership': value='active'
            elif ft=='list0': value=[]
            elif ft=='list': value=['Example declared '+key.replace('_',' ')]
            else: value='Example '+key.replace('_',' ')
            node[key]=value
        if kind=='context-profile': node.update(allowed_anchor_kinds=['product','project','product-capability'],minimum_anchors=1,maximum_anchors=3,identity_fields=['node_id','purpose'])
        if kind=='context-request': node['budget']=3
        if kind=='measurement-method': node['unit']='count'
        if kind=='measurement-result': node.update(unit='count',value=3,uncertainty=0.5)
        if kind=='model-instance-binding': node.update(parent_authority_scope='scope:parent',instance_authority_scope='scope:instance')
        nodes.append(node)
    for kind in ['product','person-reference']:
        node=copy.deepcopy(next(x for x in nodes if x['kind']==kind)); node['node_id']+='-2'; nodes.append(node)
    return nodes

def graph_relations(nodes,contracts):
    def choose(allowed,exclude=None):
        if allowed=='*': allowed='product'
        return next(x['node_id'] for x in nodes if x['kind'] in allowed.split('|') and x['node_id']!=exclude)
    edges=[]
    for name,(source,target) in RELATIONS.items():
        a=choose(source); b=choose(target,a)
        if name=='belongs-to-project': a=ident('research-inquiry')
        if name=='uses-method': a=ident('research-run')
        edges.append({'relation_id':'example:relation:'+name,'kind':name,'source':a,'target':b,'direction':contracts[name]['direction'],'scope_ref':SCOPE,'owner_route':'route:example-owner','evidence_refs':[ident('evidence-set')],'declared_effect':'Candidate review only; no automatic authority.','authority_effect':'none'})
    return edges

def profile_example(name):
    scope={'scope_ref':SCOPE}
    if name in LIFECYCLES:
        states,transitions=LIFECYCLES[name]
        p={**scope,'states':states,'transitions':[list(x) for x in transitions],'owner_route':'route:owner','gate_ref':'gate:review'}
        q={**scope,'from_state':transitions[0][0],'to_state':transitions[0][1],'owner_route':p['owner_route'],'gate_ref':p['gate_ref'],'gate_passed':True,'evidence_refs':['example:evidence']}
        bad=copy.deepcopy(q); bad['gate_passed']=False
    elif name in EVALUATIONS:
        p={**scope,'required_checks':EVALUATIONS[name]}; q={**scope,'checks':{x:True for x in EVALUATIONS[name]}}; bad=copy.deepcopy(q); bad['checks'][EVALUATIONS[name][0]]=False
    else:
        p,q,bad={
'repository-layout-policy':({'allowed_roots':['authority','evidence','docs']},{'paths':['authority/definition.json']},{'paths':['../private.json']}),
'source-selection-policy':({'allowed_sources':['source:a'],'allowed_postures':['candidate'],'max_sources':1},{'sources':[{'source_id':'source:a','posture':'candidate'}]},{'sources':[{'source_id':'source:unlisted','posture':'candidate'}]}),
'authority-aware-navigation':({'visible_postures':['candidate','admitted']},{'nodes':[{'node_id':'x','posture':'candidate'}]},{'nodes':[{'node_id':'x','posture':'withdrawn'}]}),
'challenge':({'modes':['contradict'],'owner_route':'route:owner'},{'mode':'contradict','evidence_refs':['example:evidence']},{'mode':'override','evidence_refs':[]}),
'retention':({'minimum_days':30},{'recorded_at':'2026-01-01T00:00:00Z','as_of':'2026-09-01T00:00:00Z','legal_hold':False,'permanently_reserved':False},{'recorded_at':'2026-01-01T00:00:00Z','as_of':'2026-09-01T00:00:00Z','legal_hold':True,'permanently_reserved':False}),
'semantic-consistency':({'identity_key':'definition_id+version'},{'definitions':[{'definition_id':'x','version':'1','sha256':'a'*64}]},{'definitions':[{'definition_id':'x','version':'1','sha256':'a'*64},{'definition_id':'x','version':'1','sha256':'b'*64}]}),
'publication':({'artifact_sha256':'a'*64,'destination':'example:destination','actor_ref':'example:actor','operation':'publish'},{'artifact_sha256':'a'*64,'destination':'example:destination','actor_ref':'example:actor','operation':'publish','decision_ref':'example:decision','approved':True},{'artifact_sha256':'b'*64,'destination':'example:destination','actor_ref':'example:actor','operation':'publish','decision_ref':'example:decision','approved':True}),
'cross-context-generalization':({'source_context':'a','target_context':'b'},{'source_context':'a','target_context':'b','assumptions_checked':True,'counterevidence_reviewed':True,'evidence_refs':['example:evidence']},{'source_context':'a','target_context':'c','assumptions_checked':True,'counterevidence_reviewed':True,'evidence_refs':['example:evidence']}),
'context-resolution':({'allowed_anchor_kinds':['product'],'minimum_anchors':1,'maximum_anchors':2,'maximum_budget':10},{'anchors':[{'id':'x','kind':'product'}],'requested_budget':5},{'anchors':[{'id':'x','kind':'person'}],'requested_budget':11}),
'recursion':({'maximum_depth':3},{'depth':1,'ancestor_ids':['parent'],'current_id':'child','remaining_budget':10},{'depth':4,'ancestor_ids':['child'],'current_id':'child','remaining_budget':0})
        }[name]; p={**scope,**p}; q={**scope,**q}; bad={**scope,**bad}
    return p,q,bad
