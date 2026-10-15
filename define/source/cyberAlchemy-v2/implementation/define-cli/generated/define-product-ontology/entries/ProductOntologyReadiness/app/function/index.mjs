
import {createBoundary} from '../../runtime/boundary.mjs';
import {createTracedInvoker} from '../../runtime/invocation-trace.mjs';
import ontology from '../../provenance/function/ontology.json' with {type:'json'};
import manifest from '../../manifest.json' with {type:'json'};
import {execute,validateInput} from './behavior.mjs';
import api from '../../domain/typescript/lib/index.js';
import model from '../../provenance/function/function.json' with {type:'json'};
import bindings from '../../provenance/function/bindings.json' with {type:'json'};
const modules={};
export function createInvoker(observe){const relay=event=>{const n=ontology.nodes.find(n=>n.name===event.declaration)??ontology.nodes.find(n=>n.kind==='result');observe?.({...event,definition:event.definition??(n?{name:n.name,id:n.id,source:n.source,clauses:n.clauses}:null)});};return createBoundary(model,bindings,scope=>execute(scope,api,relay),scope=>validateInput(scope,relay),modules,relay,(scope,binding)=>execute(scope,api,relay,binding),(scope,binding)=>execute(scope,api,relay,binding,'input'));};
export const {invoke,handler}=createInvoker();
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"f4eb541dec9e8540ef81b99f6b3e63fcbcf67f47ec27d3cb414587a0076ca72b","ontology_sha256":"592bc9e838404089c129f4b139625f9adabb43998dbc5f90bd09869a1396e452","behavior_sha256":"225a1af27e89f22ce4d8e14f16a413ac0bd6e7b9dd468a45b15372297def2764","contract_sha256":"adee0af871fb70c1b03524c919db5055178e831c0837805c30c8421814cf51fa"},manifest},createBoundary,modules);
export default {fetch:handler};
