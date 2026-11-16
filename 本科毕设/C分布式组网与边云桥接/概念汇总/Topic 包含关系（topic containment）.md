# Topic 包含关系（topic containment）

**一句话定义**：记作 x ⊑ y：topic x 的任何可能语义都落在 y 里（y 覆盖 x）；判定它的 MSCP 问题在 MQTT 语法约束下可线性时间求解。

**通俗解释（研0 版）**：NY/World Trade Center/#（这栋楼的一切消息）包含 NY/World Trade Center/+/+/now（这栋楼各处当前的即时消息）——订了宽频道的人必然收到窄频道的所有消息。一般「模式包含」是计算机科学里出了名的算不动（NP-Complete），但 MQTT 只允许两种通配符、且 # 只能放末尾，这两条约束让判定变成「按 / 切层逐层比对」，最多比较层数较少一方那么多次，topic 只有几层时瞬间出结果。

**关键要点**
- 定义：x ⊑ y 表示 x 的任何可能语义包含于 y（论文8 p.3）
- MSCP（MQTT Subscription Containment Problem）：判定两条订阅谁包含谁（论文8 p.3）；一般情形 NP-Complete/co-NP-Complete，MQTT 约束下降为多项式、本文给出线性算法（论文8 p.3, p.5）
- 算法：按 / 切成列表逐层比对，四种结果——相同 / t1 包含 t2 / t2 包含 t1 / 无包含（论文8 p.5）

相关：[[Selective Subscription Forwarding（SSF，选择性订阅转发）]]、[[Topic（主题）]]、[[通配符（wildcard）]]
回链：[[8网络边缘分布式MQTT代理消息分发]]
