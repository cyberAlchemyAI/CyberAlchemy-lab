/** R06 bounded SQLite FTS5 + exact native vector retrieval.
 * The document owner retains source/version/ACL authority; embedding observations
 * retain paid-effect custody. Open Questions: README.md#open-questions. */
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {types} from 'node:util';
import {assert,capture,canonical,closed,count,freeze,sha256,text} from '../shared.mjs';
import {createDocumentParser,chunkParsedDocument,PARSER_IDENTITY} from '../documents/parser/index.mjs';
export const RETRIEVAL_IDENTITY=Object.freeze({abi:'craft.embedded-retrieval/v1',indexVersion:'craft-embedded-hybrid/1.0.0',layout:1,backend:'sqlite-fts5',algorithm:'exact-cosine',strategy:'hybrid-rrf60',tokenizer:'unicode61',fusionConstant:60});
const identityKeys=['model','dimensions','preprocessing','space'];
const compareText=(a,b)=>Buffer.compare(Buffer.from(a),Buffer.from(b));
const compareRef=(a,b)=>compareText(a.sourceId,b.sourceId)||compareText(a.version,b.version)||compareText(a.chunkId,b.chunkId);
const refKey=ref=>canonical([ref.sourceId,ref.version,ref.chunkId]);
export function createRetrievalProfile({embedding,mode='local-reference'}={}){
 const representation=closed(embedding,identityKeys);for(const k of ['model','preprocessing','space'])text(representation[k],k,1024);count(representation.dimensions,'dimensions',1536);assert(representation.dimensions>0,'InvalidContract','positive embedding dimensions');
 assert(['local-reference','fixture'].includes(mode),'UnsupportedCapability','explicit supported retrieval mode');assert(mode==='fixture'||representation.dimensions===1536,'UnsupportedCapability','local reference representation is exactly1536dimensions');
 return freeze({schema:'craft.embedded-retrieval-profile/v1',mode,representation,retrieval:{strategy:RETRIEVAL_IDENTITY.strategy,fusionConstant:60},index:{backend:RETRIEVAL_IDENTITY.backend,algorithm:RETRIEVAL_IDENTITY.algorithm,version:RETRIEVAL_IDENTITY.indexVersion,tokenizer:RETRIEVAL_IDENTITY.tokenizer},limits:{documents:100,chunks:2000,dimensions:1536,topK:10,chunkChars:2000,minNorm:1e-12,maxNorm:1e6}});
}
export function validateVector(raw,dimensions){
 count(dimensions,'dimensions',1536);assert(dimensions>0,'InvalidContract','positive vector dimensions');assert(raw&&typeof raw==='object'&&!types.isProxy(raw)&&Array.isArray(raw)&&Object.getPrototypeOf(raw)===Array.prototype,'InvalidVector','dense plain vector required');
 const ds=Object.getOwnPropertyDescriptors(raw),keys=Reflect.ownKeys(ds);assert(ds.length?.value===dimensions&&keys.length===dimensions+1,'InvalidVector','exact finite vector dimensions');const vector=[];
 for(let i=0;i<dimensions;i++){const d=ds[i];assert(d?.enumerable&&Object.hasOwn(d,'value')&&typeof d.value==='number'&&Number.isFinite(d.value),'InvalidVector','finite numeric vector values required');vector.push(Object.is(d.value,-0)?0:d.value);}
 const norm=Math.hypot(...vector);assert(Number.isFinite(norm)&&norm>=1e-12&&norm<=1e6,'InvalidVector','norm must be within1e-12..1e6');return {vector,norm};
}
/** Native technical score only: no quantization and no business confidence. */
export function cosineSimilarity(left,right){
 const a=validateVector(left,left.length),b=validateVector(right,left.length);let sum=0,correction=0;
 for(let i=0;i<a.vector.length;i++){const product=(a.vector[i]/a.norm)*(b.vector[i]/b.norm),adjusted=product-correction,next=sum+adjusted;correction=(next-sum)-adjusted;sum=next;}
 return Math.max(-1,Math.min(1,sum));
}
export function fuseRanks({lexical,dense,topK=10}){
 count(topK,'topK',10);assert(topK>0,'InvalidContract','positive topK');assert(Array.isArray(lexical)&&Array.isArray(dense)&&lexical.length<=2000&&dense.length<=2000,'ResourceLimit','bounded rankings');const rows=new Map();
 for(const [kind,list] of [['lexical',lexical],['dense',dense]]){const seen=new Set();for(let i=0;i<list.length;i++){const ref=list[i];for(const k of ['sourceId','version','chunkId'])text(ref[k],k,1024);const key=refKey(ref);assert(!seen.has(key),'InvalidContract','unique ranking references');seen.add(key);let row=rows.get(key);if(!row){row={sourceId:ref.sourceId,version:ref.version,chunkId:ref.chunkId,lexicalRank:null,denseRank:null,fusionScore:0};rows.set(key,row);}row[kind+'Rank']=i+1;}}
 for(const row of rows.values())row.fusionScore=(row.lexicalRank===null?0:1/(60+row.lexicalRank))+(row.denseRank===null?0:1/(60+row.denseRank));
 return [...rows.values()].sort((a,b)=>b.fusionScore-a.fusionScore||compareRef(a,b)).slice(0,topK);
}
export function retrievalArtifactIdentity(){const files=['index.mjs','package.json'].map(path=>({path,sha256:sha256(readFileSync(new URL(path,import.meta.url)))}));return freeze({...RETRIEVAL_IDENTITY,files,artifactSha256:sha256(canonical(files)),dependencies:{parserAbi:PARSER_IDENTITY.abi,sourceAbi:'craft.document-authority/v1',embeddingAbi:'craft.embedding-observation/v1',runtime:'node26.12.1/node:sqlite'}});}
function readableQuery(query){assert(typeof query==='string'&&query.isWellFormed()&&Buffer.byteLength(query)<=4096,'InvalidContract','bounded Unicode search query');const terms=query.match(/[\p{L}\p{N}_]+/gu)??[];assert(terms.length<=32,'ResourceLimit','at most32lexical terms');return terms.length?terms.map(term=>'"'+term.replaceAll('"','""')+'"').join(' OR '):null;}
function sourceMatches(source,ref,tenant){assert(source.id===ref.id&&source.tenant===tenant&&source.revision===ref.version&&source.aclRevision===ref.acl_revision&&source.sha256===ref.sha256,'StaleOwner','indexed source version/access/content changed');}
function sameEmbedding(left,right){return canonical(left)===canonical(right);}
const originalRetrievals=new WeakMap();
export function inspectOriginalRetrieval(value){const owner=originalRetrievals.get(value);assert(owner,'ForeignOwner','original constructed retrieval');owner.current();return Object.freeze({documentPort:owner.documentPort,embeddingPort:owner.embeddingPort,parser:owner.parser,profile:owner.profile});}
export function createEmbeddedRetrieval({path,documentPort,embeddingPort,parser=createDocumentParser(),profile}={}){
 text(path,'retrieval DB path',4096);assert(documentPort?.abi==='craft.document-authority/v1'&&['read','inspectGeneration','checkpoint','activate','activeGeneration'].every(k=>typeof documentPort[k]==='function'),'ForeignOwner','original document authority port required');
 const selected=profile??createRetrievalProfile({embedding:embeddingPort?.identity});const expected=createRetrievalProfile({embedding:selected.representation,mode:selected.mode});assert(canonical(selected)===canonical(expected),'UnsupportedCapability','exact embedded profile required');
 assert(embeddingPort&&typeof embeddingPort.embed==='function'&&sameEmbedding(embeddingPort.identity,selected.representation),'UnsupportedCapability','selected original embedding observation port/identity required');assert(parser?.identity?.abi===PARSER_IDENTITY.abi&&typeof parser.parse==='function','UnsupportedCapability','selected document parser required');
 const db=new DatabaseSync(path);let ownerClosed=false,building=false;
 const existing=db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").all().map(r=>r.name).sort();
 if(existing.length){try{const allowed=['retrieval_meta','retrieval_generations','retrieval_chunks','retrieval_fts','retrieval_fts_data','retrieval_fts_idx','retrieval_fts_content','retrieval_fts_docsize','retrieval_fts_config'].sort();assert(canonical(existing)===canonical(allowed),'UnsupportedCapability','unknown retrieval store tables');assert(db.prepare('SELECT layout FROM retrieval_meta WHERE singleton=1').get()?.layout===1,'UnsupportedCapability','unsupported retrieval layout');}catch(e){db.close();throw e;}}
 db.exec(`PRAGMA busy_timeout=5000; PRAGMA journal_mode=WAL; PRAGMA synchronous=FULL;
 BEGIN IMMEDIATE;
 CREATE TABLE IF NOT EXISTS retrieval_meta(singleton INTEGER PRIMARY KEY CHECK(singleton=1),layout INTEGER NOT NULL CHECK(layout=1)) STRICT;
 INSERT OR IGNORE INTO retrieval_meta VALUES(1,1);
 CREATE TABLE IF NOT EXISTS retrieval_generations(id TEXT PRIMARY KEY,tenant TEXT NOT NULL,status TEXT NOT NULL,identity TEXT NOT NULL,profile TEXT NOT NULL) STRICT;
 CREATE UNIQUE INDEX IF NOT EXISTS retrieval_active ON retrieval_generations(tenant) WHERE status='active';
 CREATE TABLE IF NOT EXISTS retrieval_chunks(generation TEXT NOT NULL,chunk_key TEXT NOT NULL,source_id TEXT NOT NULL,version TEXT NOT NULL,acl_revision TEXT NOT NULL,source_sha256 TEXT NOT NULL,chunk_id TEXT NOT NULL,page INTEGER NOT NULL,start_offset INTEGER NOT NULL,end_offset INTEGER NOT NULL,chunk_sha256 TEXT NOT NULL,content TEXT NOT NULL,observation_id TEXT NOT NULL,vector TEXT,PRIMARY KEY(generation,chunk_key)) STRICT;
 CREATE VIRTUAL TABLE IF NOT EXISTS retrieval_fts USING fts5(content,chunk_key UNINDEXED,generation UNINDEXED,tokenize='unicode61');
 COMMIT;
 CREATE VIRTUAL TABLE temp.retrieval_authorized USING fts5(content,chunk_key UNINDEXED,tokenize='unicode61');`);
 const current=()=>{assert(!ownerClosed,'StaleOwner','retrieval owner closed');documentPort.assertCurrent?.();};
 const tx=fn=>{current();db.exec('BEGIN IMMEDIATE');try{const result=fn();db.exec('COMMIT');return result;}catch(e){if(db.isTransaction)db.exec('ROLLBACK');throw e;}};
 const inspectGeneration=(handle,principal)=>{current();text(principal,'principal');const info=documentPort.inspectGeneration(handle);assert(['building','active'].includes(info.status),'StaleOwner','generation cannot revive');assert(info.parser===parser.identity.parserVersion&&info.chunker===parser.identity.chunkerVersion&&info.index===RETRIEVAL_IDENTITY.indexVersion&&sameEmbedding(info.embedding,selected.representation),'UnsupportedCapability','generation parser/chunker/representation/index identity mismatch');assert(info.sources.length>0&&info.sources.length<=100,'ResourceLimit','document bound');for(const ref of info.sources)sourceMatches(documentPort.read({id:ref.id,tenant:info.tenant,principal}),ref,info.tenant);return info;};
 const generationBody=info=>{const {id,status,cursor,...body}=info;return body;};
 const readAuthorized=(info,principal)=>{const allowed=new Map();for(const ref of info.sources){try{const source=documentPort.read({id:ref.id,tenant:info.tenant,principal});sourceMatches(source,ref,info.tenant);allowed.set(ref.id,{source,ref});}catch(e){if(e.code==='PermissionDenied')continue;throw e;}}return allowed;};
 async function build({generation,principal,activate:promote=true}){
  assert(typeof promote==='boolean','InvalidContract','explicit technical activation mode');
  current();assert(!building,'ResourceLimit','one build at a time per index owner');building=true;
  try{
   const info=inspectGeneration(generation,principal),identity=canonical(generationBody(info)),profileIdentity=canonical(selected);
   tx(()=>{const existing=db.prepare('SELECT * FROM retrieval_generations WHERE id=?').get(info.id);if(existing)assert(existing.identity===identity&&existing.profile===profileIdentity&&existing.status!=='retired','StaleOwner','index generation identity/state drift');else{assert(db.prepare('SELECT count(*) n FROM retrieval_generations WHERE tenant=?').get(info.tenant).n<32,'ResourceLimit','retained generation bound');db.prepare("INSERT INTO retrieval_generations VALUES(?,?,'building',?,?)").run(info.id,info.tenant,identity,profileIdentity);}});
   let processed=0;const expectedKeys=new Set();
   for(const ref of info.sources){
    const source=documentPort.read({id:ref.id,tenant:info.tenant,principal});sourceMatches(source,ref,info.tenant);
    const parsed=await parser.parse({bytes:source.bytes,mediaType:source.mediaType,source:{tenant:info.tenant,sourceId:ref.id,version:ref.version}});inspectGeneration(generation,principal);
    assert(parsed.status==='parsed','DocumentReviewRequired',parsed.reason??'document did not parse');assert(parsed.sourceSha256===ref.sha256&&parsed.source.sourceId===ref.id&&parsed.source.version===ref.version&&parsed.source.tenant===info.tenant,'StaleOwner','parser result source mismatch');
    const chunks=chunkParsedDocument(parsed,{maxChars:selected.limits.chunkChars});assert(processed+chunks.length<=2000,'ResourceLimit','active chunk bound');
    for(const chunk of chunks){
     processed++;const key=refKey({sourceId:ref.id,version:ref.version,chunkId:chunk.chunkId}),digest=sha256(chunk.text),observationId=sha256(canonical({generation:info.id,key,digest,embedding:info.embedding}));assert(!expectedKeys.has(key),'InvalidContract','unique parser chunks');expectedKeys.add(key);
     let row=db.prepare('SELECT * FROM retrieval_chunks WHERE generation=? AND chunk_key=?').get(info.id,key),pending=false;
     if(row){assert(row.chunk_sha256===digest&&row.content===chunk.text&&row.observation_id===observationId,'StaleOwner','stored parser chunk changed');pending=row.vector===null;}
     else{tx(()=>{assert(db.prepare('SELECT count(*) n FROM retrieval_chunks WHERE generation=?').get(info.id).n<2000,'ResourceLimit','index chunk bound');db.prepare('INSERT INTO retrieval_chunks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)').run(info.id,key,ref.id,ref.version,ref.acl_revision,ref.sha256,chunk.chunkId,chunk.page,chunk.start,chunk.end,digest,chunk.text,observationId);});}
     if(!row?.vector){
      const request=freeze({observationId,text:chunk.text,source:{adapter:documentPort.adapterId,id:ref.id,tenant:info.tenant,version:ref.version,aclRevision:ref.acl_revision,sha256:ref.sha256},representation:info.embedding});let observation;
      if(pending){assert(typeof embeddingPort.inspect==='function','OutcomeUnknown','pending embedding requires original observation inspection');observation=await embeddingPort.inspect(request);inspectGeneration(generation,principal);assert(observation?.status==='confirmed'||observation?.status==='definitively-no-effect','OutcomeUnknown','embedding observation remains unknown');}
      if(!observation||observation.status==='definitively-no-effect'){inspectGeneration(generation,principal);observation=await embeddingPort.embed(request);inspectGeneration(generation,principal);}
      assert(observation&&Array.isArray(observation.vector),'InvalidVector','embedding observation vector required');const vector=validateVector(observation.vector,selected.representation.dimensions).vector;
      tx(()=>{db.prepare('UPDATE retrieval_chunks SET vector=? WHERE generation=? AND chunk_key=? AND vector IS NULL').run(JSON.stringify(vector),info.id,key);const inFts=db.prepare('SELECT rowid FROM retrieval_fts WHERE generation=? AND chunk_key=?').get(info.id,key);if(!inFts)db.prepare('INSERT INTO retrieval_fts(content,chunk_key,generation) VALUES(?,?,?)').run(chunk.text,key,info.id);});
     }else validateVector(JSON.parse(row.vector),selected.representation.dimensions);
     if(processed>info.cursor)documentPort.checkpoint(generation,processed);
    }
   }
   assert(processed>0&&processed<=2000,'ResourceLimit','nonempty bounded generation');assert(info.cursor<=processed,'StaleOwner','generation checkpoint exceeds actual parsed chunks');inspectGeneration(generation,principal);
   tx(()=>{const actual=db.prepare('SELECT chunk_key,vector FROM retrieval_chunks WHERE generation=?').all(info.id);assert(actual.length===expectedKeys.size&&actual.every(row=>expectedKeys.has(row.chunk_key)&&row.vector!==null),'StaleOwner','index generation is incomplete or contains stale chunks');db.prepare("UPDATE retrieval_generations SET status='ready' WHERE id=?").run(info.id);});
   const ready=freeze({generationId:info.id,tenant:info.tenant,chunks:processed,mode:selected.mode,representation:selected.representation,index:selected.index,status:'ready'});
   return promote?activate({generation,principal}):ready;
  }finally{building=false;}
 }
 /** Technical commit, selected only after the original authored application
  * decision. Two owners are deliberately not described as one transaction. */
 function activate({generation,principal}){
  const info=inspectGeneration(generation,principal),stored=db.prepare('SELECT * FROM retrieval_generations WHERE id=? AND tenant=?').get(info.id,info.tenant);
  assert(stored&&['ready','active'].includes(stored.status)&&stored.identity===canonical(generationBody(info))&&stored.profile===canonical(selected),'StaleOwner','exact ready index generation required');
  const refs=new Map(info.sources.map(ref=>[ref.id,ref])),rows=db.prepare('SELECT * FROM retrieval_chunks WHERE generation=?').all(info.id);
  assert(rows.length>0&&rows.length<=2000&&rows.length===info.cursor&&new Set(rows.map(r=>r.source_id)).size===refs.size,'StaleOwner','complete source/chunk checkpoint required');
  for(const row of rows){const ref=refs.get(row.source_id);assert(ref&&row.version===ref.version&&row.acl_revision===ref.acl_revision&&row.source_sha256===ref.sha256&&row.chunk_sha256===sha256(row.content)&&row.vector!==null&&row.chunk_key===refKey({sourceId:row.source_id,version:row.version,chunkId:row.chunk_id}),'StaleOwner','exact prepared chunk/source identity required');validateVector(JSON.parse(row.vector),selected.representation.dimensions);}
  inspectGeneration(generation,principal);
  documentPort.activate(generation);
  try{tx(()=>{db.prepare("UPDATE retrieval_generations SET status='retired' WHERE tenant=? AND status='active' AND id<>?").run(info.tenant,info.id);db.prepare("UPDATE retrieval_generations SET status='active' WHERE id=?").run(info.id);});}
  catch(error){throw Object.assign(Error('document authority activation committed; index promotion requires reconciliation'),{code:'ActivationReconciliationRequired',cause:error});}
  return freeze({generationId:info.id,tenant:info.tenant,chunks:rows.length,mode:selected.mode,representation:selected.representation,index:selected.index,status:'active'});
 }
 function search(raw){
  current();const s=closed(raw,['tenant','principal','query','vector','topK'],['tenant','principal','query','vector']);text(s.tenant,'tenant');text(s.principal,'principal');const topK=s.topK??10;count(topK,'topK',10);assert(topK>0,'InvalidContract','positive topK');const query=readableQuery(s.query),queryVector=validateVector(s.vector,selected.representation.dimensions).vector;
  const info=documentPort.activeGeneration(s.tenant);assert(info,'IndexUnavailable','no active document generation');assert(sameEmbedding(info.embedding,selected.representation)&&info.index===RETRIEVAL_IDENTITY.indexVersion,'UnsupportedCapability','active representation mismatch');
  const stored=db.prepare("SELECT * FROM retrieval_generations WHERE id=? AND tenant=? AND status='active'").get(info.id,s.tenant);assert(stored&&stored.profile===canonical(selected),'IndexUnavailable','current durable index unavailable');
  const authorized=readAuthorized(info,s.principal),rows=db.prepare('SELECT * FROM retrieval_chunks WHERE generation=?').all(info.id).filter(row=>authorized.has(row.source_id));assert(rows.length<=2000&&new Set(rows.map(r=>r.source_id)).size<=100,'ResourceLimit','bounded authorized index');
  db.exec('DELETE FROM temp.retrieval_authorized');const add=db.prepare('INSERT INTO temp.retrieval_authorized(content,chunk_key) VALUES(?,?)');const byKey=new Map();
  for(const row of rows){const {ref}=authorized.get(row.source_id);assert(row.version===ref.version&&row.acl_revision===ref.acl_revision&&row.source_sha256===ref.sha256&&row.chunk_sha256===sha256(row.content)&&row.vector!==null,'StaleOwner','stored index/source mismatch');const record={sourceId:row.source_id,version:row.version,chunkId:row.chunk_id,row};byKey.set(row.chunk_key,record);add.run(row.content,row.chunk_key);}
  const lexical=query?db.prepare('SELECT chunk_key,bm25(retrieval_authorized) lexical_score FROM temp.retrieval_authorized WHERE retrieval_authorized MATCH ?').all(query).map(item=>({...byKey.get(item.chunk_key),lexicalScore:item.lexical_score})).sort((a,b)=>a.lexicalScore-b.lexicalScore||compareRef(a,b)):[];
  const dense=[...byKey.values()].map(record=>({...record,cosine:cosineSimilarity(queryVector,JSON.parse(record.row.vector))})).sort((a,b)=>b.cosine-a.cosine||compareRef(a,b));
  const selectedRanks=fuseRanks({lexical,dense,topK}),results=selectedRanks.map(rank=>{const {row}=byKey.get(refKey(rank));return {...rank,generationId:info.id,aclRevision:row.acl_revision,sourceSha256:row.source_sha256,chunkSha256:row.chunk_sha256,page:row.page,start:row.start_offset,end:row.end_offset,text:row.content};});
  // Recheck original owner immediately before returning content; no serialized ACL mirror.
  const final=documentPort.activeGeneration(s.tenant);assert(final?.id===info.id,'StaleOwner','active index changed before release');for(const {ref} of authorized.values())sourceMatches(documentPort.read({id:ref.id,tenant:s.tenant,principal:s.principal}),ref,s.tenant);
  return freeze({generationId:info.id,mode:selected.mode,representation:selected.representation,ranking:{strategy:RETRIEVAL_IDENTITY.strategy,fusionConstant:60,scoreMeaning:'technical reciprocal ranks only'},results});
 }
 const resource=Object.freeze({identity:RETRIEVAL_IDENTITY,profile:selected,build,activate,search,inspect({tenant}){current();text(tenant,'tenant');return freeze(db.prepare('SELECT id,status FROM retrieval_generations WHERE tenant=? ORDER BY id').all(tenant));},retire({tenant,generationId}){text(tenant,'tenant');text(generationId,'generation');return tx(()=>{const g=db.prepare('SELECT * FROM retrieval_generations WHERE id=?').get(generationId);assert(g&&g.tenant===tenant,'PermissionDenied','index generation tenant');db.prepare("UPDATE retrieval_generations SET status='retired' WHERE id=?").run(generationId);db.prepare('DELETE FROM retrieval_fts WHERE generation=?').run(generationId);db.prepare('DELETE FROM retrieval_chunks WHERE generation=?').run(generationId);});},close(){assert(!building,'ResourceLimit','cannot close active build');if(!ownerClosed){ownerClosed=true;db.close();}}});originalRetrievals.set(resource,{documentPort,embeddingPort,parser,profile:selected,current});return resource;
}
