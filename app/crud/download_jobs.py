from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.database import get_db
from app.model.download_job import DownloadJob, DownloadStatus
from bson import ObjectId
from datetime import datetime

database: AsyncIOMotorDatabase = get_db()
COLLECTION = "download_jobs"

async def create_job(job_data: DownloadJob):
    job = job_data.model_dump(by_alias=True, exclude={"id"})
    result = await database[COLLECTION].insert_one(job)
    return str(result.inserted_id)

async def get_pending_jobs(limit: int = 5):
    jobs = []
    async for job in database[COLLECTION].find({"status": DownloadStatus.PENDING}).limit(limit):
        job["_id"] = str(job["_id"])
        jobs.append(DownloadJob(**job))
    return jobs

async def update_job_status(job_id: str, status: str, progress: int, error: str = ""):
    await database[COLLECTION].update_one(
        {"_id": ObjectId(job_id)},
        {
            "$set": {
                "status": status,
                "progress": progress,
                "error_message": error,
                "updated_at": datetime.now().timestamp()
            }
        }
    )

async def update_job_file_path(job_id: str, file_path: str):
    await database[COLLECTION].update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"file_path": file_path, "updated_at": datetime.now().timestamp()}}
    )
