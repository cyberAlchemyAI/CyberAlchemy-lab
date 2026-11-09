import {materializePackage} from './workspaces/products/define/implementation/cli/alchlang/runtime/package.mjs';
import {mkdtempSync} from 'node:fs';
const dir=mkdtempSync('/tmp/native-materialization-');
console.log(await materializePackage('workspaces/products/define/work/development/standalone-release/v1/evidence/e2e/materialization-package',dir+'/output'));