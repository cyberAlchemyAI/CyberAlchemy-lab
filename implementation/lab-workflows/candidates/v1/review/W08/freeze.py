"""Freeze original byte closure; parse JSON sources only, retain Markdown bytes."""
from packet import *


def freeze():
    files={}
    def add(b):
        bound(b);require(b['path'] not in files or files[b['path']]==b['sha256'],'conflicting source closure')
        files[b['path']]=b['sha256']
    context_binding={'path':str((RUN/'context-W08.json').relative_to(ROOT)),'sha256':CONTEXT_SHA};context=original(context_binding);add(context_binding)
    for b in context['source_bindings']:
        add(b)
        if b['path'].endswith('.json'):
            value=original(b)
            for r in value.get('files',[]):add({'path':r['path'],'sha256':r['sha256']})
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.name!='manifest.json' and 'receipts' not in p.parts:add(binding(p))
    path=HERE/'manifest.json'
    put(path,{'schema_version':'lab-W08-source-closure/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'files':[{'path':p,'sha256':s} for p,s in sorted(files.items())]})
    print(encoded({'result':'PASS','files':len(files),'source_drift':[],'manifest':binding(path)}).decode(),end='')


if __name__=='__main__':freeze()
