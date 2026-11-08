/** Optional formal API for an already admitted Commerce assembly.
 * It rechecks the original project and binds its capture to the same assembly;
 * code generation never opens this API and never requires formal claims.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {coreFreeze} from './commerce-core-syntax.js';
import {pinCoreImplementation} from './commerce-core-physical.js';
import {createCoreCommerceSourceOwner} from './commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from './commerce-core-semantic-owner.js';
import {assertCommerceApplicationAssemblyV1,type CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';
import {exportCoreCommerceFormalInputAdmissionV1,type CoreCommerceFormalInputAdmissionV1} from './commerce-core-formal-input-admission-v1.js';
import {exportCoreCommerceFormalUtf8V1,type CoreCommerceFormalUtf8V1} from './commerce-core-formal-utf8-v1.js';
import {exportCoreCommerceFormalJsonInputWitnessV1,type CoreCommerceFormalJsonInputWitnessV1}
 from './commerce-core-formal-json-input-v1.js';
import {exportCoreCommerceFormalPureWireWitnessV1,type CoreCommerceFormalPureWireWitnessV1}
 from './commerce-core-formal-pure-wire-v1.js';
import {exportCoreCommerceFormalPrimitiveRuleV1,type CoreCommerceFormalPrimitiveRuleV1}
 from './commerce-core-formal-primitive-rule-v1.js';
import {exportCoreCommerceFormalFirstFieldV1,type CoreCommerceFormalFirstFieldV1} from './commerce-core-formal-first-field-v1.js';
import {exportCoreCommerceFormalInputFieldsV1,exportCoreCommerceFormalInputPipelineV1,
 type CoreCommerceFormalInputFieldsV1,type CoreCommerceFormalInputPipelineV1} from './commerce-core-formal-input-fields-v1.js';
import {exportCoreCommerceFormalPureOutcomeV1,type CoreCommerceFormalPureOutcomeV1} from './commerce-core-formal-pure-outcome-v1.js';
import {exportCoreCommerceFormalOperationFailureV1,type CoreCommerceFormalOperationFailureV1} from './commerce-core-formal-operation-failure-v1.js';
import {exportCoreCommerceFormalOrderValueFlowV1,type CoreCommerceFormalOrderValueFlowV1}
 from './commerce-core-formal-order-value-flow-v1.js';
import {exportCoreCommerceFormalAsciiWireV1,type CoreCommerceFormalAsciiWireV1} from './commerce-core-formal-ascii-wire-v1.js';
import {requireCoreCommerceExactFormalModelV1} from './commerce-core-formal-exact-request-v1.js';
import {exportCoreCommerceFormalWireFaultV1,type CoreCommerceFormalWireFaultV1,type CoreCommerceFormalWireFaultKindV1}
 from './commerce-core-formal-wire-fault-v1.js';
import {exportCoreCommerceFormalEscapedWireV1,type CoreCommerceFormalEscapedWireV1}
 from './commerce-core-formal-escaped-wire-v1.js';
import type {CoreCommerceFormalLanguageV1} from './commerce-core-formal-artifacts-v1.js';

export class CommerceApplicationFormalApiErrorV1 extends Error {
 constructor(readonly code:'ForeignApplication'|'DisposedOwner'|'ForeignOwner'){
  super(code);this.name='CommerceApplicationFormalApiErrorV1';
 }
}
const fail=(code:CommerceApplicationFormalApiErrorV1['code']):never=>{throw new CommerceApplicationFormalApiErrorV1(code);};
const ext=path.extname(fileURLToPath(import.meta.url));
const pin=pinCoreImplementation(import.meta.url,[
 'commerce-core-formal-input-admission-v1'+ext,'commerce-core-formal-first-field-v1'+ext,
 'commerce-core-formal-utf8-v1'+ext,
 'commerce-core-formal-json-input-v1'+ext,
 'commerce-core-formal-pure-wire-v1'+ext,
 'commerce-core-formal-primitive-rule-v1'+ext,
 'commerce-core-formal-input-fields-v1'+ext,'commerce-core-formal-ascii-wire-v1'+ext,
 'commerce-core-formal-pure-outcome-v1'+ext,
 'commerce-core-formal-operation-failure-v1'+ext,
 'commerce-core-formal-order-value-flow-v1'+ext,
 'commerce-core-formal-exact-request-v1'+ext,'commerce-core-formal-wire-fault-v1'+ext,
 'commerce-core-formal-escaped-wire-v1'+ext,
]);

export interface CommerceApplicationFormalApiV1 {
 inspect():Readonly<{schema_version:'craft.commerce-application-formal-api/v1-candidate';application:string;
  source_capture_sha256:string;family_sha256:string;formal_claims_required:false;authority_effect:'none'}>;
 exportStructure(workflowId:string,language?:CoreCommerceFormalLanguageV1):ReturnType<CommerceApplicationAssemblyV1['exportFormalStructure']>;
 exportArtifacts(workflowId:string,language?:CoreCommerceFormalLanguageV1):ReturnType<CommerceApplicationAssemblyV1['exportFormalArtifacts']>;
 exportPureUint64(selector:string):ReturnType<CommerceApplicationAssemblyV1['exportPureUint64Formal']>;
 exportTemporal(workflowId:string):ReturnType<CommerceApplicationAssemblyV1['exportFormalTemporal']>;
 exportInputAdmission(selector:string):CoreCommerceFormalInputAdmissionV1;
 exportUtf8Stage(selector:string):CoreCommerceFormalUtf8V1;
 exportJsonInputWitness(selector:string,bytes:Uint8Array):CoreCommerceFormalJsonInputWitnessV1;
 exportPureWireWitness(selector:string,bytes:Uint8Array):CoreCommerceFormalPureWireWitnessV1;
 exportPrimitiveRule(selector:string):CoreCommerceFormalPrimitiveRuleV1;
 exportFirstField(selector:string):CoreCommerceFormalFirstFieldV1;
 exportInputFields(selector:string):CoreCommerceFormalInputFieldsV1;
 exportInputPipeline(selector:string):CoreCommerceFormalInputPipelineV1;
 exportPureOutcome(selector:string):CoreCommerceFormalPureOutcomeV1;
 exportOperationFailure(selector:string):CoreCommerceFormalOperationFailureV1;
 exportOrderValueFlow(selector:string):CoreCommerceFormalOrderValueFlowV1;
 exportAsciiWire(selector:string):CoreCommerceFormalAsciiWireV1;
 exportWireFault(selector:string,fault:CoreCommerceFormalWireFaultKindV1):CoreCommerceFormalWireFaultV1;
 exportEscapedWire(selector:string):CoreCommerceFormalEscapedWireV1;
 requireExactModel(selector:string):never;
 assertCurrent():void;
 close():void;
}
const owners=new WeakSet<object>();
export function assertCommerceApplicationFormalApiV1(api:CommerceApplicationFormalApiV1):void {
 if(!api||typeof api!=='object'||!owners.has(api))fail('ForeignOwner');
 api.assertCurrent();
}

/** Standalone optional adapter while the application assembly remains the
 * execution owner. A second checked source capture must match it exactly. */
