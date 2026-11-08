/** Private finite-fixture transport, not an application serializer. */
export type CompositionCaseValue = readonly unknown[];
export class CompositionCaseValueUnavailable extends Error {
  constructor(reason: string) {super('COMPOSITION_CASE_VALUE_UNAVAILABLE:' + reason); this.name = 'CompositionCaseValueUnavailable';}
}
const fail = (reason: string): never => {throw new CompositionCaseValueUnavailable(reason);};
function budget() {
  let visits = 0, bytes = 0;
  return {step(depth: number) {if (++visits > 20000 || depth > 64) fail('shape capacity');}, text(s: string) {if ((bytes += Buffer.byteLength(s)) > 8388608) fail('byte capacity');}};
}
function entries(v: object, array: boolean): [string, unknown][] {
  const proto = Object.getPrototypeOf(v);
  if (array ? proto !== Array.prototype : proto !== Object.prototype && proto !== null) fail('custom prototype');
  const keys = Reflect.ownKeys(v);
  if (keys.some(k => typeof k !== 'string')) fail('symbol property');
  const length = array ? Object.getOwnPropertyDescriptor(v, 'length')?.value : 0;
  if (array ? !Number.isInteger(length) || length > 4096 || keys.length !== length + 1 : keys.length > 2048) fail('shape capacity');
  return (array ? Array.from({length}, (_, i) => String(i)) : keys as string[]).map(key => {
    const d = Object.getOwnPropertyDescriptor(v, key);
    if (!d || !Object.hasOwn(d, 'value') || !d.enumerable) fail('own enumerable data required');
    return [key, d!.value];
  });
}
export function encodeCompositionCaseValue(value: unknown): CompositionCaseValue {
  const b = budget(), active = new Set<object>();
  function visit(v: unknown, depth: number): CompositionCaseValue {
    b.step(depth);
    if (v === undefined) return Object.freeze(['undefined']);
    if (v === null) return Object.freeze(['null']);
    if (typeof v === 'boolean') return Object.freeze(['boolean', v]);
    if (typeof v === 'string') {b.text(v); return Object.freeze(['string', v]);}
    if (typeof v === 'bigint') {const s = String(v); b.text(s); return Object.freeze(['bigint', s]);}
    if (typeof v === 'number') {
      if (!Number.isFinite(v)) fail('non-finite number');
      return Object.freeze(['number', Object.is(v, -0) ? '-0' : String(v)]);
    }
    if (typeof v !== 'object') return fail('inert data required');
    if (active.has(v)) fail('cycle'); active.add(v);
    const array = Array.isArray(v), fields = entries(v, array).map(([k, x]) => {
      b.text(k); const out = visit(x, depth + 1); return array ? out : Object.freeze([k, out]);
    });
    active.delete(v);
    return Object.freeze([array ? 'array' : 'record', Object.freeze(fields)]);
  }
  return visit(value, 0);
}
export function decodeCompositionCaseValue(value: unknown): unknown {
  const b = budget(), active = new Set<object>();
  const array = (v: unknown): unknown[] => {
    if (!Array.isArray(v)) return fail('wire array required');
    return entries(v, true).map(([, x]) => x);
  };
  function visit(v: unknown, depth: number): unknown {
    b.step(depth);
    const tuple = array(v);
    if (active.has(v as object)) fail('cycle'); active.add(v as object);
    const [tag, payload] = tuple;
    const finish = (out: unknown) => {active.delete(v as object); return out;};
    if (tag === 'undefined' || tag === 'null') {
      if (tuple.length !== 1) fail('wire arity'); return finish(tag === 'null' ? null : undefined);
    }
    if (tuple.length !== 2) fail('wire arity');
    if (tag === 'boolean' && typeof payload === 'boolean') return finish(payload);
    if (tag === 'string' && typeof payload === 'string') {b.text(payload); return finish(payload);}
    if (tag === 'number' && typeof payload === 'string') {
      b.text(payload); const n = Number(payload);
      if (!Number.isFinite(n) || (Object.is(n, -0) ? '-0' : String(n)) !== payload) fail('canonical number');
      return finish(n);
    }
    if (tag === 'bigint' && typeof payload === 'string') {
      b.text(payload); if (!/^(?:0|-?[1-9][0-9]*)$/.test(payload)) fail('canonical bigint'); return finish(BigInt(payload));
    }
    if (tag === 'array') return finish(array(payload).map(x => visit(x, depth + 1)));
    if (tag === 'record') {
      const out = {}, rows = array(payload), seen = new Set<string>();
      if (rows.length > 2048) fail('record capacity');
      for (const row of rows) {
        const pair = array(row), [key, field] = pair;
        if (pair.length !== 2 || typeof key !== 'string' || seen.has(key)) fail('record field');
        seen.add(key as string); b.text(key as string);
        Object.defineProperty(out, key as string, {value: visit(field, depth + 1), enumerable: true, configurable: true, writable: true});
      }
      // JS enumerates integer keys canonically. Reject wire orders it cannot retain.
      if (JSON.stringify(Object.keys(out)) !== JSON.stringify([...seen])) fail('record field order');
      return finish(out);
    }
    return fail('wire tag or payload');
  }
  return visit(value, 0);
}
