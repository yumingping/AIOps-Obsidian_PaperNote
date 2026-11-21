# MQTT Version 5.0 OASIS Standard 逐章可核验事实摘要

> 源文件：`.zwork/提取/mqtt-v5.0.txt`（OASIS mqtt-v5.0-os, 2019-03-07, 137 页）
> 页码口径：全部为 PDF 物理页码（`[PAGE p.N]` 标记，第 1 页 = p.1）。文中每节标注的页码均为实际读到的标记范围。
> 提取文本由机器抽取，表格被拍平；列含义结合上下文标签还原，个别还原不确定处标 [?]。
> 本文件是笔记性加工产物，PDF 原件只读。摘要生成日期：2026-11-20。

---

## 第 1 章 Introduction（p.11–p.20）

- 1.0–1.4：知识产权政策、规范组织结构（p.11）；术语表（Terminology，p.11–13）；规范性引用（p.13）与非规范性引用（p.13–16）。
- 1.5 Data representation（p.16–19）——本节是编解码实现的直接依据：
  - **1.5.1 Bits**（p.16）：byte 内位编号 7（最高位 MSB）到 0（最低位 LSB）。
  - **1.5.2 Two Byte Integer**（p.16）：16 位无符号整数，大端序（MSB 先发，LSB 后发）。
  - **1.5.3 Four Byte Integer**（p.16）：32 位无符号整数，大端序（MSB→…→LSB）。
  - **1.5.4 UTF-8 Encoded String**（p.16–18）：前缀 Two Byte Integer 长度（字节数），因此**最大 65,535 字节**；长度可为 0。正文必须为 well-formed UTF-8；**禁止 U+D800–U+DFFF 代理区**（[MQTT-1.5.4-1]）、**禁止 U+0000**（[MQTT-1.5.4-2]），违反即 Malformed Packet。序列 0xEF 0xBB 0xBF 一律解释为 U+FEFF，接收方不得剥离（[MQTT-1.5.4-3]）。U+0001..U+001F、U+007F..U+009F、Unicode non-characters 为 Disallowed 码点，接收方 MAY 视为 Malformed Packet（p.17）。示例（Figure 1-2，p.17–18）："A"+U+2A6D4 编码为 `00 05 41 F0 AA 9B 94`（长度 5 + 'A' + 4 字节四字节 UTF-8）。
  - **1.5.5 Variable Byte Integer（VBI）**（p.18–19）：≤127 用 1 字节；每字节低 7 位承载数据、最高位是续位（continuation bit）；**最多 4 字节**；**必须使用最少字节数编码**（[MQTT-1.5.5-1]）。Table 1-1（p.18）：
    | 字节数 | From | To |
    |---|---|---|
    | 1 | 0 (0x00) | 127 (0x7F) |
    | 2 | 128 (0x80,0x01) | 16,383 (0xFF,0x7F) |
    | 3 | 16,384 (0x80,0x80,0x01) | 2,097,151 (0xFF,0xFF,0x7F) |
    | 4 | 2,097,152 (0x80,0x80,0x80,0x01) | **268,435,455 (0xFF,0xFF,0xFF,0x7F)** |
    编码伪码：`do { encodedByte = X MOD 128; X = X DIV 128; if (X>0) encodedByte |= 128; output } while (X>0)`（p.18–19）。解码伪码：`multiplier=1; do { value += (byte AND 127)*multiplier; if (multiplier > 128*128*128) throw Malformed; multiplier *= 128 } while ((byte AND 128)!=0)`（p.19）。
  - **1.5.6 Binary Data**（p.19）：Two Byte Integer 长度 + 数据字节，0–65,535 字节。
  - **1.5.7 UTF-8 String Pair**（p.19）：两个 UTF-8 Encoded String 组成的 name-value 对，两条都必须满足 UTF-8 字符串规则（[MQTT-1.5.7-1]）。
- 1.6 Security（p.19–20）：Client/Server SHOULD 提供认证、授权与安全通信选项。1.7 编辑约定（p.20）：一致性声明编号格式 [MQTT-x.x.x-y]。1.8 变更史（p.20）：v3.1.1 是首个 OASIS 标准、亦为 ISO/IEC 20922:2016；v5.0 五大目标：可扩展性、错误报告改进、形式化常见模式（能力发现、请求/响应）、扩展机制（User Properties）、性能与小客户端支持。

## 第 2 章 MQTT Control Packet format（p.21–p.29）

### 2.1 报文三段结构（p.21）
Fixed Header（所有报文必有）→ Variable Header（部分报文）→ Payload（部分报文），顺序固定。

### 2.1.1 Fixed Header（p.21）
byte 1 高 4 位 = 报文类型，低 4 位 = 类型相关 Flags；byte 2 起 = Remaining Length。

### Table 2-1 类型值表（p.21–22）
| 值 | 报文 | 方向 | 说明 |
|---|---|---|---|
| 0 | Reserved | Forbidden | 保留 |
| 1 | CONNECT | C→S | 连接请求 |
| 2 | CONNACK | S→C | 连接确认 |
| 3 | PUBLISH | 双向 | 发布消息 |
| 4 | PUBACK | 双向 | QoS1 确认 |
| 5 | PUBREC | 双向 | QoS2 第 1 步确认 |
| 6 | PUBREL | 双向 | QoS2 第 2 步 |
| 7 | PUBCOMP | 双向 | QoS2 第 3 步（最终）确认 |
| 8 | SUBSCRIBE | C→S | 订阅请求 |
| 9 | SUBACK | S→C | 订阅确认 |
| 10 | UNSUBSCRIBE | C→S | 退订请求 |
| 11 | UNSUBACK | S→C | 退订确认 |
| 12 | PINGREQ | C→S | 心跳请求 |
| 13 | PINGRESP | S→C | 心跳响应 |
| 14 | DISCONNECT | 双向 | 断开通知（v5 新增 Server 可发） |
| 15 | AUTH | 双向 | 认证交换（v5 新增） |

