/** Static inventory of the generated Python subset, not a Python validator or
 * sandbox. It never imports code or starts a native process. Native AST/import
 * qualification remains separate. Strings/comments cannot manufacture imports.
 */
export interface PythonImport {
  readonly specifier: string;
  readonly names: readonly Readonly<{name: string; local: string}>[];
  readonly namespace: boolean;
}
type Token = {text: string; literal: boolean};
const fail = (message: string): never => {throw new TypeError('DS_PYTHON_MODULE_SURFACE:' + message);};
const identifier = (s: string) => /^[A-Za-z_][A-Za-z0-9_]*$/.test(s);

function statements(source: string) {
  const result: {tokens: Token[]; indented: boolean}[] = [];
  let i = 0, lineStart = true, indented = false, row: Token[] = [];
  const brackets: string[] = [];
  const finish = () => {if (row.length) result.push({tokens: row, indented}); row = [];};
  while (i < source.length) {
    const c = source[i]!;
    if (lineStart) {
      let spaces = 0;
      while (source[i] === ' ') {i++; spaces++;}
      if (source[i] === '\t' || source[i] === '\f') fail('unsupported indentation');
      if (!row.length) indented = spaces > 0;
      lineStart = false; continue;
    }
    if (c === '\n') {i++; if (!brackets.length) finish(); lineStart = true; continue;}
    if (c === ' ' || c === '\r' || c === '\t') {i++; continue;}
    if (c === '#') {while (i < source.length && source[i] !== '\n') i++; continue;}
    if (c === '\\') fail('explicit line continuation is outside generated subset');
    const string = /^(?:[rRuUbB]|[rR][bB]|[bB][rR])?(['"])/.exec(source.slice(i));
    if (string) {
      const quote = string[1]!, prefix = string[0].length - 1;
      i += prefix;
      const delimiter = source.startsWith(quote.repeat(3), i) ? quote.repeat(3) : quote;
      i += delimiter.length; let closed = false;
      while (i < source.length) {
        if (source.startsWith(delimiter, i)) {i += delimiter.length; closed = true; break;}
        if (source[i] === '\\') {i += 2; continue;}
        if (source[i] === '\n' && delimiter.length === 1) fail('newline in literal');
        i++;
      }
      if (!closed) fail('unterminated literal');
      row.push({text: '<string>', literal: true}); continue;
    }
    const word = /^[A-Za-z_][A-Za-z0-9_]*/.exec(source.slice(i));
    if (word) {
      const text = word[0]; i += text.length;
      if ((source[i] === '"' || source[i] === "'") && /^[rRuUbBfFtT]+$/.test(text)) fail('unsupported interpolated literal');
      row.push({text, literal: false}); continue;
    }
    if (c === ';') fail('semicolon statement is outside generated subset');
    if ('([{'.includes(c)) {brackets.push(c); if (brackets.length > 128) fail('nesting bound');}
    if (')]}'.includes(c) && brackets.pop() !== ({')': '(', ']': '[', '}': '{'} as Record<string, string>)[c]) {
      fail('unbalanced delimiter');
    }
    row.push({text: c, literal: false}); i++;
  }
  if (brackets.length) fail('unclosed delimiter');
  finish(); return result;
}

export function inventoryPythonModule(source: string) {
  if (typeof source !== 'string' || Buffer.byteLength(source) > 16 * 1024 * 1024 || source.includes('\0')) fail('source bound');
  const imports: PythonImport[] = [], bindings = new Set<string>();
  for (const row of statements(source)) {
    const tokens = row.tokens, ts = tokens.map(t => t.literal ? '<string>' : t.text);
    for (let n = 0; n < ts.length; n++) {
      if (['__import__', 'exec', 'eval'].includes(ts[n]!) && ts[n + 1] === '(') fail('dynamic module execution');
      if (['import', 'from'].includes(ts[n]!) && (ts[0] === 'import' || ts[0] === 'from')) continue;
      if (ts[n] === 'import') fail('nested or noncanonical import');
    }
    if (ts[0] === 'import' || ts[0] === 'from') {
      if (row.indented) fail('nested import');
      const namespace = ts[0] === 'import';
      const split = namespace ? 1 : ts.indexOf('import');
      if (split < 2 && !namespace) fail('from import syntax');
      const specifier = namespace ? '' : ts.slice(1, split).join('');
      if (!namespace && !/^(?:\.+(?:[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)?|[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)$/.test(specifier)) fail('module specifier');
      const values = ts.slice(namespace ? 1 : split + 1), entries: {name: string; local: string}[] = [];
      for (let n = 0; n < values.length;) {
        let name = values[n++] ?? fail('import name');
        if (!identifier(name)) fail('import name');
        while (namespace && values[n] === '.') {n++; const part = values[n++] ?? ''; if (!identifier(part)) fail('module name'); name += '.' + part;}
        let local = namespace ? name.split('.')[0]! : name;
        if (values[n] === 'as') {n++; local = values[n++] ?? ''; if (!identifier(local)) fail('import alias');}
        entries.push({name, local}); bindings.add(local);
        if (n < values.length && values[n++] !== ',') fail('import separator');
        if (n === values.length && values[n - 1] === ',') fail('trailing import comma');
      }
      if (!entries.length) fail('empty import');
      if (namespace) for (const entry of entries) imports.push({specifier: entry.name, names: [entry], namespace: true});
      else imports.push({specifier, names: entries, namespace: false});
      continue;
    }
    if (row.indented) continue;
    const declaration = ts[0] === 'async' ? 1 : 0;
    if (['def', 'class'].includes(ts[declaration] ?? '')) {
      const name = ts[declaration + 1] ?? ''; if (!identifier(name)) fail('declaration name'); bindings.add(name);
    } else if (identifier(ts[0] ?? '') && (ts[1] === '=' && ts[2] !== '=' || ts[1] === ':' && ts.some((t, i) => t === '=' && ts[i - 1] !== '=' && ts[i + 1] !== '='))) bindings.add(ts[0]!);
    else if (ts.includes('=')) {
      const end = ts.indexOf('='), left = ts.slice(0, end);
      if (left.length >= 3 && left.length % 2 === 1 && left.every((s, i) => i % 2 === 0 ? identifier(s) : s === ',')) for (let i = 0; i < left.length; i += 2) bindings.add(left[i]!);
    }
  }
  return {imports, bindings: [...bindings].sort()};
}
