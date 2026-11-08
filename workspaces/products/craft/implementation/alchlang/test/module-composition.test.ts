import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,renameSync,mkdtempSync,rmSync,copyFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {loadModuleTree,assertModuleSources,moduleEnvironment} from '../src/module-source.js';
import {checkFunction,buildFunction,inspectFunctionOntology} from '../src/function-builder.js';
import {digest} from '../src/domainspec-profile.js';
const extension=path.resolve(import.meta.dirname,'../../extensions/module-composition-v1'),source=path.join(extension,'checkout-quote.alch');
const fixture=JSON.parse(readFileSync(path.join(extension,'checkout-quote.fixtures.json'),'utf8'));
function copy(root:string){for(const name of ['checkout-quote.alch','quantity-price.alch','shipping-quote.alch'])copyFileSync(path.join(extension,name),path.join(root,name));return path.join(root,'checkout-quote.alch');}
test('imports derive namespaced schema constraints and reachable environment references',()=>{
 const tree=loadModuleTree(source);assert.equal(tree.parsed.model.schemas.Envelope.pricing.type,'Pricing__Envelope');assert.deepEqual(tree.parsed.model.schemas.Pricing__Price.min_quantity,{type:'integer',optional:true,nullable:true,min:1,max:2147483647});
 assert.deepEqual(moduleEnvironment(tree),['CHECKOUT_API_TOKEN','PRICE_SNAPSHOT_TOKEN','PRICE_SNAPSHOT_URL','SHIPPING_OPTIONS_TOKEN','SHIPPING_OPTIONS_URL']);
 assert.deepEqual(moduleEnvironment(loadModuleTree(path.join(extension,'checkout-quote-http.alch'))),['CHECKOUT_API_TOKEN','PRICING_MODULE_TOKEN','PRICING_MODULE_URL','SHIPPING_MODULE_TOKEN','SHIPPING_MODULE_URL']);
});
test('import cycles, escaped paths, unresolved types and dependency drift fail closed',t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-module-check-'));t.after(()=>rmSync(root,{recursive:true,force:true}));const file=copy(root),original=readFileSync(file,'utf8');
 for(const [from,to,error]of [['Pricing.Envelope','Pricing.Missing',/unknown imported type/],['./quantity-price.alch','../outside.alch',/ENOENT|escapes/],['import Shipping','import Pricing',/duplicate alias/]]as const){writeFileSync(file,original.replace(from,to));assert.throws(()=>loadModuleTree(file),error);}
 writeFileSync(file,original);const child=path.join(root,'quantity-price.alch'),childSource=readFileSync(child,'utf8');writeFileSync(child,childSource+'\nimport Back from "./checkout-quote.alch"\n');assert.throws(()=>loadModuleTree(file),/import cycle/);writeFileSync(child,childSource);
 const tree=loadModuleTree(file);writeFileSync(child,childSource+'\n# changed after capture\n');assert.throws(()=>assertModuleSources(tree),/FUNCTION_MODULE_SOURCE_DRIFT/);
});
test('both targets reject a mismatched imported invocation input',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-module-types-'));t.after(()=>rmSync(root,{recursive:true,force:true}));const file=copy(root);writeFileSync(file,readFileSync(file,'utf8').replace('input input.pricing','input input.shipping'));
 for(const target of ['node-http','rust-http'])await assert.rejects(()=>checkFunction(file,target),/module invocation interface/);
});
test('packaged Node composition preserves typed outcomes, child failures, local traces and import hashes',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-module-node-'));t.after(()=>rmSync(root,{recursive:true,force:true}));const out=path.join(root,'bundle');await buildFunction(source,path.join(root,'initial'));renameSync(path.join(root,'initial'),out);const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);
 assert.deepEqual(await api.invoke(fixture[0].input),fixture[0].expected.result);
 const traced=await api.invokeWithTrace(fixture[0].input);assert.equal(traced.capture.complete,true);assert.equal(traced.selected_case,3);assert.ok(traced.events.some((e:any)=>e.module==='Pricing'&&e.kind==='selected-case'));assert.ok(traced.events.some((e:any)=>e.module==='Shipping'&&e.kind==='selected-case'));
 const failure=fixture.find((f:any)=>f.name==='pricing_error_stops_shipping');const failed=await api.invokeWithTrace(failure.input);assert.equal(failed.outcome.code,'QUOTE_UNSUPPORTED_CURRENCY');assert.equal(failed.events.some((e:any)=>e.module==='Shipping'),false);assert.equal(failed.selected_case,null);
 const response=await api.handler(new Request('http://local/checkout-quote',{method:'POST',headers:{authorization:'Bearer fixture','content-type':'application/json'},body:JSON.stringify(failure.input)}),{CHECKOUT_API_TOKEN:'fixture'});assert.equal(response.status,422);assert.deepEqual(await response.json(),{error:'QUOTE_UNSUPPORTED_CURRENCY'});
 const remote=fixture.find((f:any)=>f.name==='missing_snapshot_requires_environment');const denied=await api.invokeWithTrace(remote.input);assert.equal(denied.outcome.code,'FUNCTION_INTEGRATION_REQUIRED');
 const lock=JSON.parse(readFileSync(path.join(out,'provenance/modules.json'),'utf8'));for(const alias of ['Pricing','Shipping'])assert.equal(lock[alias].manifest_sha256,digest(readFileSync(path.join(out,'modules',alias,'manifest.json'))));
 const ontology=await inspectFunctionOntology(source);assert.ok('nodes' in ontology);assert.ok(ontology.module_imports?.Pricing);assert.ok(ontology.nodes.some((n:any)=>n.name==='Pricing__Quote'));
});

test('namespace resolution ignores comments and rejects existing outside sources',t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-module-comment-')),outside=mkdtempSync(path.join(os.tmpdir(),'alch-module-outside-'));t.after(()=>{rmSync(root,{recursive:true,force:true});rmSync(outside,{recursive:true,force:true});});const file=copy(root),original=readFileSync(file,'utf8');
 writeFileSync(file,original+'\n# Pricing.NotAnExport is a comment, not a type reference.\n');assert.ok(loadModuleTree(file).children.Pricing);
 const escaped=path.join(outside,'external.alch');copyFileSync(path.join(root,'quantity-price.alch'),escaped);writeFileSync(file,original.replace('./quantity-price.alch',path.relative(root,escaped)));assert.throws(()=>loadModuleTree(file),/escapes module root/);
});
