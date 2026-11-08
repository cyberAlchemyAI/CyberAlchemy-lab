import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

// Independent, bounded native AST observation. Open questions: RULE-GENERATION.md.
// This runs only inside the existing selected Node/TypeScript toolchain image.
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
const exported = node => node.modifiers?.some(m => m.kind === K.ExportKeyword);
if (JSON.stringify([...files].sort()) !== JSON.stringify(expected.map(e => e.path).sort()) || new Set(files).size !== files.length) errors.push('artifact-set');
const api = new API({cwd: path.dirname(configPath)});
try {
  const snapshot = api.updateSnapshot({openProjects: [configPath]});
  const project = snapshot.getProject(configPath);
  if (!project) throw new Error('native project missing');
  for (const e of expected) {
    const file = path.resolve(path.dirname(configPath), e.path);
    const source = project.program.getSourceFile(file);
    if (!source) { errors.push('missing-source:' + e.path); continue; }
    for (const d of project.program.getSyntacticDiagnostics(file)) errors.push('syntax:' + d.code);
    if (!/\/features\/[a-z][a-z0-9-]*\/src\/domain\/rules\/[a-z][a-z0-9-]*\.ts$/.test(e.path)) errors.push('profile-path:' + e.path);
    const imports = [], exports = [];
    let arrow;
    for (const statement of source.statements) {
      if (statement.kind === K.ImportDeclaration) {
        const clause = statement.importClause;
        if (!clause?.namedBindings?.elements || clause.name || clause.isTypeOnly) errors.push('import-form:' + e.path);
        for (const element of clause?.namedBindings?.elements ?? []) imports.push({path: statement.moduleSpecifier.text, symbol: text(element.propertyName ?? element.name), local: text(element.name)});
      } else if (statement.kind === K.VariableStatement && exported(statement)) {
        for (const declaration of statement.declarationList.declarations) {
          exports.push(text(declaration.name)); arrow = declaration.initializer;
          if (arrow?.kind !== K.ArrowFunction || arrow.type?.kind !== K.BooleanKeyword) errors.push('boolean-arrow:' + e.path);
        }
      } else errors.push('extra-top-level:' + e.path);
    }
    if (JSON.stringify(exports) !== JSON.stringify([e.callable])) errors.push('export-set:' + e.path);
    if (JSON.stringify(imports) !== JSON.stringify(e.imports)) errors.push('import-binding:' + e.path);
    for (const i of imports) {
      const target = path.posix.normalize(path.posix.join(path.posix.dirname(e.path), i.path)).replace(/\.js$/, '.ts');
      if (!i.path.endsWith('.js') || !i.path.startsWith('.') || !expected.some(row => row.path === target)) errors.push('leaf-import:' + e.path);
    }
    const allowedCalls = new Set(['Array.isArray', 'Object.getOwnPropertyDescriptors', 'Reflect.ownKeys', ...e.imports.map(i => i.local)]);
    let returns = 0;
    const visit = node => {
      if ([K.ClassDeclaration, K.ClassExpression, K.FunctionDeclaration, K.FunctionExpression, K.SwitchStatement, K.ForStatement, K.WhileStatement].includes(node.kind)) errors.push('unsupported-executable-form:' + e.path);
      if (node.kind === K.CallExpression && !allowedCalls.has(text(node.expression))) errors.push('undeclared-call:' + e.path);
      if (node.kind === K.NewExpression && text(node.expression) !== 'TypeError') errors.push('construction:' + e.path);
      if (node.kind === K.BinaryExpression && [K.EqualsToken, K.PlusEqualsToken, K.MinusEqualsToken].includes(node.operatorToken.kind)) errors.push('assignment:' + e.path);
      if (node.kind === K.ReturnStatement) returns++;
      node.forEachChild(visit);
    };
    visit(source);
    if (returns !== 1 || arrow?.body?.statements?.at(-1)?.kind !== K.ReturnStatement) errors.push('return-path:' + e.path);
    observations.push({path: e.path, exports, imports, returns});
  }
  snapshot.dispose();
} finally { api.close(); }
console.log(JSON.stringify({schema_version: 'domainspec.configured-rule-observation/v1-candidate', result: errors.length ? 'fail' : 'pass', typescript: version, errors, observations, authority_effect: 'none'}));
if (errors.length) process.exitCode = 1;
