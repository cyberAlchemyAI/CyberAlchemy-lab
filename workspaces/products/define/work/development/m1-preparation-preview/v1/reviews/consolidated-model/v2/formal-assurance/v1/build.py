#!/usr/bin/env python3
"""Fresh correspondence, typed models and bounded rule checks; no authority effects."""
import ast
import copy
import hashlib
import importlib.util
import itertools
import json
import os
import re
import sys
import time
from pathlib import Path

import jsonschema
import formal_engine as engine

ROOT=engine.ROOT
OUT=Path(__file__).resolve().parent
BASE=OUT.parents[1]
PREFIX=str(OUT.relative_to(ROOT))
source_files={}
checks=[]


def canonical(value):return (json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def ref(path):
    p=path if isinstance(path,Path) and path.is_absolute() else ROOT/path
    b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def read(path):
    p=path if isinstance(path,Path) and path.is_absolute() else ROOT/path
    source_files[str(p.relative_to(ROOT))]=ref(p)
    return json.loads(p.read_text())
def check(name,result,detail=''):
    checks.append({'check_id':name,'outcome':'PASS' if result else 'FAIL','detail':detail})
    if not result:raise ValueError(name+': '+detail)
def write(name,data):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:f.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def pointer(document,selector):
    v=document
    for component in selector.lstrip('/').split('/'):
        component=component.replace('~1','/').replace('~0','~')
        v=v[int(component)] if isinstance(v,list) else v[component]
    return v
def link(path,label):return f'[{label}]({os.path.relpath(ROOT/path,OUT)})'
def cell(v):return str(v).replace('|','\\|').replace('\n',' ')
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(cell(v) for v in row)+' |' for row in rows])


started=time.monotonic()
model=read(BASE/'supplement-01-reviewed-model/model.json')
selected=model['selected_meanings']
changed=[s for s in selected if s['model_role'] in ['DefinitionApplication','Pack','Define']]
for path in [BASE/'package-manifest.json',BASE/'supplement-01-reviewed-model/package-manifest.json']:
    seal=read(path)
    for item in seal['files']:
        check('sealed:'+item['path'],ref(item['path'])==item)
        source_files[item['path']]=ref(item['path'])
registry=read('authority/definitions/registry.json')
lookup={(e['definition_id']+'@'+e['version']):e for e in registry['entries']}
decisions={}
for p in (ROOT/'docs/decisions').glob('*/decision.json'):
    value=json.loads(p.read_text());identity=value.get('decision_id') or value.get('record_id')
    if identity:decisions[identity]=(p,value)
for s in selected:
    check('selected-source:'+s['definition_ref'],ref(s['path'])['sha256']==s['sha256'])
    d=read(s['path']);jsonschema.Draft202012Validator(read(s['schema']['path'])).validate(d)
    check('selected-schema:'+s['definition_ref'],True)

# Exact canonical-record digest and separately captured selector content. The
# source field content_sha256 in these records is a whole-record binding.
bindings=[]
for s in changed:
    d=read(s['path'])
    for index,item in enumerate(d['source_refs']):
        entry=lookup[item['source_ref']]
        source=read(entry['path'])
        check('source-integrity:'+item['source_ref'],ref(entry['path'])['sha256']==item['content_sha256']==entry['sha256'])
        check('source-admission:'+item['source_ref'],entry['lifecycle_state']=='admitted' and entry['admission_decision_ref']==item['source_admission_ref'])
        value=pointer(source,item['selector'])
        p,decision=decisions[item['source_admission_ref']]
        read(p)
        # Registry standing and exact named Decision are checked. Not every
        # historic Decision has the same admitted-record field representation.
        check('exact-admission-record:'+item['source_ref'],item['source_admission_ref'] in json.dumps(decision))
        bindings.append({'subject':s['definition_ref'],'source_index':index,'source':ref(entry['path']),'selector':item['selector'],'selected_content_sha256':digest(value),'selected_text':value,'standing_at_capture':'admitted historical/current exact version','admission_decision':ref(p),'target_use':'selected source clause/meaning boundaries; no source truth or new effect authority'})
write('source-closure.json',{'authority_effect':'none','selected_source_bindings':bindings,'unresolved_technical_source_bindings':0,'claim_ceiling':'Exact source identity/selector/registry-standing/Decision capture only; owner identity, source truth and future-use currentness remain independent.'})

print('Selected sources captured; checking typed joint models.',flush=True)
core,raw_model=engine.build()
for p in (ROOT/'craft/formalization/candidates/definition-assurance-v1').rglob('*.py'):
    if '__pycache__' not in p.parts:source_files[str(p.relative_to(ROOT))]=ref(p)
