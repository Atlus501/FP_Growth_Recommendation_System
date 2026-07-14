from infrastructure.databases.mongodb.job_post import Job_Post_DB
from pymongo import InsertOne

from schemas.services.job_post import Job_Post

"""
Class that manages the service logic of job postings
"""
class Job_Post_Service:
    """
    Constructor for the job post service manager
    """
    def __init__ (self, db : Job_Post_DB):
        self.collection = db.collection
        self.client = db.client

    """
    Function for getting job posts
    """
    async def get_job_posts(self, id_list : list[str]):
        res = await self.collection.find({"_id" : {"$in" : id_list}}})
        return await res.to_list()
    
    """
    Function for bulk writing job posts
    """
    async def insert_job_posts(self, job_post_list : list[Job_Post]):
        if not job_post_list:
            return BulkWriteResult({}, acknowledged=True)

        requests = [InsertOne(document=job_post.model_dump()) for job_post in job_post_list]

        result = await self.collection.bulk_write(requests, ordered=False)
        return result

    """
    Function for removing one job post
    """
    async def delete_job_post(self, id):
        return await self.collection.delete_one({"_id" : id})

    """
    Function for updating one job post
    """
    async def update_job_post(self, id, job_post : Job_Post):
        return await self.collection.update_one({"_id" : id}, job_post.model_dump())