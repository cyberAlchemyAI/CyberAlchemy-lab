"""Guard every source before any host/key/native/read-workspace effects."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['build','checks']);ap.add_argument('--source-sha256',required=True);ap.add_argument('--package-sha256');ap.add_argument('--mapped-package-sha256',required=True);a=ap.parse_args()
    raw=(HERE/'source-manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=a.source_sha256:raise ValueError('independent Context source pin differs')
    m=json.loads(raw)
    for row in m['files']:
        p=ROOT/row['path']
        if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Context source bytes changed '+row['path'])
    name='_cal_current_context_delivery_v6';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    selected=__import__(name+'.'+a.mode,fromlist=['build','main'])
    if a.mode=='build':selected.build(a.source_sha256,a.mapped_package_sha256)
    else:selected.main(a.source_sha256,a.package_sha256,a.mapped_package_sha256)
if __name__=='__main__':main()