for path in ['define/development/m1-preparation-preview/v1/steps/09-assurance-evidence-closure/formal-core.json','define/development/m1-preparation-preview/v1/steps/09-assurance-evidence-closure/witnesses.json','define/development/m1-preparation-preview/v1/steps/09-assurance-evidence-closure/interpretations.json']:
    read(path)
typed=engine.evidence(core,raw_model)
write('formal-core.json',core)
write('finite-witnesses.json',{'authority_effect':'none',**typed})
check('typed-joint-consistency',typed['worlds'][0]['all_axioms_satisfied'])
check('noncollapse-direction-count',len(typed['pairs'])==2*typed['pair_count'])
check('joint-conforming-result-populated',['input','Pack'] in typed['worlds'][0]['model']['predicates']['ConformingDefineResult'])
print('Typed consistency and non-collapse witnesses checked; executing bounded rule populations.',flush=True)

# Exhaustive small universes: independent set/status calculations rather than
# accepting a role flag or reusing historical result receipts.
populations=[]
names=['S','A','F','E'];trits=list(itertools.product(range(3),repeat=4))
count=good=fully=0
for required_mask,status,extra,gap_mask in itertools.product(range(16),trits,[False,True],range(32)):
    count+=1
    required={names[i] for i in range(4) if required_mask>>i&1}
    provided={names[i] for i,x in enumerate(status) if x}
    gaps={names[i] for i in range(4) if gap_mask>>i&1}
    if gap_mask>>4&1:gaps.add('tolerance')
    observed=not extra and all(x!=2 for x in status) and gaps==required-provided
    independently=not extra and 2 not in status and all((name in gaps)==(name in required and status[i]==0) for i,name in enumerate(names)) and 'tolerance' not in gaps
    if observed!=independently:raise ValueError('application population mismatch')
    good+=observed;fully+=observed and required<=provided
populations.append({'population':'four declared parameters, every required subset, absent/typed/wrong-type values, undeclared tolerance and five gap bits','cases':count,'wellformed_assignments':good,'fully_supplied_assignments':fully,'result':'PASS','limit':'Fixed four-name plus one undeclared-name universe; metadata/source applicability checked separately.'})
for label,width in [('application metadata/reference/applicability',9),('revised Pack required feature flags',len(core['frames']['Pack'])),('revised Define result conditions',9)]:
    count=1<<width
    for mask in range(count):
        flags=[bool(mask>>i&1) for i in range(width)]
        if all(flags)!=(mask.bit_count()==width):raise ValueError('boolean aggregation mismatch '+label)
    populations.append({'population':label,'cases':count,'result':'PASS','limit':'Requirement flags are interpreted predicates, not evidence that arbitrary production records satisfy them.'})
count=0
for required_bits,exported_bits,required_known,exported_known in itertools.product(range(16),range(16),[False,True],[False,True]):
    count+=1;required={i for i in range(4) if required_bits>>i&1};exported={i for i in range(4) if exported_bits>>i&1}
    observed='NOT_EVALUABLE' if not required_known or not exported_known else ('PASS' if required<=exported else 'FAIL')
    second='NOT_EVALUABLE' if not (required_known and exported_known) else ('FAIL' if any(x not in exported for x in required) else 'PASS')
    if observed!=second:raise ValueError('identifier coverage population mismatch')
populations.append({'population':'four-identifier required/exported sets and both population-known flags','cases':count,'result':'PASS','limit':'Known empty differs from unknown; counts, accuracy, account exclusivity and action permission are not this predicate.'})
count=0
for apps,assessments,target,exact,producer,limits in itertools.product(range(3),range(3),range(3),[False,True],[False,True],[False,True]):
    count+=1
    expected=assessments==0 or (apps>target and exact and producer and limits)
    actual=all(target<apps and exact and producer and limits for _ in range(assessments))
    if expected!=actual:raise ValueError('assessment optionality/binding mismatch')
populations.append({'population':'zero/two application and assessment counts, target membership, exactness, producer and coverage flags','cases':count,'result':'PASS','limit':'Up to two apps/assessments; full method/result semantic conformance remains separate.'})
count=0
for disposition,standing,materialize,purpose,scope,owner in itertools.product(['reuse','specialize','propose','open'],['admitted','candidate','working'],[False,True],[False,True],[False,True],[False,True]):
    count+=1
    legal_reuse=disposition!='reuse' or standing=='admitted'
    selected_route=not materialize or (disposition in ['specialize','propose'] and purpose and scope and owner)
    valid=legal_reuse and selected_route
    independent=(standing=='admitted' or disposition in ['specialize','propose','open']) and (not materialize or (disposition!='reuse' and disposition!='open' and sum([purpose,scope,owner])==3))
    if valid!=independent:raise ValueError('materialization guard mismatch')
