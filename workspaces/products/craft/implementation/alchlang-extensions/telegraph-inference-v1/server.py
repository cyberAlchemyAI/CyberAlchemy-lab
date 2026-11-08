"""Alch contract adapter. Upstream owns inference, x402 verification and settlement."""
import argparse
import http.client
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
from compile import compile_source

HOP = {'connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailer','transfer-encoding','upgrade'}
REQUEST_HEADERS = {'content-type','accept','accept-encoding','payment-signature','x-payment','x-request-id','idempotency-key','last-event-id'}

def application(source, environment=None, allow_loopback_http=False):
    model = compile_source(source)
    environment = os.environ if environment is None else environment
    for binding in model['integrations'].values():
        value = environment.get(binding['url-env'])
        binding['url'] = None
        if not value:
            continue
        url = urlsplit(value)
        local = url.hostname in {'127.0.0.1','::1','localhost'}
        if url.username or url.password or url.query or url.fragment or not url.hostname or (url.scheme != 'https' and not (allow_loopback_http and local and url.scheme == 'http')):
            raise ValueError('ALCH_HTTP_UPSTREAM_URL: HTTPS required; fixture HTTP must be explicit loopback')
        if any(part in {'.','..'} for part in unquote(url.path).split('/')):
            raise ValueError('ALCH_HTTP_UPSTREAM_PATH')
        binding['url'] = url
    return model

def handler_for(model):
    slots = threading.BoundedSemaphore(16)
    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        def setup(self):
            super().setup();self.connection.settimeout(15)
        def log_message(self, *args):
            pass
        def respond(self, code, error):
            raw=json.dumps(error).encode();self.send_response(code)
            self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)))
            self.send_header('Connection','close');self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(raw);self.close_connection=True
        def handle_api(self):
            if not slots.acquire(blocking=False):
                return self.respond(503,{'error':'capacity exhausted','code':'service_unavailable'})
            try:self.forward()
            finally:slots.release()
        def forward(self):
            parsed=urlsplit(self.path);path=parsed.path;decoded=unquote(path)
            if parsed.scheme or parsed.netloc or parsed.fragment or '%' in decoded or '\\' in decoded or any(part in {'.','..'} for part in decoded.split('/')) or any(ord(c)<32 for c in decoded):
                return self.respond(400,{'error':'invalid path','code':'invalid_request'})
            if self.command=='GET' and path=='/healthz':
                return self.respond(200,{'service':'alch-telegraph-adapter','configured':all(v['url'] for v in model['integrations'].values())})
            if self.headers.get('Upgrade'):
                return self.respond(501,{'error':'WebSocket profile is not implemented','code':'not_implemented'})
            route=next((r for r in model['routes'] if r['method']==self.command and re.fullmatch(r['pattern'],path)),None)
            if route is None:
                return self.respond(404,{'error':'route not found','code':'not_found'})
            binding=model['integrations'][route['integration']];url=binding['url']
            if url is None:
                return self.respond(503,{'error':'inference upstream is not configured','code':'service_unavailable'})
            lengths=self.headers.get_all('Content-Length',[])
            if self.headers.get('Transfer-Encoding') or len(lengths)>1 or (lengths and not re.fullmatch(r'[0-9]+',lengths[0])):
                return self.respond(400,{'error':'invalid request framing','code':'invalid_request'})
            length=int(lengths[0]) if lengths else 0
            if length>binding['max-request-bytes']:
                return self.respond(413,{'error':'request exceeds configured limit','code':'request_too_large'})
            if self.command in {'POST','PUT','PATCH'} and not lengths:
                return self.respond(411,{'error':'Content-Length required','code':'length_required'})
            for name in REQUEST_HEADERS:
                if len(self.headers.get_all(name,[]))>1:
                    return self.respond(400,{'error':'duplicate forwarded header','code':'invalid_request'})
            try:
                body=self.rfile.read(length)
                if len(body)!=length:raise ValueError('short body')
            except (OSError,ValueError):
                return self.respond(400,{'error':'incomplete request','code':'invalid_request'})
            # User-controlled payloads are opaque; upstream validates the contract.
            # No caller-supplied host, forwarding identity or internal secret is trusted.
            connection_tokens={v.strip().lower() for v in self.headers.get('Connection','').split(',')}
            headers={name:value for name,value in self.headers.items() if name.lower() in REQUEST_HEADERS-HOP-connection_tokens}
            headers['Content-Length']=str(length)
            headers['Connection']='close'
            api=model['apis'][route['api']]
            target=url.path.rstrip('/')+path[len(api['mount']):]
            if parsed.query:target+='?'+parsed.query
            cls=http.client.HTTPSConnection if url.scheme=='https' else http.client.HTTPConnection
            upstream=cls(url.hostname,url.port,timeout=binding['timeout-seconds']);started=False
            try:
                upstream.request(self.command,target,body,headers)
                response=upstream.getresponse()
                # Never follow redirects or retry: a payment-bearing request may have executed.
                if response.status==101:
                    return self.respond(502,{'error':'unexpected upstream upgrade','code':'bad_gateway'})
                known=response.getheader('Content-Length')
                if known and (not known.isdigit() or int(known)>binding['max-response-bytes']):
                    return self.respond(502,{'error':'upstream response exceeds configured limit','code':'bad_gateway'})
                blocked=HOP|{x.strip().lower() for x in response.getheader('Connection','').split(',')}
                self.send_response_only(response.status)
                for name,value in response.getheaders():
                    if name.lower() not in blocked:self.send_header(name,value)
                self.send_header('Connection','close');self.end_headers();started=True
                count=0
                while True:
                    chunk=response.read1(65536)
                    if not chunk:break
                    count+=len(chunk)
                    if count>binding['max-response-bytes']:raise ValueError('upstream size limit')
                    self.wfile.write(chunk);self.wfile.flush()
            except (OSError,http.client.HTTPException,ValueError):
                if not started:
                    self.respond(502,{'error':'upstream request failed; execution outcome may be unknown','code':'bad_gateway'})
            finally:
                upstream.close();self.close_connection=True
        do_GET=handle_api
        do_POST=handle_api
        do_PUT=handle_api
        do_PATCH=handle_api
        do_DELETE=handle_api
        do_HEAD=handle_api
        do_OPTIONS=handle_api
    return Handler

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source');parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=8090)
    args=parser.parse_args();model=application(args.source)
    server=ThreadingHTTPServer((args.host,args.port),handler_for(model))
    print(json.dumps({'status':'listening','host':args.host,'port':args.port,'operations':len(model['routes'])}),flush=True)
    server.serve_forever()
