# -*- coding: utf-8 -*-
"""孤儿概念页移入 .zwork/_stale_concepts（不删除）；然后全库断链检查。"""
import os, re, json, glob, shutil

V = r"C:\Users\18132\Documents\Obsidian Vault\本科毕设"
BLOCKS = ["A协议基础与场景调研", "B代理实现与性能评测", "C分布式组网与边云桥接", "D可靠性容错与安全"]

# 当前规范术语集合 = 各 jsonl 归一后的 term
ALIAS_KEYS = None
terms = set()
for fp in glob.glob(os.path.join(V, ".zwork", "概念草稿", "*.jsonl")):
    for ln in open(fp, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        terms.add((o.get("term") or "").strip())

# 直接用 merge_concepts 的 canon 逻辑太重；以磁盘上新写的页面为准：
# 规范页 = 本次 merge 输出。这里改为：读取 概念索引.md 提取规范名。
idx = open(os.path.join(V, "概念索引.md"), encoding="utf-8").read()
valid = set(re.findall(r"\[\[([^\]|#]+)\]\]", idx))
stale_dir = os.path.join(V, ".zwork", "_stale_concepts")
os.makedirs(stale_dir, exist_ok=True)
moved = []
for b in BLOCKS:
    d = os.path.join(V, b, "概念汇总")
    if not os.path.isdir(d):
        continue
    for f in os.listdir(d):
        if f.endswith(".md") and f[:-3] not in valid:
            shutil.move(os.path.join(d, f), os.path.join(stale_dir, f))
            moved.append(b + "/" + f)
print("stale moved:", len(moved))
for m in moved:
    print("  ", m)

# 断链检查：vault 内所有 [[链接]] 是否都有同名 md（排除 .zwork）
names = set()
for root, dirs, fs in os.walk(V):
    if ".zwork" in root or ".obsidian" in root:
        continue
    for f in fs:
        if f.endswith(".md"):
            names.add(f[:-3])
links = set()
for root, dirs, fs in os.walk(V):
    if ".zwork" in root or ".obsidian" in root:
        continue
    for f in fs:
        if f.endswith(".md"):
            txt = open(os.path.join(root, f), encoding="utf-8").read()
            links |= set(re.findall(r"\[\[([^\]|#]+)\]\]", txt))
dangling = sorted(l for l in links if l not in names)
print("total links:", len(links), "dangling:", len(dangling))
for l in dangling:
    print("  DANGLING:", l)
