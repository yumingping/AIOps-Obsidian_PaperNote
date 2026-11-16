# DDS（数据分发服务）

**一句话定义**：OMG 的数据中心、无 broker 的发布/订阅中间件标准，参与者通过「全局数据空间」直接交换数据。

**通俗解释（研0 版）**：MQTT 是广播站模式（人人都要经过电台），DDS 是大家共用的一块白板——谁都能往对应栏位写（publish），想要的人盯着栏位看（subscribe），没有中心电台，设备直接互通，时延可低至 30 µs。

**关键要点**
- data-centric + brokerless；DomainParticipant 加入同一域即可互通，动态发现无需服务器（论文2 p.13）
- 核心构件 DataWriter/DataReader；topic 三元组（name、data-type、QoS）；23 种 QoS 策略（论文2 p.13）
- 适合 LAN、UDP 多播、千级节点每节点 1000 msg/s，适合边缘/fog 分布式部署（论文2 p.21）
- 致命短板：实现库极大（RTI Windows 版超 640 MB，有时 >2 GB），受限边缘设备装不下（论文2 p.25–26, 28）

相关：[[MQTT（消息队列遥测传输）]]、[[QoS（服务质量）]]、[[发布订阅模式]]
回链：[[2物联网消息协议调研]]
