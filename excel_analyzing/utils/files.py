"""File system utilities."""

import hashlib
import os
from pathlib import Path
from typing import Generator, List, Optional, Set
import re
import logging

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues.
    
    Args:
        filename: Raw filename to sanitize
        
    Returns:
        Sanitized filename safe for filesystem operations
    """
    if not filename:
        return "unnamed_file"
    
    # Remove or replace dangerous characters
    # Remove control characters and dangerous symbols
    safe = re.sub(r'[<>:"|?*;\x00-\x1f`$()&]', '', filename)
    
    # Remove leading/trailing dots and spaces
    safe = safe.strip('. ')
    
    # Replace multiple consecutive spaces with single space
    safe = re.sub(r'\s+', ' ', safe)
    
    # Limit length to 255 characters (filesystem limit)
    if len(safe) > 255:
        name, ext = os.path.splitext(safe)
        max_name_length = 255 - len(ext)
        safe = name[:max_name_length] + ext
    
    # Ensure we have something left
    if not safe or safe in ['.', '..']:
        safe = "sanitized_file"
    
    # Ensure it doesn't start with a dot (hidden file)
    if safe.startswith('.'):
        safe = 'file_' + safe[1:]
    
    return safe


def get_file_hash(file_path: Path, algorithm: str = "md5") -> str:
    """Calculate file hash."""
    hash_func = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def find_excel_files(
    directory: Path, recursive: bool = True, extensions: Optional[Set[str]] = None
) -> Generator[Path, None, None]:
    """Find Excel files in directory."""
    if extensions is None:
        extensions = {".xlsx", ".xls", ".xlsm", ".xlsb"}

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    pattern_func = directory.rglob if recursive else directory.glob

    for ext in extensions:
        for file_path in pattern_func(f"*{ext}"):
            if file_path.is_file() and not file_path.name.startswith("~$"):
                yield file_path


def ensure_directory(directory: Path) -> None:
    """Ensure directory exists, create if necessary."""
    directory.mkdir(parents=True, exist_ok=True)


def safe_filename(filename: str, max_length: int = 255) -> str:
    """Create a safe filename by removing problematic characters."""
    import re

    # Remove problematic characters
    safe = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Replace multiple underscores with single
    safe = re.sub(r"_+", "_", safe)

    # Trim length
    if len(safe) > max_length:
        name, ext = os.path.splitext(safe)
        safe = name[: max_length - len(ext)] + ext

    return safe.strip("_")


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    return file_path.stat().st_size / (1024 * 1024)


def is_file_accessible(file_path: Path) -> bool:
    """Check if file is accessible for reading."""
    try:
        with open(file_path, "rb") as f:
            f.read(1)
        return True
    except (OSError, IOError, PermissionError):
        return False


class FileWatcher:
    """Simple file watcher for monitoring directory changes."""

    def __init__(self, directory: Path):
        """Initialize file watcher."""
        self.directory = directory
        self._last_scan: Optional[Set[Path]] = None

    def get_new_files(self, extensions: Optional[Set[str]] = None) -> List[Path]:
        """Get list of new files since last scan."""
        current_files = set(find_excel_files(self.directory, extensions=extensions))

        if self._last_scan is None:
            new_files = list(current_files)
        else:
            new_files = list(current_files - self._last_scan)

        self._last_scan = current_files
        return new_files
