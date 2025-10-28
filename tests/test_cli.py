import sys
from pathlib import Path
from unittest.mock import patch

from easy_django_cli.cli import (
    _get_top_level_directory,
    execute_django_command,
    find_manage_py,
    main,
)


class TestFindManagePy:
    def test_find_manage_py_in_current_dir(self, temp_dir: Path) -> None:
        """
        GIVEN: A directory with manage.py file
        WHEN: Searching for manage.py in that directory
        THEN: The manage.py file should be found
        """
        import os

        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# manage.py")

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = find_manage_py()

            assert result is not None
            assert result.resolve() == manage_py.resolve()
        finally:
            os.chdir(original_cwd)

    def test_find_manage_py_in_parent_dir(self, temp_dir: Path) -> None:
        """
        GIVEN: A parent directory with manage.py and a subdirectory
        WHEN: Searching for manage.py from the subdirectory
        THEN: The manage.py in the parent directory should be found
        """
        import os

        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# manage.py")
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            result = find_manage_py()

            assert result is not None
            assert result.resolve() == manage_py.resolve()
        finally:
            os.chdir(original_cwd)

    def test_find_manage_py_not_found(self, temp_dir: Path) -> None:
        """
        GIVEN: A directory without manage.py file
        WHEN: Searching for manage.py in that directory
        THEN: No manage.py should be found
        """
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = find_manage_py()

            assert result is None
        finally:
            os.chdir(original_cwd)

    def test_find_manage_py_max_depth(self, temp_dir: Path) -> None:
        """
        GIVEN: A manage.py at the root and a deeply nested directory
        WHEN: Searching for manage.py from the deeply nested directory
        THEN: The manage.py at the root should be found
        """
        import os

        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# manage.py")
        deep_dir = temp_dir / "a" / "b" / "c"
        deep_dir.mkdir(parents=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(deep_dir)
            result = find_manage_py()

            assert result is not None
            assert result.resolve() == manage_py.resolve()
        finally:
            os.chdir(original_cwd)

    def test_find_manage_py_max_depth_fails(self, temp_dir: Path) -> None:
        """
        GIVEN: A manage.py beyond the max search depth
        WHEN: Searching for manage.py from a deeply nested directory
        THEN: No manage.py should be found
        """
        import os

        manage_py = temp_dir / "manage.py"
        manage_py.write_text("# manage.py")
        deep_dir = temp_dir / "a" / "b" / "c" / "d"
        deep_dir.mkdir(parents=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(deep_dir)
            result = find_manage_py()

            assert result is None
        finally:
            os.chdir(original_cwd)

    def test_find_manage_py_stops_at_git_boundary(self, temp_dir: Path) -> None:
        """
        GIVEN: A git repository without manage.py and a parent directory with manage.py
        WHEN: Searching for manage.py from inside the git repo
        THEN: The search should stop at the git boundary and not find the parent's manage.py
        """
        import os

        # Create a manage.py in the parent directory
        parent_manage_py = temp_dir / "manage.py"
        parent_manage_py.write_text("# parent manage.py")

        # Create a subdirectory with .git (simulating a git repo)
        git_repo = temp_dir / "git_repo"
        git_repo.mkdir()
        git_dir = git_repo / ".git"
        git_dir.mkdir()

        # Create a subdirectory inside the git repo
        subdir = git_repo / "subdir"
        subdir.mkdir()

        # Change to the subdir and search from there
        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            result = find_manage_py()

            # Should not find the parent's manage.py due to git boundary
            assert result is None
        finally:
            os.chdir(original_cwd)

    def test_find_manage_py_finds_within_git_repo(self, temp_dir: Path) -> None:
        """
        GIVEN: A git repository with manage.py inside it
        WHEN: Searching for manage.py from a subdirectory in the repo
        THEN: The manage.py inside the git repo should be found
        """
        import os

        # Create a git repo directory with .git
        git_repo = temp_dir / "git_repo"
        git_repo.mkdir()
        git_dir = git_repo / ".git"
        git_dir.mkdir()

        # Create manage.py inside the git repo
        manage_py = git_repo / "manage.py"
        manage_py.write_text("# manage.py")

        # Create a subdirectory inside the git repo
        subdir = git_repo / "subdir"
        subdir.mkdir()

        # Change to the subdir and search from there
        original_cwd = os.getcwd()
        try:
            os.chdir(subdir)
            result = find_manage_py()

            # Should find manage.py inside the git repo
            assert result is not None
            assert result.resolve() == manage_py.resolve()
        finally:
            os.chdir(original_cwd)


class TestGetTopLevelDirectory:
    def test_get_top_level_directory_no_django(self) -> None:
        """
        GIVEN: Django is not installed or not configured
        WHEN: Calling _get_top_level_directory
        THEN: Should return None without raising exceptions
        """
        result = _get_top_level_directory()

        # Should handle missing Django gracefully
        assert result is None

    def test_get_top_level_directory_with_django_configured(
        self, temp_dir: Path
    ) -> None:
        """
        GIVEN: Django is configured with BASE_DIR in settings
        WHEN: Calling _get_top_level_directory
        THEN: Should return the parent of BASE_DIR
        """
        # Create a mock settings module with BASE_DIR
        base_dir = temp_dir / "project"
        base_dir.mkdir()

        with patch("django.conf.settings") as mock_settings:
            mock_settings.BASE_DIR = str(base_dir)
            result = _get_top_level_directory()

            assert result is not None
            assert result.resolve() == temp_dir.resolve()

    def test_get_top_level_directory_no_base_dir(self) -> None:
        """
        GIVEN: Django is configured but settings has no BASE_DIR
        WHEN: Calling _get_top_level_directory
        THEN: Should return None
        """
        with patch("django.conf.settings") as mock_settings:
            # Mock settings without BASE_DIR attribute
            del mock_settings.BASE_DIR
            mock_settings.BASE_DIR = None

            result = _get_top_level_directory()

            assert result is None

    def test_get_top_level_directory_handles_improperly_configured(self) -> None:
        """
        GIVEN: Django raises ImproperlyConfigured when accessing settings
        WHEN: Calling _get_top_level_directory
        THEN: Should return None without raising exceptions
        """
        from django.core.exceptions import ImproperlyConfigured

        with patch("django.conf.settings") as mock_settings:
            # Simulate ImproperlyConfigured error
            type(mock_settings).BASE_DIR = property(
                lambda self: (_ for _ in ()).throw(
                    ImproperlyConfigured("Django is not configured")
                )
            )

            result = _get_top_level_directory()

            # Should catch the exception and return None
            assert result is None


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
