"""Record collectible variants direction without treating proposed settings as approved."""
import copy,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0033-definition-nft-product-proposal'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def dump(p,obj):
    text=json.dumps(obj,indent=2,sort_keys=True)+'\n'
    if p.exists() and p.read_text()!=text:raise ValueError('Preserve existing proposal')
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def revise():
    receipt=read(PREV/'verification.json')
    for b in receipt['bindings']+[receipt['active_store']]:
        if sha(ROOT/b['path'])!=b['sha256']:raise ValueError('Previous artifact changed')
    old=read(PREV/'proposal.json');p=copy.deepcopy(old);prior={v['id']:v['proposal'] for v in old['choices']}
    replacement={
      'product':'Definition NFT represents an exact shared definition as collectible visual card editions. Different visual variants share the same base image and exact definition version. Card transfer does not change KEP ownership, access or definition rights.',
      'uniqueness':'Configure named visual variants and a positive edition size for each. A card copy is identified by collection, variant and serial number within that edition. At most one successful finalized mint may occupy each copy identity; other configured copies are intentional editions, not duplicates. Proposed v1 rule: freeze the collection manifest before its first mint; changed artwork or edition sizes require a new explicitly identified collection.',
      'retry':'A retry keeps the same card-copy identity and cannot consume another edition slot. An uncertain outcome blocks a replacement attempt for that copy until reconciliation establishes its outcome. A proven failure requires fresh confirmation. No automatic replacement transaction or remint of a successfully minted copy.',
      'representation':'Use one explicitly approved base image and named visual treatments to create related card variants. Bind the base-image digest, variant image digest, collection manifest, serial number and exact definition version in each copy metadata. Preview every variant before freezing the collection. Private definition content is never included automatically. Artwork and renderer selection remain separate choices.',
      'wallet':'For initial minting, authenticate the sharing Knowledge Identity and verify its receiving/paying wallet with a one-use challenge bound to the exact collection, variant, copy, representation, devnet and expiry. Later card transfers are authorized by the current NFT holder; receiving a card does not grant KEP access or require pretending that the recipient is the original sharer.',
      'confirmation':'Show collection, visual variant, copy number, edition size, exact preview, receiving/paying wallet, devnet, fee estimate/ceiling and storage availability limit before separate mint confirmation. Changed commitments or exceeded fee ceiling require fresh confirmation. Declining causes no submission or mint fee.'}
    for choice in p['choices']:
        if choice['id'] in replacement:choice['proposal']=replacement[choice['id']]
    trade='Cards may be transferred or traded as collectible NFTs. Trade transfers the NFT only, not definition ownership, copyright, licenses or KEP decryption access. Exchange mechanics, pricing, royalties and marketplace implementation are not selected by this proposal; no actual trade is authorized here.'
    p['choices'].append({'id':'card-transfer','proposal':trade})
    def rewrite(text):
        for key,value in replacement.items():text=text.replace(prior[key],value)
        return text
    p['capability']['acceptance_conditions']=[rewrite(x) for x in p['capability']['acceptance_conditions']]+[trade]
    outcome='Represent one exact shared definition version using related collectible card variants of one approved base image, configurable edition sizes and uniquely identified copies; separately confirm minting and allow card transfer without transferring definition rights or KEP access.'
    p['product']['purpose']=outcome;p['capability']['outcome']=outcome
    p['capability']['exclusions']=[s.replace('deployment, resale, royalties, marketplace behavior, or token-gated access','deployment, automatic royalties, unselected marketplace execution, or token-gated KEP access') for s in p['capability']['exclusions']]
    p['user_direction']={'selected':['Related visual variants of the same image','Configurable collectible card editions','Cards can be traded'],'not_selected':['Exact edition sizes and artwork','Collection freeze policy','Trading mechanism, marketplace, pricing or royalties','Actual mint, payment, publication or transfer']}
    p['scope_change']='The user expands the source NFT concept to collectible card variants and tradability. This supersedes one-NFT-per-definition and the blanket exclusion of trading at the Product concept level. Implementation/effect authorization remains separate.'
    p['supersedes']=bind(PREV/'proposal.json');p['reference_bindings']=[]
    for b in old['reference_bindings']:
        ref=read(ROOT/b['path']);ref['meaning']=rewrite(ref['meaning'])
        if ref['id'].endswith('MINT-RECEIPT'):ref['meaning']+=' Receipt also identifies collection, variant and copy serial; retries preserve that identity.'
        if ref['id'].endswith('RIGHTS-SEPARATION'):ref['meaning']+=' '+trade
        ref['status']='proposed-awaiting-owner-selection';ref['source_or_proposal']='Revised local proposal with user-directed collectible variants; exact edition and transfer rules remain proposed.'
        path=HERE/'references'/(ref['id']+'.json');dump(path,ref);p['reference_bindings'].append(bind(path))
    p['status']='revised-proposal-awaiting-configuration';p['imported']=False
    p['limitations']=['Visual variants and tradability are user-directed; detailed collection, retry and transfer rules remain reviewable proposals.','Semantic proposal only; no artwork generated, runtime built, marketplace connected, mint or trade executed.','Active capability inventory and imported store remain unchanged.']
    dump(HERE/'proposal.json',p);return p
if __name__=='__main__':
    p=revise();print('Revised collectible card proposal; import unchanged.')
