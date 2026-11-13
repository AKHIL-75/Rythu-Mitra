# Dataset audit

Workbook: `telugu_english_agriculture_CLEAN_dataset.xlsx`

Sheets: ['Sheet1']

Shape: (12625, 10)


## Columns, types and null counts

query_id                  object
query_telugu              object
query_english             object
query_code_mixed          object
intent                    object
crop                      object
problem                   object
location                  object
growth_stage              object
expected_response_type    object

query_id                  0
query_telugu              0
query_english             0
query_code_mixed          0
intent                    0
crop                      0
problem                   0
location                  0
growth_stage              0
expected_response_type    0


Full-row duplicates: 0


## intent distribution

intent
fertilizer_recommendation    634
storage                      634
crop_selection               634
weather_related              634
organic_farming              633
weed_management              632
crop_planting                632
yield_improvement            632
seed_selection               632
harvesting                   631
soil_management              631
disease_management           631
pest_management              630
post_harvest_management      630
general_agriculture          630
market_price                 629
crop_nutrition               629
government_scheme            629
farming_equipment            629
irrigation                   629


## crop distribution

crop
Mango          557
Okra           548
Brinjal        532
Onion          526
Cauliflower    520
Cotton         520
Citrus         513
Groundnut      510
Tomato         509
general        507
Chilli         505
Bengal gram    503
Banana         501
Sunflower      500
Sesame         499
Sugarcane      497
Black gram     495
Papaya         494
Cabbage        491
Soybean        490
Rice           489
Maize          487
Turmeric       486
Green gram     476
Red gram       470


## problem distribution

problem
not specified                      382
crop calendar                      183
micronutrient spray                173
organic pest control               169
planting time                      169
value addition                     168
grain storage problem              167
high profit crop                   166
loan scheme                        165
general farming advice             165
drone spraying                     164
tractor subsidy                    164
stunted growth                     164
poor germination                   162
pest in storage                    162
nutrient deficiency symptoms       161
grading and packing                160
current market price               160
herbicide selection                159
Rythu Bandhu scheme                158
transplanting                      157
early harvesting                   156
weed control                       156
crop rotation planning             156
harvesting time                    155
yield improvement tips             155
organic fertilizer                 155
mandi price                        152
price fluctuation                  152
zinc deficiency                    152
crop insurance scheme              150
natural farming method             150
weed growth                        150
delayed harvest                    149
vermicompost use                   149
harvest loss                       149
parthenium weed                    148
best crop for this season          148
transport damage                   147
spacing between plants             146
suitable crop for soil             144
direct sowing method               144
storage of seeds                   143
post-harvest losses                142
sprayer machine                    142
subsidy scheme                     142
moisture damage in storage         142
harvesting machine                 141
soil salinity                      139
selling rate                       139
new farming technology             135
low yield                          132
seed quality                       130
soil erosion                       129
leaf yellowing due to nutrition    127
farming query                      126
seed rate                          124
excess water                       121
low organic matter                 121
unseasonal rain                    120
hybrid seed                        120
disease resistant variety          118
soil testing                       116
good seed variety                  113
waterlogging                       112
drought                            109
heat wave effect                   109
water shortage                     107
drought stress                     105
soil acidity                       103
hailstorm damage                    93
frost damage                        93
heavy rainfall damage               91
basal dose                          88
drip irrigation                     87
irrigation schedule                 81
nitrogen deficiency                 80
fertilizer dosage                   80
potassium deficiency                80
phosphorus deficiency               79
low soil fertility                  74
micronutrient deficiency            69
blight                              69
bacterial disease                   67
mealybug                            66
black spots on leaves               66
top dressing                        65
powdery mildew                      65
fungal infection                    61
wilt                                61
fruit borer                         61
blast disease                       59
leaf spot                           58
pest attack                         58
pod borer                           56
leaf folder                         54
whitefly                            54
mites                               53
aphids                              53
viral disease                       53
root rot                            52
army worm                           52
stem borer                          51
thrips                              48


## location distribution

location
Not specified    1641
Guntur            521
Mahabubabad       512
Anantapur         511
Nizamabad         500
Khammam           500
Visakhapatnam     500
Karimnagar        486
Hanamkonda        484
Jangaon           484
Suryapet          483
Warangal          483
Vijayawada        481
Mahabubnagar      477
Kurnool           477
Nalgonda          471
Hyderabad         468
Tirupati          465
Medak             457
Kamareddy         457
Mulugu            455
Siddipet          452
Adilabad          452
Sangareddy        408


## growth_stage distribution

growth_stage
Not specified    1639
Flowering        1433
Germination      1413
Harvesting       1393
Seedling         1393
Post-harvest     1379
Fruiting         1332
Sowing           1327
Vegetative       1316


