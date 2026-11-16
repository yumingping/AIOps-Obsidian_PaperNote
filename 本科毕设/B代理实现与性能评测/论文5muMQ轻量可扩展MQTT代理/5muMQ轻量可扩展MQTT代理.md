
- **标题**：muMQ: A Lightweight and Scalable MQTT Broker（muMQ：轻量级可扩展的 MQTT 代理）
- **作者**：Wiriyang Pipatsakulroj、Vasaka Visoottiviseth（Mahidol University, Faculty of ICT）；Ryousei Takano（日本产业技术综合研究所 AIST）
- **期刊/会议**：IEEE 会议论文（版权行 978-1-5386-0728-2/17 ©2017 IEEE；具体会议名在 PDF 文本中未出现，**未确认**，从版权行只能确认是 2017 年 IEEE 会议）
- **发表时间**：2017 年

> 页码说明：本笔记统一用 p.N = PDF 物理页码（全文 6 页，p.1–p.6），与印刷页码一致。

## 一、abstract + introduction（p.1）
### 痛点 / 已有方法为什么不行
- **message broker（[[Broker（消息代理）]]：居中转发消息的服务器程序——像小区的快递驿站，寄件人把包裹交给驿站、驿站按地址分发给收件人，寄件人与收件人互不见面）是 IoT（物联网：带联网能力的传感器/设备组成的网络）系统的核心枢纽**（星型架构的 hub），设备与应用经它间接通信（pub/sub 范式，见 [[发布订阅模式]]：发布者把消息挂到「主题」上、订阅者按主题收消息，双方互不知晓对方存在，像订报纸——报社只管把报纸投进你的信箱）（p.1）。IoT 设备量增长（传感器市场 2007–2012 年每年增长超 200%，预测十年内达万亿级）会轻易压垮 broker（p.1）。
- **纵向扩容（vertical scalability）无效**：如果软件不能充分利用多核硬件，堆硬件没用。典型例子 **Mosquitto（最常用的开源轻量级 MQTT 代理，C 语言写成）只用一个 CPU core 处理 TCP 连接和 topic 树订阅匹配**（topic：消息的分层「地址」，如 home/bedroom/temperature；topic 树即按层级组织的匹配结构）——核再多性能也不涨（p.1）。
- **内核态 TCP/IP 栈是负担**：先期研究 [4][5] 表明内核网络栈没有充分利用多核——系统调用开销 + 多核资源竞争（p.1）。
- 对比路线：多个 broker 组 cluster 可以利用多核，但部署与配置不平凡（trivial）（p.2）。

### 新方法（一段话）
muMQ 是跑在 COTS（商用现货）硬件上的高性能 MQTT broker（MQTT 见 [[MQTT（消息队列遥测传输）]]：IoT 领域最流行的轻量级发布/订阅协议，专为低带宽、不稳定网络设计），围绕 C10M 问题（[[C10M 问题（千万并发连接）]]：让一台服务器同时扛住 1000 万条并发连接的经典工程挑战——默认配置的 Linux 服务器撑到几万条连接就到顶）的两个思路设计（p.1）：**(1) 多核可扩展**——把 TCP 连接均匀分发到各 CPU core，每个 core 用 epoll 式事件循环（socket：操作系统提供的网络连接端点，程序凭它收发数据；事件循环与 epoll 见 [[事件循环（event loop）]]、[[epoll（IO 多路复用）]]——前者：一个「等事件 → 处理事件 → 再等事件」的循环线程，一条龙处理分给自己的活；后者：Linux 的高效事件通知机制，同时盯住上万条连接、谁有数据到达就报告谁，不必挨个轮询）独立处理自己的 socket 事件并在 topic 树上做订阅匹配；**(2) kernel bypass（[[内核旁路（kernel bypass）]]：让数据包绕过操作系统内核、由应用程序直接处理——像快递不走分拣中心，寄件人直接开车送到收件人门口，省去排队分拣的开销）**——采用用户态 TCP/IP 栈 **mTCP（跑在 DPDK 之上）**，避开内核栈的系统调用开销（系统调用：应用程序请求内核代办的调用，如收发包，每次都有固定的进出内核开销）与多核竞争。muMQ 可配置使用两种传输层：Linux 内核 TCP/IP 栈（muMQ-k）或 mTCP（muMQ-m）。

