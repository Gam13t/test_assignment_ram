import httpx
import asyncio
from urllib.parse import urlencode

class RickAndMortyClient:
    """
    Client class to make and proceed with the requests
    """
    class RickAndMortyURLBuilder:
        """
        Nested class to handle links is a more isolated manner
        """
        
        BASE_URL = 'https://rickandmortyapi.com/api/'
        CHARACTER_PATH = 'character'
        LOCATION_PATH = 'location'
        EPISODE_PATH = 'episode'
        
        @property
        def character_path(self):
            return f"{self.BASE_URL}{self.CHARACTER_PATH}"

        @property
        def location_path(self):
            return f"{self.BASE_URL}{self.LOCATION_PATH}"

        @property
        def episode_path(self):
            return f"{self.BASE_URL}{self.EPISODE_PATH}"  

    INITIAL_PAGE_INDEX = 1

    def __init__(self):
        self.client = httpx.AsyncClient()
        self.urlbuilder = self.RickAndMortyURLBuilder()

    async def fetch_page(self, path: str, page: int):
        """
        Fetch a single page from a given endpoint.
        """
        # Pass page as query parameter
        params = {'page': page}
        response = await self.client.get(path, params=params)
        response.raise_for_status()
        return response.json()


    async def fetch_all_pages(self, path: str):
        """
        Method for asynchronously harvesting all the info from multiple pages for the sources PATH.
        
        !Despite we receive the link to the next page with data, I suppose to implement this throught receiving initial_page_data first,
        and bulk process everything afterwards, because otherwise we will be processing pages one by one waiting for the 
        previous page to complete processing before switching to the next one, that, I believe, would drastically decrease the perfomance!
        """
        # Get info from first page to have info on how many pages do we have
        initial_page_data = await self.fetch_page(path, self.INITIAL_PAGE_INDEX)  
        total_pages = initial_page_data['info']['pages']

        # Fetch all the pages concurrently
        tasks = [self.fetch_page(path, page) for page in range(1, total_pages + 1)]
        data = await asyncio.gather(*tasks)

        # combine multiple tasks
        all_results = []

        for page_data in data:
            all_results.extend(page_data['results'])

        return all_results

    async def fetch_all_characters(self):
        return await self.fetch_all_pages(self.urlbuilder.character_path)

    async def fetch_all_locations(self):
        return await self.fetch_all_pages(self.urlbuilder.location_path)

    async def fetch_all_episodes(self):
        return await self.fetch_all_pages(self.urlbuilder.episode_path)

    async def close(self):
        await self.client.aclose()
