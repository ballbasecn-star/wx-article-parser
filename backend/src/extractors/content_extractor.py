"""
内容提取器
迁移自 /Users/apple/Project/linker-mind/processors/platforms/weixin_processor.py
包含:
- _extract_script_data
- _extract_meta_tags
- _extract_html_structure
- _normalize_weixin_msg_data
"""
import re
import json
import logging
from html import unescape
from typing import Dict, Any, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ContentExtractor:
    """微信文章内容提取器

    采用三层提取策略:
    1. script数据提取（微信msg变量）
    2. meta标签提取
    3. HTML结构提取
    """

    # 微信文章内容区域可能的class名
    CONTENT_CLASSES = [
        'rich_media_content',
        'rich_media_area',
        'wx_rich_media_content',
        'js_content',
        'article-content',
    ]
    CONTENT_IDS = ['js_content', 'content']
    IMAGE_SOURCE_ATTRS = [
        'data-src',
        'data-actualsrc',
        'data-original-src',
        'data-original',
        'src',
    ]
    IMAGE_SOURCE_ALIASES = [
        'data-src',
        'data-actualsrc',
        'data-original-src',
        'data-original',
    ]
    STYLE_BLOCKLIST = {
        'color',
        'background',
        'background-color',
        'background-image',
        'background-repeat',
        'background-position',
        'background-size',
        'background-attachment',
        'background-origin',
        'background-clip',
        'opacity',
        'visibility',
        'filter',
        'mix-blend-mode',
        '-webkit-text-fill-color',
        '-webkit-background-clip',
        'display',
    }

    # 公众号名称可能的class名
    ACCOUNT_CLASSES = ['account_name', 'rich_meta_title', 'wx_account_name', 'rich_media_meta_nickname']

    def extract(self, html: str) -> Dict[str, Any]:
        """
        从HTML中提取内容

        Args:
            html: HTML字符串

        Returns:
            提取结果字典，包含:
            - title: 标题
            - content: 纯文本内容
            - content_html: HTML内容（保留图片和排版）
            - author, account_name, description 等元数据
        """
        soup = BeautifulSoup(html, 'lxml')
        result = {}

        # 第一层: script数据提取（优先级最高）
        script_data = self._extract_from_script(soup)
        if script_data:
            result.update(script_data)
            result['_extraction_source'] = 'script'

        # 第二层: meta标签提取
        if not result.get('title') or not result.get('content'):
            meta_data = self._extract_from_meta(soup)
            result.update(meta_data)
            if not result.get('_extraction_source'):
                result['_extraction_source'] = 'meta'

        # 第三层: HTML结构提取（核心修改：提取HTML内容）
        html_data = self._extract_from_html(soup)
        result.update(html_data)
        if not result.get('_extraction_source'):
            result['_extraction_source'] = 'html'

        # 确保有标题
        if not result.get('title'):
            title_elem = soup.find('title')
            if title_elem:
                result['title'] = title_elem.get_text(strip=True)

        return result

    def extract_html_content(self, html: str) -> str:
        """
        提取文章HTML内容（保留图片和排版）

        关键处理：
        1. 提取 rich_media_content 区域
        2. 将 data-src 转换为 src（微信图片使用data-src）
        3. 清理不必要的属性和标签

        Args:
            html: 原始HTML字符串

        Returns:
            处理后的HTML字符串
        """
        soup = BeautifulSoup(html, 'lxml')

        # 查找内容区域
        content_elem = self._find_content_element(soup)

        if not content_elem:
            return ""

        self._normalize_image_tags(content_elem)
        self._sanitize_content_styles(content_elem)

        # 清理一些不必要的属性
        for tag in content_elem.find_all(True):
            # 保留基本属性
            attrs_to_keep = [
                'src',
                'href',
                'alt',
                'class',
                'id',
                'style',
                'referrerpolicy',
                'loading',
                'decoding',
            ]
            attrs = dict(tag.attrs)
            for attr in attrs:
                if attr not in attrs_to_keep:
                    del tag[attr]

        return str(content_elem)

    def _extract_from_script(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        从script标签提取数据

        微信文章通常在script标签中有msg变量，包含文章元数据
        """
        for script in soup.find_all('script'):
            if not script.string:
                continue

            # 查找msg变量
            msg_match = re.search(r'var msg = ({.+?});', script.string, re.DOTALL)
            if msg_match:
                try:
                    data = json.loads(msg_match.group(1))
                    if isinstance(data, dict):
                        return self._normalize_msg_data(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse msg data: {e}")

            # 查找其他常见格式
            for pattern in [
                r'window\.msg\s*=\s*({.+?});',
                r'ct\s*=\s*({.+?});',
            ]:
                match = re.search(pattern, script.string, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        if isinstance(data, dict):
                            return self._normalize_msg_data(data)
                    except json.JSONDecodeError:
                        pass

        return {}

    def _normalize_msg_data(self, data: Dict) -> Dict[str, Any]:
        """
        标准化微信msg数据

        Args:
            data: 原始msg数据

        Returns:
            标准化后的数据
        """
        result = {}

        # 标题
        if 'title' in data:
            result['title'] = data['title']

        # 内容
        if 'content' in data:
            result['content'] = data['content']

        # 作者信息
        if 'author' in data:
            author = data['author']
            if isinstance(author, dict):
                result['author'] = author.get('nickname', '')
                result['account_name'] = author.get('public_name', '')
            else:
                result['author'] = str(author)

        # 发布时间
        for time_key in ['publish_time', 'create_time']:
            if time_key in data:
                result['publish_date'] = data[time_key]
                break

        # 文章ID
        for id_key in ['article_id', 'itemid']:
            if id_key in data:
                result['article_id'] = data[id_key]
                break

        # 封面图
        for img_key in ['cover', 'cdn_url']:
            if img_key in data:
                result['cover_image'] = data[img_key]
                break

        return result

    def _extract_from_meta(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """从meta标签提取数据"""
        result = {}

        # 字段到meta标签的映射
        meta_mappings = {
            'title': ['og:title', 'twitter:title'],
            'description': ['og:description', 'twitter:description', 'description'],
            'author': ['og:article:author', 'article:author', 'author'],
            'cover_image': ['og:image', 'twitter:image'],
            'publish_date': ['og:article:published_time', 'article:published_time'],
        }

        for field, meta_names in meta_mappings.items():
            for meta_name in meta_names:
                # 先尝试property属性
                meta = soup.find('meta', property=meta_name)
                if meta and meta.get('content'):
                    result[field] = meta.get('content')
                    break
                # 再尝试name属性
                meta = soup.find('meta', attrs={'name': meta_name})
                if meta and meta.get('content'):
                    result[field] = meta.get('content')
                    break

        return result

    def _extract_from_html(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """从HTML结构提取数据"""
        result = {}

        # 查找内容区域
        content_elem = self._find_content_element(soup)

        if content_elem:
            self._normalize_image_tags(content_elem)
            self._sanitize_content_styles(content_elem)
            # 提取纯文本
            result['content'] = content_elem.get_text('\n', strip=True)
            result['content_html'] = str(content_elem)

        # 标题
        if not result.get('title'):
            title_elem = soup.find('h1', class_='rich_media_title')
            if title_elem:
                result['title'] = title_elem.get_text(strip=True)

        # 公众号名称
        for class_name in self.ACCOUNT_CLASSES:
            elem = soup.find('a', class_=class_name) or soup.find('span', class_=class_name)
            if elem:
                result['account_name'] = elem.get_text(strip=True)
                break

        return result

    def _find_content_element(self, soup: BeautifulSoup) -> Optional[Any]:
        """定位正文根节点"""
        content_elem = None

        for class_name in self.CONTENT_CLASSES:
            content_elem = soup.find('div', class_=class_name)
            if content_elem:
                return content_elem

        for elem_id in self.CONTENT_IDS:
            content_elem = soup.find('div', id=elem_id)
            if content_elem:
                return content_elem

        return None

    def _normalize_image_tags(self, content_elem: Any) -> None:
        """标准化微信文章中的图片节点，确保浏览器可直接渲染。"""
        for img in content_elem.find_all('img'):
            image_url = self._extract_image_url(img)
            if not image_url:
                continue

            img['src'] = image_url
            img['referrerpolicy'] = 'no-referrer'
            img['loading'] = img.get('loading') or 'lazy'
            img['decoding'] = img.get('decoding') or 'async'
            if not img.get('alt'):
                img['alt'] = '文章图片'

            for attr in self.IMAGE_SOURCE_ALIASES:
                if attr in img.attrs:
                    del img.attrs[attr]

    def _extract_image_url(self, img: Any) -> str:
        """从微信图片节点提取可渲染的图片地址。"""
        for attr in self.IMAGE_SOURCE_ATTRS:
            candidate = img.get(attr)
            cleaned = self._normalize_image_url(candidate)
            if cleaned:
                return cleaned

        return ""

    def _normalize_image_url(self, url: Optional[str]) -> str:
        """清理并标准化图片地址。"""
        if not url:
            return ""

        normalized = unescape(str(url)).strip()
        if not normalized or normalized.lower().startswith('data:image'):
            return ""

        if normalized.startswith('//'):
            normalized = f'https:{normalized}'

        return normalized

    def _sanitize_content_styles(self, content_elem: Any) -> None:
        """移除会让深色主题正文不可见的危险内联样式。"""
        for tag in content_elem.find_all(True):
            style = tag.get('style')
            if not style:
                continue

            sanitized_style = self._sanitize_style_value(style)
            if sanitized_style:
                tag['style'] = sanitized_style
            else:
                del tag['style']

    def _sanitize_style_value(self, style: str) -> str:
        """过滤掉会隐藏正文或把正文渲染成黑底黑字的样式。"""
        safe_rules = []

        for raw_rule in style.split(';'):
            rule = raw_rule.strip()
            if not rule or ':' not in rule:
                continue

            property_name, value = rule.split(':', 1)
            property_name = property_name.strip().lower()
            value = value.strip()

            if not value or property_name in self.STYLE_BLOCKLIST:
                continue

            safe_rules.append(f'{property_name}: {value}')

        return '; '.join(safe_rules)

    def extract_author(self, text: str) -> str:
        """
        从文本中提取作者

        Args:
            text: 文本内容

        Returns:
            作者名
        """
        patterns = [
            r'作者[：:]\s*([^\s@]+)',
            r'Author[：:]\s*([^\s@]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text[:3000], re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def extract_account_name(self, text: str) -> str:
        """
        从文本中提取公众号名称

        Args:
            text: 文本内容

        Returns:
            公众号名称
        """
        patterns = [
            r'公众号[：:]\s*([^\s@]+)',
            r'来自[:\s]+([^\s@]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text[:2000])
            if match:
                return match.group(1).strip()

        return ""
