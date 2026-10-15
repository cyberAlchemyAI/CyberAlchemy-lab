import * as entry_SemanticGrounding from '../../entries/SemanticGrounding/app/function/index.mjs';
import * as entry_GroundingEvidence from '../../entries/GroundingEvidence/app/function/index.mjs';
import * as entry_NonCollapse from '../../entries/NonCollapse/app/function/index.mjs';
import * as entry_NonCollapseEvidence from '../../entries/NonCollapseEvidence/app/function/index.mjs';
import * as entry_Orthogonality from '../../entries/Orthogonality/app/function/index.mjs';
import * as entry_OrthogonalityEvidence from '../../entries/OrthogonalityEvidence/app/function/index.mjs';
import * as entry_LanguageReadiness from '../../entries/LanguageReadiness/app/function/index.mjs';
import * as entry_ScopeReadiness from '../../entries/ScopeReadiness/app/function/index.mjs';
import * as entry_ConceptDisposition from '../../entries/ConceptDisposition/app/function/index.mjs';
import * as entry_PackReadiness from '../../entries/PackReadiness/app/function/index.mjs';
import * as entry_AlchHandoffReadiness from '../../entries/AlchHandoffReadiness/app/function/index.mjs';
const entrypoints={"SemanticGrounding":entry_SemanticGrounding,"GroundingEvidence":entry_GroundingEvidence,"NonCollapse":entry_NonCollapse,"NonCollapseEvidence":entry_NonCollapseEvidence,"Orthogonality":entry_Orthogonality,"OrthogonalityEvidence":entry_OrthogonalityEvidence,"LanguageReadiness":entry_LanguageReadiness,"ScopeReadiness":entry_ScopeReadiness,"ConceptDisposition":entry_ConceptDisposition,"PackReadiness":entry_PackReadiness,"AlchHandoffReadiness":entry_AlchHandoffReadiness};
export const routes=[
  {
    "id": "SemanticGrounding",
    "method": "POST",
    "path": "/define/semantic-grounding"
  },
  {
    "id": "GroundingEvidence",
    "method": "POST",
    "path": "/define/grounding-evidence"
  },
  {
    "id": "NonCollapse",
    "method": "POST",
    "path": "/define/non-collapse"
  },
  {
    "id": "NonCollapseEvidence",
    "method": "POST",
    "path": "/define/non-collapse-evidence"
  },
  {
    "id": "Orthogonality",
    "method": "POST",
    "path": "/define/orthogonality"
  },
  {
    "id": "OrthogonalityEvidence",
    "method": "POST",
    "path": "/define/orthogonality-evidence"
  },
  {
    "id": "LanguageReadiness",
    "method": "POST",
    "path": "/define/language-readiness"
  },
  {
    "id": "ScopeReadiness",
    "method": "POST",
    "path": "/define/scope-readiness"
  },
  {
    "id": "ConceptDisposition",
    "method": "POST",
    "path": "/define/concept-disposition"
  },
  {
    "id": "PackReadiness",
    "method": "POST",
    "path": "/define/pack-readiness"
  },
  {
    "id": "AlchHandoffReadiness",
    "method": "POST",
    "path": "/define/alch-handoff-readiness"
  }
];
export async function invoke(entry,input,env={},io={}){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.invoke(input,env,io);}
export function createInvoker(entry,observe){const selected=entrypoints[entry];if(!selected){const error=new Error('SERVICE_ENTRY_NOT_FOUND');error.code='SERVICE_ENTRY_NOT_FOUND';throw error;}return selected.createInvoker(observe);}
export async function handler(request,env={},io={}){const url=new URL(request.url),samePath=routes.filter(route=>route.path===url.pathname);if(!samePath.length)return Response.json({error:'NOT_FOUND'},{status:404});const route=samePath.find(route=>route.method===request.method);if(!route)return Response.json({error:'METHOD_NOT_ALLOWED'},{status:405});return entrypoints[route.id].handler(request,env,{...io,signal:io.signal??request.signal});}
export default {fetch:handler};
