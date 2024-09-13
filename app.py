import json
import asyncio 
import aiofiles
from uuid import uuid4
from aiologger import Logger
from aiologger.levels import LogLevel
from datetime import datetime

from client import RickAndMortyClient
from logger import formatter
from exceptions import RequestException

logger = Logger.with_default_handlers(name=__name__, level=LogLevel.INFO)
for handler in logger.handlers:
    handler.formatter = formatter

class RickAndMortyApp():
    """
    App class to collect and serialize data we retrieve from the client
    """
    CHARACTERS_FILE = 'characters.json'
    LOCAITONS_FILE = 'locations.json'
    EPISODES_FILE = 'episodes.json'

    def __init__(self):
        self.client = RickAndMortyClient()

    async def save_to_json(self, data, file_name):
        """
        Save data to a JSON file.
        """
        try:
            async with aiofiles.open(file_name, 'w') as file:
                await file.write(json.dumps(data, indent=4))
        except Exception as e:
            await logger.error(f"Failed to save data to {file_name}: {e}")

    async def prepare_json_data(self, data):
        """
        Serialize data with unique identifiers.
        """
        data_json = [{'id': uuid4().hex, 'RawData': obj} for obj in data]
        return data_json


    # I'll store all the parsed data to the class properties since it's unclear wether we should be storing them only in 
    # file or proceed this data futher.
    async def fetch_and_save_data(self):
        """
        Gather data from the client and save it to JSON files.
        """
        try:
            self.characters, self.locations, self.episodes = await asyncio.gather(
                self.client.fetch_all_characters(),
                self.client.fetch_all_locations(),
                self.client.fetch_all_episodes(),
            )

            characters_json, locations_json, episodes_json = await asyncio.gather(
                self.prepare_json_data(self.characters),
                self.prepare_json_data(self.locations),
                self.prepare_json_data(self.episodes),
            )

            await asyncio.gather(
                self.save_to_json(characters_json, self.CHARACTERS_FILE),
                self.save_to_json(locations_json, self.LOCAITONS_FILE),
                self.save_to_json(episodes_json, self.EPISODES_FILE),
            )
        except RequestException as exc:
            logger.error(exc)

    async def print_episodes_in_range(self):
        # Make a request series, or if we done it before - take that results
        try:
            self.episodes = await self.client.fetch_all_episodes() 
            episode_list = []
            for episode in self.episodes:
                air_date = datetime.strptime(episode['air_date'], '%B %d, %Y')
                if 2017 <= air_date.year <= 2021:
                    episode_list.append(episode['name'])

            logger.info("Episodes aired between 2017 and 2021:")
            for name in episode_list:
                logger.info(name)
        except RequestException as exc:
            logger.error(exc)

async def main():
    """
    Implementation of the program starting point
    """
    app = RickAndMortyApp()
    try:
        await asyncio.gather(
            app.fetch_and_save_data(),
            app.print_episodes_in_range(),
        )
    finally:
        await app.client.clear_cache()
        await app.client.close()

if __name__ == '__main__':
    asyncio.run(main())