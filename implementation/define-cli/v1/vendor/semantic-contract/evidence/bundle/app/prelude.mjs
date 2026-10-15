const canonical=value=>value.normalize('NFKC').trim().toLowerCase();
const semanticKeyValue=value=>canonical(value).replace(/[^\p{L}\p{N}]+/gu,' ').trim();
export function normalizeNfkc(value){if(typeof value!=='string')throw new TypeError('normalize-nfkc input must be string');return value.normalize('NFKC');}
export function canonicalText(value){if(typeof value!=='string')throw new TypeError('canonical-text input must be string');return canonical(value);}
export function semanticKey(value){if(typeof value!=='string')throw new TypeError('semantic-key input must be string');return semanticKeyValue(value);}
export function containsToken(input){if(!input||typeof input.text!=='string'||typeof input.token!=='string')throw new TypeError('contains-token input');return (canonical(input.text).match(/[\p{L}\p{N}_]+/gu)??[]).includes(canonical(input.token));}
export function containsPhrase(input){if(!input||typeof input.text!=='string'||typeof input.phrase!=='string')throw new TypeError('contains-phrase input');const text=semanticKeyValue(input.text),phrase=semanticKeyValue(input.phrase);return phrase.length>0&&(' '+text+' ').includes(' '+phrase+' ');}
export function appendReason(input){if(!input||!Array.isArray(input.reasons)||typeof input.reason!=='string'||!input.reasons.every(item=>typeof item==='string'))throw new TypeError('append-reason input');const reasons=[...input.reasons];if(!reasons.includes(input.reason))reasons.push(input.reason);return reasons;}
const operations={'normalize-nfkc':normalizeNfkc,'canonical-text':canonicalText,'semantic-key':semanticKey,'contains-token':containsToken,'contains-phrase':containsPhrase,'append-reason':appendReason};
export function invoke(operation,input){const selected=operations[operation];if(!selected)throw new Error('SEMANTIC_OPERATION_NOT_FOUND');return selected(input);}
