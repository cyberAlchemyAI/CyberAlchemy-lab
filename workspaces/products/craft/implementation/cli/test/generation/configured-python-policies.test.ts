import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {compileSelectedProjectFields,EXACT_PROJECT_FIELD_SELECTION_VERSION,EXACT_FIELD_CONTRACT_SHA256} from '../../src/input/compiled-field-model.ts';
import {planConfiguredPythonPolicies,PYTHON_POLICY_VERSION} from '../../src/generation/configured-python-policies.ts';
import {PYTHON_STRUCTURED_RULE_VERSION} from '../../src/generation/configured-python-rules.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),base='development/reconciliation-v1/profile-compiler-reconciliation/';
const bytes=(p:string)=>fs.readFileSync(path.join(project,p),'utf8'),read=(p:string)=>JSON.parse(fs.readFileSync(p,'utf8'));
const sources={policy_contract:bytes(base+'policy-generation-contract.json'),rules:{
 configuration:bytes(base+'configuration.json'),base:bytes('development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json'),python:bytes('development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json'),
 rule_contract:bytes(base+'string-order-rule-contract.json'),collection_contract:bytes(base+'rule-collection-value-contract.json'),predicate_contract:bytes(base+'rule-collection-predicate-contract.json'),numeric_contract:bytes(base+'rule-numeric-contract.json'),
 exact_contract:bytes(base+'rule-exact-contract.json'),literal_contract:bytes(base+'rule-exact-literal-contract.json'),structured_contract:bytes(base+'rule-structured-value-contract.json'),field_contract:bytes('development/reconciliation-v1/contracts/exact-field-and-reference-model.json')
}};
const boundarySource=bytes('development/reconciliation-v1/contracts/composition-boundary.json');
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'commerce:'+id}),wrap=(kind:string,element:any):any=>({kind,element});
const at=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:any):any=>({op:'literal',type,value}),eq=(left:any,right:any):any=>({op:'eq',left,right});
const property=(name:string,type:any,identity=false):any=>({name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name,ontology_property:'FIXTURE-ORDER#'+name});
const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-CHOICE#Amount',payload:scalar('UInt64')}]};
const arg=(parameter:string,value:any)=>({parameter,value}),ref=(selector:string,args:any[])=>({selector:'commerce:'+selector,arguments:args});
const policyInputs=[{name:'order',type:named('order')},{name:'total',type:scalar('UInt64')},{name:'active',type:scalar('Bool')},{name:'note',type:wrap('optional',scalar())},{name:'amounts',type:wrap('list',scalar('UInt64'))},{name:'tags',type:wrap('set',scalar())},{name:'choice',type:choice},{name:'status',type:named('status')}];
function fixture(t:any){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-policies-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const source=path.join(temp,'source'),nodes:string[]=[],edges:string[]=[];
 const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v));};
 const node=(id:string,kind:string,body:any)=>{nodes.push(id);write('specs/commerce/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'commerce',node_id:id,kind,body:{description:id,...body}});};
 const edge=(id:string,relationship:string,from:string,to:string)=>{edges.push(id);write('specs/commerce/edges/'+id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'commerce',edge_id:id,relationship,source_node_id:from,target_node_id:to,scope:'feature'});};
 node('order','Entity',{fields:['id','enabled'],typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-ORDER',properties:[property('id',scalar(),true),property('enabled',scalar('Bool'))]}});
 node('status','Enum',{values:['Ready','Draft'],typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:['Ready','Draft'].map(name=>({name,ontology_variant:'FIXTURE-STATUS#'+name,payload:null}))}});
 for(const id of ['accept','reject'])node(id,'Operation',{reads:[],writes:[],effects:[],guard:'external',failure_continuation:'fail'});
 node('review','Calculation',{inputs:['total'],typed_contract:{schema_version:'domainspec.typed-calculation/v1',ontology_calculation:'FIXTURE-REVIEW',inputs:[{name:'total',type:scalar('UInt64')}],result:scalar('UInt64'),division_rounding:'reject',expression:{op:'input',name:'total'}}});
 edge('review-calculates-accept','calculates','review','accept');
 const rule=(id:string,parameters:any[],expression:any)=>node(id,'Rule',{predicate:'structured:domainspec.typed-rule/v2',typed_contract:{schema_version:'domainspec.typed-rule/v2',ontology_rule:'FIXTURE-'+id.toUpperCase(),parameters,expression}});
 rule('high',[{name:'amount',type:scalar('UInt64')}],{op:'lt',left:lit('UInt64','100'),right:at('amount')});
 rule('forward',[{name:'amount',type:scalar('UInt64')}],{op:'rule_ref',...ref('high',[arg('amount',at('amount'))])});
 const eligibleParams=[policyInputs[0],policyInputs[2],policyInputs[3],{name:'numbers',type:wrap('set',scalar('UInt64'))},policyInputs[5],policyInputs[6],policyInputs[7]];
 rule('eligible',eligibleParams,{op:'all',terms:[eq(at('active'),lit('Bool',true)),eq(at('order','FIXTURE-ORDER#enabled'),lit('Bool',true)),eq(at('status'),{op:'variant',selector:'FIXTURE-STATUS#Ready'}),{op:'contains',left:at('numbers'),right:lit('UInt64','2')},eq(at('note'),at('note')),eq(at('tags'),at('tags')),eq(at('choice'),at('choice'))]});
 const full:any={schema_version:'domainspec.typed-policy/v2',ontology_policy:'FIXTURE-CHOOSE',inputs:policyInputs,cases:[{target:'commerce:review',rule:ref('forward',[arg('amount',at('total'))])},{target:'commerce:accept',rule:ref('eligible',eligibleParams.map((p:any)=>arg(p.name,p.name==='numbers'?{op:'to_set',value:at('amounts')}:at(p.name))))}],default_target:'commerce:reject'};
 full.cases.push({target:'commerce:review',rule:ref('forward',[arg('amount',lit('UInt64','0'))])});
 const scalarPolicy:any={...full,ontology_policy:'FIXTURE-SCALAR',inputs:[{name:'total',type:scalar('UInt64')}],cases:[{target:'commerce:accept',rule:ref('high',[arg('amount',at('total'))])}]};
 const repeated:any={...full,ontology_policy:'FIXTURE-REPEATED',cases:[full.cases[0],{...full.cases[1],target:'commerce:review'}]};
 const policies:any={choose:full,scalar:scalarPolicy,repeated};
 for(const [id,c]of Object.entries(policies) as [string,any][]){
  node(id,'Policy',{typed_contract:c});
  for(const target of new Set([...c.cases.map((x:any)=>x.target),c.default_target]) as Set<string>)edge(id+'-applies-'+target.split(':')[1],'applies',id,target.split(':')[1]!);
 }
 const saveIndex=()=>{write('project.json',{schema_version:'domainspec.project/v1',project_id:'policy-rules',features:['commerce'],cross_feature_edges:[]});write('specs/commerce/feature.json',{schema_version:'domainspec.feature/v1',feature_id:'commerce',nodes,edges});};saveIndex();
 const compile=()=>{
  const graph=loadCompiledProjectGraph(source),certificate=createCompiledProjectCertificate(graph),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256},boundarySource);
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256:certificate.graph_sha256,roots:['commerce:order','commerce:status'],bindings:[]},sources.rules.field_contract);
  const selection:any={schema_version:PYTHON_POLICY_VERSION,language:'python',rule_selection:PYTHON_STRUCTURED_RULE_VERSION,boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256,module_root:'application',roots:['commerce:choose','commerce:scalar','commerce:repeated']};
  return {graph,boundary,fields,selection,plan:()=>planConfiguredPythonPolicies(graph,boundary,fields,selection,sources)};
 };
 return {temp,source,write,node,edge,saveIndex,policies,compile,...compile()};
}

