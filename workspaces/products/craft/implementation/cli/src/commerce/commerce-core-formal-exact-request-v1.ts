/** Explicit exact-model boundary for the same admitted Commerce application.
 * Partial source-bound projections stay usable, but a request for complete
 * wire/operation behavior must fail until every admitted branch is translated.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import type {CoreCommerceSourceOwner,CoreCommerceSourceCapture} from './commerce-core-source-owner.js';
import type {CoreCommerceSemanticOwner,CoreCommerceSemanticCapture} from './commerce-core-semantic-owner.js';
import type {CommerceApplicationAssemblyV1} from './commerce-application-assembly-v1.js';

export class CoreCommerceFormalExactBindingErrorV1 extends Error {
 constructor(readonly code:'ForeignApplication'|'UnknownReference'){
  super(code);this.name='CoreCommerceFormalExactBindingErrorV1';
 }
}

export class CoreCommerceFormalExactRequestErrorV1 extends Error {
 readonly code='UnsupportedTranslation' as const;
 readonly scope='complete-selected-semantics-of-same-admitted-application' as const;
 readonly missing_semantics=Object.freeze([
  'all-admitted-byte-object-and-shared-buffer-validation',
  'byte-to-utf8-and-json-parser-outcome-including-escapes-unicode-duplicates-and-depth-priority',
  'all-input-validation-and-fuel-error-priorities',
  'complete-expression-and-output-failure-budgets',
  'complete-operation-control-argument-failure-and-action-execution',
  'native-transaction-precondition-outcomes-commit-rollback-and-disposition-proof',
  'event-outbox-and-interservice-effect-equivalence',
  'temporal-guards-observations-persistence-and-recovery',
  'generated-native-equivalence',
 ] as const);
 constructor(readonly application:string,readonly selector:string,
  readonly source_capture_sha256:string,readonly executable_sha256:string){
  super('UnsupportedTranslation: complete checked Commerce behavior is not yet translated');
  this.name='CoreCommerceFormalExactRequestErrorV1';}
}

/** Recheck the exact selected application before rejecting; no unbound or
 * stale source may be mistaken for a partial formal answer. */
export function requireCoreCommerceExactFormalModelV1(
 sources:CoreCommerceSourceOwner,capture:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 assembly:CommerceApplicationAssemblyV1,selector:string,
):never {
 sources.assertCurrent(capture);semantics.assertSource(semantic,capture);assembly.assertCurrent();
 const source=sources.inspect(capture),checked=semantics.inspect(semantic),selected=assembly.inspect();
 if(source.capture_sha256!==checked.source_capture_sha256||
  source.capture_sha256!==selected.source_capture_sha256||
  checked.application!==selected.application)throw new CoreCommerceFormalExactBindingErrorV1('ForeignApplication');
 const role=(row:{readonly module:string;readonly name:string})=>`${row.module}.${row.name}`;
 const declared=checked.pure.declarations.some(row=>row.name===selector)||
  checked.reads.some(row=>role(row.query)===selector)||
  checked.effects.some(row=>role(row.operation)===selector)||
  checked.workflows.some(row=>role(row.workflow)===selector)||
  checked.entries.some(row=>row.id===selector);
 if(!declared)throw new CoreCommerceFormalExactBindingErrorV1('UnknownReference');
 sources.assertCurrent(capture);semantics.assertSource(semantic,capture);assembly.assertCurrent();
 throw new CoreCommerceFormalExactRequestErrorV1(
  selected.application,selector,source.capture_sha256,checked.executable_sha256);
}
