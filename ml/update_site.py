"""Apply focused, reproducible upgrades to the existing multi-page site."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def update():
    for path in ROOT.glob('*.html'):
        s=path.read_text(encoding='utf8')
        if 'js/crops-data.js' not in s:
            s=s.replace('<script defer src="js/advice.js"></script>',
                '<script defer src="js/crops-data.js"></script>\n  <script defer src="js/advice.js"></script>\n  <script defer src="js/coverage.js"></script>')
        if 'js/model-data.js' not in s:s=s.replace('<script defer src="js/classifier.js"></script>',
            '<script defer src="js/entities.js"></script>\n  <script defer src="js/model-data.js"></script>\n  <script defer src="js/classifier.js"></script>')
        if path.name=='about.html' and 'model-report.html' not in s:
            s=s.replace('<div class="wrap content">','<div class="wrap content"><section class="panel"><a class="button" href="model-report.html" data-en="Model Report — project evaluation" data-te="మోడల్ నివేదిక — ప్రాజెక్ట్ మూల్యాంకనం">Model Report — project evaluation</a><p>The local server processes questions in memory. Offline mode keeps questions in this browser. See the report for measured results and dataset limitations.</p></section>')
        path.write_text(s,encoding='utf8')
    s=(ROOT/'js/app.js').read_text(encoding='utf8')
    s=s.replace("$('ask-form').addEventListener('submit',event=>{","$('ask-form').addEventListener('submit',async event=>{")
    s=s.replace("status('ask-status','');const answer=window.AgriClassifier.classify(query);remember(query);", """status('ask-status','');let answer;
      if(location.protocol!=='file:'){
        const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),2500);
        try{const response=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query}),signal:controller.signal});if(!response.ok)throw new Error('API unavailable');answer=await response.json();}catch(_){answer=window.AgriClassifier.classify(query);}finally{clearTimeout(timer);}
      }else answer=window.AgriClassifier.classify(query);
      remember(query);""")
    s=s.replace("if(!answer.intent){reveal('home-result'", "if(!answer.intent||answer.clarify||!D.topics[answer.intent]){reveal('home-result'")
    s=s.replace("${esc(cropName(answer.crop))}</span></div>","${esc(cropName(answer.crop))}</span><span class=\"badge\">${answer.confidence>=.8?dual('Clear topic','విషయం స్పష్టంగా ఉంది'):dual('Likely topic — please check','బహుశా ఈ విషయం — సరిచూడండి')}</span></div>")
    s=s.replace('const ref=D.nutrients[crop];','const base=D.nutrients[crop];\n    const manual=[\'manual-n\',\'manual-p\',\'manual-k\'].map(id=>$(id)?.value);\n    const ref=manual.every(v=>v!==undefined&&v!==\'\')?{...base,profiles:[manual.map(Number)],basalN:1,basalK:1,vegN:0,vegK:0}:base;')
    anchor="status('fert-status','');const per=fertilizerPlan(key,1)"
    if anchor in s:
        s=s.replace(anchor,"""status('fert-status','');
      const manual=['manual-n','manual-p','manual-k'].map(id=>$(id)?.value);
      if(!D.nutrients[key].profiles.length&&!manual.every(v=>v!==undefined&&v!=='')){
        reveal('fert-result',`${title('Ask for a soil-test-based plan','భూసార పరీక్ష ఆధారిత సలహా పొందండి')}<p>${esc(cropName(key))}</p><p>${dual('Consult your agriculture officer. No numerical fertilizer dose has been verified for this crop here. If you have an officer’s N:P2O5:K2O recommendation, enter it above to convert it into product equivalents.','మీ వ్యవసాయ అధికారిని సంప్రదించండి. ఈ పంటకు ఎరువుల మోతాదు ఇక్కడ నిర్ధారించలేదు. అధికారి ఇచ్చిన మోతాదును పై పెట్టెల్లో నమోదు చేయండి.')}</p><p><a href="${D.nutrients[key].source}" target="_blank" rel="noopener">${esc(D.nutrients[key].sourceName)}</a></p>${end()}`);return;
      }
      const per=fertilizerPlan(key,1)""")
    s=s.replace('Crop nutrient reference: TNAU Agritech ↗','${esc(D.nutrients[key].sourceName)}')
    # Replace unsupported water schedule arithmetic with exact user-depth unit conversion.
    start=s.index('  function waterPlan(');stop=s.index('  function setupIrrigation()',start)
    s=s[:start]+'''  function waterPlan(crop,soil,season,depth=10) {
    if(!Number.isFinite(depth)||depth<0)throw new Error('Invalid depth');
    return {litres:depth*4046.8564224,depth};
  }
'''+s[stop:]
    start=s.index("    $('irrigation-form').addEventListener");stop=s.index('\n  function profit(',start)
    s=s[:start]+'''    $('irrigation-form').addEventListener('submit',event=>{
      event.preventDefault();const key=$('water-crop').value,depth=Number($('water-depth').value),soil=$('soil').value,season=$('season').value;
      if(!Number.isFinite(depth)||depth<0||depth>1000)return;
      const plan=waterPlan(key,soil,season,depth),c=D.crops[key];
      reveal('water-result',`${title('Your water planning guide','మీ నీటి ప్రణాళిక')}<p><strong>${esc(cropName(key))}</strong></p><p>${dual('Consult your agriculture officer for the irrigation interval and depth. No crop-specific interval is inferred here.','నీరు ఇచ్చే సమయం, మోతాదు కోసం మీ వ్యవసాయ అధికారిని సంప్రదించండి.')}</p><div class="stats"><div class="stat"><strong>${number(plan.litres)} L</strong><span>${dual('Net litres per acre for your entered depth','మీరు నమోదు చేసిన లోతుకు ఎకరానికి నీటి లీటర్లు')}</span></div><div class="stat"><strong>${number(depth)} mm</strong><span>${dual('Your chosen depth, not a recommended dose','మీరు ఎంచుకున్న లోతు; సిఫార్సు కాదు')}</span></div></div><p>${esc(c.tip)}</p><p>${esc(D.water.seasonal[season])}</p><p><a href="${c.waterSource}" target="_blank" rel="noopener">ICAR — soil-moisture scheduling guidance (general)</a></p>${key==='brinjal'?'<p>TNAU brinjal reference: weekly intervals after seedling establishment; local soil and rainfall may change this. <a href="https://agritech.tnau.ac.in/horticulture/horti_vegetables_brinjal_irrigation.html">TNAU Agritech — brinjal irrigation</a></p>':''}${printButton('water-result')}${end()}`);
    });
  }
'''+s[stop:]
    s=s.replace('${money(p.sample)}<br>','${p.sample===null?\'No sample rate\':money(p.sample)}<br>')
    s=s.replace("${p.msp===null?'Not listed':money(p.msp)}","${p.msp===null?'Consult your officer':money(p.msp)}")
    s=s.replace('${esc(p.season)}</td>','${esc(p.season)}<br><a href="${p.source}" target="_blank" rel="noopener">PIB historical reference</a></td>')
    # Label both original disease cards and general inspection cues honestly.
    s=s.replace('${esc(c.en)} / ${esc(c.te)}</span>${title(\'Signs', '${esc(c.en)} / ${esc(c.te)}</span><p class="fine">Reference: TNAU Agritech crop protection; symptoms need field confirmation. For unverified crop-specific problems, consult your agriculture officer.</p>${title(\'Signs')
    (ROOT/'js/app.js').write_text(s,encoding='utf8')
    f=ROOT/'fertilizer.html';s=f.read_text(encoding='utf8')
    if 'manual-n' not in s:
        inputs=''.join(f'<div><label for="manual-{i}">{label} kg/ha</label><input id="manual-{i}" type="number" min="0" max="1000" step="0.1" placeholder="Officer-provided value"></div>' for i,label in [('n','N'),('p','P2O5'),('k','K2O')])
        s=s.replace('<button class="button" type="submit">Calculate quantities</button>', '<fieldset><legend data-en="Optional: enter all three nutrient amounts from your agriculture officer" data-te="ఐచ్ఛికం: అధికారి సూచించిన మూడు పోషక మోతాదులు నమోదు చేయండి">Optional: enter all three nutrient amounts from your agriculture officer</legend><div class="form-grid">'+inputs+'</div><p>These are your inputs, not a crop recommendation. Leave blank to see a verified reference where available.</p></fieldset><button class="button" type="submit">Calculate quantities</button>')
    f.write_text(s,encoding='utf8')
    f=ROOT/'irrigation.html';s=f.read_text(encoding='utf8')
    if 'water-depth' not in s:s=s.replace('<button class="button" type="submit">Show water plan</button>','<label for="water-depth" data-en="Your chosen net water depth (mm), for unit conversion only" data-te="మీరు ఎంచుకున్న నీటి లోతు (మి.మీ.), లీటర్ల లెక్క కోసం మాత్రమే">Your chosen net water depth (mm), for unit conversion only</label><input id="water-depth" type="number" min="0" max="1000" step="0.1" value="10" required><p>10 mm is an example input, not an irrigation recommendation.</p><button class="button" type="submit">Show water plan</button>')
    f.write_text(s,encoding='utf8')

if __name__=='__main__':update()
