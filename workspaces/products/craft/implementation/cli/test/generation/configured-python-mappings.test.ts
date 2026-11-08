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
import {planConfiguredPythonMappings, PYTHON_MAPPING_VERSION} from '../../src/generation/configured-python-mappings.ts';
import {sha256,canonicalJson} from '../../src/input/source-manifest.ts';
const project=path.resolve(import.meta.dirname,'../../../..'),pkg=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes=(f:string)=>fs.readFileSync(f,'utf8'),read=(f:string)=>JSON.parse(bytes(f));
const sources={configuration:bytes(path.join(pkg,'configuration.json')),base:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),python:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json')),mapping_contract:bytes(path.join(pkg,'mapping-generation-contract.json')),field_contract:bytes(path.join(project,'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'))};
const boundaryContract=bytes(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json')),fieldContract=bytes(path.join(project,'development/reconciliation-v1/contracts/exact-field-and-reference-model.json'));
const scalar=(name='String'):any=>({kind:'scalar',name}),named=(id:string):any=>({kind:'named',selector:'alpha:'+id}),wrap=(kind:string,element:any):any=>({kind,element});
const prop=(owner:string,name:string,type:any,identity=false):any=>({ontology_property:'FIXTURE-'+owner+'#'+name,name,type,identity,cardinality:type.kind==='optional'?'optional':type.kind==='list'?'many':type.kind==='set'?'many-unique':'one',meaning:name});
const value=(root:string,...properties:string[]):any=>({op:'path',root,properties}),lit=(type:string,value:string|boolean):any=>({op:'literal',type,value});
const field=(target:string,value:any,fallback:any=null):any=>({target,value,default:fallback});
const choice={kind:'sum',variants:[{name:'None',ontology_variant:'FIXTURE-CHOICE#None',payload:null},{name:'Amount',ontology_variant:'FIXTURE-CHOICE#Amount',payload:scalar('UInt64')},{name:'Money',ontology_variant:'FIXTURE-CHOICE#Money',payload:named('money')}]};
const orderFields=[prop('ORDER','id',scalar(),true),prop('ORDER','amount',scalar('UInt64')),prop('ORDER','enabled',scalar('Bool')),prop('ORDER','memo',wrap('optional',scalar())),prop('ORDER','money',named('money')),prop('ORDER','customer',named('mapping-customer')),prop('ORDER','lines',wrap('list',named('money'))),prop('ORDER','tags',wrap('set',scalar())),prop('ORDER','choice',choice),prop('ORDER','status',named('status'))];
orderFields.push(prop('ORDER','customers',wrap('list',named('mapping-customer'))),prop('ORDER','money_set',wrap('set',named('money'))));
const summaryFields=[...orderFields.map(p=>({...p,ontology_property:'FIXTURE-SUMMARY#'+p.name})),prop('SUMMARY','repeated',scalar('UInt64')),prop('SUMMARY','amounts',wrap('list',scalar('UInt64'))),prop('SUMMARY','unique_amounts',wrap('set',scalar('UInt64'))),prop('SUMMARY','line_amounts',wrap('list',scalar('UInt64'))),prop('SUMMARY','unique_line_amounts',wrap('set',scalar('UInt64'))),prop('SUMMARY','unique_customers',wrap('set',named('mapping-customer'))),prop('SUMMARY','set_amounts',wrap('set',scalar('UInt64')))];
const v2=()=>({schema_version:'domainspec.typed-mapping/v2',ontology_mapping:'FIXTURE-MAPPING',inputs:[{name:'order',type:named('order')},{name:'order_total',type:scalar('UInt64')},{name:'memo',type:wrap('optional',scalar())},{name:'fallback',type:scalar()},{name:'amount_list',type:wrap('list',scalar('UInt64'))}],target:'alpha:summary',fields:[
 ...orderFields.map(p=>field(p.name,p.name==='amount'?value('order_total'):p.name==='memo'?value('memo'):p.name==='status'?{op:'variant',selector:'FIXTURE-STATUS#Ready'}:value('order',p.ontology_property),p.name==='memo'?value('fallback'):null)),
 field('repeated',value('order_total')),field('amounts',value('amount_list')),field('unique_amounts',{op:'to_set',value:value('amount_list')}),field('line_amounts',value('order','FIXTURE-ORDER#lines','FIXTURE-MONEY#amount')),field('unique_line_amounts',{op:'to_set',value:value('order','FIXTURE-ORDER#lines','FIXTURE-MONEY#amount')})
 ,field('unique_customers',{op:'to_set',value:value('order','FIXTURE-ORDER#customers')}),field('set_amounts',value('order','FIXTURE-ORDER#money_set','FIXTURE-MONEY#amount'))
],total:true});
function fixture(t:any){
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-configured-mapping-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
 const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
 const write=(name:string,v:any)=>{const f=path.join(source,name);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v));};
 const feature=read(path.join(source,'specs/alpha/feature.json'));
 const node=(id:string,kind:string,body:any)=>{feature.nodes.push(id);write('specs/alpha/nodes/'+id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id:id,kind,body:{description:id,...(kind==='Entity'||kind==='Value Object'?{fields:body.typed_contract.properties.map((p:any)=>p.name)}:kind==='Enum'?{values:body.typed_contract.variants.map((v:any)=>v.name)}:kind==='Rule'?{predicate:'structured:domainspec.typed-rule/v1'}:{}),...body}});};
 const record=(id:string,kind:string,properties:any[])=>node(id,kind,{...(kind==='Value Object'?{invariant_refs:['alpha:valid-mapping-value']}:{}),typed_contract:{schema_version:'domainspec.typed-record/v1',ontology_node:'FIXTURE-'+id.toUpperCase(),properties}});
 node('valid-mapping-value','Rule',{typed_contract:{schema_version:'domainspec.typed-rule/v1',ontology_rule:'FIXTURE-VALID-MAPPING',parameters:[{name:'amount',type:scalar('UInt64')}],expression:{op:'eq',left:{op:'literal',type:'Bool',value:false},right:{op:'literal',type:'Bool',value:true}}}});
 record('money','Value Object',[prop('MONEY','amount',scalar('UInt64')),prop('MONEY','currency',scalar())]);
 record('mapping-customer','Entity',[prop('CUSTOMER','id',scalar(),true),prop('CUSTOMER','label',scalar())]);
 node('status','Enum',{typed_contract:{schema_version:'domainspec.typed-sum/v1',ontology_node:'FIXTURE-STATUS',variants:[{name:'Ready',ontology_variant:'FIXTURE-STATUS#Ready',payload:null},{name:'Draft',ontology_variant:'FIXTURE-STATUS#Draft',payload:null}]}});
 record('order','Entity',orderFields);record('summary','Entity',summaryFields);
 const full=v2(),partial={...v2(),ontology_mapping:'FIXTURE-PARTIAL',fields:[field('memo',value('memo'))],total:false};
 const zero={...v2(),ontology_mapping:'FIXTURE-CONSTANT',inputs:[],fields:[field('id',lit('String','constant')),field('amount',lit('UInt64','18446744073709551615'))],total:false};
 const legacy={schema_version:'domainspec.typed-mapping/v1',ontology_mapping:'FIXTURE-LEGACY',source:'alpha:order',target:'alpha:summary',fields:[{target:'id',source:'id',default:null},{target:'amount',source:'amount',default:null},{target:'memo',source:'memo',default:{type:'String',value:'absent-only'}}],total:false};
 const legacyPartial={...legacy,ontology_mapping:'FIXTURE-LEGACY-PARTIAL',fields:[{target:'memo',source:'memo',default:null}]};
 const contracts:any={full,partial,zero,legacy,'legacy-partial':legacyPartial,'legacy-total':{...legacy,target:'alpha:order',total:true,fields:orderFields.map(p=>({target:p.name,source:p.name,default:null}))}};
 for(const [id,c]of Object.entries(contracts) as [string,any][]){
  node('map-'+id,'Mapping',{target:c.target,...(c.schema_version.endsWith('/v1')?{source:c.source}:{}),typed_contract:c});
  const edge_id='map-'+id+'-maps-summary';feature.edges.push(edge_id);write('specs/alpha/edges/'+edge_id+'.json',{schema_version:'domainspec.edge/v1',feature_id:'alpha',edge_id,relationship:'maps',source_node_id:'map-'+id,target_node_id:c.target.split(':')[1],scope:'feature'});
 }
 write('specs/alpha/feature.json',feature);
 const compile=()=>{
  const graph=loadCompiledProjectGraph(source),graph_sha256=createCompiledProjectCertificate(graph).graph_sha256;
  const boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256,graph_sha256},boundaryContract);
  const fields=compileSelectedProjectFields(graph,{schema_version:EXACT_PROJECT_FIELD_SELECTION_VERSION,contract_sha256:EXACT_FIELD_CONTRACT_SHA256,graph_sha256,roots:['alpha:order','alpha:summary'],bindings:[]},fieldContract);
  const selection:any={schema_version:PYTHON_MAPPING_VERSION,language:'python',boundary_sha256:boundary.boundary_sha256,field_compilation_sha256:fields.compilation_sha256,module_root:'commerce',roots:Object.keys(contracts).map(id=>'alpha:map-'+id)};
  return {graph,boundary,fields,selection,plan:()=>planConfiguredPythonMappings(boundary,fields,selection,sources)};
 };
 return {temp,source,write,contracts,compile,...compile()};
}

