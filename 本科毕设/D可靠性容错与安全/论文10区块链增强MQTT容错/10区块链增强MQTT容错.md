
- **标题**：Improving Fault Tolerance and Tackling Broker Failure in MQTT through Blockchain（用区块链改进 MQTT 容错并应对 broker 失效）
- **作者**：Gita Alekhya Paul、Yashvardhan Jagnani、P Supraja（SRM Institute of Science and Technology，Chennai，印度，Networking and Communications Department）
- **期刊/会议**：2023 Third International Conference on Advances in Electrical, Computing, Communication and Sustainable Technologies (ICAECT)，DOI: 10.1109/ICAECT57570.2023.10118032
- **发表时间**：2023 年

> 页码说明：PDF 物理页码 p.1–6 与论文自身页码一致；p.5–6 大部分为参考文献，正文实际到 p.5 前半结束。本文是**机制设计 + PoC 功能演示**型论文，**无任何量化性能数据**——笔记如实记录这一缺口。

## 一、preview/abstract（p.1）
### 痛点 / 已有方法为什么不行
- [[MQTT（消息队列遥测传输）]] 5 通过 [[QoS（服务质量）]] 1/2、**[[保留消息（Retained Message）]]**（retained message：broker 给每个 topic 记住的"最后一条留言"，新订阅者一进门就能看到）、**[[持久会话（Persistent Session）]]**（persistent session：客户端断线重连后 broker 还记得它的订阅和没送达的消息，像寄存行李）、**LWT**（[[遗嘱消息]]：设备提前在 broker 留一封"遗嘱"，一旦意外掉线，broker 代它广播"我掉线了"）实现了面向**客户端**的容错与故障检测，但作者指出两个规范级限制（p.1）：
    1. **broker 每个 client ID 只存一条 retained message**——新订阅设备本应收到"一组数据点"的应用场景（如传感器历史序列）得不到满足；
    2. **规范完全没有 broker 端容错**——broker 失效会直接断网，消息丢失。
- QoS 1/2 的未确认消息存放在 broker 维护的 **dead letter queue（dead letter exchange）**中（通俗讲见 [[死信队列与死信交换（DLQ、DLX）]]：delivery 失败、对方一直不"签收"的消息被归档进去待补发的队列，像快递点里无人认领的包裹架），而这受 **broker 系统内存限制**——边缘部署的低功耗 broker 存不下大量 retained、DLQ 与遗嘱消息（p.1）。
- 大量研究用区块链为 MQTT 做**安全**加固（BFT 共识：拜占庭容错类算法，让系统在少数节点作恶时仍能达成一致，像投票时容忍少数人捣乱；fog/mist 基础设施：把计算放到离设备更近的"雾/尘"层），**容错是被冷落的优化方向**（p.1）。本文用到的两个区块链基础机制见 [[区块链账本（Blockchain Ledger）]] 与 [[智能合约（Smart Contract）]]。

### 新方法（一段话）
提出 **3 层架构**：去中心化 broker 层（多个边缘低功耗 broker + [[负载均衡器]]：把连接分摊到多台后端服务器、某台坏了就绕开它的"调度台"）+ **区块链智能合约层**（三个合约分别管多条 retained messages、DLX、域名解析）+ 客户端层；客户端经 **[[区块链命名服务（Blockchain Naming Service, BNS）]]**（BNS：把"该连哪台服务器"的地址簿放在区块链合约上，客户端永远只连一个固定域名，背后指向谁由链上记录决定，像一本改账需全网见证的电话总机）提供的域名地址接入，由负载均衡器监控并应对 broker 失效——**把"brokerful、中心化"的 MQTT 改造成带去中心化后端的混合架构**（p.1）。**定位提醒：本论文对毕设是"对比方案"，不是推荐方案**——机制思想可借鉴，上链改造不建议照搬，理由见文末「对毕设的帮助」。

