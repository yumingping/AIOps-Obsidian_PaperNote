# 服务时延（service latency）

**一句话定义**：从 publisher 发出消息到 subscriber 收到消息的时间跨度——发布/订阅系统端到端时延的标准口径。

**通俗解释（研0 版）**：从「快递揽收」到「签收」的总时长。订阅者不知道发布何时发生，所以只能逐消息在两端记时间戳再相减。论文8 的动机实验显示：链式 broker + 弱网下它非线性恶化——丢包 5% 平均时延从 0.27 s 跳到 3.0 s，丢包 15% 到 6.5 s。

**关键要点**
- 定义与测量口径：publisher 发出 → subscriber 收到，逐消息记时间戳（论文8 p.3, p.8）
- 千 broker 仿真平均时延：PF 204.4 / SF 126.3 / SSF 100.8（时间槽），SSF 比 PF 降 51%、比 SF 降 20%（论文8 p.8）
- 报告时给中位数附近的集中度而非只报均值；弱网（丢包重传）必须进测试矩阵（论文8 p.3, p.8）

相关：[[Selective Subscription Forwarding（SSF，选择性订阅转发）]]、[[分布式 broker 网络（distributed broker network）]]
回链：[[8网络边缘分布式MQTT代理消息分发]]
