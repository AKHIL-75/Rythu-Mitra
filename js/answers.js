/* Direct answers reuse reviewed knowledge-base entries; predictions do not create facts. */
(function(){
 const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const dual=(en,te)=>`<span data-en="${esc(en)}" data-te="${esc(te)}">${esc(document.documentElement.lang==='te'?te:en)}</span>`;
 const help=()=>`<p>${dual('For field-specific advice, consult your agriculture officer.','మీ పొలానికి తగిన సలహా కోసం వ్యవసాయ అధికారిని సంప్రదించండి.')} <a href="tel:18001801551">Kisan Call Centre: 1800-180-1551</a></p>`;
 const symptomName=k=>dual(SLOT_CONFIG.symptoms[k].en,SLOT_CONFIG.symptoms[k].te);
 function causes(crop,symptoms,q='',observations=[]){
  const D=window.AGRI,matches=(D.diseases[crop]||[]).filter(d=>d[4]!=='officer'&&d[3].some(k=>symptoms.includes(k)));
  let h=window.PracticalGuidance.symptoms(crop,symptoms,q,observations);
  if(matches.length)h+=`<details class="practical-matches"><summary>${dual('Other crop-guide possibilities to compare — not a diagnosis','పోల్చడానికి ఇతర పంట గైడ్ అవకాశాలు — నిర్ధారణ కాదు')}</summary>`+matches.map(d=>{const care=D.diseaseCare[d[4]];return `<article class="card"><h4>${dual(d[0],d[1])}</h4><p>${esc(d[2])}</p><p>${dual(care.organic,care.organicTe||care.organic)}</p></article>`;}).join('')+'</details>';
  return h;
 }
 function build(q,a){
  const specific=window.FarmRequests.build(q,a);
  const other=window.PracticalGuidance.other(q,a);
  if(other&&['other_agri','out_of_scope'].includes(a.intent))a={...a,intent:'other_agri',clarify:false};
  const D=window.AGRI,c=D.crops[a.crop],topic=D.topics[a.intent],symptoms=a.symptoms||[];
  let h=`<h2>${dual('Your farm question','మీ వ్యవసాయ ప్రశ్న')}</h2>`;
  if(a.intent==='out_of_scope'||!topic)return h+`<p>${dual('Please ask a farming question. Tell us your crop and what you need help with.','దయచేసి వ్యవసాయ ప్రశ్న అడగండి. మీ పంట, అవసరమైన సహాయం చెప్పండి.')}</p>`+help();
  if(a.clarify&&a.routing==='model_threshold'&&!other&&!specific)return h+`<p>${dual('Which farming topic do you need help with?','ఏ వ్యవసాయ విషయంపై సహాయం కావాలి?')}</p><div class="button-row">`+['crop_disease','fertilizer','irrigation','market_price','weather','govt_scheme'].map(k=>`<button type="button" class="button secondary small" data-question="${esc(q+' '+SLOT_CONFIG.intent_keywords[k][0])}">${dual(D.topics[k].en,D.topics[k].te)}</button>`).join('')+'</div>'+help();
  h+=`<div class="result-head"><span class="badge">${dual(topic.en,topic.te)}</span><strong class="detected-crop">${c?dual(c.en,c.te):dual('Crop not mentioned','పంట పేరు లేదు')}</strong>${symptoms.map(k=>`<span class="badge detected-symptom" data-symptom="${k}">${symptomName(k)}</span>`).join('')}</div>`;
  if(a.stage)h+=`<p>${dual('Detected growth stage:','గుర్తించిన పంట దశ:')} ${esc(a.stage.replaceAll('_',' '))}</p>`;
  if(a.location)h+=`<p>${dual('Location:','ప్రాంతం:')} ${esc(a.location)}</p>`;
  if(a.intent==='crop_disease'&&symptoms.length&&a.problem?.label&&a.problem.confidence>=.55&&a.problem.label.toLowerCase()!=='not specified')h+=`<p>${dual('Possible problem wording — please confirm:','సంభావ్య సమస్య పేరు — దయచేసి నిర్ధారించండి:')} ${esc(a.problem.label)}. ${dual('This suggestion is not a field diagnosis.','ఇది పొలంలో చేసిన నిర్ధారణ కాదు.')}</p>`;
  const cropNeeded=['crop_disease','fertilizer','irrigation','market_price'].includes(a.intent);
  if(!c&&cropNeeded&&!specific){
    h+=`<p>${dual('Which crop? Tap a crop below.','ఏ పంట? కింద పంటను ఎంచుకోండి.')}</p><div class="button-row">`;
    const button=k=>`<button type="button" class="button secondary small" data-question="${esc(D.crops[k].en+' '+q)}">${dual(D.crops[k].en,D.crops[k].te)}</button>`;
    h+=['paddy','cotton','tomato','chilli','brinjal','maize'].map(button).join('')+'</div><details><summary>'+dual('All crops','అన్ని పంటలు')+'</summary><div class="button-row">'+Object.keys(D.crops).map(button).join('')+'</div></details>';
    return h+help();
  }
  if(specific){
    h+=specific;
  }else if(a.intent==='crop_disease'){
    if(!symptoms.length&&!a.observations?.length){
      h+=window.FarmRequests.cropHealth();
      h+=`<p>${dual('What do you observe? Tap a symptom.','ఏ లక్షణం కనిపిస్తోంది? కింద ఎంచుకోండి.')}</p><div class="button-row">`+Object.keys(SLOT_CONFIG.symptoms).map(k=>`<button type="button" class="button secondary small" data-question="${esc(q+' '+SLOT_CONFIG.symptoms[k].aliases[0])}">${symptomName(k)}</button>`).join('')+'</div>';
      if(a.observations?.length)h+=`<p>${dual('This observation has no verified crop-specific answer here; a field inspection is needed.','ఈ పరిశీలనకు ఇక్కడ నిర్ధారించిన పంట సలహా లేదు. పొలంలో పరిశీలన అవసరం.')}</p>`;
      h+=help();
    }else h+=causes(a.crop,symptoms,q,a.observations||[]);
  }else if(a.intent==='fertilizer'){
    h+=window.PracticalGuidance.fertilizer();
    h+=window.FarmRequests.fertilizer(q,a);
    const n=D.nutrients[a.crop];h+=`<h3>${dual('Nutrient guidance for your crop','మీ పంటకు పోషకాల సలహా')}</h3><p>${dual(n.note,n.noteTe)}</p><p>${dual('A detected stage helps you discuss timing, but it does not establish a safe fertilizer dose. Use your soil report and record earlier applications.','దశను బట్టి సమయాన్ని అధికారితో చర్చించండి. మోతాదు కోసం భూసార నివేదిక, ముందుగా వేసిన ఎరువుల వివరాలు అవసరం.')}</p><p><a href="${esc(n.source)}" target="_blank" rel="noopener">${esc(n.sourceName)}</a></p>`+help();
  }else if(a.intent==='irrigation'){
    h+=window.PracticalGuidance.irrigation();
    h+=`<h3>${dual('Water guidance for your crop','మీ పంటకు నీటి సలహా')}</h3><p>${dual(c.tip,c.tipTe)}</p><p>${dual('No fixed crop-specific interval or depth is verified here. The full guide can convert the depth you choose into litres; it does not prescribe that depth.','ఇక్కడ నిర్ణీత నీటి వ్యవధి లేదా లోతు నిర్ధారించలేదు. పూర్తి మార్గదర్శి మీరు ఎంచుకున్న లోతును లీటర్లుగా మారుస్తుంది.')}</p><a href="${esc(c.waterSource)}" target="_blank" rel="noopener">ICAR — soil-moisture scheduling</a>`+help();
  }else if(a.intent==='market_price'){
    const params=new URLSearchParams({crop:a.crop});if(a.location)params.set('district',a.location);
    h+=window.FarmRequests.pricePlan(q,a);
    h+=`<h3>${dual('Check reported mandi prices','నివేదించిన మండి ధరలు చూడండి')}</h3><p>${dual('Open the market page with your crop selected. Choose your Telangana district, then compare the reported market, date, variety and grade. A current price must come from the price service; it cannot be inferred from your question.','మీ పంట ఎంపికతో మార్కెట్ పేజీ తెరవండి. తెలంగాణ జిల్లాను ఎంచుకుని మార్కెట్, తేదీ, రకం, గ్రేడ్ పోల్చండి. తాజా ధర ధరల సేవ నుంచి రావాలి; మీ ప్రశ్నతో ఊహించలేం.')}</p><a class="button" href="market-prices.html?${params}">${dual('View mandi rates for this crop','ఈ పంటకు మండి ధరలు చూడండి')}</a>`;
  }else if(a.intent==='weather'){
    h+=window.FarmRequests.weatherPlan(q,a);
  }else if(other){
    h+=other;
  }else{
    h+=`<p>${esc(D.home[a.intent]?.[0]||'No verified answer is available here. Please ask your agriculture officer.')}</p><p>${dual('The crop and stage do not confirm eligibility. Your district notification, cultivation records and the responsible office decide.','పంట, దశ అర్హతను నిర్ధారించవు. జిల్లా నోటిఫికేషన్, సాగు పత్రాలు, సంబంధిత కార్యాలయ నిర్ణయం వర్తిస్తాయి.')}</p>`+help();
  }
  const params=new URLSearchParams();if(c)params.set('crop',a.crop);if(symptoms.length)params.set('symptom',symptoms.join(','));if(a.stage)params.set('stage',a.stage);if(a.location)params.set('location',a.location);params.set('intent',a.intent);params.set('auto','1');
  if(!specific)h+=`<div class="button-row"><a class="button full-guide" href="${topic.file}?${params}">${dual('See full guide','పూర్తి మార్గదర్శి చూడండి')}</a></div>`;
  h+=window.PracticalGuidance.followup(q,a);
  return h+`<p class="disclaimer">${esc(D.disclaimer)}</p>`;
 }
 const weather=(a,q='')=>window.FarmRequests.weather(q,a);
 const prices=(a,q='')=>window.FarmRequests.prices(q,a);
 window.DirectAnswers={build,causes,weather,prices};
})();
