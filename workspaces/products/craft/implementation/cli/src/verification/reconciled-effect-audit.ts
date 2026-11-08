/** Trusted native AST parser shared by separately bound verification profiles. */
export function createEffectAuditRunner(diagnostic:string,schema:string):string{
 if(!/^[A-Z_]+$/.test(diagnostic)||!/^domainspec\.[a-z-]+\/v1-candidate$/.test(schema))throw new TypeError('invalid audit identity');
 return String.raw`
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';import {pathToFileURL} from 'node:url';
const [compiler,config,input]=process.argv.slice(2),selected=JSON.parse(fs.readFileSync(input,'utf8'));
const {API}=await import(pathToFileURL(path.join(compiler,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compiler,'dist/ast/index.js')).href);
const definition=JSON.parse(selected.definition),api=new API({cwd:path.dirname(config)});
const forms=new Map(definition.forbidden_forms.map(name=>{if(typeof K[name]!=='number')throw Error('__AUDIT_DIAGNOSTIC__:unknown syntax kind');return [K[name],name];})),identifiers=new Set(definition.forbidden_identifiers);
const hash=s=>createHash('sha256').update(s).digest('hex');
const identifier=n=>n.getText().replace(/\\u(?:\{([0-9a-f]+)\}|([0-9a-f]{4}))/gi,(_,wide,narrow)=>String.fromCodePoint(parseInt(wide??narrow,16)));
try{
 const snapshot=api.updateSnapshot({openProjects:[config]}),project=snapshot.getProject(config);if(!project)throw Error('__AUDIT_DIAGNOSTIC__:missing native project');
 const modules=[];
 for(const relative_path of selected.module_paths){
  const file=path.resolve(selected.module_root,relative_path),source=project.program.getSourceFile(file);
  if(!source||project.program.getSyntacticDiagnostics(file).length)throw Error('__AUDIT_DIAGNOSTIC__:missing or invalid native syntax');
  const violations=[];let visits=0;
  const visit=(n,depth=0)=>{
   if(++visits>1000000||depth>512)throw Error('__AUDIT_DIAGNOSTIC__:bounded AST capacity exceeded');
   const form=forms.get(n.kind);if(form&&violations.length<64)violations.push({code:'impure-form',name:form,offset:n.pos});
   if(n.kind===K.Identifier){const name=identifier(n);if(identifiers.has(name)&&violations.length<64)violations.push({code:'ambient-effect',name,offset:n.pos});}
   n.forEachChild(child=>visit(child,depth+1));
  };visit(source);
  modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),violations});
 }
 snapshot.dispose();process.stdout.write(JSON.stringify({schema_version:'__OBSERVATION_SCHEMA__',phase:selected.phase,definition_sha256:hash(selected.definition),modules}));
}finally{api.close();}
`.replaceAll('__AUDIT_DIAGNOSTIC__',diagnostic).replaceAll('__OBSERVATION_SCHEMA__',schema);
}
