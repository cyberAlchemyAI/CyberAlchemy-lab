import test from 'node:test';
import assert from 'node:assert/strict';
import {dataDigest,canonicalJson} from '../../src/profile-engine/contracts.js';
import {deriveGenericComputationEnvironment} from '../../src/commerce/commerce-computation-environment.js';
import {evaluateGenericPureExpressionFormalSliceV1} from '../../src/generic/formal-pure-expression-v1.js';
import {buildGenericFiniteBoolListFormalModelV1,enumerateGenericFiniteBoolListValuesV1,
 GenericFiniteBoolListFormalErrorV1} from '../../src/generic/formal-finite-bool-list-v1.js';
import type {GenericComputationContractV1} from '../../src/generic/computation-data-v1.js';

const sha='b'.repeat(64),bool={kind:'scalar',name:'Bool'} as const;
const list={kind:'list',element:bool,min_items:0,max_items:2} as const;
const contract:GenericComputationContractV1={schema_version:'craft.generic-computation/v1-candidate',
 semantics_revision:'ordered-metered-generic-v1-candidate',source_node:'Tiny.Any',
 values:{schema_version:'craft.generic-values/v1-candidate',records:[],enums:[],refinements:[],
  collection_predicates:[],root:bool},inputs:[{name:'values',type:list}],functions:[],result:bool,
 rounding:'reject',limits:{fuel:10000,max_input_bytes:128,max_output_bytes:16,max_value_bytes:128,
  max_items:2,max_call_depth:4},expression:{op:'fold',source:{op:'var',name:'values'},
  initial:{op:'literal',type:bool,value:false},state:{name:'state',type:bool},
  item:{name:'item',type:bool},body:{op:'binary',operator:'or',left:{op:'var',name:'state'},
   right:{op:'var',name:'item'}}},invariant_policy:'reject-inexact/v1',
 record_layout:'canonical-fields/v1',equality_policy:'typed-structural-metered/v1',
 append_policy:'list-item-checkpoint-capacity/v1'};

test('all seven canonical Bool-list values form a complete typed domain',()=>{
 const domain=enumerateGenericFiniteBoolListValuesV1(2);
 assert.deepEqual(domain,[[],[false],[true],[false,false],[true,false],[false,true],[true,true]]);
 const layout=deriveGenericComputationEnvironment(contract);
 const observations=domain.map(values=>{
  const wire=new Uint8Array(Buffer.from(canonicalJson({values})));
  const witness=evaluateGenericPureExpressionFormalSliceV1({contract,
   expression_types:layout.expressions,policy_actions:layout.policy_actions,
   source_capture_sha256:sha,contract_sha256:dataDigest(contract),
   executable_semantics_sha256:sha,code_epoch_sha256:sha},undefined,wire);
  assert.equal(witness.result.ok,true);
  if(witness.result.ok)assert.equal(Buffer.from(witness.result.wire_hex,'hex').toString(),
   String(values.some(Boolean)));
  return {values,input_wire_sha256:witness.input_sha256,result:witness.result};
 });
 const metadata={source_node:contract.source_node,source_capture_sha256:sha,
  contract_sha256:dataDigest(contract),executable_semantics_sha256:sha,
  code_epoch_sha256:sha,input_name:'values',max_items:2 as const};
 const model=buildGenericFiniteBoolListFormalModelV1(metadata,observations);
 assert.equal(model.observations.length,7);
 assert.equal(model.source_binding,'caller-observations-unverified');
 assert.match(model.smtlib2,/\(define-fun Admitted/);
 assert.match(model.smtlib2,/\(= Length 2\)/);
 assert.throws(()=>buildGenericFiniteBoolListFormalModelV1(metadata,
  [...observations.slice(0,2),...observations.slice(3)]),
  (error:unknown)=>error instanceof GenericFiniteBoolListFormalErrorV1&&
   error.code==='UnsupportedTranslation');
});

test('Bool-list all-input table rejects source identity and domain expansion',()=>{
 assert.throws(()=>enumerateGenericFiniteBoolListValuesV1(3 as never),
  (error:unknown)=>error instanceof GenericFiniteBoolListFormalErrorV1&&
   error.code==='UnsupportedTranslation');
 assert.throws(()=>buildGenericFiniteBoolListFormalModelV1({source_node:'Tiny.Any',
  source_capture_sha256:'bad',contract_sha256:sha,executable_semantics_sha256:sha,
  code_epoch_sha256:sha,input_name:'values',max_items:0},[]),
  (error:unknown)=>error instanceof GenericFiniteBoolListFormalErrorV1&&
   error.code==='InvalidSource');
});
