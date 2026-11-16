
- **标题**：Benchmarking Message Brokers for IoT Edge Computing: A Comprehensive Performance Study（面向 IoT 边缘计算的消息代理基准测试：一项系统性性能研究）
- **作者**：Tapajit Chandra Paul、Pawissanutt Lertpongrujikorn、Mohsen Amini Salehi（均属 University of North Texas, High Performance Cloud Computing (HPCC) Lab）；Hai Duc Nguyen（Argonne National Laboratory & University of Chicago）——作者与单位从 p.1 脚注确认
- **期刊/会议**：arXiv 预印本 **arXiv:2603.21600v1 [cs.DC]**（p.1 边栏编号确认）；致谢中出现「感谢匿名审稿人」，说明处于投稿流程，正式发表 venue **未确认**
- **发表时间**：2026 年 3 月 23 日（arXiv v1 提交日期）

> 页码说明：本笔记统一用 p.N = PDF 物理页码（全文 10 页，p.1–p.10），与 arXiv 页码一致。

## 一、abstract + introduction（p.1–2）
### 痛点 / 已有方法为什么不行
- **选型难**：MQ（Message Queue，消息队列：程序之间异步传递消息的基础设施总称，像一套「程序专用邮政系统」）生态从高吞吐流平台（Kafka——大数据领域最主流的分布式消息流平台，偏重吞吐与持久化）到面向边缘/IoT（物联网：带联网能力的传感器/设备组成的网络）的轻量协议（[[MQTT（消息队列遥测传输）]]——IoT 领域最流行的轻量级发布/订阅协议，专为低带宽、不稳定网络设计；NATS——极简文本协议的高性能消息系统；Redis Pub/Sub——内存数据库 Redis 自带的发布/订阅功能；Zenoh——面向 IoT 的「以数据为中心」新一代通信中间件）跨度极大，各系统在架构、协议语义、运行时（单线程事件循环 vs 多线程 actor、C 实现 vs JVM——分别见 [[事件循环（event loop）]]、[[native 实现与托管运行时（native vs managed runtime）]]：事件循环 = 一个线程内「等事件 → 处理事件」地串行干活；native = C/Rust/Go 等编译成机器码的直接实现，托管运行时 = Java/Erlang 等跑在虚拟机里的实现，虚拟机代管内存与线程、省心但开销大）上的权衡导致**实践中性能与资源画像差异悬殊**（p.1）。
- **已有评测的三个盲区（p.1）**：① 多局限在单一协议族（如只测 MQTT）或少数系统，**不同 [[Broker（消息代理）]]（broker：居中转发消息的服务器程序，像快递驿站收件分发）设计没法在可比条件下对照**；② 只强调固定硬件上的吞吐（[[吞吐（throughput）]]：每秒成功送达的消息条数，像高速路口每秒放行的车流量）与时延（[[端到端时延]]：一条消息从发布方发出、到订阅方收到的全程耗时，像快递从下单到签收的总时长），**忽视 CPU/内存占用及资源配额变化的影响**——而这恰是边缘/IoT 部署的关键维度；③ 云环境表现好的 broker 换到资源受限边缘硬件未必一样（p.1）。

### 新方法（一段话）
提出 **mq-bench**：一个 Rust 写的统一基准测试框架（[[基准测试（benchmark）]]：用固定且可复现的负载去考核一套系统、量化其成绩——像标准化考试，考题、时长、评分标准统一，不同「考生」（broker）的分数才有可比性），对异构 MQ 系统施加**一致的 pub/sub 负载**（pub/sub 见 [[发布订阅模式]]：发布者按「主题」发消息、订阅者按主题收消息，双方互不知晓对方存在），以标准化格式记录吞吐、时延分布与资源消耗（p.1–2）。用它在相同硬件/负载下横评 **8 个 broker：Mosquitto、EMQX、HiveMQ、RabbitMQ、ActiveMQ Artemis、NATS Server、Redis (Pub/Sub)、Zenoh Router**；实验从 500 扩到 **10,000 并发 pub-sub 对**，并给 broker 配 1–4 vCPU、2–8 GB RAM 三档 VM 资源（vCPU：虚拟机分到的虚拟 CPU 核；VM：虚拟机，用软件模拟出的隔离电脑；从 Raspberry Pi 级边缘约束到小型云实例），**同时测吞吐、p50/p95 尾时延（见 [[尾时延与分位数（p50 与 p95）]]：把每条消息耗时从小到大排队，p50 = 正中间的值——一半请求比它快；p95 = 95% 位置的值——只有 5% 比它慢。均值会被极端值稀释，分位数才能同时看清「典型体验」与「最坏一批有多糟」；尾时延 tail latency 指最慢那一小撮请求的耗时，用户感到的「偶尔卡一下」来自它）、CPU/内存占用**（p.2）。