type Plan=ReturnType<typeof planConfiguredPythonPolicies>;
function materialize(root:string,p:Plan){for(const a of p.artifacts){const f=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,a.content);}}
function payload(root:string,p:Plan,f:ReturnType<typeof fixture>){return {root,modules:p.modules,files:p.artifacts.map(a=>a.relative_path),contracts:Object.fromEntries(Object.entries(f.policies).map(([k,v])=>['commerce:'+k,v])),model:p.field_compilation_sha256?f.fields.model:null,runtime_dir:path.posix.dirname(p.artifacts.find(a=>a.relative_path.endsWith('/runtime/facts.py'))!.relative_path),rule_artifacts:p.rule_plan.artifacts.map(a=>({relative_path:a.relative_path,sha256:a.sha256})),rule_modules:p.rule_plan.modules,rule_contracts:Object.fromEntries(f.graph.nodes.filter(n=>n.kind==='Rule').map(n=>[n.selector,n.body.typed_contract]))};}
const observer=path.join(project,'impl/cli/src/verification/python-policy-observer.py');
const nativeScript=String.raw`
import copy, dataclasses, importlib, json, os, pathlib, sys, typing
data=json.load(sys.stdin);sys.path.insert(0,data['root']);f={};providers={}
def thaw(v):
    if type(v) is tuple:return [thaw(x) for x in v]
    if hasattr(v,'items'):return {k:thaw(x) for k,x in v.items()}
    return v
for m in data['modules']:
    fn=getattr(importlib.import_module(m['import_name']),m['callable']);name=m['selector'].split(':')[1];f[name]=fn
    providers[name]=importlib.import_module(m['provider_path'][:-3].replace('/','.'))
    assert thaw(fn.descriptor)==m['descriptor']
    hints=typing.get_type_hints(fn.__call__)
    assert typing.get_origin(hints['return']) is typing.Literal
    assert set(typing.get_args(hints['return']))=={c['selector'] for c in fn.descriptor['catalogue']}
    assert set(typing.get_type_hints(hints['parameters']))=={p['name'] for p in fn.descriptor['inputs']}
    for action in [lambda:setattr(fn,'descriptor',{}),lambda:fn.descriptor.__setitem__('evaluation','last'),lambda:fn.descriptor['catalogue'][0].__setitem__('selector','foreign')]:
        try:action()
        except (TypeError,AttributeError):pass
        else:raise AssertionError('MUTABLE_BINDING')
def args(total=2):return {'order':{'id':'order','enabled':True},'total':total,'active':True,'note':None,'amounts':[2,2,1],'tags':['b','a'],'choice':{'variant':'Amount','payload':'18446744073709551615'},'status':{'variant':'Ready'}}
def error(fn,p):
    try:fn(p)
    except TypeError as e:assert str(e)=='POLICY_INPUT',str(e)
    else:raise AssertionError('EXPECTED_POLICY_INPUT')
events=[];armed=False
def audit(event,args):
    if armed and (event in ('open','exec','compile','import') or event.startswith(('os.','socket.','subprocess.'))):events.append(event)
sys.addaudithook(audit);armed=True
results=[]
if 'scalar' in f:
    for n in [0,100,101,'9007199254740993','18446744073709551615']:
        expected='commerce:accept' if int(n)>100 else 'commerce:reject';actual=f['scalar']({'total':n});assert actual==expected;results.append(actual)
    for n in [True,1.0,-1,'01','+1','18446744073709551616',None]:error(f['scalar'],{'total':n})
if 'choose' in f:
    # These expectations come from the authored Rules, not generated descriptors.
    for total in [0,100,101,'18446744073709551615']:
        for active in [False,True]:
            for enabled in [False,True]:
                for status in ['Ready','Draft']:
                    p=args(total);p['active']=active;p['order']['enabled']=enabled;p['status']['variant']=status
                    expected='commerce:review' if int(total)>100 else 'commerce:accept' if active and enabled and status=='Ready' else 'commerce:reject'
                    before=copy.deepcopy(p);actual=f['choose'](p);assert actual==expected and type(actual) is str;assert p==before;results.append(actual)
                    assert f['repeated'](p)==('commerce:review' if expected!='commerce:reject' else 'commerce:reject')
    for name in ['choose','repeated']:
        for p in [None,[],{},dict(args(),extra=1)]:error(f[name],p)
        p=args();del p['note'];error(f[name],p)
        # Even a winning first case cannot hide invalid unused input.
        for patch in [{'active':1},{'note':1},{'amounts':[True]},{'tags':['a','a']},{'choice':{'variant':'None','payload':None}},{'status':{'variant':'Missing'}}]:error(f[name],{**args(101),**patch})
    assert f['choose']({**args(),'amounts':[1]})=='commerce:reject'
    for choice in [{'variant':'None'},{'variant':'Amount','payload':0}]:assert f['choose']({**args(),'choice':choice})=='commerce:accept'
    assert f['choose']({**args(),'tags':['😀','é','e\u0301'],'note':'\ud83d\ude00'})=='commerce:accept'
    calls=[]
    class ActiveDict(dict):
        def __getitem__(self,key):calls.append('get');return super().__getitem__(key)
    class ActiveInt(int):
        def __int__(self):calls.append('int');return 0
    class ActiveList(list):
        def __iter__(self):calls.append('iterate');return super().__iter__()
    error(f['choose'],ActiveDict(args()));error(f['choose'],{**args(),'order':ActiveDict(args()['order'])})
    error(f['choose'],{**args(),'total':ActiveInt(1)});error(f['choose'],{**args(),'amounts':ActiveList([2])})
    assert calls==[]
armed=False;assert events==[],events
if 'choose' in f:
    # Fault injection proves lazy argument construction and separate Rule failures.
    provider=providers['choose'];original=provider._to_set
    def bomb(*args):raise RuntimeError('LATE_ARGUMENT')
    provider._to_set=bomb
    assert f['choose'](args(101))=='commerce:review'
    try:f['choose'](args(1))
    except RuntimeError as e:assert str(e)=='LATE_ARGUMENT'
    else:raise AssertionError('MISSING_ARGUMENT_EVALUATION')
    provider._to_set=original
    dependency=provider._condition1
    def bad_rule(*args):raise TypeError('RULE_INPUT')
    provider._condition1=bad_rule
    try:f['choose'](args(101))
    except TypeError as e:assert str(e)=='RULE_INPUT'
    else:raise AssertionError('SWALLOWED_RULE_ERROR')
    provider._condition1=dependency
assert not any('.domain.operations.' in name or '.domain.calculations.' in name for name in sys.modules)
for file in data['files']:compile(pathlib.Path(data['root'],file).read_bytes(),file,'exec')
print(json.dumps({'pid':os.getpid(),'results':results,'effects':events}))
`;

