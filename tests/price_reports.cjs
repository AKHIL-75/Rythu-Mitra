const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert');
let pw;try{pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');}catch(_){pw=require(path.join(os.homedir(),'.cache','codex-runtimes','codex-primary-runtime','dependencies','node','node_modules','playwright'));}
const root=path.resolve(__dirname,'..');
const {spawnSync}=require('child_process');
const inference=spawnSync('python',['-c',"import json; from app import app; print(json.dumps(app.test_client().post('/predict',json={'query':'Hanumakonda cabbage market price'}).get_json()))"],{cwd:root,encoding:'utf8',windowsHide:true});
assert.equal(inference.status,0);const prediction=JSON.parse(inference.stdout);

const saved={status:'ok',source_mode:'saved_report',report_outdated:true,records:[{state:'Telangana',district:'Hanamkonda',market:'FIXTURE ONLY mandi',commodity:'Cabbage',variety:'Fixture variety',grade:'FAQ',arrival_date:'01/01/2000',min_price:null,max_price:null,modal_price:'0'}],unit:'INR per quintal (as published by the mandi resource)',fetched_at:'2000-01-02T00:00:00Z',message:'Saved official mandi report. These are reported rates, not a live lookup. Check each reporting date. The saved report has not been refreshed in the past 24 hours.'};
(async()=>{
 let browser;try{browser=await pw.chromium.launch({headless:true});}catch(_){browser=await pw.chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});}
 const checks=[],errors=[];
 try{
 const page=await browser.newPage();page.on('pageerror',e=>errors.push(String(e)));let payload=saved,http=200;
 await page.route('http://report.test/**',async route=>{
  const url=new URL(route.request().url());
  if(url.pathname==='/predict')return route.fulfill({json:prediction});
  if(url.pathname==='/prices')return route.fulfill({status:http,json:payload});
  const file=path.join(root,url.pathname.slice(1));
  if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
  return route.fulfill({body:fs.readFileSync(file),contentType:file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':'text/html'});
 });
 await page.goto('http://report.test/market-prices.html?lang=en');await page.waitForSelector('#live-price-results tbody tr');
 let text=await page.locator('#live-price-results').innerText();assert(text.includes('not a live lookup'));assert(text.includes(saved.fetched_at));assert(text.includes('01/01/2000'));assert.equal(await page.locator('#live-price-results tbody tr td').last().innerText(),'0');assert(text.includes('not reported'));checks.push('saved-report/date/refresh labels and zero/missing rates');
 await page.click('#language-toggle');assert.equal(await page.locator('html').getAttribute('lang'),'te');assert(/[\u0c00-\u0c7f]/.test(await page.locator('#live-price-status').innerText()));assert(/[\u0c00-\u0c7f]/.test(await page.locator('#live-price-results .notice').innerText()));checks.push('Telugu toggle updates saved-report labels');
 await page.setViewportSize({width:320,height:700});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks.push('320px mobile layout');
 payload={...saved,status:'no_records',records:[],message:'No matching rate is present in the saved official report. This does not mean the price is zero.'};
 await page.click('#live-price-form button');await page.waitForFunction(()=>!document.querySelector('#live-price-form button').disabled);assert.equal(await page.locator('#live-price-results table').count(),0);checks.push('missing commodity never fabricates rate');
 http=503;payload={status:'report_unavailable',records:[],message:'An official mandi report is not available yet.'};await page.click('#live-price-form button');await page.waitForFunction(()=>!document.querySelector('#live-price-form button').disabled);assert.equal(await page.locator('#live-price-results table').count(),0);checks.push('missing report retains explicit empty state');
 assert.equal(await page.locator('main svg,main canvas').count(),0);checks.push('no removed market charts reintroduced');
 payload=saved;http=200;await page.goto('http://report.test/index.html?lang=en');await page.fill('#query','Hanumakonda cabbage market price');await page.click('#ask-form button[type=submit]');await page.waitForSelector('#home-price-live tbody tr');
 assert((await page.locator('#home-price-live').innerText()).includes('Saved official report, not a live lookup'));assert((await page.locator('#home-price-live').innerText()).includes(saved.fetched_at));checks.push('home answer labels saved report and accepts equivalent district spelling');
 assert.deepEqual(errors,[]);checks.push('no JavaScript errors');console.log(JSON.stringify({passed:checks.length,failed:0,checks}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
