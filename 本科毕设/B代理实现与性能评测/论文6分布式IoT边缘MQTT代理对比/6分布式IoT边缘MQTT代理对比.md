- **标题**：A Comparison of MQTT Brokers for Distributed IoT Edge Computing（面向分布式 IoT 边缘计算的 MQTT 代理对比）
- **作者**：Heiko Koziolek, Sten Grüner, Julius Rückert（ABB Corporate Research Center Germany, Ladenburg，德国）
- **期刊/会议**：ECSA 2020（European Conference on Software Architecture），LNCS 12292, pp. 352–368, Springer Nature Switzerland AG
- **发表时间**：2020 年

> 页码说明：PDF 物理页 p.1–p.17 对应期刊印刷页 352–368。本笔记统一用 p.N = PDF 物理页码；引用印刷页码时另注。

## 一、preview/abstract（p.1）
### 痛点 / 已有方法为什么不行
- 企业级 IoT 场景（IoT，Internet of Things，物联网：给传感器、车辆、产线设备等「东西」联网、让它们互传数据的总称；网联汽车、智慧城市、云连工厂都是典型场景）需要**分布式 MQTT broker**（MQTT 见 [[MQTT（消息队列遥测传输）]]；broker 即 [[Broker（消息代理）]]——消息中转站，设备把消息发给它、要数据的人从它订阅收取；「分布式」指同时运行多个实例组成集群，单点故障有人顶上）来获得高可扩展性与高可用性；市面 broker 实现超过 20 个，软件架构师选型困难（p.1）。
- 已有对比研究的三类缺陷（p.1–2）：
    1. **只包含非分布式 broker**：小型性能测试测的都是单实例、非集群 broker；
    2. **只看性能**：忽略韧性（resilience）、安全、可扩展性等其他质量属性；
    3. **难以泛化**：从业者经验报告（如云平台上的极限压测）绑定特定上下文，结论搬不动。
- 缺少**面向企业 IoT 场景的 broker 评测标准**：这类场景要求 broker 集群化部署，给容量规划与配置带来特殊挑战（p.2）。

### 新方法（一段话）
用 GQM（Goal-Question-Metric，「目标—问题—指标」：先把评测目标写清楚，拆成几个要回答的问题，再给每个问题指定用哪个数字或观察来衡量，避免拍脑袋挑指标）方法系统地定义评测标准，对三个有代表性的**分布式** MQTT broker（EMQX、HiveMQ、VerneMQ）在真实 edge gateway 集群（edge gateway，边缘网关：装在现场、连接设备与云端的「门口服务器」；底座为开源边缘计算平台 [[StarlingX（开源边缘计算平台）]]，其上用 Docker（容器：把软件连同运行环境打包成标准化「集装箱」，搬到哪台机器都能原样运行）与 [[Kubernetes（K8s，容器编排系统）]] 编排管理）上做六维对比：性能、可扩展性、韧性、安全、可扩展机制（extensibility）、易用性。给出 5 项定量指标 + 3 项定性分析，并产出面向架构师的六点决策指导。**核心结论：EMQX 吞吐最高（28K msg/s），只有 HiveMQ 在测试场景中零丢消息，VerneMQ 功能相近且完全开源**（p.1）。

## 二、introduction（p.1–2）
1. 背景数字：全球 IoT 市场 2019 年约 1900 亿美元，预计 2026 年超 1.1 万亿美元（p.1）。
2. MQTT（ISO/IEC 20922）适合 IoT 的原因：为不稳定网络连接设计、消息体积开销小省带宽、发布/订阅模式（p.1）。
3. 集群化部署的特殊问题：broker 多实例分驻不同节点，实例间要交换消息与客户端会话信息（session，会话：broker 替每个客户端记的「档案」——订了哪些频道、有哪些消息还没送达）才能在单实例崩溃后存活；load balancer（[[负载均衡器]]：好比餐厅前台，所有客户端都先连它，它再把连接轮流分给后台各 broker 实例，对外只暴露一个地址）向客户端提供统一入口（p.2）。

### 本文贡献（p.2）
1. 用 GQM 系统定义分布式 MQTT broker 的评测标准；
2. 在 StarlingX 边缘网关集群上实测三个分布式 broker，报告 5 项定量指标；
3. 补充安全、易用性、可扩展机制（extensibility）的定性分析；
4. 给出软件架构师的 MQTT broker 决策指导（六个决策点）。

