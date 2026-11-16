# -*- coding: utf-8 -*-
import json, glob, os, re
D = r"C:\Users\18132\Documents\Obsidian Vault\本科毕设\.zwork\概念草稿"
V = r"C:\Users\18132\Documents\Obsidian Vault\本科毕设"
terms = []
for fp in glob.glob(os.path.join(D, "*.jsonl")):
    for ln in open(fp, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            print("BAD", fp, ln[:80])
            continue
        terms.append(o.get("term", ""))
illegal = re.compile(r'[\\/:*?"<>|]')
bad = sorted({t for t in terms if illegal.search(t)})
print("total terms:", len(terms), "unique:", len(set(terms)))
print("ILLEGAL draft terms:", bad)
links = set()
for root, dirs, fs in os.walk(V):
    if ".zwork" in root:
        continue
    for f in fs:
        if f.endswith(".md"):
            txt = open(os.path.join(root, f), encoding="utf-8").read()
            links |= set(re.findall(r"\[\[([^\]|#]+)\]\]", txt))
print("note links with illegal chars:", sorted({l for l in links if illegal.search(l)}))
