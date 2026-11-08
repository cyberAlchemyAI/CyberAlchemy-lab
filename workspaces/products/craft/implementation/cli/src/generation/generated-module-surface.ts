/** Static surface inventory for our generated modules, not a TypeScript validator.
 * Unknown module syntax fails closed. Independent native compilation remains required.
 */
export interface NativeImport {
  readonly specifier: string;
  readonly names: readonly string[];
  readonly namespace: boolean;
  readonly type_only: boolean;
  readonly reexport: boolean;
}
export interface NativeExport {readonly name: string; readonly kind: 'type' | 'value';}
type Token = {text: string; literal: boolean};
const fail = (message: string): never => {throw new TypeError('DS_MODULE_SURFACE:' + message);};
const identifier = (s: string) => /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(s);

function tokens(source: string): Token[] {
  let i = 0;
  const scan = (interpolation = false, nesting = 0): Token[] => {
    if (nesting > 128) return fail('lexical nesting bound');
    const result: Token[] = []; let braces = 0;
    while (i < source.length) {
      const c = source[i]!;
      if (/\s/.test(c)) {i++; continue;}
      if (source.startsWith('//', i)) {const end = source.indexOf('\n', i); i = end < 0 ? source.length : end; continue;}
      if (source.startsWith('/*', i)) {const end = source.indexOf('*/', i + 2); if (end < 0) fail('unterminated comment'); i = end + 2; continue;}
      if (interpolation && c === '}' && braces === 0) {i++; return result;}
      if (c === '`') {
        i++; let closed = false;
        result.push({text: '<template>', literal: true});
        while (i < source.length) {
          const next = source[i++]!;
          if (next === '\\') {i++; continue;}
          if (next === '`') {closed = true; break;}
          if (next === '$' && source[i] === '{') {
            i++;
            const embedded = scan(true, nesting + 1);
            if (embedded.some(t => !t.literal && ['import', 'export', 'require'].includes(t.text))) fail('module expression in template');
          }
        }
        if (!closed) fail('unterminated template');
        continue;
      }
      if (c === '"' || c === "'") {
        let text = '', closed = false; i++;
        while (i < source.length) {
          const next = source[i++]!;
          if (next === c) {closed = true; break;}
          if (next === '\\') {text += next + (source[i++] ?? fail('unterminated escape')); continue;}
          if (next === '\n' || next === '\r') fail('newline in literal');
          text += next;
        }
        if (!closed) fail('unterminated literal');
        result.push({text, literal: true}); continue;
      }
      const previous = result.at(-1)?.text;
      if (c === '/' && (previous === undefined || ['=', '(', '[', '{', ',', ':', ';', '!', '?', 'return', '=>', '&&', '||'].includes(previous))) {
        let inClass = false, closed = false; i++;
        while (i < source.length) {
          const next = source[i++]!;
          if (next === '\\') {i++; continue;}
          if (next === '[') inClass = true;
          if (next === ']') inClass = false;
          if (next === '/' && !inClass) {closed = true; break;}
          if (next === '\n') fail('unterminated regexp');
        }
        if (!closed) fail('unterminated regexp');
        while (i < source.length && /[a-z]/i.test(source[i]!)) i++;
        result.push({text: '<regexp>', literal: true}); continue;
      }
      const word = /^[A-Za-z_$][A-Za-z0-9_$]*|^[0-9]+(?:\.[0-9]+)?n?/.exec(source.slice(i));
      if (word) {result.push({text: word[0], literal: false}); i += word[0].length; continue;}
      const pair = source.slice(i, i + 2);
      const text = ['=>', '&&', '||', '?.', '??'].includes(pair) ? pair : c;
      if (text === '{') braces++;
      if (text === '}') braces--;
      result.push({text, literal: false}); i += text.length;
    }
    if (interpolation) fail('unterminated interpolation');
    return result;
  };
  return scan();
}

export function inventoryGeneratedModule(source: string) {
  if (typeof source !== 'string' || Buffer.byteLength(source) > 16 * 1024 * 1024) fail('source bound');
  const ts = tokens(source), imports: NativeImport[] = [], exports: NativeExport[] = [], stack: string[] = [];
  const addExport = (name: string, type: boolean) => {
    if (!identifier(name)) fail('export identifier');
    const kind = type ? 'type' as const : 'value' as const;
    if (exports.some(e => e.name === name && e.kind === kind)) fail('duplicate export:' + name);
    exports.push({name, kind});
  };
  for (let i = 0; i < ts.length; i++) {
    const t = ts[i]!; if (t.literal) continue;
    if (t.text === 'import' && stack.length !== 0 && ts[i - 1]?.text !== '.') fail('nested module expression');
    if (t.text === 'require' && ts[i + 1]?.text === '(' && ts[i - 1]?.text !== '.') fail('unselected CommonJS dependency');
    if (stack.length === 0 && (t.text === 'import' || t.text === 'export')) {
      const exporting = t.text === 'export'; let j = i + 1, typeOnly = false;
      if (ts[j]?.text === 'type') {typeOnly = true; j++;}
      if (exporting && (typeOnly && ts[j]?.text !== '{' || ['const', 'function', 'interface', 'class', 'enum'].includes(ts[j]?.text ?? ''))) {
        const declaration = typeOnly ? 'type' : ts[j++]!.text;
        addExport(ts[j]?.text ?? '', declaration === 'type' || declaration === 'interface');
        continue;
      }
      const names: string[] = []; let namespace = false;
      if (!exporting && ts[j]?.text === '*' && ts[j + 1]?.text === 'as' && identifier(ts[j + 2]?.text ?? '')) {namespace = true; j += 3;}
      else if (ts[j]?.text === '{') {
        j++;
        while (ts[j]?.text !== '}') {
          let memberType = typeOnly;
          if (ts[j]?.text === 'type' && ts[j + 1]?.text !== ',' && ts[j + 1]?.text !== '}' && ts[j + 1]?.text !== 'as') {memberType = true; j++;}
          const name = ts[j++]?.text ?? ''; if (!identifier(name)) fail('named binding');
          names.push(name); let exported = name;
          if (ts[j]?.text === 'as') {j++; exported = ts[j++]?.text ?? ''; if (!identifier(exported)) fail('alias');}
          if (exporting) addExport(exported, memberType);
          if (ts[j]?.text === ',') j++; else if (ts[j]?.text !== '}') fail('binding separator');
        }
        j++;
      } else if (!exporting && ts[j]?.literal) {
        // A static side-effect import still participates in closure.
      } else fail('unsupported module declaration');
      const from = ts[j]?.text === 'from'; if (from) j++;
      if (!ts[j]?.literal) {
        if (exporting && !from) {i = j - 1; continue;}
        fail('static module specifier required');
      }
      const specifier = ts[j]!.text;
      if (!specifier || /[\\\r\n]/.test(specifier)) fail('literal module specifier');
      imports.push({specifier, names: names.sort(), namespace, type_only: typeOnly, reexport: exporting});
      i = j; continue;
    }
    if (['{', '[', '('].includes(t.text)) stack.push(t.text);
    if (['}', ']', ')'].includes(t.text)) {
      const expected = {'}': '{', ']': '[', ')': '('}[t.text];
      if (stack.pop() !== expected) fail('unbalanced source');
    }
  }
  if (stack.length) fail('unbalanced source');
  return {imports, exports: exports.sort((a, b) => a.name < b.name ? -1 : a.name > b.name ? 1 : a.kind < b.kind ? -1 : 1)};
}
