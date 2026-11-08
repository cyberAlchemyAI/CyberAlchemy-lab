"""Create a private, allowlisted build context; never copy repository secrets or git state."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,tempfile,tomllib
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[7]
# Resolve the known repository anchor without relying on caller cwd.
REPO=next(p for p in HERE.parents if (p/'cyberAlchemy-v2/agent-routing/profile.json').is_file())
context=Path(tempfile.mkdtemp(prefix='alch-vps-image-'))
root=context/'rootfs';root.mkdir()
manifest=json.loads((HERE.parent/'host-lifecycle-v1/candidate-manifest.json').read_text())
files={}
drift=[]
for name,expected in manifest['files'].items():
    source=REPO/name
    current=hashlib.sha256(source.read_bytes()).hexdigest()
    if current!=expected:drift.append({'path':name,'previous':expected,'current':current})
    files[source]=current
(HERE/'source-drift.json').write_text(json.dumps({'status':'new-release-test-required','authority_effect':'none','changes':drift},indent=2)+'\n')
prov=REPO/'cyberAlchemy-v2/work-orchestration-implementation/extensions/alch-host-provisioning-v1'
for name,sha in json.loads((prov/'source-manifest.json').read_text())['sources'].items():files[REPO/name]=sha
for f in [REPO/'cyberAlchemy-v2/agent-routing/profile.json',prov/'source-manifest.json',prov/'bridge/target/debug/alch-provision-dag']:
    files[f]=hashlib.sha256(f.read_bytes()).hexdigest()
for name in ['cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/generatable-operation-patterns-v1/bindings/sqlite-transactional-outbox.binding-set.json','cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/package.json','projects/domainspec-v2/impl/cli/package.json']:
    f=REPO/name;files[f]=hashlib.sha256(f.read_bytes()).hexdigest()
for directory in [REPO/'cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist',REPO/'projects/domainspec-v2/impl/cli/dist']:
    for f in directory.rglob('*'):
        if f.is_file():files[f]=hashlib.sha256(f.read_bytes()).hexdigest()
for source,expected in files.items():
    assert source.is_file() and not source.is_symlink(),source
    assert hashlib.sha256(source.read_bytes()).hexdigest()==expected,source
    dest=root/source.relative_to('/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
node=Path('/home/vrondelli/.nvm/versions/node/v26.8.1/bin/node')
dest=root/node.relative_to('/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(node,dest)
rust=Path('/home/vrondelli/.rustup/toolchains/1.95.0-x86_64-unknown-linux-gnu')
for part in ['bin','lib']:shutil.copytree(rust/part,root/rust.relative_to('/')/part)
# Resolve the exact generated event crate, then copy only its registry dependency closure.
lockdir=context/'resolve';(lockdir/'src').mkdir(parents=True)
(lockdir/'src/main.rs').write_text('fn main() {}\n')
(lockdir/'Cargo.toml').write_text('[package]\nname="alch-event"\nversion="0.2.0"\nedition="2021"\n[dependencies]\nserde_json="=1.0.149"\nrusqlite={version="=0.32.1",features=["bundled"]}\nchrono={version="=0.4.45",default-features=false,features=["std"]}\n')
subprocess.run([str(rust/'bin/cargo'),'generate-lockfile','--offline','--manifest-path',str(lockdir/'Cargo.toml')],check=True,env={**os.environ,'PATH':str(rust/'bin')+':/usr/bin:/bin'})
packages=[p for p in tomllib.loads((lockdir/'Cargo.lock').read_text())['package'] if p.get('source','').startswith('registry+')]
registry=Path('/home/vrondelli/.cargo/registry');target=root/registry.relative_to('/')
# Cargo needs index metadata for feature/version resolution but no credentials/config from CARGO_HOME.
shutil.copytree(registry/'index',target/'index')
for package in packages:
    stem=package['name']+'-'+package['version']
    caches=list((registry/'cache').glob('*/'+stem+'.crate'))
    sources=list((registry/'src').glob('*/'+stem))
    # Target-specific optional crates can exist only as index entries. Cargo resolves
    # them but does not compile/download them on the tested Linux x86_64 target.
    for f in caches:
        dest=target/f.relative_to(registry);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
    for f in sources:shutil.copytree(f,target/f.relative_to(registry))
(root/'opt/alch').mkdir(parents=True)
for name in ['start.py','gateway.py']:shutil.copy2(HERE/name,root/'opt/alch'/name)
shutil.copy2(HERE/'Dockerfile',context/'Dockerfile')
shutil.rmtree(lockdir)
receipt={'context':str(context),'repository_files':len(files),'registry_packages':len(packages),'source_candidate_sha256':hashlib.sha256((HERE.parent/'host-lifecycle-v1/candidate-manifest.json').read_bytes()).hexdigest()}
(HERE/'payload-manifest.json').write_text(json.dumps({'files':{str(f.relative_to(REPO)):h for f,h in files.items()},'authority_effect':'none'},indent=2)+'\n')
(HERE/'build-context.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
