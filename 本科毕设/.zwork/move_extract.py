# -*- coding: utf-8 -*-
"""按 CLAUDE.md 结构建目录、归位 PDF、逐页提取文本与内嵌图。"""
import os, shutil, sys
import pymupdf

VAULT = r"C:\Users\18132\Documents\Obsidian Vault"
SRC = os.path.join(VAULT, "本科毕设")
EXT = os.path.join(SRC, ".zwork", "提取")
FIGS = os.path.join(EXT, "figs")
os.makedirs(EXT, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)

MAP = {
    1:  ("A协议基础与场景调研/论文1边缘计算愿景与挑战",  "Edge_Computing_Vision_and_Challenges.pdf"),
    2:  ("A协议基础与场景调研/论文2物联网消息协议调研",  "Investigating_Messaging_Protocols_for_the_Internet_of_Things_IoT.pdf"),
    3:  ("A协议基础与场景调研/论文3发布订阅协议综述",    "3567445.3571107.pdf"),
    4:  ("A协议基础与场景调研/论文4QoS级别与MQTT丢包时延相关性", "2013Correlation_analysis_of_MQTT_loss_and_delay_according_to_QoS_level.pdf"),
    5:  ("B代理实现与性能评测/论文5muMQ轻量可扩展MQTT代理", "muMQ_A_lightweight_and_scalable_MQTT_broker.pdf"),
    6:  ("B代理实现与性能评测/论文6分布式IoT边缘MQTT代理对比", "A_Comparison_of_MQTT_Brokers_for_Distributed_IoT_Edge_Computing.pdf"),
    7:  ("B代理实现与性能评测/论文7IoT边缘消息代理基准测试", "Benchmarking_Message_Brokers_for_IoT_Edge_Computing.pdf"),
    8:  ("C分布式组网与边云桥接/论文8网络边缘分布式MQTT代理消息分发", "Distributed_MQTT_Brokers_at_Network_Edges_A_Study_on_Message_Dissemination.pdf"),
    9:  ("C分布式组网与边云桥接/论文9跨组织MQTT桥接架构评估", "Evaluation_of_MQTT_Bridge_Architectures_in_a_Cross-Organizational_Context.pdf"),
    10: ("D可靠性容错与安全/论文10区块链增强MQTT容错", "Improving_Fault_Tolerance_and_Tackling_Broker_Failure_in_MQTT_through_Blockchain.pdf"),
    11: ("D可靠性容错与安全/论文11MQTT可靠性实测压力测试", "The_Price_of_Reliability_Stress-Testing_MQTT_in_Practical_IoT_Communications.pdf"),
    12: ("D可靠性容错与安全/论文12MQTT协议隐私改进", "Towards_improving_the_Privacy_in_the_MQTT_Protocol.pdf"),
}

meta = []
for n, (sub, fname) in MAP.items():
    folder = os.path.join(SRC, sub)
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, fname)
    src = os.path.join(SRC, fname)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.move(src, dst)
    if not os.path.exists(dst):
        print(f"[MISS] {n} {fname}")
        continue
    figdir = os.path.join(FIGS, str(n))
    os.makedirs(figdir, exist_ok=True)
    doc = pymupdf.open(dst)
    txt_parts = []
    seen_xref = set()
    nfig = 0
    for pno in range(len(doc)):
        page = doc[pno]
        txt_parts.append(f"\n\n===== p.{pno+1} =====\n" + page.get_text("text"))
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen_xref:
                continue
            seen_xref.add(xref)
            try:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.width < 150 or pix.height < 150 or pix.n > 4:
                    pix = None
                    continue
                if pix.colorspace and pix.colorspace.n > 3:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                nfig += 1
                if nfig <= 40:
                    pix.save(os.path.join(figdir, f"p{pno+1:03d}-img{nfig:02d}.png"))
                pix = None
            except Exception as e:
                print(f"[IMGFAIL] {n} p{pno+1} xref{xref}: {e}")
    with open(os.path.join(EXT, f"{n}.txt"), "w", encoding="utf-8") as f:
        f.write("".join(txt_parts))
    meta.append((n, fname, len(doc), os.path.getsize(os.path.join(EXT, f"{n}.txt")), nfig))
    doc.close()

with open(os.path.join(EXT, "_meta.txt"), "w", encoding="utf-8") as f:
    for n, fname, pages, size, nfig in meta:
        doc = pymupdf.open(os.path.join(SRC, MAP[n][0], fname))
        head = doc[0].get_text("text")[:700].replace("\n", " | ")
        doc.close()
        f.write(f"## 论文{n} {fname}\npages={pages} txt={size}B figs={nfig}\nHEAD: {head}\n\n")
print("DONE")
for row in meta:
    print(row)
