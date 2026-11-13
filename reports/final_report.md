# Telugu–English Code-Mixed NLP for Agricultural Query Intent Classification

N. Akhil (2303A51065), K. Vishwesh Reddy (2303A51057), SR University.

## Abstract

An agricultural intent-routing system was implemented using multilingual text,
TF-IDF and three linear classification families. Nine experiments compare word,
character and combined representations. The source workbook has 12625
records with 20 labels and three parallel text columns. Results below are from
the executed pipeline; template effects limit their interpretation.

## Introduction

Farmers mix Telugu script, romanized Telugu and English when asking about crops.
A topic classifier can connect such questions to simple guidance without claiming
to diagnose a plant. This project covers six requested agricultural topics plus
other agricultural topics and non-agricultural inputs.

## Dataset and methodology

NFC normalization, lowercase, Unicode letter/mark preservation, removal of URLs,
digits and punctuation, whitespace cleanup, and a small explicit romanized variant
dictionary are used. No stopwords are removed. Word TF-IDF 1–2 grams (20,000 features)
and char_wb TF-IDF 2–5 grams (25,000 features) are compared separately and combined.
TF-IDF is fitted inside training folds. MultinomialNB alpha is tuned over [0.25,1];
Logistic Regression C over [1,4]; LinearSVC C over [0.5,2]. LR/SVM use balanced weights.
Five-fold stratified group CV uses original workbook training text only; final fits
add synthetic examples. SVM uses sigmoid CalibratedClassifierCV with five group folds.
Seed 42 is used wherever randomness is exposed. Test evaluation occurs once after
selection for all nine prespecified experiments. Test is never used for tuning.
The browser uses the exact exported winning TF-IDF/weights/calibration, rather than
claiming that a centroid is the same model. Export parity is tested numerically.

Workbook versions share origin IDs, exact duplicate equivalence and cosine >=0.92
char_wb 3–5 near-duplicate connected components. Seven stratified group folds give
five train, one validation, one test (approximate 71/14/14). The recorded sizes are
{'train': 36443, 'validation': 4101, 'test': 3850, 'synthetic_training': 16206}. Graph vectorization uses the full corpus only for leakage auditing; learned
prediction features never use held-out text. All three parallel query versions
are used but are not independent observations. The workbook contains 20 intents;
eight labels result from merging disease/pest, merging fertilizer/nutrition,
retaining water/price/weather/schemes, grouping the other 12 as other_agri and
adding a clearly synthetic out_of_scope class. All original labels are reported.

Fifteen independently authored templates per crop per core intent improve missing
coverage and English/romanized/Telugu balance for all 97 catalog entries. Generated
rows are explicitly source=synthetic in data/synthetic_augmented.csv and train only.
The minimum is 15 training rows per crop/intent; actual counts appear in coverage.
Non-agricultural training examples are generated separately. No synthetic row is
in validation or the workbook test. Handwritten is a separate authored challenge
set, including synthetic out-of-scope text, never used for fitting or selecting.


## Experiments and results

Primary performance benchmark: **319 separately authored unseen questions**.
Raw selected-model accuracy: **0.7900**, macro-F1: **0.8002**.
The deployed confidence/context guard and slot lexicon are evaluated separately:
accuracy **0.8339**, macro-F1 **0.8388**,
clarification rate **0.3824**. A routed label is not necessarily
an answered question: missing crop/symptom/location still asks for clarification.
These are project-authored synthetic challenges, not independently collected farmer data.
No challenge query trains or selects a model. Model selection remains validation-only.

Group-disjoint English+code-mixed to Telugu-column transfer accuracy:
**0.5470**, macro-F1 **0.1164**.
Code-mixed training contains some Telugu. Train/test origins and near-duplicate groups are disjoint.

Within-intent problem classifier workbook test accuracy:
**0.9769**, separately authored problem challenge accuracy:
**1.0000** (49 queries).
Problem predictions reproduce workbook wording, not confirmed diagnoses.

Workbook results below are secondary diagnostics because the original parallel text
is highly templated. High workbook scores are not a field-performance estimate.

The selected estimator is **Logistic Regression / word**, selected by validation macro-F1
(1.0000). Workbook test accuracy is 1.0000,
macro-F1 1.0000, weighted-F1 1.0000.
The separately authored 150-query benchmark accuracy is 0.8733
and macro-F1 is 0.8682.

