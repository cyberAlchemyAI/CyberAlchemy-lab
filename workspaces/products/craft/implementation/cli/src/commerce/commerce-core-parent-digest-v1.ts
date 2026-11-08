/** Fast canonical digest for Core-owned filesystem ancestor identities.
 * This is exactly dataDigest(rows) for the closed ParentIdentity shape. It
 * changes serialization cost, not which physical identities are checked.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {createHash} from 'node:crypto';
import {types as host} from 'node:util';

export type CoreParentIdentityV1=Readonly<{
 path:string;device:string;inode:string;mode:string;link:string|null;
}>;

export class CoreParentDigestErrorV1 extends TypeError {
 constructor(readonly code:string){super(code);this.name='CoreParentDigestErrorV1';}
}
const bad=(code:string):never=>{throw new CoreParentDigestErrorV1(code);};
const fields=['path','device','inode','mode','link'] as const;

/** Internal hot path. Its precondition is a dense array of rows constructed by
 * Core's parentIdentity() from lstat/readlink: path and link are strings,
 * device/inode/mode are String(BigInt) decimal values, and no row is mutable
 * caller input. The owner still performs all filesystem currentness checks. */
export function coreParentIdentityDigestTrustedV1(rows:readonly CoreParentIdentityV1[]):string {
 const serialized=rows.map(row=>'{"device":"'+row.device+'","inode":"'+row.inode+'","link":'+
  (row.link===null?'null':JSON.stringify(row.link))+',"mode":"'+row.mode+'","path":'+
  JSON.stringify(row.path)+'}');
 return createHash('sha256').update('['+serialized.join(',')+']').digest('hex');
}

/** `captureJson` accepts plain inert objects and dense arrays. Recheck those
 * properties without its recursive copy because every member has a fixed
 * primitive type and the canonical key order is known in advance. */
export function coreParentIdentityDigestV1(rows:readonly CoreParentIdentityV1[]):string {
 if(host.isProxy(rows)||!Array.isArray(rows)||Object.getPrototypeOf(rows)!==Array.prototype||
   rows.length>10000||Reflect.ownKeys(rows).length!==rows.length+1)bad('InvalidParents');
 let bytes=0;
 for(let i=0;i<rows.length;i++){
  const element=Object.getOwnPropertyDescriptor(rows,String(i));
  if(!element||!element.enumerable||!Object.hasOwn(element,'value'))bad('InvalidParents');
  const row:unknown=element!.value;
  if(!row||typeof row!=='object'||host.isProxy(row)||
    ![Object.prototype,null].includes(Object.getPrototypeOf(row))||
    Reflect.ownKeys(row).length!==fields.length)bad('InvalidParent');
  const descriptors=Object.getOwnPropertyDescriptors(row);
  for(const name of fields){
   const descriptor=descriptors[name];
   if(!descriptor||!descriptor.enumerable||!Object.hasOwn(descriptor,'value')||
     (name==='link'?descriptor.value!==null&&typeof descriptor.value!=='string':typeof descriptor.value!=='string')||
     (name==='device'||name==='inode'||name==='mode')&&
       !/^(0|[1-9][0-9]*)$/.test(descriptor.value as string))
    bad('InvalidParent');
   bytes+=Buffer.byteLength(name)+(descriptor!.value===null?0:
    name==='device'||name==='inode'||name==='mode'?(descriptor!.value as string).length:Buffer.byteLength(descriptor!.value));
   if(bytes>16777216)bad('ParentBudget');
  }
  // Every own key was counted above; symbols, accessors and extra fields are
  // rejected rather than silently ignored by this specialized digest.
 }
 return coreParentIdentityDigestTrustedV1(rows);
}
