# OPC UA（OPC Unified Architecture）

**一句话定义**：IEC 62541 标准系列的工业互操作通信架构，自带强大的数据与信息建模能力，Part 14 扩展出 broker-based 与 broker-less 两种发布订阅传输。

**通俗解释（研0 版）**：如果说 MQTT 只保证「信能送到」，OPC UA 还规定「信里每个字段是什么意思」——它是工业自动化领域的通用语言，机床、PLC、上位机互相听得懂对方数据。论文3评估中它是唯一完全满足三层互操作的协议，但组播路线缺传输层安全、数据量扩展受限。

**关键要点**
- 唯一完全满足互操作三层（technical/syntactical/semantic，论文3 p.6–7）
- 实时性满足：已在 open62541 + TSN 上示范，OPC UA over TSN 是有前景方向（论文3 p.6）
- Part 14 组播（UDP+multicast）使 DTLS 不可用，只能靠应用层端到端签名/加密（论文3 p.6）
- 标准已规定 MQTT、AMQP 传输绑定——工业协议与轻量协议正在合流（论文3 p.7）

相关：[[IIoT（工业物联网）]]、[[互操作性（interoperability）]]、[[组播（multicast）]]
回链：[[3发布订阅协议综述]]
