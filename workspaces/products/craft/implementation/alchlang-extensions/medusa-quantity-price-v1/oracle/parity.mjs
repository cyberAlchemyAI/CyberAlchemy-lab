import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash,randomUUID} from 'node:crypto';
import {createRequire} from 'node:module';
import {mkdirSync,mkdtempSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import knexFactory from 'knex';
import {buildApplication,root} from '../build.mjs';
import {prepareQuote,quotePrice,usdToMinor} from '../adapter.mjs';
const require = createRequire(import.meta.url);
const moduleRoot = path.dirname(require.resolve('@medusajs/pricing/package.json'));
const repositoryPath = path.join(moduleRoot,'dist/repositories/pricing.js');
const {PricingRepository} = require(repositoryPath);
const sha = value => createHash('sha256').update(value).digest('hex');
const image = 'postgres:16.4-alpine@sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c';
const args = process.argv.slice(2);
assert.ok(args.length === 0 || (args.length === 2 && args[0] === '--out'), 'usage: node parity.mjs [--out NEW_DIRECTORY]');
const durable = args.length > 0;
const output = durable ? path.resolve(args[1]) : mkdtempSync(path.join(os.tmpdir(),'alch-medusa-oracle-'));
if (durable) mkdirSync(output); // Existing output is never overwritten.
const container = 'alch-medusa-price-' + randomUUID();
const password = randomUUID();
let created = false, knex;
const outcomes = [];
const docker = (...args) => execFileSync('docker',args,{encoding:'utf8',timeout:120000});
try {
  const api = await buildApplication(output);
  docker('run','--detach','--rm','--name',container,'--label','alchlang.quantity-price-oracle=true',
    '--publish','127.0.0.1::5432','--tmpfs','/var/lib/postgresql/data:rw',
    '--env','POSTGRES_USER=oracle','--env','POSTGRES_DB=oracle','--env',`POSTGRES_PASSWORD=${password}`,image);
  created = true;
  const state = JSON.parse(docker('inspect',container))[0];
  const hostPort = Number(state.NetworkSettings.Ports['5432/tcp'][0].HostPort);
  // A fresh PostgreSQL process with a minimal query schema, not a live shop or migrated Medusa installation.
  knex = knexFactory({client:'pg',connection:{host:'127.0.0.1',port:hostPort,user:'oracle',password,database:'oracle'},pool:{min:0,max:1},acquireConnectionTimeout:2000});
  let connected=false;
  for(let i=0;i<60;i++) {try {await knex.raw('select 1');connected=true;break;} catch {await new Promise(r=>setTimeout(r,250));}}
  assert.ok(connected,'temporary PostgreSQL failed to start');
  await knex.raw(`create table price_list (id text primary key, type text, rules_count integer, status text, deleted_at timestamptz, starts_at timestamptz, ends_at timestamptz);
    create table price (id text primary key, price_set_id text, amount numeric, raw_amount jsonb, min_quantity numeric, max_quantity numeric, currency_code text, price_list_id text, rules_count integer, deleted_at timestamptz);`);
  // Only the manager is supplied: Medusa's published repository and its Knex SQL run unmodified.
  const repository = new PricingRepository({manager:{getKnex:()=>knex}});
  const fixtures=JSON.parse(readFileSync(path.join(root,'fixtures.json'),'utf8'));
  const canonical = rows => rows.map(r=>({...r,amountMinor:r.amountMinor.toString()})).sort((a,b)=>a.priceId.localeCompare(b.priceId));
  async function compare(fixture) {
    await knex('price').delete();
    if(fixture.snapshot.prices.length) await knex('price').insert(fixture.snapshot.prices.map(p=>({...p, amount:p.raw_amount.value, raw_amount:JSON.stringify(p.raw_amount)})));
    const context={currency_code:fixture.request.currency_code,quantity:fixture.request.quantity};
    const upstream=await repository.calculatePrices({id:[fixture.snapshot.price_set_id]},{context});
    const prepared=prepareQuote(fixture.snapshot,fixture.request);
    const generated=api.evaluateQuery('EligiblePrices',prepared.rows,prepared.parameters);
    const reference=upstream.map(p=>({priceId:p.id,currency:p.currency_code,amountMinor:usdToMinor(p.raw_amount.value)}));
    assert.deepEqual(canonical(generated),canonical(reference),fixture.name+' eligible set');
    // Compare amount order while leaving equal-price ID order unspecified.
    assert.deepEqual(generated.map(p=>p.amountMinor),reference.map(p=>p.amountMinor),fixture.name+' amount order');
    const quote=quotePrice(api,fixture.snapshot,fixture.request);
    if(fixture.expected) for(const [key,value] of Object.entries(fixture.expected)) assert.deepEqual(quote[key],value,fixture.name+' '+key);
    if(quote.status==='quoted') assert.equal(quote.price_id,upstream[0].id);
    if(quote.status==='no_price') assert.equal(upstream.length,0);
    if(quote.status==='ambiguous_price') assert.ok(quote.price_ids.includes(upstream[0].id));
    outcomes.push({name:fixture.name,status:'pass',eligible_ids:reference.map(p=>p.priceId),quote});
  }
  for(const fixture of fixtures) {
    await compare(fixture);
    await compare({...fixture,name:fixture.name+'_reversed',snapshot:{...fixture.snapshot,prices:[...fixture.snapshot.prices].reverse()}});
  }
  let seed=123456;
  const random=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n;};
  for(let i=0;i<80;i++) {
    const fixture=structuredClone(fixtures[0]);fixture.name='seeded_'+i;delete fixture.expected;
    fixture.request.quantity=1+random(40);
    fixture.snapshot.prices=Array.from({length:random(12)},(_,j)=>{
      const min=random(3)?1+random(30):null,max=random(3)?(min??1)+random(20):null;
      return {id:'price_'+j,price_set_id:'ps_shirt',currency_code:random(5)?'usd':'eur',raw_amount:{value:(random(10000)/100).toFixed(2),precision:20},min_quantity:min,max_quantity:max,price_list_id:null,rules_count:0,deleted_at:random(10)?null:'2026-01-01T00:00:00Z'};
    });
    await compare(fixture);
  }
  await assert.rejects(repository.calculatePrices({id:['ps_shirt']},{context:{quantity:1}}),/requires currency_code/);
  const missing=structuredClone(fixtures[0]);delete missing.request.currency_code;
  assert.throws(()=>prepareQuote(missing.snapshot,missing.request),/QUOTE_CURRENCY_REQUIRED/);
  const lock=JSON.parse(readFileSync(new URL('./package-lock.json',import.meta.url),'utf8'));
  const receipt={schema_version:'alchlang.medusa-parity/v1',status:'pass',
    claim_ceiling:'Actual Medusa repository eligibility and amount ordering on a minimal PostgreSQL schema; not full service, migrations, cart integration, tax, or product approval.',
    release:'v2.18.0',source_commit:JSON.parse(readFileSync(path.join(root,'sources.json'),'utf8')).commit,
    package_integrity:lock.packages['node_modules/@medusajs/pricing'].integrity,
    repository_sha256:sha(readFileSync(repositoryPath)),lock_sha256:sha(readFileSync(new URL('./package-lock.json',import.meta.url))),
    postgres_image:image,fixture_sha256:sha(readFileSync(path.join(root,'fixtures.json'))),
    generated_manifest_sha256:sha(readFileSync(path.join(output,'bundle/manifest.json'))),
    cases:outcomes.length,missing_currency:'both reject',tie_contract:'AlchLang reports ambiguity; upstream has no ID tie-break',outcomes};
  writeFileSync(path.join(output,'parity.json'),JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({status:'pass',cases:outcomes.length,missing_currency:'both reject',receipt:durable?path.join(output,'parity.json'):null},null,2));
} finally {
  try {if(knex) await knex.destroy();} finally {
    try {if(created) docker('rm','--force',container);} finally {if(!durable)rmSync(output,{recursive:true,force:true});}
  }
}
