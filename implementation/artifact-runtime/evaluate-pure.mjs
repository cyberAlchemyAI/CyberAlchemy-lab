import {evaluateArtifact} from './pure-operation.mjs';
let raw='';for await(const chunk of process.stdin)raw+=chunk;
const [directory,member,manifest_sha256]=process.argv.slice(2);
const result=await evaluateArtifact(directory,member,JSON.parse(raw),{manifest_sha256});
if(!result.ok){console.error(JSON.stringify(result));process.exitCode=1;}
else console.log(JSON.stringify({value:JSON.parse(new TextDecoder().decode(result.wire)),fuel_used:result.fuel_used}));