| model               | features   |   cv_macro_f1 |   cv_std |   validation_macro_f1 |   test_accuracy |   test_macro_f1 |
|:--------------------|:-----------|--------------:|---------:|----------------------:|----------------:|----------------:|
| Naive Bayes         | word       |        0.9962 |   0.0015 |                0.9759 |          0.9891 |          0.9819 |
| Logistic Regression | word       |        1.0000 |   0.0000 |                1.0000 |          1.0000 |          1.0000 |
| Linear SVM          | word       |        1.0000 |   0.0000 |                1.0000 |          1.0000 |          1.0000 |
| Naive Bayes         | char       |        0.9911 |   0.0009 |                0.9586 |          0.9743 |          0.9607 |
| Logistic Regression | char       |        1.0000 |   0.0000 |                1.0000 |          1.0000 |          1.0000 |
| Linear SVM          | char       |        1.0000 |   0.0000 |                1.0000 |          1.0000 |          1.0000 |
| Naive Bayes         | combined   |        0.9969 |   0.0013 |                0.9736 |          0.9886 |          0.9818 |
| Logistic Regression | combined   |        1.0000 |   0.0000 |                1.0000 |          1.0000 |          1.0000 |
| Linear SVM          | combined   |        1.0000 |   0.0000 |                1.0000 |          1.0000 |          1.0000 |


## Error analysis

The complete misclassified workbook queries are in reports/error_analysis.csv.
Script and crop-category scores and handwritten failures are in
reports/error_analysis.md. See the recorded class-pair counts before attributing
errors to symptoms or spelling. The handwritten benchmark contains short,
typo-bearing and long queries and was not used to choose the model.

## Deployment and verification

Flask serves the saved estimator; the browser reproduces its learned weights.
Pytest checks data separation, aliases, preprocessing, regression examples and
API validation. Playwright exercises every page and every crop calculator.
The generated test summaries record executed counts and failures independently
of model metrics. The examiner page exposes results without cluttering farmer pages.
Local TCP was blocked by the execution sandbox, so browser/API integration used
the real Flask application via a stdio WSGI bridge. This verifies route/model
behavior and browser integration, but does not claim a successful TCP network
connection inside that sandbox. A separate live Open-Meteo check is recorded.

## Limitations and ethics

The workbook's collection method and licence are not established. Its regular
phrasing and implausible stage/problem combinations suggest template effects, so
high workbook scores are not estimates of field performance. Cross-language
translations are correlated. Romanized vs English is a heuristic. Rare crops have
synthetic language coverage, not independently validated farmer data. Disease and
nutrition symptoms overlap; this is an intent router, not a diagnosis tool.
Ambiguous crops (Citrus, yellow/pasupu, regional bean names) require clarification.
Out-of-scope test performance is available only on authored synthetic examples;
high confidence does not establish correctness. Broad other_agri loses subtype
detail. Confidence thresholds 0.55/margin 0.10 are design defaults and require
field calibration. Conservative crop guides use officer referral where a numeric
crop-specific recommendation was not verified; no universal dose is invented.
Prices are historical MSP references. Optional data.gov.in results retain date and market; a missing key or upstream failure yields no reported price. Weather requires
internet and is a nearby-place forecast, not a field measurement.

IndicBERT: NOT RUN. Torch, Transformers and pretrained weights are not available;
the optional extension is deferred and no neural performance is claimed.
No fake subset result or comparison row is included. The executable notebooks/indicbert_colab.ipynb is provided for a GPU Colab run, with no prefilled outputs.

Questions stay in browser storage for optional history. The local API processes
queries in memory and does not retain query bodies. Weather/city lookup sends
location text/coordinates to Open-Meteo; speech follows browser provider rules.
Do not enter personal IDs or banking information. Clear history on shared devices.
Consent, dataset licensing, Telugu agronomist review, field evaluation, and a
production WSGI server would be needed before public agricultural use.


## Conclusion

A reproducible baseline, broad entity catalog, transparent data policy and usable
offline/online interface were delivered. Workbook accuracy and authored challenge
accuracy are reported separately because template-rich data is easier than natural
farmer language. Numeric recommendations are limited to verified references.

## Future work

Collect consented independent farmer questions; ask Telugu agronomists to review
aliases and annotations; evaluate by village/season; improve transliteration and
open-set rejection; validate retrieval against local extension material; and train
an IndicBERT/MuRIL baseline only when compute and pretrained weights are available.

## References

See reports/sources.md for verified agriculture, price, weather and district links.
Dataset authorship/licence must be established with its provider.


## Direct answers and robustness upgrade

