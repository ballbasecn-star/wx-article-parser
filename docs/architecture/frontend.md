# 前端架构

## 技术栈

- **框架**: 待定（React/Vue）
- **构建工具**: Vite
- **UI组件库**: 待定
- **HTTP客户端**: Axios/Fetch
- **状态管理**: 按需选择

## 目录结构

```
frontend/
├── src/
│   ├── components/       # 通用组件
│   │   ├── common/       # 基础组件
│   │   └── business/     # 业务组件
│   ├── pages/            # 页面组件
│   │   └── Home/         # 首页
│   ├── services/         # API调用
│   │   └── api.ts        # API封装
│   ├── hooks/            # 自定义Hooks
│   ├── utils/            # 工具函数
│   ├── styles/           # 全局样式
│   └── App.tsx           # 应用入口
├── public/               # 静态资源
└── index.html            # HTML模板
```

## 组件设计原则

- 组件职责单一
- 通用组件放在 `components/common/`
- 业务组件放在 `components/business/`
- 页面特定组件放在 `pages/*/components/`
- 避免过深的组件嵌套（不超过3层）

## 页面规划

### MVP阶段页面

| 页面 | 路径 | 功能 |
|-----|------|------|
| 首页 | `/` | 输入链接、展示结果、导出 |

## 状态管理策略

MVP阶段采用轻量级状态管理：

- **组件状态**: 表单数据、UI状态
- **全局状态**: 如有需要，按需引入

## API调用规范

```typescript
// services/api.ts
const API_BASE = import.meta.env.VITE_API_URL;

// 统一请求封装
async function parseArticle(url: string) {
  const response = await fetch(`${API_BASE}/api/v1/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  return response.json();
}
```

- 统一通过 `services/` 层调用API
- 使用统一的请求封装
- 错误处理统一拦截