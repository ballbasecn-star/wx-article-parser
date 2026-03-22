# 项目结构

## 推荐目录结构

```
wx-article-parser/
├── docs/                       # 项目文档
│   ├── product/               # 产品文档
│   ├── architecture/          # 架构文档
│   ├── modules/               # 模块文档
│   ├── roadmap/               # 路线图
│   └── operations/            # 运维文档
│
├── backend/                    # 后端代码
│   ├── src/
│   │   ├── api/               # API路由
│   │   ├── parsers/           # 解析器模块
│   │   ├── extractors/        # 内容提取器
│   │   ├── schemas/           # 请求/响应模型
│   │   ├── services/          # 业务服务
│   │   └── utils/             # 工具函数
│   ├── tests/                 # 后端测试
│   └── requirements.txt       # Python依赖
│
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/        # 通用组件
│   │   ├── pages/             # 页面组件
│   │   ├── services/          # API调用
│   │   ├── hooks/             # 自定义Hooks
│   │   └── utils/             # 工具函数
│   ├── public/                # 静态资源
│   └── package.json           # 前端依赖
│
├── docker/                     # Docker配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── scripts/                    # 脚本工具
│   └── setup.sh
│
├── README.md                   # 项目说明
├── AGENTS.md                   # AI协作说明
└── .gitignore
```

## 各层职责

### 文档层 (docs/)

- **product/**: 产品需求、用户故事
- **architecture/**: 架构设计、技术决策
- **modules/**: 模块详细说明
- **roadmap/**: 开发计划和进度
- **operations/**: 部署和运维文档

### 后端层 (backend/)

- **api/**: HTTP路由和请求处理
- **parsers/**: 文章链接解析逻辑
- **extractors/**: 内容提取逻辑
- **schemas/**: API请求/响应模型定义
- **services/**: 业务逻辑封装
- **utils/**: 通用工具函数

**说明**: MVP阶段不使用数据库，无需数据持久化层。

### 前端层 (frontend/)

- **components/**: 可复用的UI组件
- **pages/**: 页面级组件
- **services/**: API调用封装
- **hooks/**: 自定义React Hooks
- **utils/**: 前端工具函数

## 依赖方向约束

```
前端 (frontend/)
    │ 依赖
    ▼
API接口 (backend/src/api/)
    │ 依赖
    ▼
业务服务 (backend/src/services/)
    │ 依赖
    ▼
解析器/提取器 (backend/src/parsers/, backend/src/extractors/)
    │ 依赖
    ▼
工具层 (backend/src/utils/)
```

## 禁止的跨层调用

- 前端不应直接调用解析器，必须通过API
- API层不应直接操作HTML解析，应调用服务层
- 工具层不应依赖业务层代码