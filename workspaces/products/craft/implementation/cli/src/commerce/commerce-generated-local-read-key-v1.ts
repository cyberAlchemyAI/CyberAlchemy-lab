/** Select the exact declared Entity identity/unique key for a generated local
 * read. The checked source owns the key order; a caller cannot choose an index.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {types as host} from 'node:util';
import {dataDigest} from '../profile-engine/contracts.js';
import type {ValueSchemaV1,OperationControlStepV1} from './commerce-data-v1.js';
import type {CommerceNativeValue} from './commerce-native-v1.js';

export function selectCommerceGeneratedLocalReadKeyIndexV1(
 values:ValueSchemaV1,read:Extract<OperationControlStepV1,{kind:'read'}>,
 actualKey:Readonly<Record<string,CommerceNativeValue>>,
):number {
 if(read.entity===null||read.call!==null||read.key===null||
  !actualKey||typeof actualKey!=='object'||Array.isArray(actualKey)||host.isProxy(actualKey)||
  ![Object.prototype,null].includes(Object.getPrototypeOf(actualKey)))
  throw new Error('original local read and closed key required');
 const entities=values.records.filter(record=>record.name===read.entity&&record.role==='Entity'&&record.entity!==null);
 if(entities.length!==1||entities[0]!.entity===null)
  throw new Error('one checked local read Entity required');
 const declared=[entities[0]!.entity.identity,...entities[0]!.entity.unique],fields=read.key.key;
 const indexes=declared.flatMap((key,index)=>dataDigest(key)===dataDigest(fields)?[index]:[]);
 const descriptors=Object.getOwnPropertyDescriptors(actualKey),names=Reflect.ownKeys(actualKey);
 if(indexes.length!==1||!fields.length||names.length!==fields.length||
  names.some(name=>typeof name!=='string'||!fields.includes(name))||
  fields.some(name=>!descriptors[name]?.enumerable||!Object.hasOwn(descriptors[name]!,'value')))
  throw new Error('source local read must use exactly one declared Entity identity or unique key');
 return indexes[0]!;
}
