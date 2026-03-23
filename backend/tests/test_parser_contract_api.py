from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.main import app
from src.schemas.response import ArticleMedia, ArticleMetadata, ArticleResponse

client = TestClient(app)


def test_parser_health_returns_contract_envelope():
    response = client.get('/api/v1/health')

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    assert body['data']['status'] == 'UP'
    assert body['error'] is None
    assert 'requestId' in body['meta']


def test_parser_capabilities_returns_contract_payload():
    response = client.get('/api/v1/capabilities')

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    assert body['data']['platform'] == 'weixin_article'
    assert 'article' in body['data']['supportedSourceTypes']


@patch('src.api.routes.ParseService.parse', new_callable=AsyncMock)
def test_parser_parse_returns_contract_payload(mock_parse):
    mock_parse.return_value = ArticleResponse(
        success=True,
        title='测试文章',
        url='https://mp.weixin.qq.com/s/test-article',
        content='正文内容',
        content_html='<p>正文内容</p>',
        metadata=ArticleMetadata(
            author='作者',
            account_name='测试公众号',
            description='摘要',
            publish_date='2026-03-23',
            article_id='test-article',
            tags=['AI'],
        ),
        media=ArticleMedia(
            cover_image='https://example.com/cover.jpg',
            images=['https://example.com/1.jpg'],
        ),
        extraction_method='script',
    )

    response = client.post(
        '/api/v1/parse',
        json={
            'requestId': 'req_wechat_parse',
            'input': {
                'sourceText': '看看这篇文章 https://mp.weixin.qq.com/s/test-article',
                'platformHint': 'weixin_article',
            },
            'options': {
                'languageHint': 'zh-CN',
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    assert body['data']['externalId'] == 'test-article'
    assert body['data']['canonicalUrl'] == 'https://mp.weixin.qq.com/s/test-article'
    assert body['meta']['requestId'] == 'req_wechat_parse'


def test_parser_parse_rejects_unsupported_url():
    response = client.post(
        '/api/v1/parse',
        json={
            'requestId': 'req_bad_url',
            'input': {
                'sourceUrl': 'https://example.com/not-wechat',
            },
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body['success'] is False
    assert body['error']['code'] == 'UNSUPPORTED_URL'
