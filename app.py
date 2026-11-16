"""Local Flask API and static site. No query body is retained or logged."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.vendor'))
import joblib
from flask import Flask, request, jsonify, send_from_directory
from ml.preprocess import normalize, script_type
from ml.slots import extract_slots,route_intent

def create_app():
    app=Flask(__name__,static_folder=None)
    app.config['MAX_CONTENT_LENGTH']=16384
    model_path=ROOT/'ml/models/best_model.joblib'
    model=joblib.load(model_path) if model_path.exists() else None
    problem_path=ROOT/'ml/models/problem_models.joblib'
    problem_models=joblib.load(problem_path) if problem_path.exists() else {}

    @app.get('/prices')
    def prices():
        from ml.prices import fetch_prices
        data,status=fetch_prices(request.args)
        return jsonify(data),status

    @app.get('/health')
    def health():
        return jsonify(status='ok' if model is not None else 'model_missing',model_loaded=model is not None),200 if model is not None else 503

    @app.post('/predict')
    def predict():
        payload=request.get_json(silent=True)
        if not isinstance(payload,dict) or not isinstance(payload.get('query'),str):
            return jsonify(error='query must be a string'),400
        q=payload['query'].strip()
        if not q or not normalize(q):return jsonify(error='Please enter a text question.'),400
        if len(q)>800:return jsonify(error='Please keep the question within 800 characters.'),400
        if model is None:return jsonify(error='Train the model with python ml/run_all.py'),503
        probs=model.predict_proba([q])[0]
        top=sorted([dict(intent=str(label),confidence=float(p)) for label,p in zip(model.classes_,probs)],key=lambda x:-x['confidence'])
        first=top[0];features=model.calibrated_classifiers_[0].estimator.named_steps['features'] if hasattr(model,'calibrated_classifiers_') else model.named_steps['features']
        empty=features.transform([q]).nnz==0
        clarify=empty or first['confidence']<.45 or first['confidence']-top[1]['confidence']<.08 or first['intent'] in ['other_agri','out_of_scope']
        slots=extract_slots(q)
        routed=route_intent(q,first['intent'],first['confidence'],first['confidence']-top[1]['confidence'])
        from ml.problems import predict_problem
        problem=predict_problem(problem_models,q,routed['intent'])
        return jsonify(**routed,raw_intent=first['intent'],confidence=first['confidence'],confidence_scope='raw_intent_model',top3=top[:3],
            **slots,problem=problem,script_type=script_type(q),
            confidence_level='Please add more detail' if routed['clarify'] else 'Likely topic — please check',
            message='Please describe the crop and whether you need crop health, nutrients, water, price, weather or scheme guidance.' if routed['clarify'] else 'Review the suggested topic before using the guide.',mode='backend')

    @app.get('/')
    def index():return send_from_directory(ROOT,'index.html')

    @app.get('/<path:path>')
    def assets(path):
        # Serve explicit public UI artifacts only, not Python, training data or models.
        if (path.endswith('.html') and '/' not in path) or (path.startswith(('js/','css/')) and path.endswith(('.js','.css'))) or (path.startswith('reports/') and path.endswith('.png')):
            return send_from_directory(ROOT,path)
        return jsonify(error='Not found'),404

    return app

app=create_app()
if __name__=='__main__':app.run(host='127.0.0.1',port=5000,debug=False)
