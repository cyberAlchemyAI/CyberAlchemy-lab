"""Selected-root proof for unchanged originals of successful retained APIs.

The host independently selects exact observations and terminal results. This
object preserves those original bytes and never revives their old permission.
"""
import copy
import json
import importlib.util
import inspect
from pathlib import Path
import sys
from types import CodeType
import retained as R
ROOT=Path(__file__).resolve().parents[4]

def enc(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

class ArchiveProof:
    def __init__(self, selections, *, transitions, typed_productions=(), original_bundles=(), native_emissions=()):
        R.need(type(selections)is list and type(original_bundles) in (list,tuple)
               and type(native_emissions) in (list,tuple)
               and (selections or original_bundles or native_emissions),
               'actual retained producers required')
        self.selections=copy.deepcopy(selections);self.transitions=copy.deepcopy(transitions)
        self.typed_productions=copy.deepcopy(list(typed_productions))
        self.original_bundles=copy.deepcopy(list(original_bundles))
        self.native_emissions=copy.deepcopy(list(native_emissions))
        R.need(len(self.native_emissions)<=1,'one exact native first-Session selection required')
        self.native_identity=None;self.native_source_cut=None
        self.native_source_binding=None;self.native_profile_binding=None;self.native_package_pin=None
        self.product_source_cut=None
        self.stamp=self.control_stamp()
        self.records,self.receipts=self.capture()
        self.record_stamp=R.sha(enc({ref:{'artifact':h,'original_sha256':R.sha(raw)} for ref,(h,raw) in self.records.items()}))
        self.guard()

    def capture(self):
        records={};receipts=[];observations=[];original_routes={}
        for selection in self.selections:
            observed=R.consume(**selection)
            observations.append(observed)
            receipts.extend([observed['observation_binding'],observed['terminal_binding']])
            for header,raw in observed['outputs']:
                key=header['version_ref']
                R.need(key not in records or records[key]==(header,raw),'ambiguous retained original revision')
                records[key]=(copy.deepcopy(header),raw)
        self.api_returned_refs=frozenset(records)
        intent_bundle=None
        if self.original_bundles:
            for selection in self.original_bundles:
                R.need(type(selection)is dict and set(selection)=={'kind','manifest_path','manifest_sha256'},
                       'closed original Work bundle selection required')
                kind=selection['kind']
                R.need(kind in ('engineering','research','intent-framing'),
                       'unsupported original Work bundle kind')
                path=ROOT/('implementation/lab-runtime/local-host/t31-native-intent-framing-0001/intent_bundle.py'
                           if kind=='intent-framing' else
                           'implementation/lab-runtime/local-host/t31-remaining-eighteen-0001/original_bundle.py')
                R.need(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),
                       'selected original Work bundle reader absent')
                digest=R.sha(path.read_bytes());name='_cal_t31_original_bundle_'+digest
                if name not in sys.modules:
                    spec=importlib.util.spec_from_file_location(name,path)
                    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
                module=sys.modules[name]
                R.need(Path(module.__file__)==path and R.sha(path.read_bytes())==digest,
                       'original Work bundle reader changed during selection')
                captured=module.consume(selection)
                if kind=='intent-framing':
                    R.need(intent_bundle is None,'one exact current intent-framing bundle required')
                    intent_bundle=captured
                for ref,pair in captured['records'].items():
                    R.need(ref not in records or records[ref]==pair,
                           'ambiguous original producer revision')
                    records[ref]=copy.deepcopy(pair)
                for transition,headers in captured['transitions'].items():
                    R.need(transition not in original_routes,
                           'duplicate original Work transition producer')
                    original_routes[transition]=[h['version_ref'] for h in headers]
                receipt_path=str(Path(selection['manifest_path']).parent/'ORIGINAL-RECEIPT.json')
                receipts.extend([captured['manifest_binding'],
                                 {'ref':receipt_path,'sha256':R.sha(captured['receipt_raw'])}])
                R.need(R.sha(path.read_bytes())==digest,
                       'original Work bundle reader changed after selection')
        self.typed_receipt_raws={}
        if self.native_emissions:
            path=ROOT/'implementation/lab-runtime/local-host/t31-remaining-eighteen-0001/native_emission_bundle.py'
            R.need(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),
                   'selected native emission bundle reader absent')
            digest=R.sha(path.read_bytes());name='_cal_t31_native_emission_bundle_'+digest
            if name not in sys.modules:
                spec=importlib.util.spec_from_file_location(name,path)
                module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
            module=sys.modules[name]
            captured=module.consume(self.native_emissions[0])
            if intent_bundle is not None:
                R.need(intent_bundle['source_binding']==captured['source_binding']
                       and intent_bundle['profile_binding']==captured['profile_binding']
                       and intent_bundle['source_cut']==captured['source_cut']
                       and intent_bundle['principal_ref']==captured['identity']['principal_ref']
                       and intent_bundle['run_ref']==captured['identity']['run_ref'],
                       'intent-framing bundle and native first Session lineage differ')
                for source_kind,native_kind in (('intent','intent'),('work','work'),
                                                ('goal','goal'),('coordination','coordination-context')):
                    R.need(intent_bundle['source_inputs'][source_kind]
                           ==captured['coordination_inputs'][native_kind],
                           'intent-framing and native first Session Source original differs')
            self.native_identity=copy.deepcopy(captured['identity'])
            self.native_source_cut=copy.deepcopy(captured['source_cut'])
            self.native_source_binding=copy.deepcopy(captured['source_binding'])
            self.native_profile_binding=copy.deepcopy(captured['profile_binding'])
            self.native_package_pin=captured['package_pin']
            for ref,pair in captured['records'].items():
                R.need(ref not in records or records[ref]==pair,
                       'ambiguous native Session output revision')
                records[ref]=copy.deepcopy(pair)
            for transition,headers in captured['transitions'].items():
                R.need(transition not in original_routes,
                       'duplicate native original transition producer')
                original_routes[transition]=[h['version_ref'] for h in headers]
            for key in ('terminal_binding','process_binding','cold_binding','emission_binding','capsule_binding'):
                receipts.append(captured[key])
            self.typed_receipt_raws[captured['capsule_binding']['ref']]=captured['capsule_raw']
            R.need(R.sha(path.read_bytes())==digest,
                   'native emission reader changed during selection')
        R.need(intent_bundle is None or self.native_emissions,
               'intent-framing requires exact native first Session selection')
        product_seen=False
        for selection in self.typed_productions:
            R.need(type(selection)is dict and set(selection)=={'module_binding','entrypoint','controls'},'closed private typed producer selection required')
            binding=selection['module_binding'];R.need(type(binding)is dict and set(binding)=={'path','sha256'},'closed typed producer code binding required')
            relative=R.relative(binding['path']);path=ROOT/relative
            R.need(path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
                   and R.sha(path.read_bytes())==binding['sha256'],'independently selected typed producer code differs')
            name='_cal_t31_private_typed_'+binding['sha256']
            if name not in sys.modules:
                spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
            module=sys.modules[name];function=getattr(module,selection['entrypoint'],None)
            R.need(Path(module.__file__)==path and inspect.isfunction(function) and function.__module__==name
                   and function.__code__.co_filename==str(path) and function.__name__==selection['entrypoint'],
                   'actual selected-root typed producer function origin differs')
            compiled=compile(path.read_bytes(),str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize)
            originals=[code for code in compiled.co_consts if isinstance(code,CodeType) and code.co_name==selection['entrypoint']]
            R.need(len(originals)==1 and function.__code__==originals[0],'actual typed producer code object differs from selected original')
            # The receipt records exactly the inputs available to this producer.
            inputs={ref:{'artifact':copy.deepcopy(h),'original_sha256':R.sha(raw)} for ref,(h,raw) in records.items()}
            produced=function(records=copy.deepcopy(records),observations=copy.deepcopy(observations),controls=copy.deepcopy(selection['controls']))
            R.need(type(produced)is dict and set(produced)=={'records','receipt','consumed_input_refs','consumed_observation_refs'}
                   and type(produced['records'])is list and produced['records'] and type(produced['receipt'])is dict
                   and type(produced['consumed_input_refs'])is list and produced['consumed_input_refs']
                   and len(set(produced['consumed_input_refs']))==len(produced['consumed_input_refs'])
                   and set(produced['consumed_input_refs'])<=set(inputs)
                   and type(produced['consumed_observation_refs'])is list and produced['consumed_observation_refs']
                   and len(set(produced['consumed_observation_refs']))==len(produced['consumed_observation_refs'])
                   and set(produced['consumed_observation_refs'])<={o['observation_binding']['ref'] for o in observations},
                   'typed production input/result closure differs')
            if relative.as_posix()=='implementation/lab-runtime/local-host/t31-remaining-eighteen-0001/product_fixture_production.py':
                current_cut=produced['receipt'].get('source_cut')
                R.need(not product_seen
                       and produced['receipt'].get('schema_version')=='lab-local-product-fixture-production/v1'
                       and current_cut==selection['controls'].get('source_cut')
                       and (self.product_source_cut is None or self.product_source_cut==current_cut),
                       'one exact current product fixture Source cut required')
                self.product_source_cut=copy.deepcopy(current_cut);product_seen=True
            output_bindings=[]
            for header,raw in produced['records']:
                R.need(type(header)is dict and set(header)==R.FIELDS and type(raw)is bytes and R.sha(raw)==header['byte_sha256']
                       and header['version_ref'] not in records,'typed producer output header/original differs or shadows an input')
                records[header['version_ref']]=(copy.deepcopy(header),raw);output_bindings.append(copy.deepcopy(header))
            receipt={'schema_version':'lab-private-typed-workflow-production/v1','producer_code_binding':binding,'entrypoint':selection['entrypoint'],
                     'controls':selection['controls'],'available_original_inputs':inputs,'consumed_input_refs':produced['consumed_input_refs'],
                     'consumed_observation_refs':produced['consumed_observation_refs'],
                     'observation_original_hashes':{o['observation_binding']['ref']:{name:R.sha(raw) for name,raw in o['files'].items()}
                                                    for o in observations if o['observation_binding']['ref'] in produced['consumed_observation_refs']},
                     'api_returned_original_refs':sorted(self.api_returned_refs),'new_private_candidate_outputs':output_bindings,
                     'causal_result':produced['receipt'],'new_candidates_were_returned_by_API':False,'authority_effect':'none'}
            raw=enc(receipt);ref='private-typed-production:'+R.sha(raw);self.typed_receipt_raws[ref]=raw;receipts.append({'ref':ref,'sha256':R.sha(raw)})
            R.need(R.sha(path.read_bytes())==binding['sha256'],'typed producer code changed during production')
        unique={}
        for binding in receipts:
            R.need(binding['ref'] not in unique or unique[binding['ref']]==binding,'ambiguous actual producer receipt')
            unique[binding['ref']]=binding
        R.need(type(self.transitions)is dict and self.transitions,'exact transition output selection required')
        for transition,refs in self.transitions.items():
            R.need(type(transition)is str and transition.startswith('transition:') and type(refs)is list and refs
                   and len(refs)==len(set(refs)) and all(ref in records for ref in refs),
                   'transition must select actual returned original records')
            if transition in original_routes:
                R.need(refs==original_routes[transition],
                       'original Work transition outputs differ from sealed producer')
        return records,list(unique.values())

    def control_stamp(self):
        return R.sha(enc({'selections':self.selections,'transitions':self.transitions,
                         'typed_productions':self.typed_productions,
                         'original_bundles':self.original_bundles,
                         'native_emissions':self.native_emissions}))

    def guard(self):
        R.need(self.control_stamp()==self.stamp,
               'independently selected actual producer controls changed')
        records,receipts=self.capture()
        R.need(records==self.records and receipts==self.receipts
               and R.sha(enc({ref:{'artifact':h,'original_sha256':R.sha(raw)} for ref,(h,raw) in records.items()}))==self.record_stamp,
               'retained actual producer originals changed')
        return True

    def profile(self):
        self.guard()
        return {'records':copy.deepcopy(self.records),
                'outputs':{transition:[copy.deepcopy(self.records[ref][0]) for ref in refs]
                           for transition,refs in self.transitions.items()},
                'receipts':copy.deepcopy(self.receipts),
                'receipt_originals':{binding['ref']:self.typed_receipt_raws[binding['ref']] if binding['ref'] in self.typed_receipt_raws else R.read(Path(binding['ref'])) for binding in self.receipts},
                'originals_are_Source_current':False,'authority_effect':'none'}
