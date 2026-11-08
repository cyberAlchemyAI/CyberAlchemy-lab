import { CompilationRejected } from "./model.js";
import { normalizeApplicationDeclarations, type ApplicationDeclaration } from "./application-source.js";
import { applicationIntegrationKinds, normalizeApplicationIntegrations, type ApplicationIntegration } from "./application-integration.js";
import { normalizeApplicationRuntimeProfiles, type ApplicationRuntimeProfile } from "./application-runtime-profile.js";
import { normalizeApplicationRealizations, type ApplicationRealization } from "./application-realization.js";
import { normalizeApplicationVerificationProfiles, type ApplicationVerificationProfile } from "./application-verification-profile.js";

export interface FormalSignature {
  sorts: Array<{ name: string }>;
  functions: Array<{ name: string; parameter_sorts: string[]; result_sort: string }>;
  predicates: Array<{ name: string; parameter_sorts: string[] }>;
  constants: Array<{ name: string; sort: string }>;
}
export type FormalTerm =
  | { kind: "variable" | "constant"; name: string; sort: string }
  | { kind: "function"; name: string; arguments: FormalTerm[]; sort: string };
export type FormalProposition =
  | { kind: "predicate"; name: string; arguments: FormalTerm[] }
  | { kind: "equal"; left: FormalTerm; right: FormalTerm }
  | { kind: "not"; operand: FormalProposition }
  | { kind: "and" | "or" | "implies" | "iff"; left: FormalProposition; right: FormalProposition }
  | { kind: "forall" | "exists"; variable: string; sort: string; body: FormalProposition };
export interface FormalClaimDeclaration {
  id: string;
  profile: "fol-core/1-candidate";
  signature: FormalSignature;
  proposition_source: string;
  proposition: FormalProposition;
  ceiling: string;
  source_line: number;
}

export interface ApplicationSourceSection {
  kind: string;
  id: string;
  line: number;
  rows: Array<{ line: number; text: string; indent?: number }>;
}
export interface ApplicationFormalSource {
  schema_version: "alchlang.application-source/v1-candidate";
  profile: "application-v1";
  domain_id: string;
  title: string;
  owner: string;
  formal_claims: FormalClaimDeclaration[];
  rules: Array<{ id: string; claim_ref: string; ontology: string | null; meaning: string | null; enforces: string[]; source_line: number }>;
  invariants: Array<{ id: string; claim_ref: string | null; rule_ref: string | null; source_line: number }>;
  declarations: ApplicationDeclaration[];
  integrations: ApplicationIntegration[];
  runtime_profiles?: ApplicationRuntimeProfile[];
  realizations?: ApplicationRealization[];
  verification_profiles?: ApplicationVerificationProfile[];
  authority_effect: "none";
}