type Plan = ReturnType<typeof planConfiguredPythonMappings>;
function materialize(root:string,p:Plan){for(const a of p.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}}
function payload(root:string,p:Plan,f:ReturnType<typeof fixture>){return {root,modules:p.modules,files:p.artifacts.map(a=>a.relative_path),contracts:Object.fromEntries(Object.entries(f.contracts).map(([k,v])=>['alpha:map-'+k,v])),model:f.fields.model,runtime_dir:path.posix.dirname(p.artifacts.find(a=>a.relative_path.endsWith('/runtime/facts.py'))!.relative_path)};}
const observer=path.join(project,'impl/cli/src/verification/python-mapping-observer.py');
const nativeScript=String.raw`
import copy, dataclasses, importlib, json, os, pathlib, sys, typing
data=json.load(sys.stdin);sys.path.insert(0,data['root']);f={}
def thaw(v):
    if dataclasses.is_dataclass(v) and hasattr(v,'entries'):return {k:thaw(x) for k,x in v.entries}
    if type(v) is tuple:return [thaw(x) for x in v]
    if hasattr(v,'items'):return {k:thaw(x) for k,x in v.items()}
    return v
for m in data['modules']:
    fn=getattr(importlib.import_module(m['import_name']),m['callable']);f[m['selector'].split('map-',1)[1]]=fn
    assert thaw(fn.descriptor)==m['descriptor']
    hints=typing.get_type_hints(fn.__call__);shape=hints['return']
    methods=typing.get_overloads(shape.__getitem__) or [shape.__getitem__]
    fields={typing.get_args(typing.get_type_hints(x)['key'])[0]:typing.get_type_hints(x)['return'] for x in methods}
    assert list(fields)==[v['name'] for v in m['descriptor']['target']['fields']]
    assert set(typing.get_type_hints(hints['parameters']))=={p['name'] for p in m['descriptor']['inputs']}
    if 'amount' in fields:assert fields['amount'] is int
    if 'enabled' in fields:assert fields['enabled'] is bool
    if 'line_amounts' in fields:assert fields['line_amounts']==tuple[int,...]
    for action in [lambda:setattr(fn,'descriptor',{}),lambda:fn.descriptor.__setitem__('total',False),lambda:fn.descriptor['target'].__setitem__('selector','foreign')]:
        try:action()
        except (TypeError,AttributeError):pass
        else:raise AssertionError('MUTABLE_BINDING')
money=lambda amount=4:{'amount':amount,'currency':'GBP'}
def order():return {'id':'order-1','amount':9,'enabled':True,'money':money(),'customer':{'id':'customer','label':'first'},'customers':[{'id':'same','label':'first'},{'id':'same','label':'second'}],'money_set':[money(2),{'amount':2,'currency':'USD'},money(1)],'lines':[money(2),money(2),money(1)],'tags':['z','a'],'choice':{'variant':'Money','payload':money('18446744073709551615')},'status':{'variant':'Draft'}}
def args():return {'order':order(),'order_total':'18446744073709551615','memo':None,'fallback':'fallback','amount_list':['9007199254740993',2,2]}
def error(fn,p,expected='MAPPING_INPUT'):
    try:fn(p)
    except TypeError as e:assert str(e)==expected,str(e)
    else:raise AssertionError('EXPECTED_'+expected)
events=[];armed=False
def audit(event,args):
    if armed and (event in ('open','exec','compile','import') or event.startswith(('os.','socket.','subprocess.'))):events.append(event)
sys.addaudithook(audit);armed=True
original=args();before=copy.deepcopy(original);out=f['full'](original)
assert original==before
assert out['amount']==out['repeated']==18446744073709551615
# Canonical length-prefixed keys sort lexically, not numerically: '16:' precedes '1:'.
assert out['amounts']==(9007199254740993,2,2) and out['unique_amounts']==(9007199254740993,2)
assert len(out['unique_customers'])==1 and out['unique_customers'][0]['label']=='first'
assert out['set_amounts']==(1,2)
assert out['line_amounts']==(2,2,1) and out['unique_line_amounts']==(1,2)
assert out['status']['variant']=='Ready' and out['memo']=='fallback'
assert out['tags']==('a','z') and out['enabled'] is True
assert out['choice']['payload']['amount']==18446744073709551615
original['order']['money']['amount']=99;original['order']['lines'][0]['amount']=99
assert out['money']['amount']==4 and out['lines'][0]['amount']==2
for x in [out,out['money'],out['customer'],out['choice'],out['choice']['payload']]:
    try:x.entries=()
    except (TypeError,AttributeError):pass
    else:raise AssertionError('MUTABLE_RESULT')
assert f['full']({**args(),'memo':''})['memo']==''
assert f['full']({**args(),'order_total':0})['amount']==0
assert thaw(f['partial'](args()))=={'memo':None}
assert thaw(f['zero']({}))=={'id':'constant','amount':18446744073709551615}
assert f['legacy']({'source':order()})['memo']=='absent-only'
assert f['legacy']({'source':{**order(),'memo':None}})['memo'] is None
assert thaw(f['legacy-partial']({'source':order()}))=={}
assert thaw(f['legacy-partial']({'source':{**order(),'memo':None}}))=={'memo':None}
error(f['legacy-total'],{'source':order()},'MAPPING_REQUIRED_VALUE')
assert f['legacy-total']({'source':{**order(),'memo':None}})['memo'] is None
for v in [True,1.0,-1,'01','+1','1\n','18446744073709551616',{},None]:error(f['full'],{**args(),'order_total':v})
for p in [None,[],{},dict(args(),extra=1)]:error(f['full'],p)
p=args();del p['memo'];error(f['full'],p)
# Normalize every declared input even if a partial projection never reads it.
error(f['partial'],{**args(),'order_total':True})
error(f['partial'],{**args(),'order':{**order(),'money':{'amount':True,'currency':'GBP'}}})
for patch in [{'tags':['a','a']},{'enabled':1},{'status':{'variant':'Unknown'}},{'choice':{'variant':'None','payload':None}},{'memo':1},{'unknown':1}]:error(f['full'],{**args(),'order':{**order(),**patch}})
for choice in [{'variant':'None'},{'variant':'Amount','payload':0},{'variant':'Money','payload':money(0)}]:assert f['full']({**args(),'order':{**order(),'choice':choice}})['choice']['variant']==choice['variant']
assert f['full']({**args(),'memo':'\ud83d\ude00'})['memo']=='😀'
assert f['full']({**args(),'memo':'e\u0301'})['memo']!='é'
calls=[]
class ActiveDict(dict):
    def __getitem__(self,k):calls.append('get');return super().__getitem__(k)
class ActiveInt(int):
    def __int__(self):calls.append('int');return 0
class ActiveList(list):
    def __iter__(self):calls.append('iterate');return super().__iter__()
error(f['full'],ActiveDict(args()));error(f['full'],{**args(),'order':ActiveDict(order())})
error(f['full'],{**args(),'order_total':ActiveInt(1)});error(f['full'],{**args(),'amount_list':ActiveList([1])})
assert calls==[],calls
result=thaw(out);armed=False
assert events==[],events
for file in data['files']:compile(pathlib.Path(data['root'],file).read_bytes(),file,'exec')
print(json.dumps({'pid':os.getpid(),'result':result,'effects':events,'mappings':len(f)}))
`;

