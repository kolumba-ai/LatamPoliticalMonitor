#!/usr/bin/env python3
"""Inject morena_data.json (+ perception.json and comment_labels.json labels) into monitor_template.html -> morena_monitor.html

perception.json maps "<videoId>|<politician-slug>" to {"p": positive|negative|neutral, "relevant": bool, "why": str}.
Pairs marked relevant=false are dropped; pairs without a label show as neutral.
"""
import json, os
d = json.load(open("morena_data.json"))
labels = json.load(open("perception.json")) if os.path.exists("perception.json") else {}
dropped = unlabeled = 0
for p in d["politicians"]:
    keep = []
    for v in p["videos"]:
        lab = labels.get(f'{v["id"]}|{p["slug"]}')
        if lab and lab.get("relevant") is False:
            dropped += 1
            continue
        if not lab:
            unlabeled += 1
        v["pc"] = (lab or {}).get("p", "neutral")
        v["why"] = (lab or {}).get("why", "Sin clasificar")
        v["caption"] = v["caption"][:400]
        v.pop("comments", None); v.pop("shares", None)
        keep.append(v)
    p["videos"] = keep
# Feedback: per video counts of comment stance, split into humans (human/unsure) and likely bots.
# comment_labels.json maps comment id -> {"s": pos|neg|neu, "b": human|bot|unsure}.
fb = {}
if os.path.exists("comments.json") and os.path.exists("comment_labels.json"):
    cm, cl = json.load(open("comments.json")), json.load(open("comment_labels.json"))
    vids = {v["id"] for p in d["politicians"] for v in p["videos"]}
    for vid in vids:
        cs = [cl[x["cid"]] for x in cm.get(vid, {}).get("comments", []) if x["cid"] in cl]
        if not cs:
            continue
        f = dict(p=0, n=0, u=0, bp=0, bn=0, bu=0, c=len(cs))
        for c in cs:
            k = {"pos": "p", "neg": "n"}.get(c["s"], "u")
            f[("b" + k) if c["b"] == "bot" else k] += 1
        fb[vid] = f
d["feedback"] = fb
print(f"feedback for {len(fb)} videos")
js = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = open("monitor_template.html").read().replace("/*DATA*/null", js, 1)
open("morena_monitor.html", "w").write(html)
print(f"morena_monitor.html {len(html)//1024} KB; dropped {dropped} unrelated, {unlabeled} unlabeled")
