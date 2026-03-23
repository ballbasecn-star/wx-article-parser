"""统一 parser 契约适配。"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi.responses import JSONResponse

from ..schemas.response import ArticleResponse
from ..utils.url_detector import URLDetector

PARSER_VERSION = "0.1.0"
_URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)


class UnsupportedUrlError(ValueError):
    """输入链接不属于当前 parser。"""


def create_request_id() -> str:
    return f"req_{uuid4().hex}"


def contract_success_response(request_id: str, data: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None,
            "meta": {
                "requestId": request_id,
                "parserVersion": PARSER_VERSION,
            },
        },
    )


def contract_error_response(
    request_id: str,
    code: str,
    message: str,
    status_code: int,
    retryable: bool,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "retryable": retryable,
            },
            "meta": {
                "requestId": request_id,
                "parserVersion": PARSER_VERSION,
            },
        },
    )


def build_health_payload() -> dict[str, str]:
    return {"status": "UP"}


def build_capabilities_payload() -> dict[str, Any]:
    return {
        "platform": "weixin_article",
        "supportedSourceTypes": ["article", "share_text"],
        "features": {
            "transcript": False,
            "images": True,
            "metrics": False,
            "authorProfile": False,
            "deepAnalysis": False,
            "batchParse": False,
            "asyncParse": False,
        },
    }


def resolve_source_url(payload: Optional[dict]) -> str:
    if not payload:
        raise ValueError("请提供 JSON 数据")

    input_payload = payload.get("input") or {}
    source_text = (input_payload.get("sourceText") or "").strip()
    source_url = (input_payload.get("sourceUrl") or "").strip()
    resolved_source = source_url or extract_url_from_text(source_text)

    if not resolved_source:
        raise ValueError("sourceText 和 sourceUrl 不能同时为空")
    if not URLDetector().is_wechat_url(resolved_source):
        raise UnsupportedUrlError("当前 parser 仅支持微信公众号文章链接")
    return resolved_source


def extract_language_hint(payload: Optional[dict]) -> Optional[str]:
    return ((payload or {}).get("options") or {}).get("languageHint") or None


def to_parsed_content_payload(article: ArticleResponse, language_hint: Optional[str]) -> dict[str, Any]:
    warnings = []
    if not article.media.images and not article.media.cover_image:
        warnings.append(
            {
                "code": "MEDIA_UNAVAILABLE",
                "message": "当前返回未包含图片资源。",
            }
        )

    return {
        "platform": "weixin_article",
        "sourceType": "article",
        "externalId": article.metadata.article_id,
        "canonicalUrl": article.url,
        "title": article.title,
        "summary": article.metadata.description,
        "author": {
            "externalAuthorId": None,
            "name": article.metadata.account_name,
            "handle": article.metadata.account_name,
            "profileUrl": None,
            "avatarUrl": None,
        },
        "publishedAt": normalize_datetime(article.metadata.publish_date),
        "language": language_hint,
        "content": {
            "rawText": article.content or None,
            "transcript": None,
            "segments": [],
        },
        "metrics": {
            "views": None,
            "likes": None,
            "comments": None,
            "shares": None,
            "favorites": None,
        },
        "tags": article.metadata.tags,
        "media": {
            "covers": compact_media([media_item(article.media.cover_image, "image/jpeg")]),
            "images": compact_media([media_item(url, None) for url in article.media.images]),
            "videos": [],
            "audios": [],
        },
        "rawPayload": {
            "contentHtml": article.content_html,
            "extractionMethod": article.extraction_method,
            "processingTime": article.processing_time,
        },
        "warnings": warnings,
    }


def extract_url_from_text(source_text: str) -> str:
    match = _URL_PATTERN.search(source_text)
    return match.group(0) if match else ""


def media_item(url: Optional[str], mime_type: Optional[str]) -> Optional[dict[str, Any]]:
    if not url:
        return None
    return {
        "url": url,
        "mimeType": mime_type,
        "width": None,
        "height": None,
        "durationMs": None,
    }


def compact_media(items: list[Optional[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [item for item in items if item]


def normalize_datetime(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    value = value.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            continue
    return None
