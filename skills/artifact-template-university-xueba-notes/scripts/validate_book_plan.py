#!/usr/bin/env python3
"""Validate Xueba teaching, outline, glossary and visual topology."""
import argparse
import json
from pathlib import Path

PAGE_TYPES={"cover","contents","overview","knowledge","visual_explanation","process","worked_example","synthesis","recap","glossary","references","answers","foldout","blank"}
BODY_TYPES=PAGE_TYPES-{"cover","contents","foldout","blank"}
HUMOUR_TYPES=PAGE_TYPES-{"cover","foldout","blank"}
VISUAL_KINDS={"microdiagram","working_diagram","sidebar_comic","overview"}
OUTLINE_KINDS={"part","chapter","unit","section","lesson","feature","appendix"}

def validate(data,base,stage="plan"):
    errors,warnings=[],[]
    def require(ok,message):
        if not ok:errors.append(message)
    def index(key,id_key="id"):
        records=data.get(key,[]);result={}
        require(isinstance(records,list),f"{key}: expected a list")
        if not isinstance(records,list):return result
        for record in records:
            if not isinstance(record,dict):errors.append(f"{key}: record must be an object");continue
            rid=record.get(id_key)
            require(isinstance(rid,str) and bool(rid.strip()),f"{key}: missing ID")
            if not isinstance(rid,str) or not rid.strip():continue
            require(rid not in result,f"{key}: duplicate ID {rid}");result[rid]=record
        return result

    require(data.get("scope") in {"chapter","whole_book"},"Unknown scope")
    require(data.get("edition") in {"print","digital"},"Unknown edition")
    require(data.get("body_format")=="teaching-units","Body must use teaching units")
    require(data.get("comic_style")=="reference-anchored-sidebar","Wrong default comic style")
    fraction=data.get("annotation_free_fraction")
    require(isinstance(fraction,(int,float)) and not isinstance(fraction,bool) and .5<=fraction<=1,"Preserve at least half the chapter annotation area")

    concepts=index("concepts");outline=index("outline");examples=index("worked_examples");visuals=index("visuals");pages=index("pages")
    questions=index("questions");answers=index("answers","question_id")
    require(bool(concepts) and bool(outline) and bool(pages),"Concepts, outline and pages are required")

    required=data.get("required_topics",[])
    require(isinstance(required,list) and bool(required),"No required topic map")
    if isinstance(required,list):
        for topic in required:require(any(c.get("topic")==topic for c in concepts.values()),f"Uncovered topic {topic}")

    for cid,concept in concepts.items():
        for field in ("topic","definition","plain_explanation","canonical_example"):
            require(isinstance(concept.get(field),str) and bool(concept[field].strip()),f"{cid}: missing {field}")
        require(isinstance(concept.get("core"),bool),f"{cid}: core must be boolean")
        prereqs=concept.get("prerequisite_ids",[])
        require(isinstance(prereqs,list),f"{cid}: prerequisite_ids must be a list")
        if isinstance(prereqs,list):
            for ref in prereqs:require(ref in concepts,f"{cid}: unknown prerequisite {ref}")
        refs=concept.get("visual_ids",[])
        require(bool(refs) or bool(str(concept.get("prose_reason","")).strip()),f"{cid}: no visual or prose reason")
        for vid in refs:
            require(vid in visuals,f"{cid}: unknown visual {vid}")
            if vid in visuals:require(cid in visuals[vid].get("concept_ids",[]),f"{cid}/{vid}: one-way teaching link")

    for oid,node in outline.items():
        require(isinstance(node.get("title"),str) and bool(node["title"].strip()),f"{oid}: missing outline title")
        require(node.get("kind") in OUTLINE_KINDS,f"{oid}: unknown outline kind")
        level=node.get("level");require(isinstance(level,int) and not isinstance(level,bool) and 1<=level<=4,f"{oid}: level must be 1–4")
        parent=node.get("parent_id")
        if parent is None:require(level==1,f"{oid}: top-level node must use level 1")
        else:
            require(parent in outline,f"{oid}: unknown parent {parent}")
            if parent in outline:require(outline[parent].get("level")==level-1,f"{oid}: parent level must be one less")

    for eid,example in examples.items():
        require(isinstance(example.get("prompt"),str) and bool(example["prompt"].strip()),f"{eid}: missing prompt")
        require(isinstance(example.get("solution"),str) and bool(example["solution"].strip()),f"{eid}: missing complete solution")
        for cid in example.get("concept_ids",[]):require(cid in concepts,f"{eid}: unknown concept {cid}")
    for qid,question in questions.items():
        require(bool(str(question.get("prompt","")).strip()),f"{qid}: empty question")
        require(qid in answers,f"{qid}: missing answer")
        if qid in answers:require(answers[qid].get("status")=="complete" and bool(str(answers[qid].get("content","")).strip()),f"{qid}: incomplete answer")
    for qid in answers:require(qid in questions,f"Orphan answer {qid}")

    for vid,visual in visuals.items():
        require(visual.get("kind") in VISUAL_KINDS,f"{vid}: unknown visual kind")
        require(visual.get("method") in {"native","generated","source"},f"{vid}: unknown method")
        require(bool(str(visual.get("purpose","")).strip()),f"{vid}: no teaching purpose")
        refs=visual.get("concept_ids",[]);require(bool(refs),f"{vid}: no concepts")
        for cid in refs:
            require(cid in concepts,f"{vid}: unknown concept {cid}")
            if cid in concepts:require(vid in concepts[cid].get("visual_ids",[]),f"{vid}/{cid}: one-way teaching link")
        if stage=="delivery":
            require(visual.get("status")=="embedded",f"{vid}: not embedded")
            asset=visual.get("asset_path");require(isinstance(asset,str) and bool(asset.strip()),f"{vid}: no asset path")
            if isinstance(asset,str) and asset.strip():require((base/asset).is_file(),f"{vid}: asset file absent")

    placed={"concept":set(),"outline":set(),"visual":set(),"example":set(),"question":set(),"answer":set()};types=set();run=comic_run=0
    mappings=[("concept_ids",concepts,"concept"),("outline_ids",outline,"outline"),("visual_ids",visuals,"visual"),("worked_example_ids",examples,"example"),("question_ids",questions,"question"),("answer_ids",answers,"answer")]
    for pid,page in pages.items():
        ptype=page.get("type");require(ptype in PAGE_TYPES,f"{pid}: unknown page type");types.add(ptype)
        for field,registry,label in mappings:
            refs=page.get(field,[]);require(isinstance(refs,list),f"{pid}: {field} must be a list")
            if isinstance(refs,list):
                for rid in refs:require(rid in registry,f"{pid}: unknown {field} {rid}");placed[label].add(rid)
        has_working=any(visuals.get(vid,{}).get("kind")!="sidebar_comic" for vid in page.get("visual_ids",[]))
        run=run+1 if ptype=="knowledge" and not has_working else 0
        if run==3:warnings.append(f"At {pid}: review three consecutive knowledge pages without a working visual")
        has_comic=any(visuals.get(vid,{}).get("kind")=="sidebar_comic" for vid in page.get("visual_ids",[]))
        comic_run=comic_run+1 if ptype=="knowledge" and not has_comic else 0
        if comic_run==3:warnings.append(f"At {pid}: review three consecutive knowledge pages without a sidebar comic")
        if page.get("humour_position") is not None:require(page["humour_position"]=="page-bottom",f"{pid}: humour must be page-bottom furniture")
        if stage=="delivery" and ptype in HUMOUR_TYPES:
            lines=page.get("humour_lines");require(isinstance(lines,int) and not isinstance(lines,bool) and lines in {1,2},f"{pid}: humour strip needs one or two lines")
            require(page.get("humour_position")=="page-bottom",f"{pid}: humour strip must be fixed at the physical page bottom")

    for registry,label in ((concepts,"concept"),(outline,"outline"),(visuals,"visual"),(examples,"example"),(questions,"question"),(answers,"answer")):
        for rid in registry:require(rid in placed[label],f"Unplaced {label} {rid}")

    glossary=data.get("chapter_glossary");require(isinstance(glossary,list) and bool(glossary),"Final chapter_glossary is required")
    terms=set()
    if isinstance(glossary,list):
        for group in glossary:
            require(isinstance(group,dict),"Glossary group must be an object")
            if not isinstance(group,dict):continue
            chapter_id=group.get("chapter_id");require(chapter_id in outline,f"Glossary group references unknown chapter {chapter_id}")
            require(bool(str(group.get("chapter_title","")).strip()),f"{chapter_id}: missing chapter_title")
            entries=group.get("entries");require(isinstance(entries,list) and bool(entries),f"{chapter_id}: no glossary entries")
            if not isinstance(entries,list):continue
            for entry in entries:
                require(isinstance(entry,dict) and set(entry)=={"term_en","meaning_zh"},f"{chapter_id}: glossary entry may contain only term_en and meaning_zh")
                if not isinstance(entry,dict):continue
                term=entry.get("term_en");meaning=entry.get("meaning_zh")
                require(isinstance(term,str) and bool(term.strip()),f"{chapter_id}: empty English term")
                require(isinstance(meaning,str) and bool(meaning.strip()),f"{chapter_id}: empty Chinese meaning")
                if isinstance(term,str):
                    key=term.strip().casefold();require(key not in terms,f"Duplicate glossary term {term}");terms.add(key)

    body_types=types&BODY_TYPES;require(len(body_types)>1 or len(pages)<=2,"Multi-page book repeats a single body page type")
    if data.get("scope")=="whole_book":
        for ptype in {"cover","contents","overview","knowledge","glossary","foldout"}:require(ptype in types,f"Whole book missing {ptype}")
        require(bool(types&{"worked_example","process"}),"Whole book needs a worked-example or method page")
    return {"status":"failed" if errors else "passed","errors":errors,"warnings":warnings,"stage":stage}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("plan",type=Path);parser.add_argument("--stage",choices=("plan","delivery"),default="plan");args=parser.parse_args()
    try:
        data=json.loads(args.plan.read_text(encoding="utf-8"))
        if not isinstance(data,dict):raise ValueError("Plan root must be an object")
        result=validate(data,args.plan.resolve().parent,args.stage)
    except (OSError,ValueError,TypeError,KeyError) as exc:result={"status":"failed","errors":[str(exc)],"warnings":[],"stage":args.stage}
    print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(1 if result["errors"] else 0)

if __name__=="__main__":main()
