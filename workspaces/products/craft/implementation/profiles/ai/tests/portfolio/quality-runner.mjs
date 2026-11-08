/** Labelled quality/measurement coordinator over actual selected native owners.
 * Gold labels never enter an execution adapter. Fixture/local observations do
 * not qualify providers or actual model quality. No app simulator or predicate.
 * Open Questions: quality-cases.json open_questions_ref. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {isDeepStrictEqual} from 'node:util';
import {evaluateQuality} from '@craft/ai-profiles/observations';
import {createDocumentParser,chunkParsedDocument,PARSER_IDENTITY} from '@craft/ai-profiles/parser';

const kinds=['parser','retrieval','citation','business-extraction'];
const statuses=new Set(['returned','refused','invalid','unavailable']);
const clone=v=>JSON.parse(JSON.stringify(v));
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function loadQualityCases(){return JSON.parse(readFileSync(new URL('./quality-cases.json',import.meta.url),'utf8'));}
function identity(runtime){assert.equal(typeof runtime?.assertCurrent,'function','original runtime currentness required');runtime.assertCurrent();const value=runtime.inspect();for(const k of ['runtime_id','resource_id','mode'])assert.equal(typeof value[k],'string','actual runtime identity required');assert.ok(['local','fixture','provider'].includes(value.mode),'runtime-derived mode');return clone(value);}
/** Host holds this trusted adapter; caller JSON cannot supply mode or labels. */
export function createQualityRuntimeAdapter({runtime,executeCase}){assert.equal(typeof executeCase,'function');const selected=identity(runtime);return Object.freeze({inspect(){assert.deepEqual(identity(runtime),selected,'selected runtime identity cannot drift');return clone(selected);},assertCurrent(){assert.deepEqual(identity(runtime),selected);},async executeCase(input){runtime.assertCurrent();const result=await executeCase(input);runtime.assertCurrent();assert.deepEqual(identity(runtime),selected);assert.ok(result&&statuses.has(result.status),'actual normalized outcome');assert.ok(Object.keys(result).every(k=>['status','value','code'].includes(k)),'closed quality result; no caller mode or label');return clone(result);}});}

export function createParserQualityAdapter({parser=createDocumentParser()}={}){
 assert.equal(parser.identity.abi,PARSER_IDENTITY.abi);const runtime={assertCurrent(){assert.equal(parser.identity.abi,PARSER_IDENTITY.abi);},inspect(){return {runtime_id:parser.identity.parserVersion,resource_id:parser.identity.isolationVersion,mode:'local'};}};
 return createQualityRuntimeAdapter({runtime,async executeCase({id,input}){const parsed=await parser.parse({bytes:new TextEncoder().encode(input.text),mediaType:input.mediaType,source:{tenant:'quality-local',sourceId:id,version:'v1'}});return parsed.status==='parsed'?{status:'returned',value:{text:parsed.text,pages:parsed.pages.length}}:{status:'invalid',value:null,code:parsed.reason??'ParserReview'};}});
}

export function createCitationQualityAdapter({parser=createDocumentParser()}={}){
 assert.equal(parser.identity.abi,PARSER_IDENTITY.abi);const runtime={assertCurrent(){assert.equal(parser.identity.abi,PARSER_IDENTITY.abi);},inspect(){return {runtime_id:parser.identity.parserVersion+':citation',resource_id:parser.identity.chunkerVersion,mode:'local'};}};
 return createQualityRuntimeAdapter({runtime,async executeCase({input}){const parsed=await parser.parse({bytes:new TextEncoder().encode(input.text),mediaType:'text/plain',source:{tenant:'quality-local',sourceId:input.sourceId,version:input.version}});if(parsed.status!=='parsed')return {status:'invalid',value:null,code:'ParserReview'};
  const c=input.citation,page=parsed.pages.find(p=>p.page===c.page),chunk=chunkParsedDocument(parsed).find(p=>p.page===c.page&&p.start<=c.start&&p.end>=c.end);
  const valid=c.sourceId===parsed.source.sourceId&&c.version===parsed.source.version&&c.sourceSha256===parsed.sourceSha256&&page&&chunk&&Number.isSafeInteger(c.start)&&Number.isSafeInteger(c.end)&&c.start>=0&&c.end>c.start&&page.text.slice(c.start,c.end)===c.quote;
  return valid?{status:'returned',value:{sourceId:c.sourceId,version:c.version,page:c.page,quote:c.quote}}:{status:'invalid',value:null,code:'CitationMismatch'};
 }});
}

/** Query context/principal and forbidden source set are host-bound. A case can
 * supply query/vector, never a tenant/principal or serialized access manifest. */
