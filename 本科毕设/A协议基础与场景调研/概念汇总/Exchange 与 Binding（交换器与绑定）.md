# Exchange 与 Binding（交换器与绑定）

**一句话定义**：AMQP 的路由机制：exchange 按规则决定消息进哪个队列，binding 是连接 exchange 与 queue 的路由规则。

**通俗解释（研0 版）**：医院分诊：分诊台（exchange）按规则表（binding）把病人分进对应诊室（queue）。「直接看号」是 direct（精确匹配），「按症状关键词模糊匹配」是 topic（通配符模式），「广播给所有诊室」是 fanout。

**关键要点**
- 四种 exchange：direct（routing key 精确匹配）、topic（通配符 * 匹配一个词 / # 匹配零或多个）、fanout（无条件广播）、header（按消息头属性 AND/OR 匹配）（论文2 p.12–13）
- queue 是命名 FIFO 缓冲；binding 描述 exchange 到 queue 的路由关系（论文2 p.11–12）
- 与 MQTT 对比：MQTT 只有 topic 一层匹配；AMQP 的 exchange 语义可表达更灵活的路由——毕设若需按内容/属性路由可借鉴

相关：[[AMQP（高级消息队列协议）]]、[[Broker（消息代理）]]、[[发布订阅模式]]
回链：[[2物联网消息协议调研]]
