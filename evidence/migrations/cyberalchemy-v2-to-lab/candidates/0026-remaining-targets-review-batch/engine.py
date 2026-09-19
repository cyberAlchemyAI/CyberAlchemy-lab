"""Read-only candidate runtime for records, relations, profiles and projections."""
import json
import math
import re
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from catalog import TYPES, RELATIONS, DERIVED, LIFECYCLES, EVALUATIONS
from schemas import record_schema, profile_shapes, obj, TEXT, strings
from profiles import evaluate, moment
from support import ROOT, LAB, load, sha, need

def read(path):
    def unique(pairs):
        result={}
        for k,v in pairs:
            need(k not in result,'Duplicate JSON key '+k); result[k]=v
        return result
    def invalid(value): raise ValueError('Invalid JSON number '+value)
    return json.loads(path.read_text(),object_pairs_hook=unique,parse_constant=invalid)

FORMATS=FormatChecker()
@FORMATS.checks('date-time', raises=(ValueError, TypeError))
def timestamp_format(value):
    if not isinstance(value,str): return True
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})',value): return False
    moment(value)
    return True

def shape(schema,value):
    Draft202012Validator(schema,format_checker=FORMATS).validate(value)
    def finite(x):
        if isinstance(x,float): need(math.isfinite(x),'Nonfinite number')
        elif isinstance(x,dict):
            for v in x.values(): finite(v)
        elif isinstance(x,list):
            for v in x: finite(v)
    finite(value)

def matches(kind,allowed): return allowed=='*' or kind in allowed.split('|')

def validate_node(node,nodes):
    name=node['kind']; shape(record_schema(name),node)
    for key,kind in TYPES[name].items():
        if kind.startswith(('id:','ids:','ids0:')):
            values=[node[key]] if kind.startswith('id:') else node[key]
            for ident in values:
                need(ident in nodes,'Dangling reference '+key)
                need(matches(nodes[ident]['kind'],kind.split(':',1)[1]),'Reference kind mismatch '+key)
        if kind=='period':
            period=node[key]; start=moment(period['start']); end=moment(period['end']) if period['end'] else None
            need(end is None or end>start,'Period must end after start')
        if kind in ['nonnegative-int','positive-int']: need(type(node[key]) is int,'Cardinality requires an integer')
    if name=='research-run':
        need(node['method_ref']==nodes[node['inquiry_ref']]['method_ref'],'Run method differs from inquiry')
        need(node['period']['end'] is not None,'Completed run requires end time')
    if name=='experiment-run': need(node['period']['end'] is not None,'Completed run requires end time')
    if name=='measurement-result': need(node['unit']==nodes[node['method_ref']]['unit'],'Measurement unit differs from Method')
    if name=='context-profile':
        need(node['minimum_anchors']<=node['maximum_anchors'],'Reversed anchor bounds')
        need(set(node['identity_fields'])<=set(TYPES['context'])|{'node_id','scope_ref','owner_ref'},'Unknown Context identity field')
    if name=='context-request':
        context=nodes[node['context_ref']]; profile=nodes[context['profile_ref']]
        need(profile['minimum_anchors']<=len(node['anchor_refs'])<=profile['maximum_anchors'],'Context anchor cardinality')
        need(all(nodes[x]['kind'] in profile['allowed_anchor_kinds'] for x in node['anchor_refs']),'Context anchor kind')
        need(node['scope_ref']==context['scope_ref'],'Context request scope mismatch')
    if name=='context-view':
        request=nodes[node['request_ref']]
        need(node['scope_ref']==request['scope_ref'],'Context view scope mismatch')
        need(len(node['selected_refs'])<=request['budget'],'Context view exceeds request budget')
        need(bool(node['selected_refs'] or node['residue_refs']),'Empty Context View must record residue')
    if name=='model-instance-binding': need(node['parent_authority_scope']!=node['instance_authority_scope'],'Parent and instance authority scopes collapse')
    if name=='team-membership':
        need(node['membership_posture']!='ended' or node['period']['end'] is not None,'Ended membership requires end time')
    return True

