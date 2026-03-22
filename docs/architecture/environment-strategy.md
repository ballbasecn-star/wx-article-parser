# 环境策略

## 环境划分

| 环境 | 用途 | 说明 |
|-----|------|------|
| dev | 本地开发调试 | 无状态服务 |
| prod | 正式运行环境 | 无状态服务 |

## 各环境配置

### dev 环境

- **用途**: 本地开发和快速验证
- **配置来源**: 环境变量 / .env.local
- **日志级别**: DEBUG
- **访问方式**: localhost

### prod 环境

- **用途**: 正式运行
- **配置来源**: 环境变量
- **日志级别**: INFO/WARNING
- **访问方式**: 正式域名

## 配置隔离原则

### 环境变量

所有环境相关配置通过环境变量管理：

```bash
# 应用配置
APP_ENV=dev|prod
APP_DEBUG=true|false
APP_PORT=8000

# 前端配置
VITE_API_URL=http://localhost:8000
```

### 配置文件

- `.env.example`: 配置模板，提交到仓库
- `.env.local`: 本地配置，不提交
- `.env.prod`: 生产配置，通过部署平台管理

## 无状态服务说明

本服务为无状态服务：
- 解析结果直接返回，不做持久化存储
- 不需要数据库或持久化存储
- 可随时扩容或重启

## 镜像版本策略

- 开发环境: 使用本地代码挂载
- 生产环境: 使用构建后的Docker镜像
- 镜像标签: 使用 git commit hash 或版本号

## 环境切换

```bash
# 本地开发
docker-compose up

# 生产部署
docker-compose -f docker-compose.prod.yml up -d
```