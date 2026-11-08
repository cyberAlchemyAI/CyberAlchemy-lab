import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
const extension=path.resolve(import.meta.dirname,'..'),implementation=path.resolve(extension,'../../implementation');
const out=process.argv[2];if(process.argv.length!==3||!out)throw Error('usage: node validation/run.mjs <new-output-directory>');
mkdirSync(out);const reports=[];
for(const module of ['quantity-price','shipping-options']){
 const target=path.resolve(out,module);let exit=0;
 try{execFileSync(process.execPath,[path.join(implementation,'dist/cli.js'),'conformance',path.join(extension,module+'.alch'),'--fixtures',path.join(extension,module+'.fixtures.json'),'--out',target],{stdio:'inherit'});}catch(e){exit=e.status??1;}
 const report=JSON.parse(readFileSync(path.join(target,'report.json'),'utf8'));reports.push({module,report_sha256:createHash('sha256').update(readFileSync(path.join(target,'report.json'))).digest('hex'),...report});if(exit&&report.status==='pass')throw Error('CONFORMANCE_EXIT_MISMATCH');
}
const result={schema_version:'alchlang.portable-suite/v1',status:reports.every(r=>r.status==='pass')?'pass':'fail',count:reports.reduce((n,r)=>n+r.count,0),reports,authority_effect:'none',claim:'Finite controlled conformance; no deployment or product approval.'};
writeFileSync(path.resolve(out,'report.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({status:result.status,count:result.count,report:path.resolve(out,'report.json')}));if(result.status!=='pass')process.exitCode=1;
