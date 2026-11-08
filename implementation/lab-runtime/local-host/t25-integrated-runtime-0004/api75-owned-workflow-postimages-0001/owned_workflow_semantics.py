"""Exact original Work semantics; proof providers never replace these predicates."""
def need(ok,reason):
    if not ok:raise ValueError(reason)
def closed(value,fields,reason):need(type(value) is dict and set(value)==set(fields),reason)
def validate(run,definition,grant,facts,read):
    closed(facts,('intent','resolution','work','coordination','goal','decision','effects','decision_edges','goal_edges'),'closed actual workflow semantic facts required')
    records={}
    roles={'intent':('intent/v1',),'resolution':('intent-resolution/v1',),'work':('work/v1',),'coordination':('coordination-context/v2',),
           'goal':('goal/v1',),'decision':('decision/v1','decision/v2')}
    for key in ('intent','resolution','work','coordination','goal','decision'):
        need(facts[key]['artifact']['carrier_ref'] in ['cal.artifact-type.'+s for s in roles[key]],'semantic carrier role differs: '+key)
        records[key]=read(facts[key])
    for key,role in [('intent','intent'),('resolution','intent_resolution'),('work','work'),('coordination','coordination_context')]:
        need(facts[key]['artifact']==run[role],'semantic input differs from exact Run role: '+key)
    intent,resolution,work,coord,goal,decision=(records[k] for k in ('intent','resolution','work','coordination','goal','decision'))
    h={key:facts[key]['artifact'] for key in records};scope=grant['scope_ref']
    need(coord['project_ref']==scope and coord['goal_ref']==h['goal']['version_ref'] and coord['goal_ref'] in work['payload']['goal_refs'],
         'exact original Work/Goal/Coordination scope does not close')
    if 'project_ref' in work['payload']:need(work['payload']['project_ref']==scope,'original Work Project differs')
    rp=resolution['payload']
    need(rp['intent_ref'] in (h['intent']['identity_ref'],h['intent']['version_ref'])
         and any(ref in rp['selected_subject_refs'] for ref in (h['work']['identity_ref'],h['work']['version_ref']))
         and not any(ref in rp['excluded_subject_refs'] for ref in (h['work']['identity_ref'],h['work']['version_ref'])),
         'exact Intent Resolution does not select this Work')
    need(rp['owner_decision_ref'] in (h['decision']['identity_ref'],h['decision']['version_ref'])
         and h['resolution']['version_ref'] in decision['payload']['subject_refs'] and decision['payload']['declared_effect_refs'],
         'exact declared Decision/Resolution connection absent')
    need(type(facts['effects']) is list and facts['effects'],'actual exact Effect records required')
    declared=set(decision['payload']['declared_effect_refs']);actual=set()
    for row in facts['effects']:
        need(row['artifact']['carrier_ref']=='cal.artifact-type.effect/v1','Effect carrier role differs')
        effect=read(row);eh=row['artifact'];matches=declared&{eh['identity_ref'],eh['version_ref']}
        need(len(matches)==1 and effect['payload']['subject_ref']==h['resolution']['version_ref'],'declared Effect names another Resolution')
        actual|=matches
    need(actual==declared,'declared Effect closure incomplete')
    need(type(facts['decision_edges']) is list and len(facts['decision_edges'])==1,'one exact declared Decision/Resolution edge required')
    need(facts['decision_edges'][0]['artifact']['carrier_ref']=='cal.artifact-type.typed-relation/v3','Decision edge carrier differs')
    edge=read(facts['decision_edges'][0])['payload']
    need(edge['relation_kind_ref']=='relation.declares-effect-on'
         and edge['source']['version_ref']==h['decision']['version_ref'] and edge['target']['version_ref']==h['resolution']['version_ref']
         and edge['qualifiers']['exact_target_version_ref']==h['resolution']['version_ref'],'exact Decision/Resolution relation differs')
    if 'project_ref' in goal:need(goal['project_ref']==scope,'Goal Project differs')
    else:
        need(type(facts['goal_edges']) is list and len(facts['goal_edges'])==1,'one exact Goal/Project edge required')
        need(facts['goal_edges'][0]['artifact']['carrier_ref']=='cal.artifact-type.typed-relation/v3','Goal edge carrier differs')
        edge=read(facts['goal_edges'][0])['payload']
        need(edge['relation_kind_ref']=='relation.member-of' and edge['source']['version_ref']==h['goal']['version_ref']
             and edge['target']['ref']==scope,'exact Goal/Project membership differs')
    need(definition['single_goal_coordination'] is True,'one Goal coordination required')
    return True
