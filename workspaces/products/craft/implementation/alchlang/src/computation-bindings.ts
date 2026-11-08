import { CompilationRejected } from "./model.js";

const MAX_DEPTH = 32;
const MAX_NODES = 262144;
const MAX_BYTES = 262144;

function reject(path: string, message: string): never {
  throw new CompilationRejected([{ code: "COMPUTATION_BINDING_DATA", path, message }]);
}

/** Descriptor-only admission; JavaScript reflection cannot exclude Proxy trap execution.
 * Detached null-prototype containers prevent inherited toJSON during later serialization.
 * Only this snapshot, never the caller's object, may be validated or serialized.
 */
export function snapshotComputationBindings(value: unknown): unknown {
  let nodes = 0;
  let bytes = 0;
  const active = new Set<object>();
  const charge = (size: number, path: string) => {
    bytes += size;
    if (bytes > MAX_BYTES) reject(path, "companion exceeds compact JSON byte cap");
  };
  const stringSize = (text: string, path: string): number => {
    // Reject before scanning/copying an unbounded key or string.
    if (text.length > MAX_BYTES - bytes) reject(path, "companion string exceeds byte cap");
    for (let i = 0; i < text.length; i++) {
      const code = text.charCodeAt(i);
      if (code >= 0xd800 && code <= 0xdbff) {
        const next = text.charCodeAt(++i);
        if (!(next >= 0xdc00 && next <= 0xdfff)) reject(path, "invalid Unicode surrogate");
      } else if (code >= 0xdc00 && code <= 0xdfff) reject(path, "invalid Unicode surrogate");
    }
    // Serialization of an admitted primitive cannot execute caller code.
    return Buffer.byteLength(JSON.stringify(text), "utf8");
  };
  const visit = (input: unknown, path: string, depth: number): unknown => {
    if (++nodes > MAX_NODES) reject(path, "companion traversal node cap exceeded");
    if (depth > MAX_DEPTH) reject(path, "companion nesting cap exceeded");
    if (input === null) { charge(4, path); return null; }
    if (typeof input === "string") { charge(stringSize(input, path), path); return input; }
    if (typeof input === "boolean") { charge(input ? 4 : 5, path); return input; }
    if (typeof input === "number") {
      if (!Number.isFinite(input)) reject(path, "finite JSON number required");
      charge(JSON.stringify(input).length, path); return input;
    }
    if (typeof input !== "object") reject(path, "ordinary JSON data required");
    if (active.has(input)) reject(path, "cyclic companion data");
    const array = Array.isArray(input);
    const prototype = Object.getPrototypeOf(input);
    if (array ? prototype !== Array.prototype : prototype !== Object.prototype && prototype !== null) reject(path, "unsupported companion prototype");
    let length = 0;
    if (array) {
      const descriptor = Object.getOwnPropertyDescriptor(input, "length");
      if (!descriptor || !("value" in descriptor) || !Number.isInteger(descriptor.value) || descriptor.value < 0) reject(path, "ordinary array length required");
      length = descriptor.value;
      if (length > MAX_NODES - nodes) reject(path, "companion traversal node cap exceeded");
    }
    const keys = Reflect.ownKeys(input);
    if (keys.length > MAX_NODES - nodes + (array ? 1 : 0)) reject(path, "companion member cap exceeded");
    if (array && keys.length !== length + 1) reject(path, "dense array without extra members required");
    charge(2, path);
    // Bound descriptor/member traversal before allocating or copying child data.
    active.add(input);
    const output: Record<string, unknown> | unknown[] = array ? [] : Object.create(null);
    if (array) Object.setPrototypeOf(output, null);
    let members = 0;
    for (const key of keys) {
      if (typeof key !== "string") reject(path, "symbol companion members are forbidden");
      if (array && key === "length") continue;
      // Array indices are not serialized keys; bound them independently of bytes.
      if (array && (key.length > 6 || !/^(0|[1-9][0-9]*)$/.test(key) || Number(key) >= length)) reject(path, "extra array member");
      // Charge/validate object keys before incorporating them into diagnostic paths.
      const keySize = array ? 0 : stringSize(key, path);
      const childPath = `${path}/${key.replaceAll("~", "~0").replaceAll("/", "~1")}`;
      const descriptor = Object.getOwnPropertyDescriptor(input, key);
      if (!descriptor || !("value" in descriptor)) reject(childPath, "accessor companion members are forbidden");
      if (!descriptor.enumerable) reject(childPath, "hidden companion members are forbidden");
      if (members++) charge(1, childPath);
      if (!array) charge(keySize + 1, childPath);
      const child = visit(descriptor.value, childPath, depth + 1);
      Object.defineProperty(output, key, { value: child, enumerable: true, writable: true, configurable: true });
    }
    active.delete(input);
    return Object.freeze(output);
  };
  const snapshot = visit(value, "$bindings", 1);
  // Verify the complete compact representation; pretty-print expansion is irrelevant.
  if (Buffer.byteLength(JSON.stringify(snapshot), "utf8") > MAX_BYTES) reject("$bindings", "companion exceeds compact JSON byte cap");
  return snapshot;
}
