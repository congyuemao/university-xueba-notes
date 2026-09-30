#!/usr/bin/env python3
"""Check both reference modes against their page geometry and answer contract."""
import argparse
import json
from pathlib import Path
import re
import pdfplumber

MM=72/25.4

def verify(path,edition):
    meta=json.loads(path.with_suffix(".layout.json").read_text())
    assert len(meta["pages"]) == 14, "Expected 14 reference pages"
    assert len(meta["page_decor"]) == 14
    assert all(1 <= rows <= 2 for rows in meta["footer_rows"]), "Footer exceeds two lines"
    with pdfplumber.open(path) as pdf:
        assert len(pdf.pages)==14
        texts=[]
        for page,decor in zip(pdf.pages,meta["page_decor"]):
            number=decor["page"]
            odd=number%2==1
            text=page.extract_text() or ""
            texts.append(text)
            assert abs(page.width-210*MM)<.1 and abs(page.height-297*MM)<.1
            assert decor["edition"]==edition
            assert decor["page_number_side"]==("right" if odd else "left")
            assert decor["section_number"]==({1:"01",9:"02"}.get(number))
            assert decor["body_top"]==(35 if number in (1,9) else 16)
            expected_columns=1 if edition=="print" else 2
            assert len(decor["annotation_columns"])==expected_columns
            assert len(decor["writing_areas"])==expected_columns
            assert text.count("我的批注")==expected_columns, f"Writing areas on page {number}"
            assert len(page.images)==(1 if number in (5,9,12) else 0)
            left,right=decor["content_left"]*MM,decor["content_right"]*MM
            chars=[c for c in page.chars if c["text"].strip()]
            overflow=[c for c in chars if c["x0"]<left-.6 or c["x1"]>right+.6]
            assert not overflow, f"Text outside content span page {number}: {[(c['text'],round(c['x0']/MM,2),round(c['x1']/MM,2)) for c in overflow[:10]]}"
            for area in decor["writing_areas"]:
                assert area["end"]-area["start"]>=18, f"No useful writing area page {number}"
            blocks=decor["annotation_blocks"]
            for column in decor["annotation_columns"]:
                x,w=column["x"],column["width"]
                column_blocks=[b for b in blocks if b["x"]==x]
                for first,second in zip(column_blocks,column_blocks[1:]):
                    assert first["y"]+first["h"]<=second["y"], f"Annotation overlap {number}"
                assert all(b["w"]==w for b in column_blocks)
            if edition=="print":
                assert decor["body_x"]==(20 if odd else 62)
                col=decor["annotation_columns"][0]
                assert col=={"side":"right" if odd else "left","x":153 if odd else 12,"width":45}
                assert decor["inner_margin"]==20
                assert decor["content_left"]==(20 if odd else 12)
                assert decor["content_right"]==(198 if odd else 190)
                for edge in page.edges:
                    assert edge["x0"]>=left-.6 and edge["x1"]<=right+.6, f"Rule in binding margin {number}"
            else:
                assert decor["body_x"]==38
                assert decor["annotation_columns"]==[{"side":"left","x":12,"width":22},{"side":"right","x":170,"width":28}]
                assert decor["content_left"]==12 and decor["content_right"]==198
            for index in [number]:
                footer_chars=[c for c in chars if 275*MM <= c["top"] <= 285*MM]
                assert footer_chars, f"Empty footer {number}"
        combined="\n".join(texts)
        assert "Complete solution" in combined
        assert "103" in combined and "Minimal Absurd" in combined
        assert all(f"Q{i}." in texts[12] for i in range(1,5))
        assert all(f"Answer to Q{i}" in texts[13] for i in range(1,5))
        assert "Choose c = 4" in texts[13]
        assert "3n + 2" in texts[10] and "Conclusion" in texts[11]
    print(json.dumps({"edition":edition,"pages":14,"status":"passed","annotations_per_page":expected_columns},ensure_ascii=False))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf",type=Path)
    parser.add_argument("--edition",choices=("print","digital"),required=True)
    args=parser.parse_args()
    verify(args.pdf.resolve(),args.edition)
