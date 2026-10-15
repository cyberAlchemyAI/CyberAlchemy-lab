import urllib.request,urllib.error,hashlib,json,concurrent.futures
from pathlib import Path
out=Path(__file__).resolve().parent
paths=['/','/craft','/bella','/agent-orchestration','/agent-orchestration-guide','/domainspec/','/domainspec/COMPLETE-GUIDE.html','/domainspec/COMPLETE-GUIDE.md','/domainspec/authority/definitions/index.html','/healthz']
def probe(path):
 url='https://cyberalchemize.com'+path
 try:response=urllib.request.urlopen(url,timeout=25)
 except urllib.error.HTTPError as e:response=e
 with response:
  body=response.read();return {'path':path,'status':response.status,'url':response.url,'sha256':hashlib.sha256(body).hexdigest(),'headers':{k.lower():v for k,v in response.headers.items()}}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(probe,paths))
assert all(r['status']==(401 if r['path'].startswith('/domainspec/') else 200) for r in rows)
(out/'public-before.json').write_text(json.dumps(rows,indent=2)+'\n');print([(r['path'],r['status']) for r in rows])
