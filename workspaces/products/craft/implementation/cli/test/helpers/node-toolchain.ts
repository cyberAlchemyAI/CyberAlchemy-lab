import path from 'node:path';
import {createRequire} from 'node:module';
import {resolveTypeScriptCompiler} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/function-builder.ts';
// Reuse the qualified native resolver for the standalone checkout. Test-only.
// Open questions: installed package tool discovery remains BA18.
const core=path.resolve(import.meta.dirname,'../..'),alch=path.resolve(core,'../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation');
export const typescriptCompiler=resolveTypeScriptCompiler(core);
export const tsxLoader=createRequire(path.join(alch,'package.json')).resolve('tsx');
export const tsxCli=path.join(path.dirname(tsxLoader),'cli.mjs');
