# MQTT v3.1.1 逐章可核验事实摘要

> 来源：`.zwork/提取/mqtt311.txt`（MQTT Version 3.1.1 OASIS Standard, 29 October 2014, 81 页 PDF 机器抽取文本）。
> 页码口径：全部为 **PDF 物理页码**，引用格式 `[PAGE p.N]`；正文标注的行号（如 1160）为提取文本中的规范条目编号，可交叉定位。
> 抽取文本中表格被拍平，个别列含义按上下文推断处已标 [?]。
> 说明：原定输出路径 `.zwork/提取/mqtt311-digest.md` 被平台限制不可写，本文件改放本科毕设根目录。

---

## 第 1 章 Introduction（p.9–15）

### 术语与角色（p.9–10）
- 规范定义 14 种 Control Packet，其中 PUBLISH 用于承载 Application Message（p.10，条目 51–53）。
- **Client**：总是主动建立到 Server 的 Network Connection（p.9，条目 23）。
- **Server**：接受连接、接受消息、处理订阅、向匹配订阅的 Client 转发消息（p.9–10，条目 30–35）。
- **Subscription** = Topic Filter + 最大 QoS，挂在单个 Session 下；同一 Session 内各 Subscription 的 Topic Filter 互不相同（p.10，条目 37–39）。
- **Session**：Client 与 Server 间的有状态交互，可短于或跨越多个 Network Connection（p.10，条目 47–49）。

### 1.5 数据表示（p.13–14）
- **Bits**：byte 内 bit 7 为最高位、bit 0 为最低位（p.13，条目 170–171）。
- **16 位整数**：大端序（big-endian），MSB 在前 LSB 在后（p.13，条目 173–175）。
- **UTF-8 encoded string**：前缀 2 字节长度字段（值为字符串本身的 UTF-8 字节数），字符串编码后长度上限 **65535 字节**（p.13，条目 181–186）。
- 收到 ill-formed UTF-8 或含 U+0000 的报文，接收方 **MUST 关闭 Network Connection**（p.14，条目 189–196，[MQTT-1.5.3-1]/[MQTT-1.5.3-2]）。
- U+D800–U+DFFF（代理区）禁止出现；控制字符 U+0001–001F、U+007F–009F 及 non-characters SHOULD NOT 使用，接收方可关闭连接（p.14，条目 191–204）。
- 序列 `0xEF 0xBB 0xBF` 恒解释为 U+FEFF，接收方 **MUST NOT 跳过或剥离**（p.14，条目 206–208，[MQTT-1.5.3-3]）。
- 示例：字符串 `A + U+2A6D4` 编码为 0x00 0x05 0x41 0xF0 0xAA 0x9B 0x94，共 7 字节（p.14–15，Figure 1.2）。

---

## 第 2 章 MQTT Control Packet format（p.16–22）

### 2.1 报文三段结构（p.16）
- Fixed header（所有报文都有）→ Variable header（部分报文）→ Payload（部分报文），顺序固定（p.16，条目 224–228）。

### 2.2.1 报文类型表（p.16–17，Table 2.1）
| 值 | 类型 | 方向 | 说明 |
|---|---|---|---|
| 0 | Reserved | Forbidden | 保留 |
| 1 | CONNECT | Client→Server | 连接请求 |
| 2 | CONNACK | Server→Client | 连接确认 |
| 3 | PUBLISH | 双向 | 发布消息 |
| 4 | PUBACK | 双向 | QoS1 确认 |
| 5 | PUBREC | 双向 | QoS2 第一步 |
| 6 | PUBREL | 双向 | QoS2 第二步 |
| 7 | PUBCOMP | 双向 | QoS2 第三步（完成） |
| 8 | SUBSCRIBE | Client→Server | 订阅请求 |
| 9 | SUBACK | Server→Client | 订阅确认 |
| 10 | UNSUBSCRIBE | Client→Server | 退订请求 |
| 11 | UNSUBACK | Server→Client | 退订确认 |
| 12 | PINGREQ | Client→Server | 心跳请求 |
| 13 | PINGRESP | Server→Client | 心跳响应 |
| 14 | DISCONNECT | Client→Server | 客户端断开 |
| 15 | Reserved | Forbidden | 保留 |

### 2.2.2 Flags（p.17–18，Table 2.2）
- byte 1 低 4 位为类型相关 flags；表中标 Reserved 的位必须为规定值，**收到非法 flags 接收方 MUST 关闭 Network Connection**（p.17，条目 241–245，[MQTT-2.2.2-1]/[MQTT-2.2.2-2]）。
- 各类型 required flags（低 4 位）：
  - 全 0：CONNECT、CONNACK、PUBACK、PUBREC、PUBCOMP、SUBACK、UNSUBACK、PINGREQ、PINGRESP、DISCONNECT；
  - **0010**（bit1=1）：PUBREL、SUBSCRIBE、UNSUBSCRIBE；
  - PUBLISH：DUP(bit3) / QoS(bit2,bit1) / RETAIN(bit0)（p.17–18，Table 2.2）。