export function createRetrievalQualityAdapter({retrieval,tenant,principal,forbiddenSourceIds=[]}){
 assert.equal(typeof retrieval?.search,'function');assert.equal(typeof retrieval?.profile?.mode,'string');const mode=retrieval.profile.mode==='fixture'?'fixture':'local';
 const runtime={assertCurrent(){retrieval.inspect({tenant});},inspect(){return {runtime_id:retrieval.identity.indexVersion,resource_id:retrieval.profile.id??retrieval.identity.backend,mode};}};
 return createQualityRuntimeAdapter({runtime,async executeCase({input}){assert.ok(Object.keys(input).every(k=>['query','vector','topK'].includes(k)),'case cannot supply source authority');const result=retrieval.search({tenant,principal,query:input.query,vector:input.vector,topK:input.topK??8});return {status:'returned',value:{firstSourceId:result.results[0]?.sourceId??null,forbiddenAbsent:result.results.every(r=>!forbiddenSourceIds.includes(r.sourceId))}};}});
}

export function createInferenceQualityAdapter({runtime,bindCase}){
 return createQualityRuntimeAdapter({runtime,async executeCase(data){const bound=await bindCase(data),result=await runtime.invoke(bound);return {status:result.kind==='candidate'?'returned':result.kind==='refusal'?'refused':result.kind==='invalid'||result.kind==='incomplete'?'invalid':'unavailable',value:result.kind==='candidate'?result.value:null};}});
}

export async function runQualityPortfolio({dataset=loadQualityCases(),adapters,budget}){
 assert.equal(dataset.schema,'craft.portfolio-quality-cases/v1');assert.ok(adapters instanceof Map);assert.ok(Array.isArray(dataset.cases)&&dataset.cases.length>0&&dataset.cases.length<=10000);const ids=new Set();for(const c of dataset.cases){assert.ok(kinds.includes(c.kind)&&!ids.has(c.id)&&statuses.has(c.expected_status));ids.add(c.id);}for(const kind of new Set(dataset.cases.map(c=>c.kind)))assert.ok(adapters.has(kind),'actual selected adapter required for '+kind);
 const budgetRead=()=>{if(!budget)return null;assert.equal(budget.port?.abi,'model-exposure-ledger/v1');return clone(budget.port.allocationSummary(budget.allocationId));};
 const budgetBefore=budgetRead(),rows=[];
 for(const c of dataset.cases){const adapter=adapters.get(c.kind);adapter.assertCurrent();const selected=clone(adapter.inspect());assert.ok(['local','fixture','provider'].includes(selected.mode));const before=process.memoryUsage().rss,started=performance.now();let actual;
  try{actual=await adapter.executeCase({id:c.id,input:clone(c.input)});adapter.assertCurrent();}catch(error){actual={status:'unavailable',value:null,code:['PermissionDenied','ResourceLimit','StaleOwner'].includes(error?.code)?error.code:'OperationFailed'};}
  const latencyMs=performance.now()-started,after=process.memoryUsage().rss;assert.ok(statuses.has(actual.status));assert.deepEqual(adapter.inspect(),selected,'actual mode/identity cannot be relabelled by result');
  rows.push({id:c.id,kind:c.kind,runtime:selected,status:actual.status,expected_status:c.expected_status,expected:clone(c.expected),actual:actual.value??null,conformance:actual.status===c.expected_status&&(actual.status!=='returned'||isDeepStrictEqual(clone(actual.value),clone(c.expected))),measurements:{latency_ms:latencyMs,rss_before_bytes:before,rss_after_bytes:after,process_max_rss_bytes:process.resourceUsage().maxRSS*1024},...(actual.code?{code:actual.code}:{})});
 }
 const evaluations=kinds.filter(kind=>rows.some(r=>r.kind===kind)).map(kind=>({kind,...evaluateQuality({kind,cases:rows.filter(r=>r.kind===kind).map(r=>({id:r.id,expected:r.expected,actual:r.actual,status:r.status})),threshold:dataset.thresholds[kind]})}));
 return {schema:'craft.portfolio-quality-observations/v1',status:evaluations.every(e=>e.status==='passed')&&rows.every(r=>r.conformance)?'passed':'failed',scope:'labelled deterministic/recorded-fixture checks; original runtime modes retained',dataset_sha256:sha(JSON.stringify(dataset)),cases:rows,evaluations,conformance:{passed:rows.filter(r=>r.conformance).length,total:rows.length},scopes:{local:rows.filter(r=>r.runtime.mode==='local').length,fixture:rows.filter(r=>r.runtime.mode==='fixture').length,provider:rows.filter(r=>r.runtime.mode==='provider').length},budget:{before:budgetBefore,after:budgetRead(),source:budget?'original-model-exposure-ledger/v1':'not-supplied'},performance_claim:'observations only; RSS samples and process-wide high-water, no speed/memory promise',provider_qualification:{status:'not-run'},real_model_quality:{status:'not-run',reason:'requires separately qualified provider corpus/model/prompt/account evidence; fixture labels do not qualify a model'},open_questions_ref:dataset.open_questions_ref};
}
