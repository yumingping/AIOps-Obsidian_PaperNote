# -*- coding: utf-8 -*-
"""把笔记中的旧概念链接名改写为规范名（ALIAS 反查），然后提示可跑 merge。"""
import os, re, glob

V = r"C:\Users\18132\Documents\Obsidian Vault\本科毕设"
ALIAS = {
    # 变体统一 → 规范名
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
    "Topic（主题）": "Topic（主题）",
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
n_files = n_repl = 0
for fp in glob.glob(os.path.join(V, "**", "*.md"), recursive=True):
    if ".zwork" in fp or os.path.basename(fp) in ("概念索引.md",):
        continue
    txt = open(fp, encoding="utf-8").read()
    orig = txt
    for old, new in ALIAS.items():
        pat = re.compile(r"\[\[" + re.escape(old) + r"(?=[\]|#])")
        txt = pat.sub("[[" + new, txt)
    if txt != orig:
        open(fp, "w", encoding="utf-8").write(txt)
        n_files += 1
        n_repl += sum(1 for o in ALIAS if ("[[" + o) in orig)
print("rewritten files:", n_files)
