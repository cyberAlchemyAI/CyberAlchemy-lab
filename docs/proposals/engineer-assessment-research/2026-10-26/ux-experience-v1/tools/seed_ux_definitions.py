"""Add the six scoped UX meanings and their proposed ontology relations once."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
DP=ROOT/'model/definitions.json'; OP=ROOT/'model/ontology.json'
defs=json.loads(DP.read_text()); ontology=json.loads(OP.read_text())
rows=[
 ('brand-identity','Brand Identity','A Brand Identity is a versioned product promise, voice and visual direction for a declared audience, including prohibited claims and owner review routes.','One product, audience and release context.','A working brand does not establish assessment validity or trademark clearance.','The rules for how the product presents itself and what it can honestly promise.'),
 ('design-system','Design System','A Design System is a versioned set of semantic tokens, interaction rules and component contracts governing consistent interfaces across named surfaces.','One product interface release and supported modes.','A token file or component catalog alone does not prove an accessible implementation.','The reusable rules that make screens work and look coherent.'),
 ('experience-flow','Experience Flow','An Experience Flow is a role- and purpose-bound sequence of user actions, visible states, receipts and exception routes for an end-to-end task.','One actor role, task and release context.','It is distinct from a backend workflow and is not a record of a completed journey.','What a person sees and does, including recovery when something goes wrong.'),
 ('interface-screen','Interface Screen','An Interface Screen is a versioned contract for one role-visible view with content, actions, states, policy disclosures, events and accessibility behavior.','One view or routed surface in the product.','A screen specification is not rendered UI or usability evidence.','The contract for what one page or view must show and allow.'),
 ('ui-component','UI Component','A UI Component is a reusable interface control with defined semantics, states, behavior, tokens and accessibility acceptance conditions.','One reusable control pattern within the design system.','A component design does not prove all uses in context are accessible.','A reusable control such as a timer or recovery notice with tested behavior.'),
 ('analytics-event-spec','Analytics Event Specification','An Analytics Event Specification is a versioned allowlist for one event name, trigger, emitter, purpose, permitted fields, deduplication rule, retention link and metric consumers.','One operational observation kind and authorized processing context.','It is not an event occurrence, a metric result, a research permission or a reason to log sensitive content.','The contract that says exactly when an event may be recorded and what it may contain.')]
existing={d['id'] for d in defs['definitions']}
for slug,term,statement,scope,boundary,intuition in rows:
    did='ea.'+slug
    if did not in existing:
        defs['definitions'].append({'id':did,'term':term,'statement':statement,'scope':scope,
            'boundaries':[boundary],'parameters':[],'intuition':intuition})
    if did not in ontology['local_meanings']:ontology['local_meanings'].append(did)
    node=''.join(s.capitalize() for s in slug.split('-'))
    if node not in {x['id'] for x in ontology['node_types']}:
        ontology['node_types'].append({'id':node,'meaning':did,'visibility':'protected-design' if slug=='analytics-event-spec' else 'participant-visible-candidate'})
edges=[('presents_brand','Product','BrandIdentity'),('governs_interface','DesignSystem','InterfaceScreen'),
 ('uses_component','InterfaceScreen','UiComponent'),('follows_flow','InterfaceScreen','ExperienceFlow'),
 ('emits_specified_event','InterfaceScreen','AnalyticsEventSpec'),('measures_ux','AnalyticsEventSpec','ProductSuccessMetric'),
 ('applies_brand','DesignSystem','BrandIdentity')]
for id,frm,to in edges:
    if id not in {x['id'] for x in ontology['edge_types']}:
        ontology['edge_types'].append({'id':id,'from':frm,'to':to})
ontology['invariants'] += [x for x in [
 'An AnalyticsEventSpec is not a SessionEvent occurrence or a ProductSuccessMetric result.',
 'An InterfaceScreen and UIComponent remain candidate contracts until browser and participant evidence support them.',
 'BrandIdentity cannot promote a provisional assessment to a validated hiring claim.'] if x not in ontology['invariants']]
DP.write_text(json.dumps(defs,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
OP.write_text(json.dumps(ontology,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
print('UX definitions and ontology:',len(defs['definitions']),len(ontology['node_types']),len(ontology['edge_types']))
