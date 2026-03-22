"""
响应模型定义
迁移自 /Users/apple/Project/linker-mind/processors/content_processor.py ProcessedContent
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ArticleMetadata(BaseModel):
    """文章元数据"""
    author: Optional[str] = Field(default=None, description="作者")
    account_name: Optional[str] = Field(default=None, description="公众号名称")
    description: Optional[str] = Field(default=None, description="文章摘要")
    publish_date: Optional[str] = Field(default=None, description="发布时间")
    article_id: Optional[str] = Field(default=None, description="文章ID")
    tags: List[str] = Field(default_factory=list, description="标签列表")


class ArticleMedia(BaseModel):
    """媒体信息"""
    cover_image: Optional[str] = Field(default=None, description="封面图")
    images: List[str] = Field(default_factory=list, description="图片列表")


class ArticleResponse(BaseModel):
    """文章解析响应"""
    success: bool = Field(default=True, description="是否成功")
    title: str = Field(default="", description="文章标题")
    url: str = Field(default="", description="原始URL")
    content: str = Field(default="", description="正文内容（纯文本）")
    content_html: str = Field(default="", description="正文内容（HTML格式，保留图片和排版）")
    html: str = Field(default="", description="原始HTML")
    metadata: ArticleMetadata = Field(default_factory=ArticleMetadata, description="元数据")
    media: ArticleMedia = Field(default_factory=ArticleMedia, description="媒体信息")
    processing_time: float = Field(default=0, description="处理时间(秒)")
    extraction_method: str = Field(default="", description="提取方法")
    error: Optional[Dict[str, str]] = Field(default=None, description="错误信息")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "title": "文章标题",
                    "url": "https://mp.weixin.qq.com/s/xxx",
                    "content": "正文内容...",
                    "html": "",
                    "metadata": {
                        "author": "作者名",
                        "account_name": "公众号名称",
                        "description": "文章摘要",
                        "publish_date": "2024-01-01",
                        "article_id": "xxx",
                        "tags": []
                    },
                    "media": {
                        "cover_image": "https://...",
                        "images": ["https://..."]
                    },
                    "processing_time": 1.234,
                    "extraction_method": "script"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="healthy", description="服务状态")
    service: str = Field(default="wx-article-parser", description="服务名称")