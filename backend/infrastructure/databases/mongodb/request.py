from infrastructure.databases.mongodb.mongodb import MongoDB

"""
Class that is going to manage requests of adding job post requests
"""
class Request_DB(MongoDB):
    def __init__(self):
        super.__init__()
        self.collection = self.get_collection("requests")

    """
    Sets up the indicies of the collection
    """
    async def setup_collection(self):
        await requests_collection.create_index([("Author", 1), ("Company", 1), ("Position", 1)], unique=True)