test('R10 Python Mapping planning binds profiles and same-graph fields deterministically',t=>{
 const f=fixture(t),p=f.plan();assert.equal(p.modules.length,6);assert.deepEqual(f.plan(),p);
 assert.deepEqual(planConfiguredPythonMappings(f.boundary,f.fields,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
 const alternate=planConfiguredPythonMappings(f.boundary,f.fields,{...f.selection,module_root:'relocated/nested'},sources);
 assert.deepEqual(alternate.artifacts.filter(a=>a.content).map(a=>a.content),p.artifacts.filter(a=>a.content).map(a=>a.content));
 const subset=planConfiguredPythonMappings(f.boundary,f.fields,{...f.selection,roots:['alpha:map-full']},sources);
 for(const a of subset.artifacts)assert.equal(a.content,p.artifacts.find(b=>a.relative_path===b.relative_path)!.content);
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
 for(const m of p.modules){const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));assert.ok(Object.isFrozen(d.target.fields));}
 fs.renameSync(f.source,path.join(f.temp,'gone'));assert.deepEqual(f.plan(),p);
});

test('R10 Python Mapping planner rejects active, stale and incompatible selections',t=>{
 const f=fixture(t);
 for(const patch of [{schema_version:'future'},{language:'rust'},{boundary_sha256:'stale'},{field_compilation_sha256:'stale'},{module_root:'../escape'},{module_root:'typing'},{roots:[]},{roots:['alpha:map-full','alpha:map-full']},{roots:['alpha:order']},{extra:true}])assert.throws(()=>planConfiguredPythonMappings(f.boundary,f.fields,{...f.selection,...patch},sources));
 assert.throws(()=>planConfiguredPythonMappings(structuredClone(f.boundary),f.fields,f.selection,sources));assert.throws(()=>planConfiguredPythonMappings(f.boundary,structuredClone(f.fields),f.selection,sources));
 for(const k of Object.keys(sources))assert.throws(()=>planConfiguredPythonMappings(f.boundary,f.fields,f.selection,{...sources,[k]:sources[k as keyof typeof sources]+' '}),/source drift/);
 let reads=0;assert.throws(()=>planConfiguredPythonMappings(f.boundary,f.fields,{...f.selection,get roots(){reads++;return [];}},sources));assert.equal(reads,0);
 const file='specs/alpha/nodes/map-full.json',original=read(path.join(f.source,file));
 for(const bad of [field('amount',value('memo')),field('memo',value('memo','unknown')),field('amount',value('order_total'),lit('UInt64','1'))]){
  const changed=structuredClone(original);changed.body.typed_contract.fields[0]=bad;f.write(file,changed);assert.throws(()=>f.compile().plan());
 }
 f.write(file,original);
 const changed=structuredClone(original);changed.body.typed_contract.ontology_mapping='FIXTURE-CHANGED';f.write(file,changed);const next=f.compile();
 assert.throws(()=>planConfiguredPythonMappings(f.boundary,next.fields,{...f.selection,field_compilation_sha256:next.fields.compilation_sha256},sources),/cross-graph/);
});

