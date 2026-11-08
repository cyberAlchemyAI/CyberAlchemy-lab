import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync,spawnSync} from 'node:child_process';
import test from 'node:test';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary,COMPOSITION_BOUNDARY_VERSION,COMPOSITION_BOUNDARY_CONTRACT_SHA256} from '../../src/input/composition-boundary.ts';
import {planConfiguredPythonEvents,PYTHON_EVENT_VERSION} from '../../src/generation/configured-python-events.ts';
import {EVENT_VALUE_PROFILE} from '../../src/generation/configured-events.ts';
import {planCompiledProjectBuild} from '../../src/generation/project-build.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';

const project=path.resolve(import.meta.dirname,'../../../..'),pkg=path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation');
const bytes=(p:string)=>fs.readFileSync(p,'utf8'),read=(p:string)=>JSON.parse(bytes(p));
const sources={configuration:bytes(path.join(pkg,'configuration.json')),base:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json')),
  python:bytes(path.join(project,'development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json')),event_contract:bytes(path.join(pkg,'event-generation-contract.json'))};
const boundaryContract=bytes(path.join(project,'development/reconciliation-v1/contracts/composition-boundary.json'));
const field=(field_id:string,name:string,required=true)=>({field_id,type_ref:{kind:'primitive',name},required});
const reference=(field_id:string,selector:string)=>({field_id,type_ref:{kind:'reference',selector},required:true});
function fixture(t:any){
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ds-events-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const source=path.join(temp,'source');fs.cpSync(path.join(project,'impl/cli/fixtures/input-roots/canonical-project'),source,{recursive:true});
  const write=(p:string,v:any)=>{const f=path.join(source,p);fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,JSON.stringify(v,null,2)+'\n');};
  const feature=read(path.join(source,'specs/alpha/feature.json'));
  const node=(node_id:string,kind:string,body:any)=>{feature.nodes.push(node_id);write('specs/alpha/nodes/'+node_id+'.json',{schema_version:'domainspec.node/v1',feature_id:'alpha',node_id,kind,body});};
  node('valid-currency','Rule',{description:'Currency rule',predicate:'currency is valid'});
  node('currency','Value Object',{description:'Currency',fields:[field('code','string')],invariant_refs:['alpha:valid-currency']});
  node('status','Enum',{description:'Status',values:['ready','closed']});
  const bodies:any={};
  for(const [id,policy] of [['settled','required'],['clocked','generated'],['empty','required']]){
    const body={description:'An occurrence, not a database write',event_type:id,version:'2',occurrence_id:field('occurrence-id','uuid'),occurred_at_policy:policy,
      payload:id==='empty'?[]:[field('amount','integer'),field('ratio','decimal'),field('enabled','boolean'),field('label','string'),field('timestamp','timestamp'),field('uuid','uuid'),field('note','string',false),reference('entity','alpha:customer'),reference('value','alpha:currency'),reference('status','alpha:status'),reference('previous','alpha:'+id)]};
    bodies['alpha:'+id]=body;node(id!,'Event',body);
  }
  write('specs/alpha/feature.json',feature);
  const graph=loadCompiledProjectGraph(source),boundary=compileCompositionBoundary(graph,{schema_version:COMPOSITION_BOUNDARY_VERSION,graph_sha256:createCompiledProjectCertificate(graph).graph_sha256,contract_sha256:COMPOSITION_BOUNDARY_CONTRACT_SHA256},boundaryContract);
  const selection:any={schema_version:PYTHON_EVENT_VERSION,language:'python',value_profile:EVENT_VALUE_PROFILE,boundary_sha256:boundary.boundary_sha256,module_root:'application',roots:Object.keys(bodies)};
  return {temp,source,write,bodies,graph,boundary,selection,plan:()=>planConfiguredPythonEvents(graph,boundary,selection,sources)};
}

