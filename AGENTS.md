# AI协作说明

本文档面向AI协作开发，定义AI参与本项目开发时应遵循的规则。

## AI标准阅读顺序

1. **AGENTS.md** (本文档) → 了解协作规则
2. **docs/roadmap/current.md** → 了解当前阶段目标
3. **docs/product/prd.md** → 了解产品范围
4. **docs/architecture/overview.md** → 了解架构边界
5. **相关模块文档** → 按需读取

**注意**: 不要一次性扫描整个 docs/ 目录，只读取当前任务相关的文档。

## 事实来源划分

| 信息类型 | 事实来源文档 |
|---------|-------------|
| 产品范围 | `docs/product/prd.md` |
| 当前阶段 | `docs/roadmap/current.md` |
| 架构边界 | `docs/architecture/overview.md` |
| 项目结构 | `docs/architecture/project-structure.md` |
| 环境策略 | `docs/architecture/environment-strategy.md` |
| 前端架构 | `docs/architecture/frontend.md` |
| 后端架构 | `docs/architecture/backend.md` |
| 数据存储 | `docs/architecture/data-storage.md` |
| 模块行为 | `docs/modules/*.md` |
| 长期决策 | `docs/architecture/decisions/*.md` |
| 运行方式 | `docs/operations/*.md` |

## 代码与文档不一致时

- 如果文档明确标记为"当前标准"，则改代码时同步修正文档
- 如果文档标记为"规划中"，则以代码现状为准

## 文档更新触发条件

当以下内容变化时，必须同步更新文档：

- 产品范围或非目标变化
- API契约变化
- 数据模型变化
- 模块职责变化
- 部署结构变化
- 环境策略变化

## Git协作规则

- AI可自动执行 `git add` 和 `git commit`
- AI不自动执行 `git push`
- 一个commit只包含一个逻辑完整的改动
- 不相关的改动不应混入当前提交

### 提交信息规范

```
<type>: <subject>

[type可选值]
feat:     新功能
fix:      修复bug
docs:     文档更新
refactor: 重构
chore:    构建/工具变动
test:     测试相关
style:    代码格式
```

## 当前阶段协作边界

详见 `docs/roadmap/current.md`