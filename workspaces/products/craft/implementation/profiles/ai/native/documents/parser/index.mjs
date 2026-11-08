import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {dirname,join} from 'node:path';
import {runIsolated,ISOLATION_VERSION} from './isolation.mjs';

export const PARSER_IDENTITY=Object.freeze({abi:'craft.document-parser/v1',parserVersion:'craft-document-parser/1.0.0',chunkerVersion:'craft-page-chunker/1.0.0',pdfjsVersion:'6.4.299',isolationVersion:ISOLATION_VERSION,nodeVersion:'v26.12.1',platform:'linux-x64'});
export const DEFAULT_LIMITS=Object.freeze({bytes:8*1024*1024,pages:100,timeMs:10000,memoryBytes:1024*1024*1024,outputBytes:4*1024*1024,textChars:500000,spans:20000});
const sha=x=>createHash('sha256').update(x).digest('hex');
const originalParsers=new WeakSet();
export function assertOriginalDocumentParser(value){if(!originalParsers.has(value))throw Object.assign(new Error('original constructed document parser'),{code:'ForeignOwner'});return PARSER_IDENTITY;}
let active=0;
function limitsFor(input={}) {
  for(const key of Object.keys(input))if(!(key in DEFAULT_LIMITS))throw Error('UNKNOWN_PARSER_LIMIT');
  const limits={...DEFAULT_LIMITS,...input};
  for(const [key,value] of Object.entries(limits))if(!Number.isSafeInteger(value)||value<1||value>DEFAULT_LIMITS[key])throw Error('INVALID_PARSER_LIMIT');
  return Object.freeze(limits);
}
function sourceFor(source){
  if(!source||typeof source!=='object'||Array.isArray(source)||Object.keys(source).sort().join(',')!=='sourceId,tenant,version')throw Error('SOURCE_IDENTITY_REQUIRED');
  for(const k of ['tenant','sourceId','version'])if(typeof source[k]!=='string'||!source[k].length||source[k].length>512)throw Error('SOURCE_IDENTITY_INVALID');
  return Object.freeze({tenant:source.tenant,sourceId:source.sourceId,version:source.version});
}
export function parserArtifactIdentity(){
  const names=['index.mjs','isolation.mjs','worker.mjs','package.json','dependency-lock.json','node_modules/pdfjs-dist/package.json','node_modules/pdfjs-dist/legacy/build/pdf.mjs','node_modules/pdfjs-dist/legacy/build/pdf.worker.mjs'];
  const dependency=dirname(createRequire(import.meta.url).resolve('pdfjs-dist/package.json'));
  const files=names.map(path=>({path,sha256:sha(readFileSync(path.startsWith('node_modules/pdfjs-dist/')?join(dependency,path.slice('node_modules/pdfjs-dist/'.length)):new URL(path,import.meta.url)))}));
  return {...PARSER_IDENTITY,files,artifactSha256:sha(JSON.stringify(files))};
}
export function createDocumentParser({nodePath=process.execPath,limits:configuredLimits}={}){
  const limits=limitsFor(configuredLimits);
  let isolation;
  const isolationReport=()=>isolation??=(async()=>{
    const r=await runIsolated({nodePath,limits:DEFAULT_LIMITS,request:{},mode:'probe'});
    const checks=['hostFilesystemDenied','packageWriteDenied','rootWriteDenied','networkDenied','processCreationDenied','evalDenied'];
    if(checks.some(key=>r[key]!==true)||!/^Seccomp:\s+2$/m.test(r.processStatus)||!/^NoNewPrivs:\s+1$/m.test(r.processStatus))throw Error('ISOLATION_VERIFICATION_FAILED');
    if(!/^Pid:\s+1$/m.test(r.processStatus)||!/^CapEff:\s+0000000000000000$/m.test(r.processStatus))throw Error('ISOLATION_VERIFICATION_FAILED');
    if(!/^Max address space\s+1073741824\s+1073741824/m.test(r.limits)||!/^Max file size\s+0\s+0/m.test(r.limits))throw Error('RESOURCE_LIMIT_VERIFICATION_FAILED');
    if(r.nodeVersion!==PARSER_IDENTITY.nodeVersion)throw Error('NODE_VERSION_MISMATCH');
    return Object.freeze({status:'verified',isolationVersion:ISOLATION_VERSION,...r});
  })();
  const parser=Object.freeze({identity:PARSER_IDENTITY,limits,isolationReport,async parse({bytes,mediaType,source}){
    const boundSource=sourceFor(source);
    if(!(bytes instanceof Uint8Array))throw Error('DOCUMENT_BYTES_REQUIRED');
    // Snapshot once before async startup so identity and parsed bytes cannot diverge.
    // Oversize inputs are rejected before copying or hashing their content.
    const content=bytes.byteLength<=limits.bytes?Buffer.from(bytes):null;
    const metadata={schema:'craft.parsed-document/v1',source:boundSource,sourceSha256:content?sha(content):null,parserVersion:PARSER_IDENTITY.parserVersion,pdfjsVersion:PARSER_IDENTITY.pdfjsVersion,chunkerVersion:PARSER_IDENTITY.chunkerVersion};
    const failure=(status,reason)=>({...metadata,status,reason,pages:[],text:''});
    if(!['text/plain','text/markdown','application/pdf'].includes(mediaType))return failure('review','UNSUPPORTED_MEDIA_TYPE');
    if(bytes.byteLength>limits.bytes)return failure('quarantine','BYTE_LIMIT');
    if(active>=2)return failure('review','PARSER_BUSY');
    active++;
    try{
      await isolationReport();
      const result=await runIsolated({nodePath,limits,request:{base64:content.toString('base64'),mediaType,limits}});
      if(!['parsed','review','quarantine'].includes(result?.status))throw Error('PARSER_PROTOCOL_INVALID');
      if(result.status!=='parsed')return failure(result.status,result.reason);
      const pages=result.pages;
      if(!Array.isArray(pages)||pages.length>limits.pages)throw Error('PARSER_PROTOCOL_INVALID');
      let total=0,spans=0;
      for(const [i,page] of pages.entries()){
        if(page.page!==i+1||typeof page.text!=='string'||!Array.isArray(page.spans))throw Error('PARSER_PROTOCOL_INVALID');
        total+=page.text.length;
        for(const span of page.spans){spans++;if(!Number.isSafeInteger(span.start)||!Number.isSafeInteger(span.end)||span.start<0||span.end<=span.start||span.end>page.text.length||page.text.slice(span.start,span.end)!==span.text)throw Error('PARSER_PROTOCOL_INVALID');}
      }
      if(total>limits.textChars||spans>limits.spans)throw Error('PARSER_PROTOCOL_INVALID');
      return {...metadata,status:'parsed',mediaType,pages,text:pages.map(p=>p.text).join('\n\f\n')};
    }catch(error){return failure('quarantine',/^[A-Z_]+$/.test(error.message)?error.message:'PARSER_FAILED');}
    finally{active--;}
  }});originalParsers.add(parser);return parser;
}

