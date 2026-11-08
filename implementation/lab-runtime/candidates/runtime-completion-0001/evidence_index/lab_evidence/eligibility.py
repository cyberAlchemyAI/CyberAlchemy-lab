"""Current eligibility from independently selected policy and review enrollment.

No historical status is read by this evaluator. The host selects policy/context
digests independently; a case author cannot enroll its own reviewer or scope.
"""
from dataclasses import dataclass
from lab_contracts.codec import canonical, closed, need, Refusal, sha, parse
from .common import binding, digest, load, sequence, unique, text, STAGES, OUTCOMES, LIMIT, POLICY_LIMIT, task_subjects
from .inventory import build

RECORD_FIELDS = ['evidence_id','task_id','original_obligation_ids',
    'acceptance_condition_ids','case_id','evidence_stage','subject_bindings',
    'selection_binding','attempt_binding','outcome','claim_ceiling','input_bindings',
    'command_binding','terminal_binding','timing_binding','state_observation_bindings',
    'review_binding','invalidation_rule','privacy_class','author_identity','observation_disposition']


def core_digest(record):
    """Acyclic review subject: evidence core excludes only the later review link."""
    return digest({k:v for k,v in record.items() if k != 'review_binding'})


class Capture:
    def __init__(self, reader):
        self.reader=reader
        self.originals={}
        self.total_bytes=0

    def read(self, selected, max_bytes=LIMIT):
        binding(selected)
        identifier=canonical(selected)
        if identifier not in self.originals:
            need(len(self.originals)<8192 and
                 self.total_bytes+selected['size_bytes']<=64*1024*1024,'CAPTURE_BOUND')
        raw=self.reader.read(selected,max_bytes=max_bytes)
        if identifier not in self.originals:self.total_bytes+=len(raw)
        self.originals[identifier]=(selected,raw)
        return raw


@dataclass(frozen=True)
class Evaluation:
    projection: dict
    originals: tuple


def disclosure(capture, allowed, enclosing):
    """Host selected exact public bytes, plus its closed public selector itself.

    The enclosing binding comes from the external caller, not a self-hash field.
    This avoids a cycle without granting a fallback for arbitrary readable data.
    """
    sequence(allowed,8192)
    approved=set()
    for selected in allowed:
        binding(selected);approved.add(canonical(selected))
    need(len(approved)==len(allowed),'DUPLICATE_DISCLOSURE_BINDING')
    approved.add(canonical(enclosing))
    need(set(capture.originals)<=approved,'PUBLIC_RETENTION_NOT_SELECTED')


