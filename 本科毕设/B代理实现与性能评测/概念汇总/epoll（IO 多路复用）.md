# epoll（IO 多路复用）

**一句话定义**：Linux 的高效事件通知机制：一个线程同时监视成千上万条 socket，只把「有数据到达」的活跃连接报告给应用。

**通俗解释（研0 版）**：像装了智能门铃的物业：不必挨家挨户敲门问（轮询 select/poll），谁家有动静门铃自动把你叫过去。select/poll 每次要返回所有「你关注的」连接，连接多事件少时开销爆炸；epoll 只返回活跃的，还有 edge-triggered（边缘触发）模式进一步减少事件量。

**关键要点**
- select/poll 返回全部感兴趣连接，epoll 只返回活跃连接
- edge-triggered：只在状态变化瞬间报一次事件
- EPOLLIN = 「连接上有数据可读」的事件标志
- muMQ、Mosquitto、论文7 的 mq-bench（Tokio 运行时）全都依赖它

相关：[[C10M 问题（千万并发连接）]]、[[SO_REUSEPORT（端口复用）]]、[[事件循环（event loop）]]
回链：[[5muMQ轻量可扩展MQTT代理]]、[[7IoT边缘消息代理基准测试]]
