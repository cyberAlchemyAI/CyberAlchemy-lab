"""Complete documentation specimens bound to captured contracts, with no admission effect."""
from pathlib import Path
from copy import deepcopy
from html import escape
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def build():
    import jsonschema
    catalog = json.loads((ROOT / 'research/catalog.json').read_text())
    target = ROOT / 'examples'
    # Actual local files make the worked comparison reproducible; every identifier
    # belongs to invented data, rather than a real customer's information.
    input_data = {'snapshot':'S1', 'account':'Northstar', 'filters':{'status':'active'}, 'required_ids':list(range(1,10001))}
    output_data = {'output':'E12', 'snapshot':'S1', 'account':'Northstar', 'filters':{'status':'active'}, 'exported_ids':list(range(1,9801))}
    save(target/'S1.json', input_data); save(target/'E12.json', output_data)
    missing = sorted(set(input_data['required_ids']) - set(output_data['exported_ids']))
    comparison = {'method':'identifier-difference@2', 'input':'S1.json', 'input_sha256':digest(target/'S1.json'),
                  'output':'E12.json', 'output_sha256':digest(target/'E12.json'), 'account':'Northstar',
                  'filters':{'status':'active'}, 'required_count':10000, 'exported_count':9800,
                  'missing_ids':missing, 'missing_count':len(missing),
                  'claim':'Identifier coverage fails for this exact saved output; cause, wider impact and recovery are unresolved.'}
    save(target/'comparison.json', comparison)
    scope = 'example:Northstar:S1:status-active:E12'
    ref = lambda kind: 'example:' + kind + '@1'
    payloads = {
      'work':dict(project_ref=ref('project'), goal_refs=[ref('goal')],
          work_statement='Compare required identifiers from S1 for Northstar and status=active against E12; prepare a bounded omission assessment.',
          input_refs=['example:S1','example:E12','example:definition-completeness@1.0.0-candidate.1'],
          output_refs=[ref('comparison'),ref('failure-assessment')], completion_state='comparison saved; assessment prepared; owner review pending'),
      'operational-observation':dict(project_ref=ref('project'), action_ref=ref('compare-action'), observed_at='2026-10-11T10:04:00Z',
          datum='Identifier comparison found 200 required IDs absent from E12: 9801 through 10000.', method_ref='example:identifier-difference@2',
          evidence_refs=[ref('comparison')], interpretation_posture='Omission observed in the fixed scope; cause is unresolved.'),
      'evidence-set':dict(source_refs=['example:S1','example:E12'], item_refs=[ref('comparison'),ref('operational-observation')],
          coverage_statement='Identifier coverage for S1, Northstar, status=active, E12, using method 2.',
          limitations=['Values were not compared.','Cause, other accounts, downstream impact and recovery were not established.']),
      'failure-occurrence':dict(subject_ref='example:E12', expected_boundary_ref='example:definition-completeness@1.0.0-candidate.1',
          observed_manifestations=['200 required identifiers absent'], detection_evidence_refs=[ref('comparison')], occurrence_posture='established in this fictional comparison',
          cause_posture='unresolved', impact_refs=[], response_action_refs=[ref('compare-action')], recovery_posture='unestablished', residue_refs=[ref('open-questions')]),
      'classification-assignment':dict(subject_ref=ref('failure-occurrence'),subject_version_ref=ref('failure-occurrence'),
          scheme_version_ref='example:failure-manifestation-scheme@1', axis_ref='example:observed-manifestation', value_ref='example:missing-required-identifiers',
          basis='Saved identifier difference; classification of manifestation only.', action_ref=ref('classify-action'), method_ref='example:classification-method@1',
          implementation_ref='example:manual-review@1', evidence_refs=[ref('comparison')], effective_period='this saved occurrence only', status='candidate'),
      'failure-assessment':dict(occurrence_ref=ref('failure-occurrence'),mode_assignment_ref=ref('classification-assignment'),
          occurrence_posture='established omission in E12',mode_posture='candidate classification: missing required identifiers; not a causal mechanism',
          cause_hypothesis_refs=[],impact_posture='Output omission established; downstream uses and other accounts unresolved.',
          containment_posture='No containment established.',recovery_posture='No recovery established.',uncertainty_refs=[ref('open-questions')]),
      'agent-assignment':dict(eligible_agent_ref=ref('agent-profile'), intent_ref=ref('intent'), project_ref=ref('project'),work_ref=ref('work'),
          owner_ref='example:service-owner',period='2026-10-11T09:45:00Z/2026-10-11T10:15:00Z',expected_output_refs=[ref('comparison'),ref('failure-assessment')],
          stop_conditions=['Pause if a selected view is unusable.','Stop if the delegation expires or is revoked.','Do not deploy or close the incident.']),
      'delegation':dict(delegator_principal_ref='example:service-owner',eligible_agent_ref=ref('agent-profile'),scope_refs=[scope],
          allowed_action_kinds=['inspect-saved-inputs','compare-identifiers','record-candidate-through-approved-route','prepare-proposal'],
          policy_refs=[ref('investigation-policy')],approval_gate_refs=[ref('owner-review')],
          effective_period='2026-10-11T09:45:00Z/2026-10-11T10:15:00Z',revocation_state='not revoked in this invented scenario',redelegation_allowed=False),
      'agent-session':dict(agent_instance_ref=ref('agent-instance-12'),assignment_ref=ref('agent-assignment'),context_view_ref=ref('context-view-3'),
          ontology_view_ref=ref('ontology-view-3'),policy_refs=[ref('investigation-policy')],authority_envelope_ref=ref('delegation'),
          input_refs=['example:S1','example:E12'],budget_refs=['example:30-minute-budget'],event_cursor='example:session-12-event-7',
          session_memory=dict(selected_input_refs=['example:S1','example:E12'],working_record_refs=[ref('failure-assessment')],
                              unresolved_questions=['What caused the omission?','What is the wider impact?','Has recovery occurred?'],expires_with_session=True),
          termination_state='paused at 10:10 because task view 3 expired; end instance when session terminates'),
    }
    preference = {
      'work':('member-of','source','project'), 'operational-observation':('originates-from','source','source'),
      'evidence-set':('member-of','source','project'), 'failure-occurrence':('evidence-bears-on','target','operational-observation'),
      'classification-assignment':('evidence-bears-on','target','operational-observation'),
      'failure-assessment':('evidence-bears-on','target','operational-observation'),
      'agent-assignment':('member-of','source','project'), 'delegation':('declares-effect-on','target','decision'),
      'agent-session':('consumes-view','source','context-view'),
    }
    specimens = {}
    for key,payload in payloads.items():
        relation,direction,other = preference[key]
        rule = next(r for r in catalog['relations'] if r['predicate']==relation)
        pair={'source_kind':key if direction=='source' else other,'target_kind':other if direction=='source' else key}
        assert pair in rule['allowed_endpoint_pairs'], (key,pair)
        specimens[key] = dict(schema_version='cyberalchemy-lab-'+key+'/v1',node_id=ref(key),kind=key,
          name=key.replace('-',' ').title()+' for the Northstar investigation',lifecycle_state='candidate',authority_effect='none',
          owner_ref='example:service-owner',scope_ref=scope,evidence_refs=[ref('comparison')],challenge_route='example:owner-review',successor_refs=[],
          relation_refs=[dict(relation_kind_ref='relation.'+relation,direction=direction,counterpart_kind=other,counterpart_ref=ref(other))],
          payload=payload,claim_ceiling='Documentation candidate only. It grants no access, admission, deployment or incident closure.')
    specimens['context-view'] = dict(authority_effect='none',kind='context-view',node_id=ref('context-view-3'),owner_ref='example:service-owner',scope_ref=scope,
      status='candidate-unadmitted',request_ref=ref('context-request'),context_ref=ref('context'),context_version_ref='example:context@3',source_epoch='example:project-epoch@3',
      generated_at='2026-10-11T09:50:00Z',expires_at='2026-10-11T10:10:00Z',
      included_material=[dict(source_ref='example:S1',selector='required_ids for account=Northstar and status=active',sha256=digest(target/'S1.json')),
                         dict(source_ref='example:E12',selector='exported_ids',sha256=digest(target/'E12.json'))],excluded_material=[dict(source_ref='example:other-accounts',reason='Outside the task scope.')],
      lineage_refs=['example:project-state@3'],limitations=['The view grants no permission.','Unusable at or after its expiry.'],
      selection_basis='Task request selects the fixed input and saved output for identifier comparison.',owner_route='example:service-owner-review',challenge_route='example:view-challenge',
      claim_ceiling='Documentation candidate; no view generated by the Lab and no permission conveyed.')
    save(target/'finite-residue-model.json',{'states':['r1','r2','r3','r4','r5'],'probabilities':[0.2]*5,'assumption':'Five equally likely distinguishable residue states in a toy model; not incident evidence.'})
    specimens['measurement-method'] = dict(authority_effect='none',kind='measurement-method',node_id='example:uniform-residue-entropy@1',owner_ref='example:model-owner',scope_ref='example:finite-residue-model@1',
      status='candidate-unadmitted',name='Entropy of five equally likely residue states',property='residue entropy',entropy_register='finite-microcanonical',
      source_operation_ref=ref('toy-source-operation'),residue_type_ref='example:five-distinguishable-residue-states@1',observable_kind='shannon-entropy',
      mathematical_reading='For five equally likely distinguishable states, H = -sum(p_i log2(p_i)) = log2(5).',
      scope_kind='finite',procedure='Select the five-state model, verify the declared equal probabilities, compute log2(5) and save the receipt.',
      conditions=['Exactly five distinct states.','Each probability is 0.2.','Probabilities sum to one.'],unit='bits',
      uncertainty_rule='Zero model-input uncertainty under the stated toy assumptions; floating-point result rounded to 15 decimal places.',claim_status='review',authority_treatment='non-governing',
      interpretation='Uncertainty among five declared model states; supplies no evidence about the Northstar omission or its cause.',
      owner_route='example:model-owner-review',challenge_route='example:measurement-challenge',claim_ceiling='Documentation candidate method for a toy model only; no incident measurement or authority.')
    specimens['measurement-result'] = dict(authority_effect='none',kind='measurement-result',node_id=ref('measurement-result'),owner_ref='example:service-owner',scope_ref=scope,
      status='candidate-unadmitted',method_ref='example:uniform-residue-entropy@1',subject_ref='example:finite-residue-model@1',residue_ref='example:five-distinguishable-residue-states@1',source_operation_ref=ref('toy-source-operation'),
      entropy_register='finite-microcanonical',observable_kind='shannon-entropy',mathematical_reading='H = log2(5) bits under the five-state uniform model.',
      scope_kind='finite',value=2.321928094887362,unit='bits',uncertainty=dict(value=0,interpretation='No input uncertainty within the invented model; rounding applies to the floating-point representation.'),
      claim_status='review',authority_treatment='non-governing',observed_at='2026-10-11T10:04:00Z',evidence_ref='example:finite-residue-model@1',receipt_ref='example:finite-model-computation@1',
      owner_route='example:model-owner-review',challenge_route='example:measurement-challenge',claim_ceiling='Toy-model documentation result; no incident omission measurement or accepted finding.')
    specimens['measurement-result']['scope_ref']='example:finite-residue-model@1'
    definition_source = next(d for d in catalog['definitions'] if d['term']=='Definition')
    definition = deepcopy(json.loads((ROOT/definition_source['source']).read_text()))
    dtype = next(t for t in catalog['artifact_types'] if t['artifact_type_ref']=='cal.artifact-type.definition/v2')
    definition.update(schema_version='cyberalchemy-lab-definition/v2',definition_id='example.definition.export-identifier-completeness',version='1.0.0-candidate.1',
      term='Export identifier completeness',aliases=[],semantic_owner_ref='example:service-owner',schema_ref='cal.schema.definition/v2',schema_digest=dtype['schema_sha256'],
      scope=dict(authority_scope_ref=scope,applicability='Identifier coverage of an export E from fixed snapshot S, declared account A and filters F.',
                 exclusions=['Value accuracy.','Live-source consistency.','Access permission.','Incident recovery or closure.']),
      boundaries=['S, A, F and E must be fixed and identified before applying the criterion.','Extra identifiers require a separate exclusivity criterion.'],
      source_refs=[],primary_consumer_refs=[ref('work'),ref('failure-assessment')],index_entry=dict(index_ref='example:proposed-definition-index',entry_id='example.definition.export-identifier-completeness'),
      drift_route=dict(owner_ref='example:service-owner',audit_ref='example:definition-drift-review',challenge_ref='example:definition-challenge'),
      evidence_refs=['example:criterion-proposal'],residue_refs=['example:source-posture-and-owner-acceptance-pending'],typed_relations=[],
      claim_ceiling='Schema-complete documentation specimen. Admitted source posture, registry synchronization and an exact owner decision still require independent review.')
    definition['classification'].update(artifact_type_ref='cal.artifact-type.definition/v2',lifecycle_posture_ref='example:candidate-authored')
    definition['source_direction'].update(generator_ref='cal.generator.definition-markdown/v2')
    # The type's own projection generator is not the Definition generator.
    # Keep the missing binding explicit rather than using an unrelated real digest.
    definition['source_direction']['generator_sha256']='0'*64
    definition['residue_refs'].append('example:definition-generator-digest-unresolved')
    definition['voices']['scientific_formal'].update(normative_statement='For a fixed input snapshot S, account A, filters F and output E, export identifier completeness holds exactly when every identifier required by S, A and F appears in E.',
      formal_expression='CompleteIds(S,A,F,E) iff RequiredIds(S,A,F) subseteq ExportedIds(E).',
      notation=[dict(symbol=s,meaning=m) for s,m in [('S','Fixed input snapshot'),('A','Declared account'),('F','Declared filters'),('E','Saved export output')]],
      boundary_conditions=definition['boundaries'],testable_conditions=['For S1, Northstar, status=active and E12, the saved comparison has 200 missing required identifiers.'])
    definition['voices']['plain_language']['explanation']='Every required row identifier for the chosen account and filters must appear in the output.'
    definition['voices']['domain_context'].update(workspace_ref='example:Northstar-investigation',explanation='The Northstar agent uses this proposed criterion to examine the saved export.',examples=['S1, Northstar, status=active, E12: incomplete by identifier coverage.'])
    specimens['definition'] = definition
    rows=[]
    for key,record in specimens.items():
        row = dtype if key=='definition' else next(t for t in catalog['artifact_types'] if t['semantic_kind']==key)
        schema_path=ROOT/row['schema_source'];schema=json.loads(schema_path.read_text())
        validator=jsonschema.Draft202012Validator(schema)
        errors=list(validator.iter_errors(record));assert not errors,(key,[e.message for e in errors])
        bad=deepcopy(record)
        path=['scope','applicability'] if key=='definition' else (['payload',next(iter(schema['properties']['payload']['required']))] if 'payload' in schema['properties'] else [next(x for x in schema['required'] if x not in ['authority_effect','kind','node_id'])])
        branch=bad
        for part in path[:-1]:branch=branch[part]
        removed=branch.pop(path[-1]);negative=list(validator.iter_errors(bad));assert len(negative)==1,(key,negative)
        save(target/(key+'.json'),record);save(target/(key+'-missing-field.json'),bad)
        rows.append(dict(key=key,title=key.replace('-',' ').title(),class_= 'complete-schema-checked',format_ref=row['artifact_type_ref'],
          schema_source=row['schema_source'],schema_sha256=digest(schema_path),contract_source=row['source'],contract_sha256=digest(ROOT/row['source']),
          valid_file='examples/'+key+'.json',invalid_file='examples/'+key+'-missing-field.json',defect='/'+ '/'.join(path),
          expected='Complete specimen passes selected JSON Schema; one missing required field fails. Admission and semantic obligations are assessed separately.',
          valid_sha256=digest(target/(key+'.json')),invalid_sha256=digest(target/(key+'-missing-field.json')),
          schema_errors=[dict(path=list(e.path),message=e.message) for e in negative]))
    patterns=[]
    for relation,source,other,qualifiers in [
      ('member-of','work','project',{'membership_role':'incident investigation'}),
      ('evidence-bears-on','operational-observation','failure-assessment',{'polarity':'supports scoped occurrence only'}),
      ('acts-for','agent-instance','principal',{'delegation_ref':ref('delegation'),'scope_ref':scope,'effective_period':'09:45–10:15 UTC','revocation_state':'not revoked in the scenario'}),
      ('consumes-view','agent-session','context-view',{'consumption_purpose':'identifier comparison'})]:
        rule=next(r for r in catalog['relations'] if r['predicate']==relation)
        props=rule['qualifier_contract']; required=props['required_axes']
        # Exact qualifier names differ by relation; values are explanations, not inferred permissions.
        qualifiers={key:qualifiers.get(key,'Northstar bounded investigation') for key in required}
        qschema=dict(type='object',additionalProperties=False,properties=props['properties'],required=required)
        jsonschema.validate(qualifiers,qschema)
        assert {'source_kind':source,'target_kind':other} in rule['allowed_endpoint_pairs']
        patterns.append(dict(relation=relation,source_kind=source,target_kind=other,qualifiers=qualifiers,
          counterexample=dict(source_kind=other,target_kind=source),failure='Reversed ordered pair is not declared.',
          source=rule['source'],sha256=digest(ROOT/rule['source'])))
        assert {'source_kind':other,'target_kind':source} not in rule['allowed_endpoint_pairs'], relation
    manifest=dict(version=1,authority_effect='none',examples=rows,relations=patterns,
      semantic_review=['All record references beginning example: are invented scenario identities; they have no registry standing.',
        'The source/output/difference files are real local teaching data. Cardinality is computed from identifiers, not inferred from row counts.',
        'The definition specimen is structurally complete but has unresolved source posture, Definition generator binding and acceptance obligations. Its all-zero generator digest is an unresolved placeholder, not verified content identity.',
        'A Context View can be structurally valid after expiry; usability is a separate time-sensitive check.',
        'The session specimen expires its memory on termination; the selected schema permits booleans but semantic requirements narrow usable values.',
        'Classification describes a manifestation, not a causal mechanism. No recovery or closure is established.'],
      applicability=dict(in_scope='S1 / Northstar / status=active / E12 identifier coverage',outside_case='An export containing every required identifier but incorrect values satisfies this coverage criterion; value accuracy needs its own definition.'))
    save(ROOT/'research/documentation-examples.json',manifest)
    return manifest