### 本文贡献（p.1）
1. 设计并实现同时用**多核可扩展 + kernel bypass** 的轻量 MQTT broker，支持两种 TCP/IP 实现切换。
2. 在重负载（多客户端并发发消息）下对比 Mosquitto 与 muMQ 的端到端时延（[[端到端时延]]：一条消息从发布方发出、经代理转发、到订阅方收到的全程耗时，像快递从下单到签收的总时长）和吞吐（[[吞吐（throughput）]]：每秒成功处理的消息条数，像高速路口每秒放行的车流量）。
3. 揭示**用户态/应用定制 TCP/IP 栈用于 pub/sub broker 的收益与问题**（这是论文最有工程价值的部分，见 §五）。

## 二、related work（p.2）
1. **MQTT broker 的连接处理技术对比（p.2）**：
    - **Mosquitto**：单线程内用 `poll` 系统调用事件驱动处理多 socket；
    - **Apache ActiveMQ**：线程池，一个连接一个线程——连接多时**上下文切换开销重**（上下文切换：CPU 从一个线程换到另一个线程前要保存/恢复现场，切换太频繁就白白烧 CPU）；
    - **RabbitMQ**：Erlang（一门为电信级高并发设计的编程语言，自带轻量「进程」与调度器）写成，靠 Erlang VM 的轻量线程池做异步 I/O——**能用几个核由 Erlang VM 决定，应用控制不了**。
    - muMQ 的差异点：每核一个事件循环 + epoll 式事件通知 + OS bypass。
2. **可扩展 I/O 多路复用（p.2）**：
    - **select/poll 的问题**（select/poll：Linux 早期的事件通知接口，epoll 的前身）：返回所有**感兴趣**连接而非**活跃**连接——连接数远大于事件数时开销爆炸；**epoll** 把活跃连接分离出来，还可用 **edge-triggered 模式**（边缘触发：只在状态「从无到有」变化的那一瞬间报告一次，而不是只要还有数据就反复报告）进一步减少事件量。
    - **SO_REUSEPORT**（[[SO_REUSEPORT（端口复用）]]，Linux 3.9+）：多个 socket 绑同一端口，每个线程有自己的 listening socket 接受连接——像银行开多个窗口、叫号系统自动把新顾客分给空闲窗口——多核 I/O 多路复用的关键开关。
3. **用户态 TCP/IP 网络（p.2）**：
    - **mTCP**：多核机器上高性能用户态 TCP 栈，短连接性能最佳（消息 <1KB 时最好），提供 **BSD-like socket 与 epoll-like 事件接口**（BSD socket：Unix/Linux 通用的网络编程接口标准；epoll-like：与 epoll 用法相似的事件接口）便于移植；以动态库链接，可跑在 PacketShader/DPDK/netmap 等包 I/O 引擎（直接在用户态高速收发包的底层网络框架）上。
    - **DPDK**：用户态网络驱动框架，**PMD（Poll Mode Driver，轮询模式驱动）由应用自己的线程直接轮询读写 NIC（网卡）的收发描述符（网卡与程序之间交接数据包用的「登记条目」）、不经内核**；提供 EAL（抽象环境层：屏蔽不同网卡与系统差异的底层接口）+ 队列/缓冲/内存管理库。mTCP 自身优化：批量包处理（batched packet processing）、flow-level core affinity、per-core 数据结构。
    - 先例 [16]：把 Redis/memcached（常用的内存键值缓存服务）移植到 mTCP；发现 memcached 移植困难——它的事件循环要等**非 TCP socket** 的文件描述符事件。**muMQ 与 KVS 的报文模式不同**：一条 published 消息与其对应的下发可以走不同 TCP 连接（p.2）。