### 2.1.3 Flags 规则（Table 2-2，p.22–23）
- 只有 **PUBLISH** 使用 flags：bit3=DUP，bit2-1=QoS，bit0=RETAIN（p.22–23）。
- **PUBREL、SUBSCRIBE、UNSUBSCRIBE** 的 bit3..0 固定为 `0,0,1,0`（即首字节分别为 0x62 / 0x82 / 0xA2），其他位为 0；其余所有报文 4 个 flag 位全部为 0。Reserved 位必须按表取值（[MQTT-2.1.3-1]），非法 flags = Malformed Packet。

### 2.1.4 Remaining Length（p.23）
VBI，表示 Variable Header + Payload 的字节数；**不含自身编码字节**。Packet size = Fixed Header 长度 + Remaining Length。

### 2.2.1 Packet Identifier（p.23–25）
- Two Byte Integer，出现于 PUBLISH（QoS>0）、PUBACK、PUBREC、PUBREL、PUBCOMP、SUBSCRIBE、SUBACK、UNSUBSCRIBE、UNSUBACK（Table 2-3，p.23–24）。
- QoS 0 的 PUBLISH **不得**带 Packet Identifier（[MQTT-2.2.1-2]）。新报文必须分配**当前未用的非零** PID（[MQTT-2.2.1-3/-4]）。
- 复用时机：QoS1 = 收到对应 PUBACK；QoS2 = 收到 PUBCOMP 或 RC≥0x80 的 PUBREC；SUBSCRIBE/UNSUBSCRIBE = 收到对应 SUBACK/UNSUBACK（p.24）。
- Client 与 Server 各自独立分配，双向可用同一 PID 并发（p.24–25 示例）。

### 2.2.2 Properties（p.25–26）
- 结构：Property Length（VBI，不含自身；无属性必须写 0，[MQTT-2.2.2-1]）+ 若干 Property；Property = Identifier（VBI）+ 值。非法 ID/类型 = Malformed Packet → CONNACK/DISCONNECT 0x81。
- **Table 2-4 属性总表（p.25–26，全部 30 项）**：
  | ID(dec/hex) | 名称 | 类型 | 用于 |
  |---|---|---|---|
  | 1/0x01 | Payload Format Indicator | Byte | PUBLISH, Will Properties |
  | 2/0x02 | Message Expiry Interval | Four Byte Integer | PUBLISH, Will Properties |
  | 3/0x03 | Content Type | UTF-8 String | PUBLISH, Will Properties |
  | 8/0x08 | Response Topic | UTF-8 String | PUBLISH, Will Properties |
  | 9/0x09 | Correlation Data | Binary Data | PUBLISH, Will Properties |
  | 11/0x0B | Subscription Identifier | VBI | PUBLISH, SUBSCRIBE |
  | 17/0x11 | Session Expiry Interval | Four Byte Integer | CONNECT, CONNACK, DISCONNECT |
  | 18/0x12 | Assigned Client Identifier | UTF-8 String | CONNACK |
  | 19/0x13 | Server Keep Alive | Two Byte Integer | CONNACK |
  | 21/0x15 | Authentication Method | UTF-8 String | CONNECT, CONNACK, AUTH |
  | 22/0x16 | Authentication Data | Binary Data | CONNECT, CONNACK, AUTH |
  | 23/0x17 | Request Problem Information | Byte | CONNECT |
  | 24/0x18 | Will Delay Interval | Four Byte Integer | Will Properties |
  | 25/0x19 | Request Response Information | Byte | CONNECT |
  | 26/0x1A | Response Information | UTF-8 String | CONNACK |
  | 28/0x1C | Server Reference | UTF-8 String | CONNACK, DISCONNECT |
  | 31/0x1F | Reason String | UTF-8 String | CONNACK, PUBACK, PUBREC, PUBREL, PUBCOMP, SUBACK, UNSUBACK, DISCONNECT, AUTH |
  | 33/0x21 | Receive Maximum | Two Byte Integer | CONNECT, CONNACK |
  | 34/0x22 | Topic Alias Maximum | Two Byte Integer | CONNECT, CONNACK |
  | 35/0x23 | Topic Alias | Two Byte Integer | PUBLISH |
  | 36/0x24 | Maximum QoS | Byte | CONNACK |
  | 37/0x25 | Retain Available | Byte | CONNACK |
  | 38/0x26 | User Property | UTF-8 String Pair | 几乎全部报文 + Will Properties（可重复出现） |
  | 39/0x27 | Maximum Packet Size | Four Byte Integer | CONNECT, CONNACK |
  | 40/0x28 | Wildcard Subscription Available | Byte | CONNACK |
  | 41/0x29 | Subscription Identifier Available | Byte | CONNACK |
  | 42/0x2A | Shared Subscription Available | Byte | CONNACK |
- 非规范性说明（p.26）：虽然 ID 定义为 VBI，本版本所有 ID 实际都是 1 字节。

### 2.3 Payload（Table 2-5，p.26–27）
CONNECT 必有；PUBLISH 可选（应用消息）；SUBSCRIBE / SUBACK / UNSUBSCRIBE / UNSUBACK 必有；其余（CONNACK、PUBACK、PUBREC、PUBREL、PUBCOMP、PINGREQ、PINGRESP、DISCONNECT、AUTH）无 Payload。

