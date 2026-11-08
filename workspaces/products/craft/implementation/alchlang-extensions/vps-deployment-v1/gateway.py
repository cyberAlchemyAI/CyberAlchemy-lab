"""Bounded transport proxy. Bearer authorization stays with the controller."""
import http.client,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import re,threading
slots=threading.BoundedSemaphore(16)
class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*_):pass
    def setup(self):super().setup();self.connection.settimeout(10)
    def reply(self,status,data,ctype='application/json'):
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(data)))
        self.send_header('Connection','close');self.send_header('Cache-Control','no-store');self.end_headers();self.close_connection=True
        try:self.wfile.write(data)
        except OSError:pass
    def run_request(self):
        if not slots.acquire(False):return self.reply(503,b'{"error":"GATEWAY_BUSY"}')
        conn=None
        try:
            if self.path=='/' and self.command=='GET':return self.reply(200,b'{"service":"Alch host","api":"/v1/projects","health":"/healthz","authentication":"Bearer token"}')
            if self.path=='/healthz' and self.command=='GET':
                conn=http.client.HTTPConnection('127.0.0.1',8080,timeout=2);conn.request('GET','/v1/projects/health');r=conn.getresponse();r.read(4096)
                return self.reply(200 if r.status==401 else 503,b'{"service":"alch-host"}')
            if not self.path.startswith('/v1/projects/'):return self.reply(404,b'{"error":"NOT_FOUND"}')
            auth=self.headers.get_all('Authorization',[])
            if len(auth)!=1 or not re.fullmatch(r'Bearer [A-Za-z0-9_-]{32,256}',auth[0]) or self.headers.get('Origin'):
                return self.reply(401,b'{"error":"UNAUTHORIZED"}')
            body=None
            if self.command=='POST':
                lengths=self.headers.get_all('Content-Length',[])
                if self.headers.get('Transfer-Encoding') or len(lengths)!=1 or not re.fullmatch('[0-9]{1,7}',lengths[0]):return self.reply(400,b'{"error":"CONTENT_LENGTH_REQUIRED"}')
                size=int(lengths[0])
                if size>262144:return self.reply(413,b'{"error":"REQUEST_TOO_LARGE"}')
                body=self.rfile.read(size)
                if len(body)!=size:return self.reply(400,b'{"error":"INCOMPLETE_BODY"}')
            conn=http.client.HTTPConnection('127.0.0.1',8080,timeout=120)
            conn.request(self.command,self.path,body,{'Authorization':auth[0],'Content-Type':self.headers.get('Content-Type','application/json')})
            response=conn.getresponse();data=response.read(1048577)
            if len(data)>1048576:return self.reply(502,b'{"error":"RESPONSE_LIMIT"}')
            self.reply(response.status,data,response.getheader('Content-Type','application/json'))
        except Exception:self.reply(502,b'{"error":"OUTCOME_UNKNOWN"}' if self.command=='POST' else b'{"error":"SERVICE_UNAVAILABLE"}')
        finally:
            if conn:conn.close()
            slots.release()
    do_GET=run_request
    do_POST=run_request
ThreadingHTTPServer(('0.0.0.0',8081),Handler).serve_forever()
