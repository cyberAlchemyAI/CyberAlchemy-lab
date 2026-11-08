"""Precompute the existing lexical inputs without changing ranking or corpus.

The browser retains its original preparation path as an independent fallback.
The review's parity check compares both paths across every entry and judgment.
"""
import re
import unicodedata
from collections import Counter
from functools import lru_cache

VERSION = 'lab-lexical/v1'
STOP = set('a an and are as at be been but by can could did do does enough for from had has have how i in is it its judge know lets me of on or our should the their them there these they this those to was way we were what when where whether which who why will with would you your versus vs'.split())
EQUIVALENTS = dict(approval='approve', approves='approve', approved='approve', approving='approve', accepted='accept', admitted='admit', admission='admit', permissions='permission', authorisation='authorization', ends='end', ended='end', ending='end', stops='stop', stopped='stop', stopping='stop', definitions='definition', defining='definition', defined='definition', define='definition', calculation='calculate', calculations='calculate', calculated='calculate', calculating='calculate', governance='govern', governing='govern', governed='govern', proof='prove', proves='prove', proven='prove', proving='prove', compiling='compile', compiled='compile', compilation='compile')


def normalize(value):
    value = unicodedata.normalize('NFKD', value)
    return re.sub('[\u0300-\u036f]', '', value).lower().replace('?', '').strip()


@lru_cache(maxsize=50000)
def stem(word):
    word = EQUIVALENTS.get(word, word)
    if len(word) > 6 and word.endswith('ies'):
        return word[:-3] + 'y'
    if len(word) > 6 and word.endswith('ing'):
        return word[:-3]
    if len(word) > 5 and word.endswith('ed'):
        return word[:-2]
    if len(word) > 5 and word.endswith('es'):
        return word[:-2]
    if len(word) > 4 and word.endswith('s') and not word.endswith(('ss', 'us')):
        return word[:-1]
    return word


def terms(value):
    value = re.sub(r"\b(?:doesn't|don't|isn't|aren't|can't|won't|shouldn't|wouldn't|couldn't)\b", ' ', normalize(value), flags=re.ASCII)
    value = re.sub(r"['’]s\b", '', value, flags=re.ASCII)
    return [stem(word) for word in re.findall(r'[a-z0-9]+(?:/[0-9]+)?', value) if word not in STOP]


def unique(values):
    return list(dict.fromkeys(values))


def prepare_entry(entry):
    aliases = entry.get('aliases', [])
    body = terms(entry['text'])
    words = unique(re.findall('[a-z0-9]+', normalize(entry['title'] + ' ' + ' '.join(aliases) + ' ' + entry['text'])))
    return {**entry, 'prepared': {
        'version': VERSION,
        'title': unique(terms(entry['title'])),
        'aliases': unique(terms(' '.join(aliases))),
        'topics': [' '.join(terms(alias)) for alias in aliases],
        'body': list(Counter(body).items()),
        'length': len(body),
        'lexicon': [[word, stem(word)] for word in words if word not in STOP],
    }}


def compile_entries(entries):
    prepared = [prepare_entry(entry) for entry in entries]
    df, lexicon, total = Counter(), {}, 0
    for entry in prepared:
        feature = entry['prepared']
        total += feature['length']
        for word in unique(feature['title'] + feature['aliases'] + [word for word, _ in feature['body']]):
            df[word] += 1
        for word, root in feature.pop('lexicon'):
            lexicon[word] = root
    return prepared, {'version': VERSION, 'df': list(df.items()), 'lexicon': list(lexicon.items()),
                      'average': total / max(1, len(prepared))}
