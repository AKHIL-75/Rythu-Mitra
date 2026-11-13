"""Create a portable deliverable without caches, logs or local dependency copies."""
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def package():
    output=ROOT/'Rythu_Mitra_NLP_Complete.zip'
    files=[]
    for p in ROOT.rglob('*'):
        relative=p.relative_to(ROOT)
        if not p.is_file() or p==output:continue
        if any(part in {'.vendor','.venv','.pytest_cache','__pycache__','cache','.git','node_modules'} for part in relative.parts):continue
        if p.name == '.env' or p.name.startswith('.env.'):continue
        if p.suffix in {'.log','.pyc','.zip'}:continue
        files.append(p)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for p in files:archive.write(p,p.relative_to(ROOT).as_posix())
    print(json.dumps({'file':str(output),'files':len(files),'bytes':output.stat().st_size},indent=2))
    return output

if __name__=='__main__':package()
