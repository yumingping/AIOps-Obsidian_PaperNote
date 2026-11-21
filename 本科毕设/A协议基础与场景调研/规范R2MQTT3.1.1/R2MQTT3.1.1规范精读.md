# R2 MQTT3.1.1规范精读

> **MQTT Version 3.1.1**（MQTT 3.1.1 版规范）/ OASIS Standard / 2014-10-29 发布 / 全文 81 页（亦即 ISO/IEC 20922:2016）。
> 页码口径：**物理页码**（PDF 第 1 页 = p.1，正文从 p.9 起，附录 p.68 起）。配套：[[R1MQTT5.0规范精读]]（现行主力版）· 总进度：[[毕设完成流程书]]。
> 阅读定位：3.1.1 是 MQTT **最简形态**——没有属性区、没有数值化原因码，报文定长字段一目了然。**建议先按本篇把 broker 语义跑通，再叠加 5.0 的增量特性**（分工见两篇笔记末尾的三档分类）。

## 一、这份规范规定了什么（§1，p.9–15）

- **含义**：与 v5.0 相同的 [[发布订阅模式]] 协议，但只有 **14 种报文**（type 15 为 Reserved 禁用，Table 2.1，p.16–17）。三种角色：Client（终端）→ Server（[[Broker（消息代理）]]）→ Session（会话）。
- **为什么先读它**：报文里每个字段都「有一个且只有一个位置」，没有可选属性——最适合第一次手写编解码器对照；而且 3.1.1 客户端（老设备、老 SDK）在边缘场景依然大量存在，broker 支持它是兼容性加分项。
- 术语（p.9–10）：Subscription = Topic Filter + 最大 QoS，挂在单个 Session 下；Session 可跨越多次网络连接。

## 二、字节怎么排：数据表示与报文结构（§1.5 + §2，p.13–22）

### 2.1 数据表示（§1.5，p.13–15）

- 16 位整数**大端序**（p.13）；UTF-8 字符串 = 2 字节长度前缀 + 内容，上限 65,535 字节（p.13）。
- 收到 ill-formed UTF-8 或 U+0000 → **必须断连**（[MQTT-1.5.3-1/-2]，p.14）。
- **Remaining Length 变长编码**（§2.2.3，p.18–19）：每字节低 7 位数据 + 最高位续位，最多 4 字节，上限 268,435,455（256 MB，`0xFF 0xFF 0xFF 0x7F`）；编码/解码伪码在 p.19（条目 280–306）。与 5.0 的 VBI 是同一机制——**先按 3.1.1 写好它，5.0 直接复用**。

### 2.2 报文结构与 flags（§2，p.16–22）

- 三段结构：Fixed header → Variable header → Payload（p.16）。
- flags 规则（Table 2.2，p.17–18）：与 5.0 相同——PUBLISH 用 DUP/QoS/RETAIN；PUBREL/SUBSCRIBE/UNSUBSCRIBE 固定 `0010`；其余全 0；非法 flags 必须断连（p.17）。
- **Packet Identifier**（§2.3.1，p.20–21）：非零、收到对应确认后才可复用；QoS0 的 PUBLISH 禁止携带（[MQTT-2.3.1-5]）；重发必须用同一 ID。
- 有/无 Variable header 与 Payload 的报文分布表（Table 2.6，p.21–22）：PINGREQ/PINGRESP/DISCONNECT 三者**既无变长头也无 Payload**（DISCONNECT 固定 2 字节）。

## 三、14 种报文逐个拆（§3，p.23–50）

### 3.1 CONNECT / CONNACK（p.23–33）