### 2.2.3 Remaining Length（p.18–19）
- 含义：从该字段之后到报文结尾的字节数（含 Variable header 与 Payload），**不含自身编码字节**（p.18，条目 256–258）。
- 变长编码：每字节低 7 位承载数据，最高位为继续位（continuation bit）；**最多 4 字节**，单字节可表 0–127（p.18，条目 260–264）。
- 编码算法：`do { b = X % 128; X /= 128; if (X>0) b |= 128; output b; } while (X>0)`（p.19，条目 280–290）。
- 解码算法含乘数累乘 128，乘数 > 128³ 时抛 Malformed Remaining Length（p.19，条目 296–306）。
- 上限：4 字节最大可编码 **268,435,455（256 MB）**，线上形式 `0xFF 0xFF 0xFF 0x7F`（p.18–19，条目 273–274、Table 2.4）。
- 字节数区间表（Table 2.4，p.18–19）：1 字节 0–127；2 字节 128–16 383；3 字节 16 384–2 097 151；4 字节 2 097 152–268 435 455。

### 2.3.1 Packet Identifier（p.20–21）
- 2 字节，出现在：PUBLISH（仅 QoS>0）、PUBACK、PUBREC、PUBREL、PUBCOMP、SUBSCRIBE、SUBACK、UNSUBSCRIBE、UNSUBACK（p.20，条目 318–320）。
- SUBSCRIBE/UNSUBSCRIBE/QoS>0 的 PUBLISH **MUST 携带非零** Packet Identifier；重发时 MUST 用同一 ID；ID 在收到对应确认（QoS1→PUBACK，QoS2→PUBCOMP，SUBSCRIBE→SUBACK，UNSUBSCRIBE→UNSUBACK）后才可复用（p.20，条目 322–330，[MQTT-2.3.1-1..4]）。
- QoS 0 的 PUBLISH **MUST NOT 携带** Packet Identifier（p.20，条目 332，[MQTT-2.3.1-5]）。
- Client 与 Server 独立分配 ID，双方可并发使用相同 ID（p.21，条目 343–344）。

### 2.4 Payload 与 Variable header 出现位置（p.21–22，Table 2.6）
- 有 Payload 的报文：CONNECT（Required）、PUBLISH（Optional，可为空）、SUBSCRIBE（Required）、SUBACK（Required）、UNSUBSCRIBE（Required）。
- 无 Payload：CONNACK、PUBACK、PUBREC、PUBREL、PUBCOMP、UNSUBACK、PINGREQ、PINGRESP、DISCONNECT。
- 有 Variable header 的报文：CONNECT（10 字节）、CONNACK（2 字节）、PUBLISH（Topic Name [+Packet ID]）、PUBACK/PUBREC/PUBREL/PUBCOMP/SUBSCRIBE/SUBACK/UNSUBSCRIBE/UNSUBACK（各 2 字节 Packet ID）。
- 无 Variable header：PINGREQ、PINGRESP、DISCONNECT（见 §3 各报文定义）。

---

## 第 3 章 MQTT Control Packets（p.23–50）

### 3.1 CONNECT（p.23–31）
- Network Connection 建立后 **第一个报文必须是 CONNECT**；同一连接上 Client 只能发一次，第二次按协议违规断开（p.23，条目 364–369，[MQTT-3.1.0-1..2]）。
- Fixed header：type=1，flags 全 0（0x10）；Remaining Length = 10（Variable header 固定 10 字节）+ Payload 长度（p.23，条目 375–379）。
- Variable header 四字段顺序：Protocol Name、Protocol Level、Connect Flags、Keep Alive（p.23，条目 381–382）。
- **Protocol Name**：UTF-8 串 "MQTT"（长度 4，0x00 0x04 'M' 'Q' 'T' 'T'），大小写敏感，未来版本不变；名字不正确时 Server MAY 断开，或按其他规范处理（此时 MUST NOT 按本规范继续处理）（p.23–24，条目 386–391，[MQTT-3.1.2-1]）。
- **Protocol Level**：3.1.1 为 **4（0x04）**；不支持时 Server MUST 回 CONNACK 返回码 0x01 并断开（p.24，条目 398–401，[MQTT-3.1.2-2]）。
- **Connect Flags**（byte 8）：bit7 User Name Flag / bit6 Password Flag / bit5 Will Retain / bit4-3 Will QoS / bit2 Will Flag / bit1 Clean Session / bit0 Reserved 必须为 0，非零则断开（p.24，条目 405–407，[MQTT-3.1.2-3]）。
- **Clean Session**（bit1，p.24–25）：
  - =0：Server MUST 依据 ClientID 恢复已有 Session（无则新建），断开后双方 MUST 存储 Session；Server MUST 存储断连期间匹配其订阅的 QoS1/2 消息（QoS0 MAY 存）（条目 416–422，[MQTT-3.1.2-4..5]）。
  - =1：双方 MUST 丢弃旧 Session、新建仅随 Network Connection 存活的 Session，状态不得复用（条目 424–426，[MQTT-3.1.2-6]）。
  - Retained message **不属于** Session state，Session 结束时 MUST NOT 删除（p.25，条目 444–445）。
  - Session state 内容：Client 侧 = 已发未确认的 QoS1/2 消息 + 已收未确认的 QoS2 消息；Server 侧 = Session 存在性、订阅、已发未确认 QoS1/2、待发 QoS1/2、已收未确认 QoS2、可选的待发 QoS0（p.25，条目 428–442）。
