import io
import json
import logging
from urllib.parse import urlparse, parse_qs
from urllib.error import HTTPError, URLError
import pytest
from ml import price_diagnostics as diagnostics
from ml import prices

@pytest.mark.parametrize('stage,expected', [('minimal', set()), ('state', {'state.keyword'}), ('filtered', {'state.keyword','district','commodity'})])
def test_probe_stages_use_one_record_and_documented_filters(monkeypatch,stage,expected,caplog):
    monkeypatch.setenv('DATA_GOV_IN_API_KEY','PRIVATE_FIXTURE_ONLY')
    calls=[]
    def open_fixture(url,timeout):
        calls.append((parse_qs(urlparse(url).query),timeout))
        return io.BytesIO(b'{"records":[{"secret_body":"DO_NOT_RETURN"}]}')
    with caplog.at_level(logging.WARNING):
        result,status=diagnostics.probe(stage,{'state':'Telangana','district':'Hanumakonda','commodity':'Bitter gourd'},open_fixture)
    params,timeout=calls[0]
    assert params['limit']==['1'] and timeout==8
    assert {k[8:-1] for k in params if k.startswith('filters[')}==expected
    assert status==200 and result['record_count']==1
    assert 'PRIVATE_FIXTURE_ONLY' not in json.dumps(result)+caplog.text
    assert 'DO_NOT_RETURN' not in json.dumps(result)+caplog.text

@pytest.mark.parametrize('error,expected',[(TimeoutError('SECRET'),'timeout'),(URLError('SECRET'),'connection_failed'),(HTTPError('SECRET',403,'SECRET',{},None),'authentication_failed'),(HTTPError('SECRET',429,'SECRET',{},None),'rate_limited'),(ValueError('SECRET'),'invalid_response')])
def test_probe_failures_are_safe(monkeypatch,error,expected,caplog):
    monkeypatch.setenv('DATA_GOV_IN_API_KEY','PRIVATE_FIXTURE_ONLY')
    def failed(*a,**k):raise error
    result,status=diagnostics.probe('minimal',{},failed)
    assert result['status']==expected and status==200
    assert 'SECRET' not in json.dumps(result)+caplog.text

@pytest.mark.parametrize('payload', [None, [], 'stage', {'stage':[]}, {'stage':'bogus'}, {'stage':'minimal','filters':[]}, {'stage':'minimal','filters':{'district':1}}])
def test_invalid_diagnostics_never_call_provider(client,monkeypatch,payload):
    monkeypatch.setenv('DIAGNOSTICS_TOKEN','ADMIN_FIXTURE_ONLY')
    monkeypatch.setattr(prices,'_open_provider',lambda *a,**k:pytest.fail('unexpected network'))
    response=client.post('/_diagnostics/prices',json=payload,headers={'Authorization':'Bearer ADMIN_FIXTURE_ONLY'})
    assert response.status_code==400

def test_diagnostic_route_disabled_and_authenticated(client,monkeypatch):
    monkeypatch.delenv('DIAGNOSTICS_TOKEN',raising=False)
    assert client.post('/_diagnostics/prices',json={}).status_code==404
    assert client.get('/price-diagnostics').status_code==404
    monkeypatch.setenv('DIAGNOSTICS_TOKEN','ADMIN_FIXTURE_ONLY')
    page=client.get('/price-diagnostics')
    assert page.status_code==200 and page.headers['Cache-Control']=='no-store'
    for header in ['', 'Bearer wrong', 'ADMIN_FIXTURE_ONLY']:
        assert client.post('/_diagnostics/prices',json={},headers={'Authorization':header}).status_code==401
    monkeypatch.setenv('DATA_GOV_IN_API_KEY','PRIVATE_FIXTURE_ONLY')
    monkeypatch.setattr(prices,'_open_provider',lambda *a,**k:io.BytesIO(b'{"records":[]}'))
    response=client.post('/_diagnostics/prices',json={'stage':'minimal'},headers={'Authorization':'Bearer ADMIN_FIXTURE_ONLY'})
    assert response.status_code==200 and response.json['record_count']==0
    assert response.headers['Cache-Control']=='no-store'
    assert 'PRIVATE_FIXTURE_ONLY' not in response.get_data(as_text=True)

def test_unauthorized_request_does_not_probe(client,monkeypatch):
    monkeypatch.setenv('DIAGNOSTICS_TOKEN','ADMIN_FIXTURE_ONLY')
    monkeypatch.setattr(prices,'_open_provider',lambda *a,**k:pytest.fail('unexpected network'))
    assert client.post('/_diagnostics/prices',json={'stage':'minimal'}).status_code==401


def test_diagnostics_reject_concurrent_probe(client,monkeypatch):
    monkeypatch.setenv('DIAGNOSTICS_TOKEN','ADMIN_FIXTURE_ONLY')
    headers={'Authorization':'Bearer ADMIN_FIXTURE_ONLY'}
    def nested_probe(*args,**kwargs):
        assert client.post('/_diagnostics/prices',json={'stage':'minimal'},headers=headers).status_code==429
        return {'status':'ok'},200
    monkeypatch.setattr(diagnostics,'probe',nested_probe)
    assert client.post('/_diagnostics/prices',json={'stage':'minimal'},headers=headers).status_code==200
