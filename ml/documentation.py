"""Write documentation from recorded measurements, never invented scores."""
import json
import platform
from pathlib import Path
import pandas as pd
import sklearn

ROOT=Path(__file__).resolve().parents[1]

def write_docs(m):
    comp=pd.DataFrame(m['comparison'])
    table=comp[['model','features','cv_macro_f1','cv_std','validation_macro_f1','test_accuracy','test_macro_f1']].to_markdown(index=False,floatfmt='.4f')
    s=m['selected'];spl=m['split_counts']
    common=f'''The selected estimator is **{s['model']} / {s['features']}**, selected by validation macro-F1
({s['validation_macro_f1']:.4f}). Workbook test accuracy is {s['test_accuracy']:.4f},
macro-F1 {s['test_macro_f1']:.4f}, weighted-F1 {s['test_weighted_f1']:.4f}.
The separately authored 150-query benchmark accuracy is {m['handwritten']['accuracy']:.4f}
and macro-F1 is {m['handwritten']['macro_f1']:.4f}.

{table}
'''
    if 'robustness' in m:
        r=m['robustness'];p=m['problem_model']
        primary={row['experiment']:row for row in r['raw_models']}
        for row in m['comparison']:
            row['handwritten_v2_accuracy']=primary[row['key']]['accuracy']
            row['handwritten_v2_macro_f1']=primary[row['key']]['macro_f1']
        m['decision_threshold']=.55;m['margin_threshold']=.10
        (ROOT/'ml/models/metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
        (ROOT/'js/metrics-data.js').write_text('window.MODEL_METRICS='+json.dumps(m,ensure_ascii=False)+';',encoding='utf8')
        pd.DataFrame(m['comparison']).to_csv(ROOT/'reports/model_comparison.csv',index=False)
        primary_text=(ROOT/'reports/robustness.md').read_text(encoding='utf8')
        workbook_columns=['model','features','cv_macro_f1','cv_std','validation_macro_f1','test_accuracy','test_macro_f1']
        workbook_table=pd.DataFrame(m['comparison'])[workbook_columns].to_markdown(index=False,floatfmt='.4f')
        (ROOT/'reports/model_comparison.md').write_text('# Model comparison — authored challenge is primary\n\n'+primary_text+'\n\n## Secondary templated-workbook diagnostic\n\n'+workbook_table+'\n\nThe deployed model remains the validation-selected word Logistic Regression; the authored challenge was not used to select it. All nine saved candidates remain available for research.\n\n'+(ROOT/'reports/problem_model.md').read_text(encoding='utf8'),encoding='utf8')
        common=f'''Primary performance benchmark: **{r['rows']} separately authored unseen questions**.
Raw selected-model accuracy: **{r['selected_raw']['accuracy']:.4f}**, macro-F1: **{r['selected_raw']['macro_f1']:.4f}**.
The deployed confidence/context guard and slot lexicon are evaluated separately:
accuracy **{r['deployed_rules']['accuracy']:.4f}**, macro-F1 **{r['deployed_rules']['macro_f1']:.4f}**,
clarification rate **{r['clarification_rate']:.4f}**. A routed label is not necessarily
an answered question: missing crop/symptom/location still asks for clarification.
These are project-authored synthetic challenges, not independently collected farmer data.
No challenge query trains or selects a model. Model selection remains validation-only.

Group-disjoint English+code-mixed to Telugu-column transfer accuracy:
**{r['cross_script']['accuracy']:.4f}**, macro-F1 **{r['cross_script']['macro_f1']:.4f}**.
Code-mixed training contains some Telugu. Train/test origins and near-duplicate groups are disjoint.

Within-intent problem classifier workbook test accuracy:
**{p['summary']['test']['accuracy']:.4f}**, separately authored problem challenge accuracy:
**{p['summary']['handwritten']['accuracy']:.4f}** ({p['summary']['handwritten']['rows']} queries).
Problem predictions reproduce workbook wording, not confirmed diagnoses.

Workbook results below are secondary diagnostics because the original parallel text
is highly templated. High workbook scores are not a field-performance estimate.

'''+common
    methodology=f'''NFC normalization, lowercase, Unicode letter/mark preservation, removal of URLs,
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
{spl}. Graph vectorization uses the full corpus only for leakage auditing; learned
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
'''
    limitations='''The workbook's collection method and licence are not established. Its regular
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
'''
    readme=f'''# Telugu–English Code-Mixed NLP for Agricultural Query Intent Classification

Rythu Mitra, SR University. Team: N. Akhil (2303A51065), K. Vishwesh Reddy (2303A51057).
Classify Telugu, romanized Telugu, English and mixed farmer questions and provide
simple topic guidance with a 97-entry crop detector.

## Install and run

```powershell
python -m pip install -r ml/requirements.txt
python ml/run_all.py
python app.py
```

Open http://127.0.0.1:5000/ for the API-backed site. Training is already completed;
the saved model can be served immediately. To open the offline site on Windows:

```powershell
Start-Process index.html
python ml/predict.py "naaku vari ki leaf spot vachindi"
python -m pytest -q
node tests/frontend.cjs
python ml/check_all.py
```

The delivered environment used local .vendor Flask dependencies after ordinary
pip DNS access failed. Entry points load that directory automatically if present.
Fresh installs should use the requirements file. Browser tests use Playwright;
run `npm install --no-save playwright` and `npx playwright install chromium` if no
existing Playwright installation is available. Tests find PLAYWRIGHT_MODULE or a
runtime installation and use local Chrome if bundled Chromium is unavailable.
`python ml/check_all.py` runs both suites, starts a temporary local API if needed,
and prints the final test/model tables. `ml/requirements-lock.txt` records the
executed Python package versions. `python ml/package_project.py` creates the
portable source/data/model/report ZIP, excluding caches and local dependencies.

## Folder structure

| Path | Purpose |
|---|---|
| `ml/` | audit, grouping, preprocessing, training, exact export, CLI |
| `ml/models/` | joblib model, label map, metrics |
| `data/` | shared crop aliases, split CSVs, synthetic and handwritten text |
| `reports/` | audit, coverage, comparison, confusion PNGs, errors, final report |
| `app.py` | Flask /health and validated POST /predict, static page serving |
| `js/` | original UI and guidance, shared entities and exact offline inference |
| `model-report.html` | examiner statistics, plots, per-class scores and demo |
| `tests/` | pytest, Playwright, alias parity and local links |

## Dataset and experiment policy

{methodology}

## Measured comparison

{common}

CV mean/std above use five original-only training folds; validation and test use
models finally fitted with training-only synthetic augmentation. All detailed
precision/recall/F1 values are in reports/model_comparison.csv and metrics.json.
An empty out_of_scope true row in workbook confusion matrices is intentional.

## Interface and content

The server returns topic, confidence, top three topics, crop, script type and a
clarification flag. Empty/non-text/over-800-character input is rejected; unknown
or uncertain input asks for more detail. HTTP failure falls back to the identical
learned browser estimator. Plain file opening works without fetch for the model,
catalog and report data. Existing history, clear, printing, symptoms,
profit calculation, scheme enquiries and language controls remain available.
Every crop is selectable. Missing verified fertilizer/water doses show an officer
referral instead of fabricated calculations; the profit calculator accepts user
prices. Disease symptoms outside the verified guide subset are inspection cues,
not claims that a named disease affects every species. Sources and limitations
are shown beside the content. See reports/sources.md.

## Limitations, ethics, privacy and optional neural model

{limitations}

## Reproduction environment

Python {platform.python_version()}, scikit-learn {sklearn.__version__}. Only load
trusted joblib artifacts; versions should match the training environment.
Run reports/test_summary.json and reports/frontend_results.json describe checks
actually performed. The speak control was removed. Compatibility speech-error messages are tested without recording. OS print dialog, and real farmer
acceptance testing require manual interaction and are not claimed as automated.

The execution sandbox blocked local TCP (WinError 10013 / network access denied).
API unit tests used Flask's test client; browser/API integration used
tests/wsgi_bridge.py to execute the actual Flask routes and saved model over
stdio, with Playwright routing the responses. Predictions were not mocked.
The file-mode site was opened directly in headless Chromium. TCP serving should
be checked by running app.py in a normal local terminal outside the sandbox.
Weather browser scenarios used deterministic fixtures; the separate live
Open-Meteo probe returned HTTP 200 and seven daily values, recorded in
reports/weather_live_check.json. See reports/verification.md for executed counts.
'''
    (ROOT/'README.md').write_text(readme,encoding='utf8')
    report=f'''# Telugu–English Code-Mixed NLP for Agricultural Query Intent Classification

N. Akhil (2303A51065), K. Vishwesh Reddy (2303A51057), SR University.

## Abstract

An agricultural intent-routing system was implemented using multilingual text,
TF-IDF and three linear classification families. Nine experiments compare word,
character and combined representations. The source workbook has {m['dataset']['rows']}
records with 20 labels and three parallel text columns. Results below are from
the executed pipeline; template effects limit their interpretation.

## Introduction

Farmers mix Telugu script, romanized Telugu and English when asking about crops.
A topic classifier can connect such questions to simple guidance without claiming
to diagnose a plant. This project covers six requested agricultural topics plus
other agricultural topics and non-agricultural inputs.

## Dataset and methodology

{methodology}

## Experiments and results

{common}

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

{limitations}

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
'''
    (ROOT/'reports/final_report.md').write_text(report,encoding='utf8')

    if 'robustness' in m:
        import importlib.util
        typo_rows=len(pd.read_csv(ROOT/'data/typo_augmented.csv'))
        extra=f"""

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

Training-only typo augmentation contains {typo_rows} rows: character swap/drop and
vowel doubling in Latin text, preserving Telugu combining marks. Near-held-out
matches are purged. The second authored challenge excludes one normalized overlap
with v1, leaving {m['robustness']['rows']} queries. The original 150-query benchmark
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
"""
        for name in ['README.md','reports/final_report.md']:
            with (ROOT/name).open('a',encoding='utf8') as f:f.write(extra)
