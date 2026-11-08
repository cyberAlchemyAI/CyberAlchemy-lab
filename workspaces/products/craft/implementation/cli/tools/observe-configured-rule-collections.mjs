import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

// Independent closed-profile observer. No generator import or source regeneration.
// Helper pins bind the already native-tested v3 support; predicate meaning still
// requires independent execution. Scope: RULE-COLLECTION-OBSERVATION.md.
const collectionHelperPins = new Set([
  '52b2b1c9a7409ed55e788061674b2c9d2ffde6425f2ece64ed5aca7b868bb163',
  'ba00455508c14fe1b8b419e296feef09c93dc80be13971211d58041318edd280',
]);
// Separately selected and independently pinned numeric boundary, not inferred from source.
const numericProfile = 'json-safe-uint64/v1-candidate';
const exactProfile = 'domainspec.typescript-exact-uint64/v1';
const exactHelperPins = new Set([
  'c1f6febd0158e4ddd099e397720f08d3d50887ac345e740e19e5d1e410e8d583',
  '29e32c34d93aa7c272e07838e1be14aefff53f609096617614878708b47860a5',
  'f7821d9fd29144af2698403c7b810056037ba00c481588e7dcc237420f8b45cb',
  '40e7cbdf695d2568e63cd299c74dc188cc82cf9aca5cbabee20647be488112f9',
]);
const numericHelperPins = new Set([
  'cbd6b26401ad66aec4af910cedf12679ee9b0f0665bc99db1fc4cd9f01e0589a',
  '434456e999b969cca200100d616cc4dff2764ac99a2072a677824c61ec691cf7',
  '4fa0e0a0fae1936fc48f849b76f09c10291639d7f83db292eb245b6f05a24a12',
]);
const digest = value => createHash('sha256').update(value).digest('hex');
const compilerRoot = '/opt/node-toolchain/node_modules/typescript';
const version = JSON.parse(fs.readFileSync(path.join(compilerRoot, 'package.json'), 'utf8')).version;
if (version !== '7.0.2') throw new Error('unselected native compiler');
const {API} = await import(pathToFileURL(path.join(compilerRoot, 'dist/api/sync/api.js')).href);
const {SyntaxKind: K} = await import(pathToFileURL(path.join(compilerRoot, 'dist/ast/index.js')).href);
const [configPath, expectedPath] = process.argv.slice(2);
const expected = JSON.parse(fs.readFileSync(expectedPath, 'utf8'));
const files = JSON.parse(fs.readFileSync(configPath, 'utf8')).files;
const errors = [], observations = [];
const text = node => node?.getText();
// Ignore formatting only outside literals; changing a key or diagnostic is not formatting.
const normalize = value => value?.replace(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\s+/g, token => /^["']/.test(token) ? token : '');
const compact = node => normalize(text(node));
const exported = node => node.modifiers?.some(m => m.kind === K.ExportKeyword);
const nativeType = (type, numeric=false, exact=false) => ({String:'string',Bool:'boolean','list<String>':'readonly string[]','set<String>':'readonly string[]','list<Bool>':'readonly boolean[]','set<Bool>':'readonly boolean[]',...(numeric?{UInt64:exact?'RuleUInt64Input':'number','list<UInt64>':exact?'readonly RuleUInt64Input[]':'readonly number[]','set<UInt64>':exact?'readonly RuleUInt64Input[]':'readonly number[]'}:{})})[type];
if (!Array.isArray(expected) || !Array.isArray(files)) throw new Error('invalid observation input');
if (JSON.stringify([...files].sort()) !== JSON.stringify(expected.map(e => e.path).sort()) || new Set(files).size !== files.length) errors.push('artifact-set');
for (const e of expected) {
  const exact = e?.value_profile === exactProfile, numeric = exact || e?.value_profile === numericProfile;
  if (!e || Object.keys(e).sort().join('|') !== 'callable|imports|parameters|path'+(numeric?'|value_profile':'') || !Array.isArray(e.parameters) || !Array.isArray(e.imports) ||
      e.parameters.some(p => !p || Object.keys(p).sort().join('|') !== 'name|type' || !/^[a-z][a-z0-9_]*$/.test(p.name) || !nativeType(p.type,numeric,exact)) ||
      new Set(e.parameters.map(p => p.name)).size !== e.parameters.length) throw new Error('invalid bound declarations');
}
const api = new API({cwd:path.dirname(configPath)});
try {
  const snapshot = api.updateSnapshot({openProjects:[configPath]});
  const project = snapshot.getProject(configPath);
  if (!project) throw new Error('native project missing');
  for (const e of expected) {
    const exact = e.value_profile === exactProfile, numeric = exact || e.value_profile === numericProfile;
    const helperPins = exact ? exactHelperPins : numeric ? numericHelperPins : collectionHelperPins;
    const reject = reason => errors.push(reason + ':' + e.path);
    if (path.posix.normalize(e.path) !== e.path || path.isAbsolute(e.path) || e.path.split('/').includes('..') ||
        !/^[a-z][a-z0-9/-]*\/features\/[a-z][a-z0-9-]*\/src\/domain\/rules\/[a-z][a-z0-9-]*\.ts$/.test(e.path)) {reject('profile-path');continue;}
    const file = path.resolve(path.dirname(configPath),e.path), source = project.program.getSourceFile(file);
    if (!source) {reject('missing-source');continue;}
    for (const diagnostic of project.program.getSyntacticDiagnostics(file)) reject('syntax-' + diagnostic.code);
    const imports = [], exports = [], seenHelpers = new Set();
    let arrow;
    for (const statement of source.statements) {
      if (statement.kind === K.ImportDeclaration) {
        const clause = statement.importClause;
        if (!clause?.namedBindings?.elements || clause.name || clause.isTypeOnly || statement.attributes) reject('import-form');
        for (const item of clause?.namedBindings?.elements ?? []) imports.push({path:statement.moduleSpecifier.text,symbol:text(item.propertyName ?? item.name),local:text(item.name)});
      } else if (statement.kind === K.VariableStatement && exported(statement)) {
        if (statement.declarationList.flags !== 2) reject('export-not-const');
        for (const declaration of statement.declarationList.declarations) {
          exports.push(text(declaration.name));arrow = declaration.initializer;
          if (arrow?.kind !== K.ArrowFunction || arrow.type?.kind !== K.BooleanKeyword || arrow.modifiers?.length) reject('boolean-arrow');
        }
      } else {
        const hash = digest(text(statement));
        if (!helperPins.has(hash) || seenHelpers.has(hash)) reject('helper-binding');
        seenHelpers.add(hash);
      }
    }
    if (seenHelpers.size !== helperPins.size || [...helperPins].some(hash => !seenHelpers.has(hash))) reject('helper-set');
    if (JSON.stringify(exports) !== JSON.stringify([e.callable])) reject('export-set');
    if (JSON.stringify(imports) !== JSON.stringify(e.imports)) reject('import-binding');
    for (const i of imports) {
      const target = path.posix.normalize(path.posix.join(path.posix.dirname(e.path),i.path)).replace(/\.js$/,'.ts');
      if (!i.path.startsWith('.') || !i.path.endsWith('.js') || !expected.some(row => row.path === target && row.callable === i.symbol)) reject('leaf-import');
    }
    if (!arrow || arrow.kind !== K.ArrowFunction || arrow.body?.kind !== K.Block) {reject('rule-body');continue;}
    const signature = `Readonly<{${e.parameters.map(p => `readonly ${JSON.stringify(p.name)}:${nativeType(p.type,numeric,exact)}`).join(';')}}>`;
    if (arrow.parameters.length !== 1 || text(arrow.parameters[0].name) !== 'parameters' || arrow.parameters[0].initializer || arrow.parameters[0].dotDotDotToken ||
        compact(arrow.parameters[0].type) !== normalize(signature)) reject('parameter-contract');
    const statements = arrow.body.statements;
    if (statements.length !== e.parameters.length + 4) reject('boundary-shape');
    if (compact(statements[0]) !== "if(parameters===null||typeofparameters!=='object'||Array.isArray(parameters))thrownewTypeError('RULE_INPUT');") reject('object-boundary');
    if (compact(statements[1]) !== 'constdescriptors=Object.getOwnPropertyDescriptors(parameters);') reject('descriptor-boundary');
    const checks = e.parameters.map(p => ['String','Bool'].includes(p.type) ?
      `typeofdescriptors[${JSON.stringify(p.name)}]?.value!==${JSON.stringify(nativeType(p.type))}` :
      `!Object.hasOwn(descriptors[${JSON.stringify(p.name)}]??{},'value')||descriptors[${JSON.stringify(p.name)}]?.enumerable!==true`);
    const boundary = `if(Reflect.ownKeys(parameters).length!==${e.parameters.length}${checks.length?'||'+checks.join('||'):''})thrownewTypeError('RULE_INPUT');`;
    if (compact(statements[2]) !== boundary) reject('field-boundary');
    const scope = new Set();
    for (const [index,p] of e.parameters.entries()) {
      const name = `p${index}`,type = nativeType(p.type,numeric,exact),scalar = ['String','Bool'].includes(p.type);
      const element = p.type.endsWith('<Bool>') ? 'boolean' : p.type.endsWith('<UInt64>') ? exact ? 'bigint' : 'number' : 'string';
      const initializer = p.type === 'UInt64' ? `normalizeRuleUInt64(descriptors[${JSON.stringify(p.name)}]!.value)` : scalar ? `descriptors[${JSON.stringify(p.name)}]!.valueas${type}` :
        `normalizeRuleCollection<${element}>(descriptors[${JSON.stringify(p.name)}]!.value,${JSON.stringify(element)},${p.type.startsWith('set<')})`;
      if (compact(statements[index+3]) !== `const${name}=${initializer};`) reject('parameter-normalization');
      scope.add(name);
    }
    const unwrap = node => node?.kind === K.ParenthesizedExpression ? unwrap(node.expression) : node;
    const operators = new Set([K.EqualsEqualsEqualsToken,K.ExclamationEqualsEqualsToken,K.LessThanToken,K.GreaterThanToken,K.LessThanEqualsToken,K.GreaterThanEqualsToken,K.AmpersandAmpersandToken,K.BarBarToken]);
    const callback = (node, outer) => {
      if (node.kind !== K.ArrowFunction || node.modifiers?.length || node.body.kind === K.Block) {reject('callback-form');return;}
      const nested = new Set(outer);
      for (const parameter of node.parameters) {
        const name = text(parameter.name);
        if (!/^q\d+$/.test(name) || nested.has(name) || parameter.initializer || parameter.dotDotDotToken) reject('callback-binding');
        nested.add(name);
      }
      expression(node.body,nested);
    };
    const expression = (raw, active) => {
      const node = unwrap(raw);
      if (!node) {reject('missing-expression');return;}
      if (node.kind === K.Identifier) {if (!active.has(text(node))) reject('unbound-value');return;}
      if ([K.StringLiteral,K.NumericLiteral,K.TrueKeyword,K.FalseKeyword].includes(node.kind)) return;
      if (exact && node.kind === K.BigIntLiteral) return;
      if (node.kind === K.BinaryExpression && operators.has(node.operatorToken.kind)) {expression(node.left,active);expression(node.right,active);return;}
      if (node.kind === K.PrefixUnaryExpression && node.operator === K.ExclamationToken) {expression(node.operand,active);return;}
      if (node.kind === K.PropertyAccessExpression && ['length','size'].includes(text(node.name))) {expression(node.expression,active);return;}
      if (node.kind === K.ElementAccessExpression) {expression(node.expression,active);expression(node.argumentExpression,active);return;}
      if (node.kind === K.NewExpression && text(node.expression) === 'Set' && node.arguments?.length === 1) {expression(node.arguments[0],active);return;}
      if (node.kind === K.ArrayLiteralExpression) {for (const item of node.elements) expression(item.kind === K.SpreadElement ? item.expression : item,active);return;}
      if (node.kind === K.CallExpression) {
        const callee = unwrap(node.expression);
        if (callee?.kind === K.ArrowFunction) {callback(callee,active);node.arguments.forEach(arg => expression(arg,active));return;}
        if (callee?.kind === K.Identifier && e.imports.some(i => i.local === text(callee))) {
          if (node.arguments.length !== 1 || node.arguments[0].kind !== K.ObjectLiteralExpression) {reject('rule-call-shape');return;}
          for (const property of node.arguments[0].properties) {
            if (property.kind !== K.PropertyAssignment || property.name.kind !== K.ComputedPropertyName || property.name.expression.kind !== K.StringLiteral) reject('rule-argument-shape');
            else expression(property.initializer,active);
          }
          return;
        }
        if (callee?.kind === K.Identifier && text(callee) === 'normalizeRuleCollection') {
          if (node.arguments.length !== 3 || !['string','boolean',...(numeric?[exact?'bigint':'number']:[])].includes(node.arguments[1]?.text) || node.arguments[2]?.kind !== K.TrueKeyword) reject('conversion-shape');
          expression(node.arguments[0],active);return;
        }
        if (callee?.kind === K.PropertyAccessExpression && ['some','every','filter','map'].includes(text(callee.name))) {
          expression(callee.expression,active);
          if (node.arguments.length !== 1) reject('callback-arity');
          if (node.arguments[0]) callback(node.arguments[0],active);
          return;
        }
        reject('undeclared-call');return;
      }
      reject('unsupported-expression');
    };
    const returned = statements.at(-1);
    if (returned?.kind !== K.ReturnStatement) reject('return-path');
    else expression(returned.expression,scope);
    observations.push({path:e.path,exports,imports,parameters:e.parameters,helper_digests:[...seenHelpers].sort(),source_sha256:digest(text(source))});
  }
  snapshot.dispose();
} finally {api.close();}
console.log(JSON.stringify({schema_version:'domainspec.configured-rule-collection-observation/v1-candidate',result:errors.length?'fail':'pass',typescript:version,errors,observations,semantic_verdict:'requires-independent-execution',authority_effect:'none'}));
if (errors.length) process.exitCode = 1;
