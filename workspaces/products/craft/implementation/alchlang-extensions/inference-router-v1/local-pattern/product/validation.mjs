import {writeFileSync,readFileSync} from 'node:fs';
import {join} from 'node:path';
import {sha} from './package.mjs';
// Shared CLI orchestration, exercised with real failing child processes.
// Open Questions: OPERATOR.md.
export async function validateSuites({output,identity,suites,run,verifyProduct,here}){
   const receipt={schema_version:'alch.inference-reference-validation/v1',status:'running',authority_effect:'none',candidate_manifest_sha256:identity.manifest_sha256,started_at:new Date().toISOString(),suites:[],open_questions_ref:join(here,'OPERATOR.md')};
   const save=()=>writeFileSync(join(output,'RESULT.json'),JSON.stringify(receipt,null,2)+'\n');save();
   try{
    for(const [name,args,expected]of suites){console.log('Checking '+name+'…');const log=join(output,name+'.log');await run(args,log);const text=readFileSync(log,'utf8');if(!new RegExp('(?:ℹ|#) pass '+expected+'(?:\\s|$)').test(text)||!/(?:ℹ|#) fail 0(?:\s|$)/.test(text))throw Error('UNEXPECTED_SUITE_COUNTS: '+name);receipt.suites.push({name,passed:expected,failed:0,log:name+'.log',sha256:sha(readFileSync(log))});save();}
    if(verifyProduct().manifest_sha256!==identity.manifest_sha256)throw Error('CANDIDATE_CHANGED');receipt.status='validated-local-candidate';receipt.tests_passed=receipt.suites.reduce((n,s)=>n+s.passed,0);receipt.finished_at=new Date().toISOString();save();console.log('PASS: '+receipt.tests_passed+' tests. Evidence: '+join(output,'RESULT.json'));
   }catch(error){receipt.status='failed';receipt.error=error.message;save();throw error;}
}
