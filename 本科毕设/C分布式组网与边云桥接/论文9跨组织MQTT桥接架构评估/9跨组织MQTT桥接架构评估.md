
- **标题**：Evaluation of MQTT Bridge Architectures in a Cross-Organizational Context（跨组织情境下 MQTT 桥接架构的评估）
- **作者**：Keila Lima、Tosin Daniel Oyetoyan、Rogardt Heldal（西挪威应用科学大学）；Wilhelm Hasselbring（德国基尔大学）
- **期刊/会议**：2025 IEEE 22nd International Conference on Software Architecture (ICSA)，DOI: 10.1109/ICSA65012.2025.00032
- **发表时间**：2025 年

> 页码说明：PDF 物理页码 p.1–12 与论文自身页码一致（IEEE 会议论文无独立印刷页码）；p.11–12 为参考文献，正文实际到 p.10 结束。**本篇 PDF 图源目录为空（figs/9/ 无提取图），全部插图以下均用文字描述并注明未提取**。

## 一、preview/abstract（p.1）
### 痛点 / 已有方法为什么不行
- IoT 设备持续增长（2023 年报告：同比 +18%，到 2025 年预计超过 **160 亿台**），大量设备把"传感器数据即服务"卖给其他组织，跨组织数据接口带来**互操作性问题**（p.1）。
- 最简单的 [[MQTT（消息队列遥测传输）]] 架构——传感器与消费系统挂在**同一个 [[Broker（消息代理）]]**（broker：所有设备共用的消息中转站，像小区统一的快递柜，收发全靠它）——**不适用于真实场景**：生产者与消费者往往被地理与网络隔开，海量数据必须经通信链路传到数据平台（p.1）。
- 常见桥接实现在 **broker 侧**（如 Eclipse Mosquitto bridge，broker 自带的转发通道），但它只在**无管理壁垒、无需数据转换、MQTT 方案同构**时可行；真实跨组织场景中数据由不同 provider 用**不同 MQTT 方案、异构格式**发布，必须先做数据转换再转发（p.1）。机制全貌见 [[MQTT 桥接（MQTT Bridge）]]。
- **broker 侧 vs client 侧桥接（生活类比）**：broker 侧桥接像"让 A 公司的邮局兼任翻译，并直接把件转投 B 公司邮局"——要求 A、B 两家邮局（broker）联手改造内部流程，还得格式兼容；client 侧桥接是在 A 的数据出口处放一个自己的"翻译+中转"组件，它以普通客户端身份从 A 的 broker 订阅、转换后发布到 B 的 broker——两家邮局都不用动。跨组织时 A 管不到 B 的 broker，所以**只有 client 侧做得到**（p.1, p.3）。
- **跨组织**（cross-organizational：数据的产生方和消费方分属不同机构，互相管不着对方的服务器，详见 [[跨组织情境（Cross-Organizational Context）]]）数据流合并还要面对**管理壁垒与信任边界**（administrative barriers：一方无权改造另一方的系统；trust boundaries：跨界数据默认不被信任，要加密与鉴权，像两家公司之间走合同与防火墙而不是内部流程）（p.1）。

### 新方法（一段话）
针对文献 [17]（同一作者团队 2024 ICSA 论文）提出的 **client-side 桥接架构**（在 broker 的客户端侧部署带数据转换功能的 bridge 组件），本文用 benchmark 方法评估其**两种部署变体**的端到端时延与可靠性，并把 **topic 名长度、payload（载荷：一条消息里真正的数据正文，不含信封/头部）大小**作为新增 benchmark 参数。对象是一个真实海洋环境监测 IoT 平台的原型。**核心发现：bridge 组件数量、MQTT 包大小、topic 名都会影响质量属性**（p.1）。

## 二、introduction（p.1–2）
1. 桥接架构的存在理由：把数据从生产者 broker 推送到**另一个网络**的消费者 broker（p.1–2）。实践中的用例（p.2）：
    1. **聚合 publisher 按 [[Topic（主题）]]（topic：消息的"频道名/收件地址"，发布者按频道发、订阅者按频道收）发布的消息**，减少 publisher broker → subscriber broker 之间的流量 [27]；
    2. 中间层做**流式数据质量分析**（语义校验、位置关联观测）；
    3. 跨域共享前的**数据过滤与预处理**（如匿名化）。
