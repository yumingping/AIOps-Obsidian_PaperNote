# 互操作性（interoperability）

**一句话定义**：两个以上系统交换信息并正确使用所交换信息的能力，分 technical（协议标准统一）、syntactical（数据格式统一）、semantic（数据含义统一）三层。

**通俗解释（研0 版）**：类比：technical = 双方都按同一套规则说话；syntactical = 用同一种表格格式；semantic = 表格里「单价」字段两边理解完全相同。只做到能传数据还不够，三层齐备才算真互操作——就像不同品牌电器要插头、电压、频率全对上才能真正通电。

**关键要点**
- 三层缺一层即只算部分满足（论文3 p.2 的 Req-1）
- 论文3评估的 8 个协议中只有 OPC UA 完全满足（靠其可扩展的数据与信息模型）
- MQTT 等多数协议无自有数据建模（data-agnostic），semantic 层要按用例自定义

相关：[[IIoT（工业物联网）]]、[[MQTT（消息队列遥测传输）]]、[[OPC UA（OPC Unified Architecture）]]
回链：[[3发布订阅协议综述]]
