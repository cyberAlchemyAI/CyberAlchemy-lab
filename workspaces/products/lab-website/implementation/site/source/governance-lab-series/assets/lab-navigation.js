/* Native disclosure routing and compatibility for the former combined page. */
(() => {
  const reference='lab-reference-library.html';
  function reveal() {
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
    if(/^(def-|type-|rel-|endpoint-|essay-|catalog-|reference$|research$|articles-library$|catalog-library$|research-library$)/.test(id)) {
      location.replace(reference+location.hash);return;
    }
    const target=document.getElementById(id);
    if(!target)return;
    for(let node=target;node;node=node.parentElement)if(node.tagName==='DETAILS')node.open=true;
    if(id==='system-map')requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'instant'}));
  }
  const contents=document.getElementById('article-contents');
  if(contents&&matchMedia('(max-width:760px)').matches)contents.open=false;
  document.addEventListener('click',event=>{
    const a=event.target.closest('a[href^="#"]');
    if(!a)return;
    const target=document.getElementById(a.hash.slice(1));
    if(target)for(let node=target;node;node=node.parentElement)if(node.tagName==='DETAILS')node.open=true;
    if(a.hash===location.hash)reveal();
  });
  addEventListener('hashchange',reveal);reveal();
})();
