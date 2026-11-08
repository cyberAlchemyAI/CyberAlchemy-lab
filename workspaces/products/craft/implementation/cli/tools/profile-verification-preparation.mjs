// Development-only source preparation profiler. Prints JSONL; fixtures own and clean their temporary files.
// Run with the existing tsx loader. Optional arguments select scalar, compound, or mixed fixtures.
import {Session} from 'node:inspector/promises';
import {workflowFixture} from '../test/helpers/workflow-verification.ts';
import {crossGeneratorPublicFixture} from '../test/helpers/cross-generator-public.ts';
import {mixedWorkflowPublicFixture} from '../test/helpers/workflow-public-mixed.ts';
import {planCompiledReconciledProject} from '../src/generation/reconciled-project.ts';
import {createReconciledSemanticControls} from '../src/verification/reconciled-semantic-controls.ts';
import {prepareCrossGeneratorVerification} from '../src/verification/reconciled-cross-generator-public.ts';
import {canonicalJson,sha256} from '../src/input/source-manifest.ts';
const session=new Session();session.connect();await session.post('Profiler.enable');await session.post('Profiler.start');
const metrics=[];
const selected=process.argv.slice(2);if(selected.some(v=>!['scalar','compound','mixed'].includes(v)))throw new Error('Use optional fixture names: scalar compound mixed');
for(const [name,fixture] of [['scalar',workflowFixture],['compound',crossGeneratorPublicFixture],['mixed',mixedWorkflowPublicFixture]]){
if(selected.length&&!selected.includes(name))continue;
const cleanup=[];try{const timer=(phase,fn)=>{const start=performance.now();const value=fn();const row={fixture:name,phase,ms:performance.now()-start};metrics.push(row);console.log(JSON.stringify(row));return value;};
const f=timer('fixture',()=>fixture({after:fn=>cleanup.push(fn)})),plan=timer('plan',()=>planCompiledReconciledProject(f.graph,f.selection));
const semantic=timer('standalone-control-preparation',()=>createReconciledSemanticControls(f.graph,plan));
const prepared=timer('cross-generator-control-preparation',()=>prepareCrossGeneratorVerification(f.graph,plan));
console.log(JSON.stringify({fixture:name,plan:plan.plan_sha256,source:f.graph.source_manifest.manifest_sha256,semantic:semantic.rows.map(r=>({selector:r.selector,state:r.state,cases:r.state==='ready'?r.cases.length:0})),prepared:prepared.families.map(f=>({family:f.family,state:f.state})),heap_used:process.memoryUsage().heapUsed}));
}finally{cleanup.reverse().forEach(fn=>fn());}}
const {profile}=await session.post('Profiler.stop');session.disconnect();
const grouped=new Map();for(const n of profile.nodes){const key=JSON.stringify([n.callFrame.functionName,n.callFrame.url]);const prior=grouped.get(key);if(prior)prior.hitCount+=(n.hitCount??0);else grouped.set(key,{...n,hitCount:n.hitCount??0});}profile.nodes=[...grouped.values()];
const total=profile.nodes.reduce((n,r)=>n+(r.hitCount??0),0);console.log(JSON.stringify({cpu_samples:total,top:profile.nodes.filter(n=>n.hitCount).sort((a,b)=>b.hitCount-a.hitCount).slice(0,18).map(n=>({function:n.callFrame.functionName,url:n.callFrame.url,line:n.callFrame.lineNumber+1,samples:n.hitCount,percent:100*n.hitCount/total})),metrics}));