test('R10 Python Mappings execute immutable projections and distinct v1/v2 default semantics',t=>{
 const f=fixture(t),results:any[]=[];
 for(const module_root of ['commerce','relocated/nested']){
  const p=planConfiguredPythonMappings(f.boundary,f.fields,{...f.selection,module_root},sources),root=path.join(f.temp,module_root);materialize(root,p);const input=JSON.stringify(payload(root,p,f));
  results.push(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B','-c',nativeScript],{input,encoding:'utf8'})));
  assert.deepEqual(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B',observer],{input,encoding:'utf8'})),{observed:6});
 }
 assert.notEqual(results[0].pid,results[1].pid);assert.deepEqual(results[0].result,results[1].result);
});

test('R10 independent Mapping observation rejects compiling semantic and effect mutants',t=>{
 const f=fixture(t),p=f.plan(),root=path.join(f.temp,'mutants');materialize(root,p);
 const m=p.modules.find(m=>m.selector==='alpha:map-full')!,file=path.join(root,m.provider_path),original=bytes(file);
 const mutants=[original.replace('if v3 is None:','if not v3:'),original.replace('v1 = p1','v1 = 0'),original.replace('keyed.setdefault(element.key(item), item)','keyed[element.key(item)] = item'),original.replace('return _cast(', 'globals()["write"] = 1\n    return _cast('),original.replace('return _cast(', 'parameters["write"] = 1\n    del parameters["write"]\n    return _cast('),original.replace('return _cast(', 'yield _cast(')];
 for(const mutant of mutants){
  assert.notEqual(mutant,original);fs.writeFileSync(file,mutant);execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:mutant});
  const changed:any=structuredClone(m);changed.descriptor.provider.sha256=sha256(mutant);
  const result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...payload(root,p,f),modules:[changed]}),encoding:'utf8'});
  assert.notEqual(result.status,0);assert.match(result.stderr,/semantics or effects/);
 }
 fs.writeFileSync(file,original);
 const facadeFile=path.join(root,m.relative_path),facade=bytes(facadeFile);
 fs.writeFileSync(facadeFile,facade.replace('frozen=True','frozen=False'));
 let result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...payload(root,p,f),modules:[m]}),encoding:'utf8'});assert.notEqual(result.status,0);assert.match(result.stderr,/frozen provider binding/);
 fs.writeFileSync(facadeFile,facade);
 const data=payload(root,p,f),supportFile=path.join(root,data.runtime_dir,'values.py'),support=bytes(supportFile),mutant=support.replace('if type(value) is not bool:','if type(value) not in (bool, int):');assert.notEqual(mutant,support);fs.writeFileSync(supportFile,mutant);
 const changed:any=structuredClone(m);changed.descriptor.runtime.find((r:any)=>r.id==='values.py').sha256=sha256(mutant);
 result=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...data,modules:[changed]}),encoding:'utf8'});assert.notEqual(result.status,0);assert.match(result.stderr,/support perimeter/);
});
