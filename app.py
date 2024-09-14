import json
import asyncio 
import aiofiles
from uuid import uuid4
from aiologger import Logger
from datetime import datetime

from client import RickAndMortyClient
from logger import formatter
from exceptions import RequestException

logger = Logger.with_default_handlers(name=__name__)
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
        self.client = RickAndMortyClient()  # Adding instance to this class to be able to request directly from the app class
        self.characters = {}  # Assume we need to hold it as a class property, refer to line 63
        self.locations = {}  # Assume we need to hold it as a class property, refer to line 63
        self.episodes = {}  # Assume we need to hold it as a class property, refer to line 63

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
    
    # We may either make a call to API or assume that we should print episodes in range as a part of the flow.
    # In this case - I'll make a check if we get the episodes list already and if we have it - I won't be making a
    # request to obatin them again. However since our code is async, most of the time self.episodes will be empty at first.
    async def print_episodes_in_range(self):
        if not self.episodes:
            try:
                self.episodes = await self.client.fetch_all_episodes()
            except RequestException as exc:
                logger.error(exc)

        episode_list = []
        for episode in self.episodes:
            air_date = datetime.strptime(episode['air_date'], '%B %d, %Y')
            if 2017 <= air_date.year <= 2021:
                episode_list.append(episode['name'])

        print("Episodes aired between 2017 and 2021:")
        for name in episode_list:
            print(name)


async def main():
    """
    Implementation of the program starting point
    """
    app = RickAndMortyApp()

    try:
        await asyncio.gather(
            app.fetch_and_save_data(),
            app.print_episodes_in_range()
        )
    finally:
        await app.client.close()

if __name__ == '__main__':
    asyncio.run(main())