- **CONNECT**（p.23–31）：变长头固定 10 字节：`Protocol Name "MQTT"（0x00 0x04 'MQTT'）→ Level=4 → Connect Flags → Keep Alive`。**没有属性区**——与 5.0 的唯一结构差异就在这里。
  - Connect Flags（byte 8，p.24–27）：bit7 User Name / bit6 Password / bit5 Will Retain / bit4-3 Will QoS / bit2 Will Flag / bit1 **Clean Session** / bit0 必须为 0。
  - **Clean Session**（p.24–25）：=0 → 恢复/新建持久会话，断开后双方必须保存状态，Server 还必须存断连期间匹配其订阅的 QoS1/2 消息；=1 → 会话随连接生灭。[[持久会话（Persistent Session）]] 的最简开关。
  - **Will**（p.26–27，[[遗嘱消息]]）：异常断开（I/O 故障、Keep Alive 超时、未发 DISCONNECT）时发布；收到 DISCONNECT 则删除。**没有 Will Delay**（遗嘱即时发）。
  - **Keep Alive**（p.27–28）：非零时空闲发 PINGREQ；Server **1.5×Keep Alive** 内没收到任何报文必须断开（[MQTT-3.1.2-24]，p.28）；=0 关闭心跳。
  - Payload 顺序（p.29–30）：`ClientID → Will Topic → Will Message → User Name → Password`（[MQTT-3.1.3-1]）。ClientID 必须存在：1–23 字节 `[0-9a-zA-Z]` 必须接受；0 字节 ID 的客户端**必须**同时置 CleanSession=1，0 字节 + CleanSession=0 → CONNACK 0x02 拒绝（[MQTT-3.1.3-8/-9]，p.29）。Password 是二进制数据不是 UTF-8 串（p.30）。
  - 同 ClientID 已在线 → **必须断开旧连接**（[MQTT-3.1.4-2]，p.30）；CONNECT 不合规 → 直接断连**不发 CONNACK**（[MQTT-3.1.4-1]，p.31）。
- **CONNACK**（p.31–33）：固定 4 字节（首字节 0x20，Remaining Length=2）：byte1 bit0 = **Session Present**，byte2 = 返回码（Table 3.1，p.32–33）：

  | 码 | 含义 |
  |---|---|
  | 0x00 | 接受连接 |
  | 0x01 | 协议版本不支持 |
  | 0x02 | ClientID 被拒绝 |
  | 0x03 | 服务不可用 |
  | 0x04 | 用户名/密码错误 |
  | 0x05 | 未授权 |

  发非零返回码后必须关连接（p.32）。

### 3.2 PUBLISH + 四个确认（p.33–40）

- **PUBLISH**（p.33–37）：flags = DUP/QoS/RETAIN（与 5.0 同义）。
  - **DUP**（p.33–34）：=1 表示重发；Server 转发时**不继承**入站 DUP；DUP=1 不能证明之前发过。
  - **RETAIN**（p.34–35，[[保留消息（Retained Message）]]）：置 1 存「最后一条」；**0 字节 payload + RETAIN=1 = 删除保留消息**（[MQTT-3.3.1-10/-11]）；新订阅时每匹配主题发一条（RETAIN=1），既有订阅匹配转发时 RETAIN=0（p.34）。**没有 Retain Handling/No Local/RAP 选项**。
  - QoS=3（两位全 1）禁止，收到必须断连（[MQTT-3.3.1-4]，p.34）。
  - Variable header：Topic Name（禁通配符）+ Packet ID（仅 QoS1/2）。
  - 重叠订阅按最大 QoS 投递；实际下发 QoS = min(发布 QoS, 授予 QoS)（p.36–37、p.43）。
- **PUBACK(0x40)/PUBREC(0x50)/PUBREL(0x62)/PUBCOMP(0x70)**（p.37–40）：全部固定 4 字节（2 字节 PID，无 Payload，无原因码）。**出错的唯一动作是断连**——这是与 5.0 最大的行为差异。

### 3.3 SUBSCRIBE / SUBACK / UNSUBSCRIBE / UNSUBACK（p.40–48）

