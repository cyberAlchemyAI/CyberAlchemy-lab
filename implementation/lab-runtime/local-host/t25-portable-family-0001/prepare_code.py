"""Create disjoint stable producer code and sealed original metadata templates.

No active family, artifact body, signed snapshot or native installation changes.
The new code requires the trusted closed provider before any family import.
"""
import ast,hashlib,json,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
OLD=ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001'
ORIGINAL=OLD/'instances/legacy-local-4636eca980a5d94d'
FAMILY=HERE/'instances/legacy-local-4636eca980a5d94d'
SLOTS={'SOURCE_PIN':'family.source','SOURCE_PACKAGE':'family.source_package','PACKAGE_PIN':'family.source_package','ADAPTER_PIN':'family.reader_source','MAPPED_PIN':'family.mapper_source','MAPPED_PACKAGE_PIN':'family.mapper_package','MAPPED_SOURCE_SHA':'family.mapper_source'}
def need(value,reason):
 if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def provider(text):
 tree=ast.parse(text);lines=text.splitlines(keepends=True);at=tree.body[0].end_lineno if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str) else 0
 lines[at:at]=['import cal_installed_runtime_selection_v1 as _INSTALL_SELECTION\n','_INSTALL_SELECTION.guard()\n'];return ''.join(lines)
def convert(role,name,text):
 text=text.replace("Path('/home/vlad_/projects/CyberAlchemy-lab')",'_INSTALL_SELECTION.root()')
 for field,slot in SLOTS.items():
  text=re.sub(r"(?m)^"+field+r"='[0-9a-f]{64}'$",field+"=_INSTALL_SELECTION.binding('"+slot+"')['sha256']",text)
 if role=='source' and name=='base.py':
  text=re.sub(r"PRIVATE_ARCHIVE=Path\('[^']+'\)","PRIVATE_ARCHIVE=Path(_INSTALL_SELECTION.value('archive.path'))",text)
  old="row={'path':(HERE/'context-native-role.json').relative_to(ROOT).as_posix(),'sha256':'070eaf1b3fa6c022e7e580e5b0cd7f15409b4cc237f3ccec93d517b923c2397a'}"
  need(old in text,'exact original Context role selection seam required')
  text=text.replace(old,"row=_INSTALL_SELECTION.binding('family.context_native_role')\n        source_manifest=parse(original(_INSTALL_SELECTION.binding('family.source')))\n        require(row in source_manifest['files'],'native role must be independently selected by Source manifest')")
  text=text.replace("(ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/loader.py')","(ROOT/_INSTALL_SELECTION.binding('engine.loader')['path'])")
  text=text.replace("(ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/pins.json')","(ROOT/_INSTALL_SELECTION.binding('engine.pins')['path'])")
  text=text.replace('def original(row):\n','def original(row):\n    _INSTALL_SELECTION.guard()\n    require(ROOT==_INSTALL_SELECTION.root(),\'selected producer Root changed\')\n')
  text=text.replace('def verify_source(pin):\n','def verify_source(pin):\n    _INSTALL_SELECTION.guard()\n    require(pin==_INSTALL_SELECTION.binding(\'family.source\')[\'sha256\'],\'independently selected Source pin differs\')\n')
 elif role=='source' and name=='build.py':
  text=re.sub(r"PRIVATE_ARCHIVE=Path\('[^']+'\)","PRIVATE_ARCHIVE=Path(_INSTALL_SELECTION.value('archive.path'))",text)
 elif role=='mapped' and name=='build.py':
  text=re.sub(r"EXE=Path\('[^']+'\)","EXE=Path(_INSTALL_SELECTION.value('native.root'))/'bin/lab-context-native-reader'",text)
 elif role=='mapped' and name=='base.py':
  text=text.replace("reader.adapter.source.B.verify_inputs(m['files'])","reader.adapter.source.B.verify_inputs(m['files'],selected_external=m.get('external_dependency_bindings',[]))")
 return provider(text)
def main():
 need(not FAMILY.exists(),'refuse overwrite generic producer family')
 FAMILY.mkdir(parents=True)
 rows=[];original_artifacts=[]
 for role in ('source','reader','mapped','context'):
  out=FAMILY/role;out.mkdir()
  for p in sorted((ORIGINAL/role).iterdir()):
   if not p.is_file() or p.name=='source-manifest.json':continue
   q=out/p.name
   if p.suffix=='.py':q.write_text(convert(role,p.name,p.read_text()))
   else:shutil.copyfile(p,q)
   rows.append({'path':str(q.relative_to(ROOT)),'sha256':sha(q.read_bytes())})
 role_source=(OLD/'installed_context_role.py').read_text().replace("ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')",'ROOT=_INSTALL_SELECTION.root()')
 role_source=re.sub(r"INSTALL=Path\('[^']+'\)","INSTALL=Path(_INSTALL_SELECTION.value('native.root'))",role_source)
 role_source=role_source.replace('    def guard(self):\n','    def guard(self):\n        _INSTALL_SELECTION.guard()\n')
 q=HERE/'installed_context_role.py';q.write_text(provider(role_source));rows.append({'path':str(q.relative_to(ROOT)),'sha256':sha(q.read_bytes())})
 # Original signed Artifact inputs retain their original relative material
 # locators. Current package copies can point at these bytes without executing
 # any old host-bound Source code. Record all 26 exact bodies for final audit.
 for p in sorted((ORIGINAL/'source/packages/0001/artifacts').glob('*.json')):
  original_artifacts.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes())})
 for p in sorted(FAMILY.rglob('*.py')):ast.parse(p.read_text())
 ast.parse(q.read_text())
 receipt={'schema_version':'lab-portable-family-code-preparation/v1','generic_family':str(FAMILY.relative_to(ROOT)),'original_family':str(ORIGINAL.relative_to(ROOT)),'stable_code_and_controls':rows,'unchanged_signed_Source_artifacts':original_artifacts,'provider_module':'cal_installed_runtime_selection_v1','original_family_modified':False,'native_code_executed':False,'authority_effect':'none'}
 p=HERE/'CODE-PREPARATION.json';need(not p.exists(),'retain prior code receipt');p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'PREPARED-stable-code','files':len(rows),'Source_artifacts':len(original_artifacts)}))
if __name__=='__main__':main()
