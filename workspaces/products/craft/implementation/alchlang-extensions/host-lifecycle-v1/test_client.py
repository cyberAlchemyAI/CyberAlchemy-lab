import contextlib
import http.server
import io
import json
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
import client
TOKEN='local_service_fixture_'*3
REV='a'*32

class ClientTests(unittest.TestCase):
    def setUp(self):
        self.calls=[];self.responses=[];owner=self
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self,*_):pass
            def handle_request(self):
                body=self.rfile.read(int(self.headers.get('Content-Length','0')))
                owner.calls.append((self.command,self.path,json.loads(body) if body else None))
                status,value=owner.responses.pop(0) if owner.responses else (200,{'status':'queued'})
                if status is None:self.connection.close();return
                data=value if isinstance(value,bytes) else json.dumps(value).encode()
                self.send_response(status);self.send_header('Content-Length',str(len(data)));self.end_headers()
                try:self.wfile.write(data)
                except OSError:pass
            do_GET=handle_request;do_POST=handle_request
        self.server=http.server.HTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.c=client.Client('http://127.0.0.1:'+str(self.server.server_port),TOKEN)
    def tearDown(self):self.server.shutdown();self.thread.join();self.server.server_close()

    def test_build_wait_never_activates(self):
        self.responses=[(202,{'revision':REV,'status':'queued'}),(200,{'status':'building'}),(200,{'status':'ready','id':REV})]
        self.assertEqual(self.c.build('shop','profile semantic-host-v1')['revision'],REV)
        self.assertEqual(self.c.wait_ready('shop',REV,1,.05)['status'],'ready')
        self.assertEqual([c[0] for c in self.calls],['POST','GET','GET'])
        self.assertFalse(any('activate' in p for _,p,_ in self.calls))
    def test_wait_is_bounded_and_failed_build_is_terminal(self):
        with self.assertRaisesRegex(client.ClientError,'BUILD_WAIT_TIMEOUT'):self.c.wait_ready('shop',REV,.12,.05)
        self.assertLessEqual(len(self.calls),3)
        self.responses=[(200,{'status':'failed'})]
        with self.assertRaisesRegex(client.ClientError,'BUILD_FAILED'):self.c.wait_ready('shop',REV)
    def test_invocation_unknown_outcome_has_no_retry(self):
        self.responses=[(None,None)]
        with self.assertRaisesRegex(client.ClientError,'OUTCOME_UNKNOWN'):
            self.c.invoke('shop','orders-local',{'facts':{},'message_id':'m1','expected_version':0})
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.calls[0][2]['message_id'],'m1')
    def test_http_denial_redirect_and_bad_protocol(self):
        self.responses=[(403,{'error':'FORBIDDEN'}),(302,{'error':'REDIRECT'}),(200,b'not-json')]
        for code in ['FORBIDDEN','REDIRECT','RESPONSE_PROTOCOL']:
            with self.assertRaisesRegex(client.ClientError,code):self.c.project('shop')
        self.assertEqual(len(self.calls),3)
    def test_functions_are_selection_metadata_not_liveness(self):
        self.responses=[(200,{'routes':[{'function':'orders-local','revision':REV}],'revisions':[{'id':REV,'status':'ready','source':'source-sha','artifact':'artifact-sha'}]})]
        value=self.c.functions('shop')['functions'][0]
        self.assertEqual(value['selection'],'selected');self.assertNotIn('running',value)
    def test_invalid_identifiers_and_envelopes_reject_locally(self):
        for body in [{},{'facts':{},'message_id':'m','expected_version':True}]:
            with self.assertRaises(client.ClientError):self.c.invoke('shop','orders-local',body)
        with self.assertRaises(client.ClientError):self.c.project('../other')
        with self.assertRaises(client.ClientError):self.c.revision('shop','../other')
        with self.assertRaises(client.ClientError):client.Client('http://example.com',TOKEN)
        with self.assertRaises(client.ClientError):client.Client('http://127.0.0.1', 'short')
        self.assertEqual(self.calls,[])
    def test_cli_errors_do_not_expose_token(self):
        self.responses=[(401,{'error':'UNAUTHORIZED'})];err=io.StringIO()
        with patch.dict(os.environ,{'ALCH_SERVICE_TOKEN':TOKEN}),contextlib.redirect_stderr(err):
            code=client.main(['--url',f'http://127.0.0.1:{self.server.server_port}','functions','shop'])
        self.assertEqual(code,1);self.assertNotIn(TOKEN,err.getvalue());self.assertEqual(json.loads(err.getvalue())['error'],'UNAUTHORIZED')

    def test_control_wait_only_polls_get(self):
        self.responses=[(202,{'request_id':'one','status':'queued'}),(200,{'request_id':'one','status':'running'}),(200,{'request_id':'one','status':'succeeded'})]
        self.c.control('shop','orders-local','drain','a'*64,'one')
        self.assertEqual(self.c.wait_control('shop','orders-local','one',1)['status'],'succeeded')
        self.assertEqual([c[0] for c in self.calls],['POST','GET','GET'])
    def test_unknown_control_preserves_cli_request_id(self):
        self.responses=[(None,{})];err=io.StringIO()
        with patch.dict(os.environ,{'ALCH_SERVICE_TOKEN':TOKEN}),contextlib.redirect_stderr(err):
            result=client.main(['--url','http://127.0.0.1:'+str(self.server.server_port),'restart','shop','orders-local','--expected','a'*64,'--request-id','stable'])
        self.assertEqual(result,1);self.assertEqual(json.loads(err.getvalue())['request_id'],'stable')
        self.assertEqual(len(self.calls),1);self.assertNotIn(TOKEN,err.getvalue())
    def test_bad_control_fields_rejected_locally(self):
        with self.assertRaisesRegex(client.ClientError,'FENCE_REQUIRED'):self.c.control('shop','orders-local','drain','bad','one')
        self.assertEqual(self.calls,[])
    def test_blocked_control_is_terminal(self):
        self.responses=[(200,{'status':'blocked','reason':'DRAIN_TIMEOUT'})]
        self.assertEqual(self.c.wait_control('shop','orders-local','one',1)['status'],'blocked')

if __name__=='__main__':unittest.main(verbosity=2)
