# R1 MQTT5.0规范精读

> **MQTT Version 5.0**（MQTT 5.0 版规范）/ OASIS Standard / 2019-03-07 发布 / 全文 137 页。
> 页码口径：**物理页码**（PDF 第 1 页 = p.1，与页脚 "Page N of 137" 一致）。配套：[[R2MQTT3.1.1规范精读]]（3.1.1 版打底）· 总进度：[[毕设完成流程书]]。
> 阅读定位：规范不是用来从头读到尾的小说，而是**写代码时的字典 + 测试时的法规依据**。先通读第二、三、四、八节建立框架，实现到哪一模块再回来精查对应小节。

## 一、这份规范规定了什么（§1，p.11–20）

- **含义**：MQTT 是一个基于 [[TCP（传输控制协议）]] 这类字节流的轻量级 [[发布订阅模式]] 协议标准，本文件规定了 15 种控制报文的**字节级格式**（§2–3）和收发双方的**行为规则**（§4），并用 `MUST/SHOULD/MAY` 三档关键词标注约束强度（MUST=必须做到，不做就不兼容；SHOULD=强烈建议；MAY=可选）。
- **为什么需要**：毕设的自研 broker 要和 mosquitto、paho 等标准实现互通，互通的唯一裁判就是这份规范——测试报错时查「规范哪一条 MUST 被违反了」，比自己猜快得多。
- 角色模型（p.9–10 术语表在 3.1.1 侧，v5.0 术语见 p.11–13）：**Client**（终端，永远主动发起连接）→ **Server**（即 [[Broker（消息代理）]]，接受连接、维护订阅、转发消息）→ **Session**（会话状态，可以跨越多次网络连接存在）。

## 二、字节怎么排：数据表示与报文结构（§1.5 + §2，p.16–29）

### 2.1 四种基本数据类型（§1.5，p.16–19）

- **Two Byte / Four Byte Integer**（p.16）：16/32 位无符号整数，**大端序**（最高位字节先发——就像写日期先写年再写月日，网络协议几乎都用这个顺序）。
- **UTF-8 Encoded String**（p.16–18）：前缀 2 字节长度 + 内容字节，最长 65,535 字节；含 U+0000 或坏编码 = Malformed Packet（p.17–18）。
- **Variable Byte Integer（VBI，变长字节整数）**（p.18–19）：每字节低 7 位是数据、最高位是「还有下一字节」的标志；最多 4 字节，上限 268,435,455（约 256 MB）；**必须用最少字节编码**（[MQTT-1.5.5-1]）。1 字节 0–127 / 2 字节到 16,383 / 3 字节到 2,097,151 / 4 字节到 268,435,455（Table 1-1，p.18）。
  - 通俗理解：像压缩包号的「滚动计数」——小数字只占 1 字节，大数字才多占，省带宽。
  - **为什么最先实现它**：Remaining Length（报文长度字段）用它编码，解析任何报文第一步都过它，是编解码器的地基。

### 2.2 Fixed Header：固定头（§2.1，p.21–23）

- **含义**：每个报文最开头的 2+ 字节：byte1 高 4 位 = 报文类型，低 4 位 = 类型相关 flags；byte2 起是 Remaining Length（只算后面的部分，不含自身）。
- **为什么需要**：收到一段字节流，broker 全靠这 1 个字节判断「这是什么报文、该走哪个处理分支」。

| 值 | 报文 | 方向 | 干什么 |
|---|---|---|---|
| 1 | CONNECT | C→S | 连接请求 |
| 2 | CONNACK | S→C | 连接确认 |
| 3 | PUBLISH | 双向 | 发消息 |
| 4 | PUBACK | 双向 | QoS1 确认 |
| 5 | PUBREC | 双向 | QoS2 第 1 步确认 |
| 6 | PUBREL | 双向 | QoS2 第 2 步 |
| 7 | PUBCOMP | 双向 | QoS2 第 3 步（收尾）确认 |
| 8 | SUBSCRIBE | C→S | 订阅 |
| 9 | SUBACK | S→C | 订阅确认 |
| 10 | UNSUBSCRIBE | C→S | 退订 |
| 11 | UNSUBACK | S→C | 退订确认 |
| 12/13 | PINGREQ/PINGRESP | C→S/S→C | 心跳 |
| 14 | DISCONNECT | **双向** | 断开通知（v5 新增 Server 也能发） |
| 15 | AUTH | 双向 | 增强认证（v5 新增） |
| 0 | Reserved | Forbidden | 保留禁用 |

