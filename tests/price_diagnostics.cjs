const fs=require('fs'),path=require('path'),os=require('os'),assert=require('assert');
let pw;try{pw=require(process.env.PLAYWRIGHT_MODULE||'playwright');}catch(_){pw=require(path.join(os.homedir(),'.cache','codex-runtimes','codex-primary-runtime','dependencies','node','node_modules','playwright'));}
const root=path.resolve(__dirname,'..');
(async()=>{
 let browser;try{browser=await pw.chromium.launch({headless:true});}catch(_){browser=await pw.chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});}
 try{
 const page=await browser.newPage();const errors=[],calls=[];page.on('pageerror',e=>errors.push(String(e)));let mode='ok';
 await page.route('http://diagnostics.test/**',async route=>{
  const url=new URL(route.request().url());
  if(url.pathname==='/_diagnostics/prices'){
   const request=route.request(),body=request.postDataJSON();calls.push(body);
   assert.equal(request.headers().authorization,'Bearer ADMIN_FIXTURE_ONLY');assert(!url.search);assert.equal(body.filters.state,'Telangana');
   if(mode==='unauthorized')return route.fulfill({status:401,json:{error:'Unauthorized'}});
   if(mode==='disabled')return route.fulfill({status:404,json:{error:'Not found'}});
   return route.fulfill({json:{stage:body.stage,status:mode==='timeout'?'timeout':'ok',elapsed_seconds:.01,...(mode==='timeout'?{}:{upstream_http_status:200,record_count:0})}});
  }
  const file=path.join(root,url.pathname==='/price-diagnostics'?'ml/price_diagnostics.html':url.pathname.slice(1));
  return route.fulfill({body:fs.readFileSync(file),contentType:file.endsWith('.js')?'application/javascript':'text/html'});
 });
 await page.goto('http://diagnostics.test/price-diagnostics');
 async function run(){await page.fill('#token','ADMIN_FIXTURE_ONLY');await page.click('#run');await page.waitForFunction(()=>!document.getElementById('run').disabled);assert.equal(await page.inputValue('#token'),'');}
 await run();assert.deepEqual(calls.map(c=>c.stage),['minimal','state','filtered']);assert.equal(await page.locator('tbody tr').count(),3);assert((await page.locator('#interpretation').innerText()).includes('All connection tests succeeded'));
 mode='timeout';await run();assert((await page.locator('#interpretation').innerText()).includes('Even the minimal request failed'));assert.equal(await page.locator('tbody tr').count(),3);
 mode='unauthorized';await run();assert((await page.locator('#status').innerText()).includes('Token rejected'));assert.equal(await page.locator('tbody tr').count(),0);
 mode='disabled';await run();assert((await page.locator('#status').innerText()).includes('Diagnostics are disabled'));
 assert.equal(await page.evaluate(()=>localStorage.length+sessionStorage.length),0);
 await page.setViewportSize({width:320,height:700});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 assert.deepEqual(errors,[]);console.log('PASS: stages, timeouts, unauthorized/disabled endpoints, token clearing, no token storage, 320px layout, no JavaScript errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
