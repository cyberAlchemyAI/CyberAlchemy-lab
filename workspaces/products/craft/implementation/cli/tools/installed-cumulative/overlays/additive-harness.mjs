/** Test-only authored-file changes precede original capture; no business callbacks. */
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import {environment,json,cleanup,rootEntry,open} from './http-harness.mjs';
let serial=0;
// Retain every original outcome assertion while making authored test producers
// obey the established explicit text-unit and 4096-character source-line rules.
function normalizeBoundedFixtureSource(source){
 if(source.includes('length(HttpSmall(item.label))'))
  source=once(source,'length(HttpSmall(item.label))','length-scalars(HttpSmall(item.label))');
 const blob=JSON.stringify('x'.repeat(9000)),chunk=JSON.stringify('x'.repeat(3000));
 const fields=['left','middle','right'].map(name=>'  field '+name+' <- '+chunk).join('\n');
 const record=name=>'value-object '+name+':\n  left '+name+'Chunk\n  middle '+name+'Chunk\n  right '+name+'Chunk\n\nvalue-object '+name+'Chunk:\n  carrier String\n  utf8-bytes 1..10000\n  unicode-scalars 1..10000';
 const scalar=name=>'value-object '+name+':\n  carrier String\n  utf8-bytes 1..10000\n  unicode-scalars 1..10000';
 if(source.includes(scalar('HttpReadPadding'))&&source.includes('  expression '+blob)){
  source=once(source,scalar('HttpReadPadding'),record('HttpReadPadding'));
  source=once(source,'  expression '+blob,fields);
 }
 if(source.includes(scalar('HttpPadding'))&&source.includes('  field padding <- '+blob)){
  source=once(source,scalar('HttpPadding'),record('HttpPadding')+'\n\nmapping HttpPaddingLiteral:\n  input decision Decision\n  target HttpPadding\n  total true\n'+fields);
  source=once(source,'  field padding <- '+blob,'  field padding <- HttpPaddingLiteral(decision)');
 }
 return source;
}

export function authored({fixture='approval',changeSource,changeHttp,changeBase}={}){
 const env=environment(),dir=path.join(env.work,'additional-'+process.pid+'-'+(++serial));mkdirSync(dir,{recursive:true,mode:0o700});const root=path.join(dir,'authored');cpSync(path.join(env.fixtures,fixture),root,{recursive:true});
 if(changeSource){const p=path.join(root,'business.alch');writeFileSync(p,normalizeBoundedFixtureSource(changeSource(readFileSync(p,'utf8'))));}
 const hp=path.join(root,'contracts/http-profile.json'),bp=path.join(root,'contracts/selected-profile.json'),http=json(hp),base=json(bp);
 if(changeHttp)changeHttp(http);if(changeBase){changeBase(base);const limits=json(path.join(root,'contracts/bounds.json'));limits.computation.limits={...base.limits};writeFileSync(path.join(root,'contracts/bounds.json'),JSON.stringify(limits));writeFileSync(path.join(root,'contracts/transactions.json'),JSON.stringify(base.transaction_bounds));}
 writeFileSync(hp,JSON.stringify(http));writeFileSync(bp,JSON.stringify(base));const oracle=json(path.join(root,'http-oracle.json'));
 return{dir,authored:root,http,base,oracle,rows:json(path.join(root,'fixture-rows.json')),input:{sourcePath:path.join(root,'business.alch'),profilePath:bp,httpProfilePath:hp,...(oracle.additional_source_paths.length?{additionalSourcePaths:oracle.additional_source_paths.map(p=>path.join(root,p))}:{})}};
}
export function accept(owner,h,dir){const r=owner.review(h,'independent-C09-additional');owner.accept(h,{decision_id:'C09-extra-'+(++serial),owner:'independent-C09-additional',outcome:'accepted',reviewed_digest:r.review_sha256},path.join(dir,'review-'+serial+'.json'));}
export async function generated(options={}){const f=authored(options),owner=createGenericHttpCompositionOwner();let h,primary;try{h=await owner.prepare(f.input);accept(owner,h,f.dir);const inspection=owner.inspect(h),out=path.join(f.dir,'generated'),manifest=await owner.generate(h,{entry:rootEntry,outputDirectory:out});const module=await import(pathToFileURL(path.join(out,'application.mjs')).href);return{...f,out,manifest,inspection,createOwner:module.createGeneratedApplicationOwner};}catch(e){primary=e;throw e;}finally{await cleanup([()=>h?owner.dispose(h):undefined],primary);}}
export async function withModified(options,fn,openOptions={}){const f=await generated(options);const r=await open(f,openOptions);let primary;try{return await fn(r,f);}catch(e){primary=e;throw e;}finally{await cleanup([()=>r.close()],primary);}}
export function once(source,before,after){assert.equal(source.split(before).length-1,1);return source.replace(before,after);}
export function setResponseTotal(expression){return source=>once(source,'field total <- decision.total','field total <- '+expression);}
