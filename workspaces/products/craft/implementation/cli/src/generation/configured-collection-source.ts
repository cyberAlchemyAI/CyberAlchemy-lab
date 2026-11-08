// Private, emitted owned-component combinators. Scope/open questions:
// development/reconciliation-v1/profile-compiler-reconciliation/COLLECTION-FACTORY-GENERATION.md.
// Composition is static generated TypeScript, not a runtime type-description interpreter.
export function renderCollectionSupport(): string {
  return renderCollectionSupportFor(["stringValue", "boolValue", "ownedValue", "optionalValue", "listValue", "setValue"]);
}

export function renderCollectionSupportFor(expressions: readonly string[]): string {
  const source = expressions.join("\n");
  const uses = (name: string): boolean => source.includes(name);
  const sequence = uses("listValue") || uses("setValue");
  return `type ValueProtocol<T> = Readonly<{normalize:(input:unknown)=>T;key:(value:T)=>string}>;
${uses("stringValue") ? `const stringValue:ValueProtocol<string> = Object.freeze({
  normalize:(input:unknown):string=>{if(typeof input !== 'string') throw new TypeError('INVALID_COMPONENT');return input;},
  key:(value:string):string=>part('String') + part(value),
});
` : ""}${uses("boolValue") ? `const boolValue:ValueProtocol<boolean> = Object.freeze({
  normalize:(input:unknown):boolean=>{if(typeof input !== 'boolean') throw new TypeError('INVALID_COMPONENT');return input;},
  key:(value:boolean):string=>part('Bool') + part(value ? '1' : '0'),
});
` : ""}${uses("ownedValue") ? `const ownedValue = <T>(provider:Readonly<{isOwned:(input:unknown)=>input is T;key:(input:unknown)=>string}>):ValueProtocol<T> => Object.freeze({
  normalize:(input:unknown):T=>{if(!provider.isOwned(input)) throw new TypeError('UNOWNED_COMPONENT');return input;},
  key:(value:T):string=>part('ValueObject') + part(provider.key(value)),
});
` : ""}${uses("optionalValue") ? `const optionalValue = <T>(element:ValueProtocol<T>):ValueProtocol<T|null> => Object.freeze({
  normalize:(input:unknown):T|null=>input === null ? null : element.normalize(input),
  key:(value:T|null):string=>part('Optional') + (value === null ? part('absent') : part('present') + part(element.key(value))),
});
` : ""}${sequence ? `const sequenceValue = <T>(element:ValueProtocol<T>,unique:boolean):ValueProtocol<readonly T[]> => {
  const ownedSequences = new WeakMap<readonly T[],string>();
  return Object.freeze({
    normalize:(input:unknown):readonly T[]=>{
      if(!Array.isArray(input) || Object.getPrototypeOf(input) !== Array.prototype) throw new TypeError('INVALID_COLLECTION');
      const descriptors:Record<string,PropertyDescriptor> = Object.getOwnPropertyDescriptors(input as object);
      const length = descriptors.length!.value as number;
      if(Reflect.ownKeys(descriptors).length !== length + 1) throw new TypeError('INVALID_COLLECTION');
      const entries:{value:T;key:string}[] = [];
      for(let i = 0; i < length; i++) {
        const descriptor = descriptors[String(i)];
        if(!descriptor || !Object.hasOwn(descriptor,'value') || !descriptor.enumerable) throw new TypeError('INVALID_COLLECTION');
        const value = element.normalize(descriptor.value);
        entries.push({value,key:element.key(value)});
      }
      if(unique) {
        if(new Set(entries.map(entry=>entry.key)).size !== entries.length) throw new TypeError('DUPLICATE_SET_VALUE');
        entries.sort((a,b)=>a.key < b.key ? -1 : a.key > b.key ? 1 : 0);
      }
      const result = Object.freeze(entries.map(entry=>entry.value));
      const key = part(unique ? 'Set' : 'List') + part(String(entries.length)) + entries.map(entry=>part(entry.key)).join('');
      ownedSequences.set(result,key);
      return result;
    },
    key:(value:readonly T[]):string=>{
      const key = ownedSequences.get(value);
      if(key === undefined) throw new TypeError('UNOWNED_COLLECTION');
      return key;
    },
  });
};
` : ""}${uses("listValue") ? "const listValue = <T>(element:ValueProtocol<T>):ValueProtocol<readonly T[]> => sequenceValue(element,false);\n" : ""}${uses("setValue") ? "const setValue = <T>(element:ValueProtocol<T>):ValueProtocol<readonly T[]> => sequenceValue(element,true);\n" : ""}`;
}
