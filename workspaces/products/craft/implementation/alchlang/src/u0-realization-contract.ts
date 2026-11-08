// GENERATED from Core u0-realization-contract.ts; canonical owner is Core.
/** Data/configuration/native ABI contracts, not checked handles or resolved future assets.
 * Open Questions: docs/U0-NATIVE-CONTRACT.md. */
export const U0_WIRE_CONTRACT = 'craft.operation-json-post/v2-candidate' as const;
export const U0_NATIVE_ABI = 'craft.u0.pure-submission/v1-candidate' as const;
export const U0_SUCCESSOR_DESCRIPTOR = 'node-http-entry-u0-v4' as const;
export const U0_WIRE_CODEC = 'canonical-decimal-string' as const;
export const U0_MAX_UINT64 = 18446744073709551615n;
export const U0_CONFIG_EXAMPLE = Object.freeze({schema_version:U0_WIRE_CONTRACT,method:'POST',pathname:'/confirm-delivery',body:'closed-submission',uint64_codec:U0_WIRE_CODEC,request_bytes:4096,response_bytes:1024,body_timeout_ms:2000} as const);
/** Independent literal maxima of the selected canonical wire encodings. */
export const U0_CANONICAL_MAX_BYTES = Object.freeze({request:46,completed:74,rejected:59});
const U0_ADAPTER_FAILURE_TABLE = [
 {code:'route-not-found',status:404}, {code:'method-not-allowed',status:405},
 {code:'unsupported-media-type',status:415}, {code:'request-aborted',status:400},
 {code:'request-too-large',status:413}, {code:'body-timeout',status:408},
 {code:'body-read-failed',status:400}, {code:'invalid-request',status:400},
 {code:'adapter-contract-defect',status:500},
] as const;
export const U0_ADAPTER_FAILURES = Object.freeze(U0_ADAPTER_FAILURE_TABLE.map(row=>Object.freeze(row)));
export type U0AdapterFailureCode = typeof U0_ADAPTER_FAILURES[number]['code'];
export interface U0WireConfiguration {
 readonly schema_version:typeof U0_WIRE_CONTRACT;readonly method:'POST';readonly pathname:'/confirm-delivery';
 readonly body:'closed-submission';readonly uint64_codec:typeof U0_WIRE_CODEC;
 readonly request_bytes:number;readonly response_bytes:number;readonly body_timeout_ms:number;
}
export interface U0Submission {readonly id:bigint;readonly verified:boolean}
export type U0ProcessOutcome<Code extends string='delivery-verification-required'> =
 | Readonly<{kind:'completed';value:U0Submission}>
 | Readonly<{kind:'rejected';code:Code}>;
export type U0PureInvoke<Code extends string='delivery-verification-required'> = (input:U0Submission)=>U0ProcessOutcome<Code>;
export type U0InjectedHandler = (request:Request)=>Promise<Response>;
export interface U0NativeRequirement {
 readonly kind:'native-requirement';readonly artifact_id:string;readonly origin:'runtime-builtin'|'registered-package';
 readonly version:Readonly<{comparison:'exact';value:string}>;readonly abi:string;
 readonly required_exports:readonly string[];readonly supplying_runtime:string;readonly authority_effect:'none';
}
export interface U0ResolvedArtifact {
 readonly kind:'resolved-native-artifact';readonly requirement:U0NativeRequirement;
 readonly resolved_version:string;readonly sha256:string;readonly bytes:number;
 readonly exports:readonly string[];readonly runtime_sha256:string;readonly platform:string;readonly architecture:string;
 readonly authority_effect:'none';
}
/** A basis is resolved only after actual SDK/codec/handler bytes exist; it excludes generated application bytes. */
export interface U0ResolvedNativeBasis {
 readonly kind:'resolved-u0-native-basis';readonly abi:typeof U0_NATIVE_ABI;readonly descriptor:typeof U0_SUCCESSOR_DESCRIPTOR;
 readonly artifacts:readonly U0ResolvedArtifact[];readonly configuration:U0WireConfiguration;
 readonly sdk_sha256:string;readonly basis_sha256:string;readonly authority_effect:'none';
}
/** Created only by the late binding owner after actual code emission, never by this type declaration. */
export interface U0RealizedApplicationSubject {
 readonly kind:'realized-u0-application';readonly executable_sha256:string;readonly capture_sha256:string;
 readonly basis_sha256:string;readonly callable_sha256:string;readonly request_graph_sha256:string;
 readonly handler_sha256:string;readonly realized_sha256:string;readonly authority_effect:'none';
}
export interface U0NativeObservation {
 readonly kind:'u0-native-observation';readonly producer:Readonly<{id:string;sha256:string}>;
 readonly subject:Readonly<{kind:'native-basis'|'realized-application';sha256:string}>;
 readonly environment:Readonly<{runtime:string;platform:string;architecture:string}>;
 readonly outcome:'passed'|'failed'|'not-observed';readonly evidence_sha256:string;readonly authority_effect:'none';
}