type Plan=ReturnType<typeof planConfiguredPythonEvents>;
function materialize(root:string,p:Plan){for(const a of p.artifacts){const file=path.join(root,a.relative_path);fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,a.content);}}
function payload(root:string,p:Plan,f:ReturnType<typeof fixture>){return {root,modules:p.modules,files:p.artifacts.map(a=>a.relative_path),bodies:f.bodies,nodes:Object.fromEntries(f.graph.nodes.map(n=>[n.selector,{kind:n.kind,body:n.body}])),runtime:p.artifacts.find(a=>a.relative_path.endsWith('/runtime/event_values.py'))!.relative_path};}
const observer=path.join(project,'impl/cli/test/generation/python-event-observer.py');
const nativeScript=String.raw`
import copy, dataclasses, importlib, inspect, json, math, os, pathlib, sys, typing
data=json.load(sys.stdin);sys.path.insert(0,data['root']);f={};reference_types={}
def thaw(v):
    if dataclasses.is_dataclass(v):return {field.name:thaw(getattr(v,field.name)) for field in dataclasses.fields(v)}
    if type(v) is tuple:return [thaw(x) for x in v]
    if hasattr(v,'items'):return {k:thaw(x) for k,x in v.items()}
    return v
def members(shape):
    if not hasattr(shape,'__getitem__'):return {}
    methods=typing.get_overloads(shape.__getitem__) or [shape.__getitem__]
    return {typing.get_args(typing.get_type_hints(m)['key'])[0]:typing.get_type_hints(m)['return'] for m in methods}
for m in data['modules']:
    module=importlib.import_module(m['import_name']);fn=getattr(module,m['callable']);f[m['selector'].split(':')[1]]=fn
    assert thaw(fn.descriptor)==m['descriptor']
    source=data['bodies'][m['selector']];generated=source['occurred_at_policy']=='generated'
    sig=inspect.signature(fn);assert list(sig.parameters)==(['input','clock'] if generated else ['input'])
    hints=typing.get_type_hints(fn.__call__);shape=typing.get_type_hints(hints['return'])
    assert typing.get_args(shape['type'])==(source['event_type'],) and typing.get_args(shape['version'])==(source['version'],)
    fields=members(shape['payload']);assert list(fields)==sorted(x['field_id'] for x in source['payload'])
    for field in source['payload']:
        t=fields[field['field_id']];ref=field['type_ref']
        if ref['kind']=='reference':
            assert t.__supertype__ is str and t.__name__==ref['selector']
            if ref['selector'] in reference_types:assert reference_types[ref['selector']] is t,'SAME_SELECTOR_TYPE_IDENTITY'
            reference_types[ref['selector']]=t
        else:assert t is {'string':str,'boolean':bool,'integer':int,'decimal':float,'timestamp':str,'uuid':str}[ref['name']]
    input_type=typing.get_type_hints(hints['input']);assert set(input_type)==({'occurrence','payload'} if generated else {'occurrence','occurredAt','payload'})
    for action in [lambda:setattr(fn,'descriptor',{}),lambda:fn.descriptor.__setitem__('publication',True),lambda:fn.descriptor['occurrence_id'].__setitem__('required',False)]:
        try:action()
        except (TypeError,AttributeError):pass
        else:raise AssertionError('MUTABLE_BINDING')
def input(amount=1):return {'occurrence':{'occurrence-id':'occurrence-1'},'occurredAt':'supplied-time','payload':{'amount':amount,'ratio':0.25,'enabled':True,'label':'','timestamp':'source-time','uuid':'source-id','entity':'customer-1','value':'currency-1','status':'ready','previous':'previous-occurrence'}}
def reject(call):
    try:call()
    except TypeError as e:assert str(e)=='EVENT_INPUT',str(e)
    else:raise AssertionError('EVENT_INPUT_MISSING')
events=[];armed=False
def audit(event,args):
    if armed and (event in ('open','exec','compile','import') or event.startswith(('os.','socket.','subprocess.'))):events.append(event)
sys.addaudithook(audit);armed=True
make=f['settled'];original=input('9223372036854775807');before=copy.deepcopy(original);event=make(original)
assert original==before and event.payload['amount']==9223372036854775807
for n in [-9223372036854775808,9223372036854775807,-9007199254740993,9007199254740993,0,-1,1]:
    assert make(input(n)).payload['amount']==n and make(input(str(n))).payload['amount']==n
assert event.type=='settled' and event.version=='2' and event.occurredAt=='supplied-time'
assert event.occurrence['occurrence-id']=='occurrence-1' and 'note' not in event.payload
original['occurrence']['occurrence-id']='changed';original['payload']['entity']='changed'
assert event.occurrence['occurrence-id']=='occurrence-1' and event.payload['entity']=='customer-1'
for action in [lambda:setattr(event,'version','9'),lambda:event.payload.__setitem__('amount',0),lambda:event.occurrence.__setitem__('occurrence-id','x')]:
    try:action()
    except (TypeError,AttributeError):pass
    else:raise AssertionError('MUTABLE_EVENT')
different=make({**input(),'occurrence':{'occurrence-id':'occurrence-2'}})
assert different.payload==make(input()).payload and different.occurrence!=make(input()).occurrence
same=make({**input(),'payload':{**input()['payload'],'label':'different'}})
assert same.occurrence==make(input()).occurrence and same.payload['label']=='different'
for note in ['','present']:assert make({**input(),'payload':{**input()['payload'],'note':note}}).payload['note']==note
for ratio in [0,-0.0,1,0.25,1e308,5e-324]:
    out=make({**input(),'payload':{**input()['payload'],'ratio':ratio}}).payload['ratio'];assert type(out) is float and out==float(ratio)
    if ratio==0:assert math.copysign(1,out)==1
assert make({**input(),'payload':{**input()['payload'],'enabled':False}}).payload['enabled'] is False
assert dict(f['empty']({'occurrence':{'occurrence-id':'empty'},'occurredAt':'time','payload':{}}).payload)=={}
# String carriers remain raw; no Unicode or timestamp/UUID format inference.
for text in ['\ud83d\ude00','e\u0301','not-a-timestamp']:
    assert make({**input(),'payload':{**input()['payload'],'label':text,'timestamp':text,'uuid':text}}).payload['label']==text
for amount in [-9223372036854775809,9223372036854775808,1.0,1.5,True,'-0','01','+1','1\n',' 1','1.0','９',None,{}]:reject(lambda:make(input(amount)))
for patch in [{'ratio':float('nan')},{'ratio':float('inf')},{'ratio':10**10000},{'ratio':True},{'enabled':1},{'label':1},{'timestamp':''},{'uuid':''},{'entity':{}},{'note':None},{'extra':1}]:reject(lambda:make({**input(),'payload':{**input()['payload'],**patch}}))
for obj in [None,[],{},dict(input(),extra=1),{**input(),'occurrence':{}},{**input(),'occurredAt':''}]:reject(lambda:make(obj))
calls=[]
class ActiveDict(dict):
    def __getitem__(self,key):calls.append('get');return super().__getitem__(key)
class ActiveInt(int):
    def __int__(self):calls.append('int');return 0
class ActiveStr(str):
    def __eq__(self,other):calls.append('eq');return True
    def __hash__(self):return str.__hash__(self)
reject(lambda:make(ActiveDict(input())));reject(lambda:make({**input(),'payload':ActiveDict(input()['payload'])}));reject(lambda:make(input(ActiveInt(1))));reject(lambda:make(input(ActiveStr('1'))))
assert calls==[]
hostile={ActiveStr('payload'):input()['payload'],'occurrence':input()['occurrence'],'occurredAt':'x'};calls.clear();reject(lambda:make(hostile));assert calls==[]
facts=input();del facts['occurredAt'];clocks=[]
def clock():clocks.append('tick');return 'explicit-time'
out=f['clocked'](facts,clock);assert clocks==['tick'] and out.occurredAt=='explicit-time'
reject(lambda:f['clocked'](input(),clock));reject(lambda:f['clocked']({**facts,'payload':{**facts['payload'],'amount':'bad'}},clock));assert clocks==['tick']
for value in ['',None,{},1,False]:reject(lambda:f['clocked'](facts,lambda:value))
reject(lambda:f['clocked'](facts,None))
sentinel=RuntimeError('CLOCK_FAILED')
def broken():raise sentinel
try:f['clocked'](facts,broken)
except RuntimeError as e:assert e is sentinel
else:raise AssertionError('SWALLOWED_CLOCK_ERROR')
# Copy normalization completes before the explicit clock can mutate caller data.
def mutating_clock():facts['payload']['amount']=99;facts['occurrence']['occurrence-id']='changed';return 'after-copy'
out=f['clocked'](facts,mutating_clock);assert out.payload['amount']==1 and out.occurrence['occurrence-id']=='occurrence-1'
result=thaw(event);armed=False;assert events==[],events
for file in data['files']:compile(pathlib.Path(data['root'],file).read_bytes(),file,'exec')
print(json.dumps({'pid':os.getpid(),'event':result,'effects':events}))
`;

