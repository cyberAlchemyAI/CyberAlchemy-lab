/** Generated Query observations are the authority. Selection data only locates
 * owned opaque leases; no serialized preference/grant mints an observation.
 * Open Questions: README.md. */
import {assert,capture,canonical,closed,sha256,text,u64} from '../shared.mjs';

/** Static `inputs` retains its original records view. `subjectInputs` selects one
 * bounded Query input from prefix + canonical UInt64 subject without a lookup
 * table. The optional single-record view correlates payload identity separately
 * from the opaque Query revision used by the original source/release owners. */
export async function createApplicationQuerySource({composition,handle,runtime,actor,entry,releaseAuthority,adapterId,inputs,subjectInputs,resultView,collectionField='records',classifications=['internal'],deadlineMs=3600000}){
 const core=await import('@domainspec-v2/cli/generic');
 assert(typeof core.createGenericQueryObservationOwner==='function','UnsupportedCapability','original protected Query observation owner required');
 const dynamic=subjectInputs===undefined?null:closed(subjectInputs,['prefix','inputField']);
 assert(dynamic?inputs===undefined:inputs instanceof Map&&inputs.size>0&&inputs.size<=100,'InvalidContract','exactly one bounded static or subject input selection');
 const field=value=>{text(value,'bounded Query field',64);assert(/^[A-Za-z_][A-Za-z0-9_]*$/.test(value)&&!['__proto__','prototype','constructor'].includes(value),'InvalidContract','single Query field name');return value;};
 if(dynamic){text(dynamic.prefix,'source subject prefix',128);field(dynamic.inputField);}
 const view=resultView===undefined?null:closed(resultView,['kind','identityField']);
 if(view){assert(view.kind==='single-record'&&collectionField==='records','InvalidContract','exact single-record source view');field(view.identityField);}
 for(const x of [entry,adapterId,collectionField])text(x);
 const selectedClassifications=capture([...classifications]);
 assert(Number.isSafeInteger(deadlineMs)&&deadlineMs>0&&deadlineMs<=3600000,'InvalidContract','finite source lease deadline');
 const selected=dynamic?null:new Map([...inputs].map(([id,values])=>{
  text(id);assert(Array.isArray(values)&&values.length>0&&values.length<=16,'InvalidContract','bounded source query group');
  return [id,capture(values)];
 }));
 const owner=core.createGenericQueryObservationOwner(composition,handle,runtime),heads=new Map();let isClosed=false,registration;
 const current=()=>{assert(!isClosed,'StaleOwner','generated Query source closed');registration?.assertCurrent?.();if(typeof core.assertGenericApplicationRuntime==='function')core.assertGenericApplicationRuntime(runtime);else runtime.assertCurrent();};
 function selection(id){
  if(dynamic){assert(id.startsWith(dynamic.prefix),'SourceUnavailable','selected source subject prefix');const subject=id.slice(dynamic.prefix.length);u64(subject);return {queries:[{[dynamic.inputField]:subject}],subject};}
  const queries=selected.get(id);assert(queries,'SourceUnavailable','selected original Query source id');
  let subject=null;
  if(view){assert(queries.length===1&&queries[0]&&typeof queries[0]==='object'&&!Array.isArray(queries[0])&&Object.hasOwn(queries[0],view.identityField),'InvalidContract','single-record input must select its identity');subject=queries[0][view.identityField];u64(subject);}
  return {queries,subject};
 }
 function describeRow(row,{id,tenant,principal}){
  current();assert(row&&row.tenant===tenant&&row.principal===principal,'PermissionDenied','same actual generated Query reader');
  const views=row.leases.map(lease=>owner.inspect(lease));
  assert(views.every(v=>v.principal.actor===principal&&v.principal.tenant===tenant),'ForeignOwner','same original source principal');
  let value;
  if(view){
   assert(views.length===1,'InvalidContract','exactly one source Query observation');const record=views[0].value;
   assert(record&&typeof record==='object'&&!Array.isArray(record)&&Object.hasOwn(record,view.identityField),'SourceUnavailable','non-null source record with selected identity');
   u64(record[view.identityField]);assert(record[view.identityField]===row.subject,'ForeignOwner','source record matches selected subject');
   value={record};
  }else value={[collectionField]:views.map(v=>v.value)};
  const bytes=new TextEncoder().encode(canonical(value));
  return {id,tenant,sha256:sha256(bytes),revision:sha256(canonical(views.map(v=>({query:v.query,source:v.source_revision,input:v.input_sha256,content:v.content_sha256})))),aclRevision:sha256(canonical(views.map(v=>v.principal))),readers:[principal],classifications:[...selectedClassifications],mediaType:'application/json',bytes};
 }
 const describe=request=>describeRow(heads.get(request.id),request);
 const port=Object.freeze({abi:'craft.generated-query-source/v1',adapterId,
  async read({id,tenant,principal}){
   current();for(const x of [id,tenant,principal])text(x);
   const {queries,subject}=selection(id),leases=[];
   try{
    for(const input of queries){
     const lease=await owner.read(actor,entry,new TextEncoder().encode(canonical(input)),{deadline_ms:Date.now()+deadlineMs});leases.push(lease);
     current();const observed=owner.inspect(lease);assert(observed.principal.actor===principal&&observed.principal.tenant===tenant&&observed.value!==null,'PermissionDenied','actual source Query principal/value required');
    }
    for(const lease of leases)owner.assertCurrent(lease);
    const next={tenant,principal,leases,subject},value=describeRow(next,{id,tenant,principal}),old=heads.get(id);
    assert(old||heads.size<100,'ResourceLimit','bounded retained source observations');
    // Do not publish a failed normalization or replace a valid head before all
    // original owner checks succeed. Concurrent refreshes retire their real old lease.
    heads.set(id,next);if(old)for(const lease of old.leases)owner.retire(lease);return value;
   }catch(error){for(const lease of leases)owner.retire(lease);throw error;}
  },
  readCurrent:describe,
  assertCurrent(){current();for(const row of heads.values())for(const lease of row.leases)owner.assertCurrent(lease);},
  close(){if(isClosed)return;isClosed=true;try{registration?.retire?.();}finally{owner.close();heads.clear();}}
 });
 try{registration=releaseAuthority.registerAdapter(adapterId,Object.freeze({readCurrent:describe}));return port;}
 catch(error){port.close();throw error;}
}
