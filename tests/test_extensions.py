import ast
import json
import joblib
import pandas as pd
from ml.preprocess import normalize
from ml.problems import predict_problem

def test_problem_model_provenance_and_scores(root):
    models=joblib.load(root/'ml/models/problem_models.joblib')
    m=json.loads((root/'reports/problem_metrics.json').read_text(encoding='utf8'))
    assert len(models)==7
    d=pd.read_csv(root/'reports/problem_predictions.csv')
    for split,g in d.groupby('split'):
        assert abs(g.correct.mean()-m['summary'][split]['accuracy'])<1e-10
    s=predict_problem(models,'tomato leaf spot treatment','crop_disease')
    assert s['label']=='leaf spot' and 0<=s['confidence']<=1

def test_primary_benchmark_unseen_and_metrics(root):
    tr=pd.read_csv(root/'data/train.csv');h=pd.read_csv(root/'data/handwritten_test_v2.csv')
    assert len(h)>=300 and len(h)==h['query'].nunique()
    assert not set(h['query'].map(normalize))&set(tr.normalized)
    r=json.loads((root/'reports/robustness_metrics.json').read_text(encoding='utf8'))
    p=pd.read_csv(root/'reports/handwritten_v2_predictions.csv')
    assert abs((p.intent==p.raw_prediction).mean()-r['selected_raw']['accuracy'])<1e-10
    assert abs((p.intent==p.deployed_prediction).mean()-r['deployed_rules']['accuracy'])<1e-10
    transfer=pd.read_csv(root/'reports/cross_script_predictions.csv');assert set(transfer.version)=={'query_telugu'}
    assert len(transfer)==r['cross_script']['test_rows']

def test_typo_training_only(root):
    d=pd.read_csv(root/'data/typo_augmented.csv');held=pd.concat([pd.read_csv(root/'data/test_original.csv'),pd.read_csv(root/'data/validation_original.csv')])
    assert len(d)>0 and set(d.source)=={'synthetic'} and set(d.split)=={'train'}
    assert not set(d.group)&set(held.group)
    assert not set(d.normalized)&set(held.normalized)

def test_colab_notebook_is_unexecuted_and_syntax_valid(root):
    n=json.loads((root/'notebooks/indicbert_colab.ipynb').read_text(encoding='utf8'))
    assert n['nbformat']==4
    for cell in n['cells']:
        if cell['cell_type']=='code':
            assert cell['execution_count'] is None and not cell['outputs']
            source=''.join(cell['source'])
            if not source.startswith('%'):ast.parse(source)