- **Will Flag**（bit2，p.26）：=1 时 Server MUST 存储 Will Message 并在连接关闭时发布（除非收到 DISCONNECT 而删除）；触发场景包括 I/O/网络故障、Keep Alive 超时、未发 DISCONNECT 即断开、协议错误（条目 473–481，[MQTT-3.1.2-8]）；发布后或收到 DISCONNECT 后 MUST 删除（条目 485–486）。Server 关机/故障时 MAY 推迟发布（p.26 末，条目 492–494）。
- **Will QoS**（bit4-3，p.26）：Will Flag=0 时必须 0；=1 时可为 0/1/2，**不得为 3**（[MQTT-3.1.2-13..14]）。
- **Will Retain**（bit5，p.26–27）：Will Flag=0 时必须 0；=1 时决定 Will Message 是否作为 retained 发布（[MQTT-3.1.2-15..17]）。
- **User Name Flag**（bit7）/ **Password Flag**（bit6，p.27）：各自决定 payload 中有无对应字段；**User Name Flag=0 时 Password Flag 必须 0**（[MQTT-3.1.2-22]）。
- **Keep Alive**（2 字节秒数，p.27）：Client 两次发报文的最大间隔；无其他报文时 MUST 发 PINGREQ（[MQTT-3.1.2-23]）。Keep Alive 非零时，Server 若 **1.5×Keep Alive** 内未收到任何报文 MUST 断开（条目 537–539，[MQTT-3.1.2-24]）；Client 未按时收到 PINGRESP SHOULD 关闭连接。Keep Alive=0 关闭心跳机制，但 Server 仍可随时断开不活跃客户端（p.28，条目 544–547）。非规范性注释：典型值几分钟，最大 18 小时 12 分 15 秒（65535 s，p.28，条目 550–551）。
- **Payload**（p.29–30）：字段顺序固定：Client Identifier → Will Topic → Will Message → User Name → Password（[MQTT-3.1.3-1]）。
  - **ClientId**：必须存在且为第一字段；UTF-8 串；Server MUST 接受 1–23 字节且仅含 `[0-9a-zA-Z]` 的 ID；**可**放宽。允许 0 字节 ID 时 Server MUST 分配唯一 ID 并按该 ID 处理；0 字节 ID 的 Client MUST 同时置 CleanSession=1；0 字节 ID + CleanSession=0 → 回 CONNACK 0x02 并关闭连接；拒绝 ID 时同样回 0x02 后关闭（p.29，条目 559–587，[MQTT-3.1.3-2..9]）。
  - **Password**：2 字节长度前缀 + 0–65535 字节**二进制数据**（不是 UTF-8 串）（p.30，条目 609–611）。
- **Response（Server 处理流程）**（p.30–31）：合理时间内未收到 CONNECT SHOULD 关连接；CONNECT 不合规 MUST 关连接且**不发 CONNACK**（[MQTT-3.1.4-1]）；验证通过后：① 同 ClientID 已在线 → MUST 断开旧连接（[MQTT-3.1.4-2]）；② 按 CleanSession 规则处理；③ MUST 回返回码 0 的 CONNACK（[MQTT-3.1.4-4]）；④ 开始投递与 Keep Alive 监控。Client 在 CONNECT 后可立即发后续报文，无需等 CONNACK；Server 拒绝连接时 MUST NOT 处理 CONNECT 之后的任何数据（p.31，条目 643–646，[MQTT-3.1.4-5]）。

### 3.2 CONNACK（p.31–33）
- Server 发给 Client 的**第一个报文必须是 CONNACK**（p.31，条目 655–657，[MQTT-3.2.0-1]）。
- Fixed header：type=2，flags 0（0x20）；Remaining Length=2（p.31，条目 663–667）。
- Variable header byte1 = Connect Acknowledge Flags：bit0 为 **Session Present（SP）**，bit7-1 必须 0（p.31–32，条目 671–674）。
- **Session Present 语义**（p.32）：CleanSession=1 的连接 SP 必须 0；CleanSession=0 时，Server 已存有该 ClientID 的 Session state → SP=1，否则 0；非零返回码时 SP 必须 0（[MQTT-3.2.2-1..4]）。SP 让 Client 校验双方对持久状态认知是否一致。
- **Connect Return code 表**（p.32–33，Table 3.1）：

  | 值 | 含义 |
  |---|---|
  | 0x00 | Connection Accepted |
  | 0x01 | 拒绝：不支持的协议版本级别 |
  | 0x02 | 拒绝：identifier rejected（ClientID 合法 UTF-8 但 Server 不允许） |
  | 0x03 | 拒绝：Server unavailable（服务不可用） |
  | 0x04 | 拒绝：bad user name or password（格式错误） |
  | 0x05 | 拒绝：not authorized（未授权） |
  | 6–255 | 保留 |

