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
from ..services.parse_service import ParseService

router = APIRouter(prefix="/api", tags=["parse"])


def get_parse_service() -> ParseService:
    """依赖注入：获取解析服务"""
    return ParseService()


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
