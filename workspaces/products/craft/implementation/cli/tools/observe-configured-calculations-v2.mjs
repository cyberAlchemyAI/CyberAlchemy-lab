import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

// Independent closed-source observer. No generator import or target evaluation.
// The pinned normalization perimeter assumes inert objects and standard intrinsics.
const supportDigests=Object.freeze({
  arithmetic:'ee7d677271f85298f6f2d47e78f5169f510950bd65379f4de0f90b681301f349',
  division:'bc4156a818172e215d93664c03e542c2e57557f3ab95eadc9c895375914831db',
});
const hash=s=>createHash('sha256').update(s).digest('hex');
const canonical=v=>JSON.stringify(v&&typeof v==='object'?Array.isArray(v)?v.map(x=>JSON.parse(canonical(x))):Object.fromEntries(Object.keys(v).sort().map(k=>[k,JSON.parse(canonical(v[k]))])):v);
const frozen=v=>v&&typeof v==='object'?Array.isArray(v)?`Object.freeze([${v.map(frozen).join(',')}])`:`Object.freeze({${Object.entries(v).map(([k,x])=>`[${JSON.stringify(k)}]:${frozen(x)}`).join(',')}})`:JSON.stringify(v);
/** expected is supplied by the checked-plan caller, never read from the target.
 * The small binding grammar is intentionally exact, not arbitrary TypeScript.
 */
export function observeCalculationV2Binding(provider,wrapper,expected,contract){
  const reject=reason=>{throw new Error('CALCULATION_OBSERVER:'+reason);};
  const {descriptor_sha256,...body}=expected.descriptor;
  if(hash(canonical(body))!==descriptor_sha256||hash(provider)!==body.provider.sha256)reject('stale descriptor or provider');
  if(body.contract_sha256!==hash(canonical(contract))||body.ontology_calculation!==contract.ontology_calculation||canonical(body.inputs)!==canonical(contract.inputs)||canonical(body.result)!==canonical(contract.result))reject('contract binding');
  if(body.return_semantics!=='value'||body.effect_contract!=='none'||body.dependency_contract!=='explicit-only'||body.failure_contract!=='declared'||body.result_consumption!=='complete'||body.primary_callable_count!==1||body.supporting_exports!=='explicit-only')reject('descriptor perimeter');
  const binding=`import {calculate} from ${JSON.stringify(expected.provider_import)};\nexport const ${expected.callable}=Object.freeze(Object.assign(calculate,{descriptor:${frozen(expected.descriptor)}}));\n`;
  if(wrapper!==binding)reject('unbound or changed callable');
  return observeCalculationV2(provider,contract);
}
export function observeCalculationV2(source,contract){
  const reject=reason=>{throw new Error('CALCULATION_OBSERVER:'+reason);};
  const marker='// Checked arithmetic program follows.\n',at=source.indexOf(marker);
  const includesDivision=(()=>{const visit=node=>node&&typeof node==='object'&&(node.op==='divide'||visit(node.left)||visit(node.right));return visit(contract.expression);})();
  if(at<0||hash(source.slice(0,at+marker.length))!==supportDigests[includesDivision?'division':'arithmetic'])reject('support perimeter');
  const lines=source.slice(at+marker.length).trimEnd().split('\n');
  const signature=lines.shift();
  const names=contract.inputs.map(p=>p.name);
  if(signature!==`export const calculate = (input:Readonly<{${names.map(n=>`readonly ${JSON.stringify(n)}:CalculationUInt64Input`).join(';')}}>):bigint=>{`)reject('signature');
  if(lines.shift()!==`  const d=properties(input,${JSON.stringify(names)});`)reject('input perimeter');
  const values=new Map();
  for(const [i,name] of names.entries()){
    if(lines.shift()!==`  const p${i}=normalize(d[${JSON.stringify(name)}]!.value);`)reject('parameter binding');
    values.set('p'+i,{op:'input',name});
  }
  const operand=s=>{
    if(/^(0|[1-9][0-9]*)n$/.test(s)){const value=s.slice(0,-1);if(value.length>20||BigInt(value)>18446744073709551615n)reject('literal');return {op:'literal',value};}
    if(!values.has(s))reject('undeclared value');return values.get(s);
  };
  const nodes=[];let next=0;
  while(lines[0]?.startsWith('  const ')){
    const line=lines.shift();
    let name,value;
    const b=/^  const (v[0-9]+)=checked\((p[0-9]+|v[0-9]+|[0-9]+n)([+*-])(p[0-9]+|v[0-9]+|[0-9]+n)\);$/.exec(line);
    const d=/^  const (v[0-9]+)=divide\((p[0-9]+|v[0-9]+|[0-9]+n),(p[0-9]+|v[0-9]+|[0-9]+n),"(floor|ceil|reject)"\);$/.exec(line);
    if(b){name=b[1];value={op:{'+':'add','-':'subtract','*':'multiply'}[b[3]],left:operand(b[2]),right:operand(b[4])};}
    else if(d){name=d[1];if(d[4]!==contract.division_rounding)reject('rounding');value={op:'divide',left:operand(d[2]),right:operand(d[3])};}
    else reject('expression perimeter');
    if(name!=='v'+next++)reject('instruction identity');values.set(name,value);nodes.push(value);
  }
  const returned=/^  return (p[0-9]+|v[0-9]+|[0-9]+n);$/.exec(lines.shift()??'');
  if(!returned||lines.length!==1||lines[0]!=='};')reject('complete primitive return');
  if(canonical(operand(returned[1]))!==canonical(contract.expression))reject('expression meaning');
  const expected=[];const walk=e=>{if(e.left){walk(e.left);walk(e.right);expected.push(e);}};walk(contract.expression);
  if(canonical(nodes)!==canonical(expected))reject('evaluation order or unconsumed instructions');
  return {result:'pass',source_sha256:hash(source),instructions:nodes.length,return_kind:'bigint',authority_effect:'none'};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  const cases=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
  const results=cases.map(c=>{try{return observeCalculationV2(fs.readFileSync(c.path,'utf8'),c.contract);}catch(e){return {result:'fail',reason:e.message};}});
  console.log(JSON.stringify({result:results.every(r=>r.result==='pass')?'pass':'fail',results}));
  if(results.some(r=>r.result==='fail'))process.exitCode=1;
}