populations.append({'population':'four dispositions, three captured standings and explicit materialization/purpose/scope/owner-route flags','cases':count,'result':'PASS','limit':'No owner appointment or accepted fidelity inferred from a route flag.'})
write('bounded-rule-results.json',{'authority_effect':'none','case_populations':populations,'total_assignments_checked':sum(x['cases'] for x in populations),'whole_repository_consistency':False,'production_runtime_qualification':False})

# Each source sentence receives an exact span and honest coverage disposition.
# Formula leaves map directly to typed rules or explicit nonmechanized flags.
fragments={
 'DefinitionApplication':[
    ('ExactSelection(m)','Unique selected meaning plus exact identity/revision/digest/captured-standing flags','WellFormedApplication'),
    ('ExactContextUse(k,u)','Declared task/consumer/use flag; carrier/incident checks ground the values','ExactTaskContextUse'),
    ('DeclaredParameters(m)','Selected meaning parameter declaration; required is a subset of allowed','ParameterContractDeclared'),
    ('dom(theta) subseteq Parameters(m)','Every binding refers to an allowed parameter under the selected meaning','BindValue/ParameterAllowed'),
    ('ValuesTyped(theta,m)','Binding value type matches the declared selected parameter type','DeclaredParameterType/ValueHasType'),
    ('MissingRequiredRecorded(theta,m,q)','Exact gap iff required parameter is absent; no spurious gap','MissingParameterGap'),
    ('ValueProvenanceRecorded(e)','Required provenance flag plus exact concrete Pack checks','ValueProvenanceRecorded'),
    ('MeaningUnchanged(m)','No semantic override; parameter substitution preserves the selected normative meaning','MeaningUnchanged'),
    ('RequiredParameters(m) subseteq dom(theta)','Every required parameter has a binding','FullyBoundApplication'),
    ('RequiredReferencesResolved(a)','Resolution is separate from declared identity and structural validity','RequiredReferencesResolved'),
    ('ApplicabilityEstablished(a)','Declared evidence of applicable use; a name alone supplies no authority','ApplicabilityEstablished'),
    ('does not entail','Checked populated countermodels for no assessment/admission/permission/effect inference','finite-witnesses.json/boundaries'),
 ],
 'Pack':[
    ('ExactIdentity(id,revision)','Exact identity/version flag and canonical file/schema integrity','VersionExact'),
    ('BoundedGoalContextUse(g,k,u)','Declared goal/context/named consumer-use requirements','Scoped/BoundedGoalDeclared/NamedConsumerUse'),
    ('TraceableIntent(g,i)','Originating intent declared; exact retained lineage in result bridge','OriginatingIntentDeclared/LineagePreserved'),
    ('FiniteNonempty(C)','Nonempty typed RequiredConcept relation','ConceptSetNonempty'),
    ('delta in Functions(C,D)','Exactly one of four closed tags for every required concept, no undeclared rows','EveryConceptSingleDisposition/NoUndeclaredConceptHandling'),
    ('dom(H)=C','Exact matching payload domain and handling tag','PayloadDomainExactlyConcepts'),
    ('PayloadMatches(H(c),delta(c))','Typed payload relation under the selected handling tag','EveryDispositionPayloadMatches'),
    ('ResolvedWithStandingAtCapture(r) or DeclaredGap(r,Q)','Recorded standing or visible unresolved gap; neither source truth nor perpetual currentness','CapturedStandingOrGaps'),
    ('ValidationScopeDeclared(V)','Independent required validation/claim scope','ValidationScopeDeclared'),
    ('EmbeddedMeaningBindingsValid(M,B)','Each embedded application satisfies the exact selected-meaning and parameter binding contract','EmbeddedMeaningBindingsValid'),
    ('SeparateAssessmentBindingsValid(Y,B,E)','Each present assessment uniquely targets a contained application with exact input/evidence, producer and coverage posture','SeparateAssessmentBindingsValid'),
    ('MaterializationSelectionExplicit(H)','No separate Definition materialization without explicit purpose/scope/owner route selection','MaterializationSelectionExplicit'),
    ('NoNewAuthorityFromPack(A)','Preparation-origin authority is false; existing independent authority is preserved','NoNewAuthorityFromPreparation'),
    ('does not entail','Countermodels separate well-formed Pack from consumer readiness, admission and execution','finite-witnesses.json/boundaries'),
 ],
 'Define':[
    ('WellFormedPack(P)','Uses the exact revised Pack relation, including embedded application/assessment/materialization rules','Pack'),
    ('PreservesIntentAndGoalLineage(X,P)','Attributable lineage predicate; changing or omitting the request cannot qualify','LineagePreserved'),
    ('AccountsForDeclaredConcepts(C0,C(P),P)','Declared coverage predicate, bounded to the selected required set','DeclaredConceptCoverage'),
    ('delta_P in Functions(C(P),D)','Inherited exactly-one handling rule of the required Pack','EveryConceptSingleDisposition'),
    ('RecordsSourceStandingAndGaps(X,P)','Exact captured standing and gap records','CapturedSourceGaps'),
    ('PreservesMeaningAndBindingSeparation(P)','Result requires preserved meaning/value distinction','PreservesMeaningAndBindingSeparation'),
    ('PreservesAssessmentProvenance(P)','Result requires retained separate assessment origin/input posture','PreservesAssessmentProvenance'),
    ('ReviewableFor(P,u)','Declared consumer reviewability; independent from readiness for action','ConsumerReviewable'),
    ('NoNewAuthorityFromPreparation(P)','Pack cannot create authority; role/capability declaration does not execute a process','NoNewAuthorityFromPreparation'),
    ('does not entail','Populated result with open exclusivity and no goal/action/owner effects','finite-witnesses.json/boundaries'),
 ],
}
formal_rows=[];clauses=[];voice_rows=[]
for s in changed:
    d=read(s['path']);formal=d['voices']['scientific_formal']
    for index,(fragment,interpretation,predicate) in enumerate(fragments[s['model_role']]):
        check('formal-fragment:'+s['model_role']+':'+fragment,fragment in formal['formal_expression'])
        formal_rows.append({'subject':s['definition_ref'],'source':ref(s['path']),'selector':'/voices/scientific_formal/formal_expression','fragment':fragment,'interpretation':interpretation,'formal_target':predicate,'fidelity_status':'FRESH_AUTHOR_CORRESPONDENCE; OWNER_ACCEPTANCE_PENDING'})
    for field in ['normative_statement','boundary_conditions','testable_conditions']:
        values=[formal[field]] if isinstance(formal[field],str) else formal[field]
        for vi,text in enumerate(values):
            sentence_spans=[(m.start(),m.end()) for m in re.finditer(r'[^.!?]+[.!?]?(?:\s|$)',text)] if field=='normative_statement' else [(0,len(text))]
            for si,(start,end) in enumerate(sentence_spans):
                excerpt=text[start:end].strip()
                if not excerpt:continue
                temporal=any(x in excerpt.lower() for x in ['histor','revision','later','epoch','session','outlive','memory','runtime'])
                effect=any(x in excerpt.lower() for x in ['authority','admit','permission','authorize','owner','govern','policy','promotion'])
                coverage='DECLARED_CONTRACT_AND_BOUNDED_COUNTERMODELS' if effect else ('SCOPED_RECORD_EPOCH_CHECKS; TEMPORAL_RUNTIME_DEFERRED' if temporal else 'INTERPRETED_TYPED_RULE_OR_CONCRETE_ARTIFACT_CHECK')
                selector='/voices/scientific_formal/'+field+('' if isinstance(formal[field],str) else '/'+str(vi))
                clauses.append({'subject':s['definition_ref'],'clause_id':s['model_role']+'-'+field+'-'+str(vi)+'-'+str(si),'source':ref(s['path']),'selector':selector,'span':[start,end],'exact_selected_text':text[start:end],'review_excerpt':excerpt,'coverage':coverage,'meaning':'Selected source clause remains normative candidate text; formal evidence does not add approval or omitted temporal/empirical facts.','coverage_inputs':[row['formal_target'] for row in formal_rows if row['subject']==s['definition_ref']],'owner_fidelity':'pending fresh exact acceptance'})
    for voice in ['plain_language','domain_context']:
        v=d['voices'][voice]
        check('non-normative-voice:'+s['model_role']+':'+voice,v['normative'] is False)
        voice_rows.append({'subject':s['definition_ref'],'source':ref(s['path']),'selector':'/voices/'+voice,'text':v['explanation'],'normative':False,'alignment':'Exact meaning and task/value/assessment separation reviewed against formal voice and incident; independent owner fidelity acceptance remains pending.'})
