# Topic（主题）

**一句话定义**：MQTT 消息的「频道名」：用斜杠 / 分层的字符串，broker 按它把消息分发给订阅者。

**通俗解释（研0 版）**：像快递地址或电视频道：home/kitchen/oven 表示「这个家的厨房的烤箱」。层级化的好处是可以只订一层——订 home/kitchen 就能收到厨房里所有设备的消息。每个 broker 还会把它组织成一棵 topic 树来管理（论文8 p.2）。

**关键要点**
- topic 按 / 分层，broker 动态维护 topic tree 存层级与客户端兴趣（论文8 p.2）
- 消息分发的本质是 topic 匹配：谁订阅的频道与消息的频道「对得上」就送（论文8 p.2–3）
- 毕设 topic 层级建议控制在 5 层以内（论文8 p.6）

相关：[[MQTT（消息队列遥测传输）]]、[[Topic 包含关系（topic containment）]]、[[通配符（wildcard）]]、[[通配符订阅（Wildcard Subscription）]]、[[MQTT 桥接（MQTT Bridge）]]、[[Broker（消息代理）]]、[[元数据（Metadata）]]
回链：[[8网络边缘分布式MQTT代理消息分发]]、[[9跨组织MQTT桥接架构评估]]、[[12MQTT协议隐私改进]]