## 三、背景：企业级 IoT 消息架构（p.2–3）
1. **通用边缘网关集群架构（Fig.1, p.3，未提取）**：IoT Devices（传感器/执行器，主要发布遥测数据）→ **Message Broker Instances**（每实例独占一个物理/虚拟节点上的 pod——K8s 最小的部署单位，可理解为一个「容器盒子」，里面通常跑一个 broker 实例；可水平扩展；实例间 synchronize 消息与会话状态）→ load balancer 做 round-robin 入口；下游三类消费者：**Mobile Apps**（订阅告警列表/车辆遥测）、**Edge Applications**（本地数据分析，如预测性维护）、**Cloud Ingestion**（跨站点统计时经互联网转入公有云）。
    - **为什么需要多实例**：单实例无法在高设备数/高消息负载下存活，也无法支撑高可用（p.3）。
2. 边缘网关集群可包含多个物理节点、多层虚拟化；可选平台有 EdgeX Foundry、Fledge、KubeEdge、Azure IoT Edge、StarlingX（p.3）——本文选 **StarlingX** 做测试底座。

## 四、GQM 评测指标与实验场景（p.3–5）
### 3.1 六组 Question/Metric（p.4）
- **性能**：M1 = 最大可持续吞吐 [[MST（最大可持续吞吐）]]（maximum sustainable throughput，publisher（发布者：往 broker 发消息的一方）与 subscriber（订阅者：从 broker 收消息的一方）都能维持稳定消息队列的最高负载速率，下同）；M2 = publisher→subscriber 平均时延。
- **可扩展性**：M3 = 最大支持并发连接数；M4 = 高负载下新 broker 实例的启动时间（对应弹性伸缩 elasticity）。
- **韧性**：M5 = broker 实例崩溃场景下的丢消息数。**为什么重要**：丢个别温度读数可接受，丢紧急停机信号不可接受；该指标受 broker 队列长度配置与负载的共同影响（p.4）。
- **安全**：拒绝对安全设定量指标（易误导），改定性讨论；M6 只测一个侧面 = 开启 [[TLS（传输层安全协议）]]（Transport Layer Security：给网络通信上锁加密的协议，相当于把明信片装进保险箱再寄，途中没人能偷看或篡改）后 MST 的开销百分比。
- **可扩展机制（extensibility）/易用性**：均为定性讨论（插件机制、安装与运维，p.4）。

### 3.2 基准实验场景（p.5）
- 测试类型三分法：**fan-in**（海量设备发布→少量订阅者，典型 IoT）、**fan-out**（少量发布者→海量消费者）、**symmetric**（对称）。本文选 **对称场景**（[[对称场景（symmetric workload）]]）：10 publisher + 10 subscriber——目的是公平比较 broker 本身的质量差异，且**避免针对 fan-in/fan-out 特调 broker 队列大小配置**（p.5）。
- 负载范围 1,000–50,000 msg/s，高于多数真实场景：BMW 车联网平台在 HiveMQ 上 1,500 msg/s，Bose 消息后端在 VerneMQ 上 9,700 msg/s（p.5）。
- **payload 固定 150 Bytes** 随机二进制内容：单个遥测值只需 4 Bytes，但真实消息带元数据（ID、时间戳等）；已有工作表明 payload ≤4096 Bytes 对 MST 影响有限（p.5）。
- **[[QoS（服务质量）]] 1**（Quality of Service：MQTT 给消息定的「投递保险等级」——0 级最省事但可能丢、1 级保证至少送到一次但要等确认回执、2 级保证恰好一次但流程最重）：保证不丢消息但需 ack（ack，确认回执：收方回一句「我收到了」，因此 QoS 1 多一个网络往返）；QoS 2 还排除重复但开销对多数 IoT 场景过高，QoS 0 有丢消息风险（p.5）。