def relation_schema(name):
    return obj({'relation_id':TEXT,'kind':{'const':name},'source':TEXT,'target':TEXT,'direction':{'const':load(ROOT/f'targets/relation.{name}/contract.json')['direction']},'owner_route':TEXT,'scope_ref':TEXT,'evidence_refs':strings(),'declared_effect':TEXT,'authority_effect':{'const':'none'}})

def validate_relation(edge,nodes):
    name=edge['kind']; need(name in RELATIONS,'Unknown relation kind'); shape(relation_schema(name),edge)
    need(edge['source'] in nodes and edge['target'] in nodes,'Dangling relation endpoint')
    source,target=nodes[edge['source']],nodes[edge['target']]
    a,b=RELATIONS[name]; need(matches(source['kind'],a) and matches(target['kind'],b),'Relation endpoint kind mismatch')
    need(edge['source']!=edge['target'],'Self relation outside profile')
    for ident in edge['evidence_refs']: need(ident in nodes and nodes[ident]['kind']=='evidence-set','Missing relation evidence')
    if name in ['successor-of','supersedes']: need(source['kind']==target['kind'],'Successor changes subject kind')
    if name=='belongs-to-product' and source['kind'] in ['product-thesis','product-capability']: need(source['product_ref']==edge['target'],'Product edge disagrees with record')
    if name=='belongs-to-project' and 'project_ref' in source: need(source['project_ref']==edge['target'],'Project edge disagrees with record')
    if name=='uses-method' and 'method_ref' in source: need(source['method_ref']==edge['target'],'Method edge disagrees with run')
    return True

def validate_graph(graph):
    need(set(graph)=={'schema_version','authority_effect','nodes','relations'},'Graph envelope fields changed')
    need(graph['schema_version']=='cal-review-graph/v1' and graph['authority_effect']=='none','Invalid graph posture')
    need(len(graph['nodes'])<=10000 and len(graph['relations'])<=20000,'Graph exceeds bounded profile')
    nodes={x['node_id']:x for x in graph['nodes']}; need(len(nodes)==len(graph['nodes']),'Duplicate node identity')
    support_schema=load(ROOT/'support-node.schema.json')
    for node in graph['nodes']:
        if node['kind'] in TYPES: validate_node(node,nodes)
        else: shape(support_schema,node)
    ids=set(); pairs=set()
    for edge in graph['relations']:
        need(edge['relation_id'] not in ids,'Duplicate relation identity'); ids.add(edge['relation_id'])
        key=(edge['kind'],edge['source'],edge['target']); need(key not in pairs,'Duplicate relation'); pairs.add(key)
        validate_relation(edge,nodes)
    for node in graph['nodes']:
        if node['kind']=='ontology': need(set(node['relation_ids'])<=ids,'Ontology references missing relation')
    # Iterative cycle check, independent of edge insertion order.
    for kind in ['successor-of','supersedes','derives-from','instance-of']:
        adjacency={ident:[] for ident in nodes}; degree={ident:0 for ident in nodes}
        for edge in graph['relations']:
            if edge['kind']==kind: adjacency[edge['source']].append(edge['target']); degree[edge['target']]+=1
        queue=[x for x,d in degree.items() if d==0]; count=0
        while queue:
            ident=queue.pop(); count+=1
            for target in adjacency[ident]:
                degree[target]-=1
                if degree[target]==0: queue.append(target)
        need(count==len(nodes),'Cycle in '+kind)
    # Overlapping duplicate assignments require an explicit future conflict profile.
    for kind,keys in [('team-membership',['person_ref','team_ref']),('role-assignment',['assignee_ref','role_ref','scope_ref'])]:
        groups={}
        for node in graph['nodes']:
            if node['kind']==kind: groups.setdefault(tuple(node[k] for k in keys),[]).append(node)
        for entries in groups.values():
            entries=sorted(entries,key=lambda n:moment(n['period']['start']))
            for left,right in zip(entries,entries[1:]):
                need(left['period']['end'] is not None and moment(left['period']['end'])<=moment(right['period']['start']),'Overlapping '+kind)
    return nodes

