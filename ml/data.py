"""Leakage-aware workbook grouping and training-only coverage augmentation."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedGroupKFold
from ml.preprocess import normalize, script_type
from ml.entities import CROPS, detect_crop

ROOT=Path(__file__).resolve().parents[1]
CORE=['crop_disease','fertilizer','irrigation','market_price','weather','govt_scheme']
MAP={'disease_management':'crop_disease','pest_management':'crop_disease',
     'fertilizer_recommendation':'fertilizer','crop_nutrition':'fertilizer',
     'weather_related':'weather','government_scheme':'govt_scheme',
     'irrigation':'irrigation','market_price':'market_price'}

TEMPLATES={
 'crop_disease':[
 'The {c} has leaf spot and fungal infection, what treatment is appropriate?',
 'I noticed insects and holes in {c} leaves; how do I identify this pest?',
 'My {c} plants are wilting with root rot, can someone inspect the disease?',
 'There is whitefly pest attack on {c}; is spraying needed?',
 'How can I manage blight disease on {c} without guessing medicine?',
 '{c} ki purugulu unnayi em mandu veyali',
 '{c} aakula meeda machalu tegulu vachindi em cheyali',
 '{c} mokkalu vadipothunnayi root rot ki treatment enti',
 '{c} lo aaku machalu mariyu pest attack kanipistundi',
 '{c} ki leaf spot vachindi medicine kosam sahayam kavali',
 '{c} ఆకులపై మచ్చలు వచ్చాయి తెగులు నివారణ ఎలా',
 '{c} పంటలో పురుగులు ఉన్నాయి ఏ మందు వాడాలి',
 '{c} మొక్కలు వాడిపోతున్నాయి వేరు కుళ్ళు చికిత్స ఏమిటి',
 '{c} ఆకులు ముడుచుకుంటున్నాయి తెల్లదోమ నివారణ చెప్పండి',
 '{c} పంటకు శిలీంధ్ర వ్యాధి వచ్చింది చికిత్స చెప్పండి'],
 'fertilizer':[
 'What fertilizer and nutrient dosage does {c} need after a soil test?',
 'How much urea DAP and potash should be supplied to {c}?',
 'What is the nitrogen deficiency fertilizer plan for {c}?',
 'Can I apply compost manure as plant nutrition to {c}?',
 'Recommend a basal fertilizer dose for {c} without repeating top dressing',
 '{c} ki eruvulu entha veyali',
 '{c} ki urea dap potash mothadu entha kavali',
 '{c} panta poshakalu nutrition kosam em eruvu',
 '{c} lo nitrogen deficiency undi fertilizer dose cheppandi',
 '{c} ki compost manure eruvu ela vadali',
 '{c} పంటకు ఎరువులు ఎంత వేయాలి',
 '{c} కోసం యూరియా డీఏపీ మోతాదు చెప్పండి',
 '{c} పోషకాల లోపానికి ఏ ఎరువు వేయాలి',
 '{c} పొలంలో కంపోస్ట్ ఎరువు ఎలా వాడాలి',
 '{c} పంటకు నత్రజని పొటాష్ ఎరువుల అవసరం ఎంత'],
 'irrigation':[
 'When should I irrigate {c} and how much water should I use?',
 'How do I schedule drip irrigation water for {c}?',
 'The soil in {c} is dry; how often is watering needed?',
 'There is waterlogging in {c}, how should I drain excess water?',
 'What irrigation schedule suits {c} on sandy soil?',
 '{c} ki neellu eppudu pettali',
 '{c} polam lo neeru enni rojula ki ivvali',
 '{c} ki drip irrigation water schedule cheppandi',
 '{c} lo nela endindi neeti tadulu ela ivvali',
 '{c} ki saguneeru entha ivvali drainage ela',
 '{c} పంటకు నీరు ఎప్పుడు పెట్టాలి',
 '{c} పొలానికి సాగునీరు ఎంత అవసరం',
 '{c} కోసం బిందు సేద్యం నీటి ప్రణాళిక చెప్పండి',
 '{c} పొలంలో నీరు నిలిచింది కాలువలు ఎలా తీయాలి',
 '{c} నేల ఎండిపోయింది నీళ్ళు ఎన్ని రోజులకు ఇవ్వాలి'],
 'market_price':[
 'What is the market price per quintal of {c}?',
 'Where can I sell {c} and compare mandi rates?',
 'Is there a historical MSP reference for {c}?',
 'How can I check the selling price of {c} today?',
 'Compare wholesale market rates before I sell my {c} harvest',
 '{c} ki eeroju market dhara entha',
 '{c} mandi rate cheppandi ekkada ammali',
 '{c} panta ammakam dharalu ela telusukovali',
 '{c} quintal selling price entha undi',
 '{c} ki msp market price information kavali',
 '{c} మార్కెట్ ధర ఎంత',
 '{c} పంటను ఎక్కడ అమ్మాలి ధరలు చెప్పండి',
 '{c} క్వింటాల్ అమ్మకం రేటు ఎంత ఉంది',
 '{c} కనీస మద్దతు ధర వివరాలు కావాలి',
 '{c} మండిలో టోకు ధర ఎలా తెలుసుకోవాలి'],
 'weather':[
 'Will rain or strong wind affect {c} this week? I need a weather forecast',
 'What is the rainfall forecast for the village growing {c}?',
 'Can a heat wave damage {c} during this weather?',
 'Is a storm or hailstorm expected over the {c} field tomorrow?',
 'Give the temperature and weather outlook for {c} farming',
 '{c} polam daggara repu varsham padutunda',
 '{c} ki vaana weather forecast cheppandi',
 '{c} panta meeda endalu heat wave prabhavam enti',
 '{c} kosam gaali vana tufanu heccharika unda',
 '{c} polam lo vatavaranam temperature ela untundi',
 '{c} పొలం దగ్గర రేపు వర్షం వస్తుందా',
 '{c} పంటకు వాతావరణ సూచన చెప్పండి',
 '{c} వద్ద ఉష్ణోగ్రత గాలివాన ఎలా ఉంటుంది',
 '{c} పంటకు వడగాలులు వడగండ్ల వాన ముప్పు ఉందా',
 '{c} కోసం ఈ వారం వర్షపాతం అంచనా కావాలి'],
 'govt_scheme':[
 'Which government scheme or subsidy supports farmers growing {c}?',
 'How do I apply for crop insurance on {c}?',
 'What documents are required for a Kisan Credit Card loan for {c}?',
 'Can a {c} farmer ask about PM KISAN eligibility?',
 'Where do I enquire about government assistance and subsidies for {c}?',
 '{c} rythu ki prabhutva pathakam sahayam kavali',
 '{c} panta bima insurance ela apply cheyali',
 '{c} ki subsidy kosam documents enti',
 '{c} kosam kcc runam loan pathakam cheppandi',
 '{c} rythu bharosa pm kisan scheme ela apply',
 '{c} రైతుకు ప్రభుత్వ పథకం వివరాలు చెప్పండి',
 '{c} పంట బీమా కోసం ఎలా దరఖాస్తు చేయాలి',
 '{c} రైతుకు సబ్సిడీ రుణం ఎలా పొందాలి',
 '{c} కోసం రైతు భరోసా పథకం అర్హత ఏమిటి',
 '{c} రైతుకు పీఎం కిసాన్ దరఖాస్తు పత్రాలు ఏవి']}

OOS=['hello','good morning','who are you','thank you','tell me a joke',
     'cricket match score','who won the football game','movie tickets booking',
     'recommend a film','play a song','write Java code','solve my math homework',
     'buy a mobile phone','where is my train','book a flight','pizza delivery',
     'asdfgh qwerty','zxqvbnm','how do I reset my password','నా పేరు అఖిల్',
     'నాకు సినిమా పాట కావాలి','క్రికెట్ స్కోరు చెప్పు','నమస్కారం','హలో',
     'mobile recharge ela cheyali','cinema ticket kavali','ipl score cheppu',
     'tell me about space travel','what is the capital of France','send a birthday wish']

def near_edges(texts, threshold=.92):
    vec=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),dtype=np.float32)
    x=vec.fit_transform(texts)
    left=[];right=[]
    for start in range(0,len(texts),256):
        sim=(x[start:start+256]@x.T).tocoo()
        mask=(sim.data>=threshold)&((sim.row+start)<sim.col)
        left.extend((sim.row[mask]+start).tolist());right.extend(sim.col[mask].tolist())
    return left,right

def prepare(df):
    records=[]
    # Each version keeps the originating row ID for parallel-translation grouping.
    for col in ['query_code_mixed','query_telugu','query_english']:
        for i,row in df.iterrows():
            records.append(dict(query=row[col],intent=MAP.get(row.intent,'other_agri'),
                original_intent=row.intent,crop=detect_crop(row.crop) or ('citrus_unspecified' if row.crop=='Citrus' else 'general'),
                source='workbook',origin_id=row.query_id,version=col,original_row=i,
                problem=row.problem,growth_stage=row.growth_stage,location=row.location))
    d=pd.DataFrame(records)
    d['normalized']=d['query'].map(normalize)
    conflict=d.groupby('normalized').intent.nunique();bad=set(conflict[conflict>1].index)
    d[d.normalized.isin(bad)].to_csv(ROOT/'data/label_conflicts.csv',index=False)
    d=d[~d.normalized.isin(bad)&d.normalized.ne('')].copy()
    # Build exact-translation equivalence edges before deduplicating text.
    unique={}; parent={}
    def find(a):
        parent.setdefault(a,a)
        while a!=parent[a]:
            parent[a]=parent[parent[a]];a=parent[a]
        return a
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    for r in d.itertuples():
        if r.normalized in unique:union(r.origin_id,unique[r.normalized])
        else:unique[r.normalized]=r.origin_id
    d=d.drop_duplicates('normalized').reset_index(drop=True)
    print('Unique parallel queries:',len(d),flush=True)
    left,right=near_edges(d.normalized.tolist())
    print('Near-duplicate pairs:',len(left),flush=True)
    for a,b in zip(left,right):union(d.at[a,'origin_id'],d.at[b,'origin_id'])
    d['group']=d.origin_id.map(find)
    print('Connected components:',d.group.nunique(),'largest:',d.groupby('group').size().max(),flush=True)
    # 7 stratified grouped folds: five for train, one validation, one test (~71/14/14).
    sg=StratifiedGroupKFold(n_splits=7,shuffle=True,random_state=42)
    d['split']='train'
    for fold,(_,hold) in enumerate(sg.split(d['query'],d.intent,d.group)):
        if fold==0:d.loc[hold,'split']='test'
        if fold==1:d.loc[hold,'split']='validation'
    print(pd.crosstab(d.intent,d['split']).to_string(),flush=True)
    d['script_type']=d['query'].map(script_type)
    d['crop_group']=d.crop.map({c['id']:c['category'] for c in CROPS}).fillna('unspecified')
    d.to_csv(ROOT/'data/workbook_clean.csv',index=False)
    for name in ['train','validation','test']:
        d[d.split==name].to_csv(ROOT/f'data/{name}_original.csv',index=False)
    with (ROOT/'reports/dataset_audit.md').open('a',encoding='utf8') as f:
        f.write(f'\n## Leakage grouping result\n\nUnique queries: {len(d)}. '
                f'Near-duplicate pairs (cosine ≥ 0.92): {len(left)}. '
                f'Connected components including parallel versions: {d.group.nunique()}.\n\n'
                +pd.crosstab(d.intent,d['split']).to_markdown()+'\n\n'
                'Seven stratified group folds allocate five to training, one validation, one test. '
                'Ratios are approximate because connected components are indivisible. '
                'Grouping TF-IDF is an unsupervised audit instrument only; prediction TF-IDF '
                'is fitted independently inside each training fold.\n')
    counts=d.intent.value_counts()
    with (ROOT/'reports/dataset_audit.md').open('a',encoding='utf8') as f:
        f.write('\n## Merged-class balance\n\n'+counts.rename('deduplicated_queries').to_frame().to_markdown()+
                f'\n\nLargest/smallest farm class ratio: {counts.max()/counts.min():.3f}. '
                'Balanced class weights are used for LR/SVM; NB retains empirical priors.\n')
    original=d[d.split=='train'].copy()
    synthetic=[]
    count_original=pd.crosstab(original.crop,original.intent)
    for c in CROPS:
        for label in CORE:
            count=int(count_original.get(label,pd.Series(dtype=int)).get(c['id'],0))
            # Supply the same 15 language variants even for represented crops:
            # the original workbook has little free romanized Telugu coverage.
            for k in range(15):
                name=(c['english_name'] if k<5 else c['romanized_aliases'][0] if k<10 else c['telugu_aliases'][0])
                query=TEMPLATES[label][k].format(c=name)
                synthetic.append(dict(query=query,intent=label,crop=c['id'],source='synthetic',
                    group=f'augmentation_{label}_{k}',origin_id=f'coverage_{c["id"]}_{label}_{k}',
                    version='coverage_template',original_intent=label,split='train',
                    normalized=normalize(query),script_type=script_type(query),crop_group=c['category']))
    for i,q in enumerate(OOS):
        for k,prefix in enumerate(['','please ','hey there ','can you help me with ']):
            text=prefix+q
            synthetic.append(dict(query=text,intent='out_of_scope',crop='general',source='synthetic',
                group=f'oos_family_{i}',origin_id=f'oos_{i}_{k}',version='non_agricultural',
                original_intent='out_of_scope',split='train',normalized=normalize(text),
                script_type=script_type(text),crop_group='unspecified'))
    syn=pd.DataFrame(synthetic)
    # Remove augmentation matching ANY held-out normalized text. Never move it to test.
    syn=syn[~syn.normalized.isin(set(d[d.split!='train'].normalized))].drop_duplicates('normalized')
    syn.to_csv(ROOT/'data/synthetic_augmented.csv',index=False)
    train=pd.concat([original,syn],ignore_index=True).drop_duplicates('normalized')
    train.to_csv(ROOT/'data/train.csv',index=False)
    rows=[]
    for c in CROPS:
        for label in CORE:
            rows.append(dict(crop=c['id'],name=c['english_name'],intent=label,
                before_workbook=int(((d.crop==c['id'])&(d.intent==label)).sum()),
                before_train=int(((original.crop==c['id'])&(original.intent==label)).sum()),
                synthetic_added=int(((syn.crop==c['id'])&(syn.intent==label)).sum()),
                after_train=int(((train.crop==c['id'])&(train.intent==label)).sum())))
    coverage=pd.DataFrame(rows);coverage.to_csv(ROOT/'reports/crop_coverage.csv',index=False)
    text='# Crop coverage\n\nMinimum: 15 training queries per required intent per crop. '
    text+='97 catalog entries, including separate taro and yam and both fodder types. '
    text+='Citrus in the workbook is not assigned arbitrarily to sweet orange or lemon. '
    text+='Counts use all deduplicated parallel query versions, not independent farmer observations.\n\n'
    text+='## Before: complete deduplicated workbook\n\n'+coverage.pivot(index='name',columns='intent',values='before_workbook').to_markdown()
    text+='\n\n## After: augmented training only\n\n'+coverage.pivot(index='name',columns='intent',values='after_train').to_markdown()
    text+='\n\nDetailed original-training and synthetic counts are in crop_coverage.csv. '
    text+='Synthetic coverage is language practice, not evidence that a disease or a subsidy exists for that crop. '
    text+='Regional aliases are approximate and should be reviewed by a Telugu agronomist. '
    text+='Broad bean (fava) is distinguished from field bean (lablab); yam and taro are separate.\n'
    (ROOT/'reports/crop_coverage.md').write_text(text,encoding='utf8')
    return train,d[d.split=='validation'].copy(),d[d.split=='test'].copy()