- **SUBSCRIBE**（p.40–43）：`PID → 若干 (Topic Filter + 1 字节 Requested QoS)`；QoS 字节高 6 位必须为 0；空 Payload 违规（p.41–42）。
- **SUBACK**（p.43–45）：返回码列表与 filter 顺序一致，**允许值仅 4 个**：0x00/0x01/0x02（授予 QoS0/1/2）、0x80（失败）（[MQTT-3.9.3-2]，p.44）——想做「部分拒绝」只有 0x80 一个选择。
- **UNSUBSCRIBE**（p.45–47）：filter **逐字符精确匹配**才删除；没删到任何订阅也必须回 UNSUBACK（p.47）。
- UNSUBACK（p.47–48）：固定 4 字节。

### 3.4 PINGREQ / PINGRESP / DISCONNECT（p.48–50）

- PINGREQ(0xC0)/PINGRESP(0xD0)：固定 2 字节心跳，收到必回（p.48）。
- **DISCONNECT**（p.49–50）：固定 2 字节，**仅 Client→Server**（5.0 里 Server 也能发）；客户端发完后不得再发任何报文；Server 收到后**必须丢弃遗嘱**（[MQTT-3.14.4-3]）。

## 四、broker 行为规则（§4，p.51–59）——与 5.0 同源，细节更简

### 4.1 状态存储（p.51）

Session state 由 Client 和 Server **各自**持有（清单见 §3.1.2.4，p.25：订阅表、已发未确认 QoS1/2、待发队列、已收未确认 QoS2 等）；**保留消息不属于 Session state**（p.51）。这就是 C++ Session 结构体的字段清单（同 [[R1MQTT5.0规范精读]] §4.1 的七项清单，少了「会话到期时刻」一项）。

### 4.2 网络连接（p.52)

必须有序、无损、双向字节流；端口 1883 / 8883（TLS）。

### 4.3 QoS 0/1/2 消息流（p.52–55）★核心

- QoS0（p.52）：发出即不管。
- QoS1（p.53）：`PUBLISH → PUBACK`；发出 PUBACK 后同 PID 的 PUBLISH 一律按新消息处理（[MQTT-4.3.2-2]）。
- **QoS2 四步握手**（p.54–55，[[QoS 2 四次握手（4-way handshake）]]）：`PUBLISH → PUBREC → PUBREL → PUBCOMP`，方向与约束同 5.0（发出 PUBREL 后不得再重发 PUBLISH；PUBREL 前重复 PUBLISH 只回 PUBREC 不重复投递）。规范还给出接收方 Method A/B 两种实现（在 PUBREC 或 PUBCOMP 时点投递下游，p.55）——选一种即可，不影响保证。
- **重发**（§4.4，p.55）：**唯一强制场景** = CleanSession=0 重连时，用**原 Packet Identifier** 重发全部未确认的 PUBLISH/PUBREL（[MQTT-4.4.0-1]）；连接存活期间没有定时重发要求。

### 4.4 消息顺序（p.56）

确认报文按序回；同主题同 QoS 按收到顺序投递（默认 Ordered Topic）。非规范注释：in-flight 窗口设为 1 可完全保序（p.56）——压测时「窗口=1 vs 窗口>1」就是一组现成对比实验。

### 4.5 主题语法（p.57–59）

与 5.0 完全一致：`/` 分层；通配符只进 filter 不进 topic name；`#` 必须结尾且独立成层、`+` 必须独占一层（[[通配符（wildcard）]]）；`$` 开头主题不被 `#`/`+` 匹配（[MQTT-4.7.2-1]，p.58）；匹配逐字符、不归一化（p.59）。**注意 3.1.1 无共享订阅**（`$share/` 会被当成普通层级）。

### 4.6 错误处理（p.59）

协议违规一律断连（[MQTT-4.8.0-1]）；Transient Error（如缓冲满）处理入站报文时遇到 → 断开该连接，但**不应影响其他客户端**（[MQTT-4.8.0-2]）——broker 隔离故障的规范依据。