2. 度量口径（p.2）：**可靠性 = 丢失消息数；时延 = 端到端延迟（ms）**——发布方发出到订阅方收到的时间差。
3. 本文贡献两条（p.2）：
    1. 给出真实可用、但**吞吐不高、存在时延与可靠性隐患**的 MQTT bridge 架构 benchmark 结果，供实践者设计前参考；
    2. 证明 **data size 与 topic name 应纳入 MQTT 系统的 benchmark 参数集**——它们对时延和可靠性有实际影响。

**桥接拓扑图示（Fig.1, p.2，未提取）**：(a) 标准 MQTT 部署：多个 Sensor → 单个 MQTT Broker（单实例/集群）→ Topic A → Data Consumer System；(b) 桥接部署：Operational Environment 1 的 Sensor → MQTT Broker，bridge 组件订阅 Topic A、转换后发布到 Operational Environment 2 的接收 broker 的 Topic B，Data Consumer 在接收侧订阅——**两个 broker 分属两个运行环境，中间就是桥接链路**。

**图解**（Fig.1, p.2，图未提取，按论文原文文字重建）：图分左右两半。(a) 半张画"一个邮局"模式：多个 Sensor（传感器）的箭头汇聚到一个 MQTT Broker 方框，经 Topic A 送达 Data Consumer System（数据消费系统）——发布与订阅都在同一个 broker 上，消息不出本组织。(b) 半张画"两个邮局+中转站"模式：Operational Environment 1（运行环境 1）里的 Sensor 把数据发给自己环境内的 MQTT Broker，一个 bridge 组件方框挂在订阅侧，把 Topic A 的数据转换后发到 Operational Environment 2 的接收 broker 的 Topic B，消费系统在环境 2 订阅——两个方框群分属两个运行环境，中间那条 bridge 箭头就是全文要测的桥接链路。**读图结论**：桥不是第三个 broker，而是挂在 broker 客户端一侧的转换组件；消息跨组织要"进一次 broker → 出来转换 → 再进另一个 broker"，比单 broker 多走一整段网络。**与毕设的关系**：毕设任务 2/5 的端—边—云架构图可直接套用 (b) 的画法——边缘环境一个 broker、云端一个 broker、中间标出 bridge 与信任边界。

## 三、MQTT 在 IoT 架构中的位置与三种 broker 部署（p.2–3）
1. **五层 IoT 架构**（p.2）：perception（感知/执行）→ network（把数据从感知层送到云侧处理层）→ processing（聚合、分析、存储）→ application（领域应用）→ business（整体管理与商业模式）。MQTT 常用于 network 层：**头部仅 2 字节、内嵌 [[QoS（服务质量）]]（Quality of Service，消息的"快递保价等级"：0=发完就不管、1=至少送到一次、2=恰好送到一次）、有序交付、复杂度低**（p.2）；相对比较研究中 MQTT 在时延与可靠性综合表现最佳 [22]（p.2）。
2. **三种 broker 部署选项**（p.3）——本文的架构坐标系：
    1. **单 broker**：包办所有连接、topic 管理、授权与消息流量；在 [[发布订阅模式]]（publish/subscribe：发布者和订阅者不直接对话，都只跟 broker 打交道，像电台按频率广播、收音机按频率收听，双方互不认识）中因资源、队列大小、持久化存储上限而**天然是瓶颈**（p.3）；
    2. **broker 集群**：复制单实例并加同步链路，吞吐与并发连接容量更高，代价是 **inter-broker 通信带来时延开销**（p.3）；
    3. **bridge（桥）**：在 broker 之间转发消息，把一个环境/系统段落的生产与另一段**解耦**（p.3）。
