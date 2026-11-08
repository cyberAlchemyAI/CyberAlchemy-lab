import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
/** Independent Draft2020-12 check using the existing local Python jsonschema tool.
 * Test-only; no Python dependency in emitted/installed runtime. */
export function assertRequestSchema(root:string,file:string,value:unknown,invalid:unknown):void {
 const script=`import json,sys,pathlib,jsonschema
from referencing import Registry,Resource
root=pathlib.Path(sys.argv[1]);schemas=[json.loads(p.read_text()) for p in root.glob('*request-application*.schema.json')]
registry=Registry().with_resources((s['$id'],Resource.from_contents(s)) for s in schemas)
schema=json.loads((root/sys.argv[2]).read_text());jsonschema.Draft202012Validator.check_schema(schema)
validator=jsonschema.Draft202012Validator(schema,registry=registry);values=json.load(sys.stdin)
validator.validate(values[0]);assert list(validator.iter_errors(values[1])), 'negative control unexpectedly valid'
`;
 const run=spawnSync('python3',['-c',script,root,file],{input:JSON.stringify([value,invalid]),encoding:'utf8'});assert.equal(run.status,0,run.stdout+run.stderr);
}
