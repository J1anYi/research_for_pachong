# Phase 4: 任务数据库与消息队列基础 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-23
**Phase:** 04-renwu-shujuku-yu-xiaoxi-duilie-jichu
**Areas discussed:** 任务数据模型, 队列架构, 去重策略

---

## 任务数据模型

### 任务状态机

| Option | Description | Selected |
|--------|-------------|----------|
| 四状态 (Recommended) | pending → downloading → completed/failed，简单清晰，重试时 failed → pending | ✓ |
| 五状态 (queued) | 增加 queued 状态区分"待下载"和"已入队"，更精细但更复杂 | |

**User's choice:** 四状态 (Recommended)
**Notes:** 简单清晰，覆盖所有场景

---

### 重试退避策略

| Option | Description | Selected |
|--------|-------------|----------|
| 指数退避 (Recommended) | 每次重试间隔翻倍：1s, 2s, 4s, 8s... 避免雪崩，业界标准 | ✓ |
| 固定间隔 | 固定间隔重试，简单但可能加剧限流 | |
| 抖动间隔 | 随机间隔重试，分散重试请求 | |

**User's choice:** 指数退避 (Recommended)
**Notes:** 业界标准做法，避免雪崩效应

---

### 任务优先级支持

| Option | Description | Selected |
|--------|-------------|----------|
| 三级优先级 (Recommended) | 高/中/低三个级别，足够灵活又不过度复杂 | ✓ |
| 数值优先级 | 数值优先级（0-100），最大灵活但管理复杂 | |
| 无优先级 | 所有任务平等处理，实现最简单 | |

**User's choice:** 三级优先级 (Recommended)
**Notes:** 足够灵活又不过度复杂

---

## 队列架构

### 消费者数量

| Option | Description | Selected |
|--------|-------------|----------|
| 1 个消费者 | 单消费者顺序处理，实现最简单，避免并发复杂性 | |
| 2-3 个消费者 (Recommended) | 适度并发，平衡下载效率和限流风险，适合图片下载场景 | ✓ |
| 5+ 个消费者 | 高并发下载，但容易触发平台限流 | |

**User's choice:** 2-3 个消费者 (Recommended)
**Notes:** 适度并发，平衡下载效率和限流风险

---

### 消息队列容量上限

| Option | Description | Selected |
|--------|-------------|----------|
| 无上限 | 无限容量，新任务直接入队，内存允许时不丢弃 | |
| 有上限 (100-500) (Recommended) | 有限容量防止内存溢出，队列满时新任务写入数据库等待调度 | ✓ |

**User's choice:** 有上限 (100-500) (Recommended)
**Notes:** 防止内存溢出，队列满时写入数据库等待调度

---

### 如何避免重复下载

| Option | Description | Selected |
|--------|-------------|----------|
| 消费者去重检查 (Recommended) | 消费者从队列取任务后检查数据库，若状态已变则跳过 | ✓ |
| 生产者去重入队 | 入队前检查数据库是否已存在相同 URL 的任务，避免重复入队 | |
| 两者都做 | 双重检查最可靠但增加复杂度 | |

**User's choice:** 消费者去重检查 (Recommended)
**Notes:** 消费者检查数据库状态，若已变则跳过

---

## 去重策略

### 用什么作为图片唯一标识

| Option | Description | Selected |
|--------|-------------|----------|
| URL 直接比较 (Recommended) | 直接用完整 URL 作为唯一标识，最简单。不同 URL = 不同图片 | ✓ |
| URL 忽略查询参数 | 去掉查询参数后比较，如 https://cdn.com/a.jpg?t=123 和 https://cdn.com/a.jpg?t=456 视为同一张 | |
| URL Hash | 用 URL 哈希作为 key，但本质还是 URL 比较，无额外收益 | |

**User's choice:** URL 直接比较 (Recommended)
**Notes:** 最简单可靠，不同 URL = 不同图片

---

### 检查任务是否存在时，检查哪些状态

| Option | Description | Selected |
|--------|-------------|----------|
| 检查所有状态 (Recommended) | 检查所有状态的记录，pending/downloading 的也算存在，避免重复入队 | ✓ |
| 仅检查 completed | 只检查 completed 的记录，允许失败/进行中的任务重新入队 | |

**User's choice:** 检查所有状态 (Recommended)
**Notes:** pending/downloading 的也算存在，避免重复入队

---

## Claude's Discretion

- 抖动间隔的具体范围（min_interval, max_interval）
- 并发下载的超时时间
- 错误分类和对应的处理策略
- 数据库文件的具体位置

## Deferred Ideas

None — discussion stayed within phase scope.
