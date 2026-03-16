import asyncio
import csv
from datetime import timedelta
from crawlee.configuration import Configuration
from crawlee.crawlers import BeautifulSoupCrawler
from crawlee.events import LocalEventManager
from crawlee.http_clients import ImpitHttpClient
from crawlee.request_loaders import RequestList
from .routes import router

async def load_urls_from_csv(file_path: str):  
    """Read URLs from CSV file."""
    def read_csv():
        with open(file_path, 'r') as file:  
            reader = csv.reader(file)  
            next(reader, None)  # Skip header row
            for row in reader:  
                if row:
                    yield row[0]  # URL is in the first column

    # Convert the synchronous generator into an async-friendly stream
    for url in read_csv():
        yield url
        # Yield control back to the event loop to keep the crawler responsive
        await asyncio.sleep(0)

async def main() -> None:
    """The crawler entry point."""
    config = Configuration(
        available_memory_ratio=0.7,
    )

    event_manager = LocalEventManager.from_config(config)

    request_list = RequestList(load_urls_from_csv('./crawler_test/lists/202601.csv'))

    request_manager = await request_list.to_tandem()

    crawler = BeautifulSoupCrawler(
        configuration=config,
        event_manager=event_manager,
        request_handler=router,
        request_manager=request_manager,
        navigation_timeout=timedelta(seconds=30),
        request_handler_timeout=timedelta(seconds=30),
        max_request_retries=1,
        max_requests_per_crawl=1000,
        http_client=ImpitHttpClient(),
    )

    await crawler.run()