（Table 2-1，p.21–22。）flags 规则（Table 2-2，p.22–23）：只有 **PUBLISH** 用 flags（bit3=DUP、bit2-1=QoS、bit0=RETAIN）；**PUBREL/SUBSCRIBE/UNSUBSCRIBE** 低 4 位固定 `0010`（首字节 0x62/0x82/0xA2）；其余全 0。flags 不对 = Malformed Packet，必须断连。

### 2.3 Packet Identifier：包标识符（§2.2.1，p.23–25）

- **含义**：2 字节编号，QoS>0 的 PUBLISH 和所有确认类报文靠它「对暗号」。
- **为什么需要**：QoS 机制的本质是「收到后要回执」，回执必须说明确认的是哪条消息——这个编号就是回执上的单号。复用时机：QoS1 收到 PUBACK 后、QoS2 收到 PUBCOMP（或失败 PUBREC）后（p.24）；QoS0 **禁止带** PID（[MQTT-2.2.1-2]）。

### 2.4 Properties 属性区（§2.2.2，p.25–26）——v5 最大的新增

- **含义**：各报文变长头尾部的一串「键值对附加信息」，Property Length（VBI）+ 若干 (ID, 值)；**没有属性也必须写长度 0**。
- **为什么需要**：v3.1.1 想加任何新能力都得改报文结构；属性区让 v5 可以按需挂载新特性（会话过期、流控、别名等 30 个属性 ID 全表在 p.25–26）。毕设重点关注的子集：

| ID | 名称 | 类型 | 出现在 | 毕设用途 |
|---|---|---|---|---|
| 0x11 | Session Expiry Interval | 4 字节 | CONNECT/CONNACK/DISCONNECT | 会话过期（[[持久会话（Persistent Session）]] 的精细化） |
| 0x21 | Receive Maximum | 2 字节 | CONNECT/CONNACK | 流控（in-flight 上限，§4.9） |
| 0x22 | Topic Alias Maximum | 2 字节 | CONNECT/CONNACK | 缺省 0 = 禁用别名（可合法偷懒） |
| 0x27 | Maximum Packet Size | 4 字节 | CONNECT/CONNACK | 边缘设备保护自己 |
| 0x1F | Reason String | UTF-8 | 各 ACK/DISCONNECT | 调试信息 |
| 0x18 | Will Delay Interval | 4 字节 | Will Properties | 遗书延迟发布 |
| 0x02 | Message Expiry Interval | 4 字节 | PUBLISH | 消息过期 |

### 2.5 Reason Code 原因码（§2.4，p.27–29）

- **含义**：1 字节，**<0x80 = 成功**（常规成功 0x00），**≥0x80 = 失败并附原因**。SUBACK/UNSUBACK 在 Payload 里带一串（每个 filter 一个）。
- **为什么需要**：v3.1.1 出错只能「直接断连」，连为什么都不说；v5 的原因码让调试和日志可解释——这也是 [[抓包（packet capture）]] 验证时最容易核对的字段。常用值：0x81 Malformed Packet、0x82 Protocol Error、0x87 Not authorized、0x8D Keep Alive timeout、0x8E Session taken over（挤掉旧连接）、0x92 PID not found、0x9B QoS not supported（全表 p.27–29）。

## 三、15 种报文逐个拆（§3，p.30–91）

### 3.1 连接组：CONNECT / CONNACK（p.30–53）

- **CONNECT**（p.30–44）：连接建立后第一个报文，且一条连接只能发一次。变长头顺序固定：`Protocol Name "MQTT" → Level=5 → Connect Flags → Keep Alive → Properties`（p.30）。Connect Flags 位图（Figure 3-4，p.31–32）：bit7 User Name / bit6 Password / bit5 Will Retain / bit4-3 Will QoS / bit2 Will Flag / bit1 **Clean Start** / bit0 必须为 0。
  - **Clean Start**（p.32）：=1 抛弃旧会话从头来；=0 且服务器存有会话则续用（CONNACK 的 Session Present=1）。
  - **Keep Alive**（p.34）：心跳秒数；非零时空闲就得发 PINGREQ，Server 在 **1.5×Keep Alive** 内没收到任何报文必须断开（[MQTT-3.1.2-22]，p.43）；CONNACK 可用 Server Keep Alive 改约定期。
  - **Will（遗嘱）**（p.32–33，[[遗嘱消息]]）：Will Flag=1 时预先存好「遗书」，连接异常断开（非正常 DISCONNECT、心跳超时）时发布；正常断开（DISCONNECT 0x00）或 Will Delay 期内重连则不发。
  - **ClientID**（p.40）：1–23 字节纯 `[0-9a-zA-Z]` 必须接受；0 长度时 Server 必须分配并在 CONNACK 返回 Assigned Client Identifier。Payload 字段顺序：`ClientID → Will Properties → Will Topic → Will Payload → User Name → Password`（p.40）。
  - 同 ClientID 重复上线 → 旧连接收 DISCONNECT 0x8E 被挤掉（[MQTT-3.1.4-3]，p.43）。
