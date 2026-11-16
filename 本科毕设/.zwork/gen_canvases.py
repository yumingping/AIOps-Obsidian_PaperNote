# -*- coding: utf-8 -*-
"""生成 12 张论文思维导图 canvas + 1 张总览 canvas（内容源自各论文精读笔记）。"""
import json, hashlib, os

VAULT = r"C:\Users\18132\Documents\Obsidian Vault"
BASE = os.path.join(VAULT, "本科毕设")

BRANCH_COLORS = ["1", "2", "5", "3", "4", "6"]  # 问题/方法/机制/数字/毕设价值/落地

def nid(key):
    return hashlib.md5(key.encode("utf-8")).hexdigest()[:16]

def leaf_h(text):
    extra = 0
    if len(text) > 26: extra += 1
    if len(text) > 52: extra += 1
    if len(text) > 78: extra += 1
    return 56 + 24 * extra

def paper_canvas(num, short, meta, folder, note_md, branches):
    nodes, edges = [], []
    # 叶子布局
    leaf_x, branch_x, center_x = 760, 380, 20
    cursor = 0
    branch_pos = []
    for bi, (title, leaves) in enumerate(branches):
        ys = []
        for leaf in leaves:
            h = leaf_h(leaf)
            nodes.append({
                "id": nid(f"{num}-leaf-{bi}-{len(ys)}"), "type": "text",
                "x": leaf_x, "y": cursor, "width": 420, "height": h,
                "text": leaf})
            ys.append((cursor, h))
            cursor += h + 24
        span = cursor - 24 - (ys[0][0])
        branch_pos.append((ys[0][0], span, bi))
        cursor += 44  # 分支组间距
    total = cursor - 44
    # 中心与分支节点
    center_id = nid(f"{num}-center")
    nodes.append({
        "id": center_id, "type": "text",
        "x": center_x, "y": total // 2 - 95, "width": 310, "height": 190,
        "text": f"# {short}\n{meta}"})
    for (start, span, bi), (title, leaves) in zip(branch_pos, branches):
        bid = nid(f"{num}-branch-{bi}")
        nodes.append({
            "id": bid, "type": "text",
            "x": branch_x, "y": start + span // 2 - 42, "width": 250, "height": 84,
            "color": BRANCH_COLORS[bi], "text": f"**{title}**"})
        edges.append({"id": nid(f"{num}-e-cb-{bi}"), "fromNode": center_id,
                      "fromSide": "right", "toNode": bid, "toSide": "left"})
        for li in range(len(leaves)):
            edges.append({"id": nid(f"{num}-e-bl-{bi}-{li}"), "fromNode": bid,
                          "fromSide": "right", "toNode": nid(f"{num}-leaf-{bi}-{li}"),
                          "toSide": "left"})
    # 精读笔记 file 节点
    fid = nid(f"{num}-file")
    nodes.append({
        "id": fid, "type": "file",
        "x": center_x, "y": total + 40, "width": 310, "height": 220,
        "file": "本科毕设/" + folder + "/" + note_md})
    edges.append({"id": nid(f"{num}-e-cf"), "fromNode": center_id,
                  "fromSide": "bottom", "toNode": fid, "toSide": "top"})
    path = os.path.join(BASE, folder, f"{num}思维导图.canvas")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=1)
    print("written:", path)

