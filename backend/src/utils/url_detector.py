"""
URL检测模块
迁移自 /Users/apple/Project/linker-mind/url_detector.py
"""
import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class URLType(Enum):
    """URL类型枚举"""
    WECHAT = "wechat"
    UNKNOWN = "unknown"


class URLInfo(BaseModel):
    """URL信息"""
    url: str
    url_type: URLType
    article_id: Optional[str] = None
    is_valid: bool = True


class URLDetector:
    """微信URL检测器"""

    # 微信公众号文章URL模式
    WECHAT_PATTERNS = [
        r'https?://mp\.weixin\.qq\.com/s/([A-Za-z0-9_-]+)',
        r'https?://mp\.weixin\.qq\.com/s\?__biz=',
    ]

    def __init__(self):
        """初始化编译好的正则表达式"""
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.WECHAT_PATTERNS
        ]

    def detect(self, url: str) -> URLInfo:
        """
        检测URL类型

        Args:
            url: URL字符串

        Returns:
            URLInfo对象
        """
        url = url.strip()

        for i, pattern in enumerate(self._compiled_patterns):
            match = pattern.match(url)
            if match:
                article_id = None
                if i == 0 and match.groups():
                    article_id = match.group(1)

                return URLInfo(
                    url=url,
                    url_type=URLType.WECHAT,
                    article_id=article_id
                )

        return URLInfo(
            url=url,
            url_type=URLType.UNKNOWN,
            is_valid=False
        )

    def is_wechat_url(self, url: str) -> bool:
        """
        判断是否为微信URL

        Args:
            url: URL字符串

        Returns:
            是否为微信URL
        """
        return 'mp.weixin.qq.com' in url.lower()

    def extract_article_id(self, url: str) -> Optional[str]:
        """
        从URL提取文章ID

        Args:
            url: URL字符串

        Returns:
            文章ID或None
        """
        match = re.search(r'/s/([A-Za-z0-9_-]+)', url)
        if match:
            return match.group(1)
        return None


# 单例实例
_detector_instance: Optional[URLDetector] = None


def get_detector() -> URLDetector:
    """获取URL检测器单例"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = URLDetector()
    return _detector_instance


def detect_url(url: str) -> URLInfo:
    """
    便捷函数：检测单个URL

    Args:
        url: URL字符串

    Returns:
        URLInfo对象
    """
    return get_detector().detect(url)