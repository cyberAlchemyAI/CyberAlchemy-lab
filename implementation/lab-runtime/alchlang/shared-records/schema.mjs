import { spawnSync } from 'node:child_process';
import { digest } from './verified-projection.mjs';

export function validateSchema(schema, bytes) {
  const walk = value => {
    if (value && typeof value === 'object') {
      for (const [key, member] of Object.entries(value)) {
        if (key === '$ref' && !member.startsWith('#')) throw Error('unqualified-schema-reference');
        walk(member);
      }
    }
  };
  walk(schema);
  const child = spawnSync('python3', ['-B', '-c',
    'import json,sys,jsonschema; x=json.load(sys.stdin); jsonschema.Draft202012Validator.check_schema(x["schema"]); jsonschema.Draft202012Validator(x["schema"]).validate(x["value"])'],
    { input: JSON.stringify({ schema, value: JSON.parse(Buffer.from(bytes)) }), encoding: 'utf8', maxBuffer: 1024 * 1024 });
  if (child.status !== 0) throw Error('schema-validation-failed: ' + child.stderr.slice(-1200));
  return digest(bytes);
}