### 2.4 Reason Code（Table 2-6，p.27–29）
1 字节无符号；**<0x80 = 成功（常规成功值为 0），≥0x80 = 失败**。CONNACK/PUBACK/PUBREC/PUBREL/PUBCOMP/DISCONNECT/AUTH 各带单个 RC；SUBACK/UNSUBACK 在 Payload 带一串 RC。主要值：
| dec | hex | 名称 | 用于 |
|---|---|---|---|
| 0 | 0x00 | Success / Normal disconnection / Granted QoS 0 | 各 ACK、DISCONNECT、SUBACK |
| 1/2 | 0x01/02 | Granted QoS 1/2 | SUBACK |
| 4 | 0x04 | Disconnect with Will Message | DISCONNECT（仅 Client） |
| 16 | 0x10 | No matching subscribers | PUBACK, PUBREC |
| 17 | 0x11 | No subscription existed | UNSUBACK |
| 24 | 0x18 | Continue authentication | AUTH |
| 25 | 0x19 | Re-authenticate | AUTH |
| 128 | 0x80 | Unspecified error | CONNACK, PUBACK, PUBREC, SUBACK, UNSUBACK, DISCONNECT |
| 129 | 0x81 | Malformed Packet | CONNACK, DISCONNECT |
| 130 | 0x82 | Protocol Error | CONNACK, DISCONNECT |
| 131 | 0x83 | Implementation specific error | CONNACK, PUBACK, PUBREC, SUBACK, UNSUBACK, DISCONNECT |
| 132 | 0x84 | Unsupported Protocol Version | CONNACK |
| 133 | 0x85 | Client Identifier not valid | CONNACK |
| 134 | 0x86 | Bad User Name or Password | CONNACK |
| 135 | 0x87 | Not authorized | CONNACK, PUBACK, PUBREC, SUBACK, UNSUBACK, DISCONNECT |
| 136 | 0x88 | Server unavailable | CONNACK |
| 137 | 0x89 | Server busy | CONNACK, DISCONNECT |
| 138 | 0x8A | Banned | CONNACK |
| 139 | 0x8B | Server shutting down | DISCONNECT |
| 140 | 0x8C | Bad authentication method | CONNACK, DISCONNECT |
| 141 | 0x8D | Keep Alive timeout | DISCONNECT |
| 142 | 0x8E | Session taken over | DISCONNECT |
| 143 | 0x8F | Topic Filter invalid | SUBACK, UNSUBACK, DISCONNECT |
| 144 | 0x90 | Topic Name invalid | CONNACK, PUBACK, PUBREC, DISCONNECT |
| 145 | 0x91 | Packet Identifier in use | PUBACK, PUBREC, SUBACK, UNSUBACK |
| 146 | 0x92 | Packet Identifier not found | PUBREL, PUBCOMP |
| 147 | 0x93 | Receive Maximum exceeded | DISCONNECT |
| 148 | 0x94 | Topic Alias invalid | DISCONNECT |
| 149 | 0x95 | Packet too large | CONNACK, DISCONNECT |
| 150 | 0x96 | Message rate too high | DISCONNECT |
| 151 | 0x97 | Quota exceeded | CONNACK, PUBACK, PUBREC, SUBACK, DISCONNECT |
| 152 | 0x98 | Administrative action | DISCONNECT |
| 153 | 0x99 | Payload format invalid | CONNACK, PUBACK, PUBREC, DISCONNECT |
| 154 | 0x9A | Retain not supported | CONNACK, DISCONNECT |
| 155 | 0x9B | QoS not supported | CONNACK, DISCONNECT |
| 156/157 | 0x9C/9D | Use another server / Server moved | CONNACK, DISCONNECT |
| 158 | 0x9E | Shared Subscriptions not supported | SUBACK, DISCONNECT |
| 159 | 0x9F | Connection rate exceeded | CONNACK, DISCONNECT |
| 160 | 0xA0 | Maximum connect time | DISCONNECT |
| 161/162 | 0xA1/A2 | Subscription Identifiers / Wildcard Subscriptions not supported | SUBACK, DISCONNECT |

## 第 3 章 各报文（p.30–p.91）

### 3.1 CONNECT（p.30–44）
- 首字节 0x10（flags 全 0）。连接建立后**第一个**报文必须是 CONNECT（[MQTT-3.1.0-1]）；一条网络连接只允许发一次，第二次 = Protocol Error（[MQTT-3.1.0-2]）。
- **变长头字段顺序**（p.30）：Protocol Name → Protocol Level → Connect Flags → Keep Alive → Properties。
- Protocol Name 必须为 UTF-8 串 "MQTT"（0x00 0x04 'M' 'Q' 'T' 'T'，Figure 3-2，p.30–31）；Protocol Version = 5 (0x05)（p.31）；不匹配时 Server MAY 回 CONNACK 0x84 并必须关闭连接。
- **Connect Flags**（Figure 3-4，p.31–32）：bit7 User Name Flag、bit6 Password Flag、bit5 Will Retain、bit4-3 Will QoS、bit2 Will Flag、bit1 **Clean Start**、bit0 Reserved 必须为 0（[MQTT-3.1.2-3]）。
- **Clean Start**（p.32）：=1 → 丢弃既有 Session 开新 Session（CONNACK 的 Session Present 必为 0）；=0 且有 Session → 续用既有状态；=0 且无 Session → 新建。
- **Will Flag**（p.32–33）：=1 时 Will Message（Will Properties+Topic+Payload）必须存入 Server；发布触发条件：I/O/网络故障、Keep Alive 超时、未发 DISCONNECT(0x00) 即断开（双向）。收到 DISCONNECT(0x00) 或 Will Delay 期内重连则删除/不发（[MQTT-3.1.2-8]）。
- **Will QoS**（p.33）：0/1/2，3 = Malformed；Will Flag=0 时必须为 0。**Will Retain**（p.33）：控制遗嘱是否带保留标志发布。
- v5 新特性（非规范性注释，p.33）：Password 可不带 User Name（v3.1.1 不允许）。
- **Keep Alive**（p.34）：Two Byte Integer，秒；非零时无其他报文则 Client 必须发 PINGREQ（[MQTT-3.1.2-20]）；Server 在 1.5×Keep Alive 内未收到任何报文必须断开（[MQTT-3.1.2-22]）；CONNACK 带 Server Keep Alive 则 Client 必须改用它；0 = 关闭机制；最大 65,535 秒 = 18 小时 12 分 15 秒（非规范注释）。
- **CONNECT 属性**（p.34–38）：Session Expiry Interval 0x11（缺省 0 = 连接关即 Session 结束；0xFFFFFFFF = 永不过期；>0 时断开后必须保存状态 [MQTT-3.1.2-23]）；Receive Maximum 0x21（缺省 65,535，禁止 0/重复）；Maximum Packet Size 0x27（禁止 0；Server 超限必须丢弃该报文并当作已发送完成 [MQTT-3.1.2-25]）；Topic Alias Maximum 0x22（缺省 0 = 不接受任何 Topic Alias）；Request Response Information 0x19（缺省 0）；Request Problem Information 0x17（缺省 1；=0 时除 PUBLISH/CONNACK/DISCONNECT 外不得带 Reason String/User Properties）；User Property 0x26；Authentication Method 0x15（出现则增强认证启动，CONNACK 前只能发 AUTH/DISCONNECT [MQTT-3.1.2-30]）；Authentication Data 0x16（无 Method 时出现 = Protocol Error）。
- **Payload 字段顺序**（p.40，正文）：Client Identifier → Will Properties → Will Topic → Will Payload → User Name → Password。【冲突】附录 B 的 [MQTT-3.1.3-1]（p.123）写成 "Client Identifier, Will Topic, Will Message, User Name, Password"，漏了 Will Properties——以正文 §3.1.3 为准（两处同为规范文本，规范自身笔误）。
- **ClientID**（p.40）：必有且为第一个字段；Server 必须接受 1–23 字节、仅 `0-9a-zA-Z` 的 ClientID（[MQTT-3.1.3-5]）；零长度 ClientID → Server 必须分配唯一 ID 并在 CONNACK 返回 Assigned Client Identifier（p.40、p.49）。
- **Will Properties**（p.40–42）：Will Delay Interval 0x18（缺省 0；延迟到「超时或 Session 结束」先到者；期内重连必须不发 [MQTT-3.1.3-9]）、Payload Format Indicator 0x01、Message Expiry Interval 0x02、Content Type 0x03、Response Topic 0x08、Correlation Data 0x09、User Property 0x26。
- **Server 处理流程**（p.43–44）：合理时间内未收到 CONNECT 应关闭；校验失败可回 CONNACK(≥0x80) 后关闭；ClientID 已在线 → 向旧连接发 DISCONNECT 0x8E (Session taken over) 并关闭（[MQTT-3.1.4-3]）；成功 → CONNACK 0x00，开始消息分发与 Keep Alive 监控。Client 可以在收到 CONNACK 前就发后续报文（p.44）。