The home page now extracts crop, symptom, observations, growth stage and district.
Shared `data/slots.json` drives Python and JavaScript. Crop noun phrases work from
all catalog aliases. Another crop overrides ambiguous pasupu; bare pasupu is yellow,
while an explicit turmeric reference without colour context is a crop. Yellowing is
not a diagnosis. Flower drop is retained as an observation rather than forced into
an unsupported disease. Home answers reuse the reviewed disease/care entries;
unknown crop-specific advice explicitly says it is unavailable and gives the
agriculture officer and Kisan Call Centre 1800-180-1551 contact. Missing slots have
crop/symptom tap choices. Guide links carry crop, symptom, stage and district and
automatically show the corresponding results. The old selection controls remain.
Fertilizer and water guidance do not invent a numerical prescription from a stage.

The original `problem`, `growth_stage`, `location` fields are retained in split CSVs.
Seven within-intent Logistic Regression models predict problem wording using
combined TF-IDF, fixed C=2 and five original-training group folds. Typo descendants
retain their originating group and problem; generic coverage examples are never
assigned guessed problem labels. Problem probabilities/weights are exported for
browser parity. The 49-query authored problem set covers only a subset of the 104
source problem names and contains explicit problem terminology, so a high score
there is not field validation.

Training-only typo augmentation contains 7356 rows: character swap/drop and
vowel doubling in Latin text, preserving Telugu combining marks. Near-held-out
matches are purged. The second authored challenge excludes one normalized overlap
with v1, leaving 319 queries. The original 150-query benchmark
remains separately reported. Prompt-supplied regression examples occur in the new
challenge, so deployed rule scores must not be interpreted as independent field
validation. No benchmark text is used for ML fitting or model selection.

### Optional reported mandi prices

The fictional sample-price column was removed. Dated 2025-26 MSP remains visible.
GET `/prices` accepts state, district, market and commodity text filters, limits the
upstream response to 100 records, and caches successful responses for ten minutes.
Every returned price retains reporting date, market, commodity and published unit.
Missing key, malformed/incomplete data and network failures return no invented rate.
API keys never appear in browser files or error messages. In PowerShell:

```powershell
$env:DATA_GOV_IN_API_KEY = 'your-own-data-gov-in-key'
python app.py
```

The key must come from your data.gov.in account. No real key was supplied here;
only fixture-based cache/filter/error tests and missing-key behavior were executed.
Verify a real keyed request manually before describing the integration as live.
Official resource: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
Official market portal: https://agmarknet.gov.in/

### Voice and optional neural model

The speak button and microphone activation were removed as requested. A compatibility
error-message renderer is tested for simulated speech error codes; it does not access
a microphone. No real-phone microphone test is required for the current text-only UI.
IndicBERT/MuRIL remains NOT RUN here: installed torch and transformers availability
is recorded in reports/robustness_metrics.json. Open notebooks/indicbert_colab.ipynb
in Colab, select a GPU, upload the complete project ZIP, and run its cells to actually
fine-tune/evaluate. It contains no precomputed neural scores or execution outputs.

Detailed measured primary, deployed-policy and cross-script results appear in
reports/robustness.md; problem scores appear in reports/problem_model.md. All nine
raw-model results are in reports/model_comparison.csv. The selected model is still
chosen by validation macro-F1, never by either authored test set.


Problem evaluation supplies the true intent for each example; this is conditional problem accuracy, not end-to-end accuracy.
See reports/answer_policy.md for ambiguity, confidence, missing-slot, price and voice decisions.


## Executed verification for this upgrade

| Suite      |   Passed |   Failed |
|:-----------|---------:|---------:|
| pytest     |      574 |        0 |
| Playwright |      560 |        0 |

| Evaluation                                          |   accuracy |   macro_f1 |
|:----------------------------------------------------|-----------:|-----------:|
| 319 authored queries: raw selected model            |     0.7900 |     0.8002 |
| 319 authored queries: deployed guards/slots         |     0.8339 |     0.8388 |
| Group-disjoint Telugu transfer                      |     0.5470 |     0.1164 |
| Conditional problem model: workbook test            |     0.9769 |     0.9768 |
| Conditional problem model: 49 named-problem queries |     1.0000 |     1.0000 |

Browser/API transport: Flask WSGI over stdio (sandbox blocks local TCP). The actual Flask routes and saved models executed. Price/network failure tests used explicit fixtures; no actual keyed mandi rate was retrieved. All 43 slot-regression queries passed in Python and in direct-answer/prefilled-guide browser flows. All 63 intent export parity cases and 21 problem export parity cases passed within 1e-6. The speak button is absent; simulated error messages were tested without microphone access.

The validation-selected word model was retained rather than selecting on the new challenge. Character and combined Logistic Regression candidates each scored 88.09% on that authored set; the full nine-experiment table is retained, without treating this test as validation. The cross-script macro-F1 of 0.1164 is a substantial limitation.
