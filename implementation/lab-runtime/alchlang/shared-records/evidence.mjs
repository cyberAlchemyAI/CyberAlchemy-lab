import {isDeepStrictEqual} from 'node:util';
import {authenticatePacket,validateContext} from './security.mjs';
import {digest} from './verified-projection.mjs';
import {verifyImplementation} from './implementation.mjs';
export function verifyPlanningEvidence(request,trust,{historical=false}={}){
 const verified=authenticatePacket(request.receipt,trust),claim=verified.statement;
 const artifact=Buffer.from(request.artifact,'base64');
 if(artifact.toString('base64')!==request.artifact)throw Error('planning-artifact-encoding');
 if(claim.version!==1||claim.predicate!=='verified-planning-input'||claim.operation!==request.operation
  ||claim.scope!==request.scope||claim.cut!==request.cut||claim.artifact.sha256!==digest(artifact)
  ||claim.artifact.bytes!==artifact.length)throw Error('planning-evidence-binding-mismatch');
 const value=JSON.parse(artifact);
 if(value.operation!==request.operation||value.scope!==request.scope||value.cut!==request.cut)throw Error('planning-evidence-context-mismatch');
 const original=trust.historical_artifacts?.[digest(artifact)];
 if(historical&&original){
  if(original.operation!==request.operation||original.scope!==request.scope||original.cut!==request.cut)throw Error('historical-evidence-context-mismatch');
 }else{
  const selected=verifyImplementation(trust.implementation);
  if(value.implementation!==selected)throw Error('planning-implementation-mismatch');
 }
 validateContext(value.input,request,trust);
 return {input:value.input,bytes:artifact,implementation:value.implementation??original?.implementation,historical:!!(historical&&original)};
}
export function sameJson(a,b){if(!isDeepStrictEqual(a,b))throw Error('original-evidence-content-mismatch');}
