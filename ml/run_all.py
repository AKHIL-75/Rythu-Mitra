"""One-command audit → split → augment → tune → evaluate → export → report."""
import os
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.vendor')]
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')

def main():
    from ml.audit import audit
    df,stats=audit()
    from ml.build_catalog import build
    build()
    from ml.data import prepare
    train,val,test=prepare(df)
    from ml.typos import augment
    train=augment(train,val,test)
    from ml.benchmarks import build as build_benchmark
    build_benchmark()
    from ml.slots import export_slots
    export_slots()
    from ml.train import train_models
    metrics=train_models(train,val,test,stats)
    from ml.documentation import write_docs
    write_docs(metrics)
    print('\nFINAL MODEL RESULTS\n')
    import pandas as pd
    print(pd.DataFrame(metrics['comparison'])[['model','features','validation_macro_f1','test_accuracy','test_macro_f1']].to_string(index=False))
    print('Handwritten accuracy:',metrics['handwritten']['accuracy'])

if __name__=='__main__':
    main()
