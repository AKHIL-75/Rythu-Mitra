"""Nine measured experiments; all feature fitting occurs inside training folds."""
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import clone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, ConfusionMatrixDisplay
from threadpoolctl import threadpool_limits
from ml.preprocess import normalize

ROOT=Path(__file__).resolve().parents[1]

def features(kind):
    word=TfidfVectorizer(preprocessor=normalize,tokenizer=str.split,token_pattern=None,
        ngram_range=(1,2),sublinear_tf=True,min_df=1,max_features=20000,dtype=np.float64)
    char=TfidfVectorizer(preprocessor=normalize,analyzer='char_wb',ngram_range=(2,5),
        sublinear_tf=True,min_df=2,max_features=25000,dtype=np.float64)
    return word if kind=='word' else char if kind=='char' else FeatureUnion([('word',word),('char',char)])

def scores(y,p):
    out={'accuracy':float(accuracy_score(y,p))}
    for average in ['macro','weighted']:
        pr,re,f,_=precision_recall_fscore_support(y,p,average=average,zero_division=0)
        out.update({f'{average}_precision':float(pr),f'{average}_recall':float(re),f'{average}_f1':float(f)})
    return out

def train_models(train,val,test,stats):
    orig=train[train.source=='workbook'].reset_index(drop=True)
    cv=list(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=42).split(orig['query'],orig.intent,orig.group))
    rows=[];fitted={}
    model_specs={
        'Naive Bayes':(MultinomialNB(),{'model__alpha':[.25,1.0]}),
        'Logistic Regression':(LogisticRegression(solver='liblinear',class_weight='balanced',max_iter=400,random_state=42),{'model__C':[1.,4.]}),
        'Linear SVM':(LinearSVC(class_weight='balanced',random_state=42,max_iter=5000),{'model__C':[.5,2.]})}
    for kind in ['word','char','combined']:
        for name,(clf,grid) in model_specs.items():
            start=time.time();key=name.lower().replace(' ','_')+'_'+kind
            print(f'Tuning {name} / {kind}: 2 candidates × 5 group folds',flush=True)
            pipe=Pipeline([('features',features(kind)),('model',clone(clf))],memory=joblib.Memory(ROOT/'ml/cache',verbose=0))
            gs=GridSearchCV(pipe,grid,scoring='f1_macro',cv=cv,n_jobs=1,refit=False,error_score='raise')
            with threadpool_limits(limits=2):
                gs.fit(orig['query'],orig.intent)
                pipe.set_params(**gs.best_params_)
                if name=='Linear SVM':
                    # Calibrate the full pipeline, including fold-local feature learning.
                    calcv=list(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=42).split(train['query'],train.intent,train.group))
                    model=CalibratedClassifierCV(pipe,method='sigmoid',cv=calcv,ensemble=False,n_jobs=1)
                else:model=pipe
                model.fit(train['query'],train.intent)
            p=model.predict(val['query'])
            row=dict(model=name,features=kind,key=key,cv_macro_f1=float(gs.best_score_),
                cv_std=float(gs.cv_results_['std_test_score'][gs.best_index_]),
                best_params=json.dumps(gs.best_params_),seconds=round(time.time()-start,2))
            row.update({'validation_'+k:v for k,v in scores(val.intent,p).items()})
            rows.append(row);fitted[key]=model
            (ROOT/'ml/models/experiments').mkdir(exist_ok=True)
            joblib.dump(model,ROOT/f'ml/models/experiments/{key}.joblib',compress=3)
            print('Validation macro-F1',row['validation_macro_f1'],'seconds',row['seconds'],flush=True)
    # Select before any evaluation on the locked test or handwritten benchmark.
    selected=max(rows,key=lambda r:(r['validation_macro_f1'],r['validation_accuracy']))
    best=fitted[selected['key']]
    joblib.dump(best,ROOT/'ml/models/best_model.joblib',compress=3)
    labels=best.classes_.tolist()
    (ROOT/'ml/models/label_map.json').write_text(json.dumps(dict(enumerate(labels)),indent=2),encoding='utf8')
    handwritten=pd.read_csv(ROOT/'data/handwritten_test.csv')
    assert len(handwritten)>=150
    assert not set(handwritten['query'].map(normalize)) & set(train['query'].map(normalize)), 'Handwritten exact overlap'
    bestpred=None
    # One final evaluation phase for all prespecified experiments. No subsequent selection.
    reports={}
    for row in rows:
        model=fitted[row['key']];pred=model.predict(test['query'])
        row.update({'test_'+k:v for k,v in scores(test.intent,pred).items()})
        reports[row['key']]=classification_report(test.intent,pred,output_dict=True,zero_division=0)
        (ROOT/f'reports/{row["key"]}_classification.json').write_text(json.dumps(reports[row['key']],indent=2),encoding='utf8')
        fig,ax=plt.subplots(figsize=(9,8))
        ConfusionMatrixDisplay.from_predictions(test.intent,pred,labels=labels,display_labels=labels,
            ax=ax,xticks_rotation=45,cmap='Greens',colorbar=False)
        ax.set_title(row['model']+' / '+row['features']+' — workbook test')
        fig.tight_layout();fig.savefig(ROOT/f'reports/{row["key"]}_confusion.png',dpi=130);plt.close(fig)
        if row['key']==selected['key']:bestpred=pred
    errors=test.copy();errors['prediction']=bestpred
    errors['correct']=errors.intent.eq(errors.prediction)
    errors[~errors.correct].to_csv(ROOT/'reports/error_analysis.csv',index=False)
    breakdown={}
    for field in ['script_type','crop_group']:
        breakdown[field]={str(k):dict(n=len(g),**scores(g.intent,g.prediction)) for k,g in errors.groupby(field)}
    handpred=best.predict(handwritten['query'])
    handwritten['prediction']=handpred;handwritten['correct']=handwritten.intent.eq(handpred)
    handwritten.to_csv(ROOT/'reports/handwritten_predictions.csv',index=False)
    hand=scores(handwritten.intent,handpred)
    hand['rows']=len(handwritten);hand['per_class']=classification_report(handwritten.intent,handpred,output_dict=True,zero_division=0)
    comp=pd.DataFrame(rows);comp.to_csv(ROOT/'reports/model_comparison.csv',index=False)
    columns=['model','features','cv_macro_f1','cv_std','validation_macro_f1','test_accuracy','test_macro_f1','test_weighted_f1']
    md='# Model comparison\n\n'+comp[columns].to_markdown(index=False,floatfmt='.4f')
    md+='\n\nCV uses only deduplicated workbook training queries, five StratifiedGroupKFold folds, '
    md+='and fold-local TF-IDF. Synthetic coverage is added only when fitting each tuned final model. '
    md+='CV and validation therefore measure different training regimes. Validation selects the winner '
    md+='by macro-F1 (accuracy breaks ties); no test or handwritten outcome chooses the model. '
    md+='Test scores are on seven workbook classes; out_of_scope has no genuine workbook test examples. '
    md+='The confusion matrices include its empty true row rather than concealing that absence.\n'
    md+=f'\nSelected: **{selected["model"]} / {selected["features"]}**.\n'
    md+=f'\nIndependent authored handwritten benchmark ({len(handwritten)} queries, all eight classes): '+json.dumps({k:v for k,v in hand.items() if k!='per_class'},indent=2)
    (ROOT/'reports/model_comparison.md').write_text(md,encoding='utf8')
    metrics=dict(seed=42,selected=selected,comparison=rows,classification=reports[selected['key']],
        breakdown=breakdown,handwritten=hand,dataset=stats,
        split_counts={'train':len(train),'validation':len(val),'test':len(test),
                      'synthetic_training':int((train.source=='synthetic').sum())},
        decision_threshold=.55,margin_threshold=.10,
        indicbert={'status':'not_run','reason':'Optional; torch/transformers and model weights are unavailable; no scores claimed.'},
        test_regression_floor=max(0.,round(selected['test_macro_f1']-.03,2)),
        notes=['Workbook provenance does not establish real farmer authorship.',
               'Romanized vs English script breakdown uses a vocabulary heuristic.',
               'Handwritten means authored for this project, not collected from farmers.',
               'Low confidence threshold 0.55 and margin 0.10 are conservative design defaults, not clinical validation.'])
    (ROOT/'ml/models/metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'js/metrics-data.js').write_text('window.MODEL_METRICS='+json.dumps(metrics,ensure_ascii=False)+';',encoding='utf8')
    summary='# Error analysis\n\n'+f'Workbook test errors: {int((~errors.correct).sum())} / {len(errors)}.\n\n'
    wrong=errors[~errors.correct]
    summary+=wrong.groupby(['intent','prediction']).size().rename('count').reset_index().to_markdown(index=False)
    summary+='\n\n## Script breakdown\n\n'+pd.DataFrame(breakdown['script_type']).T.to_markdown()
    summary+='\n\n## Crop-group breakdown\n\n'+pd.DataFrame(breakdown['crop_group']).T.to_markdown()
    summary+='\n\n## Handwritten failures\n\n'+handwritten[~handwritten.correct][['query','intent','prediction']].to_markdown(index=False)
    summary+='\n\nInterpretation: inspect short and colloquial handwritten queries separately from templated workbook text. '
    summary+='Disease/nutrient symptoms can overlap; a topic prediction cannot diagnose the cause. '
    summary+='The grouped split reduces close wording leakage but cannot establish generalization to farmer speech. '
    summary+='Held-out out-of-scope text is authored synthetic material. Confidence can be high on unfamiliar inputs.\n'
    (ROOT/'reports/error_analysis.md').write_text(summary,encoding='utf8')
    (ROOT/'reports/error_analysis_summary.json').write_text(json.dumps({
        'workbook_test_rows':len(errors),'workbook_errors':int((~errors.correct).sum()),
        'handwritten_rows':len(handwritten),'handwritten_errors':int((~handwritten.correct).sum()),
        'handwritten_confusion_pairs':handwritten[~handwritten.correct].groupby(['intent','prediction']).size().reset_index(name='count').to_dict('records'),
        'by_script_type':breakdown['script_type'],'by_crop_group':breakdown['crop_group']},ensure_ascii=False,indent=2),encoding='utf8')
    # Portable browser model: fit a clearly separate centroid fallback on IDENTICAL train rows.
    # Export the exact winning estimator separately where feasible in export.py.
    from ml.export import export_model
    export_model(best,train,val,test)
    from ml.robustness import evaluate
    metrics['robustness']=evaluate(fitted,selected,train)
    from ml.problems import train_problems
    metrics['problem_model']=train_problems(train,val,test)
    primary={r['experiment']:r for r in metrics['robustness']['raw_models']}
    for row in rows:
        row['handwritten_v2_accuracy']=primary[row['key']]['accuracy']
        row['handwritten_v2_macro_f1']=primary[row['key']]['macro_f1']
    pd.DataFrame(rows).to_csv(ROOT/'reports/model_comparison.csv',index=False)
    with (ROOT/'reports/model_comparison.md').open('a',encoding='utf8') as f:
        f.write('\n\n## Primary authored challenge and transfer\n\n'+(ROOT/'reports/robustness.md').read_text(encoding='utf8')+'\n\n'+(ROOT/'reports/problem_model.md').read_text(encoding='utf8'))
    (ROOT/'ml/models/metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'js/metrics-data.js').write_text('window.MODEL_METRICS='+json.dumps(metrics,ensure_ascii=False)+';',encoding='utf8')
    return metrics
