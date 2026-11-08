import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';

// Native structural oracle for the bounded factory slice; behavior is tested separately.
// Scope and open questions: FACTORY-GENERATION.md. Expectations are test-authored.
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
const compact = n => text(n)?.replace(/\s+/g, '');
const exported = n => n.modifiers?.some(m => m.kind === K.ExportKeyword);
const unwrap = n => n?.kind === K.CallExpression && text(n.expression) === 'Object.freeze' && n.arguments.length === 1 ? n.arguments[0] : undefined;
const property = (n, name) => n?.properties?.find(p => text(p.name) === name)?.initializer;
const assertion = n => n?.kind === K.AsExpression ? n.expression : n;
const approvedSupportHashes = Object.freeze({
  ValueProtocol:['8ccfafcc6944bb989f375c0b75775c1201ea2307babf7895b86826de945ff141'],
  stringValue:['09c78b4a2a60a53f5c25ebfeb5e5958caa994f40f5661609bc657f9c6cee2477'],
  boolValue:['c0ed60782365ed76d9668d859e76b18d47fa26411889f1c8fc12636c7abb1083'],
  ownedValue:['151b5b61ed2d3c02fbeaf049e915d9329b4fae77808007b47154d0f33c30e3ce'],
  optionalValue:['53d79918b42630d35ff5ea6cff2e45313b1c9f44c9c584e191ac57fd2da41a6b'],
  sequenceValue:['9281e0f77595b70527e4092056229d7c51b0d6ae401ffbb76547a87269efb2b4'],
  listValue:['2812b00ad7cc693f07b36b4d61f474983520124b5d73a79f7a388e18ef00ad04'],
  setValue:['538e3ea3576adcbede53287dda85d99761eac358790c9a6390e2667c716f199a'],
  SumPayloadProtocol:['b898368bba3818c278b04322fe3a127421012b493b726d13f81a28a831833a04'],
  SumCaseOf:['1753b7d741cc4b2e0d78c565d6e3cc1913812eb30c64418a175f8f92a2d04ab3'],
  sumValue:['e6d0deb434144763a5056d5f58fe2f55dbc6e09ea144829acea5eb11aa79a6fb'],
  ownedSumValue:['d5dfb3a3255ec053f56d8bfa58c790b2e662088c30f690818134b81e5643abbb'],
  ownedEntityValue:['0b060059226cda3ebb913a323c796d533d14837472e1a10abcf983fce4f6546a'],
  enumValue:['0e5f0116ed43997b5967c990bcfa3c9a41904206d1aed81d019c168d6c997234'],
  uint64Value:['6345f2163e510e1c489182c7ff6909d64c87647b2654da5244622e5793dffa9c','06347d530a1116421e9b4b0c7408ad2263287a912acaa868f59488f7a6cbb1d7'],
});
const statementName = statement => text(statement.name) ?? (statement.declarationList?.declarations?.length === 1 ? text(statement.declarationList.declarations[0].name) : undefined);
const verifySupport = (source, endName, required, error) => {
  const end = source.statements.find(statement => statementName(statement) === endName)?.getStart();
  if (end === undefined) {errors.push(error); return;}
  const support = new Map(source.statements.filter(statement => statement.getStart() < end).map(statement => [statementName(statement), statement]));
  for (const name of required) {
    const statement = support.get(name), approved = approvedSupportHashes[name];
    if (!statement || approved && !approved.includes(createHash('sha256').update(statement.getText()).digest('hex'))) {errors.push(error); return;}
  }
};
if (JSON.stringify([...files].sort()) !== JSON.stringify([...expected.files].sort())) errors.push('artifact-set');
const api = new API({cwd: path.dirname(configPath)});
try {
  const snapshot = api.updateSnapshot({openProjects: [configPath]});
  const project = snapshot.getProject(configPath);
  if (!project) throw new Error('native project missing');
  for (const e of expected.modules) {
    const file = path.resolve(path.dirname(configPath), e.path), source = project.program.getSourceFile(file);
    if (!source) {errors.push('missing-source:' + e.path); continue;}
    for (const d of project.program.getSyntacticDiagnostics(file)) errors.push('syntax:' + d.code);
    const imports = [], exports = [], variables = new Map();
    for (const s of source.statements) {
      if (s.kind === K.ImportDeclaration) {
        if ((!e.composed && s.importClause?.isTypeOnly) || s.importClause?.name || s.importClause?.namedBindings?.elements?.length !== 1) errors.push('import-form:' + e.path);
        for (const i of s.importClause?.namedBindings?.elements ?? []) imports.push({path: s.moduleSpecifier.text, symbol: text(i.propertyName ?? i.name), local: text(i.name), ...(s.importClause?.isTypeOnly ? {type_only:true} : {})});
      } else if (s.kind === K.VariableStatement) {
        if (!text(s.declarationList).startsWith('const ')) errors.push('mutable-declaration:' + e.path);
        for (const d of s.declarationList.declarations) {
          const name = text(d.name);
          if (variables.has(name)) errors.push('duplicate-symbol:' + e.path);
          variables.set(name, d.initializer);
          if (exported(s)) {
            exports.push(name);
            if (e.reference_bindings && name === e.name + 'FieldBindings') {
              const array=assertion(unwrap(d.initializer));
              if(array?.kind!==K.ArrayLiteralExpression)errors.push('reference-form:'+e.path);
              const actual=array?.elements?.map(element=>{
                const row=assertion(unwrap(element)),projection=assertion(unwrap(property(row,'projection')));
                if(row?.kind!==K.ObjectLiteralExpression || row.properties.length!==5 || projection?.kind!==K.ArrayLiteralExpression)errors.push('reference-form:'+e.path);
                return {owner:property(row,'owner')?.text,field:property(row,'field')?.text,kind:property(row,'kind')?.text,
                  target:property(row,'target')?.text,projection:projection?.elements?.map(p=>p.text)};
              });
              if(JSON.stringify(actual)!==JSON.stringify(e.reference_bindings))errors.push('reference-binding:'+e.path);
            } else if (e.provider && name === e.name + 'ValueComponent') {
              const provider = unwrap(d.initializer);
              if (provider?.kind !== K.ObjectLiteralExpression || provider.properties.length !== 6 || compact(property(provider, 'isOwned')) !== 'owned' || property(provider, 'concept')?.text !== e.provider || !/^[a-f0-9]{64}$/.test(property(provider, 'contract_sha256')?.text)) errors.push('provider-form:' + e.path);
              if(e.entity_provider && (assertion(property(provider,'protocol_id'))?.text!=='typescript.owned-entity-component/v1-candidate' ||
                compact(property(provider,'key'))!=="(value:unknown):string=>{if(!owned(value))thrownewTypeError('UNOWNED_COMPONENT');returnsnapshots.get(value)!.key;}" ||
                compact(property(provider,'equals'))!=="(left:unknown,right:unknown):boolean=>owned(left)&&owned(right)&&snapshots.get(left)!.key===snapshots.get(right)!.key"))errors.push('entity-provider:'+e.path);
            } else if (d.initializer?.kind !== K.ArrowFunction || d.initializer.parameters.length || compact(d.initializer.body) !== 'makeFactory(Object.freeze([]),baseValidators)') errors.push('factory-entry:' + e.path);
          }
        }
      } else if ([K.InterfaceDeclaration, K.TypeAliasDeclaration].includes(s.kind)) {
        if (exported(s)) exports.push(text(s.name));
      } else errors.push('top-level-form:' + e.path);
    }
    if (JSON.stringify(exports) !== JSON.stringify([e.name + 'Fields', e.name + 'Snapshot', 'create' + e.name + 'Factory', ...(e.provider ? [e.name + 'ValueComponent'] : []), ...(e.reference_bindings ? [e.name+'FieldBindings'] : [])])) errors.push('export-set:' + e.path);
    if (JSON.stringify(imports) !== JSON.stringify(e.imports)) errors.push('import-binding:' + e.path);
    if(e.reference_types || e.field_types) {
      const fields=source.statements.find(s=>s.kind===K.InterfaceDeclaration&&text(s.name)===e.name+'Fields');
      for(const [name,type] of Object.entries({...e.reference_types,...e.field_types})) {
        const field=fields?.members?.find(m=>m.name?.text===name);
        if(compact(field?.type)!==type)errors.push('reference-type:'+e.path+'#'+name);
      }
    }
    if (e.collection_protocols) {
      const actual = [...variables].filter(([name]) => /^field\d+Value$/.test(name)).map(([,value]) => compact(value));
      if (JSON.stringify(actual) !== JSON.stringify(e.collection_protocols)) errors.push('collection-composition:' + e.path);
      const protocols=e.collection_protocols.join('\n'),required=['ValueProtocol',...['stringValue','boolValue','ownedValue','optionalValue','listValue','setValue','enumValue','sumValue','ownedSumValue','uint64Value','ownedEntityValue'].filter(name=>protocols.includes(name))];
      if(protocols.includes('listValue')||protocols.includes('setValue'))required.push('sequenceValue');
      if(protocols.includes('sumValue'))required.push('SumPayloadProtocol','SumCaseOf');
      verifySupport(source,'field0Value',required,'collection-support:'+e.path);
    }
    const readValidators = initializer => {
      const array = unwrap(initializer);
      if (array?.kind !== K.ArrayLiteralExpression) {errors.push('validator-list:' + e.path); return [];}
      return array.elements.map(element => {
        const object = unwrap(element), rule = property(object, 'rule'), closure = property(object, 'closure_sha256'), artifact = property(object, 'artifact_sha256'), validate = property(object, 'validate');
        if (object?.kind !== K.ObjectLiteralExpression || object.properties.length !== 4 || rule?.kind !== K.StringLiteral || !/^[a-f0-9]{64}$/.test(closure?.text) || !/^[a-f0-9]{64}$/.test(artifact?.text) || validate?.kind !== K.ArrowFunction || validate.parameters.length !== 1) errors.push('validator-form:' + e.path);
        return {rule: rule?.text, call: compact(validate?.body)};
      });
    };
    if (JSON.stringify(readValidators(variables.get('baseValidators'))) !== JSON.stringify(e.base)) errors.push('base-binding:' + e.path);
    const extensions = unwrap(variables.get('extensionValidators'));
    const actualExtensions = extensions?.properties?.map(p => ({id: p.name?.expression?.text, validators: readValidators(p.initializer)}));
    if (JSON.stringify(actualExtensions) !== JSON.stringify(e.extensions)) errors.push('extension-binding:' + e.path);
    if (compact(variables.get('owned'))?.includes('snapshots.has(value)') !== true) errors.push('ownership-check:' + e.path);
    const visit = node => {
      if ([K.ClassDeclaration, K.ClassExpression, K.FunctionDeclaration, K.FunctionExpression].includes(node.kind)) errors.push('class-or-function:' + e.path);
      if (node.kind === K.CallExpression && ['eval', 'Function', 'JSON.stringify', 'JSON.parse'].includes(text(node.expression))) errors.push('ambient-or-serialization:' + e.path);
      if (node.kind === K.CallExpression && text(node.expression)?.startsWith('console.')) errors.push('ambient-call:' + e.path);
      node.forEachChild(visit);
    };
    visit(source);
    observations.push({path: e.path, exports, imports});
  }
  for (const e of expected.enum_components ?? []) {
    const source = project.program.getSourceFile(path.resolve(path.dirname(configPath), e.path));
    const definition = project.program.getSourceFile(path.resolve(path.dirname(configPath), e.definition));
    if (!source || !definition) {errors.push('missing-enum:' + e.path); continue;}
    const variables = new Map(), exports = [], imports = [];
    for (const s of source.statements) {
      if (s.kind === K.ImportDeclaration) imports.push(compact(s));
      else if (s.kind === K.VariableStatement) {
        if (!text(s.declarationList).startsWith('const ')) errors.push('enum-mutable:' + e.path);
        for (const d of s.declarationList.declarations) {variables.set(text(d.name), d.initializer); if (exported(s)) exports.push(text(d.name));}
      } else if (s.kind === K.TypeAliasDeclaration && exported(s)) exports.push(text(s.name));
      else errors.push('enum-top-level:' + e.path);
    }
    if (JSON.stringify(exports) !== JSON.stringify([e.name + 'Case',e.name + 'ValueComponent']) ||
      JSON.stringify(imports) !== JSON.stringify(['import{'+e.name+'asEnumDefinition}from'+JSON.stringify(e.definition_import)+';'])) errors.push('enum-bindings:' + e.path);
    const cases = unwrap(variables.get('cases')), provider = unwrap(variables.get(e.name + 'ValueComponent'));
    const actual = cases?.properties?.map(p => ({name:p.name?.expression?.text,value:compact(property(unwrap(p.initializer),'variant'))}));
    if (JSON.stringify(actual) !== JSON.stringify(e.members.map(name => ({name,value:'EnumDefinition['+JSON.stringify(name)+']'})))) errors.push('enum-cases:' + e.path);
    if (provider?.properties?.length !== 9 || property(provider,'concept')?.text !== e.selector ||
      property(provider,'contract_sha256')?.text !== e.contract_sha256 ||
      property(provider,'definition_sha256')?.text !== createHash('sha256').update(definition.getText()).digest('hex') ||
      compact(property(provider,'isOwned')) !== 'owned' || compact(property(provider,'values')) !== 'cases' ||
      compact(variables.get('ownership')) !== 'newWeakSet<object>(Object.values(cases))' ||
      !compact(variables.get('owned'))?.includes('ownership.has(value)')) errors.push('enum-ownership:' + e.path);
    const declaration = definition.statements.find(s => s.kind === K.VariableStatement && exported(s))?.declarationList.declarations[0];
    if (text(declaration?.name) !== e.name ||
      compact(declaration?.initializer) !== 'defineEnum('+JSON.stringify(Object.fromEntries(e.members.map(name=>[name,name])))+'asconst)') errors.push('enum-definition:' + e.path);
    observations.push({path:e.path,exports,imports});
  }
  for (const e of expected.sum_modules ?? []) {
    const source = project.program.getSourceFile(path.resolve(path.dirname(configPath),e.path));
    if (!source) {errors.push('missing-sum:' + e.path); continue;}
    const variables = new Map(), exports = [], imports = [];
    for (const s of source.statements) {
      if (s.kind === K.ImportDeclaration) for (const i of s.importClause?.namedBindings?.elements ?? []) imports.push({
        path:s.moduleSpecifier.text,symbol:text(i.propertyName ?? i.name),local:text(i.name),...(s.importClause?.isTypeOnly?{type_only:true}:{})});
      else if (s.kind === K.VariableStatement) {
        if (!text(s.declarationList).startsWith('const ')) errors.push('sum-mutable:' + e.path);
        for (const d of s.declarationList.declarations) {variables.set(text(d.name),d.initializer); if (exported(s)) exports.push(text(d.name));}
      } else if (s.kind === K.TypeAliasDeclaration) {if (exported(s)) exports.push(text(s.name));}
      else errors.push('sum-top-level:' + e.path);
    }
    if (JSON.stringify(exports) !== JSON.stringify([e.name+'Input',e.name+'Case',e.name+'ValueComponent']) ||
      JSON.stringify(imports) !== JSON.stringify(e.imports)) errors.push('sum-bindings:' + e.path);
    for (const [suffix, expectedType] of [['Input',e.input_type],['Case',e.case_type]]) {
      if (expectedType === undefined) continue;
      const declaration = source.statements.find(s=>s.kind===K.TypeAliasDeclaration && text(s.name)===e.name+suffix);
      if (compact(declaration?.type)!==expectedType) errors.push('sum-type:'+e.path+'#'+suffix);
    }
    if (compact(variables.get('shapeValue')) !== e.protocol) errors.push('sum-composition:' + e.path);
    const required=['ValueProtocol',...['stringValue','boolValue','ownedValue','optionalValue','listValue','setValue','enumValue','sumValue','ownedSumValue','uint64Value','ownedEntityValue'].filter(name=>e.protocol.includes(name))];
    if(e.protocol.includes('listValue')||e.protocol.includes('setValue'))required.push('sequenceValue');
    if(e.protocol.includes('sumValue'))required.push('SumPayloadProtocol','SumCaseOf');
    verifySupport(source,'shapeValue',required,'sum-support:'+e.path);
    const provider = unwrap(variables.get(e.name+'ValueComponent'));
    if (provider?.properties?.length !== 7 || property(provider,'concept')?.text !== e.selector ||
      property(provider,'contract_sha256')?.text !== e.contract_sha256 || compact(property(provider,'isOwned')) !== 'owned' ||
      compact(variables.get('cases')) !== 'newWeakMap<object,string>()' || !compact(variables.get('owned'))?.includes('cases.has(value)') ||
      !compact(property(provider,'create'))?.includes('shapeValue.normalize(input)')) errors.push('sum-ownership:' + e.path);
    observations.push({path:e.path,exports,imports});
  }
  if (expected.enum_provider) {
    const content = fs.readFileSync(path.resolve(path.dirname(configPath), expected.enum_provider.path));
    if (createHash('sha256').update(content).digest('hex') !== expected.enum_provider.sha256) errors.push('enum-provider');
  }
  snapshot.dispose();
} finally {api.close();}
console.log(JSON.stringify({schema_version: 'domainspec.configured-factory-observation/v1-candidate', result: errors.length ? 'fail' : 'pass', typescript: version, errors, observations, authority_effect: 'none'}));
if (errors.length) process.exitCode = 1;
