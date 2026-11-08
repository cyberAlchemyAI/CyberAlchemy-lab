"""Complete selected originals and exact occurrence selectors, without dedup.

The inventory selection is a reviewed host input, never computed from a caller's
claimed coverage. Every original body is read only through AnchoredReader.
Original JSON (including historical numeric metadata) is retained as bytes.
"""
from dataclasses import dataclass
import re
from lab_contracts.codec import canonical, closed, need, sha
from lab_selectors.anchors import legacy_json
from .common import binding, digest, load, sequence, unique, LIMIT

CONTEXT_HEADINGS = {'Dependencies', 'Inputs and source selectors',
    'Original obligation mapping', 'Source anchors', 'Inputs',
    'Outputs and planned write scope', 'Smallest Working Units'}
CRITERION_HEADINGS = {'Implementation detail / ordered rules',
    'Done criteria and acceptance evidence', 'Edge cases and failure modes',
    'Validation / reviewable check', 'Synchronization and handoff', 'Scope',
    'Input and authority gates', 'Preserved acceptance obligations',
    'Acceptance in this phase', 'Write and evidence rules',
    'Deferred admitted-operation obligation', 'Objective and dependencies',
    'Implementation detail: ordered rules', 'Acceptance and validation strategy',
    'Synchronization and closure'}
ARRAY_CRITERIA = {'acceptance_evidence', 'original_acceptance_evidence',
    'phase_acceptance_evidence', 'done_criteria', 'phase_done_criteria',
    'ordered_rules', 'original_ordered_rules'}


@dataclass(frozen=True)
class Inventory:
    selection_binding: dict
    summary: dict
    occurrences: tuple
    originals: tuple

    def original_bytes(self, selected_binding):
        matches = [raw for b, raw in self.originals if b == selected_binding]
        need(len(matches) == 1, 'ORIGINAL_NOT_SELECTED')
        return matches[0]

    def view(self):
        return {'summary': self.summary, 'occurrences': list(self.occurrences),
                'original_bindings': [b for b, _ in self.originals]}


def inputs(selection):
    """Inventory only, not verification: anchor selection before using its list."""
    return [d['binding'] for d in selection['documents']]


def _occurrence(doc, selector, value, role, owners):
    # SHA binds identity, selector binds occurrence even when text repeats.
    identifier = digest({'source': doc['binding'], 'selector': selector})
    return {'id': identifier, 'document_id': doc['id'],
            'source_binding': doc['binding'], 'selector': selector,
            'text': value, 'role': role, 'candidate_owners': sorted(owners)}


def _paragraphs(raw, doc, owners, ac=False):
    text = raw.decode('utf-8')
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line.encode('utf-8')))
    heading = 'preamble'
    start = None
    output = []
    def emit(end):
        nonlocal start
        if start is None:
            return
        begin, finish = offsets[start], offsets[end]
        role = 'context'
        if ac or heading in CRITERION_HEADINGS:
            role = 'criterion'
        elif heading.startswith('Smallest working unit SWU-'):
            role='criterion'
        elif heading.startswith('SWU-'):
            body=raw[begin:finish].decode('utf-8')
            label=body.split(':',1)[0]
            if label in {'- Parent','- Dependencies','- Source/context'}:role='context'
            elif label in {'- Write scope','- Selected ordered rules','- Negative cases',
                           '- Done criteria and evidence','- Reviewable check','- Handoff'}:role='criterion'
            else:role='unresolved-section'
        elif heading not in CONTEXT_HEADINGS and heading != 'preamble':
            # Unknown sections are never silently excluded from coverage.
            role = 'unresolved-section'
        selector = {'kind': 'byte-span', 'start': begin, 'end': finish,
                    'heading': heading}
        output.append(_occurrence(doc, selector,
            raw[begin:finish].decode('utf-8'), role, owners))
        start = None
    for index, line in enumerate(lines):
        match = re.match(r'^(#{1,3}) (.+?)\r?\n?$', line)
        if match:
            emit(index)
            heading = 'preamble' if len(match.group(1))==1 else match.group(2)
            # Heading bytes are preserved as context occurrences too.
            output.append(_occurrence(doc, {'kind':'byte-span',
                'start':offsets[index], 'end':offsets[index+1], 'heading':'heading'},
                line, 'context', owners))
        elif not line.strip():
            emit(index)
        elif re.match(r'^(?:- |\d+[.)] )',line):
            emit(index)
            start=index
        elif start is None:
            start = index
    emit(len(lines))
    return output