### 本文贡献（p.2）
1. **mq-bench**：开源（https://github.com/hpcclab/mq-bench）、可复现的跨协议评测工具（Rust）。
2. 受控实验方法学：最大 **10K 并发 pub-sub 对**，报吞吐 + 尾时延分位（p50/p95）+ CPU/内存，跨三档 VM。
3. 性能画像：**NATS 扩展性最好（10K 连接下 90K msg/s），Zenoh 与 RabbitMQ 次之；单线程的 Mosquitto 饱和在 45K msg/s**。
4. 资源效率分析：**Java 系 broker（HiveMQ、Artemis）内存消耗是 native 实现的 10–50 倍**。
5. 面向实践的部署指南（按负载需求 × 资源约束选 broker）。

## 二、background（p.2–3）
1. **pub/sub 模型（p.2，图1）**：publisher 发消息到命名 topic，subscriber 订阅 topic，中央 broker 路由——生产者消费者解耦、突发流量可缓冲、成员可动态加入。图1 的 IoT 场景（电表/恒温器发布 temperature、intrusion_alert，监控/能耗服务器订阅）为文字版内容（p.2；**图1 的 PDF 提取图残缺，未嵌入**）。
    - **图解（图1，未提取，据正文文字描述）**：示意图画的是 IoT 场景——左/下方的电表、恒温器等设备作为 publisher 发布 temperature（温度）、intrusion_alert（入侵告警）等 topic 的消息，中央一个 broker 节点把消息路由给右侧订阅这些 topic 的监控服务器、能耗分析服务器等 subscriber。看图要点：箭头方向 = 消息流向，topic 名标在消息旁；设备之间不直连，全部经中央 broker 中转。读图结论：**broker 是整个拓扑的单点枢纽，它的容量上限就是系统上限**。对毕设：绪论画「端—边—云消息流转图」时可参考此画法，并在 broker 节点标注容量/时延问题。
2. **评测必须覆盖的四类指标（p.2）**：throughput（持续负载下每秒送达消息数）、latency（发布到收到的时间）、scalability（客户端与消息率增长时的承受力）、**resource efficiency（相对负载的 CPU/内存消耗）**。**native 实现（C/Rust/Go）通常比托管运行时（Java/Erlang）时延与内存更低**，后者功能更全、容错更易（p.2）。
3. **协议清单（p.2–3）**：**MQTT**（三个 QoS 级别，见 [[QoS（服务质量）]]：MQTT 为投递定义的三档可靠程度；Table I：QoS 0 at-most-once 尽快但可能丢；QoS 1 at-least-once 有 ACK（接收方发回的「已收到」确认）、可能重复；QoS 2 exactly-once 四步握手、开销最高）；**AMQP 0-9-1**（RabbitMQ 的原生协议，比 MQTT 更重——exchange（交换机）按规则把消息路由进 queue（队列）等消费者取走，两级路由灵活、投递保证强、开销大）；**NATS**（简单文本协议，core 只有 at-most-once（发完即忘），主打低时延高吞吐）；**Zenoh**（数据为中心，pub/sub + 分布式存储混合，支持 brokerless P2P（不经过中央 broker 的点对点直连）或轻量 router 部署）；**RESP**（Redis 协议，内存态 pub/sub 低时延但无持久性——重启即失）。
4. **被测 broker 分类（p.3，Table II）**：
    - **MQTT 专职**：Mosquitto（C，**单线程事件循环**，面向资源受限硬件）、EMQX（Erlang/OTP——Erlang 为电信级高并发设计的语言、OTP 是其官方框架库；actor 模型：每个会话是一个独立小「演员」、带自己的信箱互不共享内存，运营商级）、HiveMQ CE（Java，非阻塞异步，企业级）；
    - **企业多协议**：RabbitMQ（Erlang，AMQP 0-9-1，路由灵活、保证强但时延高）、ActiveMQ Artemis（Java 非阻塞，多协议）；
    - **云原生/数据为中心**：NATS Server（Go，CNCF（云原生计算基金会：托管 Kubernetes 等云原生开源项目的基金会），fire-and-forget（发完即忘、不等确认）极简架构）、Zenoh Router（Rust，可 router 也可 brokerless）、Redis（C，内存 KV 的 Pub/Sub 作性能基线）。

## 三、related studies（p.3–4）
- **MQTT 专项基准（p.3）**：多数工作只测 MQTT（Mosquitto/EMQX/HiveMQ 的吞吐、时延、QoS、集群），**协议锁死在 MQTT**。
- **企业级 MQ 评测（p.3）**：另一条线比 RabbitMQ/Artemis/NATS，**完全不包含 MQTT broker**。
- **新兴协议（p.3）**：Liang et al. [18] 测过 Zenoh vs MQTT vs Kafka vs DDS；Redis Pub/Sub 学术文献仍少。
- **Gap（p.3–4，Table III）**：没有工作在**统一实验框架**里同时覆盖 MQTT broker、多协议 MQ、云原生、内存 pub/sub、数据中心件五类。本文用 mq-bench 补上——8 系统 × 5 指标（时延/吞吐/资源/扩展性/QoS）全勾。

