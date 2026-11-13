/* Run node tests/frontend.cjs. Uses Playwright and actual file:// + Flask pages. */
const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert');
const {pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..');
let pw;
try{pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');}catch(_){pw=require(path.join(os.homedir(),'.cache','codex-runtimes','codex-primary-runtime','dependencies','node','node_modules','playwright'));}
const crops=JSON.parse(fs.readFileSync(path.join(root,'data/crops.json'),'utf8'));
const summary={passed:0,failed:0,checks:[],console_errors:[]};
const useWSGI=process.env.NLP_BROWSER_WSGI==='1';
summary.transport=useWSGI?'Flask WSGI over stdio (sandbox blocks local TCP)':'HTTP over local TCP';
let bridge,bridgeCall;
if(useWSGI){
 const {spawn}=require('child_process'),readline=require('readline');
 bridge=spawn(process.env.NLP_PYTHON||'python',[path.join(root,'tests/wsgi_bridge.py')],{cwd:root,stdio:['pipe','pipe','inherit'],windowsHide:true});
 let serial=0;const pending=new Map();
 readline.createInterface({input:bridge.stdout}).on('line',line=>{try{const r=JSON.parse(line),p=pending.get(r.id);if(p){pending.delete(r.id);r.error?p.reject(Error(r.error)):p.resolve(r);}}catch(e){console.error('Bridge response',e);}});
 bridge.on('exit',code=>{for(const p of pending.values())p.reject(Error('WSGI bridge exited '+code));pending.clear();});
 bridgeCall=(request)=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});bridge.stdin.write(JSON.stringify({id,...request})+'\n');});
}
async function check(name,fn){try{await fn();summary.passed++;summary.checks.push({name,status:'passed'});}catch(e){summary.failed++;summary.checks.push({name,status:'failed',error:String(e)});console.error(name,e);}}
const weather={daily:{time:Array.from({length:7},(_,i)=>`2026-11-${String(13+i).padStart(2,'0')}`),weather_code:[2,61,3,0,0,1,1],temperature_2m_max:[36,31,32,33,34,32,31],temperature_2m_min:[23,22,22,22,23,22,21],precipitation_sum:[0,40,0,0,0,0,0],wind_speed_10m_max:[10,28,11,10,10,8,9]}};
(async()=>{
 let browser;
 try{browser=await pw.chromium.launch({headless:true});}catch(_){browser=await pw.chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});}
 const context=await browser.newContext();
 if(useWSGI)await context.route('http://rythu-mitra.test/**',async route=>{
   const request=route.request(),url=new URL(request.url());
   const response=await bridgeCall({path:url.pathname+url.search,method:request.method(),body:request.postData(),content_type:request.headers()['content-type']});
   await route.fulfill({status:response.status,contentType:response.content_type,body:Buffer.from(response.body,'base64')});
 });
 await context.route('https://api.open-meteo.com/**',route=>route.fulfill({json:weather}));
 await context.route('https://geocoding-api.open-meteo.com/**',route=>route.fulfill({json:{results:[{country_code:'IN',name:'Nizamabad',admin1:'Telangana',latitude:18.67,longitude:78.09}]}}));
 const page=await context.newPage();
 page.on('pageerror',e=>summary.console_errors.push(String(e)));
 page.on('console',msg=>{if(msg.type()==='error'&&!/Failed to load resource|net::ERR/.test(msg.text()))summary.console_errors.push(msg.text());});
 const file=name=>pathToFileURL(path.join(root,name)).href;
 const pages=fs.readdirSync(root).filter(f=>f.endsWith('.html'));
 for(const name of pages){
  await check('page and Telugu toggle: '+name,async()=>{
   await page.goto(file(name)+'?lang=en');await page.waitForSelector('#language-toggle');
   assert.equal(await page.locator('html').getAttribute('lang'),'en');
   await page.locator('#language-toggle').click();assert.equal(await page.locator('html').getAttribute('lang'),'te');
   assert.match(await page.locator('#site-header').innerText(),/[\u0c00-\u0c7f]/);
   await page.locator('#language-toggle').click();assert.equal(await page.locator('html').getAttribute('lang'),'en');
   const text=await page.locator('body').innerText();assert(!/undefined|\bNaN\b/.test(text));
   for(const select of await page.locator('.crop-select').all()){
    assert.equal(await select.locator('option').count(),crops.length);
    const options=await select.locator('option').evaluateAll(x=>x.map(o=>o.value));
    assert.deepEqual(options.sort(),crops.map(c=>c.id).sort());
   }
  });
 }
 await page.goto(file('fertilizer.html')+'?lang=en');
 for(const c of crops)await check('fertilizer crop '+c.id,async()=>{
   await page.selectOption('#fert-crop',c.id);await page.locator('#fertilizer-form button[type=submit]').click();
   const text=await page.locator('#fert-result').innerText();assert(text.includes(c.english_name));assert(!/undefined|\bNaN\b/.test(text));
 });
 // Every crop accepts an explicitly officer-provided nutrient plan and scales by acreage.
 await page.fill('#manual-n','100');await page.fill('#manual-p','50');await page.fill('#manual-k','60');
 for(const c of crops)await check('officer input conversion '+c.id,async()=>{
   await page.selectOption('#fert-crop',c.id);await page.locator('#fertilizer-form button[type=submit]').click();
   assert(await page.locator('#fert-result table').count()>=2);
   assert(!/undefined|\bNaN\b/.test(await page.locator('#fert-result').innerText()));
 });
 await check('fertilizer nutrient accounting and area scaling',async()=>{
   const p=await page.evaluate(()=>({one:AgriTools.fertilizerPlan('paddy',1),two:AgriTools.fertilizerPlan('paddy',2)}));
   p.one.forEach((a,i)=>{for(let k=0;k<3;k++){assert(Math.abs(p.two[i].total[k]-2*a.total[k])<1e-8);assert(Math.abs(a.rows.reduce((s,r)=>s+r[k],0)-a.total[k])<1e-8);}});
 });
 await page.goto(file('irrigation.html')+'?lang=en');
 for(const c of crops)await check('irrigation crop '+c.id,async()=>{
   await page.selectOption('#water-crop',c.id);await page.locator('#irrigation-form button[type=submit]').click();
   const text=await page.locator('#water-result').innerText();assert(text.includes(c.english_name));assert(!/undefined|\bNaN\b/.test(text));
   assert.match(text,/40,468/);
 });
 await page.goto(file('crop-disease.html')+'?lang=en');
 for(const c of crops)await check('health crop '+c.id,async()=>{
   await page.selectOption('#disease-crop',c.id);assert.equal(await page.locator('#disease-cards .card').count(),3);
   assert(!/undefined|\bNaN\b/.test(await page.locator('#disease-cards').innerText()));
 });
 await check('symptom checker',async()=>{
   await page.locator('input[value=spots]').check();await page.locator('#symptom-form button[type=submit]').click();assert((await page.locator('#symptom-result').innerText()).length>50);
 });
 await page.goto(file('market-prices.html')+'?lang=en');
 for(const c of crops)await check('price coverage '+c.id,async()=>{
   await page.selectOption('#live-commodity',c.english_name);assert.equal(await page.locator('#live-commodity').inputValue(),c.english_name);
 });
 await check('profit calculator',async()=>{
   await page.fill('#yield','20');await page.fill('#sale-price','2450');await page.fill('#cost','30000');await page.locator('#profit-form button[type=submit]').click();assert.match(await page.locator('#profit-result').innerText(),/19,000/);
   await page.fill('#yield','0');await page.fill('#sale-price','0');await page.fill('#cost','0');await page.locator('#profit-form button[type=submit]').click();assert.match(await page.locator('#profit-result').innerText(),/Break-even/);
 });
 await page.goto(file('weather.html')+'?lang=en');
 await check('forecast, advice and all districts',async()=>{
   await page.waitForSelector('#weather-result:not([hidden])');assert.equal(await page.locator('.day').count(),7);
   assert.equal(await page.locator('#district-list option').count(),61);
   const text=await page.locator('#weather-result').innerText();assert.match(text,/delay|Delay/);assert.match(text,/wind|Wind/);
   await page.selectOption('#city','district:Nizamabad');await page.locator('#weather-submit').click();await page.waitForFunction(()=>document.getElementById('weather-result').textContent.includes('Nizamabad'));
 });
 await check('forecast network error',async()=>{
   await context.unroute('https://api.open-meteo.com/**');await context.route('https://api.open-meteo.com/**',r=>r.abort());
   await page.locator('#weather-submit').click();await page.waitForFunction(()=>document.getElementById('weather-status').textContent.includes('could not load'));assert(await page.locator('#weather-result').isHidden());
 });
 await page.goto(file('govt-schemes.html')+'?lang=en');
 await check('scheme enquiry checker',async()=>{
   await page.locator('#eligibility-form button[type=submit]').click();assert((await page.locator('#eligibility-result').innerText()).length>100);
 });
 await page.goto(file('index.html')+'?lang=en');
 const regression=fs.readFileSync(path.join(root,'data/symptom_regression.csv'),'utf8').trim().split(/\r?\n/).slice(1).map(line=>{const [query,crop,symptom,intent]=line.split(',');return {query,crop,symptom,intent};});
 for(const c of regression)await check('direct answer and prefilled guide: '+c.query,async()=>{
   await page.goto(file('index.html')+'?lang=en');await page.fill('#query',c.query);await page.locator('#ask-form button[type=submit]').click();
   const crop=crops.find(x=>x.id===c.crop);assert((await page.locator('#home-result .detected-crop').innerText()).includes(crop.english_name));
   if(c.symptom){assert(await page.locator('#home-result [data-symptom="'+c.symptom+'"]').isVisible());const text=await page.locator('#home-result').innerText();assert(await page.locator('#home-result article').count()>0||text.includes('No verified crop-specific answer'));assert(text.includes('1800-180-1551'));}
   const target=await page.locator('#home-result .full-guide').getAttribute('href');await Promise.all([page.waitForURL(u=>u.pathname.endsWith(target.split('?')[0])),page.locator('#home-result .full-guide').click()]);await page.waitForLoadState('load');await page.waitForSelector('body[data-ready="1"]');
   if(c.intent==='crop_disease'){assert.equal(await page.locator('#disease-crop').inputValue(),c.crop);assert(await page.locator('input[name=symptom][value="'+c.symptom+'"]').isChecked());assert((await page.locator('#symptom-result').innerText()).length>40);}
   else{assert.equal(await page.locator('#water-crop').inputValue(),c.crop);assert(await page.locator('#water-result').isVisible());}
 });
 await check('fertilizer stage passed and result auto shown',async()=>{
   await page.goto(file('index.html')+'?lang=en');await page.fill('#query','patti flowering time urea eruvu mothadu enti');await page.locator('#ask-form button[type=submit]').click();await Promise.all([page.waitForURL(u=>u.pathname.endsWith('fertilizer.html')),page.locator('#home-result .full-guide').click()]);await page.waitForLoadState('load');await page.waitForSelector('body[data-ready="1"]');assert.equal(await page.locator('#fert-stage').inputValue(),'reproductive');assert(await page.locator('#fert-result').isVisible());
 });
 await check('crop and symptom tap clarification',async()=>{
   await page.goto(file('index.html')+'?lang=en');await page.fill('#query','yellow leaves');await page.locator('#ask-form button[type=submit]').click();assert.match(await page.locator('#home-result').innerText(),/Which crop/);await page.locator('#home-result button[data-question]').first().click();assert.match(await page.locator('#home-result').innerText(),/Paddy/);
 });
 await check('home weather and location prefilled guide',async()=>{
   await context.unroute('https://api.open-meteo.com/**');await context.route('https://api.open-meteo.com/**',r=>r.fulfill({json:weather}));
   await page.goto(file('index.html')+'?lang=en');await page.fill('#query','Warangal weather forecast for paddy');await page.locator('#ask-form button[type=submit]').click();
   await page.waitForFunction(()=>document.getElementById('home-weather-live')?.textContent.includes('Open-Meteo forecast'));
   await Promise.all([page.waitForURL(u=>u.pathname.endsWith('weather.html')),page.locator('#home-result .full-guide').click()]);await page.waitForLoadState('load');assert.equal(await page.locator('#custom-city').inputValue(),'Warangal');await page.waitForSelector('#weather-result:not([hidden])');
 });
 await check('speak removed and speech error compatibility messages',async()=>{
   await page.goto(file('index.html')+'?lang=en');
   assert.equal(await page.locator('#voice-btn').count(),0);
   for(const code of ['not-allowed','service-not-allowed','audio-capture','no-speech','network','aborted','language-not-supported','bad-grammar','unknown']){
     await page.evaluate(code=>VoiceErrors.render(code,document.getElementById('ask-status')),code);assert.match(await page.locator('#ask-status').innerText(),/type your farming question/);
   }
 });
 await check('no fictional price column or missing sample text',async()=>{
   await page.goto(file('market-prices.html')+'?lang=en');const text=await page.locator('body').innerText();assert(!/No sample rate|Sample mandi price/.test(text));await page.locator('#live-price-form button').click();assert.match(await page.locator('#live-price-status').innerText(),/local server/);
 });
 await page.goto(file('index.html')+'?lang=en');
 await check('problem model Python/browser parity',async()=>{
   const cases=JSON.parse(fs.readFileSync(path.join(root,'reports/problem_parity_cases.json'),'utf8'));
   const results=await page.evaluate(cases=>cases.map(c=>AgriClassifier.problem(c.query,c.intent)),cases);
   cases.forEach((c,i)=>{assert.equal(results[i].label,c.label);assert(Math.abs(results[i].confidence-c.confidence)<1e-6);});
 });
 await check('all crop alias JS twin parity',async()=>{
   const cases=crops.flatMap(c=>[c.english_name,...c.english_aliases,...c.romanized_aliases,...c.telugu_aliases].flatMap(a=>[[a,c.id==='turmeric'&&a.toLowerCase()!=='turmeric'?null:c.id],[a+' ki',c.id],[a+' lo',c.id]]));
   const bad=await page.evaluate(cases=>cases.filter(([q,id])=>CropEntities.detectCrop(q)!==id),cases);assert.deepEqual(bad,[]);
 });
 await check('exact Python to browser prediction probability parity',async()=>{
   const cases=JSON.parse(fs.readFileSync(path.join(root,'reports/export_parity_cases.json'),'utf8'));
   const results=await page.evaluate(cases=>cases.map(c=>AgriClassifier.raw(c.query)),cases);
   for(let i=0;i<cases.length;i++){assert.equal(results[i].intent,cases[i].intent,cases[i].query);for(let j=0;j<cases[i].probabilities.length;j++)assert(Math.abs(results[i].probabilities[j]-cases[i].probabilities[j])<1e-6,cases[i].query);}
 });
 await check('home offline answer, history limit, reuse and clear',async()=>{
   for(const q of ['tomato leaf spot disease','paddy urea fertilizer','cotton drip irrigation','onion market price','weather rain forecast','PM KISAN government scheme']){
    await page.fill('#query',q);await page.locator('#ask-form button[type=submit]').click();assert(await page.locator('#home-result').isVisible());
   }
   assert.equal(await page.locator('#history-list button').count(),5);await page.locator('#history-list button').first().click();assert.match(await page.locator('#query').inputValue(),/PM KISAN/);
   await page.locator('#clear-history').click();assert.equal(await page.locator('#history-list button').count(),0);assert(await page.locator('#clear-history').isDisabled());
 });
 await check('empty and unrelated questions clarify',async()=>{
   await page.fill('#query','');await page.locator('#ask-form button[type=submit]').click();assert.match(await page.locator('#ask-status').innerText(),/type a question/);
   await page.fill('#query','qzxwvvv jjjqqqzz');await page.locator('#ask-form button[type=submit]').click();assert.match(await page.locator('#home-result').innerText(),/Please ask a farming question/);
 });
 await check('examiner demo',async()=>{
   await page.goto(file('model-report.html')+'?lang=en');await page.locator('#demo-form button').click();assert.match(await page.locator('#demo-result').innerText(),/crop_disease/);assert.equal(await page.locator('#comparison tbody tr').count(),9);
 });
 await check('confusion matrix image assets',async()=>{
   const metrics=JSON.parse(fs.readFileSync(path.join(root,'ml/models/metrics.json'),'utf8'));
   for(const row of metrics.comparison){if(useWSGI){const r=await bridgeCall({path:'/reports/'+row.key+'_confusion.png'});assert.equal(r.status,200);assert(Buffer.from(r.body,'base64').length>1000);}else{const response=await context.request.get('http://127.0.0.1:5000/reports/'+row.key+'_confusion.png');assert.equal(response.status(),200);assert((await response.body()).length>1000);}}
 });
 await check('Flask backend home prediction',async()=>{
   await page.goto((useWSGI?'http://rythu-mitra.test':'http://127.0.0.1:5000')+'/?lang=en');await page.fill('#query','tomato leaf spot disease');
   const response=page.waitForResponse(r=>r.url().endsWith('/predict')&&r.request().method()==='POST');await page.locator('#ask-form button[type=submit]').click();assert.equal((await response).status(),200);await page.waitForSelector('#home-result:not([hidden])');
 });
 await check('backend slots and offline slots agree',async()=>{
   for(const c of regression.slice(0,3)){
     const offline=await page.evaluate(q=>AgriClassifier.classify(q),c.query);
     let response;if(useWSGI){const r=await bridgeCall({path:'/predict',method:'POST',body:JSON.stringify({query:c.query}),content_type:'application/json'});response=JSON.parse(Buffer.from(r.body,'base64').toString('utf8'));}else{response=await (await context.request.post('http://127.0.0.1:5000/predict',{data:{query:c.query}})).json();}
     assert.equal(response.crop,offline.crop);assert.deepEqual(response.symptoms,offline.symptoms);assert.equal(response.intent,offline.intent);
   }
 });
 await check('prices no-key API message renders',async()=>{
   await page.goto((useWSGI?'http://rythu-mitra.test':'http://127.0.0.1:5000')+'/market-prices.html?lang=en');await page.locator('#live-price-form button').click();await page.waitForFunction(()=>document.getElementById('live-price-status').textContent.includes('not configured')||document.getElementById('live-price-status').textContent.includes('could not'));assert(!/No sample rate/.test(await page.locator('body').innerText()));
 });
 await page.goto((useWSGI?'http://rythu-mitra.test':'http://127.0.0.1:5000')+'/?lang=en');
 await check('API outage falls back to local model',async()=>{
   await page.route('**/predict',r=>r.abort());await page.fill('#query','cotton drip irrigation');await page.locator('#ask-form button[type=submit]').click();await page.waitForFunction(()=>document.getElementById('home-result').textContent.includes('Water planner'));
 });
 await check('no JavaScript page errors',async()=>assert.deepEqual(summary.console_errors,[]));
 await browser.close();
 if(bridge)bridge.stdin.end();
 fs.writeFileSync(path.join(root,'reports/frontend_results.json'),JSON.stringify(summary,null,2));
 console.log(JSON.stringify({passed:summary.passed,failed:summary.failed,console_errors:summary.console_errors}));
 process.exitCode=summary.failed?1:0;
})().catch(e=>{if(bridge)bridge.stdin.end();summary.failed++;summary.checks.push({name:'runner',status:'failed',error:String(e)});fs.writeFileSync(path.join(root,'reports/frontend_results.json'),JSON.stringify(summary,null,2));console.error(e);process.exitCode=1;});