- **CONNACK**（p.44–53）：Server 发的第一个报文；变长头 = Acknowledge Flags（bit0=**Session Present**）+ Reason Code + Properties。Session Present 告诉客户端「你上次的状态我还在不在」，客户端据此决定要不要重新订阅。发 RC≥0x80 后必须关连接（p.46）。

### 3.2 发布组：PUBLISH + 四个确认（p.53–71）

- **PUBLISH**（p.53–62）：首字节 = 0x30 | DUP<<3 | QoS<<1 | RETAIN。三条关键规则：
  - **RETAIN**（p.54–55，[[保留消息（Retained Message）]]）：置 1 时 Server 保存该主题「最后一条」给未来的订阅者；**0 字节 payload + RETAIN=1 = 删除保留消息**（[MQTT-3.3.1-6/-7]）。
  - **DUP**（p.53）：=1 表示这是重发；Server 转发时不继承入站 DUP，只看自己是否重发。
  - Topic Name 是第一个变长头字段，**禁止含通配符**（[MQTT-3.3.2-2]）。
  - 多个订阅重叠时按**最大 QoS** 投递（[MQTT-3.3.4-2]，p.60）；实际下发 QoS = min(发布 QoS, 订阅授予 QoS)。
- **PUBACK/PUBREC/PUBREL/PUBCOMP**（p.62–71）：结构统一 `PID → Reason Code → Properties`，且 **Remaining Length=2 时后两项省略**（RC 视为 0x00）——最短 4 字节报文，这是「轻量」的体现。PUBREL/SUBSCRIBE/UNSUBSCRIBE 首字节必须带 `0010` flags。PUBREC/PUBREL/PUBCOMP 只可能是 0x00 或 0x92（PID not found）。

### 3.3 订阅组：SUBSCRIBE / SUBACK / UNSUBSCRIBE / UNSUBACK（p.71–83）

- **SUBSCRIBE**（p.71–76）：`PID → Properties → 若干 (Topic Filter + Subscription Options)`，空 Payload = Protocol Error。Subscription Options 字节位图（p.73）：bit1-0 最大 QoS（3=非法）、bit2 **No Local**（不回发给自己）、bit3 **Retain As Published**、bit5-4 **Retain Handling**（0=订阅时发保留消息 / 1=仅新建订阅时发 / 2=不发）——后两项与 [[No Local 与 Retain As Published]] 概念页对应。
- **SUBACK**（p.77–79）：RC 列表顺序与 filter 一一对应（0x00/01/02 授予 QoS，≥0x80 拒绝）。
- **UNSUBSCRIBE**（p.79–81）：退订按**逐字符精确匹配**（[MQTT-3.10.4-1]），一个都没删也必须回 UNSUBACK。
- 同 Session 同 filter 重复订阅 = 替换旧订阅（p.75）；Server 可以在 SUBACK 之前就开始发匹配消息（p.75）。

### 3.4 保活与断开：PINGREQ / PINGRESP / DISCONNECT / AUTH（p.83–91）

- PINGREQ(0xC0)/PINGRESP(0xD0)：**Remaining Length=0 的纯心跳**，收到必回（[MQTT-3.12.4-1]）。通俗理解：像上班打卡——不打卡的客户端会被踢。
- **DISCONNECT**（p.85–89）：v5 里 Server 也能发（带 0x8D 心跳超时、0x8B 正在关机等原因）。客户端发 0x00 = 「正常下线，遗嘱作废」（[MQTT-3.14.4-2 类规则]，p.89）。
- **AUTH**（p.89–91）：增强认证的质询/应答报文，规范标 OPTIONAL，毕设可跳过（见第八节 🟢）。

## 四、broker 行为规则（§4，p.92–110）——写 broker 主要对齐这一章