## 四、experimental design（p.4–6）
### 评测问题（p.4）
四问：payload（负载：一条消息里实际携带的数据内容，不含协议头等开销）大小如何影响时延？各 broker 最多撑多少并发客户端？CPU/内存受限时表现如何？网络不稳定时 MQTT broker 能否维持 QoS 保证？

### 三个实验的负载设计（p.4–5）
| 实验 | 参数（Table IV/V/VI） |
|---|---|
| **Exp1 时延 vs payload**（p.4） | 10 对 pub-sub；每 publisher **10 msg/s**；payload **1 KB**（传感遥测）/ **16 KB**（IoT 聚合）/ **1 MB**（批量传输）；120 s 测试 + 60 s warmup（预热：先跑一段不计入成绩的负载，让连接、缓存进入稳定状态再正式计时）；QoS 0 |
| **Exp2 吞吐与资源**（p.4） | pub-sub 对数 **500→10,000** 爬坡；每 publisher 10 msg/s，**offered load = 对数 × 速率**（offered load：施加给 broker 的目标负载量 = 对数 × 每对速率）；payload 1 KB；120 s + 60 s warmup；QoS 0；三档 VM 重复；**另有 fanout 拓扑**（[[fanout 拓扑（广播扇出）]]：一个发布者广播、N 个订阅者各收一份，像在群里发通知） |
| **Exp3 网络故障下的 QoS 可靠性**（p.4–5） | 10 对；10 msg/s；1 KB；**180 s**；**MTTF=30 s、MTTR=5 s**（故障注入见 [[故障注入与 MTTF、MTTR（fault injection）]]：MTTF 平均无故障时间 = 平均多久故障一次；MTTR 平均恢复时间 = 平均多久恢复；用 TCP RST 注入——RST：复位包，直接探断连接的「拔网线」式断连，而非优雅断连）→ 每次测试约 5–6 次故障、总宕机 25–30 s（约 **85% uptime**——uptime：正常服务时间占比）；只测 5 个 MQTT 系 broker（NATS/Redis/Zenoh QoS 语义不同）；每个 QoS 级别测**丢包率 + 端到端时延** |

### 测量指标（p.5）
- **时延**：消息头内嵌发送时间戳（见 §mq-bench），subscriber 算端到端时延；报 **min / p50 / p95**（兼顾典型与最坏情况）。
- **吞吐**：`throughput = 收到消息数 / 时长`（msg/s）。
- **CPU**：broker 容器的 CPU 占用（占分配 vCPU 的百分比），**Docker Stats API（容器平台 Docker 的资源用量查询接口——Docker 容器是一种轻量的应用隔离/打包方式）每 1 s 采样**。
- **内存**：broker 容器 RSS（MB），同样经 Docker Stats API（RSS：进程实际占用的物理内存——注意与论文5中网卡分流技术的 RSS 重名但无关）。

### broker 部署配置（p.5）
- **单节点、不组集群**——把核心 broker 性能与分布式协调开销隔离；除 Mosquitto（单线程架构无法并行化）外，**各 broker 调线程池/worker 数以吃满分配的 vCPU**（p.5）。
- broker 跑在 **KVM VM（KVM：Linux 内核自带的虚拟机技术）内的 Docker 容器**中，文件描述符上限 `nofile: 300000`（nofile：Linux 限制每个进程最多打开的文件/连接数，30 万即允许约 30 万并发连接）；**三档 VM**：**1 vCPU/2 GB**（IoT 网关级）、**2 vCPU/4 GB**（小型工控机）、**4 vCPU/8 GB**（雾节点/小服务器）（p.5）。
- 协议映射：各 broker 用原生协议（Artemis 走 MQTT 接口保持协议层一致；RabbitMQ 分别跑 MQTT 与 AMQP 0-9-1 两轮；Zenoh **严格配置为 client/router 模式**而非 P2P 以保证公平）（p.5）。

### 负载生成策略（p.5）
- **1-to-1（pair）拓扑**：每个 publisher 恰好配一个 subscriber、独占 topic——客户端间无干扰、压力集中在连接处理与路由、可复现；fanout 作为补充（仅在 4 vCPU/8 GB VM 上）。
- **QoS**：前两个实验用 **QoS 0（及各协议等价的 best-effort）**测峰值容量——跨协议公平；Exp3 才测全部三级 QoS。

### 测试床（p.5–6，图3，未提取）
两台专用裸金属节点（裸金属：不跑虚拟化、整台物理服务器直接租用；**Chameleon Cloud**：学术研究专用的可租用试验云平台，node type `compute_icelake_r650`，镜像 CC-Ubuntu22.04），高速私有网络互联：**Workload Generator Machine** 跑 mq-bench、拉起/销毁远端 broker 容器、spawn publisher/subscriber 进程并收集全部收发消息与时间戳；**Broker Execution Machine** 上 broker 跑在 KVM VM 内 Docker 容器里，资源监控模块全程实时采 CPU/内存（p.5–6）。