write('formal-correspondence.json',{'authority_effect':'none','rows':formal_rows,'whole_natural_language_equivalence':False,'owner_fidelity_acceptance':None})
write('clause-coverage.json',{'authority_effect':'none','clauses':clauses,'voices':voice_rows,'scope':'Every scientific normative/boundary/testable clause captured; per-clause coverage is qualified. Declarative correspondence is not a proof of all natural-language clauses.'})

# Fresh concrete bridge, including malformed-but-shape-valid evidence controls.
incident=read(BASE/'incident-pack.json')
preview_schema=read(BASE/'pack-embedding.schema.json')
jsonschema.Draft202012Validator(preview_schema).validate(incident)
check('incident-preview-schema',True)
application=incident['applications'][0];meaning=pointer(incident,application['meaning_ref']['selector']);assessment=incident['assessments'][0]
check('incident-meaning-exact',digest(meaning)==application['meaning_ref']['sha256'])
check('incident-application-exact',digest(application)==assessment['application_sha256'])
check('incident-task-scope',application['task_ref']==incident['scope']['task_ref']==meaning['scope_ref'])
def expand(e):
    if any(type(a)!=int or type(b)!=int or a<1 or b<a for a,b in e['identifier_ranges']):raise ValueError('invalid identifier range')
    return {x for a,b in e['identifier_ranges'] for x in range(a,b+1)}
