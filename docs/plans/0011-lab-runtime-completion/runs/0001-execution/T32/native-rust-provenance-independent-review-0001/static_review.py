"""Independent public source/cache/metadata review. No compiler/native execution."""
import hashlib,json,os,re,stat,tomllib
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-rust-provenance-preparation-0001'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_bytes())
def actual(row):
 p=Path(row['path']);p=p if p.is_absolute()else ROOT/p;s=p.lstat();raw=p.read_bytes()
 assert stat.S_ISREG(s.st_mode)and not p.is_symlink()and sha(raw)==row['sha256']and len(raw)==row['size_bytes']
 return raw

def main():
 assert sha((P/'source-manifest.json').read_bytes())=='a99cb73ddba11c9fb095860be6510e0acb301cd29f0a6c9dc776e6c99792d310'
 mf=load(P/'source-manifest.json');assert len(mf['files'])==116
 for r in mf['files']:actual(r)
 inputs=load(P/'input-selection.json');assert len(inputs['files'])==110
 for r in inputs['files']:actual(r)
 cache=load(P/'offline-cache-selection.json');assert len(cache['packages'])==cache['package_count']==32
 lock=tomllib.loads(actual(cache['lock_binding']).decode());locked={(r['name'],r['version']):r for r in lock['package']if 'source'in r};assert len(locked)==32
 for r in cache['packages']:
  row=locked[(r['package'],r['version'])];assert row['source']=='registry+https://github.com/rust-lang/crates.io-index'and row['checksum']==r['lock_checksum']==r['archive_binding']['sha256']
  actual(r['archive_binding']);index=actual(r['index_binding']);records=[]
  for token in index.split(b'\0'):
   if token.startswith(b'{'):
    try:v=json.loads(token)
    except (ValueError,UnicodeDecodeError):continue
    if v.get('name')==r['package']and v.get('vers')==r['version']:records.append(v)
  assert len(records)==1 and records[0]['cksum']==row['checksum']
  assert r['archive_destination']=='registry/cache/index.crates.io-1949cf8c6b5b557f/'+r['package']+'-'+r['version']+'.crate'
  assert r['index_destination']=='registry/index/index.crates.io-1949cf8c6b5b557f/.cache/'+r['index_binding']['path'].split('/.cache/',1)[1]
 config=json.loads(actual(cache['index_config']['source_binding']));assert config['dl']=='https://static.crates.io/crates'and cache['index_config']['destination']=='registry/index/index.crates.io-1949cf8c6b5b557f/config.json'
 proposal=load(P/'ROOT-COMMAND-PROPOSAL.json');assert len(proposal['commands'])==5 and proposal['active']is False
 commands=proposal['commands'];env=commands[0]['environment'];assert all(c['environment']==env and c['cwd']==str(ROOT)for c in commands)
 assert set(env)=={'CARGO','CARGO_HOME','CARGO_NET_OFFLINE','CC','CXX','LC_ALL','PATH','PYTHONDONTWRITEBYTECODE','PYTHONNOUSERSITE','RUSTC','RUSTDOC','TMPDIR','XDG_DATA_HOME'}
 assert env['CARGO_NET_OFFLINE']=='true'and env['PATH']=='/usr/bin:/bin'
 assert all(c['argv'][:11]==commands[0]['argv'][:11]for c in commands)
 assert commands[0]['argv'][12:]==['-vV']and commands[1]['argv'][12:]==['-vV']
 assert commands[0]['argv'][11]==env['RUSTC']and all(c['argv'][11]==env['CARGO']for c in commands[1:])
 for c in commands[2:]:
  assert '--offline'in c['argv']and '--locked'in c['argv']and '--manifest-path'in c['argv']and '--target-dir'in c['argv']and '-vv'in c['argv']
 assert '--test-threads=1'in commands[3]['argv']and commands[2]['argv'][12]=='build'and commands[3]['argv'][12]=='test'and commands[4]['argv'][12]=='build'
 assert commands[2]['argv'][commands[2]['argv'].index('--target-dir')+1]!=commands[4]['argv'][commands[4]['argv'].index('--target-dir')+1]
 production=ROOT/'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/production'
 tests=[]
 for path in sorted((production/'tests').glob('*.rs')):
  tests += re.findall(r'#\[test\]\s*fn\s+([A-Za-z_][A-Za-z0-9_]*)',path.read_text())
 expected=inputs['original_test_names'];assert len(tests)==23
 if type(expected)is dict:assert sorted(tests)==sorted(x for names in expected.values()for x in names)
 else:assert sorted(tests)==sorted(expected)
 obs=load(P/'observations.json');historical=actual(obs['original23_retained_regression_stdout_binding']).decode()
 for name in tests:assert 'test '+name+' ... ok'in historical
 assert 'observer/src/lib.rs'in actual(obs['depfile_discrepancy']['binding']).decode()
 assert obs['historical480_present']is False and not Path(obs['historical480_path']).exists()
 assert not Path(proposal['owned_root']['path']).exists()
 for r in mf['files']:actual(r)
 return {'result':'PASS-inactive-proposal-review','all116_manifest_and110_input_SHA_size_regular_leaf_checks':True,'all32_archive_lock_checksums_and_exact_index_version_checksums':True,'index_config_verified':True,'five_explicit_argv_and_identical_closed_envs':True,'original23_source_names_exact':sorted(tests),'historical23_stdout_all_names_PASS_not_current_execution':True,'old480_absent_distinct574':True,'stale_observer_depfile_preserved':True,'fresh_owned_root_currently_absent':True,'compiler_Cargo_native_or_Source_guard_executed':False}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
