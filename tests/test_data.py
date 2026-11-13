import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from ml.preprocess import normalize
from ml.data import CORE

def test_data_integrity(root):
    train=pd.read_csv(root/'data/train.csv');val=pd.read_csv(root/'data/validation_original.csv');test=pd.read_csv(root/'data/test_original.csv')
    valid=set(CORE+['other_agri','out_of_scope'])
    for frame in [train,val,test]:
        assert not frame['query'].isna().any()
        assert frame['query'].map(normalize).ne('').all()
        assert set(frame.intent)<=valid
        assert not frame.normalized.duplicated().any()
    for a,b in [(train,val),(train,test),(val,test)]:
        assert not set(a.normalized)&set(b.normalized)
        assert not set(a.group)&set(b.group)
    assert set(val.source)==set(test.source)=={'workbook'}

def test_every_crop_and_intent(root):
    d=pd.read_csv(root/'data/train.csv')
    for c in json.loads((root/'data/crops.json').read_text(encoding='utf8')):
        for label in CORE:
            assert ((d.crop==c['id'])&(d.intent==label)).sum()>=15,(c['id'],label)

def test_no_cross_split_near_duplicates(root):
    # Reproduce the independent audit feature definition over workbook text.
    d=pd.read_csv(root/'data/workbook_clean.csv')
    v=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),dtype=np.float32)
    x=v.fit_transform(d.normalized)
    for a,b in [('train','test'),('train','validation'),('validation','test')]:
        left=x[d.split.eq(a).to_numpy()];right=x[d.split.eq(b).to_numpy()]
        for i in range(0,left.shape[0],256):
            sim=left[i:i+256]@right.T
            assert sim.data.size==0 or sim.data.max()<.92,(a,b,sim.data.max())
    syn=pd.read_csv(root/'data/train.csv');syn=syn[syn.source=='synthetic']
    aug=v.transform(syn.normalized)
    held=x[d.split.ne('train').to_numpy()]
    for i in range(0,aug.shape[0],256):
        sim=aug[i:i+256]@held.T
        assert sim.data.size==0 or sim.data.max()<.92,'Synthetic/held-out near duplicate'

def test_synthetic_provenance(root):
    syn=pd.read_csv(root/'data/synthetic_augmented.csv')
    assert set(syn.source)=={'synthetic'}
    assert set(syn.split)=={'train'}
    assert {'out_of_scope',*CORE}<=set(syn.intent)

def test_handwritten_is_unseen(root):
    h=pd.read_csv(root/'data/handwritten_test.csv');tr=pd.read_csv(root/'data/train.csv')
    assert len(h)>=150
    assert not set(h['query'].map(normalize))&set(tr.normalized)
    assert h['query'].nunique()==len(h)
