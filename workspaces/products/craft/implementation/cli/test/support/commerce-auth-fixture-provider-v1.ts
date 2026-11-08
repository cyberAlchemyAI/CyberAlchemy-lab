/** Explicit private test authentication fixture. Never a public IdP/SDK API.
 * Source grants configure scratch role data; none assigns a live actor.
 * Open Questions: docs/COMMERCE-AUTH-READY-BRIDGE-V1.md#open-questions. */
import {DatabaseSync} from 'node:sqlite';
import {readFileSync,chmodSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createCommerceAuthFixtureDatabaseV1,inspectCommerceAuthFixtureDatabaseV1,sealCommerceAuthFixtureDatabaseV1,type CommerceAuthNativeOwnerV1,type AuthPermissionV1} from '../../src/commerce/commerce-auth-ready-bridge-v1.js';
const repo=fileURLToPath(new URL('../'.repeat(7),import.meta.url));
export interface FixtureAssignmentV1 {readonly subject:string;readonly evidence:string;readonly session:string;
 /** Test-only allowance for expensive actual-source replays; ordinary fixtures remain ten minutes. */
 readonly valid_for_seconds?:number;
 readonly routes:readonly {readonly entry:string;readonly permission:AuthPermissionV1}[]}
export function seedCommerceAuthFixtureDatabaseV1(owner:CommerceAuthNativeOwnerV1,assignment:FixtureAssignmentV1){
 const lifetime=assignment.valid_for_seconds??600;
 if(!Number.isSafeInteger(lifetime)||lifetime<1||lifetime>43200)
  throw new Error('bounded test fixture lifetime required');
 const expiry=Math.floor(Date.now()/1000)+lifetime;
 const handle=createCommerceAuthFixtureDatabaseV1(owner),place=inspectCommerceAuthFixtureDatabaseV1(owner,handle),db=new DatabaseSync(place.file);
 try{
  db.exec(readFileSync(path.join(repo,'auth-foundation/implementation/authorization-schema/migrations/0002_auth_service_epoch.sql'),'utf8'));
  db.prepare('INSERT INTO auth_authentication_evidence VALUES (?,?,?,?,?,?,?,?)').run(1,assignment.evidence,assignment.session,1,0,expiry,3,assignment.subject);
 }finally{db.close();}
 chmodSync(place.file,0o600);
 const setup=new DatabaseSync(place.file);
 try{
  setup.prepare('INSERT INTO auth_roles VALUES (?)').run('fixture-role');
  setup.prepare('INSERT INTO auth_sessions VALUES (?,?,?,?,?,?)').run(1,assignment.session,assignment.subject,'active',7,expiry);
  setup.prepare('INSERT INTO auth_session_active_roles VALUES (?,?,?)').run(1,'fixture-role',7);
  setup.prepare('INSERT INTO auth_authorization_revisions VALUES (?,?)').run(assignment.session,7);
  const seen=new Set<string>();
  for(const [i,row]of assignment.routes.entries()){
   const p=row.permission,key=JSON.stringify(p),scope='fixture-scope-'+i;
   if(!seen.has(key)){setup.prepare('INSERT INTO auth_role_permissions VALUES (?,?,?,?,?)').run('fixture-role',p.resource,p.action,p.scope,7);seen.add(key);}
   setup.prepare('INSERT INTO auth_route_authorization_bindings VALUES (?,?,?,?,?,?,?,?,?)').run(i+1,'commerce:'+row.entry,p.resource,p.action,p.scope,scope,1,1,5);
   setup.prepare('INSERT INTO auth_scope_evidence VALUES (?,?,?,?,?)').run(scope,p.resource,p.action,p.scope,1);
  }
 }finally{setup.close();}
 sealCommerceAuthFixtureDatabaseV1(owner,handle);
 return Object.freeze({handle,namespace:place.directory,file:place.file,assignment,
  mutate(sql:string){const c=new DatabaseSync(place.file);try{c.exec(sql);}finally{c.close();}},
 });
}
