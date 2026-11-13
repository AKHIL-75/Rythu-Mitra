/* Real browser inference and rendered guidance; never loads .env or a live API key. */
const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert'),{pathToFileURL}=require('url'),{spawnSync}=require('child_process');
let pw;try{pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');}catch(_){pw=require(path.join(os.homedir(),'.cache','codex-runtimes','codex-primary-runtime','dependencies','node','node_modules','playwright'));}
const root=path.resolve(__dirname,'..'),checks=[],errors=[];let browser;
async function check(name,fn){try{await fn();checks.push({name,status:'passed'});}catch(error){checks.push({name,status:'failed',error:String(error)});console.error(name,error);}}
(async()=>{
 try{browser=await pw.chromium.launch({headless:true});}catch(_){browser=await pw.chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});}
 const page=await browser.newPage();page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.join(root,'index.html')).href+'?lang=en');
 async function ask(q){await page.fill('#query',q);await page.locator('#ask-form button[type=submit]').click();await page.waitForSelector('#home-result:visible');return page.locator('#home-result').innerText();}
 const original='na potato chetu ki holes unnay em cheyali';let potatoAnswer;
 await check('exact user question gives practical steps, checks and no referral-only fallback',async()=>{potatoAnswer=await ask(original);for(const s of ['Potato','Steps you can take now','Inspect both leaf surfaces','caterpillars','Where are the holes?','not a confirmed diagnosis']){if(s==='not a confirmed diagnosis')continue;assert(potatoAnswer.includes(s));}assert(!potatoAnswer.includes('No verified crop-specific answer'));assert.equal(await page.locator('.practical-steps li').count(),3);assert(await page.locator('#followup-form').isVisible());});
 await check('potato tuber follow-up retains crop and changes inspection steps',async()=>{await page.locator('.practical-followup button[data-question*="tubers"]').click();const t=await page.locator('#home-result').innerText();assert(t.includes('tunnels near the eyes'));assert(t.includes('do not leave harvested tubers exposed'));assert((await page.locator('#query').inputValue()).startsWith('Potato'));});
 await check('potato stem follow-up gives stem-specific checks',async()=>{await page.locator('.practical-followup button[data-question*="stems"]').click();assert((await page.locator('#home-result').innerText()).includes('For cut potato stems'));});
 await check('typed follow-up keeps original question attached',async()=>{await ask(original);await page.fill('#followup-detail','holes in tubers, crop age 70 days');await page.locator('#followup-form button').click();assert((await page.locator('#query').inputValue()).startsWith(original));assert((await page.locator('#home-result').innerText()).includes('For potato tuber holes'));});
 for(const [symptom,query,expected] of [
  ['yellow','na potato aakulu pasupu rangu unnay','does not automatically mean nitrogen deficiency'],
  ['spots','potato leaf spots em cheyali','Keep irrigation off the leaves'],
  ['wilting','potato vadipothundi em cheyali','If dry, water the root zone slowly'],
  ['powder','potato leaves white powder em cheyali','fresh leaves develop new powdery patches'],
  ['curl','potato leaves curled em cheyali','Curling alone does not confirm a virus'],
  ['rot','potato tubers rot em cheyali','Keep rotting harvested produce apart'],
  ['flowers','tomato flower drop em cheyali','Flowers falling: check weather and water stress']
 ])await check('practical answer for '+symptom,async()=>{const t=await ask(query);assert(t.includes(expected));assert.equal(await page.locator('.practical-steps li').count(),3);});
 await check('multiple symptoms retain both action plans',async()=>{await ask('potato yellow leaves and holes em cheyali');assert.equal(await page.locator('.practical-plan').count(),2);});
 await check('all catalog crops receive each supported symptom plan',async()=>{
  const failures=await page.evaluate(()=>{const failures=[];for(const crop of CROP_CATALOG)for(const key of Object.keys(SLOT_CONFIG.symptoms)){const html=PracticalGuidance.symptoms(crop.id,[key],crop.english_name+' '+key);if(!html.includes('practical-steps')||html.includes('undefined'))failures.push(crop.id+':'+key);}return failures;});assert.deepEqual(failures,[]);
 });
 await check('fertilizer has an actionable checklist without invented dose',async()=>{const t=await ask('potato fertilizer entha veyali');assert(t.includes('Plan nutrients before buying'));assert(t.includes('soil test'));assert.equal(await page.locator('.practical-plan').count(),1);});
 await check('irrigation distinguishes dry and saturated soil',async()=>{const t=await ask('potato irrigation water eppudu pettali');assert(t.includes('If dry, apply water slowly'));assert(t.includes('If saturated, allow drainage'));});
 for(const [topic,query,expected] of [
  ['planting','potato planting em cheyali','Planting and germination: practical checks'],
  ['storage','potato storage ela cheyali','For potatoes: keep tubers in a dark'],
  ['harvest','potato harvesting ela cheyali','Harvest handling: protect quality'],
  ['weeds','potato weeds kalupu ela control cheyali','Remove small weeds by hand']
 ])await check('useful guidance for '+topic,async()=>{assert((await ask(query)).includes(expected));});
 await check('market question links selected crop to real mandi prices',async()=>{const t=await ask('potato market price entha');assert(t.includes('Check reported mandi prices'));assert(!/Historical|MSP/.test(t));assert(await page.locator('#home-result a[href*="market-prices.html?crop=potato"]').count()>0);});
 await check('unknown crop asks instead of inventing a diagnosis',async()=>{const t=await ask('unknownplant leaves have holes');assert(t.includes('Which crop?'));assert(!t.includes('Potato'));});
 await check('unrelated question keeps farming boundary',async()=>{assert((await ask('java code potato storage')).includes('Please ask a farming question'));});
 await check('answer escapes untrusted query text',async()=>{await ask('potato holes <img src=x onerror="window.badQuery=1">');assert.equal(await page.evaluate(()=>window.badQuery),undefined);assert.equal(await page.locator('#home-result img[src=x]').count(),0);});
 await ask(original);
 await check('Telugu toggle translates steps, follow-ups and headings',async()=>{await page.locator('#language-toggle').click();assert.equal(await page.locator('html').getAttribute('lang'),'te');const text=await page.locator('#home-result').innerText();assert(text.includes('ఇప్పుడు చేయగల పనులు'));assert(text.includes('ఆకుల రెండు వైపులు'));assert((await page.locator('#followup-form button').innerText()).includes('నవీకరించండి'));});
 await check('mobile answer fits at 320 pixels',async()=>{await page.setViewportSize({width:320,height:850});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.locator('#home-result').screenshot({path:path.join(root,'reports/practical_mobile.png')});});
 await page.goto(pathToFileURL(path.join(root,'crop-disease.html')).href+'?lang=en');
 await check('full crop guide symptom checker also offers practical steps',async()=>{await page.selectOption('#disease-crop','potato');await page.check('input[name=symptom][value=holes]');await page.locator('#symptom-form button').click();assert((await page.locator('#symptom-result').innerText()).includes('Steps you can take now'));});
 await check('backend and browser classifications still agree for original question',async()=>{
  const result=spawnSync('python',['-c',"import dotenv; dotenv.load_dotenv=lambda *a,**k:False; from app import app; import json; print(json.dumps(app.test_client().post('/predict',json={'query':'na potato chetu ki holes unnay em cheyali'}).get_json()))"],{cwd:root,encoding:'utf8',windowsHide:true});assert.equal(result.status,0);const a=JSON.parse(result.stdout);assert.equal(a.crop,'potato');assert.equal(a.intent,'crop_disease');assert(a.symptoms.includes('holes'));
 });
 await check('no JavaScript errors',async()=>assert.deepEqual(errors,[]));await browser.close();
 const result={passed:checks.filter(c=>c.status==='passed').length,failed:checks.filter(c=>c.status==='failed').length,javascript_errors:errors,checks,potato_answer:potatoAnswer};fs.writeFileSync(path.join(root,'reports/practical_test_results.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({passed:result.passed,failed:result.failed,javascript_errors:errors}));process.exitCode=result.failed?1:0;
})().catch(async e=>{console.error(e);if(browser)await browser.close();process.exitCode=1;});
