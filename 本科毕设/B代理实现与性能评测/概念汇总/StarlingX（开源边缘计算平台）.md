# StarlingX（开源边缘计算平台）

**一句话定义**：Linux 基金会旗下的开源边缘云/虚拟化平台，把普通服务器变成可容错的边缘节点来承载容器化应用。

**通俗解释（研0 版）**：StarlingX 相当于「边缘机房的操作系统+管家」：把几台裸金属服务器组织成带冗余高可用的边缘集群，上面再跑 Docker 容器和 K8s。论文6 用它当测试底座——两台服务器做成冗余部署，broker 以容器方式跑在上面，模拟真实工业边缘网关。

**关键要点**
- 论文6 的被测环境：StarlingX v3.0 all-in-one duplex 双服务器冗余高可用部署，每台 32 线程 + 128 GB RAM + 千兆网（论文6 p.6–7）
- 同类可选平台有 EdgeX Foundry、Fledge、KubeEdge、Azure IoT Edge 等，本文因企业级特性选 StarlingX（论文6 p.3）

相关：[[Broker（消息代理）]]、[[Kubernetes（K8s，容器编排系统）]]
回链：[[6分布式IoT边缘MQTT代理对比]]