## 二、introduction（p.1）
1. **QoS 三档的容错语义**（p.1）：QoS 0（at most once）无确认、无重传；QoS 1（at least once）靠 **PUBACK**（发布确认回执：订阅方收到消息后回给 broker 的"签收回执"）保证至少一次、可能重复；QoS 2（exactly once）恰好一次。Retained Messages 与 LWT 处理**客户端**失效；**QoS 1/2 中未确认消息存入 dead letter queue，由 broker 维护**。
2. **这些容错机制全部受系统内存限制**（p.1）——这是本文一切设计的出发点。
3. 本文两件事：用区块链改进 **QoS 与 retained messages** 的实现；实现**增强型负载均衡器**应对 **broker 失效**——后者是对 MQTT 规范本身的增量（规范里根本没有）（p.1）。
4. 客户端层支持 Publisher / Subscriber / Pub/Sub 三种模式，**客户端无需任何修改**，向后兼容旧版 MQTT（p.3）。

## 三、related work（p.2）
1. **IoT 侧**：MQTT 容错特性（LWT、QoS、Retained）只能处理**接收端**的网络/连接失效，**没有 broker 失效对策**；边缘低功耗设备上的 broker 有内存约束（p.2）。
2. **区块链侧**：哈希链式不可变账本；智能合约额外提供**数据完整性、不可否认性、安全性**；去中心化存储的内存约束比边缘 broker 硬件宽松（p.2）。
3. **先前研究为何不够**（p.2）：已有工作聚焦改进**共识算法**[6]、**fog 混合架构**[7]、用 **CoAP 替代 MQTT** 连链[8]，主线是用 BFT 类算法保证 MQTT broker 上交易的安全性与完整性 [9]–[14]。**本文的落点不同：把 MQTT 连接系统中的集中式模块拆掉，换成去中心化技术**（p.2）。

## 四、三层架构（p.2–3）
![[10-Fig1_p2.png]]
*论文图1（p.2）：三层架构总览——智能合约层（DLX / retained / 域名解析三个合约）经 gRPC API 连接去中心化 broker 层；broker 层经 MQTT packets 连接 Load Balancer Layer；最底层是无需改造的客户端应用；负载均衡器另经 gRPC API 连接 BNS。*

**图解**：图自上而下四层。最上层紫色区块是区块链智能合约层，画了三个"卷轴"图标——左红 Smart Contract (For Handling DLX)、中紫 (For Handling Retained Messages)、右蓝 (For Handling Domain Name Resolution)；这一层经中间一个 gRPC API 图块（gRPC：一种程序远程调用的通用接口，可理解为合约层的"服务窗口"）向下连接。第二层粉色区块是去中心化 broker 层，里面 4 个雪花状 MQTT Brokers 图标两两互连成网状——表示没有哪个是主 broker。第三层浅蓝横条是 Load Balancer Layer（负载均衡层），与 broker 层之间标 MQTT Packets（MQTT 数据包）双向箭头；图右缘另有一条竖线把负载均衡层经一个 gRPC API 图块接回最右边的域名解析合约——这就是 BNS 查询路径。最下层橙色区块是客户端应用层：Publisher（绿色）、Pub/Sub（橙色）、Subscriber（蓝色）三台电脑图标，与负载均衡层之间也是 MQTT Packets 箭头——客户端完全感知不到后端是区块链。**读图结论**：所有"记账"类职责（补发队列、多 retained、地址簿）被搬出 broker、上链；broker 只剩转发，坏了可以换，客户端地址不变。**与毕设的关系**：这是"接入地址与后端解耦"的参考画法——毕设架构图可借鉴其分层与箭头标注，但中间两层换成传统负载均衡 + broker 池即可。

