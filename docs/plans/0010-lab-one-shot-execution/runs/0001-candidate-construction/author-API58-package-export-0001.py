"""Create an unfrozen API successor for authenticated managed package export."""
import copy
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v57';API=BASE/'api-v58'
def replace(path,before,after):
    text=path.read_text();assert text.count(before)==1,(path,before)
    path.write_text(text.replace(before,after,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v8').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v7',BASE/'lesson-host-composition-v8',ignore=ignore)
    replace(BASE/'lesson-host-composition-v8/host.py','api-v57/service.py','api-v58/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v7','lesson-host-composition-v8')
    replace(API/'protocol.py',"PACKAGE_SUPPORTED=METADATA_SUPPORTED+('package.import',)",
        "PACKAGE_SUPPORTED=METADATA_SUPPORTED+('package.import',)\nPACKAGE_EXPORT_SUPPORTED=METADATA_SUPPORTED+('package.export',)")
    replace(API/'protocol.py',"'lesson.select','package.import')","'lesson.select','package.import','package.export')")
    path=API/'authentication.schema.json';schema=json.loads(path.read_bytes())
    policy=copy.deepcopy(next(row for row in schema['oneOf'] if row.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-package-import-policy/v1-candidate'))
    policy['properties']['schema_version']={'const':'lab-local-package-export-policy/v1-candidate'}
    policy['properties']['purpose']={'const':'durable-metadata-and-exact-package-export'}
    policy['properties']['allowed_operations']['const'][-1]='package.export'
    policy['properties']['package_export_control']=policy['properties'].pop('package_control')
    policy['required']=[('package_export_control' if name=='package_control' else name) for name in policy['required']]
    schema['oneOf'].append(policy);path.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    path=API/'auth.py'
    replace(path,"        package=value['schema_version']=='lab-local-package-import-policy/v1-candidate'",
        "        package=value['schema_version']=='lab-local-package-import-policy/v1-candidate'\n        package_export=value['schema_version']=='lab-local-package-export-policy/v1-candidate'")
    replace(path,'typed or package or value[','typed or package or package_export or value[')
    replace(path,"        if package:fields+=['package_control']","        if package:fields+=['package_control']\n        if package_export:fields+=['package_export_control']")
    replace(path,"'lab-local-package-import-policy/v1-candidate')","'lab-local-package-import-policy/v1-candidate','lab-local-package-export-policy/v1-candidate')")
    replace(path,'list(PACKAGE_SUPPORTED if package else','list(PACKAGE_EXPORT_SUPPORTED if package_export else PACKAGE_SUPPORTED if package else')
    replace(path,"        borrowed=FACT_SCOPE.policy_scope(self)",
        "        if package_export:\n            from .package_export import validate_control\n            validate_control(value,self.schemas)\n        borrowed=FACT_SCOPE.policy_scope(self)")
    replace(path,"('durable-metadata-and-exact-package-import' if package else", "('durable-metadata-and-exact-package-export' if package_export else 'durable-metadata-and-exact-package-import' if package else")
    path=API/'workspace.py'
    replace(path,"if policy['schema_version']=='lab-local-package-import-policy/v1-candidate':", "if policy['schema_version'] in ('lab-local-package-import-policy/v1-candidate','lab-local-package-export-policy/v1-candidate'):")
    replace(path,"if self.channel.policy['schema_version']=='lab-local-package-import-policy/v1-candidate' and", "if self.channel.policy['schema_version'] in ('lab-local-package-import-policy/v1-candidate','lab-local-package-export-policy/v1-candidate') and")
    path=API/'service.py'
    replace(path,'from .package_import import PackageImport','from .package_import import PackageImport\nfrom .package_export import PackageExport')
    replace(path,"        self.packages=PackageImport(self) if channel.policy['schema_version']=='lab-local-package-import-policy/v1-candidate' else None",
        "        self.packages=PackageImport(self) if channel.policy['schema_version']=='lab-local-package-import-policy/v1-candidate' else None\n        self.package_exports=PackageExport(self) if channel.policy['schema_version']=='lab-local-package-export-policy/v1-candidate' else None")
    replace(path,"'lesson_selection.py','package_import.py')}","'lesson_selection.py','package_import.py','package_export.py')}")
    replace(path," if call['operation']=='package.import' else", " if call['operation']=='package.import' else binding(str((HERE/'package_export.py').relative_to(ROOT)),(HERE/'package_export.py').read_bytes()) if call['operation']=='package.export' else")
    replace(path,"'typed.extension.prepare','package.import')", "'typed.extension.prepare','package.import','package.export')")
    # The two read-only retry branches use the original recorded receipt identity.
    text=path.read_text();needle="                    if name=='package.import':domain=self.packages.readback(message,call['expected_source_cut'],call['idempotency_key'],effective,domain)"
    assert text.count(needle)==2
    text=text.replace(needle,needle+"\n                    if name=='package.export':domain=self.package_exports.readback(message,call['expected_source_cut'],call['idempotency_key'],effective,domain)")
    path.write_text(text)
    replace(path,"                elif name=='package.import':self.packages.preflight(message,call['expected_source_cut'],call['idempotency_key'],effective)",
        "                elif name=='package.import':self.packages.preflight(message,call['expected_source_cut'],call['idempotency_key'],effective)\n                elif name=='package.export':\n                    if self.package_exports is None:raise ApplicationError('unauthorized','Independently selected package export authority is unavailable.')\n                    self.package_exports.preflight(message,call['expected_source_cut'],call['idempotency_key'],effective)")
    replace(path,"                elif name=='package.import':domain,evidence=self.packages.prepare(message,request,call['expected_source_cut'],call['idempotency_key'],effective)",
        "                elif name=='package.import':domain,evidence=self.packages.prepare(message,request,call['expected_source_cut'],call['idempotency_key'],effective)\n                elif name=='package.export':domain,evidence=self.package_exports.prepare(message,request,call['expected_source_cut'],call['idempotency_key'],effective,inner)")
    replace(API/'candidate.py',"claim['operation']=='files.materialize'", "claim['operation'] in ('files.materialize','package.export')")
    print('Authored unfrozen API58 host/policy/schema integration. Export handler, fixtures and exact qualification remain required.',flush=True)

if __name__=='__main__':main()
