import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

// Independent bounded native AST observation, not generator-provided expectations.
// Scope and open questions: ENUM-GENERATION.md. Run in the selected toolchain image.
const compilerRoot = '/opt/node-toolchain/node_modules/typescript';
const version = JSON.parse(fs.readFileSync(path.join(compilerRoot, 'package.json'), 'utf8')).version;
if (version !== '7.0.2') throw new Error('unselected native compiler');
const {API} = await import(pathToFileURL(path.join(compilerRoot, 'dist/api/sync/api.js')).href);
const {SyntaxKind: K} = await import(pathToFileURL(path.join(compilerRoot, 'dist/ast/index.js')).href);
const [configPath, expectedPath] = process.argv.slice(2);
const expected = JSON.parse(fs.readFileSync(expectedPath, 'utf8'));
const files = JSON.parse(fs.readFileSync(configPath, 'utf8')).files;
const errors = [], observations = [];
const text = n => n?.getText();
const exported = n => n.modifiers?.length === 1 && n.modifiers[0].kind === K.ExportKeyword;
const wanted = [...expected.modules.map(e => e.path), expected.provider.path].sort();
if (JSON.stringify([...files].sort()) !== JSON.stringify(wanted) || new Set(files).size !== files.length) errors.push('artifact-set');
const root = path.dirname(configPath);
const provider = fs.readFileSync(path.resolve(root, expected.provider.path));
if (createHash('sha256').update(provider).digest('hex') !== expected.provider.sha256) errors.push('provider-digest');
const api = new API({cwd: root});
try {
  const snapshot = api.updateSnapshot({openProjects: [configPath]});
  const project = snapshot.getProject(configPath);
  if (!project) throw new Error('native project missing');
  for (const e of expected.modules) {
    const file = path.resolve(root, e.path), source = project.program.getSourceFile(file);
    if (!source) {errors.push('missing-source:' + e.path); continue;}
    for (const d of project.program.getSyntacticDiagnostics(file)) errors.push('syntax:' + d.code);
    if (!/\/features\/[a-z][a-z0-9-]*\/src\/domain\/enums\/[a-z][a-z0-9-]*\.ts$/.test(e.path)) errors.push('profile-path:' + e.path);
    const imports = [], exports = [], members = [];
    for (const s of source.statements) {
      if (s.kind === K.ImportDeclaration) {
        const clause = s.importClause;
        if (clause?.name || clause?.namedBindings?.elements?.length !== 1) errors.push('import-form:' + e.path);
        const element = clause?.namedBindings?.elements?.[0];
        if (element?.propertyName || element?.isTypeOnly) errors.push('import-form:' + e.path);
        imports.push({path: s.moduleSpecifier.text, symbol: text(element?.name), type_only: !!clause?.isTypeOnly});
      } else if (s.kind === K.VariableStatement && exported(s)) {
        if (!text(s.declarationList)?.startsWith('const ') || s.declarationList.declarations.length !== 1) errors.push('const-form:' + e.path);
        for (const d of s.declarationList.declarations) {
          exports.push('value:' + text(d.name));
          const call = d.initializer;
          if (d.type || call?.kind !== K.CallExpression || text(call.expression) !== 'defineEnum' || call.arguments?.length !== 1 || call.typeArguments?.length) {errors.push('owned-call:' + e.path); continue;}
          const argument = call.arguments[0];
          if (argument.kind !== K.AsExpression || text(argument.type) !== 'const' || argument.expression.kind !== K.ObjectLiteralExpression) {errors.push('member-object:' + e.path); continue;}
          for (const p of argument.expression.properties) {
            if (p.kind !== K.PropertyAssignment || p.name?.kind !== K.StringLiteral || p.initializer?.kind !== K.StringLiteral) errors.push('static-member:' + e.path);
            members.push({name: p.name?.text, wire_value: p.initializer?.text});
          }
        }
      } else if (s.kind === K.TypeAliasDeclaration && exported(s)) {
        exports.push('type:' + text(s.name));
        if (s.typeParameters?.length || s.type.kind !== K.TypeReference || text(s.type).replace(/\s+/g, ' ') !== `EnumValue<typeof ${e.symbol}>`) errors.push('value-type:' + e.path);
      } else errors.push('extra-top-level:' + e.path);
    }
    if (JSON.stringify(exports) !== JSON.stringify(['value:' + e.symbol, 'type:' + e.symbol])) errors.push('export-set:' + e.path);
    if (JSON.stringify(members) !== JSON.stringify(e.members.map(name => ({name, wire_value: name})))) errors.push('member-set:' + e.path);
    if (JSON.stringify(imports) !== JSON.stringify([{path: e.provider_import, symbol: 'defineEnum', type_only: false}, {path: e.provider_import, symbol: 'EnumValue', type_only: true}])) errors.push('import-binding:' + e.path);
    if (path.posix.normalize(path.posix.join(path.posix.dirname(e.path), e.provider_import)).replace(/\.js$/, '.ts') !== expected.provider.path) errors.push('provider-target:' + e.path);
    observations.push({path: e.path, exports, members});
  }
  snapshot.dispose();
} finally {api.close();}
console.log(JSON.stringify({schema_version: 'domainspec.configured-enum-observation/v1-candidate', result: errors.length ? 'fail' : 'pass', typescript: version, errors, observations, authority_effect: 'none'}));
if (errors.length) process.exitCode = 1;
