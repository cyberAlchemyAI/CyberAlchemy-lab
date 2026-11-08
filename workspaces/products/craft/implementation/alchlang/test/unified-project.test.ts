import assert from 'node:assert/strict';
import test from 'node:test';
import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {buildFunction,checkFunction} from '../src/function-builder.js';
import {loadDomainSpecCompiler} from '../src/domainspec-cli.js';
import {digest} from '../src/domainspec-profile.js';
const source=path.resolve(import.meta.dirname,'../../extensions/invocation-trace-v1/quantity-price.alch');
test('Alch emits the verified DomainSpec composition and rejects broken core and integration bindings',async t=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'alch-unified-'));t.after(()=>rmSync(root,{recursive:true,force:true}));const out=path.join(root,'bundle');await buildFunction(source,out);assert.equal((await checkFunction(source)).status,'valid');
 const project=path.join(out,'provenance/lowering/project'),composition=path.join(project,'compositions/function.json'),before=readFileSync(composition,'utf8');
 const compiler=await loadDomainSpecCompiler(),compiled=compiler.compileProject(project) as any;assert.equal(compiled.graph.compositions.length,1);assert.equal(compiled.certificate.compositions[0].validation.result,'pass');
 const generated=compiled.graph.compositions[0].artifacts;
 for(const file of ['behavior.mjs','composition.json','composition-trace.json','ontology.json','function.json','bindings.json','source.alch']){
  const destination=file==='behavior.mjs'?'app/function/'+file:file==='composition-trace.json'?'evidence/function/'+file:'provenance/function/'+file;
  assert.equal(readFileSync(path.join(out,destination),'utf8'),generated[file],file);
 }
 const manifest=JSON.parse(readFileSync(path.join(out,'manifest.json'),'utf8'));
 assert.equal(manifest.output_layout,'domainspec.application-layout/v1');
 for(const [f,hash] of Object.entries(manifest.files))assert.equal(hash,digest(readFileSync(path.join(out,f))),f);
 const receipt=JSON.parse(readFileSync(path.join(out,'evidence/project-build.json'),'utf8'));
 for(const artifact of receipt.artifacts)assert.equal(artifact.sha256,digest(readFileSync(path.join(out,artifact.relative_path))),artifact.relative_path);

 for(const mutate of [
  (s:any)=>s.core_bindings.LineSubtotal.selector='quantity-price:missing',
  (s:any)=>s.core_bindings.LineSubtotal.selector='quantity-price:price-tier',
  (s:any)=>s.core_bindings.LineSubtotal.fields.amountMinor='requested_quantity',
  (s:any)=>s.core_bindings.PriceTier.fields.amountMinor='currency',
  (s:any)=>{s.core_bindings.PriceTier.fields.minQuantity='max_quantity';s.core_bindings.PriceTier.fields.maxQuantity='min_quantity';},
  (s:any)=>s.contract.records.PriceTier.amountMinor='String',
  (s:any)=>s.model.integrations.Prices.provided='input.request',
  (s:any)=>s.model.integrations.Prices.query.variant_id='input.request.missing',
  (s:any)=>s.bindings[0].integration='Missing',
  (s:any)=>s.ontology.references.pop(),
  (s:any)=>s.ontology.nodes.find((n:any)=>n.name==='LineSubtotal').typed_contract.result.name='String',
 ]){const s=JSON.parse(before);mutate(s);writeFileSync(composition,JSON.stringify(s));assert.throws(()=>compiler.compileProject(project),/DS_PROJECT_COMPOSITION|DS_DECLARATIVE/);}
 writeFileSync(composition,before);
});