test('R10 Python Event planner binds source/reference identities and leaves legacy generation unchanged',t=>{
 const f=fixture(t),p=f.plan(),legacy=planCompiledProjectBuild(f.graph,'python');assert.equal(p.modules.length,3);assert.deepEqual(f.plan(),p);
 assert.deepEqual(planConfiguredPythonEvents(f.graph,f.boundary,{...f.selection,roots:[...f.selection.roots].reverse()},sources),p);
 const alternate=planConfiguredPythonEvents(f.graph,f.boundary,{...f.selection,module_root:'relocated/nested'},sources);assert.deepEqual(alternate.artifacts.filter(a=>a.content).map(a=>a.content),p.artifacts.filter(a=>a.content).map(a=>a.content));
 const subset=planConfiguredPythonEvents(f.graph,f.boundary,{...f.selection,roots:['alpha:settled']},sources);for(const a of subset.artifacts)assert.equal(a.content,p.artifacts.find(b=>b.relative_path===a.relative_path)!.content);
 const {plan_sha256,...body}=p;assert.equal(plan_sha256,sha256(canonicalJson(body)));
 for(const m of p.modules){const {descriptor_sha256,...d}=m.descriptor;assert.equal(descriptor_sha256,sha256(canonicalJson(d)));assert.ok(Object.isFrozen(d.payload));assert.equal(d.publication,false);assert.equal(d.occurrence_registration,false);}
 assert.deepEqual(p.modules.find(m=>m.selector==='alpha:settled')!.descriptor.references.map(r=>r.kind).sort(),['Entity','Enum','Event','Value Object']);
 assert.deepEqual(planCompiledProjectBuild(f.graph,'python'),legacy);fs.renameSync(f.source,path.join(f.temp,'gone'));assert.deepEqual(f.plan(),p);
});

