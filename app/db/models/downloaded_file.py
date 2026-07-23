from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.download_job import utc_now

if TYPE_CHECKING:
    from app.db.models.download_job import DownloadJob


class DownloadedFile(Base):
    __tablename__ = "downloaded_files"

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "file_name",
            name="uq_downloaded_files_job_id_file_name",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    job_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "download_jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    job: Mapped["DownloadJob"] = relationship(
        back_populates="files",
    )