def build(reader, expected_selection):
    selection = load(reader, expected_selection, 'lab-original-inventory-selection/v1',
                     ['documents'])
    sequence(selection['documents'], 256)
    docs = {}
    raws = {}
    parsed = {}
    for doc in selection['documents']:
        closed(doc, ['id', 'binding'])
        binding(doc['binding'])
        need(doc['id'] not in docs, 'DUPLICATE_DOCUMENT')
        docs[doc['id']] = doc
        raw = reader.read(doc['binding'], max_bytes=LIMIT)
        raws[doc['id']] = raw
        if doc['id'] in {'crosswalk','completion-dag','completion-swus',
                          'inherited','phase-dag','phase-swus','original-dag','original-swus'}:
            parsed[doc['id']] = legacy_json(raw)
    required = {'crosswalk','completion-dag','completion-swus','inherited',
                'phase-dag','phase-swus','original-dag','original-swus','acceptance'}
    need(required <= set(docs), 'CORE_DOCUMENTS')
    cross = parsed['crosswalk']; dag=parsed['completion-dag']; inherited=parsed['inherited']
    need(cross['original_dag'] == dag and cross['original_completion_swu_manifest'] ==
         parsed['completion-swus'] and cross['inherited_obligation_crosswalk'] == inherited,
         'CROSSWALK_ORIGINAL_MISMATCH')
    need(inherited['original_units'] == parsed['phase-swus']['units'], 'INHERITED_SWU_MISMATCH')
    need(parsed['phase-dag']['nodes']==[t['full_original_node'] for t in inherited['tasks']],
         'INHERITED_NODE_MISMATCH')
    nodes=dag['nodes']; edges=dag['edges']; tasks=inherited['tasks']
    need(len(nodes)==36 and len(edges)==73 and len(parsed['completion-swus']['units'])==36
         and len(tasks)==46 and len(inherited['original_units'])==63
         and len(parsed['original-dag']['nodes'])==40 and len(parsed['original-swus']['units'])==57,
         'ORIGINAL_CARDINALITY')
    task_ids=[n['id'] for n in nodes]; unique(task_ids)
    need(set(task_ids)=={f'T{i:02}' for i in range(36)}, 'TASK_IDS')
    for edge in edges:
        need(edge['from'] in task_ids and edge['to'] in task_ids, 'DEPENDENCY_ENDPOINT')
    need(len({(e['from'],e['to']) for e in edges})==73,'DEPENDENCY_DUPLICATE')
    for n in nodes:
        need(set(n['depends_on'])=={e['from'] for e in edges if e['to']==n['id']},
             'DEPENDENCY_CONTRACT')
    task_owners={t['original_id']:t['completion_tasks'] for t in tasks}
    routes={t['original_id']:t['full_original_node'].get('original_criteria_obligation_route')
            for t in tasks}
    def owners_for(original_task):
        owners=set(task_owners[original_task])
        # These are source-declared possible contribution/route owners, not an
        # assignment of all original obligations to every candidate owner.
        route=routes[original_task]
        if type(route) is str:
            for phase in route.split('/'):
                owners.update(task_owners.get(phase,[]))
        return sorted(owners)
    body_specs=[]
    base=docs['completion-dag']['binding']['relative_path'].rsplit('/',1)[0]
    for n in nodes:
        body_specs.append((f'completion:{n["id"]}',base+'/'+n['contract_path'],[n['id']]))
    for t in tasks:
        body_specs.append((f'phase:{t["original_id"]}',t['original_contract'],owners_for(t['original_id'])))
        if t['full_original_node'].get('original_task_contract'):
            body_specs.append((f'original:{t["original_id"]}',
                t['full_original_node']['original_task_contract'],owners_for(t['original_id'])))
    need(len(body_specs)==122 and set(docs)==required|{x[0] for x in body_specs},
         'BODY_COVERAGE')
    occurrences=[]
    for identifier,path,owners in body_specs:
        need(docs[identifier]['binding']['relative_path']==path,'BODY_PATH')
        need(bool(owners) and set(owners)<=set(task_ids),'BODY_OWNER')
        occurrences.extend(_paragraphs(raws[identifier],docs[identifier],owners))
    def arrays(value,doc,pointer,owners):
        if type(value) is dict:
            for name,item in value.items():
                path=pointer+'/'+name.replace('~','~0').replace('/','~1')
                if name in ARRAY_CRITERIA:
                    need(type(item) is list,'CRITERIA_ARRAY')
                    for index,body in enumerate(item):
                        need(type(body) is str,'CRITERIA_TEXT')
                        occurrences.append(_occurrence(doc,{'kind':'json-pointer',
                            'pointer':path+'/'+str(index)},body,'criterion',owners))
                else:
                    arrays(item,doc,path,owners)
        elif type(value) is list:
            for index,item in enumerate(value):arrays(item,doc,pointer+'/'+str(index),owners)
    for index,n in enumerate(nodes):arrays(n,docs['completion-dag'],f'/nodes/{index}',[n['id']])
    for index,n in enumerate(parsed['completion-swus']['units']):
        arrays(n,docs['completion-swus'],f'/units/{index}',[n['parent_task']])
    for index,t in enumerate(tasks):arrays(t,docs['inherited'],f'/tasks/{index}',owners_for(t['original_id']))
    for index,u in enumerate(inherited['original_units']):
        arrays(u,docs['inherited'],f'/original_units/{index}',owners_for(u['parent_task']))
    for document,field in [('phase-dag','nodes'),('phase-swus','units'),
                           ('original-dag','nodes'),('original-swus','units')]:
        for index,item in enumerate(parsed[document][field]):
            owner=item['id'] if field=='nodes' else item['parent_task']
            arrays(item,docs[document],f'/{field}/{index}',owners_for(owner))
    acraw=raws['acceptance']
    matches=list(re.finditer(rb'^### (AC\d\d)\r?$',acraw,re.M))
    need([m.group(1).decode() for m in matches]==[f'AC{i:02}' for i in range(1,14)],'AC_COVERAGE')
    for index,match in enumerate(matches):
        end=matches[index+1].start() if index+1<len(matches) else len(acraw)
        acid=match.group(1).decode()
        owners=[n['id'] for n in nodes if acid in n['acceptance_conditions']]
        occurrences.append(_occurrence(docs['acceptance'],{'kind':'byte-span',
            'start':match.start(),'end':end,'heading':acid},
            acraw[match.start():end].decode(),'criterion',owners))
    unique([o['id'] for o in occurrences])
    summary={'tasks':task_ids,'edges':edges,
             'task_acceptance':{n['id']:n['acceptance_conditions'] for n in nodes},
             'original_routes':routes,'original_completion_owners':task_owners,
             'body_count':122,'inherited_tasks':46,
             'inherited_swus':63,'original_tasks':40,'original_swus':57,'ac_count':13,
             'dag_acceptance_occurrences':sum(len(n['acceptance_evidence']) for n in nodes),
             'criterion_count':sum(o['role']!='context' for o in occurrences),
             'occurrence_count':len(occurrences)}
    return Inventory(expected_selection,summary,tuple(occurrences),
                     tuple((d['binding'],raws[i]) for i,d in docs.items()))