PAPERS = [
(1, "边缘计算愿景与挑战", "Shi et al.\nIEEE IoT Journal 2016\n边缘计算的开山综述", "A协议基础与场景调研/论文1边缘计算愿景与挑战", "1边缘计算愿景与挑战.md", [
 ("问题", [
  "**数据在边缘产生、计算却在云端**：500 ZB vs 云 10.4 ZB",
  "云范式假设端设备只是消费者，IoT 时代既是生产者又是消费者",
  "三类应用云撑不住：超短响应 / 隐私 / 数据量太大"]),
 ("方法", [
  "**提出 edge computing 范式**：计算放在数据源附近",
  "edge = 数据源与云之间路径上的任意算力（手机/网关/cloudlet）",
  "5 个案例落地：云卸载/视频分析/智能家居/智慧城市/协同边缘"]),
 ("关键机制", [
  "edgeOS 三层：通信 → 数据抽象 → 服务管理，Naming 纵贯全层",
  "computing stream：计算跟着数据走的一条「加工流水线」",
  "六大挑战：可编程/命名/数据抽象/服务管理/隐私安全/优化指标"]),
 ("关键数字", [
  "人脸识别搬到边缘：900 → 169 ms",
  "cloudlet 能耗降 30–40%，CloneCloud 降 20×",
  "45% 的 IoT 数据将在边缘处理、不上云"]),
 ("毕设价值", [
  "绪论动机段的四个论证数字（p.1–3）",
  "总体架构章直接套 edgeOS 分层画法（p.4）",
  "测试维度：latency / bandwidth / energy / cost（p.8–9）"]),
 ("落地动作", [
  "树莓派网关 = Edge 带的实体落点",
  "消息流水线：订阅 → 过滤聚合 → 必要数据上云",
  "遗嘱/断线重连 ↔ 可靠性三视角一一对应"]),
]),
(2, "物联网消息协议调研", "Al-Masri et al.\nIEEE Access 2020\n六协议九维横评", "A协议基础与场景调研/论文2物联网消息协议调研", "2物联网消息协议调研.md", [
 ("问题", [
  "IoT 协议几十种、选型困难，系统常多协议并存",
  "HTTP 头 200B–2KB，MQTT 最小包 2 字节——差两个数量级",
  "已有综述只看单层协议，缺 OSI 全栈串联"]),
 ("方法", [
  "按 Eclipse 采用率 + 10 大云平台支持选定 6 协议",
  "九个维度横向比较（互操作/性能/可靠性/安全…）"]),
 ("关键机制", [
  "MQTT：broker 居中 + QoS 0/1/2，D2C 型",
  "AMQP：exchange → binding → queue 三级路由",
  "DDS：全局数据空间、无 broker、23 种 QoS"]),
 ("关键数字", [
  "功耗 HTTP = 5.3 × MQTT",
  "订阅扇出 trans_msg = n×topic_avg，最坏 n²",
  "实现体积差 3 个数量级：CoAP 14KB vs DDS 640MB+"]),
 ("毕设价值", [
  "「为什么选 MQTT」的四条证据链",
  "九维评估表改造成第 2 章协议对比表",
  "界定 MQTT 边界：大 payload 最差、broker 是 SPoF"]),
 ("落地动作", [
  "topic 命名要短，网关做缩写映射",
  "broker 入口校验 topic/UTF-8 防 DoS",
  "payload 大小必须作为测试变量（结论会反转）"]),
]),
(3, "发布订阅协议综述", "Nast et al.\nIoT '22 (ACM)\n8 协议 × 5 条工业需求", "A协议基础与场景调研/论文3发布订阅协议综述", "3发布订阅协议综述.md", [
 ("问题", [
  "IIoT 新增实时 + 高可靠要求，IoT 协议未必满足",
  "已有综述缺工业需求视角"]),
 ("方法", [
  "先立 5 条需求：互操作/安全/可扩展/实时/可靠",
  "再给 8 个 pub/sub 协议逐条打分"]),
 ("关键机制", [
  "**TCP 保可靠不实时；UDP 潜在实时但可靠性要自建**",
  "OPC UA：唯一完全满足三层互操作（数据建模强）",
  "broker-based 架构天生带 SPOF"]),
 ("关键数字", [
  "15 篇综述中 MQTT 出现 14 次（关注度第一）",
  "HiveMQ 集群验证到百万级设备",
  "**没有任何协议全部满足 5 条需求**"]),
 ("毕设价值", [
  "五需求矩阵 = 毕设选型评估框架",
  "引 Table 2 论证选 MQTT 并声明实时边界",
  "「缺真实性能评估」支撑任务6 必要性"]),
 ("落地动作", [
  "架构图按协议栈四层画（应用/传输/网络/接口）",
  "默认 TCP+TLS：接受时延换可靠，写明取舍",
  "架构图标注单点（MQTT-SN gateway 教训）"]),
]),
(4, "QoS级别与MQTT丢包时延相关性", "Lee et al.\nICOIN 2013\n三级 QoS 真网实测", "A协议基础与场景调研/论文4QoS级别与MQTT丢包时延相关性", "4QoS级别与MQTT丢包时延相关性.md", [
 ("问题", [
  "QoS 越高越可靠但越慢——代价差异没有定量依据",
  "OMNeT++ 仿真结果不可信"]),
 ("方法", [
  "真实商业网络抓包实测（非仿真）",
  "有线 / 无线 3G 双对照组",
  "payload 1k–16k × QoS 0/1/2 全组合"]),
 ("关键机制", [
  "QoS0 一报文 / QoS1 两报文 / QoS2 四次握手",
  "时延 = 沿途时间戳累差；丢包 = 重传请求计数",
  "测量窗口固定 5 分钟"]),
 ("关键数字", [
  "有线时延 0.03–0.14 s，无线 3G 0.4–1.0 s",
  "QoS2 丢包 ≈0.15% vs QoS0/1 ≈1.4%",
  "时延与丢包强相关：r >0.77（QoS2 达 0.991）",
  "payload >4000B 分片推高时延"]),
 ("毕设价值", [
  "任务3 的 QoS 选型依据",
  "任务6 实验设计可直接照搬"]),
 ("落地动作", [
  "Ubuntu：mosquitto + tcpdump + Wireshark 复现",
  "小消息用 QoS0/1，关键告警用 QoS2",
  "订阅端按 packet id 去重（QoS1 会重复）"]),
]),
(5, "muMQ轻量可扩展MQTT代理", "Pipatsakulroj et al.\nIEEE 2017\n多核 broker 实现论文", "B代理实现与性能评测/论文5muMQ轻量可扩展MQTT代理", "5muMQ轻量可扩展MQTT代理.md", [
 ("问题", [
  "Mosquitto 单线程只用一核，堆硬件没用",
  "内核 TCP 栈系统调用开销 + 多核资源竞争"]),
 ("方法", [
  "**每核一个 epoll 事件循环 + SO_REUSEPORT**",
  "mTCP 用户态 TCP 栈（kernel bypass，可选路径）"]),
 ("关键机制", [
  "预分配、fd 索引的 client 表",
  "topic 树 + 根节点读写锁（SUB 写锁 / PUB 读锁）",
  "每核 1:1 的 App/TCP 线程对，跨核走消息队列"]),
 ("关键数字", [
  "约 3K 行 C，移植 mTCP 只改 90 行",
  "50 对时 944K msg/s = 5.38 × Mosquitto",
  "Mosquitto 上限约 128K 订阅者（时延 1743 ms）",
  "mTCP 版 PMD 忙轮询恒占 1600% CPU"]),
 ("毕设价值", [
  "单机 broker 多核化的标准答案",
  "多核可扩展是主因，mTCP 只是第二层增益",
  "忙轮询不适合电池网关 → 论证选内核 epoll"]),
 ("落地动作", [
  "C++：epoll + SO_REUSEPORT + pthread 读写锁",
  "树莓派 4 核绑核压测（taskset）验证线性扩展",
  "架构图画出跨核消息队列路径"]),
]),
(6, "分布式IoT边缘MQTT代理对比", "Koziolek et al.\nECSA 2020\nGQM 六维集群实测", "B代理实现与性能评测/论文6分布式IoT边缘MQTT代理对比", "6分布式IoT边缘MQTT代理对比.md", [
 ("问题", [
  "分布式 broker 20+ 个怎么选",
  "已有评测：只测单机、只看性能、结论难泛化"]),
 ("方法", [
  "GQM 六维：性能/扩展/韧性/安全/扩展机制/易用",
  "StarlingX + K8s 边缘集群实测 EMQX/HiveMQ/VerneMQ"]),
 ("关键机制", [
  "对称 10 pub + 10 sub 场景，payload 150B，QoS 1",
  "MST 判据：消费落后发布 > 100 msg/s",
  "崩溃注入：杀 broker 进程看重连补偿"]),
 ("关键数字", [
  "MST：EMQX 28K / VerneMQ 10K / HiveMQ 8K msg/s",
  "崩溃丢消息：HiveMQ 0 / VerneMQ 82 / EMQX 580",
  "TLS 开销：EMQX 43% / VerneMQ 20%",
  "可靠性参数：inflight 1000 + offline queue 50000"]),
 ("毕设价值", [
  "任务6 方法学：梯度加压/重复 3 次/95%CI/双源验证",
  "崩溃判读三特征：重连耗时/补偿段/恢复基线",
  "autoscaling 只对新增连接生效（坑）"]),
 ("落地动作", [
  "Ubuntu：docker 部署 EMQX 做对照组",
  "HAProxy TCP 健康检查做 broker 切换",
  "kill -9 注入崩溃 + 持久会话验收"]),
]),
(7, "IoT边缘消息代理基准测试", "Paul et al.\narXiv 2026\nmq-bench：8 broker 横评", "B代理实现与性能评测/论文7IoT边缘消息代理基准测试", "7IoT边缘消息代理基准测试.md", [
 ("问题", [
  "MQ 生态跨度太大，缺可比条件的横评",
  "已有评测忽视 CPU/内存与资源约束"]),
 ("方法", [
  "Rust 版 mq-bench 统一框架横评 8 个 broker",
  "1–4 vCPU 三档资源 × 并发 500→10000 对"]),
 ("关键机制", [
  "消息头内嵌 64-bit 纳秒时间戳",
  "open-loop 令牌桶限速，暴露真实饱和点",
  "Toxiproxy 注入 TCP RST（MTTF 30s / MTTR 5s）",
  "只报 p50/p95，吞吐只统计稳定期"]),
 ("关键数字", [
  "多线程 native（NATS/Zenoh）90K msg/s",
  "单线程 Mosquitto 饱和 45K msg/s",
  "QoS0 丢 6.3–6.6% vs QoS1/2 全部 0%",
  "JVM 系内存高 10–50 倍"]),
 ("毕设价值", [
  "任务6 指标口径的权威模板",
  "三档边缘硬件画像（网关/工控机/雾节点）",
  "按负载 × 资源选 broker 的部署指南"]),
 ("落地动作", [
  "树莓派 ≈ 1 vCPU/2GB 档做资源画像",
  "docker stats 采 CPU/内存（1s 采样）",
  "C++：ACK 异步化，防 QoS2 串行阻塞（3.6×）"]),
]),
(8, "网络边缘分布式MQTT代理消息分发", "Hao et al.\nIEEE Cybermatics 2022\nSSF 选择性订阅转发", "C分布式组网与边云桥接/论文8网络边缘分布式MQTT代理消息分发", "8网络边缘分布式MQTT代理消息分发.md", [
 ("问题", [
  "边缘链路容量与算力受限",
  "泛洪（PF/SF）不看 topic 层级，冗余流量大"]),
 ("方法", [
  "**SSF：转发订阅前做 topic 包含判定**",
  "只发未被已有订阅覆盖的订阅"]),
 ("关键机制", [
  "包含判定 O(min 层数) 线性时间，工程可行",
  "broker 间订阅永不重复、永不重叠",
  "退订时补发被覆盖的窄订阅（防漏报）",
  "假设网络无环"]),
 ("关键数字", [
  "SSF 比 SF 省订阅流量 42–73%",
  "最坏情形比 PF 省 81% 总流量",
  "时延：PF 204 / SF 126 / SSF 101（时间槽）",
  "丢包 5→15% 时延 3.0→6.5 s 非线性恶化"]),
 ("毕设价值", [
  "三层边云架构：边缘主力、云只协调",
  "桥接模块「该不该再转发」的判据",
  "IBR/SPR 两参数扫测试矩阵"]),
 ("落地动作", [
  "Mosquitto bridge = SF 特例，直接可用",
  "包含判定几十行 C++ 接在转发前",
  "7 节点 Docker 实测 + Wireshark 算流量"]),
]),
(9, "跨组织MQTT桥接架构评估", "Lima et al.\nICSA 2025\nclient 侧桥接 benchmark", "C分布式组网与边云桥接/论文9跨组织MQTT桥接架构评估", "9跨组织MQTT桥接架构评估.md", [
 ("问题", [
  "跨组织有管理壁垒 + 信任边界，broker 侧桥接行不通",
  "单 broker 架构在真实场景不适用"]),
 ("方法", [
  "client 侧桥：订阅 → 转换 → 再发布，broker 零改动",
  "两种粒度对比：AUT1 每 provider 1 桥 vs AUT2 每流 1 桥"]),
 ("关键机制", [
  "MQTT5：No Local 防回环 + Retain As Published",
  "通配符订阅按 provider 聚合 topic",
  "收发端同主机保证时钟同步"]),
 ("关键数字", [
  "跨网+TLS 时延：QoS0/1/2 = 132/185/217 ms",
  "QoS0 下 125KB 流每千条丢 997 条；1.5KB 只丢 1",
  "桥实例翻倍只慢 3–5 ms（传输成本 > 处理成本）",
  "topic 15B vs 29B 差 ≤ 1.4 ms"]),
 ("毕设价值", [
  "边云桥接数据流的直接模板",
  "「传输成本 > 处理成本」的选型论据",
  "QoS 1 作默认档的实证依据"]),
 ("落地动作", [
  "C++ bridge 进程：通配订阅 + 转换 + 再发布",
  "启用 No Local / RAP 防回环",
  "10 轮重复 × 4000 条，消息带时间戳"]),
]),
(10, "区块链增强MQTT容错", "Paul et al.\nICAECT 2023\n链上容错 PoC", "D可靠性容错与安全/论文10区块链增强MQTT容错", "10区块链增强MQTT容错.md", [
 ("问题", [
  "规范：每 clientID 只 1 条 retained；无 broker 端容错",
  "边缘 broker 内存存不下大量未确认消息"]),
 ("方法", [
  "3 层架构：链上 3 合约 + broker 池 + 负载均衡",
  "合约管：retained 队列 / 死信队列 / BNS 域名"]),
 ("关键机制", [
  "retained → 按 topic 的链上队列",
  "未确认消息 → 链上 DLQ，重连补发",
  "客户端连固定域名，故障时 topic 迁移",
  "客户端零改动"]),
 ("关键数字", [
  "**无量化数据（仅 PoC 截图演示）**",
  "Node.js broker + SCILLA/Zilliqa 公链",
  "每条 retained/未确认消息 = 一笔链上事务"]),
 ("毕设价值", [
  "**对比方案，不是推荐方案**",
  "论证 broker 故障切换的必要性",
  "反面教材：机制必须配量化对比"]),
 ("落地动作", [
  "去区块链版：SQLite 落盘补发队列",
  "nginx/HAProxy 健康检查 + 固定接入地址",
  "S1 稳定 + S2 频繁断连的现成测试用例"]),
]),
(11, "MQTT可靠性实测压力测试", "Gaspar et al.\nIEEE IoT Magazine 2026\n7 参数全组合压测", "D可靠性容错与安全/论文11MQTT可靠性实测压力测试", "11MQTT可靠性实测压力测试.md", [
 ("问题", [
  "真实硬件 + 真实参数组合下 QoS 的代价无系统实测",
  "e-Health 场景选 QoS 无现成答案"]),
 ("方法", [
  "11 块单板机 + 隔离千兆有线网",
  "7 参数全组合：1944 配置 × 10 次 × 8700 万条"]),
 ("关键机制", [
  "RTT 口径按 QoS 分层（PUBACK/PUBCOMP/TCP ACK）",
  "Time Factor = 实际耗时 / 理论最短耗时",
  "CPU 配额故意掐算力逼出可靠性下限"]),
 ("关键数字", [
  "RTT 3.38 / 20.06 / 53.45 ms（QoS0/1/2）",
  "丢包 0.77 / 0.36 / 0.19%（随 QoS 下降）",
  "10 客户端是拐点：丢包 1.75%、长尾爆发",
  "CPU 25→100%：丢包 43.6%→0.42%"]),
 ("毕设价值", [
  "任务6 测试矩阵直接照抄",
  "报均值±标准差暴露长尾",
  "区分连接瓶颈 vs 聚合吞吐瓶颈"]),
 ("落地动作", [
  "systemd CPUQuota=25% 复现 CPU 实验",
  "树莓派当 publisher 集群 + 有线交换机",
  "网关不给 mosquitto 进程限 CPU"]),
]),
(12, "MQTT协议隐私改进", "Fischer et al.\nIEEE 2019\nAOTP topic 混淆", "D可靠性容错与安全/论文12MQTT协议隐私改进", "12MQTT协议隐私改进.md", [
 ("问题", [
  "**topic 必须对 broker 明文 → 作息可被画像**",
  "TLS 只保传输层，不管元数据"]),
 ("方法", [
  "5 种 topic 混淆，全部只在客户端做",
  "实现并验证 AOTP（进阶一次性口令）"]),
 ("关键机制", [
  "PRF 同步随机 topic（DHKE 传种子）",
  "hash 链一次性口令：每环只用一次",
  "AOTP = 隔项掺盐递推 + 随机多项式",
  "用 p/# 通配订阅过滤无关消息"]),
 ("关键数字", [
  "AOTP 解混淆 1–13 ms（RPi），占远程时延 10%",
  "ESP8266 上约 120 ms（MCU 不做解混淆）",
  "明文本地基线 3.7 ms",
  "方案 A 的 payload 体积 +33%"]),
 ("毕设价值", [
  "「安全与展望」章的扩展素材",
  "混淆 vs 明文 × 本地 vs 远程 2×2 实验",
  "混淆 ≠ 加密：统计侧信道仍是开放问题"]),
 ("落地动作", [
  "网关做混淆/解混淆，MCU 只采集发布",
  "映射表按发布频率排序降低试错开销",
  "C++：OpenSSL HMAC/SHA-256 实现 hash 链"]),
]),
]

