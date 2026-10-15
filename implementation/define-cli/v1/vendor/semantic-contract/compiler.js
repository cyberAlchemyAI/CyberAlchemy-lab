import {publishDirectory} from '../../src/publish-directory.mjs';
import { createHash } from 'node:crypto';
import { lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, realpathSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { loadDomainSpecCompiler } from './craft-adapter.mjs';
const KINDS = new Set(['axiom', 'intrinsic', 'invariant', 'governed-by', 'validation']);
const OPERATIONS = new Set(['normalize-nfkc', 'canonical-text', 'semantic-key', 'contains-token', 'contains-phrase', 'append-reason']);
const REQUIRED = {
    axiom: ['ontology', 'meaning', 'statement', 'subject', 'commitment'],
    intrinsic: ['ontology', 'meaning', 'operation', 'input', 'output'],
    invariant: ['ontology', 'meaning', 'grounded-by', 'intrinsic', 'property', 'violation'],
    'governed-by': ['constitution-ref', 'version', 'status', 'selector', 'adopted', 'authority-effect'],
    validation: ['invariant', 'method', 'fixtures', 'claim'],
};
const fail = (message) => { throw Error(`ALCH_SEMANTIC_CONTRACT: ${message}`); };
export const digest = (value) => createHash('sha256').update(value).digest('hex');
const json = (value) => JSON.stringify(value, null, 2) + '\n';
const safe = (value) => /^[A-Za-z][A-Za-z0-9_-]{0,127}$/.test(value);
const unquote = (value) => {
    if (value.startsWith('"')) {
        try {
            const parsed = JSON.parse(value);
            if (typeof parsed !== 'string')
                fail('quoted value must be a string');
            return parsed;
        }
        catch {
            fail(`invalid quoted value ${value}`);
        }
    }
    return value;
};
const regularFiles = (root) => readdirSync(root, { withFileTypes: true }).flatMap(entry => entry.isDirectory() ? regularFiles(path.join(root, entry.name)) : [path.join(root, entry.name)]);
export function executeSemanticOperation(operation, input) {
    if (operation === 'normalize-nfkc') {
        if (typeof input !== 'string')
            fail('normalize-nfkc input must be string');
        return input.normalize('NFKC');
    }
    if (operation === 'canonical-text') {
        if (typeof input !== 'string')
            fail('canonical-text input must be string');
        return input.normalize('NFKC').trim().toLowerCase();
    }
    if (operation === 'semantic-key') {
        if (typeof input !== 'string')
            fail('semantic-key input must be string');
        return input.normalize('NFKC').trim().toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
    }
    if (operation === 'contains-token') {
        if (!input || typeof input !== 'object' || typeof input.text !== 'string' || typeof input.token !== 'string')
            fail('contains-token input must contain text and token strings');
        const canonical = (value) => value.normalize('NFKC').trim().toLowerCase();
        const token = canonical(input.token), tokens = canonical(input.text).match(/[\p{L}\p{N}_]+/gu) ?? [];
        return tokens.includes(token);
    }
    if (operation === 'contains-phrase') {
        if (!input || typeof input !== 'object' || typeof input.text !== 'string' || typeof input.phrase !== 'string')
            fail('contains-phrase input must contain text and phrase strings');
        const key = (value) => value.normalize('NFKC').trim().toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim(), text = key(input.text), phrase = key(input.phrase);
        return phrase.length > 0 && (` ${text} `).includes(` ${phrase} `);
    }
    if (operation === 'append-reason') {
        if (!input || typeof input !== 'object' || !Array.isArray(input.reasons) || typeof input.reason !== 'string' || !input.reasons.every((item) => typeof item === 'string'))
            fail('append-reason input must contain reasons string array and reason string');
        const reasons = [...input.reasons], reason = input.reason;
        if (!reasons.includes(reason))
            reasons.push(reason);
        return reasons;
    }
    return fail(`unsupported operation ${operation}`);
}
function parse(source) {
    if (source.charCodeAt(0) === 0xfeff)
        fail('UTF-8 BOM is forbidden');
    if (source.includes('```'))
        fail('Markdown fences are forbidden');
    const headers = {}, declarations = [];
    let current;
    for (const [offset, raw] of source.split(/\r?\n/).entries()) {
        const line = offset + 1;
        if (!raw.trim() || raw.trimStart().startsWith('#'))
            continue;
        if (!raw.startsWith(' ')) {
            const declaration = raw.match(/^(axiom|intrinsic|invariant|governed-by|validation) ([A-Za-z][A-Za-z0-9_-]{0,127}):$/);
            if (declaration) {
                current = { kind: declaration[1], name: declaration[2], line, fields: {} };
                declarations.push(current);
                continue;
            }
            const header = raw.match(/^(domain|profile|owner|logic|runtime) (.+)$/);
            if (!header) {
                fail(`line ${line}: unsupported top-level statement`);
            }
            if (headers[header[1]])
                fail(`line ${line}: duplicate ${header[1]}`);
            headers[header[1]] = unquote(header[2]);
            current = undefined;
            continue;
        }
        if (!current) {
            fail(`line ${line}: clause without declaration`);
        }
        const clause = raw.match(/^  ([a-z][a-z0-9-]*) (.+)$/);
        if (!clause) {
            fail(`line ${line}: invalid clause`);
        }
        if (current.fields[clause[1]])
            fail(`line ${line}: duplicate clause ${clause[1]}`);
        current.fields[clause[1]] = unquote(clause[2]);
    }
    for (const header of ['domain', 'profile', 'owner', 'logic', 'runtime'])
        if (!headers[header])
            fail(`missing ${header}`);
    if (headers.profile !== 'semantic-contract-v1')
        fail('profile must be semantic-contract-v1');
    if (headers.logic !== 'sfol-v1')
        fail('logic must be sfol-v1');
    if (headers.runtime !== 'node>=26.8.1')
        fail('runtime must be node>=26.8.1');
    if (!safe(headers.owner))
        fail('unsafe owner');
    if (!declarations.length)
        fail('at least one declaration is required');
    for (const kind of KINDS)
        if (!declarations.some(item => item.kind === kind))
            fail(`at least one ${kind} declaration is required`);
    if (declarations.filter(item => item.kind === 'governed-by').length !== 1)
        fail('exactly one governed-by declaration is required');
    const names = new Set(), ontology = new Set();
    for (const declaration of declarations) {
        if (!KINDS.has(declaration.kind) || names.has(declaration.name))
            fail(`duplicate or unsupported declaration ${declaration.name}`);
        names.add(declaration.name);
        const allowed = new Set(REQUIRED[declaration.kind]);
        for (const key of Object.keys(declaration.fields))
            if (!allowed.has(key))
                fail(`${declaration.name}: unsupported clause ${key}`);
        for (const key of allowed)
            if (!declaration.fields[key])
                fail(`${declaration.name}: missing ${key}`);
        const ontologyId = declaration.fields.ontology;
        if (ontologyId) {
            if (ontology.has(ontologyId))
                fail(`duplicate ontology identity ${ontologyId}`);
            ontology.add(ontologyId);
        }
    }
    const byName = new Map(declarations.map(item => [item.name, item]));
    const requireKind = (owner, field, kind) => { const target = byName.get(owner.fields[field]); if (!target || target.kind !== kind)
        fail(`${owner.name}: ${field} must reference ${kind}`); };
    for (const declaration of declarations) {
        if (declaration.kind === 'intrinsic' && !OPERATIONS.has(declaration.fields.operation))
            fail(`${declaration.name}: unsupported operation ${declaration.fields.operation}`);
        if (declaration.kind === 'invariant') {
            requireKind(declaration, 'grounded-by', 'axiom');
            requireKind(declaration, 'intrinsic', 'intrinsic');
        }
        if (declaration.kind === 'validation') {
            requireKind(declaration, 'invariant', 'invariant');
            if (declaration.fields.method !== 'fixture' || declaration.fields.claim !== 'finite-evidence-only')
                fail(`${declaration.name}: validation must be fixture and finite-evidence-only`);
        }
        if (declaration.kind === 'governed-by' && (declaration.fields.status !== 'candidate' || declaration.fields.adopted !== 'false' || declaration.fields['authority-effect'] !== 'none'))
            fail(`${declaration.name}: constitutions must remain candidate, unadopted, and authority-effect none`);
    }
    const invariants = declarations.filter(item => item.kind === 'invariant');
    for (const invariant of invariants)
        if (declarations.filter(item => item.kind === 'validation' && item.fields.invariant === invariant.name).length !== 1)
            fail(`${invariant.name}: exactly one validation required`);
    return { headers, declarations };
}
function loadFixtures(root, declarations) {
    const paths = [...new Set(declarations.filter(item => item.kind === 'validation').map(item => item.fields.fixtures))];
    const all = [];
    const sources = {};
    for (const relative of paths) {
        if (path.isAbsolute(relative) || path.relative(root, path.resolve(root, relative)).startsWith('..'))
            fail(`fixture path escapes source root: ${relative}`);
        const resolved = realpathSync(path.resolve(root, relative));
        if (path.relative(root, resolved).startsWith('..'))
            fail(`fixture real path escapes source root: ${relative}`);
        const bytes = readFileSync(resolved, 'utf8');
        let parsed;
        try {
            parsed = JSON.parse(bytes);
        }
        catch {
            fail(`invalid fixture JSON: ${relative}`);
        }
        if (!Array.isArray(parsed))
            fail(`fixture file must contain an array: ${relative}`);
        const rows = parsed;
        sources[relative] = { sha256: digest(bytes), bytes };
        for (const value of rows) {
            if (!value || typeof value !== 'object')
                fail(`invalid fixture in ${relative}`);
            const row = value;
            if (typeof row.name !== 'string' || typeof row.validation !== 'string' || typeof row.operation !== 'string' || !('input' in row) || !('expected' in row))
                fail(`invalid fixture shape in ${relative}`);
            if (!OPERATIONS.has(row.operation))
                fail(`unsupported fixture operation ${row.operation}`);
            all.push({ ...row, source_file: relative });
        }
    }
    const validations = declarations.filter(item => item.kind === 'validation');
    for (const validation of validations) {
        const cases = all.filter(item => item.validation === validation.name && item.source_file === validation.fields.fixtures);
        if (!cases.length)
            fail(`${validation.name}: at least one fixture required in ${validation.fields.fixtures}`);
        const invariant = declarations.find(item => item.kind === 'invariant' && item.name === validation.fields.invariant);
        const intrinsic = declarations.find(item => item.kind === 'intrinsic' && item.name === invariant.fields.intrinsic);
        if (cases.some(item => item.operation !== intrinsic.fields.operation))
            fail(`${validation.name}: fixture operation differs from invariant intrinsic`);
    }
    const validationNames = new Set(validations.map(item => item.name));
    for (const fixture of all)
        if (!validationNames.has(fixture.validation))
            fail(`${fixture.name}: unknown validation ${fixture.validation}`);
    if (new Set(all.map(item => item.name)).size !== all.length)
        fail('fixture names must be unique');
    return { fixtures: all, sources };
}
function ontologyOf(sourcePath, sourceSha, domain, declarations) {
    const id = (item) => item.fields.ontology ?? item.fields['constitution-ref'] ?? `ALCH-${createHash('sha256').update(JSON.stringify([domain, item.kind, item.name])).digest('hex').slice(0, 24).toUpperCase()}`;
    const nodes = declarations.map(item => ({ id: id(item), name: item.name, kind: item.kind, meta_type: item.kind === 'invariant' || item.kind === 'validation' ? 'Rule' : item.kind === 'intrinsic' ? 'Calculation' : 'Entity', meaning: item.fields.meaning ?? `${item.kind} ${item.name}`, source: { path: path.basename(sourcePath), line: item.line, sha256: sourceSha }, ...(item.kind === 'governed-by' ? { candidate: true, adopted: false, selector: item.fields.selector } : {}) }));
    const refs = [];
    for (const item of declarations) {
        if (item.kind === 'invariant') {
            refs.push({ source: id(declarations.find(row => row.name === item.fields['grounded-by'])), target: id(item), role: 'grounds' });
            refs.push({ source: id(item), target: id(declarations.find(row => row.name === item.fields.intrinsic)), role: 'constrains' });
        }
        if (item.kind === 'validation')
            refs.push({ source: id(item), target: id(declarations.find(row => row.name === item.fields.invariant)), role: 'validates' });
        if (item.kind === 'governed-by')
            for (const invariant of declarations.filter(row => row.kind === 'invariant'))
                refs.push({ source: id(invariant), target: id(item), role: 'governed-by' });
    }
    return { schema_version: 'alchlang.semantic-contract-ontology/v1', source_format: 'alchlang', domain, source: { path: path.basename(sourcePath), sha256: sourceSha }, nodes, references: refs, status: 'generated-candidate', reference_semantics: 'compiler-local semantic links; not admitted ontology relationships', ontology_admitted: false, constitution_adopted: false, authority_effect: 'none' };
}
export async function compileSemanticContract(sourcePath) {
    const resolved = realpathSync(path.resolve(sourcePath));
    if (path.extname(resolved) !== '.alch')
        fail('source must be .alch');
    const source = readFileSync(resolved, 'utf8');
    if (Buffer.byteLength(source) > 1048576)
        fail('source exceeds 1 MiB');
    const parsed = parse(source), root = realpathSync(path.dirname(resolved)), loaded = loadFixtures(root, parsed.declarations), sourceSha = digest(source);
    const cases = loaded.fixtures.map(item => { let actual, error; try {
        actual = executeSemanticOperation(item.operation, item.input);
    }
    catch (reason) {
        error = reason instanceof Error ? reason.message : String(reason);
    } return { name: item.name, validation: item.validation, operation: item.operation, input: item.input, expected: item.expected, actual, error, pass: !error && JSON.stringify(actual) === JSON.stringify(item.expected) }; });
    const report = { schema_version: 'alchlang.semantic-contract-validation/v1', claim: 'Finite fixtures only; no universal proof, constitution adoption, or authority activation.', cases, summary: { total: cases.length, passed: cases.filter(item => item.pass).length, failed: cases.filter(item => !item.pass).length }, status: cases.every(item => item.pass) ? 'pass' : 'fail', authority_effect: 'none' };
    if (report.status !== 'pass')
        fail(`fixture validation failed: ${cases.filter(item => !item.pass).map(item => item.name).join(', ')}`);
    return { profile: 'semantic-contract-v1', sourcePath: resolved, root, source, source_sha256: sourceSha, ...parsed, ...loaded, ontology: ontologyOf(resolved, sourceSha, parsed.headers.domain, parsed.declarations), report, authority_effect: 'none' };
}
function projectFiles(compiled) {
    const feature = 'semantic-contract';
    const records = {};
    const nodeIds = [];
    for (const item of compiled.declarations) {
        const nodeId = item.name.replace(/([a-z0-9])([A-Z])/g, '$1-$2').replace(/_/g, '-').toLowerCase();
        nodeIds.push(nodeId);
        const kind = item.kind === 'intrinsic' ? 'Calculation' : item.kind === 'invariant' || item.kind === 'validation' ? 'Rule' : 'Entity';
        const description = item.fields.meaning ?? `${item.kind} ${item.name}`;
        const body = kind === 'Calculation' ? { description, inputs: ['input'] } : kind === 'Rule' ? { description, predicate: item.kind === 'invariant' ? item.fields.property : `fixture:${item.fields.fixtures}` } : { description, fields: [{ field_id: 'identity', type_ref: { kind: 'primitive', name: 'string' }, required: true }], identity_field: 'identity' };
        records[`specs/${feature}/nodes/${nodeId}.json`] = json({ schema_version: 'domainspec.node/v1', node_id: nodeId, feature_id: feature, kind, body });
    }
    records['project.json'] = json({ schema_version: 'domainspec.project/v1', project_id: 'alch-semantic-prelude', features: [feature], cross_feature_edges: [] });
    records[`specs/${feature}/feature.json`] = json({ schema_version: 'domainspec.feature/v1', feature_id: feature, nodes: nodeIds, edges: [] });
    return records;
}
function runtimeSource() {
    return `const canonical=value=>value.normalize('NFKC').trim().toLowerCase();
const semanticKeyValue=value=>canonical(value).replace(/[^\\p{L}\\p{N}]+/gu,' ').trim();
export function normalizeNfkc(value){if(typeof value!=='string')throw new TypeError('normalize-nfkc input must be string');return value.normalize('NFKC');}
export function canonicalText(value){if(typeof value!=='string')throw new TypeError('canonical-text input must be string');return canonical(value);}
export function semanticKey(value){if(typeof value!=='string')throw new TypeError('semantic-key input must be string');return semanticKeyValue(value);}
export function containsToken(input){if(!input||typeof input.text!=='string'||typeof input.token!=='string')throw new TypeError('contains-token input');return (canonical(input.text).match(/[\\p{L}\\p{N}_]+/gu)??[]).includes(canonical(input.token));}
export function containsPhrase(input){if(!input||typeof input.text!=='string'||typeof input.phrase!=='string')throw new TypeError('contains-phrase input');const text=semanticKeyValue(input.text),phrase=semanticKeyValue(input.phrase);return phrase.length>0&&(' '+text+' ').includes(' '+phrase+' ');}
export function appendReason(input){if(!input||!Array.isArray(input.reasons)||typeof input.reason!=='string'||!input.reasons.every(item=>typeof item==='string'))throw new TypeError('append-reason input');const reasons=[...input.reasons];if(!reasons.includes(input.reason))reasons.push(input.reason);return reasons;}
const operations={'normalize-nfkc':normalizeNfkc,'canonical-text':canonicalText,'semantic-key':semanticKey,'contains-token':containsToken,'contains-phrase':containsPhrase,'append-reason':appendReason};
export function invoke(operation,input){const selected=operations[operation];if(!selected)throw new Error('SEMANTIC_OPERATION_NOT_FOUND');return selected(input);}
`;
}
export async function checkSemanticContract(sourcePath) { const value = await compileSemanticContract(sourcePath); return { status: 'valid', profile: value.profile, axioms: value.declarations.filter(item => item.kind === 'axiom').length, invariants: value.declarations.filter(item => item.kind === 'invariant').length, validations: value.report.summary, authority_effect: 'none' }; }
export async function buildSemanticContract(sourcePath, outputPath) {
    const compiled = await compileSemanticContract(sourcePath), output = path.resolve(outputPath);
    try {
        lstatSync(output);
        fail('output exists');
    }
    catch (error) {
        if (error.code !== 'ENOENT')
            throw error;
    }
    mkdirSync(path.dirname(output), { recursive: true });
    const stage = mkdtempSync(path.join(path.dirname(output), '.alch-semantic-contract-'));
    const write = (name, value) => { const target = path.join(stage, name); mkdirSync(path.dirname(target), { recursive: true }); writeFileSync(target, value, { flag: 'wx' }); };
    try {
        write('app/prelude.mjs', runtimeSource());
        write('provenance/alch/source.alch', compiled.source);
        write('provenance/ontology.json', json(compiled.ontology));
        for (const [name, fixture] of Object.entries(compiled.sources))
            write(`provenance/alch/${name}`, fixture.bytes);
        const project = projectFiles(compiled);
        for (const [name, bytes] of Object.entries(project))
            write(`provenance/craft/project/${name}`, bytes);
        const compiler = await loadDomainSpecCompiler(), craft = compiler.compileProject(path.join(stage, 'provenance/craft/project'));
        const graph = { ...craft.graph, project_root: '.' };
        write('provenance/craft/graph.json', json(graph));
        write('evidence/craft/certificate.json', json(craft.certificate));
        write('evidence/craft/compiler-binding.json', json(compiler.binding));
        write('evidence/validation/report.json', json(compiled.report));
        if (readFileSync(compiled.sourcePath, 'utf8') !== compiled.source)
            fail('source drift');
        for (const [name, value] of Object.entries(compiled.sources))
            if (digest(readFileSync(path.join(compiled.root, name))) !== value.sha256)
                fail(`fixture drift ${name}`);
        const inventory = Object.fromEntries(regularFiles(stage).sort().map(file => [path.relative(stage, file).split(path.sep).join('/'), digest(readFileSync(file))]));
        write('manifest.json', json({ schema_version: 'alchlang.semantic-contract-build/v1', profile: compiled.profile, source_sha256: compiled.source_sha256, fixture_sha256: Object.fromEntries(Object.entries(compiled.sources).map(([name, value]) => [name, value.sha256])), pipeline: ['alch-source', 'semantic-contract-ontology', 'craft-project', 'domainspec-compile', 'runtime-projection', 'fixture-validation'], files: inventory, ontology_admitted: false, constitution_adopted: false, authority_effect: 'none' }));
        publishDirectory(stage, output);
        return { status: 'built', profile: compiled.profile, output, files: Object.keys(inventory).length + 1, validations: compiled.report.summary, authority_effect: 'none' };
    }
    catch (error) {
        rmSync(stage, { recursive: true, force: true });
        throw error;
    }
}