### 3.2 CONNACK（p.44–53）
- 首字节 0x20。Server 发送非 AUTH 报文前必须先发 RC=0x00 的 CONNACK（[MQTT-3.2.0-1]）；一条连接只发一个（[MQTT-3.2.0-2]）。发 RC≥0x80 后必须关闭连接（p.46）。
- 变长头顺序（p.45）：Connect Acknowledge Flags（bit0 = **Session Present**，bit7-1 保留 0）→ Connect Reason Code → Properties。
- Session Present（p.45–46）：Clean Start=1 时必为 0；Clean Start=0 且 Server 有该 ClientID 状态则为 1。Client 状态与标志不符时的处理（p.46）。非零 RC 的 CONNACK 必须置 Session Present=0。
- Connect Reason Code 表（Table 3-1，p.46–47）：0x00 Success；0x80/81/82/83；0x84 Unsupported Protocol Version；0x85 Client Identifier not valid；0x86 Bad User Name or Password；0x87 Not authorized；0x88 Server unavailable；0x89 Server busy；0x8A Banned；0x8C Bad authentication method；0x90 Topic Name invalid（Will Topic）；0x95 Packet too large；0x97 Quota exceeded；0x99 Payload format invalid（Will）；0x9A Retain not supported；0x9B QoS not supported；0x9C Use another server；0x9D Server moved；0x9F Connection rate exceeded。
- CONNACK 属性（p.47–52）：Session Expiry（可覆盖 Client 值）、Receive Maximum、Maximum QoS（0/1；缺省即支持 QoS 2；Server 不支持 QoS1/2 时必须声明，但仍必须接受请求 QoS 0/1/2 的 SUBSCRIBE [MQTT-3.2.2-9/-10]）、Retain Available（0=不支持保留消息）、Maximum Packet Size、Assigned Client Identifier、Topic Alias Maximum、Reason String、User Property、Wildcard/Subscription Identifier/Shared Subscription Available、Server Keep Alive、Response Information、Server Reference（配 0x9C/0x9D）、Authentication Method/Data。无 Payload（p.53）。

### 3.3 PUBLISH（p.53–62）
- 首字节 = 0x30 | DUP<<3 | QoS<<1 | RETAIN（Figure 3-8，p.53）。**DUP**（p.53）：重发时必须置 1；QoS0 必须为 0；Server 转发时 DUP 独立于入站报文按「是否重发」设置。**QoS**（Table 3-2，p.54）：0=至多一次、1=至少一次、2=恰好一次；两位同时为 1 禁止（[MQTT-3.3.1-4]）。**RETAIN**（p.54–55）：=1 时 Server 必须替换存储该主题保留消息；**Payload 为 0 字节 = 删除保留消息**（[MQTT-3.3.1-6/-7]）；转发时 RETAIN 由订阅选项 Retain As Published 决定。
- 变长头顺序（p.55）：**Topic Name**（必为第一字段，不得含通配符 [MQTT-3.3.2-2]）→ Packet Identifier（仅 QoS>0）→ Properties。
- PUBLISH 属性（p.56–59）：Payload Format Indicator 0x01（Server 原样转发）、Message Expiry Interval 0x02（Server 下发时必须减去在本 Server 等待的时间 [MQTT-3.3.2-6]）、Topic Alias 0x23（0 禁止；映射仅限单条连接 [MQTT-3.3.2-7]；双向各自独立维护）、Response Topic 0x08（不得含通配符）、Correlation Data 0x09、User Property 0x26（必须保序转发）、Subscription Identifier 0x0B（1–268,435,455；Client→Server 的 PUBLISH 不得携带 [MQTT-3.3.4-6]）、Content Type 0x03。
- Payload = 应用消息本体（p.60），可为 0 长度。
- 响应规则（Table 3-3，p.60）：QoS0 无响应、QoS1 → PUBACK、QoS2 → PUBREC。多订阅重叠时 Server 必须按所有匹配订阅的最大 QoS 分发（[MQTT-3.3.4-2]）。流量控制：Client/Server 未确认的 QoS>0 PUBLISH 不得超过对端 Receive Maximum，超限用 DISCONNECT 0x93（p.62）。

