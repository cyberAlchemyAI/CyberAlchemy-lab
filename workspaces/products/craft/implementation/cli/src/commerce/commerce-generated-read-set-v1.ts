/** Source-bound lifetime for generated read-set validation. Reads may observe
 * changing rows; the subsequent transaction must CAS every captured version.
 * This owner only prevents a write before the generated read-set unwinds.
 * Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md#open-questions. */
import {types as host} from 'node:util';

type Site=Readonly<{kind?:unknown;before_writes?:unknown}>;
type Lease=Readonly<{kind:'original-generated-read-set-lease/v1-candidate'}>;
type Row={path:string;closed:boolean};

function fail(code:string):never {const error=new Error(code);Object.assign(error,{code});throw error;}

/** `sites` comes from one already checked generated Operation manifest. The
 * lexical source path and one-use lease are never supplied by the caller. */
export function createCommerceGeneratedReadSetScopeV1(sites:Readonly<Record<string,unknown>>,assertCurrent:()=>void){
 if(!sites||typeof sites!=='object'||Array.isArray(sites)||host.isProxy(sites)||typeof assertCurrent!=='function')fail('InvalidContract');
 const leases=new WeakMap<object,Row>(),stack:Lease[]=[];
 const site=(path:string):Site=>{
  if(typeof path!=='string'||path.length>8192||!Object.hasOwn(sites,path))fail('UnknownSourcePath');
  const row=sites[path];if(!row||typeof row!=='object'||Array.isArray(row)||host.isProxy(row))fail('UnknownSourcePath');
  return row as Site;
 };
 const active=()=>stack.length?leases.get(stack[stack.length-1]!):undefined;
 return Object.freeze({
  open(path:string):Lease{
   assertCurrent();const declared=site(path),parent=active();
   if(declared.kind!=='read-set'||declared.before_writes!==true||parent&&!path.startsWith(parent.path+'.body['))fail('ForeignScope');
   const lease=Object.freeze({kind:'original-generated-read-set-lease/v1-candidate' as const});
   leases.set(lease,{path,closed:false});stack.push(lease);return lease;
  },
  assertRead(path:string){
   assertCurrent();const declared=site(path),parent=active();
   if(declared.kind!=='read'||parent&&!path.startsWith(parent.path+'.body['))fail('ForeignScope');
  },
  assertWritable(){assertCurrent();if(stack.length)fail('ReadSetStillOpen');},
  close(lease:unknown){
   assertCurrent();const row=lease&&typeof lease==='object'?leases.get(lease):undefined;
   if(!row||row.closed||stack[stack.length-1]!==lease)fail('ForeignScope');
   stack.pop();row.closed=true;
  },
  assertReleased(){assertCurrent();if(stack.length)fail('ReadSetStillOpen');},
 });
}
