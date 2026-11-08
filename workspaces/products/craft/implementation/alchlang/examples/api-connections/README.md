# Inbound and outbound adapters

Read [API-CONNECTIONS.md](../../docs/API-CONNECTIONS.md) for the worked flow and
actual AlchLang declarations. `connections.mjs` contains handwritten HTTP
adapters around real generated Interface normalizers, Mapping and Calculation
exports. It does not start a server, discover providers or inject domain effects.

Generate the exact installed Craft commerce example first, then run:

```sh
node connections.test.mjs \
  --generated-root /absolute/path/generated-1-js \
  --example-root /absolute/path/node_modules/@domainspec-v2/cli/examples/reconciled-commerce
```

The program verifies eight groups through actual generated exports. It uses an
HTTP-shaped request object and a supplied in-memory fetch transport returning
standard Response objects. Every network call and listener count remains zero.
The exported runner is `runApiConnections({generatedRoot, exampleRoot})`.

The public adapter functions are
`createFindHttpHandler({api,service,path?,maxBytes?})`,
`createExampleFindService({summary,commerceTotal,billingTotal,order})`, and
`createFindHttpClient({api,baseUrl,fetchImpl,version?,timeoutMs?,path?,maxBytes?})`.

The service fixture explicitly supplies the native generated Calculation inputs
and Mapping dependencies. A real service implementation supplies its own read
provider and authorization policy. The current Interface's request is a UInt64
value and result is the closed `{id,net,fee}` contract; other Interface members
need their own declared adapter shapes.

## Open Questions

[The guide](../../docs/API-CONNECTIONS.md#open-questions) owns installed package,
own-host transport and real provider qualification. The response cap is checked
after text decoding; a streaming memory bound belongs to a separately supplied
body reader. No remote behavior follows from this local witness.
