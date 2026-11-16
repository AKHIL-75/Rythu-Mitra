/* Temporary admin diagnostics. Never persist a token or use query-string authentication. */
'use strict';
const form=document.getElementById('diagnostics-form'),button=document.getElementById('run'),statusNode=document.getElementById('status');
form.addEventListener('submit',async event=>{
 event.preventDefault();if(button.disabled)return;
 let token=document.getElementById('token').value.trim();document.getElementById('token').value='';
 if(!token){statusNode.textContent='Enter the separate diagnostics token.';return;}
 const filters={state:'Telangana',district:document.getElementById('district').value.trim(),commodity:document.getElementById('commodity').value.trim()};
 const output=document.getElementById('results'),interpretation=document.getElementById('interpretation');output.replaceChildren();interpretation.textContent='';
 const table=document.createElement('table'),header=table.createTHead().insertRow();
 for(const name of ['Test','Result','Seconds','Provider HTTP']){const th=document.createElement('th');th.scope='col';th.textContent=name;header.append(th);}const body=table.createTBody();output.append(table);
 button.disabled=true;form.setAttribute('aria-busy','true');const results=[];
 try{
  for(const stage of ['minimal','state','filtered']){
   statusNode.textContent='Running '+stage+' test (up to 15 seconds)...';
   const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);let data;
   try{
    const response=await fetch('/_diagnostics/prices',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+token},body:JSON.stringify({stage,filters}),cache:'no-store',signal:controller.signal});
    if(response.status===401)throw new Error('Token rejected. Check DIAGNOSTICS_TOKEN on this deployment.');
    if(response.status===404)throw new Error('Diagnostics are disabled or this deployment lacks the new code. Add DIAGNOSTICS_TOKEN and redeploy.');
    if(!response.ok)throw new Error('Diagnostic endpoint returned HTTP '+response.status+'.');
    data=await response.json();
   }finally{clearTimeout(timer);}
   results.push(data);const row=body.insertRow();for(const value of [stage,data.status,data.elapsed_seconds??'—',data.upstream_http_status??'No HTTP response'])row.insertCell().textContent=String(value);
  }
  statusNode.textContent='All three tests completed.';
  if(results.every(r=>r.status==='ok'))interpretation.textContent='All connection tests succeeded. An empty price result can still mean no matching district/commodity records. Retry Market Prices; these probes request only one record.';
  else if(results[0]?.status==='ok')interpretation.textContent='The minimal request succeeded. Compare the state and filtered rows to identify which filtered request failed. Missing data and connection failure are different outcomes.';
  else interpretation.textContent='Even the minimal request failed. The failure is not limited to your district or crop. Send this table; more frontend changes cannot resolve an upstream connection failure.';
 }catch(error){statusNode.textContent=error.name==='AbortError'?'The diagnostic endpoint exceeded 15 seconds. Check Vercel runtime logs.':error.message;}
 finally{token='';button.disabled=false;form.removeAttribute('aria-busy');}
});
