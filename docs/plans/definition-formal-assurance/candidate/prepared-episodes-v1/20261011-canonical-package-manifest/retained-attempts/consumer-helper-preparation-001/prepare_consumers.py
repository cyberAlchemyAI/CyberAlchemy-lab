from pathlib import Path
import ast
p=Path(__file__).resolve().parent;unit=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.canonical-package-manifest');prev=unit.parent/'cal.definition.canonical-package-home';s=(prev/'inspect_carrier_consumers.py').read_text()
s=s.replace('Exact CPH manifest observations and pure declaration-helper fixtures;no selected real home.','Exact CPM current carrier and isolated membership/nesting declaration helper observations.')
s=s.replace('20261011-canonical-package-home','20261011-canonical-package-manifest').replace('CPH','CPM')
a=s.index(';caprow=');z=s.index('\n paths=',a);s=s[:a]+s[z:]
s=s.replace("'Definition_hostile_checker':b.ROOT/'authority/definitions/candidates/0008-canonical-package-home/validate.py','current_Capability_successor':b.ROOT/caprow['artifact_path'],'current_Capability_schema':b.ROOT/caprow['schema_path'],","'Definition_hostile_checker':b.ROOT/'authority/definitions/candidates/0010-artifact-surface-foundation-revision/validate.py',")
s=s.replace("['recovery_boundary_ref','governed_home_candidates','canonical_at_relations','facet_identities','facet_authority_scopes','movement_evidence','global_index_bindings']","['recovery_boundary_ref','governed_membership_evidence','entry_identity_bindings','admitted_resolution_results','registry_evidence','nearest_package_bindings','membership_change_evidence']")
a=s.index(' for q in sorted(paths[\'Definition_hostile_checker\']');z=s.index(" ck('four-Definition-hostile-witnesses'",a)
s=s[:a]+" for name in ['undeclared-carrier.json','implicit-nested-package.json']:\n  q=paths['Definition_hostile_checker'].parent/'fixtures/invalid'/name;doc=json.loads(q.read_bytes());refs[q.name]=b.ref(q);before=copy.deepcopy(doc['subject']);failures=sorted(hostile.hostile(doc['subject']));ck('Definition-declared-hostile-'+q.name,doc['expected_rule'] in failures and before==doc['subject']);definition_results.append({'fixture_id':doc['fixture_id'],'expected_rule':doc['expected_rule'],'failures':failures,'scope':'Source revision ad hoc declared membership/nesting subject only;not a canonical manifest instance.'})\n"+s[z:]
s=s.replace("ck('four-Definition-hostile-witnesses',len(definition_results)==4)","ck('two-relevant-Definition-hostile-witnesses',len(definition_results)==2)")
a=s.index(" cap=docs['current_Capability_successor']");z=s.index(' proposed=',a);s=s[:a]+s[z:]
a=s.index(' findings=');z=s.index(' for x in findings:',a)
s=s[:a]+''' findings=[{'finding_id':'CPM-CONSUMER-FINDING-001','issue':'Manifest owner,unit,aggregate and package-root fields are nonempty strings;schema/helper accept arbitrary references. Authentic home/owner/unit/recovery correspondence remains unaccepted.'},
 {'finding_id':'CPM-CONSUMER-FINDING-002','issue':'Schema accepts duplicate nonself paths while helper rejects them;schema and helper accept omission of a nonself canonical member when no actual governed inventory is provided. Complete governed-surface and unique-entry correspondence requires separate evidence.'},
 {'finding_id':'CPM-CONSUMER-FINDING-003','issue':'Declared canonical type/count1passes with an unregistered type;no linked admitted result,input carrier or current registry evidence is consumed by the helper. Direct package-validator body does not run resolve and wrapper retains explicit legacy registry route. Actual admitted resolution correspondence remains pending.'},
 {'finding_id':'CPM-CONSUMER-FINDING-004','issue':'Unbound child manifest,parent relation and duplicate independent nested declarations can pass schema/helper. Closed carrier has no direct recovery,nearest-package,membership-change or result-evidence fields. Actual child carrier existence,relation kinds,nearest containment and identity/type preservation maps remain pending.'},
 {'finding_id':'CPM-CONSUMER-FINDING-005','issue':'Current C53 Definition and C70carrier admission overlays remain separate from embedded candidate body/stale residue. Registry Context migration route remains unaccepted and no actual home/manifest instance,migration or authority was created.'}]
'''+s[z:]
s=s.replace("cal.definition.artifact-type-resolution/delivery-manifest.json","cal.definition.canonical-package-home/delivery-manifest.json")
a=s.index(",'current_Capability_successor_contract':");z=s.index(",'accepted_semantic_map_refs':",a);s=s[:a]+s[z:]
s=s.replace('live_migration_or_successor_consumer_executed','live_migration_consumer_executed').replace('No accepted owner/unit/home,canonical source,facet,registry,index,movement,successor or migration correspondence;no new instance or canonical-home selection.','No accepted owner/home,governed membership,role,result,registry,nested,nearest-package,movement or migration correspondence;no new instance or home selection.')
needle=" probe('generated-projection-declared-count-one',lambda x:x['surface_entries'][2].update(resolution_count=1),True,[])"
assert needle in s
s=s.replace(needle,needle+"\n probe('unwitnessed-governed-member-omitted',lambda x:x['surface_entries'].pop(1),True,[])\n probe('duplicate-independent-nested-declarations',lambda x:x.update(nested_packages=[copy.deepcopy(nested),copy.deepcopy(nested)]),True,[])\n probe('unsupported-nearest-package-evidence',lambda x:x.update(nearest_package_evidence={'directory':'contracts','manifest':'fixture:unaccepted'}),False,[])")
s=s.replace("'checker':b.UNIT/'inspect_carrier_consumers.py',","'checker':b.UNIT/'inspect_carrier_consumers.py','prior_CPH_consumer_findings':prev_consumer,")
s=s.replace(" paths={'current_registry':", " prev_consumer=b.BASE/'definitions/cal.definition.canonical-package-home/carrier-consumer-inspection.json'\n paths={'current_registry':")
needle=" ck('current-143-contract-catalog-preserved',len(registry['admitted_contracts'])==143)"
assert needle in s
s=s.replace(needle,needle+"\n ck('five-prior-CPH-findings-retained-with-no-accepted-maps',len(docs['prior_CPH_consumer_findings']['unresolved_consumer_findings'])==5 and docs['prior_CPH_consumer_findings']['accepted_semantic_map_refs']==[])")
ast.parse(s)
with (unit/'inspect_carrier_consumers.py').open('x') as f:f.write(s)
capture=(p.parent/'20261011-canonical-package-home/capture_consumer.py').read_text().replace('cal.definition.canonical-package-home','cal.definition.canonical-package-manifest');ast.parse(capture)
with (p/'capture_consumer.py').open('x') as f:f.write(capture)
print('Prepared CPM exact current carrier inspection and durable capture;frozen typed inputs unchanged.')