def load_graph(manifest_path):
    manifest=read(manifest_path)
    shape(load(ROOT/'graph-manifest.schema.json'),manifest)
    records=[]; edges=[]; paths=set()
    for category,out in [('nodes',records),('relations',edges)]:
        for ref in manifest[category]:
            path=(LAB/ref['path']).resolve(); need(path.is_relative_to(LAB.resolve()),'Graph member escapes Lab')
            need(path not in paths,'Duplicate graph file'); paths.add(path)
            need(sha(path)==ref['sha256'],'Graph member drift')
            out.append(read(path))
    graph={'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':records,'relations':edges}; validate_graph(graph); return graph

def project(name,graph,as_of='2026-09-07T00:00:00Z'):
    nodes=validate_graph(graph); need(name in DERIVED,'Unknown derived surface')
    kinds,relations=DERIVED[name]
    edges=[x for x in graph['relations'] if '*' in relations or x['kind'] in relations]
    selected={x['node_id'] for x in graph['nodes'] if '*' in kinds or x['kind'] in kinds}
    for edge in edges: selected.update([edge['source'],edge['target']])
    rows=[]
    for ident in sorted(selected):
        node=nodes[ident]; row={'node_id':ident,'kind':node['kind'],'status':node['status'],'authority_effect':'none'}
        if name=='team-roster' and node['kind'] in ['team-membership','role-assignment']:
            start=moment(node['period']['start']); end=moment(node['period']['end']) if node['period']['end'] else None; now=moment(as_of)
            row['current']=start<=now and (end is None or now<end)
            row['period']=node['period']
            for key in ['person_ref','team_ref','assignee_ref','role_ref']:
                if key in node: row[key]=node[key]
        rows.append(row)
    return {'surface':name,'authority_effect':'none','status':'derived-non-authoritative','as_of':as_of if name=='team-roster' else None,'nodes':rows,'relations':sorted(edges,key=lambda e:e['relation_id']),'completeness_proven':False,'view_activated':False}

def profile_eval(name,parameters,query):
    a,b=profile_shapes(name); shape(a,parameters); shape(b,query)
    if name in LIFECYCLES:
        need(parameters['states']==LIFECYCLES[name][0] and parameters['transitions']==[list(x) for x in LIFECYCLES[name][1]],'Lifecycle differs from candidate contract')
    if name in EVALUATIONS: need(parameters['required_checks']==EVALUATIONS[name],'Evaluation criteria differ from candidate contract')
    if name=='context-resolution': need(parameters['minimum_anchors']<=parameters['maximum_anchors'],'Reversed profile bounds')
    return evaluate(name,parameters,query)

def check_revision(before,after):
    need(before.get('kind') in TYPES and after.get('kind') in TYPES,'Unknown revision kind')
    shape(record_schema(before['kind']),before); shape(record_schema(after['kind']),after)
    need(before['node_id']==after['node_id'] and before['kind']==after['kind'],'Revision changes identity')
    immutable={'research-run','experiment-run','observation','measurement-result','context-view'}
    if before['kind'] in immutable: need(before==after,'Immutable execution or observation requires a new record')
    fields={'product':['identity_boundary'],'project':['identity_boundary'],'team':['identity_boundary'],'context':['purpose','profile_ref','identity_boundary'],'person-reference':['identity_scope']}.get(before['kind'],[])
    for key in ['scope_ref']+fields: need(before[key]==after[key],'Identity boundary change requires explicit successor review')
    return {'revision_compatible':True,'authority_effect':'none','revision_applied':False}