## 五、安全章与附录（§5–7 + 附录，p.60–81）——可等区

- §5（p.60–64）整章非规范：建议 TLS 用 8883；**协议不信任对称——没有客户端认证服务器的机制**（§5.4.3，p.61–62），双向认证靠 TLS 证书；三层安全档案（明文/VPN/TLS，p.64）。写论文引用即可，结合 [[12MQTT协议隐私改进]]。
- §6 WebSocket（p.65，规范性）：二进制帧承载、子协议名 `mqtt`——毕设可跳过。
- §7 Conformance（p.66–67）：合规 = 满足各自侧全部 MUST，且**不得要求实现规范外扩展**（[MQTT-7.0.0-2]）——「合法偷懒」的出处。
- 附录 A 致谢（p.68–69，MQTT 原始发明人 Andy Stanford-Clark 与 Arlen Nipper）；附录 B 全部 MUST 语句索引（p.70–79，查证用）；附录 C 修订史（p.80–81）。

## 六、3.1.1 没有（与 5.0 的差异速查）

1. 无 Properties 属性区（报文定长字段，p.16–50 通篇无属性机制）。
2. 无数值化 Reason Code（仅 CONNACK 0x00–0x05、SUBACK 0x00–0x02/0x80；其余出错 = 断连）。
3. 无共享订阅、无消息过期、无 Topic Alias、无请求/响应模式。
4. 会话寿命只有 CleanSession 二选一，不可协商。
5. Keep Alive 超时固定 1.5×，Server 不能放宽（[MQTT-3.1.2-24]，p.27）。
6. DISCONNECT 仅 C→S；报文数 14（无 AUTH）。

## 七、哪些部分可以等（三档分类）★

> 判断标准同 [[R1MQTT5.0规范精读]] 第八节。括号内为 [[毕设完成流程书]] 对应周次。

### 🔴 必须先做（W8–W12）

- Remaining Length 编解码 + Fixed Header 类型/flags 校验（§2.2）。
- CONNECT/CONNACK 全套：Protocol Name/Level 校验、Connect Flags、ClientID 规则（含 0 字节 + CleanSession=1 组合）、返回码 0x00–0x05、Session Present、挤掉旧连接（§3.1–3.2）。
- UTF-8 合法性校验（非法即断连，§1.5.3）。
- PUBLISH QoS0/1 + PUBACK；PID 规则（§2.3.1、§3.3–3.4）。
- SUBSCRIBE/SUBACK（QoS 字节校验、0x80 失败、min 降级）、UNSUBSCRIBE/UNSUBACK、PING、DISCONNECT（含遗嘱丢弃）（§3.8–3.14）。
- 主题匹配引擎（`+`/`#`/`$`，§4.7）+ 保留消息（含 0 字节删除惯用法，§3.3.1.3）。
- CleanSession=0 持久会话 + Session state 清单（§3.1.2.4、§4.1）+ Keep Alive 1.5×（§3.1.2.10）。

### 🟡 要做但可后置（W12–W16）

- **QoS2 四步握手**（§4.3.3）：状态机最复杂；最小 broker 可先只做 QoS0/1（订阅 QoS2 时 SUBACK 回 0x80），中期前补齐——它就是毕设「可靠性」章的核心素材（流程书 W10 整周）。
- Will Message（§3.1.2.5–7）：实现不难（存 topic+payload+QoS+retain，断连发布），在线监测演示有价值（流程书 W12）。
- User Name/Password 解析：字段位置是 MUST（否则解析错位），认证策略本身可后置为安全扩展。
- 重连后原 PID 重发（§4.4）+ 投递顺序（§4.6）：弱网/树莓派实验用（流程书 W13、W21）。

### 🟢 可以等（不实现）

- §5 安全实现（TLS 直接用 OpenSSL 库）、§7 的逐条 MUST 审计（按本篇引用抽查）。
- 256MB 大报文完整支持：边缘场景上限调到 256KB–1MB，超限按协议错误断连即可。
- WebSocket（§6）、Unordered Topic 管理机制（§4.6）：默认 Ordered 即合规。