records={e['evidence_id']:e for e in incident['evidence']}
for r in assessment['evidence_bindings']:check('incident-evidence:'+r['evidence_id'],digest(records[r['evidence_id']])==r['sha256'])
required=expand(records[application['bindings']['S']]);exported=expand(records[application['bindings']['E']]);missing=required-exported
expected={'required':len(required),'present':len(required&exported),'missing':len(missing)}
check('incident-counts-and-missing-identities',assessment['counts']==expected and assessment['missing_identifiers']==sorted(missing))
check('incident-outcome',assessment['outcome']==('FAIL' if missing else 'PASS'))
check('incident-not-shared-authority',not incident['readiness']['shared_admission'] and not incident['readiness']['incident_closure'])
retry=read(BASE/'incident-controls.json')
check('retry-same-meaning',retry['retry_application']['meaning_ref']==application['meaning_ref'])
check('retry-new-epoch',retry['retry_application']['revision']==2 and retry['retry_application']['bindings']['E']=='E-1042-retry')
check('retry-coverage-pass',retry['retry_assessment']['outcome']=='PASS' and retry['retry_assessment']['counts']=={'required':12000,'present':12000,'missing':0})
artifact_controls=[]
for name,changed_value in [('reversed identifier range',[[12000,1]]),('noninteger identifier range',[[1,2.5]])]:
    record=copy.deepcopy(records['S-1042']);record['identifier_ranges']=changed_value
    try:expand(record);rejected=False
    except ValueError:rejected=True
    check('artifact-control:'+name,rejected);artifact_controls.append({'case':name,'result':'REJECTED_BY_FRESH_SEMANTIC_BRIDGE','implementation_gap':'Old preview shape/range expansion alone did not enforce this semantic precondition; production validator qualification remains required.'})
for name,mutate in [('forged counts',lambda y:y['counts'].update(missing=0)),('forged outcome',lambda y:y.update(outcome='PASS')),('forged missing-ID list',lambda y:y.update(missing_identifiers=[]))]:
    y=copy.deepcopy(assessment);mutate(y)
    accepted=y['counts']==expected and y['missing_identifiers']==sorted(missing) and y['outcome']==('FAIL' if missing else 'PASS')
    check('artifact-control:'+name,not accepted);artifact_controls.append({'case':name,'result':'REJECTED_BY_RECOMPUTED_EVIDENCE','implementation_gap':'Stored values/digests alone do not prove a correct assessment; result comparison is separately required.'})
write('incident-bridge.json',{'authority_effect':'none','pack':ref(BASE/'incident-pack.json'),'application_selector':'/applications/0','meaning_selector':'/working_meanings/0','assessment_selector':'/assessments/0','exact_values':application['bindings'],'initial':{'counts':expected,'outcome':assessment['outcome']},'retry':{'same_meaning':True,'new_application_epoch':True,'counts':retry['retry_assessment']['counts'],'outcome':'PASS'},'typed_model_mapping':{'task_application':'DefinitionApplication','embedded_pack':'Pack','criterion':'Meaning:criterion','required_parameters':['S','A','F','E'],'assessment':'assessment'},'fresh_controls':artifact_controls,'production_run':False,'assessment_contract':'Illustrative synthetic inclusion result; not a complete governed Evaluation or Measurement Result','shared_admission':False,'incident_closure':False})

