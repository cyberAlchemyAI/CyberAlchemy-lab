import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync,mkdtempSync,rmSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {parseDeclarativeSource} from '../src/declarative-profile.js';
import {deriveOntology,explainOntology} from '../src/derived-ontology.js';
import {loadDomainSpecCompiler} from '../src/domainspec-cli.js';
import {buildFunction} from '../src/function-builder.js';
import {digest} from '../src/domainspec-profile.js';
const implementation=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const extension=path.resolve(implementation,'../extensions/derived-ontology-v1');
const sourcePath=path.join(extension,'quantity-price.alch'),source=readFileSync(sourcePath,'utf8');
async function inspect(text=source){const parsed=parseDeclarativeSource(text);const compiled=(await loadDomainSpecCompiler()).compileDeclarativeFunction(parsed.contract);return deriveOntology(parsed,compiled.trace,sourcePath);}
const temp=(t:any)=>{const p=mkdtempSync(path.join(os.tmpdir(),'alch-ontology-'));t.after(()=>rmSync(p,{recursive:true,force:true}));return p;};

test('ontology derives all declarations with provenance, constraints and explicit reference roles',async()=>{
 assert.ok(!/^ontology |^  ontology /m.test(source));
 const ontology=await inspect();assert.deepEqual(ontology,await inspect());
 assert.equal(ontology.source.sha256,digest(source));assert.equal(ontology.ontology_admitted,false);
 assert.ok(ontology.nodes.some(n=>n.kind==='integration'&&n.meta_type===null));
 const endpoint=ontology.nodes.find(n=>n.kind==='endpoint')!;assert.equal(endpoint.meta_type,'Interface');
 const result=ontology.nodes.find(n=>n.kind==='result')!;assert.equal(result.meta_type,'Query');assert.equal(result.cases.length,3);
 const price=ontology.nodes.find(n=>n.name==='PriceTier')!;assert.deepEqual(price.entity_identity,{field:'priceId',origin:'derived-single-identifier'});
 assert.equal(price.properties.find(p=>p.name==='priceId')!.ontology,price.id+'#priceId');
 const request=ontology.nodes.find(n=>n.name==='Request')!;assert.equal(request.constraints.quantity.min,1);
 const explanation=explainOntology(ontology,'Cheapest');assert.equal(explanation.meaning_origin,'authored');assert.ok(explanation.dependencies.some(d=>d.name==='Eligible'));
 assert.ok(source.split('\n')[explanation.definition.meaning.source.line-1].includes(explanation.answer));
 for(const n of ontology.nodes){assert.ok(source.split('\n')[n.source.line-1].includes(n.name+':'));for(const c of n.clauses)assert.equal(source.split('\n')[c.source.line-1].trim(),c.text);}
 assert.throws(()=>explainOntology(ontology,'Missing'),/ALCH_ONTOLOGY/);
});

test('ontology annotations are optional; generated structural meaning never claims authored business intent',async()=>{
 const plain=source.replace(/^  meaning .+\n/gm,'');const ontology=await inspect(plain);
 assert.ok(ontology.nodes.every(n=>n.meaning.origin==='derived-structural'));
 assert.ok(ontology.nodes.every(n=>n.meaning.text.includes('structurally derived')));
 const old=await inspect();assert.deepEqual(ontology.nodes.map(n=>n.id),old.nodes.map(n=>n.id));
});

test('stable identities ignore formatting and preserve explicit declaration renames',async()=>{
 const original=await inspect(),old=original.nodes.find(n=>n.name==='Cheapest')!;
 const spaced=await inspect('# comment\n'+source.replace('query Cheapest:','\nquery Cheapest:'));
 assert.deepEqual(spaced.nodes.map(n=>n.id),original.nodes.map(n=>n.id));
 const renamed=source.replaceAll('Cheapest','Best').replace('query Best:','query Best:\n  key "Cheapest"');
 const best=(await inspect(renamed)).nodes.find(n=>n.name==='Best')!;assert.equal(best.id,old.id);assert.equal(best.key_origin,'authored');
 const unpinned=(await inspect(source.replaceAll('Cheapest','Best'))).nodes.find(n=>n.name==='Best')!;assert.notEqual(unpinned.id,old.id);
 const explicit=(await inspect(source.replace('query Cheapest:','query Cheapest:\n  ontology "EXISTING-PRICE-SELECTION"'))).nodes.find(n=>n.name==='Cheapest')!;
 assert.equal(explicit.id,'EXISTING-PRICE-SELECTION');assert.equal(explicit.identity_origin,'authored');
});

