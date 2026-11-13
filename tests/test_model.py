import json
import pandas as pd
import pytest
from sklearn.metrics import f1_score,accuracy_score

EXAMPLES={
 'crop_disease':['tomato leaf spot disease treatment','cotton aphids pest attack','mirapa ki purugulu unnayi','వరి పంటలో పురుగులు ఉన్నాయి','వంకాయ ఆకులపై మచ్చలు వచ్చాయి తెగులు నివారణ'],
 'fertilizer':['paddy urea fertilizer dosage','banana nitrogen deficiency nutrient','tamata ki eruvulu entha veyali','పత్తి పంటకు ఎరువులు ఎంత వేయాలి','వరి కోసం యూరియా డీఏపీ మోతాదు'],
 'irrigation':['tomato drip irrigation schedule','cotton water shortage irrigation','mirapa ki neellu eppudu pettali','వరి పంటకు నీరు ఎప్పుడు పెట్టాలి','వంకాయ పొలానికి సాగునీరు ఎంత అవసరం'],
 'market_price':['tomato mandi price today','cotton selling rate market','vari ki eeroju market dhara entha','టమాటా మార్కెట్ ధర ఎంత','వరి పంటను ఎక్కడ అమ్మాలి ధరలు చెప్పండి'],
 'weather':['Guntur weather forecast rain tomorrow','heat wave weather forecast','repu varsham padutunda','పత్తి పంటకు వాతావరణ సూచన చెప్పండి','వరి పొలం దగ్గర రేపు వర్షం వస్తుందా'],
 'govt_scheme':['PM KISAN government scheme','cotton crop insurance subsidy scheme','panta bima insurance ela apply cheyali','పత్తి రైతుకు ప్రభుత్వ పథకం వివరాలు చెప్పండి','వరి పంట బీమా కోసం ఎలా దరఖాస్తు చేయాలి']}

@pytest.mark.parametrize('intent,query',[(label,q) for label,qs in EXAMPLES.items() for q in qs])
def test_fixed_examples(model,intent,query):
    assert model.predict([query])[0]==intent

def test_model_metrics(model,root):
    m=json.loads((root/'ml/models/metrics.json').read_text(encoding='utf8'))
    test=pd.read_csv(root/'data/test_original.csv')
    # Regression verification, not model selection or threshold tuning.
    score=f1_score(test.intent,model.predict(test['query']),average='macro')
    assert score>=m['test_regression_floor']
    assert abs(score-m['selected']['test_macro_f1'])<1e-10

def test_handwritten_report(model,root):
    d=pd.read_csv(root/'data/handwritten_test.csv');m=json.loads((root/'ml/models/metrics.json').read_text(encoding='utf8'))
    assert abs(accuracy_score(d.intent,model.predict(d['query']))-m['handwritten']['accuracy'])<1e-10

def test_model_loads(model):
    assert len(model.classes_)==8
