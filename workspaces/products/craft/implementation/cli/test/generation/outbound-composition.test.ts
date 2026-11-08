import test from 'node:test';
import assert from 'node:assert/strict';
import {compileOutboundComposition,OUTBOUND_COMPOSITION_PROFILE} from '../../src/typed-backend/outbound-composition.js';
const id={type:'identifier',max:128};
const input={type:{id,version:id,model:id,policy:id,stream:{type:'boolean'}}};
const reply={type:{reply:{type:'string',max:64}}};
const fixture=()=>({schema_version:OUTBOUND_COMPOSITION_PROFILE,input,modules:{Prepare:{input,output:input},Decode:{input:reply,output:reply}},limits:{deadline_ms:100,max_bytes:1024,max_concurrent:1,max_attempts:1},steps:[{id:'Prepared',kind:'local',module:'Prepare',args:'input',error:'INVALID_INPUT'},{id:'Bound',kind:'binding',binding_id:'Prepared.id',version:'Prepared.version',model:'Prepared.model',policy:'Prepared.policy'},{id:'Exchange',kind:'http',binding:'Bound',body:'Prepared',omit:['policy'],output:'Decode.input',stream:'Prepared.stream',identity:{request_id:'Prepared.id',model:'Bound.model'}},{id:'Done',kind:'local',module:'Decode',args:'Exchange',error:'INVALID_RESPONSE'}],output:'Done'});
test('normalized contract is deterministic, copied, and contains typed stage trace',()=>{const f=fixture(),a=compileOutboundComposition(f),b=compileOutboundComposition(f);assert.deepEqual(a,b);f.steps[0]!.error='CHANGED';assert.equal(a.contract.steps[0]!.error,'INVALID_INPUT');assert.deepEqual(a.output,reply);assert.equal(a.trace.steps.length,4);});
test('unknown effects, retry, unbounded limits, missing/forward references and type mismatches reject',()=>{
 const mutations=[(c:any)=>c.limits.max_attempts=2,(c:any)=>c.limits.deadline_ms=5001,(c:any)=>c.steps[2].url='https://example.test',(c:any)=>c.steps[2].binding='input',(c:any)=>c.steps[0].args='Done',(c:any)=>c.steps[0].args={id:'input.stream'},(c:any)=>c.steps[2].stream='input.id',(c:any)=>c.steps.push({...c.steps[2],id:'Again'}),(c:any)=>c.steps[1].id='constructor',(c:any)=>c.output='Exchange.missing',(c:any)=>c.steps[2].omit=['missing'],(c:any)=>c.steps[0].extra=true,(c:any)=>c.steps[3].args='Prepared',(c:any)=>c.steps[3].module='Prepare',(c:any)=>c.modules.Prepare.input={type:{id:{type:'identifier',max:10}}}];
 for(const change of mutations){const c=fixture();change(c);assert.throws(()=>compileOutboundComposition(c),/DS_OUTBOUND/);}
});
test('optional object traversal and unsupported shape constraints reject',()=>{const c:any=fixture();c.input.optional=true;assert.throws(()=>compileOutboundComposition(c),/DS_OUTBOUND/);const d:any=fixture();d.input.type.id.extra='x';assert.throws(()=>compileOutboundComposition(d),/DS_OUTBOUND/);});
