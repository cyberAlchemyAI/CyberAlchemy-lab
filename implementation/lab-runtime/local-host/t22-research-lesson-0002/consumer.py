"""Finite W04 reanalysis; candidate Lesson controls the selected population.

This is a caller's public-evidence computation, not a trusted Lab Service or a
Source-current Lesson selector. Eligibility and native permission stay separate.
"""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,math
RULE='Include every declared replay pair, retaining timeout, rejection and mismatch as explicit residue labels before calculating finite label entropy.'
PROJECT='project:cyberalchemy-v2-to-lab-migration'
def require(value,reason):
    if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)).encode()
def label(trial):
    rows=trial['observations'];require(set(rows)=={'direct','facade'},'exact paired observation required')
    if any(row['posture']=='timeout' for row in rows.values()):return 'timeout'
    if any(row['posture']!='completed' or row['returncode']!=0 for row in rows.values()):return 'rejected'
    a,b=rows['direct'],rows['facade']
    return 'parity' if a['head']==b['head'] and a['projection_sha256']==b['projection_sha256'] else 'mismatch'
def analyze(observed,lesson=None,review=None):
    trials=observed['trials'];require(len(trials)==3 and [t['sample'] for t in trials]==[1,2,3],'declared exact finite W04 cohort required')
    all_labels=[label(t) for t in trials]
    if lesson is None:
        # Explicit ablation: the completed-pair population used before the
        # Lesson is applied. It is never mislabeled the whole declared cohort.
        selected=[i for i,t in enumerate(trials) if all(r['posture']=='completed' and r['returncode']==0 for r in t['observations'].values())]
        rule='completed-pairs-only-ablation'
    else:
        require(review is not None and review['result']=='eligible-private-candidate'
                and review['lesson_sha256']==sha(encoded(lesson)),'exact reviewed candidate Lesson required')
        now=datetime.now(timezone.utc);end=datetime.fromisoformat(lesson['payload']['expires_at'])
        require(now.tzinfo is not None and end.tzinfo is not None and now<end,'candidate Lesson actual period expired')
        require(lesson['scope_ref']==PROJECT and lesson['payload']['scope_refs']==[PROJECT]
                and lesson['payload']['status']=='candidate'
                and lesson['payload']['lesson_statement']==RULE,'candidate Lesson does not apply to declared research procedure')
        require(review['scope_ref']==PROJECT and sha(encoded(observed)) in review['input_sha256s'] and len(review['input_sha256s'])==2
                and review['rule']==RULE and review['revoked'] is False,'candidate review input/scope/revocation differs')
        selected=list(range(len(trials)));rule='include-every-declared-pair'
    labels=[all_labels[i] for i in selected];require(bool(labels),'selected analysis population empty')
    counts=Counter(labels);entropy=-sum((n/len(labels))*math.log(n/len(labels)) for n in counts.values())
    return {'schema_version':'lab-T22-finite-research-reanalysis/v1-candidate','analysis_rule':rule,
            'declared_sample_size':len(trials),'analyzed_sample_size':len(labels),
            'selected_samples':[trials[i]['sample'] for i in selected],
            'excluded_samples':[t['sample'] for i,t in enumerate(trials) if i not in selected],
            'labels':labels,'label_counts':dict(sorted(counts.items())),
            'finite_label_entropy_nats':entropy,'parity_fraction_in_selected_population':counts['parity']/len(labels),
            'whole_declared_cohort_analyzed':len(labels)==len(trials),
            'performance_improvement_established':False,'population_inference':False,
            'input_sha256':sha(encoded(observed)),
            'lesson_sha256':None if lesson is None else sha(encoded(lesson)),
            'authority_effect':'none'}
