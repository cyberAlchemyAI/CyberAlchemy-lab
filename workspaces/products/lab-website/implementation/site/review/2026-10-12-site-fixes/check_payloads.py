"""Verify identical complete search payloads in both delivery forms."""
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[3]
LAB=Path(os.environ.get('LAB_SITE_FIXES_SITE',str(ROOT/'website/dist')))/'governance-lab-series'
rows=[]
for name,variable,receipt in [('site-search-index','LabSiteSearchIndex',json.loads((LAB/'research/site-search-index.json').read_text())['delivery']),('reference-search-data','LabReferenceSearchText',json.loads((LAB/'research/reference-pages.json').read_text())['search_delivery'])]:
    script=(LAB/'assets'/f'{name}.js').read_text()
    encoded=json.loads(re.search(r'atob\(("[^"]+")\)',script)[1])
    decoded=gzip.decompress(base64.b64decode(encoded))
    fallback=(LAB/'assets'/receipt['fallback']).read_text()
    literal=fallback.split('window.'+variable+'=',1)[1].split(';\n',1)[0]
    raw=literal.encode('utf-8')
    assert decoded==raw,'Delivery forms differ: '+name
    assert hashlib.sha256(raw).hexdigest()==receipt['payload_sha256']
    assert hashlib.sha256((LAB/'assets'/receipt['fallback']).read_bytes()).hexdigest()==receipt['fallback_sha256']
    payload=json.loads(raw)
    rows.append({'name':name,'bytes':len(raw),'compressedScriptBytes':len(script.encode()),'samePayload':True,'entries':len(payload.get('entries',[])) if name=='site-search-index' else len(payload)})
output=ROOT/'website/output/playwright/ux-validator/20261012-site-fixes/measurements/payload-integrity.json'
output.write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
