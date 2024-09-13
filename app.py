import json
import asyncio 
import aiofiles
from uuid import uuid4

from datetime import datetime
from client import RickAndMortyClient

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
        Method for saving json to the files
        """
        async with aiofiles.open(file_name, 'w') as file:
            await file.write(json.dumps(data, indent=4))

    async def prepare_json_data(self, data):
        """
        Basically serialise data in a proper way
        """
        data_json = [{'id': uuid4().hex, 'RawData': obj} for obj in data]
        return data_json


    # I'll store all the parsed data to the class properties since it's unclear wether we should be storing them only in 
    # file or proceed this data futher.
    async def fetch_and_save_data(self):
        """
        Method for gathering client request results and saving them to json
        """
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
    
    # We may either make a call to API or assume that we should print episodes in range as a part of the flow.
    # In this case - I'll make a check if we get the episodes list already and if we have it - I won't be making a
    # request to obatin them again. However since our code is async, most of the time self.episodes will be empty at first.
    async def print_episodes_in_range(self):
        if not self.episodes:
            self.episodes = await self.client.fetch_all_episodes()
        
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