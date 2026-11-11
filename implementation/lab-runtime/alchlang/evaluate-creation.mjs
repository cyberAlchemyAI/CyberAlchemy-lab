import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
import { implementationRoot as craftRoot } from '../../../craft/implementation/source-bindings.mjs';
import { createSourceOperationCompiler } from '../../artifact-runtime/compile-source-operation.mjs';
import { evaluateArtifact } from '../../artifact-runtime/pure-operation.mjs';

const request = JSON.parse(readFileSync(0, 'utf8'));
const selectors = {
  definition: 'Lab.Definitions.CreateDefinition.CreateDefinition',
  record: 'Lab.Records.CreateRecord.CreateRecord',
  'artifact-type': 'Lab.ArtifactTypes.CreateArtifactType.CreateArtifactType'
};
const selector = selectors[request.kind];
if (!selector) throw Error('unsupported-creation-kind');
const originalSources=[...readFileSync(path.join(root,'creation-source.alch'),'utf8').matchAll(/^  source (.+)$/gm)].map(match=>match[1]);
const source=sha(JSON.stringify(['creation-source.alch','shared-records/contracts/bounds.json','evaluate-creation.mjs',...originalSources]
  .map(name=>[name,sha(readFileSync(path.join(root,name)))])));
const output = path.join(root, '.local', 'public-creation', source, request.kind);
if (!existsSync(output)) {
  mkdirSync(path.dirname(output), { recursive: true });
  const compiler = await createSourceOperationCompiler(path.join(craftRoot, 'cli'));
  compiler.compile({ modelRoot: root, applicationPath:'creation-source.alch', pureSources:true, selector, outputDirectory: output });
}
const result = await evaluateArtifact(output, 'operation.mjs', request.input, {
  manifest_sha256: sha(readFileSync(path.join(output, 'manifest.json')))
});
if (!result.ok) throw Error(JSON.stringify(result.error));
const value = JSON.parse(new TextDecoder().decode(result.wire));
if (value.tag !== 'Returned') throw Error(value.fields.code);
process.stdout.write(JSON.stringify(value.fields.value));
