import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as alch from '../../dist/index.js';

const root=path.dirname(fileURLToPath(import.meta.url));
export function runFormation({alchModule=alch,craftModule}) {
  const source=fs.readFileSync(path.join(root,'model.alch'),'utf8');
  const bindings=JSON.parse(fs.readFileSync(path.join(root,'bindings.json'),'utf8'));
  const sources=new Map();
  for(const file of fs.readdirSync(path.join(root,'fixture')))sources.set('fixture/'+file,fs.readFileSync(path.join(root,'fixture',file)));
  const expected=['Calculation','Entity','Enum','Event','Interface','Mapping','Operation','Policy','Query','Rule','State Machine','Value Object','Workflow'];
  const formed=alchModule.lowerApplicationDomain(source,bindings,sources);
  const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'alch-meta-types-'));
  try {
    for(const [relative,bytes] of Object.entries(formed.projectFiles)) {const target=path.join(scratch,relative);fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,bytes,{flag:'wx'});}
    const compiled=craftModule.compileProject(scratch);
    assert.deepEqual([...new Set(compiled.graph.nodes.map(n=>n.kind))].sort(),expected);
    assert.deepEqual(Object.fromEntries(compiled.graph.nodes.map(n=>[n.node_id,n.kind]).sort(([a],[b])=>a.localeCompare(b))),{
      'confirm-order':'Operation','dispatch-order':'Policy','eligible-order':'Rule','fee':'Calculation','find-orders':'Query','money':'Value Object','order':'Entity','order-api':'Interface','order-lifecycle':'State Machine','order-submitted':'Event','order-to-money':'Mapping','status':'Enum','submit-flow':'Workflow','submit-order':'Operation',
    });
    for(const [before,after,code] of [
      ['status sum<Status>','status sum<Order>','APPLICATION_SUM'],
      ['parent -> Order.id','parent -> Order.amount','APPLICATION_IDENTITY_REFERENCE'],
      ['steps SubmitOrder, ConfirmOrder','steps SubmitOrder, Fee','APPLICATION_REFERENCE'],
      ['case EligibleOrder -> Fee','case EligibleOrder -> Order','APPLICATION_REFERENCE'],
      ['emits OrderSubmitted','emits Order','APPLICATION_REFERENCE'],
      ['expression add(amount, 5)','expression add(missing, 5)','APPLICATION_CALCULATION'],
    ])assert.throws(()=>alchModule.parseDomainSource(source.replace(before,after)),new RegExp(code));
    const stale=structuredClone(bindings);stale.source_sha256='0'.repeat(64);
    assert.throws(()=>alchModule.lowerApplicationDomain(source,stale,sources));
    return {schema_version:'alchlang.meta-types-formation/v1-candidate',result:'pass',profile:'application-v1',meta_types:expected,positive_cases:1,negative_cases:7,scope:'authored source, exact companions and Craft graph formation; runtime behavior is qualified by the separate Craft TypeScript journey',formal_proof_observed:false,authority_effect:'none'};
  } finally {fs.rmSync(scratch,{recursive:true,force:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const craft=await import('@domainspec-v2/cli');
  console.log(JSON.stringify(runFormation({craftModule:craft}),null,2));
}
