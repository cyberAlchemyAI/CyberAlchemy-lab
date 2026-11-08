/** Bind an original application selection to its checked technical Mapping.
 * This forms source-derived family requirements, never a resolved native basis.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import path from 'node:path';
import {dataDigest} from '../profile-engine/contracts.js';
import {parametersV5} from '../profile-engine/contracts-v5.js';
import {coreFreeze,coreRelativePath,coreSourceChildren,coreSourceDescendants,coreSourceText,coreSourceTokens,coreSourceFail as fail,type CoreSourceRange} from '../commerce/commerce-core-syntax.js';
import {assertCoreCommerceSourceOwner,parseCoreCommerceJson,type CoreCommerceSourceOwner,type CoreCommerceSourceCapture} from '../commerce/commerce-core-source-owner.js';
import {assertCoreCommerceSemanticOwner,type CoreCommerceSemanticOwner,type CoreCommerceSemanticCapture} from '../commerce/commerce-core-semantic-owner.js';
import {assertTechnicalModelOwnerV5,type CommerceTechnicalModelOwnerV5} from '../profile-engine/technical-model-v5.js';
import {assertFamilyOwnerV5,type CommerceFamilyOwnerV5} from '../profile-engine/family-v5.js';
import type {CommerceTechnicalModelHandle,CommerceDerivedFamilyHandle} from '../commerce/commerce-stages-v1.js';
import {projectCoreServiceTopologyV1} from './core-topology-bridge.js';
import type {CoreServiceTopologyV1} from './core-topology-bridge.js';
import type {TechnicalModelInspectionV5} from '../profile-engine/technical-model-v5.js';

export interface CoreApplicationFamilySelectionV1 {
 readonly schema_version:'craft.core-application-family-selection/v1-candidate';
 readonly application:string;readonly source_capture_sha256:string;
 readonly selection_source:Readonly<{path:string;sha256:string;bytes:number}>;
 readonly technical_source:Readonly<{path:string;sha256:string;bytes:number}>;
 readonly mapping:string;readonly technical_graph_sha256:string;
 readonly topology_sha256:string;readonly family_sha256:string;
 readonly services:readonly {readonly id:string;readonly module:string}[];
 readonly parameters:Readonly<{tablePrefix:string;requestBytes:4096;responseBytes:131072;bodyTimeoutMs:2000}>;
 readonly native_requirements:readonly {readonly primitive_id:string;readonly abi:string}[];
 readonly qualification:'original-application-selected-family-requirements-only;native-and-runtime-admission-not-established';
 readonly authority_effect:'none';
}

/** Validation only; the caller must source the JSON from an original capture. */
export function checkCoreApplicationProfileSelectionV1(selected:unknown,technical:TechnicalModelInspectionV5,topology:CoreServiceTopologyV1,where:CoreSourceRange){
 if(!selected||typeof selected!=='object'||Array.isArray(selected))fail('InvalidContract',where,'selected technical profile object required');
 const value=selected as Record<string,unknown>;
 if(value.schema_version!=='craft.commerce-profile-selection/v1-candidate'||value.source!==technical.source.artifact.path||value.technical_model!==technical.source.module+'@'+technical.source.version||value.selection_mapping!==technical.mapping)fail('InvalidContract',where,'selected technical module and Mapping must match original checked source');
 const parameters=parametersV5(value.parameters),rawServices=value.services;
 if(!Array.isArray(rawServices)||rawServices.some(s=>typeof s!=='string')||rawServices.length!==topology.services.length||new Set(rawServices).size!==rawServices.length||topology.services.some(s=>!rawServices.includes(s.id)))fail('InvalidContract',where,'selected services must equal the original application service set');
 return parameters;
}