## 五、候选 broker（p.5–6）
筛选条件：原生 MQTT broker、有集群支持、至少有功能裁剪的开源社区版；三者都完整支持 MQTT 3.1/5.0、SSL/TLS、全部 QoS 级别（p.6）。
1. **EMQX**：Erlang 编写（Erlang：为电信级超高并发设计的编程语言，内部「进程」轻量到单机可开几十万个，天然适合消息中转这类高并发场景），2013 年起源于中国开源项目；开源版 Apache 2.0（150 万 docker pulls）；另有企业版、私有云版与 15 MB 的 EMQ X Edge 轻量版（可对接 KubeEdge）（p.6）。
2. **HiveMQ**：Java 编写，2012 年起于德国 dc-square（2019 年更名 HiveMQ）；社区版 Apache 2.0（50 万 docker pulls），另有 professional/enterprise 版与按小时计费的云服务；客户含 BMW 车联网平台；DNS discovery 插件支持运行时增减集群节点（p.6）。
3. **VerneMQ**：Erlang/OTP 编写，2015 年起瑞士 Octavo Labs 开发；Apache 2.0 完全开源（710 万 docker pulls），无收费商业版，仅售商业支持；客户含 Microsoft、Volkswagen（p.6）。
- 对照组落选原因：Mosquitto（C 语言）**无多线程、无原生集群支持**；AWS IoT / Azure IoT 的 MQTT 支持缺功能；RabbitMQ/Kafka 的 MQTT 插件功能受限（p.5）。

## 六、测试基础设施（p.6–7）
- **被测集群**：StarlingX v3.0 all-in-one duplex 裸机双服务器冗余高可用部署；每台 2× Intel Xeon E5-2640 v3 @2.60 GHz（8 核 16 线程/颗，共 32 线程）、128 GB RAM、千兆网络；StarlingX 跑在 CentOS 7.6 上（p.6–7）。
- **容器编排**：Docker CE + K8s；HiveMQ 用 replication controller（副本控制器：K8s 里管理 N 个一模一样副本的对象），VerneMQ/EMQX 用 stateful set（有状态副本集：给每个实例固定身份与存储的编排对象，集群类应用常用）；metalLB（把外部流量引入 K8s 集群的负载均衡组件）做 Level 2 负载均衡服务；安装用 helm chart（K8s 的一键安装包模板）（VerneMQ 1.10.2、EMQX 4.0.5）或厂商教程（Enterprise HiveMQ 4.3.2 评估版）（p.7）。
- **负载驱动**：独立同网段节点（CentOS 8.1，Xeon E5-2660 v4，16 核 32 线程，8 GB RAM）；评估过 mqtt-stresser、paho-clients、Locust/MQTT、JMeter/MQTT 后选 **MZBench**（资源占用低、Web UI、BDL 基准定义语言），用 VerneMQ 提供的定制 MQTT worker，本地 Docker 运行（p.7）。
- **测量与交叉验证**：Prometheus 采 CPU 等指标 + MZBench 指标 + 各 broker 自带 dashboard 交叉核对吞吐 + MQTTExplorer 验证 topic 列表（p.7）。
- **公平性控制**：每个 broker pod 限用最多 4 个 CPU core，避免边缘集群上其他进程干扰、也保证三个 broker 对比公平（p.8）。

## 七、评测结果（p.7–13）
### 7.1 性能（p.7–9）
- 加压方式：先建立发布速率（如 4,000 msg/s）保持 2 分钟，再每 2 分钟提一档（如 +2,000 msg/s）（p.7–8）。
- **不稳定点定义**：平均消费速率与发布速率之差超过 **100 msg/s** 即视为不可持续；曲线只画到该点之前，之后 broker 开始丢消息（p.8）。
  - **这条判据拆开看**：$\text{发布速率} - \text{平均消费速率} > 100\ \text{msg/s}$。逐符号说明：发布速率 = 测试脚本定死的、publisher 每秒发出的消息条数；平均消费速率 = 实测的、subscriber 每秒实际收到的条数；100 msg/s = 允许的「欠账」上限。大白话：**发得快、收得慢，且每秒欠账超过 100 条，就说明 broker 撑不住、开始积压丢消息**——这一拐点就是当前配置下的真实吞吐天花板（MST 的实测口径）。
- Fig.2（p.7，未提取）：三 broker 的集群 CPU 利用率随负载上升，最终都在每 pod 4 核 × 2 pod ≈ 8 核处走平——**CPU 是本场景瓶颈**（更大 payload 会撞网络瓶颈，fan-in/fan-out 会撞发布/订阅队列）（p.8）。
- **Table 1 关键数字（p.8）**：

| 指标 | EMQX | HiveMQ | VerneMQ |
|---|---|---|---|
| M1 最大可持续吞吐 MST（msg/s） | **28,000** | 8,000 | 10,000 |
| M2 1,000 msg/s 时平均时延（ms） | **6.4** | 119.4 | 8.7 |