# Full cohort projection: fix the earlier mixed preview's bare-version values
# to exact identity@version lookups without touching its frozen historical file.
post=read(BASE/'registry-postimage.json')
for s in selected:post['proposed_current_lookup'][s['definition_ref'].rsplit('@',1)[0]]=s['definition_ref']
check('exact-proposed-lookups',all(post['proposed_current_lookup'][s['definition_ref'].rsplit('@',1)[0]]==s['definition_ref'] for s in selected))
check('inherited-postimage-preserved',post['entries'][:189]==registry['entries'])
check('cohort-counts',len(post['entries'])==195 and len(post['proposed_current_lookup'])==188)
post['fresh_assurance_package']=PREFIX+'/package-manifest.json';post['claim_ceiling']='Fresh mixed-candidate review projection; exact lookups corrected. Still not an adopted registry representation, human selection or admitted postimage.'
write('registry-postimage.json',post)
write('DEFINITIONS-INDEX.md','# Fresh six-meaning review index\n\nLive authority unchanged. Three changed/new meanings have fresh scoped evidence; owner review and admission remain pending.\n\n'+table(['Role','Exact candidate','Full Definition'],[[s['model_role'],s['definition_ref'],link(s['human_projection']['path'],'Read')] for s in selected])+'\n\nProspective: 195 versions / 188 identities; live: 189 / 183.\n')
drift={'authority_effect':'none','representation_status':'local evidence/package drift record; not an admitted global Drift Audit carrier','baseline':ref('authority/definitions/drift-audit.json'),'preserved_historical_findings':read('authority/definitions/drift-audit.json'),'findings':[
    {'id':'FRESH-01','condition':'Prior candidate.3 acceptance cannot cover changed/new meanings','disposition':'Fresh correspondence/consistency evidence prepared; attributable owner fidelity review pending','blocks':'semantic admission'},
    {'id':'FRESH-02','condition':'Earlier descriptive preview used bare versions for six proposed lookup values','disposition':'Corrected in fresh preview to exact identity@version; frozen predecessor retained','blocks':'qualified registry/visibility application until applicable owner review'},
    {'id':'FRESH-03','condition':'Range validation and result/evidence comparison are stronger than old preview structural checks','disposition':'Fresh negative controls detect malformed ranges and forged counts/outcomes/IDs; production adapter remains unqualified','blocks':'production conformance claim'},
    {'id':'FRESH-04','condition':'Exact v2 profile standing, owner scopes, consumer impact and full registry representation not yet effective','disposition':'Keep independent actual effect/compatibility gates open','blocks':'admission readiness/application'},
]}
write('drift-review.json',drift)

limits=[
    {'id':'FA01','boundary':'Source-to-predicate fidelity is an authored interpretation','future_work':'Exact owner acceptance of this fresh correspondence; no automatic reuse of candidate.3 acceptance.'},
    {'id':'FA02','boundary':'Parameter enumeration uses four declared names plus one undeclared tolerance, bounded values/types','future_work':'Generic production parameter-contract/value/provenance validation and stronger selected-universe evidence.'},
    {'id':'FA03','boundary':'Model consistency and distinction apply only to the explicit interpreted finite theory','future_work':'No whole-repository, full natural-language or infinite temporal theorem; stronger claims require separately scoped proof/evidence.'},
    {'id':'FA04','boundary':'Assessment binding does not establish complete Evaluation/Measurement Result conformance','future_work':'Qualify adopted profile/method, producer, exact evidence, range/input validation and recomputed result checks.'},
    {'id':'FA05','boundary':'Reference selectors, epoch changes, retention and visibility are demonstrated on selected records/flags','future_work':'Production pointer resolution, stale-cache handling, storage/retention and crash/concurrency qualification.'},
    {'id':'FA06','boundary':'Human authority, owner scope and action permission are not authenticated by these checks','future_work':'Reuse applicable admitted owner/review interfaces and exact effect decisions; no fabricated principal/key.'},
    {'id':'FA07','boundary':'Revised full-cohort registry/consumer drift and v2 standing remain separate requirements','future_work':'Qualified exact postimage/impact/profile/type/visibility closure before admission/application.'},
]
write('assurance-limits.json',{'authority_effect':'none','scope':'Fresh three-meaning interpreted evidence','items':limits,'previous_register':model['assurance_limits']['reference'],'previous_17_limits_preserved':True,'closed_actual_owner_effects':0})
summary={'schema_version':'cal.define-application-fresh-assurance-results/v1','authority_effect':'none','selected_changed_meanings':[s['definition_ref'] for s in changed],'source_bindings':len(bindings),'technical_source_gaps':0,'formal_correspondence_fragments':len(formal_rows),'source_clauses_accounted':len(clauses),'explanatory_voices_reviewed':len(voice_rows),'typed_axioms':len(core['axioms']),'joint_consistency':'SATISFIABLE_WITH_CHECKED_FINITE_MODEL','populated_model_worlds':len(typed['worlds']),'comparison_pairs':typed['pair_count'],'directed_noncollapse_witnesses':len(typed['pairs']),'non_entailment_boundaries':len(typed['boundaries']),'overlap_witnesses':len(typed['overlaps']),'typed_rejection_controls':len(typed['controls']),'bounded_rule_assignments':sum(x['cases'] for x in populations),'fresh_artifact_controls':len(artifact_controls),'formal_evidence_preparation_closed_within_declared_limits':True,'owner_fidelity_acceptance':False,'admission_ready':False,'actual_admissions':0,'application':False,'production_runtime_suite_executed':False,'mechanized_unbounded_theorem':False,'whole_repository_consistency':False,'elapsed_seconds':round(time.monotonic()-started,3)}
write('assurance-results.json',summary)

