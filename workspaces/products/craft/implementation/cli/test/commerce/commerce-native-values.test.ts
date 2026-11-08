/** Original-source codec/native component controls; no installed or context claim.
 * Open Questions: docs/COMMERCE-NATIVE-VALUES.md#open-questions. */
import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {createCoreCommerceStageSourceOwner} from '../../src/commerce/commerce-core-stage-owner.js';
import {createCoreCommerceComputationContract} from '../../src/commerce/commerce-core-pure-contract.js';
import {createCommerceComputationDomainOwner} from '../../src/commerce/commerce-computation-domain.js';
import {generateCommerceValueCodecBundle} from '../../src/commerce/commerce-value-codec-generation.js';
import {compileCommerceComputationTypeScript} from '../../src/commerce/commerce-computation-native.js';
const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,''),reference=JSON.parse(readFileSync(new URL('../../../../../../../implementation/craft-alchlang-commerce-2026-10-16/evidence/EC07/pure-producer-model-09.json',import.meta.url),'utf8'));
const bytes=(s:string)=>new TextEncoder().encode(s),wire=(v:any)=>bytes(JSON.stringify(v)),plain=(v:any):any=>typeof v==='bigint'?v:Array.isArray(v)?v.map(plain):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,plain(x)])):v;
let stage:any,source:any,domain:any,baseline:any,texts:any,bundle:any,codec:any,mod:any,dir:string;
before(async()=>{
 const sources=createCoreCommerceSourceOwner(),capture=sources.prepare(candidate),data=sources.inspect(capture),paths=new Set(data.reconstruction.modules.map(m=>m.path));texts=data.files.filter(f=>paths.has(f.path));
 stage=createCoreCommerceStageSourceOwner(sources,createCoreCommerceSemanticOwner(sources));source=await stage.prepare(candidate,'application.alch');domain=createCommerceComputationDomainOwner(stage,source);baseline=domain.check(createCoreCommerceComputationContract(texts,'Orders.PayableTotal',reference.limits));
 bundle=generateCommerceValueCodecBundle(stage,source,domain,baseline);dir=mkdtempSync(path.join(tmpdir(),'commerce-native-values-'));writeFileSync(path.join(dir,'package.json'),'{"type":"module"}');
 for(const f of bundle.files){writeFileSync(path.join(dir,f.path),f.text);writeFileSync(path.join(dir,f.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(f.text));}
 mod=await import(pathToFileURL(path.join(dir,'values-and-codecs.js')).href);codec=mod.createCommerceValueCodecs();
});
after(()=>{if(dir)rmSync(dir,{recursive:true,force:true});});
const ok=(r:any)=>{assert.equal(r.ok,true,JSON.stringify(r,(_k,v)=>typeof v==='bigint'?String(v):v));return r.value;},bad=(r:any,code='InputType')=>{assert.equal(r.ok,false);assert.equal(r.error.code,code);assert.equal(typeof r.error.path,'string');assert.equal(Number.isSafeInteger(r.error.byte_offset),true);return r.error;};
const type=(name:string)=>codec.schemaForType(name),schema=(root:any)=>({...reference.values,root}),check=(root:any)=>ok(codec.checkCommerceSchema(schema(root)));
const u64=()=>check({kind:'scalar',name:'UInt64'}),identifier=()=>type('Shop.Values.Identifier'),quoteLine=()=>type('Shop.Values.QuoteLine');
const line={sku:'A',quantity:2n,unitPriceMinor:1200n};
test('materializes compiled original invariants and22entry schemas without evaluator callbacks',()=>{
 assert.equal(bundle.files.length,2);assert.equal(bundle.manifest.source_entries.length,22);assert.equal(bundle.manifest.source_symbols.length,130);
 assert.match(bundle.manifest.qualification,/component-only/);const src=bundle.files[0].text;
 assert.match(src,/export function validateCommerceComputationValue/);assert.doesNotMatch(src,/export function evaluate(?:Observed)?\(/);assert.doesNotMatch(src,/evaluateComputation\(/);
 assert.deepEqual(Object.keys(mod).sort(),['createCommerceValueCodecs']);
});
test('closed schema proposals must match original source universe and supported root',()=>{
 assert.equal(codec.checkCommerceSchema(schema({kind:'scalar',name:'UInt64'})).ok,true);
 for(const s of [{...schema({kind:'scalar',name:'UInt64'}),extra:true},{...schema({kind:'scalar',name:'UInt64'}),records:[]},schema({kind:'record',name:'Invented.CustomerContext'})])assert.equal(codec.checkCommerceSchema(s).ok,false);
 const forged={...reference.values,root:{kind:'optional',element:{kind:'optional',element:{kind:'scalar',name:'UInt64'}}}};assert.equal(codec.checkCommerceSchema(forged).ok,false);
});
test('codec handles are factory-private and cannot be cloned or supplied by another factory',()=>{
 const h=identifier(),other=mod.createCommerceValueCodecs();for(const x of [{...h},Object.create(h),new Proxy(h,{})])assert.throws(()=>codec.inspectSchema(x),/ForeignCodecHandle/);assert.throws(()=>other.inspectSchema(h),/ForeignCodecHandle/);
});
test('native UInt64 is exact bigint; canonical wire is a decimal string',()=>{
 const h=u64();for(const v of [0n,1n,9007199254740993n,18446744073709551615n]){assert.equal(ok(codec.copyCommerceValue(h,v)),v);assert.equal(new TextDecoder().decode(ok(codec.encodeCommerceValue(h,v))),'"'+v+'"');assert.equal(ok(codec.decodeCommerceValue(h,wire(String(v)))),v);}
 for(const x of [0,1,NaN,Infinity,'1',-1n,18446744073709551616n])assert.equal(codec.copyCommerceValue(h,x).ok,false);
});
test('decimal decoding rejects coercion,signs,leading zeros,fractions and range overflow',()=>{
 const h=u64();for(const x of ['1','-1','01','+1','1.0','1e2',' 1','1\n','']){const raw=x==='1'?'1':JSON.stringify(x);bad(codec.decodeCommerceValue(h,bytes(raw)));}bad(codec.decodeCommerceValue(h,wire('18446744073709551616')),'InputBound');
});
test('record fields remain closed and source invariants run in generated code',()=>{
 const h=quoteLine();assert.deepEqual(plain(ok(codec.copyCommerceValue(h,line))),line);assert.deepEqual(plain(ok(codec.decodeCommerceValue(h,wire({sku:'A',quantity:'2',unitPriceMinor:'1200'})))),line);
 for(const v of [{...line,quantity:0n},{...line,extra:true},{sku:'A',quantity:2n}])bad(codec.copyCommerceValue(h,v));
});
test('record serialization orders keys and uses six-byte lowercase control escapes',()=>{
 const h=quoteLine(),v={...line,sku:'\u0001\n"\\é😀'};assert.equal(new TextDecoder().decode(ok(codec.encodeCommerceValue(h,v))),'{"quantity":"2","sku":"\\u0001\\u000a\\"\\\\é😀","unitPriceMinor":"1200"}');
});
test('all actual record,enum and refinement roots have bounded source schemas',()=>{
 for(const r of [...reference.values.records,...reference.values.enums,...reference.values.refinements]){const d=codec.inspectSchema(type(r.name));assert.ok(d.maximum_canonical_bytes>0&&d.maximum_canonical_bytes<=reference.limits.max_value_bytes,r.name);assert.match(d.qualification,/data-codec-schema-only/);}
});
test('refinement maxima respect their actual patterns and UTF8/control bounds',()=>{
 for(const [name,n]of [['Shop.Values.Identifier',770],['Shop.Values.RequestFingerprint',66],['Shop.Values.EventOccurrenceId',70],['Shop.Implementation.TablePrefix',18]] as const)assert.equal(codec.inspectSchema(type(name)).maximum_canonical_bytes,n,name);
 const h=identifier(),max='\u0001'.repeat(128);assert.equal(ok(codec.encodeCommerceValue(h,max)).length,770);assert.equal(ok(codec.copyCommerceValue(h,'😀'.repeat(32))),'😀'.repeat(32));bad(codec.copyCommerceValue(h,'😀'.repeat(33)),'InputBound');
 bad(codec.copyCommerceValue(h,''));bad(codec.copyCommerceValue(h,'x'.repeat(129)),'InputBound');
});
test('refinements reject malformed scalar sequences and wrong pattern data',()=>{
 bad(codec.copyCommerceValue(identifier(),'\ud800'),'InvalidUnicode');bad(codec.decodeCommerceValue(identifier(),bytes('"\\udfff"')),'InvalidUnicode');
 const h=type('Shop.Values.RequestFingerprint');assert.equal(ok(codec.copyCommerceValue(h,'a'.repeat(64))),'a'.repeat(64));bad(codec.copyCommerceValue(h,'A'.repeat(64)));
});
test('native nullary and payload enums use the source declared flat canonical wire',()=>{
 assert.equal(new TextDecoder().decode(ok(codec.encodeCommerceValue(type('Shop.Values.Currency'),'USD'))),'"USD"');
 const h=type('Orders.CheckoutObservation'),v={kind:'CaptureUnknown',attemptKey:'attempt-1'};assert.deepEqual(plain(ok(codec.copyCommerceValue(h,v))),v);assert.equal(new TextDecoder().decode(ok(codec.encodeCommerceValue(h,v))),'{"attemptKey":"attempt-1","kind":"CaptureUnknown"}');assert.deepEqual(plain(ok(codec.decodeCommerceValue(h,wire(v)))),v);
 for(const x of [{tag:'CaptureUnknown',fields:{attemptKey:'attempt-1'}},{kind:'CaptureUnknown',fields:{attemptKey:'attempt-1'}},{kind:'CaptureUnknown',attemptKey:'attempt-1',extra:true}])bad(codec.decodeCommerceValue(h,wire(x)));
});
test('explicit computation adapter converts private tag/fields without changing public canonical identity',async()=>{
 const v={kind:'CaptureUnknown',attemptKey:'attempt-1'},h=type('Orders.CheckoutObservation');assert.deepEqual(plain(ok(codec.decodeComputationValue(h,wire({tag:'CaptureUnknown',fields:{attemptKey:'attempt-1'}})))),v);
 const params=codec.schemaForCallableArguments('Orders.ObservationSignal'),input=ok(codec.encodeComputationParameters(params,{observation:v}));assert.deepEqual(JSON.parse(new TextDecoder().decode(input)),{observation:{tag:'CaptureUnknown',fields:{attemptKey:'attempt-1'}}});
 const pure=compileCommerceComputationTypeScript(domain,domain.check(createCoreCommerceComputationContract(texts,'Orders.ObservationSignal',reference.limits))),generated=await import('data:text/javascript;base64,'+Buffer.from(stripTypeScriptTypes(pure.source)).toString('base64')),result=generated.evaluate(input);assert.equal(result.ok,true);assert.equal(JSON.parse(new TextDecoder().decode(result.wire)),'CaptureUnknown');
});
test('callable argument adapter feeds exact original PayableTotal native calculation',async()=>{
 const h=codec.schemaForCallableArguments('Orders.PayableTotal'),input=ok(codec.encodeComputationParameters(h,{subtotal:3000n,discountMinor:100n,taxMinor:216n,shippingMinor:200n})),pure=compileCommerceComputationTypeScript(domain,baseline),generated=await import('data:text/javascript;base64,'+Buffer.from(stripTypeScriptTypes(pure.source)).toString('base64')),result=generated.evaluate(input);assert.equal(result.ok,true);assert.equal(JSON.parse(new TextDecoder().decode(result.wire)),'3316');
});
test('optional native tags map exactly to null and the declared element',()=>{
 const t=reference.values.records.find((r:any)=>r.name==='Payments.PaymentAttempt').fields.providerReference,h=check(t);
 for(const v of [{kind:'none'},{kind:'some',value:'provider-1'}]){const encoded=ok(codec.encodeCommerceValue(h,v));assert.deepEqual(plain(ok(codec.decodeCommerceValue(h,encoded))),v);}
 for(const v of [null,{kind:'none',value:'x'},{kind:'some'},'x'])bad(codec.copyCommerceValue(h,v));
});
test('declared full100line domain and collection invariant both survive the native boundary',()=>{
 const h=codec.schemaForCallableArguments('Orders.MerchandiseSubtotal'),lines=Array.from({length:100},(_,i)=>({sku:String(i).padStart(128,'\u0001'),quantity:1n,unitPriceMinor:1n}));assert.equal(ok(codec.copyCommerceValue(h,{lines})).lines.length,100);assert.ok(ok(codec.encodeCommerceValue(h,{lines})).length<reference.limits.max_output_bytes);
 for(const badLines of [[],[line,line],[...lines,line]])assert.equal(codec.copyCommerceValue(h,{lines:badLines}).ok,false);
});
test('native ingress rejects active objects without invoking hooks',()=>{
 let touched=0;const h=quoteLine(),accessor=Object.defineProperty({...line},'quantity',{get(){touched++;return 2n;},enumerable:true}),proxy=new Proxy(line,{ownKeys(){touched++;return [];}}),toJSON={...line,toJSON(){touched++;return {};}};
 class Line {sku='A';quantity=2n;unitPriceMinor=1200n;}
 for(const x of [accessor,proxy,toJSON,new Line(),{...line,[Symbol('x')]:true},Object.defineProperty({...line},'hidden',{value:true})])bad(codec.copyCommerceValue(h,x));assert.equal(touched,0);
});
test('lists reject holes,cycles,accessors,subclasses and additional own fields',()=>{
 const h=codec.schemaForCallableArguments('Orders.MerchandiseSubtotal');let touched=0;const hole=Array(1),getter=Object.defineProperty([],'0',{get(){touched++;return line;},enumerable:true});class Lines extends Array<any>{}
 const extra=Object.assign([line],{extra:true}),cycle:any[]=[];cycle.push(cycle);
 for(const lines of [hole,getter,new Lines(line),extra,cycle])assert.equal(codec.copyCommerceValue(h,{lines}).ok,false);assert.equal(touched,0);
});
test('byte input copies through intrinsics without constructor,species or proxy hooks',()=>{
 let touched=0;const input=wire('A');Object.defineProperty(input,'constructor',{get(){touched++;throw Error('hook');}});assert.equal(ok(codec.decodeCommerceValue(identifier(),input)),'A');
 const proxy=new Proxy(input,{get(){touched++;throw Error('hook');}});bad(codec.decodeCommerceValue(identifier(),proxy));bad(codec.decodeCommerceValue(identifier(),new Uint8Array(new SharedArrayBuffer(8))));assert.equal(touched,0);
});
test('duplicate decoded object keys reject before native schema validation',()=>{
 for(const text of ['{"sku":"A","sku":"B","quantity":"1","unitPriceMinor":"1"}','{"sku":"A","s\\u006bu":"B","quantity":"1","unitPriceMinor":"1"}'])bad(codec.decodeCommerceValue(quoteLine(),bytes(text)));
});
test('malformed UTF8 and a BOM have deterministic closed failures',()=>{
 for(const b of [[255],[192,128],[237,160,128],[244,144,128,128],[226,130]])bad(codec.decodeCommerceValue(identifier(),new Uint8Array(b)),'InvalidUnicode');bad(codec.decodeCommerceValue(identifier(),new Uint8Array([239,187,191,34,65,34])));
});
test('wire syntax,depth,trailing data and fixed input bound reject',()=>{
 const h=identifier();for(const s of ['"A"true','[','{"x":}','"\\x"','"A\n"'])bad(codec.decodeCommerceValue(h,bytes(s)));bad(codec.decodeCommerceValue(h,bytes('['.repeat(34)+'true'+']'.repeat(34))),'InputBound');bad(codec.decodeCommerceValue(h,new Uint8Array(reference.limits.max_input_bytes+1)),'InputBound');
 const padded=new Uint8Array(reference.limits.max_input_bytes);padded.fill(32);padded.set(wire('A'));assert.equal(ok(codec.decodeCommerceValue(h,padded)),'A');
});
test('entry argument schemas are source-derived and cannot accept private contexts or authority fields',()=>{
 for(const id of bundle.manifest.source_entries)assert.equal(codec.inspectSchema(codec.schemaForEntryArguments(id)).kind,'arguments');
 for(const name of ['CustomerContext','Shop.Context.CustomerContext','VerifiedCustomer','Invented.Type'])assert.throws(()=>type(name),/UnsupportedCapability/);
 const h=codec.schemaForCallableArguments('Orders.PayableTotal');bad(codec.copyCommerceValue(h,{subtotal:1n,discountMinor:0n,taxMinor:0n,shippingMinor:0n,verified:true}));assert.throws(()=>codec.encodeComputationParameters(identifier(),'A'),/ArgumentSchemaRequired/);
});
test('schema proposal metadata is inert and cannot replace original-source validation',()=>{
 let touched=0;const proposed=Object.defineProperty(schema({kind:'scalar',name:'UInt64'}),'root',{get(){touched++;return {kind:'scalar',name:'UInt64'};},enumerable:true});assert.equal(codec.checkCommerceSchema(proposed).ok,false);assert.equal(touched,0);
 assert.throws(()=>generateCommerceValueCodecBundle({...stage},source,domain,baseline));assert.throws(()=>generateCommerceValueCodecBundle(stage,source,{...domain},baseline));
});
test('wrong list type is distinct from an exceeded list count',()=>{
 const h=codec.schemaForCallableArguments('Orders.MerchandiseSubtotal');bad(codec.copyCommerceValue(h,{lines:{}}));bad(codec.copyCommerceValue(h,{lines:Array.from({length:101},()=>line)}),'InputBound');
});
test('source state-machine result codecs retain outcome provenance as data',()=>{
 const f=reference.functions.find((x:any)=>x.name==='Orders.CheckoutLifecycle'),h=check(f.result),value={tag:'transition',state:'AwaitingPayment',intents:[],machine:'Orders.CheckoutLifecycle',branch:'transition:0',reason:'matched'},encoded=ok(codec.encodeCommerceValue(h,value));assert.deepEqual(plain(ok(codec.decodeCommerceValue(h,encoded))),value);
 for(const extra of [{machine:'Invented.Machine'},{branch:'transition:999'},{reason:'invented'},{tag:'stayed',branch:'otherwise',reason:'invented'}])bad(codec.copyCommerceValue(h,{...value,...extra}));
});
test('materialization rejects a disposed genuine source-domain parent',()=>{
 domain.dispose(baseline);assert.throws(()=>generateCommerceValueCodecBundle(stage,source,domain,baseline),(e:any)=>e.diagnostics?.[0]?.code==='DisposedOwner');
});