/** Consumes sections from the existing Alch scanner; never scans another application grammar. */
export function normalizeApplicationFormalSource(domain: { id: string; title: string; owner: string }, sections: ApplicationSourceSection[]): ApplicationFormalSource {
  const fail = (code: string, line: number, message: string): never => { throw new CompilationRejected([{ code, path: `$line:${line}`, message }]); };
  const ids = new Set<string>();
  for (const section of sections.filter(item => item.kind !== "rule-enforcement")) {
    if (ids.has(section.id)) fail("DUPLICATE_IDENTIFIER", section.line, `duplicate declaration ${section.id}`);
    ids.add(section.id);
  }
  const formalClaims = sections.filter(s => s.kind === "formal-claim").map(section => {
    const signature: FormalSignature = { sorts: [], functions: [], predicates: [], constants: [] };
    let profile: string | undefined; let proposition: string | undefined; let propositionLine = section.line; let ceiling: string | undefined;
    for (let i = 0; i < section.rows.length; i++) {
      const row = section.rows[i]!;
      let match: RegExpExecArray | null;
      if ((match = /^profile\s+(.+)$/.exec(row.text))) {
        if (profile !== undefined) fail("CLAIM_PROFILE_COUNT", row.line, "claim requires exactly one profile");
        profile = match[1];
      } else if ((match = /^sort\s+([A-Za-z_][\w.-]*)$/.exec(row.text))) signature.sorts.push({ name: match[1]! });
      else if ((match = /^predicate\s+([A-Za-z_][\w.-]*)\(([^()]*)\)$/.exec(row.text))) {
        signature.predicates.push({ name: match[1]!, parameter_sorts: match[2]!.trim() ? match[2]!.split(",").map(s => s.trim()) : [] });
      } else if ((match = /^function\s+([A-Za-z_][\w.-]*)\(([^()]*)\)\s*->\s*([A-Za-z_][\w.-]*)$/.exec(row.text))) {
        signature.functions.push({ name: match[1]!, parameter_sorts: match[2]!.trim() ? match[2]!.split(",").map(s => s.trim()) : [], result_sort: match[3]! });
      } else if ((match = /^constant\s+([A-Za-z_][\w.-]*):\s*([A-Za-z_][\w.-]*)$/.exec(row.text))) signature.constants.push({ name: match[1]!, sort: match[2]! });
      else if ((match = /^proposition\s+(.+)$/.exec(row.text))) {
        if (proposition !== undefined) fail("CLAIM_PROPOSITION_COUNT", row.line, "claim requires exactly one proposition");
        proposition = match[1]!; propositionLine = row.line;
        while (section.rows[i + 1] && (section.rows[i + 1]!.indent ?? 0) > (row.indent ?? 0)) proposition += "\n" + section.rows[++i]!.text;
      } else if ((match = /^ceiling\s+("(?:[^"\\]|\\.)*")$/.exec(row.text))) {
        if (ceiling !== undefined) fail("CLAIM_CEILING_COUNT", row.line, "claim requires exactly one ceiling");
        try { ceiling = JSON.parse(match[1]!); } catch { fail("CLAIM_SYNTAX", row.line, "invalid quoted ceiling"); }
      } else fail("CLAIM_SYNTAX", row.line, `unsupported FormalClaim clause ${row.text}`);
    }
    if (profile !== "fol-core/1-candidate") fail("CLAIM_PROFILE", section.line, "this authoring component requires explicit fol-core/1-candidate");
    if (!proposition) fail("CLAIM_PROPOSITION_COUNT", section.line, "claim requires exactly one proposition");
    if (!ceiling?.trim()) fail("CLAIM_CEILING_COUNT", section.line, "claim requires a nonempty ceiling");
    return { id: section.id, profile: "fol-core/1-candidate" as const, signature,
      proposition_source: proposition!, proposition: parseFormalProposition(proposition!, signature, `$line:${propositionLine}`),
      ceiling: ceiling!, source_line: section.line };
  });
  const claimIds = new Set(formalClaims.map(claim => claim.id));
  const enforcementSections = sections.filter(s => s.kind === "rule-enforcement");
  const rules = sections.filter(s => s.kind === "rule").map(section => {
    let claim: string | undefined; let ontology: string | null = null; let meaning: string | null = null; const enforces: string[] = [];
    for (const row of section.rows) {
      let match: RegExpExecArray | null;
      if ((match = /^claim\s+([A-Za-z_][\w.-]*)$/.exec(row.text))) {
        if (claim !== undefined) fail("RULE_CONDITION_COUNT", row.line, "Rule requires exactly one claim");
        claim = match[1];
      } else if ((match = /^(ontology|meaning)\s+("(?:[^"\\]|\\.)*")$/.exec(row.text))) {
        let value: string; try { value = JSON.parse(match[2]!); } catch { return fail("RULE_SYNTAX", row.line, "invalid quoted metadata"); }
        if (match[1] === "ontology") { if (ontology !== null) fail("RULE_SYNTAX", row.line, "duplicate ontology"); ontology = value; }
        else { if (meaning !== null) fail("RULE_SYNTAX", row.line, "duplicate meaning"); meaning = value; }
      } else if ((match = /^enforces\s+([A-Za-z_][\w.-]*)$/.exec(row.text))) {
        if (enforces.includes(match[1]!)) fail("RULE_SYNTAX", row.line, "duplicate enforcement target");
        enforces.push(match[1]!);
      } else fail("RULE_SECOND_CONDITION", row.line, "Rule conditions must reference one declared FormalClaim");
    }
    if (!claim || !claimIds.has(claim)) fail("CLAIM_UNRESOLVED", section.line, `claim ${claim ?? "<missing>"} is not declared`);
    for (const relation of enforcementSections.filter(item => item.id === section.id)) {
      const target = relation.rows[0]?.text;
      if (!target || enforces.includes(target)) fail("RULE_SYNTAX", relation.line, "duplicate or malformed enforcement target");
      enforces.push(target);
    }
    for (const target of enforces) if (!sections.some(s => s.kind === "operation" && s.id === target)) fail("UNRESOLVED_REFERENCE", section.line, `Operation ${target} is not declared`);
    return { id: section.id, claim_ref: claim!, ontology, meaning, enforces, source_line: section.line };
  });
  for (const relation of enforcementSections) if (!rules.some(rule => rule.id === relation.id)) fail("UNRESOLVED_REFERENCE", relation.line, `Rule ${relation.id} is not declared`);
  const ruleIds = new Set(rules.map(r => r.id));
  const invariants = sections.filter(s => s.kind === "invariant").map(section => {
    let claimRef: string | null = null; let ruleRef: string | null = null;
    for (const row of section.rows) {
      let match: RegExpExecArray | null;
      if ((match = /^claim\s+([A-Za-z_][\w.-]*)$/.exec(row.text))) {
        if (claimRef !== null || ruleRef !== null) fail("INVARIANT_CONDITION_COUNT", row.line, "Invariant requires exactly one claim or Rule");
        claimRef = match[1]!;
      } else if ((match = /^rule\s+([A-Za-z_][\w.-]*)$/.exec(row.text))) {
        if (claimRef !== null || ruleRef !== null) fail("INVARIANT_CONDITION_COUNT", row.line, "Invariant requires exactly one claim or Rule");
        ruleRef = match[1]!;
      } else fail("INVARIANT_CONDITION_COUNT", row.line, "Invariant conditions must reference one declared claim or Rule");
    }
    if ((claimRef === null) === (ruleRef === null)) fail("INVARIANT_CONDITION_COUNT", section.line, "Invariant requires exactly one claim or Rule");
    if (claimRef !== null && !claimIds.has(claimRef)) fail("CLAIM_UNRESOLVED", section.line, `claim ${claimRef} is not declared`);
    if (ruleRef !== null && !ruleIds.has(ruleRef)) fail("UNRESOLVED_REFERENCE", section.line, `Rule ${ruleRef} is not declared`);
    return { id: section.id, claim_ref: claimRef, rule_ref: ruleRef, source_line: section.line };
  });
  const integrations = normalizeApplicationIntegrations(sections.filter(s => applicationIntegrationKinds.has(s.kind)));
  const externalWriteMembers = new Set(integrations.filter(item => item.kind === "outbound-write").flatMap(item => [
    `${item.interface.ref}#${item.write.ref}`, `${item.interface.ref}#${item.inspect.ref}`]));
  const declarations = normalizeApplicationDeclarations(sections.filter(s => !["formal-claim", "rule", "invariant", "rule-enforcement", "runtime-profile", "realization", "verification-profile"].includes(s.kind) && !applicationIntegrationKinds.has(s.kind)), ruleIds, externalWriteMembers);
  return { schema_version: "alchlang.application-source/v1-candidate", profile: "application-v1",
    domain_id: domain.id, title: domain.title, owner: domain.owner, formal_claims: formalClaims, rules, invariants,
    declarations,
    ...(sections.some(s => s.kind === "realization") ? { realizations: normalizeApplicationRealizations(sections.filter(s => s.kind === "realization"), declarations, new Set(rules.map(r => r.id))) } : {}),
    ...(sections.some(s => s.kind === "runtime-profile") ? { runtime_profiles: normalizeApplicationRuntimeProfiles(sections.filter(s => s.kind === "runtime-profile")) } : {}),
    ...(sections.some(s => s.kind === "verification-profile") ? { verification_profiles: normalizeApplicationVerificationProfiles(sections.filter(s => s.kind === "verification-profile"), claimIds) } : {}),
    integrations, authority_effect: "none" };
}

