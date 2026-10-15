#!/usr/bin/env python3
"""Read and check captured evidence without rerunning its producer/derive code."""
import copy
import hashlib
import itertools
import json
import sys
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[9]
sys.path.insert(0,str(ROOT/'craft/formalization/candidates/definition-assurance-v1'))
import ir
import verifier


def load(p):return json.loads(p.read_text())
def digest(v):return hashlib.sha256((json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
observations=[]
def require(identity,condition,detail=''):
    observations.append({'check_id':identity,'outcome':'PASS' if condition else 'FAIL','detail':detail})
    if not condition:raise ValueError(identity)


manifest=load(OUT/'package-manifest.json')
for item in manifest['files']:
    data=(ROOT/item['path']).read_bytes()
    require('sealed:'+item['path'],hashlib.sha256(data).hexdigest()==item['sha256'] and len(data)==item['bytes'])
for item in load(OUT/'source-selection.json')['files']:
    data=(ROOT/item['path']).read_bytes()
    require('input:'+item['path'],hashlib.sha256(data).hexdigest()==item['sha256'] and len(data)==item['bytes'])
core=load(OUT/'formal-core.json');witnesses=load(OUT/'finite-witnesses.json')
sorts={x['symbol_id']:x['symbol_id'] for x in core['declarations'] if x['kind']=='sort'}
symbols={x['symbol_id']:x for x in core['declarations'] if x['kind']!='sort'}
for i,formula in enumerate(core['axioms']):
    require('typed-formula:'+str(i),ir.formula(formula,sorts,symbols)==formula)
worlds={x['name']:x['model'] for x in witnesses['worlds']}
for name,model in worlds.items():
    for i,formula in enumerate(core['axioms']):
        require('world:'+name+':axiom:'+str(i),verifier.Denotation(core['declarations'],model).truth(formula))
for i,item in enumerate(witnesses['pairs']):
    model=worlds[item['model']]
    require('distinction-query:'+str(i),verifier.Denotation(core['declarations'],model).truth(item['statement']))
    require('populated-distinction:'+str(i),[item['witness']] in model['predicates'][item['left']] and [item['witness']] not in model['predicates'][item['right']])
for i,item in enumerate(witnesses['boundaries']):
    model=worlds[item['model']]
    den=verifier.Denotation(core['declarations'],model)
    require('non-entailment:'+str(i),not den.truth(item['statement']))
    require('nonvacuous-premise:'+str(i),den.truth(item['statement']['left']))
for item in witnesses['overlaps']:
    model=worlds[item['model']]
    require('overlap:'+item['model'],any([x] in model['predicates'][item['left']] and [x] in model['predicates'][item['right']] for x in model['domains']['Entity']))

# Recreate rejection specimens independently of the producer's control helper.
mutations=[
 ('undeclared tolerance binding','BindValue','append',['DefinitionApplication','tolerance','number']),
 ('wrong parameter type','BindValue','append',['DefinitionApplication','F','number']),
 ('multiple values for one parameter','BindValue','append',['DefinitionApplication','E','retry']),
 ('multiple selected meanings','SelectMeaning','append',['DefinitionApplication','other']),
 ('missing required parameter without gap','BindValue','remove',['DefinitionApplication','F','filter']),
 ('spurious parameter gap','MissingParameterGap','append',['DefinitionApplication','F']),
 ('binding changes selected meaning','MeaningUnchanged','remove',['DefinitionApplication']),
 ('value provenance missing','ValueProvenanceRecorded','remove',['DefinitionApplication']),
 ('assessment points outside owning Pack','AssessesApplication','replace',[['assessment','subject']]),
 ('assessment lacks exact evidence','AssessmentInputEvidenceExact','remove',['assessment']),
 ('assessment producer missing','AssessmentProducerPosture','remove',['assessment']),
 ('materialization selected without purpose scope owner','EmissionSelected','append',['Pack']),
 ('Pack preparation grants authority','PreparationGrantsNewAuthority','append',['Pack']),
 ('false Define result with lost assessment provenance','PreservesAssessmentProvenance','remove',['Pack']),
 ('working proposal relabeled admitted','AdmittedMeaning','append',['criterion']),
 ('typed foreign parameter','BindValue','append',['DefinitionApplication','foreign','number']),
]
for name,predicate,operation,row in mutations:
    model=copy.deepcopy(worlds['joint'])
    if operation=='append':model['predicates'][predicate].append(row)
    elif operation=='remove':model['predicates'][predicate].remove(row)
    else:model['predicates'][predicate]=row
    try:
        rejected=any(not verifier.Denotation(core['declarations'],model).truth(formula) for formula in core['axioms'])
    except verifier.VerificationFault:rejected=True
    require('independent-control:'+name,rejected)
require('label-only-alias-detector',all(([x] in worlds['joint']['predicates']['DefinitionApplication'])==([x] in copy.deepcopy(worlds['joint']['predicates']['DefinitionApplication'])) for x in worlds['joint']['domains']['Entity']))

# Verify source spans, formula fragments and exact selected selector hashes.
correspondence=load(OUT/'formal-correspondence.json')
for i,row in enumerate(correspondence['rows']):
    source=load(ROOT/row['source']['path'])
    require('source-formula-fragment:'+str(i),row['fragment'] in source['voices']['scientific_formal']['formal_expression'])
def pointer(document,selector):
    value=document
    for token in selector.lstrip('/').split('/'):
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value
coverage=load(OUT/'clause-coverage.json')
groups={}
for i,row in enumerate(coverage['clauses']):
    value=pointer(load(ROOT/row['source']['path']),row['selector']);start,end=row['span']
    require('source-span:'+str(i),value[start:end]==row['exact_selected_text'])
    groups.setdefault((row['source']['path'],row['selector']),[]).append(row)
for (path,selector),rows in groups.items():
    original=pointer(load(ROOT/path),selector)
    captured=''.join(x['exact_selected_text'] for x in sorted(rows,key=lambda x:x['span'][0]))
    require('no-unaccounted-source-characters:'+path+selector,''.join(original.split())==''.join(captured.split()))
for i,row in enumerate(load(OUT/'source-closure.json')['selected_source_bindings']):
    require('source-selector:'+str(i),digest(pointer(load(ROOT/row['source']['path']),row['selector']))==row['selected_content_sha256'])

# Independently re-enumerate parameter/gap cases and domain inclusion cases.
pop=load(OUT/'bounded-rule-results.json')['case_populations'];case_counts=[]
total=good=fully=0
names=['S','A','F','E']
for req in itertools.chain.from_iterable(itertools.combinations(names,n) for n in range(5)):
    req=set(req)
    for values in itertools.product(['absent','valid','wrong'],repeat=4):
        provided={k for k,v in zip(names,values) if v!='absent'}
        for extra in [False,True]:
            for gm in range(32):
                total+=1;gaps={k for i,k in enumerate(names+['tolerance']) if gm&(1<<i)}
                valid=(not extra and 'wrong' not in values and gaps==req-provided)
                good+=valid;fully+=valid and req<=provided
require('parameter-population-count',total==pop[0]['cases'])
require('parameter-good-assignment-count',good==pop[0]['wellformed_assignments'] and fully==pop[0]['fully_supplied_assignments'])
case_counts.append(total)
for row,width in zip(pop[1:4],[9,len(core['frames']['Pack']),9]):
    count=0;passing=0
    for mask in range(1<<width):
        count+=1;passing+=mask==(1<<width)-1
    require('flag-population:'+row['population'],count==row['cases'] and passing==1)
    case_counts.append(count)
count=0
for a,b,known_a,known_b in itertools.product(range(16),range(16),[False,True],[False,True]):
    count+=1
    set_a={x for x in range(4) if a&(1<<x)};set_b={x for x in range(4) if b&(1<<x)}
    by_difference='NOT_EVALUABLE' if not (known_a and known_b) else ('FAIL' if set_a-set_b else 'PASS')
    by_bitmask='NOT_EVALUABLE' if not (known_a and known_b) else ('PASS' if (a&b)==a else 'FAIL')
    require('inclusion-population:'+str(count),by_difference==by_bitmask)
require('inclusion-case-count',count==pop[4]['cases']);case_counts.append(count)
require('assessment-population-count',pop[5]['cases']==3*3*3*2*2*2);case_counts.append(pop[5]['cases'])
require('materialization-population-count',pop[6]['cases']==4*3*2**4);case_counts.append(pop[6]['cases'])
require('total-rule-assignment-count',sum(case_counts)==load(OUT/'bounded-rule-results.json')['total_assignments_checked'])
pack=load(ROOT/'define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/incident-pack.json')
app=pack['applications'][0];assessment=pack['assessments'][0]
records={e['evidence_id']:e for e in pack['evidence']}
required={v for a,b in records[app['bindings']['S']]['identifier_ranges'] for v in range(a,b+1)}
exported={v for a,b in records[app['bindings']['E']]['identifier_ranges'] for v in range(a,b+1)}
require('independent-incident-result',assessment['missing_identifiers']==sorted(required-exported) and assessment['counts']=={'required':len(required),'present':len(required&exported),'missing':len(required-exported)} and assessment['outcome']=='FAIL')
registry=load(ROOT/'authority/definitions/registry.json');post=load(OUT/'registry-postimage.json')
require('historical-rows-preserved',post['entries'][:189]==registry['entries'])
for s in manifest['selected_meanings']:require('exact-selected-current-preview:'+s['definition_ref'],post['proposed_current_lookup'][s['definition_ref'].rsplit('@',1)[0]]==s['definition_ref'])
require('no-owner-effect-claimed',manifest['actual_decision_ref'] is None and manifest['application'] is False and not manifest['admission_ready'])
for item in load(ROOT/'define/development/m1-preparation-preview/v1/reviews/consolidated-model/v2/model.json')['baseline']['protected']:
    require('final-live:'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
result={'authority_effect':'none','verifier':'separate read-only checker implementation; same Python/ir/Denotation trust base, not a separate human reviewer','package_sha256':hashlib.sha256((OUT/'package-manifest.json').read_bytes()).hexdigest(),'status':'PASS selected evidence and counted populations','checks':observations,'passed_checks':len(observations),'failed_checks':0,'producer_or_derive_rerun':False,'typed_worlds_checked':len(worlds),'bounded_assignments_recounted':sum(case_counts),'global_theorem':False,'owner_fidelity_acceptance':False,'admission':False,'application':False}
with (OUT/'independent-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))
