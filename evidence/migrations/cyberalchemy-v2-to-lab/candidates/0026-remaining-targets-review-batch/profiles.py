"""Candidate policy evaluators: pure previews; never issue permissions or effects."""
from pathlib import PurePosixPath
from datetime import datetime, timezone
from catalog import LIFECYCLES, EVALUATIONS

def moment(value):
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    if parsed.tzinfo is None: raise ValueError('Time must include timezone')
    return parsed.astimezone(timezone.utc)

def evaluate(name,p,q):
    from support import need
    result={'profile':name,'authority_effect':'none','action_authorized':False,'effect_executed':False}
    reasons=[]; detail={}
    if q['scope_ref']!=p['scope_ref']: return {**result,'outcome':'not-applicable','reasons':['scope-mismatch']}
    if name in LIFECYCLES:
        if q['from_state'] not in p['states'] or q['to_state'] not in p['states']: reasons.append('unknown-state')
        if [q['from_state'],q['to_state']] not in p['transitions']: reasons.append('transition-not-listed')
        if q['owner_route']!=p['owner_route']: reasons.append('owner-route-mismatch')
        if q['gate_ref']!=p['gate_ref']: reasons.append('gate-mismatch')
        if not q['evidence_refs']: reasons.append('missing-evidence')
        if q['gate_passed'] is not True: reasons.append('gate-not-passed')
        detail={'proposed_state':q['to_state'],'state_changed':False,'gate_authenticated':False}
    elif name in EVALUATIONS:
        need(set(q['checks'])<=set(p['required_checks']),'Unknown evaluation check')
        failed=[x for x in p['required_checks'] if q['checks'].get(x) is False]
        missing=[x for x in p['required_checks'] if x not in q['checks']]
        return {**result,'outcome':'block' if failed else 'defer' if missing else 'pass-for-review','failed':failed,'missing':missing,'evidence_truth_proven':False}
    elif name=='repository-layout-policy':
        for item in q['paths']:
            path=PurePosixPath(item)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] not in p['allowed_roots']: reasons.append('path-outside-layout:'+item)
        detail={'paths_checked':len(q['paths'])}
    elif name=='source-selection-policy':
        ids=[x['source_id'] for x in q['sources']]; need(len(ids)==len(set(ids)),'Duplicate source identity')
        allowed=[x for x in q['sources'] if x['posture'] in p['allowed_postures'] and x['source_id'] in p['allowed_sources']]
        chosen=sorted(allowed,key=lambda x:x['source_id'])[:p['max_sources']]
        detail={'selected':[x['source_id'] for x in chosen],'excluded':sorted(set(ids)-{x['source_id'] for x in chosen}),'selection_complete':len(chosen)==len(q['sources'])}
    elif name=='authority-aware-navigation':
        ids=[x['node_id'] for x in q['nodes']]; need(len(ids)==len(set(ids)),'Duplicate navigation node')
        detail={'visible':[{'node_id':x['node_id'],'posture':x['posture'],'governing':False} for x in sorted(q['nodes'],key=lambda x:x['node_id']) if x['posture'] in p['visible_postures']]}
    elif name=='challenge':
        if q['mode'] not in p['modes']: reasons.append('unsupported-mode')
        if not q['evidence_refs']: reasons.append('missing-evidence')
        detail={'suggested_route':p['owner_route'],'challenge_resolved':False}
    elif name=='retention':
        if moment(q['as_of'])<moment(q['recorded_at']): reasons.append('as-of-before-record')
        age=(moment(q['as_of'])-moment(q['recorded_at'])).total_seconds()/86400
        held=q['legal_hold'] or q['permanently_reserved']
        detail={'retention_result':'retain' if held or age<p['minimum_days'] else 'eligible-for-owner-review','deleted':False}
    elif name=='semantic-consistency':
        by_id={}
        for x in q['definitions']:
            key=(x['definition_id'],x['version'])
            if key in by_id and by_id[key]!=x['sha256']: reasons.append('conflicting-definition-bytes')
            by_id[key]=x['sha256']
        detail={'semantic_truth_proven':False}
    elif name=='publication':
        for field in ['artifact_sha256','destination','actor_ref','operation']:
            if q[field]!=p[field]: reasons.append('publication-'+field+'-mismatch')
        if not q['decision_ref'] or not q['approved']: reasons.append('missing-approval-assertion')
        detail={'publication_performed':False,'approval_authenticated':False}
    elif name=='cross-context-generalization':
        if q['source_context']!=p['source_context'] or q['target_context']!=p['target_context']: reasons.append('context-mismatch')
        if not q['assumptions_checked'] or not q['counterevidence_reviewed']: reasons.append('compatibility-not-shown')
        if not q['evidence_refs']: reasons.append('missing-evidence')
        detail={'authority_transferred':False}
    elif name=='context-resolution':
        if not p['minimum_anchors']<=len(q['anchors'])<=p['maximum_anchors']: reasons.append('anchor-cardinality')
        if any(x['kind'] not in p['allowed_anchor_kinds'] for x in q['anchors']): reasons.append('anchor-kind')
        if len({x['id'] for x in q['anchors']})!=len(q['anchors']): reasons.append('duplicate-anchor')
        if q['requested_budget']>p['maximum_budget']: reasons.append('budget-exceeded')
        detail={'context_activated':False}
    elif name=='recursion':
        if q['depth']>p['maximum_depth']: reasons.append('depth-exceeded')
        if len(q['ancestor_ids'])!=len(set(q['ancestor_ids'])) or q['current_id'] in q['ancestor_ids']: reasons.append('recursion-cycle')
        if q['remaining_budget']<=0: reasons.append('budget-exhausted')
        detail={'recursion_executed':False}
    else: raise ValueError('Unsupported profile '+name)
    return {**result,'outcome':'block' if reasons else 'pass-for-review','reasons':reasons,**detail}
