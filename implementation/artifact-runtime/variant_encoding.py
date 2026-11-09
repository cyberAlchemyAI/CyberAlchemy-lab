"""Bounded algebraic-data encoding from explicit source-selected group metadata."""
from copy import deepcopy
from exact_io import pointer, require, encode

def expand(groups, documents):
    require(isinstance(groups,list) and len(groups)<=100,'variant-group-bound')
    require(isinstance(documents,dict) and len(documents)<=100,'variant-document-bound')
    result=[]
    for group in groups:
        require(isinstance(group,dict) and set(group)=={'source','selector','tag','collection'},'invalid-variant-group')
        require(isinstance(group['tag'],str) and 0<len(group['tag'])<=256 and type(group['collection']) is bool,'invalid-variant-tag')
        require(group['source'] in documents,'variant-source-missing')
        selected=pointer(documents[group['source']],group['selector'])
        if group['collection']:
            require(isinstance(selected,list) and len(selected)<=256,'variant-collection-bound')
            rows=selected
        else:rows=[selected]
        for row in rows:
            require(len(result)<1024,'variant-result-bound')
            result.append({'tag':group['tag'],'fields':{'value':deepcopy(row)}})
    require(len(encode(result))<=16777216,'variant-byte-bound')
    return result