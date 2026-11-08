import {invoke} from "./evidence/bundle/app/prelude.mjs";

export const semanticContract = Object.freeze({
  profile: "semantic-contract-v1",
  source: "semantic-prelude.alch",
  binding: "direct-compiled-artifact",
  ontology_admitted: false,
  constitution_adopted: false,
  authority_effect: "none",
});

export function semanticKey(value) {
  return invoke("semantic-key", String(value ?? ""));
}

export function containsPhrase(text, phrase) {
  return invoke("contains-phrase", {text: String(text ?? ""), phrase: String(phrase ?? "")});
}
