import json
import pandas as pd
import pytest
from ml.slots import extract_slots,route_intent
from ml.audit import ROOT
CASES=pd.read_csv(ROOT/'data/symptom_regression.csv').fillna('').to_dict('records')

@pytest.mark.parametrize('case',CASES)
def test_symptom_queries(case):
    s=extract_slots(case['query']);assert s['crop']==case['crop']
    if case['symptom']:assert case['symptom'] in s['symptoms']
    else:assert 'yellow' not in s['symptoms']
    assert route_intent(case['query'],'other_agri',.99,.9)['intent']==case['intent']

def test_location_stage_and_flower_observation():
    s=extract_slots('Warangal lo patti flowering time puvvu raalutundi')
    assert s['location']=='Warangal' and s['stage']=='flowering' and s['observations']==['flower_drop']
    assert extract_slots('tomato post harvest in Markapuram')['stage']=='post_harvest'

@pytest.mark.parametrize('q',['what is seven multiplied by nine','order noodles','hello there','qzxwvvv jjjqqqzz'])
def test_nonfarm_guard(q):
    r=route_intent(q,'fertilizer',.99,.8);assert r['intent']=='out_of_scope' and r['clarify']

@pytest.mark.parametrize('q,label',[('weather','weather'),('rain','weather'),('price','market_price'),('scheme','govt_scheme'),('vaathavaranam','weather'),('dhara','market_price')])
def test_short_keyword_fallback(q,label):assert route_intent(q,'other_agri',.1,.01)['intent']==label
