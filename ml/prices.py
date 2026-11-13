"""Optional data.gov.in mandi adapter. No key, sample rates or failed data are invented."""
import json
import io
import subprocess
import sys
import os
import time
import threading
import socket
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
import requests

RESOURCE='https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
SOURCE='https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi'
CACHE={};LOCK=threading.Lock();TTL=600


# Windows urllib can time out even when Invoke-RestMethod succeeds on the same
# machine. Use the Windows connection path; send the URL over stdin so the key
# never appears in process arguments, shell history, or temporary files.
_WINDOWS_REQUEST = r"""
$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
try {
    $url = [Console]::In.ReadToEnd().Trim()
    $data = Invoke-RestMethod -Uri $url -TimeoutSec 25 -ErrorAction Stop
    @{ok=$true; data=$data} | ConvertTo-Json -Depth 20 -Compress
} catch {
    $httpStatus = 0
    if ($null -ne $_.Exception.Response) {
        try { $httpStatus = [int]$_.Exception.Response.StatusCode } catch {}
    }
    $kind = 'network'
    $cause = $_.Exception
    while ($null -ne $cause) {
        if ($cause -is [System.TimeoutException] -or
            ($cause -is [System.Net.WebException] -and $cause.Status -eq [System.Net.WebExceptionStatus]::Timeout)) {
            $kind = 'timeout'
        }
        $cause = $cause.InnerException
    }
    @{ok=$false; http_status=$httpStatus; kind=$kind} | ConvertTo-Json -Compress
}
"""


def _open_windows_provider(url, timeout):
    try:
        process = subprocess.run(
            ['powershell.exe', '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', _WINDOWS_REQUEST],
            input=url, encoding='utf-8', capture_output=True, timeout=timeout + 5,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError('Price provider timed out') from None
    except OSError:
        raise URLError('Windows price connection could not start') from None
    if process.returncode:
        raise URLError('Windows price connection failed')
    envelope = json.loads(process.stdout.lstrip('\ufeff'))
    if envelope.get('ok') is not True:
        code = envelope.get('http_status', 0)
        if code:
            raise HTTPError(RESOURCE, int(code), 'Price provider rejected request', {}, None)
        if envelope.get('kind') == 'timeout':
            raise TimeoutError('Price provider timed out')
        raise URLError('Windows price connection failed')
    return io.BytesIO(json.dumps(envelope.get('data')).encode('utf-8'))


def _open_provider(url, timeout):
    if sys.platform == 'win32':
        return _open_windows_provider(url, timeout)
    try:
        with requests.get(url, timeout=timeout, stream=True) as response:
            if response.status_code >= 400:
                raise HTTPError(RESOURCE, response.status_code, 'Price provider rejected request', response.headers, None)
            content=bytearray()
            for chunk in response.iter_content(chunk_size=65536):
                content.extend(chunk)
                if len(content)>2_000_000:
                    raise ValueError('Price provider response is too large')
            return io.BytesIO(content)
    except requests.exceptions.Timeout:
        raise TimeoutError('Price provider timed out') from None
    except requests.exceptions.SSLError as error:
        raise URLError(error) from None
    except requests.exceptions.RequestException:
        raise URLError('Price provider request failed') from None


def fetch_prices(filters,opener=None):
    key=os.environ.get('DATA_GOV_IN_API_KEY','').strip()
    base=dict(source=SOURCE,records=[],unit='INR per quintal (as published by the mandi resource)',agmarknet='https://agmarknet.gov.in/')
    if not key:return dict(base,status='not_configured',message='Live mandi prices are not configured. Check the server API key configuration or see Agmarknet. No live rate is shown.'),200
    allowed=['state','district','market','commodity'];clean={}
    for name in allowed:
        value=filters.get(name,'')
        if not isinstance(value,str) or len(value)>100:return dict(base,status='invalid_filter',message='Use text filters of at most 100 characters.'),400
        if value.strip():clean[name]=value.strip()
    cache_key=(key,tuple(sorted(clean.items())))
    with LOCK:
        cached=CACHE.get(cache_key)
        if cached and time.monotonic()-cached[0]<TTL:return dict(cached[1],cached=True),200
    params={'api-key':key,'format':'json','limit':100,**{f'filters[{k}]':v for k,v in clean.items()}}
    try:
        with (opener or _open_provider)(RESOURCE+'?'+urlencode(params),timeout=25) as response:
            raw=json.loads(response.read(2_000_000))
        if not isinstance(raw,dict) or not isinstance(raw.get('records'),list):raise ValueError('Malformed upstream payload')
        records=[]
        for r in raw['records']:
            # Keep only complete, interpretable records. Never replace a missing value with zero.
            if not all(r.get(k) not in [None,''] for k in ['state','district','market','commodity','arrival_date','modal_price']):continue
            try:
                price=float(r['modal_price'])
                if not 0<=price<float('inf'):continue
            except (TypeError,ValueError):continue
            records.append({k:r.get(k) for k in ['state','district','market','commodity','variety','grade','arrival_date','min_price','max_price','modal_price']})
        result=dict(base,status='ok' if records else 'no_records',records=records,cached=False,
                    fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),filters=clean,
                    message="Reported mandi rates: check each reporting date, market, variety and unit. They may not be today's rates." if records else 'No complete reported rates matched. Try broader filters or see Agmarknet.')
        with LOCK:
            if len(CACHE)>=128:CACHE.clear()
            CACHE[cache_key]=(time.monotonic(),result)
        return result,200
    except HTTPError as error:
        # Only return our own messages: upstream URLs and bodies may contain the key.
        if error.code in (401, 403):
            return dict(base,status='authentication_failed',message='The price provider rejected the API request. Check the data.gov.in API key configured on the server and its access permissions, then restart the server. No live rate is shown.'),502
        if error.code == 429:
            return dict(base,status='rate_limited',message='The price provider request limit has been reached. Please wait and try again later. No live rate is shown.'),503
        return dict(base,status='unavailable',message='The price provider returned an HTTP error. Please retry later or see Agmarknet. No live rate is shown.'),503
    except (TimeoutError, URLError) as error:
        reason = error.reason if isinstance(error, URLError) else error
        if isinstance(reason, (TimeoutError, socket.timeout)):
            message='The price provider took too long to respond. Please retry later. No live rate is shown.'
        elif isinstance(reason, socket.gaierror):
            message='The server could not find the price provider. Check the server internet connection and DNS settings. No live rate is shown.'
        elif isinstance(reason, ssl.SSLError):
            message='The server could not verify a secure connection to the price provider. Check the server certificates and system date. No live rate is shown.'
        else:
            message='The server could not connect to the price provider. Check the server internet connection, firewall or proxy settings. No live rate is shown.'
        return dict(base,status='connection_failed',message=message),503
    except (ValueError, TypeError, AttributeError):
        return dict(base,status='invalid_response',message='The price provider returned an unreadable or incomplete response. Please retry later or see Agmarknet. No live rate is shown.'),502
    except Exception:
        return dict(base,status='unavailable',message='The mandi price service could not be reached or returned invalid data. Please retry later or see Agmarknet. No live rate is shown.'),503
