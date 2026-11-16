# 组播（multicast）

**一句话定义**：multicast：一份数据经网络设备复制，同时发给一组已加入该组的接收者的分发方式。

**通俗解释（研0 版）**：像班级群里发一条通知全班可见，而不是挨个私聊——发一次，所有人收到。好处：无中心、无单点故障、分发效率高；坏处：很多网络（尤其跨 Internet）不支持或不可控，加密（DTLS）也难套——论文3说它是 OPC UA/DDS「缺实践评估、缺传输层安全、数据量扩展受限」的共同根源。

**关键要点**
- broker-less 协议（DDS、OPC UA UDP）的消息分发基础（论文3 p.3）
- 去掉 broker 中心 = 无 SPOF，但引入扩展性与安全难题
- DDS 基于 UDP + IP multicast；OPC UA UDP/Ethernet 用 UADP 编码 + 组分发（论文3 p.6）
- 跨 Internet 部署与大数据量受 UDP/组播限制

相关：[[OPC UA（OPC Unified Architecture）]]、[[UDP（用户数据报协议）]]、[[发布订阅模式]]
回链：[[3发布订阅协议综述]]
