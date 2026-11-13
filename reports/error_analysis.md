# Error analysis

Workbook test errors: 0 / 3850.

| intent   | prediction   | count   |
|----------|--------------|---------|

## Script breakdown

|           |    n |   accuracy |   macro_precision |   macro_recall |   macro_f1 |   weighted_precision |   weighted_recall |   weighted_f1 |
|:----------|-----:|-----------:|------------------:|---------------:|-----------:|---------------------:|------------------:|--------------:|
| english   | 1261 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| mixed     | 1641 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| romanized |   68 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| telugu    |  880 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |

## Crop-group breakdown

|             |   n |   accuracy |   macro_precision |   macro_recall |   macro_f1 |   weighted_precision |   weighted_recall |   weighted_f1 |
|:------------|----:|-----------:|------------------:|---------------:|-----------:|---------------------:|------------------:|--------------:|
| cereal      | 302 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| fibre       | 161 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| fruit       | 455 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| oilseed     | 629 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| plantation  | 182 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| pulse       | 590 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| spice       | 294 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| unspecified | 354 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |
| vegetable   | 883 |          1 |                 1 |              1 |          1 |                    1 |                 1 |             1 |

## Handwritten failures

| query                                     | intent       | prediction   |
|:------------------------------------------|:-------------|:-------------|
| boppayi aakulu curl avutunnayi virus aa   | crop_disease | other_agri   |
| పాలకూరకు పోషకాలు ఎంత అవసరం                        | fertilizer   | irrigation   |
| guava fertilizr dose after soil testing   | fertilizer   | other_agri   |
| కొత్తిమీర పంటకు కంపోస్ట్ వేయవచ్చా                      | fertilizer   | other_agri   |
| NPK for French beans                      | fertilizer   | other_agri   |
| irrigaation timing for cabbage please     | irrigation   | other_agri   |
| arati neeru morning ivvala evening ivvala | irrigation   | out_of_scope |
| గుమ్మడికి నీళ్ళు సరిపోవడం లేదు                        | irrigation   | other_agri   |
| weathr forcast for chilli field           | weather      | other_agri   |
| వాతావరణం?                                    | weather      | other_agri   |
| varshalu eppudu padatayi guntur lo        | weather      | irrigation   |
| Is PMFBY enrollment open for my crop?     | govt_scheme  | other_agri   |
| When should I harvest papaya?             | other_agri   | irrigation   |
| How do I choose a crop for red soil?      | other_agri   | govt_scheme  |
| Explain inheritance in Java               | out_of_scope | crop_disease |
| qzxwv ljkqq zzzzzz                        | out_of_scope | other_agri   |
| What is seven multiplied by nine?         | out_of_scope | weather      |
| Order noodles to my home                  | out_of_scope | fertilizer   |
| నా మొబైల్ స్క్రీన్ పగిలింది                           | out_of_scope | other_agri   |

Interpretation: inspect short and colloquial handwritten queries separately from templated workbook text. Disease/nutrient symptoms can overlap; a topic prediction cannot diagnose the cause. The grouped split reduces close wording leakage but cannot establish generalization to farmer speech. Held-out out-of-scope text is authored synthetic material. Confidence can be high on unfamiliar inputs.
