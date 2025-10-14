import os
import tempfile
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture(autouse=True)
def preserve_cwd():
    """
    Preserve and restore the current working directory.
    """
    original_cwd = os.getcwd()
    yield
    try:
        os.chdir(original_cwd)
    except (FileNotFoundError, OSError):
        # If the original directory was deleted, go to a safe location
        os.chdir(Path.home())


@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """
    Create a temporary directory for testing.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_manage_py(temp_dir: Path) -> Path:
    """
    Create a mock manage.py file for testing.
    """
    manage_py = temp_dir / "manage.py"
    manage_py.write_text(
        """#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(sys.argv)
"""
    )
    manage_py.chmod(0o755)
    return manage_py


@pytest.fixture
def mock_django_project(temp_dir: Path, mock_manage_py: Path) -> Path:
    """
    Create a mock Django project structure for testing.
    """
    # Create a minimal Django project structure
    project_dir = temp_dir / "myproject"
    project_dir.mkdir()

    # Create __init__.py
    (project_dir / "__init__.py").write_text("")

    # Create settings.py
    (project_dir / "settings.py").write_text(
        """
SECRET_KEY = 'test-key'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
USE_TZ = True
"""
    )

    return temp_dir
