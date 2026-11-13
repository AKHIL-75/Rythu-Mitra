import pytest

@pytest.mark.parametrize('path',[
    '/','/about.html','/crop-disease.html','/fertilizer.html','/govt-schemes.html',
    '/index.html','/irrigation.html','/market-prices.html','/model-report.html','/weather.html',
    '/css/style.css','/js/app.js','/js/model-report.js','/reports/logistic_regression_word_confusion.png',
])
def test_public_pages_and_assets(client,path):
    response=client.get(path)
    assert response.status_code==200,path

def test_health(client):
    r=client.get('/health');assert r.status_code==200;assert r.json['model_loaded']

@pytest.mark.parametrize('payload',[{},None,[],{'query':None},{'query':10},{'query':[]},{'query':''},{'query':'   '},{'query':'a'*801},{'query':'1234...'}])
def test_invalid_input(client,payload):
    assert client.post('/predict',json=payload).status_code==400

@pytest.mark.parametrize('q',['naaku vari ki leaf spot vachindi','పత్తి పంటకు ఎరువులు ఎంత వేయాలి','What is the market price of tomato?'])
def test_prediction(client,q):
    r=client.post('/predict',json={'query':q});assert r.status_code==200
    d=r.json;assert len(d['top3'])==3;assert 0<=d['confidence']<=1;assert d['crop']
    assert {'intent','confidence','top3','crop','script_type','clarify'}<=set(d)

def test_gibberish(client):
    r=client.post('/predict',json={'query':'qzxwvvv jjjqqqzz'})
    assert r.status_code==200 and r.json['clarify']

def test_private_files_not_served(client):
    for p in [
        '/.env','/.env.local','/app.py','/data/train.csv','/data/crops.json',
        '/ml/models/best_model.joblib','/ml/models/problem_models.joblib',
        '/ml/models/metrics.json','/ml/models/experiments/logistic_regression_word.joblib',
        '/notebooks/indicbert_colab.ipynb','/tests/test_api.py',
    ]:
        assert client.get(p).status_code==404

@pytest.mark.parametrize('query,crop,symptom,intent',[
    ('nakku vari chettu ki pasupu rangu vachindi em cheyali','paddy','yellow','crop_disease'),
    ('patti aakulu pasupu avuthunnay em cheyali','cotton','yellow','crop_disease'),
    ('pasupu panta ki neellu eppudu','turmeric',None,'irrigation')])
def test_slot_contract(client,query,crop,symptom,intent):
    r=client.post('/predict',json={'query':query});assert r.status_code==200
    assert r.json['crop']==crop and r.json['intent']==intent
    if symptom:assert symptom in r.json['symptoms']

def test_stage_and_location_api(client):
    r=client.post('/predict',json={'query':'Warangal lo patti flowering time leaf spot vachindi'})
    assert r.json['location']=='Warangal' and r.json['stage']=='flowering'
    assert 'problem' in r.json
