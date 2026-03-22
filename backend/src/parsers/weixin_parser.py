"""
微信解析器
迁移自 /Users/apple/Project/linker-mind/processors/platforms/weixin_processor.py
简化版：只保留requests方式，移除MCP WebReader和Firecrawl
"""
import time
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

import requests

from ..extractors.content_extractor import ContentExtractor
from ..extractors.image_extractor import ImageExtractor

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """解析结果"""
    success: bool
    title: str = ""
    content: str = ""
    content_html: str = ""  # HTML内容（保留图片和排版）
    html: str = ""
    metadata: Dict[str, Any] = None
    media: Dict[str, Any] = None
    extraction_method: str = ""
    error: str = ""
    processing_time: float = 0


class WeixinParser:
    """微信公众号文章解析器

    MVP版本: 使用requests获取HTML，支持重试机制
    """

    # 默认请求头（模拟移动端）
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://mp.weixin.qq.com/',
    }

    def __init__(self, timeout: int = 15, max_retries: int = 3):
        """
        初始化解析器

        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.content_extractor = ContentExtractor()
        self.image_extractor = ImageExtractor()

    def parse(self, url: str) -> ParseResult:
        """
        解析微信文章

        Args:
            url: 文章URL

        Returns:
            ParseResult对象
        """
        start_time = time.time()

        try:
            # 获取HTML
            html = self._fetch_html(url)

            # 提取内容（包含 content_html）
            content_data = self.content_extractor.extract(html)

            # 提取图片
            image_data = self.image_extractor.extract(html)

            # 构建元数据
            metadata = {
                'author': content_data.get('author'),
                'account_name': content_data.get('account_name'),
                'description': content_data.get('description'),
                'publish_date': content_data.get('publish_date'),
                'article_id': content_data.get('article_id'),
            }

            # 如果没有从内容提取到作者，尝试从文本提取
            if not metadata.get('author'):
                metadata['author'] = self.content_extractor.extract_author(
                    content_data.get('content', '')
                )

            processing_time = time.time() - start_time

            return ParseResult(
                success=True,
                title=content_data.get('title', ''),
                content=content_data.get('content', ''),
                content_html=content_data.get('content_html', ''),
                html=html,
                metadata=metadata,
                media=image_data,
                extraction_method=content_data.get('_extraction_source', 'unknown'),
                processing_time=round(processing_time, 3)
            )

        except Exception as e:
            logger.error(f"Parse error for {url}: {e}")
            return ParseResult(
                success=False,
                error=str(e),
                processing_time=round(time.time() - start_time, 3)
            )

    def _fetch_html(self, url: str) -> str:
        """
        获取文章HTML（带重试）

        Args:
            url: 文章URL

        Returns:
            HTML字符串

        Raises:
            RuntimeError: 获取失败
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.DEFAULT_HEADERS,
                    timeout=self.timeout
                )
                response.raise_for_status()
                response.encoding = 'utf-8'

                # 验证内容长度
                if len(response.text) < 100:
                    raise ValueError("Response too short, possibly blocked")

                return response.text

            except requests.RequestException as e:
                last_error = e
                logger.warning(f"Fetch attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
            except ValueError as e:
                last_error = e
                logger.warning(f"Content validation failed: {e}")
                raise

        raise RuntimeError(
            f"Failed to fetch HTML after {self.max_retries} attempts: {last_error}"
        )

    def parse_article_id(self, url: str) -> Optional[str]:
        """
        从URL解析文章ID

        Args:
            url: 文章URL

        Returns:
            文章ID或None
        """
        match = self.ARTICLE_ID_PATTERN.search(url)
        return match.group(1) if match else None

    # 文章ID正则
    ARTICLE_ID_PATTERN = __import__('re').compile(r'/s/([A-Za-z0-9_-]+)')