1. **Blockchain Smart Contract Layer（p.2–3）**——区块链上的"后端"，broker 层通过 **RPC 调用区块链 API** 发起事务：
    1. **合约 1：多条 retained messages**——**含义**：链上按 topic 维护 retained 消息队列（append / retrieve / purge），broker 收到 retained 标志置位的发布就调合约入队；新客户端订阅某 topic 时，broker 从合约状态取回整个队列发布给它。**为什么需要**：规范只允许每 client ID 一条 retained，链上存储解除了 broker 硬件限制（p.2）。
    2. **合约 2：Dead Letter Exchange（DLX）**——**含义**：每条 publisher 发出的消息（QoS > 0）都进链上 DLX；订阅者不确认就一直留着，等它以 **unclean session**（"不干净会话"：重连时不恢复旧会话状态、从头开始的连接方式，与 [[持久会话（Persistent Session）]] 相对）重连时由合约取回并推送。**为什么需要**：把 DLQ 从 broker 系统内存搬到链上，broker 就能存任意多的未确认消息（p.2–3）。
    3. **合约 3：域名解析 + 智能负载均衡**——**含义**：基于区块链命名服务（BNS [19][20][21]）做多个去中心化 broker 节点的解析，兼任智能负载均衡器：**迁移 topic、处理 broker 失效，使客户端不因 broker 失效丢数据**（p.3）。**为什么需要**：当前规范对 broker 失效零支持 [18]——publisher 把消息推给失效 broker 就直接丢失（p.3）。
2. **Decentralised Broker Layer（p.3）**：多个**边缘部署、低功耗**的 broker 在**同一个负载均衡器**下运行——架构不再有单点故障，负载均衡器保证各 broker 不越过带宽约束；它由合约层支撑计算，并经 BNS 对外暴露。
3. **Client Application Layer（p.3）**：Publisher / Pub/Sub / Subscriber 三类实体，**不感知后端改动**；所有客户端连接 **BNS 提供的地址**而非具体 broker——这是 broker 失效对客户端透明的关键。

## 五、三个容错算法（p.3–4）
### A. retained messages 的链上队列（p.3，流程图未嵌入）
流程（p.3 文字）：broker 收到 publish 请求 → 检查包内 **retained 标志** → 是则调智能合约按 topic 存入链上队列；新客户端加入并订阅该 topic → broker 调合约取回**该 topic 的 retained 消息队列**整条发给新客户端。合约状态就是一个 **topic → retained 消息数组** 的字典（见 PoC 部分 p.4）。
> 人话：把"每个主题只记住最后一条"升级成"每个主题记一条历史队列"，账本在链上，谁都能按 topic 查。

### B. Dead Letter Exchange（p.3–4）
![[10-Fig2_p4.png]]
*论文图3（p.4）：DLX 流程——PUBLISH 后 broker 检查客户端是否确认，未确认则由智能合约把消息排入链上 dead letter queue；订阅者以相同 session ID 重连后取回并接收全部未确认消息。*

**图解**：四泳道流程图，从左到右四列：Smart Contract（智能合约）、Broker（中转方）、顶端黑点（流程起点，标题 Implementing Dead Letter Exchange in MQTT）、Client（客户端）；黄色圆角框是步骤、菱形是判断。主路径（红色箭头）：Client 的 PUBLISH to topic → Broker 的 Waiting for a publish packet → Receives a PUBLISH packet → PUBLISH it to clients → 菱形 Did the client acknowledge the packet?（客户端确认了吗）——yes 走向右侧结束黑点（流程终止）；no 则向左进入合约泳道的 Queues the unacknowledged message to the dead letter queue（把未确认消息排进链上死信队列）。补发路径（黑色箭头）：Subscriber reconnects with the same session ID（订阅者带同一会话 ID 重连；session ID 是 broker 给每个客户端会话发的编号，报同一个号=同一个人回来了）→ Fetches the dead letter queue（取死信队列）→ Pops and returns the unacknowledged messages（逐条弹出返回）→ Receives all the unacknowledged messages。**读图结论**：确认检查是每条消息的必经关卡，"没签收"就上链存档，重连后整批补发——存档动作在合约泳道，说明存储不在 broker 内存里。**与毕设的关系**：毕设实现"离线补发"可直接照搬这张图的两个判断点（是否确认、是否同 session 重连），只需把"链上队列"换成"本地落盘队列"。

