#!/usr/bin/env python3
"""Reproduce local admission review material only. Never write authority or runtime state."""
import copy, hashlib, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
BASE = Path('define/development/m1-preparation-preview/v1')
OUT = BASE/'reviews/admission-package/v1'
FRESH = BASE/'reviews/consolidated-model/v2/formal-assurance/v1'
INPUTS = {}

def digest(p):
    raw=(ROOT/p).read_bytes()
    return {'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def bind(p):
    item=digest(p); INPUTS[str(p)]=item; return item
def read(p):
    bind(p); return json.loads((ROOT/p).read_text())
def put(p,obj):
    path=ROOT/OUT/p; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n' if not isinstance(obj,str) else obj.rstrip()+'\n')
    return digest(OUT/p)
def module(p,name):
    bind(p); spec=importlib.util.spec_from_file_location(name,ROOT/p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def shape(x):
    # Local closed representation check, not a general admitted metamodel schema.
    if isinstance(x,dict): return {'type':'object','additionalProperties':False,'required':list(x),'properties':{k:shape(v) for k,v in x.items()}}
    if isinstance(x,list):
        variants=[]
        for v in x:
            s=shape(v)
            if s not in variants: variants.append(s)
        return {'type':'array','items':({'anyOf':variants} if variants else False)}
    if x is None:return {'type':'null'}
    if isinstance(x,bool):return {'type':'boolean'}
    if isinstance(x,int):return {'type':'integer'}
    return {'type':'string','minLength':1}

def main():
    assert ROOT.name=='CyberAlchemy-lab', ROOT
    if (ROOT/OUT/'package-manifest.json').exists():
        raise SystemExit('This package is sealed. Prepare a new revision rather than overwriting reviewed evidence.')
    fresh=read(FRESH/'complete-package-manifest.json')
    assert digest(FRESH/'complete-package-manifest.json')['sha256']=='19bbecca1fffd7e8508b34903475ebbe985922e038781e8745388de42201ab6f'
    subjects=fresh['selected_meanings']
    for s in subjects:
        assert bind(s['path'])=={k:s[k] for k in ('path','sha256','bytes')}
        for k in ('human_projection','schema','generator'):assert bind(s[k]['path'])==s[k]
    # Bind all resolvable repository-root references in earlier immutable manifests.
    def collect(x):
        if isinstance(x,dict):
            if isinstance(x.get('path'),str) and isinstance(x.get('sha256'),str) and (ROOT/x['path']).is_file():
                assert bind(x['path'])['sha256']==x['sha256'],x['path']
            for y in x.values():collect(y)
        elif isinstance(x,list):
            for y in x:collect(y)
    for p in (FRESH/'package-manifest.json',FRESH/'complete-package-manifest.json',BASE/'reviews/consolidated-model/v2/package-manifest.json',BASE/'steps/09-assurance-evidence-closure/package-manifest.json'):
        collect(read(p))
    acceptance={
      'schema_version':'cal.define-conversational-review-record/v1','record_id':'DEFINE-APPLICATION-FRESH-FIDELITY-ACCEPTANCE-2026-10-14',
      'authority_effect':'none','requested_owner_route':'role:definition-owner','selected_outcome':'accept-with-exact-scope',
      'frozen_review_package':bind(FRESH/'complete-package-manifest.json'),'subjects':subjects[:3],
      'user_evidence':{'speaker':'human user','exact_text':'accepted within those limits, now close the remaining profile standing, consumer compatibility and registry requirements, and show me the complete admission package before we admit anything','message_id':None,'identity_ceiling':'Direct human conversation attribution only; no signed Decision, authenticated credential, scope extension or application receipt.'},
      'accepted_scope':['Fresh source/formula/voice correspondence for the three exact changed meanings','Typed finite non-collapse and consistency evidence, bounded rule checks and incident bridge within the frozen limits'],
      'limits':bind(FRESH/'assurance-limits.json'),
      'not_established':['New registry representation concurrence','Artifact Type owner scope extension','Profile adoption or effective standing','Definition admission','Current lookup or Project State change','Runtime implementation or activation'],
      'frozen_package_preserved':True}
    put('fresh-fidelity-acceptance.json',acceptance)
    prior_acceptances=[bind(BASE/f'reviews/e04-final-review/v1/E04-FIDELITY-{i:02d}-accepted-2026-10-14.json') for i in (3,4,5)]
    put('assurance-disposition.json',{'authority_effect':'none','fresh_acceptance':bind(OUT/'fresh-fidelity-acceptance.json'),'preserved_exact_fidelity_acceptances':prior_acceptances,'FA01':'Fresh three-meaning correspondence accepted within the interpreted finite evidence limits; no unbounded equivalence claim.','FA02_to_FA06':'Limits retained; production parameter/assessment/epoch enforcement and authenticated authority are not proved by this preparation.','FA07':'Registry/consumer/standing preparation is assembled in this package; effective owner/type/profile standing and operational visibility remain conditional.','previous_17_limits':bind(BASE/'reviews/e04-final-review/v1/assurance-limits.json'),'fresh_7_limits':bind(FRESH/'assurance-limits.json'),'new_owner_effects':0})
    live=read('authority/definitions/registry.json')
    old_foundation=read('authority/definitions/candidates/0001-definition-and-ctx00-v1/definitions/definition/v1/definition.json')
    new_foundation=read(BASE/'steps/03-foundational-definition/definition.json')
    assert old_foundation['scope']==new_foundation['scope']
    for key in ('normative_statement','formal_expression'):
        assert old_foundation['voices']['scientific_formal'][key]==new_foundation['voices']['scientific_formal'][key]
    catalog_path='authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
    catalog=read(catalog_path)
    old_drift=read('authority/definitions/drift-audit.json')
    owners=read('authority/owners/foundation-01/v1/owners.json')
    bind('docs/decisions/0013-foundation-01-admission/decision.json')
    bind('docs/decisions/0070-definition-complete-lab-model-admission/authorization.json')
    bind('authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json')
    baseline={ 'schema_version':'cal.define-admission-baseline/v1','authority_effect':'none',
      'definition_registry':bind('authority/definitions/registry.json'),'definition_index':bind('authority/definitions/DEFINITIONS-INDEX.md'),
      'historical_drift':bind('authority/definitions/drift-audit.json'),'artifact_type_registry':bind(catalog_path),
      'current_project_state_pointer':bind('authority/project-state-transitions/current.json'),
      'current_runtime_bundle':bind('authority/admissions/lab-operational-runtime/v1/bundle.json'),
      'definition_versions':len(live['entries']),'current_identities':len(live['current_lookup']),
      'admitted_contracts':len(catalog['admitted_contracts']),'historical_drift_findings':len(old_drift['findings'])}
    put('baseline.json',baseline)
    # No registry row is rewritten and no pending meaning is labelled admitted.
    mixed=read(FRESH/'registry-postimage.json')
    mixed['schema_version']='cal.define-mixed-registry-review/v1'
    mixed.pop('fresh_assurance_package',None)
    mixed['representation_status']='Local derived mixed-carrier review projection; not an instance of original Definition Registry/v1 authoring schema.'
    mixed['carrier_bindings']={}
    for row in mixed['entries']:
        source=read(row['path']); exact=row['definition_id']+'@'+row['version']
        mixed['carrier_bindings'][exact]=source['classification']['artifact_type_ref']
    mixed['source_direction']={'canonical_sources':'Exact preserved Definition files, live registry history and this selected-cohort manifest; future effective Decisions remain required.','projection_policy':'generated-only','generator':bind(OUT/'prepare.py')}
    mixed['publication_rule']='Do not replace the live v1 registry with this local format. Owner-qualified derived representation and a qualified successor provider are required for coherent visibility.'
    put('registry/mixed-review.json',mixed)
    put('registry/mixed-review.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Closed local review projection, no admitted registry carrier claim',**shape(mixed)})
    rows=['# Prospective Definition index','','Generated from mixed-review.json. All six additions remain candidates. Current live lookup is unchanged.','','| Definition | Carrier | Captured state | Source |','| --- | --- | --- | --- |']
    for e in sorted(mixed['entries'],key=lambda r:(r['definition_id'],r['version'])):
        exact=e['definition_id']+'@'+e['version']; rows.append(f"| `{exact}` | `{mixed['carrier_bindings'][exact]}` | {e['lifecycle_state']} | `{e['path']}` |")
    put('registry/DEFINITIONS-INDEX.md','\n'.join(rows))
    strict_path=BASE/'steps/10-profile-meanings-v1-owner-package/supplement-01-authored-postimage/authored-postimage/registry.json'
    strict=read(strict_path); put('registry/v1-bootstrap-authored.json',strict)
    render=module(Path('authority/foundation/v1/render.py'),'foundation_render')
    put('registry/V1-BOOTSTRAP-INDEX.md',render.registry(strict))
    mapping_path=BASE/'steps/10-profile-meanings-v1-owner-package/supplement-01-authored-postimage/registry-representation-mapping.json'
    mapping=read(mapping_path)
    put('registry/representation-disposition.json',{
      'schema_version':'cal.define-registry-representation-disposition/v1','authority_effect':'none',
      'v1_authoring_view':bind(OUT/'registry/v1-bootstrap-authored.json'),'original_schema':bind('authority/foundation/v1/schema.json'),
      'strict_view_role':'Two v1 meanings only: 189 inherited rows plus 2 conditional intended admitted rows. These future labels are not actual standing.',
      'exact_prior_mapping':bind(mapping_path),'preservation_rule':'V1 authored fields plus exact historical metadata and captured baseline; never treat the lossy authored fields alone as the complete admitted-output registry.',
      'mixed_view':bind(OUT/'registry/mixed-review.json'),'mixed_view_role':'195 exact versions, 188 intended current identities, per-entry v1/v2 carrier; new six entries remain candidate-authored and actual Decision refs null.',
      'representation_owner_concurrence_selected':False,
      'qualified_publication_recipe':['Select independent mechanics, Definition-registry and evidence mapping determinations.','Do not loosen or rewrite the original v1 authoring schema.','Adopt the mixed derived-view mechanics only by exact owner determination; this does not create an admitted Registry/v2 contract.','Preserve every legacy row and exact source/history byte.','Qualify successor provider against the mixed representation and immutable epoch before any canonical mirror/current pointer publication.'],
      'registry_type_changes':0,'actual_current_lookup_changed':False})
    # Correct descriptors as separate revisions; preserve every frozen predecessor.
    root=read('authority/artifact-types/artifact-type/v3/artifact.json')
    root_binding={'path':'authority/artifact-types/artifact-type/v3/artifact.json','sha256':bind('authority/artifact-types/artifact-type/v3/artifact.json')['sha256'],'admission_decision_ref':'CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION'}
    gen=module(Path('tooling/generators/artifact_type_successor.py'),'type_projection')
    profile_gen=module(BASE/'steps/04-definition-v2-profiles/generator.py','profile_projection')
    descriptor_items=[]; schema_options=[]; fixtures=[]
    spec=[('evaluation-profile','definition-evaluation-profile','evaluation','evaluationProfile'),('lifecycle-profile','definition-lifecycle-profile','lifecycle','lifecycleProfile'),('definition-binding','definition','definition','definition')]
    for slug,meaning,kind,selector in spec:
        oldpath=(BASE/'steps/05-carrier-foundational-compatibility/carriers/definition-binding-successor/artifact.json' if slug=='definition-binding' else BASE/f'steps/07-profile-formal-source-evidence/staged-carriers/{meaning}/artifact.json')
        d=read(oldpath); instance_kind=d['classification']['semantic_kind']
        d['classification']['artifact_type_ref']='cal.artifact-type.artifact-type/v3';d['artifact_type_root_binding']=root_binding
        d['classification']['semantic_kind']='artifact-type'
        d['classification']['authority_kind']='none'
        d['classification']['lifecycle_posture_ref']='candidate:define-complete-admission-review/v1'
        d['version']='2.0.0-candidate.3' if slug=='definition-binding' else '2.0.0-candidate.2'
        d['four_facets']['classification']='Proposed descriptor mechanics under current admitted Artifact Type/v3; exact scope and mechanical compatibility determinations remain unselected.'
        d['registration_policy']=root['registration_policy']
        d['self_application']={'mode':'no-self-admission','bound':'This descriptor is not the Artifact Type metamodel self-instance. Local shape checking is separate from the v3 self-only schema.','non_effect':'No self-validation, registration, schema check or projection grants standing.'}
        schema_path=('authority/artifact-types/definition/v2/schema.json' if slug=='definition-binding' else str(BASE/'steps/04-definition-v2-profiles/profile-carriers.schema.json'))
        schema_sel=None if slug=='definition-binding' else '#/$defs/'+selector
        d['registered_types']=[{'artifact_type_ref':d['artifact_type_ref'],'semantic_kind':instance_kind,'schema_path':schema_path,'schema_selector':schema_sel,'schema_sha256':bind(schema_path)['sha256'],'semantic_definition_refs':d['semantic_definition_refs'],'distinct_validation_purpose':d['distinct_validation_purpose']}]
        if slug=='definition-binding':
            d['semantic_owner_ref']='role:artifact-type-owner'
            d['validation_contract'].pop('positive_projection',None)
            d['validation_contract']['positive_witness']=next(s['path'] for s in subjects if s['model_role']=='Definition')
        d['validation_contract']['validator_path']=str(OUT/'verify.py')
        d['validation_contract']['assessment_scope']='local-descriptor-structure-exact-root-bindings-instance-schema-projection-and-hostile-controls'
        d['validation_contract']['required_checks']=['Local closed descriptor shape; not general v3 self-schema conformance','Exact current admitted root and preserved predecessor','Exact candidate semantic binding without forged standing','Closed instance schema and deterministic projection','Real negative witnesses','Pending scoped owner qualification and adoption remain blockers']
        local=Path('carriers')/slug
        neg=[]
        for label,mutate in [('wrong-root',lambda a:a['classification'].update(artifact_type_ref='cal.artifact-type.artifact-type/v2')),('forged-standing',lambda a:a['semantic_definition_bindings'][0].update(admission_posture='admitted')),('extra-field',lambda a:a.update(implicit_admission=True))]:
            neg.append(str(OUT/local/'invalid'/f'{label}.json'))
        d['validation_contract']['negative_witnesses']=neg
        d['claim_ceiling']='Exact candidate descriptor revision only. Local review schema does not claim general conformance to the admitted v3 self-only schema. Scoped mechanics/type/binding adoption and current admitted semantic premises are required before effective registration; no activation.'
        put(local/'artifact.json',d);put(local/'ARTIFACT.md',gen.render_artifact(d))
        schema_options.append(shape(d))
        descriptor_items.append({'slug':slug,'subject':bind(OUT/local/'artifact.json'),'previous_candidate':bind(oldpath),'artifact_type_ref':d['artifact_type_ref'],'schema_path':schema_path,'schema_selector':schema_sel})
        for label,mutate in [('wrong-root',lambda a:a['classification'].update(artifact_type_ref='cal.artifact-type.artifact-type/v2')),('forged-standing',lambda a:a['semantic_definition_bindings'][0].update(admission_posture='admitted')),('extra-field',lambda a:a.update(implicit_admission=True))]:
            bad=copy.deepcopy(d);mutate(bad);put(local/'invalid'/f'{label}.json',bad)
            fixtures.append({'kind':'descriptor','positive':str(OUT/local/'artifact.json'),'path':str(OUT/local/'invalid'/f'{label}.json'),'expected':'reject','cause':label})
        if slug!='definition-binding':
            p=BASE/f'steps/04-definition-v2-profiles/{kind}.json';data=read(p)
            put(Path('profiles')/f'{kind}.json',data);put(Path('profiles')/(kind.upper()+'.md'),profile_gen.render(data))
            for label,mutate in [('authority',lambda x:x.update(authority_effect='admitted')),('extra-field',lambda x:x.update(implicit_admission=True)),('wrong-subject',lambda x:x.update(subject_artifact_type_ref='cal.artifact-type.definition/v1'))]:
                bad=copy.deepcopy(data);mutate(bad);fn=Path('profiles/invalid')/f'{kind}-{label}.json';put(fn,bad)
                fixtures.append({'kind':'profile','positive':str(OUT/'profiles'/f'{kind}.json'),'path':str(OUT/fn),'schema_selector':schema_sel,'expected':'reject','cause':label})
    put('carriers/local-descriptor-review.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Local closed descriptor review mechanics; pending mechanics concurrence; not the Artifact Type/v3 self-schema','anyOf':schema_options})
    put('carriers/subjects.json',{'authority_effect':'none','descriptors':descriptor_items,'instance_schema_changes':0,'new_global_relation_kinds':0,'new_definition_application_artifact_types':0})
    for label in ('bare-lookup-version','duplicate-entry','wrong-carrier','forged-source-digest'):
        bad=copy.deepcopy(mixed)
        if label=='bare-lookup-version':bad['proposed_current_lookup']['cal.definition.definition-application']='1.0.0-candidate.1'
        elif label=='duplicate-entry':bad['entries'].append(copy.deepcopy(bad['entries'][-1]))
        elif label=='wrong-carrier':bad['carrier_bindings'][subjects[0]['definition_ref']]='cal.artifact-type.definition/v1'
        else:bad['entries'][-1]['sha256']='0'*64
        fn=Path('registry/invalid')/(label+'.json');put(fn,bad)
        fixtures.append({'kind':'registry','positive':str(OUT/'registry/mixed-review.json'),'path':str(OUT/fn),'expected':'reject','cause':label})
    bad=copy.deepcopy(strict);bad['definition_artifact_type_ref']='cal.artifact-type.definition/v2'
    put('registry/invalid/v2-under-v1-declaration.json',bad)
    fixtures.append({'kind':'v1-registry','positive':str(OUT/'registry/v1-bootstrap-authored.json'),'path':str(OUT/'registry/invalid/v2-under-v1-declaration.json'),'expected':'reject','cause':'v2-under-v1-declaration'})
    put('fixtures.json',{'authority_effect':'none','negative_cases':fixtures})
    bind('authority/artifact-types/artifact-type/v3/schema.json')
    put('carriers/mechanics-correspondence.json',{'authority_effect':'none','current_root':root_binding,'local_schema':bind(OUT/'carriers/local-descriptor-review.schema.json'),
      'original_self_schema':bind('authority/artifact-types/artifact-type/v3/schema.json'),
      'distinction':'The admitted v3 schema hardcodes the metamodel self-instance. These three descriptors are not that instance. A local closed shape and exact binding checker is proposed for their mechanical review; it grants no new generic admitted descriptor schema.',
      'obligations':[{'requirement':x,'status':'represented; executable check in verify.py'} for x in root['instance_contract']['required_semantic_fields']],
      'owner_determination_required':'Approve exact descriptor mechanics against v3 registration_policy and explicit closed local schema. No compatibility is inferred merely from a v3 root field.',
      'meaning_changes':0,'old_candidate_descriptors_preserved':True})
    proposed=[]
    for item in descriptor_items[:2]:
        d=read(item['subject']['path']);proposed.append({'artifact_type_ref':d['artifact_type_ref'],'artifact_path':item['subject']['path'],'artifact_sha256':item['subject']['sha256'],'schema_path':item['schema_path'],'schema_selector':item['schema_selector'],'schema_sha256':d['schema_digest'],'semantic_definition_refs':d['semantic_definition_refs'],'semantic_kind':d['registered_types'][0]['semantic_kind'],'lifecycle_state':'candidate-unadmitted','admission_decision_ref':None})
    type_lookup=copy.deepcopy(catalog['current_by_identity'])
    for entry in proposed:type_lookup[entry['artifact_type_ref'].rsplit('/',1)[0]]=entry['artifact_type_ref']
    put('registry/artifact-type-registration.json',{'schema_version':'cal.define-type-registration-review/v1','authority_effect':'none','baseline':bind(catalog_path),'preserved_admitted_contracts':catalog['admitted_contracts'],'preserved_descriptors':catalog['descriptors'],'proposed_contracts':proposed,'proposed_current_by_identity':type_lookup,'current_selection_changes':[{'identity':k,'from':catalog['current_by_identity'].get(k),'to':v} for k,v in type_lookup.items() if catalog['current_by_identity'].get(k)!=v],'predecessor_disposition':'Preserve both v1 contracts and all descriptor bytes; after actual qualified successor application an effective overlay records their historical route, rather than rewriting frozen predecessor records.','admitted_contracts_after_full_qualified_application':145,'actual_new_admitted_contracts':0,'duplicate_type_refs_created':0,'binding_revision_is_not_a_second_contract':True})
    def_entry=next(x for x in catalog['admitted_contracts'] if x['artifact_type_ref']=='cal.artifact-type.definition/v2')
    put('registry/definition-binding-overlay.json',{'schema_version':'cal.define-binding-revision-review/v1','authority_effect':'none','stable_artifact_type_ref':'cal.artifact-type.definition/v2','preserved_current_contract':def_entry,'proposed_descriptor_revision':descriptor_items[2]['subject'],'requested_semantic_binding':next(s for s in subjects if s['model_role']=='Definition'),'unchanged_contract_fields':['schema_digest','schema_ref','instance_contract','allowed_relation_kinds','relation_roles'],'effective_decision_ref':None,'consumer_support':'Old provider resolves the old catalog entry. A qualified successor resolver must explicitly select the new descriptor by digest and Decision while retaining old lineage; this sidecar is not existing provider support.','new_type_ref':False})
    old_impacts=read(BASE/'steps/09-assurance-evidence-closure/consumer-impact-evidence.json')
    operations=[]
    operational_paths=['implementation/lab-runtime/v2/lab_runtime/sources.py','implementation/define-cli/v1/src/context-adapter.mjs','implementation/define-cli/v1/src/lab-cli.mjs','implementation/lab-review/candidates/v1/review.py','docs/lab/how-to/prepare-definition.md','define/INTEGRATION.md','implementation/define-cli/v1/CONTRACT.md']
    for p in operational_paths:operations.append({'subject':bind(p),'disposition':'preserve exact current implementation/document; no automatic rebind or activation','runtime_qualification':'not claimed'})
    canonical_scan=[]
    for e in live['entries']:
        doc=read(e['path']); raw=json.dumps(doc)
        mentions=[s['definition_ref'].split('@')[0] for s in subjects if s['definition_ref'].split('@')[0]+'@' in raw]
        if mentions:canonical_scan.append({'subject':bind(e['path']),'exact_ref':e['definition_id']+'@'+e['version'],'mentioned_identities':mentions,'reference_classification':'Reference/mention inventory; source-versus-evidence classification retained separately in exact prior 37-row inventory.','disposition':'preserve exact source/evidence/meaning; no dynamic current-lookup substitution'})
    put('consumers/compatibility.json',{'schema_version':'cal.define-consumer-compatibility-review/v1','authority_effect':'none','prior_exact_classified_inventory':bind(BASE/'steps/09-assurance-evidence-closure/consumer-impact-evidence.json'),'prior_classification':old_impacts['reference_classification_counts'],'prior_actual_consumers':36,'canonical_versions_scanned':189,'fresh_reference_inventory':canonical_scan,'selected_operational_consumers':operations,'preserved_canonical_sources':[bind(e['path']) for e in live['entries']],
      'new_meaning_consumers':[{'meaning':s['definition_ref'],'subject':bind(s['path']),'disposition':'Use exact candidate cohort for preparation only; source standing remains pending required dependency effects.'} for s in subjects],
      'runtime_visibility_obligation':{'status':'outside semantic-only effect; blocks coherent publication and operational use','source_provider':bind(operational_paths[0]),'mechanism':'capture() binds authority/definitions/registry.json to the D74 immutable registry digest. A new canonical mirror fails that equality; admission/decision inventory also changes freshness.','resolution':'Preserve current provider and mirrors. Before publication, implement and qualify a successor that resolves an exact immutable epoch and explicit per-entry carriers/binding revision; refresh context/ontology/review using that epoch. No silent fallback or private-store rebase.'},
      'legacy_cli_obligation':{'status':'deferred operational implementation, not semantic contradiction','disposition':'Legacy cav2.definition-pack-candidate/v1 output remains supported exactly as before; embedded applications/assessments are preparation specimens until a separately qualified exporter/adapter implements them.'},
      'owner_dispositions_selected':False,'compatibility_claim':'Exact preservation of named consumers and sources only; no claim that the new cohort is usable through the current runtime.','external_private_consumers':'not inventoried; excluded from activation scope, must be checked before any later activation'})
    # Owner requests, never selected effects. One cohesive review with independently owned outcomes.
    nodes=[
      ('OWNER-SCOPE','role:repository-owner',[], 'Qualify artifact-type-owner for only the two new v2 profile carriers and the exact Definition/v2 binding revision under the current v3 root; preserve every unrelated assignment.'),
      ('REGISTRY-MAPPING','role:artifact-mechanics-owner',[], 'Concur on exact strict-v1 authored view plus preserved admitted metadata, generated views, and mixed derived representation mechanics. Separate Definition and evidence concurrence remains required.'),
      ('REGISTRY-MAPPING-SEMANTIC','role:definition-owner',['REGISTRY-MAPPING'],'Concur on exact identity/current lookup/history mapping and consumer preservation; no admission selected by this concurrence.'),
      ('REGISTRY-MAPPING-EVIDENCE','role:evidence-conformance-owner',['REGISTRY-MAPPING'],'Concur on evidence/mapping coverage and honest conditional labels; no semantic admission.'),
      ('PROFILE-MEANINGS','role:definition-owner',['REGISTRY-MAPPING-SEMANTIC','REGISTRY-MAPPING-EVIDENCE'],'Select the two v1-carried meanings only when actual v1 checks 01-06 PASS. After exact owner selection re-evaluate 07, then record lifecycle transitions in order under unchanged full-PASS gate. No prefix-PASS relabeling.'),
      ('PROFILE-MECHANICS','role:artifact-mechanics-owner',['OWNER-SCOPE'],'Qualify exact local descriptor review schema, current-v3 mechanics correspondence, unchanged concrete profiles and executable validator/negative cases. General v3 self-schema conformance is not claimed.'),
      ('PROFILE-TYPES','role:artifact-type-owner',['OWNER-SCOPE','PROFILE-MEANINGS','PROFILE-MECHANICS'],'Admit only the two exact descriptor revisions once their semantic bindings are actually admitted; preserve both v1 predecessor contracts.'),
      ('EVALUATION-ADOPTION','role:evidence-conformance-owner',['PROFILE-TYPES'],'Adopt exact evaluation.json/schema/check-contract/generator for Definition/v2; no lifecycle or Definition admission implied.'),
      ('LIFECYCLE-ADOPTION','role:definition-owner',['PROFILE-TYPES'],'Adopt exact lifecycle.json separately; transition vocabulary is not an actual transition.'),
      ('FOUNDATIONAL-SUCCESSOR','role:definition-owner',['EVALUATION-ADOPTION','LIFECYCLE-ADOPTION','REGISTRY-MAPPING-SEMANTIC','REGISTRY-MAPPING-EVIDENCE'],'Admit foundational Definition candidate.3 only after fresh actual prerequisite checks; preserve predecessor exact meaning and sources.'),
      ('DEFINITION-BINDING','role:artifact-type-owner',['OWNER-SCOPE','FOUNDATIONAL-SUCCESSOR','PROFILE-MECHANICS'],'Select one exact descriptor revision of Definition/v2 without duplicating TypeRef or changing schema, discriminator or relation roles. Runtime binding resolver support remains separate.'),
      ('DEFINITION-APPLICATION','role:definition-owner',['EVALUATION-ADOPTION','LIFECYCLE-ADOPTION','FOUNDATIONAL-SUCCESSOR','DEFINITION-BINDING'],'Admit exact reusable Definition application candidate.1; embedded task values do not become independent definitions.'),
      ('PACK-AND-DEFINE','role:definition-owner',['DEFINITION-APPLICATION'],'Admit Pack candidate.4 and Define candidate.4; exact registry/index/drift/cohort inputs and all 01-12 checks required.'),
      ('COHERENT-VISIBILITY','role:repository-owner',['PACK-AND-DEFINE'],'Future separate effect: qualify provider/resolver, stage immutable epoch, verify actual Decisions and postimages, then select one current Project State. Excluded from this semantic review selection.')]
    requests=[]
    targets={
      'OWNER-SCOPE':['baseline.json','carriers/subjects.json'],
      'REGISTRY-MAPPING':['registry/v1-bootstrap-authored.json','registry/representation-disposition.json','registry/mixed-review.json','registry/DEFINITIONS-INDEX.md'],
      'REGISTRY-MAPPING-SEMANTIC':['registry/representation-disposition.json','registry/mixed-review.json','consumers/compatibility.json'],
      'REGISTRY-MAPPING-EVIDENCE':['registry/representation-disposition.json','fixtures.json'],
      'PROFILE-MEANINGS':['registry/v1-bootstrap-authored.json'],
      'PROFILE-MECHANICS':['carriers/local-descriptor-review.schema.json','carriers/mechanics-correspondence.json','carriers/subjects.json','profiles/evaluation.json','profiles/lifecycle.json'],
      'PROFILE-TYPES':['registry/artifact-type-registration.json'],
      'EVALUATION-ADOPTION':['profiles/evaluation.json'], 'LIFECYCLE-ADOPTION':['profiles/lifecycle.json'],
      'FOUNDATIONAL-SUCCESSOR':['registry/mixed-review.json'],'DEFINITION-BINDING':['registry/definition-binding-overlay.json'],
      'DEFINITION-APPLICATION':['fresh-fidelity-acceptance.json'],'PACK-AND-DEFINE':['fresh-fidelity-acceptance.json'],
      'COHERENT-VISIBILITY':['consumers/compatibility.json']}
    for key,owner,deps,effect in nodes:
        requests.append({'request_id':key,'owner_route':owner,'depends_on':deps,'requested_effect':effect,'selected':False,'actual_decision_ref':None,'actual_effect_ref':None,'review_material':[bind(OUT/p) for p in targets[key]],'required_evidence':'Exact frozen package, selected subjects and current dependency Decisions/effects; recapture stale input before decision/application.','included_for_selection':key!='COHERENT-VISIBILITY'})
    selected_roles={'PROFILE-MEANINGS':['EvaluationProfile','LifecycleProfile'],'FOUNDATIONAL-SUCCESSOR':['Definition'],'DEFINITION-APPLICATION':['DefinitionApplication'],'PACK-AND-DEFINE':['Pack','Define']}
    for request in requests:
        request['selected_meaning_subjects']=[s for s in subjects if s['model_role'] in selected_roles.get(request['request_id'],[])]
    put('owner-requests.json',{'schema_version':'cal.define-conditional-admission-owner-requests/v1','authority_effect':'none','requests':requests,'role_scope_basis':bind('authority/owners/foundation-01/v1/owners.json'),'scope_gap':'The existing Artifact Type owner assignment explicitly names v1. Neither the shared principal nor earlier isolated v2/v3 admissions establish this new scope grant. OWNER-SCOPE requires separate trusted repository-owner determination.','identity_ceiling':'Repository-declared person:<vrondelli>; no external authentication invented.','decision_artifact_claim':'Review requests only, not instances of an admitted Decision carrier or completed Decisions.','no_effects_now':True})
    # Standing evidence is actual NOT_EVALUABLE; conditional path is separately named.
    standing={'schema_version':'cal.define-profile-standing-readiness/v1','authority_effect':'none','v1_profiles':{'evaluation':bind('authority/profiles/definition/v1/evaluation.json'),'lifecycle':bind('authority/profiles/definition/v1/lifecycle.json'),'standing_basis':'D13 admitted overlay; embedded candidate status alone is not effective standing.'},
      'v1_bootstrap':{'checks_01_05':'Existing exact preparation evidence retained; actual freshness rechecked by this package','check_06_registry':'NOT_EVALUABLE pending the three scoped mapping concurrences','check_07_decision':'NOT_EVALUABLE pending exact owner selection, and not solely that while check 06 remains open','actual_predecision_eligibility':False,'lifecycle_resolution':'No gate amendment or exception. Conditional owner selection is assessed under the existing admission_rule; then re-evaluate all seven checks to full PASS before recording candidate-authored → validated-candidate → owner-reviewed → admitted in order, with separate attributable review and application. Until then no transition is claimed.'},
      'v2_profiles':{'evaluation':bind(OUT/'profiles/evaluation.json'),'lifecycle':bind(OUT/'profiles/lifecycle.json'),'current_effective_standing':'candidate-unadmitted; adoption unselected','actual_check_11':'NOT_EVALUABLE','profile_types':[x['artifact_type_ref'] for x in proposed],'no_self_bootstrap':True},
      'actual_v2_predecision_evaluation':[{'check_id':c['check_id'],'actual_result':'EXCLUDED_BEFORE_APPLICATION' if i==13 else 'NOT_EVALUABLE','basis':'Application excluded before decision.' if i==13 else ('Exact owner admission remains unselected.' if i==12 else 'Preparatory evidence is available; no adopted applicable v2 profile, unresolved current owner/representation prerequisites, and dependent effects not yet captured. This is not an actual profile-qualified PASS.')} for i,c in enumerate(read(BASE/'steps/04-definition-v2-profiles/evaluation.json')['checks'])],
      'conditional_readiness':'DAG complete as review requests; effective standing/eligibility must be recomputed after each actual prerequisite, never copied from this preview.','actual_admission_ready':False}
    put('standing.json',standing)
    # Original carrier conforming scoped audit, with open conditions explicit.
    drift=read(BASE/'steps/10-profile-meanings-v1-owner-package/mapping-determination-v1/drift-audit.json')
    drift['record_id']='CAL-DEFINE-COMPLETE-ADMISSION-PREPARATION-DRIFT'
    drift['registry_ref']=str(OUT/'registry/v1-bootstrap-authored.json');drift['registry_sha256']=digest(OUT/'registry/v1-bootstrap-authored.json')['sha256']
    drift['findings']=[{'finding_id':key,'severity':'blocker' if key not in ['RUNTIME-VISIBILITY','BINDING-RESOLVER'] else 'warning','target':str(OUT/target),'condition':condition,'remediation':fix,'blocking_for':scope} for key,target,condition,fix,scope in [
      ('MAPPING-CONCURRENCE','registry/representation-disposition.json','Exact mechanics, semantic and evidence concurrence unselected.','Select exact independent mapping requests, then reassess check 06.','v1 bootstrap eligibility'),
      ('OWNER-SCOPE','owner-requests.json','Type-owner v3-scoped assignment is not established by current v1 assignment.','Obtain exact bounded repository-owner scope qualification.','profile type and binding effects'),
      ('DESCRIPTOR-MECHANICS','carriers/mechanics-correspondence.json','Current root is v3; its self-only schema is not a generic descriptor schema. Local mechanical qualification is proposed.','Select exact mechanics concurrence before type admission.','profile type admission'),
      ('PROFILE-STANDING','standing.json','V2 carriers/profiles are candidates and cannot qualify their own adoption.','Apply prerequisite meanings/type/adoption effects; recompute actual checks.','v2 admission eligibility'),
      ('RUNTIME-VISIBILITY','consumers/compatibility.json','Current source provider hardpins older registry; future mixed registry publication is incompatible.','Qualify successor immutable-epoch provider before publication.','coherent visibility and operational use'),
      ('BINDING-RESOLVER','registry/definition-binding-overlay.json','Local revision overlay is not consumed by existing provider.','Qualify explicit revision resolution, preserving one contract per TypeRef.','effective runtime use of revised binding')]]
    drift['claim_ceiling']='Scoped original-schema candidate audit bound to the v1 bootstrap authoring view. Zero measured summary counters are not closure of the explicit standing/owner blockers, nor a global zero-drift claim. The live historical audit and all its findings remain unchanged. Mixed representation findings are review-package observations, not a claim that mixed-review.json is a Registry/v1 instance.'
    put('registry/drift-audit.json',drift);put('registry/DRIFT-AUDIT.md',render.drift(drift))
    put('registry/historical-drift-preservation.json',{'authority_effect':'none','baseline':bind('authority/definitions/drift-audit.json'),'findings':old_drift['findings'],'inherited_findings_count':len(old_drift['findings']),'closed_by_this_review':0})
    put('publication-recipe.json',{'schema_version':'cal.define-admission-publication-recipe/v1','authority_effect':'none','executable_application_implemented':False,'current_pointer_changed':False,'recipe':['Recheck every baseline/source digest and all owner scopes; fail closed on drift.','Select only explicitly requested owner determinations, in dependency order, preserving per-role attribution.','Bootstrap two meanings through existing v1 rules; record actual Decision identities only after selection.','Qualify descriptor mechanics, admit profile types after their meanings, then adopt concrete evaluation/lifecycle profiles independently.','Recompute actual v2 checks for foundational successor, binding revision, Application, Pack and Define; conditional checks are not PASS.','Capture actual owner Decisions and applied prerequisite receipts; no future receipt hash or self-referential manifest placeholder is evidence.','For later visibility only, qualify successor provider/descriptor resolver and stage one immutable epoch with exact typed registry entries, generated index and preserved drift/history.','Validate snapshot context/ontology/review consumers against that one epoch before moving one current pointer; preserve prior epoch for recovery.','Render applied projections from captured actual effects. Do not publish this candidate mixed format or its conditional values directly.'],'unselected_effect_fields':['admission_decision_ref','application_receipt_ref','effective_source_epoch','current_project_state_transition'],'placeholders_are_not_receipts':True,'rollback':'No live changes in preparation. Any later publication requires a qualified recovery procedure and exact prior immutable epoch; no deletion or automatic reversal of an admitted Decision is inferred.'})
    put('subjects.json',{'schema_version':'cal.define-complete-admission-subjects/v1','authority_effect':'none','selected_meanings':subjects,'exact_profile_carriers':descriptor_items,'concrete_profiles':[bind(OUT/'profiles/evaluation.json'),bind(OUT/'profiles/lifecycle.json')],'incident':bind(BASE/'reviews/consolidated-model/v2/incident-pack.json'),'formal_package':bind(FRESH/'complete-package-manifest.json'),'prior_limits':bind(BASE/'reviews/e04-final-review/v1/assurance-limits.json'),'fresh_limits':bind(FRESH/'assurance-limits.json'),'registry_counts':{'before':[189,183],'bootstrap_if_applied':[191,185],'full_if_applied':[195,188]},'semantics_changed_this_preparation':0,'actual_admissions':0})
    # Candidate narrative replacements clarify the future route without editing runtime docs.
    put('consumers/DOCUMENTATION-ADDENDUM.md','''# Definition preparation: proposed integration addendum

The existing CLI prepares its legacy candidate Pack. It does not yet implement the proposed embedded Definition applications or qualified admission exporter.

The revised model reuses one exact meaning and binds task values inside a Pack. An optional assessment also stays in the Pack and records its exact inputs, producer and evidence. A changed value creates a new application; a changed criterion creates a new meaning. Standalone reusable Definitions require an explicit materialization selection.

For INC-1042, the candidate criterion applies to snapshot S-1042, account Northstar, the active-status filter and extraction E-1042. It requires every eligible record identifier in that snapshot/account/filter to occur in the extraction. Of 12,000 required records, 11,800 are present: 200 missing, FAIL. A retry binds a new extraction and application revision: all 12,000 present, PASS. Neither result closes the incident or admits a shared criterion.

Admitting the reusable model does not update a live source provider. Current context/ontology/review snapshots and exact old source bindings remain in force. A successor immutable-epoch provider and explicit binding resolver must be qualified before the new cohort is published for operational use.

This addendum is a proposed narrative update for docs/lab/how-to/prepare-definition.md, define/INTEGRATION.md and implementation/define-cli/v1/CONTRACT.md. It is not a new semantic authority or a claim of implemented support.
''')
    # Inputs are exact provenance; exclude outputs that will be sealed separately.
    put('input-bindings.json',{'authority_effect':'none','bindings':[x for p,x in sorted(INPUTS.items()) if not p.startswith(str(OUT)+'/')],'root_relative_paths':True})
    print(json.dumps({'prepared':str(OUT),'selected_meanings':len(subjects),'input_bindings':len(INPUTS),'new_profile_carrier_proposals':len(proposed),'negative_cases':len(fixtures),'actual_admissions':0}))

if __name__=='__main__':main()
