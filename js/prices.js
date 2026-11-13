/* Reported mandi prices only; never substitute historical MSP or invented rates. */
document.addEventListener('DOMContentLoaded',()=>{
 const form=document.getElementById('live-price-form');if(!form)return;
 const status=document.getElementById('live-price-status'),out=document.getElementById('live-price-results');
 const districtSelect=document.getElementById('live-district');
 const cropSelect=document.getElementById('live-commodity');
 for(const name of window.SLOT_DISTRICTS?.Telangana||[]){
  const option=document.createElement('option');option.value=name;option.textContent=name;districtSelect.append(option);
 }
 const crops=[...(window.CROP_CATALOG||[])].sort((a,b)=>a.english_name.localeCompare(b.english_name));
 for(const crop of crops){
  const option=document.createElement('option');option.value=crop.english_name;
  option.textContent=(crop.id==='chilli'?'Chilli (dry red)':crop.english_name)+(crop.romanized_aliases?.length?' / '+crop.romanized_aliases[0]:'');
  cropSelect.append(option);
 }
 const requestedCrop=new URLSearchParams(location.search).get('crop');
 const selectedCrop=crops.find(crop=>crop.id===requestedCrop);
 if(selectedCrop)cropSelect.value=selectedCrop.english_name;
 const requestedDistrict=new URLSearchParams(location.search).get('district')||new URLSearchParams(location.search).get('location');
 if((window.SLOT_DISTRICTS?.Telangana||[]).includes(requestedDistrict))districtSelect.value=requestedDistrict;
 const button=form.querySelector('button');
 let loading=false;
 form.addEventListener('submit',async e=>{
  e.preventDefault();if(loading)return;out.replaceChildren();
  if(location.protocol==='file:'){status.textContent='Live price lookup needs the local server. Open Agmarknet, or run python app.py. No live rate is shown.';return;}
  const params=new URLSearchParams({state:'Telangana'});for(const k of ['district','market','commodity']){const v=document.getElementById('live-'+k).value.trim();if(v)params.set(k,k==='commodity'?({'Chilli':'Dry Chillies','Paddy':'Paddy(Dhan)(Common)'}[v]||v):v);}
  loading=true;button.disabled=true;form.setAttribute('aria-busy','true');
  const buttonText=button.textContent;button.textContent='Checking prices...';
  status.textContent='Checking reported mandi rates. This may take up to 30 seconds.';const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),35000);
  try{
   const r=await fetch('/prices?'+params,{signal:controller.signal}),data=await r.json();status.textContent=data.message;
   if(!r.ok||data.status!=='ok')return;
   const table=document.createElement('table'),head=table.createTHead().insertRow();
   for(const h of ['Commodity / variety','State / district','Market','Reporting date','Minimum','Maximum','Modal (₹/quintal)']){const th=document.createElement('th');th.textContent=h;head.append(th);}
   const body=table.createTBody();for(const row of data.records){const tr=body.insertRow();for(const value of [row.commodity+' / '+(row.variety||'not reported'),row.state+' / '+row.district,row.market,row.arrival_date,row.min_price??'not reported',row.max_price??'not reported',row.modal_price])tr.insertCell().textContent=String(value);}
   out.append(table);const note=document.createElement('p');note.textContent='Source: data.gov.in / AGMARKNET. Fetched '+data.fetched_at+(data.cached?' (cached up to 10 minutes).':'.')+' Reporting dates may be older than today.';out.append(note);
  }catch(error){status.textContent=error.name==='AbortError'?'The price request took too long. Please retry later or see Agmarknet. No live rate is shown.':'Live prices could not be loaded. Please retry or see Agmarknet. No live rate is shown.';}
  finally{clearTimeout(timer);loading=false;button.disabled=false;button.textContent=buttonText;form.removeAttribute('aria-busy');}
 });
 if(location.protocol!=='file:')form.requestSubmit();
});
