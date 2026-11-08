import test from 'node:test';import assert from 'node:assert/strict';import {mkdtempSync,rmSync} from 'node:fs';import {tmpdir} from 'node:os';import path from 'node:path';import {DatabaseSync} from 'node:sqlite';
import {createSourceReleaseService} from '../source-release/index.mjs';
import {createDocumentAuthority} from '../documents/source-access/index.mjs';
import {createDocumentParser,PARSER_IDENTITY} from '../documents/parser/index.mjs';
import {createEmbeddedRetrieval,createRetrievalProfile,RETRIEVAL_IDENTITY,validateVector,cosineSimilarity,fuseRanks,retrievalArtifactIdentity} from './index.mjs';
const representation={model:'recorded-labelled-basis',dimensions:3,preprocessing:'exact-chunk-utf8-v1',space:'fixture-basis-v1'},bytes=text=>new TextEncoder().encode(text);
function setup(t,{embed,inspect,selectedRepresentation=representation,profile=createRetrievalProfile({embedding:selectedRepresentation,mode:'fixture'})}={}){
 const directory=mkdtempSync(path.join(tmpdir(),'craft-retrieval-')),release=createSourceReleaseService({path:path.join(directory,'release.db')}),docs=createDocumentAuthority({path:path.join(directory,'docs.db'),releaseAuthority:release.authority});let calls=0;
 const embeddingPort={identity:selectedRepresentation,async embed(request){calls++;return embed?embed(request):{vector:vectorFor(request.text)};},...(inspect?{inspect}:{})};
 const parser=createDocumentParser();let index=createEmbeddedRetrieval({path:path.join(directory,'index.db'),documentPort:docs.port,embeddingPort,parser,profile});
 const f={directory,release,docs,parser,embeddingPort,get index(){return index;},get calls(){return calls;},restart(){index.close();index=createEmbeddedRetrieval({path:path.join(directory,'index.db'),documentPort:docs.port,embeddingPort,parser,profile});},put(id,content,{tenant='A',version='v1',aclRevision='acl1',readers=['alice'],mediaType='text/plain'}={}){return docs.authority.put({id,tenant,version,aclRevision,readers,classifications:['public'],mediaType,bytes:bytes(content)});},generation(sources,tenant='A',overrides={}){return docs.port.beginGeneration({tenant,sources,parser:PARSER_IDENTITY.parserVersion,chunker:PARSER_IDENTITY.chunkerVersion,embedding:selectedRepresentation,index:RETRIEVAL_IDENTITY.indexVersion,...overrides});}};
 t.after(()=>{index.close();docs.close();release.close();rmSync(directory,{recursive:true,force:true});});return f;
}
function vectorFor(text){return /orchard|apple/i.test(text)?[1,0,0]:/engine|motor/i.test(text)?[0,1,0]:[0,0,1];}
const search=(f,query='apple',vector=[1,0,0],more={})=>f.index.search({tenant:'A',principal:'alice',query,vector,topK:10,...more});
test('actual parsed text + durable FTS5/dense rank fusion returns labelled evidence and survives reopen',async t=>{
 const f=setup(t);f.put('orchard','apple orchard harvest');f.put('engine','engine motor repairs');f.put('other','ocean weather');const g=f.generation(['orchard','engine','other']),built=await f.index.build({generation:g,principal:'alice'});assert.equal(built.chunks,3);assert.equal(f.calls,3);
 const found=search(f);assert.equal(found.results[0].sourceId,'orchard');assert.equal(found.results[0].text,'apple orchard harvest');assert.equal(found.results[0].lexicalRank,1);assert.equal(found.results[0].denseRank,1);assert.equal(found.results[0].fusionScore,2/61);assert.equal(found.mode,'fixture');assert.equal(found.representation.dimensions,3);assert.match(found.results[0].chunkSha256,/^[a-f0-9]{64}$/);
 const db=new DatabaseSync(path.join(f.directory,'index.db'));assert.equal(db.prepare('SELECT count(*) n FROM retrieval_fts WHERE retrieval_fts MATCH ?').get('apple').n,1);db.close();f.restart();assert.deepEqual(search(f),found);await f.index.build({generation:g,principal:'alice'});assert.equal(f.calls,3,'rebuild reuses completed observation vectors');
 const labels=[{query:'apple',vector:[1,0,0],expected:'orchard'},{query:'engine',vector:[0,1,0],expected:'engine'},{query:'weather',vector:[0,0,1],expected:'other'}];assert.equal(labels.filter(c=>search(f,c.query,c.vector).results[0].sourceId===c.expected).length,3);
});
test('source ACL filtering precedes lexical and vector ranks, and tenants never share an authorized corpus',async t=>{
 const f=setup(t);f.put('allowed','apple orchard');f.put('private','apple apple apple orchard',{readers:['bob','alice']});f.put('foreign','apple orchard',{tenant:'B'});const g=f.generation(['allowed','private']);await f.index.build({generation:g,principal:'alice'});
 // Bob is allowed one source only, with a current ACL; no ACL mirror is consulted.
 const bob=search(f,'apple',[1,0,0],{principal:'bob'});assert.deepEqual(bob.results.map(r=>r.sourceId),['private']);assert.equal(bob.results[0].lexicalRank,1);assert.equal(bob.results[0].denseRank,1);
 assert.deepEqual(search(f,'apple',[1,0,0],{principal:'stranger'}).results,[]);assert.throws(()=>search(f,'apple',[1,0,0],{tenant:'B'}),{code:'IndexUnavailable'});
 f.docs.authority.setAccess({id:'private',tenant:'A',aclRevision:'acl2',readers:['bob'],classifications:['public']});assert.throws(()=>search(f),{code:'StaleOwner'});
});
test('current source replacement and tombstone deny all old-generation exposure and never resurrect',async t=>{
 const f=setup(t);f.put('doc','apple orchard');const first=f.generation(['doc']);await f.index.build({generation:first,principal:'alice'});f.put('doc','engine motor',{version:'v2'});assert.throws(()=>search(f),{code:'StaleOwner'});await assert.rejects(f.index.build({generation:first,principal:'alice'}),{code:'StaleOwner'});
 const next=f.generation(['doc']);await f.index.build({generation:next,principal:'alice'});assert.equal(search(f,'engine',[0,1,0]).results[0].version,'v2');f.docs.authority.delete({id:'doc',tenant:'A'});assert.throws(()=>search(f),{code:'SourceUnavailable'});await assert.rejects(f.index.build({generation:next,principal:'alice'}),{code:'SourceUnavailable'});
});
test('revoke during an awaited embedding prevents activation; no index data is exposed',async t=>{
 let f;f=setup(t,{embed(){f.docs.authority.setAccess({id:'doc',tenant:'A',aclRevision:'acl2',readers:[],classifications:['public']});return {vector:[1,0,0]};}});f.put('doc','apple orchard');const g=f.generation(['doc']);await assert.rejects(f.index.build({generation:g,principal:'alice'}),e=>['StaleOwner','PermissionDenied'].includes(e.code));assert.equal(f.docs.port.inspectGeneration(g).status,'building');assert.throws(()=>search(f),{code:'IndexUnavailable'});
});
test('application prepares real index first, then explicitly activates after authored acceptance; deletion fences commit',async t=>{
 const f=setup(t);f.put('doc','apple orchard');const g=f.generation(['doc']);
 const ready=await f.index.build({generation:g,principal:'alice',activate:false});assert.equal(ready.status,'ready');assert.equal(f.docs.port.inspectGeneration(g).status,'building');assert.equal(f.docs.port.activeGeneration('A'),null);assert.throws(()=>search(f),{code:'IndexUnavailable'});
 f.restart();const active=f.index.activate({generation:g,principal:'alice'});assert.equal(active.status,'active');assert.equal(search(f).results[0].sourceId,'doc');assert.equal(f.calls,1);
 const other=setup(t);other.put('doc','apple orchard');const pending=other.generation(['doc']);await other.index.build({generation:pending,principal:'alice',activate:false});other.docs.authority.delete({id:'doc',tenant:'A'});assert.throws(()=>other.index.activate({generation:pending,principal:'alice'}),{code:'SourceUnavailable'});assert.throws(()=>search(other),{code:'IndexUnavailable'});
});
test('interrupted embedding resumes by original observation inspection and never blindly invokes again',async t=>{
 let first=true;const f=setup(t,{embed(){if(first){first=false;throw Object.assign(Error('unknown paid observation'),{code:'OutcomeUnknown'});}throw Error('must not repeat embed');},inspect(){return {status:'confirmed',vector:[1,0,0]};}});f.put('doc','apple orchard');const g=f.generation(['doc']);await assert.rejects(f.index.build({generation:g,principal:'alice'}),{code:'OutcomeUnknown'});assert.equal(f.calls,1);f.restart();await f.index.build({generation:g,principal:'alice'});assert.equal(f.calls,1);assert.equal(search(f).results[0].sourceId,'doc');
 const unknown=setup(t,{embed(){throw Error('lost acknowledgement');}});unknown.put('doc','apple');const h=unknown.generation(['doc']);await assert.rejects(unknown.index.build({generation:h,principal:'alice'}));await assert.rejects(unknown.index.build({generation:h,principal:'alice'}),{code:'OutcomeUnknown'});assert.equal(unknown.calls,1);
});
test('embedding space/parser identity mismatch and invalid vectors fail before activation',async t=>{
 const f=setup(t,{embed(){return {vector:[0,0,0]};}});f.put('doc','apple');const wrong=f.generation(['doc'],'A',{embedding:{...representation,space:'different'}});await assert.rejects(f.index.build({generation:wrong,principal:'alice'}),{code:'UnsupportedCapability'});assert.equal(f.calls,0);const g=f.generation(['doc']);await assert.rejects(f.index.build({generation:g,principal:'alice'}),{code:'InvalidVector'});assert.throws(()=>search(f),{code:'IndexUnavailable'});
 for(const vector of [[0,0,0],[NaN,1,0],[Infinity,0,1],[1e308,1e308,0],[1e-20,0,0],[1,0],[1,0,0,0]])assert.throws(()=>validateVector(vector,3));assert.deepEqual(validateVector([-1,0,0],3).vector,[-1,0,0]);
});
test('independent full precision cosine and fusion reference covers negative/near ties/stable identities',()=>{
 const vectors=[[1,0,0],[-1,0,0],[0,1,0],[1,1e-7,0],[1,2e-7,0],[1e5,-2e5,3e5]],q=[1,0,0];
 const independent=(a,b)=>a.reduce((n,x,i)=>n+x*b[i],0)/(Math.sqrt(a.reduce((n,x)=>n+x*x,0))*Math.sqrt(b.reduce((n,x)=>n+x*x,0)));
 for(const v of vectors)assert.ok(Math.abs(cosineSimilarity(q,v)-independent(q,v))<1e-15);assert.equal(cosineSimilarity(q,[-1,0,0]),-1);assert.ok(cosineSimilarity(q,[1,1e-7,0])>cosineSimilarity(q,[1,2e-7,0]));
 const a={sourceId:'a',version:'v1',chunkId:'1'},b={sourceId:'b',version:'v1',chunkId:'1'},c={sourceId:'c',version:'v1',chunkId:'1'};const result=fuseRanks({lexical:[b,a],dense:[a,b,c],topK:3});assert.deepEqual(result.map(r=>r.sourceId),['a','b','c']);assert.equal(result[0].fusionScore,1/61+1/62);assert.equal(result[2].fusionScore,1/63);assert.throws(()=>fuseRanks({lexical:[a,a],dense:[]}),{code:'InvalidContract'});
});
test('real search near ties, deterministic topK and lexical injection are bounded',async t=>{
 const f=setup(t,{embed({text}){return {vector:text.startsWith('a')?[1,2e-7,0]:[1,1e-7,0]};}});f.put('a','a first');f.put('b','b second');await f.index.build({generation:f.generation(['a','b']),principal:'alice'});const found=search(f,'',[1,0,0],{topK:1});assert.equal(found.results[0].sourceId,'b');assert.equal(found.results[0].lexicalRank,null);assert.throws(()=>search(f,'apple',[1,0,0],{topK:11}));assert.ok(search(f,'" OR NOT * - NEAR( )',[1,0,0]).results.length<=2);
});
test('retired indexes cannot revive; unknown schemas remain untouched; exact artifact identity exists',async t=>{
 const f=setup(t);f.put('doc','apple');const g=f.generation(['doc']);await f.index.build({generation:g,principal:'alice'});f.index.retire({tenant:'A',generationId:g.id});assert.throws(()=>search(f),{code:'IndexUnavailable'});await assert.rejects(f.index.build({generation:g,principal:'alice'}),{code:'StaleOwner'});
 const alien=path.join(f.directory,'alien.db'),db=new DatabaseSync(alien);db.exec('CREATE TABLE unrelated(a TEXT)');db.close();assert.throws(()=>createEmbeddedRetrieval({path:alien,documentPort:f.docs.port,embeddingPort:f.embeddingPort,profile:f.index.profile}),{code:'UnsupportedCapability'});const check=new DatabaseSync(alien);assert.deepEqual(check.prepare("SELECT name FROM sqlite_master WHERE type='table'").all().map(r=>r.name),['unrelated']);check.close();assert.match(retrievalArtifactIdentity().artifactSha256,/^[a-f0-9]{64}$/);assert.throws(()=>createRetrievalProfile({embedding:representation}),{code:'UnsupportedCapability'});
});
test('production representation executes1536dimensions and top10 across eleven labelled sources',async t=>{
 const repr={...representation,model:'recorded-1536-reference',dimensions:1536},profile=createRetrievalProfile({embedding:repr});const vector=Array(1536).fill(0);vector[0]=1;const f=setup(t,{selectedRepresentation:repr,profile,embed(){return {vector};}});const ids=[];for(let i=0;i<11;i++){const id='doc'+String(i).padStart(2,'0');ids.push(id);f.put(id,'apple orchard');}await f.index.build({generation:f.generation(ids),principal:'alice'});const found=search(f,'apple',vector);assert.equal(found.results.length,10);assert.deepEqual(found.results.map(r=>r.sourceId),ids.slice(0,10));assert.equal(found.representation.dimensions,1536);assert.equal(found.mode,'local-reference');
});
test('document/chunk bounds reject oversized generations and do not activate a partial index',async t=>{
 const f=setup(t);for(let i=0;i<100;i++)f.put('d'+i,'apple');assert.throws(()=>f.put('overflow','apple'),{code:'ResourceLimit'});
 const big=setup(t);const sources=[];for(let i=0;i<10;i++){sources.push('b'+i);big.put('b'+i,'apple '.repeat(68334));}const g=big.generation(sources);await assert.rejects(big.index.build({generation:g,principal:'alice'}),{code:'ResourceLimit'});assert.equal(big.docs.port.inspectGeneration(g).status,'building');assert.throws(()=>search(big),{code:'IndexUnavailable'});assert.ok(big.calls<=2000);
});