## 三、design & implementation（p.2–4）
### 设计目标（p.2–3）
四条：高单节点吞吐（减少副本数）、低端到端时延、**MQTT 标准兼容**（保证与各种客户端互操作）、**COTS 硬件**（无定制硬件）。

### 三个应用层组件（p.3）
1. **socket event loops**：响应 socket 事件处理 MQTT 逻辑，多个事件循环并行；
2. **single-instance topic tree**：全实例唯一的订阅 topic 树，做订阅匹配；
3. **in-memory client table**：保存 client 结构体（socket 描述符——操作系统给每条连接分配的编号、MQTT 状态、时间戳、client Id 等字段的内存记录）的内存指针，**以 socket descriptor（描述符）为索引**，**程序启动时预分配**整表（一次性建好，避免运行期扩容卡顿）。

![[5-Fig1_p3.png]]
*图1（p.3）：muMQ 总体架构——上层 N 个事件循环（各带 Parser）共享内存中的 topic 层级与 Client Table；传输层二选一：左边 mTCP APIs + TCP threads + DPDK（用户态），右边内核 TCP 栈 + Socket APIs；两种路径都落在同一 NIC 驱动上，按 CPU core 划分。*

**图解**：自上而下分三层。最上层 Memory（内存）：绿色框是 Topic hierarchy（订阅主题树，画成一棵红节点的树）+ 棕色框是 Client Table（客户端表，两列表格：socket ID → memory pointer 内存指针）；中间层是 N 个并排的橙色 Event loop 0/1…N，每个上面带一个黄色 Parser（解析器，把字节流拆成 MQTT 包）；再往下是二选一的传输路径——左侧灰色区在 User-level（用户态）：mTCP APIs → 多个 TCP Thread → DPDK，右侧蓝色区：Socket APIs → Kernel TCP stack（内核 TCP 栈）；最底层紫色是 NIC driver（网卡驱动），图中虚线标出用户态/内核态（Kernel-level）分界。看图要点：底部 Core 0/1…N 的灰色横条说明**每一列都对应一个 CPU 核**——关键设计是「每个核自成一条处理闭环」。读图结论：事件循环共享内存里的两份全局数据（topic 树 + client 表），传输层像插件一样可切换。对毕设：这张图就是「单机 broker 如何吃满多核」的标准答案，毕设架构图可直接以它为蓝本画三层（应用层/传输层/驱动层）。

### 事件循环的处理流程（p.3）
- 事件循环等待 socket 事件 + 检查各消息队列上是否有待发包。收到 **EPOLLIN**（epoll 报告的「这条连接上有数据可读」事件标志）后从接收缓冲读数据 → 把 TCP 字节流解析成 MQTT 包 → 按标准进入 MQTT 处理逻辑。
- **CONNECT**：TCP 连接建立后被分发到某个事件循环；收到 CONNECT 包后把 client 信息写入 in-memory table（用 TCP 栈返回的 socket descriptor 定位表项）。
- **DISCONNECT**：断开 TCP 连接，并把表中该 client 结构体**清零**移除（p.3）。
- **会话语义的实现现状**：client 结构体里保存 MQTT 状态与时间戳，但 **muMQ 不支持 retained message（保留消息：broker 替每个 topic 存最后一条消息，新订阅者一接入立刻能收到），只支持 MQTT 3.1.1 的子集（含 QoS 0）**（QoS（服务质量）见 [[QoS（服务质量）]]：MQTT 的投递可靠级别，共三档——0 档发完即忘、可能丢；1 档保底送达一次、可能重复；2 档保证恰好一次但握手最重）（p.4）——即**没有离线会话消息缓存、没有持久化**；断线即清表。这是它「轻量」的代价面。

