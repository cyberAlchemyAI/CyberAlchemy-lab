"""Frozen sources are selected independently of public request data."""
import importlib.util
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5];BASE=HERE.parent/'api-integration-v6'
BASE_SOURCE='7ab054776a5fa8fd310f60e126a29c98686d159f989fb3a721cb6dcd1f1f119f'
BASE_PROFILE='d832f9c20e487261d9987906408dfbd54c7f6cf624890f9144d750d7eb8a053f'
def package(name,path):
 if name not in sys.modules:
  spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
  m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 return name
BASE_NAME=package('_cal_governance_0148_base',BASE)
P=__import__(BASE_NAME+'.protocol',fromlist=['*']);G=__import__(BASE_NAME+'.guard',fromlist=['*']);W=__import__(BASE_NAME+'.workspace',fromlist=['privacy'])
NATIVE=HERE.parent/'runtime-byte-custody-v3/runtime'
NATIVE_NAME=package('_cal_governance_0148_native',NATIVE/'lab_runtime')
S=__import__(NATIVE_NAME+'.store',fromlist=['*']);C=__import__(NATIVE_NAME+'.common',fromlist=['*'])
O=__import__(NATIVE_NAME+'.operations',fromlist=['*']);U=__import__(NATIVE_NAME+'.custody',fromlist=['*'])
KERNEL=HERE.parent/'checkpoint-resolution-v1'
KERNEL_NAME=package('_cal_governance_0148_checkpoint',KERNEL)
K=__import__(KERNEL_NAME+'.kernel',fromlist=['*'])
OPERATIONS=('checkpoint.resolve','admission.apply','capability.adoption.prepare')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return P.compact(v)
def parse(raw):return P.frame_parse(raw)
def binding(ref,raw):return {'ref':ref,'sha256':sha(raw)}
def now():return datetime.now(timezone.utc)
def iso(v):return v.isoformat()
def instant(v):return K.instant(v)
def guard(pin):
 C.require(sha((BASE/'source-manifest.json').read_bytes())==BASE_SOURCE,'frozen full parent source pin differs')
 raw=(HERE/'source-manifest.json').read_bytes();C.require(sha(raw)==pin,'governance source pin differs')
 m=parse(raw);G._verify_files(ROOT,m['files'])
 C.require(sha((BASE/'contract-profile.json').read_bytes())==BASE_PROFILE,'base profile differs')
 C.require((HERE/'source-manifest.json').read_bytes()==raw,'governance manifest changed during guard')
