/* Local SVG charts. Data remains in tables; no network, libraries, or synthetic values. */
(function () {
  'use strict';
  const NS='http://www.w3.org/2000/svg', mounted=new Map();
  const t=(en,te)=>document.documentElement.lang==='te'?te:en;
  const colors=['#245b37','#9b6900','#994038'];
  const node=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
  function svgNode(tag,attrs={},text){const n=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;return n;}
  function words(text,width){const lines=[];let line='';for(const word of String(text).split(' ')){if(line.length+word.length>width&&line){lines.push(line);line='';}line+=(line?' ':'')+word;}if(line)lines.push(line);return lines;}
  function figure(host,title,description){const f=node('figure',undefined,'data-chart');f.append(node('figcaption',title,'chart-title'),node('p',description,'chart-note'));host.append(f);return f;}
  function table(host,headers,rows,caption){const wrap=node('div',undefined,'table-wrap chart-data'),tab=node('table');tab.append(node('caption',caption));const tr=tab.createTHead().insertRow();headers.forEach(h=>tr.append(node('th',h)));const body=tab.createTBody();rows.forEach(row=>{const r=body.insertRow();row.forEach((v,i)=>{const cell=node(i===0?'th':'td',v);if(i===0)cell.scope='row';r.append(cell);});});wrap.append(tab);host.append(wrap);}
  function mount(host,render){if(typeof host==='string')host=document.getElementById(host);if(!host)return;mounted.set(host,render);host.replaceChildren();render(host);}
  function refresh(){for(const [host,render] of mounted){if(host.isConnected){host.replaceChildren();render(host);}else mounted.delete(host);}}
  new MutationObserver(refresh).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(refresh,100);});
  const percent=x=>(x*100).toFixed(2)+'%';
  const number=x=>new Intl.NumberFormat(document.documentElement.lang==='te'?'te-IN':'en-IN',{maximumFractionDigits:2}).format(x);
  function bars(host,{title,description,rows,series,unit='',percentages=false}){
    const f=figure(host,title,description),width=Math.max(260,Math.min(host.clientWidth||600,960)-20),left=percentages?92:14,right=percentages?78:108,plot=width-left-right;
    const values=rows.flatMap(r=>r.values).filter(Number.isFinite),lo=percentages?0:Math.min(0,...values),hi=percentages?1:Math.max(0,...values),span=hi-lo||1;
    const x=v=>left+(v-lo)/span*plot;let y=32;
    const svg=svgNode('svg',{width:'100%',role:'img','aria-label':title+'; '+description});
    svg.append(svgNode('title',{},title),svgNode('desc',{},description));
    const ticks=[lo,lo<0&&hi>0?0:lo+span/2,lo+span];
    ticks.forEach((tick,i)=>svg.append(svgNode('text',{x:x(tick),y:14,'text-anchor':i===0?'start':i===2?'end':'middle',class:'chart-tick'},percentages?Math.round(tick*100)+'%':number(tick))));
    for(const row of rows){
      for(const label of words(row.label,Math.max(22,Math.floor(width/8)))){svg.append(svgNode('text',{x:3,y:y+14,class:'chart-label'},label));y+=21;}
      row.values.forEach((value,i)=>{
        if(!Number.isFinite(value))return;
        const pos=y+8,rect=svgNode('rect',{x:Math.min(x(0),x(value)),y:pos,width:Math.abs(x(value)-x(0)),height:17,rx:3,fill:value<0?colors[2]:colors[i%colors.length]});
        const label=(series[i]||'')+': '+(percentages?percent(value):number(value))+(unit?' '+unit:'');
        rect.append(svgNode('title',{},row.label+' — '+label+'; '+String(value)));svg.append(rect);
        if(percentages)svg.append(svgNode('text',{x:3,y:pos+13,class:'chart-tick'},series[i]));
        svg.append(svgNode('text',{x:width-right+7,y:pos+13,class:'chart-value'},percentages?percent(value):number(value)));
        if(!percentages&&value<0)svg.append(svgNode('text',{x:width-right+7,y:pos+30,class:'chart-tick'},t('Loss','నష్టం')));
        y+=percentages?27:39;
      });y+=17;
    }
    svg.insertBefore(svgNode('line',{x1:x(0),x2:x(0),y1:23,y2:y,stroke:'#778878','stroke-width':1}),svg.children[2]||null);
    svg.setAttribute('viewBox',`0 0 ${width} ${y+10}`);f.append(svg);
    table(f,[t('Item','అంశం'),...series.map(s=>s+(unit?' ('+unit+')':percentages?' (0–1)':''))],rows.map(r=>[r.label,...r.values.map(v=>Number.isFinite(v)?String(v):t('Not recorded','నమోదు కాలేదు'))]),percentages?t('Exact saved metric values (0–1); bars show percentages rounded to two decimals.','భద్రపరిచిన ఖచ్చితమైన విలువలు (0–1); పట్టీలలో శాతాలు రెండు దశాంశాలకు చూపించబడ్డాయి.'):t('Chart values','గ్రాఫ్ విలువలు'));
  }
  function modelCharts(m){
    const control=document.getElementById('chart-benchmark');
    const render=host=>{const workbook=control.value==='workbook';bars(host,{title:workbook?t('Secondary workbook test — raw ML','ద్వితీయ వర్క్‌బుక్ పరీక్ష — ముడి ML'):t('Primary authored benchmark — raw ML','ప్రధాన రచిత బెంచ్‌మార్క్ — ముడి ML'),description:(workbook?m.split_counts.test:m.robustness.rows)+' '+t('queries. Validation selected the model; these results did not select it.','ప్రశ్నలు. మోడల్ ఎంపిక ధృవీకరణ ఫలితాలతో జరిగింది; ఈ ఫలితాలతో కాదు.'),rows:m.comparison.map(r=>{const score=workbook?{accuracy:r.test_accuracy,macro_f1:r.test_macro_f1}:m.robustness.raw_models.find(x=>x.experiment===r.key);return {label:r.model+' / '+r.features,values:[score?.accuracy,score?.macro_f1]};}),series:[t('Accuracy','ఖచ్చితత్వం'),'Macro-F1'],percentages:true});};
    control.addEventListener('change',()=>mount('model-charts',render));mount('model-charts',render);
    const rows=[
      {label:t('Workbook test · raw selected model','వర్క్‌బుక్ పరీక్ష · ముడి ఎంపిక మోడల్')+' · n='+m.split_counts.test,values:[m.selected.test_accuracy,m.selected.test_macro_f1]},
      {label:t('Original handwritten benchmark · raw selected model','అసలు చేతిరాత బెంచ్‌మార్క్ · ముడి ఎంపిక మోడల్')+' · n='+m.handwritten.rows,values:[m.handwritten.accuracy,m.handwritten.macro_f1]},
      {label:t('Larger authored benchmark · raw selected model','పెద్ద రచిత బెంచ్‌మార్క్ · ముడి ఎంపిక మోడల్')+' · n='+m.robustness.rows,values:[m.robustness.selected_raw.accuracy,m.robustness.selected_raw.macro_f1]},
      {label:t('Cross-script · separate combined-feature LR protocol','లిపుల మధ్య పరీక్ష · వేరే combined-feature LR విధానం')+' · n='+m.robustness.cross_script.test_rows,values:[m.robustness.cross_script.accuracy,m.robustness.cross_script.macro_f1]}
    ];
    // Labels must be reconstructed when language changes, too.
    mount('generalization-charts',host=>{
      const labels=[t('Workbook test · raw selected model','వర్క్‌బుక్ పరీక్ష · ముడి ఎంపిక మోడల్'),t('Original handwritten benchmark · raw selected model','అసలు చేతిరాత బెంచ్‌మార్క్ · ముడి ఎంపిక మోడల్'),t('Larger authored benchmark · raw selected model','పెద్ద రచిత బెంచ్‌మార్క్ · ముడి ఎంపిక మోడల్'),t('Cross-script · separate combined-feature LR protocol','లిపుల మధ్య పరీక్ష · వేరే combined-feature LR విధానం')];
      const sizes=[m.split_counts.test,m.handwritten.rows,m.robustness.rows,m.robustness.cross_script.test_rows];
      bars(host,{title:t('Generalization across evaluation sets','వేర్వేరు పరీక్షలలో పనితీరు'),description:t('Selected model: '+m.selected.model+' / '+m.selected.features+'. Evaluation sets differ in difficulty, size and construction; this is not a time trend. The cross-script result uses a separate combined-feature Logistic Regression (C=2), trained on English/code-mixed text and tested on Telugu. It is not a measurement of the selected word model. Authored sets are synthetic challenges, not representative farmer samples.','ఎంపిక మోడల్: '+m.selected.model+' / '+m.selected.features+'. పరీక్షల కఠినత, పరిమాణం, నిర్మాణం వేర్వేరు; ఇది కాలానుగుణ ధోరణి కాదు. లిపుల మధ్య ఫలితం వేరే combined-feature Logistic Regression (C=2) మోడల్‌ది; ఇంగ్లీషు/మిశ్రమ పాఠ్యంతో శిక్షణ, తెలుగులో పరీక్ష. ఇది ఎంపిక చేసిన word మోడల్ ఫలితం కాదు. రచిత ప్రశ్నలు నిజమైన రైతుల ప్రతినిధి నమూనా కాదు.'),rows:rows.map((r,i)=>({...r,label:labels[i]+' · n='+sizes[i]})),series:[t('Accuracy','ఖచ్చితత్వం'),'Macro-F1'],percentages:true});
      bars(host,{title:t('Routing rules shown separately','రూటింగ్ నియమాల ఫలితాలు విడిగా'),description:t('Same 319-query authored benchmark: raw selected model versus deployed guard/slot routing rules. Rule-assisted performance is not raw ML performance.','అదే 319 రచిత ప్రశ్నలు: ముడి ఎంపిక మోడల్ మరియు అమలులోని guard/slot రూటింగ్ నియమాలు. నియమాలతో వచ్చిన ఫలితం ముడి ML ఫలితం కాదు.'),rows:[{label:t('Raw selected ML','ముడి ఎంపిక ML'),values:[m.robustness.selected_raw.accuracy,m.robustness.selected_raw.macro_f1]},{label:t('Deployed routing rules + ML','అమలులోని రూటింగ్ నియమాలు + ML'),values:[m.robustness.deployed_rules.accuracy,m.robustness.deployed_rules.macro_f1]}],series:[t('Accuracy','ఖచ్చితత్వం'),'Macro-F1'],percentages:true});
    });
  }
  const norm=x=>typeof x==='string'?x.trim().replace(/\s+/g,' ').toLowerCase():'';
  const known=x=>norm(x)&&!['na','n/a','other','others','unknown','not reported','not specified','-'].includes(norm(x));
  function priceGroups(data){
    const groups=new Map();
    if(data.status!=='ok'||!Array.isArray(data.records))return [];
    for(const r of data.records){
      const unit=r.unit||data.unit;
      const supported=norm(unit)==='inr per quintal (as published by the mandi resource)'||['inr/quintal','inr per quintal','rs/quintal','rs./quintal'].includes(norm(unit));
      const price=r.modal_price;
      if(!supported||!known(r.commodity)||!known(r.variety)||!known(r.grade)||!known(r.arrival_date)||!known(r.market)||price===null||price===undefined||String(price).trim()===''||!Number.isFinite(Number(price))||Number(price)<0)continue;
      const key=JSON.stringify([r.commodity,r.variety,r.grade,r.arrival_date].map(norm));
      if(!groups.has(key))groups.set(key,[]);groups.get(key).push(r);
    }
    return [...groups.values()].filter(g=>new Set(g.map(r=>norm(r.market)+'|'+norm(r.district))).size>1).map(group=>{
      // Ambiguous duplicate quotes for the same market are excluded, never averaged.
      const markets=new Map();for(const row of group){const key=norm(row.market)+'|'+norm(row.district);if(!markets.has(key))markets.set(key,[]);markets.get(key).push(row);}
      return [...markets.values()].filter(rows=>new Set(rows.map(r=>Number(r.modal_price))).size===1).map(rows=>rows[0]);
    }).filter(g=>g.length>1);
  }
  function prices(data){mount('market-charts',host=>{
    const groups=priceGroups(data);
    if(!groups.length){host.append(node('p',t('Price comparison unavailable: at least two different markets must report the same commodity, explicit matching variety and grade, reporting date, and INR/quintal unit. Missing or conflicting details cannot be compared. Available records remain in the price table below.','ధరల పోలిక అందుబాటులో లేదు: కనీసం రెండు మార్కెట్లలో ఒకే పంట, స్పష్టమైన ఒకే రకం మరియు గ్రేడ్, నివేదిక తేదీ, INR/క్వింటాల్ ప్రమాణం ఉండాలి. వివరాలు లేనప్పుడు లేదా విరుద్ధంగా ఉన్నప్పుడు పోల్చలేము. అందుబాటులోని వివరాలు కింది ధరల పట్టికలో ఉన్నాయి.'),'chart-note'));return;}
    groups.forEach(group=>{const r=group[0];bars(host,{title:t('Modal mandi price comparison','మండి మోడల్ ధరల పోలిక')+' — '+r.commodity,description:r.variety+' · '+r.grade+' · '+t('Reporting date','నివేదిక తేదీ')+': '+r.arrival_date+' · INR/quintal',rows:group.map(r=>({label:r.market+' · '+r.district,values:[Number(r.modal_price)]})),series:[t('Modal price','మోడల్ ధర')],unit:'INR/quintal'});});
  });}
  function clearPrices(){const host=document.getElementById('market-charts');if(host){mounted.delete(host);host.replaceChildren();}}
  function harvest(revenue,cost,profit){mount('harvest-chart',host=>bars(host,{title:t('Harvest estimate based on your inputs','మీ వివరాల ఆధారంగా పంట ఆదాయ అంచనా'),description:t('Entered harvest × sale price gives gross revenue. Profit/loss = revenue − total entered cost. This is an estimate, not a guaranteed sale price.','ఇచ్చిన దిగుబడి × అమ్మకపు ధర = స్థూల ఆదాయం. లాభం/నష్టం = ఆదాయం − మొత్తం ఖర్చు. ఇది అంచనా మాత్రమే; హామీ అమ్మకపు ధర కాదు.'),rows:[{label:t('Gross revenue','స్థూల ఆదాయం'),values:[revenue]},{label:t('Total cost','మొత్తం ఖర్చు'),values:[cost]},{label:profit<0?t('Profit/loss — loss','లాభం/నష్టం — నష్టం'):t('Profit/loss','లాభం/నష్టం'),values:[profit]}],series:[t('Amount','మొత్తం')],unit:'INR'}));}
  function weather(days,city){mount('weather-charts',host=>{
    const f=figure(host,t('Seven-day temperature forecast','ఏడు రోజుల ఉష్ణోగ్రత సూచన')+' — '+city,t('Daily high and low temperatures (°C). Forecast from Open-Meteo for the selected location.','రోజువారీ గరిష్ఠ, కనిష్ఠ ఉష్ణోగ్రతలు (°C). ఎంపిక చేసిన ప్రదేశానికి Open-Meteo సూచన.'));
    const width=Math.max(260,Math.min(host.clientWidth||600,900)-20),left=40,right=18,top=38,height=290,bottom=72;
    const low=Math.min(...days.map(d=>d.min))-2,high=Math.max(...days.map(d=>d.max))+2,span=high-low||1;
    const x=i=>left+i*(width-left-right)/6,y=v=>top+(high-v)/span*(height-top-bottom);
    const svg=svgNode('svg',{viewBox:`0 0 ${width} ${height}`,width:'100%',role:'img','aria-label':t('Daily high and low temperature in degrees Celsius','రోజువారీ గరిష్ఠ కనిష్ఠ ఉష్ణోగ్రతలు సెల్సియస్‌లో')});svg.append(svgNode('title',{},t('Temperature °C','ఉష్ణోగ్రత °C')));
    for(let i=0;i<=4;i++){const v=low+(high-low)*i/4;svg.append(svgNode('line',{x1:left,x2:width-right,y1:y(v),y2:y(v),stroke:'#dce5d9'}),svgNode('text',{x:0,y:y(v)+4,class:'chart-tick'},number(v)));}
    ['max','min'].forEach((key,s)=>{svg.append(svgNode('polyline',{points:days.map((d,i)=>x(i)+','+y(d[key])).join(' '),fill:'none',stroke:colors[s],'stroke-width':3,'stroke-dasharray':s?'6 4':'none'}));days.forEach((d,i)=>{const point=svgNode(s?'rect':'circle',s?{x:x(i)-3,y:y(d[key])-3,width:6,height:6,fill:colors[s]}:{cx:x(i),cy:y(d[key]),r:4,fill:colors[s]});point.append(svgNode('title',{},d.date+' '+key+' '+d[key]+' °C'));svg.append(point);});});
    days.forEach((d,i)=>svg.append(svgNode('text',{x:x(i),y:height-bottom+23,transform:`rotate(-45 ${x(i)} ${height-bottom+23})`,'text-anchor':'end',class:'chart-tick'},d.date)));
    f.append(node('p',t('High: solid green line / circles. Low: dashed gold line / squares. Unit: °C.','గరిష్ఠం: పచ్చ గీత / వృత్తాలు. కనిష్ఠం: బంగారు చుక్కల గీత / చతురస్రాలు. ప్రమాణం: °C.'),'chart-note'),svg);
    table(f,[t('Date','తేదీ'),t('High (°C)','గరిష్ఠం (°C)'),t('Low (°C)','కనిష్ఠం (°C)')],days.map(d=>[d.date,d.max,d.min]),t('Actual temperature forecast values','అసలు ఉష్ణోగ్రత సూచన విలువలు'));
    bars(host,{title:t('Seven-day rainfall forecast','ఏడు రోజుల వర్షపాతం సూచన')+' — '+city,description:t('Forecast rainfall totals by date, in mm. Zero means the forecast returned zero rainfall.','తేదీల వారీగా వర్షపాతం సూచన, మి.మీ.లో. సున్నా అంటే సూచనలో వర్షపాతం సున్నా.'),rows:days.map(d=>({label:d.date,values:[d.rain]})),series:[t('Rainfall','వర్షపాతం')],unit:'mm'});
  });}
  window.RythuCharts={modelCharts,prices,clearPrices,harvest,weather,priceGroups};
})();