export function selectCoreApplicationFamilyV1(
 sources:CoreCommerceSourceOwner,source:CoreCommerceSourceCapture,
 semantics:CoreCommerceSemanticOwner,semantic:CoreCommerceSemanticCapture,
 models:CommerceTechnicalModelOwnerV5,model:CommerceTechnicalModelHandle,
 families:CommerceFamilyOwnerV5,
):Readonly<{family:CommerceDerivedFamilyHandle;selection:CoreApplicationFamilySelectionV1}> {
 assertCoreCommerceSourceOwner(sources);assertCoreCommerceSemanticOwner(semantics);
 assertTechnicalModelOwnerV5(models);assertFamilyOwnerV5(families);
 if(families.modelOwner()!==models)fail('ForeignOwner',{path:'application.alch',start:0,end:0},'family must derive from the exact technical model owner');
 const topology=projectCoreServiceTopologyV1(sources,source,semantics,semantic),capture=sources.inspect(source),technical=models.inspect(model);
 const root=capture.reconstruction.modules.flatMap(m=>m.declarations).find(d=>d.interface_kind==='application-composition');
 if(!root||root.id!==topology.application||technical.source_capture_sha256!==capture.capture_sha256)fail('ForeignOwner',root?.syntax??{path:capture.application_path,start:0,end:0},'application and technical Mapping must share the original captured source');
 const clauses=coreSourceChildren(root.syntax,'interface-clause').filter(c=>coreSourceTokens(c).find(t=>!t.layout)?.token==='parameters');
 if(clauses.length!==1)fail('MissingMapping',root.syntax,'application requires one selected parameters reference');
 const references=coreSourceDescendants(clauses[0]!,'reference');
 if(references.length!==1)fail('InvalidContract',clauses[0]!,'selected parameters must have one source reference');
 const raw=coreSourceText(references[0]!),parts=raw.split('#');
 if(parts.length!==2||parts[1]!=='/parameters')fail('InvalidContract',references[0]!,'selected parameters must name an exact captured JSON parameters object');
 const selectionPath=path.posix.normalize(path.posix.join(path.posix.dirname(capture.application_path),parts[0]!));
 if(!coreRelativePath(selectionPath)||!selectionPath.endsWith('.json'))fail('InvalidContract',references[0]!,'normalized selected profile asset required');
 const file=capture.files.find(f=>f.path===selectionPath);
 if(!file)fail('MissingMapping',references[0]!,'selected profile asset absent from original capture');
 const selected=parseCoreCommerceJson(file.text,file.path);
 const parameters=checkCoreApplicationProfileSelectionV1(selected,technical,topology,references[0]!);
 const target={module:root.module,role:'Interface' as const,name:root.name};
 const family=families.derive(model,parameters,{kind:'application',targets:[target],omitted_capabilities:'unsupported-not-silently-executed'}),derived=families.inspect(family);
 if(derived.source_capture_sha256!==capture.capture_sha256||derived.graph_sha256!==technical.graph_sha256||derived.descriptor.family_mapping!==technical.mapping||dataDigest(derived.descriptor.technical_source)!==dataDigest(technical.source)||dataDigest(derived.descriptor.parameters)!==dataDigest(parameters))fail('InvalidContract',root.syntax,'derived family must retain the exact source, Mapping and selected parameters');
 const selection:CoreApplicationFamilySelectionV1=coreFreeze({schema_version:'craft.core-application-family-selection/v1-candidate',application:root.id,source_capture_sha256:capture.capture_sha256,selection_source:{path:file.path,sha256:file.sha256,bytes:file.bytes},technical_source:technical.source.artifact,mapping:technical.mapping,technical_graph_sha256:technical.graph_sha256,topology_sha256:dataDigest(topology),family_sha256:derived.family_sha256,services:topology.services,parameters,native_requirements:derived.native_requirements.map(r=>({primitive_id:r.primitive_id,abi:r.abi})),qualification:'original-application-selected-family-requirements-only;native-and-runtime-admission-not-established',authority_effect:'none'});
 sources.assertCurrent(source);semantics.assertCurrent(semantic);models.assertCurrent(model);families.assertCurrent(family);
 return Object.freeze({family,selection});
}
