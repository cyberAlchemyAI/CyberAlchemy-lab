"""Synthetic public-only checked Reader import inside the selected image."""
import importlib.metadata
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import types

PORTABLE_SHA='86863b6d4a82678a93ede709edab9285834839c69a7cebba25c50495da66cfff'
PORTABLE_PATH=Path(__file__).resolve().parent/'portable.py'
portable_raw=PORTABLE_PATH.read_bytes()
if hashlib.sha256(portable_raw).hexdigest()!=PORTABLE_SHA:
    raise RuntimeError('PORTABLE_CONTROL_CODE_DRIFT')
portable=types.ModuleType('portable_checked_control')
portable.__file__=str(PORTABLE_PATH)
exec(compile(portable_raw,portable.__file__,'exec'),portable.__dict__)

def forbid_private(event,args):
    if event in ('open','os.open') and args and 'branch.snapshot' in str(args[0]):
        raise RuntimeError('PRIVATE_ARCHIVE_PROBE_REFUSAL')

def main(argv):
    if len(argv)!=2:raise RuntimeError('expected bundle path and manifest digest')
    bundle=Path(argv[0]);digest=argv[1]
    if not bundle.is_absolute():raise RuntimeError('BUNDLE_ABSOLUTE_REQUIRED')
    env={'python':platform.python_version(),
         'jsonschema':importlib.metadata.version('jsonschema'),
         'cryptography':importlib.metadata.version('cryptography')}
    if env!={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}:
        raise RuntimeError('SELECTED_IMAGE_ENVIRONMENT_DRIFT')
    if (os.getuid(),os.getgid())!=(1000,1000):
        raise RuntimeError('SELECTED_IMAGE_UID_DRIFT')
    sys.addaudithook(forbid_private)
    loader,capture,manifest=portable.reconstruct(
        bundle,digest,portable.SELECTED_ROOT,portable.IMAGE_SITE)
    with loader.checked_modules(capture) as (reader,finder):
        if reader.SelectedReader.__module__!=loader.READER_NAME+'.reader':
            raise RuntimeError('ORIGINAL_READER_NOT_BUFFER_LOADED')
        names=[name for name,_,_ in finder.executed]
        if (len(names)<13 or loader.SOURCE_NAME not in names or
                loader.ENGINE_LOADER_NAME not in names or loader.BRIDGE_NAME not in names):
            raise RuntimeError('DYNAMIC_CODE_CLOSURE_MISSING')
    return {'schema':'context-portable-reader-image-probe/v1-synthetic',
            'status':'ORIGINAL_READER_CLASS_LOADED_FROM_BUFFERS',
            'image_environment':env,'uid':os.getuid(),'gid':os.getgid(),
            'selected_stage_path':str(portable.SELECTED_ROOT),
            'code_buffers':len(manifest['code']),
            'metadata_buffers':len(manifest['metadata']),
            'executed_buffer_count':len(names),
            'signed_open':'NOT_RUN','private_archive':'ABSENT',
            'effect':'NOT_RUN'}

if __name__=='__main__':
    print(json.dumps(main(sys.argv[1:]),sort_keys=True,separators=(',',':')))