- 发送非零返回码的 CONNACK 后 **MUST 关闭 Network Connection**（p.32，条目 705–707，[MQTT-3.2.2-5]）；无合适返回码时 MUST 不发 CONNACK 直接关连接（p.33，条目 710–711，[MQTT-3.2.2-6]）。CONNACK 无 Payload。

### 3.3 PUBLISH（p.33–37）
- Fixed header：type=3；flags = DUP(bit3)/QoS(bit2-1)/RETAIN(bit0)（p.33，条目 718–720）。
- **DUP**（bit3，p.33–34）：=1 表示可能是对先前发送尝试的重发；重发 PUBLISH 时 MUST 置 1（[MQTT-3.3.1-1]）；**QoS0 消息 DUP 必须 0**（[MQTT-3.3.1-2]）。DUP 指 Control Packet 本身而非 Application Message；Server 转发给订阅者时**不继承**入站 DUP，出站 DUP 只看出站方向是否为重发（p.33–34，条目 730–733，[MQTT-3.3.1-3]）。接收方不能凭 DUP=1 断定见过更早副本（p.34，条目 736–737）。
- **QoS**（bit2-1，p.34，Table 3.2）：0=至多一次、1=至少一次、2=恰好一次；**两 bits 同时为 1（值 3）禁止**，收到必须关连接（[MQTT-3.3.1-4]）。
- **RETAIN**（bit0，p.34–35）：Client→Server 置 1 时 Server MUST 存储消息及其 QoS 供未来订阅者；新订阅建立时每个匹配 topic 的最后一条 retained 消息 MUST 发给订阅者（[MQTT-3.3.1-5..6]）；QoS0 + RETAIN=1 会删除旧 retained、SHOULD 存新消息但可随时丢弃（[MQTT-3.3.1-7]）。Server→Client：因新订阅而发 retained 时 RETAIN 必须 1；因既有订阅匹配而发时 RETAIN 必须 0（p.34，条目 765–768，[MQTT-3.3.1-8..9]）。**RETAIN=1 且 0 字节 payload**：正常分发但 MUST 删除该 topic 已有 retained，且 0 字节 retained 不存储（即"删除 retained 消息"惯用法）（p.34–35，条目 770–775，[MQTT-3.3.1-10..11]）。RETAIN=0 时 MUST NOT 存储或改动已有 retained（[MQTT-3.3.1-12]）。
- Variable header：Topic Name（UTF-8，第一字段，**MUST NOT 含通配符**）+ Packet Identifier（仅 QoS1/2）（p.35，条目 787–800，[MQTT-3.3.2-1..2]）。
- Payload：Application Message，长度可由 Remaining Length 减 Variable header 得出；**允许 0 字节 payload**（p.36，条目 808–812）。
- Response（p.36，Table 3.4）：QoS0→无响应；QoS1→PUBACK；QoS2→PUBREC。
- Actions（p.36–37）：订阅重叠时 Server MUST 按所有匹配订阅的最大 QoS 投递（MAY 对每个订阅各发一份）（[MQTT-3.3.5-1]）；Server 不授权某 PUBLISH 时无法通知 Client，MUST 要么正常确认要么关连接（p.37，条目 834–836，[MQTT-3.3.5-2]）。

### 3.4–3.7 PUBACK / PUBREC / PUBREL / PUBCOMP（p.37–40）
- PUBACK（type=4，0x40）：对 QoS1 PUBLISH 的响应；Remaining Length=2；Variable header=Packet Identifier；无 Payload（p.37–38）。
- PUBREC（type=5，0x50）：对 QoS2 PUBLISH 的响应，QoS2 交互第二包（p.37–38）。
- PUBREL（type=6，flags **固定 0010**，0x62）：对 PUBREC 的响应，QoS2 第三包；flags 非法 MUST 视为 malformed 并关连接（p.38–39，条目 874–876，[MQTT-3.6.1-1]）。
- PUBCOMP（type=7，0x70）：对 PUBREL 的响应，QoS2 第四包（最后一包）（p.39–40）。
- 四者的 Variable header 都只含 2 字节 Packet Identifier，且 MUST 与被确认报文一致（见 2.3.1）。