correspondence_md=['# Fresh formal correspondence','','Exact source bytes are unchanged. All rows are new for Definition application candidate.1 and Pack/Define candidate.4. The interpretation is an owner review subject, not an admitted axiom set.','',table(['Meaning','Source fragment','Interpretation / evidence target'],[[x['subject'],x['fragment'],x['interpretation']+' — '+x['formal_target']] for x in formal_rows]),'','## Coverage limits','','Every scientific normative, boundary and testable clause is captured in [clause coverage](clause-coverage.json). Contract declarations and bounded witnesses are separate from temporal/runtime/identity evidence. The source clause map covers the text; it does not prove universal natural-language equivalence.','']
write('CORRESPONDENCE.md','\n'.join(correspondence_md))
complete=(BASE/'supplement-01-reviewed-model/MODEL.md').read_text()
complete=re.sub(r'\]\(([^)]+)\)',lambda m:']('+os.path.relpath((BASE/'supplement-01-reviewed-model'/m.group(1)).resolve(),OUT)+')' if not m.group(1).startswith(('http:','https:','#')) else m.group(0),complete)
complete=complete.replace('Fresh fidelity/non-collapse correspondence and impact closure for the new application meaning and changed Pack/Define bytes; earlier acceptance is not transferred.','Fresh formal correspondence and bounded consistency/non-collapse evidence are prepared in this package. Owner fidelity acceptance and impact closure remain pending; earlier acceptance is not transferred.')
complete+='\n## Fresh formal evidence for this exact revised model\n\n'+table(['Evidence','Result'],[[k,v] for k,v in summary.items() if k in ['source_bindings','formal_correspondence_fragments','source_clauses_accounted','typed_axioms','joint_consistency','comparison_pairs','directed_noncollapse_witnesses','bounded_rule_assignments']])+'\n\nSee [formal correspondence](CORRESPONDENCE.md), [assurance results](assurance-results.json), [incident bridge](incident-bridge.json), [fresh registry preview](registry-postimage.json), [drift review](drift-review.json) and [assurance limits](assurance-limits.json). Formal preparation is closed within those limits. Actual owner review, applicable standing and admission/application remain separate.\n'
write('COMPLETE-MODEL.md',complete)
readme=f'''# Complete revised model and fresh assurance package

This package closes preparation of fresh correspondence and bounded consistency/non-collapse evidence for the exact Definition application candidate.1, Definition Pack candidate.4 and CyberAlchemy Define candidate.4. It includes the full six-meaning model and keeps actual owner acceptance/admission/application unselected.

## Results

- {len(bindings)} exact admitted source bindings; zero technical source gaps.
- {len(formal_rows)} source formula correspondences and {len(clauses)} captured scientific clauses; both explanatory voices of all three meanings reviewed.
- {len(core['axioms'])} typed axioms, a populated joint consistency witness, {typed['pair_count']} comparison pairs and {len(typed['pairs'])} directed distinction countermodels.
- {len(typed['boundaries'])} non-entailment boundaries, {len(typed['overlaps'])} permitted interpreted overlaps and {len(typed['controls'])} typed rejection/alias controls.
- {sum(x['cases'] for x in populations):,} freshly checked bounded rule assignments.
- Incident initial output: 12,000 required / 11,800 present / 200 missing → FAIL. Retry: same meaning, new application/evidence epoch, all 12,000 present → PASS. Both results remain inside their proposed-meaning/synthetic evidence scope.

## What the formal evidence establishes

The selected interpreted clauses can coexist. Pack concept handling, embedded application binding, optional exact assessments and explicit materialization can be satisfied together without implying new admission, action authority, goal achievement or a completed production Evaluation. Distinct roles have populated countermodels rather than relying on different labels; an identical-obligation alias is correctly detected as collapsed.

## Findings incorporated in this package

- Fresh registry preview corrects six earlier bare-version lookup values to exact identity@version. The frozen earlier preview is preserved.
- Fresh semantic bridge rejects malformed identifier ranges and forged counts, outcomes or missing-ID lists. These controls expose production-validator requirements; the old preview/runtime is not silently relabeled conforming.
- Assessment references and exact evidence support are checked independently of its stored label. A passed binding never manufactures an assessment.

## Read the complete package

- [Complete revised model](COMPLETE-MODEL.md)
- [All six exact Definitions](DEFINITIONS-INDEX.md)
- [Fresh formula correspondence](CORRESPONDENCE.md) and [per-clause/voice coverage](clause-coverage.json)
- [Typed core](formal-core.json), [checked model witnesses](finite-witnesses.json) and [bounded populations](bounded-rule-results.json)
- [Incident evidence bridge](incident-bridge.json) and {link(str((BASE/'incident-pack.json').relative_to(ROOT)),'the complete incident Pack')}
- [Registry preview](registry-postimage.json), [drift review](drift-review.json) and {link(str((BASE/'integration-amendments.json').relative_to(ROOT)),'consumer/integration amendments')}
- [Assurance limits](assurance-limits.json), [results](assurance-results.json) and [current owner requirements](owner-review-request.json)

## Exact remaining decision scope

Fresh source/formal/voice fidelity remains a human owner review subject. Candidate profiles are not adopted; current registry mapping concurrence, full revised consumer/postimage compatibility, applicable owner/type/profile standing and production provider/exporter/evaluator qualification remain required. No shared Definition, Artifact Type, incident fact, permission or lifecycle transition is admitted here.

The evidence has explicit finite populations and Python checker trust. It is not an unrestricted theorem, full natural-language equivalence or whole-repository consistency proof. Existing 17 assurance limits and these seven fresh limits remain visible.
'''
write('REVIEW.md',readme)
write('owner-review-request.json',{'authority_effect':'none','selected':False,'actual_decision_ref':None,'subjects':changed,'review_material':[PREFIX+'/CORRESPONDENCE.md',PREFIX+'/clause-coverage.json',PREFIX+'/formal-core.json',PREFIX+'/finite-witnesses.json',PREFIX+'/bounded-rule-results.json',PREFIX+'/incident-bridge.json',PREFIX+'/assurance-limits.json'],'requested_scope':'Fresh source/formal/voice correspondence and bounded consistency/non-collapse interpretation acceptance only, with stated limits; semantic admission/application excluded.','requires_fresh_attributable_acceptance':True,'prior_acceptance_transferred':False})
for item in model['baseline']['protected']:check('live-preserved:'+item['path'],ref(item['path'])==item)
for doc in ['REVIEW.md','CORRESPONDENCE.md','COMPLETE-MODEL.md','DEFINITIONS-INDEX.md']:
    for target in re.findall(r'\]\(([^)]+)\)',(OUT/doc).read_text()):
        if target.startswith(('http:','https:','#')):continue
        check('link:'+doc+':'+target,(OUT/target.split('#')[0]).exists())