test('R10 Python Event rejects stale graph and profiles, hostile selections and implicit widening',t=>{
 const f=fixture(t);
 for(const patch of [{schema_version:'future'},{language:'typescript'},{value_profile:'float'},{module_root:'../escape'},{module_root:'re'},{module_root:'a//b'},{roots:[]},{roots:['alpha:settled','alpha:settled']},{roots:['alpha:customer']},{boundary_sha256:'stale'},{ignore_errors:true}])assert.throws(()=>planConfiguredPythonEvents(f.graph,f.boundary,{...f.selection,...patch},sources));
 for(const k of Object.keys(sources))assert.throws(()=>planConfiguredPythonEvents(f.graph,f.boundary,f.selection,{...sources,[k]:sources[k as keyof typeof sources]+' '}),/source drift/);
 assert.throws(()=>planConfiguredPythonEvents(structuredClone(f.graph),f.boundary,f.selection,sources));assert.throws(()=>planConfiguredPythonEvents(f.graph,structuredClone(f.boundary),f.selection,sources));
 const other=fixture(t);other.bodies['alpha:settled'].version='3';other.write('specs/alpha/nodes/settled.json',{schema_version:'domainspec.node/v1',node_id:'settled',feature_id:'alpha',kind:'Event',body:other.bodies['alpha:settled']});assert.throws(()=>planConfiguredPythonEvents(loadCompiledProjectGraph(other.source),f.boundary,f.selection,sources),/cross-graph/);
 let reads=0;assert.throws(()=>planConfiguredPythonEvents(f.graph,f.boundary,{...f.selection,get module_root(){reads++;return 'bad';}},sources));const roots:any=[];Object.defineProperty(roots,0,{get(){reads++;return 'alpha:settled';},enumerable:true});assert.throws(()=>planConfiguredPythonEvents(f.graph,f.boundary,{...f.selection,roots},sources));assert.throws(()=>planConfiguredPythonEvents(f.graph,f.boundary,f.selection,{...sources,get event_contract(){reads++;return sources.event_contract;}}));assert.equal(reads,0);
});

