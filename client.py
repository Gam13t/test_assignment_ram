import httpx
import asyncio
from urllib.parse import urlencode

class RickAndMortyClient:
    class RickAndMortyURLBuilder:
        """
        Nested class to handle links is a more isolated manner

        We add page query into the base URL because pagination on this page won't let us retrieve all the needed data
        in every possible scenario of usage that I can see.
        """
        
        BASE_URL = 'https://rickandmortyapi.com/api/'
        CHARACTER_PATH = 'character'
        LOCATION_PATH = 'location'
        EPISODE_PATH = 'episode'
        PAGE_QUERY = '?page={page}'
        
        @property
        def character_path(self):
            return f"{self.BASE_URL}{self.CHARACTER_PATH}"

        @property
        def location_path(self):
            return f"{self.BASE_URL}{self.LOCATION_PATH}"

        @property
        def episode_path(self):
            return f"{self.BASE_URL}{self.EPISODE_PATH}"

        def add_query_params(self, path: str, params: dict) -> str:
            """Add query parameters to the URL."""
            query_string = urlencode(params)
            if '?' in path:
                return f"{path}&{query_string}"
            else:
                return f"{path}?{query_string}"    

    INITIAL_PAGE_INDEX = 1
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.urlbuilder = self.RickAndMortyURLBuilder()

    async def fetch_page(self, path: str, page: int):
        """
        Fetch a single page from a given endpoint.
        """
        url = self.urlbuilder.add_query_params(path, {'page': page})
        print(url)
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()


    async def fetch_all_pages(self, path: str):
        """
        Method for asynchronously harvesting all the info from multiple pages for the sources PATH.
        """
        initial_page_data = await self.fetch_page(path, self.INITIAL_PAGE_INDEX)  # Get info from first page to have info on how many pages do we have
        total_pages = initial_page_data['info']['pages']

        # Fetch all the pages concurrently
        tasks = [self.fetch_page(path, page) for page in range(1, total_pages + 1)]
        data = await asyncio.gather(*tasks)

        # combine multiple tasks
        all_results = []

        for page_data in data:
            all_results.extend(page_data['results'])

        print(len(all_results))
        return all_results

    async def fetch_all_characters(self):
        return await self.fetch_all_pages(self.urlbuilder.character_path)

    async def fetch_all_locations(self):
        return await self.fetch_all_pages(self.urlbuilder.location_path)

    async def fetch_all_episodes(self):
        return await self.fetch_all_pages(self.urlbuilder.episode_path)

    async def close(self):
        await self.client.aclose()


# Example usage
if __name__ == '__main__':
    client = RickAndMortyClient()  # Make client instance
    asyncio.run(client.fetch_all_characters())  # Fetch all characters