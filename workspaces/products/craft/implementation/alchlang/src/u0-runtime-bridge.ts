import type {BusinessSourceCapture} from './business-authoring-protocol.js';
import type {BusinessCaptureIdentityV2,AuthoringBusinessInputV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessCoreRecipeOwnerV2,BusinessRequestStagesOwnerV2,BusinessPureGenerationOwnerV2,BusinessDirectApplicationOwnerV2,BusinessCoverageViewsOwnerV2,BusinessOutputWriterOwnerV2,BusinessOutputArtifactInputV2,CheckedDirectApplicationV2,BoundU0EntryV2,BusinessCheckedViewsV2} from './business-authoring-stages-v2.js';
import type {BusinessInputOwnerV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessOutputPlanV2} from './business-authoring-coverage-contract-v2.js';
import type {U0ResolvedNativeBasis} from './u0-realization-contract.js';
import type {DirectBusinessReviewOwnerV2} from './business-authoring-review.js';
/** Structural public SDK consumption only. Runtime registries remain Core-owned.
 * Open Questions: later selected/native/installed qualification. */
export interface U0RuntimeBridgeV4 {
 readonly kind:'business-u0-runtime-v4';readonly basis:U0ResolvedNativeBasis;
 readonly recipes:BusinessCoreRecipeOwnerV2;readonly reviews:DirectBusinessReviewOwnerV2;
 readonly requests:BusinessRequestStagesOwnerV2;readonly inputs:BusinessInputOwnerV2;
 readonly applications:BusinessDirectApplicationOwnerV2;readonly generation:BusinessPureGenerationOwnerV2;
 readonly views:BusinessCoverageViewsOwnerV2;
 readonly output:BusinessOutputWriterOwnerV2 & {prepareArtifacts(plan:BusinessOutputPlanV2,application:CheckedDirectApplicationV2,bound:BoundU0EntryV2,views:BusinessCheckedViewsV2):readonly BusinessOutputArtifactInputV2[]};
 captureSource(modelId:string,root:string,relative:string):Readonly<{source:BusinessSourceCapture;capture:BusinessCaptureIdentityV2}>;
 registerProject(input:AuthoringBusinessInputV2,root:string):unknown;
 assertCurrent():void;dispose():void;
}