3. **MQTT Bridge 机制**（p.3；机制全貌与两侧对比见 [[MQTT 桥接（MQTT Bridge）]]）：
    - **含义**：至少两个 broker 之间有数据流；源 broker 某 topic 上发布的数据，在接收 broker 的对应 topic 上对订阅者可用。
    - **为什么需要 MQTT 5.0 的两个标志**（p.3）：标准（2019 年发布）在非规范性注释中给出实现桥接的订阅选项——**No Local**（不把消息回发给自己的发布客户端，**防止桥接回环**——否则消息会在桥上像回声一样打转）与 **Retain As Published**（把原消息的 retained 标志，即 [[保留消息（Retained Message）]] 的"留最后一条"标记，原样带到接收侧）；两个 flag 的完整说明见 [[No Local 与 Retain As Published]]。毕设实现桥接时这两个 flag 是直接可用的抓手。
    - 文献中的三类动因（p.3）：异构传感器数据流处理（跨组织，发布侧组件不可访问）；卫星受限链路优化（发送侧预处理，同一组织）；客户端地理分离（同一组织）。**本研究聚焦 edge–cloud 链路 + 数据格式转换，桥接实现在 client 侧**（p.3）。
4. **MQTT 的安全现状**（p.3）：规范内安全特性偏少——认证（用户名/密码或增强方式，后者增加消息交换）、ACL 授权（如 Mosquitto dynamic security）、TLS/SSL 信道加密；载荷加密只是**非规范性建议**， enforcement 依赖具体实现（p.3）。

## 四、benchmark 方法与两种桥接部署选项（p.3–7）
### 质量属性与 RQ（p.3–4）
- 被测系统的三个特征（p.3）：gateway（网关：边缘侧负责把传感器数据汇拢上传的设备）作为**边缘数据 sink**（汇：所有数据流的汇聚出口）聚合传感器数据；实时系统要求数据**即到即用**（低时延）；边缘 gateway → 云系统无线传输的**可靠性**。
- **Latency vs Reliability 是内生冲突**：MQTT 的 QoS 1/2 需要额外消息交换，可靠换时延（p.3–4）。
- **RQ1**：桥接组件的部署架构如何影响跨组织数据交付的时延与可靠性（p.4）。
- **RQ2**：topic 名与 payload 大小如何影响时延与可靠性——它们占据 MQTT 包体积的大头（p.4）。

### 被测架构（AUT）与数据流（Fig.2, p.4，未提取）
**benchmark 数据流（文字重建，p.4）**：Data Provider（外部传感器系统，其 gateway = MQTT publisher client）→ **Source Broker**（每个 sensor data provider 一个实例）→ **Transformer（= bridge，client 侧组件）**：合并异构格式、统一数据模型，**转换后数据体积反而变小** → **Destination Broker**（分发给应用）→ **Data Consumer**（MQTT subscriber，应用层实时数据入口）。排除组件：Forwarder（REST 转发）、Data Warehouse（历史存储）。Monitoring Agent → Prometheus（时序指标抓取与存储的监控组件）+ Grafana（监控图表面板）。broker 用 **HiveMQ community edition**（HiveMQ 的开源社区版）（p.4–5）。

**图解**（Fig.2, p.4，图未提取，按论文原文文字重建）：图是一条从左到右的消息管道，组件画成方框、箭头即消息流向：Data Provider（外部传感器系统，其 gateway 充当 MQTT 发布端）→ Source Broker（源 broker，每个数据提供方一个实例）→ Transformer 方框——注意它画在 broker 的"客户端"位置而非 broker 内部，这就是 client 侧桥接——在此合并异构格式、统一数据模型（转换后体积反而变小）→ Destination Broker（目的 broker）→ Data Consumer（订阅端，应用的实时数据入口）。另有被排除的组件（Forwarder、Data Warehouse）与监控支线（Monitoring Agent → Prometheus + Grafana）。**读图结论**：数据转换被安排在两个 broker 之间的客户端位置，形成"边侧采集 → 桥上翻译 → 云侧分发"的管道。**与毕设的关系**：这就是毕设任务 2/5 "边缘 gateway 聚合 → broker → 桥接转换 → 云 broker → 应用订阅"的直接参考数据流。

