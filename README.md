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