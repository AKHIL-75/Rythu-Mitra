/* Deterministic browser tests: explicit API fixtures, real saved metrics, no .env access. */
const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert');
let pw;try{pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');}catch(_){pw=require(path.join(os.homedir(),'.cache','codex-runtimes','codex-primary-runtime','dependencies','node','node_modules','playwright'));}
const root=path.resolve(__dirname,'..'),metrics=JSON.parse(fs.readFileSync(path.join(root,'ml/models/metrics.json'),'utf8'));
const checks=[],errors=[];let browser;
async function check(name,fn){try{await fn();checks.push({name,status:'passed'});}catch(e){checks.push({name,status:'failed',error:String(e)});console.error(name,e);}}
const base={state:'Telangana',district:'Warangal',market:'Fixture market A',commodity:'Paddy',variety:'Fixture variety',grade:'FAQ',arrival_date:'12/11/2026',modal_price:'2300',min_price:'2200',max_price:'2400'};
const records=[base,{...base,market:'Fixture market B',modal_price:'2450'}];
const good=rows=>({status:'ok',records:rows,unit:'INR per quintal (as published by the mandi resource)',message:'Fixture reported prices',fetched_at:'TEST ONLY',cached:false});
const forecast={daily:{time:Array.from({length:7},(_,i)=>`2026-11-${13+i}`),weather_code:[0,1,2,61,0,0,1],temperature_2m_max:[32,33,31,29,30,32,34],temperature_2m_min:[20,21,19,18,19,20,21],precipitation_sum:[0,0,1,36,0,0,2],wind_speed_10m_max:[5,6,12,20,10,8,7]}};
(async()=>{
 try{browser=await pw.chromium.launch({headless:true});}catch(_){browser=await pw.chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});}
 const context=await browser.newContext();let pricePayload=good(records),priceStatus=200,weatherPayload=forecast,weatherStatus=200,holdPrice=null;
 await context.route('http://rythu-charts.test/**',async route=>{
  const u=new URL(route.request().url());
  if(u.pathname==='/prices'){if(holdPrice)await holdPrice;return route.fulfill({status:priceStatus,json:pricePayload});}
  const local=path.resolve(root,'.'+decodeURIComponent(u.pathname));
  if(!local.startsWith(root+path.sep)||!fs.existsSync(local))return route.fulfill({status:404,body:''});
  const contentType=local.endsWith('.js')?'application/javascript':local.endsWith('.css')?'text/css':local.endsWith('.json')?'application/json':local.endsWith('.png')?'image/png':'text/html';
  return route.fulfill({contentType,body:fs.readFileSync(local)});
 });
 await context.route('https://api.open-meteo.com/**',r=>r.fulfill({status:weatherStatus,json:weatherPayload}));
 await context.route('https://geocoding-api.open-meteo.com/**',r=>r.fulfill({json:{results:[{country_code:'IN',name:'Nizamabad',admin1:'Telangana',latitude:18.67,longitude:78.09}]}}));
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 const goto=name=>page.goto('http://rythu-charts.test/'+name+'?lang=en');
 const noOverflow=async()=>assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 const toggle=async lang=>{if(await page.locator('html').getAttribute('lang')!==lang)await page.locator('#language-toggle').click();await page.waitForTimeout(30);};
 async function priceRequest(payload,status=200){pricePayload=payload;priceStatus=status;await page.locator('#live-price-form button').click();await page.waitForFunction(()=>!document.querySelector('#live-price-form button').disabled);}
 await goto('model-report.html');await page.waitForSelector('#model-charts svg');
 await check('default authored benchmark: all nine exact metric pairs',async()=>{
  assert.equal(await page.locator('#chart-benchmark').inputValue(),'authored');
  const rows=await page.locator('#model-charts tbody tr').allTextContents();assert.equal(rows.length,9);
  for(let i=0;i<9;i++){const r=metrics.comparison[i],actual=metrics.robustness.raw_models.find(x=>x.experiment===r.key);assert(rows[i].includes(r.model+' / '+r.features));assert(rows[i].includes(String(actual.accuracy)));assert(rows[i].includes(String(actual.macro_f1)));}
  assert.equal(await page.locator('#model-charts rect').count(),18);
 });
 await check('secondary workbook switch uses exact saved test results',async()=>{
  await page.selectOption('#chart-benchmark','workbook');const rows=await page.locator('#model-charts tbody tr').allTextContents();for(let i=0;i<9;i++){assert(rows[i].includes(String(metrics.comparison[i].test_accuracy)));assert(rows[i].includes(String(metrics.comparison[i].test_macro_f1)));}
 });
 await check('generalization counts, separate cross-script protocol and rules',async()=>{
  const figures=page.locator('#generalization-charts figure');assert.equal(await figures.count(),2);assert.equal(await figures.nth(0).locator('tbody tr').count(),4);assert.equal(await figures.nth(1).locator('tbody tr').count(),2);
  const body=await figures.nth(0).innerText();for(const n of [3850,150,319,1256])assert(body.includes('n='+n));assert(body.includes('separate combined-feature'));assert(body.includes(String(metrics.robustness.cross_script.macro_f1)));assert((await figures.nth(1).innerText()).includes(String(metrics.robustness.deployed_rules.macro_f1)));
 });
 await check('existing report tables, matrices and classifier retained',async()=>{assert.equal(await page.locator('#confusion img').count(),9);assert.equal(await page.locator('#comparison tbody tr').count(),9);assert(await page.locator('#per-class tbody tr').count()>0);await page.locator('#demo-form button').click();assert((await page.locator('#demo-result').innerText()).includes('crop_disease'));});
 await check('report Telugu toggle updates charts and switch',async()=>{await toggle('te');assert((await page.locator('#model-charts figcaption').innerText()).includes('వర్క్'));assert((await page.locator('#chart-benchmark option').first().innerText()).includes('319'));assert((await page.locator('#generalization-charts').innerText()).includes('నియమాలు'));await toggle('en');});
 await check('report mobile layout at 375 and 320 pixels',async()=>{for(const width of [375,320]){await page.setViewportSize({width,height:850});await page.waitForTimeout(150);await noOverflow();}await page.locator('#model-charts').screenshot({path:path.join(root,'reports/charts_model_mobile.png')});});
 await page.setViewportSize({width:1280,height:900});await goto('market-prices.html');await page.waitForSelector('#live-price-results tbody tr');
 await check('market retains prices and dropdowns without charts',async()=>{assert.equal(await page.locator('#live-price-results tbody tr').count(),2);assert((await page.locator('#live-price-results').innerText()).includes('2300'));assert.equal(await page.locator('#live-district option').count(),34);assert.equal(await page.locator('script[src="js/charts.js"]').count(),0);assert.equal(await page.locator('main svg, main canvas, .data-chart').count(),0);});
 await check('market single, empty and failed responses remain functional',async()=>{await priceRequest(good([base]));assert.equal(await page.locator('#live-price-results tbody tr').count(),1);await priceRequest(good([]));assert.equal(await page.locator('#live-price-results tbody tr').count(),0);await priceRequest({status:'unavailable',message:'Provider unavailable',records:[]},503);assert((await page.locator('#live-price-status').innerText()).includes('unavailable'));});
 async function harvest(q,p,c){await page.fill('#yield',String(q));await page.fill('#sale-price',String(p));await page.fill('#cost',String(c));await page.locator('#profit-form button').click();return page.locator('#profit-result').innerText();}
 await check('harvest positive, negative and zero estimates without graphs',async()=>{assert((await harvest(20,2450,30000)).includes('19,000'));const loss=await harvest(1,100,500);assert(loss.includes('400')&&loss.includes('Estimated loss'));assert((await harvest(0,0,0)).includes('Break-even'));assert.equal(await page.locator('#profit-result svg, #profit-result canvas, #harvest-chart').count(),0);});
 await check('market mobile layout and both language toggles',async()=>{await page.setViewportSize({width:320,height:850});await noOverflow();await toggle('te');await noOverflow();assert.equal(await page.locator('html').getAttribute('lang'),'te');await toggle('en');});
 await goto('weather.html');await page.waitForSelector('#weather-charts svg');
 await check('forecast lines and rainfall bars use seven returned dates',async()=>{assert.equal(await page.locator('#weather-charts polyline').count(),2);assert.equal(await page.locator('#weather-charts circle').count(),7);const f=page.locator('#weather-charts figure');assert.equal(await f.nth(0).locator('tbody tr').count(),7);assert.equal(await f.nth(1).locator('tbody tr').count(),7);assert((await f.nth(0).innerText()).includes('°C'));assert((await f.nth(1).innerText()).includes('36'));assert((await f.nth(1).innerText()).includes('mm'));assert((await page.locator('#weather-result').innerText()).includes('What this means for your field'));});
 await check('selected location preserved in both forecast charts',async()=>{await page.selectOption('#city','custom');await page.fill('#custom-city','Nizamabad');await page.locator('#weather-submit').click();await page.waitForFunction(()=>!document.getElementById('weather-submit').disabled);const titles=await page.locator('#weather-charts figcaption').allTextContents();assert(titles.every(t=>t.includes('Nizamabad')));});
 await check('weather charts translate and fit mobile',async()=>{await toggle('te');assert((await page.locator('#weather-charts').innerText()).includes('వర్షపాతం'));await noOverflow();await page.locator('#weather-charts').screenshot({path:path.join(root,'reports/charts_weather_mobile.png')});await toggle('en');});
 await check('forecast chart series and tables equal the returned forecast',async()=>{const rows=await page.locator('#weather-charts figure').first().locator('tbody tr').allTextContents();for(let i=0;i<7;i++){assert(rows[i].includes(forecast.daily.time[i]));assert(rows[i].includes(String(forecast.daily.temperature_2m_max[i])));assert(rows[i].includes(String(forecast.daily.temperature_2m_min[i])));}});
 async function requestWeather(){await page.locator('#weather-submit').click();await page.waitForFunction(()=>!document.getElementById('weather-submit').disabled);}
 await check('zero rainfall is zero, negative temperatures supported',async()=>{weatherPayload=JSON.parse(JSON.stringify(forecast));weatherPayload.daily.precipitation_sum=Array(7).fill(0);weatherPayload.daily.temperature_2m_min=Array(7).fill(-5);weatherPayload.daily.temperature_2m_max=Array(7).fill(0);await requestWeather();assert.equal(await page.locator('#weather-charts figure').nth(1).locator('rect[width="0"]').count(),7);assert((await page.locator('#weather-charts').innerText()).includes('-5'));});
 for(const [name,payload,status] of [['empty',{},200],['single day',{daily:{...forecast.daily,time:['2026-11-13']}},200],['failure',{},503]]){
  await check('weather '+name+' preserves error handling and hides stale charts',async()=>{weatherPayload=payload;weatherStatus=status;await requestWeather();assert(await page.locator('#weather-result').isHidden());assert((await page.locator('#weather-status').innerText()).includes('could not'));assert(await page.locator('#weather-fallback').isVisible());});
 }
 await check('accessible SVG names and readable data tables',async()=>{weatherPayload=forecast;weatherStatus=200;await requestWeather();for(const svg of await page.locator('#weather-charts svg').all())assert(await svg.getAttribute('aria-label'));assert.equal(await page.locator('#weather-charts table caption').count(),2);});
 await goto('index.html');await check('farmer home has no model charts',async()=>{assert.equal(await page.locator('script[src="js/charts.js"]').count(),0);assert.equal(await page.locator('#model-charts').count(),0);});
 await check('no JavaScript errors across all tested pages',async()=>assert.deepEqual(errors,[]));
 await browser.close();const summary={passed:checks.filter(c=>c.status==='passed').length,failed:checks.filter(c=>c.status==='failed').length,checks,javascript_errors:errors};fs.writeFileSync(path.join(root,'reports/charts_test_results.json'),JSON.stringify(summary,null,2));console.log(JSON.stringify({passed:summary.passed,failed:summary.failed,javascript_errors:errors}));process.exitCode=summary.failed?1:0;
})().catch(async e=>{console.error(e);if(browser)await browser.close();process.exitCode=1;});
