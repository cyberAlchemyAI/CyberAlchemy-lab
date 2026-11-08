/** Fixed successor resource registry. Entries describe schemas, never support or custody.
 * Open Questions: docs/U0-SHARED-CONTRACTS.md. Alch mirror is generated. */
export const BUSINESS_CONTRACT_RESOURCES_V2=Object.freeze(([
 {name:'spec',file:'business-spec-v2.schema.json',version:'alchlang.business-spec/v2-candidate'},
 {name:'capture',file:'business-capture-v2.schema.json',version:'craft.business-capture/v2-candidate'},
 {name:'review',file:'business-review-v2.schema.json',version:'craft.business-review/v2-candidate'},
 {name:'decision',file:'business-decision-v2.schema.json',version:'craft.business-decision/v2-candidate'},
 {name:'lock',file:'business-authoring-lock-v2.schema.json',version:'craft.business-authoring-lock/v2-candidate'},
 {name:'wire',file:'operation-json-post-v2.schema.json',version:'craft.operation-json-post/v2-candidate'},
 {name:'coverage',file:'business-coverage-v2.schema.json',version:'craft.business-coverage/v2-candidate'},
 {name:'output',file:'business-output-v2.schema.json',version:'craft.business-output/v2-candidate'},
 {name:'output-result',file:'business-output-result-v2.schema.json',version:'craft.business-output-result/v2-candidate'},
 {name:'support-cell',file:'business-support-cell-v2.schema.json',version:'craft.business-support-cell/v2-candidate'},
] as const).map(resource=>Object.freeze(resource)));
export type BusinessContractResourceNameV2=typeof BUSINESS_CONTRACT_RESOURCES_V2[number]['name'];
