/** Root closure for the selected finite topology consumers, without evaluation.
 * Open questions: goals/plans/craft-technical-profiles-2026-10-31/UNIFIED-DESIGN.md.
 */
import {captureJson,reject,type Json} from './contracts.js';

const roots:Readonly<Record<string,Readonly<{required:readonly string[];optional:readonly string[]}>>>=Object.freeze({
 'craft.profile-engine/v1':{required:['nodes','edges','requestBytes'],optional:[]},
 'craft.technical-profile-composition/v1':{required:['nodes','edges'],optional:[]},
 'craft.technical-profile-runtime/v1':{required:['nodes','edges'],optional:['providerStages']},
});
function isTopologyObject(value:Json):value is Readonly<Record<string,Json>>{
 return value!==null&&typeof value==='object'&&!Array.isArray(value);
}

/** A closed root is formation evidence only; original consumers still check
 * field semantics, bounds, custody and execution support. An unknown consumer
 * remains inspectable inert data and gains no executable admission here.
 */
export function validateTechnicalTopologyRoot(consumer:string|null,value:unknown):Readonly<{
 status:'closed-finite-consumer'|'unverified-consumer';topology:Json;
}> {
 const topology=captureJson(value),contract=consumer!==null&&Object.hasOwn(roots,consumer)?roots[consumer]:undefined;
 if(!contract)return Object.freeze({status:'unverified-consumer',topology});
 if(!isTopologyObject(topology))return reject('TECHNICAL_PROFILE_TOPOLOGY','technical-profile/topology','selected consumer requires a closed topology object');
 const allowed=new Set([...contract.required,...contract.optional]);
 for(const key of Object.keys(topology))if(!allowed.has(key))reject('TECHNICAL_PROFILE_TOPOLOGY','technical-profile/topology/'+key,'unknown topology root slot for '+consumer);
 for(const key of contract.required)if(!Object.hasOwn(topology,key))reject('TECHNICAL_PROFILE_TOPOLOGY','technical-profile/topology/'+key,'missing topology root slot for '+consumer);
 if(!Array.isArray(topology.nodes)||!Array.isArray(topology.edges))reject('TECHNICAL_PROFILE_TOPOLOGY','technical-profile/topology','selected topology nodes and edges must be arrays');
 return Object.freeze({status:'closed-finite-consumer',topology});
}