for spec in PAPERS:
    paper_canvas(*spec)

# ============ 总览 canvas ============
def overview():
    nodes, edges = [], []
    blocks = [
        ("A 协议基础与场景调研（任务1）", "为什么需要边缘轻量中间件、为什么选 MQTT", "A协议基础与场景调研", [
            ("1边缘计算愿景与挑战", "论文1边缘计算愿景与挑战/1边缘计算愿景与挑战.md", "Shi et al. · IEEE IoT J 2016"),
            ("2物联网消息协议调研", "论文2物联网消息协议调研/2物联网消息协议调研.md", "Al-Masri et al. · IEEE Access 2020"),
            ("3发布订阅协议综述", "论文3发布订阅协议综述/3发布订阅协议综述.md", "Nast et al. · IoT '22"),
            ("4QoS级别与MQTT丢包时延相关性", "论文4QoS级别与MQTT丢包时延相关性/4QoS级别与MQTT丢包时延相关性.md", "Lee et al. · ICOIN 2013")], "5"),
        ("B 代理实现与性能评测（任务3、6）", "单机 broker 怎么实现、怎么评测", "B代理实现与性能评测", [
            ("5muMQ轻量可扩展MQTT代理", "论文5muMQ轻量可扩展MQTT代理/5muMQ轻量可扩展MQTT代理.md", "Pipatsakulroj et al. · 2017"),
            ("6分布式IoT边缘MQTT代理对比", "论文6分布式IoT边缘MQTT代理对比/6分布式IoT边缘MQTT代理对比.md", "Koziolek et al. · ECSA 2020"),
            ("7IoT边缘消息代理基准测试", "论文7IoT边缘消息代理基准测试/7IoT边缘消息代理基准测试.md", "Paul et al. · arXiv 2026")], "2"),
        ("C 分布式组网与边云桥接（任务2、5）", "多 broker 怎么组网、边云怎么桥接", "C分布式组网与边云桥接", [
            ("8网络边缘分布式MQTT代理消息分发", "论文8网络边缘分布式MQTT代理消息分发/8网络边缘分布式MQTT代理消息分发.md", "Hao et al. · 2022"),
            ("9跨组织MQTT桥接架构评估", "论文9跨组织MQTT桥接架构评估/9跨组织MQTT桥接架构评估.md", "Lima et al. · ICSA 2025")], "4"),
        ("D 可靠性容错与安全（任务4）", "broker 故障容错、可靠性边界、隐私", "D可靠性容错与安全", [
            ("10区块链增强MQTT容错", "论文10区块链增强MQTT容错/10区块链增强MQTT容错.md", "Paul et al. · ICAECT 2023"),
            ("11MQTT可靠性实测压力测试", "论文11MQTT可靠性实测压力测试/11MQTT可靠性实测压力测试.md", "Gaspar et al. · IEEE IoT Mag 2026"),
            ("12MQTT协议隐私改进", "论文12MQTT协议隐私改进/12MQTT协议隐私改进.md", "Fischer et al. · 2019")], "6"),
    ]
    GX, GW, GAP = 0, 640, 90
    GY = 0
    group_ids = {}
    bottom = 0
    for gi, (label, desc, folder, papers, color) in enumerate(blocks):
        x = gi * (GW + GAP)
        inner_w = 520
        ph, pgap = 190, 30
        gh = 90 + len(papers) * ph + (len(papers) - 1) * pgap + 40
        gid = nid(f"ov-group-{gi}")
        group_ids[gi] = gid
        nodes.append({"id": gid, "type": "group", "x": x, "y": GY,
                      "width": GW, "height": gh, "color": color, "label": label})
        nodes.append({"id": nid(f"ov-gdesc-{gi}"), "type": "text",
                      "x": x + 30, "y": GY + 40, "width": inner_w, "height": 56,
                      "text": f"*{desc}*"})
        py = GY + 40 + 56 + 20
        for pi, (short, rel, meta) in enumerate(papers):
            nodes.append({
                "id": nid(f"ov-paper-{gi}-{pi}"), "type": "file",
                "x": x + 30, "y": py, "width": inner_w, "height": ph,
                "file": "本科毕设/" + folder + "/" + rel})
            py += ph + pgap
        bottom = max(bottom, GY + gh)
    # 标题 + 故事线
    nodes.append({"id": nid("ov-title"), "type": "text",
                  "x": 900, "y": -330, "width": 640, "height": 200,
                  "text": "# 面向边缘计算场景的轻量级消息中间件研究与实现\n西安电子科技大学 · 本科毕设 · 2026-11 → 2027-05\n\n**故事线**：为什么需要边缘轻量中间件（A）→ 单机 broker 实现与评测（B）→ 多 broker 组网桥接（C）→ 可靠性与安全（D）"})
    # 故事线箭头
    edges.append({"id": nid("ov-e-ab"), "fromNode": group_ids[0], "fromSide": "right",
                  "toNode": group_ids[1], "toSide": "left", "color": "6", "label": "协议基础"})
    edges.append({"id": nid("ov-e-bc"), "fromNode": group_ids[1], "fromSide": "right",
                  "toNode": group_ids[2], "toSide": "left", "color": "6", "label": "单点瓶颈引出分布式"})
    edges.append({"id": nid("ov-e-bd"), "fromNode": group_ids[1], "fromSide": "bottom",
                  "toNode": group_ids[3], "toSide": "top", "color": "6", "label": "实现可靠性"})
    edges.append({"id": nid("ov-e-cd"), "fromNode": group_ids[2], "fromSide": "bottom",
                  "toNode": group_ids[3], "toSide": "top", "color": "6", "label": "组网保可靠"})
    edges.append({"id": nid("ov-e-dt"), "fromNode": group_ids[0], "fromSide": "bottom",
                  "toNode": group_ids[3], "toSide": "left", "color": "3",
                  "label": "QoS 实测基线（论文4→11）", "fromEnd": "none", "toEnd": "arrow"})
    # 任务书 chips
    tasks = [
        ("任务1 协议与现状调研", 0), ("任务2 总体架构设计", 2), ("任务3 发布订阅模块（QoS 0/1/2）", 1),
        ("任务4 持久化/断线重连/遗嘱", 3), ("任务5 边云桥接与组网测试", 2), ("任务6 性能测试与论文撰写", 1)]
    tx, ty = 60, bottom + 120
    for ti, (t, bi) in enumerate(tasks):
        tid = nid(f"ov-task-{ti}")
        nodes.append({"id": tid, "type": "text", "x": tx, "y": ty, "width": 300, "height": 84,
                      "color": "3", "text": f"**{t}**"})
        edges.append({"id": nid(f"ov-e-task-{ti}"), "fromNode": tid, "fromSide": "top",
                      "toNode": group_ids[bi], "toSide": "bottom"})
        tx += 330
    path = os.path.join(BASE, "毕设论文总导图.canvas")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=1)
    print("written:", path)

overview()
print("ALL DONE")
