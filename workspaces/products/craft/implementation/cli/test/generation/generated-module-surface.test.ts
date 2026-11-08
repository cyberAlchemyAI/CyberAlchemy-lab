import assert from 'node:assert/strict';
import test from 'node:test';
import {inventoryGeneratedModule} from '../../src/generation/generated-module-surface.ts';

test('inventories named declarations, aliases, namespaces and type reexports without reading strings as code', () => {
  const source = `/* export const fake = 1; */
import {run as local, type Input} from './leaf.js';
import type * as Public from '../api.js';
export type {Input as Request} from './leaf.js';
export interface Result {readonly value: string}
export type Value = Readonly<{result:Result}>;
export const execute = (x: Value) => {const text = "export const hidden = 1";return /[{}'\"/]/.test(text);};
export function check(x: number) {return x / 2;}
export {local as run};
`;
  const p = inventoryGeneratedModule(source);
  assert.deepEqual(p.exports, [{name:'Request',kind:'type'},{name:'Result',kind:'type'},{name:'Value',kind:'type'},{name:'check',kind:'value'},{name:'execute',kind:'value'},{name:'run',kind:'value'}]);
  assert.deepEqual(p.imports.map(i => [i.specifier,i.names,i.namespace,i.type_only,i.reexport]), [
    ['./leaf.js',['Input','run'],false,false,false], ['../api.js',[],true,true,false], ['./leaf.js',['Input'],false,true,true],
  ]);
});

test('unknown module syntax and malformed lexical input do not produce partial success', () => {
  for (const source of ['import thing from "x";', 'export * from "./x.js";', 'export default 1;', 'import("x")', '/*', 'const x = "', 'const x = /unterminated', 'export const x = {;', 'export const x = 1;export const x = 2;', 'const x = `text ${import("x")}`;', 'const x = `text ${1']) assert.throws(() => inventoryGeneratedModule(source), /DS_MODULE_SURFACE/);
  assert.deepEqual(inventoryGeneratedModule('export const x = `text ${String({a:1})}`;').exports,[{name:'x',kind:'value'}]);
});
