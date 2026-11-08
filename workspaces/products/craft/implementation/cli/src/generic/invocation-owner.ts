/** Original SDK parent -> one-use typed invocation and protected read composition.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import type {CommerceAuthNativeOwnerV1} from '../commerce/commerce-auth-ready-bridge-v1.js';
import type {GenericCompositionHandle} from './public-sdk.js';
import type {GenericEntryPlanHandle} from './repository-plan.js';
import type {GenericEntryResultV1,GenericAuthFaultV1} from './query-data-v1.js';
import type {GenericAccessResult,GenericFixtureActor} from './entry-authorization.js';
import type {DemoPayRawHttpPort} from './external-write-runtime.js';
import type {GenericEventRelayOwner} from './event-relay.js';
export interface GenericPreparedInput{readonly kind:'original-generic-prepared-input/v1-candidate'}
export interface GenericInvocationAuthorization{readonly kind:'original-generic-invocation-authorization/v1-candidate'}
export interface GenericInvocationTransfer{readonly kind:'original-generic-invocation-transfer/v1-candidate'}
export interface GenericRuntimeOptions{readonly service:string;readonly storePath:string;readonly mode:'create'|'reopen';readonly nativeAuth:CommerceAuthNativeOwnerV1;readonly externalWritePort?:DemoPayRawHttpPort}
export type GenericRuntimeAccessResult<T>={readonly ok:true;readonly value:T}|{readonly ok:false;readonly error:GenericAuthFaultV1;readonly fuel_used:number};
export interface GenericApplicationRuntime{
 entry(id:string):GenericEntryPlanHandle;
 prepareInput(entry:GenericEntryPlanHandle,wire:Uint8Array):GenericPreparedInput;
 authorize(actor:GenericFixtureActor|null,prepared:GenericPreparedInput):Promise<GenericRuntimeAccessResult<GenericInvocationAuthorization>>;
 consume(authorization:GenericInvocationAuthorization,prepared:GenericPreparedInput):Promise<GenericRuntimeAccessResult<GenericInvocationTransfer>>;
 execute(transfer:GenericInvocationTransfer):Promise<GenericEntryResultV1>;
 inspectPrepared(prepared:GenericPreparedInput):Readonly<{state:string;fuel_used:number;entry:string;canonical_input_sha256:string}>;
 disposePrepared(prepared:GenericPreparedInput):void;
 inspect():Readonly<Record<string,unknown>>;
 assertCurrent():void;
 close():Promise<void>;
}
export {GenericInputPreparationError} from './execution-session.js';
export async function createGenericApplicationRuntime(owner:unknown,handle:GenericCompositionHandle,options:GenericRuntimeOptions):Promise<GenericApplicationRuntime|GenericTransactionApplicationRuntime>{const {createGenericRuntimeSession}=await import('./execution-session.js');return createGenericRuntimeSession(owner,handle,options);}

import {types as host} from 'node:util';
import {assertCommerceAuthNativeOwnerV1} from '../commerce/commerce-auth-ready-bridge-v1.js';
import {coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
export function captureGenericRuntimeOptions(proposal:GenericRuntimeOptions):GenericRuntimeOptions{const at={path:'generic-runtime-options',start:0,end:0};if(host.isProxy(proposal)||!proposal||typeof proposal!=='object'||Array.isArray(proposal))fail('InvalidContract',at,'closed runtime options required');const ds=Object.getOwnPropertyDescriptors(proposal),keys=Reflect.ownKeys(proposal);if((keys.length!==4&&keys.length!==5)||keys.some(k=>typeof k!=='string'||!['service','storePath','mode','nativeAuth','externalWritePort'].includes(k))||Object.values(ds).some(d=>!d.enumerable||!Object.hasOwn(d,'value')))fail('InvalidContract',at,'plain runtime option values required');const {service,storePath,mode,nativeAuth,externalWritePort}=proposal;if(typeof service!=='string'||typeof storePath!=='string'||!['create','reopen'].includes(mode))fail('InvalidContract',at,'closed runtime selection required');if(externalWritePort!==undefined){if(host.isProxy(externalWritePort)||!externalWritePort||typeof externalWritePort!=='object'||Array.isArray(externalWritePort))fail('InvalidContract',at,'original external write port required');const port=Object.getOwnPropertyDescriptor(externalWritePort,'exchange');if(!port||!Object.hasOwn(port,'value')||typeof port.value!=='function')fail('InvalidContract',at,'raw HTTP exchange function required');}assertCommerceAuthNativeOwnerV1(nativeAuth);return Object.freeze({...{service,storePath,mode,nativeAuth},...(externalWritePort===undefined?{}:{externalWritePort})});}

/** Additive command surface. The actual session implements this only in B5. */
import type {GenericCommandMetadataV1,GenericCommandResultV1,GenericCommandInspectionV1} from './transaction-data-v1.js';
export interface GenericPreparedCommand{readonly kind:'original-generic-prepared-command/v1-candidate'}
export interface GenericCommandAuthorization{readonly kind:'original-generic-command-authorization/v1-candidate'}
export interface GenericCommandTransfer{readonly kind:'original-generic-command-transfer/v1-candidate'}
export interface GenericTransactionApplicationRuntime extends GenericApplicationRuntime{
 openEventRelay():GenericEventRelayOwner;
 prepareCommand(entry:GenericEntryPlanHandle,wire:Uint8Array,metadata:GenericCommandMetadataV1):GenericPreparedCommand;
 inspectTransferredCommandIdentity(transfer:GenericCommandTransfer):Readonly<{command_tuple_sha256:string;canonical_input_sha256:string}>;
 authorize(actor:GenericFixtureActor|null,prepared:GenericPreparedInput):Promise<GenericRuntimeAccessResult<GenericInvocationAuthorization>>;
 authorize(actor:GenericFixtureActor|null,prepared:GenericPreparedCommand):Promise<GenericRuntimeAccessResult<GenericCommandAuthorization>>;
 consume(auth:GenericInvocationAuthorization,prepared:GenericPreparedInput):Promise<GenericRuntimeAccessResult<GenericInvocationTransfer>>;
 consume(auth:GenericCommandAuthorization,prepared:GenericPreparedCommand):Promise<GenericRuntimeAccessResult<GenericCommandTransfer>>;
 executeCommand(transfer:GenericCommandTransfer):Promise<GenericCommandResultV1>;
 inspectCommand(transfer:GenericCommandTransfer):Promise<GenericCommandInspectionV1>;
 /** Original-session attestation for a fresh failed command. Replayed results
  * and caller-constructed result objects never prove absence of provider effect. */
 provesProviderNoEffect(result:GenericCommandResultV1):boolean;
 inspectPrepared(prepared:GenericPreparedInput|GenericPreparedCommand):Readonly<{state:string;fuel_used:number;entry:string;canonical_input_sha256:string}>;
 disposePrepared(prepared:GenericPreparedInput|GenericPreparedCommand):void;
}