// Code-unit offsets refer exactly to each extracted page; never cross page boundaries.
export function chunkParsedDocument(document,{maxChars=2000}={}){
  if(document?.status!=='parsed'||document.parserVersion!==PARSER_IDENTITY.parserVersion||!Array.isArray(document.pages))throw Error('PARSED_DOCUMENT_REQUIRED');
  if(!Number.isSafeInteger(maxChars)||maxChars<1||maxChars>20000)throw Error('INVALID_CHUNK_LIMIT');
  const source=sourceFor(document.source),chunks=[];
  for(const page of document.pages){
    for(let start=0;start<page.text.length;){let end=Math.min(start+maxChars,page.text.length);
      // A boundary may not split a UTF-16 surrogate pair, even at maxChars=1.
      if(end<page.text.length&&page.text.charCodeAt(end-1)>=0xd800&&page.text.charCodeAt(end-1)<=0xdbff&&page.text.charCodeAt(end)>=0xdc00&&page.text.charCodeAt(end)<=0xdfff)end+=(end-start===1?1:-1);
      const identity={source,sourceSha256:document.sourceSha256,parserVersion:document.parserVersion,chunkerVersion:PARSER_IDENTITY.chunkerVersion,page:page.page,start,end};
      chunks.push({...identity,chunkId:sha(JSON.stringify(identity)),text:page.text.slice(start,end)});start=end;
    }
  }
  return chunks;
}
