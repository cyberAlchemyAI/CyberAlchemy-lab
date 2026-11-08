from pathlib import Path
from ..execution.extension_runtime import lean_ref,lean_string
from .mapper import normalize
HERE=Path(__file__).resolve().parent
SCHEMA=HERE/'evidence-collection.schema.json'
SCOPE='Complete selected versioned evidence-collection source projection under supplied assessment truth; roots unchanged; no core application authorization.'
def modules():return [('EvidenceCollectionSemantics',HERE/'EvidenceCollectionSemantics.lean')]
def frame_lean(f):return '⟨'+', '.join([lean_string(f['profile']),lean_ref(f['context']),lean_ref(f['subject']),lean_ref(f['target']),lean_string(f['scope']),str(f['epoch'])])+'⟩'
def assessment_lean(a):return '⟨'+', '.join([lean_string(a['ref']),lean_string(a['mode']),lean_ref(a['subject']),lean_ref(a['target']),lean_string(a['scope']),'true' if a['accepted'] else 'false'])+'⟩'
def assertion_lean(a):return '⟨'+', '.join([lean_string(a['id']),lean_string(a['kind']),lean_ref(a['source']),lean_ref(a['target']),lean_string(a['qualifiers'].get('conformance_scope','')),lean_string(a['kind_version'])])+'⟩'
def render(p):
    f=p['request']['frame'];roots='['+', '.join(map(lean_string,p['roots']))+']'
    refs='['+', '.join('⟨'+lean_string(r['token'])+', '+lean_string(r['source_identity'])+'⟩' for r in p['references'])+']'
    assessments='['+', '.join(assessment_lean(a) for a in p['graph']['assessments'])+']'
    assertions='['+', '.join(assertion_lean(a) for a in p['graph']['assertions'])+']'
    supports='['+', '.join(assessment_lean(a) for a in p['supports'])+']'
    nodes='['+', '.join('⟨'+lean_ref(n['ref'])+', '+lean_string(n['kind'])+'⟩' for n in p['graph']['nodes'])+']'
    policies='['+', '.join('⟨'+lean_string(k['id'])+', '+lean_string(k['version'])+', ['+', '.join('('+lean_string(pair['source_kind'])+', '+lean_string(pair['target_kind'])+')' for pair in k['pairs'])+']⟩' for k in p['source']['proposal']['before']['registry']['kinds'])+']'
    return '\n'.join(['import EvidenceCollectionSemantics','set_option maxRecDepth 2048','open RelationalExtensions.Evidence','namespace CollectionInstance',
        'def frame : Frame := '+frame_lean(f),'def selected : Assertion := '+assertion_lean(p['selected']),
        'def source_frame : Frame := '+frame_lean(p['actual_frame']),
        'def source : Source := ⟨'+lean_string(p['identity'])+', source_frame, '+assertions+', '+assessments+', '+roots+', '+nodes+', '+policies+'⟩',
        'def references : List EvidenceRef := '+refs,
        'theorem source_frame_exact : source_frame = frame := by decide',
        'theorem all_supports : (project source selected frame references).evidence = '+supports+' := by decide',
        'theorem retained_roots : (project source selected frame references).roots = '+roots+' := by decide',
        'theorem exact_meaning : (∃ a, a ∈ supports source selected frame references) ↔ Meaning source selected frame references := projection_sound_complete source selected frame references',
        '#print axioms source_frame_exact','#print axioms all_supports','#print axioms retained_roots','#print axioms exact_meaning','end CollectionInstance',''])
def result(p):return {'schema':'relational.evidence-collection-result/v1','profile':p['request']['profile'],
    'policy':'any-current-accepted-exact-match; all-valid-supports-in-source-order','frame':p['request']['frame'],'source_identity':p['identity'],
    'source_assertion':p['selected']['id'],'references':p['references'],'conforms':bool(p['supports']),'supports':p['supports'],
    'roots_before':p['roots'],'roots_after':p['roots'],'claim_scope':'Exact selected source assertion/evidence-collection projection; no whole graph qualification or external assessment truth.',
    'authority_effect':'none','application_authorized':False}