test('R10 Python Policy binds current graph, Rule closure and immutable strategy catalogue',t=>{
 const f=fixture(t),p=f.plan();assert.equal(p.modules.length,3);assert.deepEqual(f.plan(),p);
 assert.deepEqual(planConfiguredPythonPolicies(f.graph,f.boundary,f.fields,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
 assert.deepEqual(p.rule_plan.modules.map(m=>m.selector),['commerce:eligible','commerce:forward','commerce:high']);
 assert.ok(p.artifacts.every(a=>!a.relative_path.includes('/operations/')&&!a.relative_path.includes('/calculations/')));
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
 for(const m of p.modules){const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));assert.equal(d.strategy_set_sha256,sha256(canonicalJson(d.catalogue)));assert.ok(Object.isFrozen(d.catalogue[0]));}
 const target=read(path.join(f.source,'specs/commerce/nodes/accept.json'));target.body.description+=' changed';f.write('specs/commerce/nodes/accept.json',target);const next=f.compile().plan();
 assert.notEqual(next.modules[0]!.descriptor.strategy_set_sha256,p.modules[0]!.descriptor.strategy_set_sha256);
 fs.renameSync(f.source,path.join(f.temp,'gone'));assert.deepEqual(f.plan(),p);
});

test('R10 Python Policy rejects stale boundaries, active inputs, implicit migration and invalid contracts',t=>{
 const f=fixture(t);
 for(const patch of [{schema_version:'future'},{language:'typescript'},{rule_selection:'legacy'},{boundary_sha256:'stale'},{field_compilation_sha256:'stale'},{module_root:'../escape'},{module_root:'encodings'},{roots:[]},{roots:['commerce:choose','commerce:choose']},{roots:['commerce:order']},{extra:1}])assert.throws(()=>planConfiguredPythonPolicies(f.graph,f.boundary,f.fields,{...f.selection,...patch},sources));
 assert.throws(()=>planConfiguredPythonPolicies(structuredClone(f.graph),f.boundary,f.fields,f.selection,sources));assert.throws(()=>planConfiguredPythonPolicies(f.graph,structuredClone(f.boundary),f.fields,f.selection,sources));assert.throws(()=>planConfiguredPythonPolicies(f.graph,f.boundary,structuredClone(f.fields),f.selection,sources));
 assert.throws(()=>planConfiguredPythonPolicies(f.graph,f.boundary,f.fields,f.selection,{...sources,policy_contract:sources.policy_contract+' '}),/source drift/);
 for(const k of Object.keys(sources.rules))assert.throws(()=>planConfiguredPythonPolicies(f.graph,f.boundary,f.fields,f.selection,{...sources,rules:{...sources.rules,[k]:sources.rules[k as keyof typeof sources.rules]+' '}}),/source drift/);
 let reads=0;assert.throws(()=>planConfiguredPythonPolicies(f.graph,f.boundary,f.fields,{...f.selection,get roots(){reads++;return [];}},sources));assert.equal(reads,0);
 const file='specs/commerce/nodes/choose.json',original=read(path.join(f.source,file));
 const bad=structuredClone(original);bad.body.typed_contract.cases[0].rule.arguments[0].value=at('active');f.write(file,bad);assert.throws(()=>f.compile().plan(),/type mismatch/);f.write(file,original);
 const scalarFile='specs/commerce/nodes/scalar.json',scalarOriginal=read(path.join(f.source,scalarFile));
 const legacy=structuredClone(scalarOriginal);legacy.body.typed_contract={schema_version:'domainspec.typed-policy/v1',ontology_policy:'FIXTURE-LEGACY',inputs:[{name:'total',type:scalar('UInt64')}],cases:[{target:'commerce:accept',when:{op:'gt',left:{kind:'parameter',name:'total'},right:{kind:'literal',type:'UInt64',value:100}}}],default_target:'commerce:reject'};
 legacy.body.strategies=['accept','reject'];f.write(scalarFile,legacy);assert.throws(()=>f.compile().plan(),/typed Policy v2 required/);f.write(scalarFile,scalarOriginal);
 const empty=structuredClone(scalarOriginal);empty.body.typed_contract.inputs=[];empty.body.typed_contract.cases[0].rule.arguments[0].value=lit('UInt64','101');f.write(scalarFile,empty);assert.throws(()=>f.compile().plan(),/explicit inputs and distinct strategies/);f.write(scalarFile,scalarOriginal);
 const changed=structuredClone(original);changed.body.typed_contract.ontology_policy='FIXTURE-CHANGED';f.write(file,changed);const next=f.compile();
 assert.throws(()=>planConfiguredPythonPolicies(f.graph,next.boundary,next.fields,{...next.selection},sources),/cross-graph/);
});

