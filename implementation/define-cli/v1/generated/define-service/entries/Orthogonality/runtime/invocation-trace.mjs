import { createHash } from 'node:crypto';
const hash = (value) => createHash('sha256').update(value).digest('hex');
const code = (error) => typeof error?.code === 'string' && /^[A-Z][A-Z0-9_]*$/.test(error.code) ? error.code : String(error?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'FUNCTION_INTERNAL';
// No getter execution or user toJSON hooks; exact bigint is explicitly tagged.
function encode(value, depth = 0) {
    if (depth > 40)
        throw Error('TRACE_DEPTH');
    if (typeof value === 'bigint')
        return { $uint64: value.toString() };
    if (value === null || ['string', 'boolean'].includes(typeof value))
        return value;
    if (typeof value === 'number' && Number.isFinite(value))
        return value;
    if (value === undefined)
        return { $absent: true };
    if (typeof value !== 'object' || ![Object.prototype, null, Array.prototype].includes(Object.getPrototypeOf(value)))
        throw Error('TRACE_VALUE');
    const result = Array.isArray(value) ? [] : Object.create(null);
    for (const key of Object.keys(value).sort()) {
        const d = Object.getOwnPropertyDescriptor(value, key);
        if (!('value' in d))
            throw Error('TRACE_ACCESSOR');
        result[key] = encode(d.value, depth + 1);
    }
    return result;
}
function inputHash(input) { try {
    return hash(JSON.stringify(encode(input)));
}
catch {
    return null;
} }
/** Local, provided-input diagnostic. No credentials or provider-fetch path is accepted. */
export function createTracedInvoker(model, bindings, api, execute, validateInput, ontology, identity, createBoundary, modules = {}) {
    return async function invokeWithTrace(input, options = {}) {
        const maxEvents = options.maxEvents ?? 10000, maxBytes = options.maxBytes ?? 2097152;
        if (!Number.isInteger(maxEvents) || maxEvents < 1 || maxEvents > 20000 || !Number.isInteger(maxBytes) || maxBytes < 256 || maxBytes > 4194304)
            throw Error('TRACE_LIMIT_OPTIONS');
        const events = [];
        let bytes = 2, truncated = false, dropped = 0;
        const { manifest, ...buildIdentity } = identity;
        const build_manifest_sha256 = hash(JSON.stringify(manifest, null, 2) + '\n');
        const nodes = new Map(ontology.nodes.map((n) => [n.name, n]));
        const resultNode = ontology.nodes.find((n) => n.kind === 'result');
        const observe = (event) => {
            if (truncated) {
                dropped++;
                return;
            }
            try {
                const n = event.definition ?? nodes.get(event.declaration) ?? resultNode;
                const prefix = event.kind === 'query-row' ? 'where ' : event.kind === 'assertion' ? 'require ' : ['result-case', 'selected-case'].includes(event.kind) ? 'when ' : null;
                const clauses = prefix ? n?.clauses.filter((c) => c.text.startsWith(prefix)) : [];
                const clause = prefix === 'where ' ? clauses[0] : clauses[event.index];
                const encoded = encode({ ...event, definition: n ? { name: n.name, id: n.id, source: n.source } : null, ...(clause ? { clause } : {}), sequence: events.length });
                const size = Buffer.byteLength(JSON.stringify(encoded)) + 1;
                if (events.length >= maxEvents || bytes + size > maxBytes) {
                    truncated = true;
                    dropped++;
                    return;
                }
                bytes += size;
                events.push(encoded);
                if (event.kind === 'module-error' && event.code === 'FUNCTION_MODULE_TIMEOUT')
                    truncated = true;
            }
            catch {
                truncated = true;
                dropped++;
            }
        };
        const localModel = { ...model, integrations: Object.fromEntries(Object.entries(model.integrations).map(([id, b]) => [id, { ...b, transport: b.transport.startsWith('module-') ? b.transport : 'provided' }])) };
        const boundary = createBoundary(localModel, bindings, (roots) => execute(roots, api, observe), (roots) => validateInput(roots, observe), modules, observe, (roots, binding) => execute(roots, api, observe, binding), (roots, binding) => execute(roots, api, observe, binding, 'input'));
        let outcome;
        const input_sha256 = inputHash(input);
        try {
            const result = await boundary.invoke(input, {}, { localOnly: true, fetch: async () => { throw Error('TRACE_NETWORK_FORBIDDEN'); } });
            outcome = { status: 'succeeded', result: encode(result) };
        }
        catch (error) {
            outcome = { status: 'failed', code: code(error) };
        }
        const declarations = ontology.nodes.filter((n) => ['mapping', 'query', 'rule', 'calculation'].includes(n.kind)).map((n) => {
            const starts = events.filter(e => !e.module && e.kind === 'node-start' && e.declaration === n.name).length;
            const errors = events.filter(e => !e.module && e.kind === 'node-error' && e.declaration === n.name);
            const completed = events.filter(e => !e.module && e.kind === 'node-result' && e.declaration === n.name).length;
            return { name: n.name, id: n.id, invocations_observed: starts, state: truncated ? 'not_fully_observed' : errors.length ? 'failed' : starts === 0 ? 'not_evaluated' : completed === starts ? 'succeeded' : 'not_fully_observed' };
        });
        const queries = ontology.nodes.filter((n) => n.kind === 'query').map((n) => {
            const rows = events.filter(e => !e.module && e.kind === 'query-row' && e.declaration === n.name);
            const total = events.find(e => !e.module && e.kind === 'query-start' && e.declaration === n.name)?.total ?? null;
            const complete = !truncated && events.some(e => !e.module && e.kind === 'node-result' && e.declaration === n.name);
            return { name: n.name, source: n.source, source_count: total, evaluated: rows.length, accepted: rows.filter(e => e.accepted).length, complete };
        });
        const selected = events.find(e => !e.module && e.kind === 'selected-case');
        const answer = outcome.status === 'failed' ? `Invocation failed with ${outcome.code}.` : truncated ? 'Invocation succeeded; trace capture is incomplete.' : `Invocation returned ${typeof outcome.result?.status === 'string' ? outcome.result.status : 'a result'} because case ${selected ? selected.index + 1 : 'not observed'} matched${selected?.clause ? ': ' + selected.clause.text : '.'}`;
        return { schema_version: 'alchlang.invocation-trace/v1', binding: { ...buildIdentity, build_manifest_sha256, input_sha256 }, execution_mode: 'local-provided-inputs', outcome, capture: { complete: !truncated, truncated, dropped_events: dropped, recorded_bytes: bytes, max_events: maxEvents, max_bytes: maxBytes }, answer, selection_reason: !truncated && selected ? { clause: selected.clause, rule_results: events.filter(e => !e.module && e.kind === 'node-result' && e.node_kind === 'Rule').map(e => ({ name: e.declaration, value: e.value, source: e.definition.source })) } : null, selected_case: selected?.index ?? null, queries, declarations, events, authority_effect: 'none', claim: 'local generated-code observation; not a signed attestation' };
    };
}
