"""Independent challenges are reporting-only; no benchmark-driven model selection."""
import json
import importlib.util
import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
from ml.train import scores,features
from ml.preprocess import normalize
from ml.slots import route_intent
from ml.audit import ROOT

def evaluate(models,selected,train):
    hand=pd.read_csv(ROOT/'data/handwritten_test_v2.csv');old=pd.read_csv(ROOT/'data/handwritten_test.csv')
    assert len(hand)>=300 and not set(hand['query'].map(normalize))&set(train.normalized),'V2 benchmark overlap'
    assert not set(hand['query'].map(normalize))&set(old['query'].map(normalize)),'V2 repeats v1'
    rows=[]
    for key,model in models.items():
        p=model.predict(hand['query']);row=dict(experiment=key,**scores(hand.intent,p));rows.append(row)
        if key==selected['key']:
            hand['raw_prediction']=p;probs=model.predict_proba(hand['query']);routed=[];clarifications=[]
            for q,raw,prob in zip(hand['query'],p,probs):
                top=sorted(prob,reverse=True);r=route_intent(q,str(raw),float(top[0]),float(top[0]-top[1]));routed.append(r['intent']);clarifications.append(r['clarify'])
            hand['deployed_prediction']=routed;hand['clarify']=clarifications
    hand.to_csv(ROOT/'reports/handwritten_v2_predictions.csv',index=False)
    result=dict(primary_benchmark='independently authored v2; reporting only, no selection',rows=len(hand),raw_models=rows,
        selected_raw=scores(hand.intent,hand.raw_prediction),deployed_rules=scores(hand.intent,hand.deployed_prediction),
        clarification_rate=float(hand.clarify.mean()),provenance=f'All {len(hand)} literal queries were authored for this project; this is a synthetic challenge, not a representative farmer sample. Exact overlaps with v1 are excluded and recorded separately.')
    # Group-disjoint cross-script transfer, rather than training on a test query's translations.
    d=pd.read_csv(ROOT/'data/workbook_clean.csv')
    a=d[d.split.eq('train')&d.version.isin(['query_english','query_code_mixed'])]
    b=d[d.split.eq('test')&d.version.eq('query_telugu')]
    assert not set(a.group)&set(b.group)
    model=Pipeline([('features',features('combined')),('model',LogisticRegression(C=2,solver='liblinear',class_weight='balanced',max_iter=500,random_state=42))])
    with threadpool_limits(limits=2):model.fit(a['query'],a.intent)
    pred=model.predict(b['query']);transfer=dict(train_rows=len(a),test_rows=len(b),**scores(b.intent,pred),policy='Original training groups, English+code-mixed columns only; original held-out test groups, Telugu column only. Code-mixed training can contain Telugu. Parallel translations never cross groups.')
    b=b.copy();b['prediction']=pred;b.to_csv(ROOT/'reports/cross_script_predictions.csv',index=False)
    result['cross_script']=transfer
    available={name:importlib.util.find_spec(name) is not None for name in ['torch','transformers']}
    result['indicbert']=dict(status='NOT RUN',available=available,reason='No installed torch/transformers and usable pretrained weight bundle was available; use notebooks/indicbert_colab.ipynb. No neural metrics claimed.')
    (ROOT/'reports/robustness_metrics.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    text='# Primary robustness evaluation\n\n'+result['provenance']+'\n\n'+pd.DataFrame(rows).to_markdown(index=False,floatfmt='.4f')
    text+='\n\n## Deployed guard/slot policy (reported separately from raw ML)\n\n'+pd.DataFrame([result['selected_raw'],result['deployed_rules']],index=['raw selected model','deployed guard + slot lexicon']).to_markdown(floatfmt='.4f')
    text+='\n\nClarification rate: '+str(result['clarification_rate'])+'. These thresholds and lexicons are design choices, not benchmark-tuned estimates of field performance.\n\n## Cross-script transfer\n\n'+json.dumps(transfer,indent=2)+'\n\nIndicBERT: NOT RUN. See the executable Colab notebook.\n'
    (ROOT/'reports/robustness.md').write_text(text,encoding='utf8')
    return result
