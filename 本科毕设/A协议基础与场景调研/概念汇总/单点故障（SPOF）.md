# 单点故障（SPOF）

**一句话定义**：single point of failure：系统里一旦失效就会让整体停摆的单一部件。

**通俗解释（研0 版）**：像全班作业只交一个课代表：课代表请假，收作业就中断。broker、MQTT-SN 的 standalone gateway 都是要重点设计的失效点——对策是冗余（备一个）或去中心（谁都能干，如 broker-less 组播）。

**关键要点**
- broker-based 架构的天然代价（论文3 p.3）
- MQTT-SN standalone gateway 是新的 SPOF；transparent 模式每设备一条连接、扩展性更差（论文3 p.5）
- AMQP 可借 clustering 消除 broker SPOF（论文3 p.5）
- 毕设边缘部署需给 SPOF 标注并设计降级策略

相关：[[Broker（消息代理）]]、[[发布订阅模式]]
回链：[[3发布订阅协议综述]]
