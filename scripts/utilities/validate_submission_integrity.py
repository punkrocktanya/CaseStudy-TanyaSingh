"""Verify packaged file hashes, required artifacts, and source syntax."""

# Make shared task modules importable when running this file directly.
import sys as _task_sys
from pathlib import Path as _TaskPath
_task_scripts = _TaskPath(__file__).resolve().parents[1]
for _task_dir in ("task1_data_engineering", "task2_degradation_modeling", "task3_anomaly_detection", "task4_rul_estimation", "task5_pack_scaling", "task6_reporting"):
    _task_path = str(_task_scripts / _task_dir)
    if _task_path not in _task_sys.path:
        _task_sys.path.append(_task_path)

from pathlib import Path
import ast, hashlib, json
ROOT=Path(__file__).resolve().parents[2]

def main():
    manifest=json.loads((ROOT/'SUBMISSION_MANIFEST.json').read_text(encoding='utf-8'))
    errors=[]
    for record in manifest['files']:
        p=ROOT/record['path']
        if not p.is_file(): errors.append('Missing: '+record['path']); continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=record['sha256']: errors.append('Changed: '+record['path'])
    for p in (ROOT/'scripts').rglob('*.py'):
        try: ast.parse(p.read_text(encoding='utf-8-sig'))
        except (SyntaxError, UnicodeError) as e: errors.append(f'{p}: {e}')
    if errors: raise SystemExit('Integrity errors:\n'+'\n'.join(errors))
    print(f"Verified {len(manifest['files'])} files and Python syntax. Hashes do not validate scientific results.")
if __name__=='__main__': main()
