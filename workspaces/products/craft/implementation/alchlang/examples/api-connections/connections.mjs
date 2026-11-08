// Handwritten transport adapters around actual generated Interface value protocols.
// Open Questions: README.md and ../../docs/API-CONNECTIONS.md.
const failure = code => { throw new Error(code); };
const json = value => JSON.stringify(value, (_, field) => typeof field === 'bigint' ? field.toString() : field);
const reply = (status, value) => Object.freeze({status, headers:Object.freeze({'content-type':'application/json; charset=utf-8'}), body:json(value)});

/** Host-independent inbound handler. The host supplies authentication and routing. */
export function createFindHttpHandler({api,service,path='/orders/find',maxBytes=65536}) {
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 1 || maxBytes > 262144) failure('INVALID_BYTE_BOUND');
  return async request => {
    if (request.method !== 'POST' || request.path !== path) return reply(404,{error:'ROUTE_NOT_FOUND'});
    if (!api.acceptsVersion(request.headers?.['x-interface-version'])) return reply(409,{error:'UNSUPPORTED_INTERFACE_VERSION'});
    let normalized;
    try {
      if (typeof request.body !== 'string' || Buffer.byteLength(request.body,'utf8') > maxBytes) failure('INVALID_REQUEST_BODY');
      normalized = api.endpointValues.find.request.normalize(JSON.parse(request.body));
    } catch { return reply(400,{error:'INVALID_REQUEST'}); }
    let result;
    try { result = await service.find(normalized); }
    catch (error) { return reply(error?.message === 'NOT_FOUND' ? 404 : 500,{error:error?.message === 'NOT_FOUND'?'NOT_FOUND':'SERVICE_FAILED'}); }
    try {
      const output = api.endpointValues.find.result.normalize(result);
      const response = reply(200,output);
      if (Buffer.byteLength(response.body,'utf8') > maxBytes) failure('OUTPUT_BOUND');
      return response;
    } catch { return reply(502,{error:'INVALID_SERVICE_RESULT'}); }
  };
}

/** Explicit consumer adapter using real generated calculations and result Mapping. */
export function createExampleFindService({summary,commerceTotal,billingTotal,order}) {
  return Object.freeze({async find(id) {
    if (id !== BigInt(order.id)) failure('NOT_FOUND');
    const net = commerceTotal.calculateTotal({gross:'100',adjustment:'7'});
    const fee = billingTotal.calculateTotal({gross:'3',adjustment:'2'});
    return summary.mappingSummary({order,net,fee});
  }});
}

/** Outbound Interface adapter. Passing fetch is mandatory and test transport is injectable. */
export function createFindHttpClient({api,baseUrl,fetchImpl,version='1.0.0',timeoutMs=5000,path='/orders/find',maxBytes=65536}) {
  if (typeof fetchImpl !== 'function') failure('FETCH_ADAPTER_REQUIRED');
  if (!api.acceptsVersion(version)) failure('UNSUPPORTED_INTERFACE_VERSION');
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > 60000) failure('INVALID_TIMEOUT');
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 1 || maxBytes > 262144) failure('INVALID_BYTE_BOUND');
  const base = new URL(baseUrl);
  if (!['https:','http:'].includes(base.protocol) || base.username || base.password) failure('INVALID_BASE_URL');
  const target = new URL(path,base);
  if (target.origin !== base.origin) failure('INVALID_ROUTE_ORIGIN');
  return Object.freeze({async find(raw) {
    const request = api.endpointValues.find.request.normalize(raw);
    const body = json(request);
    if (Buffer.byteLength(body,'utf8') > maxBytes) failure('REQUEST_BOUND');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(),timeoutMs);
    try {
      const response = await fetchImpl(target.href,{method:'POST',headers:{'content-type':'application/json','accept':'application/json','x-interface-version':version},body,signal:controller.signal});
      if (!response.ok) failure('REMOTE_HTTP_'+response.status);
      if (!/^application\/json(?:\s*;|$)/i.test(response.headers.get('content-type') ?? '')) failure('REMOTE_CONTENT_TYPE');
      const text = await response.text();
      if (Buffer.byteLength(text,'utf8') > maxBytes) failure('REMOTE_RESPONSE_BOUND');
      return api.endpointValues.find.result.normalize(JSON.parse(text));
    } finally { clearTimeout(timer); }
  }});
}