## 与其他论文的关系

- [[R1MQTT5.0规范精读]]：本篇是「骨架版」，R1 的属性区/原因码/流控是「增强包」；实现顺序 = 本篇 🔴 → R1 🟡。
- [[4QoS级别与MQTT丢包时延相关性]]：本篇 §4.3 定义三级 QoS 语义，该论文实测其代价，实现章+实验章分别引用。
- [[5muMQ轻量可扩展MQTT代理]]：muMQ 兼容 3.1.1/5.0 双版本的客户端共存设计可对照本篇与 R1 的差异表。
- [[11MQTT可靠性实测压力测试]]：其「断线重连后消息不丢」的实测正是 §4.4 重发规则的行为验证。
- [[6分布式IoT边缘MQTT代理对比]]：各 broker 对本规范 MUST 项的支持差异（如 QoS2、持久会话）就是其对比矩阵的行来源。

## 对毕设的帮助

- **①写论文**：第 2 章「协议选择」引用 3.1.1 的 14 种报文结构与 QoS 语义（结构简图可直接改画）；「版本演进」一小节用第六节差异表论证「基于 3.1.1 语义 + 5.0 关键特性子集」的选型；[MQTT-x.y.z-n] 编号条目可直接作为设计依据的规范引用格式。
- **②动手实现**：编解码器按本篇先写（无属性区，字段位置唯一，不易错）；Session 结构体照 §3.1.2.4 清单建字段；CONNACK 固定 4 字节、PING 固定 2 字节这些「定长报文」是单元测试的黄金样例；Method A/B（p.55）二选一实现 QoS2 投递时机。
- **③测试**：互操作测试对端用 `mosquitto_sub/pub`（不带 -V 参数默认 3.1.1）；非法用例来自 MUST 违反项（QoS=3、flags 错、空 SUBSCRIBE payload、QoS0 带 PID、0 字节 ClientID + CleanSession=0）；「窗口=1 vs >1」顺序实验（§4.6）可模仿进性能测试章。

## 怎么用 & 怎么做（研0 版落地清单）

> 配套：[[R1MQTT5.0规范精读]] · 流程书：[[毕设完成流程书]] · 概念：[[概念索引]]

- **什么时候翻这篇**：流程书 W2 与 R1 一起通读（本篇读 §2–§4 建立最小框架）；W8–W12 实现期是**主要字典**；答辩被问「为什么不用 5.0 全量特性」时用第六节差异表回答。
- **在 Ubuntu 22.04 上**：`mosquitto_sub -t '#' -d`（默认 3.1.1）观察报文；Wireshark 过滤 `tcp.port==1883` 核对 CONNECT 定长 10 字节变长头；`mosquitto_sub -c -i clientA -q 1 -t 'x/#'` + kill 后重连，验证 §4.4 重发与 Session Present 位。
- **在树莓派上**：`mosquitto-clients` 做弱网对端；`tc netem` 丢包下验证 QoS1 重发（DUP=1、原 PID）；kill -9 broker 后重启，验证 CleanSession=0 的会话恢复（订阅还在、断连期间消息补发）。
- **C++ 实现要点**：先写 `encode_vbi/decode_vbi` + 剩余长度边界单测；定长报文（CONNACK/PING/UNSUBACK/DISCONNECT/PUBACK 系列）用一个 `make_fixed_packet(type, pid)` 工厂函数统一生成；Session 结构体按 §3.1.2.4 清单落字段（订阅表用哈希表，filter→maxQoS）；主题匹配先支持 `+`/`#` 通配树再考虑线性遍历（订阅数少时线性足够，参考 [[5muMQ轻量可扩展MQTT代理]] 的取舍）；Keep Alive 用 [[epoll（IO 多路复用）]] 的定时器事件实现 1.5× 判定。
