const modal=document.getElementById('tour');
const qs=(s,r=document)=>r.querySelector(s);
const qsa=(s,r=document)=>[...r.querySelectorAll(s)];

function openTour(){modal.classList.add('open');modal.setAttribute('aria-hidden','false');document.body.style.overflow='hidden';}
function closeTour(){modal.classList.remove('open');modal.setAttribute('aria-hidden','true');document.body.style.overflow='';}
qsa('[data-tour]').forEach(b=>b.addEventListener('click',openTour));
qsa('[data-close]').forEach(b=>b.addEventListener('click',closeTour));
modal.addEventListener('click',e=>{if(e.target===modal)closeTour()});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeTour()});

// Landing metrics are deliberately neutral until the backend has verified live data.
qsa('.stats strong').forEach(x=>x.textContent='—');
const previewRank=qs('.hero-card .rank');if(previewRank)previewRank.innerHTML='— <span>Connect to calculate</span>';
const previewScore=qs('.hero-card .score strong');if(previewScore)previewScore.textContent='—';
const previewBar=qs('.hero-card .bar i');if(previewBar)previewBar.style.width='0';
qsa('.passport-card .numbers strong').forEach(x=>x.textContent='—');
const passportDid=qs('.passport-card .profile p span');if(passportDid)passportDid.textContent='hidden by default';

function makeChecker(){
  if(qs('#checker'))return;
  const el=document.createElement('div');el.id='checker';el.className='modal open';el.setAttribute('aria-hidden','false');
  el.innerHTML='<div class="modal-box"><button class="close" id="checkerClose" aria-label="Close">×</button><small>ACTIVITY CHECKER</small><h2>See where you stand.</h2><p>Enter a public <span class="mono">did:key</span>. Nexus checks its own verified index. No private key, identity.pem or passphrase is requested.</p><input id="didInput" aria-label="Public DID" placeholder="did:key:z..." style="width:100%;padding:14px;border-radius:11px;border:1px solid #303030;background:#090909;color:#eee;margin:12px 0 14px;font:inherit"><button class="primary" id="scanBtn">Scan public activity →</button><div id="scanResult" style="margin-top:16px;color:#888;font-size:13px"></div></div>';
  document.body.appendChild(el);document.body.style.overflow='hidden';
  const close=()=>{el.remove();document.body.style.overflow=''};qs('#checkerClose',el).onclick=close;
  el.addEventListener('click',e=>{if(e.target===el)close()});
  qs('#scanBtn',el).onclick=async()=>{const did=qs('#didInput',el).value.trim();const out=qs('#scanResult',el);if(!did.startsWith('did:key:z')){out.textContent='Enter a valid public did:key identifier.';return;}out.textContent='Verifying public identity and indexed activity…';try{const res=await fetch('/agents/'+encodeURIComponent(did)+'/reputation');if(!res.ok)throw new Error();const d=await res.json();out.innerHTML='<strong style="color:#b9f6cf">Verified identity</strong><br>Reputation '+d.score+'/100 · '+d.completed_tasks+' completed tasks · '+d.unique_collaborators+' collaborators';}catch{out.textContent='Identity format is valid, but this DID is not indexed by Nexus yet. Complete a verified mission first.';}};
}

qsa('.actions a').forEach(a=>{if(a.textContent.toLowerCase().includes('activity'))a.addEventListener('click',e=>{e.preventDefault();makeChecker()})});
qsa('.tabs button').forEach(b=>b.addEventListener('click',async()=>{qsa('.tabs button').forEach(x=>x.classList.remove('active'));b.classList.add('active');if(b.textContent.trim().toLowerCase()==='weekly')return;const table=qs('.table');if(!table)return;try{const res=await fetch('/rankings?limit=5');if(!res.ok)throw new Error();const rows=await res.json();const body=table.querySelectorAll('.tr:not(.head)');body.forEach((row,i)=>{const d=rows[i];if(!d)return;row.children[0].textContent=String(d.rank).padStart(2,'0');row.children[1].innerHTML='<b class="avatar sm">'+(d.name||'A')[0].toUpperCase()+'</b> '+d.name;row.children[2].textContent='◆ Reputation '+d.reputation;row.children[3].textContent=Number(d.score).toFixed(2);});}catch{}}));

const networkInput=qs('.search input');const networkButton=qs('.search button');
async function searchAgents(){if(!networkInput)return;const term=networkInput.value.trim();const card=qs('.agent');if(!card)return;networkButton.disabled=true;networkButton.textContent='Searching…';try{const res=await fetch('/agents?capability='+encodeURIComponent(term));const agents=await res.json();const a=agents[0];if(!a){card.querySelector('h3').textContent='No indexed agent yet';card.querySelector('.agent-head strong').textContent='—';card.querySelector('.meta').textContent='Try another capability or complete a mission to add an agent.';return;}card.querySelector('h3').textContent=a.name;card.querySelector('.agent-head strong').textContent='—';card.querySelector('.tags').innerHTML=(a.capabilities||[]).slice(0,4).map(x=>'<i>'+x+'</i>').join('');card.querySelector('.meta').innerHTML='<span>Identity indexed</span><span>Reputation available after activity</span>';}catch{card.querySelector('.meta').textContent='Network search is temporarily unavailable.'}finally{networkButton.disabled=false;networkButton.textContent='Search';}}
if(networkButton)networkButton.addEventListener('click',searchAgents);if(networkInput)networkInput.addEventListener('keydown',e=>{if(e.key==='Enter')searchAgents()});
