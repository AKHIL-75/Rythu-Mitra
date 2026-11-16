import ast
from pathlib import Path
from types import SimpleNamespace
import pytest
import requests
from ml import trigger_price_deploy as deploy

HOOK='https://api.vercel.com/v1/integrations/deploy/prj_FIXTURE/FIXTURE_SECRET'

@pytest.mark.parametrize('value',['','http://api.vercel.com/v1/integrations/deploy/prj_x/secret','https://example.invalid/v1/integrations/deploy/prj_x/secret','https://api.vercel.com@evil.invalid/v1/integrations/deploy/prj_x/secret','https://api.vercel.com/v1/integrations/deploy/prj_x/secret?query=secret','https://api.vercel.com/other/path','https://api.vercel.com:8443/v1/integrations/deploy/prj_x/secret'])
def test_invalid_hook_does_not_send_requests(monkeypatch,capsys,value):
    monkeypatch.setenv('VERCEL_DEPLOY_HOOK',value)
    monkeypatch.setattr(deploy.requests,'post',lambda *a,**k:pytest.fail('unexpected request'))
    assert deploy.main()==1
    assert 'FIXTURE_SECRET' not in capsys.readouterr().out


def test_deploy_hook_post_is_bounded_and_has_no_redirects(monkeypatch,capsys):
    monkeypatch.setenv('VERCEL_DEPLOY_HOOK',HOOK);calls=[]
    def post(url,**kwargs):calls.append((url,kwargs));return SimpleNamespace(status_code=201)
    monkeypatch.setattr(deploy.requests,'post',post)
    assert deploy.main()==0
    assert calls==[(HOOK,{'timeout':20,'allow_redirects':False})]
    assert HOOK not in capsys.readouterr().out


@pytest.mark.parametrize('code',[302,403,500])
def test_failed_deploy_hook_is_visible_but_secret_safe(monkeypatch,capsys,code):
    monkeypatch.setenv('VERCEL_DEPLOY_HOOK',HOOK)
    monkeypatch.setattr(deploy.requests,'post',lambda *a,**k:SimpleNamespace(status_code=code))
    assert deploy.main()==1
    output=capsys.readouterr().out
    assert str(code) in output and 'FIXTURE_SECRET' not in output


def test_network_error_never_prints_secret_url(monkeypatch,capsys):
    monkeypatch.setenv('VERCEL_DEPLOY_HOOK',HOOK)
    def fail(*a,**k):raise requests.ConnectionError(HOOK)
    monkeypatch.setattr(deploy.requests,'post',fail)
    assert deploy.main()==1
    assert 'FIXTURE_SECRET' not in capsys.readouterr().out