## expected_response_type distribution

expected_response_type
recommendation    1890
explanation       1569
procedure         1558
suggestion        1549
information       1529
steps             1515
advice            1515
solution          1500


## query_telugu

```json
{
  "empty": 0,
  "duplicates": 3249,
  "normalized_duplicates": 3429,
  "conflicting_label_queries": 0,
  "script_counts": {
    "telugu": 10037,
    "mixed": 2588
  },
  "word_length": {
    "count": 12625.0,
    "mean": 7.811326732673267,
    "std": 4.058922991647555,
    "min": 2.0,
    "25%": 4.0,
    "50%": 8.0,
    "75%": 9.0,
    "max": 21.0
  },
  "script_share_percent": {
    "telugu": 79.50099009900991,
    "mixed": 20.4990099009901
  }
}
```


## query_english

```json
{
  "empty": 0,
  "duplicates": 3387,
  "normalized_duplicates": 3387,
  "conflicting_label_queries": 0,
  "script_counts": {
    "english": 12625
  },
  "word_length": {
    "count": 12625.0,
    "mean": 9.041663366336634,
    "std": 4.809554985597159,
    "min": 2.0,
    "25%": 5.0,
    "50%": 9.0,
    "75%": 11.0,
    "max": 23.0
  },
  "script_share_percent": {
    "english": 100.0
  }
}
```


## query_code_mixed

```json
{
  "empty": 0,
  "duplicates": 2871,
  "normalized_duplicates": 2871,
  "conflicting_label_queries": 0,
  "script_counts": {
    "mixed": 12022,
    "romanized": 603
  },
  "word_length": {
    "count": 12625.0,
    "mean": 8.249346534653466,
    "std": 3.4226823117227276,
    "min": 3.0,
    "25%": 7.0,
    "50%": 8.0,
    "75%": 9.0,
    "max": 18.0
  },
  "script_share_percent": {
    "mixed": 95.22376237623762,
    "romanized": 4.776237623762376
  }
}
```


## Decisions and limitations

All 20 source intents are retained: disease_management/pest_management → crop_disease;
fertilizer_recommendation/crop_nutrition → fertilizer; weather_related → weather;
government_scheme → govt_scheme; irrigation and market_price retain their names.
The other 12 intents (all listed above) form other_agri, rather than being discarded.
Non-agricultural examples form a separately marked synthetic out_of_scope class.
The three query columns are parallel versions, not independent farmer observations.
Their provenance and authorship are not documented in the workbook: “workbook” does
not mean verified real-world farmer text. Many queries are visibly templated and
some growth-stage/problem pairings are implausible. No unsupported relabeling is done.
Conflicting normalized labels are quarantined in data/label_conflicts.csv.
Near-duplicates are conservatively defined by char_wb 3–5 TF-IDF cosine >= 0.92;
connected components and parallel versions stay in one split and one CV fold.
Splitting is performed before coverage augmentation. Synthetic rows never enter
validation or the workbook test. Evaluation of out_of_scope is separately labelled
synthetic because no original out-of-scope records exist.
Script labels are observable Telugu/Latin mixtures; romanized vs English is an
explicit vocabulary heuristic, not a language-identification ground truth.
Horticulture and organic_farming are represented; livestock/dairy/poultry/fisheries
do not have explicit source labels, so specialist advice for those is not claimed.
Near-duplicate and split statistics are appended after grouping by run_all.py.

## Leakage grouping result

Unique queries: 28188. Near-duplicate pairs (cosine ≥ 0.92): 3174. Connected components including parallel versions: 7548.

| intent       |   test |   train |   validation |
|:-------------|-------:|--------:|-------------:|
| crop_disease |    481 |    2193 |          477 |
| fertilizer   |    412 |    2149 |          324 |
| govt_scheme  |    167 |     984 |          236 |
| irrigation   |    193 |    1034 |          272 |
| market_price |    183 |     984 |          197 |
| other_agri   |   2250 |   11779 |         2370 |
| weather      |    164 |    1114 |          225 |

Seven stratified group folds allocate five to training, one validation, one test. Ratios are approximate because connected components are indivisible. Grouping TF-IDF is an unsupervised audit instrument only; prediction TF-IDF is fitted independently inside each training fold.

## Merged-class balance

| intent       |   deduplicated_queries |
|:-------------|-----------------------:|
| other_agri   |                  16399 |
| crop_disease |                   3151 |
| fertilizer   |                   2885 |
| weather      |                   1503 |
| irrigation   |                   1499 |
| govt_scheme  |                   1387 |
| market_price |                   1364 |

Largest/smallest farm class ratio: 12.023. Balanced class weights are used for LR/SVM; NB retains empirical priors.