- Fig.3（p.8，未提取）：到达 CPU 瓶颈前所有 broker 平均时延低于 150 ms；到达瓶颈后时延迅速飙升到不可接受。
- **Erlang 系两个 broker（EMQX、VerneMQ）全面优于 Java 实现的 HiveMQ**；三者消息队列大小配置相同，仍存在各自可调的 broker 级/系统级调优空间（p.9）。每次实验重复 3 次取均值并给出 95% 置信区间；吞吐数字经 MZBench 与 broker dashboard 独立双重确认（p.8）。注意：给更多 CPU（不设上限、部署更多节点）时各 broker 吞吐都能远高于此（p.8）。

### 7.2 可扩展性（p.9–10）
- **垂直方向**：三个 broker 都是多线程，能吃满主机全部核（测到 16 核）→ 换更强 CPU 即可纵向扩展；架构师应先定义负载画像再做容量规划（p.9）。
- **M3 最大连接数**：三者理论上都无限（多线程 + 水平扩展）；公开极限测试：EMQX 5000 万连接（Hotstar）、HiveMQ 1000 万连接（40 台 AWS EC2）、VerneMQ 500 万连接（80 节点 K8s）（p.9–10, Table 2）。
- **水平伸缩实验（Fig.4, p.9）**：K8s autoscaling，最少 2 pod（每节点 1 个）、最多 8 pod，设 CPU 阈值触发扩容；实验每分钟新增 1 个 publisher（+1,000 msg/s），峰值 10 publisher 共 10,000 msg/s + 10 subscriber；第 3 个 publisher 接入后越过阈值、K8s 启动新 pod。

![[6-Fig1_p9.png]]
*论文 Fig.4（p.9）：VerneMQ 的 K8s autoscaling 实验——各 broker pod 的 CPU 核占用随实验时间堆叠；提取图是原图的数据层，PDF 上「CPU threshold crossed / new pods started」等文字标注未包含在内。*

**图解**：横轴为实验时间（分钟），纵轴为集群占用的 CPU 核数；堆叠面积图的每一层颜色代表一个 broker pod，新 pod 拉起后就多出一层。从左往右读：前两个 publisher 把已有 pod 的 CPU 顶到阈值；第 3 个 publisher（约 3,000 msg/s）一接入曲线出现台阶——K8s 判定超过 CPU 阈值、启动新 pod，此后实验每分钟新增 1 个 publisher（+1,000 msg/s）就可能再抬一层台阶，最多到 8 个 pod。读图结论：**扩展由 CPU 利用率触发、且只对「新建立的连接」生效**——结合 p.10 的发现（load balancer 只分新连接、已有连接不迁移），这张台阶图只在连接数持续增加时才出现，恒定连接加压时台阶不会出现。与毕设的关系：任务5 多节点组网测试要么让客户端分批重连以触发重新分配，要么明确只按「新增连接」口径谈水平扩展收益。

- **关键工程发现（p.10）**：load balancer 只把**新连接**分给新 pod，**已有连接不迁移**——所以 autoscaling 只在有新连接时有效；**连接数恒定但速率变高时，集群无法从 autoscaling 获益，除非断开客户端重连**。
- **M4 新 pod 启动时间（p.10, Table 2）**：测量 pod 从 "PodScheduled" 到 "Ready" 的迁移时长（10 次启动均值，剔除首次拉镜像时间）：EMQX **18.6 s**、HiveMQ 20.2 s、VerneMQ **14.2 s**；低于此时长的负载峰值只能靠垂直扩展扛。容器镜像大小：EMQX 89.2 MB、VerneMQ **82.5 MB**（最小）、HiveMQ 298.6 MB。