const reserved = new Set(["forall", "exists", "not", "and", "or", "implies", "iff"]);
const identifier = /^[A-Za-z_][A-Za-z0-9_.-]*$/;

/** Fixed fol-core proposition budgets. Parentheses are syntax, not AST nodes.
 * Open Questions: docs/FORMAL-CLAIMS.md. */
export const FORMAL_PROPOSITION_LIMITS_VERSION = "fol-core-proposition-limits/v1";
export const FORMAL_PROPOSITION_LIMITS = Object.freeze({source_bytes:262144,tokens:65536,ast_nodes:16384,ast_depth:128});

/** Typed authoring representation for fol-core. This function performs no evaluation. */
export function parseFormalProposition(source: string, signature: FormalSignature, path = "$proposition"): FormalProposition {
  const tokens: Array<{ text: string; offset: number }> = [];
  const fail = (code: string, message: string, offset = tokens[cursor]?.offset ?? source.length): never => {
    throw new CompilationRejected([{ code, path: `${path}@${offset}`, message }]);
  };
  let cursor = 0;
  const limit = (kind: keyof typeof FORMAL_PROPOSITION_LIMITS, offset?: number): never =>
    fail("CLAIM_RESOURCE_LIMIT", `kind=${kind} limit=${FORMAL_PROPOSITION_LIMITS[kind]}`, offset);
  if (Buffer.byteLength(source, "utf8") > FORMAL_PROPOSITION_LIMITS.source_bytes) limit("source_bytes", 0);
  const sorts = new Set<string>();
  const names = new Set<string>();
  const declare = (name: string) => {
    if (!identifier.test(name) || reserved.has(name)) fail("FOL_SIGNATURE", `invalid signature name ${name}`, 0);
    if (names.has(name)) fail("FOL_DUPLICATE_SYMBOL", `duplicate signature name ${name}`, 0);
    names.add(name);
  };
  for (const sort of signature.sorts) { declare(sort.name); sorts.add(sort.name); }
  if (!sorts.size) fail("FOL_SIGNATURE", "at least one sort is required", 0);
  const sortExists = (sort: string) => { if (!sorts.has(sort)) fail("FOL_UNKNOWN_SORT", `undeclared sort ${sort}`); };
  for (const callable of [...signature.functions, ...signature.predicates]) {
    declare(callable.name); callable.parameter_sorts.forEach(sortExists);
  }
  for (const fn of signature.functions) sortExists(fn.result_sort);
  for (const constant of signature.constants) { declare(constant.name); sortExists(constant.sort); }
  const functions = new Map(signature.functions.map(fn => [fn.name, fn]));
  const predicates = new Map(signature.predicates.map(p => [p.name, p]));
  const constants = new Map(signature.constants.map(c => [c.name, c]));
  const used = new Set<string>();
  for (let offset = 0; offset < source.length;) {
    if (/\s/.test(source[offset]!)) { offset++; continue; }
    const match = /^(?:[A-Za-z_][A-Za-z0-9_.-]*|[():,=])/.exec(source.slice(offset));
    if (!match) fail("FOL_SYNTAX", "unexpected proposition character", offset);
    if(tokens.length >= FORMAL_PROPOSITION_LIMITS.tokens) limit("tokens", offset);
    tokens.push({ text: match![0], offset }); offset += match![0].length;
  }
  const peek = () => tokens[cursor]?.text;
  const take = (expected?: string): string => {
    const value = peek();
    if (!value || (expected && value !== expected)) fail("FOL_SYNTAX", `expected ${expected ?? "token"}`);
    cursor++; return value!;
  };
  const variableName = (): string => {
    const name = take();
    if (!identifier.test(name) || reserved.has(name)) fail("FOL_SYNTAX", "expected identifier");
    return name;
  };
  // Trampolined continuations keep every grammar transition, including grouping
  // and term arguments, off the JavaScript call stack. Scope links avoid copying
  // a growing Map for every quantified binder in hostile input.
  type Scope = {name:string;sort:string;parent:Scope|null}|null;
  const lookup=(scope:Scope,name:string):string|undefined=>{for(let row=scope;row;row=row.parent)if(row.name===name)return row.sort;return undefined;};
  type Done<T>=(value:T)=>void;
  const work:Array<()=>void>=[];
  const emit=<T>(done:Done<T>,value:T)=>{work.push(()=>done(value));};
  const depths=new WeakMap<object,number>();let nodes=0;
  const node=<T extends FormalTerm|FormalProposition>(make:()=>T,children:readonly (FormalTerm|FormalProposition)[]):T=>{
    if(nodes>=FORMAL_PROPOSITION_LIMITS.ast_nodes)limit("ast_nodes");
    let depth=1;for(const child of children)depth=Math.max(depth,1+depths.get(child)!);
    if(depth>FORMAL_PROPOSITION_LIMITS.ast_depth)limit("ast_depth");
    nodes++;const value=make();depths.set(value,depth);return value;
  };
  const argumentsFor=(expected:string[],scope:Scope,done:Done<FormalTerm[]>)=>{
    take("(");const args:FormalTerm[]=[];
    const finish=()=>{take(")");if(args.length!==expected.length)fail("FOL_ARITY",`expected ${expected.length} arguments, got ${args.length}`);
      args.forEach((arg,index)=>{if(arg.sort!==expected[index])fail("FOL_SORT_MISMATCH",`expected ${expected[index]}, got ${arg.sort}`);});emit(done,args);};
    const next=()=>{work.push(()=>term(scope,arg=>{args.push(arg);if(peek()===","){take(",");next();}else finish();}));};
    if(peek()===")")finish();else next();
  };
  const term=(scope:Scope,done:Done<FormalTerm>):void=>{
    const name=variableName(),variableSort=lookup(scope,name);
    if(variableSort){emit(done,node(()=>({kind:"variable",name,sort:variableSort}),[]));return;}
    const constant=constants.get(name);
    if(constant){used.add(name);emit(done,node(()=>({kind:"constant",name,sort:constant.sort}),[]));return;}
    const fn=functions.get(name);
    if(fn){used.add(name);work.push(()=>argumentsFor(fn.parameter_sorts,scope,args=>emit(done,node(()=>({kind:"function",name,sort:fn.result_sort,arguments:args}),args))));return;}
    fail(peek()==="("?"FOL_UNKNOWN_SYMBOL":"FOL_UNBOUND_VARIABLE",`undeclared term ${name}`);
  };
  const unary=(scope:Scope,done:Done<FormalProposition>):void=>{
    const next=peek();
    if(next==="not"){take();work.push(()=>unary(scope,operand=>emit(done,node(()=>({kind:"not",operand}),[operand]))));return;}
    if(next==="forall"||next==="exists"){
      take();const name=variableName();take(":");const sort=variableName();sortExists(sort);take(":");
      if(names.has(name))fail("FOL_SIGNATURE",`bound variable ${name} collides with a signature symbol`);
      const nested:Scope={name,sort,parent:scope};work.push(()=>iff(nested,body=>emit(done,node(()=>({kind:next,variable:name,sort,body}),[body]))));return;
    }
    if(next==="("){take();work.push(()=>iff(scope,expression=>{take(")");emit(done,expression);}));return;}
    const predicate=next&&predicates.get(next);
    if(predicate){take();used.add(predicate.name);work.push(()=>argumentsFor(predicate.parameter_sorts,scope,args=>emit(done,node(()=>({kind:"predicate",name:predicate.name,arguments:args}),args))));return;}
    if(next&&!functions.has(next)&&!constants.has(next)&&!lookup(scope,next))fail("FOL_UNKNOWN_SYMBOL",`undeclared predicate or term ${next}`);
    work.push(()=>term(scope,left=>{take("=");work.push(()=>term(scope,right=>{
      if(left.sort!==right.sort)fail("FOL_SORT_MISMATCH","equality requires matching sorts");emit(done,node(()=>({kind:"equal",left,right}),[left,right]));
    }));}));
  };
  const chain=(scope:Scope,done:Done<FormalProposition>,operator:"and"|"or",lower:(scope:Scope,done:Done<FormalProposition>)=>void)=>{
    const more=(left:FormalProposition)=>{if(peek()!==operator){emit(done,left);return;}take();work.push(()=>lower(scope,right=>more(node(()=>({kind:operator,left,right}),[left,right]))));};
    work.push(()=>lower(scope,more));
  };
  const and=(scope:Scope,done:Done<FormalProposition>)=>chain(scope,done,"and",unary);
  const or=(scope:Scope,done:Done<FormalProposition>)=>chain(scope,done,"or",and);
  const implication=(scope:Scope,done:Done<FormalProposition>)=>{
    work.push(()=>or(scope,left=>{if(peek()!=="implies"){emit(done,left);return;}take();work.push(()=>implication(scope,right=>emit(done,node(()=>({kind:"implies",left,right}),[left,right]))));}));
  };
  const iff=(scope:Scope,done:Done<FormalProposition>)=>{
    work.push(()=>implication(scope,left=>{if(peek()!=="iff"){emit(done,left);return;}take();work.push(()=>implication(scope,right=>{
      const result=node<FormalProposition>(()=>({kind:"iff",left,right}),[left,right]);if(peek()==="iff")fail("FOL_SYNTAX","parenthesize chained iff expressions");emit(done,result);
    }));}));
  };
  let proposition:FormalProposition|undefined;
  work.push(()=>iff(null,value=>{proposition=value;}));
  while(work.length)work.pop()!();
  if(!proposition)fail("FOL_SYNTAX","expected proposition");
  if (cursor !== tokens.length) fail("FOL_SYNTAX", "unexpected trailing proposition tokens");
  for (const symbol of [...functions.keys(), ...predicates.keys(), ...constants.keys()]) {
    if (!used.has(symbol)) fail("FOL_UNUSED_SYMBOL", `unused signature symbol ${symbol}`);
  }
  return proposition!;
}
