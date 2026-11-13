import io
import json
from ml import prices

def test_prices_missing_key(client,monkeypatch):
    monkeypatch.delenv('DATA_GOV_IN_API_KEY',raising=False)
    r=client.get('/prices');assert r.status_code==200 and r.json['status']=='not_configured' and not r.json['records']

def test_prices_cache_and_filters(monkeypatch):
    monkeypatch.setenv('DATA_GOV_IN_API_KEY','TEST_ONLY_NOT_A_REAL_KEY');prices.CACHE.clear();calls=[]
    # Explicit fixture, never written into real-price reports or the UI as observed data.
    fixture={'records':[dict(state='Test state',district='Test district',market='Test market',commodity='Test commodity',arrival_date='01/01/2000',modal_price='100',min_price='90',max_price='110')]}
    def opener(url,timeout):calls.append(url);return io.BytesIO(json.dumps(fixture).encode())
    a,status=prices.fetch_prices({'state':'Test state','commodity':'Test commodity'},opener)
    b,_=prices.fetch_prices({'state':'Test state','commodity':'Test commodity'},opener)
    assert status==200 and a['records'][0]['arrival_date']=='01/01/2000' and b['cached'] and len(calls)==1
    assert 'filters%5Bstate%5D' in calls[0]
    assert 'TEST_ONLY_NOT_A_REAL_KEY' not in json.dumps(a)

def test_price_failures(monkeypatch):
    monkeypatch.setenv('DATA_GOV_IN_API_KEY','test');prices.CACHE.clear()
    def broken(*a,**k):raise RuntimeError('secret URL must never be returned')
    a,status=prices.fetch_prices({},broken);assert status==503 and not a['records'] and 'secret' not in a['message']
    a,status=prices.fetch_prices({'commodity':'a'*101},broken);assert status==400

def test_incomplete_record_not_fabricated(monkeypatch):
    monkeypatch.setenv('DATA_GOV_IN_API_KEY','test');prices.CACHE.clear()
    a,status=prices.fetch_prices({},lambda *a,**k:io.BytesIO(b'{"records":[{"commodity":"Tomato","modal_price":null}]}'))
    assert status==200 and a['status']=='no_records' and not a['records']


def test_provider_http_errors_are_actionable_and_hide_secrets(monkeypatch):
    from urllib.error import HTTPError
    monkeypatch.setenv('DATA_GOV_IN_API_KEY', 'private-test-key')
    prices.CACHE.clear()
    for code, expected in [(401, 'authentication_failed'), (403, 'authentication_failed'), (429, 'rate_limited'), (500, 'unavailable')]:
        def rejected(*args, **kwargs):
            raise HTTPError('https://example.invalid/?api-key=private-test-key', code, 'private-test-key', {}, None)
        result, status = prices.fetch_prices({}, rejected)
        assert status in (502, 503) and result['status'] == expected
        assert not result['records'] and 'private-test-key' not in json.dumps(result)


def test_provider_network_errors_are_actionable(monkeypatch):
    import socket
    import ssl
    from urllib.error import URLError
    monkeypatch.setenv('DATA_GOV_IN_API_KEY', 'private-test-key')
    prices.CACHE.clear()
    for reason, expected in [(TimeoutError(), 'too long'), (socket.gaierror(), 'DNS'), (ssl.SSLError(), 'certificates'), (ConnectionRefusedError(), 'firewall')]:
        def disconnected(*args, **kwargs):
            raise URLError(reason)
        result, status = prices.fetch_prices({}, disconnected)
        assert status == 503 and result['status'] == 'connection_failed'
        assert expected in result['message'] and not result['records']


def test_malformed_provider_response_is_distinct(monkeypatch):
    monkeypatch.setenv('DATA_GOV_IN_API_KEY', 'private-test-key')
    prices.CACHE.clear()
    for payload in [b'<html>Service unavailable</html>', b'{"error":"private-test-key"}', b'{"records":[null]}']:
        result, status = prices.fetch_prices({}, lambda *args, **kwargs: io.BytesIO(payload))
        assert status == 502 and result['status'] == 'invalid_response'
        assert not result['records'] and 'private-test-key' not in json.dumps(result)


def test_windows_transport_keeps_key_out_of_command_line(monkeypatch):
    from types import SimpleNamespace
    calls = []
    def run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout=json.dumps({'ok': True, 'data': {'records': []}}))
    monkeypatch.setattr(prices.subprocess, 'run', run)
    with prices._open_windows_provider('https://example.invalid/?api-key=private-test-key', 25) as response:
        assert json.load(response) == {'records': []}
    args, kwargs = calls[0]
    assert 'private-test-key' not in ' '.join(args)
    assert kwargs['input'].endswith('private-test-key') and kwargs['timeout'] == 30
    assert kwargs['capture_output'] and kwargs['encoding'] == 'utf-8'


def test_windows_transport_errors_use_existing_safe_messages(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv('DATA_GOV_IN_API_KEY', 'private-test-key')
    monkeypatch.setattr(prices, '_open_provider', prices._open_windows_provider)
    prices.CACHE.clear()
    for envelope, expected in [
        ({'ok': False, 'http_status': 403}, 'authentication_failed'),
        ({'ok': False, 'http_status': 429}, 'rate_limited'),
        ({'ok': False, 'http_status': 0, 'kind': 'timeout'}, 'connection_failed'),
        ({'ok': False, 'http_status': 0, 'kind': 'network'}, 'connection_failed'),
    ]:
        monkeypatch.setattr(prices.subprocess, 'run', lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=json.dumps(envelope)))
        result, status = prices.fetch_prices({'state': 'Telangana'})
        assert result['status'] == expected and status in (502, 503)
        assert not result['records'] and 'private-test-key' not in json.dumps(result)


def test_windows_transport_process_timeout_hides_input(monkeypatch):
    import subprocess
    monkeypatch.setenv('DATA_GOV_IN_API_KEY', 'private-test-key')
    monkeypatch.setattr(prices, '_open_provider', prices._open_windows_provider)
    prices.CACHE.clear()
    def expired(*args, **kwargs):
        raise subprocess.TimeoutExpired('private-test-key', 30)
    monkeypatch.setattr(prices.subprocess, 'run', expired)
    result, status = prices.fetch_prices({})
    assert status == 503 and 'too long' in result['message']
    assert 'private-test-key' not in json.dumps(result)


def test_windows_script_json_and_timeout_without_network():
    import subprocess
    import sys
    import pytest
    if sys.platform != 'win32':
        pytest.skip('Windows PowerShell transport')
    fixtures = [
        ("function Invoke-RestMethod { param($Uri, $TimeoutSec, $ErrorAction) @{records=@(@{commodity='Paddy'; market='Test market'})} }", True),
        ("function Invoke-RestMethod { param($Uri, $TimeoutSec, $ErrorAction) throw [System.TimeoutException]::new('fixture timeout') }", False),
    ]
    for stub, success in fixtures:
        process = subprocess.run(
            ['powershell.exe', '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', stub + '\n' + prices._WINDOWS_REQUEST],
            input='https://example.invalid/?api-key=fixture-only', encoding='utf-8', capture_output=True,
            timeout=15, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        assert process.returncode == 0
        envelope = json.loads(process.stdout.lstrip('\ufeff'))
        assert envelope['ok'] == success
        if success:
            assert envelope['data']['records'][0]['commodity'] == 'Paddy'
        else:
            assert envelope['kind'] == 'timeout'
