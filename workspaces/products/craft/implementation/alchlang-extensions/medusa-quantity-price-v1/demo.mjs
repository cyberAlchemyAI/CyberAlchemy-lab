import {mkdtempSync, rmSync, readFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {buildApplication, root} from './build.mjs';
import {quotePrice} from './adapter.mjs';
const temp = mkdtempSync(path.join(os.tmpdir(), 'alch-price-demo-'));
try {
  const api = await buildApplication(temp);
  const fixture = JSON.parse(readFileSync(path.join(root,'fixtures.json'), 'utf8'))[0];
  console.log(JSON.stringify(quotePrice(api, fixture.snapshot, fixture.request), null, 2));
} finally { rmSync(temp, {recursive:true, force:true}); }