**图解（图3，未提取，据正文描述）**：拓扑图左右两台裸金属节点——左侧 **Workload Generator Machine**（负载生成机）跑 mq-bench：远程拉起/销毁 broker 容器、生成 publisher/subscriber 进程、收集全部收发消息与时间戳；右侧 **Broker Execution Machine**（broker 执行机）：broker 以容器跑在 VM 里，旁边挂资源监控模块全程采 CPU/内存；两机高速私网直连。看图要点：施压方与被测方物理分离，避免「自己压自己」抢资源。读图结论：**负载生成与被测对象分离 + 全程资源采样**是可信基准测试的底座。对毕设：哪怕只有两台电脑/虚拟机，也要把压测客户端与 broker 分开部署。

### mq-bench 工具（p.6，图4，未提取）
1. **架构**：Rust + **Tokio 异步运行时**（Tokio：Rust 生态最常用的异步任务调度库，少量线程即可挂起成千上万个等待中的任务）；可插拔传输适配层——MQTT（rumqttc）、NATS（async-nats）、Redis（redis-rs）、AMQP（lapin）、Zenoh（原生 SDK：官方提供的开发库），每个 adapter（协议适配器）实现统一的 `Transport` trait（trait：Rust 语言的接口约定，规定「必须实现哪些方法」；统一负责 subscribe/publish/连接管理）（p.6）。
2. **时延测量**：每条消息带 **24 字节二进制头，含 64-bit UNIX 纳秒发送时间戳**；`latency = t_recv − t_send`；**publisher 与 subscriber 同机运行保证时钟同步**；样本聚合报分位数/均值/标准差（p.6）。
3. **吞吐测量**：publisher 以 **open-loop 的 token-bucket 速率控制器**（见 [[开环负载与令牌桶（open-loop 与 token bucket）]]：open-loop 开环 = 发送节奏完全由测试工具决定，不等 broker 的确认或「慢一点」的反压信号，broker 再忙负载照发，才能测出真实饱和点；token-bucket 令牌桶 = 按固定速率往桶里攒「令牌」、每发一条消息花一枚，实现精确限速）按固定速率发包（不受 broker ACK/背压影响——背压：broker 忙不过来时让发送方减速的信号）——**准确暴露 broker 跟不上时的饱和行为**；吞吐只统计「稳定期」（脚本从连接日志识别全部预期客户端连上的时刻，broker 过载连不上时取连接数饱和时刻），**排除初始连接阶段**（p.6）。
4. **故障注入**：集成 **Toxiproxy**（TCP 代理：夹在客户端与 broker 中间转发流量的「中间人」，可按指令探断/延迟经过它的连接）注入连接重置等故障；故障到达时刻服从**指数分布**（泊松到达：故障时刻随机且相互独立、相邻间隔服从指数分布——比固定间隔更接近真实随机掉线），MTTF 控制平均间隔、MTTR 控制重连延迟；代理恢复后 **mq-bench 用相同 client Id 自动重连 subscriber，使 MQTT 会话恢复、QoS 1/2 消息可重投**（p.6）。

**图解（图4，未提取，据正文描述）**：架构分层图——最底层是可插拔传输适配层（MQTT/NATS/Redis/AMQP/Zenoh 五个 adapter 实现统一 Transport 接口），中层是负载生成（token-bucket 速率控制）、时延测量（消息头 24 字节内嵌 64-bit 纳秒发送时间戳）与故障注入（Toxiproxy）三个模块，顶层输出标准化结果（吞吐 / 时延分位数 / CPU、内存）。看图要点：adapter 之上的全部逻辑与协议无关——换被测系统只换 adapter，测量与统计原样复用。读图结论：**「负载、测量、故障注入与协议解耦」是 mq-bench 能横评 8 个系统的关键**。对毕设：自研测试工具时照此分层，协议适配与测量逻辑分离，后加协议不用重写测量。

