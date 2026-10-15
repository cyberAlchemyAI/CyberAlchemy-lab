"""Explicit frozen API source, shared types, exact byte and environment guards."""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
API=HERE.parent/'api-v18'
API_SOURCE='07a14881e21fe3c0db88ff55e0b3b982de05959cbd68a931efa89a2c3368e445'
API_PROFILE='fba4e67cada59ce70277ba2cfb09ece691193989bc20821ca4457eebcf5656ca'
NAME='_cal_review_package_api_v18'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
    module=importlib.util.module_from_spec(spec);sys.modules[NAME]=module;spec.loader.exec_module(module)
def imported(name):return __import__(NAME+'.'+name,fromlist=['*'])
P=imported('protocol');S=imported('service');M=imported('artifact_model');W=imported('workspace');G=imported('guard')
sha=P.source.sha;encoded=P.source.encoded;require=P.source.require
def guard(pin):
    path=HERE/'source-manifest.json';require(sha(path.read_bytes())==pin,'independent review kernel source pin differs')
    manifest=json.loads(path.read_bytes())
    require(manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None,'review preparation grants no owner authority')
    for row in manifest['files']:P.source.original(row)
    G.verify(API_SOURCE);return manifest