test('conflicting annotations and ambiguous entity identity fail closed',async()=>{
 for(const changed of [
  source.replace('entity PriceTier:','entity PriceTier:\n  otherId: identifier required'),
  source.replace('query Cheapest:','query Cheapest:\n  key "same"').replace('query Eligible:','query Eligible:\n  key "same"'),
  source.replace('query Cheapest:','query Cheapest:\n  ontology "EXISTING-PRICE"').replace('query Eligible:','query Eligible:\n  ontology "EXISTING-PRICE"'),
  source.replace('query Cheapest:','query Cheapest:\n  key "Cheapest"\n  key "Best"'),
  source+'\nontology Missing:\n  id "MISSING-NODE"\n',
  source.replace('entity PriceTier:','entity PriceTier:\n  identity amountMinor'),
 ])await assert.rejects(inspect(changed),/ALCH_ONTOLOGY/);
 const annotated=source.replace('entity PriceTier:','entity PriceTier:\n  identity priceId');assert.equal((await inspect(annotated)).nodes.find(n=>n.name==='PriceTier')!.entity_identity!.origin,'authored');
 // Old explicit blocks still bind the exact IDs and property descriptions.
 const old=readFileSync(path.resolve(extension,'../declarative-function-v1/quantity-price.alch'),'utf8');
 const oldOntology=await inspect(old);assert.equal(oldOntology.nodes.find(n=>n.name==='PriceTier')!.id,'ALCH-QUANTITY-PRICETIER');
 assert.equal(oldOntology.nodes.find(n=>n.name==='PriceTier')!.properties[0].meaning_origin,'authored');
});

test('build emits ontology and preserves all pricing fixtures; CLI inspection is read-only',async t=>{
 const p=temp(t),out=path.join(p,'bundle');await buildFunction(sourcePath,out);
 const compiler=await loadDomainSpecCompiler();
 const ontology=JSON.parse(readFileSync(path.join(out,'provenance/function/ontology.json'),'utf8'));assert.deepEqual(ontology,compiler.normalizeCompositionOntology(JSON.parse(JSON.stringify(await inspect()))));
 const manifest=JSON.parse(readFileSync(path.join(out,'manifest.json'),'utf8'));assert.equal(manifest.files['provenance/function/ontology.json'],digest(readFileSync(path.join(out,'provenance/function/ontology.json'))));
 const api=await import(pathToFileURL(path.join(out,'app/function/index.mjs')).href);
 const fixtures=JSON.parse(readFileSync(path.resolve(extension,'../medusa-quantity-price-v1/fixtures.json'),'utf8'));
 for(const f of fixtures){const output=await api.invoke({request:f.request,snapshot:f.snapshot});for(const [k,v]of Object.entries(f.expected))assert.deepEqual(output[k],v,f.name);}
 const cli=path.join(implementation,'dist/cli.js');
 const read=JSON.parse(execFileSync(process.execPath,[cli,'ontology',sourcePath],{encoding:'utf8'}));assert.deepEqual(read,ontology);
 const explanation=JSON.parse(execFileSync(process.execPath,[cli,'explain',sourcePath,'Cheapest'],{encoding:'utf8'}));assert.equal(explanation.subject,'Cheapest');assert.equal(explanation.authority_effect,'none');
 assert.equal(readFileSync(sourcePath,'utf8'),source);
 const invalid=path.join(p,'invalid.alch');writeFileSync(invalid,source.replace('q.amountMinor <','q.missing <'));
 assert.throws(()=>execFileSync(process.execPath,[cli,'ontology',invalid],{encoding:'utf8',stdio:'pipe'}));
});


test('function provenance is independent of the checkout root and remains content-bound',async()=>{
 const parsed=parseDeclarativeSource(source);
 const compiled=(await loadDomainSpecCompiler()).compileDeclarativeFunction(parsed.contract);
 const a=deriveOntology(parsed,compiled.trace,'/first-checkout/functions/quantity-price.alch');
 const b=deriveOntology(parsed,compiled.trace,'/second-checkout/functions/quantity-price.alch');
 assert.deepEqual(a,b);
 assert.equal(a.source.path,'quantity-price.alch');
 assert.equal(a.source.sha256,digest(source));
 assert.ok(!JSON.stringify(a).includes('/first-checkout'));
 const changed=await inspect('# different content\n'+source);
 assert.notEqual(changed.source.sha256,a.source.sha256);
});
