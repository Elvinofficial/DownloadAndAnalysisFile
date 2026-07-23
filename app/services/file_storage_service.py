from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import zipfile


@dataclass(slots=True, frozen=True)
class StoredFile:
    file_name: str
    storage_path: str


class FileStorageService:
    def __init__(
        self,
        storage_root: Path,
    ) -> None:
        self._storage_root = storage_root

    def save_archive(
        self,
        *,
        archive_bytes: bytes,
        expected_file_names: list[str],
    ) -> list[StoredFile]:
        if not expected_file_names:
            raise ValueError("Expected file names must not be empty")

        try:
            archive = zipfile.ZipFile(BytesIO(archive_bytes))
        except zipfile.BadZipFile as error:
            raise ValueError(
                "Received content is not a valid ZIP archive"
            ) from error

        with archive:
            archive_file_names = self._get_archive_file_names(archive)

            self._validate_archive_content(
                archive_file_names=archive_file_names,
                expected_file_names=expected_file_names,
            )

            stored_files: list[StoredFile] = []

            for file_name in archive_file_names:
                file_bytes = archive.read(file_name)

                stored_file = self._save_file(
                    file_name=file_name,
                    file_bytes=file_bytes,
                )

                stored_files.append(stored_file)

            return stored_files

    @staticmethod
    def _get_archive_file_names(
        archive: zipfile.ZipFile,
    ) -> list[str]:
        return [
            item.filename
            for item in archive.infolist()
            if not item.is_dir()
        ]

    @staticmethod
    def _validate_archive_content(
        *,
        archive_file_names: list[str],
        expected_file_names: list[str],
    ) -> None:
        if not archive_file_names:
            raise ValueError("ZIP archive does not contain files")

        if len(archive_file_names) != len(set(archive_file_names)):
            raise ValueError(
                "ZIP archive contains duplicate file names"
            )

        actual_names = set(archive_file_names)
        expected_names = set(expected_file_names)

        if actual_names != expected_names:
            missing_names = expected_names - actual_names
            unexpected_names = actual_names - expected_names

            raise ValueError(
                "ZIP archive content does not match requested files. "
                f"Missing: {sorted(missing_names)}. "
                f"Unexpected: {sorted(unexpected_names)}."
            )

    def _save_file(
        self,
        *,
        file_name: str,
        file_bytes: bytes,
    ) -> StoredFile:
        safe_file_name = self._validate_file_name(file_name)

        relative_path = Path("downloaded") / safe_file_name
        absolute_path = self._storage_root / relative_path

        absolute_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        absolute_path.write_bytes(file_bytes)

        return StoredFile(
            file_name=safe_file_name,
            storage_path=relative_path.as_posix(),
        )

    @staticmethod
    def _validate_file_name(
        file_name: str,
    ) -> str:
        if not file_name.strip():
            raise ValueError("File name must not be empty")

        path = Path(file_name)

        if path.name != file_name:
            raise ValueError(
                f"Unsafe file name in ZIP archive: {file_name}"
            )

        if path.suffix.lower() != ".txt":
            raise ValueError(
                f"Unsupported file extension: {file_name}"
            )

        return file_name

    def read_text_file(
        self,
        storage_path: str,
    ) -> str:
        relative_path = Path(storage_path)

        if relative_path.is_absolute():
            raise ValueError("Storage path must be relative")

        absolute_path = (
            self._storage_root / relative_path
        ).resolve()

        storage_root = self._storage_root.resolve()

        if not absolute_path.is_relative_to(storage_root):
            raise ValueError("Storage path points outside storage root")

        if not absolute_path.exists():
            raise FileNotFoundError(
                f"Stored file was not found: {storage_path}"
            )

        if not absolute_path.is_file():
            raise ValueError(
                f"Storage path is not a file: {storage_path}"
            )

        try:
            return absolute_path.read_text(
                encoding="utf-8",
            )
        except UnicodeDecodeError as error:
            raise ValueError(
                f"Stored file is not valid UTF-8: {storage_path}"
            ) from error