### 3.8 SUBSCRIBE（p.40–43）
- Fixed header：type=8，flags **固定 0010**（0x82）；非法值 MUST 视为 malformed 关连接（p.40，条目 914–918，[MQTT-3.8.1-1]）。
- Variable header：仅 Packet Identifier（p.40，条目 922–924）。
- Payload：若干「Topic Filter（UTF-8）+ Requested QoS（1 字节，高 6 位保留必须 0）」连续排列；**至少一对，空 payload 是协议违规**（p.41，条目 930–943，[MQTT-3.8.3-1..3]）；保留位非零或 QoS 不为 0/1/2 → malformed 关连接（p.41–42，条目 947–950，[MQTT-3.8.3-4]）。
- Server SHOULD 支持通配符 filter；不支持则 MUST 拒绝含通配符的订阅（p.41，条目 932–934，[MQTT-3.8.3-2]）。
- Response（p.42–43）：MUST 回 SUBACK 且带相同 Packet ID（[MQTT-3.8.4-1..2]）；Server 允许在发 SUBACK 前先发匹配的 PUBLISH（p.43，条目 963–964）。filter 与既有订阅相同 → 整体替换，matching retained 重发（[MQTT-3.8.4-3]）。多 filter 按多个 SUBSCRIBE 依次处理、合并为一个 SUBACK（[MQTT-3.8.4-4]）。**实际投递 QoS = min(发布 QoS, 授予的最大 QoS)**（p.43，条目 982–986，[MQTT-3.8.4-6]）。

### 3.9 SUBACK（p.43–45）
- type=9（0x90），Remaining Length = 2 + payload 长度；Variable header=Packet Identifier（p.44）。
- Payload 为返回码列表，顺序 MUST 与 SUBSCRIBE 的 filter 顺序一致（p.44，[MQTT-3.9.3-1]）；**允许值仅 4 个**：0x00（成功，最大 QoS0）、0x01（成功，QoS1）、0x02（成功，QoS2）、**0x80（Failure）**；其他值保留禁用（p.44，条目 1029–1036，[MQTT-3.9.3-2]）。

### 3.10 UNSUBSCRIBE（p.45–47）
- type=10，flags 固定 0010（0xA2），非法则关连接（p.45，[MQTT-3.10.1-1]）。
- Payload：至少一个 Topic Filter（UTF-8），空 payload 违规（p.46，[MQTT-3.10.3-1..2]）。
- Response（p.46–47）：filter 与 Server 所存**逐字符精确比较**，完全相同才删除订阅（p.46–47，[MQTT-3.10.4-1]）；删除时停止新增投递、完成已开始的 QoS1/2 投递（[MQTT-3.10.4-2..3]）；MUST 回 UNSUBACK（即使没有删除任何订阅）（[MQTT-3.10.4-4..5]）。

### 3.11 UNSUBACK（p.47–48）：type=11（0xB0），Remaining Length=2，Variable header=Packet ID，无 Payload。

### 3.12 PINGREQ（p.48）：type=12（0xC0），Remaining Length=0，无 Variable header / Payload。Server MUST 回 PINGRESP（[MQTT-3.12.4-1]）。

### 3.13 PINGRESP（p.48–49）：type=13（0xD0），Remaining Length=0，无 Variable header / Payload。

### 3.14 DISCONNECT（p.49–50）
- type=14（0xE0），Remaining Length=0；保留位非零 MUST 断开（[MQTT-3.14.1-1]）。**仅 Client→Server**。
- Client 发送后 MUST 关闭连接且不再发任何报文（[MQTT-3.14.4-1..2]）；Server 收到后 MUST 丢弃 Will Message 不发布（[MQTT-3.14.4-3]），并 SHOULD 关闭连接（p.49–50）。无错误码、无 reason code（与 5.0 差异）。

---

## 第 4 章 Operational behavior（p.51–59）

### 4.1 状态存储（p.51）
- QoS 保证要求 Client 与 Server **都**存储 Session state，且 MUST 在整个 Session 存续期存储；Session MUST 至少与其活跃 Network Connection 等长（条目 1160–1162，[MQTT-4.1.0-1..2]）。
- 归属方：Session state 由 **Client 与 Server 各自持有**（内容见 §3.1.2.4 清单，p.25）；**Retained messages 不属于 Server 的 Session state**，SHOULD 保留至被 Client 删除（p.51，条目 1164–1165）。
- 非规范性：存储能力有限，管理员操作/软硬件故障可导致 Session state 丢失或被丢弃（等效终止 Session）（p.51，条目 1167–1190）。

### 4.2 网络连接（p.52）
- 底层传输必须提供**有序、无损、双向字节流**；TCP/IP、TLS、WebSocket 均可，UDP 这类无连接传输单独使用不合适（p.52，条目 1201–1214）。IANA 注册端口：1883（明文）/8883（TLS）（p.52，条目 1210–1211）。