def content():
    manifest=json.loads((ROOT/'research/documentation-examples.json').read_text())
    out=['<header class="start-masthead"><p class="docs-breadcrumb">CyberAlchemy Lab / Reference examples</p><h1>Complete record examples</h1><p class="start-deck">Inspect the required fields, then compare a record with one precise defect.</p></header>',
      '<section id="example-standing"><h2>What these examples establish</h2><p>These are complete documentation specimens against the selected record schemas. Their invented <code>example:</code> identities have no registry standing. Passing a schema checks representation; it does not accept a record, establish its claims or grant permission. The links open local JSON files.</p><p>The <a href="examples/S1.json">saved input S1</a>, <a href="examples/E12.json">output E12</a> and <a href="examples/comparison.json">comparison receipt</a> reproduce the fixed Northstar example: 10,000 required identifiers, 9,800 exported and 200 confirmed missing.</p></section>']
    for row in manifest['examples']:
        key=row['key'];raw=json.loads((ROOT/row['valid_file']).read_text());
        out.append('<section id="example-'+key+'"><h2>'+escape(row['title'])+'</h2><p>Selected format: <a href="lab-reference-library.html#type-'+slug(row['format_ref'])+'">'+escape(row['format_ref'])+'</a>.</p>')
        if key=='definition':out.append('<p>The criterion binds snapshot, account, filters and output. Source posture, index synchronization and owner acceptance still require review. The all-zero generator digest explicitly marks an unresolved binding: replace it with the actual selected Definition generator’s digest before relying on that binding. Correct values are outside the identifier-coverage criterion.</p>')
        if key in ['measurement-method','measurement-result']:out.append('<p>The selected carrier is specialized for residue entropy although the semantic definition is broader. This separate <a href="examples/finite-residue-model.json">toy model</a> has five equally likely states: H = log₂(5) ≈ 2.322 bits. It supplies no Northstar incident evidence. The incident count belongs in its saved comparison and observation.</p>')
        if key=='context-view':out.append('<p>The specimen expires at 10:10 UTC. It still passes the schema after that time, but the agent cannot rely on it as a usable task view.</p>')
        if key=='delegation':out.append('<p>The fields describe the proposed permission envelope. This candidate JSON does not issue a real grant. Verify the delegator’s authority and the exact decision before acting.</p>')
        out.append('<p><a href="'+row['valid_file']+'">Complete JSON</a> · <a href="'+row['invalid_file']+'">Contrasting JSON</a></p><p><strong>One defect:</strong> the contrasting record omits <code>'+escape(row['defect'])+'</code>. The selected schema rejects that omission.</p><details class="specimen-details"><summary>Read the complete specimen</summary><pre><code>'+escape(json.dumps(raw,ensure_ascii=False,indent=2))+'</code></pre></details></section>')
    out.append('<section id="connection-examples"><h2>Read a declared connection</h2><p>A record’s local connection reference is not the complete relation assertion. The ordered endpoint kinds and required qualifiers below come from the selected relation rule. These patterns convey no permission.</p>')
    for p in manifest['relations']:
        out.append('<h3>'+escape(p['relation'])+'</h3><p><code>'+escape(p['source_kind'])+'</code> → <strong>'+escape(p['relation'])+'</strong> → <code>'+escape(p['target_kind'])+'</code></p><pre><code>'+escape(json.dumps(p['qualifiers'],ensure_ascii=False,indent=2))+'</code></pre><p><strong>Counterexample:</strong> reversing these endpoint kinds fails the declared ordered signature. An arrow drawn in an explanatory diagram does not declare a new connection.</p>')
    out.append('</section><section id="definition-boundary"><h2>Recognize a semantic boundary</h2><p>Suppose every required identifier appears in the export, but several email addresses have incorrect values. The identifier-coverage definition is satisfied; it says nothing about value accuracy. This is a boundary of the claim, not a malformed record.</p><p><a href="prepare-incident-assessment.html">Prepare an incident assessment →</a></p></section>')
    return '\n'.join(out)


if __name__=='__main__':
    result=build();print(json.dumps({'examples':len(result['examples']),'relations':len(result['relations'])}))