### 两种部署选项——本文的"桥接拓扑组合"核心（Fig.3, p.6，未提取；Table II, p.6）
- **AUT 1：每个 sensor data provider 部署一个 bridge 组件**（共 **2 个**）。依据：每个 provider 只有一种数据格式，一个 bridge 可转换其全部 sensor hub 的数据（hub：provider 下属的一路传感器数据流/采集单元）；用**通配符订阅**（wildcard subscription：用 `#`、`+` 这类"万能匹配符"一次订阅一批 topic，详见 [[通配符订阅（Wildcard Subscription）]]）按 topic 名结构捕获该 provider 所有 hub 的数据（**topic 15 字节**），好处是 hub 侧增删变化无需改 bridge 配置（p.5–6）。对照配置：不用通配符、逐个列出 hub topic 清单（**29 字节**），用于 RQ2 的 topic 大小对比（p.6）。
- **AUT 2：每个 sensor hub 数据流一个 bridge 组件**（共 **4 个**，topic 29 字节）——**生产系统的实际用法，作为基线**；hub 流与 bridge 实例一对一映射（p.5–6）。
- **结构化取舍（p.6）**：AUT 2 每实例处理量小但**网络链路多**（4 条桥接链）；AUT 1 每实例处理量大但链路少（2 条）。**这就是"桥接拓扑组合"的两个自由度：桥接实例的粒度（按 provider 聚合 vs 按流拆分）与链路数量**。
- 客户端行为仿真（p.5）：**keep alive 60 s**（keep alive：心跳间隔，超时没收到心跳就判定掉线）；每次连接用 **CLEAN START**（MQTT 5.0 的"从零开始"选项：每次连接都新建会话、不带旧状态），保证 10 轮重复之间无会话持久化；publisher 模拟真实移动/卫星链路行为——**每成功发一条就断开、下一条再重连**；subscriber 与接收 broker 同域同网，整轮保持连接。
- 资源限额（p.5）：option 1 每组件 512 MB 内存 + 半个 CPU 核；option 2 把**同等总量**均分给 4 个组件——**总资源公平对比**。
- 主机布局（Table I, p.5）：host 2（公有云，8 vCPU@2.9 GHz、16 GB、50 Gb/s）跑 2 个 source broker + 1 个接收 broker；host 1（本地机房，8 vCPU@2.5 GHz、2 GB、1 Gb/s）跑 3 个 gateway publisher + 1 个 subscriber。**收发两端 client 放同一主机以保证时钟同步、端到端时延测量有效**（p.5, p.10）。
- 时延与可靠性度量（p.5）：发布时随消息附 user property 时间戳，订阅端记录接收时间、到达时间、topic、序号与 ID；**ID 用于统计 QoS 1 的重复消息数**。
- 负载模型（p.7, Table III）：现有工具不支持 per-publisher 自定义 payload、也不适合测桥接时延，因此**自研 load driver**；**fan-in 模型**（fan-in：多路汇入一路，像多条小溪汇进同一个水库）——多 publisher 汇入单 subscriber；真实传感器数据：provider 1 两个 hub 的 payload 分别 **125 KB / 35 KB**，provider 2 每 hub **1.5 KB**；每 hub payload 每轮发布 **1000 次**、每秒一批顺序发送；每配置 **4000 条消息 × 10 轮重复**；摄取速率 1 msg/s（provider 1 每 gateway）与 2 msg/s（provider 2）。
- 信任边界（p.7）：借 OWASP threat modeling（一种安全威胁建模的记号法）标注跨组织边界；**client–broker 链路启用 TLS/SSL 加密**（TLS：给网络链路套一层加密通道，像寄信走保险箱专线，防窃听但要花时间）；broker 侧用 **LDAP**（企业目录服务的认证授权协议，可理解为统一门禁系统）做认证授权（gateway、bridge、subscriber 按配置访问 topic）——即本实验测的是"带加密开销的真实跨组织链路"。

