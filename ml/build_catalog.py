"""Authoritative alias catalog. English loanwords retained where regional names vary."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

CATALOG = '''cereal|paddy|Paddy|rice|vari,varri|వరి,బియ్యం,వడ్లు
cereal|wheat|Wheat||godhuma,godhumalu|గోధుమ,గోధుమలు
cereal|maize|Maize|corn|mokkajonna,mokka jonna|మొక్కజొన్న
cereal|jowar|Jowar|sorghum|jonna,jonnalu|జొన్న,జొన్నలు
cereal|bajra|Bajra|pearl millet|sajja,sajjalu|సజ్జ,సజ్జలు
cereal|ragi|Ragi|finger millet|ragulu|రాగి,రాగులు
cereal|barley|Barley||barli|బార్లీ
cereal|foxtail|Foxtail millet|foxtail|korra,korralu|కొర్ర,కొర్రలు
cereal|little_millet|Little millet||sama,samalu|సామ,సామలు
pulse|red_gram|Red gram|pigeon pea,arhar,toor|kandi,kandulu|కంది,కందులు
pulse|green_gram|Green gram|moong,mung|pesalu,pesara|పెసలు,పెసర
pulse|black_gram|Black gram|urad|minumulu,minumu|మినుములు,మినుము
pulse|chickpea|Chickpea|bengal gram,bengalgram|senagalu,senaga,sanagalu|శనగ,శనగలు,సెనగలు
pulse|horse_gram|Horse gram||ulavalu,ulava|ఉలవలు,ఉలవ
pulse|cowpea|Cowpea|black eyed pea|alasandalu,alasanda|అలసందలు,అలసంద
pulse|lentil|Lentil|masur|masoor|మసూర్,మసూర్ పప్పు
pulse|field_bean|Field bean|hyacinth bean,lablab|anumulu,anumu|అనుములు,అనుము
oilseed|groundnut|Groundnut|peanut|verusenaga,verusanaga,verushanaga|వేరుశనగ,వేరుసెనగ
oilseed|sunflower|Sunflower||poddu tirugudu,poddutirugudu|పొద్దుతిరుగుడు
oilseed|sesame|Sesame|sesamum|nuvvulu,nuvvu|నువ్వులు,నువ్వు
oilseed|castor|Castor||amudam|ఆముదం
oilseed|soybean|Soybean|soya bean,soyabean|soya|సోయాబీన్,సోయా
oilseed|safflower|Safflower||kusuma,kusumalu|కుసుమ,కుసుమలు
oilseed|mustard|Mustard|rapeseed|avalu,ava|ఆవాలు,ఆవ
oilseed|niger|Niger|nigerseed|verri nuvvulu|వెర్రి నువ్వులు
fibre|cotton|Cotton||patti,pathi,prathi|పత్తి
plantation|sugarcane|Sugarcane||cheruku,cheraku|చెరకు,చెరుకు
plantation|tobacco|Tobacco||pogaku|పొగాకు
fibre|jute|Jute||janumu|జనుము,జూట్
spice|chilli|Chilli|chili,chilly,chillies,red chilli|mirapa,mirchi,mirapakaya|మిరప,మిరపకాయ
spice|turmeric|Turmeric||pasupu|పసుపు
plantation|coconut|Coconut||kobbari|కొబ్బరి
plantation|oil_palm|Oil palm||ayil pam|ఆయిల్ పామ్
plantation|cashew|Cashew||jeedimamidi,jeedi|జీడిమామిడి,జీడి
fruit|mango|Mango||mamidi|మామిడి
fruit|banana|Banana|plantain|arati|అరటి
fruit|papaya|Papaya||boppayi|బొప్పాయి
fruit|guava|Guava||jama|జామ
fruit|sweet_orange|Sweet orange|mosambi|batayi,bathayi|బత్తాయి
fruit|lemon|Lemon||nimma|నిమ్మ
fruit|pomegranate|Pomegranate||danimma|దానిమ్మ
fruit|grapes|Grapes|grape|draksha|ద్రాక్ష
fruit|sapota|Sapota|chikoo,sapodilla|sapota pandu|సపోటా
fruit|custard_apple|Custard apple||seethaphalam,sitaphalam|సీతాఫలం
fruit|watermelon|Watermelon||puchakaya|పుచ్చకాయ
fruit|muskmelon|Muskmelon|cantaloupe|kharbuja|ఖర్బూజా
plantation|areca_nut|Areca nut|arecanut|vakka|వక్క
plantation|coffee|Coffee||kafi|కాఫీ
plantation|tea|Tea||teyaku|తేయాకు
plantation|rubber|Rubber||rabbaru|రబ్బరు
spice|black_pepper|Black pepper|peppercorn|miriyalu|మిరియాలు
spice|cardamom|Cardamom||yalakulu,elakulu|యాలకులు,ఏలకులు
vegetable|tomato|Tomato|tomatoes|tamata,tamota,tamato,tomata|టమాటా,టమాట
vegetable|brinjal|Brinjal|eggplant,aubergine|vankaya|వంకాయ
vegetable|okra|Okra|ladies finger,lady finger,bhindi|bendakaya|బెండకాయ,బెండ
vegetable|potato|Potato|potatoes|bangaladumpa|బంగాళాదుంప
vegetable|onion|Onion||ullipaya,ulli|ఉల్లిపాయ,ఉల్లి
vegetable|garlic|Garlic||vellulli|వెల్లుల్లి
vegetable|cabbage|Cabbage||kyabeji|క్యాబేజీ
vegetable|cauliflower|Cauliflower||kaliflower|కాలీఫ్లవర్
vegetable|carrot|Carrot||kyaret|క్యారెట్
vegetable|beetroot|Beetroot|beet|bitroot|బీట్‌రూట్,బీట్ రూట్
vegetable|radish|Radish||mullangi|ముల్లంగి
vegetable|cucumber|Cucumber||dosakaya|దోసకాయ
vegetable|bottle_gourd|Bottle gourd||sorakaya,anapakaya|సొరకాయ,ఆనపకాయ
vegetable|bitter_gourd|Bitter gourd||kakarakaya|కాకరకాయ
vegetable|ridge_gourd|Ridge gourd||beerakaya,birakaya|బీరకాయ
vegetable|snake_gourd|Snake gourd||potlakaya|పొట్లకాయ
vegetable|pumpkin|Pumpkin||gummadi,gummadikaya|గుమ్మడి,గుమ్మడికాయ
vegetable|ash_gourd|Ash gourd|winter melon|budida gummadi|బూడిద గుమ్మడి
vegetable|ivy_gourd|Ivy gourd||dondakaya|దొండకాయ
vegetable|drumstick|Drumstick|moringa|munaga|మునగ
vegetable|cluster_beans|Cluster beans|cluster bean,guar|gorachikkudu|గోరుచిక్కుడు
vegetable|french_beans|French beans|french bean,green bean|french chikkudu|ఫ్రెంచ్ బీన్స్
vegetable|broad_beans|Broad beans|broad bean,fava bean|bakla|బాక్లా,బ్రాడ్ బీన్స్
vegetable|peas|Peas|pea,garden pea|batani,batanilu|బఠాణీ,బఠాణీలు
vegetable|capsicum|Capsicum|bell pepper|simla mirchi|సిమ్లా మిర్చి
vegetable|green_chilli|Green chilli|green chili|pachi mirapa,pachimirchi|పచ్చి మిరప,పచ్చిమిర్చి
vegetable|spinach|Spinach||palakura|పాలకూర
vegetable|amaranth|Amaranth|amaranthus|thotakura,totakura|తోటకూర
vegetable|gongura|Gongura|roselle|gogu|గోంగూర,గోగు
spice|coriander|Coriander|cilantro|kothimeera,kottimeera|కొత్తిమీర
spice|curry_leaf|Curry leaf|curry leaves|karivepaku|కరివేపాకు
spice|mint|Mint||pudina|పుదీనా
spice|ginger|Ginger||allam|అల్లం
vegetable|sweet_potato|Sweet potato||chilagadadumpa|చిలగడదుంప
vegetable|tapioca|Tapioca|cassava|karra pendalam|కర్ర పెండలం
vegetable|yam|Yam|elephant foot yam|kanda|కంద
vegetable|taro|Taro|colocasia|chamadumpa|చామదుంప
flower|marigold|Marigold||banthi,banti|బంతి
flower|jasmine|Jasmine||malle|మల్లె
flower|rose|Rose||gulabi|గులాబీ
flower|chrysanthemum|Chrysanthemum||chamanthi,chamanti|చామంతి
flower|crossandra|Crossandra||kanakambaram|కనకాంబరం
plantation|mulberry|Mulberry|sericulture|pattu aaku|మల్బరీ,పట్టు ఆకు
cereal|napier|Napier|napier grass,fodder crops|napier gaddi|నేపియర్,నేపియర్ గడ్డి
cereal|maize_fodder|Maize fodder|fodder maize|mokkajonna metha|మొక్కజొన్న మేత'''

def build():
    crops=[]
    for line in CATALOG.splitlines():
        cat,cid,en,eng,roman,te=line.split('|')
        crops.append(dict(id=cid,english_name=en,english_aliases=eng.split(',') if eng else [],
                          romanized_aliases=roman.split(','),telugu_aliases=te.split(','),category=cat))
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/crops.json').write_text(json.dumps(crops,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'js/crops-data.js').write_text('/* Generated from data/crops.json; do not edit. */\nwindow.CROP_CATALOG='+json.dumps(crops,ensure_ascii=False)+';\n',encoding='utf8')
    return crops

if __name__=='__main__':
    print('Catalog crops:',len(build()))
