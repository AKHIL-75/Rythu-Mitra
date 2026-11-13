"""Audit actual workbook schema before making training decisions."""
from pathlib import Path
import json
import pandas as pd
from ml.preprocess import normalize, script_type

ROOT = Path(__file__).resolve().parents[1]

def audit():
    file = ROOT / 'telugu_english_agriculture_CLEAN_dataset.xlsx'
    excel = pd.ExcelFile(file)
    df = pd.read_excel(excel, sheet_name=excel.sheet_names[0])
    out = [f'# Dataset audit\n\nWorkbook: `{file.name}`\n\nSheets: {excel.sheet_names}\n\nShape: {df.shape}',
           '\n## Columns, types and null counts\n\n'+df.dtypes.to_string()+'\n\n'+df.isna().sum().to_string(),
           f'\nFull-row duplicates: {df.duplicated().sum()}']
    for col in df:
        if not col.startswith('query_'):
            out.append(f'\n## {col} distribution\n\n'+df[col].value_counts(dropna=False).to_string())
    stats = {'sheets':excel.sheet_names,'rows':len(df),'columns':list(df),
             'null_counts':df.isna().sum().to_dict(),'row_duplicates':int(df.duplicated().sum()),
             'intent_counts':df.intent.value_counts().to_dict(),'crop_counts':df.crop.value_counts().to_dict()}
    for col in ['query_telugu','query_english','query_code_mixed']:
        s = df[col].fillna('').astype(str)
        normal = s.map(normalize)
        conflicts = df.assign(normal=normal).groupby('normal').intent.nunique()
        info = {'empty':int(normal.eq('').sum()),'duplicates':int(s.duplicated().sum()),
                'normalized_duplicates':int(normal.duplicated().sum()),
                'conflicting_label_queries':int(conflicts.gt(1).sum()),
                'script_counts':s.map(script_type).value_counts().to_dict(),
                'word_length':s.str.split().str.len().describe().to_dict()}
        info['script_share_percent']=(s.map(script_type).value_counts(normalize=True)*100).to_dict()
        stats[col] = info
        out.append(f'\n## {col}\n\n```json\n'+json.dumps(info,ensure_ascii=False,indent=2)+'\n```')
    out.append('''\n## Decisions and limitations

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
''')
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/dataset_audit.md').write_text('\n\n'.join(out),encoding='utf8')
    (ROOT/'reports/dataset_statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
    print('\n\n'.join(out), flush=True)
    return df, stats

if __name__ == '__main__':
    audit()
