# 后端架构

## 技术栈

- **语言**: Python 3.10+
- **框架**: FastAPI（推荐）/ Flask
- **HTML解析**: BeautifulSoup4 / lxml
- **HTTP客户端**: httpx / requests
- **异步支持**: asyncio

**说明**: MVP阶段不使用数据库，解析结果直接返回，不做持久化存储。

## 目录结构

```
backend/
├── src/
│   ├── api/               # API路由
│   │   ├── __init__.py
│   │   ├── routes.py      # 路由定义
│   │   └── schemas.py     # 请求/响应模型
│   ├── parsers/           # 解析器模块
│   │   ├── __init__.py
│   │   └── article_parser.py
│   ├── extractors/        # 内容提取器
│   │   ├── __init__.py
│   │   ├── content_extractor.py
│   │   └── image_extractor.py
│   ├── services/          # 业务服务
│   │   ├── __init__.py
│   │   └── parse_service.py
│   ├── schemas/           # 请求/响应模型
│   │   ├── __init__.py
│   │   └── article.py
│   ├── utils/             # 工具函数
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── main.py            # 应用入口
├── tests/                 # 测试代码
│   ├── test_parsers/
│   └── test_extractors/
└── requirements.txt       # 依赖列表
```

## API设计原则

### RESTful风格

```
POST /api/parse          # 解析文章
GET  /api/health         # 健康检查
```

### 统一响应格式

```json
{
  "success": true,
  "data": {
    "title": "文章标题",
    "author": "作者",
    "content": "正文内容",
    "images": ["图片URL1", "图片URL2"]
  },
  "error": null
}
```

### 错误处理

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PARSE_ERROR",
    "message": "无法解析该链接"
  }
}
```

## 核心模块设计

### 解析器 (parsers/)

负责获取公众号文章HTML并初步解析：

```python
class ArticleParser:
    async def fetch(self, url: str) -> str:
        """获取文章HTML"""
        pass

    def validate_url(self, url: str) -> bool:
        """验证URL格式"""
        pass
```

### 提取器 (extractors/)

负责从HTML中提取结构化内容：

```python
class ContentExtractor:
    def extract_title(self, html: str) -> str:
        """提取标题"""
        pass

    def extract_content(self, html: str) -> str:
        """提取正文"""
        pass

class ImageExtractor:
    def extract_images(self, html: str) -> list[str]:
        """提取图片列表"""
        pass
```

### 服务层 (services/)

封装业务逻辑：

```python
class ParseService:
    async def parse_article(self, url: str) -> ArticleSchema:
        """完整解析流程，直接返回结果"""
        html = await self.parser.fetch(url)
        title = self.content_extractor.extract_title(html)
        content = self.content_extractor.extract_content(html)
        images = self.image_extractor.extract_images(html)
        return ArticleSchema(title=title, content=content, images=images)
```

## 依赖方向

```
api/ → services/ → parsers/ / extractors/ → utils/
```

- API层处理请求响应
- Services层编排业务流程
- Parsers/Extractors层处理具体解析
- Utils层提供通用工具