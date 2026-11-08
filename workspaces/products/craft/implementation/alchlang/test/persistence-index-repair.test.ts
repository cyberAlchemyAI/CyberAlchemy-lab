/** Current public source delegation, not installed archive qualification.
 * Open Questions: r5 cumulative design and R_IDX independent review. */
import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, writeFileSync, symlinkSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import test from 'node:test';
import {loadDomainSpecCompiler} from '../src/domainspec-cli.js';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../../../../../');
const core=path.join(repo,'craft/projects/domainspec-v2/impl/cli');
const fixture=JSON.parse(readFileSync(path.join(core,'../system-integration/fixtures/persistence-composition-v2/commerce-postgresql.json'),'utf8'));
test('Alch source delegation preserves ordered indexes and validates original field ownership',async t=>{
 const stage=mkdtempSync(path.join(tmpdir(),'alch-index-source-'));t.after(()=>rmSync(stage,{recursive:true,force:true}));
 const manifest=JSON.parse(readFileSync(path.join(core,'package.json'),'utf8'));manifest.exports['.'].import='./src/index.ts';writeFileSync(path.join(stage,'package.json'),JSON.stringify(manifest));symlinkSync(path.join(core,'src'),path.join(stage,'src'),'dir');
 const compiler=await loadDomainSpecCompiler(stage),input=structuredClone(fixture),m=input.persistence_mappings[0],index=m.index_mappings.find((i:any)=>i.index_id==='index:orders-customer');
 index.field_refs=['physical:orders/id','physical:orders/customer-id'];const first=compiler.compilePersistenceComposition(input);
 index.field_refs.reverse();assert.notEqual(compiler.compilePersistenceComposition(input).composition_digest,first.composition_digest);
 index.order='unordered';const unordered=compiler.compilePersistenceComposition(input);index.field_refs.reverse();assert.deepEqual(compiler.compilePersistenceComposition(input),unordered);
 for(const field of ['physical:orders/missing','physical:customers/id','physical:none/id']){
  index.field_refs=[field];assert.throws(()=>compiler.compilePersistenceComposition(input),{code:'PERSISTENCE_INDEX_FIELD'});
 }
 m.physical_models.push({model_id:'physical-model:orders/nested',model_kind:'relational-table',physical_name:'nested_orders',version:'v2'});
 m.field_mappings.push({...m.field_mappings[0],logical_property_ref:'commerce:order#nested',physical_field_ref:'physical:orders/nested/id'});index.field_refs=['physical:orders/nested/id'];
 assert.throws(()=>compiler.compilePersistenceComposition(input),{code:'PERSISTENCE_INDEX_FIELD'});
 index.model_ref='physical-model:orders/nested';
 assert.throws(()=>compiler.compilePersistenceComposition(input),{code:'PERSISTENCE_INDEX_FIELD'});
});
