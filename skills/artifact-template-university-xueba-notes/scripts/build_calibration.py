"""Validate/export the canonical authored calibration fixture.

Edit Resources/content/operations-research-calibration.json directly. Keeping
one source prevents old compressed prose from overwriting the reviewed copy.
"""
import argparse
import json
from pathlib import Path
from content_schema import validate_v2

SOURCE=Path(__file__).resolve().parents[1]/'Resources/content/operations-research-calibration.json'

def build():
    data=json.loads(SOURCE.read_text(encoding='utf-8'))
    validate_v2(data)
    return data

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    data=build()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(args.output)