- **含义**：QoS > 0 的未确认消息全部入链上 DLQ；订阅者离线或异常断连期间消息**不弹出**；重连后 broker 取回并弹出队列、补发历史未确认数据（p.3–4）。
- **为什么需要**：不管多耗带宽，QoS > 0 的客户端都要**一条不漏**地收到未确认消息，且不占 broker 内存（p.3–4）。
- **与 MQTT 自带机制的叠加关系**（检视层判断，非论文原话）：MQTT 规范里 persistent session（clean session = false）本就让 broker 为持久会话缓存 QoS 1/2 在途消息——本文的 DLX 实质是把这份缓存外置到链上以解除内存上限，并额外覆盖订阅者长期离线的场景；论文未与自带会话持久化做对比。

### C. Blockchain Naming Services 应对 broker 失效（p.4）
![[10-Fig3_p4.png]]
*论文图4（p.4）：BNS 流程——broker 主动连接负载均衡器并注册内部状态与内部 DNS 名；broker 断开时检查可用 broker 并把该 topic 重分配到可用节点；broker 重连或过载时把 topic 从过载 broker 迁到新 broker。*

**图解**：同样是四泳道流程图，列依次为 Smart Contract、Load Balancer、顶端黑点（标题 Implementing Broker Failure Handling through ZNS）、Broker。注册路径：Broker 的 Connects to the load balancer → LB 的 Waiting for a new broker connection → Receives a new broker → Registers it to the internal state → 进合约泳道 Registers an internal DNS name for the specific broker（给该 broker 在链上登记一个内部域名）。故障路径：Broker disconnects → LB 的 Checks for available brokers → 菱形 Is there any available broker?——yes 向左 Reassigns an available broker for that topic(s)（把 topic 改挂到可用 broker）；no 走向结束黑点（没人可接管）。过载路径：Broker reconnects to the load balancer → 菱形 Is there any broker overloaded?——yes 向左 Reassigns new broker to the topic(s) from overloaded brokers（把 topic 从过载节点迁出）；no 向右下 Waits for a client to publish to any topic。**读图结论**：负载均衡器是所有判断的枢纽，合约只负责"域名登记"一步；topic 是迁移的最小单位——客户端地址不变，换的只是地址背后的 broker。**与毕设的关系**：毕设的 broker 故障切换可模仿此图的三个动作（注册、健康检查、topic 迁移），用 nginx/HAProxy 的健康检查即可替代合约登记。

- **含义**：不再给客户端单一 broker URL，而是把 broker 群封装进负载均衡层，后者挂在一个**专属 BNS URL** 下；MQTT 客户端连 BNS URL，智能合约在去中心化服务器间均衡负载，并兼任 **DNS 注册商**把每个客户端指向合适的 broker（p.4）。
- **失效与过载两条路径**（p.4）：broker 失效或过载 → 负载均衡器把受影响的 **topic 迁移**到其他可用 broker → 终端客户端无感。
- **为什么需要**：这是全文唯一真正"新增"于 MQTT 规范的容错能力——规范没有任何 broker 侧故障切换机制（p.2–3）。

## 六、PoC 结果（p.4–5）
1. **实验设置（p.4，论文图5）**：1 个 publisher（P1）+ 2 个 subscriber（S1 连接稳定、**S2 频繁断连**）；**自定义 broker 用 Node.js 实现；智能合约用 SCILLA 编写（SCILLA：Zilliqa 链专用的智能合约语言）、部署在 Zilliqa 区块链（一条公链平台，任何人可发起交易，确认需全网出块）**；客户端用 MQTTX 连接自定义 broker。
2. **合约状态（p.4，论文图6）**：状态以字典存储 retained 消息——**键 = topic 名，值 = 该 topic 的 retained 消息数组**，验证了"按 topic 的 retained 队列"落地。
3. **服务器日志（p.4–5，论文图7）**：普通发布请求 broker 直接转发；**retained 消息则触发一次区块链合约事务来存储**——链上写入只发生在 retained/DLX 路径。
4. **断连恢复演示（p.5，论文图8–10）**：P1 向 S1、S2 发布 retained 与非 retained 消息；S2 中途断连；因 retained 标志置位且 QoS > 0，broker 调链上事务保留这些消息，**S2 重连后从区块链取回（fetch 合约状态）并尽快收到**。
5. **结论表述（p.5）**：PoC 证明了基于区块链的 retained 消息方案是"弹性可扩展"的，摆脱了 broker 系统内存限制；其余算法声称可用同样方式实现。
6. ****注意：全部结果为截图级功能演示，无时延/吞吐/带宽的任何数字，也没有与原生 MQTT 的对照实验**（p.4–5）——机制的性能代价完全未评估。

