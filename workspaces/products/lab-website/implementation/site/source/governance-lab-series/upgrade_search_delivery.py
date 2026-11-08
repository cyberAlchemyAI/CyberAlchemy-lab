"""One-time migration to deferred local search without discarding existing nav."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=ROOT/'assets/site-search.js';s=p.read_text()
if 'function load(){' not in s:
    s=s.replace('  const data = window.LabSiteSearchIndex;','  let data = window.LabSiteSearchIndex;\n  const base = new URL("../", document.currentScript.src).href;')
    s=s.replace('  if (!data || !header) return;\n  const base = data.base;','  if (!header) return;')
    s=s.replace("  let search=header.querySelector('.docs-search');",'''  if(sidebar&&!sidebar.querySelector('[data-site-practical]')){
    const group=create('nav','docs-practical-links');group.setAttribute('aria-label','Practical guides');
    group.append(create('p','tree-label','Practical guides'));
    for(const [key,label] of [['read-record','Read a record'],['prepare-incident-assessment','Prepare an assessment'],['prepare-definition','Prepare a definition'],['resume-agent-work','Resume agent work'],['record-examples','Complete examples']]){
      const a=create('a','',label);a.href=new URL(key+'.html',base);a.dataset.sitePractical=key;
      if(new URL(a.href).pathname===location.pathname)a.setAttribute('aria-current','page');group.append(a);
    }
    const main=sidebar.querySelector(':scope > nav');if(main)main.after(group);else sidebar.append(group);
  }
  let search=header.querySelector('.docs-search');''')
    a=s.index("  search.append(label,input,");b=s.index("  let selected=",a)
    s=s[:a]+'''  const announcement=create('p','site-search-sr-only');announcement.setAttribute('role','status');announcement.setAttribute('aria-live','polite');
  search.append(label,input,create('kbd','','/'),results,announcement);
  const groups=['The Lab','Start here','Learning paths','Practical guides','Reference examples','Guide','Expanded essays','Reference records','Craft','Research lab','Sources'];
  const normalize=window.LabSearchEngine.normalize;
  let index=data?window.LabSearchEngine.prepare(data.entries):null;
  let loading=null;
  function load(){
    if(index)return Promise.resolve(index);
    if(loading)return loading;
    loading=new Promise((resolve,reject)=>{
      const script=document.createElement('script');script.src=new URL('assets/site-search-index.js',base);
      script.onload=()=>{data=window.LabSiteSearchIndex;index=window.LabSearchEngine.prepare(data.entries);window.LabSiteSearch.count=index.length;resolve(index);};
      script.onerror=()=>{script.remove();loading=null;reject(new Error('The local search index could not be loaded.'));};document.head.append(script);
    });return loading;
  }
'''+s[b:]
    s=s.replace("count.setAttribute('role','status');toolbar.append(count);","toolbar.append(count);announcement.textContent=count.textContent;")
    s=s.replace('    let displayed=0;','''    let displayed=0;
    const best=visible.slice(0,3);
    if(best.length){
      const section=create('section','site-search-group');section.append(create('h2','site-search-group-label','Best matches'));const list=create('ul');
      for(const item of best){const li=create('li');const a=create('a');a.href=new URL(item.href,base);a.dataset.searchGroup=item.group;a.dataset.searchId=item.id;
        const title=create('strong');highlight(title,item.title,terms);const where=create('span','site-search-location',item.section||item.group);const excerpt=create('span','site-search-snippet');highlight(excerpt,snippet(item,terms),terms);a.append(title,where,excerpt);li.append(a);list.append(li);}
      section.append(list);results.append(section);displayed+=best.length;
    }''')
    s=s.replace('const all=visible.filter(item=>item.group===group);','const all=visible.filter(item=>item.group===group&&!best.includes(item));')
    a=s.index("  input.addEventListener('input',");b=s.index("  input.addEventListener('keydown'",a)
    s=s[:a]+'''  async function runSearch(){
    expanded=false;
    if(!input.value.trim()){close();return;}
    if(!index){results.replaceChildren(create('p','site-search-empty','Loading the local documentation index…'));results.hidden=false;input.setAttribute('aria-expanded','true');announcement.textContent='Loading documentation search.';}
    try{await load();matches=window.LabSearchEngine.search(index,input.value);render();}
    catch(error){results.replaceChildren(create('p','site-search-empty',error.message+' Check the assets folder, then type again to retry.'));announcement.textContent=error.message;}
  }
  input.addEventListener('input',runSearch);
  input.addEventListener('focus',()=>{load().catch(()=>{});if(input.value.trim())runSearch();});
'''+s[b:]
    s=s.replace('window.LabSiteSearch={count:index.length,groups,close};','window.LabSiteSearch={count:index?index.length:0,groups,close,ready:load,rank:value=>index?window.LabSearchEngine.search(index,value):[]};')
    p.write_text(s)
# The small engine is eager; the complete text index is delivered on focus/query.
files=[*ROOT.glob('templates/*.in'),ROOT/'research_pages.py',ROOT.parent/'craft-documentation-proposal/tools/build_article.py']
for p in files:
    s=p.read_text()
    if 'site-search-index.js' in s:
        p.write_text(s.replace('site-search-index.js','search-engine.js'))
print('Deferred search delivery installed.')
