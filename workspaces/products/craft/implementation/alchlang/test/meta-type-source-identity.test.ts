import assert from "node:assert/strict";
import test from "node:test";
import {parseDomainSource} from "../src/parser.js";

test("compatibility sources reject repeated identity and owner headers before last-wins lowering", () => {
  const source = 'domain orders "Orders"\nowner example-owner\n';
  assert.equal(parseDomainSource(source).carrier.identity !== undefined, true);
  for (const duplicate of ['domain other "Other"\n', 'owner other-owner\n', 'domain orders "Orders"\n', 'owner example-owner\n']) {
    assert.throws(() => parseDomainSource(source + duplicate), /SOURCE_IDENTITY/);
  }
});
