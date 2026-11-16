# Topic（主题）

**一句话定义**：MQTT 消息的「地址标签」，broker 依据它决定把消息转发给谁。

**通俗解释（研0 版）**：信封上的收件地址。格式如 livingroom/switch/off（客厅/开关/关）。因为 broker 要按地址分信，topic 必须对 broker 可读——所以 topic 无法像 payload 那样加密，这是 MQTT 隐私短板的核心。

**关键要点**
- 层级斜杠结构，支持 # 与 + 通配符订阅
- broker 可凭 topic 做用户画像（如 livingroom/switch/off 推断作息）
- 论文12 的五种方案本质都是「让 topic 变成无意义的暗号」，而不动 broker

相关：[[Broker（消息代理）]]、[[MQTT（消息队列遥测传输）]]、[[元数据（Metadata）]]、[[通配符（wildcard）]]、[[Topic 包含关系（topic containment）]]、[[MQTT（消息队列遥测传输）]]
回链：[[12MQTT协议隐私改进]]、[[8网络边缘分布式MQTT代理消息分发]]