### topic 树与订阅匹配（p.3）
- **含义**：MQTT topic 按 `/` 分层，对应一棵**动态树**；每个节点表示一层 topic 名，持有匹配订阅者的内存指针（指向 in-memory table）。
- **通配符节点的排序技巧**：订阅含 `#`/`+` 时，事件循环在同名父节点下**先创建通配符节点、再创建精确名节点**——让通配符订阅者**先拿到**匹配消息（p.3）。
- **锁协议**：SUBSCRIBE 时对**根节点加写锁**（读写锁见 [[读写锁（read-write lock）]]：读锁可多人同时持有——大家同时「看」树没问题；写锁一人独占——有人正在「改」树时别人既不能改也不能看，适合读多写少的场景）（阻止其他事件循环改树），按层切分 topic 名、从根向下遍历，存在则把订阅者指针挂进该节点的链表，不存在则建新节点，完成后释放写锁；PUBLISH 时对根节点加**读锁**，同样遍历找到匹配订阅者指针后，把消息推进各订阅者的消息队列，释放读锁（p.3）。
- **为什么需要读写锁**：多个事件循环（每核一个）并发访问唯一 topic 树；读多写少的访问形态适合读锁并行。

### mTCP 路径的数据流（p.3–4）
包 I/O 层：中断（网卡收到包后通知 CPU「该干活了」的信号）按 **RSS（receive-side scaling，[[RSS（接收侧扩展）]]：网卡自带的分流技术——按规则把进来的数据包拆给多个 CPU 核各自处理，避免所有包挤进同一个核）** 分发到指定 CPU core，**PMD 直接从 NIC 读包**；TCP 层：**TCP thread 从 NIC 接收描述符批量取包、做 TCP/IP 处理**，完成后通知 muMQ；应用层：muMQ 调 **mTCP-epoll API** 轮询事件 → 读 socket 缓冲处理 MQTT → 命中的消息推进订阅者消息队列 → 该订阅者所属应用线程经 mTCP 写出 → **TCP thread 批量写 NIC 发送描述符**（p.3–4）。

### 线程模型（p.4）
- **含义**：muMQ 是**单进程、事件驱动、多线程**应用，线程模型 **1:1**——一个 **TCP thread**（mTCP 侧）只与**绑定在同一 CPU core 的一个应用线程**配对，二者通过各自 context 里的 **shared buffer** 传数据。
- **为什么需要 1:1**：一个 **mTCP context（mtcp_manager 结构）只能持有一个 mtcp_epoll 描述符**——每核一对线程正好适配，且**不需要改 mTCP 一行代码**就能移植（p.4）。
- **应用线程之间的竞争与解法**：发布者的连接和匹配订阅者的连接可能被分发到**不同**应用线程；若应用线程直接往另一个 mTCP context 的 job queue 投递 MTCP_EPOLLOUT 事件会产生 race condition（竞态条件：两个线程同时读写同一份数据，结果取决于谁先谁后，像两个人同时编辑同一行文字互相覆盖）。**解法：在应用 context 上为每个 socket 建独立消息队列（FIFO 链表），发送时直接调 mtcp_write()**，跨线程只共享消息队列而不碰对方 mTCP context（p.4）。

![[5-Fig2_p3.png]]
*图2（p.4）：muMQ 线程模型——每核一对「App thread ↔ TCP thread」，经 shared TCP buffer 交换数据；App 侧每 socket 一个 Message Queue，旁路 event/job queues；多个 core 各自独立成对。*

**图解**：每个虚线框是一个 CPU 核上的「一对线程」——上半 Application 区（蓝色）是 App thread（应用线程），下半 MTCP context 区（绿色）是 TCP thread，中间黄色条是 User-level socket、橙色块是 Shared TCP buffer（两者紧贴，表示数据经共享缓冲交换）；蓝色区左上角的橙色 Message Queue 是每个 socket 一条的消息队列，中部灰色/紫色箭头组是 job queues 与 event queues（标注「旁路」：跨线程发消息不走它们，走各 socket 自己的 Message Queue）。App thread 0 与 App thread 1 之间的黑色虚线箭头表示跨核消息投递。看图要点：左右两个框结构完全相同，右侧「……」表示这套「核内一对」可复制 N 份。读图结论：**核内通过 shared buffer 协作、核间通过消息队列协作，互不触碰对方的 mTCP context**——这正是规避竞态的设计。对毕设：多线程 broker 画线程交互图时，「同核共享内存、跨核消息队列」是可直接套用的模式。

