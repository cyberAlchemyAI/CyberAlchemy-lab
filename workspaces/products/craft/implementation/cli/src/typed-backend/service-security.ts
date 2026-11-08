// Closed service security contract. Open Questions: ../../../development/inference-service-binding-plan/PLAN.md.
export interface ServiceSecurity {
  authentication: 'deferred' | 'auth-foundation';
  authorization: 'deferred' | 'tenant-permissions';
  scope: 'shared-public' | 'tenant-principal';
}
export function compileServiceSecurity(input: unknown, routes: {access?: string}[]): ServiceSecurity {
  const x=input as Record<string, unknown>;
  if (!x || typeof x !== 'object' || Array.isArray(x) || Object.keys(x).sort().join(',') !== 'authentication,authorization,scope') throw Error('SERVICE_SECURITY_CONTRACT');
  const legacy=x.authentication==='deferred' && x.authorization==='deferred' && x.scope==='shared-public';
  const protectedMode=x.authentication==='auth-foundation' && x.authorization==='tenant-permissions' && x.scope==='tenant-principal';
  if ((!legacy && !protectedMode) || !Array.isArray(routes) || routes.length<1 || routes.length>32 || routes.some(r=>protectedMode ? !['public','protected'].includes(r.access??'') : r.access!==undefined)) throw Error('SERVICE_SECURITY_CONTRACT');
  return {...x} as unknown as ServiceSecurity;
}
