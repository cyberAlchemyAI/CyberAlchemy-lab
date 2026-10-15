import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
export async function loadDomainSpecCompiler() {
  const root = resolve(import.meta.dirname, '../../../../../craft/impl/cli');
  const metadata = JSON.parse(readFileSync(resolve(root, 'package.json')));
  const entry = resolve(root, metadata.exports['.'].import);
  const api = await import(pathToFileURL(entry));
  if (api.CLI_PACKAGE_NAME !== metadata.name || api.CLI_VERSION !== metadata.version || typeof api.compileProject !== 'function') {
    throw new Error('define.craft-build-does-not-match-package; rebuild craft/impl/cli');
  }
  return {compileProject: api.compileProject,
    binding: {package: metadata.name, version: metadata.version,
      entry_sha256: createHash('sha256').update(readFileSync(entry)).digest('hex'),
      authority_effect: 'none', selection: 'existing-lab-craft-public-compiler'}};
}
