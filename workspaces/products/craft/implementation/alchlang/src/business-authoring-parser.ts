import {BUSINESS_AUTHORING_LIMITS} from './business-authoring-protocol.js';
import {BUSINESS_SPEC_V2,BUSINESS_SOURCE_V2_MARKER,BUSINESS_AUTHORING_V2_LIMITS,type BusinessSpecDataV2,type ParsedBusinessSourceV2,type DirectBusinessRuleV2,type BusinessLogicalEntryV2,type BusinessClaimV2} from './business-authoring-protocol-v2.js';
import type {BusinessSpecData,BusinessScenario,BusinessObligation,ParsedBusinessSource,BusinessClaim,BusinessEntity,BusinessRequirement,BusinessDefinition,BusinessRule,BusinessOperation,BusinessCapability,BusinessParameter} from './business-authoring-protocol.js';
import {businessReject,businessHash,businessCanonical,businessSourceKey,businessIdentifier,businessSymbol,freezeBusinessData} from './business-authoring-model.js';
import type {BusinessParserOwnerV2} from './business-authoring-stages-v2.js';
export {BusinessSourceRejected} from './business-authoring-model.js';
// Open questions: implementation-plan/TASKS.md B03 and later stages.
type Row={text:string;raw:string;line:number;column:number;depth:number};
type Block={kind:string;id:string;version?:string;row:Row;rows:Row[]};
const parsedRegistry=new WeakMap<object,string>();
const id='([A-Za-z_][A-Za-z0-9_-]{0,127})', param='([a-z][a-z0-9]*(?:_[a-z0-9]+)*)';
export function assertParsedBusinessSourceCurrent(value:ParsedBusinessSource):void {
  const fingerprint=value&&typeof value==='object'?parsedRegistry.get(value):undefined;
  if(!fingerprint||value.kind!=='parsed-business-source')businessReject('BUSINESS_HANDLE','business.alch',1,1,'registered parsed source required');
  if(businessHash(businessCanonical(value))!==fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',value.source.path,1,1,'parsed source changed');
}
/** Legacy API stays explicitly v1; the versioned dispatcher returns a discriminated union. */
export function parseBusinessSource(text:string,sourceName='business.alch'):ParsedBusinessSource {
 return parseBusinessSourceForContract(text,sourceName,'v1');
}
export function parseBusinessSourceV2(text:string,sourceName='business.alch'):ParsedBusinessSourceV2 {
 return parseBusinessSourceForContract(text,sourceName,'v2');
}
export function assertParsedBusinessSourceV2Current(value:ParsedBusinessSourceV2):void {
 const fingerprint=value&&typeof value==='object'?parsedRegistry.get(value):undefined;
 if(!fingerprint||value.kind!=='parsed-business-source-v2')businessReject('BUSINESS_HANDLE', 'business.alch',1,1,'original successor parser handle required');
 if(businessHash(businessCanonical(value))!==fingerprint)businessReject('BUSINESS_SOURCE_DRIFT',value.source.path,1,1,'captured successor source changed');
}
export function parseVersionedBusinessSource(text:string,sourceName='business.alch'):ParsedBusinessSource|ParsedBusinessSourceV2 {
 if(typeof text!=='string')businessReject('BUSINESS_SYNTAX',sourceName,1,1,'source must be text');
 if(Buffer.byteLength(text,'utf8')>BUSINESS_AUTHORING_LIMITS.source_bytes)businessReject('BUSINESS_SOURCE_BUDGET',sourceName,1,1,'source exceeds 1 MiB');
 const first=text.split(/\r?\n/).find(row=>row.trim()&&!row.trimStart().startsWith('#'));
 if(first?.trimStart().startsWith('source-contract '))return parseBusinessSourceV2(text,sourceName);
 return parseBusinessSource(text,sourceName);
}
function parseBusinessSourceForContract(text:string,sourceName:string,version:'v1'):ParsedBusinessSource;
function parseBusinessSourceForContract(text:string,sourceName:string,version:'v2'):ParsedBusinessSourceV2;
function parseBusinessSourceForContract(text:string,sourceName:string,version:'v1'|'v2'):ParsedBusinessSource|ParsedBusinessSourceV2 {
  const v2=version==='v2';
  const source=businessSourceKey(sourceName);
  const fail:(code:string,row:Row|undefined,message:string)=>never=(code,row,message)=>businessReject(code,source,row?.line??1,row?.column??1,message);
  if(typeof text!=='string')fail('BUSINESS_SYNTAX',undefined,'source must be text');
  const bytes=Buffer.byteLength(text,'utf8');
  if(bytes>BUSINESS_AUTHORING_LIMITS.source_bytes)fail('BUSINESS_SOURCE_BUDGET',undefined,'source exceeds 1 MiB');
  // Reject lone surrogates instead of silently replacing original source bytes.
  if(Buffer.from(text,'utf8').toString('utf8')!==text)fail('BUSINESS_SYNTAX',undefined,'valid Unicode source required');
  const lines=text.split('\n');
  if(lines.length>BUSINESS_AUTHORING_LIMITS.lines)fail('BUSINESS_SOURCE_BUDGET',undefined,'line budget exceeded');
  const sha256=businessHash(text),rows:Row[]=[];
  for(let i=0;i<lines.length;i++){
    const raw=i<lines.length-1?lines[i]!.replace(/\r$/,''):lines[i]!;
    if(/\t|\r|\0/.test(raw))fail('BUSINESS_SYNTAX',{line:i+1,column:1} as Row,'tabs, bare CR and NUL are forbidden');
    if(!raw.trim()||raw.trimStart().startsWith('#'))continue;
    if(raw.length>4096)fail('BUSINESS_SOURCE_BUDGET',{line:i+1,column:1} as Row,'source fact line exceeds frozen span budget');
    const spaces=raw.length-raw.trimStart().length;
    if(raw.slice(0,spaces)!==' '.repeat(spaces)||spaces%2)fail('BUSINESS_SYNTAX',{line:i+1,column:1} as Row,'exact two-space indentation required');
    if(spaces/2>BUSINESS_AUTHORING_LIMITS.depth)fail('BUSINESS_SOURCE_BUDGET',{line:i+1,column:spaces+1} as Row,'nesting budget exceeded');
    rows.push({text:raw.slice(spaces),raw,line:i+1,column:spaces+1,depth:spaces/2});
  }
  const spans:BusinessSpecData['source_spans'][number][]=[],obligations:BusinessObligation[]=[];
  const record=(row:Row,selector:string,kind:BusinessObligation['kind'])=>{
    const unique=v2?'line:'+row.line:selector+'/line:'+row.line;
    if(unique.length>4096)fail('BUSINESS_SOURCE_BUDGET',row,'provenance selector exceeds frozen budget');
    spans.push({selector:unique,source,line:row.line,column:row.column,text:row.raw,source_sha256:sha256});
    obligations.push({selector:unique,kind:v2?'clause':kind,span_selector:unique});
  };
  const ident=(value:string,row:Row,portable=false)=>businessIdentifier(value,source,row.line,row.column,portable);
  const quoted=(value:string,row:Row):string=>{
    try{const result:unknown=JSON.parse(value);if(typeof result==='string'&&result.trim())return result;}catch{}
    return fail('BUSINESS_SYNTAX',row,'nonempty JSON string required');
  };
  const match=(row:Row,pattern:string):RegExpMatchArray=>row.text.match(new RegExp('^'+pattern+'$'))??fail('BUSINESS_SYNTAX',row,'malformed or unsupported clause');
  let identity:BusinessSpecData['identity']|undefined,owner:string|undefined;
  const blocks:Block[]=[],declared=new Map<string,Row>();let active:Block|undefined;
  if(v2&&(!rows[0]||rows[0].depth!==0||rows[0].text!==BUSINESS_SOURCE_V2_MARKER))fail('BUSINESS_SOURCE_VERSION',rows[0],'explicit successor header must be the first source fact');
  for(const row of rows){
    if(v2&&row===rows[0]){record(row,'source-contract','clause');continue;}
    if(row.depth){if(!active)fail('BUSINESS_SYNTAX',row,'clause has no declaration');active.rows.push(row);continue;}
    active=undefined;
    if(row.text.startsWith('business-model ')){
      if(identity)fail('BUSINESS_AMBIGUOUS',row,'one business-model header required');
      const m=match(row,'business-model '+id+' version (\\S+) (.+)');const key=ident(m[1]!,row);
      identity={namespace:key,stable_id:key,version:m[2]!,title:quoted(m[3]!,row),owner:''};record(row,'model:'+key,'identity');continue;
    }
    if(row.text.startsWith('owner ')){
      if(owner!==undefined)fail('BUSINESS_AMBIGUOUS',row,'duplicate owner');owner=match(row,'owner (\\S+)')[1]!;record(row,'model/owner','identity');continue;
    }
    const m=match(row,(v2?'(requirement|entity|definition|formal-claim|rule|operation|entry) ':'(requirement|entity|definition|formal-claim|rule|operation|capability) ')+id+'(?: version (\\S+))?:');
    const kind=m[1]!,key=ident(m[2]!,row);
    if((kind==='formal-claim')!==!!m[3])fail('BUSINESS_SYNTAX',row,'only formal claims require version');
    const normalized=businessSymbol(key);
    if(declared.has(normalized))fail('BUSINESS_AMBIGUOUS',row,'duplicate or normalization-colliding declaration '+key);
    declared.set(normalized,row);active={kind,id:key,version:m[3],row,rows:[]};blocks.push(active);
    if(blocks.length>(v2?BUSINESS_AUTHORING_V2_LIMITS.definitions+BUSINESS_AUTHORING_V2_LIMITS.claims+BUSINESS_AUTHORING_V2_LIMITS.requirements+4:BUSINESS_AUTHORING_LIMITS.declarations))fail('BUSINESS_SOURCE_BUDGET',row,'declaration budget exceeded');
    record(row,kind+':'+key,kind==='capability'?'exposure':'declaration');
  }
  if(!identity)fail('BUSINESS_REQUIRED',undefined,'business-model header required');
  if(owner===undefined)fail('BUSINESS_REQUIRED',undefined,'owner required');
  identity={...identity!,owner:owner!};
  const data:BusinessSpecData={schema_version:'alchlang.business-spec/v1-candidate',identity,requirements:[],entities:[],definitions:[],claims:[],rules:[],operations:[],capabilities:[],source_spans:spans,obligations,authority_effect:'none'};
  let fieldCount=0;const directRules:DirectBusinessRuleV2[]=[],entries:BusinessLogicalEntryV2[]=[];
  for(const block of blocks){
    const base=block.kind+':'+block.id,seen=new Map<string,Row>();
    const once=(key:string,row:Row)=>{if(seen.has(key))fail('BUSINESS_AMBIGUOUS',row,'duplicate '+key);seen.set(key,row);};
    const required=(keys:string[])=>{for(const key of keys)if(!seen.has(key))fail('BUSINESS_REQUIRED',block.row,'missing '+key+' in '+block.id);};
    const input=(row:Row):BusinessParameter=>{const m=match(row,'input '+param+' '+id);return {name:ident(m[1]!,row,true),type_ref:ident(m[2]!,row)};};
    const strings=(row:Row,key:string)=>quoted(match(row,key+' (.+)')[1]!,row);
    const ref=(row:Row,key:string)=>ident(match(row,key+' '+id)[1]!,row);
    const location=(row:Row,key:string,kind:BusinessObligation['kind']='clause')=>record(row,base+'/'+key,kind);
    if(block.kind==='requirement'){
      const out={id:block.id,context:'',meaning:'',applies_when:[] as string[],actors:[] as string[],boundaries:[] as string[],examples:[] as BusinessScenario[],counterexamples:[] as BusinessScenario[]};
      let current:{scenario:{-readonly [K in keyof BusinessScenario]:BusinessScenario[K]};row:Row;seen:Set<string>;key:string}|undefined;const caseIds=new Set<string>();
      const finish=()=>{if(current)for(const key of ['given','when','then','why'])if(!current.seen.has(key))fail('BUSINESS_REQUIRED',current.row,'missing scenario '+key);current=undefined;};
      for(const row of block.rows){
        if(row.depth===2){
          if(!current)fail('BUSINESS_SYNTAX',row,'scenario body without case');
          const m=match(row,'(given|when|then|why) (.+)'),key=m[1]! as 'given'|'when'|'then'|'why';
          if(current.seen.has(key))fail('BUSINESS_AMBIGUOUS',row,'duplicate scenario clause');current.seen.add(key);current.scenario[key]=quoted(m[2]!,row);location(row,current.key+'/'+key,'scenario');continue;
        }
        if(row.depth!==1)fail('BUSINESS_SYNTAX',row,'unexpected requirement indentation');finish();
        const caseMatch=row.text.match(new RegExp('^(example|counterexample) '+id+':$'));
        if(caseMatch){const key=ident(caseMatch[2]!,row),norm=businessSymbol(key);if(caseIds.has(norm))fail('BUSINESS_AMBIGUOUS',row,'duplicate or colliding case');caseIds.add(norm);const scenario={case_id:key,given:'',when:'',then:'',why:''};const target=caseMatch[1]==='example'?out.examples:out.counterexamples;target.push(scenario);if(target.length>256)fail('BUSINESS_SOURCE_BUDGET',row,'scenario budget exceeded');seen.set(caseMatch[1]!,row);current={scenario,row,seen:new Set(),key:caseMatch[1]+':'+key};location(row,current.key,'scenario');continue;}
        const key=row.text.split(' ')[0]!;
        if(key==='context'||key==='meaning'){once(key,row);out[key]=strings(row,key);}
        else if(key==='applies-when'||key==='actor'||key==='actors'||key==='does-not-mean'){
          const none=row.text==='applies-when none'||row.text==='actors none';const group=key==='actor'||key==='actors'?'actors':key;
          if(key==='actors'&&!none)fail('BUSINESS_SYNTAX',row,'actors only supports none');
          const list=group==='actors'?out.actors:key==='applies-when'?out.applies_when:out.boundaries;
          if(seen.get(group)?.text.endsWith(' none')||none&&seen.has(group))fail('BUSINESS_AMBIGUOUS',row,'none cannot be mixed with repeated clauses');
          seen.set(group,row);if(!none)list.push(strings(row,key));if(list.length>256)fail('BUSINESS_SOURCE_BUDGET',row,'repeated clause budget exceeded');
        }else fail('BUSINESS_SYNTAX',row,'unknown requirement clause');location(row,key);
      }finish();required(['context','meaning','applies-when','actors','does-not-mean','example','counterexample']);(data.requirements as BusinessRequirement[]).push(out);continue;
    }
    // Other blocks have no nested syntax; every source clause is recorded once.
    const body=block.rows;for(const row of body)if(row.depth!==1)fail('BUSINESS_SYNTAX',row,'unexpected declaration indentation');
    if(block.kind==='entity'){
      const out:BusinessEntity={id:block.id,meaning:'',fields:[],identity:''};const writable=out as {meaning:string;identity:string};const fields=new Set<string>();
      for(const row of body){const key=row.text.split(' ')[0]!;
        if((key==='meaning'||key==='identity')&&!row.text.match(new RegExp('^'+param+' (UInt64|String|Bool) meaning (.+)$'))){once(key,row);if(key==='meaning')writable.meaning=strings(row,key);else writable.identity=ident(match(row,'identity '+param)[1]!,row,true);location(row,key,key==='identity'?'reference':'clause');}
        else{const m=match(row,param+' (UInt64|String|Bool) meaning (.+)'),name=ident(m[1]!,row,true);if(fields.has(businessSymbol(name)))fail('BUSINESS_AMBIGUOUS',row,'duplicate field');fields.add(businessSymbol(name));if(++fieldCount>(v2?BUSINESS_AUTHORING_V2_LIMITS.fields:256))fail('BUSINESS_SOURCE_BUDGET',row,'field budget exceeded');if(v2&&m[2]==='String')fail('BUSINESS_UNSUPPORTED',row,'successor U0 fields are UInt64 and Bool only');(out.fields as {name:string;type:'UInt64'|'String'|'Bool';meaning:string}[]).push({name,type:m[2]! as 'UInt64'|'String'|'Bool',meaning:quoted(m[3]!,row)});seen.set('field',row);location(row,'field:'+name,'field');}}
      required(['meaning','identity','field']);(data.entities as BusinessEntity[]).push(out);continue;
    }
    // Drafts are constructed entirely from matched grammar, then checked for all required keys.
    const out:Record<string,any>={id:block.id};
    if(block.kind==='formal-claim')Object.assign(out,{version:block.version,sorts:[],predicates:[],constants:[],...(v2?{subject_refs:[]}: {})});
    if(block.kind==='rule'&&!v2)out.bindings=[];
    if(block.kind==='operation'){out.guards=[];out.effects=[];}
    const localNames=new Map<string,Set<string>>();
    const uniqueName=(group:string,name:string,row:Row)=>{const names=localNames.get(group)??new Set<string>();const norm=businessSymbol(name);if(names.has(norm))fail('BUSINESS_AMBIGUOUS',row,'duplicate or colliding '+group);names.add(norm);if(names.size>256)fail('BUSINESS_SOURCE_BUDGET',row,'formal declaration/binding budget exceeded');localNames.set(group,names);};
    const allowed:Record<string,string[]>={definition:['requirement','input','meaning','boolean-field'],'formal-claim':['requirement','supersedes','profile','sort','predicate','constant','proposition','ceiling'],rule:['meaning','input','claim','bind'],operation:['meaning','input','output','requires','returns','on-rejection','effects'],capability:['invokes','public-name','audience'],entry:['invokes','public-name','permission']};
    if(v2){allowed.rule=['requirement','meaning','input','condition'];allowed['formal-claim']!.push('subject');}
    for(const row of body){const key=row.text.split(' ')[0]!;
      if(!allowed[block.kind]!.includes(key))fail('BUSINESS_SYNTAX',row,'unknown '+block.kind+' clause');
      if(!['sort','predicate','constant','bind',...(v2?['subject']:[])].includes(key))once(key,row);else seen.set(key,row);
      let clauseSelector=key;
      switch(key){
        case 'meaning':case 'ceiling':out[key]=strings(row,key);break;
        case 'requirement':out.requirement_ref=ref(row,key);break;
        case 'claim':out.claim_ref=ref(row,key);break;
        case 'input':out.input=input(row);break;
        case 'condition':{const m=match(row,'condition '+param+'\\.'+param);out.condition={kind:'boolean-field',value:{root:ident(m[1]!,row,true),path:[ident(m[2]!,row,true)]}};break;}
        case 'subject':{const name=ref(row,key);uniqueName('subject',name,row);if(out.subject_refs.length>=16)fail('BUSINESS_SOURCE_BUDGET',row,'at most sixteen assurance subjects');out.subject_refs.push(name);clauseSelector='subject:'+name;break;}
        case 'boolean-field':{const m=match(row,'boolean-field '+param+'\\.'+param);out.boolean_field={root:ident(m[1]!,row,true),path:[ident(m[2]!,row,true)]};break;}
        case 'supersedes':if(row.text!=='supersedes none')fail('BUSINESS_UNSUPPORTED',row,'supersession needs a migration capability');out.supersedes=null;break;
        case 'profile':if(row.text!=='profile fol-core/1-candidate')fail('BUSINESS_UNSUPPORTED',row,'unsupported logic profile');out.logic_profile='fol-core/1-candidate';break;
        case 'sort':{const m=match(row,'sort '+id+' interpreted-as '+id),name=ident(m[1]!,row);uniqueName('sort',name,row);clauseSelector='sort:'+name;out.sorts.push({name,type_ref:ident(m[2]!,row)});break;}
        case 'predicate':{const m=match(row,'predicate '+id+'\\('+id+'\\) defined-by '+id),name=ident(m[1]!,row);uniqueName('predicate',name,row);clauseSelector='predicate:'+name;out.predicates.push({name,sort_refs:[ident(m[2]!,row)],definition_ref:ident(m[3]!,row)});break;}
        case 'constant':{const m=match(row,'constant '+param+': '+id),name=ident(m[1]!,row,true);uniqueName('constant',name,row);clauseSelector='constant:'+name;out.constants.push({name,sort_ref:ident(m[2]!,row)});break;}
        case 'proposition':out.proposition=match(row,'proposition (\\S.*)')[1]!;break;
        case 'bind':{const m=match(row,'bind '+param+' <- '+param);uniqueName('bind',m[1]!,row);clauseSelector='bind:'+m[1]!;out.bindings.push({constant_ref:ident(m[1]!,row,true),parameter_ref:ident(m[2]!,row,true)});break;}
        case 'output':out.output_ref=ref(row,key);break;
        case 'requires':{const m=match(row,'requires '+id+'\\('+param+': '+param+'\\)');out.guards.push({rule_ref:ident(m[1]!,row),arguments:[{parameter:ident(m[2]!,row,true),value:{root:ident(m[3]!,row,true),path:[]}}]});break;}
        case 'returns':out.result={root:ident(match(row,'returns '+param)[1]!,row,true),path:[]};break;
        case 'on-rejection':out.on_rejection=ref(row,key);break;
        case 'effects':if(row.text!=='effects none')fail('BUSINESS_UNSUPPORTED',row,'only empty effects are supported');break;
        case 'invokes':out.operation_ref=ref(row,key);break;
        case 'public-name':{const value=match(row,v2?'public-name ([a-z][a-z0-9-]{0,63})':'public-name ([A-Za-z][A-Za-z0-9_]{0,127})')[1]!;out.public_name=ident(value,row);break;}
        case 'permission':if(row.text!=='permission public')fail('BUSINESS_UNSUPPORTED',row,'only explicit public permission is supported in U0');out.permission={kind:'public'};break;
        case 'audience':if(row.text!=='audience public')fail('BUSINESS_UNSUPPORTED',row,'only public audience supported');out.audience='public';break;
      }
      location(row,clauseSelector,['requirement','input','claim','boolean-field','sort','predicate','constant','bind','output','requires','returns','invokes'].includes(key)?'reference':'clause');
    }
    required(allowed[block.kind]!);
    switch(block.kind){case 'definition':(data.definitions as BusinessDefinition[]).push(out as unknown as BusinessDefinition);break;case 'formal-claim':(data.claims as BusinessClaim[]).push(out as unknown as BusinessClaim);break;case 'rule':if(v2)directRules.push(out as unknown as DirectBusinessRuleV2);else (data.rules as BusinessRule[]).push(out as unknown as BusinessRule);break;case 'operation':(data.operations as BusinessOperation[]).push(out as unknown as BusinessOperation);break;case 'capability':(data.capabilities as BusinessCapability[]).push(out as unknown as BusinessCapability);break;case 'entry':entries.push(out as unknown as BusinessLogicalEntryV2);break;}
  }
  for(const key of (v2?['requirements','entities','operations']:['requirements','entities','definitions','claims','rules','operations','capabilities']) as readonly (keyof Pick<BusinessSpecData,'requirements'|'entities'|'definitions'|'claims'|'rules'|'operations'|'capabilities'>)[])if(!data[key].length)fail('BUSINESS_REQUIRED',undefined,'at least one '+key+' declaration required');
  if(data.operations.length>16||data.capabilities.length>16||data.operations.length+data.capabilities.length>32)fail('BUSINESS_SOURCE_BUDGET',undefined,'operation/exposure entry budget exceeded');
  spans.sort((a,b)=>a.line-b.line);
  const sourceOrder=new Map(spans.map((s,i)=>[s.selector,i]));obligations.sort((a,b)=>sourceOrder.get(a.span_selector)!-sourceOrder.get(b.span_selector)!);
  if(v2){
    for(const [name,values,maximum] of [['requirements',data.requirements,16],['entities',data.entities,1],['rules',directRules,1],['operations',data.operations,1],['entries',entries,1],['definitions',data.definitions,256],['claims',data.claims,256]] as const){
      if(values.length>maximum||(['rules','entries'].includes(name)&&values.length!==1))fail('BUSINESS_SOURCE_BUDGET',undefined,'unsupported successor '+name+' count');
    }
    if(data.entities[0]!.fields.length!==2)fail('BUSINESS_REQUIRED',undefined,'successor Entity needs exactly two declared fields');
    const {capabilities:_capabilities,rules:_rules,schema_version:_version,...common}=data;
    const successor:BusinessSpecDataV2={...common,schema_version:BUSINESS_SPEC_V2,rules:directRules,entries,claims:data.claims as readonly BusinessClaimV2[]};
    const result=freezeBusinessData<ParsedBusinessSourceV2>({kind:'parsed-business-source-v2',data:successor,source:{path:source,text,sha256,bytes}},source);
    parsedRegistry.set(result,businessHash(businessCanonical(result)));return result;
  }
  const result=freezeBusinessData<ParsedBusinessSource>({kind:'parsed-business-source',data,source:{path:source,text,sha256,bytes}},source);
  parsedRegistry.set(result,businessHash(businessCanonical(result)));return result;
}
/** Source owner only. Loaded profile, Core semantic/input and native owners are later. */
export const BUSINESS_PARSER_OWNER_V2:BusinessParserOwnerV2=Object.freeze({parse:parseBusinessSourceV2,assertCurrent:assertParsedBusinessSourceV2Current});