### 实现规模（p.4）
- **约 3K 行 C 代码**：socket 事件循环 + 订阅匹配逻辑 + MQTT parser；**实现 MQTT 3.1.1 子集**（支持通配符 topic 过滤与 QoS 0；**不支持 retained message**）。
- 内核栈模式：epoll 等待事件 + **SO_REUSEPORT** 多监听 socket 绑同端口；pthread + **读写锁**做线程同步。
- **移植到 mTCP 只改了约 90 行代码**：换成 mTCP-event/socket 调用 + 修改 socket descriptor 语义逻辑（因为用 fd 索引 client 结构体指针）。

## 四、evaluation（p.4–6）
### 实验设置（p.4）
- **broker 机**：20 核 Intel Xeon E5-2650 @ 2.30 GHz、252 GB RAM、Intel 10 GbE NIC；关 Hyper-Threading（超线程：让一个物理核伪装成两个逻辑核的技术，会干扰性能测量的纯净度，故关闭）；两个 NUMA 域各预留 2 GiB 给 mTCP（NUMA：多路服务器把内存分成几组、每组更靠近一部分 CPU，访问「别人组」的内存更慢，故按域预留）（commit 2052a3df6f1a）；Debian 8.5（kernel 3.16）。
- **client 机**：8 核 Xeon E620 @ 2.4 GHz、20 GB RAM 上的 VM（CentOS 6.8），VM 数量随负载而定；broker 与 client 之间 **10 Gigabit Ethernet**。
- **对比对象**：muMQ-k（内核栈）、muMQ-m（mTCP）、Mosquitto（revision b6385d3）。**muMQ 只用 16 核而非 20 核**：muMQ-m 下 TCP 连接在各核间分布不均，此限制来自 mTCP 实现（p.4）。
- **公平性处理**：Mosquitto 关掉影响性能的附加能力——**persistent database（消息落盘）** 与 **$SYS topic 层级**（$SYS：Mosquitto 对外上报自身运行状态的系统主题，处理它带来额外内存分配 + topic 树遍历变慢）；评测聚焦网络包处理（p.4）。
- **负载设计**：全部测试只用 **QoS 0** publish；**topic 三层、6 字节**；**payload 64 字节 = 32 字节时间戳 + 32 个随机 ASCII 字符**（payload：一条消息实际携带的数据内容，不含协议头等开销；时间戳供时延计算用）；压测工具**从零自建**（epoll + Mosquitto 发行版的 MQTT client 库），跑在内核栈上（p.4）。
- 回答三问：大量客户端下时延如何？高负载下能扛多少事务？处理海量长连接订阅者时 CPU 怎么用？（p.4）

### A. 端到端时延（p.5）
- **测法**：订阅者数 1K→512K；端到端时延 = 消息从 publisher 经 broker 到 subscriber 的时长；publisher 连发 5 条消息，**publisher 与 subscriber 同 VM 以共用时钟**；订阅者用消息内时间戳对比算 RTT（往返时延：从发出到收到回应的来回时间）；10 台 VM，一对多，每 VM 一个独立 topic（p.5）。
- **结果**：订阅者 ≤32K 时三者差不多；**64K 订阅者时 Mosquitto 时延涨到 1743 ms，是 muMQ-k 的 4.3 倍、muMQ-m 的 13 倍**；muMQ-k 与 muMQ-m 之间差异很小（p.5）。**结论：muMQ 能比 Mosquitto 多扛约 4 倍订阅者**（p.5）。延迟图（Fig.3, p.5，未提取完整版）显示 Mosquitto 在 64K 后中断（其上限约 128K），muMQ-k/m 在 128K 时约 506/899 ms、256K 时约 1882/1473 ms。
- **图解（Fig.3，未提取，据正文文字描述）**：横轴为订阅者数量（1K→256K），纵轴为端到端时延（毫秒）；三条曲线分别是 Mosquitto、muMQ-k、muMQ-m。看图要点：小规模时三条线挤在一起难分高下；规模翻倍后 Mosquitto 曲线陡然上翘并在 64K 附近中断（撑不住更多连接），muMQ 两条线爬升更平缓。读图结论：**多核可扩展把「时延开始恶化」的规模点推后了约 4 倍**。对毕设：画「时延 vs 并发规模」曲线时重点标注时延拐点，拐点位置比曲线本身更能说明架构差异。