**图解**（Fig.3, p.6，图未提取，按正文与 Table II 重建）：图并排画两种桥接架构。AUT 1：2 个 Data Provider 各接自己的 Source Broker，每个 provider 后只跟 **1 个 Transformer 方框**（共 2 个 bridge），方框用通配符把该 provider 全部 hub 数据流收进来、转换后发往同一个 Destination Broker——共 2 条桥接链。AUT 2：4 路 sensor hub 数据流各自单独配 **1 个 Transformer**（共 4 个 bridge），4 条细链并行汇入 Destination Broker。**怎么看**：数 Transformer 方框数与指向 Destination Broker 的箭头条数即可——AUT 2 框多、线多但每条线负载小；AUT 1 框少、线少但每条线聚合负载大；两侧总资源相同（各 512 MB + 半核 vs 均分 4 份）。**读图结论**：这就是"按数据源聚合 vs 按流拆分"的桥接粒度二选一。**与毕设的关系**：毕设组网在"每边缘节点一个桥"与"每数据流一个桥"之间做选择时，Fig.3 就是两种画法的模板。

## 五、结果：延迟与可靠性（p.7–9）
### 总表（Table IV, p.8，10 轮均值）
| 配置 | QoS 0 | QoS 1 | QoS 2 |
|---|---|---|---|
| AUT 1，15 B topic（ms） | 132.3 | 185.3 | 216.9 |
| AUT 1，29 B topic（ms） | 132.9 | 186.7 | 217.7 |
| AUT 2，29 B topic（ms） | 135.6 | 191.2 | 221.6 |

- **QoS 越高延迟越高**（0→1→2 递增约 50/30 ms），与 MQTT 可靠性设计一致——更高 QoS 用更多消息交换换恢复能力（p.7–8）。
- **QoS 1/2 端到端零丢失**；QoS 0 端到端 4000 条只收到约 2004 条——丢失全部集中在 provider 1 的中大型 payload 流（p.8）。
- 分 payload 的 QoS 0 平均丢失（每流 1000 条，Fig.7–9, p.9）：**125 KB：997.7 / 997.8 / 997.3**（AUT1-15B / AUT1-29B / AUT2）；**35 KB：997.0 / 998.6 / 997.4**；**1.5 KB：仅 1.1 / 1.2 / 0.6**。**中大型 payload 在 QoS 0 下几乎全灭**——尽管 35/125 KB 远小于 MQTT 256 MB 的包上限（p.9）。

**图解**（Fig.7–9, p.9，图未提取）：三张柱状图按 payload 三档（125 KB / 35 KB / 1.5 KB）各一张，横轴为三种被测架构（AUT1-15B / AUT1-29B / AUT2），纵轴为每流 1000 条中 QoS 0 丢失的条数。中大盘子里柱子几乎顶格（≈997–999 条），1.5 KB 盘子里柱子矮到近 0（0.6–1.2 条）——一眼看出 payload 大小才是 QoS 0 丢失的决定变量，桥接架构选型的影响反而次要。**与毕设的关系**：毕设测 QoS 0 时照此按 payload 分档画丢失对比图，能直接支撑"中大包禁用 QoS 0"的结论。
- 丢失位置（p.9）：source broker 与 destination broker 部署在同一主机，测得的丢失**主要发生在 gateway → source broker 的摄取链路**；bridge → subscriber 段平均只丢约 1 条。真实系统中若两个被桥接的 broker 跨网，丢失可能更多（p.9）。

### RQ1 答案：桥接部署架构的影响（p.8）
- **更多 bridge 处理器 → 更高端到端延迟**：AUT 2（4 实例 4 链路）比 AUT 1（2 实例 2 链路）平均慢约 3–5 ms；AUT 1 内部 15 B 与 29 B topic 差异 ≤ **1.4 ms**（p.8）。
- 可靠性：中大型 payload 下两种架构丢失接近、无差异；**小 payload（1.5 KB）时 AUT 2 丢失几乎减半**（0.6 vs 1.1/1.2）（p.8）。
- **推断：[[传输成本大于处理成本]] → 建议桥接架构尽量少用 bridge 处理器**（p.8）。为什么：CPU 上"算一下"（合并、转换格式）只要微秒到毫秒级、几乎不出错；数据在网络上"多跑一趟"要过物理链路、加密、排队、重传，每一环都可能延迟和丢包。实测证据：AUT 2 把桥拆成 4 实例 4 链路，延迟平均比 AUT 1 慢 3–5 ms——bridge 实例翻倍本身几乎不耗时间，多出来的开销全在链路传输上。

