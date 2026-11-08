// Private immutable Entity composition; identity equality, not record equality.
// Scope/open questions: EMBEDDED-ENTITY-FACTORY-GENERATION.md.
export function renderEntitySupport():string {
  return `const ownedEntityValue = <T>(provider:Readonly<{isOwned:(input:unknown)=>input is T;key:(input:unknown)=>string}>):ValueProtocol<T> => Object.freeze({
  normalize:(input:unknown):T=>{if(!provider.isOwned(input)) throw new TypeError('UNOWNED_ENTITY');return input;},
  key:(value:T):string=>part('Entity') + part(provider.key(value)),
});
`;
}