def policy(reader, expected, inventory):
    value=load(reader,expected,'lab-criterion-policy/v1',
        ['inventory_binding','inventory_digest','entries','deferral_authorizations','mapping_bindings','acceptance_phases',
         'interpretation_review_binding'],max_bytes=POLICY_LIMIT)
    need(value['inventory_binding']==inventory.selection_binding and
         value['inventory_digest']==digest(inventory.view()),'POLICY_INVENTORY')
    sequence(value['mapping_bindings'],64)
    for selected in value['mapping_bindings']:
        binding(selected);reader.read(selected,max_bytes=LIMIT)
    binding(value['interpretation_review_binding'])
    # Policy selection is not its own review. The independent host also selects
    # the review bytes below, with the acyclic policy core digest as its subject.
    review=load(reader,value['interpretation_review_binding'],'lab-policy-review/v1',
        ['policy_core_digest','outcome','reviewer_identity','author_identity','scope'])
    need(review['policy_core_digest']==digest({k:v for k,v in value.items()
        if k!='interpretation_review_binding'}),'POLICY_REVIEW_SCOPE')
    need(review['outcome']=='PASS' and review['scope']=='criterion-interpretation',
         'POLICY_REVIEW_REQUIRED')
    entries=value['entries'];sequence(entries)
    sequence(value['deferral_authorizations'],64)
    by_id={o['id']:o for o in inventory.occurrences}
    all_occurrence_ids=set(by_id)
    sequence(value['acceptance_phases'],13)
    acceptance_occurrences=[o for o in inventory.occurrences if o['document_id']=='acceptance']
    need([r.get('acceptance_id') for r in value['acceptance_phases']]==
         [o['selector']['heading'] for o in acceptance_occurrences],'AC_PHASE_COVERAGE')
    for row,occurrence in zip(value['acceptance_phases'],acceptance_occurrences):
        closed(row,['acceptance_id','occurrence_id','candidate_tasks','later_tasks',
                    'candidate_closure_task','basis_occurrence_ids'])
        for k in ['candidate_tasks','later_tasks','basis_occurrence_ids']:unique(row[k])
        need(row['occurrence_id']==occurrence['id'],'AC_PHASE_OCCURRENCE')
        later={'T26','T27','T28','T29','T30'}
        need(row['candidate_tasks']==[t for t in occurrence['candidate_owners'] if t not in later] and
             row['later_tasks']==[t for t in occurrence['candidate_owners'] if t in later],
             'AC_PHASE_OWNER_PARTITION')
        need(row['candidate_closure_task']==('T25' if row['acceptance_id'] in {'AC05','AC13'} else 'T24'),
             'AC_CANDIDATE_CLOSURE_OWNER')
        need(row['basis_occurrence_ids'] and set(row['basis_occurrence_ids'])<=all_occurrence_ids,
             'AC_PHASE_SOURCE_BASIS')
    deferrals=set()
    for grant in value['deferral_authorizations']:
        closed(grant,['source_occurrence_id','from_task','to_task','acceptance_id','scope'])
        need(grant['source_occurrence_id'] in by_id,'DEFERRAL_SOURCE')
        source=by_id[grant['source_occurrence_id']]
        need(source['document_id']=='completion:T24' and
             source['selector'].get('heading')=='Implementation detail / ordered rules' and
             'final package/privacy/recovery AC05/AC13 clauses' in source['text'] and
             'T27-T30' in source['text'],'DEFERRAL_ORIGINAL_AUTHORIZATION')
        target=grant['to_task'];acid=grant['acceptance_id']
        need(grant['from_task']=='T24' and
             ((grant['scope']=='final-package' and target=='T25' and acid in {'AC05','AC13'}) or
              (grant['scope']=='admitted-operation' and target in {'T27','T28','T29','T30'} and
               acid in inventory.summary['task_acceptance'][target])), 'DEFERRAL_SCOPE')
        deferrals.add(('T24',target,acid))
    ids=[e.get('occurrence_id') for e in entries];unique(ids)
    need(ids==[o['id'] for o in inventory.occurrences],'POLICY_OCCURRENCE_COVERAGE')
    for entry,occurrence in zip(entries,inventory.occurrences):
        closed(entry,['occurrence_id','dispositions'])
        sequence(entry['dispositions'],36)
        need([d['task_id'] for d in entry['dispositions']]==occurrence['candidate_owners'],
             'POLICY_OWNER_COVERAGE')
        for d in entry['dispositions']:
            closed(d,['task_id','resolution','allowed_stages','required_roles',
                      'independent_review','deferred_to','rationale','terminal_kinds',
                      'allowed_dispositions','requires_timing','required_terminal_kinds',
                      'scope_occurrence_ids','basis_occurrence_ids','later_owner_units','gate_ids',
                      'required_proofs','proof_rule_ids'])
            need(d['resolution'] in {'context','required','unresolved','deferred','contribution'},'POLICY_RESOLUTION')
            text(d['rationale']);unique(d['allowed_stages']);unique(d['required_roles'])
            unique(d['terminal_kinds']);unique(d['allowed_dispositions'])
            for k in ['scope_occurrence_ids','basis_occurrence_ids','later_owner_units','gate_ids',
                      'required_terminal_kinds','proof_rule_ids']:unique(d[k])
            sequence(d['required_proofs'],16)
            pairs=[]
            for proof in d['required_proofs']:
                closed(proof,['stage','terminal_kind'])
                need(proof['stage'] in d['allowed_stages'] and
                     proof['terminal_kind'] in d['terminal_kinds'],'PROOF_PAIR_SCOPE')
                pairs.append((proof['stage'],proof['terminal_kind']))
            need(len(pairs)==len(set(pairs)),'DUPLICATE_PROOF_PAIR')
            need(set(d['required_terminal_kinds'])<=set(d['terminal_kinds']),'PROOF_KIND_COVERAGE')
            need(d['basis_occurrence_ids'] and set(d['basis_occurrence_ids'])<=all_occurrence_ids,
                 'POLICY_SOURCE_BASIS')
            need(set(d['gate_ids'])<={f'G{i:02}' for i in range(1,9)},'POLICY_GATE_ID')
            need(set(d['terminal_kinds'])<={'process','human-observation','native-effect'} and
                 set(d['allowed_dispositions'])<={'not-applicable','approve','reject','defer','stop'}
                 and type(d['requires_timing']) is bool,'POLICY_TERMINAL')
            need(set(d['allowed_stages'])<=STAGES,'POLICY_STAGE')
            need(type(d['independent_review']) is bool,'POLICY_REVIEW_TYPE')
            if occurrence['role']=='context':
                need(d['resolution']=='context','CONTEXT_CLASSIFICATION')
            else:
                need(d['resolution']!='context','CRITERION_NOT_CONTEXT')
            if d['resolution']=='contribution':
                need(not occurrence['document_id'].startswith('completion:') and
                     occurrence['document_id'] not in {'completion-dag','completion-swus'} and
                     d['scope_occurrence_ids'],'CONTRIBUTION_SCOPE')
                for scoped in d['scope_occurrence_ids']:
                    need(scoped in by_id and by_id[scoped]['role']!='context' and
                         by_id[scoped]['document_id']=='completion:'+d['task_id'],
                         'CONTRIBUTION_ORIGINAL_SCOPE')
            elif d['resolution']!='context':
                need(d['scope_occurrence_ids']==[occurrence['id']],'DIRECT_CRITERION_SCOPE')
            if d['resolution']=='required':
                need(bool(d['allowed_stages']) and bool(d['required_roles']) and
                     bool(d['terminal_kinds']) and bool(d['allowed_dispositions']) and bool(d['required_proofs']) and
                     d['independent_review'],'REQUIRED_POLICY')
            if d['resolution']=='deferred':
                need(occurrence['document_id']=='acceptance' and
                     (d['task_id'],d['deferred_to'],occurrence['selector']['heading']) in deferrals and
                     d['deferred_to'] in occurrence['candidate_owners'],'DEFERRED_OWNER')
            else:
                need(d['deferred_to'] is None,'UNEXPECTED_DEFERRED_OWNER')
        if occurrence['role']!='context':
            need(any(d['resolution'] in {'required','unresolved'} for d in entry['dispositions']),
                 'MISSING_GLOBAL_OBLIGATION_OWNER')
    return value,review


