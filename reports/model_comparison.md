# Model comparison — authored challenge is primary

# Primary robustness evaluation

All 319 literal queries were authored for this project; this is a synthetic challenge, not a representative farmer sample. Exact overlaps with v1 are excluded and recorded separately.

| experiment                   |   accuracy |   macro_precision |   macro_recall |   macro_f1 |   weighted_precision |   weighted_recall |   weighted_f1 |
|:-----------------------------|-----------:|------------------:|---------------:|-----------:|---------------------:|------------------:|--------------:|
| naive_bayes_word             |     0.7273 |            0.7549 |         0.7262 |     0.7190 |               0.7543 |            0.7273 |        0.7195 |
| logistic_regression_word     |     0.7900 |            0.8420 |         0.7895 |     0.8002 |               0.8420 |            0.7900 |        0.8005 |
| linear_svm_word              |     0.8276 |            0.8379 |         0.8271 |     0.8269 |               0.8376 |            0.8276 |        0.8271 |
| naive_bayes_char             |     0.8339 |            0.8452 |         0.8329 |     0.8260 |               0.8448 |            0.8339 |        0.8264 |
| logistic_regression_char     |     0.8809 |            0.8993 |         0.8803 |     0.8833 |               0.8992 |            0.8809 |        0.8836 |
| linear_svm_char              |     0.8621 |            0.8668 |         0.8613 |     0.8578 |               0.8667 |            0.8621 |        0.8582 |
| naive_bayes_combined         |     0.8370 |            0.8495 |         0.8362 |     0.8298 |               0.8491 |            0.8370 |        0.8301 |
| logistic_regression_combined |     0.8809 |            0.9066 |         0.8803 |     0.8848 |               0.9064 |            0.8809 |        0.8851 |
| linear_svm_combined          |     0.8746 |            0.8801 |         0.8740 |     0.8711 |               0.8799 |            0.8746 |        0.8714 |

## Deployed guard/slot policy (reported separately from raw ML)

|                               |   accuracy |   macro_precision |   macro_recall |   macro_f1 |   weighted_precision |   weighted_recall |   weighted_f1 |
|:------------------------------|-----------:|------------------:|---------------:|-----------:|---------------------:|------------------:|--------------:|
| raw selected model            |     0.7900 |            0.8420 |         0.7895 |     0.8002 |               0.8420 |            0.7900 |        0.8005 |
| deployed guard + slot lexicon |     0.8339 |            0.8697 |         0.8344 |     0.8388 |               0.8708 |            0.8339 |        0.8393 |

Clarification rate: 0.3824451410658307. These thresholds and lexicons are design choices, not benchmark-tuned estimates of field performance.

## Cross-script transfer

{
  "train_rows": 13631,
  "test_rows": 1256,
  "accuracy": 0.5469745222929936,
  "macro_precision": 0.10175180783384462,
  "macro_recall": 0.1432919297621518,
  "macro_f1": 0.11639250294712479,
  "weighted_precision": 0.3562858879154522,
  "weighted_recall": 0.5469745222929936,
  "weighted_f1": 0.4289598435345906,
  "policy": "Original training groups, English+code-mixed columns only; original held-out test groups, Telugu column only. Code-mixed training can contain Telugu. Parallel translations never cross groups."
}

IndicBERT: NOT RUN. See the executable Colab notebook.


## Secondary templated-workbook diagnostic

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

The deployed word Logistic Regression was selected by validation before evaluating these authored challenges. Character/combined candidates remain reported; the challenge did not choose deployment.

# Within-intent problem model

