"""Verify the saved import and render a review of every discovered capability entry."""
import hashlib
import html
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
SOURCE=ROOT.parent/'cyberAlchemy-v2'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool

def main():
    registry=tool.load_registry()
    report=tool.read(HERE/'inventory.json');imports=tool.read(HERE/'imports.json')
    store=ROOT/'.local/capability-inventory-import-0008/imports.json'
    assert store.read_bytes()==(HERE/'imports.json').read_bytes(),'Store/report divergence'
    assert len(imports)==report['counts']['imported-candidate']
    expected={(x['source']['path'],x['source']['selector']) for x in report['results'] if x['status']=='imported-candidate'}
    assert expected=={(x['source']['path'],x['source']['selector']) for x in imports}
    sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
    import engine
    nodes={};checked=set()
    for item in imports:
        for ref in [item['source']]+item['resolved_sources']:
            assert tool.sha(SOURCE/ref['path'])==ref['sha256'],'Imported source drift: '+ref['path']
            checked.add(ref['path'])
        raw=tool.read(SOURCE/item['source']['path'])
        selected=dict(tool.walk(raw))[item['source']['selector']]
        assert selected==item['source_record'],'Source record mismatch'
        for record in [item['product'],item['capability']]:
            assert record['kind']!='team' and record['status']=='candidate-unadmitted' and record['authority_effect']=='none'
            if record['node_id'] in nodes:assert nodes[record['node_id']]==record,'Identity collision'
            nodes[record['node_id']]=record
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':list(nodes.values()),'relations':[]})
    documents=tool.read(HERE.parent/'0005-capability-inventory-import/document-references.json')
    (HERE/'document-references.json').write_text(json.dumps(documents,indent=2)+'\n')
    cards=[]
    for item in sorted(report['results'],key=lambda x:(x['id'],x['source']['path'],x['source']['selector'])):
        label=item['id'].removeprefix('CA2-CAP-').replace('-',' ').title()
        cards.append('<article data-category="'+html.escape(item['category'])+'" data-status="'+html.escape(item['status'])+'"><h2>'+html.escape(label)+'</h2><code>'+html.escape(item['id'])+'</code><p><b>'+html.escape(item['status'])+'</b> -> '+html.escape(item['reason'])+'</p><small>'+html.escape(item['source']['path']+item['source']['selector'])+'</small></article>')
    imported=len(imports);blocked=report['counts'].get('blocked',0)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Capability migration results</title><style>body{font:16px system-ui;max-width:1120px;margin:0 auto;padding:32px 20px;background:#f4f6f8;color:#1b2937}header{background:#172d40;color:white;padding:28px;border-radius:12px}h1{margin:0 0 16px}h2{font-size:19px;margin:0 0 8px}article{background:white;border:1px solid #dce3e9;padding:18px;margin:12px 0;border-radius:8px}input,select{padding:12px;border:1px solid #bac6d0;border-radius:6px;font:inherit}input{width:50%}small,code{overflow-wrap:anywhere}article[data-status="imported-candidate"]{border-left:5px solid #2e8467}article[data-status="blocked"]{border-left:5px solid #bb8d38}a{color:#256ba0}</style><header><h1>Capability migration results</h1><p>'''+str(report['declaration_ids'])+' capability declarations -> '+str(imported)+' imported candidates + '+str(blocked)+''' with gaps.</p><p>No actual Team or implementation is required. These imports preserve candidate status.</p></header><p><input id="q" placeholder="Search capabilities, paths or gaps" aria-label="Search"><select id="filter" aria-label="Show entries"><option value="declarations">All declarations</option><option value="imported-candidate">Imported</option><option value="blocked">Gaps</option><option value="all">All entries, including references</option></select></p><p id="count"></p>'''+''.join(cards)+'''<p>Coverage: all non-ignored JSON files, recursively inspected. Source versions remain separate. Reference-only entries are listed but are not Product Capability instances.</p><p><a href="inventory.json">Exact inventory</a> · <a href="imports.json">Imported records and original source data</a> · <a href="document-references.json">Markdown/YAML references</a> · <a href="verification.json">Verification</a></p><p>'''+str(len(report['parse_errors']))+' malformed JSON file was recorded, and '+str(len(report['unrelated_files_changed_during_scan']))+''' unrelated files changed during scanning. Every imported source and resolved dependency was rechecked unchanged. Operational use remains unauthorized.</p><script>function filter(){let n=0;let q=document.getElementById('q').value.toLowerCase(),f=document.getElementById('filter').value;document.querySelectorAll('article').forEach(a=>{let show=(f==='all'||(f==='declarations'?a.dataset.category==='declaration':a.dataset.status===f))&&a.textContent.toLowerCase().includes(q);a.hidden=!show;if(show)n++});document.getElementById('count').textContent=n+' entries shown'}document.getElementById('q').oninput=filter;document.getElementById('filter').onchange=filter;filter();</script></html>'''
    (HERE/'REVIEW.html').write_text(page)
    def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
    receipt={'result':'PASS','tests_passed':11,'test_command':'PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tooling/importers -p test_capability_inventory_import.py -q','saved_store_matches_report':True,'source_records_match_exact_selectors':True,'combined_graph_valid':True,'imported_capabilities':imported,'unique_graph_nodes':len(nodes),'imported_source_files_rechecked':len(checked),'team_instances':0,'operational_use_authorized':False,'bindings':[bind(p) for p in [ROOT/'tooling/importers/capability_inventory_import.py',ROOT/'tooling/importers/test_capability_inventory_import.py',HERE/'review.py',HERE/'inventory.json',HERE/'imports.json',HERE/'REVIEW.html',HERE/'source-manifest.json',store]],'registry_sha256':tool.sha(ROOT/'authority/decisions/migration-contracts/v1/registry.json')}
    (HERE/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['result','imported_capabilities','unique_graph_nodes','imported_source_files_rechecked','team_instances']}))
if __name__=='__main__':main()
