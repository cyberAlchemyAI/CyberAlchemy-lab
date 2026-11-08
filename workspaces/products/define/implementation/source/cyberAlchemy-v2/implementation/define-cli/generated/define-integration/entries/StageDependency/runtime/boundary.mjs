export class FunctionFault extends Error {
    code;
    constructor(code) {
        super(code);
        this.code = code;
    }
}
const fail = (code) => { throw new FunctionFault(code); };
const own = (v, k) => Object.prototype.hasOwnProperty.call(v, k);
function plain(v) { if (!v || typeof v !== "object" || Array.isArray(v) || ![Object.prototype, null].includes(Object.getPrototypeOf(v)))
    fail("FUNCTION_RECORD"); for (const k of Reflect.ownKeys(v))
    if (typeof k !== "string" || !("value" in Object.getOwnPropertyDescriptor(v, k)))
        fail("FUNCTION_RECORD"); return v; }
function access(v, parts) { for (const k of parts) {
    if (v == null)
        return undefined;
    plain(v);
    v = own(v, k) ? v[k] : undefined;
} return v; }
function list(v) { if (!Array.isArray(v))
    fail("FUNCTION_LIST"); return v; }
const truth = (v) => { if (typeof v !== "boolean")
    fail("FUNCTION_BOOLEAN"); return v; };
