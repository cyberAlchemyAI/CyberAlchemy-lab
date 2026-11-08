import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const extension=path.resolve(import.meta.dirname,'..'),implementation=path.resolve(extension,'../../implementation');
const out=process.argv[2];if(process.argv.length!==3||!out)throw Error('usage: node validation/run.mjs <new-output-directory>');mkdirSync(out);
const reports=[];
for(const [name,directory]of [['checkout-quote',extension],['checkout-quote-http',extension],['quantity-price',path.resolve(extension,'../portable-conformance-v1')],['shipping-options',path.resolve(extension,'../portable-conformance-v1')]]){
 const target=path.resolve(out,name);let exit=0;
 try{execFileSync(process.execPath,[path.join(implementation,'dist/cli.js'),'conformance',path.join(directory,name+'.alch'),'--fixtures',path.join(directory,name+'.fixtures.json'),'--out',target],{stdio:'inherit'});}catch(e){exit=e.status??1;}
 const bytes=readFileSync(path.join(target,'report.json')),report=JSON.parse(bytes);if(exit&&report.status==='pass')throw Error('CONFORMANCE_EXIT_MISMATCH');reports.push({name,source:path.join(directory,name+'.alch'),fixtures:path.join(directory,name+'.fixtures.json'),report_sha256:createHash('sha256').update(bytes).digest('hex'),...report});
}
const suite={schema_version:'alchlang.module-input-conformance-suite/v1',status:reports.every(r=>r.status==='pass')?'pass':'fail',count:reports.reduce((n,r)=>n+r.count,0),reports,authority_effect:'none',claim:'Finite controlled conformance, including standalone regression cases; no live remote implementation identity or deployment claim.'};
writeFileSync(path.resolve(out,'report.json'),JSON.stringify(suite,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({status:suite.status,count:suite.count,report:path.resolve(out,'report.json')}));if(suite.status!=='pass')process.exitCode=1;