### B. 吞吐（p.5）
- **测法**：publisher 以最大速率发；broker 机收/发 socket 缓冲从默认调大到 **4 MB / 32 MB** 防止缓冲被打爆；**pub/sub 一对一**，pub/sub 对数 ∈ {1, 2, 10, 20, 50}（1/2 对用 1 台 VM，10/20/50 对用 10 台）；**两个指标**：**subscribe rate**（broker 从 publisher 收到消息的速率）与 **publish rate**（broker 发给 subscriber 的速率）（p.5）。

![[5-Fig4_p5.png]]
*图4（p.5）：五档 pub/sub 对数下的吞吐柱状图——muMQ-m（橙）在 20/50 对时显著领先，Mosquitto（灰）在 10 对后不升反降。*

**图解**：横轴是 pub/sub 对数（1/2/10/20/50），纵轴是吞吐（Messages/sec，0 到 1,000,000）；图例六项——实心灰 = Mosquitto、实心蓝 = muMQ-k、实心橙 = muMQ-m 的 subscribe rate（broker 收消息速率），带斜纹的同色柱 = 各自的 publish rate（broker 发消息速率）。看图要点：① 对数从 1 爬到 2 时三家都涨；② 10 对起灰柱不再增长、50 对时反而回落到约 175K——单线程饱和后再加压只会更糟；③ 橙柱一路涨到 50 对约 945K，是灰柱的 5 倍以上；④ 蓝柱在 10 对后横住约 590K——内核栈成为下一个瓶颈。读图结论：**吞吐天花板由「线程模型 × 传输层」共同决定**。对毕设：这张「对数爬坡找饱和点」的柱状图是毕设性能测试可直接模仿的呈现方式。

- **结果（p.5）**：
    - **20 对时 muMQ-m 比 muMQ-k 高最多 154%，比 Mosquitto 高最多 397%**；
    - **50 对时 muMQ-m 的 subscribe rate = 944,017 msg/s，publish rate = 930,275 msg/s，分别是 muMQ-k 的 1.8 倍、Mosquitto 的 5.38 倍**；
    - **muMQ-k 在 10 对即饱和**，20 对时略降；Mosquitto 同样 10 对饱和后随对数下降；
    - **muMQ 的 subscribe rate 高于 publish rate——原因是线程间锁竞争**（订阅者消息队列上的锁）；
    - **1 对时 Mosquitto 反超** muMQ-k/muMQ-m 最多 110%/104%：连接数少时内核 `poll` 反而高效（感兴趣连接少），且 **Mosquitto 单线程没有锁竞争**（p.5–6）。

### C. CPU 利用率（p.6）
- **测法**：订阅者 1K→512K，等 MQTT 层连接全部建立后用 Linux `top` 采样；10 台 VM 均摊订阅者（p.6）。
- **结果**：**muMQ-k/m 能扛到 512K 订阅者；Mosquitto 上限约 128K**，之后无法再接受新 TCP 连接——Mosquitto CPU 永远不超 100%（单核 100% = 一个核满载）；**muMQ-k 的 CPU 随订阅者指数增长，512K 时约 1400%；muMQ-m 恒定在约 1600%（共 16 核）——因为 DPDK 的 PMD 一直忙轮询 NIC，被配置的核永远满载**（p.6）。**结论：muMQ 按配置吃满多核，这是扛更多连接的根因**（p.6）。

