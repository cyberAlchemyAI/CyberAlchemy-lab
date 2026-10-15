/* Optional role focus; the entire map and overview remain readable without JS. */
(() => {
  const map=document.querySelector('.company-brain-map');
  if(!map)return;
  const detail=map.querySelector('.brain-map-detail');
  const title=detail.querySelector('h3');const body=detail.querySelector('p');
  const overview={title:title.textContent,body:body.textContent};
  const roles={
    people:{title:'People give the work direction and accountable review.',body:'People express intentions, examine evidence and make decisions within their authority. Their reviews and accepted decisions become part of the continuing project state.'},
    agents:{title:'Agents recover context and act within a scope.',body:'An agent works in a temporary session. It receives checked context and ontology views from project state, and acts only with applicable permission. Short-term memory belongs to the session.'},
    knowledge:{title:'Knowledge gives work meaning and context.',body:'Definitions establish meanings and boundaries. Sources, observations and lessons provide traceable context. The applicable knowledge informs work and supplies criteria for reviewing its results.'},
    work:{title:'Work turns an intention into an attempt you can examine.',body:'Projects coordinate bounded work. An attempt produces records of what happened, including results and evidence. Those records support investigation, review and the next person or agent taking over.'},
    decisions:{title:'Decisions govern accepted changes.',body:'An authorized decision identifies the exact change and its scope. Work and evidence inform the review. Accepted changes follow the applicable lifecycle rules; deployment and other effects need their own authority.'}
  };
  let selected=null;
  let feedback=null;
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
  reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches)feedback?.cancel();});
  const buttons=[...map.querySelectorAll('[data-brain-part]')];
  for(const button of buttons){
    button.disabled=false;
    button.addEventListener('click',()=>{
      selected=selected===button.dataset.brainPart?null:button.dataset.brainPart;
      map.classList.toggle('is-focused',Boolean(selected));
      for(const node of buttons)node.setAttribute('aria-pressed',String(node.dataset.brainPart===selected));
      for(const branch of map.querySelectorAll('[data-brain-branch]'))branch.classList.toggle('is-active',branch.dataset.brainBranch===selected);
      const copy=selected?roles[selected]:overview;title.textContent=copy.title;body.textContent=copy.body;
      feedback?.cancel();
      // One short highlight connects selection to the changing explanation;
      // the selected branch and live text remain the reduced-motion feedback.
      if(!reducedMotion.matches&&detail.animate)feedback=detail.animate([
        {backgroundColor:getComputedStyle(map).getPropertyValue('--ds-subtle').trim()},
        {backgroundColor:'transparent'}
      ],{duration:180,easing:'cubic-bezier(.16,1,.3,1)'});
    });
  }
  map.querySelector('.brain-map-hint').style.visibility='visible';
})();