### 7.3 韧性（p.10–11）
- 场景改造（避免高队列长度干扰）：1 publisher（100 msg/s）+ 2 subscriber + 2 broker pod（B1、B2）；P 和 S1 连 B1，S2 连 B2；**QoS 1 + persistent session**（持久会话：broker 替离线客户端保存订阅关系与未收完的消息，客户端重连后接着收）；队列配置 in-flight 1,000（在途窗口：已发出但还没收到确认的消息最多 1,000 条）、on-/offline message queue 50,000（在线/离线消息队列各缓存 50,000 条）（p.11）。
- 崩溃注入（[[崩溃注入测试]]，fault injection：系统稳定运行时故意把某个组件「弄死」，看系统能不能扛住——好比消防演习里故意拉响警报）：稳定后**强制杀掉 B2 上的 broker 进程**（Java VM / Erlang BEAM VM，VM 即各自语言程序赖以运行的「虚拟机引擎」）；预期 S2 经 load balancer 立即重连到 B1（抢在 K8s 重启 pod 之前）、恢复会话并收到断连期间 broker 缓冲的消息（p.11）。
- **结果（Fig.5, p.10–11，未提取；Table 3, p.11）**：HiveMQ 行为完全符合预期——S2 立即重连，且断连后消费速率短暂冲上 200 msg/s 以上（吐出积压缓冲），**平均丢消息 0**；EMQX 平均丢 **580** 条、VerneMQ 丢 **82** 条——断连造成的消费速率下降**没有被后续的超额消费补回来**，VerneMQ 还伴随客户端数持续下降（p.11）。每组重复 3 次结果一致；作者声明该意外行为**原因不明，留待后续研究**（p.11）。
- **图解（Fig.5，未提取）**：横轴为实验时间，纵轴为 S2 的消费速率（msg/s），三家 broker 各一条曲线。曲线的共同形状是「断崖 + 超额峰」：崩溃时刻消费速率骤降为 0（S2 断线），重连后先冲出一段高于 100 msg/s 的超额消费峰（吐积压），再回落到 100 msg/s 基线。读图要点：**看断崖后的峰有没有把曲线下的面积补满**——HiveMQ 补满（丢 0），EMQX/VerneMQ 留下永久缺口（丢 580/82 条，缺口面积 ≈ 丢消息数）。与毕设的关系：毕设的崩溃恢复测试（任务4/任务6）就用这套读法——断崖深度、超额峰面积、是否回到基线，三个特征量直接写进实验记录表。
- **怎么读这个测试（大白话）**：正常时 S2 每秒收到约 100 条。B2 被杀 → S2 断线，发往 S2 的消息暂存在 broker 的离线队列里 → S2 立即经负载均衡重连到还活着的 B1 并报上持久会话 → 先以高于 100 msg/s 的速度「吐积压」，再回落到 100 msg/s。判读三看：①重连是否秒级完成；②有没有超额补偿段——没有补偿段、消费曲线留下一道永久缺口，就说明积压消息真丢了；③速率恢复后能否回到原值、客户端数是否稳定（VerneMQ 还出现客户端数持续下降，说明实现层面另有问题）。
- **这不是「QoS 1 = 不丢消息」的失效**：三个 broker 队列配置相同、都用 QoS 1，丢消息差异来自 broker 崩溃时在途/缓冲消息的处理实现——协议保证与实现行为要分开看。

### 7.4 安全（p.11–12）
- 安全分三层：网络层（VPN）、传输层（TLS）、应用层（认证/授权）；本文测传输层：TLS v1.2，加密在 broker 实例处终结（p.12）。
- **TLS 开销（Fig.6, p.11，未提取；Table 4, p.12）**：EMQX 开 TLS 后 MST 从 28,000 跌到 **16,000** msg/s（M6 = **43%** 开销）；VerneMQ 从 10,000 到 8,000（**20%**）；HiveMQ **未测出**——MZBench 的 MQTT worker 连 HiveMQ 报 SSL 错误（其他客户端如 MQTTExplorer 连接正常），Table 4 中记 "?"（p.12）。
- **图解（Fig.6，未提取）**：横轴为发布速率（msg/s），纵轴为实测吞吐/时延；每个 broker 一对曲线——明文实线 vs TLS 虚线。看图要点：TLS 曲线在更低的发布速率处就「撞墙」走平，撞墙点的高度差就是加密吃掉的吞吐（EMQX 两线差距最大）。读图结论：**加密不改变曲线形状、只压低可用容量上限**，且不同 broker 压缩比例差异很大（43% vs 20%）。与毕设的关系：任务6 性能测试应补一组「同场景开/关 TLS 对照」，容量规划按明文吞吐 ×(1−开销) 折算（任务5/任务6）。
- **M6 的算法（大白话拆解）**：$M_6 = \dfrac{MST_{\text{明文}} - MST_{\text{TLS}}}{MST_{\text{明文}}} \times 100\%$。逐符号说明：$MST_{\text{明文}}$ = 不加密时的最大可持续吞吐（EMQX 为 28,000 msg/s）；$MST_{\text{TLS}}$ = 开启 TLS 加密后的吞吐（EMQX 为 16,000 msg/s）；两者之差是被加密「吃掉」的吞吐，除以明文吞吐得开销占比——代入 EMQX：(28,000 − 16,000) ÷ 28,000 ≈ 43%，代入 VerneMQ：(10,000 − 8,000) ÷ 10,000 = 20%。大白话：**加密要收「过路费」，EMQX 收得最狠（近一半吞吐没了）；毕设若必须开 TLS，容量按明文吞吐 ×(1 − 开销) 折算**（p.12）。
- 证书安装三家类似，可用 K8s secrets 挂载进 pod（p.12）。功能对比（Table 4, p.12）：认证/授权三者都支持文件+数据库，HiveMQ 额外支持 OAuth/LDAP；三者都支持证书认证；**TLS 版本 HiveMQ 支持 v1.3，EMQX/VerneMQ 只到 v1.2**。
- 直觉提醒：MST 跌 43% 意味着边缘网关若必须 TLS，容量规划要按明文吞吐 ×(1−开销) 折算。