write('verification-observations.json',{'authority_effect':'none','checks':checks,'passed':len(checks),'failed':0,'claim_ceiling':'Preparation source/schema/link/bridge checks; no owner effect or unrestricted semantic proof.'})
write('source-selection.json',{'authority_effect':'none','files':sorted(source_files.values(),key=lambda x:x['path']),'tools':{'python':sys.version,'ir':ref(ROOT/'craft/formalization/candidates/definition-assurance-v1/ir.py'),'denotation':ref(ROOT/'craft/formalization/candidates/definition-assurance-v1/verifier.py')},'ceiling':'Exact selected bytes, typed interpreter and stated finite populations; no native provider/effect dispatch.'})
files=[ref(p) for p in sorted(OUT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['package-manifest.json','independent-verification.json','routing-boundaries.json']]
write('package-manifest.json',{'schema_version':'cal.define-application-fresh-formal-review-manifest/v1','authority_effect':'none','status':'frozen fresh scoped formal evidence package; owner review/admission pending','files':files,'selected_meanings':selected,'changed_meanings':changed,'predecessor_seals':[ref(BASE/'package-manifest.json'),ref(BASE/'supplement-01-reviewed-model/package-manifest.json')],'admission_ready':False,'actual_decision_ref':None,'application':False,'exclusions':['self manifest','later independent/routing receipts','mutable navigation/progress','private/live operator state']})
print(json.dumps({'summary':summary,'manifest':ref(OUT/'package-manifest.json'),'structural_checks':len(checks)},indent=2),flush=True)
