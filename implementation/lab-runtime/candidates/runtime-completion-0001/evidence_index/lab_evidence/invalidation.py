"""Monotone invalidation over selected consumers and original acceptance edges."""
from lab_contracts.codec import closed, need, canonical
from .common import binding, load, sequence, unique, text
from .inventory import build


def invalidate(reader, expected_inventory, expected_graph, old_selection, new_selection):
    inventory=build(reader,expected_inventory)
    graph=load(reader,expected_graph,'lab-evidence-consumer-graph/v1',
        ['inventory_binding','nodes','edges','unmapped_subjects'])
    need(graph['inventory_binding']==expected_inventory,'INVALIDATION_INVENTORY')
    sequence(graph['nodes']);sequence(graph['edges'],50000)
    nodes={}
    for node in graph['nodes']:
        closed(node,['id','kind','task_id','acceptance_id']);text(node['id'])
        need(node['id'] not in nodes and node['kind'] in
             {'subject','evidence','aggregate','task','acceptance'},'INVALIDATION_NODE')
        need(node['task_id'] is None or node['task_id'] in inventory.summary['tasks'],'INVALIDATION_TASK')
        need((node['kind']=='acceptance' and node['acceptance_id'] in {f'AC{i:02}' for i in range(1,14)})
             or (node['kind']!='acceptance' and node['acceptance_id'] is None),'INVALIDATION_AC')
        nodes[node['id']]=node
    need({n['task_id'] for n in nodes.values() if n['kind']=='task'}==set(inventory.summary['tasks']),
         'INVALIDATION_TASK_COVERAGE')
    task_nodes={n['task_id']:n['id'] for n in nodes.values() if n['kind']=='task'}
    need(len(task_nodes)==sum(n['kind']=='task' for n in nodes.values()),'DUPLICATE_TASK_NODE')
    ac_nodes={n['acceptance_id']:n['id'] for n in nodes.values() if n['kind']=='acceptance'}
    need(set(ac_nodes)=={f'AC{i:02}' for i in range(1,14)} and
         len(ac_nodes)==sum(n['kind']=='acceptance' for n in nodes.values()),'INVALIDATION_AC_COVERAGE')
    required={(task_nodes[e['from']],task_nodes[e['to']]) for e in inventory.summary['edges']}
    actual=set();adj={n:set() for n in nodes}
    for edge in graph['edges']:
        closed(edge,['producer','consumer','kind'])
        need(edge['producer'] in nodes and edge['consumer'] in nodes and
             edge['kind'] in {'selected-input','dynamic-input','acceptance-dependency'},'INVALIDATION_EDGE')
        pair=edge['producer'],edge['consumer']
        adj[pair[0]].add(pair[1])
        if edge['kind']=='acceptance-dependency':actual.add(pair)
    need(required<=actual,'MISSING_ORIGINAL_DEPENDENCY')
    need(all(ac_nodes[acid] in adj[task_nodes[task]]
             for task,acids in inventory.summary['task_acceptance'].items() for acid in acids),
         'MISSING_TASK_AC_DEPENDENCY')
    unique(graph['unmapped_subjects'])
    need(set(graph['unmapped_subjects'])<={i for i,n in nodes.items() if n['kind']=='subject'},
         'UNKNOWN_SUBJECT')
    need(all(adj[i] or i in graph['unmapped_subjects'] for i,n in nodes.items()
             if n['kind']=='subject'),'MISSING_CONSUMER_COVERAGE')
    def selection(expected):
        value=load(reader,expected,'lab-invalidation-selection/v1',['subjects'])
        sequence(value['subjects']);result={}
        for item in value['subjects']:
            closed(item,['subject','binding'])
            need(item['subject'] in nodes and nodes[item['subject']]['kind']=='subject' and
                 item['subject'] not in result,'SELECTION_SUBJECT')
            binding(item['binding']);result[item['subject']]=item['binding']
        return result
    old=selection(old_selection);new=selection(new_selection)
    subject_ids={i for i,n in nodes.items() if n['kind']=='subject'}
    need(set(old)|set(new)==subject_ids,'SELECTION_SUBJECT_COVERAGE')
    changed={s for s in subject_ids if old.get(s)!=new.get(s)}
    stale=set(changed)
    uncertain=bool(changed&set(graph['unmapped_subjects']))
    if uncertain:
        stale.update(i for i,n in nodes.items() if n['kind'] in {'evidence','aggregate','task','acceptance'})
    queue=list(stale)
    while queue:
        for consumer in adj[queue.pop()]:
            if consumer not in stale:stale.add(consumer);queue.append(consumer)
    return {'schema_version':'lab-invalidation-result/v1','changed_subjects':sorted(changed),
        'stale':sorted(stale),'conservative_unknown_mapping':uncertain,
        'unaffected_candidates':sorted(set(nodes)-stale),
        'unaffected_evidence_reuse':'requires independently selected unchanged-input proof',
        'old_selection_binding':old_selection,'new_selection_binding':new_selection,
        'graph_binding':expected_graph,'authority_effect':'none','historical_records_mutated':False}
