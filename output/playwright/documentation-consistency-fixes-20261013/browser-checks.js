async (page) => {
  const pages = [
    ['home', 'governance-lab-series/index.html'],
    ['start', 'governance-lab-series/start-here.html'],
    ['guide-authority', 'governance-lab-series/governance-lab-reference.html#governance'],
    ['guide-relations', 'governance-lab-series/governance-lab-reference.html#records'],
    ['library-definitions', 'governance-lab-series/lab-reference-library.html#catalog-definitions'],
    ['library-relations', 'governance-lab-series/lab-reference-library.html#catalog-relations'],
    ['essay', 'governance-lab-series/lab-reference-library.html#essay-1'],
    ['craft', 'craft-documentation-proposal/craft-model.html#craft-overview'],
    ['read-record', 'governance-lab-series/read-record.html'],
    ['definition-record', 'governance-lab-series/reference/def-cal-definition-definition.html'],
    ['session-record', 'governance-lab-series/reference/def-cal-definition-agent-session.html'],
    ['relation-record', 'governance-lab-series/reference/rel-relation-member-of.html'],
    ['capability-relation', 'governance-lab-series/reference/rel-relation-has-capability.html'],
    ['artifact-type-record', 'governance-lab-series/reference/type-cal-artifact-type-typed-relation-v3.html'],
    ['endpoint-record', 'governance-lab-series/reference/endpoint-product.html']
  ];
  const output = '/home/vlad_/projects/CyberAlchemy-lab/output/playwright/documentation-consistency-fixes-20261013/';
  const observations = [], errors = [], failures = [];
  page.on('pageerror', error => errors.push({ url: page.url(), message: String(error) }));
  page.on('response', response => { if (response.status() >= 400) errors.push({ url: response.url(), status: response.status() }); });
  for (const width of [1440, 1024, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const [id, path] of pages) {
      await page.goto('http://127.0.0.1:33733/' + path);
      await page.waitForFunction(() => document.documentElement.dataset.docsStartup !== 'pending');
      await page.evaluate(() => new Promise(requestAnimationFrame));
      const data = await page.evaluate(() => {
        const visible = el => !!el && el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
        const measure = el => { if (!el) return null; const r=el.getBoundingClientRect(),s=getComputedStyle(el); return { x:r.x,y:r.y,width:r.width,height:r.height,fontSize:s.fontSize,display:s.display }; };
        const main=document.querySelector('main');
        const title=[...main.querySelectorAll('h1')].find(visible);
        const p=[...main.querySelectorAll('p')].find(el=>visible(el)&&el.textContent.trim().length>90&&!el.closest('.article-tree,.docs-local-nav'));
        const pattern=document.querySelector('.reference-pattern');
        const browse=document.querySelector('.article-contents');
        const toc=document.querySelector('.docs-toc');
        return {
          family:document.body.dataset.docsEnhanced||'product',
          documentWidth:document.documentElement.scrollWidth,
          header:measure(document.querySelector('header.topbar')),
          title:measure(title),titleText:title?.textContent.trim(),paragraph:measure(p),
          browseOpen:browse?.open,tocOpen:toc?.open,
          activeNavigation:[...document.querySelectorAll('.article-tree a[aria-current]')].map(a=>a.textContent.trim()),
          outlineLinks:document.querySelectorAll('.docs-toc nav a').length,
          theme:getComputedStyle(document.body).getPropertyValue('--ds-canvas').trim(),
          pattern:pattern?{display:getComputedStyle(pattern).display,columns:getComputedStyle(pattern).gridTemplateColumns,right:visible(pattern.querySelector('.direction-right')),down:visible(pattern.querySelector('.direction-down'))}:null,
          definitionAid:document.querySelector('dl.reference-aid')?{display:getComputedStyle(document.querySelector('dl.reference-aid')).display,rowColumns:getComputedStyle(document.querySelector('dl.reference-aid > div')).gridTemplateColumns}:null
        };
      });
      const row={id,width,path,...data}; observations.push(row);
      if (data.documentWidth > width + 1) failures.push({id,width,check:'page-overflow',actual:data.documentWidth});
      if (!data.title) failures.push({id,width,check:'visible-title'});
      if (['library-definitions','library-relations'].includes(id)&&Math.abs(parseFloat(data.paragraph.fontSize)-(width>900?20:18.8889))>1) failures.push({id,width,check:'catalog-reading-scale',actual:data.paragraph.fontSize});
      if (data.family==='record') {
        if (data.theme!=='#fff') failures.push({id,width,check:'documentation-theme',actual:data.theme});
        if (data.activeNavigation.length!==1) failures.push({id,width,check:'parent-catalog-selection',actual:data.activeNavigation});
        if (!data.outlineLinks) failures.push({id,width,check:'local-outline'});
        if (data.browseOpen!==(width>900)) failures.push({id,width,check:'responsive-browse',actual:data.browseOpen});
        if (data.tocOpen!==(width>1200)) failures.push({id,width,check:'responsive-outline',actual:data.tocOpen});
        if (width<900&&data.title.y>600) failures.push({id,width,check:'record-opening-position',actual:data.title.y});
      }
      if (data.pattern&&(data.pattern.display!=='grid'||data.pattern.right!==(width>620)||data.pattern.down!==(width<=620))) failures.push({id,width,check:'relation-pattern',actual:data.pattern});
      if ([1440,390].includes(width)&&['start','guide-authority','library-relations','craft','definition-record','relation-record','artifact-type-record','endpoint-record'].includes(id)) await page.screenshot({path:output+'screenshots/'+id+'-'+width+'.png'});
    }
  }
  for (const width of [1440,1024,390,320]) {
    const group=observations.filter(row=>row.width===width);
    const guide=group.find(row=>row.id==='guide-authority');
    for(const row of group.filter(row=>row.family==='record')) {
      if(Math.abs(row.title.x-guide.title.x)>1) failures.push({id:row.id,width,check:'shared-content-alignment',guideX:guide.title.x,recordX:row.title.x});
      if(Math.abs(row.header.height-guide.header.height)>1) failures.push({id:row.id,width,check:'shared-header-height',guideHeight:guide.header.height,recordHeight:row.header.height});
      if(Math.abs(parseFloat(row.paragraph?.fontSize)-parseFloat(guide.paragraph?.fontSize))>1) failures.push({id:row.id,width,check:'shared-reading-scale',guide:guide.paragraph?.fontSize,record:row.paragraph?.fontSize});
    }
  }
  return JSON.stringify({observations,errors,failures});
}
