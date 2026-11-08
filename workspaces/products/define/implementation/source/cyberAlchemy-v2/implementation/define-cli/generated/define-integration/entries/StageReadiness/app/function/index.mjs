
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"b0be22f96fca70f346e77082b82266ddd741be0f3eb3381e7b8f5bcfa88bc52a","ontology_sha256":"3aaede670151658e7adcf581ae93a906b6726205ce9f470667f0baac534cb2ea","behavior_sha256":"85313f00cc89086a5a9a5c83a585f44ce224b776b05f36a282dfdf6eeba4218a","contract_sha256":"db8b029b66deb8487aa3c13c9f8948138101e214845d2580915ec686311dd29d"},manifest},createBoundary,modules);
export default {fetch:handler};
