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
