"""Typed finite positive rules; independently supplied roots are never inferred."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'input'))
import decoder as d
s=d.s
BASE=Path(__file__).resolve().parent
SORTS={'reference','effect','scope','epoch','text'}
ROOT_SORTS=['reference','effect','scope','epoch']
CORE=[{'id':'Conforms','version':'v1','sorts':['reference'],'role':'ordinary'},
      {'id':'Admitted','version':'v1','sorts':ROOT_SORTS,'role':'protected'},
      {'id':'CheckedRoot','version':'v1','sorts':ROOT_SORTS,'role':'checked-root'}]


def identity(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def fields(value,required,label):
    s.require(isinstance(value,dict) and set(value)==set(required),'invalid '+label+' fields')


def text(value,label):
    s.require(isinstance(value,str) and value,'empty or non-string '+label)
    value.encode('utf-8',errors='strict')
    return value


def value(raw):
    s.require(isinstance(raw,dict) and isinstance(raw.get('kind'),str) and raw['kind'] in SORTS,'unknown value sort')
    kind=raw['kind']
    if kind=='reference':
        fields(raw,['kind','id','version'],'version reference');text(raw['id'],'artifact identity');text(raw['version'],'artifact version')
    elif kind=='epoch':
        fields(raw,['kind','value'],'epoch');s.require(type(raw['value']) is int and raw['value']>=0,'epoch must be a nonnegative integer')
    else:
        fields(raw,['kind','value'],'literal value');text(raw['value'],'literal')
    return deepcopy(raw)


def tuple_values(target,effect,scope,epoch):
    fields(target,['id','version'],'protected target version')
    return [value({'kind':'reference',**target}),value({'kind':'effect','value':effect}),
            value({'kind':'scope','value':scope}),value({'kind':'epoch','value':epoch})]


def normalize(request):
    fields(request,['schema','snapshot_epoch','domain','predicates','rules','facts','roots','root_assessments'],'inference request')
    s.require(request['schema']=='relational.inference-input/v1','unknown inference input version')
    s.require(type(request['snapshot_epoch']) is int and request['snapshot_epoch']>=0,'invalid captured epoch')
    s.require(all(isinstance(request[k],list) for k in ['domain','predicates','rules','facts','roots','root_assessments']),'inference inventories must be lists')
    domain=[value(v) for v in request['domain']]
    s.require(domain and len({identity(v) for v in domain})==len(domain),'empty or duplicate active domain')
    def in_domain(v):return v in domain
    signatures=[];by_id={}
    for raw in request['predicates']:
        fields(raw,['id','version','sorts','role'],'predicate')
        text(raw['id'],'predicate identity');text(raw['version'],'predicate version')
        s.require(raw['id'] not in by_id,'duplicate predicate identity')
        s.require(isinstance(raw['sorts'],list) and all(isinstance(x,str) and x in SORTS for x in raw['sorts']),'unknown predicate argument sort')
        s.require(isinstance(raw['role'],str) and raw['role'] in {'ordinary','protected','checked-root','root-carrier'},'unknown predicate role')
        if raw['role'] in {'protected','checked-root','root-carrier'}:s.require(raw['sorts']==ROOT_SORTS,'protected/carrier signatures must match all four exact coordinates')
        if raw['role']=='protected':s.require(raw['id']=='Admitted','unknown protected predicate')
        if raw['role']=='checked-root':s.require(raw['id']=='CheckedRoot','a renamed predicate cannot create roots')
        if raw['id'] in {'Admitted','CheckedRoot'}:s.require(raw in CORE,'reserved protected signature or role altered')
        normalized={**deepcopy(raw),'hash':identity(raw)};signatures.append(normalized);by_id[raw['id']]=normalized
    for mandatory in CORE:s.require(any(p=={**mandatory,'hash':identity(mandatory)} for p in signatures),'required core predicate changed or absent')
    def pred(raw):
        s.require(isinstance(raw,dict) and isinstance(raw.get('predicate'),str) and raw['predicate'] in by_id,'undeclared predicate')
        sig=by_id[raw['predicate']]
        s.require(raw.get('version',sig['version'])==sig['version'],'wrong predicate version')
        return sig
    def atom(raw):
        s.require(isinstance(raw,dict) and set(raw) in [{'predicate','terms'},{'predicate','version','terms'}],'unknown ground atom fields')
        sig=pred(raw);s.require(isinstance(raw['terms'],list) and len(raw['terms'])==len(sig['sorts']),'wrong atom arity')
        args=[value(x) for x in raw['terms']]
        s.require([x['kind'] for x in args]==sig['sorts'] and all(in_domain(x) for x in args),'wrong sort or outside active domain')
        return {'predicate':{k:sig[k] for k in ['id','version','hash']},'values':args}
    assessments={}
    for raw in request['root_assessments']:
        fields(raw,['id','version','source'],'root assessment reference')
        key=(text(raw['id'],'assessment identity'),text(raw['version'],'assessment version'))
        fields(raw['source'],['path','sha256'],'root assessment source binding')
        text(raw['source']['path'],'root assessment path');text(raw['source']['sha256'],'root assessment hash')
        s.require(key not in assessments,'duplicate root assessment identity');s.check_binding(raw['source'])
        document=d.decode((s.ROOT/raw['source']['path']).read_bytes())
        fields(document,['schema','receipt_id','receipt_version','mode','accepted','target_version','effect','scope','epoch','authority_effect','claim_ceiling'],'root assessment')
        s.require(document['schema']=='relational.existing-admission-receipt/v1-candidate' and document['mode']=='existing-admission','wrong root evidence type or role')
        s.require(document['accepted'] is True,'unaccepted existing-admission evidence')
        s.require(document['receipt_id']==raw['id'] and document['receipt_version']==raw['version'],'root assessment exact identity mismatch')
        tuple_values(document['target_version'],document['effect'],document['scope'],document['epoch'])
        s.require(document['authority_effect']=='none','candidate evidence cannot perform an authority transition')
        text(document['claim_ceiling'],'root assessment truth boundary')
        assessments[key]=(raw,document)
    roots=[];root_ids=set()
    for raw in request['roots']:
        fields(raw,['id','target_version','effect','scope','epoch','assessment_ref'],'checked root')
        s.require(text(raw['id'],'root identity') not in root_ids,'duplicate root identity');root_ids.add(raw['id'])
        fields(raw['assessment_ref'],['id','version','sha256'],'root assessment identity')
        ref=raw['assessment_ref'];s.require((ref['id'],ref['version']) in assessments,'root evidence reference absent')
        assessment,document=assessments[(ref['id'],ref['version'])]
        s.require(ref['sha256']==assessment['source']['sha256'],'wrong root receipt digest')
        s.require(all(raw[k]==document[k] for k in ['target_version','effect','scope','epoch']),'root version/effect/scope/epoch differs from independent assessment')
        s.require(raw['epoch']==request['snapshot_epoch'],'root belongs to another captured epoch')
        args=tuple_values(raw['target_version'],raw['effect'],raw['scope'],raw['epoch'])
        s.require(all(in_domain(v) for v in args),'root coordinate outside finite domain')
        roots.append({'id':raw['id'],'values':args,'assessment_source':assessment['source']})
    facts=[atom(raw) for raw in request['facts']]
    for fact in facts:
        role=by_id[fact['predicate']['id']]['role']
        if role in {'protected','root-carrier','checked-root'}:
            s.require(any(root['values']==fact['values'] for root in roots),'fabricated protected/root-carrier base fact')
    # Root leaves originate only in the independent supplied inventory. This
    # adds a CheckedRoot observation, never an Admitted conclusion.
    for root in roots:
        sig=by_id['CheckedRoot'];fact={'predicate':{k:sig[k] for k in ['id','version','hash']},'values':root['values']}
        if fact not in facts:facts.append(fact)
    s.require(len({identity(f) for f in facts})==len(facts),'duplicate initial facts')
    rules=[];rule_keys=set()
    for raw in request['rules']:
        fields(raw,['id','version','head','body'],'positive rule');text(raw['id'],'rule identity');text(raw['version'],'rule version')
        s.require((raw['id'],raw['version']) not in rule_keys,'ambiguous rule/version identity');rule_keys.add((raw['id'],raw['version']))
        s.require(isinstance(raw['body'],list),'rule body must be a positive premise list')
        var_sorts={};body_variables=set();patterns=[]
        for index,pattern in enumerate([*raw['body'],raw['head']]):
            s.require(isinstance(pattern,dict) and set(pattern) in [{'predicate','terms'},{'predicate','version','terms'}],'unsupported negation, function, constraint or pattern field')
            sig=pred(pattern);s.require(isinstance(pattern['terms'],list) and len(pattern['terms'])==len(sig['sorts']),'wrong pattern arity')
            terms=[]
            for term,sort in zip(pattern['terms'],sig['sorts']):
                s.require(isinstance(term,dict) and set(term) in [{'variable'},{'constant'}],'generated term, arithmetic or unknown expression unsupported')
                if 'variable' in term:
                    name=text(term['variable'],'variable');s.require(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',name),'unsupported variable identifier')
                    s.require(name not in var_sorts or var_sorts[name]==sort,'same variable used with incompatible sorts');var_sorts[name]=sort
                    if index<len(raw['body']):body_variables.add(name)
                    terms.append({'variable':name})
                else:
                    const=value(term['constant']);s.require(const['kind']==sort and in_domain(const),'rule literal changes sort or introduces fresh identity/value')
                    terms.append({'constant':const})
            patterns.append({'predicate':{k:sig[k] for k in ['id','version','hash']},'terms':terms})
        s.require(set(var_sorts)==body_variables,'every variable must occur in a positive body premise')
        s.require(by_id[raw['head']['predicate']]['role']!='checked-root','rules cannot produce independent root observations')
        names=sorted(var_sorts)
        for pattern in patterns:
            for term in pattern['terms']:
                if 'variable' in term:term['slot']=names.index(term.pop('variable'))
        normalized={'id':raw['id'],'version':raw['version'],'variables':[{'name':name,'sort':var_sorts[name]} for name in names],
                    'head':patterns[-1],'body':patterns[:-1]}
        normalized['hash']=identity({'source_rule':raw,'resolved_rule':normalized,'predicate_definitions':signatures})
        rules.append(normalized)
    result={'schema':'relational.inference-normal-form/v1','snapshot_epoch':request['snapshot_epoch'],
            'domain':domain,'predicates':signatures,'rules':rules,'facts':facts,'roots':roots,
            'raw_input_identity':identity(request),'authority_effect':'none','protected_policy_status':'requires-I04-lineage-review',
            'truth_boundary':'Conformance/base fact truth and the independently supplied existing-admission assessment truth are assumptions; no real authority effect is created.'}
    result['normal_form_identity']=identity(result)
    return result