test('R10 native Python Policy preserves source-order Rules, scalar-only selection and pure identity returns',t=>{
 const f=fixture(t),results:any[]=[];
 for(const module_root of ['application','relocated/nested']){
  const p=planConfiguredPythonPolicies(f.graph,f.boundary,f.fields,{...f.selection,module_root},sources),root=path.join(f.temp,module_root);materialize(root,p);const input=JSON.stringify(payload(root,p,f));
  results.push(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B','-c',nativeScript],{input,encoding:'utf8'})));
  assert.deepEqual(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B',observer],{input,encoding:'utf8'})),{observed:3});
 }
 assert.notEqual(results[0].pid,results[1].pid);assert.deepEqual(results[0].results,results[1].results);
 const p=planConfiguredPythonPolicies(f.graph,f.boundary,null,{...f.selection,roots:['commerce:scalar'],field_compilation_sha256:null},sources),root=path.join(f.temp,'scalar');materialize(root,p);const input=JSON.stringify(payload(root,p,f));
 execFileSync('/usr/bin/python3',['-I','-B','-c',nativeScript],{input,encoding:'utf8'});assert.deepEqual(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B',observer],{input,encoding:'utf8'})),{observed:1});
 // A changed authored transitive Rule changes native Policy selection and binding.
 const file='specs/commerce/nodes/high.json',node=read(path.join(f.source,file));node.body.typed_contract.expression.left.value='200';f.write(file,node);const fresh=f.compile(),next=fresh.plan(),changedRoot=path.join(f.temp,'changed');materialize(changedRoot,next);
 assert.notEqual(next.rule_plan.plan_sha256,f.plan().rule_plan.plan_sha256);
 const m=next.modules.find(m=>m.selector==='commerce:scalar')!;
 assert.equal(execFileSync('/usr/bin/python3',['-I','-B','-c','import sys,importlib;sys.path.insert(0,sys.argv[1]);print(getattr(importlib.import_module(sys.argv[2]),sys.argv[3])({"total":150}))',changedRoot,m.import_name,m.callable],{encoding:'utf8'}).trim(),'commerce:reject');
});

test('R10 independent Policy observation kills compiling selection, effect and binding mutations',t=>{
 const f=fixture(t),p=f.plan(),root=path.join(f.temp,'mutants');materialize(root,p);const m=p.modules.find(m=>m.selector==='commerce:choose')!,file=path.join(root,m.provider_path),original=fs.readFileSync(file,'utf8');
 const mutants=[original.replace('if _condition1(','if not _condition1('),original.replace('return "commerce:review"','return "commerce:reject"'),original.replace('return "commerce:reject"','return "commerce:accept"'),original.replace('keyed.setdefault(element.key(item), item)','keyed[element.key(item)] = item'),original.replace('    if _condition1(', '    globals()["write"] = 1\n    if _condition1('),original.replace('    if _condition1(', '    parameters["write"] = 1\n    del parameters["write"]\n    if _condition1('),original.replace('return "commerce:review"','yield "commerce:review"')];
 for(const mutant of mutants){
  assert.notEqual(mutant,original);fs.writeFileSync(file,mutant);execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:mutant});
  const changed:any=structuredClone(m);changed.descriptor.provider.sha256=sha256(mutant);
  const result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...payload(root,p,f),modules:[changed]}),encoding:'utf8'});assert.notEqual(result.status,0);assert.match(result.stderr,/semantics or effects/);
 }
 fs.writeFileSync(file,original);const facadeFile=path.join(root,m.relative_path),facade=fs.readFileSync(facadeFile,'utf8');fs.writeFileSync(facadeFile,facade.replace('frozen=True','frozen=False'));
 const result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...payload(root,p,f),modules:[m]}),encoding:'utf8'});assert.notEqual(result.status,0);assert.match(result.stderr,/frozen provider binding/);
 fs.writeFileSync(facadeFile,facade);
 const high=p.rule_plan.modules.find(m=>m.selector==='commerce:high')!,ruleFile=path.join(root,high.relative_path),rule=fs.readFileSync(ruleFile,'utf8');
 for(const mutant of [rule.replace('100 < p0','100 > p0'),rule.replace('    return (100', '    globals()["write"] = 1\n    return (100')]){
  assert.notEqual(mutant,rule);fs.writeFileSync(ruleFile,mutant);execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:mutant});
  const data=payload(root,p,f);data.rule_artifacts.find(a=>a.relative_path===high.relative_path)!.sha256=sha256(mutant);
  const r=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...data,modules:[m]}),encoding:'utf8'});assert.notEqual(r.status,0);assert.match(r.stderr,/Rule semantics\/effects/);
 }
});