### 3.4 PUBACK（p.62–65）
- 首字节 0x40。变长头顺序：Packet Identifier → PUBACK Reason Code → Property Length → Properties（Figure 3-11，p.63）。**Remaining Length=2 时省略 RC 与属性（RC 视为 0x00）**——最短实现只需 4 字节。
- RC 表（Table 3-4，p.63–64）：0x00 Success；0x10 No matching subscribers（仅 Server 可用）；0x80；0x83；0x87；0x90；0x91；0x97；0x99。无 Payload。

### 3.5 PUBREC（p.65–67）
- 首字节 0x50。QoS2 第 1 步确认。结构同 PUBACK（PID→RC→Props，RL=2 可省略）。RC 表（Table 3-5，p.66）与 PUBACK 相同集合（0,16,128,131,135,144,145,151,153）。无 Payload。

### 3.6 PUBREL（p.67–69）
- 首字节 **0x62**（flags 必须为 0010，[MQTT-3.6.1-1]）。QoS2 第 2 步。结构同上。RC 表（Table 3-6，p.68）：仅 0x00 Success、0x92 Packet Identifier not found。无 Payload。

### 3.7 PUBCOMP（p.69–71）
- 首字节 0x70。QoS2 第 3（最终）步。结构同上。RC 表（Table 3-7，p.70）：0x00、0x92。无 Payload。

### 3.8 SUBSCRIBE（p.71–76）
- 首字节 **0x82**（flags 固定 0010，[MQTT-3.8.1-1]）。变长头：Packet Identifier → Properties（Subscription Identifier 0x0B、User Property）（p.71–72）。
- Payload（p.72–74）：≥1 组（Topic Filter + Subscription Options 字节）；空 Payload = Protocol Error。Subscription Options：bit1-0 = 请求的最大 QoS（3 = Protocol Error）；bit2 = **No Local**（=1 时不向同一 ClientID 的连接回发；对共享订阅置 1 = Protocol Error [MQTT-3.8.3-4]）；bit3 = **Retain As Published**（=1 转发保留原 RETAIN 标志；=0 转发时置 0）；bit5-4 = **Retain Handling**：0=订阅时发送保留消息、1=仅当该订阅是新建时发送、2=订阅时不发送（3 = Protocol Error）；bit7-6 保留必须为 0（p.73）。
- 语义（p.75）：同 Session 同 Topic Filter 的非共享订阅 → 必须替换旧订阅；Server 可在发 SUBACK 前就开始发匹配的 PUBLISH；实际下发 QoS = min(发布 QoS, 授予 QoS)（[MQTT-3.8.4-8]）。

### 3.9 SUBACK（p.77–79）
- 首字节 0x90。变长头：Packet Identifier → Properties。Payload = 与 SUBSCRIBE 中 Topic Filter **顺序一致**的 RC 列表（[MQTT-3.9.3-1]）。RC 表（Table 3-8，p.78–79）：0x00/0x01/0x02 Granted QoS 0/1/2；0x80；0x83；0x87；0x8F；0x91；0x97；0x9E；0xA1；0xA2。

### 3.10 UNSUBSCRIBE（p.79–81）
- 首字节 **0xA2**（flags 固定 0010）。变长头：PID → Properties（User Property）。Payload = ≥1 个 Topic Filter（UTF-8 串连续排列）。退订按**逐字符精确匹配**删除订阅（[MQTT-3.10.4-1]）；未删任何订阅也必须回 UNSUBACK（p.81）。

### 3.11 UNSUBACK（p.81–83）
- 首字节 0xB0。变长头：PID → Properties。Payload = 与 UNSUBSCRIBE 顺序一致的 RC 列表（Table 3-9，p.83）：0x00 Success；0x11 No subscription existed；0x80；0x83；0x87；0x8F；0x91。

### 3.12 PINGREQ / 3.13 PINGRESP（p.83–85）
- 首字节分别为 0xC0 / 0xD0，**Remaining Length=0，无变长头无 Payload**。Server 收到 PINGREQ 必须回 PINGRESP（[MQTT-3.12.4-1]）；Client 收到 PINGRESP 无动作。

### 3.14 DISCONNECT（p.85–89）
- 首字节 0xE0。**Server 与 Client 都可发**（v5 新增；Server 必须在发出 RC<0x80 的 CONNACK 之后才能发 DISCONNECT [MQTT-3.14.0-1]）。
- 变长头：Disconnect Reason Code → Properties；**RL=0 时 RC 视为 0x00 (Normal disconnection)**，无属性。
- RC 表（Table 3-10，p.86–87）：0x00（双方，不发遗嘱）；0x04（Client，要求 Server 立即发遗嘱）；0x80/81/82/83；0x87（Server）；0x89 Server busy；0x8B Server shutting down；0x8D Keep Alive timeout；0x8E Session taken over；0x8F/0x90；0x93 Receive Maximum exceeded；0x94 Topic Alias invalid；0x95 Packet too large；0x96 Message rate too high；0x97；0x98 Administrative action；0x99；0x9A/0x9B（Server）；0x9C/0x9D（Server，重定向）；0x9E（Server）；0x9F Connection rate exceeded；0xA0 Maximum connect time；0xA1/0xA2（Server）。
- 属性（p.88）：Session Expiry Interval 0x11（仅 Client 可发 [MQTT-3.14.2-2]；若 CONNECT 里为 0，DISCONNECT 中置非零 = Protocol Error）、Reason String、User Property、Server Reference 0x1C。无 Payload。
- 动作（p.89）：发送方发完必须关连接且不再发任何报文；Server 收到 0x00 必须丢弃遗嘱不发布。

