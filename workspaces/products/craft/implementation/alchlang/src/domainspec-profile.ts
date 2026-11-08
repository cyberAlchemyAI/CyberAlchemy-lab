import { createHash } from "node:crypto";
import { CompilationRejected, type NormalizedDomain, type NormalizedFact, type SfolUInt64Term, type SfolFormula } from "./model.js";
export const DOMAINSPEC_PROFILE = "domainspec-1.0.0";
export const EXACT_PROFILE = "domainspec-1.0.0-exact-uint64-v1";
export const EXACT_REALIZATION = "domainspec.typescript-exact-uint64/v1";
export interface DeclarationBinding { ontology: string; meaning: string; identity?: string; invariants?: string[]; properties?: Record<string, { ontology: string; meaning: string }> }
export interface DomainSpecBindings { schema_version: "alchlang.domainspec-bindings/v1"; profile: string; source_sha256: string; owner: string; declarations: Record<string, DeclarationBinding> }
export const digest = (bytes: string | Buffer): string => createHash("sha256").update(bytes).digest("hex");
export const json = (value: unknown): string => JSON.stringify(value, null, 2) + "\n";
export function reject(code: string, where: string, message: string): never { throw new CompilationRejected([{code, path:where, message}]); }
export function symbol(id: string, separator = "-"): string {
  const s = id.replace(/([a-z0-9])([A-Z])/g, "$1-$2").replace(/[^A-Za-z0-9]+/g, "-").toLowerCase();
  if (!/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(s) || ["constructor", "prototype", "__proto__"].includes(id)) reject("DS_IDENTIFIER",id,"unsupported identifier");
  return s.replaceAll("-",separator);
}
export function fields(model: NormalizedDomain, id: string): NormalizedFact[] { return model.value_objects.find(v=>v.id===id)?.fields ?? model.facts.filter(f=>f.subject_ref===id); }
export const scalar = (type: string, exact = false): "String" | "Bool" | "UInt64" => { if(exact && type === "integer") return "UInt64"; if (["string","identifier"].includes(type)) return "String"; if(type==="boolean")return "Bool"; return reject("DS_UNSUPPORTED_TYPE",type,"first profile supports String/Bool records"); };
export function references(e: SfolFormula): string[] { return "node" in e ? e.node==="fact_ref"?[e.ref]:[] : e.operands.flatMap(references); }
export function predicate(e: SfolFormula, facts: Map<string, NormalizedFact>, rule = false, exact = false, rowFields = new Set<string>()): any {
  const value = (v: SfolFormula): any => {
    if (!("node" in v)) return reject("DS_PREDICATE", "$", "nested Boolean value not supported");
    if(v.node==="literal") {const type=scalar(v.value_type, exact); if(type==="UInt64" ? !Number.isSafeInteger(v.value) || Number(v.value)<0 : typeof v.value !== (type==="Bool"?"boolean":"string"))reject("DS_LITERAL","$","literal type mismatch"); return rule?{op:"literal",type,value:v.value}:{kind:"literal",type,value:v.value};}
    if(v.node==="fact_ref" && facts.has(v.ref)) {scalar(facts.get(v.ref)!.type, exact);return rule?{op:"path",root:symbol(v.ref,"_"),properties:[]}:{kind:rowFields.has(v.ref)?"field":"parameter",name:symbol(v.ref,"_")};}
    return reject("DS_PREDICATE", "$", "only declared scalar facts and literals are supported");
  };
  if("node" in e) return {op:"eq",left:value(e),right:rule?{op:"literal",type:"Bool",value:true}:{kind:"literal",type:"Bool",value:true}};
  if(e.operator==="not")return {op:"not",term:predicate(e.operands[0],facts,rule,exact,rowFields)};
  if(["and","or"].includes(e.operator))return {op:e.operator==="and"?"all":"any",terms:e.operands.map(o=>predicate(o,facts,rule,exact,rowFields))};
  if(["eq","neq"].includes(e.operator)){const p={op:"eq",left:value(e.operands[0]),right:value(e.operands[1])};return e.operator==="neq"?{op:"not",term:p}:p;}
  if(exact && !rule && ["lt","lte","gt","gte"].includes(e.operator))return {op:e.operator,left:value(e.operands[0]),right:value(e.operands[1])};
  return reject("DS_PREDICATE",e.operator,"only equality and Boolean composition are supported");
}
export function validateProfile(model: NormalizedDomain, raw: unknown, source: string): DomainSpecBindings {
  const b=raw as DomainSpecBindings;
  if(!b || b.schema_version!=="alchlang.domainspec-bindings/v1" || ![DOMAINSPEC_PROFILE,EXACT_PROFILE].includes(b.profile) || !b.declarations || typeof b.declarations!=="object" || Array.isArray(b.declarations))reject("DS_BINDINGS","$","explicit v1 bindings and profile required");
  const exact=b.profile===EXACT_PROFILE;
  const typeScalar=(type:string)=>scalar(type,exact);
  if(b.source_sha256!==digest(source))reject("DS_SOURCE_DRIFT","source_sha256","bindings do not match source bytes");
  if(!model.owners.includes(b.owner))reject("DS_OWNER","owner","bindings must name a declared source owner");
  for(const key of Object.keys(b))if(!["schema_version","profile","source_sha256","owner","declarations"].includes(key))reject("DS_BINDINGS",key,"unknown binding member");
  if(model.logic_profile!=="sfol-v1" || model.residue.length)reject("DS_UNSUPPORTED","$","closed SFOL model required");
  for(const key of ["enums","events","states","transitions","effects","actions","permissions","queries","workflows","interfaces","examples","authority_boundaries"] as const)if(model[key].length && !(exact && key==="queries"))reject("DS_UNSUPPORTED",key,"construct is outside first target profile");
  for(const term of model.terms)if(!["entity","value-object"].includes(term.kind))reject("DS_UNSUPPORTED",term.id,"term kind outside first profile");
  const ids=[...model.queries.map(q=>q.id),...model.terms.map(t=>t.id),...model.rules.map(t=>t.id),...model.calculations.map(t=>t.id),...model.mappings.map(t=>t.id),...model.policies.map(t=>t.id)];
  if(new Set(ids.map(i=>symbol(i))).size!==ids.length)reject("DS_SYMBOL_COLLISION","$","node names collide after normalization");
  if(Object.keys(b.declarations).sort().join("\0")!==[...ids].sort().join("\0"))reject("DS_BINDINGS","declarations","bindings must exactly cover every declaration");
  const ontology=new Set<string>();
  for(const id of ids){const d=b.declarations[id];if(!d || typeof d.meaning!=="string" || !d.meaning.trim() || !/^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$/.test(d.ontology) || ontology.has(d.ontology))reject("DS_ONTOLOGY",id,"unique explicit ontology selector and meaning required");ontology.add(d.ontology);
    for(const k of Object.keys(d))if(!["ontology","meaning","identity","invariants","properties"].includes(k))reject("DS_BINDINGS",id,"unknown declaration binding member");
    const fs=fields(model,id);
    if(model.terms.some(t=>t.id===id)){
      if(!fs.length || !d.properties || Object.keys(d.properties).sort().join("\0")!==fs.map(f=>f.id).sort().join("\0"))reject("DS_FIELDS",id,"explicit property bindings must cover the record");
      if(new Set(fs.map(f=>symbol(f.id,"_"))).size!==fs.length)reject("DS_SYMBOL_COLLISION",id,"field names collide");
      for(const f of fs){typeScalar(f.type);const p=d.properties[f.id];if(p.ontology!==`${d.ontology}#${f.id}` || typeof p.meaning!=="string" || !p.meaning.trim())reject("DS_ONTOLOGY",`${id}.${f.id}`,"property selector and meaning must be explicitly bound");}
      if(model.terms.find(t=>t.id===id)!.kind==="entity") {const identity=fs.find(f=>f.id===d.identity);if(!identity || !identity.required || typeScalar(identity.type)!=="String")reject("DS_IDENTITY",id,"explicit required String identity needed");if(d.invariants?.length)reject("DS_UNSUPPORTED",id,"Entity invariants outside first profile");}
      else {if(d.identity || !d.invariants?.length || d.invariants.some(i=>!model.rules.some(r=>r.id===i)))reject("DS_INVARIANT",id,"Value Object needs real Rule references and no identity");const vo=model.value_objects.find(v=>v.id===id)!;if(vo.equality_fields.length!==fs.length || fs.some(f=>!f.required))reject("DS_VALUE_OBJECT",id,"all required fields must participate in equality");}
    }else if(d.properties || d.identity || d.invariants)reject("DS_BINDINGS",id,"record binding on non-record declaration");
  }
  const facts=new Map(model.facts.map(f=>[f.id,f]));
  for(const rule of model.rules){if("legacy_predicate" in rule.condition)reject("DS_UNSUPPORTED",rule.id,"opaque rule");predicate(rule.condition as SfolFormula,facts,true);}
  for(const c of model.calculations)if(!exact && (c.input_facts.length || !("node" in c.expression) || c.expression.node!=="uint64_literal" || BigInt(c.expression.value)>BigInt(Number.MAX_SAFE_INTEGER)))reject("DS_NUMERIC_PROFILE",c.id,"only input-free exactly representable UInt64 constants supported");
  for(const m of model.mappings){const sf=new Map(fields(model,m.source_ref).map(f=>[f.id,f]));const tf=new Map(fields(model,m.target_ref).map(f=>[f.id,f]));if(m.total && m.clauses.length!==tf.size)reject("DS_MAPPING_TOTALITY",m.id,"total mapping must explicitly cover all target fields");for(const c of m.clauses){const t=tf.get(c.target_field);const s=c.source_field===null?null:sf.get(c.source_field);if(!t || c.source_field!==null&&!s)reject("DS_MAPPING_REFERENCE",m.id,"field must belong to the declared endpoint");if(s && typeScalar(s.type)!==typeScalar(t.type))reject("DS_MAPPING_TYPE",m.id,"field type mismatch");if(c.default_value && (typeScalar(t.type)==="UInt64" ? !Number.isSafeInteger(c.default_value.value) || Number(c.default_value.value)<0 : typeof c.default_value.value!==(typeScalar(t.type)==="Bool"?"boolean":"string")))reject("DS_MAPPING_TYPE",m.id,"default type mismatch");}}
  for(const p of model.policies){for(const id of [...p.cases.map(c=>c.target_ref),p.default_target_ref])if(!model.calculations.some(c=>c.id===id))reject("DS_POLICY_TARGET",p.id,"first profile selects constant Calculations only");for(const c of p.cases){predicate(c.predicate,facts,false,exact);if(references(c.predicate).some(id=>!p.input_facts.includes(id)))reject("DS_POLICY_INPUT",p.id,"predicate uses undeclared input");}p.input_facts.forEach(id=>typeScalar(facts.get(id)!.type));}
  if(exact) {
    for(const c of model.calculations) { c.input_facts.forEach(id=>{if(facts.get(id)?.type!=="integer")reject("DS_NUMERIC_PROFILE",c.id,"integer calculation inputs required");}); numericExpression(c.expression); }
    for(const q of model.queries) {
      const rowFields=new Set(fields(model,q.source_ref).map(f=>f.id));
      if(q.order_by.length>1)reject("DS_QUERY_ORDER",q.id,"first exact profile supports one sort key");
      if(q.input_facts.some(id=>rowFields.has(id)))reject("DS_QUERY_INPUT",q.id,"overlapping row and parameter names need an explicit precedence contract");
      const allowed=new Set([...rowFields,...q.input_facts]);
      if(q.predicate && references(q.predicate).some(id=>!allowed.has(id)))reject("DS_QUERY_INPUT",q.id,"predicate uses an undeclared query input");
      if(q.projection.some(id=>!rowFields.has(id)) || q.order_by.some(o=>!rowFields.has(o.field_ref)))reject("DS_QUERY_FIELD",q.id,"query fields must belong to its source");
      q.input_facts.forEach(id=>typeScalar(facts.get(id)!.type));
      if(q.predicate)predicate(q.predicate,facts,false,true,rowFields);
    }
  }
  const expectedEdges=new Set([...model.queries.map(q=>`${q.id}|queries|${q.source_ref}`),...model.mappings.map(m=>`${m.id}|maps|${m.target_ref}`),...model.policies.flatMap(p=>[...new Set([...p.cases.map(c=>c.target_ref),p.default_target_ref])].map(t=>`${p.id}|applies|${t}`))]);
  for(const edge of model.edges)if(!expectedEdges.has(`${edge.source}|${edge.type}|${edge.target}`))reject("DS_UNSUPPORTED_EDGE",edge.id,"edge outside lowered relationship profile");
  return b;
}

export function numericExpression(e: SfolUInt64Term): any {
  if ("node" in e) {
    if(e.node==="input_ref")return {op:"input",name:symbol(e.ref,"_")};
    const n=BigInt(e.value);
    if(n<0n || n>18446744073709551615n)reject("DS_NUMERIC_PROFILE","literal","UInt64 out of range");
    if(n<=BigInt(Number.MAX_SAFE_INTEGER))return {op:"literal",value:Number(n)};
    // Exact base-2^32 decomposition: every JSON literal is a safe integer.
    return {op:"add",left:{op:"multiply",left:{op:"literal",value:Number(n>>32n)},right:{op:"literal",value:4294967296}},right:{op:"literal",value:Number(n&4294967295n)}};
  }
  return {op:e.operator,left:numericExpression(e.operands[0]),right:numericExpression(e.operands[1])};
}
