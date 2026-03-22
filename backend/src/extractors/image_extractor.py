"""
图片提取器
迁移自 /Users/apple/Project/linker-mind/processors/platforms/weixin_processor.py _build_media_info
"""
import re
import logging
from typing import Dict, Any, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ImageExtractor:
    """微信文章图片提取器"""

    # 微信图片URL模式 - 匹配到常见图片格式参数为止
    WX_IMAGE_PATTERN = r'https?://mmbiz\.qpic\.cn/[^\s"\'<>]+'

    # 无效的图片URL模式
    INVALID_PATTERNS = ['data:image', 'blank.gif', 'loading', 'placeholder']

    # URL末尾需要清理的字符
    TRAILING_CHARS = '"\'\n\r\t\\'

    def extract(self, html: str) -> Dict[str, Any]:
        """
        从HTML中提取图片信息

        Args:
            html: HTML字符串

        Returns:
            包含cover_image和images的字典
        """
        images = []
        cover_image = None

        soup = BeautifulSoup(html, 'lxml')

        # 方法1: 从img标签提取
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and self._is_valid_image_url(src):
                cleaned_url = self._clean_url(src)
                if cleaned_url:
                    images.append(cleaned_url)

        # 方法2: 从微信特定格式提取
        wx_images = re.findall(self.WX_IMAGE_PATTERN, html)
        for img_url in wx_images:
            cleaned_url = self._clean_url(img_url)
            if cleaned_url and cleaned_url not in images:
                images.append(cleaned_url)

        # 去重（保持顺序）
        images = list(dict.fromkeys(images))

        # 封面图：优先从meta获取
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            cover_image = self._clean_url(og_image.get('content'))
        elif images:
            cover_image = images[0]

        return {
            'cover_image': cover_image,
            'images': images[:20],  # 限制最多20张图片
            'image_count': len(images)
        }

    def _clean_url(self, url: str) -> str:
        """
        清理URL，移除末尾的无效字符

        Args:
            url: 原始URL

        Returns:
            清理后的URL
        """
        if not url:
            return ""

        # 移除末尾的无效字符
        url = url.rstrip(self.TRAILING_CHARS)

        # 移除URL中间可能出现的转义引号
        url = url.replace('\x22', '').replace('\\"', '')

        return url.strip()

    def _is_valid_image_url(self, url: str) -> bool:
        """
        验证图片URL是否有效

        Args:
            url: 图片URL

        Returns:
            是否有效
        """
        if not url:
            return False

        url_lower = url.lower()

        # 过滤无效模式
        for pattern in self.INVALID_PATTERNS:
            if pattern in url_lower:
                return False

        # 检查是否为有效URL
        return url_lower.startswith('http')

    def extract_from_markdown(self, markdown: str) -> List[str]:
        """
        从Markdown中提取图片URL

        Args:
            markdown: Markdown文本

        Returns:
            图片URL列表
        """
        img_pattern = r'!\[.*?\]\((.*?)\)'
        images = re.findall(img_pattern, markdown)
        return list(dict.fromkeys(images))  # 去重