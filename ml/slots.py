"""Shared slot extraction. No extracted symptom establishes a diagnosis."""
import json
import unicodedata
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'data/slots.json').read_text(encoding='utf8'))
DISTRICTS=json.loads((ROOT/'data/districts.json').read_text(encoding='utf8'))
def clean(q):return ' '.join(''.join(c if unicodedata.category(c)[0] in 'LM' else ' ' for c in unicodedata.normalize('NFC',str(q)).lower()).split())
def has(text,a):return ' '+clean(a)+' ' in ' '+text+' '
_CROPS=json.loads((ROOT/'data/crops.json').read_text(encoding='utf8'))
_ALIASES=sorted([(clean(a),c['id']) for c in _CROPS for a in [c['english_name'],*c['english_aliases'],*c['romanized_aliases'],*c['telugu_aliases'],*CONFIG.get('extra_crop_aliases',{}).get(c['id'],[])]],key=lambda x:-len(x[0]))
_MATCHERS=[(re.compile(r'(?<!\S)'+re.escape(a)+'(?:'+'|'.join(map(re.escape,CONFIG['suffixes']))+r')?(?!\S)'),c) for a,c in _ALIASES if c!='turmeric']
def detect(query,crops):
    text=clean(query)
    for pattern,c in _MATCHERS:
        if pattern.search(text):return c
    if has(text,'turmeric'):return 'turmeric'
    refs=CONFIG['crop_reference_words']+['ki','ku','lo','కి','కు','లో']
    explicit=any(has(text,a) for a in CONFIG['turmeric_explicit']) or any(has(text,a+' '+r) for a,c in _ALIASES if c=='turmeric' for r in refs)
    price_context=any(has(text,a) for a in CONFIG['intent_keywords']['market_price']) and any(has(text,a) for a,c in _ALIASES if c=='turmeric')
    if (explicit or price_context) and not any(has(text,a) for a in CONFIG['yellow_context']):return 'turmeric'
    return None
def extract_slots(query):
    from ml.entities import CROPS
    text=clean(query);crop=detect(query,CROPS);symptoms=[]
    for key,info in CONFIG['symptoms'].items():
        if any(has(text,a) for a in info['aliases']):
            if key=='yellow' and crop=='turmeric' and not any(has(text,a) for a in CONFIG['yellow_context']):continue
            symptoms.append(key)
    stages=[(len(a),key) for key,v in CONFIG['stages'].items() for a in v if has(text,a)]
    locs=[(len(alias),n,state) for state in ['Telangana','Andhra Pradesh'] for n in DISTRICTS[state] for alias in [n,*CONFIG.get('location_aliases',{}).get(n,[])] if has(text,alias) or any(has(text,alias+suffix) for suffix in CONFIG['suffixes'])]
    topic=next((key for key,info in CONFIG.get('question_topics',{}).items() if any(has(text,a) for a in info['aliases']) and (not info.get('requires') or any(has(text,a) for a in info['requires']))),None)
    loc=max(locs,default=(0,None,None))
    return dict(crop=crop,symptoms=symptoms,observations=[k for k,v in CONFIG['observations'].items() if any(has(text,a) for a in v)],stage=max(stages,default=(0,None))[1],location=loc[1],state=loc[2],question_topic=topic)
def route_intent(query,raw_intent,confidence,margin):
    text=clean(query);slots=extract_slots(query)
    if any(has(text,p) for p in CONFIG['nonfarm_phrases']):return dict(intent='out_of_scope',clarify=True,routing='nonfarm_guard')
    if slots['question_topic']:
        return dict(intent=CONFIG['question_topics'][slots['question_topic']]['intent'],clarify=False,routing='question_topic')
    hits={k:sum(has(text,a) for a in aliases) for k,aliases in CONFIG['intent_keywords'].items()}
    for label in ['govt_scheme','market_price','weather','fertilizer','irrigation']:
        if hits[label]:return dict(intent=label,clarify=False,routing='keyword_fallback')
    if slots['symptoms'] or slots['observations'] or hits['crop_disease']:return dict(intent='crop_disease',clarify=False,routing='symptom_lexicon')
    if not slots['crop'] and not any(has(text,a) for a in CONFIG['farm_words']):return dict(intent='out_of_scope',clarify=True,routing='farming_context_required')
    return dict(intent=raw_intent,clarify=confidence<.55 or margin<.10 or raw_intent in ['out_of_scope','other_agri'],routing='model_threshold')
def export_slots():
    for file,var in [('slots','SLOT_CONFIG'),('districts','SLOT_DISTRICTS')]:
        (ROOT/f'js/{file}-data.js').write_text('window.'+var+'='+json.dumps(json.loads((ROOT/f'data/{file}.json').read_text(encoding='utf8')),ensure_ascii=False)+';',encoding='utf8')
if __name__=='__main__':export_slots()
