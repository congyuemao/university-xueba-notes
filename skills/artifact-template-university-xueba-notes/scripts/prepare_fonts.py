#!/usr/bin/env python3
"""Prepare licensed template fonts with WenKai.ttf as the body default; supports offline sources."""
import argparse
from pathlib import Path
import shutil
import tarfile
import tempfile
import urllib.request

KAI_URL = "https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/fonts/TTF/LXGWWenKai-Regular.ttf"
NOTO_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
DEFAULT_BODY_FONT = "WenKai.ttf"
DEJAVU_URL = "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.tar.bz2"
LATIN = ["DejaVuSans.ttf", "DejaVuSerif.ttf"]

def download(url, path):
    request = urllib.request.Request(url, headers={"User-Agent": "University-Xueba-Notes"})
    temporary = path.with_suffix(path.suffix + ".download")
    try:
        with urllib.request.urlopen(request, timeout=60) as source, temporary.open("wb") as target:
            shutil.copyfileobj(source, target)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)

def prepare(output, source=None):
    output.mkdir(parents=True, exist_ok=True)
    if source:
        if source.resolve() == output.resolve():
            raise ValueError("Choose a separate output directory.")
        for name in [DEFAULT_BODY_FONT,"SansBold.ttf"] + LATIN:
            file = source / name
            if file.is_file():
                shutil.copy2(file, output / name)
    if not (output / "WenKai.ttf").exists():
        download(KAI_URL, output / "WenKai.ttf")
    if not (output / "SansBold.ttf").exists():
        variable = output / "NotoSansSC.ttf"
        if not variable.exists() and source and (source / variable.name).is_file():
            shutil.copy2(source / variable.name, variable)
        if not variable.exists():
            download(NOTO_URL, variable)
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
        for name, weight in [("SansBold.ttf",700)]:
            if not (output/name).exists():
                font = TTFont(variable)
                instance = instantiateVariableFont(font, {"wght": weight}, inplace=True)
                instance.save(output/name)
                instance.close()
    missing=[]
    for name in LATIN:
        target=output/name
        system=Path("/usr/share/fonts/truetype/dejavu")/name
        if not target.exists() and system.is_file():
            shutil.copy2(system, target)
        if not target.exists():
            missing.append(name)
    if missing:
        with tempfile.TemporaryDirectory() as directory:
            archive=Path(directory)/"dejavu.tar.bz2"
            download(DEJAVU_URL,archive)
            with tarfile.open(archive,"r:bz2") as fonts:
                for name in missing:
                    member=next(m for m in fonts.getmembers() if m.name.endswith("/ttf/"+name))
                    with fonts.extractfile(member) as source_file, (output/name).open("wb") as target:
                        shutil.copyfileobj(source_file,target)
    licences=Path(__file__).resolve().parents[1]/"assets/licenses"
    for name in ["LXGW-WenKai-OFL.txt","NotoSansSC-OFL.txt","DejaVu-LICENSE.txt"]:
        shutil.copy2(licences/name,output/name)
    from fontTools.ttLib import TTFont
    for name in [DEFAULT_BODY_FONT,"SansBold.ttf"] + LATIN:
        font=TTFont(output/name)
        if not font.getBestCmap():
            raise ValueError(f"Invalid font: {name}")
        font.close()
    return output

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--source-dir",type=Path,help="Optional offline font directory")
    args=parser.parse_args()
    path=prepare(args.output_dir.resolve(),args.source_dir.resolve() if args.source_dir else None)
    print(f"Prepared template font set: {path} (body default: {DEFAULT_BODY_FONT})")

if __name__=="__main__":
    main()
