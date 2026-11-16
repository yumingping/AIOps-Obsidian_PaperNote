# AMQP（高级消息队列协议）

**一句话定义**：OASIS+ISO 双标准的二进制消息协议，为企业消息中间件互操作而生，同时支持一问一答与发布订阅，路由灵活、支持事务。

**通俗解释（研0 版）**：像邮局的智能分拣系统：信（消息）先进「分拣台」（exchange），按地址规则（binding）被投进一个个信箱（queue），收件人从信箱取信。出身金融业，功能齐全但偏重，不是为小设备设计的。

**关键要点**
- 分发三组件 exchange→binding→queue；四种 exchange：direct/topic/fanout/header（论文2 p.11–13）
- 送达保证三档：at most once / at least once / exactly once；安全 SASL+TLS；跑在 TCP（论文2 p.13）
- 优势：队列负载均衡、分布式事务、连接多路复用、离线取件；劣势：无动态发现、无多播、broker SPoF、非为 IoT 设计（论文2 p.27–28）
- 实测：CPU 与内存占用都不低（两头都吃），小 payload 场景排在 CoAP/MQTT 之后（论文2 p.21–22）

相关：[[Broker（消息代理）]]、[[Exchange 与 Binding（交换器与绑定）]]、[[MQTT（消息队列遥测传输）]]、[[发布订阅模式]]
回链：[[2物联网消息协议调研]]