## 五、discussion：移植消息 broker 到 mTCP 不平凡（p.6）
1. **mTCP 的多核可扩展特性用不上**：flow-level core affinity 与 per-core 数据结构是为 web server/KVS 设计的——那类应用每个连接自足；**broker 的发布者连接与匹配订阅者连接被随机分发到不同核**，这与 web server/KVS 完全不同的 modality（p.6）。
2. **跨核转发 → 锁竞争**：发布者与订阅者不同核时，消息要推到订阅者所在线程的消息队列，**多 topic 同时命中一个订阅者时在该订阅者的消息队列上发生锁竞争**（p.6）。这正是 §四.B 中 subscribe rate > publish rate 现象的根因。
3. **备选路线**：多进程 + 多线程混合架构——Mosquitto 的 bridge 模式（桥接：两个 broker 之间建立转发通道、互为上下游）组 cluster（集群：多台 broker 分担负载、协同对外服务），bridge 进程按 topic 把消息委派给其他 broker 进程；能用多核，但**进程间通信开销随集群内消息传播量增长而劣化**（p.6）。

## 六、conclusion（p.6）
- **性能提升的关键因素是多核可扩展**（并行处理网络包），mTCP 是第二层增益；**mTCP 版吞吐比 Mosquitto 最高超出 538%**；未来工作：对比其他支持多线程的知名 MQTT broker。源码：https://bitbucket.org/aistmu/mumq （p.6）。

## 与其他论文的关系
- 与 [[7IoT边缘消息代理基准测试]]：互为印证的两个视角——本文是「把单机 broker 做到极致」的实现论文，论文7是大规模横评；论文7 用数据证实了本文的出发点（**Mosquitto 单线程架构在 1 万连接对时饱和在 45K msg/s**，而多线程 NATS/Zenoh 可到 90K），也证实本文路线（多线程 native broker）正是其结论中扩展性最好的一类。
- 与 [[6分布式IoT边缘MQTT代理对比]]：本文给出单机垂直扩展的上限与代价（§五讨论 cluster 方案的进程间开销），论文6 从水平分布式部署的角度回答「单机不够时怎么办」——两者合起来构成「垂直 vs 水平」的完整对照。
- 与 [[2物联网消息协议调研]]：本文实现的是 MQTT 3.1.1 的子集（QoS 0 + 通配符），协议细节可回溯该调研笔记。
- 与 [[8网络边缘分布式MQTT代理消息分发]]：本文 §五 指出单机多核和 broker cluster 都有天花板，是 C 区块「网络边缘分布式 MQTT」路线的动机面之一。

## 对毕设的帮助

**写论文**
- 架构/实现章节可引用工程量数字：**约 3K 行 C** 实现「事件循环 + 订阅匹配 + parser」，移植到 mTCP 仅改**约 90 行**（p.4）——论证「每核事件循环」架构的工程可行性。
- 性能测试章节可引用的结论数字：64K 订阅者时 Mosquitto 时延 **1743 ms**（muMQ-k 的 4.3 倍、muMQ-m 的 13 倍，p.5）；50 对时 muMQ-m **subscribe rate 944,017 msg/s、publish rate 930,275 msg/s**（muMQ-k 的 1.8 倍、Mosquitto 的 5.38 倍，p.5）；**mTCP 版吞吐比 Mosquitto 最高超出 538%**（p.6）；CPU 侧 muMQ-m 恒定**约 1600%**（PMD 忙轮询）、Mosquitto 上限约 **128K 订阅者**（p.6）。
- 讨论/选型论证章节可引用 §五 两条教训：**pub/sub broker 的连接分布天然无法做 flow-level affinity**，跨线程消息队列 + 锁竞争是内禀成本；**broker cluster 的进程间通信开销随消息传播量增长而劣化**（p.6）——共同界定「单机多核（垂直扩展）」与「集群（水平扩展）」各自的边界。

