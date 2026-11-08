"""Persist an explicitly selected original ScopeIndex inside a fresh Vault.

The index and all original contract/proof/lineage/receipt bytes remain unchanged.
The actual scoped store validates their semantics against the actual journal.
"""
import importlib
import json
import os
from pathlib import Path
import sys
import retained as R
ROOT=Path(__file__).resolve().parents[4];FOLDER=ROOT/'implementation/lab-runtime/local-host/t31-scoped-output-0001'

def modules():
    sys.path.insert(0,str(FOLDER))
    result={name:importlib.import_module(name)for name in ('scoped_store','scoped_currentness','scoped_headers','scoped_kernel')}
    for name,module in result.items():
        path=FOLDER/(name+'.py');R.need(Path(module.__file__)==path and not path.is_symlink() and not any(p.is_symlink()for p in path.parents),
                                      'exact selected scoped workflow module origin required')
    return result

def capture(binding):
    R.need(type(binding)is dict and set(binding)=={'ref','sha256'},'closed independently selected ScopeIndex binding required')
    path=Path(binding['ref']);raw=R.read(path);R.need(R.sha(raw)==binding['sha256'],'independently selected ScopeIndex original differs');index=json.loads(raw)
    R.need(type(index)is dict and set(index)=={'schema_version','journal_config_sha256','scope_ref','run_ref','actor','work','source_cut','members','entries','authority_effect'}
           and index['schema_version']=='lab-owned-native-scope-index/v1' and index['authority_effect']=='none'
           and type(index['members'])is list and index['members'] and type(index['entries'])is list and index['entries'],
           'closed actual persisted native ScopeIndex required')
    originals={};refs=set();paths=set()
    for row in index['members']:
        R.need(type(row)is dict and set(row)=={'ref','path','sha256'},'closed actual native scope evidence member required')
        relative=R.relative(row['path']);R.need(row['ref']not in refs and str(relative)not in paths and str(relative)!='scope-index.json',
                                            'duplicate or shadowed native scope evidence original')
        refs.add(row['ref']);paths.add(str(relative));body=R.read(path.parent/relative)
        R.need(R.sha(body)==row['sha256'] and b'PRIVATE KEY-----'not in body,'actual native scope original member differs');originals[str(relative)]=body
    return raw,index,originals

def persist(binding,*,vault,manifest):
    raw,index,originals=capture(binding);vault=Path(vault);folder=vault/'inputs/scope-evidence'
    R.need(not folder.exists() and (vault/'inputs').is_dir(),'fresh private scope evidence custody required');folder.mkdir(mode=0o700)
    def write(path,original):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb')as stream:stream.write(original);stream.flush();os.fsync(stream.fileno())
    write(folder/'scope-index.json',raw)
    for name,body in originals.items():write(folder/R.relative(name),body)
    rows=[{'ref':'owned-fixture:scope-index','path':'inputs/scope-evidence/scope-index.json','sha256':R.sha(raw)}]
    rows.extend({'ref':row['ref'],'path':'inputs/scope-evidence/'+row['path'],'sha256':row['sha256']}for row in index['members'])
    old={row['ref']for row in manifest['materials']};R.need(not old&{row['ref']for row in rows},'scope evidence reference collides with existing private input')
    manifest['materials'].extend(rows)
    R.need(capture(binding)==(raw,index,originals),'actual native scope evidence changed during copy')
    new_binding={'ref':str(folder/'scope-index.json'),'sha256':R.sha(raw)}
    R.need(capture(new_binding)==(raw,index,originals),'persisted exact native scope evidence copy differs')
    selected=modules()['scoped_store'].ScopeSelection.from_host(folder/'scope-index.json',R.sha(raw))
    return selected,{'ref':'owned-fixture:scope-index','sha256':R.sha(raw)}
