from crawlee.crawlers import BeautifulSoupCrawlingContext
from crawlee.router import Router

router = Router[BeautifulSoupCrawlingContext]()


@router.default_handler
async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Default request handler."""
    context.log.info(f'Processing {context.request.url} ...')

    url = context.request.url
    headers = dict(context.http_response.headers)
    response_body = await context.http_response.read()

    await context.push_data(
        {
            'url': url,
            'headers': headers,
            'response_body': response_body,
        }
    )

    await context.enqueue_links(
        selector='a',
        strategy='same-domain',
    )
