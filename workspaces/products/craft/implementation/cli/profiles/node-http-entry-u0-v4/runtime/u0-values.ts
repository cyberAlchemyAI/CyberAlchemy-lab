import {types} from 'node:util';
import type {U0Submission} from '../../../src/profile-engine/u0-realization-contract.js';
import type {U0DecodedWireRecord} from './u0-json-decode.js';

/** U0 exact boundary. Scalar support is materialized verbatim from
 * src/generation/configured-exact-uint64-source.ts; the test checks parity.
 * Open Questions: U06c/U07 and J01 real native packaging/capture. */
type ValueProtocol<T> = Readonly<{normalize(input:unknown):T;key(value:T):string}>;
const part=(value:string):string=>value.length+':'+value;
const uint64Value:ValueProtocol<bigint> = Object.freeze({
  normalize:(input:unknown):bigint=>{
    let value:bigint;
    if(typeof input === 'bigint') value=input;
    else if(typeof input === 'number' && Number.isSafeInteger(input)) value=BigInt(input);
    else if(typeof input === 'string' && input.length <= 20 && /^(0|[1-9][0-9]*)$/.exec(input)?.[0] === input) value=BigInt(input);
    else throw new TypeError('INVALID_UINT64');
    if(value < 0n || value > 18446744073709551615n) throw new TypeError('INVALID_UINT64');
    return value;
  },
  key:(value:bigint):string=>part('UInt64') + part(String(value)),
});
export type U0ValueCode='U0_VALUE_SHAPE'|'U0_VALUE_DECIMAL'|'U0_VALUE_RANGE'|'U0_VALUE_NATIVE';
export class U0ValueError extends TypeError {
 constructor(readonly code:U0ValueCode){super(code);this.name='U0ValueError';}
}
function fail(code:U0ValueCode):never{throw new U0ValueError(code);}
function fields(input:unknown):Readonly<{id:unknown;verified:boolean}> {
 if(!input||typeof input!=='object'||types.isProxy(input)||Array.isArray(input))fail('U0_VALUE_SHAPE');
 const prototype=Object.getPrototypeOf(input);
 if(prototype!==null&&prototype!==Object.prototype)fail('U0_VALUE_SHAPE');
 const keys=Reflect.ownKeys(input);
 if(keys.length!==2||!keys.includes('id')||!keys.includes('verified'))fail('U0_VALUE_SHAPE');
 const descriptors=Object.getOwnPropertyDescriptors(input);
 const id=descriptors.id,verified=descriptors.verified;
 if(!id||!verified||!Object.hasOwn(id,'value')||!Object.hasOwn(verified,'value')||!id.enumerable||!verified.enumerable||typeof verified.value!=='boolean')fail('U0_VALUE_SHAPE');
 return {id:id.value,verified:verified.value};
}
function owned(id:bigint,verified:boolean):U0Submission {
 return Object.freeze(Object.assign(Object.create(null) as U0Submission,{id,verified}));
}
/** No Number conversion; the finite canonical range is checked before BigInt. */
export function formU0Submission(record:U0DecodedWireRecord):U0Submission {
 const value=fields(record),decimal=value.id;
 if(typeof decimal!=='string'||decimal.length===0||decimal.length>20)fail('U0_VALUE_DECIMAL');
 if(decimal==='0')return owned(uint64Value.normalize(decimal),value.verified);
 if(decimal.charCodeAt(0)<49||decimal.charCodeAt(0)>57)fail('U0_VALUE_DECIMAL');
 for(let i=1;i<decimal.length;i++)if(decimal.charCodeAt(i)<48||decimal.charCodeAt(i)>57)fail('U0_VALUE_DECIMAL');
 if(decimal.length===20&&decimal>'18446744073709551615')fail('U0_VALUE_RANGE');
 return owned(uint64Value.normalize(decimal),value.verified);
}
/** The pure native ABI is bigint + Boolean, even when the shared helper is wider. */
export function copyU0Submission(input:U0Submission):U0Submission {
 const value=fields(input);
 if(typeof value.id!=='bigint')fail('U0_VALUE_NATIVE');
 if(value.id<0n||value.id>18446744073709551615n)fail('U0_VALUE_RANGE');
 return owned(uint64Value.normalize(value.id),value.verified);
}