### 4.3 QoS 协议流（p.52–55）
- 投递协议对称：Client/Server 都可当 Sender 或 Receiver；Server 向多个 Client 投递时各 Client 独立处理；出站 QoS 可与入站不同（p.52，条目 1216–1223）。
- **QoS 0**（p.52）：Sender MUST 以 QoS=0、DUP=0 发 PUBLISH，无响应、无重试、无 Packet ID（[MQTT-4.3.1-1]）。
- **QoS 1**（p.53）：Sender 为新消息分配未用 Packet ID，发 QoS=1、DUP=0 的 PUBLISH，收到对应 PUBACK 前视为 unacknowledged（[MQTT-4.3.2-1]）；Receiver 接受所有权后 MUST 回带同一 Packet ID 的 PUBACK；**发出 PUBACK 后，再收到同 Packet ID 的 PUBLISH 一律视为新发布（不管 DUP 设置）**（p.53，条目 1253–1258，[MQTT-4.3.2-2]）。等待确认期间可发其他 Packet ID 的 PUBLISH。
- **QoS 2 四步握手**（p.54–55）：
  1. Sender 发 PUBLISH（QoS=2，DUP=0，含 Packet ID），收到 PUBREC 前视为 unacknowledged；
  2. Receiver 回 PUBREC（接受所有权）；**收到 PUBREL 之前，对同 Packet ID 的后续 PUBLISH 一律再回 PUBREC，且 MUST NOT 向下游重复投递**（去重前提）；
  3. Sender 收到 PUBREC 后 MUST 发 PUBREL（同 Packet ID）；**发出 PUBREL 后 MUST NOT 再重发该 PUBLISH**；PUBREL 未收到 PUBCOMP 前视为 unacknowledged；
  4. Receiver 收到 PUBREL 后 MUST 回 PUBCOMP；发出 PUBCOMP 后同 Packet ID 的 PUBLISH 视为新发布。

  （[MQTT-4.3.3-1..2]）Packet ID 在收到 PUBCOMP 后才可复用。Receiver 有 Method A/B 两种实现（在 PUBREC 或 PUBCOMP 时点启动下游投递），选其一即可，不影响保证（p.55，条目 1309–1312）。

### 4.4 重发（p.55）
- **唯一强制重发场景**：Client 以 CleanSession=0 重连时，双方 MUST 用**原 Packet Identifier** 重发所有未确认的 PUBLISH（QoS>0）与 PUBREL（p.55，条目 1314–1318，[MQTT-4.4.0-1]）。
- 即：3.1.1 中不存在「连接存活期间按定时器重发」的强制要求（历史重发是为克服老 TCP 网络丢包，非规范性注释，p.55，条目 1320–1323）。且重发仅涉及 QoS1/2（QoS0 无确认概念）。

### 4.5 消息接收（p.56）
- Server 接管消息后 MUST 把它加入所有匹配订阅的 Session state（[MQTT-4.5.0-1]）；Client 无论是否处理消息内容，都 MUST 按对应 QoS 规则确认收到的 PUBLISH（[MQTT-4.5.0-2]）。

### 4.6 消息顺序（p.56）
- Client 规则：重发 PUBLISH MUST 按原发送顺序（QoS1/2）；PUBACK MUST 按对应 PUBLISH 的接收顺序发；PUBREC 按 PUBLISH 接收顺序；PUBREL 按 PUBREC 接收顺序（p.56，条目 1335–1343，[MQTT-4.6.0-1..4]）。
- Server 默认把每个 Topic 当 **Ordered Topic**（可管理机制改为 Unordered）；对 Ordered Topic MUST 按收到顺序向每个订阅者投递（同 Topic 同 QoS）（p.56，条目 1345–1351，[MQTT-4.6.0-5..6]）。
- 非规范性：QoS1 下订阅者最终副本有序但可能收到重复（如 1,2,3,2,3,4）；把 in-flight 窗口设为 1 可完全保序（p.56，条目 1353–1366）。

### 4.7 Topic 语法（p.57–59）
- 分层符 `/`（U+002F）：相邻分隔符表示零长度层（p.57，条目 1375–1380）。
- **通配符只能用于 Topic Filter，MUST NOT 出现在 Topic Name（PUBLISH 用）中**（p.57，[MQTT-4.7.1-1]）。
- **`#`（multi-level，U+0023）**：匹配父层及任意多层子层；**必须独立成层或紧跟 `/`，且必须是 filter 最后一个字符**（p.57，[MQTT-4.7.1-2]）。例：`sport/tennis/player1/#` 匹配 `sport/tennis/player1`、`.../ranking` 等；`sport/#` 也匹配 `sport`；`#` 匹配一切；`sport/tennis#`、`sport/tennis/#/ranking` 非法（p.57，条目 1387–1399）。
- **`+`（single-level，U+002B）**：只匹配一层，**必须独占一层**，可在任意层且可与 `#` 连用（p.57–58，[MQTT-4.7.1-3]）。例：`sport/+` 不匹配 `sport` 但匹配 `sport/`；`/finance` 匹配 `+/+` 与 `/+` 但不匹配 `+`（p.57–58，条目 1407–1417）。
- **$ 开头 topic**：Server MUST NOT 把以通配符开头的 filter（`#`、`+`）匹配到 `$` 开头的 Topic Name；Server SHOULD 阻止 Client 用 `$` 开头 topic 互发消息；`$SYS/` 被广泛用作 Server 状态/控制 API 前缀；要同时收 `$SYS/#` 与普通消息须订阅 `#` 和 `$SYS/#` 两者（p.58，条目 1418–1439，[MQTT-4.7.2-1]）。
- 语义（p.58–59）：至少 1 字符；大小写敏感；可含空格；前导/尾部 `/` 产生不同 topic；仅 `/` 合法；禁 U+0000；UTF-8 编码后 ≤65535 字节；层数不限（p.58，条目 1442–1450，[MQTT-4.7.3-1..3]）；匹配时 **MUST NOT 做任何归一化或字符替换**，逐字符比较（p.59，条目 1453–1456，[MQTT-4.7.3-4]）。

