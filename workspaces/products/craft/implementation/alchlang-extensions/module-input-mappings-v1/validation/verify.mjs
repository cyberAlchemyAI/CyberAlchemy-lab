import {readFileSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const extension=path.resolve(import.meta.dirname,'..'),repo=path.resolve(extension,'../../../../../../../..');
const bytes=p=>readFileSync(p),json=p=>JSON.parse(bytes(p)),hash=b=>createHash('sha256').update(b).digest('hex');
const candidate=json(path.join(extension,'candidate.json'));assert.equal(hash(JSON.stringify(candidate.files)),candidate.scope_sha256);
for(const [file,sha]of Object.entries(candidate.files))assert.equal(hash(bytes(path.join(repo,file))),sha,file);
const suite=json(path.join(import.meta.dirname,'report.json'));assert.equal(suite.status,'pass');let count=0;
for(const report of suite.reports){
 const artifact=path.join(import.meta.dirname,'artifacts',report.name);assert.equal(hash(bytes(path.join(artifact,'report.json'))),report.report_sha256);assert.equal(hash(bytes(report.source)),report.source_sha256);assert.equal(hash(bytes(report.fixtures)),report.fixtures_sha256);assert.equal(report.count,report.cases.length);count+=report.count;
 for(const c of report.cases){assert.equal(c.status,'pass',report.name+':'+c.name);assert.ok(Object.values(c.checks).every(v=>v===true),c.name);}
 for(const target of ['node','rust']){
  const folder=path.join(artifact,target),manifest=json(path.join(folder,'manifest.json'));assert.equal(hash(bytes(path.join(folder,'manifest.json'))),report.builds[target]);
  for(const [alias,source]of Object.entries(report.dependency_sources)){const relative=alias==='.'?'source.alch':alias.split('.').map(p=>'modules/'+p).join('/')+'/source.alch';assert.equal(manifest.files[relative],source,alias);}
 }
}
assert.equal(count,suite.count);
for(const file of ['http-smoke.json','tests.json','input-evidence.json'])assert.equal(json(path.join(import.meta.dirname,file)).status,'pass',file);
assert.equal(candidate.product_approved,false);assert.equal(candidate.authority_effect,'none');
console.log(JSON.stringify({status:'pass',cases:count,files:Object.keys(candidate.files).length,scope_sha256:candidate.scope_sha256,authority_effect:'none'}));
