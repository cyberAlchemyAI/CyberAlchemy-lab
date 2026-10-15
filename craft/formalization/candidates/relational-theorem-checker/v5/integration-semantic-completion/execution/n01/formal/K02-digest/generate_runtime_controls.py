"""Generate exact byte cases; hashlib is a differential oracle, not a proof checker."""
from pathlib import Path
import hashlib,json,random
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
def bind(p): return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
 cases=[]
 def add(name,data,source=None):
  row={'name':name,'byte_length':len(data),'input_hex':data.hex(),'expected_sha256':hashlib.sha256(data).hexdigest()}
  if source:row['original_bytes']=bind(source)
  cases.append(row)
 add('empty',b'');add('abc',b'abc')
 add('nist-56-byte-message',b'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq')
 add('nist-112-byte-message',b'abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu')
 for n in [1,2,3,4,54,55,56,57,62,63,64,65,118,119,120,121,127,128,129,255,256,257,511,512,513,1024]:
  add(f'padding-and-block-boundary-{n}',bytes((17*i+91)%256 for i in range(n)))
 add('all-byte-values',bytes(range(256)))
 rnd=random.Random(2561804)
 for i in range(12):
  n=rnd.randrange(1,2049);add(f'deterministic-arbitrary-bytes-{i}',bytes(rnd.randrange(256) for _ in range(n)))
 for kind in ['resolution','role']:
  source=HERE.parent/'K02-pipeline/schemas'/f'{kind}-binding.fixture.json';data=source.read_bytes()
  add(f'original-{kind}',data,source)
  add(f'{kind}-truncated',data[:-1])
  add(f'{kind}-same-count-change',bytes([data[0]^1])+data[1:])
  add(f'{kind}-appended',data+b' ')
 index={'schema':'relational.digest-runtime-controls/v1','cases':cases,'oracle':'Python hashlib SHA-256','independent_proof_checker':False,'source_fixture_identity_roots_synthetic':True}
 (HERE/'runtime-control-index.json').write_text(json.dumps(index,indent=2)+'\n')
 lines=['import DigestControls','open RelationalSuccessor.CandidateDigest','open RelationalSuccessor.CandidateDigest.Controls']
 for i,row in enumerate(cases):
  data=bytes.fromhex(row['input_hex']);lit='['+','.join(map(str,data))+']'
  lines.append(f'def bytes{i} : Bytes := {lit}')
  lines.append(f'#eval (digestBytes bytes{i}).getD "REFUSED"')
 # Refusal tests use the unchanged submitted digest, rather than repairing it.
 refusal=[]
 for i,row in enumerate(cases):
  if row['name'].startswith('original-'):
   expected=json.dumps(row['expected_sha256']);n=row['byte_length'];refusal.append({'name':row['name']+'-unchanged','expected':'RelationalSuccessor.CandidateDigest.Outcome.verified'})
   lines.append(f'#eval classifyDigest fixtureProfile fixtureRef bytes{i} {expected} {n}')
   for offset in [1,2,3]:
    refusal.append({'name':cases[i+offset]['name']+'-old-submitted-digest','expected':'RelationalSuccessor.CandidateDigest.Outcome.digestMismatch'})
    lines.append(f'#eval classifyDigest fixtureProfile fixtureRef bytes{i+offset} {expected} {n+1}')
 index['refusal_cases']=refusal;(HERE/'runtime-control-index.json').write_text(json.dumps(index,indent=2)+'\n')
 (HERE/'DigestRuntimeControls.lean').write_text('\n'.join(lines)+'\n')
 print(json.dumps({'digest_cases':len(cases),'unchanged-and-altered-submitted-digest_cases':len(refusal)}))
if __name__=='__main__':run()
