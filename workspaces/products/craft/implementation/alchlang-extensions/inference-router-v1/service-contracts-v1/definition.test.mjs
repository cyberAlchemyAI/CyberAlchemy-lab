import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const base=dirname(fileURLToPath(import.meta.url));
const root=resolve(base,'../../../../../../../..');
const {validateDefinitionPack}=await import(pathToFileURL(resolve(root,'implementation/define-cli/index.mjs')).href);
const result=JSON.parse(readFileSync(resolve(base,'define/cli-result.json'),'utf8'));
test('Define pack is valid candidate reuse/specialization, without asserted human acceptance',()=>{
 assert.equal(result.ok,true);assert.equal(validateDefinitionPack(result.definition_pack).valid,true);
 const d=result.definition_pack.concept_dispositions;
 assert.equal(d.filter(x=>x.disposition==='reuse').length,6);assert.equal(d.filter(x=>x.disposition==='specialize').length,8);
 assert.equal(result.authority_effect,'none');assert.equal(result.definition_pack.authority.status,'candidate');
 for(const row of d){const ref=row.definition_ref??row.base_definition_ref;const [path,id]=ref.split('#');assert.ok(readFileSync(resolve(root,'..',path),'utf8').includes(id),ref);}
});
test('scripted Define CLI replay produces the exact saved candidate',()=>{
 const run=spawnSync(process.execPath,[resolve(base,'define/run.mjs')],{encoding:'utf8'});
 assert.equal(run.status,0,run.stderr);assert.deepEqual(JSON.parse(run.stdout),result);
});
test('ontology nodes resolve to their exact Define dispositions and business edges close',()=>{
 const scaffold=JSON.parse(readFileSync(resolve(base,'scaffolds.json'),'utf8'));const ids=new Set(scaffold.nodes.map(x=>x.id));
 for(const node of scaffold.nodes){const resolved=node.definition_selector.split('/').slice(1).reduce((v,k)=>v[k],result);assert.equal(resolved.concept_id,node.id);}
 for(const rel of scaffold.business_relations)assert.ok(ids.has(rel.source)&&ids.has(rel.target));
 assert.deepEqual(scaffold.new_domainspec_meta_types,[]);
});
test('repaired candidate route projects canonical sibling lookup as read-only',async()=>{
 const {loadVerifiedDecisionProfile,routeRequest}=await import(pathToFileURL(resolve(root,'implementation/agent-reasoning-engine/packages/request-decision-router/index.mjs')).href);
 const profile=loadVerifiedDecisionProfile(resolve(root,'implementation/agent-reasoning-engine/packages/request-decision-router/profiles/cyberalchemy-v1.json'),resolve(root,'..'));
 assert.equal(profile.ok,true,profile.reason_codes?.join(','));
 const context={schema_version:'are.request-context/v1',request_id:'isb02-profile-repair',raw_request:'find inside ../domainspec-core',objective_kind:'locate-domainspec-core',requested_effects:[],target_refs:[],constraints:[],evidence_refs:['user']};
 assert.equal(routeRequest(context,profile.value).selected.route_id,'CA2-ROUTE-DOMAINSPEC-CORE');
 assert.deepEqual(profile.value.routes.find(x=>x.route_id==='CA2-ROUTE-DOMAINSPEC-CORE').effect_classes,['local-read']);
 for(const effect of ['implementation','persistent-mutation','publication','external-effect'])assert.notEqual(routeRequest({...context,requested_effects:[effect]},profile.value).kind,'direct');
});
