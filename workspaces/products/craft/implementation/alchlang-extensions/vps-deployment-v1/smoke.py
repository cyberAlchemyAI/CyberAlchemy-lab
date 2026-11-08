"""Authenticated end-to-end service test. Token comes from a file, never stdout."""
import argparse,http.client,json,ssl,time
from pathlib import Path
from urllib.parse import urlsplit
p=argparse.ArgumentParser();p.add_argument('--url',required=True);p.add_argument('--token-file',required=True);p.add_argument('--source',required=True);p.add_argument('--mode',choices=['create','verify'],default='create');p.add_argument('--receipt',required=True)
a=p.parse_args();url=urlsplit(a.url);token=Path(a.token_file).read_text().strip()
def request(method,path,body=None,auth=True):
 cls=http.client.HTTPSConnection if url.scheme=='https' else http.client.HTTPConnection
 conn=cls(url.hostname,url.port,timeout=120)
 try:
  headers={'Content-Type':'application/json'}
  if auth:headers['Authorization']='Bearer '+token
  conn.request(method,path,None if body is None else json.dumps(body),headers)
  r=conn.getresponse();raw=r.read();return r.status,json.loads(raw)
 finally:conn.close()
def good(result,status=200):
 assert result[0]==status,result
 return result[1]
def state():return good(request('GET','/v1/projects/deployment-smoke/functions/orders-local/status'))
def control(action,id):
 good(request('POST','/v1/projects/deployment-smoke/functions/orders-local/'+action,{'request_id':id,'expected':state()['expected']}),202)
 deadline=time.monotonic()+100
 while time.monotonic()<deadline:
  value=good(request('GET','/v1/projects/deployment-smoke/functions/orders-local/requests/'+id))
  if value['status'] in ('succeeded','blocked','failed','outcome_unknown'):
   assert value['status']=='succeeded',value;return value
  time.sleep(.2)
 raise AssertionError('control timeout')
assert request('POST','/v1/projects/deployment-smoke',{},auth=False)[0]==401
body={'facts':{'orderId':'deployment-smoke-order','payload':{'purpose':'deployment verification'}},'message_id':'deployment-smoke-message','expected_version':0}
if a.mode=='create':
 good(request('POST','/v1/projects/deployment-smoke',{}))
 build=good(request('POST','/v1/projects/deployment-smoke/revisions',{'source':Path(a.source).read_text()}),202)
 revision=build['revision'];deadline=time.monotonic()+260
 while time.monotonic()<deadline:
  result=good(request('GET','/v1/projects/deployment-smoke/revisions/'+revision))
  if result['status']=='ready':break
  assert result['status']!='failed',result
  time.sleep(.5)
 assert result['status']=='ready',result
 good(request('POST',f'/v1/projects/deployment-smoke/revisions/{revision}/prepare',{}))
 good(request('POST',f'/v1/projects/deployment-smoke/revisions/{revision}/activate',{}))
 for _ in range(50):
  result=request('POST','/v1/projects/deployment-smoke/functions/orders-local/invoke',body)
  if result[0]!=503:break
  time.sleep(.1)
 assert good(result)['status']=='committed'
 deadline=time.monotonic()+15
 while state()['delivery']['published']<1 and time.monotonic()<deadline:time.sleep(.2)
 assert state()['delivery']['published']==1
 control('drain','smoke-drain');assert state()['health']=='drained'
 control('restart','smoke-restart');assert state()['health']=='drained'
else:
 assert state()['health']=='drained',state()
 control('resume','smoke-resume')
 for _ in range(50):
  result=request('POST','/v1/projects/deployment-smoke/functions/orders-local/invoke',body)
  if result[0]!=503:break
  time.sleep(.1)
 assert good(result)['status']=='already-committed',result
receipt={'status':'PASS','mode':a.mode,'url':a.url,'anonymous_mutation_denied':True,'function':state()}
Path(a.receipt).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','mode':a.mode}))
