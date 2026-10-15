"""Exact declared dependency closure; SCC ordering is not semantic acceptance."""
import copy
import hashlib
import json
import sys
from pathlib import Path
import contracts as c
import resolver as r

ROOT=Path(__file__).resolve().parents[4]
PACKET_UNIT=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/units/A04'
sys.path.insert(0,str(PACKET_UNIT))
import correspondence

SOURCE_KEYS=('definition_id','version_ref','path','sha256')
POLICY_VALUES={'joint-analysis','prohibited-constraining','unresolved'}


class GraphFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def source_ref(row):return {key:row[key] for key in SOURCE_KEYS}


def bound(ref,current):
    return isinstance(ref,dict) and set(ref)==set(SOURCE_KEYS) and isinstance(ref.get('version_ref'),str) and ref['version_ref'] in current and r.same_json(ref,source_ref(current[ref['version_ref']]))


def closure(seeds,adjacency):
    reached=set(seeds);pending=list(seeds)
    while pending:
        node=pending.pop()
        for neighbor in adjacency.get(node,()):
            if neighbor not in reached:reached.add(neighbor);pending.append(neighbor)
    return sorted(reached)


def components(nodes,adjacency):
    """Iterative Kosaraju; dependent -> dependency edges are retained."""
    seen=set();finished=[]
    for seed in sorted(nodes):
        if seed in seen:continue
        seen.add(seed);stack=[(seed,iter(sorted(adjacency.get(seed,()))))]
        while stack:
            node,neighbors=stack[-1]
            try:neighbor=next(neighbors)
            except StopIteration:finished.append(node);stack.pop();continue
            if neighbor not in seen:seen.add(neighbor);stack.append((neighbor,iter(sorted(adjacency.get(neighbor,())))))
    reverse={node:set() for node in nodes}
    for node in nodes:
        for neighbor in adjacency.get(node,()):reverse[neighbor].add(node)
    seen=set();result=[]
    for seed in reversed(finished):
        if seed in seen:continue
        group=[];pending=[seed];seen.add(seed)
        while pending:
            node=pending.pop();group.append(node)
            for neighbor in sorted(reverse[node]):
                if neighbor not in seen:seen.add(neighbor);pending.append(neighbor)
        result.append(sorted(group))
    return sorted(result)


def execution_order(groups,adjacency):
    owners={node:index for index,group in enumerate(groups) for node in group}
    needs={index:set() for index in range(len(groups))};consumers={index:set() for index in needs}
    for node,neighbors in adjacency.items():
        for neighbor in neighbors:
            left,right=owners[node],owners[neighbor]
            if left!=right:needs[left].add(right);consumers[right].add(left)
    ready=sorted(index for index in needs if not needs[index]);result=[]
    while ready:
        index=ready.pop(0);result.append(groups[index])
        for consumer in sorted(consumers[index]):
            needs[consumer].discard(index)
            if not needs[consumer] and consumer not in ready:ready.append(consumer);ready.sort()
    if len(result)!=len(groups):raise GraphFault('condensation-order-failure')
    return result


