"""Deterministic, train-only corruptions. Inherit origin/group; purge held-out neighbours."""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from ml.preprocess import normalize
from ml.audit import ROOT
def augment(train,val,test):
    rng=np.random.default_rng(42);rows=[]
    for _,r in train.sample(frac=.35,random_state=42).iterrows():
        q=r['query'];inds=[i for i,c in enumerate(q) if c.isascii() and c.isalpha()]
        if not inds:continue
        i=int(rng.choice(inds));op=int(rng.integers(3))
        if op==0 and i+1<len(q) and q[i+1].isalpha():q=q[:i]+q[i+1]+q[i]+q[i+2:]
        elif op==1:q=q[:i]+q[i+1:]
        else:
            vowels=[j for j in inds if q[j].lower() in 'aeiou']
            if not vowels:continue
            j=int(rng.choice(vowels));q=q[:j]+q[j]+q[j:]
        if normalize(q)==r.normalized:continue
        row=r.to_dict();row.update(query=q,normalized=normalize(q),source='synthetic',version='typo_augmentation',parent_query=r['query']);rows.append(row)
    syn=pd.DataFrame(rows)
    original=pd.read_csv(ROOT/'data/workbook_clean.csv')
    v=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),dtype=np.float32);v.fit(original.normalized)
    held=pd.concat([val,test]);h=v.transform(held.normalized);x=v.transform(syn.normalized);bad=set()
    for i in range(0,len(syn),256):
        sim=(x[i:i+256]@h.T).tocoo();bad.update((sim.row[sim.data>=.92]+i).tolist())
    syn=syn.drop(index=list(bad));syn=syn[~syn.normalized.isin(set(train.normalized)|set(held.normalized))].drop_duplicates('normalized')
    syn.to_csv(ROOT/'data/typo_augmented.csv',index=False)
    result=pd.concat([train,syn],ignore_index=True).drop_duplicates('normalized')
    result.to_csv(ROOT/'data/train.csv',index=False)
    update_coverage(result,syn)
    print('Training-only typo rows:',len(syn),'; purged near held-out:',len(bad),flush=True)
    return result

def update_coverage(train,typos):
    table=pd.read_csv(ROOT/'reports/crop_coverage.csv')
    counts=train.groupby(['crop','intent']).size();extra=typos.groupby(['crop','intent']).size()
    table['after_train']=[int(counts.get((r.crop,r.intent),0)) for r in table.itertuples()]
    table['typo_added']=[int(extra.get((r.crop,r.intent),0)) for r in table.itertuples()]
    table.to_csv(ROOT/'reports/crop_coverage.csv',index=False)
    p=ROOT/'reports/crop_coverage.md';text=p.read_text(encoding='utf8').split('\n\n## Final training including typos')[0]
    text+='\n\n## Final training including typos\n\n'+table.pivot(index='name',columns='intent',values='after_train').to_markdown()+'\n\nThe earlier table precedes typo augmentation. This table and the CSV after_train column give the actual final training counts; typo_added is separate from coverage-template synthetic_added.\n'
    p.write_text(text,encoding='utf8')
