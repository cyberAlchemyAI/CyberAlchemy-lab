import path from 'node:path';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {selectRealization} from '../meta-types/catalog.js';
import type {TypedRecordContract, TypedRuleContract, RuleExpression, ValueExpression} from '../typed-operation/contracts.js';
import type {TypedQueryContract, BackendPredicate, BackendValue} from '../typed-backend/contracts.js';
import type {PlannedArtifact} from './contracts.js';

// Candidate compiler selection, deliberately separate from numeric realizationProfile.
export const PROFILED_SELECTION_VERSION = 'domainspec.profiled-project-selection/v1-candidate';
export const PROFILED_SOURCE_DIGESTS = Object.freeze({
  base: '48d0ba174105b020bb6b94c79c27b208a67f7d5f92d4c0c9c3a28c7d91a04d9f',
  typescript: '32cf17b4a0c4d5c36f344d6cec22450a041b52e7a5bdef129a74ac319694b6b0',
});
export interface ProfiledSelection {
  readonly schema_version: typeof PROFILED_SELECTION_VERSION;
  readonly language: 'typescript';
  readonly source_root: string;
  readonly profile_digests: typeof PROFILED_SOURCE_DIGESTS;
  readonly entity_rules: readonly Readonly<{entity: string; rule: string; parameter: string}>[];
}
export interface ProfiledModule {
  readonly selector: string;
  readonly kind: string;
  readonly relative_path: string;
  readonly callable: string;
  readonly imports: readonly Readonly<{path: string; symbol: string; type_only: boolean}>[];
}
export interface ProfiledProjectPlan {
  readonly schema_version: 'domainspec.profiled-project-plan/v1-candidate';
  readonly selection: ProfiledSelection;
  readonly certificate: ReturnType<typeof createCompiledProjectCertificate>;
  readonly modules: readonly ProfiledModule[];
  readonly realizations: readonly ReturnType<typeof selectRealization>[];
  readonly artifacts: readonly PlannedArtifact[];
  readonly authority_effect: 'none';
  readonly plan_sha256: string;
}
function fail(message: string): never {throw new Error('DS_PROFILE_L0:' + message);}
function keys(value: unknown, expected: string[], label: string): asserts value is Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).sort().join('|') !== expected.sort().join('|')) fail('unknown or missing fields:' + label);
}
const pascal = (s: string) => s.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('');
const quote = JSON.stringify;
function leafImport(from: string, to: string): string {
  const rel = path.posix.relative(path.posix.dirname(from), to).replace(/\.ts$/, '.js');
  return rel.startsWith('.') ? rel : './' + rel;
}
function ruleValue(expr: ValueExpression, parameter: string, fields: TypedRecordContract): string {
  if (expr.op === 'literal' && (expr.type === 'String' || expr.type === 'Bool')) return quote(expr.value);
  if (expr.op !== 'path' || expr.root !== parameter || expr.properties.length !== 1) return fail('unsupported L0 Rule value');
  const field = fields.properties.find(p => p.ontology_property === expr.properties[0]);
  if (!field) return fail('unbound Rule field');
  return `fields[${quote(field.name)}]`;
}
function ruleExpression(expr: RuleExpression, parameter: string, fields: TypedRecordContract): string {
  if (expr.op === 'all' || expr.op === 'any') return '(' + expr.terms.map(t => ruleExpression(t, parameter, fields)).join(expr.op === 'all' ? ' && ' : ' || ') + ')';
  if (expr.op === 'not') return '!(' + ruleExpression(expr.term, parameter, fields) + ')';
  if (expr.op === 'eq') return `(${ruleValue(expr.left, parameter, fields)} === ${ruleValue(expr.right, parameter, fields)})`;
  return fail('unsupported L0 Rule expression:' + expr.op);
}
function queryValue(value: BackendValue): string {
  if (value.kind === 'literal') return quote(value.value);
  return `${value.kind === 'field' ? 'row' : 'parameters'}[${quote(value.name)}]`;
}
function queryExpression(expr: BackendPredicate): string {
  if (expr.op === 'all' || expr.op === 'any') return '(' + expr.terms.map(queryExpression).join(expr.op === 'all' ? ' && ' : ' || ') + ')';
  if (expr.op === 'not') return '!(' + queryExpression(expr.term) + ')';
  if (expr.op === 'eq') return `(${queryValue(expr.left)} === ${queryValue(expr.right)})`;
  return fail('unsupported L0 Query predicate:' + expr.op);
}
function entitySource(name: string, fields: TypedRecordContract, rule: string, rulePath: string, ruleSelector: string): string {
  const types = fields.properties.map(p => `  readonly ${quote(p.name)}: ${p.type.kind === 'scalar' && p.type.name === 'Bool' ? 'boolean' : 'string'};`).join('\n');
  const checks = fields.properties.map(p => `typeof descriptors[${quote(p.name)}]?.value === ${quote(p.type.kind === 'scalar' && p.type.name === 'Bool' ? 'boolean' : 'string')}`).join(' && ');
  const copy = fields.properties.map(p => `${quote(p.name)}: descriptors[${quote(p.name)}]!.value`).join(', ');
  const identity = fields.properties.filter(p => p.identity).map(p => `fields[${quote(p.name)}]`).join(', ');
  return `import { ${rule} } from ${quote(rulePath)};
export interface ${name}Fields {\n${types}\n}
const brand: unique symbol = Symbol(${quote(name)});
const snapshots = new WeakSet<object>();
export interface ${name}Snapshot {
  readonly [brand]: true;
  readonly fields: ${name}Fields;
  readonly hash: () => string;
  readonly sameIdentity: (other: ${name}Snapshot) => boolean;
}
type Result = Readonly<{ok:true; value:${name}Snapshot; failure_codes:readonly string[]}> | Readonly<{ok:false; value:null; failure_codes:readonly string[]}>;
type Validator = (fields:${name}Fields) => boolean;
interface Factory {
  readonly create:(input:unknown)=>Result;
  readonly reconstruct:(input:unknown)=>Result;
  readonly transition:(previous:${name}Snapshot,input:unknown)=>Result;
  readonly extend:(validate:Validator)=>Factory;
}
const failure = (code:string):Result => Object.freeze({ok:false, value:null, failure_codes:Object.freeze([code])});
const identityKey = (fields:${name}Fields):string => JSON.stringify([${identity}]);
const makeFactory = (extra:readonly Validator[]):Factory => {
  const construct = (input:unknown, previous?:${name}Snapshot):Result => {
    if (input === null || typeof input !== 'object' || Array.isArray(input)) return failure('INVALID_FIELDS');
    const descriptors = Object.getOwnPropertyDescriptors(input);
    if (Reflect.ownKeys(input).length !== ${fields.properties.length} || !(${checks}) || Object.values(descriptors).some(d => !Object.hasOwn(d,'value'))) return failure('INVALID_FIELDS');
    const fields:${name}Fields = Object.freeze({${copy}});
    // Every exposed construction route reaches the bound Rule before a snapshot exists.
    if (!${rule}(fields)) return failure(${quote('RULE_FAILED:' + ruleSelector)});
    try { if (!extra.every(validate => validate(fields) === true)) return failure('EXTENSION_FAILED'); }
    catch { return failure('EXTENSION_FAILED'); }
    const key = identityKey(fields);
    if (previous !== undefined && (!snapshots.has(previous) || previous.hash() !== key)) return failure('IDENTITY_CHANGED');
    const value:${name}Snapshot = Object.freeze({[brand]:true as const, fields, hash:()=>key, sameIdentity:(other:${name}Snapshot)=>snapshots.has(other) && other.hash() === key});
    snapshots.add(value);
    return Object.freeze({ok:true, value, failure_codes:Object.freeze([])});
  };
  return Object.freeze({
    create:(input:unknown):Result=>construct(input),
    reconstruct:(input:unknown):Result=>construct(input),
    transition:(previous:${name}Snapshot,input:unknown):Result=>snapshots.has(previous) ? construct(input,previous) : failure('INVALID_PREVIOUS'),
    extend:(validate:Validator):Factory=>{if(typeof validate!=='function') throw new TypeError('validator must be callable'); return makeFactory(Object.freeze([...extra,validate]));},
  });
};
export const create${name}Factory = () => makeFactory(Object.freeze([]));
`;
}