def compile_graph(snapshot,roots,packets,cycle_policies=(),required_edges=None,live_root=None):
    """Compile only verified authored uses. No term matching or inferred edges."""
    r.verify(snapshot,live_root)
    if not isinstance(roots,list) or not roots:raise GraphFault('nonempty-selected-roots-required')
    if not isinstance(packets,list) or not isinstance(cycle_policies,(list,tuple)):raise GraphFault('graph-input-lists-required')
    c.bounded_tree(roots);c.bounded_tree(packets);c.bounded_tree(cycle_policies)
    current={row['version_ref']:row for row in snapshot['current_entries']}
    for ref in roots:
        if not bound(ref,current):raise GraphFault('unbound-selected-root')
    root_ids=[ref['version_ref'] for ref in roots]
    if len(set(root_ids))!=len(root_ids):raise GraphFault('duplicate-selected-root')
    selected={};reports={};valid={};quarantined=[];traceability=[]
    for packet in packets:
        # A04 is the independently enforced correspondence gate.
        report=correspondence.check(packet,snapshot)
        core=packet.get('interpretation') if isinstance(packet,dict) else None
        if not isinstance(core,dict) or not bound(core.get('source'),current):raise GraphFault('unbound-packet-source')
        identity=core['source']['version_ref']
        if identity in selected:raise GraphFault('ambiguous-selected-interpretation',identity)
        selected[identity]=packet;reports[identity]=report
        if report['status'] not in {'candidate-accounted','correspondence-pending'}:
            quarantined.append({'source':core['source'],'check':report,'declared_dependency_links':copy.deepcopy(packet.get('dependency_links',[]))})
            continue
        valid[identity]=packet
        for link in packet['dependency_links']:
            if link['kind']!='semantic-use':traceability.append({'from':identity,'link':copy.deepcopy(link),'promoted_to_semantic_edge':False})
    edges=[];adjacency={identity:set() for identity in current}
    for identity,packet in sorted(valid.items()):
        core=packet['interpretation'];clauses={row['clause_id']:row for row in core['clauses']}
        for link in packet['dependency_links']:
            if link['kind']!='semantic-use':continue
            ref=link['dependency_ref'];target=ref['version_ref'];clause=clauses[link['clause_id']]
            # The A04 gate verifies exact refs, declaration/use agreement and spans.
            if not bound(ref,current):raise GraphFault('internal-unbound-validated-edge')
            adjacency[identity].add(target)
            basis={'interpretation_id':core['interpretation_id'],'scope':core['scope'],'clause_id':clause['clause_id'],'source_selector':clause['source_selector'],'excerpt_sha256':clause['excerpt_sha256'],'rationale':link['rationale']}
            edges.append({'kind':'uses_definition','from':identity,'to':target,'from_source':core['source'],'to_source':ref,'basis':basis})
    reachable=closure(root_ids,adjacency);reach=set(reachable)
    outside=sorted(set(selected)-reach)
    if outside:raise GraphFault('packet-outside-selected-transitive-closure',','.join(outside))
    selected_adjacency={node:adjacency[node]&reach for node in reachable}
    edges=[row for row in edges if row['from'] in reach]
    edges.sort(key=lambda row:(row['from'],row['to'],row['basis']['clause_id']))
    edge_pairs={(row['from'],row['to']) for row in edges}
    policy_map={}
    for record in cycle_policies:
        if not isinstance(record,dict) or set(record)!={'from_source','to_source','classification','basis','review_ref'}:raise GraphFault('malformed-cycle-policy')
        if not bound(record['from_source'],current) or not bound(record['to_source'],current):raise GraphFault('unbound-cycle-policy-source')
        if record['classification'] not in POLICY_VALUES or any(not isinstance(record[key],str) or not record[key].strip() for key in ['basis','review_ref']):raise GraphFault('malformed-cycle-policy')
        pair=(record['from_source']['version_ref'],record['to_source']['version_ref'])
        if pair not in edge_pairs:raise GraphFault('cycle-policy-without-declared-edge')
        if pair in policy_map:raise GraphFault('duplicate-cycle-policy')
        policy_map[pair]=copy.deepcopy(record)
    denominator='requires-independent-review'
    if required_edges is not None:
        if not isinstance(required_edges,list):raise GraphFault('required-edge-list-needed')
        expected=[]
        for edge in required_edges:
            if not isinstance(edge,dict) or set(edge)!={'from_source','to_source'} or not bound(edge['from_source'],current) or not bound(edge['to_source'],current):raise GraphFault('malformed-required-edge')
            expected.append((edge['from_source']['version_ref'],edge['to_source']['version_ref']))
        if len(set(expected))!=len(expected):raise GraphFault('duplicate-required-edge')
        if set(expected)!=edge_pairs:raise GraphFault('required-edge-denominator-mismatch')
        denominator='separately-compared'
    groups=components(reachable,selected_adjacency);cycle_reviews=[]
    for group in groups:
        members=set(group);internal=sorted(pair for pair in edge_pairs if pair[0] in members and pair[1] in members)
        if len(group)==1 and (group[0],group[0]) not in edge_pairs:continue
        policies=[policy_map.get(pair) for pair in internal]
        if any(policy and policy['classification']=='prohibited-constraining' for policy in policies):disposition='rejected-prohibited-cycle'
        elif any(policy is None or policy['classification']=='unresolved' for policy in policies):disposition='unresolved-cycle-classification'
        else:disposition='accepted-for-joint-analysis'
        cycle_reviews.append({'members':group,'internal_edges':[list(pair) for pair in internal],'disposition':disposition,'policies':policies,'recursive_semantics':'requires-separate-review; no least-fixed-point inference'})
    missing=sorted(reach-set(valid));pending=sorted(node for node in reach if node in reports and (reports[node]['status']!='candidate-accounted' or reports[node]['source_fidelity']!='reviewed'))
    unresolved=[]
    for edge in edges:
        if edge['to'] not in valid:unresolved.append({'from':edge['from'],'to':edge['to'],'reason':'missing-or-quarantined-dependency-interpretation'})
    for row in quarantined:
        unresolved.append({'from':row['source']['version_ref'],'reason':'invalid-correspondence-packet','check':row['check'],'declared_links':row['declared_dependency_links']})
    if any(row['disposition']=='rejected-prohibited-cycle' for row in cycle_reviews):status='rejected-prohibited-cycle'
    elif missing or unresolved or pending or denominator=='requires-independent-review' or any(row['disposition']=='unresolved-cycle-classification' for row in cycle_reviews):status='graph-compiled-with-pending-readiness'
    else:status='graph-compiled-requires-semantic-review'
    reverse={node:set() for node in reachable}
    for node,neighbors in selected_adjacency.items():
        for neighbor in neighbors:reverse[neighbor].add(node)
    value={'schema_version':'definition-assurance-dependency-graph/v1-candidate','authority_effect':'none','semantic_ready':False,'status':status,'selected_roots':sorted(root_ids),'nodes':[{'source':source_ref(current[node]),'scope':selected[node]['interpretation']['scope'] if node in selected else None,'interpretation_status':reports[node]['status'] if node in reports else 'missing-interpretation'} for node in reachable],'edges':edges,'source_correspondence_checks':{key:reports[key] for key in sorted(reports)},'unresolved':unresolved,'missing_or_quarantined_interpretations':missing,'pending_correspondence_or_fidelity':pending,'traceability_links':traceability,'edge_denominator':denominator,'strongly_connected_components':groups,'cycle_reviews':cycle_reviews,'execution_order':execution_order(groups,selected_adjacency),'reverse_affected_closure':{node:closure([node],reverse) for node in reachable},'input_bindings':{'snapshot_sha256':digest(snapshot),'packets_sha256':digest(packets),'cycle_policies_sha256':digest(cycle_policies),'required_edges_sha256':digest(required_edges)},'claim_ceiling':'Closure and SCC order only for exact explicitly declared validated semantic uses. Missing/quarantined translations, dependency completeness, source fidelity, cycle meaning and consistency remain independent gates.'}
    value['graph_sha256']=digest(value)
    return value


def verify_graph(value,snapshot,roots,packets,cycle_policies=(),required_edges=None,live_root=None):
    expected=compile_graph(snapshot,roots,packets,cycle_policies,required_edges,live_root)
    if not r.same_json(value,expected):raise GraphFault('dependency-graph-integrity-mismatch')
    return {'result':'PASS','semantic_ready':False,'authority_effect':'none'}
