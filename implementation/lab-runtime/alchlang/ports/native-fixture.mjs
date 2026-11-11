// Explicit qualification adapter; the selected Python owner verifies all native effects.
import {readFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'..');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function capabilitySha(){
 const files=['native-source.json','ports/native-fixture.mjs','ports/native-fixture.py','ports/creation.py','evaluate-creation.mjs','creation-source.alch','shared-records/contracts/bounds.json','../../artifact-runtime/compile-source-operation.mjs','../../artifact-runtime/pure-operation.mjs'];
 return sha(JSON.stringify(Object.fromEntries(files.map(name=>[name,sha(readFileSync(path.join(root,name)))]))));
}
export function nativeCall(fixture,operation,values={}){
 const child=spawnSync('python3',['-B',path.join(root,'ports/native-fixture.py')],{input:JSON.stringify({fixture,operation,...values}),encoding:'utf8',maxBuffer:16*1024*1024,timeout:operation==='artifact-type-checks'?300000:120000});
 if(child.status===86&&operation==='apply')return {kind:'unknown',process_interrupted:true};
 if(child.status!==0)throw Error('native-fixture-port: '+(child.stderr||child.error||child.stdout));
 return JSON.parse(child.stdout);
}
export function fixtureStagePort(fixture,expectedCapability){
 const calls={inspect:0,execute:0};
 const assertCurrent=()=>{if(capabilitySha()!==expectedCapability)throw Error('native-capability-source-drift');};
 const observe=value=>value.kind==='observed'?{kind:'observed',output:new Uint8Array(Buffer.from(JSON.stringify(value.result)))}:{kind:value.kind};
 const implementation=Object.freeze({capability_sha256:expectedCapability,assertCurrent,
  async inspect(request){assertCurrent();request.assertCurrent();calls.inspect++;return observe(nativeCall(fixture,'inspect',{ticket:JSON.parse(Buffer.from(request.input).toString('utf8'))}));},
  async execute(request){assertCurrent();request.assertCurrent();calls.execute++;return observe(nativeCall(fixture,'apply',{ticket:JSON.parse(Buffer.from(request.input).toString('utf8'))}));},
 });
 return {implementation,calls};
}