### 3.15 AUTH（p.89–91）
- 首字节 0xF0（flags 全 0）。双向，用于增强认证的 challenge/response；**CONNECT 未带 Authentication Method 时发 AUTH = Protocol Error**（p.89）。
- 变长头：Authenticate Reason Code → Properties；RL=0 时 RC 视为 0x00。RC 表（Table 3-11，p.90）：0x00 Success（Server）；0x18 Continue authentication（双方）；0x19 Re-authenticate（Client）。属性：Authentication Method（必须）、Authentication Data、Reason String、User Property。无 Payload。

## 第 4 章 Operational behavior（p.92–p.110）

### 4.1 Session State（p.92）
- **Client 侧状态**：①已发未完全确认的 QoS1/QoS2 消息；②已收未完全确认的 QoS2 消息。
- **Server 侧状态**：①Session 存在性（即使其余为空）；②该 Client 的订阅（含 Subscription Identifiers）；③已发未完全确认的 QoS1/2 消息；④待发的 QoS1/2 消息（可选含 QoS0）；⑤已收未完全确认的 QoS2 消息；⑥Will Message 与 Will Delay Interval；⑦未连接时 Session 的到期时刻。
- **Retained messages 不属于 Session State**，Session 结束不删除（p.92）。存储规则（4.1.1，p.92）：连接期间不得丢弃状态；连接关闭且 Session Expiry 到期后 Server 必须丢弃。

### 4.2 Network Connections（p.93）
- 底层传输必须提供**有序、无损的字节流**（双向）（[MQTT-4.2-1]）。TCP/IP、TLS、WebSocket 可用；UDP 等无连接协议不合适。**非规范注释：IANA 已注册 1883（非 TLS）与 8883（TLS）端口**。

### 4.3 QoS 0/1/2 消息流（p.93–97）
- 交付协议是对称的：Client/Server 都可作发送方或接收方；Server 向多个 Client 分发时各 Client 独立处理（p.93）。
- **QoS 0（4.3.1，p.94）**：发送方发 PUBLISH(QoS0, DUP=0)；接收方收到即取得消息所有权，无响应、无重试。
- **QoS 1（4.3.2，p.94–95）**：发送方：分配未用 PID → PUBLISH(QoS1, DUP=0) → 视为未确认直到收到对应 PUBACK；等待期间可继续发其他 PID 的 PUBLISH。接收方：接受所有权并回 PUBACK（同 PID）；**发过 PUBACK 后，同 PID 的新 PUBLISH 一律按新消息处理**（[MQTT-4.3.2-5]）。流程：`PUBLISH(QoS1,DUP=0) → PUBACK`（Figure 4.2，p.95）。
- **QoS 2（4.3.3，p.95–97）**：四步握手，报文方向：
  1. 发送方 → 接收方：PUBLISH(QoS2, DUP=0, PID)；
  2. 接收方 → 发送方：PUBREC(PID, RC)（RC≥0x80 则失败，PID 可复用）；
  3. 发送方 → 接收方：PUBREL(PID)（收到 RC<0x80 的 PUBREC 后必须发）；
  4. 接收方 → 发送方：PUBCOMP(PID)。
  发送方约束：PUBLISH 与 PUBREL 各自视为未确认直到收到下一步响应；**发出 PUBREL 后不得再重发 PUBLISH**（[MQTT-4.3.3-6]）；PUBLISH 已发出后不得应用消息过期（[MQTT-4.3.3-7]）；收到 PUBCOMP 或 RC≥0x80 的 PUBREC 后 PID 可复用。接收方约束：收到 PUBREL 前，同 PID 重复 PUBLISH 必须再回 PUBREC 且**不得向下游重复投递**（[MQTT-4.3.3-10]）；收到 PUBREL 必须回 PUBCOMP；即使已应用消息过期也必须继续完成 QoS2 确认序列（[MQTT-4.3.3-13]）。流程图 Figure 4.3（p.96–97）。
- 接收方无需先完成向下游投递即可回 PUBACK/PUBREC——此时消息所有权移交接收方（p.95、p.97 脚注）。

### 4.4 Message delivery retry（p.96）
- **v5 关键规则**：仅当 Client 以 Clean Start=0 重连且 Session 存在时，双方**必须**用原 PID 重发所有未确认的 PUBLISH（QoS>0）与 PUBREL；**这是唯一必须重发的场景，其他任何时刻都禁止重发**（[MQTT-4.4.0-1]）。（对比 v3.1.1 的重发机制已被移除。）
- 收到 RC≥0x80 的 PUBACK/PUBREC 即视为已确认，不得再重发（[MQTT-4.4.0-2]）。

### 4.5 Message receipt（p.97）
- Server 接管消息后必须为所有匹配订阅的 Client 加入其 Session State。Client 无论是否处理消息，都必须按 QoS 规则确认收到的 PUBLISH（[MQTT-4.5.0-2]）。

### 4.6 Message ordering（p.97–98）
- Client 重发 PUBLISH 必须按原发送顺序；PUBACK/PUBREC 必须按对应 PUBLISH 的接收顺序发；PUBREL 按 PUBREC 的接收顺序发（[MQTT-4.6.0-1..4]）。
- **Ordered Topic**：Server 对同一 Topic+QoS 的消息必须按来自任一 Client 的接收顺序转发；**非共享订阅下默认所有 Topic 都是 Ordered Topic**（[MQTT-4.6.0-6]）。非规范注释（p.98）：QoS1 重连后可能收到 1,2,3,2,3,4 的重复序列；双方 Receive Maximum=1 可严格保证不乱序。

