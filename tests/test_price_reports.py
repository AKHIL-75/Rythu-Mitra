import io
import json
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
import pytest
from ml import prices, price_reports as reports, refresh_prices as refresh


def record(**kw):
    return dict(state='Telangana',district='Hanamkonda',market='Fixture mandi',commodity='Cabbage',variety='Fixture variety',grade='FAQ',arrival_date='01/01/2000',min_price='90',max_price='110',modal_price='100',**kw)


@pytest.fixture
def report_path(tmp_path,monkeypatch):
    path=tmp_path/'mandi_prices.json'
    monkeypatch.setattr(reports,'REPORT_PATH',path)
    return path


def test_vercel_serves_report_without_key_or_upstream(client,monkeypatch,report_path):
    reports.save_report([record()],1)
    monkeypatch.setenv('VERCEL','1');monkeypatch.delenv('DATA_GOV_IN_API_KEY',raising=False)
    monkeypatch.setattr(prices,'fetch_prices',lambda *a,**k:pytest.fail('must not contact provider'))
    response=client.get('/prices?state=Telangana&district=Hanumakonda&commodity=Cabbage')
    assert response.status_code==200
    data=response.json
    assert data['status']=='ok' and data['source_mode']=='saved_report'
    assert data['records'][0]['arrival_date']=='01/01/2000' and data['records'][0]['modal_price']=='100'
    assert 'not a live lookup' in data['message'] and data['fetched_at']
    assert client.get('/data/mandi_prices.json').status_code==404


def test_snapshot_filters_never_substitute_district_or_commodity(report_path):
    reports.save_report([record()],1)
    for filters in [{'commodity':'Tomato'},{'district':'Warangal'},{'state':'Andhra Pradesh'},{'market':'Another mandi'}]:
        data,status=reports.reported_prices(filters)
        assert status==200 and data['status']=='no_records' and data['records']==[]
        assert 'not mean the price is zero' in data['message']


def test_zero_and_missing_values_are_preserved(report_path):
    row=record();row.update(modal_price='0',min_price=None,max_price=None)
    reports.save_report([row],1)
    result,_=reports.reported_prices({})
    assert result['records'][0]['modal_price']=='0'
    assert result['records'][0]['min_price'] is None and result['records'][0]['max_price'] is None


@pytest.mark.parametrize('value',[None,'',-1,'nan','inf',True,'secret'])
def test_invalid_modal_is_never_saved(report_path,value):
    reports.save_report([record()],1);before=report_path.read_bytes()
    row=record();row['modal_price']=value
    with pytest.raises(ValueError):reports.save_report([row],1)
    assert report_path.read_bytes()==before


def test_failed_refresh_keeps_previous_report(monkeypatch,report_path,capsys):
    reports.save_report([record()],1);before=report_path.read_bytes()
    import dotenv
    monkeypatch.setattr(dotenv,'load_dotenv',lambda *a,**k:False)
    monkeypatch.setenv('DATA_GOV_IN_API_KEY','PRIVATE_FIXTURE_ONLY')
    def broken(*args,**kwargs):raise RuntimeError('https://example.invalid/?api-key=PRIVATE_FIXTURE_ONLY')
    monkeypatch.setattr(refresh,'collect',broken)
    assert refresh.main([])==1 and report_path.read_bytes()==before
    assert 'PRIVATE_FIXTURE_ONLY' not in capsys.readouterr().out


def test_old_report_explicitly_labelled(report_path):
    reports.save_report([record()],1)
    data=json.loads(report_path.read_text());data['fetched_at']=(reports.now_utc()-timedelta(days=3)).isoformat()
    report_path.write_text(json.dumps(data))
    data,_=reports.reported_prices({})
    assert data['report_outdated'] and '24 hours' in data['message']


@pytest.mark.parametrize('mode',['missing','invalid_json','wrong_source','partial','future'])
def test_invalid_or_absent_published_report_never_causes_outbound_call(client,monkeypatch,report_path,mode):
    monkeypatch.setenv('VERCEL','1')
    monkeypatch.setattr(prices,'fetch_prices',lambda *a,**k:pytest.fail('unexpected outbound call'))
    if mode!='missing':
        reports.save_report([record()],1)
        data=json.loads(report_path.read_text())
        if mode=='wrong_source':data['source']='https://example.invalid'
        if mode=='partial':data['coverage']['complete']=False
        if mode=='future':data['fetched_at']=(reports.now_utc()+timedelta(days=1)).isoformat()
        report_path.write_text('not json' if mode=='invalid_json' else json.dumps(data))
    response=client.get('/prices?state=Telangana')
    assert response.status_code==503 and response.json['records']==[]
    assert response.json['status']=='report_unavailable'


def test_local_live_lookup_still_wins_but_saved_report_handles_failure(monkeypatch,report_path):
    reports.save_report([record()],1);monkeypatch.delenv('VERCEL',raising=False)
    live={'status':'ok','records':[{'live':'fixture'}]}
    monkeypatch.setattr(prices,'fetch_prices',lambda *a:(live,200))
    assert reports.get_prices({})==(live,200)
    monkeypatch.setattr(prices,'fetch_prices',lambda *a:({'status':'connection_failed'},503))
    assert reports.get_prices({})[0]['source_mode']=='saved_report'


def test_pagination_is_complete_and_only_safe_fields_saved(report_path):
    row1=record();row2=record();row2['market']='Fixture B';row3=record();row3['market']='Fixture C'
    row1['private_metadata']='PRIVATE_FIXTURE_ONLY';calls=[]
    payloads=[{'total':3,'records':[row1,row2]},{'total':3,'records':[row3]}]
    def opener(url,timeout):
        query=parse_qs(urlparse(url).query);calls.append(query)
        assert timeout==25 and query['filters[state.keyword]']==['Telangana']
        return io.BytesIO(json.dumps(payloads[len(calls)-1]).encode())
    rows=refresh.collect('PRIVATE_FIXTURE_ONLY',opener)
    reports.save_report(rows,len(rows))
    assert [c['offset'] for c in calls]==[['0'],['2']]
    assert 'PRIVATE_FIXTURE_ONLY' not in report_path.read_text()
    assert len(reports.reported_prices({})[0]['records'])==3


@pytest.mark.parametrize('mode',['empty','partial','wrong_state','repeated','bad_body'])
def test_collector_rejects_failed_or_incomplete_downloads(mode):
    calls=[]
    def opener(url,timeout):
        calls.append(url)
        data={'records':[record()], 'total':3}
        if mode=='empty' or mode=='partial' and len(calls)>1:data['records']=[]
        if mode=='wrong_state':data['records'][0]['state']='Punjab'
        if mode=='bad_body':return io.BytesIO(b'<html>failure</html>')
        return io.BytesIO(json.dumps(data).encode())
    with pytest.raises(ValueError):refresh.collect('PRIVATE_FIXTURE_ONLY',opener,max_pages=3)


def test_invalid_filters_are_rejected_before_report_lookup(report_path):
    result,status=reports.reported_prices({'district':'a'*101})
    assert status==400 and result['records']==[]
