# Executed verification

| suite      |   passed |   failed |
|:-----------|---------:|---------:|
| pytest     |      574 |        0 |
| Playwright |      560 |        0 |

Browser/API transport: Flask WSGI over stdio (sandbox blocks local TCP). Real API routes and model executed; no simulated predictions. Weather responses were deterministic fixtures; a separate live weather check is recorded.

| model               | features   |   test_accuracy |   test_macro_f1 |
|:--------------------|:-----------|----------------:|----------------:|
| Naive Bayes         | word       |          0.9891 |          0.9819 |
| Logistic Regression | word       |          1.0000 |          1.0000 |
| Linear SVM          | word       |          1.0000 |          1.0000 |
| Naive Bayes         | char       |          0.9743 |          0.9607 |
| Logistic Regression | char       |          1.0000 |          1.0000 |
| Linear SVM          | char       |          1.0000 |          1.0000 |
| Naive Bayes         | combined   |          0.9886 |          0.9818 |
| Logistic Regression | combined   |          1.0000 |          1.0000 |
| Linear SVM          | combined   |          1.0000 |          1.0000 |


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
