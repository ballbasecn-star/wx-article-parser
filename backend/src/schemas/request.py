"""
请求模型定义
"""
from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    """解析请求模型"""
    url: str = Field(..., description="微信公众号文章链接")
    include_html: bool = Field(default=False, description="是否包含原始HTML")
    max_retries: int = Field(default=3, ge=1, le=5, description="最大重试次数")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://mp.weixin.qq.com/s/abc123",
                    "include_html": False,
                    "max_retries": 3
                }
            ]
        }
    }