export function createCommerceApplicationFormalApiV1(
 sourceRoot:string,assembly:CommerceApplicationAssemblyV1,
):CommerceApplicationFormalApiV1 {
 assertCommerceApplicationAssemblyV1(assembly);pin.assertCurrent();
 const sources=createCoreCommerceSourceOwner();
 let capture:ReturnType<typeof sources.prepare>|undefined;
 let semantics:ReturnType<typeof createCoreCommerceSemanticOwner>|undefined;
 let semantic:ReturnType<NonNullable<typeof semantics>['check']>|undefined;
 let handedOff=false,closed=false;
 const close=()=>{if(closed)return;closed=true;
  if(semantics&&semantic)semantics.dispose(semantic);
  if(capture)sources.dispose(capture);
 };
 try{
  capture=sources.prepare(sourceRoot,'application.alch');
  semantics=createCoreCommerceSemanticOwner(sources);semantic=semantics.check(capture);
  const captured=sources.inspect(capture),checked=semantics.inspect(semantic),selected=assembly.inspect();
  if(captured.capture_sha256!==selected.source_capture_sha256||
   checked.source_capture_sha256!==selected.source_capture_sha256||
   checked.application!==selected.application)fail('ForeignApplication');
  const inspection=coreFreeze({schema_version:'craft.commerce-application-formal-api/v1-candidate' as const,
   application:selected.application,source_capture_sha256:selected.source_capture_sha256,
   family_sha256:selected.family_sha256,formal_claims_required:false as const,authority_effect:'none' as const});
  const current=()=>{
   if(closed)fail('DisposedOwner');pin.assertCurrent();
   sources.assertCurrent(capture!);semantics!.assertSource(semantic!,capture!);assembly.assertCurrent();
   const selectedNow=assembly.inspect();
   if(selectedNow.source_capture_sha256!==inspection.source_capture_sha256||
    selectedNow.family_sha256!==inspection.family_sha256)fail('ForeignApplication');
  };
  const api:CommerceApplicationFormalApiV1=Object.freeze({
   inspect(){current();return inspection;},
   exportStructure(workflowId:string,language:CoreCommerceFormalLanguageV1='alloy'){
    current();const model=assembly.exportFormalStructure(workflowId,language);current();return model;},
   exportArtifacts(workflowId:string,language:CoreCommerceFormalLanguageV1='alloy'){
    current();const model=assembly.exportFormalArtifacts(workflowId,language);current();return model;},
   exportPureUint64(selector:string){current();const model=assembly.exportPureUint64Formal(selector);current();return model;},
   exportTemporal(workflowId:string){current();const model=assembly.exportFormalTemporal(workflowId);current();return model;},
   exportInputAdmission(selector:string){current();const model=exportCoreCommerceFormalInputAdmissionV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportUtf8Stage(selector:string){current();const model=exportCoreCommerceFormalUtf8V1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportJsonInputWitness(selector:string,bytes:Uint8Array){current();
    const model=exportCoreCommerceFormalJsonInputWitnessV1(
     sources,capture!,semantics!,semantic!,assembly,selector,bytes);current();return model;},
   exportPureWireWitness(selector:string,bytes:Uint8Array){current();
    const model=exportCoreCommerceFormalPureWireWitnessV1(
     sources,capture!,semantics!,semantic!,assembly,selector,bytes);current();return model;},
   exportPrimitiveRule(selector:string){current();
    const model=exportCoreCommerceFormalPrimitiveRuleV1(
     sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportFirstField(selector:string){current();const model=exportCoreCommerceFormalFirstFieldV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportInputFields(selector:string){current();const model=exportCoreCommerceFormalInputFieldsV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportInputPipeline(selector:string){current();const model=exportCoreCommerceFormalInputPipelineV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportPureOutcome(selector:string){current();const model=exportCoreCommerceFormalPureOutcomeV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportOperationFailure(selector:string){current();const model=exportCoreCommerceFormalOperationFailureV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportOrderValueFlow(selector:string){current();const model=exportCoreCommerceFormalOrderValueFlowV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportAsciiWire(selector:string){current();const model=exportCoreCommerceFormalAsciiWireV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   exportWireFault(selector:string,fault:CoreCommerceFormalWireFaultKindV1){current();
    const model=exportCoreCommerceFormalWireFaultV1(sources,capture!,semantics!,semantic!,assembly,selector,fault);
    current();return model;},
   exportEscapedWire(selector:string){current();const model=exportCoreCommerceFormalEscapedWireV1(
    sources,capture!,semantics!,semantic!,assembly,selector);current();return model;},
   requireExactModel(selector:string):never{current();return requireCoreCommerceExactFormalModelV1(
    sources,capture!,semantics!,semantic!,assembly,selector);},
   assertCurrent:current,close,
  });
  owners.add(api);current();handedOff=true;return api;
 }finally{if(!handedOff)close();}
}
