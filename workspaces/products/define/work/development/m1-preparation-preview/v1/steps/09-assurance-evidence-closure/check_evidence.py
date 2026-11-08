#!/usr/bin/env python3
"""Current source, record, reference and consumer-preservation evidence.

Finite author checks only. Never resolve an absent effect by inventing a receipt.
All evidence outputs are create-only; previous packages remain frozen.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys
import jsonschema

STEP=Path(__file__).resolve().parent
ROOT=STEP.parents[5]
BASE=STEP.parent.parent
OLD=BASE/'steps/08-exact-postimages-review'
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def save(n,d):
    with (STEP/n).open('x') as f:json.dump(d,f,indent=2,ensure_ascii=False);f.write('\n')
def pointer(d,s):
    if s=='whole-json':return d
    assert s.startswith('/') and s!='/', 'unsupported or ambiguous selector'
    for key in s[1:].split('/'):
        key=key.replace('~1','/').replace('~0','~')
        d=d[int(key)] if isinstance(d,list) else d[key]
    assert d is not None
    return d
def module(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    checks=[]
    def check(name,value,detail=None):
        assert value,name
        checks.append({'check':name,'result':'PASS','detail':detail})
    freeze=load(STEP/'source-selection.json')
    for f in freeze['files']:check('frozen input '+f['path'],sha(ROOT/f['path'])==f['sha256'])
    for f in load(OLD/'package-manifest.json')['files']:check('prior immutable package '+f['path'],sha(ROOT/f['path'])==f['sha256'])
    registry=load(ROOT/'authority/definitions/registry.json')
    entries={e['definition_id']+'@'+e['version']:e for e in registry['entries']}
    targets=load(STEP/'targets.json')['targets'];target_checks=[]
    for t in targets:
        p=ROOT/t['path'];check('exact target '+t['definition_ref'],sha(p)==t['sha256'])
        d=load(p);schema=ROOT/t['schema']['path'];jsonschema.Draft202012Validator(load(schema)).validate(d)
        check('closed Definition schema '+t['definition_ref'],True)
        gen=ROOT/t['generator']['path'];renderer=module(gen,'generator_'+t['model_role'])
        first=renderer.render(d);second=renderer.render(d)
        check('two-run deterministic exact projection '+t['definition_ref'],first==second and first.rstrip()==(ROOT/t['human_projection']['path']).read_text().rstrip())
        check('explicit nonnormative explanatory voices '+t['definition_ref'],d['voices']['plain_language']['normative'] is False and d['voices']['domain_context']['normative'] is False)
        target_checks.append({'subject':t['definition_ref'],'schema':'PASS','projection':'PASS','voice_shape':'PASS','fresh_full_voice_fidelity':'FINAL_REVIEW_PENDING'})
    d13p=ROOT/'docs/decisions/0013-foundation-01-admission/decision.json';d13=load(d13p)
    foundation={r['record_id']:r for r in d13['admitted_records']};decisions={}
    for p in (ROOT/'docs/decisions').glob('*/decision.json'):
        d=load(p)
        if 'decision_id' in d:decisions[d['decision_id']]=p
        for member in d.get('decision_refs',[]):decisions[member]=p
    source_bindings=[];decisions_used=set();sources_used=set()
    for t in targets:
        for source in load(ROOT/t['path'])['source_refs']:
            if source['source_ref'] in foundation:
                e=foundation[source['source_ref']];decision=d13['decision_id']
            else:e=entries[source['source_ref']];decision=e['admission_decision_ref']
            p=ROOT/e['path'];dp=decisions[decision]
            check('source standing '+source['source_ref'],source['admission_posture']=='admitted' and source['source_admission_ref']==decision and load(dp)['status']=='owner-admitted')
            check('source digest '+source['source_ref'],sha(p)==source['content_sha256']==e['sha256'])
            value=pointer(load(p),source['selector'])
            row={'subject':t['definition_ref'],'source_ref':source['source_ref'],'selector':source['selector'],
                'source':bind(p),'standing_decision':bind(dp),'selected_value_sha256':hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest(),'result':'PASS'}
            # Member authority reference needs the bundle membership, not a
            # made-up status on the stable decision core itself.
            parent=load(dp)
            if decision in parent.get('decision_refs',[]):
                cores=[p for p in dp.parent.glob('decision-cores/*.json') if load(p).get('decision_id')==decision]
                check('source decision bundle member '+decision,len(cores)==1)
                core=load(cores[0]);check('member exact source target digest',any(r['target_ref']==source['source_ref'] and r['sha256']==source['content_sha256'] for r in core['target_digests']))
                row['stable_member_core']=bind(cores[0]);decisions_used.add(cores[0])
            source_bindings.append(row);decisions_used.add(dp);sources_used.add(p)
    check('all 41 selected source bindings',len(source_bindings)==41)
    save('source-closure.json',{'authority_effect':'none','bindings':source_bindings,'technical_reference_gaps':0,'new_source_admissions':0,
        'claim_ceiling':'Exact source bytes/selectors/recorded admitted standing only. Interpretive fidelity, truth and authenticated final effect authority are separate.'})
    owners=foundation['CAL-OWNERS-FOUNDATION-01'];op=ROOT/owners['path'];check('admitted owner registry digest',sha(op)==owners['sha256'])
    assignments=load(op)['role_assignments'];roles={r['role_id']:r for r in assignments}
    for role in ['artifact-mechanics-owner','artifact-type-owner','definition-owner','source-admission-owner','evidence-conformance-owner']:check('admitted separate role assignment '+role,role in roles)
    save('owner-route-evidence.json',{'authority_effect':'none','source':bind(op),'admission':bind(d13p),'assignments':assignments,
        'conversation_records':[bind(p) for p in sorted((BASE/'reviews').glob('*-accepted-*.json'))],
        'scope_limit':'Recorded assignments and direct conversational selections; no credentials, external identity authentication, signed Decision or applied effect is fabricated.'})
    impact=load(OLD/'consumer-compatibility.json');proposed=load(OLD/'registry-postimage.json')
    predecessor=entries[registry['current_lookup']['cal.definition.definition']]
    previous=load(ROOT/predecessor['path']);successor=load(ROOT/targets[2]['path'])
    for key in ['normative_statement','formal_expression']:check('foundational field preserved '+key,previous['voices']['scientific_formal'][key]==successor['voices']['scientific_formal'][key])
    check('foundational scope preserved',previous['scope']==successor['scope'])
    per_consumer=[]
    for c in impact['current_definition_consumers']:
        p=ROOT/c['path'];d=load(p)
        check('current consumer record digest '+c['exact_ref'],sha(p)==c['sha256']==entries[c['exact_ref']]['sha256'])
        source_rows=[r for r in d['source_refs'] if r['source_ref']==predecessor['definition_id']+'@'+predecessor['version']]
        evidence_rows=[r for r in d['evidence_refs'] if r==predecessor['definition_id']+'@'+predecessor['version']]
        self_reference=c['exact_ref']==predecessor['definition_id']+'@'+predecessor['version']
        check('exact historical founding reference '+c['exact_ref'],bool(source_rows or evidence_rows or self_reference))
        for r in source_rows:
            check('consumer premise digest '+c['exact_ref'],r['content_sha256']==predecessor['sha256'])
            pointer(previous,r['selector'])
        check('inherited consumer row preserved '+c['exact_ref'],entries[c['exact_ref']] in proposed['entries'])
        per_consumer.append({**c,'foundational_source_premises':source_rows,'foundational_evidence_refs':evidence_rows,'reference_class':'direct source' if source_rows else 'evidence only' if evidence_rows else 'foundational subject self-reference','material_result':'PASS exact reference/record preservation',
            'basis':'No normative/source/instance bytes are changed; admitted predecessor remains an exact preserved source, even if the proposed current lookup later selects its successor.',
            'limit':'Does not prove unchanged behavior of unselected external programs or compatibility of future rebinding.'})
    check('37 exact current Definition consumers covered',len(per_consumer)==37)
    live_types=load(ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json')
    types=[]
    for t in impact['current_type_consumers']:
        contract=t['exact_contract'];check('exact current type contract '+contract['artifact_type_ref'],contract in live_types['admitted_contracts'])
        check('type schema digest '+contract['artifact_type_ref'],sha(ROOT/contract['schema_path'])==contract['schema_sha256'])
        types.append({**t,'result':'PASS preserved selected contract; explicit future binding/adoption dependencies retained'})
    old_type=load(ROOT/'authority/artifact-types/definition/v2/artifact.json')
    new_type=load(BASE/'steps/05-carrier-foundational-compatibility/carriers/definition-binding-successor/artifact.json')
    preserved_keys=['artifact_type_ref','schema_ref','schema_digest','instance_contract','relation_roles','allowed_relation_kinds']
    for k in preserved_keys:check('Definition descriptor contract preservation '+k,old_type[k]==new_type[k])
    check('successor semantic binding exact',new_type['semantic_definition_refs']==[targets[2]['definition_ref']])
    connections=load(BASE/'steps/03-foundational-definition/compatibility-review.json')['embedded_connection_dispositions']
    check('old record retained with original historical references',sha(ROOT/predecessor['path'])==predecessor['sha256'])
    check('successor does not transfer embedded references',successor['typed_relations']==[] and successor['semantic_owner_ref']==previous['semantic_owner_ref'])
    governed=load(ROOT/'authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/governed-by.json')['payload']
    origin=load(ROOT/'authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds/originates-from.json')['payload']
    check('closed governed-by Definition endpoint',{'source_kind':'definition','target_kind':'constitution'} in governed['allowed_endpoint_pairs'] and {'source_kind':'definition','target_kind':'role'} not in governed['allowed_endpoint_pairs'])
    check('closed origin Definition endpoint',{'source_kind':'definition','target_kind':'source'} in origin['allowed_endpoint_pairs'] and {'source_kind':'definition','target_kind':'source-admission'} not in origin['allowed_endpoint_pairs'])
    check('required origin qualifier preserved',origin['qualifier_contract']['required_axes']==['origin_role'])
    operations=[]
    for c in impact['selected_operational_consumers']:
        p=ROOT/c['path'];check('selected operational/narrative consumer current '+c['path'],sha(p)==c['sha256'])
        text=p.read_text()
        if p.name=='lab-cli.mjs':
            check('existing CLI stale-context guard remains','define.compile-stale-Lab-context' in text and 'current.source_epoch!==epoch' in text)
            observation='Read-only source witness of exact epoch/expiry checks; no executable integration or new M1 conformance asserted.'
        elif p.name=='review.py':
            check('specialized review scope remains','Read-only exact C10 preparation' in text and 'protocol:lab-final-review:C10' in text)
            observation='Specialized existing C10 protocol source retains its explicit fixed scope; this is not the new C10 lifecycle-profile decision.'
        else:
            check('guide retains criterion/source/voice limits',all(s in text for s in ['Definition/v2','S, A, F and E','Plain-language and domain-context voices','source posture and acceptance obligations remain open']))
            observation='Narrative retains exact account/filter/snapshot/output boundaries and distinguishes shape validity from acceptance.'
        operations.append({**c,'result':'PASS captured preservation/narrative source witness','observation':observation,'runtime_claim':'none'})
    extra_documents=[ROOT/'define/INTEGRATION.md',ROOT/'implementation/define-cli/v1/CONTRACT.md']
    docs=[]
    for p in extra_documents:
        text=p.read_text();check('additional Define consumer current source present',len(text)>0)
        docs.append({'source':bind(p),'finding':'CLI is a runnable legacy-output candidate; exact full Lab Definition adaptation and M1 strict exporter are not claimed completed',
            'required_follow_up':'Point readers to the current preparation review and retain the distinction when future M1 runtime documentation is updated.'})
    save('consumer-impact-evidence.json',{'authority_effect':'none','definitions':per_consumer,'type_contracts':types,'operations':operations,'additional_documents':docs,
        'reference_classification_counts':{kind:sum(c['reference_class']==kind for c in per_consumer) for kind in ['direct source','evidence only','foundational subject self-reference']},
        'actual_definition_consumers':36,
        'classification_correction':'The earlier 37-record inventory used a broad reference search. Exact audit finds 34 source users, 2 evidence users and 1 subject self-reference. All 37 records are preserved; prior C02 treatment is preservation, not proof that every match is a normative dependency.',
        'foundational_change':'normative/formal/scope preserved; exact applicable carrier/profile criterion changes explicitly',
        'preserved_descriptor_fields':preserved_keys,'connections':connections,'global_relations_created':0,
        'scope_basis':[bind(BASE/'reviews/C01-accepted-2026-10-13.json'),bind(BASE/'reviews/C02-accepted-2026-10-14.json'),bind(BASE/'reviews/C03-accepted-2026-10-14.json'),bind(BASE/'reviews/C04-accepted-2026-10-14.json')],
        'claim_ceiling':'37 exact impacted records (36 consumers plus predecessor subject), three current type contracts, three selected operational/narrative witnesses and declared extra documents. Unknown/private/external consumers and future full runtime conformance are not proven.'})
    # Every current meaning is accounted for; unmodeled meanings are explicitly
    # excluded from formal proof, not labeled equivalent/distinct by their name.
    corpus=load(STEP/'corpus-selection.json')['current_records'];neighbor_ids={r['definition_id'] for r in load(STEP/'neighbor-correspondence.json')['neighbors']}
    preserved_ids={c['exact_ref'].split('@')[0] for c in per_consumer}
    screens=[]
    for t in targets:
        for e in corpus:
            exact=e['definition_id']+'@'+e['version']
            coverage='MODELED_SELECTED_ROLE_FRAME' if e['definition_id'] in neighbor_ids or e['definition_id']=='cal.definition.definition' else 'PRESERVATION_EVIDENCE_ONLY' if e['definition_id'] in preserved_ids else 'REFERENCE_CAPTURE_ONLY; NOT_FORMALIZED'
            screens.append({'target':t['definition_ref'],'current_source_ref':exact,'path':e['path'],'sha256':e['sha256'],'coverage':coverage,
                'formal_claim':'No whole-source proof from reference capture or this routing label'})
    check('complete 5 by 183 screening accounting',len(screens)==915)
    save('comparison-coverage.json',{'authority_effect':'none','screens':screens,'batches':[{'batch':1,'start':0,'count':512},{'batch':2,'start':512,'count':403}],
        'scope':'All current records accounted for; 42 executed interpreted pairs are listed separately in assurance-results.json',
        'whole_repository_consistency':'NOT_ESTABLISHED','scope_review':'C02 accepts captured consumer-preservation scope and excludes wider compatibility; no fresh universal semantic scope is silently introduced.'})
    profile_root=BASE/'steps/04-definition-v2-profiles';schema=load(profile_root/'profile-carriers.schema.json');gen=module(profile_root/'generator.py','profile_gen')
    for filename,selector,human in [('evaluation.json','evaluationProfile','EVALUATION.md'),('lifecycle.json','lifecycleProfile','LIFECYCLE.md')]:
        p=profile_root/filename;d=load(p);jsonschema.Draft202012Validator({**schema,'$ref':'#/$defs/'+selector}).validate(d)
        check('profile exact schema/projection '+filename,gen.render(d)==gen.render(d) and gen.render(d).rstrip()==(profile_root/human).read_text().rstrip())
    selections=[]
    for item in load(OLD/'remaining-decisions.json')['decisions']:
        paths=list((BASE/'reviews').glob(item['decision_id']+'-accepted-*.json'));check('one scoped conversational selection '+item['decision_id'],len(paths)==1)
        d=load(paths[0]);check('exact accepted selection binding '+item['decision_id'],d['review_item']==item['decision_id'] and d['selected_outcome']=='accept-with-exact-scope' and all(sha(ROOT/t['path'])==t['sha256'] for t in item['subjects']))
        selections.append({'item':item['decision_id'],'record':bind(paths[0]),'selected_outcome':d['selected_outcome'],'scope':d['accepted_scope'],'remaining_conditions':d['remaining_obligations']})
    save('accepted-review-selections.json',{'authority_effect':'none','selected_count':16,'selections':selections,'missing_conversational_selections':0,
        'claim_ceiling':'All explained proposals selected in conversation; no exact actual admission/adoption Decision or confirmation of this fresh evidence cohort is inferred.'})
    # Fresh evidence requires final fidelity review. Candidate profile standing
    # is intentionally not upgraded before user-authorized admission effects.
    preview=[];check_contract=load(profile_root/'check-contracts.json')
    for t in targets:
        is_v2=t['carrier_ref'].endswith('/v2');rows=[]
        if is_v2:
            for c in load(profile_root/'evaluation.json')['checks']:
                cid=c['check_id'];index=int(cid.split('-')[1]);outcome='PASS';detail='Executed exact preparation evidence within declared structural/source/preservation scope'
                if index==9:outcome='NOT_EVALUABLE';detail='Finite evidence executed; fresh interpreted scope/fidelity must be confirmed before asserting complete semantic-assurance fulfillment.'
                if index==10:outcome='NOT_EVALUABLE';detail='Earlier scoped meaning acceptance exists; new formal correspondence and final evidence cohort have not been reviewed by the owner.'
                if index==11:outcome='NOT_EVALUABLE';detail='Applicable v2 profiles/carriers are candidates. Integrity and conditional selections do not establish actual adopted standing.'
                if index==12:outcome='NOT_EVALUABLE';detail='Exact final candidate cohort is prepared/frozen later; qualified final review still depends on 09/10/11.'
                if index==13:outcome='NOT_EVALUABLE';detail='No owner admission selected; pre-decision prerequisite blockers are also explicit, so this is not solely the pending selection case.'
                if index==14:outcome='NOT_EVALUABLE';detail='No authorized application; excluded from pre-decision aggregation.'
                rows.append({'check_id':cid,'outcome':outcome,'reason':detail,'standing':'proposal-preview only'})
        else:
            for c in load(ROOT/'authority/profiles/definition/v1/evaluation.json')['checks']:
                cid=c['check_id'];index=int(cid.split('-')[2]);outcome='PASS';detail='Applicable existing v1 schema/voice/source/owner/projection preparation evidence'
                if index==6:outcome='NOT_EVALUABLE';detail='Exact mixed candidate registry/index/drift are prepared. Final compatible representation/evidence route and fresh cohort review remain required; no silent admitted-schema amendment.'
                if index==7:outcome='NOT_EVALUABLE';detail='No exact human admission Decision; registry/final-evidence obligations are also pending.'
                rows.append({'check_id':cid,'outcome':outcome,'reason':detail,'standing':'existing v1 bootstrap route; no admission'})
        required=check_contract['phases']['pre_decision'] if is_v2 else [r['check_id'] for r in rows[:6]]
        outcomes=[r['outcome'] for r in rows if r['check_id'] in required]
        aggregate='FAIL' if 'FAIL' in outcomes else 'NOT_EVALUABLE' if 'NOT_EVALUABLE' in outcomes else 'PASS'
        preview.append({'subject':t['definition_ref'],'profile':bind(profile_root/'evaluation.json') if is_v2 else bind(ROOT/'authority/profiles/definition/v1/evaluation.json'),
            'checks':rows,'pre_decision_aggregate':aggregate,'eligible_for_admission':False,'reason':'Material preparation cannot supply absent final fidelity/compatible standing or actual owner effect evidence.'})
    save('evaluation-preview.json',{'authority_effect':'none','evaluations':preview,'admission_ready':False,
        'claim_ceiling':'Honest proposal-preview assessment, not an adopted v2 Evaluation or operational enforcement result. Source and structural PASS scopes are limited as recorded.'})
    for f in freeze['files']:check('sources unchanged after audit '+f['path'],sha(ROOT/f['path'])==f['sha256'])
    save('evidence-results.json',{'authority_effect':'none','checks':checks,'source_bindings':41,'impacted_definition_records':37,'current_consumers':36,'type_contracts':3,'selected_operational_consumers':3,
        'corpus_accounting':915,'conversational_selections':16,'new_source_admissions':0,'global_relations_created':0,'admissions':0,
        'technical_reference_gaps':0,'prepared_assurance':'bounded executed evidence','fresh_owner_fidelity':'PENDING','actual_profile_adoption':'ABSENT',
        'admission_ready':False,'checker':bind(Path(__file__).resolve()),'python':sys.version})
    print(json.dumps({'checks_passed':len(checks),'source_bindings':41,'consumers':37,'corpus_accounting':915,'selections':16,'admission_ready':False}))

if __name__=='__main__':main()
