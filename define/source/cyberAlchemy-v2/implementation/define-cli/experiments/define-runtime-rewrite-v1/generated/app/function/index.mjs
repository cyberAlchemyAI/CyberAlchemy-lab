
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"ccfe7a672d4a617aef19a6ce20be5345ce9b90dfb11053425ed21b04c6e92bda","ontology_sha256":"41710b1dcc4357a449fb377e72c91e36873d9fb2d8910ce665a3cc6f4c43a965","behavior_sha256":"756622618bf5123e855e16b8758b2109f4bb266e524a91f93e29bb7bec9a13e4","contract_sha256":"7d0ca1174fe9b9dafdeeff4ec60a1c4e49fade904146bf0f6303129637972130"},manifest},createBoundary,modules);
export default {fetch:handler};