| intent       |   classes |   train_rows |   cv_macro_f1 |   cv_std |   validation_accuracy |   validation_macro_precision |   validation_macro_recall |   validation_macro_f1 |   validation_weighted_precision |   validation_weighted_recall |   validation_weighted_f1 |   test_accuracy |   test_macro_precision |   test_macro_recall |   test_macro_f1 |   test_weighted_precision |   test_weighted_recall |   test_weighted_f1 |   handwritten_accuracy |   handwritten_macro_precision |   handwritten_macro_recall |   handwritten_macro_f1 |   handwritten_weighted_precision |   handwritten_weighted_recall |   handwritten_weighted_f1 |
|:-------------|----------:|-------------:|--------------:|---------:|----------------------:|-----------------------------:|--------------------------:|----------------------:|--------------------------------:|-----------------------------:|-------------------------:|----------------:|-----------------------:|--------------------:|----------------:|--------------------------:|-----------------------:|-------------------:|-----------------------:|------------------------------:|---------------------------:|-----------------------:|---------------------------------:|------------------------------:|--------------------------:|
| crop_disease |        22 |         2773 |        0.9158 |   0.0141 |                0.9266 |                       0.9062 |                    0.9264 |                0.9140 |                          0.9115 |                       0.9266 |                   0.9163 |          0.9688 |                 0.9155 |              0.9498 |          0.9306 |                    0.9465 |                 0.9688 |             0.9565 |                 1.0000 |                        1.0000 |                     1.0000 |                 1.0000 |                           1.0000 |                        1.0000 |                    1.0000 |
| fertilizer   |        13 |         2707 |        0.9144 |   0.0053 |                0.9815 |                       0.9022 |                    0.9231 |                0.9118 |                          0.9655 |                       0.9815 |                   0.9729 |          0.9830 |                 0.9130 |              0.9231 |          0.9179 |                    0.9668 |                 0.9830 |             0.9747 |                 1.0000 |                        1.0000 |                     1.0000 |                 1.0000 |                           1.0000 |                        1.0000 |                    1.0000 |
| govt_scheme  |         5 |         1225 |        0.8280 |   0.0864 |                0.9746 |                       0.7755 |                    0.8000 |                0.7870 |                          0.9523 |                       0.9746 |                   0.9627 |          0.9701 |                 0.7912 |              0.7871 |          0.7888 |                    0.9649 |                 0.9701 |             0.9671 |                 1.0000 |                        1.0000 |                     1.0000 |                 1.0000 |                           1.0000 |                        1.0000 |                    1.0000 |
| irrigation   |         7 |         1318 |        0.8441 |   0.0047 |                0.9632 |                       0.8225 |                    0.8522 |                0.8365 |                          0.9365 |                       0.9632 |                   0.9492 |          0.9689 |                 0.8429 |              0.8393 |          0.8401 |                    0.9705 |                 0.9689 |             0.9688 |                 1.0000 |                        1.0000 |                     1.0000 |                 1.0000 |                           1.0000 |                        1.0000 |                    1.0000 |
| market_price |         5 |         1269 |        0.7813 |   0.0151 |                0.9594 |                       0.7748 |                    0.7892 |                0.7813 |                          0.9410 |                       0.9594 |                   0.9496 |          0.9563 |                 0.7756 |              0.7909 |          0.7830 |                    0.9357 |                 0.9563 |             0.9457 |                 1.0000 |                        1.0000 |                     1.0000 |                 1.0000 |                           1.0000 |                        1.0000 |                    1.0000 |
| other_agri   |        51 |        14896 |        0.9647 |   0.0017 |                0.9738 |                       0.9535 |                    0.9804 |                0.9662 |                          0.9501 |                       0.9738 |                   0.9614 |          0.9787 |                 0.9593 |              0.9804 |          0.9694 |                    0.9589 |                 0.9787 |             0.9684 |                 1.0000 |                        1.0000 |                     1.0000 |                 1.0000 |                           1.0000 |                        1.0000 |                    1.0000 |
| weather      |         7 |         1403 |        0.8432 |   0.0219 |                0.9600 |                       0.8336 |                    0.8571 |                0.8448 |                          0.9236 |                       0.9600 |                   0.9410 |          1.0000 |                 1.0000 |              1.0000 |          1.0000 |                    1.0000 |                 1.0000 |             1.0000 |                 1.0000 |                        1.0000 |                     1.0000 |                 1.0000 |                           1.0000 |                        1.0000 |                    1.0000 |

|             |      rows |   accuracy |   macro_precision |   macro_recall |   macro_f1 |   weighted_precision |   weighted_recall |   weighted_f1 |
|:------------|----------:|-----------:|------------------:|---------------:|-----------:|---------------------:|------------------:|--------------:|
| handwritten |   49.0000 |     1.0000 |            1.0000 |         1.0000 |     1.0000 |               1.0000 |            1.0000 |        1.0000 |
| test        | 3850.0000 |     0.9769 |            0.9680 |         0.9871 |     0.9768 |               0.9597 |            0.9769 |        0.9678 |
| validation  | 4101.0000 |     0.9668 |            0.9580 |         0.9836 |     0.9697 |               0.9441 |            0.9668 |        0.9546 |

Fixed C=2 Logistic Regression, combined TF-IDF; five group CV folds on original training text. Test and authored handwritten labels never used to tune. Problem predictions are suggestions, not diagnoses.

The workbook metadata includes implausible stage/problem combinations. Stage and location are extracted as slots; neither is treated as a verified agronomic causal feature. The handwritten set is project-authored, not collected from farmers.


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