### 7.5 可扩展机制 extensibility（p.12–13）
- **VerneMQ**：hooks 可改协议流、事件、条件事件；插件用 Erlang/Elixir/Lua 写、运行时加载；webhooks 把事件以 HTTP POST 发到任意端点 → 可用任意语言扩展（p.12）。
- **HiveMQ**：插件为 Java JAR、用 Google Guice 依赖注入集成；**30+ 种回调**、可向核心发指令（如 publish service）；RestService 可造 REST API；市场有开源插件（Prometheus 监控）与商业插件（HiveMQ for Kafka）（p.13）。
- **EMQX**：Erlang 扩展，厂商已提供 **25 个插件**（web dashboard、规则引擎、Lua hooks、STOMP 支持）；运行时加载；**15 个 hooks** 可链式串联；也有 webhooks（p.13）。
- 总结：三者 extensibility 都算好；**HiveMQ 开发者指南最全、hooks 最多但绑定 Java**；VerneMQ/EMQX 开源社区更活跃、hooks 少些、绑定 Erlang（p.13）。

### 7.6 易用性（p.13）
- 三者安装都顺畅：都有 Docker 镜像；VerneMQ/EMQX 提供 K8s helm chart；EMQX/HiveMQ 有 Amazon Machine Image；配置走文件+环境变量；都有 web dashboard（HiveMQ/EMQX 信息最全）与 CLI；**HiveMQ 文档最全面**（p.13）。

## 八、架构决策指导（p.13–14）
- Fig.7（p.14，未提取）：用 ADMentor 建模的问题空间，**六个顺序决策点**：
    1. **IoT 协议选型**（MQTT vs AMQP/CoAP/Kafka…）——超出本文范围；
    2. **是否集群化**：先写清负载画像（publisher/subscriber 数、payload 大小、topic、QoS、发布/订阅速率），非平凡场景大多受益于集群；
    3. **开源 vs 商业**：权衡许可费、商业支持、高级功能 vs 自建投入与社区支持——可能大幅收窄候选集；
    4. **集群配置**：pod 副本数、资源配额、autoscaling 阈值；
    5. **安全配置**：认证、授权、加密；
    6. **MQTT 配置**：队列长度、超时、**Last-Will and Testament（遗嘱消息）** 等细粒度决策，依据负载画像逐项定。
- topic 空间设计也常在架构师手里，社区有最佳实践指南，但它是连续设计空间而非离散选项（p.14）。
- **方法论建议（p.14）**：broker 安装已足够容易、负载驱动工具够强 → 架构师应在**目标部署硬件上用 MZBench BDL 写下预期负载、快速跑几轮实验**，既得到性能/可用性手感，也顺带熟悉 broker 的易用性与文档——比只读厂商 whitepaper 可靠（厂商测试难泛化，p.2）。

