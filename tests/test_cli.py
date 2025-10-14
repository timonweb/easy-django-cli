import sys
from pathlib import Path
from unittest.mock import patch

from easy_django_cli.cli import execute_django_command, find_manage_py, main


class TestFindManagePy:
    def test_find_manage_py_in_current_dir(self, temp_dir: Path) -> None:
        """
        GIVEN: A directory with manage.py file
        WHEN: Searching for manage.py in that directory
        THEN: The manage.py file should be found
        """
        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# manage.py")

        result = find_manage_py(temp_dir)

        assert result is not None
        assert result.resolve() == manage_py.resolve()

    def test_find_manage_py_in_parent_dir(self, temp_dir: Path) -> None:
        """
        GIVEN: A parent directory with manage.py and a subdirectory
        WHEN: Searching for manage.py from the subdirectory
        THEN: The manage.py in the parent directory should be found
        """
        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# manage.py")
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        result = find_manage_py(subdir)

        assert result is not None
        assert result.resolve() == manage_py.resolve()

    def test_find_manage_py_not_found(self, temp_dir: Path) -> None:
        """
        GIVEN: A directory without manage.py file
        WHEN: Searching for manage.py in that directory
        THEN: No manage.py should be found
        """
        result = find_manage_py(temp_dir)

        assert result is None

    def test_find_manage_py_max_depth(self, temp_dir: Path) -> None:
        """
        GIVEN: A manage.py at the root and a deeply nested directory
        WHEN: Searching for manage.py from the deeply nested directory
        THEN: The manage.py at the root should be found
        """
        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# manage.py")
        deep_dir = temp_dir / "a" / "b" / "c" / "d" / "e" / "f"
        deep_dir.mkdir(parents=True)

        result = find_manage_py(deep_dir)

        assert result is not None
        assert result.resolve() == manage_py.resolve()


class TestExecuteDjangoCommand:
    def test_execute_with_manage_py(self, mock_manage_py: Path) -> None:
        """
        GIVEN: A manage.py file and command arguments
        WHEN: Executing a Django command with manage.py
        THEN: The command should execute successfully
        """
        original_argv = sys.argv.copy()
        sys.argv = ["django", "--version"]

        try:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                result = execute_django_command(mock_manage_py)

                assert result == 0
                mock_run.assert_called_once()
        finally:
            sys.argv = original_argv

    def test_execute_without_manage_py(self) -> None:
        """
        GIVEN: No manage.py file available
        WHEN: Executing a Django command without manage.py
        THEN: The command should fall back to django-admin
        """
        original_argv = sys.argv.copy()
        sys.argv = ["django", "--version"]

        try:
            with patch("django.core.management.execute_from_command_line") as mock_exec:
                mock_exec.side_effect = SystemExit(0)
                result = execute_django_command(None)

                assert result == 0
        finally:
            sys.argv = original_argv

    def test_execute_handles_system_exit(self, mock_manage_py: Path) -> None:
        """
        GIVEN: A command that raises SystemExit with specific exit code
        WHEN: Executing the command
        THEN: The exit code should be returned correctly
        """
        original_argv = sys.argv.copy()
        sys.argv = ["django", "help"]

        try:
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = SystemExit(42)
                result = execute_django_command(mock_manage_py)

                assert result == 42
        finally:
            sys.argv = original_argv

    def test_execute_handles_exception(self, mock_manage_py: Path) -> None:
        """
        GIVEN: A command that raises an exception
        WHEN: Executing the command
        THEN: The error should be caught and return exit code 1
        """
        original_argv = sys.argv.copy()
        sys.argv = ["django", "invalid_command"]

        try:
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = Exception("Test error")
                result = execute_django_command(mock_manage_py)

                assert result == 1
        finally:
            sys.argv = original_argv


class TestMain:
    def test_main_finds_and_executes(self, mock_django_project: Path) -> None:
        """
        GIVEN: A Django project with manage.py
        WHEN: Running main from within the project directory
        THEN: manage.py should be found and the command executed
        """
        import os

        original_argv = sys.argv.copy()
        original_cwd = os.getcwd()
        os.chdir(mock_django_project)
        sys.argv = ["django", "--version"]

        try:
            with patch("easy_django_cli.cli.execute_django_command") as mock_exec:
                mock_exec.return_value = 0
                result = main()

                assert result == 0
                mock_exec.assert_called_once()
        finally:
            sys.argv = original_argv
            os.chdir(original_cwd)

    def test_main_without_manage_py(self, temp_dir: Path) -> None:
        """
        GIVEN: A directory without manage.py
        WHEN: Running main from that directory
        THEN: execute_django_command should be called with None
        """
        import os

        original_argv = sys.argv.copy()
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        sys.argv = ["django", "--version"]

        try:
            with patch("easy_django_cli.cli.execute_django_command") as mock_exec:
                mock_exec.return_value = 0
                result = main()

                assert result == 0
                call_args = mock_exec.call_args[0]
                assert call_args[0] is None
        finally:
            sys.argv = original_argv
            os.chdir(original_cwd)
