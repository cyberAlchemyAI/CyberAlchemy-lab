import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
const base = fileURLToPath(new URL('.', import.meta.url));
const page = readFileSync(base + 'index.html', 'utf8');
const payload = page.match(/<script type="application\/json" id="package-data">([\s\S]*?)<\/script>/)[1];
const code = page.match(/<script>\n([\s\S]*?)<\/script>/)[1];
const catalog = JSON.parse(payload);
class Element {
  constructor(tag='div') { this.tagName=tag; this.children=[]; this.dataset={}; this.attributes={}; this.listeners={}; this.textContent=''; this.value=''; this.hidden=false; }
  replaceChildren(...children) { this.children=children; }
  append(...children) { this.children.push(...children); }
  setAttribute(name,value) { this.attributes[name]=value; }
  addEventListener(name,fn) { (this.listeners[name]??=[]).push(fn); }
  querySelectorAll(tag) { return this.children.filter(child=>child.tagName===tag); }
  fire(name) { for(const fn of this.listeners[name]??[])fn({target:this}); }
}
const elements=new Map([...page.matchAll(/\bid="([^"]+)"/g)].map(match=>[match[1],new Element()]));
elements.get('package-data').textContent=payload;
elements.get('category').value='schemas';elements.get('layer').value='all';
const document={getElementById:id=>{assert(elements.has(id),'Unknown DOM ID '+id);return elements.get(id);},createElement:tag=>new Element(tag)};
const context=vm.createContext({document,console});
vm.runInContext(code,context,{filename:'explorer-inline.js',timeout:5000});
const e=id=>elements.get(id);
const checks=[];
function check(name,fn){fn();checks.push({name,result:'pass'});}
function filter(category,layer,search=''){
  e('category').value=category;e('layer').value=layer;e('search').value=search;
  e('category').fire('change');
}
check('initial schema catalog',()=>assert.equal(e('list').children.length,catalog.schemas.length));
check('schema search and selection',()=>{
  filter('schemas','all','change-proposal');
  assert.equal(e('list').children.length,1);assert.equal(e('detail-title').textContent,'change-proposal');
  assert(JSON.parse(e('definition').textContent).properties.proposal_id);
});
check('layer isolation',()=>{
  filter('schemas','L3');
  assert.equal(e('list').children.length,catalog.schemas.filter(row=>row.layer==='L3').length);
});
check('complete API catalog',()=>{
  filter('apis','all');assert.equal(e('list').children.length,16);
});
check('review API inspection',()=>{
  filter('apis','all','reviewBundle');assert.equal(e('list').children.length,1);
  assert.equal(e('detail-title').textContent,'reviewBundle');
  assert.equal(JSON.parse(e('definition').textContent).operationId,'reviewBundle');
});
check('contract inspection',()=>{
  filter('contracts','all','protectedLineage');
  assert.equal(e('detail-title').textContent,'C-protectedLineage');
  assert(JSON.parse(e('definition').textContent).rules[0].includes('epoch'));
});
check('empty search and recovery',()=>{
  filter('schemas','all','this-definition-does-not-exist');
  assert.equal(e('list').children.length,0);assert(e('source-link').hidden);
  filter('schemas','all','graph');
  assert(e('list').children.length>0);assert.equal(e('source-link').hidden,false);
});
check('dependency trace navigation',()=>{
  filter('schemas','all','');
  const graphButton=e('list').children.find(button=>button.dataset.identity==='graph');
  graphButton.fire('click');
  assert.equal(e('detail-title').textContent,'graph');
  const dependency=e('refs').children.find(button=>button.textContent.includes('relation-assertion'));
  assert(dependency);dependency.fire('click');
  assert.equal(e('detail-title').textContent,'relation-assertion');
});
check('synthetic example inspection',()=>{
  assert.equal(e('example-panel').hidden,false);
  assert.equal(JSON.parse(e('example').textContent).schema_version,'relational-checker.relation-assertion/v1-candidate');
});
check('all detail selections are readable',()=>{
  for(const category of ['schemas','contracts','apis']){
    filter(category,'all');
    for(const button of [...e('list').children]){
      button.fire('click');
      assert(e('detail-title').textContent);
      assert(JSON.parse(e('definition').textContent));
    }
  }
});
const report={
  schema_version:'relational-checker.explorer-validation/v1-candidate',result:'pass',
  method:'Node VM with a minimal DOM event harness',
  limitation:'No real browser layout, screenshot or assistive-technology testing was performed.',
  counts:{interaction_checks:checks.length,definitions_inspected:catalog.schemas.length+catalog.contracts.length+catalog.apis.length},
  checks,explorer_sha256:createHash('sha256').update(page).digest('hex')
};
writeFileSync(base+'receipts/explorer-validation.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({result:report.result,method:report.method,counts:report.counts,limitation:report.limitation},null,2));

