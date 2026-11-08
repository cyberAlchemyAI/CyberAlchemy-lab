"""Reviewable native mapping proposal, never a self-issued interpretation review.

Owners below follow the exact original completion contracts and phase routes.
The caller must obtain an independent review of the emitted core before adding
its later review binding and selecting an eligibility context.
"""
from collections import Counter
import re
from lab_contracts.codec import need
from .common import digest

# Default proof stage of each original completion contract. Clause exceptions
# below are emitted with exact source occurrence/selector and must be reviewed.
BASE_STAGE={
 'T00':'static','T01':'authorized-candidate-runtime','T02':'authorized-candidate-runtime',
 'T03':'authorized-candidate-runtime','T04':'inert-contract','T05':'authorized-candidate-runtime',
 'T06':'inert-contract','T07':'authorized-candidate-runtime','T08':'authorized-candidate-runtime',
 'T09':'authorized-candidate-runtime','T10':'authorized-effect','T11':'authorized-effect',
 'T12':'authorized-effect','T13':'authorized-effect','T14':'inert-contract','T15':'static',
 'T16':'final-qualification','T17':'final-qualification','T18':'final-qualification',
 'T19':'final-qualification','T20':'final-qualification','T21':'static',
 'T22':'final-qualification','T23':'final-qualification','T24':'final-qualification',
 'T25':'final-qualification','T26':'authorized-effect','T27':'authorized-effect',
 'T28':'authorized-effect','T29':'post-effect-verification','T30':'post-effect-verification',
 'T31':'authorized-candidate-runtime','T32':'authorized-candidate-runtime',
 'T33':'inert-contract','T34':'authorized-candidate-runtime',
 'T35':'authorized-candidate-runtime'}


def proof_requirements(o,task,direct,resolution):
    """Review proposal only: emits exact matches, never decides runtime authority.

    The emitted source map contains the original text and selector for every
    application. Review approves the concrete mapping, not an open vocabulary
    inference algorithm. Unknown heading meanings remain gated independently.
    """
    if resolution in {'context','contribution'}:
        return [],['context' if resolution=='context' else 'original-task-contribution']
    stage=BASE_STAGE[task];kind='native-effect' if task=='T26' else 'process'
    rules=['contract:'+task];wording=o['text'].lower()
    if direct and task=='T02' and any(x in wording for x in
        ['route both metadata resurrection','update only explicitly documented fixture',
         'wrong class/module still refused','loosening class guard']):
        stage='inert-contract';rules.append('T02-constructor-negative-inert')
    if direct and task=='T31' and re.sub(r'^\s*(?:-\s+|\d+[.)]\s+)', '', wording).startswith('inventory the ten'):
        stage='static';rules.append('T31-template-inventory-static')
    if direct and task=='T21' and any(x in wording for x in
        ['verify copyable setup','operator can follow','fresh operator recipe walkthrough']):
        stage='final-qualification';rules.append('T21-frozen-recipe-execution')
    pairs=[{'stage':stage,'terminal_kind':kind}]
    # Explicit selected source scopes; technical descriptions of future humans
    # are never an observation gate. The exact text/selector is retained in map.
    if direct and task=='T23':
        normalized=wording.strip().lstrip('- ').rstrip('.')
        human_only=(normalized in {'authentic human usefulness observations',
                                  'all three journeys independently checked'} or
                    'have the actual human perform all three journeys' in normalized)
        if human_only:
            pairs=[{'stage':'human-observation','terminal_kind':'human-observation'}]
            rules.append('T23-actual-owner-journey-clause')
        if 'human walkthrough and separately verified technical run' in normalized:
            pairs=[{'stage':'final-qualification','terminal_kind':'process'},
                   {'stage':'human-observation','terminal_kind':'human-observation'}]
            rules.append('T23-same-cut-human-and-technical')
    if not direct and 'real bounded users/work/evidence and cost observations' in wording:
        pairs.append({'stage':'human-observation','terminal_kind':'human-observation'})
        rules.append('R05-explicit-real-user-acceptance')
    if o['document_id']=='acceptance' and o['selector']['heading']=='AC12':
        pairs.append({'stage':'human-observation','terminal_kind':'human-observation'})
        rules.append('AC12-actual-owner-journeys')
    return pairs,rules

