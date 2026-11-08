"""Versioned exact CompositeEnvironment -> R02 adapter; no installer authority."""
from dataclasses import dataclass
from pathlib import PurePosixPath
import ast
from jsonschema import Draft202012Validator
from lab_contracts.codec import Refusal,need,closed,sha,canonical
from dependency_graph.reader import RoleReader,binding,source_cut
from dependency_graph.semantic import verify_graph
from .body_json import parse_original
from .requirements import inspect_execution_requirements,PRIOR_PATH,ORIGINAL_BINDINGS,absolute
from .origins import verify_selected_origins,OriginSelection

ORIGINAL_DESCRIPTOR_SHA='c82c6f2910ae1bd8e8446d36a2da29e4fab2a877d82a9cd6bf11fcd539d88057'
ORIGINAL_SCHEMA_SHA='0afc75cb4348a42747fabc70d3dce96d356e1466fe4b158dd085baa058784f18'
COMPOSITE={'path':'product/lab/release-candidates/v1/release-validation/0001/runtime16-draft-0276/environment-contract.json',
    'sha256':'79393346ec5b58517febe7518d4268ea1804fba1bf2061f4b3bcc69b44de3506'}
CLASSIFICATION={'path':'product/lab/release-candidates/v1/release-validation/0001/environment-contract.json',
    'sha256':'ae389483f4fbe398b82d7421bd2bc1e1b3864ebc216c932d3f85448da9c8a2e3'}

@dataclass(frozen=True)
class CompositeSelection:
    descriptor_file_id:str
    descriptor_binding:dict
    schema_file_id:str
    schema_binding:dict
    original_descriptor_file_id:str
    original_descriptor_binding:dict
    source_binding:dict
    profile_binding:dict
    source_cut:dict
    legacy_origins:list