## 七、结论与未来工作（p.5）
- 区块链消除了 IoT 设备硬件的存储/内存限制；DLQ 机制解除了 QoS 1/2 的内存限制（p.5）。
- broker 失效由封装 BNS 网络的负载均衡层处理：单 broker 失效时其余节点经负载均衡作为**回退机制**接管（p.5）。
- 未来方向：把 broker 本身也换成链上互相传消息的智能合约网络，做成 **broker-less 虚拟架构**，再与当前"软件层 + 硬件层"混合架构比较性能、时延与带宽（p.5）。

## 局限与批评（检视层判断，非论文自述）
1. **上链路径的时延代价未量化**：retained 写入、DLX 入队/取回都是同步的区块链事务，公链（Zilliqa）确认延迟与吞吐会成为消息路径上的新瓶颈——论文零数据支撑"弹性可扩展"的判断（**推测**：普通非 retained 发布不经链，时延影响可能局限于恢复路径，但论文未讨论）。
2. **不可变账本 vs purge**：合约声称 append / retrieve / purge（p.2），但区块链数据不可变，"purge"只能是合约状态层面的删除——历史消息仍在链上，隐私与存储成本问题未讨论。
3. **成本与费用模型缺失**：每条 QoS > 0 消息一条 DLX 记录、每条 retained 一笔事务——高频遥测场景的交易费用与链吞吐上限完全未评估。
4. **DLX 与 MQTT 自带 persistent session 功能重叠**（见 §五.B），论文未做对比，读者无法判断何时需要上链版 DLQ。
5. **负载均衡器本身仍是单点**：架构宣称"消除单点故障"（p.3），但负载均衡层若失效，BNS 解析与 topic 迁移全部停摆——论文未说明负载均衡器自身的冗余方案。

## 与其他论文的关系
- 区块内与 [[11MQTT可靠性实测压力测试]] 构成"机制设计 vs 实测评测"的对照：论文 11 用实测回答"MQTT 的 QoS 机制在真实压力下表现如何"，本文则在协议机制层面动手术——但正因缺实测，其改造收益未经论文 11 那类方法检验。
- 区块内与 [[12MQTT协议隐私改进]] 同属"对 MQTT 规范做扩展改造"的路线，动机不同：一个补可靠性（broker 失效、存储上限），一个补隐私；两者都说明 MQTT 规范在这些维度上留白。
- 跨区块与 [[9跨组织MQTT桥接架构评估]] 直接互补：论文 9 的桥接管道默认 broker 可用，只测了传输链路的时延与丢失；本文的 BNS 负载均衡 + broker 池恰好补上"桥接链路两端的 broker 失效怎么办"这一层，可作为端—边—云架构中 broker 接入层的设计参考。
- 与 [[1边缘计算愿景与挑战]] 的关系：本文"低功耗边缘 broker 内存不足"的前提正是边缘计算资源受限的经典设定（p.1–2）。

## 对毕设的帮助

> **定位声明：本论文对毕设是对比方案，不是推荐方案。** 它验证了"把 MQTT 容错状态外置到区块链"这条路走得通，但上链路径的时延/费用代价完全未量化（见「局限与批评」），且中心化部署下传统方案可达到同样效果——毕设应借鉴其机制思想，采用去区块链版本。

**写论文**
1. 相关工作/对比章节可引用本文作为"区块链增强 MQTT 容错"的代表性方案，对比维度直接用其三个合约职责：多 retained 存储、链上 DLQ、BNS 域名接入（p.2–3）。
2. 引用其规范级论据：MQTT 规范"每 client ID 只存一条 retained message"且"完全没有 broker 端容错"（p.1）——用于论证毕设补发机制与 broker 故障切换的必要性。

