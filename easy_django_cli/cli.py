import subprocess
import sys
from pathlib import Path
from typing import Optional


def find_manage_py(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Search for manage.py in the current directory and parent directories.

    Args:
        start_path: Directory to start searching from (defaults to current directory)

    Returns:
        Path to manage.py if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Search up
    while True:
        manage_py = current / "manage.py"
        if manage_py.exists() and manage_py.is_file():
            return manage_py

        # Move to parent directory
        parent = current.parent
        if parent == current:
            # Reached the root directory
            break
        current = parent

    return None


def run_manage_py_command(manage_py_path: Path, args: list) -> int:
    """
    Run a Django management command using manage.py.

    Args:
        manage_py_path: Path to manage.py
        args: List of command-line arguments

    Returns:
        Exit code from the command
    """
    command = [sys.executable, str(manage_py_path)] + args
    result = subprocess.run(command)
    return result.returncode


def run_django_admin_command(args: list) -> int:
    """
    Run a Django management command using django-admin.

    Args:
        args: List of command-line arguments

    Returns:
        Exit code from the command
    """
    # Fall back to django-admin
    from django.core.management import execute_from_command_line
    # Update sys.argv for django-admin style execution
    sys.argv = ["django-admin"] + args
    execute_from_command_line(sys.argv)
    return 0


def execute_django_command(manage_py_path: Optional[Path] = None) -> int:
    """
    Execute Django management command.

    Args:
        manage_py_path: Path to manage.py if found

    Returns:
        Exit code from the Django command
    """
    # Remove the script name from argv, keep only the arguments
    args = sys.argv[1:]

    try:
        if manage_py_path:
            return run_manage_py_command(manage_py_path, args)
        else:
            return run_django_admin_command(args)
    except SystemExit as e:
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
        return 1


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        Exit code
    """
    # Find manage.py in current or parent directories
    manage_py = find_manage_py()

    # Execute the Django command
    return execute_django_command(manage_py)


if __name__ == "__main__":
    sys.exit(main())
