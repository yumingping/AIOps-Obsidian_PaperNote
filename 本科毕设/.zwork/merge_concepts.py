# -*- coding: utf-8 -*-
"""合并 概念草稿/*.jsonl → 各区块 概念汇总/<term>.md + 根目录 概念索引.md"""
import os, json, glob, re

SRC = r"C:\Users\18132\Documents\Obsidian Vault\本科毕设"
DRAFT = os.path.join(SRC, ".zwork", "概念草稿")
BLOCKS = {"A": "A协议基础与场景调研", "B": "B代理实现与性能评测",
          "C": "C分布式组网与边云桥接", "D": "D可靠性容错与安全"}

concepts, dup = {}, []
# 别名归一：草稿/笔记中的旧名 → 规范名（避免文件名非法字符与变体分裂）
ALIAS = {
    "发布订阅模式（Publish/Subscribe）": "发布订阅模式",
    "发布订阅模式（publish/subscribe）": "发布订阅模式",
    "发布订阅模式（Pub/Sub）": "发布订阅模式",
    "内核旁路与 mTCP/DPDK（kernel bypass）": "内核旁路（kernel bypass）",
    "内核旁路（kernel bypass，mTCP/DPDK）": "内核旁路（kernel bypass）",
    "内核旁路（kernel bypass，mTCP·DPDK）": "内核旁路（kernel bypass）",
    "epoll（I/O 多路复用）": "epoll（IO 多路复用）",
    "传输成本大于处理成本（Transport Cost > Processing Cost）": "传输成本大于处理成本",
    "尾时延与分位数（p50/p95）": "尾时延与分位数（p50 与 p95）",
    "开环负载与令牌桶（open-loop / token bucket）": "开环负载与令牌桶（open-loop 与 token bucket）",
    "故障注入与 MTTF/MTTR（fault injection）": "故障注入与 MTTF、MTTR（fault injection）",
    "死信队列与死信交换（DLQ / DLX）": "死信队列与死信交换（DLQ、DLX）",
    "QoS（服务质量等级）": "QoS（服务质量）",
    "MQTT（消息队列遥测传输协议）": "MQTT（消息队列遥测传输）",
    "主题（Topic）": "Topic（主题）",
    "消息载荷": "payload（消息载荷）",
    "消息载荷（payload）": "payload（消息载荷）",
    "payload（有效载荷）": "payload（消息载荷）",
    "丢包率（packet loss）": "丢包率",
    "丢包率（Packet Loss）": "丢包率",
    "端到端时延（end-to-end latency）": "端到端时延",
    "端到端时延（end-to-end delay）": "端到端时延",
    "遗嘱消息（Last Will and Testament）": "遗嘱消息",
    "负载均衡器（Load Balancer）": "负载均衡器",
}
ILLEGAL = re.compile(r'[\\/:*?"<>|]')

def canon(name):
    name = (name or "").strip()
    name = ALIAS.get(name, name)
    return ILLEGAL.sub("·", name).strip()

ORDER = ["12", "34", "57", "68", "910", "1112"]  # A/B/C 优先认领共享基础概念
for fp in sorted(glob.glob(os.path.join(DRAFT, "*.jsonl")),
                 key=lambda p: ORDER.index(os.path.basename(p).split(".")[0])
                 if os.path.basename(p).split(".")[0] in ORDER else 99):
    src = os.path.basename(fp)
    with open(fp, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception as e:
                print(f"[BADJSON] {src}:{ln} {e}")
                continue
            t = canon(o.get("term"))
            if not t:
                continue
            if t in concepts:
                dup.append((t, src))
                old = concepts[t]
                old["related"] += [canon(r) for r in o.get("related", []) if canon(r) not in old["related"] and canon(r) != t]
                old["backs"] += [b for b in o.get("backs", []) if b not in old["backs"]]
                continue
            concepts[t] = {
                "term": t, "block": (o.get("block") or "A").strip().upper()[:1],
                "def": (o.get("def") or "").strip(),
                "plain": (o.get("plain") or "").strip(),
                "points": [p for p in (o.get("points") or []) if str(p).strip()],
                "related": sorted({canon(r) for r in (o.get("related") or []) if canon(r) and canon(r) != t}),
                "backs": [b for b in (o.get("backs") or []) if b.strip()],
                "src": src,
            }

for t, c in concepts.items():
    blk = c["block"] if c["block"] in BLOCKS else "A"
    d = os.path.join(SRC, BLOCKS[blk], "概念汇总")
    os.makedirs(d, exist_ok=True)
    lines = [f"# {t}", "", f"**一句话定义**：{c['def']}", "",
             f"**通俗解释（研0 版）**：{c['plain']}", ""]
    if c["points"]:
        lines += ["**关键要点**"] + [f"- {p}" for p in c["points"]] + [""]
    if c["related"]:
        lines += ["相关：" + "、".join(f"[[{r}]]" for r in c["related"])]
    if c["backs"]:
        lines += ["回链：" + "、".join(f"[[{b}]]" for b in c["backs"])]
    lines += [""]
    with open(os.path.join(d, t + ".md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

idx = ["# 概念索引", "",
       "> 全部概念解释页按区块分组；术语在论文笔记中首次出现处有浅显解释并链接到这里。", ""]
for b in "ABCD":
    group = sorted(t for t, c in concepts.items() if c["block"] == b)
    if not group:
        continue
    idx += ["## %s %s" % (b, BLOCKS[b]), ""]
    idx += [f"- [[{t}]]——{concepts[t]['def']}" for t in group]
    idx += [""]
idx = [l for l in idx]
with open(os.path.join(SRC, "概念索引.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(idx))

print("concepts:", len(concepts), "dups:", len(dup))
for t, s in dup:
    print("  DUP:", t, "<-", s)
for t in sorted(concepts):
    print("  TERM[%s] %s" % (concepts[t]["block"], t))
missing = set()
for t, c in concepts.items():
    for r in c["related"]:
        if r not in concepts:
            missing.add(r)
print("related-not-defined:", sorted(missing) if missing else "none")
