
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
export const invokeWithTrace=createTracedInvoker(model,bindings,api,execute,validateInput,ontology,{...{"source_sha256":"17432eb7f02ad176fc06d83187c757d654a9e4a18aaaac34898b00e6f8a89293","ontology_sha256":"4f1355b6d5a3903c5e05238e3227eb6d5a776944d7c955f4cfbc22adf110fb8d","behavior_sha256":"1a6e43f06e6c3919bf4fc0d4d6ac085c92266491277fc6b839661dbc53930708","contract_sha256":"cbb7f11d58f80a48bbed5f2e6b54af0130c2c3ab82c87d4e98d205445d0202f1"},manifest},createBoundary,modules);
export default {fetch:handler};
