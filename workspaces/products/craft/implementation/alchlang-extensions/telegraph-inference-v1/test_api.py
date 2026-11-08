import http.client
import json
import shutil
import socket
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from compile import compile_source
from server import application, handler_for

HERE=Path(__file__).resolve().parent
SEEN=[]

class MinerFixture(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args):pass
    def handle_api(self):
        body=self.rfile.read(int(self.headers.get('Content-Length','0')))
        SEEN.append({'method':self.command,'path':self.path,'body':body,'headers':dict(self.headers)})
        if self.path.endswith('disconnect'):
            self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
        if self.path.endswith('stream'):
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Connection','close');self.end_headers()
            self.wfile.write(b'data: first\n\n');self.wfile.flush();time.sleep(.5)
            self.wfile.write(b'data: [DONE]\n\n');self.wfile.flush();self.close_connection=True;return
        if self.path.endswith('redirect'):
            self.send_response(307);self.send_header('Location','https://unrelated.invalid/private');self.send_header('Content-Length','0');self.end_headers();return
        if self.path.endswith('/v1/ask'):
            if self.headers.get('PAYMENT-SIGNATURE') != 'fixture-proof':
                status=402;value={'error':'x402 payment required','accepts':[{'scheme':'x402','price':'10000','network':'fixture','payTo':'fixture-only'}]}
            else:
                status=200;value={'miner_used':'fixture-miner','miner_name':'Local fixture','result':{'answer':'fixture output'},'cost_usd':0.01,'duration_ms':1,'timestamp':'2026-09-06T00:00:00Z'}
        else:status=200;value={'method':self.command,'path':self.path,'fixture':True}
        raw=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('PAYMENT-REQUIRED','fixture-challenge');self.send_header('PAYMENT-RESPONSE','fixture-receipt')
        self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    do_GET=handle_api
    do_POST=handle_api
    do_PUT=handle_api
    do_PATCH=handle_api
    do_DELETE=handle_api

class ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream=ThreadingHTTPServer(('127.0.0.1',0),MinerFixture)
        threading.Thread(target=cls.upstream.serve_forever,daemon=True).start()
        port=cls.upstream.server_port
        cls.env={'TELEGRAPH_ENGINE_URL':f'http://127.0.0.1:{port}/engine','TELEGRAPH_DISPATCHER_URL':f'http://127.0.0.1:{port}/miner-dispatcher'}
        cls.model=application(HERE/'inference.alch',cls.env,allow_loopback_http=True)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(cls.model))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
    @classmethod
    def tearDownClass(cls):
        for server in [cls.server,cls.upstream]:server.shutdown();server.server_close()
    def request(self,method,path,body=b'',headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        conn.request(method,path,body,headers or {});r=conn.getresponse();result=(r.status,dict(r.getheaders()),r.read());conn.close();return result
    def test_01_contract_coverage_and_binding(self):
        model=compile_source(HERE/'inference.alch')
        self.assertEqual(len(model['routes']),32);self.assertEqual(len(model['excluded']),3)
        self.assertEqual({r['path'] for r in model['routes'] if r['operation_id']=='postAsk'},{'/engine/v1/ask'})
        self.assertEqual(model,compile_source(HERE/'inference.alch'))
    def test_02_every_public_route_reaches_correct_upstream(self):
        for route in self.model['routes']:
            with self.subTest(method=route['method'],path=route['path']):
                path=route['path']
                for key,value in [('subnet_id','fixture'),('id','42'),('miner','fixture'),('proxyPath','nested/predict')]:path=path.replace('{'+key+'}',value)
                result=self.request(route['method'],path+'?units=metric&x=a%2Bb',b'{"query":"fixture"}',{'PAYMENT-SIGNATURE':'fixture-proof'})
                self.assertEqual(result[0],200)
                self.assertEqual(SEEN[-1]['path'],path+'?units=metric&x=a%2Bb');self.assertEqual(SEEN[-1]['method'],route['method'])
    def test_03_x402_challenge_and_proof_roundtrip(self):
        first=self.request('POST','/engine/v1/ask',b'{"query":"hello"}')
        self.assertEqual(first[0],402);self.assertEqual(first[1]['PAYMENT-REQUIRED'],'fixture-challenge');self.assertEqual(json.loads(first[2])['accepts'][0]['price'],'10000')
        second=self.request('POST','/engine/v1/ask',b'{"query":"hello"}',{'PAYMENT-SIGNATURE':'fixture-proof'})
        self.assertEqual(second[0],200);self.assertEqual(second[1]['PAYMENT-RESPONSE'],'fixture-receipt')
        self.assertEqual(json.loads(second[2])['miner_used'],'fixture-miner')
    def test_04_binary_payload_preserved(self):
        payload=b'\x00\xff\r\n--boundary\r\n'
        self.assertEqual(self.request('POST','/miner-dispatcher/v1/fixture/upload',payload,{'Content-Type':'multipart/form-data; boundary=boundary'})[0],200)
        self.assertEqual(SEEN[-1]['body'],payload)
    def test_05_stream_is_not_buffered_until_end(self):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        conn.request('POST','/miner-dispatcher/v1/fixture/stream',b'{}');r=conn.getresponse();start=time.monotonic()
        self.assertEqual(r.read(13),b'data: first\n\n');self.assertLess(time.monotonic()-start,.4)
        self.assertEqual(r.read(),b'data: [DONE]\n\n');conn.close()
    def test_06_internal_identity_headers_not_forwarded(self):
        self.request('POST','/engine/v1/ask',b'{}',{'X-Internal-Secret':'never-forward','Authorization':'Bearer private','X-Forwarded-For':'127.0.0.1','PAYMENT-SIGNATURE':'fixture-proof'})
        headers={k.lower():v for k,v in SEEN[-1]['headers'].items()}
        self.assertNotIn('x-internal-secret',headers);self.assertNotIn('authorization',headers);self.assertNotIn('x-forwarded-for',headers)
    def test_07_internal_and_websocket_routes_excluded(self):
        before=len(SEEN)
        self.assertEqual(self.request('POST','/miner-dispatcher/validate',b'{}')[0],404)
        self.assertEqual(self.request('GET','/engine/ws',headers={'Upgrade':'websocket'})[0],501)
        self.assertEqual(len(SEEN),before)
    def test_08_no_retry_after_unknown_outcome(self):
        before=len(SEEN);result=self.request('POST','/miner-dispatcher/v1/fixture/disconnect',b'{}',{'PAYMENT-SIGNATURE':'fixture-proof'})
        self.assertEqual(result[0],502);self.assertEqual(len(SEEN)-before,1)
    def test_09_no_redirect_following(self):
        before=len(SEEN);result=self.request('POST','/miner-dispatcher/v1/fixture/redirect',b'{}')
        self.assertEqual(result[0],307);self.assertEqual(result[1]['Location'],'https://unrelated.invalid/private');self.assertEqual(len(SEEN)-before,1)
    def test_10_traversal_rejected(self):
        before=len(SEEN)
        for path in ['/engine/../private','/engine/%2e%2e/private','/engine/%252e%252e/private']:
            self.assertEqual(self.request('GET',path)[0],400)
        self.assertEqual(len(SEEN),before)
    def test_11_upstream_configuration_is_bounded(self):
        for value in ['http://example.com/engine','https://user:secret@example.com/engine','https://example.com/engine?secret=value']:
            with self.assertRaises(ValueError):application(HERE/'inference.alch',{'TELEGRAPH_ENGINE_URL':value})
    def test_12_missing_backend_does_not_fabricate_result(self):
        original=self.model['integrations']['Engine']['url'];self.model['integrations']['Engine']['url']=None
        try:self.assertEqual(self.request('POST','/engine/v1/ask',b'{}')[0],503)
        finally:self.model['integrations']['Engine']['url']=original
    def test_13_reject_unknown_language_clause_and_contract_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);shutil.copytree(HERE/'contracts',path/'contracts');source=path/'bad.alch'
            for text in [(HERE/'inference.alch').read_text().replace('transport http-proxy','transport javascript'),(HERE/'inference.alch').read_text().replace('./contracts/engine.json','../engine.json')]:
                source.write_text(text)
                with self.assertRaises(ValueError):compile_source(source)
    def test_14_request_limit_before_forwarding(self):
        before=len(SEEN);self.model['integrations']['Engine']['max-request-bytes']=2
        try:self.assertEqual(self.request('POST','/engine/v1/ask',b'123')[0],413)
        finally:self.model['integrations']['Engine']['max-request-bytes']=10485760
        self.assertEqual(len(SEEN),before)

if __name__=='__main__':unittest.main(verbosity=2)
