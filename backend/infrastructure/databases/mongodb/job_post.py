from infrastructure.databases.mongodb import MongoDB

"""
Class for the job post db manager
"""
class Job_Post_DB(MongoDB):
    """
    Constructor for the job post db manager
    """
    def __init__ (self):
        super.__init__()
        self.collection = self.get_collection("job_posts")

    """
    Function for setting up job post database collections
    Params: None
    Returns: None
    """
    async def setup_collection(self):
        await self.collection.create_index([("company", 1), ("position" : 1)], unique=True)