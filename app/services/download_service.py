import asyncio
import os
import logging
from datetime import datetime, timedelta
from app.crud import download_jobs as job_crud
from app.crud import books as book_crud
from app.model.download_job import DownloadJob, DownloadStatus, BookStatus
from app.services import annas_archive as anna
from app.model.book import Book as BookModel

logger = logging.getLogger(__name__)

class DownloadService:
    def __init__(self, download_dir: str, secret_key: str):
        self.download_dir = download_dir
        self.secret_key = secret_key
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)

    async def start_service(self):
        logger.info("Starting download service...")
        asyncio.create_task(self.process_pending_downloads())

    async def process_pending_downloads(self):
        while True:
            try:
                # Clean up failed books older than 24 hours
                await self.cleanup_failed_books()

                jobs = await job_crud.get_pending_jobs(limit=5)
                if not jobs:
                    await asyncio.sleep(5)
                    continue

                for job in jobs:
                    # Run in background without blocking the loop
                    asyncio.create_task(self.process_job(job))

                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error in download service loop: {e}")
                await asyncio.sleep(10)

    async def process_job(self, job: DownloadJob):
        logger.info(f"Processing download job {job.id} for book {job.book_hash}")

        try:
            await job_crud.update_job_status(job.id, DownloadStatus.DOWNLOADING, 10)

            book = await book_crud.get_book_by_hash(job.book_hash)
            
            if not book:
                # Book doesn't exist, need to download it
                await self.process_new_book(job)
            else:
                # Book exists
                status = book.get("status")
                file_path = book.get("file_path")
                
                if status == BookStatus.READY and file_path:
                    if os.path.exists(file_path):
                        await job_crud.update_job_status(job.id, DownloadStatus.COMPLETED, 100)
                        await job_crud.update_job_file_path(job.id, file_path)
                        logger.info(f"Book {job.book_hash} already available, job {job.id} completed")
                        return
                    else:
                        logger.warning(f"Book {job.book_hash} marked as ready but file missing, re-downloading")
                        await self.process_new_book(job)
                else:
                    # Exists but not ready
                    await self.process_new_book(job)

            await job_crud.update_job_status(job.id, DownloadStatus.COMPLETED, 100)
            logger.info(f"Download job {job.id} completed successfully")

        except Exception as e:
            logger.error(f"Failed to process job {job.id}: {e}")
            await job_crud.update_job_status(job.id, DownloadStatus.FAILED, 0, str(e))

    async def process_new_book(self, job: DownloadJob):
        existing_book = await book_crud.get_book_by_hash(job.book_hash)
        book_metadata = None

        if not existing_book:
            logger.info(f"Book {job.book_hash} not found, fetching metadata from Anna's archive")
            book_metadata = await anna.get_book_metadata(job.book_hash)
            
            if not book_metadata:
                book_metadata = anna.Book(hash=job.book_hash, title="Unknown Title")

            # Create the initial book record
            new_book = BookModel(
                title=book_metadata.title,
                author=book_metadata.authors or "Unknown Author",
                md5=job.book_hash,
                status=BookStatus.PROCESSING,
                format=book_metadata.format,
                size=book_metadata.size,
                language=book_metadata.language,
                cover_url=book_metadata.cover_url,
                updated_at=datetime.now().timestamp()
            )
            await book_crud.create_book(new_book)
        else:
            book_metadata = anna.Book(
                hash=existing_book.get("md5"),
                title=existing_book.get("title"),
                authors=existing_book.get("author"),
                format=existing_book.get("format"),
                size=existing_book.get("size"),
                language=existing_book.get("language"),
                cover_url=existing_book.get("cover_url")
            )

        await job_crud.update_job_status(job.id, DownloadStatus.DOWNLOADING, 30)
        
        # In the Go code, it calls annaBook.Download
        # We'll use our version
        await job_crud.update_job_status(job.id, DownloadStatus.DOWNLOADING, 50)
        
        try:
            file_path = await book_metadata.download(self.secret_key, self.download_dir)
            
            await job_crud.update_job_status(job.id, DownloadStatus.DOWNLOADING, 90)
            
            # Update book with final path and status
            await book_crud.update_book_status(job.book_hash, BookStatus.READY)
            
            # Update file_path in the book document
            collection = book_crud.database["books"]
            await collection.update_one(
                {"md5": job.book_hash},
                {"$set": {"file_path": file_path, "status": BookStatus.READY}}
            )

            await job_crud.update_job_file_path(job.id, file_path)

            # Parse the downloaded file into chapters and store them
            await self._parse_and_store_chapters(job.book_hash, file_path, book_metadata.format)
            
        except Exception as e:
            logger.error(f"Anna download error for book {job.book_hash}: {e}")
            await book_crud.update_book_status(job.book_hash, BookStatus.ERROR, str(e))
            raise e

    async def _parse_and_store_chapters(self, book_hash: str, file_path: str, format_type: str):
        """Read a downloaded file and parse it into chapters, then store in the book document."""
        try:
            # Only attempt parsing for text-extractable formats
            parseable_formats = {"txt", "epub", "doc", "docx", "fb2"}
            fmt = (format_type or "").lower().strip()
            
            if fmt not in parseable_formats:
                logger.info(f"Format '{fmt}' not parseable into chapters for book {book_hash}, skipping")
                return

            # Read the file content
            import os
            if not os.path.exists(file_path):
                logger.warning(f"File not found for chapter parsing: {file_path}")
                return

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"Empty file content for book {book_hash}")
                return

            # Parse into chapters
            service = anna.AnnasArchiveService()
            chapters = service.parse_book_content_to_chapters(content, fmt)

            if chapters:
                chapter_dicts = [
                    {"title": ch.title, "content": ch.content, "order": ch.order}
                    for ch in chapters
                ]
                # Find the book by hash and update its chapters
                book = await book_crud.get_book_by_hash(book_hash)
                if book:
                    await book_crud.update_book_chapters(book["_id"], chapter_dicts)
                    logger.info(f"Parsed {len(chapters)} chapters for book {book_hash}")
            else:
                logger.info(f"No chapters parsed for book {book_hash}")

        except Exception as e:
            logger.error(f"Chapter parsing error for book {book_hash}: {e}")

    async def cleanup_failed_books(self):
        cutoff_time = (datetime.now() - timedelta(hours=24)).timestamp()
        result = await book_crud.delete_failed_books(cutoff_time)
        if result > 0:
            logger.info(f"Cleaned up {result} failed books")