### RQ2 答案：topic 名与 payload 大小的影响（p.8–9）
- **topic 15 B 一致地略快于 29 B**（同 AUT 内全 payload 档），但作者强调要下结论需更多不同 topic 名/长度的实验（p.9）。
- payload 大小是 QoS 0 可靠性的**决定性变量**（p.9），与 Roy et al. [7] 报告的 payload–丢包相关性一致。
- **给实践的建议（p.9，加粗）**：**QoS 1 在所有 payload/topic 档位下可靠性都好；若要求较低延迟且能实现重复消息检测，选 QoS 1**。**QoS 0 + 中大型 payload（本文 35/125 KB）应避免**。**QoS 0 仅适合小 payload（如 1.5 KB）+ 带宽受限 + 可容忍少量丢失的场景**。
- 给研究的建议（p.9）：MQTT 实现应在 1 byte–256 MB 全 payload 范围内做实验；考虑网络 locality（跨网部署）；用丢包注入等模拟恶劣网络。

## 六、效度威胁与相关工作（p.10）
1. **construct validity**：收发端 client 同主机保证时钟同步；client 与 broker 分机分网——否则 QoS 0 的丢失测量没有意义（p.10）。10 轮重复 + 专用资源限额抑制云环境方差；HiveMQ 的 Prometheus 指标与订阅端记录交叉验证（p.10）。
2. **泛化边界（p.10）**：只测了 3 个 payload 档、2 个 topic 名、2 种部署、1 个 subscriber；**结论不能外推到集群部署等配置**。
3. **相关工作定位（p.10）**：既有 MQTT benchmark 多测孤立 broker 平台的时延/可扩展性（broker 节点数、client 数、QoS）；本文测**完整摄取管道上下文中的桥接架构**，并首次引入 **topic 大小**参数、使用 **KB 级真实传感器数据**（先前研究 payload 多 < 100 字节，因为直接来自传感器而没有 gateway 聚合）；未测集群，因为被测系统关注时延与可靠性而非高吞吐（p.10）。

## 七、结论与未来工作（p.10）
- **小 payload 在 QoS 0 下可可靠传输；中大型 payload 在 QoS 0 下高丢失；QoS 1/2 对所有 payload 都存在可靠性–时延冲突**（p.10）。
- **桥接处理器越多延迟越高；处理器更少、链路更少 → 平均延迟更低**（p.10）——AUT 1（每 provider 一个 bridge）在小/大 payload 档延迟更优。
- 未来工作：数据 provider 侧架构（尤其 gateway 部署选项）；不同 payload 尺寸下的能耗维度（p.10）。

## 与其他论文的关系
- 区块内与 [[8网络边缘分布式MQTT代理消息分发]] 构成任务 5（组网与桥接）的两条互补路线：论文 8 把消息分发**分布化**（broker 放置与协作），本文把消息在**组织边界间桥接**并叠加 client 侧数据转换；两者的共同对手都是"单 broker 瓶颈"（本文 p.3 的三种部署选项可直接用于组织论文 8 的架构对比）。
- 跨区块：benchmark 设计（参数矩阵、重复次数、时钟同步、Prometheus 交叉验证）与 [[7IoT边缘消息代理基准测试]] 同属一类方法学，可互相校对指标口径；QoS 0 的 payload–丢包规律与 [[11MQTT可靠性实测压力测试]]、[[4QoS级别与MQTT丢包时延相关性]] 互为印证——本文的独特贡献是把该规律放到**跨网 + TLS + 桥接管道**的真实条件下复验。
- 与 [[10区块链增强MQTT容错]] 的关系是"桥接链路的可用性"问题：本文测得桥接链路在 QoS 1/2 下可靠，但**未测 broker 本身失效**——论文 10 的 BNS 负载均衡恰好补这个洞。

## 对毕设的帮助