### 4.1 Session State：会话状态清单（p.92）

- **含义**：Server 必须为每个会话保存的 7 类状态：①会话存在性；②订阅表；③已发未确认的 QoS1/2；④待发队列；⑤已收未确认的 QoS2；⑥遗嘱 + 延迟参数；⑦会话到期时刻。
- **为什么需要**：断线重连后能「接着上次说」，全靠这份清单——它就是 C++ 里 Session 结构体的字段定义，[[持久会话（Persistent Session）]] 的规范出处。注意：**保留消息不属于会话状态**（p.92），是全局字典。

### 4.2 传输要求（p.93）

底层必须是**有序、无损的双向字节流**（[MQTT-4.2-1]）；TCP/TLS/WebSocket 可用，UDP 不行。IANA 端口：1883（明文）/ 8883（TLS）。

### 4.3 QoS 0/1/2 消息流（p.93–97）★核心

- **QoS 0**（p.94）：发出去就不管，无回执无重试——像普通信件。
- **QoS 1**（p.94–95，[[QoS（服务质量）]]）：`PUBLISH → PUBACK` 两步；发出 PUBACK 后同 PID 的 PUBLISH 一律按新消息处理（[MQTT-4.3.2-5]）。像挂号信要签收。
- **QoS 2**（p.95–97，[[QoS 2 四次握手（4-way handshake）]]）四步握手，每步方向：

| 步 | 方向 | 报文 | 发送方此时状态 |
|---|---|---|---|
| 1 | S→R | PUBLISH(QoS2, PID) | 等 PUBREC |
| 2 | R→S | PUBREC(PID) | 收到 RC<0x80 才继续 |
| 3 | S→R | PUBREL(PID) | **发出后不得再重发 PUBLISH**（[MQTT-4.3.3-6]） |
| 4 | R→S | PUBCOMP(PID) | 完成，PID 可复用 |

  接收方去重前提：收到 PUBREL 之前，同 PID 的重复 PUBLISH 必须再回 PUBREC 但**不得重复投递**（[MQTT-4.3.3-10]）——这就是「恰好一次」的实现机关，也是最容易写错的地方。
- **为什么搞这么复杂**：两步（QoS1）只能保证「至少一次」，网络重发会导致重复；四步把「确认收到」和「确认处理完」拆开，才能「恰好一次」——代价是时延，[[4QoS级别与MQTT丢包时延相关性]] 实测过这个代价。

### 4.4 重发规则（p.96）

**唯一允许重发的场景**：Clean Start=0 重连且会话存在时，必须用原 PID 重发全部未确认的 PUBLISH/PUBREL（[MQTT-4.4.0-1]）；其他任何时刻禁止重发。收到 RC≥0x80 的确认即视为完成，不再重发。毕设的断线重连实验（流程书 W13）验证的就是这一条。

### 4.5 消息顺序（p.97–98）

确认类报文按对应 PUBLISH 的顺序发；对同一主题同一 QoS，Server 必须按收到顺序投递（Ordered Topic，[MQTT-4.6.0-6]）。非规范注释（p.98）：想严格不乱序，把 Receive Maximum 设为 1 即可。

### 4.6 主题语法与匹配（p.98–101）★

- 分隔符 `/`；相邻 `/` 表示空层（`sport//` 是合法的三层主题）。
- 通配符（[[通配符（wildcard）]]、[[Topic（主题）]]）只能出现在 **Topic Filter**（订阅用），**禁止出现在 Topic Name**（发布用）：
  - `#` 多层通配：必须独立成层且是最后一个字符；`sport/#` 也匹配父级 `sport`。
  - `+` 单层通配：必须独占一层；`/finance` 匹配 `+/+` 和 `/+` 但不匹配 `+`。
  - **`$` 开头主题**（p.99–100）：`#`/`+` 开头的 filter 不得匹配 `$` 主题——订阅 `#` 收不到 `$SYS/...`。
- 匹配时不做任何大小写、编码归一化，逐字符比较（[MQTT-4.7.3-4]）。

### 4.7 订阅的两种形态（p.101–103）

普通订阅绑定单会话；**共享订阅** `$share/{ShareName}/{filter}` 把负载分摊给多个会话（消费者组）。毕设不用实现（CONNACK 里 Shared Subscription Available=0 即可合法拒绝）。

### 4.8 Flow Control 流控（p.103–104）

