from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.extractors.content_extractor import ContentExtractor


def test_extract_preserves_inline_wechat_images_in_original_order():
    extractor = ContentExtractor()
    html = """
    <html>
      <body>
        <div id="js_content" class="rich_media_content">
          <p>第一段</p>
          <figure>
            <img
              class="rich_pages wxw-img"
              src="data:image/gif;base64,placeholder"
              data-src="//mmbiz.qpic.cn/mmbiz_jpg/test-image/640?wx_fmt=jpeg&amp;from=appmsg"
            />
          </figure>
          <p>第二段</p>
        </div>
      </body>
    </html>
    """

    result = extractor.extract(html)

    assert result["content"] == "第一段\n第二段"
    assert "第一段" in result["content_html"]
    assert "第二段" in result["content_html"]
    assert result["content_html"].index("第一段") < result["content_html"].index("mmbiz.qpic.cn")
    assert result["content_html"].index("mmbiz.qpic.cn") < result["content_html"].index("第二段")
    assert 'src="https://mmbiz.qpic.cn/mmbiz_jpg/test-image/640?wx_fmt=jpeg&amp;from=appmsg"' in result["content_html"]
    assert 'referrerpolicy="no-referrer"' in result["content_html"]
    assert 'loading="lazy"' in result["content_html"]
    assert 'decoding="async"' in result["content_html"]
    assert 'data-src=' not in result["content_html"]


def test_extract_html_content_keeps_renderable_image_attributes():
    extractor = ContentExtractor()
    html = """
    <html>
      <body>
        <div class="rich_media_content">
          <p>正文</p>
          <img data-original="https://mmbiz.qpic.cn/mmbiz_png/another-image/640?wx_fmt=png" />
        </div>
      </body>
    </html>
    """

    content_html = extractor.extract_html_content(html)

    assert 'src="https://mmbiz.qpic.cn/mmbiz_png/another-image/640?wx_fmt=png"' in content_html
    assert 'referrerpolicy="no-referrer"' in content_html
    assert 'loading="lazy"' in content_html
    assert 'decoding="async"' in content_html
    assert 'data-original=' not in content_html


def test_extract_removes_dark_theme_breaking_inline_styles():
    extractor = ContentExtractor()
    html = """
    <html>
      <body>
        <div class="rich_media_content">
          <p style="color: rgb(0, 0, 0); background-color: rgb(0, 0, 0); text-align: center;">正文仍应可见</p>
        </div>
      </body>
    </html>
    """

    result = extractor.extract(html)

    assert "正文仍应可见" in result["content"]
    assert "color:" not in result["content_html"]
    assert "background-color:" not in result["content_html"]
    assert 'style="text-align: center"' in result["content_html"]
