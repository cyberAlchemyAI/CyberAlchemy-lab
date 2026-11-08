import {execFileSync} from 'node:child_process';
import {readdirSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
export const root = path.dirname(fileURLToPath(import.meta.url));
export const implementation = path.resolve(root, '../../implementation');
export function buildApplication(output) {
  output = path.resolve(output);
  const bundle = path.join(output, 'bundle'), js = path.join(output, 'js');
  execFileSync(process.execPath, [path.join(implementation, 'dist/cli.js'), 'build', path.join(root, 'quantity-price.alch'),
    '--backend', 'domainspec', '--language', 'typescript', '--profile', 'domainspec-1.0.0-exact-uint64-v1', '--out', bundle], {encoding:'utf8'});
  const files = p => readdirSync(p, {withFileTypes:true}).flatMap(e => e.isDirectory() ? files(path.join(p,e.name)) : [path.join(p,e.name)]);
  execFileSync(process.execPath, [path.join(implementation, 'scripts/run-toolchain.mjs'), 'tsc',
    '--ignoreConfig', '--strict', '--skipLibCheck', '--target', 'ES2022', '--module', 'commonjs',
    '--moduleResolution', 'bundler', '--rootDir', bundle, '--outDir', js,
    ...files(bundle).filter(p => p.endsWith('.ts'))], {encoding:'utf8', cwd:output});
  writeFileSync(path.join(js, 'package.json'), JSON.stringify({type:'commonjs'})+'\n');
  return import(pathToFileURL(path.join(js, 'domain.js')).href);
}