export function portableTimestamp(value) {
    const m = /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]{1,9}))?(Z|[+-][0-9]{2}:[0-9]{2})$/.exec(value);
    if (!m)
        return false;
    const [year, month, day, hour, minute, second] = m.slice(1, 7).map(Number);
    const days = [31, year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    return year >= 1 && month >= 1 && month <= 12 && day >= 1 && day <= days[month - 1] && hour <= 23 && minute <= 59 && second <= 59 && (m[8] === 'Z' || Number(m[8].slice(1, 3)) <= 23 && Number(m[8].slice(4)) <= 59);
}
const portableId = (s) => s.replace(/^[ \t\r\n]+|[ \t\r\n]+$/g, '').length > 0;
export function validateSchema(model, name, value, depth = 0) {
    if (depth > 32)
        fail("FUNCTION_DEPTH");
    const fields = model.schemas[name];
    if (!fields)
        fail("FUNCTION_SCHEMA");
    plain(value);
    for (const k of Object.keys(value))
        if (!own(fields, k))
            fail("FUNCTION_UNKNOWN_FIELD");
    const result = Object.create(null);
    for (const [key, s] of (model.portability ? Object.entries(fields).sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0) : Object.entries(fields))) {
        let v = own(value, key) ? value[key] : undefined;
        if (v === undefined) {
            if (s.optional)
                continue;
            fail("FUNCTION_REQUIRED");
        }
        if (v === null) {
            if (!s.nullable)
                fail("FUNCTION_TYPE");
            if (own(s, 'const') && s.const !== null)
                fail('FUNCTION_CONST');
            result[key] = null;
            continue;
        }
        if (s.type === 'string' || s.type === 'identifier' || s.type === 'timestamp') {
            if (typeof v !== 'string')
                fail('FUNCTION_TYPE');
            if (s.type === 'identifier' && !(model.portability ? portableId(v) : v.trim()))
                fail('FUNCTION_ID');
            if (s.type === 'timestamp' && !(model.portability ? portableTimestamp(v) : !Number.isNaN(Date.parse(v))))
                fail('FUNCTION_TIMESTAMP');
            if (s.max !== undefined && v.length > s.max)
                fail('FUNCTION_LIMIT');
            if (s.pattern) {
                const match = new RegExp(s.pattern).exec(v);
                if (!match || model.portability && match[0].length !== v.length)
                    fail('FUNCTION_PATTERN');
            }
        }
        else if (s.type === 'integer') {
            if (!Number.isSafeInteger(v))
                fail('FUNCTION_TYPE');
            if (s.min !== undefined && v < s.min || s.max !== undefined && v > s.max)
                fail('FUNCTION_RANGE');
        }
        else if (s.type === 'boolean') {
            truth(v);
        }
        else if (s.type === 'list') {
            list(v);
            if (s.max !== undefined && v.length > s.max)
                fail('FUNCTION_LIMIT');
            v = v.map((x) => { if (['string', 'identifier'].includes(s.items)) {
                if (typeof x !== 'string' || s.items === 'identifier' && !(model.portability ? portableId(x) : x.trim()))
                    fail('FUNCTION_TYPE');
                return x;
            } return validateSchema(model, s.items, x, depth + 1); });
        }
        else
            v = validateSchema(model, s.type, v, depth + 1);
        if (own(s, 'const') && v !== s.const)
            fail('FUNCTION_CONST');
        result[key] = v;
    }
    return result;
}
async function boundedText(response, limit, timeout = 30000) {
    if (!response.body)
        return '';
    const reader = response.body.getReader();
    const chunks = [];
    let size = 0;
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; void reader.cancel().catch(() => { }); }, timeout);
    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) {
                if (timedOut)
                    fail('FUNCTION_TIMEOUT');
                break;
            }
            size += value.byteLength;
            if (size > limit) {
                await reader.cancel();
                fail('FUNCTION_BODY_LIMIT');
            }
            chunks.push(value);
        }
    }
    finally {
        clearTimeout(timer);
        reader.releaseLock();
    }
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) {
        bytes.set(chunk, offset);
        offset += chunk.length;
    }
    return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
}
export function prepareIntegrationRequest(b, scope, env) {
    const url = env[b.urlEnv];
    if (!url)
        fail('FUNCTION_ENV_REQUIRED');
    let target;
    try {
        target = new URL(url);
    }
    catch {
        return fail('FUNCTION_URL');
    }
    if (target.protocol !== 'https:' || target.username || target.password)
        fail('FUNCTION_URL');
    for (const key of Object.keys(b.query ?? {}).sort()) {
        const value = access(scope, b.query[key].split('.'));
        if (typeof value !== 'string' && typeof value !== 'number')
            fail('FUNCTION_INTEGRATION_QUERY');
        target.searchParams.set(key, String(value));
    }
    const headers = { accept: 'application/json' };
    if (b.secretEnv) {
        const secret = env[b.secretEnv];
        if (!secret)
            fail('FUNCTION_ENV_REQUIRED');
        headers.authorization = `Bearer ${secret}`;
    }
    return { url: target.href, method: 'GET', headers, redirect: 'error', timeout_ms: b.timeout, max_bytes: b.maxBytes };
}
export function createBoundary(model, bindings, compute, precheck = () => { }, modules = {}, observe, guard, mapInput) {
    const output = (result) => { try {
        validateSchema(model, model.endpoint.output, result);
    }
    catch {
        fail('FUNCTION_OUTPUT_SCHEMA');
    } return result; };
    async function invoke(input, env = {}, io = {}) {
        if (io.signal?.aborted)
            fail('FUNCTION_CANCELLED');
        const endpoint = model.endpoint;
        const scope = { input: validateSchema(model, endpoint.input, input) };
        try {
            precheck(scope);
        }
        catch (error) {
            const code = error?.code;
            if (typeof code === 'string')
                fail(code);
            throw error;
        }
        for (const step of bindings) {
            {
                const b = model.integrations[step.integration];
                if (step.condition) {
                    const event = (e) => { try {
                        observe?.(e);
                    }
                    catch { } };
                    let passed;
                    try {
                        if (!guard)
                            fail('FUNCTION_BINDING_REQUIRED');
                        passed = truth(guard(scope, step.name));
                    }
                    catch (e) {
                        const raw = String(e?.code ?? String(e?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'FUNCTION_INTERNAL');
                        const code = /^[A-Z][A-Z0-9_]*$/.test(raw) ? raw : 'FUNCTION_INTERNAL';
                        event({ kind: 'binding-error', declaration: step.integration, binding: step.name, code });
                        throw new FunctionFault(code);
                    }
                    event({ kind: 'binding-guard', declaration: step.integration, binding: step.name, passed });
                    if (!passed) {
                        event({ kind: 'module-skipped', declaration: step.integration, binding: step.name, module: b.module, transport: b.transport });
                        continue;
                    }
                }
                if (b.transport === 'module-local' || b.transport === 'module-http') {
                    let argument;
                    if (step.input) {
                        const event = (e) => { try {
                            observe?.(e);
                        }
                        catch { } };
                        try {
                            if (!mapInput)
                                fail('FUNCTION_BINDING_INPUT_REQUIRED');
                            argument = mapInput(scope, step.name);
                            try {
                                argument = validateSchema(model, step.input.type, argument);
                            }
                            catch {
                                fail('FUNCTION_MODULE_INPUT_SCHEMA');
                            }
                            event({ kind: 'binding-input', declaration: step.integration, binding: step.name });
                        }
                        catch (e) {
                            const raw = String(e?.code ?? String(e?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'FUNCTION_INTERNAL');
                            const code = /^[A-Z][A-Z0-9_]*$/.test(raw) ? raw : 'FUNCTION_INTERNAL';
                            event({ kind: 'binding-input-error', declaration: step.integration, binding: step.name, code });
                            throw new FunctionFault(code);
                        }
                    }
                    else
                        argument = access(scope, b.input.split('.'));
                    const body = JSON.stringify(argument);
                    if (body === undefined)
                        fail('FUNCTION_REQUIRED');
                    if (new TextEncoder().encode(body).length > b.maxBytes)
                        fail('FUNCTION_MODULE_LIMIT');
                    const event = (e) => { try {
                        observe?.(e);
                    }
                    catch { } };
                    event({ kind: 'module-start', declaration: step.integration, module: b.module, transport: b.transport });
                    let result;
                    try {
                        if (b.transport === 'module-local') {
                            if (!modules[b.module])
                                fail('FUNCTION_MODULE_REQUIRED');
                            const controller = new AbortController();
                            let timer;
                            let active = true;
                            try {
                                result = await Promise.race([modules[b.module](argument, env, { ...io, signal: io.signal ? AbortSignal.any([io.signal, controller.signal]) : controller.signal }, (e) => { if (active)
                                        event({ ...e, module: b.module + (e.module ? '.' + e.module : '') }); }), new Promise((_, reject) => { timer = setTimeout(() => { controller.abort(); reject(new FunctionFault('FUNCTION_MODULE_TIMEOUT')); }, b.timeout); })]);
                            }
                            finally {
                                active = false;
                                clearTimeout(timer);
                            }
                        }
                        else {
                            if (io.localOnly)
                                fail('FUNCTION_INTEGRATION_REQUIRED');
                            const prepared = { ...prepareIntegrationRequest(b, scope, env), method: 'POST', body };
                            prepared.headers['content-type'] = 'application/json';
                            io.observeRequest?.(prepared);
                            const controller = new AbortController(), timer = setTimeout(() => controller.abort(), b.timeout);
                            try {
                                const response = await (io.fetch ?? fetch)(new URL(prepared.url), { method: 'POST', body, headers: prepared.headers, redirect: 'error', signal: io.signal ? AbortSignal.any([io.signal, controller.signal]) : controller.signal });
                                if (!Object.values(model.modules[b.module].statuses).includes(response.status)) {
                                    await response.body?.cancel();
                                    fail('FUNCTION_INTEGRATION_STATUS');
                                }
                                result = JSON.parse(await boundedText(response, b.maxBytes));
                                if (model.modules[b.module].statuses[result?.status] !== response.status)
                                    fail('FUNCTION_INTEGRATION_STATUS');
                            }
                            catch (e) {
                                if (controller.signal.aborted)
                                    fail('FUNCTION_INTEGRATION_TIMEOUT');
                                if (e instanceof FunctionFault) {
                                    if (e.code === 'FUNCTION_BODY_LIMIT')
                                        fail('FUNCTION_INTEGRATION_LIMIT');
                                    throw e;
                                }
                                fail('FUNCTION_INTEGRATION_FAILED');
                            }
                            finally {
                                clearTimeout(timer);
                            }
                        }
                        try {
                            scope[step.name] = validateSchema(model, b.output, result);
                        }
                        catch {
                            fail('FUNCTION_INTEGRATION_SCHEMA');
                        }
                        if (new TextEncoder().encode(JSON.stringify(result)).length > b.maxBytes)
                            fail('FUNCTION_MODULE_LIMIT');
                        event({ kind: 'module-result', declaration: step.integration, module: b.module, transport: b.transport });
                    }
                    catch (e) {
                        const code = e instanceof FunctionFault ? e.code : String(e?.code ?? e?.message ?? 'FUNCTION_INTERNAL');
                        event({ kind: 'module-error', declaration: step.integration, module: b.module, transport: b.transport, code });
                        fail(/^[A-Z][A-Z0-9_]*$/.test(code) ? code : 'FUNCTION_INTERNAL');
                    }
                    continue;
                }
                let remote = false;
                let data = b.provided ? access(scope, b.provided.split('.')) : undefined;
                if (data === undefined) {
                    remote = true;
                    if (io.localOnly || b.transport === 'provided')
                        fail('FUNCTION_INTEGRATION_REQUIRED');
                    const prepared = prepareIntegrationRequest(b, scope, env);
                    const target = new URL(prepared.url), headers = prepared.headers;
                    io.observeRequest?.(prepared);
                    const controller = new AbortController();
                    const timer = setTimeout(() => controller.abort(), b.timeout);
                    try {
                        const response = await (io.fetch ?? fetch)(target, { method: 'GET', headers, redirect: 'error', signal: io.signal ? AbortSignal.any([io.signal, controller.signal]) : controller.signal });
                        if (!response.ok) {
                            await response.body?.cancel();
                            fail('FUNCTION_INTEGRATION_STATUS');
                        }
                        const text = await boundedText(response, b.maxBytes);
                        data = JSON.parse(text);
                    }
                    catch (error) {
                        if (controller.signal.aborted)
                            fail('FUNCTION_INTEGRATION_TIMEOUT');
                        if (error instanceof FunctionFault) {
                            if (error.code === 'FUNCTION_BODY_LIMIT')
                                fail('FUNCTION_INTEGRATION_LIMIT');
                            throw error;
                        }
                        fail('FUNCTION_INTEGRATION_FAILED');
                    }
                    finally {
                        clearTimeout(timer);
                    }
                }
                try {
                    scope[step.name] = validateSchema(model, b.output, data);
                }
                catch (e) {
                    if (remote)
                        fail('FUNCTION_INTEGRATION_SCHEMA');
                    throw e;
                }
            }
        }
        try {
            return output(compute(scope));
        }
        catch (error) {
            const code = error?.code;
            if (typeof code === 'string' && /^[A-Z][A-Z0-9_]*$/.test(code))
                fail(code);
            throw error;
        }
    }
    async function handler(request, env = {}, io = {}) {
        const ep = model.endpoint;
        const response = (body, status) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
        if (new URL(request.url).pathname !== ep.path)
            return response({ error: 'NOT_FOUND' }, 404);
        if (request.method !== ep.method)
            return response({ error: 'METHOD_NOT_ALLOWED' }, 405);
        const secret = env[ep.authEnv];
        if (!secret)
            return response({ error: 'FUNCTION_ENV_REQUIRED' }, 503);
        if (request.headers.get('authorization') !== `Bearer ${secret}`)
            return response({ error: 'UNAUTHORIZED' }, 401);
        if (request.headers.get('content-type')?.split(';')[0].trim() !== 'application/json')
            return response({ error: 'CONTENT_TYPE' }, 415);
        try {
            let body;
            try {
                body = JSON.parse(await boundedText(request, ep.maxBytes, ep.timeout));
            }
            catch (e) {
                if (e instanceof FunctionFault)
                    throw e;
                return response({ error: 'INVALID_JSON' }, 400);
            }
            const result = await invoke(body, env, { ...io, signal: io.signal ? AbortSignal.any([request.signal, io.signal]) : request.signal });
            const status = ep.statuses[result.status];
            if (!status)
                fail('FUNCTION_RESPONSE_STATUS');
            return response(result, status);
        }
        catch (e) {
            const code = e instanceof FunctionFault ? e.code : String(e?.message ?? '').match(/\bCALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)\b/)?.[0] ?? 'FUNCTION_INTERNAL';
            return response({ error: code }, ep.errors[code] ?? (code === 'FUNCTION_INTERNAL' ? 500 : ep.errorStatus));
        }
    }
    return { invoke, handler };
}
