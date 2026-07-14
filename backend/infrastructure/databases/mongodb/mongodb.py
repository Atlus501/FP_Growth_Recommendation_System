from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import logging

from config.settings

"""
Class for managing the MongoDB instance
"""
class MongoDB:
    """
    Constructor for the MongoDB manager.
    Params: None
    """
    def __init__ (self):
        db_username = settings.MONGODB_USERNAME
        db_password = settings.MONGODB_PASSWORD
        uri = f"mongodb+srv://{db_username}:{db_password}@jobrate.67izimm.mongodb.net/?appName=JobRate"
        self.client = AsyncMongoClient(uri, server_api=ServerApi('1'))
        self.logger = logging.getLogger(__name__)

    """
    Function for getting the table that one is using
    Params: table (str) -- name of the table
    Returns: table object 
    """
    def get_collection(self, table: str):
        db = self.client["Job_Post_Rating"]
        return db[table]

    """
    Template for subclasses to set up
    """
    async def setup_collection(self):
        pass

    """
    Function to test he connction of the mongodb manager.
    Params: None
    Returns: None
    """
    async def test_connection (self):
        # Create a new client and connect to the server
        client = self.client
        # Send a ping to confirm a successful connection
        await client.admin.command('ping')

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(filename='job_post_rating.log', level=logging.INFO)
    user = User(username="watsonian132", password="testingtestingtesting123", applied_job_posts=[])
    mongodb = MongoDB_Manager()
    mongodb.setup_user_collection()
    mongodb.add_user(user)