## 五、experimental results（p.6–10）
### A. 时延 vs payload（p.6–7，图5，未提取；用 4 vCPU/8 GB VM 以留足余量、隔离协议差异）
- **1 KB**：**native broker 全部亚毫秒**——**NATS 0.21 ms**（最低）、Redis 0.26、Mosquitto 0.27、Zenoh 0.35；托管运行时明显更高：EMQX/RabbitMQ-MQTT 约 0.40–0.43 ms，Artemis 0.69、HiveMQ 0.76 ms，**HiveMQ P95 达 1.65 ms ≈ NATS 的 5 倍**（JVM 方差大）。
- **16 KB**：差距保持、略拉开——NATS 与 Mosquitto 并列最低 0.39 ms；HiveMQ 中位数涨到 1.24 ms（P95 2.25 ms）。
- **1 MB**：序列化与网络传输主导——**Zenoh 7.96 ms、NATS 8.27 ms、Redis 8.58 ms**；**AMQP-RabbitMQ（9.99 ms）反超 MQTT-RabbitMQ（12.11 ms）——AMQP 的二进制帧格式处理大消息更高效**；**Mosquitto 11.18 ms 高于 native 预期——单线程架构在大 payload 处理时成瓶颈**；EMQX 12.42 ms（Erlang 二进制处理高效）；**JVM 系最差：HiveMQ 17.41 ms、Artemis 21.60 ms，P95 超 32 ms——GC（垃圾回收：Java 虚拟机定期暂停下来清理不再使用的内存，这个暂停会拖慢正在处理的消息）开销 + 对象序列化（把内存中的对象转成可传输的字节流，JVM 下这一步又慢又费）带来 2–3 倍时延惩罚**。
- **Takeaway（p.7）**：小消息大家差不多；**payload 越大，native 越稳，托管运行时显著变慢**。
- **图解（图5，未提取，据正文描述）**：横轴三个 payload 档位（1 KB / 16 KB / 1 MB），纵轴端到端时延（毫秒），8 个 broker 各自标出 p50 与 p95 两层。看图要点：1 KB 档大家挤在 1 ms 以内难分高下；payload 越大分得越开——native 系（NATS/Zenoh/Redis/Mosquitto）在下方、JVM 系（HiveMQ/Artemis）翘到最上方，JVM 系的 p95 与 p50 间距张得最大。读图结论：**小消息看运行时底噪、大消息看序列化与架构效率；比 broker 必须报分位数**。对毕设：毕设测时延至少设两档 payload，并报 p50/p95。

### B. 吞吐 vs 客户端扩展（p.7–9，图6/图7；图6 三档 VM 的九宫格图未提取，fanout 图7 未提取）
- 前提：每 publisher 10 msg/s，目标吞吐 = 对数 × 10（1000 对 → 10K msg/s）；**RabbitMQ-AMQP 被排除出吞吐图——在三档 VM 全部于 500 对后就失败**（AMQP 协议开销重，高并发下连接管理/信道复用资源不足）（p.7）。
- **1 vCPU / 2 GB（p.7）**：≤1000 对大家都没问题；之后分化——**Zenoh 5000 对撑 50.8K msg/s；NATS 约 34K 封顶**，两者超限后**优雅降级而非崩溃**（优雅降级：扛不住时不崩溃，而是拒绝新增负载、维持已有服务）；**Redis 约 25K 后 CPU 饱和，内存仅 62–75 MB**；**Mosquitto 单线程封顶约 10K msg/s**，范围内稳定；**JVM 系挣扎：HiveMQ 超 10K msg/s 即停摆、Artemis 超 30K 直接失败**（内存 487 MB / 1.3 GB，GC 压力下易被 OOM kill——OOM kill：内存耗尽时操作系统直接把进程杀掉自保）；**HiveMQ 与 EMQX 在 2000 对、Artemis 在 3000 对时崩溃**（崩溃后全周期平均指标归零）；**结论：C/Rust/Go 系语言的 broker 在受限硬件上单位资源吞吐更高**（p.7）。
- **2 vCPU / 4 GB（p.7）**：多线程 broker 收益最大——**NATS 34K→53K msg/s（6000 对，+56%）**；Zenoh 5000 对约 50K、6000 对降为 41K（不再崩溃）；内存 NATS 656 MB、Zenoh 728 MB；单线程微涨：Redis 26K→28K（77–87 MB）、**Mosquitto 26K→40K**（284–308 MB）；托管运行时主要受益于内存翻倍缓解 OOM：EMQX 撑到 2000 对 18K msg/s（900 MB–1.3 GB）、HiveMQ 2000 对 18K 但 6000 对劣化到 4.3K（1.2–1.7 GB）、RabbitMQ-MQTT 3000 对 22K 后 6000 对掉到 2.8K（2.1 GB）、Artemis 18K→7.5K（约 2 GB）（p.7）。
- **4 vCPU / 8 GB（p.7–8）**：多数 broker 能撑到 **10000 对**，但性能差异显著——**Zenoh 9000 对约 90K msg/s（接近完美吞吐）、10000 对降到 82K；NATS 9000 对也达 90K**；两者平均用 3.3–3.5 核、内存 1.1–1.7 GB；单线程几乎不涨：**Redis 约 30K（66–90 MB）、Mosquitto 45K（500–620 MB）**；托管运行时收益最大：**EMQX 18K→47K msg/s（+161%，3.4–3.9 核，650 MB–3.7 GB）；Artemis 18K→70K msg/s（7000 对，8000 对失败）——全场 JVM 最大黑马；RabbitMQ-MQTT 22K→50K（5000–6000 对）；HiveMQ 4000 对 40K（超 5000 对失败）**；这些 broker 内存 1.6–5.5 GB。**结论：JVM/Erlang broker 要喂足资源才能打平甚至超过 native**（p.8）。
- **Takeaway（p.8）**：**扩展性由线程模型 + 运行时决定——多线程 native 吃核最有效，单线程有天花板，托管运行时要靠堆资源追**。
- **图解（图6，三档 VM 九宫格，未提取，据正文描述）**：三行 × 三档 VM（1/2/4 vCPU）的网格小图，每格横轴为 pub-sub 对数（500→10000）、纵轴为吞吐（msg/s），画出各 broker 的爬坡与饱和曲线——饱和即「再加客户端吞吐也不涨」的拐点。看图要点：同一 broker 跨三行对比 → 加核的边际收益；同一格内多 broker 对比 → 同资源下谁先饱和。读图结论：**多线程 native 的曲线随资源档位整体上移，单线程三档几乎不动，托管运行时靠内存变大「续命」**。对毕设：「资源约束 × 并发爬坡」的九宫格呈现可直接借用。
- **Fanout 拓扑（p.8–9，图7 未提取）**：1 publisher 以 **100 msg/s** 发共享 topic（1-to-1 用 10 msg/s 在 fanout 下几乎所有人都完美，无法压出饱和，故提高速率；因此**原始数字不能与 1-to-1 直接比较**）；**Zenoh 一枝独秀：10000 订阅者下撑 850K msg/s，CPU 仅约 2 核（远低于 4 核上限）——广播分发路径避开了 per-subscriber 开销**；**NATS 4000 订阅者约 400K msg/s 后崩到 10000 时的 167K msg/s（4 核全饱和）——分发成本随订阅者数线性增长**；其余多在 **约 100K msg/s 早早饱和**（与其 1-to-1 天花板一致）；**拓扑能翻转排名：1-to-1 中 Zenoh 与 NATS 相当，fanout 中 Zenoh 近线性、NATS 崩**（p.9）。
    - **图解（图7，未提取，据正文描述）**：横轴订阅者数（至 10000），纵轴吞吐（msg/s，最高达 850K 量级），各 broker 一条曲线（仅 4 vCPU/8 GB 档）。看图要点：Zenoh 一路近乎线性冲顶（10000 订阅者约 850K msg/s、CPU 仅约 2 核）；NATS 爬到 4000 订阅者约 400K 后折返下跌（10000 时 167K、4 核打满）；其余多数聚在约 100K 早饱和。读图结论：**拓扑一换排名就翻——广播分发路径的效率差异在 1-to-1 里被掩盖**。对毕设：设备上报天然是 fanout 场景，压测必须补 fanout 实验。