test('R10 native Python Events preserve exact carriers, immutable occurrence data and explicit clock order',t=>{
 const f=fixture(t),results:any[]=[];
 for(const module_root of ['application','relocated/nested']){
  const p=planConfiguredPythonEvents(f.graph,f.boundary,{...f.selection,module_root},sources),root=path.join(f.temp,module_root);materialize(root,p);const input=JSON.stringify(payload(root,p,f));
  results.push(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B','-c',nativeScript],{input,encoding:'utf8'})));assert.deepEqual(JSON.parse(execFileSync('/usr/bin/python3',['-I','-B',observer],{input,encoding:'utf8'})),{observed:3});
 }
 assert.notEqual(results[0].pid,results[1].pid);assert.deepEqual(results[0].event,results[1].event);
});

test('R10 independent Python Event observer rejects compiling value, identity, clock and effect mutants',t=>{
 const f=fixture(t),p=f.plan(),root=path.join(f.temp,'mutants');materialize(root,p);const m=p.modules.find(m=>m.selector==='alpha:settled')!,file=path.join(root,m.provider_path),original=bytes(file);
 const mutants=[original.replace('_e.integer(p["amount"])','_e.integer(p["amount"]) + 1'),original.replace('_e.text(o["occurrence-id"])','_e.text(p["entity"])'),original.replace('return EventValue("settled", "2"','return EventValue("settled", "3"'),original.replace('    return EventValue(', '    globals()["write"] = 1\n    return EventValue('),original.replace('    return EventValue(', '    input["write"] = 1\n    del input["write"]\n    return EventValue('),original.replace('frozen=True','frozen=False')];
 function reject(module:any,mutant:string,reason:RegExp){execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:mutant});const r=spawnSync('/usr/bin/python3',['-I','-B',observer],{input:JSON.stringify({...payload(root,p,f),modules:[module]}),encoding:'utf8'});assert.notEqual(r.status,0);assert.match(r.stderr,reason);}
 for(const mutant of mutants){assert.notEqual(mutant,original);fs.writeFileSync(file,mutant);const changed:any=structuredClone(m);changed.descriptor.provider.sha256=sha256(mutant);reject(changed,mutant,/Event semantics or effects/);}fs.writeFileSync(file,original);
 const clocked=p.modules.find(m=>m.selector==='alpha:clocked')!,clockFile=path.join(root,clocked.provider_path),clockSource=bytes(clockFile),clockMutant=clockSource.replace('occurredAt = _e.text(clock())','clock()\n    occurredAt = _e.text(clock())');assert.notEqual(clockMutant,clockSource);fs.writeFileSync(clockFile,clockMutant);const changed:any=structuredClone(clocked);changed.descriptor.provider.sha256=sha256(clockMutant);reject(changed,clockMutant,/Event semantics or effects/);
 const facadeFile=path.join(root,m.relative_path),facade=bytes(facadeFile);for(const mutant of [facade.replace('frozen=True','frozen=False'),facade.replace('"publication": False','"publication": True')]){assert.notEqual(mutant,facade);fs.writeFileSync(facadeFile,mutant);reject(m,mutant,/frozen provider binding|descriptor binding/);}fs.writeFileSync(facadeFile,facade);
 const supportFile=path.join(root,payload(root,p,f).runtime),support=bytes(supportFile),supportMutant=support.replace('type(value) is not bool','type(value) not in (bool, int)');assert.notEqual(supportMutant,support);fs.writeFileSync(supportFile,supportMutant);const altered:any=structuredClone(m);altered.descriptor.runtime.sha256=sha256(supportMutant);reject(altered,supportMutant,/support perimeter/);fs.writeFileSync(supportFile,support);
 const reference=clocked.reference_imports.find(r=>r.selector==='alpha:customer')!,index=clocked.reference_imports.indexOf(reference);
 const localType=clockSource.replace('from '+reference.module+' import EventRef as _Ref'+index,'from typing import NewType as _NewType\n_Ref'+index+' = _NewType("alpha:customer", str)');assert.notEqual(localType,clockSource);fs.writeFileSync(clockFile,localType);
 execFileSync('/usr/bin/python3',['-I','-B','-c','import sys;compile(sys.stdin.read(),"mutant.py","exec")'],{input:localType});
 const split:any=structuredClone(clocked);split.descriptor.provider.sha256=sha256(localType);reject(split,localType,/Event semantics or effects/);
 const result=spawnSync('/usr/bin/python3',['-I','-B','-c',nativeScript],{input:JSON.stringify(payload(root,p,f)),encoding:'utf8'});assert.notEqual(result.status,0);assert.match(result.stderr,/SAME_SELECTOR_TYPE_IDENTITY/);
});
