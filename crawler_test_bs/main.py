import aiofiles
import aiocsv
import asyncio
from datetime import timedelta
from crawlee import ConcurrencySettings
from crawlee.configuration import Configuration
from crawlee.crawlers import BeautifulSoupCrawler
from crawlee.events import LocalEventManager
from crawlee.http_clients import ImpitHttpClient
from crawlee.request_loaders import RequestList
from .routes import router

async def load_urls_from_csv(file_path: str):
    """Read URLs from CSV file asynchronously."""
    async with aiofiles.open(file_path, 'r') as file:
        reader = aiocsv.AsyncReader(file)
        # Skip header row
        await reader.__anext__()
        async for row in reader:
            if row:
                yield row[0]  # URL is in the first column
                # Yield control back to the event loop
                await asyncio.sleep(0)

async def main() -> None:
    """The crawler entry point."""
    config = Configuration(
        available_memory_ratio=0.7,
        purge_on_start=False,
    )

    concurrency = ConcurrencySettings(
        max_concurrency=30,
        desired_concurrency=15,
        max_tasks_per_minute=50,
    )

    event_manager = LocalEventManager.from_config(config)

    request_list = RequestList(
        requests=load_urls_from_csv('./crawler_test_bs/lists/202601.csv'),
        persist_requests_key='persist-requests',
        persist_state_key='persist-state',
    )

    request_manager = await request_list.to_tandem()

    crawler = BeautifulSoupCrawler(
        configuration=config,
        concurrency_settings=concurrency,
        event_manager=event_manager,
        request_handler=router,
        request_manager=request_manager,
        navigation_timeout=timedelta(seconds=20),
        request_handler_timeout=timedelta(seconds=20),
        max_request_retries=1,
        max_requests_per_crawl=1000,
        http_client=ImpitHttpClient(),
    )

    await crawler.run()
