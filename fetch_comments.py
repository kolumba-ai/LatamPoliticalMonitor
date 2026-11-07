#!/usr/bin/env python3
"""Fetch Oriane's popular comments (max 15 per video) for every video in morena_data.json -> comments.json
Usage: ORIANE_API_KEY=... python3 fetch_comments.py"""
import json, os, sys, urllib.request
KEY = os.environ.get("ORIANE_API_KEY") or sys.exit("Set ORIANE_API_KEY")
d = json.load(open("morena_data.json"))
ids = sorted({v["id"] for p in d["politicians"] for v in p["videos"]})
out = {}
for i in range(0, len(ids), 100):
    chunk = ids[i:i + 100]
    body = {"operator": "and", "filters": {"platform": {"includes": ["tiktok"]},
            "platformId": {"includes": [{"platform": "tiktok", "platformId": x} for x in chunk]}}}
    req = urllib.request.Request("https://connect.oriane.xyz/rest/contents/search?limit=100&projection=full",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=120))
    for x in r["data"]["results"]:
        out[x["platformId"]] = {"publishedAt": x["publishedAt"], "commentsCount": x.get("commentsCount") or 0,
            "comments": [{"cid": c["platformId"], "handle": c.get("profileHandle") or "", "text": c.get("content") or "",
                          "likes": c.get("likesCount") or 0, "replies": c.get("repliesCount") or 0,
                          "at": c.get("publishedAt")} for c in (x.get("popularComments") or [])]}
json.dump(out, open("comments.json", "w"), ensure_ascii=False)
n = sum(len(v["comments"]) for v in out.values())
print(f"{len(out)} videos, {n} comments, {sum(1 for v in out.values() if v['comments'])} videos with comments, "
      f"{sum(v['commentsCount'] for v in out.values())} total comments on TikTok")
