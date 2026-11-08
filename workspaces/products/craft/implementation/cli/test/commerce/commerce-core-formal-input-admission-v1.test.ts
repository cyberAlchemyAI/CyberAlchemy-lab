/** Source-bound conditional formal projections for the original Commerce application. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner,parseCoreCommerceJson} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {evaluateCommerceComputation,evaluateCommerceComputationObserved} from '../../src/commerce/commerce-computation-evaluate.js';
import {createCommerceApplicationAssemblyV1} from '../../src/commerce/commerce-application-assembly-v1.js';
import {exportCoreCommerceFormalInputAdmissionV1,assertCoreCommerceFormalInputAdmissionCurrentV1}
 from '../../src/commerce/commerce-core-formal-input-admission-v1.js';
import {exportCoreCommerceFormalUtf8V1,assertCoreCommerceFormalUtf8CurrentV1,
 evaluateCoreCommerceFormalUtf8StageV1}
 from '../../src/commerce/commerce-core-formal-utf8-v1.js';
import {exportCoreCommerceFormalJsonInputWitnessV1}
 from '../../src/commerce/commerce-core-formal-json-input-v1.js';
import {exportCoreCommerceFormalFirstFieldV1,assertCoreCommerceFormalFirstFieldCurrentV1}
 from '../../src/commerce/commerce-core-formal-first-field-v1.js';
import {exportCoreCommerceFormalInputFieldsV1,assertCoreCommerceFormalInputFieldsCurrentV1,
 exportCoreCommerceFormalInputPipelineV1,assertCoreCommerceFormalInputPipelineCurrentV1}
 from '../../src/commerce/commerce-core-formal-input-fields-v1.js';
import {exportCoreCommerceFormalPureOutcomeV1,assertCoreCommerceFormalPureOutcomeCurrentV1}
 from '../../src/commerce/commerce-core-formal-pure-outcome-v1.js';
import {exportCoreCommerceFormalPureWireWitnessV1}
 from '../../src/commerce/commerce-core-formal-pure-wire-v1.js';
import {exportCoreCommerceFormalPrimitiveRuleV1,evaluateCoreCommerceFormalPrimitiveRuleBodyV1}
 from '../../src/commerce/commerce-core-formal-primitive-rule-v1.js';
import {exportCoreCommerceFormalOperationFailureV1,assertCoreCommerceFormalOperationFailureCurrentV1}
 from '../../src/commerce/commerce-core-formal-operation-failure-v1.js';
import {exportCoreCommerceFormalOrderValueFlowV1,assertCoreCommerceFormalOrderValueFlowCurrentV1}
 from '../../src/commerce/commerce-core-formal-order-value-flow-v1.js';
import {createCommerceApplicationFormalApiV1}
 from '../../src/commerce/commerce-application-formal-api-v1.js';
import {CoreCommerceFormalExactRequestErrorV1}
 from '../../src/commerce/commerce-core-formal-exact-request-v1.js';
import {evaluateCommerceFlowDataV1,CommerceFlowDataErrorV1}
 from '../../src/commerce/commerce-flow-expression-data-v1.js';
import {commerceTransactionOutcomeMappingV1}
 from '../../src/generation/commerce-effectful-operation-source-v1.js';
import {exportCoreCommerceFormalAsciiWireV1,assertCoreCommerceFormalAsciiWireCurrentV1,encodeCoreCommerceFormalAsciiWireV1}
 from '../../src/commerce/commerce-core-formal-ascii-wire-v1.js';
import {exportCoreCommerceFormalWireFaultV1,encodeCoreCommerceFormalWireFaultV1}
 from '../../src/commerce/commerce-core-formal-wire-fault-v1.js';
import {exportCoreCommerceFormalEscapedWireV1,encodeCoreCommerceFormalEscapedWireV1}
 from '../../src/commerce/commerce-core-formal-escaped-wire-v1.js';
import type {ComputationLimitsV1} from '../../src/commerce/commerce-data-v1.js';

const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url));
const candidate=path.join(repo,'examples/ecommerce-target-candidate');
const error=(code:string)=>(actual:unknown)=>
 (actual as {code?:unknown})?.code===code||
 (actual as {diagnostics?:readonly {code?:unknown}[]})?.diagnostics?.[0]?.code===code;

test('C15 checked PayableTotal input byte and initial fuel admission preserve source priority',async()=>{
 const scratch=mkdtempSync(path.join(tmpdir(),'core-commerce-input-formal-'));
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate);
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(capture);
 const stage=createCoreCommerceStageSourceOwner(sources,semantics),source=await stage.prepare(candidate,'application.alch');
 let assembly:Awaited<ReturnType<typeof createCommerceApplicationAssemblyV1>>|undefined;
 let formalApi:ReturnType<typeof createCommerceApplicationFormalApiV1>|undefined;
 let domain:ReturnType<typeof createCommerceComputationDomainOwner>|undefined;
 let baseline:ReturnType<NonNullable<typeof domain>['check']>|undefined;
 try{
  assembly=await createCommerceApplicationAssemblyV1(candidate,path.join(scratch,'application'));
  const model=exportCoreCommerceFormalInputAdmissionV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(model.application,'Shop.Application.Ecommerce');
  assert.equal(model.service,'orders');
  assert.equal(model.max_input_bytes,1048576);
  assert.equal(model.fuel,100000);
  assert.equal(model.byte_work_unit,32);
  assert.deepEqual(model.admission_codes,{ready_for_decode:0,InputBound:1,ResourceLimit:2});
  assert.equal(model.source_capture_sha256,assembly.inspect().source_capture_sha256);
  assert.equal(model.family_sha256,assembly.inspect().family_sha256);
  assert.match(model.smtlib2,/\(define-fun InputBound \(\) Bool \(> InputByteCount MaxInputBytes\)\)/);
  assert.match(model.smtlib2,/\(define-fun InitialByteWorkExhausted \(\) Bool \(> InputByteCount \(\* 32 InitialFuel\)\)\)/);
  assert.match(model.smtlib2,/\(define-fun AdmissionStatus \(\) Int \(ite InputBound 1 \(ite InitialByteWorkExhausted 2 0\)\)\)/);
  assert.ok(model.unsupported_semantics.includes('typed-input-validation'));
  assert.doesNotThrow(()=>assertCoreCommerceFormalInputAdmissionCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',model));
  assert.throws(()=>assertCoreCommerceFormalInputAdmissionCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',
   {...model,max_input_bytes:model.max_input_bytes+1}),error('InvalidModel'));
  assert.throws(()=>exportCoreCommerceFormalInputAdmissionV1(sources,{...capture},semantics,semantic,assembly!,'Orders.PayableTotal'),
   error('ForeignOwner'));

  const captured=sources.inspect(capture),paths=new Set(captured.reconstruction.modules.map(row=>row.path));
  const texts=captured.files.filter(row=>paths.has(row.path));
  const asset=captured.files.find(row=>row.path==='contracts/compute-bounds.json')!;
  const bounds=parseCoreCommerceJson(asset.text,asset.path) as {computation:{limits:ComputationLimitsV1}};
  domain=createCommerceComputationDomainOwner(stage,source);
  baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',bounds.computation.limits));
  const over=evaluateCommerceComputation(domain,baseline,new Uint8Array(model.max_input_bytes+1));
  assert.equal(over.ok,false);
  if(over.ok)assert.fail('over-bound wire accepted');
  assert.equal(over.error.code,'InputBound');
  assert.equal(over.fuel_used,0);
  const at=evaluateCommerceComputation(domain,baseline,new Uint8Array(model.max_input_bytes));
  assert.equal(at.ok,false);
  if(at.ok)assert.fail('malformed wire accepted');
  assert.equal(at.error.code,'InputType');

  const first=exportCoreCommerceFormalFirstFieldV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(first.first_field,'subtotal');
  assert.deepEqual(first.input_fields,['subtotal','discountMinor','taxMinor','shippingMinor']);
  assert.equal(first.source_capture_sha256,model.source_capture_sha256);
  assert.equal(first.bounds_asset_sha256,model.bounds_asset_sha256);
  assert.match(first.smtlib2,/\(define-fun ClosedInput \(\) Bool \(and ParsedRootObject InputHas0 InputHas1 InputHas2 InputHas3 \(= AdditionalKeyCount 0\)\)\)/);
  assert.match(first.smtlib2,/\(define-fun FirstFieldStatus \(\) Int \(ite \(not ClosedInput\) 1 \(ite \(>= InitialByteWork InitialFuel\) 2/);
  assert.ok(first.unsupported_semantics.includes('utf8-and-json-parser-translation'));
  assert.doesNotThrow(()=>assertCoreCommerceFormalFirstFieldCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',first));
  assert.throws(()=>assertCoreCommerceFormalFirstFieldCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',
   {...first,first_field:'discountMinor'}),/InvalidModel/);
  const missing=Buffer.from('{}'),missingResult=evaluateCommerceComputation(domain,baseline,missing);
  assert.equal(missingResult.ok,false);
  if(missingResult.ok)assert.fail('missing input fields accepted');
  assert.equal(missingResult.error.code,'InputType');
  assert.equal(missingResult.fuel_used,Math.ceil(missing.length/32));
  const fields={subtotal:'x',discountMinor:'0',taxMinor:'0',shippingMinor:'0'};
  const invalid=Buffer.from(JSON.stringify(fields)),invalidResult=evaluateCommerceComputation(domain,baseline,invalid);
  assert.equal(invalidResult.ok,false);
  if(invalidResult.ok)assert.fail('invalid first wire accepted');
  assert.equal(invalidResult.error.code,'InputType');
  assert.equal(invalidResult.fuel_used,Math.ceil(invalid.length/32)+1);
  const overflow=Buffer.from(JSON.stringify({...fields,subtotal:'18446744073709551616'}));
  const overflowResult=evaluateCommerceComputation(domain,baseline,overflow);
  assert.equal(overflowResult.ok,false);
  if(overflowResult.ok)assert.fail('overflowing first wire accepted');
  assert.equal(overflowResult.error.code,'InputBound');
  assert.equal(overflowResult.fuel_used,Math.ceil(overflow.length/32)+1);

  const all=exportCoreCommerceFormalInputFieldsV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.deepEqual(all.input_fields,first.input_fields);
  assert.equal(all.max_value_bytes,524288);
  assert.equal(all.scalar_checkpoint_fuel_per_field,3);
  assert.equal(all.remaining_fuel_after_all_input_checkpoints_at_max_wire_size,67220);
  assert.equal(all.source_capture_sha256,first.source_capture_sha256);
  formalApi=createCommerceApplicationFormalApiV1(candidate,assembly);
  assert.equal(formalApi.inspect().formal_claims_required,false);
  assert.equal(formalApi.exportStructure('Orders.Checkout.Checkout').source_capture_sha256,model.source_capture_sha256);
  assert.equal(formalApi.exportPureUint64('Orders.PayableTotal').source_capture_sha256,model.source_capture_sha256);
  assert.equal(formalApi.exportTemporal('Orders.Checkout.Checkout').source_capture_sha256,model.source_capture_sha256);
  assert.equal(formalApi.exportInputAdmission('Orders.PayableTotal').smtlib2_sha256,model.smtlib2_sha256);
  const utf8=exportCoreCommerceFormalUtf8V1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(formalApi.exportUtf8Stage('Orders.PayableTotal').smtlib2_sha256,utf8.smtlib2_sha256);
  assert.equal(utf8.source_capture_sha256,model.source_capture_sha256);
  assert.equal(utf8.admission_model_sha256,model.smtlib2_sha256);
  assert.equal(utf8.max_input_bytes,model.max_input_bytes);
  assert.equal(utf8.fuel,model.fuel);
  assert.ok(utf8.unsupported_semantics.includes('general-json-syntax-escapes-duplicates-depth-and-value'));
  assert.match(utf8.smtlib2,/\(define-fun-rec StrictUtf8From/);
  assert.match(utf8.smtlib2,/\(assert \(forall \(\(i Int\)\)/);
  assert.match(utf8.smtlib2,/\(define-fun Utf8StageStatus \(\) Int \(ite InputBound 1/);
  assert.doesNotThrow(()=>assertCoreCommerceFormalUtf8CurrentV1(
   sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',utf8));
  for(const [wire,code,status] of [
   [Uint8Array.from([255]),'InvalidUnicode',3],
   [Uint8Array.from([239,187,191,255]),'InvalidUnicode',3],
   [Uint8Array.from([239,187,191,123,125]),'InputType',4],
  ] as const){
   const projected=evaluateCoreCommerceFormalUtf8StageV1(utf8,wire);
   const actual=evaluateCommerceComputation(domain,baseline,wire);
   assert.equal(projected.status,status);
   assert.equal(actual.ok,false);
   if(actual.ok)assert.fail('faulting UTF-8 wire accepted');
   assert.equal(actual.error.code,code);
   assert.equal(actual.error.expression_path,projected.fault_path);
   assert.equal(actual.fuel_used,projected.fuel_used);
  }
  const inputWire=Buffer.from('{"subtotal":"10","discountMinor":"1","taxMinor":"2","shippingMinor":"3"}');
  const witness=exportCoreCommerceFormalJsonInputWitnessV1(
   sources,capture,semantics,semantic,assembly,'Orders.PayableTotal',inputWire);
  assert.equal(formalApi.exportJsonInputWitness('Orders.PayableTotal',inputWire).smtlib2_sha256,
   witness.smtlib2_sha256);
  assert.equal(witness.source_capture_sha256,model.source_capture_sha256);
  assert.equal(witness.result.status,'ready_for_expression');
  assert.deepEqual(witness.result.values,[10n,1n,2n,3n]);
  assert.match(witness.smtlib2,/\(define-fun Input0Value \(\) Int 10\)/);
  assert.ok(witness.unsupported_semantics.includes('universal-byte-to-json-relation'));
  assert.equal(formalApi.exportFirstField('Orders.PayableTotal').smtlib2_sha256,first.smtlib2_sha256);
  assert.equal(formalApi.exportInputFields('Orders.PayableTotal').smtlib2_sha256,all.smtlib2_sha256);
  const pipeline=exportCoreCommerceFormalInputPipelineV1(
   sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(formalApi.exportInputPipeline('Orders.PayableTotal').smtlib2_sha256,pipeline.smtlib2_sha256);
  assert.equal(pipeline.input_fields_model_sha256,all.smtlib2_sha256);
  assert.equal(pipeline.parser_observation_codes.InvalidUnicode,2);
  assert.ok(pipeline.unsupported_semantics.includes('byte-to-utf8-and-json-parser-relation'));
  assert.match(pipeline.smtlib2,/\(define-fun PipelineStatus \(\) Int \(ite \(not Utf8Valid\) 1/);
  assert.match(pipeline.smtlib2,/\(define-fun PipelineFuelUsed \(\) Int \(ite \(or \(not Utf8Valid\)/);
  assert.doesNotThrow(()=>assertCoreCommerceFormalInputPipelineCurrentV1(
   sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',pipeline));
  assert.throws(()=>assertCoreCommerceFormalInputPipelineCurrentV1(
   sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',
   {...pipeline,application:'foreign'}),error('InvalidModel'));
  const deepJson='{"subtotal":'+'['.repeat(33)+'0'+']'.repeat(33)+
   ',"discountMinor":"0","taxMinor":"0","shippingMinor":"0"}';
  for(const [wire,code,path] of [
   [new Uint8Array([255]),'InvalidUnicode','$.inputs'],
   [Buffer.from('{"subtotal":"\\ud800","discountMinor":"0","taxMinor":"0","shippingMinor":"0"}'),'InvalidUnicode','$.inputs'],
   [Buffer.from('{"subtotal":"0","subtotal":"1","discountMinor":"0","taxMinor":"0","shippingMinor":"0"}'),'InputType','$.inputs'],
   [Buffer.from(deepJson),'InputBound','$.inputs'],
   [Buffer.from('{}'),'InputType','$.inputs'],
   [Buffer.from('{"subtotal":0,"discountMinor":"0","taxMinor":"0","shippingMinor":"0"}'),'InputType','$.inputs.subtotal'],
  ] as const){
   const observed=evaluateCommerceComputation(domain!,baseline!,wire);
   assert.equal(observed.ok,false);
   if(observed.ok)assert.fail('invalid source wire accepted');
   assert.equal(observed.error.code,code);
   assert.equal(observed.error.expression_path,path);
   assert.equal(observed.fuel_used,Math.ceil(wire.length/32)+(path==='$.inputs.subtotal'?1:0));
  }
  const outcome=exportCoreCommerceFormalPureOutcomeV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(formalApi.exportPureOutcome('Orders.PayableTotal').smtlib2_sha256,outcome.smtlib2_sha256);
  assert.equal(outcome.arithmetic_node_count,3);
  assert.equal(outcome.max_fuel_used_after_successful_input_at_max_wire_size,32830);
  assert.equal(outcome.max_output_bytes,524288);
  assert.equal(outcome.contract_sha256,domain.inspect(baseline).contract_sha256);
  assert.equal(outcome.input_fields_model_sha256,all.smtlib2_sha256);
  assert.match(outcome.smtlib2,/\(define-fun OutputWire \(\) String \(ite \(= Status 0\)/);
  assert.match(outcome.smtlib2,/\(define-fun FuelUsed \(\) Int \(\+ InputFuel/);
  assert.ok(outcome.unsupported_semantics.includes('parser-to-decoded-value-binding'));
  assert.doesNotThrow(()=>assertCoreCommerceFormalPureOutcomeCurrentV1(
   sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',outcome));
  assert.throws(()=>assertCoreCommerceFormalPureOutcomeCurrentV1(
   sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',
   {...outcome,max_output_bytes:22}),error('InvalidModel'));
  const evalPure=(subtotal:string,discountMinor:string,taxMinor:string,shippingMinor:string)=>{
   const wire=Buffer.from(JSON.stringify({subtotal,discountMinor,taxMinor,shippingMinor}));
   return {result:evaluateCommerceComputation(domain!,baseline!,wire),inputFuel:Math.ceil(wire.length/32)+12};
  };
  const success=evalPure('100','5','7','3');
  assert.equal(success.result.ok,true);
  if(!success.result.ok)assert.fail('valid pure root rejected');
  assert.equal(new TextDecoder().decode(success.result.wire),'"105"');
  assert.equal(success.result.fuel_used,success.inputFuel+50);
  const successWire=Buffer.from(JSON.stringify({subtotal:'100',discountMinor:'5',taxMinor:'7',shippingMinor:'3'}));
  const pureWire=exportCoreCommerceFormalPureWireWitnessV1(
   sources,capture,semantics,semantic,assembly,'Orders.PayableTotal',successWire);
  assert.equal(formalApi.exportPureWireWitness('Orders.PayableTotal',successWire).smtlib2_sha256,
   pureWire.smtlib2_sha256);
  assert.equal(pureWire.source_capture_sha256,outcome.source_capture_sha256);
  assert.equal(pureWire.pure_model_sha256,outcome.smtlib2_sha256);
  assert.equal(pureWire.result.status,'success');
  assert.equal(pureWire.result.value,105n);
  assert.equal(pureWire.result.wire_hex,Buffer.from(success.result.wire).toString('hex'));
  assert.equal(pureWire.result.fuel_used,success.result.fuel_used);
  assert.ok(pureWire.unsupported_semantics.includes('enclosing-operation-error-action-execution'));
  const canReserve=exportCoreCommerceFormalPrimitiveRuleV1(
   sources,capture,semantics,semantic,assembly,'Inventory.CanReserve');
  assert.equal(formalApi.exportPrimitiveRule('Inventory.CanReserve').smtlib2_sha256,
   canReserve.smtlib2_sha256);
  assert.equal(canReserve.source_capture_sha256,model.source_capture_sha256);
  assert.equal(canReserve.service,'inventory');
  assert.deepEqual(canReserve.used_primitive_inputs.map(row=>row.name),['quantity','available']);
  const ruleFalse=evaluateCoreCommerceFormalPrimitiveRuleBodyV1(canReserve.body,
   {quantity:0n,available:7n},{quantity:'UInt64',available:'UInt64'});
  const ruleTrue=evaluateCoreCommerceFormalPrimitiveRuleBodyV1(canReserve.body,
   {quantity:2n,available:7n},{quantity:'UInt64',available:'UInt64'});
  assert.equal(ruleFalse.value,false);
  assert.equal(ruleTrue.value,true);
  assert.equal(ruleFalse.body_fuel,12);
  assert.equal(ruleTrue.body_fuel,21);
  assert.ok(canReserve.unsupported_semantics.includes('nonprimitive-parameter-checkpoint-fuel'));
  const functionIndex=domain.inspect(baseline).contract.functions.findIndex(row=>row.name==='Orders.PayableTotal');
  assert.ok(functionIndex>=0);
  const bodyPath=`$.functions[${functionIndex}].body`;
  for(const [input,code,path,expressionFuel] of [
   [['4','5','0','0'],'ArithmeticUnderflow',bodyPath+'.left.left',31],
   [['18446744073709551615','0','1','0'],'ArithmeticOverflow',bodyPath+'.left',36],
   [['18446744073709551615','0','0','1'],'ArithmeticOverflow',bodyPath,41],
  ] as const){
   const observed=evalPure(...input);
   assert.equal(observed.result.ok,false);
   if(observed.result.ok)assert.fail('arithmetic fault accepted');
   assert.equal(observed.result.error.code,code);
   assert.equal(observed.result.error.expression_path,path);
   assert.equal(observed.result.fuel_used,observed.inputFuel+expressionFuel);
   const wire=Buffer.from(JSON.stringify({subtotal:input[0],discountMinor:input[1],
    taxMinor:input[2],shippingMinor:input[3]}));
   const projection=formalApi.exportPureWireWitness('Orders.PayableTotal',wire);
   assert.equal(projection.result.status,code);
   assert.equal(projection.result.error_path,path);
   assert.equal(projection.result.fuel_used,observed.result.fuel_used);
   assert.equal(projection.result.pure_error_annotation_attached,true);
  }
  const annotated=evaluateCommerceComputationObserved(domain!,baseline!,Buffer.from(JSON.stringify({
   subtotal:'4',discountMinor:'5',taxMinor:'0',shippingMinor:'0',
  })));
  assert.equal(annotated.evaluation_phase,'expression');
  assert.equal(annotated.declared_actions.length,1);
  assert.equal(annotated.declared_actions[0]?.declaration,'Orders.PayableTotal');
  assert.deepEqual(annotated.declared_actions[0]?.action,outcome.declared_error_annotation);
  assert.match(outcome.smtlib2,/\(define-fun ActionAttached \(\) Bool \(not \(= Status 0\)\)\)/);
  const operation=exportCoreCommerceFormalOperationFailureV1(
   sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(formalApi.exportOperationFailure('Orders.PayableTotal').smtlib2_sha256,operation.smtlib2_sha256);
  assert.equal(operation.pure_outcome_sha256,outcome.smtlib2_sha256);
  assert.equal(operation.let_binding,'payableMinor');
  assert.equal(operation.action.kind,'fail');
  assert.equal(operation.action.code,'calculation-failed');
  assert.equal(operation.adapter_decision,'evaluation-error');
  assert.equal(operation.action_requirement,'requires-original-caller-to-apply-source-action');
  assert.equal(operation.parameter_validation_decision,'parameter-validation-error');
  assert.equal(operation.parameter_validation_action,'none');
  assert.equal(operation.before_first_declared_transaction,true);
  assert.deepEqual(operation.argument_bindings,
   ['subtotal','quote.discountMinor','quote.taxMinor','quote.shippingMinor']);
  assert.equal(operation.argument_charge_count_when_ready,9);
  assert.ok(operation.unsupported_semantics.includes('actual-failure-action-execution'));
  assert.ok(operation.unsupported_semantics.includes('transaction-effects-and-rollback'));
  assert.match(operation.smtlib2,/\(define-fun OperationActionProposed \(\) Bool \(not \(= OperationFailureCause 0\)\)\)/);
  assert.match(operation.smtlib2,/\(define-fun OperationFailureCause \(\) Int \(ite \(= ArgumentStatus 1\) 1/);
  const checkedOperation=semantics.inspect(semantic).effects.find(plan=>
   `${plan.operation.module}.${plan.operation.name}`===operation.operation);
  assert.ok(checkedOperation);
  const payableStep=checkedOperation.body[operation.step_index];
  assert.equal(payableStep?.kind,'let');
  if(payableStep?.kind!=='let')assert.fail('checked payable let missing');
  assert.equal(payableStep.value.expression.op,'call');
  const callExpression=payableStep.value.expression;
  const callPath=`$.body[${operation.step_index}].value.expression`;
  const evaluateArguments=(scope:Readonly<Record<string,unknown>>)=>{
   const charges:string[]=[];
   const invoked:unknown[][]=[];
   try{
    const value=evaluateCommerceFlowDataV1(callExpression,callPath,scope,{
     charge:p=>{charges.push(p);},
     pure:(_p,args)=>{invoked.push([...args]);return 105n;},
     native:()=>assert.fail('unexpected native observation'),
     context:()=>assert.fail('unexpected private context'),
     isNullaryEnum:()=>false,
    });
    return {value,charges,invoked,error:null};
   }catch(error){return {value:null,charges,invoked,error};}
  };
  const absentSubtotal=evaluateArguments({quote:{discountMinor:5n,taxMinor:7n,shippingMinor:3n}});
  assert.ok(absentSubtotal.error instanceof CommerceFlowDataErrorV1);
  assert.equal(absentSubtotal.error.code,'InputType');
  assert.equal(absentSubtotal.error.source_path,callPath+'.arguments[0]');
  assert.equal(absentSubtotal.charges.length+1,3); // generated let-step charge
  assert.deepEqual(absentSubtotal.invoked,[]);
  const absentTax=evaluateArguments({subtotal:100n,quote:{discountMinor:5n,shippingMinor:3n}});
  assert.ok(absentTax.error instanceof CommerceFlowDataErrorV1);
  assert.equal(absentTax.error.code,'InputType');
  assert.equal(absentTax.error.source_path,callPath+'.arguments[2]');
  assert.equal(absentTax.charges.length+1,7); // generated let-step charge
  assert.deepEqual(absentTax.invoked,[]);
  const readyArguments=evaluateArguments({subtotal:100n,quote:{discountMinor:5n,taxMinor:7n,shippingMinor:3n}});
  assert.equal(readyArguments.error,null);
  assert.equal(readyArguments.value,105n);
  assert.equal(readyArguments.charges.length+1,operation.argument_charge_count_when_ready);
  assert.deepEqual(readyArguments.invoked,[[100n,5n,7n,3n]]);
  assert.doesNotThrow(()=>assertCoreCommerceFormalOperationFailureCurrentV1(
   sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',operation));
  const valueFlow=exportCoreCommerceFormalOrderValueFlowV1(
   sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(formalApi.exportOrderValueFlow('Orders.PayableTotal').smtlib2_sha256,valueFlow.smtlib2_sha256);
  assert.equal(valueFlow.operation_model_sha256,operation.smtlib2_sha256);
  assert.equal(valueFlow.operation,operation.operation);
  assert.equal(valueFlow.transaction,'AcceptCheckout');
  assert.equal(valueFlow.target_entity,'Orders.Order');
  assert.equal(valueFlow.target_field,'payableMinor');
  assert.equal(valueFlow.assumed_control_path,'fresh-normal-operation-path');
  assert.deepEqual(valueFlow.guard_action,{kind:'reject',code:'quote-expired'});
  assert.deepEqual(valueFlow.precondition_steps.map(row=>row.kind),['require-absent','capacity']);
  assert.deepEqual(valueFlow.precondition_steps.map(row=>row.entity),
   ['Orders.ReplayRecord','Orders.ReplayRecord']);
  assert.equal(valueFlow.precondition_steps[1].maximum,4096);
  assert.ok(valueFlow.unsupported_semantics.includes('native-row-write-and-commit'));
  assert.ok(valueFlow.unsupported_semantics.includes('native-disposition-proof-production'));
  assert.match(valueFlow.smtlib2,/\(define-fun QuoteNotExpired \(\) Bool \(> QuoteExpiresAtEpochMs NowEpochMs\)\)/);
  assert.match(valueFlow.smtlib2,/\(assert \(=> CapacityInstructionResumed RequireAbsentInstructionResumed\)\)/);
  assert.match(valueFlow.smtlib2,/\(assert \(=> NormalPathOrderCreateFieldEvaluationReached \(and QuoteNotExpired \(= ArgumentStatus 0\) \(= Status 0\) CapacityInstructionResumed\)\)\)/);
  assert.match(valueFlow.smtlib2,/\(define-fun OrderCreatePayableMinorFieldValue \(\) Int PayableMinorLetValue\)/);
  assert.match(valueFlow.smtlib2,/\(define-fun ProvenRollbackRejectionProposed \(\) Bool \(= OriginalDisposition 1\)\)/);
  assert.match(valueFlow.smtlib2,/\(define-fun UnresolvedCommitFailureProposed \(\) Bool \(= OriginalDisposition 2\)\)/);
  const expiryGuard=checkedOperation.body[valueFlow.guard_step_index];
  assert.equal(expiryGuard?.kind,'guard');
  if(expiryGuard?.kind!=='guard')assert.fail('checked quote expiry guard missing');
  assert.deepEqual(expiryGuard.on_false,valueFlow.guard_action);
  const guardCharges:string[]=[];
  const guardDispatch={charge:(p:string)=>{guardCharges.push(p);},
   pure:()=>assert.fail('unexpected pure call in expiry guard'),
   native:()=>assert.fail('unexpected native call in expiry guard'),
   context:()=>assert.fail('unexpected context in expiry guard'),
   isNullaryEnum:()=>false};
  const expiry=(expires:bigint,now:bigint)=>evaluateCommerceFlowDataV1(
   expiryGuard.condition.expression,valueFlow.guard_source_path,
   {quote:{expiresAtEpochMs:expires},nowEpochMs:now},guardDispatch);
  assert.equal(expiry(11n,10n),true);
  assert.equal(expiry(10n,10n),false);
  assert.equal(expiry(9n,10n),false);
  assert.equal(guardCharges.length,12);
  const transactionStep=checkedOperation.body[valueFlow.transaction_step_index];
  assert.equal(transactionStep?.kind,'transaction');
  if(transactionStep?.kind!=='transaction')assert.fail('checked acceptance transaction missing');
  const dispositionMapping=commerceTransactionOutcomeMappingV1(transactionStep.transaction);
  assert.deepEqual(valueFlow.direct_dispositions.committed,dispositionMapping.committed);
  assert.equal(dispositionMapping['rolled-back'].action?.kind,'reject');
  assert.deepEqual(valueFlow.direct_dispositions.rolled_back.action,
   dispositionMapping['rolled-back'].action);
  assert.equal(dispositionMapping.indeterminate.action?.kind,'fail');
  assert.deepEqual(valueFlow.direct_dispositions.indeterminate.action,
   dispositionMapping.indeterminate.action);
  assert.equal(valueFlow.direct_dispositions.indeterminate.retain_original,true);
  const mutation=transactionStep.transaction.body[valueFlow.mutation_index];
  assert.equal(transactionStep.transaction.body[0]?.kind,'require-absent');
  assert.equal(transactionStep.transaction.body[1]?.kind,'capacity');
  assert.equal(mutation?.kind,'mutation');
  if(mutation?.kind!=='mutation')assert.fail('checked Order create missing');
  const payableField=mutation.fields[valueFlow.field_index];
  assert.equal(payableField?.name,'payableMinor');
  assert.ok(payableField);
  const fieldCharges:string[]=[];
  const fieldDispatch={charge:(p:string)=>{fieldCharges.push(p);},
   pure:()=>assert.fail('unexpected pure call in direct Order field'),
   native:()=>assert.fail('unexpected native observation in direct Order field'),
   context:()=>assert.fail('unexpected private context in direct Order field'),
   isNullaryEnum:()=>false};
  assert.equal(evaluateCommerceFlowDataV1(payableField.value.expression,valueFlow.field_source_path,
   {payableMinor:105n},fieldDispatch),105n);
  assert.deepEqual(fieldCharges,[valueFlow.field_source_path]);
  assert.throws(()=>evaluateCommerceFlowDataV1(payableField.value.expression,valueFlow.field_source_path,
   {},fieldDispatch),(failure:unknown)=>failure instanceof CommerceFlowDataErrorV1&&
    failure.code==='InputType'&&failure.source_path===valueFlow.field_source_path);
  assert.doesNotThrow(()=>assertCoreCommerceFormalOrderValueFlowCurrentV1(
   sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',valueFlow));
  const ascii=exportCoreCommerceFormalAsciiWireV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(ascii.input_fields_model_sha256,all.smtlib2_sha256);
  assert.equal(formalApi.exportAsciiWire('Orders.PayableTotal').smtlib2_sha256,ascii.smtlib2_sha256);
  for(const selector of ['Orders.PayableTotal','Orders.PlaceOrderEntry']){
   assert.throws(()=>formalApi!.requireExactModel(selector),(failure:unknown)=>{
    if(!(failure instanceof CoreCommerceFormalExactRequestErrorV1))return false;
    assert.equal(failure.code,'UnsupportedTranslation');
    assert.equal(failure.selector,selector);
    assert.equal(failure.application,model.application);
    assert.equal(failure.source_capture_sha256,model.source_capture_sha256);
    assert.ok(failure.missing_semantics.includes('byte-to-utf8-and-json-parser-outcome-including-escapes-unicode-duplicates-and-depth-priority'));
    assert.ok(failure.missing_semantics.includes('native-transaction-precondition-outcomes-commit-rollback-and-disposition-proof'));
    return true;
   });
  }
  assert.throws(()=>formalApi!.requireExactModel('Orders.UnknownEntry'),error('UnknownReference'));
  assert.match(ascii.smtlib2,/\(define-fun InputWire \(\) String \(str\.\+\+ /);
  assert.match(ascii.smtlib2,/\(assert \(= InputByteCount \(str\.len InputWire\)\)\)/);
  assert.ok(ascii.unsupported_semantics.includes('arbitrary-json-syntax-or-key-order'));
  assert.doesNotThrow(()=>assertCoreCommerceFormalAsciiWireCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',ascii));
  const asciiWire=encodeCoreCommerceFormalAsciiWireV1(ascii,['0','x','0','0']);
  assert.deepEqual(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(asciiWire)),
   {subtotal:'0',discountMinor:'x',taxMinor:'0',shippingMinor:'0'});
  const asciiResult=evaluateCommerceComputation(domain,baseline,asciiWire);
  assert.equal(asciiResult.ok,false);
  if(asciiResult.ok)assert.fail('invalid ASCII wire accepted');
  assert.equal(asciiResult.error.code,'InputType');
  assert.equal(asciiResult.fuel_used,Math.ceil(asciiWire.length/32)+4);
  assert.throws(()=>encodeCoreCommerceFormalAsciiWireV1(ascii,['0','bad"json','0','0']),error('InvalidWireValue'));
  for(const [fault,code] of [['invalid-utf8-trailer','InvalidUnicode'],['invalid-json-trailer','InputType']] as const){
   const faultModel=exportCoreCommerceFormalWireFaultV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal',fault);
   assert.equal(faultModel.post_admission_error,code);
   assert.equal(formalApi.exportWireFault('Orders.PayableTotal',fault).smtlib2_sha256,faultModel.smtlib2_sha256);
   assert.match(faultModel.smtlib2,/\(define-fun FaultStatus \(\) Int \(ite InputBound 1 \(ite InitialByteWorkExhausted 2 3\)\)\)/);
   const faulty=encodeCoreCommerceFormalWireFaultV1(ascii,['0','0','0','0'],fault);
   const observed=evaluateCommerceComputation(domain,baseline,faulty);
   assert.equal(observed.ok,false);
   if(observed.ok)assert.fail('malformed trailer accepted');
   assert.equal(observed.error.code,code);
   assert.equal(observed.fuel_used,Math.ceil(faulty.length/32));
  }
  const escaped=exportCoreCommerceFormalEscapedWireV1(sources,capture,semantics,semantic,assembly,'Orders.PayableTotal');
  assert.equal(formalApi.exportEscapedWire('Orders.PayableTotal').smtlib2_sha256,escaped.smtlib2_sha256);
  assert.match(escaped.smtlib2,/\(define-fun-rec EscapeAscii/);
  const escapedWire=encodeCoreCommerceFormalEscapedWireV1(escaped,['0','0','0','0']);
  assert.match(new TextDecoder().decode(escapedWire),/\\u0030/);
  assert.deepEqual(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(escapedWire)),
   {subtotal:'0',discountMinor:'0',taxMinor:'0',shippingMinor:'0'});
  const escapedResult=evaluateCommerceComputation(domain,baseline,escapedWire);
  assert.equal(escapedResult.ok,true);
  const escapedInvalid=encodeCoreCommerceFormalEscapedWireV1(escaped,['x','0','0','0']);
  const escapedInvalidResult=evaluateCommerceComputation(domain,baseline,escapedInvalid);
  assert.equal(escapedInvalidResult.ok,false);
  if(escapedInvalidResult.ok)assert.fail('invalid escaped decimal accepted');
  assert.equal(escapedInvalidResult.error.code,'InputType');
  assert.equal(escapedInvalidResult.fuel_used,Math.ceil(escapedInvalid.length/32)+1);
  assert.match(all.smtlib2,/\(define-fun Field3Status \(\) Int/);
  assert.match(all.smtlib2,/\(define-fun InputStatus \(\) Int \(ite \(not ClosedInput\) 1/);
  assert.match(all.smtlib2,/\(assert \(<= \(\+ \(div \(\+ MaxInputBytes 31\) 32\) 12\) InitialFuel\)\)/);
  assert.ok(all.unsupported_semantics.includes('utf8-and-json-parser-translation'));
  assert.doesNotThrow(()=>assertCoreCommerceFormalInputFieldsCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',all));
  assert.throws(()=>assertCoreCommerceFormalInputFieldsCurrentV1(sources,capture,semantics,semantic,assembly!,'Orders.PayableTotal',
   {...all,remaining_fuel_after_all_input_checkpoints_at_max_wire_size:0}),error('InvalidModel'));
  const lateFields={subtotal:'0',discountMinor:'0',taxMinor:'0',shippingMinor:'0'};
  const second=Buffer.from(JSON.stringify({...lateFields,discountMinor:'x'}));
  const secondResult=evaluateCommerceComputation(domain,baseline,second);
  assert.equal(secondResult.ok,false);
  if(secondResult.ok)assert.fail('invalid second wire accepted');
  assert.equal(secondResult.error.code,'InputType');
  assert.equal(secondResult.fuel_used,Math.ceil(second.length/32)+4);
  const fourth=Buffer.from(JSON.stringify({...lateFields,shippingMinor:'18446744073709551616'}));
  const fourthResult=evaluateCommerceComputation(domain,baseline,fourth);
  assert.equal(fourthResult.ok,false);
  if(fourthResult.ok)assert.fail('overflowing fourth wire accepted');
  assert.equal(fourthResult.error.code,'InputBound');
  assert.equal(fourthResult.fuel_used,Math.ceil(fourth.length/32)+10);
 }finally{
  if(domain&&baseline)domain.dispose(baseline);
  formalApi?.close();
  assembly?.close();stage.dispose(source);semantics.dispose(semantic);sources.dispose(capture);
  rmSync(scratch,{recursive:true,force:true});
 }
});