def _roles(rows):
    sequence(rows,256)
    result={}
    for row in rows:
        closed(row,['role','binding']);text(row['role']);binding(row['binding'])
        need(row['role'] not in result,'DUPLICATE_ROLE')
        result[row['role']]=row['binding']
    return result


def _record(reader, expected, context, policies):
    record=load(reader,expected,'lab-evidence-record/v1',RECORD_FIELDS)
    for field in ['evidence_id','task_id','case_id','claim_ceiling','author_identity']:
        text(record[field])
    unique(record['original_obligation_ids']);unique(record['acceptance_condition_ids'])
    need(record['original_obligation_ids'],'EMPTY_EVIDENCE_SCOPE')
    need(record['evidence_stage'] in STAGES and record['outcome'] in OUTCOMES,'EVIDENCE_ENUM')
    need(record['observation_disposition'] in {'not-applicable','approve','reject','defer','stop'},
         'OBSERVATION_DISPOSITION')
    need(record['privacy_class']=='reviewed-public-receipt','PUBLIC_RECEIPT_REQUIRED')
    need(record['invalidation_rule']=='exact-selected-consumer-closure/v1','INVALIDATION_RULE')
    need(record['selection_binding']==context['selection_binding'],'WRONG_SELECTION')
    selected_roles=_roles(context['subject_bindings'])
    scoped_subjects=task_subjects(context['task_subject_bindings'])
    need(not scoped_subjects or not {'current-effect-scope','current-authority-review'}&set(selected_roles),
         'AMBIGUOUS_TASK_SUBJECTS')
    selected_roles.update(scoped_subjects.get(record['task_id'],{}))
    subjects=_roles(record['subject_bindings']);inputs=_roles(record['input_bindings'])
    need(subjects and all(selected_roles.get(k)==v for k,v in subjects.items()),'WRONG_SUBJECT')
    need(all(selected_roles.get(k)==v for k,v in inputs.items()),'WRONG_INPUT')
    for b in [record['selection_binding'],record['attempt_binding'],record['command_binding'],
              record['terminal_binding'],record['timing_binding'],record['review_binding']]:binding(b)
    sequence(record['state_observation_bindings'],128)
    for b in list(subjects.values())+list(inputs.values())+record['state_observation_bindings']:
        binding(b);reader.read(b,max_bytes=LIMIT)
    reader.read(record['selection_binding'],max_bytes=LIMIT)
    attempt=load(reader,record['attempt_binding'],'lab-evidence-attempt/v1',
        ['attempt_id','selection_binding','case_id','stage'])
    need(attempt['selection_binding']==record['selection_binding'] and
         attempt['case_id']==record['case_id'] and attempt['stage']==record['evidence_stage'],
         'ATTEMPT_SCOPE')
    command=load(reader,record['command_binding'],'lab-evidence-command/v1',
        ['evidence_id','selection_binding','attempt_binding','case_id','stage','argv',
         'environment_bindings','original_binding','command_kind'])
    terminal=load(reader,record['terminal_binding'],'lab-evidence-terminal/v1',
        ['evidence_id','selection_binding','command_binding','outcome','actual_exit',
         'cleanup','effect_state','original_binding','terminal_kind','observation_disposition'])
    for f in ['evidence_id','selection_binding','attempt_binding','case_id']:
        need(command[f]==record[f],'COMMAND_SCOPE')
    need(command['stage']==record['evidence_stage'],'COMMAND_STAGE')
    kind=command['command_kind']
    need(kind in {'process','human-observation','native-effect'} and
         terminal['terminal_kind']==kind,'TERMINAL_KIND')
    if kind=='process':
        sequence(command['argv'],256);need(command['argv'],'COMMAND_ARGV')
        for arg in command['argv']:text(arg)
    else:
        need(command['argv'] is None and terminal['actual_exit'] is None,'NONPROCESS_OS_FIELDS')
        need((kind=='human-observation' and record['evidence_stage']=='human-observation') or
             (kind=='native-effect' and record['evidence_stage'] in
              {'authorized-candidate-runtime','authorized-effect','post-effect-verification'}),
             'NONPROCESS_STAGE')
    _roles(command['environment_bindings'])
    for f in ['evidence_id','selection_binding','command_binding','outcome']:
        need(terminal[f]==record[f],'TERMINAL_SCOPE')
    need(terminal['observation_disposition']==record['observation_disposition'],'TERMINAL_DISPOSITION')
    need(terminal['actual_exit'] is None or (type(terminal['actual_exit']) is int and
         -255<=terminal['actual_exit']<=255),'EXIT_TYPE')
    need(terminal['cleanup'] in {'clean','retained-owned','unknown'} and
         terminal['effect_state'] in {'none','owned-inert','observed','unknown'},'TERMINAL_STATE')
    timing=load(reader,record['timing_binding'],'lab-evidence-timing/v1',
                ['command_binding','elapsed_ns','original_binding'])
    need(timing['command_binding']==record['command_binding'] and
         (timing['elapsed_ns'] is None or (type(timing['elapsed_ns']) is int and
          timing['elapsed_ns']>=0)),'TIMING_SCOPE')
    # Native originals are retained as exact selected metadata; these wrappers
    # are trusted only when the externally enrolled review covers their bytes.
    for value in [command,terminal,timing]:
        binding(value['original_binding']);reader.read(value['original_binding'],max_bytes=LIMIT)
    review=load(reader,record['review_binding'],'lab-evidence-review/v1',
        ['evidence_core_digest','reviewer_identity','author_identity','outcome',
         'task_id','occurrence_ids','selection_binding','stage','claim_ceiling'])
    enroll=[e for e in context['review_enrollments'] if e['review_binding']==record['review_binding']]
    need(len(enroll)==1,'REVIEW_NOT_ENROLLED')
    enrolled=enroll[0]
    need(review['reviewer_identity']==enrolled['reviewer_identity'] and
         review['author_identity']==enrolled['author_identity']==record['author_identity'] and
         review['reviewer_identity']!=review['author_identity'],'REVIEW_IDENTITY')
    need(review['evidence_core_digest']==core_digest(record)==enrolled['evidence_core_digest'],
         'REVIEW_CORE_SCOPE')
    for a,b in [('task_id','task_id'),('occurrence_ids','original_obligation_ids'),
                ('selection_binding','selection_binding'),('stage','evidence_stage'),
                ('claim_ceiling','claim_ceiling')]:need(review[a]==record[b],'REVIEW_SCOPE')
    need(review['outcome'] in OUTCOMES,'REVIEW_OUTCOME')
    timing_complete=True
    for oid in record['original_obligation_ids']:
        need((oid,record['task_id']) in policies,'UNKNOWN_CRITERION')
        p=policies[oid,record['task_id']]
        need(p['resolution']=='required','UNRESOLVED_CRITERION')
        need(record['evidence_stage'] in p['allowed_stages'],'WRONG_STAGE')
        need(kind in p['terminal_kinds'] and record['observation_disposition'] in p['allowed_dispositions'],
             'WRONG_TERMINAL_SEMANTICS')
        if kind=='process' or p['requires_timing']:
            timing_complete=timing_complete and timing['elapsed_ns'] is not None
        need(set(p['required_roles'])<=set(subjects)|set(inputs),'MISSING_SUBJECT_ROLE')
    need(set(record['acceptance_condition_ids'])==set().union(*[
         set(policies[oid,record['task_id']]['acceptance_ids']) for oid in record['original_obligation_ids']]),
         'EVIDENCE_AC_SCOPE')
    known_failure=(record['outcome'] in {'FAIL','ERROR'} or review['outcome'] in {'FAIL','ERROR'} or
                   (kind=='process' and terminal['actual_exit'] is not None and terminal['actual_exit']!=0))
    positive=(timing_complete and record['outcome']=='PASS' and review['outcome']=='PASS' and
              (kind!='process' or terminal['actual_exit']==0) and terminal['cleanup']!='unknown' and
              terminal['effect_state']!='unknown')
    # Static/inert evidence must not conceal real external effects.
    if record['evidence_stage'] in {'static','inert-contract'}:
        need(terminal['effect_state'] in {'none','owned-inert','unknown'},'INERT_EFFECT_SCOPE')
    return record,positive,'ELIGIBLE' if positive else 'KNOWN_FAILURE' if known_failure else 'INCOMPLETE',kind


