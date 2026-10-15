"""New-process verification of frozen bytes and exact independently scoped effects."""
import argparse
from package import *

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--package',required=True);parser.add_argument('--manifest-sha256',required=True)
 args=parser.parse_args();require(binding(HERE/'manifest.json')['sha256']==args.manifest_sha256,'independent source manifest pin differs')
 output=Path(args.package);require(output.is_absolute(),'absolute selected package required')
 result=validate(original(binding(output/'preparation.json')),output)
 print(encoded({**result,'source_manifest_binding':binding(HERE/'manifest.json'),'preparation_binding':binding(output/'preparation.json'),
  'fresh_process':True,'temporary_store_created':False,'private_key_created':False,'candidate_only':True}).decode(),end='')
