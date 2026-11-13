/* Shared UI and page interactions. Classic scripts work with file:// and static hosts. */
(function () {
  'use strict';
  const D = window.AGRI;
  const $ = id => document.getElementById(id);
  const page = document.body.dataset.page;
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const memory = {};
  // Storage may be disabled or unavailable on a local file. Keep the current visit usable.
  const storage = {
    get(key, fallback) { try { return localStorage.getItem(key) ?? memory[key] ?? fallback; } catch (_) { return memory[key] ?? fallback; } },
    set(key, value) { memory[key] = value; try { localStorage.setItem(key,value); } catch (_) {} },
    remove(key) { delete memory[key]; try { localStorage.removeItem(key); } catch (_) {} }
  };
  const requestedLanguage = new URLSearchParams(location.search).get('lang');
  let language = (requestedLanguage || storage.get('rythu-language','en')) === 'te' ? 'te' : 'en';
  storage.set('rythu-language',language);
  const dual = (en,te) => `<span data-en="${esc(en)}" data-te="${esc(te)}">${esc(language==='te'?te:en)}</span>`;
  const title = (en,te,tag='h2') => `<${tag}>${dual(en,te)}</${tag}>`;
  const end = () => `<p class="disclaimer">${esc(D.disclaimer)}</p>`;
  const list = (items,cls='advice-list') => `<ul class="${cls}">${items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
  const money = n => new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(n);
  const number = n => new Intl.NumberFormat('en-IN',{maximumFractionDigits:1}).format(n);
  const acreage = n => new Intl.NumberFormat('en-IN',{maximumFractionDigits:2}).format(n);
  const cropName = key => D.crops[key] ? `${D.crops[key].en} / ${D.crops[key].te}` : 'Crop not mentioned';
  const printButton = id => `<button type="button" class="button secondary small" data-print="${id}">${dual('Print advice','సలహా ముద్రించండి')}</button>`;
  function status(id,text,error=false) { const node=$(id); if(node){ node.textContent=text;node.classList.toggle('error',error); } }
  function applyLanguage() {
    document.documentElement.lang=language;
    document.querySelectorAll('[data-en][data-te]').forEach(node=>{ node.textContent=node.dataset[language]; });
    document.querySelectorAll('[data-placeholder-en]').forEach(node=>{node.placeholder=language==='te'?node.dataset.placeholderTe:node.dataset.placeholderEn;});
    $('language-toggle').textContent=language==='en'?'తెలుగు':'English';
    $('language-toggle').setAttribute('aria-label',language==='en'?'Switch headings and navigation to Telugu':'Switch headings and navigation to English');
    // file:// storage differs between browsers. Carry the preference across local pages too.
    document.querySelectorAll('a[href]').forEach(link=>{
      const raw=link.getAttribute('href');
      if(!raw||/^(?:[a-z]+:|\/\/)/i.test(raw)||!/^.*\.html(?:[?#]|$)/i.test(raw))return;
      const [pathQuery,hash]=raw.split('#'),[path,query]=pathQuery.split('?');
      const params=new URLSearchParams(query||'');params.set('lang',language);
      link.setAttribute('href',path+'?'+params.toString()+(hash?'#'+hash:''));
    });
  }
  function buildSharedUI() {
    const nav=[['index.html','home','Home','హోమ్'],['crop-disease.html','disease','Crop health','పంట ఆరోగ్యం'],['fertilizer.html','fertilizer','Fertilizer','ఎరువులు'],['irrigation.html','irrigation','Water planner','నీటి ప్రణాళిక'],['market-prices.html','market','Market prices','మార్కెట్ ధరలు'],['weather.html','weather','Weather','వాతావరణం'],['govt-schemes.html','schemes','Schemes','పథకాలు'],['about.html','about','About','మా గురించి']];
    $('site-header').innerHTML=`<div class="utility"><div class="wrap"><span>${dual('Telugu–English Agricultural Query Assistant','తెలుగు–ఇంగ్లీష్ వ్యవసాయ ప్రశ్నల సహాయకుడు')}</span><span>🌾 ${dual('A little help, close to the soil','నేలకు దగ్గరగా, రైతుకు తోడుగా')}</span></div></div><div class="wrap"><div class="brand-row"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">❧</span><span>Rythu Mitra<small>${dual('Your farm companion','మీ వ్యవసాయ మిత్రుడు')}</small></span></a><div class="header-actions"><button type="button" class="lang-btn" id="language-toggle">తెలుగు</button><button type="button" class="menu-btn" id="menu-toggle" aria-expanded="false" aria-controls="main-nav">☰ <span class="sr-only">Menu</span></button></div></div><nav id="main-nav" class="nav" aria-label="Main navigation">${nav.map(([file,key,en,te])=>`<a href="${file}" ${page===key?'aria-current="page"':''}>${dual(en,te)}</a>`).join('')}</nav></div>`;
    $('site-footer').innerHTML=`<div class="helpline"><div class="wrap"><div><strong>${dual('A real person, when you need one.','అవసరమైనప్పుడు నిపుణుల సహాయం.')}</strong><div class="fine">${dual('Kisan Call Centre • Farmer helpline','కిసాన్ కాల్ సెంటర్ • రైతు సహాయవాణి')}</div></div><a href="tel:18001801551">1800-180-1551 ↗</a></div></div><div class="site-footer"><div class="wrap"><div class="footer-top"><div><strong>❧ Rythu Mitra</strong><p>${dual('Practical guidance for your field, in the words you use every day.','మీరు రోజూ మాట్లాడే భాషలో, మీ పొలానికి ఉపయోగకరమైన సలహా.')}</p></div><div class="footer-links"><a href="about.html">${dual('About this project','ప్రాజెక్ట్ గురించి')}</a><a href="https://kvk.icar.gov.in/" target="_blank" rel="noopener noreferrer">${dual('Find a KVK ↗','కేవీకే వివరాలు ↗')}</a></div></div><div class="footer-bottom"><span>© 2026 Rythu Mitra • SR University student project</span><span>${dual('Built with care for the farming community.','రైతు సమాజం కోసం రూపొందించబడింది.')}</span></div></div></div>`;
    $('language-toggle').addEventListener('click',()=>{
      language=language==='en'?'te':'en';storage.set('rythu-language',language);
      try{const url=new URL(location.href);url.searchParams.set('lang',language);window.history.replaceState(null,'',url);}catch(_){}
      applyLanguage();
    });
    $('menu-toggle').addEventListener('click',()=>{const open=$('main-nav').classList.toggle('open');$('menu-toggle').setAttribute('aria-expanded',String(open));});
    document.querySelectorAll('.guidance-end').forEach(n=>n.outerHTML=end());
    document.addEventListener('click',event=>{const button=event.target.closest('[data-print]');if(!button)return;const target=$(button.dataset.print);if(!target)return;target.classList.add('print-target');document.body.classList.add('print-panel');window.print();});
    window.addEventListener('afterprint',()=>{document.body.classList.remove('print-panel');document.querySelectorAll('.print-target').forEach(n=>n.classList.remove('print-target'));});
  }
  function fillCrops() {
    const requested=new URLSearchParams(location.search).get('crop');
    document.querySelectorAll('.crop-select').forEach(select=>{select.innerHTML=Object.entries(D.crops).map(([key,c])=>`<option value="${key}">${esc(c.en)} / ${esc(c.te)} (${esc(c.local)})</option>`).join('');if(D.crops[requested])select.value=requested;});
  }
  function reveal(id,html,scroll=false) { const node=$(id);node.innerHTML=html;node.hidden=false;applyLanguage();if(scroll)node.scrollIntoView({behavior:'smooth',block:'start'}); }

  function setupHome() {
    const examples=[['crop_disease','naaku vari chettu ki leaf spot vachindi, em medicine veyali?'],['fertilizer','patti ki urea, DAP entha veyali?'],['irrigation','mirapa polaniki neellu enni rojula ki pettali?'],['market_price','eeroju tamota mandi price entha?'],['weather','repu Warangal lo varsham padutunda?'],['govt_scheme','PM KISAN scheme ki ela apply cheyali?']];
    $('examples').innerHTML=examples.map(([key,q])=>`<button type="button" class="example" data-question="${esc(q)}"><span>${dual(D.topics[key].en,D.topics[key].te)}</span>${esc(q)}</button>`).join('');
    $('feature-cards').innerHTML=Object.values(D.topics).map(t=>`<a class="card feature-card" href="${t.file}"><span class="feature-icon" aria-hidden="true">${t.icon}</span>${title(t.en,t.te,'h3')}<p>${dual(t.description,t.descriptionTe)}</p><span class="arrow">${dual('Explore guide →','మార్గదర్శి చూడండి →')}</span></a>`).join('');
    function readHistory(){try{const h=JSON.parse(storage.get('rythu-history','[]'));return Array.isArray(h)?h.filter(q=>typeof q==='string'&&q.trim()&&q.length<=800).slice(0,5):[];}catch(_){return [];}}
    function renderHistory(){const h=readHistory();$('history-list').innerHTML=h.length?h.map(q=>`<li><button type="button" data-question="${esc(q)}">${esc(q)}</button></li>`).join(''):`<li class="empty-state">${dual('Your recent questions will appear here.','మీ ఇటీవలి ప్రశ్నలు ఇక్కడ కనిపిస్తాయి.')}</li>`;$('clear-history').disabled=!h.length;}
    function remember(q){const h=readHistory().filter(x=>x!==q);h.unshift(q);storage.set('rythu-history',JSON.stringify(h.slice(0,5)));renderHistory();}
    $('clear-history').addEventListener('click',()=>{storage.remove('rythu-history');renderHistory();status('history-status','Your question history has been cleared.');applyLanguage();});
    document.addEventListener('click',event=>{const button=event.target.closest('[data-question]');if(button){$('query').value=button.dataset.question;$('ask-form').requestSubmit();}});
    document.addEventListener('submit',event=>{
      if(event.target.id==='home-location-form'){event.preventDefault();$('query').value=event.target.dataset.baseQuery+' in '+event.target.elements.district.value;$('ask-form').requestSubmit();return;}
      if(event.target.id!=='followup-form')return;
      event.preventDefault();const detail=event.target.elements.detail.value.trim();if(!detail)return;
      $('query').value=event.target.dataset.baseQuery+' '+detail;$('ask-form').requestSubmit();
    });
    $('ask-form').noValidate=true;
    $('ask-form').addEventListener('submit',async event=>{
      event.preventDefault();const query=$('query').value.trim();
      if(!query){$('home-result').hidden=true;status('ask-status','Please type a question, such as “vari ki neellu eppudu pettali?”',true);$('query').focus();return;}
      if(query.length>800){status('ask-status','Please keep your question within 800 characters.',true);return;}
      status('ask-status','');let answer;
      if(location.protocol!=='file:'){
        const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),2500);
        try{const response=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query}),signal:controller.signal});if(!response.ok)throw new Error('API unavailable');answer=await response.json();}catch(_){answer=window.AgriClassifier.classify(query);}finally{clearTimeout(timer);}
      }else answer=window.AgriClassifier.classify(query);
      remember(query);
      reveal('home-result',window.DirectAnswers.build(query,answer),true);
      if(answer.intent==='weather'&&answer.location)window.DirectAnswers.weather(answer,query);
      if(answer.intent==='market_price')window.DirectAnswers.prices(answer,query);
    });
    renderHistory();
  }
  function setupDisease() {
    $('symptom-options').innerHTML=D.symptoms.map(([key,en,te])=>`<label class="check"><input type="checkbox" name="symptom" value="${key}">${dual(en,te)}</label>`).join('');
    $('symptom-panel').insertAdjacentHTML('beforeend',end());
    $('prevention').innerHTML=title('A prevention checklist','నివారణ కోసం తనిఖీ జాబితా')+list(D.health.prevention,'checklist')+`<p class="source-links"><a href="https://agritech.tnau.ac.in/" target="_blank" rel="noopener noreferrer">More crop protection guidance: TNAU Agritech ↗</a></p>`+end();
    function render(){const key=$('disease-crop').value;const c=D.crops[key];$('disease-cards').innerHTML=D.diseases[key].map(([name,te,symptoms,tags,type])=>{const care=D.diseaseCare[type];return `<article class="card disease-card">${title(name,te,'h3')}<span class="badge">${esc(c.en)} / ${esc(c.te)}</span><p class="fine">Reference: TNAU Agritech crop protection; symptoms need field confirmation. For unverified crop-specific problems, consult your agriculture officer.</p>${title('Signs to look for','గమనించవలసిన లక్షణాలు','h4')}<p>${esc(symptoms)}</p>${title('Organic & field care','సేంద్రియ, పొలం సంరక్షణ','h4')}<p>${dual(care.organic,care.organicTe||care.organic)}</p>${title('Chemical control, if needed','అవసరమైతే రసాయన నియంత్రణ','h4')}<p>${dual(care.chemical,care.chemicalTe||care.chemical)}</p>${end()}</article>`;}).join('');$('symptom-result').innerHTML='';status('symptom-status','');applyLanguage();}
    $('disease-crop').addEventListener('change',render);
    $('symptom-form').addEventListener('submit',event=>{event.preventDefault();const selected=[...document.querySelectorAll('input[name=symptom]:checked')].map(x=>x.value);if(!selected.length){status('symptom-status','Please select at least one symptom.',true);return;}status('symptom-status','');const matches=D.diseases[$('disease-crop').value].map(d=>({d,n:d[3].filter(t=>selected.includes(t)).length})).filter(x=>x.n).sort((a,b)=>b.n-a.n);$('symptom-result').innerHTML=title('Possible causes to inspect','పరిశీలించవలసిన కారణాలు','h3')+`<p>${esc(D.health.checker)}</p>`+(matches.length?list(matches.map(({d})=>d[0]+': '+d[2])):`<p>${esc(D.health.noMatch)}</p>`)+(selected.includes('powder')?`<p>${esc(D.health.powder)}</p>`:'');$('symptom-result').innerHTML=window.PracticalGuidance.symptoms($('disease-crop').value,selected)+$('symptom-result').innerHTML;applyLanguage();});render();
  }

  // Exported pure functions also allow independent checks without a browser.
  function fertilizerPlan(crop,area) {
    const base=D.nutrients[crop];
    const manual=['manual-n','manual-p','manual-k'].map(id=>$(id)?.value);
    const ref=manual.every(v=>v!==undefined&&v!=='')?{...base,profiles:[manual.map(Number)],basalN:1,basalK:1,vegN:0,vegK:0}:base;
    const profiles=ref.profiles.map(([n,p,k])=>{
      const dap=p/.46,urea=Math.max(0,n-dap*.18)/.46,mop=k/.60;
      const basalU=Math.min(urea,Math.max(0,n*ref.basalN-dap*.18)/.46);
      const vegU=(urea-basalU)*(ref.basalN===1?0:ref.vegN/(1-ref.basalN));
      const rows=[[basalU,dap,mop*ref.basalK],[vegU,0,mop*ref.vegK],[urea-basalU-vegU,0,mop*(1-ref.basalK-ref.vegK)]];
      return {total:[urea,dap,mop].map(v=>v*.40468564224*area),rows:rows.map(row=>row.map(v=>Math.max(0,v)*.40468564224*area))};
    });
    return profiles;
  }
  function valueRange(values) { const low=Math.min(...values),high=Math.max(...values);return number(low)===number(high)?number(low):`${number(low)}–${number(high)}`; }
  function setupFertilizer() {
    $('fertilizer-form').addEventListener('submit',event=>{event.preventDefault();const area=Number($('fert-area').value),key=$('fert-crop').value,stage=$('fert-stage').value;if(!Number.isFinite(area)||area<=0||area>10000){status('fert-status','Enter an area greater than zero and up to 10,000 acres.',true);return;}status('fert-status','');
      const manual=['manual-n','manual-p','manual-k'].map(id=>$(id)?.value);
      if(!D.nutrients[key].profiles.length&&!manual.every(v=>v!==undefined&&v!=='')){
        reveal('fert-result',`${title('Ask for a soil-test-based plan','భూసార పరీక్ష ఆధారిత సలహా పొందండి')}<p>${esc(cropName(key))}</p><p>${dual('Consult your agriculture officer. No numerical fertilizer dose has been verified for this crop here. If you have an officer’s N:P2O5:K2O recommendation, enter it above to convert it into product equivalents.','మీ వ్యవసాయ అధికారిని సంప్రదించండి. ఈ పంటకు ఎరువుల మోతాదు ఇక్కడ నిర్ధారించలేదు. అధికారి ఇచ్చిన మోతాదును పై పెట్టెల్లో నమోదు చేయండి.')}</p><p><a href="${D.nutrients[key].source}" target="_blank" rel="noopener">${esc(D.nutrients[key].sourceName)}</a></p>${end()}`);return;
      }
      const per=fertilizerPlan(key,1),total=fertilizerPlan(key,area),stages=[['basal','Basal / before planting'],['vegetative','Early growth top dressing(s)'],['reproductive','Later growth top dressing(s)']];
      const rowHtml=(plans,unit)=>stages.map(([s,label],i)=>`<tr class="${s===stage?'is-current':''}"><td>${esc(label)}${s===stage?' • selected stage':''}</td>${[0,1,2].map(j=>`<td>${valueRange(plans.map(p=>p.rows[i][j]))} ${unit}</td>`).join('')}</tr>`).join('')+`<tr><th scope="row">Whole-season total</th>${[0,1,2].map(j=>`<td><strong>${valueRange(plans.map(p=>p.rows.reduce((sum,row)=>sum+row[j],0)))} ${unit}</strong></td>`).join('')}</tr>`;
      const table=(plans,caption)=>`<div class="table-wrap"><table><caption>${esc(caption)}</caption><thead><tr><th scope="col">When to apply</th><th scope="col">Urea</th><th scope="col">DAP</th><th scope="col">MOP / potash</th></tr></thead><tbody>${rowHtml(plans,'kg')}</tbody></table></div>`;
      reveal('fert-result',`${title('Your fertilizer planning guide','మీ ఎరువుల ప్రణాళిక')}<p><strong>${esc(cropName(key))} • ${acreage(area)} acre${area===1?'':'s'}</strong></p><div class="notice">${esc(D.fertilizerNotes.intro)}</div><p>${dual(D.nutrients[key].note,D.nutrients[key].noteTe)}</p>${title('Per acre','ఎకరానికి','h3')}${table(per,'Typical product quantities per acre, across reference crop situations.')}${title('For your whole field','మీ మొత్తం పొలానికి','h3')}${table(total,`Product quantities for ${area} acre(s).`)}<p class="fine">${esc(D.fertilizerNotes.accounting)}</p><p>${esc(D.fertilizerNotes.split)}</p>${title('Organic options','సేంద్రియ ప్రత్యామ్నాయాలు','h3')}${list(D.fertilizerNotes.organics)}<p class="source-links"><a href="${D.nutrients[key].source}" target="_blank" rel="noopener noreferrer">${esc(D.nutrients[key].sourceName)}</a></p>${printButton('fert-result')}${end()}`);
    });
  }
  function waterPlan(crop,soil,season,depth=10) {
    if(!Number.isFinite(depth)||depth<0)throw new Error('Invalid depth');
    return {litres:depth*4046.8564224,depth};
  }
  function setupIrrigation() {
    $('water-methods').innerHTML=title('Choose how you water','నీటి పద్ధతిని ఎంచుకోండి')+`<p class="muted">Illustrative costs and water savings, per acre. Compare local quotes.</p><div class="table-wrap"><table><thead><tr><th scope="col">Method</th><th scope="col">Example setup budget</th><th scope="col">Typical water saving</th><th scope="col">What to consider</th></tr></thead><tbody>${D.water.methods.map(m=>`<tr><th scope="row">${dual(m.name,m.te)}</th><td>${esc(m.cost)}</td><td>${esc(m.saving)}</td><td>${esc(m.use)}</td></tr>`).join('')}</tbody></table></div><p class="fine">${esc(D.water.costNote)}</p><p class="source-links"><a href="https://agritech.tnau.ac.in/agriculture/agri_irrigationmgt_microirrigation.html" target="_blank" rel="noopener noreferrer">Read about micro irrigation ↗</a></p>${end()}`;
    $('water-tips').innerHTML=title('Make the water go further','నీటిని ఆదా చేయండి')+list(D.water.tips,'checklist')+end();
    $('irrigation-form').addEventListener('submit',event=>{
      event.preventDefault();const key=$('water-crop').value,depth=Number($('water-depth').value),soil=$('soil').value,season=$('season').value;
      if(!Number.isFinite(depth)||depth<0||depth>1000)return;
      const plan=waterPlan(key,soil,season,depth),c=D.crops[key];
      reveal('water-result',`${title('Your water planning guide','మీ నీటి ప్రణాళిక')}<p><strong>${esc(cropName(key))}</strong></p><p>${dual('Consult your agriculture officer for the irrigation interval and depth. No crop-specific interval is inferred here.','నీరు ఇచ్చే సమయం, మోతాదు కోసం మీ వ్యవసాయ అధికారిని సంప్రదించండి.')}</p><div class="stats"><div class="stat"><strong>${number(plan.litres)} L</strong><span>${dual('Net litres per acre for your entered depth','మీరు నమోదు చేసిన లోతుకు ఎకరానికి నీటి లీటర్లు')}</span></div><div class="stat"><strong>${number(depth)} mm</strong><span>${dual('Your chosen depth, not a recommended dose','మీరు ఎంచుకున్న లోతు; సిఫార్సు కాదు')}</span></div></div><p>${dual(c.tip,c.tipTe)}</p><p>${esc(D.water.seasonal[season])}</p><p><a href="${c.waterSource}" target="_blank" rel="noopener">ICAR — soil-moisture scheduling guidance (general)</a></p>${key==='brinjal'?'<p>TNAU brinjal reference: weekly intervals after seedling establishment; local soil and rainfall may change this. <a href="https://agritech.tnau.ac.in/horticulture/horti_vegetables_brinjal_irrigation.html">TNAU Agritech — brinjal irrigation</a></p>':''}${printButton('water-result')}${end()}`);
    });
  }

  function profit(yieldQt,price,cost){return {revenue:yieldQt*price,profit:yieldQt*price-cost};}
  function setupMarket() {
    $('profit-form').addEventListener('submit',event=>{event.preventDefault();const values=['yield','sale-price','cost'].map(id=>Number($(id).value));if(values.some(v=>!Number.isFinite(v)||v<0)){status('profit-status','Use zero or positive numbers for harvest, price, and cost.',true);return;}status('profit-status','');const r=profit(...values);reveal('profit-result',`${title('Your harvest estimate','మీ పంట ఆదాయ అంచనా')}<div class="stats"><div class="stat"><strong>${money(r.revenue)}</strong><span>Gross sales</span></div><div class="stat"><strong>${money(values[2])}</strong><span>Total entered cost</span></div><div class="stat"><strong>${money(Math.abs(r.profit))}</strong><span>${r.profit<0?'Estimated loss':r.profit===0?'Break-even':'Estimated profit'}</span></div></div><p>${esc(D.market.profit)}</p>${printButton('profit-result')}`);});
  }
  function weatherAdvice(days) {
    const tips=[];if(days.some(d=>d.rain>=35))tips.push(D.weather.heavy);else if(days.some(d=>d.rain>=2))tips.push(D.weather.rain);
    if(days.some(d=>d.max>=35))tips.push(D.weather.heat);if(days.some(d=>d.wind>=25))tips.push(D.weather.wind);return tips.length?tips:[D.weather.calm];
  }
  async function getJSON(url) {
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),12000);
    try{const response=await fetch(url,{signal:controller.signal,credentials:'omit'});if(!response.ok)throw new Error('Request failed');return await response.json();}finally{clearTimeout(timer);}
  }
  function weatherIcon(code){return code<=1?'☀️':code<=3?'⛅':code<=48?'🌫️':code>=95?'⛈️':((code>=71&&code<=77)||code===85||code===86)?'🌨️':'🌧️';}
  function setupWeather() {
    let request=0;
    $('city').addEventListener('change',()=>{$('custom-city-field').hidden=!($('city').value==='custom'||$('city').value.startsWith('district:'));$('custom-city').required=$('city').value==='custom';});
    $('weather-form').addEventListener('submit',async event=>{
      event.preventDefault();const id=++request,button=$('weather-submit');button.disabled=true;$('weather-result').hidden=true;status('weather-status','Getting the latest forecast…');
      try{
        let city;
        if(($('city').value==='custom'||$('city').value.startsWith('district:'))){
          const query=$('city').value.startsWith('district:')?$('city').value.slice(9):$('custom-city').value.trim();if(!query){status('weather-status','Please enter a city name.',true);return;}
          const geo=await getJSON('https://geocoding-api.open-meteo.com/v1/search?name='+encodeURIComponent(query)+'&count=5&language=en&format=json&countryCode=IN');
          const match=geo.results?.find(r=>r.country_code==='IN');
          if(!match){status('weather-status','We could not find that city in India. Some district names do not identify a city. Choose Another city and enter your district headquarters or a nearby town.',true);return;}
          city={name:match.name+(match.admin1?', '+match.admin1:''),lat:match.latitude,lon:match.longitude};
        }else city=D.cities[Number($('city').value)];
        const url='https://api.open-meteo.com/v1/forecast?'+new URLSearchParams({latitude:city.lat,longitude:city.lon,daily:'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',forecast_days:7,timezone:'Asia/Kolkata',wind_speed_unit:'kmh'});
        const result=await getJSON(url),d=result.daily;
        if(!d||!Array.isArray(d.time)||d.time.length!==7)throw new Error('Incomplete forecast');
        const days=d.time.map((date,i)=>({date,code:d.weather_code?.[i],max:d.temperature_2m_max?.[i],min:d.temperature_2m_min?.[i],rain:d.precipitation_sum?.[i],wind:d.wind_speed_10m_max?.[i]}));
        if(days.some(day=>![day.code,day.max,day.min,day.rain,day.wind].every(v=>typeof v==='number'&&Number.isFinite(v))))throw new Error('Missing daily values');
        if(id!==request)return;
        reveal('weather-result',`${title('Your seven-day outlook','మీ ఏడు రోజుల వాతావరణం')}<p class="forecast-location"><strong>${esc(city.name)}</strong> • Updated ${esc(new Date().toLocaleString('en-IN',{timeZone:'Asia/Kolkata'}))} IST</p><div class="weather-grid">${days.map(day=>`<div class="day"><strong>${esc(new Date(day.date+'T12:00:00+05:30').toLocaleDateString(language==='te'?'te-IN':'en-IN',{weekday:'short',day:'numeric',month:'short',timeZone:'Asia/Kolkata'}))}</strong><span class="weather-icon" aria-label="Forecast condition">${weatherIcon(day.code)}</span><strong>${Math.round(day.max)}° / ${Math.round(day.min)}°</strong><small>High / low °C</small><small>Rain: ${day.rain.toFixed(1)} mm</small><small>Wind: ${Math.round(day.wind)} km/h</small></div>`).join('')}</div>${title('What this means for your field','మీ పొలానికి ఉపయోగపడే సలహా','h3')}${list(weatherAdvice(days))}<p>${esc(D.weather.note)}</p><p class="source-links"><a href="https://open-meteo.com/" target="_blank" rel="noopener noreferrer">${esc(D.weather.source)}</a> <a href="https://mausam.imd.gov.in/" target="_blank" rel="noopener noreferrer">Official IMD warnings ↗</a></p>${printButton('weather-result')}${end()}<div id="weather-charts"></div>`);window.RythuCharts.weather(days,city.name);status('weather-status','Forecast updated. Check local warnings before field work.');
      }catch(_){if(id===request)status('weather-status','We could not load the weather. Please check your internet and try again, or use the official IMD link below. No sample forecast is being shown.',true);if(!$('weather-fallback'))$('weather-form').insertAdjacentHTML('beforeend','<p id="weather-fallback"><a href="https://mausam.imd.gov.in/" target="_blank" rel="noopener noreferrer">Check official IMD weather ↗</a></p>');}
      finally{if(id===request)button.disabled=false;}
    });
    const requestedPlace=new URLSearchParams(location.search).get('location');
    if(requestedPlace){$('city').value='custom';$('custom-city').value=requestedPlace;$('city').dispatchEvent(new Event('change'));}
    $('weather-form').requestSubmit();
  }
  function eligibility(area,state,type) {
    const notes=[D.schemeNotes.intro];
    if(area>0&&area<=4.9421)notes.push(D.schemeNotes.small);
    notes.push(type==='landless'||area===0?D.schemeNotes.landless:type==='owner'?D.schemeNotes.owner:D.schemeNotes.tenant);
    if(area>0&&type!=='landless'){notes.push(state==='telangana'?D.schemeNotes.telangana:D.schemeNotes.other);notes.push(D.schemeNotes.all);}
    return notes;
  }
  function setupSchemes() {
    $('scheme-cards').innerHTML=D.schemes.map(s=>`<article class="card" id="scheme-${s.id}"><span class="badge">${dual('Official support','అధికారిక సహాయం')}</span>${title(s.name,s.te,'h3')}${title('Who can ask?','ఎవరు అడగవచ్చు?','h4')}<p>${esc(s.eligible)}</p>${title('Benefits','ప్రయోజనాలు','h4')}<p>${esc(s.benefit)}</p>${title('Documents to prepare','సిద్ధం చేసుకోవలసిన పత్రాలు','h4')}<p>${esc(s.documents)}</p>${title('How to apply','దరఖాస్తు విధానం','h4')}<p>${esc(s.apply)}</p><a class="button secondary small" href="${s.url}" target="_blank" rel="noopener noreferrer">${dual('Official website ↗','అధికారిక వెబ్‌సైట్ ↗')}</a>${end()}</article>`).join('');
    $('eligibility-form').addEventListener('submit',event=>{event.preventDefault();const area=Number($('scheme-area').value),state=$('state').value,type=$('farmer-type').value;if(!Number.isFinite(area)||area<0||area>10000){status('scheme-status','Enter a valid area from 0 to 10,000 acres.',true);return;}if(type==='landless'&&area>0){status('scheme-status','For a landless agricultural worker enter 0 acres, or select tenant / owner if you cultivate land.',true);return;}status('scheme-status','');reveal('eligibility-result',`${title('Places to start your enquiry','మీ విచారణ ప్రారంభించవలసిన చోటులు')}${list(eligibility(area,state,type))}<div class="button-row"><a class="button secondary" href="#scheme-soil">Soil Health Card</a><a class="button secondary" href="#scheme-kcc">Kisan Credit Card</a>${printButton('eligibility-result')}</div>${end()}`);});
  }
  window.AgriTools={fertilizerPlan,waterPlan,profit,weatherAdvice,eligibility};
  buildSharedUI();fillCrops();
  ({home:setupHome,disease:setupDisease,fertilizer:setupFertilizer,irrigation:setupIrrigation,market:setupMarket,weather:setupWeather,schemes:setupSchemes}[page]||(()=>{}))();
  const requestedSlots=new URLSearchParams(location.search);
  if(requestedSlots.get('auto')==='1'){
    if(requestedSlots.get('stage')){document.body.dataset.stage=requestedSlots.get('stage');const context=document.createElement('p');context.id='guide-context';context.textContent='Detected growth stage: '+requestedSlots.get('stage').replaceAll('_',' ');document.getElementById('main').prepend(context);}
    const stage=requestedSlots.get('stage');
    if(page==='disease'){
      $('disease-crop').dispatchEvent(new Event('change'));
      for(const key of (requestedSlots.get('symptom')||'').split(',')){const input=document.querySelector('input[name="symptom"][value="'+key.replace(/[^a-z]/g,'')+'"]');if(input)input.checked=true;}
      if(document.querySelector('input[name="symptom"]:checked'))$('symptom-form').requestSubmit();
    }
    if(page==='fertilizer'){
      $('fert-stage').value=['sowing','seedling','germination'].includes(stage)?'basal':stage==='vegetative'?'vegetative':'reproductive';
      if(!stage)$('fert-stage').value='basal';$('fertilizer-form').requestSubmit();
    }
    if(page==='irrigation')$('irrigation-form').requestSubmit();
    if(page==='schemes')$('eligibility-form').requestSubmit();
  }
  applyLanguage();
  document.body.dataset.ready='1';
})();
