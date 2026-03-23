"""
API路由定义
"""
from fastapi import APIRouter, Depends, Request

from .parser_contract import (
    UnsupportedUrlError,
    build_capabilities_payload,
    build_health_payload,
    contract_error_response,
    contract_success_response,
    create_request_id,
    extract_language_hint,
    resolve_source_url,
    to_parsed_content_payload,
)
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


@router.get("/v1/health", summary="统一 parser 健康检查")
async def parser_health():
    return contract_success_response(create_request_id(), build_health_payload())


@router.get("/v1/capabilities", summary="统一 parser 能力声明")
async def parser_capabilities():
    return contract_success_response(create_request_id(), build_capabilities_payload())


@router.post("/v1/parse", summary="统一 parser 解析入口")
async def parser_parse(request: Request, service: ParseService = Depends(get_parse_service)):
    payload = await request.json()
    request_id = ((payload or {}).get("requestId") or "").strip() or create_request_id()

    try:
        resolved_url = resolve_source_url(payload)
    except UnsupportedUrlError as exc:
        return contract_error_response(request_id, "UNSUPPORTED_URL", str(exc), 400, retryable=False)
    except ValueError as exc:
        return contract_error_response(request_id, "INVALID_INPUT", str(exc), 400, retryable=False)

    article = await service.parse(resolved_url, include_html=False)
    if not article.success:
        error_code = (article.error or {}).get("code")
        if error_code == "INVALID_URL":
            return contract_error_response(request_id, "UNSUPPORTED_URL", "当前 parser 仅支持微信公众号文章链接", 400, retryable=False)
        return contract_error_response(
            request_id,
            "UPSTREAM_CHANGED",
            (article.error or {}).get("message") or "解析失败",
            422,
            retryable=True,
        )

    parsed_payload = to_parsed_content_payload(article, extract_language_hint(payload))
    return contract_success_response(request_id, parsed_payload)