**动手实现**
- 对应任务3（实现 MQTT 发布/订阅模块，支持 QoS 0/1/2），架构上直接可抄的三件套——**(a) 每核一个 epoll 事件循环 + SO_REUSEPORT 多监听 socket**，让多核自然分摊连接；**(b) 预分配、以 fd 为索引的 client 表**，避免运行期哈希表扩容抖动；**(c) topic 树 + 根节点读写锁**（SUBSCRIBE 写锁 / PUBLISH 读锁）。毕设 broker 若用 C/C++/Rust 可照搬；若功能要全（retained、QoS 1/2），至少保留「单实例 topic 树 + 读锁并行匹配」的形态。
- 对应任务4（持久化、断线重连、遗嘱等可靠性机制）：muMQ 是反面教材兼边界样本——**没有持久化、没有离线会话缓存，断线即清表**。毕设要支持 QoS 1/2 就必须补上它没有的部分：离线消息按 client Id 缓存、会话状态（subscription + inflight 窗口）落盘；论文7 实证了 `clean_session=false` + 稳定 client Id + broker 端缓存就能在网络反复中断下做到 0 丢包，可作为毕设会话机制的设计依据。
- 对应任务2（总体架构设计）：本文 §五 的教训要写进架构权衡——发布者/订阅者跨核是常态，毕设架构图里应显式画出「跨核消息队列」这条路径，并在性能分析时解释它对 publish rate 的影响；若追求更高单机吞吐，mTCP/DPDK 路线（1.8× 增益）可作为展望，但要接受 **PMD 忙轮询吃满核（恒定 1600% CPU）** 的功耗代价——这对电池供电的边缘网关不可接受，正好论证毕设选内核栈 + epoll 的合理性。

**测试**
- 对应任务6（性能测试：连接数、吞吐、时延），可直接复用的测试设计——(a) **payload 内嵌 32 字节时间戳**，publisher/subscriber 同机共钟测端到端时延；(b) **subscribe rate 与 publish rate 分开报**，两者差值即锁竞争损耗的诊断信号；(c) 三档实验（大量订阅者下的时延曲线 / pub-sub 对数爬坡吞吐 / CPU 利用率 vs 连接数）加 **1→50 对饱和点寻找**；(d) 报告数字时注明 broker 版本（本文连 Mosquitto 的 git revision b6385d3 都写了）与关闭了哪些功能（persistent DB、$SYS）。

## 怎么用 & 怎么做（研0 版落地清单）

> 思维导图：[[5思维导图.canvas]] · 总览：[[毕设论文总导图.canvas]]

**什么时候翻这篇**：任务 3 写 broker 主体代码前（这是实现蓝本：三件套架构直接照搬）；架构图画线程模型时；需要论证「为什么不用 mTCP/DPDK」时。

**在 Ubuntu 22.04 上**：
- 编译原版对照：`git clone https://bitbucket.org/aistmu/mumq`（p.6 给出的源码地址）；跑不通就以笔记三件套为准自研。
- 系统调优对齐本文口径：`ulimit -n 300000`（文件描述符上限）、`sudo sysctl -w net.core.somaxconn=4096`；多核验证用 `taskset -c 0 ./mybroker` 逐核绑核对比吞吐。
- 对照组 Mosquitto：`sudo apt install mosquitto`；测吞吐时按 p.4 关掉 `persistence false` 与 `$SYS`（mosquitto.conf），保证对比公平。

**在树莓派上**：
- 树莓派 4 是 4 核 A72：把「每核一个事件循环」跑满 4 核，观察吞吐是否随核数近似线性——这是任务 3 的核心验收实验；同场景测 Mosquitto 作对照（预期单核饱和）。

**C++ 实现要点**：
- 三件套照抄（p.3–4）：
  1. 每核一个事件循环：`epoll_create1` + `EPOLLIN/EPOLLOUT`；监听 socket 设 `SO_REUSEPORT`，每线程独立 `bind/listen` 同一端口；
  2. client 表：启动时 `std::vector<Client> pool(max_fds)` 预分配、以 fd 为下标，避免运行期扩容抖动；
  3. topic 树：按 `/` 分层的节点树 + 根节点 `pthread_rwlock_t`（SUBSCRIBE 取写锁、PUBLISH 取读锁）。
- 发布者与订阅者跨核时消息走「目标 socket 所属线程的消息队列」（每 socket 一个 FIFO + `eventfd` 唤醒），不直接碰对方线程数据——对应图 2 的旁路设计（p.4）。
- 规模感：本文约 3K 行 C（p.4），毕设 broker 核心按同等量级规划，先不碰持久化/集群。
