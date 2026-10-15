// Runtime comparison only: this is not an independent proof checker.
import fs from 'node:fs';
const request = JSON.parse(fs.readFileSync(0, 'utf8'));
const whitespace = [];
let scalarCount = 0;
for (let code = 0; code <= 0x10ffff; code++) {
  if (code >= 0xd800 && code <= 0xdfff) continue;
  scalarCount++;
  if (/\s/.test(String.fromCodePoint(code))) whitespace.push(code);
}
const results = request.cases.map(({pattern, value}) => new RegExp(pattern).test(value));
process.stdout.write(JSON.stringify({scalarCount, whitespace, results, nodeVersion: process.version}));
