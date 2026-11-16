# 主题（Topic）

**一句话定义**：MQTT 里消息的'频道名/收件地址'，发布者按 topic 发、订阅者按 topic 收。

**通俗解释（研0 版）**：topic 像'小区-楼栋-房间'式的分层地址，如 factory/line3/sensor7。broker 靠它决定把消息投给谁。topic 名本身也占消息体积——论文9 发现 topic 名长短（15 字节 vs 29 字节）对延迟有可测影响，所以把它当成了 benchmark 参数。

**关键要点**
- 分层字符串，用 / 分隔；订阅时可用通配符一次订一批
- topic 名占消息包体积，长短影响时延（论文9 RQ2, p.8–9）
- 桥接时源 broker 的 topic A 会被转换映射为目的 broker 的 topic B（论文9 Fig.1）

相关：[[MQTT 桥接（MQTT Bridge）]]、[[MQTT（消息队列遥测传输）]]、[[通配符订阅（Wildcard Subscription）]]
回链：[[9跨组织MQTT桥接架构评估]]