## 九、相关工作（p.14–15）
- **非集群对比**：Sommer 等（工业 MOM，Mosquitto 在 Intel i7 Windows PC 上不同 payload 的 MST 约 1,000 msg/s）；Mishra（树莓派单实例测 Mosquitto/BevyWiseMQTT/HiveMQ，差异很小）；Bertrand-Martinez 等（ISO 25010 定性评分，Mosquitto 因简单轻量得最高）（p.15）。
- **从业者极限报告**：Mahony 等（AWS K8s 上 VerneMQ 最多 80 节点、500 万连接、9,500+ msg/s，Locust 测量）；Hotstar（VerneMQ/EMQX 对比后选 EMQX，最多 5 台 AWS 节点上测到 5,000 万连接）；HiveMQ 团队（40 台 EC2 上 1,000 万连接）；HiveMQ 官方 fan-in QoS1 场景 8 核 CPU 测到 60K msg/s；ScaleAgent（JoramMQ 44K msg/s 优于 Apollo/Mosquitto/RabbitMQ）（p.15）。
- 通用基准 SPECjms2007 已于 2016 年退役（p.15）。

## 十、结论（p.15–16）
- **EMQX 吞吐最高（28K msg/s），VerneMQ 10K，HiveMQ 8K**（测试场景限每 pod 4 核、集群最多 8 核）（p.15）。
- **只有 HiveMQ 在韧性场景零丢消息**；三者可扩展性理论上无限（多线程 + 水平扩展）；安全功能相近，都能经 webhooks 用任意语言扩展（p.15）。
- 后续计划：更多指标与场景、纳入更多消息方案、在更资源受限的边缘网关上复测、构建预测性性能模型与自动化实验生成服务（p.16）。

## 局限与提取缺口
1. **单场景局限**：只用对称 10+10 场景测性能，未做 fan-in/fan-out 专项（作者明说见其他文献，p.5）；CPU 限 8 核，数字不能外推到不限核部署（p.8）。
2. **EMQX/VerneMQ 丢消息机理未查明**：论文只报现象（p.11），毕设引用时应表述为「实测丢消息、原因未深究」而非下结论。
3. **HiveMQ 的 TLS 吞吐缺失**（MZBench SSL 错误，p.12），六维中留了一个洞。
4. **提取缺口**：本篇 PDF 提取图 3 张中 2 张为 0 字节空文件（p.1、p.10 位置），仅有 p.9 的 Fig.4 数据层图可用；Fig.1（架构）、Fig.2/3（吞吐/时延曲线）、Fig.5（韧性消费速率）、Fig.6（TLS 开销）、Fig.7（决策指导图）均未提取，正文已用文字描述并标注。另：Fig.4 的 PDF 文字标注层（触发扩容的注释）不在提取图内，图注已注明。

## 与其他论文的关系
- 区块内：与 [[5muMQ轻量可扩展MQTT代理]] 构成「自研单机 broker 实现」与「工业级分布式 broker 选型」的互补——muMQ 回答「怎么造」，本文回答「买/用哪个、怎么测」；与 [[7IoT边缘消息代理基准测试]] 同属 B 区块基准测试，本文特色是 GQM 多质量属性框架 + 真实边缘集群底座，而非纯吞吐压测。
- 跨区块：[[2物联网消息协议调研]] 里 MQTT 相对 CoAP/AMQP 的定位是本文第 1 决策点的上游输入；[[4QoS级别与MQTT丢包时延相关性]] 的 QoS 语义分析可解释本文统一选 QoS 1 的理由（p.5）；[[8网络边缘分布式MQTT代理消息分发]] 代表另一条分布式路线——本文测的集群 broker（实例间同步会话状态，p.2–3）本质是「逻辑单点」的复制同步，论文8 研究的则是无中心 broker 间的消息分发机制，两者在 p.2 的区别论述中互为参照。

## 对毕设的帮助

**写论文**（能用在哪一章、可引用哪些结论数字）
1. **任务2（总体架构）**：Fig.1（p.3，未提取）的端—边—云流转图可直接借鉴画法：IoT Devices → load balancer → 多 broker pod（stateful set，实例间 synchronize 消息+会话）→ Edge Applications / Mobile Apps / Cloud Ingestion 三类出口；架构图上要标出 pod、负载均衡与「synchronize」边，说明高可用从哪来。
2. **任务3（QoS 模块）**：QoS 档位选择的现成论证（p.5）：QoS 2 开销过大不适合多数 IoT 场景、QoS 0 有丢消息风险 → 默认 QoS 1，并把 ack 额外往返计入时延预算。
3. **可引用的结论数字**：对称 10+10、每 pod 限 4 核（双 pod ≈ 8 核总量）下 MST = EMQX 28,000 / VerneMQ 10,000 / HiveMQ 8,000 msg/s，1,000 msg/s 时平均时延 6.4 / 8.7 / 119.4 ms（Table 1, p.8）；崩溃场景平均丢消息 0 / 82 / 580（Table 3, p.11）；TLS 开销 43% / 20%（Table 4, p.12）；新 pod 启动 14.2–20.2 s、镜像 82.5–298.6 MB（Table 2, p.10）；公开极限连接 5,000 万（EMQX）/ 1,000 万（HiveMQ）/ 500 万（VerneMQ）（p.9–10）。
4. **选型/决策章节骨架**：第六节六决策点（p.13–14）可作毕设「技术选型」小节框架；并采纳其方法论——在目标硬件上用 BDL 类脚本快速试跑，而非只引厂商 whitepaper（p.2, p.14）。