### 4.7 Topic Name / Topic Filter 语法（p.98–101）
- 层级分隔符 `/`（U+002F）；相邻分隔符表示零长度层级（p.98）。
- 通配符只能用于 **Topic Filter**，禁止出现在 **Topic Name**（[MQTT-4.7.0-1]）。
- **`#`（多级通配）**：单独使用或必须紧跟 `/`，且**必须是 Filter 最后一个字符**（[MQTT-4.7.1-1]）；`sport/#` 也匹配父级 `sport`；`sport/tennis#`、`sport/tennis/#/x` 非法（p.99）。
- **`+`（单级通配）**：必须独占整个层级，可用于任意层级（含首尾）（[MQTT-4.7.1-2]）；`sport/+` 匹配 `sport/` 但不匹配 `sport`；`/finance` 匹配 `+/+` 和 `/+` 但不匹配 `+`（p.99）。
- **`$` 开头主题**（p.99–100）：Server 不得把以 `#`/`+` 开头的 Filter 匹配到 `$` 主题（[MQTT-4.7.2-1]）——订阅 `#` 收不到 `$SYS/...`；要同时收 `$SYS` 与普通主题需同时订阅 `#` 和 `$SYS/#`。
- 语义（4.7.3，p.100）：≥1 字符；大小写敏感；可含空格；前导/末尾 `/` 构成不同主题；仅 `/` 的主题合法；禁止 U+0000；UTF-8 编码后 ≤65,535 字节；匹配时 Server **不得做任何规范化**（[MQTT-4.7.3-4]）。

### 4.8 Subscriptions（p.101–103）
- 两类：Non-shared（绑定单 Session，同 Session 同 Filter 只能一条，不能负载均衡）与 **Shared**（多 Session 共享，每条消息只发给其中一个 Session——用于负载均衡）。
- 共享订阅 Filter 格式：`$share/{ShareName}/{filter}`；ShareName ≥1 字符且不含 `/`、`+`、`#`（[MQTT-4.8.2-1/-2]）。订阅共享订阅**不发送保留消息**；共享订阅存活到至少有一个关联 Session；无关联 Session 时删除并清除未投递消息（p.101–102）。
- QoS2 传输中断线：Server 必须在该 Client 重连后完成投递，Session 先终止则不得转投他人（[MQTT-4.8.2-4/-5]）；收到 RC≥0x80 的 ACK 则 Server 必须丢弃该消息且不转投（p.103）。

### 4.9 Flow Control（p.103–104）
- **Receive Maximum**（双方在 CONNECT/CONNACK 各自声明，缺省 65,535）限定未确认（未收 PUBACK/PUBCOMP）的 QoS>0 PUBLISH 数量。发送方维护 send quota：初始为不超过 Receive Maximum 的非零值（[MQTT-4.9.0-1]）；每发一条 QoS>0 PUBLISH 减 1，减到 0 必须停发 QoS>0（但必须继续处理所有其他报文 [MQTT-4.9.0-3]）。
- 配额 +1 时机：每收到 PUBACK 或 PUBCOMP（无论 RC 是否报错）、每收到 RC≥0x80 的 PUBREC；不超过初始值（p.104）。quota 与 Receive Maximum **不跨连接保留**，不属于 Session State。

### 4.10 Request/Response（p.104–106，非规范）
- Response Topic + Correlation Data 形式化请求/响应模式；Response Information（CONNACK）帮助 Client 构造响应主题。响应消息不带 Response Topic 属性。

### 4.11 Server redirection（p.106）
- CONNACK/DISCONNECT 用 0x9C（临时换 Server）/0x9D（永久换）+ 可选 Server Reference（UTF-8 串，空格分隔的 "host[:port]" 列表，格式非规范）。

### 4.12 Enhanced authentication（p.106–108）
- CONNECT 带 Authentication Method 后，可在 CONNECT 与 CONNACK 之间交换 AUTH 报文做 challenge/response（类 SASL）认证；Server 不支持该方法 → CONNACK 0x8C 或 0x87 并关闭（[MQTT-4.12.0-1]）。
- 中间 AUTH 必须 RC=0x18；认证成功以 CONNACK RC=0 结束；后续所有 AUTH 与成功 CONNACK 必须携带与 CONNECT 相同的 Authentication Method（[MQTT-4.12.0-5]）。示例：SCRAM-SHA-1、GS2-KRB5 流程（p.108）。
- 对 Client/Server 都是 **OPTIONAL**；Client 未带 Method 时双方都不得发 AUTH（[MQTT-4.12.0-6/-7]）。
- **Re-authentication**（4.12.1，p.108）：连接中 Client 随时可发 AUTH(0x19) 重认证；失败则发 DISCONNECT 并关闭。

### 4.13 Handling errors（p.109–110）
- Malformed Packet / Protocol Error：Client SHOULD 关闭连接（可先发 DISCONNECT 带 RC）；Server **必须**关闭（[MQTT-4.13.1-1]）。CONNACK/DISCONNECT 带 RC≥0x80 即表示连接将关闭（[MQTT-4.13.2-1]）。

## 第 5 章 Security（p.111–p.117，整章 non-normative）
- 强烈建议支持 TLS 的实现使用 TCP 8883（IANA 名 secure-mqtt）（p.111）。
- 5.2：可对标 NIST CSF、PCI-DSS、FIPS 140-2、NSA Suite B（p.111–112）。5.3：受限设备可用 ChaCha20（软件快于 AES、嵌入式少硬件支持）与 ISO 29192 轻量密码（p.112）。
- 5.4 实现要点：认证（User Name/Password、LDAP/OAuth、TLS 客户端证书、4.12 增强认证；明文凭证有 MITM/重放风险，p.112）；授权（尤其校验 ClientID 使用权以防会话劫持；限制 `#` 等宽 Filter，p.112–113）；Client 对 Server 的认证（基本认证无此机制，TLS 证书或增强认证可做双向认证，p.113）；完整性（TLS hash、应用层自加 hash，p.113）；隐私（TLS 加密；避免 NULL 加密套件；应用层可独立加密 payload，p.113–114）；抵赖性（p.114）；失陷检测（证书绑定主机名、CRL/OCSP，p.114）；异常行为监测（反复连接/认证、异常断开、topic scanning、动态黑名单，p.114–115）；Disallowed Unicode 码点处理（Server 不校验而 Client 校验时，发布者可致订阅者断连——给出三类补救，p.115–116）；长期连接的证书轮换与重认证（p.116）；SOCKSv5 代理（p.116–117）；安全档案分级：明文 / 安全网络（VPN）/ 安全传输（TLS）/ 行业档案（p.117）。

