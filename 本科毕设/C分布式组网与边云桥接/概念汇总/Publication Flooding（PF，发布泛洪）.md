# Publication Flooding（PF，发布泛洪）

**一句话定义**：broker 间分发机制之一：每条发布消息复制给所有 broker，订阅只在本地处理。

**通俗解释（研0 版）**：把每条消息复印一份发到所有邮局——不管有没有人要。好处是任何 broker 手上都有全量消息、订阅者连哪个都能立即收到；坏处是流量 = 消息量 ×（broker 数 − 1），发布一多就爆炸。

**关键要点**
- 最直接，但流量随消息量爆炸（论文8 p.3–4）
- 对通配符率几乎不敏感（反正全泛洪）；发布集中、多数 broker 都感兴趣时反而占优（论文8 p.6）
- 网络很空闲、处理时延主导时 PF 时延反而最低（反直觉，论文8 p.8）

相关：[[Selective Subscription Forwarding（SSF，选择性订阅转发）]]、[[Subscription Flooding（SF，订阅泛洪）]]、[[分布式 broker 网络（distributed broker network）]]
回链：[[8网络边缘分布式MQTT代理消息分发]]