**动手实现**
1. 对应任务 4（可靠性机制）：三个可直接落地的做法——(a) **多 retained 语义**：毕设若要求"新订阅者收到最近 N 条数据"，不必上链，按本文"topic → 消息队列"的字典模型在 broker 侧/应用侧本地持久化即可；(b) **DLX 思想落地为本地落盘补发**：QoS 1/2 未确认消息写 SQLite/文件而非内存，订阅者重连（clean session = false + 相同 client ID）后按序补发——这是本文 DLX 算法的去区块链版本，实现成本极低；(c) LWT 与补发联动：LWT 报告订阅者离线 → 对端把该期间消息转入补发队列。
2. 对应任务 5（组网与桥接）：**"客户端连固定接入点、后端 broker 可迁移"**的解耦模式直接可用——毕设多节点组网时，边缘节点统一连一个接入地址（域名/虚拟 IP），后端用 nginx/HAProxy TCP 健康检查 + 多 broker 池做故障切换，失效 broker 的 topic 由其他节点接管。**区块链/BNS 不是必需品**：BNS 在本文里承担的就是 DNS + 健康检查 + 指针迁移，中心化部署下传统负载均衡即可达到同样效果且时延更低——这是给毕设的真实判断。
3. 对应任务 2（总体架构）：三层划分（客户端层无感改造 / 接入层 / 存储层）启发边—云架构分层画法：**客户端兼容性作为硬约束**（毕设实现不改客户端协议栈），所有容错增强收敛在接入层与后端。

**测试**
1. 对应任务 6：本文 PoC 的"稳定订阅者 S1 + 频繁断连订阅者 S2"是断线重连测试的现成用例设计，直接搬进毕设测试方案；同时本文是一个反面教材——**机制改造必须配量化对比**（时延、恢复时间、消息完整率），毕设测试章节应按 [[9跨组织MQTT桥接架构评估]] 的 benchmark 规范给数字，不能只交截图。

## 怎么用 & 怎么做（研0 版落地清单）

> 思维导图：[[10思维导图.canvas]] · 总览：[[毕设论文总导图.canvas]]

**什么时候翻这篇**：任务 4 设计可靠性机制前（图 3 的 DLX 流程就是本地落盘补发的蓝本）；写「相关工作/对比方案」时（作为区块链路线代表作）；答辩被问「broker 挂了怎么办」时。

**在 Ubuntu 22.04 上**：
- 不上链（笔记定位声明：本文是对比方案）：把链上 DLQ 换成本地落盘——`sudo apt install libsqlite3-dev`，建表 `(client_id, packet_id, topic, payload, qos, ts)`，未确认消息插入、重连按序补发、确认后删除——即本文 DLX 的去区块链版本（p.3–4）。
- broker 故障切换不用 BNS：`sudo apt install haproxy`，TCP 健康检查 + 固定接入端口；客户端永远连一个地址，失效实例被自动摘除——对应 BNS「域名固定、后端迁移」的思想（p.4）。

**在树莓派上**：
- 复现其「内存受限」前提论证落盘必要性：给 broker 限内存（`systemd-run --scope -p MemoryMax=64M mosquitto ...`），灌大量未确认消息看行为差异；再用 S1（稳定）/S2（频繁断连）双订阅者用例（p.4）验收补发。

**C++ 实现要点**：
- 多 retained 语义按本文合约模型本地化（p.4）：`std::unordered_map<std::string, std::deque<Msg>>` 按 topic 存队列而非单条——「新订阅者收到最近 N 条」直接可用。
- 补发流程照图 3 的两个判断点实现：每条 QoS>0 消息先判「是否已确认」，未确认入落盘队列；重连时判「同一 session/client id」才补投（p.4）。
- 本文反面教训写进测试计划：任何机制改造必须给量化对比（恢复时延、消息完整率），不能只交截图（p.4–5）。
