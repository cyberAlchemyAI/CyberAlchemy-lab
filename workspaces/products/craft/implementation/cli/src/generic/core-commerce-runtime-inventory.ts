/** Files generated with a service are immutable; SQLite and identity components
 * are live runtime state checked by their original native owners.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
export type CoreCommerceRuntimeFile=Readonly<{path:string;sha256:string;bytes:number}>;

// The storage owner creates exactly these identity-component members under a
// source-digested transaction or Workflow directory. Each live component pins
// its physical members; this outer inventory rejects unrelated additions.
const identityMember=/^(?:identity|identity-reopen-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\/(?:[0-9a-f]{64}|workflow-[0-9a-f]{64})\/(?:package\.json|identity-component\.json|(?:commerce-domain-values|values-and-codecs|commerce-identity-model|context)\.(?:ts|js))$/i;

export function isCoreCommerceMutableServiceFile(relativePath:string):boolean{
 return /^store\.sqlite(?:-wal|-shm|-journal)?$/.test(relativePath)||identityMember.test(relativePath);
}

export function staticCoreCommerceServiceFiles(rows:readonly CoreCommerceRuntimeFile[]):readonly CoreCommerceRuntimeFile[]{
 return rows.filter(row=>!isCoreCommerceMutableServiceFile(row.path));
}
