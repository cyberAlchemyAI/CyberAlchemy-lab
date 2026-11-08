# Read-only discovery on the selected instance. No environment or credentials read.
# Open Questions: README.md.
import json, urllib.request, concurrent.futures
ports = set()
for path in ['/proc/net/tcp', '/proc/net/tcp6']:
    try:
        with open(path) as f:
            for line in list(f)[1:]:
                fields = line.split()
                if fields[3] == '0A':
                    ports.add(int(fields[1].split(':')[1], 16))
    except FileNotFoundError:
        pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def probe(port):
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        with opener.open('http://127.0.0.1:%d/v1/models' % port, timeout=1.5) as r:
            body = r.read(65537)
            if len(body) > 65536 or r.status != 200:
                return None
            data = json.loads(body).get('data')
            if not isinstance(data, list) or not 0 < len(data) <= 100:
                return None
            models = [{'id': m['id'], 'max_model_len': m.get('max_model_len')} for m in data
                      if isinstance(m, dict) and isinstance(m.get('id'), str) and 0 < len(m['id']) <= 128]
            return {'port': port, 'models': models} if models else None
    except Exception:
        return None
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    print(json.dumps([r for r in pool.map(probe, sorted(ports)[:64]) if r]))
