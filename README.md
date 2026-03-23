# wx-article-parser

微信公众号文章解析工具 - 解析微信公众号文章，提取内容、图片等信息。

## 核心功能

- 解析微信公众号文章链接
- 提取文章正文内容
- 提取文章中的图片资源
- 导出解析结果

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py

# 使用Docker
docker-compose up -d
```

## 发布脚本

当前仓库已经补齐“本地构建镜像 -> 导出镜像包 -> 上传服务器部署”的三段脚本：

```bash
./scripts/build-release-image.sh
./scripts/export-release-bundle.sh
./scripts/deploy-prebuilt-release.sh
```

## 技术栈

- **后端**: Python
- **前端**: 待定
- **部署**: Docker

## 文档入口

- [产品需求文档](docs/product/prd.md) - 了解产品范围和目标
- [架构概览](docs/architecture/overview.md) - 了解系统设计
- [当前阶段](docs/roadmap/current.md) - 了解开发进度
- [AI协作说明](AGENTS.md) - AI协作开发指南

## 项目结构

```
wx-article-parser/
├── docs/               # 项目文档
├── src/                # 源代码
├── tests/              # 测试代码
├── docker/             # Docker配置
└── scripts/            # 脚本工具
```

## 镜像构建与线上更新

当前仓库的生产发布固定采用“本地构建镜像 -> 本地导出 bundle -> 上传服务器并重启”的方式。

### 前置条件

本地需要具备：

- Docker / Docker Buildx
- `ssh`、`scp`
- 如果使用密码登录，还需要 `sshpass`

服务器默认目录：

```text
/root/apps/parsers/wx-article-parser/
  deploy/
  images/
```

### 1. 准备生产环境文件

```bash
cd /Users/apple/Workspace/linker-platform/parsers/wx-article-parser/deploy
cp .env.prod.example .env.prod
```

至少确认：

- `WX_ARTICLE_PARSER_HOST_PORT`

### 2. 本地构建镜像

```bash
cd /Users/apple/Workspace/linker-platform/parsers/wx-article-parser
IMAGE_TAG=20260323-<git短提交> ./scripts/build-release-image.sh
```

默认镜像名：`ballbase/wx-article-parser`

### 3. 导出镜像 bundle

```bash
cd /Users/apple/Workspace/linker-platform/parsers/wx-article-parser
IMAGE_TAG=20260323-<git短提交> ./scripts/export-release-bundle.sh
```

导出结果默认在：

```text
.tmp/release/<IMAGE_TAG>/
```

### 4. 上传服务器并更新

```bash
cd /Users/apple/Workspace/linker-platform/parsers/wx-article-parser
DEPLOY_HOST=117.72.207.52 \
DEPLOY_USER=root \
DEPLOY_PASSWORD='服务器密码' \
DEPLOY_ENV_FILE=deploy/.env.prod \
IMAGE_TAG=20260323-<git短提交> \
./scripts/deploy-prebuilt-release.sh
```

脚本默认会把服务部署到：

```text
/root/apps/parsers/wx-article-parser
```

### 5. 发布后验证

服务器本机验证：

```bash
curl -sS http://127.0.0.1:8000/api/v1/health
curl -sS http://127.0.0.1:8000/api/v1/capabilities
```

主系统联调验证：

```bash
curl -sS https://linker.ballbase.cloud/api/v1/system/parsers
```

### 6. 回滚

```bash
DEPLOY_HOST=117.72.207.52 \
DEPLOY_USER=root \
DEPLOY_PASSWORD='服务器密码' \
DEPLOY_ENV_FILE=deploy/.env.prod \
IMAGE_TAG=<旧版本号> \
./scripts/deploy-prebuilt-release.sh
```

## 一键发布

如果不想每次手动传部署变量，先在本机准备一次发布配置：

```bash
cd /Users/apple/Workspace/linker-platform/parsers/wx-article-parser/deploy
cp .release.local.env.example .release.local.env
```

之后日常发布直接执行：

```bash
cd /Users/apple/Workspace/linker-platform/parsers/wx-article-parser
./scripts/release-prod.sh
```

常用参数：

- `--image-tag <版本号>`
- `--skip-build`
- `--skip-export`
- `--skip-deploy`
- `--dry-run`
