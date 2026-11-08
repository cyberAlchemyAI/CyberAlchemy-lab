import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createDocumentParser,chunkParsedDocument,DEFAULT_LIMITS,parserArtifactIdentity} from './index.mjs';
import {runIsolated} from './isolation.mjs';
import {makePdf} from './fixtures.mjs';
const parser=createDocumentParser();
const source={tenant:'tenant-a',sourceId:'invoice-123',version:'sha256-v1'};
const input=(bytes,mediaType='application/pdf')=>({bytes,mediaType,source});

test('verified OS boundary denies host reads/writes, network, fork, eval and records hard limits',async()=>{
  const r=await parser.isolationReport();assert.equal(r.status,'verified');
  for(const key of ['hostFilesystemDenied','packageWriteDenied','rootWriteDenied','networkDenied','processCreationDenied','evalDenied'])assert.equal(r[key],true,key);
  assert.match(r.processStatus,/^Pid:\s+1$/m);assert.match(r.processStatus,/^CapEff:\s+0000000000000000$/m);
  assert.match(r.limits,/Max address space\s+1073741824\s+1073741824/);
});
test('real multi-page PDF preserves page, source and exact text spans, scripts never execute',async()=>{
  const bytes=makePdf(['Invoice 123 Total 42.00','Line 2 approved'],{script:true});
  const r=await parser.parse(input(bytes));assert.equal(r.status,'parsed',r.reason);assert.equal(r.pages.length,2);
  assert.equal(r.pages[0].text,'Invoice 123 Total 42.00');assert.equal(r.pages[1].text,'Line 2 approved');assert.deepEqual(r.source,source);
  assert.match(r.sourceSha256,/^[a-f0-9]{64}$/);assert.match(r.pages[0].spans[0].bounds.transform.join(','),/40,740/);
  for(const p of r.pages)for(const s of p.spans)assert.equal(p.text.slice(s.start,s.end),s.text);
  const chunks=chunkParsedDocument(r,{maxChars:8});assert.ok(chunks.some(c=>c.page===2));assert.deepEqual(chunks,chunkParsedDocument(r,{maxChars:8}));
  assert.equal(chunks.filter(c=>c.page===1).map(c=>c.text).join(''),r.pages[0].text);
});
test('UTF8 text and Markdown retain literal untrusted content, no markup/code execution',async()=>{
  for(const type of ['text/plain','text/markdown']){
    const text='# Olá 😀\n<script>throw 1</script>\n',r=await parser.parse(input(Buffer.from(text),type));
    assert.equal(r.status,'parsed',r.reason);assert.equal(r.text,text);
    const chunks=chunkParsedDocument(r,{maxChars:1});assert.equal(chunks.map(c=>c.text).join(''),text);assert.ok(chunks.some(c=>c.text==='😀'));
  }
});
test('genuine encrypted and image-only PDF, malformed bytes and invalid UTF8 route to typed review/quarantine',async()=>{
  const corruptXref=Buffer.from(makePdf(['must not silently repair']).toString('latin1').replace(/startxref\n\d+/,'startxref\n0'),'latin1');
  const recoverableXref=Buffer.from(makePdf(['must not silently repair']).toString('latin1').replace(/startxref\n\d+/,'startxref\n10'),'latin1');
  for(const [bytes,type,status,reason] of [[makePdf(['private'],{encrypted:true}),'application/pdf','review','ENCRYPTED_PDF'],[makePdf([''],{imageOnly:true}),'application/pdf','review','IMAGE_ONLY_OR_NO_TEXT'],[Buffer.from('%PDF-1.7\ngarbage\n%%EOF'),'application/pdf','quarantine','MALFORMED_PDF'],[corruptXref,'application/pdf','quarantine','MALFORMED_PDF'],[recoverableXref,'application/pdf','quarantine','MALFORMED_PDF'],[Buffer.from([0xc0,0xaf]),'text/plain','quarantine','INVALID_UTF8']]){
    const r=await parser.parse(input(bytes,type));assert.equal(r.status,status,JSON.stringify(r));assert.equal(r.reason,reason);assert.deepEqual(r.pages,[]);
  }
});
test('byte/page/text/span/output limits reject, no partial parsed output',async()=>{
  const cases=[{limits:{bytes:4},bytes:Buffer.from('12345'),type:'text/plain',reason:'BYTE_LIMIT'},{limits:{pages:1},bytes:makePdf(['one','two']),reason:'PAGE_LIMIT'},{limits:{textChars:2},bytes:makePdf(['long']),reason:'TEXT_LIMIT'},{limits:{spans:1},bytes:makePdf(['one','two']),reason:'SPAN_LIMIT'},{limits:{outputBytes:50},bytes:Buffer.from('long'),type:'text/plain',reason:'OUTPUT_LIMIT'}];
  for(const c of cases){const p=createDocumentParser({limits:c.limits}),r=await p.parse(input(c.bytes,c.type));assert.equal(r.status,'quarantine',JSON.stringify(r));assert.equal(r.reason,c.reason);assert.deepEqual(r.pages,[]);}
});
test('OS time and memory exhaustion kill confined worker, output flood is bounded',async()=>{
  await assert.rejects(runIsolated({nodePath:process.execPath,limits:{...DEFAULT_LIMITS,timeMs:150},mode:'burn',request:{}}),/TIME_LIMIT/);
  await assert.rejects(runIsolated({nodePath:process.execPath,limits:{...DEFAULT_LIMITS,timeMs:3000},mode:'allocate',request:{}}),/PARSER_RESOURCE_OR_ISOLATION_FAILURE/);
  await assert.rejects(runIsolated({nodePath:process.execPath,limits:{...DEFAULT_LIMITS,outputBytes:100},mode:'flood',request:{}}),/OUTPUT_LIMIT/);
});
test('exact dependency closure and source upgrade invalidation identity',()=>{
  const lock=JSON.parse(readFileSync(new URL('package-lock.json',import.meta.url))),pkg=JSON.parse(readFileSync(new URL('node_modules/pdfjs-dist/package.json',import.meta.url)));
  assert.deepEqual(readFileSync(new URL('dependency-lock.json',import.meta.url)),readFileSync(new URL('package-lock.json',import.meta.url)));
  assert.equal(pkg.version,'6.4.299');assert.equal(lock.packages['node_modules/pdfjs-dist'].version,pkg.version);
  assert.equal(lock.packages['node_modules/pdfjs-dist'].integrity,'sha512-AVl138zALtfaAPvADulE0PZThbYzCBS79nL4pOSL/6Sm/4AH5A21BD9VHt97OlCuzJuCpmeZtAtkinisF4Vb1g==');
  for(const [name,p] of Object.entries(lock.packages))if(name)assert.ok(p.version&&p.integrity,`unpinned ${name}`);
  assert.match(parserArtifactIdentity().artifactSha256,/^[a-f0-9]{64}$/);
  assert.throws(()=>chunkParsedDocument({status:'parsed',parserVersion:'older',pages:[]}),/PARSED_DOCUMENT_REQUIRED/);
});
test('unsupported formats, invalid source/config and unavailable isolation fail closed',async()=>{
  assert.equal((await parser.parse(input(Buffer.from('hello'),'application/msword'))).reason,'UNSUPPORTED_MEDIA_TYPE');
  await assert.rejects(parser.parse({...input(Buffer.from('hello'),'text/plain'),source:{tenant:'t'}}),/SOURCE_IDENTITY_REQUIRED/);
  assert.throws(()=>createDocumentParser({limits:{bytes:Infinity}}),/INVALID_PARSER_LIMIT/);
  const unavailable=createDocumentParser({nodePath:'/no-runtime-here'});
  assert.equal((await unavailable.parse(input(Buffer.from('hello'),'text/plain'))).status,'quarantine');
});
