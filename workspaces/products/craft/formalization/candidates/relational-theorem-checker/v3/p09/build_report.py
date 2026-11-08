"""Close the suite over actual outputs, fixed obligations and inherited evidence."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,ROOT,binding,check,require
from jsonschema import Draft202012Validator

layout=C.decode((HERE/'layout-suite.json').read_bytes());saved=C.decode((HERE/'saved-controls.json').read_bytes())
hostile=C.decode((HERE/'public-hostile-controls.json').read_bytes());inherited=C.decode((HERE/'inherited-controls.json').read_bytes())
cli=C.decode((HERE/'cli-controls.json').read_bytes());rich=C.decode((HERE/'rich-layout-observation.json').read_bytes())
for r in [layout,saved,hostile,inherited,cli,rich]:require(r['result']=='pass','missing executed pass report')
cases=[];controls=[]
def add(name,entry,kind,input_ref,output_ref,expected,observed,scope):
    check(input_ref);check(output_ref)
    cases.append({'name':name,'entry_point':entry,'evidence_kind':kind,'input':input_ref,'output':output_ref,
        'expected':expected,'observed':observed,'result':'pass','claim_scope':scope,'authority_effect':'none'})
    controls.append({'name':name,'result':'pass','evidence_kind':kind})
for control in layout['controls']:
    name=control['name'];kind='boundary' if any(s in name for s in ['stale','refusal','no-new-live-event']) else 'saved-inspection' if any(s in name for s in ['inspection','trace','absence','boolean']) else 'fresh-kernel'
    add(name,'Client.qualify/inspect/describe/bootstrap/apply',kind,binding(HERE/'layout-request.json'),binding(HERE/'layout-suite.json'),
        'Exact fixed profile/catalog; concrete assertion in bound layout harness','pass',
        'Twelve selected successful fresh Horn invocations, four applications, saved explanations and separately retained real deadline refusal. Harness and individual request/output bindings are retained in the report.')
audits=[]
for case in layout['cases']:
    public=C.decode(check(case['qualification']).read_bytes());q=public['qualification']['qualified_result'];manifest=q['manifest']
    require(manifest['obligations']==[o['id'] for o in C.required_inventory('rule-only')],'catalog shrink')
    build=check({'path':manifest['general']['path'],'sha256':manifest['general']['sha256']}).parent
    proof=next(build.glob('*_evidence.json'));e=C.decode(proof.read_bytes());audit=e['general']['audit']
    require(audit['accepted'] and audit['fresh_kernel_replay'] and audit['allowed_axiom_types_bound'],'incomplete actual replay')
    require(set(audit['transitive_axioms'])<={'propext','Classical.choice','Quot.sound'},'custom axiom')
    audits.append({'layout':case['layout'],'evidence':binding(proof),'required_statement':audit['required_statement'],
        'statement_mode':audit['statement_mode'],'transitive_axioms':sorted(audit['transitive_axioms'])})
    for o in C.required_inventory('rule-only'):
        add(case['layout']+'-obligation-'+o['id'],'OwnedQualifier full exact qualification','fresh-kernel',case['request'],case['qualification'],
            o['method']+': '+o['target'],'Required inventory present and fixed statements verified by the fresh full invocation',
            'Transport/binding/structural/kernel/general methods remain distinct; a saved public envelope cannot reissue this invocation.')
require({a['required_statement'] for a in audits}=={'Successor.Runtime.Catalog.RequiredGeneralBundle'},'theorem bundle changed')
require(audits[0]['statement_mode']==audits[1]['statement_mode'] and audits[0]['transitive_axioms']==audits[1]['transitive_axioms'],'statement/axiom mismatch')
add('fixed-statement-bundle-and-axioms-agree','Fresh exact kernel audits','fresh-kernel',audits[0]['evidence'],audits[1]['evidence'],
    'Same independently required bundle and foundational axiom closure','pass','Same pinned kernel replay in both layouts; not a second independent kernel.')
for c in saved['cases']:
    add(c['name'],'Saved inspector / public explanation / response contract / strict decoder',c['evidence_kind'],c['input'],binding(HERE/'saved-controls.json'),
        'Bound hostile mutation or cause must retain the required refusal/scope',c['observed'],'New finite control; no fresh qualification or application event.')
for c in hostile['cases']:
    for control in [x for x in hostile['controls'] if x['name']==c['name'] or x['name'].startswith(c['name']+'-')]:
        add(control['name'],c['entry_point'],'boundary',c['input'],c['answer'],' / '.join(c['expected'])+' with no publication capability',c['observed'],
            'Actual public supervised refusal; source diagnostic retained. Failed apply leaves the exact head unchanged.')
for c in hostile['controls']:
    if c['name'] not in {x['name'] for x in controls}:
        add(c['name'],'MappedQualifier.qualify','fresh-kernel',binding(HERE/'active-conflict-request.json'),binding(HERE/'active-conflict-result.json'),
            'Actual active pair with both origins; no fulfillment/admission','pass','One newly executed mapped proof; no Horn/application event is inferred from its saved output.')
for c in cli['cases']:
    add(c['name'],c['entry_point'],c['evidence_kind'],c['input'],c['output'],c['expected'],c['observed'],'Actual command integration; saved inspection and malformed refusals issue no application handle.')
add('rich-combined-measured-scope','Client.qualify','fresh-kernel' if rich['observed']=='qualified-candidate' else 'boundary',rich['input'],rich['output'],rich['expected'],rich['observed'],rich['scope'])
formal=C.decode((HERE/'interface-kernel-evidence.json').read_bytes())
require(formal['result']=='pass','abstract interface compilation missing')
add('five-abstract-interface-theorems','Pinned Lean compilation','abstract-theorem',binding(HERE/'InterfaceSemantics.lean'),binding(HERE/'interface-kernel-evidence.json'),
    'Typed equality and refusal-cause properties; no admitted axioms','pass',formal['scope'])
seen=set()
for report in inherited['reports']:
    check(report['report']);check(report['control_origin'])
    for c in report['controls']:
        key=(report['task'],c['name'])
        if key in seen:continue
        seen.add(key);add('inherited-'+report['task']+'-'+c['name'],'Accepted '+report['task']+' control','inherited-control',report['control_origin'],report['report'],
            'Exact current accepted control','pass','Inherited finite evidence, not reexecuted or converted into a live event. Original report retains fresh/saved/unqualified IO distinctions.')
require(len(seen)==342,'inherited count changed')
suite={'schema':'relational.qualification-suite/v3','result':'pass','cases':cases,'catalog':binding(BASE/'p01/catalog.json'),
    'required_ids':[o['id'] for o in C.required_inventory('rule-only')],'source_receipts':inherited['source_receipts'],
    'finite_regression_only':True,'authority_effect':'none'}
Draft202012Validator(C.decode((HERE/'qualification-suite.schema.json').read_bytes())).validate(suite)
(HERE/'qualification-suite.json').write_text(json.dumps(suite,indent=2)+'\n')
report={'result':'pass','suite':binding(HERE/'qualification-suite.json'),'controls':controls,'catalog_audits':audits,
    'selected_successful_fresh_horn_qualifications':layout['actual_fresh_horn_qualifications']+rich['actual_fresh_horn_qualifications'],
    'successful_layout_horn_qualifications':layout['actual_fresh_horn_qualifications'],
    'selected_successful_applications':layout['actual_applications'],'new_fresh_mapped_qualifications':hostile['actual_fresh_mapped_checks'],
    'inherited_unique_controls':342,'new_control_cases':len(controls)-342,'actual_rich_combined_status':rich['observed'],
    'retained_staged_deadline_refusal':layout['retained_failure'],'saved_or_schema_validation_does_not_issue_live_event':True,
    'measured_profile_only':True,'author_review':'Candidate implementation review; not independent review or human use assessment','authority_effect':'none'}
Draft202012Validator(C.decode((HERE/'regression-report.schema.json').read_bytes())).validate(report)
(HERE/'regression-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Closed suite:',len(cases),'cases; 342 inherited')
