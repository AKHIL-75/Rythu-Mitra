"""CLI for the trusted locally trained artifact."""
import sys
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.vendor')]
import joblib
from ml.entities import detect_crop
from ml.preprocess import script_type

def main():
    if len(sys.argv)<2:raise SystemExit('Usage: python ml/predict.py "your farm question"')
    text=' '.join(sys.argv[1:]).strip()
    if not text or len(text)>800:raise SystemExit('Please provide 1–800 characters.')
    model=joblib.load(ROOT/'ml/models/best_model.joblib')
    p=model.predict_proba([text])[0];i=int(p.argmax())
    from ml.slots import extract_slots,route_intent
    from ml.problems import predict_problem
    top=sorted(p,reverse=True)
    problem_path=ROOT/'ml/models/problem_models.joblib'
    problem_models=joblib.load(problem_path) if problem_path.exists() else {}
    routed=route_intent(text,str(model.classes_[i]),float(p[i]),float(top[0]-top[1]))
    result=dict(**routed,**extract_slots(text),raw_intent=str(model.classes_[i]),confidence=float(p[i]),confidence_scope='raw_intent_model',script_type=script_type(text),problem=predict_problem(problem_models,text,routed['intent']))
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__':main()
