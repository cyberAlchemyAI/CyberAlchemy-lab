"""Read-only AST inventory/comparison; never import or run API test fixtures."""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
LEDGER_PIN='7a90ad2d963c1b817857abbc5a4a934b6ce895fbf1fc3fd20c6c4c770c004ee5'
REVISIONS={
 'test_preparation.py:Preparation.test_small_receipt_budget_refused_before_effect':'Existing original envelope minimum: below4096 refuses as invalid-envelope before a journal effect.',
 'test_classification_api.py:ClassificationAPI.test_09_independent_axis_is_preserved':'Existing fixture materializes five artifact targets and four typed relations; assert exact nine-target closure.',
 'run_session_checks.py:Sessions.test_30_current_handler_profile_retains_all_original_contracts':'Existing catalog assertion follows the original34 contracts declared by the final shared profile.'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(value,message):
 if not value:raise ValueError(message)
def path(value):
 p=Path(value)
 if not p.is_absolute():p=ROOT/p
 require(p.is_relative_to(ROOT) and p.resolve()==p,'exact repository path required')
 return p
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def dump(node):return ast.dump(node,annotate_fields=True,include_attributes=False)
def ast_sha(node):return sha(dump(node).encode())

def discover(directory):
 directory=path(directory);methods={};classes={};modules={}
 for file in sorted(directory.glob('*.py')):
  raw=file.read_bytes();tree=ast.parse(raw.decode('utf-8'),filename=str(file));normalized=copy.deepcopy(tree);found=False
  for cls in tree.body:
   if not isinstance(cls,ast.ClassDef):continue
   rows=[n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')]
   if not rows:continue
   found=True;class_id=file.name+':'+cls.name;class_methods=[]
   for method in rows:
    ident=class_id+'.'+method.name;require(ident not in methods,'duplicate declared method: '+ident)
    methods[ident]={'file':file.name,'class':cls.name,'method':method.name,'method_ast_sha256':ast_sha(method),'method_ast':dump(method),'source_excerpt':ast.get_source_segment(raw.decode('utf-8'),method),'line':method.lineno}
    class_methods.append(ident)
   classes[class_id]={'file':file.name,'class':cls.name,'class_ast_sha256':ast_sha(cls),'methods':sorted(class_methods)}
  if found:
   # Compare setup/teardown, bases, decorators, helpers, imports and globals as
   # well as test bodies. Test bodies have their separate exact AST bindings.
   for cls in normalized.body:
    if isinstance(cls,ast.ClassDef):
     cls.body=[n for n in cls.body if not (isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_'))]
   modules[file.name]={'file_binding':binding(file),'non_test_module_ast_sha256':ast_sha(normalized)}
 return {'directory':directory.relative_to(ROOT).as_posix(),'methods':{k:methods[k] for k in sorted(methods)},'classes':{k:classes[k] for k in sorted(classes)},'modules':modules}

def original_compare(original,current):
 old=original['methods'];new=current['methods'];missing=sorted(old.keys()-new.keys());added=sorted(new.keys()-old.keys())
 changed=[]
 for ident in sorted(old.keys()&new.keys()):
  if old[ident]['method_ast_sha256']!=new[ident]['method_ast_sha256']:
   changed.append({'method':ident,'documented_revision':REVISIONS.get(ident),'original_ast_sha256':old[ident]['method_ast_sha256'],'current_ast_sha256':new[ident]['method_ast_sha256'],'original_source':old[ident]['source_excerpt'],'current_source':new[ident]['source_excerpt']})
 fixtures=[name for name,row in original['modules'].items() if name in current['modules'] and row['non_test_module_ast_sha256']!=current['modules'][name]['non_test_module_ast_sha256']]
 unexpected=[r['method'] for r in changed if r['method'] not in REVISIONS]
 unexpected_added=[ident for ident in added if not ident.startswith('test_installation_release.py:InstallationReleaseAPI.')]
 return {'original_methods':len(old),'current_methods':len(new),'missing_original_methods':missing,'added_installation_release_methods':added,'unexpected_added_methods':unexpected_added,'changed_original_methods':changed,'unexpected_changed_original_methods':unexpected,'changed_non_test_fixture_modules':fixtures,'documented_existing_revisions':REVISIONS,'acceptable':not (missing or unexpected or fixtures or unexpected_added)}

def compare(original,current):
 ledger_path=RUN/'legacy-session-native-fixture-0257/fixture-selector-ledger-v2.json'
 require(binding(ledger_path)['sha256']==LEDGER_PIN,'exact independently authored successor selector ledger required')
 ledger=json.loads(ledger_path.read_bytes());allowed={};fixture_files=set()
 for row in ledger['files']:
  previous=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v14'/row['file']
  selected=path(current['directory'])/row['file']
  require(binding(previous)['sha256']==row['old_file_sha256'] and binding(selected)['sha256']==row['new_file_sha256'],'independent fixture source bytes differ')
  fixture_files.add(row['file'])
  for delta in row['selector_deltas']:
   matches=[ident for ident,m in current['methods'].items() if m['file']==row['file'] and m['method']==delta['method']]
   require(len(matches)==1,'exact successor method selector required');ident=matches[0]
   require(current['methods'][ident]['method_ast_sha256']==delta['after_AST_sha256'],'successor method AST differs from independently selected ledger')
   allowed[ident]=delta
 result=original_compare(original,current)
 for change in result['changed_original_methods']:
  if change['method'] in allowed:change['documented_revision']=allowed[change['method']]['reason']
 result['unexpected_changed_original_methods']=[x['method'] for x in result['changed_original_methods'] if x['method'] not in REVISIONS and x['method'] not in allowed]
 result['unexpected_fixture_modules']=[f for f in result['changed_non_test_fixture_modules'] if f not in fixture_files]
 result['independent_successor_AST_ledger_binding']=binding(ledger_path)
 result['all_method_ASTs_unchanged']=not result['changed_original_methods']
 result['acceptable']=not (result['missing_original_methods'] or result['unexpected_changed_original_methods'] or result['unexpected_fixture_modules'] or result['unexpected_added_methods'])
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--original-api-directory',required=True);parser.add_argument('--api-directory',required=True);parser.add_argument('--output');args=parser.parse_args()
 value={'schema_version':'lab-final-api-method-comparison/v1-candidate','comparison':compare(discover(args.original_api_directory),discover(args.api_directory)),'tool_binding':binding(Path(__file__).resolve()),'test_execution_performed':False,'authority_effect':'none','actual_owner_outcome':None,'goal_complete':False}
 raw=json.dumps(value,indent=2,sort_keys=True)+'\n'
 if args.output:
  out=path(args.output);require(out.parent==RUN and out.name.startswith('final-api-regression-'),'owned new comparison report required')
  with out.open('x') as f:f.write(raw)
 else:print(raw,end='')
 return 0 if value['comparison']['acceptable'] else 1
if __name__=='__main__':raise SystemExit(main())