Receive Maximum（双方各自声明，缺省 65,535）限定「已发未确认」的 QoS>0 PUBLISH 数量；配额随每个 PUBACK/PUBCOMP 回 +1，**不跨连接保留**。这是 QoS1/2 压测时必须控制的变量——[[开环负载与令牌桶（open-loop 与 token bucket）]] 的实验设计里它就是那个「窗口」。

### 4.9 增强认证与错误处理（p.106–110）

增强认证（AUTH 质询/应答，类 SASL）为 OPTIONAL；错误处理：Malformed Packet / Protocol Error 时 Server **必须**断连（[MQTT-4.13.1-1]），CONNACK/DISCONNECT 带 RC≥0x80 即预告断连。

## 五、安全章与附录（§5–7 + 附录，p.111–137）

- §5 Security（p.111–117）**整章非规范**：TLS 建议 8883 端口；受限设备可用 ChaCha20（p.112）；授权要注意校验 ClientID 使用权与限制宽 filter（p.112–113）。写论文「安全与展望」时引用即可，不需要实现（结合 [[12MQTT协议隐私改进]]）。
- §6 WebSocket（p.118）、§7 Conformance（p.119，实现合规 = 满足各自侧全部 MUST）、附录 B 是全部编号条目（[MQTT-x.y.z-n]）的索引（p.121–135）——查证某条规则时从这里反查最快。

## 六、v5.0 相对 3.1.1 的关键差异（附录 C 一览表，p.136–137）

| 特性 | 3.1.1 | 5.0 | 毕设取舍 |
|---|---|---|---|
| 属性区 Properties | 无 | 全报文可选 | 🔴 结构先留空（长度 0） |
| Reason Code | 仅 CONNACK/SUBACK 有返回码 | 全 ACK + DISCONNECT | 🟡 主干跑通后补 |
| 会话寿命 | CleanSession 二选一 | Clean Start + Session Expiry 可调 | 🟡 边缘场景刚需 |
| 流控 | 无 | Receive Maximum | 🟡 压测前实现 |
| 消息过期 | 无 | Message Expiry | 🟢 |
| 共享订阅 / Topic Alias / Request-Response | 无 | 有 | 🟢（CONNACK 声明不支持即合法） |
| DISCONNECT 方向 | 仅 C→S | 双向 | 🔴 Server 侧要能回错误 |

## 七、规范里两处自相矛盾的地方（已知坑）

1. **Retain Handling=1 的语义**：正文 §3.3.1.3（p.55）=「仅当订阅**新建**时发保留消息」；附录 B 的 [MQTT-3.3.1-10]（p.126）写成完全相反的「订阅**已存在**时发」。**以正文为准**（与 Mosquitto 等主流实现一致）。
2. **CONNECT Payload 顺序**：正文 §3.1.3（p.40）为 `ClientID → Will Properties → Will Topic → Will Payload → User Name → Password`；附录 B 的 [MQTT-3.1.3-1]（p.123）漏写 Will Properties。**以正文为准**。

## 八、哪些部分可以等（三档分类）★

> 判断标准：🔴 = 与标准客户端互通的 MUST 主体；🟡 = 规范要求 MUST 但不影响互通，主干跑通后补；🟢 = OPTIONAL / 非规范 / 纯优化，可跳过。括号内为 [[毕设完成流程书]] 对应周次。

### 🔴 必须先做（W8–W12）

- VBI 编解码 + 报文编解码全套（§1.5、§2）：地基，所有报文都过它。
- CONNECT/CONNACK 全部校验 + Session Present + 挤掉旧连接（§3.1–3.2）。
- PUBLISH QoS0/1/2 + PUBACK + 四步握手与去重（§3.3、§4.3）。
- SUBSCRIBE/UNSUBSCRIBE + 主题匹配引擎（`+`/`#`/`$` 规则，§4.7）。
- 保留消息 + 会话状态清单（§3.3.1.3、§4.1）+ Keep Alive 1.5× 断开（§3.1.2）。
- QoS0 不得带 PID、flags 固定值校验、非法即断连（§2.1.3）。

### 🟡 要做但可后置（W12–W16，中期前收口）

- Session Expiry、Receive Maximum（流控）、Maximum Packet Size 属性子集（§2.4、§4.9）。
- Reason Code 矩阵补全（先只发 0x81/0x82/0x87 也能活）。
- No Local / Retain As Published / Retain Handling 三值（§3.8.3，桥接实验用得到）。
- 重连后原 PID 重发（§4.4）——流程书 W13 断线重连周实现。
- Server Keep Alive、Assigned Client Identifier。

