import test from 'node:test';
import assert from 'node:assert/strict';
import {
 classifyCoreCommerceStrictUtf8BytesV1,evaluateCoreCommerceFormalUtf8StageV1,
 type CoreCommerceFormalUtf8V1,
} from '../../src/commerce/commerce-core-formal-utf8-v1.js';

const decoder=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true});
const valid=(bytes:Uint8Array)=>{try{decoder.decode(bytes);return true;}catch{return false;}};
const model={max_input_bytes:64,fuel:1,byte_work_unit:32} as CoreCommerceFormalUtf8V1;

test('symbolic UTF-8 byte predicate agrees with fatal TextDecoder on boundary and sampled bytes',()=>{
 const cases:number[][]=[[],[0],[127],[128],[192],[193],[194,128],[223,191],
  [224,159,191],[224,160,128],[236,191,191],[237,159,191],[237,160,128],
  [239,187,191],[240,143,191,191],[240,144,128,128],[243,191,191,191],
  [244,143,191,191],[244,144,128,128],[245,128,128,128],
  [239,187,191,255],[239,187,191,123,125],[34,92,117,68,56,48,48,34]];
 let seed=0x12345678;
 for(let n=0;n<2048;n++){
  const count=n%7,bytes:number[]=[];
  for(let i=0;i<count;i++){
   seed=(Math.imul(seed,1664525)+1013904223)>>>0;
   bytes.push(seed>>>24);
  }
  cases.push(bytes);
 }
 for(const values of cases){
  const bytes=Uint8Array.from(values),classified=classifyCoreCommerceStrictUtf8BytesV1(bytes);
  assert.equal(classified.valid_utf8,valid(bytes),`UTF-8 validity: ${values.join(',')}`);
  assert.equal(classified.leading_bom,values[0]===239&&values[1]===187&&values[2]===191);
 }
 assert.equal(decoder.decode(Uint8Array.from([239,187,191,123,125])).charCodeAt(0),0xfeff);
});

test('pre-JSON typed fault and fuel priority does not imply parser acceptance',()=>{
 const bytes=(length:number)=>new Uint8Array(length);
 assert.deepEqual(evaluateCoreCommerceFormalUtf8StageV1(model,bytes(65)),
  {status:1,fuel_used:0,fault_path:'$.inputs'});
 assert.deepEqual(evaluateCoreCommerceFormalUtf8StageV1(model,bytes(33)),
  {status:2,fuel_used:1,fault_path:'$.inputs'});
 assert.deepEqual(evaluateCoreCommerceFormalUtf8StageV1(model,Uint8Array.from([255])),
  {status:3,fuel_used:1,fault_path:'$.inputs'});
 assert.deepEqual(evaluateCoreCommerceFormalUtf8StageV1(model,Uint8Array.from([239,187,191,255])),
  {status:3,fuel_used:1,fault_path:'$.inputs'});
 assert.deepEqual(evaluateCoreCommerceFormalUtf8StageV1(model,Uint8Array.from([239,187,191,123,125])),
  {status:4,fuel_used:1,fault_path:'$.inputs'});
 assert.deepEqual(evaluateCoreCommerceFormalUtf8StageV1(model,Uint8Array.from([123,125])),
  {status:0,fuel_used:1,fault_path:''});
});