export class GenericCommandPreparationError extends Error{constructor(readonly code:'MissingCommandIdentity'){super(code);this.name='GenericCommandPreparationError';}}
export function captureGenericCommandMetadata(value:GenericCommandMetadataV1):GenericCommandMetadataV1{const at={path:'generic-command-metadata',start:0,end:0};if(host.isProxy(value)||!value||typeof value!=='object'||Array.isArray(value))fail('InvalidContract',at,'closed own-data command metadata required');const prototype=Object.getPrototypeOf(value);if(prototype!==Object.prototype&&prototype!==null)fail('InvalidContract',at,'local plain or null-map command metadata required');const keys=Reflect.ownKeys(value),ds=Object.getOwnPropertyDescriptors(value);if(keys.length!==1||keys[0]!=='client_key'||!ds.client_key?.enumerable||!Object.hasOwn(ds.client_key,'value')||typeof ds.client_key.value!=='string')fail('InvalidContract',at,'exact client_key string required');const key=ds.client_key.value;let scalars=0;for(let i=0;i<key.length;i++){const n=key.charCodeAt(i);if(n>=0xd800&&n<=0xdbff){const low=key.charCodeAt(++i);if(!(low>=0xdc00&&low<=0xdfff))fail('InvalidContract',at,'unpaired command-key surrogate');}else if(n>=0xdc00&&n<=0xdfff)fail('InvalidContract',at,'unpaired command-key surrogate');scalars++;}if(scalars<1||scalars>128||Buffer.byteLength(key,'utf8')>128)fail('InvalidContract',at,'bounded nonempty UTF8 command key required');return Object.freeze({client_key:key});}
