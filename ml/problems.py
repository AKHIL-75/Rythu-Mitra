"""Within-intent problem classifiers. Source metadata is retained, not inferred as facts."""
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold,cross_val_score
from threadpoolctl import threadpool_limits
from ml.train import features,scores
from ml.preprocess import normalize,VARIANTS
from ml.audit import ROOT

def payload(pipe):
    f=pipe.named_steps['features'];clf=pipe.named_steps['model']
    result=dict(labels=clf.classes_.tolist(),kind='logistic',weights=clf.coef_.tolist(),bias=clf.intercept_.tolist(),variants=VARIANTS,vectorizers=[])
    for _,v in f.transformer_list:
        result['vectorizers'].append(dict(vocabulary={k:int(x) for k,x in v.vocabulary_.items()},idf=v.idf_.tolist(),analyzer=v.analyzer,ngram=list(v.ngram_range),sublinear_tf=v.sublinear_tf))
    return result

def predict_problem(models,query,intent):
    if intent not in models:return None
    pipe=models[intent];p=pipe.predict_proba([query])[0];i=int(p.argmax())
    return dict(label=str(pipe.classes_[i]),confidence=float(p[i]))

def train_problems(train,val,test):
    original=train[train.source.eq('workbook')&train.problem.notna()].copy()
    hand=pd.read_csv(ROOT/'data/problem_handwritten.csv')
    assert not set(hand['query'].map(normalize))&set(train.normalized)
    models={};rows=[];predictions=[]
    for intent,g in original.groupby('intent'):
        known=set(g.problem)
        assert set(hand[hand.intent==intent].problem)<=known,(intent,'unknown evaluation label')
        cv=list(StratifiedGroupKFold(5,shuffle=True,random_state=42).split(g['query'],g.problem,g.group))
        pipe=Pipeline([('features',features('combined')),('model',LogisticRegression(C=2,solver='liblinear',class_weight='balanced',max_iter=500,random_state=42))],memory=joblib.Memory(ROOT/'ml/cache/problem',verbose=0))
        # Typo rows keep the same source problem and originating group. No coverage templates guessed into problem labels.
        fit=train[train.intent.eq(intent)&train.problem.notna()&train.version.isin(['query_code_mixed','query_telugu','query_english','typo_augmentation'])]
        with threadpool_limits(limits=2):
            cv_scores=cross_val_score(pipe,g['query'],g.problem,cv=cv,scoring='f1_macro',n_jobs=1)
            pipe.fit(fit['query'],fit.problem)
        models[intent]=pipe;v=val[val.intent==intent];t=test[test.intent==intent];h=hand[hand.intent==intent]
        row=dict(intent=intent,classes=len(known),train_rows=len(fit),cv_macro_f1=float(cv_scores.mean()),cv_std=float(cv_scores.std()))
        for name,frame in [('validation',v),('test',t),('handwritten',h)]:
            p=pipe.predict(frame['query']);row.update({name+'_'+k:x for k,x in scores(frame.problem,p).items()})
            for text,y,pred in zip(frame['query'],frame.problem,p):predictions.append(dict(split=name,query=text,intent=intent,problem=y,prediction=pred,correct=y==pred))
        rows.append(row);print('Problem model:',intent,'test accuracy',row['test_accuracy'],'handwritten',row['handwritten_accuracy'],flush=True)
    joblib.dump(models,ROOT/'ml/models/problem_models.joblib',compress=3)
    exported={k:payload(v) for k,v in models.items()}
    (ROOT/'js/problem-data.js').write_text('window.PROBLEM_MODELS='+json.dumps(exported,ensure_ascii=False,separators=(',',':'))+';',encoding='utf8')
    pred=pd.DataFrame(predictions);pred.to_csv(ROOT/'reports/problem_predictions.csv',index=False)
    summary={name:dict(rows=len(g),**scores(g.problem,g.prediction)) for name,g in pred.groupby('split')}
    result=dict(models=rows,summary=summary,evaluation_conditioning='True intent supplied for each example: conditional problem accuracy, not end-to-end pipeline accuracy.',policy='Fixed C=2 Logistic Regression, combined TF-IDF; five group CV folds on original training text. Test and authored handwritten labels never used to tune. Problem predictions are suggestions, not diagnoses.')
    (ROOT/'reports/problem_metrics.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    (ROOT/'reports/problem_model.md').write_text('# Within-intent problem model\n\n'+pd.DataFrame(rows).to_markdown(index=False,floatfmt='.4f')+'\n\n'+pd.DataFrame(summary).T.to_markdown(floatfmt='.4f')+'\n\n'+result['policy']+'\n\nThe workbook metadata includes implausible stage/problem combinations. Stage and location are extracted as slots; neither is treated as a verified agronomic causal feature. The handwritten set is project-authored, not collected from farmers.\n',encoding='utf8')
    cases=[]
    for intent,g in hand.groupby('intent'):
        for q in g['query'].head(3):cases.append(dict(query=q,intent=intent,**predict_problem(models,q,intent)))
    (ROOT/'reports/problem_parity_cases.json').write_text(json.dumps(cases,ensure_ascii=False),encoding='utf8')
    return result
