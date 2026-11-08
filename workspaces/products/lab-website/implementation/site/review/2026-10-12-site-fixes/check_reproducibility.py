"""Verify identical package bytes after an ordinary whole-site rebuild."""
from pathlib import Path
import hashlib,json,os,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[3]
SITE=Path(os.environ.get('LAB_SITE_VERIFIED_ROOT',str(ROOT/'website')))
OUT=ROOT/'website/output/playwright/ux-validator/20261012-site-fixes/measurements'
def digest(data):return hashlib.sha256(data).hexdigest()
def inputs():
    return {str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in SITE.rglob('*') if p.is_file() and not set(p.relative_to(SITE).parts)&{'dist','output','artifacts','.build','.venv','__pycache__','review'}}
def package():
    with zipfile.ZipFile(SITE/'artifacts/cyberalchemy-lab-website.zip') as archive:
        return {i.filename:digest(archive.read(i)) for i in archive.infolist()},archive.testzip()
a=inputs();before=json.loads((SITE/'artifacts/build.json').read_text());files_before,_=package()
subprocess.run([str(SITE/'.venv/bin/python'),str(SITE/'build.py')],cwd=ROOT,check=True)
b=inputs();after=json.loads((SITE/'artifacts/build.json').read_text());files_after,zip_failure=package()
result={'inputFiles':len(a),'inputsChanged':sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k)),'archiveBefore':before['archive_sha256'],'archiveAfter':after['archive_sha256'],'sameArchive':before['archive_sha256']==after['archive_sha256'],'changedEntries':sorted(k for k in set(files_before)|set(files_after) if files_before.get(k)!=files_after.get(k)),'zipTest':zip_failure,'inputManifest':b}
(OUT/'release-complete-reproducibility.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='inputManifest'}))
assert result['sameArchive'] and not result['inputsChanged'] and not result['changedEntries'] and zip_failure is None
