"""Run Python and browser tests, starting a private API only when needed."""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.vendor')]

TCP_RESTRICTED=False
def alive():
    global TCP_RESTRICTED
    try:
        with urllib.request.urlopen('http://127.0.0.1:5000/health',timeout=2) as r:return r.status==200
    except Exception as e:
        if getattr(getattr(e,'reason',e),'winerror',None)==10013:TCP_RESTRICTED=True
        return False

def main():
    server=None
    log=None
    try:
        running=alive()
        if not running and not TCP_RESTRICTED:
            log=(ROOT/'reports/api_test_server.log').open('w',encoding='utf8')
            server=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            deadline=time.monotonic()+30
            while not alive() and time.monotonic()<deadline:
                if server.poll() is not None:raise RuntimeError('Test API did not start; see reports/api_test_server.log')
                time.sleep(.25)
            if not alive():raise RuntimeError('API health check timed out')
        py=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT)
        env=os.environ.copy()
        if TCP_RESTRICTED:
            env['NLP_BROWSER_WSGI']='1'
            env['NLP_PYTHON']=sys.executable
            print('Local TCP is restricted: browser integration uses actual Flask routes over stdio.',flush=True)
        web=subprocess.run(['node','tests/frontend.cjs'],cwd=ROOT,env=env)
        p=json.loads((ROOT/'reports/test_summary.json').read_text(encoding='utf8'))
        f=json.loads((ROOT/'reports/frontend_results.json').read_text(encoding='utf8'))
        import pandas as pd
        table=pd.DataFrame([{'suite':'pytest','passed':p['passed'],'failed':p['failed']+p['errors']},
                            {'suite':'Playwright','passed':f['passed'],'failed':f['failed']}])
        print('\nFINAL TEST SUMMARY\n'+table.to_string(index=False))
        comparison=pd.read_csv(ROOT/'reports/model_comparison.csv')
        print('\nMODEL RESULTS\n'+comparison[['model','features','test_accuracy','test_macro_f1']].to_string(index=False))
        (ROOT/'reports/verification.md').write_text('# Executed verification\n\n'+table.to_markdown(index=False)+'\n\nBrowser/API transport: '+f['transport']+'. Real API routes and model executed; no simulated predictions. Weather responses were deterministic fixtures; a separate live weather check is recorded.\n\n'+comparison[['model','features','test_accuracy','test_macro_f1']].to_markdown(index=False,floatfmt='.4f')+'\n',encoding='utf8')
        return int(py.returncode!=0 or web.returncode!=0)
    finally:
        if server:
            server.terminate();server.wait(timeout=10)
        if log:log.close()

if __name__=='__main__':raise SystemExit(main())
