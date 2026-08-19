import threading
import time

from app.database.config import SessionLocal
from app.database.ingestion_error_repository import IngestionErrorRepository
from app.database.ingestion_run_repository import IngestionRunRepository
from app.database.job_change_repository import JobChangeRepository
from app.database.job_repository import JobRepository
from app.services.ingestion_service import IngestionService
from app.services.persistent_deduplicator import PersistentJobDeduplicator
from app.services.validator import JobValidator
from app.sources.himalayas import HimalayasSource


class IngestionScheduler:

    def __init__(
        self,
        interval_minutes: int = 60,
        max_pages: int = 5,
        page_size: int = 20,
    ):
        self.interval_seconds = interval_minutes * 60
        self.max_pages = max_pages
        self.page_size = page_size

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _worker(self):

        while not self._stop_event.is_set():

            session = SessionLocal()

            try:

                ingestion_run_repo = IngestionRunRepository(session)

                if not ingestion_run_repo.has_active_run():

                    job_repo = JobRepository(session)
                    change_repo = JobChangeRepository(session)
                    ingestion_error_repo = IngestionErrorRepository(session)

                    validator = JobValidator()
                    deduplicator = PersistentJobDeduplicator(
                        repository=job_repo,
                        change_repository=change_repo,
                    )
                    source = HimalayasSource()

                    service = IngestionService(
                        source=source,
                        validator=validator,
                        deduplicator=deduplicator,
                        ingestion_run_repository=ingestion_run_repo,
                        ingestion_error_repository=ingestion_error_repo,
                    )

                    service.run(
                        max_pages=self.max_pages,
                        page_size=self.page_size,
                    )

            except Exception as e:

                print(f"Scheduled ingestion error: {e}")

            finally:

                session.close()

            # Sleep in 1-second chunks to allow graceful immediate exit
            for _ in range(int(self.interval_seconds)):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def start(self):

        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="IngestionSchedulerThread",
        )
        self._thread.start()

    def stop(self):

        if self._thread is not None:
            self._stop_event.set()
            self._thread.join(timeout=5)
            self._thread = None

    def is_running(self) -> bool:

        return self._thread is not None and self._thread.is_alive()
