"""Verify typed participant contracts, separately from semantic theorem proofs."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import os
import re
import shutil
import subprocess
import time

HERE=Path(__file__).resolve().parent
N01=HERE.parents[1]
SUCCESSOR=N01.parents[1]
ROOT=SUCCESSOR.parents[5]
BASE=SUCCESSOR.parents[1]
LEAN=BASE/'v1/formal/.toolcache/lean-4.33.1-linux/bin/lean'
KERNEL=BASE/'v1/formal/.toolcache/lean-4.33.1-linux/lib/lean/libleanshared.so'
ALLOWED={'propext','Quot.sound','Classical.choice'}

def read(path):return json.loads(path.read_text())
def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')

def check_bindings(value):
    if isinstance(value,dict):
        if {'path','sha256'}<=value.keys():
            assert binding(ROOT/value['path'])['sha256']==value['sha256'],value['path']
        for v in value.values():check_bindings(v)
    elif isinstance(value,list):
        for v in value:check_bindings(v)

def variable_keys(term):
    return {(term['name'],term['sort'])} if term['tag']=='variable' else set()

def structural_audit():
    manifest=read(HERE/'generation-manifest.json');check_bindings(manifest)
    contracts=read(HERE/'anchor-contracts.json');check_bindings(contracts)
    obligations=read(N01/'batch-review/obligation-targets.json')
    ids={r['id'] for r in obligations['rows'] if r['category']=='forbidden'}
    assert len(ids)==contracts['obligation_count']==148
    assert ids=={r['id'] for r in contracts['obligations']}
    assert len(contracts['plans'])==contracts['branch_plan_count']==1982
    assert len({r['id'] for r in contracts['plans']})==1982
    assert {r['unit'] for r in contracts['plans']}=={f'K{i:02}' for i in range(41)}
    definitions={d['unit']:read(ROOT/d['definition']['path']) for d in read(N01/'batch-review/index.json')['units']}
    rows={r['id']:r for r in contracts['obligations']}
    checked=0
    for p in contracts['plans']:
        d=definitions[p['unit']];pair=d['ordered_pairs'][p['signature_branch_index']]
        assert (p['source_kind'],p['target_kind'])==(pair['source_kind'],pair['target_kind'])
        expected=[tuple(x.strip().split(':')) for x in rows[p['obligation_id']]['parameter_types'].split(',')]
        assert [(a['name'],a['declared_type']) for a in p['arguments']]==expected
        available=set();all_names=set()
        for b in p['independent_existential_binders']:
            assert b['name'] not in all_names and b['name'] and b['domain'] and b['selection_role']
            assert b['domain_authenticity_proved'] is False and b['joins']
            assert any(t['tag'] in {'source','target','witness'} for t in b['joins'].values())
            for term in b['joins'].values():assert variable_keys(term)<=available
            available.add((b['name'],b['sort']));all_names.add(b['name'])
        used=set()
        for a in p['arguments']:
            term=a['term'];assert term['sort']==a['sort']==contracts['sorts'][a['declared_type']]
            assert variable_keys(term)<=available
            used |= variable_keys(term)
            if term['tag']=='witness':assert term['name'] in d['notation']['witness_fields']
        for b in p['independent_existential_binders']:
            for term in b['joins'].values():used |= variable_keys(term)
        assert available<=used
        for c in p['constraints']:
            assert c['left']['sort']==c['right']['sort']==c['sort']
            assert variable_keys(c['left'])|variable_keys(c['right'])<=available
        assert p['actual_owner_assessment'] is None
        assert p['non_entailment_proved'] is p['raw_source_role_projection_proved'] is False
        checked+=1
    assert sum(m['anchor_plan_definitions'] for m in manifest['modules'])==1982
    assert all(len(m['declarations'])==m['anchor_plan_definitions'] for m in manifest['modules'])
    declarations=[name for m in manifest['modules'] for name in m['declarations']]
    assert len(declarations)==len(set(declarations))==1982
    # Meaningful semantic-role regression expectations, independent of the
    # builder's fixed-parameter implementation. These are finite audits only.
    regression=[]
    def select(unit,label):return [p for p in contracts['plans'] if p['unit']==unit and p['conclusion_label']==label]
    def argument(plan,name):return next(a['term'] for a in plan['arguments'] if a['name']==name)
    def expect(unit,label,name,term):
        selected=select(unit,label);assert selected
        for p in selected:assert argument(p,name)==term,(p['id'],name)
        regression.append({'unit':unit,'label':label,'argument':name,'expected':term,'branches':len(selected),'result':'pass'})
    expect('K04','benefit','application',{'tag':'source','sort':'ref'})
    expect('K04','compliance','application',{'tag':'source','sort':'ref'})
    expect('K04','method-use','subject',{'tag':'witness','sort':'ref','name':'sessionOrAction'})
    expect('K13','installation','control',{'tag':'witness','sort':'ref','name':'control'})
    expect('K13','execution','control',{'tag':'witness','sort':'ref','name':'control'})
    expect('K13','effectiveness','subject',{'tag':'witness','sort':'ref','name':'control'})
    expect('K18','truth','claim',{'tag':'witness','sort':'ref','name':'proposition'})
    expect('K18','claim-acceptance','claim',{'tag':'witness','sort':'ref','name':'proposition'})
    expect('K14','cross-effect-inference','declared',{'tag':'witness','sort':'effect','name':'effect'})
    expect('K14','effect-execution','effect',{'tag':'witness','sort':'effect','name':'effect'})
    expect('K00','unrestricted-authority','universe',{'tag':'frame','sort':'universe','name':'ownedUniverse'})
    expect('K30','acceptance','subject',{'tag':'target','sort':'ref'})
    expect('K30','correctness','output',{'tag':'target','sort':'ref'})
    for unit in ['K11','K20']:
        for p in select(unit,'currentness'):
            term=argument(p,'source');assert term['tag']=='variable'
            binder=next(b for b in p['independent_existential_binders'] if b['name']==term['name'])
            assert binder['domain']=='view-lineage'
            assert binder['joins']['view']['tag']==('target' if unit=='K11' else 'source')
        regression.append({'unit':unit,'label':'currentness','argument':'source','expected':'Exact independently included source of the view, not the view or session itself','branches':len(select(unit,'currentness')),'result':'pass'})
    for p in select('K22','successful-performance'):
        term=argument(p,'agent')
        assert term['tag']==('source' if p['source_kind']=='agent-instance' else 'variable')
    regression.append({'unit':'K22','label':'successful-performance','argument':'agent','expected':'Source instance or independently associated instance of the source profile','branches':2,'result':'pass'})
    for label in ['closure','recovery-success']:
        for p in select('K34',label):assert argument(p,'incident')['tag']==('target' if p['target_kind']=='incident' else 'variable')
        regression.append({'unit':'K34','label':label,'argument':'incident','expected':'Exact Incident; a Failure Occurrence is not relabeled as an Incident','branches':2,'result':'pass'})
    for p in select('K26','assignment'):
        assert argument(p,'assignee')['tag']==('source' if p['source_kind'] in {'agent-instance','person-reference','team'} else 'variable')
    regression.append({'unit':'K26','label':'assignment','argument':'assignee','expected':'Assignable source or independently associated assignee; a Work/action/artifact is not relabeled as an actor','branches':len(select('K26','assignment')),'result':'pass'})
    write(HERE/'structural-audit.json',{'result':'all-anchor-plans-structurally-consistent','anchor_contracts':binding(HERE/'anchor-contracts.json'),'checked_plans':checked,'exact_original_ids':148,'semantic_role_regressions':regression,'regression_families':len(regression),'formal_source_semantics_proved':False,'inherited_discharges':0})
    return manifest

def negative_sources():
    prefix='import AnchorContracts\nopen CandidateConclusionAnchors\n'
    field_bad=prefix+'def bad : Term 4 .ref := .witnessField "control" (by decide)\n'
    frame_bad=prefix+'def bad : Term 4 .ref := .frameField "fabricatedAuthority" (by decide)\n'
    effect_bad=prefix+'def bad : Term 36 .effect := .witnessField "effect" (by decide)\n'
    world_bad=prefix+'def bad : Term 18 .world := .frameField "scope" (by decide)\n'
    bool_bad=prefix+'def bad : Term 18 .world := true\n'
    def plan(arguments,binders):
        return prefix+'def bad : Plan 4 [.ref] :=\n  { obligationId := "control", sourceKind := "lesson-application", targetKind := "operational-lesson", branchIndex := 0, arguments := '+arguments+', binders := '+binders+', constraints := [], structurallyValid := by decide }\n'
    def binder(name='x',sort='ref',joins=None):
        if joins is None:joins='[("subject", ⟨.ref, .source⟩)]'
        return '{ name := "'+name+'", sort := .'+sort+', domain := "independent-catalog", selectionRole := "exact selected role", joins := '+joins+' }'
    unbound=plan('.cons (.variable "x") .nil','[]')
    mismatch=plan('.cons (.frameField "frame" (by decide)) .nil','[]')
    self_join=plan('.cons (.variable "x") .nil','['+binder(joins='[("subject", ⟨.ref, .source⟩), ("self", ⟨.ref, .variable "x"⟩)]')+']')
    unused=plan('.cons .source .nil','['+binder()+']')
    duplicate=plan('.cons (.variable "x") .nil','['+binder()+', '+binder()+']')
    wrong_sort=plan('.cons (.variable "x") .nil','['+binder(sort='world')+']')
    unanchored=plan('.cons (.variable "x") .nil','['+binder(joins='[("scope", ⟨.ref, .frameField "scope" (by decide)⟩)]')+']')
    forward=plan('.cons (.variable "x") .nil','['+binder(joins='[("subject", ⟨.ref, .source⟩), ("later", ⟨.ref, .variable "y"⟩)]')+', '+binder(name='y')+']')
    return {'wrong_witness_unit':field_bad,'unknown_frame_field':frame_bad,'succession_is_not_governance_effect':effect_bad,'scope_is_not_truth_world':world_bad,'truth_is_not_supplied_boolean':bool_bad,'unbound_argument':unbound,'frame_is_not_revision':mismatch,'self_seeded_binder':self_join,'unused_existential':unused,'duplicate_binder':duplicate,'binder_sort_substitution':wrong_sort,'no_primary_participant':unanchored,'forward_reference_cycle':forward}

def run():
    manifest=structural_audit()
    assert binding(LEAN)['sha256']=='e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
    assert binding(KERNEL)['sha256']=='23d636cac1cadcba37beac30eff9b9b20d66cee726cf5defb4ae39f1284a3e5a'
    sources=[manifest['core_source']]+[m['source'] for m in manifest['modules']]
    for b in sources:
        text=(ROOT/b['path']).read_text()
        assert not re.search(r'\b(sorry|admit|native_decide)\b|^axiom\s',text,re.M),b['path']
    modules={Path(m['source']['path']).stem:m for m in manifest['modules']}
    records=[];negative_records=[];imports=[]
    negative=negative_sources();write(HERE/'negative-control-index.json',{'controls':list(negative),'count':len(negative),'meaning':'Expected compiler refusal of invalid anchor typing/binding, not semantic refutation.'})
    start=time.monotonic()
    for phase in ['compile','replay']:
        directory=HERE/phase
        assert not directory.exists(), 'Fresh verification output directory already exists; preserve it and use a new version.'
        directory.mkdir();env=os.environ.copy();env['LEAN_PATH']=str(directory)
        core_outputs=[]
        for b in sources:
            source=ROOT/b['path'];copy=directory/source.name;shutil.copyfile(source,copy)
            assert binding(copy)['sha256']==b['sha256']
            module=source.stem
            result=subprocess.run([str(LEAN),'-o',module+'.olean',source.name],cwd=directory,env=env,text=True,capture_output=True,timeout=180)
            output=result.stdout+result.stderr;log=directory/(module+'.txt');log.write_text(output)
            expected=modules.get(module,{}).get('declarations',[])
            inspected=re.findall(r"'([^']+)' (?:depends on axioms: \[[^\]]*\]|does not depend on any axioms)",output)
            assert Counter(inspected)==Counter(expected),(phase,module,'axiom inspection mismatch')
            axioms=set()
            for group in re.findall(r'depends on axioms: \[([^\]]*)\]',output):axioms.update(x.strip() for x in group.split(',') if x.strip())
            assert result.returncode==0,(phase,module,output[:3000])
            assert axioms<=ALLOWED and 'sorryAx' not in output,(phase,module,axioms)
            outputs=[binding(p) for p in sorted(directory.glob(module+'.olean*')) if p.is_file()]
            assert outputs
            records.append({'phase':phase,'source':b,'compiled_source_copy':binding(copy),'outputs':outputs,'log':binding(log),'exit_code':result.returncode,'axioms':sorted(axioms),'inspected_anchor_definitions':len(inspected)})
            if module=='AnchorContracts':core_outputs=outputs
            else:
                assert core_outputs
                imports.append({'phase':phase,'consumer':b,'module':'AnchorContracts','resolved_outputs':core_outputs,'search_path':str(directory.relative_to(ROOT)),'same_phase':True})
            if module in {'AnchorContracts','AnchorsK09','AnchorsK18','AnchorsK30','AnchorsK40'}:
                print(json.dumps({'phase':phase,'compiled_module':module,'typed_anchor_definitions':len(expected)}),flush=True)
        negative_dir=directory/'negative';negative_dir.mkdir()
        for name,text in negative.items():
            source=negative_dir/(name+'.lean');source.write_text(text)
            result=subprocess.run([str(LEAN),'-o',name+'.olean',source.name],cwd=negative_dir,env=env,text=True,capture_output=True,timeout=60)
            output=result.stdout+result.stderr;log=negative_dir/(name+'.txt');log.write_text(output)
            assert result.returncode!=0 and 'error' in output,(phase,name,'invalid contract was accepted')
            assert not (negative_dir/(name+'.olean')).exists(),(phase,name)
            negative_records.append({'phase':phase,'control':name,'source':binding(source),'log':binding(log),'exit_code':result.returncode,'expected':'compiler-refusal','result':'pass'})
        print(json.dumps({'phase':phase,'invalid_contract_refusals':len(negative),'phase_complete':True}),flush=True)
    report={'schema':'relational.conclusion-anchor-typechecking/v1','result':'all-typed-anchor-contracts-compile-and-replay-pass',
      'driver':binding(Path(__file__)),'generation_manifest':binding(HERE/'generation-manifest.json'),'anchor_contracts':binding(HERE/'anchor-contracts.json'),
      'structural_audit':binding(HERE/'structural-audit.json'),'negative_control_index':binding(HERE/'negative-control-index.json'),
      'lean_binary':binding(LEAN),'kernel_library':binding(KERNEL),'allowed_axioms':sorted(ALLOWED),
      'source_modules':42,'general_anchor_grammar_modules':1,'relation_anchor_modules':41,'typed_anchor_definitions':1982,'exact_obligation_ids':148,
      'kernel_inspections':3964,'fresh_successful_module_calls':84,'negative_refusal_controls':len(negative),'negative_compiler_calls':len(negative_records),
      'records':records,'import_resolution':imports,'negative_records':negative_records,'elapsed_seconds':round(time.monotonic()-start,3),
      'new_named_theorem_declarations':0,'semantic_non_entailment_proofs':0,'raw_source_projection_refinement_proofs':0,
      'independent_checker_run':False,'owner_approval_supplied':False,'inherited_discharges':0,'N01_accepted':False,'authority_effect':'none',
      'claim_ceiling':'Kernel-checked dependent argument sorts, declared witness/frame slots, closed and ordered existential bindings, nonempty primary participant anchoring, and exact proposed signature coverage. Not a proof of the independent conclusion predicates, source projections, catalog authenticity or complete-theory non-entailment.'}
    assert sum(r['inspected_anchor_definitions'] for r in records)==3964
    assert len(records)==84 and len(imports)==82
    write(HERE/'verification.json',report)
    print(json.dumps({k:report[k] for k in ['result','typed_anchor_definitions','exact_obligation_ids','kernel_inspections','fresh_successful_module_calls','negative_refusal_controls','negative_compiler_calls','new_named_theorem_declarations','inherited_discharges','elapsed_seconds']}),flush=True)

if __name__=='__main__':run()
