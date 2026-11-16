# No Local 与 Retain As Published

**一句话定义**：MQTT 5.0 为桥接场景提供的两个订阅选项：No Local 不把消息回发给发布者自己；Retain As Published 保留原消息的 retained 标志。

**通俗解释（研0 版）**：No Local 防'回声循环'：broker 把消息转给桥、桥又发回来，消息就在桥上打转；No Local 让发布者自己发的消息不再回给自己，循环就断了。Retain As Published 保证'保留最后一条'的标记在过桥后不变，接收侧看到的状态和发送侧一致。毕设实现桥接时这两个 flag 是现成抓手，不用自己发明防回环逻辑。

**关键要点**
- No Local（NL）：订阅选项，阻止 broker 把该客户端自己发布的消息再发给它，防桥接回环
- Retain As Published（RAP）：桥上转发时保留原 retained 标志，而不是按转发行为重置
- 两者都是 MQTT 5.0（2019）非规范性注释给出的桥接实现选项（论文9 p.3）

相关：[[MQTT 桥接（MQTT Bridge）]]、[[保留消息（Retained Message）]]
回链：[[9跨组织MQTT桥接架构评估]]
