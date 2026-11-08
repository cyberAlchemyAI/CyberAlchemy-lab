"""Reviewed question-to-topic judgments; aliases do not merge Lab concepts."""
QUERIES = [
 ('How do I inspect the Lab without a store?', 'runtime-first-inspection.html', 'The admitted public inspection task.'),
 ('How do I prepare local Work?', 'runtime-local-work.html', 'Separate owned disposable local Work preparation.'),
 ('How do I recover and retry safely?', 'runtime-recovery.html', 'Retry and recovery boundaries.'),
 ('How do I use Paperclip as a Lab reader?', 'runtime-paperclip.html', 'Bounded Paperclip reader scope.'),
 ('What is the runtime status and evidence?', 'runtime-status.html', 'Dated evidence and current limitations.'),
 ('Where is runtime state and short memory?', 'runtime-state-memory.html', 'State ownership and ephemeral memory.'),

 ('what lets an agent act?', 'resume-agent-work.html#resume-authority', 'Current scoped authority, separate from expected participation.'),
 ('where is long-term memory?', 'resume-agent-work.html#resume-reconstruct', 'Durable Project State supplies newly selected views; machine session memory expires.'),
 ('what proves an export is complete?', 'prepare-incident-assessment.html#assessment-inputs', 'The bounded identifier criterion specifies the claim and exact input scope.'),
 ('can I close the incident?', 'prepare-incident-assessment.html#assessment-review', 'Assessment preparation and incident closure have separate conditions.'),
 ('does Accept reserve capacity?', '../craft-documentation-proposal/craft-model.html#typed-model-a-reservation-is-a-different-responsibility', 'A pure Calculation classifies; an Operation changes state.'),
 ('how do I assess missing export rows?', 'prepare-incident-assessment.html', 'Outcome-oriented preparation of a bounded assessment.'),
 ('account filters snapshot', 'prepare-incident-assessment.html#assessment-inputs', 'Scope is part of the criterion.'),
 ('are counts enough?', 'prepare-incident-assessment.html#assessment-compare', 'The comparison preserves actual identifiers.'),
 ('is pagination the cause?', 'prepare-incident-assessment.html#assessment-output', 'Occurrence is established, cause remains unresolved.'),
 ('is the repair deployed?', 'prepare-incident-assessment.html#assessment-review', 'A saved proposal does not establish deployment.'),
 ('how do I know a record is accepted?', 'read-record.html#record-standing', 'Check standing and owner decision independently.'),
 ('schema valid means accepted?', 'read-record.html#record-standing', 'Schema validity and admission are distinct.'),
 ('what is the selected version?', 'read-record.html#record-select', 'Select exact record content and applicable contract.'),
 ('how do I prepare a definition?', 'prepare-definition.html', 'Practical preparation of one candidate meaning.'),
 ('definition plain language formal meaning', 'prepare-definition.html#definition-voices', 'Non-normative voices preserve the formal scope.'),
 ('non collapse definition review', 'prepare-definition.html#definition-review-material', 'Source, consistency and orthogonality review obligations.'),
 ('what if the context expires?', 'resume-agent-work.html', 'Pause, reconstruct task knowledge and check current authority.'),
 ('does a new session inherit permission?', 'resume-agent-work.html#resume-authority', 'Permission is checked for the intended continuation.'),
 ('does an agent remember across sessions?', 'resume-agent-work.html#resume-session', 'New instance and session memory; durable state has separate ownership.'),
 ('assignment versus delegation', 'resume-agent-work.html#resume-authority', 'Participation is distinct from permission.'),
 ('context view versus project state', 'resume-agent-work.html#resume-reconstruct', 'A selected derived view depends on durable source state.'),
 ('authority versus provenance', 'governance-lab-reference.html#governance', 'Governing meaning and permission differ from source traceability.'),
 ('provenance proves truth?', 'governance-lab-reference.html#evidence', 'A source trail does not accept or establish every associated claim.'),
 ('accepted code versus activated code', 'governance-lab-reference.html#change', 'Acceptance and activation have their own lifecycle conditions.'),
 ('is an ontology graph authority?', 'governance-lab-reference.html#records', 'Derived graph representation is not a competing authority source.'),
 ('which way does member of point?', 'record-examples.html#connection-examples', 'Ordered kinds and mandatory qualifiers constrain a relation.'),
 ('complete Work JSON example', 'record-examples.html#example-work', 'Full specimen and one required-field failure.'),
 ('valid expired view', 'record-examples.html#example-context-view', 'Structural validity does not establish current usability.'),
 ('measurement count entropy', 'record-examples.html#example-measurement-result', 'The selected specialized carrier differs from a simple omission count.'),
 ('incorrect values all identifiers present', 'record-examples.html#definition-boundary', 'A coverage criterion does not establish value accuracy.'),
]


def bind(entries):
    """Check independently selected exact destinations. Never change the index.

    Judgments are not aliases, prefix searches or shortest-record guesses.
    A removed destination fails the build and requires editorial review.
    """
    judgments=[]
    for query,target,reason in QUERIES:
        assert any(entry['href']==target for entry in entries),(query,target)
        judgments.append(dict(query=query,acceptable=[target],rationale=reason,kind='task-question'))
    for name in ['Work','Operational Observation','Evidence Set','Failure Assessment','Agent Assignment','Delegation','Agent Session','Context View','Definition']:
        identifier='def-cal-definition-'+name.lower().replace(' ','-')
        target='reference/'+identifier+'.html#'+identifier
        assert any(e['href']==target and e['title']==name for e in entries),name
        judgments.append(dict(query=name,acceptable=[target],rationale='Exact Definition reference title.',kind='exact-title'))
    from runtime_docs import selected as runtime_selected
    from pathlib import Path
    _,runtime_narrative,_=runtime_selected(Path(__file__).resolve().parent)
    for page in runtime_narrative['pages']:
        judgments.append(dict(query=page['title'],acceptable=[page['site_file']],rationale='Exact reviewed runtime task title.',kind='exact-title'))
    return judgments