### 4.8 错误处理（p.59）
- 除非另有规定，遇到协议违规 **MUST 关闭收到该报文的 Network Connection**（[MQTT-4.8.0-1]）。
- Transient Error（如缓冲满）：处理入站报文时遇到 → MUST 关闭该连接；Server 遇到 Transient Error 时 SHOULD NOT 影响与其他 Client 的交互（p.59，条目 1478–1483，[MQTT-4.8.0-2]）。

---

## 第 5 章 Security（p.60–64，全章非规范性）
- 明示 **Non Normative**（p.60，条目 1486）；建议 TLS 用 8883 端口（p.60，条目 1487–1488）。
- MQTT 作为传输协议只关心消息传递，安全由实现者负责，通常用 TLS（p.60，条目 1505–1507）。
- 5.4.3（p.61–62）：**协议不信任对称——没有 Client 认证 Server 的机制**，需靠 TLS 证书/VPN 补足。
- 5.4.1：CONNECT 的 Username/Password 字段如何用由实现决定（可接 LDAP/OAuth 等）；明文传凭证有 MitM/重放风险（p.61）。
- 5.4.11：三层安全 profile 示例——明文 / 安全网络（VPN）/ 安全传输（TLS）（p.64）；另有行业合规（NIST CSF、PCI-DSS、FIPS 140-2、NSA Suite B）（p.60–61、p.64）。
- 5.4.8：建议 Server 监测异常行为（反复连接、topic 扫描、连接不发数据等）并可断开/拉黑（p.63）。

## 第 6 章 WebSocket 传输（p.65，规范性）
- MQTT 报文 MUST 用 WebSocket binary frame 发送；单帧可含多个或部分报文（不对齐帧边界）；子协议必须提供并选择 "mqtt"；IANA 注册子协议名 `mqtt`（p.65，[MQTT-6.0.0-1..4]）。

## 第 7 章 Conformance（p.66–67）
- 一致性分 MQTT Server 与 MQTT Client 两类目标；可同时作为两者（如既收连接又外连其他 Server 的 Server 必须双一致）（p.66，[MQTT-7.0.0-1]）。
- **合规实现 MUST NOT 要求使用本规范之外的扩展**才能与其他合规实现互操作（p.66，[MQTT-7.0.0-2]）。
- Server/Client 须满足各自适用章节的全部 MUST 项；必须支持至少一种提供有序无损字节流的传输，但不绑定具体协议（p.66–67，[MQTT-7.1.1-1]/[MQTT-7.1.2-1]）。

## 附录（p.68–81，均 non normative）
- Appendix A Acknowledgements（p.68–69）：致谢，确认 MQTT 原始发明人为 Andy Stanford-Clark 与 Arlen Nipper。
- Appendix B Mandatory normative statements（p.70–79）：全规范 MUST/MAY 语句清单（内容未逐条核对 [?]）。
- Appendix C Revision history（p.80–81）：修订历史（未逐条核对 [?]）。

---

## 3.1.1 没有（与 5.0 的差异点）
依据：通读 §1–§7 及 §3 全部报文格式，3.1.1 中不存在以下机制（以下均为「规范文本中无对应字段/报文/章节」的否定性事实）：
1. **无 Properties / 属性区**：所有 Variable header 都是定长字段，没有任何属性包机制（对照 §2.3、§3.x，p.16–50）。
2. **无数值化 reason code**：PUBACK/PUBREC/PUBREL/PUBCOMP/DISCONNECT 只有 Packet ID 或空，没有 reason code 字节；错误路径就是「关连接」（§3.4–3.7、3.14，p.37–50；DISCONNECT 无错误码）。仅 CONNACK（0x00–0x05，p.32–33）与 SUBACK（0x00–0x02、0x80，p.44）有返回码。
3. **无 shared subscription**（共享订阅）：§3.8/§4.7 的 filter 只做逐字符匹配，无 `$share` 前缀语义。
4. **无 message expiry**：PUBLISH 无过期时间字段（§3.3，p.33–37）。
5. **无 topic alias**：PUBLISH Variable header 只有 Topic Name + Packet ID，无别名机制（p.35）。
6. **Session expiry 不可协商**：会话寿命只有 CleanSession 一个二选一位（=0 持久保持、=1 随连接结束），无 Session Expiry Interval 属性可调（§3.1.2.4，p.24–25；§4.1，p.51）。
7. 其他没有的：response topic / correlation data、payload format indicator / content type、subscription identifier、receive maximum / maximum packet size 等流控协商、AUTH 报文与增强认证（§2.2.1 Table 2.1 仅 14 种报文，p.16–17）、请求/响应模型。
8. Keep Alive 超时判定固定为 1.5×（[MQTT-3.1.2-24]，p.27），Server 不能放宽（5.0 可通过属性协商）。

