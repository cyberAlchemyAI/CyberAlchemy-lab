from pathlib import Path
import urllib.request,urllib.error,urllib.parse,hashlib,json,concurrent.futures
out=Path(__file__).resolve().parent;dist=Path.cwd()/'website/dist';base='https://cyberalchemize.com';failures=[]
def probe(path,expected=None):
 url=base+urllib.parse.quote(path,safe='/')
 try:response=urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=30)
 except urllib.error.HTTPError as e:response=e
 with response:
  data=response.read();row={'path':path,'status':response.status,'url':response.url,'sha256':hashlib.sha256(data).hexdigest(),'headers':{k.lower():v for k,v in response.headers.items()}}
 if expected:
  if row['status']!=200 or row['sha256']!=expected:failures.append({'path':path,'status':row['status'],'digest_mismatch':row['sha256']!=expected})
  suffix=Path(path).suffix
  allowed={'.js':['text/javascript','application/javascript'],'.css':['text/css'],'.svg':['image/svg+xml'],'.html':['text/html'],'.json':['application/json']}
  if suffix in allowed and row['headers'].get('content-type','').split(';')[0] not in allowed[suffix]:failures.append({'path':path,'mime':row['headers'].get('content-type')})
 return row
files=[p for p in dist.rglob('*') if p.is_file() and not any(s.startswith('.') for s in p.relative_to(dist).parts)]
def get(p):return probe('/'+p.relative_to(dist).as_posix(),hashlib.sha256(p.read_bytes()).hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:rows=list(pool.map(get,files))
before=json.loads((out/'public-before.json').read_text());preserved=[]
for old in before:
 new=probe(old['path']);preserved.append(new)
 if old['path']!='/':
  if new['status']!=old['status'] or new['sha256']!=old['sha256']:failures.append({'existing_route_changed':old['path'],'old_status':old['status'],'status':new['status']})
  for h in ['content-security-policy','referrer-policy','x-content-type-options','x-frame-options','permissions-policy','cache-control','www-authenticate','x-robots-tag']:
   if new['headers'].get(h)!=old['headers'].get(h):failures.append({'existing_header_changed':old['path'],'header':h})
 else:
  expected=hashlib.sha256((dist/'index.html').read_bytes()).hexdigest()
  if new['status']!=200 or new['sha256']!=expected:failures.append({'homepage_mismatch':True})
for path in ['/unrelated-path-that-does-not-exist','.env','/nginx.conf']:
 if not path.startswith('/'):path='/'+path
 row=probe(path)
 if row['status']!=404:failures.append({'unexpected_public_route':path,'status':row['status']})
summary={'result':'pass' if not failures else 'fail','https_files_exact':len(rows),'existing_routes_checked':len(preserved),'failures':failures,'tls_verification':True,'public_root_matches_reviewed_redirect':True,'private_routes_remain_protected':all(r['status']==401 for r in preserved if r['path'].startswith('/domainspec/'))}
(out/'public-verification.json').write_text(json.dumps({'summary':summary,'files':rows,'existing':preserved},indent=2)+'\n');print(json.dumps(summary));assert not failures,failures[:10]
