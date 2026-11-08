import {cpSync,mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
// Open questions: frozen/installed qualification BA15/18.
const cli=path.resolve(import.meta.dirname,'../..');
export function createBusinessApplicationFixture(t:{after(callback:()=>void):void},profile:string,multiple=false){
 const root=mkdtempSync(path.join(os.tmpdir(),'business-public-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(cli,'test/profile-engine/fixtures/business-notice'),root,{recursive:true});
 const file=path.join(root,'project.json'),project=JSON.parse(readFileSync(file,'utf8'));project.profiles[0]={id:profile,version:'1.0.0',path:path.join(cli,'profiles',profile)};
 if(multiple){cpSync(path.join(root,'domain.alch'),path.join(root,'audit.alch'));cpSync(path.join(root,'business-semantics.json'),path.join(root,'audit-semantics.json'));project.application_models.push({id:'audit',source:'audit.alch',semantics:'audit-semantics.json'});project.application_intents.push({...project.application_intents[0],id:'auditNotice',application_id:'audit'});}
 writeFileSync(file,JSON.stringify(project));return {root,file,project};
}
