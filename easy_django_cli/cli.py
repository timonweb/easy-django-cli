import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Directories to skip when searching for manage.py to improve performance
SKIP_DIRS = frozenset([
    "venv", "virtualenv",  # Virtual environments
    "__pycache__",  # Python cache
    "node_modules",  # JavaScript dependencies
    "static", "build", "dist",  # Build artifacts
    "logs", "log", "tmp",  # Log directories
    "media"  # Media upload directories
])

TOP_LEVEL_SEARCH_MAX_DEPTH = 3  # Max depth to search if no top-level dir is found


def run_manage_py_command(manage_py_path: Path, args: list[str]) -> int:
    """
    Execute a Django management command using the project's manage.py script.

    Runs manage.py as a subprocess using the current Python interpreter,
    passing through all command-line arguments.

    Args:
        manage_py_path: Absolute path to the Django project's manage.py file
        args: Command-line arguments to pass to manage.py (e.g., ['runserver', '8000'])

    Returns:
        Exit code from the subprocess (0 for success, non-zero for errors)
    """
    command = [sys.executable, str(manage_py_path)] + args
    result = subprocess.run(command)
    return result.returncode


def run_django_admin_command(args: list[str]) -> int:
    """
    Execute a Django management command using django-admin (fallback when manage.py not found).

    Imports Django's management module directly and executes commands in-process.
    This is useful when working with Django packages without a project structure.

    Args:
        args: Command-line arguments for django-admin (e.g., ['startproject', 'mysite'])

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    from django.core.management import execute_from_command_line

    # Set up sys.argv for django-admin execution
    sys.argv = ["django-admin"] + args
    execute_from_command_line(sys.argv)
    return 0


def execute_django_command(manage_py_path: Optional[Path] = None) -> int:
    """
    Route Django command execution to either manage.py or django-admin.

    Determines the appropriate execution method based on whether manage.py
    was found. Handles all exceptions gracefully and returns appropriate
    exit codes.

    Args:
        manage_py_path: Path to manage.py if found, None to use django-admin fallback

    Returns:
        Exit code: 0 for success, 1 for errors

    Raises:
        No exceptions are raised; all errors are caught and converted to exit codes
    """
    args = sys.argv[1:]

    try:
        if manage_py_path:
            return run_manage_py_command(manage_py_path, args)
        else:
            return run_django_admin_command(args)
    except SystemExit as e:
        # Django commands may call sys.exit(); capture and return the code
        return e.code if isinstance(e.code, int) else 1
    except ImportError:
        print(
            "Error: Django is not installed or manage.py not found.\n"
            "Please install Django or run this command from a Django project directory.",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"Error executing django command: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        # User interrupted the command (Ctrl+C)
        return 1


def _find_files_scan_dir(
        directory: Path | str,
        filename: str,
        skip_dirs: frozenset[str]
) -> Optional[str]:
    """
    Recursively scan a directory tree for a specific filename.

    Uses os.scandir for efficient directory traversal. Returns on first match
    to optimize performance. Skips hidden directories (starting with '.') and
    directories specified in skip_dirs to avoid searching irrelevant paths.

    Args:
        directory: Root directory path to start searching from
        filename: Name of the file to find (exact match)
        skip_dirs: Set of directory names to skip during traversal

    Returns:
        Absolute path to the first matching file, or None if not found
    """
    try:
        with os.scandir(directory) as it:
            # Collect subdirectories to search after checking current level
            dirs_to_search = []

            for entry in it:
                # Check if this is the file we're looking for
                if entry.is_file(follow_symlinks=False) and entry.name == filename:
                    return entry.path

                # Collect subdirectories, skipping hidden and excluded dirs
                elif entry.is_dir(follow_symlinks=False):
                    # Skip hidden directories (except current dir) and excluded directories
                    if entry.name.startswith('.') or entry.name in skip_dirs:
                        continue
                    dirs_to_search.append(entry.path)

            # Recursively search collected subdirectories
            for dir_path in dirs_to_search:
                if result := _find_files_scan_dir(dir_path, filename, skip_dirs):
                    return result

    except (PermissionError, OSError):
        # Skip directories without read permission or with other OS-level errors
        # (common in system directories, special filesystems, etc.)
        pass

    return None


def find_manage_py() -> Optional[Path]:
    """
    Locate Django's manage.py file by recursively searching upward through parent directories.

    The search starts from the specified directory (or current working directory) and
    moves upward through parent directories, performing a recursive scan of each level's
    subdirectories. This approach finds manage.py even if it's in a sibling directory
    or nested subdirectory relative to the starting point.

    The search stops at natural boundaries (git repository root, home directory, or
    filesystem root) to avoid scanning unrelated projects.

    Returns:
        Path object pointing to manage.py if found, None otherwise
    """
    current = Path.cwd().resolve()
    search_current = current
    top_level_dir = _get_top_level_directory()
    level = 0

    # Search upward through directory hierarchy
    while True:
        # Recursively search current level and all subdirectories
        if manage_py_str := _find_files_scan_dir(
                search_current, "manage.py", SKIP_DIRS
        ):
            return Path(manage_py_str)

        # Stop at natural boundaries to avoid searching unrelated projects
        # Stop if we find a .git directory (project root marker)
        if (search_current / ".git").exists():
            # We've searched this git repo and didn't find manage.py
            break

        if (search_current / "pyproject.toml").exists():
            # We've searched this project and didn't find manage.py
            break

        # If we don't have a top level directory, we limit search depth to avoid system-wide search
        if not top_level_dir and level >= TOP_LEVEL_SEARCH_MAX_DEPTH:
            return None

        # Stop at top level directory searching system-wide
        if search_current == top_level_dir:
            break

        # Move to parent directory
        parent = search_current.parent
        if parent == search_current:
            # Reached filesystem root without finding manage.py
            break

        search_current = parent
        level += 1

    return None


def _get_top_level_directory() -> Optional[Path]:
    """
    Determine the top-level directory to limit manage.py search.
    """
    try:
        from django.conf import settings
        if base_dir := getattr(settings, "BASE_DIR", None):
            return Path(base_dir).parent.resolve()
    except Exception:
        return None


def main() -> int:
    """
    Main entry point for the easy-django CLI tool.

    Searches for a Django project's manage.py file and executes the requested
    Django management command. Falls back to django-admin if manage.py is not found.

    Returns:
        Exit code: 0 for success, non-zero for errors
    """
    # Locate manage.py by searching current directory and parents
    manage_py = find_manage_py()

    # Execute the Django command with the appropriate method
    return execute_django_command(manage_py)


if __name__ == "__main__":
    sys.exit(main())
