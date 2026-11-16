# PUBACK（发布确认）

**一句话定义**：MQTT QoS 1 中 broker 对 PUBLISH 的确认回执，保证 at-least-once（至少送达一次）。

**通俗解释（研0 版）**：快递签收回执：快递员（publisher）把件交给驿站（broker），驿站回一句「收到」（PUBACK）。但回执本身也可能寄丢——publisher 没等到回执就会重发，于是可能出现重复投递；订阅端要用 packet id 做去重。

**关键要点**
- QoS 1 = PUBLISH + PUBACK 两报文（论文4 p.1 图1）
- PUBACK 丢失 → publisher 重发 → 重复消息（论文4 p.1）
- 订阅端需幂等/去重处理，可结合 packet id 实现
- 对比：QoS 2 用四次握手根治重复，代价是时延

相关：[[QoS 2 四次握手（4-way handshake）]]、[[QoS（服务质量）]]
回链：[[4QoS级别与MQTT丢包时延相关性]]