**写论文**
1. 对应任务 2（总体架构）：论文的管道形态可直接采纳——**边缘 gateway 作 sink 聚合 → source broker → bridge（client 侧 transformer）→ destination broker → 应用订阅**；异构格式转换放在 bridge 组件里而不是 broker 里，可引用其论断"broker-side 桥接（Mosquitto bridge）只在同构、无管理壁垒时可行"（p.1）。架构图按 Fig.1/Fig.3 的画法：画出**跨组织/信任边界**（OWASP 记号）与两个运行环境，把 bridge 组件明确标在 client 侧。
2. 可引用的结论数字（跨网 + TLS 条件，Table IV, p.8）：QoS 0 ≈ 132 ms、QoS 1 ≈ 185 ms、QoS 2 ≈ 217 ms；QoS 0 下 125 KB 流每千条丢约 997 条、1.5 KB 流仅丢约 1 条（p.8–9）——用于论证 QoS 选型与 payload 约束。"传输成本 > 处理成本"（p.8）可作桥接拓扑选型的论证句式，配 AUT 1 vs AUT 2 的 3–5 ms 差值。

**动手实现**
1. 对应任务 5（桥接与组网）：桥接粒度二选一有实测依据——**按数据源聚合（少实例少链路）延迟更低，按流拆分小 payload 时更可靠**；传输成本大于处理成本，**默认取少 bridge 实例的拓扑**；实现桥接用 MQTT 5.0 的 **No Local 防回环 + Retain As Published**，订阅侧用通配符按 provider 聚合 topic，方便后续增删边缘节点。
2. 对应任务 3/4（QoS 与可靠性）：**QoS 1 作为默认档**（全 payload 可靠），前提是实现重复消息去重（利用消息 ID）；**中大型 payload（>~1.5 KB 量级）禁止 QoS 0**；QoS 0 只留给小包高频、可容忍丢失的遥测流。

**测试**
1. 对应任务 6（测试设计）：可直接复用的 benchmark 规范——payload 分小/中/大三档、**topic 名长度作为显式参数**、每配置重复 10 次、收发端同主机测时延（时钟同步）、CLEAN START 隔离轮次、publisher 模拟"发一条断一次"的真实链路行为、Prometheus broker 指标与应用侧日志交叉验证、原始数据进 replication package。
2. 测试报告按"配置 × QoS"矩阵给均值表（对标 Table IV, p.8）；本文的延迟量级（跨网 + TLS）可作为毕设多节点组网测试的对照基线。

## 怎么用 & 怎么做（研0 版落地清单）

> 思维导图：[[9思维导图.canvas]] · 总览：[[毕设论文总导图.canvas]]

**什么时候翻这篇**：任务 5 实现边云桥接前（数据流与粒度二选一的模板）；桥接测试设计时（10 轮重复、时钟同步等规范）；写 QoS 选型结论时（跨网+TLS 实测数字）。

**在 Ubuntu 22.04 上**：
- 模拟跨组织边界：两台机器（或两个 docker network）各跑一个 broker，中间架桥接组件；client–broker 链路启用 TLS（Mosquitto 配 CA/证书，自研用 OpenSSL）——对应本文「带加密开销的真实跨组织链路」（p.7）。
- 测试规程照抄（p.5–7）：每配置 4000 条 × 10 轮、CLEAN START 隔离轮次、publisher「发一条断一次」模拟移动链路、发布时带 user property 时间戳、收发端同主机保证时钟同步。
- 对照矩阵按本文设置：payload 三档（约 1.5 KB / 35 KB / 125 KB）× QoS 0/1/2 × 桥接粒度（少桥少链 vs 多桥多链），复刻 Table IV 的配置 × QoS 均值表。

**在树莓派上**：
- 树莓派网关直接扮演本文的 client 侧 bridge 角色：订阅边缘 broker 的 `sensor/#` → 格式归一 → 发布云 broker 对应 topic——这就是任务 5「边—云桥接」的落地形态，两侧 broker 零改动。

**C++ 实现要点**：
- bridge 进程骨架：libmosquitto 或自研客户端，通配符订阅（`sensor/#`）+ 回调里转换 + 异步再发布；MQTT 5.0 订阅选项带 **No Local（防回环）** 与 **Retain As Published**（p.3）。
- 粒度选择有实测依据（p.8）：传输成本大于处理成本——默认按数据源聚合（少桥少链），只有小 payload 且要求更稳时才按流拆桥。
- 中大 payload（>1.5 KB 量级）禁用 QoS 0；QoS 1 作默认档并按消息 ID 去重（p.9）。