### C. 网络故障下的可靠性与时延（p.9，图8 未提取）
- **丢包**：每次测试 180 s 发 **18,200 条**消息、经历 5–6 次故障。**QoS 0 时所有 broker 丢 6.3–6.6%（1150–1200 条）——差异来自故障时刻的随机性而非实现差异（QoS 0 无缓冲无重投）**；**QoS 1 与 QoS 2 时五个 broker 全部 0% 丢包——靠持久会话（clean_session=false——clean_session 是 MQTT 的会话开关：设为 false 时 broker 在客户端断线后仍替它保留订阅与未收消息）+ 稳定 client Id + 断连期间 broker 为离线订阅者缓存消息、重连后补投**（p.9）。
- **时延**：**QoS 0 全部 P50 < 2.5 ms、P99 < 30 ms**；**QoS 1/2 的 P50 差异暴露架构差异——EMQX 与 RabbitMQ 最低（1.65–2.1 ms，Erlang 进程/actor 模型异步处理 ACK 不阻塞主消息路径）；Artemis 与 HiveMQ 中等（2.3–3.5 ms，JVM 线程池管 ACK 状态但 per-thread 开销高）；Mosquitto 最差：QoS 0 的 2.20 ms → QoS 2 的 7.93 ms（3.6 倍惩罚）——单线程必须把消息投递与 ACK 处理串行化，QoS 握手期间阻塞新消息**（p.9）。
- **尾时延是另一幅图**：**所有 broker 的 P95/P99 齐刷刷冲到 475–665 ms / 约 3000 ms——这是 5 s MTTR 窗口内消息缓冲 + 重连开销主导，与 broker 实现无关**（p.9）。
- **Takeaway（p.9）**：**高 QoS 的 ACK 开销，多线程 broker 后台消化几乎不费时延；单线程 broker 必须逐条处理 ACK，投递被拖慢**。
- **图解（图8，未提取，据正文描述）**：左半为三个 QoS 档位的丢包率对比（QoS 0 全部约 6.3–6.6%、QoS 1/2 全部 0%），右半为 QoS 0/1/2 的端到端时延分位数对比（P50/P95/P99 三层）。看图要点：丢包半边五个 broker 几乎无差异——QoS 语义决定下限；时延半边 P50 因实现而异（EMQX/RabbitMQ 最低、Mosquitto 随 QoS 升级恶化 3.6 倍），而 P95/P99 全体齐涨到数百毫秒至秒级——MTTR 恢复窗口主导。读图结论：**丢包看 QoS 语义、P50 看架构、P99 看故障恢复，三层因素各管一段**。对毕设：可靠性实验报告照此分层归因，避免把恢复窗口的开销误记到 broker 头上。