def verify_environment(reader,selection,origin_selection,semantic_request,*,repository):
    """Consume the complete reviewed T08 contract, then verify selected origins.

The installer must independently select this versioned adapter and all anchors.
Technical checkpoint review is a prerequisite of integration, not a credential
supplied by a public request. No result grants effects or actual host trust.
"""
    try:
        need(type(reader)is RoleReader and type(selection)is CompositeSelection
             and type(origin_selection)is OriginSelection,'ENV_SELECTION')
        sealed=canonical(selection.__dict__);files=reader.files;absolute(repository)
        for name in ('descriptor_binding','schema_binding','original_descriptor_binding','source_binding','profile_binding'):
            binding(getattr(selection,name))
        source_cut(selection.source_cut)
        for name in ('source_binding','profile_binding','source_cut'):
            need(getattr(selection,name)==reader.selection[name]==getattr(origin_selection,name),'ENV_SOURCE_CUT')
        def selected(file_id,b,role):
            need(type(file_id)is str and file_id in files and files[file_id]['binding']==b and files[file_id]['kind']==role,'ENV_EXACT_ORIGIN')
            return reader.read(file_id,role)
        mappings={};consumed=set()
        need(type(selection.legacy_origins)is list and len(selection.legacy_origins)<=100000,'ENV_MAP_BOUND')
        for row in selection.legacy_origins:
            closed(row,('path','file_id','binding','role'));binding(row['binding'])
            need(type(row['path'])is str and row['path'] not in mappings,'ENV_AMBIGUOUS_ORIGIN')
            mappings[row['path']]=row
        def legacy(row,role):
            closed(row,('path','sha256'))
            need(row['path'] in mappings,'ENV_MISSING_ORIGIN');chosen=mappings[row['path']]
            need(chosen['role']==role and chosen['binding']['sha256']==row['sha256'],'ENV_LEGACY_IDENTITY')
            consumed.add(row['path'])
            return selected(chosen['file_id'],chosen['binding'],role)
        with reader.boundary():
            schema_raw=selected(selection.schema_file_id,selection.schema_binding,'governed-schema')
            need(sha(schema_raw)==ORIGINAL_SCHEMA_SHA,'ENV_ORIGINAL_SCHEMA')
            original_raw=selected(selection.original_descriptor_file_id,selection.original_descriptor_binding,'environment-contract')
            need(sha(original_raw)==ORIGINAL_DESCRIPTOR_SHA,'ENV_ORIGINAL_DESCRIPTOR')
            original_descriptor=parse_original(original_raw)
            raw=selected(selection.descriptor_file_id,selection.descriptor_binding,'environment-contract')
            value=parse_original(raw);schema=parse_original(schema_raw)
            Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(value)
            closed(value,('schema_version','authority_effect','actual_owner_outcome','r02_selection',
                'original_composite_binding','historical_classification_binding','execution_dependencies',
                'host_native_binding','host_ABI_library_bindings','retained_full_proof','module_bindings'))
            need(value['schema_version']=='lab-composite-install-environment/v3-candidate'
                 and value['authority_effect']=='none' and value['actual_owner_outcome'] is None,'ENV_VERSION')
            chosen=value['r02_selection'];closed(chosen,('schema_version','json_pointer','environment'))
            need(chosen['schema_version']=='lab-R02-composite-subdocument-selection/v1-candidate'
                 and chosen['json_pointer']=='/R02_environment','ENV_R02_SELECTOR')
            closed(chosen['environment'],('implementation','interpreter_sha256','libc','machine','python_version','sqlite_version','system'))
            need(value['original_composite_binding']==COMPOSITE and value['historical_classification_binding']==CLASSIFICATION,'ENV_ORIGINAL_PROOF')
            original=parse_original(legacy(COMPOSITE,'environment-contract'))
            classification=parse_original(legacy(CLASSIFICATION,'environment-contract'))
            need(original['schema_version']=='lab-final-runtime-environment-draft/v2-candidate'
                 and chosen['environment']==original['R02_environment'],'ENV_EXACT_R02')
            need(classification['schema_version']=='lab-final-runtime-environment-contract/v1-candidate'
                 and classification['protected_repository_and_host_dependencies_required'] is True
                 and classification['protected_dependencies'],'ENV_PROTECTED_CLASSIFICATION')
            proof=value['retained_full_proof']
            closed(proof,('source_binding','profile_binding','source_rows','profile_rows','qualification','original_locator_aliases'))
            need(proof['qualification']=='unresolved-original-full-proof' and proof['original_locator_aliases']==[]
                 and proof['source_binding']==original['API_source_binding'] and proof['profile_binding']==original['API_profile_binding'],'ENV_FULL_PROOF_SELECTION')
            source=parse_original(legacy(proof['source_binding'],'source-manifest'))
            profile=parse_original(legacy(proof['profile_binding'],'contract-profile'))
            need(source['files']==original['complete_source_bindings'] and profile['files']==original['complete_profile_bindings']
                 and len(source['files'])==proof['source_rows']==original['source_rows']
                 and len(profile['files'])==proof['profile_rows']==original['profile_rows'],'ENV_FULL_ROWS')
            need(value['module_bindings']==original_descriptor['module_bindings'] and len(value['module_bindings'])==8,'ENV_MODULE_ORIGINS')
            for row in value['module_bindings']:ast.parse(legacy(row,'host-dependency'))
            deps=value['execution_dependencies'];closed(deps,('selection_binding','installed_root','execution_configuration'))
            dependency_raw=legacy(deps['selection_binding'],'execution-selection')
            prior_raw=legacy({'path':PRIOR_PATH,'sha256':ORIGINAL_BINDINGS[PRIOR_PATH]},'execution-selection')
            requirements=inspect_execution_requirements(dependency_raw,deps['selection_binding']['sha256'],prior_raw=prior_raw,repository=repository)
            original_requirements=requirements['original_value']
            need(original_requirements['environment']==chosen['environment'] and deps['execution_configuration']==original_requirements['execution_configuration'],'ENV_EXECUTION_REQUIREMENTS')
            installed=absolute(deps['installed_root'])
            native=[r for r in original_requirements['inputs'] if r['kind']=='native-executable']
            need(len(native)==1 and value['host_native_binding']=={'path':str(installed/native[0]['destination']),
                'sha256':native[0]['sha256'],'mode':native[0]['mode']},'ENV_NATIVE_ORIGIN')
            abi=[{'path':str(installed/r['destination']),'sha256':r['sha256'],
                'mode':0o755 if r['destination'].endswith('/ld-linux-x86-64.so.2') else 0o644}
                for r in original_requirements['inputs'] if r['kind']=='host-abi']
            need(value['host_ABI_library_bindings']==abi and abi,'ENV_ALL_ABI_REQUIREMENTS')
            need(consumed==set(mappings),'ENV_UNUSED_ORIGIN')
            closed(semantic_request,('policy_file_id','declared_edges','root_refs','anchor','policy_schema_raw'))
            graph=verify_graph(reader,**semantic_request)
            origins=verify_selected_origins(reader,original_requirements,origin_selection)
            need(canonical(selection.__dict__)==sealed and reader.files==files,'ENV_SELECTION_CHANGED')
        return {'schema_version':'lab-composite-environment-adapter/v1','descriptor_sha256':selection.descriptor_binding['sha256'],
            'R02_environment':chosen['environment'],'execution_requirement_counts':requirements['counts'],
            'semantic_graph':graph,'execution_origins':origins,'source_rows':len(source['files']),'profile_rows':len(profile['files']),
            'historical_execution_configuration':deps['execution_configuration'],
            'installed_source_loading_policy_verified':False,'actual_modules_imported':False,
            'full_original_proof_qualified':False,'runtime_qualified':False,'authority_effect':'none',
            'remaining':['actual host custody and installed modes','actual native/loader/runtime verification',
                'selected installed bytecode-cache loading policy (-I ignores environment prefix)',
                'original full proof member qualification and original task acceptance']}
    except Exception:
        raise Refusal('COMPOSITE_ENVIRONMENT_REFUSED') from None
