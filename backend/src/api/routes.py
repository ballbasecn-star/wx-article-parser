"""
API路由定义
"""
from fastapi import APIRouter, Depends

from ..schemas.request import ParseRequest
from ..schemas.response import ArticleResponse, HealthResponse
from ..services.parse_service import ParseService

router = APIRouter(prefix="/api", tags=["parse"])


def get_parse_service() -> ParseService:
    """依赖注入：获取解析服务"""
    return ParseService()


@router.post(
    "/parse",
    response_model=ArticleResponse,
    summary="解析微信公众号文章",
    description="解析微信公众号文章链接，提取标题、正文、图片等内容"
)
async def parse_article(
    request: ParseRequest,
    service: ParseService = Depends(get_parse_service)
) -> ArticleResponse:
    """
    解析微信公众号文章

    - **url**: 微信公众号文章链接（必须以 https://mp.weixin.qq.com/s/ 开头）
    - **include_html**: 是否包含原始HTML（可选，默认false）
    - **max_retries**: 最大重试次数（可选，默认3）
    """
    return await service.parse(request.url, request.include_html)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务是否正常运行"
)
async def health_check() -> HealthResponse:
    """健康检查"""
    return HealthResponse(status="healthy", service="wx-article-parser")