## 六、conclusion 与部署指南（p.10）
- **核心发现**：native broker 时延低于托管运行时（大 payload 下 JVM 慢 2–3 倍）；多线程 native（Zenoh/NATS）随核数扩展到 **90K msg/s**，单线程（Redis/Mosquitto）稳定但吃不到并行红利；内存差异悬殊——Redis 66–90 MB，**JVM 系高 10–50 倍**（p.10）。
- **反直觉发现（p.10）**：① **资源给足后托管运行时能反超 native——Artemis 在 4 vCPU 上 70K msg/s，高于 Redis 与 Mosquitto**；② **Mosquitto 在大 payload 下时延反而高于预期（单线程瓶颈）**。
- **部署指南（p.10）**：受限边缘设备 → 单线程 native（Mosquitto/Redis，稳定 + 内存极小）；中等边缘硬件 → 多线程 native（Zenoh/NATS，吞吐扩展好）；时延敏感 → native（大 payload 优势更明显）；功能丰富需求 → 托管运行时（RabbitMQ/Artemis，资源给足可打平）；可靠投递 → 支持 QoS 1/2 的 MQTT broker，且多线程实现的 ACK 时延代价小。
- **未来工作（p.10）**：扩展到分布式多节点部署、request-reply 等负载模式、广域 IoT 网络条件。

## 与其他论文的关系
- 与 [[5muMQ轻量可扩展MQTT代理]]：一横一纵——论文5 是「把单机 broker 用多线程 + kernel bypass 做快」的实现论文，本文则证明同一结论的另一面：**Mosquitto 单线程在 1 万连接对时饱和于 45K msg/s、QoS 2 下 ACK 串行化造成 3.6 倍时延惩罚**，而 muMQ 式的多线程事件驱动正是本文分类里扩展性最好的 native 路线；论文5 关闭 Mosquitto 的 persistent DB/$SYS 以聚焦包处理的做派，也与本文「控制变量、单节点不组集群」的方法学一致。
- 与 [[6分布式IoT边缘MQTT代理对比]]：同属 B 区块的横评类工作，本文把「单节点垂直扩展 + 资源约束」做透并留「多节点」作未来工作，论文6 正面补分布式维度。
- 与 [[4QoS级别与MQTT丢包时延相关性]]：本文 Exp3 用 TCP RST 故障注入实测 QoS 0/1/2 的丢包与时延（6.3–6.6% vs 0%、P50 2.5 ms 内 vs 数毫秒），是该论文 A 区块理论/相关性结论在 broker 实现层面的对照数据。
- 与 [[11MQTT可靠性实测压力测试]]：同为可靠性实测，本文的 MTTF/MTTR 故障模型 + Toxiproxy 注入方法可对照其压测设计。
- 与 [[1边缘计算愿景与挑战]]：本文的「三档边缘硬件画像（1C/2GB 网关 → 4C/8GB 雾节点）」是把边缘资源异构性落成可测参数的具体做法。

## 对毕设的帮助

**写论文**
- 性能评测章节的方法学论证可直接引本文：三实验矩阵（时延 vs payload 三档、并发对数 500→10K 爬坡找饱和点、故障注入下的可靠性）+ 四条原则——报 p50/p95 而非只有均值（尾时延才能暴露单线程与 GC 类问题）、吞吐只统计稳定期并排除连接建立阶段、open-loop 保持 offered load 独立于 broker 反压、CPU/内存与吞吐同采（p.4–6）。
- 可引用的结论数字：多线程 native（Zenoh/NATS）**90K msg/s** @10K 对；单线程 Mosquitto 饱和 **45K msg/s**；native 小 payload 亚毫秒（NATS **0.21 ms**）；JVM 系大 payload 慢 **2–3 倍**、内存高 **10–50 倍**；QoS 0 丢 **6.3–6.6%** vs QoS 1/2 **0%**；Mosquitto QoS 2 时延 **3.6 倍**惩罚；fanout 中 Zenoh **850K msg/s / CPU 仅约 2 核**；反直觉发现：资源给足后 Artemis **70K msg/s** 反超 native（p.7–10）。
- 选型论证可整段借用部署指南（p.10）：受限边缘设备→单线程 native；中等硬件→多线程 native；时延敏感→native；功能丰富→托管运行时（资源给足可打平）；可靠投递→支持 QoS 1/2 且 ACK 异步的 MQTT broker。

