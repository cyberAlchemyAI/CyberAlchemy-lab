import {readFileSync} from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const extension=path.resolve(import.meta.dirname,'..'),repo=path.resolve(extension,'../../../../../../../..');
const bytes=file=>readFileSync(file),json=file=>JSON.parse(bytes(file)),hash=b=>createHash('sha256').update(b).digest('hex');
const candidate=json(path.join(extension,'candidate.json'));
assert.equal(hash(JSON.stringify(candidate.files)),candidate.scope_sha256);
for(const [file,expected]of Object.entries(candidate.files))assert.equal(hash(bytes(path.join(repo,file))),expected,file);
const suite=json(path.join(import.meta.dirname,'report.json'));assert.equal(suite.status,'pass');let count=0;
for(const report of suite.reports){
 const artifact=path.join(import.meta.dirname,'artifacts',report.module);
 assert.equal(hash(bytes(path.join(artifact,'report.json'))),report.report_sha256);
 assert.equal(hash(bytes(path.join(extension,report.module+'.alch'))),report.source_sha256);
 assert.equal(hash(bytes(path.join(extension,report.module+'.fixtures.json'))),report.fixtures_sha256);
 assert.equal(report.count,report.cases.length);count+=report.count;
 for(const c of report.cases){assert.equal(c.status,'pass',c.name);assert.ok(Object.values(c.checks).every(v=>v===true),c.name);}
 for(const target of ['node','rust']){assert.equal(hash(bytes(path.join(artifact,target,'manifest.json'))),report.builds[target]);assert.equal(json(path.join(artifact,target,'composition.json')).portability,'node-rust-v1');}
}
assert.equal(count,suite.count);
console.log(JSON.stringify({status:'pass',cases:count,files:Object.keys(candidate.files).length,scope_sha256:candidate.scope_sha256,authority_effect:'none'}));
