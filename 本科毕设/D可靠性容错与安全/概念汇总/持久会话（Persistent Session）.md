# 持久会话（Persistent Session）

**一句话定义**：客户端要求 broker 记住自己的订阅与未送达消息（clean session=false / MQTT 5 的 session expiry），断线重连后接着收。

**通俗解释（研0 版）**：像健身房储物柜：你离开（断线）时不清柜（不 clean），回来（重连）时柜里东西（期间积压的消息、你的订阅关系）还在。对应的 clean session=true 就是'每次来都用一次性储物柜，走时清空'。论文10 的 DLX 本质是把这口柜子从 broker 内存挪到链上以解除容量上限。

**关键要点**
- broker 为持久会话缓存 QoS 1/2 在途消息，容量仍受内存限制——论文10 的出发点（p.1）
- unclean session 重连：不恢复旧状态、从头开始——论文10 DLX 取回路径用它触发补发（p.3–4）
- 与论文10 DLX 功能重叠：何时需要上链版 DLQ，论文未对比（笔记检视层判断）
- 毕设落法：本地落盘 + clean session=false + 相同 client ID 即可实现补发

相关：[[QoS（服务质量）]]、[[死信队列与死信交换（DLQ、DLX）]]、[[遗嘱消息]]
回链：[[10区块链增强MQTT容错]]
