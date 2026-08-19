from abc import ABC, abstractmethod
from app.models.job import Job


class JobSource(ABC):

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the job source (e.g. 'himalayas', 'remoteok')."""
        pass

    @abstractmethod
    def fetch_jobs(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Job]:
        """Fetch a page of normalized Job objects from the source."""
        pass

    @abstractmethod
    def fetch_all_jobs(
        self,
        max_pages: int = 5,
        page_size: int = 20,
    ) -> list[Job]:
        """Fetch multiple pages of normalized Job objects from the source."""
        pass
