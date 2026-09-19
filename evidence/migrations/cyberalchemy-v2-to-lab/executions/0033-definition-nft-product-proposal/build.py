"""Prepare an explicitly unselected NFT product proposal for owner review."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2'
sys.path.insert(0,str(ROOT/'tooling/importers'))
import capability_inventory_import as tool
sys.path.insert(0,str(ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0026-remaining-targets-review-batch'))
import engine
GAP=HERE.parent/'0024-definition-nft-gap-review';PREV=HERE.parent/'0032-trusted-dataset-product-import'
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':tool.sha(p)}
def dump(p,obj):
    t=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=t:raise ValueError('Preserve existing proposal')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
def build():
    for b in tool.read(PREV/'verification.json')['bindings']:
        if tool.sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact drift')
    gap=tool.read(GAP/'result.json')
    for b in gap['source_bindings']:
        if tool.sha(SOURCE/b['path'])!=b['sha256']:raise ValueError('Source drift')
    registry=tool.load_registry();cap=gap['source_record'];base={'status':'candidate-unadmitted','authority_effect':'none','scope_ref':registry['scope']}
    choices=[
      {'id':'product','proposal':'Definition NFT is a standalone optional representation Product attached to a completed KEP share. It neither changes KEP ownership nor grants rights to the definition.'},
      {'id':'uniqueness','proposal':'At most one successful finalized mint per exact definition-version commitment within this Product on Solana devnet, across sharing users. A repeated request returns the existing result; another user cannot mint a second copy under this rule.'},
      {'id':'retry','proposal':'Never automatically create a replacement mint transaction. An uncertain outcome blocks another attempt until reconciliation proves no mint succeeded. A proven failed attempt requires a fresh user confirmation before retry. No burns, replacements or successor mints in v1.'},
      {'id':'representation','proposal':'Generate a deterministic SVG definition card and versioned JSON metadata from the exact version commitment and user-approved display fields. The default card shows only the version commitment. Never read or publish private definition content automatically. Store the exact bytes and their digests; content changes create a new representation.'},
      {'id':'storage','proposal':'Keep a content-addressed local review/export copy. Before minting, require an explicitly configured content-addressed retrieval location and a successful exact-byte readback of media and metadata. Promise verifiable bytes at confirmation, not permanent availability; show that limit to the user. Provider choice and deployment remain separate implementation work.'},
      {'id':'wallet','proposal':'Authenticate the sharing Knowledge Identity separately, then require its intended receiving wallet to sign a one-use challenge bound to the identity, completed share, version, representation, devnet, intended mint attempt and expiry. The same wallet receives the NFT and pays the network fee. Wallet change or expired/reused challenge requires new verification.'},
      {'id':'confirmation','proposal':'Show the exact representation preview, receiving/paying wallet, network, fee estimate and permitted fee ceiling, and storage availability limit before a separate mint confirmation. Changed commitments, wallet or exceeded fee ceiling invalidate confirmation. Declining creates no transaction and no mint fee.'}
    ]
    statements=gap['prepared_fields']['acceptance_conditions']+[c['proposal'] for c in choices]
    pid='lab:definition-nft#CA2-PRODUCT-DEFINITION-NFT'
    product={**base,'node_id':pid,'kind':'product','name':'Definition NFT','purpose':cap['outcome'],'identity_boundary':'Optional representation of an exact shared definition version; no KEP membership change, definition ownership, copyright, licensing, truth, publication rights or mainnet behavior.','owner_ref':'Definition NFT product owner','owner_route':tool.owner(cap)}
    capability={**gap['prepared_fields'],'product_ref':pid,'acceptance_conditions':statements}
    engine.validate_graph({'schema_version':'cal-review-graph/v1','authority_effect':'none','nodes':[product,capability],'relations':[]})
    semantics={
      cap['product_ref']:product['purpose'],cap['obligation_registry_ref']:'Proposed required behavior: '+ ' '.join(statements),
      'CA2-ACTOR-DEFINITION-SHARING-USER':'The authenticated user who completed the exact KEP share and requests optional representation generation and minting.',
      'CA2-ACTOR-KEP-KNOWLEDGE-RECIPIENT':'The recipient of the completed KEP share; not the NFT receiving wallet by implication.',
      'CA2-ACTOR-DEFINITION-NFT-REPRESENTATION-PRODUCER':choices[3]['proposal'],
      'CA2-ACTOR-SOLANA-DEVNET-MINT-REALIZATION':'The later exact implementation that attempts the separately confirmed devnet mint and reports a correlated result.',
      'CA2-IDENTITY-DEFINITION-SHARING-USER':choices[5]['proposal'],
      'CA2-CAPABILITY-CONSUMER-DEFINITION-NFT-DEVNET-TRIAL':'The bounded non-production consumer of generation and optional confirmed devnet minting.',
      'CA2-CAP-CONTRACT-DEFINITION-NFT-EXACT-SHARE':'Requires completed share identity, sharing Knowledge Identity and exact definition-version commitment; all resolve to the same completed KEP share.',
      'CA2-CAP-CONTRACT-DEFINITION-NFT-GENERATION-REQUEST':'Requires an exact share and explicit display-field approval. Generation permission does not include publishing private content or minting.',
      'CA2-CAP-CONTRACT-DEFINITION-NFT-MINT-CONFIRMATION':choices[5]['proposal']+' '+choices[6]['proposal'],
      'CA2-CAP-CONTRACT-DEFINITION-NFT-REPRESENTATION':choices[3]['proposal']+' '+choices[4]['proposal'],
      'CA2-CAP-CONTRACT-DEFINITION-NFT-NO-EFFECT-RESULT':'Records the exact request/version, declined or unconfirmed state, no transaction submission and no mint fee; does not assert that hosting or generation is globally free.',
      'CA2-CAP-CONTRACT-DEFINITION-NFT-MINT-RECEIPT':'Records the attempt, exact share/version/representation, confirmed wallet and devnet, transaction identity when present, and finalized success, proven failure, or unresolved outcome. Unresolved is not a terminal success or proven failure.',
      'CA2-CAP-CONTRACT-DEFINITION-NFT-TYPED-FAILURE':'Distinguishes invalid share, private display data, storage mismatch/unavailable, invalid wallet challenge, stale confirmation, fee-ceiling breach, existing mint, proven transaction failure and unresolved outcome; preserves retry rules.',
      'CA2-CAP-POLICY-DEFINITION-NFT-EXACT-VERSION':choices[1]['proposal']+' '+choices[2]['proposal'],
      'CA2-CAP-POLICY-DEFINITION-NFT-SEPARATE-CONFIRMATION':choices[6]['proposal'],
      'CA2-CAP-POLICY-DEFINITION-NFT-NO-CONFIRMATION-NO-EFFECT':'No valid independent mint confirmation means no transaction submission and no mint fee.',
      'CA2-CAP-POLICY-DEFINITION-NFT-RIGHTS-SEPARATION':choices[0]['proposal'],
      'CA2-CAP-POLICY-DEFINITION-NFT-SOLANA-DEVNET-ONLY':'Only the explicitly bound Solana devnet environment is in scope; no mainnet or production funds.'}
    assert set(semantics)==set(gap['unresolved_identities'])
    for ident,meaning in semantics.items():dump(HERE/'references'/(ident+'.json'),{'id':ident,'meaning':meaning,'status':'proposed-awaiting-owner-selection','authority_effect':'none','source_or_proposal':'New local proposal; not a recovered source declaration.','source_bindings':gap['source_bindings']})
    proposal={'status':'proposed-awaiting-owner-selection','imported':False,'authority_effect':'none','choices':choices,'product':product,'capability':capability,'source_bindings':gap['source_bindings'],'reference_bindings':[bind(p) for p in sorted((HERE/'references').glob('*.json'))],'limitations':['Semantic proposal only; executable API schemas, cryptographic verification, wallet integration, network/storage providers and runtime implementation remain separate.','No proposal choice has been recorded as user-approved; no capability added to active store.']}
    dump(HERE/'proposal.json',proposal);return proposal
if __name__=='__main__':
    p=build();print(json.dumps({'proposal_choices':len(p['choices']),'reference_proposals':len(p['reference_bindings']),'imported':False}))
