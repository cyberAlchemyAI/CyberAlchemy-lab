import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {resolveGenericHttpProfile} from '../../src/generic/http-profile.ts';

const root=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const evidence=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence');
const paths=[
 path.join(evidence,'C14/three-app-authoring-contract-001/casedesk/http-profile.json'),
 path.join(evidence,'C09/schedule-http-second-domain-source-001/fixture/contracts/http-profile.json'),
];
for(const file of paths)test(`C14 finite HTTP profile admits ${path.basename(path.dirname(file))} two-route selection`,()=>{
 const profile=resolveGenericHttpProfile(readFileSync(file,'utf8'),file);
 assert.deepEqual(profile.routes.map(route=>route.method),['GET','POST']);
 assert.equal(profile.route_prefix,'/api');
 assert.notEqual(profile.routes[0].entry,profile.routes[1].entry);
});
test('C14 HTTP profile rejects unknown primitive and overlapping same-method routes',()=>{
 const file=paths[1],profile=JSON.parse(readFileSync(file,'utf8'));
 assert.throws(()=>resolveGenericHttpProfile(JSON.stringify({...profile,capabilities:[...profile.capabilities,'unknown-native-primitive']}),file),error=>error.diagnostics?.[0]?.code==='InvalidContract');
 assert.throws(()=>resolveGenericHttpProfile(JSON.stringify({...profile,routes:[profile.routes[0],{...profile.routes[0],id:'ScheduleHttp.Other'}]}),file),error=>error.diagnostics?.[0]?.code==='InvalidContract');
});
