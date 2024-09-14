import httpx
import asyncio
from aiologger import Logger
from aiologger.levels import LogLevel
from urllib.parse import urlencode

from exceptions import RequestException
from logger import formatter

logger = Logger.with_default_handlers(name=__name__, level=LogLevel.WARNING)
for handler in logger.handlers:
    handler.formatter = formatter

class RickAndMortyClient:
    """
    Client class to handle requests to the Rick and Morty API.
    """
    BASE_URL = 'https://rickandmortyapi.com/api/'
    CHARACTER_PATH = 'character'
    LOCATION_PATH = 'location'
    EPISODE_PATH = 'episode'

    INITIAL_PAGE_INDEX = 1

    def __init__(
        self,
        read_timeout: float = 2.0,
        connect_timeout: float = 5.0,
        max_retries: int = 5,
        retry_timeout: float = 2.0,
    ):
        self.max_retries = max_retries
        self.retry_timeout = retry_timeout
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(read_timeout, connect=connect_timeout))

    async def fetch_page_with_retry(self, path: str, page: int):
        """
        Fetch a single page from a given endpoint with retry logic.
        """
        retries = 0
        params = {'page': page}
        exception = None

        while retries < self.max_retries:
            try:
                response = await self.client.get(path, params=params)
                response.raise_for_status()
                await logger.info(f'Data from {response.url} has been obtained successfully.')
                return response.json()
            except (httpx.TimeoutException, httpx.HTTPError, httpx.ConnectError) as exc: 
                retries += 1
                exception = exc
                await logger.warning(f'HTTP Exception for {exc.request.url} - {exc}, Retries left: {self.max_retries - retries}')
                await asyncio.sleep(self.retry_timeout)
        raise RequestException("RequestException: One or more courutines were unable to retrieve data", original_exception=exception)

    async def fetch_all_pages(self, path: str):
        """
        Fetch all pages from a given endpoint concurrently.
        
        !Despite we receive the link to the next page with data, I suppose to implement this throught receiving initial_page_data first,
        and bulk process everything afterwards, because otherwise we will be processing pages one by one waiting for the 
        previous page to complete processing before switching to the next one, that, I believe, would drastically decrease the perfomance!
        """
        # Get info from first page to have info on how many pages do we have
        initial_page_data = await self.fetch_page_with_retry(path, self.INITIAL_PAGE_INDEX)  
        total_pages = initial_page_data['info']['pages']

        # Fetch all the pages concurrently
        tasks = [self.fetch_page_with_retry(path, page) for page in range(1, total_pages + 1)]
        data = await asyncio.gather(*tasks)

        # combine multiple tasks
        all_results = [item for page_data in data for item in page_data['results']]
        return all_results

    async def fetch_all_characters(self):
        return await self.fetch_all_pages(f"{self.BASE_URL}{self.CHARACTER_PATH}")

    async def fetch_all_locations(self):
        return await self.fetch_all_pages(f"{self.BASE_URL}{self.LOCATION_PATH}")

    async def fetch_all_episodes(self):
        return await self.fetch_all_pages(f"{self.BASE_URL}{self.EPISODE_PATH}")

    async def close(self):
        await self.client.aclose()
