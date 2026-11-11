import { readFileSync, existsSync, mkdirSync, mkdtempSync, renameSync, rmSync } from 'node:fs';
import path from 'node:path';
import { build, root, craftRoot, sha } from './build.mjs';
import { createSourceOperationCompiler } from '../../../../implementation/artifact-runtime/compile-source-operation.mjs';
import { evaluateArtifact } from '../../../../implementation/artifact-runtime/pure-operation.mjs';

let compiler;
const operations = new Set([
  'ReviewFiveDefinitions', 'SelectCompatibility', 'AssessExecutionContext',
  'PlanCreationRoute', 'PlanPublication', 'PlanJoinContinuation',
  'PlanLifecycleImpact', 'AssessConstructionEntry', 'AssessConstructionCompletion',
  'AssessJoinTransition', 'ValidateJoinTransition', 'ProposeJoinTransition', 'AssessJoinInitialization'
]);

export async function evaluate(operation, input) {
  if (!operations.has(operation)) throw Error('unknown-shared-operation');
  const model = build();
  const directory = path.join(root, '.local', 'operations', model.source, operation);
  if (!existsSync(directory)) {
    compiler ??= await createSourceOperationCompiler(path.join(craftRoot, 'cli'));
    mkdirSync(path.dirname(directory), { recursive: true });
    const staging = mkdtempSync(path.join(path.dirname(directory), '.compile-'));
    try {
      const output = path.join(staging, 'artifact');
      compiler.compile({
        modelRoot: path.join(model.output, 'model'),
        selector: 'Lab.SharedDesign.' + operation, outputDirectory: output
      });
      try { renameSync(output, directory); }
      catch (error) { if (!existsSync(path.join(directory, 'manifest.json'))) throw error; }
    } finally { rmSync(staging, { recursive: true, force: true }); }
  }
  const manifest = path.join(directory, 'manifest.json');
  const result = await evaluateArtifact(directory, 'operation.mjs', input, {
    manifest_sha256: sha(readFileSync(manifest))
  });
  if (!result.ok) throw Error(JSON.stringify(result.error));
  const value = JSON.parse(new TextDecoder().decode(result.wire));
  if (value.tag !== 'Returned') throw Error(value.fields.code);
  return value.fields.value;
}