**动手实现**（可直接借鉴的机制/参数/设计取舍）
1. **任务4（可靠性机制）——参数照抄**：persistent session + in-flight 队列 1,000 + offline 队列 50,000（p.11）；但「配置相同、三家丢消息 0/82/580」说明**断线重连与消息缓冲必须实测验收**，不能靠「我们用了 QoS 1」论证——这正是任务4 需要自建崩溃注入测试的原因。
2. **任务5（多节点组网）——autoscaling 的隐藏坑**：p.10 发现负载分配在连接建立时就锁定（load balancer 只分新连接、已有连接不迁移），恒定连接加压测不出水平扩展收益；毕设多节点实现要么支持客户端分批重连打散连接，要么明确只承诺新增连接的分配。
3. **测试底座选型参照**：三家均支持 Docker 镜像 + helm chart/K8s 部署、web dashboard、webhooks 任意语言扩展（p.12–13）；镜像大小 EMQX 89.2 MB / VerneMQ 82.5 MB / HiveMQ 298.6 MB 可作为边缘网关磁盘占量的参照（p.10）。

**测试**（可模仿的实验设计/指标口径）
1. **任务4——崩溃注入怎么测**：kill broker 进程 + 观察重连后消费速率是否出现「超额补偿段」（p.11）；判读口径见 7.3「怎么读这个测试」——重连耗时、补偿段有无、速率/客户端数能否恢复三个特征量。
2. **任务6（性能测试）——整套方法学可移植**：(a) 对称 10 pub/10 sub 起步避免队列调参干扰；(b) 梯度加压 2 分钟/档、+2,000 msg/s；(c) 用「消费与发布差 >100 msg/s」作 MST 判据；(d) 每组重复 3 次 + 95% CI；(e) 用 broker dashboard 与负载工具双源交叉验证；(f) 每 pod 限 4 核保证对比公平；(g) TLS 开销单测一组（毕设按本文经验预留 20–43% 容量余量，p.12）。

## 怎么用 & 怎么做（研0 版落地清单）

> 思维导图：[[6思维导图.canvas]] · 总览：[[毕设论文总导图.canvas]]

**什么时候翻这篇**：任务 5 组网方案设计前（负载均衡/崩溃切换的现成参数）；任务 6 测试方案定稿前（GQM 方法学与 MST 判据）；论文写「高可用」论述时。

**在 Ubuntu 22.04 上**：
- 部署对照组：`docker run -d -p 1883:1883 -p 18083:18083 emqx/emqx:5`，感受集群型 broker 的配置面（dashboard 在 18083 端口），与自研 broker 进同一张对比表。
- 崩溃注入复现（p.11）：1 publisher + 2 subscriber + 2 broker 实例；`kill -9 $(pidof mybroker)` 后观察订阅端重连与「超额补偿段」；消费速率用 `mosquitto_sub` 计数脚本每秒落一行日志画曲线。
- 负载均衡：`sudo apt install haproxy`，TCP 模式 + `option tcp-check` 健康检查，把两个 broker 挂到一个 1883 入口——对应本文 load balancer 角色。

**在树莓派上**：
- 两台树莓派各跑一个 broker + 一台做客户端，复刻「杀 B2 看谁接管」的韧性实验；参数照抄本文：in-flight 1000、离线队列 50000（p.11），配持久会话验收「杀进程不丢消息」。

**C++ 实现要点**：
- 持久会话三件数据要落盘（对应本文 broker 挂掉的场景）：订阅关系表、in-flight 窗口（packet id → 消息）、离线队列；重启后按 client id 恢复。
- 记住 p.10 的坑：负载分配在连接建立时锁定、已有连接不迁移——毕设做「多节点均摊」要么让客户端分批重连，要么只承诺新增连接的分配。
