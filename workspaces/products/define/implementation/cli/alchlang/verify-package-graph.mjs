import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {generate,root,node,fingerprint,selected} from './package-graph-build.mjs';
import {evaluateArtifact} from '../../../../../../implementation/artifact-runtime/pure-operation.mjs';
import {openJsonPort} from '../../../../../../implementation/artifact-runtime/json-pipe.mjs';
import {traverseNativeGraph} from '../../../../../../implementation/artifact-runtime/graph-conductor.mjs';
if(process.execPath!==node){const p=spawnSync(node,[import.meta.filename],{stdio:'inherit'});process.exit(p.status??1);}
const R=path.resolve(root,'../../../../../..'),checks=[];
const artifacts=new Map(selected.components.map(row=>[row.selector,generate(row.name)]));
async function call(selector,args){const artifact=artifacts.get(selector);assert(artifact,'selected native graph role');const r=await evaluateArtifact(artifact.output,artifact.member,args);assert.equal(r.ok,true,JSON.stringify(r));const value=JSON.parse(new TextDecoder().decode(r.wire));if(artifact.member==='operation.mjs'){if(value.tag!=='Returned')throw Error(value.fields.code);return value.fields.value;}return value;}
const protocol=await call('Define.PackageGraph.ClosureProtocol',{marker:true});
const port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
async function closure(value){const {ref}=await port.request({operation:'put-value',value});const state=await traverseNativeGraph({call,port,ref,protocol});const mask=protocol.mask_fields.flatMap(field=>state[field]);return {state,ids:Object.keys(value.members).sort().filter((_,index)=>mask[index])};}
const graph=(rows,roots)=>({members:Object.fromEntries(rows.map(([id,edges,required=false])=>[id,{dependencies:edges,required}])),required_roots:roots});
try{
 for(const [name,value,expected]of [
  ['dependency-chain',graph([['a',['b']],['b',['c']],['c',[]]],['a']),['a','b','c']],
  ['dependency-cycle',graph([['a',['b']],['b',['a']],['c',[]]],['a']),['a','b']],
  ['required-member-without-explicit-root',graph([['a',[],true],['b',[]]],[]),['a']],
  ['all-256-slots',graph(Array.from({length:256},(_,i)=>['m'+String(i).padStart(3,'0'),[],true]),[]),Array.from({length:256},(_,i)=>'m'+String(i).padStart(3,'0'))]
 ]){const result=await closure(value);assert.deepEqual(result.ids,expected);checks.push(name);}
 await assert.rejects(()=>closure(graph([['a',['missing']]],['a'])),/missing-dependency/);checks.push('missing-edge-refused');
 await assert.rejects(()=>closure(graph([['a',[]]],['missing'])),/missing-dependency/);checks.push('missing-root-refused');
 await assert.rejects(()=>closure(graph([['a',[]],['b',['missing']]],['a'])),/missing-dependency/);checks.push('optional-node-invalid-edge-refused');
 const deep=graph(Array.from({length:67},(_,i)=>['n'+String(i).padStart(3,'0'),i<66?['n'+String(i+1).padStart(3,'0')]:[]]),['n000']);await assert.rejects(()=>closure(deep),/dependency-depth/);checks.push('unseen-depth-65-refused');
 const result=await closure(graph([['a',[]],['b',[]]],['a']));await assert.rejects(()=>call(protocol.require_selected,{state:result.state,slot:'1'}),/pack-not-required/);checks.push('unrequired-pack-refused');
 await assert.rejects(()=>call(protocol.init,{value:{nodes:'257',roots:'0'}}),/member-budget/);checks.push('node-count-bound');
 const report={schema_version:'define-native-package-graph-verification/v1',status:'PASS',source:fingerprint(),checks,check_count:checks.length,python_define_engine_imported:false,scope:'Authored native graph algorithm plus generic one-hop observations; full package workflow not inferred.'};writeFileSync(path.join(root,'.local/PACKAGE-GRAPH-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{await port.close();}