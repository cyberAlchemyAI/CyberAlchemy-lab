/** Deliberately small common grammar; compilation rejects target-specific semantics. */
export function portablePattern(pattern:string):boolean{
 if(!pattern.startsWith('^')||!pattern.endsWith('$'))return false;
 let body=pattern.slice(1,-1);if(body.startsWith('(')&&body.endsWith(')'))body=body.slice(1,-1);
 if(!body)return false;
 for(const branch of body.split('|')){
  if(!branch)return false;let rest=branch;
  while(rest){const atom=/^(?:[A-Za-z0-9_ -]|\[[A-Za-z0-9_ -]+\])/.exec(rest);if(!atom)return false;rest=rest.slice(atom[0].length);
   const repeat=/^(?:\?|\{([0-9]+)(?:,([0-9]+))?\})/.exec(rest);if(repeat){if(repeat[1]&&(Number(repeat[1])>1000||repeat[2]&&(Number(repeat[2])>1000||Number(repeat[2])<Number(repeat[1]))))return false;rest=rest.slice(repeat[0].length);}
  }
 }
 try{new RegExp(pattern);}catch{return false;}return true;
}
export function validatePortableSource(source:any):void{
 const portable=source.model?.portability==='node-rust-v1',rust=source.model?.endpoint?.target==='rust-http';
 const reject=(name:string,field:string,message:string):never=>{const n=source.ontology?.nodes?.find((n:any)=>n.name===name),line=n?.properties?.find((p:any)=>p.name===field)?.line??n?.source?.line??1;throw Error(`DS_TARGET_UNSUPPORTED: ${source.ontology?.source?.path??'source.alch'}:${line}: ${name}.${field}: ${message}`);};
 if(portable||rust)for(const [name,fields]of Object.entries(source.model.schemas) as [string,any][])for(const [field,s]of Object.entries(fields) as [string,any][])if(s.pattern!==undefined){
  if(portable&&!portablePattern(s.pattern))reject(name,field,'pattern is outside portability node-rust-v1');
  if(rust&&(!/^[A-Za-z0-9_^$[\]{}()+*?|, -]+$/.test(s.pattern)||s.pattern.includes('(?')))reject(name,field,'unsupported Rust pattern syntax');
 }
 if(portable){const walk=(v:any):void=>{if(typeof v==='string'){for(const c of v){const n=c.codePointAt(0)!;if(n>=0xd800&&n<=0xdfff)reject('contract','literal','unpaired Unicode surrogate');}}else if(v&&typeof v==='object')Object.values(v).forEach(walk);};walk(source.contract);}
}
