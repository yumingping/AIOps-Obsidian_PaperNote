# 保留消息（Retained Message）

**一句话定义**：broker 为每个 topic 保存的'最后一条留言'：新订阅者一订阅就立刻收到，不用等下一次发布。

**通俗解释（研0 版）**：像办公室白板上留的当前状态：'空调=26℃'。你上班（新订阅）时先看一眼白板就知道现状，不用等下次有人更新。论文10 指出规范级限制：broker 每 client ID 只存一条 retained message（p.1），且存于受限内存；论文10 用链上队列把它升级为'每个 topic 一条历史队列'，新订阅者能收到最近一批数据。

**关键要点**
- 发布时置 retained 标志 → broker 存下该 topic 最后一条 → 新订阅即时获得
- 论文10 的表述：broker 每 client ID 只存一条 retained message（p.1，按论文原文记录）
- 论文10 合约 1：链上按 topic 维护 retained 队列（append/retrieve/purge，p.2）
- Retain As Published（论文9）：桥转发时原样保留该标志

相关：[[MQTT（消息队列遥测传输）]]、[[No Local 与 Retain As Published]]、[[智能合约（Smart Contract）]]
回链：[[10区块链增强MQTT容错]]、[[9跨组织MQTT桥接架构评估]]