def evaluate(reader, expected_inventory, expected_policy, expected_context):
    captured=Capture(reader)
    inventory=build(captured,expected_inventory)
    value,interpretation_review=policy(captured,expected_policy,inventory)
    context=load(captured,expected_context,'lab-eligibility-context/v1',
        ['selection_binding','subject_bindings','evidence_bindings','review_enrollments',
         'policy_review_binding','policy_reviewer_identity','policy_author_identity',
         'public_retention_bindings','privacy_class','task_subject_bindings'])
    need(context['privacy_class']=='reviewed-public-selector','PUBLIC_CONTEXT_REQUIRED')
    text(context['policy_reviewer_identity']);text(context['policy_author_identity'])
    need(context['policy_review_binding']==value['interpretation_review_binding'] and
         interpretation_review['reviewer_identity']==context['policy_reviewer_identity'] and
         interpretation_review['author_identity']==context['policy_author_identity'] and
         context['policy_reviewer_identity']!=context['policy_author_identity'],
         'POLICY_REVIEW_ENROLLMENT')
    binding(context['selection_binding']);captured.read(context['selection_binding'],max_bytes=LIMIT)
    global_roles=_roles(context['subject_bindings']);scoped_roles=task_subjects(context['task_subject_bindings'])
    need(not scoped_roles or not {'current-effect-scope','current-authority-review'}&set(global_roles),
         'AMBIGUOUS_TASK_SUBJECTS')
    sequence(context['evidence_bindings'],4096)
    sequence(context['review_enrollments'],4096)
    for e in context['review_enrollments']:
        closed(e,['review_binding','reviewer_identity','author_identity','evidence_core_digest'])
        binding(e['review_binding']);text(e['reviewer_identity']);text(e['author_identity'])
        need(type(e['evidence_core_digest']) is str and
             re_digest(e['evidence_core_digest']),'REVIEW_DIGEST')
    need(len({canonical(e['review_binding']) for e in context['review_enrollments']})==
         len(context['review_enrollments']),'DUPLICATE_REVIEW_ENROLLMENT')
    need(len({canonical(b) for b in context['evidence_bindings']})==len(context['evidence_bindings']),
         'DUPLICATE_EVIDENCE_BINDING')
    occurrences={o['id']:o for o in inventory.occurrences}
    policies={}
    for entry in value['entries']:
        occurrence=occurrences[entry['occurrence_id']]
        for d in entry['dispositions']:
            acids=[occurrence['selector']['heading']] if occurrence['document_id']=='acceptance' else \
                  inventory.summary['task_acceptance'][d['task_id']]
            policies[entry['occurrence_id'],d['task_id']]={**d,'acceptance_ids':acids}
    observations=[];support={};support_kinds={};support_pairs={};counts={};negative=set();incomplete=set();counterevidence={};owner_approvals=set();owner_blockers=set()
    for selected in context['evidence_bindings']:
        binding(selected)
        raw=captured.read(selected,max_bytes=LIMIT)
        try:
            original=parse(raw,max_bytes=LIMIT)
            identifier=original.get('evidence_id') if type(original) is dict else None
            if type(identifier) is str:counts[identifier]=counts.get(identifier,0)+1
        except Refusal:
            pass
    for selected in context['evidence_bindings']:
        binding(selected)
        declared='UNKNOWN'
        try:
            # Retain selected original even when its schema or claims refuse.
            raw=captured.read(selected,max_bytes=LIMIT)
            original=parse(raw,max_bytes=LIMIT)
            if type(original) is dict and original.get('outcome') in OUTCOMES:
                declared=original['outcome']
            record,eligible,reason,kind=_record(captured,selected,context,policies)
            need(counts.get(record['evidence_id'])==1,'DUPLICATE_EVIDENCE_ID')
            observations.append({'binding':selected,'outcome':record['outcome'],
                                 'eligible':eligible,'reason':reason,'terminal_kind':kind,
                                 'observation_disposition':record['observation_disposition']})
            if eligible:
                if record['task_id']=='T26':
                    if record['observation_disposition']=='approve':
                        owner_approvals.update(record['original_obligation_ids'])
                    elif record['observation_disposition'] in {'reject','defer','stop'}:
                        owner_blockers.update(record['original_obligation_ids'])
                for oid in record['original_obligation_ids']:
                    support.setdefault((oid,record['task_id']),[]).append(selected)
                    support_kinds.setdefault((oid,record['task_id']),set()).add(kind)
                    support_pairs.setdefault((oid,record['task_id']),set()).add((record['evidence_stage'],kind))
            else:
                destination=negative if reason=='KNOWN_FAILURE' else incomplete
                destination.update((oid,record['task_id']) for oid in record['original_obligation_ids'])
                for oid in record['original_obligation_ids']:
                    counterevidence.setdefault((oid,record['task_id']),[]).append(selected)
        except (Refusal,KeyError,TypeError,UnicodeError):
            observations.append({'binding':selected,'outcome':declared,'eligible':False,
                                 'reason':'EVIDENCE_REFUSED'})
    criteria=[]
    for entry in value['entries']:
        for d in entry['dispositions']:
            status={'context':'CONTEXT','unresolved':'GATED','deferred':'PENDING',
                    'required':'MISSING','contribution':'CONTRIBUTION_MISSING'}[d['resolution']]
            accepted=support.get((entry['occurrence_id'],d['task_id']),[])
            if accepted:
                status='PASS' if (set(d['required_terminal_kinds'])<=support_kinds.get(
                    (entry['occurrence_id'],d['task_id']),set()) and
                    {(p['stage'],p['terminal_kind']) for p in d['required_proofs']}<=support_pairs.get(
                    (entry['occurrence_id'],d['task_id']),set())) else 'PARTIAL'
            if (entry['occurrence_id'],d['task_id']) in incomplete:status='INCOMPLETE'
            if (entry['occurrence_id'],d['task_id']) in negative:status='CONFLICTED'
            criteria.append({'occurrence_id':entry['occurrence_id'],'task_id':d['task_id'],
                             'status':status,'deferred_to':d['deferred_to'],'support':accepted,
                             'counterevidence':counterevidence.get((entry['occurrence_id'],d['task_id']),[])})
    by_pair={(c['occurrence_id'],c['task_id']):c for c in criteria}
    for c in criteria:
        selected=policies[c['occurrence_id'],c['task_id']]
        if selected['resolution']=='contribution':
            scopes=[by_pair[oid,c['task_id']] for oid in selected['scope_occurrence_ids']]
            c['contribution_scope']=selected['scope_occurrence_ids']
            if any(s['status']=='CONFLICTED' for s in scopes):
                c['status']='CONFLICTED'
                c['counterevidence']=list({canonical(b):b for s in scopes for b in s['counterevidence']}.values())
            elif any(s['status']=='INCOMPLETE' for s in scopes):
                c['status']='INCOMPLETE'
                c['counterevidence']=list({canonical(b):b for s in scopes for b in s['counterevidence']}.values())
            elif all(s['status']=='PASS' for s in scopes):
                c['status']='PASS'
                c['support']=list({canonical(b):b for s in scopes for b in s['support']}.values())
    required_owner_ids={oid for (oid,task),p in policies.items()
        if task=='T26' and p['resolution']=='required'}
    positive_owner_route=bool(required_owner_ids) and required_owner_ids<=owner_approvals and not owner_blockers
    task_results={}
    pending=set(inventory.summary['tasks'])
    while pending:
        ready=sorted(t for t in pending if all(e['from'] in task_results
                     for e in inventory.summary['edges'] if e['to']==t))
        need(ready,'TASK_DEPENDENCY_CYCLE')
        for task in ready:
            own=[c for c in criteria if c['task_id']==task and c['status']!='CONTEXT']
            upstream=[e['from'] for e in inventory.summary['edges'] if e['to']==task]
            accepted=bool(own) and all(c['status']=='PASS' or
                     (task=='T24' and c['status']=='PENDING' and c['deferred_to'] is not None)
                     for c in own) and \
                     all(task_results[t]['status']=='ELIGIBLE' for t in upstream)
            if task in {'T27','T28','T29','T30'}:accepted=accepted and positive_owner_route
            task_results[task]={'status':'ELIGIBLE' if accepted else 'INELIGIBLE',
                'failure_observed':any(c['status']=='CONFLICTED' for c in own) or
                    any(task_results[t]['failure_observed'] for t in upstream),
                'missing_or_gated':sum(c['status'] not in {'PASS','PENDING'} for c in own),
                'pending_downstream':sum(c['status']=='PENDING' for c in own),
                'positive_owner_route_required':task in {'T27','T28','T29','T30'},
                'positive_owner_route_observed':positive_owner_route,
                'unsatisfied_predecessors':[t for t in upstream if task_results[t]['status']!='ELIGIBLE']}
            pending.remove(task)
    acceptance={}
    for acid in [f'AC{i:02}' for i in range(1,14)]:
        ids={o['id'] for o in inventory.occurrences if o['document_id']=='acceptance'
             and o['selector']['heading']==acid}
        scoped=[c for c in criteria if c['occurrence_id'] in ids]
        resolved=[]
        for c in scoped:
            if c['status']=='PENDING' and c['deferred_to'] is not None:
                target=next((other for other in scoped if other['task_id']==c['deferred_to']),None)
                if target is not None and target['status']=='PASS' and \
                        task_results[c['deferred_to']]['status']=='ELIGIBLE':
                    resolved.append({'from_task':c['task_id'],'to_task':c['deferred_to'],
                        'occurrence_id':c['occurrence_id'],'support':target['support']})
        resolved_ids={(x['from_task'],x['occurrence_id']) for x in resolved}
        phase=next(p for p in value['acceptance_phases'] if p['acceptance_id']==acid)
        def complete(tasks):
            selected=[c for c in scoped if c['task_id'] in tasks]
            return bool(selected) and all(
                (c['status']=='PASS' and task_results[c['task_id']]['status']=='ELIGIBLE') or
                (c['task_id'],c['occurrence_id']) in resolved_ids for c in selected)
        def failed(tasks):
            return any(c['status']=='CONFLICTED' for c in scoped if c['task_id'] in tasks) or any(
                task_results[t]['failure_observed'] for t in tasks)
        candidate='FAIL' if failed(phase['candidate_tasks']) else 'PASS' if complete(phase['candidate_tasks']) else 'PENDING'
        later=('NOT_APPLICABLE' if not phase['later_tasks'] else
               'FAIL' if failed(phase['later_tasks']) else 'PASS' if complete(phase['later_tasks']) else 'PENDING')
        acceptance[acid]={'status':'FAIL' if 'FAIL' in {candidate,later} else 'PASS' if candidate=='PASS' and later in {'PASS','NOT_APPLICABLE'}
                         else 'PENDING','candidate_status':candidate,'later_operational_status':later,
                         'phase_policy':phase,'dispositions':scoped}
        acceptance[acid]['resolved_deferrals']=resolved
    projection={'schema_version':'lab-current-eligibility/v1','selection_binding':context['selection_binding'],
        'inventory_binding':expected_inventory,'policy_binding':expected_policy,
        'context_binding':expected_context,'inventory_digest':digest(inventory.view()),
        'tasks':task_results,'acceptance':acceptance,'criteria':criteria,'evidence':observations,
        'historical_acceptance_changed':False,'authority_effect':'none',
        'effect_permission_conferred':False}
    disclosure(captured,context['public_retention_bindings'],expected_context)
    return Evaluation(projection,tuple(captured.originals.values()))


def re_digest(value):
    return len(value)==64 and all(c in '0123456789abcdef' for c in value)
