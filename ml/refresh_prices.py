"""Run on the working Windows connection; publish only validated official responses.
Usage: python -m ml.refresh_prices
The program loads the local .env at runtime, never prints its contents and never pushes Git.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from ml import prices
from ml.price_reports import save_report, REPORT_PATH


def collect(key, opener=None, max_pages=100):
    if not key:raise ValueError('DATA_GOV_IN_API_KEY is not configured')
    rows=[];offset=0;seen=set();total=None
    for page in range(max_pages):
        params={'api-key':key,'format':'json','limit':100,'offset':offset,'filters[state.keyword]':'Telangana'}
        with (opener or prices._open_provider)(prices.RESOURCE+'?'+urlencode(params),timeout=25) as response:
            raw=response.read(2_000_001)
        if len(raw)>2_000_000:raise ValueError('Provider page too large')
        payload=json.loads(raw)
        if not isinstance(payload,dict) or not isinstance(payload.get('records'),list):
            raise ValueError('Provider returned invalid data')
        batch=payload['records']
        if total is None and payload.get('total') is not None:
            total=int(payload['total'])
            if total<0:raise ValueError('Invalid provider count')
        if not batch:
            if total is not None and offset<total:raise ValueError('Provider returned an incomplete report')
            if not rows:raise ValueError('No records returned; previous report preserved')
            return rows
        if any(not isinstance(r,dict) or str(r.get('state','')).strip().casefold()!='telangana' for r in batch):
            raise ValueError('Provider did not respect Telangana filter')
        signature=json.dumps(batch,sort_keys=True)
        if signature in seen:raise ValueError('Provider repeated a page; previous report preserved')
        seen.add(signature);rows.extend(batch);offset+=len(batch)
        if total is not None and offset>=total:return rows
    raise ValueError('Report exceeded page limit; previous report preserved')


def main(argv=None):
    parser=argparse.ArgumentParser(description='Refresh saved Telangana mandi records from data.gov.in. Never commits or pushes files.')
    parser.parse_args(argv)
    # Normal application configuration: this program reads the key privately when
    # the owner runs it. The assistant does not inspect .env contents.
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1]/'.env',override=False)
    try:
        key=os.environ.get('DATA_GOV_IN_API_KEY','').strip()
        if not key:
            print('Refresh failed: DATA_GOV_IN_API_KEY is missing from the local .env or environment. No file was changed.')
            return 1
        print('Fetching official Telangana mandi report. Please wait; each page has a 25-second timeout.',flush=True)
        rows=collect(key)
        report=save_report(rows,len(rows))
    except Exception as error:
        # Never print exception text: it can include the request URL and API key.
        print('Refresh failed ('+type(error).__name__+'). Previous report preserved. No replacement data was written.')
        return 1
    print('SUCCESS: saved',len(report['records']),'official Telangana mandi records.')
    print('Districts:',len({r['district'] for r in report['records']}))
    print('Fetched UTC:',report['fetched_at'])
    print('Reporting dates:',', '.join(sorted({r['arrival_date'] for r in report['records']})))
    print('Publish file:',REPORT_PATH)
    print('Commit this report with the code changes, then push to refresh Vercel. It is not a live price feed.')
    return 0

if __name__=='__main__':raise SystemExit(main())