### 🟢 可以等（基本=论文写作引用即可，不实现）

- AUTH 增强认证 / 重认证（§4.12，规范明标 OPTIONAL）。
- 共享订阅 `$share/`（§4.8.2）：CONNACK 声明不支持即合规。
- Topic Alias（§3.3.2.3）：Topic Alias Maximum 缺省 0 = 禁用，合法。
- Request/Response（§4.10）、Server redirection（§4.11）。
- WebSocket 传输（§6）、§5 安全章实现、256MB 大报文完整支持（上限调到 256KB–1MB 合理）。

## 与其他论文的关系

- [[R2MQTT3.1.1规范精读]]：先按 3.1.1 打底实现（语义最简），再叠加本篇的 🟡 特性；两篇笔记的第八节合起来就是完整实现路线。
- [[4QoS级别与MQTT丢包时延相关性]]：本规范定义 QoS 语义，该论文实测三种 QoS 的时延/丢包代价——实现章引规范、实验章引实测。
- [[5muMQ轻量可扩展MQTT代理]] 与 [[6分布式IoT边缘MQTT代理对比]]：标准客户端互操作就是按本规范判分的；muMQ 的线程模型可对照 §4.8 流控设计。
- [[11MQTT可靠性实测压力测试]]：其可靠性指标（完成率/重连时延）的口径要落在 §4.3/4.4 的协议行为上。
- [[9跨组织MQTT桥接架构评估]] 与 [[MQTT 桥接（MQTT Bridge）]]：桥接语义在规范里只有订阅选项（No Local/RAP），具体桥接拓扑是论文 9 的主题。

## 对毕设的帮助

- **①写论文**：第 2 章「系统设计」引用 §2 报文结构与 §4.3 QoS 流程（报文格式表可直接改画）；「相关工作」用第六节差异表论证「为何基于 5.0 子集实现」；测试章用 Reason Code 解释异常路径结果；两处规范矛盾（第七节）可作为「实现中发现的规范歧义」写入实现细节，答辩加分。
- **②动手实现**：Session 结构体字段照抄 §4.1 清单；编解码实现顺序 = VBI → Fixed Header → 各报文；1.5×Keep Alive、`min(QoS)` 降级、重叠订阅取最大 QoS、PID 复用时机都是可直接照抄的 MUST；QoS2 去重前提（[MQTT-4.3.3-10]）是状态机设计核心。
- **③测试**：互操作测试 = 用 mosquitto_pub/sub（-V 5）当对端；非法报文用例直接来自 MUST 违反项（flags 错误、QoS=3、空 SUBSCRIBE payload、QoS0 带 PID）；抓包验证点 = CONNACK Session Present、QoS2 四步、RL=2 短确认。

## 怎么用 & 怎么做（研0 版落地清单）

> 配套：[[R2MQTT3.1.1规范精读]] · 流程书：[[毕设完成流程书]] · 概念：[[概念索引]]

- **什么时候翻这篇**：流程书 W2 通读第二/三/四节建立框架；W8–W16 写代码期间当字典逐节精查；中期报告与答辩前用第八节核对「哪些做了、哪些合法跳过」。
- **在 Ubuntu 22.04 上**：`mosquitto_sub -V 5 -t '#' -d` 观察 v5 报文与属性；Wireshark 过滤 `tcp.port==1883` 对照 §3 核对字段；`mosquitto_pub -V mqtt5 -D connect session-expiry-interval 60 ...` 试验会话过期；用 python 手写 VBI 编解码器做交叉验证。
- **在树莓派上**：装 `mosquitto-clients` 做弱网对端；拔网线重连验证 §4.4 重发规则（原 PID 重发 + DUP=1）；`tc netem` 丢包下观察 QoS1 重发与 1.5×Keep Alive 断连。
- **C++ 实现要点**：先写 `encode_vbi()/decode_vbi()` + 4 字节上限单测；报文解析按「byte1 类型/flags 校验 → Remaining Length → 变长头 → Payload」分层，任何 MUST 违反直接回 0x81/0x82 并断连；Session 结构体按 §4.1 七项清单建字段；QoS2 用「PID → {PUBLISHED, PUBRECVD, PUBREL_SENT}」状态枚举实现去重；网络层单线程 [[epoll（IO 多路复用）]] 事件循环 + 每 connection 读缓冲切帧。