**动手实现**
- 对应任务4（可靠性保障机制）——QoS 1/2 零丢包的三个必要件已给出配方：`clean_session=false` 持久会话 + 稳定 client Id + broker 为离线订阅者缓存消息、重连补投（p.9）。毕设实现断线重连时照此设计即可。
- ACK 处理必须与消息路径异步：Mosquitto 的教训——**单线程 broker 上 QoS 2 握手会串行阻塞消息投递（时延 3.6 倍）**；EMQX/RabbitMQ 的 actor/异步 ACK 模型 P50 仅 1.65–2.1 ms（p.9）。
- 对应任务3（QoS 0/1/2 实现）：Table I（p.2–3）的三级语义表（at-most-once / at-least-once + 可能重复 / exactly-once 四步握手）可作为协议实现与测试用例的对照基准。
- 自研 broker 选型：本文把「线程模型 × 运行时」的因果链跑通——**多线程 native 是吞吐扩展的正解，托管运行时在 1–2 vCPU 受限边缘硬件上会 OOM/崩溃**；muMQ（论文5）约 3K 行 C 的 epoll 事件循环是可落地参照，资源画像目标对标 native 系数字（小 payload 亚毫秒时延、百 MB 级内存）。

**测试**
- 负载参数怎么设：1-to-1 拓扑为主（每 publisher 恰配一个 subscriber、独占 topic），每 publisher **10 msg/s**，payload 三档 **1 KB / 16 KB / 1 MB**，**120 s 测试 + 60 s warmup**，峰值容量用 **QoS 0**（跨协议公平）；故障实验 **180 s、MTTF=30 s、MTTR=5 s（TCP RST、指数到达，约 85% uptime）**；fanout 须提高速率到 **100 msg/s**（10 msg/s 压不出饱和，原始数字不能与 1-to-1 直接比较）。
- 指标口径：报 **min/p50/p95**；吞吐 = 稳定期收到消息数/时长（从连接日志识别稳定期、排除连接建立阶段）；open-loop token-bucket 控制 offered load；CPU 用「占分配 vCPU 的百分比」+ RSS 内存，Docker Stats API 1 s 采样即可。
- 环境登记以保证可复现：三档资源（1C/2GB 网关、2C/4GB 工控机、4C/8GB 雾节点）、nofile 300000、单节点不组集群、各 broker 调线程/worker 数吃满 vCPU（Mosquitto 除外）、协议用原生接口（Zenoh 锁 client/router 模式、Artemis 走 MQTT 接口）保证公平（p.5）。
- 增量测试点：本文「QoS 1 可能重复」只报了丢包侧，**重复与乱序是本文未覆盖的测试点，毕设可补上**；另按 fanout 结论，毕设不能只测 1-to-1 拓扑。

## 怎么用 & 怎么做（研0 版落地清单）

> 思维导图：[[7思维导图.canvas]] · 总览：[[毕设论文总导图.canvas]]

**什么时候翻这篇**：任务 6 测试方案定稿前（指标口径权威模板：p50/p95、稳定期吞吐、资源同采）；实现 ACK 处理时（QoS 2 串行阻塞的教训）；写论文「实验环境」一节时（环境登记清单）。

**在 Ubuntu 22.04 上**：
- 故障注入：`docker run -d -p 8500:8500 shopify/toxiproxy`，建一条指向 broker 的代理，`toxiproxy-cli toggle mqtt_proxy` 一键拔线——对应本文 TCP RST 注入（p.6）。
- 资源限档复刻三档 VM：`docker run --cpus=1 --memory=2g ...`（1C/2GB 网关档）等；`docker stats` 按 1 s 采样 CPU/内存。
- 参数照抄（p.4–5）：payload 三档 1 KB/16 KB/1 MB；每 publisher 10 msg/s；120 s 测试 + 60 s warmup；故障实验 180 s、MTTF=30 s、MTTR=5 s；吞吐只统计稳定期。

**在树莓派上**：
- 树莓派 4（4 核 8 GB）≈ 本文 1–2 vCPU 档的现实对应：在它上面让自研 broker 与 Mosquitto 各做一次「并发对数爬坡」，实测单线程与多线程的饱和差——把本文结论在真实边缘硬件上复验成毕设自己的数据。

**C++ 实现要点**：
- 消息头内嵌 64-bit 纳秒时间戳（p.6）：`clock_gettime(CLOCK_REALTIME)` 写进 24 字节二进制头，订阅端算 `t_recv − t_send`；分位数用 `std::nth_element` 求 p50/p95。
- ACK 处理必须异步（p.9 Mosquitto 教训）：QoS 1/2 的确认回执由独立线程/队列处理，不占消息投递主路径——否则 QoS 2 的 3.6 倍时延惩罚会在自研 broker 上重演。
- 断线重连配方直接采用（p.9）：`clean_session=false` + 稳定 client Id + broker 端离线缓存重连补投，即可在反复断连下做到 QoS 1/2 零丢包。