## 第 6 章 WebSocket 传输（p.118）
- 报文必须用 WebSocket 二进制帧承载；帧边界与报文边界不对齐，接收方不得假设对齐；Client 必须提供子协议名 `mqtt`，Server 必须选择返回 `mqtt`；URI 不影响协议。IANA 注册 mqtt 子协议（6.1，p.118）。

## 第 7 章 Conformance（p.119）
- 分别定义 Server 与 Client 一致性条款：报文格式符合第 2/3 章、遵守 4.7/4.8 主题与订阅规则（Server）、满足第 1/2/3/4/6 章 MUST 级要求（各自排除对方专属条款）、不依赖规范外扩展。

## 附录（p.120–p.137）
- **Appendix A**（p.120）：致谢（MQTT 原始发明人 Andy Stanford-Clark 与 Arlen Nipper，OASIS TC 成员名单）。
- **Appendix B**（p.121–135，non-normative）：正文全部编号规范声明（[MQTT-x.y.z-n]）的汇总索引。
- **Appendix C**（p.136–137，non-normative）：v5.0 新特性一览：Session expiry（Clean Start + Session Expiry 拆分 Clean Session）、Message expiry、所有 ACK 带 Reason Code 与 Reason String、Server 可发 DISCONNECT、Payload Format & Content Type、Request/Response、Shared Subscriptions、Subscription ID、Topic Alias、Flow Control（Receive Maximum）、User Properties、Maximum Packet Size、可选 Server 能力声明（Maximum QoS / Retain Available / Wildcard / Subscription Identifier / Shared Subscription Available）、Enhanced authentication（含连接内重认证）、Subscription options（NoLocal、Retain Handling）、Will delay、Server Keep Alive、Assigned ClientID、Server reference。

---

## 已发现的规范内部冲突（一级证据内部不一致，记录在案）

1. **Retain Handling = 1 的语义**：正文 §3.3.1.3（p.55）与 §3.8.3.1（p.73）均为「仅当订阅**不存在**（新建）时发送保留消息」；但附录 B 的 [MQTT-3.3.1-10]（p.126）写成「订阅**已存在**时必须发送」——两处矛盾。业界通行实现按正文语义（新建才发），附录 B 为该版规范笔误。
2. **CONNECT Payload 顺序**：正文 §3.1.3（p.40）为 Client Identifier → Will Properties → Will Topic → Will Payload → User Name → Password；附录 B [MQTT-3.1.3-1]（p.123）漏写 Will Properties。以正文为准（Will Flag=1 时 Will Properties 必在 Payload，见 §3.1.3.2 p.40）。

---

## 三档分类（面向本科毕设：Ubuntu 22.04 + 树莓派 + C++ 自研轻量 broker）

### 🔴 最小可用 broker 必须实现
- 数据表示全套（§1.5）：UTF-8 串、2/4 字节整数、VBI 编解码（含最少字节校验与 4 字节上限）。
- Fixed Header：类型值表、PUBLISH 的 DUP/QoS/RETAIN、PUBREL/SUBSCRIBE/UNSUBSCRIBE 的 0010 flags、Remaining Length（§2.1）。
- 15 种报文的编解码与状态机（§3）：CONNECT 全部校验（Protocol Name/Level、ClientID、flags、Keep Alive 1.5× 断开）、CONNACK（Session Present + 0x00）、PUBLISH（Topic Name、通配符禁止）、QoS1 PUBACK、QoS2 四步握手、SUBSCRIBE/SUBACK、UNSUBSCRIBE/UNSUBACK、PINGREQ/PINGRESP、DISCONNECT。
- 核心行为（§4）：QoS0/1/2 完整消息流与 PID 管理（4.3）、重连重发规则（4.4）、消息顺序（4.6）、主题语法与匹配（4.7 含 `#`/`+`/`$` 规则）、保留消息（3.3.1.3）、会话状态存续（4.1）。
- 理由：这些是 §7 一致性条款的 MUST 主体，缺一则不与任何标准客户端（mosquitto_pub/sub 等）互通，也无法通过互操作测试。

### 🟡 建议实现但可后置
- Properties 子集：Session Expiry、Receive Maximum（流控）、Maximum Packet Size、User Property、Reason String——边缘场景下省带宽/省内存，实现难度低、答辩加分。
- Keep Alive 的 Server Keep Alive 覆盖、Retain As Published / Retain Handling 三值、No Local。
- 每报文完整 Reason Code 矩阵 + 4.13 错误处理闭环（可先只发 0x81/0x82/0x87）。
- 理由：都是 MUST 但在「最小互通」之上才被测试到；实现顺序放在 broker 主干跑通之后。

### 🟢 本科毕设可跳过（说明理由）
- 4.12 增强认证 / AUTH 报文 / 重认证：规范标注 OPTIONAL，需双端配合，毕设用 User Name/Password + TLS 已够。
- 4.8.2 共享订阅（`$share/`）：负载均衡场景，边缘网关演示用不到；CONNACK 的 Shared Subscription Available=0 即可合法拒绝。
- Topic Alias（0x23）：纯带宽优化，长主题重复发送才有收益；Topic Alias Maximum 缺省 0 即合法禁用。
- 4.10 Request/Response、4.11 Server redirection（0x9C/0x9D + Server Reference）：非规范模式/可选重定向。
- 第 6 章 WebSocket 传输：另有 TCP 即满足 §4.2；毕设网络层用 TCP/TLS。
- 第 5 章安全（非规范章）：写成论文相关工作一段即可，不要求代码实现。
- 理由：均为 OPTIONAL / non-normative / 性能优化项，不影响与标准客户端互操作，也不进入最小 MUST 集。
