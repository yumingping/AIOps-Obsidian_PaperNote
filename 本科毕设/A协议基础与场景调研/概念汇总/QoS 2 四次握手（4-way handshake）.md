# QoS 2 四次握手（4-way handshake）

**一句话定义**：MQTT QoS 2 的报文流程 PUBLISH→PUBREC→PUBREL→PUBCOMP，保证消息 exactly-once。

**通俗解释（研0 版）**：像签一份一式两份的合同：你发文本（PUBLISH），对方回「文本收到」（PUBREC）；你再回「确认那份」（PUBREL），对方回「手续办完」（PUBCOMP）。四个来回走完，双方才都确定「就这一份、没丢没重」。代价：报文数是 QoS 0 的四倍，时延显著拉长。

**关键要点**
- 四报文：PUBLISH / PUBREC / PUBREL / PUBCOMP（论文4 p.1 图1）
- 不丢消息但时延最高；payload<8,000 bytes 时时延变化不明显，之后上翘（论文4 p.3 图4）
- 有线实验把丢包压到 0.03–0.15%（QoS 0/1 约 0.85–1.37%，论文4 p.3 图5）
- 实时性敏感的消息别默认上 QoS 2

相关：[[PUBACK（发布确认）]]、[[QoS（服务质量）]]、[[端到端时延]]
回链：[[4QoS级别与MQTT丢包时延相关性]]