# These owners follow T24's staged audit, T25's package closure and the original
# admitted-operation task/AC mappings. They are not selected by numeric order.
AC_FINAL={f'AC{i:02}':('T25' if i in {5,13} else 'T24') for i in range(1,14)}
LATER_TASKS={'T26','T27','T28','T29','T30'}
ROUTE_FINAL={'A01':'T27','A02':'T28','A03':'T29','A04':'T30'}


def proposal(inventory, mapping_bindings, task_units, unit_gates):
    occurrences=inventory.occurrences
    own={task:[o['id'] for o in occurrences if o['document_id']=='completion:'+task and
                o['role']!='context' and o['selector'].get('heading')=='Done criteria and acceptance evidence']
          for task in inventory.summary['tasks']}
    task_basis={task:next(o['id'] for o in occurrences if o['document_id']=='completion:'+task
                         and o['selector'].get('heading')=='Done criteria and acceptance evidence')
                for task in inventory.summary['tasks']}
    originals={b['relative_path']:raw for b,raw in inventory.originals}
    # Source identity -> original task comes from exact original row ownership,
    # not filenames guessed at runtime. The inventory already checks body paths.
    from lab_selectors.anchors import legacy_json
    docvalues={}
    for o in occurrences:
        if o['selector']['kind']=='json-pointer' and o['document_id'] not in docvalues:
            docvalues[o['document_id']]=legacy_json(inventory.original_bytes(o['source_binding']))
    def original_task(o):
        doc=o['document_id']
        if doc.startswith(('phase:','original:')):return doc.split(':',1)[1]
        value=docvalues[doc];parts=o['selector']['pointer'].split('/')
        row=value[parts[1]][int(parts[2])]
        if doc=='inherited' and parts[1]=='tasks':return row['original_id']
        return row['parent_task'] if 'parent_task' in row else row['id']
    entries=[];source_map=[];counts=Counter();owner_counts=Counter();stage_counts=Counter()
    for o in occurrences:
        doc=o['document_id'];direct=doc.startswith('completion:') or doc in {'completion-dag','completion-swus'}
        if o['role']=='context':final=None;route=None
        elif direct:final=o['candidate_owners'][0];route=None
        elif doc=='acceptance':final=AC_FINAL[o['selector']['heading']];route='AC staged ownership'
        else:
            original=original_task(o);route=inventory.summary['original_routes'][original]
            phases=route.split('/') if type(route) is str else []
            chosen=[ROUTE_FINAL[p] for p in phases if p in ROUTE_FINAL]
            final=chosen[0] if len(chosen)==1 else ('T25' if original=='S02' else 'T24')
        need(final is None or final in o['candidate_owners'],'NATIVE_FINAL_OWNER_NOT_SOURCE_ROUTED')
        dispositions=[]
        for task in o['candidate_owners']:
            resolution='context' if o['role']=='context' else ('required' if task==final else 'contribution')
            if o['role']=='unresolved-section' and task==final:resolution='unresolved'
            pairs,proof_rules=proof_requirements(o,task,direct,resolution)
            stages=sorted({p['stage'] for p in pairs})
            kinds=sorted({p['terminal_kind'] for p in pairs})
            required_kinds=sorted({p['terminal_kind'] for p in pairs})
            roles=['code']
            if any(s not in {'static','inert-contract'} for s in stages):
                roles+=['source-family','profile','execution-environment','root-topology']
            if any(s in {'authorized-effect','post-effect-verification'} for s in stages):roles+=['role-policy']
            if task=='T23':roles+=['human-pilot-protocol','technical-bridge-selection']
            if task=='T26':roles+=['exact-final-bundle','owner-issuer-enrollment']
            if task in LATER_TASKS-{'T26'}:
                roles+=['exact-final-bundle','current-effect-scope','current-authority-review']
            basis=[o['id'],task_basis[task]]
            if final is not None:basis.append(task_basis[final])
            if doc=='acceptance':basis.append(task_basis['T24'])
            rationale=(f'Original {task} scope is a contribution defined by its exact body criteria; '
                       f'full original obligation remains with {final} through source route {route}.'
                       if resolution=='contribution' else
                       f'Exact original {task} obligation; selected stage follows its task contract. '
                       'Missing genuine evidence remains MISSING; this policy is not an outcome.')
            if task in LATER_TASKS-{'T26'}:
                rationale+=' Initial exact-final-bundle is ancestry only. Current-authority-review independently binds the current effect target, permission and reviewed lineage; later targets may differ and no initial disposition grants their effects.'
            if resolution=='context':rationale='Original structural/context bytes retained; not a completion assertion.'
            if resolution=='unresolved':rationale='Unrecognized original section requires explicit interpretation by the listed owner; no satisfaction inferred.'
            units=task_units[task]
            d={'task_id':task,'resolution':resolution,'allowed_stages':stages,'required_roles':roles,
                'independent_review':True,'deferred_to':None,'rationale':rationale,
                'required_proofs':pairs,'proof_rule_ids':proof_rules,
                'terminal_kinds':kinds,'allowed_dispositions':['approve','reject','defer','stop'] if task=='T26'
                    else ['not-applicable'],'requires_timing':task!='T26','required_terminal_kinds':required_kinds,
                'scope_occurrence_ids':[] if resolution=='context' else own[task] if resolution=='contribution' else [o['id']],
                'basis_occurrence_ids':list(dict.fromkeys(basis)),'later_owner_units':units,
                'gate_ids':sorted({g for u in units for g in unit_gates[u]})}
            dispositions.append(d);counts[resolution]+=1;owner_counts[task]+=1
            for stage in stages:stage_counts[stage]+=1
        entries.append({'occurrence_id':o['id'],'dispositions':dispositions})
        source_map.append({'occurrence_id':o['id'],'source_binding':o['source_binding'],
            'selector':o['selector'],'final_owner':final,'source_phase_route':route,
            'candidate_owners':o['candidate_owners'],'original_text':o['text'],
            'proof_scopes':[{'task_id':d['task_id'],'resolution':d['resolution'],
                'required_proofs':d['required_proofs'],'rule_ids':d['proof_rule_ids'],
                'basis_occurrence_ids':d['basis_occurrence_ids']} for d in dispositions]})
    acceptance_phases=[]
    for o in occurrences:
        if o['document_id']!='acceptance':continue
        acid=o['selector']['heading']
        acceptance_phases.append({'acceptance_id':acid,'occurrence_id':o['id'],
            'candidate_tasks':[t for t in o['candidate_owners'] if t not in LATER_TASKS],
            'later_tasks':[t for t in o['candidate_owners'] if t in LATER_TASKS],
            'candidate_closure_task':AC_FINAL[acid],
            'basis_occurrence_ids':[o['id'],task_basis['T24'],task_basis['T25']]+[
                task_basis[t] for t in o['candidate_owners'] if t in LATER_TASKS]})
    core={'schema_version':'lab-criterion-policy/v1' ,'inventory_binding':inventory.selection_binding,
          'inventory_digest':digest(inventory.view()),'entries':entries,'deferral_authorizations':[],
          'mapping_bindings':mapping_bindings,'acceptance_phases':acceptance_phases}
    accounting={'schema_version':'lab-native-policy-accounting/v1','occurrences':len(occurrences),
        'dispositions':sum(counts.values()),'resolutions':dict(counts),'owners':dict(owner_counts),
        'stages':dict(stage_counts),
        'proof_conjunctions':dict(Counter('|'.join(p['stage']+':'+p['terminal_kind'] for p in d['required_proofs'])
            for e in entries for d in e['dispositions'] if d['resolution']=='required')),
        'original_task_acceptance':False,
        'claim_ceiling':'Native structural/technical interpretation proposal; actual evidence not supplied.'}
    return core,source_map,accounting
