# Changelog

## [0.1.2]

### Changed
- Updated Development Status to Beta
- Improved search algorithm with both upward and downward directory traversal
- Added recursive downward search from each parent directory level
- Updated Python and Django version requirements
- KeyboardInterrupt exception handling for graceful command termination

## [0.1.0]

- Initial release
- Smart `manage.py` discovery that searches upward through parent directories
- `django` and `dj` command aliases to replace `python manage.py` and `django-admin`
- Fallback to `django-admin` when `manage.py` is not found
- Support for Django 4.2, 5.0, 5.1, 5.2, and 6.0
- Support for Python 3.10, 3.11, 3.12, 3.13, and 3.14
- Comprehensive test suite with pytest and pytest-django
- Skip common directories (venv, node_modules, __pycache__, etc.) for faster searching
- Git repository boundary detection to prevent searching outside project scope
