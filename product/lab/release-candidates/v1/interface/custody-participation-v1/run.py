"""Guard the entire source before importing candidate modules or causing effects."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['build','checks','eligibility','cold'])
    ap.add_argument('--source-sha256',required=True);ap.add_argument('--package-sha256');a=ap.parse_args()
    path=HERE/'source-manifest.json';raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=a.source_sha256:raise RuntimeError('independent source pin differs')
    m=json.loads(raw)
    for row in m['files']:
        p=ROOT/row['path']
        if not p.is_file() or p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise RuntimeError('source changed '+row['path'])
    name='_cal_original_participation_v1';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    target=__import__(name+'.'+{'build':'build','checks':'checks','eligibility':'eligibility_checks','cold':'cold'}[a.mode],fromlist=['main'])
    target.main(a.source_sha256,a.package_sha256)
if __name__=='__main__':main()
