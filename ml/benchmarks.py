"""Literal independently authored challenge set; never used for training/tuning."""
import pandas as pd
from ml.audit import ROOT
def build():
    records=[];label=None
    for line in (ROOT/'data/handwritten_v2_authored.txt').read_text(encoding='utf8').splitlines():
        if line.startswith('['):label=line[1:-1]
        elif line.strip():records.append(dict(query=line.strip(),intent=label,source='project_authored_unseen_v2'))
    d=pd.DataFrame(records);assert len(d)>=300
    from ml.preprocess import normalize
    old=pd.read_csv(ROOT/'data/handwritten_test.csv')
    excluded=d['query'].map(normalize).isin(set(old['query'].map(normalize)))
    d[excluded].to_csv(ROOT/'reports/handwritten_v2_overlap_excluded.csv',index=False)
    d=d[~excluded].copy()
    assert len(d)>=300
    d.to_csv(ROOT/'data/handwritten_test_v2.csv',index=False)
    print('Independent authored v2 benchmark:',len(d),d.intent.value_counts().to_dict(),flush=True)
    return d
if __name__=='__main__':build()