/** Uses only the existing checked snapshot. No project file is reread. */
export function planProfiledProject(graph: CompiledProjectGraph, selection: ProfiledSelection, profiles: Readonly<{base:string; typescript:string}>): ProfiledProjectPlan {
  assertCompiledProjectSnapshot(graph);
  keys(selection,['schema_version','language','source_root','profile_digests','entity_rules'],'selection');
  keys(selection.profile_digests,['base','typescript'],'profile digests');
  keys(profiles,['base','typescript'],'profile sources');
  if (selection.schema_version !== PROFILED_SELECTION_VERSION || selection.language !== 'typescript') fail('unsupported selection version/language');
  if (typeof selection.source_root !== 'string' || !/^[a-z][a-z0-9-]*(?:\/[a-z][a-z0-9-]*)*$/.test(selection.source_root)) fail('unsafe source root');
  for (const axis of ['base','typescript'] as const) {
    if (selection.profile_digests[axis] !== PROFILED_SOURCE_DIGESTS[axis] || sha256(profiles[axis]) !== PROFILED_SOURCE_DIGESTS[axis]) fail('stale or tampered profile:' + axis);
  }
  if (graph.compositions?.length || graph.nodes.length !== 3 || new Set(graph.nodes.map(n=>n.feature_id)).size !== 1) fail('L0 requires one feature and Entity/Rule/Query only');
  const entity = graph.nodes.find(n=>n.kind==='Entity');
  const rule = graph.nodes.find(n=>n.kind==='Rule');
  const query = graph.nodes.find(n=>n.kind==='Query');
  if (!entity || !rule || !query) return fail('L0 type denominator');
  if (!Array.isArray(selection.entity_rules) || selection.entity_rules.length !== 1) fail('exactly one declared factory Rule binding required');
  const binding = selection.entity_rules[0]!;
  keys(binding,['entity','rule','parameter'],'factory binding');
  if (typeof binding.parameter !== 'string') fail('factory parameter must be a name');
  if (binding.entity !== entity.selector || binding.rule !== rule.selector) fail('unresolved factory binding');
  const record = entity.body.typed_contract as TypedRecordContract | undefined;
  const ruleContract = rule.body.typed_contract as TypedRuleContract | undefined;
  const queryContract = query.body.typed_contract as TypedQueryContract | undefined;
  if (record?.schema_version !== 'domainspec.typed-record/v1' || ruleContract?.schema_version !== 'domainspec.typed-rule/v1' || queryContract?.schema_version !== 'domainspec.typed-query/v1') return fail('typed contracts required');
  if (!record.properties.some(p=>p.identity) || record.properties.some(p=>p.cardinality!=='one' || p.type.kind!=='scalar' || !['String','Bool'].includes(p.type.name))) fail('unsupported L0 field envelope');
  const parameter = ruleContract.parameters[0];
  if (!parameter || ruleContract.parameters.length !== 1 || parameter.name !== binding.parameter || parameter.type.kind !== 'named' || parameter.type.selector !== entity.selector) fail('Rule must bind its Entity parameter');
  if (queryContract.source !== entity.selector || queryContract.inputs.some(p=>p.type.kind!=='scalar' || !['String','Bool'].includes(p.type.name))) fail('unsupported L0 Query binding');
  const profile = JSON.parse(profiles.typescript) as {constraints: Array<{constraint_id:string;expected:string}>};
  const baseRoot = selection.source_root + '/src/';
  const entityPath = baseRoot+'domain/entities/'+entity.node_id+'.ts';
  const rulePath = baseRoot+'domain/rules/'+rule.node_id+'.ts';
  const queryPath = baseRoot+'application/queries/'+query.node_id+'.ts';
  const location = profile.constraints.find(c=>c.constraint_id==='typescript.rule-location');
  if (!location || !new RegExp(location.expected).test(rulePath.slice(selection.source_root.length+1))) fail('Rule profile location mismatch');
  const name = pascal(entity.node_id), ruleFn = 'rule'+pascal(rule.node_id), queryFn = 'query'+pascal(query.node_id);
  const modules: ProfiledModule[] = [
    {selector:entity.selector,kind:'Entity',relative_path:entityPath,callable:'create'+name+'Factory',imports:[{path:leafImport(entityPath,rulePath),symbol:ruleFn,type_only:false}]},
    {selector:rule.selector,kind:'Rule',relative_path:rulePath,callable:ruleFn,imports:[{path:leafImport(rulePath,entityPath),symbol:name+'Fields',type_only:true}]},
    {selector:query.selector,kind:'Query',relative_path:queryPath,callable:queryFn,imports:[{path:leafImport(queryPath,entityPath),symbol:name+'Snapshot',type_only:true}]},
  ];
  const ruleSource = `import type { ${name}Fields } from ${quote(leafImport(rulePath,entityPath))};\nexport const ${ruleFn} = (fields:${name}Fields):boolean => ${ruleExpression(ruleContract.expression,binding.parameter,record)};\n`;
  const predicate = queryContract.filter ? queryExpression(queryContract.filter) : 'true';
  const ordering = queryContract.order_by;
  const sort = ordering ? `selected = [...selected].sort((a,b)=>a[${quote(ordering.field)}] === b[${quote(ordering.field)}] ? 0 : a[${quote(ordering.field)}] < b[${quote(ordering.field)}] ? ${ordering.direction==='asc'?-1:1} : ${ordering.direction==='asc'?1:-1});` : '';
  const querySource = `import type { ${name}Snapshot } from ${quote(leafImport(queryPath,entityPath))};
export const ${queryFn} = (snapshots:readonly ${name}Snapshot[], parameters:Readonly<{${queryContract.inputs.map(p=>`${quote(p.name)}:${p.type.kind==='scalar'&&p.type.name==='Bool'?'boolean':'string'}`).join(';')}}>) => {
  ${queryContract.inputs.map(p=>`if(!Object.hasOwn(parameters,${quote(p.name)})) throw new TypeError(${quote('missing parameter:'+p.name)});`).join('\n  ')}
  let selected = snapshots.map(snapshot=>snapshot.fields).filter(row=>${predicate});
  ${sort}
  ${queryContract.limit === null ? '' : `selected = selected.slice(0,${queryContract.limit});`}
  return Object.freeze(selected.map(row=>Object.freeze({${queryContract.projection.map(f=>`${quote(f)}:row[${quote(f)}]`).join(',')}})));
};
`;
  const contents = [entitySource(name,record,ruleFn,leafImport(entityPath,rulePath),rule.selector),ruleSource,querySource];
  const artifacts = modules.map((m,i)=>Object.freeze({relative_path:m.relative_path,content:contents[i]!,sha256:sha256(contents[i]!),size_bytes:Buffer.byteLength(contents[i]!)})).sort((a,b)=>a.relative_path < b.relative_path ? -1 : 1);
  // Clone caller-owned selection so mutation after planning cannot alter the bound plan.
  const body = {schema_version:'domainspec.profiled-project-plan/v1-candidate' as const, selection:JSON.parse(canonicalJson(selection)) as ProfiledSelection,
    certificate:createCompiledProjectCertificate(graph), modules, realizations:graph.nodes.map(n=>selectRealization(n.meta_type_id,'typescript')),
    artifacts, authority_effect:'none' as const};
  const freeze = <T>(value:T):T => {if(value && typeof value==='object'){Object.freeze(value);Object.values(value).forEach(freeze);}return value;};
  return freeze({...body,plan_sha256:sha256(canonicalJson(body))});
}
