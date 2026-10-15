import {buildSemanticContract} from './vendor/semantic-contract/compiler.js';
const [command, source, option, target, ...extra] = process.argv.slice(2);
try {
  if (command !== 'build' || !source || option !== '--out' || !target || extra.length) throw new Error('Usage: compiler.mjs build SOURCE --out NEW_DIRECTORY');
  console.log(JSON.stringify(await buildSemanticContract(source, target)));
} catch (error) { console.error(error.message); process.exitCode = 3; }
