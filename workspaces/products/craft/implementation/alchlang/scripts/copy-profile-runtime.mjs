import {mkdirSync,copyFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
// Open questions: PE21 public envelope and PE23 installed qualification.
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
mkdirSync(path.join(root,'runtime-sources'),{recursive:true});
copyFileSync(path.join(root,'src/boundary-runtime.ts'),path.join(root,'runtime-sources/boundary-runtime.ts'));
