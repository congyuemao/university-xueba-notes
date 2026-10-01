#!/usr/bin/env python3
"""Validate a Xueba book's topic, answer and visual topology; not visual or factual QA."""
import argparse
import json
from pathlib import Path

PAGE_TYPES = {"cover", "contents", "overview", "knowledge", "visual_explanation", "process", "worked_example", "synthesis", "recap", "glossary", "answers", "foldout", "blank"}
BODY_TYPES = PAGE_TYPES - {"cover", "contents", "foldout", "blank"}
VISUAL_KINDS = {"microdiagram", "working_diagram", "sidebar_comic", "overview"}


def validate(data, base, stage="plan"):
    errors, warnings = [], []
    def require(ok, message):
        if not ok:
            errors.append(message)
    def index(key):
        result = {}
        records = data.get(key, [])
        require(isinstance(records, list), f"{key}: expected a list")
        if not isinstance(records, list):
            return result
        for record in records:
            if not isinstance(record, dict):
                errors.append(f"{key}: record must be an object")
                continue
            rid = record.get("question_id" if key == "answers" else "id")
            require(isinstance(rid, str) and bool(rid.strip()), f"{key}: missing ID")
            if not isinstance(rid, str) or not rid.strip():
                continue
            require(rid not in result, f"{key}: duplicate ID {rid}")
            result[rid] = record
        return result
    require(data.get("scope") in {"chapter", "whole_book"}, "Unknown scope")
    require(data.get("edition") in {"print", "digital"}, "Unknown edition")
    require(data.get("body_format") == "teaching-units", "Body must use teaching units")
    require(data.get("comic_style") == "pastel-educational-sidebar", "Wrong default comic style")
    fraction = data.get("annotation_free_fraction")
    require(isinstance(fraction, (int, float)) and not isinstance(fraction, bool) and .5 <= fraction <= 1, "Preserve at least half the chapter annotation area")
    concepts, questions, answers, visuals, pages = [index(k) for k in ("concepts", "questions", "answers", "visuals", "pages")]
    require(bool(concepts) and bool(pages), "No concepts or pages")
    required = data.get("required_topics", [])
    require(isinstance(required, list) and bool(required), "No required topic map")
    if isinstance(required, list):
        for topic in required:
            require(any(c.get("topic") == topic for c in concepts.values()), f"Uncovered topic {topic}")
    placed_concepts, placed_visuals, placed_questions, placed_answers = set(), set(), set(), set()
    for cid, concept in concepts.items():
        require(bool(str(concept.get("main_text", "")).strip()), f"{cid}: no central teaching text")
        refs = concept.get("visual_ids", [])
        require(bool(refs) or bool(str(concept.get("prose_reason", "")).strip()), f"{cid}: no visual or reason")
        for vid in refs:
            require(vid in visuals, f"{cid}: unknown visual {vid}")
            if vid in visuals:
                require(cid in visuals[vid].get("concept_ids", []), f"{cid}/{vid}: one-way teaching link")
    for qid, question in questions.items():
        require(bool(str(question.get("prompt", "")).strip()), f"{qid}: empty question")
        require(qid in answers, f"{qid}: missing answer")
        if qid in answers:
            answer = answers[qid]
            require(answer.get("status") == "complete" and bool(str(answer.get("content", "")).strip()), f"{qid}: incomplete answer")
    for qid in answers:
        require(qid in questions, f"Orphan answer {qid}")
    for vid, visual in visuals.items():
        require(visual.get("kind") in VISUAL_KINDS, f"{vid}: unknown visual kind")
        require(visual.get("method") in {"native", "generated", "source"}, f"{vid}: unknown method")
        require(bool(str(visual.get("purpose", "")).strip()), f"{vid}: no teaching purpose")
        refs = visual.get("concept_ids", [])
        require(bool(refs), f"{vid}: no concepts")
        for cid in refs:
            require(cid in concepts, f"{vid}: unknown concept {cid}")
            if cid in concepts:
                require(vid in concepts[cid].get("visual_ids", []), f"{vid}/{cid}: one-way teaching link")
        if stage == "delivery":
            require(visual.get("status") == "embedded", f"{vid}: not embedded")
            asset = visual.get("asset_path")
            require(isinstance(asset, str) and bool(asset.strip()), f"{vid}: no asset path")
            if isinstance(asset, str) and asset.strip():
                require((base / asset).is_file(), f"{vid}: asset file absent")
    run = 0
    types = set()
    for pid, page in pages.items():
        ptype = page.get("type")
        require(ptype in PAGE_TYPES, f"{pid}: unknown page type")
        types.add(ptype)
        for field, registry, placed in [("concept_ids", concepts, placed_concepts), ("visual_ids", visuals, placed_visuals), ("question_ids", questions, placed_questions), ("answer_ids", answers, placed_answers)]:
            for rid in page.get(field, []):
                require(rid in registry, f"{pid}: unknown {field} {rid}")
                placed.add(rid)
        has_working = any(visuals.get(vid, {}).get("kind") != "sidebar_comic" for vid in page.get("visual_ids", []))
        run = run + 1 if ptype == "knowledge" and not has_working else 0
        if run == 3:
            warnings.append(f"At {pid}: review three consecutive knowledge pages without a working visual")
        if stage == "delivery" and ptype in BODY_TYPES:
            require(page.get("footer_lines") in {1, 2}, f"{pid}: missing/long footer")
    for registry, placed, label in [(concepts, placed_concepts, "concept"), (visuals, placed_visuals, "visual"), (questions, placed_questions, "question"), (answers, placed_answers, "answer")]:
        for rid in registry:
            require(rid in placed, f"Unplaced {label} {rid}")
    body_types = types & BODY_TYPES
    require(len(body_types) > 1 or len(pages) <= 2, "Multi-page book repeats a single body page type")
    if data.get("scope") == "whole_book":
        for ptype in {"cover", "contents", "overview", "knowledge", "worked_example", "synthesis", "foldout"}:
            require(ptype in types, f"Whole book missing {ptype}")
    return {"status": "failed" if errors else "passed", "errors": errors, "warnings": warnings, "stage": stage}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--stage", choices=("plan", "delivery"), default="plan")
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Plan root must be an object")
        result = validate(data, args.plan.resolve().parent, args.stage)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {"status": "failed", "errors": [str(exc)], "warnings": [], "stage": args.stage}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["errors"] else 0)

if __name__ == "__main__":
    main()
