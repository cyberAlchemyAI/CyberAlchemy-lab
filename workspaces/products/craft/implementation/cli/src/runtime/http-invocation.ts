/** ISB-02 D45 candidate dependency; Open Questions: ../../OUTBOUND-COMPOSITION.md. */
export type InvocationJson = null | boolean | number | string | readonly InvocationJson[] | {readonly [key:string]:InvocationJson};
export interface InvocationControl {readonly deadline:number; readonly signal:AbortSignal}
export interface BindingIdentity {readonly id:string; readonly version:string}
export interface HttpExchange {readonly status:number; readonly mediaType:string; readonly body:AsyncIterable<Uint8Array>}
export interface HttpAttempt {
 readonly response:Promise<HttpExchange>;
 /** Actual resource custody ended, independently of the caller's local outcome. */
 readonly settled:Promise<void>;
 cancel(reason:'cancelled'|'deadline'|'invalid-response'):Promise<void>;
}
export interface HttpInvocation {sendOnce(binding:BindingIdentity,body:InvocationJson,control:InvocationControl):HttpAttempt}

/** Explicit operator binding policy. No-auth is confined to numeric loopback.
 * Open Questions: ../../OUTBOUND-COMPOSITION.md.
 */
export interface HttpBindingPolicy {scope:'https'|'loopback'; authentication:'bearer'|'none'}
export function validateHttpBindingPolicy(value:unknown):HttpBindingPolicy {
 const p=value as HttpBindingPolicy;
 if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).sort().join(',')!=='authentication,scope'||
 !['https','loopback'].includes(p.scope)||!['bearer','none'].includes(p.authentication)||
 p.authentication==='none'&&p.scope!=='loopback')throw Error('INVALID_BINDING_POLICY');
 return {scope:p.scope,authentication:p.authentication};
}
