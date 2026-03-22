"""
解析服务
编排解析流程
"""
import logging
from typing import Optional

from ..parsers.weixin_parser import WeixinParser, ParseResult
from ..utils.url_detector import URLDetector, URLType
from ..schemas.response import ArticleResponse, ArticleMetadata, ArticleMedia

logger = logging.getLogger(__name__)


class ParseService:
    """文章解析服务"""

    def __init__(self):
        """初始化服务"""
        self.url_detector = URLDetector()
        self.weixin_parser = WeixinParser()

    async def parse(self, url: str, include_html: bool = False) -> ArticleResponse:
        """
        解析文章URL

        Args:
            url: 文章链接
            include_html: 是否包含原始HTML

        Returns:
            ArticleResponse: 解析结果
        """
        # 1. URL检测
        url_info = self.url_detector.detect(url)

        if url_info.url_type != URLType.WECHAT:
            return ArticleResponse(
                success=False,
                url=url,
                error={
                    'code': 'INVALID_URL',
                    'message': '请提供有效的微信公众号文章链接'
                }
            )

        # 2. 解析文章
        result = self.weixin_parser.parse(url)

        if not result.success:
            return ArticleResponse(
                success=False,
                url=url,
                error={
                    'code': 'PARSE_ERROR',
                    'message': result.error or '解析失败'
                }
            )

        # 3. 构建响应
        return ArticleResponse(
            success=True,
            title=result.title,
            url=url,
            content=result.content,
            content_html=result.content_html,
            html=result.html if include_html else '',
            metadata=ArticleMetadata(
                author=result.metadata.get('author') if result.metadata else None,
                account_name=result.metadata.get('account_name') if result.metadata else None,
                description=result.metadata.get('description') if result.metadata else None,
                publish_date=result.metadata.get('publish_date') if result.metadata else None,
                article_id=result.metadata.get('article_id') if result.metadata else None,
            ),
            media=ArticleMedia(
                cover_image=result.media.get('cover_image') if result.media else None,
                images=result.media.get('images', []) if result.media else [],
            ),
            processing_time=result.processing_time,
            extraction_method=result.extraction_method
        )

    def is_valid_wechat_url(self, url: str) -> bool:
        """
        验证是否为有效的微信URL

        Args:
            url: URL字符串

        Returns:
            是否有效
        """
        url_info = self.url_detector.detect(url)
        return url_info.url_type == URLType.WECHAT