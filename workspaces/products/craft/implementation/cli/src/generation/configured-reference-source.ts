// Candidate type projection and inert metadata only; never lookup or integrity checks.
// Scope/open questions: REFERENCE-FIELD-FACTORY-GENERATION.md.
export interface ConfiguredFieldReference {
  readonly owner:string;
  readonly field:string;
  readonly kind:'identity-reference'|'field-projection';
  readonly target:string;
  readonly projection:readonly string[];
  readonly target_path:string;
  readonly target_type:string;
  readonly type_import:Readonly<{path:string;symbol:string;local:string}>|null;
  readonly wrappers:readonly ('optional'|'list'|'set')[];
}
export function renderReferenceType(r:ConfiguredFieldReference):string {
  const indexed=r.target_type+r.projection.map((p,i)=>(i?'["fields"]':'')+'['+JSON.stringify(p)+']').join('');
  return r.wrappers.reduceRight((type,wrapper)=>wrapper==='optional'?`(${type})|null`:`ReadonlyArray<${type}>`,indexed);
}
export function renderReferenceImports(bindings:readonly ConfiguredFieldReference[]):string {
  return bindings.map(r=>r.type_import?`import type {${r.type_import.symbol} as ${r.type_import.local}} from ${JSON.stringify(r.type_import.path)};\n`:'').join('');
}
export function renderReferenceDescriptors(name:string,bindings:readonly ConfiguredFieldReference[]):string {
  const q=JSON.stringify;
  return `export const ${name}FieldBindings = Object.freeze([${bindings.map(r=>`Object.freeze({owner:${q(r.owner)},field:${q(r.field)},kind:${q(r.kind)},target:${q(r.target)},projection:Object.freeze(${q(r.projection)} as const)} as const)`).join(',')}] as const);\n`;
}
