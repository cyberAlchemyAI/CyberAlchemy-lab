from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
original=R/'work/plans/definition-canonical-migration/verify-final-catalog.py';raw=original.read_text()
needle='P=Path(__file__).resolve().parent'
assert raw.count(needle)==1
redirected=raw.replace(needle,"P=R/'work/plans/definitions-records-audit-2026-11-12'")
(P/'CATALOG-CHECK-SOURCE.json').write_text(json.dumps({'path':original.relative_to(R).as_posix(),'sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'modification':'Redirect verification output only; all checks and original input paths are unchanged.'},indent=2)+'\n')
exec(compile(redirected,str(original),'exec'),{'__file__':str(original),'__name__':'__main__'})
