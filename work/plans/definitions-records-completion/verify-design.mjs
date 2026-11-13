import {readFileSync,mkdirSync,writeFileSync,mkdtempSync} from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {createSourceOperationCompiler} from '../../../implementation/artifact-runtime/compile-source-operation.mjs';import {evaluateArtifact} from '../../../implementation/artifact-runtime/pure-operation.mjs';import {implementationRoot} from '../../../workspaces/products/craft/implementation/source-bindings.mjs';import {createHash} from 'node:crypto';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),sha=x=>createHash('sha256').update(x).digest('hex'),compiler=await createSourceOperationCompiler(path.join(implementationRoot,'cli')),checks=[];
const cases={
 EnforceRead:{selector_bound:true,publication_authenticated:true,snapshot_complete:true},
 EnforceDirectory:{policy_requires_layout:true,protocol_supported:true,current_coverage_exact:true,home_assignments_verified:true,body_bound:true,projection_bound:true,lineage_bound:true,evidence_bound:true,package_verified:true},
 EnforceViews:{selector_bound:true,registry_pointer_current:true,directory_assets_current:true,indexes_current:true},
 EnforceEvolution:{identity_preserved:true,version_fresh:true,previous_bound:true,target_bound:true,owner_decision_verified:true,authority_scope_verified:true,actual_changes:['Meaning'],authorized_changes:['Meaning']},
 EnforceHost:{workspace_bound:true,runtime_shared:true,host_bound:true,semantic_project_required:false,semantic_project_present:false,semantic_project_matches:true,record_scope_matches:true},
 PlanLifecycle:{schema_valid:true,package_bound:true,session_bound:true,source_bound:true,use_bound:true,consumer_bound:true,readiness_verified:true,target_commitment_verified:true,owner_decision_verified:true},
 EnforceViewPublication:{previous_authenticated:true,registry_unchanged:true,selector_current:true,native_head_verified:true,directory_verified:true,owner_authorized:true},
 EnforceCoverage:{inventory_bound:true,subjects_complete:true,edges_resolved:true,provenance_separated:true,records_included:true},
 PlanRecordCustody:{kind:'Product',workspace_verified:true,native_record_verified:true,owner_binding_verified:true,carrier_verified:true,home_safe:true}
};
for(const [operation,value]of Object.entries(cases)){
 const out=path.join(mkdtempSync(path.join(here,'.local/design-')),operation);compiler.compile({modelRoot:root,applicationPath:'implementation/lab-workflows/records-workflow/application.alch',pureSources:true,selector:'Lab.RecordsWorkflow.'+operation,outputDirectory:out});const manifest=sha(readFileSync(path.join(out,'manifest.json')));
 const run=async v=>{const r=await evaluateArtifact(out,'operation.mjs',{value:v},{manifest_sha256:manifest});assert(r.ok,JSON.stringify(r.error));return JSON.parse(new TextDecoder().decode(r.wire));};
 const good=await run(value);assert.equal(good.tag,'Returned');checks.push(operation+':positive');
 for(const [key,expected]of Object.entries(value)){if(expected!==true||['semantic_project_required','policy_requires_layout'].includes(key))continue;const bad=await run({...value,[key]:false});assert.notEqual(bad.tag,'Returned',operation+':'+key);checks.push(operation+':'+key+'-refused');}
 if(operation==='EnforceEvolution'){const bad=await run({...value,authorized_changes:[]});assert.notEqual(bad.tag,'Returned');checks.push(operation+':unreviewed-change-refused');}
 if(operation==='EnforceHost'){const bad=await run({...value,semantic_project_required:true});assert.notEqual(bad.tag,'Returned');checks.push(operation+':actual-work-requires-project');}
}
writeFileSync(path.join(here,'DESIGN-VERIFICATION.json'),JSON.stringify({status:'PASS',checks,check_count:checks.length,source_sha256:sha(readFileSync(path.join(root,'implementation/lab-workflows/records-workflow/workflow.alch'))),scope:'Original Core source compilation and execution; generated artifacts are not semantic owner acceptance.'},null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length}));
