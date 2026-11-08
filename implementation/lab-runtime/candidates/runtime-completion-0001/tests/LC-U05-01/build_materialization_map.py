"""Select actual AC07 original source bodies and exact producer/consumer names."""
import bootstrap
from bootstrap import R,S,checked
import ast,json,hashlib,os

API='product/lab/release-candidates/v1/interface/api-integration-v30/'
PUB='product/lab/release-candidates/v1/interface/package-publication-v2/publication.py'
MIRROR='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T33/authentic-publisher-successor-inactive-0007/lab_runtime/publisher.py'
SPECS={
 'api-dispatch':(API+'service.py',['Service._call','Service.deliver_recorded']),
 'source-bytes':(API+'artifact_model.py',['record_bytes']),
 'files-handler':(API+'file_exports.py',['validate_control','FileExports.preflight','FileExports.materialize','FileExports.readback']),
 'files-kernel':(API+'export_kernel.py',['renderer_binding','ExportHost.plan','ExportHost.materialize','nested_write','nested_read']),
 'package-handler':(API+'package_export.py',['PackageExport.evaluate','PackageExport.prepare','PackageExport.readback']),
 'package-consumer':(API+'package_import.py',['PackageImport.evaluate','PackageImport.readback']),
 'package-kernel':(PUB,['Publisher.publish','Publisher.read_package']),
 'managed-mirrors':(MIRROR,['render_bundle','verify_bundle','_replace_managed','inspect_projection','_repair','_pointer_bytes']),
}

def select(path,names):
 raw=checked(R/path);tree=ast.parse(raw)
 def find(parts):
  body=tree.body
  for part in parts:
   choices=[n for n in body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==part]
   if len(choices)!=1:raise ValueError('exact original source selector missing: '+path+':'+'.'.join(parts))
   node=choices[0];body=node.body
  return {'selector':'python:'+'.'.join(parts),'start_line':node.lineno,'end_line':node.end_lineno}
 return {'binding':{'kind':'execution','root_id':'repository','relative_path':path,
          'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)},
         'selectors':[find(name.split('.')) for name in names]}

def build():
 sources={key:select(path,names) for key,(path,names) in SPECS.items()}
 schemas=[]
 for name in ['file-materialization-request','file-materialization-receipt']:
  p='docs/proposals/0007-lab-integrated-schema-package/schemas/'+name+'.schema.json';raw=checked(R/p)
  schemas.append({'kind':'execution','root_id':'repository','relative_path':p,'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)})
 return {'schema_version':'lab-ac07-materialization-source-map/v1','authority_effect':'none',
  'source_bindings':sources,'original_schema_bindings':schemas,
  'flows':[
   {'id':'files.materialize','producer_selectors':['source-bytes:record_bytes','files-handler:FileExports.preflight','files-kernel:ExportHost.plan'],
    'consumer_selectors':['api-dispatch:Service._call','files-handler:FileExports.materialize','files-handler:FileExports.readback','files-kernel:ExportHost.materialize'],
    'source_relationship':'Exact selected signed-source cut and ordered Artifact header -> original material bytes, source locator and encoding. No row path or digest grants body access.',
    'output_relationships':['byte-exact: output equals original material bytes; digest equals Artifact header byte_sha256',
      'rendered: selected export_kernel.py renderer applies JSON parse then indent=2, sorted keys, ensure_ascii=False, allow_nan=False and one LF; renderer full-byte binding is required'],
    'root_contract':'Independent export_control output_root_scope_ref plus exact output_root_identity and scope bytes; source and current permission guards before and after use.',
    'preimage_contract':'A new request generation is claimed exclusively; existing generation can only be read back with exact published marker, manifest, receipt and every selected output byte. Pending/foreign/uncertain generation refuses redispatch.',
    'original_source_mapping':'Manifest files retain relative_path, output digest/size, original Artifact header, source_locator and source_encoding.',
    'qualification_status':'unqualified-original-adapter; requires R03 stable ReadSelection and exclusive held-root integration'},
   {'id':'package.export','producer_selectors':['package-handler:PackageExport.evaluate','package-handler:PackageExport.prepare'],
    'consumer_selectors':['package-kernel:Publisher.publish','package-kernel:Publisher.read_package','package-handler:PackageExport.readback','package-consumer:PackageImport.evaluate'],
    'source_relationship':'Independently selected package plan resolves exact original source/candidate materials and complete dependency/disposition closure; package bytes and package binding are passed intact to the managed publisher.',
    'output_relationships':['byte-exact archive: immutable package payload equals the evaluated archive; readback recomputes evaluation and compares archive and exact recorded receipt'],
    'root_contract':'Independently selected managed package root/scope/identity and current source/permission guards; no caller-selected destination or actual publisher authority from the map.',
    'preimage_contract':'No-replace managed generation; uncertainty retains evidence and refuses write retry. Read_package is the recovery/readback consumer.',
    'original_source_mapping':'Selected package plan, exact package/member bindings, request binding and signed source_cut retained by package transfer/publication records.',
    'qualification_status':'unqualified-original-adapter; exact native transfer origins and stable-read integration required'},
   {'id':'managed-mirror','producer_selectors':['managed-mirrors:render_bundle','managed-mirrors:verify_bundle','managed-mirrors:_pointer_bytes'],
    'consumer_selectors':['managed-mirrors:_repair','managed-mirrors:_replace_managed','managed-mirrors:inspect_projection'],
    'source_relationship':'Mirror source is an exact member of the committed verified bundle, excluding bundle.json; current lookup is a derived projection of bundle manifest fields.',
    'output_relationships':['mirror byte-exact: destination bytes equal verified files[row.source]',
      'current lookup: exact encoded _pointer_bytes result; pointer is derived and never alternate replay authority'],
    'root_contract':'Original authority.repository_root and review.mirrors paths; successor must bind held exclusive root and selected member identity, not only pathname.',
    'preimage_contract':'Original row.before_sha256 and expected_pointer_sha256 are necessary but insufficient. Equal after bytes do not establish ownership; every existing leaf/temp requires selected ownership/identity before reuse or replace.',
    'original_source_mapping':'review.mirrors pairs exact source member with destination and before digest; current lookup pairs bundle digest with selected project-state member digest.',
    'qualification_status':'ineligible-legacy-path-until-reviewed-successor',
    'known_required_corrections':['Replace equal-bytes already-current shortcut with explicit ownership and custody verification.',
      'Route writes through selected broker/root capability with full preimage binding and no writable-alias gap.',
      'Consume a single stable R03 ReadSelection; direct path-based pointer consumers remain ineligible.']}
  ],
  'required_negative_evidence':['escaped path','symlink or ancestor/mount replacement','writable alias','existing foreign destination including equal bytes','changed expected preimage','interrupted generation/mirror repair without redispatch'],
  'original_acceptance':{'AC07':'pending T19 technical evidence and T24 assessment','T08':'not accepted by this map','T09':'not accepted by this map'},
  'actual_qualification':False,'actual_installation':False}

if __name__=='__main__':
 value=build();raw=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
 target=S/'environment/materialization-source-map.json';target.parent.mkdir(mode=0o700,exist_ok=True)
 if '--verify' in __import__('sys').argv:
  if checked(target)!=raw:raise ValueError('materialization map drift')
 else:
  with target.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':len(SPECS)+2,'effect_state':'owned-inert','cleanup':'clean'}))