---

## 三档分类（面向本科毕设：Ubuntu 22.04 上实现轻量 broker）

### 🔴 最小可用 broker 必须实现
- Remaining Length 变长编解码（含 4 字节上限检查）与 Fixed header 类型/flags 校验（§2.2，p.16–19）。
- CONNECT/CONNACK：Protocol Name "MQTT"、Level 4 校验、Connect Flags 解析、ClientId 校验（1–23 字节 / 0 字节 + CleanSession=1 规则）、返回码 0x00–0x05、Session Present、同 ClientID 挤掉旧连接（§3.1–3.2，p.23–33）。
- UTF-8 合法性校验（收到非法即关连接，§1.5.3，p.13–14）。
- PUBLISH QoS0/1 + PUBACK；Packet ID 规则（非零、复用时机）（§2.3.1、§3.3–3.4，p.20、33–38）。
- SUBSCRIBE/SUBACK（QoS 字节校验、0x80 失败、QoS 降级取 min）、UNSUBSCRIBE/UNSUBACK、PINGREQ/PINGRESP、DISCONNECT（含 Will 丢弃）（§3.8–3.14，p.40–50）。
- Topic 匹配引擎：`/` 分层、`+`/`#` 通配符规则、`$` 开头约束、逐字符匹配（§4.7，p.57–59）。
- Retained message 存取与 0 字节删除惯用法（§3.3.1.3，p.34–35）。
- CleanSession=0 的会话持久化与 Session state 清单（§3.1.2.4、§4.1，p.24–25、51）。
- Keep Alive 计时（1.5× 判定）与协议错误一律关连接（§3.1.2.10、§4.8，p.27、59）。
- 理由：这些是 MQTT Server 一致性（[MQTT-7.1.1-1] 等）的 MUST 主体，缺任何一个都无法与标准客户端（mosquitto_pub/sub、paho）互通。

### 🟡 建议实现但可后置
- **QoS 2 完整四步握手**（PUBREC/PUBREL/PUBCOMP + 去重）（§4.3.3，p.54–55）：状态机复杂度最高；最小 broker 可先只做 QoS0/1，订阅端请求 QoS2 时在 SUBACK 回 0x80。毕设中期补上，可作为「可靠性」章节的核心实验素材。
- **Will Message（遗嘱）**（§3.1.2.5–3.1.2.7，p.26–27）：实现不难（存 topic+payload+QoS+retain，断连时发布），边缘设备在线监测演示有价值，但最小互通不需要。
- **User Name/Password 字段解析与认证**（§3.1.2.8–3.1.2.9、§3.1.3.4–3.1.3.5，p.27、30）：字段位置解析是 MUST（否则长度错位），认证策略本身可选；可后置为安全扩展。
- **重发机制**（CleanSession=0 重连后按原 ID 重发，§4.4，p.55）与**投递顺序规则**（§4.6，p.56）：做持久会话 + 弱网测试（树莓派断网重连）时需要。
- WebSocket 传输（§6，p.65）：若不做浏览器端接入可整体后置。
- 理由：不影响基本互通，但分别是毕设「可靠性容错」「安全」「多接入方式」扩展点的载体，建议按任务书节奏排入中期。

### 🟢 本科毕设可跳过
- 第 5 章全部安全性指导（p.60–64）：非规范性文字，TLS 接入直接用现成库（OpenSSL 等），无需自研。
- 第 7 章 Conformance 的形式化核对与 Appendix B 的 MUST 语句清单逐条审计（p.66–67、70–79）：按本 digest 的 MUST 引用抽查即可。
- 268 MB 最大报文的完整支持（§2.2.3，p.18–19）：边缘场景把上限调到 256 KB–1 MB 完全合理，超限时按协议错误关连接即可。
- SOCKS、NIST/PCI-DSS/FIPS 合规、安全 profile 分层（§5.4.10–5.4.11，p.64）：企业合规内容，与轻量 broker 主线无关。
- Unordered Topic 管理机制（§4.6，p.56）：规范允许的优化项，保持默认 Ordered 即可。
- 理由：要么非规范性、要么是大规模部署才需要的治理能力；写论文时引用其结论即可，实现不加分。

---

## 待证项
- Appendix B/C 内容未逐条读取（p.70–79、80–81），如需引用具体 MUST 条目编号清单需再读原文。
- §3.3.5 中「Server MAY deliver further copies（每个匹配订阅一份）」允许两种投递实现（一份按最大 QoS 或每个订阅各一份），见 p.36 条目 825–829。
